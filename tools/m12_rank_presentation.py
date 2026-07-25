#!/usr/bin/env python3
"""Generate and validate period-appropriate AD 1 polity-rank presentation."""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATHS = ROOT / "config/local_paths.json"
ROSTER = ROOT / "docs/world_1ad/polities.csv"
TAG_MAP = ROOT / "docs/world_1ad/tag_map.json"
START = ROOT / "main_menu/setup/start/10_countries.txt"
LEDGER = ROOT / "docs/m12/rank_presentation.csv"
CUSTOM = ROOT / "in_game/common/customizable_localization/country_ranks.txt"
CLIENTS = (
    "english", "french", "german", "spanish", "polish", "russian",
    "braz_por", "simp_chinese", "japanese", "korean", "turkish",
)
EMPIRES = frozenset({"ROM", "PAR", "HAN"})
CITY_STATES = frozenset({
    "TEO", "CUI", "ZAP", "REC", "TIW", "NAZ", "ANU", "DJN",
})
ETHNIC_POLITIES = frozenset({
    "CRU", "CHT", "FRI", "LAN", "SEM", "HER", "QUA", "GUT", "VAN",
    "RUG", "BRG", "ANG", "SAX", "JUT", "CAT", "TRI", "ICE", "BRI",
    "ATB", "SIL", "ORD", "DUM", "GET", "BAS", "XIA", "WHU",
})
COMMUNITY_MARKERS = (
    "Communities", "Societies", "Horizon", "Sphere", "Precursors",
    "Culture", "Basketmaker", "Dorset",
)
LEAGUE_MARKERS = ("Polities", "Cities")
LEDGER_FIELDS = (
    "design_tag", "engine_tag", "name", "kind", "technical_rank",
    "government_context", "presentation_class", "display_rank",
    "ruler_title", "source", "confidence", "note",
)


@dataclass(frozen=True)
class RankStyle:
    key: str
    rank: str
    adjective: str
    ruler_male: str
    ruler_female: str


STYLES = {
    "roman_imperium": RankStyle(
        "roman_imperium", "Imperium", "imperial", "Princeps", "Princeps",
    ),
    "arsacid_kingdom": RankStyle(
        "arsacid_kingdom", "Kingdom of Kings", "Arsacid", "King of Kings", "Queen of Queens",
    ),
    "han_dynasty": RankStyle(
        "han_dynasty", "Dynasty", "imperial", "Emperor", "Empress",
    ),
    "client_kingdom": RankStyle(
        "client_kingdom", "Client Kingdom", "client-royal", "King", "Queen",
    ),
    "kingdom": RankStyle("kingdom", "Kingdom", "royal", "King", "Queen"),
    "realm": RankStyle("realm", "Realm", "realm", "Ruler", "Ruler"),
    "confederation": RankStyle(
        "confederation", "Confederation", "confederated", "Paramount Leader", "Paramount Leader",
    ),
    "city_state": RankStyle(
        "city_state", "City-State", "civic", "First Magistrate", "First Magistrate",
    ),
    "league": RankStyle(
        "league", "League", "federal", "Presiding Leader", "Presiding Leader",
    ),
    "people": RankStyle("people", "People", "communal", "Leader", "Leader"),
    "communities": RankStyle(
        "communities", "Lands", "communal", "Spokesperson", "Spokesperson",
    ),
    "polities": RankStyle(
        "polities", "Lands", "regional", "Leading House", "Leading House",
    ),
    "empire": RankStyle("empire", "Empire", "imperial", "Emperor", "Empress"),
    "great_realm": RankStyle(
        "great_realm", "Great Realm", "great-realm", "Sovereign", "Sovereign",
    ),
    "regional_polity": RankStyle(
        "regional_polity", "Regional Polity", "regional", "High Leader", "High Leader",
    ),
    "local_polity": RankStyle(
        "local_polity", "Local Polity", "local", "Leader", "Leader",
    ),
    "successor": RankStyle(
        "successor", "Successor", "successorial", "Successor", "Successor",
    ),
}


def game_dir() -> Path:
    data = json.loads(PATHS.read_text(encoding="utf-8-sig"))
    return Path(data["game_dir"]) / "game"


