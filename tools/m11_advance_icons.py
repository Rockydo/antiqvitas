#!/usr/bin/env python3
"""Validate the reviewed M11 age-group advance icon replacement set."""

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from dds import identify
from m8_knowledge import AGE_NAMES, advance_records


ROOT = Path(__file__).resolve().parents[1]
DIMENSIONS = (256, 256)
ADVANCE_TREE = ROOT / "in_game/common/advances/00_antiquitas_m8_tree.txt"
DIRECT_LEDGER = ROOT / "docs/m11/direct_advance_icons.csv"


@dataclass(frozen=True)
class AdvanceIcon:
    age: str
    icon: str
    source: str
    master: str
    texture: str


ADVANCE_ICONS = (
    AdvanceIcon(
        "Principate", "abacus_advance",
        "assets_queue/generated_sources/antq_advance_principate_source.png",
        "assets_queue/generated/antq_advance_principate_256.png",
        "main_menu/gfx/interface/advance/abacus_advance.dds",
    ),
    AdvanceIcon(
        "High Empires", "legalism_advance",
        "assets_queue/generated_sources/antq_advance_high_empires_source.png",
        "assets_queue/generated/antq_advance_high_empires_256.png",
        "main_menu/gfx/interface/advance/legalism_advance.dds",
    ),
    AdvanceIcon(
        "Crisis", "road_advance_1",
        "assets_queue/generated_sources/antq_advance_crisis_source.png",
        "assets_queue/generated/antq_advance_crisis_256.png",
        "main_menu/gfx/interface/advance/road_advance_1.dds",
    ),
    AdvanceIcon(
        "Dominate", "crown_power_advance_discovery",
        "assets_queue/generated_sources/antq_advance_dominate_source.png",
        "assets_queue/generated/antq_advance_dominate_256.png",
        "main_menu/gfx/interface/advance/crown_power_advance_discovery.dds",
    ),
    AdvanceIcon(
        "Migrations", "expansionism",
        "assets_queue/generated_sources/antq_advance_migrations_source.png",
        "assets_queue/generated/antq_advance_migrations_256.png",
        "main_menu/gfx/interface/advance/expansionism.dds",
    ),
)


def png_size(path: Path) -> tuple[int, int]:
    with Image.open(path) as image:
        if image.format != "PNG":
            raise ValueError(f"M11 advance-icon master is not PNG: {path}")
        return image.size


def direct_assets() -> list[AdvanceIcon]:
    if not DIRECT_LEDGER.is_file():
        return []
    required = ("key", "age", "subject", "source", "confidence", "status", "note")
    with DIRECT_LEDGER.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != required:
            raise ValueError(f"{DIRECT_LEDGER.relative_to(ROOT)} must use header {','.join(required)}")
        rows = list(reader)
    result: list[AdvanceIcon] = []
    seen: set[str] = set()
    record_ages = {record.key: AGE_NAMES[record.age_index] for record in advance_records()}
    for number, row in enumerate(rows, start=2):
        if (row.get("status") or "").strip() != "complete":
            continue
        key = (row.get("key") or "").strip()
        if not re.fullmatch(r"antq_[a-z0-9_]+", key) or key in seen:
            raise ValueError(f"{DIRECT_LEDGER.relative_to(ROOT)}:{number}: invalid or duplicate completed key {key!r}")
        if (row.get("confidence") or "").strip() != "secure":
            raise ValueError(f"{DIRECT_LEDGER.relative_to(ROOT)}:{number}: completed art must use secure confidence")
        if key not in record_ages:
            raise ValueError(f"{DIRECT_LEDGER.relative_to(ROOT)}:{number}: completed art has unknown advance {key}")
        age = (row.get("age") or "").strip()
        if age != record_ages[key]:
            raise ValueError(
                f"{DIRECT_LEDGER.relative_to(ROOT)}:{number}: {key} must use age "
                f"{record_ages[key]!r}, not {age!r}"
            )
        if not (row.get("subject") or "").strip() or not (row.get("source") or "").strip():
            raise ValueError(f"{DIRECT_LEDGER.relative_to(ROOT)}:{number}: completed art needs subject and source")
        slug = key.removeprefix("antq_")
        result.append(AdvanceIcon(
            age, f"antq_advance_{slug}",
            f"assets_queue/generated_sources/antq_advance_{slug}_source.png",
            f"assets_queue/generated/antq_advance_{slug}_256.png",
            f"main_menu/gfx/interface/advance/antq_advance_{slug}.dds",
        ))
        seen.add(key)
    return result


def validate_tree_mapping(direct: list[AdvanceIcon]) -> None:
    text = ADVANCE_TREE.read_text(encoding="utf-8")
    found = re.findall(r"^\s*icon\s*=\s*([^\s#]+)", text, flags=re.MULTILINE)
    direct_by_age = {age: sum(asset.age == age for asset in direct) for age in AGE_NAMES}
    expected = {
        asset.icon for asset in ADVANCE_ICONS if direct_by_age[asset.age] < 50
    } | {asset.icon for asset in direct}
    if set(found) != expected:
        raise ValueError(
            "M8 advance icons and the M11 reviewed icon mapping diverge: "
            f"expected {sorted(expected)}, found {sorted(set(found))}"
        )
    by_age = {asset.age: asset.icon for asset in ADVANCE_ICONS}
    for age, icon in by_age.items():
        expected_count = 50 - sum(asset.age == age for asset in direct)
        if found.count(icon) != expected_count:
            raise ValueError(f"M8 fallback icon {icon} must cover {expected_count} advances, found {found.count(icon)}")
    for asset in direct:
        if found.count(asset.icon) != 1:
            raise ValueError(f"M8 direct icon {asset.icon} must cover exactly one advance, found {found.count(asset.icon)}")


def validate() -> None:
    if len({asset.icon for asset in ADVANCE_ICONS}) != len(ADVANCE_ICONS):
        raise ValueError("duplicate M11 advance icon identifier")
    direct = direct_assets()
    validate_tree_mapping(direct)
    for asset in (*ADVANCE_ICONS, *direct):
        source = ROOT / asset.source
        master = ROOT / asset.master
        texture = ROOT / asset.texture
        for path, role in ((source, "source"), (master, "master"), (texture, "texture")):
            if not path.is_file():
                raise ValueError(f"M11 {asset.age} advance-icon {role} is missing: {path}")
        if png_size(master) != DIMENSIONS:
            raise ValueError(f"M11 {asset.age} advance-icon master has wrong dimensions: {master}")
        details = identify(texture)
        if details != {
            "format": "DDS", "width": str(DIMENSIONS[0]), "height": str(DIMENSIONS[1]),
            "depth": "8", "channels": "srgba 4.0",
        }:
            raise ValueError(
                f"M11 {asset.age} advance-icon texture has unexpected format: {texture}: {details}"
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate the fixed M11 advance icon set")
    parser.parse_args()
    validate()
    direct = direct_assets()
    print(f"m11_advance_icons: PASS ({len(direct)} direct icons + {len(ADVANCE_ICONS)} reviewed transitional group icons for 250 advances)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
