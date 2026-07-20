#!/usr/bin/env python3
"""Generate the M3 country-definition, placeholder-CoA, and name layers.

The AD 1 roster deliberately retains historical design tags even where they
collide with the installed database.  This generator is the only place that
turns those design tags into the collision-safe engine tags from tag_map.json.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "docs/world_1ad/polities.csv"
TAG_MAP = ROOT / "docs/world_1ad/tag_map.json"
M4_REGIONAL_PROFILES = ROOT / "docs/m4/regional_profiles.csv"
M4_TAG_PROFILES = ROOT / "docs/m4/tag_profiles.csv"
M4_SYMBOLS = ROOT / "docs/m4/definition_symbols.json"
CORE_COAS = ROOT / "docs/m11/core_coas.csv"
COA_THEMES = ROOT / "docs/m11/coa_theme_catalog.csv"
SYMBOLS = ROOT / "docs/vanilla_symbols"
COUNTRIES = ROOT / "in_game/setup/countries/antq_00_world.txt"
COAS = ROOT / "main_menu/common/coat_of_arms/coat_of_arms/antq_00_coa_standards.txt"
LOC_ROOT = ROOT / "main_menu/localization"
LANGUAGES = (
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


@dataclass(frozen=True)
class Profile:
    culture: str
    religion: str
    rgb: tuple[int, int, int]
    flag_primary: str
    flag_secondary: str


# The M3 palette and placeholder-CoA layer is deliberately retained while M4
# replaces only the country definition's historical culture and religion.
# Keeping visual and historical profiles separate prevents a map-color choice
# from silently becoming historical population data.
REGION_PROFILES: dict[str, Profile] = {
    "Africa": Profile("nubian", "hellenism_religion", (128, 105, 58), "yellow", "black"),
    "Anatolia": Profile("greek_culture", "hellenism_religion", (62, 104, 155), "blue", "yellow"),
    "Andes": Profile("quechan_culture", "inti", (161, 91, 43), "red", "yellow"),
    "Arabia": Profile("yemeni_culture", "sunni", (80, 123, 74), "green", "white"),
    "Balkans": Profile("greek_culture", "hellenism_religion", (99, 71, 142), "purple", "yellow"),
    "Baltic": Profile("latvian", "norse", (51, 108, 114), "green", "white"),
    "Britain": Profile("welsh", "norse", (51, 116, 67), "green", "white"),
    "Caribbean-Amazon": Profile("arawak_culture", "shamanism", (37, 137, 143), "blue", "white"),
    "Caucasus": Profile("armenian_culture", "zoroastrian", (155, 87, 65), "red", "yellow"),
    "Central Asia": Profile("farsi_culture", "zoroastrian", (133, 78, 58), "red", "yellow"),
    "China": Profile("hani_culture", "mahayana", (191, 49, 38), "red", "yellow"),
    "Danube": Profile("roman_culture", "norse", (95, 124, 72), "green", "yellow"),
    "Eastern Europe": Profile("latvian", "norse", (86, 98, 130), "blue", "white"),
    "Finland": Profile("finnish", "norse", (59, 119, 132), "blue", "white"),
    "Germania": Profile("german_baltic", "norse", (80, 100, 68), "green", "yellow"),
    "India": Profile("tamil", "hindu", (178, 116, 41), "orange", "yellow"),
    "Iran": Profile("farsi_culture", "zoroastrian", (143, 42, 42), "red", "yellow"),
    "Ireland": Profile("irish", "norse", (52, 125, 78), "green", "white"),
    "Japan": Profile("korean_culture", "shinto", (185, 62, 73), "red", "white"),
    "Korea": Profile("korean_culture", "mahayana", (54, 91, 153), "blue", "white"),
    "Lanka": Profile("sinhalese", "theravada", (190, 139, 31), "yellow", "red"),
    "Levant": Profile("syriac_culture", "hellenism_religion", (128, 90, 51), "yellow", "red"),
    "Mesoamerica": Profile("nahua_culture", "mesoamerican", (43, 129, 96), "green", "yellow"),
    "Mesopotamia": Profile("syriac_culture", "zoroastrian", (117, 68, 49), "red", "yellow"),
    "North America": Profile("inuit_culture", "shamanism", (63, 109, 133), "blue", "white"),
    "Northern Andes": Profile("quechan_culture", "inti", (140, 93, 55), "red", "yellow"),
    "Oceania": Profile("tagalog_culture", "shamanism", (36, 121, 144), "blue", "white"),
    "Pontic": Profile("armenian_culture", "zoroastrian", (102, 83, 132), "purple", "yellow"),
    "Rome": Profile("roman_culture", "hellenism_religion", (125, 35, 54), "purple", "yellow"),
    "Scandinavia": Profile("swedish", "norse", (61, 104, 151), "blue", "yellow"),
    "Southeast Asia": Profile("khmer_culture", "theravada", (66, 125, 90), "green", "yellow"),
    "Steppe": Profile("mongolian_culture", "tengri", (105, 111, 119), "blue", "yellow"),
    "Tarim": Profile("hani_culture", "mahayana", (148, 102, 54), "yellow", "red"),
    "West Africa": Profile("somali_culture", "bantu_religion", (135, 96, 43), "yellow", "black"),
}

# A few historically conspicuous states need clearly recognizable map colors
# while M11's sourced coats of arms are still pending.
TAG_PROFILES: dict[str, Profile] = {
    "ROM": Profile("roman_culture", "hellenism_religion", (128, 24, 48), "purple", "yellow"),
    "PAR": Profile("farsi_culture", "zoroastrian", (121, 28, 38), "red", "yellow"),
    "HAN": Profile("hani_culture", "mahayana", (204, 42, 31), "red", "yellow"),
    "JUD": Profile("syriac_culture", "judaism", (83, 107, 154), "blue", "white"),
    "GAL": Profile("syriac_culture", "judaism", (83, 107, 154), "blue", "white"),
    "BAT": Profile("syriac_culture", "judaism", (83, 107, 154), "blue", "white"),
    "KUS": Profile("nubian", "hellenism_religion", (102, 81, 43), "yellow", "black"),
    "AKS": Profile("amhara", "bantu_religion", (111, 87, 45), "yellow", "green"),
    "MAY": Profile("mixe_culture", "mayan", (35, 122, 79), "green", "yellow"),
    "ZAP": Profile("zapotec_culture", "mesoamerican", (45, 129, 91), "green", "yellow"),
    "EPI": Profile("zoque_culture", "mesoamerican", (42, 120, 98), "green", "yellow"),
    "CHI": Profile("arawak_culture", "shamanism", (47, 112, 109), "blue", "white"),
}

# The country database adds rank-derived words such as "Empire" itself.  The
# historical roster can retain precise scholarly names while its UI label avoids
# the engine's duplicate-title warning.
DISPLAY_NAMES = {
    "ROM": "Roman Commonwealth",
    "PAR": "Parthia",
}


@dataclass(frozen=True)
class HistoricalProfile:
    culture: str
    religion: str
    source: str
    confidence: str
    note: str


@dataclass(frozen=True)
class CoaOverride:
    emblem: str
    color1: str
    color2: str
    color3: str
    emblem_color1: str
    emblem_color2: str
    emblem_color3: str
    position_x: str
    position_y: str
    scale_x: str
    scale_y: str
    source: str
    confidence: str
    note: str


def esc(value: str) -> str:
    return value.replace('"', "'")


def load_rows() -> list[dict[str, str]]:
    with ROSTER.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_historical_profiles(path: Path, key_column: str) -> dict[str, HistoricalProfile]:
    """Load source-labelled M4 profile data without burying it in code."""
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    profiles: dict[str, HistoricalProfile] = {}
    for row in rows:
        key = row.get(key_column, "").strip()
        if not key:
            raise ValueError(f"{path.relative_to(ROOT)} has a blank {key_column}")
        if key in profiles:
            raise ValueError(f"{path.relative_to(ROOT)} repeats {key_column} {key}")
        required = ("culture", "religion", "source", "confidence", "note")
        missing = [field for field in required if not row.get(field, "").strip()]
        if missing:
            raise ValueError(
                f"{path.relative_to(ROOT)} {key}: blank required fields {', '.join(missing)}"
            )
        profiles[key] = HistoricalProfile(
            row["culture"].strip(),
            row["religion"].strip(),
            row["source"].strip(),
            row["confidence"].strip(),
            row["note"].strip(),
        )
    return profiles


def load_coa_overrides() -> dict[str, CoaOverride]:
    required = (
        "tag", "emblem", "color1", "color2", "color3", "emblem_color1",
        "emblem_color2", "emblem_color3", "position_x", "position_y",
        "scale_x", "scale_y", "source", "confidence", "note",
    )
    with CORE_COAS.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    overrides: dict[str, CoaOverride] = {}
    for row in rows:
        missing = [field for field in required if not row.get(field, "").strip()]
        if missing:
            raise ValueError(f"{CORE_COAS.relative_to(ROOT)} has blank fields: {', '.join(missing)}")
        tag = row["tag"].strip()
        if tag in overrides:
            raise ValueError(f"{CORE_COAS.relative_to(ROOT)} repeats tag {tag}")
        overrides[tag] = CoaOverride(*[row[field].strip() for field in required[1:]])
    return overrides


def load_coa_themes() -> dict[str, CoaOverride]:
    """Load regional UI standards used where no direct-country review exists."""
    required = (
        "region", "emblem", "color1", "color2", "color3", "emblem_color1",
        "emblem_color2", "emblem_color3", "position_x", "position_y",
        "scale_x", "scale_y", "source", "confidence", "note",
    )
    with COA_THEMES.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    themes: dict[str, CoaOverride] = {}
    for row in rows:
        missing = [field for field in required if not row.get(field, "").strip()]
        if missing:
            raise ValueError(f"{COA_THEMES.relative_to(ROOT)} has blank fields: {', '.join(missing)}")
        region = row["region"].strip()
        if region in themes:
            raise ValueError(f"{COA_THEMES.relative_to(ROOT)} repeats region {region}")
        themes[region] = CoaOverride(*[row[field].strip() for field in required[1:]])
    return themes


def historical_profile_for(row: dict[str, str]) -> HistoricalProfile:
    regions = load_historical_profiles(M4_REGIONAL_PROFILES, "region")
    tags = load_historical_profiles(M4_TAG_PROFILES, "tag")
    try:
        return tags.get(row["tag"], regions[row["region"]])
    except KeyError as exc:
        raise ValueError(f"no M4 historical profile for {row.get('tag')} / {row.get('region')}") from exc


def load_engine_tags() -> dict[str, str]:
    payload = json.loads(TAG_MAP.read_text(encoding="utf-8"))
    return {entry["design_tag"]: entry["engine_tag"] for entry in payload["entries"]}


def variant_color(profile: Profile, design_tag: str) -> tuple[int, int, int]:
    """Keep regional families visible while avoiding same-color adjacent tags."""
    if design_tag in {"ROM", "PAR", "HAN"}:
        return profile.rgb
    digest = hashlib.sha256(design_tag.encode("ascii")).digest()
    return tuple(max(18, min(237, channel + (byte % 29) - 14)) for channel, byte in zip(profile.rgb, digest))


def profile_for(row: dict[str, str]) -> Profile:
    try:
        visual = TAG_PROFILES.get(row["tag"], REGION_PROFILES[row["region"]])
        historical = historical_profile_for(row)
        return Profile(
            historical.culture,
            historical.religion,
            visual.rgb,
            visual.flag_primary,
            visual.flag_secondary,
        )
    except KeyError as exc:
        raise ValueError(f"no country profile for {row.get('tag')} / {row.get('region')}") from exc


def adjective(name: str) -> str:
    special = {
        "Roman Empire": "Roman",
        "Western Han": "Han",
        "Parthian Empire": "Parthian",
        "Herodian Judea": "Judean",
        "Herodian Galilee-Peraea": "Galilean",
        "Herodian Batanea": "Bataean",
        "Wa": "Wa",
        "Aksum": "Aksumite",
        "Kush": "Kushite",
        "Goguryeo": "Goguryeo",
    }
    return special.get(name, name)


def display_name(design_tag: str, name: str) -> str:
    return DISPLAY_NAMES.get(design_tag, name)


def country_definitions(rows: list[dict[str, str]], tags: dict[str, str]) -> str:
    lines = [
        "# Generated by tools/generate_country_definitions.py --write.",
        "# M3 visuals plus source-labelled M4 ancient culture/religion profiles.",
    ]
    for row in rows:
        profile = profile_for(row)
        red, green, blue = variant_color(profile, row["tag"])
        lines.extend(
            (
                "",
                f'{tags[row["tag"]]} = {{ # {row["name"]}; {row["source"]}',
                f"\tcolor = rgb {{ {red} {green} {blue} }}",
                f"\tcolor2 = rgb {{ {255 - red} {255 - green} {255 - blue} }}",
                "",
                f"\tculture_definition = {profile.culture}",
                f"\treligion_definition = {profile.religion}",
                "\tis_historic = yes",
                "}",
            )
        )
    return "\n".join(lines) + "\n"


def placeholder_coas(rows: list[dict[str, str]], tags: dict[str, str]) -> str:
    overrides = load_coa_overrides()
    themes = load_coa_themes()
    lines = [
        "# Generated by tools/generate_country_definitions.py --write.",
        "# Source-labelled M11 period-inspired UI standards, not historical flag reconstructions.",
    ]
    for row in rows:
        standard = overrides.get(row["tag"], themes[row["region"]])
        lines.extend(
            (
                "",
                f'{tags[row["tag"]]} = {{ # {row["name"]}; {standard.source}',
                '\tpattern = "pattern_solid.dds"',
                f'\tcolor1 = "{standard.color1}"',
                f'\tcolor2 = "{standard.color2}"',
                f'\tcolor3 = "{standard.color3}"',
                "\tcolored_emblem = {",
                f'\t\ttexture = "{standard.emblem}"',
                f'\t\tcolor1 = {standard.emblem_color1}',
                f'\t\tcolor2 = {standard.emblem_color2}',
                f'\t\tcolor3 = {standard.emblem_color3}',
                f'\t\tinstance = {{ position = {{ {standard.position_x} {standard.position_y} }} scale = {{ {standard.scale_x} {standard.scale_y} }} }}',
                "\t}",
                "}",
            )
        )
    return "\n".join(lines) + "\n"


def localization(rows: list[dict[str, str]], tags: dict[str, str], language: str) -> str:
    lines = [
        f"l_{language}:",
        " # Generated from the AD 1 roster. English text is intentionally mirrored by plan.",
    ]
    for row in rows:
        engine_tag = tags[row["tag"]]
        name = esc(display_name(row["tag"], row["name"]))
        lines.append(f' {engine_tag}: "{name}"')
        lines.append(f' {engine_tag}_ADJ: "{esc(adjective(row["name"]))}"')
    return "\n".join(lines) + "\n"


def outputs() -> dict[Path, tuple[str, str]]:
    rows = load_rows()
    tags = load_engine_tags()
    roster_tags = {row["tag"] for row in rows}
    if roster_tags != set(tags):
        missing = sorted(roster_tags - set(tags))
        extra = sorted(set(tags) - roster_tags)
        raise ValueError(f"tag map mismatch; missing={missing}, extra={extra}")
    result: dict[Path, tuple[str, str]] = {
        COUNTRIES: (country_definitions(rows, tags), "utf-8-sig"),
        COAS: (placeholder_coas(rows, tags), "utf-8"),
    }
    for language in LANGUAGES:
        path = LOC_ROOT / language / f"antq_m3_countries_l_{language}.yml"
        result[path] = (localization(rows, tags, language), "utf-8-sig")
    return result


def validate_references() -> list[str]:
    m4_symbols = json.loads(M4_SYMBOLS.read_text(encoding="utf-8"))
    culture_symbols = set(m4_symbols["cultures"])
    religion_symbols = set(m4_symbols["religions"])
    rows = load_rows()
    roster_regions = {row["region"] for row in rows}
    roster_tags = {row["tag"] for row in rows}
    regional_profiles = load_historical_profiles(M4_REGIONAL_PROFILES, "region")
    tag_profiles = load_historical_profiles(M4_TAG_PROFILES, "tag")
    coa_overrides = load_coa_overrides()
    coa_themes = load_coa_themes()
    local_paths = json.loads((ROOT / "config/local_paths.json").read_text(encoding="utf-8"))
    colored_emblems = Path(local_paths["game_dir"]) / "game/main_menu/gfx/coat_of_arms/colored_emblems"
    failures: list[str] = []
    missing_regions = sorted(roster_regions - set(regional_profiles))
    extra_regions = sorted(set(regional_profiles) - roster_regions)
    if missing_regions:
        failures.append(f"M4 regional profiles missing roster regions: {', '.join(missing_regions)}")
    if extra_regions:
        failures.append(f"M4 regional profiles have unknown regions: {', '.join(extra_regions)}")
    unknown_tags = sorted(set(tag_profiles) - roster_tags)
    if unknown_tags:
        failures.append(f"M4 tag profiles have unknown roster tags: {', '.join(unknown_tags)}")
    unknown_coa_tags = sorted(set(coa_overrides) - roster_tags)
    if unknown_coa_tags:
        failures.append(f"M11 core CoAs have unknown roster tags: {', '.join(unknown_coa_tags)}")
    missing_theme_regions = sorted(roster_regions - set(coa_themes))
    extra_theme_regions = sorted(set(coa_themes) - roster_regions)
    if missing_theme_regions:
        failures.append(f"M11 CoA themes missing roster regions: {', '.join(missing_theme_regions)}")
    if extra_theme_regions:
        failures.append(f"M11 CoA themes have unknown regions: {', '.join(extra_theme_regions)}")
    for layer, standards in (("core CoA", coa_overrides), ("CoA theme", coa_themes)):
        for name, standard in standards.items():
            if standard.confidence not in {"secure", "contested"}:
                failures.append(f"M11 {layer} {name}: invalid confidence {standard.confidence}")
            if not standard.emblem.startswith("ce_") or not standard.emblem.endswith(".dds"):
                failures.append(f"M11 {layer} {name}: invalid colored-emblem name {standard.emblem}")
            if not (colored_emblems / standard.emblem).is_file():
                failures.append(f"M11 {layer} {name}: absent local colored emblem {standard.emblem}")
    for row in rows:
        profile = profile_for(row)
        if profile.culture not in culture_symbols:
            failures.append(f"{row['tag']}: unknown M4 culture {profile.culture}")
        if profile.religion not in religion_symbols:
            failures.append(f"{row['tag']}: unknown M4 religion {profile.religion}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    failures = validate_references()
    expected = outputs()
    if args.write:
        if failures:
            print("country_definitions: FAIL", file=sys.stderr)
            print("\n".join(f"  - {failure}" for failure in failures), file=sys.stderr)
            return 1
        for path, (content, encoding) in expected.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding=encoding, newline="\n")
            print(f"country_definitions: wrote {path.relative_to(ROOT)}")
        return 0
    for path, (content, encoding) in expected.items():
        if not path.is_file():
            failures.append(f"missing generated output {path.relative_to(ROOT)}")
            continue
        actual = path.read_text(encoding=encoding)
        if actual != content:
            failures.append(f"stale generated output {path.relative_to(ROOT)}")
    if failures:
        print("country_definitions: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return 1
    print(f"country_definitions: PASS ({len(load_rows())} definitions; {len(LANGUAGES)} mirrored localizations)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
