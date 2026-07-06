---
name: mcp-creator
description: "Build MCP servers from API specs (OpenAPI, Postman, SDK codegen JSON). This skill should be used whenever the user asks to \"create an MCP server\", \"build MCP tools\", \"generate MCP from API\", \"wrap an API as MCP\", \"turn this API into tools\", \"make an MCP for [service]\", or mentions converting API specs/documentation into MCP tools. Also trigger when the user has API spec files (JSON, YAML, Postman collections) and wants to expose them through FastMCP, or when building spec-driven code generators for any REST API. Use this skill even if the user just says \"MCP\" combined with any API name (e.g., \"MCP for Stripe\", \"MCP for GitHub\", \"Shopify MCP\")."
metadata:
  version: 0.1.0
---

# MCP Creator

Build production-ready MCP servers from API specifications using FastMCP with spec-driven code generation.

## Overview

This skill encodes the battle-tested pattern from building meta-ads-mcp-codemode (1,265 tools from 119 specs). The approach: parse API specs → generate async Python tool functions → register with FastMCP → apply Code Mode for large tool counts.

## The Process

### Step 0 — Preflight & Setup (rode ANTES de tudo)

O skill roda dentro do Claude Code, então o Claude **se auto-provisiona** — não faça o usuário instalar nada na mão. Antes de gerar qualquer coisa, garanta os pré-requisitos:

**1. Python 3.10+ e uv** (dependências de sistema) — rode via Bash:
```bash
bash assets/setup.sh
```
O script confere Python 3.10+ e **instala o `uv` se faltar**. Se o Python for < 3.10, oriente: Mac `brew install python@3.12`, ou python.org/downloads.

**2. Busca de specs (Exa) — caminho principal:**
Confira se a Exa está disponível neste turno: `ToolSearch({ query: "exa", max_results: 5 })`.
- **`web_search_exa` aparece** → use na discovery (o aluno normalmente já conectou a Exa no Kit de Partida da F1).
- **Não aparece** → peça pro usuário conectar (setup único, uma vez só):
  > "Pra achar as specs das APIs eu uso a busca da Exa. Cria uma conta grátis em https://exa.ai (sem cartão) e me cola a API key aqui."

  Com a key, conecte por ele no **terminal puro** (fora do Claude):
  ```bash
  claude mcp add --transport http exa "https://mcp.exa.ai/mcp?tools=web_search_exa,web_fetch_exa&exaApiKey=SUA_KEY"
  ```
  Depois reabra o Claude.
- **Rede de segurança:** se o usuário não quiser conectar agora, **NÃO trave** — caia pro `WebSearch` nativo na discovery (Níveis 1/2/3). A busca nativa acha specs bem o suficiente; só perde a consistência/qualidade da Exa.

Só depois do preflight, siga pro Step 1.

### Step 1: Research & Discovery (3 níveis)

Se o usuário já tem specs prontas, detectar o formato e pular pro Step 2:

| Source | Format | Adapter |
|--------|--------|---------|
| OpenAPI/Swagger | JSON/YAML with `paths` | OpenAPI adapter |
| Postman Collection | JSON with `item[].request` | Postman adapter |
| SDK Codegen | JSON with `apis[]` and `fields[]` | Direct (native format) |
| Raw docs/URL | HTML/Markdown | Scrape → manual spec creation |

Se não tem specs, rodar o **pipeline de 3 níveis** (consultar `references/spec-discovery.md` para detalhes completos):

**Nível 1 — Busca de Specs** (paralelo): APIs.guru + Postman + vendor repos + SwaggerHub + GitHub. Todas as fontes ao mesmo tempo via Exa (`web_search_exa`). Apresentar achados ao usuário para aprovação antes de prosseguir.

**Nível 2 — Busca de Contexto** (paralelo, após aprovação): docs oficiais da API, changelog, rate limits, auth patterns, SDKs existentes, enum definitions. Entender a API profundamente antes de gerar código. Apresentar resumo ao usuário.

**Nível 3 — Complemento** (após primeiro draft): gaps identificados durante geração — endpoints faltando, enums incompletos, edge cases. Busca cirúrgica nos pontos específicos.

