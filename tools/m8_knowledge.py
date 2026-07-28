#!/usr/bin/env python3
"""Render and validate ANTIQVITAS's complete M8 knowledge layer.

The installed database is deliberately replaced by exact filenames: continuing
to carry medieval and early-modern advances underneath an ancient tree would
make anachronisms reachable even when the new advances are sound.  This tool
keeps the source manifest tied to the locally pinned EU5 installation and
produces the continuous historical trees from the documented M8 design.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from dates import AntqDate, M2_MIRROR_LANGUAGES
from legacy_institutions import legacy_references, neutralize_references

ROOT = Path(__file__).resolve().parents[1]
ADVANCES = ROOT / "in_game/common/advances"
INSTITUTIONS = ROOT / "in_game/common/institution"
SCRIPTED_TRIGGERS = ROOT / "in_game/common/scripted_triggers"
AUTO_MODIFIERS = ROOT / "in_game/common/auto_modifiers"
STATIC_MODIFIERS = ROOT / "main_menu/common/static_modifiers"
LOC_ROOT = ROOT / "main_menu/localization"
ROSTER = ROOT / "docs/world_1ad/polities.csv"
TAG_PROFILES = ROOT / "docs/m4/tag_profiles.csv"
REGIONAL_PROFILES = ROOT / "docs/m4/regional_profiles.csv"
CULTURES_LEDGER = ROOT / "docs/m4/cultures.csv"
DIRECT_ADVANCE_ART = ROOT / "docs/m11/direct_advance_icons.csv"
ADVANCE_LEDGER = ROOT / "docs/m8/advances.csv"
REACHABILITY_LEDGER = ROOT / "docs/m8/start_research_reachability.csv"
INSTITUTION_LEDGER = ROOT / "docs/m8/institutions.csv"
INSTALLED_INSTITUTION_LEDGER = ROOT / "docs/m8/installed_institution_inventory.csv"
VANILLA_INSTITUTION_SYMBOLS = ROOT / "docs/vanilla_symbols/institution.json"
REGIONAL_BUILDINGS = ROOT / "in_game/common/building_types/00_antiquitas_regional_buildings.txt"
REGIONAL_BUILDING_LEDGER = ROOT / "docs/m5/regional_building_families.csv"
ANCIENT_UNITS = ROOT / "in_game/common/unit_types/00_antiquitas_m7_units.txt"
ANCIENT_REFORMS = ROOT / "in_game/common/government_reforms/00_antiquitas_m6_core.txt"
ANCIENT_PRIVILEGES = ROOT / "in_game/common/estate_privileges/00_antiquitas_m6_core.txt"
ANCIENT_CASUS_BELLI = ROOT / "in_game/common/casus_belli/00_antiquitas_m9.txt"
ANCIENT_SUBJECT_TYPES = ROOT / "in_game/common/subject_types/00_antiquitas_m9_subjects.txt"

AGE_KEYS = (
    "age_1_traditions", "age_2_renaissance", "age_3_discovery",
    "age_4_reformation", "age_5_absolutism", "age_6_revolutions",
)
AGE_NAMES = ("Principate", "High Empires", "Crisis", "Dominate", "Federate Age", "Migrations")
ICONS = (
    "abacus_advance", "legalism_advance", "road_advance_1",
    "crown_power_advance_discovery", "expansionism", "expansionism",
)
FORBIDDEN = (
    "gunpowder", "cannon", "arquebus", "musket", "flintlock", "colonial",
    "ocean_crossing", "steam", "printing_press",
)
UNLOCK = re.compile(r"^\s*unlock_(?:unit|levy)\s*=", re.IGNORECASE)
TOP_LEVEL = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\s*=\s*\{")
POTENTIAL = re.compile(r"^\s*potential\s*=")
CAN_SPAWN = re.compile(r"^\s*can_spawn\s*=")
ALLOW = re.compile(r"^\s*allow\s*=")
CORE_TAGS = frozenset(("ROM", "HAN", "PAR"))
# The AD 1 setup retains a small, engine-native law/policy surface for
# administrative continuity.  M8 replaces the vanilla advances that formerly
# unlocked these categories, so matching ancient advances must carry the
# unlocks or the engine strips otherwise valid start laws at initialization.
# These are mechanics-category bridges, not claims that their vanilla labels
# describe the historical institutions represented by M6's custom adapters.
START_UNLOCKS: dict[str, tuple[tuple[str, str], ...]] = {
    # Every AD 1 technology tier receives the five depth-zero advances.  The
    # installed tribal templates set these two engine-native law categories at
    # creation, so their category bridges must live at that universally held
    # depth rather than at later thematic advances.  This is only a mechanical
    # compatibility mapping; M6's custom laws remain the historical surface.
    "antq_imperial_cult": (
        ("unlock_law", "legal_code_law"),
        ("unlock_law", "education_masses_law"),
        ("unlock_law", "tribal_legal_basis_law"),
    ),
    "antq_provincial_census": (("unlock_law", "administrative_system"),),
    "antq_tax_registers": (("unlock_law", "distribution_of_power_law"),),
    "antq_road_milestones": (("unlock_law", "royal_court_customs_law"),),
    "antq_municipal_charters": (("unlock_law", "feudal_de_jure_law"),),
    # Vanilla's first infantry advance unlocks this court policy.  Its units
    # are deliberately suppressed, but this category bridge is still needed
    # for monarchies that retain the engine-native court selection.
    "antq_professional_standing_armies": (
        ("unlock_law", "medieval_levy_law"),
        ("unlock_policy", "aristocratic_court_policy"),
    ),
    "antq_auxiliary_service": (("unlock_law", "tribal_religious_values_law"),),
    "antq_drill_routines": (("unlock_law", "tribal_organization_law"),),
    "antq_monsoon_navigation": (("unlock_law", "coin_laws"),),
    "antq_red_sea_piloting": (("unlock_law", "mining_law"),),
    "antq_caravan_accounting": (("unlock_law", "immigration_law"),),
    "antq_paper_precursors": (("unlock_law", "cultural_traditions_law"),),
    # Polygyny is a policy inside the religious marriage_law category; it is
    # not itself granted by a vanilla advance.  Unlock its parent category.
    "antq_civic_associations": (("unlock_law", "marriage_law"),),
}

# Engine capabilities that the disabled vanilla traditions tree used to grant.
# These must live on a universally owned Age-I root or every AD 1 state has zero
# tax base and the economy panel immediately declares it bankrupt.  Provincial
# Census is the historical surface; `enable_taxation` and
# `has_stability_investment` are locally verified engine switches.
START_CAPABILITIES: dict[str, tuple[tuple[str, str], ...]] = {
    "antq_provincial_census": (
        ("enable_taxation", "yes"),
        ("has_stability_investment", "yes"),
    ),
}

# Direct ancient-system bridges.  Start reforms and privileges sit on universal
# depth-zero foundations so setup assignments remain valid.  Later political
# forms, diplomacy and every active unit are attached to historically coherent
# branches.  The regional production system is distributed separately below.
CONTENT_UNLOCKS: dict[str, tuple[tuple[str, str], ...]] = {
    "antq_imperial_cult": (
        ("unlock_government_reform", "antq_principate"),
        ("unlock_government_reform", "antq_han_imperial_bureaucracy"),
        ("unlock_government_reform", "antq_lankan_kingdom"),
        ("unlock_government_reform", "antq_indian_ganasangha"),
        ("unlock_government_reform", "antq_indo_scythian_kingship"),
        ("unlock_government_reform", "antq_indo_greek_kingship"),
        ("unlock_government_reform", "antq_parthian_king_of_kings"),
        ("unlock_government_reform", "antq_client_monarchy"),
        ("unlock_government_reform", "antq_parthian_subkingdom"),
        ("unlock_government_reform", "antq_arian_satrapal_court"),
        ("unlock_government_reform", "antq_yuezhi_five_yabghus"),
    ),
    "antq_provincial_census": (
        ("unlock_government_reform", "antq_buffer_kingdom"),
        ("unlock_government_reform", "antq_kushite_dual_kingship"),
        ("unlock_government_reform", "antq_steppe_confederation"),
        ("unlock_government_reform", "antq_xianbei_eastern_confederacy"),
        ("unlock_government_reform", "antq_early_korean_kingdom"),
        ("unlock_government_reform", "antq_regional_kingship"),
        ("unlock_government_reform", "antq_kangju_confederated_kingship"),
        ("unlock_government_reform", "antq_sogdian_city_compact"),
        ("unlock_government_reform", "antq_dayuan_oasis_kingship"),
        ("unlock_government_reform", "antq_wusun_kunmi_confederacy"),
        ("unlock_government_reform", "antq_han_western_regions_kingship"),
        ("unlock_government_reform", "antq_yancai_aorsi_confederacy"),
        ("unlock_government_reform", "antq_saryarka_late_iron_network"),
        ("unlock_government_reform", "antq_altai_contact_network"),
        ("unlock_government_reform", "antq_zhangzhung_plateau_kingship"),
        ("unlock_government_reform", "antq_sumpa_highland_confederacy"),
        ("unlock_government_reform", "antq_changtang_pastoral_network"),
        ("unlock_government_reform", "antq_central_plateau_agropastoral_network"),
        ("unlock_government_reform", "antq_eastern_plateau_corridor_network"),
        ("unlock_government_reform", "antq_tamilakam_velir_court"),
        ("unlock_government_reform", "antq_central_indian_urban_kingship"),
        ("unlock_government_reform", "antq_central_indian_janapada"),
        ("unlock_government_reform", "antq_central_indian_megalithic_network"),
        ("unlock_government_reform", "antq_upper_mahanadi_kingship"),
        ("unlock_government_reform", "antq_mainland_river_corridor_network"),
        ("unlock_government_reform", "antq_sa_huynh_exchange_network"),
        ("unlock_government_reform", "antq_mainland_highland_exchange_network"),
        ("unlock_government_reform", "antq_mainland_iron_age_basin_network"),
        ("unlock_government_reform", "antq_amur_forest_river_network"),
        ("unlock_government_reform", "antq_sakhalin_maritime_network"),
        ("unlock_government_reform", "antq_ussuri_poltsian_network"),
        ("unlock_government_reform", "antq_northern_okjeo_corridor"),
        ("unlock_government_reform", "antq_indian_ocean_atoll_network"),
        ("unlock_government_reform", "antq_advanced_chiefdom"),
        ("unlock_government_reform", "antq_northern_indian_coin_kingship"),
        ("unlock_government_reform", "antq_pundranagara_urban_kingship"),
        ("unlock_government_reform", "antq_bengal_riverine_community_network"),
        ("unlock_government_reform", "antq_eastern_megalithic_community_network"),
        ("unlock_government_reform", "antq_eastern_hill_valley_network"),
        ("unlock_government_reform", "antq_himalayan_highland_network"),
        ("unlock_government_reform", "antq_far_side_port_chiefdom"),
        ("unlock_government_reform", "antq_horn_pastoral_network"),
        ("unlock_government_reform", "antq_west_african_savanna_compound_network"),
        ("unlock_government_reform", "antq_west_african_ironworking_network"),
        ("unlock_government_reform", "antq_west_african_forest_network"),
        ("unlock_government_reform", "antq_early_ironworking_community_network"),
        ("unlock_government_reform", "antq_mobile_hunter_herder_network"),
        ("unlock_government_reform", "antq_settled_town_cluster"),
        ("unlock_government_reform", "antq_tribal_kingdom"),
        ("unlock_government_reform", "antq_artaxiad_highland_kingship"),
        ("unlock_government_reform", "antq_nabataean_caravan_kingship"),
        ("unlock_government_reform", "antq_himyarite_terrace_kingship"),
        ("unlock_government_reform", "antq_satavahana_deccan_kingship"),
        ("unlock_government_reform", "antq_catuvellaunian_oppidum_kingship"),
        ("unlock_government_reform", "antq_trinovantian_coin_kingship"),
        ("unlock_government_reform", "antq_brigantian_hillfort_confederacy"),
        ("unlock_government_reform", "antq_durotrigian_hillfort_coin_order"),
        ("unlock_government_reform", "antq_ivernian_regional_assembly"),
        ("unlock_government_reform", "antq_aestian_amber_coast_order"),
        ("unlock_government_reform", "antq_frisian_terp_community_order"),
        ("unlock_government_reform", "antq_dacian_divided_kingships"),
        ("unlock_government_reform", "antq_garamantian_oasis_state"),
        ("unlock_government_reform", "antq_marcomannic_bohemian_kingship"),
        ("unlock_government_reform", "antq_cheruscan_kindred_assembly"),
        ("unlock_government_reform", "antq_chattian_host_order"),
        ("unlock_government_reform", "antq_batavian_rhine_compact"),
        ("unlock_government_reform", "antq_semnonian_sacred_confederacy"),
        ("unlock_government_reform", "antq_sabaean_marib_kingship"),
        ("unlock_government_reform", "antq_mauretanian_client_kingship"),
        ("unlock_government_reform", "antq_herodian_judean_ethnarchy"),
        ("unlock_government_reform", "antq_cappadocian_client_kingship"),
        ("unlock_government_reform", "antq_odrysian_client_kingship"),
        ("unlock_government_reform", "antq_bosporan_client_kingship"),
        ("unlock_government_reform", "antq_herodian_galilean_tetrarchy"),
        ("unlock_government_reform", "antq_herodian_batanean_tetrarchy"),
        ("unlock_government_reform", "antq_commagenean_client_kingship"),
        ("unlock_government_reform", "antq_emesan_client_dynasty"),
    ),
    "antq_imperial_chancery": (
        ("unlock_government_reform", "antq_dominate"),
    ),
    "antq_regional_commands": (
        ("unlock_government_reform", "antq_sassanid_centralized_monarchy"),
    ),
    "antq_civic_associations": (
        ("unlock_estate_privilege", "antq_indo_scythian_satraps"),
        ("unlock_estate_privilege", "antq_indo_greek_city_elites"),
        ("unlock_estate_privilege", "antq_ganasangha_council"),
        ("unlock_estate_privilege", "antq_lankan_monastic_patronage"),
        ("unlock_estate_privilege", "antq_senatorial_land_exemption"),
        ("unlock_estate_privilege", "antq_equestrian_service"),
        ("unlock_estate_privilege", "antq_roman_priestly_colleges"),
        ("unlock_estate_privilege", "antq_annona_privilege"),
        ("unlock_estate_privilege", "antq_praetorian_donatives"),
        ("unlock_estate_privilege", "antq_han_palace_bureau"),
        ("unlock_estate_privilege", "antq_wang_clan_regency"),
        ("unlock_estate_privilege", "antq_parthian_great_house_autonomy"),
    ),
    "antq_imperial_ceremony": (
        ("unlock_estate_privilege", "antq_client_royal_autonomy"),
        ("unlock_estate_privilege", "antq_kushite_royal_court"),
        ("unlock_estate_privilege", "antq_steppe_clan_autonomy"),
        ("unlock_estate_privilege", "antq_korean_royal_court"),
        ("unlock_estate_privilege", "antq_tribal_elder_council"),
        ("unlock_estate_privilege", "antq_brittonic_druidic_council"),
        ("unlock_estate_privilege", "antq_parthian_subking_autonomy"),
        ("unlock_estate_privilege", "antq_border_court_autonomy"),
        ("unlock_estate_privilege", "antq_second_temple_priesthood"),
        ("unlock_estate_privilege", "antq_regional_royal_court"),
        ("unlock_estate_privilege", "antq_chiefly_court"),
        ("unlock_estate_privilege", "antq_town_cluster_council"),
        ("unlock_estate_privilege", "antq_oppidum_councils"),
        ("unlock_estate_privilege", "antq_hillfort_retinues"),
        ("unlock_estate_privilege", "antq_channel_exchange_compacts"),
        ("unlock_estate_privilege", "antq_hibernian_cattle_compacts"),
        ("unlock_estate_privilege", "antq_hibernian_maritime_followings"),
        ("unlock_estate_privilege", "antq_hibernian_ritual_specialists"),
        ("unlock_estate_privilege", "antq_germanic_assembly_acclamation"),
        ("unlock_estate_privilege", "antq_germanic_household_retainers"),
        ("unlock_estate_privilege", "antq_germanic_sacred_grove_custodians"),
        ("unlock_estate_privilege", "antq_baltic_amber_route_brokers"),
        ("unlock_estate_privilege", "antq_baltic_hillfort_households"),
        ("unlock_estate_privilege", "antq_baltic_burial_custodians"),
        ("unlock_estate_privilege", "antq_przeworsk_smithing_households"),
        ("unlock_estate_privilege", "antq_dyakovo_hillfort_households"),
        ("unlock_estate_privilege", "antq_gorodets_rampart_custodians"),
        ("unlock_estate_privilege", "antq_northern_seasonal_rounds"),
        ("unlock_estate_privilege", "antq_dnieper_river_brokers"),
        ("unlock_estate_privilege", "antq_kama_sanctuary_custodians"),
        ("unlock_estate_privilege", "antq_pyanobor_mortuary_households"),
        ("unlock_estate_privilege", "antq_sargat_kurgan_retinues"),
        ("unlock_estate_privilege", "antq_altai_contact_caravans"),
        ("unlock_estate_privilege", "antq_kulay_casting_households"),
    ),
    "antq_professional_standing_armies": (
        ("unlock_casus_belli", "antq_punitive_expedition"),
        ("unlock_unit", "antq_thureophoroi"),
        ("unlock_unit", "antq_hellenistic_phalanx"),
        ("unlock_unit", "antq_han_crossbow_infantry"),
        ("unlock_unit", "antq_indian_longbowmen"),
        ("unlock_unit", "antq_war_elephants"),
        ("unlock_unit", "antq_nubian_archers"),
        ("unlock_unit", "antq_cataphracts"),
        ("unlock_unit", "antq_parthian_horse_archers"),
        ("unlock_unit", "antq_steppe_horse_archers"),
        ("unlock_unit", "antq_numidian_light_horse"),
        ("unlock_unit", "antq_camelry"),
        ("unlock_unit", "antq_british_chariots"),
        ("unlock_unit", "antq_british_hillfort_spearmen"),
        ("unlock_unit", "antq_northern_british_skirmishers"),
        ("unlock_unit", "antq_hibernian_javelin_bands"),
        ("unlock_unit", "antq_hibernian_coastal_warbands"),
        ("unlock_unit", "antq_angrivarian_spear_following"),
        ("unlock_unit", "antq_suebian_household_retinue"),
        ("unlock_unit", "antq_baltic_hillfort_spearmen"),
        ("unlock_unit", "antq_baltic_forest_skirmishers"),
        ("unlock_unit", "antq_cretan_archers"),
        ("unlock_unit", "antq_saka_horse"),
        ("unlock_unit", "antq_galatian_swordsmen"),
        ("unlock_unit", "antq_thracian_peltasts"),
        ("unlock_unit", "antq_numidian_horse_company"),
        ("unlock_unit", "antq_parthian_foot_archers"),
        ("unlock_unit", "antq_parthian_noble_lancers"),
        ("unlock_unit", "antq_syrian_archers"),
        ("unlock_unit", "antq_iberian_swordsmen"),
        ("unlock_unit", "antq_dacian_falxmen"),
        ("unlock_unit", "antq_armenian_horse"),
    ),
    "antq_auxiliary_service": (
        ("unlock_unit", "antq_trireme"),
        ("unlock_unit", "antq_merchant_roundship"),
        ("unlock_unit", "antq_monsoon_dhow"),
        ("unlock_unit", "antq_austronesian_outrigger"),
        ("unlock_unit", "antq_cilician_marines"),
    ),
    "antq_drill_routines": (
        ("unlock_unit", "antq_legionaries"),
        ("unlock_unit", "antq_auxilia"),
        ("unlock_unit", "antq_roman_alae"),
        ("unlock_unit", "antq_roman_marines"),
        ("unlock_unit", "antq_roman_sagittarii"),
        ("unlock_unit", "antq_roman_scouts"),
        ("unlock_unit", "antq_balearic_slingers"),
    ),
    "antq_river_crossings": (
        ("unlock_unit", "antq_liburnian"),
        ("unlock_unit", "antq_quinquereme"),
    ),
    "antq_frontier_patrols": (
        ("unlock_unit", "antq_germanic_horse"),
        ("unlock_unit", "antq_germanic_bodyguards"),
    ),
    "antq_comitatenses_doctrine": (("unlock_unit", "antq_comitatenses"),),
    "antq_limitanei_service": (("unlock_unit", "antq_limitanei"),),
    "antq_tax_registers": (
        ("unlock_subject_type", "antq_client_kingdom"),
        ("unlock_casus_belli", "antq_impose_client_king"),
    ),
    "antq_library_catalogues": (
        ("unlock_subject_type", "antq_satrapy"),
        ("unlock_casus_belli", "antq_sasanid_unification"),
    ),
    "antq_legal_petitions": (
        ("unlock_subject_type", "antq_tributary"),
        ("unlock_casus_belli", "antq_chinese_warlord_unification"),
    ),
    "antq_municipal_charters": (("unlock_subject_type", "antq_autonomous_city"),),
    "antq_monsoon_navigation": (("unlock_casus_belli", "antq_demand_tribute"),),
    "antq_road_milestones": (("unlock_casus_belli", "antq_frontier_rectification"),),
    "antq_field_engineering": (
        ("unlock_unit", "antq_warbands"),
        ("unlock_unit", "antq_germanic_spearmen"),
        ("unlock_unit", "antq_germanic_javelins"),
        ("unlock_casus_belli", "antq_loot_raid"),
    ),
    "antq_port_customs": (("unlock_casus_belli", "antq_succession_intervention"),),
    "antq_orthodoxy_debates": (("unlock_casus_belli", "antq_holy_suppression"),),
    "antq_federate_musters": (("unlock_subject_type", "antq_foederati"),),
    "antq_seasonal_markets": (("unlock_casus_belli", "antq_gupta_digvijaya"),),
}


# Five ten-step strands run through the plan's five conceptual arcs; the
# mandatory sixth engine slot divides the final arc into two five-step halves.
# Their names are the source-led historical statements; individual mechanical
# effects stay bounded to locally verified engine contracts in M9/M10.
TRACKS: dict[str, tuple[tuple[str, ...], ...]] = {
    "statecraft": (
        ("imperial_cult", "provincial_census", "tax_registers", "road_milestones", "legal_petitions", "municipal_charters", "public_granaries", "frontier_dispatches", "imperial_archives", "standing_administration"),
        ("jurists_law", "commentary_schools", "provincial_assizes", "civic_patronage", "municipal_accounting", "estate_registries", "imperial_rescripts", "law_of_persons", "provincial_governance", "high_empire_administration"),
        ("crisis_coinage", "emergency_levies", "fiscal_reassessment", "mint_accounting", "regional_commands", "emergency_rescripts", "grain_annona", "imperial_dioceses", "revenue_recovery", "crisis_statecraft"),
        ("diocesan_administration", "codification", "notarial_offices", "imperial_chancery", "provincial_prefects", "tax_in_kind", "public_post", "legal_compilations", "late_roman_bureaucracy", "dominate_statecraft"),
        ("kingdom_charters", "barbarian_hospitality", "land_assignment", "successor_taxation", "royal_notaries", "regional_law_codes", "mixed_courts", "settlement_registers", "kingdom_building", "post_roman_statecraft"),
    ),
    "warfare": (
        ("professional_standing_armies", "auxiliary_service", "drill_routines", "supply_columns", "field_engineering", "frontier_patrols", "river_crossings", "siegecraft_basics", "legionary_logistics", "principate_warfare"),
        ("cataphract_adoption", "composite_bow_tactics", "camel_screening", "frontier_cavalry", "mounted_scouts", "heavy_cavalry_drill", "campaign_seasons", "deep_defence", "imperial_field_forces", "high_empire_warfare"),
        ("mobile_field_armies", "crisis_fortification", "wall_building", "beacon_networks", "regional_reserves", "cavalry_screening", "siege_relief", "marching_camps", "defence_in_depth", "crisis_warfare"),
        ("comitatenses_doctrine", "limitanei_service", "foederati_settlement", "heavy_lancer_refinement", "military_bureaux", "fortified_crossings", "mobile_reserves", "frontier_commands", "late_antique_logistics", "dominate_warfare"),
        ("federate_musters", "settlement_service", "warband_integration", "horse_furniture", "shield_wall_tactics", "regional_militias", "successor_armies", "frontier_kingdoms", "migration_warfare", "late_antique_arms"),
    ),
    "exchange": (
        ("monsoon_navigation", "red_sea_piloting", "caravan_accounting", "silk_exchange", "port_customs", "desert_waystations", "merchant_diasporas", "coin_exchange", "seasonal_markets", "principate_exchange"),
        ("silk_road_caravanserais", "long_distance_credit", "market_regulation", "eastern_mediterranean_routes", "indian_ocean_monsoons", "border_customs", "merchant_associations", "warehouse_accounts", "imperial_trade", "high_empire_exchange"),
        ("crisis_trade_routes", "debased_currency_exchange", "military_supply_markets", "fortified_warehouses", "caravan_protection", "regional_exchange", "grain_convoys", "emergency_tolls", "resilient_markets", "crisis_exchange"),
        ("state_annona_routes", "bureaucratic_customs", "foederati_provisioning", "frontier_market_towns", "church_storehouses", "caravan_tolls", "late_antique_coinage", "regional_fairs", "dominate_exchange", "late_antique_commerce"),
        ("migration_market_links", "gift_exchange", "kingdom_tolls", "riverine_trade", "settlement_markets", "regional_caravans", "successor_coinage", "frontier_fairs", "kingdom_exchange", "post_roman_commerce"),
    ),
    "learning": (
        ("paper_precursors", "bamboo_registers", "library_catalogues", "han_classics", "astronomical_tables", "medical_compendia", "legal_commentaries", "surveying_methods", "scholarly_correspondence", "principate_learning"),
        ("juristic_schools", "mathematical_handbooks", "medical_schools", "textual_criticism", "observatory_records", "library_endowments", "philosophical_dialogue", "engineering_manuals", "scholarly_networks", "high_empire_learning"),
        ("crisis_scholarly_preservation", "portable_archives", "clerical_literacy", "military_manuals", "medical_relief", "calendar_revision", "epistolary_networks", "regional_schools", "crisis_learning", "survival_of_texts"),
        ("state_church", "monastic_scriptoria", "orthodoxy_debates", "codex_manuscripts", "legal_scholars", "bureaucratic_education", "commentary_traditions", "late_antique_schools", "doctrinal_debate", "dominate_learning"),
        ("monastic_libraries", "translation_circles", "kingdom_schools", "clerical_recordkeeping", "lawbook_copying", "regional_chronicles", "successor_scholarship", "pilgrim_learning", "migration_learning", "late_antique_letters"),
    ),
    "society": (
        ("civic_associations", "imperial_ceremony", "urban_waterworks", "public_baths", "religious_endowments", "veteran_settlement", "provincial_elites", "ritual_calendars", "civic_identity", "principate_society"),
        ("cosmopolitan_cities", "public_philanthropy", "legal_statuses", "religious_plurals", "urban_professions", "provincial_citizenship", "athletic_festivals", "scholarly_patronage", "high_empire_society", "imperial_cultures"),
        ("crisis_communities", "refugee_settlement", "plague_relief", "local_patronage", "religious_consolation", "fortified_towns", "rural_resilience", "civic_recovery", "crisis_society", "surviving_cities"),
        ("church_endowments", "monastic_communities", "imperial_orthodoxy", "settled_foederati", "late_antique_cities", "charitable_hospices", "regional_elites", "religious_law", "dominate_society", "late_antique_communities"),
        ("hospitality_of_barbarians", "mixed_settlements", "kingdom_churches", "regional_identities", "customary_law", "migration_networks", "successor_elites", "rural_communities", "migrations_society", "roman_successor_worlds"),
    ),
}


@dataclass(frozen=True)
class Advance:
    key: str
    name: str
    age: str
    age_index: int
    depth: int
    track: str
    profile: str
    requires: tuple[str, ...]
    effects: tuple[tuple[str, str], ...]
    description: str
    source: str


@dataclass(frozen=True)
class Institution:
    key: str
    name: str
    description: str
    age: str
    location: str
    start_active: bool
    earliest: str
    spread_band: str
    profile: str
    trade_spread: bool
    source: str


@dataclass(frozen=True)
class InstitutionProfile:
    key: str
    summary: str
    script: tuple[str, ...]


@dataclass(frozen=True)
class AdvanceProfile:
    key: str
    name: str
    summary: str
    culture_groups: tuple[str, ...]
    adoption_institutions: tuple[str, ...]
    source: str


ADVANCE_PROFILES = {
    profile.key: profile
    for profile in (
        AdvanceProfile(
            "shared", "Shared Foundations",
            "Practices transferable across several ancient political and cultural settings.",
            (), (), "P15;CAH-XI;CAH-XII",
        ),
        AdvanceProfile(
            "roman_italic", "Roman and Italic",
            "Roman and Italic civic, legal, logistical, and imperial practice.",
            ("antq_italic_group", "antq_iberian_group", "antq_balkan_group"),
            ("antq_roman_law_engineering",), "P8.1;P15;CAH-XI;OCD",
        ),
        AdvanceProfile(
            "hellenic", "Hellenic",
            "Hellenic civic, scholarly, military, and eastern Mediterranean practice.",
            ("antq_hellenic_group", "antq_anatolian_group"),
            ("antq_hellenism",), "P8.1;P15;CAH-XI;OCD",
        ),
        AdvanceProfile(
            "celtic", "Celtic and Brittonic",
            "Celtic and Brittonic political, martial, exchange, and community practice.",
            ("antq_celtic_group",),
            ("antq_foederati_statecraft",), "P8.7;P15;CAH-XI",
        ),
        AdvanceProfile(
            "germanic", "Germanic",
            "Germanic assembly, warband, settlement, exchange, and confederation practice.",
            ("antq_germanic_group",),
            ("antq_foederati_statecraft",), "P8.7;P15;CAH-XI;STR-GER",
        ),
        AdvanceProfile(
            "iranian_steppe", "Iranian and Steppe",
            "Iranian court, cavalry, caravan, and steppe-confederation practice.",
            ("antq_iranian_group", "antq_steppe_group"),
            ("antq_cataphract_warfare",), "P8.2;P8.8;P15;CAH-XI",
        ),
        AdvanceProfile(
            "indic", "Indic",
            "Indic court, monastic, agrarian, military, and Indian Ocean practice.",
            ("antq_indian_group", "antq_tibetan_group"),
            ("antq_buddhist_monasticism",), "P8.4;P15;CAH-XI",
        ),
        AdvanceProfile(
            "han_east_asian", "Han and East Asian",
            "Han and neighbouring East Asian administrative, textual, military, and agrarian practice.",
            ("antq_sinitic_group", "antq_korean_group", "antq_japonic_group"),
            ("antq_han_bureaucratic_statecraft", "antq_papermaking"),
            "P8.3;P15;BHR;Bielenstein",
        ),
        AdvanceProfile(
            "near_eastern", "Near Eastern",
            "Levantine, Anatolian, Mesopotamian, and Caucasian urban and caravan practice.",
            ("antq_semitic_group", "antq_anatolian_group", "antq_caucasian_group"),
            ("antq_theological_orthodoxy",), "P8.1;P8.2;P15;CAH-XI",
        ),
        AdvanceProfile(
            "african", "African",
            "Nile, Maghrebi, Red Sea, and sub-Saharan political and exchange practice.",
            ("antq_nile_group", "antq_berber_group", "antq_subsaharan_group"),
            ("antq_christian_monasticism",), "P8.5;P15;CAH-XI",
        ),
        AdvanceProfile(
            "american", "American",
            "Regionally bounded American urban, agrarian, exchange, and political practice.",
            ("antq_american_group", "antq_mesoamerican_group", "antq_andean_group"),
            (), "P8.10;P15",
        ),
        AdvanceProfile(
            "oceanian", "Austronesian and Oceanian",
            "Austronesian, Southeast Asian, and Oceanian maritime and community practice.",
            ("antq_austronesian_group", "antq_oceanic_group", "antq_southeast_asian_group"),
            (), "P8.9;P15",
        ),
        AdvanceProfile(
            "baltic", "Baltic",
            "Amber-coast, hillfort, mortuary, river-portage, and seasonal assembly practice.",
            ("antq_baltic_group",),
            (), "P8.7;P15;TAC-GER;PAN-WBB",
        ),
        AdvanceProfile(
            "slavic_eastern", "Vistula, Dnieper, and Eastern European",
            "Archaeologically bounded forest, river, settlement, and household practices without projecting later states.",
            ("antq_slavic_group",),
            (), "P8.7;P15;AWE-DNIEPER-DVINA;ENC-NEEU",
        ),
        AdvanceProfile(
            "uralic", "Volga, Kama, and Northern Forest",
            "River-portage, sanctuary, metallurgical, oral, and seasonal-round practices of the northern forest and forest-steppe.",
            ("antq_uralic_group",),
            (), "P8.7;P15;BSE-GORODETS;BSE-GLYADENOVO;BSE-UST-POLUY",
        ),
    )
}

S2_ESTATE_PRIVILEGES = ROOT / "docs/m6/estate_order_privileges.csv"
S2_ALTERNATIVE_REFORMS = ROOT / "docs/m6/alternative_reform_paths.csv"
S2_ANCIENT_LAWS = ROOT / "docs/m6/ancient_law_options.csv"
S2_ESTATE_ADVANCE_PROFILES: dict[str, tuple[str, ...]] = {
    "roman": ("roman_italic",),
    "late_roman": ("roman_italic",),
    "han": ("han_east_asian",),
    "late_han": ("han_east_asian",),
    "iranian": ("iranian_steppe",),
    "sasanian": ("iranian_steppe",),
    "civic": ("hellenic",),
    "gana": ("indic",),
    "steppe": ("iranian_steppe",),
    "tribal": ("celtic", "germanic"),
    "sacral": ("african", "indic"),
    "royal": ("near_eastern", "han_east_asian", "african"),
    "xiongnu": ("iranian_steppe",),
    "xianbei": ("iranian_steppe",),
    "goguryeo": ("han_east_asian",),
    "kushite": ("african",),
    "lankan": ("indic",),
    "armenian": ("iranian_steppe",),
    "nabataean": ("near_eastern",),
    "himyarite": ("near_eastern",),
    "satavahana": ("indic",),
    "cheruscan": ("germanic",),
    "chattian": ("germanic",),
    "batavian": ("germanic",),
    "semnonian": ("germanic",),
    "catuvellaunian": ("celtic",),
    "trinovantian": ("celtic",),
    "brigantian": ("celtic",),
    "durotrigian": ("celtic",),
    "ivernian": ("celtic",),
    "aestian": ("baltic",),
    "frisian": ("germanic",),
    "dacian": ("hellenic",),
    "garamantian": ("african",),
    "marcomannic": ("germanic",),
    "sabaean": ("near_eastern",),
    "mauretanian": ("african",),
    "judean": ("near_eastern",),
    "cappadocian": ("hellenic",),
    "thracian": ("hellenic",),
    "bosporan": ("hellenic", "iranian_steppe"),
    "galilean": ("near_eastern",),
    "batanean": ("near_eastern",),
    "commagenean": ("near_eastern", "hellenic"),
    "emesan": ("near_eastern",),
}

# Each engine age contains five compact trees. The first four ages use two
# shared roots and two culturally bounded branches with internal convergence;
# the two five-node late ages use one shared root and two bounded branches.
BRANCH_PROFILES: dict[str, tuple[tuple[str, str], ...]] = {
    "statecraft": (
        ("roman_italic", "han_east_asian"),
        ("hellenic", "iranian_steppe"),
        ("near_eastern", "indic"),
        ("roman_italic", "african"),
        ("germanic", "celtic"),
        ("american", "oceanian"),
    ),
    "warfare": (
        ("roman_italic", "germanic"),
        ("american", "celtic"),
        ("han_east_asian", "african"),
        ("indic", "near_eastern"),
        ("germanic", "roman_italic"),
        ("roman_italic", "germanic"),
    ),
    "exchange": (
        ("indic", "near_eastern"),
        ("han_east_asian", "african"),
        ("roman_italic", "iranian_steppe"),
        ("celtic", "germanic"),
        ("american", "oceanian"),
        ("hellenic", "near_eastern"),
    ),
    "learning": (
        ("iranian_steppe", "hellenic"),
        ("indic", "roman_italic"),
        ("hellenic", "germanic"),
        ("hellenic", "iranian_steppe"),
        ("han_east_asian", "indic"),
        ("iranian_steppe", "han_east_asian"),
    ),
    "society": (
        ("american", "oceanian"),
        ("oceanian", "near_eastern"),
        ("african", "american"),
        ("indic", "han_east_asian"),
        ("germanic", "iranian_steppe"),
        ("oceanian", "celtic"),
    ),
}

TRACK_EFFECTS: dict[str, tuple[tuple[str, str], ...]] = {
    "statecraft": (
        ("country_cabinet_efficiency", "0.01"),
        ("stability_cost_efficiency", "0.02"),
        ("global_monthly_control", "0.001"),
        ("tax_income_efficiency", "small_tax_income_efficiency_bonus"),
        ("legislative_efficiency", "0.05"),
    ),
    "warfare": (
        ("levy_recovery_modifier", "0.01"),
        ("army_logistics_distance_modifier", "0.10"),
        ("army_maintenance_efficiency", "0.01"),
        ("land_morale_modifier", "0.01"),
        ("discipline", "0.005"),
    ),
    "exchange": (
        ("trade_range_modifier", "0.02"),
        ("merchant_maintenance_efficiency", "0.01"),
        ("global_trade_through_owned_territory_efficiency", "0.05"),
        ("import_efficiency", "tiny_trade_efficiency_bonus"),
        ("export_efficiency", "small_trade_efficiency_bonus"),
    ),
    "learning": (
        ("research_speed_modifier", "0.01"),
        ("cultural_influence_modifier", "0.01"),
        ("global_monthly_literacy", "0.005"),
        ("global_institution_growth_modifier", "0.10"),
        ("research_speed_modifier", "0.015"),
    ),
    "society": (
        ("global_disease_resistance", "0.005"),
        ("global_population_capacity_modifier", "0.02"),
        ("global_pop_promotion_speed_modifier", "0.025"),
        ("global_pop_assimilation_speed_modifier", "0.025"),
        ("stability_cost_efficiency", "0.02"),
    ),
}

# User-requested first tranche of the 3x advance expansion.  Twenty-two
# five-node regional paths add 110 Age-I advances without creating isolated
# roots: each path branches at its second node, converges, and ends in a
# culture-bounded capstone.  Later ages receive equivalent depth in subsequent
# tranches; this opening tranche first fixes every AD 1 start.
AGE1_EXPANSION: dict[str, tuple[tuple[str, tuple[str, ...]], ...]] = {
    "statecraft": (
        ("celtic", (
            "oppidum_council_summons", "guest_friends_arbitration",
            "tribute_feast_tallies", "clientage_oath_networks",
            "confederated_council_customs",
        )),
        ("african", (
            "meroitic_temple_stewardship", "kandake_court_delegates",
            "oasis_tribute_stations", "nile_caravan_adjudication",
            "royal_storehouse_seals",
        )),
        ("baltic", (
            "amber_coast_assemblies", "hillfort_household_speakers",
            "burial_community_custodians", "coastal_route_arbitration",
            "intercommunity_oath_circles",
        )),
        ("uralic", (
            "seasonal_round_councils", "river_portage_stewards",
            "sanctuary_offering_custody", "forest_steppe_envoys",
            "dispersed_household_compacts",
        )),
    ),
    "warfare": (
        ("iranian_steppe", (
            "remount_pasture_registers", "horse_archer_screening",
            "scale_armour_workshops", "armoured_retinue_drill",
            "cataphract_reserve_system",
        )),
        ("indic", (
            "elephant_corps_stables", "longbow_guild_levies",
            "fortified_river_camps", "monsoon_campaign_stores",
            "frontier_gana_musters",
        )),
        ("celtic", (
            "hillfort_muster_beacons", "chariot_screening",
            "champion_retinues", "oppidum_supply_caches",
            "confederate_war_councils",
        )),
        ("slavic_eastern", (
            "forest_ambush_routes", "riverine_spear_musters",
            "dugout_crossing_craft", "fortified_refuge_settlements",
            "seasonal_warband_leadership",
        )),
    ),
    "exchange": (
        ("roman_italic", (
            "amphora_capacity_standards", "publicani_freight_contracts",
            "river_port_dues", "collegia_distribution_halls",
            "annona_coastal_convoys",
        )),
        ("han_east_asian", (
            "bronze_cash_strings", "state_granary_carriage",
            "relay_market_stations", "salt_iron_bureau_exchange",
            "western_regions_caravan_seals",
        )),
        ("african", (
            "garamantian_oasis_stages", "meroe_nile_caravans",
            "red_sea_entrepots", "sahel_iron_exchange",
            "ivory_route_brokers",
        )),
        ("baltic", (
            "amber_route_waystations", "coastal_hide_fairs",
            "river_portage_exchange", "bloomery_iron_barter",
            "seasonal_market_circuits",
        )),
    ),
    "learning": (
        ("hellenic", (
            "polis_archive_stewards", "peripatetic_teaching_circles",
            "geometric_commentary_schools", "medical_case_histories",
            "interpolis_scholarly_correspondence",
        )),
        ("roman_italic", (
            "agrimensor_field_books", "augural_calendar_tables",
            "juristic_responsa", "legionary_commentarii",
            "provincial_archive_copying",
        )),
        ("han_east_asian", (
            "bamboo_slip_collation", "clerical_script_examinations",
            "calendrical_offices", "hydraulic_administration_manuals",
            "court_classics_recensions",
        )),
        ("indic", (
            "brahmi_scribal_schools", "recitation_lineages",
            "ayurvedic_compendia", "astronomical_reckoning",
            "monastic_text_collections",
        )),
        ("uralic", (
            "route_memory_specialists", "seasonal_ecological_calendars",
            "metalworking_apprenticeships", "ritual_poetry_lineages",
            "interregional_oral_exchanges",
        )),
    ),
    "society": (
        ("american", (
            "monumental_precinct_stewardship", "communal_field_schedules",
            "lineage_feast_obligations", "ritual_exchange_journeys",
            "seasonal_ceremonial_calendars",
        )),
        ("near_eastern", (
            "temple_city_almonries", "synagogue_councils",
            "caravan_diaspora_quarters", "civic_cult_associations",
            "village_elder_compacts",
        )),
        ("germanic", (
            "household_retinue_feasts", "sacred_grove_custody",
            "wergild_arbitration", "fosterage_and_hostages",
            "assembly_acclamation_customs",
        )),
        ("slavic_eastern", (
            "riverside_hamlet_cooperation", "household_oven_clusters",
            "seasonal_forest_clearings", "mortuary_community_feasts",
            "intersettlement_marriage_networks",
        )),
        ("oceanian", (
            "outrigger_kin_voyages", "shell_valuables_exchange",
            "navigational_star_lore", "stilt_settlement_compacts",
            "island_feast_redistribution",
        )),
    ),
}

TRACK_DESCRIPTIONS = {
    "statecraft": "recordkeeping, adjudication, revenue, and political coordination",
    "warfare": "recruitment, command, logistics, fortification, and battlefield practice",
    "exchange": "market, caravan, maritime, monetary, and provisioning networks",
    "learning": "textual, scientific, legal, medical, and educational traditions",
    "society": "civic, religious, household, settlement, and welfare institutions",
}


INSTITUTION_PROFILES = {
    profile.key: profile
    for profile in (
        InstitutionProfile(
            "mediterranean_letters",
            "Mediterranean civic and learned networks",
            (
                "OR = {",
                "\tregion = region:italy_region",
                "\tregion = region:balkan_region",
                "\tregion = region:anatolia_region",
                "\tregion = region:egypt_region",
                "\tregion = region:crescent_region",
                "}",
            ),
        ),
        InstitutionProfile(
            "roman_imperial_practice",
            "Roman and provincial societies inside the historical imperial sphere",
            (
                "AND = {",
                "\tOR = {",
                "\t\tregion = region:italy_region",
                "\t\tregion = region:iberia_region",
                "\t\tregion = region:france_region",
                "\t\tregion = region:great_britain_region",
                "\t\tregion = region:north_german_region",
                "\t\tregion = region:south_german_region",
                "\t\tregion = region:balkan_region",
                "\t\tregion = region:anatolia_region",
                "\t\tregion = region:crescent_region",
                "\t\tregion = region:egypt_region",
                "\t\tregion = region:maghreb_region",
                "\t}",
                "\tOR = {",
                "\t\tdominant_culture = { has_culture_group = culture_group:antq_italic_group }",
                "\t\tdominant_culture = { has_culture_group = culture_group:antq_hellenic_group }",
                "\t\tdominant_culture = { has_culture_group = culture_group:antq_celtic_group }",
                "\t\tdominant_culture = { has_culture_group = culture_group:antq_iberian_group }",
                "\t\tdominant_culture = { has_culture_group = culture_group:antq_anatolian_group }",
                "\t\tdominant_culture = { has_culture_group = culture_group:antq_semitic_group }",
                "\t\tdominant_culture = { has_culture_group = culture_group:antq_berber_group }",
                "\t}",
                "}",
            ),
        ),
        InstitutionProfile(
            "east_asian_administration",
            "Sinitic, Korean, and adjacent East Asian administrative contexts",
            (
                "AND = {",
                "\tOR = {",
                "\t\tregion = region:east_china_region",
                "\t\tregion = region:north_china_region",
                "\t\tregion = region:south_china_region",
                "\t\tregion = region:west_china_region",
                "\t\tregion = region:korea_region",
                "\t\tregion = region:manchuria_region",
                "\t\tregion = region:indochina_region",
                "\t}",
                "\tOR = {",
                "\t\tdominant_culture = { has_culture_group = culture_group:antq_sinitic_group }",
                "\t\tdominant_culture = { has_culture_group = culture_group:antq_korean_group }",
                "\t\tdominant_culture = { has_culture_group = culture_group:antq_southeast_asian_group }",
                "\t}",
                "}",
            ),
        ),
        InstitutionProfile(
            "buddhist_networks",
            "Buddhist communities across South, Central, and East Asian corridors",
            (
                "OR = {",
                "\tdominant_religion = { group = religion_group:antq_buddhist_group }",
                "\tregion = region:bengal_region",
                "\tregion = region:central_india_region",
                "\tregion = region:deccan_region",
                "\tregion = region:hindustan_region",
                "\tregion = region:western_india_region",
                "\tregion = region:xinjiang_region",
                "\tregion = region:tibet_region",
                "\tregion = region:east_china_region",
                "\tregion = region:north_china_region",
                "\tregion = region:south_china_region",
                "\tregion = region:west_china_region",
                "\tregion = region:korea_region",
                "\tregion = region:indochina_region",
                "}",
            ),
        ),
        InstitutionProfile(
            "iranian_steppe_cavalry",
            "Iranian, steppe, Caucasian, and eastern Roman military corridors",
            (
                "OR = {",
                "\tregion = region:persia_region",
                "\tregion = region:khorasan_region",
                "\tregion = region:steppes_region",
                "\tregion = region:caucasus_region",
                "\tregion = region:xinjiang_region",
                "\tregion = region:anatolia_region",
                "\tregion = region:crescent_region",
                "\tregion = region:balkan_region",
                "\tdominant_culture = { has_culture_group = culture_group:antq_iranian_group }",
                "\tdominant_culture = { has_culture_group = culture_group:antq_steppe_group }",
                "}",
            ),
        ),
        InstitutionProfile(
            "east_central_asian_paper",
            "East and Central Asian craft-transfer corridors",
            (
                "OR = {",
                "\tregion = region:east_china_region",
                "\tregion = region:north_china_region",
                "\tregion = region:south_china_region",
                "\tregion = region:west_china_region",
                "\tregion = region:korea_region",
                "\tregion = region:manchuria_region",
                "\tregion = region:xinjiang_region",
                "\tregion = region:indochina_region",
                "}",
            ),
        ),
        InstitutionProfile(
            "christian_monastic",
            "Locations whose dominant faith belongs to the Christian family",
            (
                "dominant_religion = { group = religion_group:antq_christian_group }",
            ),
        ),
        InstitutionProfile(
            "christian_councils",
            "Christian communities participating in conciliar networks",
            (
                "dominant_religion = { group = religion_group:antq_christian_group }",
            ),
        ),
        InstitutionProfile(
            "late_roman_frontier",
            "Late Roman and neighboring federate settlement zones",
            (
                "AND = {",
                "\tOR = {",
                "\t\tregion = region:balkan_region",
                "\t\tregion = region:carpathia_region",
                "\t\tregion = region:north_german_region",
                "\t\tregion = region:south_german_region",
                "\t\tregion = region:france_region",
                "\t\tregion = region:italy_region",
                "\t\tregion = region:great_britain_region",
                "\t\tregion = region:anatolia_region",
                "\t\tregion = region:steppes_region",
                "\t}",
                "\tOR = {",
                "\t\tdominant_culture = { has_culture_group = culture_group:antq_italic_group }",
                "\t\tdominant_culture = { has_culture_group = culture_group:antq_hellenic_group }",
                "\t\tdominant_culture = { has_culture_group = culture_group:antq_germanic_group }",
                "\t\tdominant_culture = { has_culture_group = culture_group:antq_celtic_group }",
                "\t\tdominant_culture = { has_culture_group = culture_group:antq_steppe_group }",
                "\t}",
                "}",
            ),
        ),
    )
}


INSTITUTION_DATA = (
    Institution("antq_hellenism", "Hellenism", "A living network of Greek civic, literary, and sacred institutions.", "age_1_traditions", "athens", True, "1.1.1", "early", "mediterranean_letters", True, "P14.3;CAH-XI"),
    Institution("antq_roman_law_engineering", "Roman Law and Engineering", "Roman legal practice and public engineering circulate through imperial networks.", "age_1_traditions", "rome", True, "1.1.1", "early", "roman_imperial_practice", True, "P14.3;OCD;CAH-XI"),
    Institution("antq_han_bureaucratic_statecraft", "Han Bureaucratic Statecraft", "Written administration, registers, and examination-minded statecraft radiate from Han China.", "age_1_traditions", "jingzhao", True, "1.1.1", "early", "east_asian_administration", False, "P14.3;BHR;Bielenstein"),
    Institution("antq_buddhist_monasticism", "Buddhist Monasticism", "Buddhist monastic communities preserve learning and create durable religious networks.", "age_1_traditions", "anuradhapura", True, "1.1.1", "early", "buddhist_networks", True, "P14.3;CAH-XI"),
    Institution("antq_cataphract_warfare", "Cataphract Warfare", "Heavy armoured cavalry methods circulate from the Iranian and steppe worlds.", "age_2_renaissance", "merv", False, "96.1.1", "early", "iranian_steppe_cavalry", False, "P14.3;CAH-XI"),
    Institution("antq_papermaking", "Papermaking", "Paper and its associated craft knowledge spread outward from Luoyang.", "age_2_renaissance", "luoyang", False, "105.1.1", "mid", "east_central_asian_paper", True, "P14.3;BHR"),
    Institution("antq_christian_monasticism", "Christian Monasticism", "Egyptian ascetic communities establish a second monastic centre of gravity.", "age_3_discovery", "alexandria", False, "270.1.1", "mid", "christian_monastic", True, "P14.3;CAH-XII"),
    Institution("antq_theological_orthodoxy", "Theological Orthodoxy", "Council-led doctrinal settlement shapes the late Roman religious world.", "age_4_reformation", "iznik", False, "325.1.1", "late", "christian_councils", False, "P14.3;CAH-XII"),
    Institution("antq_foederati_statecraft", "Foederati Statecraft", "Land-for-service settlements become a deliberate frontier and imperial practice.", "age_5_absolutism", "edirne", False, "382.1.1", "late", "late_roman_frontier", False, "P14.3;AMM-31"),
)

# The institution manager resolves an exact institution_birth static modifier
# at every origin. Each value stays below the comparable vanilla birth
# modifier: these are small local advantages, not a substitute for research,
# institutions, or the dated historical currents.
INSTITUTION_BIRTH_EFFECTS: dict[str, tuple[str, str]] = {
    "antq_hellenism": ("local_cultural_influence", "0.10"),
    "antq_roman_law_engineering": ("local_monthly_development", "0.001"),
    "antq_han_bureaucratic_statecraft": ("local_cultural_tradition", "0.10"),
    "antq_buddhist_monasticism": ("local_max_literacy", "1"),
    "antq_cataphract_warfare": ("local_manpower_modifier", "0.05"),
    "antq_papermaking": ("local_max_literacy", "2"),
    "antq_christian_monasticism": ("local_pop_conversion_speed_modifier", "0.10"),
    "antq_theological_orthodoxy": ("local_pop_conversion_speed_modifier", "0.20"),
    "antq_foederati_statecraft": ("local_levy_size_modifier", "0.05"),
}


def installed_dir(relative: str) -> Path:
    config = json.loads((ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig"))
    return Path(config["game_dir"]) / "game" / relative


def advance_description(name: str, track: str, profile: str, age_index: int) -> str:
    context = ADVANCE_PROFILES[profile]
    return (
        f"{name} represents {TRACK_DESCRIPTIONS[track]} within "
        f"{context.name.lower()} contexts during the {AGE_NAMES[age_index]}."
    )


def advance_display_name(name: str, profile: str) -> str:
    """Expose the regional path in the UI without discarding reviewed icon keys."""
    display = name.replace("_", " ").title()
    if profile == "shared":
        return display
    # A handful of preserved art keys contain a culture-specific noun even
    # when the new DAG assigns that visual concept to a transferable branch.
    # Neutralise those nouns before prefixing the actual path identity.
    replacements = {
        "Han ": "Court ",
        "Roman ": "Imperial ",
        "Barbarian ": "Frontier ",
    }
    for old, new in replacements.items():
        display = display.replace(old, new)
    return f"{ADVANCE_PROFILES[profile].name}: {display}"


def advance_records() -> tuple[Advance, ...]:
    records: list[Advance] = []
    for track, age_groups in TRACKS.items():
        for conceptual_index, group in enumerate(age_groups):
            # EU5 validates `requires` within one age only. Each age therefore
            # contains complete branching trees; the mandatory sixth slot
            # divides the final conceptual arc at 376.
            if len(group) != 10:
                raise ValueError(f"{track} conceptual age {conceptual_index + 1} must have exactly ten advances")
            segments = (
                ((4, group[:5]), (5, group[5:]))
                if conceptual_index == 4
                else ((conceptual_index, group),)
            )
            for age_index, segment in segments:
                profile_a, profile_b = BRANCH_PROFILES[track][age_index]
                if len(segment) == 10:
                    depths = (0, 0, 1, 1, 1, 1, 2, 2, 3, 2)
                    profiles = (
                        "shared", "shared", profile_a, profile_a, profile_b,
                        profile_b, profile_a, profile_b, profile_a, profile_b,
                    )
                    parents = (
                        (), (), (0,), (0,), (1,), (1,), (2, 3), (4,),
                        (6,), (5,),
                    )
                elif len(segment) == 5:
                    depths = (0, 1, 1, 2, 2)
                    profiles = ("shared", profile_a, profile_b, profile_a, profile_b)
                    parents = ((), (0,), (0,), (1,), (2,))
                else:
                    raise ValueError(f"{track} {AGE_KEYS[age_index]} has unsupported segment size")
                segment_keys = tuple(f"antq_{name}" for name in segment)
                for index, name in enumerate(segment):
                    key = f"antq_{name}"
                    profile = profiles[index]
                    depth = depths[index]
                    display_name = advance_display_name(name, profile)
                    records.append(Advance(
                        key, display_name, AGE_KEYS[age_index], age_index, depth,
                        track, profile,
                        tuple(segment_keys[parent] for parent in parents[index]),
                        (TRACK_EFFECTS[track][depth],),
                        advance_description(display_name, track, profile, age_index),
                        ADVANCE_PROFILES[profile].source,
                    ))
        age_one_root = f"antq_{TRACKS[track][0][0]}"
        expansion_depths = (1, 2, 3, 3, 4)
        expansion_parents = ((age_one_root,), (0,), (1,), (1,), (2, 3))
        for profile, branch in AGE1_EXPANSION[track]:
            if len(branch) != 5:
                raise ValueError(f"{track}/{profile} Age-I expansion must have five advances")
            branch_keys = tuple(f"antq_{name}" for name in branch)
            for index, name in enumerate(branch):
                key = branch_keys[index]
                depth = expansion_depths[index]
                requirements = tuple(
                    parent if isinstance(parent, str) else branch_keys[parent]
                    for parent in expansion_parents[index]
                )
                display_name = advance_display_name(name, profile)
                records.append(Advance(
                    key, display_name, AGE_KEYS[0], 0, depth, track, profile,
                    requirements,
                    (TRACK_EFFECTS[track][depth],),
                    advance_description(display_name, track, profile, 0),
                    ADVANCE_PROFILES[profile].source,
                ))
    return tuple(records)


def ordered_top_level_keys(path: Path, prefix: str = "antq_") -> tuple[str, ...]:
    """Inventory generated subsystem definitions without matching nested blocks."""
    keys: list[str] = []
    depth = 0
    for line in path.read_text(encoding="utf-8-sig", errors="strict").splitlines():
        code = line.split("#", 1)[0]
        if depth == 0 and TOP_LEVEL.match(code):
            key = code.split("=", 1)[0].strip()
            if key.startswith(prefix):
                keys.append(key)
        depth += brace_delta(line)
        if depth < 0:
            raise ValueError(f"negative brace depth while reading {path}")
    if depth != 0 or not keys:
        raise ValueError(f"unable to inventory top-level keys in {path}")
    return tuple(keys)


BUILDING_TRACK_HINTS: dict[str, tuple[str, ...]] = {
    "statecraft": (
        "monetal", "weightmaker", "mensores", "customs_gate", "seal_cutter",
    ),
    "warfare": (
        "weapon", "armour", "arrow", "harness", "chariot", "ironmongery",
        "shield", "scabbard", "chainmaker", "nailery", "locksmith",
        "wiredrawer", "crucible_steel",
    ),
    "learning": (
        "scriptorium", "papyrus", "parchment", "stationer", "scroll",
        "reed_pen", "instrument", "apothecary", "materia_medica", "herbal",
    ),
    "society": (
        "granary", "cistern", "fountain", "bath", "bread", "brewery",
        "brewhouse", "honey", "soap", "lamp", "figurine", "mosaic",
        "macellum",
    ),
}

ROMAN_ECONOMY_UNLOCKS: dict[str, tuple[str, ...]] = {
    "antq_tax_registers": (
        "antq_reg_villa_rustica", "antq_reg_tabernae_row", "antq_reg_forum_basilica",
        "antq_reg_insulae_quarter", "antq_reg_temple_precinct", "antq_reg_collegia_hall",
    ),
    "antq_road_milestones": (
        "antq_reg_aqueduct_distribution", "antq_reg_thermae_complex",
        "antq_reg_cursus_mansio", "antq_reg_river_port", "antq_reg_colonia_forum",
    ),
    "antq_public_granaries": (
        "antq_reg_horrea_complex", "antq_reg_annona_bakery",
        "antq_reg_quarry_contractors", "antq_reg_olive_estate",
        "antq_reg_vineyard_estate", "antq_reg_textile_quarter",
        "antq_reg_ceramic_quarter", "antq_reg_bronze_workers_collegium",
        "antq_reg_lead_pipeworks", "antq_reg_unguentarium",
    ),
    "antq_supply_columns": (
        "antq_reg_castra_fabrica", "antq_reg_frontier_magazine",
    ),
}


def regional_building_keys() -> tuple[str, ...]:
    with REGIONAL_BUILDING_LEDGER.open(encoding="utf-8-sig", newline="") as handle:
        keys = tuple((row.get("key") or "").strip() for row in csv.DictReader(handle))
    if not keys or any(not key.startswith("antq_reg_") for key in keys) or len(keys) != len(set(keys)):
        raise ValueError("regional building ledger has missing, invalid, or duplicate keys")
    return keys


def building_track(key: str) -> str:
    for track, hints in BUILDING_TRACK_HINTS.items():
        if any(hint in key for hint in hints):
            return track
    return "exchange"


def content_unlocks(records: tuple[Advance, ...]) -> dict[str, tuple[tuple[str, str], ...]]:
    """Compose explicit cross-system packages for the ancient advance DAG.

    Regional workshops are ancient practices rather than literal inventions.
    Their tiers represent the administrative ability to reproduce them at
    scale.  Shared foundations keep every culture eligible, while source order
    moves from common production toward increasingly specialised workshops.
    """
    result: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for key, entries in START_UNLOCKS.items():
        result[key].extend(entries)
    for key, entries in CONTENT_UNLOCKS.items():
        result[key].extend(entries)
    with S2_ESTATE_PRIVILEGES.open(encoding="utf-8-sig", newline="") as handle:
        estate_rows = list(csv.DictReader(handle))
    by_profile: dict[str, list[str]] = defaultdict(list)
    for row in estate_rows:
        key = (row.get("key") or "").strip()
        matched = next(
            (
                profile for profile in S2_ESTATE_ADVANCE_PROFILES
                if key.startswith(f"antq_{profile}_")
            ),
            None,
        )
        if matched is None:
            raise ValueError(f"S2 estate privilege has no research profile: {key}")
        by_profile[matched].append(key)
    for profile, privilege_keys in by_profile.items():
        candidates = sorted(
            (
                record for record in records
                if record.age_index == 0
                and record.profile in S2_ESTATE_ADVANCE_PROFILES[profile]
                and record.depth >= 1
            ),
            key=lambda record: (record.depth, record.track, record.key),
        )
        if not candidates:
            raise ValueError(f"no Age-I research candidates for S2 estate profile {profile}")
        for index, privilege in enumerate(privilege_keys):
            result[candidates[index * len(candidates) // len(privilege_keys)].key].append(
                ("unlock_estate_privilege", privilege)
            )
    with S2_ALTERNATIVE_REFORMS.open(encoding="utf-8-sig", newline="") as handle:
        reform_rows = list(csv.DictReader(handle))
    reforms_by_profile: dict[str, list[str]] = defaultdict(list)
    for row in reform_rows:
        profile = (row.get("profile") or "").strip()
        reform = (row.get("reform") or "").strip()
        age_index_text = (row.get("age_index") or "0").strip()
        if profile not in S2_ESTATE_ADVANCE_PROFILES or not reform.startswith("antq_"):
            raise ValueError(f"invalid alternative reform research profile: {profile}/{reform}")
        try:
            age_index = int(age_index_text)
        except ValueError as exc:
            raise ValueError(
                f"invalid reform age index: {profile}/{reform}/{age_index_text}"
            ) from exc
        if not 0 <= age_index < len(AGE_KEYS):
            raise ValueError(
                f"out-of-range reform age index: {profile}/{reform}/{age_index}"
            )
        reforms_by_profile[f"{profile}|{age_index}"].append(reform)
    for profile_age, reform_keys in reforms_by_profile.items():
        profile, age_index_text = profile_age.split("|", 1)
        age_index = int(age_index_text)
        candidates = sorted(
            (
                record for record in records
                if record.age_index == age_index
                and record.profile in S2_ESTATE_ADVANCE_PROFILES[profile]
                and record.depth >= 2
            ),
            key=lambda record: (record.depth, record.track, record.key),
        )
        if not candidates:
            raise ValueError(
                f"no deeper age-{age_index + 1} research candidates for reform profile {profile}"
            )
        for index, reform in enumerate(reform_keys):
            result[candidates[index * len(candidates) // len(reform_keys)].key].append(
                ("unlock_government_reform", reform)
            )
    with S2_ANCIENT_LAWS.open(encoding="utf-8-sig", newline="") as handle:
        law_rows = list(csv.DictReader(handle))
    profile_laws = tuple(dict.fromkeys(
        (row.get("law") or "").strip() for row in law_rows
    ))
    if len(profile_laws) != 182 or any(not law.startswith("antq_s2_") for law in profile_laws):
        raise ValueError("S2 legal registry must expose 182 unique profile law groups")
    universal_roots = sorted(
        (
            record for record in records
            if record.age_index == 0 and record.depth == 0 and record.profile == "shared"
        ),
        key=lambda record: (record.track, record.key),
    )
    if len(universal_roots) != 10:
        raise ValueError("S2 legal unlocks require the ten universally held Age-I roots")
    for index, law in enumerate(profile_laws):
        result[universal_roots[index % len(universal_roots)].key].append(
            ("unlock_law", law)
        )
    managed_roman_buildings: set[str] = set()
    for advance, buildings in ROMAN_ECONOMY_UNLOCKS.items():
        result[advance].extend(("unlock_building", building) for building in buildings)
        managed_roman_buildings.update(buildings)

    buildings = tuple(
        building for building in regional_building_keys()
        if building not in managed_roman_buildings
    )
    grouped: dict[str, list[str]] = {track: [] for track in TRACKS}
    for building in buildings:
        grouped[building_track(building)].append(building)
    for track, keys in grouped.items():
        candidates = sorted(
            (
                record for record in records
                if record.track == track and record.profile == "shared"
            ),
            key=lambda record: (record.age_index, record.depth, record.key),
        )
        if not candidates:
            raise ValueError(f"no shared {track} advances available for building packages")
        for index, building in enumerate(keys):
            slot = min(len(candidates) - 1, index * len(candidates) // len(keys))
            result[candidates[slot].key].append(("unlock_building", building))
    return {key: tuple(entries) for key, entries in result.items()}


def direct_advance_icons(records: tuple[Advance, ...]) -> dict[str, str]:
    """Return direct M11 icon identifiers for reviewed completed rows only."""
    if not DIRECT_ADVANCE_ART.is_file():
        return {}
    with DIRECT_ADVANCE_ART.open(encoding="utf-8-sig", newline="") as handle:
        entries = list(csv.DictReader(handle))
    valid = {record.key for record in records}
    direct: dict[str, str] = {}
    for row in entries:
        key = (row.get("key") or "").strip()
        if (row.get("status") or "").strip() != "complete":
            continue
        if key not in valid:
            raise ValueError(f"direct advance-art ledger has unknown advance {key}")
        if key in direct:
            raise ValueError(f"direct advance-art ledger repeats completed advance {key}")
        direct[key] = "antq_advance_" + key.removeprefix("antq_")
    return direct


def technology_level(row: dict[str, str]) -> int:
    """Tune the plan's three starting tiers from the checked M3 polity ledger."""
    if row["tag"] in CORE_TAGS:
        # Level 4 owns every Age-I node because the generated tree caps
        # `starting_technology_level` at four.  That left Rome, Han, and Arsacid
        # Iran with nothing researchable until the next dated age.  Level 3 keeps
        # their advanced baseline while leaving the final Age-I branches open.
        return 3
    if row["kind"] in {"country", "subject"} and row["tier"] in {"1", "2"}:
        return 3
    if row["kind"] == "sop":
        return 1
    return 2


