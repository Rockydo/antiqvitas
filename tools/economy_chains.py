"""Shared construction and institutional-upkeep contracts for S2 economy chains."""

from __future__ import annotations

from decimal import Decimal
from typing import Iterable


CULTIVATOR_CONSTRUCTION_PACKAGE = "antq_small_cultivator_construction"
TRIBAL_CONSTRUCTION_PACKAGES = {
    "subsistence": "antq_small_tribal_subsistence_construction",
    "pastoral": "antq_small_tribal_pastoral_construction",
    "craft": "antq_small_tribal_craft_construction",
    "exchange": "antq_small_tribal_exchange_construction",
    "ritual": "antq_small_tribal_ritual_construction",
    "warrior": "antq_small_tribal_warrior_construction",
}

# The engine exposes a transient AD 1 balance before its first estate,
# population, and market settlement.  AI capital decisions must use the real
# settled budget instead.  This shared contract deliberately leaves player
# construction visible and enabled from day one.
AI_CAPITAL_SETTLEMENT_DATE = "3.1.1"
AI_CAPITAL_RESERVE_MONTHS = 24
AI_CAPITAL_SURPLUS_DIVISOR = 2


def ai_capital_affordability_trigger(indent: str = "\t\t") -> list[str]:
    """Render the scalable country trigger for ordinary custom construction."""
    return [
        f"{indent}OR = {{",
        f"{indent}\tis_ai = no",
        f"{indent}\tAND = {{",
        f"{indent}\t\tcurrent_date >= {AI_CAPITAL_SETTLEMENT_DATE}",
        f"{indent}\t\tnum_loans = 0",
        f"{indent}\t\tgold >= {{ value = monthly_income_total multiply = {AI_CAPITAL_RESERVE_MONTHS} }}",
        f"{indent}\t\tmonthly_balance > {{ value = monthly_income_total divide = {AI_CAPITAL_SURPLUS_DIVISOR} }}",
        f"{indent}\t}}",
        f"{indent}}}",
    ]


