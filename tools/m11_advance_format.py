#!/usr/bin/env python3
"""Normalize and audit advance icons for every installed EU5 GUI surface."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from dds import convert, identify
from m11_advance_icons import ADVANCE_ICONS, AdvanceIcon, direct_assets


ROOT = Path(__file__).resolve().parents[1]
LOCAL_PATHS = ROOT / "config/local_paths.json"
ATLAS_SOURCE = (
    ROOT / "assets_queue/advance_format/sources/advance_format_outliers_01.png"
)
ATLAS_RGBA = (
    ROOT / "assets_queue/advance_format/masters/advance_format_outliers_01_rgba.png"
)
REFERENCE_DIR = ROOT / "assets_queue/advance_format/vanilla_references"
REFERENCE_BOARD = REFERENCE_DIR / "installed_eu5_advance_cutouts.png"
SURFACE_AUDIT = ROOT / "docs/m11/advance_icon_surface_audit.csv"
FORMAT_GUIDE = ROOT / "docs/m11/ADVANCE_ICON_FORMAT.md"
CONTACT_SHEET = ROOT / "docs/m11/ADVANCE_ICON_FORMAT_CONTACT_SHEET.png"
SURFACE_PREVIEW = ROOT / "docs/m11/ADVANCE_ICON_SURFACE_PREVIEW.png"
MANIFEST = ROOT / "docs/m11/advance_icon_format_manifest.json"
SIZE = (256, 256)
EXPECTED_ASSETS = 886

OUTLIER_QUADRANTS = {
    "antq_advance_regional_law_codes_256.png": "top_left",
    "antq_advance_high_empire_administration_256.png": "top_right",
    "antq_advance_seasonal_markets_256.png": "bottom_left",
    "antq_advance_standing_administration_256.png": "bottom_right",
}


@dataclass(frozen=True)
class Surface:
    file: str
    expression: str
    count: int
    surface: str
    display: str
    local_mask: str


SURFACES = (
    Surface(
        "main_menu/gui/shared/building_tooltips.gui",
        "GetAdvanceIcon",
        1,
        "building requirement tooltip",
        "small prerequisite icon",
        "none at asset call",
    ),
    Surface(
        "main_menu/gui/shared/advances_tooltips.gui",
        "GetAdvanceIcon",
        3,
        "current-research and advance tooltips",
        "79%, 97%, and 100% icon wells",
        "mixed: none, round, and square-round",
    ),
    Surface(
        "in_game/gui/messages.gui",
        "GetAdvanceIcon",
        2,
        "research message decorations",
        "60x60",
        "none",
    ),
    Surface(
        "in_game/gui/technology_lateralview.gui",
        "GetAdvanceIcon",
        2,
        "technology current-research panels",
        "compact and large current-research wells",
        "none at asset call",
    ),
    Surface(
        "in_game/gui/technology_lateralview.gui",
        "GetChoiceIcon",
        1,
        "technology-tree choice node",
        "tree node",
        "GUI node chrome only",
    ),
    Surface(
        "in_game/gui/agenda_view.gui",
        "GetAdvanceIcon",
        1,
        "agenda current-research button",
        "65% of round top-navigation well",
        "none",
    ),
    Surface(
        "in_game/gui/advances_lateralview.gui",
        "GetAdvanceIcon",
        3,
        "research list, queue, and age cards",
        "full round/card wells",
        "mixed",
    ),
    Surface(
        "in_game/gui/hud_topbar.gui",
        "GetAdvanceIcon",
        1,
        "HUD current-research button",
        "65% of round topbar well",
        "none",
    ),
    Surface(
        "in_game/gui/shared/combat_tooltips.gui",
        "GetAdvanceIcon",
        2,
        "combat unlock prerequisites",
        "small prerequisite icons",
        "none at asset call",
    ),
)

REFERENCE_FILES = (
    "administrative_leadership.png",
    "bureaucracy_law_advance.png",
    "markets_for_salt.png",
    "legalism_advance.png",
    "installed_eu5_advance_cutouts.png",
)


def png_bytes(image: Image.Image) -> bytes:
    stream = io.BytesIO()
    image.save(stream, format="PNG", optimize=True)
    return stream.getvalue()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assets() -> tuple[AdvanceIcon, ...]:
    combined = (*ADVANCE_ICONS, *direct_assets())
    if len(combined) != EXPECTED_ASSETS:
        raise ValueError(
            f"expected {EXPECTED_ASSETS} reviewed advance assets, found {len(combined)}"
        )
    masters = [asset.master for asset in combined]
    repeated = {
        master for master in masters if masters.count(master) > 1
    }
    expected_shared = {
        "assets_queue/generated/antq_advance_migrations_256.png"
    }
    if repeated != expected_shared or masters.count(next(iter(expected_shared))) != 2:
        raise ValueError(
            "only the two mandatory late engine slots may share the reviewed "
            "Migrations master"
        )
    return combined


def legacy_round_alpha(image: Image.Image) -> Image.Image:
    """Retain reviewed RGB artwork while removing square GUI corners."""
    result = image.convert("RGBA")
    scale = 4
    mask = Image.new("L", (SIZE[0] * scale, SIZE[1] * scale), 0)
    draw = ImageDraw.Draw(mask)
    inset = 7 * scale
    draw.ellipse(
        (inset, inset, SIZE[0] * scale - inset - 1, SIZE[1] * scale - inset - 1),
        fill=255,
    )
    mask = mask.filter(ImageFilter.GaussianBlur(6))
    mask = mask.resize(SIZE, Image.Resampling.LANCZOS)
    result.putalpha(mask)
    return result


def atlas_piece(quadrant: str) -> Image.Image:
    with Image.open(ATLAS_RGBA) as opened:
        image = opened.convert("RGBA")
    if image.width != image.height or image.width % 2:
        raise ValueError(f"four-up RGBA atlas has invalid dimensions {image.size}")
    half = image.width // 2
    box = {
        "top_left": (0, 0, half, half),
        "top_right": (half, 0, image.width, half),
        "bottom_left": (0, half, half, image.height),
        "bottom_right": (half, half, image.width, image.height),
    }[quadrant]
    piece = image.crop(box)
    threshold = piece.getchannel("A").point(lambda value: 255 if value >= 12 else 0)
    bounds = threshold.getbbox()
    if bounds is None:
        raise ValueError(f"{quadrant}: four-up atlas cell is empty")
    piece = piece.crop(bounds)
    maximum = 220
    scale = min(maximum / piece.width, maximum / piece.height)
    size = (
        max(1, round(piece.width * scale)),
        max(1, round(piece.height * scale)),
    )
    piece = piece.resize(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    canvas.alpha_composite(
        piece,
        ((SIZE[0] - piece.width) // 2, (SIZE[1] - piece.height) // 2),
    )
    return canvas


def expected_master(asset: AdvanceIcon) -> Image.Image:
    path = ROOT / asset.master
    quadrant = OUTLIER_QUADRANTS.get(path.name)
    if quadrant:
        return atlas_piece(quadrant)
    with Image.open(path) as opened:
        if opened.size != SIZE:
            raise ValueError(f"{asset.master}: expected {SIZE}, found {opened.size}")
        candidate = opened.convert("RGBA")
    # Preserve native cutouts from the four-up chroma pipeline. Older square
    # scene masters receive the deterministic round-alpha compatibility mask.
    alpha = candidate.getchannel("A")
    bounds = alpha.point(lambda value: 255 if value >= 12 else 0).getbbox()
    perimeter = (
        list(alpha.crop((0, 0, SIZE[0], 1)).get_flattened_data())
        + list(alpha.crop((0, SIZE[1] - 1, SIZE[0], SIZE[1])).get_flattened_data())
        + list(alpha.crop((0, 1, 1, SIZE[1] - 1)).get_flattened_data())
        + list(alpha.crop((SIZE[0] - 1, 1, SIZE[0], SIZE[1] - 1)).get_flattened_data())
    )
    if (
        bounds is not None
        and bounds[0] >= 3 and bounds[1] >= 3
        and bounds[2] <= SIZE[0] - 3 and bounds[3] <= SIZE[1] - 3
        and max(perimeter) == 0
    ):
        return candidate
    return legacy_round_alpha(candidate)


def alpha_metrics(image: Image.Image) -> dict[str, object]:
    alpha = image.getchannel("A")
    values = list(alpha.get_flattened_data())
    active = sum(value >= 12 for value in values)
    opaque = sum(value >= 245 for value in values)
    threshold = alpha.point(lambda value: 255 if value >= 12 else 0)
    bounds = threshold.getbbox()
    perimeter = (
        list(alpha.crop((0, 0, SIZE[0], 1)).get_flattened_data())
        + list(
            alpha.crop((0, SIZE[1] - 1, SIZE[0], SIZE[1])).get_flattened_data()
        )
        + list(alpha.crop((0, 1, 1, SIZE[1] - 1)).get_flattened_data())
        + list(
            alpha.crop(
                (SIZE[0] - 1, 1, SIZE[0], SIZE[1] - 1)
            ).get_flattened_data()
        )
    )
    return {
        "active_fraction": round(active / len(values), 6),
        "opaque_fraction": round(opaque / len(values), 6),
        "alpha_bbox": list(bounds) if bounds else [],
        "perimeter_max": max(perimeter),
    }


def validate_alpha(asset: AdvanceIcon, image: Image.Image) -> list[str]:
    failures: list[str] = []
    if image.mode != "RGBA" or image.size != SIZE:
        return [f"{asset.master}: master must be RGBA {SIZE[0]}x{SIZE[1]}"]
    metrics = alpha_metrics(image)
    active = float(metrics["active_fraction"])
    bounds = metrics["alpha_bbox"]
    if not 0.10 <= active <= 0.79:
        failures.append(f"{asset.master}: implausible alpha coverage {active:.3f}")
    if int(metrics["perimeter_max"]) != 0:
        failures.append(f"{asset.master}: alpha reaches the square perimeter")
    if not bounds or min(bounds[0], bounds[1]) < 3 or max(bounds[2], bounds[3]) > 253:
        failures.append(f"{asset.master}: subject violates the 3px safe perimeter")
    corners = (
        image.getpixel((0, 0))[3],
        image.getpixel((255, 0))[3],
        image.getpixel((0, 255))[3],
        image.getpixel((255, 255))[3],
    )
    if any(corners):
        failures.append(f"{asset.master}: square corners are not transparent")
    return failures


def game_root() -> Path:
    config = json.loads(LOCAL_PATHS.read_text(encoding="utf-8-sig"))
    return Path(config["game_dir"]) / "game"


def surface_rows() -> tuple[list[dict[str, str]], list[str]]:
    failures: list[str] = []
    game = game_root()
    rows: list[dict[str, str]] = []
    for surface in SURFACES:
        path = game / surface.file
        if not path.is_file():
            failures.append(f"missing installed GUI surface {path}")
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        count = text.count(surface.expression)
        if count != surface.count:
            failures.append(
                f"{surface.file}: {surface.expression} count is {count}, "
                f"expected {surface.count}"
            )
        rows.append(
            {
                "file": surface.file,
                "expression": surface.expression,
                "count": str(surface.count),
                "surface": surface.surface,
                "display": surface.display,
                "local_mask": surface.local_mask,
                "asset_requirement": "RGBA; transparent perimeter; centered 3px-safe subject",
            }
        )
    all_gui_calls = 0
    for path in game.rglob("*.gui"):
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        all_gui_calls += text.count("GetAdvanceIcon")
        all_gui_calls += text.count("GetChoiceIcon")
    expected = sum(surface.count for surface in SURFACES)
    if all_gui_calls != expected:
        failures.append(
            f"installed GUI union has {all_gui_calls} advance-icon calls, "
            f"ledger covers {expected}"
        )
    return rows, failures


def csv_payload(rows: list[dict[str, str]]) -> str:
    fields = (
        "file",
        "expression",
        "count",
        "surface",
        "display",
        "local_mask",
        "asset_requirement",
    )
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def format_guide(rows: list[dict[str, str]]) -> str:
    calls = sum(int(row["count"]) for row in rows)
    return f"""# Advance Icon Format

