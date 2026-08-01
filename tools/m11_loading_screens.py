#!/usr/bin/env python3
"""Build and validate ANTIQVITAS animated loading-screen layer stacks.

The EU5 loading-scene scripts are additive in the installed build.  We retain
their engine-owned scene and image declarations, and instead VFS-override each
of the exact eight DDS texture paths they already reference. Plate 00 is an
opaque master background. Plates 04-07 are independently authored, whole-object
accent groups derived from four-up guides made against the installed Rossbach
stack; plates 01-03 remain transparent compatibility planes. The complete
master stays in the stable base because EU5 fades overlays away at completion;
terrain, trees, architecture, and generated replacement pixels must therefore
never be required to keep the image coherent.
"""

from __future__ import annotations

import argparse
import csv
import concurrent.futures
import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from dds import convert, identify


ROOT = Path(__file__).resolve().parents[1]
CONTACT_SHEET = ROOT / "docs" / "m11" / "loading_screens_contact_sheet.png"
LAYER_CONTACT_SHEET = ROOT / "docs" / "m11" / "loading_depth_layers_contact.png"
COMPOSITE_CONTACT_SHEET = (
    ROOT / "docs" / "m11" / "loading_depth_composites_contact.png"
)
LAYER_LEDGER = ROOT / "docs" / "m11" / "loading_depth_layers.csv"
LAYER_ROOT = ROOT / "loading_screen/gfx/loading_screen_assets/antq/layers"
DEPTH_ROOT = ROOT / "assets_queue/generated/loading_depth"
CLEAN_ROOT = ROOT / "assets_queue/generated/loading_clean"
CLEAN_SOURCE_ROOT = ROOT / "assets_queue/generated_sources/loading_clean"
HYBRID_ROOT = ROOT / "assets_queue/generated/loading_hybrid_plates"
GUIDE_ROOT = ROOT / "assets_queue/generated/loading_layer_guides"
LOCAL_PATHS = ROOT / "config/local_paths.json"
DIMENSIONS = (3840, 2160)
GUIDE_PALETTE = np.asarray((
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255),
    (255, 255, 255),
), dtype=np.int32)
SEMANTIC_CLOSE_PIXELS = 11
SEMANTIC_DILATE_PIXELS = 5
FOREGROUND_CLASSES = frozenset((3, 4, 5, 6))
ACTIVE_LAYER_OFFSET = 3
MIN_COMPONENT_PIXELS = 64
MAX_COMPONENT_FRACTION = 0.01
TARGET_ACCENT_FRACTION = 0.03
MAX_ACCENT_COMPONENTS = 16


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

