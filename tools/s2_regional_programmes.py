#!/usr/bin/env python3
"""Culture-gated administrative programmes for small-state profiles.

Dedicated flagship councils stay exclusive. These overlays give every
tribal, royal, civic, gana, steppe, and sacral opening polity at least
four programmes tied to its culture group rather than the shared floor.
"""

from __future__ import annotations

from dataclasses import dataclass


ADMIN = (("country_cabinet_efficiency", "0.025"), ("global_monthly_control", "0.0025"))
FOOD = (("global_pop_food_consumption", "-0.01"), ("global_production_efficiency", "0.025"))
TRADE = (("global_trade_through_owned_territory_efficiency", "0.05"), ("global_burghers_estate_power", "0.025"))
MIL = (("global_levy_size_modifier", "0.05"), ("land_morale_modifier", "0.01"))
LOGISTICS = (("global_supply_limit_modifier", "0.05"), ("global_road_building_time", "-0.05"))
PRESTIGE = (("monthly_prestige", "0.05"), ("country_cabinet_efficiency", "0.02"))
CLERGY = (("global_clergy_estate_power", "0.025"), ("country_cabinet_efficiency", "0.02"))
TRIBES = (("global_tribes_estate_power", "0.025"), ("global_levy_size_modifier", "0.04"))
PEASANTS = (("global_pop_food_consumption", "-0.01"), ("global_levy_size_modifier", "0.03"))
ASSIZE = (("stability_cost_efficiency", "-0.03"), ("global_monthly_control", "0.002"))
PUBLIC_WORKS = (("global_road_building_time", "-0.05"), ("global_production_efficiency", "0.02"))
NAVY = (("global_sailors_modifier", "0.04"), ("navy_maintenance_efficiency", "-0.03"))


@dataclass(frozen=True)
class RegionalProgramme:
    slug: str
    name: str
    description: str
    ability: str
    modifiers: tuple[tuple[str, str], ...]
    source: str
    confidence: str
    note: str


@dataclass(frozen=True)
class RegionalPack:
    slug: str
    culture_groups: tuple[str, ...]
    sheet: str
    programmes: tuple[RegionalProgramme, ...]


def p(
    slug: str, name: str, desc: str, ability: str, mods: tuple[tuple[str, str], ...],
    source: str, confidence: str, note: str,
) -> RegionalProgramme:
    return RegionalProgramme(slug, name, desc, ability, mods, source, confidence, note)


