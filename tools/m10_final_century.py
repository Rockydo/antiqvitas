#!/usr/bin/env python3
"""Render AD 400-476 historical currents from the shared chronology ledger."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from dates import AntqDate, M2_MIRROR_LANGUAGES, indexed_timeline, load_timeline
from m10_fourth_century import script_token
from m10_history import engine_tags, start_country_locations

ROOT = Path(__file__).resolve().parents[1]
TIMELINE = ROOT / "docs/timeline.csv"
EVENTS = ROOT / "in_game/events/antq_m10_final_century.txt"
SITUATIONS = ROOT / "in_game/common/situations/antq_m10_final_century.txt"
DISASTERS = ROOT / "in_game/common/disasters/antq_m10_final_century.txt"
LOC = ROOT / "main_menu/localization"
COLORS = ROOT / "main_menu/common/named_colors/antq_m10_final_century.txt"
COAS = ROOT / "main_menu/common/coat_of_arms/coat_of_arms/antq_m10_final_century.txt"
BATCH_START = AntqDate.parse("400.1.1")
BATCH_END = AntqDate.parse("476.9.4")

# XAA remains the WRE's runtime identity after the 395 cosmetic transition.
# HNS and ERO are the dynamic identities created by the fourth-century layer.
TARGETS = {
    "radagaisus_rhine": "ROM",
    "britain_abandoned": "ROM",
    "alaric_sack": "ROM",
    "visigoth_settlement": "ROM",
    "vandal_africa": "ROM",
    "attila": "HNS",
    "hephthalites": "PAR",
    "constantinople_earthquake": "ERO",
    "adventus_saxonum": "ROM",
    "chalcedon_avarayr": "ARM",
    "vandal_sack_rome": "VND",
    "cape_bon": "ERO",
    "odoacer_finale": "ROM",
}
# Retain reviewed M11 event-image links in the generator so regenerated scripts
# cannot silently drop a game-facing texture.
EVENT_IMAGES = {
    "alaric_sack": "gfx/interface/illustrations/event/antq_alaric_sack.dds",
    "adventus_saxonum": "gfx/interface/illustrations/event/antq_adventus_saxonum.dds",
    "attila": "gfx/interface/illustrations/event/antq_attila.dds",
    "britain_abandoned": "gfx/interface/illustrations/event/antq_britain_abandoned.dds",
    "constantinople_earthquake": "gfx/interface/illustrations/event/antq_constantinople_earthquake.dds",
    "hephthalites": "gfx/interface/illustrations/event/antq_hephthalites.dds",
    "radagaisus_rhine": "gfx/interface/illustrations/event/antq_radagaisus_rhine.dds",
    "vandal_africa": "gfx/interface/illustrations/event/antq_vandal_africa.dds",
    "visigoth_settlement": "gfx/interface/illustrations/event/antq_visigoth_settlement.dds",
}
DYNAMIC_TARGETS = {"HNS", "ERO", "VND"}
GENERATED_TAGS = {"VSG", "VND", "ODO"}
VISIGOTH_LOCATIONS = (
    "toulouse", "castelnaudary", "lavaur", "verdun_sur_garonne",
    "villemur", "bordeaux", "libourne",
)
VANDAL_LOCATIONS = ("tunis", "nabeul", "hammamet", "el_fahs", "zaghouan")


@dataclass(frozen=True)
class Current:
    key: str
    kind: str
    date: AntqDate
    end_date: AntqDate | None
    summary: str
    source: str
    label: str
    engine_tag: str
    event_id: int

    @property
    def event_key(self) -> str:
        return f"antq_m10_final.{self.event_id}"

    @property
    def script_key(self) -> str:
        return f"antq_m10_final_{script_token(self.key)}"


def currents() -> tuple[Current, ...]:
    tags = engine_tags()
    result: list[Current] = []
    for row in load_timeline(TIMELINE):
        if row["rails_strength"].strip() == "system":
            continue
        date = AntqDate.parse(row["date"])
        if not BATCH_START <= date <= BATCH_END:
            continue
        key = row["key"].strip()
        target = TARGETS.get(key)
        if target is None:
            raise ValueError(f"final-century target missing for {key}")
        if target not in DYNAMIC_TARGETS and target not in tags:
            raise ValueError(f"final-century target {target} missing from tag map")
        end_value = row.get("end_date", "").strip()
        result.append(Current(
            key, row["type"].strip(), date,
            AntqDate.parse(end_value) if end_value else None,
            row["summary"].strip(), row["source"].strip(), row["label"].strip(),
            target if target in DYNAMIC_TARGETS else tags[target], 5000 + len(result),
        ))
    return tuple(result)


def validate(records: tuple[Current, ...]) -> None:
    if {r.key for r in records} != set(TARGETS):
        raise ValueError("final-century ledger does not exactly match the target table")
    if len({r.event_id for r in records}) != len(records):
        raise ValueError("final-century event IDs are not unique")
    unknown_images = sorted(set(EVENT_IMAGES) - {r.key for r in records})
    if unknown_images:
        raise ValueError(f"final-century illustration map has no corresponding current: {unknown_images}")
    for image in EVENT_IMAGES.values():
        texture = ROOT / "main_menu" / image
        if not texture.is_file():
            raise ValueError(f"final-century event illustration is missing: {texture}")
    collisions = GENERATED_TAGS & set(engine_tags().values())
    if collisions:
        raise ValueError(f"generated final-century tag collision: {sorted(collisions)}")
    roman = start_country_locations(engine_tags()["ROM"])
    for location in (*VISIGOTH_LOCATIONS, *VANDAL_LOCATIONS):
        if location not in roman:
            raise ValueError(f"final-century seed {location} is not in the reviewed Roman mesh")
    for record in records:
        if record.kind not in {"situation", "disaster", "event"}:
            raise ValueError(f"unsupported final-century type: {record.key}={record.kind}")
        if not record.source or not record.summary or not record.label:
            raise ValueError(f"incomplete final-century ledger row: {record.key}")
        if record.key != "odoacer_finale" and (record.end_date is None or record.end_date <= record.date):
            raise ValueError(f"invalid final-century window: {record.key}")


def outcome(record: Current) -> str:
    if record.kind == "disaster":
        return "negative"
    return "positive" if record.key in {"visigoth_settlement", "vandal_africa", "odoacer_finale"} else "neutral"


def form_country(tag: str, capital: str, culture: str, religion: str, locations: tuple[str, ...]) -> tuple[str, ...]:
    lines = [
        f"\t\tlocation:{capital} = {{",
        "\t\t\tcreate_country_from_location = {",
        f"\t\t\t\tdefine_unique_country_tag = {tag}",
        f"\t\t\t\tchange_country_name = {tag}",
        f"\t\t\t\tchange_country_adjective = {tag}",
        f"\t\t\t\tchange_country_color = map_{tag}",
        f"\t\t\t\tchange_country_flag = {tag}",
        f"\t\t\t\tchange_culture = culture:{culture}",
        f"\t\t\t\tchange_religion = religion:{religion}",
        "\t\t\t\tchange_government_type = government_type:monarchy",
        "\t\t\t\tadd_reform = government_reform:antq_regional_kingship",
        "\t\t\t\tchange_heir_selection = heir_selection:cognatic_primogeniture",
        "\t\t\t}", f"\t\t\tadd_core = c:{tag}", "\t\t}",
        "\t\tevery_owned_location = {", "\t\t\tlimit = {", "\t\t\t\tOR = {",
    ]
    lines.extend(f"\t\t\t\t\tthis = location:{location}" for location in locations)
    lines.extend((
        "\t\t\t\t}", "\t\t\t}", f"\t\t\tchange_location_owner = c:{tag}",
        f"\t\t\tadd_core = c:{tag}", "\t\t}",
    ))
    return tuple(lines)


def impact(record: Current) -> tuple[str, ...]:
    if record.key == "visigoth_settlement":
        return (
            "\t\t# CAM-GAUL: Aquitanian/Toulouse local-mesh proxy; see ASSUMPTIONS.md.",
            *form_country("VSG", "toulouse", "antq_gothic", "antq_early_christianity", VISIGOTH_LOCATIONS),
            "\t\tadd_stability = stability_mild_penalty",
        )
    if record.key == "vandal_africa":
        return (
            "\t\t# CAM-VANDAL: Tunis is the installed local proxy for Carthage; see ASSUMPTIONS.md.",
            *form_country("VND", "tunis", "antq_vandalic", "antq_early_christianity", VANDAL_LOCATIONS),
            "\t\tadd_stability = stability_mild_penalty",
        )
    if record.key == "odoacer_finale":
        return (
            "\t\t# OUP-ODO: terminal Western-Roman identity adapter; campaign end remains 476.9.4.",
            "\t\tchange_tag_cosmetic = { tag = ODO }",
            "\t\tadd_prestige = prestige_mild_penalty",
        )
    if record.kind == "disaster":
        return ("\t\tadd_stability = stability_mild_penalty", "\t\tadd_prestige = prestige_mild_penalty")
    if record.kind == "situation":
        return ("\t\tadd_stability = stability_weak_penalty",)
    return ("\t\tadd_prestige = prestige_mild_bonus",)


def window(record: Current) -> tuple[AntqDate, AntqDate]:
    if record.key == "odoacer_finale":
        # The campaign terminates on 4 September; this is the latest usable
        # monthly trigger window and the end itself remains owned by dates.py.
        end = indexed_timeline(TIMELINE)["end"]
        return AntqDate(end.year, 1, 1), end
    assert record.end_date is not None
    return record.date, record.end_date


def event_script(records: tuple[Current, ...]) -> str:
    lines = ["# Generated by tools/m10_final_century.py --write; AD 400-476 currents.", "namespace = antq_m10_final", ""]
    for record in records:
        start, end = window(record)
        lines.extend((
            f"# {record.label}; {record.source}; recipient={record.engine_tag}", f"{record.event_key} = {{",
            "\ttype = country_event", f"\ttitle = {record.event_key}.title", f"\tdesc = {record.event_key}.desc",
            f"\toutcome = {outcome(record)}", "\tfire_only_once = yes",
        ))
        image = EVENT_IMAGES.get(record.key)
        if image is not None:
            lines.append(f'\timage = "{image}"')
        if record.kind not in {"situation", "disaster"}:
            lines.extend(("\tdynamic_historical_event = {", f"\t\ttag = {record.engine_tag}", f"\t\tfrom = {start.engine()}", f"\t\tto = {end.engine()}", "\t\tmonthly_chance = 100", "\t}"))
        lines.extend(("\toption = {", f"\t\tname = {record.event_key}.a", "\t\thistorical_option = yes", *impact(record), "\t}", "}", ""))
    return "\n".join(lines)


def manager_script(records: tuple[Current, ...], kind: str) -> str:
    lines = [f"# Generated by tools/m10_final_century.py --write; AD 400-476 {kind}s.", ""]
    for record in records:
        if record.kind != kind:
            continue
        _, end = window(record)
        lines.extend((f"{record.script_key} = {{", "\tmonthly_spawn_chance = monthly_spawn_chance_unique"))
        if kind == "situation":
            lines.extend(("\tcontent_trigger = {", f"\t\ttag = {record.engine_tag}", "\t}"))
        lines.extend((
            "\tcan_start = {",
            *( () if kind == "situation" else (f"\t\ttag = {record.engine_tag}",) ),
            f"\t\tcurrent_date >= {record.date.engine()}", f"\t\tcurrent_date < {end.engine()}",
            f"\t\tcountry_exists = c:{record.engine_tag}", "\t}", "\tcan_end = {", f"\t\tcurrent_date >= {end.engine()}", "\t}",
            "\ton_start = {", f"\t\tc:{record.engine_tag} = {{ trigger_event_non_silently = {record.event_key} }}", "\t}", "}", "",
        ))
    return "\n".join(lines)


def localization(records: tuple[Current, ...], language: str) -> str:
    lines = [f"l_{language}:", ' VSG: "Visigoths"', ' VSG_ADJ: "Visigothic"', ' VND: "Vandals"', ' VND_ADJ: "Vandal"', ' ODO: "Kingdom of Italy"', ' ODO_ADJ: "Italian"']
    for record in records:
        description = f"{record.summary} This historical current follows the strong setting."
        lines.extend((f' {record.event_key}.title: "{record.label}"', f' {record.event_key}.desc: "{description}"', f' {record.event_key}.a: "Meet the historical current."', f' {record.event_key}.entry: "{record.label}"', f' {record.event_key}.entry_short: "{record.label}"'))
        if record.kind in {"situation", "disaster"}:
            lines.extend((f' {record.script_key}: "{record.label}"', f' {record.script_key}_desc: "{description}"'))
    return "\n".join(lines) + "\n"


def outputs(records: tuple[Current, ...]) -> dict[Path, str]:
    result = {
        EVENTS: event_script(records), SITUATIONS: manager_script(records, "situation"), DISASTERS: manager_script(records, "disaster"),
        COLORS: "# Generated by tools/m10_final_century.py --write; temporary finale colors.\ncolors = {\n\tmap_VSG = rgb { 62 93 135 }\n\tmap_VND = rgb { 94 72 45 }\n\tmap_ODO = rgb { 85 114 75 }\n}\n",
        COAS: "# Generated by tools/m10_final_century.py --write; M11 replaces these temporary CoAs.\nVSG = { pattern = \"pattern_solid.dds\" color1 = \"blue\" color2 = \"yellow\" }\nVND = { pattern = \"pattern_solid.dds\" color1 = \"brown\" color2 = \"yellow\" }\nODO = { pattern = \"pattern_solid.dds\" color1 = \"green\" color2 = \"white\" }\n",
    }
    for language in ("english", *M2_MIRROR_LANGUAGES):
        result[LOC / language / f"antq_m10_final_century_l_{language}.yml"] = localization(records, language)
    return result


def write(records: tuple[Current, ...]) -> None:
    for path, content in outputs(records).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8" if path == COAS else "utf-8-sig", newline="\n") as handle:
            handle.write(content)
        print(f"m10_final_century: wrote {path.relative_to(ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        records = currents(); validate(records)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"m10_final_century: FAIL\n  - {exc}"); return 1
    if args.write:
        write(records); return 0
    stale = [path for path, expected in outputs(records).items() if not path.is_file() or path.read_text(encoding="utf-8-sig") != expected]
    if stale:
        print("m10_final_century: FAIL\n" + "\n".join(f"  - stale {p.relative_to(ROOT)}" for p in stale)); return 1
    print(f"m10_final_century: PASS ({len(records)} currents)"); return 0


if __name__ == "__main__":
    raise SystemExit(main())
