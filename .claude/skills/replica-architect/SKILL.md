---
name: replica-architect
description: >-
  Planeja a stack, o schema do banco e a API de um clone de app, a partir do
  mapa de reconhecimento que o replica-recon escreveu. Escolhe tecnologia
  simples e gerenciada, transforma o modelo de dados inferido em SQL de verdade
  com índices e regras de acesso, lista cada rota por fluxo e ordena a
  construção começando por uma fatia vertical fina. Use quando o usuário disser
  "planeja o clone", "qual stack eu uso", "desenha o banco de dados", "escreve o
  schema", "planeja a API", "arquitetura da minha versão do X", ou depois que o
  /replica-recon terminar. Triggers: "plan the clone", "what stack should I
  use", "design the database", "write the schema", "plan the API", "architecture
  for my version of X".
---

# replica-architect

## Contrato de execução

PASSOS: stack → schema → API → pontos críticos → ordem de construção
BLOQUEIA: nenhum. Todo passo pode ser pulado ou reordenado conforme o projeto.
PODE PULAR: qualquer passo, desde que apareça como ⏭️ no recibo com o motivo.
RECIBO: RECIBO: replica-architect | ✅<passo> · ⏭️<passo>(motivo) | tabelas no schema · rotas na API

Checklist: antes de começar, crie um todo por passo acima; marque cada um ao terminar ou ao pular.

Lê `replica/recon.md` e `replica/features.csv`. Escreve
`replica/architecture.md` (template: architecture.md nesta pasta).

Se não houver mapa de reconhecimento, pare e rode `/replica-recon` primeiro.
Planejar um clone de memória, do que você acha que o app faz, é o jeito de
perder metade dele.

## Passo 1: a stack

Use o que o usuário já conhece, se ele tiver uma stack. Do contrário, o padrão,
porque cada peça é gerenciada, documentada e barata com zero usuários:

| camada | padrão | alternativas |
| --- | --- | --- |
| app web | Next.js (App Router) + TypeScript | Remix, SvelteKit, Rails |
| estilos | Tailwind, tokens do replica-design | CSS modules |
| mobile | Expo (React Native) | SwiftUI, Kotlin |
| banco de dados | Postgres no Supabase ou Neon | PlanetScale, SQLite (Turso) |
| ORM | Drizzle ou Prisma | SQL puro |
| auth | Supabase Auth ou Auth.js | Clerk |
| pagamentos | Stripe Checkout + Billing | Lemon Squeezy, Paddle |
| e-mail | Resend ou Postmark | SES |
| jobs | Vercel Cron, Inngest ou Trigger.dev | um worker no Fly |
| arquivos | Supabase Storage ou Cloudflare R2 | S3 |
| hospedagem | Vercel | Netlify, Fly, Render |

Escreva cada escolha com uma linha de por quê. Um banco de dados. Nada de
microsserviços. O clone não precisa da arquitetura do original, precisa das
features do original.

## Passo 2: o schema

Transforme o modelo de dados inferido em SQL. Para toda tabela:

- `id uuid primary key default gen_random_uuid()`, `created_at`, `updated_at`
- uma coluna de dono (`user_id` ou `org_id`) em tudo que pertence a um usuário
- chaves estrangeiras com uma regra de `on delete` decidida, não a padrão
- índices em toda chave estrangeira e em toda coluna que você filtra ou ordena
- enums ou check constraints para campos de status
- horários como `timestamptz`, sempre, guardados em UTC
- dinheiro como inteiro em centavos mais uma coluna de moeda
- regras de acesso: row level security do Postgres no Supabase, ou uma checagem
  de autorização por consulta na camada de dados. Escreva qual das duas.

Exemplo, para um app de agendamento:

```sql
create table bookings (
  id uuid primary key default gen_random_uuid(),
  event_type_id uuid not null references event_types(id) on delete cascade,
  host_id uuid not null references users(id) on delete cascade,
  start_at timestamptz not null,
  end_at timestamptz not null,
  guest_name text not null,
  guest_email text not null,
  guest_timezone text not null,
  status text not null default 'confirmed'
    check (status in ('confirmed','cancelled','rescheduled')),
  answers jsonb not null default '{}',
  created_at timestamptz not null default now(),
  constraint no_zero_length check (end_at > start_at)
);
create index on bookings (host_id, start_at);
```

Depois, as restrições duras que o reconhecimento encontrou. Dois convidados
reservando o mesmo horário é um problema de banco de dados (uma exclusion
constraint ou um índice único), não um problema de interface.

## Passo 3: a API

Uma tabela por fluxo do mapa de reconhecimento. Para cada rota ou server action:

`método caminho | o que faz | quem pode chamar | entrada | saída | fluxo`

Mais os webhooks de entrada (Stripe, provedores de calendário) e de saída, e os
jobs em segundo plano (lembretes, sincronização, limpeza) com a agenda de cada
um.

Só APIs oficiais e públicas, com as chaves do próprio usuário. Nunca os
endpoints privados do app original, mesmo que estejam visíveis no navegador.

## Passo 4: as partes que mordem

Escreva uma linha sobre cada uma que se aplicar: fusos horários e horário de
verão, idempotência (webhooks chegam duas vezes), condições de corrida, limites
de requisições, limites de tamanho de arquivo, busca, tempo real, offline,
entregabilidade de e-mail, multi-tenancy, exclusão de dados conforme a LGPD/GDPR.

## Passo 5: ordem de construção

1. **Fatia vertical.** O loop central de ponta a ponta, feio: cadastro, fazer a
   única coisa, ver o resultado. Prova a stack.
2. **Must-haves** (obrigatórias) do `features.csv`, por área.
3. **Should-haves** (desejáveis), depois could-haves (opcionais).
4. **As correções** que o replica-entrepreneur encontrar, depois de rodar.

Cada marco lista suas telas (IDs S), tabelas e rotas.

## Saída

`replica/architecture.md`, o SQL em `replica/schema.sql` ou como a primeira
migration, e um resumo: a stack em uma linha, o número de tabelas, o número de
rotas, as três partes mais arriscadas e o próximo passo: `/replica-design`.