def technology_tier_summary() -> tuple[int, int, int, int]:
    with ROSTER.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    counts = {level: 0 for level in range(1, 5)}
    for row in rows:
        counts[technology_level(row)] += 1
    if counts[4] != 0 or not all(counts[level] for level in (1, 2, 3)):
        raise ValueError("M8 starting-technology policy no longer partitions the M3 roster")
    return tuple(counts[level] for level in range(1, 5))


def start_research_rows(records: tuple[Advance, ...]) -> list[dict[str, str]]:
    """Prove day-one Age-I choices for every playable M3 roster entry.

    Eligibility follows the generated contracts exactly: a country owns every
    Age-I node whose starting level is at or below its roster technology tier,
    and may choose an unowned node only when all parents are owned and its
    primary culture group satisfies the node potential.  Institution-led
    cross-adoption is deliberately excluded from this minimum proof.
    """
    with CULTURES_LEDGER.open(encoding="utf-8-sig", newline="") as handle:
        culture_groups = {
            row["key"].strip(): row["group"].strip()
            for row in csv.DictReader(handle)
        }
    with TAG_PROFILES.open(encoding="utf-8-sig", newline="") as handle:
        tag_cultures = {
            row["tag"].strip(): row["culture"].strip()
            for row in csv.DictReader(handle)
        }
    with REGIONAL_PROFILES.open(encoding="utf-8-sig", newline="") as handle:
        regional_cultures = {
            row["region"].strip(): row["culture"].strip()
            for row in csv.DictReader(handle)
        }
    with ROSTER.open(encoding="utf-8-sig", newline="") as handle:
        roster = list(csv.DictReader(handle))

    age_one = tuple(record for record in records if record.age_index == 0)
    rows: list[dict[str, str]] = []
    for polity in roster:
        tag = polity["tag"].strip()
        culture = tag_cultures.get(tag, regional_cultures.get(polity["region"].strip(), ""))
        group = culture_groups.get(culture, "")
        level = technology_level(polity)
        owned = {
            record.key
            for record in age_one
            if min(4, record.depth + 1) <= level
        }
        eligible = [
            record.key
            for record in age_one
            if record.key not in owned
            and all(required in owned for required in record.requires)
            and (
                record.profile == "shared"
                or group in ADVANCE_PROFILES[record.profile].culture_groups
            )
        ]
        rows.append({
            "tag": tag,
            "name": polity["name"].strip(),
            "tier": polity["tier"].strip(),
            "kind": polity["kind"].strip(),
            "culture": culture,
            "culture_group": group,
            "technology_level": str(level),
            "owned_age_i": str(len(owned)),
            "eligible_count": str(len(eligible)),
            "eligible_keys": ";".join(eligible),
            "status": "pass" if len(eligible) >= 2 else "fail",
        })
    return rows


