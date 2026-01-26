#!/usr/bin/env python3
"""
Install Habbo clothing assets from a .nitro package into a server layout.

This script extracts a .nitro (zip) file, copies figuremap/figuredata/data
assets into the target directories, and optionally applies SQL migrations.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Installs Habbo clothing assets from a .nitro file into your server."
        )
    )
    parser.add_argument("nitro", type=Path, help="Path to the .nitro file")
    parser.add_argument(
        "--server-root",
        type=Path,
        help=(
            "Root folder of your Habbo server files. If set, defaults for "
            "figuremap, figuredata and data folders will be created under it."
        ),
    )
    parser.add_argument(
        "--figuremap-dir",
        type=Path,
        help="Override target directory for figuremap assets",
    )
    parser.add_argument(
        "--figuredata-dir",
        type=Path,
        help="Override target directory for figuredata assets",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        help="Override target directory for data assets",
    )
    parser.add_argument(
        "--db-host",
        default="localhost",
        help="MySQL host for applying SQL",
    )
    parser.add_argument("--db-port", type=int, default=3306, help="MySQL port")
    parser.add_argument("--db-user", help="MySQL user")
    parser.add_argument("--db-pass", help="MySQL password")
    parser.add_argument("--db-name", help="MySQL database name")
    parser.add_argument(
        "--mysql-bin",
        default="mysql",
        help="Path to mysql client binary (default: mysql)",
    )
    return parser.parse_args()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def copy_dir_contents(src: Path, dest: Path) -> None:
    ensure_dir(dest)
    for item in src.iterdir():
        target = dest / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)


def find_candidate_file(root: Path, names: tuple[str, ...]) -> Path | None:
    for name in names:
        candidate = root / name
        if candidate.exists():
            return candidate
    for path in root.rglob("*"):
        if path.is_file() and path.name in names:
            return path
    return None


def find_candidate_dir(root: Path, names: tuple[str, ...]) -> Path | None:
    for path in root.rglob("*"):
        if path.is_dir() and path.name.lower() in names:
            return path
    return None


def apply_sql(
    sql_files: list[Path],
    mysql_bin: str,
    host: str,
    port: int,
    user: str | None,
    password: str | None,
    db_name: str | None,
) -> None:
    if not sql_files:
        print("No SQL files found.")
        return

    if not user or not db_name:
        print("SQL files found but missing --db-user or --db-name; skipping SQL.")
        return

    for sql_file in sql_files:
        cmd = [
            mysql_bin,
            f"--host={host}",
            f"--port={port}",
            f"--user={user}",
            db_name,
        ]
        env = os.environ.copy()
        if password:
            env["MYSQL_PWD"] = password
        print(f"Applying SQL: {sql_file}")
        try:
            subprocess.run(cmd, check=True, env=env, stdin=sql_file.open("rb"))
        except FileNotFoundError:
            raise SystemExit(
                f"mysql client not found: {mysql_bin}. Install MySQL client or "
                "use --mysql-bin to point to it."
            ) from None
        except subprocess.CalledProcessError as exc:
            raise SystemExit(f"Failed to apply SQL {sql_file}: {exc}") from exc


def main() -> None:
    args = parse_args()
    nitro = args.nitro

    if not nitro.exists():
        raise SystemExit(f".nitro file not found: {nitro}")

    if not zipfile.is_zipfile(nitro):
        raise SystemExit("The provided .nitro file is not a valid zip archive.")

    server_root = args.server_root
    figuremap_dir = args.figuremap_dir
    figuredata_dir = args.figuredata_dir
    data_dir = args.data_dir

    if server_root:
        figuremap_dir = figuremap_dir or server_root / "figuremap"
        figuredata_dir = figuredata_dir or server_root / "figuredata"
        data_dir = data_dir or server_root / "data"

    if not any([figuremap_dir, figuredata_dir, data_dir]):
        raise SystemExit(
            "You must provide --server-root or explicit --figuremap-dir/"
            "--figuredata-dir/--data-dir paths."
        )

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        with zipfile.ZipFile(nitro, "r") as archive:
            archive.extractall(tmp_path)

        figuremap_src = find_candidate_file(tmp_path, ("figuremap.xml",))
        figuredata_src = find_candidate_file(tmp_path, ("figuredata.xml",))
        figuremap_dir_src = find_candidate_dir(tmp_path, ("figuremap",))
        figuredata_dir_src = find_candidate_dir(tmp_path, ("figuredata",))
        data_src = find_candidate_dir(tmp_path, ("data", "gamedata"))
        sql_files = sorted(tmp_path.rglob("*.sql"))

        if figuremap_dir and figuremap_dir_src:
            print(f"Copying figuremap folder to {figuremap_dir}")
            copy_dir_contents(figuremap_dir_src, figuremap_dir)
        elif figuremap_dir and figuremap_src:
            print(f"Copying figuremap file to {figuremap_dir}")
            ensure_dir(figuremap_dir)
            shutil.copy2(figuremap_src, figuremap_dir / figuremap_src.name)

        if figuredata_dir and figuredata_dir_src:
            print(f"Copying figuredata folder to {figuredata_dir}")
            copy_dir_contents(figuredata_dir_src, figuredata_dir)
        elif figuredata_dir and figuredata_src:
            print(f"Copying figuredata file to {figuredata_dir}")
            ensure_dir(figuredata_dir)
            shutil.copy2(figuredata_src, figuredata_dir / figuredata_src.name)

        if data_dir and data_src:
            print(f"Copying data folder to {data_dir}")
            copy_dir_contents(data_src, data_dir)

        apply_sql(
            sql_files,
            mysql_bin=args.mysql_bin,
            host=args.db_host,
            port=args.db_port,
            user=args.db_user,
            password=args.db_pass,
            db_name=args.db_name,
        )

    print("Installation complete.")


if __name__ == "__main__":
    main()
