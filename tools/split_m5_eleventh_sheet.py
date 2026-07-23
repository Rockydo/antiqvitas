#!/usr/bin/env python3
"""Derive the twelve reviewed regional-building PNG masters from one sheet."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets_queue/generated_sources/antq_reg_eleventh_pass_sheet_source.png"
OUT = ROOT / "assets_queue/generated"
DDS = ROOT / "tools/dds.py"
ICON_DIR = ROOT / "main_menu/gfx/interface/icons/buildings"
KEYS = (
    "locksmith", "nailery", "chainmaker", "wiredrawer", "shieldmaker", "scabbard_maker",
    "fishing_tackle", "feltworks", "carpet_loom", "cork_workshop", "brushmaker", "tesserae_kiln",
)


def main() -> int:
    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)
    OUT.mkdir(parents=True, exist_ok=True)
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    image = Image.open(SOURCE).convert("RGBA")
    width, height = image.size
    if width < 900 or height < 1200:
        raise ValueError(f"unexpected source-sheet dimensions {image.size}")
    for index, slug in enumerate(KEYS):
        col, row = index % 3, index // 3
        left = round(col * width / 3) + 5
        top = round(row * height / 4) + 5
        right = round((col + 1) * width / 3) - 5
        bottom = round((row + 1) * height / 4) - 5
        png = OUT / f"antq_reg_{slug}.png"
        image.crop((left, top, right, bottom)).resize((128, 128), Image.Resampling.LANCZOS).save(png)
        subprocess.run([sys.executable, str(DDS), "convert", str(png), str(ICON_DIR / f"antq_reg_{slug}.dds"), "--compression", "bc7"], check=True)
    print(f"split_m5_eleventh_sheet: wrote {len(KEYS)} PNG/DDS pairs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