REGIONAL_PACKS: tuple[RegionalPack, ...] = (
    RegionalPack(
        "germanic",
        ("antq_germanic_group", "antq_baltic_group"),
        "regional_programmes_01.png",
        (
            p("wergild_staff_tallies", "Wergild Staff Tallies",
              "Witness compensation staffs, sureties, and kindred payments before a killing or cattle-theft becomes a feud.",
              "adm", ASSIZE + (("global_tribes_estate_power", "0.02"),),
              "TAC-GER;CAH-X;P13", "secure",
              "Tacitus records compensation and kindred surety among Germanic peoples; Baltic amber communities used analogous witnessed settlements."),
            p("grove_boundary_marks", "Grove Boundary Marks",
              "Renew posts, offerings, and exclusion around locally recognized sacred groves without inventing a temple clergy.",
              "adm", CLERGY + (("global_tribes_estate_power", "0.02"),),
              "TAC-GER;CAH-X", "secure",
              "Sacred groves and bounded ritual precincts are the attested Germanic and Baltic cult landscape, not later parish churches."),
            p("cattle_tribute_counts", "Cattle Tribute Counts",
              "Count horned stock, winter fodder, and gift-cattle owed to a host or neighboring kindred after a seasonal muster.",
              "adm", FOOD + TRIBES,
              "TAC-GER;CAH-X;P8.7", "secure",
              "Livestock, not coin, is the ordinary Germanic and Baltic public wealth in the first-century sources."),
            p("host_shield_stacks", "Host Shield Stacks",
              "Inspect stacked shields, spears, and packed grain for a bounded summer host rather than a standing army.",
              "mil", MIL + TRIBES,
              "TAC-GER;CAH-X", "secure",
              "Seasonal infantry hosts with publicly counted equipment are the attested Germanic levy form."),
        ),
    ),
    RegionalPack(
        "celtic",
        ("antq_celtic_group",),
        "regional_programmes_02.png",
        (
            p("oppidum_grain_pits", "Oppidum Grain Pits",
              "Audit lined storage pits, sealed jars, and emergency seed inside fortified agglomerations and their dependent fields.",
              "adm", FOOD + PEASANTS,
              "BG;CUN-CELT;CAH-X", "secure",
              "Southern British and Gallic oppida concentrate grain storage; this does not claim every Celtic people lived in oppida."),
            p("cattle_bridewealth_rings", "Cattle Bridewealth Rings",
              "Record livestock, gold rings, and sureties that bind marriages and clientage among leading kindreds.",
              "dip", PRESTIGE + TRIBES,
              "BG;CUN-CELT;P8.7", "contested",
              "Cattle and prestige metal as marriage and client gifts are widely attested; exact legal formulas vary by people."),
            p("chariot_fitting_stores", "Chariot Fitting Stores",
              "Keep terrets, linchpins, harness rings, and spare wheels ready for the limited chariot contingents still used in Britain and the western seaboard.",
              "mil", MIL + LOGISTICS,
              "BG;CUN-CELT;CAH-X", "secure",
              "Caesar and the British archaeological record preserve late chariot use; this is not a continental Gallic field-army claim."),
            p("oenach_assembly_posts", "Oenach Assembly Posts",
              "Mark the seasonal fair-ground, guest-right, and dispute posts where cattle, news, and judgments move together.",
              "dip", TRADE + TRIBES,
              "CUN-CELT;P8.7;CAH-X", "contested",
              "Irish oenach and British seasonal assemblies are later-attested; the mechanic is a conservative fair-and-judgment adapter."),
        ),
    ),
    RegionalPack(
        "uralic",
        ("antq_uralic_group", "antq_slavic_group"),
        "regional_programmes_03.png",
        (
            p("fur_bundle_accounts", "Fur Bundle Accounts",
              "Tally winter pelts, bark tallies, and exchange debts before spring travel on forest rivers.",
              "adm", TRADE + TRIBES,
              "CAH-XI;P8.7;TAC-GER", "contested",
              "Forest-zone fur exchange is archaeological and later-textual; no centralized fur office is asserted."),
            p("river_boat_relays", "River Boat Relays",
              "Stage dugouts, paddles, portage poles, and food caches along the seasonal river corridors.",
              "dip", LOGISTICS + NAVY,
              "CAH-XI;P8.7", "secure",
              "River transport is the ordinary long-distance means across the forest zone; this is not an ocean navy."),
            p("winter_store_pits", "Winter Store Pits",
              "Inspect lined pits, smoked fish, and seed against a long winter before any gift or raid is authorized.",
              "adm", FOOD + PEASANTS,
              "CAH-XI;P8.7", "secure",
              "Seasonal storage is required by the northern subsistence round and needs no invented granary bureaucracy."),
            p("forest_grove_gifts", "Forest Grove Gifts",
              "Place offerings at recognized groves and waters without converting later chroniclers' temples into AD 1 buildings.",
              "adm", CLERGY + TRIBES,
              "TAC-GER;CAH-XI", "contested",
              "Grove and water cult is the conservative northern ritual claim; named later Slavic temples are excluded."),
        ),
    ),
    RegionalPack(
        "african",
        ("antq_subsaharan_group", "antq_nile_group"),
        "regional_programmes_04.png",
        (
            p("compound_granary_seals", "Compound Granary Seals",
              "Seal household and compound granaries, compare spoilage, and release seed after a poor harvest.",
              "adm", FOOD + PEASANTS,
              "CAM-WAF;UNESCO-AFR;P8.5", "secure",
              "Mud-brick and basket granaries are the ordinary West African and Nilotic store; no later emirate warehouse is implied."),
            p("bloomery_iron_shares", "Bloomery Iron Shares",
              "Share blooms, tuyeres, charcoal, and finished hoes among smithing compounds that supply the surrounding fields.",
              "adm", PUBLIC_WORKS + TRADE,
              "CAM-WAF;NSUKKA;P8.5", "secure",
              "Nsukka-Lejja and related bloomery landscapes justify shared iron production without a royal foundry."),
            p("cattle_kraal_counts", "Cattle Kraal Counts",
              "Count kraaled cattle, calves, and loan-stock before a dry-season move or compensation hearing.",
              "adm", FOOD + TRIBES,
              "CAM-WAF;P8.5", "secure",
              "Cattle as wealth and surety is widely attested across savanna and Nile pastoral communities."),
            p("shrine_offering_jars", "Shrine Offering Jars",
              "Inventory terracotta jars, beer, and iron gifts at compound and landscape shrines without inventing a state church.",
              "adm", CLERGY + TRIBES,
              "CAM-WAF;P8.5;P11", "contested",
              "Local shrine economy is secure; named later priesthoods and Islamic or Christian offices are excluded."),
        ),
    ),
    RegionalPack(
        "indic",
        ("antq_indian_group",),
        "regional_programmes_05.png",
        (
            p("tank_sluice_turns", "Tank Sluice Turns",
              "Apportion sluice openings, embankment labor, and tank-bed cultivation among the villages that share one reservoir.",
              "adm", PUBLIC_WORKS + PEASANTS,
              "CAH-XI;P8.4;THAPAR", "secure",
              "Deccan and Tamil tank irrigation is attested; this is not a later Chola imperial water-board."),
            p("village_share_cords", "Village Share Cords",
              "Renew knotted share-cords, field boundaries, and harvest dues before the monsoon sowing.",
              "adm", ADMIN + PEASANTS,
              "CAH-XI;P8.4", "contested",
              "Village share and boundary witnessing is a conservative adapter; no uniform jati constitution is asserted."),
            p("monsoon_seed_jars", "Monsoon Seed Jars",
              "Seal seed, pulse, and emergency grain against the wet season and inspect them after the first storms.",
              "adm", FOOD + PEASANTS,
              "CAH-XI;P8.4", "secure",
              "Monsoon risk makes seed custody a public concern independent of any later revenue department."),
            p("guild_weight_stones", "Guild Weight Stones",
              "Compare merchant weights, punch-marked coin, and craft measures in market towns without inventing a Mauryan revival.",
              "dip", TRADE + ASSIZE,
              "CAH-XI;P8.4;THAPAR", "secure",
              "Craft and merchant weight control is attested in early historic towns; Satavahana and gana courts keep their own deeper offices."),
        ),
    ),
    RegionalPack(
        "nanyang",
        (
            "antq_austronesian_group", "antq_southeast_asian_group",
            "antq_oceanic_group", "antq_japonic_group",
            "antq_korean_group", "antq_north_maluku_group",
        ),
        "regional_programmes_06.png",
        (
            p("outrigger_cordage_stores", "Outrigger Cordage Stores",
              "Keep coconut-fiber lashings, spare spars, and hull patches ready for inter-island and monsoon-coast travel.",
              "mil", NAVY + LOGISTICS,
              "BELLWOOD;P8.6;CAH-XI", "secure",
              "Lashed outrigger and coastal craft are the ordinary island and monsoon-coast transport; no oceanic treasure-fleet is granted."),
            p("monsoon_bead_chests", "Monsoon Bead Chests",
              "Inventory Indo-Pacific beads, bronze fragments, and sealed chests that move with the monsoon traders.",
              "dip", TRADE + PRESTIGE,
              "BELLWOOD;SAHUYNH;P8.6", "secure",
              "Bead and metal exchange is the archaeologically visible prestige economy of the South China Sea and Island Southeast Asia."),
            p("reef_fish_weirs", "Reef and River Weirs",
              "Maintain weirs, traps, and drying racks so coastal and river communities can feed a gathering or voyage.",
              "adm", FOOD + NAVY,
              "BELLWOOD;P8.6", "secure",
              "Fish weirs and drying are ordinary subsistence, not a later commercial fishery."),
            p("ancestor_jar_watches", "Ancestor Jar Watches",
              "Guard jar burials, boat-coffins, and lineage bones that authorize land and voyage rights.",
              "adm", CLERGY + TRIBES,
              "BELLWOOD;SAHUYNH;P8.6", "secure",
              "Jar and boat burial landscapes are the attested ancestral claim; later Hindu-Buddhist temples are not backdated."),
        ),
    ),
    RegionalPack(
        "mesoamerican",
        ("antq_mesoamerican_group",),
        "regional_programmes_07.png",
        (
            p("milpa_seed_gourds", "Milpa Seed Gourds",
              "Select maize, bean, and squash seed and assign milpa plots before the rains without claiming later imperial tribute maize.",
              "adm", FOOD + PEASANTS,
              "COE-MEX;P8.8;SANDERS", "secure",
              "Milpa polyculture is the Formative and Classic subsistence base across Mesoamerica."),
            p("obsidian_core_shares", "Obsidian Core Shares",
              "Share prismatic cores, blades, and quarry access among workshops that supply household and ritual cutting tools.",
              "adm", TRADE + PUBLIC_WORKS,
              "COE-MEX;P8.8", "secure",
              "Obsidian blade-core industry is the diagnostic Mesoamerican craft economy."),
            p("cacao_tribute_bundles", "Cacao and Cloth Bundles",
              "Count cacao, cotton cloth, and bark-paper tallies offered to a civic center without projecting Aztec imperial tribute backward.",
              "adm", PRESTIGE + TRADE,
              "COE-MEX;P8.8", "contested",
              "Cacao and cloth as prestige goods are Formative-Classic; the mechanic refuses later Triple Alliance quotas."),
            p("incensario_calendar_watches", "Incensario Calendar Watches",
              "Keep incense burners, greenstone, and day-count marks for civic ritual without inventing a single pan-Mesoamerican priesthood.",
              "adm", CLERGY + PRESTIGE,
              "COE-MEX;P8.8", "contested",
              "Civic ritual calendars are real; no one later Aztec or Maya state cult is imposed on every opening tag."),
        ),
    ),
    RegionalPack(
        "andean",
        ("antq_andean_group",),
        "regional_programmes_08.png",
        (
            p("terrace_water_turns", "Terrace Water Turns",
              "Apportion canal openings and terrace labor along a valley without claiming a later Inka hydraulic office.",
              "adm", PUBLIC_WORKS + PEASANTS,
              "MOSELEY;P8.8", "secure",
              "Coastal and highland irrigation terraces long predate the Inka; this is a local water-turn adapter."),
            p("llama_caravan_packs", "Llama Caravan Packs",
              "Inspect pack bags, ropes, and salt or dried-fish loads before a highland-coast caravan leaves.",
              "dip", TRADE + LOGISTICS,
              "MOSELEY;P8.8", "secure",
              "Camelid caravans are the ordinary Andean bulk transport."),
            p("chuno_store_courts", "Chuño Store Courts",
              "Air-freeze potatoes, stack chuño, and seal coastal fishmeal so a valley can survive a failed wet season.",
              "adm", FOOD + PEASANTS,
              "MOSELEY;P8.8", "secure",
              "Freeze-drying and coastal fishmeal storage are attested Andean risk buffers."),
            p("spondylus_huaca_gifts", "Spondylus Huaca Gifts",
              "Offer spondylus, cloth, and chicha at local huacas without converting later Inka state cult into an AD 1 church.",
              "adm", CLERGY + PRESTIGE,
              "MOSELEY;P8.8", "contested",
              "Spondylus and local huaca offerings are secure; imperial solar cult is not backdated."),
        ),
    ),
    RegionalPack(
        "woodland",
        ("antq_american_group",),
        "regional_programmes_09.png",
        (
            p("copper_mica_exchanges", "Copper and Mica Exchanges",
              "Move Hopewell-horizon copper, mica, and marine shell through gift circuits without inventing a continental state.",
              "dip", TRADE + PRESTIGE,
              "CARR-HOPEWELL;P8.8", "secure",
              "Hopewell interaction is an exchange and ritual network, not a political empire."),
            p("canoe_portage_marks", "Canoe Portage Marks",
              "Keep canoes, paddles, and portage poles at the carries that join river basins for seasonal travel.",
              "dip", LOGISTICS + NAVY,
              "CARR-HOPEWELL;P8.8", "secure",
              "River canoe travel is the woodland long-distance means."),
            p("hunt_cache_pits", "Hunt Cache Pits",
              "Hide dried meat, hides, and spare points along a seasonal hunt so a winter camp is not emptied by one failure.",
              "adm", FOOD + TRIBES,
              "CARR-HOPEWELL;P8.8", "secure",
              "Seasonal hunting caches are ordinary Eastern Woodland practice."),
            p("earthwork_labor_cords", "Earthwork Labor Cords",
              "Call bounded labor for earthworks and repair without claiming later Mississippian chiefly corvée as an AD 1 constitution.",
              "adm", PUBLIC_WORKS + TRIBES,
              "CARR-HOPEWELL;P8.8", "contested",
              "Middle Woodland earthwork labor is real; Cahokia-style kingship is not projected backward."),
        ),
    ),
    RegionalPack(
        "highland",
        ("antq_tibetan_group",),
        "regional_programmes_10.png",
        (
            p("barley_threshing_floors", "Barley Threshing Floors",
              "Share threshing floors, winnowing, and seed barley after the short high-valley harvest.",
              "adm", FOOD + PEASANTS,
              "CAM-TIB-ARCH;ANT-BANGGA;P8.3", "secure",
              "Naked barley is the documented high-plateau staple of the Yarlung and Tsangpo valleys."),
            p("yak_salt_caravans", "Yak Salt Caravans",
              "Load salt cakes, barley, and yak-hair packs for the high-pass exchanges that link valleys to lakes.",
              "dip", TRADE + LOGISTICS,
              "CAM-TIB-ARCH;P8.3", "secure",
              "Salt and barley movement by yak is the ordinary plateau exchange; later tea-horse offices are excluded."),
            p("pass_cairn_watches", "Pass Cairn Watches",
              "Maintain cairns, windbreaks, and emergency dung-fuel at the passes that close for half the year.",
              "adm", LOGISTICS + TRIBES,
              "CAM-TIB-ARCH;P8.3", "secure",
              "High-pass infrastructure is a survival office, not a later imperial road department."),
            p("hearth_sanctuary_stores", "Hearth Sanctuary Stores",
              "Protect butter, barley beer, and copper vessels at household and landscape sanctuaries without backdating later Bon or Buddhist institutions.",
              "adm", CLERGY + FOOD,
              "CAM-TIB-ARCH;P8.3;P11", "contested",
              "Household and landscape ritual stores are the conservative plateau claim."),
        ),
    ),
    RegionalPack(
        "semitic",
        ("antq_semitic_group",),
        "regional_programmes_11.png",
        (
            p("well_right_stones", "Well Right Stones",
              "Witness well-mouth stones, watering turns, and compensation when a flock overdraws a desert well.",
              "adm", ASSIZE + FOOD,
              "P8.2;OCD;CAH-X", "secure",
              "Well rights are the ordinary Arabian and Levantine pastoral public good."),
            p("incense_caravan_seals", "Incense Caravan Seals",
              "Seal incense, myrrh, and leather water-skins and assign escorts along the north-south caravan chain.",
              "dip", TRADE + LOGISTICS,
              "P8.2;CAH-X;PERIPLUS", "secure",
              "Incense-route sealing and escort are attested; Himyar and Nabataea keep their deeper court offices."),
            p("date_grove_shares", "Date Grove Shares",
              "Apportion irrigation turns, pollination labor, and dried-date stores among oasis households.",
              "adm", FOOD + PEASANTS,
              "P8.2;CAH-X", "secure",
              "Date oasis agriculture is the ordinary Arabian settled base."),
            p("high_place_incense", "High-Place Incense",
              "Keep incense, standing stones, and votive plaques at high places and town sanctuaries without inventing a later caliphal waqf.",
              "adm", CLERGY + PRESTIGE,
              "P8.2;OCD;P11", "contested",
              "High-place and civic incense cult is attested across the Semitic world; Islamic institutions are excluded."),
        ),
    ),
    RegionalPack(
        "berber",
        ("antq_berber_group",),
        "regional_programmes_12.png",
        (
            p("transhumance_cairns", "Transhumance Cairns",
              "Mark summer and winter pastures and the cairns that keep flocks off sown valley floors.",
              "adm", FOOD + TRIBES,
              "P8.5;CAH-X;STRABO", "secure",
              "Atlas and pre-desert transhumance is the ordinary Numidian and Gaetulian subsistence."),
            p("foggara_water_turns", "Foggara Water Turns",
              "Share underground channel labor and watering turns in oases that cannot be farmed from rainfall.",
              "adm", PUBLIC_WORKS + PEASANTS,
              "P8.5;UNESCO-AFR", "secure",
              "Saharan foggara/qanat irrigation is an ancient oasis technique, not a later colonial well-field."),
            p("salt_slab_caravans", "Salt Slab Caravans",
              "Load salt slabs, dates, and hides and assign desert escorts without inventing a later trans-Saharan empire.",
              "dip", TRADE + LOGISTICS,
              "P8.5;CAH-X", "contested",
              "Saharan salt movement is real; medieval Ghana/Mali route politics are not backdated."),
            p("tumulus_ancestor_gifts", "Tumulus Ancestor Gifts",
              "Place pottery, weapons, and food at ancestral tumuli that authorize pasture and oasis claims.",
              "adm", CLERGY + TRIBES,
              "P8.5;CAH-X", "secure",
              "Numidian and Saharan tumulus landscapes are the attested ancestral claim."),
        ),
    ),
    RegionalPack(
        "inner",
        ("antq_iranian_group", "antq_steppe_group"),
        "regional_programmes_14.png",
        (
            p("oasis_canal_turns", "Oasis Canal Turns",
              "Share sluice labor, watering hours, and canal-bank repair among oasis and river-margin communities of Inner Asia.",
              "adm", PUBLIC_WORKS + PEASANTS,
              "CAH-XI;IRAN-ADMIN;P8.2", "secure",
              "Oasis irrigation is the ordinary Tarim and Transoxianan settled base; no later Islamic waqf office is implied."),
            p("caravan_seal_packets", "Caravan Seal Packets",
              "Seal cargo, assign escorts, and record compensation along the oasis and steppe exchange corridors.",
              "dip", TRADE + LOGISTICS,
              "CAH-XI;P8.2;P8.3", "secure",
              "Sealed long-distance cargo is attested across the Inner Asian corridors without asserting a single imperial post."),
            p("remount_bit_stores", "Remount Bit Stores",
              "Keep bits, bridles, felt saddle-cloths, and replacement mounts ready for envoys and a bounded campaign season.",
              "mil", MIL + LOGISTICS,
              "CAH-XI;P8.3;IRAN-ADMIN", "secure",
              "Remount custody is shared by Iranian and steppe polities; later Mongol decimal horse-relays are excluded."),
            p("fire_and_gift_plaques", "Fire and Gift Plaques",
              "Protect fire-dishes, libation bowls, and prestige plaques used in oath, guest, and lineage rites.",
              "adm", CLERGY + PRESTIGE,
              "CAH-XI;IRAN-ADMIN;P8.2", "contested",
              "Fire and gift ritual is a conservative Inner Asian adapter; it does not reconstruct a uniform Magian church."),
        ),
    ),
    RegionalPack(
        "caucasian",
        ("antq_caucasian_group", "antq_balkan_group"),
        "regional_programmes_13.png",
        (
            p("pass_tower_watches", "Pass Tower Watches",
              "Keep firewood, missiles, and a night watch on the defiles that close a highland valley.",
              "mil", MIL + LOGISTICS,
              "P8.2;STRABO;CAH-X", "secure",
              "Caucasian and Balkan highland passes are the ordinary defensive geography."),
            p("wine_amphora_shares", "Wine Amphora Shares",
              "Count amphorae, vine-props, and guest-wine before a highland feast or tribute gift.",
              "adm", TRADE + PRESTIGE,
              "P8.2;STRABO;CAH-X", "secure",
              "Colchian and Caucasian viticulture is classical; this is not a later Georgian royal cellar."),
            p("hillfort_grain_bins", "Hillfort Grain Bins",
              "Inspect timber bins and smoked meat inside hillforts that must feed a closed-in winter.",
              "adm", FOOD + MIL,
              "P8.2;CAH-X", "secure",
              "Hillfort storage is the ordinary Balkan and Caucasian winter reserve."),
            p("hostage_surety_tokens", "Hostage Surety Tokens",
              "Keep tokens, gifts, and named hostages that bind valley confederacies after a raid.",
              "dip", PRESTIGE + ASSIZE,
              "P8.2;STRABO;CAH-X", "secure",
              "Hostage and gift surety is the attested highland diplomacy; no later feudal homage is implied."),
        ),
    ),
)