def start_research_ledger(records: tuple[Advance, ...]) -> str:
    fields = (
        "tag", "name", "tier", "kind", "culture", "culture_group",
        "technology_level", "owned_age_i", "eligible_count",
        "eligible_keys", "status",
    )
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(start_research_rows(records))
    return buffer.getvalue()


def institution_manager() -> str:
    lines = ["institution_manager = {", "\tinstitutions = {"]
    for institution in INSTITUTION_DATA:
        if institution.start_active:
            lines.append(f"\t\t{institution.key} = {{ active = yes birth_place = {institution.location} }}")
    lines.extend(("\t}", "}", ""))
    return "\n".join(lines)


def validate(records: tuple[Advance, ...]) -> None:
    failures: list[str] = []
    unlocks = content_unlocks(records)
    if len(records) != 360:
        failures.append(f"expected 360 advances after the Age-I expansion, got {len(records)}")
    keys = [record.key for record in records]
    if len(keys) != len(set(keys)):
        failures.append("advance keys are not unique")
    expected_counts = (160, 50, 50, 50, 25, 25)
    for age_index, age in enumerate(AGE_KEYS):
        age_records = [record for record in records if record.age == age]
        expected = expected_counts[age_index]
        if len(age_records) != expected:
            failures.append(f"{age} has {len(age_records)}, not {expected} advances")
        depth_limit = 5 if age_index == 0 else (4 if age_index < 4 else 3)
        if any(record.depth not in range(depth_limit) for record in age_records):
            failures.append(f"{age} has a depth outside 0..{depth_limit - 1}")
        regional_profiles = {record.profile for record in age_records} - {"shared"}
        if len(regional_profiles) < 8:
            failures.append(f"{age} exposes only {len(regional_profiles)} regional profiles")
    roots = [record for record in records if not record.requires]
    if len(roots) != 50:
        failures.append("the 30 branching trees must have exactly 50 shared roots")
    key_set = set(keys)
    unknown_unlock_keys = sorted(set(unlocks) - key_set)
    if unknown_unlock_keys:
        failures.append(
            "M8 unlock mapping has unknown advances: " + ", ".join(unknown_unlock_keys)
        )
    unknown_capability_keys = sorted(set(START_CAPABILITIES) - key_set)
    if unknown_capability_keys:
        failures.append(
            "M8 start-capability mapping has unknown advances: "
            + ", ".join(unknown_capability_keys)
        )
    if START_CAPABILITIES.get("antq_provincial_census") != (
        ("enable_taxation", "yes"),
        ("has_stability_investment", "yes"),
    ):
        failures.append("the universally held Provincial Census lost its economy capabilities")
    unlock_fields = {
        field for entries in unlocks.values() for field, _target in entries
    }
    supported_unlock_fields = {
        "unlock_building", "unlock_unit", "unlock_law", "unlock_policy",
        "unlock_estate_privilege", "unlock_government_reform",
        "unlock_casus_belli", "unlock_subject_type",
    }
    if unlock_fields - supported_unlock_fields:
        failures.append(
            "M8 unlock mapping uses unsupported fields: "
            + ", ".join(sorted(unlock_fields - supported_unlock_fields))
        )
    target_sources = {
        "unlock_building": (REGIONAL_BUILDINGS, "antq_reg_"),
        "unlock_unit": (ANCIENT_UNITS, "antq_"),
        "unlock_estate_privilege": (ANCIENT_PRIVILEGES, "antq_"),
        "unlock_government_reform": (ANCIENT_REFORMS, "antq_"),
        "unlock_casus_belli": (ANCIENT_CASUS_BELLI, "antq_"),
        "unlock_subject_type": (ANCIENT_SUBJECT_TYPES, "antq_"),
    }
    for field, (path, prefix) in target_sources.items():
        expected_targets = (
            set(regional_building_keys())
            if field == "unlock_building"
            else set(ordered_top_level_keys(path, prefix))
        )
        actual_targets = [
            target
            for entries in unlocks.values()
            for unlock_field, target in entries
            if unlock_field == field
        ]
        actual_set = set(actual_targets)
        if actual_set != expected_targets:
            failures.append(
                f"{field} coverage mismatch: "
                f"missing={sorted(expected_targets - actual_set)}, "
                f"extra={sorted(actual_set - expected_targets)}"
            )
        if len(actual_targets) != len(actual_set):
            failures.append(f"{field} repeats one or more unlock targets")
    with S2_ANCIENT_LAWS.open(encoding="utf-8-sig", newline="") as handle:
        expected_profile_laws = {
            (row.get("law") or "").strip() for row in csv.DictReader(handle)
        }
    actual_profile_laws = [
        target
        for entries in unlocks.values()
        for unlock_field, target in entries
        if unlock_field == "unlock_law" and target.startswith("antq_s2_")
    ]
    if set(actual_profile_laws) != expected_profile_laws:
        failures.append(
            "S2 profile-law unlock coverage mismatch: "
            f"missing={sorted(expected_profile_laws - set(actual_profile_laws))}, "
            f"extra={sorted(set(actual_profile_laws) - expected_profile_laws)}"
        )
    if len(actual_profile_laws) != len(set(actual_profile_laws)):
        failures.append("S2 profile-law unlocks repeat one or more targets")
    by_key = {record.key: record for record in records}
    required_by = {required for record in records for required in record.requires}
    leaves = [record.key for record in records if record.key not in required_by]
    if len(leaves) != 102:
        failures.append("the expanded branching trees must have exactly 102 terminal choices")
    child_counts = {key: 0 for key in keys}
    for record in records:
        for required in record.requires:
            child_counts[required] += 1
    if sum(count >= 2 for count in child_counts.values()) != 72:
        failures.append("the expanded advance DAG must contain exactly 72 branch points")
    if sum(len(record.requires) >= 2 for record in records) != 42:
        failures.append("the expanded advance DAG must contain exactly 42 convergence nodes")
    for profile in set(ADVANCE_PROFILES) - {"shared"}:
        profile_leaves = [key for key in leaves if by_key[key].profile == profile]
        minimum_leaves = 2 if profile in {"baltic", "slavic_eastern", "uralic"} else 3
        if len(profile_leaves) < minimum_leaves:
            failures.append(f"advance profile {profile} offers only {len(profile_leaves)} terminal choices")
    profile_counts = {
        profile: sum(record.profile == profile for record in records)
        for profile in ADVANCE_PROFILES
    }
    for profile, count in profile_counts.items():
        minimum = 50 if profile == "shared" else 10
        if count < minimum:
            failures.append(f"advance profile {profile} has only {count} nodes")
    for record in records:
        if record.profile not in ADVANCE_PROFILES:
            failures.append(f"{record.key} uses an unknown advance profile")
        if not record.effects:
            failures.append(f"{record.key} has no consequential effect")
        if not record.description or "knowledge:" in record.description.lower():
            failures.append(f"{record.key} has a placeholder description")
        if not record.source:
            failures.append(f"{record.key} has no source")
        for required in record.requires:
            if required not in key_set:
                failures.append(f"{record.key} requires an unknown advance")
                continue
            parent = by_key[required]
            if parent.age != record.age:
                failures.append(f"{record.key} has a cross-age requirement")
            if parent.depth >= record.depth:
                failures.append(f"{record.key} does not descend from {required}")
            if parent.profile not in {"shared", record.profile}:
                failures.append(f"{record.key} converges across incompatible profiles")
        if any(token in record.key for token in FORBIDDEN):
            failures.append(f"anachronistic token in {record.key}")
    names = " ".join(keys)
    if "stirrup" in names:
        failures.append("the contested stirrup is outside M8's research tree")
    institution_keys = [item.key for item in INSTITUTION_DATA]
    if len(institution_keys) != len(set(institution_keys)):
        failures.append("institution keys are not unique")
    for item in INSTITUTION_DATA:
        if item.age not in AGE_KEYS:
            failures.append(f"{item.key} uses an invalid age")
        try:
            AntqDate.parse(item.earliest)
        except ValueError as exc:
            failures.append(f"{item.key} has invalid date: {exc}")
        if item.spread_band not in {"early", "mid", "late"}:
            failures.append(f"{item.key} uses invalid spread band")
        if item.profile not in INSTITUTION_PROFILES:
            failures.append(f"{item.key} uses unknown eligibility profile")
        if not item.source:
            failures.append(f"{item.key} has no historical source")
    if sum(item.start_active for item in INSTITUTION_DATA) != 4:
        failures.append("M8 requires four active AD 1 institution origins")
    han = next(item for item in INSTITUTION_DATA if item.key == "antq_han_bureaucratic_statecraft")
    han_profile = "\n".join(INSTITUTION_PROFILES[han.profile].script)
    if han.trade_spread or any(
        token in han_profile
        for token in ("europe", "italy_region", "france_region", "roman_imperial")
    ):
        failures.append("Han statecraft must not have ordinary trade or European eligibility")
    if set(INSTITUTION_BIRTH_EFFECTS) != set(institution_keys):
        failures.append("institution birth modifiers do not exactly cover the M8 institutions")
    technology_tier_summary()
    reachability = start_research_rows(records)
    for row in reachability:
        if not row["culture"]:
            failures.append(f"{row['tag']} has no M4 primary-culture profile")
        elif not row["culture_group"]:
            failures.append(f"{row['tag']} culture {row['culture']} has no M4 culture group")
        if int(row["eligible_count"]) < 2:
            failures.append(
                f"{row['tag']} has only {row['eligible_count']} day-one research choices"
            )
    rome = next((row for row in reachability if row["tag"] == "ROM"), None)
    if rome is None or int(rome["eligible_count"]) < 4:
        failures.append("Rome must have at least four day-one Age-I research choices")
    if failures:
        raise ValueError("\n".join(failures))


