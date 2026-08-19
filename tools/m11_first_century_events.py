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


SECOND_CENTURY_EFFECTS: dict[str, dict[str, tuple[str, ...]]] = {
    "trajan_dacia": {
        "directed": (gold(26), manpower("-1.2"), "\t\tadd_army_tradition = army_tradition_mild_bonus"),
        "delegated": (gold(12), "\t\tadd_war_exhaustion = war_exhaustion_weak_bonus", "\t\tadd_prestige = prestige_weak_bonus"),
    },
    "cai_lun_paper": {
        "directed": (gold(9), "\t\tadd_research_progress = research_progress_mild_bonus", "\t\tadd_prestige = prestige_weak_bonus"),
        "delegated": (gold(3), "\t\tadd_legitimacy = legitimacy_weak_bonus", "\t\tadd_research_progress = research_progress_weak_bonus"),
    },
    "trajan_parthia": {
        "directed": (gold(27), manpower("-1.15"), "\t\tadd_legitimacy = legitimacy_weak_bonus"),
        "delegated": (gold(12), "\t\tadd_prestige = prestige_mild_bonus", "\t\tadd_war_exhaustion = war_exhaustion_weak_bonus"),
    },
    "antioch_earthquake": {
        "directed": (gold(20), "\t\tadd_stability = stability_mild_bonus", manpower("-0.15")),
        "delegated": (gold(8), "\t\tadd_prestige = prestige_weak_penalty", "\t\tadd_legitimacy = legitimacy_weak_bonus"),
    },
    "hadrians_wall": {
        "directed": (gold(19), "\t\tadd_stability = stability_weak_bonus", manpower("-0.35")),
        "delegated": (gold(8), "\t\tadd_army_tradition = army_tradition_weak_bonus", "\t\tadd_prestige = prestige_weak_penalty"),
    },
    "kanishka_apogee": {
        "directed": (gold(14), "\t\tadd_legitimacy = legitimacy_mild_bonus", "\t\tadd_research_progress = research_progress_weak_bonus"),
        "delegated": (gold(6), "\t\tadd_prestige = prestige_mild_bonus", "\t\tadd_stability = stability_weak_penalty"),
    },
    "bar_kokhba": {
        "directed": (gold(24), manpower("-1.0"), "\t\tadd_stability = stability_weak_bonus"),
        "delegated": (gold(11), "\t\tadd_army_tradition = army_tradition_mild_bonus", "\t\tadd_prestige = prestige_mild_penalty"),
    },
    "antonine_wall": {
        "directed": (gold(17), manpower("-0.4"), "\t\tadd_prestige = prestige_weak_bonus"),
        "delegated": (gold(7), "\t\tadd_stability = stability_weak_bonus", "\t\tadd_war_exhaustion = war_exhaustion_weak_bonus"),
    },
    "celestial_masters": {
        "directed": (gold(10), "\t\tadd_religious_influence_if_valid = { VALUE = religious_influence_mild_bonus }", "\t\tadd_stability = stability_weak_penalty"),
        "delegated": (gold(4), "\t\tadd_legitimacy = legitimacy_mild_bonus", "\t\tadd_religious_influence_if_valid = { VALUE = religious_influence_weak_penalty }"),
    },
    "gothic_migration": {
        "directed": (gold(16), "\t\tadd_stability = stability_mild_bonus", manpower("-0.3")),
        "delegated": (gold(7), manpower("-0.55"), "\t\tadd_prestige = prestige_weak_penalty"),
    },
    "verus_parthia": {
        "directed": (gold(22), manpower("-0.8"), "\t\tadd_army_tradition = army_tradition_weak_bonus"),
        "delegated": (gold(10), "\t\tadd_prestige = prestige_weak_bonus", "\t\tadd_stability = stability_weak_penalty"),
    },
    "antonine_plague": {
        "directed": (gold(23), "\t\tadd_stability = stability_mild_bonus", manpower("-0.6")),
        "delegated": (gold(9), "\t\tadd_legitimacy = legitimacy_weak_bonus", "\t\tadd_prestige = prestige_mild_penalty"),
    },
    "daqin_embassy": {
        "directed": (gold(12), "\t\tadd_prestige = prestige_mild_bonus", "\t\tadd_research_progress = research_progress_weak_bonus"),
        "delegated": (gold(5), "\t\tadd_legitimacy = legitimacy_weak_bonus", "\t\tadd_prestige = prestige_weak_bonus"),
    },
    "marcomannic_wars": {
        "directed": (gold(25), manpower("-1.05"), "\t\tadd_army_tradition = army_tradition_mild_bonus"),
        "delegated": (gold(11), "\t\tadd_war_exhaustion = war_exhaustion_weak_bonus", "\t\tadd_stability = stability_weak_penalty"),
    },
    "yellow_turbans": {
        "directed": (gold(21), manpower("-0.85"), "\t\tadd_stability = stability_weak_bonus"),
        "delegated": (gold(9), "\t\tadd_legitimacy = legitimacy_mild_penalty", "\t\tadd_army_tradition = army_tradition_weak_bonus"),
    },
    "champa_formation": {
        "directed": (gold(11), "\t\tadd_legitimacy = legitimacy_mild_bonus", "\t\tadd_prestige = prestige_weak_bonus"),
        "delegated": (gold(4), manpower("-0.25"), "\t\tadd_stability = stability_weak_bonus"),
    },
    "five_emperors": {
        "directed": (gold(22), "\t\tadd_legitimacy = legitimacy_mild_bonus", manpower("-0.65")),
        "delegated": (gold(9), "\t\tadd_stability = stability_mild_penalty", "\t\tadd_prestige = prestige_weak_bonus"),
    },
}


