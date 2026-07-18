#!/usr/bin/env python3
"""Idempotently select a clean vanilla or ANTIQVITAS playset."""

from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_config() -> dict[str, object]:
    return json.loads((ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig"))


def backup(path: Path) -> Path | None:
    if not path.exists():
        return None
    directory = ROOT / "baselines/runtime/launcher_backups"
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = directory / f"{path.name}.{stamp}.bak"
    shutil.copy2(path, target)
    return target


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False, newline="\n"
    ) as handle:
        json.dump(value, handle, indent="\t")
        handle.write("\n")
        temp = Path(handle.name)
    temp.replace(path)
    json.loads(path.read_text(encoding="utf-8"))


def configure_json(path: Path, mod_path: str | None) -> None:
    previous = backup(path)
    try:
        data = (
            json.loads(path.read_text(encoding="utf-8-sig"))
            if path.exists()
            else {"file_version": "1.0.0", "playsets": []}
        )
        for playset in data.get("playsets", []):
            playset.pop("isActive", None)
        playset = {
            "name": "ANTIQVITAS" if mod_path else "ANTIQVITAS Vanilla Baseline",
            "isActive": True,
            "isAutomaticallySorted": False,
            "orderedListMods": (
                [{"path": mod_path.replace("\\", "/") + "/", "isEnabled": True}]
                if mod_path
                else []
            ),
            "DLC": [],
        }
        data["playsets"] = [
            item
            for item in data.get("playsets", [])
            if item.get("name") not in {"ANTIQVITAS", "ANTIQVITAS Vanilla Baseline"}
        ]
        data["playsets"].append(playset)
        atomic_json(path, data)
        loaded = json.loads(path.read_text(encoding="utf-8"))
        active = [item for item in loaded["playsets"] if item.get("isActive")]
        if len(active) != 1 or active[0]["orderedListMods"] != playset["orderedListMods"]:
            raise RuntimeError("playset read-back integrity check failed")
    except Exception:
        if previous:
            shutil.copy2(previous, path)
        raise


def inspect_sqlite(path: Path) -> list[str]:
    with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as db:
        return [
            row[0]
            for row in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
        ]


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--enable", action="store_true")
    mode.add_argument("--vanilla", action="store_true")
    parser.add_argument("--inspect", action="store_true")
    args = parser.parse_args()
    config = load_config()
    user_dir = Path(str(config["user_dir"]))
    playsets = user_dir / "playsets.json"
    sqlite = user_dir / "launcher-v2.sqlite"
    mod_path = str(config["mod_dir"] or config["repo_dir"]) if args.enable else None
    if playsets.exists() or not sqlite.exists():
        configure_json(playsets, mod_path)
        print(f"active playset: {'ANTIQVITAS' if mod_path else 'vanilla'} ({playsets})")
        return 0
    tables = inspect_sqlite(sqlite)
    print(f"launcher SQLite schema discovered: {', '.join(tables)}")
    print(
        "Refusing an unverified SQLite mutation; this installed build normally uses playsets.json",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