def advance_potential(record: Advance) -> list[str]:
    profile = ADVANCE_PROFILES[record.profile]
    if record.profile == "shared":
        return []
    lines = ["\tpotential = {", "\t\tOR = {"]
    for group in profile.culture_groups:
        lines.append(
            f"\t\t\tculture = {{ has_culture_group = culture_group:{group} }}"
        )
    for institution in profile.adoption_institutions:
        lines.append(
            f"\t\t\thas_embraced_institution = institution:{institution}"
        )
    lines.extend(("\t\t}", "\t}"))
    return lines


def advance_script(records: tuple[Advance, ...]) -> str:
    lines = [
        "# Generated by tools/m8_knowledge.py --write; complete ANTIQVITAS ancient knowledge trees.",
        "# Five branching trees per age; cultural paths support explicit institution-led adoption.",
    ]
    direct = direct_advance_icons(records)
    unlocks = content_unlocks(records)
    for record in records:
        icon = direct.get(record.key, ICONS[record.age_index])
        lines.extend((f"{record.key} = {{", f"\tage = {record.age}", f"\ticon = {icon}", f"\tdepth = {record.depth}", f"\tresearch_cost = {2 + record.age_index * 2 + record.depth * 0.5:.1f}"))
        lines.extend(advance_potential(record))
        for field, value in record.effects:
            lines.append(f"\t{field} = {value}")
        for field, value in START_CAPABILITIES.get(record.key, ()):
            lines.append(f"\t{field} = {value}")
        for field, target in unlocks.get(record.key, ()):
            lines.append(f"\t{field} = {target}")
        if record.age_index == 0:
            lines.append(f"\tstarting_technology_level = {min(4, record.depth + 1)}")
        for required in record.requires:
            lines.append(f"\trequires = {required}")
        lines.extend((f"\tai_weight = {{ add = {100 - record.depth * 10} }}", "}", ""))
    return "\n".join(lines)


