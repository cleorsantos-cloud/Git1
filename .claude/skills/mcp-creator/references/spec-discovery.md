# MCP Creator — Spec Discovery Reference

## Overview

Finding API specs is the critical first step. Without specs, there's no code generation. This document covers a 3-level research pipeline — inspired by the hiring process — that goes from broad discovery to deep understanding to surgical gap-filling, with human approval between each level.

## Pipeline de 3 Níveis

```
Nível 1: Busca de Specs (paralelo)
    │ APIs.guru + Postman + vendor + SwaggerHub + GitHub
    │ Apresentar achados → usuário aprova
    ▼
Nível 2: Busca de Contexto (paralelo)
    │ Docs oficiais + auth + rate limits + enums + SDKs
    │ Apresentar resumo → usuário aprova
    ▼
Nível 3: Complemento (cirúrgico)
    │ Gaps identificados durante geração
    │ Endpoints faltando + enums incompletos + edge cases
    ▼
Specs completas → pronto para gerar
```

---

## Nível 1: Busca de Specs

Objetivo: encontrar specs machine-readable da API. Rodar TODAS as fontes em paralelo (não sequencial).

### Busca paralela via Exa

```
web_search_exa: "{api-name} openapi spec" OR "{api-name} swagger.json" OR "{api-name} postman collection" OR "{api-name} sdk codegen"
```

### Fontes (todas ao mesmo tempo)

#### APIs.guru — OpenAPI Directory

The "Wikipedia for Web APIs". Community-maintained, 2,000+ specs.

```bash
# Browse available APIs
curl -s https://api.apis.guru/v2/list.json | python3 -c "
import json, sys
apis = json.load(sys.stdin)
for name in sorted(apis.keys())[:20]:
    print(f'{name}: {apis[name][\"preferred\"]}')
"

# Get a specific spec
curl -s "https://api.apis.guru/v2/specs/stripe.com/2023-10-16/openapi.json" > stripe.json

# Or clone the whole directory (sparse)
git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/APIs-guru/openapi-directory.git
cd openapi-directory
git sparse-checkout set APIs/{service-name}
```

**What's there**: Stripe, GitHub, Slack, Twilio, AWS, Google, Microsoft, Shopify, HubSpot, Notion, Asana, Jira, and hundreds more.

**Format**: OpenAPI 2.0 or 3.x JSON/YAML.

#### Postman API Network

Massive directory of API collections, many official from the API vendors themselves.

**How to find**:
- Browse: `https://www.postman.com/explore`
- Search for API name
- Look for "Official" badge — these are maintained by the API company
- Export as Collection v2.1 JSON

**What's there**: Meta, Google, Stripe, Twilio, AWS, Salesforce, HubSpot, Notion, GitHub, Shopify, and thousands more.

**Format**: Postman Collection v2.1 JSON with `item[].request` structure.

#### Vendor's Own Spec

Many APIs publish their spec directly:

| Pattern | Example |
|---------|---------|
| `/openapi.json` | `https://api.example.com/openapi.json` |
| `/swagger.json` | `https://api.example.com/swagger.json` |
| `/v3/api-docs` | Spring Boot apps |
| `/api/v2/openapi.yaml` | `https://api.example.com/api/v2/openapi.yaml` |
| GitHub repo | `github.com/{company}/openapi` or `{company}-api-specs` |

**GitHub search strategies**:
```
https://github.com/search?q={company}+openapi&type=repositories
https://github.com/search?q={company}+swagger&type=repositories
https://github.com/search?q={company}-sdk-codegen&type=repositories
```

**Known vendor repos**:

| API | Repo |
|-----|------|
| Meta/Facebook | `facebook/facebook-business-sdk-codegen` (951 specs) |
| Meta/Facebook | `facebook/openapi` (consolidated OpenAPI) |
| Stripe | `stripe/openapi` (official) |
| GitHub | `github/rest-api-description` (official) |
| Twilio | `twilio/twilio-oai` (official OpenAPI) |
| AWS | `aws/aws-sdk-js` (API models in JSON) |
| Google | `googleapis/google-api-go-client` (discovery docs) |
| Shopify | `Shopify/shopify-api-js` (REST resources) |
| HubSpot | `HubSpot/HubSpot-public-api-spec-collection` |

#### SwaggerHub Public Catalog

```bash
# Search for an API
curl -s "https://api.swaggerhub.com/apis?query=stripe&limit=5" | python3 -m json.tool

# Get a specific spec
curl -s "https://api.swaggerhub.com/apis/{owner}/{api}/{version}" \
  -H "Accept: application/json"
```

#### Scrape Documentation (se nenhuma spec machine-readable encontrada)

```python
# Using Firecrawl MCP
result = firecrawl_scrape(url="https://docs.example.com/api/reference")

# Or firecrawl_map to discover all doc pages
sitemap = firecrawl_map(url="https://docs.example.com/api/")
```

After scraping, manually extract:
- Base URL and versioning
- Endpoints (path + method)
- Parameters (name, type, required)
- Auth mechanism
- Response format

### Entrega do Nível 1

Apresentar ao usuário:

```
Specs encontradas para {API}:

| Fonte | Formato | Endpoints | Qualidade |
|-------|---------|-----------|-----------|
| APIs.guru | OpenAPI 3.0 | 47 | Alta (oficial) |
| Postman | Collection v2.1 | 52 | Média (comunidade) |
| Vendor GitHub | SDK codegen JSON | 120+ | Alta (951 specs) |

Recomendação: usar {fonte} como base principal + {fonte} para complementar enums.

Aprovar para prosseguir ao Nível 2?
```

