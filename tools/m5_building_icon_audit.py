#!/usr/bin/env python3
"""Audit every active building icon against the ANTIQVITAS UI contract."""

from __future__ import annotations

import argparse
import csv
import hashlib
from dataclasses import dataclass
from io import StringIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import m5_ancient_building_replacements
import m5_regional_buildings
import m5_roman_buildings
from m11_ui_asset_ledger import building_master


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/m5/building_icon_audit.csv"
CONTACT = ROOT / "docs/m5/BUILDING_ICON_CIRCLE_AUDIT.png"
EXPECTED_TOTAL = 277
# Raise this after each reviewed re-art batch. It prevents regressions while the
# open P3 task advances toward the final 265/265 gate.
MIN_STYLE_PASS = 277
NAVY = (16, 25, 43, 255)


@dataclass(frozen=True)
class Item:
    cohort: str
    key: str
    name: str
    master: Path


@dataclass(frozen=True)
class Audit:
    item: Item
    circle_safe: bool
    dark_blue_field: bool
    style_pass: bool
    opaque_pixels: int
    transparent_pixels: int
    ring_rgb: tuple[int, int, int]
    navy_ring_fraction: float
    sha256: str
    dhash: int


def items() -> list[Item]:
    result: list[Item] = []
    for row in m5_roman_buildings.load():
        result.append(Item("named_roman", row["key"], row["name"], building_master(row["key"])))
    for row in m5_ancient_building_replacements.load():
        result.append(Item("ancient_replacement", row["key"], row["name"], building_master(row["key"])))
    families, _seeds = m5_regional_buildings.load()
    for row in families:
        result.append(Item("regional_family", row["key"], row["name"], building_master(row["key"])))
    return result


def difference_hash(image: Image.Image) -> int:
    """Return a compact visual hash used to expose near-aliases for review."""
    sample = image.convert("RGB").resize((9, 8), Image.Resampling.LANCZOS).convert("L")
    pixels = list(sample.getdata())
    result = 0
    for y in range(8):
        for x in range(8):
            result = (result << 1) | (pixels[y * 9 + x] > pixels[y * 9 + x + 1])
    return result


def audit(item: Item) -> Audit:
    with Image.open(item.master) as opened:
        image = opened.convert("RGBA")
    if image.size != (128, 128):
        raise ValueError(f"{item.key} master is {image.size}, expected 128x128")
    alpha = list(image.getchannel("A").getdata())
    opaque = sum(value >= 240 for value in alpha)
    transparent = sum(value <= 15 for value in alpha)
    corners = tuple(image.getpixel(point)[3] for point in ((0, 0), (127, 0), (0, 127), (127, 127)))
    # A 128px circle occupies about 12.7k pixels. The softened 122px mask used
    # by the accepted pipeline has roughly 11.3k opaque and 4.35k transparent.
    circle_safe = max(corners) <= 15 and 10_500 <= opaque <= 12_800 and 3_300 <= transparent <= 5_200

    ring: list[tuple[int, int, int]] = []
    for y in range(128):
        for x in range(128):
            distance = ((x - 63.5) ** 2 + (y - 63.5) ** 2) ** 0.5
            red, green, blue, pixel_alpha = image.getpixel((x, y))
            if 45 <= distance <= 57 and pixel_alpha >= 200:
                ring.append((red, green, blue))
    if not ring:
        ring_rgb = (255, 255, 255)
    else:
        ring_rgb = tuple(round(sum(pixel[channel] for pixel in ring) / len(ring)) for channel in range(3))
    red, green, blue = ring_rgb
    navy_pixels = sum(
        max(pixel) <= 100 and pixel[2] >= pixel[0] and pixel[2] >= pixel[1] + 2
        for pixel in ring
    )
    navy_fraction = navy_pixels / len(ring) if ring else 0.0
    # A complex architectural silhouette can cross the ring; requiring at
    # least 35% genuinely navy pixels preserves a visible common field while
    # allowing tall monuments and long aqueducts to remain legible.
    dark_blue = navy_fraction >= 0.35
    return Audit(
        item=item,
        circle_safe=circle_safe,
        dark_blue_field=dark_blue,
        style_pass=circle_safe and dark_blue,
        opaque_pixels=opaque,
        transparent_pixels=transparent,
        ring_rgb=ring_rgb,
        navy_ring_fraction=navy_fraction,
        sha256=hashlib.sha256(image.tobytes()).hexdigest(),
        dhash=difference_hash(image),
    )


def neighbors(audits: list[Audit]) -> dict[str, str]:
    result: dict[str, list[str]] = {entry.item.key: [] for entry in audits}
    for index, left in enumerate(audits):
        for right in audits[index + 1:]:
            distance = (left.dhash ^ right.dhash).bit_count()
            if distance <= 3:
                result[left.item.key].append(f"{right.item.key}:{distance}")
                result[right.item.key].append(f"{left.item.key}:{distance}")
    return {key: ";".join(values) for key, values in result.items()}


