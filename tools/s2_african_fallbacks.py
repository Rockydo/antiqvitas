#!/usr/bin/env python3
"""Render and audit the Africa language/religion fallback-removal tranche."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

from dds import convert, identify


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "assets_queue/african_fallbacks/sources"
MASTER_DIR = ROOT / "assets_queue/african_fallbacks/masters"
GENERATED_SOURCES = ROOT / "assets_queue/generated_sources"
GENERATED_MASTERS = ROOT / "assets_queue/generated"
BUILDING_TEXTURES = ROOT / "main_menu/gfx/interface/icons/buildings"
RELIGION_TEXTURES = ROOT / "main_menu/gfx/interface/icons/religion"
MANIFEST = ROOT / "docs/m12/african_fallbacks_manifest.json"
CULTURES = ROOT / "docs/m4/cultures.csv"
RELIGIONS = ROOT / "docs/m4/religions.csv"
PROFILES = ROOT / "docs/m4/tag_profiles.csv"
FAMILIES = ROOT / "docs/m5/regional_building_families.csv"
SEEDS = ROOT / "docs/m5/regional_building_seeds.csv"

BADGE_BUILDING_SHEET = "southern_hunter_herder_badge_buildings_01.png"
DOCTRINE_SHEET = "southern_hunter_herder_doctrines_01.png"
RELIGION = "antq_southern_african_hunter_herder_traditions"
RELIGION_SLUG = RELIGION.removeprefix("antq_")
RELIGION_SOURCE = (
    GENERATED_SOURCES / f"antq_religion_{RELIGION_SLUG}_source.png"
)
RELIGION_MASTER = (
    GENERATED_MASTERS / f"antq_religion_{RELIGION_SLUG}_128.png"
)

BUILDINGS = (
    ("antq_reg_southern_rock_shelter_custody", "top_right"),
    ("antq_reg_seasonal_waterhole_camp", "bottom_left"),
    ("antq_reg_riverine_gathering_ground", "bottom_right"),
)
EXPECTED_CULTURE_LANGUAGES = {
    "antq_kebbi_river": "antq_western_hausaland_language",
    "antq_zamfara_plateau": "antq_western_hausaland_language",
    "antq_katsina_plain": "antq_western_hausaland_language",
    "antq_gobir_tarka": "antq_western_hausaland_language",
    "antq_nsukka_lejja": "antq_nsukka_lejja_language",
    "antq_lower_oueme": "antq_lower_oueme_language",
    "antq_volta_basin": "antq_volta_interfluve_language",
    "antq_akan_forest": "antq_bosumtwi_forest_language",
    "antq_ngovo": "antq_ngovo_horizon_language",
    "antq_urewe": "antq_urewe_horizon_language",
    "antq_kwale": "antq_kwale_horizon_language",
    "antq_ruvuma_lurio": "antq_ruvuma_lurio_language",
    "antq_limpopo_hunter_herder": "antq_limpopo_hunter_herder_language",
    "antq_zambezi_forager": "antq_zambezi_forager_language",
}


def rows(path: Path, key: str) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        result = {
            (row.get(key) or "").strip(): {
                field: (value or "").strip()
                for field, value in row.items()
            }
            for row in csv.DictReader(handle)
        }
    return result


def quadrant_box(
    size: tuple[int, int], quadrant: str
) -> tuple[int, int, int, int]:
    width, height = size
    if width != height or width < 1024 or width % 2:
        raise ValueError(f"four-up atlas must be an even square >=1024, got {size}")
    half = width // 2
    return {
        "top_left": (0, 0, half, half),
        "top_right": (half, 0, width, half),
        "bottom_left": (0, half, half, height),
        "bottom_right": (half, half, width, height),
    }[quadrant]


def crop(quadrant: str, size: tuple[int, int]) -> Image.Image:
    with Image.open(SOURCE_DIR / BADGE_BUILDING_SHEET) as opened:
        piece = opened.crop(quadrant_box(opened.size, quadrant)).convert("RGBA")
    return ImageOps.fit(piece, size, method=Image.Resampling.LANCZOS)


def building_master(quadrant: str) -> Image.Image:
    raw = crop(quadrant, (128, 128))
    keyed = raw.copy()
    keyed.putalpha(Image.new("L", raw.size, 255))
    keyed.putdata([
        (
            red,
            green,
            blue,
            0
            if max(red, green, blue) < 72
            else min(255, max(0, (max(red, green, blue) - 60) * 6)),
        )
        for red, green, blue, _alpha in keyed.get_flattened_data()
    ])
    icon = Image.new("RGBA", raw.size, (16, 25, 43, 255))
    icon.alpha_composite(keyed)
    mask = Image.new("L", icon.size, 0)
    ImageDraw.Draw(mask).ellipse((3, 3, 124, 124), fill=255)
    icon.putalpha(mask.filter(ImageFilter.GaussianBlur(0.7)))
    return icon


def png_bytes(image: Image.Image) -> bytes:
    stream = io.BytesIO()
    image.save(stream, format="PNG", optimize=True)
    return stream.getvalue()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest() -> dict[str, object]:
    return {
        "scope": "West African language roots and southern African hunter-herder traditions",
        "source_boundary": (
            "Language families are technical engine constraints; names are "
            "archaeological/geographic roots, not recovered AD 1 persons. "
            "The religion and buildings are plural material-context adapters."
        ),
        "counts": {
            "reviewed_culture_languages": len(EXPECTED_CULTURE_LANGUAGES),
            "new_religions": 1,
            "new_doctrines": 4,
            "new_regional_buildings": len(BUILDINGS),
            "curated_building_seeds": 12,
            "direct_assets": 8,
        },
        "art": {
            "four_up_contract": True,
            "sources": {
                name: sha256(SOURCE_DIR / name)
                for name in (BADGE_BUILDING_SHEET, DOCTRINE_SHEET)
            },
            "style_references": (
                "Actual installed EU5 religion, religious-aspect, and building "
                "assets supplied through the three boards under "
                "assets_queue/african_fallbacks/vanilla_references."
            ),
        },
        "sources": [
            "JAH-HAUSALAND", "JAR-WA-NETWORKS", "HER-LEJJA", "OUP-BENIN",
            "JAH-GHANA", "GLOT-CHADIC", "GLOT-IGBOID", "GLOT-GBE",
            "GLOT-GUR", "GLOT-AKANIC", "JAH-BANTU-MOBILITY",
            "OUP-SOUTH-AFRICA", "CAM-SA-2024",
        ],
    }


def write() -> None:
    for directory in (
        MASTER_DIR,
        GENERATED_SOURCES,
        GENERATED_MASTERS,
        BUILDING_TEXTURES,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    source_badge = crop("top_left", (768, 768))
    RELIGION_SOURCE.write_bytes(png_bytes(source_badge))
    badge = crop("top_left", (128, 128))
    RELIGION_MASTER.write_bytes(png_bytes(badge))
    (MASTER_DIR / f"{RELIGION}_128.png").write_bytes(png_bytes(badge))

    for key, quadrant in BUILDINGS:
        master_image = building_master(quadrant)
        master = GENERATED_MASTERS / f"{key}_128.png"
        payload = png_bytes(master_image)
        master.write_bytes(payload)
        (MASTER_DIR / f"{key}_128.png").write_bytes(payload)
        convert(master, BUILDING_TEXTURES / f"{key}.dds", "dxt5", True)

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(
        json.dumps(manifest(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        "s2_african_fallbacks: wrote 1 religion badge, "
        "3 building icons, and 1 manifest"
    )


def validate() -> list[str]:
    failures: list[str] = []
    for name in (BADGE_BUILDING_SHEET, DOCTRINE_SHEET):
        source = SOURCE_DIR / name
        if not source.is_file():
            failures.append(f"missing four-up source {source.relative_to(ROOT)}")
            continue
        with Image.open(source) as opened:
            if opened.size != (1254, 1254):
                failures.append(f"{name} must be 1254x1254, got {opened.size}")

    cultures = rows(CULTURES, "key")
    for key, expected in EXPECTED_CULTURE_LANGUAGES.items():
        found = cultures.get(key, {}).get("language", "")
        if found != expected:
            failures.append(f"{key} language must be {expected}, found {found}")
        note = cultures.get(key, {}).get("note", "").lower()
        if "mande" in found or "mande" in note:
            failures.append(f"{key} retains the temporary Mande fallback")

    religions = rows(RELIGIONS, "key")
    religion = religions.get(RELIGION, {})
    if (
        religion.get("group") != "antq_african_folk_group"
        or religion.get("language") != "khoe_language"
        or religion.get("confidence") != "contested"
        or "plural" not in religion.get("note", "").lower()
    ):
        failures.append("southern hunter-herder religion lost its plural boundary")

    profiles = rows(PROFILES, "tag")
    for tag in ("LMP", "ZHF"):
        if profiles.get(tag, {}).get("religion") != RELIGION:
            failures.append(f"{tag} does not use {RELIGION}")
        if "uniform" not in profiles.get(tag, {}).get("note", "").lower():
            failures.append(f"{tag} lacks the non-uniformity boundary")

    families = rows(FAMILIES, "key")
    for key, _quadrant in BUILDINGS:
        if key not in families:
            failures.append(f"missing regional building family {key}")
    with SEEDS.open(encoding="utf-8-sig", newline="") as handle:
        seed_rows = [
            row
            for row in csv.DictReader(handle)
            if (row.get("key") or "").startswith("reg_southern_hh_")
        ]
    if len(seed_rows) != 12:
        failures.append(
            f"southern hunter-herder seed contract is {len(seed_rows)}, expected 12"
        )
    if {row["family"] for row in seed_rows} != {key for key, _ in BUILDINGS}:
        failures.append("southern hunter-herder seeds do not cover all 3 families")

    expected_pngs = {
        RELIGION_SOURCE: png_bytes(crop("top_left", (768, 768))),
        RELIGION_MASTER: png_bytes(crop("top_left", (128, 128))),
        MASTER_DIR / f"{RELIGION}_128.png": png_bytes(
            crop("top_left", (128, 128))
        ),
    }
    for key, quadrant in BUILDINGS:
        payload = png_bytes(building_master(quadrant))
        expected_pngs[GENERATED_MASTERS / f"{key}_128.png"] = payload
        expected_pngs[MASTER_DIR / f"{key}_128.png"] = payload
    for path, expected in expected_pngs.items():
        if not path.is_file() or path.read_bytes() != expected:
            failures.append(f"missing or stale direct master {path.relative_to(ROOT)}")

    for key, _quadrant in BUILDINGS:
        texture = BUILDING_TEXTURES / f"{key}.dds"
        if not texture.is_file():
            failures.append(f"missing direct building texture {texture.relative_to(ROOT)}")
            continue
        details = identify(texture)
        if (
            details["format"] != "DDS"
            or details["width"] != "128"
            or details["height"] != "128"
        ):
            failures.append(f"invalid direct building DDS contract for {key}")

    if (
        not MANIFEST.is_file()
        or json.loads(MANIFEST.read_text(encoding="utf-8")) != manifest()
    ):
        failures.append("missing or stale African fallback manifest")
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
        failures = validate()
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        failures = [str(exc)]
    if failures:
        print("s2_african_fallbacks: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return 1
    print(
        "s2_african_fallbacks: PASS "
        "(14 language profiles; 1 plural religion; "
        "4 doctrines; 3 buildings; 12 seeds; 8 direct assets)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
