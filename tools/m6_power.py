#!/usr/bin/env python3
"""Validate and render the first sourced ANTIQVITAS M6 power foundation."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from dates import AntqDate, BiographyDate, M2_MIRROR_LANGUAGES
from goods_integration import bindings as goods_bindings, modifier_additions, modifier_name
from s2_ancient_laws import (
    all_law_options as s2_all_law_options,
    profile_law_pairs as s2_profile_law_pairs,
    starting_laws_by_tag as s2_starting_laws_by_tag,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/m6"
TAG_MAP = ROOT / "docs/world_1ad/tag_map.json"
POLITIES = ROOT / "docs/world_1ad/polities.csv"
GOVERNMENT_TYPES = ROOT / "docs/vanilla_symbols/government_type.json"
LOC_ROOT = ROOT / "main_menu/localization"
REFORM_OUTPUT = ROOT / "in_game/common/government_reforms/00_antiquitas_m6_core.txt"
PRIVILEGE_OUTPUT = ROOT / "in_game/common/estate_privileges/00_antiquitas_m6_core.txt"
LAW_OUTPUT = ROOT / "in_game/common/laws/00_antiquitas_m6_core.txt"
CHARACTER_BOOTSTRAP_OUTPUT = ROOT / "in_game/common/on_action/antq_m6_character_bootstrap.txt"
ESTATE_CHANGE_OUTPUT = ROOT / "in_game/common/on_action/estate_changes.txt"
RULER_TRANSITION_EVENT_OUTPUT = ROOT / "in_game/events/antq_m6_ruler_transition.txt"
RULER_GUARD_MODIFIER_OUTPUT = (
    ROOT / "main_menu/common/static_modifiers/00_antiquitas_m6_ruler_guard.txt"
)
POLITICAL_CONTRACT_OUTPUT = ROOT / "docs/m6/political_profile_contracts.csv"
TOKEN_RE = re.compile(r"^[a-z][a-z0-9_]*$")
VALUE_RE = re.compile(r"^(?:-?(?:\d+(?:\.\d+)?|\.\d+)|[a-z][a-z0-9_]*)$")
ROMAN_SUCCESSION_GUARDED = frozenset((
    "antq_augustus",
    "antq_gaius_caesar",
    "antq_tiberius",
    "antq_livia",
))
ANCIENT_SUBSISTENCE_FOOD_FLOOR = 0.10
TEUTOBURG_GUARDED = frozenset(("antq_publius_quinctilius_varus",))
HISTORICAL_LIFESPAN_GUARDED = ROMAN_SUCCESSION_GUARDED | TEUTOBURG_GUARDED
ROMAN_SUCCESSION_GUARD = "antq_m6_historical_lifespan_guard"
DYN_FIELDS = ("key", "name", "home", "source", "confidence", "note")
CHAR_FIELDS = (
    "key", "design_tag", "name", "female", "culture", "religion", "birth_date",
    "death_date", "birthplace", "dynasty", "adm", "dip", "mil", "estate", "source",
    "confidence", "note",
)
GOV_FIELDS = (
    "design_tag", "government_type", "heir_selection", "ruler", "heir", "consort", "active_regent",
    "regency", "start_regency_date", "end_regency_date", "reform", "privileges", "laws", "societal_values",
    "source", "confidence", "note",
)
REGIONAL_GOV_FIELDS = (
    "key", "tags", "privileges", "laws", "source", "confidence", "note",
)
PRIV_FIELDS = ("key", "estate", "name", "description", "modifiers", "source", "confidence", "note")
S2_PRIV_FIELDS = PRIV_FIELDS + ("potential_reforms", "potential_tags", "exclusive_with")
LAW_FIELDS = (
    "law", "law_category", "law_gov_group", "name", "description", "option", "option_name",
    "option_description", "modifiers", "estate_preferences", "source", "confidence", "note",
)
TERM_FIELDS = (
    "design_tag", "character", "engine_start_date", "engine_end_date", "regnal_number",
    "historical_reign", "source", "confidence", "note",
)
REGNAL_HISTORY_FIELDS = (
    "design_tag", "sequence", "name", "historical_start", "historical_end", "source", "confidence", "note",
)
ROSTER_REPORT = DATA / "ROSTER_COVERAGE.md"
MIN_SOURCED_CHARACTERS = 250
MAX_SOURCED_CHARACTERS = 400
MIN_NAMED_TIER_PROFILES = 32
ANONYMOUS_PROFILE_MARKERS = ("anonymous", "no current individual ruler")
# The AD 1 bookmark replaces the installed multi-tier 1337 government and
# privilege stacks with one sourced ancient foundation per polity.  Live
# hands-off campaigns proved that the resulting estate equilibria began near
# 10-20%, then crossed the engine's unconditional-rebellion threshold and
# produced worldwide civil wars in years 3-15.  A first 25-point compact passed
# the opening decade, but an uninterrupted AD 1-99 observer campaign showed a
# slower cascade: 1,292 rebel movements across 271 countries, 38 active defaults,
# and 11 simultaneous civil wars.  Every active default had estate rebels.  A
# Later clean AD 1-29 replays showed why satisfaction alone was insufficient.
# In V24, unlinked estates remained healthy (48.7% p10, 75.1% median), but the
# first temporary shock that created a movement linked the estate to it and
# pinned the linked estate near zero (0.24% p10).  The resulting 1,075 live
# movements produced 36 civil wars and nine defaults.  V25's smaller first
# correction still left the healthy unlinked noble tail at 36.8% (p10), while
# 158 linked noble movements grew by 1.80%/month at the median and drove 33
# civil wars by AD 29.  Fifteen more compact points put every measured healthy
# estate p10 above the engine's 50% danger line.  The installed base modifier
# adds 0.001 passive monthly rebel growth, so the matching -0.001 ancient floor
# removes only that unconditional drift.  Vanilla itself uses a -0.10 joining
# threshold; applying that scale keeps marginally dissatisfied pops out while
# severe discontent, disasters, occupation, and scripted revolts remain live.
FOUNDATIONAL_ESTATE_COMPACT = "0.60"
FOUNDATIONAL_REBEL_GROWTH = "-0.003"
FOUNDATIONAL_REBEL_JOIN_THRESHOLD = "-0.15"
ESTATE_IDENTITY_SETTLEMENT_FLOOR = (
    ("0.20", "0.60"),
    ("0.40", "0.40"),
    ("0.60", "0.20"),
)
SOCIAL_VALUE_KEYS = frozenset((
    "centralization_vs_decentralization", "traditionalist_vs_innovative", "aristocracy_vs_plutocracy",
    "serfdom_vs_free_subjects", "mercantilism_vs_free_trade", "offensive_vs_defensive", "quality_vs_quantity",
    "capital_economy_vs_traditional_economy", "individualism_vs_communalism", "outward_vs_inward",
))
LAW_CATEGORIES = frozenset(("administrative", "military", "religious", "socioeconomic"))
MODIFIER_KEYS = frozenset((
	"clergy_estate_target_satisfaction", "country_cabinet_efficiency", "global_burghers_estate_power",
	"global_clergy_estate_power", "global_crown_estate_power",
	"copper_impacts_inflation", "copper_used_for_minting", "goods_gold_impacts_inflation",
	"goods_gold_used_for_minting",
    "global_levy_size_modifier", "global_nobles_estate_power", "global_pop_assimilation_speed_modifier",
    "global_pop_food_consumption", "global_monthly_food_modifier", "global_tribes_estate_power",
    "burghers_estate_target_satisfaction", "land_morale_modifier", "monthly_towards_aristocracy",
	"minting_income_factor", "minting_inflation_threshold", "monthly_towards_centralization",
	"monthly_towards_decentralization", "nobles_estate_target_satisfaction", "silver_impacts_inflation",
	"silver_used_for_minting", "tribes_estate_target_satisfaction", "slavery_blocked",
	"ban_exports_of_slaves_goods", "ban_imports_of_slaves_goods", "tolerance_heathen",
	"monthly_republican_tradition",
    "global_peasants_estate_power", "peasants_estate_target_satisfaction",
    "nobles_estate_max_tax", "clergy_estate_max_tax", "burghers_estate_max_tax",
    "global_monthly_control", "global_trade_through_owned_territory_efficiency",
    "global_production_efficiency", "research_speed_modifier", "stability_cost_efficiency",
    "cultures_capacity", "court_spending_efficiency", "monthly_rebel_growth",
    "pop_join_rebel_threshold",
    "monthly_towards_free_subjects",
    "crown_estate_power_from_cabinet", "nobles_estate_power_from_cabinet",
    "clergy_estate_power_from_cabinet", "burghers_estate_power_from_cabinet",
    "tribes_estate_power_from_cabinet", "estate_power_from_cabinet",
    "set_cabinet_member_cost_modifier", "replace_cabinet_member_cost_modifier",
))
MODIFIER_KEYS |= frozenset(
    modifier_name(row)
    for row in goods_bindings()
    if row.surface == "privilege_modifier"
)

POLITICAL_CONTRACTS: dict[str, tuple[str, str, str, str]] = {
    "antq_principate": (
        "global_crown_estate_power=0.18|global_nobles_estate_power=0.06|"
        "global_burghers_estate_power=0.05|crown_estate_power_from_cabinet=0.20|"
        "nobles_estate_power_from_cabinet=0.15|replace_cabinet_member_cost_modifier=0.10",
        "P8.1;P11;P13;OCD", "secure",
        "Augustan tribunician and proconsular authority materially strengthens the princeps, while senatorial cabinet leverage plus equestrian access preserve negotiated government and patronage friction below the later Dominate.",
    ),
    "antq_dominate": (
        "global_nobles_estate_power=-0.05|crown_estate_power_from_cabinet=0.25|"
        "set_cabinet_member_cost_modifier=-0.10",
        "P8.1;P11;P13;OCD", "secure",
        "Palatine appointment strengthens the court at the expense of autonomous aristocratic weight.",
    ),
    "antq_han_imperial_bureaucracy": (
        "global_crown_estate_power=0.15|global_nobles_estate_power=0.05|"
        "crown_estate_power_from_cabinet=0.25|set_cabinet_member_cost_modifier=-0.10",
        "P8.3;P13;BHR;CTP-WM", "secure",
        "Imperial offices strengthen the throne while court lineages remain politically consequential.",
    ),
    "antq_lankan_kingdom": (
        "global_clergy_estate_power=0.10|global_peasants_estate_power=0.05|"
        "clergy_estate_power_from_cabinet=0.15|replace_cabinet_member_cost_modifier=0.05",
        "P8.4;P11;P13;CAH-XI", "contested",
        "Monastic patronage and irrigation households shape the sacral court.",
    ),
    "antq_artaxiad_highland_kingship": (
        "global_nobles_estate_power=0.12|global_clergy_estate_power=0.04|"
        "nobles_estate_power_from_cabinet=0.25|replace_cabinet_member_cost_modifier=0.10",
        "P8.2;P11;P13;CAH-XI;IRAN-ARM", "contested",
        "The contested Artaxiad court negotiates authority with highland dynasts and sanctuaries under Roman-Arsacid frontier pressure.",
    ),
    "antq_nabataean_caravan_kingship": (
        "global_nobles_estate_power=0.08|global_burghers_estate_power=0.12|"
        "burghers_estate_power_from_cabinet=0.25|replace_cabinet_member_cost_modifier=0.05",
        "P8.1;P8.5;P11;P13;OCD;PLE;NABATAEA-MAP", "secure",
        "The named Aretas-Huldu court rests on caravan, water, sanctuary, and oasis interests without a claimed uniform bureaucracy.",
    ),
    "antq_himyarite_terrace_kingship": (
        "global_nobles_estate_power=0.10|global_peasants_estate_power=0.08|"
        "estate_power_from_cabinet=0.22|replace_cabinet_member_cost_modifier=0.08",
        "P8.5;P8.6;P11;P13;CAH-XI;OCD-HIM;HIMYAR-HIST;OUP-REDSEA", "contested",
        "Highland lineages and terrace communities structure an anonymous AD 1 royal adapter without inventing a recovered Himyarite office hierarchy.",
    ),
    "antq_satavahana_deccan_kingship": (
        "global_nobles_estate_power=0.10|global_burghers_estate_power=0.08|"
        "nobles_estate_power_from_cabinet=0.18|burghers_estate_power_from_cabinet=0.12|"
        "replace_cabinet_member_cost_modifier=0.06",
        "P8.4;P11;P13;CAH-XI", "contested",
        "A conservative Deccan court adapter balances titled regional houses, guild exchange, gifts, waterworks, and cultivation during a ruler gap.",
    ),
    "antq_catuvellaunian_oppidum_kingship": (
        "global_nobles_estate_power=0.11|global_burghers_estate_power=0.06|"
        "nobles_estate_power_from_cabinet=0.22|replace_cabinet_member_cost_modifier=0.07",
        "P8.7;P11;P13;CAH-XI;BM-DRU", "contested",
        "Tasciovanian kingship coordinates dynastic mints, oppida, retinues, sacred places, and exchange without claiming a recovered British constitution.",
    ),
    "antq_trinovantian_coin_kingship": (
        "global_nobles_estate_power=0.11|global_burghers_estate_power=0.09|"
        "nobles_estate_power_from_cabinet=0.23|country_cabinet_efficiency=0.025",
        "P8.7;P11;P13;CAH-XI;CCI-DUB;BM-DRU", "contested",
        "Dubnovellaunos's coin horizon supports a distinct Trinovantian court while exact Camulodunon procedure and dynastic reach remain unrecoverable.",
    ),
    "antq_brigantian_hillfort_confederacy": (
        "global_tribes_estate_power=0.13|global_nobles_estate_power=0.08|"
        "tribes_estate_power_from_cabinet=0.24|replace_cabinet_member_cost_modifier=0.08",
        "P8.7;P11;P13;CAH-XI;PLE;PTO-GEO-II2;BRIGANTIA-STANWICK", "contested",
        "A large but internally varied northern frame coordinates kindreds, routes, stores, and musters without projecting Cartimandua's later client court back to AD 1.",
    ),
    "antq_durotrigian_hillfort_coin_order": (
        "global_nobles_estate_power=0.08|global_burghers_estate_power=0.11|"
        "estate_power_from_cabinet=0.23|replace_cabinet_member_cost_modifier=0.07",
        "P8.7;P11;P13;CAH-XI;PTO-GEO-II2;DUROTRIGES-PROJECT", "contested",
        "Distinctive coinage, pottery, burial, settlement, and enclosure evidence supports a local order without proving one centralized Durotrigian state.",
    ),
    "antq_ivernian_regional_assembly": (
        "global_tribes_estate_power=0.15|global_nobles_estate_power=0.06|"
        "tribes_estate_power_from_cabinet=0.25|replace_cabinet_member_cost_modifier=0.06",
        "P8.7;P11;P13;PTO-GEO-II1;DARCY-IRE;IRON-AGE-IRELAND", "contested",
        "A deliberately low-centralization Ivernian adapter represents seasonal coordination without back-projecting medieval Gaelic offices or false settlement density.",
    ),
    "antq_aestian_amber_coast_order": (
        "global_tribes_estate_power=0.14|global_burghers_estate_power=0.09|"
        "tribes_estate_power_from_cabinet=0.23|burghers_estate_power_from_cabinet=0.15|"
        "replace_cabinet_member_cost_modifier=0.06",
        "P8.7;P11;P13;TAC-GER-45;ARCHAEOMETRY-NE-BALTIC", "contested",
        "A plural amber-coast adapter coordinates shore and woodland communities without converting Tacitus's AD 98 description into a centralized AD 1 constitution.",
    ),
    "antq_frisian_terp_community_order": (
        "global_tribes_estate_power=0.11|global_peasants_estate_power=0.10|"
        "tribes_estate_power_from_cabinet=0.21|estate_power_from_cabinet=0.16|"
        "replace_cabinet_member_cost_modifier=0.05",
        "P8.7;P11;P13;TAC-ANN-4.72;GRONINGEN-TERP;PALEOHISTORIA-FRISII", "contested",
        "Long-lived terp communities and early Roman contact support a distinct salt-marsh order without projecting the AD 28 revolt or later Frisian institutions backward.",
    ),
    "antq_dacian_divided_kingships": (
        "global_nobles_estate_power=0.13|global_tribes_estate_power=0.08|"
        "nobles_estate_power_from_cabinet=0.24|global_levy_size_modifier=0.025|"
        "replace_cabinet_member_cost_modifier=0.09",
        "P8.7;P11;P13;CAH-XI;PLE;STR-GEO-7.3.11", "contested",
        "Post-Burebista Dacia begins as divided regional powers, not one restored kingdom; selected hillfort, metal, route, and mounted interests structure the adapter.",
    ),
    "antq_garamantian_oasis_state": (
        "global_nobles_estate_power=0.10|global_burghers_estate_power=0.10|"
        "burghers_estate_power_from_cabinet=0.20|country_cabinet_efficiency=0.025|"
        "replace_cabinet_member_cost_modifier=0.07",
        "P8.5;P11;P13;CAH-XI;PLE;LEICESTER-TRANSSAHARA;BILNAS-GARAMANTES", "secure",
        "Archaeology securely supports an urbanized Garamantian oasis state, extensive irrigation, mobility, and long-distance exchange while its named AD 1 offices remain unknown.",
    ),
    "antq_marcomannic_bohemian_kingship": (
        "global_tribes_estate_power=0.12|global_nobles_estate_power=0.10|"
        "tribes_estate_power_from_cabinet=0.20|nobles_estate_power_from_cabinet=0.16|"
        "replace_cabinet_member_cost_modifier=0.09",
        "P8.7;P11;P13;CAH-XI;TAC-GER", "secure",
        "Maroboduus's organized kingdom rests on a royal retinue and negotiated allied kindreds without importing later Germanic institutions.",
    ),
    "antq_cheruscan_kindred_assembly": (
        "global_tribes_estate_power=0.12|global_nobles_estate_power=0.08|"
        "tribes_estate_power_from_cabinet=0.24|replace_cabinet_member_cost_modifier=0.06",
        "P8.7;P11;P13;CAH-XI;TAC-GER;YOUNG-GERMANIA", "contested",
        "Cheruscan authority is modeled through armed kindred deliberation and negotiated coalition leadership without inventing a fixed constitution for AD 1.",
    ),
    "antq_chattian_host_order": (
        "global_nobles_estate_power=0.11|global_tribes_estate_power=0.08|"
        "nobles_estate_power_from_cabinet=0.25|global_levy_size_modifier=0.025",
        "P8.7;P11;P13;CAH-XI;TAC-GER;YOUNG-GERMANIA", "contested",
        "Chattian political weight is attached to selected leaders, disciplined infantry, and prepared host service while later office structures remain excluded.",
    ),
    "antq_batavian_rhine_compact": (
        "global_nobles_estate_power=0.10|global_tribes_estate_power=0.06|"
        "nobles_estate_power_from_cabinet=0.22|country_cabinet_efficiency=0.025",
        "P8.1;P8.7;P11;P13;CAH-XI;TAC-GER;YOUNG-GERMANIA", "contested",
        "The Batavian compact joins island councils and concentrated auxiliary service to Rome without projecting the later revolt or a modern treaty constitution backward.",
    ),
    "antq_semnonian_sacred_confederacy": (
        "global_clergy_estate_power=0.12|global_tribes_estate_power=0.10|"
        "tribes_estate_power_from_cabinet=0.22|replace_cabinet_member_cost_modifier=0.08",
        "P8.7;P11;P13;CAH-XI;TAC-GER;YOUNG-GERMANIA", "contested",
        "Delegated gathering and sacred-grove custody frame Semnonian authority while Tacitus's later rhetoric and exact district count are treated cautiously.",
    ),
    "antq_sabaean_marib_kingship": (
        "global_peasants_estate_power=0.10|global_burghers_estate_power=0.08|"
        "estate_power_from_cabinet=0.23|replace_cabinet_member_cost_modifier=0.07",
        "P8.5;P8.6;P11;P13;CAH-XI;UNESCO-SABA;UNESCO-INCENSE", "contested",
        "An anonymous Sabaean court coordinates Ma'rib waterworks, sanctuaries, incense exchange, and highland lineages without inventing a named ruler or office hierarchy.",
    ),
    "antq_mauretanian_client_kingship": (
        "global_nobles_estate_power=0.08|global_burghers_estate_power=0.08|"
        "nobles_estate_power_from_cabinet=0.16|burghers_estate_power_from_cabinet=0.14|"
        "replace_cabinet_member_cost_modifier=0.06",
        "P8.1;P8.5;P11;P13;CAH-XI;OCD;OCD-PTO", "secure",
        "Juba II and Cleopatra Selene's client court balances regional houses, royal domains, cities, ports, and frontier service without becoming a uniform Roman administration.",
    ),
    "antq_herodian_judean_ethnarchy": (
        "global_clergy_estate_power=0.10|global_nobles_estate_power=0.08|"
        "clergy_estate_power_from_cabinet=0.20|replace_cabinet_member_cost_modifier=0.06",
        "P8.1;P11;P13;OCD;JOS-SAL", "secure",
        "Archelaus's ethnarchy balances Herodian dynastic authority, the Jerusalem temple establishment, toparchic assessment, pilgrimage, and Roman confirmation.",
    ),
    "antq_cappadocian_client_kingship": (
        "global_nobles_estate_power=0.10|global_burghers_estate_power=0.06|"
        "nobles_estate_power_from_cabinet=0.20|replace_cabinet_member_cost_modifier=0.07",
        "P8.1;P11;P13;OCD;PLE", "secure",
        "Archelaus's long client kingship negotiates royal domains, sanctuary property, highland routes, cavalry households, and Roman patronage.",
    ),
    "antq_odrysian_client_kingship": (
        "global_nobles_estate_power=0.11|global_tribes_estate_power=0.08|"
        "nobles_estate_power_from_cabinet=0.22|replace_cabinet_member_cost_modifier=0.09",
        "P8.1;P11;P13;OCD;TAC-THR;MGL-THR", "contested",
        "Rhoemetalces's Odrysian court balances dynastic claimants, mounted retainers, mountain communities, Aegean cities, and Roman intervention.",
    ),
    "antq_bosporan_client_kingship": (
        "global_burghers_estate_power=0.10|global_nobles_estate_power=0.08|"
        "burghers_estate_power_from_cabinet=0.20|replace_cabinet_member_cost_modifier=0.08",
        "P8.1;P11;P13;OCD;PLE;ZAV-ASP", "contested",
        "The deliberately contested Bosporan succession balances royal claimants, Greek poleis, grain ports, mounted households, and steppe-frontier compacts.",
    ),
    "antq_herodian_galilean_tetrarchy": (
        "global_burghers_estate_power=0.10|global_nobles_estate_power=0.07|"
        "burghers_estate_power_from_cabinet=0.18|replace_cabinet_member_cost_modifier=0.06",
        "P8.1;P11;P13;OCD;JOS-SAL", "secure",
        "Antipas's tetrarchy balances Herodian domains, fisheries, regional houses, ritual stores, markets, Peraean routes, and Roman confirmation.",
    ),
    "antq_herodian_batanean_tetrarchy": (
        "global_tribes_estate_power=0.10|global_nobles_estate_power=0.08|"
        "tribes_estate_power_from_cabinet=0.20|replace_cabinet_member_cost_modifier=0.07",
        "P8.1;P11;P13;OCD", "secure",
        "Philip's northern tetrarchy negotiates highland houses, sanctuaries, basalt settlements, cisterns, routes, horse service, and Roman patronage.",
    ),
    "antq_commagenean_client_kingship": (
        "global_nobles_estate_power=0.11|global_clergy_estate_power=0.07|"
        "nobles_estate_power_from_cabinet=0.20|replace_cabinet_member_cost_modifier=0.08",
        "P8.1;P11;P13;OCD;BM-COM", "secure",
        "Antiochus III's court balances dynastic houses, sanctuaries, Euphrates passage, highland cavalry, cultivation, and Roman-Arsacid diplomacy.",
    ),
    "antq_emesan_client_dynasty": (
        "global_clergy_estate_power=0.10|global_burghers_estate_power=0.08|"
        "clergy_estate_power_from_cabinet=0.18|replace_cabinet_member_cost_modifier=0.07",
        "P8.1;P11;P13;OCD;PLE;LBD-EME", "contested",
        "Iamblichus II's Sampsigeramid court balances dynastic houses, sanctuary custody, caravan and textile exchange, mounted service, and Roman patronage.",
    ),
    "antq_indian_ganasangha": (
        "global_peasants_estate_power=0.10|global_burghers_estate_power=0.05|"
        "estate_power_from_cabinet=0.20|replace_cabinet_member_cost_modifier=-0.10",
        "P8.4;P13;CAH-XI", "contested",
        "Rotating lineage delegates make offices accessible but politically embedded.",
    ),
    "antq_indo_scythian_kingship": (
        "global_tribes_estate_power=0.05|nobles_estate_power_from_cabinet=0.20|"
        "replace_cabinet_member_cost_modifier=0.10",
        "P8.4;P13;CAH-XI", "contested",
        "Mounted households and regional dynasts constrain appointments.",
    ),
    "antq_indo_greek_kingship": (
        "global_nobles_estate_power=0.05|burghers_estate_power_from_cabinet=0.20|"
        "set_cabinet_member_cost_modifier=-0.05",
        "P8.4;P13;CAH-XI;OCD", "contested",
        "Royal office works through established civic elites and magistracies.",
    ),
    "antq_northern_indian_coin_kingship": (
        "global_nobles_estate_power=0.08|global_burghers_estate_power=0.07|"
        "nobles_estate_power_from_cabinet=0.16|burghers_estate_power_from_cabinet=0.12|"
        "replace_cabinet_member_cost_modifier=0.05",
        "P8.4;P13;ASI-MITRA;IGNCA-PANCHALA", "contested",
        "Local coinages support differentiated courts and exchange interests without reconstructing one common post-Shunga constitution.",
    ),
    "antq_pundranagara_urban_kingship": (
        "global_nobles_estate_power=0.06|global_burghers_estate_power=0.10|"
        "burghers_estate_power_from_cabinet=0.18|country_cabinet_efficiency=0.025|"
        "replace_cabinet_member_cost_modifier=0.05",
        "P8.4;P13;UNESCO-MAHASTHAN;CAM-BANGLADESH", "contested",
        "Mahasthan's fortified urban horizon supports a court-and-town adapter, but not a recovered AD 1 dynasty or office list.",
    ),
    "antq_bengal_riverine_community_network": (
        "global_tribes_estate_power=0.07|global_burghers_estate_power=0.06|"
        "tribes_estate_power_from_cabinet=0.16|global_trade_through_owned_territory_efficiency=0.03|"
        "replace_cabinet_member_cost_modifier=0.04",
        "P8.4;P13;CAM-BANGLADESH", "contested",
        "Riverine early-historic zones coordinate households, landing places, cultivation, and exchange without backdating later Bengal kingdoms.",
    ),
    "antq_eastern_megalithic_community_network": (
        "global_tribes_estate_power=0.09|global_peasants_estate_power=0.07|"
        "tribes_estate_power_from_cabinet=0.18|global_production_efficiency=0.025|"
        "replace_cabinet_member_cost_modifier=0.04",
        "P8.4;P13;OUP-NEINDIA", "contested",
        "Megalithic and iron-working settlement evidence supports local coordination, not one Chota Nagpur ethnicity, state, or ruler.",
    ),
    "antq_eastern_hill_valley_network": (
        "global_tribes_estate_power=0.10|global_peasants_estate_power=0.05|"
        "tribes_estate_power_from_cabinet=0.20|global_monthly_food_modifier=0.02|"
        "replace_cabinet_member_cost_modifier=0.03",
        "P8.4;P13;ASI-AMBARI;OUP-NEINDIA", "contested",
        "Valley, foothill, and upland communities coordinate seasonal work, passage, and restitution without later kingdom or ethnic borders.",
    ),
    "antq_himalayan_highland_network": (
        "global_tribes_estate_power=0.11|global_peasants_estate_power=0.04|"
        "tribes_estate_power_from_cabinet=0.21|global_monthly_control=0.02|"
        "replace_cabinet_member_cost_modifier=0.03",
        "P8.4;P13;UCL-BHUTAN;OUP-NEINDIA", "contested",
        "Highland route and settlement evidence supports decentralized coordination without projecting later Bhutanese or Sikkimese institutions backward.",
    ),
    "antq_parthian_king_of_kings": (
        "global_tribes_estate_power=0.05|nobles_estate_power_from_cabinet=0.30|"
        "replace_cabinet_member_cost_modifier=0.15",
        "P8.2;P13;CAH-XI;OCD", "secure",
        "Great-house participation is powerful and costly to rearrange.",
    ),
    "antq_sassanid_centralized_monarchy": (
        "global_clergy_estate_power=0.10|crown_estate_power_from_cabinet=0.25|"
        "set_cabinet_member_cost_modifier=-0.10",
        "P8.2;P13;CAH-XI", "secure",
        "A stronger royal and religious administrative compact distinguishes the later monarchy.",
    ),
    "antq_client_monarchy": (
        "global_nobles_estate_power=0.05|estate_power_from_cabinet=0.10|"
        "replace_cabinet_member_cost_modifier=0.05",
        "P8.1;P13;OCD", "secure",
        "Local court houses retain leverage inside a patron-constrained monarchy.",
    ),
    "antq_parthian_subkingdom": (
        "global_tribes_estate_power=0.05|nobles_estate_power_from_cabinet=0.20|"
        "replace_cabinet_member_cost_modifier=0.10",
        "P8.2;P13;OCD", "contested",
        "Regional dynastic office remains negotiated with the great-house order.",
    ),
    "antq_arian_satrapal_court": (
        "global_nobles_estate_power=0.07|burghers_estate_power_from_cabinet=0.12|"
        "global_trade_through_owned_territory_efficiency=0.03|"
        "replace_cabinet_member_cost_modifier=0.07",
        "IRAN-ARIA;P8.2;P13", "contested",
        "Aria's old satrapal and urban frame is represented without inventing an independently attested AD 1 dynasty or fixed constitution.",
    ),
    "antq_kangju_confederated_kingship": (
        "global_tribes_estate_power=0.08|nobles_estate_power_from_cabinet=0.18|"
        "global_trade_through_owned_territory_efficiency=0.03|"
        "replace_cabinet_member_cost_modifier=0.08",
        "HAN-WR;IRAN-SOG-KANGJU;P8.3;P13", "contested",
        "The Kangju king coordinates constituent rulers, mounted households, pasture routes, and Sogdian towns rather than administering one unitary state.",
    ),
    "antq_sogdian_city_compact": (
        "global_burghers_estate_power=0.09|burghers_estate_power_from_cabinet=0.20|"
        "global_trade_through_owned_territory_efficiency=0.04|"
        "replace_cabinet_member_cost_modifier=0.05",
        "IRAN-SOG-KANGJU;HAN-WR;P8.2;P13", "contested",
        "Principal towns and landed houses coordinate exchange and defence beneath Kangju predominance without implying a unified Sogdian crown.",
    ),
    "antq_dayuan_oasis_kingship": (
        "global_burghers_estate_power=0.06|nobles_estate_power_from_cabinet=0.12|"
        "global_production_efficiency=0.025|replace_cabinet_member_cost_modifier=0.04",
        "HAN-WR;P8.3;P13", "contested",
        "The Ferghana court balances irrigated towns, horse-breeding households, route interests, and Han-facing diplomacy.",
    ),
    "antq_wusun_kunmi_confederacy": (
        "global_tribes_estate_power=0.09|nobles_estate_power_from_cabinet=0.16|"
        "land_morale_modifier=0.025|replace_cabinet_member_cost_modifier=0.07",
        "HAN-WR;HHS-WR;P8.3;P13", "secure",
        "The Kunmi's authority depends on mobile households, subordinate leaders, remount pastures, and negotiated relations with Han and Xiongnu.",
    ),
    "antq_yuezhi_five_yabghus": (
        "global_tribes_estate_power=0.07|nobles_estate_power_from_cabinet=0.18|"
        "land_morale_modifier=0.025|replace_cabinet_member_cost_modifier=0.08",
        "HAN-WR;UNESCO-CA-NOMADS;P8.3;P13", "contested",
        "The five yabghu framework represents a divided Yuezhi-Bactrian political field without fixing the disputed chronology of Kushan consolidation.",
    ),
    "antq_han_western_regions_kingship": (
        "global_burghers_estate_power=0.05|nobles_estate_power_from_cabinet=0.10|"
        "global_trade_through_owned_territory_efficiency=0.025|"
        "replace_cabinet_member_cost_modifier=0.04",
        "HAN-WR;HHS-WR;P8.3;P13", "contested",
        "A local oasis king and court operate within tributary and protectorate relationships; this is not a Han commandery or direct cultural annexation.",
    ),
    "antq_yancai_aorsi_confederacy": (
        "global_tribes_estate_power=0.10|tribes_estate_power_from_cabinet=0.22|"
        "land_morale_modifier=0.02|replace_cabinet_member_cost_modifier=0.05",
        "HAN-WR;UNESCO-CA-NOMADS;P8.3;P13", "contested",
        "A mobile lower-Ural confederational adapter uses the debated Yancai-Aorsi association without asserting exact borders or a recovered office system.",
    ),
    "antq_saryarka_late_iron_network": (
        "global_tribes_estate_power=0.11|global_peasants_estate_power=0.04|"
        "tribes_estate_power_from_cabinet=0.20|global_monthly_food_modifier=0.02|"
        "replace_cabinet_member_cost_modifier=0.02",
        "UNESCO-CA-NOMADS;P8.3;P13", "contested",
        "A material-horizon and route network represents central-steppe communities without manufacturing a single ethnicity, state, or ruler.",
    ),
    "antq_altai_contact_network": (
        "global_tribes_estate_power=0.11|tribes_estate_power_from_cabinet=0.21|"
        "global_trade_through_owned_territory_efficiency=0.02|"
        "replace_cabinet_member_cost_modifier=0.02",
        "UNESCO-CA-NOMADS;P8.3;P13", "contested",
        "Altai herding, exchange, and ritual communities are represented as a contact network rather than a falsely unitary ancient nation.",
    ),
    "antq_zhangzhung_plateau_kingship": (
        "global_nobles_estate_power=0.06|global_tribes_estate_power=0.05|"
        "nobles_estate_power_from_cabinet=0.14|global_monthly_food_modifier=0.015|"
        "replace_cabinet_member_cost_modifier=0.05",
        "OXF-SINO-TIB;CAM-TIB-ARCH;P13", "contested",
        "A bounded western-plateau court adapter models Zhang Zhung without inventing an AD 1 ruler list, fixed constitution, maximal borders, or organized later Bon.",
    ),
    "antq_sumpa_highland_confederacy": (
        "global_tribes_estate_power=0.11|tribes_estate_power_from_cabinet=0.21|"
        "global_monthly_food_modifier=0.02|global_trade_through_owned_territory_efficiency=0.015|"
        "replace_cabinet_member_cost_modifier=0.03",
        "OXF-SINO-TIB;CAM-TIB-ARCH;P13", "contested",
        "A northeastern highland-confederational adapter models Sumpa without projecting later imperial administration or a recovered uniform political order.",
    ),
    "antq_changtang_pastoral_network": (
        "global_tribes_estate_power=0.12|tribes_estate_power_from_cabinet=0.22|"
        "global_monthly_food_modifier=0.025|land_morale_modifier=0.015|"
        "replace_cabinet_member_cost_modifier=0.02",
        "ANT-TIB-HERDING;CAM-TIB-ARCH;P13", "contested",
        "High-pasture mobility, corrals, and seasonal coordination are represented without creating a unitary Changtang people or state.",
    ),
    "antq_central_plateau_agropastoral_network": (
        "global_tribes_estate_power=0.09|global_peasants_estate_power=0.06|"
        "tribes_estate_power_from_cabinet=0.18|global_production_efficiency=0.025|"
        "replace_cabinet_member_cost_modifier=0.025",
        "ANT-BANGGA;CAM-TIB-ARCH;P13", "contested",
        "Settled cultivation, herd management, and river-valley exchange are represented without backdating the Yarlung dynasty or a central Tibetan state.",
    ),
    "antq_eastern_plateau_corridor_network": (
        "global_tribes_estate_power=0.10|global_peasants_estate_power=0.04|"
        "tribes_estate_power_from_cabinet=0.20|global_trade_through_owned_territory_efficiency=0.025|"
        "replace_cabinet_member_cost_modifier=0.03",
        "CAM-EAST-TIB;RAD-YUSHU;OXF-EAST-RIM;P13", "contested",
        "Eastern river and escarpment corridors model unequal exchange and highland subsistence without treating mortuary forms as one ethnicity or state.",
    ),
    "antq_tamilakam_velir_court": (
        "global_nobles_estate_power=0.08|global_burghers_estate_power=0.05|"
        "nobles_estate_power_from_cabinet=0.16|global_trade_through_owned_territory_efficiency=0.02|"
        "replace_cabinet_member_cost_modifier=0.05",
        "CAM-TAMIL-MERCHANTS;UNESCO-KANCHI;JRAS-SATIYAPUTRA;P13", "contested",
        "A bounded Tamilakam chiefly court balances leading houses, cultivators, poets, and exchange while later Chola and Pallava institutions remain outside its frame.",
    ),
    "antq_central_indian_urban_kingship": (
        "global_nobles_estate_power=0.06|global_burghers_estate_power=0.08|"
        "burghers_estate_power_from_cabinet=0.16|global_production_efficiency=0.02|"
        "replace_cabinet_member_cost_modifier=0.04",
        "CAH-INDUS;JRAS-VEDISA;P13", "contested",
        "Post-Mauryan urban authority at Ujjayini and Vedisa is represented without inventing a shared dynasty, constitution, or uniform religious settlement.",
    ),
    "antq_central_indian_janapada": (
        "global_nobles_estate_power=0.07|global_peasants_estate_power=0.05|"
        "nobles_estate_power_from_cabinet=0.15|global_monthly_food_modifier=0.015|"
        "replace_cabinet_member_cost_modifier=0.04",
        "CAH-INDUS;P13", "contested",
        "The Chedi regional identity supports a bounded janapada adapter while its AD 1 ruler, capital, offices, and exact frontier remain unrecovered.",
    ),
    "antq_central_indian_megalithic_network": (
        "global_tribes_estate_power=0.10|global_peasants_estate_power=0.05|"
        "tribes_estate_power_from_cabinet=0.20|global_production_efficiency=0.02|"
        "replace_cabinet_member_cost_modifier=0.025",
        "CAM-CENTRAL-INDIA-MEGALITHS;INFLIB-EARLY-HISTORIC;P13", "contested",
        "Megalithic and Iron-Age landscapes support local coordination but do not establish one ethnicity, court, priesthood, or centralized state.",
    ),
    "antq_upper_mahanadi_kingship": (
        "global_nobles_estate_power=0.06|global_peasants_estate_power=0.07|"
        "estate_power_from_cabinet=0.15|global_monthly_food_modifier=0.02|"
        "replace_cabinet_member_cost_modifier=0.04",
        "INFLIB-DAKSHINA-KOSALA;INFLIB-EARLY-HISTORIC;P13", "contested",
        "A conservative Dakshina Kosala court adapter coordinates the upper Mahanadi without backdating later Sirpur dynasties, offices, or capital claims.",
    ),
    "antq_indian_ocean_atoll_network": (
        "global_tribes_estate_power=0.08|global_burghers_estate_power=0.06|"
        "tribes_estate_power_from_cabinet=0.16|global_trade_through_owned_territory_efficiency=0.03|"
        "replace_cabinet_member_cost_modifier=0.025",
        "CAM-MALDIVES;P13", "contested",
        "A decentralized atoll network models maritime exchange and local coordination without projecting the later sultanate, modern state, or uniform creed into AD 1.",
    ),
    "antq_mainland_river_corridor_network": (
        "global_tribes_estate_power=0.08|global_burghers_estate_power=0.05|"
        "tribes_estate_power_from_cabinet=0.17|global_trade_through_owned_territory_efficiency=0.025|"
        "replace_cabinet_member_cost_modifier=0.025",
        "CAM-MYANMAR-CHRON;CAM-ARAKAN-BOUNDARY;P13", "contested",
        "River and littoral communities coordinate landing places, passage, restitution, and exchange without one ethnic state or centralized port authority.",
    ),
    "antq_sa_huynh_exchange_network": (
        "global_tribes_estate_power=0.07|global_burghers_estate_power=0.06|"
        "tribes_estate_power_from_cabinet=0.16|global_trade_through_owned_territory_efficiency=0.03|"
        "replace_cabinet_member_cost_modifier=0.025",
        "CAM-SAH;VASS-SAH;P13", "contested",
        "Coastal production, burial communities, and maritime exchange are represented without backdating Champa or one Sa Huynh government.",
    ),
    "antq_mainland_highland_exchange_network": (
        "global_tribes_estate_power=0.10|global_peasants_estate_power=0.04|"
        "tribes_estate_power_from_cabinet=0.20|global_trade_through_owned_territory_efficiency=0.02|"
        "replace_cabinet_member_cost_modifier=0.025",
        "UNESCO-JARS;ANT-NLAOS;CAM-MYANMAR-CHRON;P13", "contested",
        "Highland households coordinate forest access, mortuary obligations, passes, and exchange without later ethnic or state boundaries.",
    ),
    "antq_mainland_iron_age_basin_network": (
        "global_tribes_estate_power=0.08|global_peasants_estate_power=0.07|"
        "tribes_estate_power_from_cabinet=0.17|global_monthly_food_modifier=0.02|"
        "replace_cabinet_member_cost_modifier=0.025",
        "CAM-SEA-IRON;P13", "contested",
        "Intermontane settlements coordinate rice cultivation, water, exchange, and defence without backdating Lanna, Shan, or Tai states.",
    ),
    "antq_amur_forest_river_network": (
        "global_tribes_estate_power=0.10|global_peasants_estate_power=0.04|"
        "tribes_estate_power_from_cabinet=0.20|global_trade_through_owned_territory_efficiency=0.02|"
        "replace_cabinet_member_cost_modifier=0.025",
        "NMJH-YIL;CAM-PROTOTUNGUSIC;RAD-RFE-IRON;P13", "contested",
        "Forest-river households coordinate fisheries, landing places, winter stores, and exchange without one state or recovered constitution.",
    ),
    "antq_sakhalin_maritime_network": (
        "global_tribes_estate_power=0.09|global_burghers_estate_power=0.04|"
        "tribes_estate_power_from_cabinet=0.18|global_trade_through_owned_territory_efficiency=0.025|"
        "replace_cabinet_member_cost_modifier=0.025",
        "RAD-SAKHALIN;P13", "contested",
        "Maritime communities coordinate shore access, fishing, sea-mammal use, and exchange without a later ethnic polity.",
    ),
    "antq_ussuri_poltsian_network": (
        "global_tribes_estate_power=0.08|global_peasants_estate_power=0.06|"
        "tribes_estate_power_from_cabinet=0.18|global_monthly_food_modifier=0.02|"
        "replace_cabinet_member_cost_modifier=0.025",
        "NMJH-YIL;CAM-PROTOTUNGUSIC;P13", "contested",
        "Pol'tse-facing river and basin communities coordinate cultivation, forest access, exchange, and defence without a fixed Yilou state.",
    ),
    "antq_northern_okjeo_corridor": (
        "global_tribes_estate_power=0.07|global_burghers_estate_power=0.05|"
        "tribes_estate_power_from_cabinet=0.16|global_trade_through_owned_territory_efficiency=0.025|"
        "replace_cabinet_member_cost_modifier=0.025",
        "NMJH-YIL;P13", "contested",
        "Tumen and southern Maritime communities coordinate passage and exchange without a later Korean court or fixed frontier.",
    ),
    "antq_borneo_cave_river_network": (
        "global_tribes_estate_power=0.10|global_peasants_estate_power=0.04|"
        "tribes_estate_power_from_cabinet=0.20|global_trade_through_owned_territory_efficiency=0.02|"
        "replace_cabinet_member_cost_modifier=0.025",
        "ANU-NIAH-METAL;QSR-LIANG-JON;P13", "contested",
        "Cave and river households coordinate burial places, forest access, landing places, and exchange without one island state.",
    ),
    "antq_borneo_coastal_exchange_network": (
        "global_tribes_estate_power=0.07|global_burghers_estate_power=0.06|"
        "tribes_estate_power_from_cabinet=0.16|global_trade_through_owned_territory_efficiency=0.03|"
        "replace_cabinet_member_cost_modifier=0.025",
        "ANU-NIAH-METAL;MYH-BUKIT-TENGKORAK;P13", "contested",
        "River mouths, pottery, and maritime exchange link coastal households without a centralized port or later kingdom.",
    ),
    "antq_borneo_interior_river_network": (
        "global_tribes_estate_power=0.10|global_peasants_estate_power=0.05|"
        "tribes_estate_power_from_cabinet=0.20|global_trade_through_owned_territory_efficiency=0.02|"
        "replace_cabinet_member_cost_modifier=0.025",
        "ANTH-KAL-IRON;QINT-LIANG-ABU;P13", "contested",
        "River communities coordinate portage, forest access, cultivation, and exchange without later ethnic borders.",
    ),
    "antq_borneo_foothill_iron_network": (
        "global_tribes_estate_power=0.08|global_peasants_estate_power=0.06|"
        "tribes_estate_power_from_cabinet=0.17|global_monthly_food_modifier=0.02|"
        "replace_cabinet_member_cost_modifier=0.025",
        "ANTH-KAL-IRON;P13", "contested",
        "Foothill households coordinate ore, charcoal, furnaces, river passage, and cultivation without a uniform guild or later state.",
    ),
    "antq_philippine_coastal_river_network": (
        "global_tribes_estate_power=0.08|global_peasants_estate_power=0.05|"
        "tribes_estate_power_from_cabinet=0.17|global_trade_through_owned_territory_efficiency=0.025|"
        "replace_cabinet_member_cost_modifier=0.025",
        "NMP-PH-METAL;NMP-PH-JARS;P13", "contested",
        "River, bay, and coastal households coordinate landing places, cultivation, passage, and exchange without one island kingdom.",
    ),
    "antq_philippine_mortuary_community_network": (
        "global_tribes_estate_power=0.08|global_clergy_estate_power=0.06|"
        "tribes_estate_power_from_cabinet=0.17|global_monthly_food_modifier=0.02|"
        "replace_cabinet_member_cost_modifier=0.025",
        "NMP-PH-JARS;NMP-KALANAY;CCP-MAITUM;P13", "contested",
        "Communities coordinate secondary burials, ancestral places, cultivation, and exchange without inventing a common priesthood or state.",
    ),
    "antq_philippine_island_exchange_network": (
        "global_tribes_estate_power=0.07|global_burghers_estate_power=0.06|"
        "tribes_estate_power_from_cabinet=0.15|global_trade_through_owned_territory_efficiency=0.03|"
        "replace_cabinet_member_cost_modifier=0.025",
        "NMP-KALANAY;BELLINA-SHK;P13", "contested",
        "Island households coordinate anchorages, pottery exchange, passage, and restitution without a centralized thalassocracy.",
    ),
    "antq_philippine_cave_coast_network": (
        "global_tribes_estate_power=0.09|global_peasants_estate_power=0.05|"
        "tribes_estate_power_from_cabinet=0.18|global_trade_through_owned_territory_efficiency=0.02|"
        "replace_cabinet_member_cost_modifier=0.025",
        "NMP-TABON;ATENEO-MINDORO;NMP-PH-JARS;P13", "contested",
        "Cave, rockshelter, and coastal households coordinate burial places, shore access, subsistence, and exchange without a later island polity.",
    ),
    "antq_sulawesi_coastal_exchange_network": (
        "global_tribes_estate_power=0.075|global_peasants_estate_power=0.045|"
        "tribes_estate_power_from_cabinet=0.165|global_trade_through_owned_territory_efficiency=0.028|"
        "replace_cabinet_member_cost_modifier=0.026",
        "ANU-SULAWESI;SPAFA-TOPOGARO;P13", "contested",
        "Coastal households coordinate landing places, cultivation, passage, and exchange without a later kingdom or common island government.",
    ),
    "antq_sulawesi_island_exchange_network": (
        "global_tribes_estate_power=0.065|global_burghers_estate_power=0.065|"
        "tribes_estate_power_from_cabinet=0.145|global_trade_through_owned_territory_efficiency=0.032|"
        "replace_cabinet_member_cost_modifier=0.026",
        "ANU-SULAWESI;P13", "contested",
        "Island households coordinate anchorages, short crossings, exchange, and restitution without a centralized thalassocracy.",
    ),
    "antq_sulawesi_highland_mortuary_network": (
        "global_tribes_estate_power=0.095|global_clergy_estate_power=0.065|"
        "tribes_estate_power_from_cabinet=0.185|global_monthly_food_modifier=0.022|"
        "replace_cabinet_member_cost_modifier=0.026",
        "UNESCO-LORE;SPAFA-TOPOGARO;P13", "contested",
        "Highland communities coordinate cultivation, ancestral places, jar burial, and valley passage without inventing a common priesthood.",
    ),
    "antq_sulawesi_river_lake_network": (
        "global_tribes_estate_power=0.085|global_peasants_estate_power=0.055|"
        "tribes_estate_power_from_cabinet=0.175|global_monthly_food_modifier=0.024|"
        "replace_cabinet_member_cost_modifier=0.026",
        "BRIN-KARAMA;ANU-SULAWESI;P13", "contested",
        "River and lake communities coordinate cultivation, portage, forest access, and exchange without projecting later iron kingdoms backward.",
    ),
    "antq_sulawesi_peninsula_community_network": (
        "global_tribes_estate_power=0.09|global_peasants_estate_power=0.04|"
        "tribes_estate_power_from_cabinet=0.16|global_trade_through_owned_territory_efficiency=0.024|"
        "replace_cabinet_member_cost_modifier=0.026",
        "ANU-SULAWESI;P13", "contested",
        "Peninsular households coordinate coast, gardens, inland paths, and exchange without a later ethnic federation or named ruler.",
    ),
    "antq_north_maluku_metal_age_network": (
        "global_tribes_estate_power=0.07|global_burghers_estate_power=0.07|"
        "tribes_estate_power_from_cabinet=0.15|global_trade_through_owned_territory_efficiency=0.035|"
        "replace_cabinet_member_cost_modifier=0.026",
        "ANU-MALUKU;P13", "contested",
        "Metal-Age island communities coordinate pottery, landing places, food, and exchange without backdating the Ternate or Tidore sultanates.",
    ),
    "antq_point_peninsula_seasonal_network": (
        "global_tribes_estate_power=0.083|global_peasants_estate_power=0.047|"
        "tribes_estate_power_from_cabinet=0.163|global_monthly_food_modifier=0.021|"
        "replace_cabinet_member_cost_modifier=0.027",
        "NYSM-POINT;OAS-POINT;NPS-HOPEWELL;P13", "contested",
        "Lake, river, and forest communities coordinate seasonal fishing, gathering, cultivation, burial places, and exchange without a later confederacy or recovered common constitution.",
    ),
    "antq_havana_hopewell_exchange_network": (
        "global_tribes_estate_power=0.071|global_clergy_estate_power=0.057|"
        "tribes_estate_power_from_cabinet=0.151|global_trade_through_owned_territory_efficiency=0.031|"
        "replace_cabinet_member_cost_modifier=0.028",
        "ISAS-HAVANA;ISM-DICKSON;ISAS-AMBOTTOM;NPS-HOPEWELL;P13", "contested",
        "Illinois-valley communities coordinate habitation, earthwork gatherings, mortuary obligations, craft exchange, and river passage without treating Hopewell as one people or state.",
    ),
    "antq_central_mississippi_woodland_network": (
        "global_tribes_estate_power=0.087|global_peasants_estate_power=0.053|"
        "tribes_estate_power_from_cabinet=0.177|global_monthly_food_modifier=0.023|"
        "replace_cabinet_member_cost_modifier=0.029",
        "NPS-OZARK-HOPEWELL;MOSHPO-CMO;P13", "contested",
        "River-valley and upland communities coordinate subsistence, mound obligations, local exchange, and passage without projecting the later Mississippian world or historic nations backward.",
    ),
    "antq_kansas_city_hopewell_network": (
        "global_tribes_estate_power=0.077|global_burghers_estate_power=0.063|"
        "tribes_estate_power_from_cabinet=0.157|global_trade_through_owned_territory_efficiency=0.029|"
        "replace_cabinet_member_cost_modifier=0.030",
        "MOSHPO-KC;NPS-OZARK-HOPEWELL;P13", "contested",
        "Lower-Missouri and eastern-Plains communities coordinate floodplain villages, tributary camps, resources, and exchange without treating an archaeological complex as a single polity.",
    ),
    "antq_mahan_small_state_league": (
        "global_tribes_estate_power=0.071|global_peasants_estate_power=0.059|"
        "tribes_estate_power_from_cabinet=0.159|global_monthly_food_modifier=0.024|"
        "replace_cabinet_member_cost_modifier=0.031",
        "NAJU-MAHAN;NMK-SAMHAN;AKS-LELANG;P13", "contested",
        "Mahan's many agricultural small states coordinate assemblies, river access, stores, ritual obligations, and diplomacy without one recovered AD 1 constitution.",
    ),
    "antq_jinhan_small_state_league": (
        "global_tribes_estate_power=0.073|global_burghers_estate_power=0.057|"
        "tribes_estate_power_from_cabinet=0.161|global_trade_through_owned_territory_efficiency=0.027|"
        "replace_cabinet_member_cost_modifier=0.032",
        "NMK-YEONGNAM;NMK-SAMHAN;P13", "contested",
        "Jinhan's Yeongnam small states coordinate cultivation, bronze-working, exchange, and collective defence without backdating the later Silla kingdom.",
    ),
    "antq_byeonhan_iron_exchange_league": (
        "global_tribes_estate_power=0.067|global_burghers_estate_power=0.073|"
        "tribes_estate_power_from_cabinet=0.153|global_trade_through_owned_territory_efficiency=0.035|"
        "replace_cabinet_member_cost_modifier=0.033",
        "JINJU-BYEONHAN;NMK-YEONGNAM;P13", "contested",
        "Byeonhan's western-Gyeongnam small states coordinate iron, ports, navigation, and exchange without backdating the later Gaya confederacies.",
    ),
    "antq_soanian_king_and_council": (
        "global_tribes_estate_power=0.083|global_nobles_estate_power=0.067|"
        "tribes_estate_power_from_cabinet=0.173|nobles_estate_power_from_cabinet=0.137|"
        "replace_cabinet_member_cost_modifier=0.031",
        "STR-CAUC;P13", "secure",
        "Strabo explicitly records a Soanian king and three-hundred-member council; modifiers preserve both royal and council leverage without treating his reported host size as a census.",
    ),
    "antq_andean_irrigated_valley_network": (
        "global_peasants_estate_power=0.077|global_clergy_estate_power=0.051|"
        "tribes_estate_power_from_cabinet=0.147|global_monthly_food_modifier=0.024|"
        "global_trade_through_owned_territory_efficiency=0.021",
        "CWP-ANDES;MET-ANDES-1500;P13", "contested",
        "Coastal and intermontane valley communities coordinate irrigation, stores, ritual obligations, and exchange without imposing one coast-wide state or recovered water constitution.",
    ),
    "antq_andean_highland_community_network": (
        "global_tribes_estate_power=0.081|global_peasants_estate_power=0.063|"
        "tribes_estate_power_from_cabinet=0.159|global_monthly_food_modifier=0.019|"
        "replace_cabinet_member_cost_modifier=0.023",
        "CWP-ANDES;ANT-HUARPA;P13", "contested",
        "Highland communities coordinate cultivation, pasture, passes, exchange, and collective ritual without backdating later ayllu constitutions or imperial administration.",
    ),
    "antq_andean_ceremonial_centre_network": (
        "global_clergy_estate_power=0.089|global_burghers_estate_power=0.057|"
        "clergy_estate_power_from_cabinet=0.181|global_production_efficiency=0.023|"
        "replace_cabinet_member_cost_modifier=0.029",
        "CWP-ANDES;CAM-NASCA-EIP;MET-ANDES-1500;P13", "contested",
        "First-order Andean ceremonial centres coordinate public works, specialist production, cultivation, and regional exchange without asserting one uniform territorial state.",
    ),
    "antq_wankarani_mound_village_network": (
        "global_tribes_estate_power=0.087|global_peasants_estate_power=0.069|"
        "tribes_estate_power_from_cabinet=0.171|global_monthly_food_modifier=0.017|"
        "global_trade_through_owned_territory_efficiency=0.019",
        "JFA-WANK;LAA-WANK;P13", "secure",
        "Central-Altiplano mound villages coordinate camelid herding, households, exchange, and ritual activity without inventing a Wankarani state or common ruler.",
    ),
    "antq_herrera_plateau_exchange_network": (
        "global_peasants_estate_power=0.073|global_burghers_estate_power=0.057|"
        "tribes_estate_power_from_cabinet=0.151|global_monthly_food_modifier=0.021|"
        "global_trade_through_owned_territory_efficiency=0.025",
        "QINT-HERRERA;P13", "contested",
        "Herrera-period plateau communities coordinate cultivation, salt and valley exchange, gathering obligations, and common works without backdating Muisca political institutions.",
    ),
    "antq_sierra_nevada_early_community_network": (
        "global_tribes_estate_power=0.083|global_peasants_estate_power=0.061|"
        "tribes_estate_power_from_cabinet=0.163|global_monthly_food_modifier=0.018|"
        "global_trade_through_owned_territory_efficiency=0.017",
        "CAM-SNSM;P13", "contested",
        "Sierra slope and coast communities coordinate subsistence, river passage, exchange, and local obligations before the dated Neguanje and Tairona built-settlement systems.",
    ),
    "antq_loja_regional_development_network": (
        "global_peasants_estate_power=0.071|global_tribes_estate_power=0.067|"
        "tribes_estate_power_from_cabinet=0.157|global_monthly_food_modifier=0.020|"
        "global_trade_through_owned_territory_efficiency=0.023",
        "GUFFROY-LOJA;OGBURN-LOJA;P13", "contested",
        "Loja and Catamayo valley communities coordinate cultivation, settlement, inter-valley passage, and exchange without backdating later ethnic polities.",
    ),
    "antq_daga_highland_garden_network": (
        "global_tribes_estate_power=0.085|global_peasants_estate_power=0.065|"
        "tribes_estate_power_from_cabinet=0.170|global_monthly_food_modifier=0.024|"
        "replace_cabinet_member_cost_modifier=0.026",
        "JPA-PAPUA;CAM-NGU;P13", "contested",
        "Highland-slope communities coordinate gardens, forest access, household obligations, and exchange without inventing one Daga constitution or fixed ethnic frontier.",
    ),
    "antq_bomberai_coastal_community_network": (
        "global_tribes_estate_power=0.070|global_burghers_estate_power=0.065|"
        "tribes_estate_power_from_cabinet=0.160|global_trade_through_owned_territory_efficiency=0.030|"
        "replace_cabinet_member_cost_modifier=0.025",
        "ANU-BOMBERAI;CAM-NGU;P13", "contested",
        "Bomberai coastal communities coordinate landing places, forest products, exchange, and restitution without backdating a later kingdom or maritime constitution.",
    ),
    "antq_early_mariana_island_network": (
        "global_tribes_estate_power=0.075|global_peasants_estate_power=0.055|"
        "tribes_estate_power_from_cabinet=0.160|global_trade_through_owned_territory_efficiency=0.026|"
        "global_monthly_food_modifier=0.020",
        "WA-MARIANA;ANU-MIC;P13", "contested",
        "Early Mariana communities coordinate island subsistence, passage, pottery, and gatherings without reconstructing a contact-era hierarchy or common state.",
    ),
    "antq_yap_ulithi_island_network": (
        "global_tribes_estate_power=0.080|global_burghers_estate_power=0.060|"
        "tribes_estate_power_from_cabinet=0.170|global_trade_through_owned_territory_efficiency=0.032|"
        "global_monthly_food_modifier=0.017",
        "ICA-YAP;ANU-MIC;P13", "contested",
        "Yap and Ulithi communities coordinate island passage, provisioning, exchange, and restitution without projecting the later sawei hierarchy into AD 1.",
    ),
    "antq_orinoco_llanos_ceramic_network": (
        "global_peasants_estate_power=0.075|global_tribes_estate_power=0.060|"
        "tribes_estate_power_from_cabinet=0.155|global_monthly_food_modifier=0.022|"
        "global_trade_through_owned_territory_efficiency=0.020",
        "JWP-ORINOCO;P13", "contested",
        "Orinoco-Llanos communities coordinate cultivation, ceramics, river passage, and exchange without equating material style with Arawak language or polity.",
    ),
    "antq_windward_island_ceramic_network": (
        "global_tribes_estate_power=0.070|global_peasants_estate_power=0.050|"
        "global_burghers_estate_power=0.055|global_trade_through_owned_territory_efficiency=0.030|"
        "global_monthly_food_modifier=0.019",
        "SCIADV-CARIB;P13", "contested",
        "Windward Island communities coordinate gardens, fishing, pottery, passage, and exchange without backdating a later Island Carib identity or common polity.",
    ),
    "antq_central_california_coastal_network": (
        "global_tribes_estate_power=0.080|global_peasants_estate_power=0.070|"
        "tribes_estate_power_from_cabinet=0.165|global_monthly_food_modifier=0.026|"
        "global_trade_through_owned_territory_efficiency=0.016",
        "NOAA-MONTEREY;P13", "contested",
        "Central-coast communities coordinate estuary, shore, woodland, gathering, and exchange obligations without imposing a contact-era ethnonym or language boundary.",
    ),
    "antq_acutuba_central_amazon_network": (
        "global_peasants_estate_power=0.080|global_tribes_estate_power=0.060|"
        "tribes_estate_power_from_cabinet=0.160|global_monthly_food_modifier=0.028|"
        "global_trade_through_owned_territory_efficiency=0.023",
        "SA-EXPANSIONS;ACUTUBA-CHRON;P13", "contested",
        "Acutuba-phase communities coordinate floodplain cultivation, ceramics, river passage, and exchange without inventing one territorial state or priesthood.",
    ),
    "antq_mesoamerican_urban_ritual_center": (
        "global_clergy_estate_power=0.10|global_burghers_estate_power=0.07|"
        "clergy_estate_power_from_cabinet=0.20|global_production_efficiency=0.025|"
        "replace_cabinet_member_cost_modifier=0.04",
        "INAH-IZAPA;INAH-CUICUILCO-TEO;INAH-TEO-START;P13", "contested",
        "A first-order ceremonial and exchange center coordinates public space, specialist production, cultivation, and regional ties without an invented recovered constitution.",
    ),
    "antq_mesoamerican_formative_civic_network": (
        "global_clergy_estate_power=0.07|global_peasants_estate_power=0.06|"
        "tribes_estate_power_from_cabinet=0.15|global_monthly_food_modifier=0.02|"
        "replace_cabinet_member_cost_modifier=0.01",
        "INAH-CANTONA;INAH-CHALCATZINGO;INAH-TAMTOC;P13", "contested",
        "Formative centers and cultivating communities coordinate water, stores, ritual places, exchange, and common works without a falsely uniform state.",
    ),
    "antq_mesoamerican_exchange_corridor_network": (
        "global_tribes_estate_power=0.08|global_burghers_estate_power=0.06|"
        "tribes_estate_power_from_cabinet=0.15|global_trade_through_owned_territory_efficiency=0.03|"
        "replace_cabinet_member_cost_modifier=0.02",
        "INAH-TAPAK;P8.10;P13", "contested",
        "Communities along coast, river, pass, and basin routes coordinate passage, exchange, restitution, and defence without later ethnic or imperial borders.",
    ),
    "antq_mesoamerican_highland_community_network": (
        "global_tribes_estate_power=0.10|global_peasants_estate_power=0.06|"
        "tribes_estate_power_from_cabinet=0.18|global_monthly_food_modifier=0.02|"
        "replace_cabinet_member_cost_modifier=0.01",
        "INAH-IZAPA;P8.10;P13", "contested",
        "Highland settlements coordinate cultivation, passes, exchange, ritual obligations, and collective defence without imposing a later ethnic polity.",
    ),
    "antq_west_mexican_shaft_tomb_chiefdom": (
        "global_clergy_estate_power=0.09|global_nobles_estate_power=0.06|"
        "clergy_estate_power_from_cabinet=0.18|global_production_efficiency=0.02|"
        "replace_cabinet_member_cost_modifier=0.03",
        "INAH-WEST-SHAFT;INAH-COLIMA;P13", "contested",
        "Ranked households coordinate mortuary places, specialist production, cultivation, and exchange without one western Mexican state.",
    ),
    "antq_teuchitlan_civic_center_network": (
        "global_clergy_estate_power=0.08|global_burghers_estate_power=0.07|"
        "estate_power_from_cabinet=0.18|global_trade_through_owned_territory_efficiency=0.025|"
        "replace_cabinet_member_cost_modifier=0.03",
        "INAH-TEUCHITLAN;P13", "contested",
        "Central Jalisco chiefly centers coordinate circular precincts, households, production, and exchange without a fixed territorial kingdom.",
    ),
    "antq_west_mexican_basin_community_network": (
        "global_tribes_estate_power=0.08|global_peasants_estate_power=0.07|"
        "tribes_estate_power_from_cabinet=0.15|global_monthly_food_modifier=0.02|"
        "replace_cabinet_member_cost_modifier=0.01",
        "INAH-CHUPICUARO;INAH-WEST-MEXICO;INAH-TOLUCA;P13", "contested",
        "Basin and highland communities coordinate cultivation, stores, mortuary obligations, and exchange without a later ethnic state.",
    ),
    "antq_west_mexican_highland_corridor_network": (
        "global_tribes_estate_power=0.09|global_burghers_estate_power=0.05|"
        "tribes_estate_power_from_cabinet=0.16|global_trade_through_owned_territory_efficiency=0.025|"
        "replace_cabinet_member_cost_modifier=0.02",
        "INAH-MEZCALA;INAH-WEST-SHAFT;P13", "contested",
        "Highland communities coordinate passes, exchange, restitution, ritual places, and defence without later frontier identities.",
    ),
    "antq_sonoran_desert_farming_network": (
        "global_tribes_estate_power=0.08|global_peasants_estate_power=0.08|"
        "tribes_estate_power_from_cabinet=0.14|global_monthly_food_modifier=0.025|"
        "replace_cabinet_member_cost_modifier=0.01",
        "NPS-SONORAN;P13", "contested",
        "Ancestral Sonoran households coordinate river and runoff farming, water access, exchange, and seasonal obligations before later mature systems.",
    ),
    "antq_buffer_kingdom": (
        "global_burghers_estate_power=0.05|estate_power_from_cabinet=0.10|"
        "replace_cabinet_member_cost_modifier=0.05",
        "P8.2;P13;OCD", "contested",
        "Court, route, and urban interests compete under frontier diplomatic pressure.",
    ),
    "antq_kushite_dual_kingship": (
        "global_clergy_estate_power=0.10|global_peasants_estate_power=0.05|"
        "clergy_estate_power_from_cabinet=0.20|set_cabinet_member_cost_modifier=-0.05",
        "P8.5;P13;CAH-XI", "secure",
        "Sacral legitimacy and cultivating communities structure royal appointments.",
    ),
    "antq_steppe_confederation": (
        "global_nobles_estate_power=0.10|tribes_estate_power_from_cabinet=0.30|"
        "replace_cabinet_member_cost_modifier=0.10",
        "P8.3;P13;CAH-XI", "secure",
        "Lineage leaders gain weight from office and resist rapid replacement.",
    ),
    "antq_xianbei_eastern_confederacy": (
        "global_tribes_estate_power=0.12|global_nobles_estate_power=0.06|"
        "tribes_estate_power_from_cabinet=0.24|replace_cabinet_member_cost_modifier=0.06",
        "P8.8;P9;P13;CAH-XI;XIANBEI-CONFEDERACY", "contested",
        "Separate eastern-steppe Xianbei groups bargain through leading households, mounted followings, pasture circuits, and seasonal gatherings before later unification.",
    ),
    "antq_early_korean_kingdom": (
        "global_crown_estate_power=0.10|nobles_estate_power_from_cabinet=0.15|"
        "set_cabinet_member_cost_modifier=-0.05",
        "P8.3;P13;SAM", "secure",
        "Royal consolidation coexists with leading regional houses.",
    ),
    "antq_regional_kingship": (
        "global_nobles_estate_power=0.05|estate_power_from_cabinet=0.10|"
        "replace_cabinet_member_cost_modifier=0.05",
        "P8;P13", "contested",
        "A conservative regional floor gives court elites limited appointment leverage.",
    ),
    "antq_advanced_chiefdom": (
        "global_clergy_estate_power=0.05|tribes_estate_power_from_cabinet=0.20|"
        "replace_cabinet_member_cost_modifier=-0.05",
        "P8.7;P13;CAH-XI", "contested",
        "Recognized kindreds and ritual custodians share a comparatively accessible council.",
    ),
    "antq_far_side_port_chiefdom": (
        "global_burghers_estate_power=0.08|global_tribes_estate_power=0.05|"
        "burghers_estate_power_from_cabinet=0.20|"
        "global_trade_through_owned_territory_efficiency=0.04|"
        "replace_cabinet_member_cost_modifier=0.02",
        "PME-BARBARIA;AJA-SOMALILAND;P8.5;P13", "contested",
        "A separate port chief mediates roadstead access, exchange households, mobile suppliers, and visiting merchants without ruling a unitary Barbaria.",
    ),
    "antq_horn_pastoral_network": (
        "global_tribes_estate_power=0.10|global_peasants_estate_power=0.05|"
        "tribes_estate_power_from_cabinet=0.20|"
        "global_trade_through_owned_territory_efficiency=0.025|"
        "replace_cabinet_member_cost_modifier=-0.02",
        "AJA-SOMALILAND;P8.5;P13", "contested",
        "Mobile and heterogeneous pastoral households coordinate routes, water, restitution, and exchange without a centralized state or fixed ethnic border.",
    ),
    "antq_west_african_savanna_compound_network": (
        "global_tribes_estate_power=0.08|global_peasants_estate_power=0.08|"
        "tribes_estate_power_from_cabinet=0.14|burghers_estate_power_from_cabinet=0.08|"
        "global_monthly_food_modifier=0.025|replace_cabinet_member_cost_modifier=-0.02",
        "JAH-HAUSALAND;JAR-WA-NETWORKS;P8.5;P13", "contested",
        "Dispersed savanna compounds coordinate cultivation, grazing, river access, and restitution without backdating later Hausa identities or states.",
    ),
    "antq_west_african_ironworking_network": (
        "global_tribes_estate_power=0.06|global_peasants_estate_power=0.06|"
        "tribes_estate_power_from_cabinet=0.10|burghers_estate_power_from_cabinet=0.10|"
        "global_production_efficiency=0.035|replace_cabinet_member_cost_modifier=-0.01",
        "HER-LEJJA;MET-IRON;JAR-WA-NETWORKS;P8.5;P13", "contested",
        "Ironworking, farming, and exchange households coordinate furnaces, fuel, food, and circulation without implying one ethnicity or centralized polity.",
    ),
    "antq_west_african_forest_network": (
        "global_tribes_estate_power=0.09|global_peasants_estate_power=0.05|"
        "tribes_estate_power_from_cabinet=0.14|clergy_estate_power_from_cabinet=0.08|"
        "global_monthly_food_modifier=0.02|replace_cabinet_member_cost_modifier=-0.03",
        "OUP-BENIN;JAH-GHANA;JAR-WA-NETWORKS;P8.5;P13", "contested",
        "Forest households coordinate land access, cultivation, ritual custody, and river exchange without backdating later dynasties, cities, or states.",
    ),
    "antq_early_ironworking_community_network": (
        "global_tribes_estate_power=0.07|global_peasants_estate_power=0.07|"
        "tribes_estate_power_from_cabinet=0.12|burghers_estate_power_from_cabinet=0.08|"
        "global_production_efficiency=0.025|replace_cabinet_member_cost_modifier=-0.02",
        "JAH-BANTU-MOBILITY;SCI-CONGO-RAINFOREST;QI-EAFRICA;P8.5;P13", "contested",
        "Dispersed farming, foraging, herding, potting, and ironworking communities coordinate exchange and local obligations without a centralized state or single ethnic identity.",
    ),
    "antq_mobile_hunter_herder_network": (
        "global_tribes_estate_power=0.12|global_peasants_estate_power=0.03|"
        "tribes_estate_power_from_cabinet=0.18|"
        "global_trade_through_owned_territory_efficiency=0.02|"
        "replace_cabinet_member_cost_modifier=-0.04",
        "OUP-SOUTH-AFRICA;JAH-BANTU-MOBILITY;P8.5;P13", "contested",
        "Mobile hunter-herder communities coordinate access, exchange, restitution, and seasonal movement without a uniform polity, language, or later territorial identity.",
    ),
    "antq_settled_town_cluster": (
        "global_peasants_estate_power=0.05|burghers_estate_power_from_cabinet=0.20|"
        "set_cabinet_member_cost_modifier=-0.10",
        "P8;P13;OCD", "contested",
        "Civic and exchange households dominate an inexpensive magistracy.",
    ),
    "antq_tribal_kingdom": (
        "global_nobles_estate_power=0.10|tribes_estate_power_from_cabinet=0.25|"
        "replace_cabinet_member_cost_modifier=0.05|court_spending_efficiency=0.35",
        "P8.7;P13;CAH-XI", "secure",
        "A leading house rules through powerful kindreds and office-bearing retainers.",
    ),
}

ALTERNATIVE_REFORM_OUTPUT = ROOT / "docs/m6/alternative_reform_paths.csv"
REFORM_VISIBILITY_OUTPUT = ROOT / "docs/m6/reform_visibility_matrix.csv"
ALTERNATIVE_REFORMS: tuple[tuple[str, str, str, str, str, str, str, str, str], ...] = (
    ("antq_augustan_dyarchy", "roman", "monarchy", "Augustan Dyarchy",
     "Balance the princeps' household administration with senatorial commissions and equestrian execution.",
     "global_crown_estate_power=0.10|global_nobles_estate_power=0.10|nobles_estate_power_from_cabinet=0.20|replace_cabinet_member_cost_modifier=0.10",
     "P8.1;P11;P13;OCD", "secure", "A gameplay path for the republic-facade settlement, not two legally equal sovereign powers."),
    ("antq_provincial_principate", "roman", "monarchy", "Provincial Principate",
     "Broaden provincial petitions, civic mediation, and equestrian administration within imperial rule.",
     "global_burghers_estate_power=0.10|global_peasants_estate_power=0.05|burghers_estate_power_from_cabinet=0.20|set_cabinet_member_cost_modifier=-0.05",
     "P8.1;P11;P13;OCD", "contested", "Abstracts greater provincial consultation without inventing representative government."),
    ("antq_memorialist_han_court", "han", "monarchy", "Memorialist Han Court",
     "Give formal memorials, remonstrance, and reviewed appointments greater weight at the imperial court.",
     "global_nobles_estate_power=0.10|global_burghers_estate_power=0.10|estate_power_from_cabinet=0.20|replace_cabinet_member_cost_modifier=0.05",
     "P8.3;P13;BHR;CTP-WM", "secure", "Models documented memorial practice without projecting later examination institutions."),
    ("antq_commandery_supervision", "han", "monarchy", "Commandery Supervision",
     "Strengthen audited commandery returns, rotating inspectors, and direct imperial appointment.",
     "global_crown_estate_power=0.20|global_peasants_estate_power=0.05|crown_estate_power_from_cabinet=0.30|set_cabinet_member_cost_modifier=-0.10",
     "P8.3;P13;BHR", "secure", "Represents stronger oversight while preserving local variation and court politics."),
    ("antq_iranian_great_house_reform", "iranian", "monarchy", "Great-House Compact",
     "Entrust mounted service and regional judgment to leading houses under negotiated royal precedence.",
     "global_nobles_estate_power=0.20|global_tribes_estate_power=0.10|nobles_estate_power_from_cabinet=0.35|replace_cabinet_member_cost_modifier=0.20",
     "P8.2;P13;CAH-XI;OCD", "secure", "A high-autonomy Arsacid path; exact constitutional procedure remains unrecoverable."),
    ("antq_iranian_royal_domain", "iranian", "monarchy", "Iranian Royal Domain",
     "Expand royal estates, sealed accounts, and court-appointed officers without erasing great houses.",
     "global_crown_estate_power=0.20|global_clergy_estate_power=0.05|crown_estate_power_from_cabinet=0.25|set_cabinet_member_cost_modifier=-0.05",
     "P8.2;P13;CAH-XI", "contested", "Combines attested royal-domain tendencies across a broad Iranian profile."),
    ("antq_boule_magistracy", "civic", "republic", "Boule and Magistracies",
     "Center civic administration on audited magistracies, council rotations, and public benefaction.",
     "global_burghers_estate_power=0.15|global_nobles_estate_power=0.05|burghers_estate_power_from_cabinet=0.25|set_cabinet_member_cost_modifier=-0.10",
     "P8.4;P13;OCD", "secure", "A civic constitutional path whose franchise remains locally variable."),
    ("antq_federal_synedrion", "civic", "republic", "Federal Synedrion",
     "Coordinate member communities through shared delegates, sanctuary diplomacy, and bounded contributions.",
     "global_peasants_estate_power=0.10|global_burghers_estate_power=0.10|estate_power_from_cabinet=0.25|replace_cabinet_member_cost_modifier=0.05",
     "P8.4;P13;CAH-XI;OCD", "contested", "Uses a conservative federal-council adapter rather than one universal league constitution."),
    ("antq_lineage_rotation", "gana", "republic", "Lineage Rotation",
     "Rotate recognized lineage delegates and offices to preserve collective legitimacy.",
     "global_nobles_estate_power=0.10|global_peasants_estate_power=0.10|estate_power_from_cabinet=0.25|replace_cabinet_member_cost_modifier=-0.15",
     "P8.4;P13;CAH-XI", "contested", "A gameplay abstraction for oligarchic collective office, not a fixed franchise."),
    ("antq_gana_muster_confederacy", "gana", "republic", "Muster Confederacy",
     "Bind assembly rights to witnessed military, road, and granary contributions.",
     "global_nobles_estate_power=0.15|global_burghers_estate_power=0.05|nobles_estate_power_from_cabinet=0.20|replace_cabinet_member_cost_modifier=0.05",
     "P8.4;P13;CAH-XI", "contested", "Connects collective defense to assembly bargaining without inventing a standing federation."),
    ("antq_steppe_wing_confederacy", "steppe", "steppe_horde", "Wing Confederacy",
     "Formalize left-right command, lineage musters, and negotiated pasture circuits.",
     "global_tribes_estate_power=0.20|global_nobles_estate_power=0.15|tribes_estate_power_from_cabinet=0.35|replace_cabinet_member_cost_modifier=0.15",
     "P8.3;P13;CAH-XI", "secure", "Avoids projecting later decimal ranks onto first-century confederations."),
    ("antq_steppe_gift_court", "steppe", "steppe_horde", "Prestige-Gift Court",
     "Concentrate envoys, tribute gifts, and brokered appointments around the ruling lineage.",
     "global_crown_estate_power=0.10|global_burghers_estate_power=0.05|estate_power_from_cabinet=0.20|set_cabinet_member_cost_modifier=-0.05",
     "P8.3;P13;CAH-XI", "contested", "Models gift circulation as political infrastructure, not a salaried bureaucracy."),
    ("antq_elder_moot_kingship", "tribal", "tribe", "Elder-Moot Kingship",
     "Require leading-kindred and ritual assent for musters, settlements, and succession bargains.",
     "global_tribes_estate_power=0.20|global_clergy_estate_power=0.10|tribes_estate_power_from_cabinet=0.25|replace_cabinet_member_cost_modifier=0.10",
     "P8.7;P13;CAH-XI", "contested", "A regional floor for varied assemblies, not a single Germanic or Celtic constitution."),
    ("antq_warband_retinue_kingship", "tribal", "tribe", "Warband-Retinue Kingship",
     "Shift authority toward gift-bound retainers and a ruler able to sustain repeated campaigns.",
     "global_nobles_estate_power=0.15|global_tribes_estate_power=0.10|nobles_estate_power_from_cabinet=0.30|replace_cabinet_member_cost_modifier=0.15",
     "P8.7;P13;CAH-XI", "secure", "Represents retinue consolidation without assuming later feudal vassalage."),
    ("antq_temple_endowment_court", "sacral", "monarchy", "Temple-Endowment Court",
     "Govern through protected cult endowments, scribal custody, and ritual provisioning.",
     "global_clergy_estate_power=0.20|global_crown_estate_power=0.05|clergy_estate_power_from_cabinet=0.30|replace_cabinet_member_cost_modifier=0.10",
     "P8.4;P8.5;P11;P13", "contested", "A cross-regional sacral path whose local temple and monastic forms remain distinct."),
    ("antq_irrigation_palace", "sacral", "monarchy", "Irrigation Palace",
     "Tie royal legitimacy to reservoirs, canal labor, granaries, and audited distributions.",
     "global_peasants_estate_power=0.15|global_crown_estate_power=0.10|crown_estate_power_from_cabinet=0.20|set_cabinet_member_cost_modifier=-0.10",
     "P8.4;P8.5;P13;CAH-XI", "contested", "A gameplay adapter for court-waterwork relationships, not universal hydraulic despotism."),
    ("antq_petition_court", "royal", "monarchy", "Petition Court",
     "Regularize witnessed petitions, sealed replies, and arbitration among court and urban houses.",
     "global_burghers_estate_power=0.10|global_nobles_estate_power=0.05|estate_power_from_cabinet=0.20|set_cabinet_member_cost_modifier=-0.05",
     "P8;P13;OCD", "contested", "A conservative royal-court path for regions lacking a narrower attested constitution."),
    ("antq_frontier_muster_monarchy", "royal", "monarchy", "Frontier-Muster Monarchy",
     "Organize royal authority around fortress stores, retainer service, and route protection.",
     "global_nobles_estate_power=0.15|global_tribes_estate_power=0.05|nobles_estate_power_from_cabinet=0.25|replace_cabinet_member_cost_modifier=0.10",
     "P8;P13;CAH-XI", "contested", "A bounded frontier adapter rather than a claim of one transregional military monarchy."),
    ("antq_xiongnu_dual_wing_command", "xiongnu", "steppe_horde", "Left and Right Wing Command",
     "Balance the chanyu's household with eastern and western command networks, lineage musters, and pasture arbitration.",
     "global_tribes_estate_power=0.20|global_nobles_estate_power=0.10|tribes_estate_power_from_cabinet=0.40|replace_cabinet_member_cost_modifier=0.15",
     "P8.3;P13;BHR;CAH-XI", "secure", "Models the securely reported wing structure without importing later decimal ranks or a fixed territorial bureaucracy."),
    ("antq_xiongnu_gift_circuit", "xiongnu", "steppe_horde", "Chanyu Gift Circuit",
     "Concentrate envoys, hostages, prestige gifts, and frontier exchange around the chanyu's itinerant court.",
     "global_crown_estate_power=0.15|global_burghers_estate_power=0.10|estate_power_from_cabinet=0.25|set_cabinet_member_cost_modifier=-0.05",
     "P8.3;P13;BHR;SAM", "contested", "Treats recorded gift and diplomatic exchange as political infrastructure, not a salaried central chancery."),
    ("antq_goguryeo_fortress_lineages", "goguryeo", "monarchy", "Fortress-Lineage Kingship",
     "Broker royal commands through fortress communities, leading lineages, beacon obligations, and witnessed musters.",
     "global_nobles_estate_power=0.15|global_tribes_estate_power=0.10|nobles_estate_power_from_cabinet=0.30|replace_cabinet_member_cost_modifier=0.10",
     "P8.3;P13;CAH-XI", "contested", "Represents an early fortress and lineage polity without projecting the mature Three Kingdoms office hierarchy backward."),
    ("antq_goguryeo_granary_court", "goguryeo", "monarchy", "Royal Granary Court",
     "Strengthen the royal household through millet stores, artisan obligations, route signals, and rotating fortress officers.",
     "global_crown_estate_power=0.15|global_peasants_estate_power=0.10|crown_estate_power_from_cabinet=0.30|set_cabinet_member_cost_modifier=-0.10",
     "P8.3;P13;CAH-XI", "contested", "A bounded centralizing path grounded in subsistence and fortified settlement rather than a recovered administrative code."),
    ("antq_kushite_dual_household", "kushite", "monarchy", "Dual Royal Household",
     "Coordinate royal households, sealed tribute, provincial brokers, and desert-route dispatches around Meroe.",
     "global_crown_estate_power=0.15|global_nobles_estate_power=0.10|estate_power_from_cabinet=0.30|replace_cabinet_member_cost_modifier=0.05",
     "P8.5;P11;P13;CAH-XI", "contested", "Uses the attested prominence of royal women and rulers without claiming two equal sovereign offices in every reign."),
    ("antq_kushite_temple_domain", "kushite", "monarchy", "Temple-Domain Stewardship",
     "Entrust cult storehouses, Nile contributions, metalwork returns, and provincial hospitality to protected stewards.",
     "global_clergy_estate_power=0.20|global_burghers_estate_power=0.05|clergy_estate_power_from_cabinet=0.30|set_cabinet_member_cost_modifier=-0.05",
     "P8.5;P11;P13;CAH-XI", "contested", "Combines attested cult and material contexts without inventing a uniform Meroitic temple bureaucracy."),
    ("antq_lankan_reservoir_kingship", "lankan", "monarchy", "Reservoir Stewardship Kingship",
     "Ground royal legitimacy in reservoir accounts, labor rotations, elephant service, and regional petition circuits.",
     "global_crown_estate_power=0.15|global_peasants_estate_power=0.15|crown_estate_power_from_cabinet=0.25|set_cabinet_member_cost_modifier=-0.10",
     "P8.4;P11;P13", "secure", "Models securely important irrigation patronage while avoiding the claim of one centralized hydraulic administration."),
    ("antq_lankan_sangha_endowments", "lankan", "monarchy", "Sangha Endowment Court",
     "Balance royal patronage, monastic endowments, port measures, and regional lineages through recorded grants.",
     "global_clergy_estate_power=0.20|global_burghers_estate_power=0.10|clergy_estate_power_from_cabinet=0.25|replace_cabinet_member_cost_modifier=0.05",
     "P8.4;P11;P13;BHR", "secure", "Represents early Buddhist patronage and donation practice without importing later monastic landholding arrangements wholesale."),
    ("antq_armenian_dynast_compact", "armenian", "monarchy", "Highland Dynast Compact",
     "Entrust fortress commands, mounted service, pass security, and arbitration to leading highland houses under royal precedence.",
     "global_nobles_estate_power=0.20|global_tribes_estate_power=0.05|nobles_estate_power_from_cabinet=0.35|replace_cabinet_member_cost_modifier=0.18",
     "P8.2;P11;P13;CAH-XI;IRAN-ARM", "contested", "Dynastic and fortress bargaining is evidence-bounded; no single written Artaxiad compact or fixed rank order is claimed."),
    ("antq_armenian_royal_domain_court", "armenian", "monarchy", "Artaxata Royal-Domain Court",
     "Strengthen royal domains, sealed accounts, pass couriers, and embassy coordination without erasing highland dynasts.",
     "global_crown_estate_power=0.18|global_burghers_estate_power=0.07|crown_estate_power_from_cabinet=0.28|set_cabinet_member_cost_modifier=-0.07",
     "P8.2;P11;P13;CAH-XI;IRAN-ARM", "contested", "A centralizing gameplay branch grounded in royal-domain and route functions, not a recovered Artaxiad chancery."),
    ("antq_nabataean_water_stewardship", "nabataean", "monarchy", "Cistern Stewardship Court",
     "Ground royal legitimacy in cisterns, channels, oasis labor, sanctuary stores, and predictable water compacts.",
     "global_peasants_estate_power=0.15|global_crown_estate_power=0.10|crown_estate_power_from_cabinet=0.22|set_cabinet_member_cost_modifier=-0.08",
     "P8.1;P8.5;P11;P13;OCD;PLE;NABATAEA-MAP", "secure", "Water management is securely important, while this branch avoids claiming one centralized kingdom-wide hydraulic administration."),
    ("antq_nabataean_customs_court", "nabataean", "monarchy", "Caravan Customs Court",
     "Empower caravan, merchant, and artisan houses through protected routes, stable measures, and reviewed customs schedules.",
     "global_burghers_estate_power=0.20|global_nobles_estate_power=0.05|burghers_estate_power_from_cabinet=0.32|replace_cabinet_member_cost_modifier=0.10",
     "P8.1;P8.5;P11;P13;OCD;PLE;NABATAEA-MAP", "secure", "The branch represents caravan and customs leverage without reducing the Nabataean kingdom to a modern commercial state."),
    ("antq_himyarite_irrigation_court", "himyarite", "monarchy", "Highland Irrigation Court",
     "Coordinate terrace walls, dams, water release, storage, and seasonal repair through protected cultivating communities.",
     "global_peasants_estate_power=0.18|global_crown_estate_power=0.10|crown_estate_power_from_cabinet=0.24|set_cabinet_member_cost_modifier=-0.08",
     "P8.5;P8.6;P11;P13;CAH-XI;OCD-HIM;HIMYAR-HIST", "contested", "A highland waterwork branch grounded in material context, not a claim for a uniform Himyarite hydraulic bureaucracy."),
    ("antq_himyarite_incense_route_court", "himyarite", "monarchy", "Incense-Route Court",
     "Center royal coordination on incense assessment, protected inland routes, Red Sea dispatches, and port measures.",
     "global_burghers_estate_power=0.18|global_nobles_estate_power=0.07|burghers_estate_power_from_cabinet=0.28|replace_cabinet_member_cost_modifier=0.08",
     "P8.5;P8.6;P11;P13;CAH-XI;OUP-REDSEA", "contested", "Incense and maritime exchange are securely relevant, while exact court offices and assessed shares remain unrecoverable."),
    ("antq_satavahana_guild_court", "satavahana", "monarchy", "Guild and Caravan Court",
     "Regularize guild gifts, caravan passage, inspected measures, water access, and royal hospitality across Deccan routes.",
     "global_burghers_estate_power=0.20|global_clergy_estate_power=0.05|burghers_estate_power_from_cabinet=0.30|set_cabinet_member_cost_modifier=-0.05",
     "P8.4;P11;P13;CAH-XI", "contested", "Uses attested exchange and donation contexts without projecting later guild constitutions uniformly into AD 1."),
    ("antq_satavahana_maharathi_compact", "satavahana", "monarchy", "Maharathi and Mahabhoja Compact",
     "Entrust regional service, elephant and mounted musters, route protection, and local arbitration to titled houses.",
     "global_nobles_estate_power=0.20|global_tribes_estate_power=0.06|nobles_estate_power_from_cabinet=0.34|replace_cabinet_member_cost_modifier=0.16",
     "P8.4;P11;P13;CAH-XI", "contested", "Attested titles support a regional-house branch, but their precise AD 1 competence and hierarchy are not reconstructed."),
    ("antq_catuvellaunian_dynastic_mint_court", "catuvellaunian", "tribe", "Dynastic Mint Court",
     "Center royal authority on witnessed weights, dies, prestige exchange, retinue gifts, and succession display at the oppida.",
     "global_burghers_estate_power=0.15|global_nobles_estate_power=0.10|burghers_estate_power_from_cabinet=0.28|set_cabinet_member_cost_modifier=-0.05",
     "P8.7;P11;P13;CAH-XI;BM-DRU", "contested", "Coinage and dynastic display are securely relevant, while the branch avoids inventing a centralized mint bureaucracy or monetary economy."),
    ("antq_catuvellaunian_oppida_compact", "catuvellaunian", "tribe", "Oppida Compact",
     "Coordinate stores, craft measures, sanctuary hearings, cultivating households, and Channel exchange among fortified settlement centers.",
     "global_peasants_estate_power=0.10|global_tribes_estate_power=0.08|estate_power_from_cabinet=0.25|replace_cabinet_member_cost_modifier=0.08",
     "P8.7;P11;P13;CAH-XI;BM-DRU", "contested", "Oppida provide a defensible settlement framework, not proof of an equal federation, fixed franchise, or uniform administration."),
    ("antq_marcomannic_retinue_court", "marcomannic", "tribe", "Maroboduus's Retinue Court",
     "Concentrate gifts, arms, intelligence, frontier envoys, and repeated campaign service around the royal following.",
     "global_nobles_estate_power=0.20|global_tribes_estate_power=0.08|nobles_estate_power_from_cabinet=0.35|replace_cabinet_member_cost_modifier=0.18",
     "P8.7;P11;P13;CAH-XI;TAC-GER", "secure", "The ruler's organized following is securely important; this path does not turn personal bonds into medieval vassalage or salaried office."),
    ("antq_marcomannic_allied_host_compact", "marcomannic", "tribe", "Allied Host Compact",
     "Distribute settlement, wagon, warrior, provisioning, and frontier-watch obligations among negotiated allied kindreds.",
     "global_tribes_estate_power=0.20|global_peasants_estate_power=0.06|tribes_estate_power_from_cabinet=0.32|replace_cabinet_member_cost_modifier=0.10",
     "P8.7;P11;P13;CAH-XI;TAC-GER", "contested", "The branch models negotiated host contributions without claiming a permanent federation, equal member peoples, or fixed territorial levies."),
    ("antq_sabaean_irrigation_court", "sabaean", "monarchy", "Ma'rib Irrigation Court",
     "Ground royal legitimacy in dam masonry, canal clearing, measured releases, cultivation, and bounded seasonal labor.",
     "global_peasants_estate_power=0.18|global_crown_estate_power=0.10|crown_estate_power_from_cabinet=0.24|set_cabinet_member_cost_modifier=-0.08",
     "P8.5;P8.6;P11;P13;CAH-XI;UNESCO-SABA", "secure", "The Ma'rib water system is secure, while the branch avoids hydraulic-despotism claims or a uniform kingdom-wide water bureaucracy."),
    ("antq_sabaean_sanctuary_route_court", "sabaean", "monarchy", "Sanctuary and Incense-Route Court",
     "Balance sanctuary inventories, incense assessments, caravan water, protected passage, and Red Sea forwarding.",
     "global_clergy_estate_power=0.14|global_burghers_estate_power=0.14|burghers_estate_power_from_cabinet=0.25|replace_cabinet_member_cost_modifier=0.06",
     "P8.5;P8.6;P11;P13;CAH-XI;UNESCO-INCENSE", "contested", "Sanctuary and incense-route contexts are securely important, while exact AD 1 court competences and assessed shares remain uncertain."),
    ("antq_mauretanian_urban_court", "mauretanian", "monarchy", "Caesarea Urban Court",
     "Strengthen civic petitions, port returns, inspected craft measures, dynastic diplomacy, and accountable royal workshops.",
     "global_burghers_estate_power=0.18|global_crown_estate_power=0.08|burghers_estate_power_from_cabinet=0.28|set_cabinet_member_cost_modifier=-0.06",
     "P8.1;P8.5;P11;P13;CAH-XI;OCD;OCD-PTO", "secure", "Juba's court and urban patronage support the branch without implying that every community shared a Roman civic constitution."),
    ("antq_mauretanian_frontier_compact", "mauretanian", "monarchy", "Mounted Frontier Compact",
     "Entrust mounted watch, guides, water access, regional musters, and border intelligence to negotiated frontier communities.",
     "global_tribes_estate_power=0.16|global_nobles_estate_power=0.10|nobles_estate_power_from_cabinet=0.28|replace_cabinet_member_cost_modifier=0.12",
     "P8.1;P8.5;P11;P13;CAH-XI", "contested", "Mounted frontier service is modeled conservatively without flattening diverse Mauretanian communities into a single tribal institution."),
    ("antq_judean_temple_court", "judean", "monarchy", "Jerusalem Temple Court",
     "Give temple stores, priestly hearings, pilgrimage order, and sanctuary provisioning a larger place in ethnarchic government.",
     "global_clergy_estate_power=0.18|global_burghers_estate_power=0.06|clergy_estate_power_from_cabinet=0.30|replace_cabinet_member_cost_modifier=0.10",
     "P8.1;P11;P13;OCD;JOS-SAL", "secure", "The Jerusalem temple establishment is securely central, while this branch does not treat priestly authority as a uniform civil bureaucracy."),
    ("antq_judean_toparchy_compact", "judean", "monarchy", "Judean Toparchy Compact",
     "Work through regional assessment districts, cultivating communities, cistern upkeep, market peace, and witnessed local petitions.",
     "global_peasants_estate_power=0.12|global_nobles_estate_power=0.08|estate_power_from_cabinet=0.25|set_cabinet_member_cost_modifier=-0.05",
     "P8.1;P11;P13;OCD;JOS-SAL", "contested", "Toparchic districts and local assessment are defensible, but their precise AD 1 competences and representative character remain uncertain."),
    ("antq_cappadocian_domain_court", "cappadocian", "monarchy", "Cappadocian Domain Court",
     "Concentrate sealed accounts, royal estates, sanctuary inventories, and appointed custodians around Archelaus's household.",
     "global_crown_estate_power=0.18|global_peasants_estate_power=0.08|crown_estate_power_from_cabinet=0.28|set_cabinet_member_cost_modifier=-0.07",
     "P8.1;P11;P13;OCD;PLE", "contested", "Royal-domain and sanctuary interests are historically grounded, while the exact reach of a centralized domain administration is not reconstructed."),
    ("antq_cappadocian_pass_compact", "cappadocian", "monarchy", "Cappadocian Pass Compact",
     "Entrust caravan passage, highland watch, cavalry musters, and market safe-conducts to negotiated regional houses and towns.",
     "global_burghers_estate_power=0.14|global_nobles_estate_power=0.10|burghers_estate_power_from_cabinet=0.25|replace_cabinet_member_cost_modifier=0.08",
     "P8.1;P11;P13;OCD;PLE", "contested", "Cappadocia's routes and mounted households support this branch without implying a recovered fixed council or uniform pass law."),
    ("antq_thracian_dynastic_court", "thracian", "monarchy", "Odrysian Dynastic Court",
     "Concentrate royal seals, succession hearings, retinue gifts, city diplomacy, and Roman embassies around the ruling house.",
     "global_nobles_estate_power=0.20|global_burghers_estate_power=0.05|nobles_estate_power_from_cabinet=0.34|replace_cabinet_member_cost_modifier=0.16",
     "P8.1;P11;P13;OCD;TAC-THR;MGL-THR", "contested", "Dynastic fragmentation and Roman intervention are secure contexts, but the precise AD 1 court hierarchy and Pythodoris's role remain contested."),
    ("antq_thracian_mountain_host", "thracian", "monarchy", "Thracian Mountain Host",
     "Distribute pass watch, horse service, timber and grain provisioning, sanctuary oaths, and frontier warning among regional communities.",
     "global_tribes_estate_power=0.18|global_peasants_estate_power=0.08|tribes_estate_power_from_cabinet=0.30|replace_cabinet_member_cost_modifier=0.10",
     "P8.1;P11;P13;OCD;TAC-THR;MGL-THR", "contested", "The branch models negotiated regional service without flattening Thracian peoples into a single tribe or inventing a permanent federal host."),
    ("antq_bosporan_polis_court", "bosporan", "monarchy", "Bosporan Polis Court",
     "Give grain measures, harbor petitions, sanctuary inventories, and civic mediation greater weight in royal government.",
     "global_burghers_estate_power=0.20|global_clergy_estate_power=0.05|burghers_estate_power_from_cabinet=0.30|set_cabinet_member_cost_modifier=-0.05",
     "P8.1;P11;P13;OCD;PLE;ZAV-ASP", "secure", "Greek poleis and grain ports securely structured Bosporan power, while their local constitutions and leverage varied."),
    ("antq_bosporan_steppe_compact", "bosporan", "monarchy", "Bosporan Steppe Compact",
     "Broker mounted service, pasture access, frontier intelligence, claimant support, and strait defense with regional households.",
     "global_tribes_estate_power=0.18|global_nobles_estate_power=0.10|tribes_estate_power_from_cabinet=0.30|replace_cabinet_member_cost_modifier=0.12",
     "P8.1;P11;P13;OCD;PLE;ZAV-ASP", "contested", "Mounted and steppe-frontier interests are defensible, but this path avoids inventing one ethnic bloc, fixed treaty, or recovered council."),
    ("antq_galilean_lake_court", "galilean", "monarchy", "Galilean Lake Court",
     "Center tetrarchic administration on fisheries, landing places, market measures, storage, and road peace around the lake settlements.",
     "global_burghers_estate_power=0.18|global_peasants_estate_power=0.08|burghers_estate_power_from_cabinet=0.30|set_cabinet_member_cost_modifier=-0.05",
     "P8.1;P11;P13;OCD;JOS-SAL", "contested", "Fisheries and market exchange are defensible functions, while one centralized lake administration or royal monopoly is not claimed."),
    ("antq_galilean_peraean_compact", "galilean", "monarchy", "Galilean-Peraean Compact",
     "Work through regional houses, pastoral communities, water access, road service, and witnessed local assessment across the divided tetrarchy.",
     "global_nobles_estate_power=0.14|global_tribes_estate_power=0.12|estate_power_from_cabinet=0.26|replace_cabinet_member_cost_modifier=0.08",
     "P8.1;P11;P13;OCD;JOS-SAL", "contested", "The geographical division and route obligations are secure contexts, but no representative compact or uniform Peraean institution is reconstructed."),
    ("antq_batanean_highland_court", "batanean", "monarchy", "Batanean Highland Court",
     "Concentrate sealed grants, basalt settlement works, cistern returns, sanctuary inventories, and appointed route custodians around Philip's household.",
     "global_crown_estate_power=0.16|global_clergy_estate_power=0.08|crown_estate_power_from_cabinet=0.26|set_cabinet_member_cost_modifier=-0.06",
     "P8.1;P11;P13;OCD", "contested", "Settlement, water, and sanctuary functions are grounded, while their concentration in a uniform tetrarchic administration remains a gameplay path."),
    ("antq_batanean_frontier_compact", "batanean", "monarchy", "Batanean Frontier Compact",
     "Entrust highland watch, guides, horse service, pasture and water access, and restitution to negotiated northern communities.",
     "global_tribes_estate_power=0.20|global_nobles_estate_power=0.08|tribes_estate_power_from_cabinet=0.32|replace_cabinet_member_cost_modifier=0.11",
     "P8.1;P11;P13;OCD", "contested", "The branch models highland and frontier service without inventing one Batanean ethnic bloc, fixed treaty, or permanent host."),
    ("antq_commagenean_sanctuary_court", "commagenean", "monarchy", "Commagenean Sanctuary Court",
     "Give sanctuary inventories, dynastic display, hospitality, orchard gifts, and ritual custody greater weight in royal government.",
     "global_clergy_estate_power=0.18|global_nobles_estate_power=0.10|clergy_estate_power_from_cabinet=0.30|replace_cabinet_member_cost_modifier=0.10",
     "P8.1;P11;P13;OCD;BM-COM", "secure", "Commagene's dynastic-sanctuary setting is secure, while this branch does not reconstruct a kingdom-wide priestly bureaucracy."),
    ("antq_commagenean_euphrates_compact", "commagenean", "monarchy", "Euphrates Passage Compact",
     "Entrust ferry safety, stable weights, caravan passage, landing stores, and compensation to negotiated river and merchant houses.",
     "global_burghers_estate_power=0.18|global_nobles_estate_power=0.08|burghers_estate_power_from_cabinet=0.28|set_cabinet_member_cost_modifier=-0.04",
     "P8.1;P11;P13;OCD;BM-COM", "contested", "Euphrates passage and exchange are secure contexts, but no complete Commagenean ferry code or merchant council is recovered."),
    ("antq_emesan_sanctuary_court", "emesan", "monarchy", "Emesan Sanctuary Court",
     "Center dynastic legitimacy on sanctuary stores, ritual hospitality, offerings, lamps, textiles, and protected custodianship.",
     "global_clergy_estate_power=0.20|global_crown_estate_power=0.06|clergy_estate_power_from_cabinet=0.32|replace_cabinet_member_cost_modifier=0.11",
     "P8.1;P11;P13;OCD;PLE;LBD-EME", "contested", "Emesa's sanctuary importance is defensible, while exact AD 1 priestly offices and their relationship to Iamblichus II remain unrecoverable."),
    ("antq_emesan_caravan_compact", "emesan", "monarchy", "Orontes Caravan Compact",
     "Entrust route security, pack service, textile measures, water, escorts, and compensation to caravan and city houses.",
     "global_burghers_estate_power=0.20|global_nobles_estate_power=0.07|burghers_estate_power_from_cabinet=0.30|set_cabinet_member_cost_modifier=-0.05",
     "P8.1;P11;P13;OCD;PLE;LBD-EME", "contested", "Caravan and urban exchange support the branch without implying a surviving uniform customs code or permanent merchant constitution."),
    ("antq_cheruscan_coalition_leadership", "cheruscan", "tribe", "Cheruscan Coalition Leadership",
     "Coordinate kindred delegates, frontier intelligence, compensation settlements, and seasonal musters under a recognized coalition leader.",
     "global_tribes_estate_power=0.16|global_nobles_estate_power=0.10|tribes_estate_power_from_cabinet=0.30|global_levy_size_modifier=0.025|replace_cabinet_member_cost_modifier=0.08",
     "P8.7;P11;P13;CAH-XI;TAC-GER;YOUNG-GERMANIA", "contested", "Coalition leadership fits the later Cheruscan political record, but no permanent AD 1 confederate office or uniform territorial federation is claimed."),
    ("antq_cheruscan_retinue_kingship", "cheruscan", "tribe", "Cheruscan Retinue Kingship",
     "Concentrate gifts, hostages, scouts, and repeated frontier service around a prestigious leader and his armed following.",
     "global_nobles_estate_power=0.18|global_tribes_estate_power=0.08|nobles_estate_power_from_cabinet=0.32|country_cabinet_efficiency=0.02|replace_cabinet_member_cost_modifier=0.14",
     "P8.7;P11;P13;CAH-XI;TAC-GER;YOUNG-GERMANIA", "contested", "Retinue consolidation is securely attested as a Germanic tendency, but this branch does not invent hereditary kingship or medieval vassalage."),
    ("antq_chattian_elder_war_council", "chattian", "tribe", "Chattian Elder War Council",
     "Let proven elders prepare campaigns, hear compensation disputes, and allocate tools, baggage, provisions, and forest routes.",
     "global_tribes_estate_power=0.13|global_nobles_estate_power=0.12|tribes_estate_power_from_cabinet=0.26|country_cabinet_efficiency=0.025|replace_cabinet_member_cost_modifier=0.07",
     "P8.7;P11;P13;CAH-XI;TAC-GER;YOUNG-GERMANIA", "contested", "The path translates Tacitus's emphasis on preparation and selected leadership into bounded gameplay, not a recovered Chattian senate."),
    ("antq_chattian_chosen_warrior_host", "chattian", "tribe", "Chattian Chosen-Warrior Host",
     "Elevate oath-bound front-rank warriors and disciplined infantry as the political core of a repeatedly mustered host.",
     "global_nobles_estate_power=0.18|global_tribes_estate_power=0.10|nobles_estate_power_from_cabinet=0.32|global_levy_size_modifier=0.045|replace_cabinet_member_cost_modifier=0.12",
     "P8.7;P11;P13;CAH-XI;TAC-GER", "secure", "Tacitus securely describes vowed and selected Chattian warriors, while his moralizing contrast and the institution's exact earlier form remain bounded."),
    ("antq_batavian_auxiliary_treaty", "batavian", "tribe", "Batavian Auxiliary Treaty",
     "Make concentrated cavalry, swimming river assault, Roman stipends, and elite hostages the basis of a negotiated allied service order.",
     "global_nobles_estate_power=0.16|global_crown_estate_power=0.06|nobles_estate_power_from_cabinet=0.30|global_levy_size_modifier=0.035|country_cabinet_efficiency=0.025",
     "P8.1;P8.7;P11;P13;CAH-XI;TAC-GER", "secure", "Batavian exemption from ordinary tribute in return for concentrated military service is secure, but treaty clauses and institutional continuity are not reconstructed."),
    ("antq_batavian_island_assembly", "batavian", "tribe", "Batavian Island Assembly",
     "Give island communities greater authority over floodbank labor, ferry passage, pasture returns, musters, and compensation hearings.",
     "global_tribes_estate_power=0.16|global_peasants_estate_power=0.08|tribes_estate_power_from_cabinet=0.28|global_monthly_control=0.0005|replace_cabinet_member_cost_modifier=0.06",
     "P8.7;P11;P13;CAH-XI;TAC-GER;YOUNG-GERMANIA", "contested", "The assembly is a conservative local adapter for a Rhine-island community and does not claim a surviving Batavian civic constitution."),
    ("antq_semnonian_grove_delegation", "semnonian", "tribe", "Semnonian Grove Delegation",
     "Bind affiliated districts through escorted delegates, witnessed oaths, ritual peace, compensation, and seasonal sacred gathering.",
     "global_clergy_estate_power=0.18|global_tribes_estate_power=0.12|clergy_estate_power_from_cabinet=0.28|stability_cost_efficiency=-0.03|replace_cabinet_member_cost_modifier=0.10",
     "P8.7;P11;P13;CAH-XI;TAC-GER", "secure", "Tacitus securely reports delegated sacred-grove gathering; its constitutional reach and exact AD 1 procedure remain unrecoverable."),
    ("antq_semnonian_district_muster", "semnonian", "tribe", "Semnonian District Muster",
     "Distribute seasonal host, provision, amber-route, and affiliate guarantees among recognized districts and kindreds.",
     "global_tribes_estate_power=0.18|global_nobles_estate_power=0.08|tribes_estate_power_from_cabinet=0.31|global_levy_size_modifier=0.03|replace_cabinet_member_cost_modifier=0.08",
     "P8.7;P11;P13;CAH-XI;TAC-GER", "contested", "The district branch uses Tacitus's confederate scale without literalizing his rhetorical hundred-canton claim or inventing fixed quotas."),
    ("antq_trinovantian_oppidum_court", "trinovantian", "tribe", "Trinovantian Oppidum Court",
     "Concentrate coin custody, stores, craft measures, petitions, and succession display around the principal oppidum court.",
     "global_crown_estate_power=0.10|global_nobles_estate_power=0.11|global_burghers_estate_power=0.09|country_cabinet_efficiency=0.03|set_cabinet_member_cost_modifier=-0.04",
     "P8.7;P11;P13;CAH-XI;CCI-DUB;BM-DRU", "contested", "The branch uses coin and oppidum evidence without inventing a centralized Trinovantian mint bureaucracy, fixed capital administration, or uniform urban polity."),
    ("antq_trinovantian_channel_compact", "trinovantian", "tribe", "Trinovantian Channel Compact",
     "Entrust landing security, weights, imported vessels, escorts, restitution, and gifts to protected exchange households.",
     "global_burghers_estate_power=0.18|global_nobles_estate_power=0.07|burghers_estate_power_from_cabinet=0.30|global_trade_through_owned_territory_efficiency=0.035|replace_cabinet_member_cost_modifier=0.07",
     "P8.7;P11;P13;CAH-XI;CCI-DUB;BM-DRU", "contested", "Cross-Channel exchange is securely relevant, but no surviving compact, customs schedule, or permanent merchant council is claimed."),
    ("antq_brigantian_kindred_compact", "brigantian", "tribe", "Brigantian Kindred Compact",
     "Bind participating northern communities through witnessed passage, pasture, compensation, refuge, gift, and muster agreements.",
     "global_tribes_estate_power=0.19|global_nobles_estate_power=0.07|tribes_estate_power_from_cabinet=0.31|replace_cabinet_member_cost_modifier=0.09|stability_cost_efficiency=-0.02",
     "P8.7;P11;P13;CAH-XI;PLE;PTO-GEO-II2", "contested", "The branch exposes confederate bargaining without asserting that the later Brigantian name denoted one permanent AD 1 federation or equal member peoples."),
    ("antq_brigantian_hillfort_court", "brigantian", "tribe", "Brigantian Hillfort Court",
     "Build a more concentrated northern court around selected stores, route intelligence, retinue gifts, hostages, and repeated musters.",
     "global_nobles_estate_power=0.17|global_tribes_estate_power=0.10|nobles_estate_power_from_cabinet=0.29|global_levy_size_modifier=0.03|replace_cabinet_member_cost_modifier=0.13",
     "P8.7;P11;P13;CAH-XI;BRIGANTIA-STANWICK", "contested", "Stanwick and later royal politics justify a possible concentration path, but neither is treated as proof of an AD 1 capital or Cartimanduan constitution."),
    ("antq_durotrigian_coin_weight_council", "durotrigian", "tribe", "Durotrigian Coin-Weight Council",
     "Give coin, pottery, metalworking, landing, and measured-exchange households greater authority over shared standards.",
     "global_burghers_estate_power=0.19|global_nobles_estate_power=0.06|burghers_estate_power_from_cabinet=0.31|global_production_efficiency=0.025|set_cabinet_member_cost_modifier=-0.04",
     "P8.7;P11;P13;CAH-XI;DUROTRIGES-PROJECT", "contested", "Distinctive material production supports the branch, but it does not claim a recovered coin council, central mint, or modern market economy."),
    ("antq_durotrigian_settlement_compact", "durotrigian", "tribe", "Durotrigian Settlement Compact",
     "Coordinate selected enclosures, rural stores, refuge, pottery, cattle, coastal watch, and compensation through local communities.",
     "global_tribes_estate_power=0.15|global_peasants_estate_power=0.11|tribes_estate_power_from_cabinet=0.27|global_monthly_control=0.0005|replace_cabinet_member_cost_modifier=0.06",
     "P8.7;P11;P13;CAH-XI;DUROTRIGES-PROJECT", "contested", "The path preserves distributed settlement evidence and explicitly avoids treating every hillfort as an occupied fortress or member of a formal league."),
    ("antq_ivernian_seaway_compact", "ivernian", "tribe", "Ivernian Seaway Compact",
     "Coordinate landing places, hide boats, escorts, beads, ceramics, iron, compensation, and hospitality along regional routes.",
     "global_burghers_estate_power=0.13|global_tribes_estate_power=0.12|estate_power_from_cabinet=0.25|global_trade_through_owned_territory_efficiency=0.03|replace_cabinet_member_cost_modifier=0.05",
     "P8.7;P11;P13;PTO-GEO-II1;DARCY-IRE;IRON-AGE-IRELAND", "contested", "The branch represents defensible exchange relationships without inventing a port bureaucracy, written compact, or dense settlement hierarchy."),
    ("antq_ivernian_cattle_gift_court", "ivernian", "tribe", "Ivernian Cattle-Gift Court",
     "Concentrate hospitality, cattle gifts, sureties, martial followings, ritual custody, and compensation around a prestigious household.",
     "global_nobles_estate_power=0.14|global_tribes_estate_power=0.13|nobles_estate_power_from_cabinet=0.25|global_levy_size_modifier=0.025|replace_cabinet_member_cost_modifier=0.10",
     "P8.7;P11;P13;PTO-GEO-II1;DARCY-IRE;IRON-AGE-IRELAND", "contested", "This is a playable concentration path, not a claim for an AD 1 Ivernian king, medieval Gaelic court, codified clientship, or island-wide political order."),
    ("antq_aestian_shore_exchange_compact", "aestian", "tribe", "Aestian Shore-Exchange Compact",
     "Entrust amber sorting, landing access, coastal passage, weights, escorts, and restitution to protected exchange households.",
     "global_burghers_estate_power=0.18|global_tribes_estate_power=0.10|burghers_estate_power_from_cabinet=0.30|global_trade_through_owned_territory_efficiency=0.035|replace_cabinet_member_cost_modifier=0.06",
     "P8.7;P11;P13;TAC-GER-45;ARCHAEOMETRY-NE-BALTIC", "secure", "Long-distance material connections and Baltic amber are secure, but no surviving customs compact, central market, or Aestian export monopoly is claimed."),
    ("antq_aestian_woodland_assembly", "aestian", "tribe", "Aestian Woodland Assembly",
     "Give shore and woodland communities greater authority over passage, refuge, watch, household contributions, compensation, and offering custody.",
     "global_tribes_estate_power=0.20|global_peasants_estate_power=0.08|tribes_estate_power_from_cabinet=0.32|stability_cost_efficiency=-0.02|replace_cabinet_member_cost_modifier=0.05",
     "P8.7;P11;P13;TAC-GER-45;ARCHAEOMETRY-NE-BALTIC", "contested", "The path preserves plural communities and local custody without treating Tacitus's later ethnographic summary as a recovered AD 1 assembly system."),
    ("antq_frisian_tidal_compact", "frisian", "tribe", "Frisian Tidal Compact",
     "Coordinate terp labor, changing channels, landing access, salt-marsh stores, guides, warning, and restitution through participating communities.",
     "global_tribes_estate_power=0.18|global_peasants_estate_power=0.11|tribes_estate_power_from_cabinet=0.29|global_monthly_control=0.0005|replace_cabinet_member_cost_modifier=0.05",
     "P8.7;P11;P13;GRONINGEN-TERP;PALEOHISTORIA-FRISII", "secure", "Terp settlement and adaptation to the salt-marsh landscape are secure; the compact is a gameplay abstraction rather than a recovered written league."),
    ("antq_frisian_frontier_council", "frisian", "tribe", "Frisian Frontier Council",
     "Concentrate negotiation of cattle, hides, service, landing rights, complaints, and resistance at the Roman Rhine frontier.",
     "global_nobles_estate_power=0.13|global_burghers_estate_power=0.10|nobles_estate_power_from_cabinet=0.23|country_cabinet_efficiency=0.025|replace_cabinet_member_cost_modifier=0.09",
     "P8.7;P11;P13;TAC-ANN-4.72;PALEOHISTORIA-FRISII", "contested", "The branch uses secure early Roman contact and the later tribute crisis without pre-scripting the AD 28 revolt or inventing permanent subjection."),
    ("antq_dacian_hillfort_compact", "dacian", "tribe", "Dacian Hillfort Compact",
     "Bind divided regional rulers through selected stores, metal contributions, pass warning, mounted service, external oaths, and mutual refuge.",
     "global_tribes_estate_power=0.14|global_nobles_estate_power=0.13|estate_power_from_cabinet=0.28|global_levy_size_modifier=0.025|replace_cabinet_member_cost_modifier=0.08",
     "P8.7;P11;P13;CAH-XI;PLE;STR-GEO-7.3.11", "contested", "Strabo securely reports political division after Burebista; the compact provides cooperation without reuniting Dacia under an invented AD 1 monarch."),
    ("antq_dacian_mountain_court", "dacian", "tribe", "Dacian Mountain Court",
     "Concentrate metal accounts, hillfort stores, mounted command, sanctuary oaths, and Carpathian passage around one ascendant regional house.",
     "global_nobles_estate_power=0.19|global_burghers_estate_power=0.09|nobles_estate_power_from_cabinet=0.31|global_levy_size_modifier=0.035|replace_cabinet_member_cost_modifier=0.13",
     "P8.7;P11;P13;CAH-XI;PLE;STR-GEO-7.3.11", "contested", "A concentration path is plausible within divided Dacia, but it is not Decebalus's later kingdom and does not assert one permanent capital or priestly monarchy."),
    ("antq_garamantian_irrigation_court", "garamantian", "monarchy", "Garamantian Irrigation Court",
     "Concentrate shaft clearing, underground-gallery repair, water rotation, oasis stores, field gates, and household petitions around the leading court.",
     "global_crown_estate_power=0.12|global_peasants_estate_power=0.15|estate_power_from_cabinet=0.28|global_production_efficiency=0.03|set_cabinet_member_cost_modifier=-0.04",
     "P8.5;P11;P13;LEICESTER-TRANSSAHARA", "secure", "Large irrigation systems and oasis agriculture are secure; the branch does not invent named water offices, a codified schedule, or unrestricted royal ownership."),
    ("antq_garamantian_caravan_compact", "garamantian", "monarchy", "Garamantian Caravan Compact",
     "Give caravan, craft, and outer-oasis interests greater authority over protected water, routes, measures, materials, guides, and restitution.",
     "global_burghers_estate_power=0.19|global_tribes_estate_power=0.09|burghers_estate_power_from_cabinet=0.31|global_trade_through_owned_territory_efficiency=0.04|replace_cabinet_member_cost_modifier=0.08",
     "P8.5;P11;P13;LEICESTER-TRANSSAHARA;BILNAS-GARAMANTES", "secure", "Saharan mobility and long-distance exchange are archaeologically secure, but no surviving caravan constitution or court monopoly is reconstructed."),
)

SUCCESSOR_REFORMS: tuple[
    tuple[str, str, str, str, str, str, str, str, str, str], ...
] = (
    (
        "antq_flavian_imperial_settlement", "roman", "monarchy",
        "Flavian Imperial Settlement",
        "Rebuild imperial credit, army discipline, public works, and senatorial cooperation after a contested succession and civil war.",
        "global_crown_estate_power=0.12|global_nobles_estate_power=0.08|estate_power_from_cabinet=0.22|replace_cabinet_member_cost_modifier=0.08",
        "P8.1;P9;P13;P15;CAH-XI;OCD", "secure",
        "The AD 69-79 reconstruction is secure; the path models a durable political settlement rather than a single formal Flavian constitution.",
        "0",
    ),
    (
        "antq_antonine_provincial_principate", "roman", "monarchy",
        "Antonine Provincial Principate",
        "Integrate provincial aristocracies, juristic petition, civic benefaction, and frontier command into a mature imperial court.",
        "global_nobles_estate_power=0.10|global_burghers_estate_power=0.10|nobles_estate_power_from_cabinet=0.18|burghers_estate_power_from_cabinet=0.16|set_cabinet_member_cost_modifier=-0.04",
        "P8.1;P9;P13;P15;CAH-XI;OCD", "secure",
        "Provincial elite integration and expanded imperial adjudication are secure trends; one fixed Antonine constitution is not asserted.",
        "1",
    ),
    (
        "antq_severan_military_principate", "roman", "monarchy",
        "Severan Military Principate",
        "Concentrate succession, donatives, juristic administration, and frontier command around a court sustained by the professional armies.",
        "global_crown_estate_power=0.16|global_nobles_estate_power=0.06|crown_estate_power_from_cabinet=0.28|replace_cabinet_member_cost_modifier=0.14",
        "P8.1;P9;P13;P15;CAH-XII;OCD", "secure",
        "The Severan military and juristic court is secure; the gameplay path does not reduce all civilian government to army patronage.",
        "2",
    ),
    (
        "antq_tetrarchic_collegium", "late_roman", "monarchy",
        "Tetrarchic Collegium",
        "Distribute imperial presence, field command, taxation, and regional supervision among a formally ranked college of rulers.",
        "global_crown_estate_power=0.18|estate_power_from_cabinet=0.20|crown_estate_power_from_cabinet=0.30|set_cabinet_member_cost_modifier=-0.08",
        "P8.1;P9;P13;P15;CAH-XII;OCD;ND", "secure",
        "Diocletian's collegiate rule is secure, while its exact succession logic remains a political project rather than a stable written constitution.",
        "3",
    ),
    (
        "antq_constantinian_consistory", "late_roman", "monarchy",
        "Constantinian Consistory",
        "Center rescripts, palace offices, imperial religion, mobile armies, and prefectural government on the victorious dynastic court.",
        "global_crown_estate_power=0.20|global_clergy_estate_power=0.10|crown_estate_power_from_cabinet=0.34|set_cabinet_member_cost_modifier=-0.12",
        "P8.1;P9;P11;P13;P15;CAH-XII;OCD;ND", "secure",
        "The Constantinian palace and religious settlement is secure; later fourth-century elaboration is not projected unchanged onto AD 324.",
        "3",
    ),
    (
        "antq_late_imperial_twin_courts", "late_roman", "monarchy",
        "Late Imperial Twin Courts",
        "Coordinate western and eastern courts, military masters, prefectures, federate settlements, and dynastic legitimacy across a divided empire.",
        "global_crown_estate_power=0.14|global_nobles_estate_power=0.10|global_clergy_estate_power=0.08|estate_power_from_cabinet=0.26|replace_cabinet_member_cost_modifier=0.10",
        "P8.1;P9;P11;P13;P15;CAH-XII;OCD;ND", "contested",
        "Separate eastern and western courts are secure after AD 395; the shared path abstracts coordination and rivalry without claiming legal partition.",
        "4",
    ),
    (
        "antq_xin_state_reorganization", "han", "monarchy",
        "Xin State Reorganization",
        "Attempt a dynastic and fiscal refoundation through renamed offices, revised ranks, currency experiments, land claims, and more directive central policy.",
        "global_crown_estate_power=0.18|global_nobles_estate_power=-0.04|crown_estate_power_from_cabinet=0.28|replace_cabinet_member_cost_modifier=0.12",
        "P8.3;P9;P13;BHR;CTP-WM;CAH-X", "secure",
        "Wang Mang's AD 9 usurpation and extensive reform programme are secure; the path abstracts contested implementation and does not present Xin policy as successful or internally uniform.",
        "0",
    ),
    (
        "antq_guangwu_restoration_court", "late_han", "monarchy",
        "Guangwu Restoration Court",
        "Rebuild imperial authority from Luoyang through selective restoration, military demobilization, commandery appointments, tax restraint, and negotiated elite support.",
        "global_crown_estate_power=0.14|global_nobles_estate_power=0.08|estate_power_from_cabinet=0.20|set_cabinet_member_cost_modifier=-0.06",
        "P8.3;P9;P13;BHR;CAH-X", "secure",
        "The Eastern Han restoration from AD 25 is secure; this reform models its political settlement rather than treating every Guangwu measure as permanent.",
        "0",
    ),
    (
        "antq_eastern_han_secretariat", "late_han", "monarchy",
        "Eastern Han Imperial Secretariat",
        "Coordinate memorials, edicts, appointments, and provincial reports through the palace Secretariat while retaining the formal Three Excellencies and Nine Ministers.",
        "global_crown_estate_power=0.16|global_nobles_estate_power=0.06|crown_estate_power_from_cabinet=0.30|set_cabinet_member_cost_modifier=-0.08",
        "P8.3;P9;P13;BHR;CAH-X", "secure",
        "The Secretariat's growing executive importance is secure, but exact competence and its balance with formal high offices changed across Eastern Han.",
        "1",
    ),
    (
        "antq_affinal_regency_court", "late_han", "monarchy",
        "Affinal Regency Court",
        "Govern for a minor emperor through a dowager court, empress kin, senior generals, formal ministers, memorial channels, and contested palace access.",
        "global_nobles_estate_power=0.15|global_crown_estate_power=0.08|nobles_estate_power_from_cabinet=0.28|replace_cabinet_member_cost_modifier=0.14",
        "P8.3;P9;P13;BHR;CAH-X", "secure",
        "Repeated Eastern Han minority regencies and affinal-general dominance are secure; no single factional cycle is treated as constitutionally inevitable.",
        "1",
    ),
    (
        "antq_provincial_inspectorate_commands", "late_han", "monarchy",
        "Provincial Inspectorate Commands",
        "Entrust broader fiscal, judicial, supply, and military coordination to regional inspectors and governors during sustained internal or frontier emergency.",
        "global_nobles_estate_power=0.14|global_tribes_estate_power=0.05|nobles_estate_power_from_cabinet=0.24|global_monthly_control=-0.0005|replace_cabinet_member_cost_modifier=0.12",
        "P8.3;P9;P13;BHR;CAH-XII", "secure",
        "Late Han provincial commands and their role in fragmentation are secure; this path does not project permanent independent warlord states onto earlier inspector circuits.",
        "2",
    ),
    (
        "antq_three_kingdoms_chancellery", "late_han", "monarchy",
        "Three Kingdoms Chancellery",
        "Concentrate mobilization, appointments, registers, granaries, diplomatic claims, and restoration ideology in a wartime imperial chancellery.",
        "global_crown_estate_power=0.12|global_nobles_estate_power=0.12|estate_power_from_cabinet=0.26|replace_cabinet_member_cost_modifier=0.10",
        "P8.3;P9;P13;CAH-XII", "secure",
        "Competing imperial chancellery states after 220 are secure; the singular gameplay path does not erase the distinct institutions of Wei, Shu, and Wu.",
        "2",
    ),
    (
        "antq_jin_reunification_court", "late_han", "monarchy",
        "Jin Reunification Court",
        "Reconcile a reunified imperial court, titled houses, command appointments, land and household registers, legal compilation, and provincial defense.",
        "global_crown_estate_power=0.13|global_nobles_estate_power=0.13|nobles_estate_power_from_cabinet=0.22|set_cabinet_member_cost_modifier=-0.04",
        "P8.3;P9;P13;CAH-XII", "secure",
        "Western Jin reunification in 280 is secure; the reform is a bounded successor path and does not imply lasting stability or project later northern and southern institutions backward.",
        "3",
    ),
    (
        "antq_vologasid_dynastic_settlement", "iranian", "monarchy",
        "Vologasid Dynastic Settlement",
        "Stabilize Arsacid rule through dynastic recognition, great-house bargaining, subking obligations, royal foundations, and renewed command of the Iranian and Mesopotamian routes.",
        "global_crown_estate_power=0.10|global_nobles_estate_power=0.10|estate_power_from_cabinet=0.20|country_cabinet_efficiency=0.025|replace_cabinet_member_cost_modifier=-0.03",
        "P8.2;P9;P13;CAH-XI;IRAN-ARSACID", "secure",
        "Vologases I's accession in AD 51 and long consolidation are secure; the path abstracts a durable settlement without inventing a single promulgated constitution.",
        "0",
    ),
    (
        "antq_arsacid_dual_court_compact", "iranian", "monarchy",
        "Arsacid Regional-Court Compact",
        "Coordinate seasonal and regional courts, subkings, great-house retinues, caravan routes, and Mesopotamian-Iranian revenue without forcing them into uniform provinces.",
        "global_crown_estate_power=0.08|global_nobles_estate_power=0.13|global_burghers_estate_power=0.06|nobles_estate_power_from_cabinet=0.22|set_cabinet_member_cost_modifier=-0.04",
        "P8.2;P9;P13;CAH-XI;IRAN-ADMIN;IRAN-ARSACID", "contested",
        "Multiple royal centers and regional bargaining are secure features; the compact is a gameplay path and not a claim for a formal two-capital constitution.",
        "1",
    ),
    (
        "antq_late_arsacid_house_mobilization", "iranian", "monarchy",
        "Late Arsacid House Mobilization",
        "Meet intensified Roman war and dynastic rivalry through larger great-house hosts, fortified corridors, emergency tribute, hostage guarantees, and contested royal leadership.",
        "global_nobles_estate_power=0.16|global_crown_estate_power=0.06|global_levy_size_modifier=0.06|nobles_estate_power_from_cabinet=0.28|replace_cabinet_member_cost_modifier=0.12",
        "P8.2;P9;P13;CAH-XII;IRAN-ARSACID", "secure",
        "Late Arsacid dynastic conflict, Roman pressure, and dependence on regional military power are secure; the reform does not make collapse inevitable.",
        "2",
    ),
    (
        "antq_ardashir_unification_court", "sasanian", "monarchy",
        "Ardashir's Unification Court",
        "Replace Arsacid dynastic predominance through direct royal conquest, palace command, provincial submission, dynastic foundations, and a new Sasanian language of kingship.",
        "global_crown_estate_power=0.20|global_nobles_estate_power=-0.03|crown_estate_power_from_cabinet=0.32|global_monthly_control=0.001|replace_cabinet_member_cost_modifier=0.10",
        "P8.2;P9;P13;CAH-XII;IRAN-ADMIN", "secure",
        "Ardashir I's victory in AD 224 and Sasanian refoundation are secure; the path does not imply instant administrative uniformity across the conquered realm.",
        "2",
    ),
    (
        "antq_shapur_imperial_settlement", "sasanian", "monarchy",
        "Shapur's Imperial Settlement",
        "Coordinate royal command, conquered populations, cities, frontier war, captives and specialists, provincial revenues, and a confidently imperial court.",
        "global_crown_estate_power=0.16|global_burghers_estate_power=0.08|estate_power_from_cabinet=0.24|global_production_efficiency=0.03|set_cabinet_member_cost_modifier=-0.06",
        "P8.2;P9;P13;CAH-XII;IRAN-ADMIN", "secure",
        "Shapur I's campaigns, foundations, and imperial claims are secure; the settlement abstracts uneven incorporation and avoids assigning every later office to his reign.",
        "2",
    ),
    (
        "antq_sasanian_shahrdar_marzban_order", "sasanian", "monarchy",
        "Shahrdar and Marzban Order",
        "Balance royal princes, provincial lords, frontier commanders, fortified districts, mounted forces, tax returns, and the royal post in a ranked but negotiated imperial order.",
        "global_crown_estate_power=0.13|global_nobles_estate_power=0.12|nobles_estate_power_from_cabinet=0.24|global_levy_size_modifier=0.045|replace_cabinet_member_cost_modifier=0.06",
        "P8.2;P9;P13;CAH-XII;IRAN-ADMIN;IRAN-FRAMADAR", "contested",
        "Sasanian provincial and frontier ranks are securely attested, but titles, hierarchy, and competencies changed; this is a bounded fourth-century development path.",
        "3",
    ),
    (
        "antq_yazdegerd_concordat_court", "sasanian", "monarchy",
        "Yazdegerd's Concordat Court",
        "Use royal protection, judicial petition, elite bargaining, and supervised religious establishments to manage a plural empire during renewed great-house tension.",
        "global_crown_estate_power=0.15|global_clergy_estate_power=0.09|global_nobles_estate_power=0.07|crown_estate_power_from_cabinet=0.26|stability_cost_efficiency=-0.03",
        "P8.2;P9;P11;P13;CAH-XII;IRAN-JUDICIAL", "secure",
        "Yazdegerd I's reign from AD 399 and its changing religious policies are secure; concordat denotes a gameplay settlement, not a single surviving treaty or uniform toleration.",
        "5",
    ),
    (
        "antq_bahram_great_house_settlement", "sasanian", "monarchy",
        "Bahram's Great-House Settlement",
        "Reconcile a contested accession through aristocratic recognition, court ceremony, frontier command, hunting and martial prestige, and negotiated provincial service.",
        "global_nobles_estate_power=0.14|global_crown_estate_power=0.11|nobles_estate_power_from_cabinet=0.25|global_levy_size_modifier=0.035|replace_cabinet_member_cost_modifier=0.05",
        "P8.2;P9;P13;CAH-XII;IRAN-ADMIN", "secure",
        "Bahram V's accession in AD 420 and reliance on elite settlement are secure in broad outline; literary court motifs are not treated as literal administrative records.",
        "5",
    ),
    (
        "antq_xiongnu_southern_frontier_court", "xiongnu", "steppe_horde",
        "Southern Xiongnu Frontier Court",
        "Recast the southern wing as a frontier-facing chanyu court sustained by lineage recognition, Han stipends, hostage diplomacy, pasture access, and supervised markets.",
        "global_tribes_estate_power=0.12|global_crown_estate_power=0.08|tribes_estate_power_from_cabinet=0.24|country_cabinet_efficiency=0.025|replace_cabinet_member_cost_modifier=0.06",
        "P8.8;P9;P13;IRAN-XIO;BARFIELD-XIONGNU", "secure",
        "The AD 48 division and southern submission in AD 50 are secure; this path models a negotiated frontier court without treating every southern group as uniformly settled.",
        "0",
    ),
    (
        "antq_xiongnu_northern_western_confederacy", "xiongnu", "steppe_horde",
        "Northern and Western Xiongnu Confederacy",
        "Preserve independent chanyu authority through western tribute relays, wing commands, mobile pasture circuits, fortified crossings, and negotiated clan hosts.",
        "global_tribes_estate_power=0.18|global_nobles_estate_power=0.08|tribes_estate_power_from_cabinet=0.30|global_levy_size_modifier=0.04|replace_cabinet_member_cost_modifier=0.10",
        "P8.8;P9;P13;IRAN-XIO;BARFIELD-XIONGNU", "secure",
        "The northern polity after AD 48 and its displacement by AD 91 are secure; the western framing abstracts changing routes and does not assert one continuous territorial state.",
        "0",
    ),
    (
        "antq_southern_xiongnu_commandery_settlement", "xiongnu", "steppe_horde",
        "Southern Xiongnu Commandery Settlement",
        "Coordinate chanyu households, five regional divisions, Han commanderies, registered dependants, market supply, pasture allocation, and frontier defense.",
        "global_crown_estate_power=0.11|global_tribes_estate_power=0.12|crown_estate_power_from_cabinet=0.22|global_monthly_control=0.0005|set_cabinet_member_cost_modifier=-0.04",
        "P8.8;P9;P13;IRAN-XIO;CAH-X", "contested",
        "Southern Xiongnu residence within the Han frontier is secure, but settlement patterns and commandery supervision varied; the path is not a claim of complete sedentarization.",
        "0",
    ),
    (
        "antq_xiongnu_five_divisions_order", "xiongnu", "steppe_horde",
        "Five Xiongnu Divisions Order",
        "Administer relocated southern Xiongnu communities through five divisions, hereditary leaders, household registers, military obligations, and provincial supervision.",
        "global_crown_estate_power=0.12|global_tribes_estate_power=0.10|crown_estate_power_from_cabinet=0.24|global_monthly_control=0.0007|replace_cabinet_member_cost_modifier=0.07",
        "P8.8;P9;P13;IRAN-XIO;CAH-XII", "secure",
        "The reorganization into five divisions in AD 216 is secure; exact local practice and the balance between hereditary leadership and imperial supervision remain uneven.",
        "2",
    ),
    (
        "antq_han_zhao_chanyu_court", "xiongnu", "steppe_horde",
        "Han-Zhao Chanyu Court",
        "Join chanyu lineage legitimacy to an imperial claimant court, registered military households, provincial appointments, siege supply, and negotiated elite service.",
        "global_crown_estate_power=0.16|global_tribes_estate_power=0.08|global_nobles_estate_power=0.06|crown_estate_power_from_cabinet=0.28|replace_cabinet_member_cost_modifier=0.10",
        "P8.8;P9;P13;IRAN-XIO;CAH-XII", "secure",
        "Liu Yuan's imperial claim from AD 304 and its Xiongnu political inheritance are secure; the path does not collapse the varied Sixteen Kingdoms into one ethnic polity.",
        "3",
    ),
    (
        "antq_tanshihuai_three_divisions", "xianbei", "tribe",
        "Tanshihuai's Three Divisions",
        "Coordinate a newly expansive Xianbei confederation through central, eastern, and western divisions, appointed chiefs, mounted followings, tribute, and seasonal assembly.",
        "global_tribes_estate_power=0.16|global_nobles_estate_power=0.08|tribes_estate_power_from_cabinet=0.30|global_levy_size_modifier=0.045|replace_cabinet_member_cost_modifier=0.08",
        "P8.8;P9;P13;XIANBEI-CONFEDERACY;CAH-XI", "secure",
        "Tanshihuai's mid-second-century confederation and threefold organization are secure in broad outline; office detail remains dependent on later transmitted accounts.",
        "1",
    ),
    (
        "antq_xianbei_successor_federations", "xianbei", "tribe",
        "Xianbei Successor Federations",
        "Let regional lineages and mounted households rebuild smaller federations after failed central succession, using marriage, compensation, pasture bargains, and frontier embassies.",
        "global_tribes_estate_power=0.20|global_nobles_estate_power=0.10|nobles_estate_power_from_cabinet=0.22|replace_cabinet_member_cost_modifier=0.12|stability_cost_efficiency=0.04",
        "P8.8;P9;P13;XIANBEI-CONFEDERACY;CAH-XI", "secure",
        "Fragmentation after Tanshihuai's death in AD 181 is secure; this plural path deliberately avoids inventing one continuous Xianbei central government.",
        "1",
    ),
    (
        "antq_murong_frontier_court", "xianbei", "tribe",
        "Murong Frontier Court",
        "Build a durable frontier court from lineage command, mounted households, fortified settlements, Chinese administrative expertise, embassies, and incorporated communities.",
        "global_crown_estate_power=0.12|global_tribes_estate_power=0.10|global_nobles_estate_power=0.08|country_cabinet_efficiency=0.03|global_monthly_control=0.0006",
        "P8.8;P9;P13;CAH-XII;XIANBEI-CONFEDERACY", "contested",
        "Murong consolidation and mixed frontier institutions are secure later developments; the path abstracts several courts and does not invent a single constitutional founding date.",
        "3",
    ),
    (
        "antq_tuoba_dai_confederacy", "xianbei", "tribe",
        "Tuoba Dai Confederacy",
        "Bind Tuoba lineages, allied chiefs, pasture circuits, mounted hosts, frontier markets, and northern commandery relationships into a more durable confederate court.",
        "global_tribes_estate_power=0.14|global_crown_estate_power=0.10|tribes_estate_power_from_cabinet=0.25|global_levy_size_modifier=0.035|set_cabinet_member_cost_modifier=-0.03",
        "P8.8;P9;P13;CAH-XII;XIANBEI-CONFEDERACY", "secure",
        "The Dai polity's recognition in AD 315 and Tuoba lineage framework are secure; later Northern Wei institutions are not projected back onto this confederate stage.",
        "3",
    ),
    (
        "antq_rouran_khaganate", "xianbei", "steppe_horde",
        "Rouran Khaganate",
        "Organize a fourth-century successor confederation through a khagan's court, ranked chiefs, ternary commands, tributary relations, mobile hosts, and seasonal encampments.",
        "global_crown_estate_power=0.13|global_tribes_estate_power=0.13|crown_estate_power_from_cabinet=0.24|global_levy_size_modifier=0.05|replace_cabinet_member_cost_modifier=0.08",
        "P8.8;P9;P13;IRAN-KHAGAN;ROURAN-ORGANIZATION", "secure",
        "The Rouran confederation under Shelun from AD 402 and early khagan title are secure; neither institution is projected onto the AD 1 Xianbei opening.",
        "5",
    ),
)


def reform_path_rows() -> tuple[
    tuple[str, str, str, str, str, str, str, str, str, str], ...
]:
    return tuple((*row, "0") for row in ALTERNATIVE_REFORMS) + SUCCESSOR_REFORMS


for (
    _key, _profile, _government, _name, _description, _modifiers,
    _source, _confidence, _note, _age_index,
) in reform_path_rows():
    POLITICAL_CONTRACTS[_key] = (_modifiers, _source, _confidence, _note)

PROFILE_BASE_REFORMS: dict[str, tuple[str, ...]] = {
    "roman": ("antq_principate",),
    "late_roman": ("antq_dominate",),
    "han": ("antq_han_imperial_bureaucracy",),
    "late_han": (),
    "iranian": (
        "antq_parthian_king_of_kings", "antq_parthian_subkingdom",
        "antq_indo_scythian_kingship", "antq_arian_satrapal_court",
        "antq_yuezhi_five_yabghus",
    ),
    "sasanian": ("antq_sassanid_centralized_monarchy",),
    "civic": ("antq_indo_greek_kingship", "antq_settled_town_cluster"),
    "gana": ("antq_indian_ganasangha",),
    "steppe": (
        "antq_kangju_confederated_kingship", "antq_wusun_kunmi_confederacy",
        "antq_yancai_aorsi_confederacy",
    ),
    "tribal": (
        "antq_advanced_chiefdom", "antq_tribal_kingdom",
        "antq_saryarka_late_iron_network", "antq_altai_contact_network",
        "antq_sumpa_highland_confederacy", "antq_changtang_pastoral_network",
        "antq_central_plateau_agropastoral_network",
        "antq_eastern_plateau_corridor_network",
        "antq_central_indian_megalithic_network",
        "antq_indian_ocean_atoll_network",
        "antq_mainland_river_corridor_network",
        "antq_sa_huynh_exchange_network",
        "antq_mainland_highland_exchange_network",
        "antq_mainland_iron_age_basin_network",
        "antq_amur_forest_river_network",
        "antq_sakhalin_maritime_network",
        "antq_ussuri_poltsian_network",
        "antq_northern_okjeo_corridor",
        "antq_borneo_cave_river_network",
        "antq_borneo_coastal_exchange_network",
        "antq_borneo_interior_river_network",
        "antq_borneo_foothill_iron_network",
        "antq_philippine_coastal_river_network",
        "antq_philippine_mortuary_community_network",
        "antq_philippine_island_exchange_network",
        "antq_philippine_cave_coast_network",
        "antq_sulawesi_coastal_exchange_network",
        "antq_sulawesi_island_exchange_network",
        "antq_sulawesi_highland_mortuary_network",
        "antq_sulawesi_river_lake_network",
        "antq_sulawesi_peninsula_community_network",
        "antq_north_maluku_metal_age_network",
        "antq_point_peninsula_seasonal_network",
        "antq_havana_hopewell_exchange_network",
        "antq_central_mississippi_woodland_network",
        "antq_kansas_city_hopewell_network",
        "antq_mahan_small_state_league",
        "antq_jinhan_small_state_league",
        "antq_byeonhan_iron_exchange_league",
        "antq_soanian_king_and_council",
        "antq_andean_irrigated_valley_network",
        "antq_andean_highland_community_network",
        "antq_andean_ceremonial_centre_network",
        "antq_wankarani_mound_village_network",
        "antq_herrera_plateau_exchange_network",
        "antq_sierra_nevada_early_community_network",
        "antq_loja_regional_development_network",
        "antq_daga_highland_garden_network",
        "antq_bomberai_coastal_community_network",
        "antq_early_mariana_island_network",
        "antq_yap_ulithi_island_network",
        "antq_orinoco_llanos_ceramic_network",
        "antq_windward_island_ceramic_network",
        "antq_central_california_coastal_network",
        "antq_acutuba_central_amazon_network",
        "antq_bengal_riverine_community_network",
        "antq_eastern_megalithic_community_network",
        "antq_eastern_hill_valley_network",
        "antq_himalayan_highland_network",
        "antq_far_side_port_chiefdom",
        "antq_horn_pastoral_network",
        "antq_west_african_savanna_compound_network",
        "antq_west_african_ironworking_network",
        "antq_west_african_forest_network",
        "antq_early_ironworking_community_network",
        "antq_mobile_hunter_herder_network",
        "antq_mesoamerican_formative_civic_network",
        "antq_mesoamerican_highland_community_network",
        "antq_mesoamerican_exchange_corridor_network",
        "antq_mesoamerican_urban_ritual_center",
        "antq_west_mexican_shaft_tomb_chiefdom",
        "antq_teuchitlan_civic_center_network",
        "antq_west_mexican_basin_community_network",
        "antq_west_mexican_highland_corridor_network",
        "antq_sonoran_desert_farming_network",
    ),
    "sacral": (),
    "royal": (
        "antq_client_monarchy", "antq_buffer_kingdom", "antq_regional_kingship",
        "antq_northern_indian_coin_kingship", "antq_pundranagara_urban_kingship",
        "antq_sogdian_city_compact", "antq_dayuan_oasis_kingship",
        "antq_han_western_regions_kingship", "antq_zhangzhung_plateau_kingship",
        "antq_tamilakam_velir_court", "antq_central_indian_urban_kingship",
        "antq_central_indian_janapada", "antq_upper_mahanadi_kingship",
    ),
    "xiongnu": ("antq_steppe_confederation",),
    "xianbei": ("antq_xianbei_eastern_confederacy",),
    "goguryeo": ("antq_early_korean_kingdom",),
    "kushite": ("antq_kushite_dual_kingship",),
    "lankan": ("antq_lankan_kingdom",),
    "armenian": ("antq_artaxiad_highland_kingship",),
    "nabataean": ("antq_nabataean_caravan_kingship",),
    "himyarite": ("antq_himyarite_terrace_kingship",),
    "satavahana": ("antq_satavahana_deccan_kingship",),
    "catuvellaunian": ("antq_catuvellaunian_oppidum_kingship",),
    "trinovantian": ("antq_trinovantian_coin_kingship",),
    "brigantian": ("antq_brigantian_hillfort_confederacy",),
    "durotrigian": ("antq_durotrigian_hillfort_coin_order",),
    "ivernian": ("antq_ivernian_regional_assembly",),
    "aestian": ("antq_aestian_amber_coast_order",),
    "frisian": ("antq_frisian_terp_community_order",),
    "dacian": ("antq_dacian_divided_kingships",),
    "garamantian": ("antq_garamantian_oasis_state",),
    "marcomannic": ("antq_marcomannic_bohemian_kingship",),
    "cheruscan": ("antq_cheruscan_kindred_assembly",),
    "chattian": ("antq_chattian_host_order",),
    "batavian": ("antq_batavian_rhine_compact",),
    "semnonian": ("antq_semnonian_sacred_confederacy",),
    "sabaean": ("antq_sabaean_marib_kingship",),
    "mauretanian": ("antq_mauretanian_client_kingship",),
    "judean": ("antq_herodian_judean_ethnarchy",),
    "cappadocian": ("antq_cappadocian_client_kingship",),
    "thracian": ("antq_odrysian_client_kingship",),
    "bosporan": ("antq_bosporan_client_kingship",),
    "galilean": ("antq_herodian_galilean_tetrarchy",),
    "batanean": ("antq_herodian_batanean_tetrarchy",),
    "commagenean": ("antq_commagenean_client_kingship",),
    "emesan": ("antq_emesan_client_dynasty",),
}
PROFILE_PARLIAMENTS = {
    "roman": "antq_roman_senate",
    "late_roman": "antq_imperial_consistory",
    "han": "antq_han_court_conference",
    "late_han": "antq_eastern_han_imperial_secretariat",
    "iranian": "antq_iranian_great_council",
    "sasanian": "antq_sasanian_royal_council",
    "civic": "antq_civic_assembly",
    "gana": "antq_gana_assembly",
    "steppe": "antq_confederation_council",
    "tribal": "antq_tribal_assembly",
    "sacral": "antq_sacral_court",
    "royal": "antq_royal_council",
    "xiongnu": "antq_xiongnu_wing_council",
    "xianbei": "antq_xianbei_chiefly_assembly",
    "goguryeo": "antq_goguryeo_royal_council",
    "kushite": "antq_meroitic_royal_council",
    "lankan": "antq_anuradhapura_royal_council",
    "armenian": "antq_armenian_royal_council",
    "nabataean": "antq_nabataean_royal_council",
    "himyarite": "antq_himyarite_royal_council",
    "satavahana": "antq_satavahana_royal_council",
    "catuvellaunian": "antq_catuvellaunian_royal_council",
    "trinovantian": "antq_trinovantian_camulodunon_council",
    "brigantian": "antq_brigantian_northern_council",
    "durotrigian": "antq_durotrigian_hillfort_assembly",
    "ivernian": "antq_ivernian_regional_gathering",
    "aestian": "antq_aestian_amber_coast_gathering",
    "frisian": "antq_frisian_terp_assembly",
    "dacian": "antq_dacian_hillfort_council",
    "garamantian": "antq_garamantian_oasis_council",
    "marcomannic": "antq_marcomannic_royal_council",
    "cheruscan": "antq_cheruscan_coalition_assembly",
    "chattian": "antq_chattian_host_council",
    "batavian": "antq_batavian_island_council",
    "semnonian": "antq_semnonian_grove_assembly",
    "sabaean": "antq_sabaean_royal_council",
    "mauretanian": "antq_mauretanian_royal_council",
    "judean": "antq_judean_ethnarchic_council",
    "cappadocian": "antq_cappadocian_royal_council",
    "thracian": "antq_thracian_royal_council",
    "bosporan": "antq_bosporan_royal_council",
    "galilean": "antq_galilean_tetrarchic_council",
    "batanean": "antq_batanean_tetrarchic_council",
    "commagenean": "antq_commagenean_royal_council",
    "emesan": "antq_emesan_dynastic_council",
}

# Bookmark setup does not execute a reform's ``on_activate`` effect.  Export
# the same council contract so generated AD 1 governments begin initialized.
PARLIAMENT_BY_REFORM = {
    reform: PROFILE_PARLIAMENTS[profile]
    for profile, reforms_for_profile in PROFILE_BASE_REFORMS.items()
    for reform in reforms_for_profile
}


@dataclass(frozen=True)
class PowerData:
    dynasties: tuple[dict[str, str], ...]
    characters: tuple[dict[str, str], ...]
    governments: dict[str, dict[str, str]]
    ruler_terms: tuple[dict[str, str], ...]
    regnal_histories: tuple[dict[str, str], ...]
    privileges: tuple[dict[str, str], ...]
    laws: tuple[dict[str, str], ...]
    tags: dict[str, str]


def read_rows(path: Path, fields: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != fields:
            raise ValueError(f"{path.relative_to(ROOT)} header does not match required field order")
        return [{key: (value or "").strip() for key, value in row.items()} for row in reader]


def require_token(value: str, label: str) -> None:
    if not TOKEN_RE.fullmatch(value):
        raise ValueError(f"{label} must be a lowercase script token: {value!r}")


def pipe_values(value: str, label: str) -> tuple[str, ...]:
    parts = tuple(value.split("|")) if value else ()
    if not parts or any(not part for part in parts):
        raise ValueError(f"{label} must be a non-empty pipe-delimited list")
    return parts


def assignments(value: str, label: str) -> tuple[tuple[str, str], ...]:
    parsed: list[tuple[str, str]] = []
    for part in pipe_values(value, label):
        if part.count("=") != 1:
            raise ValueError(f"{label} has an invalid assignment {part!r}")
        key, assigned = part.split("=", 1)
        require_token(key, f"{label} modifier")
        if not VALUE_RE.fullmatch(assigned):
            raise ValueError(f"{label} has an unsafe value {assigned!r}")
        parsed.append((key, assigned))
    if len({key for key, _ in parsed}) != len(parsed):
        raise ValueError(f"{label} contains a duplicate key")
    return tuple(parsed)


def political_contract_ledger() -> str:
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(("reform", "modifiers", "source", "confidence", "note"))
    for reform, (modifiers, source, confidence, note) in POLITICAL_CONTRACTS.items():
        writer.writerow((reform, modifiers, source, confidence, note))
    return output.getvalue()


def alternative_reform_ledger() -> str:
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow((
        "reform", "profile", "government", "name", "description", "modifiers",
        "source", "confidence", "note", "age_index",
    ))
    writer.writerows(reform_path_rows())
    return output.getvalue()


def reform_visibility_matrix(data: PowerData) -> str:
    """Render the exact opening reform family visible to every AD 1 tag."""
    profile_by_base = {
        reform: profile
        for profile, base_reforms in PROFILE_BASE_REFORMS.items()
        for reform in base_reforms
    }
    alternatives_by_profile = {
        profile: tuple(row[0] for row in reform_path_rows() if row[1] == profile)
        for profile in PROFILE_BASE_REFORMS
    }
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(("design_tag", "engine_tag", "opening_reform", "profile", "visible_reforms"))
    with POLITIES.open(encoding="utf-8-sig", newline="") as handle:
        for polity in sorted(csv.DictReader(handle), key=lambda row: row["tag"]):
            government = data.governments.get(polity["tag"])
            opening = (
                government["reform"]
                if government
                else (
                    "antq_advanced_chiefdom"
                    if polity["kind"] == "sop"
                    else "antq_regional_kingship"
                )
            )
            profile = profile_by_base.get(opening, "")
            if not profile:
                raise ValueError(f"opening reform {opening} has no visibility profile")
            visible = {opening, *alternatives_by_profile[profile]}
            if polity["tag"] == "ROM":
                visible.add("antq_dominate")
            writer.writerow((
                polity["tag"], data.tags[polity["tag"]], opening, profile,
                "|".join(sorted(visible)),
            ))
    return stream.getvalue()


def has_named_active_head(government: dict[str, str]) -> bool:
    """Recognize both ordinary rulers and the verified Han regency shape."""
    return government["ruler"] != "random" and bool(
        government["ruler"] or (government["regency"] and government["heir"])
    )


def load_power_data() -> PowerData:
    dynasties = read_rows(DATA / "dynasties.csv", DYN_FIELDS)
    characters = read_rows(DATA / "characters.csv", CHAR_FIELDS)
    governments_rows = read_rows(DATA / "governments.csv", GOV_FIELDS)
    regional_government_rows = read_rows(
        DATA / "regional_government_overlays.csv", REGIONAL_GOV_FIELDS
    )
    ruler_terms = read_rows(DATA / "ruler_terms.csv", TERM_FIELDS)
    regnal_histories = read_rows(DATA / "regnal_histories.csv", REGNAL_HISTORY_FIELDS)
    privileges = read_rows(DATA / "privileges.csv", PRIV_FIELDS)
    for row in privileges:
        row["potential_reforms"] = ""
        row["potential_tags"] = ""
        row["exclusive_with"] = ""
    privileges.extend(read_rows(DATA / "estate_order_privileges.csv", S2_PRIV_FIELDS))
    for row in privileges:
        additions = modifier_additions("privilege_modifier", row["key"])
        if additions:
            suffix = "|".join(f"{key}={value}" for key, value in additions)
            row["modifiers"] = "|".join(
                part for part in (row["modifiers"], suffix) if part
            )
    laws = read_rows(DATA / "laws.csv", LAW_FIELDS)
    tags = {entry["design_tag"]: entry["engine_tag"] for entry in json.loads(TAG_MAP.read_text(encoding="utf-8"))["entries"]}
    locations = set(json.loads((ROOT / "docs/vanilla_symbols/locations.json").read_text(encoding="utf-8-sig")))
    government_types = set(json.loads(GOVERNMENT_TYPES.read_text(encoding="utf-8-sig")))
    estates = set(json.loads((ROOT / "docs/vanilla_symbols/estate.json").read_text(encoding="utf-8-sig")))
    failures: list[str] = []
    dynasty_keys: set[str] = set()
    for row in dynasties:
        if any(not row[field] for field in DYN_FIELDS):
            failures.append("dynasties.csv contains a blank required field")
            continue
        try:
            require_token(row["key"], "dynasty key")
        except ValueError as exc:
            failures.append(str(exc))
        if row["key"] in dynasty_keys:
            failures.append(f"duplicate dynasty key: {row['key']}")
        dynasty_keys.add(row["key"])
        if row["home"] not in locations:
            failures.append(f"dynasty {row['key']} has unknown home location {row['home']}")
        if row["confidence"] not in {"secure", "contested"}:
            failures.append(f"dynasty {row['key']} has invalid confidence {row['confidence']}")

    character_keys: set[str] = set()
    for row in characters:
        required = ("key", "design_tag", "name", "female", "culture", "religion", "dynasty", "source", "confidence", "note")
        if any(not row[field] for field in required):
            failures.append("characters.csv contains a blank required field")
            continue
        try:
            require_token(row["key"], "character key")
        except ValueError as exc:
            failures.append(str(exc))
        if row["key"] in character_keys:
            failures.append(f"duplicate character key: {row['key']}")
        character_keys.add(row["key"])
        if row["design_tag"] not in tags:
            failures.append(f"character {row['key']} references unknown design tag {row['design_tag']}")
        if row["female"] not in {"yes", "no"}:
            failures.append(f"character {row['key']} has invalid female value {row['female']}")
        if row["dynasty"] not in dynasty_keys:
            failures.append(f"character {row['key']} references unknown dynasty {row['dynasty']}")
        if row["birthplace"] and row["birthplace"] not in locations:
            failures.append(f"character {row['key']} has unknown birthplace {row['birthplace']}")
        if row["confidence"] not in {"secure", "contested"}:
            failures.append(f"character {row['key']} has invalid confidence {row['confidence']}")
        dates: list[BiographyDate] = []
        for field in ("birth_date", "death_date"):
            if not row[field]:
                continue
            try:
                dates.append(BiographyDate.parse(row[field]))
            except ValueError as exc:
                failures.append(f"character {row['key']} invalid {field}: {exc}")
        if len(dates) == 2 and dates[1] <= dates[0]:
            failures.append(f"character {row['key']} dies on or before birth")
        ratings = tuple(row[field] for field in ("adm", "dip", "mil"))
        if any(ratings) and not all(ratings):
            failures.append(f"character {row['key']} must provide all or no ability ratings")
        for rating in ratings:
            if rating and (not rating.isdigit() or not 0 <= int(rating) <= 100):
                failures.append(f"character {row['key']} has invalid ability rating {rating}")

    privilege_keys: set[str] = set()
    for row in privileges:
        if any(not row[field] for field in PRIV_FIELDS):
            failures.append("privileges.csv contains a blank required field")
            continue
        try:
            require_token(row["key"], "privilege key")
            parsed_modifiers = assignments(row["modifiers"], f"privilege {row['key']}")
        except ValueError as exc:
            failures.append(str(exc))
            parsed_modifiers = ()
        if row["key"] in privilege_keys:
            failures.append(f"duplicate privilege key: {row['key']}")
        privilege_keys.add(row["key"])
        if row["estate"] not in estates:
            failures.append(f"privilege {row['key']} uses unknown estate {row['estate']}")
        for key, _ in parsed_modifiers:
            if key not in MODIFIER_KEYS:
                failures.append(f"privilege {row['key']} uses unharvested modifier {key}")
        estate_power_key = {
            "nobles_estate": "global_nobles_estate_power",
            "clergy_estate": "global_clergy_estate_power",
            "burghers_estate": "global_burghers_estate_power",
            "peasants_estate": "global_peasants_estate_power",
            "tribes_estate": "global_tribes_estate_power",
        }.get(row["estate"])
        if estate_power_key and estate_power_key not in {
            key for key, _ in parsed_modifiers
        }:
            failures.append(
                f"privilege {row['key']} has no power set for {row['estate']}"
            )
        if row["confidence"] not in {"secure", "contested"}:
            failures.append(f"privilege {row['key']} has invalid confidence {row['confidence']}")
        if row["potential_reforms"]:
            try:
                for reform in pipe_values(
                    row["potential_reforms"], f"privilege {row['key']} reforms"
                ):
                    require_token(reform, f"privilege {row['key']} reform")
            except ValueError as exc:
                failures.append(str(exc))
        if row["potential_tags"]:
            for tag in pipe_values(
                row["potential_tags"], f"privilege {row['key']} tags"
            ):
                if tag not in set(tags.values()):
                    failures.append(f"privilege {row['key']} uses unknown engine tag {tag}")
    for row in privileges:
        if row["exclusive_with"] and row["exclusive_with"] not in privilege_keys:
            failures.append(
                f"privilege {row['key']} excludes unknown privilege {row['exclusive_with']}"
            )

    law_keys: set[str] = set()
    law_options: set[tuple[str, str]] = set()
    for row in laws:
        if any(not row[field] for field in LAW_FIELDS):
            failures.append("laws.csv contains a blank required field")
            continue
        try:
            for field in ("law", "law_category", "law_gov_group", "option"):
                require_token(row[field], f"law {row['law']} {field}")
            parsed_modifiers = assignments(row["modifiers"], f"law {row['law']}")
            preferences = pipe_values(row["estate_preferences"], f"law {row['law']} estate preferences")
        except ValueError as exc:
            failures.append(str(exc))
            parsed_modifiers = ()
            preferences = ()
        if row["law"] in law_keys:
            failures.append(f"duplicate law key: {row['law']}")
        law_keys.add(row["law"])
        law_options.add((row["law"], row["option"]))
        if row["law_category"] not in LAW_CATEGORIES:
            failures.append(f"law {row['law']} has unsupported category {row['law_category']}")
        if row["law_gov_group"] not in government_types:
            failures.append(f"law {row['law']} has unknown government group {row['law_gov_group']}")
        for estate in preferences:
            if estate not in estates:
                failures.append(f"law {row['law']} uses unknown estate preference {estate}")
        for key, _ in parsed_modifiers:
            if key not in MODIFIER_KEYS:
                failures.append(f"law {row['law']} uses unharvested modifier {key}")
        if row["confidence"] not in {"secure", "contested"}:
            failures.append(f"law {row['law']} has invalid confidence {row['confidence']}")
    law_options.update(s2_all_law_options())

    government_rows_by_tag = {row["design_tag"]: row.copy() for row in governments_rows}
    if len(government_rows_by_tag) != len(governments_rows):
        failures.append("governments.csv contains duplicate design tags")
    overlay_keys: set[str] = set()
    for row in regional_government_rows:
        if any(not row[field] for field in REGIONAL_GOV_FIELDS):
            failures.append("regional_government_overlays.csv contains a blank required field")
            continue
        try:
            require_token(row["key"], "regional government overlay key")
            overlay_tags = pipe_values(row["tags"], f"regional overlay {row['key']} tags")
            overlay_privileges = pipe_values(
                row["privileges"], f"regional overlay {row['key']} privileges"
            )
            overlay_laws = assignments(row["laws"], f"regional overlay {row['key']} laws")
        except ValueError as exc:
            failures.append(str(exc))
            continue
        if row["key"] in overlay_keys:
            failures.append(f"duplicate regional government overlay: {row['key']}")
        overlay_keys.add(row["key"])
        if row["confidence"] not in {"secure", "contested"}:
            failures.append(
                f"regional government overlay {row['key']} has invalid confidence "
                f"{row['confidence']}"
            )
        for privilege in overlay_privileges:
            if privilege not in privilege_keys:
                failures.append(
                    f"regional government overlay {row['key']} references unknown privilege "
                    f"{privilege}"
                )
        for law, option in overlay_laws:
            if (law, option) not in law_options:
                failures.append(
                    f"regional government overlay {row['key']} references unknown law option "
                    f"{law}={option}"
                )
        for design_tag in overlay_tags:
            if design_tag not in government_rows_by_tag:
                failures.append(
                    f"regional government overlay {row['key']} references unknown profile "
                    f"{design_tag}"
                )
                continue
            government = government_rows_by_tag[design_tag]
            existing_privileges = list(pipe_values(
                government["privileges"], f"government {design_tag} privileges"
            ))
            for privilege in overlay_privileges:
                if privilege not in existing_privileges:
                    existing_privileges.append(privilege)
            existing_laws = dict(assignments(
                government["laws"], f"government {design_tag} laws"
            ))
            for law, option in overlay_laws:
                if law in existing_laws and existing_laws[law] != option:
                    failures.append(
                        f"regional government overlay {row['key']} conflicts on {design_tag} "
                        f"law {law}"
                    )
                existing_laws[law] = option
            government["privileges"] = "|".join(existing_privileges)
            government["laws"] = "|".join(
                f"{law}={option}" for law, option in existing_laws.items()
            )
            government["source"] = f"{government['source']};{row['source']}"
            government["note"] = f"{government['note']} Regional layer: {row['note']}"
    profile_laws = s2_starting_laws_by_tag()
    for design_tag, government in government_rows_by_tag.items():
        if design_tag not in profile_laws:
            failures.append(f"government {design_tag} has no S2 legal profile")
            continue
        existing_laws = dict(assignments(
            government["laws"], f"government {design_tag} laws before S2 profile"
        ))
        for law, option in profile_laws[design_tag]:
            if law in existing_laws and existing_laws[law] != option:
                failures.append(f"S2 legal profile conflicts on {design_tag} law {law}")
            existing_laws[law] = option
        government["laws"] = "|".join(
            f"{law}={option}" for law, option in existing_laws.items()
        )
        government["source"] = f"{government['source']};S2-LAWS"
        government["note"] = (
            f"{government['note']} Legal profile: fourteen mutually exclusive "
            "AD 1 policy questions from the generated S2 law registry."
        )
    governments_rows = list(government_rows_by_tag.values())

    governments: dict[str, dict[str, str]] = {}
    for row in governments_rows:
        required = (
            "design_tag", "government_type", "heir_selection", "reform", "privileges", "laws",
            "societal_values", "source", "confidence", "note",
        )
        if any(not row[field] for field in required):
            failures.append("governments.csv contains a blank required field")
            continue
        if row["design_tag"] in governments:
            failures.append(f"duplicate government profile: {row['design_tag']}")
        governments[row["design_tag"]] = row
        if row["design_tag"] not in tags:
            failures.append(f"government references unknown design tag {row['design_tag']}")
        if row["government_type"] not in government_types:
            failures.append(f"government {row['design_tag']} uses unknown type {row['government_type']}")
        regency = bool(row["regency"])
        if not row["ruler"] and not (regency and row["heir"]):
            failures.append(
                f"government {row['design_tag']} needs a ruler, or a regency heir"
            )
        if regency and row["ruler"]:
            failures.append(
                f"government {row['design_tag']} must use heir rather than ruler during a regency"
            )
        random_ruler = row["ruler"] == "random"
        if random_ruler and row["government_type"] not in {"monarchy", "republic", "tribe"}:
            failures.append(f"government {row['design_tag']} uses random ruler with an unverified type")
        for field in ("ruler", "heir", "consort", "active_regent"):
            if row[field] and row[field] not in character_keys and not (field == "ruler" and random_ruler):
                failures.append(f"government {row['design_tag']} references unknown {field} {row[field]}")
        government_head = row["heir"] if regency else row["ruler"]
        if government_head in character_keys:
            ruler = next(character for character in characters if character["key"] == government_head)
            if ruler["design_tag"] != row["design_tag"]:
                failures.append(
                    f"government {row['design_tag']} active head belongs to {ruler['design_tag']}"
                )
        terms = tuple(row[field] for field in ("regency", "start_regency_date", "end_regency_date"))
        if any(terms) and not all(terms):
            failures.append(f"government {row['design_tag']} has an incomplete regency")
        if all(terms):
            try:
                start = AntqDate.parse(row["start_regency_date"])
                end = AntqDate.parse(row["end_regency_date"])
                if end <= start:
                    failures.append(f"government {row['design_tag']} regency end is not after start")
            except ValueError as exc:
                failures.append(f"government {row['design_tag']} invalid regency date: {exc}")
        if row["confidence"] not in {"secure", "contested"}:
            failures.append(f"government {row['design_tag']} has invalid confidence {row['confidence']}")
        try:
            assigned_privileges = pipe_values(row["privileges"], f"government {row['design_tag']} privileges")
            assigned_laws = assignments(row["laws"], f"government {row['design_tag']} laws")
            assigned_values = assignments(row["societal_values"], f"government {row['design_tag']} societal values")
        except ValueError as exc:
            failures.append(str(exc))
            assigned_privileges = ()
            assigned_laws = ()
            assigned_values = ()
        for privilege in assigned_privileges:
            if privilege not in privilege_keys:
                failures.append(f"government {row['design_tag']} references unknown privilege {privilege}")
        for law, option in assigned_laws:
            if (law, option) not in law_options:
                failures.append(f"government {row['design_tag']} references unknown law option {law}={option}")
        for key, value in assigned_values:
            if key not in SOCIAL_VALUE_KEYS:
                failures.append(f"government {row['design_tag']} uses unknown societal value {key}")
            if not re.fullmatch(r"-?\d+", value) or not -100 <= int(value) <= 100:
                failures.append(f"government {row['design_tag']} has invalid societal value {key}={value}")

    with POLITIES.open(encoding="utf-8-sig", newline="") as handle:
        polity_rows = list(csv.DictReader(handle))
    all_tags = {row["tag"] for row in polity_rows if row.get("tag")}
    tier_tags = {
        row["tag"]
        for row in polity_rows
        if row.get("tier") in {"1", "2"} and row.get("tag")
    }
    for design_tag in sorted(tier_tags - set(governments)):
        failures.append(f"missing M6 government profile for Tier-1/2 tag {design_tag}")
    for design_tag in sorted(set(governments) - all_tags):
        failures.append(f"M6 government profile is not a current polity tag: {design_tag}")
    if not MIN_SOURCED_CHARACTERS <= len(characters) <= MAX_SOURCED_CHARACTERS:
        failures.append(
            f"M6 requires {MIN_SOURCED_CHARACTERS}-{MAX_SOURCED_CHARACTERS} source-led characters; "
            f"found {len(characters)}"
        )
    named_profiles = sum(
        1 for government in governments.values()
        if has_named_active_head(government)
    )
    if named_profiles < MIN_NAMED_TIER_PROFILES:
        failures.append(
            f"M6 requires at least {MIN_NAMED_TIER_PROFILES} Tier-1/2 profiles with a named active head; "
            f"found {named_profiles}"
        )
    for design_tag, government in governments.items():
        if government["ruler"] == "random" and not any(
            marker in government["note"].lower() for marker in ANONYMOUS_PROFILE_MARKERS
        ):
            failures.append(
                f"anonymous M6 profile {design_tag} must state its evidence boundary in the note"
            )

    # The compact M6 core privilege table predates the explicit potential columns
    # used by the later estate-order table.  Derive an exact country boundary from
    # the reviewed opening setups so none of those regional contracts appears in
    # an unrelated country's estate UI.
    privilege_start_tags: dict[str, list[str]] = {
        row["key"]: [] for row in privileges
    }
    for design_tag, government in governments.items():
        for privilege in pipe_values(
            government["privileges"], f"government {design_tag} privileges"
        ):
            privilege_start_tags[privilege].append(tags[design_tag])
    for privilege in privileges:
        if privilege["potential_reforms"] or privilege["potential_tags"]:
            continue
        eligible_tags = tuple(dict.fromkeys(privilege_start_tags[privilege["key"]]))
        if not eligible_tags:
            failures.append(
                f"privilege {privilege['key']} has neither an explicit potential nor "
                "an opening country assignment"
            )
            continue
        privilege["potential_tags"] = "|".join(eligible_tags)
    privilege_rows_by_key = {row["key"]: row for row in privileges}
    for privilege in privileges:
        if not privilege["potential_reforms"] and not privilege["potential_tags"]:
            failures.append(f"privilege {privilege['key']} has no declared visibility gate")
        if privilege["potential_reforms"] and privilege["potential_tags"]:
            failures.append(
                f"privilege {privilege['key']} mixes profile and exact-country gates"
            )
    for design_tag, government in governments.items():
        engine_tag = tags[design_tag]
        for privilege_key in pipe_values(
            government["privileges"], f"government {design_tag} privileges"
        ):
            privilege = privilege_rows_by_key[privilege_key]
            reforms = set(pipe_values(
                privilege["potential_reforms"],
                f"privilege {privilege_key} potential reforms",
            )) if privilege["potential_reforms"] else set()
            exact_tags = set(pipe_values(
                privilege["potential_tags"],
                f"privilege {privilege_key} potential tags",
            )) if privilege["potential_tags"] else set()
            if government["reform"] not in reforms and engine_tag not in exact_tags:
                failures.append(
                    f"government {design_tag} starts with unauthorized privilege "
                    f"{privilege_key}"
                )

    term_tags: set[str] = set()
    term_pairs: set[tuple[str, str]] = set()
    campaign_start = AntqDate.parse("1.1.1")
    for row in ruler_terms:
        required = ("design_tag", "character", "engine_start_date", "historical_reign", "source", "confidence", "note")
        if any(not row[field] for field in required):
            failures.append("ruler_terms.csv contains a blank required field")
            continue
        if row["design_tag"] not in governments:
            failures.append(f"ruler term references unknown government profile {row['design_tag']}")
        if row["character"] not in character_keys:
            failures.append(f"ruler term references unknown character {row['character']}")
        elif row["design_tag"] in governments and row["character"] != (
            governments[row["design_tag"]]["heir"]
            if governments[row["design_tag"]]["regency"]
            else governments[row["design_tag"]]["ruler"]
        ):
            failures.append(f"ruler term for {row['design_tag']} must use the active government ruler")
        pair = (row["design_tag"], row["character"])
        if pair in term_pairs:
            failures.append(f"duplicate ruler term for {row['design_tag']} / {row['character']}")
        term_pairs.add(pair)
        if row["design_tag"] in term_tags:
            failures.append(f"multiple current ruler terms for {row['design_tag']}")
        term_tags.add(row["design_tag"])
        try:
            start = AntqDate.parse(row["engine_start_date"])
            if start != campaign_start:
                failures.append(f"ruler term for {row['design_tag']} must begin on the campaign start")
            if row["engine_end_date"] and AntqDate.parse(row["engine_end_date"]) <= start:
                failures.append(f"ruler term for {row['design_tag']} ends on or before its start")
        except ValueError as exc:
            failures.append(f"ruler term for {row['design_tag']} has an invalid engine date: {exc}")
        if row["regnal_number"] and (not row["regnal_number"].isdigit() or not 1 <= int(row["regnal_number"]) <= 999):
            failures.append(f"ruler term for {row['design_tag']} has an invalid regnal number")
        if row["confidence"] not in {"secure", "contested"}:
            failures.append(f"ruler term for {row['design_tag']} has invalid confidence {row['confidence']}")
    for design_tag, government in governments.items():
        if (
            government["ruler"] != "random"
            and not government["regency"]
            and design_tag not in term_tags
        ):
            failures.append(f"government {design_tag} has no campaign-valid ruler term")

    history_by_tag: dict[str, list[int]] = {}
    history_pairs: set[tuple[str, int]] = set()
    for row in regnal_histories:
        if any(not row[field] for field in REGNAL_HISTORY_FIELDS):
            failures.append("regnal_histories.csv contains a blank required field")
            continue
        if row["design_tag"] not in tags:
            failures.append(f"regnal history references unknown design tag {row['design_tag']}")
        if not row["sequence"].isdigit() or int(row["sequence"]) < 1:
            failures.append(f"regnal history has invalid sequence {row['sequence']!r}")
            continue
        pair = (row["design_tag"], int(row["sequence"]))
        if pair in history_pairs:
            failures.append(f"duplicate regnal-history sequence for {row['design_tag']}: {row['sequence']}")
        history_pairs.add(pair)
        history_by_tag.setdefault(row["design_tag"], []).append(int(row["sequence"]))
        if row["confidence"] not in {"secure", "contested"}:
            failures.append(f"regnal history for {row['design_tag']} has invalid confidence {row['confidence']}")
    for design_tag in ("ROM", "HAN"):
        sequence = sorted(history_by_tag.get(design_tag, []))
        if not sequence:
            failures.append(f"regnal history is required for {design_tag}")
        elif sequence != list(range(1, len(sequence) + 1)):
            failures.append(f"regnal history for {design_tag} is not a contiguous sequence")

    used_reforms = {government["reform"] for government in governments.values()}
    # Core/regional contracts include every reviewed regional network above,
    # including the eight exact final-placeholder replacements.
    expected_contract_count = 136 + len(ALTERNATIVE_REFORMS) + len(SUCCESSOR_REFORMS)
    if (
        len(POLITICAL_CONTRACTS) != expected_contract_count
        or not used_reforms.issubset(POLITICAL_CONTRACTS)
    ):
        failures.append(
            "political appointment contracts must cover every core, regional, and successor reform"
        )
    if len({contract[0] for contract in POLITICAL_CONTRACTS.values()}) < 121:
        failures.append("political appointment contracts are insufficiently differentiated")
    path_rows = reform_path_rows()
    alternative_profiles = [row[1] for row in path_rows]
    two_path_profiles = {
            "roman", "han", "civic", "gana", "steppe", "tribal",
            "sacral", "royal", "goguryeo", "kushite", "lankan",
            "armenian", "nabataean", "himyarite", "satavahana",
            "catuvellaunian", "marcomannic", "sabaean", "mauretanian",
            "judean", "cappadocian", "thracian", "bosporan",
            "galilean", "batanean", "commagenean", "emesan",
            "cheruscan", "chattian", "batavian", "semnonian",
            "trinovantian", "brigantian", "durotrigian", "ivernian",
            "aestian", "frisian", "dacian", "garamantian",
    } - {"roman", "han"}
    if (
        len(path_rows) != len(ALTERNATIVE_REFORMS) + len(SUCCESSOR_REFORMS)
        or alternative_profiles.count("roman") != 5
        or alternative_profiles.count("late_roman") != 3
        or alternative_profiles.count("han") != 3
        or alternative_profiles.count("late_han") != 6
        or alternative_profiles.count("iranian") != 5
        or alternative_profiles.count("sasanian") != 5
        or alternative_profiles.count("xiongnu") != 7
        or alternative_profiles.count("xianbei") != 5
        or any(alternative_profiles.count(profile) != 2 for profile in two_path_profiles)
    ):
        failures.append(
            "reform paths must provide two regional alternatives plus the documented deeper imperial and steppe successor arcs"
        )
    for reform, (modifier_text, _source, confidence, note) in POLITICAL_CONTRACTS.items():
        try:
            parsed = assignments(modifier_text, f"political contract {reform}")
        except ValueError as exc:
            failures.append(str(exc))
            parsed = ()
        for key, _value in parsed:
            if key not in MODIFIER_KEYS:
                failures.append(
                    f"political contract {reform} uses unharvested modifier {key}"
                )
        if confidence not in {"secure", "contested"} or len(note) < 55:
            failures.append(f"political contract {reform} lacks a bounded evidence note")

    if failures:
        raise ValueError("\n".join(sorted(set(failures))))
    return PowerData(
        tuple(dynasties), tuple(characters), governments, tuple(ruler_terms), tuple(regnal_histories),
        tuple(privileges), tuple(laws), tags,
    )


def dynasty_manager(data: PowerData) -> str:
    lines = ["# Generated by tools/m6_power.py --write; sourced M6 core dynasties.", "dynasty_manager = {"]
    for row in data.dynasties:
        lines.extend((
            f"\t{row['key']} = {{",
            f"\t\tname = {{ name = {row['key']} }}",
            f"\t\thome = {row['home']}",
            "\t}",
            "",
        ))
    lines.extend(("}", ""))
    return "\n".join(lines)


def character_manager(data: PowerData) -> str:
    lines = [
        "# Generated by tools/m6_power.py --write; source-labelled M6 core roster.",
        "# Parents precede children whenever future CSV rows add parent references.",
        "# Pre-campaign biography dates remain sourced ledger metadata and are never emitted.",
        "character_db = {",
    ]
    runtime_bce_officeholders = {
        "antq_gaius_caesar",
        "antq_livia",
    }
    for row in data.characters:
        # The two non-ruler BCE officeholders are supplied by the runtime age
        # adapter.  Augustus and Phraates remain serialized as stable office
        # placeholders so country initialization cannot pick a random head.
        if row["key"] in runtime_bce_officeholders:
            continue
        first_name_key = (
            "antq_m6_placeholder_ruler"
            if row["key"] in {"antq_augustus", "antq_phraates_v"}
            else row["key"]
        )
        lines.extend((
            f"\t{row['key']} = {{",
            f"\t\tfirst_name = {{ name = {first_name_key} }}",
            f"\t\tculture = {row['culture']}",
            f"\t\treligion = {row['religion']}",
        ))
        if row["female"] == "yes":
            lines.append("\t\tfemale = yes")
        if all(row[field] for field in ("adm", "dip", "mil")):
            lines.append(f"\t\tadm = {row['adm']} dip = {row['dip']} mil = {row['mil']}")
        for field in ("birth_date", "death_date"):
            if row[field]:
                date = BiographyDate.parse(row[field])
                # EU5's bookmark character parser accepts campaign-calendar
                # dates only.  Retaining a BCE date here invalidates the entire
                # character, which in turn silently replaces a named ruler,
                # heir, or regent.  The original date remains in the sourced
                # CSV and its note; only engine-representable dates are written.
                if date.year >= 1:
                    lines.append(f"\t\t{field} = {date.engine()}")
        if row["birthplace"]:
            lines.append(f"\t\tbirth = {row['birthplace']}")
        if row["estate"]:
            lines.append(f"\t\testate = {row['estate']}")
        lines.extend((
            f"\t\tdynasty = {row['dynasty']}",
            f"\t\ttag = {data.tags[row['design_tag']]}",
            "\t}",
            "",
        ))
    lines.extend(("}", ""))
    return "\n".join(lines)


def runtime_adult_officeholders(data: PowerData) -> frozenset[str]:
    """Return named opening officeholders whose adult age predates the calendar."""
    characters = {row["key"]: row for row in data.characters}
    keys: set[str] = set()
    for government in data.governments.values():
        for field in ("ruler", "consort", "active_regent"):
            key = government[field]
            if not key or key == "random":
                continue
            character = characters[key]
            birth = character["birth_date"]
            if not birth or BiographyDate.parse(birth).year < 1:
                keys.add(key)
    return frozenset(keys)


def runtime_adult_rulers(data: PowerData) -> frozenset[str]:
    officeholders = runtime_adult_officeholders(data)
    return frozenset(
        row["ruler"] for row in data.governments.values()
        if row["ruler"] in officeholders
    )


def character_bootstrap(data: PowerData) -> str:
    """Install adult pre-calendar officeholders without invoking succession."""
    characters = {row["key"]: row for row in data.characters}
    keys = (
        "antq_augustus",
        "antq_gaius_caesar",
        "antq_livia",
        "antq_phraates_v",
    )
    if any(key not in characters for key in keys):
        raise ValueError("BCE officeholder bootstrap lacks a required source row")
    varus_key = "antq_publius_quinctilius_varus"
    if varus_key not in characters:
        raise ValueError("Roman officeholder bootstrap lacks the sourced Varus record")
    varus = characters[varus_key]
    lines = [
        "# Generated by tools/m6_power.py --write; adult pre-calendar officeholder adapter.",
        "# Bookmark dates cannot express BCE adult ages; install them before play begins.",
        "on_game_start = {",
        "\ton_actions = { antq_m6_restore_roman_officeholders }",
        "}",
        "",
        "antq_m6_restore_roman_officeholders = {",
        "\teffect = {",
        f"\t\tc:{data.tags['ROM']} = {{",
    ]
    scopes: dict[str, str] = {}

    def append_runtime_character(key: str) -> None:
        row = characters[key]
        if row["birth_date"]:
            birth = BiographyDate.parse(row["birth_date"])
            if birth.year >= 1:
                raise ValueError(f"{key}: runtime bootstrap expects a pre-calendar adult")
            age_range = f"{abs(birth.year)} {abs(birth.year)}"
        else:
            # The source establishes an adult officeholder but deliberately
            # does not invent a precise birth year.  Retain that uncertainty.
            age_range = "25 60"
        scope = f"antq_m6_adult_{key.removeprefix('antq_')}"
        scopes[key] = scope
        lines.extend((
            "\t\t\tcreate_character = {",
            f"\t\t\t\tfirst_name = {key}",
            f"\t\t\t\tculture = culture:{row['culture']}",
            f"\t\t\t\treligion = religion:{row['religion']}",
            f"\t\t\t\tdynasty = dynasty:{row['dynasty']}",
        ))
        if row["birthplace"]:
            lines.append(f"\t\t\t\tbirth_location = location:{row['birthplace']}")
        lines.extend((
            "\t\t\t\testate = estate_type:nobles_estate",
            f"\t\t\t\tage = {{ {age_range} }}",
        ))
        if row["female"] == "yes":
            lines.append("\t\t\t\tfemale = yes")
        lines.extend((
            f"\t\t\t\tsave_scope_as = {scope}",
            "\t\t\t}",
        ))

    for key in ("antq_augustus", "antq_gaius_caesar", "antq_livia"):
        append_runtime_character(key)
    lines.extend((
        f"\t\t\tcharacter:{varus_key} ?= {{ save_scope_as = antq_m6_placeholder_varus }}",
        "\t\t\tkill_character_silently = scope:antq_m6_placeholder_varus",
        "\t\t\t# BM-VAR establishes an adult Roman official, but not a precise birth date.",
        "\t\t\tcreate_character = {",
        f"\t\t\t\tfirst_name = {varus_key}",
        f"\t\t\t\tculture = culture:{varus['culture']}",
        f"\t\t\t\treligion = religion:{varus['religion']}",
        f"\t\t\t\tdynasty = dynasty:{varus['dynasty']}",
        "\t\t\t\tbirth_location = location:rome",
        "\t\t\t\testate = estate_type:nobles_estate",
        "\t\t\t\tage = { 40 55 }",
        "\t\t\t\tsave_scope_as = antq_m6_adult_varus",
        "\t\t\t}",
        "\t\t\tset_variable = { name = antq_teutoburg_varus value = scope:antq_m6_adult_varus }",
        f"\t\t\tset_as_designated_heir = scope:{scopes['antq_gaius_caesar']}",
        f"\t\t\tscope:{scopes['antq_augustus']} = {{",
        f"\t\t\t\tmarry_character = scope:{scopes['antq_livia']}",
        "\t\t\t}",
        f"\t\t\tset_new_ruler_no_update = scope:{scopes['antq_augustus']}",
        "\t\t\tkill_character_silently = character:antq_augustus",
        "\t\t\treset_regency = yes",
        "\t\t}",
        f"\t\tc:{data.tags['PAR']} = {{",
    ))
    append_runtime_character("antq_phraates_v")
    append_runtime_character("antq_musa")
    lines.extend((
        f"\t\t\tscope:{scopes['antq_phraates_v']} = {{",
        f"\t\t\t\tmarry_character = scope:{scopes['antq_musa']}",
        "\t\t\t}",
        f"\t\t\tset_new_ruler_no_update = scope:{scopes['antq_phraates_v']}",
        "\t\t\tkill_character_silently = character:antq_phraates_v",
        "\t\t\tkill_character_silently = character:antq_musa",
        "\t\t\treset_regency = yes",
        "\t\t}",
    ))
    for government in sorted(data.governments.values(), key=lambda row: row["design_tag"]):
        ruler_key = government["ruler"]
        if ruler_key not in runtime_adult_rulers(data) or ruler_key in {
            "antq_augustus", "antq_phraates_v"
        }:
            continue
        tag = data.tags[government["design_tag"]]
        old_ruler_scope = f"antq_m6_old_{government['design_tag'].lower()}_ruler"
        placeholder_scope = f"antq_m6_placeholder_{ruler_key.removeprefix('antq_')}"
        lines.extend((
            f"\t\tc:{tag} = {{",
            f"\t\t\truler ?= {{ save_scope_as = {old_ruler_scope} }}",
            f"\t\t\tcharacter:{ruler_key} ?= {{ save_scope_as = {placeholder_scope} }}",
            f"\t\t\tkill_character_silently = scope:{placeholder_scope}",
        ))
        append_runtime_character(ruler_key)
        consort_key = government["consort"]
        if consort_key in runtime_adult_officeholders(data):
            consort_placeholder = (
                f"antq_m6_placeholder_{consort_key.removeprefix('antq_')}"
            )
            lines.extend((
                f"\t\t\tcharacter:{consort_key} ?= {{ save_scope_as = {consort_placeholder} }}",
                f"\t\t\tkill_character_silently = scope:{consort_placeholder}",
            ))
            append_runtime_character(consort_key)
            lines.extend((
                f"\t\t\tscope:{scopes[ruler_key]} = {{",
                f"\t\t\t\tmarry_character = scope:{scopes[consort_key]}",
                "\t\t\t}",
            ))
        lines.extend((
            # Close the bookmark-generated random ruler's term before
            # installing the sourced adult. Killing it after replacement alone
            # leaves two simultaneously active term records in EU5 1.3.11.
            f"\t\t\tscope:{old_ruler_scope} = {{ remove_ruler = root }}",
            f"\t\t\tset_new_ruler = scope:{scopes[ruler_key]}",
            f"\t\t\tkill_character_silently = scope:{old_ruler_scope}",
            "\t\t}",
        ))

    # Han begins in a sourced regency.  Its BCE-born regent needs the same
    # runtime adult treatment even though he is not the ruler.
    han = data.governments["HAN"]
    regent_key = han["active_regent"]
    regent_placeholder = f"antq_m6_placeholder_{regent_key.removeprefix('antq_')}"
    lines.extend((
        f"\t\tc:{data.tags['HAN']} = {{",
        f"\t\t\tcharacter:{regent_key} ?= {{ save_scope_as = {regent_placeholder} }}",
        f"\t\t\tkill_character_silently = scope:{regent_placeholder}",
    ))
    append_runtime_character(regent_key)
    lines.extend((
        f"\t\t\tset_regent = scope:{scopes[regent_key]}",
        "\t\t}",
        "\t}",
        "}",
        "",
    ))
    return "\n".join(lines)


def character_manager(data: PowerData) -> str:
    """Do not serialize impossible pre-calendar births into the bookmark DB."""
    return "\n".join((
        "# Generated by tools/m6_power.py --write.",
        "# AD 1 cannot encode BCE births in the bookmark calendar; all sourced",
        "# living court characters are created with bounded ages on game start.",
        "character_db = {",
        "}",
        "",
    ))


def character_bootstrap(data: PowerData) -> str:
    """Create the complete sourced living court roster at valid runtime ages."""
    officeholders = runtime_adult_officeholders(data)
    characters_by_tag: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in data.characters:
        characters_by_tag[row["design_tag"]].append(row)
    character_keys = {row["key"] for row in data.characters}
    scopes = {
        key: f"antq_m6_living_{key.removeprefix('antq_')}"
        for key in character_keys
    }
    lines = [
        "# Generated by tools/m6_power.py --write; complete AD 1 living-court bootstrap.",
        "# Exact BCE births retain their sourced opening age. Undated adults and",
        "# court-context people use explicit bounded ranges rather than invented dates.",
        "on_game_start = {",
        "\ton_actions = { antq_m6_create_living_courts }",
        "}",
        "",
        "antq_m6_create_living_courts = {",
        "\teffect = {",
    ]

    def age_range(row: dict[str, str]) -> str:
        if row["birth_date"]:
            birth = BiographyDate.parse(row["birth_date"])
            if birth.year >= 1:
                raise ValueError(f"{row['key']}: bootstrap age expects a BCE birth")
            age = abs(birth.year)
            return f"{age} {age}"
        if row["key"] == "antq_publius_quinctilius_varus":
            # His sourced governorship from 8 BCE establishes an adult Roman
            # official at the bookmark even though the reviewed ledger avoids
            # claiming a disputed exact birth year.  Keep him old enough to be
            # a credible commander throughout the contingent AD 9 chain.
            return "40 55"
        if row["key"] in officeholders:
            return "25 60"
        # The source establishes presence at court, not an exact life stage.
        return "0 65"

    for design_tag in sorted(characters_by_tag):
        tag = data.tags[design_tag]
        lines.append(f"\t\tc:{tag} = {{")
        for row in sorted(characters_by_tag[design_tag], key=lambda item: item["key"]):
            # Rome's engine-created 1 January term is retained as a one-day
            # opening identity carrier below.  Keep the sourced age-63
            # character anonymous until the clean 2 January term handoff so
            # the live court never contains two visible Augustuses.
            first_name = (
                "antq_m6_placeholder_ruler"
                if row["key"] == "antq_augustus"
                else row["key"]
            )
            lines.extend((
                "\t\t\tcreate_character = {",
                f"\t\t\t\tfirst_name = {first_name}",
                f"\t\t\t\tculture = culture:{row['culture']}",
                f"\t\t\t\treligion = religion:{row['religion']}",
                f"\t\t\t\tdynasty = dynasty:{row['dynasty']}",
            ))
            if row["birthplace"]:
                lines.append(f"\t\t\t\tbirth_location = location:{row['birthplace']}")
            if row["key"] in officeholders:
                lines.append("\t\t\t\testate = estate_type:nobles_estate")
            if row["female"] == "yes":
                lines.append("\t\t\t\tfemale = yes")
            lines.extend((
                f"\t\t\t\tage = {{ {age_range(row)} }}",
                f"\t\t\t\tsave_scope_as = {scopes[row['key']]}",
                "\t\t\t}",
            ))
            if row["key"] in HISTORICAL_LIFESPAN_GUARDED:
                lines.extend((
                    f"\t\t\tscope:{scopes[row['key']]} = {{",
                    "\t\t\t\tadd_character_modifier = { modifier = "
                    f"{ROMAN_SUCCESSION_GUARD} years = -1 mode = add_and_extend }}",
                    "\t\t\t}",
                ))

        government = data.governments.get(design_tag)
        if government is not None:
            ruler_key = government["ruler"]
            # Han's securely sourced minor monarch is represented in the ledger
            # as the regency heir rather than a concurrent bookmark ruler.
            if design_tag == "HAN":
                ruler_key = government["heir"]
            if ruler_key and ruler_key != "random":
                lines.extend((
                    "\t\t\tset_variable = { name = antq_m6_opening_ruler "
                    f"value = scope:{scopes[ruler_key]} }}",
                    # A one-day transition is required by the engine's dated
                    # ruler-term container. Replacing a bookmark-generated
                    # ruler on 1.1.1 creates two same-day active terms even
                    # when the old character is retired first.
                    "\t\t\ttrigger_event_silently = { id = antq_m6.1 days = 1 }",
                ))
                if design_tag == "ROM":
                    # EU5 creates a valid current term before on_game_start.
                    # Replacing its holder on the same date produces an
                    # overlapping-term diagnostic.  Instead, make that exact
                    # live holder Augustus for the first playable day, then
                    # hand the office to the sourced age-63 character on the
                    # next date.  This preserves immediate identity, a single
                    # active term, and the historically correct age horizon.
                    augustus = next(
                        row for row in characters_by_tag[design_tag]
                        if row["key"] == "antq_augustus"
                    )
                    lines.extend((
                        "\t\t\truler ?= {",
                        "\t\t\t\tset_first_name = antq_augustus",
                        f"\t\t\t\tchange_character_culture = culture:{augustus['culture']}",
                        f"\t\t\t\tchange_character_religion = religion:{augustus['religion']}",
                        f"\t\t\t\tchange_dynasty = dynasty:{augustus['dynasty']}",
                        "\t\t\t\tchange_character_estate = estate_type:nobles_estate",
                        "\t\t\t\tadd_character_modifier = { modifier = "
                        f"{ROMAN_SUCCESSION_GUARD} years = -1 mode = add_and_extend }}",
                        "\t\t\t}",
                    ))
            heir_key = government["heir"]
            if heir_key and design_tag != "HAN":
                lines.append(
                    f"\t\t\tset_as_designated_heir = scope:{scopes[heir_key]}"
                )
            consort_key = government["consort"]
            if consort_key and ruler_key and ruler_key != "random":
                if design_tag == "ROM":
                    lines.extend((
                        "\t\t\truler ?= {",
                        f"\t\t\t\tmarry_character = scope:{scopes[consort_key]}",
                        "\t\t\t}",
                        "\t\t\tset_variable = { name = antq_m6_opening_consort "
                        f"value = scope:{scopes[consort_key]} }}",
                    ))
                else:
                    lines.extend((
                        f"\t\t\tscope:{scopes[ruler_key]} = {{",
                        f"\t\t\t\tmarry_character = scope:{scopes[consort_key]}",
                        "\t\t\t}",
                    ))
            regent_key = government["active_regent"]
            if regent_key:
                lines.append(f"\t\t\tset_regent = scope:{scopes[regent_key]}")
        if design_tag == "ROM":
            varus = scopes["antq_publius_quinctilius_varus"]
            lines.append(
                f"\t\t\tset_variable = {{ name = antq_teutoburg_varus value = scope:{varus} }}"
            )
            lines.extend((
                "\t\t\tadd_country_modifier = { modifier = antq_augustan_auctoritas years = -1 }",
                "\t\t\trandom_character = {",
                "\t\t\t\tlimit = { is_adult = yes in_cabinet = no NOT = { is_heir = yes } }",
                "\t\t\t\tsave_scope_as = antq_m6_officer_1",
                "\t\t\t}",
                "\t\t\tif = {",
                "\t\t\t\tlimit = { exists = scope:antq_m6_officer_1 }",
                "\t\t\t\tadd_character_to_first_open_cabinet = { target = scope:antq_m6_officer_1 }",
                "\t\t\t}",
                "\t\t\trandom_character = {",
                "\t\t\t\tlimit = { is_adult = yes in_cabinet = no NOT = { is_heir = yes } }",
                "\t\t\t\tsave_scope_as = antq_m6_officer_2",
                "\t\t\t}",
                "\t\t\tif = {",
                "\t\t\t\tlimit = { exists = scope:antq_m6_officer_2 }",
                "\t\t\t\tadd_character_to_first_open_cabinet = { target = scope:antq_m6_officer_2 }",
                "\t\t\t}",
                "\t\t\trandom_character = {",
                "\t\t\t\tlimit = { is_adult = yes in_cabinet = no NOT = { is_heir = yes } }",
                "\t\t\t\tsave_scope_as = antq_m6_officer_3",
                "\t\t\t}",
                "\t\t\tif = {",
                "\t\t\t\tlimit = { exists = scope:antq_m6_officer_3 }",
                "\t\t\t\tadd_character_to_first_open_cabinet = { target = scope:antq_m6_officer_3 }",
                "\t\t\t}",
            ))
            for key in sorted(ROMAN_SUCCESSION_GUARDED):
                if key == "antq_augustus":
                    continue
                short_key = key.removeprefix("antq_")
                lines.append(
                    f"\t\t\tset_variable = {{ name = antq_m6_roman_{short_key} "
                    f"value = scope:{scopes[key]} }}"
                )
        lines.append("\t\t}")
    lines.extend(("\t}", "}", ""))
    return "\n".join(lines)


def ruler_guard_modifier() -> str:
    """Prevent random mortality from corrupting sourced dated character arcs."""
    return "\n".join((
        "# Generated by tools/m6_power.py --write.",
        "# Removed by sourced chronology events; it is never permanent.",
        f"{ROMAN_SUCCESSION_GUARD} = {{",
        "\tis_immortal = yes",
        "}",
        "",
        "antq_augustan_auctoritas = {",
        "\tglobal_crown_estate_power = 0.12",
        "}",
        "",
    ))


def ruler_transition_event() -> str:
    """Install sourced heads and preserve Rome's documented early succession."""
    return "\n".join((
        "namespace = antq_m6",
        "",
        "antq_m6.1 = {",
        "\ttype = country_event",
        "\thidden = yes",
        "\ttitle = empty_text",
        "\timmediate = {",
        "\t\tif = {",
        "\t\t\tlimit = { has_variable = antq_m6_opening_ruler }",
        "\t\t\truler ?= { save_scope_as = antq_m6_departing_ruler }",
        "\t\t\tvar:antq_m6_opening_ruler ?= {",
        "\t\t\t\tsave_scope_as = antq_m6_opening_ruler_scope",
        "\t\t\t}",
        "\t\t\tif = {",
        "\t\t\t\tlimit = { tag = XAA }",
        "\t\t\t\tvar:antq_m6_opening_ruler = {",
        "\t\t\t\t\tset_first_name = antq_augustus",
        "\t\t\t\t}",
        "\t\t\t\tvar:antq_m6_opening_consort ?= {",
        "\t\t\t\t\tsave_scope_as = antq_m6_handoff_consort",
        "\t\t\t\t}",
        "\t\t\t}",
        "\t\t\tif = {",
        "\t\t\t\tlimit = { exists = scope:antq_m6_opening_ruler_scope }",
        "\t\t\t\tset_new_ruler_no_update = scope:antq_m6_opening_ruler_scope",
        "\t\t\t}",
        "\t\t\tif = {",
        "\t\t\t\tlimit = { exists = scope:antq_m6_departing_ruler }",
        "\t\t\t\tkill_character_silently = scope:antq_m6_departing_ruler",
        "\t\t\t}",
        "\t\t\tif = {",
        "\t\t\t\tlimit = {",
        "\t\t\t\t\ttag = XAA",
        "\t\t\t\t\thas_variable = antq_m6_opening_consort",
        "\t\t\t\t}",
        "\t\t\t\tvar:antq_m6_opening_ruler = {",
        "\t\t\t\t\tmarry_character_ignore_blocks = scope:antq_m6_handoff_consort",
        "\t\t\t\t}",
        "\t\t\t}",
        "\t\t\tif = {",
        "\t\t\t\tlimit = { tag = XAA }",
        "\t\t\t\tset_variable = { name = antq_m6_roman_augustus value = var:antq_m6_opening_ruler }",
        "\t\t\t\tremove_variable = antq_m6_opening_consort",
        "\t\t\t}",
        "\t\t\tremove_variable = antq_m6_opening_ruler",
        "\t\t}",
        "\t}",
        "}",
        "",
        "# Gaius Caesar died in AD 4; Tiberius then became Augustus's heir.",
        "antq_m6.2 = {",
        "\ttype = country_event",
        "\thidden = yes",
        "\ttitle = empty_text",
        "\tfire_only_once = yes",
        "\tdynamic_historical_event = {",
        "\t\ttag = XAA",
        "\t\tfrom = 4.2.21",
        "\t\tto = 4.3.21",
        "\t\tmonthly_chance = 100",
        "\t}",
        "\timmediate = {",
        "\t\tif = {",
        "\t\t\tlimit = { has_variable = antq_m6_roman_gaius_caesar }",
        "\t\t\tvar:antq_m6_roman_gaius_caesar = {",
        f"\t\t\t\tremove_character_modifier = {ROMAN_SUCCESSION_GUARD}",
        "\t\t\t\tsave_scope_as = antq_m6_departing_gaius_caesar",
        "\t\t\t}",
        "\t\t\tkill_character_silently = scope:antq_m6_departing_gaius_caesar",
        "\t\t\tremove_variable = antq_m6_roman_gaius_caesar",
        "\t\t}",
        "\t\tif = {",
        "\t\t\tlimit = { has_variable = antq_m6_roman_tiberius }",
        "\t\t\tvar:antq_m6_roman_tiberius = { save_scope_as = antq_m6_tiberius_heir_scope }",
        "\t\t\tset_as_designated_heir = scope:antq_m6_tiberius_heir_scope",
        "\t\t}",
        "\t}",
        "}",
        "",
        "# Augustus died on 19 August AD 14; Tiberius succeeds without a regency.",
        "antq_m6.3 = {",
        "\ttype = country_event",
        "\thidden = yes",
        "\ttitle = empty_text",
        "\tfire_only_once = yes",
        "\tdynamic_historical_event = {",
        "\t\ttag = XAA",
        "\t\tfrom = 14.8.19",
        "\t\tto = 14.9.19",
        "\t\tmonthly_chance = 100",
        "\t}",
        "\timmediate = {",
        "\t\tif = {",
        "\t\t\tlimit = {",
        "\t\t\t\thas_variable = antq_m6_roman_augustus",
        "\t\t\t\thas_variable = antq_m6_roman_tiberius",
        "\t\t\t}",
        "\t\t\tvar:antq_m6_roman_augustus = {",
        f"\t\t\t\tremove_character_modifier = {ROMAN_SUCCESSION_GUARD}",
        "\t\t\t\tsave_scope_as = antq_m6_departing_augustus",
        "\t\t\t}",
        "\t\t\tvar:antq_m6_roman_tiberius = {",
        "\t\t\t\tsave_scope_as = antq_m6_succeeding_tiberius",
        "\t\t\t}",
        "\t\t\tset_new_ruler_no_update = scope:antq_m6_succeeding_tiberius",
        "\t\t\tkill_character_silently = scope:antq_m6_departing_augustus",
        "\t\t\tremove_variable = antq_m6_roman_augustus",
        "\t\t\tcreate_character = {",
        "\t\t\t\tculture = culture:antq_latin",
        "\t\t\t\treligion = religion:antq_religio_romana",
        "\t\t\t\tdynasty = dynasty:antq_julio_claudian_dynasty",
        "\t\t\t\testate = estate_type:nobles_estate",
        "\t\t\t\tage = { 20 30 }",
        "\t\t\t\tsave_scope_as = antq_m6_roman_succession_reserve_scope",
        "\t\t\t}",
        "\t\t\tscope:antq_m6_roman_succession_reserve_scope = {",
        f"\t\t\t\tadd_character_modifier = {{ modifier = {ROMAN_SUCCESSION_GUARD} years = -1 mode = add_and_extend }}",
        "\t\t\t}",
        "\t\t\tset_variable = { name = antq_m6_roman_succession_reserve value = scope:antq_m6_roman_succession_reserve_scope }",
        "\t\t\tset_as_designated_heir = scope:antq_m6_roman_succession_reserve_scope",
        "\t\t}",
        "\t\tif = {",
        "\t\t\tlimit = { has_variable = antq_m6_roman_livia }",
        "\t\t\tvar:antq_m6_roman_livia = {",
        f"\t\t\t\tremove_character_modifier = {ROMAN_SUCCESSION_GUARD}",
        "\t\t\t}",
        "\t\t\tremove_variable = antq_m6_roman_livia",
        "\t\t}",
        "\t}",
        "}",
        "",
    ))