def rank_for(row: dict[str, str]) -> str:
    if row["tag"] in EMPIRES:
        return "rank_empire"
    if row["kind"] == "sop":
        return "rank_county"
    return "rank_kingdom"


def presentation_class(row: dict[str, str]) -> str:
    tag, name, kind = row["tag"], row["name"], row["kind"]
    if tag == "ROM":
        return "roman_imperium"
    if tag == "PAR":
        return "arsacid_kingdom"
    if tag == "HAN":
        return "han_dynasty"
    if kind == "subject":
        return "client_kingdom"
    if "Confederation" in name:
        return "confederation"
    if kind == "sop":
        if any(marker in name for marker in COMMUNITY_MARKERS):
            return "communities"
        if any(marker in name for marker in LEAGUE_MARKERS):
            return "polities"
        return "people"
    if any(marker in name for marker in LEAGUE_MARKERS):
        return "league"
    if tag in CITY_STATES:
        return "city_state"
    if tag in ETHNIC_POLITIES:
        return "people"
    if "Kingdom" in name or tag in {"MCM", "DAC", "PND", "KUS"}:
        return "kingdom"
    return "realm"


def load_rows() -> list[dict[str, str]]:
    with ROSTER.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    mapping = {
        row["design_tag"]: row["engine_tag"]
        for row in json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))["entries"]
    }
    blocks = start_country_blocks()
    output: list[dict[str, str]] = []
    for row in rows:
        style_key = presentation_class(row)
        style = STYLES[style_key]
        engine_tag = mapping[row["tag"]]
        block = blocks.get(engine_tag, "")
        government_match = re.search(
            r"\n\s*government = \{\s*\n\s*type = ([a-z0-9_]+)",
            block,
        )
        government_context = (
            government_match.group(1) if government_match is not None else "missing"
        )
        output.append({
            "design_tag": row["tag"],
            "engine_tag": engine_tag,
            "name": row["name"],
            "kind": row["kind"],
            "technical_rank": rank_for(row),
            "government_context": government_context,
            "presentation_class": style_key,
            "display_rank": style.rank,
            "ruler_title": f"{style.ruler_male}/{style.ruler_female}",
            "source": row["source"],
            "confidence": row["confidence"],
            "note": (
                "Numeric rank retained for engine balance; explicit flavor resolver "
                "prevents medieval raw-rank presentation."
            ),
        })
    return output


def write_ledger(rows: list[dict[str, str]]) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LEDGER_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def trigger_block(tags: list[str]) -> list[str]:
    if len(tags) == 1:
        return [f"\t\t\ttag = {tags[0]}"]
    return [
        "\t\t\tOR = {",
        *(f"\t\t\t\ttag = {tag}" for tag in tags),
        "\t\t\t}",
    ]


