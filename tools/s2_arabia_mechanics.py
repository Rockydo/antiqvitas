#!/usr/bin/env python3
"""Render and audit the source-bounded interior-Arabia mechanical layer."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import struct
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageOps

from dates import M2_MIRROR_LANGUAGES
from dds import convert, identify


ROOT = Path(__file__).resolve().parents[1]
ACTION_SHEET = ROOT / "assets_queue/arabia_mechanics/sources/arabia_route_actions_01.png"
ACTION_MASTER_DIR = ROOT / "assets_queue/arabia_mechanics/masters"
ACTION_ICON_DIR = ROOT / "main_menu/gfx/interface/icons/generic_actions"
ACTION_OUTPUT = ROOT / "in_game/common/generic_actions/antq_s2_arabian_route_actions.txt"
AI_LIST_OUTPUT = ROOT / "in_game/common/generic_action_ai_lists/antq_s2_arabian_route_actions_list.txt"
BIAS_OUTPUT = ROOT / "in_game/common/biases/00_antiquitas_s2_arabian_routes.txt"
MANIFEST = ROOT / "docs/m12/arabia_mechanics_manifest.json"
LOC_ROOT = ROOT / "main_menu/localization"
IO_KEY = "antq_arabian_route_exchanges"
LANGUAGES = ("english", *M2_MIRROR_LANGUAGES)

PRIVILEGES = (
    "antq_agraean_oasis_watch_obligations",
    "antq_chaulotaean_pasture_route_compacts",
    "antq_kindite_interior_caravan_escort_terms",
    "antq_tamudaean_well_access_guarantees",
    "antq_gerrhaean_aromatic_transit_measures",
    "antq_gerrhaean_oasis_customs_watch",
    "antq_cataraean_gulf_anchorage_safe_conducts",
    "antq_omanite_coastal_pilotage_compacts",
    "antq_qatabanian_timna_transit_assessments",
    "antq_hadramite_shabwa_incense_store_custody",
    "antq_sabaean_interkingdom_caravan_safe_conducts",
    "antq_omanite_wadi_water_rotations",
)
BUILDINGS = (
    "antq_reg_south_arabian_terrace_sluices",
    "antq_reg_arabian_caravan_station",
    "antq_reg_aromatic_resin_sorting_house",
    "antq_reg_eastern_arabian_aflaj",
)
UNITS = (
    "antq_nabataean_caravan_guards",
    "antq_north_arabian_camel_scouts",
    "antq_south_arabian_highland_levies",
    "antq_omanite_coastal_warbands",
)
DOCTRINES = (
    "antq_doctrine_arabian_polytheism_sanctuary_leagues",
    "antq_doctrine_arabian_polytheism_aniconic_betyls",
    "antq_doctrine_arabian_polytheism_caravan_vows",
    "antq_doctrine_arabian_polytheism_rain_and_pasture_rites",
    "antq_doctrine_south_arabian_religion_temple_confederacies",
    "antq_doctrine_south_arabian_religion_incense_vows",
    "antq_doctrine_south_arabian_religion_irrigation_observance",
    "antq_doctrine_south_arabian_religion_pilgrimage_sanctuaries",
)
ARABIA_DESIGN_TAGS = (
    "NAB", "SAB", "HIM", "QAT", "HAD", "KIN",
    "THM", "AGR", "GRH", "QTR", "OMN", "BED",
)
QUADRANTS = ("top_left", "top_right", "bottom_left", "bottom_right")


@dataclass(frozen=True)
class RouteAction:
    key: str
    title: str
    description: str
    cost: int
    opinion: str
    opinion_label: str
    actor_effect: str
    target_effect: str


ACTIONS = (
    RouteAction(
        "antq_negotiate_route_safe_conduct",
        "Negotiate Route Safe-Conduct",
        "Exchange a bounded guarantee for merchants and messengers crossing a member polity's routes.",
        10,
        "antq_opinion_route_safe_conduct",
        "Route Safe-Conduct",
        "add_prestige = prestige_weak_bonus",
        "",
    ),
    RouteAction(
        "antq_coordinate_cistern_repairs",
        "Coordinate Cistern Repairs",
        "Share labor, tools, and provisions for a route cistern used by both member polities.",
        15,
        "antq_opinion_cistern_cooperation",
        "Cistern Cooperation",
        "",
        "add_stability = stability_weak_bonus",
    ),
    RouteAction(
        "antq_exchange_route_intelligence",
        "Exchange Route Intelligence",
        "Share reports about wells, pasture, disrupted passages, and caravan security.",
        8,
        "antq_opinion_route_intelligence",
        "Route Intelligence Shared",
        "add_legitimacy = legitimacy_weak_bonus",
        "",
    ),
    RouteAction(
        "antq_settle_transit_incident",
        "Settle Transit Incident",
        "Compensate losses and restore passage after a bounded caravan or watering dispute.",
        12,
        "antq_opinion_transit_settlement",
        "Transit Incident Settled",
        "add_stability = stability_weak_bonus",
        "",
    ),
)


def esc(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def action_block(action: RouteAction) -> str:
    actor_effect = f"\n\t\t\t{action.actor_effect}" if action.actor_effect else ""
    target_effect = f"\n\t\t\t{action.target_effect}" if action.target_effect else ""
    return f"""# STR-ARAB; PTO-ARAB; UNESCO-INCENSE [contested]
