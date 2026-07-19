#!/usr/bin/env python3
"""Validate and render the first sourced ANTIQVITAS M6 power foundation."""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path

from dates import AntqDate, BiographyDate, M2_MIRROR_LANGUAGES

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/m6"
TAG_MAP = ROOT / "docs/world_1ad/tag_map.json"
GOVERNMENT_TYPES = ROOT / "docs/vanilla_symbols/government_type.json"
LOC_ROOT = ROOT / "main_menu/localization"
REFORM_OUTPUT = ROOT / "in_game/common/government_reforms/00_antiquitas_m6_core.txt"
TOKEN_RE = re.compile(r"^[a-z][a-z0-9_]*$")
DYN_FIELDS = ("key", "name", "home", "source", "confidence", "note")
CHAR_FIELDS = (
    "key", "design_tag", "name", "female", "culture", "religion", "birth_date",
    "death_date", "birthplace", "dynasty", "adm", "dip", "mil", "estate", "source",
    "confidence", "note",
)
GOV_FIELDS = (
    "design_tag", "government_type", "heir_selection", "ruler", "heir", "consort", "active_regent",
    "regency", "start_regency_date", "end_regency_date", "reform", "source", "confidence", "note",
)


@dataclass(frozen=True)
class PowerData:
    dynasties: tuple[dict[str, str], ...]
    characters: tuple[dict[str, str], ...]
    governments: dict[str, dict[str, str]]
    tags: dict[str, str]