def render_custom(rows: list[dict[str, str]]) -> str:
    groups: dict[str, list[str]] = {}
    for row in rows:
        groups.setdefault(row["presentation_class"], []).append(row["engine_tag"])
    lines = [
        "# Generated by tools/m12_rank_presentation.py --write.",
        "# Explicit AD 1 roster resolver; numeric rank remains an engine balance tier.",
        "country_flavor = {",
        "\ttype = country",
        "",
    ]
    for style_key, tags in groups.items():
        lines.extend((
            "\ttext = {",
            f"\t\tlocalization_key = antq_rank_{style_key}",
            "\t\ttrigger = {",
        ))
        lines.extend(trigger_block(sorted(tags)))
        lines.extend(("\t\t}", "\t}", ""))
    # Installed scripts set these two variables and Jomini requires their
    # original live resolver references even though no AD 1 roster tag can
    # reach the medieval flavor branches.  Keeping the references after every
    # explicit roster branch preserves a clean log without changing display.
    lines.extend((
        "\ttext = {",
        "\t\tlocalization_key = rank_victual_brothers",
        "\t\ttrigger = { has_variable = VTB_victual_brothers }",
        "\t}",
        "",
        "\ttext = {",
        "\t\tlocalization_key = country_flavor_france_dauphin",
        "\t\ttrigger = { has_variable = adopted_the_title_dauphin }",
        "\t}",
        "",
    ))
    for style_key, trigger in (
        ("empire", "country_rank_is_empire = yes"),
        ("great_realm", "country_rank_is_kingdom = yes"),
        ("regional_polity", "country_rank_is_duchy = yes"),
    ):
        lines.extend((
            "\ttext = {",
            f"\t\tlocalization_key = antq_rank_{style_key}",
            f"\t\ttrigger = {{ {trigger} }}",
            "\t}",
            "",
        ))
    lines.extend((
        "\ttext = {",
        "\t\tlocalization_key = antq_rank_local_polity",
        "\t\tfallback = yes",
        "\t}",
        "}",
        "country_flavor_prefix = { parent = country_flavor suffix = \"_prefix\" log_loc_errors = no if_invalid_loc = return_empty }",
        "country_flavor_ADJ = { parent = country_flavor suffix = \"_ADJ\" log_loc_errors = no if_invalid_loc = fallback_to_next_entry }",
        "country_flavor_ruler_suffix_female = { parent = country_flavor suffix = \"_ruler_suffix_female\" log_loc_errors = no if_invalid_loc = return_empty }",
        "country_flavor_ruler_suffix_male = { parent = country_flavor suffix = \"_ruler_suffix_male\" log_loc_errors = no if_invalid_loc = return_empty }",
        "country_flavor_ruler_female = { parent = country_flavor suffix = \"_ruler_female\" log_loc_errors = no if_invalid_loc = fallback_to_next_entry }",
        "country_flavor_ruler_male = { parent = country_flavor suffix = \"_ruler_male\" log_loc_errors = no if_invalid_loc = fallback_to_next_entry }",
        "",
        "country_flavor_heir = {",
        "\ttype = country",
        "\ttext = { localization_key = antq_rank_successor fallback = yes }",
        "}",
        "country_flavor_heir_suffix = { parent = country_flavor_heir suffix = \"_suffix\" log_loc_errors = no if_invalid_loc = return_empty }",
        "country_flavor_heir_suffix_female = { parent = country_flavor_heir suffix = \"_suffix_female\" log_loc_errors = no if_invalid_loc = return_empty }",
        "country_flavor_heir_female = { parent = country_flavor_heir suffix = \"_female\" log_loc_errors = no if_invalid_loc = return_loc_key }",
        "",
        "country_flavor_regent = {",
        "\ttype = country",
        "\ttext = { localization_key = antq_rank_regent fallback = yes }",
        "}",
        "country_flavor_regent_female = { parent = country_flavor_regent suffix = \"_female\" log_loc_errors = no if_invalid_loc = return_loc_key }",
        "",
        "country_flavor_courtier = {",
        "\ttype = country",
        "\ttext = { localization_key = antq_rank_courtier fallback = yes }",
        "}",
        "country_flavor_courtier_female = { parent = country_flavor_courtier suffix = \"_female\" log_loc_errors = no if_invalid_loc = return_loc_key }",
        "",
        "country_flavor_consort = {",
        "\ttype = country",
        "\ttext = { localization_key = antq_rank_consort fallback = yes }",
        "}",
        "country_flavor_consort_suffix = { parent = country_flavor_consort suffix = \"_suffix\" log_loc_errors = no if_invalid_loc = return_empty }",
        "country_flavor_consort_suffix_female = { parent = country_flavor_consort suffix = \"_suffix_female\" log_loc_errors = no if_invalid_loc = return_empty }",
        "country_flavor_consort_female = { parent = country_flavor_consort suffix = \"_female\" log_loc_errors = no if_invalid_loc = return_loc_key }",
        "",
    ))
    return "\n".join(lines)


def rank_localization_entries() -> list[str]:
    lines: list[str] = []
    used = (
        "roman_imperium", "arsacid_kingdom", "han_dynasty", "client_kingdom",
        "kingdom", "realm", "confederation", "city_state", "league", "people",
        "communities", "polities", "empire", "great_realm", "regional_polity",
        "local_polity", "successor",
    )
    for key in used:
        style = STYLES[key]
        lines.extend((
            f' antq_rank_{key}: "{style.rank}"',
            f' antq_rank_{key}_ADJ: "{style.adjective}"',
            f' antq_rank_{key}_ruler_male: "{style.ruler_male}"',
            f' antq_rank_{key}_ruler_female: "{style.ruler_female}"',
        ))
    lines.extend((
        ' antq_rank_successor_female: "Successor"',
        ' antq_rank_regent: "Regent"',
        ' antq_rank_regent_female: "Regent"',
        ' antq_rank_courtier: "Courtier"',
        ' antq_rank_courtier_female: "Courtier"',
        ' antq_rank_consort: "Consort"',
        ' antq_rank_consort_female: "Consort"',
    ))
    return lines


