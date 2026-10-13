---
name: replica-design
description: >-
  Reconstrói o design system de um app para o clone: papéis de cor, escala
  tipográfica, espaçamento, raio, sombras e cada componente com seus estados,
  como design tokens mais specs de componentes, usando assets originais no lugar
  de logos, ícones, ilustrações ou fontes licenciadas do alvo. Inclui um
  verificador de contraste WCAG. Use quando o usuário disser "iguala o design",
  "reconstrói o design system", "pega as cores e as fontes", "deixa com a cara
  do X", "design tokens pro meu clone", ou depois do /replica-architect.
  Triggers: "match the design", "rebuild the design system", "get the colours
  and fonts", "make it look like X", "design tokens for my clone".
---

# replica-design

## Contrato de execução

PASSOS: medir o original → tokens → specs de componentes → primitivos
BLOQUEIA: nenhum. Todo passo pode ser pulado ou reordenado conforme o projeto.
PODE PULAR: qualquer passo, desde que apareça como ⏭️ no recibo com o motivo.
RECIBO: RECIBO: replica-design | ✅<passo> · ⏭️<passo>(motivo) | tokens definidos · componentes especificados · pares de contraste reprovados

Checklist: antes de começar, crie um todo por passo acima; marque cada um ao terminar ou ao pular.

Lê `replica/recon.md` e as screenshots em `replica/screens/`. Escreve
`replica/design/tokens.json` (template nesta pasta), `tokens.css`, o mapeamento
para o Tailwind e `replica/design/components.md`.

```bash
python3 contrast.py replica/design/tokens.json     # every text pair, WCAG ratio
```

## As regras

O que você reconstrói é o **sistema**: os papéis, a escala, os padrões, o jeito
como um formulário ou um modal se comporta. Isso não tem dono, e os usuários
esperam. O que você nunca leva:

- **Logos, ícones, ilustrações, fotos, sons.** Use um conjunto de ícones aberto
  (Lucide, Phosphor, Heroicons, Tabler, todos MIT ou similar) e faça ou
  encomende suas próprias ilustrações. Não copie as deles pelo contorno.
- **Fontes licenciadas.** Se o original usa uma fonte paga ou proprietária,
  escolha uma aberta com a mesma função: Inter, Geist, IBM Plex, Manrope,
  Source Serif.
- **O texto deles.** Cada rótulo e cada estado vazio é escrito do zero.
- **A cor da marca deles.** Registre como um papel (`accent`), use um
  placeholder neutro por enquanto, e o replica-brand dá a sua própria. A cor
  de assinatura somada ao layout de assinatura é trade dress, e muda antes do
  lançamento.

## Passo 1: meça, não chute

A partir das screenshots (dê zoom, use um conta-gotas de cor na máquina do
usuário):

- **Papéis de cor**, não cores: bg, surface, border, border-input, text,
  text-muted, accent, on-accent, danger, success, warning. Conte quantos cinzas
  o app realmente usa. Geralmente de 5 a 7.
- **Escala tipográfica**: tamanhos, alturas de linha, pesos. Encaixe numa escala
  (12, 14, 16, 20, 28, 40 é comum). Anote a categoria da fonte, não o arquivo.
- **Espaçamento**: meça os vãos entre os elementos. Quase sempre é base 4 ou 8.
  Escreva a escala.
- **Raio, sombra, movimento**: dois ou três de cada.
- **Layout**: largura máxima do conteúdo, grid, breakpoints, largura da
  sidebar, altura do header.

## Passo 2: escreva os tokens

Preencha o `tokens.json`. Mantenha os nomes dos papéis. O replica-brand só
troca os valores. Gere o `tokens.css` como custom properties e mapeie-os no
tema do Tailwind, para que os componentes usem `bg-surface text-muted`, nunca
hex cru.

Adicione uma lista `pairs` com toda combinação de texto e fundo que o app usa,
e então:

```bash
python3 contrast.py replica/design/tokens.json
```

AA é o piso: 4,5:1 para texto corrido, 3:1 para texto grande e para bordas de
campo e anéis de foco. O script sai com código 1 se houver falha. Conserte nos
tokens, não componente por componente.

## Passo 3: specs de componentes

Para cada componente da lista do reconhecimento, um bloco em `components.md`:

```
Button
  variants  primary, secondary, ghost, danger
  sizes     sm 32px, md 40px, lg 48px
  states    default, hover, active, focus-visible (2px ring, accent), disabled, loading
  tokens    bg accent, text on-accent, radius md, font sm/600
  a11y      real <button>, visible focus, loading keeps the label for screen readers
  used on   S02, S07, S09
```

Todo estado que o reconhecimento viu, mais os que ele deveria ter visto: focus,
disabled, loading, error, empty. O comportamento de teclado e de leitor de tela
faz parte da spec.

## Passo 4: construa os primitivos

Construa os componentes em código uma vez, isolados (uma rota `/design` ou
Storybook), antes de qualquer tela. Use uma base acessível se a stack tiver uma
(Radix, shadcn/ui, React Aria). Tire uma screenshot da página. Essa é a
verificação do design system.

## Saída

`tokens.json`, `tokens.css`, a config do Tailwind, `components.md`, os
primitivos construídos e um relatório de contraste com zero falhas AA. Próximo:
`/replica-build`.
