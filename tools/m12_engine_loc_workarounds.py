#!/usr/bin/env python3
"""Generate and verify narrow EU5 1.3.11 localization compatibility fixes.

The stock geography map-name path formats tooltip-backed labels twice.  A
vanilla ``|L`` style marker therefore becomes an unknown ``l`` tag on the
second pass.  The Proximity map legend also treats the building modifier
``local_proximity_source`` as a data-system function, which does not exist.

The mounted trait catalog also contains a small set of early-modern and
medieval labels that remain reachable in an ancient campaign. Exact ancient
overrides preserve the mechanics while removing those anachronisms. The
installed source is hash-pinned so a game patch cannot silently expand or
change that reviewed surface.

This generator keeps every exact contract synchronized across every language
shipped by ANTIQVITAS.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"

LANGUAGES = (
    "english",
    "braz_por",
    "french",
    "german",
    "japanese",
    "korean",
    "polish",
    "russian",
    "simp_chinese",
    "spanish",
    "turkish",
)
PROXIMITY_LEGEND = "Has a Local Proximity Source Building"
TRAIT_SOURCE_RELATIVE = Path(
    "game/main_menu/localization/english/traits_l_english.yml"
)
TRAIT_SOURCE_SHA256 = "f64e1d224809a589c20b421f427f4b78eca8eb9dbc63be5797ad30c79ed0bb3d"

# All of these are reachable through mounted ruler, commander, explorer, or
# child traits (plus ruler-policy labels shown beside them). Even normally
# event-assigned traits are owned here so no alternate grant path can expose a
# post-antique name.
TRAIT_OVERRIDES = (
    ("colonialist", "Settlement Advocate"),
    ("capitalist", "Wealth Builder"),
    ("desc_incorruptible", "This ruler is Incorruptible. Building an ordered state is a constant battle against corruption. Officials are always tempted to take bribes, while favoring friends and relatives is a common human impulse. By firmly rejecting such practices, our ruler sets an example for the entire country."),
    ("desc_expansionist", "This ruler is an Expansionist. Our ruler is personally invested in claiming and settling new lands and is dedicated to keeping frontier settlement a priority for our state."),
    ("expansionist_die_desc", "Our settlers shall mourn the loss of their great benefactor."),
    ("cannoneer", "Artillery Specialist"),
    ("desc_cannoneer", "This General is an Artillery Specialist. Close study of torsion engines, bolt-shooters, and stone-throwers makes artillery under this leader more effective."),
    ("cannoneer_die_desc", "The artillery crews mourn [CHARACTER.GetHerHis] passing as if [CHARACTER.GetSheHe] was one of their own."),
    ("buccaneer", "Sea Raider"),
    ("desc_buccaneer", "This Admiral is a Sea Raider. Commissioned raiders commanded by this leader will be more effective."),
    ("buccaneer_die_desc", "With [CHARACTER.GetHerHim] gone, our enemies will feel safer along the shipping lanes."),
    ("naval_gunner", "Naval Artillery Master"),
    ("desc_naval_gunner", "This Admiral is a Naval Artillery Master. Constant drill of artillery crews means heavy [ships|e] commanded by this leader will deal more damage."),
    ("naval_gunner_die_desc", "[CHARACTER.GetHerHis|U] constant drill of our artillery crews greatly increased our sea power during [CHARACTER.GetHerHis] lifetime."),
    ("mamluk", "Household Guard"),
    ("mamluks", "Household Guards"),
    ("desc_mamluk", "This General belongs to the highly trained $mamluks$. Originally bound to a household and trained from youth, such retainers stand out as disciplined professional warriors."),
    ("mamluk_die_desc", "[CHARACTER.GetHerHis|U] brothers in arms will remember [CHARACTER.GetHimHer]."),
    ("hussar_commander", "Steppe Cavalry Commander"),
    ("desc_hussar_commander", "This General is a true Steppe Cavalry Commander. Cavalry charges led by this character will be more effective."),
    ("hussar_commander_die_desc", "[CHARACTER.GetSheHe|U] was a fearsome leader of horsemen and victor of many battles. Without [CHARACTER.GetHerHim], our cavalry may never achieve such glory again."),
    ("desc_curious_adventurer", "This explorer is relentlessly curious, visiting every island and mapping every coastline to uncover the secrets of distant lands. Unlike other explorers, this one does not care for personal gain."),
    ("desc_treasure_hunter", "This explorer cares only for wealth and will do anything to find rare treasures in distant lands, even at the expense of their inhabitants."),
    ("scientist_on_sea", "Natural Philosopher at Sea"),
    ("desc_scientist_on_sea", "This explorer is a natural philosopher first and foremost. Charting the land matters less than studying the flora and fauna of distant shores."),
    ("scientist_on_sea_die_desc", "[CHARACTER.GetHerHis|U] name will live in the many plants and animals [CHARACTER.GetSheHe] named."),
    ("child_gallant", "Noble-Spirited"),
    ("desc_child_gallant", "Even as a child, they show courage, grace, courtesy, and attentive conduct. Such promise may earn praise and lasting stories when they come of age."),
    ("child_gallant_die_desc", "All mourn the passing of [CHARACTER.GetName]. Such remarkable promise was taken from this world too soon."),
)

GEOGRAPHY_STRUCTS = (
    ("game_province_definition_struct", "PROVINCE_DEFINITION"),
    ("game_area_struct", "AREA"),
    ("game_area_land_struct", "AREA_LAND"),
    ("game_area_highlight_struct", "AREA_HIGHLIGHT"),
    ("game_region_struct", "REGION"),
    ("game_scripted_geography_struct", "SCRIPTED_GEOGRAPHY"),
    ("game_region_land_struct", "REGION_LAND"),
    ("game_sub_continent_struct", "SUB_CONTINENT"),
    ("game_sub_continent_land_struct", "SUB_CONTINENT_LAND"),
    ("game_continent_struct", "CONTINENT"),
    ("game_continent_land_struct", "CONTINENT_LAND"),
)


def output_path(language: str) -> Path:
    return (
        ROOT
        / "main_menu"
        / "localization"
        / language
        / f"zzz_antq_engine_formatter_fix_l_{language}.yml"
    )


def validate_trait_source() -> None:
    config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
    source = Path(config["game_dir"]) / TRAIT_SOURCE_RELATIVE
    if not source.is_file():
        raise ValueError(f"missing installed trait localization source: {source}")
    actual = hashlib.sha256(source.read_bytes()).hexdigest()
    if actual != TRAIT_SOURCE_SHA256:
        raise ValueError(
            "installed trait localization source changed: "
            f"expected {TRAIT_SOURCE_SHA256}, found {actual} ({source})"
        )


def render(language: str) -> str:
    lines = [
        "\ufeff" + f"l_{language}:",
        " # EU5 1.3.11 double-formats tooltip-backed geography map labels.",
        " # Retain each tooltip target while omitting only the redundant |L style.",
    ]
    lines.extend(
        f' {key}: "#TOOLTIP:{tooltip},$DESC_KEY$ $KEY_LOC$#!"'
        for key, tooltip in GEOGRAPHY_STRUCTS
    )
    lines.extend(
        (
            " # The stock legend resolves local_proximity_source as a missing data function.",
            f' LEGEND_KEY_PROXIMITY_BUILDING: "{PROXIMITY_LEGEND}"',
            " # Mounted stock traits retain medieval and early-modern prose; mechanics stay intact.",
        )
    )
    lines.extend(f' {key}: "{value}"' for key, value in TRAIT_OVERRIDES)
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    try:
        validate_trait_source()
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"m12_engine_loc_workarounds: FAIL\n  - {exc}")
        return 1

    mismatches: list[Path] = []
    for language in LANGUAGES:
        path = output_path(language)
        expected = render(language).encode("utf-8")
        if args.check:
            if not path.is_file() or path.read_bytes() != expected:
                mismatches.append(path)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(expected)

    if mismatches:
        print("m12_engine_loc_workarounds: FAIL")
        for path in mismatches:
            print(f"  - regenerate {path.relative_to(ROOT)}")
        return 1
    action = "verified" if args.check else "generated"
    print(
        "m12_engine_loc_workarounds: PASS — "
        f"{action} {len(LANGUAGES)} synchronized localization layers"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
