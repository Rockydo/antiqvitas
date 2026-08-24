#!/usr/bin/env python3
"""Guard obsolete startup branches and apply generated AD 1 raw-material effects.

EU5's generic hardcoded startup handler retains several country-specific 1337
initializers and assumes that Catholic and Shinto IO instances always exist.
ANTIQVITAS replaces the start managers and deliberately has neither instance
at AD 1.  This renderer preserves the installed source byte-for-byte except
for safe-scope operators on those absent IO lookups and dynamic post-campaign
date gates around dated country setup blocks. It also neutralizes every known
globally reachable comparison against post-campaign characters which do not
exist in the AD 1 registry.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path

from dates import AntqDate, END
from dead_script_links import (
    sanitize_dead_links,
    sanitize_out_of_campaign_dates,
    validate_inventory,
)
from generate_rgo_remap import rendered as rendered_rgo_remap
from generate_rgo_remap import runtime_worker_seeds
from legacy_institutions import neutralize_references
from m12_system_quarantine import neutralize_removed_country_scopes


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
SOURCE_RELATIVE = Path("game/in_game/common/on_action/_hardcoded.txt")
OUTPUT = ROOT / "in_game/common/on_action/_hardcoded.txt"
COUNTRY_MONTHLY_RELATIVE = Path("game/in_game/common/on_action/country_monthly.txt")
COUNTRY_MONTHLY_OUTPUT = ROOT / "in_game/common/on_action/country_monthly.txt"
COUNTRY_STATIC_RELATIVE = Path("game/main_menu/common/static_modifiers/country.txt")
COUNTRY_STATIC_OUTPUT = ROOT / "main_menu/common/static_modifiers/country.txt"
CHARACTER_STATIC_RELATIVE = Path("game/main_menu/common/static_modifiers/character.txt")
CHARACTER_STATIC_OUTPUT = ROOT / "main_menu/common/static_modifiers/character.txt"
DEAD_LINK_SCRIPTED_EFFECT_RELATIVES = (
    Path("game/in_game/common/international_organizations/religious_leagues.txt"),
    Path("game/in_game/common/international_organizations/sect.txt"),
    Path("game/in_game/common/scripted_effects/country_effects.txt"),
    Path("game/in_game/common/scripted_effects/international_organization_effects.txt"),
    Path("game/in_game/common/scripted_effects/on_action_effects.txt"),
    Path("game/in_game/common/script_values/chinese_expedition.txt"),
    Path("game/in_game/common/scripted_triggers/disaster_triggers.txt"),
)
STATIC_MODIFIER_SOURCE_ROOT = Path("game/main_menu/common/static_modifiers")
STATIC_MODIFIER_OUTPUT_ROOT = ROOT / "main_menu/common/static_modifiers"
RUNTIME_UNUSED_MODIFIER_MANIFEST = (
    ROOT / "config/runtime_unused_static_modifiers_eu5_1_3_11.txt"
)
UNUSED_INSTALLED_STATIC_MODIFIERS = {
    "D008_fate_of_the_phoenix_modifiers.txt": frozenset({
        "italian_siege_engines_modifier",
        "local_italian_fortifications_modifier",
        "patronize_orthodox_monastery_modifier",
        "reformation_of_the_cavalry_modifier",
        "reformation_of_the_galley_fleet_modifier",
        "reformation_of_the_infantry_modifier",
        "reformation_of_the_merchant_fleet_modifier",
        "reformation_of_the_thema_headquarters_modifier",
        "urban_development_projects_modifier",
    }),
    "character.txt": frozenset({
        "chi_leading_expedition",
        "hired_artist_from_member",
        "hired_cabinet_character_from_member",
        "hired_military_leader_from_member",
    }),
    "country.txt": frozenset({
        "aggressive_planning",
        "affirmation_of_biljno_polje",
        "bul_diplomatic_reintegration",
        "bureaucratic_spending_reform_modifier",
        "burghers_concessions_modifier",
        "clergy_concessions_modifier",
        "commenced_infrastructure_works",
        "conducted_population_census",
        "conversion_efforts_modifier",
        "curbed_burghers_power_modifier",
        "curbed_clergy_power_modifier",
        "curbed_noble_power_modifier",
        "curbed_peasants_power_modifier",
        "delhi_embassies_modifier",
        "delhi_loyal_governors_modifier",
        "delhi_reaffirm_vassal_relations_modifier",
        "distributed_imperial_circle_grant",
        "dhimmi_concessions_modifier",
        "diplomatic_betrayal_modifier",
        "expanded_palace_bureaucracy",
        "fervor_of_the_faithful_modifier",
        "imposed_circle_authority",
        "increased_tariff_control",
        "invest_in_members_administration_modifier",
        "invest_in_members_economy_modifier",
        "invest_in_members_military_modifier",
        "issued_great_warnings",
        "no_burghers_parliament_modifier",
        "no_clergy_parliament_modifier",
        "no_nobles_parliament_modifier",
        "noble_concessions_modifier",
        "orthodox_cabinet_eff_modifier",
        "orthodox_cabinet_examinations_modifier",
        "orthodox_clerical_proceedings_modifier",
        "orthodox_clerical_taxation_modifier",
        "orthodox_conversion_efforts_modifier",
        "orthodox_protect_the_faith_modifier",
        "orthodox_spiritual_literature_and_understanding_modifier",
        "parliament_approved_militarization",
        "parliament_declared_holidays",
        "patriarch_improved_relations_modifier",
        "patriarch_increase_baptism_modifier",
        "patriarch_peace_modifier",
        "patriarch_rally_population_modifier",
        "patriarch_sponsors_monasteries_modifier",
        "peasants_concessions_modifier",
        "pious_prosperity_modifier",
        "prepare_for_katun",
        "pressured_circle_loyalty",
        "promoted_moderates_modifier",
        "promoted_radicals_modifier",
        "reduction_of_circle_titles",
        "reformed_circle_coinage_leader",
        "reformed_circle_coinage_member",
        "reinforced_fortifications",
        "reformation_of_the_horde",
        "religious_concessions_modifier",
        "reduced_payment_obligations",
        "reshaped_bureaucracy",
        "rtr_appeased_the_court",
        "sengoku_incrementing_recruitment",
        "societal_value_push_absolutism",
        "societal_value_push_aristocracy",
        "societal_value_push_belligerent",
        "societal_value_push_capital_economy",
        "societal_value_push_centralization",
        "societal_value_push_communalism",
        "societal_value_push_conciliatory",
        "societal_value_push_decentralization",
        "societal_value_push_defensive",
        "societal_value_push_free_subjects",
        "societal_value_push_free_trade",
        "societal_value_push_humanist",
        "societal_value_push_individualism",
        "societal_value_push_innovative",
        "societal_value_push_inward",
        "societal_value_push_land",
        "societal_value_push_liberalism",
        "societal_value_push_mercantilism",
        "societal_value_push_naval",
        "societal_value_push_offensive",
        "societal_value_push_outward",
        "societal_value_push_plutocracy",
        "societal_value_push_quality",
        "societal_value_push_quantity",
        "societal_value_push_serfdom",
        "societal_value_push_sinicized",
        "societal_value_push_spiritualist",
        "societal_value_push_traditional_economy",
        "societal_value_push_traditionalist",
        "societal_value_push_unsinicized",
        "sovereign_of_anatolia",
        "strong_diplomacy_modifier",
        "studying_jurisprudence_modifier",
        "strengthened_ministry_of_personnel",
        "wave_of_humanism_modifier",
        "wave_of_spiritualism_modifier",
    }),
    "international_organization.txt": frozenset({
        "ghibellines_sanction_pope_modifier",
        "ghibellines_sanction_pope_own_modifier",
        "guelphs_sanction_emperor_modifier",
        "guelphs_sanction_emperor_own_modifier",
    }),
    "location.txt": frozenset({
        "enforced_rationing_policy",
        "expanded_production_of_raw_goods_modifier",
        "host_olympiad_location_modifier",
        "iw_fortify_key_location_modifier",
        "rtr_rein_in_area_modifier",
        "rot_timur_scare",
    }),
    "province.txt": frozenset({
        "cultural_intermixing_modifier",
        "hw_heretic_conversions_modifier",
        "hw_prepared_defenses_modifier",
        "rev_demoted_aristocracy_modifier",
        "recent_inspection_modifier",
        "ws_show_unity_of_faith",
    }),
    "religion.txt": frozenset({
        "atemoztli_gr",
        "atemoztli_mass",
        "atlcahualo_gr",
        "atlcahualo_mass",
        "apaturia_modifier",
        "apellai_modifier",
        "ayamarca_raymi_quilla_modifier",
        "aymoray_quilla_modifier",
        "ayrihua_quilla_modifier",
        "capac_raymi_quilla_modifier",
        "carneia_modifier",
        "chacra_conaqui_quilla_modifier",
        "chacra_yapuy_quilla_modifier",
        "coia_raymi_quilla_modifier",
        "compitalia_modifier",
        "equus_october_modifier",
        "etzalcualiztli_gr",
        "etzalcualiztli_mass",
        "fordicidia_modifier",
        "gymnopaedia_modifier",
        "halieia_modifier",
        "hatun_pucuy_quilla_modifier",
        "haucai_cusqui_quilla_modifier",
        "huey_tecuilhuitl_gr",
        "huey_tecuilhuitl_mass",
        "huey_tozoztli_gr",
        "huey_tozoztli_mass",
        "heraclean_games_modifier",
        "hetairideia_modifier",
        "laphria_modifier",
        "izcalli_gr",
        "izcalli_mass",
        "ludi_plebeii_modifier",
        "ludi_romani_modifier",
        "lupercalia_modifier",
        "lykaia_modifier",
        "mercuralia_modifier",
        "neptunalia_modifier",
        "pacha_pucuy_quilla_modifier",
        "panathenaic_games_modifier",
        "panionia_modifier",
        "ochpaniztli_gr",
        "ochpaniztli_mass",
        "panquetzaliztli_gr",
        "panquetzaliztli_mass",
        "quecholli_gr",
        "quecholli_mass",
        "quinquatria_modifier",
        "saturnalia_modifier",
        "tecuilhuitontli_gr",
        "tecuilhuitontli_mass",
        "tepeilhuitl_gr",
        "tepeilhuitl_mass",
        "teteo_eco_gr",
        "teteo_eco_mass",
        "tititl_gr",
        "tititl_mass",
        "tlacaxipehualiztli_gr",
        "tlacaxipehualiztli_mass",
        "tlaxochimaco_gr",
        "tlaxochimaco_mass",
        "toxcatl_gr",
        "toxcatl_mass",
        "tozoztontli_gr",
        "tozoztontli_mass",
        "uinal_ceh_modifier",
        "uinal_chen_modifier",
        "uinal_kankin_modifier",
        "uinal_kayab_modifier",
        "uinal_mac_modifier",
        "uinal_mol_modifier",
        "uinal_muan_modifier",
        "uinal_pax_modifier",
        "uinal_pop_modifier",
        "uinal_uayeb_modifier",
        "uinal_uo_modifier",
        "uinal_xul_modifier",
        "uinal_yaxkin_modifier",
        "uinal_zac_modifier",
        "uinal_zec_modifier",
        "uinal_zip_modifier",
        "uinal_zotz_modifier",
        "uma_raymi_quilla_modifier",
        "vestalia_modifier",
        "vinalia_rustica_modifier",
        "xocotl_huetzi_gr",
        "xocotl_huetzi_mass",
        "zamay_quilla_modifier",
    }),
    "unit.txt": frozenset({
        "extensive_training_modifier",
    }),
}
BANKRUPTCY_STATIC_OUTPUT = ROOT / "main_menu/common/static_modifiers/antq_bankruptcy.txt"
CAPACITY_STATIC_OUTPUT = ROOT / "main_menu/common/static_modifiers/antq_opening_capacity.txt"
AI_STABILITY_OUTPUT = ROOT / "loading_screen/common/defines/antq_ai_stability.txt"
ANCIENT_ECONOMY_OUTPUT = (
    ROOT / "loading_screen/common/defines/antq_ancient_economy.txt"
)
RGO_DEMAND_RELATIVE = Path(
    "game/in_game/common/goods_demand/special_construction_demands.txt"
)
RGO_DEMAND_OUTPUT = ROOT / "in_game/common/goods_demand/special_construction_demands.txt"
ECONOMY_GUI_RELATIVE = Path("game/in_game/gui/economy_lateralview.gui")
ECONOMY_GUI_OUTPUT = ROOT / "in_game/gui/economy_lateralview.gui"
CREDIT_GUI_RELATIVE = Path("game/in_game/gui/credit.gui")
CREDIT_GUI_OUTPUT = ROOT / "in_game/gui/credit.gui"
MARRY_NOBLE_RELATIVE = Path(
    "game/in_game/common/character_interactions/marry_noble.txt"
)
MARRY_NOBLE_OUTPUT = ROOT / "in_game/common/character_interactions/marry_noble.txt"
LOC_ROOT = ROOT / "main_menu/localization"
MIRROR_LANGUAGES = (
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


def ai_stability_defines() -> bytes:
    """Bound AI capital commitments to a pace its treasury can actually carry.

    EU5 evaluates construction candidates per location, but pays for them from
    one country treasury.  The vanilla parallel ratio lets an empire commit
    several year-long projects on every evaluation pulse while the evaluator
    capitalizes two years of projected operating income.  In the AD 1 economy
    that produced 28 simultaneous Parthian projects, estate debt above eight
    years of income, and bankruptcy in AD 6 despite a positive normal budget.

    A first bounded pass still let a freshly emptied queue rebuild every six
    months.  That made a one-location polity start roughly one project per
    half-year and a 21-location Omanite polity start two at once: by AD 5 the
    latter had completed four buildings, was paying for a fifth, and had spent
    through its opening treasury despite having no army.  Ancient capital
    formation now uses a ten-year empty/stale-queue horizon.  The engine also
    expands the initial queue from the country's displayed opening balance.
    That balance is calculated before the first monthly estate/population
    settlement, so small tribal states briefly look able to afford five or
    more projects and then pay for those stale candidates after their real
    income has settled below one gold.  An unreachable price reference
    disables only that transient-balance expansion.  Runtime comparison then
    established that the location product is floored: a zero minimum lets a
    1-33-location polity leave the forced location queue empty, while viable
    utility/balance candidates and independent RGO upgrades remain enabled.
    Active payers recovered from 65 in AD 2 to 86 in AD 5, proving this does
    not freeze construction, but division 7 still committed stale candidates
    every 2-6 months and bankrupted low-cashflow states.  Division 18 limits
    small states to roughly one queued start every 17 months.  A 0.005 parallel
    ratio (capped at three) restores proportional throughput for the largest
    empires.  A three-year empty-plan retry then passed AD 7 but caused four
    delayed bankruptcies by AD 14 as subsistence states repeated capital cycles
    faster than they could replenish reserves.  Candidate 7 isolated a second
    engine path: after committing a queued building, the native repeat formula
    replenished the queue from that candidate, so a nominal one- or two-building
    plan could become dozens of projects before the queue clear.  Disable that
    same-candidate replenishment and align both empty and non-empty refreshes to a
    fifteen-year capital cycle.  Countries still receive a location-scaled batch
    on each refresh, while independent RGO upgrades continue normally.  Runtime
    candidates 9 and 11 still started 141-147 simultaneous projects in AD 2,
    predominantly marginal Cultivator plots.  Candidate 12 then proved that the
    native monthly-location caps do not govern this evaluator: the same fresh
    interval produced 149 projects.  Those ineffective overrides are deliberately
    not retained.  Cultivator, tribal, and regional building eligibility instead
    own a shared country-level settlement and affordability contract, while this
    file bounds only the queue path proved by the runtime comparisons.  Candidate
    14 then isolated the remaining small-state losses to native RGO capital cost,
    food provisioning, and court scale rather than custom construction.  The
    subsequent AD 1-8 comparison caught Kindah taking a second RGO expansion
    on roughly 0.1 gold of monthly net revenue.  Runtime then proved the native
    RGO path ignores the general affordable-loan fraction as well as every
    construction-queue control.  Its directly mounted material demands are
    therefore adapted separately by ancient_rgo_demands().
    """
    return b"\xef\xbb\xbf" + b"""# ANTIQVITAS has no active local-governor/proximity-source building chain.\n# Avoid the engine's unused proximity-candidate market path; ordinary building AI remains enabled.\n# Ancient treasuries commit finite location-scaled project batches on a fifteen-year capital cycle and enter saving mode before debt becomes systemic.\n# Ignore the transient pre-settlement opening balance when sizing the initial queue; location count remains the durable capacity signal.\n# The engine floors the location product, so zero minimum avoids a forced candidate for small states without disabling viable utility candidates or independent RGO upgrades.\n# Disable native same-candidate queue replenishment: it otherwise turns a bounded batch into an unbounded chain before the next clear.\n# Debt-financed purchases may consume at most five percent of capacity; cash-funded buildings and RGO upgrades remain available.\n# Bound the separate monthly location evaluator to one new project per place/pulse; finite queue batches and RGO upgrades remain active.\n# Reallocate whole small trade routes: the native ten-percent transfer emits sub-unit changes below NMarket.MARKET_TRADE_CHANGE_PER_CLICK.\nNAI = {\n\tAI_PROXIMITY_CANDIDATE_UPDATE_CHANCE = 0\n\tAI_CONSTRUCTIONS_PREDICTED_INCOME_MONTHS = 6\n\tAI_CONSTRUCTIONS_EMPTY_QUEUE_UPDATE_MONTHS = 180\n\tAI_CONSTRUCTIONS_CLEAR_QUEUE_MONTHS = 180\n\tAI_CONSTRUCTION_QUEUE_SIZE_OWNED_LOCATIONS_MULT = 0.03\n\tAI_CONSTRUCTION_QUEUE_SIZE_BUILDING_PRICE_REFERENCE = 1000000\n\tAI_CONSTRUCTION_QUEUE_SIZE_MINIMUM = 0\n\tAI_CONSTRUCTION_QUEUE_PARALLEL_BUILD_RATIO = 0.005\n\tAI_CONSTRUCTION_QUEUE_PARALLEL_CHECK_RATIO = 0.02\n\tAI_CONSTRUCTION_QUEUE_PARALLEL_BUILD_MAX = 3\n\tAI_CONSTRUCTION_QUEUE_PARALLEL_CHECK_MAX = 20\n\tAI_CONSTRUCTION_QUEUE_REPEAT_MULT = 0\n\tAI_CONSTRUCTION_QUEUE_REPEAT_BIAS = 1000000\n\tAI_STEAL_MERCHANT_CAPACITY_RATIO = 1\n\tAI_ALLOWED_PARALLEL_SAME_TYPE_CONSTRUCTION_RATIO = 0.005\n\tAI_ALLOWED_PARALLEL_SAME_TYPE_CONSTRUCTION_MINIMUM = 1\n\tAI_ALLOWED_PARALLEL_TOTAL_CONSTRUCTION_RATIO = 0.01\n\tAI_MAX_NEW_BUILDINGS_PER_LOCATION = 1\n\tAI_CONSTRUCTION_DAILY_RANK_BASE_DIVISION = 18\n\tAFFORDABLE_LOAN_COST_FRACTION = 0.05\n\tAI_HIGH_DEBT_RATIO_TO_TAX_BASE = 1.5\n\tAI_SAVING_MODE_MONTHS_TO_REPAY_DEBT = 36\n}\n"""
