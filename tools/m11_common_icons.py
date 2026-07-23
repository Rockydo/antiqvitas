#!/usr/bin/env python3
"""Build and validate M11's religion and institution icon contracts.

Religion icons migrate from exact-key, reviewed vanilla aliases to direct
ANTIQVITAS-owned assets through a checked ledger. The nine M8 institution keys
already use ANTIQVITAS-owned generated masters. Both sets are checked against
the asset resolver's direct key-to-filename contract.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
RELIGIONS = ROOT / "in_game/common/religions/antq_m4_religions.txt"
INSTITUTIONS = ROOT / "in_game/common/institution/00_antiquitas_m8_institutions.txt"
RELIGION_TEXTURES = ROOT / "main_menu/gfx/interface/icons/religion"
INSTITUTION_TEXTURES = ROOT / "main_menu/gfx/interface/icons/institutions"
DDS = ROOT / "tools/dds.py"
DIRECT_RELIGION_LEDGER = ROOT / "docs/m11/direct_religion_icons.csv"
DIMENSIONS = (128, 128)


@dataclass(frozen=True)
class ReligionIcon:
    key: str
    vanilla_source: str


@dataclass(frozen=True)
class DirectReligionIcon:
    key: str
    source: str
    master: str


@dataclass(frozen=True)
class InstitutionIcon:
    key: str
    source: str
    master: str


# The source names are engine-native broad motifs, not assertions that the
# source religion is identical to ANTIQVITAS's sourced historical category.
RELIGION_ICONS = (
    ReligionIcon("antq_religio_romana", "hellenism_religion"),
    ReligionIcon("antq_hellenic", "hellenism_religion"),
    ReligionIcon("antq_early_christianity", "catholic"),
    ReligionIcon("antq_judaism", "judaism"),
    ReligionIcon("antq_arsacid_zoroastrianism", "zoroastrian"),
    ReligionIcon("antq_manichaeism", "manichaeism"),
    ReligionIcon("antq_theravada", "theravada"),
    ReligionIcon("antq_mahayana", "mahayana"),
    ReligionIcon("antq_brahmanism", "hindu"),
    ReligionIcon("antq_jainism", "jain"),
    ReligionIcon("antq_chinese_state_cult", "sanjiao"),
    ReligionIcon("antq_daoism", "sanjiao"),
    ReligionIcon("antq_kami", "shinto"),
    ReligionIcon("antq_korean_muism", "shamanism"),
    ReligionIcon("antq_tengri", "tengri"),
    ReligionIcon("antq_bon", "bon"),
    ReligionIcon("antq_kemetic", "hellenism_religion"),
    ReligionIcon("antq_kushite_amun", "hellenism_religion"),
    ReligionIcon("antq_aksumite_paganism", "hellenism_religion"),
    ReligionIcon("antq_arabian_polytheism", "hellenism_religion"),
    ReligionIcon("antq_south_arabian_religion", "hellenism_religion"),
    ReligionIcon("antq_punic", "hellenism_religion"),
    ReligionIcon("antq_celtic_religion", "norse"),
    ReligionIcon("antq_germanic_religion", "norse"),
    ReligionIcon("antq_baltic_slavic", "romuva"),
    ReligionIcon("antq_finnic", "muinaisusko"),
    ReligionIcon("antq_berber_religion", "guanche_religion"),
    ReligionIcon("antq_nile_cushitic", "ajok_religion"),
    ReligionIcon("antq_west_african", "songhai_religion"),
    ReligionIcon("antq_bantu_religion", "bantu_religion"),
    ReligionIcon("antq_mesoamerican", "mesoamerican"),
    ReligionIcon("antq_andean", "inti"),
    ReligionIcon("antq_north_american", "great_plains_shamanism"),
    ReligionIcon("antq_siberian", "shamanism"),
    ReligionIcon("antq_austronesian_religion", "anitism_religion"),
    ReligionIcon("antq_australian_dreaming", "dreamtime_religion"),
    ReligionIcon("antq_caribbean", "tain_feyentun_religion"),
)


INSTITUTION_ICONS = (
    InstitutionIcon(
        "antq_hellenism",
        "assets_queue/generated_sources/antq_institution_hellenism_source.png",
        "assets_queue/generated/antq_institution_hellenism_128.png",
    ),
    InstitutionIcon(
        "antq_roman_law_engineering",
        "assets_queue/generated_sources/antq_institution_roman_law_engineering_source.png",
        "assets_queue/generated/antq_institution_roman_law_engineering_128.png",
    ),
    InstitutionIcon(
        "antq_han_bureaucratic_statecraft",
        "assets_queue/generated_sources/antq_institution_han_bureaucratic_statecraft_source.png",
        "assets_queue/generated/antq_institution_han_bureaucratic_statecraft_128.png",
    ),
    InstitutionIcon(
        "antq_buddhist_monasticism",
        "assets_queue/generated_sources/antq_institution_buddhist_monasticism_source.png",
        "assets_queue/generated/antq_institution_buddhist_monasticism_128.png",
    ),
    InstitutionIcon(
        "antq_cataphract_warfare",
        "assets_queue/generated_sources/antq_institution_cataphract_warfare_source.png",
        "assets_queue/generated/antq_institution_cataphract_warfare_128.png",
    ),
    InstitutionIcon(
        "antq_papermaking",
        "assets_queue/generated_sources/antq_institution_papermaking_source.png",
        "assets_queue/generated/antq_institution_papermaking_128.png",
    ),
    InstitutionIcon(
        "antq_christian_monasticism",
        "assets_queue/generated_sources/antq_institution_christian_monasticism_source.png",
        "assets_queue/generated/antq_institution_christian_monasticism_128.png",
    ),
    InstitutionIcon(
        "antq_theological_orthodoxy",
        "assets_queue/generated_sources/antq_institution_theological_orthodoxy_source.png",
        "assets_queue/generated/antq_institution_theological_orthodoxy_128.png",
    ),
    InstitutionIcon(
        "antq_foederati_statecraft",
        "assets_queue/generated_sources/antq_institution_foederati_statecraft_source.png",
        "assets_queue/generated/antq_institution_foederati_statecraft_128.png",
    ),
)


def direct_religion_icons() -> tuple[DirectReligionIcon, ...]:
    if not DIRECT_RELIGION_LEDGER.is_file():
        return ()
    required = ("key", "subject", "source", "confidence", "status", "note")
    with DIRECT_RELIGION_LEDGER.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != required:
            raise ValueError(
                f"{DIRECT_RELIGION_LEDGER.relative_to(ROOT)} must use header "
                f"{','.join(required)}"
            )
        rows = list(reader)
    known = {icon.key for icon in RELIGION_ICONS}
    result: list[DirectReligionIcon] = []
    seen: set[str] = set()
    for number, row in enumerate(rows, start=2):
        if (row.get("status") or "").strip() != "complete":
            continue
        key = (row.get("key") or "").strip()
        if not re.fullmatch(r"antq_[a-z0-9_]+", key) or key in seen:
            raise ValueError(
                f"{DIRECT_RELIGION_LEDGER.relative_to(ROOT)}:{number}: "
                f"invalid or duplicate completed key {key!r}"
            )
        if key not in known:
            raise ValueError(
                f"{DIRECT_RELIGION_LEDGER.relative_to(ROOT)}:{number}: "
                f"completed art has unknown religion {key}"
            )
        if (row.get("confidence") or "").strip() != "secure":
            raise ValueError(
                f"{DIRECT_RELIGION_LEDGER.relative_to(ROOT)}:{number}: "
                "completed art must use secure confidence"
            )
        if not (row.get("subject") or "").strip() or not (row.get("source") or "").strip():
            raise ValueError(
                f"{DIRECT_RELIGION_LEDGER.relative_to(ROOT)}:{number}: "
                "completed art needs subject and source"
            )
        slug = key.removeprefix("antq_")
        result.append(DirectReligionIcon(
            key,
            f"assets_queue/generated_sources/antq_religion_{slug}_source.png",
            f"assets_queue/generated/antq_religion_{slug}_128.png",
        ))
        seen.add(key)
    if len({icon.source for icon in result}) != len(result):
        raise ValueError("M11 direct religion icons must not share a generated source")
    if len({icon.master for icon in result}) != len(result):
        raise ValueError("M11 direct religion icons must not share a generated master")
    return tuple(result)


def game_dir() -> Path:
    return Path(json.loads(CONFIG.read_text(encoding="utf-8"))["game_dir"])


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dds_details(path: Path) -> dict[str, str]:
    command = [sys.executable, str(DDS), "identify", str(path)]
    return json.loads(subprocess.run(command, check=True, text=True, capture_output=True).stdout)


def check_dds(path: Path, label: str) -> None:
    details = dds_details(path)
    expected = {
        "format": "DDS", "width": str(DIMENSIONS[0]), "height": str(DIMENSIONS[1]),
        "depth": "8", "channels": "srgba 4.0",
    }
    if details != expected:
        raise ValueError(f"{label} has unexpected DDS contract: {path}: {details}")


def definition_keys(path: Path) -> set[str]:
    return set(re.findall(r"(?m)^(antq_[a-z0-9_]+)\s*=\s*\{", path.read_text(encoding="utf-8-sig")))


def write() -> None:
    vanilla_dir = game_dir() / "game/main_menu/gfx/interface/icons/religion"
    RELIGION_TEXTURES.mkdir(parents=True, exist_ok=True)
    INSTITUTION_TEXTURES.mkdir(parents=True, exist_ok=True)
    direct_religions = {icon.key: icon for icon in direct_religion_icons()}
    for icon in RELIGION_ICONS:
        if icon.key in direct_religions:
            continue
        source = vanilla_dir / f"{icon.vanilla_source}.dds"
        target = RELIGION_TEXTURES / f"{icon.key}.dds"
        if not source.is_file():
            raise ValueError(f"missing installed M11 religion-icon source: {source}")
        shutil.copy2(source, target)
    for icon in direct_religions.values():
        master = ROOT / icon.master
        if not master.is_file():
            raise ValueError(f"missing M11 direct religion-icon master: {master}")
        subprocess.run(
            [sys.executable, str(DDS), "convert", str(master),
             str(RELIGION_TEXTURES / f"{icon.key}.dds"), "--compression", "bc7"],
            check=True,
        )
    for icon in INSTITUTION_ICONS:
        master = ROOT / icon.master
        if not master.is_file():
            raise ValueError(f"missing M11 institution-icon master: {master}")
        subprocess.run(
            [sys.executable, str(DDS), "convert", str(master),
             str(INSTITUTION_TEXTURES / f"{icon.key}.dds"), "--compression", "bc7"],
            check=True,
        )


def validate() -> None:
    religion_keys = definition_keys(RELIGIONS)
    institution_keys = definition_keys(INSTITUTIONS)
    direct_religions = {icon.key: icon for icon in direct_religion_icons()}
    mapped_religions = {icon.key for icon in RELIGION_ICONS}
    mapped_institutions = {icon.key for icon in INSTITUTION_ICONS}
    if religion_keys != mapped_religions:
        raise ValueError(
            "M4 religion keys and M11 icon map diverge: "
            f"definitions-only={sorted(religion_keys - mapped_religions)}, "
            f"icons-only={sorted(mapped_religions - religion_keys)}"
        )
    if institution_keys != mapped_institutions:
        raise ValueError(
            "M8 institution keys and M11 icon map diverge: "
            f"definitions-only={sorted(institution_keys - mapped_institutions)}, "
            f"icons-only={sorted(mapped_institutions - institution_keys)}"
        )
    if len({icon.source for icon in INSTITUTION_ICONS}) != len(INSTITUTION_ICONS):
        raise ValueError("M11 institution icons must not share a generated source")
    if len({icon.master for icon in INSTITUTION_ICONS}) != len(INSTITUTION_ICONS):
        raise ValueError("M11 institution icons must not share a generated master")
    vanilla_dir = game_dir() / "game/main_menu/gfx/interface/icons/religion"
    for icon in RELIGION_ICONS:
        direct = direct_religions.get(icon.key)
        if direct is not None:
            source = ROOT / direct.source
            master = ROOT / direct.master
            target = RELIGION_TEXTURES / f"{icon.key}.dds"
            for path, label in ((source, "source"), (master, "master"), (target, "texture")):
                if not path.is_file():
                    raise ValueError(f"missing M11 direct religion {label}: {path}")
            with Image.open(master) as image:
                if image.format != "PNG" or image.size != DIMENSIONS:
                    raise ValueError(f"M11 direct religion master has wrong PNG contract: {master}")
            check_dds(target, "M11 direct religion texture")
            continue
        source = vanilla_dir / f"{icon.vanilla_source}.dds"
        target = RELIGION_TEXTURES / f"{icon.key}.dds"
        if icon.vanilla_source == "_default":
            raise ValueError(f"M11 religion icon cannot use the default asset: {icon.key}")
        for path, label in ((source, "installed source"), (target, "mod texture")):
            if not path.is_file():
                raise ValueError(f"missing M11 religion {label}: {path}")
            check_dds(path, f"M11 religion {label}")
        if sha256(source) != sha256(target):
            raise ValueError(f"M11 religion texture is not an exact reviewed source alias: {target}")
    for icon in INSTITUTION_ICONS:
        source = ROOT / icon.source
        master = ROOT / icon.master
        target = INSTITUTION_TEXTURES / f"{icon.key}.dds"
        for path, label in ((source, "source"), (master, "master"), (target, "texture")):
            if not path.is_file():
                raise ValueError(f"missing M11 institution {label}: {path}")
        with Image.open(master) as image:
            if image.format != "PNG" or image.size != DIMENSIONS:
                raise ValueError(f"M11 institution master has wrong PNG contract: {master}")
        check_dds(target, "M11 institution texture")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="render M11 direct-key icon textures")
    parser.add_argument("--check", action="store_true", help="validate the M11 common-screen icon contract")
    args = parser.parse_args()
    if args.write:
        write()
    validate()
    print(
        f"m11_common_icons: PASS ({len(direct_religion_icons())} direct religion icons; "
        f"{len(RELIGION_ICONS) - len(direct_religion_icons())} religion aliases; "
        f"{len(INSTITUTION_ICONS)} generated institution icons)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