Human-in-the-loop entre cada nível: apresentar o que achou, usuário aprova antes de prosseguir.

### Step 2: Scaffold the Project

Create the project structure. Consult `references/architecture.md` for the full layout.

```bash
mkdir -p my-api-mcp/{specs,src/my_api_mcp/tools,scripts,tests}
touch my-api-mcp/src/my_api_mcp/__init__.py my-api-mcp/src/my_api_mcp/tools/__init__.py
```

Key files to create:
1. **`pyproject.toml`** — Package metadata + dependencies
2. **`src/my_api_mcp/client.py`** — Async HTTP client (start from `assets/client_template.py`)
3. **`src/my_api_mcp/generator.py`** — Spec parser + code generator
4. **`src/my_api_mcp/server.py`** — FastMCP entry point

Customize the client template:
- Replace `{{API_NAME}}`, `{{BASE_URL}}`, `{{API_VERSION}}`, `{{ENV_VAR_TOKEN}}`
- Adapt auth strategy (bearer token, API key, OAuth2)
- Adapt pagination pattern (cursor-based, offset, link headers)

### Step 3: Write the Generator

The generator is the core — it reads spec files and outputs Python async functions. Consult `references/generator-patterns.md` for complete patterns.

Key decisions:
1. **Function naming**: `{method}_{entity}_{edge}` (e.g., `get_campaign_adsets`)
2. **Parameter handling**: Required params as positional, optional as keyword with `None` default
3. **Reserved words**: Use `_safe_param_name()` to append `_` to Python keywords
4. **Enum values**: Include ALL enum values in docstrings — never truncate. This is critical because agents discover valid parameter values through `get_schema`, and truncated values mean the agent can't find what it needs
5. **Field hints**: For GET endpoints, list available fields in the `fields` parameter docstring
6. **Structured output (condicional)**: emit `outputSchema` só quando a spec fornece o schema de resposta (OpenAPI). SDK codegen/Postman/GET fields-driven → mantém `-> str`. Ver `references/generator-patterns.md` §9.

### Step 4: Generate Tools

Run the generator to produce tool modules:

```python
python -m my_api_mcp.generator
```

Verify:
- Each module has the right function count
- Functions have proper signatures and docstrings
- Enum values appear in docstrings
- No duplicate function names across modules

### Step 5: Configure the Server

```python
from fastmcp import FastMCP
from fastmcp.experimental.transforms.code_mode import CodeMode, MontySandboxProvider

mcp = FastMCP("my-api", instructions="...")

# Code Mode is always enabled — collapses all tools into 3 meta-tools
# (search, get_schema, execute) for a consistent agent interface
sandbox = MontySandboxProvider(
    limits={"max_duration_secs": 30, "max_memory": 100_000_000},
)
mcp.add_transform(CodeMode(sandbox_provider=sandbox))

def main():
    """CLI entry point — called by the [project.scripts] command."""
    mcp.run()
```

**Code Mode is always enabled by default.** It collapses all tools into 3 meta-tools (`search`, `get_schema`, `execute`), which scales better regardless of tool count and provides a consistent interface for agents.

### Step 6: Test (você roda, não o usuário)

**Quem roda os testes é VOCÊ via Bash. Não cole comandos pro usuário rodar manualmente.**

**Passo 1 — Smoke test sem token** (só confere imports e CodeMode):

```bash
cd <project-dir> && uv venv && uv pip install -e .
.venv/bin/python -c "
from <package>.server import mcp
import asyncio
async def check():
    tools = await mcp.list_tools()
    assert len(tools) == 3, f'Esperava 3 meta-tools (CodeMode), achei {len(tools)}'
    print('✓ CodeMode OK — 3 meta-tools registradas')
asyncio.run(check())
"
```

Se falhar com `Monty.__new__() got unexpected keyword argument 'external_functions'`, é o pin do `pydantic-monty==0.0.7` que não foi respeitado — refaça o `uv pip install` ou aceite que o fastmcp resolveu pra versão mais antiga compatível.

**Passo 2 — Live test com token** (uma chamada real contra a API):

