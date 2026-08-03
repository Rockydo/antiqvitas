#!/usr/bin/env python3
"""Generate Round 5's shared tribesmen-worker building layer and opening seeds."""
from __future__ import annotations

import argparse, csv, hashlib, json, subprocess, sys
from collections import defaultdict
from io import StringIO
from pathlib import Path
from PIL import Image, ImageDraw

from m5_regional_buildings import good_prices

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"in_game/common/building_types/00_antiquitas_r5_tribal_buildings.txt"
LEDGER=ROOT/"docs/m5/tribal_buildings.csv"
SEEDS=ROOT/"docs/m5/tribal_building_seeds.csv"
SOURCES=ROOT/"assets_queue/generated_sources/tribal_buildings"
MASTERS=ROOT/"assets_queue/generated/tribal_buildings"
ICONS=ROOT/"main_menu/gfx/interface/icons/buildings"
CONTACT=ROOT/"docs/m5/TRIBAL_BUILDING_ICON_CONTACT.png"
DDS=ROOT/"tools/dds.py"
ROSTER=ROOT/"docs/world_1ad/polities.csv"
OWNERSHIP=ROOT/"docs/world_1ad/ownership_resolved.csv"
TAG_PROFILES=ROOT/"docs/m4/tag_profiles.csv"
REGIONAL_PROFILES=ROOT/"docs/m4/regional_profiles.csv"
CULTURES=ROOT/"docs/m4/cultures.csv"
LANGS=("english","french","german","spanish","polish","russian","braz_por","simp_chinese","japanese","korean","turkish")
BRANCHES=("subsistence","pastoral","craft","exchange","ritual","warrior")

