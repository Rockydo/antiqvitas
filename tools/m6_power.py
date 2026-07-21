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
POLITIES = ROOT / "docs/world_1ad/polities.csv"
GOVERNMENT_TYPES = ROOT / "docs/vanilla_symbols/government_type.json"
LOC_ROOT = ROOT / "main_menu/localization"
REFORM_OUTPUT = ROOT / "in_game/common/government_reforms/00_antiquitas_m6_core.txt"
PRIVILEGE_OUTPUT = ROOT / "in_game/common/estate_privileges/00_antiquitas_m6_core.txt"
LAW_OUTPUT = ROOT / "in_game/common/laws/00_antiquitas_m6_core.txt"
TOKEN_RE = re.compile(r"^[a-z][a-z0-9_]*$")
VALUE_RE = re.compile(r"^(?:-?(?:\d+(?:\.\d+)?|\.\d+)|[a-z][a-z0-9_]*)$")
DYN_FIELDS = ("key", "name", "home", "source", "confidence", "note")
CHAR_FIELDS = (
    "key", "design_tag", "name", "female", "culture", "religion", "birth_date",
    "death_date", "birthplace", "dynasty", "adm", "dip", "mil", "estate", "source",
    "confidence", "note",
)
GOV_FIELDS = (
    "design_tag", "government_type", "heir_selection", "ruler", "heir", "consort", "active_regent",
    "regency", "start_regency_date", "end_regency_date", "reform", "privileges", "laws", "societal_values",
    "source", "confidence", "note",
)
PRIV_FIELDS = ("key", "estate", "name", "description", "modifiers", "source", "confidence", "note")
LAW_FIELDS = (
    "law", "law_category", "law_gov_group", "name", "description", "option", "option_name",
    "option_description", "modifiers", "estate_preferences", "source", "confidence", "note",
)
TERM_FIELDS = (
    "design_tag", "character", "engine_start_date", "engine_end_date", "regnal_number",
    "historical_reign", "source", "confidence", "note",
)
REGNAL_HISTORY_FIELDS = (
    "design_tag", "sequence", "name", "historical_start", "historical_end", "source", "confidence", "note",
)
ROSTER_REPORT = DATA / "ROSTER_COVERAGE.md"
MIN_SOURCED_CHARACTERS = 250
MAX_SOURCED_CHARACTERS = 400
MIN_NAMED_TIER_PROFILES = 32
ANONYMOUS_PROFILE_MARKERS = ("anonymous", "no current individual ruler")
SOCIAL_VALUE_KEYS = frozenset((
    "centralization_vs_decentralization", "traditionalist_vs_innovative", "aristocracy_vs_plutocracy",
    "serfdom_vs_free_subjects", "mercantilism_vs_free_trade", "offensive_vs_defensive", "quality_vs_quantity",
    "capital_economy_vs_traditional_economy", "individualism_vs_communalism", "outward_vs_inward",
))
LAW_CATEGORIES = frozenset(("administrative", "military", "religious", "socioeconomic"))
MODIFIER_KEYS = frozenset((
	"clergy_estate_target_satisfaction", "country_cabinet_efficiency", "global_burghers_estate_power",
	"global_clergy_estate_power", "global_crown_estate_power",
	"copper_impacts_inflation", "copper_used_for_minting", "goods_gold_impacts_inflation",
	"goods_gold_used_for_minting",
    "global_levy_size_modifier", "global_nobles_estate_power", "global_pop_assimilation_speed_modifier",
    "global_pop_food_consumption", "global_tribes_estate_power",
    "burghers_estate_target_satisfaction", "land_morale_modifier", "monthly_towards_aristocracy",
	"minting_income_factor", "minting_inflation_threshold", "monthly_towards_centralization",
	"monthly_towards_decentralization", "nobles_estate_target_satisfaction", "silver_impacts_inflation",
	"silver_used_for_minting", "tribes_estate_target_satisfaction", "slavery_blocked",
	"ban_exports_of_slaves_goods", "ban_imports_of_slaves_goods", "tolerance_heathen",
	"monthly_republican_tradition",
))


