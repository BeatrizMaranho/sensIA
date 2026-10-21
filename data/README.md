# Dados: baixar fora do Git e usar localmente

## SHOT oficial

- Repositório e instruções: https://github.com/wentaozhu/AutoShot
- Google Drive indicado pelos autores: https://drive.google.com/drive/folders/1xZN6tvefXXmpZlIZ6GoSUUxpDQQOSNfJ?usp=sharing
- Anotações/listagem: https://github.com/wentaozhu/AutoShot/blob/main/kuaishou_v2.txt

São 853 vídeos e 11.606 anotações de planos; não são classes de estímulo. O tamanho total dos arquivos **ainda não foi aferido pela equipe**. Conferir tamanho e espaço livre na fonte antes de baixar. Começar com um arquivo/parte para inspeção, não com todos os frames exportados.

## Organização local

1. Baixar arquivos da fonte oficial e extrair em `data/raw/shot/`, preservando os originais e os nomes.
2. Identificar anotações por vídeo. Conferir no artigo/suplemento se o índice começa em 0 ou 1 e como transições são representadas antes de gerar rótulos.
3. Se seguir o avaliador oficial, mesclar `ads_game_videos_2` com `ads_game_videos` e as partes `video_download*` em `video_download`, conforme o README original. Antes de mesclar, verificar colisões de nomes e preservar cópia dos originais.
4. Inventariar os arquivos (pode demorar: lê todos os bytes para SHA-256):

```powershell
python scripts/inventory_data.py --root data/raw/shot --output data/manifests/shot_files.csv
```

5. Conferir e versionar o CSV pequeno. O inventário não produz rótulos nem splits automaticamente.
6. Registrar os splits em `data/manifests/shot_splits.csv` a partir do exemplo. Preservar o teste oficial; criar validação apenas no treino. Nunca dividir frames do mesmo vídeo entre conjuntos.

## Compartilhar com os colegas

**Opção inicial recomendada:** todos baixam da mesma pasta oficial e comparam inventários/hashes; o GitHub guarda instruções e manifestos. Não é necessário duplicar o dataset no Drive da equipe.

Se precisarem de subconjunto fixo ou derivados, usar pasta compartilhada institucional/Drive da equipe, com acesso autorizado e versão imutável (`shot-subset-v1`). Registrar URL, critérios e hashes no manifesto. Não publicar novamente dados sem verificar os termos. Nenhuma pasta externa foi criada por este scaffold.

Evolução MLOps: DVC com armazenamento remoto aprovado pela equipe para versionar dados/artefatos. Não foi configurado um remoto ou autenticação nesta etapa.

## Por que não subir os vídeos aqui?

GitHub bloqueia arquivos acima de 100 MiB no Git comum; upload via navegador limita arquivos a 25 MiB. Muitos arquivos menores também tornam clones e histórico pesados. https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github

O `.gitignore` protege vídeos, compactados e dados locais. Ele não impede criação de arquivos no seu computador: as pastas existem em cada clone, mas seu conteúdo não é enviado. Git LFS tem limites/cotas; não é nossa opção inicial para o SHOT.

## Catálogo infantil

Usar `data/raw/catalog/` para arquivos autorizados. Registrar origem, licença, tema, idioma e escopo (trecho ou vídeo completo) em `data/manifests/catalog.csv`. Precisamos de variedade de ritmo/movimento, não apenas vídeos presumidos como intensos. Métricas do trecho não representam automaticamente o filme inteiro.
