#!/usr/bin/env python3
"""Replace EU5's societal-value union with an antiquity-era contract."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from dates import M2_MIRROR_LANGUAGES


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
VALUES = ROOT / "in_game/common/societal_values/00_default.txt"
ACTION = ROOT / "in_game/common/cabinet_actions/change_societal_values.txt"
SETUP = ROOT / "main_menu/setup/start/10_countries.txt"
REPORT = ROOT / "docs/s3/SOCIETAL_VALUES.md"
LOC_ROOT = ROOT / "main_menu/localization"
LANGUAGES = ("english", *M2_MIRROR_LANGUAGES)

VALUE_KEYS = (
    "centralization_vs_decentralization",
    "traditionalist_vs_innovative",
    "spiritualist_vs_humanist",
    "aristocracy_vs_plutocracy",
    "serfdom_vs_free_subjects",
    "mercantilism_vs_free_trade",
    "belligerent_vs_conciliatory",
    "quality_vs_quantity",
    "offensive_vs_defensive",
    "land_vs_naval",
    "capital_economy_vs_traditional_economy",
    "individualism_vs_communalism",
    "outward_vs_inward",
    "sinicized_vs_unsinicized",
    "absolutism_vs_liberalism",
    "mysticism_vs_jurisprudence",
    "latinization_vs_hellenization",
)

VALUES_TEXT = """# ANTIQVITAS exact-name replacement of the installed societal-value union.
# Technical keys remain stable for engine references; presentation and effects
# model public practice from AD 1 through 476.

centralization_vs_decentralization = {
	left_modifier = {
		global_crown_estate_power = 0.40
		global_distance_from_capital_speed_propagation = 0.15
		control_importance_modifier = 0.15
		subject_loyalty = -10
	}
	right_modifier = {
		global_estate_target_satisfaction = small_permanent_target_satisfaction
		global_estate_satisfaction_recovery = 0.001
		control_importance_modifier = -0.08
		subject_loyalty = 15
	}
	opinion_importance_multiplier = 0.5
}

traditionalist_vs_innovative = {
	left_modifier = {
		cultural_tradition_modifier = 0.75
		stability_cost_efficiency = 0.25
		embrace_institution_cost_modifier = 0.75
		institution_importance_modifier = -0.10
	}
	right_modifier = {
		global_max_literacy = 5
		cultural_influence_modifier = 0.50
		research_speed_modifier = 0.05
		embrace_institution_cost_modifier = -0.20
		institution_importance_modifier = 0.10
	}
}

spiritualist_vs_humanist = {
	left_modifier = {
		global_clergy_city_desired_pop_scaled = 0.01
		tolerance_own = 1
		global_pop_conversion_speed_modifier = 0.20
		religious_unity_importance_modifier = 0.10
	}
	right_modifier = {
		tolerance_heretic = 1
		tolerance_heathen = 1
		country_cabinet_efficiency = 0.05
		global_pop_conversion_speed_modifier = -0.20
		religious_unity_importance_modifier = -0.10
	}
}

aristocracy_vs_plutocracy = {
	left_modifier = {
		discipline = 0.05
		global_nobles_estate_power = 0.35
		global_nobles_city_desired_pop_scaled = 0.01
		court_spending_efficiency = -0.10
	}
	right_modifier = {
		selling_efficiency = small_trade_efficiency_bonus
		global_burghers_estate_power = 0.35
		global_burghers_city_desired_pop_scaled = 0.01
		market_building_levels = 0.25
	}
}

serfdom_vs_free_subjects = {
	age = age_4_reformation
	left_modifier = {
		global_raw_material_output = 0.10
		levy_recovery_modifier = 0.25
		peasants_estate_levy_size = 0.15
		global_peasant_enfranchisment = -0.20
		control_importance_modifier = 0.05
	}
	right_modifier = {
		global_pop_promotion_speed_modifier = 0.50
		global_devastation_recovery = 0.005
		peasants_estate_levy_size = -0.10
		global_peasant_enfranchisment = 0.20
		control_importance_modifier = -0.03
	}
}

mercantilism_vs_free_trade = {
	left_modifier = {
		merchant_maintenance_efficiency = 0.10
		foreign_export_from_market_efficiency = -0.05
		global_trade_protection_factor = 0.25
		import_efficiency = small_trade_efficiency_penalty
	}
	right_modifier = {
		global_trades_per_burgher = 0.50
		global_merchant_power = 0.10
		global_trade_protection_factor = -0.10
		selling_efficiency = small_trade_efficiency_bonus
	}
}

