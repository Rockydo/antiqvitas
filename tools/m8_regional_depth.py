#!/usr/bin/env python3
"""Historically bounded regional themes for the S2-P3 knowledge expansion."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RegionalTheme:
    anchor: str
    summary: str
    source: str


# Each entry continues one of the twenty-two reviewed Age-I regional paths
# through the High Empires, Crisis, Dominate, and Migrations conceptual ages.
# The final conceptual age is divided between the engine's two mandatory late
# slots by branch ordinal in m8_knowledge.py.
LATER_THEMES: dict[tuple[str, str], tuple[RegionalTheme, ...]] = {
    ("statecraft", "celtic"): (
        RegionalTheme("antonine_civitas", "Provincial civitates joined local councils, tribute assessment, and imperial petitioning without erasing indigenous elites.", "P8.7;P15;CAH-XI;OCD"),
        RegionalTheme("post_severan_frontier", "Contracting imperial supervision made frontier notables and fortified communities carry more adjudication and levy coordination.", "P8.7;P15;CAH-XII"),
        RegionalTheme("pictish_confederate", "Northern British communities coordinated through mobile kingship, elite gift exchange, and fortified regional centres.", "P8.7;P15;CAH-XII"),
        RegionalTheme("successor_brittonic", "Post-imperial Brittonic rulers combined warband households, Roman civic memory, and negotiated local authority.", "P8.7;P15;CAH-XII"),
    ),
    ("statecraft", "african"): (
        RegionalTheme("aksumite_red_sea_chancery", "Aksumite rulers linked highland tribute, Adulis customs, inscriptions, and diplomatic exchange across the Red Sea.", "P8.5;P15;PER;CAH-XI"),
        RegionalTheme("meroe_nobadia_transition", "Middle Nile authorities adapted temple estates, caravan tolls, and regional courts as Meroitic central power changed.", "P8.5;P15;CAH-XII"),
        RegionalTheme("aksumite_inscriptional_kingship", "Royal titulature, monumental inscriptions, coin issues, and provincial delegates articulated Aksumite sovereignty.", "P8.5;P15;CAH-XII"),
        RegionalTheme("nubian_frontier_courts", "Nile successor communities governed through fortified courts, cattle wealth, river exchange, and negotiated religious patronage.", "P8.5;P15;CAH-XII"),
    ),
    ("statecraft", "baltic"): (
        RegionalTheme("wielbark_coastal_assemblies", "Baltic coastal communities coordinated amber exchange, cemeteries, household leaders, and seasonal meeting places.", "P8.7;P15;PAN-WBB"),
        RegionalTheme("amber_route_redistribution", "Reduced Roman demand shifted authority toward local brokers controlling portages, metal, hides, and ceremonial valuables.", "P8.7;P15;PAN-WBB"),
        RegionalTheme("hillfort_district_compacts", "Fortified nodes and dispersed farmsteads sustained district-scale obligations without projecting later territorial states.", "P8.7;P15;PAN-WBB"),
        RegionalTheme("post_roman_coastal_lordship", "Migration-era coast and river communities concentrated exchange and armed followings around emergent local lords.", "P8.7;P15;PAN-WBB"),
    ),
    ("statecraft", "uralic"): (
        RegionalTheme("kama_metallurgical_custody", "Kama communities tied metallurgical specialists, sanctuary deposits, and river-route stewards to seasonal authority.", "P8.7;P15;BSE-GLYADENOVO"),
        RegionalTheme("forest_steppe_refuge_councils", "Instability along the forest-steppe strengthened refuge settlements, kin delegates, and negotiated portage protection.", "P8.7;P15;BSE-GORODETS"),
        RegionalTheme("volga_portage_confederation", "Volga and Kama route communities coordinated tribute gifts, iron exchange, and seasonal armed escorts.", "P8.7;P15;BSE-GORODETS;BSE-GLYADENOVO"),
        RegionalTheme("northern_sanctuary_networks", "Northern forest societies maintained wide ritual and exchange ties through custodians rather than territorial bureaucracy.", "P8.7;P15;BSE-UST-POLUY"),
    ),
    ("warfare", "iranian_steppe"): (
        RegionalTheme("kushan_parthian_armoured_hosts", "Iranian and Central Asian rulers combined horse archers, armoured retainers, remount systems, and fortified depots.", "P8.2;P8.8;P15;CAH-XI"),
        RegionalTheme("sasanian_aswaran_reform", "Early Sasanian armies integrated noble cavalry obligations, royal armouries, siege practice, and frontier garrisons.", "P8.2;P15;CAH-XII"),
        RegionalTheme("shapur_frontier_armies", "Third- and fourth-century Iranian warfare joined heavy cavalry, elephants, siege trains, and defended frontier corridors.", "P8.2;P15;CAH-XII;AMM"),
        RegionalTheme("hunnic_iranian_composite_cavalry", "Late antique mounted armies blended steppe archery, armoured lancers, dispersed remounts, and negotiated client contingents.", "P8.2;P8.8;P15;CAH-XII"),
    ),
    ("warfare", "indic"): (
        RegionalTheme("satavahana_frontier_corps", "Deccan powers coordinated elephants, infantry guild levies, fortified routes, and monsoon-aware provisioning.", "P8.4;P15;CAH-XI"),
        RegionalTheme("post_kushan_cavalry_elephants", "North Indian armies balanced cavalry mobility, elephant shock, archery, and fortified river crossings.", "P8.4;P15;CAH-XII"),
        RegionalTheme("samudragupta_campaign_system", "Gupta campaigning depended on tributary contingents, mobile royal forces, river logistics, and negotiated submissions.", "P8.4;P15;CAH-XII"),
        RegionalTheme("late_gupta_frontier_defence", "Fifth-century Indian rulers answered frontier pressure with layered forts, mounted contingents, and regional military households.", "P8.4;P15;CAH-XII"),
    ),
    ("warfare", "celtic"): (
        RegionalTheme("hadrianic_auxiliary_frontier", "British and continental communities supplied scouts, auxiliaries, hill routes, and local knowledge to imperial frontiers.", "P8.7;P15;CAH-XI"),
        RegionalTheme("crisis_hillfort_refuges", "Third-century insecurity renewed defended gathering places, local musters, and protected food stores.", "P8.7;P15;CAH-XII"),
        RegionalTheme("northern_british_war_leagues", "Late Roman northern warfare relied on raiding confederacies, rapid musters, and negotiated elite leadership.", "P8.7;P15;CAH-XII;AMM"),
        RegionalTheme("post_roman_warband_households", "Successor rulers fused household retainers, refurbished forts, mounted messengers, and community levies.", "P8.7;P15;CAH-XII"),
    ),
    ("warfare", "slavic_eastern"): (
        RegionalTheme("zarubintsy_forest_warbands", "Forest and river communities used ambush routes, light spears, boats, and dispersed refuge settlements.", "P8.7;P15;AWE-DNIEPER-DVINA"),
        RegionalTheme("chernyakhiv_frontier_levies", "Mixed frontier settlements supported infantry levies, river movement, and military exchange with steppe and Roman neighbours.", "P8.7;P15;ENC-NEEU"),
        RegionalTheme("dnieper_earthwork_refuges", "Communities under Gothic and Hunnic pressure relied on concealed routes, earthworks, stored grain, and flexible war leaders.", "P8.7;P15;ENC-NEEU"),
        RegionalTheme("antae_river_war_leagues", "Late fifth-century eastern European groups coordinated river crossings, seasonal hosts, and federated raiding leadership.", "P8.7;P15;ENC-NEEU"),
    ),
    ("exchange", "roman_italic"): (
        RegionalTheme("antonine_annona_circuits", "State grain fleets, amphora standards, river ports, and merchant collegia linked Mediterranean demand.", "P8.1;P15;CAH-XI;OCD"),
        RegionalTheme("crisis_requisition_markets", "Coin instability and civil war redirected exchange through military requisition, tax in kind, and defended depots.", "P8.1;P15;CAH-XII"),
        RegionalTheme("late_roman_fiscal_convoys", "The Dominate moved grain, cloth, arms, and official correspondence through supervised transport obligations.", "P8.1;P15;CAH-XII"),
        RegionalTheme("successor_mediterranean_exchange", "Fifth-century ports preserved narrower circuits of grain, oil, ceramics, metal, and diplomatic gifts.", "P8.1;P15;CAH-XII"),
    ),
    ("exchange", "han_east_asian"): (
        RegionalTheme("western_regions_relay_trade", "Eastern Han relay stations, commandery markets, and protected corridors connected China with Central Asia.", "P8.3;P15;BHR;Bielenstein"),
        RegionalTheme("three_kingdoms_river_exchange", "Competing regimes relied on granary transport, river fleets, market towns, and controlled metal and salt exchange.", "P8.3;P15;CAH-XII"),
        RegionalTheme("jin_migrant_market_networks", "Population movement carried craft skills and commercial ties between northern corridors and southern river basins.", "P8.3;P15;CAH-XII"),
        RegionalTheme("northern_southern_granary_circuits", "Fifth-century courts sustained regional exchange with river transport, frontier markets, and public granary networks.", "P8.3;P15;CAH-XII"),
    ),
    ("exchange", "african"): (
        RegionalTheme("adulis_indian_ocean_exchange", "Adulis connected highland products, Nile and Red Sea routes, Roman demand, Arabia, and Indian Ocean shipping.", "P8.5;P15;PER;CAH-XI"),
        RegionalTheme("sahel_iron_cattle_corridors", "Savanna exchange linked iron-producing communities, pastoral wealth, river routes, and forest-edge goods.", "P8.5;P15;CAH-XII"),
        RegionalTheme("aksumite_coin_customs", "Aksumite coinage and customs oversight supported Red Sea diplomacy, port dues, and highland redistribution.", "P8.5;P15;CAH-XII"),
        RegionalTheme("horn_oceanic_entrepots", "Late antique Horn ports mediated ivory, aromatics, livestock, textiles, and ceramics across seasonal sea lanes.", "P8.5;P15;PER;CAH-XII"),
    ),
    ("exchange", "baltic"): (
        RegionalTheme("wielbark_amber_fairs", "Amber, hides, iron, and imported vessels moved through coastal fairs and river-portage intermediaries.", "P8.7;P15;PAN-WBB"),
        RegionalTheme("post_roman_import_contraction", "Shrinking imperial imports encouraged local metal exchange, repair, reuse, and shorter seasonal circuits.", "P8.7;P15;PAN-WBB"),
        RegionalTheme("migration_age_portages", "Baltic and inland communities protected boat landings, overland carries, and exchange across changing political zones.", "P8.7;P15;PAN-WBB"),
        RegionalTheme("vistula_coastal_redistribution", "Fifth-century route leaders joined maritime access, river movement, workshops, and elite gift exchange.", "P8.7;P15;PAN-WBB"),
    ),
    ("learning", "hellenic"): (
        RegionalTheme("second_sophistic_schools", "Urban teachers, libraries, rhetoric, medicine, and civic patronage sustained a shared Greek learned world.", "P8.1;P15;CAH-XI;OCD"),
        RegionalTheme("plotinian_philosophical_circles", "Third-century schools combined textual commentary, mathematics, medicine, and competing philosophical curricula.", "P8.1;P15;CAH-XII"),
        RegionalTheme("late_antique_academy_networks", "Teachers and students circulated between major eastern cities, preserving and disputing classical texts.", "P8.1;P15;CAH-XII"),
        RegionalTheme("christian_classical_dialectic", "Fifth-century scholars adapted rhetoric, philosophy, manuscript culture, and legal reasoning to new religious institutions.", "P8.1;P15;CAH-XII"),
    ),
    ("learning", "roman_italic"): (
        RegionalTheme("classical_juristic_responsa", "Jurists organized imperial rulings, private law, provincial petitions, and professional legal interpretation.", "P8.1;P15;OCD;CAH-XI"),
        RegionalTheme("third_century_rescript_bureaus", "Crisis government still depended on petitions, rescripts, military records, surveying, and fiscal archives.", "P8.1;P15;CAH-XII"),
        RegionalTheme("diocletianic_codex_practice", "Late imperial offices collected precedents, standardized forms, and coordinated census and price information.", "P8.1;P15;CAH-XII"),
        RegionalTheme("theodosian_legal_compilation", "Fifth-century compilers reconciled imperial constitutions, provincial practice, church privilege, and court procedure.", "P8.1;P15;CAH-XII"),
    ),
    ("learning", "han_east_asian"): (
        RegionalTheme("eastern_han_commentarial_schools", "Classicist lineages, astronomical offices, medical texts, and administrative manuals circulated through Han literati networks.", "P8.3;P15;BHR;Bielenstein"),
        RegionalTheme("three_kingdoms_technical_writings", "Competing courts sponsored agronomy, cartography, calendrics, medicine, and strategic commentary.", "P8.3;P15;CAH-XII"),
        RegionalTheme("jin_manuscript_culture", "Paper manuscripts, calligraphic practice, private collections, and migrant scholars reshaped learned exchange.", "P8.3;P15;CAH-XII"),
        RegionalTheme("northern_southern_textual_transmission", "Court and monastic networks copied classics, Buddhist texts, histories, and technical works across divided China.", "P8.3;P15;CAH-XII"),
    ),
    ("learning", "indic"): (
        RegionalTheme("kushan_buddhist_scholasticism", "Monastic centres, multilingual inscriptions, medical learning, and long-distance patronage supported textual debate.", "P8.4;P15;CAH-XI"),
        RegionalTheme("sanskrit_courtly_synthesis", "Sanskrit literary culture connected courts, ritual specialists, grammar, astronomy, and political praise.", "P8.4;P15;CAH-XII"),
        RegionalTheme("gupta_mathematical_astronomy", "Fourth-century Indian scholars refined computation, calendrics, astronomy, medicine, and learned commentary.", "P8.4;P15;CAH-XII"),
        RegionalTheme("monastic_pilgrimage_texts", "Pilgrims and monasteries carried manuscripts, translation practices, sacred geography, and institutional memory.", "P8.4;P15;CAH-XII"),
    ),
    ("learning", "uralic"): (
        RegionalTheme("kama_craft_lineages", "Specialist learning passed through metallurgical apprenticeship, route memory, ecological calendars, and ritual performance.", "P8.7;P15;BSE-GLYADENOVO"),
        RegionalTheme("forest_refuge_memory", "Dispersed communities preserved practical knowledge of waterways, soils, winter travel, and protected gathering places.", "P8.7;P15;BSE-GORODETS"),
        RegionalTheme("volga_interpreter_networks", "Intermediaries transmitted route knowledge, metalworking techniques, languages, and diplomatic custom along river corridors.", "P8.7;P15;BSE-GORODETS"),
        RegionalTheme("northern_oral_canonical_traditions", "Ritual specialists and craft households maintained durable oral corpora without inventing an unsupported written bureaucracy.", "P8.7;P15;BSE-UST-POLUY"),
    ),
    ("society", "american"): (
        RegionalTheme("teotihuacan_neighbourhood_expansion", "Apartment compounds, craft quarters, ritual precincts, and immigrant communities structured a major Mesoamerican city.", "P8.10;P15;MILLON"),
        RegionalTheme("moche_civic_ritual_polities", "North Andean communities joined irrigation, craft specialization, monumental ceremony, and elite redistribution.", "P8.10;P15;MOSELEY"),
        RegionalTheme("maya_dynastic_urban_networks", "Lowland centres organized households, markets, reservoirs, writing, and dynastic ritual through linked urban landscapes.", "P8.10;P15;MARTIN-GRUBE"),
        RegionalTheme("late_formative_regional_successors", "Fifth-century American societies developed distinct post-formative urban, ceremonial, and exchange solutions.", "P8.10;P15"),
    ),
    ("society", "near_eastern"): (
        RegionalTheme("rabbinic_academy_communities", "Jewish communities sustained law, charity, worship, and learned debate after the destruction of the Jerusalem temple.", "P8.1;P15;CAH-XI"),
        RegionalTheme("syriac_christian_networks", "Syriac-speaking congregations connected households, bishops, ascetics, merchants, and manuscript communities.", "P8.1;P8.2;P15;CAH-XII"),
        RegionalTheme("sasanian_communal_jurisdictions", "Religious and professional communities negotiated family law, taxation, charity, and authority under Sasanian rule.", "P8.2;P15;CAH-XII"),
        RegionalTheme("late_antique_pilgrim_cities", "Shrines, hostels, markets, bishops, and civic patrons reshaped settlement life across the eastern Mediterranean.", "P8.1;P15;CAH-XII"),
    ),
    ("society", "germanic"): (
        RegionalTheme("marcomannic_confederate_households", "War leaders coordinated retinues, tribute, hostages, assemblies, and farm households across shifting confederacies.", "P8.7;P15;STR-GER;CAH-XI"),
        RegionalTheme("gothic_chernyakhiv_communities", "Mixed settlements joined farming, craft production, exchange, armed followings, and negotiated group identities.", "P8.7;P15;ENC-NEEU"),
        RegionalTheme("federate_settlement_societies", "Late Roman treaties settled armed groups through land, rations, military service, and recognized leadership.", "P8.7;P15;CAH-XII;AMM"),
        RegionalTheme("successor_kingdom_households", "Fifth-century kingdoms fused royal retinues, Roman administration, customary settlements, and church patronage.", "P8.7;P15;CAH-XII"),
    ),
    ("society", "slavic_eastern"): (
        RegionalTheme("zarubintsy_riverside_households", "Small river settlements coordinated ovens, storage, fields, fishing, seasonal movement, and mortuary obligations.", "P8.7;P15;AWE-DNIEPER-DVINA"),
        RegionalTheme("chernyakhiv_mixed_settlements", "Large frontier communities combined diverse building customs, agriculture, crafts, exchange, and cemeteries.", "P8.7;P15;ENC-NEEU"),
        RegionalTheme("post_chernyakhiv_refuge_communities", "Political disruption favoured smaller settlements, portable wealth, flexible kin groups, and protected subsistence.", "P8.7;P15;ENC-NEEU"),
        RegionalTheme("prague_korchak_household_clusters", "Late fifth-century settlement traditions emphasized compact households, handmade pottery, mixed farming, and riverine mobility.", "P8.7;P15;ENC-NEEU"),
    ),
    ("society", "oceanian"): (
        RegionalTheme("mekong_coastal_chiefdoms", "Mainland and island communities linked irrigated fields, coastal exchange, ritual centres, and chiefly redistribution.", "P8.9;P15;HCSEA"),
        RegionalTheme("austronesian_interisland_networks", "Sailing kin groups maintained exchange in ceramics, beads, metals, foods, and ritual knowledge across island chains.", "P8.9;P15;BELLWOOD"),
        RegionalTheme("lapita_descendant_communities", "Oceanic societies adapted inherited voyaging, horticulture, fishing, and ceremonial exchange to local archipelagos.", "P8.9;P15;KIRCH"),
        RegionalTheme("late_ancient_island_polities", "Fifth-century maritime communities developed regionally distinct harbour, lineage, ritual, and redistribution institutions.", "P8.9;P15;BELLWOOD;KIRCH"),
    ),
}


NODE_SUFFIXES: dict[str, tuple[tuple[str, str], ...]] = {
    "statecraft": (
        ("delegates", "trained delegates linked local authorities to wider political networks."),
        ("tallies", "regular tallies made obligations, stores, and negotiated contributions legible."),
        ("arbitration", "recognized mediators settled disputes across household and district boundaries."),
        ("stewardship", "specialized stewards coordinated routes, stores, petitions, and public works."),
        ("compact", "a durable compact balanced central claims with local consent and custom."),
    ),
    "warfare": (
        ("scouts", "scouts and guides converted local terrain knowledge into operational warning."),
        ("musters", "structured musters joined household contingents without requiring a permanently paid central army."),
        ("supply", "distributed fodder, food, remount, and equipment stores sustained campaigning."),
        ("drill", "retinues rehearsed coordinated movement suited to their regional arms and terrain."),
        ("command", "layered command joined specialist troops, local levies, and allied contingents."),
    ),
    "exchange": (
        ("waystations", "protected stopping places concentrated information, storage, and route maintenance."),
        ("weights", "shared measures and recognized valuations reduced disputes between trading communities."),
        ("brokers", "trusted brokers mediated language, credit, tolls, and political permission."),
        ("convoys", "coordinated river, road, or maritime convoys reduced seasonal transport risk."),
        ("circuits", "interlocking circuits connected producers, redistribution centres, and distant consumers."),
    ),
    "learning": (
        ("teachers", "recognized teachers transmitted difficult knowledge through durable personal lineages."),
        ("catalogues", "catalogues organized texts, observations, precedents, or oral corpora for retrieval."),
        ("commentaries", "commentary reconciled inherited authorities with new evidence and political settings."),
        ("observations", "systematic observation refined practical knowledge through repeated empirical practice."),
        ("curriculum", "a stable curriculum reproduced regional expertise across several institutions."),
    ),
    "society": (
        ("households", "household obligations anchored welfare, production, ritual, and political belonging."),
        ("endowments", "durable endowments supported cult, charity, feasting, and communal infrastructure."),
        ("mediation", "mediators reconciled status, kinship, religious, and neighbourhood disputes."),
        ("assemblies", "periodic assemblies coordinated rites, mutual aid, and collective obligations."),
        ("communities", "interlocking communities sustained a recognizable regional social order."),
    ),
}


EFFECT_SCALES: dict[str, tuple[tuple[str, float, float], ...]] = {
    "statecraft": (
        ("country_cabinet_efficiency", 0.0040, 0.000003),
        ("stability_cost_efficiency", 0.0080, 0.000003),
        ("global_monthly_control", 0.00010, 0.0000003),
        ("tax_income_efficiency", 0.0045, 0.000003),
        ("legislative_efficiency", 0.0120, 0.000004),
    ),
    "warfare": (
        ("levy_recovery_modifier", 0.0040, 0.000003),
        ("army_logistics_distance_modifier", 0.0200, 0.000010),
        ("army_maintenance_efficiency", 0.0045, 0.000003),
        ("land_morale_modifier", 0.0030, 0.000002),
        ("discipline", 0.0010, 0.000001),
    ),
    "exchange": (
        ("trade_range_modifier", 0.0080, 0.000005),
        ("merchant_maintenance_efficiency", 0.0040, 0.000003),
        ("global_trade_through_owned_territory_efficiency", 0.0150, 0.000008),
        ("import_efficiency", 0.0035, 0.000003),
        ("export_efficiency", 0.0040, 0.000003),
    ),
    "learning": (
        ("research_speed_modifier", 0.0040, 0.000002),
        ("cultural_influence_modifier", 0.0045, 0.000003),
        ("global_monthly_literacy", 0.0010, 0.000001),
        ("global_institution_growth_modifier", 0.0250, 0.000010),
        ("research_speed_modifier", 0.0130, 0.000002),
    ),
    "society": (
        ("global_disease_resistance", 0.0015, 0.000001),
        ("global_population_capacity_modifier", 0.0060, 0.000004),
        ("global_pop_promotion_speed_modifier", 0.0080, 0.000005),
        ("global_pop_assimilation_speed_modifier", 0.0085, 0.000005),
        ("stability_cost_efficiency", 0.0300, 0.000004),
    ),
}

# EU5's persistent script reader rejects numeric literals beyond five decimal
# places. Distinct values therefore advance in 1e-5 steps rather than relying
# on engine-invalid sixth or seventh decimal digits.
ENGINE_DECIMAL_STEP = 0.00001


def later_branch_pairs() -> tuple[tuple[str, str], ...]:
    return tuple(LATER_THEMES)


def branch_names(theme: RegionalTheme, track: str) -> tuple[str, ...]:
    return tuple(f"{theme.anchor}_{suffix}" for suffix, _description in NODE_SUFFIXES[track])


def node_description(theme: RegionalTheme, track: str, node_index: int) -> str:
    action = NODE_SUFFIXES[track][node_index][1]
    return f"{theme.summary} In this advance, {action}"


def node_effect(
    track: str,
    conceptual_age: int,
    branch_ordinal: int,
    node_index: int,
) -> tuple[str, str]:
    field, base, _increment = EFFECT_SCALES[track][node_index]
    ordinal = (conceptual_age - 1) * len(LATER_THEMES) + branch_ordinal + 1
    value = base + ENGINE_DECIMAL_STEP * ordinal
    return field, f"{value:.5f}".rstrip("0").rstrip(".")


def validate_catalog(expected_pairs: set[tuple[str, str]]) -> None:
    if set(LATER_THEMES) != expected_pairs:
        raise ValueError(
            "S2-P3 later-theme paths diverge from Age-I regional paths: "
            f"missing={sorted(expected_pairs - set(LATER_THEMES))}, "
            f"extra={sorted(set(LATER_THEMES) - expected_pairs)}"
        )
    anchors: set[str] = set()
    keys: set[str] = set()
    effects: set[tuple[str, str]] = set()
    for branch_ordinal, ((track, _profile), themes) in enumerate(LATER_THEMES.items()):
        if len(themes) != 4:
            raise ValueError(f"{track} later path must cover four conceptual ages")
        for conceptual_age, theme in enumerate(themes, start=1):
            if theme.anchor in anchors:
                raise ValueError(f"repeated S2-P3 regional anchor {theme.anchor}")
            anchors.add(theme.anchor)
            if not theme.summary or not theme.source:
                raise ValueError(f"incomplete S2-P3 regional theme {theme.anchor}")
            for node_index, key in enumerate(branch_names(theme, track)):
                if key in keys:
                    raise ValueError(f"repeated S2-P3 regional advance {key}")
                keys.add(key)
                effect = node_effect(track, conceptual_age, branch_ordinal, node_index)
                if effect in effects:
                    raise ValueError(f"repeated S2-P3 regional effect {effect}")
                effects.add(effect)
    if len(keys) != 440 or len(effects) != 440:
        raise ValueError(f"S2-P3 regional catalog must contain 440 unique nodes, got {len(keys)}")
