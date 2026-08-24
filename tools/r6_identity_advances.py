#!/usr/bin/env python3
"""Exact-polity knowledge paths added after the sixth manual playtest."""

from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class IdentityPath:
    design_tag: str
    engine_tag: str
    polity: str
    profile: str
    tracks: tuple[str, str, str]
    names: tuple[str, ...]
    effects: tuple[tuple[str, str], tuple[str, str], tuple[str, str]]
    unit: str
    building: str
    source: str


@dataclass(frozen=True)
class CulturePath:
    culture: str
    culture_name: str
    profile: str
    tracks: tuple[str, str, str]
    names: tuple[str, ...]
    effects: tuple[tuple[str, str], tuple[str, str], tuple[str, str]]
    source: str


PATHS = (
    IdentityPath("ROM", "XAA", "Roman", "roman_italic", ("statecraft", "warfare", "statecraft"),
        ("Augustan Provincial Correspondence", "Aerarium and Fiscus Accounts", "Cursus Publicus Dispatches", "Legionary Vexillation Doctrine", "Danubian Fleet Logistics", "Imperial Armoury Standards", "Diocletianic Provincial Dioceses", "Notitia Command Registers", "Western Prefectural Administration"),
        (("country_cabinet_efficiency", "0.005"), ("global_monthly_control", "0.00025"), ("army_logistics_distance_modifier", "0.025")), "antq_legionaries", "antq_reg_forum_basilica", "P8.1;P15;CAH-XI;CAH-XII"),
    IdentityPath("HAN", "XAR", "Han", "han_east_asian", ("statecraft", "learning", "warfare"),
        ("Commandery Merit Registers", "Salt and Iron Memorials", "Imperial Courier Tallies", "Taixue Classics Curriculum", "Court Astronomers' Bureau", "Paper Archive Offices", "Tuntian Military Settlements", "Northern Garrison Granaries", "Three Kingdoms Field Manuals"),
        (("research_speed_modifier", "0.005"), ("global_monthly_literacy", "0.002"), ("global_manpower_modifier", "0.01")), "antq_han_crossbow_infantry", "antq_reg_silk_loom", "P8.3;P15;CAH-XI;CAH-XII"),
    IdentityPath("PAR", "XAH", "Parthian", "iranian", ("warfare", "exchange", "statecraft"),
        ("Arsacid Remount Estates", "Parthian Shot Rotations", "Noble Cataphract Reserves", "Ctesiphon Caravan Customs", "Caspian Gate Convoys", "Drachm Mint Assays", "Great House Hostages", "Satrapal Royal Judges", "King of Kings Chancery"),
        (("army_maintenance_efficiency", "0.005"), ("land_morale_modifier", "0.005"), ("trade_range_modifier", "0.01")), "antq_parthian_horse_archers", "antq_reg_scale_armoury", "P8.2;P15;CAH-XI;CAH-XII"),
    IdentityPath("ARM", "XAO", "Armenian", "iranian", ("statecraft", "warfare", "learning"),
        ("Nakharar Service Compacts", "Artaxiad Highland Courts", "Armenian Pass Toll Registers", "Ayrudzi Noble Musters", "Caucasus Beacon Chains", "Mountain Fortress Magazines", "Armenian Scriptoria", "Bilingual Court Archives", "Highland Ecclesiastical Schools"),
        (("global_monthly_control", "0.0002"), ("levy_recovery_modifier", "0.0075"), ("research_speed_modifier", "0.004")), "antq_armenian_horse", "antq_reg_stationer", "P8.2;P15;CAH-XI;OCD-ARM"),
    IdentityPath("JUD", "JUD", "Judean", "near_eastern", ("statecraft", "society", "learning"),
        ("Temple Treasury Accounts", "Sanhedrin Petition Procedure", "Pilgrimage Road Wardens", "Diaspora Relief Collections", "Synagogue Community Councils", "Rabbinic Legal Deliberation", "Mishnah Compilation Circles", "Academy Correspondence", "Late Antique Hebrew Commentary"),
        (("stability_cost_efficiency", "0.0075"), ("global_disease_resistance", "0.0025"), ("global_monthly_literacy", "0.002")), "antq_syrian_archers", "antq_reg_scroll_workshop", "P8.5;P15;CAH-XI;CAH-XII"),
    IdentityPath("AKS", "AKS", "Aksumite", "nile_north_african", ("exchange", "warfare", "statecraft"),
        ("Adulis Customs Brokers", "Red Sea Monsoon Schedules", "Highland Ivory Caravans", "Aksumite Spear Retinues", "Escarpment Supply Depots", "Red Sea Patrol Stations", "Aksumite Coin Standards", "Ge'ez Royal Inscriptions", "Highland Provincial Courts"),
        (("trade_range_modifier", "0.0125"), ("global_manpower_modifier", "0.0075"), ("country_cabinet_efficiency", "0.004")), "antq_red_sea_sewn_patrol", "antq_reg_ivory_carver", "P8.5;P15;PER;CAH-XI"),
    IdentityPath("YUE", "YUE", "Yuezhi-Kushan", "inner_asian_steppe", ("warfare", "exchange", "society"),
        ("Yabghu Mounted Retinues", "Bactrian Remount Markets", "Kushan Armoured Cavalry", "Bactrian Gold Coinage", "Trans-Pamir Caravan Guards", "Indus-Oxus Customs", "Kushan Religious Patronage", "Gandharan Workshop Networks", "Buddhist Cosmopolitan Courts"),
        (("army_logistics_distance_modifier", "0.02"), ("trade_range_modifier", "0.01"), ("cultural_influence_modifier", "0.005")), "antq_saka_horse", "antq_reg_lapidary", "P8.8;P15;CAH-XI;CAH-XII"),
    IdentityPath("SAT", "SAT", "Satavahana", "indic", ("statecraft", "exchange", "warfare"),
        ("Deccan Maharathi Compacts", "Prakrit Donation Records", "Plateau Revenue Circuits", "Western Ghats Caravan Passes", "Cotton Guild Endowments", "Monsoon Port Brokers", "Deccan Elephant Reserves", "River Fort Supply Camps", "Dakshinapatha Field Commands"),
        (("tax_income_efficiency", "tiny_tax_income_efficiency_bonus"), ("export_efficiency", "tiny_trade_efficiency_bonus"), ("army_maintenance_efficiency", "0.005")), "antq_deccan_spear_company", "antq_reg_cotton_weavery", "P8.4;P15;CAH-XI;CAH-XII"),
    IdentityPath("XIO", "XIO", "Xiongnu", "inner_asian_steppe", ("warfare", "statecraft", "exchange"),
        ("Left and Right Wing Musters", "Composite Bow Horse Screens", "Mobile Felt Supply Camps", "Chanyu Hostage Diplomacy", "Tributary People Interpreters", "Seasonal Horde Councils", "Frontier Gift Tallies", "Horse-Silk Market Protocols", "Oasis Protection Rides"),
        (("levy_recovery_modifier", "0.01"), ("army_logistics_distance_modifier", "0.02"), ("trade_range_modifier", "0.0075")), "antq_steppe_horse_archers", "antq_reg_packsaddle_workshop", "P8.8;P15;CAH-XI;CAH-XII"),
    IdentityPath("KUS", "XBE", "Kushite", "nile_north_african", ("statecraft", "exchange", "warfare"),
        ("Meroitic Temple Stewards", "Kandake Court Delegates", "Nile Tribute Seals", "Middle Nile Quay Stores", "Elephant and Gold Caravans", "Cataract Toll Stations", "Kushite Archer Estates", "Desert Well Garrisons", "Nile Fortified Corridors"),
        (("country_cabinet_efficiency", "0.004"), ("trade_range_modifier", "0.01"), ("global_manpower_modifier", "0.0075")), "antq_nile_bow_company", "antq_reg_reed_boatyard", "P8.5;P15;PER;CAH-XI"),
    IdentityPath("NAB", "NAB", "Nabataean", "near_eastern", ("exchange", "statecraft", "warfare"),
        ("Petra Caravan Brokerage", "Incense Route Water Tallies", "Rock-Cut Cistern Custody", "Nabataean Customs Courts", "Desert Client Diplomacy", "Bilingual Contract Archives", "Caravan Guard Companies", "Wadi Beacon Posts", "Arabian Limes Cooperation"),
        (("merchant_maintenance_efficiency", "0.0075"), ("trade_range_modifier", "0.01"), ("army_logistics_distance_modifier", "0.015")), "antq_nabataean_caravan_guards", "antq_reg_arabian_caravan_station", "P8.2;P15;CAH-XI;OCD-NAB"),
    IdentityPath("DAC", "DAC", "Dacian", "hellenic", ("warfare", "statecraft", "exchange"),
        ("Carpathian Hillfort Musters", "Falx Workshop Standards", "Mountain Pass Scouts", "Dacian Tarabostes Councils", "Orastie Fortress Administration", "Danube Tribute Exchanges", "Carpathian Iron Routes", "Salt Mine Convoys", "Danubian Market Compacts"),
        (("land_morale_modifier", "0.005"), ("global_manpower_modifier", "0.0075"), ("export_efficiency", "tiny_trade_efficiency_bonus")), "antq_dacian_falxmen", "antq_reg_weapon_smith", "P8.1;P15;CAH-XI;OCD-DAC"),
    IdentityPath("HIM", "HIM", "Himyarite", "near_eastern", ("statecraft", "exchange", "warfare"),
        ("Terrace Sluice Custodians", "Highland Irrigation Levies", "Musnad Dam Inscriptions", "Aromatic Resin Customs", "Bab al-Mandab Pilotage", "South Arabian Caravan Courts", "Highland Spear Levies", "Monsoon Port Garrisons", "Yemeni Pass Magazines"),
        (("global_population_capacity_modifier", "0.0075"), ("trade_range_modifier", "0.0125"), ("levy_recovery_modifier", "0.0075")), "antq_south_arabian_highland_levies", "antq_reg_south_arabian_terrace_sluices", "P8.2;P15;CAH-XI;OCD-HIM"),
    IdentityPath("BTV", "BTV", "Batavian", "germanic", ("warfare", "exchange", "statecraft"),
        ("Rhine Auxiliary Cohorts", "River Crossing Scouts", "Island Horse Musters", "Rhine Frontier Markets", "North Sea Boat Landings", "Auxiliary Pay Brokers", "Batavian Assembly Oaths", "Roman Service Arbitration", "Delta Defensive Compacts"),
        (("levy_recovery_modifier", "0.01"), ("trade_range_modifier", "0.0075"), ("stability_cost_efficiency", "0.005")), "antq_batavian_auxiliary_cohort", "antq_reg_batavian_auxiliary_muster", "P8.7;P15;TAC-GER;CAH-XI"),
    IdentityPath("GOG", "GOG", "Goguryeo", "han_east_asian", ("warfare", "statecraft", "learning"),
        ("Yemaek Mountain Garrisons", "Mounted Archer Retinues", "Yalu Fortress Chains", "Five Tribe Court Offices", "Tributary Envoy Protocols", "Royal Tomb Labor Registers", "Goguryeo Monumental Inscriptions", "Buddhist Translation Houses", "Korean Chronicle Compilations"),
        (("global_manpower_modifier", "0.0075"), ("global_monthly_control", "0.0002"), ("research_speed_modifier", "0.004")), "antq_korean_plank_patrol", "antq_reg_bell_foundry", "P8.3;P15;CAH-XI;OCD-GOG"),
)


