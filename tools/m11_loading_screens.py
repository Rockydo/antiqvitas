#!/usr/bin/env python3
"""Build and validate ANTIQVITAS animated loading-screen depth plates.

The EU5 loading-scene scripts are additive in the installed build.  We retain
their engine-owned scene and image declarations, and instead VFS-override each
of the exact eight DDS texture paths they already reference. Plate 00 is the
reviewed opaque panorama; plates 01-07 are sparse, independently animated RGBA
depth fields derived from that panorama rather than opaque duplicate hardlinks.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from dds import convert, identify


ROOT = Path(__file__).resolve().parents[1]
CONTACT_SHEET = ROOT / "docs" / "m11" / "loading_screens_contact_sheet.png"
LAYER_CONTACT_SHEET = ROOT / "docs" / "m11" / "loading_depth_layers_contact.png"
LAYER_LEDGER = ROOT / "docs" / "m11" / "loading_depth_layers.csv"
LAYER_ROOT = ROOT / "loading_screen/gfx/loading_screen_assets/antq/layers"
DIMENSIONS = (3840, 2160)


@dataclass(frozen=True)
class LoadingScreen:
    key: str
    title: str
    scope: str
    source: str
    master: str
    texture: str


SCREENS = (
    LoadingScreen("ostia", "Ostia", "Ostia, AD 1", "assets_queue/generated_sources/antq_loading_ostia_ad1.png", "assets_queue/generated/antq_loading_ostia_ad1_3840x2160.png", "loading_screen/gfx/loading_screen_assets/antq/images/antq_loading_ostia_ad1.dds"),
    LoadingScreen("forum", "Augustan Forum", "Rome, AD 1", "assets_queue/generated_sources/antq_loading_forum_augustan_ad1.png", "assets_queue/generated/antq_loading_forum_augustan_ad1_3840x2160.png", "loading_screen/gfx/loading_screen_assets/antq/images/antq_loading_forum_augustan_ad1.dds"),
    LoadingScreen("alexandria", "Alexandria", "Alexandria, AD 1", "assets_queue/generated_sources/antq_loading_alexandria_ad1.png", "assets_queue/generated/antq_loading_alexandria_ad1_3840x2160.png", "loading_screen/gfx/loading_screen_assets/antq/images/antq_loading_alexandria_ad1.dds"),
    LoadingScreen("changan", "Chang'an", "Chang'an, AD 1", "assets_queue/generated_sources/antq_loading_changan_ad1.png", "assets_queue/generated/antq_loading_changan_ad1_3840x2160.png", "loading_screen/gfx/loading_screen_assets/antq/images/antq_loading_changan_ad1.dds"),
    LoadingScreen("meroe", "Meroë", "Meroë, AD 1", "assets_queue/generated_sources/antq_loading_meroe_ad1.png", "assets_queue/generated/antq_loading_meroe_ad1_3840x2160.png", "loading_screen/gfx/loading_screen_assets/antq/images/antq_loading_meroe_ad1.dds"),
    LoadingScreen("rhine", "Lower Rhine", "Lower Rhine, AD 1", "assets_queue/generated_sources/antq_loading_rhine_ad1.png", "assets_queue/generated/antq_loading_rhine_ad1_3840x2160.png", "loading_screen/gfx/loading_screen_assets/antq/images/antq_loading_rhine_ad1.dds"),
    LoadingScreen("teotihuacan", "Teotihuacan", "Teotihuacan, c. AD 100", "assets_queue/generated_sources/antq_loading_teotihuacan_ad100.png", "assets_queue/generated/antq_loading_teotihuacan_ad100_3840x2160.png", "loading_screen/gfx/loading_screen_assets/antq/images/antq_loading_teotihuacan_ad100.dds"),
    LoadingScreen("campus_martius", "Campus Martius", "Rome, AD 1", "assets_queue/generated_sources/antq_loading_campus_martius_ad1.png", "assets_queue/generated/antq_loading_campus_martius_ad1_3840x2160.png", "loading_screen/gfx/loading_screen_assets/antq/images/antq_loading_campus_martius_ad1.dds"),
    LoadingScreen("arikamedu", "Arikamedu", "Coromandel Coast, AD 1", "assets_queue/generated_sources/antq_loading_arikamedu_ad1.png", "assets_queue/generated/antq_loading_arikamedu_ad1_3840x2160.png", "loading_screen/gfx/loading_screen_assets/antq/images/antq_loading_arikamedu_ad1.dds"),
    LoadingScreen("jenne", "Jenne-jeno", "Inland Niger Delta, AD 1", "assets_queue/generated_sources/antq_loading_jennenjeno_ad1.png", "assets_queue/generated/antq_loading_jennenjeno_ad1_3840x2160.png", "loading_screen/gfx/loading_screen_assets/antq/images/antq_loading_jennenjeno_ad1.dds"),
    LoadingScreen("monte_alban", "Monte Alban", "Oaxaca, AD 1", "assets_queue/generated_sources/antq_loading_monte_alban_ad1.png", "assets_queue/generated/antq_loading_monte_alban_ad1_3840x2160.png", "loading_screen/gfx/loading_screen_assets/antq/images/antq_loading_monte_alban_ad1.dds"),
    LoadingScreen("palmyra", "Palmyra", "Syria, AD 1", "assets_queue/generated_sources/antq_loading_palmyra_ad1.png", "assets_queue/generated/antq_loading_palmyra_ad1_3840x2160.png", "loading_screen/gfx/loading_screen_assets/antq/images/antq_loading_palmyra_ad1.dds"),
    LoadingScreen("pompeii", "Pompeii", "Campania, AD 1", "assets_queue/generated_sources/antq_loading_pompeii_ad1.png", "assets_queue/generated/antq_loading_pompeii_ad1_3840x2160.png", "loading_screen/gfx/loading_screen_assets/antq/images/antq_loading_pompeii_ad1.dds"),
    LoadingScreen("ephesus", "Ephesus", "Asia, AD 1", "assets_queue/generated_sources/antq_loading_ephesus_ad1.png", "assets_queue/generated/antq_loading_ephesus_ad1_3840x2160.png", "loading_screen/gfx/loading_screen_assets/antq/images/antq_loading_ephesus_ad1.dds"),
    LoadingScreen("germanic_rhine", "Germanic Lower Rhine", "Lower Rhine, AD 1", "assets_queue/generated_sources/antq_loading_lower_rhine_germanic_ad1.png", "assets_queue/generated/antq_loading_lower_rhine_germanic_ad1_3840x2160.png", "loading_screen/gfx/loading_screen_assets/antq/images/antq_loading_lower_rhine_germanic_ad1.dds"),
    LoadingScreen("camulodunum", "Camulodunum", "Britain, AD 1", "assets_queue/generated_sources/antq_loading_camulodunum_ad1.png", "assets_queue/generated/antq_loading_camulodunum_ad1_3840x2160.png", "loading_screen/gfx/loading_screen_assets/antq/images/antq_loading_camulodunum_ad1.dds"),
)

# All currently selectable scene keys. Every inherited scene receives one
# reviewed ancient panorama and its seven true alpha/depth overlays.
SCENE_ASSIGNMENTS = {
    "rossbach": "germanic_rhine", "florence": "pompeii", "zheng_he": "changan",
    "martin_luther": "forum", "damascus_ambassadors": "palmyra",
    "deccan": "arikamedu", "aztec": "teotihuacan", "iroquois_ambush": "monte_alban",
    "ashanti": "jenne", "white_mountain": "camulodunum", "hansa": "ephesus",
}


def texture_targets(scene_name: str) -> tuple[Path, ...]:
    return tuple(
        ROOT / "loading_screen" / "gfx" / "loading_screen_assets" / "00" / "images"
        / f"loading_screen_{scene_name}_{index:02d}.dds"
        for index in range(8)
    )


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def layer_texture(screen: LoadingScreen, index: int) -> Path:
    if index == 0:
        return ROOT / screen.texture
    return LAYER_ROOT / f"{screen.key}_{index:02d}.dds"


def depth_masks(image: Image.Image) -> tuple[np.ndarray, ...]:
    """Return seven sparse masks tuned to the installed layer animation stack."""
    rgb = np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0
    height, width = rgb.shape[:2]
    yy, xx = np.mgrid[0:height, 0:width]
    x = xx.astype(np.float32) / max(1, width - 1)
    y = yy.astype(np.float32) / max(1, height - 1)
    luminance = rgb[:, :, 0] * 0.2126 + rgb[:, :, 1] * 0.7152 + rgb[:, :, 2] * 0.0722
    saturation = rgb.max(axis=2) - rgb.min(axis=2)
    gradient_y, gradient_x = np.gradient(luminance)
    detail = np.hypot(gradient_x, gradient_y)
    scale = max(float(np.percentile(detail, 97.5)), 0.001)
    detail = np.clip(detail / scale, 0.0, 1.0)

    def window(value: np.ndarray, low: float, high: float, softness: float = 0.06) -> np.ndarray:
        enter = np.clip((value - low) / softness, 0.0, 1.0)
        leave = np.clip((high - value) / softness, 0.0, 1.0)
        return enter * leave

    def radial(cx: float, cy: float, sx: float, sy: float) -> np.ndarray:
        return np.exp(-(((x - cx) / sx) ** 2 + ((y - cy) / sy) ** 2))

    content = np.clip(0.18 + detail * 0.62 + saturation * 0.32, 0.0, 1.0)
    masks = (
        window(y, 0.28, 1.02, 0.08) * (0.48 + content * 0.52),
        window(y, -0.02, 0.66, 0.10) * np.clip((luminance - 0.34) * 2.4, 0.0, 1.0),
        window(y, 0.24, 0.88) * radial(0.22, 0.57, 0.34, 0.40) * content,
        window(y, 0.24, 0.88) * radial(0.78, 0.57, 0.34, 0.40) * content,
        window(y, 0.58, 1.03, 0.09) * (0.38 + content * 0.62),
        window(y, 0.38, 1.03) * radial(0.30, 0.75, 0.25, 0.29) * np.clip(content * 1.3, 0.0, 1.0),
        window(y, 0.38, 1.03) * radial(0.72, 0.75, 0.25, 0.29) * np.clip(content * 1.3, 0.0, 1.0),
    )
    strengths = (0.84, 0.48, 0.67, 0.67, 0.78, 0.88, 0.88)
    result: list[np.ndarray] = []
    for mask, strength in zip(masks, strengths, strict=True):
        alpha = np.clip(mask * strength, 0.0, 1.0)
        alpha[alpha < 0.055] = 0.0
        result.append((alpha * 255.0).astype(np.uint8))
    return tuple(result)


def render_depth_plate(image: Image.Image, alpha: np.ndarray) -> Image.Image:
    rgba = np.asarray(image.convert("RGBA")).copy()
    rgba[:, :, 3] = alpha
    rgba[:, :, :3][alpha == 0] = 0
    return Image.fromarray(rgba, "RGBA")


def alpha_stats(path: Path) -> tuple[float, float, float]:
    with Image.open(path) as opened:
        alpha = opened.convert("RGBA").getchannel("A")
        histogram = alpha.histogram()
        pixels = opened.width * opened.height
    zero = histogram[0] * 100.0 / pixels
    opaque = histogram[255] * 100.0 / pixels
    mean = sum(index * count for index, count in enumerate(histogram)) / pixels
    return zero, opaque, mean


def write_layers() -> None:
    LAYER_ROOT.mkdir(parents=True, exist_ok=True)
    temp_root = ROOT / ".tmp"
    temp_root.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    previews: list[tuple[str, int, Image.Image]] = []
    for screen in SCREENS:
        with Image.open(ROOT / screen.master) as opened:
            panorama = opened.convert("RGB")
            masks = depth_masks(panorama)
            previews.append((screen.key, 0, panorama.resize((240, 135))))
            with tempfile.TemporaryDirectory(prefix="antq-loading-", dir=temp_root) as temporary:
                work = Path(temporary)
                for index, alpha in enumerate(masks, start=1):
                    plate = render_depth_plate(panorama, alpha)
                    png = work / f"{screen.key}_{index:02d}.png"
                    plate.save(png, optimize=True)
                    target = layer_texture(screen, index)
                    convert(png, target, "bc3", mipmaps=True)
                    preview = plate.resize((240, 135), Image.Resampling.LANCZOS)
                    previews.append((screen.key, index, preview))
        for index in range(8):
            texture = layer_texture(screen, index)
            zero, opaque, mean = alpha_stats(texture)
            rows.append({
                "screen": screen.key,
                "layer": str(index),
                "texture": str(texture.relative_to(ROOT)),
                "sha256": digest(texture),
                "zero_alpha_percent": f"{zero:.3f}",
                "opaque_alpha_percent": f"{opaque:.3f}",
                "mean_alpha": f"{mean:.3f}",
            })
    LAYER_LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LAYER_LEDGER.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "screen", "layer", "texture", "sha256",
                "zero_alpha_percent", "opaque_alpha_percent", "mean_alpha",
            ),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)

    tile_width, tile_height, label = 240, 135, 18
    canvas = Image.new("RGB", (8 * tile_width, 16 * (tile_height + label)), "#171a1f")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    for row, screen in enumerate(SCREENS):
        for index in range(8):
            _, _, preview = previews[row * 8 + index]
            x, y = index * tile_width, row * (tile_height + label)
            checker = Image.new("RGB", preview.size, "#262b31")
            if preview.mode == "RGBA":
                checker.paste(preview, (0, 0), preview)
            else:
                checker.paste(preview, (0, 0))
            canvas.paste(checker, (x, y))
            draw.text((x + 4, y + tile_height + 3), f"{screen.key} / {index:02d}", fill="#eef0e8", font=font)
    LAYER_CONTACT_SHEET.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(LAYER_CONTACT_SHEET, optimize=True)


def render_contact_sheet() -> None:
    thumbnail, columns, padding, label_height = (480, 270), 2, 20, 34
    rows = (len(SCREENS) + columns - 1) // columns
    sheet = Image.new("RGB", (padding + columns * (thumbnail[0] + padding), padding + rows * (thumbnail[1] + label_height + padding)), (20, 23, 27))
    draw, font = ImageDraw.Draw(sheet), ImageFont.load_default()
    for index, screen in enumerate(SCREENS):
        x = padding + (index % columns) * (thumbnail[0] + padding)
        y = padding + (index // columns) * (thumbnail[1] + label_height + padding)
        with Image.open(ROOT / screen.master) as image:
            sheet.paste(image.convert("RGB").resize(thumbnail), (x, y))
        label = f"{screen.title} - {screen.scope}".replace("Meroë", "Meroe")
        draw.text((x, y + thumbnail[1] + 8), label, fill=(235, 235, 235), font=font)
    CONTACT_SHEET.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(CONTACT_SHEET)


def write() -> None:
    # Remove the rejected additive-script experiment before the next smoke.
    for rejected in (
        ROOT / "loading_screen" / "gfx" / "scenes" / "00_loading_screens.txt",
        ROOT / "loading_screen" / "gfx" / "images" / "antq_loading_screens.txt",
    ):
        if rejected.exists():
            rejected.unlink()
    write_layers()
    screens = {screen.key: screen for screen in SCREENS}
    for scene_name, screen_key in SCENE_ASSIGNMENTS.items():
        screen = screens[screen_key]
        for index, target in enumerate(texture_targets(scene_name)):
            source = layer_texture(screen, index)
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                target.unlink()
            os.link(source, target)
    render_contact_sheet()


def validate() -> None:
    if len(SCREENS) != 16 or len({screen.key for screen in SCREENS}) != len(SCREENS):
        raise ValueError("loading-screen collection must contain sixteen unique reviewed panoramas")
    expected_scenes = {"rossbach", "florence", "zheng_he", "martin_luther", "damascus_ambassadors", "deccan", "aztec", "iroquois_ambush", "ashanti", "white_mountain", "hansa"}
    if set(SCENE_ASSIGNMENTS) != expected_scenes:
        raise ValueError("loading-screen override no longer covers every installed selectable scene")
    screens = {screen.key: screen for screen in SCREENS}
    if not set(SCENE_ASSIGNMENTS.values()) <= set(screens):
        raise ValueError("loading-screen assignment refers to an unknown reviewed panorama")
    for screen in SCREENS:
        source, master, texture = ROOT / screen.source, ROOT / screen.master, ROOT / screen.texture
        for path, role in ((source, "source"), (master, "master"), (texture, "texture")):
            if not path.is_file():
                raise ValueError(f"{screen.title} loading-screen {role} is missing: {path}")
        with Image.open(master) as image:
            if image.format != "PNG" or image.size != DIMENSIONS:
                raise ValueError(f"{screen.title} loading-screen master must be 3840x2160 PNG: {master}")
        if identify(texture) != {"format": "DDS", "width": "3840", "height": "2160", "depth": "8", "channels": "srgb  3.0"}:
            raise ValueError(f"{screen.title} loading-screen DDS has unexpected contract: {texture}")
        layer_hashes: set[str] = set()
        for index in range(8):
            layer = layer_texture(screen, index)
            if not layer.is_file():
                raise ValueError(f"{screen.title} loading depth layer is missing: {layer}")
            details = identify(layer)
            if details["width"] != "3840" or details["height"] != "2160":
                raise ValueError(f"{screen.title} loading layer has invalid dimensions: {layer}")
            if index and "".join(details["channels"].split()) != "srgba4.0":
                raise ValueError(f"{screen.title} loading overlay lost alpha: {layer}")
            zero, opaque, mean = alpha_stats(layer)
            if index and not (10.0 < zero < 99.8 and opaque < 80.0 and 2.0 < mean < 235.0):
                raise ValueError(
                    f"{screen.title} layer {index:02d} is not a sparse depth plate: "
                    f"zero={zero:.2f}, opaque={opaque:.2f}, mean={mean:.2f}"
                )
            layer_hashes.add(digest(layer))
        if len(layer_hashes) != 8:
            raise ValueError(f"{screen.title} loading layers contain opaque duplicates")
    for scene_name, screen_key in SCENE_ASSIGNMENTS.items():
        screen = screens[screen_key]
        for index, target in enumerate(texture_targets(scene_name)):
            if not target.is_file() or digest(target) != digest(layer_texture(screen, index)):
                raise ValueError(f"{scene_name} inherited loading texture is stale: {target}")
    if not CONTACT_SHEET.is_file():
        raise ValueError("loading-screen contact sheet is missing; run tools/m11_loading_screens.py --write")
    if not LAYER_CONTACT_SHEET.is_file() or not LAYER_LEDGER.is_file():
        raise ValueError("loading depth-layer review outputs are missing")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="link reviewed assets to installed texture paths")
    parser.add_argument("--check", action="store_true", help="validate reviewed masters, DDS, and VFS overrides")
    args = parser.parse_args()
    if args.write:
        write()
    if args.check or not args.write:
        validate()
    print(
        f"m11_loading_screens: PASS ({len(SCREENS)} panoramas x 8 true depth layers; "
        f"{len(SCENE_ASSIGNMENTS)} selectable scenes VFS-overridden)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
