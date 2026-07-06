#!/usr/bin/env bash
# mcp-creator — preflight de pré-requisitos de sistema (Python 3.10+, uv).
# O Claude roda isso no Step 0 do skill; o usuário também pode rodar na mão.
# A busca de specs (Exa) é conferida/conectada pelo Claude no Step 0, não aqui.

echo "== mcp-creator · preflight =="

# 1) Python 3.10+
if command -v python3 >/dev/null 2>&1; then
  PYV=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null)
  MAJ=${PYV%%.*}; MIN=${PYV##*.}
  if [ "${MAJ:-0}" -eq 3 ] && [ "${MIN:-0}" -ge 10 ]; then
    echo "✅ Python $PYV"
  else
    echo "⚠  Python $PYV encontrado — o FastMCP precisa de 3.10+."
    echo "   Mac:  brew install python@3.12"
    echo "   Outros: https://www.python.org/downloads/"
  fi
else
  echo "❌ Python 3 não encontrado."
  echo "   Mac:  brew install python@3.12"
  echo "   Outros: https://www.python.org/downloads/"
fi

# 2) uv (gerenciador de pacotes Python usado no scaffold)
if command -v uv >/dev/null 2>&1; then
  echo "✅ uv $(uv --version 2>/dev/null | awk '{print $2}')"
else
  echo "⚙  uv não encontrado — instalando (astral.sh)..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
  if command -v uv >/dev/null 2>&1; then
    echo "✅ uv instalado ($(uv --version 2>/dev/null | awk '{print $2}'))"
  else
    echo "⚠  uv instalado, mas fora do PATH desta sessão."
    echo "   Rode:  export PATH=\"\$HOME/.local/bin:\$PATH\"   (ou reabra o terminal)"
  fi
fi

echo "== preflight de sistema concluído =="
echo "Próximo: o Claude confere a busca de specs (Exa) no Step 0 e segue pro Step 1."