# Rows follow the twelve reviewed four-up source sheets in lexical sheet/cell order.
# Gate vocabulary is rendered to locally verified location-scope triggers below.
CATALOG=(
 ("grain_patch","Grain Patch","subsistence","wheat","0.22","farmland","P12.1;P12.3","Small mixed grain plots worked by free and kindred households."),
 ("pulse_garden","Pulse Garden","subsistence","legumes","0.21","any","P12.1;P12.3","Legume gardens support household subsistence and soil recovery."),
 ("tuber_mounds","Tuber Mounds","subsistence","potato","0.20","america","P8.10;P12.1","American mound cultivation represents locally appropriate tuber husbandry."),
 ("floodplain_plots","Floodplain Plots","subsistence","millet","0.22","river","P12.1;P12.3","Seasonally renewed alluvium supports bounded household plots."),
 ("forest_garden","Forest Garden","subsistence","fruit","0.19","forest","P12.1;PER","Managed woodland edges yield fruit without clearing a full field system."),
 ("nut_grove","Nut Grove","subsistence","antq_tree_nuts","0.18","forest","P12.1;P14;PER","Nut-bearing trees provide a durable gathered and managed food source."),
 ("fishing_weir","Fishing Weir","subsistence","fish","0.20","river","P12.1;P12.3","Stake-and-basket weirs harvest predictable river runs."),
 ("shellfish_camp","Shellfish Camp","subsistence","fish","0.18","coast","P12.1;P12.3","A seasonal shoreline shelter supports shellfish and inshore gathering."),
 ("cattle_fold","Cattle Fold","pastoral","livestock","0.20","pasture","P8.5;P12.1","Wattle folds protect cattle and organize dung, milking, and exchange."),
 ("small_stock_enclosure","Small-Stock Enclosure","pastoral","wool","0.20","dry_pasture","P8.2;P8.5;P12.1","A dry-stone fold supports sheep and goats in marginal grazing lands."),
 ("horse_herd_camp","Horse-Herd Camp","pastoral","horses","0.16","pasture","P8.2;P8.8;P12.1","A mobile herding camp maintains remounts without a state stud system."),
 ("camel_camp","Camel Camp","pastoral","antq_camels","0.15","arid","P8.2;P8.5;P12.1","Watered corrals and woven windbreaks sustain caravan camels."),
 ("reindeer_corral","Reindeer Corral","pastoral","wild_game","0.15","cold","P8.7;P12.1","Northern households manage reindeer access and seasonal gathering."),
 ("woodland_pannage","Woodland Pannage","pastoral","livestock","0.18","forest","P8.7;P12.1","Woodland grazing turns mast and undergrowth into household livestock."),
 ("transhumance_station","Transhumance Station","pastoral","wool","0.18","upland","P8.1;P8.4;P8.5;P12.1","A seasonal upland station anchors recurring herd movements."),
 ("fodder_meadow","Fodder Meadow","pastoral","livestock","0.17","grassland","P12.1;P12.3","Cut hay and managed meadow extend the winter endurance of herds."),
 ("household_loom","Household Loom","craft","cloth","0.16","any","P12.1;P12.3","Household looms turn local fibre and wool into coarse cloth."),
 ("hide_curing_rack","Hide-Curing Rack","craft","leather","0.15","any","P12.1;P12.3","Scraping, smoking, and stretching preserve hides for local use."),
 ("bone_antler_workshop","Bone and Antler Workshop","craft","tools","0.12","cold_forest","P8.7;P12.1","Bone and antler are shaped into awls, combs, handles, and fittings."),
 ("pottery_hearth","Pottery Hearth","craft","pottery","0.17","any","P12.1;P12.3","Open firing and hand-building supply coarse household vessels."),
 ("charcoal_clamp","Charcoal Clamp","craft","coal","0.12","forest","P12.1;P12.3","Earth-covered clamps provide small quantities of controlled charcoal."),
 ("bloomery_hearth","Bloomery Hearth","craft","iron","0.10","upland","P8.7;P12.1;P12.3","A low shaft hearth produces rough blooms for local smithing."),
 ("basketry_shelter","Basketry Shelter","craft","furniture","0.14","wet_or_forest","P12.1;P12.3","Reed and wicker work supplies containers, mats, and light furnishings."),
 ("dugout_canoe_yard","Dugout Canoe Yard","craft","naval_supplies","0.12","water","P8.9;P12.1","Adzes and controlled fire hollow timber for local watercraft."),
 ("raised_granary","Raised Granary","exchange","","0","any","P12.1;P12.3","Raised storage reduces damp, vermin, and seasonal food loss."),
 ("storage_pits","Lined Storage Pits","exchange","","0","any","P12.1;P12.3","Covered clay-lined pits preserve grain and roots between seasons."),
 ("cattle_exchange","Cattle Exchange Ground","exchange","","0","pasture","P8.5;P8.7;P12.1","A bounded meeting ground regularizes livestock exchange and restitution."),
 ("river_landing","River Landing","exchange","","0","river","P8.7;P8.9;P12.1","A log landing links canoes, baskets, and short-haul river exchange."),
 ("portage_station","Portage Station","exchange","","0","forest_river","P8.7;P12.1","Rollers and cached gear reduce the cost of recurring overland carries."),
 ("salt_exchange","Salt Exchange Place","exchange","","0","any","P12.1;P12.3","Trusted measures and storage support exchange in essential salt."),
 ("caravan_camp","Caravan Camp","exchange","","0","dry_pasture","P8.2;P8.5;P12.1","A guarded watering and loading place supports modest caravan traffic."),
 ("guest_hall","Communal Guest Hall","exchange","","0","any","P8.7;P12.1","Collective hospitality sustains envoys, traders, and reciprocal obligations."),
 ("assembly_ground","Assembly Ground","ritual","","0","any","P8.7;P11","A speaking stone and timber benches structure public deliberation."),
 ("sacred_grove","Sacred Grove Precinct","ritual","","0","forest","P8.7;P11","A bounded grove protects offerings and customary ritual access."),
 ("ancestor_house","Ancestor House","ritual","","0","any","P8.9;P11","A small custodial house preserves lineage offerings and memory."),
 ("feast_hall","Communal Feast Hall","ritual","","0","any","P8.7;P11","Shared feasting turns stored produce into obligation and prestige."),
 ("mound_precinct","Mound Precinct","ritual","","0","flatland","P8.10;P11","A raised ceremonial place anchors periodic gatherings and offerings."),
 ("oath_stone","Oath-Stone Place","ritual","","0","any","P8.7;P11","Witnessed oaths at a recognized stone reinforce negotiated settlements."),
 ("initiation_lodge","Initiation Lodge","ritual","","0","any","P8.5;P8.9;P11","A secluded lodge supports age-grade and custodial rites."),
 ("council_enclosure","Council Enclosure","ritual","","0","any","P8.7;P11","A wattle enclosure gives elders and household heads a durable council place."),
 ("warrior_lodge","Warrior Lodge","warrior","","0","any","P8.7;P13","A modest lodge stores shields and organizes household retainers."),
 ("palisade_ring","Palisade Ring","warrior","","0","any","P8.7;P13","A timber ring protects people, livestock, and stored produce in raids."),
 ("hill_refuge","Hill Refuge","warrior","","0","upland","P8.1;P8.7;P13","A small earth-and-timber refuge uses difficult ground rather than masonry."),
 ("watch_mound","Watch Mound","warrior","","0","flatland","P8.7;P13","A raised lookout and signal fire warn dispersed settlements."),
 ("shield_workshop","Shield Workshop","warrior","weaponry","0.10","any","P8.7;P13","Timber, hide, and fittings become shields for local musters."),
 ("spear_forge","Spear Forge","warrior","weaponry","0.11","upland","P8.7;P13","A small hearth and shaft rack supply spearheads and repairs."),
 ("horse_muster","Horse Muster Ground","warrior","","0","pasture","P8.2;P8.8;P13","A fenced muster assembles mounts, tack, and lances for short campaigns."),
 ("river_barricade","River Barricade","warrior","","0","river","P8.7;P8.9;P13","Chained logs and piles obstruct hostile craft at a defended crossing."),
)

