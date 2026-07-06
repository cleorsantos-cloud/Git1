#!/usr/bin/env bash
# brasilapi-mcp — instalação de um comando.
# Recria o venv, gera as tools a partir da spec, e registra o servidor
# no ~/.claude.json (escopo user) como stdio, sem token.
#
# Uso: bash scripts/install.sh
# Rodar de qualquer diretório — resolve os caminhos sozinho.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CLAUDE_JSON="${HOME}/.claude.json"

echo "== brasilapi-mcp · install =="
echo "Projeto: $PROJECT_DIR"

# 1) uv (o preflight da skill mcp-creator normalmente já garante isso)
export PATH="$HOME/.local/bin:$PATH"
if ! command -v uv >/dev/null 2>&1; then
  echo "⚙  uv não encontrado — instalando (astral.sh)..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi
echo "✅ uv $(uv --version 2>/dev/null | awk '{print $2}')"

cd "$PROJECT_DIR"

# 2) venv + install (idempotente — reaproveita se já existir)
echo "-- criando/atualizando venv --"
uv venv --python 3.12 --allow-existing
uv pip install -e .

# 3) regenera as tools a partir da spec (idempotente)
echo "-- gerando tools a partir da spec --"
PYTHONPATH="$PROJECT_DIR/src" "$PROJECT_DIR/.venv/bin/python" -m brasilapi_mcp.generator

ENTRY="$PROJECT_DIR/.venv/bin/brasilapi-mcp"
if [ ! -x "$ENTRY" ]; then
  echo "❌ entry point não encontrado em $ENTRY" >&2
  exit 1
fi

# 4) registra em ~/.claude.json (escopo user), preservando outros MCPs já configurados
echo "-- registrando em $CLAUDE_JSON --"
python3 - "$ENTRY" "$CLAUDE_JSON" <<'PY'
import json, shutil, sys, os

entry, claude_json = sys.argv[1], sys.argv[2]

if os.path.exists(claude_json):
    shutil.copy(claude_json, claude_json + ".bak")
    d = json.load(open(claude_json))
else:
    d = {}

d.setdefault("mcpServers", {})["brasilapi"] = {
    "type": "stdio",
    "command": entry,
    "args": [],
    "env": {},
}
json.dump(d, open(claude_json, "w"), indent=2)
print(f"registrado. mcpServers: {list(d['mcpServers'].keys())}")
PY

echo ""
echo "== instalação concluída =="
echo "Próximos passos:"
echo "  1. Saia e reabra o Claude Code (/exit) para carregar o servidor."
echo "  2. Rode /mcp e confira: brasilapi ✓ connected"
echo "  3. Se a política de rede deste ambiente bloquear domínios externos,"
echo "     libere 'brasilapi.com.br' para as chamadas reais funcionarem."
