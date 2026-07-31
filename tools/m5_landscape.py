#!/usr/bin/env python3
"""Audit and generate conservative AD 1 landscape corrections."""

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
LEDGER = ROOT / "docs/m5/landscape_changes.csv"
DISTRIBUTION = ROOT / "docs/m5/landscape_distribution.csv"
SUMMARY = ROOT / "docs/m5/LANDSCAPE_AUDIT.md"
HIERARCHY = ROOT / "docs/vanilla_symbols/geography_hierarchy.json"
REGIONS = ROOT / "docs/vanilla_symbols/regions.json"
ENTRY = re.compile(
    r"^(?P<location>[A-Za-z0-9_]+)\s*=\s*\{(?P<body>[^\r\n]*)\}\s*$",
    re.MULTILINE,
)
FIELD = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([A-Za-z0-9_.-]+)")
FOREST_GOODS = {"beeswax", "fur", "lumber", "medicaments", "wild_game"}
CROPS = {
    "cotton", "fiber_crops", "fruit", "legumes", "millet", "olives", "rice",
    "saffron", "sugar", "wheat", "wine",
}
MEDITERRANEAN_REGIONS = {
    "Africa", "Anatolia", "Balkans", "Iran", "Levant", "Rome",
}
ASIAN_REGIONS = {"China", "India", "Southeast Asia"}
GERMAN_CORE_AREAS = {
    "bavaria_area", "bohemia_area", "brandenburg_area", "franconia_area",
    "hesse_area", "lower_saxony_area", "mecklenburg_area", "moravia_area",
    "pomerania_area", "swabia_area", "upper_saxony_area", "westphalia_area",
}
IBERIAN_HUMID_AREAS = {
    "galicia_area", "leon_area", "navarre_area", "north_portugal_area",
}
IBERIAN_MOSAIC_AREAS = {
    "andalusia_area", "aragon_area", "castile_area", "catalonia_area",
    "extremadura_area", "granada_area", "south_portugal_area", "toledo_area",
    "valencia_area",
}
IBERIAN_WOOD_PASTURE_GOODS = {
    "beeswax", "fruit", "horses", "livestock", "lumber", "medicaments",
    "olives", "wild_game", "wine", "wool",
}
MARSH_GRASSLAND = {
    "abdas", "al_madar", "an_nil", "basra", "numaniyyah", "suq_al_shuyukh",
    "zuwayr",
}
MARSH_FARMLAND = {
    "abadan", "al_qatr", "nasiriyah", "samawa", "wasit",
}
IRRIGATED_MESOPOTAMIA = {
    "baghdad", "hillah", "karbala", "khalis", "kufa", "rusafa", "samarra",
    "tikrit", "ukbara",
}
RULE_META = {
    "mesopotamian_marsh": (
        "P12.3;BHR;SCHU-CHA", "contested",
        "Lower Tigris-Euphrates wetland proxy; exact installed field extent is approximate.",
    ),
    "mesopotamian_irrigation": (
        "P12.3;BHR", "contested",
        "Irrigated alluvial cultivation proxy; this does not reconstruct one canal or output level.",
    ),
    "germania_forest_product": (
        "P8.7;TAC-GER;STR-GER", "contested",
        "Forest-product field restored to an open woodland mosaic in ancient Germania.",
    ),
    "germania_dense_woodland": (
        "P8.7;TAC-GER;STR-GER", "contested",
        "Forest-product field restored to denser ancient Germanic woodland.",
    ),
    "germania_central_mosaic": (
        "P8.7;EURO-REVEALS;NORTH-EURO-POLLEN", "contested",
        "Central German grassland field restored to a predominantly wooded "
        "Barbaricum mosaic; crop clearings and coastal or river wetlands remain open.",
    ),
    "germania_upland_forest": (
        "P8.7;EURO-REVEALS;BOHEMIAN-POLLEN", "contested",
        "Existing central German upland woods receive the denser forest class; "
        "this is a coarse canopy presentation rather than a local pollen estimate.",
    ),
    "iberian_atlantic_mosaic": (
        "P8.6;IBERIA-NORTH-POLLEN;IBERIA-MOLINA", "contested",
        "Humid Atlantic Iberian non-cereal ground receives a woodland-mosaic "
        "presentation while documented upland heath and agricultural openings remain.",
    ),
    "iberian_mountain_forest": (
        "P8.6;IBERIA-NORTH-POLLEN;IBERIA-TELENO", "contested",
        "Existing humid mountain woods receive a denser forest presentation "
        "without treating all Atlantic Iberian uplands as closed canopy.",
    ),
    "iberian_wood_pasture_mosaic": (
        "P8.6;EURO-REVEALS;IBERIA-MOLINA", "contested",
        "Non-cereal Iberian hill and plateau ground receives an open woodland "
        "or wood-pasture mosaic; cereal basins and arid mineral ground remain open.",
    ),
    "atlantic_woodland": (
        "P8.6;PTO-GEO-II2;NMI-IRON-AGE", "contested",
        "Forest-product field restored to Atlantic woodland without claiming closed-canopy coverage.",
    ),
    "atlantic_wetland": (
        "P8.6;PTO-GEO-II2;NMI-IRON-AGE", "contested",
        "Existing wetland receives a wooded Atlantic-margin presentation.",
    ),
    "mediterranean_cultivation": (
        "P12.1;P12.3;BHR", "contested",
        "Crop-bearing Mediterranean field receives a cultivation presentation, not a yield estimate.",
    ),
    "african_aridity_gradient": (
        "P8.10;SOR-AFRICA-FRONTIER", "contested",
        "Arid upland non-crop field is represented as sparse rather than continuous grassland.",
    ),
    "asian_rice_lowland": (
        "P8.3;P8.4;CAH-XI;BHR", "contested",
        "Rice-bearing warm flatland represents managed alluvial or lowland cultivation.",
    ),
    "steppe_forest_mosaic": (
        "P8.8;AES-SOUTH-URAL;RAS-SARGAT-CHRON;ASU-ALTAI-KULAY;ENC-NEEU", "contested",
        "Continental flat forest is represented as a forest-steppe woodland mosaic.",
    ),
}