REGIONAL_CATALOG=(
 ("med_terraces","Dry-Stone Cultivation Terraces","subsistence","fruit","0.18","upland","mediterranean","antq_italic_group|antq_hellenic_group|antq_iberian_group|antq_balkan_group|antq_anatolian_group|antq_semitic_group|antq_caucasian_group","P8.1;P12.1","Terraces conserve scarce soil for vines, grain, and household orchards."),
 ("med_hill_cistern","Rock-Cut Hill Cistern","exchange","","0","dry_pasture","mediterranean","antq_italic_group|antq_hellenic_group|antq_iberian_group|antq_balkan_group|antq_anatolian_group|antq_semitic_group|antq_caucasian_group","P8.1;P12.1","Cut stone and runoff channels secure hill-community water."),
 ("med_lineage_press","Lineage Press Shelter","craft","wine","0.16","dry_pasture","mediterranean","antq_italic_group|antq_hellenic_group|antq_iberian_group|antq_balkan_group|antq_anatolian_group|antq_semitic_group|antq_caucasian_group","P8.1;P12.1","A household beam press processes olives and grapes below urban scale."),
 ("med_hillfort_gate","Dry-Stone Hillfort Gate","warrior","","0","upland","mediterranean","antq_italic_group|antq_hellenic_group|antq_iberian_group|antq_balkan_group|antq_anatolian_group|antq_semitic_group|antq_caucasian_group","P8.1;P13","A timber gate closes a regional dry-stone refuge."),
 ("north_bog_iron","Bog-Iron Hearth","craft","iron","0.10","wet_or_forest","northern_forest","antq_celtic_group|antq_germanic_group|antq_baltic_group|antq_slavic_group|antq_uralic_group","P8.7;P12.1","Small furnaces turn gathered bog ore into rough blooms."),
 ("north_amber_shelter","Amber Exchange Shelter","exchange","","0","coast","northern_forest","antq_celtic_group|antq_germanic_group|antq_baltic_group|antq_slavic_group|antq_uralic_group","P8.7;P12.1","Sorted amber and trusted weights sustain northern coastal exchange."),
 ("north_causeway","Timber Bog Causeway","exchange","","0","wet_or_forest","northern_forest","antq_celtic_group|antq_germanic_group|antq_baltic_group|antq_slavic_group|antq_uralic_group","P8.7;P12.1","Split-log trackways connect settlements across saturated ground."),
 ("north_warband_hall","Northern Warband Hall","warrior","","0","cold_forest","northern_forest","antq_celtic_group|antq_germanic_group|antq_baltic_group|antq_slavic_group|antq_uralic_group","P8.7;P13","A low log hall stores arms and hosts a chieftain's retainers."),
 ("steppe_felt_camp","Felt-Tent Encampment","exchange","","0","pasture","iranian_steppe","antq_iranian_group|antq_steppe_group","P8.2;P8.8","Portable felt dwellings keep a mobile community supplied."),
 ("steppe_mare_camp","Mare-Herd Camp","pastoral","livestock","0.18","pasture","iranian_steppe","antq_iranian_group|antq_steppe_group","P8.2;P8.8","Tethering and leather vessels support horse-herd dairy production."),
 ("steppe_kurgan_moot","Kurgan Assembly Precinct","ritual","","0","pasture","iranian_steppe","antq_iranian_group|antq_steppe_group","P8.2;P8.8;P11","An ancestral mound anchors assemblies and offerings."),
 ("steppe_bowyer","Composite-Bow Shelter","warrior","weaponry","0.10","dry_pasture","iranian_steppe","antq_iranian_group|antq_steppe_group","P8.2;P8.8;P13","Horn, sinew, wood, and glue become compact recurved bows."),
 ("nile_wadi_cistern","Wadi Runoff Cistern","exchange","","0","arid","nile_sahara","antq_nile_group|antq_berber_group","P8.5;P12.1","Diversion walls capture episodic runoff for people and herds."),
 ("nile_reed_fishery","Reed-Channel Fishery","subsistence","fish","0.18","river","nile_sahara","antq_nile_group|antq_berber_group","P8.5;P12.1","Papyrus screens and traps organize shallow-water fishing."),
 ("nile_caravan_well","Desert Caravan Well","exchange","","0","arid","nile_sahara","antq_nile_group|antq_berber_group","P8.5;P12.1","A maintained well and trough sustain bounded desert movement."),
 ("nile_route_watch","Rocky-Route Watch","warrior","","0","arid","nile_sahara","antq_nile_group|antq_berber_group","P8.5;P13","A low enclosure and signal fire guard a difficult approach."),
 ("ssa_yam_fields","Yam Mound Fields","subsistence","fruit","0.18","wet_or_forest","subsaharan","antq_subsaharan_group","P8.5;P12.1","Mounded cultivation supports intensive household root crops."),
 ("ssa_smelting_court","Iron-Smelting Court","craft","iron","0.11","any","subsaharan","antq_subsaharan_group","P8.5;P12.1","Multiple clay furnaces organize skilled bloomery production."),
 ("ssa_cattle_kraal","Long-Horn Cattle Kraal","pastoral","livestock","0.19","pasture","subsaharan","antq_subsaharan_group","P8.5;P12.1","A thorn-and-wattle kraal protects cattle and concentrates manure."),
 ("ssa_lineage_compound","Lineage Courtyard Compound","ritual","","0","any","subsaharan","antq_subsaharan_group","P8.5;P11","Related households share storage, ritual duties, and a central court."),
 ("indic_millet_terraces","Contour Millet Terraces","subsistence","millet","0.20","upland","indic_highland","antq_indian_group|antq_tibetan_group","P8.4;P12.1","Contour bunds stabilize humid and highland grain plots."),
 ("indic_monsoon_tank","Community Monsoon Tank","exchange","","0","river","indic_highland","antq_indian_group|antq_tibetan_group","P8.4;P12.1","An earthen tank stores seasonal rainfall outside state irrigation."),
 ("indic_cotton_veranda","Household Cotton Veranda","craft","cloth","0.16","warm","indic_highland","antq_indian_group|antq_tibetan_group","P8.4;P12.1","A shaded household loom turns local cotton into coarse cloth."),
 ("indic_clan_stockade","Clan Stockade","warrior","","0","upland","indic_highland","antq_indian_group|antq_tibetan_group","P8.4;P13","Timber and earth protect a hill or forest community."),
 ("east_millet_terraces","Dryland Millet Terraces","subsistence","millet","0.20","upland","east_asian","antq_sinitic_group|antq_korean_group|antq_japonic_group","P8.3;P12.1","Earthen bunds stabilize dryland millet on frontier slopes."),
 ("east_raised_granary","Rammed-Earth Raised Granary","exchange","","0","any","east_asian","antq_sinitic_group|antq_korean_group|antq_japonic_group","P8.3;P12.1","A raised store combines rammed earth with a timber superstructure."),
 ("east_lacquer_bamboo","Lacquer and Bamboo Workshop","craft","furniture","0.12","forest","east_asian","antq_sinitic_group|antq_korean_group|antq_japonic_group","P8.3;P12.1","Household specialists finish bamboo and wooden vessels."),
 ("east_beacon","Frontier Beacon Platform","warrior","","0","flatland","east_asian","antq_sinitic_group|antq_korean_group|antq_japonic_group","P8.3;P13","A rammed-earth platform relays smoke and fire warnings."),
 ("ocean_stilt_granary","Island Stilt Granary","exchange","","0","coast","austronesian","antq_austronesian_group|antq_oceanic_group|antq_southeast_asian_group|antq_north_maluku_group","P8.9;P12.1","A lashed high-floor granary protects food from damp and pests."),
 ("ocean_outrigger_yard","Outrigger-Canoe Yard","craft","naval_supplies","0.12","coast","austronesian","antq_austronesian_group|antq_oceanic_group|antq_southeast_asian_group|antq_north_maluku_group","P8.9;P12.1","Lashed booms and carved hulls support regional island voyaging."),
 ("ocean_sago_grove","Managed Sago Grove","subsistence","fruit","0.18","wet_or_forest","austronesian","antq_austronesian_group|antq_oceanic_group|antq_southeast_asian_group|antq_north_maluku_group","P8.9;P12.1","Managed palms provide storable starch in wet tropical settings."),
 ("ocean_shell_exchange","Shell-Valuables Shelter","exchange","","0","coast","austronesian","antq_austronesian_group|antq_oceanic_group|antq_southeast_asian_group|antq_north_maluku_group","P8.9;P12.1","Drilled shells and woven mats mediate island obligations and exchange."),
 ("america_raised_fields","American Raised Fields","subsistence","maize","0.20","wetlands","american","antq_american_group|antq_mesoamerican_group|antq_andean_group","P8.10;P12.1","Raised beds and channels intensify maize and squash cultivation."),
 ("america_obsidian_shelter","Obsidian Workshop","craft","tools","0.10","upland","american","antq_american_group|antq_mesoamerican_group|antq_andean_group","P8.10;P12.1","Pressure flaking turns volcanic glass into blades and points."),
 ("america_mound_plaza","Earthen Mound Plaza","ritual","","0","flatland","american","antq_american_group|antq_mesoamerican_group|antq_andean_group","P8.10;P11","A low mound and open plaza organize ceremony without later monumental forms."),
 ("america_palisaded_village","Palisaded Village Cluster","warrior","","0","any","american","antq_american_group|antq_mesoamerican_group|antq_andean_group","P8.10;P13","A timber enclosure protects clustered houses and stores."),
)

