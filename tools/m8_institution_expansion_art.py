#!/usr/bin/env python3
"""Build and validate four-up direct art for S2-P3's new institutions."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from dds import convert, identify
from m8_knowledge import INSTITUTION_DATA
from m8_later_expansion_art import CELLS, cell_box, remove_green


ROOT = Path(__file__).resolve().parents[1]
SHEET_DIR = ROOT / "assets_queue/generated_sources/s2_p3_institutions"
SOURCE_DIR = ROOT / "assets_queue/generated_sources"
MASTER_DIR = ROOT / "assets_queue/generated"
TEXTURE_DIR = ROOT / "main_menu/gfx/interface/icons/institutions"
REFERENCE = ROOT / "assets_queue/references/vanilla_institution_style_reference.png"
MANIFEST = ROOT / "docs/m8/s2_p3_institution_art_manifest.csv"
CONTACT = ROOT / "docs/m8/s2_p3_institution_art_contact_sheet.png"
MANIFEST_FIELDS = (
    "sheet", "cell", "key", "name", "age", "subject", "source",
    "reference", "prompt",
)
EXISTING_KEYS = {
    "antq_hellenism", "antq_roman_law_engineering",
    "antq_han_bureaucratic_statecraft", "antq_buddhist_monasticism",
    "antq_cataphract_warfare", "antq_papermaking",
    "antq_christian_monasticism", "antq_theological_orthodoxy",
    "antq_foederati_statecraft",
}
FILLERS = (
    ("calibration_seal", "plain late-antique bronze seal box and cord"),
    ("calibration_route", "plain wooden route marker, small weight, and cord"),
    ("calibration_lamp", "plain ceramic oil lamp and closed unmarked tablet"),
)


def new_items():
    result = tuple(item for item in INSTITUTION_DATA if item.key not in EXISTING_KEYS)
    if len(result) != 21:
        raise ValueError(f"S2-P3 institution art requires 21 new items, got {len(result)}")
    return result


def sheet_path(index: int) -> Path:
    return SHEET_DIR / f"sheet_{index // 4 + 1:02}.png"


def paths(key: str) -> tuple[Path, Path, Path]:
    slug = key.removeprefix("antq_")
    return (
        SOURCE_DIR / f"antq_institution_{slug}_source.png",
        MASTER_DIR / f"antq_institution_{slug}_128.png",
        TEXTURE_DIR / f"{key}.dds",
    )


def prompt_for(group) -> str:
    entries = list(group)
    while len(entries) < 4:
        filler_key, filler_subject = FILLERS[len(entries) - len(group)]
        entries.append((filler_key, filler_subject, "Late-antique style calibration object."))
    lines = [
        "Use case: stylized-concept",
        "Asset type: four separate Europa Universalis V institution-icon cutouts",
        "Primary request: Create exactly four distinct emblematic institution icons in a clean 2x2 grid.",
        "Input image: the supplied contact strip contains exact installed EU5 institution icons; match their crisp isolated-object rendering, high material realism, compact silhouette, neutral lighting, and premium native-game finish.",
        "Scene/backdrop: perfectly flat solid #00ff00 chroma-key field in all four quadrants; no dividers, frames, floor, texture, gradients, or shadows on the field.",
        "Composition/framing: one bold centered symbol or compact cluster of at most three objects per quadrant; generous padding; no object crossing a quadrant boundary.",
        "Color/lighting: authentic material colors and neutral soft studio light; no sepia, yellow wash, or generic fantasy glow.",
    ]
    for cell, entry in zip(CELLS, entries, strict=True):
        if isinstance(entry, tuple):
            _key, subject, description = entry
            name = subject
        else:
            name = entry.name
            description = entry.description
        lines.append(
            f"{cell.replace('_', ' ').title()}: {name}. "
            f"Choose one historically grounded emblematic object composition. "
            f"Historical brief: {description}"
        )
    lines.extend((
        "Constraints: exactly four different icons; AD 1-476 objects only; distinguish each region and pathway materially; no text, letters, numerals, glyphs, flags, maps, heraldry, portraits, hands, readable inscriptions, modern objects, medieval plate armour, firearms, watermark, borders, or badges.",
        "Avoid: generic scroll-and-coin repetition, cheap yellow filter, muddy monochrome, fantasy props, crowded scenes, buildings as backgrounds, square picture panels, vignette, or repeated silhouettes.",
    ))
    return "\n".join(lines)


def manifest_text(items) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=MANIFEST_FIELDS, lineterminator="\n")
    writer.writeheader()
    for start in range(0, len(items), 4):
        group = items[start:start + 4]
        prompt = prompt_for(group)
        for offset, item in enumerate(group):
            writer.writerow({
                "sheet": f"sheet_{start // 4 + 1:02}.png",
                "cell": CELLS[offset],
                "key": item.key,
                "name": item.name,
                "age": item.age,
                "subject": item.description,
                "source": f"{item.source};P20",
                "reference": str(REFERENCE.relative_to(ROOT)).replace("\\", "/"),
                "prompt": prompt,
            })
    return buffer.getvalue()


def build_master(crop: Image.Image) -> Image.Image:
    keyed = remove_green(crop)
    bounds = keyed.getchannel("A").getbbox()
    if bounds is None:
        raise ValueError("chroma-keyed institution cell is empty")
    subject = keyed.crop(bounds)
    subject.thumbnail((110, 110), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    canvas.alpha_composite(
        subject, ((128 - subject.width) // 2, (128 - subject.height) // 2)
    )
    return canvas


def render_contact(items) -> None:
    columns = 7
    tile = 144
    rows = (len(items) + columns - 1) // columns
    canvas = Image.new("RGB", (columns * tile, rows * (tile + 22)), "#111925")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    for index, item in enumerate(items):
        _source, master, _texture = paths(item.key)
        with Image.open(master) as image:
            preview = ImageOps.contain(image.convert("RGBA"), (128, 128))
        x = index % columns * tile
        y = index // columns * (tile + 22)
        canvas.paste(preview.convert("RGB"), (x + 8, y + 8), preview.getchannel("A"))
        draw.text((x + 4, y + 140), item.key[5:25], fill="#e7dfce", font=font)
    CONTACT.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(CONTACT, format="PNG", optimize=True)


def write(items) -> None:
    for directory in (SOURCE_DIR, MASTER_DIR, TEXTURE_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    opened: dict[Path, Image.Image] = {}
    try:
        for index, item in enumerate(items):
            sheet = sheet_path(index)
            if not sheet.is_file():
                raise ValueError(f"missing institution four-up sheet {sheet.relative_to(ROOT)}")
            if sheet not in opened:
                opened[sheet] = Image.open(sheet).convert("RGB")
            crop = opened[sheet].crop(cell_box(opened[sheet].size, index))
            source, master, texture = paths(item.key)
            keyed = remove_green(crop)
            keyed.save(source, format="PNG", optimize=True)
            build_master(crop).save(master, format="PNG", optimize=True)
            convert(master, texture, "bc7", True)
    finally:
        for image in opened.values():
            image.close()
    render_contact(items)


def check(items) -> None:
    failures: list[str] = []
    expected_manifest = manifest_text(items)
    actual_manifest = (
        MANIFEST.read_text(encoding="utf-8-sig") if MANIFEST.is_file() else ""
    )
    if actual_manifest != expected_manifest:
        failures.append("S2-P3 institution-art manifest is stale")
    hashes: dict[str, str] = {}
    for index, item in enumerate(items):
        sheet = sheet_path(index)
        source, master, texture = paths(item.key)
        for path, role in (
            (sheet, "sheet"), (source, "source"),
            (master, "master"), (texture, "texture"),
        ):
            if not path.is_file():
                failures.append(f"missing institution {role}: {path.relative_to(ROOT)}")
        if master.is_file():
            with Image.open(master) as image:
                rgba = image.convert("RGBA")
                bounds = rgba.getchannel("A").getbbox()
                if image.format != "PNG" or image.size != (128, 128):
                    failures.append(f"invalid institution master {item.key}")
                if bounds is None or bounds[0] < 8 or bounds[1] < 8 or bounds[2] > 120 or bounds[3] > 120:
                    failures.append(f"unsafe institution framing {item.key}: {bounds}")
                if rgba.getchannel("A").getpixel((0, 0)):
                    failures.append(f"opaque institution corner {item.key}")
                digest = hashlib.sha256(rgba.tobytes()).hexdigest()
            if digest in hashes:
                failures.append(f"institution visual alias: {hashes[digest]} and {item.key}")
            hashes[digest] = item.key
        if texture.is_file():
            expected = {
                "format": "DDS", "width": "128", "height": "128",
                "depth": "8", "channels": "srgba 4.0",
            }
            details = identify(texture)
            if details != expected:
                failures.append(f"invalid institution DDS {item.key}: {details}")
    if len({sheet_path(index) for index in range(len(items))}) != 6:
        failures.append("21 institution icons must use six four-up source sheets")
    if not REFERENCE.is_file():
        failures.append("installed EU5 institution reference is missing")
    if not CONTACT.is_file():
        failures.append("institution contact sheet is missing")
    if failures:
        raise ValueError("\n".join(failures))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if sum((args.manifest, args.write, args.check)) != 1:
        parser.error("provide exactly one mode")
    try:
        items = new_items()
        if args.manifest:
            MANIFEST.parent.mkdir(parents=True, exist_ok=True)
            MANIFEST.write_text(manifest_text(items), encoding="utf-8")
            print("m8_institution_expansion_art: wrote six four-up prompts")
            return 0
        if args.write:
            write(items)
        check(items)
    except (OSError, ValueError, csv.Error) as exc:
        print(f"m8_institution_expansion_art: FAIL\n  - {exc}")
        return 1
    print(
        "m8_institution_expansion_art: PASS "
        "(21 direct BC7 icons from six installed-EU5-referenced four-up sheets)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