belligerent_vs_conciliatory = {
	left_modifier = {
		global_war_score_efficiency = 0.10
		casus_belli_creation_speed_modifier = 0.15
		aggressiveness_modifier = 0.08
		manpower_importance_modifier = 0.10
	}
	right_modifier = {
		diplomatic_reputation = diplomatic_reputation_mild_bonus
		country_cabinet_efficiency = 0.05
		casus_belli_creation_speed_modifier = -0.15
		aggressiveness_modifier = -0.08
		diplomacy_importance_modifier = 0.10
	}
}

quality_vs_quantity = {
	left_modifier = {
		military_tactics = 0.05
		land_morale_recovery = 0.01
		army_initiative = 0.15
		army_maintenance_efficiency = -0.05
	}
	right_modifier = {
		possible_frontage_modifier = 0.05
		food_consumption_modifier = -0.05
		army_initiative = -0.10
		army_maintenance_efficiency = 0.10
	}
	opinion_importance_multiplier = 0.5
}

offensive_vs_defensive = {
	left_modifier = {
		siege_ability = 0.05
		assault_ability = 0.05
		army_movement_speed = 0.05
		army_logistics_distance_modifier = 0.20
	}
	right_modifier = {
		fort_maintenance_efficiency = 0.20
		global_defensive = 0.25
		regiment_reinforcement_speed = 0.05
		fort_limit_modifier = 0.25
	}
}

land_vs_naval = {
	left_modifier = {
		land_cost_on_distance_from_capital_speed_propagation = 0.10
		global_max_rgo_size_modifier = 0.03
		trade_land_efficiency = small_trade_land_efficiency_bonus
		trade_sea_efficiency = large_trade_sea_efficiency_penalty
	}
	right_modifier = {
		sea_cost_on_distance_from_capital_when_maritime = -0.50
		global_maritime_presence_modifier = 0.15
		trade_sea_efficiency = small_trade_sea_efficiency_bonus
		trade_land_efficiency = small_trade_land_efficiency_penalty
	}
	opinion_importance_multiplier = 0.1
}

capital_economy_vs_traditional_economy = {
	left_modifier = {
		global_production_efficiency = medium_production_efficiency_bonus
		global_building_establishment_speed = 0.10
		global_build_buildings_efficiency = 0.10
		global_monthly_food_modifier = -0.10
	}
	right_modifier = {
		global_raw_material_output = 0.10
		global_population_capacity_modifier = 0.10
		global_max_rgo_size_modifier_in_rural = 0.15
		global_monthly_food_modifier = 0.10
	}
}

individualism_vs_communalism = {
	left_modifier = {
		land_morale_modifier = 0.05
		naval_morale_modifier = 0.05
		global_migration_speed_modifier = 0.20
		global_estate_target_satisfaction = small_permanent_target_satisfaction_penalty
	}
	right_modifier = {
		pop_join_rebel_threshold = -0.025
		revoke_privilege_cost_modifier = -0.20
		global_migration_speed_modifier = -0.20
		global_estate_target_satisfaction = small_permanent_target_satisfaction
	}
}

outward_vs_inward = {
	age = age_3_discovery
	left_modifier = {
		power_projection = 3
		diplomatic_capacity_modifier = 0.15
		aggressiveness_modifier = 0.03
		subjugation_preference_modifier = 0.05
		trade_importance_modifier = 0.05
	}
	right_modifier = {
		global_crown_estate_power = 0.15
		global_monthly_control = 0.003
		cultural_tradition_modifier = 0.25
		aggressiveness_modifier = -0.05
		subjugation_preference_modifier = -0.05
	}
}

sinicized_vs_unsinicized = {
	allow = {
		OR = {
			antq_law_profile_han_trigger = yes
			antq_law_profile_eastern_trigger = yes
		}
	}
	left_modifier = {
		legislative_efficiency = 0.15
		research_speed_modifier = 0.05
		cultural_tradition_modifier = -0.25
		tribute_payment_received_modifier = 0.10
	}
	right_modifier = {
		prestige_decay = -0.001
		stability_cost_efficiency = 0.25
		cultural_tradition_modifier = 0.25
		global_merchant_capacity_modifier = -0.10
	}
}

absolutism_vs_liberalism = {
	age = age_5_absolutism
	left_modifier = {
		global_crown_estate_power = 0.50
		revoke_privilege_cost_modifier = -0.15
		pop_join_rebel_threshold = -0.015
		global_estate_target_satisfaction = small_permanent_target_satisfaction_penalty
	}
	right_modifier = {
		cultures_capacity_modifier = 0.10
		parliament_request_issue_support_needed = -0.05
		pop_join_rebel_threshold = 0.015
		global_estate_target_satisfaction = small_permanent_target_satisfaction
	}
}

