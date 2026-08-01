#!/usr/bin/env python3
"""Render checked antiquity-specific raw and processed goods contracts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "docs/m5/custom_goods.csv"
OUTPUT = ROOT / "in_game/common/goods/00_antiquitas_raw_goods.txt"
POP_DEMAND_SOURCE_RELATIVE = Path("game/in_game/common/goods_demand/pop_demands.txt")
POP_DEMAND_OUTPUT = ROOT / "in_game/common/goods_demand/pop_demands.txt"
GOODS_LOCALIZATION_SOURCE_RELATIVE = Path("game/main_menu/localization")
ASSET_SOURCE = ROOT / "assets_queue/generated"
ICON_DIR = ROOT / "main_menu/gfx/interface/icons/trade_goods"
ILLUSTRATION_DIR = ICON_DIR / "illustrations"
MODIFIER_TYPES = ROOT / "main_menu/common/modifier_type_definitions/00_antiquitas_goods.txt"
MODIFIER_ICONS = ROOT / "main_menu/common/modifier_icons/00_antiquitas_goods.txt"
LOCALIZATION_DIR = ROOT / "main_menu/localization"
LANGUAGES = (
    "english",
    "french",
    "german",
    "spanish",
    "polish",
    "russian",
    "braz_por",
    "simp_chinese",
    "japanese",
    "korean",
    "turkish",
)
FIELDS = (
    "key",
    "name",
    "description",
    "category",
    "method",
    "color_r",
    "color_g",
    "color_b",
    "price",
    "transport_cost",
    "food",
    "all",
    "nobles",
    "burghers",
    "clergy",
    "source",
    "confidence",
    "note",
)
KEY_RE = re.compile(r"^antq_[a-z0-9_]+$")
METHODS = {"farming", "gathering", "mining", "hunting", "forestry"}
GOODS_CATEGORIES = {"raw_material", "produced"}
POP_DEMAND_INSERTION = re.compile(r"^(?P<indent>[ \t]*)mercury\s*=\s*1(?P<ending>\r?\n)$", re.MULTILINE)
COAL_NAME = re.compile(r'^(?P<indent>[ \t]*)coal:\s*".*"$', re.MULTILINE)
COAL_DESCRIPTION = re.compile(r'^(?P<indent>[ \t]*)coal_desc:\s*".*"$', re.MULTILINE)
ANCIENT_LOCALIZATION_REPLACEMENTS = {
    "horses_desc": (
        "Horses provide remounts, traction, prestige, courier service, and the "
        "mounted arm of armies from Atlantic Europe to the Eurasian steppe."
    ),
    "tar_desc": (
        "Wood tar and natural bitumen seal hulls, roofs, ropes, baskets, and "
        "containers, making them essential to shipyards and waterproof construction."
    ),
    "copper_desc": (
        "Copper is worked alone and with tin as bronze for tools, vessels, "
        "coinage, fittings, armor, and weapons across the ancient world."
    ),
    "lead_desc": (
        "Lead is obtained from galena, often alongside silver, and used for "
        "pipes, weights, anchors, roofing, vessels, pigments, and other ancient crafts."
    ),
    "goods_gold_desc": (
        "Gold is worked into coin, plate, jewellery, cult offerings, and royal "
        "gifts; its durability and scarcity make it a portable store of prestige and wealth."
    ),
    "silver_desc": (
        "Silver supports coinage, tribute, plate, jewellery, and temple wealth, "
        "linking mines and mints to armies, courts, cities, and long-distance trade."
    ),
    "gems_desc": (
        "Rubies, sapphires, diamonds, emeralds, garnets, and jade adorn regalia, "
        "jewellery, seals, cult objects, and elite gifts across ancient exchange networks."
    ),
    "stone_desc": (
        "Quarried stone supplies walls, roads, bridges, temples, monuments, mills, "
        "drains, and durable civic construction."
    ),
    "tin_desc": (
        "Tin is prized above all as the alloying metal for bronze, and also serves "
        "in pewter, coatings, vessels, fittings, and specialist metalwork."
    ),
    "silk_desc": (
        "Silk is reeled and woven in East Asia, then exchanged as cloth, thread, "
        "gifts, and tribute through Central Asian, Indian, and maritime routes."
    ),
    "dyes_desc": (
        "Indigo, madder, woad, saffron, murex, and other dyestuffs colour cloth, "
        "leather, paint, and ritual materials; vivid and fast colours command high prices."
    ),
    "sugar_desc": (
        "Cane sugar is a scarce South Asian sweetener and medicinal preparation, "
        "traded in limited quantities alongside honey, fruits, and syrups."
    ),
    "tobacco_desc": (
        "Tobacco represents locally cultivated American Nicotiana plants used "
        "within Indigenous ritual, medicinal, and social traditions; it has no Old World trade route."
    ),
    "tea_desc": (
        "Tea represents the bounded use of tea leaves and related infusions in "
        "southern and western Han contexts."
    ),
    "cocoa_desc": (
        "Cacao represents locally cultivated American Theobroma used in drinks, "
        "foodways, exchange, and ritual contexts within its native range."
    ),
    "coffee": "Unavailable Legacy Crop",
    "coffee_desc": (
        "This compatibility entry has no AD 1 production or demand in ANTIQVITAS."
    ),
    "naval_supplies_desc": (
        "Naval supplies combine timber, tar, rope, sailcloth, cordage, fittings, "
        "and other materials needed to build and maintain ancient ships."
    ),
    "ivory_desc": (
        "Elephant and hippopotamus ivory is carved into inlays, handles, furniture, "
        "statuettes, writing tablets, ornaments, and prestigious gifts."
    ),
    "fur_desc": (
        "Furs and dressed pelts provide warm clothing, bedding, trim, tribute, and "
        "exchange goods from northern forests, mountains, and steppe margins."
    ),
    "lumber_desc": (
        "Cut timber supplies houses, halls, ships, carts, bridges, scaffolds, mines, "
        "fortifications, fuel, and countless household implements."
    ),
    "salt_desc": (
        "Mined, boiled, or solar-evaporated salt preserves food, supports livestock, "
        "seasons diets, and moves in bulk along roads, rivers, and coasts."
    ),
    "porcelain": "High-Fired Ceramics",
    "porcelain_desc": (
        "High-fired, fine-bodied ceramics represent the developing glazed and "
        "vitrified wares of ancient East Asian kilns."
    ),
    "firearms": "Unavailable Legacy Armament",
    "firearms_desc": (
        "This compatibility entry has no production, demand, or unlock in ANTIQVITAS."
    ),
    "cannons": "Unavailable Legacy Artillery",
    "cannons_desc": (
        "This compatibility entry has no production, demand, or unlock in ANTIQVITAS."
    ),
    "wheat_desc": (
        "Wheat represents staple cereals feeding people and animals; failed "
        "harvests threaten urban supply, prices, and public order."
    ),
    "steel_desc": (
        "Steel represents deliberately carburized, quenched, and refined iron "
        "used for edged tools, armor fittings, springs, and high-quality weapons in ancient workshops."
    ),
    "glass_desc": (
        "Glassworkers shape vessels, beads, inlays, windows, mirrors, and ornaments "
        "from silica, fluxes, colourants, and recycled cullet."
    ),
    "cloth_desc": (
        "Cloth comprises woven wool, linen, cotton, hemp, and other fibres used for "
        "clothing, blankets, sails, tents, wrappings, and household textiles."
    ),
    "wine_desc": (
        "Wine is a staple drink, ration, offering, medicine, and trade good produced "
        "in vineyards and stored or shipped in jars, skins, and barrels."
    ),
    "liquor": "Infused Wine",
    "liquor_desc": (
        "Infused wines combine fermented grape or grain drinks with herbs, resins, "
        "honey, fruits, and spices for household, medicinal, and ceremonial use."
    ),
    "paper": "Writing Materials",
    "paper_desc": (
        "Prepared papyrus, bark sheets, early fibre paper, parchment, bamboo slips, "
        "wooden tablets, and other writing materials sustain records and correspondence."
    ),
    "books": "Scrolls and Codices",
    "books_desc": (
        "Scrolls, stitched manuscripts, tablets, and early codices preserve law, "
        "accounts, literature, ritual, scholarship, and official correspondence."
    ),
    "leather_desc": (
        "Tanned hides supply footwear, belts, harness, shields, armour fittings, "
        "containers, parchment, tents, upholstery, and durable clothing."
    ),
    "potato_desc": (
        "Potatoes represent Andean tubers cultivated around the Lake Titicaca "
        "basin and neighboring highlands within their native American range."
    ),
    "fish_desc": (
        "Fresh, dried, salted, smoked, and fermented fish feed inland and coastal "
        "communities while fisheries supply sailors, merchants, and military stores."
    ),
    "maize_desc": (
        "Maize is a major Indigenous American cereal cultivated in fields and gardens, "
        "eaten fresh or dried, ground into meal, stored, and exchanged within its native range."
    ),
    "legumes_desc": (
        "Beans, peas, lentils, chickpeas, and other pulses provide storable protein, "
        "restore soils, and complement cereal diets across many farming systems."
    ),
    "amber_desc": (
        "Fossil resin from Baltic and other deposits is gathered and worked into "
        "beads, amulets, inlays, ornaments, and valuable long-distance exchange goods."
    ),
    "alum_desc": (
        "Alum serves as a mordant for dyes and as an ingredient in tanning, medicine, "
        "pigments, and specialist crafts; desert and volcanic sources support wide trade."
    ),
    "slaves_goods_desc": (
        "Enslaved people are moved between markets to fill vacant @slaves! "
        "[ShowPopTypeName('slaves')] work through warfare, raiding, punishment, debt, and trade."
    ),
    "beer_desc": (
        "Beer brewed from barley, wheat, millet, sorghum, rice, or other grains is a "
        "staple drink, ration, offering, and source of calories in many ancient societies."
    ),
    "fruit_desc": (
        "Dates, figs, grapes, apples, pears, citrus, melons, and other fruits supply "
        "fresh, dried, pressed, fermented, and preserved foods suited to local climates."
    ),
    "mercury_desc": (
        "Mercury and cinnabar are used cautiously in pigments, gilding, ritual objects, "
        "medicine, and specialist metallurgical experiments."
    ),
    "cloves_desc": (
        "Cloves are aromatic flower buds from the Maluku Islands, valued in food, "
        "medicine, fragrance, court ritual, and long-distance maritime exchange."
    ),
    "saltpeter_desc": (
        "Saltpeter is a naturally occurring mineral used in limited ancient "
        "medicinal, preservation, and workshop contexts; it has no military economy here."
    ),
    "fine_cloth_desc": (
        "Fine cloth represents high-value ancient textiles, including carefully "
        "finished wool, linen, cotton, muslin, damask, and silk."
    ),
    "elephants_desc": (
        "Elephants serve as prestigious animals, sources of labor, and war beasts "
        "in parts of India, Southeast Asia, the Iranian world, and North Africa."
    ),
    "marble_desc": (
        "Marble is a prestigious building and sculptural stone quarried, traded, "
        "and worked throughout the ancient Mediterranean and neighboring regions."
    ),
    "colonial_charter_maintenance": "Inactive Overseas Charter Maintenance",
    "colonial_administration_requirements": "Inactive Overseas Administrations",
    "modern_council_hall_maintenance": "Inactive Council Halls",
    "cotton_desc": (
        "Cotton represents ancient South Asian and African fibre crops spun, "
        "woven, and exchanged through regional and maritime networks."
    ),
    "rifle_infantry_maintenance": "Inactive Legacy Missile-Troop Upkeep",
    "rifle_infantry_construction": "Inactive Legacy Missile-Troop Equipment",
    "build_railroad_demand": "Inactive Legacy Road Construction",
    "maintain_railroad_demand": "Inactive Legacy Road Maintenance",
    "demands_of_muskets": "Inactive Legacy Weapon Demand",
    "manufactory_input": "Workshop Input",
    "naval_supplies_manufactory_maintenance": "Naval-Supply Workshops",
    "printing_manufactory_maintenance": "Document Workshops",
    "paper_manufactory_maintenance": "Paper Workshops",
    "firearms_guild_steel_maintenance": "Inactive Legacy Armament Shops",
    "cannon_foundry_maintenance": "Inactive Legacy Siege Works",
    "firearms_manufactory_maintenance": "Inactive Legacy Armament Workshops",
    "pottery_manufactory_maintenance": "Pottery Workshops",
    "furniture_manufactory_maintenance": "Furniture Workshops",
    "manufactory_construction": "Workshop Construction",
    "porcelain_manufactory_maintenance": "Porcelain Workshops",
    "tannery_manufactory_maintenance": "Tanning Workshops",
    "gun_factory_maintenance": "Inactive Legacy Armament Works",
    "weapon_manufactory_maintenance": "Weapon Workshops",
    "lutheran_preacher_maintenance": "Inactive Legacy Preachers",
    "lacquerware_manufactory_maintenance": "Lacquerware Workshops",
    "guns_foundry_maintenance": "Inactive Legacy Siege Works",
    "brewery_manufactory_maintenance": "Brewing Workshops",
    "leather_manufactory_maintenance": "Leather Workshops",
    "hand_cannon_guild_maintenance": "Inactive Legacy Siege-Artisan Shops",
    "fine_cloth_manufactory_maintenance": "Fine-Cloth Workshops",
    "silk_cloth_manufactory_maintenance": "Silk Workshops",
    "firearms_factory_maintenance": "Inactive Legacy Armament Works",
    "jesuit_college_maintenance": "Inactive Legacy Religious College",
    "janissary_barracks_maintenance": "Inactive Legacy Barracks",
    "ghilman_barracks_maintenance": "Inactive Legacy Barracks",
    "safaviyya_order_hall_maintenance": "Inactive Legacy Order Hall",
    "scottish_whisky_distillery_maintenance": "Inactive Legacy Distillery",
    "scottish_whisky_distillery_mill_maintenance": "Inactive Legacy Distillery Mills",
    "novodevichy_building_construction": "Inactive Legacy Religious Construction",
    "dutch_trade_outpost_maintenance": "Inactive Legacy Overseas Outpost",
    "local_newspaper_needs": "Inactive Legacy Printed News",
    "POP_DEMAND_PRINTING_PRESS": "Inactive Legacy Printing",
    "POP_DEMAND_ANGLICAN_VESTMENTS": "Inactive Legacy Clerical Vestments",
    "gun_smith_slot_0": "Inactive Legacy Armament Method",
    "guns_guild_lumber_maintenance": "Inactive Legacy Armament Material",
    "guns_guild_bronze_maintenance": "Inactive Legacy Armament Material",
    "guns_guild_iron_maintenance": "Inactive Legacy Armament Material",
    "guns_guild_steel_maintenance": "Inactive Legacy Armament Material",
    "gun_smith_slot_1": "Inactive Legacy Projectile Method",
    "guns_guild_ammunition_stone_maintenance": "Inactive Legacy Projectiles",
    "guns_guild_ammunition_lead_maintenance": "Inactive Legacy Projectiles",
    "guns_guild_ammunition_iron_maintenance": "Inactive Legacy Projectiles",
    "hab_reformed_monastery_maintenance_desc": (
        "An inactive compatibility method retained only for engine references."
    ),
    "guns_guild_lumber_maintenance_desc": (
        "An inactive compatibility method retained only for engine references."
    ),
    "jesuit_college_maintenance_desc": (
        "An inactive compatibility method retained only for engine references."
    ),
    "janissary_barracks_maintenance_desc": (
        "An inactive compatibility method retained only for engine references."
    ),
    "ghilman_barracks_maintenance_desc": (
        "An inactive compatibility method retained only for engine references."
    ),
    "safaviyya_order_hall_maintenance_desc": (
        "An inactive compatibility method retained only for engine references."
    ),
    "scottish_whisky_distillery_maintenance_desc": (
        "An inactive compatibility method retained only for engine references."
    ),
    "guns_guild_ammunition_stone_maintenance_desc": (
        "An inactive compatibility method retained only for engine references."
    ),
}
LOCALIZATION_LINE = re.compile(
    r'^(?P<indent>[ \t]*)(?P<key>[A-Za-z0-9_]+):\s*".*"\s*$',
    re.MULTILINE,
)


def rows() -> list[dict[str, str]]:
    with INPUT.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("custom_goods.csv header does not match required field order")
        return list(reader)


def number(value: str, field: str, key: str, minimum: float = 0.0) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ValueError(f"custom_goods.csv {key} has invalid {field} {value}") from exc
    if parsed < minimum:
        raise ValueError(f"custom_goods.csv {key} has {field} below {minimum}")
    return parsed


def render_goods(entries: list[dict[str, str]]) -> str:
    lines = [
        "# Generated by tools/generate_ancient_goods.py --write.",
        "# M5 antiquity-specific goods; sources and rationale: docs/m5/custom_goods.csv.",
    ]
    for row in sorted(entries, key=lambda item: item["key"]):
        lines.append(f"{row['key']} = {{")
        if row["category"] == "raw_material":
            lines.append(f"\tmethod = {row['method']}")
        lines.extend(
            (
                f"\tcategory = {row['category']}",
                f"\tcolor = rgb {{ {row['color_r']} {row['color_g']} {row['color_b']} }}",
                f"\tdefault_market_price = {row['price']}",
                f"\ttransport_cost = {row['transport_cost']}",
            )
        )
        if float(row["food"]):
            lines.append(f"\tfood = {row['food']}")
        lines.extend(("", "\tdemand_add = {"))
        for pop in ("all", "nobles", "burghers", "clergy"):
            if float(row[pop]):
                lines.append(f"\t\t{pop} = {row[pop]}")
        lines.extend(
            (
                "\t}",
                "",
                "\torigin_in_old_world = yes",
                "\tcustom_tags = { old_world_goods antq_ancient_economy }",
                "\tno_demand_if_no_market_availability = yes",
                "}",
                "",
            )
        )
    return "\n".join(lines)


def pop_demand_source() -> Path:
    try:
        config = json.loads((ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig"))
        source = Path(str(config["game_dir"])) / POP_DEMAND_SOURCE_RELATIVE
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot resolve installed pop-demand registry: {exc}") from exc
    if not source.is_file():
        raise ValueError(f"installed pop-demand registry is missing: {source}")
    return source


def render_pop_demands(entries: list[dict[str, str]]) -> bytes:
    """Copy the engine's special demand registry and add every ANTIQVITAS good.

    ``pop_demand`` is not an additive generic script object: engine setup warns
    when a good's pop demand is absent from this one registry.  An exact-name
    source-pinned overlay keeps every installed demand key while extending the
    raw-material section with the generated custom-good inventory.
    """
    source = pop_demand_source()
    raw = source.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    content = raw.decode("utf-8-sig")
    matches = list(POP_DEMAND_INSERTION.finditer(content))
    if len(matches) != 1:
        raise ValueError(
            "installed pop-demand registry drift: expected exactly one mercury raw-material anchor, "
            f"found {len(matches)}"
        )
    match = matches[0]
    ending = match.group("ending")
    indent = match.group("indent")
    injected = [
        f"{indent}# ANTIQVITAS custom antiquity goods; generated from docs/m5/custom_goods.csv.{ending}",
    ]
    injected.extend(f"{indent}{row['key']} = 1{ending}" for row in sorted(entries, key=lambda item: item["key"]))
    rendered = content[: match.end()] + "".join(injected) + content[match.end() :]
    payload = rendered.encode("utf-8")
    return (b"\xef\xbb\xbf" if has_bom else b"") + payload


def render_goods_localization_override(language: str) -> str:
    """Preserve parser keys while ancientizing active and legacy goods text."""
    config = json.loads((ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig"))
    source = (
        Path(str(config["game_dir"]))
        / GOODS_LOCALIZATION_SOURCE_RELATIVE
        / "english"
        / "goods_l_english.yml"
    )
    if not source.is_file():
        raise ValueError(f"installed goods localization is missing: {source}")
    content = source.read_text(encoding="utf-8-sig")
    content, header_count = re.subn(r"^l_english:", f"l_{language}:", content, count=1)
    if header_count != 1:
        raise ValueError("installed English goods localization has no canonical language header")
    content, name_count = COAL_NAME.subn(
        r'\g<indent>coal: "Charcoal"',
        content,
    )
    content, description_count = COAL_DESCRIPTION.subn(
        r'\g<indent>coal_desc: "Wood charcoal fuels household hearths, kilns, bloomeries, and metalworking furnaces throughout the ancient world."',
        content,
    )
    if (name_count, description_count) != (1, 1):
        raise ValueError(
            f"installed English goods localization drift: expected one coal name and description, "
            f"found {name_count} and {description_count}"
        )
    counts = {key: 0 for key in ANCIENT_LOCALIZATION_REPLACEMENTS}

    def replace_line(match: re.Match[str]) -> str:
        key = match.group("key")
        replacement = ANCIENT_LOCALIZATION_REPLACEMENTS.get(key)
        if replacement is None:
            return match.group(0)
        counts[key] += 1
        escaped = replacement.replace("\\", "\\\\").replace('"', '\\"')
        return f'{match.group("indent")}{key}: "{escaped}"'

    content = LOCALIZATION_LINE.sub(replace_line, content)
    drift = {key: count for key, count in counts.items() if count != 1}
    if drift:
        raise ValueError(
            "installed English goods localization drift for ancient text replacements: "
            f"{drift}"
        )
    return "\n".join(line.rstrip(" \t") for line in content.splitlines()).rstrip("\n") + "\n"


def modifier_names(row: dict[str, str]) -> tuple[tuple[str, str], ...]:
    key = row["key"]
    name = row["name"]
    return (
        (f"can_extract_{key}", f"Can Extract {name}"),
        (f"ban_exports_of_{key}", f"Ban Exports of {name}"),
        (f"ban_imports_of_{key}", f"Ban Imports of {name}"),
        (f"local_{key}_output_modifier", f"Local {name} Output"),
        (f"global_{key}_output_modifier", f"Global {name} Output"),
        (f"global_{key}_pop_demand", f"{name} Pop Demand"),
        (f"{key}_impacts_inflation", f"{name} Impacts Inflation"),
        (f"{key}_used_for_minting", f"{name} Used for Minting"),
    )


def render_localization(entries: list[dict[str, str]], language: str) -> str:
    lines = [f"l_{language}:"]
    for row in sorted(entries, key=lambda item: item["key"]):
        lines.append(f' {row["key"]}: "{row["name"]}"')
        lines.append(f' {row["key"]}_desc: "{row["description"]}"')
        for key, name in modifier_names(row):
            lines.append(f' MODIFIER_TYPE_NAME_{key}: "{name}"')
            lines.append(f' MODIFIER_TYPE_DESC_{key}: "{name}."')
    return "\n".join(lines) + "\n"


def render_modifier_types(entries: list[dict[str, str]]) -> str:
    contracts = (
        ("can_extract_{key}", "boolean", "country"),
        ("ban_exports_of_{key}", "boolean", "country"),
        ("ban_imports_of_{key}", "boolean", "country"),
        ("local_{key}_output_modifier", "percent", "location"),
        ("global_{key}_output_modifier", "percent", "country"),
        ("global_{key}_pop_demand", "percent", "country"),
        ("{key}_impacts_inflation", "percent", "country"),
        ("{key}_used_for_minting", "boolean", "country"),
    )
    lines = [
        "# Generated by tools/generate_ancient_goods.py --write.",
        "# Required modifier contracts synthesized by the EU5 goods parser.",
    ]
    for row in sorted(entries, key=lambda item: item["key"]):
        for template, value_type, scope in contracts:
            key = template.format(key=row["key"])
            lines.extend(
                (
                    f"{key}={{",
                    f"\t{value_type}=yes",
                    "\tgame_data={",
                    f"\t\tcategory={scope}",
                    "\t}",
                    "}",
                    "",
                )
            )
    return "\n".join(lines)


def render_modifier_icons(entries: list[dict[str, str]]) -> str:
    lines = [
        "# Generated by tools/generate_ancient_goods.py --write.",
        "# The vanilla default modifier texture is an intentional neutral fallback.",
    ]
    for row in sorted(entries, key=lambda item: item["key"]):
        for key, _name in modifier_names(row):
            lines.extend(
                (
                    f"{key} = {{",
                    '\tpositive = "gfx/interface/icons/modifier_types/_default.dds"',
                    "}",
                    "",
                )
            )
    return "\n".join(lines)


def dds_identify(path: Path) -> tuple[str, str, str, str]:
    magick = ROOT / ".tools/ImageMagick/magick.exe"
    executable = str(magick) if magick.is_file() else "magick"
    result = subprocess.run(
        [executable, "identify", "-format", "%m|%w|%h|%[channels]", str(path)],
        check=True,
        text=True,
        capture_output=True,
    )
    return tuple(result.stdout.split("|", 3))  # type: ignore[return-value]


def verify_dds(
    path: Path,
    expected_width: str,
    expected_height: str,
    minimum_size: int,
    failures: list[str],
) -> None:
    try:
        fmt, width, height, channels = dds_identify(path)
        if (fmt, width, height, channels) != ("DDS", expected_width, expected_height, "srgba 4.0"):
            failures.append(
                f"{path.relative_to(ROOT)} must be {expected_width}x{expected_height} DDS sRGBA, got "
                f"{fmt} {width}x{height} {channels}"
            )
        elif path.stat().st_size < minimum_size:
            failures.append(f"{path.relative_to(ROOT)} has no complete mip chain")
    except (OSError, subprocess.CalledProcessError) as exc:
        failures.append(f"{path.relative_to(ROOT)} cannot be identified: {exc}")


def validate(entries: list[dict[str, str]]) -> None:
    failures: list[str] = []
    seen: set[str] = set()
    colors: set[tuple[int, int, int]] = set()
    for row in entries:
        key = row.get("key", "").strip()
        required = tuple(field for field in FIELDS if field != "method")
        if any(not row.get(field, "").strip() for field in required):
            failures.append("custom_goods.csv contains a blank required field")
            continue
        if key in seen:
            failures.append(f"custom_goods.csv repeats key {key}")
        if not KEY_RE.fullmatch(key):
            failures.append(f"custom_goods.csv key {key} must be namespaced antq_ ASCII")
        if row["category"] not in GOODS_CATEGORIES:
            failures.append(f"custom_goods.csv {key} has invalid category {row['category']}")
        if row["category"] == "raw_material" and row["method"] not in METHODS:
            failures.append(f"custom_goods.csv {key} has invalid raw-material method {row['method']}")
        if row["category"] == "produced" and row["method"]:
            failures.append(f"custom_goods.csv {key} produced goods must not declare an RGO method")
        try:
            color = tuple(int(row[field]) for field in ("color_r", "color_g", "color_b"))
            if any(value < 0 or value > 255 for value in color):
                raise ValueError
            if color in colors:
                failures.append(f"custom_goods.csv repeats RGB color {color}")
            colors.add(color)
        except ValueError:
            failures.append(f"custom_goods.csv {key} has an invalid RGB color")
        if row["confidence"] not in {"secure", "contested"}:
            failures.append(f"custom_goods.csv {key} has invalid confidence {row['confidence']}")
        for field in ("price", "transport_cost", "food", "all", "nobles", "burghers", "clergy"):
            try:
                number(row[field], field, key)
            except ValueError as exc:
                failures.append(str(exc))
        png = ASSET_SOURCE / f"{key}.png"
        icon = ICON_DIR / f"icon_goods_{key}.dds"
        illustration = ILLUSTRATION_DIR / f"icon_goods_{key}.dds"
        if not png.is_file():
            failures.append(f"custom_goods.csv {key} is missing source art {png.relative_to(ROOT)}")
        else:
            try:
                with Image.open(png) as image:
                    if image.mode != "RGBA":
                        failures.append(f"{png.relative_to(ROOT)} must have an alpha channel")
                    elif image.getpixel((0, 0))[3] != 0:
                        failures.append(f"{png.relative_to(ROOT)} must have a transparent corner")
                    else:
                        alpha = image.getchannel("A")
                        histogram = alpha.histogram()
                        mean_alpha = sum(value * count for value, count in enumerate(histogram)) / (
                            255 * image.width * image.height
                        )
                        if mean_alpha >= 0.67:
                            failures.append(
                                f"{png.relative_to(ROOT)} has geometric backplate occupancy "
                                f"({mean_alpha:.3f}); custom trade goods must be direct object cutouts"
                            )
            except OSError as exc:
                failures.append(f"{png.relative_to(ROOT)} is unreadable: {exc}")
        if not icon.is_file():
            failures.append(f"custom_goods.csv {key} is missing icon {icon.relative_to(ROOT)}")
        else:
            verify_dds(icon, "128", "128", 21900, failures)
        if not illustration.is_file():
            failures.append(f"custom_goods.csv {key} is missing illustration {illustration.relative_to(ROOT)}")
        else:
            verify_dds(illustration, "1080", "440", 630_000, failures)
        seen.add(key)
    if failures:
        raise ValueError("\n".join(sorted(set(failures))))


def expected_files(entries: list[dict[str, str]]) -> dict[Path, tuple[str, str]]:
    values: dict[Path, tuple[str, str]] = {
        OUTPUT: (render_goods(entries), "utf-8-sig"),
        MODIFIER_TYPES: (render_modifier_types(entries), "utf-8-sig"),
        MODIFIER_ICONS: (render_modifier_icons(entries), "utf-8-sig"),
    }
    for language in LANGUAGES:
        path = LOCALIZATION_DIR / language / f"antq_m5_goods_l_{language}.yml"
        values[path] = (render_localization(entries, language), "utf-8-sig")
        exact_path = LOCALIZATION_DIR / language / f"goods_l_{language}.yml"
        values[exact_path] = (render_goods_localization_override(language), "utf-8-sig")
    return values


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        entries = rows()
        if not entries:
            raise ValueError("custom_goods.csv has no entries")
        validate(entries)
        outputs = expected_files(entries)
        pop_demands = render_pop_demands(entries)
    except (OSError, ValueError, csv.Error, subprocess.CalledProcessError) as exc:
        print(f"ancient_goods: FAIL\n  - {exc}")
        return 1
    if args.write:
        for path, (content, encoding) in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding=encoding, newline="\n")
            print(f"ancient_goods: wrote {path.relative_to(ROOT)}")
        POP_DEMAND_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        POP_DEMAND_OUTPUT.write_bytes(pop_demands)
        print(f"ancient_goods: wrote {POP_DEMAND_OUTPUT.relative_to(ROOT)}")
        return 0
    stale = [
        path.relative_to(ROOT).as_posix()
        for path, (content, encoding) in outputs.items()
        if not path.is_file() or path.read_text(encoding=encoding) != content
    ]
    if not POP_DEMAND_OUTPUT.is_file() or POP_DEMAND_OUTPUT.read_bytes() != pop_demands:
        stale.append(POP_DEMAND_OUTPUT.relative_to(ROOT).as_posix())
    if stale:
        print("ancient_goods: FAIL\n  - stale or missing " + "\n  - ".join(stale))
        return 1
    raw_count = sum(row["category"] == "raw_material" for row in entries)
    print(
        "ancient_goods: PASS "
        f"({len(entries)} custom antiquity goods: {raw_count} raw / {len(entries) - raw_count} processed; "
        f"{len(LANGUAGES)} language mirrors)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
