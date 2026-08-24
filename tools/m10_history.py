#!/usr/bin/env python3
"""Render the first M10 historical-current batch from the shared timeline.

The AD 1-96 batch uses the installed dynamic-historical-event contract for
dated events and the installed situation/disaster managers for ongoing crises.
Every emitted date originates in ``docs/timeline.csv`` and passes through
``AntqDate`` before it reaches a game script.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path

from advance_event_packages import knowledge_response_lines
from dates import AntqDate, M2_MIRROR_LANGUAGES, days_between, load_timeline, offset_date
from goods_integration import event_effect_lines

ROOT = Path(__file__).resolve().parents[1]
TIMELINE = ROOT / "docs/timeline.csv"
TAG_MAP = ROOT / "docs/world_1ad/tag_map.json"
EVENT_OUTPUT = ROOT / "in_game/events/antq_m10_first_century.txt"
TEUTOBURG_TRIGGER_OUTPUT = ROOT / "in_game/common/scripted_triggers/antq_s7_teutoburg.txt"
TEUTOBURG_LIFESPAN_GUARD = "antq_m6_historical_lifespan_guard"
SITUATION_OUTPUT = ROOT / "in_game/common/situations/antq_m10_first_century.txt"
DISASTER_OUTPUT = ROOT / "in_game/common/disasters/antq_m10_first_century.txt"
LOC_ROOT = ROOT / "main_menu/localization"
COLOR_OUTPUT = ROOT / "main_menu/common/named_colors/antq_m10_transformations.txt"
COA_OUTPUT = ROOT / "main_menu/common/coat_of_arms/coat_of_arms/antq_m10_transformations.txt"
NORTH_XIONGNU_SEED = ROOT / "docs/m10/northern_xiongnu_48_locations.csv"
START_COUNTRIES = ROOT / "main_menu/setup/start/10_countries.txt"
LOCATION_COORDINATES = ROOT / "docs/vanilla_symbols/location_coordinates.json"
BATCH_END = AntqDate.parse("96.1.1")

TEUTOBURG_OPPONENTS = ("CRU", "CHT", "BRC", "MCM", "SEM", "BTV", "FRI", "SGM", "LAN")
TEUTOBURG_POLICY_EVENT = "antq_m10.1099"


def progress_variable(record: object) -> str:
    """Return a collision-proof progress variable for a historical current."""
    return f"{record.script_key}_resolution_progress"


def resolution_trigger_lines(record: object, *, country_scoped: bool) -> tuple[str, ...]:
    """End through earned progress; the sourced date is only a safety bound."""
    variable = progress_variable(record)
    return (
        "\tcan_end = {",
        "\t\tOR = {",
        f"\t\t\tcurrent_date >= {record.end_date.engine()}",
        f"\t\t\tvar:{variable} >= 100",
        "\t\t}",
        "\t}",
    )


def current_lifecycle_lines(record: object, *, country_scoped: bool) -> tuple[str, ...]:
    """Render staged progress, recurring pressure, and recovery for a current.

    Peaceful consolidation is the fastest route. A stable mobilized state can
    force a slower resolution, while a collapsing state still inches toward the
    safety bound. The pressure tick spends manpower, tax/market income, and food
    instead of substituting prestige notifications for material consequences.
    """
    variable = progress_variable(record)
    profile = event_choice_profile(record)
    peace_rate, war_rate, collapse_rate = {
        "contest": (2.5, 1.75, 0.5),
        "frontier": (2.25, 2.0, 0.5),
        "crisis": (2.0, 1.0, 0.5),
        "belief": (3.0, 1.0, 0.75),
        "exchange": (3.25, 1.25, 0.75),
        "foundation": (2.75, 1.5, 0.5),
        "government": (2.75, 1.25, 0.5),
    }[profile]
    disease = record.key in {"antonine_plague", "cyprian_plague"}
    baseline_pressure = (
        (
            "add_manpower = { value = monthly_manpower multiply = -0.5 }",
            "add_gold = { value = monthly_income_trade_and_tax multiply = -0.25 }",
            "capital = { province = { change_province_food_percentage = -0.01 } }",
        )
        if disease
        else (
            "add_manpower = { value = monthly_manpower multiply = -0.25 }",
            "add_gold = { value = monthly_income_trade_and_tax multiply = -0.15 }",
            "capital = { province = { change_province_food_percentage = -0.005 } }",
        )
    )
    pressure_effects = baseline_pressure + {
        "contest": ("add_stability = stability_weak_penalty",),
        "frontier": ("add_war_exhaustion = war_exhaustion_weak_bonus",),
        "crisis": ("add_stability = stability_weak_penalty",),
        "belief": (
            "add_religious_influence_if_valid = { VALUE = religious_influence_weak_penalty }",
        ),
        "exchange": ("add_prestige = prestige_weak_penalty",),
        "foundation": ("add_legitimacy = legitimacy_weak_penalty",),
        "government": ("add_stability = stability_weak_penalty",),
    }[profile]
    success_effects = {
        "contest": ("add_army_tradition = army_tradition_weak_bonus", "add_stability = stability_weak_bonus"),
        "frontier": ("add_army_tradition = army_tradition_mild_bonus", "add_prestige = prestige_weak_bonus"),
        "crisis": ("add_stability = stability_mild_bonus",),
        "belief": ("add_religious_influence_if_valid = { VALUE = religious_influence_mild_bonus }",),
        "exchange": ("add_research_progress = research_progress_weak_bonus", "add_prestige = prestige_weak_bonus"),
        "foundation": ("add_legitimacy = legitimacy_mild_bonus", "add_stability = stability_weak_bonus"),
        "government": ("add_legitimacy = legitimacy_weak_bonus", "add_stability = stability_weak_bonus"),
    }[profile]
    failure_effects = {
        "contest": ("add_stability = stability_mild_penalty",),
        "frontier": ("add_war_exhaustion = war_exhaustion_mild_bonus",),
        "crisis": ("add_stability = stability_mild_penalty",),
        "belief": ("add_religious_influence_if_valid = { VALUE = religious_influence_mild_penalty }",),
        "exchange": ("add_prestige = prestige_mild_penalty",),
        "foundation": ("add_legitimacy = legitimacy_mild_penalty",),
        "government": ("add_stability = stability_mild_penalty",),
    }[profile]
    pressure_weight = 3 if disease else 1
    empty_weight = 9 if disease else 23
    milestone_variables = tuple(
        f"{record.script_key}_milestone_{threshold}" for threshold in (25, 50, 75)
    )
    start_event = (
        f"\t\ttrigger_event_non_silently = {record.event_key}"
        if country_scoped else
        f"\t\tc:{record.engine_tag} = {{ trigger_event_non_silently = {record.event_key} }}"
    )
    end_key = "on_end" if country_scoped else "on_ended"
    lines = [
        "\ton_start = {",
        f"\t\tset_variable = {{ name = {variable} value = 0 }}",
        start_event,
        "\t}",
        "\ton_monthly = {",
    ]
    if not country_scoped:
        lines.append(f"\t\tc:{record.engine_tag} = {{")
    country_indent = "\t\t" if country_scoped else "\t\t\t"
    progress_prefix = "" if country_scoped else "root = { "
    progress_suffix = "" if country_scoped else " }"
    lines.extend((
        f"{country_indent}if = {{",
        f"{country_indent}\tlimit = {{ stability >= 20 at_war = no }}",
        f"{country_indent}\t{progress_prefix}change_variable = {{ name = {variable} add = {peace_rate:g} }}{progress_suffix}",
        f"{country_indent}}}",
        f"{country_indent}else_if = {{",
        f"{country_indent}\tlimit = {{ stability >= 0 at_war = yes }}",
        f"{country_indent}\t{progress_prefix}change_variable = {{ name = {variable} add = {war_rate:g} }}{progress_suffix}",
        f"{country_indent}}}",
        f"{country_indent}else = {{",
        f"{country_indent}\t{progress_prefix}change_variable = {{ name = {variable} add = {collapse_rate:g} }}{progress_suffix}",
        f"{country_indent}}}",
        f"{country_indent}random_list = {{",
        f"{country_indent}\t{pressure_weight} = {{",
        *(f"{country_indent}\t\t{effect}" for effect in pressure_effects),
        f"{country_indent}\t}}",
        f"{country_indent}\t{empty_weight} = {{}}",
        f"{country_indent}}}",
    ))
    if not country_scoped:
        lines.append("\t\t}")
    for threshold, milestone in zip((25, 50, 75), milestone_variables):
        lines.extend((
            "\t\tif = {",
            f"\t\t\tlimit = {{ var:{variable} >= {threshold} NOT = {{ has_variable = {milestone} }} }}",
            f"\t\t\tset_variable = {milestone}",
            (
                "\t\t\tadd_prestige = prestige_weak_bonus"
                if country_scoped else
                f"\t\t\tc:{record.engine_tag} ?= {{ add_prestige = prestige_weak_bonus }}"
            ),
            "\t\t}",
        ))
    lines.extend(("\t}", f"\t{end_key} = {{", "\t\tif = {", f"\t\t\tlimit = {{ var:{variable} >= 100 }}"))
    if country_scoped:
        lines.extend(f"\t\t\t{effect}" for effect in success_effects)
    else:
        lines.append(f"\t\t\tc:{record.engine_tag} ?= {{")
        lines.extend(f"\t\t\t\t{effect}" for effect in success_effects)
        lines.append("\t\t\t}")
    lines.extend(("\t\t}", "\t\telse = {"))
    if country_scoped:
        lines.extend(f"\t\t\t{effect}" for effect in failure_effects)
    else:
        lines.append(f"\t\t\tc:{record.engine_tag} ?= {{")
        lines.extend(f"\t\t\t\t{effect}" for effect in failure_effects)
        lines.append("\t\t\t}")
    lines.extend(("\t\t}", f"\t\tif = {{ limit = {{ has_variable = {variable} }} remove_variable = {variable} }}"))
    lines.extend(
        f"\t\tif = {{ limit = {{ has_variable = {milestone} }} remove_variable = {milestone} }}"
        for milestone in milestone_variables
    )
    lines.extend(("\t}",))
    return tuple(lines)


def situation_presentation_lines(key: str, anchor_tag: str) -> tuple[str, ...]:
    """Render the panel and map contract required by active situations.

    The map callback runs in location scope, so the anchor country's owned
    locations receive its current country color while the rest use the engine's
    neutral data-map color.  Tooltip and legend keys are generated by the
    visible-unions localization mirror for every supported language.
    """
    return (
        "\ttooltip = {",
        f'\t\tcustom_tooltip = "{key}_tooltip"',
        "\t}",
        "\tis_data_map = yes",
        "\tmap_color = {",
        "\t\tif = {",
        f"\t\t\tlimit = {{ owner ?= c:{anchor_tag} }}",
        "\t\t\tvalue = owner.country_color",
        "\t\t}",
        "\t\telse = {",
        "\t\t\tvalue = define:NMapColors|DEFAULT_COLOR",
        "\t\t}",
        "\t}",
        "\tlegend_key = {",
        f'\t\tdesc = "{key}_legend"',
        "\t\tcolor = define:NMapColors|MAP_COLOR_HIGH",
        "\t}",
    )


def disaster_modifier_lines(record: object) -> tuple[str, ...]:
    """Apply continuous human and fiscal costs while a disaster is active."""
    if record.key in {"antonine_plague", "cyprian_plague"}:
        return (
            "\tmodifier = {",
            "\t\tglobal_population_growth = -0.003",
            "\t\tglobal_manpower_modifier = -0.12",
            "\t\tglobal_monthly_food_modifier = -0.10",
            "\t\ttax_income_efficiency = small_tax_income_efficiency_penalty",
            "\t}",
        )
    return (
        "\tmodifier = {",
        "\t\tglobal_manpower_modifier = -0.04",
        "\t\tglobal_monthly_food_modifier = -0.025",
        "\t\ttax_income_efficiency = tiny_tax_income_efficiency_penalty",
        "\t}",
    )
NORTH_XIONGNU_TAG = "XNO"
NORTH_XIONGNU_MAX_Y = 1945.0

# The event recipient is the narrowest safe political actor for each current.
# It determines the game-facing notification and effects, not exclusive
# historical ownership of a multi-polity event.
TARGETS = {
    "gaius_eastern_settlement": "ARM",
    "immensum_bellum": "ROM",
    "illyrian_revolt": "ROM",
    "teutoburg": "ROM",
    "wang_mang_xin": "HAN",
    "augustan_succession": "ROM",
    "tacfarinas_war": "ROM",
    "florus_sacrovir": "ROM",
    "kushan_unification": "YUE",
    "christianity_foundation": "JUD",
    "trung_sisters": "HAN",
    "mauretania_annexation": "MAU",
    "claudian_britain": "ROM",
    "xiongnu_split": "XIO",
    "silphium_extinction": "ROM",
    "armenian_war": "ARM",
    "boudica_revolt": "ICE",
    "great_fire_rome": "ROM",
    "buddhism_han_court": "HAN",
    "tiridates_coronation": "ARM",
    "great_jewish_revolt": "JUD",
    "second_temple_destruction": "JUD",
    "year_four_emperors": "ROM",
    "batavian_revolt": "BTV",
    "vesuvius": "ROM",
    "mons_graupius": "ROM",
    "dacian_wars": "DAC",
    "han_xianbei": "HAN",
}

# A deliberately small, reviewed set of event illustrations.  Keep art links
# here instead of hand-editing the generated script so regeneration preserves
# the game-visible reference and validation can prove that its texture exists.
EVENT_IMAGES = {
    "augustan_succession": "gfx/interface/illustrations/event/antq_augustan_succession.dds",
    "armenian_war": "gfx/interface/illustrations/event/antq_armenian_war.dds",
    "batavian_revolt": "gfx/interface/illustrations/event/antq_batavian_revolt.dds",
    "boudica_revolt": "gfx/interface/illustrations/event/antq_boudica_revolt.dds",
    "buddhism_han_court": "gfx/interface/illustrations/event/antq_buddhism_han_court.dds",
    "christianity_foundation": "gfx/interface/illustrations/event/antq_christianity_foundation.dds",
    "claudian_britain": "gfx/interface/illustrations/event/antq_claudian_britain.dds",
    "dacian_wars": "gfx/interface/illustrations/event/antq_dacian_wars.dds",
    "florus_sacrovir": "gfx/interface/illustrations/event/antq_florus_sacrovir.dds",
    "gaius_eastern_settlement": "gfx/interface/illustrations/event/antq_gaius_eastern_settlement.dds",
    "great_fire_rome": "gfx/interface/illustrations/event/antq_great_fire_rome.dds",
    "great_jewish_revolt": "gfx/interface/illustrations/event/antq_great_jewish_revolt.dds",
    "han_xianbei": "gfx/interface/illustrations/event/antq_han_xianbei.dds",
    "illyrian_revolt": "gfx/interface/illustrations/event/antq_illyrian_revolt.dds",
    "immensum_bellum": "gfx/interface/illustrations/event/antq_immensum_bellum.dds",
    "kushan_unification": "gfx/interface/illustrations/event/antq_kushan_unification.dds",
    "mauretania_annexation": "gfx/interface/illustrations/event/antq_mauretania_annexation.dds",
    "mons_graupius": "gfx/interface/illustrations/event/antq_mons_graupius.dds",
    "second_temple_destruction": "gfx/interface/illustrations/event/antq_second_temple_destruction.dds",
    "silphium_extinction": "gfx/interface/illustrations/event/antq_silphium_extinction.dds",
    "tacfarinas_war": "gfx/interface/illustrations/event/antq_tacfarinas_war.dds",
    "teutoburg": "gfx/interface/illustrations/event/antq_teutoburg.dds",
    "tiridates_coronation": "gfx/interface/illustrations/event/antq_tiridates_coronation.dds",
    "trung_sisters": "gfx/interface/illustrations/event/antq_trung_sisters.dds",
    "vesuvius": "gfx/interface/illustrations/event/antq_vesuvius.dds",
    "wang_mang_xin": "gfx/interface/illustrations/event/antq_xin_dynasty_crisis.dds",
    "xiongnu_split": "gfx/interface/illustrations/event/antq_xiongnu_split.dds",
    "year_four_emperors": "gfx/interface/illustrations/event/antq_year_four_emperors.dds",
}


@dataclass(frozen=True)
class Current:
    key: str
    kind: str
    date: AntqDate
    end_date: AntqDate
    region: str
    summary: str
    rails: str
    source: str
    label: str
    design_tag: str
    engine_tag: str
    event_id: int

    @property
    def script_key(self) -> str:
        return f"antq_m10_{self.key}"

    @property
    def event_key(self) -> str:
        return f"antq_m10.{self.event_id}"


def engine_tags() -> dict[str, str]:
    payload = json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))
    return {entry["design_tag"]: entry["engine_tag"] for entry in payload["entries"]}


def matching_block(text: str, open_brace: int) -> str:
    """Return one balanced Paradox block, including its braces."""
    depth = 0
    for index, character in enumerate(text[open_brace:], open_brace):
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                return text[open_brace : index + 1]
    raise ValueError("unterminated Paradox block")


def validate_ai_chance_syntax(script: str, *, source: str) -> None:
    """Reject effect-flow syntax inside event MTTH/AI-weight blocks.

    EU5 parses ``ai_chance`` with the mean-time-to-happen grammar: conditional
    weights must be ``modifier`` blocks. Effect-style ``if``/``add`` tokens can
    make the engine abandon the containing option and reject every later event
    even when the file's braces are balanced.
    """
    for match in re.finditer(r"\bai_chance\s*=\s*\{", script):
        block = matching_block(script, match.end() - 1)
        invalid = re.search(r"(?m)^\s*(?:if|else_if|else|add)\s*=", block)
        if invalid is not None:
            line = script.count("\n", 0, match.start()) + 1
            raise ValueError(
                f"{source}:{line}: ai_chance uses effect-flow token "
                f"{invalid.group(0).strip()} instead of modifier = {{ factor = ... }}"
            )


def start_country_locations(tag: str) -> frozenset[str]:
    """Read the checked M3 start surface so a later map revision cannot silently
    turn a dated release into an empty country.
    """
    text = START_COUNTRIES.read_text(encoding="utf-8-sig")
    country = re.search(rf"(?m)^\s*{re.escape(tag)}\s*=\s*\{{", text)
    if country is None:
        raise ValueError(f"M10 source country {tag} is absent from the AD 1 start")
    country_block = matching_block(text, country.end() - 1)
    ownership = re.search(r"\bown_control_core\s*=\s*\{", country_block)
    if ownership is None:
        raise ValueError(f"M10 source country {tag} has no core ownership block")
    ownership_block = matching_block(country_block, ownership.end() - 1)
    return frozenset(re.findall(r"(?m)^\s*([A-Za-z][A-Za-z0-9_]*)\s*$", ownership_block[1:-1]))


def northern_xiongnu_locations() -> tuple[str, ...]:
    """Load the reviewed AD 48 Northern-Xiongnu map proxy.

    `IRAN-XIO` fixes the broad historical distinction--the northern polity
    remained in Mongolia while the southern polity moved within Han's northern
    frontier--but does not provide EU5 location-by-location borders.  The CSV
    materializes the northern slice of the reviewed M3 Xiongnu surface; checks
    below keep that approximation explicit and reviewable.
    """
    with NORTH_XIONGNU_SEED.open(encoding="utf-8-sig", newline="") as handle:
        rows = tuple(csv.DictReader(handle))
    required_fields = {"location", "role", "selection", "source"}
    if not rows or not required_fields.issubset(rows[0]):
        raise ValueError("Northern Xiongnu seed has an invalid header")
    locations = tuple(row["location"].strip() for row in rows)
    if any(not location for location in locations):
        raise ValueError("Northern Xiongnu seed contains an empty location")
    if len(locations) != len(set(locations)):
        raise ValueError("Northern Xiongnu seed contains duplicate locations")
    capitals = tuple(row["location"].strip() for row in rows if row["role"].strip() == "capital")
    if len(capitals) != 1 or capitals[0] != locations[0]:
        raise ValueError("Northern Xiongnu seed must begin with its sole capital location")
    if any(not row["selection"].strip() or not row["source"].strip() for row in rows):
        raise ValueError("Northern Xiongnu seed lacks its approximation rationale")

    coordinates = json.loads(LOCATION_COORDINATES.read_text(encoding="utf-8"))["locations"]
    missing_coordinates = sorted(set(locations) - set(coordinates))
    if missing_coordinates:
        raise ValueError(f"Northern Xiongnu locations absent from coordinate index: {missing_coordinates}")
    too_southern = [location for location in locations if coordinates[location]["y"] >= NORTH_XIONGNU_MAX_Y]
    if too_southern:
        raise ValueError(f"Northern Xiongnu location slice crosses its documented coordinate boundary: {too_southern}")
    absent_from_xiongnu = sorted(set(locations) - start_country_locations("XIO"))
    if absent_from_xiongnu:
        raise ValueError(f"Northern Xiongnu locations are not AD 1 Xiongnu holdings: {absent_from_xiongnu}")
    return locations


def currents() -> tuple[Current, ...]:
    mapped_tags = engine_tags()
    result: list[Current] = []
    for row in load_timeline(TIMELINE):
        if row["rails_strength"].strip() == "system":
            continue
        date = AntqDate.parse(row["date"])
        if date >= BATCH_END:
            continue
        key = row["key"].strip()
        design_tag = TARGETS.get(key)
        if design_tag is None:
            raise ValueError(f"M10 first-century target missing for {key}")
        if design_tag not in mapped_tags:
            raise ValueError(f"M10 target {design_tag} for {key} is absent from tag map")
        end_value = row.get("end_date", "").strip()
        if not end_value:
            raise ValueError(f"M10 first-century current {key} needs an end date")
        result.append(
            Current(
                key=key,
                kind=row["type"].strip(),
                date=date,
                end_date=AntqDate.parse(end_value),
                region=row["region"].strip(),
                summary=row["summary"].strip(),
                rails=row["rails_strength"].strip(),
                source=row["source"].strip(),
                label=row["label"].strip(),
                design_tag=design_tag,
                engine_tag=mapped_tags[design_tag],
                event_id=1000 + len(result),
            )
        )
    return tuple(result)


def validate(records: tuple[Current, ...]) -> None:
    if not records:
        raise ValueError("M10 first-century batch is empty")
    if set(TARGETS) != {record.key for record in records}:
        missing = sorted(set(TARGETS) - {record.key for record in records})
        extra = sorted({record.key for record in records} - set(TARGETS))
        raise ValueError(f"M10 first-century ledger/target mismatch: missing={missing}, extra={extra}")
    unknown_images = sorted(set(EVENT_IMAGES) - {record.key for record in records})
    if unknown_images:
        raise ValueError(f"M10 illustration map has no corresponding current: {unknown_images}")
    for image in EVENT_IMAGES.values():
        texture = ROOT / "main_menu" / image
        if not texture.is_file():
            raise ValueError(f"M10 event illustration is missing: {texture}")
    if len({record.event_id for record in records}) != len(records):
        raise ValueError("M10 event IDs must be unique")
    mapped_tags = engine_tags()
    if NORTH_XIONGNU_TAG in mapped_tags.values():
        raise ValueError(f"M10 dynamic tag {NORTH_XIONGNU_TAG} collides with the AD 1 tag map")
    northern_xiongnu_locations()
    for record in records:
        if record.kind not in {"situation", "disaster", "event", "tagswitch", "formation"}:
            raise ValueError(f"unsupported M10 kind for {record.key}: {record.kind}")
        if record.rails != "Strong":
            raise ValueError(f"M10 first-century current {record.key} must retain Strong rails")
        if record.end_date <= record.date:
            raise ValueError(f"M10 first-century current {record.key} has an invalid window")
        if not record.source or not record.label or not record.summary:
            raise ValueError(f"M10 first-century current {record.key} lacks source text")


def event_outcome(record: Current) -> str:
    if record.key == "teutoburg":
        return "negative"
    if record.key == "second_temple_destruction":
        return "negative"
    if record.kind == "disaster":
        return "negative"
    if record.kind in {"formation", "tagswitch"}:
        return "positive"
    return "neutral"


def impact_lines(record: Current) -> tuple[str, ...]:
    """Use only effects harvested from installed country-event files."""
    if record.key == "teutoburg":
        return (
            "\t\tadd_manpower = { value = monthly_manpower multiply = -3 }",
            "\t\tadd_war_exhaustion = war_exhaustion_severe_bonus",
            "\t\tadd_stability = stability_mild_penalty",
            "\t\tadd_prestige = prestige_mild_penalty",
            "\t\tvar:antq_teutoburg_opponent ?= {",
            "\t\t\tadd_prestige = prestige_mild_bonus",
            "\t\t\tadd_army_tradition = army_tradition_mild_bonus",
            "\t\t}",
        )
    if record.key == "christianity_foundation":
        return (
            "\t\treligion:antq_early_christianity = {",
            "\t\t\tenable_religion = yes",
            "\t\t\tcreate_holy_site = { name = antq_christian_jerusalem_memory type = pilgrimage_city importance = 5 location = location:jerusalem religions = { religion:antq_early_christianity } }",
            "\t\t\tcreate_holy_site = { name = antq_christian_antioch_community type = pilgrimage_city importance = 4 location = location:antioch religions = { religion:antq_early_christianity } }",
            "\t\t\tcreate_holy_site = { name = antq_christian_ephesos_community type = pilgrimage_city importance = 3 location = location:ayasuluk religions = { religion:antq_early_christianity } }",
            "\t\t\tcreate_holy_site = { name = antq_christian_roman_memory type = pilgrimage_city importance = 5 location = location:rome religions = { religion:antq_early_christianity } }",
            "\t\t}",
            "\t\t# The AD 30 current seeds a small Jerusalem community; it does not convert Judea.",
            "\t\tlocation:jerusalem = {",
            "\t\t\tevery_pop = {",
            "\t\t\t\tlimit = { religion = religion:antq_judaism }",
            "\t\t\t\tsplit_pop = { fraction = 0.02 religion = religion:antq_early_christianity }",
            "\t\t\t}",
            "\t\t}",
            "\t\tadd_prestige = prestige_mild_bonus",
        )
    if record.key == "second_temple_destruction":
        return (
            "\t\tlocation:jerusalem = {",
            "\t\t\tif = {",
            "\t\t\t\tlimit = { has_building_with_at_least_one_level = antq_second_temple_jerusalem }",
            '\t\t\t\tdestroy_building = "building(building_type:antq_second_temple_jerusalem|owner)"',
            "\t\t\t}",
            "\t\t}",
            "\t\tadd_stability = stability_mild_penalty",
        )
    if record.key == "kushan_unification":
        return (
            "\t\tchange_tag_cosmetic = { tag = KSH }",
            "\t\tset_country_rank = country_rank:rank_empire",
            "\t\tadd_prestige = prestige_mild_bonus",
            "\t\tadd_legitimacy = legitimacy_mild_bonus",
        )
    if record.key == "xiongnu_split":
        locations = northern_xiongnu_locations()
        capital, *territory = locations
        lines = [
            "\t\t# Northern slice: IRAN-XIO; local M3 coordinate proxy, documented in docs/m10/.",
            f"\t\tlocation:{capital} = {{",
            "\t\t\tcreate_country_from_location = {",
            f"\t\t\t\tdefine_unique_country_tag = {NORTH_XIONGNU_TAG}",
            f"\t\t\t\tchange_country_name = {NORTH_XIONGNU_TAG}",
            f"\t\t\t\tchange_country_adjective = {NORTH_XIONGNU_TAG}",
            f"\t\t\t\tchange_country_color = map_{NORTH_XIONGNU_TAG}",
            f"\t\t\t\tchange_country_flag = {NORTH_XIONGNU_TAG}",
            "\t\t\t\tchange_culture = ROOT.culture",
            "\t\t\t\tchange_religion = ROOT.religion",
            "\t\t\t\tchange_government_type = government_type:steppe_horde",
            "\t\t\t\tadd_reform = government_reform:antq_steppe_confederation",
            "\t\t\t\tchange_heir_selection = heir_selection:tribal_oldest_male",
            "\t\t\t}",
            f"\t\t\tadd_core = c:{NORTH_XIONGNU_TAG}",
            "\t\t}",
            "\t\tevery_owned_location = {",
            "\t\t\tlimit = {",
            "\t\t\t\tOR = {",
        ]
        lines.extend(f"\t\t\t\t\tthis = location:{location}" for location in territory)
        lines.extend((
            "\t\t\t\t}",
            "\t\t\t}",
            f"\t\t\tchange_location_owner = c:{NORTH_XIONGNU_TAG}",
            f"\t\t\tadd_core = c:{NORTH_XIONGNU_TAG}",
            "\t\t}",
            "\t\tchange_tag_cosmetic = { tag = XSO }",
            "\t\tadd_stability = stability_mild_penalty",
        ))
        return tuple(lines)
    if record.kind == "disaster":
        return ("\t\tadd_stability = stability_mild_penalty", "\t\tadd_prestige = prestige_mild_penalty")
    if record.kind == "situation":
        return ("\t\tadd_stability = stability_weak_penalty",)
    if record.kind in {"formation", "tagswitch"}:
        return ("\t\tadd_prestige = prestige_mild_bonus", "\t\tadd_legitimacy = legitimacy_mild_bonus")
    return ("\t\tadd_prestige = prestige_mild_bonus",)


def event_choice_profile(record: object) -> str:
    """Classify a current for authored choice text and materially distinct costs."""
    key = record.key
    if record.kind == "disaster":
        return "crisis"
    if record.kind == "situation":
        return "contest"
    if record.kind in {"formation", "tagswitch"}:
        return "foundation"
    if any(token in key for token in (
        "christian", "buddh", "celestial", "manichae", "conversion",
        "nicaea", "thessalonica", "chalcedon", "temple", "olympic",
    )):
        return "belief"
    if any(token in key for token in ("mission", "embassy", "paper", "silphium")):
        return "exchange"
    if any(token in key for token in (
        "teutoburg", "fire", "wall", "graupius", "caledonia", "sack",
    )):
        return "frontier"
    return "government"


EVENT_CHOICE_TEXT = {
    "contest": (
        "Pursue the recorded settlement of {label}.",
        "Negotiate a local compact for {label}.",
        "Mobilize to impose a settlement in {label}.",
    ),
    "crisis": (
        "Follow the recorded emergency measures for {label}.",
        "Fund local relief and reconstruction during {label}.",
        "Impose guarded rationing throughout {label}.",
    ),
    "foundation": (
        "Recognize the political order created by {label}.",
        "Build {label} through negotiated local compacts.",
        "Impose the new order of {label} from the center.",
    ),
    "belief": (
        "Accept the recorded religious settlement of {label}.",
        "Protect debate and competing communities during {label}.",
        "Bind the court publicly to one side of {label}.",
    ),
    "exchange": (
        "Adopt the practice transmitted through {label}.",
        "Fund the merchants and scholars carrying {label}.",
        "Keep the knowledge of {label} under court supervision.",
    ),
    "frontier": (
        "Carry out the recorded frontier response to {label}.",
        "Rebuild locally and bargain through {label}.",
        "Answer {label} with forts and concentrated troops.",
    ),
    "government": (
        "Accept the recorded constitutional course of {label}.",
        "Seek consent through offices during {label}.",
        "Issue a binding central decree for {label}.",
    ),
}


def event_choice_localization(record: object) -> tuple[str, str, str]:
    if record.key == "teutoburg":
        return (
            "Accept the Varian disaster and withdraw the shattered commands.",
            "Extricate the field army through prepared Rhine positions.",
            "Concentrate reinforcements and contest the frontier campaign.",
        )
    return tuple(
        text.format(label=record.label)
        for text in EVENT_CHOICE_TEXT[event_choice_profile(record)]
    )


def event_path_variable(record: object, path: str) -> str:
    return f"antq_m10_{record.key}_{path}_path"


def historical_event_choice_lines(record: object) -> tuple[str, ...]:
    path_state = (
        () if record.key == "odoacer_finale" else
        (f"\t\tset_variable = {event_path_variable(record, 'chronicle')}",)
    )
    return (
        *path_state,
        "\t\tai_chance = {",
        "\t\t\tbase = 50",
        "\t\t\tmodifier = { factor = 1.24 stability >= 20 }",
        "\t\t\tmodifier = { factor = 0.84 at_war = yes }",
        "\t\t}",
    )


def alternative_event_option_lines(record: object) -> tuple[str, ...]:
    """Provide two persistent, non-cosmetic alternatives to the historical path."""
    profile = event_choice_profile(record)
    if record.key == "teutoburg":
        second = (
            "\t\tadd_gold = -18",
            "\t\tadd_manpower = { value = monthly_manpower multiply = -1 }",
            "\t\tadd_war_exhaustion = war_exhaustion_weak_bonus",
            "\t\tadd_stability = stability_weak_bonus",
            "\t\tvar:antq_teutoburg_opponent ?= { add_prestige = prestige_weak_bonus }",
        )
        third = (
            "\t\tadd_gold = -24",
            "\t\tadd_manpower = { value = monthly_manpower multiply = -2 }",
            "\t\tadd_war_exhaustion = war_exhaustion_mild_bonus",
            "\t\tadd_army_tradition = army_tradition_mild_bonus",
            "\t\tvar:antq_teutoburg_opponent ?= { add_manpower = { value = monthly_manpower multiply = -1 } }",
        )
    elif profile == "crisis":
        second = ("\t\tadd_gold = -24", "\t\tadd_stability = stability_weak_bonus", "\t\tadd_prestige = prestige_mild_bonus")
        third = ("\t\tadd_manpower = { value = monthly_manpower multiply = -1 }", "\t\tadd_stability = stability_weak_penalty", "\t\tadd_legitimacy = legitimacy_mild_bonus")
    elif profile in {"contest", "frontier"}:
        second = ("\t\tadd_gold = -16", "\t\tadd_stability = stability_weak_bonus", "\t\tadd_prestige = prestige_mild_penalty")
        third = ("\t\tadd_gold = -10", "\t\tadd_manpower = { value = monthly_manpower multiply = -1.5 }", "\t\tadd_stability = stability_weak_penalty", "\t\tadd_prestige = prestige_mild_bonus")
    elif profile == "belief":
        second = ("\t\tadd_gold = -18", "\t\tadd_stability = stability_weak_bonus", "\t\tadd_prestige = prestige_mild_bonus")
        third = ("\t\tadd_legitimacy = legitimacy_mild_bonus", "\t\tadd_stability = stability_weak_penalty")
    elif profile == "exchange":
        second = ("\t\tadd_gold = -20", "\t\tadd_prestige = prestige_mild_bonus")
        third = ("\t\tadd_gold = -10", "\t\tadd_stability = stability_weak_bonus", "\t\tadd_prestige = prestige_mild_penalty")
    elif profile == "foundation":
        second = ("\t\tadd_gold = -20", "\t\tadd_stability = stability_weak_bonus")
        third = ("\t\tadd_legitimacy = legitimacy_mild_bonus", "\t\tadd_stability = stability_weak_penalty", "\t\tadd_prestige = prestige_mild_bonus")
    else:
        second = ("\t\tadd_gold = -18", "\t\tadd_stability = stability_weak_bonus", "\t\tadd_prestige = prestige_mild_penalty")
        third = ("\t\tadd_legitimacy = legitimacy_mild_bonus", "\t\tadd_stability = stability_weak_penalty", "\t\tadd_prestige = prestige_mild_bonus")
    compact_state = (
        () if record.key == "odoacer_finale" else
        (f"\t\tset_variable = {event_path_variable(record, 'compact')}",)
    )
    command_state = (
        () if record.key == "odoacer_finale" else
        (f"\t\tset_variable = {event_path_variable(record, 'command')}",)
    )
    return (
        "\toption = {",
        f"\t\tname = {record.event_key}.b",
        *compact_state,
        *second,
        "\t\tai_chance = {",
        "\t\t\tbase = 30",
        "\t\t\tmodifier = { factor = 1.6 stability < 0 }",
        "\t\t\tmodifier = { factor = 0.6 gold < 30 }",
        "\t\t}",
        "\t}",
        "\toption = {",
        f"\t\tname = {record.event_key}.c",
        *command_state,
        *third,
        "\t\tai_chance = {",
        "\t\t\tbase = 20",
        "\t\t\tmodifier = { factor = 1.75 at_war = yes }",
        "\t\t\tmodifier = { factor = 0.25 monthly_manpower < 1 }",
        "\t\t}",
        "\t}",
    )


def event_script(records: tuple[Current, ...]) -> str:
    lines = [
        "# Generated by tools/m10_history.py --write; first-century historical currents.",
        "# Dates are emitted only from docs/timeline.csv through AntqDate.",
        "namespace = antq_m10",
        "",
    ]
    for record in records:
        lines.extend((
            f"# {record.label}; {record.source}; recipient={record.design_tag}",
            f"{record.event_key} = {{",
            "\ttype = country_event",
            f"\ttitle = {record.event_key}.title",
            f"\tdesc = {record.event_key}.desc",
            f"\toutcome = {event_outcome(record)}",
            "\tfire_only_once = yes",
        ))
        image = EVENT_IMAGES.get(record.key)
        if image is not None:
            lines.append(f'\timage = "{image}"')
        if record.kind not in {"situation", "disaster"}:
            event_from = record.date
            if record.key == "teutoburg":
                # A battle culmination belongs late in the sourced AD 9 window,
                # after campaign conditions can develop; it is never a day-one
                # calendar notification.
                event_from = offset_date(
                    record.date,
                    (days_between(record.date, record.end_date) * 3) // 5,
                )
            lines.extend((
                "\tdynamic_historical_event = {",
                f"\t\ttag = {record.engine_tag}",
                f"\t\tfrom = {event_from.engine()}",
                f"\t\tto = {record.end_date.engine()}",
                "\t\tmonthly_chance = 100",
                "\t}",
            ))
        if record.key == "teutoburg":
            lines.extend((
                "\ttrigger = {",
                "\t\tantq_teutoburg_campaign_ready_trigger = yes",
                "\t\tNOT = { has_variable = antq_teutoburg_battle_resolved }",
                "\t}",
                "\timmediate = {",
                *teutoburg_opponent_capture_lines(indent="\t\t"),
                "\t\tset_variable = antq_teutoburg_battle_resolved",
                "\t\tif = { limit = { has_variable = antq_teutoburg_chain_active } remove_variable = antq_teutoburg_chain_active }",
                "\t\tif = {",
                "\t\t\tlimit = { has_variable = antq_teutoburg_varus }",
                "\t\t\tvar:antq_teutoburg_varus = {",
                f"\t\t\t\tremove_character_modifier = {TEUTOBURG_LIFESPAN_GUARD}",
                "\t\t\t\tsave_scope_as = antq_teutoburg_departing_varus",
                "\t\t\t}",
                "\t\t\tkill_character_silently = scope:antq_teutoburg_departing_varus",
                "\t\t\tremove_variable = antq_teutoburg_varus",
                "\t\t}",
                "\t}",
            ))
        lines.extend((
            "\toption = {",
            f"\t\tname = {record.event_key}.a",
            "\t\thistorical_option = yes",
            *historical_event_choice_lines(record),
            *impact_lines(record),
            *event_effect_lines(record.key),
            *knowledge_response_lines(record.kind, 0),
            "\t}",
            *alternative_event_option_lines(record),
            "}",
            "",
        ))
    teutoburg = next(record for record in records if record.key == "teutoburg")
    policy_from = offset_date(teutoburg.end_date, 1)
    policy_to = offset_date(policy_from, 365)
    lines.extend((
        "# Counterfactual Germania policy; derived from the end of the sourced Teutoburg window.",
        f"{TEUTOBURG_POLICY_EVENT} = {{",
        "\ttype = country_event",
        f"\ttitle = {TEUTOBURG_POLICY_EVENT}.title",
        f"\tdesc = {TEUTOBURG_POLICY_EVENT}.desc",
        "\toutcome = neutral",
        "\tfire_only_once = yes",
        f'\timage = "{EVENT_IMAGES["immensum_bellum"]}"',
        "\tdynamic_historical_event = {",
        f"\t\ttag = {teutoburg.engine_tag}",
        f"\t\tfrom = {policy_from.engine()}",
        f"\t\tto = {policy_to.engine()}",
        "\t\tmonthly_chance = 100",
        "\t}",
        "\ttrigger = {",
        "\t\tNOT = { has_variable = antq_teutoburg_battle_resolved }",
        "\t\tNOT = { has_variable = antq_teutoburg_policy_resolved }",
        "\t}",
        "\timmediate = {",
        "\t\tset_variable = antq_teutoburg_policy_resolved",
        "\t\tif = {",
        "\t\t\tlimit = { has_variable = antq_teutoburg_varus }",
        "\t\t\tvar:antq_teutoburg_varus = {",
        f"\t\t\t\tremove_character_modifier = {TEUTOBURG_LIFESPAN_GUARD}",
        "\t\t\t}",
        "\t\t\tremove_variable = antq_teutoburg_varus",
        "\t\t}",
        "\t}",
        "\toption = {",
        f"\t\tname = {TEUTOBURG_POLICY_EVENT}.a",
        "\t\thistorical_option = yes",
        "\t\tadd_gold = -12",
        "\t\tadd_stability = stability_weak_bonus",
        "\t\tadd_prestige = prestige_weak_penalty",
        "\t\tai_chance = { base = 50 }",
        "\t}",
        "\toption = {",
        f"\t\tname = {TEUTOBURG_POLICY_EVENT}.b",
        "\t\tadd_manpower = { value = monthly_manpower multiply = -1 }",
        "\t\tadd_prestige = prestige_weak_bonus",
        "\t\tai_chance = { base = 30 }",
        "\t}",
        "\toption = {",
        f"\t\tname = {TEUTOBURG_POLICY_EVENT}.c",
        "\t\tadd_gold = -16",
        "\t\tadd_legitimacy = legitimacy_weak_bonus",
        "\t\tai_chance = { base = 20 }",
        "\t}",
        "}",
        "",
    ))
    script = "\n".join(lines)
    validate_ai_chance_syntax(script, source=str(EVENT_OUTPUT.relative_to(ROOT)))
    return script


def teutoburg_trigger_script() -> str:
    """Require a living Roman Varus and a real war against a frontier polity."""
    mapped_tags = engine_tags()
    opponent_tags = tuple(mapped_tags[design_tag] for design_tag in TEUTOBURG_OPPONENTS)
    lines = [
        "# Generated by tools/m10_history.py --write; Round 7 Teutoburg campaign gate.",
        "# Country scope. Territorial ownership and unrelated wars are intentionally insufficient.",
        "antq_teutoburg_campaign_ready_trigger = {",
        "\ttrigger_if = {",
        "\t\tlimit = { has_variable = antq_teutoburg_varus }",
        "\t\tvar:antq_teutoburg_varus = { is_alive = yes }",
        "\t}",
        "\ttrigger_else = { always = no }",
        "\tOR = {",
    ]
    for tag in opponent_tags:
        lines.extend((
            "\t\tAND = {",
            f"\t\t\tcountry_exists = c:{tag}",
            f"\t\t\tis_at_war_with = c:{tag}",
            "\t\t}",
        ))
    lines.extend(("\t}", "}", ""))
    return "\n".join(lines)


def teutoburg_opponent_capture_lines(*, indent: str) -> tuple[str, ...]:
    """Persist the first qualifying opponent for participant-facing consequences."""
    mapped_tags = engine_tags()
    lines: list[str] = []
    for index, design_tag in enumerate(TEUTOBURG_OPPONENTS):
        tag = mapped_tags[design_tag]
        keyword = "if" if index == 0 else "else_if"
        lines.extend((
            f"{indent}{keyword} = {{",
            f"{indent}\tlimit = {{ country_exists = c:{tag} is_at_war_with = c:{tag} }}",
            f"{indent}\tc:{tag} = {{ save_scope_as = antq_teutoburg_selected_opponent }}",
            f"{indent}\tset_variable = {{ name = antq_teutoburg_opponent value = scope:antq_teutoburg_selected_opponent }}",
            f"{indent}}}",
        ))
    return tuple(lines)


def situation_script(records: tuple[Current, ...]) -> str:
    lines = [
        "# Generated by tools/m10_history.py --write; first-century situations.",
        "# These strong historical currents start once within their sourced windows.",
        "",
    ]
    for record in records:
        if record.kind != "situation":
            continue
        lines.extend((
            f"# {record.label}; {record.source}",
            f"{record.script_key} = {{",
            "\tmonthly_spawn_chance = monthly_spawn_chance_unique",
            "\tcontent_trigger = {",
            f"\t\ttag = {record.engine_tag}",
            "\t}",
            "\tcan_start = {",
            f"\t\tcurrent_date >= {record.date.engine()}",
            f"\t\tcurrent_date < {record.end_date.engine()}",
            f"\t\tcountry_exists = c:{record.engine_tag}",
            "\t}",
            *resolution_trigger_lines(record, country_scoped=False),
            "\tvisible = {",
            f"\t\tcountry_exists = c:{record.engine_tag}",
            "\t}",
            *situation_presentation_lines(record.script_key, record.engine_tag),
            *current_lifecycle_lines(record, country_scoped=False),
        ))
        lines.extend(("}", ""))
    return "\n".join(lines)


def disaster_script(records: tuple[Current, ...]) -> str:
    lines = [
        "# Generated by tools/m10_history.py --write; first-century disasters.",
        "# A disaster is rooted in its named recipient country and ends with its window.",
        "",
    ]
    for record in records:
        if record.kind != "disaster":
            continue
        lines.extend((
            f"# {record.label}; {record.source}",
            f"{record.script_key} = {{",
            "\tmonthly_spawn_chance = monthly_spawn_chance_unique",
            "\tcan_start = {",
            f"\t\ttag = {record.engine_tag}",
            f"\t\tcurrent_date >= {record.date.engine()}",
            f"\t\tcurrent_date < {record.end_date.engine()}",
            "\t\thas_any_active_disaster = no",
            "\t}",
            *resolution_trigger_lines(record, country_scoped=True),
            *disaster_modifier_lines(record),
            *current_lifecycle_lines(record, country_scoped=True),
            "}",
            "",
        ))
    return "\n".join(lines)


def localization(records: tuple[Current, ...], language: str) -> str:
    lines = [f"l_{language}:"]
    lines.extend((
        ' KSH: "Kushan"',
        ' KSH_ADJ: "Kushan"',
        ' XNO: "Northern Xiongnu"',
        ' XNO_ADJ: "Northern Xiongnu"',
        ' XSO: "Southern Xiongnu"',
        ' XSO_ADJ: "Southern Xiongnu"',
    ))
    for record in records:
        description = (
            f"{record.summary}. Decisions taken during this current alter its "
            "pace, cost, and eventual resolution."
        )
        lines.extend((
            f' {record.event_key}.title: "{record.label}"',
            f' {record.event_key}.desc: "{description}"',
            f' {record.event_key}.a: "{event_choice_localization(record)[0]}"',
            f' {record.event_key}.b: "{event_choice_localization(record)[1]}"',
            f' {record.event_key}.c: "{event_choice_localization(record)[2]}"',
            f' {record.event_key}.entry: "{record.label}"',
            f' {record.event_key}.entry_short: "{record.label}"',
        ))
        if record.kind in {"situation", "disaster"}:
            lines.extend((
                f' {record.script_key}: "{record.label}"',
                f' {record.script_key}_desc: "{description}"',
            ))
    lines.extend((
        f' {TEUTOBURG_POLICY_EVENT}.title: "The Germania Frontier Policy"',
        f' {TEUTOBURG_POLICY_EVENT}.desc: "No Varian disaster has defined the northern frontier. The court must now decide whether Germania is to be held through a compact Rhine line, continued forward occupation, or negotiated frontier partnerships."',
        f' {TEUTOBURG_POLICY_EVENT}.a: "Consolidate a defensible Rhine command."',
        f' {TEUTOBURG_POLICY_EVENT}.b: "Maintain the forward military districts."',
        f' {TEUTOBURG_POLICY_EVENT}.c: "Build compacts with the frontier peoples."',
        f' {TEUTOBURG_POLICY_EVENT}.entry: "The Germania Frontier Policy"',
        f' {TEUTOBURG_POLICY_EVENT}.entry_short: "Germania Policy"',
    ))
    return "\n".join(lines) + "\n"


def transformation_colors() -> str:
    return "\n".join((
        "# Generated by tools/m10_history.py --write; temporary M10 transformation colors.",
        "colors = {",
        "\tmap_KSH = rgb { 157 102 47 }",
        "\tmap_XNO = rgb { 88 101 126 }",
        "\tmap_XSO = rgb { 96 118 84 }",
        "}",
        "",
    ))


def transformation_coas() -> str:
    return "\n".join((
        "# Generated by tools/m10_history.py --write; M11 non-reconstructive transformation UI standards.",
        "KSH = {",
        "\tpattern = \"pattern_solid.dds\"",
        "\tcolor1 = \"orange\"",
        "\tcolor2 = \"yellow\"",
        "\tcolor3 = \"red\"",
        "\tcolored_emblem = { texture = \"ce_auspicious_conch_shell_simple.dds\" color1 = color2 color2 = color2 color3 = color3 instance = { position = { 0.5 0.5 } scale = { 0.82 0.82 } } }",
        "}",
        "",
        "XSO = {",
        "\tpattern = \"pattern_solid.dds\"",
        "\tcolor1 = \"green\"",
        "\tcolor2 = \"yellow\"",
        "\tcolor3 = \"red\"",
        "\tcolored_emblem = { texture = \"ce_horse_salient.dds\" color1 = color2 color2 = color2 color3 = color3 instance = { position = { 0.5 0.5 } scale = { 0.83 0.83 } } }",
        "}",
        "",
        "XNO = {",
        "\tpattern = \"pattern_solid.dds\"",
        "\tcolor1 = \"blue\"",
        "\tcolor2 = \"yellow\"",
        "\tcolor3 = \"white\"",
        "\tcolored_emblem = { texture = \"ce_horse_salient.dds\" color1 = color2 color2 = color2 color3 = color3 instance = { position = { 0.5 0.5 } scale = { 0.83 0.83 } } }",
        "}",
        "",
    ))


def outputs(records: tuple[Current, ...]) -> dict[Path, str]:
    rendered = {
        EVENT_OUTPUT: event_script(records),
        TEUTOBURG_TRIGGER_OUTPUT: teutoburg_trigger_script(),
        SITUATION_OUTPUT: situation_script(records),
        DISASTER_OUTPUT: disaster_script(records),
        COLOR_OUTPUT: transformation_colors(),
        COA_OUTPUT: transformation_coas(),
    }
    for language in ("english", *M2_MIRROR_LANGUAGES):
        rendered[LOC_ROOT / language / f"antq_m10_first_century_l_{language}.yml"] = localization(records, language)
    return rendered


def write(records: tuple[Current, ...]) -> None:
    for path, content in outputs(records).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        encoding = "utf-8" if path == COA_OUTPUT else "utf-8-sig"
        path.write_text(content, encoding=encoding, newline="\n")
        print(f"m10_history: wrote {path.relative_to(ROOT)}")


def check(records: tuple[Current, ...]) -> bool:
    failures: list[str] = []
    for path, expected in outputs(records).items():
        if not path.is_file():
            failures.append(f"missing {path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8-sig") != expected:
            failures.append(f"stale {path.relative_to(ROOT)}")
    if failures:
        print("m10_history: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return False
    counts = {kind: sum(record.kind == kind for record in records) for kind in ("situation", "disaster", "event", "tagswitch", "formation")}
    print(
        "m10_history: PASS "
        f"({len(records)} first-century currents; {counts['situation']} situations; "
        f"{counts['disaster']} disasters; {counts['event']} events; "
        f"{counts['tagswitch']} tag switch; {counts['formation']} formation)"
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        records = currents()
        validate(records)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"m10_history: FAIL\n  - {exc}")
        return 1
    if args.write:
        write(records)
        return 0
    return 0 if check(records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
