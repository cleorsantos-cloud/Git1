# google-ads-mcp

Servidor MCP para a [Google Ads API](https://developers.google.com/google-ads/api/docs/start), feito para operar as contas penduradas na conta administradora (MCC) da Agência Bona Vita. Mesmo padrão do `brasilapi-mcp` deste repositório: FastMCP, cliente `httpx` assíncrono e Code Mode.

## Por que existe

O token de desenvolvedor da agência foi aprovado em julho de 2026 para a MCC **384-539-1611**, com acesso básico e limite de 15 mil operações por dia. Com ele, um único servidor enxerga todas as contas filhas, sem depender de conector de terceiro nem de autorização conta a conta.

## Tools

| Tool | O que faz |
|---|---|
| `list_accessible_customers` | contas que o refresh token alcança |
| `list_client_accounts` | contas filhas da MCC, com nome, moeda e status |
| `list_campaigns` | campanhas com status, orçamento e métricas do período |
| `list_ads` | anúncios com URL final e situação de política, filtrando reprovados |
| `list_keywords` | palavras-chave com cliques, custo e conversões |
| `run_gaql` | consulta GAQL livre, saída de emergência |
| `create_responsive_search_ad` | cria anúncio de pesquisa responsivo |
| `set_ad_status` | pausa, ativa ou remove anúncio |
| `set_campaign_status` | pausa, ativa ou remove campanha |
| `set_campaign_budget` | altera o orçamento diário |

As quatro últimas são de escrita e só funcionam com `GOOGLE_ADS_MCP_ALLOW_WRITES=1`. Sem essa variável o servidor sobe em modo somente leitura e as tools de escrita recusam a chamada. Todas aceitam `validate_only` para simular sem gravar.

## Limite da API que vale conhecer

A URL final de um anúncio publicado **não é editável**. O que a interface chama de editar, por baixo, cria um anúncio novo e remove o antigo. Para consertar destino quebrado, use `create_responsive_search_ad` com a URL correta e depois `set_ad_status` para pausar o antigo.

## Credenciais

Cinco variáveis de ambiente, nenhuma delas no repositório:

| Variável | Onde obter |
|---|---|
| `GOOGLE_ADS_DEVELOPER_TOKEN` | na MCC, em Ferramentas e configurações, Configuração, API Center |
| `GOOGLE_ADS_CLIENT_ID` | credencial OAuth de aplicativo para computador, no Google Cloud Console |
| `GOOGLE_ADS_CLIENT_SECRET` | mesma credencial OAuth |
| `GOOGLE_ADS_REFRESH_TOKEN` | gerado uma vez pelo consentimento, veja abaixo |
| `GOOGLE_ADS_LOGIN_CUSTOMER_ID` | ID da MCC, só dígitos, ex: 3845391611 |

Opcionais: `GOOGLE_ADS_API_VERSION` (padrão `v26`), `GOOGLE_ADS_MCP_ALLOW_WRITES`, `GOOGLE_ADS_MCP_NO_CODEMODE`.

### Gerando o refresh token

Antes, no Google Cloud Console: habilite a Google Ads API no projeto e crie uma credencial OAuth do tipo **App para computador**. O tipo importa, porque ele libera o retorno em `localhost` sem precisar cadastrar URL.

Depois, na sua máquina, com navegador:

```bash
pip install google-auth-oauthlib
python3 scripts/get_refresh_token.py \
  --client-id "SEU_CLIENT_ID" \
  --client-secret "SEU_CLIENT_SECRET"
```

Se preferir, baixe o JSON da credencial e use `--client-secrets-file client_secret.json`. Numa máquina sem navegador, acrescente `--no-browser` e cole a URL num navegador qualquer. A porta do retorno é 8080 e muda com `--port`.

O script abre o consentimento do Google. Entre com a conta que administra a MCC, autorize, e o refresh token aparece no terminal já no formato da variável de ambiente. Ele não expira enquanto não for revogado, então trate como senha.

Se o Google não devolver refresh token, é porque aquela conta já autorizou este cliente antes. Revogue em [myaccount.google.com/permissions](https://myaccount.google.com/permissions) e rode de novo.

## Instalação

```bash
export GOOGLE_ADS_DEVELOPER_TOKEN=...
export GOOGLE_ADS_CLIENT_ID=...
export GOOGLE_ADS_CLIENT_SECRET=...
export GOOGLE_ADS_REFRESH_TOKEN=...
export GOOGLE_ADS_LOGIN_CUSTOMER_ID=3845391611
export GOOGLE_ADS_MCP_ALLOW_WRITES=1   # opcional, libera escrita

bash scripts/install.sh
```

O script cria o venv, instala o pacote e registra o servidor em `~/.claude.json` no escopo user, preservando os MCPs já configurados. Depois reabra o Claude Code e confira `/mcp`, que deve mostrar `google-ads ✓ connected`.

## Registro manual

```json
{
  "mcpServers": {
    "google-ads": {
      "type": "stdio",
      "command": "<caminho-absoluto>/.venv/bin/google-ads-mcp",
      "args": [],
      "env": {
        "GOOGLE_ADS_DEVELOPER_TOKEN": "...",
        "GOOGLE_ADS_CLIENT_ID": "...",
        "GOOGLE_ADS_CLIENT_SECRET": "...",
        "GOOGLE_ADS_REFRESH_TOKEN": "...",
        "GOOGLE_ADS_LOGIN_CUSTOMER_ID": "3845391611"
      }
    }
  }
}
```

## Requisito de rede

As chamadas batem em `googleads.googleapis.com` e `oauth2.googleapis.com`. Em ambiente com allowlist de rede, libere os dois domínios, senão o servidor sobe mas toda chamada falha no proxy.

## Versão da API

O padrão é `v26`. Em 28/09/2026, sondando o host da API, as versões vivas eram **v22 a v26**; da v21 para trás o endpoint já responde 404. O Google descontinua versões a cada poucos meses, então, quando aparecer erro de endpoint não encontrado, aponte `GOOGLE_ADS_API_VERSION` para a versão vigente e reinicie o servidor. Nada mais muda no código.

Para descobrir a versão atual sem abrir a documentação, uma requisição sem autenticação já diferencia: versão viva responde 401, versão removida responde 404.

```bash
for v in v25 v26 v27 v28; do
  printf "%s -> " "$v"
  curl -s -o /dev/null -w "%{http_code}\n" \
    "https://googleads.googleapis.com/$v/customers:listAccessibleCustomers"
done
```
