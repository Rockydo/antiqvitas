#!/usr/bin/env python3
"""Split reviewed four-up Roman economy sheets into direct EU5 assets."""

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
SHEET_DIR = ROOT / "assets_queue/generated_sources/roman_economy"
SOURCE_DIR = ROOT / "assets_queue/generated/roman_economy"
GENERAL_SOURCE_DIR = ROOT / "assets_queue/generated"
BUILDING_DIR = ROOT / "main_menu/gfx/interface/icons/buildings"
GOODS_DIR = ROOT / "main_menu/gfx/interface/icons/trade_goods"
ILLUSTRATION_DIR = GOODS_DIR / "illustrations"
LEDGER = ROOT / "docs/m5/roman_economy_art.csv"
CONTACT = ROOT / "docs/m5/ROMAN_ECONOMY_ART_CONTACT.png"
DDS = ROOT / "tools/dds.py"
QUADRANTS = ("top_left", "top_right", "bottom_left", "bottom_right")

SHEETS: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("buildings_01.png", (("building", "antq_reg_villa_rustica"), ("building", "antq_reg_tabernae_row"), ("building", "antq_reg_forum_basilica"), ("building", "antq_reg_horrea_complex"))),
    ("buildings_02.png", (("building", "antq_reg_annona_bakery"), ("building", "antq_reg_aqueduct_distribution"), ("building", "antq_reg_thermae_complex"), ("building", "antq_reg_cursus_mansio"))),
    ("buildings_03.png", (("building", "antq_reg_river_port"), ("building", "antq_reg_colonia_forum"), ("building", "antq_reg_castra_fabrica"), ("building", "antq_reg_frontier_magazine"))),
    ("buildings_04.png", (("building", "antq_reg_quarry_contractors"), ("building", "antq_reg_olive_estate"), ("building", "antq_reg_vineyard_estate"), ("building", "antq_reg_textile_quarter"))),
    ("buildings_05.png", (("building", "antq_reg_ceramic_quarter"), ("building", "antq_reg_insulae_quarter"), ("building", "antq_reg_temple_precinct"))),
    ("buildings_06.png", (("building", "antq_reg_bronze_workers_collegium"), ("building", "antq_reg_lead_pipeworks"), ("building", "antq_reg_unguentarium"), ("building", "antq_reg_collegia_hall"))),
    ("goods_01.png", (("good", "antq_olive_oil"), ("good", "antq_preserved_fish"), ("good", "antq_grain_products"), ("good", "antq_perfumes"))),
    ("goods_02.png", (("good", "antq_wax_goods"), ("good", "antq_soap"), ("good", "antq_bronze_wares"), ("good", "antq_lead_wares"))),
)


def quadrant_box(size: tuple[int, int], quadrant: str) -> tuple[int, int, int, int]:
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