_ai_stability_defines_with_rejected_monthly_caps = ai_stability_defines


def ai_stability_defines() -> bytes:
    """Render proven construction and bounded mercenary-AI controls.

    R17's eighteen-year production observer retained a healthy mercenary
    system (445 available captains, ten hired leader records, and five live
    contracts), but three AIs submitted a hire after another country had
    already consumed the selected leader.  Keep autonomous hiring enabled and
    reduce only its default force-composition preference to one quarter.  This
    lowers simultaneous bids while leaving pools, player access, pricing,
    regional companies, and the normal hardcoded hire path untouched.
    """
    payload = _ai_stability_defines_with_rejected_monthly_caps()
    payload = payload.replace(
        b"# Debt-financed purchases may consume at most five percent of capacity; cash-funded buildings and RGO upgrades remain available.\n",
        b"",
    )
    payload = payload.replace(
        b"# Bound the separate monthly location evaluator to one new project per place/pulse; finite queue batches and RGO upgrades remain active.\n",
        b"",
    )
    for key in (
        b"AI_ALLOWED_PARALLEL_SAME_TYPE_CONSTRUCTION_RATIO",
        b"AI_ALLOWED_PARALLEL_SAME_TYPE_CONSTRUCTION_MINIMUM",
        b"AI_ALLOWED_PARALLEL_TOTAL_CONSTRUCTION_RATIO",
        b"AI_MAX_NEW_BUILDINGS_PER_LOCATION",
        b"AFFORDABLE_LOAN_COST_FRACTION",
        b"AI_STEAL_MERCHANT_CAPACITY_RATIO",
    ):
        payload = b"\n".join(
            line for line in payload.split(b"\n") if key not in line
        )
    payload = payload.replace(
        b"# Reallocate whole small trade routes: the native ten-percent transfer emits sub-unit changes below NMarket.MARKET_TRADE_CHANGE_PER_CLICK.\n",
        b"",
    )
    payload = payload.replace(
        b"NAI = {\n",
        b"# Preserve autonomous ancient mercenary hiring while reducing same-tick "
        b"competition for globally shared captains.\nNAI = {\n"
        b"\tDEFAULT_MERCENARY_ARMY_PREFERENCE = 0.25\n",
        1,
    )
    if payload.count(b"DEFAULT_MERCENARY_ARMY_PREFERENCE = 0.25") != 1:
        raise ValueError("mercenary AI preference must be emitted exactly once")
    return payload


def ancient_economy_defines() -> bytes:
    """Scale salaried overhead and both halves of native RGO capital cost.

    RGO construction demand controls only the material stream.  EU5 separately
    charges a hardcoded cash purchase from ``GOODS_RGO_BASE_COST`` and
    ``GOODS_RGO_PRICE_SCALE``.  R14 proved the distinction: after material
    intensity fell to one twentieth, Thamud still paid 50.25 gold for an
    expansion, began another, and accumulated 112.71 debt by AD 9.  Scale both
    cash terms to one twentieth as well; this preserves a real investment cost
    while making repeated field expansion commensurate with ancient rural
    works and the polity's actual cashflow.
    """
    return b"\xef\xbb\xbf" + b"""# ANTIQVITAS ancient public-finance scale.
# Palace and diplomatic service is embedded in aristocratic, municipal,
# temple, and household obligations rather than an early-modern salaried
# apparatus.  The one-percent fractions retain material operating budgets.
# Native RGO upgrades also contain a cash purchase independent of their
# material demand; both terms use the same one-twentieth ancient capital scale.
NEconomy = {
\tCOURT_SPENDING_FRACTON = 0.01
\tDIPLOMATIC_SPENDING_FRACTION = 0.01
\tGOODS_RGO_BASE_COST = 0.025
\tGOODS_RGO_PRICE_SCALE = 0.0125
}
"""


