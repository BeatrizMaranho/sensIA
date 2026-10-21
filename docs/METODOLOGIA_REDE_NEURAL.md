# Metodologia do experimento de detecção de cortes — sensIA

**Versão:** 0.1 — preparação anterior ao treinamento. **Data do registro:** 21/10/2026.

Este documento descreve os procedimentos realizados e as decisões metodológicas do experimento. Etapas futuras estão identificadas como planejadas. As evidências desta versão são os inventários, relatórios e montagens produzidos no computador da equipe e compartilhados para análise; não existem resultados de treinamento a relatar. A conclusão do experimento será acrescentada após execução e avaliação do modelo.

Resumo dos indicadores: [evidência estruturada da preparação](evidencias/preparacao_shot_2026-10-21.json). Esse resumo não substitui os relatórios locais originais.

## 1. Objetivo e delimitação

O objetivo é construir e testar uma rede neural própria para identificar cortes abruptos entre planos de um vídeo. Inicialmente, a tarefa será formulada como classificação supervisionada de pares de frames consecutivos: presença ou ausência de corte. Essa formulação é uma decisão experimental da equipe, e não uma reprodução da arquitetura AutoShot. A viabilidade da arquitetura e de seus parâmetros ainda será testada.

No sistema sensIA, as transições detectadas permitirão calcular frequência de cortes e duração dos planos. A rede não deverá editar o vídeo ou estimar diretamente saúde, bem-estar ou fadiga. Movimento dentro do plano, mudança semântica de cena e corte de edição são conceitos distintos. Transições graduais e efeitos ambíguos não serão automaticamente tratados como cortes abruptos ou como exemplos negativos.

Trata-se de uma pesquisa aplicada, com abordagem quantitativa e experimento supervisionado exploratório. A preparação inclui inspeção visual qualitativa dos rótulos. A comparação com um detector pré-treinado está prevista como referência futura, sem substituir a necessidade de construir e avaliar a solução própria. Nenhum desempenho superior ou capacidade de generalização foi demonstrado até esta versão.

## 2. Fonte dos dados e seleção do subconjunto

Foi escolhido o dataset SHOT, disponibilizado pelos autores do AutoShot para estudo de detecção de fronteiras entre planos. O repositório oficial descreve 853 vídeos curtos e 11.606 anotações de planos e fornece os links de acesso [1]. O dataset fornece supervisão para transições; não fornece rótulos de intensidade sensorial ou de saudabilidade.

A equipe baixou `video_download.zip` da pasta indicada pelos autores e o extraiu em `data/raw/shot/video_download/`. O tamanho de download informado pela equipe foi de aproximadamente 3,27 GB; esse valor não foi usado como medida do tamanho total do SHOT. O arquivo `kuaishou_v2.txt` foi obtido do repositório oficial para relacionar vídeos e anotações.

O recorte foi escolhido por viabilidade de download e inspeção, constituindo amostra de conveniência, e não amostragem representativa do dataset ou de conteúdos infantis. A presença de vídeos diversos e em outros idiomas é compatível com a investigação inicial de transições visuais. A transferência para vídeos infantis exigirá avaliação específica posterior.

Os originais permanecem fora do histórico Git. Código, configurações e manifestos pequenos são versionados. Esse arranjo não dispensa verificar condições de uso ou atribuição antes de compartilhar vídeos e montagens. O uso de dados e o uso de pesos pré-treinados são decisões distintas: nesta fase não houve uso de pesos AutoShot para treinar a rede própria.

## 3. Inventário e identificação dos arquivos

Foi executado `scripts/inventory_data.py`, registrando caminho relativo, tamanho e SHA-256. O inventário contém 101 arquivos, dos quais 100 são MP4; a contagem de arquivos também inclui `.DS_Store`, que não participa do experimento. O manifesto está em `data/manifests/shot_files.csv`.

O hash foi adotado para reconhecer a versão exata dos bytes de cada arquivo, detectar alterações entre etapas e permitir comparação de cópias pela equipe. SHA-256 está disponível no módulo oficial `hashlib` [2]. Hashes iguais não comprovam correção das anotações, representatividade ou validade científica dos dados.

## 4. Correspondência e leitura das anotações

A associação foi feita pelo nome do vídeo. Encontraram-se 93 nomes presentes nas anotações e sete sem correspondência no arquivo consultado. Os sete permanecem preservados, mas não são candidatos ao treinamento supervisionado inicial sem obter supervisão correspondente.