def government_block(
    row: dict[str, str], current_term: dict[str, str] | None = None,
    runtime_rulers: frozenset[str] = frozenset({"antq_augustus", "antq_phraates_v"}),
) -> list[str]:
    lines = [
        "\t\t\tgovernment = {",
        f"\t\t\t\ttype = {row['government_type']}",
        f"\t\t\t\their_selection = {row['heir_selection']}",
        "\t\t\t\tparliament = {",
        "\t\t\t\t\tparliament_type = "
        + PARLIAMENT_BY_REFORM.get(
            row["reform"],
            "antq_tribal_assembly"
            if row["government_type"] == "tribe"
            else "antq_royal_council",
        ),
        "\t\t\t\t}",
    ]
    runtime_named_ruler = row["ruler"] in runtime_rulers
    if runtime_named_ruler or row["regency"]:
        lines.append("\t\t\t\truler = random")
    elif row["ruler"]:
        lines.append(f"\t\t\t\truler = {row['ruler']}")

    def append_field(field: str) -> None:
        if row[field]:
            value = (
                AntqDate.parse(row[field]).engine()
                if field in {"start_regency_date", "end_regency_date"}
                else row[field]
            )
            lines.append(f"\t\t\t\t{field} = {value}")

    # Every named officeholder is installed by the runtime court bootstrap;
    # bookmark references would resolve to impossible age-zero BCE records.
    lines.extend((
        "\t\t\t\treforms = {",
        f"\t\t\t\t\t{row['reform']}",
        "\t\t\t\t}",
    ))
    lines.append("\t\t\t\tprivilege = {")
    lines.extend(f"\t\t\t\t\t{privilege}" for privilege in pipe_values(row["privileges"], "government privileges"))
    lines.append("\t\t\t\t}")
    # M8 gives every exact legal profile its own already-researched Age-I
    # foundation. Install the complete fourteen-question ancient profile here;
    # holder potentials and isolated unlocks keep foreign law systems invisible.
    profile_laws = s2_starting_laws_by_tag()[row["design_tag"]]
    lines.append("\t\t\t\tlaws = {")
    lines.extend((
        "\t\t\t\t\tmarriage_law = monogamous_marriage",
        "\t\t\t\t\their_religion_law = heir_same_religion",
    ))
    lines.extend(
        f"\t\t\t\t\t{law} = {option}"
        for law, option in profile_laws
    )
    lines.append("\t\t\t\t}")
    lines.extend(f"\t\t\t\t{key} = {value}" for key, value in assignments(row["societal_values"], "government societal values"))
    lines.append("\t\t\t}")
    return lines


