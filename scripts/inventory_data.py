"""Inventaria arquivos locais sem copiá-los ou enviar dados à rede."""
import argparse
import csv
import hashlib
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        parser.error(f"Diretório inexistente: {root}")
    output = args.output.resolve()
    paths = sorted(p for p in root.rglob("*") if p.is_file()
                   and p.name not in {".gitkeep", "README.md"} and p.resolve() != output)
    if not paths:
        parser.error("Nenhum arquivo de dados encontrado. Baixe e extraia uma parte do dataset primeiro.")
    if output.exists():
        parser.error("Saída já existe. Escolha um novo nome para preservar a versão anterior.")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["relative_path", "size_bytes", "sha256"])
        for path in paths:
            digest = hashlib.sha256()
            with path.open("rb") as source:
                for chunk in iter(lambda: source.read(1024 * 1024), b""):
                    digest.update(chunk)
            writer.writerow([path.relative_to(root).as_posix(), path.stat().st_size, digest.hexdigest()])
    print(f"{len(paths)} arquivos inventariados em {output}")


if __name__ == "__main__":
    main()