START_HEADER = re.compile(r"^\s*on_game_start\s*=\s*\{\s*(?:#.*)?$")
COUNTRY_HEADER = re.compile(r"^(?P<indent>\s*)c:(?P<tag>[A-Z]{3})\s*=\s*\{\s*(?:#.*)?$")
SAFE_SCOPE = re.compile(
    r"^(?P<indent>\s*)(?P<scope>religion:catholic|"
    r"international_organization:catholic_church|"
    r"international_organization:shinto)\s*=\s*\{"
)
RGO_SETUP_ANCHOR = re.compile(r"^\s*setup_area_preferences\s*=\s*yes\s*(?:#.*)?$")
EXPECTED_COUNTRY_GATES = Counter({
    "CHI": 1,
    "MAJ": 1,
    "JAP": 1,
    "BYZ": 2,
    "VER": 1,
    "TEU": 1,
    "BUL": 1,
})
EXPECTED_SAFE_SCOPES = Counter({
    "religion:catholic": 1,
    "international_organization:catholic_church": 2,
    "international_organization:shinto": 2,
})
EXPECTED_RGO_CHANGE_COUNT = 848
EXPECTED_CUSTOM_RGO_GOODS = frozenset({
    "antq_barley",
    "antq_camels",
    "antq_coconuts",
    "antq_dates",
    "antq_jade",
    "antq_naphtha",
    "antq_papyrus",
    "antq_sesame",
    "antq_silphium",
    "antq_tree_nuts",
})
EXPECTED_ANNONA_SEED_LOCATIONS = frozenset({"cagliari", "faiyum", "sousse", "syracuse"})
ANNONA_ROUTES = ROOT / "docs/m5/annona_trade_routes.csv"
ROMAN_MINT_ROUTES = ROOT / "docs/m5/roman_mint_trade_routes.csv"
RGO_AUDIT = ROOT / "docs/m5/global_rgo_audit.csv"
TAG_MAP = ROOT / "docs/world_1ad/tag_map.json"
ANNONA_ROUTE_FIELDS = (
    "source_location", "destination_location", "merchant_location", "good",
    "desired", "locked", "source", "confidence", "note",
)
EXPECTED_ANNONA_ROUTE_SOURCES = frozenset({"cagliari", "faiyum", "sousse", "syracuse"})
EXPECTED_ROMAN_MINT_ROUTES = {
    "huelva": "silver",
    "kutlovitsa": "goods_gold",
}
EXPECTED_ROMAN_MINT_RUNTIME_SUPPLY = {
    "huelva": "silver",
    "kutlovitsa": "goods_gold",
}
EXPECTED_ROMAN_MINT_RUNTIME_AMOUNTS = {
    "huelva": 1,
    "kutlovitsa": 2,
}
LEGACY_EVENT_REGISTRY_ANCHORS = (
    "imperial_circles.1",
    "imperial_circles.11",
    "imperial_circles.12",
    "imperial_circles.70",
    "imperial_circles.71",
)
OPENING_PROVINCE_FOOD_RESERVE = Decimal("0.50")
OPENING_CAPACITY_LEDGER = ROOT / "docs/world_1ad/opening_capacity_adapters.csv"
OPENING_CAPACITY_FIELDS = (
    "location", "engine_excess_people", "capacity_bonus_thousands",
)
OPENING_CAPACITY_CALIBRATION = ROOT / "docs/world_1ad/opening_capacity_residual_calibration.csv"
OPENING_CAPACITY_CALIBRATION_FIELDS = (
    "location", "initial_bonus_thousands", "residual_excess_people",
    "effective_capacity_rate", "final_bonus_thousands",
)
OPENING_CAPACITY_TIERS = (1, 2, 5, 10, 15, 20, 25, 30, 35, 40, 50, 60, 75, 100, 150, 200, 300, 400)
OBSOLETE_COUNTRY_STATIC_MODIFIERS = (
    "chi_administration_in_disarray",
    "chi_yuan_religious_stability",
)
OBSOLETE_CHARACTER_STATIC_MODIFIERS = (
    "sbl_heir_of_empty_coat",
    "is_byz_john_kantakouzenos",
    "is_tim_timur",
    "is_lbv_heinrich_xiv_wittelsbach",
)
EXPECTED_OPENING_CAPACITY_LOCATIONS = 464
EXPECTED_OPENING_CAPACITY_EXCESS = 6_506_587
EXPECTED_OPENING_CAPACITY_RESIDUAL_LOCATIONS = 61
EXPECTED_OPENING_CAPACITY_RESIDUAL_EXCESS = 322_966
LEGACY_INSTITUTION_CALLBACK = """#root = country, scope:target = institution
on_institution_embraced = {
	effect = {
		if = {
			limit = { scope:target = institution:scientific_revolution }
			root = { trigger_event_non_silently = institution_events.139 }
		}
		if = {
			limit = { scope:target = institution:artillery_institution }
			root = { trigger_event_non_silently = institution_events.115 }
		}
		if = {
			limit = { scope:target = institution:printing_press }
			root = { add_country_modifier = { modifier = printing_press_books years = -1 } }
		}
	}
}"""
ANTIQUE_INSTITUTION_CALLBACK = """#root = country, scope:target = institution
on_institution_embraced = {
	effect = {
		# ANTIQVITAS: retain unreachable registry anchors for two installed events.
		if = {
			limit = { always = no }
			root = { trigger_event_non_silently = institution_events.139 }
		}
		if = {
			limit = { always = no }
			root = { trigger_event_non_silently = institution_events.115 }
		}
	}
}"""
FRONTIER_OWNER_HOOK = "\t\tantq_frontier_owner_name_effect = yes"
ABSENT_CHARACTER_COMPARISONS = (
    (
        "\t\t\t\truler ?= character:dlh_muhammad_bin_tughluq",
        "\t\t\t\talways = no # ANTIQVITAS: post-campaign Muhammad bin Tughluq hook",
        "Muhammad bin Tughluq siege",
    ),
    (
        "\t\t\tlimit = { scope:old_ruler = character:maj_hayam_wuruk }",
        "\t\t\tlimit = { always = no } # ANTIQVITAS: post-campaign Hayam Wuruk hook",
        "Hayam Wuruk ruler-death",
    ),
    (
        "\t\t\t\tscope:old_ruler = character:grm_yakub_i",
        "\t\t\t\talways = no # ANTIQVITAS: post-campaign Yakub I hook",
        "Yakub I ruler-death",
    ),
)
ABSENT_CHARACTER_SCOPES = (
    (
        "\t\t\tcharacter:sco_robert_the_bruce = {",
        "\t\t\tcharacter:sco_robert_the_bruce ?= {",
        "Robert the Bruce civil-war",
    ),
)
BUKKA_RAYA_COMPARISON = (
    "\t\t\t\tscope:recipient = character:vij_bukka_raya_sangama"
)
BUKKA_RAYA_NEUTRAL = (
    "\t\t\t\talways = no # ANTIQVITAS: post-campaign Bukka Raya hook"
)
VIJ_BATTLE_CHARACTER_COMPARISONS = (
    (
        "\t\t\t\t\t\tcharacter:vij_harihara_sangama = {\n"
        "\t\t\t\t\t\t\tis_ruler = yes\n"
        "\t\t\t\t\t\t}",
        "Harihara Sangama",
    ),
    (
        "\t\t\t\t\t\tcharacter:vij_bukka_raya_sangama = {\n"
        "\t\t\t\t\t\t\tis_ruler = yes\n"
        "\t\t\t\t\t\t}",
        "Bukka Raya",
    ),
)
PATRIARCH_SETUP_LIMIT = (
    "\t\t#Set up patriarchates\n"
    "\t\tevery_international_organization = {\n"
    "\t\t\tlimit = {\n"
    "\t\t\t\tinternational_organization_type = "
    "international_organization_type:autocephalous_patriarchate"
)
PATRIARCH_SETUP_LIMIT_GUARDED = (
    PATRIARCH_SETUP_LIMIT
    + "\n\t\t\t\tcurrent_date > {end} "
    "# ANTIQVITAS: medieval patriarch identities are outside the campaign"
)
PHOENIX_DLC_LIMIT = (
    "\t\t}\n"
    "\t\tif = {\n"
    "\t\t\tlimit = {\n"
    '\t\t\t\thas_dlc = "d008_fate_of_the_phoenix"\n'
    "\t\t\t}\n"
    "\t\t\treligion:orthodox = {"
)
PHOENIX_DLC_LIMIT_GUARDED = (
    "\t\t}\n"
    "\t\tif = {\n"
    "\t\t\tlimit = {\n"
    '\t\t\t\thas_dlc = "d008_fate_of_the_phoenix"\n'
    "\t\t\t\tcurrent_date > {end} "
    "# ANTIQVITAS: medieval pentarchy identities are outside the campaign\n"
    "\t\t\t}\n"
    "\t\t\treligion:orthodox = {"
)


def source_path() -> Path:
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
        source = Path(str(config["game_dir"])) / SOURCE_RELATIVE
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot resolve installed hardcoded startup handler: {exc}") from exc
    if not source.is_file():
        raise ValueError(f"installed hardcoded startup handler is missing: {source}")
    return source


def installed_path(relative: Path) -> Path:
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
        source = Path(str(config["game_dir"])) / relative
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot resolve installed source {relative}: {exc}") from exc
    if not source.is_file():
        raise ValueError(f"installed source is missing: {source}")
    return source


def brace_delta(line: str) -> int:
    code = line.split("#", 1)[0]
    return code.count("{") - code.count("}")


def newline_for(line: str) -> str:
    return "\r\n" if line.endswith("\r\n") else "\n"


def neutral_marry_noble() -> bytes:
    """Preserve ancient marriage while removing one absent medieval identity."""
    raw = installed_path(MARRY_NOBLE_RELATIVE).read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    if text.count(BUKKA_RAYA_COMPARISON) != 1:
        raise ValueError("installed Bukka Raya marriage hook inventory drift")
    text = text.replace(BUKKA_RAYA_COMPARISON, BUKKA_RAYA_NEUTRAL, 1)
    text = re.sub(r"[ \t]+(?=\r?$)", "", text, flags=re.MULTILINE)
    return (b"\xef\xbb\xbf" if has_bom else b"") + text.encode("utf-8")


def ancient_rgo_demands() -> bytes:
    """Scale the native RGO path to ancient, low-cash capital formation.

    True RGO upgrades bypass building eligibility, queue cadence, saving-mode,
    and affordable-loan controls.  The installed 0.1 daily lumber/masonry
    demand charged a minor polity roughly 80 gold before even completing a
    basic field expansion.  The first one-fifth adapter was still too large:
    a fresh Thamud AI began seven upgrades by AD 10, accumulated 104 gold of
    debt, and defaulted despite a positive settled peacetime budget.  One
    twentieth of the installed material intensity preserves a real market
    purchase and the full native build time while bringing this otherwise
    ungoverned capital path into the same range as ANTIQVITAS's small rural
    works.
    """
    raw = installed_path(RGO_DEMAND_RELATIVE).read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    pattern = re.compile(
        r"(?m)^(?P<indent>\s*)(?P<good>lumber|masonry)\s*=\s*0\.1\s*$"
    )
    matches = pattern.findall(text)
    if len(matches) != 5 or Counter(good for _indent, good in matches) != Counter(
        {"lumber": 4, "masonry": 1}
    ):
        raise ValueError("installed RGO construction-demand inventory drift")
    text = pattern.sub(
        lambda match: f"{match.group('indent')}{match.group('good')} = 0.005",
        text,
    )
    return (b"\xef\xbb\xbf" if has_bom else b"") + text.encode("utf-8")


