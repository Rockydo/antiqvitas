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
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from dates import AntqDate, END

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
COMMON = ROOT / "in_game/common"
LOC_ROOT = ROOT / "main_menu/localization"
START_POPS = ROOT / "main_menu/setup/start/06_pops.txt"
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
}
RELIGIOUS_ASPECT_SLOTS = 2
RELIGIOUS_ASPECT_FEATURES = (("has_religious_influence", "yes"),)
RELIGIOUS_ASPECT_DEFINITION_MODIFIERS = (
    ("monthly_religious_influence", "0.10"),
    ("maximum_religious_influence", "400"),
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
    if not START_POPS.is_file():
        raise ValueError(f"missing generated AD 1 population setup: {START_POPS.relative_to(ROOT)}")
    return set(re.findall(r"\breligion\s*=\s*([A-Za-z0-9_]+)", START_POPS.read_text(encoding="utf-8")))


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
    lines = [f"# Generated by {Path(__file__).name} --write.", "# M4 sourced culture foundation."]
    for row in rows:
        lines.extend(
            (
                "",
                f"{row.key} = {{ # {row.source}; {row.note}",
                f"\tlanguage = {dialects.get(row.language, defaults[row.group])}",
                f"\tcolor = antq_culture_color_{row.key}",
                "\ttags = { european_gfx }",
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
    absent_from_start = {row.key for row in rows} - starting_pop_religions()
    aspect_religions = {row.key for row in rows}
    terminal_date = AntqDate(*END).engine()
    lines = [
        f"# Generated by {Path(__file__).name} --write.",
        "# M4 sourced religion foundation; M10 owns dated conversions and schisms.",
        "# Native groups preserve engine pagan/mechanics contracts; semantic ANTIQVITAS families remain localized separately.",
    ]
    for row in rows:
        lines.extend(
            (
                "",
                f"{row.key} = {{ # {row.source}; {row.note}",
                f"\tcolor = antq_religion_color_{row.key}",
                f"\tgroup = {native_religion_group(row)}",
                *(
                    (f"\treligious_aspects = {RELIGIOUS_ASPECT_SLOTS}",)
                    if row.key in aspect_religions
                    else ()
                ),
                *(
                    f"\t{field} = {value}"
                    for field, value in (
                        RELIGIOUS_ASPECT_FEATURES
                        if row.key in aspect_religions
                        else ()
                    )
                ),
                *(("\thas_omens = yes",) if row.key == "antq_religio_romana" else ()),
                *(
                    (f"\tenable = {terminal_date} # unavailable before ANTIQVITAS campaign end",)
                    if row.key in absent_from_start
                    else ()
                ),
                "\tdefinition_modifier = {",
                "\t\ttolerance_own = 0.01",
                *(
                    f"\t\t{field} = {value}"
                    for field, value in (
                        RELIGIOUS_ASPECT_DEFINITION_MODIFIERS
                        if row.key in aspect_religions
                        else ()
                    )
                ),
                *(("\t\tomens_offered = 3",) if row.key == "antq_religio_romana" else ()),
                "\t}",
                "\topinions = {",
                "\t}",
                "}",
            )
        )
    return "\n".join(lines) + "\n"


def render_religion_groups(groups: set[str]) -> str:
    lines = [f"# Generated by {Path(__file__).name} --write.", "# M4 ancient religion groups."]
    for group in sorted(groups):
        lines.extend(("", f"{group} = {{", "\tcolor = map_ROM", "\tconvert_slaves_at_start = no", "}"))
    return "\n".join(lines) + "\n"


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
    files: dict[Path, tuple[str, str]] = {
        COMMON / "culture_groups/antq_m4_groups.txt": (render_groups({row.group for row in culture_rows}, "culture"), "utf-8-sig"),
        COMMON / "cultures/antq_m4_cultures.txt": (
            render_cultures(
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
            ),
            "utf-8-sig",
        ),
        COMMON / "religion_groups/antq_m4_groups.txt": (render_religion_groups({row.group for row in religion_rows}), "utf-8-sig"),
        COMMON / "religions/antq_m4_religions.txt": (render_religions(religion_rows), "utf-8-sig"),
        COMMON / "languages/antq_m4_languages.txt": (render_languages(language_rows), "utf-8-sig"),
        ROOT / "main_menu/common/named_colors/antq_m4_colors.txt": (render_named_colors(culture_rows, religion_rows, language_rows), "utf-8-sig"),
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
