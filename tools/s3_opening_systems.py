#!/usr/bin/env python3
"""Validate and render S3 opening-system compatibility repairs."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

from dates import M2_MIRROR_LANGUAGES

ROOT = Path(__file__).resolve().parents[1]
LOC_ROOT = ROOT / "main_menu/localization"
GOODS = ROOT / "docs/m5/custom_goods.csv"
GOODS_SCRIPT = ROOT / "in_game/common/goods/00_antiquitas_raw_goods.txt"
ADVANCES = ROOT / "in_game/common/advances/00_antiquitas_m8_tree.txt"
LAWS = ROOT / "in_game/common/laws/01_common.txt"
SETUP = ROOT / "main_menu/setup/start/10_countries.txt"
REPORT = ROOT / "docs/s3/opening_systems.csv"
LANGUAGES = ("english", *M2_MIRROR_LANGUAGES)
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


def installed_wheat_food() -> float:
    config = json.loads((ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig"))
    directory = Path(config["game_dir"]) / "game/in_game/common/goods"
    for path in sorted(directory.glob("*.txt")):
        text = path.read_text(encoding="utf-8-sig")
        match = re.search(r"(?ms)^wheat\s*=\s*\{(?P<body>.*?)^\}", text)
        if match:
            food = re.search(r"(?m)^\s*food\s*=\s*(?P<value>[0-9.]+)", match.group("body"))
            if not food:
                raise ValueError("installed wheat definition has no food value")
            return float(food.group("value"))
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
    flour = float(custom_good("antq_grain_products")["food"])
    wheat = installed_wheat_food()
    rows = (
        ("processed_food_order", f"flour={flour:g};wheat={wheat:g}", "pass" if flour > wheat else "fail"),
        ("opening_rgo_capacity", "global_max_rgo_size_modifier=0.10", "pass"),
        ("parthian_profile_laws", "14 Iranian groups + Arsacid autonomy", "pass"),
        ("mandatory_law_adapter", "heir_religion_law retained and ancientized", "pass"),
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
    flour = float(custom_good("antq_grain_products")["food"])
    wheat = installed_wheat_food()
    if flour <= wheat:
        failures.append(f"Flour and Bread food {flour:g} is not above wheat {wheat:g}")

    advance = top_level_block(
        ADVANCES.read_text(encoding="utf-8-sig"),
        "antq_provincial_census",
    )
    if "global_max_rgo_size_modifier = 0.10" not in advance:
        failures.append("universally owned Provincial Census lacks opening RGO capacity")

    law = top_level_block(LAWS.read_text(encoding="utf-8-sig"), "heir_religion_law")
    if "ANTIQVITAS mounted-system quarantine" in law or "potential = { always = no }" in law:
        failures.append("mandatory heir_religion_law remains quarantined")

    parthia = top_level_block(SETUP.read_text(encoding="utf-8-sig"), "XAH")
    if re.search(r"(?m)^\s*laws\s*=", parthia):
        failures.append("Parthia emits blocked custom law assignments during setup")
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
