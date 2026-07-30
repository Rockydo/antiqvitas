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


def classify(
    location: str,
    region: str,
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
        region == "Germania"
        and vegetation == "grasslands"
        and good in FOREST_GOODS
    ):
        return "germania_forest_product", {"vegetation": "woods"}
    if region == "Germania" and vegetation == "woods" and good in FOREST_GOODS:
        return "germania_dense_woodland", {"vegetation": "forest"}
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
    changes: dict[str, dict[str, str]] = {}
    for location, region in sorted(regions.items()):
        if location not in entries:
            raise ValueError(f"controlled location {location} has no installed template")
        result = classify(location, region, entries[location])
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
    if len(changes) < 300:
        raise ValueError(f"landscape pass is unexpectedly small: {len(changes)}")
    return changes


def rendered() -> tuple[str, str, str, int]:
    entries = installed_entries()
    regions = owner_regions()
    changes = landscape_changes()
    ledger_out = io.StringIO(newline="")
    writer = csv.writer(ledger_out, lineterminator="\n")
    writer.writerow((
        "location", "region", "rule", "old_topography", "new_topography",
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
