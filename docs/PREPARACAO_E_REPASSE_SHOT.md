# SHOT piloto v1 — preparação final e repasse para Ana e Luan

**Situação:** implementação pronta para execução local; treinamento ainda não executado. A versão é um piloto para aprender cortes abruptos, não uma reprodução integral do benchmark. A metodologia anterior permanece como histórico em [METODOLOGIA_REDE_NEURAL.md](METODOLOGIA_REDE_NEURAL.md).

## 1. Decisão sobre o teste oficial

Foi consultado o avaliador oficial [compare_inference_baseline_groundtruth_v2.py](https://github.com/wentaozhu/AutoShot/blob/77c82ff826a9301bb173d9be786297a49d73d081/compare_inference_baseline_groundtruth_v2.py), que carrega `gt_scenes_dict_baseline_v2.pickle` como anotações de teste. Foram obtidos 200 identificadores numéricos do arquivo por leitura estática dos opcodes de strings com [pickletools.genops](https://docs.python.org/3/library/pickletools.html#pickletools.genops), sem executar `pickle.load` ou os redutores. O SHA do blob foi conferido contra a árvore Git oficial.

A lista versionada está em `data/manifests/shot_reference/official_test_ids.csv`; `provenance.json` registra commit, caminho, hash SHA-256 e blob de origem. Ela serve para reservar a participação no teste: não contém as anotações do benchmark e não torna os vídeos automaticamente aptos à avaliação.

No subconjunto local de 100 vídeos, 27 pertencem a essa lista. Eles são reservados e nenhum par de treino/validação é gerado a partir deles. A primeira inspeção de `38667643656.mp4` e a revisão de `48422312550.mp4` ocorreram antes desse mapeamento; ambos pertencem à lista. Registrar essa exposição exploratória como limitação e não usá-los para ajustar hiperparâmetros. Não presumir que os demais vídeos estão formalmente no treino oficial: o split gerado se chama piloto fora do teste conhecido.

## 2. Política operacional do piloto

Escolhas da equipe, anteriores ao primeiro treinamento; não são limiares científicos de estímulo:

- Considerar apenas transições abruptas candidatas com `fim = inicio + 1`, cujos índices existem.
- Excluir temporariamente vídeos sem anotação, blocos duplicados, erros não terminais de anotação, duplicatas por hash/nome ou divergência entre contagens informada e decodificada.
- Excluir por inteiro vídeos com revisão de candidato incerta/desalinhada, nesta primeira versão. Isso inclui `48580643264.mp4`. `39672724739.mp4` já tinha formato de anotação a revisar e também apresentou um candidato incerto.
- Divergência do valor de cabeçalho, isoladamente, permanece como alerta e não causa exclusão. Os frames decodificados orientam os limites do arquivo. Não reescalar nem corrigir a fonte.
- O registro terminal `N-1,N` não gera um positivo, pois o segundo frame não existe. Isso não afirma a intenção original do anotador. A região final fica fora dos negativos pela margem de proteção.
- Os demais intervalos, inclusive graduais, criam regiões de proteção. Negativos só são amostrados quando **ambos** os frames estão fora dessas regiões.
- Margem inicial: cinco frames em torno dos intervalos. É uma heurística operacional configurável, não limiar validado e não duração uniforme em segundos (os FPS variam).
- Para cada positivo, amostrar até três negativos por vídeo, sem reposição. A proporção reduz volume no piloto; não representa a prevalência real e deve constar da avaliação.
- Separar aproximadamente 20% dos vídeos elegíveis para validação antes de gerar pares, com semente 42 e ordem inicial registrada pelo script. O agrupamento é por vídeo; arquivos idênticos com nomes diferentes são excluídos nesta versão. Duplicatas visuais/trechos derivados não são detectados automaticamente e exigem revisão posterior.

O script preserva os originais e cria dados derivados com política e hashes. Os rótulos positivos são candidatos provenientes da fonte, não validação visual exaustiva. Usar o piloto para demonstrar o pipeline e aprender; avaliar generalização depois, com protocolo fixado.

## 3. Organização prevista com os relatórios compartilhados

| Grupo | Vídeos | Uso |
|---|---:|---|
| Treino piloto | 43 | Ajustar pesos da rede |
| Validação piloto | 11 | Selecionar configurações/checkpoint |
| Teste oficial reservado | 27 | Não usado para treino nem seleção; preparar avaliação separadamente depois |
| Excluídos nesta versão | 19 | Preservados para revisão |

| Conjunto | Positivos candidatos | Negativos amostrados | Total de pares |
|---|---:|---:|---:|
| Treino | 331 | 993 | 1.324 |
| Validação | 85 | 255 | 340 |

Essas contagens foram calculadas a partir dos CSVs compartilhados, da revisão registrada e da política v1. A execução local deve confirmar hashes e gerar o resumo definitivo. Se divergir, investigar os insumos; não ajustar manualmente para forçar os números.

Os 54 vídeos selecionados somam 2.026.995.735 bytes no inventário (aproximadamente 2,03 GB decimais / 1,89 GiB), sem contar metadados do pacote. O ZIP é gerado sem recompressão: precisa desse espaço adicional, mas evita duplicar os vídeos em outra pasta e não exporta frames.

## 4. Comando da Ana: gerar manifestos e pacote para o Luan

Após obter esta branch pelo Git, execute na raiz do repositório, com a auditoria e a revisão já existentes:

```powershell
python scripts/prepare_shot_pilot.py --bundle data/processed/shot_pilot_v1.zip
```

O comando usa apenas a biblioteca padrão Python; não exige reinstalar OpenCV nem baixar outro ZIP. Verifica hashes dos arquivos de entrada e dos vídeos selecionados, reserva o teste e cria:

- `data/processed/shot_pilot_v1/videos.csv`: todos os 100 vídeos, seus splits e motivos de exclusão/revisão.
- `pairs.csv`: nome/caminho, `frame_a`, `frame_b`, rótulo 0/1 e split. São índices, não imagens exportadas. Os índices começam em zero, e `frame_b = frame_a + 1`.
- `summary.json`: política, configuração, contagens e hashes de proveniência.
- `data/processed/shot_pilot_v1.zip`: somente os 54 vídeos de treino/validação, metadados, anotações originais, relatórios de auditoria/revisão e referência de IDs oficiais.

O teste reservado e os vídeos excluídos **não** estão no ZIP; a classificação deles permanece no manifesto. A pasta `data/processed/` e arquivos ZIP são ignorados pelo Git. Não publicar o pacote no GitHub. Compartilhar pelo armazenamento institucional/Drive autorizado, respeitando os termos do dataset, e enviar ao Luan o SHA-256 do ZIP mostrado no terminal. Esta tarefa não cria uma pasta externa nem transfere dados a outra pessoa automaticamente.

Se não precisar de ZIP, executar sem `--bundle`. Saídas existentes não são sobrescritas. Para outra execução, definir uma nova pasta com `--output` e um novo ZIP; não alterar a versão entregue ao colega.

## 5. Comando do Luan: conferir e usar

Depois de obter o código e baixar o pacote:

```powershell
python scripts/prepare_shot_pilot.py --verify-bundle "CAMINHO_DO_ZIP_RECEBIDO"
```

Esse modo confere o CRC e o SHA-256 de cada arquivo declarado no pacote, sem extrair. Comparar também o SHA-256 do ZIP com o enviado pela Ana, por exemplo com `Get-FileHash -Algorithm SHA256`. Os hashes detectam divergências; não substituem conhecer a origem do pacote.

Após conferir, extrair para uma pasta local, por exemplo `data/raw/shot_pilot_v1/`. O ZIP contém `videos/`, `metadata/`, `source/`, `audit/`, `review/`, `reference/` e `bundle.json`.

O loader da rede deve ler `metadata/pairs.csv`, buscar cada `relative_path` dentro de `videos/` e carregar os índices declarados. `label=1` significa candidato a corte; `label=0` significa negativo amostrado. Respeitar o campo `split`; não executar uma segunda divisão aleatória por par. Carregar os frames sob demanda, evitando manter todos os vídeos na RAM. Redimensionamento, normalização, ordem de canais e arquitetura serão definidos no código de treino e registrados.

## 6. Divisão de responsabilidades

| Ana — dados e rastreabilidade | Luan — loader e primeiro modelo |
|---|---|
| Gerar versão v1 e conferir resumo | Conferir pacote e reproduzir contagens |
| Preservar originais, relatórios e pacote entregue | Implementar leitura de pares e transformação das imagens |
| Registrar política, limitações e decisões em docs | Construir CNN própria e verificar execução em batch pequeno |
| Organizar avaliação e análise de erros com Luan | Integrar treinamento e curvas ao MLflow |

Ambos revisam vazamento, distribuição de classes, configuração e resultados. Não gerar métricas fictícias ou afirmar validação independente dos rótulos. Escolher arquitetura/hiperparâmetros usando treino/validação, sem consumir o teste reservado nessa escolha.

## 7. Critério para encerrar a preparação

- [ ] Comando executado localmente e hashes aceitos.
- [ ] Resumo com splits/pares conferido e guardado.
- [ ] Pacote verificado e acesso compartilhado com Luan.
- [ ] Luan confirma mesmas contagens e aceita o contrato de entrada.

Ao concluir isso, a preparação do **piloto v1** pode ser considerada encerrada para o primeiro treino. Isso não encerra curadoria integral do SHOT, teste oficial completo ou generalização para vídeos infantis. O ambiente e a implementação do treinamento ainda precisam ser fixados; a divergência OpenCV reportada está documentada na metodologia.

## Referências técnicas

- AutoShot, repositório oficial e avaliador pinado no commit indicado: https://github.com/wentaozhu/AutoShot
- Python, inspeção estática pickletools: https://docs.python.org/3/library/pickletools.html
- Python, SHA-256: https://docs.python.org/3/library/hashlib.html
- Python, CSV: https://docs.python.org/3/library/csv.html
- Python, amostragem com semente: https://docs.python.org/3/library/random.html
- Python, pacote ZIP e verificação CRC: https://docs.python.org/3/library/zipfile.html
- MLOps e avaliação: [MLOPS.md](MLOPS.md). O comando gera evidências locais; envio ao MLflow será integrado ao treinamento.

Documentações sustentam as operações técnicas. Margem, razão de negativos, exclusões conservadoras e fração de validação são decisões operacionais explícitas do experimento, não regras prescritas pelas bibliotecas.