def render_report(audits: list[Audit]) -> str:
    near = neighbors(audits)
    stream = StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow((
        "cohort", "key", "name", "master", "circle_safe", "dark_blue_field",
        "style_pass", "opaque_pixels", "transparent_pixels", "ring_rgb",
        "navy_ring_fraction", "sha256", "near_duplicate_dhash",
    ))
    for entry in audits:
        writer.writerow((
            entry.item.cohort,
            entry.item.key,
            entry.item.name,
            entry.item.master.relative_to(ROOT).as_posix(),
            str(entry.circle_safe).lower(),
            str(entry.dark_blue_field).lower(),
            str(entry.style_pass).lower(),
            entry.opaque_pixels,
            entry.transparent_pixels,
            "/".join(str(value) for value in entry.ring_rgb),
            f"{entry.navy_ring_fraction:.3f}",
            entry.sha256,
            near[entry.item.key],
        ))
    return stream.getvalue()


def ellipsis(text: str, width: int) -> str:
    return text if len(text) <= width else text[:width - 1] + "…"


def render_contact(audits: list[Audit]) -> Image.Image:
    tile_width, tile_height = 154, 176
    columns = 12
    rows = (len(audits) + columns - 1) // columns
    contact = Image.new("RGBA", (columns * tile_width, rows * tile_height + 54), NAVY)
    draw = ImageDraw.Draw(contact)
    font = ImageFont.load_default()
    passed = sum(entry.style_pass for entry in audits)
    draw.text((12, 10), f"Active building icons: {passed}/{len(audits)} circle-safe dark-blue", fill=(235, 239, 245), font=font)
    draw.text((12, 28), "Green = contract pass; red = requires re-art", fill=(170, 180, 195), font=font)
    for index, entry in enumerate(audits):
        x = (index % columns) * tile_width
        y = (index // columns) * tile_height + 54
        with Image.open(entry.item.master) as opened:
            icon = opened.convert("RGBA").resize((128, 128), Image.Resampling.LANCZOS)
        # Display the exact circular in-widget silhouette over the canonical
        # panel field, not the source against a checkerboard or white square.
        contact.alpha_composite(icon, (x + 13, y + 4))
        color = (100, 222, 150) if entry.style_pass else (245, 112, 105)
        draw.rectangle((x + 8, y, x + 145, y + 169), outline=color, width=2)
        draw.text((x + 8, y + 136), ellipsis(entry.item.name, 22), fill=(232, 235, 240), font=font)
        flags = f"C:{'Y' if entry.circle_safe else 'N'} B:{'Y' if entry.dark_blue_field else 'N'}"
        draw.text((x + 8, y + 151), flags, fill=color, font=font)
    return contact


def validate(audits: list[Audit]) -> None:
    failures: list[str] = []
    keys = [entry.item.key for entry in audits]
    if len(audits) != EXPECTED_TOTAL:
        failures.append(f"active building inventory is {len(audits)}, expected {EXPECTED_TOTAL}")
    if len(keys) != len(set(keys)):
        failures.append("active building inventory contains duplicate keys")
    exact: dict[str, str] = {}
    for entry in audits:
        if entry.sha256 in exact:
            failures.append(f"exact visual alias: {exact[entry.sha256]} and {entry.item.key}")
        exact[entry.sha256] = entry.item.key
    passed = sum(entry.style_pass for entry in audits)
    if passed < MIN_STYLE_PASS:
        failures.append(f"style pass count regressed to {passed}; floor is {MIN_STYLE_PASS}")
    expected = render_report(audits)
    if not REPORT.is_file() or REPORT.read_text(encoding="utf-8-sig") != expected:
        failures.append(f"stale or missing audit report: {REPORT.relative_to(ROOT)}")
    if not CONTACT.is_file():
        failures.append(f"missing circle audit contact sheet: {CONTACT.relative_to(ROOT)}")
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
        audits = [audit(item) for item in items()]
        if args.write:
            REPORT.parent.mkdir(parents=True, exist_ok=True)
            REPORT.write_text(render_report(audits), encoding="utf-8-sig", newline="")
            render_contact(audits).convert("RGB").save(CONTACT)
        validate(audits)
    except (OSError, ValueError, csv.Error) as exc:
        print(f"m5_building_icon_audit: FAIL\n  - {exc}")
        return 1
    passed = sum(entry.style_pass for entry in audits)
    near = sum(bool(value) for value in neighbors(audits).values())
    print(
        f"m5_building_icon_audit: PASS "
        f"({passed}/{len(audits)} style-compliant; {near} icons have a dHash neighbor <=3)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