def apply_ancient_subsistence_floor(rendered: str) -> str:
    """Give every ancient government the same small subsistence adapter.

    Runtime province ledgers showed natural food balances missing break-even
    by roughly ten percent after the opening reserves drained.  XEQ's seven
    provinces, for example, carried a 46.7-unit structural deficit against
    495.6 units of consumption in AD 3; a first three-percent candidate reduced
    the deficit to 32.9 but still made minimum provisioning cost the state its
    whole tax income.  Ten percent closes that measured engine-granularity gap
    while leaving climate, goods, RGOs, government bonuses, and policy
    differences responsible for all food beyond the common floor.
    """
    lines = rendered.splitlines()
    output: list[str] = []
    depth = 0
    in_modifier = False
    modifier_count = 0
    adapted_count = 0
    saw_food = False
    original_food_value: float | None = None
    food_line = re.compile(
        r"^(?P<indent>\s*)global_monthly_food_modifier\s*=\s*"
        r"(?P<value>[0-9]+(?:\.[0-9]+)?)\s*$"
    )
    for line in lines:
        before = depth
        stripped = line.strip()
        if not in_modifier and before == 1 and stripped == "country_modifier = {":
            in_modifier = True
            modifier_count += 1
            saw_food = False
            original_food_value = None
        elif in_modifier and before == 2:
            match = food_line.match(line)
            if match:
                existing = float(match.group("value"))
                if original_food_value is not None:
                    if abs(existing - original_food_value) > 1e-9:
                        raise ValueError(
                            "government reform has conflicting direct food modifiers"
                        )
                    # Political-contract and historical-profile data sometimes
                    # repeat the same modifier. Collapse that pre-existing
                    # duplicate so the engine receives one unambiguous value.
                    continue
                original_food_value = existing
                value = existing + ANCIENT_SUBSISTENCE_FOOD_FLOOR
                line = (
                    f"{match.group('indent')}global_monthly_food_modifier = "
                    f"{value:.3f}"
                )
                saw_food = True
                adapted_count += 1
            elif stripped == "}":
                if not saw_food:
                    output.append(
                        "\t\tglobal_monthly_food_modifier = "
                        f"{ANCIENT_SUBSISTENCE_FOOD_FLOOR:.3f}"
                    )
                    adapted_count += 1
                in_modifier = False
        output.append(line)
        depth += line.count("{") - line.count("}")
        if depth < 0:
            raise ValueError("government reform brace depth became negative")
    if depth != 0 or in_modifier:
        raise ValueError("government reform subsistence pass ended inside a block")
    if modifier_count == 0 or adapted_count != modifier_count:
        raise ValueError(
            "government reform subsistence coverage drift: "
            f"{adapted_count}/{modifier_count}"
        )
    return "\n".join(output)


