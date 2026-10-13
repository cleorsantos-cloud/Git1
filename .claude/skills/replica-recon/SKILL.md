---
name: replica-recon
description: >-
  Faz a engenharia reversa de qualquer app em um mapa de reconhecimento:
  inventário de telas, fluxos de usuário, lista de componentes, modelo de dados
  inferido e matriz de features, a partir de páginas públicas, screenshots,
  listagens de loja de apps, documentação de ajuda e a conta do próprio usuário.
  É o primeiro passo do pacote Replica. Use quando o usuário disser "clona esse
  app", "faz engenharia reversa do X", "como funciona o X", "mapeia o X", "quais
  telas o X tem", "quero fazer minha versão do X", "copia esse app", ou colar a
  URL ou o link da App Store de um app querendo reconstruí-lo. Triggers: "clone
  this app", "reverse engineer X", "how does X work", "map out X", "what screens
  does X have", "I want to build my own version of X", "copy this app".
---

# replica-recon

## Contrato de execução

PASSOS: escopo → fontes → telas → fluxos → componentes → modelo de dados → matriz de features → o que não dá pra clonar → tamanho
BLOQUEIA: nenhum. Todo passo pode ser pulado ou reordenado conforme o projeto.
PODE PULAR: qualquer passo, desde que apareça como ⏭️ no recibo com o motivo.
RECIBO: RECIBO: replica-recon | ✅<passo> · ⏭️<passo>(motivo) | telas mapeadas · fluxos · features na matriz

Checklist: antes de começar, crie um todo por passo acima; marque cada um ao terminar ou ao pular.

Todo o resto do pacote se constrói sobre o que esta skill escreve. Um mapa de
reconhecimento ruim dá um clone ruim, então dedique o tempo necessário aqui.

A saída vai para o projeto do usuário:

```
replica/recon.md        the recon map (template: recon-map.md in this folder)
replica/features.csv    the feature matrix (template: features.csv in this folder)
replica/screens/        reference screenshots of the original. Never shipped.
```

## As regras, antes de tudo

Esta skill reconstrói **funcionalidade e padrões de UX**, no estilo clean-room.
Ela estuda o que o app faz e como o usuário se move por ele. Não leva nada que
pertença ao app.

- **Só fontes públicas e a conta do próprio usuário.** Nunca entre na conta de
  outra pessoa, nunca peça senha, nunca contorne um paywall ou um login por
  qualquer truque.
- **Ler, não raspar.** Nada de crawlers, downloads em massa ou loops. Se uma
  ferramenta de navegador estiver conectada ao navegador do próprio usuário,
  leia as páginas em velocidade humana, com o usuário presente.
- **Nada de código-fonte, nada de APIs privadas.** Não leia nem salve os
  bundles de JavaScript do app, não descompile o binário, não registre as
  chamadas de rede para copiar endpoints. Ler a documentação pública de API
  pode.
- **Confira os termos de uso.** Os termos de alguns produtos proíbem usar uma
  conta para construir um produto concorrente. Se a conta do usuário estiver
  sob termos assim, avise e trabalhe só com fontes públicas.
- **Screenshots são referência.** Ficam em `replica/screens/`, servem para
  comparar layouts e nunca entram no clone.

## Passo 1: escopo

Pergunte três coisas, ou proponha as respostas e peça um sim:

1. **Qual app, qual plataforma.** Web, iOS, Android, desktop.
2. **Qual fatia.** "Todo o Notion" não é um projeto. "As páginas, os blocos e o
   compartilhamento do Notion" é. O padrão é o loop central: o fluxo pelo qual
   os usuários pagam.
3. **Para quem é.** O negócio do próprio usuário, um nicho, um produto para
   vender.

## Passo 2: liste as fontes

Monte primeiro uma tabela de fontes, com uma URL em cada linha. Em ordem de
valor:

| fonte | o que entrega |
| --- | --- |
| central de ajuda / docs | a lista de features mais completa que existe, e as configurações |
| página de preços | quais features importam (são as que eles travam por plano) |
| changelog | o que foi adicionado recentemente, o que o time considera importante |
| listagem da loja de apps | screenshots de cada tela-chave, o pitch, as avaliações |
| vídeos públicos de demonstração | fluxos reais, clique a clique |
| site de marketing | posicionamento, o loop central nas palavras deles |
| a conta do próprio usuário | o produto real, em todos os estados, conduzido pelo usuário |
| docs públicas da API | o modelo de dados, quase de graça |

## Passo 3: inventário de telas

Uma linha por tela. Os IDs são estáveis: S01, S02... Todos os outros arquivos
se referem a eles.

`ID | tela | rota ou como chegar | finalidade | componentes-chave | estados vistos`

Os estados importam: vazio, carregando, preenchido, erro, sem permissão,
mobile. Um estado vazio que você não registrou é um estado vazio que você não
vai construir.

## Passo 4: fluxos de usuário

F01, F02... Cada um é um objetivo e as telas por onde ele passa:

```
F01 Guest books a meeting
    S07 booking page -> S08 pick a time -> S09 details form -> S10 confirmed
    edge: no slots this week, time zone differs, slot taken while filling the form
```

Conte os cliques do caminho feliz. Esse número vira a marca a superar.

## Passo 5: componentes

Toda parte repetida da interface: botões, campos, seletores de data, modais,
tabelas, toasts, navegação. Nome, variantes, estados, quais telas usam. Isso
vira a lista de componentes do replica-design.

## Passo 6: modelo de dados inferido

Entidades, campos e relacionamentos, cada um com sua evidência e um nível de
confiança:

```
Booking  id, event_type_id, start_at, end_at, guest_name, guest_email,
         status (confirmed | cancelled | rescheduled), answers (json)
         evidence: S09 form fields, S10 confirmation, help article "Cancel a booking"
         confidence: high
```

Marque palpite como palpite. O replica-architect transforma isso em um schema
de verdade.

## Passo 7: matriz de features

Escreva `replica/features.csv` (colunas: feature, area, priority, original,
clone, notes). A prioridade é must / should / could (deve / deveria / poderia).
`clone` começa em `no` em todas as linhas e é preenchido durante a construção.
O replica-diff dá a nota.

## Passo 8: o que não dá pra clonar

Liste com honestidade, como linhas `skip` com o motivo: conteúdo licenciado (um
catálogo de música, um banco de imagens), a rede e seus usuários, dados que o
app possui, acordos com parceiros, hardware, licenças regulatórias (bancos,
saúde). "Clonar qualquer app" significa as features e o fluxo, não o que o app
possui.

## Passo 9: dimensione

Telas, fluxos, entidades e as partes difíceis (tempo real, sincronização,
pagamentos, integrações de calendário ou e-mail, offline). Dê um tamanho: S (um
fim de semana), M (algumas semanas), L (um trimestre), XL (redefina o escopo).
Sem prometer um clone perfeito.

## Saída

`replica/recon.md` e `replica/features.csv`, depois um resumo de cinco linhas:
o loop central, a contagem de telas e fluxos, as três partes mais difíceis, o
que está fora do escopo e o próximo passo: `/replica-architect`.