@dataclass(frozen=True)
class PowerData:
    dynasties: tuple[dict[str, str], ...]
    characters: tuple[dict[str, str], ...]
    governments: dict[str, dict[str, str]]
    ruler_terms: tuple[dict[str, str], ...]
    regnal_histories: tuple[dict[str, str], ...]
    privileges: tuple[dict[str, str], ...]
    laws: tuple[dict[str, str], ...]
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


def pipe_values(value: str, label: str) -> tuple[str, ...]:
    parts = tuple(value.split("|")) if value else ()
    if not parts or any(not part for part in parts):
        raise ValueError(f"{label} must be a non-empty pipe-delimited list")
    return parts


def assignments(value: str, label: str) -> tuple[tuple[str, str], ...]:
    parsed: list[tuple[str, str]] = []
    for part in pipe_values(value, label):
        if part.count("=") != 1:
            raise ValueError(f"{label} has an invalid assignment {part!r}")
        key, assigned = part.split("=", 1)
        require_token(key, f"{label} modifier")
        if not VALUE_RE.fullmatch(assigned):
            raise ValueError(f"{label} has an unsafe value {assigned!r}")
        parsed.append((key, assigned))
    if len({key for key, _ in parsed}) != len(parsed):
        raise ValueError(f"{label} contains a duplicate key")
    return tuple(parsed)


def has_named_active_head(government: dict[str, str]) -> bool:
    """Recognize both ordinary rulers and the verified Han regency shape."""
    return government["ruler"] != "random" and bool(
        government["ruler"] or (government["regency"] and government["heir"])
    )


