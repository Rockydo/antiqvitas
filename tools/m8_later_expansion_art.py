#!/usr/bin/env python3
"""Build and validate S2-P3's keyed later-advance art archive."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from dds import convert, identify
from m8_knowledge import AGE_NAMES, DIRECT_ADVANCE_ART, advance_records
from m8_regional_depth import LATER_THEMES, branch_names


ROOT = Path(__file__).resolve().parents[1]
SHEET_DIR = ROOT / "assets_queue/generated_sources/s2_p3_advances"
SOURCE_DIR = ROOT / "assets_queue/generated_sources"
MASTER_DIR = ROOT / "assets_queue/generated"
TEXTURE_DIR = ROOT / "main_menu/gfx/interface/advance"
MANIFEST = ROOT / "docs/m8/s2_p3_advance_art_manifest.csv"
CONTACT = ROOT / "docs/m8/s2_p3_advance_art_contact_sheet.png"
REFERENCE = ROOT / "assets_queue/references/vanilla_advance_style_reference.png"
EXPECTED_ACTIVE_COUNT = 395
EXPECTED_ARCHIVE_COUNT = 440
EXPECTED_SHEET_COUNT = 110
SHEET_CAPACITY = 4
LEDGER_FIELDS = ("key", "age", "subject", "source", "confidence", "status", "note")
MANIFEST_FIELDS = (
    "sheet", "cell", "key", "age", "track", "profile", "subject",
    "historical_brief", "source", "reference", "prompt",
)
CELLS = ("top_left", "top_right", "bottom_left", "bottom_right")


TRACK_OBJECTS = {
    "statecraft": "seals, tally sticks, document tablets, weights, and council tokens",
    "warfare": "period weapons, armour fittings, remount gear, route markers, and ration vessels",
    "exchange": "weights, containers, route objects, coins or weighed media, cordage, and cargo seals",
    "learning": "writing materials where attested, teaching objects, instruments, models, and catalogued specimens",
    "society": "household, ritual, charitable, assembly, craft, and settlement objects",
}


def later_keys() -> set[str]:
    return {
        f"antq_{name}"
        for (track, _profile), themes in LATER_THEMES.items()
        for theme in themes
        for name in branch_names(theme, track)
    }


def expansion_records():
    keys = later_keys()
    reviewed = {
        row["key"] for row in ledger_rows()
        if "S2-P3 four-up sheet" in row["note"]
    }
    records = tuple(
        record for record in advance_records()
        if record.key in keys and record.key in reviewed
    )
    if len(records) != EXPECTED_ACTIVE_COUNT:
        raise ValueError(
            "S2-P3 keyed later-art selection must cover "
            f"{EXPECTED_ACTIVE_COUNT} active records exactly"
        )
    return records


def manifest_rows() -> list[dict[str, str]]:
    if not MANIFEST.is_file():
        return []
    with MANIFEST.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != MANIFEST_FIELDS:
            raise ValueError(f"advance-art manifest must use {MANIFEST_FIELDS}")
        return [dict(row) for row in reader]


def sheet_path(index: int) -> Path:
    return SHEET_DIR / f"sheet_{index // SHEET_CAPACITY + 1:03}.png"


def cell_box(size: tuple[int, int], index: int) -> tuple[int, int, int, int]:
    width, height = size
    if width != height or width < 1024 or width % 2:
        raise ValueError(f"S2-P3 four-up sheet must be even square >=1024, got {size}")
    cell = index % SHEET_CAPACITY
    column = cell % 2
    row = cell // 2
    return (
        column * width // 2,
        row * height // 2,
        (column + 1) * width // 2,
        (row + 1) * height // 2,
    )


def paths(key: str) -> tuple[Path, Path, Path]:
    slug = key.removeprefix("antq_")
    return (
        SOURCE_DIR / f"antq_advance_{slug}_source.png",
        MASTER_DIR / f"antq_advance_{slug}_256.png",
        TEXTURE_DIR / f"antq_advance_{slug}.dds",
    )


def prompt_for(records) -> str:
    lines = [
        "Use case: stylized-concept",
        "Asset type: four separate Europa Universalis V advance-icon cutouts",
        "Primary request: Create exactly four distinct archaeological still-life icon compositions in a clean 2x2 grid.",
        "Input image: the supplied image is an exact installed EU5 advance-icon style reference; match its crisp isolated-object rendering, realistic material detail, natural color, edge treatment, and transparent-cutout composition.",
        "Scene/backdrop: perfectly flat solid #00ff00 chroma-key field in all four cells; no dividers, frames, shadows on the field, gradients, texture, floor plane, or lighting variation.",
        "Style/medium: premium EU5-native painted-realistic object cutouts, not a generic fantasy-game icon, not a miniature scene.",
        "Composition/framing: one centered, generously padded cluster per quadrant; keep every object wholly inside its quadrant and visually separated from the other three.",
        "Lighting/mood: neutral soft studio light with controlled highlights; authentic material colors; no sepia or yellow filter.",
    ]
    for cell, record in zip(CELLS, records, strict=True):
        lines.append(
            f"{cell.replace('_', ' ').title()}: {record.name}. "
            f"Use historically appropriate {TRACK_OBJECTS[record.track]}. "
            f"Historical brief: {record.description}"
        )
    lines.extend((
        "Constraints: exactly four different icons; AD 96-476 material culture only; use region-specific objects and construction; no repeated composition; no text, letters, numerals, glyphs, flags, maps, heraldry, portraits, borders, badges, coins with readable inscriptions, modern objects, medieval plate armour, firearms, or watermark.",
        "Avoid: cheap yellow grading, muddy monochrome, generic fantasy props, crowded tableaux, people, architecture filling the cell, square picture backgrounds, drop shadows, vignette, or objects crossing quadrant boundaries.",
    ))
    return "\n".join(lines)


def manifest_text(records) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=MANIFEST_FIELDS, lineterminator="\n")
    writer.writeheader()
    for sheet_start in range(0, len(records), SHEET_CAPACITY):
        group = records[sheet_start:sheet_start + SHEET_CAPACITY]
        if len(group) != SHEET_CAPACITY:
            raise ValueError("S2-P3 advance art must divide into complete four-up sheets")
        prompt = prompt_for(group)
        for offset, record in enumerate(group):
            writer.writerow({
                "sheet": f"sheet_{sheet_start // SHEET_CAPACITY + 1:03}.png",
                "cell": CELLS[offset],
                "key": record.key,
                "age": AGE_NAMES[record.age_index],
                "track": record.track,
                "profile": record.profile,
                "subject": record.name,
                "historical_brief": record.description,
                "source": f"{record.source};P20",
                "reference": str(REFERENCE.relative_to(ROOT)).replace("\\", "/"),
                "prompt": prompt,
            })
    return buffer.getvalue()


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
    retained = [row for row in ledger_rows() if row["key"] not in keys]
    for index, record in enumerate(records):
        retained.append({
            "key": record.key,
            "age": AGE_NAMES[record.age_index],
            "subject": record.name,
            "source": f"{record.source};P20",
            "confidence": "secure",
            "status": "complete",
            "note": (
                "Dedicated EU5-referenced archaeological cutout; reviewed in "
                f"S2-P3 four-up sheet {index // SHEET_CAPACITY + 1}, "
                f"{CELLS[index % SHEET_CAPACITY]}."
            ),
        })
    with DIRECT_ADVANCE_ART.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LEDGER_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(retained)


def remove_green(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    pixels = []
    for red, green, blue, _alpha in rgba.get_flattened_data():
        distance = max(abs(red), abs(green - 255), abs(blue))
        dominance = green - max(red, blue)
        key_like = distance <= 32 or dominance >= 16
        if not key_like:
            alpha = 255
        else:
            ratio = max(0.0, min(1.0, (distance - 12) / (220 - 12)))
            ratio = ratio * ratio * (3 - 2 * ratio)
            distance_alpha = round(255 * ratio)
            dominance_alpha = round(
                255 * (1 - min(1.0, max(0, dominance) / max(1, 255 - max(red, blue))))
            )
            alpha = min(distance_alpha, dominance_alpha)
            if alpha <= 8:
                alpha = 0
        if alpha == 0:
            pixels.append((0, 0, 0, 0))
            continue
        if key_like and alpha < 252:
            green = min(green, max(0, max(red, blue) - 1))
        pixels.append((red, green, blue, alpha))
    rgba.putdata(pixels)
    alpha = rgba.getchannel("A").filter(ImageFilter.MinFilter(3))
    rgba.putalpha(alpha)
    return rgba


def build_master(crop: Image.Image) -> Image.Image:
    keyed = remove_green(crop)
    bounds = keyed.getchannel("A").getbbox()
    if bounds is None:
        raise ValueError("chroma-keyed advance cell is empty")
    subject = keyed.crop(bounds)
    subject.thumbnail((220, 220), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    canvas.alpha_composite(
        subject,
        ((256 - subject.width) // 2, (256 - subject.height) // 2),
    )
    return canvas


def render_contact(records) -> None:
    columns = 10
    tile = 112
    label = 28
    rows = (len(records) + columns - 1) // columns
    canvas = Image.new("RGB", (columns * tile, rows * (tile + label)), "#101722")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    for index, record in enumerate(records):
        _source, master, _texture = paths(record.key)
        with Image.open(master) as image:
            checker = Image.new("RGB", (tile - 4, tile - 4), "#293341")
            preview = ImageOps.contain(
                image.convert("RGBA"), (tile - 4, tile - 4),
                Image.Resampling.LANCZOS,
            )
            checker.paste(preview.convert("RGB"), (0, 0), preview.getchannel("A"))
        x = index % columns * tile
        y = index // columns * (tile + label)
        canvas.paste(checker, (x + 2, y + 2))
        draw.text(
            (x + 3, y + tile + 1),
            f"{index + 1:03} {record.key[5:21]}",
            fill="#e8e0d0",
            font=font,
        )
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
            master = build_master(crop)
            source_path, master_path, texture_path = paths(record.key)
            remove_green(crop).save(source_path, format="PNG", optimize=True)
            master.save(master_path, format="PNG", optimize=True)
            convert(master_path, texture_path, "bc7", True)
    finally:
        for image in opened.values():
            image.close()
    write_ledger(records)
    render_contact(records)


def check(records) -> None:
    failures: list[str] = []
    manifest = manifest_rows()
    manifest_keys = [row["key"] for row in manifest]
    if len(manifest) != EXPECTED_ARCHIVE_COUNT:
        failures.append(
            f"expected {EXPECTED_ARCHIVE_COUNT} archived manifest rows, "
            f"got {len(manifest)}"
        )
    if len(set(manifest_keys)) != len(manifest_keys):
        failures.append("S2-P3 advance-art manifest has duplicate keys")
    if len({row["sheet"] for row in manifest}) != EXPECTED_SHEET_COUNT:
        failures.append(
            f"S2-P3 advance art must retain {EXPECTED_SHEET_COUNT} four-up sheets"
        )
    active_keys = {record.key for record in records}
    if not active_keys.issubset(set(manifest_keys)):
        failures.append("active S2-P3 art keys are absent from the archive manifest")
    complete = {
        row["key"]: row for row in ledger_rows() if row["status"] == "complete"
    }
    hashes: dict[str, str] = {}
    for row in manifest:
        key = row["key"]
        sheet = SHEET_DIR / row["sheet"]
        source, master, texture = paths(key)
        if key not in complete:
            failures.append(f"direct art ledger is missing {key}")
        for path, role in (
            (sheet, "four-up sheet"), (source, "source"),
            (master, "master"), (texture, "texture"),
        ):
            if not path.is_file():
                failures.append(f"missing {role} for {key}: {path.relative_to(ROOT)}")
        if master.is_file():
            with Image.open(master) as image:
                rgba = image.convert("RGBA")
                if image.format != "PNG" or image.size != (256, 256):
                    failures.append(f"invalid master contract for {key}")
                alpha = rgba.getchannel("A")
                bounds = alpha.getbbox()
                if bounds is None:
                    failures.append(f"empty alpha for {key}")
                elif (
                    bounds[0] < 12 or bounds[1] < 12
                    or bounds[2] > 244 or bounds[3] > 244
                ):
                    failures.append(f"unsafe circular framing for {key}: {bounds}")
                if alpha.getpixel((0, 0)) or alpha.getpixel((255, 255)):
                    failures.append(f"opaque master corner for {key}")
                digest = hashlib.sha256(rgba.tobytes()).hexdigest()
            if digest in hashes:
                failures.append(f"visual alias: {hashes[digest]} and {key}")
            hashes[digest] = key
        if texture.is_file():
            details = identify(texture)
            expected = {
                "format": "DDS", "width": "256", "height": "256",
                "depth": "8", "channels": "srgba 4.0",
            }
            if details != expected:
                failures.append(f"invalid DDS for {key}: {details}")
    if len(records) != EXPECTED_ACTIVE_COUNT:
        failures.append(
            f"expected {EXPECTED_ACTIVE_COUNT} active later records, got {len(records)}"
        )
    if not REFERENCE.is_file():
        failures.append("installed EU5 advance style reference is missing")
    if not CONTACT.is_file():
        failures.append("S2-P3 advance-art contact sheet is missing")
    if failures:
        raise ValueError("\n".join(failures))


def write_manifest(records) -> None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(manifest_text(records), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if sum((args.manifest, args.write, args.check)) != 1:
        parser.error("provide exactly one of --manifest, --write, or --check")
    try:
        records = expansion_records()
        if args.manifest:
            raise ValueError(
                "the 440-key S2-P3 manifest is an archival contract; "
                "do not rebuild it from the split active tree"
            )
        if args.write:
            raise ValueError(
                "the 440-key S2-P3 art archive is already rendered; "
                "do not positionally rewrite it from the split active tree"
            )
        check(records)
    except (OSError, ValueError, csv.Error) as exc:
        print(f"m8_later_expansion_art: FAIL\n  - {exc}")
        return 1
    print(
        "m8_later_expansion_art: PASS "
        f"({len(records)} active + "
        f"{EXPECTED_ARCHIVE_COUNT - len(records)} retired direct BC7 icons from "
        f"{EXPECTED_SHEET_COUNT} EU5-referenced four-up sheets)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