PACKAGE_GOODS: dict[str, tuple[tuple[str, str], ...]] = {
    # Cultivator levels and tribal branches are household/community works, not
    # state farms, guildhalls, horse breeders, prestige monuments, or forts.
    # Their former vanilla baskets were 4-100+ times their physical scale and
    # could consume an entire minor polity treasury in one AI capital cycle.
    CULTIVATOR_CONSTRUCTION_PACKAGE: (
        ("lumber", "0.05"),
        ("tools", "0.01"),
    ),
    TRIBAL_CONSTRUCTION_PACKAGES["subsistence"]: (
        ("lumber", "0.05"),
        ("tools", "0.01"),
    ),
    TRIBAL_CONSTRUCTION_PACKAGES["pastoral"]: (
        ("lumber", "0.06"),
        ("livestock", "0.03"),
        ("leather", "0.01"),
    ),
    TRIBAL_CONSTRUCTION_PACKAGES["craft"]: (
        ("lumber", "0.08"),
        ("tools", "0.02"),
        ("clay", "0.03"),
    ),
    TRIBAL_CONSTRUCTION_PACKAGES["exchange"]: (
        ("lumber", "0.04"),
        ("pottery", "0.02"),
    ),
    TRIBAL_CONSTRUCTION_PACKAGES["ritual"]: (
        ("lumber", "0.08"),
        ("cloth", "0.02"),
        ("pottery", "0.02"),
    ),
    TRIBAL_CONSTRUCTION_PACKAGES["warrior"]: (
        ("lumber", "0.15"),
        ("weaponry", "0.02"),
        ("leather", "0.03"),
    ),
    # Bootstrap industries cannot consume their own downstream products.
    # Ropewalks and wood-tar kilns use a raw-material basket so a market with
    # neither tar nor cordage can establish the chain from first principles.
    "antq_s2_enabling_industry_construction": (
        ("lumber", "0.25"),
        ("clay", "0.15"),
        ("stone", "0.10"),
    ),
    "antq_s2_workshop_construction": (
        ("masonry", "0.30"),
        ("lumber", "0.10"),
        ("tools", "0.05"),
        ("antq_cordage", "0.020"),
    ),
    "antq_s2_market_construction": (
        ("masonry", "0.30"),
        ("lumber", "0.15"),
        ("cloth", "0.05"),
        ("pottery", "0.04"),
    ),
    "antq_s2_port_construction": (
        ("lumber", "0.40"),
        ("masonry", "0.10"),
        ("tar", "0.06"),
        ("antq_cordage", "0.060"),
    ),
    "antq_s2_fortification_construction": (
        ("masonry", "0.30"),
        ("stone", "0.25"),
        ("lumber", "0.20"),
        ("weaponry", "0.05"),
    ),
    "antq_s2_waterworks_construction": (
        ("masonry", "0.35"),
        ("stone", "0.20"),
        ("lumber", "0.10"),
        ("tools", "0.05"),
    ),
    "antq_s2_civic_construction": (
        ("masonry", "0.35"),
        ("stone", "0.15"),
        ("lumber", "0.10"),
        ("cloth", "0.04"),
    ),
    "antq_s2_archive_construction": (
        ("masonry", "0.25"),
        ("lumber", "0.15"),
        ("cloth", "0.04"),
        ("leather", "0.03"),
    ),
    "antq_s2_sanctuary_construction": (
        ("masonry", "0.30"),
        ("stone", "0.15"),
        ("lumber", "0.10"),
        ("pottery", "0.04"),
    ),
    "antq_s2_rural_construction": (
        ("lumber", "0.25"),
        ("masonry", "0.15"),
        ("tools", "0.05"),
        ("antq_cordage", "0.030"),
    ),
    "antq_s2_storehouse_construction": (
        ("masonry", "0.25"),
        ("lumber", "0.20"),
        ("pottery", "0.08"),
        ("antq_cordage", "0.030"),
    ),
    "antq_s2_roadworks_construction": (
        ("stone", "0.30"),
        ("masonry", "0.20"),
        ("lumber", "0.10"),
        ("antq_cordage", "0.020"),
    ),
}

# These families must be day-one constructible from raw materials so ordinary
# construction, ship repair, and army upkeep are not seed-locked.
OPENING_STAPLE_BUILDINGS = frozenset({
    "antq_reg_ropewalk",
    "antq_reg_charcoal_hearth",
    "antq_reg_iron_bloomery",
    "antq_reg_brickworks",
    "antq_reg_ironmongery",
    "antq_reg_linen_weavery",
    "antq_reg_pottery_kiln",
    "antq_reg_hide_curing_yard",
    "antq_reg_leatherworks",
    "antq_reg_grain_mill",
    "antq_reg_fish_saltery",
    "antq_reg_meat_curing_yard",
    "antq_reg_sailmaker",
    "antq_reg_arrow_fletchery",
    "antq_reg_shipyard",
    # Cavalry maintenance and Mediterranean food processing were profile-locked
    # to a handful of tags. They must be recoverable from raw materials by any
    # polity that can actually place the building.
    "antq_reg_cheese_dairy",
    "antq_reg_olive_press",
})

# Processed goods demanded by ordinary infantry, cavalry, and ships. Regional
# camel/elephant specialties stay profile-gated.
ARMY_STAPLE_GOODS = frozenset({
    "weaponry",
    "antq_leather_goods",
    "antq_iron_hardware",
    "antq_grain_products",
    "antq_cured_meat",
    "antq_cheese_curds",
    "antq_cordage",
    "antq_sailcloth",
    "antq_preserved_fish",
})