mysticism_vs_jurisprudence = {
	allow = {
		OR = {
			antq_law_profile_iranian_trigger = yes
			antq_law_profile_arabian_trigger = yes
		}
	}
	left_modifier = {
		land_morale_modifier = 0.05
		global_pop_conversion_speed_modifier = 0.05
		clergy_estate_target_satisfaction = medium_permanent_target_satisfaction
	}
	right_modifier = {
		research_speed_modifier = 0.05
		country_cabinet_efficiency = 0.05
		clergy_estate_target_satisfaction = medium_permanent_target_satisfaction
	}
}

latinization_vs_hellenization = {
	allow = {
		OR = {
			antq_law_profile_roman_trigger = yes
			antq_law_profile_hellenistic_trigger = yes
		}
	}
	left_modifier = {
		diplomatic_spending_cost = -0.10
		legislative_efficiency = 0.10
		cultural_tradition_modifier = 0.10
	}
	right_modifier = {
		stability_cost_efficiency = 0.20
		tolerance_own = 0.25
		cultural_influence_modifier = 0.25
	}
}
"""

ACTION_TEXT = """# ANTIQVITAS retained engine action for deliberate value movement.
change_societal_values = {
	ability = dip
	societal_values = 0.1
	forbid_for_automation = yes
	progress = {
		scope:actor = {
			value = societal_value_progress
		}
	}
}
"""

LOC = {
    "centralization_vs_decentralization": "Palace Rule vs Local Rule",
    "centralization_vs_decentralization_desc": "Palace rule concentrates officers, records, and obligations around the court; local rule relies on communities, councils, and subordinate rulers.",
    "centralization_focus": "Palace Rule",
    "decentralization_focus": "Local Rule",
    "traditionalist_vs_innovative": "Ancestral Custom vs Learned Inquiry",
    "traditionalist_vs_innovative_desc": "Ancestral custom protects inherited practice and stability; learned inquiry rewards recordkeeping, scholarship, and the adoption of tested methods.",
    "traditionalist_focus": "Ancestral Custom",
    "innovative_focus": "Learned Inquiry",
    "spiritualist_vs_humanist": "Sacred Authority vs Civic Concord",
    "spiritualist_vs_humanist_desc": "Sacred authority gives cult institutions a leading public role; civic concord accommodates several rites in pursuit of political peace.",
    "spiritualist_focus": "Sacred Authority",
    "humanist_focus": "Civic Concord",
    "aristocracy_vs_plutocracy": "Landed Retinues vs Mercantile Houses",
    "aristocracy_vs_plutocracy_desc": "Landed retinues place military households and hereditary notables first; mercantile houses give greater influence to wealthy traders and urban patrons.",
    "aristocracy_focus": "Landed Retinues",
    "plutocracy_focus": "Mercantile Houses",
    "serfdom_vs_free_subjects": "Bound Tenure vs Free Households",
    "serfdom_vs_free_subjects_desc": "Bound tenure ties cultivators to assessed estates and service; free households preserve movement, civic standing, and independent obligations.",
    "serfdom_focus": "Bound Tenure",
    "free_subjects_focus": "Free Households",
    "mercantilism_vs_free_trade": "Regulated Exchange vs Open Exchange",
    "mercantilism_vs_free_trade_desc": "Regulated exchange protects designated routes, staples, and official dues; open exchange gives merchants wider freedom to seek buyers and suppliers.",
    "mercantilism_focus": "Regulated Exchange",
    "free_trade_focus": "Open Exchange",
    "belligerent_vs_conciliatory": "Warlike Posture vs Conciliation",
    "belligerent_vs_conciliatory_desc": "A warlike posture treats force and intimidation as ordinary statecraft; conciliation prefers envoys, guarantees, tribute settlements, and negotiated restraint.",
    "belligerent_focus": "Warlike Posture",
    "conciliatory_focus": "Conciliation",
    "quality_vs_quantity": "Veteran Core vs Mass Muster",
    "quality_vs_quantity_desc": "A veteran core concentrates equipment and training among proven soldiers; a mass muster fields broader household and community obligations at lower cost.",
    "quality_focus": "Veteran Core",
    "quantity_focus": "Mass Muster",
    "offensive_vs_defensive": "Campaign Initiative vs Fortified Defence",
    "offensive_vs_defensive_desc": "Campaign initiative emphasizes rapid movement, siege work, and operations abroad; fortified defence invests in walls, strongpoints, and recovery near home.",
    "offensive_focus": "Campaign Initiative",
    "defensive_focus": "Fortified Defence",
    "land_vs_naval": "Landward Provision vs Maritime Reach",
    "land_vs_naval_desc": "Landward provision prioritizes roads, fields, and overland supply; maritime reach invests in ports, shipping, and command of coastal routes.",
    "land_focus": "Landward Provision",
    "naval_focus": "Maritime Reach",
    "capital_economy_vs_traditional_economy": "Urban Workshops vs Rural Provision",
    "capital_economy_vs_traditional_economy_desc": "Urban workshops concentrate skilled production and construction; rural provision expands food, raw materials, and resilient local subsistence.",
    "capital_economy_focus": "Urban Workshops",
    "traditional_economy_focus": "Rural Provision",
    "individualism_vs_communalism": "Household Autonomy vs Communal Obligation",
    "individualism_vs_communalism_desc": "Household autonomy permits greater movement and private distinction; communal obligation strengthens shared duties, collective security, and accepted custom.",
    "individualism_focus": "Household Autonomy",
    "communalism_focus": "Communal Obligation",
    "outward_vs_inward": "Frontier Engagement vs Internal Consolidation",
    "outward_vs_inward_desc": "Frontier engagement seeks influence through diplomacy, exchange, and subordinate rulers; internal consolidation strengthens control and inherited institutions.",
    "outward_focus": "Frontier Engagement",
    "inward_focus": "Internal Consolidation",
    "sinicized_vs_unsinicized": "Imperial Rites vs Local Custom",
    "sinicized_vs_unsinicized_desc": "Imperial rites adopt court ceremony, written administration, and tributary forms associated with the Han sphere; local custom preserves regional authority and practice.",
    "sinicized_focus": "Imperial Rites",
    "unsinicized_focus": "Local Custom",
    "absolutism_vs_liberalism": "Court Command vs Deliberative Rule",
    "absolutism_vs_liberalism_desc": "Court command concentrates late-antique authority in the ruler and household; deliberative rule preserves councils, assemblies, and negotiated consent.",
    "absolutism_focus": "Court Command",
    "liberalism_focus": "Deliberative Rule",
    "mysticism_vs_jurisprudence": "Revelatory Mysteries vs Learned Law",
    "mysticism_vs_jurisprudence_desc": "Revelatory mysteries privilege inspired, initiatory, and esoteric authority; learned law privileges jurists, interpreters, and recorded judgment.",
    "mysticism_focus": "Revelatory Mysteries",
    "jurisprudence_focus": "Learned Law",
    "latinization_vs_hellenization": "Latin Public Forms vs Hellenic Public Forms",
    "latinization_vs_hellenization_desc": "Latin public forms favor western legal and administrative usage; Hellenic public forms favor Greek civic, court, and documentary traditions.",
    "latinization_focus": "Latin Public Forms",
    "hellenization_focus": "Hellenic Public Forms",
    "change_societal_values": "Guide Public Practice",
    "change_societal_values_desc": "Assigns the cabinet to encourage a deliberate shift in one public practice.",
    "change_societal_values_action": "Guide Public Practice",
    "change_societal_values_active": "Guiding Public Practice",
}


def game_root() -> Path:
    data = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
    return Path(str(data["game_dir"])) / "game"


def top_level_keys(text: str) -> tuple[str, ...]:
    return tuple(
        re.findall(r"(?m)^(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*\{", text)
    )


def localization(language: str) -> str:
    lines = [f"l_{language}:"]
    for key, value in LOC.items():
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f' {key}: "{escaped}"')
    return "\n".join(lines) + "\n"


def report_text(counts: dict[str, int]) -> str:
    return f"""<!-- Generated by tools/s3_societal_values.py. -->

