---
name: replica-launch
description: >-
  Escreve o lançamento de um clone de app: a landing page construída sobre o
  ângulo de posicionamento, o preço definido a partir da tabela pública do
  original e das reclamações dos usuários dele, e o listing da App Store e do
  Google Play validado contra os limites das lojas e as regras anticópia. Use
  quando o usuário disser "faz a landing page", "quanto eu cobro", "qual o
  preço", "texto da App Store", "listing das lojas", "screenshots das lojas",
  "plano de lançamento", "Product Hunt", ou depois de /replica-brand. Triggers
  in English: "landing page", "pricing", "how much should I charge", "App
  Store listing", "store screenshots", "launch plan", "Product Hunt".
---

# replica-launch

## Contrato de execução

PASSOS: landing page → preço → listing das lojas → plano de lançamento
BLOQUEIA: nenhum. Todo passo pode ser pulado ou reordenado conforme o projeto.
PODE PULAR: qualquer passo, desde que apareça como ⏭️ no recibo com o motivo.
RECIBO: RECIBO: replica-launch | ✅<passo> · ⏭️<passo>(motivo) | avisos do lint do listing · faixa de preço definida

Checklist: antes de começar, crie um todo por passo acima; marque cada um ao terminar ou ao pular.

Lê `replica/fixes.md` (o ângulo e as evidências), `replica/brand.md` e
`replica/brand.json`. Grava `replica/launch/`: `landing.md`, `pricing.md`,
`listing.json`, `launch-plan.md`.

```bash
python3 listing.py replica/launch/listing.json      # limits, claims, the original's name
```

Comece a partir do `listing.example.json` desta pasta.

## As regras

- **Nada de prova falsa.** Nada de depoimentos inventados, número de usuários,
  nota de estrelas, logos de imprensa ou faixa "confiado por". Uma seção de
  prova vazia é melhor que uma falsa. Usuários reais do beta, com permissão,
  podem entrar.
- **Nada de citação de avaliador como depoimento.** As avaliações do original
  são pesquisa.
- **O nome do original fica fora** do nome do seu app, do listing da loja, das
  palavras-chave e dos anúncios. Apple e Google reprovam, e isso convida a uma
  notificação de remoção (takedown).

## Passo 1: landing page

`landing.md`, seção por seção, e depois construa no projeto:

1. **Hero**: o ângulo como título (o que você faz, para quem), uma linha
   embaixo, um botão. Screenshot do produto real.
2. **O problema**: os dois principais temas de "ódio", em palavras simples.
   Parafraseie, não cite avaliadores.
3. **Como funciona**: três passos, a partir do fluxo central.
4. **Funcionalidades**: cada uma amarrada a um conserto do `fixes.md`. Comece
   pelos consertos, não pelas funcionalidades de paridade. Paridade é o preço
   de entrada.
5. **Preço**: a tabela do passo 2.
6. **FAQ**: as objeções reais, inclusive "posso importar de ferramentas
   {{category}}?" se você construiu um importador.
7. **Chamada final para ação.**

Texto na voz da marca. Rode a checagem de contraste do replica-design na
página.

## Passo 2: preço

`pricing.md`:

- A página pública de preços do original e 2 ou 3 alternativas, numa tabela
  só, com a URL e a data da leitura. Preço muda, então a data importa.
- O que os avaliadores disseram sobre preço e cobrança, vindo do `feedback.md`,
  com contagens.
- O modelo: plano grátis ou trial, por assento ou fixo, mensal e anual (anual
  costuma dar 2 meses grátis).
- No máximo três planos. Nomeie pelo público a que se destinam.
- Conserte no produto as reclamações de cobrança: cancelamento em um clique,
  e-mails de renovação claros, sem saltos surpresa por assento.
- Os produtos e preços do Stripe a criar (o usuário cria).

## Passo 3: listing da loja

Preencha o `listing.json` e rode:

```bash
python3 listing.py replica/launch/listing.json
```

Ele confere os limites da App Store (nome 30, subtítulo 30, texto
promocional 170, palavras-chave 100, descrição 4000) e do Google Play (título
30, descrição curta 80, completa 4000), conta caracteres como uma pessoa
contaria, aponta promessas de ranking e de preço nos campos curtos, emoji,
caracteres desperdiçados nas palavras-chave e **qualquer nome da lista
`avoid`** em qualquer ponto do listing. Sai com código 1 em caso de erro.

A Diretriz 4.1 (Copycats) do App Review da Apple reprova apps que apenas
copiam um app popular ou fazem mudanças mínimas no nome ou na interface de
outro app. O que te faz passar na revisão são os seus consertos e a sua marca
própria, então deixe-os visíveis nos screenshots e nas primeiras linhas da
descrição.

Prepare também: screenshots nos tamanhos exigidos hoje (confira no App Store
Connect e no Play Console na hora do envio, eles mudam), rótulos de
privacidade e o formulário de segurança de dados, política de privacidade e
URLs de suporte, classificação etária e notas para o revisor com uma conta de
demonstração que ele possa usar.

## Passo 4: plano de lançamento

`launch-plan.md`: lista de espera ou de beta antes do lançamento, analytics e
rastreamento de erros no ar, onde os usuários insatisfeitos do original
conversam (os threads do Reddit e as comunidades da pesquisa), um post no
Product Hunt ou no Hacker News que abra com o conserto, e os 10 primeiros
usuários para conversar um a um.

## Saída

`replica/launch/` completo, landing page construída, `listing.py` passando.
Próximo: `/replica-deploy`.
