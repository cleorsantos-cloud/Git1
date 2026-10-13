# Arquitetura: {{seu app}} (uma reconstrução das features centrais de {{app}})

## Stack

| camada | escolha | por quê |
| --- | --- | --- |
| web | | |
| banco de dados | | |
| auth | | |
| pagamentos | | |
| e-mail | | |
| jobs | | |
| hospedagem | | |

## Schema

Tabelas: {{n}}. Regras de acesso: {{RLS | checagens na camada de dados}}.

```sql
-- ou veja replica/schema.sql
```

## API

| método caminho | faz o quê | quem | entrada | saída | fluxo |
| --- | --- | --- | --- | --- | --- |

Webhooks de entrada: {{...}}  Webhooks de saída: {{...}}
Jobs: {{nome, agenda, o que faz}}

## As partes que mordem

- fusos horários:
- idempotência:
- condições de corrida:

## Ordem de construção

1. Fatia vertical: {{telas, tabelas, rotas}}
2. Must-haves (obrigatórias):
3. Should-haves (desejáveis):
4. Correções vindas do replica-entrepreneur:
