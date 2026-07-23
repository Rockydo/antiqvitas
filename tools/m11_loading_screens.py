#!/usr/bin/env python3
"""Validate the reviewed ANTIQVITAS selectable loading-screen textures.

The EU5 loading-scene scripts are additive in the installed build.  We retain
their engine-owned scene and image declarations, and instead VFS-override each
of the exact DDS texture paths they already reference.  This is the same
asset-level mechanism successfully used by the mod's existing startup splash.
"""

from __future__ import annotations

import argparse
import hashlib
import os
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from dds import identify


ROOT = Path(__file__).resolve().parents[1]
CONTACT_SHEET = ROOT / "docs" / "m11" / "loading_screens_contact_sheet.png"
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
)

# All currently selectable scene keys. Every one gets opaque, same-scene art
# on each inherited layer, ensuring a random vanilla scene cannot appear.
SCENE_ASSIGNMENTS = {
    "rossbach": "rhine", "florence": "forum", "zheng_he": "changan",
    "martin_luther": "campus_martius", "damascus_ambassadors": "alexandria",
    "deccan": "meroe", "aztec": "teotihuacan", "iroquois_ambush": "ostia",
    "ashanti": "meroe", "white_mountain": "rhine", "hansa": "ostia",
}


def texture_targets(scene_name: str) -> tuple[Path, ...]:
    return tuple(
        ROOT / "loading_screen" / "gfx" / "loading_screen_assets" / "00" / "images"
        / f"loading_screen_{scene_name}_{index:02d}.dds"
        for index in range(8)
    )


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    screens = {screen.key: screen for screen in SCREENS}
    for scene_name, screen_key in SCENE_ASSIGNMENTS.items():
        source = ROOT / screens[screen_key].texture
        for target in texture_targets(scene_name):
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                target.unlink()
            os.link(source, target)
    render_contact_sheet()


def validate() -> None:
    if len(SCREENS) != 8 or len({screen.key for screen in SCREENS}) != len(SCREENS):
        raise ValueError("loading-screen set must contain eight unique reviewed panoramas")
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
    for scene_name, screen_key in SCENE_ASSIGNMENTS.items():
        source_digest = digest(ROOT / screens[screen_key].texture)
        for target in texture_targets(scene_name):
            if not target.is_file() or digest(target) != source_digest:
                raise ValueError(f"{scene_name} inherited loading texture is stale: {target}")
    if not CONTACT_SHEET.is_file():
        raise ValueError("loading-screen contact sheet is missing; run tools/m11_loading_screens.py --write")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="link reviewed assets to installed texture paths")
    parser.add_argument("--check", action="store_true", help="validate reviewed masters, DDS, and VFS overrides")
    args = parser.parse_args()
    if args.write:
        write()
    if args.check or not args.write:
        validate()
    print(f"m11_loading_screens: PASS ({len(SCREENS)} reviewed panoramas; {len(SCENE_ASSIGNMENTS)} selectable scenes VFS-overridden)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
