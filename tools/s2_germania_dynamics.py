#!/usr/bin/env python3
"""Render and audit the source-bounded Germania/Baltic dynamics tranche."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

from dates import AntqDate, M2_MIRROR_LANGUAGES
from dds import convert, identify


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "assets_queue/germania_dynamics/sources"
MASTER_DIR = ROOT / "assets_queue/germania_dynamics/masters"
ACTION_ICON_DIR = ROOT / "main_menu/gfx/interface/icons/generic_actions"
BUILDING_ICON_DIR = ROOT / "main_menu/gfx/interface/icons/buildings"
BUILDING_MASTER_DIR = ROOT / "assets_queue/generated"
SITUATION_DIR = ROOT / "main_menu/gfx/interface/illustrations/situation"
UNIT_SHEET_DIR = ROOT / "assets_queue/generated/unit_icons/sheets"
ACTION_OUTPUT = ROOT / "in_game/common/generic_actions/antq_s2_germania_actions.txt"
AI_LIST_OUTPUT = ROOT / "in_game/common/generic_action_ai_lists/antq_s2_germania_actions_list.txt"
BIAS_OUTPUT = ROOT / "in_game/common/biases/00_antiquitas_s2_germania_actions.txt"
SITUATION_OUTPUT = ROOT / "in_game/common/situations/antq_s2_germania_dynamics.txt"
LOC_ROOT = ROOT / "main_menu/localization"
MANIFEST = ROOT / "docs/m12/germania_dynamics_manifest.json"
LANGUAGES = ("english", *M2_MIRROR_LANGUAGES)
QUADRANTS = ("top_left", "top_right", "bottom_left", "bottom_right")

FRONTIER_IO = "antq_germanic_frontier_exchanges"
NORTHERN_IO = "antq_northern_amber_assemblies"


@dataclass(frozen=True)
class Action:
    key: str
    title: str
    description: str
    io: str
    cost: int
    opinion: str
    opinion_label: str
    actor_effect: str
    target_effect: str
    sheet: str
    quadrant: str


@dataclass(frozen=True)
class BuildingArt:
    key: str
    sheet: str
    quadrant: str


@dataclass(frozen=True)
class SituationArt:
    key: str
    title: str
    description: str
    sheet: str
    quadrant: str


@dataclass(frozen=True)
class NewSituation:
    key: str
    title: str
    description: str
    start: AntqDate
    end: AntqDate
    anchor: str
    monthly_effect: str
    source: str


ACTIONS = (
    Action("antq_send_frontier_envoys", "Send Frontier Envoys", "Send interpreters and gift-bearers to settle a bounded frontier question.", FRONTIER_IO, 10, "antq_opinion_frontier_envoys", "Frontier Envoys Received", "add_prestige = prestige_weak_bonus", "", "germania_actions_01.png", "top_left"),
    Action("antq_hold_rhine_frontier_market", "Hold Rhine Frontier Market", "Open a guarded market meeting for livestock, metalwork, salt, and frontier exchange.", FRONTIER_IO, 15, "antq_opinion_frontier_market", "Frontier Market Held", "", "add_stability = stability_weak_bonus", "germania_actions_01.png", "top_right"),
    Action("antq_exchange_frontier_hostages", "Exchange Frontier Hostages", "Exchange elite wards as a limited guarantee without asserting permanent submission.", FRONTIER_IO, 12, "antq_opinion_frontier_hostages", "Hostage Guarantee", "add_legitimacy = legitimacy_weak_bonus", "", "germania_actions_01.png", "bottom_left"),
    Action("antq_settle_rhine_border_incident", "Settle Border Incident", "Compensate losses and restore passage after a bounded river or pasture dispute.", FRONTIER_IO, 12, "antq_opinion_border_settlement", "Border Incident Settled", "add_stability = stability_weak_bonus", "", "germania_actions_01.png", "bottom_right"),
    Action("antq_coordinate_river_passage", "Coordinate River Passage", "Arrange boats, guides, and provisions for a declared movement across a frontier river.", FRONTIER_IO, 14, "antq_opinion_river_passage", "River Passage Coordinated", "add_prestige = prestige_weak_bonus", "", "germania_actions_02.png", "top_left"),
    Action("antq_renew_auxiliary_compact", "Renew Auxiliary Compact", "Renew bounded service, pay, and return guarantees with a frontier partner.", FRONTIER_IO, 18, "antq_opinion_auxiliary_compact", "Auxiliary Compact Renewed", "add_legitimacy = legitimacy_weak_bonus", "add_prestige = prestige_weak_bonus", "germania_actions_03.png", "bottom_left"),
    Action("antq_send_amber_convoy", "Send Amber Convoy", "Dispatch a guarded amber convoy through coastal and river-portage contacts.", NORTHERN_IO, 10, "antq_opinion_amber_convoy", "Amber Convoy Received", "add_prestige = prestige_weak_bonus", "", "germania_actions_02.png", "top_right"),
    Action("antq_negotiate_migrant_transit", "Negotiate Migrant Transit", "Set terms for a migrating following to cross another polity's routes and pastures.", NORTHERN_IO, 12, "antq_opinion_migrant_transit", "Migrant Transit Agreed", "add_stability = stability_weak_bonus", "", "germania_actions_02.png", "bottom_left"),
    Action("antq_muster_allied_host", "Muster Allied Host", "Coordinate provisions and a temporary host without creating a permanent confederate army.", NORTHERN_IO, 18, "antq_opinion_allied_host", "Allied Host Mustered", "add_prestige = prestige_weak_bonus", "add_legitimacy = legitimacy_weak_bonus", "germania_actions_02.png", "bottom_right"),
    Action("antq_witness_assembly_compact", "Witness Assembly Compact", "Exchange witnesses at an assembly to preserve a negotiated inter-polity compact.", NORTHERN_IO, 10, "antq_opinion_assembly_compact", "Assembly Compact Witnessed", "add_legitimacy = legitimacy_weak_bonus", "", "germania_actions_03.png", "top_left"),
    Action("antq_exchange_retinue_gifts", "Exchange Retinue Gifts", "Exchange restrained gifts between leading households and their armed followings.", NORTHERN_IO, 12, "antq_opinion_retinue_gifts", "Retinue Gifts Exchanged", "add_prestige = prestige_weak_bonus", "", "germania_actions_03.png", "top_right"),
    Action("antq_proclaim_sacred_truce", "Proclaim Sacred Truce", "Place a short inter-polity truce under witnessed sacred observance.", NORTHERN_IO, 14, "antq_opinion_sacred_truce", "Sacred Truce Proclaimed", "add_stability = stability_weak_bonus", "add_stability = stability_weak_bonus", "germania_actions_03.png", "bottom_right"),
)

BUILDINGS = (
    BuildingArt("antq_reg_marcomannic_royal_compound", "germania_buildings_01.png", "top_left"),
    BuildingArt("antq_reg_germanic_assembly_field", "germania_buildings_01.png", "top_right"),
    BuildingArt("antq_reg_semnonian_sacred_grove", "germania_buildings_01.png", "bottom_left"),
    BuildingArt("antq_reg_rhine_frontier_market", "germania_buildings_01.png", "bottom_right"),
    BuildingArt("antq_reg_batavian_auxiliary_muster", "germania_buildings_02.png", "top_left"),
    BuildingArt("antq_reg_aestian_amber_sorting_ground", "germania_buildings_02.png", "top_right"),
    BuildingArt("antq_reg_vistula_migration_staging", "germania_buildings_02.png", "bottom_left"),
    BuildingArt("antq_reg_north_sea_boat_landing", "germania_buildings_02.png", "bottom_right"),
)

SITUATION_ART = (
    SituationArt("antq_s2_maroboduus_rivalry", "Maroboduus and the Rhine Coalitions", "Marcomannic royal power, Cheruscan coalition politics, and Roman pressure compete without predetermining Teutoburg or a Germanic union.", "germania_situations_01.png", "top_left"),
    SituationArt("antq_m10_immensum_bellum", "Immensum Bellum", "Roman operations beyond the Rhine meet independent assemblies, retinues, and shifting frontier coalitions.", "germania_situations_01.png", "top_right"),
    SituationArt("antq_m10_batavian_revolt", "Batavian Revolt", "Batavian auxiliary ties and lower-Rhine autonomy turn into a bounded revolt current.", "germania_situations_01.png", "bottom_left"),
    SituationArt("antq_m10_second_marcomannic_wars", "Marcomannic Wars", "Danubian war and migration pressure strain Rome and independent northern polities.", "germania_situations_01.png", "bottom_right"),
    SituationArt("antq_m10_second_gothic_migration", "Gothic Migration", "Gutonic movements from the lower Vistula toward the Pontic world develop over generations.", "germania_situations_02.png", "top_left"),
    SituationArt("antq_s2_alemannic_formation", "Alemannic Formation", "A later upper-Rhine confederate identity may emerge from changing local coalitions.", "germania_situations_02.png", "top_right"),
    SituationArt("antq_s2_frankish_formation", "Frankish Formation", "A later lower-Rhine confederate identity may emerge without retrojecting Franks into AD 1.", "germania_situations_02.png", "bottom_left"),
    SituationArt("antq_s2_aestian_amber_shore", "Aestian Amber Shore", "Plural Aestian shore communities connect amber exchange and sacred landscapes without becoming a Baltic superstate.", "germania_situations_02.png", "bottom_right"),
)

NEW_SITUATIONS = (
    NewSituation("antq_s2_maroboduus_rivalry", SITUATION_ART[0].title, SITUATION_ART[0].description, AntqDate.parse("1.1.1"), AntqDate.parse("20.1.1"), "XBK", "add_legitimacy = legitimacy_weak_bonus", "P8.7;STR-GER;TAC-ANN-II;OCD-CHER"),
    NewSituation("antq_s2_alemannic_formation", SITUATION_ART[5].title, SITUATION_ART[5].description, AntqDate.parse("213.1.1"), AntqDate.parse("215.1.1"), "XBL", "add_prestige = prestige_weak_bonus", "P8.7;OCD-ALE"),
    NewSituation("antq_s2_frankish_formation", SITUATION_ART[6].title, SITUATION_ART[6].description, AntqDate.parse("250.1.1"), AntqDate.parse("261.1.1"), "BTV", "add_prestige = prestige_weak_bonus", "P8.7;CAM-FRK"),
    NewSituation("antq_s2_aestian_amber_shore", SITUATION_ART[7].title, SITUATION_ART[7].description, AntqDate.parse("1.1.1"), AntqDate.parse("476.9.4"), "AES", "add_stability = stability_weak_bonus", "P8.7;TAC-GER;PAN-WBB;VU-BRUSH;LIT-WLSC"),
)

UNITS = (
    "antq_marcomannic_royal_retinue",
    "antq_batavian_auxiliary_cohort",
    "antq_semnonian_grove_muster",
    "antq_aestian_amber_road_guards",
    "antq_gothic_migrant_host",
    "antq_alamannic_confederate_host",
    "antq_frankish_rhine_warband",
    "antq_saxon_coastal_warband",
)


def esc(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def action_block(action: Action) -> str:
    actor_effect = f"\n\t\t\t{action.actor_effect}" if action.actor_effect else ""
    target_effect = f"\n\t\t\t{action.target_effect}" if action.target_effect else ""
    return f"""# {("STR-GER; TAC-GER; TAC-ANN-II" if action.io == FRONTIER_IO else "TAC-GER; PAN-WBB; VU-BRUSH")} [contested]
