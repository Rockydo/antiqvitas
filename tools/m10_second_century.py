#!/usr/bin/env python3
"""Render the AD 97-199 M10 historical-current batch.

The shared timeline remains the only source of emitted game dates.  This batch
keeps the existing situation/disaster manager contract and adds the first
source-led Southeast-Asian dynamic formation: Linyi/Champa in AD 192.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from dates import AntqDate, M2_MIRROR_LANGUAGES, load_timeline
from m10_history import engine_tags, start_country_locations

ROOT = Path(__file__).resolve().parents[1]
TIMELINE = ROOT / "docs/timeline.csv"
TAG_MAP = ROOT / "docs/world_1ad/tag_map.json"
EVENT_OUTPUT = ROOT / "in_game/events/antq_m10_second_century.txt"
SITUATION_OUTPUT = ROOT / "in_game/common/situations/antq_m10_second_century.txt"
DISASTER_OUTPUT = ROOT / "in_game/common/disasters/antq_m10_second_century.txt"
LOC_ROOT = ROOT / "main_menu/localization"
COLOR_OUTPUT = ROOT / "main_menu/common/named_colors/antq_m10_second_century.txt"
COA_OUTPUT = ROOT / "main_menu/common/coat_of_arms/coat_of_arms/antq_m10_second_century.txt"
BATCH_START = AntqDate.parse("97.1.1")
BATCH_END = AntqDate.parse("200.1.1")
CHAMPA_TAG = "CPC"
CHAMPA_LOCATIONS = ("amarendrapura", "phon_nha", "visnupura", "vrddha_ratnapura")

# The recipient is the game-facing anchor.  It is not an exclusive historical
# ownership assertion for currents spanning more than one polity.
TARGETS = {
    "gan_ying": "HAN",
    "trajan_dacia": "ROM",
    "cai_lun_paper": "HAN",
    "trajan_parthia": "ROM",
    "antioch_earthquake": "ROM",
    "hadrians_wall": "ROM",
    "kanishka_apogee": "YUE",
    "bar_kokhba": "JUD",
    "antonine_wall": "ROM",
    "celestial_masters": "HAN",
    "gothic_migration": "GUT",
    "verus_parthia": "ROM",
    "antonine_plague": "ROM",
    "daqin_embassy": "HAN",
    "marcomannic_wars": "ROM",
    "yellow_turbans": "HAN",
    "champa_formation": "HAN",
    "five_emperors": "ROM",
}

# Keep reviewed event-art links in the generator rather than hand-editing the
# rendered script: regeneration then preserves every game-facing reference and
# validation proves its texture remains present.
EVENT_IMAGES = {
    "antioch_earthquake": "gfx/interface/illustrations/event/antq_antioch_earthquake.dds",
    "cai_lun_paper": "gfx/interface/illustrations/event/antq_cai_lun_paper.dds",
    "gan_ying": "gfx/interface/illustrations/event/antq_gan_ying.dds",
    "hadrians_wall": "gfx/interface/illustrations/event/antq_hadrians_wall.dds",
    "trajan_dacia": "gfx/interface/illustrations/event/antq_trajan_dacia.dds",
    "trajan_parthia": "gfx/interface/illustrations/event/antq_trajan_parthia.dds",
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
        return f"antq_m10_second_{self.key}"

    @property
    def event_key(self) -> str:
        return f"antq_m10_second.{self.event_id}"


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
            raise ValueError(f"M10 second-century target missing for {key}")
        if design_tag not in mapped_tags:
            raise ValueError(f"M10 target {design_tag} for {key} is absent from tag map")
        end_value = row.get("end_date", "").strip()
        if not end_value:
            raise ValueError(f"M10 second-century current {key} needs an end date")
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
            event_id=2000 + len(result),
        ))
    return tuple(result)


def validate(records: tuple[Current, ...]) -> None:
    if not records:
        raise ValueError("M10 second-century batch is empty")
    if set(TARGETS) != {record.key for record in records}:
        missing = sorted(set(TARGETS) - {record.key for record in records})
        extra = sorted({record.key for record in records} - set(TARGETS))
        raise ValueError(f"M10 second-century ledger/target mismatch: missing={missing}, extra={extra}")
    if len({record.event_id for record in records}) != len(records):
        raise ValueError("M10 second-century event IDs must be unique")
    unknown_images = sorted(set(EVENT_IMAGES) - {record.key for record in records})
    if unknown_images:
        raise ValueError(f"M10 second-century illustration map has no corresponding current: {unknown_images}")
    for image in EVENT_IMAGES.values():
        texture = ROOT / "main_menu" / image
        if not texture.is_file():
            raise ValueError(f"M10 second-century event illustration is missing: {texture}")
    mapped_tags = engine_tags()
    if CHAMPA_TAG in mapped_tags.values():
        raise ValueError(f"M10 dynamic tag {CHAMPA_TAG} collides with the AD 1 tag map")
    han_locations = start_country_locations(mapped_tags["HAN"])
    missing_rinan = sorted(set(CHAMPA_LOCATIONS) - han_locations)
    if missing_rinan:
        raise ValueError(f"M10 Champa seed is not Han-controlled at AD 1: {missing_rinan}")
    for record in records:
        if record.kind not in {"situation", "disaster", "event", "tagswitch", "formation"}:
            raise ValueError(f"unsupported M10 kind for {record.key}: {record.kind}")
        if record.rails != "Strong":
            raise ValueError(f"M10 second-century current {record.key} must retain Strong rails")
        if record.end_date <= record.date:
            raise ValueError(f"M10 second-century current {record.key} has an invalid window")
        if not record.source or not record.label or not record.summary:
            raise ValueError(f"M10 second-century current {record.key} lacks source text")


def event_outcome(record: Current) -> str:
    if record.kind == "disaster":
        return "negative"
    if record.kind in {"formation", "tagswitch"}:
        return "positive"
    return "neutral"


def champa_formation_lines() -> tuple[str, ...]:
    capital, *territory = CHAMPA_LOCATIONS
    lines = [
        "\t\t# CHAM-BIRTH; Linyi/Rinan local-mesh proxy, documented in docs/ASSUMPTIONS.md.",
        f"\t\tlocation:{capital} = {{",
        "\t\t\tcreate_country_from_location = {",
        f"\t\t\t\tdefine_unique_country_tag = {CHAMPA_TAG}",
        f"\t\t\t\tchange_country_name = {CHAMPA_TAG}",
        f"\t\t\t\tchange_country_adjective = {CHAMPA_TAG}",
        f"\t\t\t\tchange_country_color = map_{CHAMPA_TAG}",
        f"\t\t\t\tchange_country_flag = {CHAMPA_TAG}",
        "\t\t\t\tchange_culture = culture:antq_austronesian",
        "\t\t\t\tchange_religion = religion:antq_austronesian_religion",
        "\t\t\t\tchange_government_type = government_type:monarchy",
        "\t\t\t\tadd_reform = government_reform:antq_regional_kingship",
        "\t\t\t\tchange_heir_selection = heir_selection:cognatic_primogeniture",
        "\t\t\t}",
        f"\t\t\tadd_core = c:{CHAMPA_TAG}",
        "\t\t}",
        "\t\tevery_owned_location = {",
        "\t\t\tlimit = {",
        "\t\t\t\tOR = {",
    ]
    lines.extend(f"\t\t\t\t\tthis = location:{location}" for location in territory)
    lines.extend((
        "\t\t\t\t}",
        "\t\t\t}",
        f"\t\t\tchange_location_owner = c:{CHAMPA_TAG}",
        f"\t\t\tadd_core = c:{CHAMPA_TAG}",
        "\t\t}",
        "\t\tadd_prestige = prestige_mild_bonus",
    ))
    return tuple(lines)


def impact_lines(record: Current) -> tuple[str, ...]:
    if record.key == "champa_formation":
        return champa_formation_lines()
    if record.key == "antonine_plague":
        han = engine_tags()["HAN"]
        return (
            "\t\tadd_stability = stability_mild_penalty",
            "\t\tadd_prestige = prestige_mild_penalty",
            f"\t\tc:{han} = {{",
            "\t\t\tadd_stability = stability_weak_penalty",
            "\t\t\tadd_prestige = prestige_weak_penalty",
            "\t\t}",
        )
    if record.kind == "disaster":
        return ("\t\tadd_stability = stability_mild_penalty", "\t\tadd_prestige = prestige_mild_penalty")
    if record.kind == "situation":
        return ("\t\tadd_stability = stability_weak_penalty",)
    if record.kind in {"formation", "tagswitch"}:
        return ("\t\tadd_prestige = prestige_mild_bonus", "\t\tadd_legitimacy = legitimacy_mild_bonus")
    return ("\t\tadd_prestige = prestige_mild_bonus",)


def event_script(records: tuple[Current, ...]) -> str:
    lines = [
        "# Generated by tools/m10_second_century.py --write; AD 97-199 historical currents.",
        "# Dates are emitted only from docs/timeline.csv through AntqDate.",
        "namespace = antq_m10_second",
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
    lines = ["# Generated by tools/m10_second_century.py --write; AD 97-199 situations.", ""]
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
    lines = ["# Generated by tools/m10_second_century.py --write; AD 97-199 disasters.", ""]
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
    lines = [f"l_{language}:", ' CPC: "Champa"', ' CPC_ADJ: "Champa"']
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
        "# Generated by tools/m10_second_century.py --write; temporary Champa color.",
        "colors = {",
        "\tmap_CPC = rgb { 175 103 48 }",
        "}",
        "",
    ))


def coas() -> str:
    return "\n".join((
        "# Generated by tools/m10_second_century.py --write; M11 replaces this temporary CoA.",
        "CPC = {",
        "\tpattern = \"pattern_solid.dds\"",
        "\tcolor1 = \"orange\"",
        "\tcolor2 = \"yellow\"",
        "}",
        "",
    ))


def outputs(records: tuple[Current, ...]) -> dict[Path, str]:
    rendered = {
        EVENT_OUTPUT: event_script(records),
        SITUATION_OUTPUT: situation_script(records),
        DISASTER_OUTPUT: disaster_script(records),
        COLOR_OUTPUT: colors(),
        COA_OUTPUT: coas(),
    }
    for language in ("english", *M2_MIRROR_LANGUAGES):
        rendered[LOC_ROOT / language / f"antq_m10_second_century_l_{language}.yml"] = localization(records, language)
    return rendered


def write(records: tuple[Current, ...]) -> None:
    for path, content in outputs(records).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8" if path == COA_OUTPUT else "utf-8-sig", newline="\n") as handle:
            handle.write(content)
        print(f"m10_second_century: wrote {path.relative_to(ROOT)}")


def check(records: tuple[Current, ...]) -> bool:
    failures = [
        f"missing {path.relative_to(ROOT)}" if not path.is_file() else f"stale {path.relative_to(ROOT)}"
        for path, expected in outputs(records).items()
        if not path.is_file() or path.read_text(encoding="utf-8-sig") != expected
    ]
    if failures:
        print("m10_second_century: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return False
    counts = {kind: sum(record.kind == kind for record in records) for kind in ("situation", "disaster", "event", "tagswitch", "formation")}
    print(
        "m10_second_century: PASS "
        f"({len(records)} currents; {counts['situation']} situations; {counts['disaster']} disasters; "
        f"{counts['event']} events; {counts['formation']} formation)"
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
        print(f"m10_second_century: FAIL\n  - {exc}")
        return 1
    if args.write:
        write(records)
        return 0
    return 0 if check(records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