1. Pedir o token ao usuário **uma única vez** com mensagem do tipo: *"Cola seu `<NOME>_API_TOKEN` que eu rodo um smoke test contra a API real e em seguida registro o servidor no Claude Code."*

2. Criar `scripts/smoke_test.py` com 1-2 chamadas read-only (ex.: `list_*` com `limit=2`).

3. **Você** roda o script via Bash, passando o token inline:

```bash
cd <project-dir> && <NOME>_API_TOKEN="<valor-colado>" .venv/bin/python scripts/smoke_test.py
```

4. Apresentar a saída ao usuário. Se houver erro 401/403, o token tá errado — pedir de novo. Se 200, prosseguir pro Step 7 **com o mesmo token** (não pedir de novo).

### Step 7: Registrar localmente no Claude Code (OBRIGATÓRIO)

**NUNCA use `claude mcp add` via CLI** — a flag `-e` é variadic e engole o nome do server, gerando erros confusos como `missing required argument 'name'`. Edite `~/.claude.json` direto.

**Procedimento:**

1. **Reusar o token coletado no Step 6** — não pedir de novo. Se chegou aqui, o smoke test live passou com esse token, então tá certo.

2. Editar `~/.claude.json` programaticamente (faz backup, lê, injeta, escreve):

```python
import json, shutil
p = '/Users/<USUARIO>/.claude.json'
shutil.copy(p, p + '.bak')
d = json.load(open(p))
d.setdefault('mcpServers', {})['<nome-do-mcp>'] = {
    "type": "stdio",
    "command": "/caminho/absoluto/.venv/bin/<entry-point>",
    "args": [],
    "env": {
        "<API_TOKEN_ENV>": "<valor-coletado-do-usuario>"
    }
}
json.dump(d, open(p, 'w'), indent=2)
```

3. Verificar com `claude mcp list | grep <nome-do-mcp>` — esperar `✓ Connected` no output.

4. Avisar o usuário que precisa **sair e abrir de novo o Claude Code** (`/exit`) pra carregar o servidor — sem isso ele não aparece nas tools.

**Por que editar direto e não usar `claude mcp add`:** o CLI tem UX ruim com flags variadic. Quando você pode fazer 3 linhas de Python sem ambiguidade, faça.

**Se o arquivo já tiver muitos MCPs**: o Python script preserva tudo via merge — só adiciona a chave nova. O `.bak` te protege se algo der errado.

### Step 8: Package and Document

1. Update `pyproject.toml` version
2. Write CHANGELOG.md
3. Add maintenance scripts (`scripts/update_and_regenerate.sh`)
4. Document in README: setup, Claude Desktop config, endpoint coverage table

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| `execute` quebra com `Monty.__new__() got unexpected keyword argument 'external_functions'` | `pydantic-monty==0.0.8` quebrou o CodeMode. Pin `"pydantic-monty==0.0.7"` no pyproject.toml |
| Agent can't find enum values | Include ALL values in docstrings, never truncate |
| `SyntaxError` from reserved words | Use `_safe_param_name()` for all parameter names |
| `list<enum>` not resolved | Extract inner name: `ptype[5:-1]` from `list<name>` |
| Duplicate function names | Prefix with entity name: `get_campaign_adsets` not `get_adsets` |
| Rate limits during generation | Generator creates static code — rate limits only affect runtime |

## Additional Resources

### Reference Files
- **`references/architecture.md`** — Project structure, pipeline, dependencies, design decisions
- **`references/generator-patterns.md`** — Spec parsing, function generation, adapters for OpenAPI/Postman
- **`references/example-brasilapi.md`** — Exemplo trabalhado e rodável: spec da BrasilAPI (12 grupos) → 16 tools geradas → Code Mode, com exemplos de uso reais pra demo

### Asset Files
- **`assets/client_template.py`** — Starter HTTP client with auth, pagination, rate limiting

### Reference Implementation
Public starter repo: **https://github.com/thaleslaray/meta-ads-claude-starter** — demonstrates every pattern in this skill (spec-driven generation, Code Mode, FastMCP setup). Use como base de comparação quando estiver construindo MCPs complexos.