def read_rows(path: Path, fields: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != fields:
            raise ValueError(f"{path.relative_to(ROOT)} header does not match required field order")
        return [{key: (value or "").strip() for key, value in row.items()} for row in reader]


def require_token(value: str, label: str) -> None:
    if not TOKEN_RE.fullmatch(value):
        raise ValueError(f"{label} must be a lowercase script token: {value!r}")


def load_power_data() -> PowerData:
    dynasties = read_rows(DATA / "dynasties.csv", DYN_FIELDS)
    characters = read_rows(DATA / "characters.csv", CHAR_FIELDS)
    governments_rows = read_rows(DATA / "governments.csv", GOV_FIELDS)
    tags = {entry["design_tag"]: entry["engine_tag"] for entry in json.loads(TAG_MAP.read_text(encoding="utf-8"))["entries"]}
    locations = set(json.loads((ROOT / "docs/vanilla_symbols/locations.json").read_text(encoding="utf-8-sig")))
    government_types = set(json.loads(GOVERNMENT_TYPES.read_text(encoding="utf-8-sig")))
    failures: list[str] = []
    dynasty_keys: set[str] = set()
    for row in dynasties:
        if any(not row[field] for field in DYN_FIELDS):
            failures.append("dynasties.csv contains a blank required field")
            continue
        try:
            require_token(row["key"], "dynasty key")
        except ValueError as exc:
            failures.append(str(exc))
        if row["key"] in dynasty_keys:
            failures.append(f"duplicate dynasty key: {row['key']}")
        dynasty_keys.add(row["key"])
        if row["home"] not in locations:
            failures.append(f"dynasty {row['key']} has unknown home location {row['home']}")
        if row["confidence"] not in {"secure", "contested"}:
            failures.append(f"dynasty {row['key']} has invalid confidence {row['confidence']}")

    character_keys: set[str] = set()
    for row in characters:
        required = ("key", "design_tag", "name", "female", "culture", "religion", "dynasty", "source", "confidence", "note")
        if any(not row[field] for field in required):
            failures.append("characters.csv contains a blank required field")
            continue
        try:
            require_token(row["key"], "character key")
        except ValueError as exc:
            failures.append(str(exc))
        if row["key"] in character_keys:
            failures.append(f"duplicate character key: {row['key']}")
        character_keys.add(row["key"])
        if row["design_tag"] not in tags:
            failures.append(f"character {row['key']} references unknown design tag {row['design_tag']}")
        if row["female"] not in {"yes", "no"}:
            failures.append(f"character {row['key']} has invalid female value {row['female']}")
        if row["dynasty"] not in dynasty_keys:
            failures.append(f"character {row['key']} references unknown dynasty {row['dynasty']}")
        if row["birthplace"] and row["birthplace"] not in locations:
            failures.append(f"character {row['key']} has unknown birthplace {row['birthplace']}")
        if row["confidence"] not in {"secure", "contested"}:
            failures.append(f"character {row['key']} has invalid confidence {row['confidence']}")
        dates: list[BiographyDate] = []
        for field in ("birth_date", "death_date"):
            if not row[field]:
                continue
            try:
                dates.append(BiographyDate.parse(row[field]))
            except ValueError as exc:
                failures.append(f"character {row['key']} invalid {field}: {exc}")
        if len(dates) == 2 and dates[1] <= dates[0]:
            failures.append(f"character {row['key']} dies on or before birth")
        ratings = tuple(row[field] for field in ("adm", "dip", "mil"))
        if any(ratings) and not all(ratings):
            failures.append(f"character {row['key']} must provide all or no ability ratings")
        for rating in ratings:
            if rating and (not rating.isdigit() or not 0 <= int(rating) <= 100):
                failures.append(f"character {row['key']} has invalid ability rating {rating}")

    governments: dict[str, dict[str, str]] = {}
    for row in governments_rows:
        required = ("design_tag", "government_type", "heir_selection", "ruler", "reform", "source", "confidence", "note")
        if any(not row[field] for field in required):
            failures.append("governments.csv contains a blank required field")
            continue
        if row["design_tag"] in governments:
            failures.append(f"duplicate government profile: {row['design_tag']}")
        governments[row["design_tag"]] = row
        if row["design_tag"] not in tags:
            failures.append(f"government references unknown design tag {row['design_tag']}")
        if row["government_type"] not in government_types:
            failures.append(f"government {row['design_tag']} uses unknown type {row['government_type']}")
        for field in ("ruler", "heir", "consort", "active_regent"):
            if row[field] and row[field] not in character_keys:
                failures.append(f"government {row['design_tag']} references unknown {field} {row[field]}")
        if row["ruler"] in character_keys:
            ruler = next(character for character in characters if character["key"] == row["ruler"])
            if ruler["design_tag"] != row["design_tag"]:
                failures.append(f"government {row['design_tag']} ruler belongs to {ruler['design_tag']}")
        terms = tuple(row[field] for field in ("regency", "start_regency_date", "end_regency_date"))
        if any(terms) and not all(terms):
            failures.append(f"government {row['design_tag']} has an incomplete regency")
        if all(terms):
            try:
                start = AntqDate.parse(row["start_regency_date"])
                end = AntqDate.parse(row["end_regency_date"])
                if end <= start:
                    failures.append(f"government {row['design_tag']} regency end is not after start")
            except ValueError as exc:
                failures.append(f"government {row['design_tag']} invalid regency date: {exc}")
        if row["confidence"] not in {"secure", "contested"}:
            failures.append(f"government {row['design_tag']} has invalid confidence {row['confidence']}")

    if failures:
        raise ValueError("\n".join(sorted(set(failures))))
    return PowerData(tuple(dynasties), tuple(characters), governments, tags)


def dynasty_manager(data: PowerData) -> str:
    lines = ["# Generated by tools/m6_power.py --write; sourced M6 core dynasties.", "dynasty_manager = {"]
    for row in data.dynasties:
        lines.extend((
            f"\t{row['key']} = {{",
            f"\t\tname = {{ name = {row['key']} }}",
            f"\t\thome = {row['home']}",
            "\t}",
            "",
        ))
    lines.extend(("}", ""))
    return "\n".join(lines)


def character_manager(data: PowerData) -> str:
    lines = [
        "# Generated by tools/m6_power.py --write; source-labelled M6 core roster.",
        "# Parents precede children whenever future CSV rows add parent references.",
        "character_db = {",
    ]
    for row in data.characters:
        lines.extend((
            f"\t{row['key']} = {{",
            f"\t\tfirst_name = {{ name = {row['key']} }}",
            f"\t\tculture = {row['culture']}",
            f"\t\treligion = {row['religion']}",
        ))
        if row["female"] == "yes":
            lines.append("\t\tfemale = yes")
        if all(row[field] for field in ("adm", "dip", "mil")):
            lines.append(f"\t\tadm = {row['adm']} dip = {row['dip']} mil = {row['mil']}")
        for field in ("birth_date", "death_date"):
            if row[field]:
                lines.append(f"\t\t{field} = {BiographyDate.parse(row[field]).engine()}")
        if row["birthplace"]:
            lines.append(f"\t\tbirth = {row['birthplace']}")
        if row["estate"]:
            lines.append(f"\t\testate = {row['estate']}")
        lines.extend((
            f"\t\tdynasty = {row['dynasty']}",
            f"\t\ttag = {data.tags[row['design_tag']]}",
            "\t}",
            "",
        ))
    lines.extend(("}", ""))
    return "\n".join(lines)


def government_block(row: dict[str, str]) -> list[str]:
    lines = [
        "\t\t\tgovernment = {",
        f"\t\t\t\ttype = {row['government_type']}",
        f"\t\t\t\their_selection = {row['heir_selection']}",
        f"\t\t\t\truler = {row['ruler']}",
    ]
    for field in ("heir", "consort", "active_regent", "regency", "start_regency_date", "end_regency_date"):
        if row[field]:
            lines.append(f"\t\t\t\t{field} = {row[field]}")
    lines.extend((
        "\t\t\t\treforms = {",
        f"\t\t\t\t\t{row['reform']}",
        "\t\t\t\t}",
        "\t\t\t}",
    ))
    return lines


def reforms() -> str:
    return """# Generated by tools/m6_power.py --write; M6 historical government adapters.
# These retain the five locally installed government types and use only local modifier keys.
antq_principate = {
	major = yes
	government = monarchy
	country_modifier = {
		global_crown_estate_power = 0.10
		monthly_towards_centralization = societal_value_monthly_move
	}
	years = 2
}

antq_han_imperial_bureaucracy = {
	major = yes
	government = monarchy
	country_modifier = {
		monthly_towards_centralization = societal_value_monthly_move
		monthly_towards_innovative = societal_value_monthly_move
	}
	years = 2
}

antq_parthian_king_of_kings = {
	major = yes
	government = monarchy
	country_modifier = {
		global_nobles_estate_power = 0.15
		monthly_towards_decentralization = societal_value_monthly_move
	}
	years = 2
}
"""


def localization(data: PowerData, language: str) -> str:
    entries = [(row["key"], row["name"]) for row in data.dynasties]
    entries.extend((row["key"], row["name"]) for row in data.characters)
    entries.extend((
        ("antq_principate", "Principate"),
        ("antq_principate_desc", "A republic-facade monarchy centred on the princeps and his auctoritas."),
        ("antq_han_imperial_bureaucracy", "Han Imperial Bureaucracy"),
        ("antq_han_imperial_bureaucracy_desc", "A palace-centred bureaucracy whose mandate rests on effective and legitimate rule."),
        ("antq_parthian_king_of_kings", "Parthian King of Kings"),
        ("antq_parthian_king_of_kings_desc", "An Arsacid monarchy balancing the royal court with powerful Iranian noble houses."),
    ))
    return "\n".join([f"l_{language}:", *(f' {key}: "{value}"' for key, value in entries), ""])


def outputs(data: PowerData) -> dict[Path, str]:
    result = {REFORM_OUTPUT: reforms()}
    for language in ("english", *M2_MIRROR_LANGUAGES):
        result[LOC_ROOT / language / f"antq_m6_power_l_{language}.yml"] = localization(data, language)
    return result


def write(data: PowerData) -> None:
    for path, content in outputs(data).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8-sig", newline="\n")
        print(f"m6_power: wrote {path.relative_to(ROOT)}")


def check(data: PowerData) -> bool:
    failures = []
    for path, expected in outputs(data).items():
        if not path.is_file():
            failures.append(f"missing {path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8-sig") != expected:
            failures.append(f"stale {path.relative_to(ROOT)}")
    if failures:
        print("m6_power: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return False
    print(f"m6_power: PASS ({len(data.dynasties)} dynasties, {len(data.characters)} characters, {len(data.governments)} governments)")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        data = load_power_data()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"m6_power: FAIL\n  - {exc}")
        return 1
    if args.write:
        write(data)
        return 0
    return 0 if check(data) else 1


if __name__ == "__main__":
    raise SystemExit(main())