FIELDS=("key","name","branch","scope","profiles","produced","output","gate","max_levels","source","confidence","note","icon_sheet","icon_cell")
CELLS=("top_left","top_right","bottom_left","bottom_right")

def rows():
    result=[]
    for index,(slug,name,branch,produced,output,gate,source,note) in enumerate(CATALOG):
        result.append({"key":f"antq_trib_{slug}","name":name,"branch":branch,"scope":"shared","profiles":"ALL","produced":produced,"output":output,"gate":gate,"max_levels":"2","source":source,"confidence":"contested","note":note,"icon_sheet":f"tribal_sheet_{index//4+1:02d}.png","icon_cell":CELLS[index%4]})
    for offset,(slug,name,branch,produced,output,gate,profile,groups,source,note) in enumerate(REGIONAL_CATALOG,start=len(CATALOG)):
        result.append({"key":f"antq_trib_{slug}","name":name,"branch":branch,"scope":"regional","profiles":groups,"produced":produced,"output":output,"gate":gate,"max_levels":"2","source":source,"confidence":"contested","note":note,"icon_sheet":f"tribal_sheet_{offset//4+1:02d}.png","icon_cell":CELLS[offset%4]})
    return result

def csv_text(entries):
    s=StringIO(newline=""); w=csv.DictWriter(s,fieldnames=FIELDS,lineterminator="\n"); w.writeheader(); w.writerows(entries); return s.getvalue()