def reforms(data: PowerData) -> str:
    rendered = """# Generated by tools/m6_power.py --write; M6 historical government adapters.
# These retain the five locally installed government types and use only local modifier keys.
# Flat research represents the institutions that transmit practical knowledge;
# literacy remains a separate population process and scales it further.
antq_principate = {
	major = yes
	government = monarchy
	country_modifier = {
		cultures_capacity = 10
		monthly_towards_centralization = societal_value_monthly_move
		global_monthly_control = 0.0005
		global_trade_through_owned_territory_efficiency = 0.03
		nobles_estate_max_tax = 0.02
		burghers_estate_max_tax = 0.03
		research_speed = 0.15
	}
	years = 2
}

antq_dominate = {
	major = yes
	government = monarchy
	country_modifier = {
		global_crown_estate_power = 0.15
		monthly_towards_centralization = societal_value_monthly_move
		country_cabinet_efficiency = 0.025
		research_speed = 0.15
	}
	years = 2
}

antq_han_imperial_bureaucracy = {
	major = yes
	government = monarchy
	country_modifier = {
		cultures_capacity = 8
		monthly_legitimacy = 0.05
		monthly_towards_centralization = societal_value_monthly_move
		monthly_towards_innovative = societal_value_monthly_move
		research_speed = 0.15
	}
	years = 2
}

antq_lankan_kingdom = {
	major = yes
	government = monarchy
	country_modifier = {
		global_crown_estate_power = 0.05
		country_cabinet_efficiency = 0.025
		research_speed = 0.10
	}
	years = 2
}

antq_indian_ganasangha = {
	major = yes
	government = republic
	country_modifier = {
		monthly_republican_tradition = 0.05
		global_nobles_estate_power = 0.05
		research_speed = 0.10
	}
	years = 2
}

antq_indo_scythian_kingship = {
	major = yes
	government = monarchy
	country_modifier = {
		cultures_capacity = 3
		global_nobles_estate_power = 0.05
		land_morale_modifier = 0.025
		research_speed = 0.10
	}
	years = 2
}

antq_indo_greek_kingship = {
	major = yes
	government = monarchy
	country_modifier = {
		global_burghers_estate_power = 0.05
		country_cabinet_efficiency = 0.025
		research_speed = 0.10
	}
	years = 2
}

antq_parthian_king_of_kings = {
	major = yes
	government = monarchy
	country_modifier = {
		cultures_capacity = 3
		global_nobles_estate_power = 0.15
		monthly_towards_decentralization = societal_value_monthly_move
		research_speed = 0.15
	}
	years = 2
}

antq_sassanid_centralized_monarchy = {
	major = yes
	government = monarchy
	country_modifier = {
		global_crown_estate_power = 0.15
		monthly_towards_centralization = societal_value_monthly_move
		land_morale_modifier = 0.025
		research_speed = 0.15
	}
	years = 2
}

antq_client_monarchy = {
	major = yes
	government = monarchy
	country_modifier = {
		global_crown_estate_power = 0.05
		monthly_towards_centralization = societal_value_minor_monthly_move
		research_speed = 0.08
	}
	years = 2
}

antq_parthian_subkingdom = {
	major = yes
	government = monarchy
	country_modifier = {
		global_nobles_estate_power = 0.10
		monthly_towards_decentralization = societal_value_minor_monthly_move
		research_speed = 0.08
	}
	years = 2
}

antq_arian_satrapal_court = {
	major = yes
	government = monarchy
	country_modifier = {
		global_nobles_estate_power = 0.05
		global_trade_through_owned_territory_efficiency = 0.03
		research_speed = 0.09
	}
	years = 2
}

antq_kangju_confederated_kingship = {
	major = yes
	government = monarchy
	country_modifier = {
		global_tribes_estate_power = 0.08
		monthly_towards_decentralization = societal_value_minor_monthly_move
		research_speed = 0.08
	}
	years = 2
}

antq_sogdian_city_compact = {
	major = yes
	government = monarchy
	country_modifier = {
		global_burghers_estate_power = 0.08
		global_trade_through_owned_territory_efficiency = 0.04
		research_speed = 0.10
	}
	years = 2
}

antq_dayuan_oasis_kingship = {
	major = yes
	government = monarchy
	country_modifier = {
		global_burghers_estate_power = 0.05
		global_production_efficiency = 0.025
		research_speed = 0.09
	}
	years = 2
}

antq_wusun_kunmi_confederacy = {
	major = yes
	government = monarchy
	country_modifier = {
		global_tribes_estate_power = 0.08
		land_morale_modifier = 0.025
		research_speed = 0.08
	}
	years = 2
}

antq_yuezhi_five_yabghus = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.07
		land_morale_modifier = 0.025
		research_speed = 0.08
	}
	years = 2
}

antq_han_western_regions_kingship = {
	major = yes
	government = monarchy
	country_modifier = {
		global_burghers_estate_power = 0.05
		global_trade_through_owned_territory_efficiency = 0.025
		research_speed = 0.09
	}
	years = 2
}

antq_yancai_aorsi_confederacy = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.10
		land_morale_modifier = 0.02
		research_speed = 0.07
	}
	years = 2
}

antq_saryarka_late_iron_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.10
		global_monthly_food_modifier = 0.02
		research_speed = 0.06
	}
	years = 2
}

antq_altai_contact_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.10
		global_trade_through_owned_territory_efficiency = 0.02
		research_speed = 0.06
	}
	years = 2
}

antq_zhangzhung_plateau_kingship = {
	major = yes
	government = monarchy
	country_modifier = {
		global_nobles_estate_power = 0.06
		global_monthly_food_modifier = 0.015
		research_speed = 0.08
	}
	years = 2
}

antq_sumpa_highland_confederacy = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.10
		global_trade_through_owned_territory_efficiency = 0.015
		research_speed = 0.07
	}
	years = 2
}

antq_changtang_pastoral_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.11
		global_monthly_food_modifier = 0.025
		research_speed = 0.06
	}
	years = 2
}

antq_central_plateau_agropastoral_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_peasants_estate_power = 0.06
		global_production_efficiency = 0.025
		research_speed = 0.07
	}
	years = 2
}

antq_eastern_plateau_corridor_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.10
		global_trade_through_owned_territory_efficiency = 0.025
		research_speed = 0.07
	}
	years = 2
}

antq_tamilakam_velir_court = {
	major = yes
	government = monarchy
	country_modifier = {
		global_nobles_estate_power = 0.08
		global_trade_through_owned_territory_efficiency = 0.02
		research_speed = 0.09
	}
	years = 2
}

antq_central_indian_urban_kingship = {
	major = yes
	government = monarchy
	country_modifier = {
		global_burghers_estate_power = 0.08
		global_production_efficiency = 0.02
		research_speed = 0.09
	}
	years = 2
}

antq_central_indian_janapada = {
	major = yes
	government = monarchy
	country_modifier = {
		global_nobles_estate_power = 0.07
		global_monthly_food_modifier = 0.015
		research_speed = 0.08
	}
	years = 2
}

antq_central_indian_megalithic_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.10
		global_production_efficiency = 0.02
		research_speed = 0.07
	}
	years = 2
}

antq_upper_mahanadi_kingship = {
	major = yes
	government = monarchy
	country_modifier = {
		global_peasants_estate_power = 0.07
		global_monthly_food_modifier = 0.02
		research_speed = 0.08
	}
	years = 2
}

antq_indian_ocean_atoll_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_burghers_estate_power = 0.06
		global_trade_through_owned_territory_efficiency = 0.03
		research_speed = 0.07
	}
	years = 2
}

antq_mainland_river_corridor_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.08
		global_trade_through_owned_territory_efficiency = 0.025
		research_speed = 0.07
	}
	years = 2
}

antq_sa_huynh_exchange_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_burghers_estate_power = 0.06
		global_trade_through_owned_territory_efficiency = 0.03
		research_speed = 0.07
	}
	years = 2
}

antq_mainland_highland_exchange_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.10
		global_trade_through_owned_territory_efficiency = 0.02
		research_speed = 0.07
	}
	years = 2
}

antq_mainland_iron_age_basin_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_peasants_estate_power = 0.07
		global_monthly_food_modifier = 0.02
		research_speed = 0.07
	}
	years = 2
}

antq_amur_forest_river_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.10
		global_trade_through_owned_territory_efficiency = 0.02
		research_speed = 0.07
	}
	years = 2
}

antq_sakhalin_maritime_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.09
		global_trade_through_owned_territory_efficiency = 0.025
		research_speed = 0.07
	}
	years = 2
}

antq_ussuri_poltsian_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_peasants_estate_power = 0.06
		global_monthly_food_modifier = 0.02
		research_speed = 0.07
	}
	years = 2
}

antq_northern_okjeo_corridor = {
	major = yes
	government = tribe
	country_modifier = {
		global_burghers_estate_power = 0.05
		global_trade_through_owned_territory_efficiency = 0.025
		research_speed = 0.07
	}
	years = 2
}

antq_borneo_cave_river_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.10
		global_trade_through_owned_territory_efficiency = 0.02
		research_speed = 0.07
	}
	years = 2
}

antq_borneo_coastal_exchange_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_burghers_estate_power = 0.06
		global_trade_through_owned_territory_efficiency = 0.03
		research_speed = 0.07
	}
	years = 2
}

antq_borneo_interior_river_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.10
		global_trade_through_owned_territory_efficiency = 0.02
		research_speed = 0.07
	}
	years = 2
}

antq_borneo_foothill_iron_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_peasants_estate_power = 0.06
		global_monthly_food_modifier = 0.02
		research_speed = 0.07
	}
	years = 2
}

antq_philippine_coastal_river_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.08
		global_trade_through_owned_territory_efficiency = 0.025
		research_speed = 0.07
	}
	years = 2
}

antq_philippine_mortuary_community_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_clergy_estate_power = 0.06
		global_monthly_food_modifier = 0.02
		research_speed = 0.07
	}
	years = 2
}

antq_philippine_island_exchange_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_burghers_estate_power = 0.06
		global_trade_through_owned_territory_efficiency = 0.03
		research_speed = 0.07
	}
	years = 2
}

antq_philippine_cave_coast_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.09
		global_trade_through_owned_territory_efficiency = 0.02
		research_speed = 0.07
	}
	years = 2
}

antq_sulawesi_coastal_exchange_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.075
		global_trade_through_owned_territory_efficiency = 0.028
		research_speed = 0.07
	}
	years = 2
}

antq_sulawesi_island_exchange_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_burghers_estate_power = 0.065
		global_trade_through_owned_territory_efficiency = 0.032
		research_speed = 0.07
	}
	years = 2
}

antq_sulawesi_highland_mortuary_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_clergy_estate_power = 0.065
		global_monthly_food_modifier = 0.022
		research_speed = 0.07
	}
	years = 2
}

antq_sulawesi_river_lake_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.085
		global_monthly_food_modifier = 0.024
		research_speed = 0.07
	}
	years = 2
}

antq_sulawesi_peninsula_community_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.09
		global_trade_through_owned_territory_efficiency = 0.024
		research_speed = 0.07
	}
	years = 2
}

antq_north_maluku_metal_age_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_burghers_estate_power = 0.07
		global_trade_through_owned_territory_efficiency = 0.035
		research_speed = 0.07
	}
	years = 2
}

antq_point_peninsula_seasonal_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.083
		global_monthly_food_modifier = 0.021
		research_speed = 0.07
	}
	years = 2
}

antq_havana_hopewell_exchange_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_clergy_estate_power = 0.057
		global_trade_through_owned_territory_efficiency = 0.031
		research_speed = 0.075
	}
	years = 2
}

antq_central_mississippi_woodland_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.087
		global_monthly_food_modifier = 0.023
		research_speed = 0.07
	}
	years = 2
}

antq_kansas_city_hopewell_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_burghers_estate_power = 0.063
		global_trade_through_owned_territory_efficiency = 0.029
		research_speed = 0.07
	}
	years = 2
}

antq_mahan_small_state_league = {
	major = yes
	government = tribe
	country_modifier = {
		global_peasants_estate_power = 0.059
		global_monthly_food_modifier = 0.024
		research_speed = 0.075
	}
	years = 2
}

antq_jinhan_small_state_league = {
	major = yes
	government = tribe
	country_modifier = {
		global_burghers_estate_power = 0.057
		global_trade_through_owned_territory_efficiency = 0.027
		research_speed = 0.075
	}
	years = 2
}

antq_byeonhan_iron_exchange_league = {
	major = yes
	government = tribe
	country_modifier = {
		global_burghers_estate_power = 0.073
		global_trade_through_owned_territory_efficiency = 0.035
		research_speed = 0.075
	}
	years = 2
}

antq_soanian_king_and_council = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.083
		global_nobles_estate_power = 0.067
		country_cabinet_efficiency = 0.03
		research_speed = 0.075
	}
	years = 2
}

antq_andean_irrigated_valley_network = {
	major = yes
	government = tribe
	country_modifier = {
		research_speed = 0.075
	}
	years = 2
}

antq_andean_highland_community_network = {
	major = yes
	government = tribe
	country_modifier = {
		research_speed = 0.075
	}
	years = 2
}

antq_andean_ceremonial_centre_network = {
	major = yes
	government = tribe
	country_modifier = {
		research_speed = 0.09
	}
	years = 2
}

antq_wankarani_mound_village_network = {
	major = yes
	government = tribe
	country_modifier = {
		research_speed = 0.075
	}
	years = 2
}

antq_herrera_plateau_exchange_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_peasants_estate_power = 0.073
		global_burghers_estate_power = 0.057
		global_monthly_food_modifier = 0.021
		global_trade_through_owned_territory_efficiency = 0.025
		research_speed = 0.075
	}
	years = 2
}

antq_sierra_nevada_early_community_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.083
		global_peasants_estate_power = 0.061
		global_monthly_food_modifier = 0.018
		research_speed = 0.07
	}
	years = 2
}

antq_loja_regional_development_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_peasants_estate_power = 0.071
		global_tribes_estate_power = 0.067
		global_monthly_food_modifier = 0.020
		global_trade_through_owned_territory_efficiency = 0.023
		research_speed = 0.075
	}
	years = 2
}

antq_daga_highland_garden_network = {
	major = yes
	government = tribe
	country_modifier = {
		research_speed = 0.065
	}
	years = 2
}

antq_bomberai_coastal_community_network = {
	major = yes
	government = tribe
	country_modifier = {
		research_speed = 0.065
	}
	years = 2
}

antq_early_mariana_island_network = {
	major = yes
	government = tribe
	country_modifier = {
		research_speed = 0.07
	}
	years = 2
}

antq_yap_ulithi_island_network = {
	major = yes
	government = tribe
	country_modifier = {
		research_speed = 0.07
	}
	years = 2
}

antq_orinoco_llanos_ceramic_network = {
	major = yes
	government = tribe
	country_modifier = {
		research_speed = 0.07
	}
	years = 2
}

antq_windward_island_ceramic_network = {
	major = yes
	government = tribe
	country_modifier = {
		research_speed = 0.07
	}
	years = 2
}

antq_central_california_coastal_network = {
	major = yes
	government = tribe
	country_modifier = {
		research_speed = 0.065
	}
	years = 2
}

antq_acutuba_central_amazon_network = {
	major = yes
	government = tribe
	country_modifier = {
		research_speed = 0.075
	}
	years = 2
}

antq_mesoamerican_urban_ritual_center = {
	major = yes
	government = tribe
	country_modifier = {
		global_clergy_estate_power = 0.10
		global_burghers_estate_power = 0.07
		global_production_efficiency = 0.025
		research_speed = 0.09
	}
	years = 2
}

antq_mesoamerican_formative_civic_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_clergy_estate_power = 0.07
		global_peasants_estate_power = 0.06
		global_monthly_food_modifier = 0.02
		research_speed = 0.075
	}
	years = 2
}

antq_mesoamerican_exchange_corridor_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.08
		global_burghers_estate_power = 0.06
		global_trade_through_owned_territory_efficiency = 0.03
		research_speed = 0.07
	}
	years = 2
}

antq_mesoamerican_highland_community_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.10
		global_peasants_estate_power = 0.06
		global_monthly_food_modifier = 0.02
		research_speed = 0.065
	}
	years = 2
}

antq_west_mexican_shaft_tomb_chiefdom = {
	major = yes
	government = tribe
	country_modifier = {
		global_clergy_estate_power = 0.09
		global_nobles_estate_power = 0.06
		global_production_efficiency = 0.02
		research_speed = 0.075
	}
	years = 2
}

antq_teuchitlan_civic_center_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_clergy_estate_power = 0.08
		global_burghers_estate_power = 0.07
		global_trade_through_owned_territory_efficiency = 0.025
		research_speed = 0.08
	}
	years = 2
}

antq_west_mexican_basin_community_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.08
		global_peasants_estate_power = 0.07
		global_monthly_food_modifier = 0.02
		research_speed = 0.07
	}
	years = 2
}

antq_west_mexican_highland_corridor_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.09
		global_burghers_estate_power = 0.05
		global_trade_through_owned_territory_efficiency = 0.025
		research_speed = 0.065
	}
	years = 2
}

antq_sonoran_desert_farming_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.08
		global_peasants_estate_power = 0.08
		global_monthly_food_modifier = 0.025
		research_speed = 0.065
	}
	years = 2
}

antq_buffer_kingdom = {
	major = yes
	government = monarchy
	country_modifier = {
		global_nobles_estate_power = 0.05
		country_cabinet_efficiency = 0.025
		research_speed = 0.08
	}
	years = 2
}

antq_kushite_dual_kingship = {
	major = yes
	government = monarchy
	country_modifier = {
		global_crown_estate_power = 0.05
		country_cabinet_efficiency = 0.025
		research_speed = 0.10
	}
	years = 2
}

antq_steppe_confederation = {
	major = yes
	government = steppe_horde
	country_modifier = {
		global_tribes_estate_power = 0.10
		monthly_towards_decentralization = societal_value_monthly_move
		research_speed = 0.06
	}
	years = 2
}

antq_xianbei_eastern_confederacy = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.08
		country_cabinet_efficiency = 0.025
		research_speed = 0.07
	}
	years = 2
}

antq_early_korean_kingdom = {
	major = yes
	government = monarchy
	country_modifier = {
		global_nobles_estate_power = 0.05
		country_cabinet_efficiency = 0.025
		research_speed = 0.10
	}
	years = 2
}

antq_regional_kingship = {
	major = yes
	government = monarchy
	country_modifier = {
		global_crown_estate_power = 0.05
		country_cabinet_efficiency = 0.025
		research_speed = 0.10
	}
	years = 2
}

antq_advanced_chiefdom = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.05
		country_cabinet_efficiency = 0.025
		research_speed = 0.06
	}
	years = 2
}

antq_northern_indian_coin_kingship = {
	major = yes
	government = monarchy
	country_modifier = {
		global_nobles_estate_power = 0.06
		global_burghers_estate_power = 0.05
		country_cabinet_efficiency = 0.025
		research_speed = 0.10
	}
	years = 2
}

antq_pundranagara_urban_kingship = {
	major = yes
	government = monarchy
	country_modifier = {
		global_burghers_estate_power = 0.08
		global_trade_through_owned_territory_efficiency = 0.03
		research_speed = 0.09
	}
	years = 2
}

antq_bengal_riverine_community_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.06
		global_burghers_estate_power = 0.05
		global_trade_through_owned_territory_efficiency = 0.03
		research_speed = 0.07
	}
	years = 2
}

antq_eastern_megalithic_community_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.08
		global_peasants_estate_power = 0.06
		global_production_efficiency = 0.025
		research_speed = 0.065
	}
	years = 2
}

antq_eastern_hill_valley_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.09
		global_monthly_food_modifier = 0.02
		country_cabinet_efficiency = 0.02
		research_speed = 0.06
	}
	years = 2
}

antq_himalayan_highland_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.10
		global_monthly_control = 0.02
		monthly_towards_decentralization = societal_value_minor_monthly_move
		research_speed = 0.06
	}
	years = 2
}

antq_far_side_port_chiefdom = {
	major = yes
	government = tribe
	country_modifier = {
		global_burghers_estate_power = 0.08
		global_tribes_estate_power = 0.05
		global_trade_through_owned_territory_efficiency = 0.04
		research_speed = 0.08
	}
	years = 2
}

antq_horn_pastoral_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.10
		monthly_towards_decentralization = societal_value_minor_monthly_move
		global_trade_through_owned_territory_efficiency = 0.025
		research_speed = 0.06
	}
	years = 2
}

antq_west_african_savanna_compound_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.08
		global_peasants_estate_power = 0.08
		global_monthly_food_modifier = 0.025
		research_speed = 0.065
	}
	years = 2
}

antq_west_african_ironworking_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.06
		global_peasants_estate_power = 0.06
		global_production_efficiency = 0.035
		research_speed = 0.07
	}
	years = 2
}

antq_west_african_forest_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.09
		global_peasants_estate_power = 0.05
		monthly_towards_decentralization = societal_value_minor_monthly_move
		research_speed = 0.06
	}
	years = 2
}

antq_early_ironworking_community_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.07
		global_peasants_estate_power = 0.07
		global_production_efficiency = 0.025
		research_speed = 0.07
	}
	years = 2
}

antq_mobile_hunter_herder_network = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.12
		monthly_towards_decentralization = societal_value_minor_monthly_move
		global_trade_through_owned_territory_efficiency = 0.02
		research_speed = 0.05
	}
	years = 2
}

antq_settled_town_cluster = {
	major = yes
	government = republic
	country_modifier = {
		global_burghers_estate_power = 0.05
		country_cabinet_efficiency = 0.025
		research_speed = 0.10
	}
	years = 2
}

antq_tribal_kingdom = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.10
		monthly_towards_decentralization = societal_value_minor_monthly_move
		research_speed = 0.06
	}
	years = 2
}

antq_artaxiad_highland_kingship = {
	major = yes
	government = monarchy
	country_modifier = {
		global_nobles_estate_power = 0.08
		country_cabinet_efficiency = 0.025
		research_speed = 0.10
	}
	years = 2
}

antq_nabataean_caravan_kingship = {
	major = yes
	government = monarchy
	country_modifier = {
		global_burghers_estate_power = 0.08
		global_trade_through_owned_territory_efficiency = 0.04
		research_speed = 0.10
	}
	years = 2
}

antq_himyarite_terrace_kingship = {
	major = yes
	government = monarchy
	country_modifier = {
		global_peasants_estate_power = 0.08
		global_pop_food_consumption = -0.01
		research_speed = 0.10
	}
	years = 2
}

antq_satavahana_deccan_kingship = {
	major = yes
	government = monarchy
	country_modifier = {
		global_nobles_estate_power = 0.05
		global_burghers_estate_power = 0.05
		research_speed = 0.10
	}
	years = 2
}

antq_catuvellaunian_oppidum_kingship = {
	major = yes
	government = tribe
	country_modifier = {
		global_nobles_estate_power = 0.08
		global_burghers_estate_power = 0.04
		research_speed = 0.08
	}
	years = 2
}

antq_trinovantian_coin_kingship = {
	major = yes
	government = tribe
	country_modifier = {
		global_nobles_estate_power = 0.07
		global_burghers_estate_power = 0.05
		research_speed = 0.08
	}
	years = 2
}

antq_brigantian_hillfort_confederacy = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.08
		global_levy_size_modifier = 0.025
		research_speed = 0.07
	}
	years = 2
}

antq_durotrigian_hillfort_coin_order = {
	major = yes
	government = tribe
	country_modifier = {
		global_burghers_estate_power = 0.07
		global_production_efficiency = 0.025
		research_speed = 0.08
	}
	years = 2
}

antq_ivernian_regional_assembly = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.09
		monthly_towards_decentralization = societal_value_minor_monthly_move
		research_speed = 0.07
	}
	years = 2
}

antq_aestian_amber_coast_order = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.08
		global_trade_through_owned_territory_efficiency = 0.025
		research_speed = 0.07
	}
	years = 2
}

antq_frisian_terp_community_order = {
	major = yes
	government = tribe
	country_modifier = {
		global_peasants_estate_power = 0.07
		global_road_building_time = -0.04
		research_speed = 0.07
	}
	years = 2
}

antq_dacian_divided_kingships = {
	major = yes
	government = tribe
	country_modifier = {
		global_nobles_estate_power = 0.08
		global_levy_size_modifier = 0.025
		research_speed = 0.08
	}
	years = 2
}

antq_garamantian_oasis_state = {
	major = yes
	government = monarchy
	country_modifier = {
		global_burghers_estate_power = 0.07
		global_production_efficiency = 0.025
		research_speed = 0.08
	}
	years = 2
}

antq_marcomannic_bohemian_kingship = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.08
		global_nobles_estate_power = 0.06
		research_speed = 0.08
	}
	years = 2
}

antq_cheruscan_kindred_assembly = {
	major = yes
	government = tribe
	country_modifier = {
		global_tribes_estate_power = 0.07
		country_cabinet_efficiency = 0.02
		research_speed = 0.07
	}
	years = 2
}

antq_chattian_host_order = {
	major = yes
	government = tribe
	country_modifier = {
		global_nobles_estate_power = 0.07
		global_levy_size_modifier = 0.03
		research_speed = 0.07
	}
	years = 2
}

antq_batavian_rhine_compact = {
	major = yes
	government = tribe
	country_modifier = {
		global_nobles_estate_power = 0.06
		country_cabinet_efficiency = 0.025
		research_speed = 0.08
	}
	years = 2
}

antq_semnonian_sacred_confederacy = {
	major = yes
	government = tribe
	country_modifier = {
		global_clergy_estate_power = 0.08
		stability_cost_efficiency = -0.03
		research_speed = 0.07
	}
	years = 2
}

antq_sabaean_marib_kingship = {
	major = yes
	government = monarchy
	country_modifier = {
		global_peasants_estate_power = 0.08
		global_pop_food_consumption = -0.01
		research_speed = 0.10
	}
	years = 2
}

antq_mauretanian_client_kingship = {
	major = yes
	government = monarchy
	country_modifier = {
		global_nobles_estate_power = 0.05
		global_burghers_estate_power = 0.05
		research_speed = 0.10
	}
	years = 2
}

antq_herodian_judean_ethnarchy = {
	major = yes
	government = monarchy
	country_modifier = {
		global_clergy_estate_power = 0.08
		global_nobles_estate_power = 0.05
		research_speed = 0.10
	}
	years = 2
}

antq_cappadocian_client_kingship = {
	major = yes
	government = monarchy
	country_modifier = {
		cultures_capacity = 2
		global_nobles_estate_power = 0.06
		global_burghers_estate_power = 0.04
		research_speed = 0.10
	}
	years = 2
}

antq_odrysian_client_kingship = {
	major = yes
	government = monarchy
	country_modifier = {
		global_nobles_estate_power = 0.07
		global_tribes_estate_power = 0.06
		research_speed = 0.10
	}
	years = 2
}

antq_bosporan_client_kingship = {
	major = yes
	government = monarchy
	country_modifier = {
		global_burghers_estate_power = 0.07
		global_nobles_estate_power = 0.05
		research_speed = 0.10
	}
	years = 2
}

antq_herodian_galilean_tetrarchy = {
	major = yes
	government = monarchy
	country_modifier = {
		global_burghers_estate_power = 0.07
		global_nobles_estate_power = 0.04
		research_speed = 0.10
	}
	years = 2
}

antq_herodian_batanean_tetrarchy = {
	major = yes
	government = monarchy
	country_modifier = {
		global_tribes_estate_power = 0.07
		global_nobles_estate_power = 0.05
		research_speed = 0.10
	}
	years = 2
}

antq_commagenean_client_kingship = {
	major = yes
	government = monarchy
	country_modifier = {
		cultures_capacity = 2
		global_nobles_estate_power = 0.07
		global_clergy_estate_power = 0.05
		research_speed = 0.10
	}
	years = 2
}

antq_emesan_client_dynasty = {
	major = yes
	government = monarchy
	country_modifier = {
		global_clergy_estate_power = 0.07
		global_burghers_estate_power = 0.05
		research_speed = 0.10
	}
	years = 2
}
"""
    parliament_by_reform = {
        reform: PROFILE_PARLIAMENTS[profile]
        for profile, reforms_for_profile in PROFILE_BASE_REFORMS.items()
        for reform in reforms_for_profile
    }
    holders_by_reform: dict[str, set[str]] = {}
    for government in data.governments.values():
        holders_by_reform.setdefault(government["reform"], set()).add(
            data.tags[government["design_tag"]]
        )
    with POLITIES.open(encoding="utf-8-sig", newline="") as handle:
        for polity in csv.DictReader(handle):
            if polity["tag"] in data.governments:
                continue
            fallback = (
                "antq_advanced_chiefdom"
                if polity["kind"] == "sop"
                else "antq_regional_kingship"
            )
            holders_by_reform.setdefault(fallback, set()).add(data.tags[polity["tag"]])
    # Explicit future-state bridges retain the same historical polity without
    # opening a Roman or Han successor constitution to every monarchy.
    holders_by_reform.setdefault("antq_dominate", set()).add(data.tags["ROM"])
    path_rows = reform_path_rows()
    alternatives_by_profile = {
        profile: tuple(row[0] for row in path_rows if row[1] == profile)
        for profile in PROFILE_BASE_REFORMS
    }
    for reform, parliament in parliament_by_reform.items():
        start = rendered.index(f"{reform} = {{")
        end = rendered.index("\n}\n", start)
        block = rendered[start:end]
        modifier_anchor = "\tcountry_modifier = {\n"
        if modifier_anchor not in block:
            raise ValueError(f"government reform {reform} lost its modifier anchor")
        contract_lines = "".join(
            f"\t\t{key} = {value}\n"
            for key, value in assignments(
                POLITICAL_CONTRACTS[reform][0], f"political contract {reform}"
            )
        )
        contract_lines = (
            "\t\tglobal_estate_target_satisfaction = "
            f"{FOUNDATIONAL_ESTATE_COMPACT}\n"
            "\t\tmonthly_rebel_growth = "
            f"{FOUNDATIONAL_REBEL_GROWTH}\n"
            "\t\tpop_join_rebel_threshold = "
            f"{FOUNDATIONAL_REBEL_JOIN_THRESHOLD}\n"
            + contract_lines
        )
        block = block.replace(
            modifier_anchor, f"{modifier_anchor}{contract_lines}", 1
        )
        government_line = next(
            line for line in block.splitlines() if line.startswith("\tgovernment = ")
        )
        potential_lines = [
            "\tpotential = {",
            "\t\tOR = {",
            f"\t\t\thas_reform = government_reform:{reform}",
            *(
                f"\t\t\thas_or_had_tag = {tag}"
                for tag in sorted(holders_by_reform.get(reform, set()))
            ),
            "\t\t}",
            "\t}",
        ]
        block = block.replace(
            government_line,
            government_line + "\n" + "\n".join(potential_lines),
            1,
        )
        anchor = "\n\tyears = 2"
        if anchor not in block:
            raise ValueError(f"government reform {reform} lost its years anchor")
        block = block.replace(
            anchor,
            f"\n\ton_activate = {{\n\t\tset_parliament_type = parliament_type:{parliament}\n\t}}{anchor}",
            1,
        )
        rendered = rendered[:start] + block + rendered[end:]
    lines = [rendered.rstrip(), "", "# Profile-locked alternative ancient reform paths."]
    for (
        key, profile, government, _name, _description, modifier_text,
        _source, _confidence, _note, _age_index,
    ) in path_rows:
        family = PROFILE_BASE_REFORMS[profile] + alternatives_by_profile[profile]
        lines.extend((
            f"{key} = {{", "\tmajor = yes", f"\tgovernment = {government}",
            "\tpotential = {", "\t\tOR = {",
            *(f"\t\t\thas_reform = government_reform:{reform}" for reform in family),
            "\t\t}", "\t}", "\tcountry_modifier = {",
            "\t\tglobal_estate_target_satisfaction = "
            + FOUNDATIONAL_ESTATE_COMPACT,
            "\t\tmonthly_rebel_growth = " + FOUNDATIONAL_REBEL_GROWTH,
            "\t\tpop_join_rebel_threshold = "
            + FOUNDATIONAL_REBEL_JOIN_THRESHOLD,
            *(f"\t\t{modifier} = {value}" for modifier, value in assignments(
                modifier_text, f"alternative reform {key}"
            )),
            "\t}", "\ton_activate = {",
            f"\t\tset_parliament_type = parliament_type:{PROFILE_PARLIAMENTS[profile]}",
            "\t}", "\tyears = 2", "}", "",
        ))
    rendered = "\n".join(lines)
    return apply_ancient_subsistence_floor(rendered)


