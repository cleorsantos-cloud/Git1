#!/usr/bin/env bash
# google-ads-mcp — instalação de um comando.
# Cria o venv, instala o pacote e registra o servidor no ~/.claude.json
# (escopo user) como stdio, lendo as credenciais do ambiente.
#
# Uso:
#   export GOOGLE_ADS_DEVELOPER_TOKEN=...
#   export GOOGLE_ADS_CLIENT_ID=...
#   export GOOGLE_ADS_CLIENT_SECRET=...
#   export GOOGLE_ADS_REFRESH_TOKEN=...
#   export GOOGLE_ADS_LOGIN_CUSTOMER_ID=3845391611
#   bash scripts/install.sh
#
# Rodar de qualquer diretório — resolve os caminhos sozinho.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CLAUDE_JSON="${HOME}/.claude.json"

echo "== google-ads-mcp · install =="
echo "Projeto: $PROJECT_DIR"

# 1) checagem das credenciais (não imprime valores)
FALTANDO=()
for VAR in GOOGLE_ADS_DEVELOPER_TOKEN GOOGLE_ADS_CLIENT_ID GOOGLE_ADS_CLIENT_SECRET \
           GOOGLE_ADS_REFRESH_TOKEN GOOGLE_ADS_LOGIN_CUSTOMER_ID; do
  if [ -z "${!VAR:-}" ]; then FALTANDO+=("$VAR"); fi
done
if [ ${#FALTANDO[@]} -gt 0 ]; then
  echo "❌ variáveis ausentes: ${FALTANDO[*]}" >&2
  echo "   Exporte todas antes de rodar. Veja o README." >&2
  exit 1
fi
echo "✅ credenciais presentes no ambiente"

# 2) uv
export PATH="$HOME/.local/bin:$PATH"
if ! command -v uv >/dev/null 2>&1; then
  echo "⚙  uv não encontrado — instalando (astral.sh)..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi
echo "✅ uv $(uv --version 2>/dev/null | awk '{print $2}')"

cd "$PROJECT_DIR"

# 3) venv + install (idempotente)
echo "-- criando/atualizando venv --"
uv venv --python 3.12 --allow-existing
uv pip install -e .

ENTRY="$PROJECT_DIR/.venv/bin/google-ads-mcp"
if [ ! -x "$ENTRY" ]; then
  echo "❌ entry point não encontrado em $ENTRY" >&2
  exit 1
fi

# 4) registra em ~/.claude.json (escopo user), preservando os outros MCPs
echo "-- registrando em $CLAUDE_JSON --"
python3 - "$ENTRY" "$CLAUDE_JSON" <<'PY'
import json, os, shutil, sys

entry, claude_json = sys.argv[1], sys.argv[2]

if os.path.exists(claude_json):
    shutil.copy(claude_json, claude_json + ".bak")
    with open(claude_json) as fh:
        d = json.load(fh)
else:
    d = {}

d.setdefault("mcpServers", {})["google-ads"] = {
    "type": "stdio",
    "command": entry,
    "args": [],
    "env": {
        "GOOGLE_ADS_DEVELOPER_TOKEN": os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
        "GOOGLE_ADS_CLIENT_ID": os.environ["GOOGLE_ADS_CLIENT_ID"],
        "GOOGLE_ADS_CLIENT_SECRET": os.environ["GOOGLE_ADS_CLIENT_SECRET"],
        "GOOGLE_ADS_REFRESH_TOKEN": os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
        "GOOGLE_ADS_LOGIN_CUSTOMER_ID": os.environ["GOOGLE_ADS_LOGIN_CUSTOMER_ID"],
        "GOOGLE_ADS_API_VERSION": os.environ.get("GOOGLE_ADS_API_VERSION", ""),
        "GOOGLE_ADS_MCP_ALLOW_WRITES": os.environ.get("GOOGLE_ADS_MCP_ALLOW_WRITES", ""),
    },
}
with open(claude_json, "w") as fh:
    json.dump(d, fh, indent=2)
print(f"registrado. mcpServers: {list(d['mcpServers'].keys())}")
PY

echo ""
echo "== instalação concluída =="
echo "Próximos passos:"
echo "  1. Saia e reabra o Claude Code (/exit) para carregar o servidor."
echo "  2. Rode /mcp e confira: google-ads ✓ connected"
echo "  3. Teste com list_client_accounts — deve listar as contas da MCC."
echo "  4. Escrita só liga com GOOGLE_ADS_MCP_ALLOW_WRITES=1."
echo "  5. Em ambiente com allowlist de rede, libere googleads.googleapis.com"
echo "     e oauth2.googleapis.com."
