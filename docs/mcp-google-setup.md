# Instalar MCPs oficiais do Google (Ads + Analytics) — no computador

Guia para rodar os servidores MCP **oficiais do Google** localmente no PC,
usados com Claude Desktop ou Claude Code. Ambos são gratuitos e mantidos pelo
próprio Google. Rodam via `pipx` (servidor local), então NÃO precisam de
hospedagem.

Repositórios oficiais:
- Google Ads: https://github.com/googleads/google-ads-mcp  (somente leitura)
- Google Analytics: https://github.com/googleanalytics/google-analytics-mcp

---

## 0. Pré-requisitos (uma vez só)

1. **Python 3.10+** instalado.
2. **pipx**:
   ```bash
   python3 -m pip install --user pipx
   python3 -m pipx ensurepath
   ```
3. **gcloud CLI** (para autenticação ADC): instale o Google Cloud SDK.
4. **Um projeto no Google Cloud** (pode ser o mesmo para os dois MCPs).
   Anote o `PROJECT_ID`.

---

## 1. Google Analytics MCP (mais fácil — comece por aqui)

### 1.1 No Google Cloud Console
- Selecione (ou crie) seu projeto.
- Ative as APIs:
  - **Google Analytics Admin API**
  - **Google Analytics Data API**

### 1.2 Autenticação (ADC)
Faça login com uma conta que tenha acesso ao seu Google Analytics:
```bash
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/cloud-platform
```
Isso gera um arquivo de credenciais ADC (o caminho aparece no terminal).

### 1.3 Configuração no cliente Claude
Adicione ao seu config MCP (ver seção 3):
```json
"analytics-mcp": {
  "command": "pipx",
  "args": ["run", "analytics-mcp"],
  "env": {
    "GOOGLE_PROJECT_ID": "SEU_PROJECT_ID"
  }
}
```

---

## 2. Google Ads MCP (precisa de developer token)

> ⚠️ O passo mais demorado é o **developer token** — ele sai de uma conta
> **administradora (MCC/manager)** do Google Ads e pode exigir aprovação do
> Google ("Explorer access" já basta para consultar contas de produção).

### 2.1 Developer token
- Entre na sua conta **MCC** do Google Ads.
- **Ferramentas → Configuração → Central de API** → copie o developer token.
- Garanta pelo menos **Explorer access**.

### 2.2 No Google Cloud Console
- Ative a **Google Ads API** no seu projeto.
- Crie credenciais **OAuth 2.0 Client** (tipo "Desktop") OU use ADC:
  ```bash
  gcloud auth application-default login \
    --scopes=https://www.googleapis.com/auth/adwords,https://www.googleapis.com/auth/cloud-platform
  ```

### 2.3 Configuração no cliente Claude
```json
"google-ads-mcp": {
  "command": "pipx",
  "args": ["run", "--spec", "git+https://github.com/googleads/google-ads-mcp.git", "google-ads-mcp"],
  "env": {
    "GOOGLE_PROJECT_ID": "SEU_PROJECT_ID",
    "GOOGLE_ADS_DEVELOPER_TOKEN": "SEU_DEVELOPER_TOKEN",
    "GOOGLE_ADS_LOGIN_CUSTOMER_ID": "ID_DA_MCC_SEM_TRACOS"
  }
}
```
> `GOOGLE_ADS_LOGIN_CUSTOMER_ID` só é necessário se você acessa via conta MCC.

---

## 3. Onde colar a configuração

### Claude Code (CLI) — jeito mais fácil
Use o comando (roda no terminal do PC), um para cada servidor:
```bash
claude mcp add analytics-mcp -- pipx run analytics-mcp
claude mcp add google-ads-mcp -- pipx run --spec git+https://github.com/googleads/google-ads-mcp.git google-ads-mcp
```
Depois edite as variáveis de ambiente com `claude mcp edit` (ou no
`~/.claude.json`) para incluir o `GOOGLE_PROJECT_ID` etc.

### Claude Desktop
Edite `claude_desktop_config.json`:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Estrutura:
```json
{
  "mcpServers": {
    "analytics-mcp": { ... },
    "google-ads-mcp": { ... }
  }
}
```
Reinicie o Claude Desktop depois de salvar.

---

## 4. Testar
- Analytics: peça "liste minhas propriedades do Google Analytics".
- Ads: peça "liste as contas de anúncio acessíveis" (`list_accessible_customers`).

Se der erro de credencial, quase sempre é: API não ativada, ADC sem o escopo
certo, ou developer token sem Explorer access.

---

## Observações
- O Google Ads MCP oficial é **somente leitura** (análise/relatórios; não cria
  nem edita campanhas).
- Para uso no **celular/web**, esses servidores locais NÃO funcionam direto —
  seria preciso hospedar no Google Cloud Run e adicionar como conector remoto.
  Este guia cobre o uso no **computador**.
