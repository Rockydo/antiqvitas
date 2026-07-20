#!/usr/bin/env python3
"""Validate the reviewed M11 age-illustration replacement set."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from dds import identify


ROOT = Path(__file__).resolve().parents[1]
DIMENSIONS = (1080, 440)


@dataclass(frozen=True)
class AgeArt:
    key: str
    title: str
    source: str
    master: str
    texture: str


AGE_ART = (
    AgeArt(
        "age_1_traditions", "Principate",
        "assets_queue/generated_sources/antq_age_principate_source.png",
        "assets_queue/generated/antq_age_principate_1080x440.png",
        "main_menu/gfx/interface/illustrations/advances/age_1_traditions.dds",
    ),
    AgeArt(
        "age_2_renaissance", "High Empires",
        "assets_queue/generated_sources/antq_age_high_empires_source_v2.png",
        "assets_queue/generated/antq_age_high_empires_1080x440.png",
        "main_menu/gfx/interface/illustrations/advances/age_2_renaissance.dds",
    ),
    AgeArt(
        "age_3_discovery", "Crisis",
        "assets_queue/generated_sources/antq_age_crisis_source.png",
        "assets_queue/generated/antq_age_crisis_1080x440.png",
        "main_menu/gfx/interface/illustrations/advances/age_3_discovery.dds",
    ),
    AgeArt(
        "age_4_reformation", "Dominate",
        "assets_queue/generated_sources/antq_age_dominate_source.png",
        "assets_queue/generated/antq_age_dominate_1080x440.png",
        "main_menu/gfx/interface/illustrations/advances/age_4_reformation.dds",
    ),
    AgeArt(
        "age_5_absolutism", "Migrations",
        "assets_queue/generated_sources/antq_age_migrations_source.png",
        "assets_queue/generated/antq_age_migrations_1080x440.png",
        "main_menu/gfx/interface/illustrations/advances/age_5_absolutism.dds",
    ),
)


def png_size(path: Path) -> tuple[int, int]:
    with Image.open(path) as image:
        if image.format != "PNG":
            raise ValueError(f"age-art master is not PNG: {path}")
        return image.size


def validate() -> None:
    if len({asset.key for asset in AGE_ART}) != len(AGE_ART):
        raise ValueError("duplicate M11 age-art key")
    expected = {f"age_{index}_{name}" for index, name in enumerate(
        ("traditions", "renaissance", "discovery", "reformation", "absolutism"), 1
    )}
    if {asset.key for asset in AGE_ART} != expected:
        raise ValueError("M11 age-art mapping no longer covers the five playable age keys")
    for asset in AGE_ART:
        source = ROOT / asset.source
        master = ROOT / asset.master
        texture = ROOT / asset.texture
        for path, role in ((source, "source"), (master, "master"), (texture, "texture")):
            if not path.is_file():
                raise ValueError(f"M11 {asset.title} age-art {role} is missing: {path}")
        if png_size(master) != DIMENSIONS:
            raise ValueError(f"M11 {asset.title} age-art master has wrong dimensions: {master}")
        details = identify(texture)
        if details != {
            "format": "DDS", "width": str(DIMENSIONS[0]), "height": str(DIMENSIONS[1]),
            "depth": "8", "channels": "srgba 4.0",
        }:
            raise ValueError(f"M11 {asset.title} age-art texture has unexpected format: {texture}: {details}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate the fixed M11 age-art set")
    parser.parse_args()
    validate()
    print(f"m11_age_art: PASS ({len(AGE_ART)} reviewed 1080x440 age illustrations)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