def estate_privileges(data: PowerData) -> str:
    lines = ["# Generated by tools/m6_power.py --write; M6 historical estate adapters."]
    # Visibility is ledger-owned.  Never widen an exact country grant with its
    # opening reform: broad reforms such as antq_tribal_kingdom are deliberately
    # shared by unrelated peoples and would expose every regional privilege to
    # every country using that mechanical government floor.
    for row in data.privileges:
        lines.extend((
            f"{row['key']} = {{",
            f"\testate = {row['estate']}",
        ))
        declared_reforms = list(
            pipe_values(
                row["potential_reforms"],
                f"privilege {row['key']} potential reforms",
            )
        ) if row["potential_reforms"] else []
        if declared_reforms or row["potential_tags"]:
            lines.extend(("\tpotential = {", "\t\tOR = {"))
            lines.extend(
                f"\t\t\thas_reform = government_reform:{reform}"
                for reform in declared_reforms
            )
            if row["potential_tags"]:
                tags = pipe_values(
                    row["potential_tags"], f"privilege {row['key']} potential tags"
                )
                lines.extend(f"\t\t\thas_or_had_tag = {tag}" for tag in tags)
            lines.extend(("\t\t}", "\t}"))
        if row["exclusive_with"]:
            lines.extend((
                "\tallow = {",
                f"\t\tNOT = {{ has_estate_privilege = estate_privilege:{row['exclusive_with']} }}",
                "\t}",
                "\tcan_revoke = { }",
            ))
        lines.append("\tcountry_modifier = {")
        lines.extend(f"\t\t{key} = {value}" for key, value in assignments(row["modifiers"], f"privilege {row['key']}"))
        lines.extend(("\t}", "}", ""))
    return "\n".join(lines)


