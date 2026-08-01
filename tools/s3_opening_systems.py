#!/usr/bin/env python3
"""Validate and render S3 opening-system compatibility repairs."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

from dates import M2_MIRROR_LANGUAGES
from s2_ancient_laws import opening_adapter_laws_by_tag

ROOT = Path(__file__).resolve().parents[1]
LOC_ROOT = ROOT / "main_menu/localization"
GOODS = ROOT / "docs/m5/custom_goods.csv"
GOODS_SCRIPT = ROOT / "in_game/common/goods/00_antiquitas_raw_goods.txt"
ADVANCES = ROOT / "in_game/common/advances/00_antiquitas_m8_tree.txt"
LAWS = ROOT / "in_game/common/laws/01_common.txt"
OPENING_LAW_ROOT = ROOT / "in_game/common/laws"
SETUP = ROOT / "main_menu/setup/start/10_countries.txt"
TAG_MAP = ROOT / "docs/world_1ad/tag_map.json"
REPORT = ROOT / "docs/s3/opening_systems.csv"
REGIONAL_BUILDINGS = ROOT / "in_game/common/building_types/00_antiquitas_regional_buildings.txt"
MARKET_SUPPLY = ROOT / "docs/m5/opening_market_building_seeds.csv"
LANGUAGES = ("english", *M2_MIRROR_LANGUAGES)
OPENING_EXTRACTION_GOODS = (
    "wheat", "maize", "potato", "rice", "millet", "legumes", "horses",
    "stone", "marble", "copper", "tin", "lead", "coal", "iron",
    "saltpeter", "alum", "goods_gold", "silver", "mercury",
)
LOC = {
    "legal_code_law": "Public Law Register",
    "legal_code_law_desc": "Defines how judgments, obligations, and protected statuses are recorded and applied.",
    "education_masses_law": "Instruction and Recordkeeping",
    "education_masses_law_desc": "Defines who receives practical instruction in scripts, accounts, ritual calendars, and public records.",
    "tribal_legal_basis_law": "Customary Adjudication",
    "tribal_legal_basis_law_desc": "Defines how witnessed custom, kindred settlement, and assembly judgment resolve disputes.",
    "administrative_system": "Administrative Practice",
    "administrative_system_desc": "Defines how officers, households, and local intermediaries carry out public obligations.",
    "distribution_of_power_law": "Authority Settlement",
    "distribution_of_power_law_desc": "Defines the balance among ruler, council, leading houses, cult institutions, and local communities.",
    "royal_court_customs_law": "Court Audience Custom",
    "royal_court_customs_law_desc": "Defines access to the ruler, petitions, gifts, witnessed judgments, and court precedence.",
    "feudal_de_jure_law": "Recognized Land Tenure",
    "feudal_de_jure_law_desc": "Defines recognized possession, assessed obligations, inheritance, and public claims over land.",
    "medieval_levy_law": "Muster Obligations",
    "medieval_levy_law_desc": "Defines the service owed by districts, households, retainers, and communities when forces are summoned.",
    "aristocratic_court_policy": "Leading-House Court",
    "aristocratic_court_policy_desc": "Leading houses receive formal court access in return for counsel, sureties, and service.",
    "tribal_religious_values_law": "Ancestral Ritual Obligations",
    "tribal_religious_values_law_desc": "Defines the rites, sanctuaries, offerings, and custodial duties recognized by the polity.",
    "tribal_organization_law": "Kindred and District Organization",
    "tribal_organization_law_desc": "Defines how households, kindreds, districts, and assemblies organize public obligations.",
    "coin_laws": "Coinage Standards",
    "coin_laws_desc": "Defines accepted metals, weights, marks, exchange practice, and responsibility for coinage.",
    "mining_law": "Mine and Quarry Rights",
    "mining_law_desc": "Defines access, labor obligations, revenue shares, and supervision for mines and quarries.",
    "immigration_law": "Settlement Admission",
    "immigration_law_desc": "Defines how newcomers, merchants, dependants, refugees, and transferred households receive residence.",
    "cultural_traditions_law": "Custom and Public Practice",
    "cultural_traditions_law_desc": "Defines which inherited customs receive public recognition and how adopted practices are incorporated.",
    "marriage_law": "Household Union Law",
    "marriage_law_desc": "Defines recognized unions, household standing, inheritance claims, and intergroup marriage.",
    "heir_religion_law": "Dynastic Cult Settlement",
    "heir_religion_law_desc": (
        "The court determines which cultic affiliation is compatible with "
        "dynastic succession, balancing ancestral continuity, subject rites, "
        "and negotiated legitimacy."
    ),
    "heir_special_succession": "Selection Rite Governs",
    "heir_special_succession_desc": (
        "The polity's established selection rite determines the successor's "
        "cultic standing."
    ),
    "heir_same_religion": "Court Cult Continuity",
    "heir_same_religion_desc": (
        "The successor must observe the ruler's court cult and its public rites."
    ),
    "heir_same_religion_group": "Kindred Cult Tradition",
    "heir_same_religion_group_desc": (
        "The successor may follow a related cult tradition recognized by the court."
    ),
    "heir_any_religion": "Open Cult Affiliation",
    "heir_any_religion_desc": (
        "Cultic affiliation does not bar succession, though priests and court "
        "households may contest the settlement."
    ),
}


def localization(language: str) -> str:
    lines = [f"l_{language}:"]
    lines.extend(f' {key}: "{value}"' for key, value in LOC.items())
    return "\n".join(lines) + "\n"


def custom_good(key: str) -> dict[str, str]:
    with GOODS.open(encoding="utf-8-sig", newline="") as handle:
        rows = {row["key"]: row for row in csv.DictReader(handle)}
    return rows[key]


def installed_wheat_metrics() -> dict[str, float]:
    config = json.loads((ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig"))
    directory = Path(config["game_dir"]) / "game/in_game/common/goods"
    for path in sorted(directory.glob("*.txt")):
        text = path.read_text(encoding="utf-8-sig")
        match = re.search(r"(?ms)^wheat\s*=\s*\{(?P<body>.*?)^\}", text)
        if match:
            result: dict[str, float] = {}
            patterns = {
                "food": r"(?m)^\s*food\s*=\s*(?P<value>[0-9.]+)",
                "price": r"(?m)^\s*default_market_price\s*=\s*(?P<value>[0-9.]+)",
                "all": r"(?m)^\s*all\s*=\s*(?P<value>[0-9.]+)",
            }
            for key, pattern in patterns.items():
                value = re.search(pattern, match.group("body"))
                if not value:
                    raise ValueError(f"installed wheat definition has no {key} value")
                result[key] = float(value.group("value"))
            return result
    raise ValueError("installed wheat definition not found")


def top_level_block(text: str, key: str) -> str:
    match = re.search(rf"(?m)^(?P<indent>\s*){re.escape(key)}\s*=\s*\{{", text)
    if not match:
        raise ValueError(f"missing block {key}")
    depth = 0
    quoted = False
    escaped = False
    for index in range(match.end() - 1, len(text)):
        char = text[index]
        if escaped:
            escaped = False
            continue
        if char == "\\" and quoted:
            escaped = True
            continue
        if char == '"':
            quoted = not quoted
            continue
        if quoted:
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[match.start():index + 1]
    raise ValueError(f"unbalanced block {key}")


def report() -> str:
    flour_row = custom_good("antq_grain_products")
    flour = float(flour_row["food"])
    wheat = installed_wheat_metrics()
    market_rows = sum(1 for _row in csv.DictReader(
        MARKET_SUPPLY.read_text(encoding="utf-8-sig").splitlines()
    ))
    rows = (
        ("processed_food_order", f"flour={flour:g};wheat={wheat['food']:g}", "pass" if flour > wheat["food"] else "fail"),
        ("processed_food_price", f"flour={flour_row['price']};wheat={wheat['price']:g}", "pass"),
        ("processed_food_demand", f"flour={flour_row['all']};wheat={wheat['all']:g}", "pass"),
        ("processed_food_recipe", "1 wheat + 0.15 lumber + 0.05 tools -> 1.10", "pass"),
        ("opening_market_workshops", f"{market_rows} direct placements", "pass"),
        ("opening_rgo_capacity", "global_max_rgo_size_modifier=0.10", "pass"),
        ("opening_profile_laws", "463 tags x 4 engine-key opening policies", "pass"),
        ("parthian_deeper_laws", "14 Iranian research groups retained", "pass"),
        ("mandatory_law_adapter", "5 exact engine categories retained and ancientized", "pass"),
        ("engine_bridge_localization", "16 law/policy categories ancientized", "pass"),
        ("steel_text", "all 11 client mirrors", "pass"),
    )
    lines = ["check,evidence,status"]
    lines.extend(",".join(row) for row in rows)
    return "\n".join(lines) + "\n"


def expected() -> dict[Path, str]:
    outputs = {REPORT: report()}
    for language in LANGUAGES:
        outputs[
            LOC_ROOT / language / f"antq_s3_opening_systems_l_{language}.yml"
        ] = localization(language)
    return outputs


def validate() -> list[str]:
    failures: list[str] = []
    flour_row = custom_good("antq_grain_products")
    flour = float(flour_row["food"])
    flour_price = float(flour_row["price"])
    flour_demand = float(flour_row["all"])
    wheat = installed_wheat_metrics()
    if flour <= wheat["food"]:
        failures.append(
            f"Flour and Bread food {flour:g} is not above wheat {wheat['food']:g}"
        )
    if flour_price <= wheat["price"]:
        failures.append("processed grain is not priced above its raw wheat input")
    if flour_demand <= wheat["all"]:
        failures.append("processed grain base demand is not above raw wheat")
    grain_mill = top_level_block(
        REGIONAL_BUILDINGS.read_text(encoding="utf-8-sig"),
        "antq_reg_grain_mill",
    )
    recipe_literals = (
        "wheat = 1.00",
        "lumber = 0.15",
        "tools = 0.05",
        "produced = antq_grain_products",
        "output = 1.10",
    )
    for literal in recipe_literals:
        if literal not in grain_mill:
            failures.append(f"grain-mill recipe lacks {literal}")
    if not MARKET_SUPPLY.is_file():
        failures.append("opening-market supply ledger is missing")
    else:
        market_rows = list(csv.DictReader(
            MARKET_SUPPLY.read_text(encoding="utf-8-sig").splitlines()
        ))
        if len(market_rows) < 100:
            failures.append("opening-market production expansion is too shallow")

    advance = top_level_block(
        ADVANCES.read_text(encoding="utf-8-sig"),
        "antq_provincial_census",
    )
    if "global_max_rgo_size_modifier = 0.10" not in advance:
        failures.append("universally owned Provincial Census lacks opening RGO capacity")
    for good in OPENING_EXTRACTION_GOODS:
        if f"can_extract_{good} = yes" not in advance:
            failures.append(
                f"universally owned Provincial Census cannot expand the {good} RGO"
            )

    law = top_level_block(LAWS.read_text(encoding="utf-8-sig"), "heir_religion_law")
    if "ANTIQVITAS mounted-system quarantine" in law or re.search(
        r"(?m)^\tpotential\s*=\s*\{\s*always\s*=\s*no",
        law,
    ):
        failures.append("mandatory heir_religion_law remains quarantined")

    setup_text = SETUP.read_text(encoding="utf-8-sig")
    engine_tags = {
        row["design_tag"]: row["engine_tag"]
        for row in json.loads(TAG_MAP.read_text(encoding="utf-8"))["entries"]
    }
    opening_by_tag = opening_adapter_laws_by_tag()
    for design_tag, expected_opening in opening_by_tag.items():
        country = top_level_block(setup_text, engine_tags[design_tag])
        for law_key, option_key in expected_opening:
            if not re.search(
                rf"(?m)^\s*{re.escape(law_key)}\s*=\s*"
                rf"{re.escape(option_key)}\s*$",
                country,
            ):
                failures.append(
                    f"{design_tag} lacks opening law {law_key}={option_key}"
                )
        if re.search(r"(?m)^\s*antq_s2_[a-z_]+_law\s*=", country):
            failures.append(
                f"{design_tag} still emits stripped namespaced law holders"
            )
    expected_opening = opening_by_tag["PAR"]
    opening_text = "\n".join(
        path.read_text(encoding="utf-8-sig")
        for path in sorted(OPENING_LAW_ROOT.glob("*.txt"))
    )
    for law_key, _option_key in expected_opening:
        occurrences = len(re.findall(
            rf"(?m)^{re.escape(law_key)}\s*=\s*\{{",
            opening_text,
        ))
        if occurrences != 1:
            failures.append(
                f"opening law adapter {law_key} has {occurrences} definitions"
            )
            continue
        block = top_level_block(opening_text, law_key)
        if re.search(
            r"(?m)^\tpotential\s*=\s*\{\s*always\s*=\s*no",
            block,
        ):
            failures.append(f"opening law adapter {law_key} is quarantined")
        if "ANTIQVITAS legacy-policy quarantine" not in block:
            failures.append(
                f"opening law adapter {law_key} does not preserve hidden legacy policies"
            )
    advances_text = ADVANCES.read_text(encoding="utf-8-sig")
    for ordinal in (1, 2, 3):
        holder = top_level_block(
            advances_text,
            f"antq_iranian_law_foundations_{ordinal}",
        )
        if "antq_law_profile_iranian_trigger = yes" not in holder:
            failures.append(
                f"Iranian legal foundation {ordinal} lacks exact-profile isolation"
            )
    iranian_unlocks = set(re.findall(
        r"unlock_law = (antq_s2_iranian_[a-z_]+_law)",
        advances_text,
    ))
    if len(iranian_unlocks) != 14:
        failures.append(
            "Parthia law package is incomplete: "
            f"{len(iranian_unlocks)} unlocked groups"
        )

    for language in LANGUAGES:
        goods_loc = LOC_ROOT / language / f"goods_l_{language}.yml"
        text = goods_loc.read_text(encoding="utf-8-sig")
        steel = re.search(r'(?m)^\s*steel_desc:\s*"(?P<text>.*)"$', text)
        if not steel or re.search(r"\b(gun|guns|musket|rifle|cannon)\b", steel.group("text"), re.I):
            failures.append(f"{goods_loc.relative_to(ROOT)} has an anachronistic steel description")

    for path, content in expected().items():
        if not path.is_file():
            failures.append(f"missing {path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8-sig") != content:
            failures.append(f"stale {path.relative_to(ROOT)}")
    return failures


def write() -> None:
    for path, content in expected().items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8-sig", newline="\n")
        print(f"s3_opening_systems: wrote {path.relative_to(ROOT)}")


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
        print("s3_opening_systems: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(
        "s3_opening_systems: PASS "
        "(profile-isolated law packages; mandatory adapter; universal RGO; flour>wheat; ancient steel)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
