"""BrasilAPI MCP server. Registers all generated tools and applies Code Mode
when available, collapsing them into 3 meta-tools (search / get_schema / execute).
"""

import os

from fastmcp import FastMCP

from brasilapi_mcp.tools import generated

mcp = FastMCP(
    "brasilapi",
    instructions=(
        "MCP da BrasilAPI — API pública brasileira, sem autenticação. "
        "Consulta CEP, CNPJ, bancos, DDD, feriados, ISBN, taxas (Selic/CDI/IPCA), "
        "NCM, participantes PIX, UFs do IBGE, corretoras da CVM e domínios .br."
    ),
)

for _tool in generated.ALL_TOOLS:
    mcp.tool(_tool)

# Code Mode collapses all tools into 3 meta-tools (search/get_schema/execute).
# Opt out with BRASILAPI_MCP_NO_CODEMODE=1 if the sandbox is unavailable.
if os.environ.get("BRASILAPI_MCP_NO_CODEMODE") != "1":
    try:
        from fastmcp.experimental.transforms.code_mode import (
            CodeMode,
            MontySandboxProvider,
        )

        _sandbox = MontySandboxProvider(
            limits={"max_duration_secs": 30, "max_memory": 100_000_000},
        )
        mcp.add_transform(CodeMode(sandbox_provider=_sandbox))
    except Exception as exc:  # pragma: no cover - environment dependent
        import sys

        print(
            f"[brasilapi-mcp] Code Mode indisponível ({exc}); "
            f"expondo as {len(generated.ALL_TOOLS)} tools diretamente.",
            file=sys.stderr,
        )


def main():
    """CLI entry point (console_script)."""
    mcp.run()


if __name__ == "__main__":
    main()
