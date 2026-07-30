#!/usr/bin/env python3
"""Build and audit the complete installed location-illustration surface.

The installed resolver is split across the base game and three mounted DLCs.
This tool inventories that union, replaces every structural/ritual layer with
AD 1 art at the exact mounted path, and records the period-neutral natural
layers that remain engine-owned.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps
import numpy as np

from dds import convert, identify


ROOT = Path(__file__).resolve().parents[1]
GAME = Path(r"<GAME_DIR>\game")
SOURCE_DIR = ROOT / "assets_queue/generated_sources/location_view"
MASTER_DIR = ROOT / "assets_queue/generated/location_view/masters"
LEDGER = ROOT / "docs/s3/location_illustration_union.csv"
CONTACT = ROOT / "docs/s3/location_ancient_structures_contact.png"
CHROMA_HELPER = (
    Path.home() / ".codex/skills/.system/imagegen/scripts/remove_chroma_key.py"
)
QUADRANTS = ("top_left", "top_right", "bottom_left", "bottom_right")
STRUCTURAL = {
    "settlement1", "settlement2", "fortifications", "fortification", "dock",
    "religious_buildings", "factories", "wall", "monuments", "holy_sites",
}
ANCIENT_RETAINED = {
    "pyramids", "teotihuacan", "sanchi_stupa", "parthenon", "stonehenge",
}


@dataclass(frozen=True)
class Sheet:
    filename: str
    kind: str
    regions: tuple[str, str, str, str]


REGIONAL_SHEETS = (
    Sheet("antq_location_roman_4up.png", "regional", ("roman",) * 4),
    Sheet("antq_location_iranian_syrian_4up.png", "regional", ("iranian_syrian",) * 4),
    Sheet("antq_location_germanic_celtic_4up.png", "regional", ("germanic_celtic",) * 4),
    Sheet("antq_location_han_4up.png", "regional", ("han",) * 4),
    Sheet("antq_location_indian_4up.png", "regional", ("indian",) * 4),
    Sheet("antq_location_african_4up.png", "regional", ("african",) * 4),
    Sheet("antq_location_mesoamerican_4up.png", "regional", ("mesoamerican",) * 4),
    Sheet("antq_location_woodland_4up.png", "regional", ("woodland",) * 4),
)
SPECIAL_SHEETS = (
    Sheet(
        "antq_location_workshops_civil_4up.png", "workshop",
        ("roman", "iranian_syrian", "han", "indian"),
    ),
    Sheet(
        "antq_location_workshops_vernacular_4up.png", "workshop",
        ("germanic_celtic", "african", "mesoamerican", "woodland"),
    ),
    Sheet(
        "antq_location_walls_old_world_4up.png", "wall",
        ("roman", "iranian_syrian", "germanic_celtic", "han"),
    ),
    Sheet(
        "antq_location_walls_regional_4up.png", "wall",
        ("indian", "african", "mesoamerican", "woodland"),
    ),
)
REGIONAL_KINDS = ("settlement", "fortification", "dock", "religious")


def resolver_files() -> list[Path]:
    return sorted(GAME.rglob("*images_location*.txt"))


def texture_union() -> list[str]:
    result: set[str] = set()
    for path in resolver_files():
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        result.update(re.findall(r'texture_file\s*=\s*"([^"]+)"', text))
    return sorted(result)


def category(relative: str) -> str:
    parts = relative.replace("\\", "/").split("/")
    try:
        return parts[parts.index("location") + 1]
    except (ValueError, IndexError):
        return "other"


def installed_texture(relative: str) -> Path | None:
    for mounted in (GAME / "main_menu", GAME / "in_game"):
        direct = mounted / relative
        if direct.is_file():
            return direct
    for dlc in sorted((GAME / "dlc").glob("*")):
        for mounted in (dlc / "main_menu", dlc / "in_game"):
            candidate = mounted / relative
            if candidate.is_file():
                return candidate
    return None


def region_for(relative: str) -> str:
    folded = relative.casefold().replace("\\", "/")
    matches = (
        (("byzantium",), "roman"),
        (("north_german",), "germanic_celtic"),
        (("syrian",), "iranian_syrian"),
        (("asian",), "han"),
        (("deccan", "indian"), "indian"),
        (("ashanti",), "african"),
        (("aztec",), "mesoamerican"),
        (("iroquois", "stockade"), "woodland"),
    )
    for needles, region in matches:
        if any(needle in folded for needle in needles):
            return region
    monument_regions = (
        (("leshan",), "han"),
        (("samarra", "hagia", "meteora", "colosseum", "peters"), "roman"),
        (("cholula", "teotihuacan"), "mesoamerican"),
        (("ranganathaswamy", "mahabodhi", "sanchi"), "indian"),
        (("kaaba", "holy_sepulchre"), "iranian_syrian"),
    )
    for needles, region in monument_regions:
        if any(needle in folded for needle in needles):
            return region
    return "roman"


def kind_for(relative: str) -> str:
    cat = category(relative)
    if cat in {"settlement1", "settlement2"}:
        return "settlement"
    if cat in {"fortifications", "fortification"}:
        return "fortification"
    if cat == "dock":
        return "dock"
    if cat == "factories":
        return "workshop"
    if cat == "wall" or "wall" in Path(relative).stem.casefold():
        return "wall"
    if cat in {"religious_buildings", "monuments", "holy_sites"}:
        return "religious"
    return "retained"


def quadrant_box(size: tuple[int, int], quadrant: str) -> tuple[int, int, int, int]:
    width, height = size
    if width != height or width % 2:
        raise ValueError(f"four-up source must be even and square, got {size}")
    half, inset = width // 2, 8
    return {
        "top_left": (inset, inset, half - inset, half - inset),
        "top_right": (half + inset, inset, width - inset, half - inset),
        "bottom_left": (inset, half + inset, half - inset, height - inset),
        "bottom_right": (half + inset, half + inset, width - inset, height - inset),
    }[quadrant]


def remove_chroma(source: Path, target: Path) -> None:
    if not CHROMA_HELPER.is_file():
        raise ValueError(f"missing chroma helper: {CHROMA_HELPER}")
    subprocess.run(
        [
            sys.executable, str(CHROMA_HELPER),
            "--input", str(source), "--out", str(target),
            "--auto-key", "border", "--soft-matte",
            "--transparent-threshold", "12", "--opaque-threshold", "220",
            "--despill", "--force",
        ],
        check=True,
    )


def master_path(region: str, kind: str) -> Path:
    return MASTER_DIR / region / f"{kind}.png"


def purge_magenta_fringe(source: Image.Image) -> Image.Image:
    """Remove generator chroma drift that survives border-distance keying."""
    rgba = np.array(source.convert("RGBA"))
    red = rgba[:, :, 0].astype(np.int16)
    green = rgba[:, :, 1].astype(np.int16)
    blue = rgba[:, :, 2].astype(np.int16)
    fringe = (
        (red > 115)
        & (blue > 105)
        & (green * 100 < np.minimum(red, blue) * 72)
    )
    rgba[:, :, 3][fringe] = 0
    rgba[:, :, :3][fringe] = 0
    return Image.fromarray(rgba, "RGBA")


def build_masters() -> None:
    MASTER_DIR.mkdir(parents=True, exist_ok=True)
    temp_root = ROOT / ".tmp"
    temp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="antq-location-", dir=temp_root) as temporary:
        work = Path(temporary)
        for sheet in (*REGIONAL_SHEETS, *SPECIAL_SHEETS):
            source = SOURCE_DIR / sheet.filename
            if not source.is_file():
                raise ValueError(f"missing reviewed four-up sheet: {source}")
            with Image.open(source) as opened:
                image = opened.convert("RGB")
                for index, (quadrant, region) in enumerate(
                    zip(QUADRANTS, sheet.regions, strict=True)
                ):
                    kind = REGIONAL_KINDS[index] if sheet.kind == "regional" else sheet.kind
                    raw = work / f"{source.stem}_{index}_raw.png"
                    keyed = work / f"{source.stem}_{index}_keyed.png"
                    image.crop(quadrant_box(image.size, quadrant)).save(raw)
                    remove_chroma(raw, keyed)
                    with Image.open(keyed) as transparent:
                        rgba = purge_magenta_fringe(transparent)
                        box = rgba.getchannel("A").getbbox()
                        if box is None:
                            raise ValueError(f"empty keyed asset: {source}:{quadrant}")
                        subject = rgba.crop(box)
                    target = master_path(region, kind)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    subject.save(target, optimize=True)


def staged_scale(relative: str) -> float:
    stem = Path(relative).stem.casefold()
    if "rural" in stem or "dock1" in stem or "bastion" in stem:
        return 0.68
    if "town" in stem or "dock2" in stem or "castle" in stem:
        return 0.82
    if "city" in stem or "dock3" in stem or "fortress" in stem:
        return 0.94
    return 0.90


def render_target(relative: str, source: Image.Image, size: tuple[int, int]) -> Image.Image:
    width, height = size
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    subject = source.convert("RGBA")
    scale = staged_scale(relative)
    maximum = (max(1, int(width * scale)), max(1, int(height * 0.94)))
    subject.thumbnail(maximum, Image.Resampling.LANCZOS)
    if "settlement2" in relative.casefold():
        subject = ImageOps.mirror(subject)
        alpha = subject.getchannel("A").point(lambda value: int(value * 0.88))
        subject.putalpha(alpha)
    x = (width - subject.width) // 2
    y = height - subject.height
    canvas.alpha_composite(subject, (x, y))
    return canvas


def write_contact() -> None:
    paths = sorted(MASTER_DIR.glob("*/*.png"))
    tile, label, columns = (280, 180), 28, 4
    rows = (len(paths) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * tile[0], rows * (tile[1] + label)), "#171b20")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for index, path in enumerate(paths):
        x = (index % columns) * tile[0]
        y = (index // columns) * (tile[1] + label)
        with Image.open(path) as opened:
            art = ImageOps.contain(opened.convert("RGBA"), (tile[0] - 12, tile[1] - 12))
        sheet.paste(art, (x + (tile[0] - art.width) // 2, y + tile[1] - art.height), art)
        draw.text((x + 6, y + tile[1] + 6), f"{path.parent.name}/{path.stem}", fill="#edf0e8", font=font)
    CONTACT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(CONTACT, optimize=True)


def write_ledger(rows: list[dict[str, str]]) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    fields = (
        "category", "texture", "installed_source", "status", "region", "art_kind",
        "target", "dimensions", "sha256", "note",
    )
    with LEDGER.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write(force: bool = False) -> None:
    build_masters()
    rows: list[dict[str, str]] = []
    replaced = 0
    for relative in texture_union():
        installed = installed_texture(relative)
        cat = category(relative)
        stem = Path(relative).stem.casefold()
        kind = kind_for(relative)
        target = ROOT / "main_menu" / relative
        status, note = "retained_engine_period_neutral", "natural/effect layer; no built structure"
        digest = ""
        dimensions = ""
        if installed is not None:
            details = identify(installed)
            dimensions = f"{details['width']}x{details['height']}"
        if cat in STRUCTURAL and installed is not None:
            if any(key in stem for key in ANCIENT_RETAINED):
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(installed, target)
                status, note = "retained_reviewed_ancient", "installed ancient monument retained"
            else:
                region = region_for(relative)
                art = master_path(region, kind)
                installed_details = identify(installed)
                expected_size = (
                    int(installed_details["width"]), int(installed_details["height"])
                )
                current = identify(target) if target.is_file() else {}
                if (
                    force
                    or
                    current.get("width") != str(expected_size[0])
                    or current.get("height") != str(expected_size[1])
                    or "".join(current.get("channels", "").split()) != "srgba4.0"
                ):
                    with Image.open(art) as opened:
                        rendered = render_target(relative, opened, expected_size)
                    temp_root = ROOT / ".tmp"
                    temp_root.mkdir(parents=True, exist_ok=True)
                    with tempfile.TemporaryDirectory(prefix="antq-location-dds-", dir=temp_root) as temporary:
                        png = Path(temporary) / "target.png"
                        rendered.save(png, optimize=True)
                        convert(png, target, "bc7", mipmaps=True)
                status, note = "replaced_ad1", "generated four-up against exact installed EU5 references"
                replaced += 1
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
        rows.append({
            "category": cat,
            "texture": relative,
            "installed_source": str(installed or ""),
            "status": status,
            "region": region_for(relative) if cat in STRUCTURAL else "",
            "art_kind": kind if cat in STRUCTURAL else "",
            "target": str(target.relative_to(ROOT)) if target.is_file() else "",
            "dimensions": dimensions,
            "sha256": digest,
            "note": note,
        })
    write_ledger(rows)
    write_contact()
    print(f"s3_location_illustrations: wrote {replaced} AD 1 replacements; audited {len(rows)} installed textures")


def validate() -> None:
    failures: list[str] = []
    textures = texture_union()
    if len(resolver_files()) != 4:
        failures.append(f"expected four installed resolver files, found {len(resolver_files())}")
    if len(textures) != 255:
        failures.append(f"installed location union drifted from 255 to {len(textures)}")
    if not LEDGER.is_file():
        failures.append("location illustration union ledger is missing")
        rows: list[dict[str, str]] = []
    else:
        with LEDGER.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        if {row["texture"] for row in rows} != set(textures):
            failures.append("location union ledger does not exactly match installed resolver union")
    replaced = [row for row in rows if row["status"] == "replaced_ad1"]
    if len(replaced) < 130:
        failures.append(f"expected at least 130 structural replacements, found {len(replaced)}")
    banned = ("castle", "starfort", "hagia", "samarra", "peters", "holy_sepulchre", "ranganathaswamy", "enryakuji")
    for row in rows:
        if any(word in row["texture"].casefold() for word in banned):
            if row["status"] != "replaced_ad1":
                failures.append(f"anachronistic resolver not replaced: {row['texture']}")
    for row in replaced:
        target = ROOT / row["target"]
        if not target.is_file():
            failures.append(f"missing location override: {target}")
            continue
        details = identify(target)
        if f"{details['width']}x{details['height']}" != row["dimensions"]:
            failures.append(f"dimension mismatch: {target}")
        if "".join(details["channels"].split()) != "srgba4.0":
            failures.append(f"location override lost alpha: {target}")
        if hashlib.sha256(target.read_bytes()).hexdigest() != row["sha256"]:
            failures.append(f"stale location override digest: {target}")
    if len(list(MASTER_DIR.glob("*/*.png"))) != 48:
        failures.append("expected 48 reviewed regional/kind masters")
    if not CONTACT.is_file():
        failures.append("location structure contact sheet is missing")
    if failures:
        raise ValueError("\n".join(failures[:40]))
    print(
        f"s3_location_illustrations: PASS ({len(textures)} installed textures; "
        f"{len(replaced)} AD 1 structural replacements)"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if args.write:
        write(force=args.force)
    if args.check or not args.write:
        validate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