def brace_delta(line: str) -> int:
    """Count structural braces in a plain Paradox-script line.

    The installed advance files do not use quoted script blocks in definition
    headers. Ignoring comments avoids a prose brace from corrupting the small
    source-preserving transform below.
    """
    code = line.split("#", 1)[0]
    return code.count("{") - code.count("}")


def inject_inline_false(line: str) -> str:
    """Add `always = no` to a one-line trigger without losing its references."""
    code, marker, comment = line.partition("#")
    closing = code.rfind("}")
    if closing < 0:
        raise ValueError(f"expected inline trigger block: {line!r}")
    # The closing brace must remain before the explanatory comment; otherwise
    # the comment consumes it and corrupts the containing advance definition.
    suffix = (" " + marker + comment) if marker else ""
    return code[:closing] + " always = no" + code[closing:] + " # M8 disables vanilla" + suffix


def optionalize_market_links(line: str) -> str:
    """Keep compatibility readers while making absent AD 1 market links safe."""
    code, marker, comment = line.partition("#")
    code = re.sub(r"(?<!\?)\bmarket\s*=\s*\{", "market ?= {", code)
    suffix = marker + comment if marker else ""
    return code + suffix


def disabled_content(path: Path, field: re.Pattern[str], field_name: str, kind: str, strip_unlocks: bool) -> str:
    """Add a false condition without deleting references inside the source block."""
    raw = path.read_text(encoding="utf-8-sig", errors="strict")
    rendered = [
        f"# Generated by tools/m8_knowledge.py --write; M8 disables vanilla {kind} gameplay.",
        "# Keys and their dependent trigger references remain valid for loaded vanilla script.",
    ]
    depth = 0
    root_has_gate = False
    root_open = False
    legacy_allow_depth: int | None = None
    for line in raw.splitlines():
        code = line.split("#", 1)[0]
        delta = brace_delta(line)
        if legacy_allow_depth is not None:
            rendered.append(optionalize_market_links(line))
            depth += delta
            if depth == legacy_allow_depth:
                legacy_allow_depth = None
            continue
        if depth == 0 and TOP_LEVEL.match(code):
            root_open = delta > 0
            root_has_gate = False
            rendered.append(line)
            depth += delta
            continue
        if root_open and depth == 1 and kind == "advancement" and ALLOW.match(code):
            # EU5 evaluates `allow` even when `potential` is false. Preserve
            # harmless variable readers needed by the engine's load-time
            # contract audit, but false-gate the block and optionalize market
            # links so countries without an established AD 1 market are safe.
            if delta == 0:
                rendered.append(optionalize_market_links(inject_inline_false(line)))
            else:
                rendered.append(optionalize_market_links(line))
                indent = code[: len(code) - len(code.lstrip())]
                rendered.append(f"{indent}\talways = no # M8 disables vanilla advancement")
                legacy_allow_depth = depth
                depth += delta
            continue
        if root_open and depth == 1 and field.match(code):
            if delta == 0:
                rendered.append(inject_inline_false(line))
            else:
                rendered.append(line)
                indent = code[: len(code) - len(code.lstrip())]
                rendered.append(f"{indent}\talways = no # M8 disables vanilla {kind}")
            root_has_gate = True
            depth += delta
            continue
        if root_open and depth == 1 and delta < 0 and not root_has_gate:
            rendered.append(f"\t{field_name} = {{ always = no }} # M8 disables vanilla {kind}")
            root_has_gate = True
        if not (strip_unlocks and UNLOCK.match(code)):
            rendered.append(line)
        depth += delta
        if root_open and depth == 0:
            root_open = False
    if depth != 0:
        raise ValueError(f"unable to preserve brace structure in {path.name}")
    return "\n".join(rendered) + "\n"


