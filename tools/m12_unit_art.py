#!/usr/bin/env python3
"""Build and validate direct EU5 recruitment illustrations for all ancient units."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from dds import convert, identify


ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "docs/m7/units.csv"
QUARANTINE = ROOT / "docs/m12/unit_quarantine_manifest.json"
SOURCE_DIR = ROOT / "assets_queue/generated/unit_icons/sheets"
MASTER_DIR = ROOT / "assets_queue/generated/unit_icons/masters"
STRIP_DIR = ROOT / "assets_queue/generated/unit_icons/strips"
MASK_SOURCE_DIR = ROOT / "assets_queue/generated/unit_icons/masks"
TEXTURE_DIR = ROOT / "main_menu/gfx/interface/illustrations/units"
MASK_DIR = TEXTURE_DIR / "masks"
LEDGER = ROOT / "docs/m12/unit_art_ledger.csv"
CONTACT_SHEET = ROOT / "docs/m12/unit_art_contact_sheet.png"
MASTER_SIZE = (1024, 1024)
STRIP_SIZE = (1080, 440)
FRAME_SIZE = (360, 440)
QUADRANTS = ("top_left", "top_right", "bottom_left", "bottom_right")


@dataclass(frozen=True)
class Sheet:
    filename: str
    keys: tuple[str, str, str, str]


SHEETS = (
    Sheet("unit_sheet_01_roman_core.png", (
        "antq_legionaries", "antq_auxilia", "antq_roman_alae", "antq_roman_marines",
    )),
    Sheet("unit_sheet_02_roman_specialists.png", (
        "antq_roman_sagittarii", "antq_roman_scouts", "antq_comitatenses", "antq_limitanei",
    )),
    Sheet("unit_sheet_03_hellenistic.png", (
        "antq_thureophoroi", "antq_hellenistic_phalanx", "antq_cretan_archers", "antq_thracian_peltasts",
    )),
    Sheet("unit_sheet_04_germanic.png", (
        "antq_warbands", "antq_germanic_horse", "antq_germanic_spearmen", "antq_germanic_javelins",
    )),
    Sheet("unit_sheet_05_western_mercenaries.png", (
        "antq_germanic_bodyguards", "antq_galatian_swordsmen", "antq_iberian_swordsmen", "antq_dacian_falxmen",
    )),
    Sheet("unit_sheet_06_han_india_nubia.png", (
        "antq_han_crossbow_infantry", "antq_indian_longbowmen", "antq_war_elephants", "antq_nubian_archers",
    )),
    Sheet("unit_sheet_07_iranian_steppe.png", (
        "antq_cataphracts", "antq_parthian_horse_archers", "antq_steppe_horse_archers", "antq_saka_horse",
    )),
    Sheet("unit_sheet_08_africa_arabia_britain.png", (
        "antq_numidian_light_horse", "antq_camelry", "antq_british_chariots", "antq_numidian_horse_company",
    )),
    Sheet("unit_sheet_09_eastern_specialists.png", (
        "antq_parthian_foot_archers", "antq_parthian_noble_lancers", "antq_syrian_archers", "antq_armenian_horse",
    )),
    Sheet("unit_sheet_10_mediterranean_navy.png", (
        "antq_liburnian", "antq_trireme", "antq_quinquereme", "antq_merchant_roundship",
    )),
    Sheet("unit_sheet_11_ocean_coastal.png", (
        "antq_monsoon_dhow", "antq_austronesian_outrigger", "antq_cilician_marines", "antq_balearic_slingers",
    )),
    Sheet("unit_sheet_12_britain_hibernia.png", (
        "antq_british_hillfort_spearmen", "antq_northern_british_skirmishers",
        "antq_hibernian_javelin_bands", "antq_hibernian_coastal_warbands",
    )),
)

CATEGORY_SUFFIXES = (
    ("heavy_infantry", "army_heavy_infantry"),
    ("light_infantry", "army_light_infantry"),
    ("heavy_cavalry", "army_heavy_cavalry"),
    ("light_cavalry", "army_light_cavalry"),
    ("light_ship", "navy_light_ship"),
    ("heavy_ship", "navy_heavy_ship"),
    ("transport", "navy_transport"),
    ("galley", "navy_galley"),
)
LEDGER_FIELDS = (
    "key", "name", "kind", "status", "age", "category", "sheet", "quadrant",
    "master", "strip", "texture", "mask", "dimensions", "compression",
    "resolver", "source", "confidence", "note",
)


def roster() -> dict[str, dict[str, str]]:
    with ROSTER.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    result = {row["key"]: row for row in rows}
    if len(result) != len(rows):
        raise ValueError("M7 unit roster contains duplicate keys")
    return result


def category(copy_from: str) -> str:
    for suffix, value in CATEGORY_SUFFIXES:
        if copy_from.endswith(suffix):
            return value
    raise ValueError(f"no recruitment-art category mapping for {copy_from}")


def art_index() -> dict[str, tuple[Sheet, str]]:
    result: dict[str, tuple[Sheet, str]] = {}
    for sheet in SHEETS:
        if len(sheet.keys) != 4:
            raise ValueError(f"{sheet.filename} does not map exactly four icons")
        for quadrant, key in zip(QUADRANTS, sheet.keys, strict=True):
            if key in result:
                raise ValueError(f"unit art mapping repeats {key}")
            result[key] = (sheet, quadrant)
    return result


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def destinations(row: dict[str, str]) -> tuple[Path, Path, Path, Path]:
    cat = category(row["copy_from"])
    basename = f"{cat}_{row['key']}"
    return (
        MASTER_DIR / f"{row['key']}.png",
        STRIP_DIR / f"{basename}_1080x440.png",
        TEXTURE_DIR / f"{basename}.dds",
        MASK_DIR / f"{basename}.dds",
    )


def quadrant_box(size: tuple[int, int], quadrant: str) -> tuple[int, int, int, int]:
    width, height = size
    if width != height or width % 2 or height % 2:
        raise ValueError(f"four-up source must be square with even dimensions, got {size}")
    half_x, half_y = width // 2, height // 2
    inset = 4
    boxes = {
        "top_left": (inset, inset, half_x - inset, half_y - inset),
        "top_right": (half_x + inset, inset, width - inset, half_y - inset),
        "bottom_left": (inset, half_y + inset, half_x - inset, height - inset),
        "bottom_right": (half_x + inset, half_y + inset, width - inset, height - inset),
    }
    return boxes[quadrant]


def build_master(source: Image.Image, quadrant: str) -> Image.Image:
    crop = source.crop(quadrant_box(source.size, quadrant))
    return ImageOps.fit(
        crop.convert("RGB"), MASTER_SIZE, method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    )


def build_strip(master: Image.Image) -> Image.Image:
    frame = ImageOps.fit(
        master, FRAME_SIZE, method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.48),
    )
    strip = Image.new("RGB", STRIP_SIZE)
    for index in range(3):
        strip.paste(frame, (index * FRAME_SIZE[0], 0))
    return strip


def ledger_rows(rows: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    index = art_index()
    output: list[dict[str, str]] = []
    for key in sorted(rows):
        row = rows[key]
        sheet, quadrant = index[key]
        master, strip, texture, mask = destinations(row)
        output.append({
            "key": key,
            "name": row["name"],
            "kind": row["kind"],
            "status": "complete",
            "age": row["age"],
            "category": category(row["copy_from"]),
            "sheet": relative(SOURCE_DIR / sheet.filename),
            "quadrant": quadrant,
            "master": relative(master),
            "strip": relative(strip),
            "texture": relative(texture),
            "mask": relative(mask),
            "dimensions": "1080x440; 3x360x440 frames",
            "compression": "DXT1 + full mip chain",
            "resolver": "[unit_category]_[unit_type] (direct priority 2)",
            "source": row["source"],
            "confidence": row["confidence"],
            "note": row["note"],
        })
    return output


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LEDGER_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_contact_sheet(rows: dict[str, dict[str, str]]) -> None:
    columns, tile_width, image_height, label_height = 4, 260, 286, 42
    ordered = sorted(rows)
    line_count = (len(ordered) + columns - 1) // columns
    canvas = Image.new("RGB", (columns * tile_width, line_count * (image_height + label_height)), "#101723")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    for index, key in enumerate(ordered):
        x = (index % columns) * tile_width
        y = (index // columns) * (image_height + label_height)
        master, _strip, _texture, _mask = destinations(rows[key])
        with Image.open(master) as source:
            preview = ImageOps.fit(source.convert("RGB"), (tile_width - 8, image_height - 8), Image.Resampling.LANCZOS)
        canvas.paste(preview, (x + 4, y + 4))
        draw.text((x + 6, y + image_height + 4), rows[key]["name"], fill="#f0e7cf", font=font)
        draw.text((x + 6, y + image_height + 20), key, fill="#aebbc9", font=font)
    CONTACT_SHEET.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(CONTACT_SHEET, format="PNG", optimize=True)


def write() -> None:
    rows = roster()
    index = art_index()
    expected = set(rows)
    if set(index) != expected:
        raise ValueError(
            f"four-up mappings differ from M7 roster: missing={sorted(expected - set(index))}; "
            f"extra={sorted(set(index) - expected)}"
        )
    for directory in (MASTER_DIR, STRIP_DIR, MASK_SOURCE_DIR, TEXTURE_DIR, MASK_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    opened: dict[str, Image.Image] = {}
    try:
        for key, row in rows.items():
            sheet, quadrant = index[key]
            if sheet.filename not in opened:
                source_path = SOURCE_DIR / sheet.filename
                if not source_path.is_file():
                    raise ValueError(f"missing generated four-up source {source_path}")
                opened[sheet.filename] = Image.open(source_path).convert("RGB")
            master_image = build_master(opened[sheet.filename], quadrant)
            strip_image = build_strip(master_image)
            master, strip, texture, mask = destinations(row)
            mask_source = MASK_SOURCE_DIR / f"{category(row['copy_from'])}_{key}_mask_1080x440.png"
            master_image.save(master, format="PNG", optimize=True)
            strip_image.save(strip, format="PNG", optimize=True)
            Image.new("RGB", STRIP_SIZE, "black").save(mask_source, format="PNG", optimize=True)
            convert(strip, texture, "dxt1", mipmaps=True)
            convert(mask_source, mask, "dxt1", mipmaps=True)
    finally:
        for image in opened.values():
            image.close()
    write_csv(LEDGER, ledger_rows(rows))
    write_contact_sheet(rows)
    print(f"m12_unit_art: wrote {len(rows)} direct illustrations + masks from {len(SHEETS)} four-up sources")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate() -> bool:
    failures: list[str] = []
    try:
        rows = roster()
        index = art_index()
        manifest = json.loads(QUARANTINE.read_text(encoding="utf-8-sig"))
        active = set(manifest["active_custom_definitions"])
        if set(rows) != active:
            failures.append("M7 art roster differs from active unit-quarantine definitions")
        if set(index) != active:
            failures.append("four-up unit-art mapping does not exactly cover active ancient units")
        if len(SHEETS) != 12 or sum(len(sheet.keys) for sheet in SHEETS) != 48:
            failures.append("unit-art source contract is not 12 sheets / 48 icons")
        for sheet in SHEETS:
            path = SOURCE_DIR / sheet.filename
            if not path.is_file():
                failures.append(f"missing four-up source {relative(path)}")
                continue
            with Image.open(path) as image:
                if image.format != "PNG" or image.size[0] != image.size[1] or image.size[0] % 2:
                    failures.append(f"invalid four-up source geometry {relative(path)}")
        expected_ledger = ledger_rows(rows)
        if not LEDGER.is_file():
            failures.append(f"missing {relative(LEDGER)}")
        else:
            with LEDGER.open(encoding="utf-8-sig", newline="") as handle:
                actual_ledger = list(csv.DictReader(handle))
            if actual_ledger != expected_ledger:
                failures.append(f"stale {relative(LEDGER)}")
        texture_hashes: set[str] = set()
        for key, row in rows.items():
            master, strip, texture, mask = destinations(row)
            mask_source = MASK_SOURCE_DIR / f"{category(row['copy_from'])}_{key}_mask_1080x440.png"
            for path, dimensions in (
                (master, MASTER_SIZE), (strip, STRIP_SIZE), (mask_source, STRIP_SIZE),
            ):
                if not path.is_file():
                    failures.append(f"missing {relative(path)}")
                    continue
                with Image.open(path) as image:
                    if image.format != "PNG" or image.size != dimensions:
                        failures.append(f"wrong PNG format/size: {relative(path)}")
            for path in (texture, mask):
                if not path.is_file():
                    failures.append(f"missing {relative(path)}")
                    continue
                details = identify(path)
                expected_details = {
                    "format": "DDS", "width": "1080", "height": "440", "depth": "8",
                }
                if (
                    {key: details[key] for key in expected_details} != expected_details
                    or "".join(details["channels"].split()) != "srgb3.0"
                ):
                    failures.append(f"wrong DDS contract: {relative(path)} = {details}")
            if texture.is_file():
                digest = sha256(texture)
                if digest in texture_hashes:
                    failures.append(f"direct unit illustration is aliased: {relative(texture)}")
                texture_hashes.add(digest)
        if not CONTACT_SHEET.is_file():
            failures.append(f"missing {relative(CONTACT_SHEET)}")
        else:
            with Image.open(CONTACT_SHEET) as image:
                if image.format != "PNG" or image.width < 1000 or image.height < 3000:
                    failures.append(f"invalid contact sheet {relative(CONTACT_SHEET)}")
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        failures.append(str(exc))
    if failures:
        print("m12_unit_art: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return False
    print("m12_unit_art: PASS (48 unique direct recruitment illustrations; 48 direct masks; zero fallbacks)")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.write:
            write()
            return 0
        return 0 if validate() else 1
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"m12_unit_art: FAIL\n  - {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
