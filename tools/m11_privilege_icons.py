#!/usr/bin/env python3
"""Render and validate direct ANTIQVITAS estate-privilege UI icons.

The installed UI resolves ``GetEstatePrivilegeIcon`` by privilege definition
key.  This tool keeps the staged migration auditable: each completed ledger row
has an individual source, 64x90 master, and direct BC7 DDS texture.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PRIVILEGES = ROOT / "docs/m6/privileges.csv"
LEDGER = ROOT / "docs/m11/direct_privilege_icons.csv"
ICON_DIR = ROOT / "main_menu/gfx/interface/icons/privileges"
DDS = ROOT / "tools/dds.py"
DIMENSIONS = (64, 90)
FIELDS = ("key", "subject", "source", "confidence", "status", "note")


@dataclass(frozen=True)
class DirectIcon:
    key: str
    source: Path
    master: Path


def privilege_keys() -> set[str]:
    with PRIVILEGES.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ())[:2] != ("key", "estate"):
            raise ValueError(f"unexpected privilege ledger header: {PRIVILEGES}")
        keys = {(row.get("key") or "").strip() for row in reader}
    if not keys or any(not key.startswith("antq_") for key in keys):
        raise ValueError("M6 privilege ledger has invalid ANTIQVITAS keys")
    return keys


def direct_icons() -> tuple[DirectIcon, ...]:
    with LEDGER.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError(f"{LEDGER.relative_to(ROOT)} must use header {','.join(FIELDS)}")
        rows = list(reader)
    known = privilege_keys()
    result: list[DirectIcon] = []
    seen: set[str] = set()
    for number, row in enumerate(rows, start=2):
        if (row.get("status") or "").strip() != "complete":
            continue
        key = (row.get("key") or "").strip()
        if key not in known or key in seen:
            raise ValueError(f"{LEDGER.relative_to(ROOT)}:{number}: unknown or duplicate completed key {key!r}")
        if (row.get("confidence") or "").strip() != "secure":
            raise ValueError(f"{LEDGER.relative_to(ROOT)}:{number}: completed icon must use secure confidence")
        if not (row.get("subject") or "").strip() or not (row.get("source") or "").strip():
            raise ValueError(f"{LEDGER.relative_to(ROOT)}:{number}: completed icon needs subject and source")
        slug = key.removeprefix("antq_")
        result.append(DirectIcon(
            key,
            ROOT / "assets_queue/generated_sources" / f"antq_privilege_{slug}_source.png",
            ROOT / "assets_queue/generated" / f"antq_privilege_{slug}_64x90.png",
        ))
        seen.add(key)
    if len({icon.source for icon in result}) != len(result):
        raise ValueError("direct privilege icons may not share a generated source")
    if len({icon.master for icon in result}) != len(result):
        raise ValueError("direct privilege icons may not share a generated master")
    return tuple(result)


def dds_details(path: Path) -> dict[str, str]:
    command = [sys.executable, str(DDS), "identify", str(path)]
    return json.loads(subprocess.run(command, check=True, text=True, capture_output=True).stdout)


def check_dds(path: Path) -> None:
    expected = {
        "format": "DDS", "width": str(DIMENSIONS[0]), "height": str(DIMENSIONS[1]),
        "depth": "8", "channels": "srgba 4.0",
    }
    actual = dds_details(path)
    if actual != expected:
        raise ValueError(f"direct privilege DDS has unexpected contract: {path}: {actual}")


def write() -> None:
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    for icon in direct_icons():
        if not icon.master.is_file():
            raise ValueError(f"missing direct privilege master: {icon.master}")
        subprocess.run(
            [sys.executable, str(DDS), "convert", str(icon.master),
             str(ICON_DIR / f"{icon.key}.dds"), "--compression", "bc7"],
            check=True,
        )


def validate() -> None:
    direct = direct_icons()
    for icon in direct:
        texture = ICON_DIR / f"{icon.key}.dds"
        for path, label in ((icon.source, "source"), (icon.master, "master"), (texture, "texture")):
            if not path.is_file():
                raise ValueError(f"missing direct privilege {label}: {path}")
        with Image.open(icon.master) as image:
            if image.format != "PNG" or image.size != DIMENSIONS:
                raise ValueError(f"direct privilege master has wrong PNG contract: {icon.master}")
        check_dds(texture)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        if args.write:
            write()
        validate()
    except (OSError, ValueError, csv.Error, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"m11_privilege_icons: FAIL\n  - {exc}")
        return 1
    direct = direct_icons()
    print(f"m11_privilege_icons: PASS ({len(direct)} direct privilege icons; {len(privilege_keys()) - len(direct)} remaining)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
