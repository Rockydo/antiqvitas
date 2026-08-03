#!/usr/bin/env python3
"""Round 5 disjoint Iranian, steppe, Nile/North-African, and sub-Saharan paths."""

from __future__ import annotations


SOURCE = {
    "iranian": "P8.2;P15;CAH-XI;CAH-XII",
    "inner_asian_steppe": "P8.8;P15;CAH-XI;CAH-XII",
    "nile_north_african": "P8.5;P15;PER;CAH-XI;CAH-XII",
    "subsaharan": "P8.5;P15;CAH-XI;CAH-XII",
}

# Five deliberately named opening nodes per path.  m8_knowledge supplies the
# branch/convergence shape and bounded effects.
OPENING_PATHS: dict[tuple[str, str], tuple[str, ...]] = {
    ("statecraft", "iranian"): (
        "satrapal_household_registers", "arsacid_dynastic_compacts",
        "temple_estate_adjudication", "royal_road_station_offices",
        "king_of_kings_delegated_rule",
    ),
    ("warfare", "iranian"): (
        "iranian_remount_estates", "parthian_shot_drill",
        "cataphract_armour_workshops", "noble_cavalry_retinues",
        "arsacid_combined_cavalry_command",
    ),
    ("exchange", "iranian"): (
        "iranian_caravanserai_precursors", "silver_drachm_accounts",
        "mesopotamian_plateau_brokers", "caspian_gate_convoys",
        "silk_road_customs_compacts",
    ),
    ("statecraft", "inner_asian_steppe"): (
        "seasonal_horde_councils", "left_right_wing_commands",
        "tribute_envoy_protocols", "subject_people_interpreters",
        "chanyu_confederate_authority",
    ),
    ("warfare", "inner_asian_steppe"): (
        "steppe_remount_herds", "composite_bow_screening",
        "decimal_riding_musters", "mobile_felt_supply_camps",
        "confederate_horse_archer_command",
    ),
    ("exchange", "inner_asian_steppe"): (
        "pastoral_surplus_fairs", "frontier_gift_tallies",
        "oasis_interpreter_brokers", "caravan_protection_rides",
        "steppe_sown_exchange_corridors",
    ),
    ("statecraft", "nile_north_african"): (
        "nile_temple_land_stewards", "nomos_petition_delegates",
        "desert_oasis_tribute_tallies", "caravan_route_arbitration",
        "river_desert_court_compacts",
    ),
    ("exchange", "nile_north_african"): (
        "nile_quay_storehouses", "alexandrian_measure_offices",
        "red_sea_customs_brokers", "horn_monsoon_convoys",
        "nile_red_sea_exchange_circuits",
    ),
    ("learning", "nile_north_african"): (
        "temple_scribal_houses", "demotic_greek_catalogues",
        "alexandrian_medical_commentaries", "nile_flood_observations",
        "north_african_scribal_curricula",
    ),
    ("statecraft", "subsaharan"): (
        "lineage_council_speakers", "cattle_tribute_tallies",
        "ironworking_custodian_compacts", "river_crossing_arbitration",
        "savanna_forest_authority_networks",
    ),
    ("warfare", "subsaharan"): (
        "savanna_scouting_parties", "age_grade_musters",
        "iron_spear_supply_households", "woodland_ambush_drill",
        "regional_war_league_command",
    ),
    ("exchange", "subsaharan"): (
        "niger_river_waystations", "iron_cattle_value_tallies",
        "forest_savanna_brokers", "seasonal_porter_convoys",
        "interregional_exchange_circuits",
    ),
}