def rows(path: Path, comments: bool = False) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        source = (line for line in handle if not line.startswith("#")) if comments else handle
        return list(csv.DictReader(source))


def installed_entries() -> dict[str, dict[str, str]]:
    config = json.loads((ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig"))
    source = Path(config["game_dir"]) / "game/in_game/map_data/location_templates.txt"
    return {
        match["location"]: dict(FIELD.findall(match["body"]))
        for match in ENTRY.finditer(source.read_text(encoding="utf-8"))
    }


def owner_regions() -> dict[str, str]:
    roster = {row["tag"]: row["region"] for row in rows(ROSTER)}
    return {
        row["location"]: roster[row["tag"]]
        for row in rows(OWNERSHIP, comments=True)
    }


def geographic_scopes(
    entries: dict[str, dict[str, str]],
) -> tuple[dict[str, str], dict[str, str]]:
    hierarchy = json.loads(HIERARCHY.read_text(encoding="utf-8-sig"))
    region_keys = set(json.loads(REGIONS.read_text(encoding="utf-8-sig")))
    location_keys = set(entries)
    map_regions: dict[str, str] = {}
    map_areas: dict[str, str] = {}

    def descendants(root: str) -> set[str]:
        found: set[str] = set()
        stack = list(hierarchy.get(root, ()))
        seen: set[str] = set()
        while stack:
            key = stack.pop()
            if key in seen:
                continue
            seen.add(key)
            if key in location_keys:
                found.add(key)
            elif key in hierarchy:
                stack.extend(hierarchy[key])
        return found

    for region in sorted(region_keys):
        for location in descendants(region):
            if location in map_regions and map_regions[location] != region:
                raise ValueError(
                    f"location {location} occurs in map regions "
                    f"{map_regions[location]} and {region}"
                )
            map_regions[location] = region
        for area in hierarchy.get(region, ()):
            if not area.endswith("_area"):
                continue
            for location in descendants(area):
                if location in map_areas and map_areas[location] != area:
                    raise ValueError(
                        f"location {location} occurs in map areas "
                        f"{map_areas[location]} and {area}"
                    )
                map_areas[location] = area
    return map_regions, map_areas


def classify(
    location: str,
    region: str,
    map_region: str,
    map_area: str,
    fields: dict[str, str],
) -> tuple[str, dict[str, str]] | None:
    topography = fields.get("topography", "")
    vegetation = fields.get("vegetation", "")
    climate = fields.get("climate", "")
    good = fields.get("raw_material", "")

    if location in MARSH_GRASSLAND:
        return "mesopotamian_marsh", {
            "topography": "wetlands", "vegetation": "grasslands",
        }
    if location in MARSH_FARMLAND:
        return "mesopotamian_marsh", {
            "topography": "wetlands", "vegetation": "farmland",
        }
    if location in IRRIGATED_MESOPOTAMIA:
        return "mesopotamian_irrigation", {"vegetation": "farmland"}
    if (
        map_area in GERMAN_CORE_AREAS
        and vegetation == "grasslands"
        and topography in {"flatland", "hills", "plateau"}
        and good not in CROPS
    ):
        return "germania_central_mosaic", {"vegetation": "woods"}
    if (
        map_area in GERMAN_CORE_AREAS
        and vegetation == "woods"
        and topography in {"hills", "mountains", "plateau"}
        and good not in CROPS
    ):
        return "germania_upland_forest", {"vegetation": "forest"}
    if (
        region == "Germania"
        and vegetation == "grasslands"
        and good in FOREST_GOODS
    ):
        return "germania_forest_product", {"vegetation": "woods"}
    if region == "Germania" and vegetation == "woods" and good in FOREST_GOODS:
        return "germania_dense_woodland", {"vegetation": "forest"}
    if (
        map_region == "iberia_region"
        and map_area in IBERIAN_HUMID_AREAS
        and vegetation == "grasslands"
        and topography in {"flatland", "hills", "mountains", "plateau"}
        and good not in CROPS
    ):
        return "iberian_atlantic_mosaic", {"vegetation": "woods"}
    if (
        map_region == "iberia_region"
        and map_area in IBERIAN_HUMID_AREAS
        and vegetation == "sparse"
        and climate == "oceanic"
        and topography in {"hills", "mountains", "plateau"}
    ):
        return "iberian_atlantic_mosaic", {"vegetation": "woods"}
    if (
        map_region == "iberia_region"
        and map_area in IBERIAN_HUMID_AREAS
        and vegetation == "woods"
        and climate == "oceanic"
        and topography == "mountains"
    ):
        return "iberian_mountain_forest", {"vegetation": "forest"}
    if (
        map_region == "iberia_region"
        and map_area in IBERIAN_MOSAIC_AREAS
        and vegetation in {"grasslands", "sparse"}
        and topography in {"hills", "plateau"}
        and climate in {"mediterranean", "oceanic"}
        and good in IBERIAN_WOOD_PASTURE_GOODS
    ):
        return "iberian_wood_pasture_mosaic", {"vegetation": "woods"}
    if (
        region in {"Britain", "Ireland"}
        and vegetation in {"farmland", "grasslands"}
        and good in FOREST_GOODS
    ):
        return "atlantic_woodland", {"vegetation": "woods"}
    if (
        region in {"Britain", "Ireland"}
        and topography == "wetlands"
        and vegetation == "sparse"
    ):
        return "atlantic_wetland", {"vegetation": "woods"}
    if (
        region in MEDITERRANEAN_REGIONS
        and climate == "mediterranean"
        and vegetation == "grasslands"
        and good in CROPS
    ):
        return "mediterranean_cultivation", {"vegetation": "farmland"}
    if (
        region == "Africa"
        and climate in {"arid", "cold_arid"}
        and topography in {"hills", "plateau"}
        and vegetation == "grasslands"
        and good not in CROPS
    ):
        return "african_aridity_gradient", {"vegetation": "sparse"}
    if (
        region in ASIAN_REGIONS
        and topography == "flatland"
        and vegetation in {"grasslands", "woods"}
        and good == "rice"
    ):
        return "asian_rice_lowland", {
            "topography": "wetlands", "vegetation": "farmland",
        }
    if (
        region == "Steppe"
        and climate == "continental"
        and topography in {"flatland", "plateau"}
        and vegetation == "forest"
    ):
        return "steppe_forest_mosaic", {"vegetation": "woods"}
    return None


def landscape_changes() -> dict[str, dict[str, str]]:
    entries = installed_entries()
    regions = owner_regions()
    map_regions, map_areas = geographic_scopes(entries)
    changes: dict[str, dict[str, str]] = {}
    for location, region in sorted(regions.items()):
        if location not in entries:
            raise ValueError(f"controlled location {location} has no installed template")
        result = classify(
            location,
            region,
            map_regions.get(location, ""),
            map_areas.get(location, ""),
            entries[location],
        )
        if result is None:
            continue
        rule, updates = result
        if rule not in RULE_META:
            raise ValueError(f"landscape rule {rule} has no source contract")
        effective = {
            key: value
            for key, value in updates.items()
            if entries[location].get(key, "") != value
        }
        if effective:
            changes[location] = {"rule": rule, **effective}
    if len(changes) < 500:
        raise ValueError(f"landscape pass is unexpectedly small: {len(changes)}")
    return changes


def rendered() -> tuple[str, str, str, int]:
    entries = installed_entries()
    regions = owner_regions()
    map_regions, map_areas = geographic_scopes(entries)
    changes = landscape_changes()
    ledger_out = io.StringIO(newline="")
    writer = csv.writer(ledger_out, lineterminator="\n")
    writer.writerow((
        "location", "region", "map_region", "map_area", "rule",
        "old_topography", "new_topography",
        "old_vegetation", "new_vegetation", "climate", "raw_material",
        "source", "confidence", "note",
    ))
    after = {location: dict(fields) for location, fields in entries.items()}
    for location, change in sorted(changes.items()):
        fields = entries[location]
        rule = change["rule"]
        source, confidence, note = RULE_META[rule]
        after[location].update({
            key: value for key, value in change.items() if key != "rule"
        })
        writer.writerow((
            location,
            regions[location],
            map_regions.get(location, ""),
            map_areas.get(location, ""),
            rule,
            fields.get("topography", ""),
            after[location].get("topography", ""),
            fields.get("vegetation", ""),
            after[location].get("vegetation", ""),
            fields.get("climate", ""),
            fields.get("raw_material", ""),
            source,
            confidence,
            note,
        ))

    before_counts: Counter[tuple[str, str, str]] = Counter()
    after_counts: Counter[tuple[str, str, str]] = Counter()
    for location, region in regions.items():
        for dimension in ("topography", "vegetation", "climate"):
            before_counts[(region, dimension, entries[location].get(dimension, ""))] += 1
            after_counts[(region, dimension, after[location].get(dimension, ""))] += 1
    focus_map_regions = {
        "iberia_region", "north_german_region", "south_german_region",
    }
    for location, map_region in map_regions.items():
        if location not in regions or map_region not in focus_map_regions:
            continue
        scope = f"map:{map_region}"
        for dimension in ("topography", "vegetation", "climate"):
            before_counts[
                (scope, dimension, entries[location].get(dimension, ""))
            ] += 1
            after_counts[
                (scope, dimension, after[location].get(dimension, ""))
            ] += 1

    def vegetation_counts(scope: set[str]) -> Counter[str]:
        return Counter(after[location].get("vegetation", "") for location in scope)

    german_core = {
        location for location in regions
        if map_areas.get(location, "") in GERMAN_CORE_AREAS
    }
    iberia = {
        location for location in regions
        if map_regions.get(location, "") == "iberia_region"
    }
    north_german = {
        location for location in regions
        if map_regions.get(location, "") == "north_german_region"
    }
    south_german = {
        location for location in regions
        if map_regions.get(location, "") == "south_german_region"
    }
    if not all((german_core, iberia, north_german, south_german)):
        raise ValueError("priority landscape geography did not resolve")
    core_counts = vegetation_counts(german_core)
    iberia_counts = vegetation_counts(iberia)
    north_counts = vegetation_counts(north_german)
    south_counts = vegetation_counts(south_german)
    if core_counts["grasslands"] > 120:
        raise ValueError(
            f"central Germania retains {core_counts['grasslands']} grassland fields"
        )
    for area in sorted(GERMAN_CORE_AREAS):
        area_locations = {
            location for location in regions if map_areas.get(location, "") == area
        }
        if not area_locations:
            raise ValueError(f"central German audit area {area} did not resolve")
        area_counts = vegetation_counts(area_locations)
        area_grass = area_counts["grasslands"] / len(area_locations)
        area_woodland = (
            area_counts["forest"] + area_counts["woods"]
        ) / len(area_locations)
        if area_grass > 0.45:
            raise ValueError(
                f"{area} retains a {area_grass:.1%} grassland share"
            )
        if area_woodland < 0.50:
            raise ValueError(
                f"{area} woodland share fell below 50% ({area_woodland:.1%})"
            )
    if (north_counts["forest"] + north_counts["woods"]) / len(north_german) < 0.52:
        raise ValueError("north German woodland share fell below 52%")
    if (south_counts["forest"] + south_counts["woods"]) / len(south_german) < 0.62:
        raise ValueError("south German woodland share fell below 62%")
    iberian_woodland = iberia_counts["forest"] + iberia_counts["woods"]
    if iberian_woodland / len(iberia) < 0.43:
        raise ValueError("Iberian woodland share fell below 43%")
    iberian_open = iberia_counts["farmland"] + iberia_counts["grasslands"]
    if iberian_open / len(iberia) < 0.30:
        raise ValueError("Iberian open cultivation share fell below 30%")
    cereal_openings = sum(
        after[location].get("vegetation", "") in {"farmland", "grasslands"}
        and entries[location].get("raw_material", "") in CROPS
        for location in iberia
    )
    if cereal_openings < 70:
        raise ValueError(
            f"Iberia retains only {cereal_openings} open crop-bearing fields"
        )
    for area in sorted(IBERIAN_HUMID_AREAS):
        area_locations = {
            location for location in iberia if map_areas.get(location, "") == area
        }
        if not area_locations:
            raise ValueError(f"humid Iberian audit area {area} did not resolve")
        area_counts = vegetation_counts(area_locations)
        area_woodland = (
            area_counts["forest"] + area_counts["woods"]
        ) / len(area_locations)
        if area_woodland < 0.60:
            raise ValueError(
                f"{area} woodland share fell below 60% ({area_woodland:.1%})"
            )
    distribution_out = io.StringIO(newline="")
    distribution_writer = csv.writer(distribution_out, lineterminator="\n")
    distribution_writer.writerow(("region", "dimension", "value", "before", "after", "delta"))
    for key in sorted(set(before_counts) | set(after_counts)):
        before = before_counts[key]
        final = after_counts[key]
        distribution_writer.writerow((*key, before, final, final - before))

    rule_counts = Counter(change["rule"] for change in changes.values())
    region_counts = Counter(regions[location] for location in changes)
    summary = [
        "# AD 1 Landscape Audit",
        "",
        "Generated by `tools/m5_landscape.py` from the installed template surface.",
        "Map geometry, rivers, coasts, and adjacency are untouched.",
        "",
        f"- {len(regions):,} controlled locations audited.",
        f"- {len(changes):,} sourced presentation changes.",
        f"- {sum('topography' in row for row in changes.values()):,} topography changes.",
        f"- {sum('vegetation' in row for row in changes.values()):,} vegetation changes.",
        "- Climate changes: 0.",
        f"- Central German core: {core_counts['grasslands']:,} grasslands; "
        f"{core_counts['forest'] + core_counts['woods']:,} forest/woods.",
        f"- North German map region: "
        f"{(north_counts['forest'] + north_counts['woods']) / len(north_german):.1%} "
        "forest/woods.",
        f"- South German map region: "
        f"{(south_counts['forest'] + south_counts['woods']) / len(south_german):.1%} "
        "forest/woods.",
        f"- Iberian map region: {iberian_woodland / len(iberia):.1%} forest/woods; "
        f"{iberian_open / len(iberia):.1%} open cultivation; "
        f"{cereal_openings:,} open crop-bearing fields.",
        "",
        "## Rules",
        "",
    ]
    summary.extend(f"- {key}: {value:,}" for key, value in sorted(rule_counts.items()))
    summary.extend(("", "## Regions changed", ""))
    summary.extend(f"- {key}: {value:,}" for key, value in sorted(region_counts.items()))
    summary.extend((
        "",
        "These are coarse engine presentation classes, not palaeoenvironmental",
        "reconstructions or quantified ancient land cover.",
        "",
    ))
    return (
        ledger_out.getvalue(),
        distribution_out.getvalue(),
        "\n".join(summary),
        len(changes),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        ledger, distribution, summary, count = rendered()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"m5_landscape: FAIL\n  - {exc}")
        return 1
    outputs = (
        (LEDGER, ledger, "utf-8-sig"),
        (DISTRIBUTION, distribution, "utf-8-sig"),
        (SUMMARY, summary, "utf-8"),
    )
    if args.write:
        for path, value, encoding in outputs:
            path.write_text(value, encoding=encoding, newline="\n")
        print(f"m5_landscape: wrote {count} sourced changes")
        return 0
    failures = [
        f"stale or missing {path.relative_to(ROOT)}"
        for path, value, encoding in outputs
        if not path.is_file() or path.read_text(encoding=encoding) != value
    ]
    if failures:
        print("m5_landscape: FAIL\n  - " + "\n  - ".join(failures))
        return 1
    print(f"m5_landscape: PASS ({count} sourced changes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
