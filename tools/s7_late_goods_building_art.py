#!/usr/bin/env python3
"""Render and validate the four dated late-antique production-building icons."""

from __future__ import annotations

import argparse
import csv
import hashlib
import subprocess
import sys
from io import StringIO
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from m5_trade_good_cutouts import cell_box, fit_rgba, magenta_foreground


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets_queue/generated_sources/regional_buildings/late_goods_buildings_01.png"
SOURCE_HASH = "da00c7abc5d3e45baeea2ffd7e984879f296afbf46d9bd7fdb0899127e7ff21b"
MASTER_DIR = ROOT / "assets_queue/generated"
ICON_DIR = ROOT / "main_menu/gfx/interface/icons/buildings"
LEDGER = ROOT / "docs/m5/later_antique_goods_building_art.csv"
CONTACT = ROOT / "docs/m5/LATER_ANTIQUE_BUILDINGS_CONTACT.png"
DDS = ROOT / "tools/dds.py"
CELLS = (
    ("top_left", "antq_reg_codex_bindery"),
    ("top_right", "antq_reg_yue_celadon_kiln"),
    ("bottom_left", "antq_reg_polychrome_goldsmith"),
    ("bottom_right", "antq_reg_diatretum_glasshouse"),
)
NAVY = (16, 25, 43, 255)


def render(source: Image.Image, cell: str) -> Image.Image:
    crop = source.crop(cell_box(source.size, cell))
    rgba, alpha = magenta_foreground(crop)
    cutout = fit_rgba(rgba, alpha, extent=96)
    icon = Image.new("RGBA", (128, 128), NAVY)
    icon.alpha_composite(cutout)
    circle = Image.new("L", icon.size, 0)
    ImageDraw.Draw(circle).ellipse((3, 3, 124, 124), fill=255)
    icon.putalpha(circle.filter(ImageFilter.GaussianBlur(0.7)))
    return icon


def convert_dds(source: Path, target: Path) -> None:
    subprocess.run(
        [sys.executable, str(DDS), "convert", str(source), str(target), "--compression", "dxt5"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.DEVNULL,
    )


def ledger_text() -> str:
    stream = StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(("building", "source", "cell", "source_sha256", "style_reference"))
    for cell, key in CELLS:
        writer.writerow((
            key,
            SOURCE.relative_to(ROOT).as_posix(),
            cell,
            SOURCE_HASH,
            "installed EU5 scriptorium/porcelain_guild/jewelry_guild/glassworks and reviewed ANTIQVITAS circular workshops",
        ))
    return stream.getvalue()


def write_contact() -> None:
    tile = 168
    contact = Image.new("RGBA", (tile * 4, 184), (34, 41, 55, 255))
    draw = ImageDraw.Draw(contact)
    for index, (_cell, key) in enumerate(CELLS):
        x = index * tile
        with Image.open(MASTER_DIR / f"{key}.png") as icon:
            contact.alpha_composite(icon.convert("RGBA"), (x + 20, 8))
        draw.text((x + 5, 144), key.removeprefix("antq_reg_"), fill=(238, 241, 246, 255))
    contact.convert("RGB").save(CONTACT)


def write() -> None:
    if not SOURCE.is_file() or hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_HASH:
        raise ValueError("missing or changed reviewed late-building source atlas")
    MASTER_DIR.mkdir(parents=True, exist_ok=True)
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    with Image.open(SOURCE) as source:
        source = source.convert("RGBA")
        for cell, key in CELLS:
            icon = render(source, cell)
            master = MASTER_DIR / f"{key}.png"
            icon.save(master)
            convert_dds(master, ICON_DIR / f"{key}.dds")
    LEDGER.write_text(ledger_text(), encoding="utf-8-sig", newline="")
    write_contact()


def check() -> None:
    failures: list[str] = []
    if not SOURCE.is_file() or hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_HASH:
        failures.append("late-building source atlas is missing or changed")
    if not LEDGER.is_file() or LEDGER.read_text(encoding="utf-8-sig") != ledger_text():
        failures.append("late-building art ledger is stale")
    if not CONTACT.is_file():
        failures.append("late-building contact sheet is missing")
    digests: dict[str, str] = {}
    for _cell, key in CELLS:
        master = MASTER_DIR / f"{key}.png"
        icon = ICON_DIR / f"{key}.dds"
        if not master.is_file() or not icon.is_file():
            failures.append(f"{key} is missing master or DDS")
            continue
        with Image.open(master) as image:
            if image.mode != "RGBA" or image.size != (128, 128):
                failures.append(f"{key} master must be 128x128 RGBA")
                continue
            alpha = np.asarray(image.getchannel("A"), dtype=np.uint8)
            occupied = float((alpha > 24).mean())
            if not 0.68 <= occupied <= 0.78:
                failures.append(f"{key} has implausible circular-icon occupancy {occupied:.3f}")
            if any(image.getpixel(point)[3] for point in ((0, 0), (127, 0), (0, 127), (127, 127))):
                failures.append(f"{key} has an opaque corner")
        digest = hashlib.sha256(icon.read_bytes()).hexdigest()
        prior = digests.setdefault(digest, key)
        if prior != key:
            failures.append(f"duplicate late-building icons: {prior} and {key}")
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
    except (OSError, ValueError, csv.Error, subprocess.CalledProcessError) as exc:
        print(f"late-goods building art: FAIL\n{exc}", file=sys.stderr)
        return 1
    print("late-goods building art: PASS (4 circular icons; hash-pinned four-up source)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
