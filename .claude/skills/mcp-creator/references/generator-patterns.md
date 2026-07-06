# MCP Creator — Generator Patterns

## Table of Contents
1. Spec Parsing
2. Helper Utilities (_snake_case, SKIP_EDGES, Fields constants)
3. Function Generation
4. Parameter Handling
5. Enum Resolution
6. Module Assembly
7. OpenAPI Adapter
8. Postman Adapter
9. Structured Output (`outputSchema`) — condicional

---

## 1. Spec Parsing

### SDK Codegen JSON format

Each spec file represents an API entity (e.g., Campaign.json):

```json
{
  "name": "Campaign",
  "fields": [
    {"name": "id", "type": "string"},
    {"name": "name", "type": "string"},
    {"name": "status", "type": "string"}
  ],
  "apis": [
    {
      "endpoint": "#get",
      "method": "GET",
      "params": []
    },
    {
      "endpoint": "adsets",
      "method": "GET",
      "params": [
        {"name": "effective_status", "type": "list<string>", "required": false}
      ]
    },
    {
      "endpoint": "#update",
      "method": "POST",
      "params": [
        {"name": "name", "type": "string", "required": false},
        {"name": "status", "type": "campaign_status_enum", "required": false}
      ]
    }
  ]
}
```

Key conventions:
- `#get`, `#update`, `#delete` = operations on the entity itself
- Named endpoints (e.g., `adsets`) = edges/relationships
- `fields[]` = readable fields for GET requests

### Spec selection heuristic

Not all spec files have APIs. Filter specs:
```python
specs_with_apis = [s for s in all_specs if len(s.get("apis", [])) >= 2]
```

Specs with 0-1 APIs are usually data structures, not API entities.

---

## 2. Helper Utilities

### CamelCase to snake_case

Used everywhere — entity names, function names, edge names:

```python
import re

def _snake_case(name: str) -> str:
    """Convert CamelCase to snake_case: AdAccount → ad_account."""
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    s = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s)
    return s.lower().replace(" ", "_").replace("-", "_")
```

### Edge filtering

Some edges are internal, deprecated, or not useful. Skip them during generation:

```python
SKIP_EDGES = {
    "activities", "adlabels", "trackingtag",
    "adrules_governed", "userpermissions",
}

# In generation loop:
for api in spec.get("apis", []):
    edge = api.get("endpoint", "")
    if edge in SKIP_EDGES:
        continue
```

Adapt `SKIP_EDGES` per API — these are Meta-specific examples.

### Fields constants

Generate a constant listing all readable fields per entity. Powers the `fields` parameter docstring hint:

```python
def _generate_fields_constant(spec_name: str, fields: list[dict]) -> str:
    field_names = sorted(f["name"] for f in fields if f.get("name"))
    const_name = f"{_snake_case(spec_name).upper()}_FIELDS"
    fields_str = json.dumps(field_names, indent=4)
    return f"{const_name} = {fields_str}\n"
```

Output example:
```python
CAMPAIGN_FIELDS = [
    "id",
    "name",
    "objective",
    "status"
]
```

---

## 3. Function Generation

### Naming convention

| Endpoint | Method | Function Name |
|----------|--------|---------------|
| `#get` | GET | `get_{entity}` |
| `#update` | POST | `update_{entity}` |
| `#delete` | DELETE | `delete_{entity}` |
| `adsets` | GET | `get_{entity}_adsets` |
| `adsets` | POST | `create_{entity}_adsets` |
| `copies` | POST | `copy_{entity}` |

### Function template

```python
async def get_campaign(campaign_id: str, fields: Optional[str] = None) -> str:
    """GET /#get on Campaign.

    Args:
        campaign_id: The ID of the Campaign object.
        fields: Comma-separated list of fields to return. Available: id, name, status, ...
    """
    params = {}
    params["fields"] = fields or "id,name"
    result = await _client.get(f"{campaign_id}", params=params)
    return json.dumps(result, indent=2)
```

### Path templates

- Self operations: `{entity_id}`
- Edge operations: `{entity_id}/{edge_name}`
- Account-scoped: `act_{account_id}/{edge_name}` (special case for AdAccount-like entities)

---

## 4. Parameter Handling

### Python reserved words

These names conflict with Python keywords/builtins. Add trailing underscore (PEP 8):

```python
import keyword
PYTHON_RESERVED = set(keyword.kwlist) | {
    "bytes", "filter", "object", "type", "zip", "id",
    "input", "format", "hash", "list", "map", "set",
}

def _safe_param_name(name: str) -> str:
    return f"{name}_" if name in PYTHON_RESERVED else name
```

The original API name is preserved in the params dict:
```python
# Parameter named "type" in API → "type_" in function signature
if type_ is not None:
    params["type"] = type_  # Original name sent to API
```

### Type mapping

```python
TYPE_MAP = {
    "string": "str", "int": "int", "unsigned int": "int",
    "float": "float", "bool": "bool", "datetime": "str",
    "Object": "str", "map": "str", "file": "str",
    "integer": "int", "number": "float", "boolean": "bool",
    "array": "str",  # JSON string
}
```

Lists and complex objects become `str` (JSON-encoded).

---

## 5. Enum Resolution

### Why it matters

Without enum values in docstrings, the agent using Code Mode can't discover valid parameter values via `get_schema`. This is critical — the agent needs to know that `metric` accepts `reach, views, follows, profile_visits`, not just `str`.

### Resolution logic

