#!/usr/bin/env python3
"""Render and enforce vanilla-style transparent cutouts for every custom trade good."""

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


ROOT = Path(__file__).resolve().parents[1]
SHEET_DIR = ROOT / "assets_queue/generated_sources/trade_goods_cutouts"
MASTER_DIR = ROOT / "assets_queue/generated"
ROMAN_MASTER_DIR = MASTER_DIR / "roman_economy"
CRAFT_MASTER_DIR = MASTER_DIR / "ancient_goods_expansion"
ICON_DIR = ROOT / "main_menu/gfx/interface/icons/trade_goods"
GOODS_CSV = ROOT / "docs/m5/custom_goods.csv"
LEDGER = ROOT / "docs/m5/trade_good_cutouts.csv"
CONTACT = ROOT / "docs/m5/TRADE_GOOD_CUTOUTS_CONTACT.png"
DDS = ROOT / "tools/dds.py"
CELLS = ("top_left", "top_right", "bottom_left", "bottom_right")

SHEETS = {
    "goods_cutouts_01.png": (
        "4f3689e57956f21c77a01e0c1f86cc935adf74313e06d44c91b53421bd92c9df",
        ("antq_olive_oil", "antq_preserved_fish", "antq_grain_products", "antq_perfumes"),
    ),
    "goods_cutouts_02.png": (
        "38a147198b04bf09e1288a50c0013b2316bbcecb70d2ef1a358b8b35c81216e6",
        ("antq_wax_goods", "antq_soap", "antq_bronze_wares", "antq_lead_wares"),
    ),
    "goods_cutouts_03.png": (
        "6284e531a98e2d7923fb6b3576b799d98c30270fe32fe0ed1c01633d25c49ad5",
        ("antq_fine_ceramics", "antq_glasswares", "antq_iron_hardware", "antq_leather_goods"),
    ),
    "goods_cutouts_04.png": (
        "5fa1c4bc74c0925c7324ddfbc06c0155903323b3eef1e4ef3403fd9e3d8630ed",
        ("antq_cordage", "antq_parchment", "antq_lacquerware", "antq_amber_ornaments"),
    ),
    "goods_cutouts_05.png": (
        "bf6a6953e51b3c82b4b1b8486dcaa6babd1ec62999b864aa7691435b7fca5c87",
        ("antq_glass_beads", "antq_carpets", "antq_felt_goods", "antq_sailcloth"),
    ),
    "goods_cutouts_06.png": (
        "6fba1c220d69db07047916a0a7f4c6698fd97cca07edadbf0428df158ac3a85d",
        ("antq_dates", "antq_sesame", "antq_tree_nuts", "antq_coconuts"),
    ),
    "goods_cutouts_07.png": (
        "4f59708245eb95b18a09298afd810328c3c6901787f99be259494d084ae7a6c8",
        ("antq_cheese_curds", "antq_cured_meat", "antq_dried_fruit", "antq_nut_pastes"),
    ),
    "goods_cutouts_08.png": (
        "e1d7b32be04c634c2f5940a383a6ef245440d4927b64a72bf2fd98b9df181e32",
        ("antq_sesame_oil", "antq_coconut_products", "antq_rice_wine", "antq_soy_condiments"),
    ),
}

PRESERVED_DIRECT = {
    "antq_papyrus",
    "antq_silphium",
    "antq_naphtha",
    "antq_jade",
    "antq_camels",
}
BARLEY_SOURCE = ROOT / "assets_queue/generated_sources/antq_barley_source.png"
BARLEY_HASH = "082e6302579b430313af9fb3e74adc11bf3cfcbb1b0afc241b5d01d56c0003d5"
ROMAN_KEYS = set(SHEETS["goods_cutouts_01.png"][1]) | set(SHEETS["goods_cutouts_02.png"][1])
CRAFT_KEYS = (
    set(SHEETS["goods_cutouts_03.png"][1])
    | set(SHEETS["goods_cutouts_04.png"][1])
    | set(SHEETS["goods_cutouts_05.png"][1])
    | {"antq_barley"}
)


