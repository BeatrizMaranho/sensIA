# Primeiro experimento da CNN de cortes — sensIA

Execução no Colab: 21/10/2026. Registro: 23/10/2026. Status: **referência inicial (baseline) concluída; revisão humana dos erros pendente**.

A CNN aprendeu a distinguir pares com e sem corte neste piloto. Na validação, identificou 64 dos 85 cortes anotados, deixou passar 21 e gerou cinco falsos alarmes. O resultado demonstra funcionamento do treinamento e desempenho no recorte avaliado. Ainda precisamos avaliar a detecção ao longo de vídeos completos.

## 1. Evidência e rastreabilidade

A análise utiliza as saídas do notebook executado `01_treino_piloto_cnn (1).ipynb`, compartilhado pela equipe. Não houve novo treinamento durante esta documentação. Os valores por época foram transcritos automaticamente dos logs exibidos, com o arredondamento desses logs; não substituem o `history.csv` original.

- [Resumo estruturado e hashes](evidencias/piloto_cnn_v1.json).
- [Métricas por época](evidencias/piloto_cnn_v1_epocas.csv).
- [Fila de revisão dos oito erros exibidos](evidencias/piloto_cnn_v1_revisao_erros.csv).
- Notebook de implementação: [01_treino_piloto_cnn.ipynb](../notebooks/01_treino_piloto_cnn.ipynb).
- Execução MLflow: `5d73096d74474a05a4be4ab64abb4bc0`.

O notebook informou a preservação de `resultados_20261021_193201_664979.zip` no Drive da equipe, com SHA-256 `3461ec90c3e2f2759de86e66ba01e194fcc738cf50ce49adb4b562de87e8dc20`. Esse ZIP não foi fornecido separadamente para conferência nesta análise. O resumo distingue o hash informado da verificação independente. O notebook executado original deve ser preservado pela equipe junto aos artefatos.

## 2. Como o pairs.csv entrou no treino

O CSV foi usado como um índice: indicou o arquivo de vídeo, dois índices consecutivos de frames, o rótulo e a divisão previamente definida. A rede recebeu as imagens carregadas a partir desses índices. O rótulo orientou o ajuste dos pesos no treino.

| Conjunto | Vídeos | Pares sem corte (0) | Pares com corte (1) | Total |
|---|---:|---:|---:|---:|
| Treino | 43 | 993 | 331 | 1.324 |
| Validação | 11 | 255 | 85 | 340 |

Os vídeos de validação são distintos dos vídeos de treino. Os 27 vídeos locais identificados como teste oficial permaneceram reservados, sem avaliação neste experimento. O pacote conferido no Colab tem SHA-256 `620c30271977cf8cf20ae1da981404d80db53735ae665c6513c99452f5c4be8c`.

Cada imagem foi redimensionada mantendo proporção e preenchida com bordas pretas até 96 × 96 pixels, convertida de BGR para RGB e concatenada à outra imagem do par. A entrada tem seis canais: três do frame A e três do B. Os arrays observados foram `(1324, 96, 96, 6)` e `(340, 96, 96, 6)`.

## 3. Configuração efetivamente executada

CNN própria com 26.129 parâmetros treináveis, sem pesos pré-treinados: três convoluções com 16, 32 e 64 filtros; dois MaxPooling; GlobalAveragePooling; camada densa com 32 unidades; Dropout de 0,3; saída sigmoid. A normalização de pixels é feita por divisão por 255 dentro do modelo.

Semente 42, Adam, taxa de aprendizado 0,001, binary cross-entropy, lotes de 32 e máximo de dez épocas. Não houve ponderação de classes. O limiar de classificação foi fixado em 0,5: scores maiores ou iguais a esse valor geram previsão de corte. Esse é um limiar operacional do classificador de cortes; não classifica intensidade sensorial ou saúde.

Ambiente exibido: Python 3.13.15, TensorFlow 2.21.0, OpenCV 4.14.0 e GPU detectada. As versões diferem do ambiente Windows usado na preparação. Para reprodução, preservar também `environment.json` e `requirements_observed.txt` exportados; este documento não presume versões que não foram exibidas.

## 4. Comportamento durante o aprendizado

Na primeira época, a acurácia da validação foi de 75%, mas o recall de cortes foi zero: prever apenas a classe majoritária já produz 75% de acurácia neste conjunto. Isso explica por que acurácia isolada não basta.

A partir da terceira época, o recall de cortes aumentou. Na quinta, chegou a aproximadamente 74,12%; na oitava, a 75,29%. A loss de treino caiu de 0,5919 para 0,2120 ao longo das dez épocas. A menor loss de validação foi 0,3176 na época oito.

O callback `EarlyStopping` foi configurado com `monitor="val_loss"`, `patience=3` e `restore_best_weights=True`. As dez épocas foram concluídas: não houve parada antecipada. Ao final, os pesos associados à menor loss de validação foram restaurados, conforme a configuração e o comportamento documentado do callback [1]. Os resultados finais são consistentes com a época oito, e não com a última linha do log.

Depois das primeiras melhorias, a loss de validação oscilou enquanto a de treino continuou caindo. Isso sugere saturação do ganho e possível início de sobreajuste; uma única execução pequena não estabelece sua gravidade ou causa. A revisão dos erros vem antes da decisão de aumentar a arquitetura ou prolongar o treino.