```python
ptype_raw = param.get("type", "")
enum_name = ptype_raw

# Extract enum from list<> wrapper
if ptype_raw.startswith("list<") and ptype_raw.endswith(">"):
    enum_name = ptype_raw[5:-1]

# Check if it's an enum type
if "_enum_" in enum_name.lower():
    enum_values = enums.get(enum_name, [])
    if not enum_values:
        enum_values = enums.get(ptype_raw, [])  # Fallback to full type
    if enum_values:
        enum_hint = f" Values: {', '.join(enum_values)}"
```

### Include ALL values

Never truncate enum values. The whole point is discoverability through `get_schema`.

---

## 6. Module Assembly

### Module template

```python
"""Auto-generated API tools — {module_name}."""

import json
from typing import Optional

from my_api_mcp.client import ApiClient

_client = ApiClient()

# ... generated functions ...
```

### Server registration

```python
def _register_generated_tools():
    tools_dir = Path(__file__).parent / "tools"
    skip_modules = {"__init__", "targeting", "generic"}

    for module_path in sorted(tools_dir.glob("*.py")):
        module_name = module_path.stem
        if module_name in skip_modules:
            continue
        module = importlib.import_module(f"my_api_mcp.tools.{module_name}")
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            if inspect.iscoroutinefunction(obj) and not name.startswith("_"):
                mcp.tool(obj)
```

---

## 7. OpenAPI Adapter

Convert OpenAPI 3.x specs to the internal format:

```python
def openapi_to_internal(openapi_spec: dict) -> list[dict]:
    """Convert OpenAPI paths to internal spec format."""
    entities = {}
    for path, methods in openapi_spec.get("paths", {}).items():
        # Extract entity from path: /campaigns/{id} → Campaign
        parts = path.strip("/").split("/")
        entity = parts[0].title().rstrip("s")  # campaigns → Campaign

        for method, operation in methods.items():
            if method.upper() not in ("GET", "POST", "PUT", "DELETE", "PATCH"):
                continue
            api_entry = {
                "endpoint": parts[-1] if len(parts) > 1 else "#get",
                "method": method.upper(),
                "params": _extract_openapi_params(operation),
            }
            entities.setdefault(entity, {"name": entity, "apis": [], "fields": []})
            entities[entity]["apis"].append(api_entry)
    return list(entities.values())
```

---

## 8. Postman Adapter

Convert Postman Collection v2.1:

```python
def postman_to_internal(collection: dict) -> list[dict]:
    """Convert Postman collection items to internal spec format."""
    entities = {}
    for item in collection.get("item", []):
        request = item.get("request", {})
        url = request.get("url", {})
        path_parts = url.get("path", [])
        method = request.get("method", "GET")

        # Extract entity from URL path
        entity = _infer_entity(path_parts)
        endpoint = path_parts[-1] if len(path_parts) > 1 else "#get"

        params = []
        for qp in url.get("query", []):
            params.append({
                "name": qp["key"],
                "type": "string",
                "required": False,
            })

        entities.setdefault(entity, {"name": entity, "apis": [], "fields": []})
        entities[entity]["apis"].append({
            "endpoint": endpoint,
            "method": method,
            "params": params,
        })
    return list(entities.values())
```

---

## 9. Structured Output (`outputSchema`) — condicional

**Regra:** emitir `outputSchema` **só quando a spec fornece o schema da resposta**. Onde não fornece, manter o retorno como `str` (JSON) — NÃO inventar um schema genérico (`dict`/`object` vazio não ajuda o agente e ainda infla a tool).

### Por que condicional
Com `outputSchema`, o FastMCP valida a saída e devolve `structuredContent`; e — via `get_schema` no Code Mode — o agente vê o **formato de retorno** antes de escrever o código do `execute()`, então acerta os campos de primeira. É best practice da spec MCP 2025-11-25. **Mas** isso só vale se o schema for real:

| Fonte da spec | Tem response schema? | Retorno gerado |
|---|---|---|
| **OpenAPI 3.x** (endpoint com schema, não fields-driven) | sim | `TypedDict` → `outputSchema` automático |
| **SDK codegen (Meta) / Postman** | normalmente não | `-> str` (JSON), sem outputSchema |
| **GET com `fields`** (resposta muda conforme os campos pedidos) | shape dinâmico | `-> str` (pular, mesmo em OpenAPI) |

### Detecção (só OpenAPI expõe isso)
```python
def _response_schema(operation: dict) -> dict | None:
    """Schema JSON da resposta 2xx, ou None se a spec não define."""
    for code, resp in (operation.get("responses") or {}).items():
        if str(code).startswith("2"):
            schema = (resp.get("content", {})
                          .get("application/json", {})
                          .get("schema"))
            if schema:
                return schema
    return None
```

### Geração: FastMCP deriva o schema da ANOTAÇÃO de retorno
O FastMCP gera o `outputSchema` sozinho a partir do tipo de retorno da função. Então, quando há schema (e o endpoint não é fields-driven), gere um `TypedDict` e devolva o dict — sem `json.dumps`:

```python
from typing import TypedDict

class GetCampaignResult(TypedDict):
    id: str
    name: str
    status: str

async def get_campaign(campaign_id: str) -> GetCampaignResult:
    """GET /#get on Campaign."""
    return await _client.get(f"{campaign_id}")   # FastMCP valida + devolve structuredContent
```

Sem response schema (Meta SDK codegen, Postman, ou GET fields-driven) → **mantém o fallback atual** (Seção 3): `-> str` com `json.dumps(result, indent=2)`. A decisão é por-endpoint, igual à resolução de enums: pega o ganho onde a spec dá o schema, sem forçar onde não dá.