def load_power_data() -> PowerData:
    dynasties = read_rows(DATA / "dynasties.csv", DYN_FIELDS)
    characters = read_rows(DATA / "characters.csv", CHAR_FIELDS)
    governments_rows = read_rows(DATA / "governments.csv", GOV_FIELDS)
    ruler_terms = read_rows(DATA / "ruler_terms.csv", TERM_FIELDS)
    regnal_histories = read_rows(DATA / "regnal_histories.csv", REGNAL_HISTORY_FIELDS)
    privileges = read_rows(DATA / "privileges.csv", PRIV_FIELDS)
    laws = read_rows(DATA / "laws.csv", LAW_FIELDS)
    tags = {entry["design_tag"]: entry["engine_tag"] for entry in json.loads(TAG_MAP.read_text(encoding="utf-8"))["entries"]}
    locations = set(json.loads((ROOT / "docs/vanilla_symbols/locations.json").read_text(encoding="utf-8-sig")))
    government_types = set(json.loads(GOVERNMENT_TYPES.read_text(encoding="utf-8-sig")))
    estates = set(json.loads((ROOT / "docs/vanilla_symbols/estate.json").read_text(encoding="utf-8-sig")))
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

    privilege_keys: set[str] = set()
    for row in privileges:
        if any(not row[field] for field in PRIV_FIELDS):
            failures.append("privileges.csv contains a blank required field")
            continue
        try:
            require_token(row["key"], "privilege key")
            parsed_modifiers = assignments(row["modifiers"], f"privilege {row['key']}")
        except ValueError as exc:
            failures.append(str(exc))
            parsed_modifiers = ()
        if row["key"] in privilege_keys:
            failures.append(f"duplicate privilege key: {row['key']}")
        privilege_keys.add(row["key"])
        if row["estate"] not in estates:
            failures.append(f"privilege {row['key']} uses unknown estate {row['estate']}")
        for key, _ in parsed_modifiers:
            if key not in MODIFIER_KEYS:
                failures.append(f"privilege {row['key']} uses unharvested modifier {key}")
        if row["confidence"] not in {"secure", "contested"}:
            failures.append(f"privilege {row['key']} has invalid confidence {row['confidence']}")

    law_keys: set[str] = set()
    law_options: set[tuple[str, str]] = set()
    for row in laws:
        if any(not row[field] for field in LAW_FIELDS):
            failures.append("laws.csv contains a blank required field")
            continue
        try:
            for field in ("law", "law_category", "law_gov_group", "option"):
                require_token(row[field], f"law {row['law']} {field}")
            parsed_modifiers = assignments(row["modifiers"], f"law {row['law']}")
            preferences = pipe_values(row["estate_preferences"], f"law {row['law']} estate preferences")
        except ValueError as exc:
            failures.append(str(exc))
            parsed_modifiers = ()
            preferences = ()
        if row["law"] in law_keys:
            failures.append(f"duplicate law key: {row['law']}")
        law_keys.add(row["law"])
        law_options.add((row["law"], row["option"]))
        if row["law_category"] not in LAW_CATEGORIES:
            failures.append(f"law {row['law']} has unsupported category {row['law_category']}")
        if row["law_gov_group"] not in government_types:
            failures.append(f"law {row['law']} has unknown government group {row['law_gov_group']}")
        for estate in preferences:
            if estate not in estates:
                failures.append(f"law {row['law']} uses unknown estate preference {estate}")
        for key, _ in parsed_modifiers:
            if key not in MODIFIER_KEYS:
                failures.append(f"law {row['law']} uses unharvested modifier {key}")
        if row["confidence"] not in {"secure", "contested"}:
            failures.append(f"law {row['law']} has invalid confidence {row['confidence']}")

    governments: dict[str, dict[str, str]] = {}
    for row in governments_rows:
        required = (
            "design_tag", "government_type", "heir_selection", "reform", "privileges", "laws",
            "societal_values", "source", "confidence", "note",
        )
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
        regency = bool(row["regency"])
        if not row["ruler"] and not (regency and row["heir"]):
            failures.append(
                f"government {row['design_tag']} needs a ruler, or a regency heir"
            )
        if regency and row["ruler"]:
            failures.append(
                f"government {row['design_tag']} must use heir rather than ruler during a regency"
            )
        random_ruler = row["ruler"] == "random"
        if random_ruler and row["government_type"] not in {"monarchy", "republic", "tribe"}:
            failures.append(f"government {row['design_tag']} uses random ruler with an unverified type")
        for field in ("ruler", "heir", "consort", "active_regent"):
            if row[field] and row[field] not in character_keys and not (field == "ruler" and random_ruler):
                failures.append(f"government {row['design_tag']} references unknown {field} {row[field]}")
        government_head = row["heir"] if regency else row["ruler"]
        if government_head in character_keys:
            ruler = next(character for character in characters if character["key"] == government_head)
            if ruler["design_tag"] != row["design_tag"]:
                failures.append(
                    f"government {row['design_tag']} active head belongs to {ruler['design_tag']}"
                )
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
        try:
            assigned_privileges = pipe_values(row["privileges"], f"government {row['design_tag']} privileges")
            assigned_laws = assignments(row["laws"], f"government {row['design_tag']} laws")
            assigned_values = assignments(row["societal_values"], f"government {row['design_tag']} societal values")
        except ValueError as exc:
            failures.append(str(exc))
            assigned_privileges = ()
            assigned_laws = ()
            assigned_values = ()
        for privilege in assigned_privileges:
            if privilege not in privilege_keys:
                failures.append(f"government {row['design_tag']} references unknown privilege {privilege}")
        for law, option in assigned_laws:
            if (law, option) not in law_options:
                failures.append(f"government {row['design_tag']} references unknown law option {law}={option}")
        for key, value in assigned_values:
            if key not in SOCIAL_VALUE_KEYS:
                failures.append(f"government {row['design_tag']} uses unknown societal value {key}")
            if not re.fullmatch(r"-?\d+", value) or not -100 <= int(value) <= 100:
                failures.append(f"government {row['design_tag']} has invalid societal value {key}={value}")

    with POLITIES.open(encoding="utf-8-sig", newline="") as handle:
        tier_tags = {
            row["tag"]
            for row in csv.DictReader(handle)
            if row.get("tier") in {"1", "2"} and row.get("tag")
        }
    for design_tag in sorted(tier_tags - set(governments)):
        failures.append(f"missing M6 government profile for Tier-1/2 tag {design_tag}")
    for design_tag in sorted(set(governments) - tier_tags):
        failures.append(f"M6 government profile is not a Tier-1/2 tag: {design_tag}")
    if not MIN_SOURCED_CHARACTERS <= len(characters) <= MAX_SOURCED_CHARACTERS:
        failures.append(
            f"M6 requires {MIN_SOURCED_CHARACTERS}-{MAX_SOURCED_CHARACTERS} source-led characters; "
            f"found {len(characters)}"
        )
    named_profiles = sum(
        1 for government in governments.values()
        if has_named_active_head(government)
    )
    if named_profiles < MIN_NAMED_TIER_PROFILES:
        failures.append(
            f"M6 requires at least {MIN_NAMED_TIER_PROFILES} Tier-1/2 profiles with a named active head; "
            f"found {named_profiles}"
        )
    for design_tag, government in governments.items():
        if government["ruler"] == "random" and not any(
            marker in government["note"].lower() for marker in ANONYMOUS_PROFILE_MARKERS
        ):
            failures.append(
                f"anonymous M6 profile {design_tag} must state its evidence boundary in the note"
            )

    term_tags: set[str] = set()
    term_pairs: set[tuple[str, str]] = set()
    campaign_start = AntqDate.parse("1.1.1")
    for row in ruler_terms:
        required = ("design_tag", "character", "engine_start_date", "historical_reign", "source", "confidence", "note")
        if any(not row[field] for field in required):
            failures.append("ruler_terms.csv contains a blank required field")
            continue
        if row["design_tag"] not in governments:
            failures.append(f"ruler term references unknown government profile {row['design_tag']}")
        if row["character"] not in character_keys:
            failures.append(f"ruler term references unknown character {row['character']}")
        elif row["design_tag"] in governments and row["character"] != (
            governments[row["design_tag"]]["heir"]
            if governments[row["design_tag"]]["regency"]
            else governments[row["design_tag"]]["ruler"]
        ):
            failures.append(f"ruler term for {row['design_tag']} must use the active government ruler")
        pair = (row["design_tag"], row["character"])
        if pair in term_pairs:
            failures.append(f"duplicate ruler term for {row['design_tag']} / {row['character']}")
        term_pairs.add(pair)
        if row["design_tag"] in term_tags:
            failures.append(f"multiple current ruler terms for {row['design_tag']}")
        term_tags.add(row["design_tag"])
        try:
            start = AntqDate.parse(row["engine_start_date"])
            if start != campaign_start:
                failures.append(f"ruler term for {row['design_tag']} must begin on the campaign start")
            if row["engine_end_date"] and AntqDate.parse(row["engine_end_date"]) <= start:
                failures.append(f"ruler term for {row['design_tag']} ends on or before its start")
        except ValueError as exc:
            failures.append(f"ruler term for {row['design_tag']} has an invalid engine date: {exc}")
        if row["regnal_number"] and (not row["regnal_number"].isdigit() or not 1 <= int(row["regnal_number"]) <= 999):
            failures.append(f"ruler term for {row['design_tag']} has an invalid regnal number")
        if row["confidence"] not in {"secure", "contested"}:
            failures.append(f"ruler term for {row['design_tag']} has invalid confidence {row['confidence']}")
    for design_tag, government in governments.items():
        if (
            government["ruler"] != "random"
            and not government["regency"]
            and design_tag not in term_tags
        ):
            failures.append(f"government {design_tag} has no campaign-valid ruler term")

    history_by_tag: dict[str, list[int]] = {}
    history_pairs: set[tuple[str, int]] = set()
    for row in regnal_histories:
        if any(not row[field] for field in REGNAL_HISTORY_FIELDS):
            failures.append("regnal_histories.csv contains a blank required field")
            continue
        if row["design_tag"] not in tags:
            failures.append(f"regnal history references unknown design tag {row['design_tag']}")
        if not row["sequence"].isdigit() or int(row["sequence"]) < 1:
            failures.append(f"regnal history has invalid sequence {row['sequence']!r}")
            continue
        pair = (row["design_tag"], int(row["sequence"]))
        if pair in history_pairs:
            failures.append(f"duplicate regnal-history sequence for {row['design_tag']}: {row['sequence']}")
        history_pairs.add(pair)
        history_by_tag.setdefault(row["design_tag"], []).append(int(row["sequence"]))
        if row["confidence"] not in {"secure", "contested"}:
            failures.append(f"regnal history for {row['design_tag']} has invalid confidence {row['confidence']}")
    for design_tag in ("ROM", "HAN"):
        sequence = sorted(history_by_tag.get(design_tag, []))
        if not sequence:
            failures.append(f"regnal history is required for {design_tag}")
        elif sequence != list(range(1, len(sequence) + 1)):
            failures.append(f"regnal history for {design_tag} is not a contiguous sequence")

    if failures:
        raise ValueError("\n".join(sorted(set(failures))))
    return PowerData(
        tuple(dynasties), tuple(characters), governments, tuple(ruler_terms), tuple(regnal_histories),
        tuple(privileges), tuple(laws), tags,
    )


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
    ]
    if row["ruler"]:
        lines.append(f"\t\t\t\truler = {row['ruler']}")

    def append_field(field: str) -> None:
        if row[field]:
            value = (
                AntqDate.parse(row[field]).engine()
                if field in {"start_regency_date", "end_regency_date"}
                else row[field]
            )
            lines.append(f"\t\t\t\t{field} = {value}")

    if row["regency"]:
        # Match the installed native regency shape.  The source ledger retains
        # the sitting head, but an open ruler_term at exactly 1.1.1 is rejected
        # by the installed engine as a future term; the heir field supplies the
        # current head for the start state.
        for field in ("regency", "active_regent", "start_regency_date", "end_regency_date", "heir", "consort"):
            append_field(field)
    else:
        for field in ("heir", "consort", "active_regent", "regency", "start_regency_date", "end_regency_date"):
            append_field(field)
    # Native start data represents a current ruler with `ruler`, not an open
    # `ruler_term` at the campaign boundary.  M6 keeps its fully sourced
    # campaign-boundary term ledger for historical audit, but does not emit
    # invalid start-date terms into the live setup manager.
    lines.extend((
        "\t\t\t\treforms = {",
        f"\t\t\t\t\t{row['reform']}",
        "\t\t\t\t}",
    ))
    lines.append("\t\t\t\tprivilege = {")
    lines.extend(f"\t\t\t\t\t{privilege}" for privilege in pipe_values(row["privileges"], "government privileges"))
    lines.append("\t\t\t\t}")
    lines.append("\t\t\t\tlaws = {")
    lines.extend(f"\t\t\t\t\t{law} = {option}" for law, option in assignments(row["laws"], "government laws"))
    lines.append("\t\t\t\t}")
    lines.extend(f"\t\t\t\t{key} = {value}" for key, value in assignments(row["societal_values"], "government societal values"))
    lines.append("\t\t\t}")
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

