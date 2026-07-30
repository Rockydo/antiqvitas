#!/usr/bin/env python3
"""Generate the M5 full map-template override with audited AD 1 RGO corrections."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
ROSTER = ROOT / "docs/world_1ad/polities.csv"
RULES = ROOT / "docs/goods_remap.csv"
ANCHORS = ROOT / "docs/m5/rgo_anchors.csv"
CUSTOM_GOODS = ROOT / "docs/m5/custom_goods.csv"
ANNONA_GRAIN_ANCHORS = ROOT / "docs/m5/annona_grain_anchors.csv"
OUTPUT = ROOT / "in_game/map_data/location_templates.txt"
REPORT = ROOT / "docs/m5/rgo_remap_report.csv"
GLOBAL_AUDIT = ROOT / "docs/m5/global_rgo_audit.csv"
CAPACITY_REPORT = ROOT / "docs/m5/rgo_capacity_distribution.csv"
CAPACITY_SUMMARY = ROOT / "docs/m5/RGO_CAPACITY_AUDIT.md"
MARKETS = ROOT / "docs/m5/markets.csv"
ROADS = ROOT / "docs/m5/road_segments.csv"
LINE = re.compile(r"^(?P<location>[A-Za-z0-9_]+)\s*=\s*\{(?P<body>.*?\braw_material\s*=\s*)(?P<good>[A-Za-z0-9_]+)(?P<tail>.*)$", re.MULTILINE)
ENTRY_LINE = re.compile(
    r"^(?P<location>[A-Za-z0-9_]+)\s*=\s*\{(?P<body>[^\r\n]*)\}\s*$",
    re.MULTILINE,
)
FIELD = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([A-Za-z0-9_.-]+)")
ENVIRONMENT_RULES = {
    "olives": (
        {"mediterranean", "subtropical", "arid"}, "fruit", "P12.1;PER", "secure",
        "Olive cultivation is removed from climates outside its Mediterranean and adjacent dryland envelope.",
    ),
    "wine": (
        {"mediterranean", "subtropical", "continental", "oceanic", "arid"},
        "fruit", "P12.1;PER", "contested",
        "Grape-wine cultivation is removed from arctic, cold-arid, and tropical templates.",
    ),
    "sugar": (
        {"tropical", "subtropical"}, "fiber_crops", "P12.1;PER", "secure",
        "Ancient sugar cultivation is retained only in warm cultivation templates.",
    ),
    "pepper": (
        {"tropical", "subtropical"}, "medicaments", "P12.1;PER", "secure",
        "Pepper production is retained only in tropical and subtropical templates.",
    ),
    "cloves": (
        {"tropical"}, "medicaments", "P12.1;PER", "secure",
        "Clove production is retained only in tropical source-island templates.",
    ),
    "cocoa": (
        {"tropical", "subtropical"}, "fruit", "P12.1;PER", "secure",
        "Cacao cultivation is retained only in warm American templates.",
    ),
    "cotton": (
        {"tropical", "subtropical", "arid", "mediterranean", "continental"},
        "fiber_crops", "P12.1;PER", "contested",
        "Cotton is removed from arctic, cold-arid, and cool-oceanic templates.",
    ),
    "tea": (
        {"tropical", "subtropical", "continental"}, "medicaments", "P12.1;PER", "contested",
        "Minor Han-era tea production is retained only in plausible Chinese cultivation climates.",
    ),
}
RESOURCE_FAMILIES = {
    "staple_crop": {
        "antq_barley", "legumes", "maize", "millet", "potato", "rice", "wheat",
    },
    "orchard_or_specialty_crop": {
        "chili", "cloves", "cocoa", "fruit", "olives", "pepper", "saffron",
        "sugar", "tea", "wine",
    },
    "fiber_or_dye_crop": {
        "antq_papyrus", "cotton", "dyes", "fiber_crops", "silk", "tobacco",
    },
    "pastoral": {
        "antq_camels", "elephants", "horses", "livestock", "wool",
    },
    "aquatic": {"fish", "pearls"},
    "forest_or_gathered": {
        "antq_silphium", "beeswax", "fur", "incense", "ivory", "lumber",
        "medicaments", "wild_game",
    },
    "mineral_or_quarried": {
        "alum", "amber", "antq_jade", "antq_naphtha", "clay", "coal", "copper",
        "gems", "goods_gold", "iron", "lead", "marble", "mercury", "salt", "sand",
        "silver", "stone", "tin",
    },
}
SPECIALTY_GOODS = {
    "antq_camels", "antq_jade", "antq_naphtha", "antq_papyrus", "antq_silphium",
    "cloves", "elephants", "incense", "pepper", "silk", "tea",
}


def rows(path: Path, comments: bool = False) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        source = (line for line in handle if not line.startswith("#")) if comments else handle
        return list(csv.DictReader(source))


def split_pipe(value: str) -> set[str]:
    return {item for item in value.split("|") if item}


def capacity_class(fields: dict[str, str]) -> str:
    topography = fields.get("topography", "")
    vegetation = fields.get("vegetation", "")
    climate = fields.get("climate", "")
    if topography == "atoll":
        return "marine_atoll"
    if topography == "wetlands":
        return "wetland_or_riverine"
    if vegetation == "farmland":
        return "intensive_cultivation"
    if vegetation in {"forest", "jungle", "woods"}:
        return "woodland_or_forest"
    if vegetation in {"desert", "sparse"} and climate in {"arid", "cold_arid"}:
        return "dryland_or_oasis"
    if topography in {"mountains", "plateau", "high_lakes"}:
        return "highland"
    if vegetation == "grasslands":
        return "open_mixed_land"
    return "mixed_land"


def resource_family(good: str) -> str:
    if not good:
        return "none"
    matches = [family for family, goods in RESOURCE_FAMILIES.items() if good in goods]
    if len(matches) != 1:
        raise ValueError(f"RGO good {good} has no unique resource-family classification")
    return matches[0]


def fit_class(
    family: str,
    capacity: str,
    good: str,
    anchored: bool,
    harbor: str,
) -> str:
    if family == "none":
        return "not_applicable"
    if anchored:
        return "source_anchored"
    if good in SPECIALTY_GOODS:
        return "bounded_specialty"
    aligned = {
        "staple_crop": {
            "intensive_cultivation", "mixed_land", "open_mixed_land",
            "wetland_or_riverine",
        },
        "orchard_or_specialty_crop": {
            "dryland_or_oasis", "intensive_cultivation", "mixed_land",
            "open_mixed_land", "woodland_or_forest",
        },
        "fiber_or_dye_crop": {
            "dryland_or_oasis", "intensive_cultivation", "mixed_land",
            "open_mixed_land", "wetland_or_riverine",
        },
        "pastoral": {
            "dryland_or_oasis", "highland", "mixed_land", "open_mixed_land",
        },
        "aquatic": {"marine_atoll", "wetland_or_riverine"},
        "forest_or_gathered": {"highland", "woodland_or_forest"},
        "mineral_or_quarried": {"dryland_or_oasis", "highland"},
    }
    if capacity in aligned.get(family, set()):
        return "environmentally_aligned"
    if family == "aquatic" and harbor:
        return "environmentally_aligned"
    return "broad_capacity_proxy"


def trade_access_class(
    location: str,
    harbor: str,
    market_locations: set[str],
    road_locations: set[str],
) -> str:
    if location in market_locations:
        return "market_anchor"
    if location in road_locations:
        return "reviewed_road_corridor"
    if harbor:
        try:
            suitability = float(harbor)
        except ValueError as exc:
            raise ValueError(f"{location} has invalid harbor suitability {harbor}") from exc
        if suitability >= 0.5:
            return "major_harbor"
        if suitability > 0:
            return "coastal_access"
        return "coastal_local"
    return "inland"


def runtime_worker_seeds() -> tuple[tuple[str, str, int, str, str, str], ...]:
    """Validate the source-led RGO capacity seeds that need a live effect."""
    required = ("location", "good", "worker_levels", "source", "confidence", "note")
    seeds: list[tuple[str, str, int, str, str, str]] = []
    seen: set[str] = set()
    locations = set(json.loads((ROOT / "docs/vanilla_symbols/locations.json").read_text(encoding="utf-8-sig")))
    controlled = {row["location"] for row in rows(OWNERSHIP, comments=True)}
    valid_goods = set(json.loads((ROOT / "docs/vanilla_symbols/good.json").read_text(encoding="utf-8-sig")))
    valid_goods |= {row.get("key", "").strip() for row in rows(CUSTOM_GOODS)}
    for row in rows(ANNONA_GRAIN_ANCHORS):
        if any(not row.get(field, "").strip() for field in required):
            raise ValueError("annona_grain_anchors.csv has a blank required field")
        location = row["location"]
        good = row["good"]
        if location in seen:
            raise ValueError(f"annona_grain_anchors.csv repeats location {location}")
        if location not in locations or location not in controlled:
            raise ValueError(f"annona_grain_anchors.csv has an unknown or uncontrolled location {location}")
        if good not in valid_goods:
            raise ValueError(f"annona_grain_anchors.csv has unknown good {good}")
        try:
            workers = int(row["worker_levels"])
        except ValueError as exc:
            raise ValueError(f"annona_grain_anchors.csv {location} has invalid worker_levels") from exc
        if not 1 <= workers <= 10:
            raise ValueError(f"annona_grain_anchors.csv {location} worker_levels must be 1 through 10")
        if row["confidence"] not in {"secure", "contested"}:
            raise ValueError(f"annona_grain_anchors.csv {location} has invalid confidence")
        seeds.append((location, good, workers, row["source"], row["confidence"], row["note"]))
        seen.add(location)
    if not seeds:
        raise ValueError("annona_grain_anchors.csv has no worker seeds")
    return tuple(sorted(seeds))


def rendered() -> tuple[str, str, tuple[tuple[str, str, str, str, str], ...]]:
    config = json.loads((ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig"))
    source = Path(config["game_dir"]) / "game/in_game/map_data/location_templates.txt"
    roster_rows = rows(ROSTER)
    roster = {row["tag"]: row for row in roster_rows}
    if len(roster) != len(roster_rows):
        raise ValueError("polity roster has duplicate tags")
    owner_region: dict[str, str] = {}
    for row in rows(OWNERSHIP, comments=True):
        tag = row["tag"]
        if tag not in roster:
            raise ValueError(f"ownership references unknown polity {tag}")
        owner_region[row["location"]] = roster[tag]["region"]
    raw_rules = rows(RULES)
    rules: dict[str, dict[str, str]] = {}
    for rule in raw_rules:
        source_good = rule.get("source_good", "").strip()
        if source_good in rules:
            raise ValueError(f"RGO rules duplicate source good {source_good}")
        rules[source_good] = rule
    valid_goods = set(json.loads((ROOT / "docs/vanilla_symbols/good.json").read_text(encoding="utf-8-sig")))
    custom_goods = rows(CUSTOM_GOODS)
    custom_keys = {row.get("key", "").strip() for row in custom_goods}
    if "" in custom_keys or len(custom_keys) != len(custom_goods):
        raise ValueError("custom_goods.csv has blank or duplicate custom-good keys")
    valid_goods |= custom_keys
    valid_regions = {row["region"] for row in roster_rows}
    controlled_locations = set(owner_region)
    for source_good, rule in rules.items():
        if source_good not in valid_goods or rule["replacement_good"] not in valid_goods:
            raise ValueError(f"RGO rule has unknown good {source_good}->{rule['replacement_good']}")
        if not all(rule.get(field, "").strip() for field in ("source_good", "replacement_good", "source", "confidence", "note")):
            raise ValueError("RGO rule has blank required field")
        if rule["confidence"] not in {"secure", "contested"}:
            raise ValueError(f"RGO rule has invalid confidence {rule['confidence']}")
        allowed = split_pipe(rule.get("allowed_regions", ""))
        allowed_locations = split_pipe(rule.get("allowed_locations", ""))
        unknown_regions = allowed - valid_regions
        if unknown_regions:
            raise ValueError(f"RGO rule for {source_good} has unknown regions {sorted(unknown_regions)}")
        unknown_locations = allowed_locations - controlled_locations
        if unknown_locations:
            raise ValueError(
                f"RGO rule for {source_good} has unknown controlled locations "
                f"{sorted(unknown_locations)}"
            )
        if allowed and allowed_locations:
            outside = {
                location
                for location in allowed_locations
                if owner_region[location] not in allowed
            }
            if outside:
                raise ValueError(
                    f"RGO rule for {source_good} allowlist leaves its allowed regions: "
                    f"{sorted(outside)}"
                )
    locations = set(json.loads((ROOT / "docs/vanilla_symbols/locations.json").read_text(encoding="utf-8-sig")))
    anchors: dict[str, dict[str, str]] = {}
    for anchor in rows(ANCHORS):
        location = anchor.get("location", "").strip()
        if location in anchors:
            raise ValueError(f"RGO anchors duplicate location {location}")
        if not all(anchor.get(field, "").strip() for field in ("location", "good", "source", "confidence", "note")):
            raise ValueError("RGO anchor has blank required field")
        if location not in locations:
            raise ValueError(f"RGO anchor has unknown installed location {location}")
        if location not in owner_region:
            raise ValueError(f"RGO anchor location {location} is not controlled in AD 1")
        if anchor["good"] not in valid_goods:
            raise ValueError(f"RGO anchor {location} has unknown good {anchor['good']}")
        if anchor["confidence"] not in {"secure", "contested"}:
            raise ValueError(f"RGO anchor {location} has invalid confidence {anchor['confidence']}")
        anchors[location] = anchor
    changes: list[tuple[str, str, str, str, str]] = []
    def replace(match: re.Match[str]) -> str:
        location, good = match["location"], match["good"]
        anchor = anchors.get(location)
        region = owner_region.get(location)
        if anchor:
            replacement = anchor["good"]
            if good == replacement:
                return match.group(0)
            changes.append((location, region, "anchor", good, replacement))
            return f"{location} = {{{match['body']}{replacement}{match['tail']}"
        replacement = good
        operation = ""
        rule = rules.get(good)
        if rule and region:
            allowed = split_pipe(rule.get("allowed_regions", ""))
            allowed_locations = split_pipe(rule.get("allowed_locations", ""))
            if allowed_locations:
                permitted = location in allowed_locations
            elif allowed:
                permitted = region in allowed
            else:
                permitted = False
            if not permitted:
                replacement = rule["replacement_good"]
                operation = (
                    "location_allowlist_rule"
                    if allowed_locations
                    else "regional_rule"
                )
        environment = ENVIRONMENT_RULES.get(replacement)
        if environment and region:
            fields = dict(FIELD.findall(match.group(0)))
            climate = fields.get("climate", "")
            allowed_climates, environment_replacement, *_boundary = environment
            if climate and climate not in allowed_climates:
                replacement = environment_replacement
                operation = "environment_rule"
        if replacement == good:
            return match.group(0)
        changes.append((location, region, operation, good, replacement))
        return f"{location} = {{{match['body']}{replacement}{match['tail']}"
    content = LINE.sub(replace, source.read_text(encoding="utf-8"))
    if not changes:
        raise ValueError("RGO rules produced no owned-location corrections")
    counts = Counter((operation, old, new) for _, _, operation, old, new in changes)
    report = ["location,region,operation,source_good,replacement_good"]
    report.extend(",".join(row) for row in sorted(changes))
    report.append("")
    report.append("# counts")
    report.extend(f"# {operation}:{old}->{new},{count}" for (operation, old, new), count in sorted(counts.items()))
    seeds = runtime_worker_seeds()
    report.append("")
    report.append("# runtime worker seeds")
    report.extend(f"# {location},{good},{workers}" for location, good, workers, *_ in seeds)
    return content, "\n".join(report) + "\n", tuple(changes)


def global_audit(
    content: str, changes: tuple[tuple[str, str, str, str, str], ...]
) -> str:
    """Return one transparent AD 1 audit row for every controlled location."""
    config = json.loads((ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig"))
    source = Path(config["game_dir"]) / "game/in_game/map_data/location_templates.txt"
    original_entries = {
        match.group("location"): dict(FIELD.findall(match.group("body")))
        for match in ENTRY_LINE.finditer(source.read_text(encoding="utf-8"))
    }
    current_entries = {
        match.group("location"): dict(FIELD.findall(match.group("body")))
        for match in ENTRY_LINE.finditer(content)
    }
    roster = {row["tag"]: row for row in rows(ROSTER)}
    ownership = rows(OWNERSHIP, comments=True)
    change_by_location = {
        location: (operation, old, new)
        for location, _region, operation, old, new in changes
    }
    rules = {row["source_good"]: row for row in rows(RULES)}
    anchors = {row["location"]: row for row in rows(ANCHORS)}
    market_locations = {row["location"] for row in rows(MARKETS)}
    road_locations = {
        location
        for row in rows(ROADS)
        for location in (row["origin"], row["destination"])
    }
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow((
        "location", "tag", "region", "topography", "vegetation", "climate",
        "natural_harbor_suitability", "capacity_class", "resource_family",
        "fit_class", "trade_access", "installed_good", "ad1_good", "decision",
        "source", "confidence", "note",
    ))
    seen: set[str] = set()
    for row in sorted(ownership, key=lambda item: item["location"]):
        location = row["location"]
        if location in seen:
            raise ValueError(f"global RGO audit repeats controlled location {location}")
        seen.add(location)
        if location not in original_entries or location not in current_entries:
            raise ValueError(f"controlled location {location} has no RGO template")
        original = original_entries[location]
        current = current_entries[location]
        anchor = anchors.get(location)
        changed = change_by_location.get(location)
        if not current.get("raw_material"):
            decision = "nonproductive_water_or_wasteland_template"
            source_key = "EU5-LOCAL-MAP;P12.1"
            confidence = "secure"
            note = (
                "The controlled template has no raw-material field and remains "
                "nonproductive; it is audited but not assigned a fictitious RGO."
            )
        elif anchor:
            decision = "direct_anchor" if not changed else "direct_anchor_correction"
            source_key = anchor["source"]
            confidence = anchor["confidence"]
            note = anchor["note"]
        elif changed:
            operation, old, new = changed
            if operation == "environment_rule":
                _allowed, _replacement, source_key, confidence, note = ENVIRONMENT_RULES[old]
            else:
                rule = rules[old]
                source_key = rule["source"]
                confidence = rule["confidence"]
                note = rule["note"]
            decision = operation
        else:
            decision = "retained_after_period_environment_screen"
            source_key = "P12.1;PER"
            confidence = "contested"
            note = (
                "Period-valid broad resource retained after regional and environmental "
                "screen; this is not a claim of location-specific attested extraction."
            )
        harbor = current.get("natural_harbor_suitability", "")
        capacity = capacity_class(current)
        family = resource_family(current.get("raw_material", ""))
        fit = fit_class(
            family,
            capacity,
            current.get("raw_material", ""),
            anchor is not None,
            harbor,
        )
        writer.writerow((
            location,
            row["tag"],
            roster[row["tag"]]["region"],
            current.get("topography", ""),
            current.get("vegetation", ""),
            current.get("climate", ""),
            harbor,
            capacity,
            family,
            fit,
            trade_access_class(
                location,
                harbor,
                market_locations,
                road_locations,
            ),
            original.get("raw_material", ""),
            current.get("raw_material", ""),
            decision,
            source_key,
            confidence,
            note,
        ))
    if len(seen) != len(ownership):
        raise ValueError(
            "global RGO audit must cover every controlled location; "
            f"expected {len(ownership)}, found {len(seen)}"
        )
    return output.getvalue()


def capacity_distribution(audit: str) -> str:
    audit_rows = list(csv.DictReader(io.StringIO(audit)))
    counts = Counter(
        (
            row["region"],
            row["capacity_class"],
            row["resource_family"],
            row["fit_class"],
            row["trade_access"],
        )
        for row in audit_rows
    )
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(
        (
            "region",
            "capacity_class",
            "resource_family",
            "fit_class",
            "trade_access",
            "locations",
        )
    )
    for key, count in sorted(counts.items()):
        writer.writerow((*key, count))
    return output.getvalue()


def capacity_summary(
    audit: str,
    changes: tuple[tuple[str, str, str, str, str], ...],
) -> str:
    audit_rows = list(csv.DictReader(io.StringIO(audit)))
    decision_counts = Counter(row["decision"] for row in audit_rows)
    capacity_counts = Counter(row["capacity_class"] for row in audit_rows)
    family_counts = Counter(row["resource_family"] for row in audit_rows)
    fit_counts = Counter(row["fit_class"] for row in audit_rows)
    trade_counts = Counter(row["trade_access"] for row in audit_rows)
    good_counts = Counter(row["ad1_good"] for row in audit_rows if row["ad1_good"])
    allowlist_corrections = sum(
        1 for _location, _region, operation, _old, _new in changes
        if operation == "location_allowlist_rule"
    )
    lines = [
        "# Global RGO Capacity Audit",
        "",
        "Generated by `tools/generate_rgo_remap.py`; the CSV ledger covers every",
        "controlled AD 1 location and the distribution file groups the exact",
        "capacity/resource/fit/access union.",
        "",
        f"- {len(audit_rows):,} audited controlled templates.",
        f"- {len(changes):,} installed-to-AD-1 corrections.",
        f"- {allowlist_corrections:,} fine location-allowlist corrections.",
        f"- {decision_counts.get('nonproductive_water_or_wasteland_template', 0):,} "
        "honestly nonproductive templates.",
        "- Tea is confined to eleven Sichuan proxies; cloves to Ternate and",
        "  Tidore; pepper to ten Malabar/Western Ghats proxies.",
        "",
        "## Capacity classes",
        "",
    ]
    lines.extend(
        f"- {key}: {value:,}" for key, value in sorted(capacity_counts.items())
    )
    lines.extend(("", "## Resource families", ""))
    lines.extend(
        f"- {key}: {value:,}" for key, value in sorted(family_counts.items())
    )
    lines.extend(("", "## Fit classes", ""))
    lines.extend(f"- {key}: {value:,}" for key, value in sorted(fit_counts.items()))
    lines.extend(("", "## Trade access", ""))
    lines.extend(
        f"- {key}: {value:,}" for key, value in sorted(trade_counts.items())
    )
    lines.extend(("", "## Bounded specialties", ""))
    for good in sorted(SPECIALTY_GOODS):
        lines.append(f"- {good}: {good_counts.get(good, 0):,}")
    lines.extend(
        (
            "",
            "Capacity and fit are conservative map-level classifications, not",
            "reconstructed output or a claim of site-level extraction. Direct",
            "anchors retain their row-specific source and confidence.",
            "",
        )
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        content, report, changes = rendered()
        audit = global_audit(content, changes)
        distribution = capacity_distribution(audit)
        summary = capacity_summary(audit, changes)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"rgo_remap: FAIL\n  - {exc}")
        return 1
    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(content, encoding="utf-8", newline="\n")
        REPORT.write_text(report, encoding="utf-8-sig", newline="\n")
        GLOBAL_AUDIT.write_text(audit, encoding="utf-8-sig", newline="\n")
        CAPACITY_REPORT.write_text(distribution, encoding="utf-8-sig", newline="\n")
        CAPACITY_SUMMARY.write_text(summary, encoding="utf-8", newline="\n")
        print(
            f"rgo_remap: wrote {OUTPUT.relative_to(ROOT)} "
            f"({len(changes)} corrections; {len(rows(OWNERSHIP, comments=True))} audited locations)"
        )
        return 0
    failures = []
    for path, expected, encoding in (
        (OUTPUT, content, "utf-8"),
        (REPORT, report, "utf-8-sig"),
        (GLOBAL_AUDIT, audit, "utf-8-sig"),
        (CAPACITY_REPORT, distribution, "utf-8-sig"),
        (CAPACITY_SUMMARY, summary, "utf-8"),
    ):
        if not path.is_file() or path.read_text(encoding=encoding) != expected:
            failures.append(f"stale or missing {path.relative_to(ROOT)}")
    if failures:
        print("rgo_remap: FAIL\n  - " + "\n  - ".join(failures))
        return 1
    print(
        f"rgo_remap: PASS ({len(changes)} corrections; "
        f"{len(rows(OWNERSHIP, comments=True))} audited locations)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