def gate_lines(gate):
    table={
      "any":[], "farmland":["\t\tvegetation = farmland"],
      "river":["\t\thas_river = yes"], "coast":["\t\tis_port = yes"],
      "water":["\t\tOR = {","\t\t\thas_river = yes","\t\t\tis_port = yes","\t\t}"],
      "forest":["\t\tOR = {","\t\t\tvegetation = woods","\t\t\tvegetation = forest","\t\t\tvegetation = jungle","\t\t}"],
      "pasture":["\t\tOR = {","\t\t\tvegetation = grasslands","\t\t\tvegetation = sparse","\t\t\tvegetation = farmland","\t\t}"],
      "grassland":["\t\tOR = {","\t\t\tvegetation = grasslands","\t\t\tvegetation = farmland","\t\t}"],
      "arid":["\t\tOR = {","\t\t\tclimate = arid","\t\t\tclimate = cold_arid","\t\t}"],
      "dry_pasture":["\t\tOR = {","\t\t\tclimate = arid","\t\t\tclimate = cold_arid","\t\t\tvegetation = sparse","\t\t\tvegetation = grasslands","\t\t}"],
      "cold":["\t\tOR = {","\t\t\tclimate = arctic","\t\t\tclimate = continental","\t\t\tclimate = cold_arid","\t\t}"],
      "upland":["\t\tOR = {","\t\t\ttopography = hills","\t\t\ttopography = plateau","\t\t\ttopography = mountains","\t\t}"],
      "flatland":["\t\tOR = {","\t\t\ttopography = flatland","\t\t\ttopography = hills","\t\t}"],
      "america":["\t\tcontinent = continent:america"],
      "warm":["\t\tOR = {","\t\t\tclimate = tropical","\t\t\tclimate = subtropical","\t\t\tclimate = arid","\t\t\tclimate = mediterranean","\t\t}"],
      "wetlands":["\t\ttopography = wetlands"],
      "cold_forest":["\t\tOR = {","\t\t\tclimate = arctic","\t\t\tclimate = continental","\t\t\tvegetation = woods","\t\t\tvegetation = forest","\t\t}"],
      "wet_or_forest":["\t\tOR = {","\t\t\ttopography = wetlands","\t\t\tvegetation = woods","\t\t\tvegetation = forest","\t\t\tvegetation = jungle","\t\t}"],
      "forest_river":["\t\tOR = {","\t\t\thas_river = yes","\t\t\tvegetation = woods","\t\t\tvegetation = forest","\t\t}"],
    }
    if gate not in table: raise ValueError(f"unknown tribal ecology gate {gate}")
    return table[gate]

