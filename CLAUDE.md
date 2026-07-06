# Projeto git1 — Memória compartilhada (computador ↔ celular)

Este arquivo é a "ponte" entre as sessões do Claude Code no computador e no
celular/web. Como o histórico de chat NÃO sincroniza entre ambientes, usamos
este arquivo (versionado no Git) para guardar o contexto que importa.

## Como funciona a integração

- O que conecta os dois lados é o **GitHub**, não o chat.
- Tudo que for commitado e enviado (`push`) num lado, aparece no outro.
- O histórico da conversa em si é isolado por sessão — por isso anotamos aqui
  o estado do trabalho antes de trocar de dispositivo.

## Fluxo recomendado

1. **Ao terminar no computador:** peça pra atualizar a seção "Estado atual"
   abaixo, faça commit e push.
2. **Ao abrir no celular:** o Claude lê este arquivo e retoma de onde parou.
3. **Vale o inverso também** (celular → computador).

## Comandos úteis no computador (CLI)

- `claude --continue` — retoma a última conversa local.
- `claude --resume` — lista as sessões locais para escolher.

> Observação: `--continue`/`--resume` só funcionam para o histórico LOCAL do
> computador. Eles não puxam as sessões web/celular.

## Estado atual

- Branch de trabalho: `claude/sync-computer-mobile-chat-eiac3n`.
- **Objetivo:** instalar os MCPs oficiais do Google (Ads + Analytics) no PC.
- Guias no repo: `docs/mcp-google-setup.md` e `docs/google-ads-api-design-doc.rtf`.

### Google Ads MCP
- [x] Formulário de solicitação do **developer token** enviado ao Google.
- [ ] Aguardando aprovação do token (revisão manual, horas a dias).
- [ ] Após aprovado: configurar o MCP (seção 2 do guia).

### Google Analytics MCP
- [ ] Instalar (não depende do token do Ads — pode fazer já). Seção 1 do guia.

### Próximos passos
- Instalar o Analytics MCP agora (no terminal do PC, com `claude`).
- Quando o token do Ads sair, plugar o Google Ads MCP.
