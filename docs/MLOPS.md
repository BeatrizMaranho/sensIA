# MLOps mínimo desde o primeiro experimento

## Ferramentas e responsabilidades

Git/GitHub: código, configurações, manifestos pequenos, versões das regras e metadados das fontes. Dados e pesos: armazenamento externo autorizado ou fonte oficial. MLflow: execuções, métricas e artefatos. https://mlflow.org/docs/latest/ml/tracking/

Instalar `requirements.txt`; ao primeiro ambiente validado, salvar versões efetivas em um lock e usá-lo nas reproduções. Ainda não há ambiente validado de ponta a ponta.

Para servidor local com SQLite explícito (o banco é ignorado pelo Git):

```powershell
mlflow server --backend-store-uri sqlite:///mlflow.db --host 127.0.0.1 --port 5000
```

Nas futuras implementações, configurar o cliente para `http://127.0.0.1:5000`. Essa instância é local e não compartilhada automaticamente. A equipe deve definir host/armazenamento persistente antes de compartilhar um servidor. Não expor servidor publicamente sem autenticação.

## Registrar no treinamento

Commit, versão/hash do manifesto, splits por vídeo, semente, arquitetura, normalização, amostragem de negativos, hiperparâmetros, loss por época, precisão/recall/F1, tolerância temporal e pesos. Usar pareamento um-para-um entre eventos previstos e reais para não contar várias detecções do mesmo corte como vários acertos. Ajustar threshold e tolerância/protocolo na validação; reservar teste para avaliação final. Teste oficial do SHOT pode já ter sido usado no treino de modelos pré-treinados: verificar antes de alegar comparação independente.

## Registrar no agente

ID/hash do vídeo (não upload público do conteúdo), configuração da extração, versão do prompt e dos documentos, provedor/modelo, ferramentas e trechos recuperados, regra aplicada, resultado, latência e erros. Não registrar chaves ou conteúdo privado sem necessidade/consentimento.

## Avaliação do protótipo

Conjunto fixo de vídeos e perguntas, revisão humana de: números fiéis à ferramenta, citação existente, evidência que sustenta a interpretação, reconhecimento de ausência de evidência, falhas e tempo de execução. Registrar contagens e critérios; não confundir avaliação do agente com F1 do detector.

Não precisa instalar uma pilha de infraestrutura completa para a entrega inicial. DVC/remoto e registro de modelos podem entrar quando o acesso aos dados e o primeiro treinamento estiverem estáveis.
