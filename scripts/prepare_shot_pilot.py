"""Prepara pares/manifestos e pacote opcional do piloto SHOT, sem treinar ou alterar originais."""
import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import random
import subprocess
import zipfile


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fields):
    with path.open('x', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def classify(v, rows, test_ids, uncertain_names, duplicate_hashes):
    reasons = []
    n = int(v['decoded_frames'])
    if v['opened'] != 'True' or n < 2 or v['reported_frames'] != v['decoded_frames']:
        reasons.append('video_read_review')
    if int(v['annotation_blocks']) != 1:
        reasons.append('annotation_missing_or_duplicated')
    if 'duplicate_video_name' in v['review_reasons'] or v['sha256'] in duplicate_hashes:
        reasons.append('duplicate_video')
    if v['video_name'] in uncertain_names:
        reasons.append('visual_review_uncertain_or_misaligned')
    for r in rows:
        terminal = bool(r['start']) and int(r['start']) == n-1 and int(r['end']) == n
        if r['status'] != 'within_bounds' and not terminal:
            reasons.append('nonterminal_annotation_review')
    abrupt = [r for r in rows if r['status'] == 'within_bounds'
              and int(r['end']) == int(r['start']) + 1]
    if not abrupt:
        reasons.append('no_eligible_abrupt_candidates')
    if v['video_name'] in test_ids:
        return 'official_test_reserved', sorted(set(reasons))
    return ('excluded' if reasons else 'pilot_candidate'), sorted(set(reasons))


def make_pairs(v, rows, split, rng, margin, ratio):
    n = int(v['decoded_frames'])
    positives, masks = set(), []
    for r in rows:
        if not r['start'] or not r['end']:
            continue
        a, b = int(r['start']), int(r['end'])
        # Guardas afetam apenas a amostragem negativa; anotacoes nao sao corrigidas.
        masks.append((max(0, a-margin), min(n-1, b+margin)))
        if r['status'] == 'within_bounds' and b == a+1:
            positives.add(b)
    negative_pool = [t for t in range(1, n)
                     if t not in positives and all(t-1 > b or t < a for a, b in masks)]
    negatives = rng.sample(negative_pool, min(len(negative_pool), ratio*len(positives)))
    result = [{'video_name':v['video_name'], 'relative_path':v['relative_path'],
               'frame_a':t-1, 'frame_b':t, 'label':label, 'split':split}
              for label, ts in [(1, sorted(positives)), (0, sorted(negatives))] for t in ts]
    return result


def verify_bundle(path):
    """Verifica CRC e hashes dos videos que o pacote declara conter."""
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:
            raise ValueError('Falha de CRC no ZIP.')
        info = json.loads(z.read('bundle.json'))
        for item in info['files']:
            h = hashlib.sha256()
            with z.open(item['archive_path']) as f:
                for chunk in iter(lambda:f.read(1024*1024),b''):
                    h.update(chunk)
            if h.hexdigest() != item['sha256']:
                raise ValueError('Hash divergente: '+item['archive_path'])
    print('Pacote verificado: CRC e hashes de todos os arquivos declarados.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--videos', type=Path, default=Path('data/raw/shot/video_download'))
    p.add_argument('--audit', type=Path, default=Path('reports/shot_audit_v1'))
    p.add_argument('--review', type=Path, default=Path('reports/shot_visual_v1/review_assistant.csv'))
    p.add_argument('--annotations', type=Path, default=Path('data/raw/shot/kuaishou_v2.txt'))
    p.add_argument('--reference', type=Path, default=Path('data/manifests/shot_reference'))
    p.add_argument('--output', type=Path, default=Path('data/processed/shot_pilot_v1'))
    p.add_argument('--seed', type=int, default=42)
    p.add_argument('--validation-fraction', type=float, default=0.2)
    p.add_argument('--negative-ratio', type=int, default=3)
    p.add_argument('--guard-frames', type=int, default=5)
    p.add_argument('--bundle', type=Path, help='ZIP opcional com metadados e somente videos de treino/validacao.')
    p.add_argument('--verify-bundle', type=Path, help='Somente verificar um ZIP recebido, sem extrair.')
    args = p.parse_args()
    if args.verify_bundle:
        verify_bundle(args.verify_bundle)
        return
    if not 0 < args.validation_fraction < 1 or args.negative_ratio < 1 or args.guard_frames < 1:
        p.error('Confira fracao, proporcao negativa e margem.')
    required = [args.audit/'videos.csv', args.audit/'intervals.csv', args.audit/'summary.json',
                args.review, args.review.parent/'manifest.json', args.annotations,
                args.reference/'official_test_ids.csv', args.reference/'provenance.json']
    if not args.videos.is_dir() or any(not x.is_file() for x in required):
        p.error('Faltam videos ou arquivos de auditoria/revisao/referencia. Consulte docs/PREPARACAO_E_REPASSE_SHOT.md.')
    if args.output.exists() or (args.bundle and args.bundle.exists()):
        p.error('Saida ja existe. Preserve a versao anterior e escolha outro caminho.')
    if args.bundle and args.output.resolve() in args.bundle.resolve().parents:
        p.error('O ZIP deve ficar fora da pasta de metadados de saida.')
    audit_summary = json.loads((args.audit/'summary.json').read_text(encoding='utf-8-sig'))
    review_manifest = json.loads((args.review.parent/'manifest.json').read_text(encoding='utf-8-sig'))
    provenance = json.loads((args.reference/'provenance.json').read_text())
    if sha(args.annotations) != audit_summary['annotation_sha256']:
        p.error('As anotacoes mudaram desde a auditoria.')
    for name in ['videos.csv', 'intervals.csv']:
        if sha(args.audit/name) != review_manifest['audit_hashes'][name]:
            p.error('A revisao visual e a auditoria nao correspondem: '+name)
    if sha(args.reference/'official_test_ids.csv') != provenance['ids_csv_sha256']:
        p.error('Lista de teste oficial modificada sem atualizar proveniencia.')
    test_ids = {r['video_name'] for r in read_csv(args.reference/'official_test_ids.csv')}
    if len(test_ids) != provenance['ids_count']:
        p.error('Contagem de IDs oficiais inconsistente.')
    videos = read_csv(args.audit/'videos.csv')
    intervals = read_csv(args.audit/'intervals.csv')
    review = read_csv(args.review)
    if not review or any(r['decision'] not in {'aligned','uncertain','misaligned'} for r in review):
        p.error('A revisao deve estar registrada: aligned, uncertain ou misaligned.')
    names = [v['video_name'] for v in videos]
    if len(names) != len(set(names)):
        p.error('Auditoria contem nomes duplicados; resolver antes do piloto.')
    uncertain = {r['video_name'] for r in review if r['kind']=='candidate' and r['decision']!='aligned'}
    grouped = defaultdict(list)
    for r in intervals:
        grouped[r['video_name']].append(r)
    hashes = Counter(v['sha256'] for v in videos)
    duplicate_hashes = {h for h, count in hashes.items() if count > 1}
    records = []
    for v in videos:
        status, reasons = classify(v, grouped[v['video_name']], test_ids, uncertain, duplicate_hashes)
        record = {**v, 'split':status, 'exclusion_or_review_reasons':';'.join(reasons)}
        record['source_audit_training_ready'] = record.pop('training_ready', 'unknown')
        records.append(record)
    eligible = sorted([r for r in records if r['split']=='pilot_candidate'],key=lambda r:r['video_name'])
    if len(eligible) < 2:
        p.error('Menos de dois candidatos elegiveis fora do teste oficial.')
    rng = random.Random(args.seed)
    rng.shuffle(eligible)
    n_val = min(len(eligible)-1, max(1, math.ceil(len(eligible)*args.validation_fraction)))
    val_names = {v['video_name'] for v in eligible[:n_val]}
    for r in records:
        if r['split']=='pilot_candidate':
            r['split']='validation' if r['video_name'] in val_names else 'train'
    pairs = []
    selected = [r for r in records if r['split'] in {'train','validation'}]
    for i,v in enumerate(selected,1):
        relative = Path(v['relative_path'])
        path = args.videos/relative
        if relative.is_absolute() or '..' in relative.parts or not path.is_file():
            p.error('Caminho de video invalido: '+str(relative))
        print(f"[{i}/{len(selected)}] Verificando {v['video_name']}",flush=True)
        if sha(path) != v['sha256']:
            p.error('Video mudou desde a auditoria: '+v['video_name'])
        pairs.extend(make_pairs(v, grouped[v['video_name']], v['split'], rng,
                                args.guard_frames,args.negative_ratio))
    if any(r['video_name'] in test_ids for r in pairs):
        raise RuntimeError('Vazamento: video reservado em pares de treino/validacao.')
    for split in ['train','validation']:
        if {r['label'] for r in pairs if r['split']==split} != {0,1}:
            p.error('Cada conjunto precisa conter positivos e negativos: '+split)
    for record in records:
        record['pilot_pairs_ready'] = record['split'] in {'train','validation'}
    args.output.mkdir(parents=True,exist_ok=False)
    write_csv(args.output/'videos.csv',records,list(records[0]))
    write_csv(args.output/'pairs.csv',pairs,['video_name','relative_path','frame_a','frame_b','label','split'])
    split_counts = dict(Counter(r['split'] for r in records))
    pair_counts = dict(Counter(f"{r['split']}_label_{r['label']}" for r in pairs))
    config = {'dataset_version':args.output.name,'seed':args.seed,'validation_fraction':args.validation_fraction,
              'negative_ratio':args.negative_ratio,'guard_frames':args.guard_frames,
              'indexing':'zero_based','target':'abrupt_cut_between_frame_a_and_frame_b',
              'policy':'Exclude nonterminal annotation errors, inconsistent reads, duplicate blocks/hash and visually uncertain candidate videos; reserve official test; gradual intervals and all transitions guard negatives.',
              'video_counts':split_counts,'pair_counts':pair_counts,'training_executed':False,
              'official_benchmark_reproduction':False,'inputs_sha256':{str(x):sha(x) for x in required},
              'official_reference':provenance,'script_sha256':sha(Path(__file__)),
              'created_at_utc':datetime.now(timezone.utc).isoformat(),
              'note':'Rotulos candidatos da fonte, nao validacao visual exaustiva. Teste reservado nao foi preparado para avaliacao.'}
    try:
        config['git_commit']=subprocess.check_output(['git','rev-parse','HEAD'],text=True,stderr=subprocess.DEVNULL).strip()
    except (OSError,subprocess.CalledProcessError):
        config['git_commit']=None
    (args.output/'summary.json').write_text(json.dumps(config,indent=2),encoding='utf-8')
    if args.bundle:
        args.bundle.parent.mkdir(parents=True,exist_ok=True)
        manifest=[]
        with zipfile.ZipFile(args.bundle,'x',compression=zipfile.ZIP_STORED,allowZip64=True) as z:
            for f in sorted(args.output.iterdir()):
                arc='metadata/'+f.name;z.write(f,arc);manifest.append({'archive_path':arc,'sha256':sha(f)})
            for v in selected:
                f=args.videos/v['relative_path'];arc='videos/'+Path(v['relative_path']).as_posix()
                z.write(f,arc);manifest.append({'archive_path':arc,'sha256':v['sha256']})
            for folder, paths in [
                ('audit', [args.audit/n for n in ['videos.csv','intervals.csv','summary.json']]),
                ('review', [args.review, args.review.parent/'manifest.json']),
                ('reference', [args.reference/'official_test_ids.csv', args.reference/'provenance.json'])]:
                for f in paths:
                    arc=folder+'/'+f.name
                    z.write(f,arc);manifest.append({'archive_path':arc,'sha256':sha(f)})
            z.write(args.annotations,'source/kuaishou_v2.txt')
            manifest.append({'archive_path':'source/kuaishou_v2.txt','sha256':sha(args.annotations)})
            z.writestr('bundle.json',json.dumps({'files':manifest,'video_scope':'train_and_validation_only'},indent=2))
        print('ZIP:',args.bundle.resolve())
        print('ZIP SHA-256:',sha(args.bundle))
    print(json.dumps({'video_counts':split_counts,'pair_counts':pair_counts},indent=2))
    print('Metadados:',args.output.resolve())
    print('Pares sao indices; nenhum frame foi exportado e nenhum treinamento foi executado.')


if __name__=='__main__':
    main()