# One opening producer per remaining processed staple. Profile-gated, not
# world-universal; later-antique specialties stay dated.
OPENING_PRIMARY_PRODUCERS = OPENING_STAPLE_BUILDINGS | frozenset({
    "antq_reg_wine_press",
    "antq_reg_brewhouse",
    "antq_reg_olive_press",
    "antq_reg_cheese_dairy",
    "antq_reg_joinery",
    "antq_reg_glassworks",
    "antq_reg_jeweler",
    "antq_reg_bronze_foundry",
    "antq_reg_scriptorium",
    "antq_reg_wax_workshop",
    "antq_reg_soapworks",
    "antq_reg_perfumery",
    "antq_reg_papyrus_workshop",
    "antq_reg_parchmentery",
    "antq_reg_feltworks",
    "antq_reg_carpet_loom",
    "antq_reg_lacquer_workshop",
    "antq_reg_crucible_steel_workshop",
    "antq_reg_rice_wine_house",
    "antq_reg_soy_fermentary",
    "antq_reg_sesame_oil_press",
    "antq_reg_coconut_workshop",
    "antq_reg_date_drying_yard",
    "antq_reg_nut_grinding_house",
    "antq_reg_fineware_kiln",
    "antq_reg_lead_foundry",
    "antq_reg_amber_carver",
    "antq_reg_dye_workshop",
    "antq_reg_fullonica",
    "antq_reg_tesserae_kiln",
})

# Custom raw goods cannot use live ``change_raw_material`` on 1.3.11.
# These peasant cultivators are the AD 1 extraction route.
OPENING_CUSTOM_CULTIVATORS = frozenset({
    "antq_cult_papyrus_beds",
    "antq_cult_date_groves",
    "antq_cult_sesame_plots",
    "antq_cult_nut_orchards",
    "antq_cult_coconut_groves",
    "antq_cult_camel_corrals",
    "antq_cult_barley_plots",
})

PACKAGE_NAMES = {
    CULTIVATOR_CONSTRUCTION_PACKAGE: "Household Cultivator Construction",
    TRIBAL_CONSTRUCTION_PACKAGES["subsistence"]: "Tribal Subsistence Construction",
    TRIBAL_CONSTRUCTION_PACKAGES["pastoral"]: "Tribal Pastoral Construction",
    TRIBAL_CONSTRUCTION_PACKAGES["craft"]: "Tribal Craft Construction",
    TRIBAL_CONSTRUCTION_PACKAGES["exchange"]: "Tribal Exchange Construction",
    TRIBAL_CONSTRUCTION_PACKAGES["ritual"]: "Tribal Ritual Construction",
    TRIBAL_CONSTRUCTION_PACKAGES["warrior"]: "Tribal Warrior Construction",
    "antq_s2_enabling_industry_construction": "Enabling Industry Construction",
    "antq_s2_workshop_construction": "Workshop Construction",
    "antq_s2_market_construction": "Market Construction",
    "antq_s2_port_construction": "Port Construction",
    "antq_s2_fortification_construction": "Fortification Construction",
    "antq_s2_waterworks_construction": "Waterworks Construction",
    "antq_s2_civic_construction": "Civic Construction",
    "antq_s2_archive_construction": "Archive Construction",
    "antq_s2_sanctuary_construction": "Sanctuary Construction",
    "antq_s2_rural_construction": "Rural Construction",
    "antq_s2_storehouse_construction": "Storehouse Construction",
    "antq_s2_roadworks_construction": "Roadworks Construction",
}