def replace_top_level_definition(text: str, key: str, replacement: str) -> str:
    """Replace one preserved registry definition without regexing nested script."""
    lines = text.splitlines()
    rendered: list[str] = []
    depth = 0
    replacing = False
    found = False
    for line in lines:
        code = line.split("#", 1)[0]
        delta = brace_delta(line)
        if not replacing and depth == 0 and TOP_LEVEL.match(code):
            current = code.split("=", 1)[0].strip()
            if current == key:
                rendered.extend(replacement.rstrip().splitlines())
                replacing = True
                found = True
                depth += delta
                if depth == 0:
                    replacing = False
                continue
        if replacing:
            depth += delta
            if depth == 0:
                replacing = False
            continue
        rendered.append(line)
        depth += delta
    if depth != 0 or replacing:
        raise ValueError(f"unable to replace top-level definition {key}")
    if not found:
        raise ValueError(f"installed registry lost required compatibility key {key}")
    return "\n".join(rendered) + "\n"


def disabled_advance_content(path: Path) -> str:
    """Keep every vanilla advance key valid but make it permanently unavailable."""
    rendered = neutralize_references(
        disabled_content(path, POTENTIAL, "potential", "advancement", True),
        remap_effects=True,
    )
    if path.name == "0_age_of_traditions.txt":
        # Preserve the installed modifier-bearing compatibility key alongside
        # the custom census root. The opening economy has no functioning market
        # yet, so day-one tax values cannot independently prove which key the
        # 1.3.11 initialization path consumes. Keeping both anciently presented
        # shapes is safer than silently removing a hardcoded economy contract.
        rendered = replace_top_level_definition(
            rendered,
            "taxation_advance",
            """taxation_advance = {
\tage = age_1_traditions
\ticon = antq_advance_provincial_census
\tdepth = 0
\tresearch_cost = 2.0
\tenable_taxation = yes
\thas_stability_investment = yes
\tstarting_technology_level = 1
\tpotential = { always = yes }
\tai_weight = { add = 0 }
} # ANTIQVITAS engine adapter: ancient tribute and census capability""",
        )
    return rendered


