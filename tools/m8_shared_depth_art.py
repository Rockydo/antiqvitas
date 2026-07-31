#!/usr/bin/env python3
"""Build and validate twenty four-up sheets for the shared-depth advances."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from dds import convert, identify
from m8_knowledge import AGE_NAMES, DIRECT_ADVANCE_ART, advance_records
from m8_later_expansion_art import (
    CELLS,
    LEDGER_FIELDS,
    TRACK_OBJECTS,
    build_master,
    cell_box,
    paths,
    remove_green,
)


ROOT = Path(__file__).resolve().parents[1]
SHEET_DIR = ROOT / "assets_queue/generated_sources/s3_shared_advances"
MANIFEST = ROOT / "docs/m8/s3_shared_advance_art_manifest.csv"
CONTACT = ROOT / "docs/m8/s3_shared_advance_art_contact_sheet.png"
REFERENCE = ROOT / "assets_queue/references/vanilla_advance_style_reference.png"
EXPECTED_COUNT = 80
SHEET_CAPACITY = 4
MANIFEST_FIELDS = (
    "sheet", "cell", "key", "age", "track", "subject",
    "historical_brief", "source", "reference", "prompt",
)


def selected_records():
    records = tuple(
        record for record in advance_records()
        if record.key.startswith("antq_shared_")
    )
    if len(records) != EXPECTED_COUNT:
        raise ValueError(f"expected {EXPECTED_COUNT} shared-depth advances, got {len(records)}")
    return records


def sheet_path(index: int) -> Path:
    return SHEET_DIR / f"sheet_{index // SHEET_CAPACITY + 1:03}.png"


def prompt_for(records) -> str:
    lines = [
        "Use case: stylized-concept",
        "Asset type: exactly four separate Europa Universalis V advance-icon cutouts",
        "Primary request: Create four distinct archaeological still-life icon compositions in a clean 2x2 grid.",
        "Input image: the supplied image is an exact installed EU5 advance-icon reference. Match its crisp isolated-object rendering, realistic material detail, restrained natural color, edge treatment, transparent-cutout composition, and premium finish exactly.",
        "Scene/backdrop: perfectly flat solid #00ff00 chroma-key field in all four cells; no dividers, frames, texture, gradients, floor plane, or lighting variation in the green.",
        "Composition/framing: one centered and generously padded object cluster per quadrant. Keep all objects wholly inside their own quadrant with large clear gaps at the centre lines.",
        "Lighting/mood: neutral soft studio light, controlled highlights, authentic material colours. Absolutely no yellow, sepia, orange, or teal grading.",
    ]
    for cell, record in zip(CELLS, records, strict=True):
        lines.append(
            f"{cell.replace('_', ' ').title()}: {record.name}. "
            f"Compose an unmistakable cluster from historically appropriate "
            f"{TRACK_OBJECTS[record.track]}. Historical brief: {record.description}"
        )
    lines.extend((
        "Constraints: exactly four different icons; material culture appropriate to AD 1-476; visually distinguish all four by silhouette and materials; no repeated central object; no text, letters, numerals, maps, heraldry, portraits, people, modern objects, medieval plate armour, firearms, borders, badges, readable inscriptions, or watermark.",
        "Avoid: generic fantasy props, cheap yellow filter, muddy monochrome, crowded miniature scenes, full buildings, square picture backgrounds, drop shadows on the green, vignette, quadrant dividers, or any object crossing a quadrant boundary.",
    ))
    return "\n".join(lines)


def manifest_text(records) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=MANIFEST_FIELDS, lineterminator="\n")
    writer.writeheader()
    for start in range(0, len(records), SHEET_CAPACITY):
        group = records[start:start + SHEET_CAPACITY]
        prompt = prompt_for(group)
        for offset, record in enumerate(group):
            writer.writerow({
                "sheet": sheet_path(start).name,
                "cell": CELLS[offset],
                "key": record.key,
                "age": AGE_NAMES[record.age_index],
                "track": record.track,
                "subject": record.name,
                "historical_brief": record.description,
                "source": f"{record.source};P20",
                "reference": str(REFERENCE.relative_to(ROOT)).replace("\\", "/"),
                "prompt": prompt,
            })
    return stream.getvalue()


def ledger_rows() -> list[dict[str, str]]:
    with DIRECT_ADVANCE_ART.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != LEDGER_FIELDS:
            raise ValueError(f"direct art ledger must use {LEDGER_FIELDS}")
        return [
            {field: (row.get(field) or "").strip() for field in LEDGER_FIELDS}
            for row in reader
        ]


def write_ledger(records) -> None:
    keys = {record.key for record in records}
    rows = [row for row in ledger_rows() if row["key"] not in keys]
    for index, record in enumerate(records):
        rows.append({
            "key": record.key,
            "age": AGE_NAMES[record.age_index],
            "subject": record.name,
            "source": f"{record.source};P20",
            "confidence": "secure",
            "status": "complete",
            "note": (
                "Dedicated installed-EU5-referenced cutout; reviewed in S3 shared "
                f"four-up sheet {index // 4 + 1}, {CELLS[index % 4]}."
            ),
        })
    with DIRECT_ADVANCE_ART.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LEDGER_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def render_contact(records) -> None:
    columns, tile, label = 10, 112, 28
    rows = (len(records) + columns - 1) // columns
    canvas = Image.new("RGB", (columns * tile, rows * (tile + label)), "#101722")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    for index, record in enumerate(records):
        _source, master, _texture = paths(record.key)
        with Image.open(master) as image:
            preview = ImageOps.contain(
                image.convert("RGBA"), (tile - 4, tile - 4), Image.Resampling.LANCZOS
            )
        background = Image.new("RGB", (tile - 4, tile - 4), "#293341")
        background.paste(preview.convert("RGB"), (0, 0), preview.getchannel("A"))
        x = index % columns * tile
        y = index // columns * (tile + label)
        canvas.paste(background, (x + 2, y + 2))
        draw.text(
            (x + 3, y + tile + 1),
            f"{index + 1:02} {record.key.removeprefix('antq_shared_')[:17]}",
            fill="#e8e0d0",
            font=font,
        )
    CONTACT.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(CONTACT, format="PNG", optimize=True)


def write(records) -> None:
    opened: dict[Path, Image.Image] = {}
    try:
        for index, record in enumerate(records):
            sheet = sheet_path(index)
            if not sheet.is_file():
                raise ValueError(f"missing generated sheet {sheet.relative_to(ROOT)}")
            if sheet not in opened:
                opened[sheet] = Image.open(sheet).convert("RGB")
            crop = opened[sheet].crop(cell_box(opened[sheet].size, index))
            source_path, master_path, texture_path = paths(record.key)
            source_path.parent.mkdir(parents=True, exist_ok=True)
            master_path.parent.mkdir(parents=True, exist_ok=True)
            texture_path.parent.mkdir(parents=True, exist_ok=True)
            remove_green(crop).save(source_path, format="PNG", optimize=True)
            build_master(crop).save(master_path, format="PNG", optimize=True)
            convert(master_path, texture_path, "bc7", True)
    finally:
        for image in opened.values():
            image.close()
    write_ledger(records)
    render_contact(records)


def check(records) -> None:
    failures: list[str] = []
    actual_manifest = MANIFEST.read_text(encoding="utf-8-sig") if MANIFEST.is_file() else ""
    if actual_manifest != manifest_text(records):
        failures.append("shared advance-art manifest is stale")
    complete = {row["key"] for row in ledger_rows() if row["status"] == "complete"}
    hashes: dict[str, str] = {}
    for index, record in enumerate(records):
        sheet = sheet_path(index)
        source, master, texture = paths(record.key)
        if record.key not in complete:
            failures.append(f"direct art ledger is missing {record.key}")
        for path, role in ((sheet, "sheet"), (source, "source"), (master, "master"), (texture, "texture")):
            if not path.is_file():
                failures.append(f"missing {role} for {record.key}")
        if master.is_file():
            with Image.open(master) as image:
                rgba = image.convert("RGBA")
                bounds = rgba.getchannel("A").getbbox()
                if image.size != (256, 256) or bounds is None:
                    failures.append(f"invalid master for {record.key}")
                elif bounds[0] < 12 or bounds[1] < 12 or bounds[2] > 244 or bounds[3] > 244:
                    failures.append(f"unsafe circular framing for {record.key}: {bounds}")
                digest = hashlib.sha256(rgba.tobytes()).hexdigest()
            if digest in hashes:
                failures.append(f"visual alias: {hashes[digest]} and {record.key}")
            hashes[digest] = record.key
        if texture.is_file() and identify(texture) != {
            "format": "DDS", "width": "256", "height": "256",
            "depth": "8", "channels": "srgba 4.0",
        }:
            failures.append(f"invalid DDS for {record.key}")
    if len({sheet_path(index) for index in range(len(records))}) != 20:
        failures.append("shared advance art must use exactly twenty four-up sheets")
    if not REFERENCE.is_file():
        failures.append("installed EU5 advance reference is missing")
    if not CONTACT.is_file():
        failures.append("shared advance-art contact sheet is missing")
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
        records = selected_records()
        if args.manifest:
            MANIFEST.parent.mkdir(parents=True, exist_ok=True)
            MANIFEST.write_text(manifest_text(records), encoding="utf-8")
            print("m8_shared_depth_art: wrote twenty four-up prompts")
        elif args.write:
            write(records)
            print("m8_shared_depth_art: wrote 80 direct advance assets")
        else:
            check(records)
            print("m8_shared_depth_art: OK")
    except (OSError, ValueError) as error:
        print("m8_shared_depth_art: FAIL")
        print(error)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
