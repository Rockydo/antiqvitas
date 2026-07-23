#!/usr/bin/env python3
"""Generate the twelfth twelve-family M5 productive-economy expansion.

The choices deliberately add calibrated finished-good production, rather than
another layer of local modifiers: medicine, fine textiles, fermentation,
masonry, and ironworking were central to classical urban demand.
"""

from __future__ import annotations

import argparse
import csv
from io import StringIO
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FAMILIES = ROOT / "docs/m5/regional_building_families.csv"
SEEDS = ROOT / "docs/m5/regional_building_seeds.csv"
FAMILY_FIELDS = ("key", "name", "description", "category", "pop_type", "employment_size", "build_time", "modifier", "maintenance", "goods", "source", "confidence", "note", "icon_subject")
SEED_FIELDS = ("key", "family", "location", "macro", "source", "confidence", "note")
SOURCE = "P12.1;P12.3;P14"
NOTE = "Regional city-and-hinterland productive-craft proxy rather than a named workshop, owner, output total, or route."
# A deliberately Rome-centred, eastern-Mediterranean commercial surface.  The
# city points are already controlled and macro-checked in the M5 ledger.
LOCATIONS = (
    ("rome", "Europe"), ("lyon", "Europe"), ("ravenna", "Europe"), ("cordoba", "Europe"),
    ("alexandria", "North Africa"), ("tunis", "North Africa"),
    ("antioch", "Middle East"), ("damascus", "Middle East"), ("jerusalem", "Middle East"), ("sidon", "Middle East"),
)
FAMILIES_TO_ADD = (
    ("herbal_apothecary", "Herbal Apothecary", "A reusable workshop preparing plant remedies, ointments, and simple medicinal compounds.", "consumer_goods_category", "local_life_expectancy=0.01", "wild_game=0.05;fiber_crops=0.19", "wild_game;fiber_crops", "Ancient herbal apothecary with dried plants stone mortar and small ceramic jars"),
    ("wool_drapery", "Wool Drapery", "A reusable weaving workshop turning wool into finer cloth for urban and regional demand.", "consumer_goods_category", "local_production_efficiency=0.02", "wool=0.12;tools=0.03", "wool;tools", "Ancient wool drapery with upright loom folded wool cloth and yarn baskets"),
    ("silk_drapery", "Silk Drapery", "A reusable loom-house finishing imported or eastern silk into high-value cloth.", "consumer_goods_category", "local_production_efficiency=0.02", "silk=0.10;tools=0.03", "silk;tools", "Ancient silk drapery with loom silk bolts spools and a small wooden shuttle"),
    ("dye_finishing_house", "Dye Finishing House", "A reusable finishing yard for alum-fixed dyes and high-value colored cloth.", "consumer_goods_category", "local_production_efficiency=0.02", "alum=0.05;dyes=0.10;cloth=0.05;tools=0.03", "alum;dyes;cloth;tools", "Ancient textile dye finishing house with dye vat colored cloth and ceramic pigment bowls"),
    ("wheat_brewery", "Wheat Brewery", "A reusable fermentation house for grain drink, represented by the engine's generic beer good.", "consumer_goods_category", "local_merchant_capacity=0.01", "wheat=0.12;lumber=0.05;tools=0.03", "wheat;lumber;tools", "Ancient wheat brewery with wheat sheaves fermentation amphorae and ceramic cups"),
    ("millet_brewery", "Millet Brewery", "A reusable fermentation house for millet drink, represented by the engine's generic beer good.", "consumer_goods_category", "local_merchant_capacity=0.01", "millet=0.12;lumber=0.05;tools=0.03", "millet;lumber;tools", "Ancient millet brewery with millet ears earthen fermentation jars and grain baskets"),
    ("fruit_brewery", "Fruit Fermenting House", "A reusable press and fermentation house for fruit drink, represented by the engine's generic beer good.", "consumer_goods_category", "local_merchant_capacity=0.01", "fruit=0.12;lumber=0.05;tools=0.03", "fruit;lumber;tools", "Ancient fruit fermenting house with wooden press fruit baskets clay jars and pressed must"),
    ("rice_brewery", "Rice Fermenting House", "A reusable fermentation house for rice drink, represented by the engine's generic beer good.", "consumer_goods_category", "local_merchant_capacity=0.01", "rice=0.12;lumber=0.05;tools=0.03", "rice;lumber;tools", "Ancient rice fermenting house with rice bundles ceramic jars and a woven mat"),
    ("stone_masonry_yard", "Stone Masonry Yard", "A reusable cutting yard supplying dressed stone and construction masonry.", "basic_industry_category", "local_production_efficiency=0.02", "stone=0.12;tools=0.03", "stone;tools", "Ancient stone masonry yard with dressed blocks wooden mallet chisels and chips"),
    ("clay_brickworks", "Clay Brickworks", "A reusable brick yard firing clay construction material for urban building demand.", "basic_industry_category", "local_production_efficiency=0.02", "clay=0.14;lumber=0.05;tools=0.03", "clay;lumber;tools", "Ancient clay brickworks with stacked fired bricks small kiln clay basin and wooden moulds"),
    ("crucible_steel_workshop", "Crucible Steel Workshop", "A reusable high-heat ironworking shop producing the engine's steel good without asserting a named ancient works.", "basic_industry_category", "local_production_efficiency=0.02", "iron=0.14;coal=0.12;tools=0.04", "iron;coal;tools", "Ancient crucible steel workshop with clay crucibles charcoal hearth tongs and dark iron billets"),
    ("materia_medica", "Materia Medica Workshop", "A reusable specialist workshop for mineral and animal-derived medicinal compounds.", "consumer_goods_category", "local_life_expectancy=0.01", "mercury=0.02;ivory=0.05;tools=0.03", "mercury;ivory;tools", "Ancient materia medica workshop with stone mortar dried roots ceramic jars and small scales"),
)


