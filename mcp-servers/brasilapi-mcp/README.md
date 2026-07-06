# brasilapi-mcp

Servidor MCP para a [BrasilAPI](https://brasilapi.com.br) — API pública brasileira, **sem autenticação**. Gerado com a skill `mcp-creator` (spec-driven + Code Mode).

## O que faz

Uma spec (`specs/brasilapi_spec.json`, 12 grupos) vira **17 tools async** automaticamente via `generator.py`. O `server.py` registra tudo e aplica **Code Mode**, colapsando em 3 meta-tools (`search` / `get_schema` / `execute`) — o agente vê 3, não 17.

Grupos: CEP, CNPJ, Bancos, DDD, Feriados, ISBN, Taxas (Selic/CDI/IPCA), NCM, PIX, IBGE/UF, Corretoras CVM, Registro.br.

## Setup

```bash
uv venv --python 3.12
uv pip install -e .
python -m brasilapi_mcp.generator   # regenera tools/generated.py a partir da spec
```

## Registrar no Claude Code (escopo user)

Aponte o `~/.claude.json` (chave `mcpServers`) para o entry point do venv:

```json
{
  "mcpServers": {
    "brasilapi": {
      "type": "stdio",
      "command": "<caminho-absoluto>/.venv/bin/brasilapi-mcp",
      "args": [],
      "env": {}
    }
  }
}
```

Depois reabra o Claude Code (`/exit`) e confira `/mcp` → deve mostrar `brasilapi ✓ connected`.

## Requisito de rede

As chamadas batem em `https://brasilapi.com.br`. Em ambientes com allowlist de rede, libere `brasilapi.com.br`.

## Regenerar após mudar a spec

Edite `specs/brasilapi_spec.json` e rode `python -m brasilapi_mcp.generator`. As tools aparecem sozinhas — o gerador não muda.
