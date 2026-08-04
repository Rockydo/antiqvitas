#!/usr/bin/env python3
"""Replace synthetic names on the campaign's highest-visibility map fields.

The map has far more fields than securely attested ancient settlement names.
This generator never invents a pseudo-ancient town. It preserves reviewed
ancient names, promotes a roster/city label only when that field is still on the
synthetic Tier-3 layer, and otherwise describes the field relative to the
nearest reviewed period anchor as an explicit geographic gameplay proxy.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from io import StringIO
from pathlib import Path

from generate_m4_tier3_names import installed_names
ROOT = Path(__file__).resolve().parents[1]
POLITIES = ROOT / "docs/world_1ad/polities.csv"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
CITY_TARGETS = ROOT / "docs/m4/population_city_targets.csv"
URBAN_NODES = ROOT / "docs/m5/urban_nodes.csv"
POPS = ROOT / "main_menu/setup/start/06_pops.txt"
HIERARCHY = ROOT / "docs/vanilla_symbols/geography_hierarchy.json"
COORDINATES = ROOT / "docs/vanilla_symbols/location_coordinates.json"
CULTURES = ROOT / "docs/m4/cultures.csv"
CORRECTIONS = ROOT / "docs/m4/location_name_corrections.csv"
DYNAMIC_REPORT = ROOT / "docs/m4/dynamic_location_names.csv"
LEDGERS = (
    ("curated", ROOT / "docs/m4/dynamic_location_name_overrides.csv"),
    ("qualified", ROOT / "docs/m4/qualified_location_name_overrides.csv"),
    ("tier2", ROOT / "docs/m4/tier2_location_name_overrides.csv"),
    ("tier2_wide", ROOT / "docs/m4/tier2_wide_location_name_overrides.csv"),
    ("tier2_remote", ROOT / "docs/m4/tier2_remote_location_name_overrides.csv"),
    ("tier2_far", ROOT / "docs/m4/tier2_far_location_name_overrides.csv"),
    ("tier2_ultra", ROOT / "docs/m4/tier2_ultra_location_name_overrides.csv"),
    ("tier3", ROOT / "docs/m4/tier3_location_name_overrides.csv"),
)
ROOT_FALLBACKS = ROOT / "docs/m4/tier3_map_name_fallbacks.csv"
R5_GEOGRAPHY = ROOT / "docs/r5/geography_names.csv"
OUTPUT = ROOT / "docs/m4/priority_location_name_overrides.csv"
AUDIT = ROOT / "docs/m4/priority_location_name_audit.csv"
SUMMARY = ROOT / "docs/m4/priority_location_name_summary.json"

PRIORITY_REGIONS = {
    "germania": {"Germania", "Eastern Europe", "Finland"},
    "india": {"India"},
    "japan": {"Japan"},
    "west_africa": {"West Africa"},
}
GEOGRAPHIC_SCOPES = {
    "gaul": ("france_region", "brabant_area", "flanders_area", "wallonia_area"),
    "anatolia": ("anatolia_region",),
    "italy": ("italy_region",),
    "germania_north": ("north_german_region",),
    "germania_south": ("south_german_region",),
    "germania_baltic": ("baltic_region",),
    "germania_scandinavia": ("scandinavian_region",),
    "han_north": ("north_china_region",),
    "han_east": ("east_china_region",),
    "han_south": ("south_china_region",),
    "han_west": ("west_china_region",),
    "india_hindustan": ("hindustan_region",),
    "india_bengal": ("bengal_region",),
    "india_central": ("central_india_region",),
    "india_deccan": ("deccan_region",),
    "india_west": ("western_india_region",),
    "west_africa_sahel": ("sahel_region",),
    "west_africa_guinea": ("guinea_region",),
}
ROMAN_SCOPES = {
    "roman_italy": ("italy_region",),
    "roman_gaul": ("france_region",),
    "roman_iberia": ("iberia_region",),
    "roman_maghreb": ("maghreb_region",),
    "roman_balkans": ("balkan_region",),
    "roman_anatolia": ("anatolia_region",),
    "roman_egypt": ("egypt_region",),
    "roman_crescent": ("crescent_region",),
}
GROUP_SIZES = {
    "roman": 80,
    "han": 100,
    "germania": 100,
    "india": 100,
    "japan": 120,
    "west_africa": 100,
    "gaul": 100,
    "anatolia": 100,
    "italy": 160,
    "japan_region": 120,
    "roman_italy": 160,
}
DEFAULT_GROUP_SIZE = 60
LARGE_IMPERIAL_TAGS = {"ROM", "HAN", "PAR"}
POP_RE = re.compile(
    r"(?m)^\t(?P<location>[a-z0-9_]+) = \{\r?\n"
    r"\t\tdefine_pop = \{[^\r\n]*\bsize = (?P<size>[0-9.]+)"
)
ALGORITHMIC_DIRECTIONAL = re.compile(
    r"^(?:Core|Inner|Middle|Outer|Far)\b.*\bLands$|"
    r"\b(?:Approaches|Hinterland|Region) of\b",
    re.IGNORECASE,
)


def rows(path: Path, *, comments: bool = False) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        lines = (line for line in handle if not comments or not line.startswith("#"))
        return list(csv.DictReader(lines))


def r5_location_names() -> dict[str, dict[str, str]]:
    """Return the reviewed AD 1 root name for each installed location.

    Priority adapters are written after the Round 5 geography pass.  They must
    preserve its researched roots rather than promoting a vanilla cartographic
    fallback merely because a field is populous or otherwise prominent.
    """
    required = {
        "granularity", "key", "ad1_name", "source", "confidence", "note",
    }
    result: dict[str, dict[str, str]] = {}
    for row in rows(R5_GEOGRAPHY):
        if not required.issubset(row):
            raise ValueError(
                f"{R5_GEOGRAPHY.relative_to(ROOT)} lacks required Round 5 columns"
            )
        if row["granularity"] != "location":
            continue
        location = row["key"].strip()
        name = row["ad1_name"].strip()
        if not location or not name:
            raise ValueError(
                f"{R5_GEOGRAPHY.relative_to(ROOT)} has blank location name data"
            )
        if location in result:
            raise ValueError(
                f"{R5_GEOGRAPHY.relative_to(ROOT)} has duplicate location {location}"
            )
        result[location] = {
            "historical_name": name,
            "source": row["source"].strip(),
            "confidence": row["confidence"].strip(),
            "note": row["note"].strip(),
        }
    if not result:
        raise ValueError(f"{R5_GEOGRAPHY.relative_to(ROOT)} has no location names")
    return result


def leaves(
    key: str,
    hierarchy: dict[str, list[str]],
    trail: tuple[str, ...] = (),
) -> set[str]:
    if key in trail:
        raise ValueError(f"cyclic geography path {' -> '.join((*trail, key))}")
    children = hierarchy.get(key)
    if not children:
        return {key}
    result: set[str] = set()
    for child in children:
        if child == key:
            result.add(child)
        else:
            result.update(leaves(child, hierarchy, (*trail, key)))
    return result


def effective_entries() -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in rows(CORRECTIONS):
        result[row["location"]] = {**row, "layer": "correction"}
    correction_keys = set(result)
    # Secure coordinate-verified capitals are generated from the roster rather
    # than stored in an input ledger. They remain stable when this priority
    # layer is added, so harvest only that non-circular subset of the report.
    for row in rows(DYNAMIC_REPORT):
        if row.get("anchor_kind") == "capital" and row["location"] not in result:
            result[row["location"]] = {**row, "layer": "capital"}
    for layer, path in LEDGERS:
        for row in rows(path):
            location = row["location"]
            if location in correction_keys or location in result:
                continue
            result[location] = {**row, "layer": layer}
    for row in rows(ROOT_FALLBACKS):
        result.setdefault(
            row["location"],
            {**row, "culture": "", "layer": "tier3_root"},
        )
    return result


def population() -> dict[str, float]:
    return {
        match.group("location"): float(match.group("size"))
        for match in POP_RE.finditer(POPS.read_text(encoding="utf-8-sig"))
    }


def intended_direct_names(
    polities: list[dict[str, str]],
) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in polities:
        name = re.sub(
            r"\s*\([^)]*\bfield\b[^)]*\)\s*",
            "",
            row["historical_capital"],
        ).strip()
        result[row["map_capital"]] = {
            "name": name,
            "source": row["source"],
            "confidence": row["confidence"],
            "note": (
                f"{row['tag']} roster capital/territorial label on its documented "
                "engine proxy"
            ),
            "category": "capital",
        }
    for row in rows(CITY_TARGETS):
        if not row["location"] or row["mode"] == "subsumed":
            continue
        result[row["location"]] = {
            "name": row["place"].replace("_", "-"),
            "source": row["source"],
            "confidence": row["confidence"],
            "note": row["note"],
            "category": "top_city",
        }
    for row in rows(URBAN_NODES):
        result.setdefault(
            row["location"],
            {
                "name": row["key"].replace("_", " ").title(),
                "source": row["source"],
                "confidence": row["confidence"],
                "note": row["note"],
                "category": "urban_node",
            },
        )
    return result


def priority_locations(
    polities: list[dict[str, str]],
    owner: dict[str, str],
    pop: dict[str, float],
    hierarchy: dict[str, list[str]],
) -> dict[str, set[str]]:
    categories: dict[str, set[str]] = defaultdict(set)
    for row in polities:
        categories[row["map_capital"]].add("capital")
    for row in rows(CITY_TARGETS):
        if row["location"] and row["mode"] != "subsumed":
            categories[row["location"]].add("top_city")
    for row in rows(URBAN_NODES):
        categories[row["location"]].add("urban_node")

    by_tag = {row["tag"]: row for row in polities}
    groups: dict[str, set[str]] = {
        "roman": {location for location, tag in owner.items() if tag == "ROM"},
        "han": {location for location, tag in owner.items() if tag == "HAN"},
    }
    for group, regions in PRIORITY_REGIONS.items():
        groups[group] = {
            location
            for location, tag in owner.items()
            if by_tag.get(tag, {}).get("region") in regions
        }
    for group, scopes in GEOGRAPHIC_SCOPES.items():
        groups[group] = set().union(*(leaves(scope, hierarchy) for scope in scopes))
    roman_locations = {
        location for location, tag in owner.items() if tag == "ROM"
    }
    for group, scopes in ROMAN_SCOPES.items():
        groups[group] = (
            set().union(*(leaves(scope, hierarchy) for scope in scopes))
            & roman_locations
        )

    for group, locations in groups.items():
        for location in sorted(
            locations & set(pop),
            key=lambda item: (-pop[item], item),
        )[: GROUP_SIZES.get(group, DEFAULT_GROUP_SIZE)]:
            categories[location].add(f"priority_{group}")
    return categories


def coordinates() -> dict[str, tuple[float, float]]:
    payload = json.loads(COORDINATES.read_text(encoding="utf-8-sig"))["locations"]
    return {
        key: (float(value["x"]), float(value["y"]))
        for key, value in payload.items()
    }


def bearing(dx: float, dy: float) -> str:
    # Screen-space y grows southward.
    angle = (math.degrees(math.atan2(dx, -dy)) + 360.0) % 360.0
    names = (
        "North",
        "North-northeast",
        "Northeast",
        "East-northeast",
        "East",
        "East-southeast",
        "Southeast",
        "South-southeast",
        "South",
        "South-southwest",
        "Southwest",
        "West-southwest",
        "West",
        "West-northwest",
        "Northwest",
        "North-northwest",
    )
    return names[int((angle + 11.25) // 22.5) % 16]


def proxy_name(anchor: str, distance: float, direction: str) -> str:
    if distance <= 4.0:
        return f"Environs of {anchor}"
    if distance <= 8.0:
        return f"{direction} Approaches to {anchor}"
    if distance <= 16.0:
        return f"{direction} Hinterland of {anchor}"
    return f"{direction} Region of {anchor}"


def generated_overrides() -> tuple[
    list[dict[str, str]],
    dict[str, set[str]],
    dict[str, dict[str, str]],
    dict[str, str],
]:
    polities = rows(POLITIES)
    owner = {
        row["location"]: row["tag"]
        for row in rows(OWNERSHIP, comments=True)
    }
    pop = population()
    hierarchy = json.loads(HIERARCHY.read_text(encoding="utf-8-sig"))
    coords = coordinates()
    effective = effective_entries()
    categories = priority_locations(polities, owner, pop, hierarchy)
    direct = intended_direct_names(polities)
    by_tag = {row["tag"]: row for row in polities}
    cultures = {row["key"]: row for row in rows(CULTURES)}
    map_labels = installed_names()
    r5_names = r5_location_names()

    culture_locations: dict[str, list[str]] = defaultdict(list)
    for location, entry in effective.items():
        culture = entry.get("culture", "")
        if "|" not in culture and culture in cultures and location in coords:
            culture_locations[culture].append(location)
    culture_geometry: dict[
        str,
        tuple[float, float, dict[str, float]],
    ] = {}
    for culture, locations in culture_locations.items():
        cx = sum(coords[key][0] for key in locations) / len(locations)
        cy = sum(coords[key][1] for key in locations) / len(locations)
        distances = {
            key: math.hypot(coords[key][0] - cx, coords[key][1] - cy)
            for key in locations
        }
        culture_geometry[culture] = (cx, cy, distances)

    owner_locations: dict[str, list[str]] = defaultdict(list)
    for key, tag in owner.items():
        if key in coords:
            owner_locations[tag].append(key)
    owner_geometry: dict[str, tuple[float, float, dict[str, float]]] = {}
    for tag, locations in owner_locations.items():
        cx = sum(coords[key][0] for key in locations) / len(locations)
        cy = sum(coords[key][1] for key in locations) / len(locations)
        distances = {
            key: math.hypot(coords[key][0] - cx, coords[key][1] - cy)
            for key in locations
        }
        owner_geometry[tag] = (cx, cy, distances)

    anchors: dict[str, dict[str, str]] = {
        location: entry
        for location, entry in effective.items()
        if entry["layer"] not in {"tier3", "tier3_root"} and location in coords
    }
    for location, entry in direct.items():
        if location in coords:
            anchors.setdefault(
                location,
                {
                    "historical_name": entry["name"],
                    "source": entry["source"],
                    "confidence": entry["confidence"],
                    "layer": "direct_source",
                },
            )

    output: list[dict[str, str]] = []
    for location in sorted(categories):
        current = effective.get(location)
        if not current:
            raise ValueError(f"priority location has no effective name: {location}")
        if current["layer"] not in {"tier3", "tier3_root"}:
            continue
        # The Roman audit deliberately leaves fields without a secure identity
        # on vanilla localization. Do not reintroduce synthetic territorial
        # prose through this lower-confidence priority layer.
        if owner.get(location) == "ROM":
            continue
        if location not in coords:
            raise ValueError(f"priority location has no centroid: {location}")
        culture = current.get("culture", "")
        if not culture:
            raise ValueError(
                f"priority synthetic location has no culture adapter: {location}"
            )

        if location in direct:
            selected = direct[location]
            name = selected["name"]
            source = f"{selected['source']};GEO-PROXY"
            note = (
                f"High-visibility {selected['category']} replacement for a synthetic "
                f"Tier-3 form. {selected['note']}; the engine field is a documented "
                "proxy and not an exact settlement polygon."
            )
        else:
            reviewed = r5_names.get(location)
            if reviewed:
                name = reviewed["historical_name"]
                source = f"{current['source']};R5-GEOGRAPHY;{reviewed['source']}"
                note = (
                    "High-visibility field replaces the installed cartographic "
                    "fallback with its reviewed Round 5 AD 1 geography root. "
                    f"{reviewed['note']}"
                )
            else:
                name = map_labels.get(
                    location,
                    location.replace("_", " ").replace("-", " ").title(),
                )
                source = f"{current['source']};T3N:transparent-map-label"
                note = (
                    "High-visibility unresolved field retains a concise installed "
                    "cartographic label. It is explicitly not presented as an attested "
                    "ancient settlement name."
                )
        output.append(
            {
                "location": location,
                "culture": culture,
                "historical_name": name,
                "source": source,
                "confidence": "tier2",
                "note": note,
            }
        )
    return output, categories, effective, owner


def audit_rows(
    overrides: list[dict[str, str]],
    categories: dict[str, set[str]],
    effective: dict[str, dict[str, str]],
    owner: dict[str, str],
) -> list[dict[str, str]]:
    replacement = {row["location"]: row for row in overrides}
    output: list[dict[str, str]] = []
    for location in sorted(categories):
        if location in replacement:
            entry = replacement[location]
            layer = "priority_proxy"
            classification = (
                "transparent_map_fallback"
                if "T3N:transparent-map-label" in entry["source"]
                else "conservative_regional_proxy"
            )
        elif (
            owner.get(location) == "ROM"
            and effective[location]["layer"] in {"tier3", "tier3_root"}
        ):
            entry = {
                "historical_name": "[EU5 vanilla pass-through]",
                "source": "P10;PLE",
                "confidence": "contested",
                "note": (
                    "The Roman identity audit found no sufficiently secure AD 1 "
                    "field identity. Runtime localization deliberately falls "
                    "through to EU5 vanilla instead of emitting a synthetic name."
                ),
            }
            layer = "roman_vanilla_passthrough"
            classification = "unresolved_vanilla_passthrough"
        else:
            entry = effective[location]
            layer = entry["layer"]
            classification = (
                "attested"
                if entry.get("confidence") == "secure"
                and layer in {"capital", "curated", "correction"}
                else "conservative_regional_proxy"
            )
        output.append(
            {
                "location": location,
                "categories": "|".join(sorted(categories[location])),
                "historical_name": entry["historical_name"],
                "layer": layer,
                "classification": classification,
                "source": entry["source"],
                "confidence": entry["confidence"],
                "note": entry["note"],
            }
        )
    return output


def csv_text(values: list[dict[str, str]], fields: tuple[str, ...]) -> str:
    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(values)
    return stream.getvalue()


def render() -> dict[Path, tuple[str, str]]:
    overrides, categories, effective, owner = generated_overrides()
    audit = audit_rows(overrides, categories, effective, owner)
    directional = [
        row["location"]
        for row in overrides
        if ALGORITHMIC_DIRECTIONAL.search(row["historical_name"])
    ]
    if directional:
        raise ValueError(
            "algorithmic directional names remain: " + ", ".join(directional)
        )
    if len(audit) < 1900:
        raise ValueError(f"priority audit unexpectedly small: {len(audit)}")
    if len(overrides) < 1000:
        raise ValueError(
            f"too few high-visibility synthetic replacements: {len(overrides)}"
        )
    capitals = {
        row["location"]
        for row in audit
        if "capital" in row["categories"].split("|")
    }
    expected_capitals = {
        row["map_capital"] for row in rows(POLITIES) if row["map_capital"] != "TBD"
    }
    if capitals != expected_capitals:
        missing = sorted(expected_capitals - capitals)
        extra = sorted(capitals - expected_capitals)
        raise ValueError(
            "priority capital audit mismatch "
            f"(missing={','.join(missing)} extra={','.join(extra)})"
        )
    forbidden = [
        row["location"]
        for row in audit
        if row["layer"] in {"tier3", "tier3_root"}
    ]
    if forbidden:
        raise ValueError("synthetic priority names remain: " + ", ".join(forbidden))
    if any(
        not row["historical_name"]
        or not row["source"]
        or row["classification"]
        not in {
            "attested",
            "securely_reconstructed",
            "conservative_regional_proxy",
            "transparent_map_fallback",
            "unresolved_vanilla_passthrough",
        }
        for row in audit
    ):
        raise ValueError("priority audit has blank or invalid source/classification data")
    summary = {
        "priority_locations": len(audit),
        "generated_replacements": len(overrides),
        "roman_vanilla_passthroughs": sum(
            row["layer"] == "roman_vanilla_passthrough" for row in audit
        ),
        "categories": dict(
            sorted(
                Counter(
                    category
                    for row in audit
                    for category in row["categories"].split("|")
                ).items()
            )
        ),
        "classifications": dict(
            sorted(Counter(row["classification"] for row in audit).items())
        ),
        "layers": dict(sorted(Counter(row["layer"] for row in audit).items())),
    }
    return {
        OUTPUT: (
            csv_text(
                overrides,
                (
                    "location",
                    "culture",
                    "historical_name",
                    "source",
                    "confidence",
                    "note",
                ),
            ),
            "utf-8-sig",
        ),
        AUDIT: (
            csv_text(
                audit,
                (
                    "location",
                    "categories",
                    "historical_name",
                    "layer",
                    "classification",
                    "source",
                    "confidence",
                    "note",
                ),
            ),
            "utf-8-sig",
        ),
        SUMMARY: (
            json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            "utf-8",
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        expected = render()
    except (OSError, ValueError, csv.Error, json.JSONDecodeError) as exc:
        print(f"m4_priority_location_names: FAIL\n  - {exc}")
        return 1
    if args.write:
        for path, (content, encoding) in expected.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding=encoding, newline="\n")
            print(f"m4_priority_location_names: wrote {path.relative_to(ROOT)}")
        return 0
    stale = [
        path.relative_to(ROOT)
        for path, (content, encoding) in expected.items()
        if not path.is_file() or path.read_text(encoding=encoding) != content
    ]
    if stale:
        print("m4_priority_location_names: FAIL")
        for path in stale:
            print(f"  - stale or missing {path}")
        return 1
    payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
    print(
        "m4_priority_location_names: PASS "
        f"({payload['priority_locations']} high-visibility fields; "
        f"{payload['generated_replacements']} synthetic forms replaced)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