RAW_REPLACEMENTS = {
    "rank_county": "Local Polity",
    "rank_county_ADJ": "local",
    "rank_county_ruler_male": "Leader",
    "rank_county_ruler_female": "Leader",
    "rank_county_tribe": "People",
    "rank_county_tribe_ADJ": "communal",
    "rank_county_tribe_ruler_male": "Leader",
    "rank_county_tribe_ruler_female": "Leader",
    "rank_duchy": "Regional Polity",
    "rank_duchy_ADJ": "regional",
    "rank_duchy_ruler_male": "High Leader",
    "rank_duchy_ruler_female": "High Leader",
    "rank_duchy_tribe": "Confederation",
    "rank_duchy_tribe_ADJ": "confederated",
    "rank_duchy_tribe_ruler_male": "Paramount Leader",
    "rank_duchy_tribe_ruler_female": "Paramount Leader",
}
LOC_LINE = re.compile(r'^(?P<indent>\s*)(?P<key>[^:#\s][^:]*):(?P<version>\d+)?\s+".*"\s*$')


def render_government_localization(client: str) -> str:
    source = (
        game_dir()
        / "main_menu/localization/english/government_names_l_english.yml"
    )
    lines = source.read_text(encoding="utf-8-sig").splitlines()
    output = [f"l_{client}:"]
    replaced: set[str] = set()
    for line in lines[1:]:
        match = LOC_LINE.match(line)
        if match and match.group("key") in RAW_REPLACEMENTS:
            key = match.group("key")
            output.append(f' {key}: "{RAW_REPLACEMENTS[key]}"')
            replaced.add(key)
        else:
            # Exact-name mirroring is required for raw-rank precedence.  Strip
            # the one unused post-476 adjective while preserving its key as an
            # inert engine adapter.
            sanitized = re.sub(
                r'^( country_rank_colony_ADJ:)\s+".*"\s*$',
                r'\1 "dependent"',
                line,
            )
            sanitized = re.sub(
                r"#placeholder XX #!",
                "#italic none listed#!",
                sanitized,
                flags=re.IGNORECASE,
            )
            output.append(sanitized)
    for key in sorted(set(RAW_REPLACEMENTS) - replaced):
        output.append(f' {key}: "{RAW_REPLACEMENTS[key]}"')
    output.extend(("", "# ANTIQVITAS explicit AD 1 rank resolver", *rank_localization_entries(), ""))
    return "\n".join(output)


def render_interaction_localization(client: str) -> str:
    source = (
        game_dir()
        / "main_menu/localization/english/country_interactions_l_english.yml"
    )
    lines = source.read_text(encoding="utf-8-sig").splitlines()
    output = [f"l_{client}:"]
    for line in lines[1:]:
        match = LOC_LINE.match(line)
        if match and match.group("key") == "county_privileges":
            output.append(' county_privileges: "Local-Polity Privileges"')
        elif match and match.group("key") == "elevate_county":
            output.append(' elevate_county: "Elevate Local Polity"')
        else:
            # These exact mirrors retain inactive engine keys but must never
            # reintroduce a visible early-modern adjective.
            value = line
            if ":" in line:
                key, tail = line.split(":", 1)
                tail = re.sub(r"\bColonial\b", "Chartered", tail)
                tail = re.sub(r"\bcolonial\b", "chartered", tail)
                value = f"{key}:{tail}"
            output.append(value)
    output.append("")
    return "\n".join(output)


def write_localization() -> None:
    for client in CLIENTS:
        base = ROOT / f"main_menu/localization/{client}"
        base.mkdir(parents=True, exist_ok=True)
        (base / f"government_names_l_{client}.yml").write_text(
            render_government_localization(client),
            encoding="utf-8-sig",
            newline="\n",
        )
        (base / f"country_interactions_l_{client}.yml").write_text(
            render_interaction_localization(client),
            encoding="utf-8-sig",
            newline="\n",
        )


