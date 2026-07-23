#!/usr/bin/env python3
"""Generate the eleventh twelve-family M5 productive-craft expansion."""

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
SOURCE = "P12.1;P12.3;MET-ROMAN-TRADE"
NOTE = "Regional city-and-hinterland productive-craft proxy rather than a named workshop owner output total or route."
LOCATIONS = (
    ("rome", "Europe"), ("lyon", "Europe"), ("ravenna", "Europe"), ("cordoba", "Europe"),
    ("bordeaux", "Europe"), ("alexandria", "North Africa"),
    ("tunis", "North Africa"), ("antioch", "Middle East"), ("damascus", "Middle East"),
    ("jerusalem", "Middle East"),
)
FAMILIES_TO_ADD = (
    ("locksmith", "Locksmith", "A reusable workshop for bronze and iron locks, keys, hinges, and secure fittings.", "basic_industry_category", "local_production_efficiency=0.02", "copper=0.06;iron=0.06;coal=0.03;tools=0.03", "copper;iron;coal;tools", "Ancient locksmith bench with bronze keys lock plates hinges and small chisels"),
    ("nailery", "Nailery", "A reusable forge turning iron stock into nails, rivets, and ordinary construction fastenings.", "basic_industry_category", "local_production_efficiency=0.02", "iron=0.10;coal=0.05;tools=0.03", "iron;coal;tools", "Ancient iron nail forge with anvil nail rods tongs and charcoal hearth"),
    ("chainmaker", "Chainmaker", "A reusable forge for linked iron chain, hooks, and heavy transport fittings.", "basic_industry_category", "local_production_efficiency=0.02", "iron=0.11;coal=0.05;tools=0.03", "iron;coal;tools", "Ancient chainmaker forge with linked iron chain hooks anvil and charcoal furnace"),
    ("wiredrawer", "Wire Drawer", "A reusable bench drawing fine bronze wire for fittings, jewelry, and instrument work.", "consumer_goods_category", "local_production_efficiency=0.015", "copper=0.09;tin=0.02;tools=0.03", "copper;tin;tools", "Ancient bronze wire drawing bench with drawplate coils of wire and hand tools"),
    ("shieldmaker", "Shieldmaker", "A reusable workshop assembling wooden and leather shields with metal fittings for civic and military demand.", "weapons_industry_category", "local_garrison_size=0.01", "lumber=0.12;leather=0.08;iron=0.03;tools=0.04", "lumber;leather;iron;tools", "Ancient shieldmaker workshop with oval shields wood leather bosses and fitting tools"),
    ("scabbard_maker", "Scabbard Maker", "A reusable leather and metal fitting shop for sword sheaths, straps, and repaired weapon furniture.", "weapons_industry_category", "local_garrison_size=0.01", "leather=0.10;copper=0.03;iron=0.02;tools=0.03", "leather;copper;iron;tools", "Ancient scabbard maker bench with leather sword sheath bronze fittings awls and knives"),
    ("fishing_tackle", "Fishing-Tackle Workshop", "A reusable workshop for nets, hooks, floats, cord, and coastal fishing gear.", "naval_category", "local_sailors=0.008", "fiber_crops=0.10;iron=0.03;lumber=0.04;tools=0.03", "fiber_crops;iron;lumber;tools", "Ancient fishing tackle workshop with nets hooks floats cord coils and wooden rack"),
    ("feltworks", "Feltworks", "A reusable fulling and pressing yard for dense felt cloth, mats, and practical coverings.", "consumer_goods_category", "local_production_efficiency=0.02", "wool=0.13;cloth=0.04;tools=0.02", "wool;cloth;tools", "Ancient feltmaking workshop with wool mats water vat bow and pressing bench"),
    ("carpet_loom", "Carpet Loom", "A reusable upright loom for patterned woolen coverings and durable household textiles.", "consumer_goods_category", "local_production_efficiency=0.02", "wool=0.12;dyes=0.04;tools=0.02", "wool;dyes;tools", "Ancient carpet loom with patterned wool textile thread spools and upright wooden frame"),
    ("cork_workshop", "Cork Workshop", "A reusable cutting and finishing workshop for cork stoppers, floats, and light fittings.", "consumer_goods_category", "local_merchant_capacity=0.01", "lumber=0.10;fiber_crops=0.04;tools=0.02", "lumber;fiber_crops;tools", "Ancient cork workshop with cork bark stoppers knives basket and wooden workbench"),
    ("brushmaker", "Brushmaker", "A reusable workshop for bristle brushes, wooden handles, and cleaning or finishing tools.", "consumer_goods_category", "local_merchant_capacity=0.01", "livestock=0.06;lumber=0.08;fiber_crops=0.03;tools=0.02", "livestock;lumber;fiber_crops;tools", "Ancient brushmaker bench with bristle brushes wooden handles twine and cutting knife"),
    ("tesserae_kiln", "Tesserae Kiln", "A reusable kiln and sorting yard for colored glass and stone mosaic cubes.", "basic_industry_category", "local_production_efficiency=0.02", "glass=0.08;stone=0.08;clay=0.05;lumber=0.05;tools=0.03", "glass;stone;clay;lumber;tools", "Ancient mosaic tesserae kiln with colored glass stone cubes clay bowls and small domed furnace"),
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
    current_families = read(FAMILIES, FAMILY_FIELDS)
    family_at = next((index for index, row in enumerate(current_families) if row["key"] in keys), len(current_families))
    family_rows = [row for row in current_families if row["key"] not in keys]
    additions = []
    for slug, name, description, category, modifier, maintenance, goods, subject in FAMILIES_TO_ADD:
        additions.append({"key": f"antq_reg_{slug}", "name": name, "description": description, "category": category, "pop_type": "burghers", "employment_size": "guild_employment", "build_time": "guild_build_time", "modifier": modifier, "maintenance": maintenance, "goods": goods, "source": SOURCE, "confidence": "contested", "note": "A broad antique craft proxy rather than a named workshop, owner, output, or route.", "icon_subject": subject})
    family_rows[family_at:family_at] = additions
    current_seeds = read(SEEDS, SEED_FIELDS)
    seed_at = next((index for index, row in enumerate(current_seeds) if row["family"] in keys), len(current_seeds))
    seed_rows = [row for row in current_seeds if row["family"] not in keys]
    seed_additions = []
    for slug, *_ in FAMILIES_TO_ADD:
        family = f"antq_reg_{slug}"
        for location, macro in LOCATIONS:
            seed_additions.append({"key": f"reg_eleventh_{location}_{slug}", "family": family, "location": location, "macro": macro, "source": SOURCE, "confidence": "contested", "note": NOTE})
    seed_rows[seed_at:seed_at] = seed_additions
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
        print(f"m5_eleventh_buildings: FAIL\n  - {exc}")
        return 1
    if args.write:
        for path, content in expected.items():
            path.write_text(content, encoding="utf-8-sig", newline="")
        print("m5_eleventh_buildings: wrote 12 families and 120 placements")
        return 0
    stale = [path.relative_to(ROOT) for path, content in expected.items() if not path.is_file() or path.read_text(encoding="utf-8-sig") != content]
    if stale:
        print(f"m5_eleventh_buildings: FAIL\n  - stale or missing {stale}")
        return 1
    print("m5_eleventh_buildings: PASS (12 families; 120 placements)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
