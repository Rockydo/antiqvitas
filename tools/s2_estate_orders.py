#!/usr/bin/env python3
"""Render and audit polity-aware ancient estate identities and privileges."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image

from dates import M2_MIRROR_LANGUAGES
from dds import identify

ROOT = Path(__file__).resolve().parents[1]
PATHS = ROOT / "config/local_paths.json"
SOURCES = ROOT / "assets_queue/estate_orders/sources"
GENERATED_SOURCES = ROOT / "assets_queue/generated_sources"
MASTERS = ROOT / "assets_queue/generated"
DDS_TOOL = ROOT / "tools/dds.py"
CONTENT_LEDGER = ROOT / "docs/m6/estate_order_privileges.csv"
ART_LEDGER = ROOT / "docs/m6/estate_order_art.csv"
CUSTOM_LOC_OUT = ROOT / "in_game/common/customizable_localization/estates.txt"
BASE_CUSTOM_LOC_HASH = "5c91728a9faf2d3f656e15e7321aa3240bf90b14deea49b73ab688ddda420575"
ESTATES = ("crown_estate", "nobles_estate", "clergy_estate", "burghers_estate", "peasants_estate", "tribes_estate")

# profile|reforms|atlas|hash|sources|confidence|evidence boundary|six displayed order names
PROFILE_DATA = r"""
roman|antq_principate~antq_augustan_dyarchy~antq_provincial_principate~antq_flavian_imperial_settlement~antq_antonine_provincial_principate~antq_severan_military_principate|roman_orders_atlas.png|e68c0ea154a1aed7cc33e62febf23601128929cdf72d46b61c5f624d3d01dd12|P8.1;P11;P13;OCD|secure|Orders are engine participation categories; they do not make the Augustan orders equal corporate estates or the Senate a sovereign legislature.|Imperial Household~Senatorial Order~Public Priesthoods~Equestrians and Civic Elites~Citizens and Provincials~Allied Communities
han|antq_han_imperial_bureaucracy~antq_memorialist_han_court~antq_commandery_supervision~antq_xin_state_reorganization|han_orders_atlas.png|790add7428c58d7934c5d30264f3583088ec63c5d62e0abd40495f72972816fe|P8.3;P13;BHR;CTP-WM|secure|The categories distinguish court, ritual, registered household, workshop, and exchange interests without imposing European estates on Han institutions.|Imperial House~Court and Great Families~Ritual and Scholarly Officials~Artisans and Merchants~Registered Households~Frontier Communities
iranian|antq_parthian_king_of_kings~antq_parthian_subkingdom~antq_indo_scythian_kingship~antq_arian_satrapal_court~antq_yuezhi_five_yabghus~antq_iranian_great_house_reform~antq_iranian_royal_domain~antq_vologasid_dynastic_settlement~antq_arsacid_dual_court_compact~antq_late_arsacid_house_mobilization|iranian_orders_atlas.png|8a7927087431399bc0144d1b7e80cfa7b47dfca58e314f0dd539e15a3fa10afd|P8.2;P9;P13;CAH-XI;OCD;IRAN-ADMIN;IRAN-ARSACID;IRAN-ARIA;HAN-WR|contested|The profile models negotiated royal, great-house, cult, caravan, cultivating, and mounted interests without asserting one written constitution or fixed Mahistan.|Royal House~Great Houses~Temple Networks~Caravan and Urban Houses~Cultivating Communities~Mounted Clans
civic|antq_indo_greek_kingship~antq_settled_town_cluster~antq_boule_magistracy~antq_federal_synedrion|civic_orders_atlas.png|351cbbb537ff56a943566973db2f9edc1cc33628a932b71fc84b6738ec882275|P8.2;P8.5;P11;P13;OCD|secure|The civic profile covers related council, sanctuary, harbor, guild, and household functions without claiming identical constitutions or citizen bodies.|Civic Magistracies~Leading Houses~Sanctuary Custodians~Guilds and Traders~Citizen and Rural Households~Dependent Communities
gana|antq_indian_ganasangha~antq_lineage_rotation~antq_gana_muster_confederacy|gana_orders_atlas.png|512fa08d4a70e66a54c56216f7b1e996579f6862f6a9a684a10ed1afc8279d8c|P8.5;P11;P13;CAH-XI|contested|Clan delegates and assembly offices are bounded gameplay categories; participation, hierarchy, and procedure varied and are incompletely recoverable.|Assembly Magistrates~Clan Delegates~Shrines and Renunciant Houses~Guilds and Caravans~Cultivating Households~Confederated Clans
steppe|antq_steppe_wing_confederacy~antq_steppe_gift_court~antq_kangju_confederated_kingship~antq_wusun_kunmi_confederacy~antq_yancai_aorsi_confederacy|steppe_orders_atlas.png|173a0512bfd691e9acd21d61c7b9798f343b72e227bea272ad3cf2aaf66cb7c2|P8.3;P8.6;P8.7;P13;CAH-XI;HAN-WR;HHS-WR;UNESCO-CA-NOMADS|contested|The engine orders proxy ruling lineages, retinues, ritual custodians, brokers, and herding households without treating all Inner Asian societies as one polity.|Ruling Lineage~Leading Retinues~Ritual Custodians~Caravan Brokers~Herding Households~Confederated Clans
tribal|antq_advanced_chiefdom~antq_tribal_kingdom~antq_elder_moot_kingship~antq_warband_retinue_kingship~antq_far_side_port_chiefdom~antq_horn_pastoral_network~antq_west_african_savanna_compound_network~antq_west_african_ironworking_network~antq_west_african_forest_network~antq_early_ironworking_community_network~antq_mobile_hunter_herder_network~antq_bengal_riverine_community_network~antq_eastern_megalithic_community_network~antq_eastern_hill_valley_network~antq_himalayan_highland_network~antq_saryarka_late_iron_network~antq_altai_contact_network~antq_sumpa_highland_confederacy~antq_changtang_pastoral_network~antq_central_plateau_agropastoral_network~antq_eastern_plateau_corridor_network|tribal_orders_atlas.png|9aa72377a282f3652e13b9fd7ee5bf6b9558256b149172dffcc37e6fc0206a8c|P8.3;P8.4;P8.7;P11;P13;CAH-XI;CAM-BANGLADESH;OUP-NEINDIA;UNESCO-CA-NOMADS;CAM-TIB-ARCH;ANT-BANGGA|contested|This broad fallback exposes differentiated assembly, retinue, ritual, exchange, and household interests while retaining the need for later regional subdivision.|Leading House~Household Retinues~Sacred Custodians~Exchange Households~Free Cultivators~Kindreds and Clans
sacral|antq_temple_endowment_court~antq_irrigation_palace|sacral_orders_atlas.png|60c182e94e8f921acf2f533baafd8f25ebb89a31f80a7e1d8f013c12fb7c063d|P8.4;P8.5;P11;P13;BHR|contested|The profile translates different court-temple relationships into one engine floor without claiming shared theology or administration.|Consecrated Royal House~Court Lineages~Temple Networks~Market and Artisan Houses~Irrigation and Cultivating Households~Frontier Communities
royal|antq_client_monarchy~antq_buffer_kingdom~antq_regional_kingship~antq_northern_indian_coin_kingship~antq_pundranagara_urban_kingship~antq_sogdian_city_compact~antq_dayuan_oasis_kingship~antq_han_western_regions_kingship~antq_zhangzhung_plateau_kingship~antq_petition_court~antq_frontier_muster_monarchy|royal_orders_atlas.png|03c5d29d261c2c10792377defa0d4ba5840e6f0427daeaa29f2c0b29a11852cd|P8.2;P8.3;P8.4;P8.5;P11;P13;CAH-XI;ASI-MITRA;UNESCO-MAHASTHAN;HAN-WR;IRAN-SOG-KANGJU;OXF-SINO-TIB|contested|The royal profile is a regional floor for incomplete evidence; it does not assert common titulature, succession, court offices, or tribute systems.|Royal Household~Dynastic and Regional Elites~Cult and Sanctuary Networks~Town and Caravan Houses~Rural Households~Frontier and Clan Communities
xiongnu|antq_steppe_confederation~antq_xiongnu_dual_wing_command~antq_xiongnu_gift_circuit~antq_xiongnu_southern_frontier_court~antq_xiongnu_northern_western_confederacy~antq_southern_xiongnu_commandery_settlement~antq_xiongnu_five_divisions_order~antq_han_zhao_chanyu_court|xiongnu_orders_atlas.png|3e603f13b81f1de516bba7f31d1bd0050ea604b30b2a33fd783dc9446fc92208|P8.3;P9;P13;BHR;CAH-XI;IRAN-XIO;XIONGNU-CONFEDERACY|secure|These orders model the chanyu household, wing commanders, brokers, ritual custody, herding households, and negotiated lineages without importing later Mongol ranks or treating every successor settlement as unchanged.|Chanyu Household~Wing Commanders~Rite and Oath Custodians~Frontier Caravan Brokers~Herding Households~Confederated Lineages
goguryeo|antq_early_korean_kingdom|goguryeo_orders_atlas.png|0890f5d7dcb24f4859e4d6991948c8ad919d6af346382a29f332d1cdaf38c00c|P8.3;P13;SAM|secure|The categories translate an early Goguryeo court and fortified communities into engine orders without projecting later Three Kingdoms institutions backward.|Royal House~Senior Lineages~Ancestral Rite Custodians~Walled-Settlement Artisans~Cultivating Households~Frontier Fort Communities
kushite|antq_kushite_dual_kingship|kushite_orders_atlas.png|b93ff9b6915c7260613769a2b6d27d3ffd37d4dd216486347afacb2fa122bd56|P8.5;P11;P13;CAH-XI|secure|Royal, temple, craft, Nile, and frontier categories are Meroitic gameplay interfaces, not a claim for a recoverable formal constitution.|Meroitic Royal House~Court and Provincial Lineages~Temple Networks~Iron, Gold, and Caravan Houses~Nile Cultivating Households~Desert and Southern Communities
lankan|antq_lankan_kingdom|lankan_orders_atlas.png|ee79f5c0a1fb5bc3415130a271fdcade8eec87daffc21b14c5093f2cf0ea1dfa|P8.4;P11;P13;BHR|secure|These categories separate the Anuradhapura court, monastic endowments, market craft, reservoir cultivation, and regional communities without inventing a single codified estate system.|Anuradhapura Royal House~Court and Regional Lineages~Monastic and Sanctuary Communities~Market and Artisan Houses~Reservoir Cultivating Households~Regional and Forest Communities
armenian|antq_artaxiad_highland_kingship~antq_armenian_dynast_compact~antq_armenian_royal_domain_court|armenian_orders_atlas.png|b75ad228b5133a9781b6313e6079969fb9c61d28ac976fff58a5b25d7f70c99d|P8.2;P11;P13;CAH-XI;IRAN-ARM|contested|The categories model the contested Artaxiad court through highland dynasts, sanctuaries, routes, cultivation, and fortress communities without claiming a recovered constitution.|Artaxata Royal House~Highland Dynasts~Sanctuary Custodians~Caravan and Artisan Houses~Vineyard and Grain Communities~Fortress and Pass Communities
nabataean|antq_nabataean_caravan_kingship~antq_nabataean_water_stewardship~antq_nabataean_customs_court|nabataean_orders_atlas.png|0d9e74f8a4526cd9164c8a26f2c07e78baee4343d271d98c3cf7b04f10b5ef9a|P8.1;P8.5;P11;P13;OCD;PLE;NABATAEA-MAP|secure|The orders translate the securely named Aretas-Huldu court and Nabataean water, caravan, sanctuary, and cultivating interests without inventing a uniform bureaucracy.|Nabataean Royal House~Caravan Aristocracy~Sanctuary Custodians~Merchant and Artisan Houses~Oasis and Vineyard Cultivators~Route and Oasis Communities
himyarite|antq_himyarite_terrace_kingship~antq_himyarite_irrigation_court~antq_himyarite_incense_route_court|himyarite_orders_atlas.png|f43f1c3265f01cb73b438c35e91496514e2c6ed16c414af398bad0564ecd527a|P8.5;P8.6;P11;P13;CAH-XI;OCD-HIM;HIMYAR-HIST;OUP-REDSEA|contested|Highland lineages, sanctuaries, incense and port exchange, terrace cultivators, and route communities are evidence-bounded interfaces; no complete AD 1 office hierarchy is claimed.|Himyarite Royal House~Highland Lineages~Sanctuary Custodians~Incense and Port Houses~Terrace Cultivators~Route and Tribal Communities
satavahana|antq_satavahana_deccan_kingship~antq_satavahana_guild_court~antq_satavahana_maharathi_compact|satavahana_orders_atlas.png|e9a41f6c94cc636a11c2736e4d0d23386f34a66d1ce6d772e66c797b73d18a3a|P8.4;P11;P13;CAH-XI|contested|The profile represents a contested AD 1 Deccan succession through royal, titled-house, religious, guild, cultivating, and frontier interests without reconstructing a lost cabinet.|Satavahana Royal House~Maharathi and Mahabhoja Houses~Monastic and Sanctuary Communities~Guild and Caravan Houses~Cultivating Communities~Frontier and Forest Communities
catuvellaunian|antq_catuvellaunian_oppidum_kingship~antq_catuvellaunian_dynastic_mint_court~antq_catuvellaunian_oppida_compact|catuvellaunian_orders_atlas.png|59f57278e21908d98199fd0b007ba964391f50ffdea50c98267556ba1ffc1caf|P8.7;P11;P13;CAH-XI;BM-DRU|contested|The profile uses the named Tasciovanian dynasty, oppida, coinage, exchange, and retinue evidence without claiming a recovered Catuvellaunian constitution or uniform British social order.|Verlamion Royal House~Dynastic and Retinue Houses~Sacred-Place Custodians~Oppidum Craft and Market Houses~Cultivating Communities~Channel and Frontier Communities
trinovantian|antq_trinovantian_coin_kingship~antq_trinovantian_oppidum_court~antq_trinovantian_channel_compact|trinovantian_orders_atlas.png|9ffe652b18ef03513d8187f1ed5d5bec119d895906ec53215b321912f8ddbae2|P8.7;P11;P13;CAH-XI;CCI-DUB;BM-DRU|contested|The orders use Dubnovellaunos's coin horizon, oppida, Channel exchange, retinue, sacred-place, and cultivating evidence without claiming a recovered Camulodunon constitution.|Camulodunon Royal House~Coin-Bearing and Chariot Houses~Sacred-Place Custodians~Channel Exchange Houses~Oppidum Cultivating Households~Woodland and Pasture Communities
brigantian|antq_brigantian_hillfort_confederacy~antq_brigantian_kindred_compact~antq_brigantian_hillfort_court|brigantian_orders_atlas.png|5f4aa3aba1dc9e12be32cdfb06e0e60802004f30cf1d6a7f8f45f2424781c6f8|P8.7;P11;P13;CAH-XI;PLE;PTO-GEO-II2;BRIGANTIA-STANWICK|contested|The orders model a large but internally varied northern frame through leading kindreds, musters, ritual custody, passage, cattle, grain, and upland communities without projecting Cartimandua's later court back to AD 1.|Northern Leading Kindreds~Mounted and Chariot Followings~Ritual and Oath Custodians~Pennine Passage and Exchange Houses~Cattle and Grain Households~Upland Communities
durotrigian|antq_durotrigian_hillfort_coin_order~antq_durotrigian_coin_weight_council~antq_durotrigian_settlement_compact|durotrigian_orders_atlas.png|e1f97b441e34928a42c70461c89e32e6f8eeabf90d62684ced363308f99bdc05|P8.7;P11;P13;CAH-XI;PTO-GEO-II2;DUROTRIGES-PROJECT|contested|The orders translate a distinctive coinage, pottery, burial, settlement, coastal, and enclosure landscape without treating every hillfort as an occupied capital or proving one centralized polity.|Hillfort and Enclosure Houses~Retinue and Chariot Households~Burial and Sacred Custodians~Pottery and Coin Exchange Houses~Field and Grain Households~Coastal and Rural Communities
ivernian|antq_ivernian_regional_assembly~antq_ivernian_seaway_compact~antq_ivernian_cattle_gift_court|ivernian_orders_atlas.png|1635dd2b1ba3de41d174e8b65531b39d4739d6954fff02d7ba31d4806bcf2f5b|P8.7;P11;P13;PTO-GEO-II1;DARCY-IRE;IRON-AGE-IRELAND|contested|The orders are a cautious southwest-Irish adapter for kin groups, seaway followings, ritual custody, smithing, cattle, cultivation, and regional communities; no medieval Gaelic office system is back-projected.|Leading Kin Groups~Seaway and Martial Followings~Ritual and Wetland Custodians~Exchange and Smithing Households~Cattle and Cultivating Households~Regional Free Communities
aestian|antq_aestian_amber_coast_order~antq_aestian_shore_exchange_compact~antq_aestian_woodland_assembly|aestian_orders_atlas.png|e5876709451c75450bd5bc105d8fea07b45564cfafa46fc81371005ec6944d99|P8.7;P11;P13;TAC-GER-45;ARCHAEOMETRY-NE-BALTIC|contested|The orders represent plural southeastern Baltic shore communities through leading households, martial followings, local ritual custody, amber exchange, cultivation, woodland use, and lagoon passage without asserting one centralized Aestian state.|Leading Amber-Coast Households~Shore and Woodland Followings~Local Offering Custodians~Amber and Coastal Exchange Houses~Cultivating and Woodland Households~Lagoon and Shore Communities
frisian|antq_frisian_terp_community_order~antq_frisian_tidal_compact~antq_frisian_frontier_council|frisian_orders_atlas.png|2f83730ed5c01fb6ee5ec6208a5fda9e52f716161cedcdcf53b4bc34bf457a9e|P8.7;P11;P13;TAC-ANN-4.72;GRONINGEN-TERP;PALEOHISTORIA-FRISII|contested|The orders use long-lived terp settlement, salt-marsh production, coastal passage, and early Roman contact without projecting the AD 28 revolt or a later Frisian identity backward as fixed institutions.|Leading Terp Households~Coastal Martial Followings~Oath and Offering Custodians~Tidal Exchange Houses~Cattle and Marsh Households~Terp and Lagoon Communities
dacian|antq_dacian_divided_kingships~antq_dacian_hillfort_compact~antq_dacian_mountain_court|dacian_orders_atlas.png|a38c92e36a19c5c745c76cbe01047cefb0c1d14c5a6d8870d685b5ce5af72f2d|P8.7;P11;P13;CAH-XI;PLE;STR-GEO-7.3.11|contested|The orders model divided post-Burebista rulers, mounted followings, local sanctuaries, metalworking, cultivation, and mountain communities without restoring a single AD 1 Dacian crown or later centralized priesthood.|Hillfort Ruling Houses~Mounted and Warrior Followings~Sanctuary and Oath Custodians~Mining, Smithing, and Exchange Houses~Cultivating and Herd Households~Mountain-Pass Communities
garamantian|antq_garamantian_oasis_state~antq_garamantian_irrigation_court~antq_garamantian_caravan_compact|garamantian_orders_atlas.png|5c7c64aa201850e92db029ae8372c0ae5139af450920eebc3df49e8c00cbfc7d|P8.5;P11;P13;CAH-XI;PLE;LEICESTER-TRANSSAHARA;BILNAS-GARAMANTES|secure|The orders translate the archaeological oasis state into leading houses, mounted followings, local ritual custody, caravan crafts, irrigators, cultivators, and outer-oasis communities without inventing named AD 1 offices.|Leading Oasis Houses~Mounted and Chariot Followings~Burial and Ritual Custodians~Caravan and Craft Houses~Irrigator and Oasis Cultivators~Outer-Oasis and Mobile Communities
marcomannic|antq_marcomannic_bohemian_kingship~antq_marcomannic_retinue_court~antq_marcomannic_allied_host_compact|marcomannic_orders_atlas.png|3fa760bb960e4d06e63f244eea1f8ac53e936a3ff96b7bb5fa6aeb4a6a9a6f9b|P8.7;P11;P13;CAH-XI;TAC-GER|secure|The orders model Maroboduus's royal household, retinue, allied kindreds, sacred custody, exchange, settlement, and frontier interests without inventing fixed Germanic offices.|Marcomannic Royal House~Royal Retinue and Leading Houses~Sacred and Oath Custodians~Iron and Amber Exchange Houses~Settlement Communities~Allied Kindreds
cheruscan|antq_cheruscan_kindred_assembly~antq_cheruscan_coalition_leadership~antq_cheruscan_retinue_kingship|cheruscan_orders_atlas.png|74b87d1faf5037f74845d0eadd7922e2b883cd2db049698e08ac14a77817882c|P8.7;P9;P11;P13;CAH-XI;TAC-GER;TAC-ANN|contested|The orders model Cheruscan kindreds, retinues, sacred custody, frontier exchange, settlements, and coalition communities without inventing a permanent monarchy or recovered constitutional offices.|Leading Kindreds and Assembly~Retinue and War-Leader Houses~Grove and Oath Custodians~Frontier Brokers and Smithing Households~Cultivating Settlement Households~Allied and Forest Communities
chattian|antq_chattian_host_order~antq_chattian_elder_war_council~antq_chattian_chosen_warrior_host|chattian_orders_atlas.png|b66c1b9d9c538c5a86858f8bbd47bf201115293e08e6b165bc8403347c4b53eb|P8.7;P9;P11;P13;CAH-XI;TAC-GER|contested|The orders translate securely distinctive Chattian infantry preparation, selected leaders, vowed warriors, tools, baggage, settlements, and forest districts without treating Tacitus's moralizing account as a complete constitution.|Chosen Leaders and Elder Council~Disciplined Foot-Host Households~Vow and Sacred-Place Custodians~Smith and Frontier Exchange Households~Farming and Provision Households~Forest District Communities
batavian|antq_batavian_rhine_compact~antq_batavian_auxiliary_treaty~antq_batavian_island_assembly|batavian_orders_atlas.png|1714bc32f5e7ca240276584c841e9439bebb41857e43743326487f09af0e5509|P8.7;P9;P11;P13;CAH-XI;TAC-GER;TAC-HIST|secure|The orders represent Batavian island leadership, auxiliary-service households, river custody, ferries, horses, cultivation, floodbanks, and allied communities while keeping exact levy procedure contested.|Leading Island Households and Council~Auxiliary Commanders and Cohort Households~River and Oath Custodians~Ferry, Horse, and Exchange Households~Island Farming and Floodbank Households~Allied Rhine Communities
semnonian|antq_semnonian_sacred_confederacy~antq_semnonian_grove_delegation~antq_semnonian_district_muster|semnonian_orders_atlas.png|2b1ec14c86a26187f2e2265f2f6be298aab4e5983cadaf260f4a1ad0a916c728|P8.7;P9;P11;P13;CAH-XI;TAC-GER|contested|The orders model Semnonian district delegates, retinues, grove custody, Elbe and amber exchange, cultivating households, and Suebian affiliates without asserting a centralized priesthood or fixed hundred-district bureaucracy.|Leading District Households and Delegates~War Leaders and Retinue Households~Sacred-Grove and Oath Custodians~Elbe, Amber, and Craft Households~Cultivating and Provision Households~Suebian Affiliate Communities
sabaean|antq_sabaean_marib_kingship~antq_sabaean_irrigation_court~antq_sabaean_sanctuary_route_court|sabaean_orders_atlas.png|2bf4713352ea3d59a0f8df494e62c98e3342a2ef878fca60a421a5e4590e547e|P8.5;P8.6;P11;P13;CAH-XI;UNESCO-SABA;UNESCO-INCENSE|contested|The anonymous AD 1 court is represented through royal, lineage, sanctuary, incense, waterwork, cultivating, and route interests without inventing a named ruler or complete office hierarchy.|Sabaean Royal House~Highland and Waterwork Lineages~Sanctuary Custodians~Incense and Caravan Houses~Dam and Canal Communities~Highland and Route Communities
mauretanian|antq_mauretanian_client_kingship~antq_mauretanian_urban_court~antq_mauretanian_frontier_compact|mauretanian_orders_atlas.png|1a94154370142251fa3e4f178e7182903e28efef8ff31f4c3a0b2569b671b01e|P8.1;P8.5;P11;P13;CAH-XI;OCD;OCD-PTO|secure|The profile translates Juba II and Cleopatra Selene's client court, royal domains, urban and port exchange, cultivation, cult, and frontier service without treating Mauretania as a uniform Roman administration.|Mauretanian Royal House~Court and Regional Houses~Sanctuary Custodians~Port and Craft Houses~Olive and Grain Communities~Frontier Communities
judean|antq_herodian_judean_ethnarchy~antq_judean_temple_court~antq_judean_toparchy_compact|judean_orders_atlas.png|d0f97e61dcaf57aad9bf9d2540ee63a278de5a17d912ef86d7e67fa2fd858500|P8.1;P11;P13;OCD;JOS-SAL|secure|The orders translate Herodian royal, regional, Temple, market, cultivating, and pastoral interests into engine categories without reconstructing a Judean estate constitution.|Herodian Royal House~Herodian and Regional Houses~Second Temple Priestly Custodians~Merchant and Artisan Houses~Cultivating Communities~Frontier and Pastoral Communities
cappadocian|antq_cappadocian_client_kingship~antq_cappadocian_domain_court~antq_cappadocian_pass_compact|cappadocian_orders_atlas.png|d3507d4bb4ca0e89bf69be6b3db8d529b261d310ad47fad5fe6bfc0f35519b72|P8.1;P11;P13;OCD;PLE|secure|The categories model Archelaus's client court through royal domains, regional houses, sanctuaries, caravan crafts, cultivation, and mountain communities without inventing a recovered office hierarchy.|Cappadocian Royal House~Dynastic and Estate Houses~Sanctuary Custodians~Caravan and Craft Houses~Grain, Vine, and Pastoral Communities~Highland and Pass Communities
thracian|antq_odrysian_client_kingship~antq_thracian_dynastic_court~antq_thracian_mountain_host|thracian_orders_atlas.png|492ad0133b6f2b884c5df7ba7219a5095b2e63c810b3dbcb69ca78f03eae440c|P8.1;P11;P13;OCD;TAC-THR;MGL-THR|contested|The orders distinguish Sapaean royal, retinue, sanctuary, city, producing, and mountain interests without pre-scripting the later partition or claiming uniform Thracian institutions.|Sapaean Royal House~Dynastic and Retinue Houses~Sanctuary and Oath Custodians~Aegean and Pontic City Houses~Grain, Timber, and Pastoral Communities~Mountain and Frontier Communities
bosporan|antq_bosporan_client_kingship~antq_bosporan_polis_court~antq_bosporan_steppe_compact|bosporan_orders_atlas.png|fd1e57c6757896ef09f9ae50ec529940158b65d97fc0d3ff5066072ceae0b5af|P8.1;P11;P13;OCD;PLE;ZAV-ASP|contested|The categories preserve the disputed Dynamis-Aspurgus boundary while separating court, polis, sanctuary, grain, fishing, and steppe-frontier interests.|Bosporan Royal House~Royal Claimant and Mounted Houses~Polis and Sanctuary Custodians~Grain and Harbor Houses~Cultivating, Fishing, and Craft Communities~Steppe and Frontier Communities
galilean|antq_herodian_galilean_tetrarchy~antq_galilean_lake_court~antq_galilean_peraean_compact|galilean_orders_atlas.png|60288641a6224df8bdf13fdb6506b4410b89b2e718af968513111d7483154736|P8.1;P11;P13;OCD;JOS-SAL|secure|The categories translate Antipas's Herodian court through regional houses, ritual custody, fisheries, markets, cultivation, pastoral service, and Peraean routes without reconstructing an estate constitution.|Galilean Tetrarchic House~Herodian and Regional Houses~Ritual and Sanctuary Custodians~Lake and Market Houses~Olive and Grain Communities~Peraean Pastoral Communities
batanean|antq_herodian_batanean_tetrarchy~antq_batanean_highland_court~antq_batanean_frontier_compact|batanean_orders_atlas.png|69a333c19ae5bff562a708246bbacb4a4e34184d01912bffd3d3afdad76f74d0|P8.1;P11;P13;OCD|secure|The categories translate Philip's northern tetrarchy through highland houses, sanctuary custody, caravan crafts, cultivating and pastoral households, and frontier communities without inventing fixed offices.|Batanean Tetrarchic House~Highland and Regional Houses~Sanctuary Custodians~Caravan and Craft Houses~Cultivating and Pastoral Communities~Mountain Frontier Communities
commagenean|antq_commagenean_client_kingship~antq_commagenean_sanctuary_court~antq_commagenean_euphrates_compact|commagenean_orders_atlas.png|950534eb28cfcf97790a259c5268ba5090761c2f3143ae5d6ef1f7a4a77744ee|P8.1;P11;P13;OCD;BM-COM|secure|The categories model Antiochus III's court through royal and highland houses, sanctuaries, Euphrates passage, cultivation, and mounted frontier interests without claiming a recovered constitution.|Commagenean Royal House~Highland Dynastic Houses~Sanctuary Custodians~Euphrates Ferry and Merchant Houses~Orchard and Grain Communities~Mounted Frontier Communities
emesan|antq_emesan_client_dynasty~antq_emesan_sanctuary_court~antq_emesan_caravan_compact|emesan_orders_atlas.png|15431cf4297da0b2ae5eae20bd7e12f1e211e1c8d2edd367197de4be731911b5|P8.1;P11;P13;OCD;PLE;LBD-EME|contested|The categories preserve Iamblichus II's secure court while treating its later descent, sanctuary, caravan, urban, cultivating, and mounted institutions as bounded rather than fully recoverable.|Emesan Dynastic House~Court and Regional Houses~Sanctuary Custodians~Caravan and City Craft Houses~Orontes Cultivating Communities~Mounted Frontier Communities
late_roman|antq_dominate~antq_tetrarchic_collegium~antq_constantinian_consistory~antq_late_imperial_twin_courts|late_roman_orders_atlas.png|d274269d261318a67697b177ceab786bcdfecb4102a98162c67af1fade4bd18b|P8.1;P9;P11;P13;P15;CAH-XII;OCD;ND|secure|These six engine orders distinguish palatine, senatorial, religious, curial, producing, and frontier interests without treating the later empire as a static corporate constitution.|Palatine Household and Officers~Senatorial Houses and Provincial Magnates~Imperial Religious Institutions~Curiales and State Contractors~Registered Cultivators and Urban Communities~Frontier and Military Communities
late_han|antq_guangwu_restoration_court~antq_eastern_han_secretariat~antq_affinal_regency_court~antq_provincial_inspectorate_commands~antq_three_kingdoms_chancellery~antq_jin_reunification_court|late_han_orders_atlas.png|a05af9c3a91bb718d652631f3ea067f61b91aa13ed04573728583229c7b2cd94|P8.3;P9;P13;BHR;CAH-X;CAH-XII|secure|These categories distinguish the restored and later Han palace Secretariat, affinal and provincial families, ritual scholarship, registered production, cultivation, and frontier service without projecting a later examination state backward.|Imperial Household and Secretariat~Affinal and Provincial Great Families~Classical and Ritual Officials~Workshops and Market Households~Registered Cultivating Households~Frontier Garrisons and Communities
sasanian|antq_sassanid_centralized_monarchy~antq_ardashir_unification_court~antq_shapur_imperial_settlement~antq_sasanian_shahrdar_marzban_order~antq_yazdegerd_concordat_court~antq_bahram_great_house_settlement|sasanian_orders_atlas.png|04fa40340dc454300e5dff17eb924468ae2729fad3e5aa65ba8442f003ccaa3f|P8.2;P9;P13;CAH-XII;IRAN-ADMIN;IRAN-FRAMADAR;IRAN-JUDICIAL|secure|These categories distinguish the Sasanian palace, great houses and provincial officers, religious and judicial establishments, urban production, cultivation, and frontier service while acknowledging that ranks and competencies changed across the dynasty.|Royal House and Palace Officers~Great Houses and Provincial Lords~Fire and Judicial Establishments~Urban, Artisan, and Caravan Houses~Cultivating and Taxpaying Communities~Frontier Warriors and Garrisons
xianbei|antq_xianbei_eastern_confederacy~antq_tanshihuai_three_divisions~antq_xianbei_successor_federations~antq_murong_frontier_court~antq_tuoba_dai_confederacy~antq_rouran_khaganate|xianbei_orders_atlas.png|d6a140da2d62355e9376de9116bde5c284963546dcc5aa307f508792c5921a14|P8.8;P9;P13;CAH-XI;CAH-XII;XIANBEI-CONFEDERACY;IRAN-KHAGAN|contested|These categories model separate eastern-steppe Xianbei groups and later dated federations through chiefly households, lineages, rites, brokers, herders, and federated communities without projecting Tanshihuai or Rouran institutions back to AD 1.|Chiefly Household and Assembly~Leading Lineages and Mounted Followings~Oath and Seasonal Rite Custodians~Frontier Brokers and Craft Households~Herding Households~Federated Eastern-Steppe Communities
""".strip()

# profile|slug|estate|display name|description
PRIVILEGE_DATA = r"""
roman|senatorial_commissions|nobles_estate|Senatorial Commissions|Recognized senatorial commissions scrutinize provincial accounts and public obligations while preserving the princeps' final authority.
roman|provincial_land_surveys|nobles_estate|Provincial Land Surveys|Elite landholders support surveyed boundaries and assessed estates in return for predictable fiscal treatment and stronger local influence.
roman|collegial_cult_stipends|clergy_estate|Collegial Cult Stipends|Public priestly colleges receive protected stipends for calendars, vows, auspices, and the custody of civic ritual equipment.
roman|equestrian_public_contracts|burghers_estate|Equestrian Public Contracts|Equestrian contractors receive stable terms for transport, tax collection, supplies, and other bounded public undertakings.
roman|recognized_collegia|burghers_estate|Recognized Collegia|Selected craft, burial, and neighborhood associations gain legal recognition while accepting registration and public-service obligations.
roman|petition_and_census_guarantees|peasants_estate|Petition and Census Guarantees|Citizens and provincials receive regular petition channels and predictable census obligations at the cost of slower coercive extraction.
late_roman|palatine_office_access|nobles_estate|Palatine Office Access|Court and provincial houses receive recognized channels into palatine offices while accepting closer imperial scrutiny and appointment costs.
late_roman|senatorial_provincial_hearings|nobles_estate|Senatorial Provincial Hearings|Senatorial and provincial magnates retain bounded hearings on assessments, honors, and regional administration without recovering republican sovereignty.
late_roman|religious_intercession_channels|clergy_estate|Religious Intercession Channels|Recognized religious institutions receive a bounded route for intercession, endowment review, and community petitions under imperial law.
late_roman|curial_delivery_credits|burghers_estate|Curial Delivery Credits|Curiales and state contractors receive measured credits for transport, manufacture, and requisition while remaining liable for public delivery.
late_roman|registered_cultivator_remissions|peasants_estate|Registered Cultivator Remissions|Cultivating communities receive reviewed remissions after harvest loss in return for registered holdings and predictable in-kind assessments.
late_roman|frontier_service_settlements|tribes_estate|Frontier Service Settlements|Frontier and federate communities receive bounded land, ration, or market terms in exchange for witnessed military and watch obligations.
han|palace_memorial_access|nobles_estate|Palace Memorial Access|Court and great families retain regulated channels for authenticated memorials, appointments, and review of commandery reports.
han|registered_estate_returns|nobles_estate|Registered Estate Returns|Powerful households submit land and dependent-household returns in exchange for predictable assessment and recognized status.
han|calendar_and_ritual_consultation|clergy_estate|Calendar and Ritual Consultation|Ritual and scholarly officials receive a formal hearing on calendars, court rites, omens, and the language of imperial measures.
han|commandery_workshop_quotas|burghers_estate|Commandery Workshop Quotas|Registered workshops receive material allotments and stable quotas while their managers accept inspection and production obligations.
han|licensed_long_distance_trade|burghers_estate|Licensed Long-Distance Trade|Merchant households gain licensed routes and protected markets in return for tallies, duties, and scrutiny of bulk movement.
han|predictable_corvee_rotations|peasants_estate|Predictable Corvée Rotations|Registered households receive seasonal limits and rotation rules for labor service, reducing disruption while constraining immediate mobilization.
iranian|great_house_counsel|nobles_estate|Great-House Counsel|Leading houses receive a recognized place in dynastic arbitration and regional consultation while retaining costly political leverage.
iranian|mounted_host_compacts|nobles_estate|Mounted-Host Compacts|Great houses specify mounted followings, equipment, and seasons of service in return for wider command and local autonomy.
iranian|temple_endowment_registers|clergy_estate|Temple Endowment Registers|Temple networks receive protected endowments and inventories while acknowledging royal arbitration over contested grants.
iranian|caravan_toll_compacts|burghers_estate|Caravan Toll Compacts|Urban and caravan houses receive stable toll schedules and recognized weighing practices at the cost of reduced discretionary revenue.
iranian|safe_conduct_guarantees|burghers_estate|Safe-Conduct Guarantees|Merchants gain enforceable escorts and compensation procedures while accepting route registration and royal oversight.
iranian|irrigation_labor_compacts|peasants_estate|Irrigation Labor Compacts|Cultivating communities receive scheduled water and maintenance obligations instead of unlimited demands by local powers.
civic|magistrate_accountability|nobles_estate|Magistrate Accountability|Leading houses accept audited terms, recorded handovers, and council scrutiny in return for secure eligibility for civic office.
civic|euergetic_public_works|nobles_estate|Civic Benefaction Compacts|Wealthy households fund bounded public works and festivals in exchange for honors and a stronger voice in civic priorities.
civic|sanctuary_inventory_rights|clergy_estate|Sanctuary Inventory Rights|Sanctuary custodians retain protected inventories and revenues while accepting civic review of public endowments.
civic|harbor_dues_farming|burghers_estate|Harbor-Dues Farming|Merchant groups receive predictable harbor collection contracts while surrendering part of the city's immediate fiscal flexibility.
civic|recognized_craft_associations|burghers_estate|Recognized Craft Associations|Craft associations gain arbitration and mutual-aid rights in exchange for registered measures, service, and production standards.
civic|grain_and_water_guarantees|peasants_estate|Grain and Water Guarantees|Citizen and rural households receive protected access to civic grain and water systems while accepting maintenance duties.
gana|clan_delegate_rotation|nobles_estate|Clan Delegate Rotation|Recognized clans rotate delegates through the assembly, widening consultation while slowing concentrated executive action.
gana|warrior_household_service|nobles_estate|Warrior-Household Service|Leading warrior households provide equipment and retainers under negotiated quotas rather than an unlimited royal levy.
gana|shrine_hospitality_endowments|clergy_estate|Shrine Hospitality Endowments|Shrines and renunciant houses receive bounded support for hospitality without becoming a single centralized clergy.
gana|road_hospitality_compacts|burghers_estate|Road Hospitality Compacts|Caravan and guild households maintain wells, shelters, and animal facilities in exchange for protected passage and fees.
gana|guild_arbitration_rights|burghers_estate|Guild Arbitration Rights|Recognized craft and merchant bodies arbitrate internal disputes while accepting assembly review in external cases.
gana|communal_granary_shares|peasants_estate|Communal Granary Shares|Cultivating households contribute measured shares to local stores and receive bounded release rights during scarcity.
steppe|wing_council_precedence|nobles_estate|Wing-Council Precedence|Leading retinues receive an ordered place in wing councils and gift distributions, increasing cohesion but constraining the ruler.
steppe|mounted_retinue_quotas|tribes_estate|Mounted-Retinue Quotas|Confederated clans state remount, bow, and retainer quotas in return for negotiated pasture and campaign expectations.
steppe|cauldron_and_rite_custody|clergy_estate|Rite-Custody Grants|Ritual custodians receive protected vessels and offerings without implying one uniform steppe priesthood or rite.
steppe|seasonal_pasture_circuits|tribes_estate|Seasonal Pasture Circuits|Clan circuits receive recognized grazing and watering sequences at the cost of central freedom to redirect herds.
steppe|gift_circulation_obligations|burghers_estate|Gift-Circulation Obligations|Caravan brokers organize cloth, fittings, livestock, and diplomatic gifts while gaining influence over exchange routes.
steppe|herding_household_remounts|peasants_estate|Herding-Household Remounts|Herding households supply measured remounts and products under predictable quotas instead of open-ended requisition.
tribal|elder_assembly_hearing|tribes_estate|Elder Assembly Hearing|Kindreds and leading households receive a regular hearing before major levies, migrations, settlements, or external compacts.
tribal|household_retinue_gifts|nobles_estate|Household-Retinue Gifts|Leading retinues receive arms and prestige goods while accepting explicit service and hospitality obligations.
tribal|grove_custodianship|clergy_estate|Sacred-Place Custodianship|Local ritual custodians receive protected offerings and access without inventing a uniform priesthood or sacred landscape.
tribal|seasonal_cattle_compacts|tribes_estate|Seasonal Cattle Compacts|Kindreds receive recognized grazing, watering, and restitution customs at the cost of stronger central direction.
tribal|river_exchange_protection|burghers_estate|River-Exchange Protection|Exchange households gain protected landing places, measures, and escorts while accumulating influence over scarce imports.
tribal|free_household_muster|peasants_estate|Free-Household Muster|Free cultivating households accept bounded muster and provisioning duties in return for limits on arbitrary extraction.
sacral|treasury_seal_custody|nobles_estate|Treasury Seal Custody|Court lineages share witnessed custody of selected treasury seals and measures, improving accountability while increasing elite leverage.
sacral|granary_endowments|clergy_estate|Granary Endowments|Temple or monastic networks receive measured grain endowments and storage duties without becoming a universal state church.
sacral|reservoir_labor_rotations|peasants_estate|Reservoir Labor Rotations|Cultivating households receive scheduled waterwork labor and allocation rules at the cost of rapid extraordinary mobilization.
sacral|processional_provisioning|clergy_estate|Processional Provisioning|Ritual institutions receive bounded vessels, textiles, and provisions while accepting inventory and calendar oversight.
sacral|scribal_register_custody|burghers_estate|Scribal Register Custody|Literate and artisan households maintain selected store, donation, and labor records in return for recognized office access.
sacral|frontier_hospitality_endowments|tribes_estate|Frontier Hospitality Endowments|Frontier communities maintain water, offerings, and safe lodging while gaining negotiated protection and local influence.
royal|palace_petition_days|nobles_estate|Palace Petition Days|Regional elites receive regular petition hearings and witnessed judgments, improving coordination while strengthening court access.
royal|dynastic_hostage_compacts|nobles_estate|Dynastic Surety Compacts|Elite houses exchange wards, oaths, and sureties under bounded agreements that reduce conflict but preserve their leverage.
royal|sanctuary_patronage|clergy_estate|Sanctuary Patronage|Cult and sanctuary networks receive protected gifts and inventories while accepting royal arbitration of disputed grants.
royal|tribute_assessment_registers|burghers_estate|Tribute Assessment Registers|Town and caravan houses keep witnessed measures and schedules, reducing arbitrary dues at the cost of immediate revenue.
royal|caravan_protection_guarantees|burghers_estate|Caravan Protection Guarantees|Merchants gain escorts and compensation rules while recognized brokers acquire a stronger voice in royal policy.
royal|fortress_grain_and_muster|peasants_estate|Fortress Grain and Muster|Rural households provide measured grain and bounded muster service in return for predictable demands and local defense.
xiongnu|wing_command_precedence|nobles_estate|Wing-Command Precedence|Left and right wing commanders receive witnessed precedence and campaign directions while accepting bounded obligations to the chanyu.
xiongnu|lineage_surety_exchange|nobles_estate|Lineage Surety Exchange|Leading lineages exchange wards, oath gifts, and witnessed guarantees that reduce defection while preserving their leverage.
xiongnu|cauldron_and_oath_custody|clergy_estate|Cauldron and Oath Custody|Ritual custodians protect vessels and oath rites without implying a centralized or uniform priesthood.
xiongnu|frontier_market_tallies|burghers_estate|Frontier Market Tallies|Brokers receive protected exchange places and measured tallies for silk, livestock, and metal goods under close supervision.
xiongnu|seasonal_pasture_compacts|peasants_estate|Seasonal Pasture Compacts|Herding households receive recognized grazing circuits and water access in return for predictable movement and supply duties.
xiongnu|remount_quota_compacts|tribes_estate|Remount Quota Compacts|Confederated lineages provide measured remounts and horse gear rather than open-ended requisition.
goguryeo|lineage_council_hearing|nobles_estate|Senior-Lineage Hearing|Senior lineages receive a witnessed hearing on appointments, fortress commands, and disputed local obligations.
goguryeo|fortress_command_rotations|nobles_estate|Fortress Command Rotations|Leading houses rotate bounded fortress duties, reducing private capture while slowing concentrated command.
goguryeo|ancestral_rite_stores|clergy_estate|Ancestral Rite Stores|Rite custodians receive protected vessels and stores under royal inventory without becoming a centralized clergy.
goguryeo|walled_artisan_obligations|burghers_estate|Walled Artisan Obligations|Iron, tile, and pottery specialists gain protected working space while accepting measured fortress-supply duties.
goguryeo|millet_store_guarantees|peasants_estate|Millet Store Guarantees|Cultivating households contribute measured grain shares and retain bounded emergency-release claims.
goguryeo|beacon_and_palisade_service|tribes_estate|Beacon and Palisade Service|Frontier communities maintain beacon, timber, and watch obligations under a predictable seasonal rotation.
kushite|dual_court_seal_custody|nobles_estate|Dual Court Seal Custody|Royal and provincial lineages witness selected seals and tribute measures without implying equal constitutional authority.
kushite|provincial_tribute_bowls|nobles_estate|Provincial Tribute Measures|Regional elites receive stable contribution measures while acknowledging royal review of retained shares.
kushite|temple_storehouse_inventories|clergy_estate|Temple Storehouse Inventories|Temple networks retain endowed stores and offerings under witnessed inventories and royal protection.
kushite|iron_and_gold_workshop_terms|burghers_estate|Iron and Gold Workshop Terms|Metalworking and caravan houses receive stable material and market terms while accepting inspected measures.
kushite|nile_cultivator_rotations|peasants_estate|Nile Cultivator Rotations|Riverine households receive bounded labor and water schedules instead of unrestricted demands.
kushite|desert_route_hospitality|tribes_estate|Desert Route Hospitality|Frontier communities maintain water, guides, and safe lodging in return for protected exchange and local influence.
lankan|regional_lineage_petitions|nobles_estate|Regional Lineage Petitions|Court and regional lineages receive witnessed hearings on land, service, and reservoir obligations.
lankan|reservoir_supervision_terms|nobles_estate|Reservoir Supervision Terms|Leading households accept audited waterwork duties in return for predictable access and honors.
lankan|monastic_endowment_registers|clergy_estate|Monastic Endowment Registers|Monastic and sanctuary communities retain bounded gifts and stores under witnessed inventories.
lankan|port_and_market_measures|burghers_estate|Port and Market Measures|Market and artisan houses gain protected weights and dues while accepting inspection of exchange.
lankan|tank_labor_rotations|peasants_estate|Reservoir Labor Rotations|Cultivating households receive scheduled repair and water-allocation duties around local tanks.
lankan|forest_route_compacts|tribes_estate|Forest Route Compacts|Regional communities maintain paths, honey, elephant service, and hospitality under bounded obligations.
armenian|royal_seal_custody|nobles_estate|Artaxata Royal Seal Custody|Royal and dynastic witnesses share custody of selected seals and measures, improving trust while preserving court leverage.
armenian|fortress_dynast_service_terms|nobles_estate|Fortress-Dynast Service Terms|Highland dynasts state fortress, mounted, and seasonal service in exchange for recognized command and local standing.
armenian|sanctuary_offering_inventories|clergy_estate|Sanctuary Offering Inventories|Sanctuary custodians retain protected vessels and offerings under witnessed inventories without becoming a centralized clergy.
armenian|caravan_artisan_safe_conducts|burghers_estate|Caravan and Artisan Safe-Conducts|Exchange and specialist households receive protected passage and measures while accepting route and supply obligations.
armenian|vineyard_grain_labor_compacts|peasants_estate|Vineyard and Grain Labor Compacts|Cultivating communities receive seasonal limits on domain and fortress labor in return for predictable contributions.
armenian|fortress_pass_watch_rotations|tribes_estate|Fortress-Pass Watch Rotations|Pass communities maintain beacons, paths, and bounded watch service under recognized seasonal rotations.
nabataean|royal_seal_custody|nobles_estate|Nabataean Royal Seal Custody|Royal and caravan houses witness selected seals, measures, and grants while acknowledging the king's final judgment.
nabataean|caravan_route_obligations|nobles_estate|Caravan Aristocracy Route Obligations|Leading caravan houses maintain escorts, water, and pack service in return for precedence and protected route interests.
nabataean|sanctuary_offering_inventories|clergy_estate|Sanctuary Offering Inventories|Sanctuary custodians retain bounded offerings, lamps, and stores under witnessed inventories.
nabataean|merchant_artisan_safe_conducts|burghers_estate|Merchant and Artisan Safe-Conducts|Merchant and craft households gain predictable measures and passage while accepting customs inspection.
nabataean|oasis_vineyard_water_compacts|peasants_estate|Oasis and Vineyard Water Compacts|Cultivators receive scheduled cistern and channel access in return for measured maintenance labor.
nabataean|route_oasis_watch_rotations|tribes_estate|Route and Oasis Watch Rotations|Route communities maintain wells, signals, and escorts under bounded rotations and compensation rules.
himyarite|royal_seal_custody|nobles_estate|Himyarite Royal Seal Custody|Royal and lineage witnesses share selected seals and contribution measures without implying a recovered chancery.
himyarite|highland_lineage_terrace_service|nobles_estate|Highland Lineage Terrace Service|Leading lineages coordinate terrace, dam, and levy obligations in return for recognized local authority.
himyarite|sanctuary_offering_inventories|clergy_estate|Sanctuary Offering Inventories|Sanctuary custodians retain incense, vessels, lamps, and stores under witnessed inventories.
himyarite|incense_port_safe_conducts|burghers_estate|Incense and Port Safe-Conducts|Incense and port houses gain protected measures and routes while accepting assessed dues and inspection.
himyarite|terrace_cultivator_water_compacts|peasants_estate|Terrace Cultivator Water Compacts|Cultivators receive scheduled water and repair obligations instead of open-ended terrace labor demands.
himyarite|route_tribal_watch_rotations|tribes_estate|Route and Tribal Watch Rotations|Route communities maintain wells, escorts, and bounded watch service under negotiated rotations.
satavahana|royal_seal_custody|nobles_estate|Satavahana Royal Seal Custody|Royal and titled houses witness selected seals, measures, and gifts while preserving final royal judgment.
satavahana|maharathi_mahabhoja_service_terms|nobles_estate|Maharathi and Mahabhoja Service Terms|Titled regional houses state mounted, elephant, and route obligations in exchange for recognized precedence.
satavahana|monastic_sanctuary_inventories|clergy_estate|Monastic and Sanctuary Inventories|Religious communities retain bounded gifts, vessels, and hospitality stores under witnessed inventories.
satavahana|guild_caravan_safe_conducts|burghers_estate|Guild and Caravan Safe-Conducts|Guild and caravan households receive protected routes and measures while accepting inspected obligations.
satavahana|cultivator_tank_compacts|peasants_estate|Cultivator Tank Compacts|Cultivating communities receive scheduled tank access and repair duties instead of unlimited labor calls.
satavahana|frontier_forest_watch_rotations|tribes_estate|Frontier and Forest Watch Rotations|Forest and frontier communities maintain paths, watch, and elephant-route service under bounded rotations.
catuvellaunian|royal_seal_custody|nobles_estate|Verlamion Royal Seal Custody|Royal and dynastic witnesses share custody of selected seals, weights, and blank flans while preserving final royal judgment.
catuvellaunian|dynastic_retinue_service_terms|nobles_estate|Dynastic Retinue Service Terms|Leading houses state chariot, retinue, hospitality, and campaign obligations in exchange for recognized precedence.
catuvellaunian|sacred_place_offering_inventories|clergy_estate|Sacred-Place Offering Inventories|Ritual custodians retain bounded vessels, offerings, and hospitality stores under witnessed review without becoming a centralized priesthood.
catuvellaunian|oppidum_craft_market_measures|burghers_estate|Oppidum Craft and Market Measures|Craft and exchange households receive stable weights and landing protections while accepting inspected obligations.
catuvellaunian|cultivator_store_compacts|peasants_estate|Cultivator Store Compacts|Cultivating communities receive predictable grain, livestock, and labor shares instead of open-ended requisition.
catuvellaunian|channel_frontier_watch_rotations|tribes_estate|Channel and Frontier Watch Rotations|Landing and frontier communities maintain signals, escorts, paths, and bounded watch duties under recognized rotations.
trinovantian|coin_house_hearings|nobles_estate|Coin-House Hearings|Leading coin-bearing houses receive witnessed hearings on dies, weights, succession display, and royal exchange while accepting accountable custody.
trinovantian|chariot_retinue_terms|nobles_estate|Trinovantian Chariot-Retinue Terms|Chariot and retinue households state vehicles, harness, equipment, hospitality, and bounded campaign service for recognized precedence.
trinovantian|sacred_place_custody|clergy_estate|Trinovantian Sacred-Place Custody|Local custodians retain protected vessels, oath objects, and hearing standing without becoming a centralized priesthood.
trinovantian|channel_exchange_safe_conducts|burghers_estate|Trinovantian Channel Safe-Conducts|Landing and exchange households receive protected routes, stable weights, and restitution while accepting registered obligations.
trinovantian|oppidum_store_guarantees|peasants_estate|Oppidum Store Guarantees|Cultivating households provide measured grain, livestock, craft stock, and labor while retaining bounded emergency access to stores.
trinovantian|woodland_pasture_compacts|tribes_estate|Woodland and Pasture Compacts|Regional communities receive passage, grazing, and refuge guarantees in return for guides, warnings, and bounded service.
brigantian|leading_kindred_hearings|nobles_estate|Brigantian Leading-Kindred Hearings|Prominent northern households receive witnessed hearings on musters, passage, gifts, and compensation without becoming a permanent royal senate.
brigantian|mounted_chariot_service_terms|nobles_estate|Mounted and Chariot Service Terms|Leading martial households state horses, vehicles, harness, equipment, provisions, and bounded campaign duties for recognized command.
brigantian|ritual_oath_custody|clergy_estate|Brigantian Ritual and Oath Custody|Local custodians protect vessels, oath objects, and assembly peace without projecting a uniform druidic hierarchy.
brigantian|pennine_passage_safe_conducts|burghers_estate|Pennine Passage Safe-Conducts|Guide and exchange households receive protected ridge paths, crossings, measures, and compensation under stated obligations.
brigantian|cattle_grain_rotations|peasants_estate|Cattle and Grain Rotations|Farming households receive seasonal limits on herd, grain, transport, and hospitality contributions.
brigantian|upland_community_guarantees|tribes_estate|Upland Community Guarantees|Regional communities retain local judgment and refuge rights while accepting warning, guide, and defensive service.
durotrigian|enclosure_house_hearings|nobles_estate|Enclosure-House Hearings|Leading households receive witnessed hearings on selected stores, refuge, watch, and compensation without private ownership of every hillfort.
durotrigian|retinue_chariot_terms|nobles_estate|Durotrigian Retinue and Chariot Terms|Martial households state vehicles, harness, shields, spears, hospitality, and bounded service for recognized command.
durotrigian|burial_sacred_custody|clergy_estate|Burial and Sacred Custody|Local custodians protect vessels, brooches, mirrors, offering places, and witnessed access without imposing one uniform rite.
durotrigian|pottery_coin_measures|burghers_estate|Pottery and Coin Measures|Pottery, metal, and exchange households receive stable material and weight terms while accepting witnessed measures.
durotrigian|field_grain_compacts|peasants_estate|Field and Grain Compacts|Cultivating households provide measured harvest, cattle, transport, pottery, and store shares rather than open-ended requisition.
durotrigian|coastal_rural_guarantees|tribes_estate|Coastal and Rural Guarantees|Regional communities receive landing, refuge, and local-judgment guarantees in return for warning, transport, and bounded watch.
ivernian|kin_group_hearings|nobles_estate|Ivernian Kin-Group Hearings|Prominent kin groups receive witnessed hearings on gifts, sureties, hospitality, and disputes without implying permanent kingship.
ivernian|seaway_following_terms|nobles_estate|Ivernian Seaway-Following Terms|Martial and boat-owning households state equipment, escort, hospitality, and bounded service for recognized precedence.
ivernian|wetland_offering_custody|clergy_estate|Wetland Offering Custody|Local custodians protect vessels, rings, deposition places, and access without reconstructing an island-wide cult authority.
ivernian|exchange_smithing_safe_conducts|burghers_estate|Exchange and Smithing Safe-Conducts|Smithing and exchange households receive protected materials, landing access, and compensation under measured obligations.
ivernian|cattle_cultivator_compacts|peasants_estate|Cattle and Cultivator Compacts|Households provide measured cattle, grain, hides, wool, and hospitality while retaining bounded local shares.
ivernian|regional_community_guarantees|tribes_estate|Ivernian Regional Community Guarantees|Participating communities retain local judgment and passage rights while accepting surety, warning, and seasonal contribution duties.
aestian|leading_household_hearings|nobles_estate|Amber-Coast Household Hearings|Leading coastal households receive witnessed hearings on exchange, gifts, passage, compensation, and external guarantees without becoming a permanent senate.
aestian|shore_following_terms|nobles_estate|Shore and Woodland Following Terms|Martial households state spears, shields, rope, guides, provisions, and bounded defensive service for recognized precedence.
aestian|local_offering_custody|clergy_estate|Local Offering Custody|Local custodians protect vessels, amber beads, tokens, and gathering peace without becoming a centralized priesthood.
aestian|amber_exchange_safe_conducts|burghers_estate|Amber Exchange Safe-Conducts|Sorting and exchange households receive protected landing access, stable measures, and restitution while accepting witnessed obligations.
aestian|cultivator_woodland_compacts|peasants_estate|Cultivator and Woodland Compacts|Households provide measured grain, beeswax, hides, timber, and tools while retaining bounded local shares.
aestian|lagoon_community_guarantees|tribes_estate|Lagoon Community Guarantees|Shore communities retain passage, fishing, refuge, and local judgment in return for guides, warnings, and bounded watch.
frisian|leading_terp_hearings|nobles_estate|Leading Terp Hearings|Prominent mound households receive witnessed hearings on maintenance, passage, tribute, gifts, and compensation without becoming hereditary lords.
frisian|coastal_following_terms|nobles_estate|Frisian Coastal Following Terms|Martial households state spears, shields, paddles, provisions, and bounded shore service for recognized command.
frisian|oath_offering_custody|clergy_estate|Frisian Oath and Offering Custody|Local custodians protect vessels, rings, fire bowls, and assembly peace without projecting a uniform priestly order.
frisian|tidal_exchange_safe_conducts|burghers_estate|Tidal Exchange Safe-Conducts|Salt, hide, pottery, and landing households receive protected channels, measures, and restitution under stated obligations.
frisian|cattle_marsh_compacts|peasants_estate|Cattle and Marsh Compacts|Households receive measured cattle, hide, barley, salt, fodder, and drainage obligations suited to local resources.
frisian|terp_community_guarantees|tribes_estate|Terp Community Guarantees|Mound communities retain local judgment and refuge rights while accepting predictable maintenance, warning, and passage duties.
dacian|hillfort_house_hearings|nobles_estate|Hillfort-House Hearings|Regional ruling houses receive witnessed hearings on stores, routes, command, gifts, and compensation without claiming one Dacian crown.
dacian|mounted_following_terms|nobles_estate|Dacian Mounted-Following Terms|Martial households state horses, bridle equipment, spears, shields, provisions, and bounded campaign service.
dacian|sanctuary_oath_custody|clergy_estate|Dacian Sanctuary and Oath Custody|Local custodians protect vessels, rings, lamps, and external oaths without reconstructing one centralized priesthood.
dacian|mining_smithing_safe_conducts|burghers_estate|Mining and Smithing Safe-Conducts|Mining, metalworking, and exchange households receive protected materials, routes, and compensation under measured obligations.
dacian|cultivator_herd_compacts|peasants_estate|Cultivator and Herd Compacts|Households provide measured grain, hides, transport, fodder, and hospitality while retaining bounded local shares.
dacian|mountain_pass_guarantees|tribes_estate|Mountain-Pass Guarantees|Pass communities retain local judgment and refuge rights in return for scouts, guides, signals, and bounded defense.
garamantian|leading_oasis_hearings|nobles_estate|Leading Oasis-House Hearings|Prominent oasis houses receive witnessed hearings on water, stores, routes, command, and compensation without inventing named offices.
garamantian|mounted_chariot_terms|nobles_estate|Garamantian Mounted and Chariot Terms|Martial households state bridle, wheel, shield, spear, water, provision, and bounded desert service obligations.
garamantian|burial_ritual_custody|clergy_estate|Burial and Ritual Custody|Local custodians protect vessels, markers, beads, lamps, and witnessed access without imposing one uniform cult hierarchy.
garamantian|caravan_craft_safe_conducts|burghers_estate|Caravan and Craft Safe-Conducts|Caravan and craft households receive protected water, routes, measures, materials, and restitution under accountable terms.
garamantian|irrigator_cultivator_compacts|peasants_estate|Irrigator and Cultivator Compacts|Oasis households receive protected water shares and measured clearing, repair, grain, date, and gate obligations.
garamantian|outer_oasis_guarantees|tribes_estate|Outer-Oasis Community Guarantees|Mobile and outer-oasis communities retain passage and local judgment in return for route knowledge, warning, and bounded service.
marcomannic|royal_gift_custody|nobles_estate|Royal Gift Custody|Royal and leading households witness selected arms, fittings, vessels, and prestige gifts without implying a written treasury administration.
marcomannic|retinue_command_terms|nobles_estate|Retinue Command Terms|Leading companions receive precedence and gift shares in exchange for explicit arms, hospitality, and campaign service.
marcomannic|sacred_oath_stores|clergy_estate|Sacred Oath Stores|Ritual custodians retain bounded vessels, oath gifts, and hospitality supplies without becoming a uniform priesthood.
marcomannic|iron_amber_safe_conducts|burghers_estate|Iron and Amber Safe-Conducts|Exchange households gain protected river and overland movement while accepting witnessed weights and restitution rules.
marcomannic|settlement_provision_compacts|peasants_estate|Settlement Provision Compacts|Farming communities provide measured grain, livestock, wagon, and hospitality shares under predictable seasonal terms.
marcomannic|allied_kindred_muster_terms|tribes_estate|Allied Kindred Muster Terms|Allied kindreds state bounded warrior, wagon, remount, and watch obligations rather than facing unlimited calls.
cheruscan|kindred_assembly_guarantees|tribes_estate|Kindred Assembly Guarantees|Participating kindreds receive witnessed hearings on compensation, passage, coalition service, and external oaths before extraordinary demands.
cheruscan|retinue_service_terms|nobles_estate|Cheruscan Retinue Service Terms|Leading warband households state followers, equipment, hospitality, and bounded campaign duties in return for recognized command precedence.
cheruscan|grove_oath_custody|clergy_estate|Grove and Oath Custody|Ritual custodians receive protected vessels, rings, and assembly standing while remaining local witnesses rather than a centralized priesthood.
cheruscan|frontier_broker_safe_conducts|burghers_estate|Frontier-Broker Safe-Conducts|Interpreters, smiths, and exchange households receive protected routes, stable weights, and compensation for registered frontier movement.
cheruscan|settlement_provision_limits|peasants_estate|Settlement Provision Limits|Cultivating households provide measured grain, livestock, wagons, and hospitality under seasonal terms rather than unlimited coalition requisition.
cheruscan|forest_community_compacts|tribes_estate|Forest Community Compacts|Allied communities receive recognized passage and refuge rights in return for scouts, warnings, guides, and bounded defensive service.
chattian|chosen_leader_hearings|nobles_estate|Chosen-Leader Hearings|Selected commanders receive obedience for a bounded campaign after assembly review of rank, timing, route, and expected service.
chattian|prepared_foot_host_terms|nobles_estate|Prepared Foot-Host Terms|Warband households state infantry, tools, baggage, and provisions in exchange for clear command and distribution of captured goods.
chattian|warrior_vow_custody|clergy_estate|Warrior-Vow Custody|Vow custodians witness limited front-rank service and its completion without imposing Tacitus's literary custom on every Chattian household.
chattian|smith_tool_exchange|burghers_estate|Smith and Tool Exchange|Smithing households receive protected iron, charcoal, routes, and weights while accepting measured deliveries of tools and fittings.
chattian|host_provision_rotations|peasants_estate|Host Provision Rotations|Farming households provide grain, livestock, wagons, and hospitality through stated rotations rather than open-ended warband support.
chattian|forest_district_musters|tribes_estate|Forest District Musters|District communities receive warning and compensation guarantees in return for scouts, fieldworks, routes, and bounded levy service.
batavian|island_council_hearings|nobles_estate|Island Council Hearings|Leading households receive witnessed hearings on alliance service, exemptions, river passage, floodbanks, and compensation.
batavian|auxiliary_service_terms|nobles_estate|Auxiliary Service Terms|Military households state selected fighters, officers, equipment, training, and replacement duties in return for recognized gifts and exemptions.
batavian|river_oath_custody|clergy_estate|River and Oath Custody|Local custodians protect vessels, crossing oaths, and assembly peace without becoming a uniform Batavian priesthood.
batavian|ferry_horse_safe_conducts|burghers_estate|Ferry and Horse Safe-Conducts|Boat, horse, and exchange households receive protected landing places, stable measures, and restitution for registered Rhine service.
batavian|floodbank_labor_rotations|peasants_estate|Floodbank Labor Rotations|Island households receive predictable waterwork and pasture calendars in return for measured dike, revetment, and store duties.
batavian|allied_rhine_guarantees|tribes_estate|Allied Rhine Guarantees|Local communities retain bounded judgment and shared-water rights while accepting warning, passage, and defensive obligations.
semnonian|district_delegation_hearings|nobles_estate|District Delegation Hearings|Leading district households receive witnessed precedence and speaking rights while accepting common assembly and hospitality obligations.
semnonian|retinue_muster_terms|nobles_estate|Semnonian Retinue Muster Terms|War-leader households state followers, shields, spears, and provisions in return for command precedence and bounded gift shares.
semnonian|sacred_grove_custody|clergy_estate|Sacred-Grove Custody|Grove custodians receive protected objects, offerings, and assembly standing while the gathering remains delegated rather than a central temple state.
semnonian|elbe_amber_safe_conducts|burghers_estate|Elbe and Amber Safe-Conducts|River, amber, and craft households receive stable weights, protected passage, and restitution without conceding a royal trade monopoly.
semnonian|assembly_provision_rotations|peasants_estate|Assembly Provision Rotations|Cultivating households provide measured grain, pottery, livestock, baskets, and hospitality through predictable seasonal rotations.
semnonian|suebian_affiliate_guarantees|tribes_estate|Suebian Affiliate Guarantees|Participating communities exchange witnesses, passage, compensation, and bounded aid while retaining local leaders and judgment.
sabaean|royal_seal_custody|nobles_estate|Sabaean Royal Seal Custody|Royal and lineage witnesses share selected seals and contribution measures without inventing a recovered Sabaean chancery.
sabaean|lineage_dam_service_terms|nobles_estate|Lineage Dam Service Terms|Leading houses coordinate masonry, channel, levy, and storage obligations in return for recognized supervision and precedence.
sabaean|sanctuary_offering_inventories|clergy_estate|Sanctuary Offering Inventories|Sanctuary custodians retain incense, vessels, lamps, and bounded hospitality stores under witnessed review.
sabaean|incense_caravan_safe_conducts|burghers_estate|Incense Caravan Safe-Conducts|Caravan and craft households receive protected routes and stable measures while accepting assessed shares and inspection.
sabaean|dam_canal_water_compacts|peasants_estate|Dam and Canal Water Compacts|Cultivating communities receive predictable releases and seasonal repair duties instead of open-ended waterwork labor.
sabaean|highland_route_watch_rotations|tribes_estate|Highland and Route Watch Rotations|Route communities maintain wells, signals, escorts, and bounded watch service under negotiated rotations.
mauretanian|royal_seal_custody|nobles_estate|Mauretanian Royal Seal Custody|Royal and regional witnesses share custody of selected seals, measures, and grants while acknowledging final royal judgment.
mauretanian|court_regional_house_service|nobles_estate|Court and Regional House Service|Leading houses state mounted, domain, hospitality, and regional obligations in exchange for recognized access and precedence.
mauretanian|sanctuary_offering_inventories|clergy_estate|Sanctuary Offering Inventories|Cult custodians retain bounded vessels, lamps, gifts, and hospitality stores under witnessed inventories.
mauretanian|port_craft_measures|burghers_estate|Port and Craft Measures|Port and specialist households gain stable weights, protected movement, and workshop terms while accepting inspection.
mauretanian|olive_grain_labor_compacts|peasants_estate|Olive and Grain Labor Compacts|Cultivating communities receive seasonal limits on estate and transport labor in return for predictable contributions.
mauretanian|frontier_watch_rotations|tribes_estate|Frontier Watch Rotations|Regional communities maintain guides, signals, mounted patrol support, and water access under bounded rotations.
judean|royal_seal_custody|nobles_estate|Herodian Royal Seal Custody|Royal and regional witnesses share selected seals, grants, and assessed measures while preserving final ethnarchic judgment.
judean|regional_house_hearings|nobles_estate|Regional House Hearings|Herodian and local houses receive witnessed hearings over domains, service, and assessment before coercive settlement.
judean|temple_store_inventories|clergy_estate|Second Temple Store Inventories|Priestly custodians retain protected offerings, supplies, and hospitality stores under witnessed inventories.
judean|pilgrim_market_safe_conducts|burghers_estate|Pilgrim and Market Safe-Conducts|Merchant and artisan households gain protected roads and stable measures while accepting inspected obligations.
judean|cultivator_assessment_compacts|peasants_estate|Cultivator Assessment Compacts|Cultivating communities receive predictable measures and seasonal labor limits in return for bounded contributions.
judean|pastoral_frontier_rotations|tribes_estate|Pastoral and Frontier Rotations|Pastoral communities maintain routes, water, guides, and bounded watch duties under recognized rotations.
cappadocian|royal_domain_custody|nobles_estate|Cappadocian Royal-Domain Custody|Royal and regional witnesses confirm selected domain stores, grants, and measures without asserting a uniform cadastre.
cappadocian|estate_house_service_terms|nobles_estate|Estate-House Service Terms|Leading houses state mounted, domain, hospitality, and pass obligations in return for recognized precedence.
cappadocian|sanctuary_store_inventories|clergy_estate|Sanctuary Store Inventories|Cult custodians retain bounded offerings, grain, oil, textiles, and hospitality supplies under review.
cappadocian|caravan_craft_safe_conducts|burghers_estate|Caravan and Craft Safe-Conducts|Caravan and artisan households receive secure stages and stable measures while accepting inspected dues.
cappadocian|grain_vine_pastoral_compacts|peasants_estate|Grain, Vine, and Pastoral Compacts|Producing communities receive seasonal labor limits and predictable transport obligations.
cappadocian|highland_pass_watch_rotations|tribes_estate|Highland Pass Watch Rotations|Mountain communities maintain guides, signals, relays, and bounded watch under recognized rotations.
thracian|royal_seal_hearings|nobles_estate|Sapaean Royal Seal Hearings|Royal and dynastic witnesses share custody of selected seals and grants without resolving the later partition.
thracian|retinue_horse_service_terms|nobles_estate|Retinue and Horse Service Terms|Leading houses state mounts, equipment, hospitality, and campaign obligations in exchange for precedence.
thracian|sanctuary_oath_stores|clergy_estate|Sanctuary and Oath Stores|Ritual custodians retain bounded vessels, offerings, oath gifts, and hospitality supplies under witnessed review.
thracian|aegean_pontic_city_measures|burghers_estate|Aegean and Pontic City Measures|City and exchange houses gain stable measures and protected routes while accepting inspected contributions.
thracian|grain_timber_pastoral_compacts|peasants_estate|Grain, Timber, and Pastoral Compacts|Producing communities provide measured grain, timber, wool, livestock, and wagon service under predictable terms.
thracian|mountain_frontier_rotations|tribes_estate|Mountain and Frontier Rotations|Regional communities maintain guides, signals, water access, and bounded watch duties under negotiated rotations.
bosporan|royal_seal_custody|nobles_estate|Bosporan Royal Seal Custody|Court houses witness selected seals and grants without using mechanics to settle the contested succession.
bosporan|claimant_mounted_service_terms|nobles_estate|Claimant and Mounted-House Service Terms|Royal and mounted houses state escort, horse, hospitality, and frontier duties in return for recognized access.
bosporan|polis_sanctuary_inventories|clergy_estate|Polis and Sanctuary Inventories|Civic cult custodians retain bounded offerings, vessels, stores, and hospitality under witnessed review.
bosporan|grain_harbor_measures|burghers_estate|Grain and Harbor Measures|Grain and exchange houses gain stable measures, storage terms, and strait protection while accepting inspected dues.
bosporan|cultivator_fisher_craft_compacts|peasants_estate|Cultivator, Fisher, and Craft Compacts|Producing communities receive predictable labor and transport terms in exchange for measured goods and upkeep.
bosporan|steppe_frontier_terms|tribes_estate|Steppe and Frontier Terms|Mounted and pastoral communities receive recognized pasture and restitution terms for bounded escort and watch service.
galilean|tetrarchic_seal_custody|nobles_estate|Galilean Tetrarchic Seal Custody|Herodian and regional houses witness selected grants, estate terms, and petitions under the tetrarch's final authority.
galilean|regional_house_hearings|nobles_estate|Galilean Regional-House Hearings|Leading houses receive witnessed hearings over possession, hospitality, route, and service obligations.
galilean|ritual_store_inventories|clergy_estate|Galilean Ritual Store Inventories|Religious custodians retain bounded lamps, vessels, oil, grain, and hospitality stores under review.
galilean|lake_market_measures|burghers_estate|Lake and Market Measures|Fishery, craft, and exchange households gain stable measures, landing terms, and road peace while accepting inspected dues.
galilean|olive_grain_labor_compacts|peasants_estate|Olive and Grain Labor Compacts|Cultivating communities receive seasonal labor and transport limits in exchange for measured produce and upkeep.
galilean|peraean_pastoral_rotations|tribes_estate|Peraean Pastoral Rotations|Pastoral and route communities receive recognized water and restitution terms for bounded guide and watch service.
batanean|tetrarchic_seal_custody|nobles_estate|Batanean Tetrarchic Seal Custody|Philip's court and leading houses witness selected grants, route duties, and settlement obligations.
batanean|highland_house_service_terms|nobles_estate|Highland-House Service Terms|Leading houses state horse, hospitality, storage, and pass obligations in exchange for recognized precedence.
batanean|sanctuary_store_inventories|clergy_estate|Batanean Sanctuary Store Inventories|Cult custodians retain bounded lamps, vessels, offerings, textiles, and hospitality stores under review.
batanean|caravan_craft_safe_conducts|burghers_estate|Batanean Caravan Safe-Conducts|Caravan and craft households receive secure stages and stable measures while accepting inspected dues.
batanean|cultivator_pastoral_compacts|peasants_estate|Cultivator and Pastoral Compacts|Producing households receive seasonal labor, water, and transport limits in exchange for measured supplies.
batanean|mountain_frontier_rotations|tribes_estate|Batanean Mountain Rotations|Highland communities maintain guides, signals, water access, and bounded frontier watch under recognized rotations.
commagenean|royal_seal_custody|nobles_estate|Commagenean Royal Seal Custody|Royal and highland houses witness selected grants, domain terms, and dynastic petitions.
commagenean|highland_cavalry_terms|nobles_estate|Highland Cavalry Terms|Dynastic houses state mounts, armor, hospitality, and campaign obligations in exchange for recognized precedence.
commagenean|sanctuary_offering_inventories|clergy_estate|Commagenean Sanctuary Inventories|Cult custodians retain bounded incense, lamps, vessels, offerings, and hospitality stores under witnessed review.
commagenean|euphrates_passage_measures|burghers_estate|Euphrates Passage Measures|Ferry and merchant houses gain stable weights, landing terms, and restitution while accepting inspected dues.
commagenean|orchard_grain_compacts|peasants_estate|Orchard and Grain Compacts|Cultivating communities receive seasonal labor and transport limits in exchange for measured fruit, wine, and grain.
commagenean|mounted_frontier_rotations|tribes_estate|Commagenean Frontier Rotations|Mounted communities receive recognized access and restitution for bounded escort, signal, and watch service.
emesan|dynastic_seal_custody|nobles_estate|Emesan Dynastic Seal Custody|Sampsigeramid and regional houses witness selected grants, petitions, and service terms under the dynast.
emesan|court_house_service_terms|nobles_estate|Emesan Court-House Service Terms|Leading houses state horse, hospitality, escort, and storage obligations in exchange for precedence.
emesan|sanctuary_store_inventories|clergy_estate|Emesan Sanctuary Store Inventories|Cult custodians retain bounded lamps, incense, offerings, vessels, textiles, and hospitality stores under review.
emesan|caravan_city_measures|burghers_estate|Emesan Caravan and City Measures|Caravan, textile, and craft houses gain stable measures and secure passage while accepting inspected dues.
emesan|orontes_cultivator_compacts|peasants_estate|Orontes Cultivator Compacts|Cultivating communities receive seasonal labor and transport limits in exchange for measured grain, olives, and vines.
emesan|mounted_frontier_terms|tribes_estate|Emesan Mounted Frontier Terms|Mounted communities receive recognized water and restitution terms for bounded escort, warning, and watch service.
late_han|secretariat_memorial_channels|nobles_estate|Secretariat Memorial Channels|Senior officials and provincial families receive authenticated routes for memorials and evaluations while accepting palace review and recorded responsibility.
late_han|affinal_household_disclosure|nobles_estate|Affinal Household Disclosure|Empress families and imperial kin disclose selected appointments, seals, and dependants in return for recognized court access and protection.
late_han|classics_and_ritual_stipends|clergy_estate|Classics and Ritual Stipends|Taixue teachers and ritual officials receive bounded grain, materials, and copying support under court review without becoming a later examination establishment.
late_han|registered_workshop_deliveries|burghers_estate|Registered Workshop Deliveries|Workshop and market households receive measured inputs and delivery credits while accepting inspected quotas for state demand.
late_han|cultivator_register_corrections|peasants_estate|Cultivator Register Corrections|Registered households receive witnessed correction of land, labor, and grain liabilities after migration or crop loss.
late_han|garrison_market_compacts|tribes_estate|Garrison Market Compacts|Frontier communities receive regulated market access, restitution, and supply terms in exchange for bounded watch, transport, and warning duties.
sasanian|palace_seal_command_access|nobles_estate|Palace Seal and Command Access|Palace officers receive authenticated access to selected royal commands and senior appointment dockets while accepting recorded custody and review.
sasanian|great_house_provincial_service|nobles_estate|Great-House Provincial Service Terms|Great houses and provincial lords state mounted, fiscal, court-attendance, and frontier obligations in return for bounded precedence and recognized possession.
sasanian|fire_judicial_endowment_registers|clergy_estate|Fire and Judicial Endowment Registers|Religious and judicial establishments receive protected stores and revenues under inventory, petition, and royal-arbitration duties.
sasanian|urban_workshop_delivery_credits|burghers_estate|Urban Workshop Delivery Credits|Artisan, market, and caravan houses receive measured inputs and delivery credits while accepting inspected quotas and route obligations.
sasanian|cultivating_tax_remissions|peasants_estate|Cultivating Tax Remissions|Cultivating communities receive witnessed correction and remission after crop, irrigation, herd, or war loss in return for registered liabilities.
sasanian|frontier_service_settlements|tribes_estate|Frontier Service Settlements|Frontier warriors and garrison communities receive land, market, and restitution terms for bounded watch, transport, remount, and defense service.
xianbei|chiefly_assembly_hearings|nobles_estate|Chiefly Assembly Hearings|Leading households receive witnessed hearings on allegiance, precedence, compensation, and federation duties while accepting assembly judgments.
xianbei|mounted_following_service|nobles_estate|Mounted-Following Service Terms|Leading lineages state riders, bows, remounts, scouts, and rendezvous in return for bounded command and gift precedence.
xianbei|seasonal_oath_custody|clergy_estate|Seasonal Oath Custody|Rite custodians receive protected vessels, gifts, and assembly standing while accepting shared custody rather than a centralized priesthood.
xianbei|frontier_broker_safe_conducts|burghers_estate|Frontier-Broker Safe-Conducts|Interpreters, traders, and craft households receive protected meeting places, measures, escorts, and restitution for registered exchange.
xianbei|herding_circuit_compacts|peasants_estate|Herding-Circuit Compacts|Mobile households receive recognized pasture and water routes in return for warning, transport, remount, and seasonal supply duties.
xianbei|federated_lineage_guarantees|tribes_estate|Federated Lineage Guarantees|Participating communities exchange wards, gifts, and witnessed guarantees that reduce sudden defection while preserving local leadership.
""".strip()

# design tag|profile|slug|estate|name|description|modifiers|source|confidence|note|atlas|hash|cell|exclusive slug
COUNTRY_PRIVILEGE_DATA = r"""
ROM|roman|senatorial_fiscal_review|nobles_estate|Senatorial Fiscal Review|Senatorial commissions receive audited provincial accounts and a protected hearing before extraordinary assessments, increasing scrutiny while strengthening elite leverage.|global_nobles_estate_power=0.12|nobles_estate_target_satisfaction=medium_privilege_target_satisfaction|country_cabinet_efficiency=0.04|research_speed_modifier=0.02|nobles_estate_max_tax=-0.06|P8.1;P11;P13;OCD|secure|A bounded Augustan commission privilege; it does not make the Senate sovereign over imperial finance.|major_privileges_west_atlas.png|82822073adad217060082ead7964cfa35ed9ac785cdddb2032f02009f3ea906f|0|equestrian_collection_concessions
ROM|roman|equestrian_collection_concessions|burghers_estate|Equestrian Collection Concessions|Equestrian contractors receive stable transport, supply, and collection terms in return for inspected measures and public-service guarantees.|global_burghers_estate_power=0.12|burghers_estate_target_satisfaction=medium_privilege_target_satisfaction|global_trade_through_owned_territory_efficiency=0.06|global_production_efficiency=0.03|burghers_estate_max_tax=-0.05|P8.1;P11;P13;OCD|secure|Models bounded public contracting rather than a permanent tax-farming monopoly over every Roman province.|major_privileges_west_atlas.png|82822073adad217060082ead7964cfa35ed9ac785cdddb2032f02009f3ea906f|1|senatorial_fiscal_review
ROM|roman|senatorial_provincial_commissions|nobles_estate|Senatorial Provincial Commissions|Senatorial commissioners receive audited provincial returns and a protected hearing on selected elite liabilities, increasing scrutiny and aristocratic leverage.|global_nobles_estate_power=0.13|nobles_estate_target_satisfaction=medium_privilege_target_satisfaction|country_cabinet_efficiency=0.045|research_speed_modifier=0.02|nobles_estate_max_tax=-0.06|P8.1;P11;P13;OCD|secure|Augustan and early-imperial senatorial commissions are represented as bounded review, not sovereign control of provincial government.|roman_major_privileges_ii_atlas.png|447f09066a075492ee347720f2fbf10a461a0e02fac790cb54546a1eccdf9012|0|imperial_legatine_inspections
ROM|roman|imperial_legatine_inspections|nobles_estate|Imperial Legatine Inspections|Imperial legates and trusted commissioners may inspect selected provincial accounts, boundaries, and commands at the cost of senatorial autonomy.|global_nobles_estate_power=0.09|nobles_estate_target_satisfaction=medium_privilege_target_satisfaction|global_monthly_control=0.001|country_cabinet_efficiency=0.055|nobles_estate_max_tax=-0.03|P8.1;P11;P13;OCD|secure|The branch models ad hoc imperial inspection without inventing a permanent uniform inspectorate for every province.|roman_major_privileges_ii_atlas.png|447f09066a075492ee347720f2fbf10a461a0e02fac790cb54546a1eccdf9012|1|senatorial_provincial_commissions
ROM|roman|equestrian_procuratorial_careers|burghers_estate|Equestrian Procuratorial Careers|Equestrian households gain recognized fiscal, estate, supply, and household career routes while accepting stricter accounting and replacement obligations.|global_burghers_estate_power=0.13|burghers_estate_target_satisfaction=medium_privilege_target_satisfaction|country_cabinet_efficiency=0.05|global_trade_through_owned_territory_efficiency=0.045|burghers_estate_max_tax=-0.055|P8.1;P11;P13;OCD|secure|Equestrian procuratorial service is secure; the privilege compresses offices that developed unevenly across the imperial period.|roman_major_privileges_ii_atlas.png|447f09066a075492ee347720f2fbf10a461a0e02fac790cb54546a1eccdf9012|2|municipal_decurion_obligations
ROM|roman|municipal_decurion_obligations|burghers_estate|Municipal Decurion Obligations|Municipal governing households receive protected local precedence in return for assessed works, grain, hospitality, and civic accounting duties.|global_burghers_estate_power=0.11|burghers_estate_target_satisfaction=medium_privilege_target_satisfaction|global_production_efficiency=0.035|global_monthly_control=0.0005|burghers_estate_max_tax=-0.04|P8.1;P11;P13;OCD|secure|Municipal elite obligations are secure, while their formal liability and terminology changed markedly across the imperial centuries.|roman_major_privileges_ii_atlas.png|447f09066a075492ee347720f2fbf10a461a0e02fac790cb54546a1eccdf9012|3|equestrian_procuratorial_careers
ROM|roman|veteran_allotment_guarantees|peasants_estate|Veteran Allotment Guarantees|Discharged soldiers receive surveyed allotments or reviewed grants while accepting settlement, reserve, and local public obligations.|global_peasants_estate_power=0.10|peasants_estate_target_satisfaction=medium_privilege_target_satisfaction|global_levy_size_modifier=0.05|land_morale_modifier=0.02|global_monthly_control=-0.0005|P8.1;P11;P13;OCD|secure|Veteran settlement is securely grounded; the guarantee avoids asserting one empire-wide tenure or universal military-colony programme.|roman_major_privileges_ii_atlas.png|447f09066a075492ee347720f2fbf10a461a0e02fac790cb54546a1eccdf9012|4|provincial_petition_safeguards
ROM|roman|provincial_petition_safeguards|peasants_estate|Provincial Petition Safeguards|Provincial and civic communities receive authenticated petition channels and bounded review before extraordinary requisitions or status changes.|global_peasants_estate_power=0.11|peasants_estate_target_satisfaction=medium_privilege_target_satisfaction|stability_cost_efficiency=-0.04|country_cabinet_efficiency=0.025|global_monthly_control=-0.001|P8.1;P11;P13;OCD|secure|Petitioning the emperor and governors is secure; access, remedy, and enforcement remained unequal and are not idealized here.|roman_major_privileges_ii_atlas.png|447f09066a075492ee347720f2fbf10a461a0e02fac790cb54546a1eccdf9012|5|veteran_allotment_guarantees
HAN|han|court_remonstrance_access|nobles_estate|Court Remonstrance Access|Authenticated memorials and remonstrance receive a protected route to the throne, improving review while empowering court and scholarly families.|global_nobles_estate_power=0.11|nobles_estate_target_satisfaction=medium_privilege_target_satisfaction|research_speed_modifier=0.025|country_cabinet_efficiency=0.035|nobles_estate_max_tax=-0.05|P8.3;P11;P13;BHR|secure|The memorial channel is secure; this privilege does not project later examination recruitment into Western Han.|major_privileges_west_atlas.png|82822073adad217060082ead7964cfa35ed9ac785cdddb2032f02009f3ea906f|2|commandery_fiscal_discretion
HAN|han|commandery_fiscal_discretion|burghers_estate|Commandery Fiscal Discretion|Commandery officers and registered workshops may meet assessed quotas through locally balanced grain, craft, and transport returns.|global_burghers_estate_power=0.11|burghers_estate_target_satisfaction=medium_privilege_target_satisfaction|global_production_efficiency=0.035|global_monthly_control=-0.0005|burghers_estate_max_tax=-0.05|P8.3;P11;P13;BHR|contested|A decentralized Han alternative grounded in commandery administration, not a recovered empire-wide concession.|major_privileges_west_atlas.png|82822073adad217060082ead7964cfa35ed9ac785cdddb2032f02009f3ea906f|3|court_remonstrance_access
PAR|iranian|royal_domain_review|nobles_estate|Royal-Domain Review|Royal stewards inspect selected domains, tribute vessels, and route obligations before confirming great-house possession.|global_nobles_estate_power=0.10|nobles_estate_target_satisfaction=medium_privilege_target_satisfaction|country_cabinet_efficiency=0.045|global_monthly_control=0.0005|nobles_estate_max_tax=-0.04|P8.2;P11;P13;CAH-XI|contested|A centralizing Arsacid counterweight; no complete royal-domain survey or uniform procedure is claimed.|major_privileges_west_atlas.png|82822073adad217060082ead7964cfa35ed9ac785cdddb2032f02009f3ea906f|4|great_house_levy_exemptions
PAR|iranian|great_house_levy_exemptions|nobles_estate|Great-House Levy Exemptions|Leading houses retain broader fiscal exemptions in exchange for specified mounted contingents, remounts, and seasonal command.|global_nobles_estate_power=0.14|nobles_estate_target_satisfaction=medium_privilege_target_satisfaction|global_levy_size_modifier=0.06|land_morale_modifier=0.02|nobles_estate_max_tax=-0.08|P8.2;P11;P13;CAH-XI|secure|Great-house mounted service is secure, while exact exemption levels and a single written compact remain unrecoverable.|major_privileges_west_atlas.png|82822073adad217060082ead7964cfa35ed9ac785cdddb2032f02009f3ea906f|5|royal_domain_review
XIO|xiongnu|wing_gift_precedence|nobles_estate|Wing Gift Precedence|Eastern and western commanders receive witnessed precedence in prestige gifts and campaign distributions while accepting explicit muster duties.|global_nobles_estate_power=0.13|nobles_estate_target_satisfaction=medium_privilege_target_satisfaction|land_morale_modifier=0.025|global_levy_size_modifier=0.05|nobles_estate_max_tax=-0.05|P8.3;P11;P13;BHR|secure|The wing hierarchy and gift politics are secure; exact shares and rank order are gameplay abstractions.|major_privileges_east_atlas.png|ec3f9e9429eb216c3c36bfe2dd958025e55f246449df4b672117475af6d499fd|0|pasture_circuit_autonomy
XIO|xiongnu|pasture_circuit_autonomy|tribes_estate|Pasture-Circuit Autonomy|Confederated lineages retain recognized grazing and watering circuits in return for remount, hospitality, and frontier-watch quotas.|global_tribes_estate_power=0.13|tribes_estate_target_satisfaction=medium_privilege_target_satisfaction|global_pop_food_consumption=-0.01|global_levy_size_modifier=0.03|global_monthly_control=-0.001|P8.3;P11;P13;BHR|contested|A bounded pasture compact without claims for cadastral boundaries or one uniform confederation-wide rule.|major_privileges_east_atlas.png|ec3f9e9429eb216c3c36bfe2dd958025e55f246449df4b672117475af6d499fd|1|wing_gift_precedence
KUS|kushite|royal_seal_inspection|nobles_estate|Royal Seal Inspection|Royal agents and provincial lineages jointly witness selected tribute seals and metal measures before redistribution.|global_nobles_estate_power=0.11|nobles_estate_target_satisfaction=medium_privilege_target_satisfaction|country_cabinet_efficiency=0.04|global_production_efficiency=0.025|nobles_estate_max_tax=-0.04|P8.5;P11;P13;CAH-XI|contested|Uses attested Meroitic seals and tribute contexts without inventing a complete chancery procedure.|major_privileges_east_atlas.png|ec3f9e9429eb216c3c36bfe2dd958025e55f246449df4b672117475af6d499fd|2|temple_storehouse_immunity
KUS|kushite|temple_storehouse_immunity|clergy_estate|Temple Storehouse Immunity|Protected cult storehouses retain bounded offerings and grain reserves under inventory, hospitality, and public-rite obligations.|global_clergy_estate_power=0.13|clergy_estate_target_satisfaction=medium_privilege_target_satisfaction|global_monthly_food_modifier=0.03|stability_cost_efficiency=-0.04|clergy_estate_max_tax=-0.07|P8.5;P11;P13;CAH-XI|contested|Cult storage is secure in context; uniform immunity across all Meroitic temples is not claimed.|major_privileges_east_atlas.png|ec3f9e9429eb216c3c36bfe2dd958025e55f246449df4b672117475af6d499fd|3|royal_seal_inspection
ANU|lankan|reservoir_audit_grants|peasants_estate|Reservoir Audit Grants|Reservoir communities gain witnessed water schedules and remissions when their measured repair and field obligations are met.|global_peasants_estate_power=0.11|peasants_estate_target_satisfaction=medium_privilege_target_satisfaction|global_monthly_food_modifier=0.035|global_production_efficiency=0.025|global_monthly_control=-0.0005|P8.4;P11;P13|secure|Irrigation patronage and labor are secure; the audit grant is a bounded administrative reconstruction.|major_privileges_east_atlas.png|ec3f9e9429eb216c3c36bfe2dd958025e55f246449df4b672117475af6d499fd|4|monastic_endowment_immunity
ANU|lankan|monastic_endowment_immunity|clergy_estate|Monastic Endowment Immunity|Recorded monastic gifts and stores receive bounded fiscal protection in return for hospitality, teaching, and inventory duties.|global_clergy_estate_power=0.13|clergy_estate_target_satisfaction=medium_privilege_target_satisfaction|research_speed_modifier=0.02|stability_cost_efficiency=-0.05|clergy_estate_max_tax=-0.07|P8.4;P11;P13;BHR|secure|Early Buddhist endowments are secure; the exact immunity and obligations are gameplay abstractions.|major_privileges_east_atlas.png|ec3f9e9429eb216c3c36bfe2dd958025e55f246449df4b672117475af6d499fd|5|reservoir_audit_grants
ARM|armenian|fortress_dynast_service|nobles_estate|Fortress-Dynast Service|Highland dynasts retain witnessed precedence over selected fortresses in return for mounted contingents, stores, and pass security.|global_nobles_estate_power=0.13|nobles_estate_target_satisfaction=medium_privilege_target_satisfaction|global_levy_size_modifier=0.05|land_morale_modifier=0.02|nobles_estate_max_tax=-0.06|P8.2;P11;P13;CAH-XI;IRAN-ARM|secure|Armenian dynastic and fortress power is secure; a single uniform service compact is not claimed.|major_privileges_southwest_atlas.png|1399660365ef9a8c066c9229fc1a2906ed6379b0732c9186d26e801eccc067ea|0|artaxata_court_arbitration
ARM|armenian|artaxata_court_arbitration|nobles_estate|Artaxata Court Arbitration|The royal court guarantees witnessed hearings over succession, hostages, domains, and cross-border obligations before coercive settlement.|global_nobles_estate_power=0.10|nobles_estate_target_satisfaction=medium_privilege_target_satisfaction|country_cabinet_efficiency=0.045|global_monthly_control=0.0005|nobles_estate_max_tax=-0.04|P8.2;P11;P13;CAH-XI;IRAN-ARM|contested|A bounded court-arbitration alternative for a kingdom between Roman and Arsacid power, not a recovered Armenian procedure.|major_privileges_southwest_atlas.png|1399660365ef9a8c066c9229fc1a2906ed6379b0732c9186d26e801eccc067ea|1|fortress_dynast_service
NAB|nabataean|caravan_water_guarantees|burghers_estate|Caravan-Water Guarantees|Caravan and oasis households receive protected access to cisterns, guides, and compensation in return for upkeep and route intelligence.|global_burghers_estate_power=0.12|burghers_estate_target_satisfaction=medium_privilege_target_satisfaction|global_trade_through_owned_territory_efficiency=0.06|global_pop_food_consumption=-0.01|burghers_estate_max_tax=-0.06|P8.1;P8.5;P11;P13;OCD;PLE|secure|Nabataean water management and caravan exchange are secure; uniform compensation rules are a gameplay abstraction.|major_privileges_southwest_atlas.png|1399660365ef9a8c066c9229fc1a2906ed6379b0732c9186d26e801eccc067ea|2|royal_customs_inspection
NAB|nabataean|royal_customs_inspection|burghers_estate|Royal Customs Inspection|Royal agents confirm weights, aromatic cargo, storage, and transit dues while granting licensed merchants predictable assessment.|global_burghers_estate_power=0.10|burghers_estate_target_satisfaction=medium_privilege_target_satisfaction|global_production_efficiency=0.03|global_monthly_control=0.0005|burghers_estate_max_tax=-0.04|P8.1;P8.5;P11;P13;OCD;PLE|contested|Attested trade and material measures support the adapter; no complete Nabataean customs code survives.|major_privileges_southwest_atlas.png|1399660365ef9a8c066c9229fc1a2906ed6379b0732c9186d26e801eccc067ea|3|caravan_water_guarantees
HIM|himyarite|terrace_water_compacts|peasants_estate|Terrace-Water Compacts|Terrace communities receive witnessed water turns and remission after measured dam, channel, and retaining-wall labor.|global_peasants_estate_power=0.12|peasants_estate_target_satisfaction=medium_privilege_target_satisfaction|global_monthly_food_modifier=0.035|global_production_efficiency=0.025|global_monthly_control=-0.0005|P8.5;P8.6;P11;P13;CAH-XI|secure|South Arabian irrigation and communal maintenance are secure; one kingdom-wide compact is not claimed.|major_privileges_southwest_atlas.png|1399660365ef9a8c066c9229fc1a2906ed6379b0732c9186d26e801eccc067ea|4|incense_route_toll_farm
HIM|himyarite|incense_route_toll_farm|burghers_estate|Incense-Route Toll Farm|Recognized incense houses collect bounded route and market dues under inspected weights while financing escorts and water stations.|global_burghers_estate_power=0.13|burghers_estate_target_satisfaction=medium_privilege_target_satisfaction|global_trade_through_owned_territory_efficiency=0.065|country_cabinet_efficiency=0.025|burghers_estate_max_tax=-0.07|P8.5;P8.6;P11;P13;CAH-XI|contested|Incense exchange and royal exactions are secure in context; the toll farm is a bounded gameplay reconstruction.|major_privileges_southwest_atlas.png|1399660365ef9a8c066c9229fc1a2906ed6379b0732c9186d26e801eccc067ea|5|terrace_water_compacts
SAT|satavahana|guild_charter_arbitration|burghers_estate|Guild-Charter Arbitration|Merchant, craft, and caravan bodies receive internal arbitration and protected measures while accepting royal review in external disputes.|global_burghers_estate_power=0.13|burghers_estate_target_satisfaction=medium_privilege_target_satisfaction|global_production_efficiency=0.035|global_trade_through_owned_territory_efficiency=0.05|burghers_estate_max_tax=-0.06|P8.4;P11;P13;CAH-XI|secure|Corporate exchange and donations are secure; a uniform surviving Satavahana guild charter is not claimed.|major_privileges_east_north_atlas.png|56d39b676eecac67934f63fd7640e7e90daba03b5b428202ed445b147fc52b67|0|maharathi_muster_precedence
SAT|satavahana|maharathi_muster_precedence|nobles_estate|Maharathi Muster Precedence|Leading military houses receive precedence and bounded revenue concessions in return for mounted service, equipment, and route defense.|global_nobles_estate_power=0.13|nobles_estate_target_satisfaction=medium_privilege_target_satisfaction|global_levy_size_modifier=0.055|land_morale_modifier=0.02|nobles_estate_max_tax=-0.065|P8.4;P11;P13;CAH-XI|contested|Maharathi titles and elite military roles are attested, while exact AD 1 service obligations remain uncertain.|major_privileges_east_north_atlas.png|56d39b676eecac67934f63fd7640e7e90daba03b5b428202ed445b147fc52b67|1|guild_charter_arbitration
GOG|goguryeo|fortress_lineage_command|nobles_estate|Fortress-Lineage Command|Senior lineages retain rotating command in selected walled settlements in return for armor, beacon, and relief obligations.|global_nobles_estate_power=0.13|nobles_estate_target_satisfaction=medium_privilege_target_satisfaction|global_levy_size_modifier=0.05|land_morale_modifier=0.02|nobles_estate_max_tax=-0.055|P8.3;P11;P13;SAM|contested|Fortified settlement and lineage brokerage are secure; a formal rotation schedule is not recoverable for AD 1.|major_privileges_east_north_atlas.png|56d39b676eecac67934f63fd7640e7e90daba03b5b428202ed445b147fc52b67|2|royal_granary_inspection
GOG|goguryeo|royal_granary_inspection|peasants_estate|Royal Granary Inspection|Cultivating households gain measured seed and emergency-release claims when royal agents verify stores and seasonal labor.|global_peasants_estate_power=0.11|peasants_estate_target_satisfaction=medium_privilege_target_satisfaction|global_monthly_food_modifier=0.03|country_cabinet_efficiency=0.03|global_monthly_control=-0.0005|P8.3;P11;P13;SAM|contested|Millet storage is materially grounded; the inspection and release guarantee are conservative gameplay abstractions.|major_privileges_east_north_atlas.png|56d39b676eecac67934f63fd7640e7e90daba03b5b428202ed445b147fc52b67|3|fortress_lineage_command
CRU|cheruscan|coalition_assembly_hearing|tribes_estate|Coalition Assembly Hearing|Participating kindreds receive a witnessed hearing before coalition musters, compensation settlements, and external oaths.|global_tribes_estate_power=0.13|tribes_estate_target_satisfaction=medium_privilege_target_satisfaction|country_cabinet_efficiency=0.025|monthly_towards_decentralization=societal_value_minor_monthly_move|global_monthly_control=-0.001|P8.7;P11;P13;TAC-GER|contested|Assembly and coalition bargaining are bounded from literary and archaeological evidence; one formal Cheruscan procedure is not claimed.|major_privileges_east_north_atlas.png|56d39b676eecac67934f63fd7640e7e90daba03b5b428202ed445b147fc52b67|4|retinue_gift_precedence
CRU|cheruscan|retinue_gift_precedence|nobles_estate|Retinue-Gift Precedence|Leading warband households receive imported and local prestige goods in return for explicit hospitality, escort, and campaign duties.|global_nobles_estate_power=0.13|nobles_estate_target_satisfaction=medium_privilege_target_satisfaction|land_morale_modifier=0.025|global_levy_size_modifier=0.045|nobles_estate_max_tax=-0.055|P8.7;P11;P13;TAC-GER|secure|Retinue gift exchange is securely attested as a relationship; exact precedence and quotas remain gameplay values.|major_privileges_east_north_atlas.png|56d39b676eecac67934f63fd7640e7e90daba03b5b428202ed445b147fc52b67|5|coalition_assembly_hearing
HAN|han|three_excellencies_nomination_review|nobles_estate|Three Excellencies Nomination Review|Senior appointments pass through recorded evaluation by the formal high offices, strengthening scrutiny while preserving great-family influence over recommendations.|global_nobles_estate_power=0.12|nobles_estate_target_satisfaction=medium_privilege_target_satisfaction|country_cabinet_efficiency=0.045|research_speed_modifier=0.02|nobles_estate_max_tax=-0.055|P8.3;P11;P13;BHR|secure|Formal high-office recommendation and evaluation are secure; the privilege does not imply impartial modern recruitment or a later examination system.|han_major_privileges_ii_atlas.png|d08bba199a80f5f393d400971a01cd76989bce48913d853c044ff31164895d19|0|secretariat_appointment_channel
HAN|han|secretariat_appointment_channel|nobles_estate|Secretariat Appointment Channel|The palace Secretariat coordinates memorials and appointment drafts more directly, improving executive coherence at the cost of wider high-office review.|global_nobles_estate_power=0.09|nobles_estate_target_satisfaction=medium_privilege_target_satisfaction|country_cabinet_efficiency=0.06|global_monthly_control=0.001|nobles_estate_max_tax=-0.035|P8.3;P11;P13;BHR|secure|The Secretariat's rising coordinating role is secure; exact competence changed across the Han centuries and is not frozen here.|han_major_privileges_ii_atlas.png|d08bba199a80f5f393d400971a01cd76989bce48913d853c044ff31164895d19|1|three_excellencies_nomination_review
HAN|han|regional_inspector_circuits|nobles_estate|Regional Inspector Circuits|Rotating inspectors review commandery officials, powerful households, justice, roads, and revenue, increasing central visibility while unsettling provincial elites.|global_nobles_estate_power=0.09|nobles_estate_target_satisfaction=medium_privilege_target_satisfaction|global_monthly_control=0.0012|country_cabinet_efficiency=0.05|nobles_estate_max_tax=-0.03|P8.3;P11;P13;BHR|secure|Han inspector circuits are secure; the privilege avoids treating later provinces as an unchanged AD 1 territorial tier.|han_major_privileges_ii_atlas.png|d08bba199a80f5f393d400971a01cd76989bce48913d853c044ff31164895d19|2|commandery_administrator_tenure
HAN|han|commandery_administrator_tenure|nobles_estate|Commandery Administrator Tenure|Administrators receive more stable local tenure and discretion over registers, grain, and labor, improving continuity while reducing the center's immediate reach.|global_nobles_estate_power=0.13|nobles_estate_target_satisfaction=medium_privilege_target_satisfaction|global_production_efficiency=0.035|global_monthly_control=-0.001|nobles_estate_max_tax=-0.06|P8.3;P11;P13;BHR|contested|Local administrative discretion is a bounded counterfactual path, not a recovered empire-wide Han tenure guarantee.|han_major_privileges_ii_atlas.png|d08bba199a80f5f393d400971a01cd76989bce48913d853c044ff31164895d19|3|regional_inspector_circuits
HAN|han|state_salt_iron_workshops|burghers_estate|State Salt and Iron Workshops|The court retains direct participation in major salt and iron production, strengthening inspected supply and revenue while burdening registered producers.|global_burghers_estate_power=0.09|burghers_estate_target_satisfaction=medium_privilege_target_satisfaction|global_production_efficiency=0.045|country_cabinet_efficiency=0.035|burghers_estate_max_tax=-0.035|P8.3;P11;P13;BHR|secure|Han state involvement in salt and iron is secure, but its scope and administration varied and are not represented as one timeless monopoly.|han_major_privileges_ii_atlas.png|d08bba199a80f5f393d400971a01cd76989bce48913d853c044ff31164895d19|4|local_market_workshop_compacts
HAN|han|local_market_workshop_compacts|burghers_estate|Local Market and Workshop Compacts|Commandery workshops and market households gain more local control over inputs, measures, and deliveries in return for assessed quotas and transport obligations.|global_burghers_estate_power=0.13|burghers_estate_target_satisfaction=medium_privilege_target_satisfaction|global_trade_through_owned_territory_efficiency=0.055|global_production_efficiency=0.03|burghers_estate_max_tax=-0.065|P8.3;P11;P13;BHR|contested|This delegated alternative is grounded in local administration and production, not a claim for free markets or a surviving uniform compact.|han_major_privileges_ii_atlas.png|d08bba199a80f5f393d400971a01cd76989bce48913d853c044ff31164895d19|5|state_salt_iron_workshops
PAR|iranian|great_house_succession_acclamation|nobles_estate|Great-House Succession Acclamation|Leading Arsacid houses receive a witnessed role in recognizing a dynastic successor, strengthening negotiated legitimacy while increasing aristocratic leverage.|global_nobles_estate_power=0.14|nobles_estate_target_satisfaction=medium_privilege_target_satisfaction|stability_cost_efficiency=-0.03|country_cabinet_efficiency=0.025|nobles_estate_max_tax=-0.065|P8.2;P9;P11;P13;CAH-XI;IRAN-ARSACID|contested|Great-house participation in Arsacid succession is secure in broad terms; this privilege does not claim a permanent constitutional electoral college or fixed Mahistan procedure.|arsacid_major_privileges_ii_atlas.png|19fdf86d85af7583308eaf02be7a5998526756f988736a8474d0b85e3cb39ecc|0|royal_dynastic_nomination
PAR|iranian|royal_dynastic_nomination|nobles_estate|Royal Dynastic Nomination|The reigning king names and prepares an Arsacid successor through court command, hostages, and provincial recognition, improving continuity while narrowing great-house initiative.|global_nobles_estate_power=0.09|nobles_estate_target_satisfaction=medium_privilege_target_satisfaction|global_monthly_control=0.001|country_cabinet_efficiency=0.055|nobles_estate_max_tax=-0.035|P8.2;P9;P11;P13;CAH-XI;IRAN-ARSACID|contested|Royal nomination and dynastic preparation are plausible Arsacid practices; no uniform rule of primogeniture or uncontested nomination is asserted.|arsacid_major_privileges_ii_atlas.png|19fdf86d85af7583308eaf02be7a5998526756f988736a8474d0b85e3cb39ecc|1|great_house_succession_acclamation
PAR|iranian|subkingdom_tribute_autonomy|nobles_estate|Subkingdom Tribute Autonomy|Subordinate kings retain broader local succession, cult, justice, and revenue authority in return for stated gifts, attendance, and mounted service.|global_nobles_estate_power=0.13|nobles_estate_target_satisfaction=medium_privilege_target_satisfaction|global_levy_size_modifier=0.04|global_trade_through_owned_territory_efficiency=0.035|global_monthly_control=-0.001|P8.2;P9;P11;P13;CAH-XI;IRAN-ADMIN|secure|Arsacid subkingdoms and negotiated local authority are secure; the single compact is a gameplay interface for diverse arrangements.|arsacid_major_privileges_ii_atlas.png|19fdf86d85af7583308eaf02be7a5998526756f988736a8474d0b85e3cb39ecc|2|royal_domain_assessment
PAR|iranian|royal_domain_assessment|nobles_estate|Royal-Domain Assessment|Royal officers inventory selected lands, herds, stores, workshops, and route obligations, strengthening direct resources while constraining regional autonomy.|global_nobles_estate_power=0.09|nobles_estate_target_satisfaction=medium_privilege_target_satisfaction|global_monthly_control=0.0012|global_production_efficiency=0.035|nobles_estate_max_tax=-0.035|P8.2;P9;P11;P13;CAH-XI;IRAN-ADMIN|contested|Royal estates are secure, but no uniform Arsacid cadastre or empire-wide assessment procedure is claimed.|arsacid_major_privileges_ii_atlas.png|19fdf86d85af7583308eaf02be7a5998526756f988736a8474d0b85e3cb39ecc|3|subkingdom_tribute_autonomy
PAR|iranian|noble_mounted_host_exemptions|nobles_estate|Noble Mounted-Host Exemptions|Great houses retain wider fiscal and local immunities in exchange for specified cataphracts, horse archers, remounts, equipment, and campaign seasons.|global_nobles_estate_power=0.15|nobles_estate_target_satisfaction=medium_privilege_target_satisfaction|global_levy_size_modifier=0.065|land_morale_modifier=0.025|nobles_estate_max_tax=-0.085|P8.2;P9;P11;P13;CAH-XI;IRAN-ARSACID|secure|Great-house mounted service is secure, while exact exemptions and quotas remain bounded gameplay values.|arsacid_major_privileges_ii_atlas.png|19fdf86d85af7583308eaf02be7a5998526756f988736a8474d0b85e3cb39ecc|4|standing_royal_garrisons
PAR|iranian|standing_royal_garrisons|nobles_estate|Standing Royal Garrisons|The royal court maintains more directly supplied frontier and urban garrisons, improving command continuity while reducing reliance on great-house hosts.|global_nobles_estate_power=0.08|nobles_estate_target_satisfaction=medium_privilege_target_satisfaction|country_cabinet_efficiency=0.04|global_monthly_control=0.001|nobles_estate_max_tax=-0.03|P8.2;P9;P11;P13;CAH-XI;IRAN-ARSACID|contested|Direct royal forces and garrisons are plausible and situational; the privilege does not project a later centralized standing army onto the whole Arsacid period.|arsacid_major_privileges_ii_atlas.png|19fdf86d85af7583308eaf02be7a5998526756f988736a8474d0b85e3cb39ecc|5|noble_mounted_host_exemptions
XIO|xiongnu|chanyu_lineage_nomination|nobles_estate|Chanyu Lineage Nomination|The ruling lineage prepares an eligible successor through seniority, maternal alliances, wards, gifts, and wing consultation, improving continuity while narrowing chiefly initiative.|global_nobles_estate_power=0.09|nobles_estate_target_satisfaction=medium_privilege_target_satisfaction|country_cabinet_efficiency=0.05|global_monthly_control=0.0008|nobles_estate_max_tax=-0.035|P8.3;P9;P11;P13;BHR;CAH-XI|contested|Royal-lineage succession is secure in broad terms; no uniform primogeniture or uncontested nomination procedure is asserted.|xiongnu_major_privileges_ii_atlas.png|0c5c55a3a08b10d457144d709dc229039fa3042e38e82899aaf62d6afc1b1787|0|wing_commander_acclamation
XIO|xiongnu|wing_commander_acclamation|nobles_estate|Wing-Commander Acclamation|Left and right commanders receive a witnessed role in recognizing the next chanyu, strengthening confederate consent while increasing wing leverage.|global_nobles_estate_power=0.14|nobles_estate_target_satisfaction=medium_privilege_target_satisfaction|global_levy_size_modifier=0.05|land_morale_modifier=0.02|nobles_estate_max_tax=-0.065|P8.3;P9;P11;P13;BHR;CAH-XI|contested|Wing authority is secure, but the acclamation mechanism is a bounded political choice rather than a recovered electoral constitution.|xiongnu_major_privileges_ii_atlas.png|0c5c55a3a08b10d457144d709dc229039fa3042e38e82899aaf62d6afc1b1787|1|chanyu_lineage_nomination
XIO|xiongnu|han_frontier_stipend_treaty|burghers_estate|Han Frontier Stipend Treaty|The court prioritizes stable silk, grain, gifts, markets, envoys, and frontier restraint through a negotiated treaty relationship with Han.|global_burghers_estate_power=0.11|burghers_estate_target_satisfaction=medium_privilege_target_satisfaction|global_trade_through_owned_territory_efficiency=0.055|global_pop_food_consumption=-0.008|burghers_estate_max_tax=-0.05|P8.3;P9;P11;P13;BHR;XIONGNU-CONFEDERACY|secure|Treaty exchange and Han goods were politically important; the privilege does not reduce the relationship to one-sided tribute or permanent peace.|xiongnu_major_privileges_ii_atlas.png|0c5c55a3a08b10d457144d709dc229039fa3042e38e82899aaf62d6afc1b1787|2|independent_western_tribute_circuit
XIO|xiongnu|independent_western_tribute_circuit|tribes_estate|Independent Western Tribute Circuit|The chanyu sustains authority through western subordinate peoples, oasis courts, escorts, route intelligence, and retained military freedom rather than Han stipends.|global_tribes_estate_power=0.13|tribes_estate_target_satisfaction=medium_privilege_target_satisfaction|global_levy_size_modifier=0.045|global_trade_through_owned_territory_efficiency=0.04|global_monthly_control=-0.001|P8.3;P9;P11;P13;CAH-XI;IRAN-XIO|secure|Xiongnu influence in the Western Regions is secure but fluctuating; the circuit does not claim uniform direct rule over every oasis.|xiongnu_major_privileges_ii_atlas.png|0c5c55a3a08b10d457144d709dc229039fa3042e38e82899aaf62d6afc1b1787|3|han_frontier_stipend_treaty
XIO|xiongnu|chanyu_gift_redistribution|nobles_estate|Chanyu Gift Redistribution|Prestige silk, vessels, fittings, livestock, and captured goods pass through the chanyu's court for measured redistribution, strengthening central brokerage.|global_nobles_estate_power=0.09|nobles_estate_target_satisfaction=medium_privilege_target_satisfaction|country_cabinet_efficiency=0.045|global_monthly_control=0.001|nobles_estate_max_tax=-0.035|P8.3;P9;P11;P13;BHR;XIONGNU-CONFEDERACY|secure|Central redistribution is a secure political mechanism; exact shares and a permanent treasury administration are not asserted.|xiongnu_major_privileges_ii_atlas.png|0c5c55a3a08b10d457144d709dc229039fa3042e38e82899aaf62d6afc1b1787|4|lineage_gift_retention_quotas
XIO|xiongnu|lineage_gift_retention_quotas|tribes_estate|Lineage Gift-Retention Quotas|Confederated lineages retain a larger stated share of gifts, livestock, and captured goods in return for explicit riders, remounts, and hospitality.|global_tribes_estate_power=0.15|tribes_estate_target_satisfaction=medium_privilege_target_satisfaction|global_levy_size_modifier=0.055|land_morale_modifier=0.015|global_monthly_control=-0.001|P8.3;P9;P11;P13;BHR;XIONGNU-CONFEDERACY|contested|Lineage retention and service bargaining are secure in principle; quantified quotas are gameplay abstractions.|xiongnu_major_privileges_ii_atlas.png|0c5c55a3a08b10d457144d709dc229039fa3042e38e82899aaf62d6afc1b1787|5|chanyu_gift_redistribution
""".strip()


def profiles() -> list[dict[str, object]]:
    result = []
    for line in PROFILE_DATA.splitlines():
        slug, reforms, atlas, digest, source, confidence, note, names = line.split("|")
        result.append({
            "slug": slug, "reforms": tuple(reforms.split("~")), "atlas": atlas,
            "hash": digest, "source": source, "confidence": confidence, "note": note,
            "names": tuple(names.split("~")),
        })
    return result


def privileges_by_profile() -> dict[str, list[dict[str, str]]]:
    result = {str(profile["slug"]): [] for profile in profiles()}
    for line in PRIVILEGE_DATA.splitlines():
        profile, slug, estate, name, description = line.split("|")
        result[profile].append({
            "slug": slug, "estate": estate, "name": name, "description": description,
        })
    return result


def country_privileges() -> list[dict[str, str]]:
    tags = {
        row["design_tag"]: row["engine_tag"]
        for row in json.loads((ROOT / "docs/world_1ad/tag_map.json").read_text(encoding="utf-8"))["entries"]
    }
    result = []
    for line in COUNTRY_PRIVILEGE_DATA.splitlines():
        parts = line.split("|")
        if len(parts) != 18:
            raise ValueError(f"country privilege row has {len(parts)} fields instead of 18")
        (
            design_tag, profile, slug, estate, name, description,
            source, confidence, note, atlas, digest, cell, exclusive_slug,
        ) = (*parts[:6], *parts[11:])
        modifier_text = "|".join(parts[6:11])
        result.append({
            "design_tag": design_tag, "engine_tag": tags[design_tag], "profile": profile,
            "slug": slug, "estate": estate, "name": name, "description": description,
            "modifiers": modifier_text, "source": source, "confidence": confidence,
            "note": note, "atlas": atlas, "hash": digest, "cell": cell,
            "exclusive_slug": exclusive_slug,
        })
    return result


POWER = {
    "nobles_estate": "global_nobles_estate_power",
    "clergy_estate": "global_clergy_estate_power",
    "burghers_estate": "global_burghers_estate_power",
    "peasants_estate": "global_peasants_estate_power",
    "tribes_estate": "global_tribes_estate_power",
}
MAX_TAX = {
    "nobles_estate": "nobles_estate_max_tax",
    "clergy_estate": "clergy_estate_max_tax",
    "burghers_estate": "burghers_estate_max_tax",
}


def item_key(profile: dict[str, object], privilege: dict[str, str]) -> str:
    return f"antq_{profile['slug']}_{privilege['slug']}"


def country_item_key(privilege: dict[str, str]) -> str:
    return f"antq_{privilege['profile']}_{privilege['slug']}"


def modifiers(profile_index: int, cell: int, estate: str) -> tuple[tuple[str, str], ...]:
    result: list[tuple[str, str]] = [
        (POWER[estate], f"{0.08 + 0.01 * (profile_index % 3):.2f}"),
        (f"{estate}_target_satisfaction", "medium_privilege_target_satisfaction"),
    ]
    if cell == 0:
        result += [
            ("country_cabinet_efficiency", f"{0.020 + 0.0025 * profile_index:.4f}".rstrip("0")),
            ("monthly_towards_centralization" if profile_index in {0, 1, 3, 7, 8} else "monthly_towards_decentralization", "societal_value_minor_monthly_move"),
        ]
    elif cell == 1:
        result += [
            ("global_levy_size_modifier", f"{0.035 + 0.005 * (profile_index % 4):.3f}".rstrip("0")),
            ("land_morale_modifier", f"{0.010 + 0.0025 * (profile_index % 3):.4f}".rstrip("0")),
            ("monthly_towards_decentralization", "societal_value_minor_monthly_move"),
        ]
    elif cell == 2:
        result += [
            ("research_speed_modifier", f"{0.015 + 0.0025 * (profile_index % 4):.4f}".rstrip("0")),
            ("stability_cost_efficiency", "-0.05"),
        ]
    elif cell == 3:
        result += [
            ("global_trade_through_owned_territory_efficiency", f"{0.040 + 0.005 * (profile_index % 3):.3f}".rstrip("0")),
            ("country_cabinet_efficiency", "0.015"),
        ]
    elif cell == 4:
        result += [
            ("global_production_efficiency", f"{0.020 + 0.0025 * (profile_index % 4):.4f}".rstrip("0")),
            ("country_cabinet_efficiency", "0.015"),
        ]
    else:
        result += [
            ("global_pop_food_consumption", f"{-0.006 - 0.001 * (profile_index % 4):.3f}".rstrip("0")),
            ("global_levy_size_modifier", f"{0.020 + 0.005 * (profile_index % 3):.3f}".rstrip("0")),
            ("monthly_towards_free_subjects", "societal_value_minor_monthly_move"),
            ("global_monthly_control", "-0.0005"),
        ]
    if estate in MAX_TAX:
        result.append((MAX_TAX[estate], f"{-0.03 - 0.01 * (cell % 3):.2f}"))
    elif cell != 5:
        result.append(("global_monthly_control", "-0.0005"))
    return tuple(result)


def q(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def csv_text(header: tuple[str, ...], rows: list[tuple[str, ...]]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    return stream.getvalue()


def exclusive_key(profile: dict[str, object], entries: list[dict[str, str]], cell: int) -> str:
    partner = {0: 1, 1: 0, 3: 4, 4: 3}.get(cell)
    if partner is None or entries[cell]["estate"] != entries[partner]["estate"]:
        return ""
    return item_key(profile, entries[partner])


def content_ledger() -> str:
    grouped = privileges_by_profile()
    rows = []
    for profile_index, profile in enumerate(profiles()):
        entries = grouped[str(profile["slug"])]
        for cell, privilege in enumerate(entries):
            mods = "|".join(f"{name}={value}" for name, value in modifiers(profile_index, cell, privilege["estate"]))
            rows.append((
                item_key(profile, privilege), privilege["estate"], privilege["name"],
                privilege["description"], mods, str(profile["source"]), str(profile["confidence"]),
                str(profile["note"]), "|".join(profile["reforms"]), "",
                exclusive_key(profile, entries, cell),
            ))
    for privilege in country_privileges():
        rows.append((
            country_item_key(privilege), privilege["estate"], privilege["name"],
            privilege["description"], privilege["modifiers"], privilege["source"],
            privilege["confidence"], privilege["note"], "", privilege["engine_tag"],
            f"antq_{privilege['profile']}_{privilege['exclusive_slug']}",
        ))
    return csv_text(
        (
            "key", "estate", "name", "description", "modifiers", "source",
            "confidence", "note", "potential_reforms", "potential_tags", "exclusive_with",
        ),
        rows,
    )


def source_crop_path(key: str) -> Path:
    return GENERATED_SOURCES / f"antq_privilege_{key.removeprefix('antq_')}_source.png"


def master_path(key: str) -> Path:
    return MASTERS / f"antq_privilege_{key.removeprefix('antq_')}_64x90.png"


def texture_path(key: str) -> Path:
    return ROOT / f"main_menu/gfx/interface/icons/privileges/{key}.dds"


def art_ledger() -> str:
    grouped = privileges_by_profile()
    rows = []
    for profile in profiles():
        for cell, privilege in enumerate(grouped[str(profile["slug"])]):
            key = item_key(profile, privilege)
            rows.append((
                key, str(profile["slug"]), privilege["name"], str(profile["source"]), "secure",
                "Direct material-context illustration; no person, writing, polity emblem, universal constitutional claim, or reconstructed ceremony.",
                f"assets_queue/estate_orders/sources/{profile['atlas']}", str(profile["hash"]), str(cell),
                source_crop_path(key).relative_to(ROOT).as_posix(),
                master_path(key).relative_to(ROOT).as_posix(),
                texture_path(key).relative_to(ROOT).as_posix(),
            ))
    for privilege in country_privileges():
        key = country_item_key(privilege)
        rows.append((
            key, privilege["profile"], privilege["name"], privilege["source"],
            "secure",
            "Country-specific material-context illustration; exact tag gate, no person, writing, emblem, or reconstructed ceremony.",
            f"assets_queue/estate_orders/sources/{privilege['atlas']}",
            privilege["hash"], privilege["cell"],
            source_crop_path(key).relative_to(ROOT).as_posix(),
            master_path(key).relative_to(ROOT).as_posix(),
            texture_path(key).relative_to(ROOT).as_posix(),
        ))
    return csv_text(
        ("key", "profile", "subject", "source", "confidence", "note", "source_atlas", "source_sha256", "cell", "source_crop", "master", "texture"),
        rows,
    )


def game_custom_loc_source() -> Path:
    data = json.loads(PATHS.read_text(encoding="utf-8-sig"))
    return Path(data["game_dir"]) / "game/in_game/common/customizable_localization/estates.txt"


def custom_estate_localization() -> str:
    source = game_custom_loc_source()
    raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != BASE_CUSTOM_LOC_HASH:
        raise ValueError(f"installed estates custom-localization source drift: {source}")
    rendered = raw.decode("utf-8-sig")
    for estate in ESTATES:
        anchor = f"{estate} = {{\n\ttype = country\n"
        if anchor not in rendered:
            raise ValueError(f"installed estate localization lacks exact anchor {estate}")
        insertion = [anchor.rstrip("\n"), "", "\t# ANTIQVITAS ancient order identities."]
        for profile in profiles():
            insertion += [
                "\ttext = {", f"\t\tlocalization_key = antq_estate_{profile['slug']}_{estate}",
                "\t\ttrigger = {", "\t\t\tOR = {",
                *(f"\t\t\t\thas_reform = government_reform:{reform}" for reform in profile["reforms"]),
                "\t\t\t}", "\t\t}", "\t}", "",
            ]
        rendered = rendered.replace(anchor, "\n".join(insertion), 1)
    return "\n".join(line.rstrip() for line in rendered.splitlines()) + "\n"


def localization(language: str) -> str:
    lines = [f"l_{language}:"]
    for profile in profiles():
        for estate, name in zip(ESTATES, profile["names"], strict=True):
            key = f"antq_estate_{profile['slug']}_{estate}"
            lines += [f' {key}: "{q(name)}"', f' {key}_desc: "{q(name)} in this ancient political profile."']
    return "\n".join(lines) + "\n"


def expected_files() -> dict[Path, str]:
    outputs = {
        CONTENT_LEDGER: content_ledger(), ART_LEDGER: art_ledger(),
        CUSTOM_LOC_OUT: custom_estate_localization(),
    }
    for language in ("english", *M2_MIRROR_LANGUAGES):
        outputs[ROOT / f"main_menu/localization/{language}/antq_s2_estates_l_{language}.yml"] = localization(language)
    return outputs


def build_art() -> None:
    GENERATED_SOURCES.mkdir(parents=True, exist_ok=True)
    MASTERS.mkdir(parents=True, exist_ok=True)
    grouped = privileges_by_profile()
    for profile in profiles():
        atlas = SOURCES / str(profile["atlas"])
        if hashlib.sha256(atlas.read_bytes()).hexdigest() != profile["hash"]:
            raise ValueError(f"source atlas hash drift: {atlas.relative_to(ROOT)}")
        with Image.open(atlas) as image:
            width, height = image.size
            if width % 3 or height % 2 or width < 1200 or height < 1000:
                raise ValueError(f"{atlas.relative_to(ROOT)} is not a usable 3x2 atlas")
            cell_width, cell_height = width // 3, height // 2
            rgb = image.convert("RGB")
            for cell, privilege in enumerate(grouped[str(profile["slug"])]):
                key = item_key(profile, privilege)
                x, y = (cell % 3) * cell_width, (cell // 3) * cell_height
                available_width, available_height = cell_width - 16, cell_height - 16
                target_aspect = 64 / 90
                if available_width / available_height > target_aspect:
                    crop_height = available_height
                    crop_width = round(crop_height * target_aspect)
                else:
                    crop_width = available_width
                    crop_height = round(crop_width / target_aspect)
                left = x + (cell_width - crop_width) // 2
                top = y + (cell_height - crop_height) // 2
                crop = rgb.crop((left, top, left + crop_width, top + crop_height))
                crop.save(source_crop_path(key), format="PNG", optimize=True)
                crop.resize((64, 90), Image.Resampling.LANCZOS).save(master_path(key), format="PNG", optimize=True)
                texture_path(key).parent.mkdir(parents=True, exist_ok=True)
                subprocess.run(
                    [sys.executable, str(DDS_TOOL), "convert", str(master_path(key)), str(texture_path(key)), "--compression", "bc7"],
                    check=True,
                )
    by_atlas: dict[str, list[dict[str, str]]] = {}
    for privilege in country_privileges():
        by_atlas.setdefault(privilege["atlas"], []).append(privilege)
    for atlas_name, entries in by_atlas.items():
        atlas = SOURCES / atlas_name
        if hashlib.sha256(atlas.read_bytes()).hexdigest() != entries[0]["hash"]:
            raise ValueError(f"source atlas hash drift: {atlas.relative_to(ROOT)}")
        with Image.open(atlas) as image:
            width, height = image.size
            if width % 3 or height % 2 or width < 1200 or height < 1000:
                raise ValueError(f"{atlas.relative_to(ROOT)} is not a usable 3x2 atlas")
            cell_width, cell_height = width // 3, height // 2
            rgb = image.convert("RGB")
            for privilege in entries:
                key = country_item_key(privilege)
                cell = int(privilege["cell"])
                x, y = (cell % 3) * cell_width, (cell // 3) * cell_height
                available_width, available_height = cell_width - 16, cell_height - 16
                target_aspect = 64 / 90
                if available_width / available_height > target_aspect:
                    crop_height = available_height
                    crop_width = round(crop_height * target_aspect)
                else:
                    crop_width = available_width
                    crop_height = round(crop_width / target_aspect)
                left = x + (cell_width - crop_width) // 2
                top = y + (cell_height - crop_height) // 2
                crop = rgb.crop((left, top, left + crop_width, top + crop_height))
                crop.save(source_crop_path(key), format="PNG", optimize=True)
                crop.resize((64, 90), Image.Resampling.LANCZOS).save(
                    master_path(key), format="PNG", optimize=True
                )
                texture_path(key).parent.mkdir(parents=True, exist_ok=True)
                subprocess.run(
                    [
                        sys.executable, str(DDS_TOOL), "convert", str(master_path(key)),
                        str(texture_path(key)), "--compression", "bc7",
                    ],
                    check=True,
                )


def validate() -> list[str]:
    failures = []
    rows = list(csv.DictReader(io.StringIO(content_ledger())))
    expected_count = len(profiles()) * 6 + len(country_privileges())
    if len(rows) != expected_count or len({row["key"] for row in rows}) != expected_count:
        failures.append(
            f"estate-order ledger must contain {expected_count} unique privileges"
        )
    if any(len(row["description"]) < 75 for row in rows):
        failures.append("estate-order privilege description is too shallow")
    if len({row["modifiers"] for row in rows}) < 30:
        failures.append("estate-order privileges need at least 30 distinct effect packages")
    for profile in profiles():
        atlas = SOURCES / str(profile["atlas"])
        if not atlas.is_file() or hashlib.sha256(atlas.read_bytes()).hexdigest() != profile["hash"]:
            failures.append(f"missing or drifted source atlas: {atlas.relative_to(ROOT)}")
    for privilege in country_privileges():
        atlas = SOURCES / privilege["atlas"]
        if not atlas.is_file() or hashlib.sha256(atlas.read_bytes()).hexdigest() != privilege["hash"]:
            failures.append(f"missing or drifted source atlas: {atlas.relative_to(ROOT)}")
        if not privilege["engine_tag"]:
            failures.append(f"country privilege lacks exact tag gate: {privilege['slug']}")
    for path, expected in expected_files().items():
        if not path.is_file():
            failures.append(f"missing generated file: {path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8-sig") != expected:
            failures.append(f"stale generated file: {path.relative_to(ROOT)}")
    for row in rows:
        key = row["key"]
        crop, master, texture = source_crop_path(key), master_path(key), texture_path(key)
        if not crop.is_file() or not master.is_file() or not texture.is_file():
            failures.append(f"missing direct art chain: {key}")
            continue
        with Image.open(crop) as image:
            if image.width < 350 or image.height < 490 or abs(image.width / image.height - 64 / 90) > 0.01:
                failures.append(f"wrong source crop contract: {crop.relative_to(ROOT)} = {image.size}")
        with Image.open(master) as image:
            if image.size != (64, 90):
                failures.append(f"wrong master dimensions: {master.relative_to(ROOT)}")
        expected_dds = {"format": "DDS", "width": "64", "height": "90", "depth": "8", "channels": "srgba 4.0"}
        if identify(texture) != expected_dds:
            failures.append(f"wrong DDS contract: {texture.relative_to(ROOT)}")
    return failures


def write() -> None:
    build_art()
    for path, rendered in expected_files().items():
        path.parent.mkdir(parents=True, exist_ok=True)
        encoding = "utf-8-sig" if path.suffix == ".yml" or path == CUSTOM_LOC_OUT else "utf-8"
        path.write_text(rendered, encoding=encoding, newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.write:
            write()
        failures = validate()
    except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        failures = [str(exc)]
    if failures:
        print("s2_estate_orders: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    count = len(profiles())
    privilege_count = count * 6 + len(country_privileges())
    print(
        f"s2_estate_orders: PASS ({count} profiles; {privilege_count} privileges; "
        f"{privilege_count} direct icons; {count * 6} polity-aware order names)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
