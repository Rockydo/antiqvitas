#!/usr/bin/env python3
"""Validate the complete first-manual-playtest symptom closure matrix."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs/m12/manual_symptom_regression.csv"
REPORT = ROOT / "docs/m12/manual_symptom_regression.json"
ROUTE = ROOT / "docs/m12/rapid_regression_route.csv"
SCREENS = ROOT / "docs/m12/rapid_regression_screens.csv"
RUN_CHECKS = ROOT / "tools/run_checks.py"

EXPECTED_IDS = {
    "loading_quotes", "subject_loyalty", "world_granularity", "rank_language",
    "pop_classes", "italy_population", "gallic_cultures", "galatian_presence",
    "character_scenes", "unit_registry", "unit_art", "country_agenda",
    "building_art", "institutions", "advance_tree", "disease_panel",
    "location_names", "rome_economy", "frontend", "installed_leakage",
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def build_report() -> dict[str, object]:
    failures: list[str] = []
    matrix = rows(LEDGER)
    route = rows(ROUTE)
    screens = rows(SCREENS)
    ids = [row["id"].strip() for row in matrix]
    require(set(ids) == EXPECTED_IDS, f"symptom IDs differ: {sorted(set(ids) ^ EXPECTED_IDS)}", failures)
    require(len(ids) == len(set(ids)), "duplicate symptom ID", failures)
    run_checks = RUN_CHECKS.read_text(encoding="utf-8")
    registered: set[str] = set()
    for row in matrix:
        require(row["status"].strip() == "pass", f"{row['id']}: status is not pass", failures)
        evidence = ROOT / row["evidence"].strip()
        require(evidence.is_file(), f"{row['id']}: missing evidence {evidence.relative_to(ROOT)}", failures)
        validators = [value.strip() for value in row["validators"].split(";") if value.strip()]
        require(bool(validators), f"{row['id']}: no validators", failures)
        for validator in validators:
            script = ROOT / "tools" / f"{validator}.py"
            require(script.is_file(), f"{row['id']}: missing validator {script.relative_to(ROOT)}", failures)
            require(
                f'tools/{validator}.py' in run_checks,
                f"{row['id']}: {validator} is not mandatory in make validate",
                failures,
            )
            registered.add(validator)

    expected_stages = [
        "loading", "rome_selector", "subjects", "city_and_pops",
        "buildings_and_goods", "recruitment", "institutions", "advances",
        "diseases", "save_reload", "culture_variants", "leakage",
    ]
    require(
        [row["stage"].strip() for row in route] == expected_stages,
        "rapid route order or stage set changed",
        failures,
    )
    require(
        [int(row["order"]) for row in route] == list(range(1, len(route) + 1)),
        "rapid route order is not contiguous",
        failures,
    )
    for row in route:
        evidence = ROOT / row["evidence"].strip()
        require(evidence.is_file(), f"{row['stage']}: missing route evidence {evidence.relative_to(ROOT)}", failures)
        require(bool(row["assertion"].strip()), f"{row['stage']}: missing route assertion", failures)
    require(len(screens) >= 8, f"rapid screenshot manifest has only {len(screens)} rows", failures)
    require(
        all(row["status"].strip() == "accepted" for row in screens),
        "rapid screenshot manifest contains unaccepted evidence",
        failures,
    )
    for row in screens:
        evidence = ROOT / row["evidence"].strip()
        require(evidence.is_file(), f"{row['screen']}: missing screenshot evidence {evidence.relative_to(ROOT)}", failures)

    census = json.loads((ROOT / "docs/m12/installed_content_leakage.json").read_text(encoding="utf-8"))
    require(not census["uncovered"], "installed-content census has uncovered sources", failures)
    require(not census["visible_forbidden_hits"], "installed-content census has visible forbidden text", failures)
    require(census["localization"]["loading_tip_complete"], "loading-tip union is incomplete", failures)
    require(census["localization"]["country_history_complete"], "country-history union is incomplete", failures)

    subjects = rows(ROOT / "docs/m9/subject_start_balance.csv")
    require(len(subjects) == 25, f"expected 25 start dependencies, got {len(subjects)}", failures)
    require(
        all(float(row["base_loyalty_to_overlord"]) > 0 and float(row["expected_start_loyalty_min"]) > 0 for row in subjects),
        "a start dependency permits zero loyalty",
        failures,
    )

    polities = rows(ROOT / "docs/world_1ad/polities.csv")
    regions = Counter(row["region"] for row in polities)
    require(len(polities) >= 229, f"polity roster regressed to {len(polities)}", failures)
    require(
        len({row["tag"] for row in polities}) == len(polities),
        "polity roster contains duplicate design tags",
        failures,
    )
    for region, minimum in {"Germania": 48, "Finland": 13, "Japan": 10, "West Africa": 13}.items():
        require(regions[region] >= minimum, f"{region} granularity regressed to {regions[region]}", failures)

    cities = {row["location"]: row for row in rows(ROOT / "docs/m4/population_city_targets.csv")}
    require(float(cities.get("rome", {}).get("game_location_target_thousands", 0)) == 1000, "Roma target is not one million", failures)
    require(len(cities) >= 45, f"major-city ledger regressed to {len(cities)} rows", failures)

    gallic = rows(ROOT / "docs/m4/gallic_culture_totals.csv")
    galatian = rows(ROOT / "docs/m4/galatian_culture_totals.csv")
    require(len(gallic) >= 60, f"Gallic atlas regressed to {len(gallic)} cultures", failures)
    require(len(galatian) == 3, f"Galatian atlas has {len(galatian)} communities", failures)
    dynamic = {row["location"]: row["historical_name"] for row in rows(ROOT / "docs/m4/dynamic_location_names.csv")}
    require(
        dynamic.get("ankara") == "Ancyra"
        and dynamic.get("sivrihisar") == "Pessinous"
        and dynamic.get("bozok") == "Tavium",
        "Ancyra/Pessinous/Tavium runtime anchors are incomplete",
        failures,
    )

    pop_art = rows(ROOT / "docs/m12/pop_presentation.csv")
    require(len(pop_art) == 48 and all(row["status"] == "complete" for row in pop_art), "pop presentation is incomplete", failures)
    ranks = rows(ROOT / "docs/m12/rank_presentation.csv")
    medieval_rank_words = {"County", "Count", "Duchy", "Duke"}
    require(
        len(ranks) == len(polities)
        and not any(row["display_rank"] in medieval_rank_words or row["ruler_title"] in medieval_rank_words for row in ranks),
        "rank presentation exposes medieval language",
        failures,
    )

    unit_art = rows(ROOT / "docs/m12/unit_art_ledger.csv")
    unit_count = len(rows(ROOT / "docs/m7/units.csv"))
    require(
        len(unit_art) == unit_count,
        f"unit-art ledger has {len(unit_art)} rows for {unit_count} units",
        failures,
    )
    require(
        len({row["texture"] for row in unit_art}) == unit_count,
        "unit textures are aliased",
        failures,
    )
    require(
        len({row["mask"] for row in unit_art}) == unit_count,
        "unit masks are aliased",
        failures,
    )

    institutions = rows(ROOT / "docs/m8/institutions.csv")
    advances = rows(ROOT / "docs/m8/advances.csv")
    require(len(institutions) == 9, f"ancient institution set has {len(institutions)} entries", failures)
    require(len(advances) >= 360, f"advance tree has only {len(advances)} entries", failures)
    require(all(row["description"].strip() for row in advances), "an advance lacks a description", failures)
    require(sum(bool(row["requires"].strip()) for row in advances) >= 200, "advance tree branching regressed", failures)
    require(sum(bool(row["unlocks"].strip()) for row in advances) >= 60, "advance unlock density regressed", failures)

    politics = rows(ROOT / "docs/m6/ancient_politics_content.csv")
    politics_counts = Counter(row["category"] for row in politics)
    require(
        politics_counts == {
            "parliament_type": 32,
            "cabinet_action": 178,
            "parliament_issue": 114,
            "parliament_agenda": 114,
        },
        f"ancient political-system breadth regressed: {dict(politics_counts)}",
        failures,
    )
    estate_orders = rows(ROOT / "docs/m6/estate_order_privileges.csv")
    require(
        len(estate_orders) == 234 and len({row["key"] for row in estate_orders}) == 234,
        "ancient estate-order privilege breadth regressed",
        failures,
    )
    require(
        len({row["modifiers"] for row in estate_orders}) >= 30,
        "ancient estate-order effect diversity regressed",
        failures,
    )
    political_contracts = rows(ROOT / "docs/m6/political_profile_contracts.csv")
    require(
        len(political_contracts) == 114
        and len({row["reform"] for row in political_contracts}) == 114
        and len({row["modifiers"] for row in political_contracts}) >= 110,
        "ancient appointment and political-weight contracts regressed",
        failures,
    )
    alternative_reforms = rows(ROOT / "docs/m6/alternative_reform_paths.csv")
    alternative_profiles = Counter(row["profile"] for row in alternative_reforms)
    require(
        len(alternative_reforms) == 79
        and alternative_profiles["roman"] == 5
        and alternative_profiles["late_roman"] == 3
        and alternative_profiles["han"] == 3
        and alternative_profiles["late_han"] == 6
        and alternative_profiles["iranian"] == 5
        and alternative_profiles["sasanian"] == 5
        and sum(count == 2 for count in alternative_profiles.values()) == 26
        and len(alternative_profiles) == 32,
        "ancient alternative reform paths regressed",
        failures,
    )
    law_profiles = rows(ROOT / "docs/m6/ancient_law_profiles.csv")
    law_options = rows(ROOT / "docs/m6/ancient_law_options.csv")
    law_groups = {(row["profile"], row["law"]) for row in law_options}
    require(
        len(law_profiles) == 292
        and len({row["tag"] for row in law_profiles}) == 292
        and len({row["profile"] for row in law_profiles}) == 13,
        "ancient legal-profile coverage regressed",
        failures,
    )
    require(
        len(law_groups) == 182
        and len(law_options) == 584
        and sum(
            sum(
                row["profile"] == profile and row["law"] == law
                for row in law_options
            ) == 4
            for profile, law in law_groups
        ) == 38
        and sum(
            sum(
                row["profile"] == profile and row["law"] == law
                for row in law_options
            ) == 3
            for profile, law in law_groups
        ) == 144,
        "ancient multi-option legal breadth regressed",
        failures,
    )
    councils = (
        ROOT / "in_game/common/parliament_types/00_antiquitas_s2.txt"
    ).read_text(encoding="utf-8-sig")
    require(
        councils.count("parliament_base_support =") == 32
        and councils.count("_agenda_impact =") == 96,
        "ancient council participation weights regressed",
        failures,
    )

    disease = json.loads((ROOT / "docs/m12/disease_dependency_manifest.json").read_text(encoding="utf-8"))
    require(len(disease["installed_diseases"]) == 7, "disease definition union changed", failures)
    require(disease["asset_count"] >= 20, "disease UI dependency mirror is incomplete", failures)

    court_dir = ROOT / "main_menu/gfx/interface/illustrations/government/throne_rooms"
    require(len(list(court_dir.glob("antq_throne_room_*.dds"))) == 12, "court background DDS set is incomplete", failures)

    report: dict[str, object] = {
        "status": "pass" if not failures else "fail",
        "symptoms": len(matrix),
        "route_steps": len(route),
        "accepted_screens": len(screens),
        "mandatory_validators": sorted(registered),
        "assertions": {
            "installed_definitions": census["installed_definition_count"],
            "installed_references": census["installed_reference_count"],
            "installed_art_links": census["installed_art_reference_count"],
            "start_dependencies": len(subjects),
            "polities": len(polities),
            "major_city_targets": len(cities),
            "gallic_cultures": len(gallic),
            "galatian_communities": len(galatian),
            "pop_art_variants": len(pop_art),
            "rank_profiles": len(ranks),
            "unit_art": len(unit_art),
            "institutions": len(institutions),
            "advances": len(advances),
            "ancient_political_entries": len(politics),
            "profile_locked_estate_privileges": len(estate_orders),
            "political_profile_contracts": len(political_contracts),
            "alternative_reform_paths": len(alternative_reforms),
            "ancient_law_profiles": len(law_profiles),
            "ancient_law_groups": len(law_groups),
            "ancient_law_options": len(law_options),
            "diseases": len(disease["installed_diseases"]),
            "court_backgrounds": len(list(court_dir.glob("antq_throne_room_*.dds"))),
        },
        "failures": failures,
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if report["status"] != "pass":
        print("p4_manual_regression: FAIL")
        for failure in report["failures"]:
            print(f"  - {failure}")
        return 1
    if args.write:
        REPORT.write_text(rendered, encoding="utf-8", newline="\n")
    elif not REPORT.is_file() or REPORT.read_text(encoding="utf-8") != rendered:
        print(f"p4_manual_regression: FAIL\n  - stale report; run {Path(__file__).name} --write")
        return 1
    print(
        "p4_manual_regression: PASS "
        f"({report['symptoms']} manual symptoms; "
        f"{len(report['mandatory_validators'])} mandatory validators)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
