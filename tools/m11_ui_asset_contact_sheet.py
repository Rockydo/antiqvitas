#!/usr/bin/env python3
"""Render a whole-inventory visual review sheet for direct ANTIQVITAS UI art."""

from __future__ import annotations

import argparse
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from m11_ui_asset_ledger import Asset, assets


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/m11/UI_ASSET_CONTACT_SHEET.png"
COLUMNS = 16
THUMB = 100
CELL_WIDTH = 116
CELL_HEIGHT = 126
PADDING = 16
HEADING = 28
BACKGROUND = (18, 21, 25, 255)
PANEL = (33, 38, 45, 255)
LABEL = (230, 232, 235, 255)
HEADING_COLOR = (242, 205, 132, 255)


def source(item: Asset) -> Path:
    return item.master or item.texture


def groups(items: list[Asset]) -> list[tuple[str, list[Asset]]]:
    labels = sorted({item.surface for item in items})
    return [(label, sorted((item for item in items if item.surface == label), key=lambda item: item.key)) for label in labels]


def sheet_bytes(items: list[Asset]) -> bytes:
    sections = groups(items)
    rows = sum((len(entries) + COLUMNS - 1) // COLUMNS for _label, entries in sections)
    height = PADDING + len(sections) * HEADING + rows * CELL_HEIGHT + (len(sections) - 1) * PADDING + PADDING
    width = PADDING + COLUMNS * CELL_WIDTH + PADDING
    sheet = Image.new("RGBA", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    y = PADDING
    for label, entries in sections:
        draw.text((PADDING, y + 6), f"{label} ({len(entries)})", fill=HEADING_COLOR, font=font)
        y += HEADING
        for index, item in enumerate(entries):
            column, row = index % COLUMNS, index // COLUMNS
            x = PADDING + column * CELL_WIDTH
            cell_y = y + row * CELL_HEIGHT
            sheet.paste(PANEL, (x, cell_y, x + THUMB, cell_y + THUMB))
            with Image.open(source(item)) as image:
                thumbnail = image.convert("RGBA")
                thumbnail.thumbnail((THUMB, THUMB), Image.Resampling.LANCZOS)
                offset = (x + (THUMB - thumbnail.width) // 2, cell_y + (THUMB - thumbnail.height) // 2)
                sheet.alpha_composite(thumbnail, offset)
            label_text = item.key.removeprefix("antq_").replace("_", " ")[:20]
            draw.text((x, cell_y + THUMB + 4), label_text, fill=LABEL, font=font)
        y += ((len(entries) + COLUMNS - 1) // COLUMNS) * CELL_HEIGHT + PADDING
    output = BytesIO()
    sheet.convert("RGB").save(output, format="PNG", optimize=True)
    return output.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        items = assets()
        rendered = sheet_bytes(items)
        if args.write:
            OUTPUT.parent.mkdir(parents=True, exist_ok=True)
            OUTPUT.write_bytes(rendered)
        if not OUTPUT.is_file() or OUTPUT.read_bytes() != rendered:
            raise ValueError(f"stale or missing direct UI contact sheet: {OUTPUT.relative_to(ROOT)}")
    except (OSError, ValueError) as exc:
        print(f"m11_ui_asset_contact_sheet: FAIL\n  - {exc}")
        return 1
    print(f"m11_ui_asset_contact_sheet: PASS ({len(items)} direct UI assets across {len(groups(items))} surfaces)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
