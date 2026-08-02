#!/usr/bin/env python3
"""Generate checked M4 culture and religion definition foundations.

The source CSVs are deliberately historical design data rather than an opaque
script dump.  They keep engine-valid language links explicit, generate the
additive definition files with the locally verified UTF-8-BOM convention, and
export a small symbol index for later country/pop generators.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from dates import AntqDate, END, START, load_timeline

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/m4"
CULTURES = DATA / "cultures.csv"
RELIGIONS = DATA / "religions.csv"
PROFILES = DATA / "regional_profiles.csv"
VANILLA_LANGUAGES = ROOT / "docs/vanilla_symbols/language.json"
VANILLA_RELIGION_GROUPS = ROOT / "docs/vanilla_symbols/religion_group.json"
M4_LANGUAGES = DATA / "languages.csv"
CULTURAL_VIEW_CLUSTERS = DATA / "cultural_view_clusters.csv"
CULTURAL_VIEWS = DATA / "cultural_views.csv"
SYMBOLS = DATA / "definition_symbols.json"
RELIGION_MECHANICS_AUDIT = DATA / "religion_mechanics.csv"
TIMELINE = ROOT / "docs/timeline.csv"
COMMON = ROOT / "in_game/common"
LOC_ROOT = ROOT / "main_menu/localization"
START_POPS = ROOT / "main_menu/setup/start/06_pops.txt"
COMPATIBILITY_POPS = ROOT / "main_menu/setup/start/21_locations.txt"
LOCAL_PATHS = ROOT / "config/local_paths.json"
LOCALIZATION_LANGUAGES = (
    "english",
    "french",
    "german",
    "spanish",
    "polish",
    "russian",
    "braz_por",
    "simp_chinese",
    "japanese",
    "korean",
    "turkish",
)

# EU5's `is_religion_pagan` trigger recognises its native folk groups.  Keep
# ANTIQVITAS's finer historical families (the CSV `group` column and its
# localization) while mapping the engine-facing group to the closest native
# mechanics family.  This preserves the historical labels and makes the
# engine's marriage, reform, god, and slave-demand contracts operate on AD 1
# religions rather than treating every custom group as non-pagan.
NATIVE_RELIGION_GROUPS = {
    "antq_abrahamic_group": "israelite_group",
    "antq_african_folk_group": "folk_african_group",
    "antq_american_religion_group": "tonal_group",
    "antq_arabian_religion_group": "folk_asian_group",
    "antq_buddhist_group": "buddhist",
    "antq_christian_group": "christian",
    "antq_classical_pagan_group": "folk_european_group",
    "antq_east_asian_religion_group": "folk_asian_group",
    "antq_european_folk_group": "folk_european_group",
    "antq_indian_religion_group": "dharmic",
    "antq_iranian_religion_group": "zoroastrian_group",
    "antq_nile_religion_group": "folk_african_group",
    "antq_northeast_indian_religion_group": "folk_asian_group",
    "antq_oceanic_religion_group": "folk_polynesian_group",
    "antq_steppe_religion_group": "folk_asian_group",
}
NATIVE_RELIGION_GROUP_OVERRIDES = {
    "antq_manichaeism": "manichaean_group",
    "antq_andean": "folk_peruvian_group",
    "antq_north_american": "folk_north_american_group",
    "antq_caribbean": "folk_caribbean_group",
    "antq_australian_dreaming": "folk_australian_group",
    "antq_papuan_local_traditions": "folk_papuan_group",
    "antq_mariana_island_traditions": "folk_micronesian_group",
    "antq_western_caroline_traditions": "folk_micronesian_group",
    "antq_central_amazon_traditions": "folk_brazilian_group",
    "antq_mainland_southeast_asian_traditions": "folk_se_asian_group",
}
RELIGION_TIMELINE_KEYS = {
    "antq_early_christianity": "christianity_foundation",
    "antq_daoism": "celestial_masters",
    "antq_manichaeism": "manichaeism_foundation",
}
RELIGIOUS_VIEW_PAIRS = (
    ("antq_religio_romana", "antq_hellenic", "kindred"),
    ("antq_religio_romana", "antq_punic", "positive"),
    ("antq_hellenic", "antq_punic", "positive"),
    ("antq_early_christianity", "antq_judaism", "positive"),
    ("antq_arsacid_zoroastrianism", "antq_eastern_iranian_traditions", "positive"),
    ("antq_eastern_iranian_traditions", "antq_tarim_oasis_traditions", "positive"),
    ("antq_arsacid_zoroastrianism", "antq_manichaeism", "negative"),
    ("antq_theravada", "antq_mahayana", "kindred"),
    ("antq_brahmanism", "antq_jainism", "positive"),
    ("antq_chinese_state_cult", "antq_daoism", "positive"),
    ("antq_kami", "antq_korean_muism", "positive"),
    ("antq_tengri", "antq_siberian", "positive"),
    ("antq_kemetic", "antq_kushite_amun", "kindred"),
    ("antq_kushite_amun", "antq_aksumite_paganism", "positive"),
    ("antq_arabian_polytheism", "antq_south_arabian_religion", "positive"),
)


@dataclass(frozen=True)
class Definition:
    key: str
    name: str
    group: str
    language: str
    source: str
    confidence: str
    note: str


@dataclass(frozen=True)
class ReligionMechanics:
    profile: str
    slots: int
    influence: bool
    modifiers: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class Profile:
    region: str
    culture: str
    religion: str
    source: str
    confidence: str
    note: str


@dataclass(frozen=True)
class Language:
    group: str
    key: str
    name: str
    family: str
    fallback: str
    male_names: str
    female_names: str
    dynasty_names: str
    source: str
    confidence: str
    note: str


def read_rows(
    path: Path,
    expected: tuple[str, ...],
    *,
    allow_blank: tuple[str, ...] = (),
) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != expected:
            raise ValueError(f"{path.relative_to(ROOT)}: unexpected header")
        rows = list(reader)
    if not rows:
        raise ValueError(f"{path.relative_to(ROOT)}: no rows")
    for number, row in enumerate(rows, start=2):
        if any(not row[key].strip() for key in expected if key not in allow_blank):
            raise ValueError(f"{path.relative_to(ROOT)}:{number}: blank required field")
    return rows


def definitions(path: Path) -> list[Definition]:
    rows = read_rows(path, ("key", "name", "group", "language", "source", "confidence", "note"))
    return [Definition(**row) for row in rows]


def profiles() -> list[Profile]:
    rows = read_rows(PROFILES, ("region", "culture", "religion", "source", "confidence", "note"))
    return [Profile(**row) for row in rows]


def languages() -> list[Language]:
    rows = read_rows(
        M4_LANGUAGES,
        (
            "group",
            "key",
            "name",
            "family",
            "fallback",
            "male_names",
            "female_names",
            "dynasty_names",
            "source",
            "confidence",
            "note",
        ),
        allow_blank=("family",),
    )
    return [Language(**row) for row in rows]


def title(key: str) -> str:
    return key.removeprefix("antq_").removesuffix("_group").replace("_", " ").title()


def native_religion_group(row: Definition) -> str:
    return NATIVE_RELIGION_GROUP_OVERRIDES.get(row.key, NATIVE_RELIGION_GROUPS[row.group])


def mechanic(
    profile: str,
    slots: int,
    influence: bool,
    *modifiers: tuple[str, str],
) -> ReligionMechanics:
    return ReligionMechanics(profile, slots, influence, tuple(modifiers))


def religion_mechanics(row: Definition) -> ReligionMechanics:
    """Return a bounded historical family profile, never a universal clone."""
    key = row.key
    if key == "antq_early_christianity":
        return mechanic("christian_missionary", 3, True,
            ("tolerance_own", "1.00"), ("tolerance_heretic", "0.50"),
            ("monthly_religious_influence", "0.10"), ("maximum_religious_influence", "400"),
            ("global_pop_conversion_speed_modifier", "0.08"), ("global_max_literacy", "2"))
    if key == "antq_judaism":
        return mechanic("jewish_covenantal", 2, True,
            ("tolerance_own", "1.50"), ("tolerance_heathen", "0.50"),
            ("monthly_religious_influence", "0.06"), ("maximum_religious_influence", "250"),
            ("global_pop_conversion_speed_modifier", "-0.10"), ("monthly_legitimacy", "0.02"))
    if row.group == "antq_classical_pagan_group":
        return mechanic("mediterranean_civic", 2, True,
            ("tolerance_own", "0.75"), ("tolerance_heathen", "1.00"),
            ("monthly_religious_influence", "0.08"), ("maximum_religious_influence", "300"),
            ("monthly_legitimacy", "0.03"))
    if key == "antq_arsacid_zoroastrianism":
        return mechanic("iranian_state", 2, True,
            ("tolerance_own", "1.00"), ("tolerance_heathen", "0.50"),
            ("monthly_religious_influence", "0.08"), ("maximum_religious_influence", "300"),
            ("global_pop_conversion_speed_modifier", "0.02"), ("monthly_legitimacy", "0.03"))
    if key == "antq_manichaeism":
        return mechanic("manichaean_missionary", 3, True,
            ("tolerance_own", "1.00"), ("tolerance_heretic", "1.00"),
            ("monthly_religious_influence", "0.10"), ("maximum_religious_influence", "350"),
            ("global_pop_conversion_speed_modifier", "0.10"), ("global_max_literacy", "2"))
    if key in {"antq_theravada", "antq_mahayana"}:
        return mechanic("buddhist_monastic", 2, True,
            ("tolerance_own", "1.00"), ("tolerance_heathen", "1.00"),
            ("monthly_religious_influence", "0.08"), ("maximum_religious_influence", "300"),
            ("global_pop_conversion_speed_modifier", "0.04"), ("global_max_literacy", "2"))
    if key == "antq_brahmanism":
        return mechanic("brahmanical_ritual", 2, True,
            ("tolerance_own", "1.00"), ("tolerance_heathen", "0.75"),
            ("monthly_religious_influence", "0.07"), ("maximum_religious_influence", "300"),
            ("global_pop_conversion_speed_modifier", "0.02"), ("monthly_legitimacy", "0.03"))
    if key == "antq_jainism":
        return mechanic("jain_community", 2, True,
            ("tolerance_own", "1.25"), ("tolerance_heathen", "1.00"),
            ("monthly_religious_influence", "0.06"), ("maximum_religious_influence", "250"),
            ("global_pop_conversion_speed_modifier", "-0.05"), ("global_life_expectancy", "0.02"))
    if key == "antq_chinese_state_cult":
        return mechanic("han_state_rites", 2, True,
            ("tolerance_own", "0.75"), ("tolerance_heathen", "1.00"),
            ("monthly_religious_influence", "0.08"), ("maximum_religious_influence", "300"),
            ("global_pop_conversion_speed_modifier", "0.01"), ("monthly_legitimacy", "0.04"))
    if key == "antq_daoism":
        return mechanic("daoist_organized", 2, True,
            ("tolerance_own", "1.00"), ("tolerance_heathen", "1.00"),
            ("monthly_religious_influence", "0.07"), ("maximum_religious_influence", "275"),
            ("global_pop_conversion_speed_modifier", "0.03"), ("global_monthly_prosperity", "0.02"))
    if row.group == "antq_east_asian_religion_group":
        return mechanic("east_asian_local", 1, False,
            ("tolerance_own", "0.75"), ("tolerance_heathen", "1.00"),
            ("global_pop_conversion_speed_modifier", "-0.05"),
            ("global_monthly_food_modifier", "0.01"), ("global_monthly_prosperity", "0.01"))
    if key == "antq_tengri":
        return mechanic("steppe_sky", 1, False,
            ("tolerance_own", "0.75"), ("tolerance_heathen", "0.50"),
            ("global_pop_conversion_speed_modifier", "-0.05"), ("land_morale_modifier", "0.02"))
    if row.group == "antq_steppe_religion_group":
        return mechanic("highland_forest_local", 1, False,
            ("tolerance_own", "0.75"), ("tolerance_heathen", "0.75"),
            ("global_pop_conversion_speed_modifier", "-0.10"),
            ("global_monthly_food_modifier", "0.02"), ("global_hostile_attrition", "0.02"))
    if row.group == "antq_nile_religion_group":
        return mechanic("nile_state_temple", 2, True,
            ("tolerance_own", "0.75"), ("tolerance_heathen", "1.00"),
            ("monthly_religious_influence", "0.07"), ("maximum_religious_influence", "275"),
            ("monthly_legitimacy", "0.03"), ("global_monthly_prosperity", "0.02"))
    if row.group == "antq_arabian_religion_group":
        return mechanic("arabian_temple_network", 2, True,
            ("tolerance_own", "0.75"), ("tolerance_heathen", "0.75"),
            ("monthly_religious_influence", "0.06"), ("maximum_religious_influence", "250"),
            ("monthly_legitimacy", "0.02"), ("global_monthly_food_modifier", "0.01"))
    if row.group == "antq_european_folk_group":
        return mechanic("european_local_cult", 1, False,
            ("tolerance_own", "0.75"), ("tolerance_heathen", "0.50"),
            ("global_pop_conversion_speed_modifier", "-0.08"), ("land_morale_modifier", "0.01"))
    if row.group == "antq_african_folk_group":
        return mechanic("african_local_cult", 1, False,
            ("tolerance_own", "0.75"), ("tolerance_heathen", "0.75"),
            ("global_pop_conversion_speed_modifier", "-0.10"),
            ("global_monthly_food_modifier", "0.02"), ("global_life_expectancy", "0.01"))
    if key in {"antq_mesoamerican", "antq_andean"}:
        return mechanic("american_state_ritual", 2, True,
            ("tolerance_own", "0.75"), ("tolerance_heathen", "0.50"),
            ("monthly_religious_influence", "0.06"), ("maximum_religious_influence", "250"),
            ("monthly_legitimacy", "0.02"), ("global_monthly_food_modifier", "0.02"))
    if row.group == "antq_american_religion_group":
        return mechanic("american_local_cult", 1, False,
            ("tolerance_own", "0.75"), ("tolerance_heathen", "0.75"),
            ("global_pop_conversion_speed_modifier", "-0.10"),
            ("global_monthly_food_modifier", "0.02"), ("global_hostile_attrition", "0.03"))
    if row.group == "antq_oceanic_religion_group":
        return mechanic("oceanic_local_cult", 1, False,
            ("tolerance_own", "0.75"), ("tolerance_heathen", "1.00"),
            ("global_pop_conversion_speed_modifier", "-0.10"),
            ("global_monthly_food_modifier", "0.02"), ("global_monthly_prosperity", "0.02"))
    if row.group == "antq_iranian_religion_group":
        return mechanic("iranian_local_cult", 1, False,
            ("tolerance_own", "0.75"), ("tolerance_heathen", "0.75"),
            ("global_pop_conversion_speed_modifier", "-0.08"),
            ("global_monthly_prosperity", "0.01"), ("cultural_tradition_modifier", "0.02"))
    if row.group in {"antq_northeast_indian_religion_group", "antq_buddhist_group"}:
        return mechanic("asian_local_cult", 1, False,
            ("tolerance_own", "0.75"), ("tolerance_heathen", "1.00"),
            ("global_pop_conversion_speed_modifier", "-0.10"),
            ("global_monthly_food_modifier", "0.02"), ("global_monthly_prosperity", "0.01"))
    raise ValueError(f"{row.key}: no explicit religion-mechanics profile")


def religious_opinions(row: Definition, rows: list[Definition]) -> tuple[tuple[str, str], ...]:
    known = {item.key for item in rows}
    opinions: list[tuple[str, str]] = []
    for left, right, view in RELIGIOUS_VIEW_PAIRS:
        if left not in known or right not in known:
            raise ValueError(f"religious view references unknown pair: {left}, {right}")
        if row.key == left:
            opinions.append((right, view))
        elif row.key == right:
            opinions.append((left, view))
    return tuple(sorted(opinions))


def language_families() -> set[str]:
    config = json.loads(LOCAL_PATHS.read_text(encoding="utf-8-sig"))
    root = Path(config["game_dir"]) / "game/in_game/common/languages"
    pattern = re.compile(r"(?m)^\s*family\s*=\s*([A-Za-z0-9_]+)")
    return {
        value
        for path in root.glob("*.txt")
        for value in pattern.findall(path.read_text(encoding="utf-8-sig", errors="replace"))
    }


def game_definition_dir(kind: str) -> Path:
    """Return a read-only vanilla definition folder verified by local paths."""
    config = json.loads(LOCAL_PATHS.read_text(encoding="utf-8-sig"))
    directory = Path(config["game_dir"]) / "game/in_game/common" / kind
    if not directory.is_dir():
        raise ValueError(f"missing locally installed vanilla {kind} directory: {directory}")
    return directory


def brace_delta(line: str) -> int:
    """Count script braces while ignoring comments and quoted text."""
    quoted = False
    escaped = False
    delta = 0
    for char in line:
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '#':
            break
        elif char == '"':
            quoted = True
        elif char == '{':
            delta += 1
        elif char == '}':
            delta -= 1
    return delta


TOP_LEVEL_DEFINITION = re.compile(r"^\s*[A-Za-z0-9_]+\s*=\s*\{")
TOP_LEVEL_ENABLE = re.compile(r"^\s*enable\s*=")


def render_vanilla_compatibility(path: Path, kind: str) -> str:
    """Mirror one vanilla definition file with total-conversion start guards.

    Exact-name overlays retain symbols used by otherwise inert vanilla scripts.
    The live engine rejects the culture suppressor shown in its shipped schema,
    so culture mirrors remain byte-equivalent compatibility copies. Religion
    definitions use their locally demonstrated availability field, generated
    from the single campaign calendar at the terminal campaign date, so vanilla
    religions cannot appear in an AD 1 start.
    """
    if kind not in {"cultures", "religions"}:
        raise ValueError(f"unsupported vanilla compatibility kind: {kind}")
    lines = path.read_text(encoding="utf-8-sig", errors="strict").splitlines()
    output = [
        f"# Generated from installed vanilla {kind}/{path.name} by {Path(__file__).name} --write.",
        "# ANTIQVITAS exact-name compatibility overlay; do not hand-edit.",
    ]
    depth = 0
    terminal_date = AntqDate(*END).engine()
    for line in lines:
        code = line.split("#", 1)[0]
        delta = brace_delta(line)
        top_level_open = depth == 0 and TOP_LEVEL_DEFINITION.match(code)
        direct_child = depth == 1
        if kind == "religions" and direct_child and TOP_LEVEL_ENABLE.match(code):
            depth += delta
            continue
        output.append(line)
        if top_level_open:
            if kind == "religions":
                output.append(
                    f"\tenable = {terminal_date} # unavailable before ANTIQVITAS campaign end"
                )
        depth += delta
        if depth < 0:
            raise ValueError(f"unbalanced vanilla source {path}")
    if depth:
        raise ValueError(f"unbalanced vanilla source {path}")
    return "\n".join(output) + "\n"


def vanilla_compatibility_outputs(kind: str) -> dict[Path, tuple[str, str]]:
    source = game_definition_dir(kind)
    source_files = sorted(source.glob("*.txt"))
    if not source_files:
        raise ValueError(f"no vanilla {kind} definition files found in {source}")
    return {
        COMMON / kind / path.name: (render_vanilla_compatibility(path, kind), "utf-8-sig")
        for path in source_files
    }


def starting_pop_religions() -> set[str]:
    paths = (START_POPS, COMPATIBILITY_POPS)
    missing = [path.relative_to(ROOT) for path in paths if not path.is_file()]
    if missing:
        raise ValueError(f"missing generated AD 1 population setup: {missing}")
    return set().union(*(
        set(re.findall(r"\breligion\s*=\s*([A-Za-z0-9_]+)", path.read_text(encoding="utf-8")))
        for path in paths
    ))


def religion_availability() -> dict[str, tuple[AntqDate, str]]:
    timeline = {row["key"]: row for row in load_timeline(TIMELINE)}
    result: dict[str, tuple[AntqDate, str]] = {}
    for religion, timeline_key in RELIGION_TIMELINE_KEYS.items():
        if timeline_key not in timeline:
            raise ValueError(f"timeline lacks religion foundation current {timeline_key}")
        row = timeline[timeline_key]
        result[religion] = (AntqDate.parse(row["date"]), row["source"].strip())
    return result


def render_religion_mechanics_audit(rows: list[Definition]) -> str:
    availability = religion_availability()
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow((
        "religion", "semantic_group", "native_group", "profile", "slots",
        "influence", "modifiers", "enable_date", "source", "confidence", "note",
    ))
    for row in rows:
        mechanics = religion_mechanics(row)
        enabled = availability.get(row.key)
        writer.writerow((
            row.key, row.group, native_religion_group(row), mechanics.profile,
            mechanics.slots, "yes" if mechanics.influence else "no",
            ";".join(f"{key}={value}" for key, value in mechanics.modifiers),
            enabled[0].engine() if enabled else AntqDate(*START).engine(),
            enabled[1] if enabled else row.source, row.confidence, row.note,
        ))
    return output.getvalue()


def validate(
    cultures: list[Definition], religions: list[Definition], regional: list[Profile], language_rows: list[Language]
) -> list[str]:
    failures: list[str] = []
    vanilla_languages = set(json.loads(VANILLA_LANGUAGES.read_text(encoding="utf-8-sig")))
    vanilla_religion_groups = set(json.loads(VANILLA_RELIGION_GROUPS.read_text(encoding="utf-8-sig")))
    families = language_families()
    custom_languages = {row.key for row in language_rows}
    for label, rows in (("culture", cultures), ("religion", religions)):
        keys = [row.key for row in rows]
        if len(keys) != len(set(keys)):
            failures.append(f"duplicate M4 {label} key")
        for row in rows:
            if not row.key.startswith("antq_"):
                failures.append(f"{label} key is not namespaced: {row.key}")
            if not row.group.startswith("antq_"):
                failures.append(f"{label} group is not namespaced: {row.group}")
            allowed_languages = (
                vanilla_languages | custom_languages
                if label == "culture"
                else vanilla_languages
            )
            if row.language not in allowed_languages:
                failures.append(f"{row.key}: unknown locally harvested language {row.language}")
            if row.confidence not in {"secure", "contested"}:
                failures.append(f"{row.key}: invalid confidence {row.confidence}")
            if label == "religion":
                if row.group not in NATIVE_RELIGION_GROUPS:
                    failures.append(f"{row.key}: no native religion-group compatibility mapping")
                elif native_religion_group(row) not in vanilla_religion_groups:
                    failures.append(f"{row.key}: unknown native religion group {native_religion_group(row)}")
    culture_keys = {row.key for row in cultures}
    religion_keys = {row.key for row in religions}
    availability = religion_availability()
    if set(availability) != set(RELIGION_TIMELINE_KEYS):
        failures.append("religion availability does not match the dated foundation roster")
    if not set(availability).issubset(religion_keys):
        failures.append("religion availability references an unknown religion")
    mechanics = [religion_mechanics(row) for row in religions]
    if len({item.profile for item in mechanics}) < 20:
        failures.append("religion mechanics expose fewer than 20 distinct historical profiles")
    if {item.slots for item in mechanics} != {1, 2, 3}:
        failures.append("religion aspect slots do not span local, organized, and missionary profiles")
    if {item.influence for item in mechanics} != {False, True}:
        failures.append("religious influence access is not differentiated")
    opinion_values = {
        view for row in religions for _, view in religious_opinions(row, religions)
    }
    if not {"kindred", "positive", "negative"}.issubset(opinion_values):
        failures.append("interfaith opinion profiles lack kindred/positive/negative distinctions")
    overlap = sorted(culture_keys & religion_keys)
    if overlap:
        failures.append(f"culture/religion keys share a localization namespace: {', '.join(overlap)}")
    regions = [row.region for row in regional]
    if len(regions) != len(set(regions)):
        failures.append("duplicate M4 regional profile")
    for row in regional:
        if row.culture not in culture_keys:
            failures.append(f"{row.region}: unknown M4 culture {row.culture}")
        if row.religion not in religion_keys:
            failures.append(f"{row.region}: unknown M4 religion {row.religion}")
        if row.confidence not in {"secure", "contested"}:
            failures.append(f"{row.region}: invalid profile confidence {row.confidence}")
    keys = [row.key for row in language_rows]
    if len(keys) != len(set(keys)):
        failures.append("duplicate M4 language key")
    for row in language_rows:
        if not row.group.startswith("antq_") or not row.key.startswith("antq_"):
            failures.append(f"M4 language is not namespaced: {row.key}")
        if row.family and row.family not in families:
            failures.append(f"{row.key}: unknown local language family {row.family}")
        if row.fallback not in vanilla_languages:
            failures.append(f"{row.key}: unknown local language fallback {row.fallback}")
        if row.confidence not in {"secure", "contested"}:
            failures.append(f"{row.key}: invalid language confidence {row.confidence}")
    for group in {row.group for row in cultures}:
        default = group.removesuffix("_group") + "_language"
        if default not in custom_languages:
            failures.append(
                f"culture group {group} has no default M4 language {default}"
            )
    return sorted(set(failures))


def render_groups(groups: set[str], label: str) -> str:
    lines = [f"# Generated by {Path(__file__).name} --write.", f"# M4 {label} groups; M4 content foundation."]
    for group in sorted(groups):
        lines.extend(("", f"{group} = {{", "}"))
    return "\n".join(lines) + "\n"


def render_cultures(
    rows: list[Definition],
    dialects: dict[str, str],
    defaults: dict[str, str],
    opinions: dict[str, dict[str, str]],
) -> str:
    location_gfx = {
        "antq_italic_group": "mediterranean_gfx",
        "antq_hellenic_group": "east_mediterranean_gfx",
        "antq_iberian_group": "mediterranean_gfx",
        "antq_anatolian_group": "east_mediterranean_gfx",
        "antq_indian_group": "indian_gfx",
        "antq_iranian_group": "middle_east_gfx",
        "antq_semitic_group": "middle_east_gfx",
        "antq_caucasian_group": "middle_east_gfx",
        "antq_berber_group": "african_gfx",
        "antq_nile_group": "african_gfx",
        "antq_subsaharan_group": "african_gfx",
        "antq_sinitic_group": "east_asian_gfx",
        "antq_korean_group": "east_asian_gfx",
        "antq_japonic_group": "east_asian_gfx",
        "antq_tibetan_group": "east_asian_gfx",
        "antq_southeast_asian_group": "east_asian_gfx",
        "antq_austronesian_group": "east_asian_gfx",
        "antq_north_maluku_group": "east_asian_gfx",
        "antq_oceanic_group": "east_asian_gfx",
        "antq_mesoamerican_group": "south_american_gfx",
        "antq_andean_group": "south_american_gfx",
        "antq_american_group": "north_american_gfx",
        "antq_steppe_group": "middle_east_gfx",
    }
    lines = [f"# Generated by {Path(__file__).name} --write.", "# M4 sourced culture foundation."]
    for row in rows:
        specific_gfx = location_gfx.get(row.group, "european_gfx")
        # Installed Mediterranean fallbacks need the lower-priority European
        # audio/ethnicity resolver. Other continental tags are self-contained.
        gfx_tags = (
            (specific_gfx, "european_gfx")
            if specific_gfx in {"mediterranean_gfx", "east_mediterranean_gfx"}
            else (specific_gfx,)
        )
        tags = " ".join(gfx_tags)
        lines.extend(
            (
                "",
                f"{row.key} = {{ # {row.source}; {row.note}",
                f"\tlanguage = {dialects.get(row.language, defaults[row.group])}",
                f"\tcolor = antq_culture_color_{row.key}",
                f"\ttags = {{ {tags} }}",
                "\topinions = {",
                *(
                    f"\t\t{target} = {view}"
                    for target, view in sorted(opinions.get(row.key, {}).items())
                ),
                "\t}",
                "\tculture_groups = {",
                f"\t\t{row.group}",
                "\t}",
                "}",
            )
        )
    return "\n".join(lines) + "\n"


def cultural_opinions(culture_keys: set[str]) -> dict[str, dict[str, str]]:
    levels = {"enemy", "negative", "neutral", "positive", "kindred"}
    result: defaultdict[str, dict[str, str]] = defaultdict(dict)

    def assign(source: str, target: str, view: str, context: str) -> None:
        if source == target:
            raise ValueError(f"{context}: self-directed cultural view")
        if source not in culture_keys or target not in culture_keys:
            raise ValueError(f"{context}: unknown culture {source} -> {target}")
        old = result[source].get(target)
        if old is not None and old != view:
            raise ValueError(
                f"{context}: conflicting cultural view {source} -> {target}: {old}/{view}"
            )
        result[source][target] = view

    cluster_fields = ("cluster", "view", "cultures", "source", "confidence", "note")
    with CULTURAL_VIEW_CLUSTERS.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != cluster_fields:
            raise ValueError(f"{CULTURAL_VIEW_CLUSTERS.relative_to(ROOT)}: unexpected header")
        clusters = list(reader)
    seen_clusters: set[str] = set()
    for number, row in enumerate(clusters, start=2):
        if any(not row[field].strip() for field in cluster_fields):
            raise ValueError(
                f"{CULTURAL_VIEW_CLUSTERS.relative_to(ROOT)}:{number}: blank required field"
            )
        cluster = row["cluster"].strip()
        view = row["view"].strip()
        members = tuple(item.strip() for item in row["cultures"].split("|") if item.strip())
        if cluster in seen_clusters or len(members) < 2 or len(members) != len(set(members)):
            raise ValueError(f"{cluster}: invalid or duplicate cultural-view cluster")
        if view not in levels or row["confidence"].strip() not in {"secure", "contested"}:
            raise ValueError(f"{cluster}: invalid view or confidence")
        seen_clusters.add(cluster)
        for source in members:
            for target in members:
                if source != target:
                    assign(source, target, view, cluster)

    view_fields = (
        "source_culture", "target_culture", "view", "reciprocal",
        "source", "confidence", "note",
    )
    with CULTURAL_VIEWS.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != view_fields:
            raise ValueError(f"{CULTURAL_VIEWS.relative_to(ROOT)}: unexpected header")
        rows = list(reader)
    for number, row in enumerate(rows, start=2):
        if any(not row[field].strip() for field in view_fields):
            raise ValueError(
                f"{CULTURAL_VIEWS.relative_to(ROOT)}:{number}: blank required field"
            )
        source = row["source_culture"].strip()
        target = row["target_culture"].strip()
        view = row["view"].strip()
        reciprocal = row["reciprocal"].strip()
        if view not in levels or reciprocal not in {"yes", "no"}:
            raise ValueError(f"{CULTURAL_VIEWS.relative_to(ROOT)}:{number}: invalid view")
        if row["confidence"].strip() not in {"secure", "contested"}:
            raise ValueError(f"{CULTURAL_VIEWS.relative_to(ROOT)}:{number}: invalid confidence")
        assign(source, target, view, f"{CULTURAL_VIEWS.name}:{number}")
        if reciprocal == "yes":
            assign(target, source, view, f"{CULTURAL_VIEWS.name}:{number}")
    return {key: dict(value) for key, value in result.items()}


def render_religions(rows: list[Definition]) -> str:
    availability = religion_availability()
    lines = [
        f"# Generated by {Path(__file__).name} --write.",
        "# M4 sourced religion foundation; M10 owns dated conversions and schisms.",
        "# Future faith objects stay loaded so dated M10 effects can resolve them; no adherent pop exists before its foundation event.",
        "# Native groups preserve engine pagan/mechanics contracts; semantic ANTIQVITAS families remain localized separately.",
    ]
    for row in rows:
        mechanics = religion_mechanics(row)
        opinions = religious_opinions(row, rows)
        lines.extend(
            (
                "",
                f"{row.key} = {{ # {row.source}; {row.note}",
                f"\tcolor = antq_religion_color_{row.key}",
                f"\tgroup = {native_religion_group(row)}",
                *((f"\tenable = {availability[row.key][0].engine()}",) if row.key in availability else ()),
                f"\treligious_aspects = {mechanics.slots}",
                *(("\thas_religious_influence = yes",) if mechanics.influence else ()),
                *(("\thas_omens = yes",) if row.key == "antq_religio_romana" else ()),
                "\tdefinition_modifier = {",
                *(f"\t\t{field} = {value}" for field, value in mechanics.modifiers),
                *(("\t\tomens_offered = 3",) if row.key == "antq_religio_romana" else ()),
                "\t}",
            )
        )
        if opinions:
            lines.extend((
                "\topinions = {",
                *(f"\t\t{target} = {opinion}" for target, opinion in opinions),
                "\t}",
            ))
        lines.append("}")
    return "\n".join(lines) + "\n"


def render_religion_groups(groups: set[str]) -> str:
    return (
        f"# Generated by {Path(__file__).name} --write.\n"
        "# Semantic ANTIQVITAS families live in docs/m4/religions.csv; engine-facing religions use populated native groups.\n"
        "# No empty custom religion-group adapters are mounted.\n"
    )


def render_languages(rows: list[Language]) -> str:
    lines = [f"# Generated by {Path(__file__).name} --write.", "# M4 ancient language roots and their engine-valid dialects."]
    for row in rows:
        dialect = row.key.replace("_language", "_dialect")
        male = " ".join(name_key(value) for value in row.male_names.split("|"))
        female = " ".join(name_key(value) for value in row.female_names.split("|"))
        dynasty = " ".join(name_key(value) for value in row.dynasty_names.split("|"))
        lines.extend(
            (
                "",
                f"{row.key} = {{ # {row.source}; {row.note}",
                f"\tcolor = antq_language_color_{row.key}",
            )
        )
        if row.family:
            lines.append(f"\tfamily = {row.family}")
        lines.extend(
            (
                f"\tfallback = {row.fallback}",
                "\tmale_names = {",
                f"\t\t{male}",
                "\t}",
                "\tfemale_names = {",
                f"\t\t{female}",
                "\t}",
                "\tdynasty_names = {",
                f"\t\t{dynasty}",
                "\t}",
                "\tlowborn = {",
                f"\t\t{dynasty}",
                "\t}",
                "\tdialects = {",
                f"\t\t{dialect} = {{ }}",
                "\t}",
                "}",
            )
        )
    return "\n".join(lines) + "\n"


def name_key(value: str) -> str:
    return "antq_name_" + re.sub(r"[^a-z0-9_]+", "_", value.lower()).strip("_")


def language_name_entries(rows: list[Language]) -> dict[str, str]:
    entries: dict[str, str] = {}
    for row in rows:
        for raw in (*row.male_names.split("|"), *row.female_names.split("|"), *row.dynasty_names.split("|")):
            key = name_key(raw)
            old = entries.setdefault(key, raw)
            if old != raw:
                raise ValueError(f"name key collision: {old!r} and {raw!r}")
    return entries


def render_named_colors(cultures: list[Definition], religions: list[Definition], languages: list[Language]) -> str:
    """Render unique named colors; the engine reports duplicate culture colors."""
    rows = (
        [("culture", row) for row in cultures]
        + [("religion", row) for row in religions]
        + [("language", row) for row in languages]
    )
    lines = [f"# Generated by {Path(__file__).name} --write.", "colors = {"]
    for index, (kind, row) in enumerate(rows):
        hue = (index * 137 + 19) % 360
        saturation = 52 + (index * 17) % 39
        value = 48 + (index * 11) % 39
        lines.append(f"\tantq_{kind}_color_{row.key} = hsv360 {{ {hue} {saturation} {value} }}")
    lines.append("}")
    return "\n".join(lines) + "\n"


def render_localization(cultures: list[Definition], religions: list[Definition], languages: list[Language], language: str) -> str:
    lines = [f"l_{language}:", " # M4 names are deliberately mirrored in all supported game languages."]
    for row in cultures:
        lines.append(f' {row.key}: "{row.name}"')
    for group in sorted({row.group for row in cultures}):
        lines.append(f' {group}: "{title(group)}"')
        lines.append(f' {group}_ADJ: "{title(group)}"')
        lines.append(f' {group}_desc: "{title(group)} culture family."')
    for row in religions:
        lines.append(f' {row.key}: "{row.name}"')
        lines.append(f' {row.key}_ADJ: "{row.name}"')
        lines.append(f' {row.key}_desc: "{row.name} is represented by its AD 1 historical community."')
    for group in sorted({row.group for row in religions}):
        lines.append(f' {group}: "{title(group)}"')
        lines.append(f' {group}_ADJ: "{title(group)}"')
        lines.append(f' {group}_desc: "{title(group)} religious family."')
    for row in languages:
        lines.append(f' {row.key}: "{row.name}"')
        lines.append(f' {row.key.replace("_language", "_dialect")}: "{row.name}"')
    for key, name in sorted(language_name_entries(languages).items()):
        lines.append(f' {key}: "{name}"')
    return "\n".join(lines) + "\n"


def outputs() -> tuple[dict[Path, tuple[str, str]], dict[str, object]]:
    culture_rows = definitions(CULTURES)
    religion_rows = definitions(RELIGIONS)
    profile_rows = profiles()
    language_rows = languages()
    failures = validate(culture_rows, religion_rows, profile_rows, language_rows)
    if failures:
        raise ValueError("\n".join(failures))
    opinions = cultural_opinions({row.key for row in culture_rows})
    absent_from_start = {row.key for row in religion_rows} - starting_pop_religions()
    culture_script = render_cultures(
        culture_rows,
        {
            row.key: row.key.replace("_language", "_dialect")
            for row in language_rows
        },
        {
            row.group: (
                row.group.removesuffix("_group") + "_dialect"
            )
            for row in language_rows
        },
        opinions,
    )
    custom_tag_rows = re.findall(r"(?m)^\s*tags\s*=\s*\{([^}]*)\}", culture_script)
    bad_tag_rows = []
    for tags in custom_tag_rows:
        values = tags.split()
        allowed_pair = (
            len(values) == 2
            and values[0] in {"mediterranean_gfx", "east_mediterranean_gfx"}
            and values[1] == "european_gfx"
        )
        if len(values) != len(set(values)) or not (len(values) == 1 or allowed_pair):
            bad_tag_rows.append(tags)
    if len(custom_tag_rows) != len(culture_rows) or bad_tag_rows:
        raise ValueError(
            "custom culture graphical tags must be one self-contained resolver or "
            "a Mediterranean resolver plus lower-priority european_gfx; "
            f"rows={len(custom_tag_rows)}/{len(culture_rows)} bad={bad_tag_rows[:3]}"
        )
    files: dict[Path, tuple[str, str]] = {
        COMMON / "culture_groups/antq_m4_groups.txt": (render_groups({row.group for row in culture_rows}, "culture"), "utf-8-sig"),
        COMMON / "cultures/antq_m4_cultures.txt": (culture_script, "utf-8-sig"),
        COMMON / "religion_groups/antq_m4_groups.txt": (render_religion_groups({row.group for row in religion_rows}), "utf-8-sig"),
        COMMON / "religions/antq_m4_religions.txt": (render_religions(religion_rows), "utf-8-sig"),
        COMMON / "languages/antq_m4_languages.txt": (render_languages(language_rows), "utf-8-sig"),
        ROOT / "main_menu/common/named_colors/antq_m4_colors.txt": (render_named_colors(culture_rows, religion_rows, language_rows), "utf-8-sig"),
        RELIGION_MECHANICS_AUDIT: (render_religion_mechanics_audit(religion_rows), "utf-8-sig"),
    }
    files.update(vanilla_compatibility_outputs("cultures"))
    files.update(vanilla_compatibility_outputs("religions"))
    for language in LOCALIZATION_LANGUAGES:
        files[LOC_ROOT / language / f"antq_m4_people_l_{language}.yml"] = (
            render_localization(culture_rows, religion_rows, language_rows, language),
            "utf-8-sig",
        )
    index: dict[str, object] = {
        "cultures": [row.key for row in culture_rows],
        "religions": [row.key for row in religion_rows],
        "languages": [row.key for row in language_rows],
        "dialects": [row.key.replace("_language", "_dialect") for row in language_rows],
        "regional_profiles": {row.region: {"culture": row.culture, "religion": row.religion} for row in profile_rows},
        "religions_absent_from_start": sorted(absent_from_start),
        "religion_mechanics_profiles": {
            row.key: religion_mechanics(row).profile for row in religion_rows
        },
        "religion_enable_dates": {
            key: value[0].engine() for key, value in religion_availability().items()
        },
    }
    return files, index


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        files, index = outputs()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"m4_definitions: FAIL\n  - {exc}")
        return 1
    if args.write:
        for path, (content, encoding) in files.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding=encoding, newline="\n")
        SYMBOLS.parent.mkdir(parents=True, exist_ok=True)
        SYMBOLS.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
        print(f"m4_definitions: wrote {len(index['cultures'])} cultures and {len(index['religions'])} religions")
        return 0
    failures: list[str] = []
    for path, (content, encoding) in files.items():
        if not path.is_file():
            failures.append(f"missing generated output {path.relative_to(ROOT)}")
        elif path.read_text(encoding=encoding) != content:
            failures.append(f"stale generated output {path.relative_to(ROOT)}")
    expected_index = json.dumps(index, indent=2) + "\n"
    if not SYMBOLS.is_file() or SYMBOLS.read_text(encoding="utf-8") != expected_index:
        failures.append(f"stale generated output {SYMBOLS.relative_to(ROOT)}")
    if failures:
        print("m4_definitions: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return 1
    print(f"m4_definitions: PASS ({len(index['cultures'])} cultures; {len(index['religions'])} religions; {len(index['regional_profiles'])} regional profiles)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