# Each built-in image-generation call classified four finished scenes at once
# against their matching clean plates. The installed eight-layer Rossbach
# contact sheet was the structural reference in every call. Guides determine
# semantic ownership only; the final RGB always comes from the original master.
GUIDE_ASSIGNMENTS = {
    "germanic_rhine": ("guide_germanic_pompeii_changan_arikamedu.png", 0),
    "pompeii": ("guide_germanic_pompeii_changan_arikamedu.png", 1),
    "changan": ("guide_germanic_pompeii_changan_arikamedu.png", 2),
    "arikamedu": ("guide_germanic_pompeii_changan_arikamedu.png", 3),
    "ostia": ("guide_ostia_forum_alexandria_meroe.png", 0),
    "forum": ("guide_ostia_forum_alexandria_meroe.png", 1),
    "alexandria": ("guide_ostia_forum_alexandria_meroe.png", 2),
    "meroe": ("guide_ostia_forum_alexandria_meroe.png", 3),
    "rhine": ("guide_rhine_teotihuacan_campus_jenne.png", 0),
    "teotihuacan": ("guide_rhine_teotihuacan_campus_jenne.png", 1),
    "campus_martius": ("guide_rhine_teotihuacan_campus_jenne.png", 2),
    "jenne": ("guide_rhine_teotihuacan_campus_jenne.png", 3),
    "monte_alban": ("guide_monte_palmyra_ephesus_camulodunum.png", 0),
    "palmyra": ("guide_monte_palmyra_ephesus_camulodunum.png", 1),
    "ephesus": ("guide_monte_palmyra_ephesus_camulodunum.png", 2),
    "camulodunum": ("guide_monte_palmyra_ephesus_camulodunum.png", 3),
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
    return LAYER_ROOT / f"{screen.key}_{index:02d}.dds"


def depth_path(screen: LoadingScreen) -> Path:
    return DEPTH_ROOT / Path(screen.master).name


def clean_path(screen: LoadingScreen) -> Path:
    return CLEAN_ROOT / f"{screen.key}_clean_3840x2160.png"


def clean_source_path(screen: LoadingScreen) -> Path:
    return CLEAN_SOURCE_ROOT / f"{screen.key}_clean_source.png"


def hybrid_path(screen: LoadingScreen) -> Path:
    return HYBRID_ROOT / f"{screen.key}_hybrid_3840x2160.png"


def installed_loading_root() -> Path:
    config = json.loads(LOCAL_PATHS.read_text(encoding="utf-8-sig"))
    return (
        Path(config["game_dir"])
        / "game/loading_screen/gfx"
    )


def guide_classes(screen: LoadingScreen) -> tuple[np.ndarray, np.ndarray]:
    filename, panel = GUIDE_ASSIGNMENTS[screen.key]
    with Image.open(GUIDE_ROOT / filename) as opened:
        guide = opened.convert("RGB")
        half_width = guide.width // 2
        half_height = guide.height // 2
        column, row = panel % 2, panel // 2
        bounds = (
            column * half_width,
            row * half_height,
            guide.width if column else half_width,
            guide.height if row else half_height,
        )
        panel_image = guide.crop(bounds).resize(
            DIMENSIONS, Image.Resampling.NEAREST,
        )
    # int16 overflows at 255**2 and silently assigns black/cyan pixels to the
    # wrong planes. Keep squared RGB distances in a 32-bit domain.
    rgb = np.asarray(panel_image, dtype=np.int32)
    distance = (
        (rgb[:, :, None, :] - GUIDE_PALETTE[None, None, :, :]) ** 2
    ).sum(axis=3)
    return distance.argmin(axis=2).astype(np.uint8), rgb.max(axis=2) > 48


def semantic_ownership(screen: LoadingScreen) -> tuple[np.ndarray, np.ndarray]:
    """Return four exclusive, whole-object foreground planes.

    The guide's red/green/blue fields describe architecture, terrain, and broad
    vegetation. Animating those fields duplicates the horizon and produces the
    conspicuous ghost image seen in-game. Only yellow/magenta/cyan/white seeds
    are foreground candidates. Connected components remain indivisible, then
    are depth-ordered into four balanced planes so every scene has genuine
    parallax without slicing a person, cart, vessel, or prop into fragments.
    """
    guide_class, guide_union = guide_classes(screen)
    raw_foreground = guide_union & np.isin(
        guide_class, np.asarray(sorted(FOREGROUND_CLASSES), dtype=np.uint8)
    )

    components: list[tuple[float, int, np.ndarray]] = []
    for semantic_class in sorted(FOREGROUND_CLASSES):
        count, labels, stats, centroids = cv2.connectedComponentsWithStats(
            (raw_foreground & (guide_class == semantic_class)).astype(np.uint8),
            connectivity=8,
        )
        for label in range(1, count):
            area = int(stats[label, cv2.CC_STAT_AREA])
            if area < MIN_COMPONENT_PIXELS:
                continue
            center_y = float(centroids[label, 1]) / DIMENSIONS[1]
            # Semantic color gives the primary back-to-front order; vertical
            # position gives stable ordering among separate objects.
            score = float(semantic_class - 3) + center_y
            if area <= int(guide_class.size * MAX_COMPONENT_FRACTION):
                components.append((score, area, labels == label))

    if len(components) < 4:
        raise ValueError(
            f"{screen.title} guide contains only {len(components)} coherent "
            "foreground objects; four are required"
        )
    # Retain a restrained set of visible accents. A master painted as a single
    # image cannot safely donate large cutouts: when EU5 fades an overlay, any
    # synthetic fill beneath it becomes an obvious hole. Small intact objects
    # provide the vanilla-style pop without making scene coherence depend on
    # an overlay's current transform or opacity.
    target_area = int(guide_class.size * TARGET_ACCENT_FRACTION)
    selected: list[tuple[float, int, np.ndarray]] = []
    selected_area = 0
    for component in sorted(components, key=lambda item: item[1], reverse=True):
        if len(selected) >= MAX_ACCENT_COMPONENTS:
            break
        if len(selected) < 4 or selected_area + component[1] <= target_area:
            selected.append(component)
            selected_area += component[1]
    components = sorted(selected, key=lambda item: item[0])

    # Partition the ordered whole objects into four approximately balanced
    # planes. The leave-one-per-plane guard makes all four meshes meaningful.
    seed_planes = np.full(guide_class.shape, 255, dtype=np.uint8)
    cursor = 0
    remaining_area = sum(item[1] for item in components)
    for plane in range(4):
        remaining_planes = 4 - plane
        if plane == 3:
            stop = len(components)
        else:
            target = remaining_area / remaining_planes
            accumulated = 0
            stop = cursor
            maximum_stop = len(components) - (remaining_planes - 1)
            while stop < maximum_stop and (accumulated < target or stop == cursor):
                accumulated += components[stop][1]
                stop += 1
        for _score, _area, component in components[cursor:stop]:
            seed_planes[component] = plane
        consumed = sum(item[1] for item in components[cursor:stop])
        remaining_area -= consumed
        cursor = stop

    accepted = seed_planes != 255
    union = accepted.astype(np.uint8) * 255
    union = cv2.morphologyEx(
        union,
        cv2.MORPH_CLOSE,
        np.ones((SEMANTIC_CLOSE_PIXELS, SEMANTIC_CLOSE_PIXELS), dtype=np.uint8),
    )
    union = cv2.dilate(
        union,
        np.ones((SEMANTIC_DILATE_PIXELS, SEMANTIC_DILATE_PIXELS), dtype=np.uint8),
    ) > 0

    nearest_distance = np.full(guide_class.shape, 1e9, dtype=np.float32)
    nearest_plane = np.zeros(guide_class.shape, dtype=np.uint8)
    for index in range(4):
        seed = (seed_planes == index).astype(np.uint8)
        if not np.any(seed):
            raise ValueError(f"{screen.title} foreground plane {index + 1} is empty")
        distance = cv2.distanceTransform(1 - seed, cv2.DIST_L2, 5)
        closer = distance < nearest_distance
        nearest_distance[closer] = distance[closer]
        nearest_plane[closer] = index
    return nearest_plane, union


def depth_masks(
    screen: LoadingScreen,
    panorama: Image.Image,
    clean: Image.Image,
    depth_image: Image.Image,
) -> tuple[np.ndarray, ...]:
    """Turn semantic guides into four coherent whole-object planes.

    The previous implementation intersected the guides with a pixel-difference
    field. That looked correct in a static composite but shredded objects into
    hundreds of independently displaced fragments in EU5. Vanilla layers use
    whole silhouettes, so guide ownership is now the sole alpha authority.
    """
    depth = np.asarray(depth_image.convert("L"), dtype=np.uint8)
    if not np.any(depth > 3):
        raise ValueError(f"{screen.title} depth map has no subject field")
    nearest_plane, candidate = semantic_ownership(screen)

    masks: list[np.ndarray] = []
    for index in range(7):
        active_plane = index - ACTIVE_LAYER_OFFSET
        binary = (
            candidate & (nearest_plane == active_plane)
            if active_plane >= 0
            else np.zeros(candidate.shape, dtype=bool)
        ).astype(np.uint8) * 255
        alpha = np.asarray(
            Image.fromarray(binary, "L").filter(
                ImageFilter.GaussianBlur(radius=1.25)
            ),
            dtype=np.uint8,
        ).copy()
        alpha[alpha < 6] = 0
        masks.append(alpha)
    return tuple(masks)


def render_depth_plate(image: Image.Image, alpha: np.ndarray) -> Image.Image:
    rgba = np.asarray(image.convert("RGBA")).copy()
    rgba[:, :, 3] = alpha
    rgba[:, :, :3][alpha == 0] = 0
    return Image.fromarray(rgba, "RGBA")


def render_hybrid_plate(
    screen: LoadingScreen,
    panorama: Image.Image,
    generated_clean: Image.Image,
) -> Image.Image:
    """Return the pristine master as the always-coherent engine base plate."""
    del screen, generated_clean
    return panorama.convert("RGB").copy()


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
    HYBRID_ROOT.mkdir(parents=True, exist_ok=True)
    temp_root = ROOT / ".tmp"
    temp_root.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    previews: list[tuple[str, int, Image.Image]] = []
    composites: list[tuple[str, Image.Image]] = []
    for screen in SCREENS:
        with Image.open(ROOT / screen.master) as opened:
            panorama = opened.convert("RGB")
            with Image.open(clean_path(screen)) as clean_opened:
                clean = clean_opened.convert("RGB")
                if clean.size != panorama.size:
                    raise ValueError(
                        f"{screen.title} clean plate does not match panorama: "
                        f"{clean.size} != {panorama.size}"
                    )
            with Image.open(depth_path(screen)) as depth_opened:
                if depth_opened.size != panorama.size:
                    raise ValueError(
                        f"{screen.title} depth map does not match panorama: "
                        f"{depth_opened.size} != {panorama.size}"
                    )
                masks = depth_masks(screen, panorama, clean, depth_opened)
            base = render_hybrid_plate(screen, panorama, clean)
            base.save(hybrid_path(screen), optimize=True)
            previews.append((screen.key, 0, base.resize((240, 135))))
            composite = base.convert("RGBA")
            with tempfile.TemporaryDirectory(prefix="antq-loading-", dir=temp_root) as temporary:
                work = Path(temporary)
                conversions: list[tuple[Path, Path, str]] = [
                    (hybrid_path(screen), layer_texture(screen, 0), "bc1")
                ]
                for index, alpha in enumerate(masks, start=1):
                    plate = render_depth_plate(panorama, alpha)
                    png = work / f"{screen.key}_{index:02d}.png"
                    plate.save(png, optimize=True)
                    target = layer_texture(screen, index)
                    conversions.append((png, target, "bc3"))
                    composite.alpha_composite(plate)
                    preview = plate.resize((240, 135), Image.Resampling.LANCZOS)
                    previews.append((screen.key, index, preview))
                with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                    futures = [
                        executor.submit(convert, png, target, compression, mipmaps=True)
                        for png, target, compression in conversions
                    ]
                    for future in futures:
                        future.result()
            composites.append(
                (screen.key, composite.convert("RGB").resize((480, 270)))
            )
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

    composite_canvas = Image.new(
        "RGB",
        (4 * 480, 4 * (270 + label)),
        "#171a1f",
    )
    composite_draw = ImageDraw.Draw(composite_canvas)
    for index, (key, preview) in enumerate(composites):
        x = (index % 4) * 480
        y = (index // 4) * (270 + label)
        composite_canvas.paste(preview, (x, y))
        composite_draw.text(
            (x + 4, y + 273),
            f"{key} / assembled",
            fill="#eef0e8",
            font=font,
        )
    composite_canvas.save(COMPOSITE_CONTACT_SHEET, optimize=True)


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
    if set(GUIDE_ASSIGNMENTS) != set(screens):
        raise ValueError("semantic loading guides must cover all sixteen screens")
    for filename, _panel in set(GUIDE_ASSIGNMENTS.values()):
        guide = GUIDE_ROOT / filename
        if not guide.is_file():
            raise ValueError(f"missing four-up semantic loading guide: {guide}")
        with Image.open(guide) as image:
            if image.format != "PNG" or image.width < 1600 or image.height < 900:
                raise ValueError(f"invalid four-up semantic loading guide: {guide}")
    for screen in SCREENS:
        source, master, texture = ROOT / screen.source, ROOT / screen.master, ROOT / screen.texture
        depth = depth_path(screen)
        clean = clean_path(screen)
        hybrid = hybrid_path(screen)
        clean_source = clean_source_path(screen)
        for path, role in (
            (source, "source"),
            (master, "master"),
            (depth, "depth map"),
            (texture, "finished-scene texture"),
            (clean_source, "clean-plate source"),
            (clean, "clean plate"),
            (hybrid, "hybrid plate"),
        ):
            if not path.is_file():
                raise ValueError(f"{screen.title} loading-screen {role} is missing: {path}")
        with Image.open(master) as image:
            if image.format != "PNG" or image.size != DIMENSIONS:
                raise ValueError(f"{screen.title} loading-screen master must be 3840x2160 PNG: {master}")
        with Image.open(depth) as image:
            if image.format != "PNG" or image.size != DIMENSIONS:
                raise ValueError(f"{screen.title} depth map must be 3840x2160 PNG: {depth}")
            rgb = np.asarray(image.convert("RGB"))
            if not (np.array_equal(rgb[:, :, 0], rgb[:, :, 1])
                    and np.array_equal(rgb[:, :, 1], rgb[:, :, 2])):
                raise ValueError(f"{screen.title} depth map is not grayscale: {depth}")
        with Image.open(clean) as image:
            if image.format != "PNG" or image.size != DIMENSIONS:
                raise ValueError(
                    f"{screen.title} clean plate must be 3840x2160 PNG: {clean}"
                )
        with Image.open(hybrid) as image:
            if image.format != "PNG" or image.size != DIMENSIONS:
                raise ValueError(
                    f"{screen.title} hybrid plate must be 3840x2160 PNG: {hybrid}"
                )
        if identify(texture) != {"format": "DDS", "width": "3840", "height": "2160", "depth": "8", "channels": "srgb  3.0"}:
            raise ValueError(f"{screen.title} loading-screen DDS has unexpected contract: {texture}")
        layer_hashes: set[str] = set()
        layer_images: list[np.ndarray] = []
        nonempty_layers = 0
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
            semitransparent = 100.0 - zero - opaque
            semantic_contract = (
                # Vanilla Rossbach's broad terrain plane is ~73% opaque; plane
                # area alone is not evidence of duplication.
                20.0 < zero < 99.99
                and 0.0 <= opaque < 80.0
                # Vanilla deliberately uses broad translucent atmosphere and
                # fine silhouettes; feather ratio is not an ownership test.
                and 0.01 < semitransparent < 45.0
                and 0.01 < mean < 125.0
            )
            empty_contract = (
                zero > 99.99
                and opaque < 0.01
                and semitransparent < 0.01
                and mean < 0.01
            )
            if index and semantic_contract:
                nonempty_layers += 1
            if index and not (semantic_contract or empty_contract):
                raise ValueError(
                    f"{screen.title} layer {index:02d} violates semantic alpha: "
                    f"zero={zero:.2f}, opaque={opaque:.2f}, "
                    f"semi={semitransparent:.2f}, mean={mean:.2f}"
                )
            layer_hashes.add(digest(layer))
            with Image.open(layer) as opened:
                layer_images.append(np.asarray(opened.convert("RGBA")))
        if nonempty_layers != 4 or len(layer_hashes) < 5:
            raise ValueError(
                f"{screen.title} has {nonempty_layers}, not four, independent "
                "foreground planes"
            )
        coverage = np.stack(
            [image[:, :, 3] > 128 for image in layer_images[1:]],
            axis=0,
        ).sum(axis=0)
        expected_class, expected_union = semantic_ownership(screen)
        actual_union = coverage > 0
        intersection = np.logical_and(actual_union, expected_union).sum()
        union_pixels = np.logical_or(actual_union, expected_union).sum()
        guide_iou = float(intersection / max(1, union_pixels))
        if guide_iou < 0.94:
            raise ValueError(
                f"{screen.title} animated silhouettes diverge from semantic "
                f"guide (IoU={guide_iou:.3f})"
            )
        for index, image in enumerate(layer_images[1:]):
            actual = image[:, :, 3] > 128
            active_plane = index - ACTIVE_LAYER_OFFSET
            expected = (
                expected_union & (expected_class == active_plane)
                if active_plane >= 0
                else np.zeros(expected_union.shape, dtype=bool)
            )
            class_union = np.logical_or(actual, expected).sum()
            class_iou = (
                np.logical_and(actual, expected).sum() / class_union
                if class_union else 1.0
            )
            # Small sparse classes lose proportionally more edge pixels in
            # BC3; 0.85 still rejects the former texture-difference fragments
            # while allowing the measured 0.888 round-trip minimum.
            if class_iou < 0.85:
                raise ValueError(
                    f"{screen.title} layer {index + 1:02d} is not a coherent "
                    f"semantic silhouette (IoU={class_iou:.3f})"
                )
        overlap = float((coverage > 1).mean() * 100.0)
        union = float((coverage > 0).mean() * 100.0)
        if not 0.5 < union < 6.0:
            raise ValueError(
                f"{screen.title} semantic foreground coverage is {union:.2f}%"
            )
        if overlap > 0.05:
            raise ValueError(
                f"{screen.title} loading planes overlap {overlap:.2f}% of pixels"
            )
        clean_rgb = layer_images[0][:, :, :3].astype(np.int16)
        with Image.open(master) as opened:
            master_rgb = np.asarray(opened.convert("RGB"), dtype=np.int16)
        outside = ~expected_union
        outside_difference = np.abs(clean_rgb - master_rgb).mean(axis=2)[outside]
        if float(outside_difference.mean()) > 5.0:
            raise ValueError(
                f"{screen.title} base plate diverges from the master outside "
                f"cutouts ({outside_difference.mean():.2f} mean RGB delta)"
            )
        all_difference = np.abs(clean_rgb - master_rgb).mean(axis=2)
        if float(all_difference.mean()) > 5.0:
            raise ValueError(
                f"{screen.title} base plate is not the complete master "
                f"({all_difference.mean():.2f} mean RGB delta)"
            )
    for scene_name, screen_key in SCENE_ASSIGNMENTS.items():
        screen = screens[screen_key]
        for index, target in enumerate(texture_targets(scene_name)):
            if not target.is_file() or digest(target) != digest(layer_texture(screen, index)):
                raise ValueError(f"{scene_name} inherited loading texture is stale: {target}")
    if not CONTACT_SHEET.is_file():
        raise ValueError("loading-screen contact sheet is missing; run tools/m11_loading_screens.py --write")
    if (
        not LAYER_CONTACT_SHEET.is_file()
        or not COMPOSITE_CONTACT_SHEET.is_file()
        or not LAYER_LEDGER.is_file()
    ):
        raise ValueError("loading depth-layer review outputs are missing")
    installed = installed_loading_root()
    scene_text = (
        installed / "scenes/00_loading_screens.txt"
    ).read_text(encoding="utf-8-sig")
    image_text = (
        installed / "images/00_loading_screen_rossbach.txt"
    ).read_text(encoding="utf-8-sig")
    for index in range(8):
        reference = (
            installed
            / "loading_screen_assets/00/images"
            / f"loading_screen_rossbach_{index:02d}.dds"
        )
        if not reference.is_file():
            raise ValueError(f"installed loading reference is missing: {reference}")
        layer = 8 - index
        image_marker = f"loading_screen_rossbach_layer{layer} ="
        image_start = image_text.find(image_marker)
        image_block = (
            image_text[image_start:image_start + 360]
            if image_start >= 0
            else ""
        )
        texture = f"loading_screen_rossbach_{index:02d}.dds"
        scene_binding = (
            f'list = "loading_screen_rossbach_layer{layer}"\n'
            f'\t\tpdxmesh = "layer_{layer}_mesh"'
        )
        if texture not in image_block or scene_binding not in scene_text:
            raise ValueError(
                f"installed _07-near/_00-far binding changed at {texture}"
            )


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
        f"m11_loading_screens: PASS ({len(SCREENS)} exact master plates + "
        f"four restrained accent planes; {len(SCENE_ASSIGNMENTS)} selectable "
        "scenes VFS-overridden)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
