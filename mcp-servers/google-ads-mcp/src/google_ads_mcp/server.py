"""Servidor MCP da Google Ads API.

Registra as tools e aplica Code Mode quando disponível, colapsando tudo em
3 meta-tools (search / get_schema / execute), no mesmo padrão do brasilapi-mcp.
"""

import os
import sys

from fastmcp import FastMCP

from google_ads_mcp.client import GoogleAdsClient
from google_ads_mcp.tools import core

_MODO = "leitura e escrita" if GoogleAdsClient.writes_enabled() else "somente leitura"

mcp = FastMCP(
    "google-ads",
    instructions=(
        "MCP da Google Ads API para as contas sob a conta administradora da "
        "Agência Bona Vita. Lê contas, campanhas, anúncios e palavras-chave, e "
        "opera criação de anúncio de pesquisa responsivo, status de anúncio e "
        "campanha e orçamento diário. IDs de conta aceitam hífens. A URL final "
        "de um anúncio existente não pode ser editada: crie um anúncio novo e "
        "pause o antigo. Comece por list_client_accounts para descobrir as "
        f"contas filhas. Modo atual: {_MODO}."
    ),
)

for _tool in core.ALL_TOOLS:
    mcp.tool(_tool)

# Code Mode colapsa as tools em 3 meta-tools (search/get_schema/execute).
# Desligue com GOOGLE_ADS_MCP_NO_CODEMODE=1 se o sandbox não estiver disponível.
if os.environ.get("GOOGLE_ADS_MCP_NO_CODEMODE") != "1":
    try:
        from fastmcp.experimental.transforms.code_mode import (
            CodeMode,
            MontySandboxProvider,
        )

        _sandbox = MontySandboxProvider(
            limits={"max_duration_secs": 30, "max_memory": 100_000_000},
        )
        mcp.add_transform(CodeMode(sandbox_provider=_sandbox))
    except Exception as exc:  # pragma: no cover - depende do ambiente
        print(
            f"[google-ads-mcp] Code Mode indisponível ({exc}); "
            f"expondo as {len(core.ALL_TOOLS)} tools diretamente.",
            file=sys.stderr,
        )


def main():
    """Entry point de CLI (console_script)."""
    mcp.run()


if __name__ == "__main__":
    main()