Uma conferência preliminar identificou apenas 44 correspondências porque exigia um número após `.mp4`. A inspeção do arquivo oficial mostrou cabeçalhos com e sem esse número. O reconhecimento foi corrigido antes de qualquer treinamento, resultando nas 93 correspondências. Essa revisão evitou interpretar uma limitação do parser como ausência de dados.

A auditoria passou a reconhecer pares separados por vírgula ou espaço e pares entre colchetes; linhas de formato desconhecido, nomes ou blocos duplicados foram sinalizados. Não foram adivinhadas correções de valores. A implementação usa `re` para reconhecimento dos padrões e `csv` para relatórios tabulares [3,4]. Esses módulos sustentam a implementação; os padrões aceitos e a política de revisão são decisões do projeto.

## 5. Inspeção inicial e auditoria estrutural

Foi aberto o vídeo `38667643656.mp4` e gerada uma montagem dos índices OpenCV 64, 65, 66 e 67. Observou-se mudança de uma cartela para pessoas em um restaurante entre os índices 65 e 66, coerente com a anotação `65,66`.

O OpenCV informou 630 frames, e a leitura sequencial também produziu 630 frames, indexados de 0 a 629. O cabeçalho da anotação traz 649 e inclui o intervalo `629,630`. A indexação zero foi adotada como hipótese diagnóstica apoiada nessa inspeção, sem afirmar sua validade global para todas as anotações.

Em seguida, executou-se `scripts/audit_shot.py`. A leitura dos vídeos empregou `VideoCapture`, `isOpened`, `get`, `read` e `release`. A documentação oficial descreve a captura/leitura e a decodificação do próximo frame [5]. A comparação entre contagem informada e efetivamente decodificada foi uma verificação adotada pela equipe; divergência não foi interpretada automaticamente como corrupção do arquivo.

### 5.1 Resultados da auditoria de preparação

| Indicador | Resultado observado |
|---|---:|
| Vídeos encontrados | 100 |
| Vídeos que abriram | 100 |
| Nomes com anotação correspondente | 93 |
| Nomes sem correspondência | 7 |
| Vídeos com pelo menos um motivo de revisão | 93 |
| Registros de intervalos examinados | 1.042 |
| Intervalos com status `within_bounds` | 954 |
| Intervalos com algum status de revisão | 88 |

O critério diagnóstico para limites foi `0 <= inicio < fim < frames_decodificados`. `within_bounds` significa conformidade estrutural com essa hipótese, não confirmação visual de um corte. As contagens incluem registros de blocos duplicados; portanto, não representam necessariamente eventos únicos.

Os 88 registros sinalizados distribuíram-se em 82 casos de ordem ou limites, três duplicatas, dois formatos não reconhecidos e um caso de ordem temporal não monotônica. Entre os 82 casos de ordem/limites, 73 são pares exatamente no formato `N-1,N`, sendo N a quantidade de frames decodificados. Esse padrão é compatível com uma possível convenção de encerramento, mas a intenção original permanece a confirmar. Tais pares não formam exemplos positivos válidos de duas imagens existentes; não serão truncados ou deslocados automaticamente.

Os motivos por vídeo se sobrepõem: 80 têm intervalos para revisão, 41 têm valor de cabeçalho diferente da contagem decodificada, sete não têm anotação, dois têm blocos duplicados e um tem divergência entre contagem informada e decodificada. Por isso, a soma dos motivos não deve ser usada como número de vídeos. Os alertas não equivalem a inutilização do conjunto.

Os vídeos `40924061188.mp4` e `48543247831.mp4` não apresentaram intervalos classificados dentro dos limites. Isso não permite rotulá-los como vídeos sem cortes. Em `49986240582.mp4`, foram informados 702 frames e decodificados 701, exigindo revisão específica.

## 6. Revisão visual exploratória

Foi executado `scripts/review_shot.py` com semente 42. A seleção foi feita com `random.Random(seed).sample`, após ordenação da lista elegível, preservando no manifesto os vídeos escolhidos [6]. A semente documenta a amostragem; não substitui preservar a lista selecionada e a versão do ambiente.

Foram elegíveis vídeos com uma anotação em bloco único, contagem informada consistente com a decodificada e pelo menos três candidatos abruptos dentro dos limites. O script verificou os hashes antes de usar os índices e leu os frames sequencialmente para compor as montagens. A seleção exclui certos problemas estruturais e, portanto, é exploratória e condicionada aos critérios de elegibilidade.