LATER_CENTURY_EFFECTS: dict[str, dict[str, tuple[str, ...]]] = {
    "severus_caledonia": {
        "directed": (gold(23), manpower("-0.95"), "\t\tadd_army_tradition = army_tradition_weak_bonus"),
        "delegated": (gold(10), "\t\tadd_war_exhaustion = war_exhaustion_weak_bonus", "\t\tadd_prestige = prestige_mild_penalty"),
    },
    "constitutio_antoniniana": {
        "directed": (gold(18), "\t\tadd_legitimacy = legitimacy_mild_bonus", "\t\tadd_stability = stability_weak_penalty"),
        "delegated": (gold(7), "\t\tadd_prestige = prestige_weak_bonus", "\t\tadd_legitimacy = legitimacy_weak_penalty"),
    },
    "alemanni_formation": {
        "directed": (gold(13), manpower("-0.45"), "\t\tadd_prestige = prestige_mild_bonus"),
        "delegated": (gold(5), "\t\tadd_stability = stability_weak_bonus", manpower("-0.2")),
    },
    "three_kingdoms": {
        "directed": (gold(24), manpower("-0.9"), "\t\tadd_legitimacy = legitimacy_mild_bonus"),
        "delegated": (gold(11), "\t\tadd_stability = stability_mild_penalty", manpower("-0.4")),
    },
    "sassanid_revolution": {
        "directed": (gold(20), "\t\tadd_legitimacy = legitimacy_mild_bonus", manpower("-0.7")),
        "delegated": (gold(8), "\t\tadd_prestige = prestige_mild_penalty", "\t\tadd_army_tradition = army_tradition_weak_bonus"),
    },
    "third_century_crisis": {
        "directed": (gold(28), "\t\tadd_stability = stability_mild_bonus", manpower("-0.8")),
        "delegated": (gold(12), "\t\tadd_legitimacy = legitimacy_mild_penalty", "\t\tadd_war_exhaustion = war_exhaustion_weak_bonus"),
    },
    "manichaeism_foundation": {
        "directed": (gold(11), "\t\tadd_religious_influence_if_valid = { VALUE = religious_influence_mild_bonus }", "\t\tadd_prestige = prestige_weak_bonus"),
        "delegated": (gold(4), "\t\tadd_stability = stability_weak_penalty", "\t\tadd_research_progress = research_progress_weak_bonus"),
    },
    "frankish_formation": {
        "directed": (gold(14), manpower("-0.5"), "\t\tadd_prestige = prestige_weak_bonus"),
        "delegated": (gold(6), "\t\tadd_stability = stability_weak_bonus", "\t\tadd_army_tradition = army_tradition_weak_bonus"),
    },
    "cyprian_plague": {
        "directed": (gold(21), "\t\tadd_stability = stability_mild_bonus", manpower("-0.55")),
        "delegated": (gold(9), "\t\tadd_prestige = prestige_mild_penalty", "\t\tadd_legitimacy = legitimacy_weak_bonus"),
    },
    "diocletian_dominate": {
        "directed": (gold(22), "\t\tadd_legitimacy = legitimacy_mild_bonus", "\t\tadd_research_progress = research_progress_weak_bonus"),
        "delegated": (gold(9), "\t\tadd_stability = stability_weak_penalty", "\t\tadd_prestige = prestige_weak_bonus"),
    },
    "eight_princes": {
        "directed": (gold(25), manpower("-1.0"), "\t\tadd_legitimacy = legitimacy_weak_bonus"),
        "delegated": (gold(11), "\t\tadd_stability = stability_mild_penalty", "\t\tadd_prestige = prestige_weak_penalty"),
    },
    "armenia_conversion": {
        "directed": (gold(12), "\t\tadd_religious_influence_if_valid = { VALUE = religious_influence_mild_bonus }", "\t\tadd_legitimacy = legitimacy_weak_bonus"),
        "delegated": (gold(5), "\t\tadd_stability = stability_weak_penalty", "\t\tadd_prestige = prestige_mild_bonus"),
    },
    "constantine_civil_wars": {
        "directed": (gold(26), manpower("-1.1"), "\t\tadd_legitimacy = legitimacy_mild_bonus"),
        "delegated": (gold(12), "\t\tadd_army_tradition = army_tradition_mild_bonus", "\t\tadd_stability = stability_weak_penalty"),
    },
    "nicaea": {
        "directed": (gold(10), "\t\tadd_religious_influence_if_valid = { VALUE = religious_influence_mild_bonus }", "\t\tadd_stability = stability_weak_bonus"),
        "delegated": (gold(4), "\t\tadd_legitimacy = legitimacy_weak_bonus", "\t\tadd_religious_influence_if_valid = { VALUE = religious_influence_weak_penalty }"),
    },
    "shapur_julian": {
        "directed": (gold(24), manpower("-0.95"), "\t\tadd_army_tradition = army_tradition_mild_bonus"),
        "delegated": (gold(11), "\t\tadd_prestige = prestige_weak_bonus", "\t\tadd_war_exhaustion = war_exhaustion_weak_bonus"),
    },
    "aksum_meroë": {
        "directed": (gold(15), manpower("-0.6"), "\t\tadd_prestige = prestige_mild_bonus"),
        "delegated": (gold(6), "\t\tadd_legitimacy = legitimacy_weak_bonus", manpower("-0.3")),
    },
    "crete_earthquake": {
        "directed": (gold(16), "\t\tadd_stability = stability_mild_bonus", "\t\tadd_prestige = prestige_weak_penalty"),
        "delegated": (gold(7), manpower("-0.15"), "\t\tadd_legitimacy = legitimacy_weak_bonus"),
    },
    "huns_arrive": {
        "directed": (gold(17), manpower("-0.55"), "\t\tadd_war_exhaustion = war_exhaustion_weak_bonus"),
        "delegated": (gold(7), "\t\tadd_stability = stability_weak_bonus", "\t\tadd_prestige = prestige_mild_penalty"),
    },
    "gothic_refugees": {
        "directed": (gold(18), "\t\tadd_stability = stability_mild_bonus", manpower("-0.35")),
        "delegated": (gold(8), manpower("-0.6"), "\t\tadd_prestige = prestige_weak_penalty"),
    },
    "thessalonica": {
        "directed": (gold(13), "\t\tadd_religious_influence_if_valid = { VALUE = religious_influence_mild_bonus }", "\t\tadd_legitimacy = legitimacy_mild_bonus"),
        "delegated": (gold(5), "\t\tadd_stability = stability_weak_penalty", "\t\tadd_prestige = prestige_weak_bonus"),
    },
    "fei_river": {
        "directed": (gold(23), manpower("-0.85"), "\t\tadd_legitimacy = legitimacy_weak_bonus"),
        "delegated": (gold(10), "\t\tadd_stability = stability_weak_bonus", "\t\tadd_army_tradition = army_tradition_mild_bonus"),
    },
    "gwanggaeto": {
        "directed": (gold(16), manpower("-0.5"), "\t\tadd_legitimacy = legitimacy_mild_bonus"),
        "delegated": (gold(6), "\t\tadd_prestige = prestige_mild_bonus", "\t\tadd_stability = stability_weak_penalty"),
    },
    "olympic_sunset": {
        "directed": (gold(9), "\t\tadd_religious_influence_if_valid = { VALUE = religious_influence_weak_penalty }", "\t\tadd_prestige = prestige_mild_penalty"),
        "delegated": (gold(3), "\t\tadd_stability = stability_weak_bonus", "\t\tadd_legitimacy = legitimacy_weak_penalty"),
    },
    "east_west_division": {
        "directed": (gold(19), "\t\tadd_legitimacy = legitimacy_mild_bonus", "\t\tadd_stability = stability_weak_penalty"),
        "delegated": (gold(8), "\t\tadd_prestige = prestige_weak_penalty", manpower("-0.25")),
    },
    "faxian_gupta": {
        "directed": (gold(12), "\t\tadd_research_progress = research_progress_mild_bonus", "\t\tadd_prestige = prestige_mild_bonus"),
        "delegated": (gold(5), "\t\tadd_legitimacy = legitimacy_weak_bonus", "\t\tadd_research_progress = research_progress_weak_bonus"),
    },
    "radagaisus_rhine": {
        "directed": (gold(21), manpower("-0.75"), "\t\tadd_war_exhaustion = war_exhaustion_weak_bonus"),
        "delegated": (gold(9), "\t\tadd_stability = stability_weak_penalty", "\t\tadd_army_tradition = army_tradition_weak_bonus"),
    },
    "britain_abandoned": {
        "directed": (gold(14), "\t\tadd_stability = stability_weak_bonus", manpower("-0.4")),
        "delegated": (gold(6), "\t\tadd_prestige = prestige_mild_penalty", "\t\tadd_war_exhaustion = war_exhaustion_weak_bonus"),
    },
    "alaric_sack": {
        "directed": (gold(20), manpower("-0.7"), "\t\tadd_prestige = prestige_mild_penalty"),
        "delegated": (gold(8), "\t\tadd_stability = stability_mild_penalty", "\t\tadd_legitimacy = legitimacy_weak_bonus"),
    },
    "visigoth_settlement": {
        "directed": (gold(15), "\t\tadd_stability = stability_mild_bonus", "\t\tadd_prestige = prestige_weak_bonus"),
        "delegated": (gold(6), manpower("-0.35"), "\t\tadd_legitimacy = legitimacy_weak_penalty"),
    },
    "vandal_africa": {
        "directed": (gold(22), manpower("-0.8"), "\t\tadd_prestige = prestige_weak_penalty"),
        "delegated": (gold(10), "\t\tadd_stability = stability_weak_penalty", "\t\tadd_army_tradition = army_tradition_mild_bonus"),
    },
    "attila": {
        "directed": (gold(27), manpower("-1.15"), "\t\tadd_army_tradition = army_tradition_mild_bonus"),
        "delegated": (gold(12), "\t\tadd_war_exhaustion = war_exhaustion_weak_bonus", "\t\tadd_stability = stability_mild_penalty"),
    },
    "hephthalites": {
        "directed": (gold(18), manpower("-0.65"), "\t\tadd_prestige = prestige_weak_bonus"),
        "delegated": (gold(7), "\t\tadd_stability = stability_weak_bonus", manpower("-0.35")),
    },
    "constantinople_earthquake": {
        "directed": (gold(17), "\t\tadd_stability = stability_mild_bonus", "\t\tadd_prestige = prestige_weak_penalty"),
        "delegated": (gold(7), "\t\tadd_legitimacy = legitimacy_weak_bonus", manpower("-0.2")),
    },
    "adventus_saxonum": {
        "directed": (gold(14), manpower("-0.45"), "\t\tadd_stability = stability_weak_bonus"),
        "delegated": (gold(6), "\t\tadd_prestige = prestige_weak_penalty", "\t\tadd_army_tradition = army_tradition_weak_bonus"),
    },
    "chalcedon_avarayr": {
        "directed": (gold(16), "\t\tadd_religious_influence_if_valid = { VALUE = religious_influence_mild_bonus }", manpower("-0.4")),
        "delegated": (gold(7), "\t\tadd_legitimacy = legitimacy_weak_bonus", "\t\tadd_stability = stability_weak_penalty"),
    },
    "vandal_sack_rome": {
        "directed": (gold(19), manpower("-0.55"), "\t\tadd_prestige = prestige_mild_penalty"),
        "delegated": (gold(8), "\t\tadd_stability = stability_mild_penalty", "\t\tadd_war_exhaustion = war_exhaustion_weak_bonus"),
    },
    "cape_bon": {
        "directed": (gold(18), manpower("-0.7"), "\t\tadd_army_tradition = army_tradition_weak_bonus"),
        "delegated": (gold(8), "\t\tadd_prestige = prestige_weak_bonus", "\t\tadd_stability = stability_weak_penalty"),
    },
}


CURRENT_EFFECTS = {**FIRST_CENTURY_EFFECTS, **SECOND_CENTURY_EFFECTS, **LATER_CENTURY_EFFECTS}


def packages_are_unique() -> list[str]:
    failures: list[str] = []
    seen: dict[tuple[tuple[str, ...], tuple[str, ...]], str] = {}
    for key, package in CURRENT_EFFECTS.items():
        signature = (package["directed"], package["delegated"])
        prior = seen.get(signature)
        if prior:
            failures.append(f"{key} reuses effect pair from {prior}")
        else:
            seen[signature] = key
    return failures
