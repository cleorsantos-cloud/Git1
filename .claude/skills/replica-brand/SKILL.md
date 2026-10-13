---
name: replica-brand
description: >-
  Batiza e faz o rebrand de um clone de app para que seja do próprio usuário:
  candidatos de nome com as checagens de marca, domínio, loja e handle a
  rodar, uma paleta nova com contraste verificado, um brief de logo, um guia
  de voz e uma ferramenta de varredura que acha qualquer sobra do original no
  código. Use quando o usuário disser "dá um nome pro meu app", "faz o rebrand
  do clone", "faz isso virar meu", "escolhe nome e cores", "brief de logo",
  "voz da marca", "confere se sobrou algo do original", ou depois do
  /replica-entrepreneur. Roda sempre antes do /replica-launch. Gatilhos em
  inglês: "name my app", "rebrand the clone", "make it mine", "pick a name and
  colours", "logo brief", "brand voice", "check for leftovers".
---

# replica-brand

## Contrato de execução

PASSOS: nome → checagens → paleta → brief de logo → voz → varredura
BLOQUEIA: nenhum. Todo passo pode ser pulado ou reordenado conforme o projeto.
PODE PULAR: qualquer passo, desde que apareça como ⏭️ no recibo com o motivo.
RECIBO: RECIBO: replica-brand | ✅<passo> · ⏭️<passo>(motivo) | nome escolhido · sobras do original na varredura

Checklist: antes de começar, crie um todo por passo acima; marque cada um ao terminar ou ao pular.

Nada é lançado sob a identidade do original. Esta skill é a linha entre "um
clone" e "o seu app".

Ferramenta nesta pasta:

```bash
python3 sweep.py . --avoid "Original Name,Its Company" --domains original.com --colors "#006bff"
python3 sweep.py . --config replica/brand.json        # same, from the brand file
```

Grava `replica/brand.md` e `replica/brand.json` (`avoid`, `domains`,
`colors`, usados pelo `sweep.py`, pelo `listing.py` e pelo replica-deploy).

## Passo 1: o nome

Leia o ângulo em `replica/fixes.md`. Gere 20 candidatos em estilos variados:
descritivo (Booklink), composto (Slotwise), inventado (Calvo), metáfora
(Harbor), verbo (Book). Depois corte para 5 com estes filtros:

- **Não pode ser confundível com o original** em som, aparência ou
  significado, nem com qualquer outro app da mesma categoria. Esse é o teste
  que os escritórios de marcas usam, então é o teste daqui. Nada de trocadilho
  com o nome deles, nada de gêmeo com "-ly".
- Curto, soletrável depois de ouvir uma vez, sem significado estranho nos
  idiomas grandes.
- Diz algo sobre o ângulo, ou pelo menos não briga com ele.

## Passo 2: as checagens, executadas, não presumidas

Para cada um dos 5, uma linha por checagem. Marque cada uma como **a rodar**,
ou com o resultado e a data em que foi rodada. Nunca escreva "disponível"
para uma checagem que ninguém rodou.

| checagem | onde |
| --- | --- |
| marca nos EUA | tmsearch.uspto.gov, a classe do app (geralmente 9 e 42) |
| marca na UE | euipo.europa.eu eSearch, ou TMview para vários escritórios |
| Canadá | base de marcas de ised-isde.canada.ca |
| global | WIPO Global Brand Database |
| domínio | `whois name.com`, ou a busca do registrador |
| App Store e Play | busque o nome exato |
| handles | X, Instagram, TikTok, GitHub |
| a web | busque "nome + categoria" |

São checagens de triagem, não liberação jurídica. Antes de gastar dinheiro com
o nome, um advogado de marcas deve fazer uma busca de verdade.

## Passo 3: paleta

Uma paleta nova, escrita nos mesmos papéis de token que o replica-design
montou. Escolha um matiz de marca primário de uma família diferente da do
original (se o dele é azul, o seu não é um azul parecido). Depois:

```bash
python3 ../replica-design/contrast.py replica/design/tokens.json
```

Zero falhas de AA. Adicione as cores de marca do original ao `brand.json`
para que a varredura pegue qualquer uma que sobreviva.

## Passo 4: brief de logo

Não é um logo, é um brief para quem for fazê-lo (o usuário, um designer, um
modelo de imagem):

- a ideia em uma linha, ligada ao nome e ao ângulo
- tipo de marca: wordmark, símbolo mais wordmark, ou monograma
- tem que funcionar em 16px (favicon) e como ícone de app em 1024px
- entregáveis: SVG, ícone de app 1024x1024 sem transparência para iOS, kit de
  favicon, imagem social 1200x630
- **não pode lembrar a marca do original**: nada de forma, par de cores ou
  truque de letra em comum. Ponha o logo do original ao lado dos rascunhos e
  confira.

## Passo 5: voz

Três palavras para como ela soa, com o que cada uma não significa ("direta,
não ríspida"). Cinco pares de faça e não faça. Depois reescreva nessa voz as
10 strings mais vistas do clone (cadastro, estados vazios, o botão principal,
a confirmação, o erro). Tudo novo, nada ecoando a formulação do original.

## Passo 6: a varredura

Troque todo nome, cor e string provisórios. Depois:

```bash
python3 sweep.py . --config replica/brand.json
```

Ela procura no conteúdo e nos nomes dos arquivos o nome do original (inclusive
dentro de identificadores como `CalendlyEmbed`), domínios e cores, ignorando
`node_modules`, saída de build e a pasta de planejamento `replica/`. Saída 1
significa que sobrou algo. Corrija até ela dizer que está limpo. Confira
também a olho: o favicon, os títulos das páginas, os templates de e-mail, a
imagem OG, o ícone do app.

## Saída

`replica/brand.md` (nome com as checagens, paleta, brief de logo, voz),
`replica/brand.json`, tokens atualizados, strings reescritas e uma varredura
limpa. Próximo: `/replica-launch`.