def profile_lines(entry):
    if entry["scope"]=="shared": return []
    groups=entry["profiles"].split("|")
    return ["\t\tOR = {",*(f"\t\t\tdominant_culture = {{ has_culture_group = culture_group:{group} }}" for group in groups),"\t\t}"]

def upkeep(entry):
    if entry["produced"]:
        prices=good_prices(); gross=prices[entry["produced"]]*float(entry["output"]); target=gross/1.20
        return [("tools",target*.25/prices["tools"]),("lumber",target*.35/prices["lumber"]),("livestock",target*.40/prices["livestock"])]
    return [("tools",.012),("lumber",.035),("leather",.010)]

def building_text(entries):
    lines=["# Generated by tools/r5_tribal_buildings.py --write.","# Shared AD 1 tribesmen-worker economy; low caps and modest outputs preserve settled advantages.",""]
    category={"subsistence":"rgo_building_category","pastoral":"rgo_building_category","craft":"basic_industry_category","exchange":"trade_category","ritual":"cultural_category","warrior":"military_category"}
    build={"subsistence":("rural_build_time","farm_constructions"),"pastoral":("rural_build_time","horse_breeders_construction"),"craft":("workshop_build_time","guild_construction"),"exchange":("village_build_time","basic_construction_needs"),"ritual":("cultural_building_time","prestige_building_construction"),"warrior":("small_fort_building","stockade_construction")}
    for e in entries:
        key=e["key"]; bt,demand=build[e["branch"]]
        lines += [f"{key} = {{","\taudio_tier = 1","\tis_foreign = no","\tpop_type = tribesmen",f"\tcategory = {category[e['branch']]}","\temployment_size = generic_tribesmen_employment","\trural_settlement = yes","\ttown = yes","\tcity = yes","\tmegalopolis = yes",f"\tbuild_time = {bt}",f"\tmax_levels = {e['max_levels']}","\tlocation_potential = {",*gate_lines(e["gate"]),*profile_lines(e),"\t}","\tunique_production_methods = {",f"\t\t{key}_maintenance = {{"]
        lines += [f"\t\t\t{good} = {amount:.4f}" for good,amount in upkeep(e)]
        if e["produced"]: lines += [f"\t\t\tproduced = {e['produced']}",f"\t\t\toutput = {e['output']}","\t\t\tdebug_max_profit = rural_profit_margin"]
        lines += ["\t\t\tcategory = building_maintenance","\t\t}","\t}","\tmodifier = {"]
        modifiers={"subsistence":("\t\tlocal_food_capacity = 10","\t\tlocal_monthly_food_modifier = 0.005"),"pastoral":("\t\tlocal_food_capacity = 6","\t\tlocal_population_capacity = 3"),"craft":("\t\tlocal_production_efficiency = 0.01",),"exchange":("\t\tlocal_merchant_capacity = 0.10","\t\tlocal_merchant_power = 0.01"),"ritual":("\t\tlocal_unrest = -0.02","\t\tlocal_cultural_tradition = 0.01"),"warrior":("\t\tlocal_manpower = 0.005","\t\tlocal_garrison_size = 0.01","\t\tcan_recruit_regiment_in_this_location = yes")}
        lines += [*modifiers[e["branch"]],"\t}",f"\tconstruction_demand = {demand}","\tcustom_tags = { antq_tribal_building }","}",""]
    return "\n".join(lines)