antq_dominate = {
	major = yes
	government = monarchy
	country_modifier = {
		global_crown_estate_power = 0.15
		monthly_towards_centralization = societal_value_monthly_move
		country_cabinet_efficiency = 0.025
	}
	years = 2
}

antq_han_imperial_bureaucracy = {
	major = yes
	government = monarchy
	country_modifier = {
		monthly_legitimacy = 0.05
		monthly_towards_centralization = societal_value_monthly_move
		monthly_towards_innovative = societal_value_monthly_move
	}
	years = 2
}

antq_lankan_kingdom = {
	major = yes
	government = monarchy
	country_modifier = {
		global_crown_estate_power = 0.05
		country_cabinet_efficiency = 0.025
	}
	years = 2
}

antq_indian_ganasangha = {
	major = yes
	government = republic
	country_modifier = {
		monthly_republican_tradition = 0.05
		global_nobles_estate_power = 0.05
	}
	years = 2
}

antq_indo_scythian_kingship = {
	major = yes
	government = monarchy
	country_modifier = {
		global_nobles_estate_power = 0.05
		land_morale_modifier = 0.025
	}
	years = 2
}

antq_indo_greek_kingship = {
	major = yes
	government = monarchy
	country_modifier = {
		global_burghers_estate_power = 0.05
		country_cabinet_efficiency = 0.025
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

antq_sassanid_centralized_monarchy = {
	major = yes
	government = monarchy
	country_modifier = {
		global_crown_estate_power = 0.15
		monthly_towards_centralization = societal_value_monthly_move
		land_morale_modifier = 0.025
	}
	years = 2
}

antq_client_monarchy = {
	major = yes
	government = monarchy
	country_modifier = {
		global_crown_estate_power = 0.05
		monthly_towards_centralization = societal_value_minor_monthly_move
	}
	years = 2
}

antq_parthian_subkingdom = {
	major = yes
	government = monarchy
	country_modifier = {
		global_nobles_estate_power = 0.10
		monthly_towards_decentralization = societal_value_minor_monthly_move
	}
	years = 2
}

antq_buffer_kingdom = {
	major = yes
	government = monarchy
	country_modifier = {
		global_nobles_estate_power = 0.05
		country_cabinet_efficiency = 0.025
	}
	years = 2
}

antq_kushite_dual_kingship = {
	major = yes
	government = monarchy
	country_modifier = {
		global_crown_estate_power = 0.05
		country_cabinet_efficiency = 0.025
	}
	years = 2
}

antq_steppe_confederation = {
	major = yes
	government = steppe_horde
	country_modifier = {
		global_tribes_estate_power = 0.10
		monthly_towards_decentralization = societal_value_monthly_move
	}
	years = 2
}

antq_early_korean_kingdom = {
	major = yes
	government = monarchy
	country_modifier = {
		global_nobles_estate_power = 0.05
		country_cabinet_efficiency = 0.025
	}
	years = 2
}

antq_regional_kingship = {
	major = yes
	government = monarchy
	country_modifier = {
		global_crown_estate_power = 0.05
		country_cabinet_efficiency = 0.025
	}
	years = 2
}

antq_advanced_chiefdom = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.05
		country_cabinet_efficiency = 0.025
	}
	years = 2
}

