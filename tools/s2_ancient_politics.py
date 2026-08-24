#!/usr/bin/env python3
"""Render and audit the first deep ancient council/cabinet replacement."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import subprocess
import sys
from dataclasses import dataclass, replace
from pathlib import Path

from PIL import Image

from dates import M2_MIRROR_LANGUAGES
from dds import identify
from m5_trade_good_cutouts import magenta_cutout
from m6_power import PROFILE_BASE_REFORMS
from s2_regional_programmes import (
    REGIONAL_PACKS,
    SHEET_HASHES,
    SMALL_STATE_PROFILE_SLUGS,
    action_key,
    all_programmes,
)

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
CONFIG = ROOT / "config/local_paths.json"
CABINET_GUI_RELATIVE = Path("in_game/gui/shared/cabinet_cards.gui")
CABINET_GUI_OUT = ROOT / CABINET_GUI_RELATIVE
CABINET_GUI_SOURCE_SHA256 = "1e1d7464d31bfe2b3b17ddbc2764755132bc0e70118f4dbd46a186233e4f71fa"
CABINET_GUI_BAD_CONTEXT = 'text = "[CabinetItem.GetActionProgressLongWordier]"'
CABINET_GUI_SAFE_CONTEXT = 'text = "[Cabinet.GetActionProgressLongWordier]"'


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
ASSIZE = (("stability_cost_efficiency", "-0.03"), ("global_monthly_control", "0.002"))
PUBLIC_WORKS = (("global_road_building_time", "-0.05"), ("global_production_efficiency", "0.02"))
MINT = (("country_cabinet_efficiency", "0.02"), ("global_trade_through_owned_territory_efficiency", "0.03"))
SUBJECTS = (("subject_loyalty", "5"), ("monthly_prestige", "0.04"))
NAVY = (("global_sailors_modifier", "0.04"), ("navy_maintenance_efficiency", "-0.03"))
RITUAL = (("research_speed_modifier", "0.015"), ("stability_cost_efficiency", "-0.025"))


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
        (
            "antq_principate", "antq_augustan_dyarchy",
            "antq_provincial_principate", "antq_flavian_imperial_settlement",
            "antq_antonine_provincial_principate", "antq_severan_military_principate",
        ),
        ("nobles_estate", "burghers_estate", "clergy_estate"),
        "roman_principate_atlas.png", "1e990edda4ce5fbba251e79738731b1141090ab6d69111895354474c00497f36",
        "P8.1;P11;P13;OCD", "secure",
        "Engine estates represent senators, equestrian contractors, and public priestly colleges; this does not turn the Augustan Senate into a sovereign legislature.",
        (
            a("census_rolls", "Census Rolls", "Coordinate citizen, property, and status returns through censoria potestas and provincial reporting.", "adm", ADMIN),
            a("provincial_dispatches", "Provincial Dispatches", "Collate governors' reports, petitions, and senatorial commissions before decisions reach the princeps.", "dip", CONTROL),
            a("aerarium_accounts", "Aerarium Accounts", "Reconcile public receipts, contracts, and coin reserves without pretending that imperial and senatorial finances were one office.", "adm", TRADE),
            a("grain_contracts", "Annona Contracts", "Supervise measures, shippers, storage obligations, and the politically vital grain supply.", "dip", FOOD),
            a("legionary_rosters", "Legionary Rosters", "Maintain discharge, donative, veteran, and replacement records for the standing legions.", "mil", MIL),
            a("imperial_correspondence", "Imperial Correspondence", "Sort authenticated petitions, provincial dispatches, draft replies, and sealed instructions moving through the princeps' household.", "dip", ADMIN),
            a("provincial_assize_returns", "Provincial Assize Returns", "Collate governors' assize itineraries, civic appeals, boundary disputes, and judgments without imposing one uniform provincial procedure.", "adm", ASSIZE),
            a("public_works_curators", "Public-Works Curators", "Coordinate road, bridge, aqueduct, riverbank, and public-building commissions through bounded curatorships and local contracts.", "adm", PUBLIC_WORKS),
            a("mint_assay_accounts", "Mint and Assay Accounts", "Inspect bullion, dies, weights, fineness, and delivery accounts while preserving the varied organization of imperial mints.", "adm", MINT),
            a("client_king_dossiers", "Client-King Dossiers", "Maintain dynastic, treaty, hostage, gift, petition, and succession records for the empire's negotiated ring of client courts.", "dip", SUBJECTS),
            a("fleet_supply_returns", "Fleet Supply Returns", "Review crews, hull fittings, cordage, amphorae, harbor stores, and grain-escort obligations for the imperial fleets.", "mil", NAVY),
        ),
        (
            m("census_review", "Provincial Census Review", "Debate a coordinated review of provincial declarations, civic status, and assessed obligations.", "Senatorial Provincial Scrutiny", "Senatorial houses demand a formal commission before provincial assessments are revised.", "nobles_estate", ADMIN, NOBLES),
            m("annona_commission", "Annona Contract Commission", "Authorize scrutiny of grain measures, storage losses, and shipping contracts.", "Equestrian Contract Petition", "Equestrian contractors seek predictable terms and protected performance of public supply contracts.", "burghers_estate", FOOD, TRADE),
            m("legionary_settlement", "Legionary Settlement Act", "Settle discharge grants and veteran obligations without stripping frontier commands of replacements.", "Priestly Calendar Petition", "The public colleges ask that musters, vows, and games respect the authorized civic calendar.", "clergy_estate", MIL, CLERGY),
            m("provincial_appeals", "Provincial Appeals Docket", "Authorize a bounded hearing of civic petitions, governors' judgments, and disputed public obligations.", "Senatorial Assize Commission", "Senatorial houses request a witnessed role in reviewing provincial judgments and elite liabilities.", "nobles_estate", ASSIZE, NOBLES),
            m("public_works_appropriation", "Public-Works Appropriation", "Set priorities for roads, aqueducts, bridges, embankments, and civic repairs without promising a universal building programme.", "Contractors' Maintenance Terms", "Equestrian and civic contractors seek predictable inspection, payment, and material-delivery terms.", "burghers_estate", PUBLIC_WORKS, TRADE),
            m("mint_standard", "Mint Standard Review", "Review bullion receipts, weight standards, die custody, and coin deliveries across the active imperial mints.", "Moneyers' Assay Petition", "Mint and exchange households request stable assays and protection from retrospective liability.", "burghers_estate", MINT, TRADE),
            m("client_king_settlement", "Client-King Settlement", "Recognize a succession, guarantee, hostage return, or revised obligation at one of Rome's dependent courts.", "Dynastic Embassy Hearing", "Senatorial houses seek a formal hearing before a major client succession or guarantee is settled.", "nobles_estate", SUBJECTS, PRESTIGE),
            m("fleet_supply_contract", "Fleet Supply Contract", "Set bounded terms for crews, grain escort, harbor stores, timber fittings, sailcloth, and cordage.", "Navicular Contract Petition", "Shipping and harbor households request compensation rules and inspected measures for public carriage.", "burghers_estate", NAVY, TRADE),
            m("pontifical_calendar_review", "Pontifical Calendar Review", "Coordinate vows, public rites, games, prodigy reports, and magistrates' calendars without turning priestly colleges into a church.", "Priestly College Consultation", "Public priestly colleges request secure consultation before the civic ritual calendar is altered.", "clergy_estate", RITUAL, CLERGY),
        ),
    ),
    Profile(
        "late_roman", "antq_imperial_consistory", "Imperial Consistory",
        "The late imperial consistory and palatine offices coordinate rescripts, prefectural returns, provincial dispatches, military supply, and court deliberation around the emperor.",
        (
            "antq_dominate", "antq_tetrarchic_collegium",
            "antq_constantinian_consistory", "antq_late_imperial_twin_courts",
        ),
        ("nobles_estate", "clergy_estate", "burghers_estate"),
        "late_roman_consistory_atlas.png", "f0cdfa119856f3cc36736a23966bc19b20d2b7a2b8d39d31a4d2bf3948c65329",
        "P8.1;P9;P11;P13;P15;CAH-XII;OCD;ND", "secure",
        "The profile separates later palatine and prefectural government from the Augustan Senate while compressing offices whose exact hierarchy changed repeatedly between Diocletian and 476.",
        (
            a("imperial_rescripts", "Imperial Rescript Bureau", "Order petitions, legal consultations, draft constitutions, authenticated replies, and archive copies through the late imperial court.", "adm", ADMIN),
            a("praetorian_prefecture_returns", "Praetorian Prefecture Returns", "Reconcile taxation, appeals, transport, supply, and provincial reports at the empire's senior regional prefectures.", "adm", CONTROL),
            a("diocesan_dispatches", "Diocesan Dispatches", "Coordinate vicars, governors, relays, reports, and appeals without presenting every late province as administratively identical.", "dip", LOGISTICS),
            a("field_army_registers", "Field-Army Registers", "Track comitatenses, frontier detachments, remounts, arms, pay, and replacements across mobile and regional commands.", "mil", MIL),
            a("annona_militaris_accounts", "Annona Militaris Accounts", "Assess and route grain, fodder, clothing, animals, transport, and other supplies required by the late imperial armies.", "adm", FOOD),
        ),
        (
            m("prefectural_assessment", "Prefectural Assessment Cycle", "Review apportioned taxes, transport obligations, remissions, arrears, and provincial capacity across a bounded prefectural circuit.", "Provincial Magnates' Assessment Petition", "Senatorial and provincial houses request predictable liabilities and a hearing before extraordinary reassessment.", "nobles_estate", ADMIN, NOBLES),
            m("imperial_appeals", "Imperial Appeals Session", "Resolve selected provincial appeals and rescripts while preserving lower jurisdictions and the court's limited attention.", "Ecclesiastical Intercession Petition", "Recognized religious authorities request a bounded hearing for communities, prisoners, or disputed endowments.", "clergy_estate", ASSIZE, CLERGY),
            m("military_supply_allocation", "Military Supply Allocation", "Balance field-army, frontier, transport, grain, clothing, and remount demands across the active commands.", "State Contractors' Delivery Terms", "Curial, transport, workshop, and merchant households seek measured requisitions and reliable delivery credits.", "burghers_estate", LOGISTICS, TRADE),
        ),
    ),
    Profile(
        "han", "antq_han_court_conference", "Han Court Conference",
        "Western Han court conferences reconcile memorials, the Three Excellencies and Nine Ministers, commandery returns, fiscal registers, ritual consultation, and the competing claims of palace, affinal, and scholarly officeholders.",
        (
            "antq_han_imperial_bureaucracy", "antq_memorialist_han_court",
            "antq_commandery_supervision", "antq_xin_state_reorganization",
        ),
        ("nobles_estate", "burghers_estate", "peasants_estate"),
        "han_court_atlas.png", "7d57f4dcc204afa0670c412fe1a649b257c6dcacd80dcf04d16216b6dede3380",
        "P8.3;P13;BHR;CTP-WM", "secure",
        "The three participating estates are technical proxies for court lineages, salaried administrators, registered cultivator households, and affected workshop or market interests; this is not a later examination ministry system.",
        (
            a("commandery_reports", "Commandery Reports", "Collate population, justice, harvest, and revenue returns from commanderies and kingdoms.", "adm", ADMIN),
            a("imperial_secretariat", "Imperial Secretariat", "Order memorials, draft replies, authenticate tallies, and prevent contradictory palace instructions.", "dip", CONTROL),
            a("granary_registers", "Granary Registers", "Compare receipts, spoilage, release orders, and local price pressures across official stores.", "adm", FOOD),
            a("courier_relays", "Courier Relays", "Maintain tallies, relay horses, sealed document tubes, and the roads between reporting stations.", "dip", LOGISTICS),
            a("frontier_command", "Frontier Command Returns", "Synchronize beacon reports, garrison strength, remount needs, and crossbow stores.", "mil", MIL),
            a("three_excellencies_reviews", "Three Excellencies Reviews", "Coordinate high-level civil, military, and supervisory recommendations among the empire's senior offices.", "adm", ADMIN),
            a("nine_ministers_dockets", "Nine Ministers Dockets", "Order ritual, household, guard, horse, justice, diplomatic, clan, revenue, and palace-service business for conference and decision.", "adm", CONTROL),
            a("regional_inspector_reports", "Regional Inspector Reports", "Collate rotating inspectors' reports on commandery officials, powerful households, justice, revenue, roads, and public order.", "dip", ASSIZE),
            a("household_registration_returns", "Household Registration Returns", "Reconcile registered households, land, age and service categories, grain obligations, migration, and local discrepancies.", "adm", FOOD),
            a("salt_iron_accounts", "Salt and Iron Accounts", "Review salt production, iron tools and castings, workshop deliveries, prices, transport, and contested state participation.", "adm", MINT),
            a("grand_herald_guest_registers", "Grand Herald Guest Registers", "Maintain audiences, interpreters, gifts, seals, hostages, and ranked obligations for kings, tributaries, and foreign envoys.", "dip", PRESTIGE),
        ),
        (
            m("commandery_audit", "Commandery Audit Cycle", "Dispatch a bounded audit of household registers, judgments, and remittances.", "Court Lineage Appointment Memorial", "Powerful court lineages press for candidates whose obligations and competence the throne can verify.", "nobles_estate", ADMIN, NOBLES),
            m("granary_allocation", "Granary Allocation Conference", "Balance local reserves against transport loss, relief, and frontier demand.", "Clerks' Register Petition", "Administrative households request stable appointments and adequate staff for the expanding register burden.", "burghers_estate", FOOD, ADMIN),
            m("frontier_dispatch", "Frontier Garrison Dispatch", "Set remount, beacon, and stores priorities for the northern commands.", "Cultivator Corvée Relief", "Registered households petition for predictable labor rotations during the agricultural season.", "peasants_estate", MIL, PEASANTS),
            m("official_recommendations", "Official Recommendation Review", "Compare service records, local recommendations, court memorials, and conflicts of interest before senior appointments.", "Great-Family Nomination Memorial", "Court and provincial families seek recognized recommendation channels while accepting review of kinship and prior service.", "nobles_estate", ADMIN, NOBLES),
            m("justice_docket", "Commandant of Justice Docket", "Review selected capital cases, conflicting judgments, amnesties, and remands without replacing local adjudication.", "Clerks' Procedural Petition", "Administrative households request authenticated forms and protection from contradictory retrospective orders.", "burghers_estate", ASSIZE, ADMIN),
            m("household_register_revision", "Household Register Revision", "Set a bounded cycle for correcting household, land, labor, and service records after migration, death, or crop failure.", "Registered Household Hearing", "Cultivating households petition for witnessed corrections before extraordinary labor or grain demands.", "peasants_estate", CONTROL, PEASANTS),
            m("salt_iron_supply", "Salt and Iron Supply Conference", "Balance state revenue, tool supply, workshop capacity, transport loss, and local prices without assuming one unchanging monopoly.", "Workshop Quota Petition", "Workshop and market households request stable inputs, inspected measures, and bounded delivery liability.", "burghers_estate", MINT, TRADE),
            m("western_regions_audience", "Western Regions Audience", "Set gifts, hostages, ranks, escort, relay, and frontier-market terms for a bounded diplomatic audience.", "Court Precedence Memorial", "Great families request witnessed order and accountability in the distribution of honors and diplomatic gifts.", "nobles_estate", PRESTIGE, NOBLES),
            m("ritual_calendar", "Ritual and Calendar Consultation", "Review court rites, ancestral observance, calendrical coordination, and the language of public measures.", "Scholarly Remonstrance", "Ritual and scholarly officials seek a protected memorial channel without claiming a later examination establishment.", "nobles_estate", RITUAL, ADMIN),
        ),
    ),
    Profile(
        "late_han", "antq_eastern_han_imperial_secretariat", "Eastern Han Imperial Secretariat",
        "The restored and later Han court increasingly coordinates memorials, appointments, imperial decisions, provincial reports, military commands, and ritual scholarship through the palace Secretariat while the Three Excellencies retain formal standing.",
        (
            "antq_guangwu_restoration_court", "antq_eastern_han_secretariat",
            "antq_affinal_regency_court", "antq_provincial_inspectorate_commands",
            "antq_three_kingdoms_chancellery", "antq_jin_reunification_court",
        ),
        ("nobles_estate", "burghers_estate", "clergy_estate"),
        "late_han_secretariat_atlas.png", "9bff557047681d86fe076b3272b199a26677568f00f6b2d557c0bc3d6b6ea7f0",
        "P8.3;P9;P13;BHR;CAH-X;CAH-XII", "secure",
        "The profile models the documented rise of the Imperial Secretariat and late-Han court/provincial tensions while keeping Eastern Han, Three Kingdoms, and Jin successor paths separate reforms rather than one static bureaucracy.",
        (
            a("secretariat_memorials", "Secretariat Memorials", "Register, classify, draft, authenticate, and circulate imperial decisions and memorial replies through the palace Secretariat.", "adm", ADMIN),
            a("three_excellencies_evaluations", "Three Excellencies Evaluations", "Review senior officials, provincial reports, ceremonial standing, and administrative failures through the formal high offices.", "adm", ASSIZE),
            a("provincial_inspector_returns", "Provincial Inspector Returns", "Compare circuit reports on administrators, powerful households, justice, revenue, roads, and armed disorder.", "dip", CONTROL),
            a("palace_affinal_dockets", "Palace and Affinal Dockets", "Track regency authority, imperial kin, empress families, household appointments, seals, and conflicts of interest.", "dip", PRESTIGE),
            a("military_command_registers", "Military Command Registers", "Coordinate generalships, garrisons, volunteers, crossbow stores, remounts, grain, and emergency regional commands.", "mil", MIL),
        ),
        (
            m("secretariat_authority", "Secretariat Authority Review", "Define which memorials, appointments, edicts, and reports pass through the palace Secretariat and how they are authenticated.", "Formal Office Remonstrance", "Senior officials demand recorded review before palace instructions displace the outer court.", "nobles_estate", ADMIN, NOBLES),
            m("provincial_emergency_command", "Provincial Emergency Command", "Assign bounded military, supply, and reporting authority against rebellion or frontier crisis without normalizing permanent warlord government.", "Commandery Supply Petition", "Administrative and market households seek measured requisitions and delivery credits under emergency command.", "burghers_estate", MIL, TRADE),
            m("classics_recommendation", "Classics and Recommendation Conference", "Coordinate Taixue learning, local recommendation, court scholarship, and official evaluation without projecting the later examination system backward.", "Scholarly Office Petition", "Classical and ritual officials request protected teaching resources and a hearing on appointments and court rites.", "clergy_estate", RITUAL, CLERGY),
        ),
    ),
    Profile(
        "iranian", "antq_iranian_great_council", "Arsacid Great-House Council",
        "The Arsacid king of kings negotiates succession, subking tribute, mounted host service, royal domains, road security, and dynastic precedence with great houses and royal officers.",
        (
            "antq_parthian_king_of_kings", "antq_parthian_subkingdom",
            "antq_indo_scythian_kingship", "antq_iranian_great_house_reform",
            "antq_iranian_royal_domain", "antq_vologasid_dynastic_settlement",
            "antq_arsacid_dual_court_compact", "antq_late_arsacid_house_mobilization",
        ),
        ("nobles_estate", "clergy_estate", "burghers_estate"),
        "iranian_council_atlas.png", "4986d7ce7a8951994a1fb9dd3679b7cd7e89425c442960c9ce411847942972c3",
        "P8.2;P9;P13;CAH-XI;OCD;IRAN-ADMIN;IRAN-ARSACID", "contested",
        "Great-house power, subkings, host service, and dynastic negotiation are secure; the council is a bounded gameplay arena and does not assert a fixed constitutional Mahistan.",
        (
            a("noble_host_musters", "Noble-Host Musters", "Record the mounted followings and equipment promised by royal and regional houses.", "mil", NOBLES),
            a("royal_road_couriers", "Royal-Road Couriers", "Protect relay mounts, sealed messages, and road stations between court and sub-kingdoms.", "dip", LOGISTICS),
            a("satrapal_accounts", "Regional Accounts", "Reconcile silver, gifts, levies, and retained local revenues without inventing uniform provinces.", "adm", ADMIN),
            a("caravan_protection", "Caravan Safe-Conducts", "Coordinate escorts, watering points, and compensation rules on long-distance routes.", "dip", TRADE),
            a("dynastic_arbitration", "Dynastic Arbitration", "Use hostages, oaths, marriages, and precedence rulings to contain disputes among houses.", "adm", PRESTIGE),
            a("dynastic_succession_dockets", "Dynastic Succession Dockets", "Record royal nominations, Arsacid lineage claims, great-house acclamation, hostages, and the obligations attached to a succession settlement.", "dip", PRESTIGE),
            a("subkingdom_tribute_returns", "Subkingdom Tribute Returns", "Review gifts, coin, mounted service, court attendance, and retained local authority among subordinate kings without pretending they form uniform provinces.", "adm", SUBJECTS),
            a("royal_domain_accounts", "Royal-Domain Accounts", "Inventory selected royal lands, herds, workshops, stores, and revenues while distinguishing them from great-house and subking possessions.", "adm", CONTROL),
            a("mounted_host_registers", "Mounted-Host Registers", "Compare promised cataphracts, horse archers, remounts, armor, baggage, and campaigning seasons before a royal muster.", "mil", MIL),
            a("river_caravan_customs", "River and Caravan Customs", "Coordinate weights, sealed cargo, ferries, river landings, escorts, and compensation along Mesopotamian and Iranian exchange routes.", "dip", TRADE),
            a("hostage_oath_registers", "Hostage and Oath Registers", "Preserve witnessed guarantees, dynastic hostages, marriage bonds, precedence, and restitution terms used to stabilize negotiated settlements.", "adm", ASSIZE),
        ),
        (
            m("host_contribution", "Noble-Host Contribution", "Set the scale and season of great-house mounted service.", "Great-House Precedence Claim", "Leading houses demand that court precedence reflect service, lineage, and negotiated autonomy.", "nobles_estate", MIL, NOBLES),
            m("road_protection", "Royal-Road Protection", "Fund relays and escorts on routes binding the royal court to regional powers.", "Fire-Custodian Endowment", "Ritual custodians request secure revenues for court and local sacred observance.", "clergy_estate", LOGISTICS, CLERGY),
            m("silver_reckoning", "Satrapal Silver Reckoning", "Review retained revenue, royal gifts, and coin remittances without asserting a uniform tax code.", "Caravan Safe-Conduct Petition", "Merchant households seek enforceable passage and compensation after losses on protected roads.", "burghers_estate", ADMIN, TRADE),
            m("succession_acclamation", "Arsacid Succession Acclamation", "Weigh royal nomination, Arsacid lineage, great-house support, military command, and hostage guarantees in a disputed succession.", "Great-House Acclamation Claim", "Leading houses seek a witnessed voice in recognizing the next king while accepting responsibility for the settlement they endorse.", "nobles_estate", PRESTIGE, NOBLES),
            m("subking_tribute", "Subking Tribute Settlement", "Set bounded tribute, attendance, host service, coin, gifts, and arbitration duties for subordinate kings.", "Subking Autonomy Petition", "Regional dynasts seek recognition of local law, cult, and succession in return for stated royal obligations.", "nobles_estate", SUBJECTS, NOBLES),
            m("royal_domain_assessment", "Royal-Domain Assessment", "Review selected royal estates, herds, stores, workshops, and conveyance obligations without claiming a uniform empire-wide cadastre.", "Cultivator Liability Petition", "Royal-domain communities seek measured dues, seasonal labor limits, and witnessed correction after crop or herd loss.", "peasants_estate", CONTROL, PEASANTS),
            m("mounted_host_quota", "Mounted-Host Quota", "Allocate cataphracts, horse archers, remounts, armor, baggage, and campaign duration among royal and great-house contingents.", "Mounted-House Exemption Claim", "Great houses seek fiscal and local exemptions proportional to the contingents, remounts, and command they provide.", "nobles_estate", MIL, NOBLES),
            m("river_caravan_customs", "River and Caravan Customs Review", "Set weights, sealed cargo procedures, ferries, river landings, escort liability, and compensation on protected routes.", "Merchant Measure Petition", "Caravan and urban houses seek stable measures and predictable tolls in return for registered cargo and route intelligence.", "burghers_estate", TRADE, TRADE),
            m("hostage_oath_settlement", "Hostage and Oath Settlement", "Review hostages, marriage bonds, witnessed oaths, restitution, and precedence after conflict among dynastic houses.", "Sanctuary Witness Petition", "Cult custodians seek recognized custody of oaths and deposits without claiming a uniform empire-wide religious jurisdiction.", "clergy_estate", ASSIZE, CLERGY),
        ),
    ),
    Profile(
        "sasanian", "antq_sasanian_royal_council", "Sasanian Royal Council",
        "The Sasanian king of kings coordinates palace command, provincial revenue, frontier officers, the royal post, and judicial-religious petitions through a more directive court while still bargaining with great houses and local authorities.",
        (
            "antq_sassanid_centralized_monarchy", "antq_ardashir_unification_court",
            "antq_shapur_imperial_settlement", "antq_sasanian_shahrdar_marzban_order",
            "antq_yazdegerd_concordat_court", "antq_bahram_great_house_settlement",
        ),
        ("nobles_estate", "clergy_estate", "burghers_estate"),
        "sasanian_royal_council_atlas.png", "d5a17faa93bc77d2595f1525473c4b2ad730f6599ad47be57dec1643f00489ce",
        "P8.2;P9;P13;CAH-XII;IRAN-ADMIN;IRAN-FRAMADAR;IRAN-JUDICIAL", "secure",
        "The profile uses securely attested Sasanian court, revenue, frontier, post, and judicial-religious functions; exact office titles and competencies varied across the dynasty and are not frozen into one recovered constitution.",
        (
            a("grand_command_office", "Grand Command Office", "Authenticate royal instructions, senior appointments, court precedence, military commissions, and the circulation of sealed commands.", "adm", ADMIN),
            a("provincial_revenue_registers", "Provincial Revenue Registers", "Compare land, household, produce, coin, exemption, and arrears returns while allowing for regional variation and incomplete assessment.", "adm", CONTROL),
            a("marzban_frontier_returns", "Marzban Frontier Returns", "Review fortified zones, mounted forces, garrison stores, intelligence, tribute, and diplomatic obligations along exposed frontiers.", "mil", MIL),
            a("royal_post_dispatches", "Royal Post Dispatches", "Coordinate road stations, remounts, couriers, sealed intelligence, official travel, and emergency supply across the imperial network.", "dip", LOGISTICS),
            a("judicial_religious_petitions", "Judicial and Religious Petitions", "Review appeals involving royal justice, local custom, endowments, fire establishments, family law, and conflicts of jurisdiction.", "adm", ASSIZE),
        ),
        (
            m("provincial_assessment", "Provincial Assessment Review", "Set a bounded cycle for reconciling land, household, produce, coin, exemption, and arrears returns with regional officers.", "Great-House Assessment Petition", "Provincial houses seek witnessed limits and inherited exemptions while accepting audited service and remittance obligations.", "nobles_estate", CONTROL, NOBLES),
            m("frontier_command", "Frontier Command Settlement", "Allocate fortified commands, cavalry, stores, intelligence, diplomacy, and relief duties among frontier officers and regional powers.", "Garrison Community Petition", "Frontier communities seek market access, restitution, and measured transport duties in return for watch and supply service.", "burghers_estate", MIL, TRADE),
            m("judicial_religious_settlement", "Judicial and Religious Settlement", "Coordinate royal adjudication, local custom, family law, endowment disputes, and religious establishments without collapsing their distinct jurisdictions.", "Fire and Judicial Endowment Petition", "Religious and learned officers seek protected stores and hearings while accepting inventories and royal arbitration.", "clergy_estate", ASSIZE, CLERGY),
        ),
    ),
    Profile(
        "civic", "antq_civic_assembly", "Civic Council",
        "A boule or comparable civic body manages accounts, magistracies, sanctuaries, harbor obligations, and the enrolled citizen body.",
        ("antq_indo_greek_kingship", "antq_settled_town_cluster", "antq_boule_magistracy", "antq_federal_synedrion"), ("burghers_estate", "nobles_estate", "peasants_estate"),
        "civic_assembly_atlas.png", "3a43c68d91f7436abfa49f1d703c284fcb192a400f5d317d083992826f90c158",
        "P8.4;P13;CAH-XI;OCD", "contested",
        "The civic surface is deliberately constitutional rather than ethnic and does not imply identical franchise rules in every city.",
        (
            a("civic_accounts", "Civic Accounts", "Publish magistrates' receipts, sanctuary funds, contracts, and arrears for council scrutiny.", "adm", ADMIN),
            a("harbor_dues", "Harbor Dues", "Standardize weights, amphora stamps, wharf charges, and exemptions for local commerce.", "dip", TRADE),
            a("citizen_muster", "Citizen Muster Roll", "Keep an enrolled civic levy and its equipment obligations current.", "mil", MIL),
            a("magistrate_rotations", "Magistrate Rotations", "Sequence offices, handovers, seals, and public accounting to limit administrative capture.", "adm", CONTROL),
            a("sanctuary_embassies", "Sanctuary Embassies", "Coordinate sacred envoys, interstate honors, and treaty deposits at recognized sanctuaries.", "dip", PRESTIGE),
            a("ward_assessment_returns", "Ward Assessment Returns", "Reconcile household, property, boundary, and service tallies by civic ward while accepting scrutiny from enrolled local interests.", "adm", ADMIN + (("global_burghers_estate_power", "0.02"),)),
            a("harbor_market_arbitration", "Harbor-Market Arbitration", "Hear disputed measures, berthing obligations, storage claims, and damaged cargo before they disrupt civic exchange.", "dip", TRADE + (("global_burghers_estate_power", "0.02"),)),
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
        ("antq_indian_ganasangha", "antq_lineage_rotation", "antq_gana_muster_confederacy"), ("nobles_estate", "peasants_estate", "burghers_estate"),
        "gana_assembly_atlas.png", "6cc71845187d386edb2c22f9f580725b6f2af0190e42128f0228512ebee42608",
        "P8.4;P13;CAH-XI", "contested",
        "The mechanics are a conservative gana-sangha adapter and do not reconstruct one franchise or procedure for every polity.",
        (
            a("clan_delegates", "Clan Delegates", "Maintain recognized speaking order, delegate tokens, and witnessed assembly decisions.", "adm", ADMIN),
            a("assembly_arbitration", "Assembly Arbitration", "Resolve obligations between lineages before disputes fracture collective action.", "dip", PRESTIGE),
            a("confederate_muster", "Confederate Muster", "Count each participating lineage's equipment and seasonal service.", "mil", MIL),
            a("road_hospitality", "Road Hospitality", "Coordinate water, shelter, safe conduct, and reciprocal duties for travelers.", "dip", TRADE),
            a("communal_granaries", "Communal Granaries", "Audit shared measures, seed reserves, spoilage, and emergency distributions.", "adm", FOOD),
            a("clan_seat_rotation", "Clan-Seat Rotation", "Record the speaking tokens, rotation, witnesses, and handover obligations that keep one lineage from capturing the assembly.", "adm", CONTROL + (("global_nobles_estate_power", "0.02"),)),
            a("irrigation_labor_registers", "Irrigation Labor Registers", "Apportion channel clearance, embankment repair, and water turns among represented communities without fixing one universal tenure.", "adm", PUBLIC_WORKS + (("global_peasants_estate_power", "0.02"),)),
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
        ("antq_steppe_wing_confederacy", "antq_steppe_gift_court"), ("tribes_estate", "nobles_estate", "burghers_estate"),
        "steppe_council_atlas.png", "e191587a1bf4a4fd5bdb77f2a2f0b9ef350d46fb709b20ac1e8a71c22ddb9a7b",
        "P8.3;P13;CAH-XI", "secure",
        "Terminology avoids projecting the later Mongol quriltai and decimal institutions onto AD 1 confederations.",
        (
            a("pasture_circuits", "Seasonal Pasture Circuits", "Coordinate negotiated access to winter, spring, summer, and autumn grazing.", "adm", FOOD),
            a("wing_musters", "Left-Right Wing Musters", "Count mounted followings and assign a campaign direction without inventing later decimal ranks.", "mil", MIL),
            a("gift_circulation", "Prestige-Gift Circulation", "Move silk, plaques, vessels, livestock, and honors through the confederate hierarchy.", "dip", PRESTIGE),
            a("envoy_circuits", "Envoy Circuits", "Maintain tallies, interpreters, escorts, and relay mounts for distant lineages.", "dip", LOGISTICS),
            a("remount_registers", "Remount Herd Registers", "Protect breeding stock and allocate fresh mounts to envoys and war leaders.", "mil", NOBLES),
            a("pasture_circuit_tallies", "Pasture-Circuit Tallies", "Witness seasonal routes, water access, reserve grazing, and compensation before herd movements become armed disputes.", "adm", FOOD + (("global_tribes_estate_power", "0.02"),)),
            a("remount_herd_levies", "Remount and Herd Levies", "Count serviceable mounts, replacement animals, fodder burdens, and lineage contributions for a bounded campaign season.", "mil", MIL + (("global_tribes_estate_power", "0.02"),)),
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
        ("antq_advanced_chiefdom", "antq_tribal_kingdom", "antq_elder_moot_kingship", "antq_warband_retinue_kingship"), ("tribes_estate", "clergy_estate", "burghers_estate"),
        "tribal_assembly_atlas.png", "7ab5f2b0be3cdc70c17ae253ae7143d4fa87cf57792becd0be4c0a119753c1af",
        "P8.7;P13;CAH-XI", "contested",
        "A minimal engine adapter for varied early Iron Age assemblies; regional laws and privileges carry narrower archaeological claims.",
        (
            a("elder_moot", "Elder Moot", "Sequence speakers, witnesses, compensation claims, and collective obligations.", "adm", ADMIN),
            a("warband_gifts", "Warband Gifts", "Bind temporary followings through equipment, hospitality, and publicly remembered gifts.", "dip", PRESTIGE),
            a("grove_custody", "Sacred-Place Custody", "Maintain offerings, boundaries, and seasonal observance without inventing a central priesthood.", "adm", CLERGY),
            a("seasonal_muster", "Seasonal Muster", "Count shields, spears, provisions, and expected service for a limited campaign.", "mil", MIL),
            a("river_exchange", "River Exchange Peace", "Protect weights, ferries, guest-right, and specialist traffic at meeting places.", "dip", TRADE),
            a("seasonal_subsistence_round", "Seasonal Subsistence Round", "Coordinate field, woodland, fishing, and hunting access through the locally recognized seasonal round.", "adm", FOOD + (("global_tribes_estate_power", "0.02"),)),
            a("intercommunity_envoys", "Intercommunity Envoys", "Send witnessed staffs, gifts, safe-conduct terms, and compensation proposals to neighboring communities.", "dip", PRESTIGE + (("global_tribes_estate_power", "0.02"),)),
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
        ("antq_temple_endowment_court", "antq_irrigation_palace"), ("clergy_estate", "nobles_estate", "peasants_estate"),
        "sacral_court_atlas.png", "e3f2c652277ae4a140c20c8fe64f6381efae9c53e54fae6e89271f12d2cff1fb",
        "P8.4;P8.5;P11;P13;CAH-XI;PLE", "contested",
        "The shared interface models administrative conjunction, not a claim that Kushite and Lankan sacred kingship were institutionally identical.",
        (
            a("temple_storehouses", "Temple Storehouses", "Audit sealed jars, endowed land receipts, offerings, and emergency releases.", "adm", FOOD),
            a("royal_waterworks", "Royal Waterworks", "Coordinate survey, sluice labor, storage, and repair around ancient irrigation.", "adm", CONTROL),
            a("cult_processions", "Cult Processions", "Sequence regalia, offerings, routes, and hospitality for public royal rites.", "dip", PRESTIGE),
            a("scribal_accounts", "Scribal Accounts", "Reconcile weights, stores, grants, and labor through locally appropriate records.", "adm", ADMIN),
            a("frontier_offerings", "Frontier Offerings", "Support boundary sanctuaries and local compacts without asserting uniform doctrine.", "dip", CLERGY),
            a("sanctuary_estate_accounts", "Sanctuary Estate Accounts", "Inventory endowed plots, tenant obligations, offerings, seals, and authorized releases while preserving royal oversight.", "adm", ADMIN + (("global_clergy_estate_power", "0.02"),)),
            a("festival_supply_calendar", "Festival Supply Calendar", "Sequence grain, vessels, garlands, animals, labor, and hospitality so public rites do not empty emergency stores.", "dip", FOOD + (("global_clergy_estate_power", "0.02"),)),
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
        ("antq_client_monarchy", "antq_buffer_kingdom", "antq_regional_kingship", "antq_petition_court", "antq_frontier_muster_monarchy"),
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
            a("provincial_envoy_returns", "Provincial Envoy Returns", "Collate petitions, local judgments, travel conditions, gifts, and urgent warnings carried back from subordinate districts.", "dip", CONTROL + (("global_nobles_estate_power", "0.02"),)),
            a("royal_storehouse_inspection", "Royal Storehouse Inspection", "Check seals, measures, grain quality, tools, arrears, and release orders in the court's principal reserves.", "adm", FOOD + (("global_burghers_estate_power", "0.02"),)),
        ),
        (
            m("tribute_review", "Tribute Register Review", "Reconcile local obligations, court needs, and remittances owed beyond the kingdom.", "Retainer Garrison Petition", "Landed retainers seek clear service and provisioning obligations.", "nobles_estate", ADMIN, NOBLES),
            m("embassy_fund", "Embassy Reception Fund", "Authorize gifts and hospitality without exhausting the court treasury.", "Caravan Security Petition", "Merchant households ask the court to protect approaches, markets, and compensation claims.", "burghers_estate", PRESTIGE, TRADE),
            m("fortress_stores", "Fortress Provisioning Measure", "Set grain, water, missile, and labor reserves for exposed strongholds.", "Sanctuary Endowment Petition", "Cult custodians request protected stores and land for public rites and travelers.", "clergy_estate", LOGISTICS, CLERGY),
        ),
    ),
    Profile(
        "xiongnu", "antq_xiongnu_wing_council", "Xiongnu Wing Council",
        "The chanyu's court coordinates left and right wings, lineage sureties, pasture circuits, envoys, remounts, and prestige-gift distribution.",
        (
            "antq_steppe_confederation", "antq_xiongnu_dual_wing_command",
            "antq_xiongnu_gift_circuit", "antq_xiongnu_southern_frontier_court",
            "antq_xiongnu_northern_western_confederacy",
            "antq_southern_xiongnu_commandery_settlement",
            "antq_xiongnu_five_divisions_order", "antq_han_zhao_chanyu_court",
        ),
        ("tribes_estate", "nobles_estate", "burghers_estate"),
        "xiongnu_chanyu_atlas.png", "f458ad1af8ad185d10fb6eaf9c649231a5c9b69a6310752a7e63c7d4b5258ec9",
        "P8.3;P9;P13;BHR;CAH-XI;IRAN-XIO;XIONGNU-CONFEDERACY", "secure",
        "The wing council is a bounded Xiongnu adapter; it does not import later Mongol titles, decimal ranks, or a permanent representative assembly.",
        (
            a("pasture_returns", "Pasture Circuit Returns", "Reconcile lineage access to seasonal grazing and water before scarcity breaks confederate obligations.", "adm", FOOD),
            a("wing_muster", "Wing Muster Tallies", "Count mounted followings, bows, remounts, and rendezvous points for the left and right wings.", "mil", MIL),
            a("silk_gift_register", "Silk-Gift Register", "Track prestige silk, plaques, vessels, and livestock through the chanyu's negotiated gift hierarchy.", "dip", PRESTIGE),
            a("envoy_relays", "Envoy Relay Circuit", "Coordinate interpreters, escort guarantees, relay mounts, and tallies across distant lineages.", "dip", LOGISTICS),
            a("lineage_sureties", "Lineage Sureties", "Record wards, oath gifts, and witnessed guarantees without treating mobile lineages as salaried offices.", "adm", CONTROL),
            a("chanyu_lineage_nominations", "Chanyu Lineage Nominations", "Review dynastic seniority, eligible royal kinsmen, left-wing standing, maternal alliances, and the sureties attached to succession.", "dip", PRESTIGE),
            a("wing_command_returns", "Wing Command Returns", "Compare the left and right wings' subordinate rulers, mounted followings, pasture access, rendezvous, and gift obligations.", "mil", NOBLES),
            a("frontier_treaty_accounts", "Frontier Treaty Accounts", "Track peace gifts, silk, grain, hostages, envoys, markets, and reciprocal obligations in relations with Han.", "dip", TRADE),
            a("western_tribute_relays", "Western Tribute Relays", "Coordinate tribute, envoys, escorts, remounts, and route intelligence among western subordinate peoples and oasis courts.", "dip", LOGISTICS),
            a("craft_household_stores", "Craft and Household Stores", "Inventory metal fittings, bows, leatherwork, textiles, grain, and dependent-household production needed by court and host.", "adm", MINT),
            a("seasonal_assembly_dockets", "Seasonal Assembly Dockets", "Prepare tribute, oath, sacrifice, justice, marriage, and campaign business for the confederacy's recurring gatherings.", "adm", ASSIZE),
        ),
        (
            m("wing_contribution", "Left-Right Wing Contribution", "Set a bounded mounted contribution and rendezvous for each wing.", "Wing Command Precedence", "Leading commanders demand rank and gift shares proportionate to service.", "nobles_estate", MIL, NOBLES),
            m("pasture_compact", "Seasonal Pasture Compact", "Mediate water and grazing circuits among confederated lineages.", "Herding-Household Water Claim", "Mobile households seek protected seasonal access under prior compact.", "tribes_estate", FOOD, TRIBES),
            m("frontier_exchange", "Frontier Exchange Peace", "Guarantee a supervised meeting place for silk, livestock, and metal exchange.", "Caravan Broker Safe-Conduct", "Long-distance brokers seek escorts and compensation for losses.", "burghers_estate", TRADE, TRADE),
            m("chanyu_succession", "Chanyu Succession Settlement", "Weigh dynastic seniority, royal-lineage claims, wing support, maternal alliances, and hostage guarantees in a contested succession.", "Wing Acclamation Claim", "Leading commanders seek a witnessed role in recognizing a successor while accepting responsibility for confederate unity.", "nobles_estate", PRESTIGE, NOBLES),
            m("wing_appointments", "Wing Appointment Review", "Assign left and right commanders, subordinate rulers, rendezvous, pasture responsibilities, and campaign authority.", "Lineage Command Petition", "Major lineages seek commands proportionate to their following, routes, and remount contribution.", "tribes_estate", MIL, TRIBES),
            m("han_treaty", "Han Frontier Treaty Review", "Set peace gifts, hostages, markets, envoys, frontier restraint, and reciprocal obligations without treating the relationship as simple tribute.", "Frontier Broker Petition", "Interpreters and exchange households seek protected markets, measured tallies, escorts, and compensation.", "burghers_estate", TRADE, TRADE),
            m("western_tribute", "Western Tribute Circuit", "Allocate envoys, escorts, remounts, gifts, and route intelligence among western subordinate peoples and oasis courts.", "Western Lineage Autonomy Claim", "Distant confederates seek retained local rule in return for bounded tribute, host service, and passage.", "tribes_estate", LOGISTICS, TRIBES),
            m("dependent_households", "Craft and Dependent-Household Provision", "Set measured deliveries of metalwork, bows, leather, textiles, grain, and transport without assuming uniform servile status.", "Craft-Household Delivery Petition", "Dependent and specialist households seek stable inputs, witnessed quotas, and protection from repeated requisition.", "burghers_estate", MINT, TRADE),
            m("seasonal_assembly", "Seasonal Assembly Settlement", "Coordinate tribute, oath, sacrifice, justice, marriage alliances, and campaign decisions at a recurring gathering.", "Oath Custodian Petition", "Ritual custodians seek protected vessels, gifts, and a witnessed place in confederate settlements without becoming a centralized priesthood.", "tribes_estate", ASSIZE, TRIBES),
        ),
    ),
    Profile(
        "xianbei", "antq_xianbei_chiefly_assembly", "Xianbei Chiefly Assembly",
        "Eastern-steppe leaders coordinate lineage allegiance, mounted followings, pasture movement, frontier embassies, seasonal gatherings, and compensation before the later Tanshihuai confederation.",
        (
            "antq_xianbei_eastern_confederacy", "antq_tanshihuai_three_divisions",
            "antq_xianbei_successor_federations", "antq_murong_frontier_court",
            "antq_tuoba_dai_confederacy", "antq_rouran_khaganate",
        ),
        ("tribes_estate", "nobles_estate", "burghers_estate"),
        "xianbei_chiefly_council_atlas.png", "d2e1f5e05f34c9ed04ecbca830465b3b96f84fc506a9e0732165c67232c55ac5",
        "P8.8;P9;P13;CAH-XI;CAH-XII;XIANBEI-CONFEDERACY;IRAN-KHAGAN", "contested",
        "The opening profile models separate eastern-steppe Xianbei groups; Tanshihuai's three divisions and later successor federations are dated reforms, not institutions projected back to AD 1.",
        (
            a("lineage_circuit_returns", "Lineage Circuit Returns", "Reconcile eastern-steppe lineages, pasture routes, water, seasonal movement, wards, and gifts without imposing fixed territorial districts.", "adm", FOOD),
            a("mounted_following_returns", "Mounted Following Returns", "Count bows, riders, remounts, harness, scouts, and rendezvous promised by leading households.", "mil", MIL),
            a("frontier_embassies", "Frontier Embassy Tallies", "Coordinate interpreters, gifts, escorts, markets, and intelligence in dealings with Wuhuan, Xiongnu, Han, and northeastern neighbors.", "dip", TRADE),
            a("seasonal_hunt_assemblies", "Seasonal Hunt Assemblies", "Use recurring gatherings and collective hunts to review allegiance, disputes, pasture access, and campaign readiness.", "dip", PRESTIGE),
            a("lineage_compensation", "Lineage Compensation Dockets", "Set witnessed restitution for livestock, pasture, injury, broken guarantees, and failed service among federated groups.", "adm", ASSIZE),
        ),
        (
            m("lineage_federation", "Lineage Federation Hearing", "Define shared allegiance, assembly attendance, wards, gifts, and the retained authority of participating leaders.", "Chiefly Precedence Claim", "Leading households seek precedence proportional to following, seniority, and service while accepting federation obligations.", "nobles_estate", PRESTIGE, NOBLES),
            m("pasture_hunt", "Pasture and Hunt Circuit", "Set seasonal movement, shared hunting grounds, water access, scouts, and protection against overuse.", "Herding Circuit Petition", "Mobile households seek recognized water and grazing routes in return for warning, transport, and remount duties.", "tribes_estate", FOOD, TRIBES),
            m("frontier_exchange", "Eastern Frontier Exchange", "Authorize bounded markets, interpreters, escorts, restitution, and intelligence exchange along the Han and Wuhuan approaches.", "Broker and Artisan Petition", "Exchange and craft households seek stable measures, inputs, safe conduct, and protection from repeated requisition.", "burghers_estate", TRADE, TRADE),
        ),
    ),
    Profile(
        "goguryeo", "antq_goguryeo_royal_council", "Goguryeo Royal Council",
        "The early royal court coordinates senior lineages, walled settlements, grain stores, beacon frontiers, craft obligations, and river-valley labor.",
        ("antq_early_korean_kingdom",), ("nobles_estate", "peasants_estate", "burghers_estate"),
        "goguryeo_court_atlas.png", "4481a1b0e96e1279652ceeb8c59805357479b0ca4de2913deddc812638343973",
        "P8.3;P13;SAM", "secure",
        "The interface is specific to the opening Goguryeo frame but does not project the mature later Three Kingdoms bureaucracy into AD 1.",
        (
            a("fortress_households", "Fortress Household Returns", "Count households, stores, and bounded service around walled river-valley settlements.", "adm", ADMIN),
            a("millet_stores", "Millet Store Accounts", "Review receipts, seed reserves, spoilage, and emergency releases at defended centers.", "adm", FOOD),
            a("beacon_dispatches", "Beacon Frontier Dispatches", "Coordinate watch rotations, signal fuel, arrows, and relief from one fortified node to the next.", "mil", LOGISTICS),
            a("lineage_petitions", "Senior-Lineage Petitions", "Hear witnessed claims over commands, land, compensation, and court precedence.", "dip", CONTROL),
            a("artisan_obligations", "Fortress Artisan Obligations", "Measure iron, tile, pottery, and repair duties among attached specialists and household workshops.", "adm", TRADE),
        ),
        (
            m("fortress_rotation", "Fortress Command Rotation", "Set bounded command and provisioning turns among senior houses.", "Senior-Lineage Command Claim", "Leading houses demand a witnessed share of fortress authority.", "nobles_estate", CONTROL, NOBLES),
            m("grain_reserve", "Millet Reserve Measure", "Protect seed and emergency grain before extraordinary requisition.", "Cultivator Labor Calendar", "Farming households seek service rotations that respect the crop cycle.", "peasants_estate", FOOD, PEASANTS),
            m("craft_supply", "Fortress Craft Supply", "Set iron, tile, vessel, and repair obligations for defended centers.", "Artisan Working-Space Petition", "Specialist households seek protected materials and predictable service.", "burghers_estate", TRADE, TRADE),
        ),
    ),
    Profile(
        "kushite", "antq_meroitic_royal_council", "Meroitic Royal Council",
        "The Meroitic court coordinates royal and provincial lineages, temple stores, Nile contributions, iron and gold workshops, caravans, and desert frontiers.",
        ("antq_kushite_dual_kingship",), ("nobles_estate", "clergy_estate", "burghers_estate"),
        "kushite_court_atlas.png", "a81b2482701dc32fb86f60996c31c7ee3ab27c613dc19c51a271595a0c0ce4e9",
        "P8.5;P11;P13;CAH-XI", "secure",
        "Dual royal authority and administrative categories remain gameplay abstractions; the surviving evidence does not yield a complete formal constitution.",
        (
            a("royal_seals", "Royal Seal Witnesses", "Coordinate witnessed orders and contributions across the royal household and provincial authorities.", "adm", CONTROL),
            a("nile_contributions", "Nile Contribution Measures", "Reconcile grain, livestock, craft, and retained provincial shares without inventing a uniform tax code.", "adm", FOOD),
            a("temple_stores", "Temple Storehouse Audit", "Review endowed stores, offering vessels, and hospitality obligations under royal protection.", "adm", CLERGY),
            a("metalwork_returns", "Iron and Gold Workshop Returns", "Measure charcoal, blooms, tools, ornaments, and exchange obligations around royal centers.", "dip", TRADE),
            a("desert_dispatches", "Desert Route Dispatches", "Maintain guides, wells, bows, and hospitality across exposed northern and eastern routes.", "mil", LOGISTICS),
        ),
        (
            m("provincial_measure", "Provincial Contribution Measure", "Set witnessed regional contributions and retained shares.", "Court-Lineage Precedence Claim", "Royal and provincial houses seek a legible place in contribution and command.", "nobles_estate", ADMIN, NOBLES),
            m("temple_inventory", "Temple Storehouse Inventory", "Review offerings, endowed stores, and public hospitality obligations.", "Temple Endowment Petition", "Cult custodians seek protected resources for rites and maintenance.", "clergy_estate", FOOD, CLERGY),
            m("workshop_terms", "Royal Workshop Terms", "Set material, market, and inspection rules for metal and caravan houses.", "Caravan and Smithing Petition", "Specialist houses seek safe routes and predictable measures.", "burghers_estate", TRADE, TRADE),
        ),
    ),
    Profile(
        "lankan", "antq_anuradhapura_royal_council", "Anuradhapura Royal Council",
        "The Anuradhapura court coordinates regional lineages, monastic endowments, reservoirs, cultivating households, ports, craft exchange, and elephant service.",
        ("antq_lankan_kingdom",), ("nobles_estate", "clergy_estate", "peasants_estate"),
        "lankan_court_atlas.png", "1068194d5ad9aed5375674fa4bd78ef888cc4ec14f7f1f26fbf1addbf4ba946e",
        "P8.4;P11;P13;BHR", "secure",
        "The council models coordination around the opening kingdom; it does not impose later administrative terminology or a uniform island constitution.",
        (
            a("reservoir_accounts", "Reservoir and Sluice Accounts", "Coordinate surveys, water release, silt clearing, and bounded repair labor around tanks.", "adm", CONTROL),
            a("endowment_stores", "Monastic Endowment Stores", "Review donated land receipts, grain, lamps, vessels, and hospitality without making monasteries state offices.", "adm", CLERGY),
            a("port_measures", "Port and Market Measures", "Maintain weights, beads, coins, vessels, and dues at connected exchange points.", "dip", TRADE),
            a("regional_petitions", "Regional Lineage Petitions", "Hear witnessed claims over service, land, water, and royal access.", "dip", PRESTIGE),
            a("elephant_service", "Elephant and Frontier Service", "Register handlers, fodder, ropes, forest routes, and bounded royal service.", "mil", LOGISTICS),
        ),
        (
            m("tank_repairs", "Reservoir Repair Rotation", "Set survey, clearing, sluice, and labor obligations for a bounded waterwork.", "Cultivator Water Calendar", "Farming households seek predictable releases and seasonal labor.", "peasants_estate", CONTROL, PEASANTS),
            m("endowment_review", "Monastic Endowment Review", "Inventory protected gifts and hospitality stores without absorbing them into the palace.", "Monastic Store Petition", "Religious communities request secure vessels, grain, and lamp supplies.", "clergy_estate", CLERGY, CLERGY),
            m("regional_hearing", "Regional Service Hearing", "Reconcile lineage, elephant, road, and reservoir obligations.", "Regional-Lineage Access Claim", "Leading houses request witnessed access to royal judgment.", "nobles_estate", ADMIN, NOBLES),
        ),
    ),
    Profile(
        "armenian", "antq_armenian_royal_council", "Artaxata Royal Council",
        "The contested Artaxiad court coordinates highland dynasts, fortress service, sanctuary interests, royal domains, caravan passes, and diplomacy between Roman and Arsacid powers.",
        ("antq_artaxiad_highland_kingship", "antq_armenian_dynast_compact", "antq_armenian_royal_domain_court"),
        ("nobles_estate", "clergy_estate", "burghers_estate"),
        "armenian_court_atlas.png", "b5fefe53b833b4ba751561ddb0519e403a89a61bc3f949a56485ff5c5a89f928",
        "P8.2;P11;P13;CAH-XI;IRAN-ARM", "contested",
        "Tigranes IV and Erato are retained, but the council is an evidence-bounded interface rather than a recovered Artaxiad constitution or office list.",
        (
            a("highland_fortress_musters", "Highland Fortress Musters", "Reconcile dynastic mounted followings, garrison stores, and bounded service at the highland strongholds.", "mil", MIL),
            a("pass_courier_relays", "Pass Courier Relays", "Maintain horses, bells, sealed dispatches, and safe stages across exposed mountain routes.", "dip", LOGISTICS),
            a("dynastic_arbitration", "Artaxata Dynastic Arbitration", "Use witnessed oaths, precedence, sureties, and compensation to contain disputes among leading houses.", "dip", PRESTIGE),
            a("royal_domain_accounts", "Royal Domain Accounts", "Review grain, wine, livestock, and retained domain obligations without inventing a uniform cadastre.", "adm", ADMIN),
            a("frontier_embassies", "Roman-Arsacid Embassy Reception", "Coordinate gifts, interpreters, guarantees, and precedence under pressure from both imperial frontiers.", "dip", CONTROL),
        ),
        (
            m("fortress_service", "Fortress Service Assessment", "Set bounded garrison, mounted, and provisioning duties among highland dynasts.", "Highland Dynast Command Claim", "Leading houses demand witnessed command shares and limits on extraordinary service.", "nobles_estate", MIL, NOBLES),
            m("sanctuary_review", "Sanctuary Endowment Review", "Inventory vessels, offerings, stores, and protected gifts without centralizing local cults.", "Sanctuary Custodian Petition", "Cult custodians seek secure stores and recognition of locally witnessed obligations.", "clergy_estate", CLERGY, CLERGY),
            m("pass_guarantees", "Caravan Pass Guarantees", "Coordinate escort, compensation, and water obligations on highland exchange routes.", "Caravan and Artisan Safe-Conduct", "Exchange households request predictable passage, measures, and restitution after route losses.", "burghers_estate", LOGISTICS, TRADE),
        ),
    ),
    Profile(
        "nabataean", "antq_nabataean_royal_council", "Petra Royal Council",
        "The court of Aretas IV and Huldu coordinates caravan houses, cisterns and channels, sanctuary stores, customs measures, oasis cultivation, and relations with Rome.",
        ("antq_nabataean_caravan_kingship", "antq_nabataean_water_stewardship", "antq_nabataean_customs_court"),
        ("nobles_estate", "clergy_estate", "burghers_estate"),
        "nabataean_court_atlas.png", "fd2933034aee392cd322bf41a750171f7f34b9c41f731da5ffb6201e274e032a",
        "P8.1;P8.5;P11;P13;OCD;PLE;NABATAEA-MAP", "secure",
        "The named court and importance of exchange and water management are secure; exact council membership and one kingdom-wide administrative code are not claimed.",
        (
            a("cistern_channel_returns", "Cistern and Channel Returns", "Review storage, channel clearing, water release, and measured labor across royal and community works.", "adm", FOOD),
            a("caravan_safe_conducts", "Desert Caravan Safe-Conducts", "Coordinate escorts, watering places, compensation rules, and protected movement between route communities.", "dip", LOGISTICS),
            a("customs_measures", "Customs Measures", "Maintain weights, containers, assessed dues, and exemptions at connected exchange points.", "adm", TRADE),
            a("sanctuary_store_inventories", "Sanctuary and Store Inventories", "Witness offerings, lamps, vessels, and hospitality stores without absorbing sanctuaries into the palace.", "adm", CLERGY),
            a("client_embassies", "Client Embassy Reception", "Manage gifts, interpreters, dynastic standing, and guarantees within the kingdom's Roman relationship.", "dip", PRESTIGE),
        ),
        (
            m("water_rotation", "Cistern Maintenance Rotation", "Set bounded clearing, repair, and distribution duties for a waterwork.", "Oasis Cultivator Water Claim", "Cultivating households request predictable access and seasonal maintenance terms.", "nobles_estate", FOOD, NOBLES),
            m("sanctuary_inventory", "Sanctuary Store Inventory", "Review protected offerings, lamps, incense, and hospitality supplies.", "Sanctuary Custodian Petition", "Cult custodians seek witnessed protection for bounded stores and gifts.", "clergy_estate", CLERGY, CLERGY),
            m("customs_revision", "Caravan Customs Revision", "Balance route security, stable measures, exemptions, and royal receipts.", "Merchant and Artisan Safe-Conduct", "Exchange households request enforceable passage and predictable customs measures.", "burghers_estate", TRADE, TRADE),
        ),
    ),
    Profile(
        "himyarite", "antq_himyarite_royal_council", "Himyarite Highland Council",
        "The highland court coordinates lineage authority, terraces and dams, sanctuary stores, incense routes, Red Sea exchanges, cultivating communities, and bounded levy service.",
        ("antq_himyarite_terrace_kingship", "antq_himyarite_irrigation_court", "antq_himyarite_incense_route_court"),
        ("nobles_estate", "clergy_estate", "burghers_estate"),
        "himyarite_court_atlas.png", "5854e1bf928bae15eca406cc4bddb87a2d513887daadce45fc8f2dab750394aa",
        "P8.5;P8.6;P11;P13;CAH-XI;OCD-HIM;HIMYAR-HIST;OUP-REDSEA", "contested",
        "The anonymous opening ruler and incomplete AD 1 office evidence remain explicit; mechanics use securely important highland, water, incense, port, and lineage contexts.",
        (
            a("terrace_dam_works", "Terrace and Dam Works", "Coordinate fitted masonry, water release, repair labor, and storage around highland cultivation.", "adm", FOOD),
            a("incense_assessments", "Incense Route Assessments", "Review weights, protected routes, pack service, and assessed shares in aromatics exchange.", "dip", TRADE),
            a("red_sea_dispatches", "Red Sea Port Dispatches", "Coordinate amphorae, rope, pilots, cargo measures, and inland movement from western ports.", "dip", LOGISTICS),
            a("sanctuary_inventories", "Sanctuary Store Inventories", "Witness incense, lamps, vessels, and bounded stores without inventing a centralized priesthood.", "adm", CLERGY),
            a("lineage_levy_returns", "Lineage Levy Returns", "Set shields, spears, provisions, and seasons of service among highland lineages.", "mil", MIL),
        ),
        (
            m("terrace_repairs", "Terrace Repair Rotation", "Set bounded masonry, clearing, and water obligations for highland communities.", "Highland Lineage Water Claim", "Leading houses request witnessed shares in water and repair supervision.", "nobles_estate", FOOD, NOBLES),
            m("sanctuary_stores", "Sanctuary Store Review", "Inventory incense, vessels, lamps, and protected hospitality stores.", "Sanctuary Offering Petition", "Cult custodians seek recognized supplies and limits on extraordinary requisition.", "clergy_estate", CLERGY, CLERGY),
            m("incense_passage", "Incense Passage Measure", "Balance assessed dues, escorts, port movement, and compensation on protected routes.", "Incense and Port Safe-Conduct", "Exchange houses ask for stable measures and enforceable protection between highland and coast.", "burghers_estate", TRADE, TRADE),
        ),
    ),
    Profile(
        "satavahana", "antq_satavahana_royal_council", "Deccan Royal Council",
        "The contested Satavahana court coordinates titled regional houses, religious gifts, guild and caravan exchange, inland routes, cultivating communities, waterworks, and elephant service.",
        ("antq_satavahana_deccan_kingship", "antq_satavahana_guild_court", "antq_satavahana_maharathi_compact"),
        ("nobles_estate", "clergy_estate", "burghers_estate"),
        "satavahana_court_atlas.png", "0598aefe1a9e6781a35a836c35cc87a87578082803099c43a39489ef2bb263eb",
        "P8.4;P11;P13;CAH-XI", "contested",
        "Maharathi and mahabhoja titles, donations, routes, and exchange inform a conservative interface; no named AD 1 ruler or uniform Deccan bureaucracy is invented.",
        (
            a("deccan_route_returns", "Deccan Route Returns", "Coordinate water, pack service, beads, textiles, and safe passage between inland exchange centers.", "dip", LOGISTICS),
            a("guild_donation_records", "Guild and Donation Records", "Witness weights, gifts, craft obligations, hospitality, and the customary compacts of exchange households.", "adm", TRADE),
            a("market_measures", "Market Weights and Measures", "Maintain balanced weights, containers, and inspected measures across connected markets.", "adm", ADMIN),
            a("elephant_mounted_musters", "Elephant and Mounted Musters", "Register handlers, harness, fodder, mounted followings, and bounded seasons of service.", "mil", MIL),
            a("tank_irrigation_accounts", "Tank and Irrigation Accounts", "Review water release, silt clearing, repair labor, seed needs, and community shares.", "adm", FOOD),
        ),
        (
            m("regional_service", "Regional Service Assessment", "Set bounded mounted, elephant, route, and provisioning duties for titled houses.", "Maharathi and Mahabhoja Claim", "Regional houses request witnessed precedence and limits on extraordinary service.", "nobles_estate", MIL, NOBLES),
            m("donation_inventory", "Donation and Store Inventory", "Review bounded gifts, vessels, lamps, and hospitality resources of religious communities.", "Monastic and Sanctuary Petition", "Religious communities seek protected gifts without becoming organs of the royal court.", "clergy_estate", CLERGY, CLERGY),
            m("guild_passage", "Guild and Caravan Passage", "Set weights, route protection, compensation, and water obligations for exchange households.", "Guild Safe-Conduct Petition", "Guild and caravan houses request predictable measures and enforceable passage.", "burghers_estate", TRADE, TRADE),
        ),
    ),
    Profile(
        "catuvellaunian", "antq_catuvellaunian_royal_council", "Verlamion Royal Council",
        "The court of Tasciovanus coordinates dynastic mints, oppidum stores, retinues, sacred places, cultivating communities, Channel exchange, and relations among neighboring British peoples.",
        ("antq_catuvellaunian_oppidum_kingship", "antq_catuvellaunian_dynastic_mint_court", "antq_catuvellaunian_oppida_compact"),
        ("nobles_estate", "clergy_estate", "burghers_estate"),
        "catuvellaunian_court_atlas.png", "c494a8e3f8d4d91c3b5ba896b6087d9bc3c94ee56db4ee002fc3e3e3c854c770",
        "P8.7;P11;P13;CAH-XI;BM-DRU", "contested",
        "Tasciovanus and Cunobelinus anchor the opening dynasty, while coinage, oppida, exchange, and retinue mechanics remain bounded interpretations rather than a recovered constitution.",
        (
            a("oppidum_store_returns", "Oppidum Store Returns", "Review grain, livestock, craft stock, and hospitality obligations at fortified settlement centers.", "adm", FOOD),
            a("weight_die_oversight", "Weight and Die Oversight", "Maintain witnessed weights, blank flans, dies, and accountable distribution among the ruler's trusted officers.", "adm", ADMIN),
            a("chariot_retinue_muster", "Chariot and Retinue Muster", "Register vehicles, harness, spears, provisions, and bounded seasons of service among leading households.", "mil", MIL),
            a("channel_exchange_guarantees", "Channel Exchange Guarantees", "Coordinate landing places, measures, escorts, and restitution for cross-Channel and regional exchange.", "dip", TRADE),
            a("sanctuary_assembly_hearing", "Sanctuary Assembly Hearing", "Hear witnessed oaths, offerings, succession claims, and inter-community petitions at recognized gathering places.", "dip", PRESTIGE),
        ),
        (
            m("oppidum_contributions", "Oppidum Contribution Compact", "Set bounded grain, craft, transport, and watch obligations among settlement communities.", "Dynastic and Retinue Precedence", "Leading houses request recognized command shares and limits on extraordinary demands.", "nobles_estate", CONTROL, NOBLES),
            m("sacred_place_review", "Sacred-Place Offering Review", "Inventory bounded vessels, offerings, and hospitality stores without inventing a centralized priesthood.", "Sacred-Place Custodian Petition", "Ritual custodians seek protected stores and witnessed access to royal judgment.", "clergy_estate", CLERGY, CLERGY),
            m("channel_measures", "Channel Exchange Measure", "Balance landing security, weights, restitution, and royal receipts among exchange households.", "Oppidum Craft and Market Claim", "Craft and exchange houses request predictable measures and protected routes.", "burghers_estate", TRADE, TRADE),
        ),
    ),
    Profile(
        "trinovantian", "antq_trinovantian_camulodunon_council", "Camulodunon Council",
        "Dubnovellaunos's Trinovantian court coordinates coin and weight custody, oppidum stores, Channel landings, chariot-retinue service, sacred-place hearings, and relations with neighboring British powers.",
        ("antq_trinovantian_coin_kingship", "antq_trinovantian_oppidum_court", "antq_trinovantian_channel_compact"),
        ("nobles_estate", "burghers_estate", "clergy_estate"),
        "trinovantian_council_atlas.png", "a61d2e41c8e38936b46778b9ea5c1b91efe9b9843d4a36da7cb38c35bcfe8357",
        "P8.7;P11;P13;CAH-XI;CCI-DUB;BM-DRU", "contested",
        "Dubnovellaunos and an AD 1 coin horizon are attested, while the Camulodunon council, exact royal reach, and relationship with neighboring dynasties remain bounded gameplay reconstructions.",
        (
            a("coin_die_returns", "Coin and Die Returns", "Review blank flans, dies, weights, metal stocks, and accountable distribution through the royal storehouse.", "adm", ADMIN),
            a("oppidum_store_returns", "Camulodunon Store Returns", "Reconcile grain, livestock, pottery, craft stock, and hospitality at the principal settlement centers.", "adm", FOOD),
            a("channel_landing_guarantees", "Channel Landing Guarantees", "Maintain landing places, escorts, measures, imported vessels, and restitution for registered cross-Channel exchange.", "dip", TRADE),
            a("chariot_retinue_musters", "Chariot-Retinue Musters", "Count vehicles, harness, spear equipment, provisions, and bounded service among leading households.", "mil", MIL),
            a("sacred_place_hearings", "Sacred-Place Hearings", "Witness succession claims, external oaths, offerings, and inter-community settlements without inventing a centralized priesthood.", "dip", PRESTIGE),
        ),
        (
            m("coin_issue", "Coin-Issue Settlement", "Set bounded metal, die, weight, distribution, and witness duties for a new royal issue.", "Coin-House Precedence", "Leading houses seek recognized access to dies, prestige exchange, and royal judgment.", "nobles_estate", ADMIN, NOBLES),
            m("oppidum_contributions", "Oppidum Contribution Compact", "Set grain, livestock, craft, transport, and watch shares among settlement communities.", "Store and Cultivator Guarantee", "Cultivating households seek measured contributions and emergency access to protected stores.", "peasants_estate", FOOD, PEASANTS),
            m("channel_exchange", "Channel Exchange Measure", "Balance landing security, weights, gifts, restitution, and royal receipts among exchange households.", "Landing-House Safe-Conduct", "Craft and exchange households request protected routes and predictable measures.", "burghers_estate", TRADE, TRADE),
        ),
    ),
    Profile(
        "brigantian", "antq_brigantian_northern_council", "Brigantian Northern Council",
        "Brigantian leading kindreds coordinate hillfort stores, Pennine passage, cattle and grain returns, mounted and chariot service, inter-kindred gifts, and a large but internally varied northern political frame.",
        ("antq_brigantian_hillfort_confederacy", "antq_brigantian_kindred_compact", "antq_brigantian_hillfort_court"),
        ("tribes_estate", "nobles_estate", "peasants_estate"),
        "brigantian_council_atlas.png", "7faef0fd1dddc47a58f8719a06fd8c187358b1c20feab8933923629fe0918246",
        "P8.7;P11;P13;CAH-XI;PLE;PTO-GEO-II2;BRIGANTIA-STANWICK", "contested",
        "The later Brigantian name and large northern frame are secure, but AD 1 unity, Stanwick's political role, council procedure, and any direct continuity to Cartimandua's later court remain uncertain.",
        (
            a("hillfort_store_returns", "Hillfort Store Returns", "Review grain, livestock, pottery, timber, hospitality, and refuge capacity without assuming every enclosure is a permanent capital.", "adm", FOOD),
            a("pennine_passage_watch", "Pennine Passage Watch", "Coordinate ridge paths, river crossings, signals, guides, escorts, and compensation across the northern frame.", "mil", LOGISTICS),
            a("cattle_pasture_reckoning", "Cattle and Pasture Reckoning", "Set seasonal grazing, herd, fodder, grain, and restitution duties among participating communities.", "adm", CONTROL),
            a("mounted_chariot_musters", "Mounted and Chariot Musters", "Count horses, vehicles, harness, spears, provisions, and bounded service among leading households.", "mil", MIL),
            a("kindred_gift_compacts", "Inter-Kindred Gift Compacts", "Witness vessels, torcs, amber, wool, hospitality, sureties, and compensation without inventing a permanent federation.", "dip", PRESTIGE),
        ),
        (
            m("northern_muster", "Northern Muster Compact", "Set mounted, chariot, infantry, route, and provision obligations for a bounded common campaign.", "Leading-Kindred Command Claim", "Prominent households request command precedence and gift shares proportionate to service.", "nobles_estate", MIL, NOBLES),
            m("pasture_peace", "Pasture and Passage Peace", "Set grazing, crossing, compensation, refuge, and warning duties across participating districts.", "Community Autonomy Claim", "Local communities seek retained judgment and limits on extraordinary calls.", "tribes_estate", CONTROL, TRIBES),
            m("hillfort_stores", "Hillfort Store Rotation", "Coordinate grain, livestock, timber, pottery, and hospitality contributions at selected enclosures.", "Household Provision Limit", "Cultivating households demand measured rotations and access during local emergency.", "peasants_estate", FOOD, PEASANTS),
        ),
    ),
    Profile(
        "durotrigian", "antq_durotrigian_hillfort_assembly", "Durotrigian Hillfort Assembly",
        "Durotrigian communities coordinate a distinctive coin, pottery, burial, settlement, coastal-exchange, and hillfort landscape without assuming one recovered capital or unitary written constitution.",
        ("antq_durotrigian_hillfort_coin_order", "antq_durotrigian_coin_weight_council", "antq_durotrigian_settlement_compact"),
        ("nobles_estate", "burghers_estate", "peasants_estate"),
        "durotrigian_council_atlas.png", "9e856bc1deb934c13408ba3e41a0d43a6d0bb54fb8c692958b16f7b3370a4631",
        "P8.7;P11;P13;CAH-XI;PTO-GEO-II2;DUROTRIGES-PROJECT", "contested",
        "The Durotrigian material package of pottery, coinage, burial, settlement, and defended enclosures is unusually distinct; political centralization and occupation of every hillfort remain unproven.",
        (
            a("hillfort_store_returns", "Hillfort and Enclosure Returns", "Review grain, livestock, pottery, timber, refuge, and hospitality at selected enclosures without treating all hillforts as occupied fortresses.", "adm", CONTROL),
            a("coin_weight_returns", "Coin and Weight Returns", "Reconcile small silver issues, blank metal, weights, dies, and distribution without inventing a centralized mint bureau.", "adm", ADMIN),
            a("pottery_craft_measures", "Pottery and Craft Measures", "Maintain clay, firing, spindle, iron-tool, vessel, and exchange standards across a distinctive production landscape.", "dip", TRADE),
            a("burial_custody_hearings", "Burial-Custody Hearings", "Protect grave goods, vessels, mirrors, brooches, and local custodianship without claiming one uniform rite or central priesthood.", "dip", PRESTIGE),
            a("coastal_exchange_returns", "Coastal Exchange Returns", "Review landing places, salt, rope, hides, ceramics, escorts, and restitution along the southern coast.", "mil", LOGISTICS),
        ),
        (
            m("coin_standard", "Durotrigian Coin Standard", "Set bounded metal, weight, die, circulation, and witness duties for local issues.", "Coin and Craft-House Claim", "Exchange and specialist households seek stable weights and protected access to materials.", "burghers_estate", ADMIN, TRADE),
            m("hillfort_contributions", "Enclosure Contribution Compact", "Set grain, livestock, timber, refuge, and watch duties at selected defended places.", "Leading-House Custody Claim", "Prominent households seek bounded command and store oversight without permanent ownership.", "nobles_estate", CONTROL, NOBLES),
            m("field_settlement", "Field and Settlement Rotation", "Coordinate harvest, pottery, transport, cattle, and emergency store shares among rural communities.", "Cultivator Contribution Limit", "Farming households seek measured duties and access to common stores.", "peasants_estate", FOOD, PEASANTS),
        ),
    ),
    Profile(
        "ivernian", "antq_ivernian_regional_gathering", "Ivernian Regional Gathering",
        "Ivernian communities coordinate cattle gifts, seaway and river exchange, ironworking, wetland offerings, hospitality, sureties, and seasonal contributions in a deliberately low-centralization southwest-Irish adapter.",
        ("antq_ivernian_regional_assembly", "antq_ivernian_seaway_compact", "antq_ivernian_cattle_gift_court"),
        ("tribes_estate", "nobles_estate", "clergy_estate"),
        "ivernian_council_atlas.png", "25c00dd1ddc89d18098c79e496393075c68453d59b3725008549a7e3c129409d",
        "P8.7;P11;P13;PTO-GEO-II1;DARCY-IRE;IRON-AGE-IRELAND", "contested",
        "Ptolemy's Iverni are later evidence and the Irish Iron Age settlement record is sparse; the profile avoids medieval Gaelic offices, a royal-site constitution, ogham administration, or false territorial precision.",
        (
            a("seasonal_gathering_returns", "Seasonal Gathering Returns", "Register participating communities, provisions, hospitality, witnesses, sureties, and local disputes without claiming a permanent central assembly.", "adm", ASSIZE),
            a("cattle_gift_returns", "Cattle-Gift Returns", "Track cattle, hides, vessels, wool, hospitality, compensation, and retained household shares under bounded seasonal terms.", "adm", FOOD),
            a("seaway_exchange_guarantees", "Seaway Exchange Guarantees", "Coordinate hide boats, landing places, rope, beads, ceramics, escorts, and restitution without inventing a port bureaucracy.", "dip", TRADE),
            a("iron_smith_contributions", "Iron-Smith Contributions", "Protect bloomery iron, charcoal, tools, unfinished blanks, and specialist exchange under measured obligations.", "mil", LOGISTICS),
            a("wetland_deposition_custody", "Wetland Deposition Custody", "Protect vessels, rings, deposition places, witnesses, and local access without reconstructing one island-wide cult authority.", "dip", PRESTIGE),
        ),
        (
            m("cattle_gifts", "Cattle and Hospitality Compact", "Set bounded cattle, hide, vessel, wool, feast, and compensation shares among participating households.", "Leading-Kin Gift Claim", "Prominent households seek precedence and larger retained shares in return for sureties and armed service.", "nobles_estate", FOOD, NOBLES),
            m("seaway_passage", "Seaway Passage Compact", "Set landing, escort, rope, boat, compensation, and hospitality obligations along regional routes.", "Regional Community Guarantee", "Participating communities seek retained local judgment and predictable passage duties.", "tribes_estate", TRADE, TRIBES),
            m("offering_custody", "Offering-Place Custody", "Protect bounded vessels, rings, access, witnesses, and seasonal peace at recognized deposition places.", "Ritual Custodian Petition", "Local custodians seek protected objects and a witnessed role without becoming a centralized priesthood.", "clergy_estate", PRESTIGE, CLERGY),
        ),
    ),
    Profile(
        "aestian", "antq_aestian_amber_coast_gathering", "Aestian Amber-Coast Gathering",
        "Aestian shore and woodland communities coordinate amber exchange, coastal landings, route watch, household contributions, and local offering custody without assuming one centralized Baltic kingdom.",
        ("antq_aestian_amber_coast_order", "antq_aestian_shore_exchange_compact", "antq_aestian_woodland_assembly"),
        ("tribes_estate", "burghers_estate", "clergy_estate"),
        "aestian_council_atlas.png", "cac9391c02c6bd9d86d3449c5dc434ca404b0ba4f99e91fd77cdd09af3f9d7fb",
        "P8.7;P11;P13;TAC-GER-45;ARCHAEOMETRY-NE-BALTIC", "contested",
        "Tacitus's Aestian description dates to AD 98 and does not recover an AD 1 constitution; amber, coastal exchange, mixed material connections, and plural communities provide the bounded playable frame.",
        (
            a("amber_weight_returns", "Amber and Weight Returns", "Review raw and worked amber, balances, containers, witnesses, and exchange shares without inventing a centralized export office.", "adm", MINT),
            a("coastal_landing_guarantees", "Coastal Landing Guarantees", "Coordinate paddles, rope, landing access, hides, ceramics, escorts, and restitution along the southeastern Baltic shore.", "dip", TRADE),
            a("woodland_shore_watch", "Woodland and Shore Watch", "Set guide, warning, trail, lagoon, and refuge obligations among participating communities.", "mil", LOGISTICS),
            a("household_contribution_stores", "Household Contribution Stores", "Reconcile grain, beeswax, hides, modest iron tools, pottery, and retained household shares.", "adm", FOOD),
            a("offering_place_custody", "Offering-Place Custody", "Protect local vessels, amber beads, tokens, witnesses, and access without reconstructing one Aestian priesthood or cult hierarchy.", "dip", PRESTIGE),
        ),
        (
            m("amber_measure", "Amber Measure Compact", "Set bounded sorting, weight, witness, landing, and exchange obligations for coastal amber.", "Amber-House Safe-Conduct", "Exchange households seek stable measures, protected passage, and enforceable restitution.", "burghers_estate", TRADE, TRADE),
            m("shore_passage", "Shore and Woodland Passage", "Coordinate trails, lagoons, guides, warning signals, refuge, and compensation across participating districts.", "Community Passage Guarantee", "Local communities demand retained judgment and predictable watch obligations.", "tribes_estate", LOGISTICS, TRIBES),
            m("offering_custody", "Local Offering Custody", "Protect bounded vessels, beads, tokens, access, witnesses, and gathering peace.", "Custodian Hearing Claim", "Local ritual custodians seek protected objects and a witnessed hearing role without centralized authority.", "clergy_estate", PRESTIGE, CLERGY),
        ),
    ),
    Profile(
        "frisian", "antq_frisian_terp_assembly", "Frisian Terp Assembly",
        "Frisian salt-marsh communities coordinate terp maintenance, cattle and hide obligations, tidal passage, household stores, and the negotiated Roman frontier without projecting the AD 28 revolt backward.",
        ("antq_frisian_terp_community_order", "antq_frisian_tidal_compact", "antq_frisian_frontier_council"),
        ("tribes_estate", "peasants_estate", "burghers_estate"),
        "frisian_council_atlas.png", "216654b1d02f97182af2509bce83b23ef8b10bf1d7934e6f20cf929b0cc0ea20",
        "P8.7;P11;P13;TAC-ANN-4.72;GRONINGEN-TERP;PALEOHISTORIA-FRISII", "contested",
        "Terp settlement begins centuries before AD 1 and Roman contact is secure from 12 BC; Tacitus's ox-hide crisis is an AD 28 warning about frontier extraction, not an opening revolt or a complete Frisian constitution.",
        (
            a("terp_maintenance_returns", "Terp Maintenance Returns", "Review turf, clay, drainage, timber, basketry, and rotating labor required to sustain salt-marsh settlement mounds.", "adm", PUBLIC_WORKS),
            a("hide_tribute_reckoning", "Cattle and Hide Reckoning", "Set measured cattle, hide, horn, rope, and retained-household shares without imposing the later aurochs-hide abuse.", "adm", CONTROL),
            a("tidal_passage_watch", "Tidal Passage Watch", "Coordinate paddles, rope, reeds, landing access, signals, guides, and coastal warning through changing channels.", "mil", LOGISTICS),
            a("marsh_cattle_stores", "Marsh Household Stores", "Reconcile barley, hides, salt, pottery, fodder, and refuge stocks among terp communities.", "adm", FOOD),
            a("rhine_embassy_dossiers", "Rhine Embassy Dossiers", "Witness gifts, tribute terms, auxiliary service, safe passage, and complaints at the Roman frontier without assuming permanent submission.", "dip", SUBJECTS),
        ),
        (
            m("terp_maintenance", "Terp Maintenance Rotation", "Set bounded turf, clay, timber, drainage, basket, and labor shares among mound communities.", "Terp Community Guarantee", "Participating communities seek retained judgment and predictable maintenance rotations.", "tribes_estate", PUBLIC_WORKS, TRIBES),
            m("hide_tribute", "Hide and Herd Assessment", "Measure cattle, hide, horn, rope, and retained shares under witnessed frontier obligations.", "Marsh Household Limit", "Cattle and cultivating households demand assessments suited to local herds and resources.", "peasants_estate", FOOD, PEASANTS),
            m("frontier_posture", "Rhine Frontier Posture", "Balance embassies, tribute, service, landing rights, warnings, and resistance without scripting the later revolt.", "Tidal Exchange Safe-Conduct", "Coastal exchange households seek protected routes, stable measures, and restitution.", "burghers_estate", CONTROL, TRADE),
        ),
    ),
    Profile(
        "dacian", "antq_dacian_hillfort_council", "Dacian Hillfort Council",
        "The divided post-Burebista Dacian and Getic rulers coordinate selected hillfort stores, metalworking, Carpathian passages, mounted hosts, and external oaths while preserving their separate courts.",
        ("antq_dacian_divided_kingships", "antq_dacian_hillfort_compact", "antq_dacian_mountain_court"),
        ("nobles_estate", "tribes_estate", "burghers_estate"),
        "dacian_council_atlas.png", "90ccb887d6f47f06f248b07317bcf2365fb316492e508b44b302ffbbf5826e60",
        "P8.7;P11;P13;CAH-XI;PLE;STR-GEO-7.3.11", "contested",
        "Strabo reports that Burebista's successors divided power into several states; the profile therefore models negotiated hillfort rulers and material capacities rather than a single AD 1 monarch or a Decebalan state.",
        (
            a("hillfort_store_returns", "Dacian Fortress Store Returns", "Review grain, amphorae, timber, iron fittings, refuge, and hospitality at selected defended centers.", "adm", CONTROL),
            a("iron_silver_accounts", "Iron and Silver Accounts", "Reconcile ore, bloomery iron, silver-bearing material, tools, ingots, weights, and specialist obligations.", "adm", MINT),
            a("carpathian_pass_watch", "Carpathian Pass Watch", "Coordinate trail markers, signals, scouts, timber obstacles, river crossings, and protected supply caches.", "mil", LOGISTICS),
            a("mounted_host_muster", "Mounted Host Muster", "Count bridle fittings, remount obligations, spears, shields, provisions, and bounded campaign service.", "mil", MIL),
            a("sanctuary_oath_hearings", "Sanctuary and Oath Hearings", "Witness vessels, rings, external guarantees, compensation, and local ritual custody without reconstructing one centralized priesthood.", "dip", PRESTIGE),
        ),
        (
            m("rulers_compact", "Hillfort Rulers' Compact", "Set bounded command, refuge, store, route, and compensation obligations among divided regional powers.", "Leading-House Precedence", "Prominent houses seek witnessed command and gift shares without claiming a single crown.", "nobles_estate", CONTROL, NOBLES),
            m("workshop_contributions", "Metal Workshop Contributions", "Set measured ore, fuel, tool, ingot, transport, and retained specialist shares.", "Miner and Smith Safe-Conduct", "Metalworking and exchange households seek protected materials, routes, and compensation.", "burghers_estate", MINT, TRADE),
            m("pass_muster", "Carpathian Pass Muster", "Coordinate scouts, mounted service, stores, signals, guides, and bounded common defense.", "Mountain Community Guarantee", "Pass communities seek retained judgment and limits on extraordinary musters.", "tribes_estate", LOGISTICS, TRIBES),
        ),
    ),
    Profile(
        "garamantian", "antq_garamantian_oasis_council", "Garamantian Oasis Council",
        "Garamantian leading houses coordinate oasis settlements, underground irrigation, caravan passage, field stores, mounted forces, and trans-Saharan exchange across the Fazzan state.",
        ("antq_garamantian_oasis_state", "antq_garamantian_irrigation_court", "antq_garamantian_caravan_compact"),
        ("nobles_estate", "burghers_estate", "peasants_estate"),
        "garamantian_council_atlas.png", "42a86c05372a36a344390343fc93f7af5671fec64d0024f9fe49ffb26fe58fd2",
        "P8.5;P11;P13;CAH-XI;PLE;LEICESTER-TRANSSAHARA;BILNAS-GARAMANTES", "secure",
        "Archaeology securely supports an urbanized oasis state, extensive irrigation, mobility, and long-distance exchange; individual AD 1 rulers and a recovered office hierarchy remain unknown.",
        (
            a("foggara_water_accounts", "Foggara Water Accounts", "Review shafts, underground galleries, lamps, rope, clearing labor, water shares, and repair priorities across oasis communities.", "adm", PUBLIC_WORKS),
            a("oasis_store_returns", "Oasis Store Returns", "Reconcile dates, grain, jars, seed, fodder, irrigation gates, and emergency household access.", "adm", FOOD),
            a("caravan_route_guarantees", "Caravan Route Guarantees", "Coordinate water skins, route stones, guides, pack equipment, beads, restitution, and protected passage.", "dip", TRADE),
            a("mounted_chariot_musters", "Saharan Chariot Musters", "Count bridle fittings, wheel equipment, shields, spears, water, provisions, and bounded desert service.", "mil", MIL),
            a("trans_saharan_exchange_inventory", "Trans-Saharan Exchange Inventory", "Review copper, beads, ivory, cloth, ceramics, weights, and accountable shares without treating exchange as one royal monopoly.", "dip", MINT),
        ),
        (
            m("water_rotation", "Oasis Water Rotation", "Set clearing, shaft, gallery, gate, field, and household water obligations under witnessed rotations.", "Irrigator Share Petition", "Cultivating households demand protected water shares and measured repair labor.", "peasants_estate", PUBLIC_WORKS, PEASANTS),
            m("caravan_passage", "Caravan Passage Compact", "Set water, guide, route, compensation, measure, and landing obligations for long-distance exchange.", "Caravan-House Safe-Conduct", "Exchange households seek protected passage, stable measures, and enforceable restitution.", "burghers_estate", TRADE, TRADE),
            m("oasis_contributions", "Oasis Defense and Store Compact", "Coordinate mounted service, settlement refuge, grain, dates, water skins, and route warning among leading houses.", "Leading-House Command Claim", "Prominent oasis houses seek bounded command and store oversight in return for defense and guarantees.", "nobles_estate", MIL, NOBLES),
        ),
    ),
    Profile(
        "marcomannic", "antq_marcomannic_royal_council", "Marcomannic Royal Council",
        "Maroboduus's Bohemian kingdom coordinates the royal retinue, allied kindreds, settlement stores, iron and amber exchange, sacred custodians, and diplomacy along the Roman frontier.",
        ("antq_marcomannic_bohemian_kingship", "antq_marcomannic_retinue_court", "antq_marcomannic_allied_host_compact"),
        ("nobles_estate", "tribes_estate", "clergy_estate"),
        "marcomannic_court_atlas.png", "c705d1ec9155ea51d91ceb511d517dc379503093254b842a424a09cc695568a4",
        "P8.7;P11;P13;CAH-XI;TAC-GER", "secure",
        "Maroboduus and the organized Marcomannic kingdom are secure; the council models retinue, allied-host, settlement, exchange, and frontier functions without inventing fixed offices.",
        (
            a("bohemian_settlement_returns", "Bohemian Settlement Returns", "Review grain, livestock, ironwork, storage, and hospitality among the kingdom's settlement communities.", "adm", CONTROL),
            a("retinue_gift_muster", "Retinue Gift Muster", "Coordinate arms, fittings, provisions, prestige goods, and service among the king's close followers.", "mil", MIL),
            a("allied_host_contributions", "Allied Host Contributions", "Set bounded warrior, remount, wagon, and supply duties among allied kindreds.", "mil", LOGISTICS),
            a("iron_amber_exchange", "Iron and Amber Exchange", "Protect river and overland exchange while maintaining witnessed weights and compensation customs.", "dip", TRADE),
            a("roman_frontier_envoys", "Roman Frontier Envoys", "Receive interpreters, gifts, guarantees, hostages, and intelligence without reducing the kingdom to Roman dependency.", "dip", PRESTIGE),
        ),
        (
            m("retinue_service", "Royal Retinue Service", "Set arms, gift, hospitality, and campaign expectations for the royal following.", "Retinue Command Claim", "Leading companions request precedence, shares, and limits on extraordinary service.", "nobles_estate", MIL, NOBLES),
            m("allied_host_terms", "Allied Host Compact", "Reconcile settlement, wagon, warrior, and provisioning obligations among allied kindreds.", "Kindred Muster Petition", "Confederated communities seek witnessed quotas and restitution rules.", "tribes_estate", LOGISTICS, PEASANTS),
            m("sacred_oath_review", "Sacred Oath and Store Review", "Protect bounded rite objects, oath gifts, and hospitality stores without inventing a uniform clergy.", "Sacred Custodian Petition", "Ritual custodians request recognized stores and a place in major oath settlements.", "clergy_estate", CLERGY, CLERGY),
        ),
    ),
    Profile(
        "cheruscan", "antq_cheruscan_coalition_assembly", "Cheruscan Coalition Assembly",
        "Cheruscan kindreds coordinate assembly hearings, temporary coalition leadership, retinue gifts, forest passage, compensation, and Roman-frontier policy without assuming a permanent monarchy.",
        ("antq_cheruscan_kindred_assembly", "antq_cheruscan_coalition_leadership", "antq_cheruscan_retinue_kingship"),
        ("tribes_estate", "nobles_estate", "clergy_estate"),
        "cheruscan_coalition_council_atlas.png", "8b2426d5dacd24a05d8a1a06203d1a18b5096051973e7b2f76f2c9c242e7e4c9",
        "P8.7;P9;P11;P13;CAH-XI;TAC-GER;TAC-ANN", "contested",
        "Assembly, retinue, coalition, hostage, compensation, and frontier relationships are bounded from literary and archaeological evidence; no fixed Cheruscan constitution or inevitable Arminian monarchy is asserted.",
        (
            a("kindred_hearings", "Kindred Assembly Hearings", "Sequence speakers, witnesses, precedence, compensation claims, and collective obligations among participating kindreds.", "adm", ASSIZE),
            a("coalition_musters", "Coalition Muster Returns", "Count shields, spears, provisions, scouts, and bounded service pledged to a temporary common campaign.", "mil", MIL),
            a("retinue_gift_returns", "Retinue Gift Returns", "Track arms, fittings, livestock, imported vessels, and hospitality supporting leading warband households.", "dip", PRESTIGE),
            a("forest_passage_scouts", "Forest Passage Scouts", "Coordinate guides, concealed stores, river crossings, warning routes, and restitution for allied passage.", "mil", LOGISTICS),
            a("hostage_oath_settlements", "Hostage and Oath Settlements", "Witness wards, rings, vessels, compensation, and frontier guarantees without treating them as permanent peace.", "dip", CONTROL),
        ),
        (
            m("coalition_leadership", "Coalition War Leadership", "Choose bounded campaign leadership, rendezvous, scouting, and contribution terms without creating a permanent crown.", "Leading-Kindred Command Claim", "Prominent kindreds seek command precedence proportionate to followers, gifts, and service.", "nobles_estate", MIL, NOBLES),
            m("compensation_peace", "Kindred Compensation Peace", "Set cattle, weapons, hospitality, and witness obligations after injury, broken oaths, or disputed passage.", "Assembly Hearing Guarantee", "Participating kindreds demand a public hearing before renewed feud or extraordinary levy.", "tribes_estate", ASSIZE, TRIBES),
            m("frontier_posture", "Roman Frontier Posture", "Balance embassies, hostages, markets, scouts, and resistance without assuming permanent alliance or war.", "Sacred Oath Custody", "Ritual custodians seek protected vessels and a witnessed place in external settlements.", "clergy_estate", CONTROL, CLERGY),
        ),
    ),
    Profile(
        "chattian", "antq_chattian_host_council", "Chattian Host Council",
        "Chattian leaders coordinate a disciplined foot host, chosen-warrior vows, forest fieldworks, settlement provisions, rank, and deliberate campaign timing.",
        ("antq_chattian_host_order", "antq_chattian_elder_war_council", "antq_chattian_chosen_warrior_host"),
        ("tribes_estate", "nobles_estate", "peasants_estate"),
        "chattian_host_council_atlas.png", "84bbc14bc77c3333a7669a85021f87f86fe4718b6e1b456d1d6a632b45699a60",
        "P8.7;P9;P11;P13;CAH-XI;TAC-GER", "contested",
        "Tacitus securely distinguishes Chattian infantry, preparation, selected leaders, baggage, and vowed warriors, but his moralizing account does not recover a complete AD 1 constitution.",
        (
            a("foot_host_musters", "Foot-Host Muster Returns", "Count shields, spears, tools, baggage, provisions, and rendezvous for a deliberately prepared infantry campaign.", "mil", MIL),
            a("chosen_warrior_vows", "Chosen-Warrior Vow Custody", "Record bounded service and hospitality for vowed front-rank warriors without treating a literary custom as universal status.", "dip", PRESTIGE),
            a("forest_fieldworks", "Forest Fieldwork Stores", "Maintain axes, spades, stakes, baskets, warning routes, and night camp works for sustained operations.", "mil", LOGISTICS),
            a("settlement_provisions", "Settlement Provision Returns", "Set measured grain, livestock, wagon, tool, and hospitality duties for the host.", "adm", FOOD),
            a("elder_discipline_hearings", "Elder Discipline Hearings", "Review appointment, rank, timing, compensation, and failures of service before the assembled host.", "adm", ASSIZE),
        ),
        (
            m("host_levy", "Prepared Host Levy", "Set infantry, tool, baggage, and provision obligations for a sustained campaign.", "Commander and Rank Petition", "Chosen leaders seek recognized precedence and obedience for the campaign's bounded duration.", "nobles_estate", MIL, NOBLES),
            m("warrior_vow", "Chosen-Warrior Vow", "Recognize a limited front-rank following and its support obligations without imposing the custom on every household.", "Household Provision Limit", "Settlement communities demand measured support and an end date for exceptional hospitality.", "peasants_estate", PRESTIGE, PEASANTS),
            m("forest_campaign", "Forest Campaign Preparation", "Coordinate fieldworks, scouts, stores, routes, and deliberate timing before crossing a contested frontier.", "District Muster Hearing", "Participating communities seek witnessed quotas, warning duties, and compensation for losses.", "tribes_estate", LOGISTICS, TRIBES),
        ),
    ),
    Profile(
        "batavian", "antq_batavian_island_council", "Batavian Island Council",
        "Batavian island households coordinate Roman-alliance obligations, elite auxiliary service, Rhine crossings, horses, floodbanks, pasture, gifts, and retained local authority.",
        ("antq_batavian_rhine_compact", "antq_batavian_auxiliary_treaty", "antq_batavian_island_assembly"),
        ("nobles_estate", "tribes_estate", "burghers_estate"),
        "batavian_island_council_atlas.png", "03cfeeee8dc748dcd405299a9ca1bddc30d157f42e215f6891df8077f437e331",
        "P8.7;P9;P11;P13;CAH-XI;TAC-GER;TAC-HIST", "secure",
        "Batavian Rhine-island settlement, alliance, tax exemption, and concentrated military service are secure; council procedure and exact AD 1 levy terms remain bounded reconstructions.",
        (
            a("auxiliary_levy_returns", "Auxiliary Levy Returns", "Count selected fighters, equipment, officers, training, and replacement obligations under the Roman alliance.", "mil", MIL),
            a("rhine_crossing_service", "Rhine Crossing Service", "Maintain ferries, ropes, oars, boat clamps, guides, and guarded landing places across the delta.", "mil", LOGISTICS),
            a("horse_swimmer_musters", "Horse and River-Swimmer Musters", "Register horses, harness, waterproof stores, scouts, and specialist crossing service without projecting later unit tables backward.", "mil", NOBLES),
            a("stipend_gift_accounts", "Stipend and Gift Accounts", "Track imported vessels, coin, wool, arms, hospitality, and reciprocal obligations attached to alliance service.", "dip", TRADE),
            a("floodbank_pasture_returns", "Floodbank and Pasture Returns", "Coordinate dikes, revetments, water levels, cattle routes, grain stores, and seasonal communal labor.", "adm", FOOD),
        ),
        (
            m("treaty_levy", "Alliance Levy Compact", "Set selected military service, equipment, command, replacement, and reciprocal protection under the Roman relationship.", "Auxiliary Household Precedence", "Leading service households seek command shares, gifts, and recognized exemptions.", "nobles_estate", MIL, NOBLES),
            m("river_passage", "Rhine Passage Measure", "Guarantee ferries, landing places, escorts, compensation, and accountable movement through the island channels.", "Ferry and Exchange Petition", "Boat, horse, and exchange households seek stable access and measured obligations.", "burghers_estate", LOGISTICS, TRADE),
            m("island_labor", "Island Waterwork Rotation", "Set bounded floodbank, pasture, warning, and store duties among island communities.", "Island Community Guarantee", "Local communities seek predictable labor rotations and retained authority over shared water and pasture.", "tribes_estate", FOOD, TRIBES),
        ),
    ),
    Profile(
        "semnonian", "antq_semnonian_grove_assembly", "Semnonian Grove Assembly",
        "Semnonian district delegates coordinate the sacred-grove gathering, a large confederate muster, oath peace, Elbe and amber exchange, provisions, and Suebian affiliate guarantees.",
        ("antq_semnonian_sacred_confederacy", "antq_semnonian_grove_delegation", "antq_semnonian_district_muster"),
        ("clergy_estate", "tribes_estate", "nobles_estate"),
        "semnonian_grove_council_atlas.png", "0c0fd4584af69ec59c7141105f9f6f25e97993fc70042399b0d00dff9c06b80b",
        "P8.7;P9;P11;P13;CAH-XI;TAC-GER", "contested",
        "Tacitus securely reports Semnonian precedence, numerous districts, and a delegated sacred-grove gathering; exact numbers, ritual procedure, and permanent political authority remain uncertain.",
        (
            a("grove_delegations", "Sacred-Grove Delegations", "Register participating districts, hospitality, protected objects, oath witnesses, and an assembly peace without inventing a centralized priesthood.", "adm", CLERGY),
            a("district_muster_returns", "District Muster Returns", "Count shields, spears, leaders, provisions, and bounded service among the many participating districts.", "mil", MIL),
            a("oath_peace_custody", "Oath-Peace Custody", "Protect the gathering's temporary peace, witnesses, compensation, and inter-district guarantees.", "dip", CONTROL),
            a("elbe_amber_exchange", "Elbe and Amber Exchange", "Maintain river passage, raw amber, weights, cloth exchange, escorts, and restitution without claiming a royal monopoly.", "dip", TRADE),
            a("seasonal_provision_returns", "Seasonal Provision Returns", "Set grain, livestock, pottery, basketry, and hospitality contributions for delegations and host.", "adm", FOOD),
        ),
        (
            m("grove_assembly", "Sacred-Grove Assembly", "Set delegation, peace, offering, hospitality, and witness obligations for a bounded common gathering.", "Grove Custodian Petition", "Ritual custodians seek protected objects and authority to preserve the assembly peace.", "clergy_estate", CLERGY, CLERGY),
            m("district_muster", "Confederate District Muster", "Set shields, spears, provisions, leaders, and rendezvous among participating districts.", "War-Leader Precedence", "Leading retinue households seek command and gift shares proportionate to service.", "nobles_estate", MIL, NOBLES),
            m("affiliate_guarantees", "Suebian Affiliate Guarantees", "Exchange witnesses, rings, passage, compensation, and bounded aid while preserving local leadership.", "District Autonomy Claim", "Participating communities demand retained local judgment and limits on extraordinary calls.", "tribes_estate", CONTROL, TRIBES),
        ),
    ),
    Profile(
        "sabaean", "antq_sabaean_royal_council", "Ma'rib Royal Council",
        "The anonymous Sabaean court coordinates the Ma'rib dam and canals, sanctuary stores, incense caravans, highland cultivation, levy service, and exchanges linking the interior and Red Sea.",
        ("antq_sabaean_marib_kingship", "antq_sabaean_irrigation_court", "antq_sabaean_sanctuary_route_court"),
        ("peasants_estate", "clergy_estate", "burghers_estate"),
        "sabaean_court_atlas.png", "9684aed9c1c4e0fe6b8be86d9450aef656828d9ec0496d2e3877009e4e7e0e3f",
        "P8.5;P8.6;P11;P13;CAH-XI;UNESCO-SABA;UNESCO-INCENSE", "contested",
        "The opening ruler remains explicitly anonymous; securely important Ma'rib waterworks, sanctuaries, highland cultivation, and incense exchange ground a conservative council adapter.",
        (
            a("marib_dam_canal_returns", "Ma'rib Dam and Canal Returns", "Review masonry, silt clearing, water release, storage, and bounded community labor around the oasis system.", "adm", FOOD),
            a("incense_caravan_dispatches", "Incense Caravan Dispatches", "Coordinate pack service, water, escorts, assessed shares, and compensation across inland routes.", "dip", TRADE),
            a("sanctuary_inventory_returns", "Sanctuary Inventory Returns", "Witness incense, vessels, lamps, gifts, and hospitality stores without inventing a centralized priesthood.", "adm", CLERGY),
            a("highland_levy_returns", "Highland Levy Returns", "Set shields, spears, provisions, signals, and bounded service among regional lineages.", "mil", MIL),
            a("red_sea_embassy_measures", "Red Sea Embassy Measures", "Coordinate port gifts, interpreters, amphorae, rope, and inland forwarding for diplomatic and commercial visitors.", "dip", LOGISTICS),
        ),
        (
            m("waterwork_rotation", "Ma'rib Waterwork Rotation", "Set bounded masonry, clearing, water-allocation, and labor duties around dam and canal communities.", "Cultivator Water Calendar", "Cultivating communities request predictable releases and seasonal repair obligations.", "peasants_estate", FOOD, PEASANTS),
            m("sanctuary_stores", "Sanctuary Offering Inventory", "Review protected incense, vessels, lamps, gifts, and hospitality stores.", "Sanctuary Custodian Petition", "Cult custodians seek recognized supplies and limits on extraordinary requisition.", "clergy_estate", CLERGY, CLERGY),
            m("incense_routes", "Incense Route Measure", "Balance weights, escorts, water, assessed shares, and compensation along protected routes.", "Caravan Safe-Conduct Petition", "Caravan and craft households request stable measures and enforceable passage.", "burghers_estate", TRADE, TRADE),
        ),
    ),
    Profile(
        "mauretanian", "antq_mauretanian_royal_council", "Caesarea Royal Council",
        "The court of Juba II and Cleopatra Selene coordinates royal estates, civic and port returns, Mediterranean diplomacy, craft and coin measures, mounted frontier service, and regional communities.",
        ("antq_mauretanian_client_kingship", "antq_mauretanian_urban_court", "antq_mauretanian_frontier_compact"),
        ("nobles_estate", "burghers_estate", "tribes_estate"),
        "mauretanian_court_atlas.png", "c3069e9e2dd659e71981eb1d66e29f740b30761d67d63bd16bacfd95b323e976",
        "P8.1;P8.5;P11;P13;CAH-XI;OCD;OCD-PTO", "secure",
        "The named royal couple and client relationship are secure; this profile avoids both a uniform 'Romanized' state and a recovered Mauretanian constitutional office list.",
        (
            a("civic_port_returns", "Civic and Port Returns", "Review cargo measures, landing obligations, workshops, storage, and civic petitions at connected royal centers.", "adm", TRADE),
            a("royal_estate_accounts", "Royal Estate Accounts", "Review grain, olives, vines, livestock, and retained-domain service without inventing a uniform cadastre.", "adm", FOOD),
            a("mounted_frontier_muster", "Mounted Frontier Muster", "Register horses, tack, spears, rations, guides, and bounded seasons of regional service.", "mil", MIL),
            a("mediterranean_embassies", "Mediterranean Embassy Reception", "Coordinate interpreters, gifts, dynastic standing, and Roman guarantees while preserving local royal agency.", "dip", PRESTIGE),
            a("craft_coin_measures", "Craft and Coin Measures", "Maintain balances, weights, blank flans, dies, ceramic measures, and accountable workshops.", "adm", ADMIN),
        ),
        (
            m("royal_domain_review", "Royal-Domain Review", "Set bounded estate, contribution, and service terms among court and regional houses.", "Court and Regional House Claim", "Leading houses request witnessed precedence and limits on extraordinary royal demands.", "nobles_estate", ADMIN, NOBLES),
            m("port_craft_measures", "Port and Craft Measure", "Balance landing security, stable weights, workshop duties, and royal receipts.", "Port and Craft Petition", "Exchange and specialist households seek predictable measures and protected movement.", "burghers_estate", TRADE, TRADE),
            m("frontier_watch_terms", "Frontier Watch Rotation", "Set bounded mounted, guide, signal, and provisioning duties among frontier communities.", "Frontier Community Compact", "Regional communities request recognized rotations, water access, and restitution.", "tribes_estate", LOGISTICS, PEASANTS),
        ),
    ),
    Profile(
        "judean", "antq_judean_ethnarchic_council", "Jerusalem Ethnarchic Council",
        "Herod Archelaus's court coordinates Herodian domains, Second Temple stores, local assessments, waterworks, roads, markets, and obligations under Roman patronage.",
        ("antq_herodian_judean_ethnarchy", "antq_judean_temple_court", "antq_judean_toparchy_compact"),
        ("nobles_estate", "clergy_estate", "burghers_estate"),
        "judean_court_atlas.png", "f2a277b1544b0bf1a6a189bb40e43b06eacfc8cfa39544cff05160a23d347b92",
        "P8.1;P11;P13;OCD;JOS-SAL", "secure",
        "The named ethnarch and Temple's importance are secure; council, assessment, and waterwork interfaces remain bounded gameplay abstractions rather than a reconstructed Judean constitution.",
        (
            a("temple_store_accounts", "Second Temple Store Accounts", "Witness offering vessels, grain, oil, incense, and protected stores without turning the priesthood into a royal department.", "adm", CLERGY),
            a("toparchy_assessments", "Toparchy and Land Assessments", "Reconcile local measures, cultivating households, Herodian domains, and bounded contributions.", "adm", ADMIN),
            a("cistern_waterwork_returns", "Cistern and Waterwork Returns", "Coordinate channels, cisterns, masonry, and seasonal repair without claiming one centralized hydraulic office.", "adm", FOOD),
            a("pilgrim_market_peace", "Pilgrim Road and Market Peace", "Protect roads, guest traffic, measures, and restitution around Jerusalem and regional markets.", "dip", TRADE),
            a("roman_embassy_returns", "Roman Embassy Returns", "Prepare interpreters, guarantees, gifts, petitions, and assessed obligations for the patron court.", "dip", PRESTIGE),
        ),
        (
            m("temple_store_review", "Second Temple Store Review", "Inventory protected offerings, supplies, and hospitality stores without absorbing them into the royal household.", "Priestly Custodian Petition", "Temple custodians request stable inventories and limits on extraordinary requisition.", "clergy_estate", CLERGY, CLERGY),
            m("toparchy_assessment", "Toparchy Assessment", "Set bounded local, domain, market, and road obligations under witnessed measures.", "Regional-House Hearing", "Herodian and regional houses request a hearing before assessments and service terms change.", "nobles_estate", ADMIN, NOBLES),
            m("pilgrim_market_order", "Pilgrim and Market Order", "Coordinate safe passage, measures, water access, and compensation during major traffic.", "Merchant and Artisan Petition", "Exchange households seek predictable measures and enforceable road peace.", "burghers_estate", TRADE, TRADE),
        ),
    ),
    Profile(
        "cappadocian", "antq_cappadocian_royal_council", "Tyana Royal Council",
        "King Archelaus's court coordinates royal domains, sanctuaries, mountain passes, caravan movement, highland cavalry, cultivation, and relations with Rome.",
        ("antq_cappadocian_client_kingship", "antq_cappadocian_domain_court", "antq_cappadocian_pass_compact"),
        ("nobles_estate", "clergy_estate", "burghers_estate"),
        "cappadocian_court_atlas.png", "48e4d137998b4e8be8a64f8c3bd345953a92202e89601af694319d15a87e3ce9",
        "P8.1;P11;P13;OCD;PLE", "secure",
        "Archelaus's client kingship is secure; the profile does not claim a recovered Cappadocian cadastre, office hierarchy, or uniform sanctuary administration.",
        (
            a("royal_domain_returns", "Royal Domain Returns", "Review grain, vines, wool, livestock, and retained obligations without inventing a uniform survey.", "adm", FOOD),
            a("mountain_pass_couriers", "Mountain-Pass Couriers", "Maintain relay animals, sealed dispatches, lamps, guides, and road restitution across highland routes.", "dip", LOGISTICS),
            a("sanctuary_store_returns", "Sanctuary Store Returns", "Witness offerings, lamps, grain, textiles, and protected hospitality without centralizing every cult.", "adm", CLERGY),
            a("highland_cavalry_muster", "Highland Cavalry Muster", "Register horses, tack, shields, spear fittings, feed, and bounded seasons of service.", "mil", MIL),
            a("roman_client_embassies", "Roman Client Embassies", "Coordinate interpreters, gifts, guarantees, petitions, and dynastic standing with the patron court.", "dip", PRESTIGE),
        ),
        (
            m("domain_assessment", "Royal-Domain Assessment", "Set bounded domain receipts, transport, and cultivating obligations.", "Dynastic and Estate-House Claim", "Leading houses request witnessed possession and limits on extraordinary service.", "nobles_estate", ADMIN, NOBLES),
            m("sanctuary_inventory", "Sanctuary Inventory", "Review protected offerings, grain, oil, and hospitality stores.", "Sanctuary Custodian Petition", "Cult custodians seek recognized stores and predictable requisition limits.", "clergy_estate", CLERGY, CLERGY),
            m("pass_safe_conduct", "Mountain-Pass Safe-Conduct", "Set relay, escort, guide, and compensation terms across highland routes.", "Caravan and Craft Petition", "Caravan and artisan households seek secure stages and stable measures.", "burghers_estate", LOGISTICS, TRADE),
        ),
    ),
    Profile(
        "thracian", "antq_thracian_royal_council", "Sapaean Royal Council",
        "Rhoemetalces's client court coordinates dynastic claims, retinue and horse service, mountain passes, grain and timber contributions, sanctuaries, and Greek city petitions.",
        ("antq_odrysian_client_kingship", "antq_thracian_dynastic_court", "antq_thracian_mountain_host"),
        ("nobles_estate", "burghers_estate", "tribes_estate"),
        "thracian_court_atlas.png", "38574bde669d8fa3a3c38d674a1a39060f6e76241abd315d333711619203273a",
        "P8.1;P11;P13;OCD;TAC-THR;MGL-THR", "contested",
        "The named Sapaean court and later succession actors are secure, while Pythodoris's start role and any unified administrative hierarchy remain explicitly contested.",
        (
            a("dynastic_claim_hearings", "Dynastic Claim Hearings", "Witness precedence, oaths, seals, and compensation without pre-scripting the later partition.", "adm", PRESTIGE),
            a("mountain_pass_watch", "Mountain-Pass Watch", "Coordinate guides, signals, water, road repair, and bounded watch rotations.", "dip", LOGISTICS),
            a("horse_retinue_musters", "Horse and Retinue Musters", "Register mounts, tack, shields, spear fittings, feed, and seasonal service.", "mil", MIL),
            a("grain_timber_returns", "Grain, Timber, and Pastoral Returns", "Review grain, wool, timber, livestock, and wagon obligations through measured contributions.", "adm", FOOD),
            a("aegean_pontic_petitions", "Aegean and Pontic City Petitions", "Hear market, harbor, measure, sanctuary, and road claims from connected cities.", "dip", TRADE),
        ),
        (
            m("dynastic_hearing", "Sapaean Dynastic Hearing", "Set witnessed precedence and bounded service without deciding the later succession in advance.", "Royal and Retinue House Claim", "Leading houses request recognized access and compensation for service.", "nobles_estate", PRESTIGE, NOBLES),
            m("city_measure_review", "City and Harbor Measure Review", "Balance stable measures, route security, and royal receipts.", "Aegean and Pontic City Petition", "Urban and exchange households seek predictable dues and protected movement.", "burghers_estate", TRADE, TRADE),
            m("mountain_watch_rotation", "Mountain Watch Rotation", "Set bounded guide, signal, horse, and provisioning duties among regional communities.", "Mountain Community Compact", "Regional communities request recognized rotations, water access, and restitution.", "tribes_estate", LOGISTICS, TRIBES),
        ),
    ),
    Profile(
        "bosporan", "antq_bosporan_royal_council", "Bosporan Royal Council",
        "The contested Bosporan court coordinates royal seals, grain exports, polis petitions, strait security, sanctuaries, and mounted frontier relationships across the Cimmerian Bosporus.",
        ("antq_bosporan_client_kingship", "antq_bosporan_polis_court", "antq_bosporan_steppe_compact"),
        ("nobles_estate", "burghers_estate", "tribes_estate"),
        "bosporan_court_atlas.png", "c443b4ed68a09e3ddcdf05754e8625c7b3a00819a253c32dd8f3d3b35c3c65d3",
        "P8.1;P11;P13;OCD;PLE;ZAV-ASP", "contested",
        "Dynamis remains the plan's contested start anchor and Aspurgus a living claimant; none of the council mechanics settles the disputed accession or invents a complete Bosporan constitution.",
        (
            a("succession_seal_custody", "Succession and Seal Custody", "Witness seals, keys, petitions, and royal grants without resolving the disputed accession through mechanics.", "adm", PRESTIGE),
            a("grain_export_measures", "Grain Export Measures", "Review measures, amphorae, storage, transport loss, and protected export obligations.", "adm", FOOD),
            a("strait_harbor_watch", "Strait and Harbor Watch", "Coordinate ropes, lamps, harbor gear, pilots, and bounded patrol or repair obligations.", "mil", LOGISTICS),
            a("polis_market_petitions", "Polis and Market Petitions", "Hear claims over weights, storage, sanctuary property, roads, and local magistracies.", "dip", TRADE),
            a("steppe_frontier_compacts", "Steppe Frontier Compacts", "Coordinate mounted service, gifts, pasture access, escorts, and restitution with frontier groups.", "dip", MIL),
        ),
        (
            m("royal_seal_hearing", "Royal Seal Hearing", "Set witnessed custody for grants and petitions without deciding the contested succession.", "Royal and Claimant-House Petition", "Court houses demand recognized access, guarantees, and service terms.", "nobles_estate", PRESTIGE, NOBLES),
            m("grain_harbor_measure", "Grain and Harbor Measure", "Balance storage, export, strait security, and royal receipts.", "Polis and Harbor Petition", "Urban and exchange houses seek stable measures and protected shipping.", "burghers_estate", TRADE, TRADE),
            m("steppe_frontier_terms", "Steppe Frontier Terms", "Set bounded mounted, escort, gift, and pasture obligations.", "Frontier Community Compact", "Mounted and pastoral communities request recognized access and restitution.", "tribes_estate", MIL, TRIBES),
        ),
    ),
    Profile(
        "galilean", "antq_galilean_tetrarchic_council", "Sepphoris Tetrarchic Council",
        "Herod Antipas's court coordinates Herodian domains, lake fisheries, Galilean and Peraean roads, market measures, ritual stores, cultivation, and obligations under Roman patronage.",
        ("antq_herodian_galilean_tetrarchy", "antq_galilean_lake_court", "antq_galilean_peraean_compact"),
        ("nobles_estate", "clergy_estate", "burghers_estate"),
        "galilean_court_atlas.png", "36c8991e57906b049c5a1fe67b6c475dbae2045405e018d8f3e2ea977e0dca4d",
        "P8.1;P11;P13;OCD;JOS-SAL", "secure",
        "Antipas's tetrarchy is secure; fishery, market, domain, ritual, and road interfaces are bounded gameplay functions rather than a reconstructed Galilean constitution.",
        (
            a("lake_fishery_returns", "Lake Fishery Returns", "Review boats, nets, landing places, preserved fish, measured shares, and restitution without inventing one royal fishing monopoly.", "adm", FOOD),
            a("peraean_road_dispatches", "Peraean Road Dispatches", "Coordinate guides, lamps, water, repairs, pack service, and compensation across the Jordanian routes.", "dip", LOGISTICS),
            a("market_measure_returns", "Market Measure Returns", "Inspect balances, jars, baskets, fish measures, and bounded dues at connected settlements.", "adm", TRADE),
            a("domain_olive_grain_accounts", "Domain Olive and Grain Accounts", "Review Herodian estates, olives, grain, storage, and cultivating obligations under witnessed measures.", "adm", ADMIN),
            a("roman_patron_petitions", "Roman Patron Petitions", "Prepare interpreters, gifts, guarantees, fiscal petitions, and dynastic standing for the patron court.", "dip", PRESTIGE),
        ),
        (
            m("domain_assessment", "Herodian Domain Assessment", "Set bounded estate, cultivation, transport, and market obligations.", "Regional-House Hearing", "Herodian and regional houses request witnessed possession and limits on extraordinary demands.", "nobles_estate", ADMIN, NOBLES),
            m("ritual_store_review", "Ritual Store Review", "Witness protected lamps, vessels, oil, grain, and hospitality stores.", "Ritual Custodian Petition", "Religious custodians request predictable inventories and requisition limits.", "clergy_estate", CLERGY, CLERGY),
            m("lake_market_measure", "Lake and Market Measure", "Balance fishery access, safe landing, stable measures, and court receipts.", "Fisher and Market Petition", "Fishery, craft, and exchange households seek predictable dues and restitution.", "burghers_estate", TRADE, TRADE),
        ),
    ),
    Profile(
        "batanean", "antq_batanean_tetrarchic_council", "Panias Tetrarchic Council",
        "Philip's northern Herodian court coordinates basalt settlements, cisterns, highland routes, sanctuary stores, cultivation, pastoral service, and frontier obligations under Roman patronage.",
        ("antq_herodian_batanean_tetrarchy", "antq_batanean_highland_court", "antq_batanean_frontier_compact"),
        ("nobles_estate", "clergy_estate", "tribes_estate"),
        "batanean_court_atlas.png", "e167dc00c22889c9d35ddfc344b4d9c9276bfb8afcdec63028b9ed62f5120f56",
        "P8.1;P11;P13;OCD", "secure",
        "Philip's tetrarchy is secure; basalt, cistern, sanctuary, highland, and frontier interfaces remain conservative adapters rather than a recovered Batanean office hierarchy.",
        (
            a("basalt_cistern_returns", "Basalt and Cistern Returns", "Coordinate masonry, jars, cistern clearing, measured water access, and bounded settlement labor.", "adm", FOOD),
            a("highland_route_watch", "Highland Route Watch", "Maintain guides, cairns, signals, lamps, road repairs, and restitution across northern routes.", "dip", LOGISTICS),
            a("sanctuary_store_returns", "Panias Sanctuary Store Returns", "Witness lamps, offerings, vessels, textiles, and protected hospitality without centralizing every cult.", "adm", CLERGY),
            a("horse_frontier_muster", "Horse and Frontier Muster", "Register mounts, tack, spear fittings, feed, guides, and bounded seasons of service.", "mil", MIL),
            a("roman_client_embassies", "Batanaean Frontier Embassies", "Coordinate interpreters, guarantees, petitions, gifts, and tetrarchic standing with the patron court.", "dip", PRESTIGE),
        ),
        (
            m("highland_house_service", "Highland-House Service", "Set witnessed possession, hospitality, horse, and route duties among leading houses.", "Highland-House Petition", "Leading households seek recognized precedence and bounded service terms.", "nobles_estate", ADMIN, NOBLES),
            m("sanctuary_inventory", "Northern Sanctuary Inventory", "Review protected vessels, lamps, offerings, textiles, and guest supplies.", "Sanctuary Custodian Petition", "Cult custodians request stable stores and limits on extraordinary requisition.", "clergy_estate", CLERGY, CLERGY),
            m("frontier_rotation", "Mountain Frontier Rotation", "Set bounded guide, signal, water, horse, and watch obligations.", "Frontier Community Compact", "Highland communities seek recognized rotations, water access, and restitution.", "tribes_estate", LOGISTICS, TRIBES),
        ),
    ),
    Profile(
        "commagenean", "antq_commagenean_royal_council", "Samosata Royal Council",
        "Antiochus III's court coordinates royal and dynastic houses, Euphrates crossings, sanctuaries, highland cavalry, orchards, cultivation, and diplomacy between Rome and Arsacid Iran.",
        ("antq_commagenean_client_kingship", "antq_commagenean_sanctuary_court", "antq_commagenean_euphrates_compact"),
        ("nobles_estate", "clergy_estate", "burghers_estate"),
        "commagenean_court_atlas.png", "6c266ebc2c50dd94e1f52a1a5d2bfd406c2cf138af4a5d64924d9359c6bf2122",
        "P8.1;P11;P13;OCD;BM-COM", "secure",
        "Antiochus III and Commagene's client setting are secure; the exact court, sanctuary, ferry, and highland competences remain bounded reconstructions.",
        (
            a("royal_domain_returns", "Commagenean Domain Returns", "Review orchards, grain, vines, storage, and bounded cultivating obligations without inventing a uniform cadastre.", "adm", FOOD),
            a("euphrates_ferry_measures", "Euphrates Ferry Measures", "Coordinate ropes, boats, pilots, weights, landing stores, assessed passage, and restitution.", "dip", TRADE),
            a("sanctuary_inventory_returns", "Nemrud Sanctuary Inventories", "Witness offerings, incense, lamps, vessels, and hospitality without projecting one centralized priesthood.", "adm", CLERGY),
            a("highland_cavalry_muster", "Commagenean Cavalry Muster", "Register horses, tack, scale fittings, spears, feed, and bounded seasonal service.", "mil", MIL),
            a("roman_arsacid_embassies", "Roman and Arsacid Embassies", "Coordinate interpreters, gifts, guarantees, hostages, and dynastic standing between neighboring powers.", "dip", PRESTIGE),
        ),
        (
            m("dynastic_domain_hearing", "Dynastic Domain Hearing", "Set witnessed possession, contribution, and mounted-service terms among royal and highland houses.", "Highland Dynast Petition", "Leading houses request recognized precedence and bounded royal demands.", "nobles_estate", ADMIN, NOBLES),
            m("sanctuary_inventory", "Commagenean Sanctuary Inventory", "Review protected offerings, vessels, lamps, incense, and guest stores.", "Sanctuary Custodian Petition", "Cult custodians seek stable inventories and requisition limits.", "clergy_estate", CLERGY, CLERGY),
            m("euphrates_passage", "Euphrates Passage Measure", "Balance ferry safety, stable weights, landing obligations, and court receipts.", "Ferry and Merchant Petition", "River and exchange households seek predictable dues and enforceable restitution.", "burghers_estate", TRADE, TRADE),
        ),
    ),
    Profile(
        "emesan", "antq_emesan_dynastic_council", "Emesan Dynastic Council",
        "Iamblichus II's Sampsigeramid court coordinates dynastic households, sanctuary stores, Orontes routes, caravan and textile exchange, mounted service, cultivation, and Roman patronage.",
        ("antq_emesan_client_dynasty", "antq_emesan_sanctuary_court", "antq_emesan_caravan_compact"),
        ("nobles_estate", "clergy_estate", "burghers_estate"),
        "emesan_court_atlas.png", "4853471711798ca4eb0a2422e81435e4b66a7b8cc58f2b47037a5105f63dc21b",
        "P8.1;P11;P13;OCD;PLE;LBD-EME", "contested",
        "Iamblichus II's AD 1 court is secure, while the later descent line and exact sanctuary, caravan, military, and urban office hierarchy remain explicitly contested.",
        (
            a("sanctuary_store_returns", "Emesan Sanctuary Returns", "Witness lamps, incense, vessels, textiles, offerings, and hospitality without inventing a complete priestly administration.", "adm", CLERGY),
            a("orontes_caravan_dispatches", "Orontes Caravan Dispatches", "Coordinate pack service, amphorae, rope, water, escorts, weights, and compensation along connected routes.", "dip", LOGISTICS),
            a("mounted_retinue_muster", "Mounted Retinue Muster", "Register horses, tack, arrows, spear fittings, feed, gifts, and bounded seasons of service.", "mil", MIL),
            a("city_textile_measures", "City and Textile Measures", "Inspect dyed wool, balances, jars, workshop obligations, storage, and bounded market dues.", "adm", TRADE),
            a("roman_patron_embassies", "Roman Patron Embassies", "Prepare interpreters, gifts, guarantees, petitions, and dynastic standing for Roman-facing diplomacy.", "dip", PRESTIGE),
        ),
        (
            m("dynastic_house_hearing", "Sampsigeramid House Hearing", "Set witnessed access, possession, hospitality, and mounted-service terms among court houses.", "Dynastic-House Petition", "Royal and regional houses request precedence and limits on extraordinary service.", "nobles_estate", PRESTIGE, NOBLES),
            m("sanctuary_stores", "Emesan Sanctuary Stores", "Review protected lamps, incense, offerings, vessels, textiles, and guest supplies.", "Sanctuary Custodian Petition", "Cult custodians request recognized stores and predictable requisition limits.", "clergy_estate", CLERGY, CLERGY),
            m("caravan_city_measures", "Caravan and City Measures", "Balance route security, workshop measures, market dues, and court receipts.", "Caravan and Artisan Petition", "Exchange and specialist households seek secure passage and stable measures.", "burghers_estate", TRADE, TRADE),
        ),
    ),
)

# M6 owns the complete opening-reform registry. Keep bespoke successor reforms
# declared beside their councils, but merge every later-added regional opening
# reform into the same authoritative profile so small states cannot silently
# lose all cabinet programmes when the government catalogue expands.
PROFILES = tuple(
    replace(
        profile,
        reforms=tuple(dict.fromkeys(PROFILE_BASE_REFORMS.get(profile.slug, ()) + profile.reforms)),
    )
    for profile in PROFILES
)

COUNCIL_DYNAMICS: dict[str, tuple[str, tuple[tuple[str, str], ...]]] = {
    "roman": (
        "0.10",
        (("nobles_estate", "0.25"), ("burghers_estate", "0.15"), ("clergy_estate", "0.05")),
    ),
    "late_roman": (
        "0.08",
        (("nobles_estate", "0.18"), ("clergy_estate", "0.16"), ("burghers_estate", "0.12")),
    ),
    "han": (
        "0.15",
        (("nobles_estate", "0.10"), ("burghers_estate", "0.20"), ("peasants_estate", "-0.10")),
    ),
    "late_han": (
        "0.08",
        (("nobles_estate", "0.18"), ("burghers_estate", "0.12"), ("clergy_estate", "0.16")),
    ),
    "iranian": (
        "0.05",
        (("nobles_estate", "0.30"), ("clergy_estate", "0.10"), ("burghers_estate", "-0.05")),
    ),
    "sasanian": (
        "0.12",
        (("nobles_estate", "0.22"), ("clergy_estate", "0.18"), ("burghers_estate", "0.08")),
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
    "xiongnu": (
        "0.05",
        (("tribes_estate", "0.35"), ("nobles_estate", "0.20"), ("burghers_estate", "-0.05")),
    ),
    "xianbei": (
        "0.08",
        (("tribes_estate", "0.30"), ("nobles_estate", "0.18"), ("burghers_estate", "0.02")),
    ),
    "goguryeo": (
        "0.10",
        (("nobles_estate", "0.25"), ("peasants_estate", "0.10"), ("burghers_estate", "0.05")),
    ),
    "kushite": (
        "0.10",
        (("nobles_estate", "0.15"), ("clergy_estate", "0.25"), ("burghers_estate", "0.05")),
    ),
    "lankan": (
        "0.10",
        (("nobles_estate", "0.15"), ("clergy_estate", "0.20"), ("peasants_estate", "0.10")),
    ),
    "armenian": (
        "0.05",
        (("nobles_estate", "0.25"), ("clergy_estate", "0.05"), ("burghers_estate", "0.10")),
    ),
    "nabataean": (
        "0.15",
        (("nobles_estate", "0.10"), ("clergy_estate", "0.05"), ("burghers_estate", "0.25")),
    ),
    "himyarite": (
        "0.05",
        (("nobles_estate", "0.20"), ("clergy_estate", "0.10"), ("burghers_estate", "0.15")),
    ),
    "satavahana": (
        "0.10",
        (("nobles_estate", "0.20"), ("clergy_estate", "0.10"), ("burghers_estate", "0.15")),
    ),
    "catuvellaunian": (
        "0.10",
        (("nobles_estate", "0.22"), ("clergy_estate", "0.08"), ("burghers_estate", "0.12")),
    ),
    "trinovantian": (
        "0.10",
        (("nobles_estate", "0.22"), ("burghers_estate", "0.16"), ("clergy_estate", "0.08")),
    ),
    "brigantian": (
        "0.05",
        (("tribes_estate", "0.24"), ("nobles_estate", "0.20"), ("peasants_estate", "0.12")),
    ),
    "durotrigian": (
        "0.05",
        (("nobles_estate", "0.16"), ("burghers_estate", "0.18"), ("peasants_estate", "0.14")),
    ),
    "ivernian": (
        "0.00",
        (("tribes_estate", "0.28"), ("nobles_estate", "0.14"), ("clergy_estate", "0.12")),
    ),
    "aestian": (
        "0.00",
        (("tribes_estate", "0.26"), ("burghers_estate", "0.18"), ("clergy_estate", "0.10")),
    ),
    "frisian": (
        "0.05",
        (("tribes_estate", "0.22"), ("peasants_estate", "0.18"), ("burghers_estate", "0.14")),
    ),
    "dacian": (
        "0.05",
        (("nobles_estate", "0.24"), ("tribes_estate", "0.18"), ("burghers_estate", "0.12")),
    ),
    "garamantian": (
        "0.10",
        (("nobles_estate", "0.20"), ("burghers_estate", "0.18"), ("peasants_estate", "0.14")),
    ),
    "marcomannic": (
        "0.05",
        (("nobles_estate", "0.22"), ("tribes_estate", "0.28"), ("clergy_estate", "0.03")),
    ),
    "cheruscan": (
        "0.05",
        (("tribes_estate", "0.28"), ("nobles_estate", "0.22"), ("clergy_estate", "0.08")),
    ),
    "chattian": (
        "0.05",
        (("tribes_estate", "0.20"), ("nobles_estate", "0.28"), ("peasants_estate", "0.08")),
    ),
    "batavian": (
        "0.10",
        (("nobles_estate", "0.24"), ("tribes_estate", "0.14"), ("burghers_estate", "0.16")),
    ),
    "semnonian": (
        "0.05",
        (("clergy_estate", "0.30"), ("tribes_estate", "0.22"), ("nobles_estate", "0.12")),
    ),
    "sabaean": (
        "0.10",
        (("peasants_estate", "0.18"), ("clergy_estate", "0.12"), ("burghers_estate", "0.20")),
    ),
    "mauretanian": (
        "0.15",
        (("nobles_estate", "0.16"), ("burghers_estate", "0.14"), ("tribes_estate", "0.06")),
    ),
    "judean": (
        "0.10",
        (("nobles_estate", "0.14"), ("clergy_estate", "0.22"), ("burghers_estate", "0.10")),
    ),
    "cappadocian": (
        "0.10",
        (("nobles_estate", "0.20"), ("clergy_estate", "0.08"), ("burghers_estate", "0.12")),
    ),
    "thracian": (
        "0.05",
        (("nobles_estate", "0.22"), ("burghers_estate", "0.10"), ("tribes_estate", "0.16")),
    ),
    "bosporan": (
        "0.10",
        (("nobles_estate", "0.16"), ("burghers_estate", "0.20"), ("tribes_estate", "0.12")),
    ),
    "galilean": (
        "0.10",
        (("nobles_estate", "0.14"), ("clergy_estate", "0.12"), ("burghers_estate", "0.18")),
    ),
    "batanean": (
        "0.10",
        (("nobles_estate", "0.16"), ("clergy_estate", "0.10"), ("tribes_estate", "0.18")),
    ),
    "commagenean": (
        "0.10",
        (("nobles_estate", "0.20"), ("clergy_estate", "0.12"), ("burghers_estate", "0.12")),
    ),
    "emesan": (
        "0.10",
        (("nobles_estate", "0.18"), ("clergy_estate", "0.16"), ("burghers_estate", "0.14")),
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
    lines = ["# Generated by tools/s2_ancient_politics.py --write.", "# Profile-locked ancient administrative programmes."]
    for profile in PROFILES:
        for action in profile.actions:
            key = f"antq_{profile.slug}_{action.slug}"
            lines.extend(("", f"{key} = {{", f"\tability = {action.ability}", "\tpotential = {"))
            lines.extend(reform_trigger(profile.reforms))
            lines.extend((
                "\t}",
                "\tallow_multiple = no",
                "\tai_will_do = {",
                "\t\tvalue = 1",
                "\t}",
                "\tcountry_modifier = {",
            ))
            lines.extend(modifier_lines(action.modifiers, "\t\t"))
            lines.extend(("\t}", "}"))
    small_reforms = tuple(dict.fromkeys(
        reform
        for profile in PROFILES
        if profile.slug in SMALL_STATE_PROFILE_SLUGS
        for reform in profile.reforms
    ))
    for pack, programme in all_programmes():
        key = action_key(pack, programme)
        lines.extend(("", f"{key} = {{", f"\tability = {programme.ability}", "\tpotential = {"))
        lines.extend(reform_trigger(small_reforms))
        lines.append("\t\tOR = {")
        lines.extend(
            f"\t\t\tdominant_culture ?= {{ has_culture_group = culture_group:{group} }}"
            for group in pack.culture_groups
        )
        lines.extend((
            "\t\t}",
            "\t}",
            "\tallow_multiple = no",
            "\tai_will_do = {",
            "\t\tvalue = 1",
            "\t}",
            "\tcountry_modifier = {",
        ))
        lines.extend(modifier_lines(programme.modifiers, "\t\t"))
        lines.extend(("\t}", "}"))
    return "\n".join(lines) + "\n"


def parliament_issues() -> str:
    lines = ["# Generated by tools/s2_ancient_politics.py --write.", "# Council debates with profile-specific outcomes."]
    for profile in PROFILES:
        for motion in profile.motions:
            key = f"antq_issue_{profile.slug}_{motion.slug}"
            modifier = f"{key}_outcome"
            lines.extend((
                "", f"{key} = {{", f"\testate = {motion.estate}",
                "\tmodifier_when_in_debate = {", "\t\tcountry_cabinet_efficiency = 0.01", "\t}",
                "\tallow = {", f"\t\tparliament_type = parliament_type:{profile.parliament}", "\t}",
                "\tchance = {", "\t\tadd = {", "\t\t\tif = {", "\t\t\t\tlimit = {",
                f"\t\t\t\t\tparliament_type = parliament_type:{profile.parliament}",
                "\t\t\t\t}", "\t\t\t\tvalue = 1", "\t\t\t}",
                "\t\t\telse = { value = 0 }", "\t\t}", "\t}", "\ton_debate_passed = {",
                f"\t\tadd_country_modifier = {{ modifier = {modifier} years = 10 mode = add_and_extend }}",
                "\t}", "\ton_debate_failed = { parliament_debate_failed_effect = yes }", "}",
            ))
    return "\n".join(lines) + "\n"


def parliament_agendas() -> str:
    lines = ["# Generated by tools/s2_ancient_politics.py --write.", "# Estate requests tied to actual ancient council profiles."]
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
            issue_modifier = f"{issue}_outcome"
            agenda_modifier = f"{agenda}_concession"
            settlement_name = (
                motion.issue_name
                if motion.issue_name.lower().endswith(" settlement")
                else f"{motion.issue_name} Settlement"
            )
            concession_name = (
                motion.agenda_name
                if motion.agenda_name.lower().endswith(" concession")
                else f"{motion.agenda_name} Concession"
            )
            lines.extend((
                f' {issue}: "{q(motion.issue_name)}"',
                f' {issue}_desc: "{q(motion.issue_description)}"',
                f' {issue_modifier}: "{q(settlement_name)}"',
                f' {issue}_outcome_desc: "The council has enacted its reviewed settlement for a limited term."',
                f' STATIC_MODIFIER_NAME_{issue_modifier}: "${issue_modifier}$"',
                f' STATIC_MODIFIER_DESC_{issue_modifier}: "${issue_modifier}_desc$"',
                f' {agenda}: "{q(motion.agenda_name)}"',
                f' {agenda}_desc: "{q(motion.agenda_description)}"',
                f' {agenda_modifier}: "{q(concession_name)}"',
                f" {agenda}_concession_desc: \"The court or council has accepted this interest group's bounded request.\"",
                f' STATIC_MODIFIER_NAME_{agenda_modifier}: "${agenda_modifier}$"',
                f' STATIC_MODIFIER_DESC_{agenda_modifier}: "${agenda_modifier}_desc$"',
            ))
    for pack, programme in all_programmes():
        key = action_key(pack, programme)
        lines.extend((
            f' {key}: "{q(programme.name)}"',
            f' {key}_desc: "{q(programme.description)}"',
            f' {key}_action: "{q(programme.name)}"',
            f' {key}_active: "Administering {q(programme.name)}"',
            f' {key}_action_progress: "In progress"',
            f' {key}_action_progress_wordier: "{q(programme.name)}: in progress"',
            f' {key}_action_progress_long_wordier: "{q(programme.name)}: administrative programme in progress"',
            f' {key}_action_progress_tooltip: "{q(programme.description)}"',
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
    for pack, programme in all_programmes():
        rows.append((
            "cabinet_action", action_key(pack, programme), f"regional_{pack.slug}",
            programme.name, programme.description, programme.source, programme.confidence, programme.note,
        ))
    return csv_text(("category", "key", "profile", "name", "description", "source", "confidence", "note"), rows)


def art_records() -> list[tuple[str, str, Profile, int]]:
    records: list[tuple[str, str, Profile, int]] = []
    for profile in PROFILES:
        records.append(("parliament_type", profile.parliament, profile, 0))
        records.extend(("cabinet_action", f"antq_{profile.slug}_{action.slug}", profile, index) for index, action in enumerate(profile.actions, 1))
    tribal = next(profile for profile in PROFILES if profile.slug == "tribal")
    for pack in REGIONAL_PACKS:
        records.extend(
            ("cabinet_action", action_key(pack, programme), tribal, cell)
            for cell, programme in enumerate(pack.programmes)
        )
    return records


ART_SOURCE_OVERRIDES: dict[str, tuple[str, str, int]] = {
    f"antq_roman_{slug}": (
        "roman_state_offices_ii_atlas.png",
        "44cd5ed49cdf7b2c31f7f8744db2424335f0d80e531b624dec9d1c606b822a6a",
        cell,
    )
    for cell, slug in enumerate((
        "imperial_correspondence",
        "provincial_assize_returns",
        "public_works_curators",
        "mint_assay_accounts",
        "client_king_dossiers",
        "fleet_supply_returns",
    ))
}
ART_SOURCE_OVERRIDES.update({
    f"antq_han_{slug}": (
        "han_state_offices_ii_atlas.png",
        "b74874ce120568b763746a7c0ae809318885e4ee9ff918e5c524237e9d376e95",
        cell,
    )
    for cell, slug in enumerate((
        "three_excellencies_reviews",
        "nine_ministers_dockets",
        "regional_inspector_reports",
        "household_registration_returns",
        "salt_iron_accounts",
        "grand_herald_guest_registers",
    ))
})
ART_SOURCE_OVERRIDES.update({
    key: (sheet, digest, cell)
    for sheet, digest, keys in (
        (
            "small_state_programmes_01.png",
            "7424a09449823235bc0c3051587a7dee5406ae3152c0a66d61393f18201b1562",
            (
                "antq_civic_ward_assessment_returns",
                "antq_civic_harbor_market_arbitration",
                "antq_gana_clan_seat_rotation",
                "antq_gana_irrigation_labor_registers",
            ),
        ),
        (
            "small_state_programmes_02.png",
            "d288ea77e1f5a45f701f175a0dfe78745548f035471394048d76a59d7706a1a2",
            (
                "antq_steppe_pasture_circuit_tallies",
                "antq_steppe_remount_herd_levies",
                "antq_tribal_seasonal_subsistence_round",
                "antq_tribal_intercommunity_envoys",
            ),
        ),
        (
            "small_state_programmes_03.png",
            "a46bf3282ccff4315d28f7bb5e7bd852caaaa2a8ee929182b1abc5c2dfe50257",
            (
                "antq_sacral_sanctuary_estate_accounts",
                "antq_sacral_festival_supply_calendar",
                "antq_royal_provincial_envoy_returns",
                "antq_royal_royal_storehouse_inspection",
            ),
        ),
    )
    for cell, key in enumerate(keys)
})
ART_SOURCE_OVERRIDES.update({
    action_key(pack, programme): (pack.sheet, SHEET_HASHES[pack.sheet], cell)
    for pack in REGIONAL_PACKS
    for cell, programme in enumerate(pack.programmes)
})
ART_SOURCE_OVERRIDES.update({
    f"antq_xiongnu_{slug}": (
        "xiongnu_state_offices_ii_atlas.png",
        "ce9be47311990f525ae76b0665903e94017e3aadbd41c14ad39844f587d75fcd",
        cell,
    )
    for cell, slug in enumerate((
        "chanyu_lineage_nominations",
        "wing_command_returns",
        "frontier_treaty_accounts",
        "western_tribute_relays",
        "craft_household_stores",
        "seasonal_assembly_dockets",
    ))
})
ART_SOURCE_OVERRIDES.update({
    f"antq_iranian_{slug}": (
        "arsacid_state_offices_ii_atlas.png",
        "48c033de6c0ecf548d271007dd1fac131af723a5a3324e26e3955d2e98875330",
        cell,
    )
    for cell, slug in enumerate((
        "dynastic_succession_dockets",
        "subkingdom_tribute_returns",
        "royal_domain_accounts",
        "mounted_host_registers",
        "river_caravan_customs",
        "hostage_oath_registers",
    ))
})


def art_source_contract(
    key: str, profile: Profile, default_cell: int,
) -> tuple[str, str, int, str]:
    source_file, source_hash, cell = ART_SOURCE_OVERRIDES.get(
        key, (profile.source_file, profile.source_hash, default_cell)
    )
    layout = (
        "four_up_chroma"
        if source_file.startswith(("small_state_programmes_", "regional_programmes_"))
        else "six_up_painting"
    )
    return source_file, source_hash, cell, layout


def master_path(key: str) -> Path:
    return MASTERS / f"{key}_128.png"


def texture_path(category: str, key: str) -> Path:
    folder = "parliament_types" if category == "parliament_type" else "cabinet_actions"
    return ROOT / f"main_menu/gfx/interface/icons/{folder}/{key}.dds"


def art_ledger() -> str:
    rows = []
    for category, key, profile, cell in art_records():
        source_file, source_hash, source_cell, layout = art_source_contract(key, profile, cell)
        rows.append((
            category, key, profile.slug, f"assets_queue/politics/sources/{source_file}",
            source_hash, str(source_cell), layout, master_path(key).relative_to(ROOT).as_posix(),
            texture_path(category, key).relative_to(ROOT).as_posix(), "128x128 BC7 sRGBA + full mip chain",
        ))
    return csv_text(("category", "key", "profile", "source", "source_sha256", "cell", "source_layout", "master", "texture", "contract"), rows)


def installed_game_root() -> Path:
    """Return the installed data root used by deterministic compatibility mirrors."""
    config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
    return Path(config["game_dir"]) / "game"


def cabinet_gui() -> str:
    """Mirror the installed cabinet card with its invalid data-context call repaired.

    The installed widget sets the surrounding data context to ``Cabinet`` but then
    invokes ``GetActionProgressLongWordier`` through ``CabinetItem``.  Active
    administrative programmes consequently flood error.log whenever the card is
    refreshed without an incidental CabinetItem context.  Engine data-type docs
    expose this method on Cabinet, so retain the installed UI byte-for-byte apart
    from that single receiver correction.
    """
    source = installed_game_root() / CABINET_GUI_RELATIVE
    raw = source.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != CABINET_GUI_SOURCE_SHA256:
        raise ValueError(
            f"installed cabinet GUI hash drift: expected {CABINET_GUI_SOURCE_SHA256}, got {digest}"
        )
    text = raw.decode("utf-8-sig")
    if text.count(CABINET_GUI_BAD_CONTEXT) != 1:
        raise ValueError("installed cabinet GUI no longer has exactly one unsafe progress receiver")
    if CABINET_GUI_SAFE_CONTEXT in text:
        raise ValueError("installed cabinet GUI unexpectedly already contains the safe progress receiver")
    return text.replace(CABINET_GUI_BAD_CONTEXT, CABINET_GUI_SAFE_CONTEXT, 1)


def expected_files() -> dict[Path, str]:
    outputs = {
        TYPE_OUT: parliament_types(),
        CABINET_OUT: cabinet_actions(),
        ISSUE_OUT: parliament_issues(),
        AGENDA_OUT: parliament_agendas(),
        MODIFIER_OUT: static_modifiers(),
        CONTENT_LEDGER: content_ledger(),
        ART_LEDGER: art_ledger(),
        CABINET_GUI_OUT: cabinet_gui(),
    }
    for language in ("english", *M2_MIRROR_LANGUAGES):
        outputs[ROOT / f"main_menu/localization/{language}/antq_s2_politics_l_{language}.yml"] = localization(language)
        outputs[ROOT / f"main_menu/localization/{language}/zz_antq_s2_ui_l_{language}.yml"] = ui_localization(language)
    return outputs


def build_art() -> None:
    MASTERS.mkdir(parents=True, exist_ok=True)
    for category, key, profile, cell in art_records():
        source_file, source_hash, source_cell, layout = art_source_contract(key, profile, cell)
        source = SOURCES / source_file
        if hashlib.sha256(source.read_bytes()).hexdigest() != source_hash:
            raise ValueError(f"source hash drift: {source.relative_to(ROOT)}")
        with Image.open(source) as image:
            if layout == "six_up_painting":
                if image.size != (1536, 1024):
                    raise ValueError(f"{source.relative_to(ROOT)} must be 1536x1024")
                x, y = (source_cell % 3) * 512, (source_cell // 3) * 512
                rendered = image.convert("RGB").crop((x + 8, y + 8, x + 504, y + 504)).resize((128, 128), Image.Resampling.LANCZOS)
            else:
                if image.width != image.height or image.width % 2:
                    raise ValueError(f"{source.relative_to(ROOT)} must be a square four-up atlas")
                half = image.width // 2
                x, y = (source_cell % 2) * half, (source_cell // 2) * half
                rendered = magenta_cutout(image.crop((x, y, x + half, y + half)))
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
    expected_counts = {
        "parliament_type": len(PROFILES),
        "cabinet_action": sum(len(profile.actions) for profile in PROFILES) + len(all_programmes()),
        "parliament_issue": sum(len(profile.motions) for profile in PROFILES),
        "parliament_agenda": sum(len(profile.motions) for profile in PROFILES),
    }
    rendered_actions = cabinet_actions()
    rendered_issues = parliament_issues()
    rendered_cabinet_gui = cabinet_gui()
    if CABINET_GUI_BAD_CONTEXT in rendered_cabinet_gui:
        failures.append("cabinet GUI retains the invalid CabinetItem progress receiver")
    if rendered_cabinet_gui.count(CABINET_GUI_SAFE_CONTEXT) != 1:
        failures.append("cabinet GUI does not contain exactly one context-safe Cabinet progress receiver")
    action_count = expected_counts["cabinet_action"]
    if "ai_will_do = { base =" in rendered_actions:
        failures.append("cabinet-action AI uses invalid modifier-style base syntax")
    if rendered_actions.count("\tai_will_do = {\n\t\tvalue = 1\n\t}") != action_count:
        failures.append("cabinet actions do not all use the installed effect-script AI contract")
    issue_count = expected_counts["parliament_issue"]
    if rendered_issues.count("\t\t\telse = { value = 0 }\n") != issue_count:
        failures.append("parliament issues do not all zero-weight mismatched council profiles")
    for profile in PROFILES:
        expected = sum(
            len(candidate.motions)
            for candidate in PROFILES
            if candidate.parliament == profile.parliament
        )
        actual = rendered_issues.count(
            f"\t\t\t\t\tparliament_type = parliament_type:{profile.parliament}\n"
        )
        if actual != expected:
            failures.append(
                f"parliament issue AI profile weight coverage differs for {profile.slug}: "
                f"expected {expected}, found {actual}"
            )
    if counts != expected_counts:
        failures.append(f"content counts differ: {counts}")
    if len({row["key"] for row in rows}) != len(rows):
        failures.append("duplicate ancient-politics content key")
    if any(len(row["description"]) < 55 for row in rows):
        failures.append("an ancient-politics description is too shallow")
    if set(COUNCIL_DYNAMICS) != {profile.slug for profile in PROFILES}:
        failures.append("council political dynamics do not cover exactly the installed profiles")
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
    for source_file, source_hash, _cell in ART_SOURCE_OVERRIDES.values():
        source = SOURCES / source_file
        if not source.is_file():
            failures.append(f"missing source atlas: {source.relative_to(ROOT)}")
        elif hashlib.sha256(source.read_bytes()).hexdigest() != source_hash:
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
    count = len(PROFILES)
    action_count = sum(len(profile.actions) for profile in PROFILES)
    motion_count = sum(len(profile.motions) for profile in PROFILES)
    art_count = len(art_records())
    print(
        f"s2_ancient_politics: PASS ({count} councils; {action_count} cabinet actions; "
        f"{motion_count} issues; {motion_count} agendas; {art_count} direct icons)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