def runtime_rgo_effects(newline: str) -> list[str]:
    """Validate the M5 ledger without mutating raw materials at startup.

    EU5 1.3.11 accepts individual commands but crashes in its first-quarter
    renderer/market refresh after any bookmark-time ``change_raw_material``
    operation.  Keep the complete sourced ledger checked, but do not emit the
    unsafe live effect until the engine supplies a safe batch surface.
    """
    _, _, changes = rendered_rgo_remap()
    if len(changes) != EXPECTED_RGO_CHANGE_COUNT:
        raise ValueError(
            "runtime RGO inventory drift: "
            f"expected {EXPECTED_RGO_CHANGE_COUNT}, found {len(changes)}"
        )
    locations = [location for location, _, _, _, _ in changes]
    if len(locations) != len(set(locations)):
        raise ValueError("runtime RGO ledger contains duplicate location effects")
    custom_goods = {replacement_good for _, _, _, _, replacement_good in changes if replacement_good.startswith("antq_")}
    if custom_goods != EXPECTED_CUSTOM_RGO_GOODS:
        raise ValueError(
            "runtime custom-good inventory drift: "
            f"expected {sorted(EXPECTED_CUSTOM_RGO_GOODS)}, found {sorted(custom_goods)}"
        )
    annona_seeds = runtime_worker_seeds()
    if {location for location, *_ in annona_seeds} != EXPECTED_ANNONA_SEED_LOCATIONS:
        raise ValueError(
            "runtime annona-seed inventory drift: "
            f"expected {sorted(EXPECTED_ANNONA_SEED_LOCATIONS)}, "
            f"found {sorted(location for location, *_ in annona_seeds)}"
        )
    return [
        "\t\t# ANTIQVITAS M5 RGO ledger is validated but intentionally not "
        f"mutated at bookmark startup (EU5 1.3.11 first-quarter crash).{newline}",
    ]


def annona_route_rows() -> tuple[list[dict[str, str]], str]:
    """Load the route ledger and resolve Rome through the generated tag map."""
    with ANNONA_ROUTES.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if tuple(reader.fieldnames or ()) != ANNONA_ROUTE_FIELDS:
            raise ValueError("annona route ledger field order drift")
        rows = list(reader)
    locations = set(json.loads(
        (ROOT / "docs/vanilla_symbols/locations.json").read_text(encoding="utf-8-sig")
    ))
    goods = set(json.loads(
        (ROOT / "docs/vanilla_symbols/good.json").read_text(encoding="utf-8-sig")
    ))
    sources: set[str] = set()
    for row in rows:
        if any(not row[field].strip() for field in ANNONA_ROUTE_FIELDS):
            raise ValueError("annona route ledger contains a blank required field")
        sources.add(row["source_location"])
        for field in ("source_location", "destination_location", "merchant_location"):
            if row[field] not in locations:
                raise ValueError(f"annona route uses unknown {field} {row[field]}")
        if row["good"] not in goods:
            raise ValueError(f"annona route uses unknown good {row['good']}")
        try:
            desired = Decimal(row["desired"])
        except InvalidOperation as exc:
            raise ValueError(f"annona route has invalid desired capacity {row['desired']}") from exc
        if desired <= 0 or row["locked"] != "yes":
            raise ValueError("annona routes must have positive capacity and remain locked")
        if row["destination_location"] != "rome" or row["merchant_location"] != "rome":
            raise ValueError("annona route does not terminate through Rome's merchant market")
        if row["good"] != "wheat":
            raise ValueError("annona route ledger contains a non-wheat route")
        if row["confidence"] not in {"secure", "contested"}:
            raise ValueError(f"annona route has invalid confidence {row['confidence']}")
    if sources != EXPECTED_ANNONA_ROUTE_SOURCES or len(rows) != len(sources):
        raise ValueError(f"annona route source inventory drift: {sorted(sources)}")
    entries = json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))["entries"]
    roman_tags = [entry["engine_tag"] for entry in entries if entry["design_tag"] == "ROM"]
    if len(roman_tags) != 1:
        raise ValueError(f"Roman engine-tag mapping is not singular: {roman_tags}")
    return rows, roman_tags[0]


def annona_trade_effects(newline: str) -> list[str]:
    """Create proven country-scoped routes after markets and countries exist."""
    rows, roman_tag = annona_route_rows()
    lines = [
        f"\t\t# ANTIQVITAS M5: country-scoped annona routes; live-proven after monthly settlement.{newline}",
        f"\t\tc:{roman_tag} = {{{newline}",
    ]
    for row in rows:
        lines.extend((
            f"\t\t\tcreate_trade = {{{newline}",
            f"\t\t\t\tfrom = location:{row['source_location']}.market{newline}",
            f"\t\t\t\tto = location:{row['destination_location']}.market{newline}",
            f"\t\t\t\tmerchant = location:{row['merchant_location']}.market{newline}",
            f"\t\t\t\tgoods = goods:{row['good']}{newline}",
            f"\t\t\t\tdesired = {row['desired']}{newline}",
            f"\t\t\t\tlocked = {row['locked']}{newline}",
            f"\t\t\t}} # {row['source']}{newline}",
        ))
    lines.append(f"\t\t}}{newline}")
    return lines


def roman_mint_route_rows() -> tuple[list[dict[str, str]], str]:
    """Load empire-internal bullion routes required by Rome's coinage law."""
    with ROMAN_MINT_ROUTES.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if tuple(reader.fieldnames or ()) != ANNONA_ROUTE_FIELDS:
            raise ValueError("Roman mint route ledger field order drift")
        rows = list(reader)
    locations = set(json.loads(
        (ROOT / "docs/vanilla_symbols/locations.json").read_text(encoding="utf-8-sig")
    ))
    goods = set(json.loads(
        (ROOT / "docs/vanilla_symbols/good.json").read_text(encoding="utf-8-sig")
    ))
    actual: dict[str, str] = {}
    for row in rows:
        if any(not row[field].strip() for field in ANNONA_ROUTE_FIELDS):
            raise ValueError("Roman mint route ledger contains a blank required field")
        source = row["source_location"]
        if source in actual:
            raise ValueError(f"duplicate Roman mint source {source}")
        actual[source] = row["good"]
        for field in ("source_location", "destination_location", "merchant_location"):
            if row[field] not in locations:
                raise ValueError(f"Roman mint route uses unknown {field} {row[field]}")
        if row["good"] not in goods:
            raise ValueError(f"Roman mint route uses unknown good {row['good']}")
        try:
            desired = Decimal(row["desired"])
        except InvalidOperation as exc:
            raise ValueError(
                f"Roman mint route has invalid desired capacity {row['desired']}"
            ) from exc
        if desired <= 0 or row["locked"] != "yes":
            raise ValueError("Roman mint routes must be positive and locked")
        if row["destination_location"] != "rome" or row["merchant_location"] != "rome":
            raise ValueError("Roman mint route does not terminate through Rome's market")
        if row["confidence"] not in {"secure", "contested"}:
            raise ValueError(f"Roman mint route has invalid confidence {row['confidence']}")
    if actual != EXPECTED_ROMAN_MINT_ROUTES:
        raise ValueError(f"Roman mint route inventory drift: {actual}")

    with RGO_AUDIT.open(encoding="utf-8-sig", newline="") as stream:
        audit = {row["location"]: row for row in csv.DictReader(stream)}
    for source, good in actual.items():
        row = audit.get(source)
        if row is None or row["tag"] != "ROM" or row["ad1_good"] != good:
            raise ValueError(
                f"Roman mint source is not an owned matching AD 1 RGO: {source}/{good}"
            )

    entries = json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))["entries"]
    roman_tags = [entry["engine_tag"] for entry in entries if entry["design_tag"] == "ROM"]
    if len(roman_tags) != 1:
        raise ValueError(f"Roman engine-tag mapping is not singular: {roman_tags}")
    return rows, roman_tags[0]


def roman_mint_trade_effects(newline: str) -> list[str]:
    """Connect Rome's owned bullion RGOs to the capital coinage market."""
    rows, roman_tag = roman_mint_route_rows()
    lines = [
        f"\t\t# ANTIQVITAS S7: bounded internal bullion routes for Augustan coinage.{newline}",
        f"\t\tc:{roman_tag} = {{{newline}",
    ]
    for row in rows:
        lines.extend((
            f"\t\t\tcreate_trade = {{{newline}",
            f"\t\t\t\tfrom = location:{row['source_location']}.market{newline}",
            f"\t\t\t\tto = location:{row['destination_location']}.market{newline}",
            f"\t\t\t\tmerchant = location:{row['merchant_location']}.market{newline}",
            f"\t\t\t\tgoods = goods:{row['good']}{newline}",
            f"\t\t\t\tdesired = {row['desired']}{newline}",
            f"\t\t\t\tlocked = {row['locked']}{newline}",
            f"\t\t\t}} # {row['source']}{newline}",
        ))
    lines.append(f"\t\t}}{newline}")
    return lines


def annona_monthly_supply() -> bytes:
    """Render the safe, recurring source supply for the four Annona routes.

    Altering a location's raw material at bookmark startup is a confirmed EU5
    1.3.11 crash surface.  ``sell_goods_from_location`` is the native market
    settlement effect used by installed events: its enclosing market is the
    destination while its ``location`` argument identifies the producer being
    paid.  Run it only during Rome's monthly pulse, after the routes and
    markets exist, so each source ledger entry delivers a bounded shipment to
    the Roman destination rather than changing the map's RGO state.
    """
    seeds = runtime_worker_seeds()
    if {location for location, *_ in seeds} != EXPECTED_ANNONA_SEED_LOCATIONS:
        raise ValueError("annona monthly-supply source inventory drift")
    if any(good != "wheat" for _, good, *_ in seeds):
        raise ValueError("annona monthly-supply ledger contains a non-wheat good")
    lines = [
        "\n# ANTIQVITAS M5: bounded monthly Annona source deliveries; no RGO mutation.\n",
        "antq_annona_monthly_supply = {\n",
        "\ttrigger = { tag = XAA }\n",
        "\teffect = {\n",
    ]
    for location, good, _workers, source, _confidence, _note in seeds:
        lines.extend((
            "\t\tlocation:rome.market = {\n",
            "\t\t\tsell_goods_from_location = {\n",
            f"\t\t\t\tgoods = goods:{good}\n",
            "\t\t\t\tamount = 1\n",
            f"\t\t\t\tlocation = location:{location}\n",
            f"\t\t\t}} # {source}\n",
            "\t\t}\n",
        ))
    lines.extend(("\t}\n", "}\n"))
    return "".join(lines).encode("utf-8")