def estate_change_on_action(data: PowerData) -> str:
    """Preserve the ancient compact across engine estate-identity resets.

    EUV resets an estate's *current* satisfaction when its dominant culture or
    religion changes.  That is tolerable for the much smaller 1337 realms, but
    the AD 1 territorial empires can re-elect several different demographic
    pluralities in succession.  A live Rome replay showed the reset bypassing
    the Principate's 60-point target compact, taking all represented estates
    from 64--96% to 0--5% and creating a civil-war cascade by AD 22.

    Restore only the changed estate, only for a generated ancient reform, and
    only up to the same 60-point floor already justified by the long-run M6
    balance campaign.  The stepped adjustment is deliberately bounded: a
    culture/religion change can never manufacture satisfaction above 80%, and
    ordinary taxation, privileges, disasters, wars, and event shocks remain
    fully effective.
    """
    reform_keys = tuple(
        re.findall(r"(?m)^([a-z][a-z0-9_]*) = \{$", reforms(data))
    )
    if not reform_keys or len(reform_keys) != len(set(reform_keys)):
        raise ValueError("ancient reform inventory for estate settlement is invalid")

    def block(on_action: str) -> list[str]:
        lines = [
            f"{on_action} = {{",
            "\ttrigger = {",
            "\t\tOR = {",
            *(f"\t\t\thas_reform = government_reform:{key}" for key in reform_keys),
            "\t\t}",
            "\t}",
            "\teffect = {",
        ]
        for index, (threshold, adjustment) in enumerate(ESTATE_IDENTITY_SETTLEMENT_FLOOR):
            branch = "if" if index == 0 else "else_if"
            lines.extend((
                f"\t\t{branch} = {{",
                "\t\t\tlimit = {",
                "\t\t\t\testate_satisfaction = {",
                "\t\t\t\t\testate_type = scope:estate",
                f"\t\t\t\t\tvalue < {threshold}",
                "\t\t\t\t}",
                "\t\t\t}",
                "\t\t\tadd_estate_satisfaction = {",
                "\t\t\t\ttype = scope:estate",
                f"\t\t\t\tvalue = {adjustment}",
                "\t\t\t}",
                "\t\t}",
            ))
        lines.extend(("\t}", "}", ""))
        return lines

    return "\n".join((
        "# Generated by tools/m6_power.py --write; AD 1 estate-identity settlement adapter.",
        "# root = country, scope:estate = estate type",
        *block("on_estate_culture_changed"),
        "# root = country, scope:estate = estate type",
        *block("on_estate_religion_changed"),
    ))


