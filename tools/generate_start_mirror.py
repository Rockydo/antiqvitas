#!/usr/bin/env python3
"""Generate ANTIQVITAS's exact-filename M3 start-manager mirror.

Setup managers are additive in EU5.  Replacing every installed start filename
is therefore the only locally verified way to prevent the 1337 snapshot from
surviving beneath the AD 1 database.  Content generators extend these roots in
later M3 batches; this first batch proves the empty roots are valid on build
24187685 before historical ownership is introduced.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "main_menu/setup/start"

FILES = {
    "02_core.txt": """institution_manager = {\n}\n\nreligion_manager = {\n}\n""",
    "03_markets.txt": "market_manager = {\n}\n",
    "04_dynasties.txt": "dynasty_manager = {\n}\n",
    "05_characters.txt": "character_db = {\n}\n",
    "06_pops.txt": "locations = {\n}\n",
    "07_cities_and_buildings.txt": "locations = {\n}\n",
    "08_institutions.txt": "locations = {\n}\n",
    "09_roads.txt": "road_network = {\n}\n",
    "10_countries.txt": """current_age = age_1_traditions\n\ncountries = {\n\tcountries = {\n\t}\n}\n""",
    "11_art.txt": "work_of_art_manager = {\n}\n",
    "12_diplomacy.txt": "diplomacy_manager = {\n}\n",
    "13_religion.txt": "building_manager = {\n}\n",
    "14_development.txt": "development = {\n}\n",
    "15_international_organizations.txt": "international_organization_manager = {\n}\n",
    "16_wars.txt": "war_manager = {\n}\n",
    "18_opinions.txt": "diplomacy_manager = {\n}\n",
    "19_diseases.txt": "disease_outbreak_manager = {\n}\n",
    "20_rivals.txt": "diplomacy_manager = {\n}\n",
    "21_locations.txt": "locations = {\n}\n",
    "22_situations.txt": "situation_manager = {\n}\n",
    "23_colonies.txt": "colony_manager = {\n}\n",
    "24_town_rights.txt": "townrights_manager = {\n}\n",
    "25_area_preferences.txt": "countries = {\n\tcountries = {\n\t}\n}\n",
    "26_ai_personalities.txt": "countries = {\n\tcountries = {\n\t}\n}\n",
    "27_armies.txt": "unit_manager = {\n}\n",
}


def installed_start_filenames() -> set[str]:
    config = json.loads((ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig"))
    source = Path(config["game_dir"]) / "game/main_menu/setup/start"
    return {path.name for path in source.glob("*.txt")}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    failures: list[str] = []
    if args.write:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        for name, content in FILES.items():
            path = OUTPUT_DIR / name
            path.write_text(content, encoding="utf-8", newline="\n")
            print(f"start_mirror: wrote {path.relative_to(ROOT)}")
        return 0
    actual = {path.name for path in OUTPUT_DIR.glob("*.txt")} if OUTPUT_DIR.is_dir() else set()
    expected = set(FILES)
    installed = installed_start_filenames()
    if installed != expected:
        failures.append(
            "installed start-manager inventory changed; refresh FILES before relying on the mirror"
        )
    for name in sorted(expected - actual):
        failures.append(f"missing M3 start mirror {name}")
    for name in sorted(actual - expected):
        failures.append(f"unexpected start file {name}; add it to generator inventory")
    for name, content in FILES.items():
        path = OUTPUT_DIR / name
        if path.is_file() and path.read_text(encoding="utf-8") != content:
            failures.append(f"stale generated start mirror {name}")
    if failures:
        print("start_mirror: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return 1
    print(f"start_mirror: PASS ({len(FILES)} exact manager filenames)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
