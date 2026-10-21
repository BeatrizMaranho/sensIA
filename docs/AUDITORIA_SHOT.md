# Auditoria do subconjunto SHOT

A primeira montagem enviada pela equipe mostrou a troca entre os índices OpenCV 65 e 66 do vídeo `38667643656.mp4`. A leitura sequencial encontrou 630 frames (0 a 629); o cabeçalho de anotação traz 649 e o intervalo final 629,630 exige revisão. Isso não permite concluir que as demais marcações estão alinhadas ou que o cabeçalho é uma contagem confiável.

Execute no diretório do projeto, com OpenCV instalado:

```powershell
python scripts/audit_shot.py
```

O script lê e decodifica todos os MP4s e calcula hashes; pode levar vários minutos. Não extrai imagens, altera originais, corrige índices, treina modelos ou divide os dados.

Saída padrão: `reports/shot_audit_v1/` (fora do Git). Uma pasta existente é preservada; para repetir, use `--output reports/shot_audit_v2`.

- `videos.csv`: frames informados/decodificados, FPS, hash, correspondência e motivos de revisão.
- `intervals.csv`: linha original e status dos intervalos; cabeçalhos sem número e pares com vírgula, espaço ou colchetes são reconhecidos. Formatos desconhecidos não são corrigidos por adivinhação. Blocos/nomes duplicados são sinalizados.
- `summary.json`: totais, versão do OpenCV, hash do script/anotações e commit (quando disponível), para rastreabilidade.

O parser espera cabeçalhos numéricos `.mp4` com contagem opcional. Cabeçalho desconhecido com `.mp4` interrompe o bloco anterior; arquivos afetados devem ser revisados pela correspondência/contagem e pela fonte original.

`within_bounds` significa apenas que `0 <= inicio < fim < frames_decodificados`, uma hipótese diagnóstica de indexação zero baseada na primeira montagem. Não é validação semântica do rótulo; valores que diferem do cabeçalho são sinalizados, não descartados. Nenhum vídeo é automaticamente liberado para treino (`training_ready=False`). Falha de leitura pode refletir arquivo/codec; não interpretar automaticamente como corrupção.

Próximo passo após o relatório: revisar amostras no início/meio/fim de vários vídeos, esclarecer bordas e possíveis sentinelas de fim, documentar decisões e gerar versão derivada aprovada. Intervalos rejeitados não devem virar exemplos negativos nem deve haver amostragem perto de regiões ambíguas. Preservar teste oficial e dividir por vídeo de origem só depois de conferir os IDs correspondentes.

Para MLflow, os relatórios podem ser registrados como artefatos em uma execução de preparação dos dados; esta versão gera rastreabilidade local, mas ainda não envia ao servidor automaticamente. Não publicar caminhos/arquivos privados sem revisão.