Installed EU5 build 24187685 exposes advance art through {calls} calls across
{len(rows)} GUI contexts. Some add a round mask; the agenda, HUD, messages, and
other contexts do not. The asset itself must therefore be safe everywhere.

## Required master

- 256x256 RGBA PNG; BC7 sRGB DDS with mipmaps.
- Fully transparent square perimeter and corners; visible alpha stays inside a
  3px safe perimeter.
- One compact, centered subject readable at 60px. Preserve useful reviewed art;
  legacy scene art may use the checked circular-alpha retrofit.
- New art must be generated four-up against actual installed EU5 advance
  cutouts, on a flat chroma-key field, then split and keyed locally.
- No baked square backdrop, border, frame, text, watermark, yellow wash,
  modern object, or subject touching the edge.

Run `python tools/m11_advance_format.py --write` after changing advance art, then
`--check`. The generated surface ledger is
`docs/m11/advance_icon_surface_audit.csv`; the contact sheet is reviewed in
actual circular context.

## Targeted replacements

Regional Law Codes, High Empire Administration, Seasonal Markets, Standing
Administration, and all 440 S2-P3 regional additions use EU5-referenced
four-up cutout sheets. Compatible earlier illustrations retain their reviewed
compositions under the deterministic alpha contract.
"""


def preview_icon(image: Image.Image, size: int) -> Image.Image:
    resized = image.resize((size, size), Image.Resampling.LANCZOS)
    return resized


def contact_sheet(asset_list: tuple[AdvanceIcon, ...]) -> Image.Image:
    columns = 20
    tile = 96
    label = 22
    rows = math.ceil(len(asset_list) / columns)
    canvas = Image.new("RGB", (columns * tile, rows * (tile + label)), "#101720")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    for index, asset in enumerate(asset_list):
        with Image.open(ROOT / asset.master) as opened:
            icon = preview_icon(opened.convert("RGBA"), 76)
        x = index % columns * tile
        y = index // columns * (tile + label)
        draw.ellipse((x + 9, y + 9, x + 86, y + 86), fill="#294454", outline="#9e8252", width=2)
        canvas.paste(icon, (x + 10, y + 10), icon)
        slug = Path(asset.master).stem.removeprefix("antq_advance_")
        draw.text((x + 3, y + 97), f"{index + 1:03} {slug[:10]}", fill="#e5dcc8", font=font)
    return canvas


def surface_preview(asset_list: tuple[AdvanceIcon, ...]) -> Image.Image:
    by_name = {Path(asset.master).name: asset for asset in asset_list}
    names = (
        "antq_advance_regional_law_codes_256.png",
        "antq_advance_high_empire_administration_256.png",
        "antq_advance_seasonal_markets_256.png",
        "antq_advance_standing_administration_256.png",
        "antq_advance_public_granaries_256.png",
        "antq_advance_imperial_archives_256.png",
    )
    sizes = (26, 42, 60, 96)
    cell_w, cell_h = 150, 126
    canvas = Image.new("RGB", (len(sizes) * cell_w, len(names) * cell_h + 34), "#111821")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    for column, size in enumerate(sizes):
        draw.text((column * cell_w + 8, 10), f"{size}px asset preview", fill="#efe4ce", font=font)
    for row, name in enumerate(names):
        asset = by_name[name]
        with Image.open(ROOT / asset.master) as opened:
            rgba = opened.convert("RGBA")
        for column, size in enumerate(sizes):
            x = column * cell_w
            y = row * cell_h + 34
            center_x = x + cell_w // 2
            center_y = y + 52
            radius = max(18, size // 2 + 6)
            draw.ellipse(
                (
                    center_x - radius,
                    center_y - radius,
                    center_x + radius,
                    center_y + radius,
                ),
                fill="#2b4b5c",
                outline="#a98a56",
                width=2,
            )
            icon = preview_icon(rgba, size)
            canvas.paste(icon, (center_x - size // 2, center_y - size // 2), icon)
            if column == 0:
                slug = name.removeprefix("antq_advance_").removesuffix("_256.png")
                draw.text((x + 4, y + 104), slug[:24], fill="#d7ccb8", font=font)
    return canvas


def manifest_payload(
    asset_list: tuple[AdvanceIcon, ...],
    rows: list[dict[str, str]],
) -> str:
    config = json.loads(LOCAL_PATHS.read_text(encoding="utf-8-sig"))
    entries = []
    for asset in asset_list:
        master = ROOT / asset.master
        texture = ROOT / asset.texture
        with Image.open(master) as opened:
            metrics = alpha_metrics(opened.convert("RGBA"))
        entries.append(
            {
                "master": asset.master,
                "texture": asset.texture,
                "master_sha256": sha256(master),
                "texture_sha256": sha256(texture),
                **metrics,
            }
        )
    payload = {
        "game_build_id": config["game_build_id"],
        "asset_count": len(asset_list),
        "gui_call_count": sum(int(row["count"]) for row in rows),
        "gui_context_count": len(rows),
        "contract": {
            "master": "256x256 RGBA PNG",
            "texture": "256x256 BC7 sRGB DDS with mipmaps",
            "perimeter": "fully transparent; visible alpha inside 3px",
            "future_generation": "four-up; installed EU5 cutout references; chroma-key removal",
        },
        "targeted_four_up": {
            "source": str(ATLAS_SOURCE.relative_to(ROOT)).replace("\\", "/"),
            "rgba": str(ATLAS_RGBA.relative_to(ROOT)).replace("\\", "/"),
            "source_sha256": sha256(ATLAS_SOURCE),
            "rgba_sha256": sha256(ATLAS_RGBA),
            "quadrants": OUTLIER_QUADRANTS,
        },
        "vanilla_references": {
            name: sha256(REFERENCE_DIR / name) for name in REFERENCE_FILES
        },
        "assets": entries,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def write() -> None:
    asset_list = assets()
    for asset in asset_list:
        master = ROOT / asset.master
        texture = ROOT / asset.texture
        formatted = expected_master(asset)
        rendered = png_bytes(formatted)
        changed = master.read_bytes() != rendered
        if changed:
            master.write_bytes(rendered)
        if changed or not texture.is_file():
            convert(master, texture, "bc7", True)
    rows, failures = surface_rows()
    if failures:
        raise ValueError("\n".join(failures))
    SURFACE_AUDIT.write_text(csv_payload(rows), encoding="utf-8", newline="\n")
    FORMAT_GUIDE.write_text(format_guide(rows), encoding="utf-8", newline="\n")
    CONTACT_SHEET.write_bytes(png_bytes(contact_sheet(asset_list)))
    SURFACE_PREVIEW.write_bytes(png_bytes(surface_preview(asset_list)))
    MANIFEST.write_text(
        manifest_payload(asset_list, rows),
        encoding="utf-8",
        newline="\n",
    )


def check() -> list[str]:
    failures: list[str] = []
    asset_list = assets()
    for required in (
        ATLAS_SOURCE,
        ATLAS_RGBA,
        REFERENCE_BOARD,
        *(REFERENCE_DIR / name for name in REFERENCE_FILES),
    ):
        if not required.is_file():
            failures.append(f"missing advance-format source {required.relative_to(ROOT)}")
    if failures:
        return failures
    for asset in asset_list:
        master = ROOT / asset.master
        texture = ROOT / asset.texture
        if not master.is_file() or not texture.is_file():
            failures.append(f"missing formatted chain for {asset.master}")
            continue
        expected = png_bytes(expected_master(asset))
        if master.read_bytes() != expected:
            failures.append(f"{asset.master}: stale advance alpha format")
        with Image.open(master) as opened:
            failures.extend(validate_alpha(asset, opened.convert("RGBA")))
            if opened.mode != "RGBA":
                failures.append(f"{asset.master}: PNG storage mode is {opened.mode}, expected RGBA")
        details = identify(texture)
        if details != {
            "format": "DDS",
            "width": "256",
            "height": "256",
            "depth": "8",
            "channels": "srgba 4.0",
        }:
            failures.append(f"{asset.texture}: invalid formatted DDS {details}")
    rows, surface_failures = surface_rows()
    failures.extend(surface_failures)
    expected_text = (
        (SURFACE_AUDIT, csv_payload(rows)),
        (FORMAT_GUIDE, format_guide(rows)),
        (MANIFEST, manifest_payload(asset_list, rows)),
    )
    for path, expected in expected_text:
        if not path.is_file():
            failures.append(f"missing generated format audit {path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8-sig") != expected:
            failures.append(f"stale generated format audit {path.relative_to(ROOT)}")
    expected_images = (
        (CONTACT_SHEET, png_bytes(contact_sheet(asset_list))),
        (SURFACE_PREVIEW, png_bytes(surface_preview(asset_list))),
    )
    for path, expected in expected_images:
        if not path.is_file():
            failures.append(f"missing generated format preview {path.relative_to(ROOT)}")
        elif path.read_bytes() != expected:
            failures.append(f"stale generated format preview {path.relative_to(ROOT)}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.write:
            write()
        failures = check()
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"m11_advance_format: FAIL\n  - {exc}", file=sys.stderr)
        return 1
    if failures:
        print("m11_advance_format: FAIL", file=sys.stderr)
        for failure in sorted(set(failures)):
            print(f"  - {failure}", file=sys.stderr)
        return 1
    print(
        "m11_advance_format: PASS "
        f"({EXPECTED_ASSETS} RGBA/BC7 icons; 16 installed GUI calls; "
        "444 EU5-referenced cutouts)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
