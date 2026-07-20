#!/usr/bin/env python3
"""Render the AD 300-399 M10 historical-current batch.

The fourth century needs two bounded geography adapters.  Hunnic arrival uses
Kazan as the reviewed local-map Volga entry proxy; the 395 Roman split transfers
the active Roman locations in a transparent late-antique regional envelope to a
new Eastern Roman state.  Neither adapter claims that the AD 1 mesh is a full
fourth-century provincial atlas.  The generated ledgers make both choices
reviewable rather than hiding them in event script.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from dates import AntqDate, M2_MIRROR_LANGUAGES, indexed_timeline, load_timeline
from m10_history import engine_tags, start_country_locations

ROOT = Path(__file__).resolve().parents[1]
TIMELINE = ROOT / "docs/timeline.csv"
GEOGRAPHY = ROOT / "docs/vanilla_symbols/geography_hierarchy.json"
EVENT_OUTPUT = ROOT / "in_game/events/antq_m10_fourth_century.txt"
SITUATION_OUTPUT = ROOT / "in_game/common/situations/antq_m10_fourth_century.txt"
DISASTER_OUTPUT = ROOT / "in_game/common/disasters/antq_m10_fourth_century.txt"
LOC_ROOT = ROOT / "main_menu/localization"
COLOR_OUTPUT = ROOT / "main_menu/common/named_colors/antq_m10_fourth_century.txt"
COA_OUTPUT = ROOT / "main_menu/common/coat_of_arms/coat_of_arms/antq_m10_fourth_century.txt"
HUN_LEDGER = ROOT / "docs/m10/hunnic_arrival_seed.csv"
EAST_LEDGER = ROOT / "docs/m10/eastern_roman_395_locations.csv"
BATCH_START = AntqDate.parse("300.1.1")
BATCH_END = AntqDate.parse("400.1.1")
HUNNIC_ENTRY_LOCATION = "kazan"
HUNNIC_TAG = "HNS"
EASTERN_ROMAN_TAG = "ERO"

# The recipients are current anchors, not a claim of exclusive ownership for a
# broad historical process.  SIB and GUT are the closest reviewed AD 1 anchors
# for the Volga and Gothic refugee currents.
TARGETS = {
    "armenia_conversion": "ARM",
    "constantine_civil_wars": "ROM",
    "nicaea": "ROM",
    "shapur_julian": "PAR",
    "aksum_meroë": "AKS",
    "crete_earthquake": "ROM",
    "huns_arrive": "SIB",
    "gothic_refugees": "GUT",
    "thessalonica": "ROM",
    "fei_river": "HAN",
    "gwanggaeto": "GOG",
    "olympic_sunset": "ROM",
    "east_west_division": "ROM",
    "faxian_gupta": "HAN",
}

# Retain event-art links in the generator so regenerated fourth-century scripts
# cannot silently drop a reviewed game-facing texture.
EVENT_IMAGES = {
    "aksum_meroë": "gfx/interface/illustrations/event/antq_aksum_meroe.dds",
    "armenia_conversion": "gfx/interface/illustrations/event/antq_armenia_conversion.dds",
    "constantine_civil_wars": "gfx/interface/illustrations/event/antq_constantine_civil_wars.dds",
    "crete_earthquake": "gfx/interface/illustrations/event/antq_crete_earthquake.dds",
    "east_west_division": "gfx/interface/illustrations/event/antq_east_west_division.dds",
    "faxian_gupta": "gfx/interface/illustrations/event/antq_faxian_gupta.dds",
    "fei_river": "gfx/interface/illustrations/event/antq_fei_river.dds",
    "gothic_refugees": "gfx/interface/illustrations/event/antq_gothic_refugees.dds",
    "gwanggaeto": "gfx/interface/illustrations/event/antq_gwanggaeto.dds",
    "huns_arrive": "gfx/interface/illustrations/event/antq_huns_arrive.dds",
    "nicaea": "gfx/interface/illustrations/event/antq_nicaea.dds",
    "olympic_sunset": "gfx/interface/illustrations/event/antq_olympic_sunset.dds",
    "shapur_julian": "gfx/interface/illustrations/event/antq_shapur_julian.dds",
    "thessalonica": "gfx/interface/illustrations/event/antq_thessalonica.dds",
}

# A deliberately limited political envelope for the eastern court.  The list
# tracks the active Roman locations within these local-map regions and is not a
# claim that all listed 1337 geography describes the 395 provincial boundary.
EASTERN_ROME_AREAS = (
    "aegean_archipelago_area",
    "albania_area",
    "black_sea_area",
    "bulgaria_area",
    "cappadocia_area",
    "central_anatolia_area",
    "cilicia_area",
    "cyrenaica_area",
    "lower_egypt_area",
    "macedonia_area",
    "marmara_area",
    "morea_area",
    "northern_greece_area",
    "pontus_area",
    "serbia_area",
    "sinai_area",
    "thrace_area",
    "upper_egypt_area",
    "west_anatolia_area",
    "levant_area",
)

COSMETIC_TAGS = {"WRE"}
DYNAMIC_TAGS = {HUNNIC_TAG, EASTERN_ROMAN_TAG}


def script_token(value: str) -> str:
    """Keep display/source keys Unicode while emitting engine-safe identifiers."""
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9_]+", "_", normalized.lower()).strip("_")


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
        return f"antq_m10_fourth_{script_token(self.key)}"

    @property
    def event_key(self) -> str:
        return f"antq_m10_fourth.{self.event_id}"


def currents() -> tuple[Current, ...]:
    mapped_tags = engine_tags()
    result: list[Current] = []
    for row in load_timeline(TIMELINE):
        if row["rails_strength"].strip() == "system":
            continue
        date = AntqDate.parse(row["date"])
        if not BATCH_START <= date < BATCH_END:
            continue
        key = row["key"].strip()
        design_tag = TARGETS.get(key)
        if design_tag is None:
            raise ValueError(f"M10 fourth-century target missing for {key}")
        if design_tag not in mapped_tags:
            raise ValueError(f"M10 target {design_tag} for {key} is absent from tag map")
        end_value = row.get("end_date", "").strip()
        if not end_value:
            raise ValueError(f"M10 fourth-century current {key} needs an end date")
        result.append(Current(
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
            event_id=4000 + len(result),
        ))
    return tuple(result)


def geography() -> dict[str, list[str]]:
    with GEOGRAPHY.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("local geography hierarchy is not an object")
    return data


def descendants(key: str, hierarchy: dict[str, list[str]]) -> set[str]:
    if key not in hierarchy:
        raise ValueError(f"eastern Roman area {key} is absent from local geography")
    result: set[str] = set()
    for child in hierarchy[key]:
        if child in hierarchy:
            result.update(descendants(child, hierarchy))
        else:
            result.add(child)
    return result


def eastern_roman_locations() -> tuple[tuple[str, str], ...]:
    hierarchy = geography()
    active_rome = start_country_locations(engine_tags()["ROM"])
    location_areas: dict[str, str] = {}
    for area in EASTERN_ROME_AREAS:
        for location in descendants(area, hierarchy):
            location_areas.setdefault(location, area)
    return tuple(
        (location, location_areas[location])
        for location in sorted(active_rome & set(location_areas))
    )


def roman_east_ledger(locations: tuple[tuple[str, str], ...]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(("location", "local_map_area", "role", "source"))
    writer.writerow(("constantinople", "thrace_area", "AD 395 Eastern Roman capital formation", "OUP-EW;CAM-DYNASTY; current THR location converted by the strong historical current"))
    for location, area in locations:
        writer.writerow((location, area, "AD 395 Eastern Roman transfer envelope", "OUP-EW;CAM-DYNASTY; local M3 mesh proxy"))
    return stream.getvalue()


def hunnic_ledger() -> str:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(("location", "role", "source", "note"))
    writer.writerow((HUNNIC_ENTRY_LOCATION, "Volga entry proxy", "CAM-HUN;CAM-ATT", "Reviewed M3 Siberian-Societies location; not a claim of an exact Hunnic ethnogenesis site."))
    return stream.getvalue()


def validate(records: tuple[Current, ...]) -> None:
    if not records:
        raise ValueError("M10 fourth-century batch is empty")
    record_keys = {record.key for record in records}
    if set(TARGETS) != record_keys:
        missing = sorted(set(TARGETS) - record_keys)
        extra = sorted(record_keys - set(TARGETS))
        raise ValueError(f"M10 fourth-century ledger/target mismatch: missing={missing}, extra={extra}")
    if len({record.event_id for record in records}) != len(records):
        raise ValueError("M10 fourth-century event IDs must be unique")
    unknown_images = sorted(set(EVENT_IMAGES) - record_keys)
    if unknown_images:
        raise ValueError(f"M10 fourth-century illustration map has no corresponding current: {unknown_images}")
    for image in EVENT_IMAGES.values():
        texture = ROOT / "main_menu" / image
        if not texture.is_file():
            raise ValueError(f"M10 fourth-century event illustration is missing: {texture}")
    mapped_tags = engine_tags()
    collisions = sorted((COSMETIC_TAGS | DYNAMIC_TAGS) & set(mapped_tags.values()))
    if collisions:
        raise ValueError(f"M10 fourth-century generated tag collides with AD 1 runtime tag(s): {collisions}")
    if HUNNIC_ENTRY_LOCATION not in start_country_locations(mapped_tags["SIB"]):
        raise ValueError("Hunnic Volga proxy is not owned by the reviewed AD 1 Siberian anchor")
    eastern_locations = eastern_roman_locations()
    if len(eastern_locations) < 100:
        raise ValueError("Eastern Roman transfer envelope is unexpectedly small")
    thrace_tag = mapped_tags.get("THR")
    if thrace_tag is None or "constantinople" not in start_country_locations(thrace_tag):
        raise ValueError("Eastern Roman capital seed must resolve to the reviewed AD 1 Thracian location")
    for record in records:
        if record.kind not in {"situation", "disaster", "event", "tagswitch", "formation"}:
            raise ValueError(f"unsupported M10 kind for {record.key}: {record.kind}")
        if record.rails != "Strong":
            raise ValueError(f"M10 fourth-century current {record.key} must retain Strong rails")
        if record.end_date <= record.date:
            raise ValueError(f"M10 fourth-century current {record.key} has an invalid window")
        if not record.source or not record.label or not record.summary:
            raise ValueError(f"M10 fourth-century current {record.key} lacks source text")


def event_outcome(record: Current) -> str:
    if record.kind == "disaster":
        return "negative"
    if record.kind in {"formation", "tagswitch"}:
        return "positive"
    return "neutral"


def impact_lines(record: Current, eastern_locations: tuple[tuple[str, str], ...]) -> tuple[str, ...]:
    """Use only effects verified by the local event corpus/script-doc dump."""
    if record.key == "armenia_conversion":
        return (
            "\t\t# IRAN-ARMCONV: 301 is the plan's traditional-current anchor; chronology is contested.",
            "\t\tchange_religion = religion:antq_early_christianity",
            "\t\tadd_prestige = prestige_mild_bonus",
        )
    if record.key == "thessalonica":
        return (
            "\t\tchange_religion = religion:antq_early_christianity",
            "\t\tadd_legitimacy = legitimacy_mild_bonus",
        )
    if record.key == "huns_arrive":
        return (
            "\t\t# CAM-HUN;CAM-ATT; Kazan is the bounded Volga local-mesh entry proxy.",
            f"\t\tlocation:{HUNNIC_ENTRY_LOCATION} = {{",
            "\t\t\tcreate_country_from_location = {",
            f"\t\t\t\tdefine_unique_country_tag = {HUNNIC_TAG}",
            f"\t\t\t\tchange_country_name = {HUNNIC_TAG}",
            f"\t\t\t\tchange_country_adjective = {HUNNIC_TAG}",
            f"\t\t\t\tchange_country_color = map_{HUNNIC_TAG}",
            f"\t\t\t\tchange_country_flag = {HUNNIC_TAG}",
            "\t\t\t\tchange_culture = ROOT.culture",
            "\t\t\t\tchange_religion = ROOT.religion",
            "\t\t\t\tchange_government_type = government_type:steppe_horde",
            "\t\t\t\tadd_reform = government_reform:antq_steppe_confederation",
            "\t\t\t\tchange_heir_selection = heir_selection:tribal_oldest_male",
            "\t\t\t}",
            f"\t\t\tadd_core = c:{HUNNIC_TAG}",
            "\t\t}",
            f"\t\tc:{engine_tags()['ALA']} = {{",
            "\t\t\tadd_stability = stability_mild_penalty",
            "\t\t\tadd_prestige = prestige_mild_penalty",
            "\t\t}",
            "\t\tadd_prestige = prestige_mild_bonus",
        )
    if record.key == "olympic_sunset":
        return (
            "\t\tdestroy_international_organization = { target = international_organization:antq_panhellenic_games }",
            "\t\tadd_legitimacy = legitimacy_mild_bonus",
        )
    if record.key == "east_west_division":
        locations = tuple(location for location, _ in eastern_locations)
        lines = [
            "\t\t# OUP-EW;CAM-DYNASTY; bounded regional envelope documented in docs/m10/.",
            "\t\tchange_tag_cosmetic = { tag = WRE }",
            "\t\tlocation:constantinople = {",
            "\t\t\tcreate_country_from_location = {",
            f"\t\t\t\tdefine_unique_country_tag = {EASTERN_ROMAN_TAG}",
            f"\t\t\t\tchange_country_name = {EASTERN_ROMAN_TAG}",
            f"\t\t\t\tchange_country_adjective = {EASTERN_ROMAN_TAG}",
            f"\t\t\t\tchange_country_color = map_{EASTERN_ROMAN_TAG}",
            f"\t\t\t\tchange_country_flag = {EASTERN_ROMAN_TAG}",
            "\t\t\t\tchange_culture = ROOT.culture",
            "\t\t\t\tchange_religion = ROOT.religion",
            "\t\t\t\tchange_government_type = government_type:monarchy",
            "\t\t\t\tadd_reform = government_reform:antq_dominate",
            "\t\t\t\tchange_heir_selection = heir_selection:cognatic_primogeniture",
            "\t\t\t}",
            f"\t\t\tadd_core = c:{EASTERN_ROMAN_TAG}",
            "\t\t}",
            "\t\tevery_owned_location = {",
            "\t\t\tlimit = {",
            "\t\t\t\tOR = {",
        ]
        lines.extend(f"\t\t\t\t\tthis = location:{location}" for location in locations)
        lines.extend((
            "\t\t\t\t}",
            "\t\t\t}",
            f"\t\t\tchange_location_owner = c:{EASTERN_ROMAN_TAG}",
            f"\t\t\tadd_core = c:{EASTERN_ROMAN_TAG}",
            "\t\t}",
            "\t\tadd_prestige = prestige_mild_bonus",
        ))
        return tuple(lines)
    if record.kind == "disaster":
        return ("\t\tadd_stability = stability_mild_penalty", "\t\tadd_prestige = prestige_mild_penalty")
    if record.kind == "situation":
        return ("\t\tadd_stability = stability_weak_penalty",)
    if record.kind in {"formation", "tagswitch"}:
        return ("\t\tadd_prestige = prestige_mild_bonus", "\t\tadd_legitimacy = legitimacy_mild_bonus")
    return ("\t\tadd_prestige = prestige_mild_bonus",)


def event_window(record: Current, dates: dict[str, AntqDate]) -> tuple[AntqDate, AntqDate]:
    # The row begins after Frigidus in 394; the shared age boundary records the
    # actual 395 succession.  Both values come through tools/dates.py.
    if record.key == "east_west_division":
        return dates["age_migrations"], record.end_date
    return record.date, record.end_date


def event_script(records: tuple[Current, ...], eastern_locations: tuple[tuple[str, str], ...]) -> str:
    dates = indexed_timeline(TIMELINE)
    lines = [
        "# Generated by tools/m10_fourth_century.py --write; AD 300-399 historical currents.",
        "# Dates are emitted only from docs/timeline.csv through AntqDate.",
        "namespace = antq_m10_fourth",
        "",
    ]
    for record in records:
        start, end = event_window(record, dates)
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
                f"\t\tfrom = {start.engine()}",
                f"\t\tto = {end.engine()}",
                "\t\tmonthly_chance = 100",
                "\t}",
            ))
        lines.extend((
            "\toption = {",
            f"\t\tname = {record.event_key}.a",
            "\t\thistorical_option = yes",
            *impact_lines(record, eastern_locations),
            "\t}",
            "}",
            "",
        ))
    return "\n".join(lines)


def situation_script(records: tuple[Current, ...]) -> str:
    lines = ["# Generated by tools/m10_fourth_century.py --write; AD 300-399 situations.", ""]
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
    lines = ["# Generated by tools/m10_fourth_century.py --write; AD 300-399 disasters.", ""]
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
    lines = [
        f"l_{language}:",
        ' HNS: "Huns"',
        ' HNS_ADJ: "Hunnic"',
        ' WRE: "Western Roman Empire"',
        ' WRE_ADJ: "Western Roman"',
        ' ERO: "Eastern Roman Empire"',
        ' ERO_ADJ: "Eastern Roman"',
    ]
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


def colors() -> str:
    return "\n".join((
        "# Generated by tools/m10_fourth_century.py --write; temporary fourth-century transformation colors.",
        "colors = {",
        "\tmap_HNS = rgb { 105 80 50 }",
        "\tmap_WRE = rgb { 126 41 43 }",
        "\tmap_ERO = rgb { 88 53 122 }",
        "}",
        "",
    ))


def coas() -> str:
    return "\n".join((
        "# Generated by tools/m10_fourth_century.py --write; M11 replaces these temporary CoAs.",
        "HNS = {",
        "\tpattern = \"pattern_solid.dds\"",
        "\tcolor1 = \"brown\"",
        "\tcolor2 = \"yellow\"",
        "}",
        "",
        "WRE = {",
        "\tpattern = \"pattern_solid.dds\"",
        "\tcolor1 = \"red\"",
        "\tcolor2 = \"yellow\"",
        "}",
        "",
        "ERO = {",
        "\tpattern = \"pattern_solid.dds\"",
        "\tcolor1 = \"purple\"",
        "\tcolor2 = \"yellow\"",
        "}",
        "",
    ))


def outputs(records: tuple[Current, ...]) -> dict[Path, str]:
    eastern_locations = eastern_roman_locations()
    rendered = {
        EVENT_OUTPUT: event_script(records, eastern_locations),
        SITUATION_OUTPUT: situation_script(records),
        DISASTER_OUTPUT: disaster_script(records),
        COLOR_OUTPUT: colors(),
        COA_OUTPUT: coas(),
        HUN_LEDGER: hunnic_ledger(),
        EAST_LEDGER: roman_east_ledger(eastern_locations),
    }
    for language in ("english", *M2_MIRROR_LANGUAGES):
        rendered[LOC_ROOT / language / f"antq_m10_fourth_century_l_{language}.yml"] = localization(records, language)
    return rendered


def write(records: tuple[Current, ...]) -> None:
    for path, content in outputs(records).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        encoding = "utf-8" if path == COA_OUTPUT else "utf-8-sig"
        with path.open("w", encoding=encoding, newline="\n") as handle:
            handle.write(content)
        print(f"m10_fourth_century: wrote {path.relative_to(ROOT)}")


def check(records: tuple[Current, ...]) -> bool:
    failures = [
        f"missing {path.relative_to(ROOT)}" if not path.is_file() else f"stale {path.relative_to(ROOT)}"
        for path, expected in outputs(records).items()
        if not path.is_file() or path.read_text(encoding="utf-8-sig") != expected
    ]
    if failures:
        print("m10_fourth_century: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return False
    counts = {kind: sum(record.kind == kind for record in records) for kind in ("situation", "disaster", "event", "tagswitch", "formation")}
    print(
        "m10_fourth_century: PASS "
        f"({len(records)} currents; {counts['situation']} situations; {counts['disaster']} disasters; "
        f"{counts['event']} events; {counts['tagswitch']} tag switch; {counts['formation']} formations)"
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
        print(f"m10_fourth_century: FAIL\n  - {exc}")
        return 1
    if args.write:
        write(records)
        return 0
    return 0 if check(records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
