# Exploração

Começar pela inspeção de um vídeo SHOT com anotações sobrepostas; depois criar treinamento. Mover funções reutilizáveis para src/sensia. Limpar saídas grandes antes do commit.

## Primeiro treinamento no Colab

[01_treino_piloto_cnn.ipynb](01_treino_piloto_cnn.ipynb) é a primeira versão simples do treino: CNN própria de pares, respeitando os splits do pacote SHOT piloto v1.

1. Abrir o notebook no Google Colab e selecionar GPU se disponível.
2. Colocar o ZIP compartilhado no Drive e ajustar somente `ZIP_PATH` inicialmente.
3. Executar as células em ordem. A decodificação de vídeos pode demorar.
4. Conferir exemplos, curvas, matriz de confusão, recall/F1 e erros.
5. Executar a célula final para preservar resultados e o registro MLflow local no Drive.

O notebook verifica o SHA-256 do ZIP gerado pela Ana, não usa o teste oficial e não carrega pesos pré-treinados. Registra ambiente e configuração. O ambiente Colab é observado, sem presumir versões iguais às usadas no Windows. Para repetir um treino do zero, reconstruir a rede antes de executar fit.

Validação inicial do arquivo: estrutura nbformat e sintaxe verificadas; loader exercitado em MP4 sintético, incluindo RGB, ordem dos índices e seis canais. O treinamento TensorFlow, integração MLflow e resultados reais precisam ser executados no Colab; não há métricas preenchidas ou pesos treinados neste commit.
