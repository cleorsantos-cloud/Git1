#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de Recibo de Aluguel em PDF editável (AcroForm).

Cria um arquivo PDF com campos de formulário preenchíveis diretamente em
qualquer leitor de PDF (Adobe Acrobat, Foxit, navegadores, etc.), incluindo
o campo "Desconto de Pontualidade".

Gera duas páginas: a 1ª via (Locatário) e a 2ª via (Locador).

Uso:
    python3 gerar_recibo_aluguel.py [arquivo_saida.pdf]

Se nenhum arquivo for informado, gera "recibo_aluguel.pdf" na pasta atual.
"""

import sys

from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

# Paleta simples e sóbria
AZUL = HexColor("#1f3a5f")
CINZA = HexColor("#666666")
CINZA_CLARO = HexColor("#f0f0f0")
BORDA = HexColor("#bbbbbb")
VERDE = HexColor("#1a7f37")

LARGURA, ALTURA = A4
MARGEM = 20 * mm
LARGURA_UTIL = LARGURA - 2 * MARGEM


def _campo(c, nome, x, y, largura, altura, *, valor="", tamanho=10, alinhamento="L", multilinha=False):
    """Adiciona um campo de texto editável ao formulário."""
    flags = ""
    if multilinha:
        flags = "multiline"
    c.acroForm.textfield(
        name=nome,
        tooltip=nome.replace("_", " ").capitalize(),
        x=x,
        y=y,
        width=largura,
        height=altura,
        value=valor,
        fontSize=tamanho,
        borderWidth=0.7,
        borderColor=BORDA,
        fillColor=HexColor("#fbfbfb"),
        textColor=black,
        forceBorder=True,
        fieldFlags=flags,
    )


def _rotulo(c, texto, x, y, *, tamanho=7.5, cor=CINZA, negrito=False):
    c.setFont("Helvetica-Bold" if negrito else "Helvetica", tamanho)
    c.setFillColor(cor)
    c.drawString(x, y, texto)


# Altura padrão dos campos e folga entre o rótulo e o topo do campo
H = 7 * mm          # altura do campo de texto
GAP_ROTULO = 1.5 * mm   # distância do rótulo acima do campo


def bloco(c, rotulo, nome, x, y, largura, **kw):
    """Desenha rótulo + campo. Retorna o novo y (abaixo do bloco)."""
    _rotulo(c, rotulo, x, y + H + GAP_ROTULO, tamanho=kw.pop("tam_rotulo", 7.5))
    _campo(c, nome, x, y, largura, H, **kw)


def desenhar_via(c, via):
    """Desenha uma via completa do recibo em uma página A4 inteira."""
    sufixo = "_v1" if via == 1 else "_v2"
    y = ALTURA - MARGEM

    # -------- Cabeçalho --------
    alt_cab = 16 * mm
    c.setFillColor(AZUL)
    c.rect(MARGEM, y - alt_cab, LARGURA_UTIL, alt_cab, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(MARGEM + 6 * mm, y - 10.5 * mm, "RECIBO DE ALUGUEL")

    # Nº do recibo (caixa branca à direita, dentro do cabeçalho)
    _rotulo(c, "RECIBO Nº", MARGEM + LARGURA_UTIL - 52 * mm, y - 6 * mm, cor=white, tamanho=8)
    _campo(c, f"numero_recibo{sufixo}", MARGEM + LARGURA_UTIL - 52 * mm, y - 13 * mm, 44 * mm, 6 * mm, tamanho=10)

    y -= alt_cab + 12 * mm

    # -------- Valor em destaque + mês de referência --------
    faixa = 11 * mm
    c.setFillColor(CINZA_CLARO)
    c.rect(MARGEM, y - 2 * mm, LARGURA_UTIL, faixa, fill=1, stroke=0)
    c.setFillColor(AZUL)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(MARGEM + 5 * mm, y + 2 * mm, "VALOR:  R$")
    _campo(c, f"valor_recebido{sufixo}", MARGEM + 34 * mm, y + 0.5 * mm, 45 * mm, 7 * mm, tamanho=13)

    _rotulo(c, "MÊS DE REFERÊNCIA", MARGEM + 90 * mm, y + 10.5 * mm)
    _campo(c, f"mes_referencia{sufixo}", MARGEM + 90 * mm, y + 0.5 * mm, LARGURA_UTIL - 95 * mm, 7 * mm, tamanho=11)

    y -= 20 * mm

    # -------- Dados do locatário --------
    bloco(c, "RECEBI(EMOS) DE (LOCATÁRIO)", f"locatario{sufixo}", MARGEM, y, LARGURA_UTIL * 0.62)
    bloco(c, "CPF / CNPJ", f"cpf_locatario{sufixo}", MARGEM + LARGURA_UTIL * 0.64, y, LARGURA_UTIL * 0.36)
    y -= H + 9 * mm

    bloco(c, "A IMPORTÂNCIA DE (POR EXTENSO)", f"valor_extenso{sufixo}", MARGEM, y, LARGURA_UTIL, tamanho=9)
    y -= H + 9 * mm

    bloco(c, "REFERENTE AO ALUGUEL DO IMÓVEL SITUADO EM", f"endereco_imovel{sufixo}", MARGEM, y, LARGURA_UTIL, tamanho=9)
    y -= H + 12 * mm

    # -------- Demonstrativo de valores --------
    col_val_x = MARGEM + LARGURA_UTIL - 50 * mm
    larg_val = 50 * mm

    # Cabeçalho da tabela
    c.setFillColor(AZUL)
    c.rect(MARGEM, y, LARGURA_UTIL, 7 * mm, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(MARGEM + 3 * mm, y + 2 * mm, "DESCRIÇÃO")
    c.drawString(col_val_x + 2 * mm, y + 2 * mm, "VALOR (R$)")
    y -= 2 * mm

    def linha(rotulo, nome, *, negrito=False, cor=black, destaque=False):
        nonlocal y
        altura_linha = 9 * mm
        y -= altura_linha
        if destaque:
            c.setFillColor(CINZA_CLARO)
            c.rect(MARGEM, y - 1 * mm, LARGURA_UTIL, altura_linha, fill=1, stroke=0)
        c.setFillColor(cor)
        c.setFont("Helvetica-Bold" if negrito else "Helvetica", 10)
        c.drawString(MARGEM + 3 * mm, y + 1.5 * mm, rotulo)
        _campo(c, f"{nome}{sufixo}", col_val_x, y, larg_val, 6.5 * mm, tamanho=11, alinhamento="R")

    linha("Valor do aluguel", "valor_aluguel")
    # >>> Campo solicitado: Desconto de Pontualidade <<<
    linha("(-) Desconto de pontualidade", "desconto_pontualidade", cor=VERDE)
    linha("(+) Água / Condomínio / IPTU / outros encargos", "encargos")
    linha("(+) Multa / Juros por atraso", "multa_juros")
    linha("VALOR TOTAL PAGO", "valor_total", negrito=True, destaque=True)

    y -= 14 * mm

    # -------- Datas e forma de pagamento --------
    bloco(c, "VENCIMENTO", f"vencimento{sufixo}", MARGEM, y, 42 * mm)
    bloco(c, "DATA DE PAGAMENTO", f"data_pagamento{sufixo}", MARGEM + 50 * mm, y, 42 * mm)
    bloco(c, "FORMA DE PAGAMENTO", f"forma_pagamento{sufixo}", MARGEM + 100 * mm, y, LARGURA_UTIL - 100 * mm)
    y -= H + 20 * mm

    # -------- Local, data e assinatura do locador --------
    bloco(c, "LOCAL E DATA", f"local_data{sufixo}", MARGEM, y, LARGURA_UTIL * 0.5)

    ass_x = MARGEM + LARGURA_UTIL * 0.55
    ass_larg = LARGURA_UTIL * 0.45
    bloco(c, "LOCADOR (NOME / ASSINATURA)", f"locador{sufixo}", ass_x, y, ass_larg)
    y -= H + 9 * mm
    bloco(c, "CPF / CNPJ DO LOCADOR", f"cpf_locador{sufixo}", ass_x, y, ass_larg)

    # -------- Rodapé: identificação da via --------
    c.setFillColor(AZUL)
    c.setFont("Helvetica-Bold", 9)
    etiqueta = "1ª VIA — LOCATÁRIO" if via == 1 else "2ª VIA — LOCADOR"
    c.drawString(MARGEM, MARGEM - 2 * mm, etiqueta)
    c.setFillColor(CINZA)
    c.setFont("Helvetica-Oblique", 7)
    c.drawRightString(
        MARGEM + LARGURA_UTIL, MARGEM - 2 * mm,
        "Preencha os campos diretamente no leitor de PDF.",
    )


def gerar(caminho_saida):
    c = canvas.Canvas(caminho_saida, pagesize=A4)
    c.setTitle("Recibo de Aluguel")
    c.setAuthor("Recibo de Aluguel")
    c.setSubject("Recibo de aluguel editável com campo de desconto de pontualidade")

    desenhar_via(c, via=1)
    c.showPage()
    desenhar_via(c, via=2)
    c.showPage()
    c.save()


def main():
    saida = sys.argv[1] if len(sys.argv) > 1 else "recibo_aluguel.pdf"
    gerar(saida)
    print(f"PDF editável gerado: {saida}")


if __name__ == "__main__":
    main()
