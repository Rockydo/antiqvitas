#!/usr/bin/env python3
"""Validate and render the first sourced ANTIQVITAS M6 power foundation."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
from dataclasses import dataclass
from pathlib import Path

from dates import AntqDate, BiographyDate, M2_MIRROR_LANGUAGES
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
POLITICAL_CONTRACT_OUTPUT = ROOT / "docs/m6/political_profile_contracts.csv"
TOKEN_RE = re.compile(r"^[a-z][a-z0-9_]*$")
VALUE_RE = re.compile(r"^(?:-?(?:\d+(?:\.\d+)?|\.\d+)|[a-z][a-z0-9_]*)$")
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
    "monthly_towards_free_subjects",
    "crown_estate_power_from_cabinet", "nobles_estate_power_from_cabinet",
    "clergy_estate_power_from_cabinet", "burghers_estate_power_from_cabinet",
    "tribes_estate_power_from_cabinet", "estate_power_from_cabinet",
    "set_cabinet_member_cost_modifier", "replace_cabinet_member_cost_modifier",
))

POLITICAL_CONTRACTS: dict[str, tuple[str, str, str, str]] = {
    "antq_principate": (
        "global_nobles_estate_power=0.10|global_burghers_estate_power=0.05|"
        "nobles_estate_power_from_cabinet=0.15|replace_cabinet_member_cost_modifier=0.10",
        "P8.1;P11;P13;OCD", "secure",
        "Senatorial and equestrian access matters, but replacement carries patronage friction.",
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
    "antq_settled_town_cluster": (
        "global_peasants_estate_power=0.05|burghers_estate_power_from_cabinet=0.20|"
        "set_cabinet_member_cost_modifier=-0.10",
        "P8;P13;OCD", "contested",
        "Civic and exchange households dominate an inexpensive magistracy.",
    ),
    "antq_tribal_kingdom": (
        "global_nobles_estate_power=0.10|tribes_estate_power_from_cabinet=0.25|"
        "replace_cabinet_member_cost_modifier=0.05",
        "P8.7;P13;CAH-XI", "secure",
        "A leading house rules through powerful kindreds and office-bearing retainers.",
    ),
}

ALTERNATIVE_REFORM_OUTPUT = ROOT / "docs/m6/alternative_reform_paths.csv"
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
)

for (
    _key, _profile, _government, _name, _description, _modifiers,
    _source, _confidence, _note,
) in ALTERNATIVE_REFORMS:
    POLITICAL_CONTRACTS[_key] = (_modifiers, _source, _confidence, _note)

PROFILE_BASE_REFORMS: dict[str, tuple[str, ...]] = {
    "roman": ("antq_principate", "antq_dominate"),
    "han": ("antq_han_imperial_bureaucracy",),
    "iranian": (
        "antq_parthian_king_of_kings", "antq_parthian_subkingdom",
        "antq_indo_scythian_kingship", "antq_sassanid_centralized_monarchy",
    ),
    "civic": ("antq_indo_greek_kingship", "antq_settled_town_cluster"),
    "gana": ("antq_indian_ganasangha",),
    "steppe": (),
    "tribal": ("antq_advanced_chiefdom", "antq_tribal_kingdom"),
    "sacral": (),
    "royal": (
        "antq_client_monarchy", "antq_buffer_kingdom", "antq_regional_kingship",
    ),
    "xiongnu": ("antq_steppe_confederation",),
    "goguryeo": ("antq_early_korean_kingdom",),
    "kushite": ("antq_kushite_dual_kingship",),
    "lankan": ("antq_lankan_kingdom",),
}
PROFILE_PARLIAMENTS = {
    "roman": "antq_roman_senate",
    "han": "antq_han_court_conference",
    "iranian": "antq_iranian_great_council",
    "civic": "antq_civic_assembly",
    "gana": "antq_gana_assembly",
    "steppe": "antq_confederation_council",
    "tribal": "antq_tribal_assembly",
    "sacral": "antq_sacral_court",
    "royal": "antq_royal_council",
    "xiongnu": "antq_xiongnu_wing_council",
    "goguryeo": "antq_goguryeo_royal_council",
    "kushite": "antq_meroitic_royal_council",
    "lankan": "antq_anuradhapura_royal_council",
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
        "source", "confidence", "note",
    ))
    writer.writerows(ALTERNATIVE_REFORMS)
    return output.getvalue()


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
    if len(POLITICAL_CONTRACTS) != 45 or not used_reforms.issubset(POLITICAL_CONTRACTS):
        failures.append(
            "political appointment contracts must cover 19 core and 26 alternative reforms"
        )
    if len({contract[0] for contract in POLITICAL_CONTRACTS.values()}) < 30:
        failures.append("political appointment contracts are insufficiently differentiated")
    alternative_profiles = [row[1] for row in ALTERNATIVE_REFORMS]
    if len(ALTERNATIVE_REFORMS) != 26 or any(
        alternative_profiles.count(profile) != 2
        for profile in {
            "roman", "han", "iranian", "civic", "gana", "steppe", "tribal",
            "sacral", "royal", "xiongnu", "goguryeo", "kushite", "lankan",
        }
    ):
        failures.append("alternative reforms must provide two paths for every political profile")
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
        "character_db = {",
    ]
    for row in data.characters:
        lines.extend((
            f"\t{row['key']} = {{",
            f"\t\tfirst_name = {{ name = {row['key']} }}",
            f"\t\tculture = {row['culture']}",
            f"\t\treligion = {row['religion']}",
        ))
        if row["female"] == "yes":
            lines.append("\t\tfemale = yes")
        if all(row[field] for field in ("adm", "dip", "mil")):
            lines.append(f"\t\tadm = {row['adm']} dip = {row['dip']} mil = {row['mil']}")
        for field in ("birth_date", "death_date"):
            if row[field]:
                lines.append(f"\t\t{field} = {BiographyDate.parse(row[field]).engine()}")
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


def government_block(
    row: dict[str, str], current_term: dict[str, str] | None = None
) -> list[str]:
    lines = [
        "\t\t\tgovernment = {",
        f"\t\t\t\ttype = {row['government_type']}",
        f"\t\t\t\their_selection = {row['heir_selection']}",
    ]
    if row["ruler"]:
        lines.append(f"\t\t\t\truler = {row['ruler']}")
    if current_term:
        # The installed start data pairs a named current ruler with a
        # `ruler_term`.  At an AD 1 campaign boundary the source ledger cannot
        # honestly supply a pre-start accession date, while `1.1.1` itself is
        # rejected as future.  A date-less current term establishes the
        # sourced incumbent without asserting an unsupported accession day.
        lines.append("\t\t\t\truler_term = {")
        lines.append(f"\t\t\t\t\tcharacter = {current_term['character']}")
        if current_term["regnal_number"]:
            lines.append(f"\t\t\t\t\tregnal_number = {current_term['regnal_number']}")
        lines.append("\t\t\t\t}")

    def append_field(field: str) -> None:
        if row[field]:
            value = (
                AntqDate.parse(row[field]).engine()
                if field in {"start_regency_date", "end_regency_date"}
                else row[field]
            )
            lines.append(f"\t\t\t\t{field} = {value}")

    if row["regency"]:
        # Match the installed native regency shape.  The source ledger retains
        # the sitting head, but an open ruler_term at exactly 1.1.1 is rejected
        # by the installed engine as a future term; the heir field supplies the
        # current head for the start state.
        for field in ("regency", "active_regent", "start_regency_date", "end_regency_date", "heir", "consort"):
            append_field(field)
    else:
        for field in ("heir", "consort", "active_regent", "regency", "start_regency_date", "end_regency_date"):
            append_field(field)
    lines.extend((
        "\t\t\t\treforms = {",
        f"\t\t\t\t\t{row['reform']}",
        "\t\t\t\t}",
    ))
    lines.append("\t\t\t\tprivilege = {")
    lines.extend(f"\t\t\t\t\t{privilege}" for privilege in pipe_values(row["privileges"], "government privileges"))
    lines.append("\t\t\t\t}")
    lines.append("\t\t\t\tlaws = {")
    lines.extend(f"\t\t\t\t\t{law} = {option}" for law, option in assignments(row["laws"], "government laws"))
    lines.append("\t\t\t\t}")
    lines.extend(f"\t\t\t\t{key} = {value}" for key, value in assignments(row["societal_values"], "government societal values"))
    lines.append("\t\t\t}")
    return lines


def reforms() -> str:
    rendered = """# Generated by tools/m6_power.py --write; M6 historical government adapters.