def roman_mint_monthly_supply() -> bytes:
    """Guarantee bounded delivery from Rome's staffed bullion RGOs.

    Runtime qualification showed that the locked routes alone do not deliver
    either Huelva silver or Kutlovitsa gold reliably during the opening year.
    Preserve the historical gold-and-silver law and its real staffed sources
    by selling one unit of silver and two units of gold into Rome's market
    during Rome's monthly pulse.  The gold transfer remains below the 3.13
    country output observed in the live minting tooltip.  In this native effect
    the enclosing market is the sale destination and ``location`` is the
    credited producer.
    """
    rows, roman_tag = roman_mint_route_rows()
    supply_rows = [
        row for row in rows
        if row["source_location"] in EXPECTED_ROMAN_MINT_RUNTIME_SUPPLY
    ]
    actual = {
        row["source_location"]: row["good"] for row in supply_rows
    }
    if actual != EXPECTED_ROMAN_MINT_RUNTIME_SUPPLY:
        raise ValueError("Roman mint runtime-supply inventory drift")
    if set(EXPECTED_ROMAN_MINT_RUNTIME_AMOUNTS) != set(actual):
        raise ValueError("Roman mint runtime-supply amount inventory drift")
    lines = [
        "\n# ANTIQVITAS S7: bounded monthly Roman bullion-source deliveries; no RGO mutation.\n",
        "antq_roman_mint_monthly_supply = {\n",
        f"\ttrigger = {{ tag = {roman_tag} }}\n",
        "\teffect = {\n",
    ]
    for row in supply_rows:
        location = row["source_location"]
        good = row["good"]
        lines.extend((
            f"\t\tlocation:{row['destination_location']}.market = {{\n",
            "\t\t\tsell_goods_from_location = {\n",
            f"\t\t\t\tgoods = goods:{good}\n",
            f"\t\t\t\tamount = {EXPECTED_ROMAN_MINT_RUNTIME_AMOUNTS[location]}\n",
            f"\t\t\t\tlocation = location:{location}\n",
            f"\t\t\t}} # {row['source']}\n",
            "\t\t}\n",
        ))
    lines.extend(("\t}\n", "}\n"))
    return "".join(lines).encode("utf-8")


def roman_succession_monthly() -> bytes:
    """Make Rome's sourced opening succession deterministic.

    ``dynamic_historical_event.monthly_chance`` participates in the engine's
    historical-event lottery; it is not a guaranteed deadline.  Candidate 16
    therefore reached 14.11.30 with Augustus still ruling even though the
    transition event itself worked when invoked directly.  The country pulse
    is the authoritative deadline adapter: it invokes the existing idempotent
    transition events once their persisted character scopes and dates are
    both present.  It also protects a living adult succession reserve while
    that character is heir.  On accession, the reserve loses immortality and
    a new protected heir is created; this prevents both random pre-accession
    death and permanent immortal rulers.
    """
    return b"""\n# ANTIQVITAS M6: deterministic sourced Julio-Claudian succession deadlines.
antq_m6_roman_succession_monthly = {
\ttrigger = { tag = XAA }
\teffect = {
\t\tif = {
\t\t\tlimit = {
\t\t\t\tcurrent_date > 4.2.20
\t\t\t\thas_variable = antq_m6_roman_gaius_caesar
\t\t\t\thas_variable = antq_m6_roman_tiberius
\t\t\t}
\t\t\ttrigger_event_silently = antq_m6.2
\t\t}
\t\tif = {
\t\t\tlimit = {
\t\t\t\tcurrent_date > 14.8.18
\t\t\t\thas_variable = antq_m6_roman_augustus
\t\t\t\thas_variable = antq_m6_roman_tiberius
\t\t\t}
\t\t\ttrigger_event_silently = antq_m6.3
\t\t}
\t\tif = {
\t\t\tlimit = {
\t\t\t\tcurrent_date > 37.3.15
\t\t\t\thas_variable = antq_m6_roman_tiberius
\t\t\t}
\t\t\tvar:antq_m6_roman_tiberius = {
\t\t\t\tremove_character_modifier = antq_m6_historical_lifespan_guard
\t\t\t}
\t\t\tremove_variable = antq_m6_roman_tiberius
\t\t}
\t\tif = {
\t\t\tlimit = {
\t\t\t\thas_variable = antq_m6_roman_succession_reserve
\t\t\t\truler ?= var:antq_m6_roman_succession_reserve
\t\t\t}
\t\t\tvar:antq_m6_roman_succession_reserve = {
\t\t\t\tremove_character_modifier = antq_m6_historical_lifespan_guard
\t\t\t}
\t\t\tremove_variable = antq_m6_roman_succession_reserve
\t\t\tcreate_character = {
\t\t\t\tculture = culture:antq_latin
\t\t\t\treligion = religion:antq_religio_romana
\t\t\t\tdynasty = dynasty:antq_julio_claudian_dynasty
\t\t\t\testate = estate_type:nobles_estate
\t\t\t\tage = { 20 30 }
\t\t\t\tsave_scope_as = antq_m6_roman_succession_reserve_scope
\t\t\t}
\t\t\tscope:antq_m6_roman_succession_reserve_scope = {
\t\t\t\tadd_character_modifier = { modifier = antq_m6_historical_lifespan_guard years = -1 mode = add_and_extend }
\t\t\t}
\t\t\tset_variable = { name = antq_m6_roman_succession_reserve value = scope:antq_m6_roman_succession_reserve_scope }
\t\t\tset_as_designated_heir = scope:antq_m6_roman_succession_reserve_scope
\t\t}
\t\t# Seat empty cabinet slots after courtiers die so the 0.20
\t\t# crown-from-cabinet lever does not go unused. The first-open
\t\t# effect no-ops when every slot is already filled.
\t\trandom_character = {
\t\t\tlimit = { is_adult = yes in_cabinet = no NOT = { is_heir = yes } }
\t\t\tsave_scope_as = antq_m6_cabinet_refill_1
\t\t}
\t\tif = {
\t\t\tlimit = { exists = scope:antq_m6_cabinet_refill_1 }
\t\t\tadd_character_to_first_open_cabinet = { target = scope:antq_m6_cabinet_refill_1 }
\t\t}
\t\trandom_character = {
\t\t\tlimit = { is_adult = yes in_cabinet = no NOT = { is_heir = yes } }
\t\t\tsave_scope_as = antq_m6_cabinet_refill_2
\t\t}
\t\tif = {
\t\t\tlimit = { exists = scope:antq_m6_cabinet_refill_2 }
\t\t\tadd_character_to_first_open_cabinet = { target = scope:antq_m6_cabinet_refill_2 }
\t\t}
\t\trandom_character = {
\t\t\tlimit = { is_adult = yes in_cabinet = no NOT = { is_heir = yes } }
\t\t\tsave_scope_as = antq_m6_cabinet_refill_3
\t\t}
\t\tif = {
\t\t\tlimit = { exists = scope:antq_m6_cabinet_refill_3 }
\t\t\tadd_character_to_first_open_cabinet = { target = scope:antq_m6_cabinet_refill_3 }
\t\t}
\t}
}
"""



def ancient_council_session() -> bytes:
    """Reset the standing-council timer without opening the parliament UI.

    Vanilla estate satisfaction equilibrium falls by about 0.9% for every
    month since the last council.  ``call_parliament`` is quarantined to
    ``ai_tick = never``, so an unattended or AI country never convenes and
    hits -1107% after a century.  A silent start/end at the capital keeps
    the Senate/court in session on a 36-month cadence.
    """
    return b"""
# ANTIQVITAS: standing ancient councils reset the lack-of-parliament penalty.
antq_ancient_council_session = {
	trigger = {
		months_since_last_parliament_called > 36
		is_active_parliament = no
	}
	effect = {
		start_parliament_effect = yes
		end_parliament = yes
	}
}
"""


def country_monthly() -> bytes:
    """Inject ANTIQVITAS adapters into the installed monthly country pulse."""
    raw = installed_path(COUNTRY_MONTHLY_RELATIVE).read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    anchor = re.compile(
        rf"(?m)^(monthly_country_pulse\s*=\s*\{{{re.escape(newline)}"
        rf"\ton_actions\s*=\s*\{{{re.escape(newline)})"
    )
    if len(tuple(anchor.finditer(text))) != 1:
        raise ValueError("installed monthly-country pulse action anchor inventory drift")
    text = anchor.sub(
        lambda match: match.group(1)
        + f"\t\tantq_m6_roman_succession_monthly{newline}"
        + f"\t\tantq_ancient_council_session{newline}"
        + f"\t\tantq_m9_organization_ai_pulse{newline}"
        + f"\t\tantq_m10_situation_ai_pulse{newline}"
        + f"\t\tantq_s2_germania_ai_pulse{newline}"
        + f"\t\tantq_s2_arabian_route_ai_pulse{newline}"
        + f"\t\tantq_annona_monthly_supply{newline}"
        + f"\t\tantq_roman_mint_monthly_supply{newline}",
        text,
        count=1,
    )
    monthly_supply = annona_monthly_supply().decode("utf-8").replace("\n", newline)
    mint_supply = roman_mint_monthly_supply().decode("utf-8").replace("\n", newline)
    succession = roman_succession_monthly().decode("utf-8").replace("\n", newline)
    council = ancient_council_session().decode("utf-8").replace("\n", newline)
    text = neutralize_removed_country_scopes(
        text + succession + council + monthly_supply + mint_supply
    )
    return (b"\xef\xbb\xbf" if has_bom else b"") + text.encode("utf-8")


def opening_food_reserve_effects(newline: str) -> list[str]:
    """Seed bounded household, civic, and state grain stores at the bookmark.

    The installed setup surface creates every AD 1 province with an empty food
    stockpile.  Once markets settle, countries therefore buy several months of
    food at once and large states appear insolvent despite viable production.
    A percentage effect is capacity-bounded and scales with each province; it
    supplies no recurring income or production bonus.
    """
    reserve = format(OPENING_PROVINCE_FOOD_RESERVE, "f")
    return [
        f"\t\t# ANTIQVITAS S4: capacity-bounded opening food stores; not recurring supply.{newline}",
        f"\t\tevery_country = {{{newline}",
        f"\t\t\tevery_province = {{{newline}",
        f"\t\t\t\tchange_province_food_percentage = {reserve}{newline}",
        f"\t\t\t}}{newline}",
        f"\t\t}}{newline}",
    ]


def opening_capacity_rows() -> list[dict[str, str]]:
    """Load the fresh-bookmark engine audit and verify its bounded adapters."""
    with OPENING_CAPACITY_LEDGER.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if tuple(reader.fieldnames or ()) != OPENING_CAPACITY_FIELDS:
            raise ValueError("opening-capacity ledger field order drift")
        rows = list(reader)
    locations = set(json.loads(
        (ROOT / "docs/vanilla_symbols/locations.json").read_text(encoding="utf-8-sig")
    ))
    seen: set[str] = set()
    total_excess = 0
    for row in rows:
        location = row["location"]
        if location in seen or location not in locations:
            raise ValueError(f"duplicate or unknown opening-capacity location {location}")
        seen.add(location)
        try:
            excess = int(row["engine_excess_people"])
            bonus = int(row["capacity_bonus_thousands"])
        except ValueError as exc:
            raise ValueError(f"non-integer opening-capacity row for {location}") from exc
        if excess <= 0 or bonus not in OPENING_CAPACITY_TIERS:
            raise ValueError(f"invalid opening-capacity values for {location}")
        # Engine capacity modifiers use thousands, as population setup does.
        # Retain at least ten percent headroom over the observed day-one deficit.
        if bonus * 1000 < excess * 1.10:
            raise ValueError(f"opening-capacity adapter lacks margin for {location}")
        total_excess += excess
    if len(rows) != EXPECTED_OPENING_CAPACITY_LOCATIONS:
        raise ValueError(
            f"opening-capacity inventory drift: expected {EXPECTED_OPENING_CAPACITY_LOCATIONS}, "
            f"found {len(rows)}"
        )
    if total_excess != EXPECTED_OPENING_CAPACITY_EXCESS:
        raise ValueError(
            f"opening-capacity excess drift: expected {EXPECTED_OPENING_CAPACITY_EXCESS}, "
            f"found {total_excess}"
        )
    if [row["location"] for row in rows] != sorted(seen):
        raise ValueError("opening-capacity ledger must remain location-sorted")
    anchors = {row["location"]: int(row["capacity_bonus_thousands"]) for row in rows}
    if anchors.get("rome") != 300 or anchors.get("jingzhao") != 400:
        raise ValueError("Rome/Jingzhao opening-capacity anchors drifted")
    with OPENING_CAPACITY_CALIBRATION.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if tuple(reader.fieldnames or ()) != OPENING_CAPACITY_CALIBRATION_FIELDS:
            raise ValueError("opening-capacity calibration field order drift")
        calibration = list(reader)
    if len(calibration) != EXPECTED_OPENING_CAPACITY_RESIDUAL_LOCATIONS:
        raise ValueError("opening-capacity residual calibration inventory drift")
    residual_total = 0
    for row in calibration:
        location = row["location"]
        if location not in anchors:
            raise ValueError(f"capacity calibration uses unknown adapter {location}")
        try:
            initial = int(row["initial_bonus_thousands"])
            residual = int(row["residual_excess_people"])
            rate = Decimal(row["effective_capacity_rate"])
            final = int(row["final_bonus_thousands"])
        except (ValueError, InvalidOperation) as exc:
            raise ValueError(f"invalid capacity calibration values for {location}") from exc
        original = int(next(item["engine_excess_people"] for item in rows if item["location"] == location))
        if initial <= 0 or residual <= 0 or rate <= 0 or final != anchors[location]:
            raise ValueError(f"capacity calibration/adapter mismatch for {location}")
        if final * 1000 * rate < Decimal(original) * Decimal("1.25"):
            raise ValueError(f"capacity calibration lacks measured margin for {location}")
        residual_total += residual
    if residual_total != EXPECTED_OPENING_CAPACITY_RESIDUAL_EXCESS:
        raise ValueError("opening-capacity residual total drift")
    return rows


