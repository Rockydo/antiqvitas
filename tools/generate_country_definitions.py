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
SYMBOLS = ROOT / "docs/vanilla_symbols"
COUNTRIES = ROOT / "in_game/setup/countries/antq_00_world.txt"
COAS = ROOT / "main_menu/common/coat_of_arms/coat_of_arms/antq_00_placeholders.txt"
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


# These are valid current-engine fallbacks for country definitions only.  They
# are not M4's historical culture/religion map: M4 replaces each of these
# references with the era's sourced culture and faith trees before those map
# modes become a scholarly deliverable.
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


def esc(value: str) -> str:
    return value.replace('"', "'")


def load_rows() -> list[dict[str, str]]:
    with ROSTER.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


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
        return TAG_PROFILES.get(row["tag"], REGION_PROFILES[row["region"]])
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
        "# M3 country definitions; M4 replaces culture/religion fallbacks with ancient trees.",
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
    lines = [
        "# Generated by tools/generate_country_definitions.py --write.",
        "# Deliberately simple M3 placeholder flags; M11 supplies sourced historical CoAs.",
    ]
    for row in rows:
        profile = profile_for(row)
        lines.extend(
            (
                "",
                f'{tags[row["tag"]]} = {{ # {row["name"]}',
                '\tpattern = "pattern_solid.dds"',
                f'\tcolor1 = "{profile.flag_primary}"',
                f'\tcolor2 = "{profile.flag_secondary}"',
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
    culture_symbols = set(json.loads((SYMBOLS / "culture.json").read_text(encoding="utf-8-sig")))
    religion_symbols = set(json.loads((SYMBOLS / "religion.json").read_text(encoding="utf-8-sig")))
    failures: list[str] = []
    for row in load_rows():
        profile = profile_for(row)
        if profile.culture not in culture_symbols:
            failures.append(f"{row['tag']}: unknown culture fallback {profile.culture}")
        if profile.religion not in religion_symbols:
            failures.append(f"{row['tag']}: unknown religion fallback {profile.religion}")
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
