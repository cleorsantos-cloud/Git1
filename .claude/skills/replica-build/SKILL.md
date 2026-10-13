---
name: replica-build
description: >-
  Reconstrói um app tela por tela a partir do mapa do recon: primeiro o shell
  do app, depois o fluxo principal como fatia vertical, depois cada tela com
  todos os seus estados, marcando a matriz de features conforme avança.
  Escreve cada linha do zero, nunca o código, os assets ou os textos do
  original. Use quando o usuário disser "constrói o clone", "constrói a tela
  S07", "começa a construir", "refaz essa tela", "implementa a página de
  agendamento", ou depois do /replica-design. Gatilhos em inglês: "build the
  clone", "build screen S07", "start building", "rebuild this screen",
  "implement the booking page".
---

# replica-build

## Contrato de execução

PASSOS: shell do app → fatia vertical → tela por tela → build log
BLOQUEIA: nenhum. Todo passo pode ser pulado ou reordenado conforme o projeto.
PODE PULAR: qualquer passo, desde que apareça como ⏭️ no recibo com o motivo.
RECIBO: RECIBO: replica-build | ✅<passo> · ⏭️<passo>(motivo) | telas prontas / total · features ticadas na matriz

Checklist: antes de começar, crie um todo por passo acima; marque cada um ao terminar ou ao pular.

Lê `replica/recon.md`, `replica/architecture.md`, `replica/design/`.
Atualiza `replica/features.csv` (a coluna `clone`) e mantém
`replica/build-log.md`.

## As regras

- **Clean room.** Cada linha de código é escrita aqui, a partir do mapa do
  recon e das specs. Nunca cole o HTML, CSS, JavaScript, SVGs ou imagens do
  original, nunca carregue nada do domínio ou da CDN dele, nunca "veja o
  código-fonte e adapte".
- **Suas palavras.** Escreva do zero cada rótulo, botão, estado vazio e
  e-mail. Igualar o que um botão faz é paridade. Igualar a frase dele é
  cópia.
- **Só tokens.** Nada de hex ou valores em pixel soltos nos componentes. Se
  falta um valor, acrescente-o aos tokens.

## Passo 1: o shell do app

Roteamento de todas as telas do inventário (páginas stub servem), o layout
(nav, header, sidebar), os tokens ligados, os primitivos do replica-design e
dados de seed para as telas terem algo real para mostrar. Faça commit.

## Passo 2: a fatia vertical

O loop principal do mapa do recon, de ponta a ponta, antes de qualquer outra
coisa. Num app de agendamento: criar um tipo de evento, abrir a página
pública, reservar um horário, ver na dashboard. Feio tudo bem. O ponto é
funcionar. Se o replica-backend ainda não rodou, use os dados de seed e uma
camada de dados falsa com as mesmas assinaturas de função, para que trocar
pela real não mude nenhum código de tela.

## Passo 3: tela por tela

Siga a ordem do `architecture.md`. Para cada tela:

1. Leia a linha dela no mapa do recon: propósito, componentes, estados, quais
   fluxos passam por ela.
2. Olhe o screenshot de referência para layout e hierarquia. Não para pixels.
3. Construa com os primitivos. Dados reais vindos da camada de dados.
4. **Todos os estados**: vazio, carregando (skeletons, não spinners, se o
   original usa), preenchido, erro, sem permissão, conteúdo longo (um nome de
   60 caracteres), largura mobile.
5. O básico, sempre: HTML semântico, labels nos inputs, alcançável pelo
   teclado, foco visível, imagens com texto alternativo.
6. Marque as linhas correspondentes do `features.csv` como `yes` ou `partial`
   (com uma nota).
7. Tire um screenshot no mesmo viewport da referência para
   `replica/clone-screens/S07.png`, para o replica-diff.
8. Um commit por tela: `build: S07 booking page`.

## Definição de pronto, por tela

- [ ] todos os estados do mapa do recon, mais vazio, erro e carregando
- [ ] funciona em 390px e 1440px de largura
- [ ] só com teclado: dá para completar o fluxo
- [ ] sem erros no console
- [ ] nenhum texto fixo emprestado do original
- [ ] features.csv atualizado
- [ ] screenshot salvo para o diff

## Passo 4: o build log

`replica/build-log.md`, uma linha por tela: ID, data, pronta ou parcial, o que
falta, o que foi mais difícil do que o esperado. Quando uma feature se mostrar
maior do que parecia, diga isso no log e no chat. Não entregue metade dela em
silêncio.

## Quando travar em como algo funciona

Volte ao original como usuário: leia o artigo de ajuda, veja o walkthrough
público, use a conta do próprio usuário. Não escarafunche o código nem as
chamadas de rede dele. Depois construa a sua própria versão do comportamento.

## Saída

Telas construídas, matriz de features atualizada, screenshots salvos e um
resumo: telas prontas do total, must-haves prontos do total, o que vem a
seguir. Depois `/replica-backend` se a camada de dados ainda é falsa, senão
`/replica-test`.
