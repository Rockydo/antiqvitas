#!/usr/bin/env python3
"""Render twelve reviewed food goods and eight workshops from pinned four-up atlases."""

from __future__ import annotations

import argparse
import csv
import hashlib
import subprocess
import sys
from io import StringIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SHEET_DIR = ROOT / "assets_queue/generated_sources/food_goods_expansion"
MASTER_DIR = ROOT / "assets_queue/generated"
GOODS_DIR = ROOT / "main_menu/gfx/interface/icons/trade_goods"
ILLUSTRATION_DIR = GOODS_DIR / "illustrations"
BUILDING_DIR = ROOT / "main_menu/gfx/interface/icons/buildings"
CONTACT = ROOT / "docs/m5/FOOD_GOODS_EXPANSION_CONTACT.png"
LEDGER = ROOT / "docs/m5/food_goods_art.csv"
DDS = ROOT / "tools/dds.py"
CELLS = ("top_left", "top_right", "bottom_left", "bottom_right")

SHEETS = {
    "food_goods_raw_01.png": (
        "477f76c9ac0eac92036048ebc71a3ed291f0bce1753329419d442b765004be8a",
        (
            ("antq_dates", "top_left"),
            ("antq_sesame", "top_right"),
            ("antq_tree_nuts", "bottom_left"),
            ("antq_coconuts", "bottom_right"),
        ),
        "good",
    ),
    "food_goods_preserved_01.png": (
        "c08447520f1a9e3ea09d8a9727dc8cdeb71b76c9ecbe6105bc047a8bef867c53",
        (
            ("antq_cheese_curds", "top_left"),
            ("antq_cured_meat", "top_right"),
            ("antq_dried_fruit", "bottom_left"),
            ("antq_nut_pastes", "bottom_right"),
        ),
        "good",
    ),
    "food_goods_liquid_01.png": (
        "2478f8887a29606256e6057f616aabbbecf76a452b8015003330c6cba846157e",
        (
            ("antq_sesame_oil", "top_left"),
            ("antq_coconut_products", "top_right"),
            ("antq_rice_wine", "bottom_left"),
            ("antq_soy_condiments", "bottom_right"),
        ),
        "good",
    ),
    "food_buildings_01.png": (
        "8d3bfcbee855441b9fa10930b56b1077f115bd1594336746f1ffc0aea6ac7919",
        (
            ("antq_reg_date_drying_yard", "top_left"),
            ("antq_reg_sesame_oil_press", "top_right"),
            ("antq_reg_nut_grinding_house", "bottom_left"),
            ("antq_reg_coconut_workshop", "bottom_right"),
        ),
        "building",
    ),
    "food_buildings_02.png": (
        "0771f26cfa0a9f028f132916a62a05ea6485b8948cbd34cf50ed11401018f2c4",
        (
            ("antq_reg_cheese_dairy", "top_left"),
            ("antq_reg_meat_curing_yard", "top_right"),
            ("antq_reg_rice_wine_house", "bottom_left"),
            ("antq_reg_soy_fermentary", "bottom_right"),
        ),
        "building",
    ),
}


def cell_box(size: tuple[int, int], cell: str) -> tuple[int, int, int, int]:
    width, height = size
    if width != height or width < 1024 or width % 2:
        raise ValueError(f"four-up sheet must be an even square at least 1024px, got {width}x{height}")
    half = width // 2
    index = CELLS.index(cell)
    column, row = index % 2, index // 2
    return column * half, row * half, (column + 1) * half, (row + 1) * half


def icon_master(source: Image.Image, cell: str) -> Image.Image:
    crop = source.crop(cell_box(source.size, cell)).convert("RGBA")
    icon = ImageOps.fit(crop, (128, 128), method=Image.Resampling.LANCZOS)
    mask = Image.new("L", icon.size, 0)
    ImageDraw.Draw(mask).ellipse((3, 3, 124, 124), fill=255)
    icon.putalpha(mask.filter(ImageFilter.GaussianBlur(0.7)))
    return icon