Em cada vídeo selecionado foram exibidos o primeiro, central e último candidato abrupto elegível, e não necessariamente todos os cortes. Cada linha mostra os índices `[inicio-1, inicio, fim, fim+1]`. Quando disponível, uma linha adicional apresenta o intervalo terminal; índices inexistentes recebem indicação de indisponibilidade, sem substituição por frames vizinhos.

### 6.1 Registro da revisão assistida

A avaliação das montagens foi feita por assistente de IA e registrada pela equipe em `review_assistant.csv`. Foram examinados 15 candidatos em cinco vídeos, além de quatro linhas terminais. Doze candidatos foram considerados aparentemente alinhados; três foram mantidos como incertos por efeitos ou necessidade de maior contexto temporal.

| Vídeo | Candidatos aparentemente alinhados | Candidatos incertos |
|---|---|---|
| `39672724739.mp4` | 51–52; 292–293 | 480–481 |
| `44940814236.mp4` | 44–45; 191–192; 368–369 | — |
| `48422312550.mp4` | 237–238; 580–581; 1016–1017 | — |
| `48580643264.mp4` | 378–379 | 312–313; 679–680 |
| `48827388116.mp4` | 64–65; 1004–1005; 1433–1434 | — |

Esses julgamentos não constituem validação humana independente nem medida de acurácia da rede. Os 12 casos não autorizam extrapolar alinhamento aos 954 intervalos. A revisão é evidência preliminar para formular a política de preparação; uma decisão final deve considerar os vídeos/sequências quando a montagem for insuficiente.

## 7. Decisões e pendências antes do treinamento

| Tema | Decisão ou situação nesta versão |
|---|---|
| Originais | Preservados; nenhuma correção sobrescreve a fonte |
| Rótulos | Ainda não foram gerados pares de treino |
| Intervalos terminais | Não usar como positivos de duas imagens; manter origem e motivo da exclusão |
| Erros/ambiguidade | Não corrigir por adivinhação nem converter automaticamente em negativos |
| Indexação | Hipótese zero apoiada em amostras; confirmar política operacional antes da geração |
| Transições graduais | Fora do alvo inicial; definir faixa de exclusão de negativos ao redor dessas regiões |
| Vídeos sem anotação | Fora do treino supervisionado inicial |
| Duplicatas | Resolver blocos/arquivos antes de contar eventos e dividir os dados |
| Cabeçalhos divergentes | Sinalizar e investigar; não reescalar índices automaticamente |
| Modelo próprio | Formulação proposta, arquitetura e framework ainda não implementados |

As exclusões precisam constar em um manifesto derivado e versionado, com justificativas e identificação da fonte. Preservar intervalos duvidosos em relatórios permite retornar à decisão, em vez de apagar evidências. As regras acima são propostas metodológicas da equipe; nenhuma documentação de biblioteca as valida como regra universal do SHOT.

## 8. Particionamento e prevenção de vazamento — a executar

A identidade dos vídeos do teste oficial do SHOT ainda não foi mapeada para o subconjunto local. Não foi criado um manifesto que comprove sua separação. Logo, a preservação operacional do teste oficial e a divisão treino/validação não podem ser declaradas concluídas.

Antes do treino, deverão ser identificados os IDs e a origem dos conjuntos oficiais, reservando os vídeos de teste. A validação será construída somente a partir dos vídeos oficiais de treino disponíveis e elegíveis. Se o recorte baixado não fornecer vídeos de treino suficientes, será necessário ampliar o download; não se deve reutilizar teste oficial como treino para manter a alegação de avaliação oficial.

A unidade de separação será o vídeo de origem, antes da extração dos pares, evitando compartilhar frames entre conjuntos. A documentação do scikit-learn descreve procedimentos de divisão que preservam grupos e fundamenta esse cuidado [7]; a biblioteca ainda não foi usada para realizar o split neste experimento. As proporções e contagens finais permanecem a definir conforme disponibilidade, distribuição e protocolo.

A inspeção exploratória dos dados antecedeu esse mapeamento. Após identificar os conjuntos, registrar se vídeos inspecionados pertencem ao teste e impedir que seus resultados sejam usados para ajustar regras específicas, arquitetura ou hiperparâmetros. A qualidade final será avaliada em dados não usados na seleção do modelo. Duplicatas e derivações do mesmo vídeo precisam permanecer no mesmo grupo.

## 9. Protocolo do primeiro experimento — planejado

O baseline proposto é uma CNN pequena construída pela equipe para classificar pares consecutivos de frames. Antes de executá-lo, deverão ser fixados: arquitetura/framework, resolução e normalização, política de cores, critério de positivos, distância de exclusão das regiões ambíguas, amostragem de negativos, semente, otimizador, taxa de aprendizado, batch size e quantidade máxima de épocas. Esses valores ainda não são resultados nem configurações efetivamente testadas.

