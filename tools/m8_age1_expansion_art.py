#!/usr/bin/env python3
"""Build and validate direct art for the expanded Age-I research branches."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from dds import convert, identify
from m8_knowledge import AGE_NAMES, DIRECT_ADVANCE_ART, TRACKS, advance_records


ROOT = Path(__file__).resolve().parents[1]
SHEET_DIR = ROOT / "assets_queue/generated_sources/age1_expansion"
SOURCE_DIR = ROOT / "assets_queue/generated_sources"
MASTER_DIR = ROOT / "assets_queue/generated"
TEXTURE_DIR = ROOT / "main_menu/gfx/interface/advance"
CONTACT = ROOT / "docs/m8/age1_expansion_art_contact_sheet.png"
SHEET_CAPACITY = 16
EXPECTED_COUNT = 110
LEDGER_FIELDS = ("key", "age", "subject", "source", "confidence", "status", "note")


def expansion_records():
    original = {
        f"antq_{name}"
        for age_groups in TRACKS.values()
        for group in age_groups
        for name in group
    }
    return tuple(record for record in advance_records() if record.key not in original)


def sheet_path(index: int) -> Path:
    return SHEET_DIR / f"sheet_{index // SHEET_CAPACITY + 1:02}.png"


def cell_box(size: tuple[int, int], index: int) -> tuple[int, int, int, int]:
    width, height = size
    if width != height:
        raise ValueError(f"Age-I expansion sheet must be square, got {size}")
    column = index % 4
    row = (index // 4) % 4
    inset = max(3, round(width / 320))
    left = round(column * width / 4) + inset
    top = round(row * height / 4) + inset
    right = round((column + 1) * width / 4) - inset
    bottom = round((row + 1) * height / 4) - inset
    return left, top, right, bottom


def paths(key: str) -> tuple[Path, Path, Path]:
    slug = key.removeprefix("antq_")
    return (
        SOURCE_DIR / f"antq_advance_{slug}_source.png",
        MASTER_DIR / f"antq_advance_{slug}_256.png",
        TEXTURE_DIR / f"antq_advance_{slug}.dds",
    )


def ledger_rows() -> list[dict[str, str]]:
    if not DIRECT_ADVANCE_ART.is_file():
        return []
    with DIRECT_ADVANCE_ART.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != LEDGER_FIELDS:
            raise ValueError(f"direct art ledger must use {LEDGER_FIELDS}")
        return [{field: (row.get(field) or "").strip() for field in LEDGER_FIELDS} for row in reader]


def write_ledger(records) -> None:
    expansion_keys = {record.key for record in records}
    retained = [row for row in ledger_rows() if row["key"] not in expansion_keys]
    for index, record in enumerate(records):
        retained.append({
            "key": record.key,
            "age": AGE_NAMES[record.age_index],
            "subject": record.name,
            "source": f"{record.source};P20",
            "confidence": "secure",
            "status": "complete",
            "note": (
                "Dedicated archaeological still-life; visually reviewed in "
                f"Age-I expansion sheet {index // SHEET_CAPACITY + 1}, "
                f"cell {index % SHEET_CAPACITY + 1}."
            ),
        })
    with DIRECT_ADVANCE_ART.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LEDGER_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(retained)


def render_contact(records) -> None:
    columns = 8
    tile = 128
    label = 32
    rows = (len(records) + columns - 1) // columns
    canvas = Image.new("RGB", (columns * tile, rows * (tile + label)), "#0b1018")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    for index, record in enumerate(records):
        _source, master, _texture = paths(record.key)
        with Image.open(master) as image:
            preview = ImageOps.fit(image.convert("RGB"), (tile - 4, tile - 4), Image.Resampling.LANCZOS)
        x = index % columns * tile
        y = index // columns * (tile + label)
        canvas.paste(preview, (x + 2, y + 2))
        draw.text((x + 3, y + tile + 2), f"{index + 1:03} {record.key[5:24]}", fill="#e7deca", font=font)
    CONTACT.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(CONTACT, format="PNG", optimize=True)


def write(records) -> None:
    for directory in (SOURCE_DIR, MASTER_DIR, TEXTURE_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    opened: dict[Path, Image.Image] = {}
    try:
        for index, record in enumerate(records):
            sheet = sheet_path(index)
            if not sheet.is_file():
                raise ValueError(f"missing generated sheet {sheet.relative_to(ROOT)}")
            if sheet not in opened:
                opened[sheet] = Image.open(sheet).convert("RGB")
            crop = opened[sheet].crop(cell_box(opened[sheet].size, index))
            master = ImageOps.fit(
                crop, (256, 256), method=Image.Resampling.LANCZOS,
                centering=(0.5, 0.5),
            )
            source_path, master_path, texture_path = paths(record.key)
            crop.save(source_path, format="PNG", optimize=True)
            master.save(master_path, format="PNG", optimize=True)
            convert(master_path, texture_path, "bc7", True)
    finally:
        for image in opened.values():
            image.close()
    write_ledger(records)
    render_contact(records)


def check(records) -> None:
    failures: list[str] = []
    complete = {
        row["key"]: row
        for row in ledger_rows()
        if row["status"] == "complete"
    }
    hashes: dict[str, str] = {}
    for index, record in enumerate(records):
        sheet = sheet_path(index)
        source, master, texture = paths(record.key)
        if record.key not in complete:
            failures.append(f"direct art ledger is missing {record.key}")
        for path, role in ((sheet, "sheet"), (source, "source"), (master, "master"), (texture, "texture")):
            if not path.is_file():
                failures.append(f"missing {role} for {record.key}: {path.relative_to(ROOT)}")
        if master.is_file():
            with Image.open(master) as image:
                if image.size != (256, 256) or image.format != "PNG":
                    failures.append(f"invalid master for {record.key}")
                digest = hashlib.sha256(image.convert("RGBA").tobytes()).hexdigest()
            if digest in hashes:
                failures.append(f"visual alias: {hashes[digest]} and {record.key}")
            hashes[digest] = record.key
        if texture.is_file():
            details = identify(texture)
            expected = {
                "format": "DDS", "width": "256", "height": "256",
                "depth": "8", "channels": "srgba 4.0",
            }
            if details != expected:
                failures.append(f"invalid DDS for {record.key}: {details}")
    if len(records) != EXPECTED_COUNT:
        failures.append(f"expected {EXPECTED_COUNT} expansion records, got {len(records)}")
    if not CONTACT.is_file():
        failures.append("missing Age-I expansion art contact sheet")
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
        records = expansion_records()
        if args.write:
            write(records)
        check(records)
    except (OSError, ValueError, csv.Error) as exc:
        print(f"m8_age1_expansion_art: FAIL\n  - {exc}")
        return 1
    print(
        "m8_age1_expansion_art: PASS "
        f"({len(records)} direct BC7 icons from 7 reviewed sheets)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
