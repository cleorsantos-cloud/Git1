---
name: replica-test
description: >-
  Clica por todos os fluxos de um clone de app e testa à procura de bugs:
  plano de testes gerado a partir dos fluxos do recon com caminhos felizes e
  casos de borda, testes end-to-end com Playwright onde der, passada manual no
  navegador onde não der, e relatórios de bug em formato fixo com severidade,
  passos e evidência. Use quando o usuário disser "testa meu clone", "acha os
  bugs", "faz um QA disso", "clica em tudo", "escreve os testes e2e", "isso
  funciona?", ou depois do /replica-build ou /replica-backend. Gatilhos em
  inglês: "test my clone", "find bugs", "QA this", "click through everything",
  "write e2e tests", "does it work".
---

# replica-test

## Contrato de execução

PASSOS: plano de testes → automatizar → clicar no resto → reportar bugs → loop de correção
BLOQUEIA: nenhum. Todo passo pode ser pulado ou reordenado conforme o projeto.
PODE PULAR: qualquer passo, desde que apareça como ⏭️ no recibo com o motivo.
RECIBO: RECIBO: replica-test | ✅<passo> · ⏭️<passo>(motivo) | testes passando/total · bugs abertos por severidade

Checklist: antes de começar, crie um todo por passo acima; marque cada um ao terminar ou ao pular.

Lê os fluxos em `replica/recon.md`. Escreve `replica/test-plan.md`,
`replica/bugs.md` e testes end-to-end no projeto (`e2e/`). Templates nesta
pasta: `test-plan.md`, `bug-report.md`, `e2e.example.spec.ts`.

## A regra

**Teste o seu clone, não o original.** Nunca faça load test, fuzz, script ou
martelada nos servidores do app original. Usar o original à mão, como um
usuário normal, para ver como ele se comporta, tudo bem.

## Passo 1: o plano

Para cada fluxo F01, F02... do mapa do recon, escreva:

- **Caminho feliz**: os passos e o que o usuário deve ver no final.
- **Casos de borda** que se aplicam. Passe por esta lista em todo fluxo:
  entrada vazia, entrada muito longa, emoji e acentos, duas abas ao mesmo
  tempo, clique duplo no submit, botão voltar no meio do fluxo, refresh no
  meio do fluxo, rede lenta, offline, sessão expirada, dados de um segundo
  usuário (devem ser invisíveis), fusos horários e horário de verão, largura
  mobile, só teclado, labels para leitor de tela.
- **Casos negativos**: senha errada, cartão recusado (cartão de teste do
  Stripe `4000 0000 0000 0002`), permissão negada, registro apagado.

Numere todo caso: F01-H1, F01-E3, F01-N2.

## Passo 2: automatize o que der

Playwright, um spec por fluxo, contra o servidor de desenvolvimento local com
dados de seed. Use roles e labels como seletores
(`getByRole('button', { name: 'Book' })`), nunca classes CSS. Veja
`e2e.example.spec.ts`.

```bash
npm i -D @playwright/test && npx playwright install chromium
npx playwright test
```

Acrescente a todo spec: falhar em erros de console, falhar em qualquer
resposta 5xx e um scan de acessibilidade com axe (`@axe-core/playwright`) em
cada tela.

## Passo 3: clique pelo resto

O que não dá para automatizar (e-mails chegando, OAuth com provedores reais,
pagamentos de ponta a ponta, glitches visuais) recebe uma passada manual. Se
houver uma ferramenta de navegador, dirija o clone local com ela e tire
screenshot de cada passo. Senão, entregue o checklist ao usuário e espere as
respostas.

## Passo 4: reporte os bugs

Todo bug vai em `replica/bugs.md` no formato do `bug-report.md`: um ID, uma
severidade, passos exatos, esperado, obtido, evidência. Severidade:

| | significa |
| --- | --- |
| S1 | perda de dados, falha de segurança, pagamento errado, fluxo principal bloqueado |
| S2 | uma feature quebrada, sem contorno |
| S3 | quebrada mas com contorno, ou visivelmente errada |
| S4 | cosmético |

Reporte só o que você reproduziu. "Pode ser um problema" vai numa lista
separada de "a verificar".

## Passo 5: loop de correção

Corrija S1 e S2 primeiro. Em cada correção: escreva o teste que falha
primeiro, corrija, veja o teste passar, mantenha o teste. Rode a suíte inteira
depois de cada lote. Atualize o `bugs.md` com o commit que corrigiu cada um.

## Saída

`test-plan.md`, os specs, `bugs.md` e um resumo: casos executados, passaram,
falharam, bugs por severidade, corrigidos até agora. Não publique nada com
S1 aberto. Próximo: `/replica-diff`.