# Bilateral route adapter only: no defensive call, military access, annexation, or territorial claim.
{action.key} = {{
\ticon = {action.key}
\ttype = internationalorganization
\tai_tick = monthly
\tai_tick_frequency = 12
\tautomation_tick = monthly
\tautomation_tick_frequency = 1
\tshow_message_to_target = yes

\tpotential = {{
\t\texists = international_organization:{IO_KEY}
\t\tscope:actor = {{
\t\t\tis_member_of_international_organization = international_organization:{IO_KEY}
\t\t}}
\t}}

\tselect_trigger = {{
\t\tlooking_for_a = international_organization
\t\tsource = actor
\t\ttarget_flag = recipient
\t\tname = "choose_international_organization"
\t\tcolumn = {{ data = name }}
\t\tvisible = {{
\t\t\tinternational_organization_type = international_organization_type:{IO_KEY}
\t\t}}
\t}}

\tselect_trigger = {{
\t\tlooking_for_a = country
\t\ttarget_flag = target
\t\tname = "choose_country"
\t\tinteraction_source_list = {{
\t\t\tinternational_organization:{IO_KEY} = {{
\t\t\t\tevery_international_organization_member = {{
\t\t\t\t\tadd_to_list = source
\t\t\t\t}}
\t\t\t}}
\t\t}}
\t\tcolumn = {{ data = name }}
\t\tvisible = {{
\t\t\tthis != scope:actor
\t\t\tis_member_of_international_organization = international_organization:{IO_KEY}
\t\t}}
\t}}

\tallow = {{
\t\texists = scope:target
\t\tscope:actor = {{ gold >= {action.cost} }}
\t\tscope:target = {{
\t\t\tis_member_of_international_organization = international_organization:{IO_KEY}
\t\t}}
\t}}

\tcooldown = {{
\t\ttype = {action.key}
\t\tyears = 3
\t}}

\teffect = {{
\t\tscope:actor = {{
\t\t\tadd_gold = -{action.cost}{actor_effect}
\t\t}}
\t\tscope:target = {{
\t\t\tadd_opinion = {{ target = scope:actor modifier = {action.opinion} }}{target_effect}
\t\t}}
\t}}

\tai_will_do = {{
\t\tadd = {{ value = 12 }}
\t\tif = {{
\t\t\tlimit = {{ scope:actor = {{ gold < {action.cost * 2} }} }}
\t\t\tadd = {{ value = -30 }}
\t\t}}
\t}}
}}"""


def action_script() -> str:
    return (
        "# Generated by tools/s2_arabia_mechanics.py --write.\n"
        "# Arabian Route Exchanges is non-territorial and non-military.\n\n"
        + "\n\n".join(action_block(action) for action in ACTIONS)
        + "\n"
    )


def ai_list_script() -> str:
    actions = "\n".join(f"\t\t{action.key}" for action in ACTIONS)
    return (
        "# Generated by tools/s2_arabia_mechanics.py --write.\n"
        "antq_s2_arabian_route_actions_list = {\n"
        "\tpotential = { always = yes }\n"
        "\tactions = {\n"
        f"{actions}\n"
        "\t}\n"
        "}\n"
    )


def bias_script() -> str:
    values = (15, 12, 10, 14)
    lines = [
        "# Generated by tools/s2_arabia_mechanics.py --write.",
        "# Temporary bilateral trust from bounded route cooperation.",
        "",
    ]
    for action, value in zip(ACTIONS, values, strict=True):
        lines.extend((
            f"{action.opinion} = {{",
            f"\tvalue = {value}",
            "\tyearly_decay = 1",
            "}",
            "",
        ))
    return "\n".join(lines)


def localization(language: str) -> str:
    lines = [f"l_{language}:"]
    for action in ACTIONS:
        lines.extend((
            f' {action.key}: "{esc(action.title)}"',
            f' {action.key}_desc: "{esc(action.description)}"',
            f' {action.opinion}: "{esc(action.opinion_label)}"',
        ))
    return "\n".join(lines) + "\n"


def messages(language: str) -> str:
    lines = [f"l_{language}:"]
    for action in ACTIONS:
        message = f"PERFORM_{action.key}_ACTION"
        lines.extend((
            f' {message}_SETUP: "When a member polity uses the ${action.key}$ action."',
            f' {message}_HEADER: "$MESSENGER$"',
            f' {message}_TITLE: "[SCOPE.sCountry(\'actor\').GetName] has used ${action.key}$."',
            f' {message}_EFFECTS: "$EFFECT$"',
            f' {message}_LOG: "${message}_TITLE$"',
            f' {message}_BTN1: "OK"',
            f' {message}_BTN2: "OK"',
            f' {message}_BTN3: "$common_string_go_to$"',
            f' {message}_MAP: ""',
        ))
    return "\n".join(lines) + "\n"


def outputs() -> dict[Path, str]:
    result = {
        ACTION_OUTPUT: action_script(),
        AI_LIST_OUTPUT: ai_list_script(),
        BIAS_OUTPUT: bias_script(),
    }
    for language in LANGUAGES:
        result[
            LOC_ROOT / language / f"antq_s2_arabian_routes_l_{language}.yml"
        ] = localization(language)
        result[
            LOC_ROOT / language / f"antq_s2_arabian_route_messages_l_{language}.yml"
        ] = messages(language)
    return result


def quadrant_box(size: tuple[int, int], index: int) -> tuple[int, int, int, int]:
    width, height = size
    if width != height or width % 2:
        raise ValueError(f"Arabian action source must be an even square 2x2 sheet, got {size}")
    half = width // 2
    return (
        (0, 0, half, half),
        (half, 0, width, half),
        (0, half, half, height),
        (half, half, width, height),
    )[index]


def write_art() -> None:
    ACTION_MASTER_DIR.mkdir(parents=True, exist_ok=True)
    ACTION_ICON_DIR.mkdir(parents=True, exist_ok=True)
    with Image.open(ACTION_SHEET) as source:
        for index, action in enumerate(ACTIONS):
            crop = source.crop(quadrant_box(source.size, index)).convert("RGBA")
            master = ImageOps.fit(crop, (128, 128), method=Image.Resampling.LANCZOS)
            master_path = ACTION_MASTER_DIR / f"{action.key}_128.png"
            texture_path = ACTION_ICON_DIR / f"{action.key}.dds"
            master.save(master_path, optimize=True)
            convert(master_path, texture_path, "dxt5", True)


def load_keys(path: Path) -> set[str]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return {row["key"] for row in csv.DictReader(handle)}


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest() -> dict[str, object]:
    return {
        "scope": "AD 1 interior Arabia regional mechanics",
        "source_boundary": (
            "Distinct political, water, route, military, and cult profiles; no unsupported "
            "north/east/Omani ethnic polygons or uniform peninsula constitution."
        ),
        "counts": {
            "privileges": len(PRIVILEGES),
            "buildings": len(BUILDINGS),
            "building_seeds": 16,
            "units": len(UNITS),
            "direct_doctrines": len(DOCTRINES),
            "route_actions": len(ACTIONS),
            "route_io_members": len(ARABIA_DESIGN_TAGS),
            "generated_assets": 32,
        },
        "route_io": {
            "key": IO_KEY,
            "design_tags": list(ARABIA_DESIGN_TAGS),
            "nonmilitary": True,
            "nonterritorial": True,
        },
        "art": {
            "action_sheet": ACTION_SHEET.relative_to(ROOT).as_posix(),
            "action_sheet_sha256": file_sha256(ACTION_SHEET),
            "style_references": (
                "Installed EU5 category-matched building, privilege, unit, "
                "religious-aspect, and generic-action DDS assets under "
                "assets_queue/arabia_mechanics/vanilla_references."
            ),
            "four_up_contract": True,
        },
        "sources": [
            "P8.5", "P8.6", "P11", "P13", "P14", "STR-ARAB",
            "PTO-ARAB", "OCD-GERRHA", "THAJ-ARCH", "NABATAEA-MAP",
            "UNESCO-QATABAN", "UNESCO-INCENSE", "UNESCO-SABA", "HIMYAR-HIST",
        ],
    }


def expected_unit_textures() -> list[Path]:
    from m12_unit_art import destinations, roster

    rows = roster()
    return [destinations(rows[key])[2] for key in UNITS]


def validate() -> list[str]:
    failures: list[str] = []
    ledger_contracts = (
        (ROOT / "docs/m6/estate_order_privileges.csv", PRIVILEGES, "privilege"),
        (ROOT / "docs/m5/regional_building_families.csv", BUILDINGS, "building"),
        (ROOT / "docs/m7/units.csv", UNITS, "unit"),
    )
    for path, expected, label in ledger_contracts:
        missing = sorted(set(expected) - load_keys(path))
        if missing:
            failures.append(f"missing Arabian {label} keys: {', '.join(missing)}")
    with (ROOT / "docs/m5/regional_building_seeds.csv").open(
        encoding="utf-8-sig", newline=""
    ) as handle:
        seed_rows = [row for row in csv.DictReader(handle) if row["key"].startswith("reg_arabia_")]
    if len(seed_rows) != 16 or {row["family"] for row in seed_rows} != set(BUILDINGS):
        failures.append("Arabian regional-building seed contract is not 16 placements / 4 families")
    if any(row["macro"] != "Middle East" for row in seed_rows):
        failures.append("Arabian regional-building seeds escaped the Middle East macro")

    io_script = ROOT / "in_game/common/international_organizations/00_antiquitas_m9.txt"
    io_start = ROOT / "main_menu/setup/start/15_international_organizations.txt"
    for path in (io_script, io_start):
        if not path.is_file() or IO_KEY not in path.read_text(encoding="utf-8-sig"):
            failures.append(f"missing Arabian route IO contract in {path.relative_to(ROOT)}")
    if io_start.is_file():
        start_text = io_start.read_text(encoding="utf-8-sig")
        engine_tags = json.loads(
            (ROOT / "docs/world_1ad/tag_map.json").read_text(encoding="utf-8-sig")
        )["entries"]
        mapping = {row["design_tag"]: row["engine_tag"] for row in engine_tags}
        missing_tags = [
            tag for tag in ARABIA_DESIGN_TAGS if mapping[tag] not in start_text
        ]
        if missing_tags:
            failures.append(f"Arabian route IO start membership misses: {', '.join(missing_tags)}")

    for path, expected in outputs().items():
        if not path.is_file():
            failures.append(f"missing generated route file: {path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8-sig") != expected:
            failures.append(f"stale generated route file: {path.relative_to(ROOT)}")

    textures = [
        *(ROOT / f"main_menu/gfx/interface/icons/privileges/{key}.dds" for key in PRIVILEGES),
        *(ROOT / f"main_menu/gfx/interface/icons/buildings/{key}.dds" for key in BUILDINGS),
        *expected_unit_textures(),
        *(ROOT / f"main_menu/gfx/interface/icons/religious_aspects/{key}.dds" for key in DOCTRINES),
        *(ACTION_ICON_DIR / f"{action.key}.dds" for action in ACTIONS),
    ]
    for texture in textures:
        if not texture.is_file():
            failures.append(f"missing Arabian direct texture: {texture.relative_to(ROOT)}")
    for action in ACTIONS:
        master = ACTION_MASTER_DIR / f"{action.key}_128.png"
        texture = ACTION_ICON_DIR / f"{action.key}.dds"
        if master.is_file():
            with Image.open(master) as image:
                if image.mode != "RGBA" or image.size != (128, 128):
                    failures.append(f"wrong route-action master contract: {action.key}")
        if texture.is_file() and identify(texture) != {
            "format": "DDS", "width": "128", "height": "128",
            "depth": "8", "channels": "srgba 4.0",
        }:
            failures.append(f"wrong route-action DDS contract: {action.key}")
        elif texture.is_file():
            raw = texture.read_bytes()
            if len(raw) < 128 or struct.unpack_from("<I", raw, 28)[0] != 8:
                failures.append(f"route-action DDS lacks full mip chain: {action.key}")
    expected_manifest = json.dumps(manifest(), indent=2, ensure_ascii=False) + "\n"
    if not MANIFEST.is_file():
        failures.append("missing Arabia mechanics manifest")
    elif MANIFEST.read_text(encoding="utf-8-sig") != expected_manifest:
        failures.append("stale Arabia mechanics manifest")
    return failures


def write() -> None:
    write_art()
    for path, content in outputs().items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8-sig", newline="\n")
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(
        json.dumps(manifest(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


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
    except (OSError, ValueError, csv.Error, json.JSONDecodeError) as exc:
        failures = [str(exc)]
    if failures:
        print("s2_arabia_mechanics: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(
        "s2_arabia_mechanics: PASS "
        "(12 privileges; 4 buildings / 16 placements; 4 units; "
        "8 cult icons; 4 route actions; 32 direct assets)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
