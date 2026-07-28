#!/usr/bin/env python3
"""Render twelve reviewed ancient craft goods from two pinned six-up atlases."""

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
SHEET_DIR = ROOT / "assets_queue/generated_sources/ancient_goods_expansion"
SOURCE_DIR = ROOT / "assets_queue/generated/ancient_goods_expansion"
GENERAL_SOURCE_DIR = ROOT / "assets_queue/generated"
GOODS_DIR = ROOT / "main_menu/gfx/interface/icons/trade_goods"
ILLUSTRATION_DIR = GOODS_DIR / "illustrations"
LEDGER = ROOT / "docs/m5/ancient_goods_expansion_art.csv"
CONTACT = ROOT / "docs/m5/ANCIENT_GOODS_EXPANSION_CONTACT.png"
DDS = ROOT / "tools/dds.py"

SHEETS = {
    "goods_crafts_01.png": (
        "e97a7640907cedcfacca6f0c8536df674d9fca5d553ce7aff177d9bf89d0b195",
        (
            "antq_fine_ceramics", "antq_glasswares", "antq_iron_hardware",
            "antq_leather_goods", "antq_cordage", "antq_parchment",
        ),
    ),
    "goods_crafts_02.png": (
        "2526977c69d5a89dbd7635e0a4248cb45e42d7842fc90f281c03bd725efdee31",
        (
            "antq_lacquerware", "antq_amber_ornaments", "antq_glass_beads",
            "antq_carpets", "antq_felt_goods", "antq_sailcloth",
        ),
    ),
}
DIRECT_SOURCES = {
    "antq_barley": (
        "antq_barley_source.png",
        "082e6302579b430313af9fb3e74adc11bf3cfcbb1b0afc241b5d01d56c0003d5",
    ),
}
CELLS = ("top_left", "top_middle", "top_right", "bottom_left", "bottom_middle", "bottom_right")


def records() -> list[tuple[str, str, str]]:
    result = [
        (key, sheet, cell)
        for sheet, (_digest, keys) in SHEETS.items()
        for key, cell in zip(keys, CELLS, strict=True)
    ]
    keys = [key for key, _sheet, _cell in result]
    if len(keys) != len(set(keys)):
        raise ValueError("ancient-goods atlas mapping repeats a key")
    return result


def cell_box(size: tuple[int, int], cell: str) -> tuple[int, int, int, int]:
    width, height = size
    if (width, height) != (1536, 1024):
        raise ValueError(f"six-up sheet must be exactly 1536x1024, got {width}x{height}")
    index = CELLS.index(cell)
    column, row = index % 3, index // 3
    return column * 512, row * 512, (column + 1) * 512, (row + 1) * 512


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


def direct_icon_master(source: Image.Image) -> Image.Image:
    icon = ImageOps.fit(source.convert("RGBA"), (128, 128), method=Image.Resampling.LANCZOS)
    mask = Image.new("L", icon.size, 0)
    ImageDraw.Draw(mask).ellipse((3, 3, 124, 124), fill=255)
    icon.putalpha(mask.filter(ImageFilter.GaussianBlur(0.7)))
    return icon


def direct_illustration(source: Image.Image) -> Image.Image:
    crop = source.convert("RGBA")
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


def ledger_text(rows: list[tuple[str, str, str]]) -> str:
    stream = StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(("key", "sheet", "cell", "style_reference", "historical_reference"))
    for key, sheet, cell in rows:
        writer.writerow((
            key,
            sheet,
            cell,
            "installed EU5 direct trade-good icons; restrained dark-blue archaeological still life",
            "docs/m5/custom_goods.csv; docs/m5/regional_building_families.csv",
        ))
    for key, (source, _digest) in sorted(DIRECT_SOURCES.items()):
        writer.writerow((
            key,
            source,
            "direct",
            "installed EU5 direct trade-good icons; restrained dark-blue archaeological still life",
            "docs/m5/custom_goods.csv; docs/world_1ad/SOURCES.md",
        ))
    return stream.getvalue()


