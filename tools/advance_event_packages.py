#!/usr/bin/env python3
"""Shared event-response bridges for ANTIQVITAS advance packages."""

from __future__ import annotations

FOUNDATIONS = (
    {
        "statecraft": "antq_imperial_cult",
        "warfare": "antq_professional_standing_armies",
        "exchange": "antq_monsoon_navigation",
        "learning": "antq_paper_precursors",
        "society": "antq_civic_associations",
    },
    {
        "statecraft": "antq_jurists_law",
        "warfare": "antq_cataphract_adoption",
        "exchange": "antq_silk_road_caravanserais",
        "learning": "antq_juristic_schools",
        "society": "antq_cosmopolitan_cities",
    },
    {
        "statecraft": "antq_crisis_coinage",
        "warfare": "antq_mobile_field_armies",
        "exchange": "antq_crisis_trade_routes",
        "learning": "antq_crisis_scholarly_preservation",
        "society": "antq_crisis_communities",
    },
    {
        "statecraft": "antq_diocesan_administration",
        "warfare": "antq_comitatenses_doctrine",
        "exchange": "antq_state_annona_routes",
        "learning": "antq_state_church",
        "society": "antq_church_endowments",
    },
    {
        "statecraft": "antq_kingdom_charters",
        "warfare": "antq_federate_musters",
        "exchange": "antq_migration_market_links",
        "learning": "antq_monastic_libraries",
        "society": "antq_hospitality_of_barbarians",
    },
    {
        "statecraft": "antq_regional_law_codes",
        "warfare": "antq_regional_militias",
        "exchange": "antq_regional_caravans",
        "learning": "antq_regional_chronicles",
        "society": "antq_migration_networks",
    },
)


def event_track(kind: str) -> str:
    lowered = kind.lower()
    if lowered in {"formation", "tagswitch", "government", "succession"}:
        return "statecraft"
    if lowered in {"disaster", "situation", "war", "invasion", "revolt"}:
        return "warfare"
    if lowered in {"trade", "economy", "market"}:
        return "exchange"
    if lowered in {"institution", "religion", "learning"}:
        return "learning"
    return "society"


def knowledge_response_lines(kind: str, age_index: int) -> tuple[str, ...]:
    """Reward preparedness without suppressing a historical current."""
    track = event_track(kind)
    advance = FOUNDATIONS[age_index][track]
    # Warfare currents commonly carry an immediate stability cost.  Rewarding
    # preparation with the exact opposite stability constant makes the option
    # tooltip read as a cosmetic loss-and-refund and can leave its net effect
    # at zero.  Army tradition is both thematically appropriate and visibly
    # consequential without erasing the current's political cost.
    effect = (
        "add_army_tradition = army_tradition_weak_bonus"
        if track == "warfare"
        else "add_prestige = prestige_weak_bonus"
    )
    return (
        "\t\t# Learned practice shapes the response; it never gates the current.",
        "\t\tif = {",
        f"\t\t\tlimit = {{ has_advance = {advance} }}",
        f"\t\t\t{effect}",
        "\t\t}",
    )