def records() -> list[tuple[str, str, str]]:
    rows = [
        (key, sheet, cell)
        for sheet, (_digest, keys) in SHEETS.items()
        for key, cell in zip(keys, CELLS, strict=True)
    ]
    rows.append(("antq_barley", BARLEY_SOURCE.name, "direct_rematte"))
    return rows


def custom_keys() -> set[str]:
    with GOODS_CSV.open(encoding="utf-8-sig", newline="") as stream:
        return {row["key"] for row in csv.DictReader(stream)}


def cell_box(size: tuple[int, int], cell: str) -> tuple[int, int, int, int]:
    width, height = size
    if width != height or width % 2:
        raise ValueError(f"four-up cutout sheet must be even and square, got {size}")
    half = width // 2
    index = CELLS.index(cell)
    column, row = index % 2, index // 2
    return column * half, row * half, (column + 1) * half, (row + 1) * half


def fit_rgba(source: Image.Image, alpha: np.ndarray, extent: int = 116) -> Image.Image:
    rgba = np.asarray(source.convert("RGBA"), dtype=np.uint8).copy()
    rgba[:, :, 3] = alpha
    ys, xs = np.where(alpha > 12)
    if not len(xs):
        raise ValueError("cutout has no foreground")
    margin = max(2, min(source.size) // 128)
    left, right = max(0, int(xs.min()) - margin), min(source.width, int(xs.max()) + margin + 1)
    top, bottom = max(0, int(ys.min()) - margin), min(source.height, int(ys.max()) + margin + 1)
    crop = Image.fromarray(rgba, "RGBA").crop((left, top, right, bottom))
    scale = min(extent / crop.width, extent / crop.height)
    size = (max(1, round(crop.width * scale)), max(1, round(crop.height * scale)))
    crop = crop.resize(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    canvas.alpha_composite(crop, ((128 - crop.width) // 2, (128 - crop.height) // 2))
    return canvas


def magenta_cutout(source: Image.Image) -> Image.Image:
    rgb = np.asarray(source.convert("RGB"), dtype=np.float32)
    distance = np.maximum.reduce((np.abs(rgb[:, :, 0] - 255), rgb[:, :, 1], np.abs(rgb[:, :, 2] - 255)))
    distance_alpha = np.clip((distance - 3) * (255 / 42), 0, 255)
    # Darker generated shadows remain magenta in hue even when distant from #ff00ff.
    hue_score = np.abs(rgb[:, :, 0] - rgb[:, :, 2]) + 1.5 * rgb[:, :, 1]
    hue_alpha = np.clip((hue_score - 25) * (255 / 80), 0, 255)
    alpha = np.minimum(distance_alpha, hue_alpha).astype(np.uint8)
    neutral_dark = (rgb.max(axis=2) < 90) & ((rgb.max(axis=2) - rgb.min(axis=2)) < 18)
    alpha[neutral_dark] = distance_alpha[neutral_dark].astype(np.uint8)
    alpha[alpha < 40] = 0

    # Remove chroma spill only on antialiased edge pixels; opaque purples remain intact.
    edge = alpha < 245
    spill = np.maximum(0, np.minimum(rgb[:, :, 0], rgb[:, :, 2]) - rgb[:, :, 1])
    correction = spill * (1 - 0.25 * alpha.astype(np.float32) / 255)
    rgb[:, :, 0][edge] = np.maximum(rgb[:, :, 1][edge], rgb[:, :, 0][edge] - correction[edge])
    rgb[:, :, 2][edge] = np.maximum(rgb[:, :, 1][edge], rgb[:, :, 2][edge] - correction[edge])
    rgba = Image.fromarray(np.dstack((rgb.astype(np.uint8), alpha)), "RGBA")
    return fit_rgba(rgba, alpha)


def barley_cutout(source: Image.Image) -> Image.Image:
    rgb = np.asarray(source.convert("RGB"), dtype=np.float32)
    maximum = rgb.max(axis=2)
    warm = np.maximum(0, rgb[:, :, 0] - rgb[:, :, 2])
    score = np.maximum((maximum - 38) / 42, warm / 35)
    alpha = np.clip(score * 255, 0, 255).astype(np.uint8)
    alpha = np.asarray(
        Image.fromarray(alpha, "L").filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.GaussianBlur(1.4)),
        dtype=np.uint8,
    )
    return fit_rgba(source, alpha)


def plate_metrics(image: Image.Image) -> tuple[float, float]:
    alpha = np.asarray(image.convert("RGBA").getchannel("A"), dtype=np.float32) / 255
    yy, xx = np.ogrid[:128, :128]
    radius = np.sqrt((xx - 63.5) ** 2 + (yy - 63.5) ** 2)
    ring = (radius >= 48) & (radius <= 58)
    return float(alpha.mean()), float((alpha[ring] > 0.78).mean())


def has_geometric_plate(image: Image.Image) -> bool:
    mean_alpha, ring_coverage = plate_metrics(image)
    return mean_alpha >= 0.67 or ring_coverage >= 0.82


def dds(source: Path, target: Path) -> None:
    subprocess.run(
        [sys.executable, str(DDS), "convert", str(source), str(target), "--compression", "dxt5"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.DEVNULL,
    )


def retained_targets(key: str) -> list[Path]:
    targets = [MASTER_DIR / f"{key}.png"]
    if key in ROMAN_KEYS:
        targets.append(ROMAN_MASTER_DIR / f"{key}.png")
    if key in CRAFT_KEYS:
        targets.append(CRAFT_MASTER_DIR / f"{key}.png")
    return targets


def ledger_text() -> str:
    stream = StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(("key", "source", "cell", "result", "style_reference"))
    for key, source, cell in records():
        writer.writerow((key, source, cell, "transparent_object_cutout", "installed EU5 wheat/amber/cloth/pottery/iron/leather/glass/beeswax"))
    for key in sorted(PRESERVED_DIRECT):
        writer.writerow((key, "existing reviewed direct master", "direct", "transparent_object_cutout", "installed EU5 direct trade-good icons"))
    return stream.getvalue()


def write_contact(keys: list[str]) -> None:
    tile, label_height, columns = 156, 24, 8
    rows = (len(keys) + columns - 1) // columns
    contact = Image.new("RGBA", (columns * tile, rows * (tile + label_height)), (40, 45, 54, 255))
    draw = ImageDraw.Draw(contact)
    for index, key in enumerate(keys):
        x, y = (index % columns) * tile, (index // columns) * (tile + label_height)
        for cy in range(8, 136, 16):
            for cx in range(8, 136, 16):
                color = (222, 222, 222, 255) if ((cx + cy) // 16) % 2 else (154, 154, 154, 255)
                draw.rectangle((x + cx, y + cy, x + cx + 15, y + cy + 15), fill=color)
        with Image.open(MASTER_DIR / f"{key}.png") as icon:
            contact.alpha_composite(icon.convert("RGBA"), (x + 8, y + 8))
        draw.text((x + 4, y + 140), key.removeprefix("antq_"), fill=(236, 239, 244, 255))
    contact.convert("RGB").save(CONTACT)


def write() -> None:
    for directory in (MASTER_DIR, ROMAN_MASTER_DIR, CRAFT_MASTER_DIR, ICON_DIR, LEDGER.parent):
        directory.mkdir(parents=True, exist_ok=True)
    opened: dict[str, Image.Image] = {}
    rendered: dict[str, Image.Image] = {}
    for key, sheet, cell in records():
        if cell == "direct_rematte":
            if hashlib.sha256(BARLEY_SOURCE.read_bytes()).hexdigest() != BARLEY_HASH:
                raise ValueError("reviewed barley source hash drift")
            with Image.open(BARLEY_SOURCE) as source:
                rendered[key] = barley_cutout(source)
            continue
        if sheet not in opened:
            path = SHEET_DIR / sheet
            expected = SHEETS[sheet][0]
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                raise ValueError(f"missing or changed reviewed cutout atlas {path.relative_to(ROOT)}")
            opened[sheet] = Image.open(path).convert("RGBA")
        rendered[key] = magenta_cutout(opened[sheet].crop(cell_box(opened[sheet].size, cell)))

    for key, icon in rendered.items():
        if has_geometric_plate(icon):
            raise ValueError(f"{key} still has geometric plate occupancy")
        targets = retained_targets(key)
        for target in targets:
            target.parent.mkdir(parents=True, exist_ok=True)
            icon.save(target)
        dds(targets[0], ICON_DIR / f"icon_goods_{key}.dds")
    for key in sorted(PRESERVED_DIRECT):
        source_path = MASTER_DIR / f"{key}.png"
        if not source_path.is_file():
            raise ValueError(f"missing reviewed direct master {source_path.relative_to(ROOT)}")
        with Image.open(source_path) as source:
            rgba = source.convert("RGBA")
            alpha = np.asarray(rgba.getchannel("A"), dtype=np.uint8)
            icon = fit_rgba(rgba, alpha) if rgba.size != (128, 128) else rgba.copy()
        if has_geometric_plate(icon):
            raise ValueError(f"{key} preserved direct master has geometric plate occupancy")
        icon.save(source_path)
        dds(source_path, ICON_DIR / f"icon_goods_{key}.dds")
    for image in opened.values():
        image.close()
    LEDGER.write_text(ledger_text(), encoding="utf-8-sig", newline="")
    write_contact(sorted(custom_keys()))


def check() -> None:
    failures: list[str] = []
    expected = custom_keys()
    mapped = {key for key, _sheet, _cell in records()} | PRESERVED_DIRECT
    if mapped != expected:
        failures.append(f"cutout coverage mismatch: missing={sorted(expected - mapped)} extra={sorted(mapped - expected)}")
    if not LEDGER.is_file() or LEDGER.read_text(encoding="utf-8-sig") != ledger_text():
        failures.append("trade-good cutout ledger is stale")
    if not CONTACT.is_file():
        failures.append("trade-good cutout contact sheet is missing")
    for sheet, (digest, _keys) in SHEETS.items():
        path = SHEET_DIR / sheet
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            failures.append(f"missing or changed reviewed cutout atlas {path.relative_to(ROOT)}")
    hashes: dict[str, str] = {}
    for key in sorted(expected):
        master = MASTER_DIR / f"{key}.png"
        icon = ICON_DIR / f"icon_goods_{key}.dds"
        if not master.is_file() or not icon.is_file():
            failures.append(f"{key} is missing direct-cutout master or DDS")
            continue
        with Image.open(master) as image:
            if image.mode != "RGBA" or image.size != (128, 128):
                failures.append(f"{key} master must be 128x128 RGBA")
                continue
            mean_alpha, ring_coverage = plate_metrics(image)
            if has_geometric_plate(image):
                failures.append(f"{key} has geometric plate: alpha={mean_alpha:.3f} ring={ring_coverage:.3f}")
            if image.getpixel((0, 0))[3] != 0:
                failures.append(f"{key} master has an opaque corner")
        digest = hashlib.sha256(icon.read_bytes()).hexdigest()
        previous = hashes.setdefault(digest, key)
        if previous != key:
            failures.append(f"duplicate direct trade-good icons: {previous} and {key}")
        for retained in retained_targets(key)[1:]:
            if not retained.is_file() or retained.read_bytes() != master.read_bytes():
                failures.append(f"{key} retained owning-generator master is stale")
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
        print(f"m5_trade_good_cutouts: FAIL\n  - {exc}")
        return 1
    print(f"m5_trade_good_cutouts: PASS ({len(custom_keys())} transparent direct icons; zero geometric backplates)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
