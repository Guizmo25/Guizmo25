#!/usr/bin/env python3
"""Extract figuremap and figuredata from a .nitro bundle."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Iterable


FIGUREMAP_NAMES = {"figuremap.xml", "figuremap.json"}
FIGUREDATA_NAMES = {"figuredata.xml", "figuredata.json"}


def iter_files(root: Path) -> Iterable[Path]:
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            yield Path(dirpath) / filename


def collect_targets(root: Path) -> tuple[list[Path], list[Path]]:
    figuremap_files: list[Path] = []
    figuredata_files: list[Path] = []
    for path in iter_files(root):
        name = path.name.lower()
        if name in FIGUREMAP_NAMES:
            figuremap_files.append(path)
        if name in FIGUREDATA_NAMES:
            figuredata_files.append(path)
    return figuremap_files, figuredata_files


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def copy_files(files: Iterable[Path], destination: Path) -> int:
    ensure_dir(destination)
    copied = 0
    for path in files:
        target = destination / path.name
        shutil.copy2(path, target)
        copied += 1
    return copied


def extract_nitro(nitro_path: Path) -> Path:
    temp_dir = Path(tempfile.mkdtemp(prefix="nitro_extract_"))
    with zipfile.ZipFile(nitro_path) as zf:
        zf.extractall(temp_dir)
    return temp_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Copie automatiquement les fichiers figuremap et figuredata depuis un .nitro "
            "(zip) ou un dossier Nitro."
        )
    )
    parser.add_argument(
        "nitro",
        help="Chemin vers le fichier .nitro (zip) ou un dossier Nitro.",
    )
    parser.add_argument(
        "--output",
        default="output",
        help="Dossier de sortie (par défaut: ./output).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    nitro_path = Path(args.nitro).expanduser().resolve()
    output_dir = Path(args.output).expanduser().resolve()

    if not nitro_path.exists():
        print(f"Erreur: le chemin '{nitro_path}' est introuvable.", file=sys.stderr)
        return 1

    temp_dir: Path | None = None
    root = nitro_path
    if nitro_path.is_file():
        if nitro_path.suffix.lower() != ".nitro" and not zipfile.is_zipfile(nitro_path):
            print(
                "Erreur: le fichier fourni n'est pas un .nitro ou un zip valide.",
                file=sys.stderr,
            )
            return 1
        temp_dir = extract_nitro(nitro_path)
        root = temp_dir
    elif not nitro_path.is_dir():
        print("Erreur: le chemin doit être un fichier ou un dossier.", file=sys.stderr)
        return 1

    figuremap_files, figuredata_files = collect_targets(root)

    figuremap_dir = output_dir / "figuremap"
    figuredata_dir = output_dir / "figuredata"

    figuremap_count = copy_files(figuremap_files, figuremap_dir)
    figuredata_count = copy_files(figuredata_files, figuredata_dir)

    print(f"Figuremap copiés: {figuremap_count} -> {figuremap_dir}")
    print(f"Figuredata copiés: {figuredata_count} -> {figuredata_dir}")

    if temp_dir:
        shutil.rmtree(temp_dir)

    if figuremap_count == 0 and figuredata_count == 0:
        print("Aucun fichier figuremap/figuredata trouvé.", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