def illustration(source: Image.Image, cell: str) -> Image.Image:
    crop = source.crop(cell_box(source.size, cell)).convert("RGBA")
    crop.thumbnail((440, 420), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (1080, 440), (16, 25, 43, 255))
    canvas.alpha_composite(crop, ((1080 - crop.width) // 2, (440 - crop.height) // 2))
    return canvas


def dds(source: Path, target: Path) -> None:
    subprocess.run(
        [sys.executable, str(DDS), "convert", str(source), str(target), "--compression", "dxt5"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.DEVNULL,
    )


def records() -> list[tuple[str, str, str, str]]:
    result: list[tuple[str, str, str, str]] = []
    for sheet, (_digest, entries, kind) in SHEETS.items():
        result.extend((key, sheet, cell, kind) for key, cell in entries)
    keys = [key for key, _sheet, _cell, _kind in result]
    if len(keys) != len(set(keys)):
        raise ValueError("food-goods atlas mapping repeats a key")
    return result


def ledger_text(entries: list[tuple[str, str, str, str]]) -> str:
    stream = StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(("key", "kind", "sheet", "cell", "style_reference", "historical_reference"))
    for key, sheet, cell, kind in entries:
        writer.writerow(
            (
                key,
                kind,
                sheet,
                cell,
                "installed EU5 direct trade-good/building icons; exact four-up 2x2 atlas; neutral dark-navy commodity still life",
                "docs/m5/custom_goods.csv; docs/m5/regional_building_families.csv; docs/m5/food_building_seeds.csv",
            )
        )
    return stream.getvalue()


def write() -> None:
    entries = records()
    for directory in (MASTER_DIR, GOODS_DIR, ILLUSTRATION_DIR, BUILDING_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    opened: dict[str, Image.Image] = {}
    previews: list[tuple[str, str, Image.Image]] = []
    for key, sheet, cell, kind in entries:
        if sheet not in opened:
            path = SHEET_DIR / sheet
            if not path.is_file():
                raise ValueError(f"missing reviewed four-up source {path.relative_to(ROOT)}")
            expected_hash = SHEETS[sheet][0]
            if hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
                raise ValueError(f"reviewed atlas hash drift for {path.relative_to(ROOT)}")
            opened[sheet] = Image.open(path).convert("RGBA")
            cell_box(opened[sheet].size, CELLS[0])
        master = icon_master(opened[sheet], cell)
        master_path = MASTER_DIR / f"{key}.png"
        master.save(master_path)
        if kind == "good":
            dds(master_path, GOODS_DIR / f"icon_goods_{key}.dds")
            wide = illustration(opened[sheet], cell)
            wide_path = MASTER_DIR / f"{key}_illustration.png"
            wide.save(wide_path)
            dds(wide_path, ILLUSTRATION_DIR / f"icon_goods_{key}.dds")
        else:
            dds(master_path, BUILDING_DIR / f"{key}.dds")
        previews.append((key, kind, master))
    for source in opened.values():
        source.close()

    tile, columns = 180, 5
    rows = (len(previews) + columns - 1) // columns
    contact = Image.new("RGBA", (columns * tile, rows * (tile + 28)), (16, 25, 43, 255))
    draw = ImageDraw.Draw(contact)
    for index, (key, kind, icon) in enumerate(previews):
        x, y = (index % columns) * tile, (index // columns) * (tile + 28)
        contact.alpha_composite(icon.resize((160, 160), Image.Resampling.NEAREST), (x + 10, y + 4))
        label = key.removeprefix("antq_reg_").removeprefix("antq_")
        draw.text((x + 6, y + 166), f"{kind[0]}:{label}", fill=(222, 226, 232, 255))
    contact.convert("RGB").save(CONTACT)
    LEDGER.write_text(ledger_text(entries), encoding="utf-8-sig", newline="")


def check() -> None:
    entries = records()
    failures: list[str] = []
    if not LEDGER.is_file() or LEDGER.read_text(encoding="utf-8-sig") != ledger_text(entries):
        failures.append("food-goods art ledger is stale")
    if not CONTACT.is_file():
        failures.append("food-goods contact sheet is missing")
    hashes: dict[str, str] = {}
    for sheet, (expected_hash, _entries, _kind) in SHEETS.items():
        path = SHEET_DIR / sheet
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
            failures.append(f"missing or changed reviewed atlas {path.relative_to(ROOT)}")
    for key, _sheet, _cell, kind in entries:
        master = MASTER_DIR / f"{key}.png"
        targets = [master]
        if kind == "good":
            targets.extend(
                (
                    GOODS_DIR / f"icon_goods_{key}.dds",
                    ILLUSTRATION_DIR / f"icon_goods_{key}.dds",
                    MASTER_DIR / f"{key}_illustration.png",
                )
            )
        else:
            targets.append(BUILDING_DIR / f"{key}.dds")
        for target in targets:
            if not target.is_file():
                failures.append(f"missing direct asset {target.relative_to(ROOT)}")
                continue
            if target.suffix.lower() == ".dds":
                digest = hashlib.sha256(target.read_bytes()).hexdigest()
                previous = hashes.setdefault(digest, str(target.relative_to(ROOT)))
                if previous != str(target.relative_to(ROOT)):
                    failures.append(f"duplicate direct DDS assets {previous} and {target.relative_to(ROOT)}")
        if master.is_file():
            with Image.open(master) as image:
                if image.mode != "RGBA" or image.size != (128, 128) or image.getpixel((0, 0))[3] != 0:
                    failures.append(f"invalid circle-safe master {master.relative_to(ROOT)}")
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
        if args.write:
            write()
        check()
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"m5_food_goods_expansion: FAIL\n  - {exc}")
        return 1
    print(
        "m5_food_goods_expansion: PASS "
        f"({sum(kind == 'good' for *_rest, kind in records())} goods and "
        f"{sum(kind == 'building' for *_rest, kind in records())} buildings "
        f"from {len(SHEETS)} reviewed four-up atlases)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
