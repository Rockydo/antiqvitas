"""Shared construction and institutional-upkeep contracts for S2 economy chains."""

from __future__ import annotations

from decimal import Decimal
from typing import Iterable


PACKAGE_GOODS: dict[str, tuple[tuple[str, str], ...]] = {
    "antq_s2_workshop_construction": (
        ("masonry", "0.30"),
        ("lumber", "0.10"),
        ("tools", "0.05"),
        ("antq_iron_hardware", "0.025"),
        ("antq_cordage", "0.020"),
    ),
    "antq_s2_market_construction": (
        ("masonry", "0.30"),
        ("lumber", "0.15"),
        ("cloth", "0.05"),
        ("pottery", "0.04"),
        ("antq_iron_hardware", "0.020"),
        ("antq_leather_goods", "0.020"),
    ),
    "antq_s2_port_construction": (
        ("lumber", "0.40"),
        ("masonry", "0.10"),
        ("naval_supplies", "0.10"),
        ("tar", "0.06"),
        ("antq_cordage", "0.060"),
        ("antq_sailcloth", "0.040"),
        ("antq_iron_hardware", "0.025"),
    ),
    "antq_s2_fortification_construction": (
        ("masonry", "0.30"),
        ("stone", "0.25"),
        ("lumber", "0.20"),
        ("weaponry", "0.05"),
        ("steel", "0.010"),
        ("antq_iron_hardware", "0.040"),
        ("antq_leather_goods", "0.025"),
    ),
    "antq_s2_waterworks_construction": (
        ("masonry", "0.35"),
        ("stone", "0.20"),
        ("lumber", "0.10"),
        ("tools", "0.05"),
        ("antq_lead_wares", "0.040"),
        ("antq_iron_hardware", "0.025"),
    ),
    "antq_s2_civic_construction": (
        ("masonry", "0.35"),
        ("stone", "0.15"),
        ("lumber", "0.10"),
        ("cloth", "0.04"),
        ("antq_bronze_wares", "0.025"),
        ("antq_fine_ceramics", "0.025"),
    ),
    "antq_s2_archive_construction": (
        ("masonry", "0.25"),
        ("lumber", "0.15"),
        ("paper", "0.05"),
        ("books", "0.03"),
        ("antq_papyrus", "0.030"),
        ("antq_parchment", "0.020"),
        ("antq_wax_goods", "0.020"),
    ),
    "antq_s2_sanctuary_construction": (
        ("masonry", "0.30"),
        ("stone", "0.15"),
        ("lumber", "0.10"),
        ("incense", "0.02"),
        ("antq_bronze_wares", "0.020"),
        ("antq_wax_goods", "0.020"),
        ("antq_fine_ceramics", "0.020"),
    ),
    "antq_s2_rural_construction": (
        ("lumber", "0.25"),
        ("masonry", "0.15"),
        ("tools", "0.05"),
        ("antq_cordage", "0.030"),
        ("antq_leather_goods", "0.025"),
        ("antq_iron_hardware", "0.020"),
    ),
    "antq_s2_storehouse_construction": (
        ("masonry", "0.25"),
        ("lumber", "0.20"),
        ("pottery", "0.08"),
        ("antq_cordage", "0.030"),
        ("antq_iron_hardware", "0.025"),
    ),
    "antq_s2_roadworks_construction": (
        ("stone", "0.30"),
        ("masonry", "0.20"),
        ("lumber", "0.10"),
        ("antq_iron_hardware", "0.025"),
        ("antq_cordage", "0.020"),
    ),
}

PACKAGE_NAMES = {
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
    "antq_s2_workshop_construction": (
        ("antq_iron_hardware", "0.010"),
        ("antq_cordage", "0.010"),
    ),
    "antq_s2_market_construction": (
        ("antq_cordage", "0.020"),
        ("antq_leather_goods", "0.015"),
        ("antq_fine_ceramics", "0.010"),
    ),
    "antq_s2_port_construction": (
        ("antq_cordage", "0.040"),
        ("antq_sailcloth", "0.030"),
        ("antq_iron_hardware", "0.020"),
        ("antq_cured_meat", "0.020"),
    ),
    "antq_s2_fortification_construction": (
        ("steel", "0.005"),
        ("antq_iron_hardware", "0.030"),
        ("antq_leather_goods", "0.020"),
        ("antq_cured_meat", "0.030"),
    ),
    "antq_s2_waterworks_construction": (
        ("antq_lead_wares", "0.030"),
        ("antq_iron_hardware", "0.020"),
    ),
    "antq_s2_civic_construction": (
        ("antq_papyrus", "0.020"),
        ("antq_parchment", "0.010"),
        ("antq_wax_goods", "0.010"),
        ("antq_bronze_wares", "0.010"),
    ),
    "antq_s2_archive_construction": (
        ("antq_papyrus", "0.040"),
        ("antq_parchment", "0.030"),
        ("antq_wax_goods", "0.020"),
    ),
    "antq_s2_sanctuary_construction": (
        ("incense", "0.020"),
        ("antq_wax_goods", "0.020"),
        ("antq_perfumes", "0.010"),
        ("antq_fine_ceramics", "0.010"),
    ),
    "antq_s2_rural_construction": (
        ("antq_cordage", "0.020"),
        ("antq_leather_goods", "0.020"),
        ("antq_iron_hardware", "0.010"),
    ),
    "antq_s2_storehouse_construction": (
        ("antq_cordage", "0.020"),
        ("antq_iron_hardware", "0.010"),
    ),
    "antq_s2_roadworks_construction": (
        ("antq_iron_hardware", "0.020"),
        ("antq_cordage", "0.020"),
        ("antq_leather_goods", "0.010"),
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