def write() -> None:
    rows = records()
    for directory in (SOURCE_DIR, GENERAL_SOURCE_DIR, GOODS_DIR, ILLUSTRATION_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    opened: dict[str, Image.Image] = {}
    previews: list[tuple[str, Image.Image]] = []
    for key, sheet, cell in rows:
        if sheet not in opened:
            source_path = SHEET_DIR / sheet
            if not source_path.is_file():
                raise ValueError(f"missing generated six-up source {source_path.relative_to(ROOT)}")
            expected_hash = SHEETS[sheet][0]
            actual_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
            if actual_hash != expected_hash:
                raise ValueError(f"reviewed atlas hash drift for {source_path.relative_to(ROOT)}")
            opened[sheet] = Image.open(source_path).convert("RGBA")
            cell_box(opened[sheet].size, CELLS[0])
        master = icon_master(opened[sheet], cell)
        retained = SOURCE_DIR / f"{key}.png"
        general = GENERAL_SOURCE_DIR / f"{key}.png"
        master.save(retained)
        master.save(general)
        dds(general, GOODS_DIR / f"icon_goods_{key}.dds")
        wide = illustration(opened[sheet], cell)
        wide_path = SOURCE_DIR / f"{key}_illustration.png"
        wide.save(wide_path)
        dds(wide_path, ILLUSTRATION_DIR / f"icon_goods_{key}.dds")
        previews.append((key, master))
    for key, (filename, expected_hash) in sorted(DIRECT_SOURCES.items()):
        source_path = ROOT / "assets_queue/generated_sources" / filename
        if not source_path.is_file():
            raise ValueError(f"missing generated direct source {source_path.relative_to(ROOT)}")
        actual_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            raise ValueError(f"reviewed direct-source hash drift for {source_path.relative_to(ROOT)}")
        with Image.open(source_path) as source:
            master = direct_icon_master(source)
            wide = direct_illustration(source)
        retained = SOURCE_DIR / f"{key}.png"
        general = GENERAL_SOURCE_DIR / f"{key}.png"
        master.save(retained)
        master.save(general)
        dds(general, GOODS_DIR / f"icon_goods_{key}.dds")
        wide_path = SOURCE_DIR / f"{key}_illustration.png"
        wide.save(wide_path)
        dds(wide_path, ILLUSTRATION_DIR / f"icon_goods_{key}.dds")
        previews.append((key, master))
    for image in opened.values():
        image.close()

    tile, columns = 180, 6
    contact = Image.new("RGBA", (columns * tile, 2 * (tile + 28)), (16, 25, 43, 255))
    draw = ImageDraw.Draw(contact)
    for index, (key, icon) in enumerate(previews):
        x, y = (index % columns) * tile, (index // columns) * (tile + 28)
        contact.alpha_composite(icon.resize((160, 160), Image.Resampling.NEAREST), (x + 10, y + 4))
        draw.text((x + 6, y + 166), key.removeprefix("antq_"), fill=(222, 226, 232, 255))
    contact.convert("RGB").save(CONTACT)
    LEDGER.write_text(ledger_text(rows), encoding="utf-8-sig", newline="")


def check() -> None:
    rows = records()
    failures: list[str] = []
    if not LEDGER.is_file() or LEDGER.read_text(encoding="utf-8-sig") != ledger_text(rows):
        failures.append("ancient-goods expansion art ledger is stale")
    if not CONTACT.is_file():
        failures.append("ancient-goods expansion contact sheet is missing")
    hashes: dict[str, str] = {}
    for sheet, (expected_hash, _keys) in SHEETS.items():
        path = SHEET_DIR / sheet
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
            failures.append(f"missing or changed reviewed atlas {path.relative_to(ROOT)}")
    for key, (filename, expected_hash) in sorted(DIRECT_SOURCES.items()):
        path = ROOT / "assets_queue/generated_sources" / filename
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
            failures.append(f"missing or changed reviewed direct source {path.relative_to(ROOT)}")
    keys = [key for key, _sheet, _cell in rows] + sorted(DIRECT_SOURCES)
    for key in keys:
        master = SOURCE_DIR / f"{key}.png"
        general = GENERAL_SOURCE_DIR / f"{key}.png"
        icon = GOODS_DIR / f"icon_goods_{key}.dds"
        wide = ILLUSTRATION_DIR / f"icon_goods_{key}.dds"
        for target in (master, general, icon, wide):
            if not target.is_file():
                failures.append(f"missing direct asset {target.relative_to(ROOT)}")
                continue
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
            previous = hashes.setdefault(digest, str(target.relative_to(ROOT)))
            if previous != str(target.relative_to(ROOT)) and target.suffix.lower() == ".dds":
                failures.append(f"duplicate direct DDS assets {previous} and {target.relative_to(ROOT)}")
        if master.is_file():
            with Image.open(master) as image:
                if image.mode != "RGBA" or image.size != (128, 128) or image.getpixel((0, 0))[3] != 0:
                    failures.append(f"invalid circle-safe master {master.relative_to(ROOT)}")
        if master.is_file() and (not general.is_file() or general.read_bytes() != master.read_bytes()):
            failures.append(f"missing or stale retained master {general.relative_to(ROOT)}")
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
        print(f"m5_ancient_goods_expansion: FAIL\n  - {exc}")
        return 1
    print(
        "m5_ancient_goods_expansion: PASS "
        f"({len(records()) + len(DIRECT_SOURCES)} direct goods from "
        f"{len(SHEETS)} reviewed atlases and {len(DIRECT_SOURCES)} reviewed direct source)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
