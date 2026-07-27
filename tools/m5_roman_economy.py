#!/usr/bin/env python3
"""Generate the layered Roman provincial economy expansion.

The profile ledger records market-scale development portfolios rather than
claiming that every named structure existed in every engine location polygon.
"""

from __future__ import annotations

import argparse
import csv
from io import StringIO
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FAMILIES = ROOT / "docs/m5/regional_building_families.csv"
SEEDS = ROOT / "docs/m5/regional_building_seeds.csv"
PROFILES = ROOT / "docs/m5/roman_economy_profiles.csv"
URBAN_NODES = ROOT / "docs/m5/urban_nodes.csv"
FAMILY_FIELDS = (
    "key", "name", "description", "category", "pop_type", "employment_size",
    "build_time", "modifier", "maintenance", "goods", "source", "confidence",
    "note", "icon_subject",
)
SEED_FIELDS = ("key", "family", "location", "macro", "source", "confidence", "note")
PROFILE_FIELDS = ("profile", "name", "locations", "families", "source", "confidence", "note")
URBAN_FIELDS = ("key", "location", "profile", "source", "confidence", "note")
SOURCE = "P12.1;P12.3;CAH-XI;MET-ROMAN-HOUSING;MET-ROMAN-TRADE"
NOTE = "Roman provincial market-scale portfolio proxy; not a named workshop, owner, quantified output, or excavated plan."

