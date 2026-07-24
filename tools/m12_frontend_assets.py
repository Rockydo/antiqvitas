#!/usr/bin/env python3
"""Validate ANTIQVITAS's direct, engine-proven frontend asset overrides."""

from __future__ import annotations

from pathlib import Path

from dds import identify


ROOT = Path(__file__).resolve().parents[1]
ASSETS = (
    (
        "main-menu panorama",
        "assets_queue/generated_sources/antq_frontend_background_ad1.png",
        "assets_queue/generated/antq_frontend_background_ad1_3840x2160.png",
        "loading_screen/gfx/interface/illustrations/loading_screens/frontend_bg_1.dds",
        ("3840", "2160", "srgb  3.0"),
    ),
    (
        "ANTIQVITAS title",
        "assets_queue/generated_sources/antq_frontend_logo_source.png",
        "assets_queue/generated/antq_frontend_logo_1024.png",
        "main_menu/gfx/interface/logos/eu5_logo.dds",
        ("1024", "1024", "srgba 4.0"),
    ),
)


def validate() -> None:
    for label, source, master, texture, expected in ASSETS:
        for path in (source, master, texture):
            if not (ROOT / path).is_file():
                raise ValueError(f"{label} asset missing: {path}")
        details = identify(ROOT / texture)
        if (details["width"], details["height"], details["channels"]) != expected:
            raise ValueError(f"{label} DDS contract changed: {details}")


if __name__ == "__main__":
    validate()
    print(f"m12_frontend_assets: PASS ({len(ASSETS)} direct frontend overrides)")
