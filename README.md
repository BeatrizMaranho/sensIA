# sensIA

Análise explicável de características visuais de vídeos, com recomendações de conteúdos semelhantes que apresentem menor intensidade nas dimensões medidas.

Projeto experimental da Residência em IA. 
Entrega final: **11/12/2026**.

## Estado atual

Esta versão organiza o trabalho: documentação, diretórios, configurações e inventário dos dados. **Ainda não implementa agente, API, interface ou rede treinada.**

## Duas frentes em paralelo

1. **Agente classificador/analista:** ferramentas de extração OpenCV, comparação com referência experimental e busca de evidências (RAG). Deve informar métricas, limitações e fonte/página. O protótipo não depende da rede; cortes indisponíveis devem ser `null`, nunca zero.
2. **Rede própria:** usar o SHOT para aprender detecção de transições entre planos. OpenCV decodifica frames; a rede detecta transições; funções calculam cortes/minuto e duração dos planos. Começar por cortes abruptos, após conferir a correspondência das anotações.

O recomendador vem depois: busca tema semelhante no catálogo e compara métricas previamente calculadas. SHOT treina o detector; não fornece classes de estímulo nem substitui o catálogo infantil.

## Comece aqui

- [Plano, divisão e critérios de entrega](docs/PLANO.md)
- [Download e compartilhamento dos dados](data/README.md)
- [Arquitetura e contrato entre frentes](docs/ARQUITETURA.md)
- [MLOps e avaliação](docs/MLOPS.md)
- [Metodologia do experimento da rede neural](docs/METODOLOGIA_REDE_NEURAL.md)
- [Como contribuir](CONTRIBUTING.md)

## Preparar ambiente

Recomendação inicial: Python 3.11. Os comandos abaixo criam o ambiente; não iniciam um agente.

```powershell
git clone https://github.com/BeatrizMaranho/sensIA.git
cd sensIA
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/inventory_data.py --help
```

No Linux/macOS, ative com `source .venv/bin/activate`. Copie `.env.example` para `.env` apenas quando configurar serviços. Nunca envie chaves ao Git.

## Pastas

| Caminho | Uso |
|---|---|
| `src/sensia/metrics/` | Extração das métricas |
| `src/sensia/agents/` | Agente analista e futuro recomendador |
| `src/sensia/rag/` | Ingestão, recuperação e referências |
| `src/sensia/models/` | Rede própria e adaptação de detectores |
| `src/sensia/api/` | API de integração |
| `app/` | Interface futura |
| `data/raw/shot/` | Vídeos e anotações locais, ignorados pelo Git |
| `data/raw/catalog/` | Vídeos do catálogo, ignorados pelo Git |
| `data/manifests/` | Inventários e divisões reproduzíveis, sem vídeos |
| `knowledge/` | Metadados das fontes e documentos locais |
| `configs/` | Configurações versionadas |
| `notebooks/` | Exploração e experimentos |
| `models/`, `reports/` | Artefatos locais; publicar resultados selecionados nos PRs/MLflow |

## Limites da interpretação

As métricas descrevem o conteúdo, não diagnosticam saúde, fadiga ou acessibilidade. Regras experimentais devem ter versão, escopo e justificativa. Não há limiar numérico ativado nesta estrutura. O RAG não transforma uma associação científica em limite universal. Separar cortes, mudanças semânticas de cena e movimento dentro do plano.

## Fontes iniciais

- [AutoShot / SHOT](https://github.com/wentaozhu/AutoShot): vídeos e anotações para detecção de planos; citar Zhu et al., CVPR Workshops 2023.
- [Kim e Ju (2024)](https://doi.org/10.1016/j.displa.2024.102861): movimento, brilho e avaliações humanas de fadiga em vídeos de jogos de direção; não fornece limiar de cortes nem de saturação.

Verificar com os mentores o requisito de atualidade do resource: AutoShot é de 2023. Não tratar sua idade como automaticamente compatível com a exigência de até dois anos.
