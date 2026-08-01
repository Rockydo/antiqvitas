#!/usr/bin/env python3
"""Validate the sourced AD 1 PLA catch-all replacement."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "docs/world_1ad/polities.csv"
TAG_MAP = ROOT / "docs/world_1ad/tag_map.json"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
AREAS = ROOT / "docs/world_1ad/ownership_areas.csv"
RESIDUAL = ROOT / "docs/world_1ad/ownership_residual_areas.csv"
DIRECT = ROOT / "docs/world_1ad/ownership_locations.csv"
PROFILES = ROOT / "docs/m4/tag_profiles.csv"
CULTURES = ROOT / "docs/m4/cultures.csv"
GOVERNMENTS = ROOT / "docs/m6/governments.csv"
COAS = ROOT / "docs/m11/core_coas.csv"
SETTLEMENTS = ROOT / "docs/m5/global_settlement_audit.csv"
LAWS = ROOT / "docs/m6/ancient_law_profiles.csv"
REFORMS = ROOT / "in_game/common/government_reforms/00_antiquitas_m6_core.txt"
ADVANCES = ROOT / "in_game/common/advances/00_antiquitas_m8_tree.txt"
LEDGER = ROOT / "docs/m12/plains_woodland_granularity.csv"
LANGUAGE_CLIENTS = (
    "english", "french", "german", "spanish", "polish", "russian",
    "braz_por", "simp_chinese", "japanese", "korean", "turkish",
)

EXPECTED = {
    "PPA": (
        "Adirondack-St Lawrence", "oswegatchie",
        ("adirondacks_province", "oswegatchie_province"),
        "antq_adirondack_point_peninsula", "antq_point_peninsula_seasonal_network",
        {
            "itekiatonhniarikon", "kawenote", "oronia", "oskennonton",
            "ticonderoga", "tsiietsenhtha", "nikahionhwakowa", "oswegatchie",
        },
    ),
    "MHP": (
        "Mohawk Point Peninsula", "canajoharie",
        ("kanienkehaka_province",), "antq_mohawk_point_peninsula",
        "antq_point_peninsula_seasonal_network",
        {"canajoharie", "oneonta", "saratoga", "schenectady", "teionontatatie"},
    ),
    "FLP": (
        "Finger Lakes Peninsula", "oswego",
        (
            "gayogohono_province", "onondagega_province",
            "onondowaga_province", "onyotaaka_province",
        ),
        "antq_finger_lakes_point_peninsula", "antq_point_peninsula_seasonal_network",
        {
            "assorodus", "gahato", "skaniatares", "oswego", "otsiningo",
            "tsikahiotsisto", "canadaigua", "geneseo", "irondequoit",
            "tsonentsiio", "niiohehsane", "oneniote", "onenioteke",
            "teiehonwahkhkwatha",
        },
    ),
    "HVI": (
        "Havana-Illinois Valley", "peoria",
        ("kishwaukee_province", "peoria_province"), "antq_havana_illinois_valley",
        "antq_havana_hopewell_exchange_network",
        {"peewareewa", "peoria", "sangamon"},
    ),
    "ABW": (
        "American Bottom Woodland", "cahokia",
        ("cahokia_province", "mitchigamea_province", "moingwena_province"),
        "antq_american_bottom_middle_woodland",
        "antq_havana_hopewell_exchange_network",
        {
            "amonokoa", "cahokia", "kaskankaham", "kaskaskia", "macoupin",
            "ochechiton", "moingwena",
        },
    ),
    "CMW": (
        "Mississippi Woodland", "tamaroa",
        ("tamaroa_province", "towosaghy_province"),
        "antq_central_mississippi_woodland",
        "antq_central_mississippi_woodland_network",
        {"chariton", "emasulia", "oahaha", "tamaroa", "wyaconda", "chepoussa", "st_francois_mts"},
    ),
    "MRW": (
        "Meramec-Missouri Woodland", "meramec",
        ("meramec_province",), "antq_meramec_missouri_woodland",
        "antq_central_mississippi_woodland_network",
        {"meramec", "pahatsi", "tanwakanwakaghe"},
    ),
    "KCP": (
        "Lower Missouri Hopewell", "nodaway",
        ("nodaway_province",), "antq_kansas_city_hopewell",
        "antq_kansas_city_hopewell_network",
        {"nodaway", "nudarcha", "wimihsoorita", "omaha"},
    ),
}
FIELDS = (
    "design_tag", "engine_tag", "name", "map_capital", "provinces",
    "location_count", "former_pla_locations", "culture", "culture_group",
    "religion", "government_type", "reform", "seeded_locations",
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
        if row[key] in result:
            raise ValueError(f"{path.relative_to(ROOT)} repeats {key} {row[key]}")
        result[row[key]] = row
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
    ownership_rows = rows(OWNERSHIP)
    owned = {
        tag: {row["location"] for row in ownership_rows if row["tag"] == tag}
        for tag in EXPECTED
    }
    area_rows = rows(AREAS)
    provinces = {
        tag: {row["geography"] for row in area_rows if row["tag"] == tag}
        for tag in EXPECTED
    }
    if "PLA" in roster or any(row["tag"] == "PLA" for row in ownership_rows):
        failures.append("obsolete PLA catch-all survives in roster or ownership")
    for path in (AREAS, RESIDUAL, DIRECT):
        if any(row["tag"] == "PLA" for row in rows(path)):
            failures.append(f"obsolete PLA selector survives in {path.relative_to(ROOT)}")
    all_expected = set().union(*(entry[5] for entry in EXPECTED.values()))
    if len(all_expected) != 51:
        failures.append("validator's former PLA location contract is not exactly 51")

    reform_text = REFORMS.read_text(encoding="utf-8-sig")
    advance_text = ADVANCES.read_text(encoding="utf-8-sig")
    output: list[dict[str, str]] = []
    for tag, (name, capital, expected_provinces, culture, reform, locations) in EXPECTED.items():
        polity = roster.get(tag)
        profile = profiles.get(tag)
        culture_row = cultures.get(culture)
        government = governments.get(tag)
        coa = coas.get(tag)
        settlement = settlements.get(tag)
        if polity is None:
            failures.append(f"missing reviewed North American frame {tag}")
            continue
        if polity["name"] != name or polity["region"] != "North America" or polity["map_capital"] != capital:
            failures.append(f"{tag} identity, region, or capital changed")
        if owned[tag] != locations or capital not in owned[tag]:
            failures.append(f"{tag} ownership differs from its reviewed former-PLA set")
        if provinces[tag] != set(expected_provinces):
            failures.append(f"{tag} installed-province frame changed")
        if profile is None or profile["culture"] != culture or profile["religion"] != "antq_north_american":
            failures.append(f"{tag} lacks reviewed culture/religion profile")
        if culture_row is None or culture_row["group"] != "antq_american_group":
            failures.append(f"{tag} lacks reviewed American archaeological culture")
        if government is None or government["reform"] != reform:
            failures.append(f"{tag} lacks reviewed government reform {reform}")
        if coa is None or not coa["emblem"]:
            failures.append(f"{tag} lacks a direct reviewed UI standard")
        if settlement is None or int(settlement["seeded_locations"]) < 1:
            failures.append(f"{tag} lacks an opening settlement seed")
        if laws.get(tag, {}).get("profile") != "transoceanic":
            failures.append(f"{tag} lacks the reviewed American legal profile")
        if not re.search(rf"(?m)^{re.escape(reform)}\s*=\s*\{{", reform_text):
            failures.append(f"generated reform definition missing {reform}")
        if f"unlock_government_reform = {reform}" in advance_text:
            failures.append(f"opening reform leaked into research: {reform}")
        engine_tag = mapping.get(tag, "")
        if not engine_tag:
            failures.append(f"{tag} lacks a collision-safe engine tag")
        output.append({
            "design_tag": tag, "engine_tag": engine_tag, "name": name,
            "map_capital": capital, "provinces": "|".join(expected_provinces),
            "location_count": str(len(owned[tag])),
            "former_pla_locations": str(len(owned[tag])), "culture": culture,
            "culture_group": culture_row["group"] if culture_row else "",
            "religion": profile["religion"] if profile else "",
            "government_type": government["government_type"] if government else "",
            "reform": government["reform"] if government else "",
            "seeded_locations": settlement["seeded_locations"] if settlement else "",
            "placements": settlement["placements"] if settlement else "",
            "emblem": coa["emblem"] if coa else "",
            "source": polity["source"], "confidence": polity["confidence"],
        })
    if set().union(*owned.values()) != all_expected:
        failures.append("the eight frames do not preserve exactly the 51 former PLA locations")

    for language in LANGUAGE_CLIENTS:
        text = (
            ROOT / f"main_menu/localization/{language}/antq_m3_countries_l_{language}.yml"
        ).read_text(encoding="utf-8-sig")
        for entry in output:
            for suffix in ("", "_ADJ"):
                key = entry["engine_tag"] + suffix
                if not re.search(rf"^\s*{re.escape(key)}:\s+\"", text, re.MULTILINE):
                    failures.append(f"{language} lacks {key}")
        if re.search(r'^\s*\w+:\s+"[^"]*Plains and Coastal Societies', text, re.I | re.M):
            failures.append(f"{language} retains the obsolete PLA display name")
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
            print(f"s2_plains_woodland_granularity: wrote {LEDGER.relative_to(ROOT)}")
            return 0
        if args.check:
            if not LEDGER.is_file():
                failures.append(f"missing {LEDGER.relative_to(ROOT)}")
            elif LEDGER.read_text(encoding="utf-8-sig") != content:
                failures.append(f"stale {LEDGER.relative_to(ROOT)}")
        if failures:
            print("s2_plains_woodland_granularity: FAIL")
            for failure in failures:
                print(f"  - {failure}")
            return 1
        print("s2_plains_woodland_granularity: PASS (8 frames; 51 former PLA locations)")
        return 0
    except (KeyError, OSError, ValueError) as exc:
        print(f"s2_plains_woodland_granularity: FAIL ({exc})")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
