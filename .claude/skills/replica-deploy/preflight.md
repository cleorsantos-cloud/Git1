# Checklist de deploy: {{your app}}

Data: {{YYYY-MM-DD}}  Commit: {{sha}}  Ok do usuário: {{sim / ainda não}}

## Checagem pré-voo (preflight) — tudo precisa passar

- [ ] suíte e2e verde: {{n passaram / n}}
- [ ] nenhum bug S1 ou S2 aberto
- [ ] paridade: todos os must-haves prontos ({{n/n}}), nota de funcionalidades {{n}}
- [ ] varredura de rebrand limpa (`sweep.py` com exit 0)
- [ ] listing da loja passa (`listing.py` com exit 0), se for publicar nas lojas
- [ ] build de produção passa
- [ ] política de privacidade e termos no ar, com todos os processadores listados
- [ ] exclusão de conta funciona
- [ ] favicon, títulos, imagem OG, e-mails e ícone do app são seus

## Produção

- [ ] banco de produção separado, backups ligados, migrações no deploy
- [ ] variáveis de ambiente configuradas (nomes batem com o .env.example)
- [ ] Stripe live: produtos, preços, endpoint de webhook + segredo, uma compra real reembolsada
- [ ] redirect URIs e origens do OAuth incluem o domínio de produção
- [ ] verificação do Google OAuth aprovada (se usar escopos sensíveis)
- [ ] domínio de envio de e-mail verificado

## Domínio

- [ ] A @ -> {{value}}
- [ ] CNAME www -> {{value}}
- [ ] SPF, DKIM, DMARC configurados
- [ ] host canônico escolhido, o outro redireciona
- [ ] HTTPS válido

## Acompanhamento

- [ ] rastreamento de erros
- [ ] checagens de uptime
- [ ] analytics
- [ ] fluxo central feito no site no ar, no desktop e no celular