def pre_market_revenue_script() -> str:
    """Bridge the engine's unsafe no-market startup interval without seeding markets."""
    return """# Generated by tools/m8_knowledge.py --write.
# EU5 1.3.11 crashes when AD 1 markets are created instantly or pre-seeded.
# Automatic market construction is retained.  The engine's normal create-market
# price scales to five months of economic base and bankrupts large AD 1 states
# before their first ledger exists, so only that bootstrap construction is free.
# Both adapters end as soon as a country's capital gains market access.
antq_pre_market_in_kind_revenue = {
\tpotential_trigger = {
\t\tcapital ?= {
\t\t\tmarket_access <= 0
\t\t}
\t}
\tscales_with = {
\t\tvalue = country_economical_base
\t\tdivide = 4
\t\tmin = 5
\t\tmax = 200
\t}
\tmonthly_gold_income = 1
\tcreate_market_cost_modifier = -1
}
"""


def disabled_institution_content(path: Path) -> str:
    """Keep vanilla institution IDs for event links while preventing spawns."""
    return disabled_content(path, CAN_SPAWN, "can_spawn", "institution", False)


def installed_institution_keys(path: Path) -> tuple[str, ...]:
    """Read only top-level institution IDs from one installed age file."""
    result: list[str] = []
    depth = 0
    for line in path.read_text(encoding="utf-8-sig", errors="strict").splitlines():
        code = line.split("#", 1)[0]
        if depth == 0 and TOP_LEVEL.match(code):
            result.append(code.split("=", 1)[0].strip())
        depth += brace_delta(line)
    if depth != 0 or not result:
        raise ValueError(f"unable to inventory installed institutions in {path.name}")
    return tuple(result)


def legacy_institution_stubs(path: Path) -> str:
    """Remove installed IDs entirely; nullable-age records crash the Advances UI."""
    keys = installed_institution_keys(path)
    return (
        "# Generated by tools/m8_knowledge.py --write.\n"
        f"# Removed {len(keys)} post-antique institutions from {path.name}; "
        "all installed references are neutralized by generated exact-name overlays.\n"
    )


def empty_overrides(relative: str, destination: Path, label: str) -> dict[Path, str]:
    source = installed_dir(relative)
    if not source.is_dir():
        raise ValueError(f"installed {label} directory missing: {source}")
    outputs: dict[Path, str] = {}
    for path in sorted(source.glob("*.txt")):
        if path.name == "readme.txt":
            continue
        if label == "advance":
            outputs[destination / path.name] = disabled_advance_content(path)
        else:
            outputs[destination / path.name] = legacy_institution_stubs(path)
    if not outputs:
        raise ValueError(f"installed {label} manifest is empty")
    return outputs


def institution_eligibility_script() -> str:
    lines = [
        "# Generated by tools/m8_knowledge.py --write.",
        "# Root scope: receiving location. These gates constrain every spread channel.",
    ]
    for profile in INSTITUTION_PROFILES.values():
        lines.append(f"antq_institution_eligible_{profile.key} = {{")
        lines.extend(f"\t{line}" for line in profile.script)
        lines.extend(("}", ""))
    return "\n".join(lines)


def gated_value(field: str, base: str, profile: str) -> list[str]:
    return [
        f"\t{field} = {{",
        "\t\tvalue = 0",
        "\t\tif = {",
        f"\t\t\tlimit = {{ antq_institution_eligible_{profile} = yes }}",
        f"\t\t\tadd = {base}",
        "\t\t}",
        "\t}",
    ]