antq_settled_town_cluster = {
	major = yes
	government = republic
	country_modifier = {
		global_burghers_estate_power = 0.05
		country_cabinet_efficiency = 0.025
	}
	years = 2
}

antq_tribal_kingdom = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.10
		monthly_towards_decentralization = societal_value_minor_monthly_move
	}
	years = 2
}
"""


def estate_privileges(data: PowerData) -> str:
    lines = ["# Generated by tools/m6_power.py --write; M6 historical estate adapters."]
    for row in data.privileges:
        lines.extend((
            f"{row['key']} = {{",
            f"\testate = {row['estate']}",
            "\tcountry_modifier = {",
        ))
        lines.extend(f"\t\t{key} = {value}" for key, value in assignments(row["modifiers"], f"privilege {row['key']}"))
        lines.extend(("\t}", "}", ""))
    return "\n".join(lines)


def law_definitions(data: PowerData) -> str:
    lines = ["# Generated by tools/m6_power.py --write; M6 historical legal adapters."]
    for row in data.laws:
        lines.extend((
            f"{row['law']} = {{",
            f"\tlaw_category = {row['law_category']}",
            f"\tlaw_gov_group = {row['law_gov_group']}",
            "\tpotential = {",
            f"\t\tgovernment_type = government_type:{row['law_gov_group']}",
            "\t}",
            f"\t{row['option']} = {{",
            "\t\tcountry_modifier = {",
        ))
        lines.extend(f"\t\t\t{key} = {value}" for key, value in assignments(row["modifiers"], f"law {row['law']}"))
        lines.extend(("\t\t}", "\t\tyears = 2", "\t\testate_preferences = {"))
        lines.extend(f"\t\t\t{estate}" for estate in pipe_values(row["estate_preferences"], f"law {row['law']} estate preferences"))
        lines.extend(("\t\t}", "\t}"))
        if row["law"] == "antq_citizenship_law":
            lines.extend((
                "\tantq_universal_citizenship = {",
                "\t\tcountry_modifier = {",
                "\t\t\tglobal_pop_assimilation_speed_modifier = 0.02",
                "\t\t\tmonthly_towards_centralization = societal_value_minor_monthly_move",
                "\t\t}",
                "\t\tyears = 2",
                "\t\testate_preferences = {",
                "\t\t\tburghers_estate",
                "\t\t\tnobles_estate",
                "\t\t}",
                "\t}",
            ))
        lines.extend(("}", ""))
    return "\n".join(lines)


def localization(data: PowerData, language: str) -> str:
    entries = [(row["key"], row["name"]) for row in data.dynasties]
    entries.extend((row["key"], row["name"]) for row in data.characters)
    entries.extend((
        ("antq_principate", "Principate"),
        ("antq_principate_desc", "A republic-facade monarchy centred on the princeps and his auctoritas."),
        ("antq_dominate", "Dominate"),
        ("antq_dominate_desc", "A later Roman monarchy emphasizing central court authority and regional administration."),
        ("antq_han_imperial_bureaucracy", "Han Imperial Bureaucracy"),
        ("antq_han_imperial_bureaucracy_desc", "A palace-centred bureaucracy whose Mandate of Heaven is represented through legitimacy and effective rule."),
        ("antq_lankan_kingdom", "Anuradhapura Kingship"),
        ("antq_lankan_kingdom_desc", "A Lankan royal court whose monastic and irrigation patronage is a central source of authority."),
        ("antq_indian_ganasangha", "Indian Ganasangha"),
        ("antq_indian_ganasangha_desc", "A clan-based republican council represented through the installed republic government type."),
        ("antq_indo_scythian_kingship", "Indo-Scythian Kingship"),
        ("antq_indo_scythian_kingship_desc", "A politically composite northern Indian monarchy supported by regional military elites."),
        ("antq_indo_greek_kingship", "Late Indo-Greek Kingship"),
        ("antq_indo_greek_kingship_desc", "The final eastern-Punjab Indo-Greek court, supported by a compact with its urban elites."),
        ("antq_parthian_king_of_kings", "Parthian King of Kings"),
        ("antq_parthian_king_of_kings_desc", "An Arsacid monarchy balancing the royal court with powerful Iranian noble houses."),
        ("antq_sassanid_centralized_monarchy", "Sassanid Centralized Monarchy"),
        ("antq_sassanid_centralized_monarchy_desc", "A centralized Iranian monarchy that supersedes the Arsacid great-house adapter after the Sassanid revolution."),
        ("antq_client_monarchy", "Client Monarchy"),
        ("antq_client_monarchy_desc", "A local royal court whose position is shaped by imperial patronage."),
        ("antq_parthian_subkingdom", "Parthian Sub-Kingdom"),
        ("antq_parthian_subkingdom_desc", "A regional Iranian court whose authority rests on local elites and an Arsacid-facing political order."),
        ("antq_buffer_kingdom", "Buffer Kingdom"),
        ("antq_buffer_kingdom_desc", "A frontier court balancing local authority against stronger neighbouring powers."),
        ("antq_kushite_dual_kingship", "Kushite Dual Kingship"),
        ("antq_kushite_dual_kingship_desc", "A Kushite royal court represented through the named Natakamani-Amanitore co-rule."),
        ("antq_steppe_confederation", "Steppe Confederation"),
        ("antq_steppe_confederation_desc", "A confederation whose chanyu must balance the leading clans."),
        ("antq_early_korean_kingdom", "Early Korean Kingdom"),
        ("antq_early_korean_kingdom_desc", "A developing royal kingdom supported by leading political houses."),
        ("antq_regional_kingship", "Regional Kingship"),
        ("antq_regional_kingship_desc", "A bounded technical monarchy adapter for an attested regional court without a defensible current ruler."),
        ("antq_advanced_chiefdom", "Advanced Chiefdom"),
        ("antq_advanced_chiefdom_desc", "A developing chiefly polity represented through the installed tribal government type."),
        ("antq_settled_town_cluster", "Settled Town Cluster"),
        ("antq_settled_town_cluster_desc", "A settled urban community represented through a bounded council adapter rather than an invented monarchy."),
        ("antq_tribal_kingdom", "Tribal Kingdom"),
        ("antq_tribal_kingdom_desc", "A kingship sustained and constrained by leading kin groups."),
    ))
    for row in data.privileges:
        entries.extend(((row["key"], row["name"]), (f"{row['key']}_desc", row["description"])))
    for row in data.laws:
        entries.extend(((row["law"], row["name"]), (f"{row['law']}_desc", row["description"])))
        entries.extend(((row["option"], row["option_name"]), (f"{row['option']}_desc", row["option_description"])))
    entries.extend((
        ("antq_universal_citizenship", "Universal Citizenship"),
        ("antq_universal_citizenship_desc", "A legal-status adapter for Caracalla's AD 212 grant of citizenship to free imperial inhabitants."),
    ))
    return "\n".join([f"l_{language}:", *(f' {key}: "{value}"' for key, value in entries), ""])


def outputs(data: PowerData) -> dict[Path, str]:
    result = {REFORM_OUTPUT: reforms(), PRIVILEGE_OUTPUT: estate_privileges(data), LAW_OUTPUT: law_definitions(data)}
    for language in ("english", *M2_MIRROR_LANGUAGES):
        result[LOC_ROOT / language / f"antq_m6_power_l_{language}.yml"] = localization(data, language)
    return result


def roster_coverage(data: PowerData) -> str:
    """Render the auditable boundary between named and anonymous AD 1 profiles."""
    characters_by_tag: dict[str, list[dict[str, str]]] = {}
    for character in data.characters:
        characters_by_tag.setdefault(character["design_tag"], []).append(character)
    named = [
        government for _, government in sorted(data.governments.items())
        if has_named_active_head(government)
    ]
    anonymous = [
        government for _, government in sorted(data.governments.items())
        if government["ruler"] == "random"
    ]
    lines = [
        "# M6 Tier-1/2 roster coverage",
        "",
        "Generated by `tools/m6_power.py --write`; do not hand-edit.",
        "",
        "## Checked coverage",
        "",
        f"- Tier-1/2 government profiles: **{len(data.governments)} / {len(data.governments)}**",
        f"- Source-led character records: **{len(data.characters)}** (plan target: 250--400)",
        f"- Named active-head profiles: **{len(named)}**",
        f"- Evidence-bounded anonymous/collective profiles: **{len(anonymous)}**",
        f"- Dynasties: **{len(data.dynasties)}**; campaign-valid ruler terms: **{len(data.ruler_terms)}**; "
        f"regnal-history rows: **{len(data.regnal_histories)}**",
        "",
        "An anonymous/collective profile is not an omitted polity. It is the deliberate `ruler = random` "
        "engine representation where the project sources establish a polity, confederation, or settlement "
        "form but not a defensible AD 1 incumbent. No generic person is entered into `character_db` to "
        "simulate missing evidence. Its individual source and limitation are in `governments.csv`.",
        "",
        "## Profiles with named active heads",
        "",
        "| Tag | Active head | Source-led character records |",
        "| --- | --- | ---: |",
    ]
    for government in named:
        active_head = government["heir"] if government["regency"] else government["ruler"]
        lines.append(
            f"| {government['design_tag']} | `{active_head}` | "
            f"{len(characters_by_tag.get(government['design_tag'], []))} |"
        )
    lines.extend((
        "",
        "## Evidence-bounded anonymous or collective profiles",
        "",
        "| Tag | Government adapter | Source route |",
        "| --- | --- | --- |",
    ))
    for government in anonymous:
        lines.append(
            f"| {government['design_tag']} | `{government['reform']}` | {government['source']} |"
        )
    lines.append("")
    return "\n".join(lines)


def write(data: PowerData) -> None:
    for path, content in outputs(data).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8-sig", newline="\n")
        print(f"m6_power: wrote {path.relative_to(ROOT)}")
    ROSTER_REPORT.write_text(roster_coverage(data), encoding="utf-8", newline="\n")
    print(f"m6_power: wrote {ROSTER_REPORT.relative_to(ROOT)}")


def check(data: PowerData) -> bool:
    failures = []
    for path, expected in outputs(data).items():
        if not path.is_file():
            failures.append(f"missing {path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8-sig") != expected:
            failures.append(f"stale {path.relative_to(ROOT)}")
    if not ROSTER_REPORT.is_file():
        failures.append(f"missing {ROSTER_REPORT.relative_to(ROOT)}")
    elif ROSTER_REPORT.read_text(encoding="utf-8") != roster_coverage(data):
        failures.append(f"stale {ROSTER_REPORT.relative_to(ROOT)}")
    if failures:
        print("m6_power: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return False
    print(
        f"m6_power: PASS ({len(data.dynasties)} dynasties, {len(data.characters)} characters, "
        f"{len(data.governments)} governments, {len(data.ruler_terms)} ruler terms, "
        f"{len(data.regnal_histories)} regnal-history rows, {len(data.privileges)} privileges, {len(data.laws)} laws; "
        f"{sum(1 for government in data.governments.values() if has_named_active_head(government))} named / "
        f"{sum(1 for government in data.governments.values() if government['ruler'] == 'random')} anonymous profiles)"
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
