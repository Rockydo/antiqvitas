#!/usr/bin/env python3
"""Validate the exact AD 1 replacement of the former CHI macro-frame."""

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
SELECTORS = tuple(
    ROOT / relative for relative in (
        "docs/world_1ad/ownership_areas.csv",
        "docs/world_1ad/ownership_residual_areas.csv",
        "docs/world_1ad/ownership_locations.csv",
    )
)
PROFILES = ROOT / "docs/m4/tag_profiles.csv"
CULTURES = ROOT / "docs/m4/cultures.csv"
GOVERNMENTS = ROOT / "docs/m6/governments.csv"
COAS = ROOT / "docs/m11/core_coas.csv"
SETTLEMENTS = ROOT / "docs/m5/global_settlement_audit.csv"
LAWS = ROOT / "docs/m6/ancient_law_profiles.csv"
REFORMS = ROOT / "in_game/common/government_reforms/00_antiquitas_m6_core.txt"
ADVANCES = ROOT / "in_game/common/advances/00_antiquitas_m8_tree.txt"
LEDGER = ROOT / "docs/m12/chibchan_granularity.csv"
LANGUAGES = (
    "english", "french", "german", "spanish", "polish", "russian",
    "braz_por", "simp_chinese", "japanese", "korean", "turkish",
)

EXPECTED = {
    "HRC": (
        "Herrera Plateau",
        "Northern Andes",
        "funza",
        "antq_herrera_plateau",
        "antq_herrera_plateau_exchange_network",
        "ce_colombia_",
        {
            "boiaca", "bosa_colombia", "caqueza", "chicaquicha", "choconta",
            "chunsua", "duitama", "funza", "paribari", "suamox",
        },
    ),
    "SNE": (
        "Sierra Nevada Early",
        "Northern Andes",
        "chayrama",
        "antq_sierra_nevada_early",
        "antq_sierra_nevada_early_community_network",
        "ce_colombia_",
        {"chayrama", "teyuna", "yaharo"},
    ),
    "LRC": (
        "Loja Regional-Development",
        "Andes",
        "malacatos",
        "antq_loja_regional_development",
        "antq_loja_regional_development_network",
        "ce_andean_",
        {"calvas", "cangochamba", "malacatos"},
    ),
}
FIELDS = (
    "design_tag", "engine_tag", "name", "map_capital", "location_count",
    "culture", "religion", "government_type", "reform", "seeded_locations",
    "placements", "emblem", "source", "confidence",
)


def rows(path: Path) -> list[dict[str, str]]:
    payload = "\n".join(
        line for line in path.read_text(encoding="utf-8-sig").splitlines()
        if not line.lstrip().startswith("#")
    )
    return list(csv.DictReader(io.StringIO(payload)))


def keyed(path: Path, key: str) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in rows(path):
        value = row[key]
        if value in result:
            raise ValueError(f"{path.relative_to(ROOT)} repeats {key} {value}")
        result[value] = row
    return result


