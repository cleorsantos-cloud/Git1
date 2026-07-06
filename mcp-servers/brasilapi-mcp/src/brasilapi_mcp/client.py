"""BrasilAPI async HTTP client. Public API — no authentication required."""

import asyncio
from typing import Any, Optional

import httpx

BASE_URL = "https://brasilapi.com.br/api"


class ApiError(Exception):
    """Error returned by BrasilAPI."""

    def __init__(self, message: str, status_code: int = 0):
        self.status_code = status_code
        super().__init__(message)


class RateLimitError(ApiError):
    """Rate limit hit — caller should retry with backoff."""
    pass


class ApiClient:
    """Async HTTP client for BrasilAPI (no auth)."""

    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=BASE_URL,
                timeout=httpx.Timeout(30.0, read=60.0),
                limits=httpx.Limits(max_connections=20),
                headers={"User-Agent": "brasilapi-mcp/0.1.0"},
            )
        return self._client

    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
    ) -> Any:
        client = await self._get_client()
        clean_params = {k: v for k, v in (params or {}).items() if v is not None}

        for attempt in range(3):
            response = await client.request(
                method,
                endpoint if endpoint.startswith("http") else f"/{endpoint.lstrip('/')}",
                params=clean_params,
            )

            if 200 <= response.status_code < 300:
                return response.json()

            if response.status_code == 429:
                if attempt < 2:
                    await asyncio.sleep(2 ** (attempt + 1))
                    continue
                raise RateLimitError(response.text, status_code=429)

            raise ApiError(response.text, status_code=response.status_code)

        raise ApiError("Max retries exceeded")

    async def get(self, endpoint: str, params: Optional[dict[str, Any]] = None) -> Any:
        return await self.request("GET", endpoint, params=params)

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