def read(path: Path, fields: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != fields:
            raise ValueError(f"{path.relative_to(ROOT)} header mismatch")
        return [{field: row.get(field, "") for field in fields} for row in reader]


def render(fields: tuple[str, ...], rows: list[dict[str, str]]) -> str:
    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def outputs() -> dict[Path, str]:
    keys = {f"antq_reg_{item[0]}" for item in FAMILIES_TO_ADD}
    family_rows = [row for row in read(FAMILIES, FAMILY_FIELDS) if row["key"] not in keys]
    for slug, name, description, category, modifier, maintenance, goods, subject in FAMILIES_TO_ADD:
        family_rows.append({"key": f"antq_reg_{slug}", "name": name, "description": description, "category": category, "pop_type": "burghers", "employment_size": "guild_employment", "build_time": "guild_build_time", "modifier": modifier, "maintenance": maintenance, "goods": goods, "source": SOURCE, "confidence": "contested", "note": "A broad antique craft proxy rather than a named workshop, owner, output, or route.", "icon_subject": subject})
    seed_rows = [row for row in read(SEEDS, SEED_FIELDS) if row["family"] not in keys]
    for slug, *_ in FAMILIES_TO_ADD:
        family = f"antq_reg_{slug}"
        for location, macro in LOCATIONS:
            seed_rows.append({"key": f"reg_twelfth_{location}_{slug}", "family": family, "location": location, "macro": macro, "source": SOURCE, "confidence": "contested", "note": NOTE})
    return {FAMILIES: render(FAMILY_FIELDS, family_rows), SEEDS: render(SEED_FIELDS, seed_rows)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        expected = outputs()
    except (OSError, ValueError) as exc:
        print(f"m5_twelfth_buildings: FAIL\n  - {exc}")
        return 1
    if args.write:
        for path, content in expected.items():
            path.write_text(content, encoding="utf-8-sig", newline="")
        print("m5_twelfth_buildings: wrote 12 families and 120 placements")
        return 0
    stale = [path.relative_to(ROOT) for path, content in expected.items() if not path.is_file() or path.read_text(encoding="utf-8-sig") != content]
    if stale:
        print(f"m5_twelfth_buildings: FAIL\n  - stale or missing {stale}")
        return 1
    print("m5_twelfth_buildings: PASS (12 families; 120 placements)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
