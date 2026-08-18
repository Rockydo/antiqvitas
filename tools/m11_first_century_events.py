#!/usr/bin/env python3
"""Per-current first-century phase-event effect packages.

Theme defaults remain the fallback for later centuries. These packages make
each AD 1-100 current pay a distinct, historically bounded cost instead of
repeating the same stability/prestige pair.
"""

from __future__ import annotations


def gold(cost: int) -> str:
    return f"\t\tadd_gold = -{cost}"


def manpower(factor: str) -> str:
    return f"\t\tadd_manpower = {{ value = monthly_manpower multiply = {factor} }}"


# Directed = costly intervention. Delegated = cheaper local/default path.
# Every first-century current must have a unique (directed, delegated) pair.
FIRST_CENTURY_EFFECTS: dict[str, dict[str, tuple[str, ...]]] = {
    "gaius_eastern_settlement": {
        "directed": (gold(18), "\t\tadd_legitimacy = legitimacy_mild_bonus", "\t\tadd_prestige = prestige_weak_bonus"),
        "delegated": (gold(8), manpower("-0.35"), "\t\tadd_stability = stability_weak_penalty"),
    },
    "immensum_bellum": {
        "directed": (gold(22), manpower("-1.0"), "\t\tadd_army_tradition = army_tradition_mild_bonus"),
        "delegated": (gold(10), "\t\tadd_war_exhaustion = war_exhaustion_weak_bonus", "\t\tadd_prestige = prestige_weak_penalty"),
    },
    "illyrian_revolt": {
        "directed": (gold(20), manpower("-0.9"), "\t\tadd_stability = stability_mild_bonus"),
        "delegated": (gold(9), "\t\tadd_army_tradition = army_tradition_weak_bonus", manpower("-0.4")),
    },
    "teutoburg": {
        "directed": (gold(16), manpower("-0.6"), "\t\tadd_army_tradition = army_tradition_weak_bonus"),
        "delegated": (gold(6), "\t\tadd_war_exhaustion = war_exhaustion_weak_bonus", "\t\tadd_prestige = prestige_mild_penalty"),
    },
    "wang_mang_xin": {
        "directed": (gold(20), "\t\tadd_stability = stability_mild_bonus", "\t\tadd_legitimacy = legitimacy_weak_penalty"),
        "delegated": (gold(7), "\t\tadd_legitimacy = legitimacy_mild_bonus", "\t\tadd_stability = stability_weak_penalty"),
    },
    "augustan_succession": {
        "directed": (gold(14), "\t\tadd_legitimacy = legitimacy_mild_bonus", "\t\tadd_prestige = prestige_weak_bonus"),
        "delegated": (gold(5), "\t\tadd_stability = stability_weak_penalty", "\t\tadd_legitimacy = legitimacy_weak_bonus"),
    },
    "tacfarinas_war": {
        "directed": (gold(17), manpower("-0.7"), "\t\tadd_army_tradition = army_tradition_weak_bonus"),
        "delegated": (gold(8), "\t\tadd_prestige = prestige_weak_penalty", manpower("-0.3")),
    },
    "florus_sacrovir": {
        "directed": (gold(13), "\t\tadd_stability = stability_mild_bonus", manpower("-0.4")),
        "delegated": (gold(6), "\t\tadd_prestige = prestige_weak_bonus", "\t\tadd_stability = stability_weak_penalty"),
    },
    "kushan_unification": {
        "directed": (gold(15), "\t\tadd_legitimacy = legitimacy_mild_bonus", manpower("-0.45")),
        "delegated": (gold(7), "\t\tadd_prestige = prestige_mild_bonus", "\t\tadd_stability = stability_weak_penalty"),
    },
    "christianity_foundation": {
        "directed": (gold(10), "\t\tadd_religious_influence_if_valid = { VALUE = religious_influence_mild_bonus }", "\t\tadd_stability = stability_weak_penalty"),
        "delegated": (gold(4), "\t\tadd_legitimacy = legitimacy_weak_bonus", "\t\tadd_religious_influence_if_valid = { VALUE = religious_influence_weak_penalty }"),
    },
    "trung_sisters": {
        "directed": (gold(16), manpower("-0.8"), "\t\tadd_prestige = prestige_weak_bonus"),
        "delegated": (gold(7), "\t\tadd_stability = stability_weak_penalty", manpower("-0.35")),
    },
    "mauretania_annexation": {
        "directed": (gold(18), "\t\tadd_legitimacy = legitimacy_mild_bonus", manpower("-0.5")),
        "delegated": (gold(8), "\t\tadd_prestige = prestige_weak_bonus", "\t\tadd_stability = stability_weak_penalty"),
    },
    "claudian_britain": {
        "directed": (gold(24), manpower("-1.1"), "\t\tadd_army_tradition = army_tradition_mild_bonus"),
        "delegated": (gold(11), "\t\tadd_war_exhaustion = war_exhaustion_weak_bonus", "\t\tadd_prestige = prestige_weak_bonus"),
    },
    "xiongnu_split": {
        "directed": (gold(12), "\t\tadd_legitimacy = legitimacy_mild_bonus", manpower("-0.4")),
        "delegated": (gold(5), "\t\tadd_prestige = prestige_mild_penalty", "\t\tadd_stability = stability_weak_bonus"),
    },
    "silphium_extinction": {
        "directed": (gold(11), "\t\tadd_research_progress = research_progress_mild_bonus", "\t\tadd_prestige = prestige_weak_penalty"),
        "delegated": (gold(4), "\t\tadd_stability = stability_weak_bonus", "\t\tadd_prestige = prestige_mild_penalty"),
    },
    "armenian_war": {
        "directed": (gold(21), manpower("-0.85"), "\t\tadd_legitimacy = legitimacy_weak_bonus"),
        "delegated": (gold(9), "\t\tadd_prestige = prestige_mild_bonus", "\t\tadd_stability = stability_weak_penalty"),
    },
    "boudica_revolt": {
        "directed": (gold(19), manpower("-0.95"), "\t\tadd_stability = stability_weak_bonus"),
        "delegated": (gold(8), "\t\tadd_army_tradition = army_tradition_mild_bonus", "\t\tadd_prestige = prestige_weak_penalty"),
    },
    "great_fire_rome": {
        "directed": (gold(25), "\t\tadd_stability = stability_mild_bonus", "\t\tadd_prestige = prestige_weak_penalty"),
        "delegated": (gold(10), "\t\tadd_legitimacy = legitimacy_weak_penalty", "\t\tadd_stability = stability_weak_bonus"),
    },
    "buddhism_han_court": {
        "directed": (gold(12), "\t\tadd_research_progress = research_progress_mild_bonus", "\t\tadd_religious_influence_if_valid = { VALUE = religious_influence_weak_bonus }"),
        "delegated": (gold(5), "\t\tadd_legitimacy = legitimacy_mild_bonus", "\t\tadd_stability = stability_weak_penalty"),
    },
    "tiridates_coronation": {
        "directed": (gold(16), "\t\tadd_prestige = prestige_mild_bonus", "\t\tadd_legitimacy = legitimacy_weak_bonus"),
        "delegated": (gold(7), manpower("-0.3"), "\t\tadd_prestige = prestige_weak_bonus"),
    },
    "great_jewish_revolt": {
        "directed": (gold(23), manpower("-1.05"), "\t\tadd_stability = stability_weak_bonus"),
        "delegated": (gold(10), "\t\tadd_war_exhaustion = war_exhaustion_weak_bonus", "\t\tadd_army_tradition = army_tradition_weak_bonus"),
    },
    "year_four_emperors": {
        "directed": (gold(20), "\t\tadd_legitimacy = legitimacy_mild_bonus", manpower("-0.7")),
        "delegated": (gold(8), "\t\tadd_stability = stability_mild_penalty", "\t\tadd_prestige = prestige_weak_bonus"),
    },
    "batavian_revolt": {
        "directed": (gold(17), manpower("-0.65"), "\t\tadd_prestige = prestige_weak_penalty"),
        "delegated": (gold(7), "\t\tadd_army_tradition = army_tradition_mild_bonus", "\t\tadd_stability = stability_weak_penalty"),
    },
    "second_temple_destruction": {
        "directed": (gold(14), "\t\tadd_religious_influence_if_valid = { VALUE = religious_influence_mild_penalty }", "\t\tadd_stability = stability_weak_bonus"),
        "delegated": (gold(6), "\t\tadd_prestige = prestige_mild_penalty", manpower("-0.25")),
    },
    "vesuvius": {
        "directed": (gold(22), "\t\tadd_stability = stability_mild_bonus", manpower("-0.2")),
        "delegated": (gold(9), "\t\tadd_prestige = prestige_weak_penalty", "\t\tadd_legitimacy = legitimacy_weak_bonus"),
    },
    "mons_graupius": {
        "directed": (gold(15), manpower("-0.55"), "\t\tadd_army_tradition = army_tradition_mild_bonus"),
        "delegated": (gold(6), "\t\tadd_war_exhaustion = war_exhaustion_weak_bonus", "\t\tadd_prestige = prestige_mild_bonus"),
    },
    "dacian_wars": {
        "directed": (gold(21), manpower("-0.9"), "\t\tadd_army_tradition = army_tradition_weak_bonus"),
        "delegated": (gold(9), "\t\tadd_prestige = prestige_weak_bonus", "\t\tadd_war_exhaustion = war_exhaustion_weak_bonus"),
    },
    "han_xianbei": {
        "directed": (gold(18), manpower("-0.75"), "\t\tadd_prestige = prestige_weak_bonus"),
        "delegated": (gold(8), "\t\tadd_stability = stability_weak_bonus", "\t\tadd_legitimacy = legitimacy_weak_penalty"),
    },
    "gan_ying": {
        "directed": (gold(13), "\t\tadd_research_progress = research_progress_mild_bonus", "\t\tadd_prestige = prestige_mild_bonus"),
        "delegated": (gold(5), "\t\tadd_legitimacy = legitimacy_weak_bonus", "\t\tadd_research_progress = research_progress_weak_bonus"),
    },
    "moche_formation": {
        "directed": (gold(11), "\t\tadd_stability = stability_mild_bonus", "\t\tadd_prestige = prestige_weak_bonus"),
        "delegated": (gold(4), "\t\tadd_legitimacy = legitimacy_weak_bonus", manpower("-0.2")),
    },
}


def packages_are_unique() -> list[str]:
    failures: list[str] = []
    seen: dict[tuple[tuple[str, ...], tuple[str, ...]], str] = {}
    for key, package in FIRST_CENTURY_EFFECTS.items():
        signature = (package["directed"], package["delegated"])
        prior = seen.get(signature)
        if prior:
            failures.append(f"{key} reuses first-century effect pair from {prior}")
        else:
            seen[signature] = key
    return failures
