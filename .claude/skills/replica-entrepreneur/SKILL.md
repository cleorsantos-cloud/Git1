---
name: replica-entrepreneur
description: >-
  Pesquisa o app que está sendo clonado e lê o que seus usuários reais dizem
  em avaliações públicas (App Store, Google Play, G2, Capterra, Trustpilot,
  Reddit, Hacker News, o próprio quadro de pedidos de feature), depois
  ranqueia o que eles odeiam, o que falta e o que ninguém resolveu, e
  transforma isso em um plano de correções para o clone e em um ângulo de
  posicionamento vendável. Toda citação é real, literal e com link. Use quando
  o usuário disser "do que o pessoal reclama do X", "lê as avaliações", "como
  faço o meu ficar melhor", "acha a brecha", "que funcionalidades faltam",
  "como eu posiciono isso", "faz isso vender", ou depois do /replica-diff.
  Gatilhos em inglês: "what do people hate about X", "read the reviews", "how
  do I make mine better", "find the gap", "what features are missing", "how do
  I position this", "make it sellable".
---

# replica-entrepreneur

## Contrato de execução

PASSOS: coletar avaliações → ranquear → três listas → plano de correção → ângulo
BLOQUEIA: nenhum. Todo passo pode ser pulado ou reordenado conforme o projeto.
PODE PULAR: qualquer passo, desde que apareça como ⏭️ no recibo com o motivo.
RECIBO: RECIBO: replica-entrepreneur | ✅<passo> · ⏭️<passo>(motivo) | avaliações lidas · fontes · dores ranqueadas

Checklist: antes de começar, crie um todo por passo acima; marque cada um ao terminar ou ao pular.

Uma cópia pura de um app não tem razão de existir. Esta skill encontra a
razão: o que os usuários do original odeiam, nas palavras deles, e corrige
isso no seu.

Ferramenta nesta pasta:

```bash
python3 reviews.py replica/reviews.csv --out replica/feedback.md
```

## As regras, que não são negociáveis

- **Nunca fabrique.** Nada de avaliações, citações, notas, contagens,
  usuários ou fontes inventados. Se uma fonte não puder ser acessada, diga e
  siga em frente. Se são 14 avaliações, diga 14.
- **Toda citação é literal e com link.** Copiada exatamente da página, com a
  URL da avaliação ou da thread. O `reviews.py` descarta qualquer linha sem
  link.
- **Ler, não raspar.** Leia as páginas de avaliações como uma pessoa lê, no
  navegador, e copie as linhas para a planilha. Nada de bibliotecas de
  scraping contra lojas ou sites de avaliação cujos termos proíbem isso. Feeds
  públicos oficiais e APIs são aceitáveis dentro dos seus termos: o feed RSS
  de avaliações de clientes da Apple
  (`https://itunes.apple.com/us/rss/customerreviews/id=<APP_ID>/sortBy=mostRecent/json`),
  a API Algolia do Hacker News (`hn.algolia.com/api/v1/search?query=...`), a
  API oficial do Reddit sob os termos dela.
- **Nunca avaliações falsas.** Nem para o seu app, nem contra o deles. É
  ilegal nos EUA (regra da FTC de 2024) e em muitos outros lugares.
- **Quem avalia não é seu depoimento.** As palavras deles são pesquisa. Não
  coloque na sua landing page.

## Passo 1: coletar

Mire em 100+ avaliações em pelo menos três fontes, das mais recentes para as
mais antigas:

| fonte | onde |
| --- | --- |
| App Store | a página do app, Ratings and Reviews, See All; ou o feed RSS acima |
| Google Play | a listagem, See all reviews, ordenar por mais recentes |
| G2, Capterra, Trustpilot | as páginas de avaliação do produto, filtre também por 1 a 3 estrelas |
| Reddit | busque "X alternative", "switched from X", "X sucks", "X vs" |
| Hacker News | a API Algolia ou a busca do site, mesmas consultas |
| o quadro do próprio original | o roadmap público ou quadro de pedidos de feature (Canny e similares) e a contagem de votos |
| o changelog dele | o que ele lançou, para você não "corrigir" o que já foi corrigido |

Cada linha em `replica/reviews.csv`: `source,url,date,rating,text`, com o texto
copiado exatamente. Leia também as avaliações de 3 e 4 estrelas. "Love it,
but..." é onde as melhores correções se escondem.

## Passo 2: ranquear

```bash
python3 reviews.py replica/reviews.csv --out replica/feedback.md
```

Ele separa as avaliações em temas (`themes.json`, edite para a categoria do
app), dá mais peso a notas baixas e a avaliações recentes, marca como thin os
temas com menos de 3 avaliações ou de uma fonte só, lista cada pedido nas
palavras dos próprios usuários e destaca as notas baixas que não casaram com
nenhum tema. Leia essa última lista à mão. Muitas vezes é a melhor parte.

## Passo 3: três listas

A partir do `feedback.md`, escreva três listas ranqueadas. Cada item: o
problema em uma linha, quantas avaliações, quantas fontes, uma ou duas
citações com link.

1. **O que eles odeiam.** Reclamações sobre coisas que o app faz.
2. **O que falta.** Funcionalidades que as pessoas pedem pelo nome.
3. **O que ninguém resolveu.** Trabalhos inteiros ou grupos que o app ignora
   ("not built for teams", "useless for therapists"). Isso vira
   posicionamento.

Temas thin entram na lista como thin. Não apresente três comentários irritados
no Reddit como tendência.

## Passo 4: o plano de correção

Escolha de 5 a 8 itens por evidência vezes o quão barato é corrigir. Para
cada um: o que construir ou mudar, tamanho (S, M, L), qual skill faz e a
evidência. Adicione cada um ao `replica/features.csv` como uma linha com
`original` igual a `no`. Reclamações de preço e cobrança vão para o
`/replica-launch`.

## Passo 5: o ângulo

Três opções de posicionamento, cada uma ancorada em um tema principal:

```
For {{who}} who {{hate this about the original, in plain words}},
{{your app}} {{does this instead}}.
Evidence: {{theme}}, {{n}} reviews across {{n}} sources.
```

Recomende uma. Ela orienta o nome e a voz do replica-brand e o hero do
replica-launch. Não coloque o nome do original no nome do seu app, nos
anúncios nem na listagem da loja. Uma página de comparação factual é questão
jurídica para um advogado do seu país.

## Saída

`replica/reviews.csv`, `replica/feedback.md`, `replica/fixes.md` (três
listas, plano de correção, ângulo), novas linhas no `features.csv` e um
resumo que informa o tamanho da amostra. Próximo: `/replica-brand`.