# slug, name, description, category, pop, employment, build time, modifier,
# maintenance, goods, visual subject
FAMILIES_TO_ADD = (
    ("villa_rustica", "Villa Rustica", "A scalable estate centre coordinating grain, vines, olives, storage, and rural labor for a nearby market.", "basic_industry_category", "laborers", "generic_peasant_building_employment", "guild_build_time", "local_monthly_food_modifier=0.01;local_population_capacity=0.01", "wheat=0.14;lumber=0.05;tools=0.03", "wheat;lumber;tools", "Early imperial Roman villa rustica work court with tiled farmhouse grain jars olive baskets and wooden farm tools"),
    ("tabernae_row", "Tabernae Row", "A scalable row of street-front shops and workshops connecting households to an urban market.", "trade_category", "burghers", "trade_employment", "market_build_time", "local_merchant_capacity=0.015;local_merchant_power=0.01", "pottery=0.05;lumber=0.05;tools=0.02", "pottery;lumber;tools", "Roman tabernae street row with open wooden shop fronts amphorae scales awnings and stone pavement"),
    ("forum_basilica", "Forum Basilica", "A scalable civic-commercial hall for adjudication, contracts, exchange, and public business.", "government_category", "burghers", "trade_employment", "government_build_time", "local_max_control=0.01;local_merchant_power=0.015", "stone=0.10;marble=0.04;lumber=0.05;tools=0.03", "stone;marble;lumber;tools", "Augustan Roman forum basilica interior with columned nave tribunal merchants wax tablets and restrained civic statuary"),
    ("horrea_complex", "Horrea Complex", "A scalable warehouse complex for grain, oil, wine, equipment, and redistributive storage.", "infrastructure_category", "laborers", "trade_employment", "infrastructure_build_time", "local_monthly_food_modifier=0.02;local_merchant_capacity=0.01", "lumber=0.08;stone=0.06;pottery=0.06;tools=0.03", "lumber;stone;pottery;tools", "Roman horrea warehouse courtyard with raised storerooms grain sacks amphora stacks hand carts and guarded doors"),
    ("annona_bakery", "Annona Bakery", "A scalable mill-and-oven complex turning public and market grain into urban staples.", "consumer_goods_category", "burghers", "guild_employment", "guild_build_time", "local_monthly_food_modifier=0.02;local_production_efficiency=0.01", "wheat=0.16;lumber=0.06;stone=0.04;tools=0.03", "wheat;lumber;stone;tools", "Roman commercial bakery with donkey millstone domed ovens bread loaves grain sacks and terracotta counters"),
    ("aqueduct_distribution", "Aqueduct Distribution Works", "A scalable network of settling tanks, conduits, fountains, and local water distribution.", "infrastructure_category", "laborers", "generic_peasant_building_employment", "infrastructure_build_time", "local_disease_resistance=0.01;local_population_capacity=0.02", "stone=0.12;lead=0.05;clay=0.05;tools=0.04", "stone;lead;clay;tools", "Roman aqueduct distribution castellum with masonry channels lead pipes settling basin and public fountain"),
    ("thermae_complex", "Public Thermae", "A scalable public bathing complex supporting hygiene, sociability, and dense urban life.", "cultural_category", "burghers", "cultural_employment", "cultural_building_time", "local_disease_resistance=0.01;local_life_expectancy=0.005", "stone=0.10;marble=0.04;coal=0.06;lumber=0.06;tools=0.03", "stone;marble;coal;lumber;tools", "Early imperial Roman public baths with vaulted frigidarium marble basin hypocaust vents and bronze bathing vessels"),
    ("cursus_mansio", "Cursus Publicus Mansio", "A scalable road station for official couriers, remounts, travelers, records, and state dispatches.", "government_category", "burghers", "trade_employment", "infrastructure_build_time", "local_max_control=0.015;local_merchant_capacity=0.005", "lumber=0.08;livestock=0.06;leather=0.03;tools=0.03", "lumber;livestock;leather;tools", "Roman roadside mansio courtyard with milestone courier horse covered cart writing tablet and tiled lodging"),
    ("river_port", "River and Coastal Portus", "A scalable quay, landing, store, and handling space connecting inland supply to maritime markets.", "trade_category", "soldiers", "dock_employment", "medium_port_building_time", "local_merchant_capacity=0.015;local_sailors=0.008", "lumber=0.12;naval_supplies=0.06;fiber_crops=0.04;tools=0.04", "lumber;naval_supplies;fiber_crops;tools", "Roman river portus with stone quay grain barge mast crane amphorae rope coils and warehouse frontage"),
    ("colonia_forum", "Colonia Civic Forum", "A scalable civic centre for municipal administration, cult, market exchange, and local incorporation.", "government_category", "burghers", "trade_employment", "government_build_time", "local_max_control=0.015;local_cultural_tradition=0.005", "stone=0.10;marble=0.03;lumber=0.05;tools=0.03", "stone;marble;lumber;tools", "Roman colonia forum with compact temple basilica market stalls inscribed altar and paved public square"),
    ("castra_fabrica", "Castra Fabrica", "A scalable military workshop producing and repairing arms, fittings, carts, and camp equipment.", "weapons_industry_category", "burghers", "guild_employment", "guild_build_time", "local_garrison_size=0.015;local_repair_speed=0.01", "iron=0.12;lumber=0.08;leather=0.05;tools=0.04", "iron;lumber;leather;tools", "Roman legionary fabrica inside timber earth camp with forge armor tools shield fittings cart parts and standards"),
    ("frontier_magazine", "Frontier Supply Magazine", "A scalable protected store for grain, equipment, fodder, and replacement material on military routes.", "defense_category", "soldiers", "stockade_employment", "small_fort_building", "local_garrison_size=0.02;local_repair_speed=0.01", "wheat=0.10;lumber=0.08;leather=0.03;tools=0.03", "wheat;lumber;leather;tools", "Early Roman frontier magazine with timber palisade raised granary supply carts shield racks and grain sacks"),
    ("quarry_contractors", "Quarry Contractors' Yard", "A scalable organization of cutters, haulers, cranes, and dressed building stone for public and private works.", "basic_industry_category", "laborers", "guild_employment", "guild_build_time", "local_production_efficiency=0.02", "stone=0.12;lumber=0.06;tools=0.04", "stone;lumber;tools", "Roman quarry contractors yard with dressed blocks column drum treadwheel crane sledges chisels and ox cart"),
    ("olive_estate", "Olive Estate", "A scalable estate complex integrating groves, crushing, pressing, settling, and amphora storage.", "basic_industry_category", "laborers", "generic_peasant_building_employment", "guild_build_time", "local_production_efficiency=0.02", "olives=0.16;pottery=0.06;lumber=0.04;tools=0.04", "olives;pottery;lumber;tools", "Roman olive estate with grove stone crusher beam press settling jars workers and tiled storage wing"),
    ("vineyard_estate", "Vineyard Estate", "A scalable estate complex integrating vineyards, pressing, fermentation, and amphora storage.", "basic_industry_category", "laborers", "generic_peasant_building_employment", "guild_build_time", "local_production_efficiency=0.02", "fruit=0.16;pottery=0.06;lumber=0.04;tools=0.04", "fruit;pottery;lumber;tools", "Roman vineyard estate with vine rows wooden press fermentation vats amphorae pruning knives and tiled villa"),
    ("textile_quarter", "Textile Quarter", "A scalable concentration of spinning, weaving, fulling, dyeing, drying, and cloth merchants.", "consumer_goods_category", "burghers", "guild_employment", "guild_build_time", "local_production_efficiency=0.025", "wool=0.12;fiber_crops=0.08;dyes=0.03;tools=0.03", "wool;fiber_crops;dyes;tools", "Roman textile quarter courtyard with upright looms fulling vats dyed wool cloth drying racks and baskets"),
    ("ceramic_quarter", "Ceramic Quarter", "A scalable concentration of clay preparation, kilns, amphorae, lamps, tiles, and tableware.", "basic_industry_category", "burghers", "guild_employment", "guild_build_time", "local_production_efficiency=0.025", "clay=0.16;lumber=0.08;tools=0.04", "clay;lumber;tools", "Roman ceramic quarter with multiple updraft kilns amphora stacks oil lamps tiles potters wheels and clay pits"),
    ("insulae_quarter", "Insulae Quarter", "A scalable mixed residential-commercial quarter of apartments, courtyards, shops, and neighborhood services.", "infrastructure_category", "laborers", "generic_peasant_building_employment", "infrastructure_build_time", "local_population_capacity=0.025;local_merchant_capacity=0.005", "stone=0.08;lumber=0.08;clay=0.08;tools=0.03", "stone;lumber;clay;tools", "Roman insulae neighborhood with multistory brick apartments balconies street shops fountain and paved alley"),
    ("temple_precinct", "Urban Temple Precinct", "A scalable sanctuary precinct supporting ritual, civic identity, endowments, and public gathering.", "religious_category", "clergy", "religious_building_employment", "religious_building_time", "local_cultural_tradition=0.01;local_clergy_max_literacy=0.01", "stone=0.08;marble=0.04;incense=0.03;tools=0.03", "stone;marble;incense;tools", "Early imperial Roman urban temple precinct with podium temple altar portico votive reliefs incense and worshippers"),
    ("collegia_hall", "Collegia Hall", "A scalable meeting and dining hall for occupational, funerary, neighborhood, and cult associations.", "cultural_category", "burghers", "cultural_employment", "cultural_building_time", "local_cultural_tradition=0.008;local_unrest=-0.005", "stone=0.06;lumber=0.06;pottery=0.04;tools=0.02", "stone;lumber;pottery;tools", "Roman collegium meeting hall with dining couches patron altar occupation tools amphorae and membership tablets"),
    ("bronze_workers_collegium", "Bronze Workers' Collegium", "A scalable casting quarter for vessels, fittings, lamps, weights, bells, and civic metalwork.", "basic_industry_category", "burghers", "guild_employment", "guild_build_time", "local_production_efficiency=0.02", "copper=0.12;tin=0.03;coal=0.04;tools=0.03", "copper;tin;coal;tools", "Roman bronze workers collegium with charcoal furnaces clay molds crucibles vessels lamps weights and casting tools"),
    ("lead_pipeworks", "Lead Pipeworks", "A scalable casting and sheet-working yard supplying pipes, clamps, weights, and building fittings.", "basic_industry_category", "burghers", "guild_employment", "guild_build_time", "local_production_efficiency=0.02", "lead=0.14;coal=0.04;tools=0.03", "lead;coal;tools", "Roman lead pipeworks with cast fistula pipes sheet lead molds clamps weights charcoal hearth and tools"),
    ("unguentarium", "Unguentarium", "A scalable workshop blending aromatic oils, resins, pigments, and medicinal or ritual perfumes.", "consumer_goods_category", "burghers", "guild_employment", "guild_build_time", "local_merchant_power=0.01;local_production_efficiency=0.01", "incense=0.08;olives=0.06;pottery=0.05;tools=0.02", "incense;olives;pottery;tools", "Roman unguent workshop with glass perfume flasks bronze scales incense resin olive oil mortar and sealed jars"),
)