def law_definitions(data: PowerData) -> str:
    lines = ["# Generated by tools/m6_power.py --write; M6 historical legal adapters."]
    for row in data.laws:
        lines.extend((
            f"{row['law']} = {{",
            f"\tlaw_category = {row['law_category']}",
        ))
        if row["law"] != "antq_steppe_governance_law":
            lines.append(f"\tlaw_gov_group = {row['law_gov_group']}")
        # These first-generation adapters are retained for save/event symbol
        # compatibility only.  The complete S2 profile laws supersede them;
        # making them visible produces foreign, uninitialized duplicate rows.
        lines.extend((
            "\tpotential = {",
            "\t\talways = no",
            "\t}",
        ))
        lines.extend((
            f"\t{row['option']} = {{",
            "\t\tcountry_modifier = {",
        ))
        lines.extend(f"\t\t\t{key} = {value}" for key, value in assignments(row["modifiers"], f"law {row['law']}"))
        lines.extend(("\t\t}", "\t\tyears = 2", "\t\testate_preferences = {"))
        lines.extend(f"\t\t\t{estate}" for estate in pipe_values(row["estate_preferences"], f"law {row['law']} estate preferences"))
        lines.extend(("\t\t}", "\t}"))
        if row["law"] == "antq_citizenship_law":
            lines.extend((
                "\tantq_universal_citizenship = {",
                "\t\tcountry_modifier = {",
                "\t\t\tglobal_pop_assimilation_speed_modifier = 0.02",
                "\t\t\tmonthly_towards_centralization = societal_value_minor_monthly_move",
                "\t\t}",
                "\t\tyears = 2",
                "\t\testate_preferences = {",
                "\t\t\tburghers_estate",
                "\t\t\tnobles_estate",
                "\t\t}",
                "\t}",
            ))
        lines.extend(("}", ""))
    return "\n".join(lines)