def loc_text(language,entries):
    lines=[f"l_{language}:"]
    for e in entries:
        lines += [f' {e["key"]}:0 "{e["name"]}"',f' {e["key"]}_desc:0 "{e["note"]}"',f' {e["key"]}_maintenance:0 "{e["name"]} Upkeep"']
    return "\ufeff"+"\n".join(lines)+"\n"

def owner_rows():
    with OWNERSHIP.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))

def seed_rows(entries):
    opening=("antq_trib_raised_granary","antq_trib_household_loom","antq_trib_assembly_ground","antq_trib_warrior_lodge")
    with ROSTER.open(encoding="utf-8-sig",newline="") as f: sops={r["tag"]:r for r in csv.DictReader(f) if r["kind"]=="sop"}
    with TAG_PROFILES.open(encoding="utf-8-sig",newline="") as f: tag_cultures={r["tag"]:r["culture"] for r in csv.DictReader(f)}
    with REGIONAL_PROFILES.open(encoding="utf-8-sig",newline="") as f: region_cultures={r["region"]:r["culture"] for r in csv.DictReader(f)}
    with CULTURES.open(encoding="utf-8-sig",newline="") as f: culture_groups={r["key"]:r["group"] for r in csv.DictReader(f)}
    owned=defaultdict(list)
    for r in owner_rows():
        if r["tag"] in sops: owned[r["tag"]].append(r["location"])
    result=[]
    for tag in sorted(sops):
        locations=sorted(set(owned[tag])); capital=sops[tag]["map_capital"]
        if capital in locations: locations.remove(capital); locations.insert(0,capital)
        if not locations: raise ValueError(f"SoP {tag} has no controlled location for tribal seeds")
        culture=tag_cultures.get(tag,region_cultures.get(sops[tag]["region"]))
        group=culture_groups.get(culture,"")
        regional=tuple(e["key"] for e in entries if e["scope"]=="regional" and group in e["profiles"].split("|"))
        if len(regional)!=4: raise ValueError(f"SoP {tag} culture {culture}/{group} has {len(regional)} regional tribal buildings")
        for index,building in enumerate((*opening,*regional)):
            result.append({"key":f"r5_trib_{tag.lower()}_{index+1}","tag":tag,"location":locations[index%len(locations)],"building":building,"level":"1","source":"P8.7;P12.1;P13","confidence":"contested","note":"Balanced collective-polity opening package; not an excavated structure claim."})
    return result

def seed_csv(entries):
    fields=("key","tag","location","building","level","source","confidence","note"); s=StringIO(newline=""); w=csv.DictWriter(s,fieldnames=fields,lineterminator="\n"); w.writeheader(); w.writerows(seed_rows(entries)); return s.getvalue()

