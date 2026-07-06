# Exemplo trabalhado — MCP da BrasilAPI (codegen em escala)

Exemplo mínimo e **rodável** do padrão do mcp-creator: uma **spec** vira **N tools** automaticamente (0 escritas à mão), e o **Code Mode** colapsa tudo em 3 meta-tools. Alvo: [BrasilAPI](https://brasilapi.com.br) — API pública brasileira, sem auth.

> Por que esse exemplo: com 2 endpoints o mcp-creator é overkill (escrever à mão é mais rápido). O ganho aparece **em escala** — aqui, **16 tools de 12 grupos** saem de uma spec, e o gerador (~50 linhas) não muda se virarem 200.

## Os 4 arquivos

```
brasilapi_spec.json   # a spec: 12 grupos (Cep, Cnpj, Bank, Ddd, Feriado, Cptec,
                      #   Isbn, Taxa, Ncm, Pix, IbgeUf, Corretora, RegistroBr)
client.py             # cliente HTTP async (httpx), ~10 linhas
generator.py          # lê a spec e EMITE tools_generated.py (o coração)
server.py             # FastMCP + Code Mode
```

Fluxo: `python generator.py` → gera `tools_generated.py` com **16 funções async** → `server.py` registra e aplica Code Mode.

```
✓ geradas 16 tools em tools_generated.py
Code Mode: True | expostas ao agente: 3 (search/get_schema/execute) | reais por baixo: 16
```

O agente nunca vê 16 tools inflando o contexto — vê 3. Ele faz `search` ("quero consultar um CEP"), pega o schema, e `execute`. É o que segura o contexto quando a API é gigante.

## Como registrar (local, stdio)

```bash
bash ~/.claude/skills/mcp-creator/assets/setup.sh --skill brasilapi   # cria venv + deps
# depois: registrar em ~/.claude.json apontando pro server.py (ver Step 7 do SKILL.md)
```

## Exemplos de uso — pra mostrar pra galera

Depois de registrado, é só **conversar em português**. O Claude usa as 3 meta-tools por baixo pra achar e rodar a função certa. Perguntas reais e o que volta (dados reais, jul/2026):

| Você pergunta | Tool gerada usada | Resposta real |
|---|---|---|
| "Qual a Selic e o CDI hoje?" | `list_taxa` | **Selic 14,25% · CDI 14,15% · IPCA 4,72%** |
| "Que endereço é o CEP 01310-100?" | `get_cep` | Avenida Paulista, Bela Vista, São Paulo/SP |
| "Que banco é o código 341? E o 260?" | `get_bank` | **341 = Itaú Unibanco** · 260 = Nu Pagamentos |
| "Quais cidades são DDD 71?" | `get_ddd` | Bahia — 15 cidades (Vera Cruz, Simões Filho, Saubara…) |
| "Quais os feriados nacionais de 2026?" | `list_feriado` | 01/01 Confraternização · 17/02 Carnaval · 03/04 Sexta Santa · 05/04 Páscoa… (13 no total) |
| "Acha o livro do ISBN 9788533613379" | `get_isbn` | **O Senhor dos Anéis — A Sociedade do Anel** (Tolkien) |
| "A empresa do CNPJ 47.960.950/0001-21?" | `get_cnpj` | Magazine Luiza S/A — Franca/SP |
| "O domínio brasilapi.com.br está registrado?" | `get_registro_br` | REGISTERED |
| "Lista as corretoras da CVM" | `list_corretora` | 375 corretoras |
| "Quantos bancos existem no Brasil?" | `list_bank` | 479 |

Ideias de demo ao vivo (encadeando tools — o agente resolve sozinho):
- *"Sou de Salvador (DDD 71), qual a Selic e tem feriado essa semana?"* → `get_ddd` + `list_taxa` + `list_feriado`.
- *"Consulta o CNPJ da Magazine Luiza e me diz a cidade e o CEP dela."* → `get_cnpj` → `get_cep`.

Personas da imersão: **contador** (CNPJ, NCM, taxas), **advogado** (CNPJ de partes, registro.br), **gestor** (bancos/PIX pra conciliação).

## A lição (o motivo do exemplo)

| Cenário | Melhor ferramenta |
|---|---|
| 2 endpoints | escrever à mão (mcp-creator é overkill) |
| **16 endpoints** (este) | **mcp-creator** — codegen + Code Mode já compensam |
| 200 endpoints (Stripe, Meta) | **só** mcp-creator não explode; o gerador é o mesmo |

O gerador é escrito **uma vez** e é indiferente ao tamanho da spec. Adicionar um grupo = adicionar uma entrada no JSON; as tools aparecem sozinhas. Foi esse padrão que gerou 1.265 tools de 119 specs no meta-ads-mcp.
