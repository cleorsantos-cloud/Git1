---
name: replica-diff
description: >-
  Compara um clone de app com o original: nota de paridade de funcionalidades
  a partir da matriz de features (ponderada por must, should, could) com a
  lista do que falta na ordem de construção, mais um diff de layout por
  screenshots que ignora cor, para que um rebrand não conte contra você. Duas
  ferramentas Python só com biblioteca padrão. Use quando o usuário disser
  "quão perto está meu clone", "compara com o original", "o que falta",
  "checagem de paridade", "diff das telas", "está pronto?", ou depois do
  /replica-test. Gatilhos em inglês: "how close is my clone", "compare it to
  the original", "what's missing", "parity check", "diff the screens", "is it
  ready".
---

# replica-diff

## Contrato de execução

PASSOS: paridade de features → diff de layout → diff de comportamento → relatório
BLOQUEIA: nenhum. Todo passo pode ser pulado ou reordenado conforme o projeto.
PODE PULAR: qualquer passo, desde que apareça como ⏭️ no recibo com o motivo.
RECIBO: RECIBO: replica-diff | ✅<passo> · ⏭️<passo>(motivo) | score de paridade % · must-haves faltando

Checklist: antes de começar, crie um todo por passo acima; marque cada um ao terminar ou ao pular.

Duas ferramentas nesta pasta, ambas Python com biblioteca padrão, sem instalar nada:

```bash
python3 parity.py replica/features.csv                         # feature parity + missing list
python3 imgdiff.py replica/screens/S07.png replica/clone-screens/S07.png --out diff-S07.png
python3 imgdiff.py a.png b.png --json > replica/diffs/S07.json # for parity.py --visual
python3 parity.py replica/features.csv --visual replica/diffs/*.json --markdown > replica/parity.md
```

## O que paridade significa aqui

**Paridade significa fazer o mesmo trabalho, não ter a mesma aparência.** A
nota de funcionalidades é o número que importa: o usuário consegue fazer tudo
o que fazia no original? A nota de layout confere a estrutura (a informação
está nos mesmos lugares, na mesma hierarquia), porque é isso que faz quem está
migrando se sentir em casa. Ela ignora a cor de propósito, porque o
replica-brand troca todas as cores de propósito. Não persiga paridade de
pixel com o original. O visual exato dele é o trade dress, e ele muda antes
do lançamento.

## Passo 1: paridade de features

Confirme que o `replica/features.csv` está atualizado: a coluna `clone` de
cada linha é `yes`, `partial` (com nota), `no` ou `skip` (com motivo). Depois:

```bash
python3 parity.py replica/features.csv
```

Ele pesa must 3, should 2, could 1, conta partial como metade, deixa de fora
as linhas `skip` e as linhas que você adicionou e que o original não tem, e
imprime: a nota, os must-haves feitos do total, cada área da mais fraca para a
mais forte, e a lista do que falta na ordem de construção. Must-haves não
concluídos significa que não dá para lançar, e ele avisa.

## Passo 2: diff de layout

Para cada tela-chave, tire dois screenshots no **mesmo viewport** (1440x900
desktop, 390x844 mobile) e no **mesmo estado** (mesmo formato de dados, mesma
aba aberta, logado do mesmo jeito). Os do original vêm de páginas públicas ou
da conta do próprio usuário, salvos em `replica/screens/`. Os do clone vão em
`replica/clone-screens/`.

```bash
python3 imgdiff.py replica/screens/S07.png replica/clone-screens/S07.png --out replica/diffs/S07.png
```

O modo layout (padrão) transforma os dois em mapas de bordas, corta em uma
grade e compara onde as coisas estão, pontuando só as células que têm
conteúdo. Ele informa a nota (igual 90+, próximo 75+, parcial 50+, diferente),
as regiões que diferem (nas coordenadas de pixel do original, maiores
primeiro) e a diferença de altura, se a página do clone for muito mais longa
ou mais curta. Screenshots retina e não retina podem ser comparados: ambos
são escalados para a mesma largura.

`--mode pixel` é comparação exata. Use para as suas próprias regressões (clone
de hoje contra clone da semana passada), não contra o original.

## Passo 3: diff de comportamento

Percorra cada fluxo nos dois apps e compare o que as notas não enxergam:
cliques para concluir o fluxo principal, o que acontece nos erros, o que é
lembrado entre visitas, quais e-mails chegam. Menos cliques que o original é
vitória. Escreva cada diferença assim: fluxo, o original faz, o clone faz,
corrigir ou manter.

## Passo 4: o relatório

`replica/parity.md`: nota geral, nota de funcionalidades, nota de layout por
tela, funcionalidades faltando na ordem de construção, diferenças de
comportamento e um veredito:

- **não lançável**: qualquer must-have faltando, ou qualquer bug S1 aberto
- **lançável**: todos os must-haves feitos, nota de funcionalidades 80+, sem S1 nem S2 abertos
- **melhor que o original**: lançável, mais as correções vindas do
  replica-entrepreneur. Este é o objetivo. Uma cópia pura não tem razão de existir.

Dê números honestos. Um clone com 62% está em 62%.

## Saída

`replica/parity.md`, as imagens de diff e as cinco primeiras coisas a
construir. Depois `/replica-build` para as lacunas, ou `/replica-entrepreneur`
se a paridade já estiver boa.
