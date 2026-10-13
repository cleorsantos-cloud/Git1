# Mapa de reconhecimento: {{app}} ({{plataforma}})

Escopo: {{a fatia que está sendo clonada}}
Para: {{para quem é o clone}}
Data: {{AAAA-MM-DD}}

## Fontes

| # | fonte | URL | notas |
| --- | --- | --- | --- |
| 1 | central de ajuda | | |

## Loop central

{{uma frase: aquilo pelo que os usuários pagam}}

## Telas

| ID | tela | rota / como chegar | finalidade | componentes-chave | estados vistos |
| --- | --- | --- | --- | --- | --- |
| S01 | | | | | vazio, preenchido, erro |

## Fluxos

```
F01 {{objetivo}}
    S01 -> S02 -> S03
    cliques do caminho feliz: {{n}}
    edge: {{casos}}
```

## Componentes

| componente | variantes | estados | usado em |
| --- | --- | --- | --- |
| Button | primary, secondary, ghost, danger | default, hover, focus, disabled, loading | todas |

## Modelo de dados inferido

```
{{Entidade}}  {{campos}}
              evidence: {{IDs de tela, artigos de ajuda}}
              confidence: high | medium | guess
```

Relacionamentos: {{User 1-n EventType, EventType 1-n Booking, ...}}

## Matriz de features

Veja `features.csv`. Must (deve): {{n}}, should (deveria): {{n}}, could (poderia): {{n}}, skip (pular): {{n}}.

## Fora do escopo (não dá ou não deve ser clonado)

- {{conteúdo licenciado, a rede, acordos com parceiros, ...}}

## Tamanho

Telas {{n}}, fluxos {{n}}, entidades {{n}}. Partes difíceis: {{lista}}. Tamanho: {{S|M|L|XL}}.
