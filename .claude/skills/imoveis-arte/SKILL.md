---
name: imoveis-arte
description: Criação de artes no Canva para Instagram de corretor de imóveis — carrossel (cada slide) e post estático. Estilo limpo, minimalista, paleta SP Clean (branco + azul-noite + dourado). Use sempre que precisar criar o design visual de um post de imóveis para Instagram. Ative quando o usuário pedir "cria a arte", "faz o design", "gera o carrossel no Canva", "monta o post visual", "faz a imagem do slide", "cria o post no Canva" ou qualquer variação de criação de design para redes sociais imobiliárias.
---

# imoveis-arte — Design para Instagram Imobiliário

Você cria o design visual dos posts de Instagram para um corretor de imóveis em SP. O copy já vem da skill `imoveis-copy` (ou do usuário diretamente). Seu trabalho é transformar o texto em designs no Canva usando a identidade visual SP Clean.

O estilo é limpo, minimalista e profissional — sem parecer banco nem imobiliária grande, sem fotos de imóvel (o usuário não tem banco de imagens).

---

## Identidade visual: SP Clean

Aplique esta identidade em todos os designs:

| Elemento | Valor |
|---|---|
| Fundo principal | Branco (#FFFFFF) |
| Bloco de cor | Azul-noite (#1C3041) |
| Texto sobre branco | Quase-preto (#1A1A1A) |
| Texto sobre azul | Branco (#FFFFFF) |
| Acento/destaque | Dourado quente (#C9A260) |
| Fonte | Montserrat Bold para título, Montserrat Regular para subtexto |

**Regras de composição:**
- Texto centralizado e grande o suficiente para ser lido sem dar zoom
- Margem generosa nas bordas (mínimo 8% da largura)
- Sem ícones decorativos, bordas floridas ou elementos desnecessários
- O slide de CTA (último slide do carrossel) usa fundo azul-noite (#1C3041) com texto branco — cria contraste visual na hora de deslizar

---

## Entrada esperada

**Vindo do imoveis-copy:** use o texto exato dos slides + legenda já produzido.

**Chegando direto:** pergunte apenas o que for estritamente necessário:
- Carrossel ou post estático?
- Texto de cada slide (se não veio do imoveis-copy)

---

## Fluxo: carrossel

### Passo 1 — Gere o slide 1 no Canva

Slide 1 é o mais importante: para o scroll. Gere com `generate-design`:

- `design_type`: `"instagram_post"` (1080×1350px, 4:5)
- `query` em inglês (Canva performa melhor):

```
Minimalist Instagram carousel slide for São Paulo real estate agent.
White background (#FFFFFF). Large bold dark navy heading: "[TEXTO DO SLIDE 1]".
Montserrat Bold font. Centered layout. Clean and professional.
Thin warm gold (#C9A260) bottom accent bar. No photos, no icons.
[Se houver subtexto: smaller Montserrat Regular gray subtext below: "[SUBTEXTO]"]
```

Substitua `[TEXTO DO SLIDE 1]` e `[SUBTEXTO]` pelo conteúdo real.

Apresente os candidatos ao usuário. Quando ele escolher, salve com `create-design-from-candidate`.

### Passo 2 — Brief dos slides restantes

Após confirmar o estilo, entregue este brief para o usuário duplicar e editar no Canva:

```
BRIEF — CARROSSEL COMPLETO

Instruções: abra o Slide 1 no Canva, clique com botão direito na página
e selecione "Duplicar página" para cada slide. Edite apenas os textos.

SLIDE 1 ✅ já criado no Canva

SLIDE 2:
  Título: [texto]
  Subtexto: [texto se houver]
  Fundo: branco

SLIDE 3:
  Título: [texto]
  Subtexto: [texto se houver]
  Fundo: branco

[...repita para cada slide intermediário...]

SLIDE [N] — CTA (último slide):
  Texto: [CTA]
  Fundo: azul-noite (#1C3041) — inverta as cores deste slide
  Texto: branco (#FFFFFF)
  Instrução no Canva: selecione o fundo, mude para #1C3041.
  Selecione o texto, mude para #FFFFFF.
```

### Opção: gerar todos os slides no Canva

Se o usuário pedir para gerar todos (mais demorado mas sem trabalho manual), gere um por um em sequência usando o mesmo prompt base. Adapte apenas o texto. Para o slide CTA, use:

```
Minimalist Instagram carousel final slide, São Paulo real estate.
Dark navy background (#1C3041). Bold white centered CTA text: "[TEXTO CTA]".
Montserrat Bold. Gold (#C9A260) thin accent element. No photos.
```

Salve cada slide com `create-design-from-candidate` e liste todos os links ao final.

---

## Fluxo: post estático

Uma única imagem. Gere 2 candidatos para o usuário escolher.

**Candidato A — fundo branco (mais leve):**
```
Minimalist Instagram post, São Paulo real estate agent.
White background. Very large bold dark navy text: "[TEXTO DA IMAGEM]".
Montserrat Bold, centered. Warm gold (#C9A260) thin bottom bar accent.
No photos, no clutter. Professional and clean.
```

**Candidato B — fundo azul-noite (mais impacto):**
```
Bold minimalist Instagram post, São Paulo real estate.
Deep navy background (#1C3041). Large bold white text: "[TEXTO DA IMAGEM]".
Montserrat Bold, centered. Warm gold (#C9A260) subtle accent element.
High contrast, professional, no photos.
```

Apresente ambos. Quando o usuário escolher, salve com `create-design-from-candidate` e informe o link.

---

## Regras gerais de execução

- Sempre `design_type: "instagram_post"` — nunca `poster`, `flyer` ou outro tipo
- Prompts sempre em inglês — o gerador do Canva responde melhor
- Se os candidatos gerados não respeitarem o estilo (muito colorido, com fotos, fonte errada), refine o prompt adicionando mais restrições e tente mais uma vez antes de reportar problema
- Ao final de cada geração, liste os links dos designs criados no Canva para o usuário acessar
- Nunca use fotos de imóveis — o usuário não tem banco de imagens e arte limpa com texto converte mais
