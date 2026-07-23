#!/usr/bin/env python3
"""Derive twelve Roman temple/civic 128px masters and direct DDS icons."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets_queue/generated_sources/antq_roman_temple_civic_sheet_source.png"
OUT = ROOT / "assets_queue/generated"
ICONS = ROOT / "main_menu/gfx/interface/icons/buildings"
DDS = ROOT / "tools/dds.py"
KEYS = (
    "aedes_concordiae_augustae", "aedes_bellonae", "aedes_iovis_tonantis", "aedes_magnae_matris",
    "forum_iulium", "aedes_divi_iulii", "aedes_fortunae_primigeniae", "puteal_libonis",
    "casa_romuli", "porticus_gai_et_luci", "chalcidicum_iulium", "aedes_victoriae",
)


def main() -> int:
    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)
    image = Image.open(SOURCE).convert("RGBA")
    width, height = image.size
    if width < 1000 or height < 1000:
        raise ValueError(f"unexpected source sheet dimensions: {image.size}")
    OUT.mkdir(parents=True, exist_ok=True)
    ICONS.mkdir(parents=True, exist_ok=True)
    # The model supplied four rows; retain exactly its first three rows (12 tiles).
    for index, key in enumerate(KEYS):
        col, row = index % 4, index // 4
        left, top = round(col * width / 4) + 5, round(row * height / 4) + 5
        right, bottom = round((col + 1) * width / 4) - 5, round((row + 1) * height / 4) - 5
        png = OUT / f"antq_{key}.png"
        image.crop((left, top, right, bottom)).resize((128, 128), Image.Resampling.LANCZOS).save(png)
        subprocess.run([sys.executable, str(DDS), "convert", str(png), str(ICONS / f"antq_{key}.dds"), "--compression", "bc7"], check=True)
    print(f"split_m5_roman_temple_civic_sheet: wrote {len(KEYS)} PNG/DDS pairs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
