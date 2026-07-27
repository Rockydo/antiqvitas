#!/usr/bin/env python3
"""Render and audit the first deep ancient council/cabinet replacement."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from dates import M2_MIRROR_LANGUAGES
from dds import identify

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "assets_queue/politics/sources"
MASTERS = ROOT / "assets_queue/politics/masters"
DDS_TOOL = ROOT / "tools/dds.py"
TYPE_OUT = ROOT / "in_game/common/parliament_types/00_antiquitas_s2.txt"
CABINET_OUT = ROOT / "in_game/common/cabinet_actions/00_antiquitas_s2.txt"
ISSUE_OUT = ROOT / "in_game/common/parliament_issues/00_antiquitas_s2.txt"
AGENDA_OUT = ROOT / "in_game/common/parliament_agendas/00_antiquitas_s2.txt"
MODIFIER_OUT = ROOT / "main_menu/common/static_modifiers/antq_s2_politics.txt"
CONTENT_LEDGER = ROOT / "docs/m6/ancient_politics_content.csv"
ART_LEDGER = ROOT / "docs/m6/ancient_politics_art.csv"


@dataclass(frozen=True)
class Action:
    slug: str
    name: str
    description: str
    ability: str
    modifiers: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class Motion:
    slug: str
    issue_name: str
    issue_description: str
    agenda_name: str
    agenda_description: str
    estate: str
    outcome: tuple[tuple[str, str], ...]
    concession: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class Profile:
    slug: str
    parliament: str
    name: str
    description: str
    reforms: tuple[str, ...]
    estates: tuple[str, ...]
    source_file: str
    source_hash: str
    source: str
    confidence: str
    note: str
    actions: tuple[Action, ...]
    motions: tuple[Motion, ...]


ADMIN = (("country_cabinet_efficiency", "0.025"), ("global_monthly_control", "0.0025"))
CONTROL = (("monthly_towards_centralization", "societal_value_minor_monthly_move"), ("country_cabinet_efficiency", "0.02"))
FOOD = (("global_pop_food_consumption", "-0.01"), ("global_production_efficiency", "0.025"))
TRADE = (("global_trade_through_owned_territory_efficiency", "0.05"), ("global_burghers_estate_power", "0.025"))
MIL = (("global_levy_size_modifier", "0.05"), ("land_morale_modifier", "0.01"))
LOGISTICS = (("global_supply_limit_modifier", "0.05"), ("global_road_building_time", "-0.05"))
PRESTIGE = (("monthly_prestige", "0.05"), ("country_cabinet_efficiency", "0.02"))
NOBLES = (("global_nobles_estate_power", "0.025"), ("land_morale_modifier", "0.01"))
CLERGY = (("global_clergy_estate_power", "0.025"), ("country_cabinet_efficiency", "0.02"))
TRIBES = (("global_tribes_estate_power", "0.025"), ("global_levy_size_modifier", "0.04"))
PEASANTS = (("global_pop_food_consumption", "-0.01"), ("global_levy_size_modifier", "0.03"))


def a(slug: str, name: str, desc: str, ability: str, mods: tuple[tuple[str, str], ...]) -> Action:
    return Action(slug, name, desc, ability, mods)


def m(
    slug: str, issue: str, issue_desc: str, agenda: str, agenda_desc: str,
    estate: str, outcome: tuple[tuple[str, str], ...], concession: tuple[tuple[str, str], ...],
) -> Motion:
    return Motion(slug, issue, issue_desc, agenda, agenda_desc, estate, outcome, concession)


PROFILES = (
    Profile(
        "roman", "antq_roman_senate", "Roman Senate",
        "The Senate remains the Principate's principal arena for elite deliberation, provincial scrutiny, honors, finance, and the public language of the res publica.",
        ("antq_principate", "antq_dominate"), ("nobles_estate", "burghers_estate", "clergy_estate"),
        "roman_principate_atlas.png", "1e990edda4ce5fbba251e79738731b1141090ab6d69111895354474c00497f36",
        "P8.1;P11;P13;OCD", "secure",
        "Engine estates represent senators, equestrian contractors, and public priestly colleges; this does not turn the Augustan Senate into a sovereign legislature.",
        (
            a("census_rolls", "Census Rolls", "Coordinate citizen, property, and status returns through censoria potestas and provincial reporting.", "adm", ADMIN),
            a("provincial_dispatches", "Provincial Dispatches", "Collate governors' reports, petitions, and senatorial commissions before decisions reach the princeps.", "dip", CONTROL),
            a("aerarium_accounts", "Aerarium Accounts", "Reconcile public receipts, contracts, and coin reserves without pretending that imperial and senatorial finances were one office.", "adm", TRADE),
            a("grain_contracts", "Annona Contracts", "Supervise measures, shippers, storage obligations, and the politically vital grain supply.", "dip", FOOD),
            a("legionary_rosters", "Legionary Rosters", "Maintain discharge, donative, veteran, and replacement records for the standing legions.", "mil", MIL),
        ),
        (
            m("census_review", "Provincial Census Review", "Debate a coordinated review of provincial declarations, civic status, and assessed obligations.", "Senatorial Provincial Scrutiny", "Senatorial houses demand a formal commission before provincial assessments are revised.", "nobles_estate", ADMIN, NOBLES),
            m("annona_commission", "Annona Contract Commission", "Authorize scrutiny of grain measures, storage losses, and shipping contracts.", "Equestrian Contract Petition", "Equestrian contractors seek predictable terms and protected performance of public supply contracts.", "burghers_estate", FOOD, TRADE),
            m("legionary_settlement", "Legionary Settlement Act", "Settle discharge grants and veteran obligations without stripping frontier commands of replacements.", "Priestly Calendar Petition", "The public colleges ask that musters, vows, and games respect the authorized civic calendar.", "clergy_estate", MIL, CLERGY),
        ),
    ),
    Profile(
        "han", "antq_han_court_conference", "Han Court Conference",
        "Imperial conferences reconcile memorials, commandery returns, fiscal registers, and the competing claims of palace, affinal, and scholarly officeholders.",
        ("antq_han_imperial_bureaucracy",), ("nobles_estate", "burghers_estate", "peasants_estate"),
        "han_court_atlas.png", "7d57f4dcc204afa0670c412fe1a649b257c6dcacd80dcf04d16216b6dede3380",
        "P8.3;P13;BHR;CTP-WM", "secure",
        "The three participating estates are technical proxies for court lineages, salaried administrators and registered cultivator households.",
        (
            a("commandery_reports", "Commandery Reports", "Collate population, justice, harvest, and revenue returns from commanderies and kingdoms.", "adm", ADMIN),
            a("imperial_secretariat", "Imperial Secretariat", "Order memorials, draft replies, authenticate tallies, and prevent contradictory palace instructions.", "dip", CONTROL),
            a("granary_registers", "Granary Registers", "Compare receipts, spoilage, release orders, and local price pressures across official stores.", "adm", FOOD),
            a("courier_relays", "Courier Relays", "Maintain tallies, relay horses, sealed document tubes, and the roads between reporting stations.", "dip", LOGISTICS),
            a("frontier_command", "Frontier Command Returns", "Synchronize beacon reports, garrison strength, remount needs, and crossbow stores.", "mil", MIL),
        ),
        (
            m("commandery_audit", "Commandery Audit Cycle", "Dispatch a bounded audit of household registers, judgments, and remittances.", "Court Lineage Appointment Memorial", "Powerful court lineages press for candidates whose obligations and competence the throne can verify.", "nobles_estate", ADMIN, NOBLES),
            m("granary_allocation", "Granary Allocation Conference", "Balance local reserves against transport loss, relief, and frontier demand.", "Clerks' Register Petition", "Administrative households request stable appointments and adequate staff for the expanding register burden.", "burghers_estate", FOOD, ADMIN),
            m("frontier_dispatch", "Frontier Garrison Dispatch", "Set remount, beacon, and stores priorities for the northern commands.", "Cultivator Corvée Relief", "Registered households petition for predictable labor rotations during the agricultural season.", "peasants_estate", MIL, PEASANTS),
        ),
    ),
    Profile(
        "iranian", "antq_iranian_great_council", "Iranian Great Council",
        "The king negotiates host service, regional authority, road security, and dynastic precedence with great houses and royal officers.",
        ("antq_parthian_king_of_kings", "antq_parthian_subkingdom", "antq_indo_scythian_kingship", "antq_sassanid_centralized_monarchy"),
        ("nobles_estate", "clergy_estate", "burghers_estate"),
        "iranian_council_atlas.png", "4986d7ce7a8951994a1fb9dd3679b7cd7e89425c442960c9ce411847942972c3",
        "P8.2;P13;CAH-XI;OCD", "secure",
        "This shared engine surface covers related Iranian court negotiations while preserving polity-specific laws and privileges.",
        (
            a("noble_host_musters", "Noble-Host Musters", "Record the mounted followings and equipment promised by royal and regional houses.", "mil", NOBLES),
            a("royal_road_couriers", "Royal-Road Couriers", "Protect relay mounts, sealed messages, and road stations between court and sub-kingdoms.", "dip", LOGISTICS),
            a("satrapal_accounts", "Regional Accounts", "Reconcile silver, gifts, levies, and retained local revenues without inventing uniform provinces.", "adm", ADMIN),
            a("caravan_protection", "Caravan Safe-Conducts", "Coordinate escorts, watering points, and compensation rules on long-distance routes.", "dip", TRADE),
            a("dynastic_arbitration", "Dynastic Arbitration", "Use hostages, oaths, marriages, and precedence rulings to contain disputes among houses.", "adm", PRESTIGE),
        ),
        (
            m("host_contribution", "Noble-Host Contribution", "Set the scale and season of great-house mounted service.", "Great-House Precedence Claim", "Leading houses demand that court precedence reflect service, lineage, and negotiated autonomy.", "nobles_estate", MIL, NOBLES),
            m("road_protection", "Royal-Road Protection", "Fund relays and escorts on routes binding the royal court to regional powers.", "Fire-Custodian Endowment", "Ritual custodians request secure revenues for court and local sacred observance.", "clergy_estate", LOGISTICS, CLERGY),
            m("silver_reckoning", "Satrapal Silver Reckoning", "Review retained revenue, royal gifts, and coin remittances without asserting a uniform tax code.", "Caravan Safe-Conduct Petition", "Merchant households seek enforceable passage and compensation after losses on protected roads.", "burghers_estate", ADMIN, TRADE),
        ),
    ),
    Profile(
        "civic", "antq_civic_assembly", "Civic Council",
        "A boule or comparable civic body manages accounts, magistracies, sanctuaries, harbor obligations, and the enrolled citizen body.",
        ("antq_indo_greek_kingship", "antq_settled_town_cluster"), ("burghers_estate", "nobles_estate", "peasants_estate"),
        "civic_assembly_atlas.png", "3a43c68d91f7436abfa49f1d703c284fcb192a400f5d317d083992826f90c158",
        "P8.4;P13;CAH-XI;OCD", "contested",
        "The civic surface is deliberately constitutional rather than ethnic and does not imply identical franchise rules in every city.",
        (
            a("civic_accounts", "Civic Accounts", "Publish magistrates' receipts, sanctuary funds, contracts, and arrears for council scrutiny.", "adm", ADMIN),
            a("harbor_dues", "Harbor Dues", "Standardize weights, amphora stamps, wharf charges, and exemptions for local commerce.", "dip", TRADE),
            a("citizen_muster", "Citizen Muster Roll", "Keep an enrolled civic levy and its equipment obligations current.", "mil", MIL),
            a("magistrate_rotations", "Magistrate Rotations", "Sequence offices, handovers, seals, and public accounting to limit administrative capture.", "adm", CONTROL),
            a("sanctuary_embassies", "Sanctuary Embassies", "Coordinate sacred envoys, interstate honors, and treaty deposits at recognized sanctuaries.", "dip", PRESTIGE),
        ),
        (
            m("harbor_revision", "Harbor Dues Revision", "Review weights, exemptions, and wharf obligations without choking exchange.", "Merchant Wharf Petition", "Exchange households request predictable dues and protection for civic storage space.", "burghers_estate", TRADE, TRADE),
            m("muster_roll", "Citizen Muster Roll", "Reconcile defense obligations with the enrolled citizen and resident population.", "Landed Council Rotation", "Leading landholders press to preserve an orderly rotation through high civic offices.", "nobles_estate", MIL, NOBLES),
            m("sanctuary_embassy", "Sanctuary Embassy", "Authorize gifts and delegates for a treaty, festival, or inter-city appeal.", "Smallholder Debt Arbitration", "Cultivating households ask the council to mediate obligations threatening the civic levy base.", "peasants_estate", PRESTIGE, PEASANTS),
        ),
    ),
    Profile(
        "gana", "antq_gana_assembly", "Gana Assembly",
        "Lineage delegates deliberate over arbitration, shared defense, hospitality, and common resources without a hereditary monarch.",
        ("antq_indian_ganasangha",), ("nobles_estate", "peasants_estate", "burghers_estate"),
        "gana_assembly_atlas.png", "6cc71845187d386edb2c22f9f580725b6f2af0190e42128f0228512ebee42608",
        "P8.4;P13;CAH-XI", "contested",
        "The mechanics are a conservative gana-sangha adapter and do not reconstruct one franchise or procedure for every polity.",
        (
            a("clan_delegates", "Clan Delegates", "Maintain recognized speaking order, delegate tokens, and witnessed assembly decisions.", "adm", ADMIN),
            a("assembly_arbitration", "Assembly Arbitration", "Resolve obligations between lineages before disputes fracture collective action.", "dip", PRESTIGE),
            a("confederate_muster", "Confederate Muster", "Count each participating lineage's equipment and seasonal service.", "mil", MIL),
            a("road_hospitality", "Road Hospitality", "Coordinate water, shelter, safe conduct, and reciprocal duties for travelers.", "dip", TRADE),
            a("communal_granaries", "Communal Granaries", "Audit shared measures, seed reserves, spoilage, and emergency distributions.", "adm", FOOD),
        ),
        (
            m("delegate_apportionment", "Clan Delegate Apportionment", "Reconcile recognized lineages and their speaking weight for the next assembly.", "Lineage Seniority Petition", "Senior lineages demand that precedence and witnessed obligations remain legible.", "nobles_estate", ADMIN, NOBLES),
            m("confederate_muster", "Confederate Muster", "Set the bounded campaign service owed by participating lineages.", "Cultivator Irrigation Claim", "Cultivating households request priority for shared water and seasonal labor.", "peasants_estate", MIL, PEASANTS),
            m("shared_granary", "Shared Granary Measure", "Set reserve, seed, and emergency distribution rules for common stores.", "Caravan Hospitality Duty", "Exchange households ask the assembly to enforce safe and reciprocal road hospitality.", "burghers_estate", FOOD, TRADE),
        ),
    ),
    Profile(
        "steppe", "antq_confederation_council", "Confederation Council",
        "Lineage leaders coordinate pasture circuits, left-right wings, gifts, envoys, and remounts around the chanyu's court.",
        ("antq_steppe_confederation",), ("tribes_estate", "nobles_estate", "burghers_estate"),
        "steppe_council_atlas.png", "e191587a1bf4a4fd5bdb77f2a2f0b9ef350d46fb709b20ac1e8a71c22ddb9a7b",
        "P8.3;P13;CAH-XI", "secure",
        "Terminology avoids projecting the later Mongol quriltai and decimal institutions onto AD 1 confederations.",
        (
            a("pasture_circuits", "Seasonal Pasture Circuits", "Coordinate negotiated access to winter, spring, summer, and autumn grazing.", "adm", FOOD),
            a("wing_musters", "Left-Right Wing Musters", "Count mounted followings and assign a campaign direction without inventing later decimal ranks.", "mil", MIL),
            a("gift_circulation", "Prestige-Gift Circulation", "Move silk, plaques, vessels, livestock, and honors through the confederate hierarchy.", "dip", PRESTIGE),
            a("envoy_circuits", "Envoy Circuits", "Maintain tallies, interpreters, escorts, and relay mounts for distant lineages.", "dip", LOGISTICS),
            a("remount_herds", "Remount Herd Registers", "Protect breeding stock and allocate fresh mounts to envoys and war leaders.", "mil", NOBLES),
        ),
        (
            m("pasture_circuit", "Seasonal Pasture Circuit", "Mediate grazing routes before scarcity turns lineage disputes violent.", "Herding-Household Pasture Claim", "Mobile households demand access consistent with seasonal need and prior compact.", "tribes_estate", FOOD, TRIBES),
            m("wing_muster", "Left-Right Wing Muster", "Set contributions and rendezvous points for a bounded confederate campaign.", "Lineage Gift Share", "Leading lineages demand a share of prestige goods proportionate to service and standing.", "nobles_estate", MIL, NOBLES),
            m("envoy_passage", "Envoy Safe Passage", "Guarantee relay access and protection for confederate and foreign envoys.", "Broker Safe-Conduct Petition", "Long-distance brokers seek compensation rules and escorts through contested pasture.", "burghers_estate", LOGISTICS, TRADE),
        ),
    ),
    Profile(
        "tribal", "antq_tribal_assembly", "Elders' Assembly",
        "Local leading kindreds, ritual custodians, and specialist households negotiate season, muster, exchange, and customary settlement.",
        ("antq_advanced_chiefdom", "antq_tribal_kingdom"), ("tribes_estate", "clergy_estate", "burghers_estate"),
        "tribal_assembly_atlas.png", "7ab5f2b0be3cdc70c17ae253ae7143d4fa87cf57792becd0be4c0a119753c1af",
        "P8.7;P13;CAH-XI", "contested",
        "A minimal engine adapter for varied early Iron Age assemblies; regional laws and privileges carry narrower archaeological claims.",
        (
            a("elder_moot", "Elder Moot", "Sequence speakers, witnesses, compensation claims, and collective obligations.", "adm", ADMIN),
            a("warband_gifts", "Warband Gifts", "Bind temporary followings through equipment, hospitality, and publicly remembered gifts.", "dip", PRESTIGE),
            a("grove_custody", "Sacred-Place Custody", "Maintain offerings, boundaries, and seasonal observance without inventing a central priesthood.", "adm", CLERGY),
            a("seasonal_muster", "Seasonal Muster", "Count shields, spears, provisions, and expected service for a limited campaign.", "mil", MIL),
            a("river_exchange", "River Exchange Peace", "Protect weights, ferries, guest-right, and specialist traffic at meeting places.", "dip", TRADE),
        ),
        (
            m("moot_calendar", "Assembly Calendar", "Set a season and place for witnessed settlement of collective disputes.", "Leading-Kindred Gift Claim", "Prominent kindreds seek recognized compensation for hosting and military service.", "tribes_estate", ADMIN, TRIBES),
            m("host_muster", "Seasonal Host Muster", "Agree a limited service obligation, rendezvous, and food burden.", "Sacred-Place Offering Petition", "Ritual custodians request labor and gifts for bounded local observance.", "clergy_estate", MIL, CLERGY),
            m("river_peace", "River-Market Peace", "Guarantee safe exchange at a seasonal river or track junction.", "Smithing-Household Exchange Right", "Specialist households seek protected movement of iron, amber, tools, and weights.", "burghers_estate", TRADE, TRADE),
        ),
    ),
    Profile(
        "sacral", "antq_sacral_court", "Sacral Court Council",
        "Royal, temple, scribal, and cultivating interests meet around stores, waterworks, ceremonial obligations, and frontier cult.",
        ("antq_lankan_kingdom", "antq_kushite_dual_kingship"), ("clergy_estate", "nobles_estate", "peasants_estate"),
        "sacral_court_atlas.png", "e3f2c652277ae4a140c20c8fe64f6381efae9c53e54fae6e89271f12d2cff1fb",
        "P8.4;P8.5;P11;P13;CAH-XI;PLE", "contested",
        "The shared interface models administrative conjunction, not a claim that Kushite and Lankan sacred kingship were institutionally identical.",
        (
            a("temple_storehouses", "Temple Storehouses", "Audit sealed jars, endowed land receipts, offerings, and emergency releases.", "adm", FOOD),
            a("royal_waterworks", "Royal Waterworks", "Coordinate survey, sluice labor, storage, and repair around ancient irrigation.", "adm", CONTROL),
            a("cult_processions", "Cult Processions", "Sequence regalia, offerings, routes, and hospitality for public royal rites.", "dip", PRESTIGE),
            a("scribal_accounts", "Scribal Accounts", "Reconcile weights, stores, grants, and labor through locally appropriate records.", "adm", ADMIN),
            a("frontier_offerings", "Frontier Offerings", "Support boundary sanctuaries and local compacts without asserting uniform doctrine.", "dip", CLERGY),
        ),
        (
            m("storehouse_audit", "Temple Storehouse Audit", "Review offerings, sealed reserves, and endowed receipts under royal protection.", "Priestly Offering Share", "Temple custodians request a stable share for ritual, hospitality, and maintenance.", "clergy_estate", FOOD, CLERGY),
            m("canal_labor", "Royal Canal Labor", "Set repair, survey, and sluice obligations around a bounded irrigation work.", "Court Waterworks Petition", "Leading households seek priority for channels sustaining royal centers and endowed land.", "nobles_estate", CONTROL, NOBLES),
            m("seed_reserve", "Cultivator Seed Reserve", "Protect seed and emergency stores before ceremonial or military requisition.", "Cultivator Labor Calendar", "Farming households request that corvée and ritual service respect the crop cycle.", "peasants_estate", FOOD, PEASANTS),
        ),
    ),
    Profile(
        "royal", "antq_royal_council", "Royal Council",
        "A client or regional court coordinates petitions, tribute, embassies, dynastic guarantees, and fortress supply.",
        ("antq_client_monarchy", "antq_buffer_kingdom", "antq_regional_kingship", "antq_early_korean_kingdom"),
        ("nobles_estate", "burghers_estate", "clergy_estate"),
        "royal_council_atlas.png", "fe3e1232bff8a306800f20c5151590d4df405dabfe36e14a7ea87a9d450324a3",
        "P8.1;P8.2;P8.3;P13;OCD;PLE", "contested",
        "This is a lower-claim court adapter; polity-specific laws, privileges, rulers, and subject relations retain the historical distinctions.",
        (
            a("palace_petitions", "Palace Petitions", "Register claims, witnesses, seals, and ordered replies before access becomes pure patronage.", "adm", ADMIN),
            a("tribute_registers", "Tribute Registers", "Track local contributions, retained shares, gifts, and remittances to an overlord.", "adm", TRADE),
            a("court_embassies", "Court Embassies", "Prepare gifts, interpreters, routes, and treaty copies for neighboring great powers.", "dip", PRESTIGE),
            a("dynastic_compacts", "Dynastic Compacts", "Record hostages, marriages, oaths, and succession guarantees without making them permanent peace.", "dip", CONTROL),
            a("fortress_provisioning", "Fortress Provisioning", "Balance grain, missiles, water, and garrison service at strategic strongholds.", "mil", LOGISTICS),
        ),
        (
            m("tribute_review", "Tribute Register Review", "Reconcile local obligations, court needs, and remittances owed beyond the kingdom.", "Retainer Garrison Petition", "Landed retainers seek clear service and provisioning obligations.", "nobles_estate", ADMIN, NOBLES),
            m("embassy_fund", "Embassy Reception Fund", "Authorize gifts and hospitality without exhausting the court treasury.", "Caravan Security Petition", "Merchant households ask the court to protect approaches, markets, and compensation claims.", "burghers_estate", PRESTIGE, TRADE),
            m("fortress_stores", "Fortress Provisioning Measure", "Set grain, water, missile, and labor reserves for exposed strongholds.", "Sanctuary Endowment Petition", "Cult custodians request protected stores and land for public rites and travelers.", "clergy_estate", LOGISTICS, CLERGY),
        ),
    ),
)

COUNCIL_DYNAMICS: dict[str, tuple[str, tuple[tuple[str, str], ...]]] = {
    "roman": (
        "0.10",
        (("nobles_estate", "0.25"), ("burghers_estate", "0.15"), ("clergy_estate", "0.05")),
    ),
    "han": (
        "0.15",
        (("nobles_estate", "0.10"), ("burghers_estate", "0.20"), ("peasants_estate", "-0.10")),
    ),
    "iranian": (
        "0.05",
        (("nobles_estate", "0.30"), ("clergy_estate", "0.10"), ("burghers_estate", "-0.05")),
    ),
    "civic": (
        "0.10",
        (("burghers_estate", "0.25"), ("nobles_estate", "0.10"), ("peasants_estate", "0.15")),
    ),
    "gana": (
        "0.15",
        (("nobles_estate", "0.20"), ("peasants_estate", "0.20"), ("burghers_estate", "0.05")),
    ),
    "steppe": (
        "0.05",
        (("tribes_estate", "0.35"), ("nobles_estate", "0.15"), ("burghers_estate", "-0.10")),
    ),
    "tribal": (
        "0.05",
        (("tribes_estate", "0.30"), ("clergy_estate", "0.15"), ("burghers_estate", "-0.10")),
    ),
    "sacral": (
        "0.10",
        (("clergy_estate", "0.30"), ("nobles_estate", "0.10"), ("peasants_estate", "0.05")),
    ),
    "royal": (
        "0.10",
        (("nobles_estate", "0.20"), ("burghers_estate", "0.05"), ("clergy_estate", "0.05")),
    ),
}


def q(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def reform_trigger(reforms: tuple[str, ...], indent: str = "\t\t") -> list[str]:
    lines = [f"{indent}OR = {{"]
    lines.extend(f"{indent}\thas_reform = government_reform:{key}" for key in reforms)
    lines.append(f"{indent}}}")
    return lines


def modifier_lines(modifiers: tuple[tuple[str, str], ...], indent: str) -> list[str]:
    return [f"{indent}{key} = {value}" for key, value in modifiers]


def parliament_types() -> str:
    lines = ["# Generated by tools/s2_ancient_politics.py --write.", "# Distinct ancient deliberative institutions; no medieval parliament adapter is reused."]
    for profile in PROFILES:
        lines.extend(("", f"{profile.parliament} = {{", "\ttype = country", "\tpotential = {"))
        lines.extend(reform_trigger(profile.reforms))
        lines.extend(("\t}", "\tallow = {"))
        lines.extend(reform_trigger(profile.reforms))
        lines.extend(("\t}", "\tmodifier = {", "\t\thas_a_parliamentary_system = yes"))
        lines.extend(f"\t\t{estate}_can_participate_in_parliament = yes" for estate in profile.estates)
        base_support, agenda_impacts = COUNCIL_DYNAMICS[profile.slug]
        lines.append(f"\t\tparliament_base_support = {base_support}")
        lines.extend(
            f"\t\t{estate}_agenda_impact = {impact}"
            for estate, impact in agenda_impacts
        )
        lines.extend(("\t}", "}"))
    return "\n".join(lines) + "\n"


def cabinet_actions() -> str:
    lines = ["# Generated by tools/s2_ancient_politics.py --write.", "# Forty-five profile-locked ancient administrative programmes."]
    for profile in PROFILES:
        for action in profile.actions:
            key = f"antq_{profile.slug}_{action.slug}"
            lines.extend(("", f"{key} = {{", f"\tability = {action.ability}", "\tpotential = {"))
            lines.extend(reform_trigger(profile.reforms))
            lines.extend(("\t}", "\tallow_multiple = no", "\tcountry_modifier = {"))
            lines.extend(modifier_lines(action.modifiers, "\t\t"))
            lines.extend(("\t}", "}"))
    return "\n".join(lines) + "\n"


def parliament_issues() -> str:
    lines = ["# Generated by tools/s2_ancient_politics.py --write.", "# Twenty-seven council debates with profile-specific outcomes."]
    for profile in PROFILES:
        for motion in profile.motions:
            key = f"antq_issue_{profile.slug}_{motion.slug}"
            modifier = f"{key}_outcome"
            lines.extend((
                "", f"{key} = {{", f"\testate = {motion.estate}",
                "\tmodifier_when_in_debate = {", "\t\tcountry_cabinet_efficiency = 0.01", "\t}",
                "\tallow = {", f"\t\tparliament_type = parliament_type:{profile.parliament}", "\t}",
                "\tchance = { add = 1 }", "\ton_debate_passed = {",
                f"\t\tadd_country_modifier = {{ modifier = {modifier} years = 10 mode = add_and_extend }}",
                "\t}", "\ton_debate_failed = { parliament_debate_failed_effect = yes }", "}",
            ))
    return "\n".join(lines) + "\n"


def parliament_agendas() -> str:
    lines = ["# Generated by tools/s2_ancient_politics.py --write.", "# Twenty-seven estate requests tied to actual ancient council profiles."]
    for profile in PROFILES:
        for motion in profile.motions:
            key = f"antq_agenda_{profile.slug}_{motion.slug}"
            modifier = f"{key}_concession"
            lines.extend((
                "", f"{key} = {{", "\ttype = country", f"\testate = {motion.estate}",
                "\timportance = 1.5", "\tpotential = {",
                f"\t\tparliament_type = parliament_type:{profile.parliament}", "\t}",
                "\ton_accept = {",
                f"\t\tadd_country_modifier = {{ modifier = {modifier} years = 5 mode = add_and_extend }}",
                "\t}", "\tchance = 10", "}",
            ))
    return "\n".join(lines) + "\n"


def static_modifiers() -> str:
    lines = ["# Generated by tools/s2_ancient_politics.py --write."]
    for profile in PROFILES:
        for motion in profile.motions:
            issue = f"antq_issue_{profile.slug}_{motion.slug}_outcome"
            agenda = f"antq_agenda_{profile.slug}_{motion.slug}_concession"
            lines.extend(("", f"{issue} = {{"))
            lines.extend(modifier_lines(motion.outcome, "\t"))
            lines.extend(("}", "", f"{agenda} = {{"))
            lines.extend(modifier_lines(motion.concession, "\t"))
            lines.append("}")
    return "\n".join(lines) + "\n"


def localization(language: str) -> str:
    lines = [f"l_{language}:"]
    for profile in PROFILES:
        lines.extend((
            f' {profile.parliament}: "{q(profile.name)}"',
            f' {profile.parliament}_desc: "{q(profile.description)}"',
        ))
        for action in profile.actions:
            key = f"antq_{profile.slug}_{action.slug}"
            lines.extend((
                f' {key}: "{q(action.name)}"',
                f' {key}_desc: "{q(action.description)}"',
                f' {key}_action: "{q(action.name)}"',
                f' {key}_active: "Administering {q(action.name)}"',
                f' {key}_action_progress: "In progress"',
                f' {key}_action_progress_wordier: "{q(action.name)}: in progress"',
                f' {key}_action_progress_long_wordier: "{q(action.name)}: administrative programme in progress"',
                f' {key}_action_progress_tooltip: "{q(action.description)}"',
            ))
        for motion in profile.motions:
            issue = f"antq_issue_{profile.slug}_{motion.slug}"
            agenda = f"antq_agenda_{profile.slug}_{motion.slug}"
            lines.extend((
                f' {issue}: "{q(motion.issue_name)}"',
                f' {issue}_desc: "{q(motion.issue_description)}"',
                f' {issue}_outcome: "{q(motion.issue_name)} Settlement"',
                f' {issue}_outcome_desc: "The council has enacted its reviewed settlement for a limited term."',
                f' {agenda}: "{q(motion.agenda_name)}"',
                f' {agenda}_desc: "{q(motion.agenda_description)}"',
                f' {agenda}_concession: "{q(motion.agenda_name)} Concession"',
                f" {agenda}_concession_desc: \"The court or council has accepted this interest group's bounded request.\"",
            ))
    return "\n".join(lines) + "\n"


def ui_localization(language: str) -> str:
    """Replace fixed medieval/early-modern government-panel chrome.

    The engine's tab labels cannot vary by parliament type, so these use
    deliberately neutral ancient terms.  The active institution itself keeps
    the profile-specific name rendered above.
    """
    entries = (
        ("game_concept_estate", "Social Order"),
        ("game_concept_estates", "Social Orders"),
        ("game_concept_parliament", "Council"),
        ("game_concept_parliament_desc", "A country's deliberative body brings recognized social orders, officeholders, or lineage delegates into a bounded session. Its exact name, participants, and issues depend on the active ancient government profile."),
        ("game_concept_parliament_seat", "Council Seat"),
        ("game_concept_parliament_type", "Council Type"),
        ("game_concept_parliament_types", "Council Types"),
        ("game_concept_parliament_agenda", "Council Agenda"),
        ("game_concept_parliament_agendas", "Council Agendas"),
        ("game_concept_parliament_issue", "Council Issue"),
        ("game_concept_parliament_issues", "Council Issues"),
        ("game_concept_parliament_support", "Council Support"),
        ("game_concept_cabinet", "State Offices"),
        ("game_concept_cabinet_desc", "The higher offices and trusted agents through which a country carries out administration, dispatches, stores, musters, accounts, and diplomacy."),
        ("game_concept_cabinet_member", "State Officer"),
        ("game_concept_cabinet_members", "State Officers"),
        ("game_concept_cabinet_action", "Administrative Programme"),
        ("game_concept_cabinet_actions", "Administrative Programmes"),
        ("game_concept_cabinet_seat", "State Office"),
        ("game_concept_cabinet_seats", "State Offices"),
        ("game_concept_cabinet_efficiency", "Administrative Efficiency"),
        ("SUBTAB_GOVERNMENT_ESTATES_TT_FLAVOR_TEXT", "\"No ruler governs without households, temples, soldiers, and towns.\""),
        ("SUBTAB_GOVERNMENT_PARLIAMENT", "Council"),
        ("SUBTAB_GOVERNMENT_PARLIAMENT_TT_TEXT", "This window convenes the recognized participants of our active ancient council and resolves its profile-specific issues and agendas."),
        ("SUBTAB_GOVERNMENT_PARLIAMENT_TT_FLAVOR_TEXT", "\"Counsel before action; account after office.\""),
        ("SUBTAB_GOVERNMENT_CABINET", "State Offices"),
        ("SUBTAB_GOVERNMENT_CABINET_TT_TEXT", "This window appoints characters to state offices and assigns the administrative programmes available to our government profile."),
        ("SUBTAB_GOVERNMENT_CABINET_TT_FLAVOR_TEXT", "\"Records, messengers, stores, and officers turn command into government.\""),
        ("call_parliament", "Convene the Council"),
        ("call_parliament_desc", "Convene our active council to deliberate on a historically bounded issue, negotiate participating orders' agendas, review a law, request contributions or a muster, or sanction a war."),
        ("request_more_taxes", "Request Emergency Contributions"),
        ("request_more_taxes_desc", "Ask the participating social orders to authorize exceptional contributions for a defined public need."),
        ("ask_for_larger_levies", "Request an Expanded Muster"),
        ("ask_for_larger_levies_desc", "Ask the participating social orders to provide a larger bounded military muster."),
        ("ask_for_law_changes", "Submit a Law for Review"),
        ("ask_for_law_changes_desc", "Submit a policy in the country's ancient law system for council review."),
        ("prepare_for_war", "Seek Council Sanction for War"),
        ("prepare_for_war_desc", "Ask the active council to recognize a public cause for war against an eligible neighboring or diplomatically reachable country."),
        ("force_parliament_issue", "Direct the Council's Debate"),
        ("force_parliament_issue_header", "Direct the Council's Debate"),
        ("PARLIAMENT_IN_SESSION", "[Player.GetGovernment.GetParliament.GetName] in Session"),
        ("APPOINT_CABINET", "Appoint a State Officer"),
        ("ADD_CABINET_CHARACTER", "Appoint a State Officer"),
        ("NO_CURRENT_ADVISOR", "No state officer has been appointed to this office."),
        ("NO_CABINET_ACTION", "No administrative programme assigned"),
        ("SELECT_CABINET_MEMBER", "Select the character to hold this state office:"),
        ("AUTOMATED_SYSTEM_CABINET", "State Offices"),
        ("AUTOMATED_SYSTEM_PARLIAMENT", "Council"),
    )
    lines = [f"l_{language}:"]
    lines.extend(f' {key}: "{q(value)}"' for key, value in entries)
    return "\n".join(lines) + "\n"


def csv_text(header: tuple[str, ...], rows: list[tuple[str, ...]]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    return stream.getvalue()


def content_ledger() -> str:
    rows: list[tuple[str, ...]] = []
    for profile in PROFILES:
        rows.append(("parliament_type", profile.parliament, profile.slug, profile.name, profile.description, profile.source, profile.confidence, profile.note))
        for action in profile.actions:
            rows.append(("cabinet_action", f"antq_{profile.slug}_{action.slug}", profile.slug, action.name, action.description, profile.source, profile.confidence, profile.note))
        for motion in profile.motions:
            rows.append(("parliament_issue", f"antq_issue_{profile.slug}_{motion.slug}", profile.slug, motion.issue_name, motion.issue_description, profile.source, profile.confidence, profile.note))
            rows.append(("parliament_agenda", f"antq_agenda_{profile.slug}_{motion.slug}", profile.slug, motion.agenda_name, motion.agenda_description, profile.source, profile.confidence, profile.note))
    return csv_text(("category", "key", "profile", "name", "description", "source", "confidence", "note"), rows)


def art_records() -> list[tuple[str, str, Profile, int]]:
    records: list[tuple[str, str, Profile, int]] = []
    for profile in PROFILES:
        records.append(("parliament_type", profile.parliament, profile, 0))
        records.extend(("cabinet_action", f"antq_{profile.slug}_{action.slug}", profile, index) for index, action in enumerate(profile.actions, 1))
    return records


def master_path(key: str) -> Path:
    return MASTERS / f"{key}_128.png"


def texture_path(category: str, key: str) -> Path:
    folder = "parliament_types" if category == "parliament_type" else "cabinet_actions"
    return ROOT / f"main_menu/gfx/interface/icons/{folder}/{key}.dds"


def art_ledger() -> str:
    rows = []
    for category, key, profile, cell in art_records():
        rows.append((
            category, key, profile.slug, f"assets_queue/politics/sources/{profile.source_file}",
            profile.source_hash, str(cell), master_path(key).relative_to(ROOT).as_posix(),
            texture_path(category, key).relative_to(ROOT).as_posix(), "128x128 BC7 sRGBA + full mip chain",
        ))
    return csv_text(("category", "key", "profile", "source", "source_sha256", "cell", "master", "texture", "contract"), rows)


def expected_files() -> dict[Path, str]:
    outputs = {
        TYPE_OUT: parliament_types(),
        CABINET_OUT: cabinet_actions(),
        ISSUE_OUT: parliament_issues(),
        AGENDA_OUT: parliament_agendas(),
        MODIFIER_OUT: static_modifiers(),
        CONTENT_LEDGER: content_ledger(),
        ART_LEDGER: art_ledger(),
    }
    for language in ("english", *M2_MIRROR_LANGUAGES):
        outputs[ROOT / f"main_menu/localization/{language}/antq_s2_politics_l_{language}.yml"] = localization(language)
        outputs[ROOT / f"main_menu/localization/{language}/zz_antq_s2_ui_l_{language}.yml"] = ui_localization(language)
    return outputs


def build_art() -> None:
    MASTERS.mkdir(parents=True, exist_ok=True)
    for category, key, profile, cell in art_records():
        source = SOURCES / profile.source_file
        if hashlib.sha256(source.read_bytes()).hexdigest() != profile.source_hash:
            raise ValueError(f"source hash drift: {source.relative_to(ROOT)}")
        with Image.open(source) as image:
            if image.size != (1536, 1024):
                raise ValueError(f"{source.relative_to(ROOT)} must be 1536x1024")
            x, y = (cell % 3) * 512, (cell // 3) * 512
            rendered = image.convert("RGB").crop((x + 8, y + 8, x + 504, y + 504)).resize((128, 128), Image.Resampling.LANCZOS)
            master = master_path(key)
            master.parent.mkdir(parents=True, exist_ok=True)
            rendered.save(master, format="PNG", optimize=True)
        texture = texture_path(category, key)
        texture.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [sys.executable, str(DDS_TOOL), "convert", str(master), str(texture), "--compression", "bc7"],
            check=True,
        )


def validate() -> list[str]:
    failures: list[str] = []
    content = content_ledger()
    rows = list(csv.DictReader(io.StringIO(content)))
    counts = {category: sum(row["category"] == category for row in rows) for category in {row["category"] for row in rows}}
    expected_counts = {"parliament_type": 9, "cabinet_action": 45, "parliament_issue": 27, "parliament_agenda": 27}
    if counts != expected_counts:
        failures.append(f"content counts differ: {counts}")
    if len({row["key"] for row in rows}) != len(rows):
        failures.append("duplicate ancient-politics content key")
    if any(len(row["description"]) < 55 for row in rows):
        failures.append("an ancient-politics description is too shallow")
    if set(COUNCIL_DYNAMICS) != {profile.slug for profile in PROFILES}:
        failures.append("council political dynamics do not cover exactly the nine profiles")
    if len(set(COUNCIL_DYNAMICS.values())) != len(PROFILES):
        failures.append("council political dynamics must be distinct by profile")
    for profile in PROFILES:
        base_support, agenda_impacts = COUNCIL_DYNAMICS[profile.slug]
        if not 0 <= float(base_support) <= 0.25:
            failures.append(f"unsafe base support for council profile {profile.slug}")
        if {estate for estate, _impact in agenda_impacts} != set(profile.estates):
            failures.append(
                f"agenda-impact participants differ from council participants for {profile.slug}"
            )
        if any(not -0.25 <= float(impact) <= 0.40 for _estate, impact in agenda_impacts):
            failures.append(f"unsafe agenda impact for council profile {profile.slug}")
        source = SOURCES / profile.source_file
        if not source.is_file():
            failures.append(f"missing source atlas: {source.relative_to(ROOT)}")
        elif hashlib.sha256(source.read_bytes()).hexdigest() != profile.source_hash:
            failures.append(f"source atlas hash drift: {source.relative_to(ROOT)}")
    for path, expected in expected_files().items():
        if not path.is_file():
            failures.append(f"missing generated file: {path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8-sig") != expected:
            failures.append(f"stale generated file: {path.relative_to(ROOT)}")
    for category, key, _, _ in art_records():
        master = master_path(key)
        texture = texture_path(category, key)
        if not master.is_file():
            failures.append(f"missing art master: {master.relative_to(ROOT)}")
        else:
            with Image.open(master) as image:
                if image.size != (128, 128):
                    failures.append(f"wrong master dimensions: {master.relative_to(ROOT)}")
        if not texture.is_file():
            failures.append(f"missing direct texture: {texture.relative_to(ROOT)}")
        else:
            details = identify(texture)
            if details != {"format": "DDS", "width": "128", "height": "128", "depth": "8", "channels": "srgba 4.0"}:
                failures.append(f"wrong DDS contract: {texture.relative_to(ROOT)} = {details}")
    return failures


def write() -> None:
    build_art()
    bom_scripts = {TYPE_OUT, CABINET_OUT, ISSUE_OUT, AGENDA_OUT, MODIFIER_OUT}
    for path, rendered in expected_files().items():
        path.parent.mkdir(parents=True, exist_ok=True)
        encoding = "utf-8-sig" if path.suffix == ".yml" or path in bom_scripts else "utf-8"
        path.write_text(rendered, encoding=encoding, newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        write()
    failures = validate()
    if failures:
        print("s2_ancient_politics: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("s2_ancient_politics: PASS (9 councils; 45 cabinet actions; 27 issues; 27 agendas; 54 direct icons)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
