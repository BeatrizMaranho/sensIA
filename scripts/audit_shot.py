"""Audita SHOT localmente. Nao corrige anotacoes nem cria rotulos de treino."""
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess

HEADER = re.compile(r"^(\d+\.mp4)(?:\s+(\d+))?\s*$", re.IGNORECASE)
PAIR = re.compile(r"^\s*(-?\d+)\s*(?:,|\s)\s*(-?\d+)\s*$")


def parse_annotations(text):
    """Mantem linhas e blocos duplicados; aceita virgula/espaco e colchetes."""
    blocks = {}
    current = None
    for line_no, original in enumerate(text.splitlines(), 1):
        line = original.strip()
        if not line:
            continue
        header = HEADER.fullmatch(line)
        if header:
            current = {"line": line_no, "header_value": int(header[2]) if header[2] else None,
                       "rows": []}
            blocks.setdefault(header[1], []).append(current)
            continue
        if ".mp4" in line.lower():
            # Nao anexar um cabecalho desconhecido ao video anterior.
            current = None
        if current is not None:
            cleaned = line
            if cleaned.startswith("[") and cleaned.endswith("]"):
                cleaned = cleaned[1:-1]
            pair = PAIR.fullmatch(cleaned)
            current["rows"].append({"line": line_no, "raw": original,
                                    "pair": tuple(map(int, pair.groups())) if pair else None})
    return blocks


def digest_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_video(path, cv2):
    cap = cv2.VideoCapture(str(path))
    try:
        if not cap.isOpened():
            return {"opened": False, "reported_frames": None, "decoded_frames": 0,
                    "fps": None, "width": None, "height": None}
        reported = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        decoded = 0
        while True:
            ok, _ = cap.read()
            if not ok:
                break
            decoded += 1
        return {"opened": True, "reported_frames": reported, "decoded_frames": decoded,
                "fps": fps if fps > 0 else None, "width": width, "height": height}
    finally:
        cap.release()


def write_csv(path, rows, fields):
    with path.open("x", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--videos", type=Path, default=Path("data/raw/shot/video_download"))
    parser.add_argument("--annotations", type=Path, default=Path("data/raw/shot/kuaishou_v2.txt"))
    parser.add_argument("--output", type=Path, default=Path("reports/shot_audit_v1"))
    args = parser.parse_args()
    if not args.videos.is_dir() or not args.annotations.is_file():
        parser.error("Confira os caminhos de videos e anotacoes.")
    if args.output.exists():
        parser.error("Pasta de saida ja existe. Use --output com outro nome para preservar a execucao anterior.")
    paths = sorted(p for p in args.videos.rglob("*") if p.is_file()
                   and p.suffix.lower() == ".mp4" and "__MACOSX" not in p.parts
                   and not p.name.startswith("._"))
    if not paths:
        parser.error("Nenhum MP4 encontrado.")
    try:
        import cv2
    except ImportError:
        parser.error("Instale OpenCV no ambiente: python -m pip install opencv-python-headless")
    source = args.annotations.read_text(encoding="utf-8-sig")
    blocks = parse_annotations(source)
    counts = Counter(p.name for p in paths)
    args.output.mkdir(parents=True, exist_ok=False)
    videos, intervals = [], []
    for number, path in enumerate(paths, 1):
        print(f"[{number}/{len(paths)}] {path.name}", flush=True)
        info = inspect_video(path, cv2)
        entries = blocks.get(path.name, [])
        reasons = []
        if not info["opened"] or not info["decoded_frames"]:
            reasons.append("unreadable_or_empty")
        if info["reported_frames"] != info["decoded_frames"]:
            reasons.append("reported_decoded_mismatch")
        if not entries:
            reasons.append("annotation_missing")
        if len(entries) > 1:
            reasons.append("duplicate_annotation_blocks")
        if counts[path.name] > 1:
            reasons.append("duplicate_video_name")
        header_values = [b["header_value"] for b in entries if b["header_value"] is not None]
        if any(v != info["decoded_frames"] for v in header_values):
            reasons.append("header_value_differs_from_decoded_count")
        valid = invalid = 0
        seen = set()
        previous_start = None
        for block in entries:
            for row in block["rows"]:
                pair = row["pair"]
                status = "within_bounds"
                if pair is None:
                    status = "unrecognized_format"
                else:
                    start, end = pair
                    if not 0 <= start < end < info["decoded_frames"]:
                        status = "invalid_order_or_out_of_bounds"
                    elif pair in seen:
                        status = "duplicate_interval"
                    elif previous_start is not None and start < previous_start:
                        status = "non_monotonic_order"
                    seen.add(pair)
                    previous_start = start
                if status == "within_bounds":
                    valid += 1
                else:
                    invalid += 1
                intervals.append({"video_name": path.name, "source_line": row["line"],
                                  "raw_annotation": row["raw"],
                                  "start": pair[0] if pair else None,
                                  "end": pair[1] if pair else None, "status": status})
        if invalid:
            reasons.append("interval_review_required")
        if entries and not valid and not invalid:
            reasons.append("empty_annotation_block")
        videos.append({"relative_path": path.relative_to(args.videos).as_posix(),
                       "video_name": path.name, "sha256": digest_file(path), **info,
                       "annotation_blocks": len(entries),
                       "header_values": json.dumps(header_values),
                       "intervals_within_bounds": valid, "intervals_for_review": invalid,
                       "review_reasons": ";".join(reasons),
                       "visual_alignment": "not_validated", "training_ready": False})
    write_csv(args.output / "videos.csv", videos, list(videos[0]))
    write_csv(args.output / "intervals.csv", intervals,
              ["video_name", "source_line", "raw_annotation", "start", "end", "status"])
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True,
                                         stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        commit = None
    summary = {"created_at_utc": datetime.now(timezone.utc).isoformat(),
               "script_sha256": digest_file(Path(__file__)), "git_commit": commit,
               "opencv_version": cv2.__version__, "videos_root": str(args.videos.resolve()),
               "annotation_sha256": digest_file(args.annotations),
               "annotation_path": str(args.annotations.resolve()),
               "index_assumption": "zero_based_diagnostic_only",
               "videos_found": len(videos),
               "videos_with_annotation": sum(v["annotation_blocks"] > 0 for v in videos),
               "videos_without_annotation": sum(v["annotation_blocks"] == 0 for v in videos),
               "videos_flagged_for_review": sum(bool(v["review_reasons"]) for v in videos),
               "intervals_within_bounds": sum(v["intervals_within_bounds"] for v in videos),
               "intervals_for_review": sum(v["intervals_for_review"] for v in videos),
               "note": "Limites e sintaxe nao comprovam alinhamento visual. Sem correcao, rotulos ou splits gerados."}
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print("Relatorios em:", args.output.resolve())


if __name__ == "__main__":
    main()
