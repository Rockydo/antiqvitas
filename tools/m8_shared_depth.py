#!/usr/bin/env python3
"""Broadly transferable ancient-practice nodes used to deepen every profile."""

from __future__ import annotations


# These are adoption opportunities, not claims that every society began with an
# identical institution. Subjects stay at the level of materially widespread
# practices that could move between unrelated ancient political settings.
SHARED_DEPTH_BY_AGE: tuple[tuple[tuple[str, str, str, str], ...], ...] = (
    (
        ("community_granary_customs", "society", "Community Granary Customs", "Households pooled durable food reserves under locally witnessed rules for contribution, access, and replenishment."),
        ("seasonal_labour_calendars", "learning", "Seasonal Labour Calendars", "Observed rains, floods, migrations, and crop cycles organized recurring work without requiring a written calendar."),
        ("field_boundary_witnesses", "statecraft", "Field Boundary Witnesses", "Recognized neighbours and elders preserved boundaries through remembered markers, testimony, and periodic inspection."),
        ("river_crossing_guides", "warfare", "River Crossing Guides", "Local pilots identified fords, currents, landing places, and seasonal hazards for travellers and armed hosts."),
        ("market_day_signals", "exchange", "Market-Day Signals", "Regular gatherings used visible or audible signals to coordinate exchange across dispersed settlements."),
        ("well_and_cistern_care", "society", "Well and Cistern Care", "Shared labour kept wells, cisterns, springs, and their access paths clean and serviceable."),
        ("craft_apprentice_households", "learning", "Craft Apprentice Households", "Specialist households transmitted tool use, material selection, and workshop routines through supervised practice."),
        ("muster_ground_markers", "warfare", "Muster-Ground Markers", "Known assembly places and route markers reduced delay when household contingents gathered for defence."),
        ("trusted_route_brokers", "exchange", "Trusted Route Brokers", "Intermediaries joined unfamiliar traders to local hosts, measures, languages, and customary guarantees."),
        ("gift_and_tribute_tallies", "statecraft", "Gift and Tribute Tallies", "Tokens, notched objects, or remembered witness lists tracked recurring gifts and negotiated contributions."),
        ("healing_plant_memory", "learning", "Healing-Plant Memory", "Practitioners preserved tested knowledge of local plants, preparation methods, seasons, and harmful substitutes."),
    ),
    (
        ("relay_rest_stations", "exchange", "Relay Rest Stations", "Maintained stopping places concentrated water, shelter, route knowledge, and replacement labour along busy corridors."),
        ("sealed_storage_customs", "statecraft", "Sealed Storage Customs", "Witnessed seals, knots, marks, and guarded thresholds made communal stores easier to audit."),
        ("watch_fire_signals", "warfare", "Watch-Fire Signals", "Prepared signal points passed warnings between settlements faster than ordinary messengers."),
        ("canal_and_ditch_musters", "society", "Canal and Ditch Musters", "Recurring work parties cleared irrigation, drainage, and boundary channels before seasonal demand."),
        ("travelling_healers", "learning", "Travelling Healers", "Mobile practitioners compared remedies, injuries, and treatment routines across several communities."),
        ("portage_team_organization", "exchange", "Portage-Team Organization", "Coordinated carriers moved boats and cargo around rapids, shallows, divides, and broken roads."),
        ("public_measure_stones", "statecraft", "Public Measure Stones", "Recognized reference weights or volumes reduced disputes without imposing one universal ancient standard."),
        ("reserve_seed_stores", "society", "Reserve Seed Stores", "Protected seed stocks separated the next sowing from ordinary consumption and emergency redistribution."),
        ("scout_interpreter_networks", "warfare", "Scout-Interpreter Networks", "Guides able to cross linguistic and political frontiers improved warning, negotiation, and route selection."),
        ("fortified_store_compounds", "warfare", "Fortified Store Compounds", "Defended enclosures protected food, tools, and transport gear needed during concentrated campaigning."),
        ("regional_arbitration_meetings", "statecraft", "Regional Arbitration Meetings", "Periodic gatherings let recognized mediators settle disputes that crossed household or settlement boundaries."),
        ("specialist_tool_markets", "exchange", "Specialist Tool Markets", "Regular exchange connected metalworkers, woodworkers, farmers, fishers, and carriers to repairable equipment."),
        ("observational_weather_lore", "learning", "Observational Weather Lore", "Long observation of winds, clouds, animals, and water levels improved seasonal planning."),
        ("quarry_work_crews", "society", "Quarry Work Crews", "Specialized teams coordinated extraction, rough shaping, hauling, and safe access to useful stone."),
        ("boat_repair_yards", "exchange", "Boat Repair Yards", "Concentrated timber, fibre, pitch, tools, and skilled labour shortened repairs at busy landings."),
        ("campaign_fodder_stores", "warfare", "Campaign Fodder Stores", "Distributed feed and food reserves reduced the burden of sudden military concentration on nearby households."),
        ("itinerant_memory_specialists", "learning", "Itinerant Memory Specialists", "Reciters, teachers, and ritual experts carried genealogies, agreements, calendars, and technical lore between communities."),
    ),
    (
        ("emergency_grain_reserves", "society", "Emergency Grain Reserves", "Ring-fenced food stores supported communities through failed harvests, raids, displacement, and interrupted exchange."),
        ("refuge_route_markers", "warfare", "Refuge-Route Markers", "Known paths, water points, and concealed crossings guided non-combatants toward defensible refuges."),
        ("salvage_metal_workshops", "exchange", "Salvage-Metal Workshops", "Damaged tools, fittings, and weapons were sorted, reforged, and returned to use when fresh metal was scarce."),
        ("contingency_councils", "statecraft", "Contingency Councils", "Emergency gatherings assigned watches, stores, routes, and temporary authority during acute disruption."),
        ("mobile_field_stores", "warfare", "Mobile Field Stores", "Portable rations, repair materials, and containers followed campaigning groups beyond permanent depots."),
        ("guarded_market_enclosures", "exchange", "Guarded Market Enclosures", "Defined trading grounds and neutral guardians allowed exchange to continue amid local insecurity."),
        ("epidemic_burial_protocols", "society", "Epidemic Burial Protocols", "Communities organized additional burial labour and safer handling when ordinary funerary routines were overwhelmed."),
        ("water_ration_customs", "society", "Water-Ration Customs", "Negotiated turns and witnessed shares reduced conflict when wells, cisterns, or channels ran low."),
        ("replacement_tool_stocks", "exchange", "Replacement Tool Stocks", "Standard repair pieces and stored hand tools kept essential cultivation, transport, and construction moving."),
        ("local_warning_runners", "warfare", "Local Warning Runners", "Practised messengers linked outlying farms, watch points, refuges, and assembly grounds."),
        ("dispute_truce_days", "statecraft", "Dispute-Truce Days", "Recognized pauses in local feuds created safe occasions for arbitration, exchange, and shared repair work."),
        ("healer_exchange_circuits", "learning", "Healer Exchange Circuits", "Practitioners compared treatments and materia medica along pilgrimage, market, and kinship routes."),
        ("temporary_river_ferries", "exchange", "Temporary River Ferries", "Locally assembled boats, rafts, ropes, and crews restored movement where regular crossings failed."),
        ("surplus_seed_protection", "society", "Surplus Seed Protection", "Separate custody kept planting seed from being consumed or seized during short-term emergencies."),
        ("frontier_hostage_mediation", "statecraft", "Frontier Hostage Mediation", "Third-party custodians and customary guarantees reduced the risks of negotiated hostages and sureties."),
        ("fortress_repair_musters", "warfare", "Fortress Repair Musters", "Rapid labour levies restored gates, ditches, walls, and internal stores before renewed attack."),
        ("oral_crisis_chronicles", "learning", "Oral Crisis Chronicles", "Remembered sequences of famine, conflict, movement, and recovery preserved practical warnings for later generations."),
    ),
    (
        ("storehouse_oversight", "statecraft", "Storehouse Oversight", "Separated custody, witnessed issues, and periodic inspection made large collective stores harder to divert."),
        ("road_and_portage_inspections", "exchange", "Road and Portage Inspections", "Routine inspection identified broken surfaces, unsafe landings, blocked passes, and exhausted staging places."),
        ("river_embankment_musters", "society", "River-Embankment Musters", "Coordinated labour repaired banks, spillways, and drainage before damaging seasonal water."),
        ("settlement_watch_rotations", "warfare", "Settlement Watch Rotations", "Scheduled watches distributed warning duty across households while keeping gates and approaches observed."),
        ("trained_messenger_relays", "statecraft", "Trained Messenger Relays", "Known stages, replacement runners, and recognized credentials made official messages more dependable."),
        ("standard_ration_bundles", "warfare", "Standard Ration Bundles", "Predictable bundles of grain, preserved food, salt, and containers simplified short campaigns."),
        ("frontier_market_wards", "exchange", "Frontier Market Wards", "Separate market quarters and local guarantors managed visitors, tolls, storage, and disputes at political boundaries."),
        ("healing_house_endowments", "society", "Healing-House Endowments", "Durable gifts of food, space, labour, or income supported care beyond one healer's household."),
        ("craft_quality_witnesses", "statecraft", "Craft-Quality Witnesses", "Recognized specialists judged materials and workmanship in recurring public or institutional contracts."),
        ("reservoir_silt_clearance", "society", "Reservoir Silt Clearance", "Regular crews removed silt, repaired linings, and protected inlets to preserve stored water."),
        ("winter_fodder_planning", "warfare", "Winter Fodder Planning", "Advance allocation of feed and sheltered storage kept transport animals and herds viable through hard seasons."),
        ("customary_appeal_hearings", "statecraft", "Customary Appeal Hearings", "Higher or wider assemblies reconsidered disputes when ordinary local mediation failed."),
        ("regional_festival_calendars", "learning", "Regional Festival Calendars", "Coordinated ceremonial dates structured travel, exchange, labour pauses, and intercommunity obligations."),
        ("refuge_wall_maintenance", "warfare", "Refuge-Wall Maintenance", "Periodic repair kept occasional refuges defensible before an emergency rather than after one began."),
        ("long_distance_pilotage", "exchange", "Long-Distance Pilotage", "Experienced pilots combined seasonal winds, currents, landmarks, water sources, and political knowledge."),
        ("granary_pest_control", "learning", "Granary Pest Control", "Drying, cleaning, sealed containers, raised floors, and inspection reduced losses in stored food."),
        ("shared_work_obligations", "society", "Shared Work Obligations", "Negotiated labour shares sustained waterworks, roads, walls, storehouses, and sacred places without a permanent workforce."),
    ),
    (
        ("allied_contingent_musters", "warfare", "Allied Contingent Musters", "Separate forces coordinated assembly places, command signals, supplies, and agreed periods of service."),
        ("frontier_exchange_fairs", "exchange", "Frontier Exchange Fairs", "Protected periodic fairs linked communities divided by political authority, language, or recent conflict."),
        ("refuge_fortification", "warfare", "Refuge Fortification", "Earth, timber, stone, and reused materials strengthened defensible places for short periods of danger."),
        ("migrant_craft_settlements", "society", "Migrant Craft Settlements", "Incoming specialists established workshops while adapting their skills to local materials and patrons."),
        ("boat_bridge_teams", "exchange", "Boat-Bridge Teams", "Coordinated boats, rope, decking, anchors, and crews created temporary crossings for people and supplies."),
        ("mixed_custom_arbitration", "statecraft", "Mixed-Custom Arbitration", "Mediators reconciled differing legal memories, host obligations, and compensation customs in mixed settlements."),
        ("winter_quarter_stores", "warfare", "Winter-Quarter Stores", "Distributed food, fuel, bedding, and repair materials reduced destructive foraging around seasonal quarters."),
        ("hostage_exchange_guarantees", "statecraft", "Hostage-Exchange Guarantees", "Neutral custody, kinship ties, and witnessed terms made political sureties more predictable."),
        ("route_interpreter_households", "learning", "Route-Interpreter Households", "Multilingual households preserved practical knowledge of roads, markets, tolls, hosts, and diplomatic etiquette."),
    ),
    (
        ("resettlement_boundary_surveys", "statecraft", "Resettlement Boundary Surveys", "Witnessed walks and durable markers defined new fields, pastures, water access, and obligations after movement."),
        ("mobile_market_camps", "exchange", "Mobile Market Camps", "Temporary stalls, corrals, storage, and guarded meeting grounds followed shifting populations and routes."),
        ("portable_ritual_equipment", "society", "Portable Ritual Equipment", "Transportable vessels, textiles, emblems, and instruments sustained communal rites during displacement."),
        ("migrant_crop_exchanges", "learning", "Migrant Crop Exchanges", "Moving cultivators carried seeds and techniques while learning which varieties suited unfamiliar soils and seasons."),
        ("multilingual_brokers", "exchange", "Multilingual Brokers", "Intermediaries translated language, measures, gifts, guarantees, and political expectations between newcomers and hosts."),
        ("transport_train_repairs", "warfare", "Transport-Train Repairs", "Mobile smiths, woodworkers, leatherworkers, and rope makers kept carts, pack gear, boats, and containers serviceable."),
        ("river_crossing_flotillas", "warfare", "River-Crossing Flotillas", "Collected boats, rafts, pilots, rope, and landing crews moved large groups across difficult waterways."),
        ("dispersed_refuge_networks", "society", "Dispersed Refuge Networks", "Several small refuges, food caches, paths, and host communities reduced reliance on one vulnerable centre."),
        ("successor_toll_compacts", "statecraft", "Successor Toll Compacts", "Neighbouring authorities negotiated passage dues and safe conduct where older political systems had fragmented."),
    ),
)


EXPECTED_COUNTS = (11, 17, 17, 17, 9, 9)


def validate_catalog() -> None:
    if tuple(map(len, SHARED_DEPTH_BY_AGE)) != EXPECTED_COUNTS:
        raise ValueError("shared advance-density catalog has the wrong per-age counts")
    rows = [row for age in SHARED_DEPTH_BY_AGE for row in age]
    keys = [row[0] for row in rows]
    if len(rows) != 80 or len(keys) != len(set(keys)):
        raise ValueError("shared advance-density catalog must contain 80 unique nodes")
    if {row[1] for row in rows} != {
        "statecraft", "warfare", "exchange", "learning", "society"
    }:
        raise ValueError("shared advance-density catalog lost one or more tracks")