def localization(data: PowerData, language: str) -> str:
    entries = [(row["key"], row["name"]) for row in data.dynasties]
    entries.extend((row["key"], row["name"]) for row in data.characters)
    entries.extend((
        (
            f"STATIC_MODIFIER_NAME_{ROMAN_SUCCESSION_GUARD}",
            "Sourced Historical Chronology",
        ),
        (
            "STATIC_MODIFIER_NAME_antq_augustan_auctoritas",
            "Augustan Auctoritas",
        ),
        (
            "STATIC_MODIFIER_DESC_antq_augustan_auctoritas",
            "The princeps holds tribunician and proconsular authority that strengthens imperial command without abolishing senatorial, equestrian, or municipal bargaining.",
        ),
        ("antq_principate", "Principate"),
        ("antq_principate_desc", "A republic-facade monarchy centred on the princeps and his auctoritas."),
        ("antq_dominate", "Dominate"),
        ("antq_dominate_desc", "A later Roman monarchy emphasizing central court authority and regional administration."),
        ("antq_han_imperial_bureaucracy", "Han Imperial Bureaucracy"),
        ("antq_han_imperial_bureaucracy_desc", "A palace-centred bureaucracy whose Mandate of Heaven is represented through legitimacy and effective rule."),
        ("antq_lankan_kingdom", "Anuradhapura Kingship"),
        ("antq_lankan_kingdom_desc", "A Lankan royal court whose monastic and irrigation patronage is a central source of authority."),
        ("antq_artaxiad_highland_kingship", "Artaxiad Highland Kingship"),
        ("antq_artaxiad_highland_kingship_desc", "A contested Artaxiad court balancing highland dynasts, fortresses, sanctuaries, routes, and Roman-Arsacid frontier pressure."),
        ("antq_nabataean_caravan_kingship", "Nabataean Caravan Kingship"),
        ("antq_nabataean_caravan_kingship_desc", "The court of Aretas IV and Huldu coordinating caravan houses, waterworks, sanctuaries, oasis cultivation, and Roman relations."),
        ("antq_himyarite_terrace_kingship", "Himyarite Terrace Kingship"),
        ("antq_himyarite_terrace_kingship_desc", "An evidence-bounded highland court balancing lineages, terraces, sanctuaries, incense routes, ports, and cultivating communities."),
        ("antq_satavahana_deccan_kingship", "Satavahana Deccan Kingship"),
        ("antq_satavahana_deccan_kingship_desc", "A conservative Deccan court adapter balancing titled houses, religious gifts, guild exchange, cultivation, waterworks, and routes."),
        ("antq_catuvellaunian_oppidum_kingship", "Catuvellaunian Oppidum Kingship"),
        ("antq_catuvellaunian_oppidum_kingship_desc", "Tasciovanus's kingship coordinating dynastic mints, oppida, retinues, sacred places, cultivation, and Channel exchange."),
        ("antq_trinovantian_coin_kingship", "Trinovantian Coin Kingship"),
        ("antq_trinovantian_coin_kingship_desc", "Dubnovellaunos's bounded court coordinating coin custody, Camulodunon stores, Channel landings, retinues, and sacred-place hearings."),
        ("antq_brigantian_hillfort_confederacy", "Brigantian Hillfort Confederacy"),
        ("antq_brigantian_hillfort_confederacy_desc", "A large but internally varied northern order coordinating kindreds, selected hillfort stores, Pennine routes, herds, and musters."),
        ("antq_durotrigian_hillfort_coin_order", "Durotrigian Hillfort and Coin Order"),
        ("antq_durotrigian_hillfort_coin_order_desc", "A distributed political order grounded in distinctive coinage, pottery, burial, settlement, coastal, and enclosure traditions."),
        ("antq_ivernian_regional_assembly", "Ivernian Regional Assembly"),
        ("antq_ivernian_regional_assembly_desc", "A low-centralization southwest-Irish gathering coordinating cattle gifts, seaway exchange, smithing, offerings, hospitality, and sureties."),
        ("antq_aestian_amber_coast_order", "Aestian Amber-Coast Order"),
        ("antq_aestian_amber_coast_order_desc", "A plural southeastern Baltic order coordinating amber exchange, coastal passage, woodland watch, household stores, and local offering custody."),
        ("antq_frisian_terp_community_order", "Frisian Terp Community Order"),
        ("antq_frisian_terp_community_order_desc", "A salt-marsh order coordinating terp maintenance, cattle and hides, tidal passage, household stores, and negotiated Roman-frontier obligations."),
        ("antq_dacian_divided_kingships", "Dacian Divided Kingships"),
        ("antq_dacian_divided_kingships_desc", "The post-Burebista regional powers coordinating selected hillfort stores, metalworking, Carpathian passages, mounted hosts, and external oaths."),
        ("antq_garamantian_oasis_state", "Garamantian Oasis State"),
        ("antq_garamantian_oasis_state_desc", "An urbanized Fazzan oasis state coordinating underground irrigation, settlement stores, caravan routes, mounted forces, and Saharan exchange."),
        ("antq_marcomannic_bohemian_kingship", "Marcomannic Bohemian Kingship"),
        ("antq_marcomannic_bohemian_kingship_desc", "Maroboduus's organized kingdom balancing the royal retinue, allied kindreds, settlement stores, exchange, and Roman-frontier diplomacy."),
        ("antq_cheruscan_kindred_assembly", "Cheruscan Kindred Assembly"),
        ("antq_cheruscan_kindred_assembly_desc", "An armed kindred assembly coordinating compensation, frontier intelligence, seasonal musters, and negotiated coalition leadership."),
        ("antq_chattian_host_order", "Chattian Host Order"),
        ("antq_chattian_host_order_desc", "A prepared infantry host whose selected leaders, vowed warriors, provisions, tools, and forest routes structure political authority."),
        ("antq_batavian_rhine_compact", "Batavian Rhine Compact"),
        ("antq_batavian_rhine_compact_desc", "A Rhine-island political order balancing local assembly, river service, and concentrated auxiliary obligations to Rome."),
        ("antq_semnonian_sacred_confederacy", "Semnonian Sacred Confederacy"),
        ("antq_semnonian_sacred_confederacy_desc", "A confederate order whose delegated gathering, district musters, compensation, and sacred-grove custody bind affiliated kindreds."),
        ("antq_sabaean_marib_kingship", "Sabaean Ma'rib Kingship"),
        ("antq_sabaean_marib_kingship_desc", "An anonymous Sabaean court grounded in Ma'rib waterworks, sanctuaries, incense routes, highland cultivation, and regional service."),
        ("antq_mauretanian_client_kingship", "Mauretanian Client Kingship"),
        ("antq_mauretanian_client_kingship_desc", "The court of Juba II and Cleopatra Selene balancing royal domains, cities, ports, frontier communities, and Roman patronage."),
        ("antq_herodian_judean_ethnarchy", "Herodian Judean Ethnarchy"),
        ("antq_herodian_judean_ethnarchy_desc", "Archelaus's ethnarchy balancing Herodian dynastic authority, the Jerusalem temple establishment, toparchic assessment, pilgrimage, and Roman confirmation."),
        ("antq_cappadocian_client_kingship", "Cappadocian Client Kingship"),
        ("antq_cappadocian_client_kingship_desc", "Archelaus's client court balancing royal domains, sanctuary property, highland routes, cavalry households, and Roman patronage."),
        ("antq_odrysian_client_kingship", "Odrysian Client Kingship"),
        ("antq_odrysian_client_kingship_desc", "Rhoemetalces's court balancing dynastic claimants, mounted retainers, mountain communities, Aegean cities, and Roman intervention."),
        ("antq_bosporan_client_kingship", "Bosporan Client Kingship"),
        ("antq_bosporan_client_kingship_desc", "A contested Bosporan succession balancing royal claimants, Greek poleis, grain ports, mounted households, and steppe-frontier compacts."),
        ("antq_herodian_galilean_tetrarchy", "Herodian Galilean Tetrarchy"),
        ("antq_herodian_galilean_tetrarchy_desc", "Antipas's tetrarchy balancing Herodian domains, lake fisheries, Galilean and Peraean routes, ritual stores, markets, and Roman confirmation."),
        ("antq_herodian_batanean_tetrarchy", "Herodian Batanean Tetrarchy"),
        ("antq_herodian_batanean_tetrarchy_desc", "Philip's northern tetrarchy balancing highland houses, sanctuaries, basalt settlements, cisterns, routes, horse service, and Roman patronage."),
        ("antq_commagenean_client_kingship", "Commagenean Client Kingship"),
        ("antq_commagenean_client_kingship_desc", "Antiochus III's court balancing dynastic houses, sanctuaries, Euphrates passage, highland cavalry, cultivation, and Roman-Arsacid diplomacy."),
        ("antq_m6_placeholder_ruler", "Interim Seat"),
        ("antq_emesan_client_dynasty", "Emesan Client Dynasty"),
        ("antq_emesan_client_dynasty_desc", "Iamblichus II's Sampsigeramid court balancing dynastic houses, sanctuary custody, caravan and textile exchange, mounted service, and Roman patronage."),
        ("antq_indian_ganasangha", "Indian Ganasangha"),
        ("antq_indian_ganasangha_desc", "A clan-based republican council represented through the installed republic government type."),
        ("antq_indo_scythian_kingship", "Indo-Scythian Kingship"),
        ("antq_indo_scythian_kingship_desc", "A politically composite northern Indian monarchy supported by regional military elites."),
        ("antq_indo_greek_kingship", "Late Indo-Greek Kingship"),
        ("antq_indo_greek_kingship_desc", "The final eastern-Punjab Indo-Greek court, supported by a compact with its urban elites."),
        ("antq_parthian_king_of_kings", "Parthian King of Kings"),
        ("antq_parthian_king_of_kings_desc", "An Arsacid monarchy balancing the royal court with powerful Iranian noble houses."),
        ("antq_sassanid_centralized_monarchy", "Sassanid Centralized Monarchy"),
        ("antq_sassanid_centralized_monarchy_desc", "A centralized Iranian monarchy that supersedes the Arsacid great-house adapter after the Sassanid revolution."),
        ("antq_client_monarchy", "Client Monarchy"),
        ("antq_client_monarchy_desc", "A local royal court whose position is shaped by imperial patronage."),
        ("antq_parthian_subkingdom", "Parthian Sub-Kingdom"),
        ("antq_parthian_subkingdom_desc", "A regional Iranian court whose authority rests on local elites and an Arsacid-facing political order."),
        ("antq_arian_satrapal_court", "Arian Satrapal Court"),
        ("antq_arian_satrapal_court_desc", "Aria's old satrapal and urban frame balancing landed houses, caravan interests, cultivators, and Arsacid-facing authority."),
        ("antq_kangju_confederated_kingship", "Kangju Confederated Kingship"),
        ("antq_kangju_confederated_kingship_desc", "A royal confederation coordinating constituent rulers, mounted households, pasture routes, and Sogdian towns."),
        ("antq_sogdian_city_compact", "Sogdian City Compact"),
        ("antq_sogdian_city_compact_desc", "Principal towns and landed houses coordinating exchange and defence beneath Kangju predominance without a unitary Sogdian crown."),
        ("antq_dayuan_oasis_kingship", "Dayuan Oasis Kingship"),
        ("antq_dayuan_oasis_kingship_desc", "The Ferghana court balancing irrigated towns, horse-breeding households, route interests, and Han-facing diplomacy."),
        ("antq_wusun_kunmi_confederacy", "Wusun Kunmi Confederacy"),
        ("antq_wusun_kunmi_confederacy_desc", "The Kunmi's negotiated authority over mobile households, subordinate leaders, remount pastures, and frontier diplomacy."),
        ("antq_yuezhi_five_yabghus", "Yuezhi Five Yabghus"),
        ("antq_yuezhi_five_yabghus_desc", "A divided Yuezhi-Bactrian political field represented without fixing the disputed chronology of Kushan consolidation."),
        ("antq_han_western_regions_kingship", "Western Regions Kingship"),
        ("antq_han_western_regions_kingship_desc", "A local oasis king and court operating through tributary and protectorate relations rather than direct Han annexation."),
        ("antq_yancai_aorsi_confederacy", "Yancai-Aorsi Confederacy"),
        ("antq_yancai_aorsi_confederacy_desc", "A mobile lower-Ural confederational adapter using the debated Yancai-Aorsi association without invented borders or offices."),
        ("antq_saryarka_late_iron_network", "Saryarka Late Iron-Age Network"),
        ("antq_saryarka_late_iron_network_desc", "Central-steppe communities linked by herding, exchange, burial, and seasonal routes without a falsely unitary state."),
        ("antq_altai_contact_network", "Altai Contact Network"),
        ("antq_altai_contact_network_desc", "Altai herding, exchange, and ritual communities represented as a contact network rather than one ancient nation."),
        ("antq_zhangzhung_plateau_kingship", "Zhang Zhung Plateau Kingship"),
        ("antq_zhangzhung_plateau_kingship_desc", "A bounded western-plateau court balancing leading houses, pastoral households, exchange routes, and local ritual custody without invented AD 1 offices."),
        ("antq_sumpa_highland_confederacy", "Sumpa Highland Confederacy"),
        ("antq_sumpa_highland_confederacy_desc", "Northeastern highland groups coordinate pasture, river passage, exchange, and collective defence without later imperial administration."),
        ("antq_changtang_pastoral_network", "Changtang Pastoral Network"),
        ("antq_changtang_pastoral_network_desc", "Mobile high-pasture households coordinate seasonal grazing, corrals, restitution, and common defence without a centralized state."),
        ("antq_central_plateau_agropastoral_network", "Central Plateau Agropastoral Network"),
        ("antq_central_plateau_agropastoral_network_desc", "River-valley settlements coordinate barley cultivation, herd management, storage, passage, and seasonal obligations without a backdated dynasty."),
        ("antq_eastern_plateau_corridor_network", "Eastern Plateau Corridor Network"),
        ("antq_eastern_plateau_corridor_network_desc", "Highland households and leading exchange brokers coordinate river corridors, pasture, mortuary obligations, and defence without one ethnic state."),
        ("antq_tamilakam_velir_court", "Tamilakam Velir Court"),
        ("antq_tamilakam_velir_court_desc", "A bounded chiefly court balancing leading houses, cultivators, poets, and exchange through attested early Tamil institutions."),
        ("antq_central_indian_urban_kingship", "Central Indian Urban Kingship"),
        ("antq_central_indian_urban_kingship_desc", "Post-Mauryan urban authority coordinates leading houses, workshops, cultivators, and religious patrons without an invented common dynasty."),
        ("antq_central_indian_janapada", "Central Indian Janapada"),
        ("antq_central_indian_janapada_desc", "A regional court and cultivating communities sustain an older janapada identity whose exact AD 1 offices and frontier are unrecovered."),
        ("antq_central_indian_megalithic_network", "Central Indian Megalithic Network"),
        ("antq_central_indian_megalithic_network_desc", "Iron-Age settlements and commemorative landscapes coordinate production, passage, restitution, and collective defence without one ethnic state."),
        ("antq_upper_mahanadi_kingship", "Upper Mahanadi Kingship"),
        ("antq_upper_mahanadi_kingship_desc", "A conservative Dakshina Kosala court coordinates riverine cultivation and inland exchange without projecting later Sirpur dynasties."),
        ("antq_indian_ocean_atoll_network", "Indian Ocean Atoll Network"),
        ("antq_indian_ocean_atoll_network_desc", "Atoll communities coordinate marine production, passage, and exchange without a later sultanate or centralized island state."),
        ("antq_mainland_river_corridor_network", "Mainland River Corridor Network"),
        ("antq_mainland_river_corridor_network_desc", "River and littoral communities coordinate landing places, passage, restitution, and exchange without one centralized state."),
        ("antq_sa_huynh_exchange_network", "Sa Huynh Exchange Network"),
        ("antq_sa_huynh_exchange_network_desc", "Coastal production, burial communities, and maritime exchange operate without a backdated Champa state."),
        ("antq_mainland_highland_exchange_network", "Mainland Highland Exchange Network"),
        ("antq_mainland_highland_exchange_network_desc", "Highland communities coordinate forest access, passes, mortuary duties, and exchange without later ethnic borders."),
        ("antq_mainland_iron_age_basin_network", "Mainland Iron-Age Basin Network"),
        ("antq_mainland_iron_age_basin_network_desc", "Intermontane settlements coordinate cultivation, water, exchange, and defence without backdating later Tai states."),
        ("antq_amur_forest_river_network", "Amur Forest-River Network"),
        ("antq_amur_forest_river_network_desc", "Forest-river households coordinate fisheries, stores, passage, and exchange without one centralized state."),
        ("antq_sakhalin_maritime_network", "Sakhalin Maritime Network"),
        ("antq_sakhalin_maritime_network_desc", "Island communities coordinate shore access, fishing, sea-mammal use, and exchange without a later ethnic polity."),
        ("antq_ussuri_poltsian_network", "Ussuri Pol'tse Network"),
        ("antq_ussuri_poltsian_network_desc", "River and basin communities coordinate cultivation, forest access, exchange, and defence without a fixed Yilou state."),
        ("antq_northern_okjeo_corridor", "Northern Okjeo Corridor"),
        ("antq_northern_okjeo_corridor_desc", "Tumen and southern Maritime communities coordinate passage and exchange without a later Korean court."),
        ("antq_borneo_cave_river_network", "Borneo Cave-River Network"),
        ("antq_borneo_cave_river_network_desc", "Cave and river households coordinate burial places, forest access, landing places, and exchange without one island state."),
        ("antq_borneo_coastal_exchange_network", "Borneo Coastal Exchange Network"),
        ("antq_borneo_coastal_exchange_network_desc", "River mouths, pottery, and maritime exchange link coastal households without a centralized port or later kingdom."),
        ("antq_borneo_interior_river_network", "Borneo Interior River Network"),
        ("antq_borneo_interior_river_network_desc", "River communities coordinate portage, forest access, cultivation, and exchange without later ethnic borders."),
        ("antq_borneo_foothill_iron_network", "Borneo Foothill Iron Network"),
        ("antq_borneo_foothill_iron_network_desc", "Foothill households coordinate ore, charcoal, furnaces, river passage, and cultivation without a uniform guild or later state."),
        ("antq_philippine_coastal_river_network", "Philippine Coastal-River Network"),
        ("antq_philippine_coastal_river_network_desc", "River, bay, and coastal households coordinate landing places, cultivation, passage, and exchange without one island kingdom."),
        ("antq_philippine_mortuary_community_network", "Philippine Mortuary Community Network"),
        ("antq_philippine_mortuary_community_network_desc", "Communities coordinate ancestral places, secondary burials, cultivation, and exchange without a common priesthood or state."),
        ("antq_philippine_island_exchange_network", "Philippine Island Exchange Network"),
        ("antq_philippine_island_exchange_network_desc", "Island households coordinate anchorages, pottery exchange, passage, and restitution without a centralized thalassocracy."),
        ("antq_philippine_cave_coast_network", "Philippine Cave-Coast Network"),
        ("antq_philippine_cave_coast_network_desc", "Cave, rockshelter, and coastal households coordinate burial places, shore access, subsistence, and exchange without a later island polity."),
        ("antq_sulawesi_coastal_exchange_network", "Sulawesi Coastal Exchange Network"),
        ("antq_sulawesi_coastal_exchange_network_desc", "Coastal households coordinate landing places, cultivation, passage, and exchange without a later kingdom or common island government."),
        ("antq_sulawesi_island_exchange_network", "Sulawesi Island Exchange Network"),
        ("antq_sulawesi_island_exchange_network_desc", "Island households coordinate anchorages, short crossings, exchange, and restitution without a centralized thalassocracy."),
        ("antq_sulawesi_highland_mortuary_network", "Sulawesi Highland Mortuary Network"),
        ("antq_sulawesi_highland_mortuary_network_desc", "Highland communities coordinate cultivation, ancestral places, jar burial, and valley passage without inventing a common priesthood."),
        ("antq_sulawesi_river_lake_network", "Sulawesi River-Lake Network"),
        ("antq_sulawesi_river_lake_network_desc", "River and lake communities coordinate cultivation, portage, forest access, and exchange without projecting later iron kingdoms backward."),
        ("antq_sulawesi_peninsula_community_network", "Sulawesi Peninsula Community Network"),
        ("antq_sulawesi_peninsula_community_network_desc", "Peninsular households coordinate coast, gardens, inland paths, and exchange without a later ethnic federation or named ruler."),
        ("antq_north_maluku_metal_age_network", "North Maluku Metal-Age Network"),
        ("antq_north_maluku_metal_age_network_desc", "Metal-Age island communities coordinate pottery, landing places, food, and exchange without backdating the Ternate or Tidore sultanates."),
        ("antq_point_peninsula_seasonal_network", "Point Peninsula Seasonal Network"),
        ("antq_point_peninsula_seasonal_network_desc", "Lake, river, and forest communities coordinate seasonal subsistence, burial places, and exchange without a later confederacy or common state."),
        ("antq_havana_hopewell_exchange_network", "Havana Hopewell Exchange Network"),
        ("antq_havana_hopewell_exchange_network_desc", "Illinois-valley communities coordinate earthwork gatherings, mortuary obligations, craft exchange, and river passage without treating Hopewell as one people."),
        ("antq_central_mississippi_woodland_network", "Central Mississippi Woodland Network"),
        ("antq_central_mississippi_woodland_network_desc", "River-valley and upland communities coordinate subsistence, mound obligations, exchange, and passage before the later Mississippian world."),
        ("antq_kansas_city_hopewell_network", "Kansas City Hopewell Network"),
        ("antq_kansas_city_hopewell_network_desc", "Lower-Missouri and eastern-Plains communities coordinate floodplain villages, tributary camps, resources, and exchange without one archaeological polity."),
        ("antq_mahan_small_state_league", "Mahan Small-State League"),
        ("antq_mahan_small_state_league_desc", "Mahan agricultural small states coordinate assemblies, river access, stores, ritual obligations, and diplomacy without one recovered AD 1 constitution."),
        ("antq_jinhan_small_state_league", "Jinhan Small-State League"),
        ("antq_jinhan_small_state_league_desc", "Jinhan small states coordinate cultivation, bronze-working, exchange, and collective defence without backdating Silla."),
        ("antq_byeonhan_iron_exchange_league", "Byeonhan Iron-Exchange League"),
        ("antq_byeonhan_iron_exchange_league_desc", "Byeonhan small states coordinate iron, ports, navigation, and exchange without backdating Gaya."),
        ("antq_soanian_king_and_council", "Soanian King and Council"),
        ("antq_soanian_king_and_council_desc", "A highland king governs with the attested council of three hundred, balancing leading households without inventing an AD 1 ruler or succession code."),
        ("antq_andean_irrigated_valley_network", "Andean Irrigated-Valley Network"),
        ("antq_andean_irrigated_valley_network_desc", "Valley communities coordinate irrigation, stores, ritual obligations, and exchange without a coast-wide state or invented water constitution."),
        ("antq_andean_highland_community_network", "Andean Highland Community Network"),
        ("antq_andean_highland_community_network_desc", "Highland communities coordinate cultivation, pasture, passes, exchange, and ritual without backdating later imperial administration."),
        ("antq_andean_ceremonial_centre_network", "Andean Ceremonial-Centre Network"),
        ("antq_andean_ceremonial_centre_network_desc", "Ceremonial centres coordinate public works, specialist production, cultivation, and exchange without asserting one uniform territorial state."),
        ("antq_wankarani_mound_village_network", "Wankarani Mound-Village Network"),
        ("antq_wankarani_mound_village_network_desc", "Central-Altiplano mound villages coordinate camelid herding, households, exchange, and ritual without inventing a common ruler."),
        ("antq_herrera_plateau_exchange_network", "Herrera Plateau Exchange Network"),
        ("antq_herrera_plateau_exchange_network_desc", "Plateau communities coordinate cultivation, salt and valley exchange, gatherings, and common works without backdating Muisca institutions."),
        ("antq_sierra_nevada_early_community_network", "Sierra Nevada Early Community Network"),
        ("antq_sierra_nevada_early_community_network_desc", "Slope and coast communities coordinate subsistence, river passage, exchange, and local obligations before the dated Neguanje and Tairona systems."),
        ("antq_loja_regional_development_network", "Loja Regional Development Network"),
        ("antq_loja_regional_development_network_desc", "Loja and Catamayo valley communities coordinate cultivation, passage, and exchange without backdating later ethnic polities."),
        ("antq_daga_highland_garden_network", "Daga Highland Garden Network"),
        ("antq_daga_highland_garden_network_desc", "Highland-slope communities coordinate gardens, forest access, households, and exchange without a reconstructed common constitution."),
        ("antq_bomberai_coastal_community_network", "Bomberai Coastal Community Network"),
        ("antq_bomberai_coastal_community_network_desc", "Coastal communities coordinate landing places, forest products, exchange, and restitution without backdating a later kingdom."),
        ("antq_early_mariana_island_network", "Early Mariana Island Network"),
        ("antq_early_mariana_island_network_desc", "Island communities coordinate subsistence, passage, pottery, and gatherings without a reconstructed contact-era hierarchy."),
        ("antq_yap_ulithi_island_network", "Yap-Ulithi Island Network"),
        ("antq_yap_ulithi_island_network_desc", "Island communities coordinate passage, provisioning, exchange, and restitution without projecting the later sawei hierarchy into AD 1."),
        ("antq_orinoco_llanos_ceramic_network", "Orinoco-Llanos Ceramic Network"),
        ("antq_orinoco_llanos_ceramic_network_desc", "Communities coordinate cultivation, ceramics, river passage, and exchange without equating material style with language or polity."),
        ("antq_windward_island_ceramic_network", "Windward Island Ceramic Network"),
        ("antq_windward_island_ceramic_network_desc", "Island communities coordinate gardens, fishing, pottery, passage, and exchange without a later ethnic or political identity."),
        ("antq_central_california_coastal_network", "Central California Coastal Network"),
        ("antq_central_california_coastal_network_desc", "Coastal communities coordinate estuary, shore, woodland, gathering, and exchange obligations without a contact-era ethnonym."),
        ("antq_acutuba_central_amazon_network", "Acutuba Central-Amazon Network"),
        ("antq_acutuba_central_amazon_network_desc", "Floodplain communities coordinate cultivation, ceramics, river passage, and exchange without an invented territorial state."),
        ("antq_mesoamerican_urban_ritual_center", "Mesoamerican Urban-Ritual Center"),
        ("antq_mesoamerican_urban_ritual_center_desc", "A first-order ceremonial and exchange center coordinates public space, specialist production, cultivation, and regional ties without an invented recovered constitution."),
        ("antq_mesoamerican_formative_civic_network", "Mesoamerican Formative Civic Network"),
        ("antq_mesoamerican_formative_civic_network_desc", "Formative centers and cultivating communities coordinate water, stores, ritual places, exchange, and common works without a falsely uniform state."),
        ("antq_mesoamerican_exchange_corridor_network", "Mesoamerican Exchange-Corridor Network"),
        ("antq_mesoamerican_exchange_corridor_network_desc", "Communities along coast, river, pass, and basin routes coordinate passage, exchange, restitution, and defence without later ethnic or imperial borders."),
        ("antq_mesoamerican_highland_community_network", "Mesoamerican Highland Community Network"),
        ("antq_mesoamerican_highland_community_network_desc", "Highland settlements coordinate cultivation, passes, exchange, ritual obligations, and collective defence without imposing a later ethnic polity."),
        ("antq_west_mexican_shaft_tomb_chiefdom", "West Mexican Shaft-Tomb Chiefdom"),
        ("antq_west_mexican_shaft_tomb_chiefdom_desc", "Ranked households coordinate mortuary places, specialist production, cultivation, and exchange without one western Mexican state."),
        ("antq_teuchitlan_civic_center_network", "Teuchitlan Civic-Center Network"),
        ("antq_teuchitlan_civic_center_network_desc", "Central Jalisco chiefly centers coordinate circular precincts, households, production, and exchange without a fixed territorial kingdom."),
        ("antq_west_mexican_basin_community_network", "West Mexican Basin Community Network"),
        ("antq_west_mexican_basin_community_network_desc", "Basin and highland communities coordinate cultivation, stores, mortuary obligations, and exchange without a later ethnic state."),
        ("antq_west_mexican_highland_corridor_network", "West Mexican Highland-Corridor Network"),
        ("antq_west_mexican_highland_corridor_network_desc", "Highland communities coordinate passes, exchange, restitution, ritual places, and defence without later frontier identities."),
        ("antq_sonoran_desert_farming_network", "Sonoran Desert Farming Network"),
        ("antq_sonoran_desert_farming_network_desc", "Ancestral Sonoran households coordinate river and runoff farming, water access, exchange, and seasonal obligations before later mature systems."),
        ("antq_buffer_kingdom", "Buffer Kingdom"),
        ("antq_buffer_kingdom_desc", "A frontier court balancing local authority against stronger neighbouring powers."),
        ("antq_kushite_dual_kingship", "Kushite Dual Kingship"),
        ("antq_kushite_dual_kingship_desc", "A Kushite royal court represented through the named Natakamani-Amanitore co-rule."),
        ("antq_steppe_confederation", "Steppe Confederation"),
        ("antq_steppe_confederation_desc", "A confederation whose chanyu must balance the leading clans."),
        ("antq_xianbei_eastern_confederacy", "Xianbei Eastern Confederacy"),
        ("antq_xianbei_eastern_confederacy_desc", "Separate eastern-steppe chiefly groups negotiate mounted service, pasture access, and seasonal assembly before the later Tanshihuai confederation."),
        ("antq_early_korean_kingdom", "Early Korean Kingdom"),
        ("antq_early_korean_kingdom_desc", "A developing royal kingdom supported by leading political houses."),
        ("antq_regional_kingship", "Regional Kingship"),
        ("antq_regional_kingship_desc", "A bounded technical monarchy adapter for an attested regional court without a defensible current ruler."),
        ("antq_advanced_chiefdom", "Advanced Chiefdom"),
        ("antq_advanced_chiefdom_desc", "A developing chiefly polity represented through the installed tribal government type."),
        ("antq_northern_indian_coin_kingship", "Northern Indian Coin Kingship"),
        ("antq_northern_indian_coin_kingship_desc", "A local northern Indian court whose coinage, leading houses, cultivators, and exchange networks are represented without imposing one shared post-Shunga constitution."),
        ("antq_pundranagara_urban_kingship", "Pundranagara Urban Kingship"),
        ("antq_pundranagara_urban_kingship_desc", "A fortified early-historic urban court at Pundranagara represented without inventing a recovered AD 1 dynasty or bureaucracy."),
        ("antq_bengal_riverine_community_network", "Bengal Riverine Community Network"),
        ("antq_bengal_riverine_community_network_desc", "Riverine households, landing places, cultivators, and exchange groups coordinate without backdating later Bengal kingdoms."),
        ("antq_eastern_megalithic_community_network", "Eastern Megalithic Community Network"),
        ("antq_eastern_megalithic_community_network_desc", "Plateau settlements, iron-working households, and commemorative landscapes coordinate without implying one ethnicity or state."),
        ("antq_eastern_hill_valley_network", "Eastern Hill-Valley Network"),
        ("antq_eastern_hill_valley_network_desc", "Valley and upland communities coordinate seasonal work, passage, restitution, and exchange without later political borders."),
        ("antq_himalayan_highland_network", "Himalayan Highland Network"),
        ("antq_himalayan_highland_network_desc", "Highland communities coordinate routes, cultivation, herding, and local obligations without projecting later Himalayan states backward."),
        ("antq_far_side_port_chiefdom", "Far-Side Port Chiefdom"),
        ("antq_far_side_port_chiefdom_desc", "A separately led northern-Horn market coordinating roadstead access, exchange households, mobile suppliers, and visiting merchants."),
        ("antq_horn_pastoral_network", "Horn Pastoral Network"),
        ("antq_horn_pastoral_network_desc", "Mobile pastoral households coordinate routes, water, restitution, and exchange without a centralized state or fixed ethnic border."),
        ("antq_west_african_savanna_compound_network", "West African Savanna Compound Network"),
        ("antq_west_african_savanna_compound_network_desc", "Dispersed savanna compounds coordinate cultivation, grazing, river access, and restitution without backdating later Hausa identities or states."),
        ("antq_west_african_ironworking_network", "West African Ironworking Network"),
        ("antq_west_african_ironworking_network_desc", "Ironworking, farming, and exchange households coordinate furnaces, fuel, food, and circulation without implying one ethnicity or centralized polity."),
        ("antq_west_african_forest_network", "West African Forest Network"),
        ("antq_west_african_forest_network_desc", "Forest households coordinate land access, cultivation, ritual custody, and river exchange without backdating later dynasties, cities, or states."),
        ("antq_early_ironworking_community_network", "Early Ironworking Community Network"),
        ("antq_early_ironworking_community_network_desc", "Dispersed farming, foraging, herding, potting, and ironworking communities coordinate exchange and local obligations without a centralized state or single ethnic identity."),
        ("antq_mobile_hunter_herder_network", "Mobile Hunter-Herder Network"),
        ("antq_mobile_hunter_herder_network_desc", "Mobile hunter-herder communities coordinate access, exchange, restitution, and seasonal movement without a uniform polity, language, or later territorial identity."),
        ("antq_settled_town_cluster", "Settled Town Cluster"),
        ("antq_settled_town_cluster_desc", "A settled urban community represented through a bounded council adapter rather than an invented monarchy."),
        ("antq_tribal_kingdom", "Tribal Kingdom"),
        ("antq_tribal_kingdom_desc", "A kingship sustained and constrained by leading kin groups."),
    ))
    for key, _profile, _government, name, description, *_rest in reform_path_rows():
        entries.extend(((key, name), (f"{key}_desc", description)))
    for row in data.privileges:
        entries.extend(((row["key"], row["name"]), (f"{row['key']}_desc", row["description"])))
    for row in data.laws:
        entries.extend(((row["law"], row["name"]), (f"{row['law']}_desc", row["description"])))
        entries.extend(((row["option"], row["option_name"]), (f"{row['option']}_desc", row["option_description"])))
    entries.extend((
        ("antq_universal_citizenship", "Universal Citizenship"),
        ("antq_universal_citizenship_desc", "A legal-status adapter for Caracalla's AD 212 grant of citizenship to free imperial inhabitants."),
    ))
    return "\n".join([f"l_{language}:", *(f' {key}: "{value}"' for key, value in entries), ""])


def outputs(data: PowerData) -> dict[Path, str]:
    result = {
        REFORM_OUTPUT: reforms(data),
        PRIVILEGE_OUTPUT: estate_privileges(data),
        LAW_OUTPUT: law_definitions(data),
        CHARACTER_BOOTSTRAP_OUTPUT: character_bootstrap(data),
        ESTATE_CHANGE_OUTPUT: estate_change_on_action(data),
        RULER_TRANSITION_EVENT_OUTPUT: ruler_transition_event(),
        RULER_GUARD_MODIFIER_OUTPUT: ruler_guard_modifier(),
        POLITICAL_CONTRACT_OUTPUT: political_contract_ledger(),
        ALTERNATIVE_REFORM_OUTPUT: alternative_reform_ledger(),
        REFORM_VISIBILITY_OUTPUT: reform_visibility_matrix(data),
    }
    for language in ("english", *M2_MIRROR_LANGUAGES):
        result[LOC_ROOT / language / f"antq_m6_power_l_{language}.yml"] = localization(data, language)
    return result


def roster_coverage(data: PowerData) -> str:
    """Render the auditable boundary between named and anonymous AD 1 profiles."""
    characters_by_tag: dict[str, list[dict[str, str]]] = {}
    for character in data.characters:
        characters_by_tag.setdefault(character["design_tag"], []).append(character)
    named = [
        government for _, government in sorted(data.governments.items())
        if has_named_active_head(government)
    ]
    anonymous = [
        government for _, government in sorted(data.governments.items())
        if government["ruler"] == "random"
    ]
    lines = [
        "# M6 explicit government and roster coverage",
        "",
        "Generated by `tools/m6_power.py --write`; do not hand-edit.",
        "",
        "## Checked coverage",
        "",
        f"- Explicit government profiles: **{len(data.governments)}** "
        "(complete for Tier-1/2, with sourced Tier-3 regional additions)",
        f"- Source-led character records: **{len(data.characters)}** (plan target: 250--400)",
        f"- Named active-head profiles: **{len(named)}**",
        f"- Evidence-bounded anonymous/collective profiles: **{len(anonymous)}**",
        f"- Dynasties: **{len(data.dynasties)}**; campaign-valid ruler terms: **{len(data.ruler_terms)}**; "
        f"regnal-history rows: **{len(data.regnal_histories)}**",
        "",
        "An anonymous/collective profile is not an omitted polity. It is the deliberate `ruler = random` "
        "engine representation where the project sources establish a polity, confederation, or settlement "
        "form but not a defensible AD 1 incumbent. No generic person is entered into `character_db` to "
        "simulate missing evidence. Its individual source and limitation are in `governments.csv`.",
        "",
        "## Profiles with named active heads",
        "",
        "| Tag | Active head | Source-led character records |",
        "| --- | --- | ---: |",
    ]
    for government in named:
        active_head = government["heir"] if government["regency"] else government["ruler"]
        lines.append(
            f"| {government['design_tag']} | `{active_head}` | "
            f"{len(characters_by_tag.get(government['design_tag'], []))} |"
        )
    lines.extend((
        "",
        "## Evidence-bounded anonymous or collective profiles",
        "",
        "| Tag | Government adapter | Source route |",
        "| --- | --- | --- |",
    ))
    for government in anonymous:
        lines.append(
            f"| {government['design_tag']} | `{government['reform']}` | {government['source']} |"
        )
    lines.append("")
    return "\n".join(lines)


def write(data: PowerData) -> None:
    for path, content in outputs(data).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8-sig", newline="\n")
        print(f"m6_power: wrote {path.relative_to(ROOT)}")
    ROSTER_REPORT.write_text(roster_coverage(data), encoding="utf-8", newline="\n")
    print(f"m6_power: wrote {ROSTER_REPORT.relative_to(ROOT)}")


def check(data: PowerData) -> bool:
    failures = []
    rendered_characters = character_manager(data)
    rendered_bootstrap = character_bootstrap(data)
    rendered_reforms = reforms(data)
    rendered_estate_changes = estate_change_on_action(data)
    modifier_blocks = rendered_reforms.count("\tcountry_modifier = {\n")
    for modifier, value in (
        ("global_estate_target_satisfaction", FOUNDATIONAL_ESTATE_COMPACT),
        ("monthly_rebel_growth", FOUNDATIONAL_REBEL_GROWTH),
        ("pop_join_rebel_threshold", FOUNDATIONAL_REBEL_JOIN_THRESHOLD),
    ):
        count = rendered_reforms.count(f"\t\t{modifier} = {value}\n")
        if count != modifier_blocks:
            failures.append(
                f"foundational {modifier} coverage drift: {count}/{modifier_blocks}"
            )
    ancient_reform_keys = re.findall(
        r"(?m)^([a-z][a-z0-9_]*) = \{$", rendered_reforms
    )
    for on_action in (
        "on_estate_culture_changed",
        "on_estate_religion_changed",
    ):
        if rendered_estate_changes.count(f"{on_action} = {{") != 1:
            failures.append(f"estate settlement lacks exactly one {on_action}")
    for reform in ancient_reform_keys:
        count = rendered_estate_changes.count(
            f"has_reform = government_reform:{reform}"
        )
        if count != 2:
            failures.append(
                f"estate settlement reform coverage drift for {reform}: {count}/2"
            )
    for threshold, adjustment in ESTATE_IDENTITY_SETTLEMENT_FLOOR:
        if rendered_estate_changes.count(f"value < {threshold}") != 2:
            failures.append(
                f"estate settlement threshold coverage drift for {threshold}"
            )
        if rendered_estate_changes.count(f"value = {adjustment}") != 2:
            failures.append(
                f"estate settlement adjustment coverage drift for {adjustment}"
            )
    if rendered_estate_changes.count("\n\t\t\t\ttype = scope:estate\n") != 6:
        failures.append("estate settlement does not target only the changed estate")
    adult_rulers = runtime_adult_rulers(data)
    if re.search(r"(?m)^\s*[a-z0-9_]+\s*=\s*\{", rendered_characters.split("character_db = {", 1)[1]):
        failures.append("bookmark character DB contains a pre-calendar character")
    if rendered_bootstrap.count("\t\t\tcreate_character = {") != len(data.characters):
        failures.append("complete runtime living-court creation inventory drift")
    named_heads = sum(
        1 for government in data.governments.values()
        if has_named_active_head(government)
    )
    if rendered_bootstrap.count("id = antq_m6.1 days = 1") != named_heads:
        failures.append("delayed named-head transition inventory drift")
    if rendered_bootstrap.count("name = antq_m6_opening_ruler") != named_heads:
        failures.append("runtime named-head target inventory drift")
    if rendered_bootstrap.count(
        f"modifier = {ROMAN_SUCCESSION_GUARD} years = -1"
    ) != len(HISTORICAL_LIFESPAN_GUARDED) + 1:
        failures.append("historical character mortality-guard inventory drift")
    for key in ROMAN_SUCCESSION_GUARDED:
        if key == "antq_augustus":
            # The active 1 January holder has engine ID zero, which cannot be
            # persisted in a character variable.  antq_m6.1 stores the age-63
            # handoff character under this key on the next date.
            continue
        short_key = key.removeprefix("antq_")
        if f"name = antq_m6_roman_{short_key}" not in rendered_bootstrap:
            failures.append(f"Roman succession scope is not persisted: {key}")
    varus_guard_anchor = (
        "scope:antq_m6_living_publius_quinctilius_varus = {\n"
        f"\t\t\t\tadd_character_modifier = {{ modifier = {ROMAN_SUCCESSION_GUARD} "
        "years = -1 mode = add_and_extend }"
    )
    if varus_guard_anchor not in rendered_bootstrap:
        failures.append("Varus is not protected through the contingent AD 9 arc")
    if "modifier = antq_augustan_auctoritas years = -1" not in rendered_bootstrap:
        failures.append("Rome lacks the opening Augustan auctoritas crown modifier")
    if rendered_bootstrap.count("add_character_to_first_open_cabinet") != 3:
        failures.append("Rome does not fill three opening cabinet officer slots")
    if "antq_augustan_auctoritas = {" not in ruler_guard_modifier():
        failures.append("Augustan auctoritas modifier definition is missing")
    rendered_transition = ruler_transition_event()
    for token in (
        "set_new_ruler_no_update = scope:antq_m6_opening_ruler_scope",
        "kill_character_silently = scope:antq_m6_departing_ruler",
        "remove_variable = antq_m6_opening_ruler",
        "set_first_name = antq_augustus",
        "save_scope_as = antq_m6_handoff_consort",
        "marry_character_ignore_blocks = scope:antq_m6_handoff_consort",
        "name = antq_m6_roman_augustus value = var:antq_m6_opening_ruler",
    ):
        if token not in rendered_transition:
            failures.append(f"delayed ruler transition lacks {token}")
    for token in (
        "from = 4.2.21",
        "save_scope_as = antq_m6_departing_gaius_caesar",
        "kill_character_silently = scope:antq_m6_departing_gaius_caesar",
        "set_as_designated_heir = scope:antq_m6_tiberius_heir_scope",
        "from = 14.8.19",
        "set_new_ruler_no_update = scope:antq_m6_succeeding_tiberius",
        "kill_character_silently = scope:antq_m6_departing_augustus",
        "name = antq_m6_roman_succession_reserve",
        "set_as_designated_heir = scope:antq_m6_roman_succession_reserve_scope",
        "remove_variable = antq_m6_roman_livia",
    ):
        if token not in rendered_transition:
            failures.append(f"Roman sourced succession lacks {token}")
    for effect in (
        "kill_character_silently",
        "set_as_designated_heir",
        "set_new_ruler",
        "set_new_ruler_no_update",
    ):
        if re.search(rf"\b{effect}\s*=\s*var:", rendered_transition):
            failures.append(
                f"Roman sourced succession passes unsupported variable target to {effect}"
            )
    if (
        "var:antq_m6_roman_tiberius = {\n"
        f"\t\t\t\tremove_character_modifier = {ROMAN_SUCCESSION_GUARD}"
    ) in rendered_transition:
        failures.append("Tiberius mortality guard is removed before the AD 37 horizon")
    if ruler_guard_modifier().count("is_immortal = yes") != 1:
        failures.append("Roman sourced succession guard lost mortality protection")
    if "character:" in rendered_bootstrap:
        failures.append("runtime court bootstrap depends on impossible keyed placeholders")
    roman_government = "\n".join(
        government_block(data.governments["ROM"], runtime_rulers=adult_rulers)
    )
    if "ruler = random" not in roman_government or "antq_augustus" in roman_government:
        failures.append("Roman bookmark government is not runtime-court safe")
    for government in data.governments.values():
        ruler = government["ruler"]
        if ruler not in adult_rulers:
            continue
        rendered_government = "\n".join(
            government_block(government, runtime_rulers=adult_rulers)
        )
        if "ruler = random" not in rendered_government or f"ruler = {ruler}" in rendered_government:
            failures.append(
                f"{government['design_tag']}: pre-calendar named ruler is exposed to bookmark age randomization"
            )
        if f"first_name = {ruler}" not in rendered_bootstrap:
            failures.append(
                f"{government['design_tag']}: adult runtime ruler {ruler} is not recreated"
            )
    for token in (
        "first_name = antq_augustus",
        "first_name = antq_gaius_caesar",
        "first_name = antq_livia",
        "set_as_designated_heir = scope:antq_m6_living_gaius_caesar",
        "marry_character = scope:antq_m6_living_livia",
        "value = scope:antq_m6_living_augustus",
        "value = scope:antq_m6_living_phraates_v",
        "value = scope:antq_m6_living_emperor_ping",
        "set_regent = scope:antq_m6_living_wang_mang",
        "age = { 63 63 }",
        "age = { 9 9 }",
        "marry_character = scope:antq_m6_living_livia",
    ):
        if token not in rendered_bootstrap:
            failures.append(f"Roman runtime officeholder contract lacks {token}")
    visibility_rows = list(csv.DictReader(io.StringIO(reform_visibility_matrix(data))))
    if len(visibility_rows) != len(data.tags):
        failures.append(
            f"reform visibility matrix has {len(visibility_rows)} tags; expected {len(data.tags)}"
        )
    rome_visibility = {
        reform
        for row in visibility_rows if row["design_tag"] == "ROM"
        for reform in row["visible_reforms"].split("|")
    }
    forbidden_rome = {
        "antq_han_imperial_bureaucracy",
        "antq_indo_scythian_kingship",
        "antq_parthian_king_of_kings",
    }
    if rome_visibility & forbidden_rome:
        failures.append(
            f"Roman reform visibility leaks foreign systems {sorted(rome_visibility & forbidden_rome)}"
        )
    for base_reform in {
        reform for reforms_for_profile in PROFILE_BASE_REFORMS.values() for reform in reforms_for_profile
    }:
        start = rendered_reforms.find(f"{base_reform} = {{")
        end = rendered_reforms.find("\n}\n", start)
        if start < 0 or "\n\tpotential = {" not in rendered_reforms[start:end]:
            failures.append(f"base reform {base_reform} lacks an exact-holder potential")
    for value in re.findall(r"(?m)^\s*(?:birth_date|death_date)\s*=\s*(-?\d+\.\d+\.\d+)\s*$", rendered_characters):
        try:
            AntqDate.parse(value)
        except ValueError as exc:
            failures.append(f"generated character date {value} is not campaign-valid ({exc})")
    for path, expected in outputs(data).items():
        if not path.is_file():
            failures.append(f"missing {path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8-sig") != expected:
            failures.append(f"stale {path.relative_to(ROOT)}")
    if not ROSTER_REPORT.is_file():
        failures.append(f"missing {ROSTER_REPORT.relative_to(ROOT)}")
    elif ROSTER_REPORT.read_text(encoding="utf-8") != roster_coverage(data):
        failures.append(f"stale {ROSTER_REPORT.relative_to(ROOT)}")
    if failures:
        print("m6_power: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return False
    print(
        f"m6_power: PASS ({len(data.dynasties)} dynasties, {len(data.characters)} characters, "
        f"{len(data.governments)} governments, {len(data.ruler_terms)} ruler terms, "
        f"{len(data.regnal_histories)} regnal-history rows, {len(data.privileges)} privileges, "
        f"{len(data.laws) + len(s2_profile_law_pairs())} laws; "
        f"{sum(1 for government in data.governments.values() if has_named_active_head(government))} named / "
        f"{sum(1 for government in data.governments.values() if government['ruler'] == 'random')} anonymous profiles)"
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        data = load_power_data()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"m6_power: FAIL\n  - {exc}")
        return 1
    if args.write:
        write(data)
        return 0
    return 0 if check(data) else 1


if __name__ == "__main__":
    raise SystemExit(main())
