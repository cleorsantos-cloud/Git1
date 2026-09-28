"""Cliente assíncrono da Google Ads API (REST).

Autenticação: OAuth 2.0 com refresh token de uma conta que tenha acesso à
conta administradora (MCC). O developer token vem do API Center da MCC.

Variáveis de ambiente obrigatórias:
    GOOGLE_ADS_DEVELOPER_TOKEN   token do API Center da MCC
    GOOGLE_ADS_LOGIN_CUSTOMER_ID ID da MCC, só dígitos (ex: 3845391611)

Credencial do OAuth, de um jeito ou de outro:
    a) GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_SECRET e
       GOOGLE_ADS_REFRESH_TOKEN diretamente no ambiente; ou
    b) GOOGLE_APPLICATION_CREDENTIALS apontando para um arquivo de credencial
       de usuário autorizado (o ADC que o `gcloud auth application-default
       login` grava), de onde os três valores são lidos.

Opcionais:
    GOOGLE_ADS_API_VERSION       versão da API (padrão: v26)
    GOOGLE_ADS_MCP_ALLOW_WRITES  "1" libera as tools de escrita
"""

import asyncio
import json
import os
import re
import time
from typing import Any, Optional

import httpx

OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token"
API_HOST = "https://googleads.googleapis.com"
DEFAULT_API_VERSION = "v26"

_REQUIRED_ENV = (
    "GOOGLE_ADS_DEVELOPER_TOKEN",
    "GOOGLE_ADS_LOGIN_CUSTOMER_ID",
)

# Pares variável de ambiente -> chave no arquivo de credencial do ADC.
_OAUTH_FIELDS = (
    ("GOOGLE_ADS_CLIENT_ID", "client_id"),
    ("GOOGLE_ADS_CLIENT_SECRET", "client_secret"),
    ("GOOGLE_ADS_REFRESH_TOKEN", "refresh_token"),
)


class ConfigError(RuntimeError):
    """Configuração ausente ou inválida."""


class ApiError(Exception):
    """Erro devolvido pela Google Ads API."""

    def __init__(self, message: str, status_code: int = 0, details: Any = None):
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class RateLimitError(ApiError):
    """Cota estourada — o chamador deve tentar de novo com backoff."""


class WritesDisabledError(RuntimeError):
    """Tool de escrita chamada sem GOOGLE_ADS_MCP_ALLOW_WRITES=1."""


def normalize_customer_id(customer_id: str) -> str:
    """Aceita 386-824-5329 ou 3868245329 e devolve só os dígitos."""
    digits = re.sub(r"\D", "", str(customer_id or ""))
    if len(digits) != 10:
        raise ConfigError(
            f"ID de cliente inválido: {customer_id!r}. "
            "Use os 10 dígitos da conta, com ou sem hífens."
        )
    return digits


def micros_to_units(micros: Any) -> Optional[float]:
    """Converte valor em micros (padrão da API) para a moeda da conta."""
    if micros in (None, ""):
        return None
    try:
        return round(int(micros) / 1_000_000, 2)
    except (TypeError, ValueError):
        return None