def read(path: Path, fields: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != fields:
            raise ValueError(f"{path.relative_to(ROOT)} header mismatch")
        return [{field: (row.get(field) or "").strip() for field in fields} for row in reader]


def render(fields: tuple[str, ...], rows: list[dict[str, str]]) -> str:
    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def outputs() -> dict[Path, str]:
    family_keys = {f"antq_reg_{row[0]}" for row in FAMILIES_TO_ADD}
    family_rows = [row for row in read(FAMILIES, FAMILY_FIELDS) if row["key"] not in family_keys]
    family_at = next(
        (index for index, row in enumerate(family_rows) if row["key"] == "antq_reg_herbal_apothecary"),
        len(family_rows),
    )
    additions: list[dict[str, str]] = []
    for slug, name, description, category, pop, employment, build_time, modifier, maintenance, goods, subject in FAMILIES_TO_ADD:
        additions.append(
            {
                "key": f"antq_reg_{slug}", "name": name, "description": description,
                "category": category, "pop_type": pop, "employment_size": employment,
                "build_time": build_time, "modifier": modifier, "maintenance": maintenance,
                "goods": goods, "source": SOURCE, "confidence": "secure", "note": NOTE,
                "icon_subject": subject,
            }
        )
    family_rows[family_at:family_at] = additions

    profiles = read(PROFILES, PROFILE_FIELDS)
    town_locations = {
        row["location"] for row in read(URBAN_NODES, URBAN_FIELDS) if row["profile"] == "town"
    }
    city_only_slugs = {
        "forum_basilica", "horrea_complex", "aqueduct_distribution",
        "thermae_complex", "insulae_quarter", "temple_precinct", "collegia_hall",
    }
    slugs = {row[0] for row in FAMILIES_TO_ADD}
    seed_rows = [row for row in read(SEEDS, SEED_FIELDS) if not row["key"].startswith("reg_roman_economy_")]
    seed_at = next(
        (index for index, row in enumerate(seed_rows) if row["key"].startswith("reg_twelfth_")),
        len(seed_rows),
    )
    seed_additions: list[dict[str, str]] = []
    for profile in profiles:
        locations = [value for value in profile["locations"].split(";") if value]
        selected = slugs if profile["families"] == "all" else set(profile["families"].split(";"))
        unknown = selected - slugs
        if unknown:
            raise ValueError(f"profile {profile['profile']} uses unknown family slugs {sorted(unknown)}")
        for location in locations:
            macro = "North Africa" if location in {"alexandria", "tunis", "sousse", "bizerte", "annaba", "gabes"} else (
                "Middle East" if location in {"antioch", "ayasuluk"} else "Europe"
            )
            for slug in sorted(selected):
                if location in town_locations and slug in city_only_slugs:
                    continue
                seed_additions.append(
                    {
                        "key": f"reg_roman_economy_{profile['profile']}_{location}_{slug}",
                        "family": f"antq_reg_{slug}", "location": location, "macro": macro,
                        "source": profile["source"], "confidence": profile["confidence"],
                        "note": profile["note"],
                    }
                )
    seed_rows[seed_at:seed_at] = seed_additions

    # s2_global_settlements.py owns all opening placement, including these
    # Roman families. Keeping one placement owner prevents capital clustering.
    return {FAMILIES: render(FAMILY_FIELDS, family_rows)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        expected = outputs()
    except (OSError, ValueError, csv.Error) as exc:
        print(f"m5_roman_economy: FAIL\n  - {exc}")
        return 1
    if args.write:
        for path, content in expected.items():
            path.write_text(content, encoding="utf-8-sig", newline="")
        print(
            f"m5_roman_economy: wrote {len(FAMILIES_TO_ADD)} families; "
            "global placement delegated"
        )
        return 0
    stale = [
        path.relative_to(ROOT)
        for path, content in expected.items()
        if not path.is_file() or path.read_text(encoding="utf-8-sig") != content
    ]
    if stale:
        print(f"m5_roman_economy: FAIL\n  - stale or missing {stale}")
        return 1
    print(f"m5_roman_economy: PASS ({len(FAMILIES_TO_ADD)} Roman families)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