# Four later conceptual ages per path.  Each theme expands into five specific
# advances (delegates/tallies/etc.) using the established regional-depth engine.
LATER_PATHS: dict[tuple[str, str], tuple[tuple[str, str, str], ...]] = {
    ("statecraft", "iranian"): (
        ("kushan_arsacid_border_chanceries", "Iranian courts coordinated dynastic households, border governors, temple estates, and multilingual petitions across contested eastern provinces.", SOURCE["iranian"]),
        ("sasanian_provincial_offices", "Early Sasanian rule joined royal appointees, aristocratic houses, district revenues, seals, and inherited local jurisdictions.", SOURCE["iranian"]),
        ("shapur_inscriptional_kingship", "Monumental titulature, provincial correspondence, tax offices, and negotiated noble service articulated a durable Iranian imperial order.", SOURCE["iranian"]),
        ("late_sasanian_frontier_governance", "Frontier marzbans, court households, fortified districts, and religious foundations coordinated late antique Iranian rule.", SOURCE["iranian"]),
    ),
    ("warfare", "iranian"): (
        ("kushan_parthian_armoured_hosts", "Iranian powers combined armoured lancers, horse archers, remount estates, elephants, and fortified depots without adopting a nomad confederacy structure.", SOURCE["iranian"]),
        ("ardashir_royal_armies", "Early Sasanian forces integrated noble cavalry obligations, royal armouries, siege specialists, and defended frontier corridors.", SOURCE["iranian"]),
        ("shapur_combined_field_forces", "Iranian field armies coordinated aswaran cavalry, infantry, elephants, siege trains, and garrisoned approaches.", SOURCE["iranian"]),
        ("late_iranian_border_commands", "Late antique Iranian defence linked armoured cavalry, frontier districts, allied contingents, and strategic fortress systems.", SOURCE["iranian"]),
    ),
    ("exchange", "iranian"): (
        ("kushan_plateau_caravan_revenues", "Kushan and Arsacid corridors tied coin, caravan tolls, oasis markets, and Mesopotamian demand to Iranian court revenue.", SOURCE["iranian"]),
        ("sasanian_mint_customs_networks", "Royal mints, customs stations, market inspectors, and protected caravan routes supported Sasanian fiscal consolidation.", SOURCE["iranian"]),
        ("persian_gulf_entrepot_system", "Gulf ports and inland caravan towns coordinated textiles, aromatics, metals, horses, and seasonal oceanic exchange.", SOURCE["iranian"]),
        ("late_sasanian_silk_corridors", "Late antique Iranian merchants and officials managed longer chains linking Central Asia, India, Mesopotamia, and the Mediterranean.", SOURCE["iranian"]),
    ),
    ("statecraft", "inner_asian_steppe"): (
        ("xiongnu_winged_confederation", "Xiongnu leadership balanced left and right wings, royal kin, tributary peoples, hostage exchange, and seasonal assemblies.", SOURCE["inner_asian_steppe"]),
        ("xianbei_successor_leagues", "Post-Xiongnu steppe rulers assembled mobile followings through marriage alliances, gifts, ranked commanders, and negotiated pasture access.", SOURCE["inner_asian_steppe"]),
        ("rouan_confederate_households", "Fourth-century Inner Asian confederacies linked elite households, subject groups, tribute missions, and dispersed military camps.", SOURCE["inner_asian_steppe"]),
        ("steppe_imperial_brokerage", "Fifth-century steppe powers governed broad coalitions through interpreters, diplomatic gifts, mobile courts, and delegated war leadership.", SOURCE["inner_asian_steppe"]),
    ),
    ("warfare", "inner_asian_steppe"): (
        ("xiongnu_deep_remount_systems", "Large remount herds, mounted archery, dispersed camps, scouts, and rapid concentration sustained Xiongnu campaigning.", SOURCE["inner_asian_steppe"]),
        ("xianbei_mobile_commands", "Xianbei forces joined skilled riders, composite bows, captured equipment, flexible wings, and seasonal pasture logistics.", SOURCE["inner_asian_steppe"]),
        ("hunnic_confederate_cavalry", "Fourth-century steppe armies combined horse-archer mobility, tributary contingents, terror, reconnaissance, and negotiated submission.", SOURCE["inner_asian_steppe"]),
        ("late_steppe_siege_adaptation", "Fifth-century confederacies retained mobile cavalry while absorbing engineers, armour, infantry clients, and frontier siege practice.", SOURCE["inner_asian_steppe"]),
    ),
    ("exchange", "inner_asian_steppe"): (
        ("han_xiongnu_frontier_markets", "Regulated frontier markets, diplomatic gifts, livestock exchange, and caravan protection linked Han and Xiongnu economies.", SOURCE["inner_asian_steppe"]),
        ("xianbei_oasis_brokerage", "Mobile leaders, oasis merchants, interpreters, and border settlements maintained exchange after the Xiongnu political order fractured.", SOURCE["inner_asian_steppe"]),
        ("steppe_silk_tribute_routes", "Silk, horses, metalwork, livestock, captives, and prestige goods circulated through confederate tribute and commercial channels.", SOURCE["inner_asian_steppe"]),
        ("migration_age_caravan_guards", "Late steppe rulers protected selected routes and markets while taxing movement across politically fragmented corridors.", SOURCE["inner_asian_steppe"]),
    ),
    ("statecraft", "nile_north_african"): (
        ("roman_nile_temple_administration", "Nile officials, temple estates, village scribes, tax grain, and river transport connected local communities to provincial government.", SOURCE["nile_north_african"]),
        ("meroe_nobadia_transition", "Middle Nile authorities adapted temple lands, cattle wealth, caravan tolls, and regional courts as Meroitic central power changed.", SOURCE["nile_north_african"]),
        ("late_roman_african_civic_courts", "North African cities and rural estates coordinated petitions, taxation, church patronage, and defended local administration.", SOURCE["nile_north_african"]),
        ("nubian_berber_successor_courts", "Nile and Maghrebi successor communities governed through fortified courts, tribal compacts, route revenues, and negotiated religious authority.", SOURCE["nile_north_african"]),
    ),
    ("exchange", "nile_north_african"): (
        ("adulis_nile_oceanic_exchange", "Adulis and Nile routes connected highland products, Roman demand, Arabia, and Indian Ocean shipping through multilingual brokers.", SOURCE["nile_north_african"]),
        ("african_grain_amphora_circuits", "North African grain, oil, ceramics, livestock, and textiles moved through estate markets, coastal ports, and state provisioning.", SOURCE["nile_north_african"]),
        ("aksumite_coin_customs", "Aksumite coinage, Red Sea customs, caravan routes, and port dues supported highland redistribution and oceanic diplomacy.", SOURCE["nile_north_african"]),
        ("late_horn_maghreb_entrepots", "Late antique ports mediated ivory, aromatics, grain, oil, livestock, textiles, and ceramics across narrower regional sea lanes.", SOURCE["nile_north_african"]),
    ),
    ("learning", "nile_north_african"): (
        ("alexandrian_scribal_schools", "Greek, Demotic, temple, medical, and mathematical learning coexisted in urban and sacred institutions along the Nile.", SOURCE["nile_north_african"]),
        ("north_african_rhetorical_networks", "African cities supported rhetoric, law, Christian scholarship, agronomy, and administrative correspondence.", SOURCE["nile_north_african"]),
        ("coptic_nubian_textual_transition", "New religious texts and languages entered older Nile scribal landscapes through monasteries, courts, and local translators.", SOURCE["nile_north_african"]),
        ("late_african_monastic_libraries", "Monastic and episcopal communities preserved manuscripts, medical practice, legal memory, and regional correspondence.", SOURCE["nile_north_african"]),
    ),
    ("statecraft", "subsaharan"): (
        ("middle_niger_urban_councils", "Middle Niger communities coordinated clustered settlement, floodplain use, craft quarters, exchange, and lineage authority without invented monarchies.", SOURCE["subsaharan"]),
        ("sahel_iron_cattle_compacts", "Savanna leaders connected iron specialists, herders, cultivators, river crossings, and seasonal assemblies through reciprocal obligations.", SOURCE["subsaharan"]),
        ("forest_savanna_district_networks", "Forest-edge and savanna communities organized land, ritual, craft custody, and dispute settlement through layered local authorities.", SOURCE["subsaharan"]),
        ("late_antique_niger_chad_polities", "Emergent regional centres coordinated tribute, markets, ritual legitimacy, and armed protection across Niger and Chad basin routes.", SOURCE["subsaharan"]),
    ),
    ("warfare", "subsaharan"): (
        ("savanna_iron_spear_musters", "Iron weapons, shield infantry, scouts, age grades, and cattle-supported logistics strengthened savanna defensive coalitions.", SOURCE["subsaharan"]),
        ("forest_corridor_war_parties", "Woodland forces relied on local guides, ambush, river movement, compact supply, and flexible household contingents.", SOURCE["subsaharan"]),
        ("sahelian_mounted_screening", "Where ecology permitted, mounted scouts supplemented infantry musters, protected trade routes, and widened political warning networks.", SOURCE["subsaharan"]),
        ("regional_refuge_fortifications", "Earthworks, defended hilltops, stored food, ironworking households, and alliance musters protected late antique communities.", SOURCE["subsaharan"]),
    ),
    ("exchange", "subsaharan"): (
        ("niger_inland_delta_exchange", "River craft, floodplain food, pottery, iron, livestock, and craft specialists supported dense Middle Niger exchange.", SOURCE["subsaharan"]),
        ("sahel_forest_edge_corridors", "Iron, salt, livestock, grains, hides, and forest products moved through brokers linking ecological zones.", SOURCE["subsaharan"]),
        ("east_african_coastal_hinterlands", "Coastal and hinterland communities exchanged iron, ceramics, livestock, ivory, food, and imported goods without assuming later mercantile states.", SOURCE["subsaharan"]),
        ("late_niger_chad_market_networks", "Regional market places, river routes, porter relays, and protected crossings concentrated exchange across expanding settlement systems.", SOURCE["subsaharan"]),
    ),
}


def validate() -> None:
    profiles = {profile for _track, profile in OPENING_PATHS}
    expected = {
        (track, profile)
        for profile in profiles
        for track in (
            ("statecraft", "warfare", "exchange")
            if profile != "nile_north_african"
            else ("statecraft", "exchange", "learning")
        )
    }
    if set(OPENING_PATHS) != expected or set(LATER_PATHS) != expected:
        raise ValueError("Round 5 split-profile paths must cover exactly three tracks per profile")
    names = [name for path in OPENING_PATHS.values() for name in path]
    anchors = [row[0] for path in LATER_PATHS.values() for row in path]
    if any(len(path) != 5 for path in OPENING_PATHS.values()):
        raise ValueError("each Round 5 opening profile path must contain five nodes")
    if any(len(path) != 4 for path in LATER_PATHS.values()):
        raise ValueError("each Round 5 profile path must cover four later conceptual ages")
    if len(names) != len(set(names)) or len(anchors) != len(set(anchors)):
        raise ValueError("Round 5 split-profile node names and anchors must be unique")


validate()