def opening_capacity_effects(newline: str) -> list[str]:
    """Apply only the capacity the fresh engine audit proved was missing."""
    lines = [
        f"\t\t# ANTIQVITAS S4: engine-proven AD 1 settlement capacity adapters.{newline}",
    ]
    for row in opening_capacity_rows():
        tier = int(row["capacity_bonus_thousands"])
        lines.extend((
            f"\t\tlocation:{row['location']} = {{{newline}",
            f"\t\t\tadd_location_modifier = {{{newline}",
            f"\t\t\t\tmodifier = antq_opening_capacity_{tier:03d}{newline}",
            f"\t\t\t\tyears = -1{newline}",
            f"\t\t\t\tmode = add_and_extend{newline}",
            f"\t\t\t}}{newline}",
            f"\t\t}}{newline}",
        ))
    return lines


def opening_capacity_static() -> bytes:
    """Render reusable location-capacity tiers in engine population units."""
    chunks: list[str] = []
    for tier in opening_capacity_tiers():
        chunks.append(
            f"antq_opening_capacity_{tier:03d} = {{\n"
            "\tgame_data = {\n"
            "\t\tcategory = location\n"
            "\t}\n\n"
            f"\tlocal_population_capacity = {tier}\n"
            "}\n"
        )
    return b"\xef\xbb\xbf" + "\n".join(chunks).encode("utf-8")


def ancient_parliament_effect(newline: str) -> list[str]:
    """Assign the deliberative institution paired with each active M6 reform.

    History setup adds reforms directly and does not reliably fire their
    ``on_activate`` effect.  The installed ``on_game_start`` callback is the
    earliest locally proven country-effect surface after governments exist.
    """
    parliament_by_reforms = (
        ("antq_roman_senate", ("antq_principate", "antq_dominate")),
        ("antq_han_court_conference", ("antq_han_imperial_bureaucracy",)),
        ("antq_iranian_great_council", (
            "antq_parthian_king_of_kings", "antq_parthian_subkingdom",
            "antq_indo_scythian_kingship", "antq_sassanid_centralized_monarchy",
        )),
        ("antq_civic_assembly", ("antq_indo_greek_kingship", "antq_settled_town_cluster")),
        ("antq_gana_assembly", ("antq_indian_ganasangha",)),
        ("antq_confederation_council", ("antq_steppe_confederation",)),
        ("antq_tribal_assembly", ("antq_advanced_chiefdom", "antq_tribal_kingdom")),
        ("antq_sacral_court", ("antq_lankan_kingdom", "antq_kushite_dual_kingship")),
        ("antq_royal_council", (
            "antq_client_monarchy", "antq_buffer_kingdom",
            "antq_regional_kingship", "antq_early_korean_kingdom",
        )),
    )
    lines = [
        f"\t\t# ANTIQVITAS S2: establish each reform's source-bounded ancient council.{newline}",
        f"\t\tevery_country = {{{newline}",
    ]
    for parliament, reforms in parliament_by_reforms:
        lines.extend((f"\t\t\tif = {{{newline}", f"\t\t\t\tlimit = {{{newline}", f"\t\t\t\t\tOR = {{{newline}"))
        lines.extend(
            f"\t\t\t\t\t\thas_reform = government_reform:{reform}{newline}"
            for reform in reforms
        )
        lines.extend((
            f"\t\t\t\t\t}}{newline}",
            f"\t\t\t\t}}{newline}",
            f"\t\t\t\tset_parliament_type = parliament_type:{parliament}{newline}",
            f"\t\t\t}}{newline}",
        ))
    lines.append(f"\t\t}}{newline}")
    return lines


def replace_top_level_block(text: str, key: str, replacement: str) -> str:
    """Replace one top-level Clausewitz block while preserving surrounding text."""
    header = re.compile(rf"(?m)^{re.escape(key)}\s*=\s*\{{\s*(?:#.*)?$")
    matches = list(header.finditer(text))
    if len(matches) != 1:
        raise ValueError(f"expected one top-level {key} block, found {len(matches)}")
    start = matches[0].start()
    depth = 0
    end: int | None = None
    for match in re.finditer(r"[{}]", text[matches[0].start():]):
        depth += 1 if match.group() == "{" else -1
        if depth == 0:
            end = matches[0].start() + match.end()
            break
    if end is None:
        raise ValueError(f"top-level {key} block does not close")
    return text[:start] + replacement + text[end:]


def remove_top_level_blocks(text: str, keys: tuple[str, ...]) -> str:
    """Remove exact obsolete definitions while retaining the installed mirror."""
    for key in keys:
        text = replace_top_level_block(text, key, "")
    return text


def runtime_unused_static_modifiers() -> frozenset[str]:
    """Load the versioned clean-start unused-modifier linker inventory."""
    if not RUNTIME_UNUSED_MODIFIER_MANIFEST.is_file():
        # Bootstrap only: --capture-runtime-unused-modifiers creates it.
        return frozenset()
    values: list[str] = []
    identifier = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
    for line_number, raw in enumerate(
        RUNTIME_UNUSED_MODIFIER_MANIFEST.read_text(
            encoding="utf-8-sig"
        ).splitlines(),
        start=1,
    ):
        value = raw.strip()
        if not value or value.startswith("#"):
            continue
        if identifier.fullmatch(value) is None:
            raise ValueError(
                "runtime unused-modifier manifest line "
                f"{line_number} is not an identifier: {value}"
            )
        values.append(value)
    if not values or values != sorted(set(values)):
        raise ValueError(
            "runtime unused-modifier manifest must be nonempty, unique, and sorted"
        )
    return frozenset(values)


def installed_static_modifier_locations() -> dict[str, str]:
    """Index unique top-level modifier definitions in installed root registries."""
    config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
    source_root = Path(str(config["game_dir"])) / STATIC_MODIFIER_SOURCE_ROOT
    if not source_root.is_dir():
        raise ValueError(f"installed static-modifier root is missing: {source_root}")
    header = re.compile(r"^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*\{")
    locations: dict[str, str] = {}
    duplicates: set[str] = set()
    for source in sorted(source_root.glob("*.txt")):
        depth = 0
        for line in source.read_text(encoding="utf-8-sig").splitlines():
            code = line.partition("#")[0]
            if depth == 0 and (match := header.match(code)) is not None:
                key = match.group("key")
                if key in locations:
                    duplicates.add(key)
                else:
                    locations[key] = source.name
            depth += brace_delta(code)
            if depth < 0:
                raise ValueError(f"{source}: top-level brace depth became negative")
        if depth != 0:
            raise ValueError(f"{source}: top-level brace contract changed")
    if duplicates:
        raise ValueError(
            "installed static modifiers repeat across root registries: "
            + ", ".join(sorted(duplicates)[:10])
        )
    return locations


def unused_static_modifiers_by_file() -> dict[str, frozenset[str]]:
    """Return the source-audited unreachable modifier inventory by file."""
    return dict(UNUSED_INSTALLED_STATIC_MODIFIERS)