**Não prosseguir sem aprovação do usuário.**

---

## Nível 2: Busca de Contexto

Objetivo: entender a API profundamente antes de gerar código. Specs sozinhas não bastam — precisamos saber como a API realmente funciona.

### Pesquisas paralelas

Rodar em paralelo via Exa + Firecrawl:

#### 2A — Auth & Infraestrutura

```
web_search_exa: "{api-name} authentication oauth2 API key bearer token"
web_search_exa: "{api-name} rate limits throttling quotas"
web_search_exa: "{api-name} API versioning changelog breaking changes 2025 2026"
```

Extrair:
- Mecanismo de auth (bearer, API key, OAuth2, HMAC)
- Rate limits (requests/min, quotas diárias)
- Base URL e versionamento
- Headers obrigatórios

#### 2B — SDKs & Tooling Existente

```
web_search_exa: "{api-name} python SDK async client library"
web_search_exa: "{api-name} MCP server existing"
```

Verificar:
- Existe SDK oficial? (pode revelar patterns de auth, pagination, error handling)
- Já existe MCP server pra essa API? (evitar duplicação)
- Bibliotecas wrapper populares (podem ter insights sobre edge cases)

#### 2C — Enums & Tipos

```
web_search_exa: "{api-name} API enum values status types"
```

Se a spec não inclui enum values:
- Raspar docs da API com Firecrawl para extrair valores válidos
- Buscar no SDK oficial por definições de tipos/constantes
- Criar `enum_types.json` manualmente a partir dos docs

Sem enum values nos docstrings, o agente usando Code Mode não consegue descobrir valores válidos via `get_schema`. Isso é crítico.

#### 2D — Pagination & Error Handling

```
web_search_exa: "{api-name} API pagination cursor offset next page"
web_search_exa: "{api-name} API error codes error handling"
```

Extrair:
- Padrão de paginação (cursor, offset, link headers)
- Formato de erros (status codes, error objects)
- Retry strategies recomendadas

### Entrega do Nível 2

Apresentar ao usuário:

```
Contexto da API {name}:

Auth: Bearer token via env var {VAR_NAME}
Rate limits: 200 req/min, 5000/dia
Pagination: cursor-based (campo "next" no response)
Base URL: https://api.example.com/v2/
Enums: 23 tipos encontrados nos docs
SDK: Python oficial existe (referência para patterns)
MCP existente: Não encontrado

Gaps identificados:
- 5 endpoints sem documentação de parâmetros
- Enum "status" tem valores diferentes entre docs e spec

Aprovar para começar a gerar?
```

**Não prosseguir sem aprovação do usuário.**

---

## Nível 3: Complemento (pós-geração)

Objetivo: após gerar o primeiro draft dos tools, identificar e preencher gaps específicos.

### Quando rodar

Após o generator produzir os módulos Python, revisar:

1. **Endpoints sem parâmetros** — spec tinha endpoint mas sem params. Buscar nos docs.
2. **Enums incompletos** — docstring mostra `str` em vez de valores. Buscar valores reais.
3. **Edges internas/deprecadas** — endpoints que existem na spec mas não fazem sentido expor. Adicionar ao `SKIP_EDGES`.
4. **Campos faltando** — `{ENTITY}_FIELDS` com poucos campos. Verificar se spec está incompleta.
5. **Auth edge cases** — endpoints que precisam de permissões especiais ou scopes diferentes.

### Busca cirúrgica

Diferente dos níveis 1 e 2 (broad search), o nível 3 é cirúrgico — busca só nos pontos específicos:

```
web_search_exa: "{api-name} {endpoint-name} parameters documentation"
firecrawl_scrape: "https://docs.example.com/api/{endpoint-name}"
```

### Entrega do Nível 3

```
Gaps preenchidos:

| Gap | Resolução |
|-----|-----------|
| /users/{id}/posts sem params | Encontrados: limit, since, fields |
| Enum "campaign_status" incompleto | Adicionados: PAUSED, ARCHIVED, DELETED |
| Edge "activities" interna | Adicionado ao SKIP_EDGES |

Regenerar tools com specs atualizadas?
```

---

## Spec Format Detection

Given a JSON file, detect the format:

```python
def detect_spec_format(data: dict) -> str:
    if "openapi" in data or "swagger" in data:
        return "openapi"
    if "info" in data and "item" in data:
        return "postman"
    if "apis" in data and "fields" in data:
        return "sdk_codegen"
    if "paths" in data:
        return "openapi"
    return "unknown"
```

## Spec Quality Checklist

Before feeding specs to the generator, verify:

- [ ] Endpoints have methods (GET/POST/PUT/DELETE)
- [ ] Parameters have names and types
- [ ] Required vs optional is specified
- [ ] Enum values are included (not just "string")
- [ ] Auth mechanism is documented
- [ ] Base URL / API version is clear
- [ ] Response schemas exist (nice to have, not required)

## Combining Multiple Sources

Sometimes the best spec comes from combining sources:

1. **Postman collection** for endpoint structure + example payloads
2. **OpenAPI spec** for parameter types and enums
3. **SDK codegen** for field definitions and edge relationships
4. **Scraped docs** for enum values and business logic

Merge strategy: use the most detailed source for each aspect.
