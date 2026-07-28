#!/usr/bin/env python3
"""Validate the sourced AD 1 Finland-to-Altai granularity pass."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "docs/world_1ad/polities.csv"
TAG_MAP = ROOT / "docs/world_1ad/tag_map.json"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
PROFILES = ROOT / "docs/m4/tag_profiles.csv"
GOVERNMENTS = ROOT / "docs/m6/governments.csv"
PRIVILEGES = ROOT / "docs/m6/privileges.csv"
LAWS = ROOT / "docs/m6/laws.csv"
OVERLAYS = ROOT / "docs/m6/regional_government_overlays.csv"
COAS = ROOT / "docs/m11/core_coas.csv"
PRIVILEGE_ART = ROOT / "docs/m11/direct_privilege_icons.csv"
HISTORIES = ROOT / "docs/m12/country_history_agendas.csv"
RANKS = ROOT / "docs/m12/rank_presentation.csv"
START_POPS = ROOT / "main_menu/setup/start/06_pops.txt"
LEDGER = ROOT / "docs/m12/eastern_granularity.csv"
LANGUAGES = (
    "english", "french", "german", "spanish", "polish", "russian",
    "braz_por", "simp_chinese", "japanese", "korean", "turkish",
)
EXPECTED = {
    "PRZ": ("Greater-Poland Przeworsk Group", 35),
    "LPR": ("Lesser-Poland Przeworsk Group", 40),
    "ILM": ("Msta-Ilmen Late Dyakovo Horizon", 49),
    "PLH": ("Pskov-Luga Striated Pottery Group", 51),
    "BLF": ("Beloe-Mologa Late Dyakovo Horizon", 33),
    "MOK": ("Moskva-Oka Late Dyakovo Culture", 59),
    "UVF": ("Nizhny-Novgorod Gorodets Group", 31),
    "UVD": ("Upper Volga Late Dyakovo Horizon", 47),
    "KLY": ("Klyazma Late Dyakovo Horizon", 31),
    "WHT": ("Late Kargopol Culture", 29),
    "MZN": ("Late Belomorye Culture", 7),
    "VYG": ("Pidzh Culture", 27),
    "MRV": ("Sura-Volga Gorodets Culture", 43),
    "TGD": ("Tsna-Upper Don Gorodets Horizon", 41),
    "SMD": ("Smolensk Dnieper-Dvina Group", 46),
    "RZM": ("Oka-Moksha Gorodets Culture", 45),
    "BLR": ("Upper Dnieper-Dvina Culture", 56),
    "NEM": ("Upper Neman Striated Pottery Group", 39),
    "PDL": ("Podolian Lipița Group", 25),
    "RLG": ("Red-Ruthenian Lipița Group", 36),
    "DNP": ("Desna Zarubintsy Group", 39),
    "RBD": ("Right-Bank Zarubintsy Group", 39),
    "LBD": ("Left-Bank Zarubintsy Group", 23),
    "KRL": ("Ladoga Early Iron-Age Horizon", 22),
    "PRM": ("Middle Kama Glyadenovo Culture", 36),
    "VYP": ("Vyatka Pyanobor Horizon", 33),
    "VLF": ("Lower Kama Pyanobor Culture", 51),
    "SUG": ("Kara-Abyz Culture", 26),
    "SMY": ("Dzhudzhydyag Culture", 3),
    "SRG": ("Omsk-Ishim Sargat Culture", 42),
    "AKL": ("Forest-Steppe Altai Kulay Group", 21),
    "ALT": ("Altai Xiongnu-Contact Horizon", 33),
    "KUL": ("Kulay Horizon", 19),
    "UGR": ("Lower Irtysh Kulay Horizon", 24),
    "SIB": ("Tes-Tashtyk Transition", 3),
}
REQUIRED_PRIVILEGES = {
    "antq_przeworsk_smithing_households",
    "antq_dyakovo_hillfort_households",
    "antq_gorodets_rampart_custodians",
    "antq_northern_seasonal_rounds",
    "antq_dnieper_river_brokers",
    "antq_kama_sanctuary_custodians",
    "antq_pyanobor_mortuary_households",
    "antq_sargat_kurgan_retinues",
    "antq_altai_contact_caravans",
    "antq_kulay_casting_households",
}
REQUIRED_LAWS = {
    "antq_przeworsk_production_law",
    "antq_dyakovo_settlement_law",
    "antq_gorodets_fortification_law",
    "antq_northern_round_law",
    "antq_dnieper_exchange_law",
    "antq_kama_ritual_law",
    "antq_pyanobor_mortuary_law",
    "antq_sargat_retinue_law",
    "antq_altai_contact_law",
    "antq_kulay_casting_law",
}
EXPECTED_OVERLAYS = {
    "antq_przeworsk_material_layer": {"PRZ", "LPR"},
    "antq_dyakovo_hillfort_layer": {"ILM", "PLH", "BLF", "MOK", "UVD", "KLY"},
    "antq_gorodets_rampart_layer": {"UVF", "MRV", "TGD", "RZM"},
    "antq_northern_round_layer": {"WHT", "MZN", "VYG", "KRL", "SMY"},
    "antq_dnieper_exchange_layer": {"SMD", "BLR", "NEM", "PDL", "RLG", "DNP", "RBD", "LBD"},
    "antq_middle_kama_ritual_layer": {"PRM"},
    "antq_pyanobor_household_layer": {"VYP", "VLF", "SUG"},
    "antq_sargat_retinue_layer": {"SRG"},
    "antq_altai_contact_layer": {"AKL", "ALT"},
    "antq_kulay_casting_layer": {"KUL", "UGR", "SIB"},
}
FORBIDDEN = re.compile(r"\b(?:societies|communities|land of|generic|placeholder)\b", re.I)
ANACHRONISTIC_AGENDA = re.compile(
    r"\b(?:renaissance|feudal|medieval|gunpowder|colonial|reformation)\b", re.I
)
POP_CULTURE = re.compile(
    r"(?m)^\t(?P<location>[a-z0-9_]+) = \{\r?\n"
    r"\t\tdefine_pop = \{[^\r\n]*\bculture = (?P<culture>[a-z0-9_]+)"
)
FIELDS = (
    "design_tag", "engine_tag", "name", "map_capital", "location_count",
    "culture", "religion", "government_type", "reform", "emblem",
    "source", "confidence",
)


def rows(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8-sig")
    payload = "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith("#")
    )
    return list(csv.DictReader(io.StringIO(payload)))


def keyed(path: Path, field: str) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in rows(path):
        key = row[field]
        if key in result:
            raise ValueError(f"{path.relative_to(ROOT)} repeats {field} {key}")
        result[key] = row
    return result


def expected_rows() -> tuple[list[dict[str, str]], list[str]]:
    failures: list[str] = []
    roster = keyed(ROSTER, "tag")
    profiles = keyed(PROFILES, "tag")
    governments = keyed(GOVERNMENTS, "design_tag")
    coas = keyed(COAS, "tag")
    histories = keyed(HISTORIES, "design_tag")
    ranks = keyed(RANKS, "design_tag")
    privileges = keyed(PRIVILEGES, "key")
    laws = keyed(LAWS, "law")
    overlays = keyed(OVERLAYS, "key")
    art = keyed(PRIVILEGE_ART, "key")
    mapping = {
        row["design_tag"]: row["engine_tag"]
        for row in json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))["entries"]
    }
    ownership = rows(OWNERSHIP)
    owner = {row["location"]: row["tag"] for row in ownership}
    counts = Counter(row["tag"] for row in ownership)
    pop_cultures = {
        match.group("location"): match.group("culture")
        for match in POP_CULTURE.finditer(START_POPS.read_text(encoding="utf-8-sig"))
    }
    cultures_by_tag: dict[str, set[str]] = {}
    for row in ownership:
        culture = pop_cultures.get(row["location"])
        if culture:
            cultures_by_tag.setdefault(row["tag"], set()).add(culture)

    result: list[dict[str, str]] = []
    for tag, (name, count) in EXPECTED.items():
        polity = roster.get(tag)
        profile = profiles.get(tag)
        government = governments.get(tag)
        coa = coas.get(tag)
        history = histories.get(tag)
        rank = ranks.get(tag)
        if polity is None:
            failures.append(f"missing reviewed eastern tag {tag}")
            continue
        if polity["name"] != name:
            failures.append(f"{tag} must display as {name}, found {polity['name']}")
        if FORBIDDEN.search(polity["name"]):
            failures.append(f"{tag} retains generic display name {polity['name']}")
        if counts[tag] != count:
            failures.append(f"{tag} ownership changed from {count} to {counts[tag]}")
        if counts[tag] > 60:
            failures.append(f"{tag} exceeds the 60-location reviewed-frame cap")
        if owner.get(polity["map_capital"]) != tag:
            failures.append(f"{tag} does not own reviewed capital {polity['map_capital']}")
        if profile is None:
            failures.append(f"{tag} lacks a culture/religion profile")
        elif profile["culture"] not in cultures_by_tag.get(tag, set()):
            failures.append(f"{tag} primary culture {profile['culture']} is absent from owned pops")
        if government is None:
            failures.append(f"{tag} lacks an explicit government package")
        if coa is None:
            failures.append(f"{tag} lacks a direct reviewed UI standard")
        if (
            history is None
            or history["name"] != name
            or ANACHRONISTIC_AGENDA.search(history["text"])
        ):
            failures.append(f"{tag} lacks a current non-generic AD 1 agenda")
        if rank is None or rank["name"] != name:
            failures.append(f"{tag} lacks current rank presentation")
        engine_tag = mapping.get(tag, "")
        if not engine_tag:
            failures.append(f"{tag} lacks a collision-safe engine tag")
        result.append({
            "design_tag": tag,
            "engine_tag": engine_tag,
            "name": name,
            "map_capital": polity["map_capital"],
            "location_count": str(counts[tag]),
            "culture": profile["culture"] if profile else "",
            "religion": profile["religion"] if profile else "",
            "government_type": government["government_type"] if government else "",
            "reform": government["reform"] if government else "",
            "emblem": coa["emblem"] if coa else "",
            "source": polity["source"],
            "confidence": polity["confidence"],
        })

    if owner.get("kazan") != "VLF":
        failures.append(f"Kazan must belong to VLF, found {owner.get('kazan', '<none>')}")
    if any(row["tag"] == "SIB" and row["location"] == "kazan" for row in ownership):
        failures.append("Tes-Tashtyk transition frame still steals Kazan")

    for key in REQUIRED_PRIVILEGES:
        row = privileges.get(key)
        icon = art.get(key)
        if row is None or not row["source"] or row["confidence"] != "contested":
            failures.append(f"{key} lacks bounded privilege data")
        if icon is None or icon["status"] != "complete" or icon["confidence"] != "secure":
            failures.append(f"{key} lacks complete direct privilege art")
        slug = key.removeprefix("antq_")
        for path in (
            ROOT / f"assets_queue/generated_sources/antq_privilege_{slug}_source.png",
            ROOT / f"assets_queue/generated/antq_privilege_{slug}_64x90.png",
            ROOT / f"main_menu/gfx/interface/icons/privileges/{key}.dds",
        ):
            if not path.is_file():
                failures.append(f"{key} lacks {path.relative_to(ROOT)}")
    for key in REQUIRED_LAWS:
        row = laws.get(key)
        if row is None or not row["source"] or row["confidence"] != "contested":
            failures.append(f"{key} lacks bounded law data")
    for key, expected_tags in EXPECTED_OVERLAYS.items():
        row = overlays.get(key)
        actual = set(row["tags"].split("|")) if row else set()
        if actual != expected_tags:
            failures.append(
                f"{key} tag coverage changed: expected {'|'.join(sorted(expected_tags))}, "
                f"found {'|'.join(sorted(actual))}"
            )

    for language in LANGUAGES:
        path = ROOT / f"main_menu/localization/{language}/antq_m3_countries_l_{language}.yml"
        text = path.read_text(encoding="utf-8-sig")
        for row in result:
            for suffix in ("", "_ADJ"):
                key = row["engine_tag"] + suffix
                if not re.search(rf"^\s*{re.escape(key)}:\s+\"", text, re.MULTILINE):
                    failures.append(f"{language} lacks {key} localization")
    return result, failures


def render(data: list[dict[str, str]]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(data)
    return stream.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        data, failures = expected_rows()
        content = render(data)
        if args.write and not failures:
            LEDGER.write_text(content, encoding="utf-8-sig", newline="")
            print(
                "s2_eastern_granularity: wrote "
                f"{LEDGER.relative_to(ROOT)} ({len(data)} reviewed frames)"
            )
            return 0
        if args.check:
            if not LEDGER.is_file():
                failures.append(f"missing {LEDGER.relative_to(ROOT)}")
            elif LEDGER.read_text(encoding="utf-8-sig") != content:
                failures.append(f"stale {LEDGER.relative_to(ROOT)}")
        if failures:
            print("s2_eastern_granularity: FAIL")
            for failure in failures:
                print(f"  - {failure}")
            return 1
        print(
            "s2_eastern_granularity: PASS "
            f"({len(data)} frames; largest {max(int(row['location_count']) for row in data)}; "
            f"{len(REQUIRED_PRIVILEGES)} privileges/laws with direct art; 11-client localization)"
        )
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"s2_eastern_granularity: FAIL\n  - {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
