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

from dates import AntqDate, M2_MIRROR_LANGUAGES, load_timeline

ROOT = Path(__file__).resolve().parents[1]
TIMELINE = ROOT / "docs/timeline.csv"
TAG_MAP = ROOT / "docs/world_1ad/tag_map.json"
EVENT_OUTPUT = ROOT / "in_game/events/antq_m10_first_century.txt"
SITUATION_OUTPUT = ROOT / "in_game/common/situations/antq_m10_first_century.txt"
DISASTER_OUTPUT = ROOT / "in_game/common/disasters/antq_m10_first_century.txt"
LOC_ROOT = ROOT / "main_menu/localization"
COLOR_OUTPUT = ROOT / "main_menu/common/named_colors/antq_m10_transformations.txt"
COA_OUTPUT = ROOT / "main_menu/common/coat_of_arms/coat_of_arms/antq_m10_transformations.txt"
NORTH_XIONGNU_SEED = ROOT / "docs/m10/northern_xiongnu_48_locations.csv"
START_COUNTRIES = ROOT / "main_menu/setup/start/10_countries.txt"
LOCATION_COORDINATES = ROOT / "docs/vanilla_symbols/location_coordinates.json"
BATCH_END = AntqDate.parse("96.1.1")
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
    if record.key == "second_temple_destruction":
        return "negative"
    if record.kind == "disaster":
        return "negative"
    if record.kind in {"formation", "tagswitch"}:
        return "positive"
    return "neutral"


def impact_lines(record: Current) -> tuple[str, ...]:
    """Use only effects harvested from installed country-event files."""
    if record.key == "second_temple_destruction":
        return (
            "\t\tlocation:jerusalem = {",
            "\t\t\tif = {",
            "\t\t\t\tlimit = { has_building_with_at_least_one_level = temple }",
            '\t\t\t\tdestroy_building = "building(building_type:temple|owner)"',
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
            "\t\tdestroy_international_organization = { target = international_organization:antq_xiongnu_confederation }",
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
            lines.extend((
                "\tdynamic_historical_event = {",
                f"\t\ttag = {record.engine_tag}",
                f"\t\tfrom = {record.date.engine()}",
                f"\t\tto = {record.end_date.engine()}",
                "\t\tmonthly_chance = 100",
                "\t}",
            ))
        lines.extend((
            "\toption = {",
            f"\t\tname = {record.event_key}.a",
            "\t\thistorical_option = yes",
            *impact_lines(record),
            "\t}",
            "}",
            "",
        ))
    return "\n".join(lines)


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
            "\tcan_end = {",
            f"\t\tcurrent_date >= {record.end_date.engine()}",
            "\t}",
            "\tvisible = {",
            f"\t\tcountry_exists = c:{record.engine_tag}",
            "\t}",
            "\ton_start = {",
            f"\t\tc:{record.engine_tag} = {{ trigger_event_non_silently = {record.event_key} }}",
            "\t}",
            "}",
            "",
        ))
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
            "\tcan_end = {",
            f"\t\tcurrent_date >= {record.end_date.engine()}",
            "\t}",
            "\ton_start = {",
            f"\t\ttrigger_event_non_silently = {record.event_key}",
            "\t}",
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
        description = f"{record.summary} This historical current follows the {record.rails.lower()} setting."
        lines.extend((
            f' {record.event_key}.title: "{record.label}"',
            f' {record.event_key}.desc: "{description}"',
            f' {record.event_key}.a: "Meet the historical current."',
            f' {record.event_key}.entry: "{record.label}"',
            f' {record.event_key}.entry_short: "{record.label}"',
        ))
        if record.kind in {"situation", "disaster"}:
            lines.extend((
                f' {record.script_key}: "{record.label}"',
                f' {record.script_key}_desc: "{description}"',
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
