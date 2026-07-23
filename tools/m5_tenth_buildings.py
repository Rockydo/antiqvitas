#!/usr/bin/env python3
"""Generate the tenth twelve-family regional M5 building pass."""

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
LOCATIONS = (("rome", "Europe"), ("lyon", "Europe"), ("alexandria", "North Africa"), ("tunis", "North Africa"), ("antioch", "Middle East"), ("damascus", "Middle East"), ("patna", "South Asia"), ("khambat", "South Asia"), ("chengdu", "East Asia"), ("jingzhao", "East Asia"))
FAMILIES_TO_ADD = (
    ("combmaker", "Combmaker", "A reusable ivory and bone comb-cutting bench for ordinary grooming and small luxury goods.", "consumer_goods_category", "local_production_efficiency=0.015", "ivory=0.06;tools=0.03", "ivory;tools", "Ancient combmaker with carved ivory and bone combs fine saw and small workbench"),
    ("bell_foundry", "Bell Foundry", "A reusable bronze bell and small-casting workshop for civic ritual, animals, and market fittings.", "basic_industry_category", "local_production_efficiency=0.02", "copper=0.10;tin=0.03;coal=0.04;tools=0.03", "copper;tin;coal;tools", "Ancient bronze bell foundry with clay molds small bells crucible and charcoal hearth"),
    ("oarwright", "Oarwright", "A reusable workshop for river and coastal oars, thole pins, and light craft fittings.", "basic_industry_category", "local_production_efficiency=0.02", "lumber=0.14;fiber_crops=0.05;tar=0.03;tools=0.03", "lumber;fiber_crops;tar;tools", "Ancient oarwright with long wooden oars boat stern shavings and riverbank workbench"),
    ("spindlework", "Spindlework", "A reusable spinning and spindle-fitting workshop preparing fiber for regional cloth production.", "consumer_goods_category", "local_production_efficiency=0.02", "fiber_crops=0.12;clay=0.03;tools=0.02", "fiber_crops;clay;tools", "Ancient spindlework room with upright spindles spun fiber clay whorls and woven baskets"),
    ("torchmaker", "Torchmaker", "A reusable workshop for beeswax torches, wick bundles, and practical lighting supplies.", "consumer_goods_category", "local_merchant_capacity=0.01", "beeswax=0.10;fiber_crops=0.04;pottery=0.03;tools=0.02", "beeswax;fiber_crops;pottery;tools", "Ancient beeswax torchmaker with bundled torches clay lamps wick strands and wax cakes"),
    ("sieve_maker", "Sieve Maker", "A reusable reed-sieve and grain-sorting workshop for household and market handling.", "consumer_goods_category", "local_merchant_capacity=0.01", "fiber_crops=0.12;lumber=0.04;tools=0.02", "fiber_crops;lumber;tools", "Ancient sieve maker with round woven reed sieves grain basket and bundled cane"),
    ("mortar_grinder", "Mortar and Pestle Workshop", "A reusable stone-grinding workshop for culinary, dye, and apothecary implements.", "basic_industry_category", "local_production_efficiency=0.02", "stone=0.12;iron=0.03;tools=0.03", "stone;iron;tools", "Ancient mortar and pestle workshop with stone bowls crushed herbs chisels and grinding tools"),
    ("seal_cutter", "Seal Cutter", "A reusable gem and seal-cutting bench for small personal and administrative objects.", "consumer_goods_category", "local_production_efficiency=0.015", "goods_gold=0.04;tools=0.03;dyes=0.02", "goods_gold;tools;dyes", "Ancient gem and seal cutter with engraved stones bow drill fine tools and wax seals"),
    ("kiln_furniture", "Kiln Furniture Workshop", "A reusable workshop for ceramic firing supports, shelves, and kiln accessories.", "basic_industry_category", "local_production_efficiency=0.02", "clay=0.14;lumber=0.06;tools=0.03", "clay;lumber;tools", "Ancient kiln furniture workshop with clay firing supports shelves props and domed kiln"),
    ("reed_pen_maker", "Reed-Pen Maker", "A reusable cutting and finishing workshop for reed pens, ink containers, and routine writing tools.", "consumer_goods_category", "local_clergy_max_literacy=0.01", "paper=0.08;dyes=0.03;lumber=0.03;tools=0.02", "paper;dyes;lumber;tools", "Ancient reed-pen maker with cut reeds ink jar papyrus sheet and trimming knife"),
    ("sail_needle_shop", "Sail-Needle Shop", "A reusable repair workshop for sail needles, awls, thread, and patched cloth.", "basic_industry_category", "local_production_efficiency=0.02", "lumber=0.08;fiber_crops=0.08;tar=0.04;cloth=0.04;tools=0.03", "lumber;fiber_crops;tar;cloth;tools", "Ancient sail-needle shop with patched sailcloth bronze needles awls and rope coil"),
    ("pulley_workshop", "Pulley Workshop", "A reusable woodworking shop for rope pulleys, tackle, and lifting fittings for trade and craft.", "basic_industry_category", "local_production_efficiency=0.02", "lumber=0.12;fiber_crops=0.08;tar=0.04;tools=0.03", "lumber;fiber_crops;tar;tools", "Ancient pulley workshop with wooden grooved wheels rope tackle timber pegs and dockside tools"),
)


def read(path: Path, fields: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != fields:
            raise ValueError(f"{path.relative_to(ROOT)} header mismatch")
        # The established ledger reader intentionally consumes only its fixed
        # declared columns; retain that compatibility for legacy rows whose
        # free-text icon subject contains a historical unescaped comma.
        return [{field: row.get(field, "") for field in fields} for row in reader]


def render(path: Path, fields: tuple[str, ...], rows: list[dict[str, str]]) -> str:
    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader(); writer.writerows(rows)
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
            seed_rows.append({"key": f"reg_tenth_{location}_{slug}", "family": family, "location": location, "macro": macro, "source": SOURCE, "confidence": "contested", "note": NOTE})
    return {FAMILIES: render(FAMILIES, FAMILY_FIELDS, family_rows), SEEDS: render(SEEDS, SEED_FIELDS, seed_rows)}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--write", action="store_true"); parser.add_argument("--check", action="store_true"); args = parser.parse_args()
    if args.write == args.check: parser.error("provide exactly one of --write or --check")
    try: expected = outputs()
    except (OSError, ValueError) as exc: print(f"m5_tenth_buildings: FAIL\n  - {exc}"); return 1
    if args.write:
        for path, content in expected.items(): path.write_text(content, encoding="utf-8-sig", newline="")
        print("m5_tenth_buildings: wrote 12 families and 120 placements"); return 0
    stale = [path.relative_to(ROOT) for path, content in expected.items() if path.read_text(encoding="utf-8-sig") != content]
    if stale: print(f"m5_tenth_buildings: FAIL\n  - stale or missing {stale}"); return 1
    print("m5_tenth_buildings: PASS (12 families; 120 placements)"); return 0


if __name__ == "__main__": raise SystemExit(main())