UPKEEP_GOODS: dict[str, tuple[tuple[str, str], ...]] = {
    # Institutional demand may only use RGOs or goods whose opening staple
    # producer is universally constructible from raw materials. Papyrus, steel,
    # incense, sailcloth, and similar specialties remain trade goods, not a
    # day-one maintenance lock on every civic or military building.
    "antq_s2_enabling_industry_construction": (),
    "antq_s2_workshop_construction": (
        ("antq_cordage", "0.010"),
        ("tools", "0.010"),
    ),
    "antq_s2_market_construction": (
        ("pottery", "0.020"),
        ("cloth", "0.015"),
    ),
    "antq_s2_port_construction": (
        ("antq_cordage", "0.040"),
        ("tar", "0.020"),
    ),
    "antq_s2_fortification_construction": (
        ("weaponry", "0.020"),
        ("leather", "0.020"),
    ),
    "antq_s2_waterworks_construction": (
        ("tools", "0.020"),
        ("masonry", "0.010"),
    ),
    "antq_s2_civic_construction": (
        ("cloth", "0.020"),
        ("pottery", "0.010"),
    ),
    "antq_s2_archive_construction": (
        ("cloth", "0.020"),
        ("leather", "0.015"),
    ),
    "antq_s2_sanctuary_construction": (
        ("pottery", "0.020"),
        ("cloth", "0.010"),
    ),
    "antq_s2_rural_construction": (
        ("antq_cordage", "0.020"),
        ("leather", "0.015"),
        ("tools", "0.010"),
    ),
    "antq_s2_storehouse_construction": (
        ("pottery", "0.020"),
        ("antq_cordage", "0.010"),
    ),
    "antq_s2_roadworks_construction": (
        ("tools", "0.020"),
        ("antq_cordage", "0.015"),
    ),
}

WATER_TOKENS = (
    "aqua", "aqueduct", "bath", "canal", "cistern", "irrig", "noria",
    "qanat", "reservoir", "sluice", "thermae", "water",
)
ARCHIVE_TOKENS = (
    "academy", "archive", "library", "school", "scriptor", "stationer",
    "taixue",
)
STORAGE_TOKENS = (
    "annona", "granary", "horrea", "storehouse", "warehouse",
)
ROAD_TOKENS = (
    "bridge", "caravanserai", "cursus", "ferry", "mansio", "road",
)
RURAL_TOKENS = (
    "estate", "farm", "field", "garden", "grove", "orchard", "pasture",
    "terrace", "villa",
)


def _contains(key: str, tokens: tuple[str, ...]) -> bool:
    return any(token in key for token in tokens)


def construction_package(key: str, category: str) -> str:
    """Assign one reviewed demand package from stable building semantics."""
    if key in OPENING_CUSTOM_CULTIVATORS or key.startswith("antq_cult_"):
        return CULTIVATOR_CONSTRUCTION_PACKAGE
    if key in OPENING_STAPLE_BUILDINGS:
        return "antq_s2_enabling_industry_construction"
    if category == "defense_category":
        return "antq_s2_fortification_construction"
    if category == "naval_category":
        return "antq_s2_port_construction"
    if category == "religious_category":
        return "antq_s2_sanctuary_construction"
    if _contains(key, STORAGE_TOKENS):
        return "antq_s2_storehouse_construction"
    if _contains(key, WATER_TOKENS):
        return "antq_s2_waterworks_construction"
    if _contains(key, ARCHIVE_TOKENS):
        return "antq_s2_archive_construction"
    if _contains(key, ROAD_TOKENS):
        return "antq_s2_roadworks_construction"
    if _contains(key, RURAL_TOKENS):
        return "antq_s2_rural_construction"
    if category == "trade_category":
        return "antq_s2_market_construction"
    if category in {"cultural_category", "government_category", "infrastructure_category"}:
        return "antq_s2_civic_construction"
    return "antq_s2_workshop_construction"


def institutional_upkeep(
    key: str,
    category: str,
    *,
    productive: bool,
) -> tuple[tuple[str, str], ...]:
    """Add bounded demand only to services; productive recipes stay calibrated."""
    if productive:
        return ()
    return UPKEEP_GOODS[construction_package(key, category)]


def merge_goods(
    base: Iterable[tuple[str, str]],
    additions: Iterable[tuple[str, str]],
) -> tuple[tuple[str, str], ...]:
    """Merge additions without emitting duplicate good keys."""
    result = list(base)
    positions = {good: index for index, (good, _amount) in enumerate(result)}
    for good, amount in additions:
        if good not in positions:
            positions[good] = len(result)
            result.append((good, amount))
            continue
        index = positions[good]
        combined = Decimal(result[index][1]) + Decimal(amount)
        rendered = format(combined, "f").rstrip("0").rstrip(".")
        result[index] = (good, rendered or "0")
    return tuple(result)
