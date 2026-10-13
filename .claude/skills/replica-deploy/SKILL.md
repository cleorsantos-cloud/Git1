---
name: replica-deploy
description: >-
  Coloca no ar um clone de app no domínio do próprio usuário: portão de
  checagem pré-voo (preflight) com testes verdes, itens essenciais de paridade
  prontos, varredura de rebrand limpa, listing validado e páginas legais no ar;
  depois banco e variáveis de produção, host, registros DNS do domínio e do
  e-mail, Stripe em modo live, redirects de OAuth, monitoramento e builds
  mobile para TestFlight e Play. Use quando o usuário disser "coloca no ar",
  "faz o deploy", "publica o app", "conecta meu domínio", "vai pra produção",
  "sobe pra produção", ou depois de /replica-launch. Triggers in English:
  "deploy it", "ship it", "put it live", "connect my domain", "go to
  production", "publish the app".
---

# replica-deploy

## Contrato de execução

PASSOS: preflight → serviços de produção → host e domínio → monitoramento → mobile (se houver app)
BLOQUEIA: nenhum. Todo passo pode ser pulado ou reordenado conforme o projeto.
PODE PULAR: qualquer passo, desde que apareça como ⏭️ no recibo com o motivo.
RECIBO: RECIBO: replica-deploy | ✅<passo> · ⏭️<passo>(motivo) | itens do preflight ✅/total · URL no ar

Checklist: antes de começar, crie um todo por passo acima; marque cada um ao terminar ou ao pular.

Lê tudo em `replica/`. Grava `replica/deploy.md` (o checklist do
`preflight.md` desta pasta, preenchido).

## As regras

- **Nada vai ao ar sem o ok do usuário.** Mostre os resultados do preflight e
  pergunte.
- **O usuário compra e faz login.** O Claude nunca compra domínio, digita
  cartão, digita senha nem cola chave live. O Claude escreve os registros DNS,
  os nomes das variáveis de ambiente e os comandos exatos; o usuário faz os
  passos nas contas.
- **Só depois do rebrand.** A varredura (sweep) tem que estar limpa. Sem
  exceções.

## Passo 1: preflight

Rode todas as checagens e cole os resultados no `deploy.md`:

```bash
npx playwright test                                                  # replica-test
python3 ../replica-diff/parity.py replica/features.csv               # must-haves done
python3 ../replica-brand/sweep.py . --config replica/brand.json      # exit 0: clean
python3 ../replica-launch/listing.py replica/launch/listing.json     # if shipping to stores
npm run build                                                        # production build passes
```

(Os caminhos são relativos ao lugar onde o pack foi instalado. Em
`~/.claude/skills/` ficam `~/.claude/skills/replica-diff/parity.py` e assim
por diante.)

Mais, à mão: nenhum bug S1 ou S2 aberto, páginas de política de privacidade e
termos no ar (listando todos os processadores), banner de cookies se você usa
cookies não essenciais na UE ou no Reino Unido, exclusão de conta funcionando,
favicon, títulos e imagem OG são seus.

Qualquer falha trava o deploy. Diga qual e por quê.

## Passo 2: serviços de produção

- Um **projeto de produção separado** para o banco de dados (nunca o de
  desenvolvimento), backups ligados, migrações rodadas pelo deploy, não à mão.
- Variáveis de ambiente configuradas no host para produção, batendo com o
  `.env.example`. Chaves live só aqui.
- **Stripe**: passe para o modo live, recrie produtos e preços, adicione o
  endpoint de webhook de produção e o segredo de assinatura dele, faça uma
  compra real de teste e reembolse.
- **OAuth**: adicione o domínio de produção aos redirect URIs e às origens
  autorizadas de cada provedor. Escopos do Google que exigem verificação
  precisam estar aprovados, senão só usuários de teste conseguem entrar.
- **E-mail**: o domínio de envio verificado no provedor.

## Passo 3: host e domínio

Padrão: Vercel para Next.js (Netlify, Cloudflare Pages, Fly ou Render nos
outros casos). Conecte o repositório para que a `main` faça deploy e os pull
requests ganhem URLs de preview.

O domínio, depois que o usuário o comprar em qualquer registrador:

| registro | nome | valor |
| --- | --- | --- |
| A | @ | o IP do apex do host (Vercel: aparece nas configurações do domínio) |
| CNAME | www | o destino do host (Vercel: `cname.vercel-dns.com`) |
| TXT | @ ou um subdomínio | o valor de verificação do host, se pedido |

DNS de e-mail vindo do provedor de e-mail: SPF (TXT), DKIM (CNAME ou TXT) e um
registro DMARC começando em `v=DMARC1; p=none; rua=mailto:you@yourdomain` e
depois apertado para `quarantine` quando os relatórios estiverem limpos. Sem
isso, seus e-mails de confirmação caem no spam.

Escolha um host canônico (apex ou www) e redirecione o outro. O HTTPS é
automático nos hosts acima; confira.

## Passo 4: monitoramento

Rastreamento de erros (Sentry ou o do host), checagens de uptime na home e na
API do fluxo central, logs guardados, analytics (um que respeite a
privacidade dispensa o banner de cookies) e um alerta para o e-mail ou o
celular do usuário. Depois faça você mesmo o fluxo central no site no ar e
peça ao usuário que faça no celular dele.

## Passo 5: mobile, se houver app

Expo: `eas build` e depois `eas submit` para o TestFlight e para o teste
interno do Play. Nativo: archive no Xcode e upload para o App Store Connect;
bundle do Gradle para o Play Console. O usuário é dono das contas de
desenvolvedor (US$ 99 por ano na Apple, US$ 25 uma única vez no Google). Beta
primeiro, depois a revisão com o listing do replica-launch.

## Saída

`replica/deploy.md` com cada checagem e seu resultado, a URL no ar, os
registros DNS configurados e o que acompanhar na primeira semana. O clone agora
é um app com o seu nome.