SMALL_STATE_PROFILE_SLUGS = ("civic", "gana", "steppe", "tribal", "sacral", "royal")

SHEET_HASHES = {
    "regional_programmes_01.png": "13425860d3a32d213b454c65e0f01b1f2814185fabea02d6d0c88bb4e7d7031f",
    "regional_programmes_02.png": "13dfec17cc29515393f61283bb301521432c11404f4b69ce606b88b9a1c0b6de",
    "regional_programmes_03.png": "45187045093971cff7c847774d40b21a24b652dcd587e1413d4eb506f0f11a60",
    "regional_programmes_04.png": "41a8694c183446cc9fac3c5729a7e1ed9fc212a46ba3fed6c45e39f0a67ca207",
    "regional_programmes_05.png": "d0e1d56dc087ce13c619ae09fde661f818d3ad7ecf925d752d0cab88cdeb63e3",
    "regional_programmes_06.png": "d795d75f46671a82a3d96c842615bd8c1f1db65611f3ba208594b891bec06274",
    "regional_programmes_07.png": "6ce85bddad3e18c00d2a52364349bc853f2f9d040fabb6fe305cece0f407c8df",
    "regional_programmes_08.png": "f173abcc3d09554d3b053cf943bfcd80fd4b94840d6dab9636d3429fec9b8c26",
    "regional_programmes_09.png": "e128d9c044ba06a3b7fc18bf90f4096ec839a800aaffa5ad6c00e95db9ae98f9",
    "regional_programmes_10.png": "4fcb825f4e78883eb086ad278661a97590c45863a40d6415de57d18216e99c97",
    "regional_programmes_11.png": "08f5b1395d7141fc54d9c38466632e06a000a1bbbf3883c2066f2efdf42edccb",
    "regional_programmes_12.png": "1958f81996d1af4da6ddf85a0855fa1233c86512616a9127d20cb8d06c887396",
    "regional_programmes_13.png": "d6e4a93892f610d7e9e75db431d1382475331583bf7d183c66d041b38ad25d68",
    "regional_programmes_14.png": "d5a3f0391237510fd60da801610bff47d707944899e2b728d1329c9da644e535",
}


def all_programmes() -> tuple[tuple[RegionalPack, RegionalProgramme], ...]:
    return tuple((pack, programme) for pack in REGIONAL_PACKS for programme in pack.programmes)


def action_key(pack: RegionalPack, programme: RegionalProgramme) -> str:
    return f"antq_regprog_{pack.slug}_{programme.slug}"


def culture_groups_for_tag(group: str) -> tuple[RegionalPack, ...]:
    return tuple(pack for pack in REGIONAL_PACKS if group in pack.culture_groups)


def covered_culture_groups() -> set[str]:
    return {group for pack in REGIONAL_PACKS for group in pack.culture_groups}
