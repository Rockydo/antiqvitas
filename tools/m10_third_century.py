#!/usr/bin/env python3
"""Render the AD 200-299 M10 historical-current batch.

The renderer owns the third century's discrete history surface while preserving
the shared timeline as the sole authority for every emitted script date.  Its
three political transformations deliberately use in-place cosmetic identities:
the available AD 1 country mesh is an anchor for a source-bounded historical
current, not a claim of a complete third-century territorial reconstruction.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from dates import AntqDate, M2_MIRROR_LANGUAGES, load_timeline
from m10_history import engine_tags

ROOT = Path(__file__).resolve().parents[1]
TIMELINE = ROOT / "docs/timeline.csv"
EVENT_OUTPUT = ROOT / "in_game/events/antq_m10_third_century.txt"
SITUATION_OUTPUT = ROOT / "in_game/common/situations/antq_m10_third_century.txt"
DISASTER_OUTPUT = ROOT / "in_game/common/disasters/antq_m10_third_century.txt"
LOC_ROOT = ROOT / "main_menu/localization"
COLOR_OUTPUT = ROOT / "main_menu/common/named_colors/antq_m10_third_century.txt"
COA_OUTPUT = ROOT / "main_menu/common/coat_of_arms/coat_of_arms/antq_m10_third_century.txt"
BATCH_START = AntqDate.parse("200.1.1")
BATCH_END = AntqDate.parse("300.1.1")

# Recipients are notification and mechanic anchors, not exclusive historical
# ownership assertions for broad currents.  CHT and GER are the closest
# reviewed AD 1 local-mesh anchors for the two deliberately in-place Germanic
# confederation adapters.
TARGETS = {
    "severus_caledonia": "ROM",
    "constitutio_antoniniana": "ROM",
    "alemanni_formation": "CHT",
    "three_kingdoms": "HAN",
    "sassanid_revolution": "PAR",
    "third_century_crisis": "ROM",
    "manichaeism_foundation": "PAR",
    "frankish_formation": "GER",
    "diocletian_dominate": "ROM",
    "eight_princes": "HAN",
}

# Keep reviewed event-art links in the generator rather than hand-editing the
# rendered script: regeneration preserves every game-facing reference and
# validation proves its texture remains present.
EVENT_IMAGES = {
    "constitutio_antoniniana": "gfx/interface/illustrations/event/antq_constitutio_antoniniana.dds",
    "severus_caledonia": "gfx/interface/illustrations/event/antq_severus_caledonia.dds",
}

# These are visual country identities, intentionally not runtime country tags.
COSMETIC_TAGS = {"ALM", "SAS", "FRK"}


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
        return f"antq_m10_third_{self.key}"

    @property
    def event_key(self) -> str:
        return f"antq_m10_third.{self.event_id}"


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
            raise ValueError(f"M10 third-century target missing for {key}")
        if design_tag not in mapped_tags:
            raise ValueError(f"M10 target {design_tag} for {key} is absent from tag map")
        end_value = row.get("end_date", "").strip()
        if not end_value:
            raise ValueError(f"M10 third-century current {key} needs an end date")
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
            event_id=3000 + len(result),
        ))
    return tuple(result)


def validate(records: tuple[Current, ...]) -> None:
    if not records:
        raise ValueError("M10 third-century batch is empty")
    record_keys = {record.key for record in records}
    if set(TARGETS) != record_keys:
        missing = sorted(set(TARGETS) - record_keys)
        extra = sorted(record_keys - set(TARGETS))
        raise ValueError(f"M10 third-century ledger/target mismatch: missing={missing}, extra={extra}")
    if len({record.event_id for record in records}) != len(records):
        raise ValueError("M10 third-century event IDs must be unique")
    unknown_images = sorted(set(EVENT_IMAGES) - record_keys)
    if unknown_images:
        raise ValueError(f"M10 third-century illustration map has no corresponding current: {unknown_images}")
    for image in EVENT_IMAGES.values():
        texture = ROOT / "main_menu" / image
        if not texture.is_file():
            raise ValueError(f"M10 third-century event illustration is missing: {texture}")
    mapped_tags = engine_tags()
    collisions = sorted(COSMETIC_TAGS & set(mapped_tags.values()))
    if collisions:
        raise ValueError(f"M10 third-century cosmetic tag collides with AD 1 runtime tag(s): {collisions}")
    for record in records:
        if record.kind not in {"situation", "disaster", "event", "tagswitch", "formation"}:
            raise ValueError(f"unsupported M10 kind for {record.key}: {record.kind}")
        if record.rails != "Strong":
            raise ValueError(f"M10 third-century current {record.key} must retain Strong rails")
        if record.end_date <= record.date:
            raise ValueError(f"M10 third-century current {record.key} has an invalid window")
        if not record.source or not record.label or not record.summary:
            raise ValueError(f"M10 third-century current {record.key} lacks source text")


def event_outcome(record: Current) -> str:
    if record.kind == "disaster":
        return "negative"
    if record.kind in {"formation", "tagswitch"}:
        return "positive"
    return "neutral"


def impact_lines(record: Current) -> tuple[str, ...]:
    """Use only effects verified by the local event corpus/script-doc dump."""
    if record.key == "constitutio_antoniniana":
        return (
            "\t\tremove_policy = policy:antq_peregrini_status",
            "\t\tadd_policy = policy:antq_universal_citizenship",
            "\t\tadd_prestige = prestige_mild_bonus",
        )
    if record.key == "alemanni_formation":
        return (
            "\t\tchange_tag_cosmetic = { tag = ALM }",
            "\t\tadd_prestige = prestige_mild_bonus",
            "\t\tadd_legitimacy = legitimacy_mild_bonus",
        )
    if record.key == "sassanid_revolution":
        return (
            "\t\tchange_tag_cosmetic = { tag = SAS }",
            "\t\tremove_reform = government_reform:antq_parthian_king_of_kings",
            "\t\tadd_reform = government_reform:antq_sassanid_centralized_monarchy",
            "\t\tadd_prestige = prestige_mild_bonus",
            "\t\tadd_legitimacy = legitimacy_mild_bonus",
        )
    if record.key == "frankish_formation":
        return (
            "\t\tchange_tag_cosmetic = { tag = FRK }",
            "\t\tadd_prestige = prestige_mild_bonus",
            "\t\tadd_legitimacy = legitimacy_mild_bonus",
        )
    if record.key == "diocletian_dominate":
        return (
            "\t\tremove_reform = government_reform:antq_principate",
            "\t\tadd_reform = government_reform:antq_dominate",
            "\t\tadd_stability = stability_mild_bonus",
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
        "# Generated by tools/m10_third_century.py --write; AD 200-299 historical currents.",
        "# Dates are emitted only from docs/timeline.csv through AntqDate.",
        "namespace = antq_m10_third",
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
    lines = ["# Generated by tools/m10_third_century.py --write; AD 200-299 situations.", ""]
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
    lines = ["# Generated by tools/m10_third_century.py --write; AD 200-299 disasters.", ""]
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
        ' ALM: "Alemanni"',
        ' ALM_ADJ: "Alemannic"',
        ' SAS: "Sassanid Persia"',
        ' SAS_ADJ: "Sassanid"',
        ' FRK: "Franks"',
        ' FRK_ADJ: "Frankish"',
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
        "# Generated by tools/m10_third_century.py --write; temporary third-century transformation colors.",
        "colors = {",
        "\tmap_ALM = rgb { 73 112 78 }",
        "\tmap_SAS = rgb { 122 32 37 }",
        "\tmap_FRK = rgb { 51 84 125 }",
        "}",
        "",
    ))


def coas() -> str:
    return "\n".join((
        "# Generated by tools/m10_third_century.py --write; M11 replaces these temporary CoAs.",
        "ALM = {",
        "\tpattern = \"pattern_solid.dds\"",
        "\tcolor1 = \"green\"",
        "\tcolor2 = \"white\"",
        "}",
        "",
        "SAS = {",
        "\tpattern = \"pattern_solid.dds\"",
        "\tcolor1 = \"red\"",
        "\tcolor2 = \"yellow\"",
        "}",
        "",
        "FRK = {",
        "\tpattern = \"pattern_solid.dds\"",
        "\tcolor1 = \"blue\"",
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
        rendered[LOC_ROOT / language / f"antq_m10_third_century_l_{language}.yml"] = localization(records, language)
    return rendered


def write(records: tuple[Current, ...]) -> None:
    for path, content in outputs(records).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8" if path == COA_OUTPUT else "utf-8-sig", newline="\n") as handle:
            handle.write(content)
        print(f"m10_third_century: wrote {path.relative_to(ROOT)}")


def check(records: tuple[Current, ...]) -> bool:
    failures = [
        f"missing {path.relative_to(ROOT)}" if not path.is_file() else f"stale {path.relative_to(ROOT)}"
        for path, expected in outputs(records).items()
        if not path.is_file() or path.read_text(encoding="utf-8-sig") != expected
    ]
    if failures:
        print("m10_third_century: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return False
    counts = {kind: sum(record.kind == kind for record in records) for kind in ("situation", "disaster", "event", "tagswitch", "formation")}
    print(
        "m10_third_century: PASS "
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
        print(f"m10_third_century: FAIL\n  - {exc}")
        return 1
    if args.write:
        write(records)
        return 0
    return 0 if check(records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
