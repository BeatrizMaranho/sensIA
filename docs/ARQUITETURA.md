# Arquitetura e contrato v0.1

## Integração planejada

Interface -> API -> agente analista -> ferramentas de extração e consulta RAG -> relatório. O extrator chama o detector de cortes por uma interface substituível. No início, detector indisponível; depois rede própria e, para comparação/fallback documentado, AutoShot. Não existe API implementada ainda.

Separar extração determinística, decisão experimental e explicação do LLM. O agente não calcula fluxo óptico por texto. O RAG recupera evidência e limites; não inventa um ponto de corte. Detecção de cortes não é classificação de fadiga.

## Contrato inicial

Consultar `configs/analysis.example.json`: é um EXEMPLO FICTÍCIO para desenvolver a integração, nunca resultado experimental.

- `schema_version`: versão do contrato.
- `video_id`, `duration_s`: identificador e duração real.
- `processing`: resolução de análise, intervalo entre frames, algoritmo e unidade de movimento. Normalização adicional deve ser explícita.
- `metrics`: médias de movimento, S e V em escala OpenCV 8 bits; proporção vibrante em [0,1], cujo critério deve ser definido. Movimento é calculado entre frames, S/V por frame.
- `shots.status`: `unavailable` ou `available`. Sem detector, contagem e durações são `null`.
- `classification.status`: `not_configured` até existir regra aprovada/versionada; não confundir corte de decisão da rede com limiar experimental de ritmo.
- `evidence`: trechos realmente recuperados, fonte e página; vazio até consulta real.

Para movimento contínuo, evitar contabilizar descontinuidades de edição como fluxo dentro do plano quando o detector estiver disponível. Reportar duração média E mediana dos planos e cortes/minuto. A média global sozinha esconde picos.

## Ferramentas previstas

`extract_metrics(video)` -> contrato de métricas; `compare_reference(metrics, config)` -> comparação reproduzível quando referência configurada; `retrieve_evidence(query)` -> fontes/trechos/páginas. Agente deve tratar erros e ausência de evidência. Definir provedor do LLM/API antes da implementação.

## Recomendador (etapa seguinte)

Buscar candidatos por tema/sinopse, comparar métricas calculadas no mesmo protocolo e apresentar diferenças por dimensão. Sem candidato melhor, informar isso. Não inferir menor movimento só por haver planos longos. Sem catálogo processado, não inventar títulos ou métricas.