def icon_master(source: Image.Image, quadrant: str) -> Image.Image:
    crop = source.crop(quadrant_box(source.size, quadrant)).convert("RGBA")
    icon = ImageOps.fit(crop, (128, 128), method=Image.Resampling.LANCZOS)
    mask = Image.new("L", icon.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((3, 3, 124, 124), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(0.7))
    icon.putalpha(mask)
    return icon


def illustration(source: Image.Image, quadrant: str) -> Image.Image:
    crop = source.crop(quadrant_box(source.size, quadrant)).convert("RGBA")
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
    rows: list[tuple[str, str, str, str]] = []
    for filename, entries in SHEETS:
        if len(entries) > 4:
            raise ValueError(f"{filename} has more than four mapped quadrants")
        for quadrant, (kind, key) in zip(QUADRANTS, entries, strict=False):
            rows.append((kind, key, filename, quadrant))
    keys = [key for _kind, key, _sheet, _quadrant in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("Roman economy art mapping repeats a key")
    return rows


def render_ledger(rows: list[tuple[str, str, str, str]]) -> str:
    stream = StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(("kind", "key", "sheet", "quadrant", "style_references", "historical_reference"))
    for kind, key, sheet, quadrant in rows:
        style = "installed EU5 direct building icons" if kind == "building" else "installed EU5 direct trade-good icons"
        history = "docs/m5/roman_economy_profiles.csv; docs/m5/regional_building_families.csv; docs/m5/custom_goods.csv"
        writer.writerow((kind, key, sheet, quadrant, style, history))
    return stream.getvalue()


def expected_targets(rows: list[tuple[str, str, str, str]]) -> list[Path]:
    result: list[Path] = []
    for kind, key, _sheet, _quadrant in rows:
        if kind == "building":
            result.append(BUILDING_DIR / f"{key}.dds")
        else:
            result.extend((GOODS_DIR / f"icon_goods_{key}.dds", ILLUSTRATION_DIR / f"icon_goods_{key}.dds"))
    return result


def write() -> None:
    rows = records()
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    GENERAL_SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    BUILDING_DIR.mkdir(parents=True, exist_ok=True)
    GOODS_DIR.mkdir(parents=True, exist_ok=True)
    ILLUSTRATION_DIR.mkdir(parents=True, exist_ok=True)
    opened: dict[str, Image.Image] = {}
    previews: list[tuple[str, Image.Image]] = []
    for kind, key, sheet, quadrant in rows:
        if sheet not in opened:
            source = SHEET_DIR / sheet
            if not source.is_file():
                raise ValueError(f"missing generated four-up source {source.relative_to(ROOT)}")
            opened[sheet] = Image.open(source).convert("RGBA")
        master = icon_master(opened[sheet], quadrant)
        master_path = SOURCE_DIR / f"{key}.png"
        master.save(master_path)
        general_path = GENERAL_SOURCE_DIR / f"{key}.png"
        master.save(general_path)
        if kind == "building":
            dds(master_path, BUILDING_DIR / f"{key}.dds")
        else:
            dds(general_path, GOODS_DIR / f"icon_goods_{key}.dds")
            wide = illustration(opened[sheet], quadrant)
            wide_path = SOURCE_DIR / f"{key}_illustration.png"
            wide.save(wide_path)
            dds(wide_path, ILLUSTRATION_DIR / f"icon_goods_{key}.dds")
        previews.append((key, master))
    for image in opened.values():
        image.close()

    tile = 180
    columns = 8
    rows_count = (len(previews) + columns - 1) // columns
    contact = Image.new("RGBA", (columns * tile, rows_count * (tile + 28)), (16, 25, 43, 255))
    draw = ImageDraw.Draw(contact)
    for index, (key, icon) in enumerate(previews):
        x = (index % columns) * tile
        y = (index // columns) * (tile + 28)
        contact.alpha_composite(icon.resize((160, 160), Image.Resampling.NEAREST), (x + 10, y + 4))
        draw.text((x + 6, y + 166), key.replace("antq_reg_", "").replace("antq_", ""), fill=(222, 226, 232, 255))
    contact.convert("RGB").save(CONTACT)
    LEDGER.write_text(render_ledger(rows), encoding="utf-8-sig", newline="")


def check() -> None:
    rows = records()
    failures: list[str] = []
    ledger = render_ledger(rows)
    if not LEDGER.is_file() or LEDGER.read_text(encoding="utf-8-sig") != ledger:
        failures.append("Roman economy art ledger is stale")
    if not CONTACT.is_file():
        failures.append("Roman economy contact sheet is missing")
    hashes: dict[str, str] = {}
    for target in expected_targets(rows):
        if not target.is_file():
            failures.append(f"missing direct asset {target.relative_to(ROOT)}")
            continue
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        if digest in hashes:
            failures.append(f"duplicate direct assets {hashes[digest]} and {target.relative_to(ROOT)}")
        hashes[digest] = str(target.relative_to(ROOT))
    for kind, key, _sheet, _quadrant in rows:
        master = SOURCE_DIR / f"{key}.png"
        if not master.is_file():
            failures.append(f"missing master {master.relative_to(ROOT)}")
            continue
        with Image.open(master) as image:
            if image.mode != "RGBA" or image.size != (128, 128) or image.getpixel((0, 0))[3] != 0:
                failures.append(f"invalid circle-safe master {master.relative_to(ROOT)}")
        retained = GENERAL_SOURCE_DIR / f"{key}.png"
        if not retained.is_file() or retained.read_bytes() != master.read_bytes():
            failures.append(f"missing or stale retained master {retained.relative_to(ROOT)}")
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
        print(f"m5_roman_economy_art: FAIL\n  - {exc}")
        return 1
    print(f"m5_roman_economy_art: PASS ({len(records())} direct circle-safe assets from {len(SHEETS)} four-up sheets)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