def write() -> None:
    rows = load_rows()
    write_ledger(rows)
    CUSTOM.parent.mkdir(parents=True, exist_ok=True)
    CUSTOM.write_text(render_custom(rows), encoding="utf-8-sig", newline="\n")
    write_localization()
    print("m12_rank_presentation: wrote 229 polity classifications, exact resolver, and 22 client mirrors")


def start_country_blocks() -> dict[str, str]:
    text = START.read_text(encoding="utf-8-sig")
    matches = list(re.finditer(r"^\t\t([A-Z0-9]{3}) = \{ #", text, re.MULTILINE))
    blocks: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks[match.group(1)] = text[match.start():end]
    return blocks


def validate() -> bool:
    failures: list[str] = []
    try:
        rows = load_rows()
        if len(rows) != 229 or len({row["engine_tag"] for row in rows}) != 229:
            failures.append("rank ledger must cover exactly 229 unique engine tags")
        expected_counts = {"rank_county": 133, "rank_kingdom": 93, "rank_empire": 3}
        counts = {
            rank: sum(row["technical_rank"] == rank for row in rows)
            for rank in expected_counts
        }
        if counts != expected_counts:
            failures.append(f"technical rank distribution changed: {counts}")
        expected_ledger = rows
        if not LEDGER.is_file():
            failures.append(f"missing {LEDGER.relative_to(ROOT)}")
        else:
            with LEDGER.open(encoding="utf-8-sig", newline="") as handle:
                actual = list(csv.DictReader(handle))
            if actual != expected_ledger:
                failures.append(f"stale {LEDGER.relative_to(ROOT)}")
        expected_custom = render_custom(rows)
        if (
            not CUSTOM.is_file()
            or not CUSTOM.read_bytes().startswith(b"\xef\xbb\xbf")
            or CUSTOM.read_text(encoding="utf-8-sig") != expected_custom
        ):
            failures.append(f"stale or missing {CUSTOM.relative_to(ROOT)}")
        blocks = start_country_blocks()
        for row in rows:
            block = blocks.get(row["engine_tag"])
            if block is None:
                failures.append(f"start manager lacks {row['engine_tag']}")
                continue
            if f"country_rank = {row['technical_rank']}" not in block:
                failures.append(
                    f"{row['design_tag']}/{row['engine_tag']} lacks expected {row['technical_rank']}"
                )
            if row["government_context"] == "missing":
                failures.append(
                    f"{row['design_tag']}/{row['engine_tag']} has no resolved government context"
                )
        for client in CLIENTS:
            for filename, expected in (
                (
                    f"government_names_l_{client}.yml",
                    render_government_localization(client),
                ),
                (
                    f"country_interactions_l_{client}.yml",
                    render_interaction_localization(client),
                ),
            ):
                path = ROOT / f"main_menu/localization/{client}/{filename}"
                if not path.is_file():
                    failures.append(f"missing exact localization mirror {path.relative_to(ROOT)}")
                    continue
                raw = path.read_bytes()
                if not raw.startswith(b"\xef\xbb\xbf"):
                    failures.append(f"missing UTF-8 BOM: {path.relative_to(ROOT)}")
                if raw.decode("utf-8-sig") != expected:
                    failures.append(f"stale exact localization mirror {path.relative_to(ROOT)}")
        english = (
            ROOT / "main_menu/localization/english/government_names_l_english.yml"
        ).read_text(encoding="utf-8-sig")
        for key, value in RAW_REPLACEMENTS.items():
            if f' {key}: "{value}"' not in english:
                failures.append(f"raw rank adapter not replaced: {key}")
        for forbidden in (
            ' rank_county: "County"', ' rank_duchy: "Duchy"',
            ' rank_county_ruler_male: "Count"', ' rank_duchy_ruler_male: "Duke"',
        ):
            if forbidden in english:
                failures.append(f"medieval raw rank remains: {forbidden.strip()}")
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        failures.append(str(exc))
    if failures:
        print("m12_rank_presentation: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return False
    classes = len({row["presentation_class"] for row in load_rows()})
    print(
        "m12_rank_presentation: PASS "
        f"(229 tags; {classes} period classes; no raw County/Count/Duchy/Duke)"
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.write:
            write()
            return 0
        return 0 if validate() else 1
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"m12_rank_presentation: FAIL\n  - {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
