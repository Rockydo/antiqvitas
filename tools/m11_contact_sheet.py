#!/usr/bin/env python3
"""Render the reviewable M11 event-art contact sheet from retained masters."""

from __future__ import annotations

from html import escape
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
MASTERS = ROOT / "assets_queue" / "generated"
DOCS = ROOT / "docs" / "m11"
HTML_OUTPUT = DOCS / "contact_sheet.html"
PNG_OUTPUT = DOCS / "contact_sheet.png"
SUFFIX = "_1080x440.png"
THUMBNAIL = (360, 147)
COLUMNS = 3
PADDING = 18
LABEL_HEIGHT = 30
BACKGROUND = (20, 23, 27, 255)
LABEL = (235, 235, 235, 255)


def title(path: Path) -> str:
    return path.stem.removeprefix("antq_").removesuffix("_1080x440").replace("_", " ").title()


def sources() -> list[Path]:
    entries = sorted(
        path for path in MASTERS.glob(f"antq_*{SUFFIX}")
        if not path.stem.startswith("antq_age_")
    )
    if not entries:
        raise RuntimeError("No M11 event masters found")
    return entries


def render_png(entries: list[Path]) -> None:
    rows = (len(entries) + COLUMNS - 1) // COLUMNS
    width = PADDING + COLUMNS * (THUMBNAIL[0] + PADDING)
    height = PADDING + rows * (THUMBNAIL[1] + LABEL_HEIGHT + PADDING)
    sheet = Image.new("RGBA", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for index, source in enumerate(entries):
        column = index % COLUMNS
        row = index // COLUMNS
        x = PADDING + column * (THUMBNAIL[0] + PADDING)
        y = PADDING + row * (THUMBNAIL[1] + LABEL_HEIGHT + PADDING)
        with Image.open(source) as image:
            sheet.alpha_composite(image.convert("RGBA").resize(THUMBNAIL), (x, y))
        draw.text((x, y + THUMBNAIL[1] + 7), title(source), fill=LABEL, font=font)
    sheet.convert("RGB").save(PNG_OUTPUT)


def render_html(entries: list[Path]) -> None:
    cards = "\n".join(
        "    <figure><img src=\"../../assets_queue/generated/"
        + escape(source.name)
        + "\" alt=\""
        + escape(title(source))
        + "\"><figcaption>"
        + escape(title(source))
        + "</figcaption></figure>"
        for source in entries
    )
    HTML_OUTPUT.write_text(
        "<!doctype html>\n"
        "<html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<title>ANTIQVITAS M11 Event Art Contact Sheet</title>"
        "<style>body{background:#14171b;color:#eee;font:16px system-ui;margin:2rem}"
        "main{max-width:1200px;margin:auto}section{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}"
        "figure{margin:0;background:#20252b;padding:8px}img{width:100%;height:auto;display:block}"
        "figcaption{padding:8px 2px 2px;text-transform:none}</style></head><body><main>"
        "<h1>ANTIQVITAS M11 event-art review</h1>"
        "<p>Generated from retained 1080x440 masters. Each image remains subject to its individual scope record.</p>"
        "<section>\n" + cards + "\n</section></main></body></html>\n",
        encoding="utf-8",
    )


def main() -> int:
    entries = sources()
    DOCS.mkdir(parents=True, exist_ok=True)
    render_png(entries)
    render_html(entries)
    print(f"m11_contact_sheet: wrote {len(entries)} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