## 5. Resultado final na validação

Métricas recalculadas a partir da matriz exibida. Precisão, recall e F1 abaixo se referem à classe **corte**; suas definições seguem a documentação scikit-learn [2].

| Modelo | Acurácia | Precisão de cortes | Recall de cortes | F1 de cortes |
|---|---:|---:|---:|---:|
| Sempre prever sem corte | 75,00% | 0,00% | 0,00% | 0,00% |
| CNN própria | 92,35% | 92,75% | 75,29% | 83,12% |

| Rótulo de referência | Previu sem corte | Previu corte |
|---|---:|---:|
| Sem corte | 250 | 5 |
| Corte | 21 | 64 |

A rede acertou 314 dos 340 pares. Das 69 previsões de corte, 64 corresponderam a cortes anotados. Dos 85 cortes anotados, encontrou 64. Portanto, neste protocolo, deixar passar cortes foi mais frequente que gerar falsos alarmes.

## 6. Análise exploratória dos erros

O notebook exibiu os quatro primeiros falsos positivos e os quatro primeiros falsos negativos na ordem do CSV. Eles não são amostra aleatória nem representam todos os 26 erros.

A inspeção assistida das imagens levantou três hipóteses para investigação:

1. **Movimento versus corte:** exemplos de gameplay classificados como corte podem envolver mudança de câmera ou conteúdo local dentro de um plano.
2. **Mudança em região pequena:** dois cortes não detectados em um desenho apresentam cabeçalho e rodapé estáticos. A região fixa pode reduzir a evidência global da transição.
3. **Anotação/contexto:** alguns pares parecem visualmente muito diferentes apesar de rótulo negativo, ou muito semelhantes apesar de rótulo positivo. É necessário assistir à sequência e consultar a anotação original antes de concluir que existe erro de rótulo.

Essas hipóteses não demonstram quais características internas a CNN utilizou. Os scores mostrados nas figuras são arredondados; um score exibido como 1,00 não comprova certeza nem calibração do modelo.

A fila em CSV mantém os rótulos originais e `human_decision=pending`. Para revisá-la, Ana e Luan devem abrir o vídeo com contexto antes e depois do par e registrar: decisão (`confirmed`, `annotation_issue` ou `uncertain`), nome do revisor e justificativa. Nenhum rótulo foi alterado nesta análise. Se uma revisão justificar alteração, criar nova versão do conjunto e conservar a comparação com a versão original; não sobrescrever silenciosamente a validação após ver os erros.

## 7. MLOps e limites do resultado

O notebook implementa registro de parâmetros, ambiente, métricas por época e artefatos em uma execução MLflow, abordagem alinhada ao Tracking [3]. As saídas mostram o identificador da execução e o caminho do pacote exportado. Isso não equivale a publicar um servidor compartilhado ou registrar o modelo no Model Registry. O banco local arquivado pode conter caminhos absolutos do Colab; sua restauração em outro ambiente requer conferir esses caminhos.

As métricas são de pares amostrados de 11 vídeos de validação, usados também para selecionar o checkpoint. Os 340 pares não equivalem a 340 vídeos independentes. Negativos foram amostrados longe das regiões anotadas e na proporção artificial de três para um; o resultado não estima diretamente a taxa de falsos alarmes em todos os frames de vídeos reais.

Não foram medidos: detecção de eventos em vídeo completo, transições graduais, generalização para conteúdos infantis, desempenho no teste oficial ou classificação de estímulo visual. A revisão exploratória de dados foi assistida por IA e não valida todos os rótulos. A exposição inicial a algumas amostras depois identificadas como teste permanece documentada na metodologia.

## 8. Próxima decisão experimental

Preservar esta execução como baseline. Primeiro, revisar os exemplos da fila com contexto temporal; depois, calcular métricas por vídeo e examinar todos os erros a partir de `predicoes_validacao.csv`. Esse arquivo completo permanece no pacote de resultados e ainda precisa ser fornecido para essa etapa da análise.

Em seguida, executar o modelo salvo sobre sequências completas dos vídeos de validação, estabelecendo antes o protocolo de contagem de eventos e tolerância de correspondência. Só então escolher um próximo experimento controlado, alterando uma variável por vez e mantendo registro no MLflow. O teste reservado deve continuar fora dos ajustes.

**Conclusão do piloto:** a preparação e o carregamento permitiram treinar uma CNN própria e obter desempenho superior à referência majoritária no protocolo de pares. O recall de cortes e os erros observados orientam a próxima investigação. A integração como detector de ritmo no sensIA depende de avaliação temporal adicional.

## Referências técnicas

[1] KERAS. [EarlyStopping](https://keras.io/api/callbacks/early_stopping/). Base para monitoramento e restauração de pesos.

[2] SCIKIT-LEARN. [precision_recall_fscore_support](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_fscore_support.html). Base para interpretação de precisão, recall e F1.

[3] MLFLOW. [MLflow Tracking](https://mlflow.org/docs/latest/ml/tracking/). Base para registro de parâmetros, métricas e artefatos.

Referências consultadas em 23/10/2026. As documentações explicam as ferramentas; configuração, resultados, hipóteses e decisões experimentais pertencem ao projeto.
