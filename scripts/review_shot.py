"""Gera montagens para revisao humana a partir da auditoria SHOT; nao cria rotulos."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import random
from datetime import datetime, timezone


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def select_examples(rows):
    # Somente candidatos abruptos; transicoes graduais exigem outra revisao.
    pairs = sorted({(int(r["start"]), int(r["end"])) for r in rows
                    if r["status"] == "within_bounds" and r["start"] and r["end"]
                    and int(r["end"]) == int(r["start"]) + 1})
    if not pairs:
        return []
    positions = sorted({0, len(pairs) // 2, len(pairs) - 1})
    return [("candidate", *pairs[i]) for i in positions]


def read_requested(path, indices, cv2):
    # Ler sequencialmente evita rotular uma busca aproximada por seek como frame exato.
    wanted = {i for i in indices if i >= 0}
    result = {}
    cap = cv2.VideoCapture(str(path))
    try:
        if not cap.isOpened():
            return result
        i = 0
        while wanted and i <= max(wanted):
            ok, frame = cap.read()
            if not ok:
                break
            if i in wanted:
                result[i] = frame
            i += 1
    finally:
        cap.release()
    return result


def make_tile(frame, index, cv2, np):
    canvas = np.zeros((248, 240, 3), dtype=np.uint8)
    if frame is not None:
        h, w = frame.shape[:2]
        scale = min(240 / w, 216 / h)
        resized = cv2.resize(frame, (max(1, round(w * scale)), max(1, round(h * scale))))
        rh, rw = resized.shape[:2]
        x, y = (240 - rw) // 2, 32 + (216 - rh) // 2
        canvas[y:y+rh, x:x+rw] = resized
    else:
        cv2.putText(canvas, "FRAME UNAVAILABLE", (8, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 190, 255), 1)
    cv2.putText(canvas, f"OpenCV index: {index}", (8, 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    return canvas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--videos", type=Path, default=Path("data/raw/shot/video_download"))
    parser.add_argument("--audit", type=Path, default=Path("reports/shot_audit_v1"))
    parser.add_argument("--output", type=Path, default=Path("reports/shot_visual_v1"))
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.count <= 0:
        parser.error("--count precisa ser positivo.")
    if args.output.exists():
        parser.error("Saida ja existe. Preserve a revisao e use outro --output.")
    if not args.videos.is_dir() or not all((args.audit / n).is_file() for n in ["videos.csv", "intervals.csv"]):
        parser.error("Confira a pasta dos videos e os CSVs originais da auditoria.")
    try:
        import cv2
        import numpy as np
    except ImportError:
        parser.error("Instale: python -m pip install opencv-python-headless")
    videos, intervals = read_csv(args.audit / "videos.csv"), read_csv(args.audit / "intervals.csv")
    grouped = {}
    for row in intervals:
        grouped.setdefault(row["video_name"], []).append(row)
    candidates = []
    for v in videos:
        if v["opened"] != "True" or v["reported_frames"] != v["decoded_frames"]:
            continue
        if int(v["annotation_blocks"]) != 1 or "duplicate_video_name" in v["review_reasons"]:
            continue
        examples = select_examples(grouped.get(v["video_name"], []))
        if len(examples) >= 3 and (args.videos / v["relative_path"]).is_file():
            candidates.append(v)
    candidates.sort(key=lambda v: v["relative_path"])
    if not candidates:
        parser.error("Sem videos elegiveis para tres candidatos abruptos. Confira a auditoria.")
    chosen = random.Random(args.seed).sample(candidates, min(args.count, len(candidates)))
    # Verificar hash antes de usar indices de uma versao anterior do video.
    for v in chosen:
        path = args.videos / v["relative_path"]
        h = hashlib.sha256()
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                h.update(chunk)
        if h.hexdigest() != v["sha256"]:
            parser.error(f"Video mudou desde a auditoria: {v['video_name']}. Gere nova auditoria.")
    args.output.mkdir(parents=True, exist_ok=False)
    review = []
    for number, v in enumerate(chosen, 1):
        name = v["video_name"]
        examples = select_examples(grouped[name])
        n = int(v["decoded_frames"])
        terminal = any(r["start"] and r["end"] and int(r["start"]) == n-1
                       and int(r["end"]) == n for r in grouped[name])
        if terminal:
            examples.append(("terminal_review", n-1, n))
        requested = {i for _, a, b in examples for i in [a-1, a, b, b+1]}
        frames = read_requested(args.videos / v["relative_path"], requested, cv2)
        rows = []
        for row_no, (kind, start, end) in enumerate(examples, 1):
            indices = [start-1, start, end, end+1]
            tiles = [make_tile(frames.get(i), i, cv2, np) for i in indices]
            title = np.zeros((30, 960, 3), dtype=np.uint8)
            cv2.putText(title, f"{name} | {kind} | annotation {start},{end}",
                        (8, 21), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            rows.extend([title, cv2.hconcat(tiles)])
            review.append({"video_name": name, "image": Path(name).stem + ".jpg",
                           "row": row_no, "kind": kind, "start": start, "end": end,
                           "all_requested_frames_read": all(i in frames for i in indices),
                           "decision": "pending", "reviewer": "", "notes": ""})
        out = args.output / (Path(name).stem + ".jpg")
        if not cv2.imwrite(str(out), cv2.vconcat(rows)):
            raise RuntimeError(f"Falha ao salvar {out}")
        print(f"[{number}/{len(chosen)}] {out}", flush=True)
    with (args.output / "review.csv").open("x", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(review[0]))
        writer.writeheader()
        writer.writerows(review)
    manifest = {"created_at_utc": datetime.now(timezone.utc).isoformat(), "seed": args.seed,
                "opencv_version": cv2.__version__, "selected_videos": chosen,
                "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "audit_hashes": {n: hashlib.sha256((args.audit/n).read_bytes()).hexdigest()
                                 for n in ["videos.csv", "intervals.csv"]},
                "note": "Amostra exploratoria; nao estima acuracia nem libera conjunto inteiro para treino."}
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("Abra os JPGs e registre a revisao em review.csv. Nenhum rotulo de treino foi criado.")


if __name__ == "__main__":
    main()
