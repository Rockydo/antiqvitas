#!/usr/bin/env python3
"""Derive twelve Roman civic 128px masters and direct DDS icons from one sheet."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets_queue/generated_sources/antq_roman_republican_civic_sheet_source.png"
OUT = ROOT / "assets_queue/generated"
ICONS = ROOT / "main_menu/gfx/interface/icons/buildings"
DDS = ROOT / "tools/dds.py"
KEYS = (
    "aedes_vestae", "aedes_saturni", "miliarium_aureum", "aedes_penatium",
    "fornix_fabianus", "ara_saturni", "rostra_augusti", "basilica_iulia",
    "porticus_pompeiana", "theatrum_pompei", "aedes_iovis_statoris", "curiae_veteres",
)


def main() -> int:
    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)
    image = Image.open(SOURCE).convert("RGBA")
    width, height = image.size
    if width < 900 or height < 1200:
        raise ValueError(f"unexpected source sheet dimensions: {image.size}")
    OUT.mkdir(parents=True, exist_ok=True)
    ICONS.mkdir(parents=True, exist_ok=True)
    for index, key in enumerate(KEYS):
        col, row = index % 3, index // 3
        left, top = round(col * width / 3) + 5, round(row * height / 4) + 5
        right, bottom = round((col + 1) * width / 3) - 5, round((row + 1) * height / 4) - 5
        png = OUT / f"antq_{key}.png"
        image.crop((left, top, right, bottom)).resize((128, 128), Image.Resampling.LANCZOS).save(png)
        subprocess.run([sys.executable, str(DDS), "convert", str(png), str(ICONS / f"antq_{key}.dds"), "--compression", "bc7"], check=True)
    print(f"split_m5_roman_republican_sheet: wrote {len(KEYS)} PNG/DDS pairs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
