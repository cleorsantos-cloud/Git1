---
name: replica-backend
description: >-
  Constrói o backend de um clone de app: auth, migrations do banco e regras de
  acesso, pagamentos com Stripe, e-mail, jobs em background e integrações com
  terceiros apenas por APIs oficiais, mais um checklist de segurança. Use
  quando o usuário disser "coloca login", "configura o auth", "liga o banco de
  dados", "coloca pagamento", "conecta o Stripe", "integra o Google Calendar",
  "manda e-mails", "backend do meu clone", ou quando o /replica-build estiver
  rodando com dados falsos. Gatilhos em inglês: "add login", "set up auth",
  "wire up the database", "add payments", "connect Stripe", "add Google
  Calendar", "send emails", "backend for my clone".
---

# replica-backend

## Contrato de execução

PASSOS: auth → banco → pagamentos → e-mail e jobs → integrações → checklist de segurança
BLOQUEIA: nenhum. Todo passo pode ser pulado ou reordenado conforme o projeto.
PODE PULAR: qualquer passo, desde que apareça como ⏭️ no recibo com o motivo.
RECIBO: RECIBO: replica-backend | ✅<passo> · ⏭️<passo>(motivo) | itens do checklist de segurança ✅/total

Checklist: antes de começar, crie um todo por passo acima; marque cada um ao terminar ou ao pular.

Lê `replica/architecture.md`. Escreve migrations e código de servidor, e
mantém `replica/backend.md` (checklist abaixo) em dia.

## As regras

- **Só APIs oficiais e públicas, com as chaves do próprio usuário.** Nunca
  chame os endpoints privados do app original, nunca reuse o cliente OAuth
  dele, nunca faça proxy por ele.
- **O usuário cria as contas e as chaves.** O Claude nunca se cadastra em
  serviços, nunca digita senha, cartão ou chave live. O usuário cria o projeto
  no Stripe, Supabase, Resend ou Google Cloud e coloca as chaves em
  `.env.local`. O Claude escreve o `.env.example` com todos os nomes de
  variável e nenhum valor.
- **Modo de teste primeiro.** Chaves e cartões de teste do Stripe até o
  replica-deploy.

## Auth

- Cadastro por e-mail com verificação, redefinição de senha, magic link se o
  original tiver. OAuth (Google, Apple) com os apps de desenvolvedor do
  próprio usuário.
- Sessões: cookies http-only e secure. Sair de todos os dispositivos.
- Papéis e times se o mapa do recon tiver: owner, admin, member, com uma única
  função que responde "esse usuário pode fazer isso com esse registro".
- Exclusão de conta que realmente exclui. A Apple exige isso para apps com
  cadastro.

## Banco de dados

- Migrations a partir do `architecture.md`, versionadas e executadas por um
  script.
- Regras de acesso em toda tabela: políticas de row level security no
  Supabase, ou a função de autorização chamada em toda query. Teste: um
  segundo usuário não pode receber nada de volta.
- Script de seed com dados falsos realistas (sem pessoas reais).
- Backups ligados (os backups diários do host contam, confira se estão
  habilitados).

## Pagamentos

- Stripe Checkout para assinar um plano, o Customer Portal para mudanças e
  cancelamento. Não construa formulários de cartão.
- Webhooks: verifique a assinatura, guarde o id do evento, torne todo handler
  idempotente (o Stripe reenvia). Trate `checkout.session.completed`,
  `customer.subscription.updated`, `customer.subscription.deleted`,
  `invoice.payment_failed`.
- O status da assinatura vive no seu banco, atualizado por webhooks e lido
  pelo seu app. Nunca confie no client.
- Cancelar é um clique. Cobrança difícil de cancelar é uma das maiores
  reclamações da maioria dos apps e, em muitos lugares, é ilegal.

## E-mail e jobs

- E-mail transacional por Resend ou Postmark, a partir do seu próprio domínio.
  Templates escritos do zero.
- Jobs para tudo que depende de tempo (lembretes, digests, sync, limpeza), com
  retries e um log de dead-letter. Horários em UTC, exibidos no fuso do
  usuário.

## Integrações

Para cada integração da matriz de features: a API oficial, os escopos OAuth
necessários (o mínimo possível), o processo de revisão do provedor, os limites
de taxa. Escopos do Google como o Calendar precisam da verificação OAuth do
Google antes do lançamento público, o que leva semanas. Comece cedo e
registre isso no `backend.md`.

## Checklist de segurança

- [ ] segredos só em variáveis de ambiente, `.env*` no `.gitignore`, nada nos bundles do client
- [ ] entrada validada no servidor (zod ou similar) em toda rota
- [ ] autorização checada em toda leitura e escrita, testada com um segundo usuário
- [ ] rate limit em auth, cadastro e em tudo que envia e-mail ou SMS
- [ ] webhooks verificam assinaturas
- [ ] uploads: limites de tamanho e tipo, servidos de um domínio ou bucket separado
- [ ] nenhum dado de usuário em URLs ou logs
- [ ] dependências auditadas (`npm audit`)
- [ ] política de privacidade lista todo processador (Stripe, Resend, host, analytics)

## Saída

Auth, banco, pagamentos em modo de teste, e-mail e integrações funcionando,
`.env.example`, `replica/backend.md` com o checklist marcado, linhas da matriz
de features atualizadas. Próximo: `/replica-test`.