def pruned_static_modifier_output(filename: str) -> bytes:
    """Mirror one installed registry file without proven unreachable keys."""
    keys = unused_static_modifiers_by_file()[filename]
    source = installed_path(STATIC_MODIFIER_SOURCE_ROOT / filename)
    raw = source.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = remove_top_level_blocks(
        raw.decode("utf-8-sig"), tuple(sorted(keys))
    )
    return (b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8")


def dead_link_scripted_effect_outputs() -> dict[Path, bytes]:
    """Mirror inherited scripted effects without unreachable variable setters."""
    validate_inventory()
    outputs: dict[Path, bytes] = {}
    for relative in DEAD_LINK_SCRIPTED_EFFECT_RELATIVES:
        source = installed_path(relative)
        raw = source.read_bytes()
        bom = raw.startswith(b"\xef\xbb\xbf")
        text, changed = sanitize_dead_links(
            raw.decode("utf-8-sig"), label=relative.as_posix()
        )
        text, date_changes = sanitize_out_of_campaign_dates(text)
        if relative.name == "international_organization_effects.txt":
            newline = "\r\n" if "\r\n" in text else "\n"
            parameter_stub = newline.join((
                "call_io_parliament = {",
                "\thidden_effect = {",
                "\t\tif = {",
                "\t\t\tlimit = { always = no }",
                "\t\t\t$international_organization$ ?= { }",
                "\t\t}",
                "\t}",
                "}",
            ))
            text = replace_top_level_block(text, "call_io_parliament", parameter_stub)
        if relative.name == "country_effects.txt":
            # Its only consumers are removed medieval content, and its body is
            # the sole remaining reference to the pruned societal-push modifier
            # family. Keep the rest of the installed scripted-effect registry.
            text = remove_top_level_blocks(
                text, ("apply_societal_value_push_modifiers",)
            )
        if changed == 0:
            raise ValueError(f"{relative}: expected at least one dead variable setter")
        expected_date_changes = 1 if relative.name == "country_effects.txt" else 0
        if date_changes != expected_date_changes:
            raise ValueError(
                f"{relative}: expected {expected_date_changes} post-campaign date "
                f"sanitizations, found {date_changes}"
            )
        output = ROOT / relative.relative_to("game")
        outputs[output] = (b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8")
    return outputs


def additional_static_modifier_outputs() -> dict[Path, bytes]:
    """Return exact-file mirrors for unused-modifier registries not patched elsewhere."""
    unused = unused_static_modifiers_by_file()
    return {
        STATIC_MODIFIER_OUTPUT_ROOT / filename: pruned_static_modifier_output(filename)
        for filename in sorted(unused)
        if filename not in {"country.txt", "character.txt"}
    }


def validate_unused_static_modifier_references() -> None:
    """Fail if a removed static modifier regains any mounted script reference."""
    unused = unused_static_modifiers_by_file()
    keys = frozenset().union(*unused.values())
    if len(keys) != 215:
        raise ValueError(
            f"unused installed static-modifier inventory drift: {len(keys)}"
        )
    token = re.compile(
        r"(?<![A-Za-z0-9_])(?:"
        + "|".join(re.escape(key) for key in sorted(keys, key=len, reverse=True))
        + r")(?![A-Za-z0-9_])"
    )
    header = re.compile(r"^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*\{")
    modifier_reference = re.compile(
        r"\b(?:add|has|remove)_(?:country|character|province|location|unit|"
        r"international_organization)_modifier\s*=|\bmodifier\s*=|"
        r"\bstatic_modifier:"
    )
    references: list[str] = []
    for phase in ("main_menu", "loading_screen", "in_game"):
        for path in sorted((ROOT / phase).rglob("*.txt")):
            text = path.read_text(encoding="utf-8-sig")
            for line_number, line in enumerate(text.splitlines(), start=1):
                code = line.partition("#")[0]
                if modifier_reference.search(code) is None:
                    continue
                matches = list(token.finditer(code))
                if not matches:
                    continue
                definition = header.match(line)
                if definition is not None and definition.group("key") in keys:
                    continue
                references.append(
                    f"{path.relative_to(ROOT).as_posix()}:{line_number}:"
                    + ",".join(match.group(0) for match in matches)
                )
    if references:
        raise ValueError(
            "removed static modifiers regained mounted references: "
            + "; ".join(references[:10])
        )


def opening_capacity_tiers() -> tuple[int, ...]:
    """Return only tiers assigned by the audited opening-capacity ledger."""
    return tuple(sorted({
        int(row["capacity_bonus_thousands"])
        for row in opening_capacity_rows()
    }))


def neutral_country_static() -> bytes:
    """Neutralize the epoch ghost and remove unreachable post-campaign blocks."""
    source = installed_path(COUNTRY_STATIC_RELATIVE)
    raw = source.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    replacement = newline.join(
        (
            "is_bankrupt = {",
            "\tgame_data = {",
            "\t\tcategory = country",
            "\t}",
            "",
            "\t# ANTIQVITAS: EU5 treats its minimum date as a recent-bankruptcy",
            "\t# timestamp. Genuine bankruptcies receive the complete effects",
            "\t# through antq_genuine_bankruptcy in on_bankruptcy instead.",
            "}",
        )
    )
    result = replace_top_level_block(text, "is_bankrupt", replacement)
    result = remove_top_level_blocks(
        result,
        tuple(sorted(
            set(OBSOLETE_COUNTRY_STATIC_MODIFIERS)
            | set(unused_static_modifiers_by_file()["country.txt"])
        )),
    )
    return (b"\xef\xbb\xbf" if bom else b"") + result.encode("utf-8")


def neutral_character_static() -> bytes:
    """Mirror installed character modifiers without unreachable legacy blocks."""
    source = installed_path(CHARACTER_STATIC_RELATIVE)
    raw = source.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = remove_top_level_blocks(
        raw.decode("utf-8-sig"),
        tuple(sorted(
            set(OBSOLETE_CHARACTER_STATIC_MODIFIERS)
            | set(unused_static_modifiers_by_file()["character.txt"])
        )),
    )
    return (b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8")


def genuine_bankruptcy_static() -> bytes:
    """Reproduce the installed bankruptcy consequences under a safe custom key."""
    text = """antq_genuine_bankruptcy = {
	game_data = {
		category = country
	}

	total_loan_capacity_modifier = -0.5
	global_estate_target_satisfaction = small_permanent_target_satisfaction_penalty
	global_crown_estate_power = -0.9
	global_pop_promotion_speed = -0.05
	global_pop_demotion_speed = 0.20
	land_morale_modifier = -0.9
	naval_morale_modifier = -0.9
	research_speed_modifier = -0.9
	global_construction_speed = -0.9
	monthly_towards_traditional_economy = societal_value_huge_monthly_move
}
"""
    return b"\xef\xbb\xbf" + text.encode("utf-8")


def bankruptcy_gui(relative: Path) -> bytes:
    """Show the native bankruptcy banner only for a real bankruptcy callback."""
    source = installed_path(relative)
    raw = source.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    native_visibility = 'visible = "[GetPlayer.GetEconomy.IsDuringBankruptcy]"'
    custom_visibility = (
        "visible = "
        '"[GetPlayer.MakeScope.GetVariable(\'antq_genuine_bankruptcy\').IsSet]"'
    )
    if text.count(native_visibility) != 1:
        raise ValueError(
            f"{relative}: expected one native bankruptcy-banner visibility"
        )
    if text.count("ShowModifierEffect('is_bankrupt')") != 1:
        raise ValueError(f"{relative}: expected one native bankruptcy tooltip")
    text = text.replace(native_visibility, custom_visibility, 1)
    text = text.replace(
        "ShowModifierEffect('is_bankrupt')",
        "ShowModifierEffect('antq_genuine_bankruptcy')",
        1,
    )
    return (b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8")


def bankruptcy_localization(language: str) -> bytes:
    text = (
        f"l_{language}:\n"
        ' STATIC_MODIFIER_NAME_antq_genuine_bankruptcy: "Bankruptcy"\n'
        ' STATIC_MODIFIER_DESC_antq_genuine_bankruptcy: "A genuine state default '
        'has disrupted credit, administration, morale, and construction."\n'
    )
    for tier in opening_capacity_tiers():
        text += (
            f' STATIC_MODIFIER_NAME_antq_opening_capacity_{tier:03d}: '
            '"Ancient Settlement Network"\n'
            f' STATIC_MODIFIER_DESC_antq_opening_capacity_{tier:03d}: '
            '"Dispersed farms, waterworks, storage, and settlement systems support the '
            'documented population of this location."\n'
        )
    return b"\xef\xbb\xbf" + text.encode("utf-8")


def render() -> bytes:
    source = source_path()
    raw = source.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    lines = raw.decode("utf-8-sig").splitlines(keepends=True)
    rendered: list[str] = []
    depth = 0
    in_start = False
    gated_depth: int | None = None
    country_gates: Counter[str] = Counter()
    safe_scopes: Counter[str] = Counter()
    out_of_campaign = AntqDate(*END).engine()
    rgo_injected = False

    for line in lines:
        code = line.split("#", 1)[0]
        if depth == 0 and START_HEADER.match(code):
            in_start = True

        country = COUNTRY_HEADER.match(code) if in_start and gated_depth is None else None
        safe = SAFE_SCOPE.match(code) if in_start and gated_depth is None else None

        if in_start and not rgo_injected and RGO_SETUP_ANCHOR.match(code):
            rendered.append(line)
            rendered.extend(runtime_rgo_effects(newline_for(line)))
            rendered.extend(opening_capacity_effects(newline_for(line)))
            rendered.extend(opening_food_reserve_effects(newline_for(line)))
            rendered.extend(annona_trade_effects(newline_for(line)))
            rendered.extend(roman_mint_trade_effects(newline_for(line)))
            rendered.extend(ancient_parliament_effect(newline_for(line)))
            rendered.append("\tc:XAA = {\n")
            rendered.append("\t\tif = {\n")
            rendered.append(
                "\t\t\tlimit = { always = no } "
                "# ANTIQVITAS unreachable inherited-event registry anchors\n"
            )
            rendered.extend(
                f"\t\t\ttrigger_event_non_silently = {event}\n"
                for event in LEGACY_EVENT_REGISTRY_ANCHORS
            )
            rendered.append("\t\t}\n")
            rendered.append("\t}\n")
            rgo_injected = True
            depth += brace_delta(code)
            continue

        if country is not None and country.group("tag") in EXPECTED_COUNTRY_GATES:
            indent = country.group("indent")
            # The outer country lookup itself must be optional: an inner date
            # gate cannot prevent the scope link from resolving at AD 1.
            rendered.append(line.replace(" =", " ?=", 1))
            depth += brace_delta(code)
            gated_depth = depth
            newline = newline_for(line)
            rendered.append(f"{indent}\tif = {{{newline}")
            rendered.append(
                f"{indent}\t\tlimit = {{ current_date > {out_of_campaign} }} "
                "# ANTIQVITAS guards dated vanilla startup\n"
            )
            country_gates[country.group("tag")] += 1
            continue

        if safe is not None:
            scope = safe.group("scope")
            rendered.append(line.replace(" =", " ?=", 1))
            safe_scopes[scope] += 1
            depth += brace_delta(code)
        elif gated_depth is not None and depth == gated_depth and code.strip() == "}":
            indent = line[: len(line) - len(line.lstrip())]
            rendered.append(f"{indent}\t}}{newline_for(line)}")
            rendered.append(line)
            depth += brace_delta(code)
            gated_depth = None
        elif gated_depth is not None:
            rendered.append(f"\t{line}" if line.strip() else line)
            depth += brace_delta(code)
        else:
            rendered.append(line)
            depth += brace_delta(code)

        if depth < 0:
            raise ValueError("hardcoded startup handler brace depth became negative")
        if in_start and depth == 0:
            in_start = False

    if depth != 0:
        raise ValueError(f"hardcoded startup handler brace depth ends at {depth}")
    if gated_depth is not None:
        raise ValueError("dated country setup block did not close")
    if not rgo_injected:
        raise ValueError("installed startup handler is missing the runtime RGO insertion anchor")
    rendered_text = "".join(rendered)
    for event in LEGACY_EVENT_REGISTRY_ANCHORS:
        anchor_pattern = re.compile(
            rf"(?m)^\s*trigger_event_non_silently\s*=\s*"
            rf"{re.escape(event)}\s*$"
        )
        if len(anchor_pattern.findall(rendered_text)) != 1:
            raise ValueError(f"legacy event registry anchor drift: {event}")
    if country_gates != EXPECTED_COUNTRY_GATES:
        raise ValueError(
            f"dated startup-country inventory drift: expected={dict(EXPECTED_COUNTRY_GATES)} "
            f"found={dict(country_gates)}"
        )
    if safe_scopes != EXPECTED_SAFE_SCOPES:
        raise ValueError(
            f"startup IO scope inventory drift: expected={dict(EXPECTED_SAFE_SCOPES)} "
            f"found={dict(safe_scopes)}"
        )
    text = "".join(rendered)
    newline = "\r\n" if "\r\n" in text else "\n"
    autocephalous_prompt = re.compile(
        r"(?m)^(?P<indent>[ \t]*)fire_generic_action\s*=\s*\{\r?\n"
        r"(?P=indent)[ \t]+type\s*=\s*join_autocephalous_patriarchate\r?\n"
        r"(?P=indent)[ \t]+actor\s*=\s*root\r?\n"
        r"(?P=indent)[ \t]+recipient\s*=\s*root\.religion\r?\n"
        r"(?P=indent)\}"
    )
    text, autocephalous_prompt_count = autocephalous_prompt.subn(
        r"\g<indent># ANTIQVITAS: medieval autocephalous membership prompt is unavailable.",
        text,
    )
    if autocephalous_prompt_count != 2:
        raise ValueError(
            "installed autocephalous generic-action prompt inventory drift: "
            f"{autocephalous_prompt_count}"
        )
    patriarch_source = PATRIARCH_SETUP_LIMIT.replace("\n", newline)
    patriarch_guarded = PATRIARCH_SETUP_LIMIT_GUARDED.replace(
        "{end}", out_of_campaign
    ).replace("\n", newline)
    if text.count(patriarch_source) != 1:
        raise ValueError("installed medieval patriarch startup inventory drift")
    text = text.replace(patriarch_source, patriarch_guarded, 1)
    phoenix_source = PHOENIX_DLC_LIMIT.replace("\n", newline)
    phoenix_guarded = PHOENIX_DLC_LIMIT_GUARDED.replace(
        "{end}", out_of_campaign
    ).replace("\n", newline)
    if text.count(phoenix_source) != 1:
        raise ValueError("installed medieval pentarchy startup inventory drift")
    text = text.replace(phoenix_source, phoenix_guarded, 1)
    for comparison, label in VIJ_BATTLE_CHARACTER_COMPARISONS:
        source = comparison.replace("\n", newline)
        neutral = (
            "\t\t\t\t\t\talways = no # ANTIQVITAS: post-campaign "
            f"{label} battle hook"
        )
        if text.count(source) != 1:
            raise ValueError(
                f"installed {label} battle-character hook inventory drift"
            )
        text = text.replace(source, neutral, 1)
    for comparison, neutral, label in ABSENT_CHARACTER_COMPARISONS:
        source = comparison.replace("\n", newline)
        replacement = neutral.replace("\n", newline)
        if text.count(source) != 1:
            raise ValueError(
                f"installed {label} character-comparison hook inventory drift"
            )
        text = text.replace(source, replacement, 1)
    for scope, optional_scope, label in ABSENT_CHARACTER_SCOPES:
        source = scope.replace("\n", newline)
        replacement = optional_scope.replace("\n", newline)
        if text.count(source) != 1:
            raise ValueError(
                f"installed {label} direct-character hook inventory drift"
            )
        text = text.replace(source, replacement, 1)
    legacy_callback = LEGACY_INSTITUTION_CALLBACK.replace("\n", newline)
    antique_callback = ANTIQUE_INSTITUTION_CALLBACK.replace("\n", newline)
    if text.count(legacy_callback) != 1:
        raise ValueError("installed post-antique institution callback inventory drift")
    text = text.replace(legacy_callback, antique_callback)
    owner_effect = re.search(
        r"(?ms)^on_location_changed_owner\s*=\s*\{.*?^\teffect\s*=\s*\{\s*(?:#.*)?\r?\n",
        text,
    )
    if owner_effect is None or text.count(FRONTIER_OWNER_HOOK) != 0:
        raise ValueError("installed location-owner callback inventory drift")
    text = (
        text[: owner_effect.end()]
        + FRONTIER_OWNER_HOOK
        + newline
        + text[owner_effect.end() :]
    )
    bankruptcy_anchor = (
        f"on_bankruptcy = {{{newline}"
        f"\teffect = {{{newline}"
    )
    if text.count(bankruptcy_anchor) != 1:
        raise ValueError("installed on_bankruptcy callback inventory drift")
    bankruptcy_adapter = (
        bankruptcy_anchor
        + f"\t\t# ANTIQVITAS: distinguish a real default from the year-one epoch ghost.{newline}"
        f"\t\tset_variable = {{ name = antq_genuine_bankruptcy value = yes years = 5 }}{newline}"
        f"\t\tif = {{{newline}"
        f"\t\t\tlimit = {{ has_variable = antq_genuine_bankruptcy }}{newline}"
        f"\t\t\tadd_country_modifier = {{ modifier = antq_genuine_bankruptcy years = 5 }}{newline}"
        f"\t\t}}{newline}"
    )
    text = text.replace(bankruptcy_anchor, bankruptcy_adapter, 1)
    civil_war_anchor = (
        f"on_civil_war_start = {{{newline}"
        f"\teffect = {{{newline}"
    )
    if text.count(civil_war_anchor) != 1:
        raise ValueError("installed on_civil_war_start callback inventory drift")
    civil_war_treasury = (
        civil_war_anchor
        + f"\t\t# ANTIQVITAS: partitioned governments control revenue but the engine does not divide the parent treasury between them.{newline}"
        f"\t\t# Give both sides a bounded three-year mobilization reserve. The former five-year/500-gold experiment prolonged wars while surrender_civil_war was accidentally quarantined; lifecycle restoration, not an oversized subsidy, is the root fix.{newline}"
        f"\t\tadd_gold = {{{newline}"
        f"\t\t\tvalue = monthly_income_trade_and_tax{newline}"
        f"\t\t\tmultiply = 36{newline}"
        f"\t\t\tmin = 25{newline}"
        f"\t\t\tmax = 250{newline}"
        f"\t\t}}{newline}"
        f"\t\tscope:target = {{{newline}"
        f"\t\t\tadd_gold = {{{newline}"
        f"\t\t\t\tvalue = monthly_income_trade_and_tax{newline}"
        f"\t\t\t\tmultiply = 36{newline}"
        f"\t\t\t\tmin = 25{newline}"
        f"\t\t\t\tmax = 250{newline}"
        f"\t\t\t}}{newline}"
        f"\t\t}}{newline}"
    )
    text = text.replace(civil_war_anchor, civil_war_treasury, 1)
    validate_inventory()
    text, _dead_links = sanitize_dead_links(text, label=SOURCE_RELATIVE.as_posix())
    text, date_changes = sanitize_out_of_campaign_dates(text)
    if date_changes != 1:
        raise ValueError(
            "hardcoded on-action post-campaign date inventory drift: "
            f"expected 1, sanitized {date_changes}"
        )
    text = neutralize_removed_country_scopes(text)
    result = neutralize_references(text, remap_effects=False).encode("utf-8")
    return (b"\xef\xbb\xbf" if has_bom else b"") + result


def write() -> None:
    outputs = {
        OUTPUT: render(),
        COUNTRY_MONTHLY_OUTPUT: country_monthly(),
        COUNTRY_STATIC_OUTPUT: neutral_country_static(),
        CHARACTER_STATIC_OUTPUT: neutral_character_static(),
        BANKRUPTCY_STATIC_OUTPUT: genuine_bankruptcy_static(),
        CAPACITY_STATIC_OUTPUT: opening_capacity_static(),
        AI_STABILITY_OUTPUT: ai_stability_defines(),
        ANCIENT_ECONOMY_OUTPUT: ancient_economy_defines(),
        RGO_DEMAND_OUTPUT: ancient_rgo_demands(),
        ECONOMY_GUI_OUTPUT: bankruptcy_gui(ECONOMY_GUI_RELATIVE),
        CREDIT_GUI_OUTPUT: bankruptcy_gui(CREDIT_GUI_RELATIVE),
        MARRY_NOBLE_OUTPUT: neutral_marry_noble(),
    }
    outputs.update(additional_static_modifier_outputs())
    outputs.update(dead_link_scripted_effect_outputs())
    for language in MIRROR_LANGUAGES:
        outputs[
            LOC_ROOT / language / f"antq_m12_bankruptcy_l_{language}.yml"
        ] = bankruptcy_localization(language)
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        print(f"m12_hardcoded_startup: wrote {path.relative_to(ROOT)}")
    validate_unused_static_modifier_references()


def check() -> bool:
    try:
        expected = render()
    except (OSError, ValueError) as exc:
        print(f"m12_hardcoded_startup: FAIL\n  - {exc}")
        return False
    expected_outputs = {
        OUTPUT: expected,
        COUNTRY_MONTHLY_OUTPUT: country_monthly(),
        COUNTRY_STATIC_OUTPUT: neutral_country_static(),
        CHARACTER_STATIC_OUTPUT: neutral_character_static(),
        BANKRUPTCY_STATIC_OUTPUT: genuine_bankruptcy_static(),
        CAPACITY_STATIC_OUTPUT: opening_capacity_static(),
        AI_STABILITY_OUTPUT: ai_stability_defines(),
        ANCIENT_ECONOMY_OUTPUT: ancient_economy_defines(),
        RGO_DEMAND_OUTPUT: ancient_rgo_demands(),
        ECONOMY_GUI_OUTPUT: bankruptcy_gui(ECONOMY_GUI_RELATIVE),
        CREDIT_GUI_OUTPUT: bankruptcy_gui(CREDIT_GUI_RELATIVE),
        MARRY_NOBLE_OUTPUT: neutral_marry_noble(),
    }
    expected_outputs.update(additional_static_modifier_outputs())
    expected_outputs.update(dead_link_scripted_effect_outputs())
    for language in MIRROR_LANGUAGES:
        expected_outputs[
            LOC_ROOT / language / f"antq_m12_bankruptcy_l_{language}.yml"
        ] = bankruptcy_localization(language)
    stale = [
        path.relative_to(ROOT)
        for path, content in expected_outputs.items()
        if not path.is_file() or path.read_bytes() != content
    ]
    if stale:
        print(
            "m12_hardcoded_startup: FAIL\n"
            "  - stale or missing " + ", ".join(map(str, stale))
        )
        return False
    try:
        validate_unused_static_modifier_references()
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        print(f"m12_hardcoded_startup: FAIL\n  - {exc}")
        return False
    print(
        "m12_hardcoded_startup: PASS "
        f"(5 safe absent-IO scopes; 8 dated country-startup gates; "
        f"{EXPECTED_RGO_CHANGE_COUNT} validated deferred RGO corrections; "
        "1 deterministic Roman succession deadline adapter; "
        "4 recurring safe Annona source deliveries; "
        "2 bounded staffed Roman bullion-source deliveries; "
        f"{EXPECTED_OPENING_CAPACITY_LOCATIONS} bounded capacity adapters; "
        "7 absent future-character hooks; 2 date-gated medieval character setups; "
        "6 unreachable legacy static modifiers; "
        "1 low-year bankruptcy epoch adapter; "
        "1 finite-batch AI capital-investment contract; "
        "5 ancient-scale native RGO construction demands; "
        "1 symmetric three-year civil-war treasury contract)"
    )
    return True


def capture_runtime_unused_modifiers(log_path: Path) -> None:
    """Capture EU5's clean-start unused static-modifier linker inventory."""
    if not log_path.is_file():
        raise ValueError(f"runtime error log is missing: {log_path}")
    pattern = re.compile(
        r"Modifier '([A-Za-z_][A-Za-z0-9_]*)' was not used by the script or code"
    )
    observed = sorted(set(pattern.findall(log_path.read_text(encoding="utf-8-sig"))))
    if not observed:
        raise ValueError("runtime error log contains no unused static modifiers")
    locations = installed_static_modifier_locations()
    unknown = sorted(set(observed) - locations.keys())
    if unknown:
        raise ValueError(
            "runtime unused-modifier inventory contains non-installed definitions: "
            + ", ".join(unknown[:10])
        )
    config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
    header = [
        "# Generated by tools/m12_hardcoded_startup.py "
        "--capture-runtime-unused-modifiers.",
        "# Authoritative EU5 clean-start linker output after event quarantine.",
        f"# game_build_id={config.get('game_build_id', 'unknown')}",
    ]
    RUNTIME_UNUSED_MODIFIER_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    RUNTIME_UNUSED_MODIFIER_MANIFEST.write_text(
        "\n".join(header + observed) + "\n", encoding="utf-8"
    )
    print(
        "m12_hardcoded_startup: captured "
        f"{len(observed)} runtime unused static modifiers in "
        f"{RUNTIME_UNUSED_MODIFIER_MANIFEST}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument(
        "--capture-runtime-unused-modifiers", type=Path, metavar="ERROR_LOG"
    )
    args = parser.parse_args()
    if args.write:
        try:
            write()
        except (OSError, ValueError) as exc:
            print(f"m12_hardcoded_startup: FAIL\n  - {exc}")
            return 1
        return 0
    if args.capture_runtime_unused_modifiers is not None:
        try:
            capture_runtime_unused_modifiers(args.capture_runtime_unused_modifiers)
        except (OSError, ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            print(f"m12_hardcoded_startup: FAIL\n  - {exc}")
            return 1
        return 0
    return 0 if check() else 1


if __name__ == "__main__":
    raise SystemExit(main())