# S3 societal-value replacement

- Installed union: {len(VALUE_KEYS)} exact technical keys, all overridden.
- Ancient presentation: {len(LOC)} localized labels/descriptions in 11 clients.
- Opening seeds: centralization {counts['centralization_vs_decentralization']};
  custom/inquiry {counts['traditionalist_vs_innovative']}; landed/merchant
  {counts['aristocracy_vs_plutocracy']}; urban/rural
  {counts['capital_economy_vs_traditional_economy']}.
- Dated axes: Bound Tenure in Dominate; Frontier Engagement in Crisis; Court
  Command in Federate Age.
- Profile axes: Imperial Rites for Han/eastern profiles; Revelatory
  Mysteries/Learned Law for Iranian/Arabian profiles; Latin/Hellenic Public
  Forms for Roman/Hellenistic profiles.
- Cabinet movement action is retained and no longer quarantined.
"""


def expected_outputs() -> dict[Path, bytes]:
    setup_text = SETUP.read_text(encoding="utf-8")
    counts = {
        key: len(re.findall(rf"(?m)^\s*{re.escape(key)}\s*=", setup_text))
        for key in VALUE_KEYS
    }
    outputs = {
        VALUES: b"\xef\xbb\xbf" + VALUES_TEXT.encode("utf-8"),
        ACTION: b"\xef\xbb\xbf" + ACTION_TEXT.encode("utf-8"),
        REPORT: report_text(counts).encode("utf-8"),
    }
    for language in LANGUAGES:
        outputs[
            LOC_ROOT / language / f"antq_s3_societal_values_l_{language}.yml"
        ] = b"\xef\xbb\xbf" + localization(language).encode("utf-8")
    return outputs


def validate() -> list[str]:
    failures: list[str] = []
    installed = (
        game_root() / "in_game/common/societal_values/00_default.txt"
    ).read_text(encoding="utf-8-sig")
    installed_keys = top_level_keys(installed)
    authored_keys = top_level_keys(VALUES_TEXT)
    if installed_keys != VALUE_KEYS:
        failures.append(
            f"installed societal union drift: expected {VALUE_KEYS}, found {installed_keys}"
        )
    if authored_keys != VALUE_KEYS:
        failures.append(
            f"authored societal union drift: expected {VALUE_KEYS}, found {authored_keys}"
        )

    required_gates = {
        "serfdom_vs_free_subjects": "age = age_4_reformation",
        "outward_vs_inward": "age = age_3_discovery",
        "absolutism_vs_liberalism": "age = age_5_absolutism",
        "sinicized_vs_unsinicized": "antq_law_profile_eastern_trigger = yes",
        "mysticism_vs_jurisprudence": "antq_law_profile_iranian_trigger = yes",
        "latinization_vs_hellenization": "antq_law_profile_roman_trigger = yes",
    }
    for key, gate in required_gates.items():
        start = VALUES_TEXT.find(f"\n{key} = {{")
        end = VALUES_TEXT.find("\n}\n", start)
        block = VALUES_TEXT[start:end + 3]
        if gate not in block:
            failures.append(f"{key} lacks required gate {gate}")

    setup_text = SETUP.read_text(encoding="utf-8")
    for key in (
        "centralization_vs_decentralization",
        "traditionalist_vs_innovative",
        "aristocracy_vs_plutocracy",
        "capital_economy_vs_traditional_economy",
    ):
        count = len(re.findall(rf"(?m)^\s*{re.escape(key)}\s*=", setup_text))
        if count < 350:
            failures.append(f"{key} has only {count} opening seeds")

    prohibited_visible = re.compile(
        r"\b(?:absolutism|liberalism|mercantilism|serfdom|humanism|"
        r"renaissance|reformation|quran|hadith|frankish|orthodox)\b",
        re.IGNORECASE,
    )
    for key, value in LOC.items():
        match = prohibited_visible.search(value)
        if match:
            failures.append(f"{key} contains post-antique term {match.group()!r}")

    if "mounted-system quarantine" in ACTION_TEXT or "always = no" in ACTION_TEXT:
        failures.append("cabinet action remains quarantined")
    return failures


def write() -> None:
    failures = validate()
    if failures:
        raise ValueError("\n".join(failures))
    for path, payload in expected_outputs().items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    print(
        "s3_societal_values: wrote "
        f"{len(VALUE_KEYS)} values, {len(LOC)} localization entries, "
        f"{len(LANGUAGES)} clients"
    )


def check() -> bool:
    try:
        failures = validate()
        outputs = expected_outputs()
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"s3_societal_values: FAIL\n  - {exc}")
        return False
    for path, payload in outputs.items():
        if not path.is_file() or path.read_bytes() != payload:
            failures.append(f"stale or missing {path.relative_to(ROOT)}")
    if failures:
        print("s3_societal_values: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return False
    print(
        "s3_societal_values: PASS "
        f"({len(VALUE_KEYS)} exact ancient axes; {len(LOC)} labels; "
        f"{len(LANGUAGES)} clients; cabinet movement enabled)"
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        try:
            write()
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
            print(f"s3_societal_values: FAIL\n  - {exc}")
            return 1
        return 0
    return 0 if check() else 1


if __name__ == "__main__":
    raise SystemExit(main())