# These retain the five locally installed government types and use only local modifier keys.
# Flat research represents the institutions that transmit practical knowledge;
# literacy remains a separate population process and scales it further.
antq_principate = {
	major = yes
	government = monarchy
	country_modifier = {
		global_crown_estate_power = 0.10
		monthly_towards_centralization = societal_value_monthly_move
		monthly_gold_income = 500
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
"""
    parliament_by_reform = {
        reform: PROFILE_PARLIAMENTS[profile]
        for profile, reforms_for_profile in PROFILE_BASE_REFORMS.items()
        for reform in reforms_for_profile
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
        block = block.replace(
            modifier_anchor, f"{modifier_anchor}{contract_lines}", 1
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
    alternatives_by_profile = {
        profile: tuple(row[0] for row in ALTERNATIVE_REFORMS if row[1] == profile)
        for profile in PROFILE_BASE_REFORMS
    }
    lines = [rendered.rstrip(), "", "# Profile-locked alternative ancient reform paths."]
    for (
        key, profile, government, _name, _description, modifier_text,
        _source, _confidence, _note,
    ) in ALTERNATIVE_REFORMS:
        family = PROFILE_BASE_REFORMS[profile] + alternatives_by_profile[profile]
        lines.extend((
            f"{key} = {{", "\tmajor = yes", f"\tgovernment = {government}",
            "\tpotential = {", "\t\tOR = {",
            *(f"\t\t\thas_reform = government_reform:{reform}" for reform in family),
            "\t\t}", "\t}", "\tcountry_modifier = {",
            *(f"\t\t{modifier} = {value}" for modifier, value in assignments(
                modifier_text, f"alternative reform {key}"
            )),
            "\t}", "\ton_activate = {",
            f"\t\tset_parliament_type = parliament_type:{PROFILE_PARLIAMENTS[profile]}",
            "\t}", "\tyears = 2", "}", "",
        ))
    rendered = "\n".join(lines)
    return rendered


def estate_privileges(data: PowerData) -> str:
    lines = ["# Generated by tools/m6_power.py --write; M6 historical estate adapters."]
    for row in data.privileges:
        lines.extend((
            f"{row['key']} = {{",
            f"\testate = {row['estate']}",
        ))
        if row["potential_reforms"] or row["potential_tags"]:
            lines.extend(("\tpotential = {", "\t\tOR = {"))
            if row["potential_reforms"]:
                reforms = pipe_values(
                    row["potential_reforms"], f"privilege {row['key']} potential reforms"
                )
                lines.extend(
                    f"\t\t\thas_reform = government_reform:{reform}" for reform in reforms
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


def law_definitions(data: PowerData) -> str:
    lines = ["# Generated by tools/m6_power.py --write; M6 historical legal adapters."]
    for row in data.laws:
        lines.extend((
            f"{row['law']} = {{",
            f"\tlaw_category = {row['law_category']}",
            f"\tlaw_gov_group = {row['law_gov_group']}",
            "\tpotential = {",
            f"\t\tgovernment_type = government_type:{row['law_gov_group']}",
            "\t}",
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
        ("antq_principate", "Principate"),
        ("antq_principate_desc", "A republic-facade monarchy centred on the princeps and his auctoritas."),
        ("antq_dominate", "Dominate"),
        ("antq_dominate_desc", "A later Roman monarchy emphasizing central court authority and regional administration."),
        ("antq_han_imperial_bureaucracy", "Han Imperial Bureaucracy"),
        ("antq_han_imperial_bureaucracy_desc", "A palace-centred bureaucracy whose Mandate of Heaven is represented through legitimacy and effective rule."),
        ("antq_lankan_kingdom", "Anuradhapura Kingship"),
        ("antq_lankan_kingdom_desc", "A Lankan royal court whose monastic and irrigation patronage is a central source of authority."),
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
        ("antq_buffer_kingdom", "Buffer Kingdom"),
        ("antq_buffer_kingdom_desc", "A frontier court balancing local authority against stronger neighbouring powers."),
        ("antq_kushite_dual_kingship", "Kushite Dual Kingship"),
        ("antq_kushite_dual_kingship_desc", "A Kushite royal court represented through the named Natakamani-Amanitore co-rule."),
        ("antq_steppe_confederation", "Steppe Confederation"),
        ("antq_steppe_confederation_desc", "A confederation whose chanyu must balance the leading clans."),
        ("antq_early_korean_kingdom", "Early Korean Kingdom"),
        ("antq_early_korean_kingdom_desc", "A developing royal kingdom supported by leading political houses."),
        ("antq_regional_kingship", "Regional Kingship"),
        ("antq_regional_kingship_desc", "A bounded technical monarchy adapter for an attested regional court without a defensible current ruler."),
        ("antq_advanced_chiefdom", "Advanced Chiefdom"),
        ("antq_advanced_chiefdom_desc", "A developing chiefly polity represented through the installed tribal government type."),
        ("antq_settled_town_cluster", "Settled Town Cluster"),
        ("antq_settled_town_cluster_desc", "A settled urban community represented through a bounded council adapter rather than an invented monarchy."),
        ("antq_tribal_kingdom", "Tribal Kingdom"),
        ("antq_tribal_kingdom_desc", "A kingship sustained and constrained by leading kin groups."),
    ))
    for key, _profile, _government, name, description, *_rest in ALTERNATIVE_REFORMS:
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
        REFORM_OUTPUT: reforms(),
        PRIVILEGE_OUTPUT: estate_privileges(data),
        LAW_OUTPUT: law_definitions(data),
        POLITICAL_CONTRACT_OUTPUT: political_contract_ledger(),
        ALTERNATIVE_REFORM_OUTPUT: alternative_reform_ledger(),
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
