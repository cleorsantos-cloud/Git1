# Recibo de Aluguel em PDF editável

Modelo de **recibo de aluguel em PDF preenchível** (com campos de formulário
AcroForm), incluindo o campo de **Desconto de Pontualidade**. Os campos podem
ser preenchidos diretamente no leitor de PDF (Adobe Acrobat/Reader, Foxit,
navegadores como Chrome/Edge, Preview do macOS, etc.) — sem precisar imprimir.

## Arquivos

| Arquivo | Descrição |
|---|---|
| `recibo_aluguel.pdf` | Recibo pronto para usar. 2 páginas: **1ª via (Locatário)** e **2ª via (Locador)**. |
| `gerar_recibo_aluguel.py` | Script que gera o PDF (permite personalizar layout, textos e campos). |

## Como usar

1. Abra `recibo_aluguel.pdf` no seu leitor de PDF.
2. Clique nos campos e preencha (número do recibo, valor, locatário, imóvel,
   valores, datas, etc.).
3. Preencha o **Desconto de pontualidade** quando o pagamento for feito em dia.
4. Salve o PDF preenchido e/ou imprima para assinar.

## Campos disponíveis

- Recibo Nº e Mês de referência
- Valor recebido (R$) e valor por extenso
- Locatário e CPF/CNPJ
- Endereço do imóvel
- **Demonstrativo de valores (cada valor em seu próprio campo):**
  - (+) Valor do aluguel
  - (+) Condomínio
  - (+) IPTU
  - **(-) Desconto de pontualidade (pagamento até o vencimento)**
  - **Valor total pago**
- Vencimento, Data de pagamento e Forma de pagamento
- Local e data
- Locador (nome / assinatura) e CPF/CNPJ do locador

## Gerar novamente / personalizar

Requer Python 3 e a biblioteca `reportlab`:

```bash
pip install reportlab
python3 gerar_recibo_aluguel.py             # gera recibo_aluguel.pdf
python3 gerar_recibo_aluguel.py meu.pdf     # gera com outro nome
```

Edite `gerar_recibo_aluguel.py` para alterar cores, textos dos rótulos ou
adicionar/remover campos.
