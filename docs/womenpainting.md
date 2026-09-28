# WomenPainting — estado do atendimento

Atualizado em 28/09/2026. Cliente da Agência Bona Vita.

## Quem é

Women Painting & Decorating, pintura e decoração residencial e comercial na Grande Toronto, mais de 16 anos de mercado, time formado por mulheres. Donas: Deborah Viveiros e Rafaela "Raffie" Valadares.

| Item | Valor |
|---|---|
| Site | womenpainting.com |
| Contatos | womenpainting@hotmail.com, info@womenpainting.com |
| Telefones | (647) 407-1077, (416) 400-3401 |
| Instagram | @womenpainting |
| Google Ads | 386-824-5329, sob a MCC 384-539-1611 |
| Perfil no Google | nota 5,0 com 78 avaliações |
| Fee | 350 por mês, atendimento às segundas |
| Início | setembro de 2023 |

## Diagnóstico

O site virou uma página única. Só `/` e `/thank-you/` respondem. Endereços antigos como `/contact/`, `/services/`, `/interior-painting/`, `/gallery/` e as páginas de cidade devolvem 404. Isso explica de uma vez os 404 do Search Console, as páginas órfãs do Ahrefs e as reprovações de anúncio por destino que não funciona.

Campanha em operação, semana de 19 a 25 de setembro, campanha `[Women] [PESQUISA] [OnGoing]]`:

| Métrica | Valor |
|---|---|
| Custo | 17,42 |
| Cliques | 9 |
| Impressões | 141 |
| CTR | 6,38% |
| CPC médio | 1,94 |
| Conversões | não rastreadas |

Em novembro de 2024 a conta fazia 28.700 impressões e 119 cliques por mês. O alcance despencou.

## Feito

- **robots.txt corrigido em 28/09.** Estava `Disallow: /`, bloqueando todo rastreamento. Agora libera tudo e aponta `https://womenpainting.com/sitemap-index.xml`, endereço confirmado em produção.
- **Conector próprio do Google Ads** criado em `mcp-servers/google-ads-mcp`, com leitura, escrita e CLI para rodar sem servidor MCP.

## Decisões do cliente

- Não ativar campanha nenhuma. Só a `[Women] [PESQUISA] [OnGoing]]` segue rodando, como está.
- Consertar primeiro os anúncios reprovados, depois o e-mail.

## Próximos passos

1. **Ler os anúncios da campanha que está no ar** e conferir se alguma URL final aponta para página morta. Não alterar a campanha.
2. **Campanha `[Women] [PESQUISA] [TESTE]`**, 5 anúncios reprovados: criar os substitutos com status PAUSED e URL final `https://womenpainting.com/`, caminhos `painting` e `toronto`, depois pausar os antigos. A copy aprovada está em `docs/womenpainting-anuncios.md`.
3. **Campanha `[Women][DISPLAY] Campanha Inverno`**, 35 anúncios reprovados: recomendação é remover em vez de refazer, porque a campanha fica pausada e o criativo seria refeito de qualquer forma. Aguardando decisão.
4. **E-mail sem SPF e DKIM.** Mensagens de `info@womenpainting.com` voltam desde julho, com erro 550-5.7.26 do Gmail. A Raffie reportou em 14/07/2026 e não houve resposta. Provável perda de orçamento por e-mail não entregue.
5. **404 do Search Console.** Listar as URLs e redirecionar para a home, ou recriar as páginas.
6. **Sem medição de conversão.** Sem a tag, não dá para justificar verba.

## Pendências de médio prazo

O site de duas páginas não sustenta ranking para as palavras que o relatório mensal acompanhava, como "interior painting". A correção de verdade é recriar páginas por serviço e por cidade, o que resolve 404, anúncio e SEO de uma vez.

## Como ligar a ferramenta

As credenciais ficam em variável de ambiente, nunca no repositório nem no chat. Veja `mcp-servers/google-ads-mcp/README.md`. Para rodar sem servidor MCP:

```bash
cd mcp-servers/google-ads-mcp
uv venv --python 3.12 --allow-existing && uv pip install -e .
.venv/bin/python -m google_ads_mcp.cli list_client_accounts
```
