"""Linha de comando para rodar as mesmas tools sem servidor MCP.

Serve para ambientes onde registrar um MCP não vale a pena, como um
container efêmero, mas as credenciais estão no ambiente.

Uso:
    python -m google_ads_mcp.cli                      # lista as tools
    python -m google_ads_mcp.cli list_client_accounts
    python -m google_ads_mcp.cli list_ads customer_id=386-824-5329 only_disapproved=true
    python -m google_ads_mcp.cli run_gaql customer_id=386-824-5329 query="SELECT ..."

Argumentos vão como chave=valor, na mesma grafia dos parâmetros da tool.
true, false, números e listas em JSON são convertidos automaticamente.
"""

import asyncio
import inspect
import json
import sys
from typing import Any

from google_ads_mcp.client import ApiError, ConfigError, WritesDisabledError
from google_ads_mcp.tools import core

_TOOLS = {tool.__name__: tool for tool in core.ALL_TOOLS}


def _coerce(valor: str) -> Any:
    """Converte o valor de texto para bool, número ou JSON quando der."""
    baixo = valor.lower()
    if baixo in ("true", "verdadeiro"):
        return True
    if baixo in ("false", "falso"):
        return False
    if valor.startswith(("[", "{")):
        try:
            return json.loads(valor)
        except json.JSONDecodeError:
            return valor
    try:
        return int(valor)
    except ValueError:
        pass
    try:
        return float(valor)
    except ValueError:
        return valor


def _listar() -> None:
    print("Tools disponíveis:\n")
    for nome, tool in _TOOLS.items():
        assinatura = inspect.signature(tool)
        params = ", ".join(
            p if v.default is inspect.Parameter.empty else f"{p}={v.default!r}"
            for p, v in assinatura.parameters.items()
        )
        resumo = (tool.__doc__ or "").strip().split("\n")[0]
        print(f"  {nome}({params})\n      {resumo}\n")


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ("-h", "--help", "help"):
        _listar()
        return 0

    nome = args[0]
    if nome not in _TOOLS:
        print(f"Tool desconhecida: {nome}\n", file=sys.stderr)
        _listar()
        return 2

    kwargs: dict[str, Any] = {}
    for bruto in args[1:]:
        if "=" not in bruto:
            print(f"Argumento inválido: {bruto!r}. Use chave=valor.", file=sys.stderr)
            return 2
        chave, _, valor = bruto.partition("=")
        kwargs[chave] = _coerce(valor)

    try:
        print(asyncio.run(_TOOLS[nome](**kwargs)))
    except (ConfigError, WritesDisabledError) as exc:
        print(f"Configuração: {exc}", file=sys.stderr)
        return 3
    except ApiError as exc:
        print(f"Google Ads API ({exc.status_code}): {exc}", file=sys.stderr)
        return 4
    except TypeError as exc:
        print(f"Argumentos da tool: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        # Saída cortada por um pipe, como `| head`. Não é erro do programa.
        try:
            sys.stdout.close()
        finally:
            sys.exit(0)