# Non-territorial adapter only: no alliance, military access, annexation, or shared Germanic sovereignty.
{action.key} = {{
\ticon = {action.key}
\ttype = internationalorganization
\tai_tick = monthly
\tai_tick_frequency = 12
\tautomation_tick = monthly
\tautomation_tick_frequency = 1
\tshow_message_to_target = yes

\tpotential = {{
\t\texists = international_organization:{action.io}
\t\tscope:actor = {{ is_member_of_international_organization = international_organization:{action.io} }}
\t}}
\tselect_trigger = {{
\t\tlooking_for_a = international_organization
\t\tsource = actor
\t\ttarget_flag = recipient
\t\tname = "choose_international_organization"
\t\tcolumn = {{ data = name }}
\t\tvisible = {{ international_organization_type = international_organization_type:{action.io} }}
\t}}
\tselect_trigger = {{
\t\tlooking_for_a = country
\t\ttarget_flag = target
\t\tname = "choose_country"
\t\tinteraction_source_list = {{
\t\t\tinternational_organization:{action.io} = {{
\t\t\t\tevery_international_organization_member = {{ add_to_list = source }}
\t\t\t}}
\t\t}}
\t\tcolumn = {{ data = name }}
\t\tvisible = {{
\t\t\tthis != scope:actor
\t\t\tis_member_of_international_organization = international_organization:{action.io}
\t\t}}
\t}}
\tallow = {{
\t\texists = scope:target
\t\tscope:actor = {{ gold >= {action.cost} }}
\t\tscope:target = {{ is_member_of_international_organization = international_organization:{action.io} }}
\t}}
\tcooldown = {{ type = {action.key} years = 5 }}
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
    return "# Generated by tools/s2_germania_dynamics.py --write.\n\n" + "\n\n".join(action_block(action) for action in ACTIONS) + "\n"


def ai_list_script() -> str:
    actions = "\n".join(f"\t\t{action.key}" for action in ACTIONS)
    return (
        "# Generated by tools/s2_germania_dynamics.py --write.\n"
        "antq_s2_germania_actions_list = {\n"
        "\tpotential = { always = yes }\n"
        "\tactions = {\n"
        f"{actions}\n"
        "\t}\n"
        "}\n"
    )


def bias_script() -> str:
    lines = ["# Generated by tools/s2_germania_dynamics.py --write.", ""]
    for index, action in enumerate(ACTIONS):
        lines.extend((f"{action.opinion} = {{", f"\tvalue = {10 + index % 6}", "\tyearly_decay = 1", "}", ""))
    return "\n".join(lines)


def situation_script() -> str:
    lines = [
        "# Generated by tools/s2_germania_dynamics.py --write.",
        "# All dates are AntqDate-validated; pressure is deliberately low-frequency.",
        "",
    ]
    for record in NEW_SITUATIONS:
        lines.extend((
            f"# {record.source}",
            f"{record.key} = {{",
            "\tmonthly_spawn_chance = monthly_spawn_chance_unique",
            f"\tcontent_trigger = {{ tag = {record.anchor} }}",
            "\tcan_start = {",
            f"\t\tcurrent_date >= {record.start.engine()}",
            f"\t\tcurrent_date < {record.end.engine()}",
            f"\t\tcountry_exists = c:{record.anchor}",
            "\t}",
            "\tcan_end = {",
            "\t\tOR = {",
            f"\t\t\tcurrent_date >= {record.end.engine()}",
            f"\t\t\tvar:{record.key}_resolution_progress >= 100",
            "\t\t}",
            "\t}",
            f"\tvisible = {{ country_exists = c:{record.anchor} }}",
            "\ton_start = {",
            f"\t\tset_variable = {{ name = {record.key}_resolution_progress value = 0 }}",
            f"\t\tc:{record.anchor} = {{ {record.monthly_effect} }}",
            "\t}",
            "\ton_monthly = {",
            f"\t\tc:{record.anchor} = {{",
            "\t\t\tif = {",
            "\t\t\t\tlimit = { stability >= 20 at_war = no }",
            f"\t\t\t\troot = {{ change_variable = {{ name = {record.key}_resolution_progress add = 3 }} }}",
            "\t\t\t}",
            "\t\t\telse_if = {",
            "\t\t\t\tlimit = { stability >= 0 at_war = yes }",
            f"\t\t\t\troot = {{ change_variable = {{ name = {record.key}_resolution_progress add = 1.5 }} }}",
            "\t\t\t}",
            f"\t\t\telse = {{ root = {{ change_variable = {{ name = {record.key}_resolution_progress add = 0.5 }} }} }}",
            "\t\t\trandom_list = {",
            f"\t\t\t\t1 = {{ {record.monthly_effect} }}",
            "\t\t\t\t23 = {}",
            "\t\t\t}",
            "\t\t}",
            "\t}",
            "\ton_ended = {",
            f"\t\tif = {{ limit = {{ has_variable = {record.key}_resolution_progress }} remove_variable = {record.key}_resolution_progress }}",
            "\t}",
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
    for record in NEW_SITUATIONS:
        lines.extend((
            f' {record.key}: "{esc(record.title)}"',
            f' {record.key}_desc: "{esc(record.description)}"',
            f' {record.key}_info: "{esc(record.description)}"',
        ))
    return "\n".join(lines) + "\n"


def messages(language: str) -> str:
    lines = [f"l_{language}:"]
    for action in ACTIONS:
        key = f"PERFORM_{action.key}_ACTION"
        lines.extend((
            f' {key}_SETUP: "When a polity uses the ${action.key}$ action."',
            f' {key}_HEADER: "$MESSENGER$"',
            f' {key}_TITLE: "[SCOPE.sCountry(\'actor\').GetName] has used ${action.key}$."',
            f' {key}_EFFECTS: "$EFFECT$"',
            f' {key}_LOG: "${key}_TITLE$"',
            f' {key}_BTN1: "OK"',
            f' {key}_BTN2: "OK"',
            f' {key}_BTN3: "$common_string_go_to$"',
            f' {key}_MAP: ""',
        ))
    return "\n".join(lines) + "\n"


def outputs() -> dict[Path, str]:
    rendered = {
        ACTION_OUTPUT: action_script(),
        AI_LIST_OUTPUT: ai_list_script(),
        BIAS_OUTPUT: bias_script(),
        SITUATION_OUTPUT: situation_script(),
    }
    for language in LANGUAGES:
        rendered[LOC_ROOT / language / f"antq_s2_germania_dynamics_l_{language}.yml"] = localization(language)
        rendered[LOC_ROOT / language / f"antq_s2_germania_messages_l_{language}.yml"] = messages(language)
    return rendered


def quadrant_box(size: tuple[int, int], quadrant: str) -> tuple[int, int, int, int]:
    width, height = size
    if width < 512 or height < 512:
        raise ValueError(f"four-up source is too small, got {size}")
    half_x, half_y = width // 2, height // 2
    return {
        "top_left": (0, 0, half_x, half_y),
        "top_right": (half_x, 0, width, half_y),
        "bottom_left": (0, half_y, half_x, height),
        "bottom_right": (half_x, half_y, width, height),
    }[quadrant]


def crop(sheet: str, quadrant: str, size: tuple[int, int], mode: str) -> Image.Image:
    with Image.open(SOURCE_DIR / sheet) as source:
        piece = source.crop(quadrant_box(source.size, quadrant)).convert(mode)
        return ImageOps.fit(piece, size, method=Image.Resampling.LANCZOS)


def write_art() -> None:
    for directory in (MASTER_DIR, ACTION_ICON_DIR, BUILDING_ICON_DIR, BUILDING_MASTER_DIR, SITUATION_DIR, UNIT_SHEET_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    for action in ACTIONS:
        master = MASTER_DIR / f"{action.key}_128.png"
        crop(action.sheet, action.quadrant, (128, 128), "RGBA").save(master, optimize=True)
        convert(master, ACTION_ICON_DIR / f"{action.key}.dds", "dxt5", True)
    for building in BUILDINGS:
        raw = crop(building.sheet, building.quadrant, (128, 128), "RGBA")
        keyed = raw.copy()
        keyed.putalpha(Image.new("L", raw.size, 255))
        pixels = list(keyed.getdata())
        keyed.putdata([
            (red, green, blue, 0 if max(red, green, blue) < 72 else min(255, max(0, (max(red, green, blue) - 60) * 6)))
            for red, green, blue, _alpha in pixels
        ])
        icon = Image.new("RGBA", raw.size, (16, 25, 43, 255))
        icon.alpha_composite(keyed)
        mask = Image.new("L", icon.size, 0)
        ImageDraw.Draw(mask).ellipse((3, 3, 124, 124), fill=255)
        icon.putalpha(mask.filter(ImageFilter.GaussianBlur(0.7)))
        master = BUILDING_MASTER_DIR / f"{building.key}_128.png"
        icon.save(master, optimize=True)
        icon.save(MASTER_DIR / f"{building.key}_128.png", optimize=True)
        convert(master, BUILDING_ICON_DIR / f"{building.key}.dds", "dxt5", True)
    for situation in SITUATION_ART:
        master = MASTER_DIR / f"{situation.key}_1080x440.png"
        crop(situation.sheet, situation.quadrant, (1080, 440), "RGBA").save(master, optimize=True)
        convert(master, SITUATION_DIR / f"{situation.key}.dds", "dxt5", True)
    shutil.copyfile(SOURCE_DIR / "germania_units_01.png", UNIT_SHEET_DIR / "unit_sheet_15_germania_opening_depth.png")
    shutil.copyfile(SOURCE_DIR / "germania_units_02.png", UNIT_SHEET_DIR / "unit_sheet_16_germania_late_confederations.png")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_keys(path: Path) -> set[str]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return {(row.get("key") or "").strip() for row in csv.DictReader(handle)}


def manifest() -> dict[str, object]:
    return {
        "scope": "Germania, lower Rhine, lower Vistula, Scandinavia, and Aestian shore dynamics",
        "source_boundary": "Independent polities and plural Aestian communities; the two IOs are hidden UI adapters, never shared sovereignty, alliance, or territorial organizations.",
        "counts": {
            "actions": len(ACTIONS),
            "regional_buildings": len(BUILDINGS),
            "regional_building_seeds": 24,
            "units": len(UNITS),
            "situation_illustrations": len(SITUATION_ART),
            "new_recurring_situations": len(NEW_SITUATIONS),
            "direct_assets": len(ACTIONS) + len(BUILDINGS) + len(UNITS) + len(SITUATION_ART),
        },
        "art": {
            "four_up_contract": True,
            "sources": {
                path.name: file_sha256(path)
                for path in sorted(SOURCE_DIR.glob("germania_*.png"))
            },
            "style_references": "Actual installed EU5 generic-action, building, unit, and situation assets copied to assets_queue/germania_dynamics/vanilla_references and supplied category-by-category.",
        },
        "sources": [
            "P8.7", "P14", "STR-GER", "TAC-GER", "TAC-ANN-II", "OCD-CHER",
            "OCD-QUA", "TAC-BAT", "PAN-WBB", "VU-BRUSH", "LIT-WLSC", "UT-TARAND",
        ],
    }


def write() -> None:
    write_art()
    for path, content in outputs().items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8-sig", newline="\n")
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print("s2_germania_dynamics: wrote 36 direct assets, 12 actions, and 4 recurring situations")


def validate() -> list[str]:
    failures: list[str] = []
    if len(ACTIONS) != 12 or len(BUILDINGS) != 8 or len(UNITS) != 8 or len(SITUATION_ART) != 8:
        failures.append("Germania tranche count contract is not 12 actions / 8 buildings / 8 units / 8 situations")
    for path, expected in outputs().items():
        if not path.is_file():
            failures.append(f"missing generated file: {path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8-sig") != expected:
            failures.append(f"stale generated file: {path.relative_to(ROOT)}")
    contracts = (
        (ROOT / "docs/m5/regional_building_families.csv", {item.key for item in BUILDINGS}, "building"),
        (ROOT / "docs/m7/units.csv", set(UNITS), "unit"),
    )
    for path, expected, label in contracts:
        missing = sorted(expected - load_keys(path))
        if missing:
            failures.append(f"missing Germania {label} ledger keys: {missing}")
    seed_path = ROOT / "docs/m5/regional_building_seeds.csv"
    if seed_path.is_file():
        with seed_path.open(encoding="utf-8-sig", newline="") as handle:
            rows = [row for row in csv.DictReader(handle) if (row.get("key") or "").startswith("reg_germania_depth_")]
        if len(rows) != 24 or {row["family"] for row in rows} != {item.key for item in BUILDINGS}:
            failures.append("Germania building seed contract is not 24 placements / 8 families")
    for io in (FRONTIER_IO, NORTHERN_IO):
        for path in (
            ROOT / "in_game/common/international_organizations/00_antiquitas_m9.txt",
            ROOT / "main_menu/setup/start/15_international_organizations.txt",
        ):
            if not path.is_file() or io not in path.read_text(encoding="utf-8-sig"):
                failures.append(f"missing {io} contract in {path.relative_to(ROOT)}")
    textures = [
        *(ACTION_ICON_DIR / f"{item.key}.dds" for item in ACTIONS),
        *(BUILDING_ICON_DIR / f"{item.key}.dds" for item in BUILDINGS),
        *(SITUATION_DIR / f"{item.key}.dds" for item in SITUATION_ART),
    ]
    for texture in textures:
        if not texture.is_file():
            failures.append(f"missing direct texture: {texture.relative_to(ROOT)}")
            continue
        try:
            info = identify(texture)
            if info["format"] != "DDS":
                failures.append(f"invalid DDS texture: {texture.relative_to(ROOT)}")
        except Exception as exc:
            failures.append(f"unreadable DDS {texture.relative_to(ROOT)}: {exc}")
    for situation in SITUATION_ART:
        texture = SITUATION_DIR / f"{situation.key}.dds"
        if texture.is_file():
            info = identify(texture)
            if (info["width"], info["height"]) != ("1080", "440"):
                failures.append(f"wrong situation texture geometry: {situation.key}")
    for sheet in ("unit_sheet_15_germania_opening_depth.png", "unit_sheet_16_germania_late_confederations.png"):
        if not (UNIT_SHEET_DIR / sheet).is_file():
            failures.append(f"missing M12 four-up unit source: {sheet}")
    if not MANIFEST.is_file() or json.loads(MANIFEST.read_text(encoding="utf-8")) != manifest():
        failures.append("missing or stale Germania dynamics manifest")
    action_text = ACTION_OUTPUT.read_text(encoding="utf-8-sig") if ACTION_OUTPUT.is_file() else ""
    if "can_declare_war" in action_text or "military_access" in action_text:
        failures.append("Germania exchange actions escaped their non-military boundary")
    situation_text = SITUATION_OUTPUT.read_text(encoding="utf-8-sig") if SITUATION_OUTPUT.is_file() else ""
    if "AES" not in situation_text or "476.9.4" not in situation_text:
        failures.append("Aestian amber-shore situation lost its plural long-duration boundary")
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
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        failures = [str(exc)]
    if failures:
        print("s2_germania_dynamics: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return 1
    print("s2_germania_dynamics: PASS (12 actions; 8 buildings; 8 units; 8 situations; 36 direct assets)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