def art(entries):
    MASTERS.mkdir(parents=True,exist_ok=True); ICONS.mkdir(parents=True,exist_ok=True); previews=[]
    for index,e in enumerate(entries):
        source=SOURCES/e["icon_sheet"]
        if not source.is_file(): continue
        with Image.open(source) as im:
            rgba=im.convert("RGBA"); w,h=rgba.size
            if w!=h or w<1024: raise ValueError(f"bad tribal four-up source {source.name}: {rgba.size}")
            half=w//2; gap=max(2,w//512); q=index%4; x=q%2; y=q//2
            box=(x*half+(gap if x else 0),y*half+(gap if y else 0),(x+1)*half-(gap if not x else 0),(y+1)*half-(gap if not y else 0))
            icon=rgba.crop(box).resize((128,128),Image.Resampling.LANCZOS)
        master=MASTERS/f"{e['key']}.png"; icon.save(master)
        subprocess.run([sys.executable,str(DDS),"convert",str(master),str(ICONS/f"{e['key']}.dds"),"--compression","dxt5"],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
        previews.append((e["key"],icon.copy()))
    if len(previews)==len(entries):
        canvas=Image.new("RGBA",(960,((len(entries)+5)//6)*180),(16,25,43,255)); d=ImageDraw.Draw(canvas)
        for i,(key,icon) in enumerate(previews):
            x=i%6*160+16; y=i//6*180+4; canvas.alpha_composite(icon,(x,y)); d.text((x,y+132),key[10:29],fill="white")
        canvas.convert("RGB").save(CONTACT)

def outputs(entries):
    return {OUT:building_text(entries),LEDGER:csv_text(entries),SEEDS:seed_csv(entries),**{ROOT/f"main_menu/localization/{lang}/antq_r5_tribal_buildings_l_{lang}.yml":loc_text(lang,entries) for lang in LANGS}}

def write(entries):
    for path,content in outputs(entries).items(): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(content,encoding="utf-8-sig" if path.suffix!=".yml" else "utf-8",newline="\n")
    art(entries)

def check(entries):
    failures=[]; goods=set(json.loads((ROOT/"docs/vanilla_symbols/good.json").read_text())); goods.update(r["key"] for r in csv.DictReader((ROOT/"docs/m5/custom_goods.csv").open(encoding="utf-8-sig",newline="")))
    shared=[e for e in entries if e["scope"]=="shared"]; regional=[e for e in entries if e["scope"]=="regional"]
    if len(shared)!=48 or len(regional)!=36 or {e["branch"] for e in entries}!=set(BRANCHES): failures.append("tribal catalogue must contain 48 shared and 36 regional rows across six branches")
    if any(sum(e["branch"]==b for e in shared)!=8 for b in BRANCHES): failures.append("each shared tribal branch must contain exactly eight buildings")
    with CULTURES.open(encoding="utf-8-sig",newline="") as f: all_groups={r["group"] for r in csv.DictReader(f)}
    regional_groups={group for e in regional for group in e["profiles"].split("|")}
    if regional_groups!=all_groups: failures.append(f"regional tribal culture-group coverage drift missing={sorted(all_groups-regional_groups)} extra={sorted(regional_groups-all_groups)}")
    if len({e["key"] for e in entries})!=len(entries): failures.append("duplicate tribal building key")
    if {e["produced"] for e in entries if e["produced"]}-goods: failures.append("tribal catalogue uses unknown produced goods")
    for path,content in outputs(entries).items():
        if not path.is_file() or path.read_text(encoding="utf-8-sig")!=content.lstrip("\ufeff"): failures.append(f"stale {path.relative_to(ROOT)}")
    hashes={}
    for e in entries:
        for p in (SOURCES/e["icon_sheet"],MASTERS/f"{e['key']}.png",ICONS/f"{e['key']}.dds"):
            if not p.is_file(): failures.append(f"missing tribal art {p.relative_to(ROOT)}")
        p=ICONS/f"{e['key']}.dds"
        if p.is_file():
            h=hashlib.sha256(p.read_bytes()).hexdigest()
            if h in hashes: failures.append(f"tribal icon alias {hashes[h]} / {e['key']}")
            hashes[h]=e["key"]
    seeds=seed_rows(entries); counts=defaultdict(int)
    for seed in seeds: counts[seed["tag"]]+=1
    if len(counts)!=337 or set(counts.values())!={8}: failures.append(f"SoP opening tribal placement coverage drift: tags={len(counts)} counts={sorted(set(counts.values()))}")
    if not CONTACT.is_file(): failures.append("tribal icon contact sheet missing")
    if failures: raise ValueError("\n".join(failures))

def main():
    p=argparse.ArgumentParser(); p.add_argument("--write",action="store_true"); p.add_argument("--check",action="store_true"); a=p.parse_args()
    if a.write==a.check: p.error("choose exactly one")
    try:
        entries=rows()
        if a.write: write(entries)
        check(entries)
    except (OSError,ValueError,csv.Error,subprocess.CalledProcessError) as exc: print(f"r5_tribal_buildings: FAIL\n  - {exc}"); return 1
    print(f"r5_tribal_buildings: PASS (48 shared + 36 regional tribesmen buildings; {len(seed_rows(entries))} SoP placements; 21 four-up sheets)"); return 0
if __name__=="__main__": raise SystemExit(main())