CULTURE_PATHS = (
    CulturePath("antq_latin", "Latin", "roman_italic", ("statecraft", "learning", "warfare"),
        ("Municipal Duumviral Registers", "Centuriation Boundary Stones", "Provincial Legal Formulae", "Juristic Responsa Circles", "Agrimensor Field Books", "Latin Epigraphic Habit", "Legionary Survey Parties", "Veteran Colony Cadres", "Late Roman Legal Compendia"),
        (("global_monthly_control", "0.00015"), ("global_monthly_literacy", "0.0015"), ("army_logistics_distance_modifier", "0.0125")), "P8.1;P15;CAH-XI;CAH-XII"),
    CulturePath("antq_greek_koine", "Greek Koine", "hellenic", ("learning", "statecraft", "exchange"),
        ("Koine Civic Archives", "Rhetorical Teaching Circles", "Medical Case Collections", "Polis Embassy Protocols", "Agonistic Civic Patronage", "Provincial Petition Greek", "Aegean Freight Contracts", "Eastern Mediterranean Notaries", "Late Antique Commentary Schools"),
        (("research_speed_modifier", "0.004"), ("cultural_influence_modifier", "0.004"), ("trade_range_modifier", "0.0075")), "P8.1;P15;CAH-XI;CAH-XII"),
    CulturePath("antq_parthian", "Parthian", "iranian", ("warfare", "statecraft", "exchange"),
        ("Parthian Shot Apprenticeship", "Armoured Horse Estates", "Clan Retinue Signals", "Arsacid House Genealogies", "Satrapal Arbitration", "Temple Estate Compacts", "Drachm Weight Assays", "Caspian Caravan Escorts", "Mesopotamian-Iranian Brokers"),
        (("land_morale_modifier", "0.004"), ("stability_cost_efficiency", "0.005"), ("merchant_maintenance_efficiency", "0.005")), "P8.2;P15;CAH-XI;CAH-XII"),
    CulturePath("antq_armenian", "Armenian", "iranian", ("statecraft", "warfare", "learning"),
        ("Nakharar Genealogical Memory", "Highland Court Mediation", "Pass-Duty Compacts", "Ayrudzi Household Service", "Mountain Beacon Custody", "Fortress Granary Rotations", "Armenian Alphabet Schools", "Scriptural Translation Circles", "Highland Chronicle Houses"),
        (("country_cabinet_efficiency", "0.003"), ("global_manpower_modifier", "0.005"), ("research_speed_modifier", "0.003")), "P8.2;P15;CAH-XI;OCD-ARM"),
    CulturePath("antq_judean", "Judean", "near_eastern", ("society", "learning", "exchange"),
        ("Synagogue Alms Committees", "Pilgrimage Household Networks", "Communal Arbitration", "Tannaitic Deliberation", "Mishnah Memory Schools", "Diaspora Letter Collections", "Diaspora Merchant Trusts", "Sabbatical Produce Accounts", "Academy Support Remittances"),
        (("global_disease_resistance", "0.002"), ("global_monthly_literacy", "0.0015"), ("trade_range_modifier", "0.006")), "P8.5;P15;CAH-XI;CAH-XII"),
    CulturePath("antq_han", "Han", "han_east_asian", ("statecraft", "learning", "exchange"),
        ("Clerical-Script Registers", "County Merit Recommendations", "Granary Balance Reports", "Five Classics Exegesis", "Hydraulic Gazetteers", "Calendrical Observation Bureaus", "Bronze Cash Strings", "Relay Market Tallies", "Silk Frontier Accounting"),
        (("country_cabinet_efficiency", "0.003"), ("research_speed_modifier", "0.0035"), ("import_efficiency", "tiny_trade_efficiency_bonus")), "P8.3;P15;CAH-XI;CAH-XII"),
    CulturePath("antq_xiongnu", "Xiongnu", "inner_asian_steppe", ("warfare", "statecraft", "exchange"),
        ("Composite-Bow Riding Schools", "Remount Herd Rotations", "Winged Encirclement Signals", "Seasonal Confederacy Assemblies", "Royal Kin Hostage Exchanges", "Subject-People Interpreters", "Horse-Silk Equivalencies", "Pasture Market Truces", "Oasis Escort Obligations"),
        (("levy_recovery_modifier", "0.0075"), ("army_logistics_distance_modifier", "0.015"), ("trade_range_modifier", "0.006")), "P8.8;P15;CAH-XI;CAH-XII"),
    CulturePath("antq_dacian", "Dacian", "hellenic", ("warfare", "exchange", "statecraft"),
        ("Hillfort Muster Beacons", "Falx Smithing Houses", "Carpathian Pass Ambushes", "Salt-Mine Pack Routes", "Danube River Exchanges", "Carpathian Iron Brokers", "Tarabostes Council Oaths", "Fortress District Stewards", "Mountain Tribute Compacts"),
        (("global_manpower_modifier", "0.005"), ("export_efficiency", "tiny_trade_efficiency_bonus"), ("stability_cost_efficiency", "0.004")), "P8.1;P15;CAH-XI;OCD-DAC"),
    CulturePath("antq_phoenician_punic", "Phoenician-Punic", "near_eastern", ("exchange", "statecraft", "learning"),
        ("Harbor Freight Partnerships", "Purple-Dye Workshop Contracts", "Western Sea Pilotage", "Suffete Council Procedure", "Temple Tariff Archives", "Estate-Oil Export Tallies", "Punic Bilingual Inscriptions", "Agronomic Compendia", "Maritime Notarial Schools"),
        (("trade_range_modifier", "0.008"), ("merchant_maintenance_efficiency", "0.005"), ("global_monthly_literacy", "0.001")), "P8.5;P15;PER;CAH-XI"),
    CulturePath("antq_himyarite", "Himyarite", "near_eastern", ("statecraft", "exchange", "warfare"),
        ("Terrace Water Shares", "Dam Repair Levies", "Musnad Boundary Records", "Aromatic Resin Grading", "Monsoon Sailing Windows", "Bab al-Mandab Customs", "Highland Pass Scouts", "Camel Supply Relays", "Yemeni Fortress Stores"),
        (("global_population_capacity_modifier", "0.005"), ("trade_range_modifier", "0.008"), ("army_logistics_distance_modifier", "0.0125")), "P8.2;P15;CAH-XI;OCD-HIM"),
    CulturePath("antq_maya", "Maya", "american", ("learning", "statecraft", "society"),
        ("Long Count Daykeeping", "Eclipse Observation Tables", "Scribal Codex Houses", "Dynastic Stelae Programs", "Reservoir Labor Rotations", "Causeway Tribute Processions", "Household Milpa Calendars", "Cave-Ritual Custodians", "Intercity Marriage Diplomacy"),
        (("research_speed_modifier", "0.003"), ("global_population_capacity_modifier", "0.005"), ("stability_cost_efficiency", "0.004")), "P8.11;P15;CAH-XI;CAH-XII"),
    CulturePath("antq_moche", "Moche", "american", ("statecraft", "exchange", "warfare"),
        ("Irrigation Canal Overseers", "Valley Labor Rotations", "Huaca Storehouse Seals", "Copper-Gilding Workshops", "Coastal Cotton Exchanges", "Ceremonial Craft Quarters", "Valley Warrior Retinues", "Desert Road Waystations", "Fortified Canal Headworks"),
        (("global_population_capacity_modifier", "0.005"), ("export_efficiency", "tiny_trade_efficiency_bonus"), ("global_manpower_modifier", "0.005")), "P8.11;P15;CAH-XI;CAH-XII"),
)


if len(PATHS) != 15 or len({path.design_tag for path in PATHS}) != len(PATHS):
    raise ValueError("Round 6 identity paths must contain 15 unique flagship polities")
if any(len(path.names) != 9 for path in PATHS):
    raise ValueError("each Round 6 identity path must contain nine advances")


DESIGN_BY_ENGINE = {path.engine_tag: path.design_tag for path in PATHS}


def node_key(path: IdentityPath, index: int) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", path.names[index].lower()).strip("_")
    return f"antq_identity_{path.design_tag.lower()}_{slug}"


def culture_node_key(path: CulturePath, index: int) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", path.names[index].lower()).strip("_")
    culture = path.culture.removeprefix("antq_")
    return f"antq_culture_{culture}_{slug}"


IDENTITY_UNLOCKS = {
    node_key(path, 1): (("unlock_unit", path.unit),)
    for path in PATHS
}
for _path in PATHS:
    IDENTITY_UNLOCKS[node_key(_path, 2)] = (("unlock_building", _path.building),)

if len(CULTURE_PATHS) != 12 or any(len(path.names) != 9 for path in CULTURE_PATHS):
    raise ValueError("Round 6 exact-culture paths must contain 12 nine-node traditions")