def audit() -> tuple[list[dict[str, str]], list[str]]:
    failures: list[str] = []
    roster = keyed(ROSTER, "tag")
    profiles = keyed(PROFILES, "tag")
    cultures = keyed(CULTURES, "key")
    governments = keyed(GOVERNMENTS, "design_tag")
    coas = keyed(COAS, "tag")
    settlements = keyed(SETTLEMENTS, "tag")
    laws = keyed(LAWS, "tag")
    mapping = {
        row["design_tag"]: row["engine_tag"]
        for row in json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))["entries"]
    }
    ownership = rows(OWNERSHIP)
    owner = {row["location"]: row["tag"] for row in ownership}
    counts = Counter(row["tag"] for row in ownership)
    reform_text = REFORMS.read_text(encoding="utf-8-sig")
    advance_text = ADVANCES.read_text(encoding="utf-8-sig")

    expected_locations = set().union(*(item[6] for item in EXPECTED.values()))
    actual_locations = {row["location"] for row in ownership if row["tag"] in EXPECTED}
    if len(expected_locations) != 16 or actual_locations != expected_locations:
        failures.append("reviewed former-CHI surface must contain exactly the pinned 16 locations")
    if "CHI" in roster or counts["CHI"]:
        failures.append("obsolete CHI macro-frame survives in roster or resolved ownership")
    for path in SELECTORS:
        if any(row["tag"] == "CHI" for row in rows(path)):
            failures.append(f"obsolete CHI selector survives in {path.relative_to(ROOT)}")

    output: list[dict[str, str]] = []
    for tag, (name, region, capital, culture, reform, emblem_prefix, locations) in EXPECTED.items():
        polity = roster.get(tag)
        profile = profiles.get(tag)
        government = governments.get(tag)
        coa = coas.get(tag)
        settlement = settlements.get(tag)
        if polity is None:
            failures.append(f"missing reviewed former-CHI replacement {tag}")
            continue
        actual = {location for location in locations if owner.get(location) == tag}
        if actual != locations or counts[tag] != len(locations):
            failures.append(f"{tag} must own exactly {sorted(locations)}")
        if polity["name"] != name or polity["region"] != region or polity["map_capital"] != capital:
            failures.append(f"{tag} identity, region, or capital changed")
        if profile is None or profile["culture"] != culture or profile["religion"] != "antq_andean":
            failures.append(f"{tag} lacks its reviewed culture/religion profile")
        if culture not in cultures:
            failures.append(f"{tag} references undefined culture {culture}")
        if government is None or government["government_type"] != "tribe" or government["reform"] != reform:
            failures.append(f"{tag} lacks reviewed government reform {reform}")
        if coa is None or not coa["emblem"].startswith(emblem_prefix):
            failures.append(f"{tag} lacks a reviewed direct regional standard")
        if settlement is None or int(settlement["seeded_locations"]) < 1:
            failures.append(f"{tag} lacks an opening settlement seed")
        if laws.get(tag, {}).get("profile") != "transoceanic":
            failures.append(f"{tag} lacks the transoceanic legal profile")
        if not re.search(rf"(?m)^{re.escape(reform)}\s*=\s*\{{", reform_text):
            failures.append(f"generated reform definition missing {reform}")
        if f"unlock_government_reform = {reform}" in advance_text:
            failures.append(f"opening reform leaked into research: {reform}")
        output.append({
            "design_tag": tag,
            "engine_tag": mapping.get(tag, ""),
            "name": name,
            "map_capital": capital,
            "location_count": str(counts[tag]),
            "culture": profile["culture"] if profile else "",
            "religion": profile["religion"] if profile else "",
            "government_type": government["government_type"] if government else "",
            "reform": government["reform"] if government else "",
            "seeded_locations": settlement["seeded_locations"] if settlement else "",
            "placements": settlement["placements"] if settlement else "",
            "emblem": coa["emblem"] if coa else "",
            "source": polity["source"],
            "confidence": polity["confidence"],
        })

    for language in LANGUAGES:
        text = (
            ROOT / f"main_menu/localization/{language}/antq_m3_countries_l_{language}.yml"
        ).read_text(encoding="utf-8-sig")
        for entry in output:
            for suffix in ("", "_ADJ"):
                key = entry["engine_tag"] + suffix
                if not key or not re.search(rf"^\s*{re.escape(key)}:\s+\"", text, re.MULTILINE):
                    failures.append(f"{language} lacks {key or entry['design_tag']}")
        if re.search(r'^\s*\w+:\s+"[^"]*Chibchan Societies', text, re.I | re.M):
            failures.append(f"{language} retains the obsolete CHI display name")
    return output, failures


def render(output: list[dict[str, str]]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(output)
    return stream.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        output, failures = audit()
        content = render(output)
        if args.write and not failures:
            LEDGER.write_text(content, encoding="utf-8-sig", newline="")
            print(f"s2_chibchan_granularity: wrote {LEDGER.relative_to(ROOT)}")
            return 0
        if args.check:
            if not LEDGER.is_file():
                failures.append(f"missing {LEDGER.relative_to(ROOT)}")
            elif LEDGER.read_text(encoding="utf-8-sig") != content:
                failures.append(f"stale {LEDGER.relative_to(ROOT)}")
        if failures:
            print("s2_chibchan_granularity: FAIL")
            for failure in failures:
                print(f"  - {failure}")
            return 1
        print("s2_chibchan_granularity: PASS (3 frames; 16 exact former-CHI locations)")
        return 0
    except (KeyError, OSError, ValueError) as exc:
        print(f"s2_chibchan_granularity: FAIL ({exc})")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