Como cortes podem ser menos frequentes que pares sem corte, a distribuição de classes será medida. Eventual reamostragem ou ponderação será ajustada no treino. A avaliação deve distinguir a tarefa de classificação dos pares da detecção de eventos ao longo do vídeo. Para eventos, o protocolo deverá definir tolerância em frames e pareamento um-para-um, evitando contar detecções repetidas do mesmo evento como acertos distintos.

Precisão, recall e F1 serão reportados, acompanhados de loss de treino/validação, distribuição dos dados e análise de erros; acurácia isolada não será o critério de sucesso. Limiares de decisão e escolha de checkpoints serão ajustados na validação. O teste será utilizado após fixar essas escolhas. Não há valores de métricas, duração de treino ou conclusão a preencher antes da execução.

## 10. Rastreabilidade e MLOps

A rastreabilidade local já inclui hashes dos vídeos, anotações e scripts, commits, semente da amostra e relatórios. Os scripts preservam pastas de saída existentes, permitindo manter execuções distintas. Git registra versões do código; o uso de branches e PRs organiza revisão e integração [8]. Os resultados locais não devem ser presumidos como já anexados ao GitHub ou a um servidor MLflow.

A integração de treinamento com MLflow permanece planejada. O Tracking oferece registros de parâmetros, métricas e artefatos [9]. No primeiro treino deverão ser registrados: versão do código, hashes dos manifestos e splits, política dos rótulos, configuração, versões do ambiente, loss por época, métricas, checkpoint e relatórios. Não houve confirmação de uma execução real de treinamento ou de upload desses artefatos ao MLflow nesta etapa.

### 10.1 Identificadores já observados

| Evidência | Identificação |
|---|---|
| Auditoria | `2026-10-21T14:55:58.100998+00:00` |
| Commit da auditoria | `342148da596a926c273491338bca51ca06702bb1` |
| SHA-256 do script de auditoria | `382ab9e03464b55c7cb95fa2e9a481559145d4fcb9d8a07178480c83cc381de5` |
| SHA-256 das anotações | `7ca3fe97375a2c95fdcb510f647ba78371c184612ca03c8909a0cf38b91db873` |
| Geração das montagens | `2026-10-21T15:15:24.587627+00:00` |
| SHA-256 do script das montagens | `df2e08cdb3d1393c1779b41fe93ea0eeab16ae8a2bd5fbb1412850ffb5ec7a98` |
| SHA-256 do relatório de vídeos | `164980a2ec80fab63514011ca9576320b5e790affd29931be7a4bff161fe9003` |
| SHA-256 do relatório de intervalos | `3e8bb06457f3d6a676b455697086f551b5a2968fa2d482a591fc234aa01d65a2` |

O ambiente do Windows reportou `cv2.__version__ == 5.0.0`. O `requirements.txt` inicial especifica OpenCV menor que 5; existe, portanto, uma divergência de ambiente a resolver antes do treinamento. Essa informação não foi substituída por uma versão presumida. Registrar versão do Python, nome/versão da distribuição instalada, NumPy, backend de vídeo, sistema e hardware; depois fixar um ambiente efetivamente testado. A documentação OpenCV consultada na referência [5] é da série 4.x, e não comprova compatibilidade integral com o ambiente reportado.

## 11. Situação dos itens de trabalho

| Item | Status em 21/10/2026 |
|---|---|
| Baixar uma parte oficial e conferir vídeos/anotações | Concluído para aquisição e inspeção exploratória; qualidade dos rótulos ainda em preparação |
| Confirmar convenções de frames/transições | Parcial: amostras revisadas; bordas, efeitos e política global pendentes |
| Gerar inventário SHA-256 | Concluído |
| Identificar e preservar teste oficial por manifesto | Pendente |
| Criar validação por vídeo a partir do treino | Pendente |
| Primeiro treinamento próprio | Não executado |
| Registrar treinamento no MLflow | Não executado |

## 12. Limitações e espaço para conclusão posterior

O recorte é pequeno e de conveniência; a revisão visual cobre poucos candidatos e foi assistida por IA. Há ambiguidades de anotação, metadados divergentes, duplicatas e vídeos sem supervisão correspondente. A generalização para clipes infantis, transições graduais, outros formatos e efeitos de câmera não foi medida. A seleção exploratória não permite estimar desempenho populacional.

