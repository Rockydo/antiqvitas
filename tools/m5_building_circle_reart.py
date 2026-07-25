#!/usr/bin/env python3
"""Split reviewed four-up sheets into circle-safe active building icons."""

from __future__ import annotations

import argparse
import csv
import hashlib
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

import m5_roman_buildings
import m5_regional_buildings


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/m5/building_circle_reart.csv"
SHEET_DIR = ROOT / "assets_queue/generated_sources/building_circle_reart"
MASTER_DIR = ROOT / "assets_queue/generated"
ICON_DIR = ROOT / "main_menu/gfx/interface/icons/buildings"
DDS = ROOT / "tools/dds.py"
FIELDS = ("sheet", "quadrant", "key", "cohort", "style_references", "review")
QUADRANTS = ("top_left", "top_right", "bottom_left", "bottom_right")


def rows() -> list[dict[str, str]]:
    with MANIFEST.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError(f"manifest fields must be {FIELDS}")
        result = [{key: (value or "").strip() for key, value in row.items()} for row in reader]
    if not result:
        raise ValueError("building re-art manifest is empty")
    return result


def box(size: tuple[int, int], quadrant: str) -> tuple[int, int, int, int]:
    width, height = size
    if width != height or width % 2:
        raise ValueError(f"four-up sheet must be even and square, got {size}")
    half = width // 2
    return {
        "top_left": (0, 0, half, half),
        "top_right": (half, 0, width, half),
        "bottom_left": (0, half, half, height),
        "bottom_right": (half, half, width, height),
    }[quadrant]


def master(source: Image.Image, quadrant: str) -> Image.Image:
    crop = source.crop(box(source.size, quadrant)).convert("RGBA")
    icon = ImageOps.fit(crop, (128, 128), method=Image.Resampling.LANCZOS)
    mask = Image.new("L", icon.size, 0)
    ImageDraw.Draw(mask).ellipse((3, 3, 124, 124), fill=255)
    icon.putalpha(mask.filter(ImageFilter.GaussianBlur(0.7)))
    return icon


def convert(source: Path, target: Path) -> None:
    subprocess.run(
        [sys.executable, str(DDS), "convert", str(source), str(target), "--compression", "dxt5"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.DEVNULL,
    )


def master_path(key: str) -> Path:
    suffixed = MASTER_DIR / f"{key}_128.png"
    plain = MASTER_DIR / f"{key}.png"
    return suffixed if suffixed.is_file() or not plain.is_file() else plain


def validate_manifest(entries: list[dict[str, str]]) -> None:
    failures: list[str] = []
    active_by_cohort = {
        "named_roman": {row["key"] for row in m5_roman_buildings.load()},
        "regional_family": {row["key"] for row in m5_regional_buildings.load()[0]},
    }
    seen_keys: set[str] = set()
    seen_slots: set[tuple[str, str]] = set()
    for row in entries:
        key = row["key"]
        slot = (row["sheet"], row["quadrant"])
        if not all(row.values()):
            failures.append(f"blank manifest field in row for {key or '<blank>'}")
        if row["quadrant"] not in QUADRANTS:
            failures.append(f"invalid quadrant for {key}: {row['quadrant']}")
        if row["cohort"] not in active_by_cohort:
            failures.append(f"invalid re-art cohort for {key}: {row['cohort']}")
        elif key not in active_by_cohort[row["cohort"]]:
            failures.append(f"manifest key is not active in {row['cohort']}: {key}")
        if key in seen_keys:
            failures.append(f"duplicate manifest key: {key}")
        if slot in seen_slots:
            failures.append(f"duplicate sheet slot: {slot[0]} {slot[1]}")
        if row["review"] != "accepted":
            failures.append(f"sheet slot is not visually accepted: {key}")
        if row["style_references"] != "installed EU5 building icons":
            failures.append(f"missing installed-EU5 style provenance: {key}")
        seen_keys.add(key)
        seen_slots.add(slot)
    if failures:
        raise ValueError("\n".join(failures))


def write(entries: list[dict[str, str]]) -> None:
    MASTER_DIR.mkdir(parents=True, exist_ok=True)
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    opened: dict[str, Image.Image] = {}
    try:
        for row in entries:
            sheet = row["sheet"]
            if sheet not in opened:
                path = SHEET_DIR / sheet
                if not path.is_file():
                    raise ValueError(f"missing reviewed source sheet {path.relative_to(ROOT)}")
                opened[sheet] = Image.open(path).convert("RGBA")
            image = master(opened[sheet], row["quadrant"])
            target = master_path(row["key"])
            image.save(target)
            convert(target, ICON_DIR / f"{row['key']}.dds")
    finally:
        for image in opened.values():
            image.close()


def check(entries: list[dict[str, str]]) -> None:
    failures: list[str] = []
    hashes: dict[str, str] = {}
    for row in entries:
        sheet = SHEET_DIR / row["sheet"]
        master_file = master_path(row["key"])
        texture = ICON_DIR / f"{row['key']}.dds"
        for path, label in ((sheet, "sheet"), (master_file, "master"), (texture, "texture")):
            if not path.is_file():
                failures.append(f"missing {label} for {row['key']}: {path.relative_to(ROOT)}")
        if not master_file.is_file():
            continue
        with Image.open(master_file) as image:
            if image.mode != "RGBA" or image.size != (128, 128):
                failures.append(f"invalid master format for {row['key']}")
            elif max(image.getpixel(point)[3] for point in ((0, 0), (127, 0), (0, 127), (127, 127))) > 15:
                failures.append(f"master is not circle-safe for {row['key']}")
            digest = hashlib.sha256(image.convert("RGBA").tobytes()).hexdigest()
        if digest in hashes:
            failures.append(f"visual alias: {hashes[digest]} and {row['key']}")
        hashes[digest] = row["key"]
    if failures:
        raise ValueError("\n".join(failures))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        entries = rows()
        validate_manifest(entries)
        if args.write:
            write(entries)
        check(entries)
    except (OSError, ValueError, csv.Error, subprocess.CalledProcessError) as exc:
        print(f"m5_building_circle_reart: FAIL\n  - {exc}")
        return 1
    sheet_count = len({row["sheet"] for row in entries})
    print(f"m5_building_circle_reart: PASS ({len(entries)} direct icons from {sheet_count} reviewed sheets)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
