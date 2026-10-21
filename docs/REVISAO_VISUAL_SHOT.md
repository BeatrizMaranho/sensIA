# Revisão visual do SHOT: próximo passo após auditoria

Com `reports/shot_audit_v1/videos.csv` e `intervals.csv` originais disponíveis:

```powershell
python scripts/review_shot.py
```

A saída `reports/shot_visual_v1/` terá até cinco JPGs, `review.csv` e `manifest.json`. Pode levar alguns minutos; o script verifica hashes dos vídeos antes de usar a auditoria. Não repete a auditoria inteira. Diretório existente é preservado; use `--output reports/shot_visual_v2` para outra execução.

Amostra fixa com seed 42: vídeos com leitura de contagem consistente, um bloco de anotação e pelo menos três candidatos abruptos dentro dos limites. Em cada vídeo: primeiro, central e último candidato abrupto (não necessariamente o primeiro/último corte real do vídeo). Se houver intervalo terminal N-1,N, acrescenta uma linha de revisão; os índices inexistentes aparecem como `FRAME UNAVAILABLE`, nunca são substituídos por frames vizinhos.

Cada linha mostra [início-1, início, fim, fim+1]. Comparar as duas imagens centrais:

- Há mudança de plano entre elas? Registrar `aligned` em `decision` se confirmada.
- Não há? Registrar `misaligned` e explicar em `notes`.
- Há dúvida, falha de leitura ou transição não abrupta? Registrar `uncertain`.
- Linha `terminal_review`: manter `uncertain` até esclarecer a convenção original. Não confirma erro nem encerramento apenas pela imagem; não existe frame N em um vídeo de N frames indexados de zero.

Preencher `reviewer` e `notes`. Não marcar como alinhado apenas por terem cores diferentes; buscar continuidade/ruptura de plano. Não preencher automaticamente resultados pela saída do detector que pretendemos avaliar.

Este é um diagnóstico exploratório. Não extrapolar cinco vídeos para validação de todos os rótulos, nem escolher hiperparâmetros pelo conjunto de teste. Transições graduais, casos com erros estruturais, duplicatas e demais divergências exigem política própria. Após essa revisão, documentar política de bordas, casos ambíguos e construção de rótulos antes dos splits/treino. Nunca transformar anotações descartadas em negativos por padrão.

Guardar os CSVs e o manifesto para rastreabilidade; podem ser anexados a uma execução do MLflow. O script não envia automaticamente ao servidor. As montagens de dados de terceiros permanecem locais e fora do Git; verificar termos antes de redistribuir.