def institution_script() -> str:
    lines = [
        "# Generated by tools/m8_knowledge.py --write; M8 ancient institutions.",
        "# All dates are AntqDate-validated; every propagation channel is profile-gated.",
    ]
    for item in INSTITUTION_DATA:
        lines.extend((
            f"{item.key} = {{",
            f"\tage = {item.age}",
            f"\tlocation = {item.location}",
            "\tcan_spawn = {",
            f"\t\tcurrent_date >= {AntqDate.parse(item.earliest).engine()}",
            f"\t\tthis = location:{item.location}",
            f"\t\tantq_institution_eligible_{item.profile} = yes",
            "\t}",
        ))
        lines.extend(gated_value("promote_chance", "100", item.profile))
        lines.extend(gated_value(
            "spread_from_friendly_coast_border_location",
            f"institution_base_spread_from_friendly_neighbor_with_{item.spread_band}",
            item.profile,
        ))
        lines.extend(gated_value(
            "spread_from_any_coast_border_location",
            f"institution_base_spread_from_neighbor_with_{item.spread_band}",
            item.profile,
        ))
        for field in ("spread_from_any_import", "spread_from_any_export"):
            base = (
                f"institution_trade_spread_value_{item.spread_band}"
                if item.trade_spread else "0"
            )
            lines.extend(gated_value(field, base, item.profile))
        lines.extend(gated_value(
            "spread_embraced_to_capital",
            f"institution_total_embraced_to_capital_{item.spread_band}",
            item.profile,
        ))
        lines.extend(gated_value(
            "spread_scale_on_control_if_owner_embraced", "2", item.profile,
        ))
        lines.extend(gated_value(
            "spread_to_market_member",
            f"institution_spread_to_market_member_{item.spread_band}",
            item.profile,
        ))
        lines.extend(gated_value(
            "spread_to_market_center", "institution_spread_to_market_center", item.profile,
        ))
        lines.extend(("}", ""))
    return "\n".join(lines)


def advance_ledger(records: tuple[Advance, ...]) -> str:
    fields = (
        "key", "name", "age", "track", "branch", "depth", "requires",
        "eligibility", "description", "effects", "unlocks", "ai_weight",
        "icon", "source",
    )
    icons = direct_advance_icons(records)
    unlock_map = content_unlocks(records)
    rows = [",".join(fields)]
    for record in records:
        profile = ADVANCE_PROFILES[record.profile]
        unlocks = unlock_map.get(record.key, ())
        values = (
            record.key,
            record.name,
            record.age,
            record.track,
            profile.name,
            str(record.depth),
            ";".join(record.requires),
            profile.summary,
            record.description,
            ";".join(
                f"{field}={value}"
                for field, value in (
                    *record.effects,
                    *START_CAPABILITIES.get(record.key, ()),
                )
            ),
            ";".join(f"{field}={target}" for field, target in unlocks),
            str(100 - record.depth * 10),
            icons.get(record.key, ICONS[record.age_index]),
            record.source,
        )
        rows.append(",".join(f'"{value.replace(chr(34), chr(34) * 2)}"' for value in values))
    return "\n".join(rows) + "\n"


def institution_ledger() -> str:
    fields = (
        "key", "name", "age", "earliest", "birthplace", "start_active",
        "eligibility_profile", "eligibility_summary", "ordinary_trade_spread", "source",
    )
    rows = [",".join(fields)]
    for item in INSTITUTION_DATA:
        profile = INSTITUTION_PROFILES[item.profile]
        values = (
            item.key, item.name, item.age, AntqDate.parse(item.earliest).engine(),
            item.location, "yes" if item.start_active else "no", item.profile,
            profile.summary, "yes" if item.trade_spread else "no", item.source,
        )
        rows.append(",".join(f'"{value.replace(chr(34), chr(34) * 2)}"' for value in values))
    return "\n".join(rows) + "\n"


def installed_institution_ledger() -> str:
    source = installed_dir("in_game/common/institution")
    symbol_keys = set(json.loads(VANILLA_INSTITUTION_SYMBOLS.read_text(encoding="utf-8-sig")))
    rows: list[tuple[str, str, str]] = []
    for path in sorted(source.glob("age_*.txt")):
        for key in installed_institution_keys(path):
            rows.append((key, path.name, "removed_from_database"))
    installed_keys = {key for key, _path, _status in rows}
    if installed_keys != symbol_keys:
        raise ValueError(
            "installed institution inventory differs from harvested symbols: "
            f"missing={sorted(symbol_keys - installed_keys)}, "
            f"extra={sorted(installed_keys - symbol_keys)}"
        )
    lines = ["key,installed_file,mod_status"]
    lines.extend(",".join(row) for row in rows)
    return "\n".join(lines) + "\n"


def institution_birth_modifiers() -> str:
    lines = [
        "# Generated by tools/m8_knowledge.py --write; M8 institution-origin modifiers.",
        "# The installed institution manager resolves institution_birth at each birthplace.",
    ]
    for item in INSTITUTION_DATA:
        modifier, value = INSTITUTION_BIRTH_EFFECTS[item.key]
        lines.extend((
            f"{item.key}_birth = {{",
            "\tgame_data = {",
            "\t\tcategory = location",
            "\t}",
            f"\t{modifier} = {value}",
            "}",
            "",
        ))
    return "\n".join(lines)


def removed_institution_birth_modifiers() -> str:
    return (
        "# Generated by tools/m8_knowledge.py --write.\n"
        "# Exact-name override: birth modifiers for the 18 removed post-antique institutions.\n"
    )


def localization(records: tuple[Advance, ...], language: str) -> str:
    lines = [f"l_{language}:"]
    lines.extend(
        (
            ' taxation_advance: "Tribute and Census Administration"',
            ' taxation_advance_desc: "Registers, assessed communities, and in-kind levies sustain the state before coin and market exchange reach every province."',
            ' AUTO_MODIFIER_NAME_antq_pre_market_in_kind_revenue: "In-Kind Provincial Revenue"',
            ' AUTO_MODIFIER_DESC_antq_pre_market_in_kind_revenue: "Produce, tribute, and requisitioned supplies support the state while its capital market is being organized."',
        )
    )
    for record in records:
        lines.append(f' {record.key}: "{record.name}"')
        lines.append(f' {record.key}_desc: "{record.description}"')
    for item in INSTITUTION_DATA:
        lines.append(f' {item.key}: "{item.name}"')
        lines.append(f' {item.key}_desc: "{item.description}"')
        lines.append(
            f' STATIC_MODIFIER_NAME_{item.key}_birth: '
            f'"Birthplace of ${item.key}$"'
        )
        lines.append(
            f' STATIC_MODIFIER_DESC_{item.key}_birth: '
            f'"Historic origin of the {item.name} institution."'
        )
    return "\n".join(lines) + "\n"


def outputs(records: tuple[Advance, ...]) -> dict[Path, str]:
    rendered = {
        **empty_overrides("in_game/common/advances", ADVANCES, "advance"),
        ADVANCES / "00_antiquitas_m8_tree.txt": advance_script(records),
        **empty_overrides("in_game/common/institution", INSTITUTIONS, "institution"),
        INSTITUTIONS / "00_antiquitas_m8_institutions.txt": institution_script(),
        SCRIPTED_TRIGGERS / "00_antiquitas_m8_institution_spread.txt": institution_eligibility_script(),
        AUTO_MODIFIERS / "00_antiquitas_pre_market_revenue.txt": pre_market_revenue_script(),
        STATIC_MODIFIERS / "institutions.txt": removed_institution_birth_modifiers(),
        STATIC_MODIFIERS / "antq_m8_institution_birth.txt": institution_birth_modifiers(),
        ADVANCE_LEDGER: advance_ledger(records),
        INSTITUTION_LEDGER: institution_ledger(),
        INSTALLED_INSTITUTION_LEDGER: installed_institution_ledger(),
        REACHABILITY_LEDGER: start_research_ledger(records),
    }
    for language in ("english", *M2_MIRROR_LANGUAGES):
        rendered[LOC_ROOT / language / f"antq_m8_knowledge_l_{language}.yml"] = localization(records, language)
    return rendered


def expected_inventory(relative: str, destination: Path, custom: str) -> set[Path]:
    source = installed_dir(relative)
    installed = {
        destination / path.name
        for path in source.glob("*.txt")
        if path.name != "readme.txt"
    }
    if not installed:
        raise ValueError(f"installed inventory is empty: {relative}")
    return { *installed, destination / custom }


def unsafe_disabled_allows(text: str) -> list[str]:
    """Return reasons any retained top-level legacy allow is not inert/safe."""
    failures: list[str] = []
    lines = text.splitlines()
    depth = 0
    root_open = False
    index = 0
    while index < len(lines):
        line = lines[index]
        code = line.split("#", 1)[0]
        delta = brace_delta(line)
        if depth == 0 and TOP_LEVEL.match(code):
            root_open = delta > 0
            depth += delta
            index += 1
            continue
        if root_open and depth == 1 and ALLOW.match(code):
            block = [line]
            target_depth = depth
            depth += delta
            index += 1
            while delta > 0 and index < len(lines) and depth != target_depth:
                child = lines[index]
                block.append(child)
                depth += brace_delta(child)
                index += 1
            rendered = "\n".join(block)
            if "always = no" not in rendered:
                failures.append("top-level allow lacks permanent false gate")
            if re.search(r"(?<!\?)\bmarket\s*=\s*\{", rendered):
                failures.append("top-level allow retains a mandatory market link")
            continue
        depth += delta
        index += 1
        if root_open and depth == 0:
            root_open = False
    return failures


def write(records: tuple[Advance, ...]) -> None:
    for path, content in outputs(records).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8-sig", newline="\n")
        print(f"m8_knowledge: wrote {path.relative_to(ROOT)}")


def check(records: tuple[Advance, ...]) -> bool:
    failures: list[str] = []
    expected = outputs(records)
    for path, content in expected.items():
        if not path.is_file():
            failures.append(f"missing {path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8-sig") != content:
            failures.append(f"stale {path.relative_to(ROOT)}")
    advance_inventory = expected_inventory("in_game/common/advances", ADVANCES, "00_antiquitas_m8_tree.txt")
    permitted_advances = advance_inventory | {ADVANCES / "antq_age_scaffolds.txt"}
    actual_advances = set(ADVANCES.glob("*.txt"))
    for path in sorted(actual_advances - permitted_advances):
        failures.append(f"unexpected advance file {path.relative_to(ROOT)}")
    institution_inventory = expected_inventory("in_game/common/institution", INSTITUTIONS, "00_antiquitas_m8_institutions.txt")
    actual_institutions = set(INSTITUTIONS.glob("*.txt")) if INSTITUTIONS.is_dir() else set()
    for path in sorted(actual_institutions - institution_inventory):
        failures.append(f"unexpected institution file {path.relative_to(ROOT)}")
    for path in advance_inventory:
        text = path.read_text(encoding="utf-8-sig") if path.is_file() else ""
        if UNLOCK.search(text):
            failures.append(f"unit or levy unlock survived in {path.relative_to(ROOT)}")
        for reason in unsafe_disabled_allows(text):
            failures.append(f"{reason} in {path.relative_to(ROOT)}")
    for path in institution_inventory:
        text = path.read_text(encoding="utf-8-sig") if path.is_file() else ""
        if "00_antiquitas_m8" not in path.name:
            if "post-antique institutions" not in text:
                failures.append(f"vanilla institution file is not an explicit empty override in {path.relative_to(ROOT)}")
            if any(TOP_LEVEL.match(line) for line in text.splitlines()):
                failures.append(f"legacy institution definition survives in {path.relative_to(ROOT)}")
            if legacy_references(text):
                failures.append(f"legacy institution reference survives in {path.relative_to(ROOT)}")
    custom_institutions = INSTITUTIONS / "00_antiquitas_m8_institutions.txt"
    if custom_institutions.is_file():
        text = custom_institutions.read_text(encoding="utf-8-sig")
        for item in INSTITUTION_DATA:
            marker = f"antq_institution_eligible_{item.profile}"
            if text.count(marker) != 10:
                failures.append(f"{item.key} does not gate all ten spawn/spread channels")
    custom_tree = ADVANCES / "00_antiquitas_m8_tree.txt"
    if custom_tree.is_file() and any(token in custom_tree.read_text(encoding="utf-8-sig").lower() for token in FORBIDDEN):
        failures.append("anachronistic token survived in the M8 tree")
    if failures:
        print("m8_knowledge: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return False
    tiers = technology_tier_summary()
    unlock_map = content_unlocks(records)
    unlock_count = sum(len(entries) for entries in unlock_map.values())
    print(
        "m8_knowledge: PASS "
        f"(360 advances; 9 ancient institutions; 18 legacy institutions removed; "
        f"{unlock_count} ancient-system unlocks; "
        f"{len(start_research_rows(records))} opening profiles researchable; "
        f"starting tiers 1/2/3/4 = {'/'.join(map(str, tiers))}; no vanilla unlocks)"
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
        records = advance_records()
        validate(records)
        if args.write:
            write(records)
            return 0
        return 0 if check(records) else 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"m8_knowledge: FAIL\n  - {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
