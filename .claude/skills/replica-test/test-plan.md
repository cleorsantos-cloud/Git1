# Plano de testes: {{seu app}}

Build: {{commit}}  Data: {{AAAA-MM-DD}}  Ambiente: local, dados de seed

| caso | fluxo | tipo | passos | esperado | auto | resultado |
| --- | --- | --- | --- | --- | --- | --- |
| F01-H1 | visitante agenda uma reunião | feliz | abrir /u/demo/30min, escolher amanhã 10:00, preencher o formulário, enviar | tela de confirmação, agendamento no dashboard do anfitrião, e-mail para os dois | e2e | |
| F01-E1 | | borda: horário ocupado enquanto preenche o formulário | | mensagem clara, escolher outro horário, sem agendamento duplicado | e2e | |
| F01-E2 | | borda: visitante em outro fuso horário | | horários mostrados no fuso do visitante, salvos em UTC | e2e | |
| F01-N1 | | negativo: cartão recusado | | erro exibido, nenhum agendamento criado | manual | |