Após o treinamento, acrescentar: versão final dos dados, quantidade de vídeos/pares por conjunto, distribuição de classes, arquitetura e configuração efetivamente usadas, identificação da execução MLflow, curvas, métricas, exemplos de erros, comparação de referência e limitações observadas. A conclusão deve distinguir funcionamento do pipeline, desempenho no protocolo escolhido e utilidade no sensIA. Esta versão não antecipa aprovação ou eficácia do modelo.

## Referências

[1] ZHU, W. et al. **AutoShot: A Short Video Dataset and State-of-the-Art Shot Boundary Detection.** CVPR Workshops, 2023. Repositório oficial e acesso ao artigo/dados: https://github.com/wentaozhu/AutoShot . Anotações: https://github.com/wentaozhu/AutoShot/blob/main/kuaishou_v2.txt . Base para origem e finalidade dos dados; a rede proposta aqui é própria.

[2] PYTHON SOFTWARE FOUNDATION. **hashlib — Secure hashes and message digests.** https://docs.python.org/3/library/hashlib.html . Base técnica para o cálculo SHA-256.

[3] PYTHON SOFTWARE FOUNDATION. **re — Regular expression operations.** https://docs.python.org/3/library/re.html . Base técnica do reconhecimento de padrões.

[4] PYTHON SOFTWARE FOUNDATION. **csv — CSV File Reading and Writing.** https://docs.python.org/3/library/csv.html . Base técnica dos relatórios tabulares.

[5] OPENCV. **VideoCapture Class Reference.** https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html . Base técnica da leitura/decodificação. Referência de API da série 4.x; conferir ambiente reportado antes de fixar dependências.

[6] PYTHON SOFTWARE FOUNDATION. **random — Generate pseudo-random numbers.** https://docs.python.org/3/library/random.html . Base técnica da amostragem com semente.

[7] SCIKIT-LEARN DEVELOPERS. **Cross-validation: evaluating estimator performance — grouped data.** https://scikit-learn.org/stable/modules/cross_validation.html#cross-validation-iterators-for-grouped-data . Fundamentação do protocolo planejado de separação por grupo; uso ainda não executado.

[8] GIT. **git-merge Documentation.** https://git-scm.com/docs/git-merge . Referência técnica de integração de versões.

[9] MLFLOW. **MLflow Tracking.** https://mlflow.org/docs/latest/ml/tracking/ . Referência do registro planejado de experimentos; registro de treino ainda não executado.

Documentações consultadas em 21/10/2026. URLs de documentação atual podem mudar de versão; não são prova da versão instalada. Decisões e observações próprias estão explicitadas ao longo do texto e não são atribuídas aos autores dessas ferramentas.


## 13. Atualização v0.2 — preparo do piloto e repasse (21/10/2026)

As seções anteriores preservam o registro anterior ao mapeamento do teste. Nesta atualização, foram identificados 200 IDs no arquivo usado pelo avaliador oficial AutoShot como ground truth de teste. A procedência e os hashes estão em `data/manifests/shot_reference/`. Há 27 correspondências nos 100 vídeos locais; eles ficam reservados, sem geração de pares de treino/validação.

Foi implementado `scripts/prepare_shot_pilot.py`, com política conservadora documentada em [PREPARACAO_E_REPASSE_SHOT.md](PREPARACAO_E_REPASSE_SHOT.md). Aplicando a política aos relatórios compartilhados, o planejamento resulta em 43 vídeos de treino, 11 de validação, 27 reservados e 19 excluídos nesta versão. Os pares previstos são 331 positivos e 993 negativos no treino, 85 positivos e 255 negativos na validação. As contagens só serão consideradas entrega local efetiva após execução e verificação de hashes no computador da equipe.

A margem de cinco frames, a razão de até três negativos por positivo e a fração de validação de 20% são escolhas operacionais explícitas, não prescrições científicas. A revisão exploratória já incluiu exemplos de vídeos posteriormente identificados como teste; essa exposição é uma limitação a registrar. O piloto fora do teste conhecido não é apresentado como reprodução completa dos splits/benchmark oficiais. Os dados reservados ainda exigem preparação própria para avaliação.

A versão compartilhável inclui vídeos de treino/validação, pares por índice e proveniência, sem frames exportados. Ana prepara e confere o pacote; Luan confere os hashes e implementa loader/rede. A divisão por vídeo deve ser respeitada. A execução do treinamento, a fixação do ambiente e seu registro no MLflow permanecem pendentes. A preparação local será concluída quando o resumo e o pacote forem conferidos pela equipe.