class GoogleAdsClient:
    """Cliente REST da Google Ads API, com cache do access token."""

    def __init__(self) -> None:
        self._client: Optional[httpx.AsyncClient] = None
        self._access_token: Optional[str] = None
        self._token_expiry: float = 0.0
        self._lock = asyncio.Lock()

    # ---- configuração ----

    @staticmethod
    def _oauth_from_adc() -> dict[str, str]:
        """Lê client id, secret e refresh token do arquivo do ADC, se houver.

        O arquivo apontado por GOOGLE_APPLICATION_CREDENTIALS serve quando é
        do tipo `authorized_user`. Conta de serviço não vale para a Google Ads
        API sem delegação de domínio, então é recusada com mensagem clara.
        """
        caminho = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if not caminho:
            return {}
        if not os.path.exists(caminho):
            raise ConfigError(
                f"GOOGLE_APPLICATION_CREDENTIALS aponta para {caminho}, que não existe."
            )
        try:
            with open(caminho, encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except (OSError, json.JSONDecodeError) as exc:
            raise ConfigError(
                f"Não consegui ler o arquivo de credencial {caminho}: {exc}"
            ) from exc

        tipo = dados.get("type")
        if tipo == "service_account":
            raise ConfigError(
                f"O arquivo {caminho} é de conta de serviço. A Google Ads API não "
                "aceita conta de serviço sem delegação de domínio no Workspace. "
                "Gere uma credencial de usuário com scripts/get_refresh_token.py "
                "ou com `gcloud auth application-default login`."
            )

        encontrados = {
            destino: dados[origem]
            for destino, origem in _OAUTH_FIELDS
            if dados.get(origem)
        }
        return encontrados

    def config(self) -> dict[str, str]:
        missing = [name for name in _REQUIRED_ENV if not os.environ.get(name)]
        if missing:
            raise ConfigError(
                "Variáveis de ambiente ausentes: "
                + ", ".join(missing)
                + ". Veja o README do google-ads-mcp."
            )

        oauth = {
            nome: os.environ[nome] for nome, _ in _OAUTH_FIELDS if os.environ.get(nome)
        }
        if len(oauth) < len(_OAUTH_FIELDS):
            for nome, valor in self._oauth_from_adc().items():
                oauth.setdefault(nome, valor)

        faltando = [nome for nome, _ in _OAUTH_FIELDS if nome not in oauth]
        if faltando:
            raise ConfigError(
                "Credencial do OAuth incompleta. Faltam: "
                + ", ".join(faltando)
                + ". Defina essas variáveis, ou aponte GOOGLE_APPLICATION_CREDENTIALS "
                "para um arquivo de credencial de usuário autorizado que as contenha."
            )

        return {
            "developer_token": os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
            "client_id": oauth["GOOGLE_ADS_CLIENT_ID"],
            "client_secret": oauth["GOOGLE_ADS_CLIENT_SECRET"],
            "refresh_token": oauth["GOOGLE_ADS_REFRESH_TOKEN"],
            "login_customer_id": normalize_customer_id(
                os.environ["GOOGLE_ADS_LOGIN_CUSTOMER_ID"]
            ),
        }

    @property
    def api_version(self) -> str:
        return os.environ.get("GOOGLE_ADS_API_VERSION") or DEFAULT_API_VERSION

    @staticmethod
    def writes_enabled() -> bool:
        return os.environ.get("GOOGLE_ADS_MCP_ALLOW_WRITES") == "1"

    @staticmethod
    def require_writes() -> None:
        if not GoogleAdsClient.writes_enabled():
            raise WritesDisabledError(
                "Escrita bloqueada. Este servidor sobe em modo somente leitura. "
                "Defina GOOGLE_ADS_MCP_ALLOW_WRITES=1 no ambiente do MCP para "
                "liberar criação, pausa e alteração de orçamento."
            )

    # ---- HTTP ----

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0, read=120.0),
                limits=httpx.Limits(max_connections=10),
                headers={"User-Agent": "google-ads-mcp/0.1.0"},
            )
        return self._client

    async def access_token(self) -> str:
        """Devolve um access token válido, renovando quando faltar 1 minuto."""
        async with self._lock:
            if self._access_token and time.time() < self._token_expiry - 60:
                return self._access_token

            cfg = self.config()
            client = await self._get_client()
            response = await client.post(
                OAUTH_TOKEN_URL,
                data={
                    "client_id": cfg["client_id"],
                    "client_secret": cfg["client_secret"],
                    "refresh_token": cfg["refresh_token"],
                    "grant_type": "refresh_token",
                },
            )
            if response.status_code != 200:
                raise ApiError(
                    "Falha ao renovar o access token do OAuth. Confira client ID, "
                    f"secret e refresh token. Resposta: {response.text}",
                    status_code=response.status_code,
                )
            payload = response.json()
            self._access_token = payload["access_token"]
            self._token_expiry = time.time() + int(payload.get("expires_in", 3600))
            return self._access_token

    def _headers(self, token: str, login_customer_id: str) -> dict[str, str]:
        cfg_token = os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"]
        return {
            "Authorization": f"Bearer {token}",
            "developer-token": cfg_token,
            "login-customer-id": login_customer_id,
            "Content-Type": "application/json",
        }

    async def request(
        self,
        method: str,
        path: str,
        json_body: Optional[dict[str, Any]] = None,
    ) -> Any:
        """Chama a API e devolve o JSON, traduzindo os erros mais comuns."""
        cfg = self.config()
        token = await self.access_token()
        client = await self._get_client()
        url = f"{API_HOST}/{self.api_version}/{path.lstrip('/')}"

        for attempt in range(3):
            response = await client.request(
                method,
                url,
                json=json_body,
                headers=self._headers(token, cfg["login_customer_id"]),
            )

            if 200 <= response.status_code < 300:
                return response.json() if response.content else {}

            if response.status_code == 429:
                if attempt < 2:
                    await asyncio.sleep(2 ** (attempt + 1))
                    continue
                raise RateLimitError(response.text, status_code=429)

            if response.status_code == 404:
                raise ApiError(
                    f"Endpoint não encontrado ({url}). A versão "
                    f"{self.api_version} pode ter sido descontinuada — ajuste "
                    "GOOGLE_ADS_API_VERSION para a versão atual da API.",
                    status_code=404,
                )

            raise ApiError(
                self._explain(response), status_code=response.status_code
            )

        raise ApiError("Número máximo de tentativas excedido")

    @staticmethod
    def _explain(response: httpx.Response) -> str:
        """Extrai a mensagem útil do corpo de erro da Google Ads API."""
        try:
            payload = response.json()
        except (ValueError, json.JSONDecodeError):
            return response.text

        error = payload.get("error", payload)
        parts = [error.get("message", "")]
        for detail in error.get("details", []):
            for failure_error in detail.get("errors", []):
                message = failure_error.get("message")
                if message:
                    parts.append(message)
                location = failure_error.get("location", {})
                for field in location.get("fieldPathElements", []):
                    name = field.get("fieldName")
                    if name:
                        parts.append(f"campo: {name}")
        return " | ".join(p for p in parts if p) or response.text

    # ---- operações de alto nível ----

    async def search(
        self,
        customer_id: str,
        query: str,
        page_size: int = 200,
        max_pages: int = 10,
    ) -> list[dict[str, Any]]:
        """Roda uma consulta GAQL e devolve todas as linhas, paginando."""
        cid = normalize_customer_id(customer_id)
        rows: list[dict[str, Any]] = []
        page_token: Optional[str] = None

        for _ in range(max_pages):
            body: dict[str, Any] = {"query": query, "pageSize": page_size}
            if page_token:
                body["pageToken"] = page_token
            payload = await self.request(
                "POST", f"customers/{cid}/googleAds:search", json_body=body
            )
            rows.extend(payload.get("results", []))
            page_token = payload.get("nextPageToken")
            if not page_token:
                break

        return rows

    async def mutate(
        self,
        customer_id: str,
        resource: str,
        operations: list[dict[str, Any]],
        validate_only: bool = False,
    ) -> Any:
        """Executa um mutate. `resource` é o nome REST, ex: adGroupAds."""
        cid = normalize_customer_id(customer_id)
        body = {"operations": operations, "validateOnly": validate_only}
        return await self.request(
            "POST", f"customers/{cid}/{resource}:mutate", json_body=body
        )

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
