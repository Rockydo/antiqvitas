#!/usr/bin/env python3
"""Generate the deep, polity-aware ANTIQVITAS legal layer.

The engine presents laws as a country-scoped group containing mutually
exclusive policies.  This generator therefore gives every opening polity one
of thirteen evidence-bounded legal profiles.  Each profile receives the same
fourteen gameplay questions, but its terminology, political beneficiaries,
starting settlement, and historical boundary remain profile-specific.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
from dataclasses import dataclass
from pathlib import Path

from dates import M2_MIRROR_LANGUAGES

ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "docs/world_1ad/polities.csv"
TAG_MAP = ROOT / "docs/world_1ad/tag_map.json"
LAW_OUTPUT = ROOT / "in_game/common/laws/01_antiquitas_s2_profile_laws.txt"
TRIGGER_OUTPUT = ROOT / "in_game/common/scripted_triggers/00_antiquitas_s2_law_profiles.txt"
PROFILE_LEDGER = ROOT / "docs/m6/ancient_law_profiles.csv"
OPTION_LEDGER = ROOT / "docs/m6/ancient_law_options.csv"
LOC_ROOT = ROOT / "main_menu/localization"

LAW_CATEGORIES = frozenset(("administrative", "military", "religious", "socioeconomic"))
ESTATES = frozenset((
    "crown_estate", "nobles_estate", "clergy_estate", "burghers_estate",
    "peasants_estate", "tribes_estate",
))
ALLOWED_MODIFIERS = frozenset((
    "ban_exports_of_slaves_goods", "ban_imports_of_slaves_goods",
    "burghers_estate_max_tax", "burghers_estate_target_satisfaction",
    "clergy_estate_max_tax", "clergy_estate_target_satisfaction",
    "country_cabinet_efficiency", "diplomatic_capacity_modifier",
    "diplomatic_reputation", "global_burghers_estate_power",
    "global_clergy_estate_power", "global_crown_estate_power",
    "global_integration_speed_modifier", "global_levy_recruitment_speed_modifier",
    "global_levy_size_modifier", "global_max_rural_control",
    "global_monthly_control", "global_monthly_food_modifier",
    "global_nobles_estate_power", "global_peasants_estate_power",
    "global_pop_assimilation_speed_modifier", "global_pop_conversion_speed_modifier",
    "global_pop_food_consumption", "global_production_efficiency",
    "global_trade_through_owned_territory_efficiency", "global_tribes_estate_power",
    "land_morale_modifier", "legislative_efficiency", "levy_combat_efficiency_modifier",
    "minting_income_factor", "minting_inflation_threshold",
    "monthly_towards_aristocracy", "monthly_towards_centralization",
    "monthly_towards_decentralization",
    "monthly_towards_free_trade", "monthly_towards_humanist",
    "monthly_towards_inward",
    "monthly_towards_outward", "monthly_towards_quality",
    "monthly_towards_quantity",
    "monthly_towards_spiritualist", "nobles_estate_max_tax",
    "nobles_estate_target_satisfaction", "peasants_estate_max_tax",
    "peasants_estate_target_satisfaction", "pop_join_rebel_threshold",
    "replace_cabinet_member_cost_modifier", "set_cabinet_member_cost_modifier",
    "slavery_blocked", "stability_cost_efficiency", "subject_loyalty",
    "tolerance_heathen", "tribes_estate_target_satisfaction",
    "wrong_culture_levy_size",
))
FORBIDDEN = frozenset((
    "feudal", "renaissance", "parliament", "serf", "colonial", "national",
    "constitutional", "modern", "medieval",
))


@dataclass(frozen=True)
class Profile:
    key: str
    name: str
    regions: tuple[str, ...]
    exact_tags: tuple[str, ...]
    central: str
    mediated: str
    local: str
    estates: tuple[str, str, str]
    extra_effects: tuple[tuple[tuple[str, str], ...], ...]
    source: str
    confidence: str
    boundary: str
    starting_stance: str = "mediated"


PROFILES = (
    Profile(
        "roman", "Roman Imperial", (), ("ROM",),
        "Censorial", "Municipal", "Provincial",
        ("crown_estate", "nobles_estate", "burghers_estate"),
        (
            (("monthly_towards_centralization", "societal_value_minor_monthly_move"),),
            (("global_nobles_estate_power", "0.03"),),
            (("global_pop_assimilation_speed_modifier", "0.01"),),
        ),
        "P8.1;P11;P13;OCD", "secure",
        "Models Roman public law and imperial administration without assuming uniform provincial practice.",
    ),
    Profile(
        "han", "Western Han", ("China",), (),
        "Imperial Secretariat", "Commandery", "County",
        ("crown_estate", "nobles_estate", "peasants_estate"),
        (
            (("global_monthly_control", "0.02"),),
            (("country_cabinet_efficiency", "0.02"),),
            (("peasants_estate_target_satisfaction", "tiny_permanent_target_satisfaction"),),
        ),
        "P8.3;P11;P13;BHR;CTP-WM", "secure",
        "Uses Western Han commandery-county and court institutions without backdating later examination systems.",
    ),
    Profile(
        "iranian", "Arsacid-Iranian", ("Iran", "Mesopotamia", "Caucasus"), (),
        "Royal Domain", "Great-House", "Regional Court",
        ("crown_estate", "nobles_estate", "tribes_estate"),
        (
            (("global_crown_estate_power", "0.03"),),
            (("global_nobles_estate_power", "0.03"),),
            (("global_tribes_estate_power", "0.03"),),
        ),
        "P8.2;P11;P13;CAH-XI;OCD", "contested",
        "Represents negotiated Arsacid royal, dynastic, civic, and temple authority rather than one codified Iranian constitution.",
    ),
    Profile(
        "hellenistic", "Eastern Mediterranean Civic-Royal",
        ("Levant", "Anatolia", "Balkans", "Pontic"), (),
        "Royal Chancery", "Civic Council", "Local Magistracy",
        ("crown_estate", "burghers_estate", "nobles_estate"),
        (
            (("global_crown_estate_power", "0.03"),),
            (("global_burghers_estate_power", "0.03"),),
            (("global_nobles_estate_power", "0.03"),),
        ),
        "P8.1;P8.4;P11;P13;OCD", "contested",
        "Provides a bounded civic-royal adapter while preserving local differences among poleis, leagues, client courts, and temple cities.",
    ),
    Profile(
        "indic", "Indic", ("India", "Lanka"), (),
        "Royal Edict", "Lineage Assembly", "Village Compact",
        ("crown_estate", "nobles_estate", "peasants_estate"),
        (
            (("monthly_towards_centralization", "societal_value_minor_monthly_move"),),
            (("global_nobles_estate_power", "0.03"),),
            (("global_peasants_estate_power", "0.03"),),
        ),
        "P8.4;P11;P13;CAH-XI", "contested",
        "Combines securely broad legal questions with locally variable royal, lineage, corporate, monastic, and village institutions.",
    ),
    Profile(
        "steppe", "Inner Asian Confederation",
        ("Steppe", "Central Asia", "Tarim"), (),
        "Chanyu Court", "Wing Council", "Pasture Assembly",
        ("crown_estate", "nobles_estate", "tribes_estate"),
        (
            (("global_crown_estate_power", "0.03"),),
            (("global_nobles_estate_power", "0.03"),),
            (("global_tribes_estate_power", "0.03"),),
        ),
        "P8.3;P11;P13;CAH-XI", "contested",
        "Models confederative bargaining, tribute, pasture, and retinue obligations without projecting later steppe law codes.",
    ),
    Profile(
        "germanic", "Germanic", ("Germania", "Scandinavia"), (),
        "King's Following", "People's Assembly", "Kindred",
        ("nobles_estate", "tribes_estate", "peasants_estate"),
        (
            (("nobles_estate_target_satisfaction", "tiny_permanent_target_satisfaction"),),
            (("global_tribes_estate_power", "0.03"),),
            (("monthly_towards_decentralization", "societal_value_minor_monthly_move"),),
        ),
        "P8.7;P11;P13;TAC-GER", "contested",
        "Uses Tacitus critically alongside archaeology and does not impose a single constitution on distinct peoples.",
    ),
    Profile(
        "celtic", "Brittonic-Hibernian", ("Britain", "Ireland"), (),
        "Royal Retinue", "Gathered Council", "Kin Community",
        ("nobles_estate", "tribes_estate", "clergy_estate"),
        (
            (("global_nobles_estate_power", "0.03"),),
            (("global_tribes_estate_power", "0.03"),),
            (("global_clergy_estate_power", "0.03"),),
        ),
        "P8.7;P11;P13;HE-HILLFORT;NMI-IRON-AGE", "contested",
        "Separates gameplay choices from later insular law tracts and from claims of a uniform druidic state.",
    ),
    Profile(
        "arabian", "Arabian Route-and-Oasis", ("Arabia",), (),
        "Royal Caravan Court", "Oasis Council", "Tribal Compact",
        ("crown_estate", "burghers_estate", "tribes_estate"),
        (
            (("global_crown_estate_power", "0.03"),),
            (("global_burghers_estate_power", "0.03"),),
            (("global_tribes_estate_power", "0.03"),),
        ),
        "P8.5;P11;P13;OCD;PLE", "contested",
        "Distinguishes caravan, oasis, tribal, and South Arabian court practices without backdating Islamic-era institutions.",
    ),
    Profile(
        "northern", "Northern Forest-and-River",
        ("Baltic", "Finland", "Eastern Europe", "Danube"), (),
        "Retinue Custody", "Hillfort Council", "Household Round",
        ("nobles_estate", "tribes_estate", "peasants_estate"),
        (
            (("global_nobles_estate_power", "0.02"),),
            (("global_tribes_estate_power", "0.03"),),
            (("global_pop_food_consumption", "-0.005"),),
        ),
        "P8.7;P11;P13;ENC-NEEU", "contested",
        "An archaeological gameplay frame for dispersed communities, not evidence for common ethnic states or written codes.",
    ),
    Profile(
        "african", "African Royal-and-Community", ("Africa", "West Africa"), (),
        "Royal Household", "Market-and-Sanctuary Council", "Community Compact",
        ("crown_estate", "burghers_estate", "tribes_estate"),
        (
            (("global_crown_estate_power", "0.03"),),
            (("global_burghers_estate_power", "0.03"),),
            (("global_tribes_estate_power", "0.03"),),
        ),
        "P8.5;P11;P13;CAH-XI", "contested",
        "Provides varied royal, urban, pastoral, and community choices without turning archaeological horizons into centralized states.",
    ),
    Profile(
        "eastern", "Eastern Maritime-and-Peninsular",
        ("Korea", "Japan", "Southeast Asia"), (),
        "Royal Storehouse", "Port-and-Lineage Council", "Settlement Compact",
        ("crown_estate", "nobles_estate", "burghers_estate"),
        (
            (("global_crown_estate_power", "0.03"),),
            (("global_nobles_estate_power", "0.03"),),
            (("global_burghers_estate_power", "0.03"),),
        ),
        "P8.3;P8.4;P11;P13;CAH-XI", "contested",
        "A low-resolution regional floor that avoids projecting later centralized Japanese, Korean, or Southeast Asian systems into AD 1.",
    ),
    Profile(
        "transoceanic", "American-and-Oceanian Community",
        ("Andes", "Northern Andes", "Mesoamerica", "North America",
         "Caribbean-Amazon", "Oceania"), (),
        "Ritual Center", "Lineage Council", "Household Community",
        ("clergy_estate", "tribes_estate", "peasants_estate"),
        (
            (("global_clergy_estate_power", "0.03"),),
            (("global_tribes_estate_power", "0.03"),),
            (("global_peasants_estate_power", "0.03"),),
        ),
        "P8.8;P11;P13", "contested",
        "Uses broad archaeological institutions only where evidence permits and does not invent written constitutions or unified macro-polities.",
    ),
)


@dataclass(frozen=True)
class Theme:
    key: str
    title: str
    category: str
    question: str
    labels: tuple[str, str, str]
    descriptions: tuple[str, str, str]
    effects: tuple[tuple[tuple[str, str], ...], ...]
    preferences: tuple[tuple[str, ...], ...]


THEMES = (
    Theme(
        "status", "Status and Incorporation", "socioeconomic",
        "who receives protected public standing and how outsiders enter it",
        ("Status Register", "Graduated Standing", "Local Admission"),
        (
            "A central register defines protected status efficiently but concentrates political authority.",
            "Recognized communities mediate several grades of status, trading speed for accommodation.",
            "Local bodies admit households flexibly, easing friction while weakening uniform administration.",
        ),
        (
            (("global_integration_speed_modifier", "0.06"), ("global_pop_assimilation_speed_modifier", "0.01")),
            (("global_integration_speed_modifier", "0.03"), ("pop_join_rebel_threshold", "-0.01")),
            (("global_pop_assimilation_speed_modifier", "0.025"), ("global_monthly_control", "-0.01")),
        ),
        (("crown_estate",), ("nobles_estate", "burghers_estate"), ("peasants_estate", "tribes_estate")),
    ),
    Theme(
        "dependent_labor", "Dependent Labor and Manumission", "socioeconomic",
        "the obligations, sale, protection, and release of dependent laborers",
        ("Recorded Obligations", "Protected Manumission", "Household Dependence"),
        (
            "Officials record dependent obligations and taxable releases, improving oversight at social cost.",
            "Protected routes to release improve incorporation while reducing elite extraction.",
            "Households regulate dependency locally, lowering provisioning burdens but entrenching private power.",
        ),
        (
            (("peasants_estate_max_tax", "0.03"), ("pop_join_rebel_threshold", "0.01")),
            (("global_pop_assimilation_speed_modifier", "0.02"), ("nobles_estate_max_tax", "-0.02")),
            (("global_pop_food_consumption", "-0.01"), ("peasants_estate_max_tax", "0.02")),
        ),
        (("crown_estate", "nobles_estate"), ("peasants_estate", "burghers_estate"), ("nobles_estate", "tribes_estate")),
    ),
    Theme(
        "revenue", "Revenue and Assessment", "administrative",
        "how communities are assessed and how public obligations are collected",
        ("Assessed Registers", "Negotiated Quotas", "In-Kind Contributions"),
        (
            "Regular assessment improves extraction and control but enlarges the central administrative burden.",
            "Councils bargain fixed contributions, supporting legitimacy at the expense of maximum revenue.",
            "Communities meet obligations in kind, sustaining production while leaving more local discretion.",
        ),
        (
            (("peasants_estate_max_tax", "0.04"), ("global_monthly_control", "0.015")),
            (("burghers_estate_max_tax", "0.025"), ("stability_cost_efficiency", "0.025")),
            (("global_production_efficiency", "0.025"), ("monthly_towards_decentralization", "societal_value_minor_monthly_move")),
        ),
        (("crown_estate",), ("burghers_estate", "nobles_estate"), ("peasants_estate", "tribes_estate")),
    ),
    Theme(
        "land", "Land Tenure and Agrarian Duty", "socioeconomic",
        "access to land, agrarian dues, and collective maintenance",
        ("Surveyed Allotments", "Estate Stewardship", "Communal Tenure"),
        (
            "Surveyed allotments support control and predictable dues but privilege central claims.",
            "Leading estates organize cultivation efficiently while increasing aristocratic leverage.",
            "Communal tenure protects subsistence and local resilience while limiting direct control.",
        ),
        (
            (("global_max_rural_control", "0.03"), ("global_monthly_control", "0.01")),
            (("global_monthly_food_modifier", "0.025"), ("global_nobles_estate_power", "0.04")),
            (("global_pop_food_consumption", "-0.01"), ("global_max_rural_control", "-0.02")),
        ),
        (("crown_estate",), ("nobles_estate",), ("peasants_estate", "tribes_estate")),
    ),
    Theme(
        "muster", "Military Service and Muster", "military",
        "who serves, for how long, and through which public or household obligation",
        ("Registered Service", "Retinue Service", "Community Muster"),
        (
            "Registered service raises dependable forces but increases administrative and social pressure.",
            "Elite retinues improve cohesion and morale while narrowing the military base.",
            "A broad seasonal muster supplies numbers quickly but sacrifices some battlefield efficiency.",
        ),
        (
            (("global_levy_size_modifier", "0.075"), ("global_levy_recruitment_speed_modifier", "-0.05")),
            (("land_morale_modifier", "0.02"), ("global_levy_size_modifier", "-0.025")),
            (("global_levy_recruitment_speed_modifier", "0.10"), ("levy_combat_efficiency_modifier", "-0.04")),
        ),
        (("crown_estate",), ("nobles_estate",), ("peasants_estate", "tribes_estate")),
    ),
    Theme(
        "local_rule", "Local and Provincial Rule", "administrative",
        "the balance among central officers, intermediary councils, and local communities",
        ("Appointed Officers", "Mediated Councils", "Local Custody"),
        (
            "Appointed officers improve coordination and control but strengthen the center.",
            "Intermediary councils improve cabinet throughput while preserving negotiated authority.",
            "Local custody lowers resistance and administrative reach together.",
        ),
        (
            (("country_cabinet_efficiency", "0.04"), ("global_monthly_control", "0.015")),
            (("legislative_efficiency", "0.04"), ("stability_cost_efficiency", "0.02")),
            (("pop_join_rebel_threshold", "-0.02"), ("global_max_rural_control", "-0.025")),
        ),
        (("crown_estate",), ("nobles_estate", "burghers_estate"), ("peasants_estate", "tribes_estate")),
    ),
    Theme(
        "cult", "Public Cult and Ritual Custody", "religious",
        "who maintains public rites, sanctuaries, vows, and tolerated local observances",
        ("Public Rite", "Collegiate Custody", "Local Observance"),
        (
            "The central authority sponsors public rites, strengthening religious administration but narrowing plural practice.",
            "Recognized colleges and sanctuaries share ritual custody and stabilize elite bargains.",
            "Local observance broadens toleration while reducing the reach of an official cult.",
        ),
        (
            (("global_pop_conversion_speed_modifier", "0.08"), ("tolerance_heathen", "-1")),
            (("clergy_estate_target_satisfaction", "small_permanent_target_satisfaction"), ("stability_cost_efficiency", "0.02")),
            (("tolerance_heathen", "1"), ("global_pop_conversion_speed_modifier", "-0.05")),
        ),
        (("crown_estate", "clergy_estate"), ("clergy_estate", "nobles_estate"), ("tribes_estate", "peasants_estate")),
    ),
    Theme(
        "household", "Household and Inheritance", "socioeconomic",
        "household succession, guardianship, property transmission, and kin obligation",
        ("Recorded Succession", "Lineage Arbitration", "Household Custom"),
        (
            "Recorded succession eases state integration but places family affairs under official scrutiny.",
            "Lineages arbitrate inheritance disputes, preserving elite consent at a cost to central uniformity.",
            "Household custom protects local practice and mobility while weakening predictable assessment.",
        ),
        (
            (("global_integration_speed_modifier", "0.035"), ("monthly_towards_centralization", "societal_value_minor_monthly_move")),
            (("nobles_estate_target_satisfaction", "tiny_permanent_target_satisfaction"), ("global_monthly_control", "-0.005")),
            (("global_pop_assimilation_speed_modifier", "0.01"), ("peasants_estate_max_tax", "-0.015")),
        ),
        (("crown_estate",), ("nobles_estate", "tribes_estate"), ("peasants_estate",)),
    ),
    Theme(
        "commerce", "Commerce and Market Conduct", "socioeconomic",
        "safe conduct, tolls, market oversight, and the standing of merchants",
        ("Public Toll Schedule", "Merchant Arbitration", "Open Local Exchange"),
        (
            "Published toll schedules improve route revenue and enforcement but privilege official channels.",
            "Merchant arbitration improves production and exchange while increasing urban political weight.",
            "Open local exchange reduces barriers and strengthens communities at the expense of central receipts.",
        ),
        (
            (("global_trade_through_owned_territory_efficiency", "0.06"), ("global_monthly_control", "0.01")),
            (("global_production_efficiency", "0.03"), ("global_burghers_estate_power", "0.04")),
            (("global_trade_through_owned_territory_efficiency", "0.03"), ("burghers_estate_max_tax", "-0.02")),
        ),
        (("crown_estate",), ("burghers_estate",), ("peasants_estate", "tribes_estate")),
    ),
    Theme(
        "coinage", "Coinage and Standards", "socioeconomic",
        "mint authority, accepted standards, weighed media, and seigniorage",
        ("Official Standard", "Multiple Civic Issues", "Weighed Exchange"),
        (
            "An official standard increases mint receipts but makes price stability depend on central restraint.",
            "Several recognized issues support commerce while sharing monetary authority with urban elites.",
            "Weighed and customary exchange is flexible but yields less direct mint revenue.",
        ),
        (
            (("minting_income_factor", "0.10"), ("minting_inflation_threshold", "-0.01")),
            (("minting_income_factor", "0.06"), ("global_burghers_estate_power", "0.04")),
            (("minting_income_factor", "0.025"), ("stability_cost_efficiency", "0.02")),
        ),
        (("crown_estate",), ("burghers_estate",), ("tribes_estate", "peasants_estate")),
    ),
    Theme(
        "courts", "Courts and Petition", "administrative",
        "the hearing of disputes, appeals, testimony, and petitions",
        ("Central Appeal", "Collegiate Judgment", "Local Composition"),
        (
            "A central appeal improves consistency and state control but increases administrative load.",
            "Collegiate judgment balances elite interests and lowers the political cost of legislation.",
            "Local composition resolves disputes accessibly while limiting uniform precedent.",
        ),
        (
            (("legislative_efficiency", "0.04"), ("country_cabinet_efficiency", "-0.015")),
            (("stability_cost_efficiency", "0.035"), ("global_nobles_estate_power", "0.025")),
            (("pop_join_rebel_threshold", "-0.015"), ("global_monthly_control", "-0.01")),
        ),
        (("crown_estate",), ("nobles_estate", "clergy_estate"), ("peasants_estate", "tribes_estate")),
    ),
    Theme(
        "offices", "Offices and Appointment", "administrative",
        "appointment, tenure, replacement, and accountability in public office",
        ("Direct Appointment", "Rotating Office", "Patron-Nominated Office"),
        (
            "Direct appointment makes staffing faster but concentrates office in the ruler's hands.",
            "Rotation broadens access and improves deliberation while making replacement less predictable.",
            "Patron nomination secures elite cooperation but makes office-holders costly to dislodge.",
        ),
        (
            (("set_cabinet_member_cost_modifier", "-0.10"), ("global_crown_estate_power", "0.04")),
            (("country_cabinet_efficiency", "0.03"), ("replace_cabinet_member_cost_modifier", "-0.05")),
            (("replace_cabinet_member_cost_modifier", "0.15"), ("global_nobles_estate_power", "0.04")),
        ),
        (("crown_estate",), ("burghers_estate", "tribes_estate"), ("nobles_estate",)),
    ),
    Theme(
        "migration", "Migration and Settlement", "administrative",
        "the admission, relocation, patronage, and settlement of mobile households",
        ("Directed Settlement", "Sponsored Communities", "Negotiated Passage"),
        (
            "Directed settlement accelerates incorporation and control but privileges central priorities.",
            "Recognized communities sponsor newcomers, balancing integration with corporate autonomy.",
            "Negotiated passage reduces cultural friction while leaving migration weakly supervised.",
        ),
        (
            (("global_pop_assimilation_speed_modifier", "0.02"), ("global_monthly_control", "0.01")),
            (("global_integration_speed_modifier", "0.025"), ("global_burghers_estate_power", "0.025")),
            (("tolerance_heathen", "1"), ("global_pop_assimilation_speed_modifier", "-0.01")),
        ),
        (("crown_estate",), ("burghers_estate", "tribes_estate"), ("peasants_estate", "tribes_estate")),
    ),
    Theme(
        "external", "Envoys, Clients, and External Compacts", "administrative",
        "envoys, tributary obligations, client rulers, hostages, and negotiated peace",
        ("Central Envoys", "Client Mediation", "Reciprocal Compacts"),
        (
            "Central envoys improve diplomatic standing but demand sustained court resources.",
            "Client mediation strengthens subordinate loyalty while empowering intermediary rulers.",
            "Reciprocal compacts broaden diplomatic capacity but bind the center to negotiated obligations.",
        ),
        (
            (("diplomatic_reputation", "1"), ("country_cabinet_efficiency", "-0.01")),
            (("subject_loyalty", "5"), ("global_nobles_estate_power", "0.03")),
            (("diplomatic_capacity_modifier", "0.05"), ("monthly_towards_outward", "societal_value_minor_monthly_move")),
        ),
        (("crown_estate",), ("nobles_estate", "tribes_estate"), ("burghers_estate", "tribes_estate")),
    ),
)

STANCE_KEYS = ("central", "mediated", "local")


def read_roster() -> list[dict[str, str]]:
    with ROSTER.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def tag_profiles() -> dict[str, str]:
    rows = read_roster()
    assigned: dict[str, str] = {}
    for row in rows:
        matches = [
            profile.key
            for profile in PROFILES
            if row["tag"] in profile.exact_tags or row["region"] in profile.regions
        ]
        if len(matches) != 1:
            raise ValueError(
                f"{row['tag']} ({row['region']}) must resolve exactly one law profile; "
                f"found {matches}"
            )
        assigned[row["tag"]] = matches[0]
    return assigned


def law_key(profile: str, theme: str) -> str:
    return f"antq_s2_{profile}_{theme}_law"


def option_key(profile: str, theme: str, stance: str) -> str:
    return f"antq_s2_{profile}_{theme}_{stance}"


def profile_by_key() -> dict[str, Profile]:
    return {profile.key: profile for profile in PROFILES}


def starting_laws_by_tag() -> dict[str, tuple[tuple[str, str], ...]]:
    profiles = profile_by_key()
    return {
        tag: tuple(
            (
                law_key(profile_key, theme.key),
                option_key(profile_key, theme.key, profiles[profile_key].starting_stance),
            )
            for theme in THEMES
        )
        for tag, profile_key in tag_profiles().items()
    }


def profile_law_pairs() -> tuple[tuple[str, str, str], ...]:
    return tuple(
        (profile.key, law_key(profile.key, theme.key), theme.key)
        for profile in PROFILES
        for theme in THEMES
    )


def all_law_options() -> set[tuple[str, str]]:
    return {
        (law_key(profile.key, theme.key), option_key(profile.key, theme.key, stance))
        for profile in PROFILES
        for theme in THEMES
        for stance in STANCE_KEYS
    }


def profile_power_modifier(profile: Profile, stance_index: int) -> tuple[str, str]:
    estate = profile.estates[stance_index]
    return (f"global_{estate.removesuffix('_estate')}_estate_power", "0.02")


def option_effects(
    profile: Profile, theme: Theme, stance_index: int
) -> tuple[tuple[str, str], ...]:
    effects = list(theme.effects[stance_index])
    effects.extend(profile.extra_effects[stance_index])
    power = profile_power_modifier(profile, stance_index)
    if power not in effects:
        effects.append(power)
    return tuple(effects)


def render_laws() -> str:
    lines = [
        "# Generated by tools/s2_ancient_laws.py --write.",
        "# Thirteen profile-gated AD 1 legal systems; 14 questions and 3 policies each.",
    ]
    for profile in PROFILES:
        for theme in THEMES:
            lines.extend((
                "",
                f"{law_key(profile.key, theme.key)} = {{",
                f"\tlaw_category = {theme.category}",
                "\tpotential = {",
                f"\t\tantq_law_profile_{profile.key}_trigger = yes",
                "\t}",
            ))
            for stance_index, stance in enumerate(STANCE_KEYS):
                lines.extend((
                    f"\t{option_key(profile.key, theme.key, stance)} = {{",
                    "\t\tcountry_modifier = {",
                ))
                lines.extend(
                    f"\t\t\t{modifier} = {value}"
                    for modifier, value in option_effects(profile, theme, stance_index)
                )
                lines.extend(("\t\t}", "\t\tyears = 2", "\t\testate_preferences = {"))
                preferences = tuple(dict.fromkeys(
                    (*theme.preferences[stance_index], profile.estates[stance_index])
                ))
                lines.extend(f"\t\t\t{estate}" for estate in preferences)
                lines.extend(("\t\t}", "\t}"))
            lines.append("}")
    return "\n".join(lines) + "\n"


def render_triggers() -> str:
    tag_map = {
        row["design_tag"]: row["engine_tag"]
        for row in json.loads(TAG_MAP.read_text(encoding="utf-8"))["entries"]
    }
    assignments = tag_profiles()
    lines = [
        "# Generated by tools/s2_ancient_laws.py --write.",
        "# Country-scope profile triggers use collision-safe engine tags.",
    ]
    for profile in PROFILES:
        tags = sorted(tag_map[tag] for tag, key in assignments.items() if key == profile.key)
        lines.extend(("", f"antq_law_profile_{profile.key}_trigger = {{", "\tOR = {"))
        lines.extend(f"\t\thas_or_had_tag = {tag}" for tag in tags)
        lines.extend(("\t}", "}"))
    return "\n".join(lines) + "\n"


def profile_ledger() -> str:
    assignments = tag_profiles()
    profiles = profile_by_key()
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow((
        "tag", "region", "profile", "profile_name", "starting_laws",
        "source", "confidence", "boundary",
    ))
    for row in read_roster():
        profile = profiles[assignments[row["tag"]]]
        writer.writerow((
            row["tag"], row["region"], profile.key, profile.name, len(THEMES),
            profile.source, profile.confidence, profile.boundary,
        ))
    return output.getvalue()


def option_ledger() -> str:
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow((
        "profile", "law", "theme", "category", "law_name", "law_description",
        "option", "stance", "option_name", "option_description", "modifiers",
        "estate_preferences", "starting", "source", "confidence", "boundary",
    ))
    for profile in PROFILES:
        for theme in THEMES:
            for stance_index, stance in enumerate(STANCE_KEYS):
                preferences = tuple(dict.fromkeys(
                    (*theme.preferences[stance_index], profile.estates[stance_index])
                ))
                writer.writerow((
                    profile.key,
                    law_key(profile.key, theme.key),
                    theme.key,
                    theme.category,
                    f"{profile.name} {theme.title}",
                    f"Defines {theme.question} within the {profile.name} political sphere.",
                    option_key(profile.key, theme.key, stance),
                    stance,
                    f"{getattr(profile, stance)} {theme.labels[stance_index]}",
                    theme.descriptions[stance_index],
                    "|".join(f"{key}={value}" for key, value in option_effects(
                        profile, theme, stance_index
                    )),
                    "|".join(preferences),
                    "yes" if stance == profile.starting_stance else "no",
                    profile.source,
                    profile.confidence,
                    profile.boundary,
                ))
    return output.getvalue()


def localization(language: str) -> str:
    rows: list[tuple[str, str]] = []
    for profile in PROFILES:
        for theme in THEMES:
            key = law_key(profile.key, theme.key)
            rows.extend((
                (key, f"{profile.name} {theme.title}"),
                (f"{key}_desc", f"Defines {theme.question} within the {profile.name} political sphere."),
            ))
            for stance_index, stance in enumerate(STANCE_KEYS):
                option = option_key(profile.key, theme.key, stance)
                rows.extend((
                    (option, f"{getattr(profile, stance)} {theme.labels[stance_index]}"),
                    (f"{option}_desc", theme.descriptions[stance_index]),
                ))
    lines = [f"l_{language}:"]
    lines.extend(f' {key}: "{value}"' for key, value in rows)
    return "\n".join(lines) + "\n"


def outputs() -> dict[Path, str]:
    result = {
        LAW_OUTPUT: render_laws(),
        TRIGGER_OUTPUT: render_triggers(),
        PROFILE_LEDGER: profile_ledger(),
        OPTION_LEDGER: option_ledger(),
    }
    for language in ("english", *M2_MIRROR_LANGUAGES):
        result[LOC_ROOT / language / f"antq_s2_laws_l_{language}.yml"] = localization(language)
    return result


def validate_content() -> None:
    failures: list[str] = []
    assignments = tag_profiles()
    if len(PROFILES) != 13 or len(THEMES) != 14:
        failures.append("legal layer must contain 13 profiles and 14 themes")
    if len(assignments) != 292:
        failures.append(f"legal profiles must cover 292 tags; found {len(assignments)}")
    if len(profile_law_pairs()) != 182 or len(all_law_options()) != 546:
        failures.append("legal breadth must be 182 groups and 546 options")
    if {theme.category for theme in THEMES} - LAW_CATEGORIES:
        failures.append("unsupported legal category")
    for profile in PROFILES:
        if profile.confidence not in {"secure", "contested"} or not profile.source:
            failures.append(f"profile {profile.key} lacks source/confidence")
        packages: set[tuple[tuple[str, str], ...]] = set()
        for theme in THEMES:
            for stance_index in range(3):
                effects = option_effects(profile, theme, stance_index)
                packages.add(effects)
                if len(effects) < 3:
                    failures.append(
                        f"{profile.key}/{theme.key}/{STANCE_KEYS[stance_index]} "
                        "needs at least three effects"
                    )
                for modifier, _value in effects:
                    if modifier not in ALLOWED_MODIFIERS:
                        failures.append(
                            f"{profile.key}/{theme.key} uses unverified modifier {modifier}"
                        )
                preferences = (*theme.preferences[stance_index], profile.estates[stance_index])
                if set(preferences) - ESTATES:
                    failures.append(f"{profile.key}/{theme.key} uses unknown estate")
        if len(packages) != 42:
            failures.append(f"profile {profile.key} contains duplicate policy effect packages")
    text = render_laws().lower()
    for word in FORBIDDEN:
        if f" {word}" in text:
            failures.append(f"generated law definition contains prohibited term {word}")
    for path, expected in outputs().items():
        if not path.is_file():
            failures.append(f"missing generated law artifact {path.relative_to(ROOT)}")
            continue
        encoding = (
            "utf-8-sig"
            if path.suffix == ".yml" or path in {LAW_OUTPUT, TRIGGER_OUTPUT}
            else "utf-8"
        )
        if path.read_text(encoding=encoding) != expected:
            failures.append(f"stale generated law artifact {path.relative_to(ROOT)}")
    if failures:
        raise ValueError("\n".join(failures))
    counts: dict[str, int] = {}
    for profile in assignments.values():
        counts[profile] = counts.get(profile, 0) + 1
    print(
        "s2_ancient_laws: PASS "
        f"({len(PROFILES)} profiles; {len(assignments)} tags; "
        f"{len(profile_law_pairs())} law groups; {len(all_law_options())} options; "
        f"42 distinct packages/profile; distribution "
        + ", ".join(f"{key}={counts[key]}" for key in sorted(counts))
        + ")"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        for path, text in outputs().items():
            path.parent.mkdir(parents=True, exist_ok=True)
            encoding = (
                "utf-8-sig"
                if path.suffix == ".yml" or path in {LAW_OUTPUT, TRIGGER_OUTPUT}
                else "utf-8"
            )
            path.write_text(text, encoding=encoding, newline="\n")
    validate_content()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
