#!/usr/bin/env python3
"""Generate exact AD 1 country-history agendas for every playable start."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLITIES = ROOT / "docs/world_1ad/polities.csv"
TAG_MAP = ROOT / "docs/world_1ad/tag_map.json"
LEDGER = ROOT / "docs/m12/country_history_agendas.csv"
CUSTOMIZABLE = (
    ROOT / "in_game/common/customizable_localization/country_history.txt"
)
LANGUAGES = (
    "english",
    "french",
    "german",
    "spanish",
    "polish",
    "russian",
    "braz_por",
    "simp_chinese",
    "japanese",
    "korean",
    "turkish",
)
FORBIDDEN = re.compile(
    r"\b(?:renaissance|feudalis[mt]|gunpowder|colonial|absolutis[mt]|"
    r"revolution|enlightenment|rifle|redcoat|grenzer)\b",
    re.IGNORECASE,
)


REGIONS: dict[str, tuple[str, str]] = {
    "Rome": (
        "Mediterranean revenues, provincial cities, client courts, and long frontiers bind a vast dominion together.",
        "keep the provinces supplied, the army obedient, and dependent rulers useful without exhausting local communities",
    ),
    "Levant": (
        "Temple communities, caravan routes, Hellenistic cities, and Roman power meet across the southern Levant.",
        "balance local law and cult with taxation, urban rivalry, and the demands of stronger neighbours",
    ),
    "Arabia": (
        "Incense routes, irrigated kingdoms, oases, pastoral ranges, and Red Sea ports sustain distinct Arabian communities.",
        "secure water and caravan exchange while negotiating between settled courts and mobile kin networks",
    ),
    "Anatolia": (
        "Old royal houses and self-governing cities persist beneath growing Roman influence in Anatolia.",
        "preserve local authority, connect inland production to the coasts, and avoid becoming a frontier pawn",
    ),
    "Balkans": (
        "Mountain routes and Thracian communities stand between the Aegean, Danube, and Roman provincial order.",
        "hold local elites together while protecting routes and bargaining with Roman commanders",
    ),
    "Pontic": (
        "Greek ports, steppe peoples, and dynastic courts contest the shores and hinterlands of the Black Sea.",
        "keep ports and pastoral corridors connected without allowing either urban or steppe interests to dominate",
    ),
    "Africa": (
        "Nile, Red Sea, Saharan, Maghrebi, and Horn networks support sharply different African societies.",
        "protect the ecological base of power and turn long-distance exchange into durable local authority",
    ),
    "West Africa": (
        "Iron-working communities and inland exchange networks grow along the Niger, Volta, and their neighbouring zones.",
        "strengthen settlement, ironworking, river exchange, and obligations among neighbouring communities",
    ),
    "Iran": (
        "The Arsacid order joins Iranian uplands, Mesopotamian cities, caravan routes, and powerful local houses.",
        "manage noble and client autonomy while guarding the routes that connect Iran to Mesopotamia and Central Asia",
    ),
    "Mesopotamia": (
        "River cities, temple estates, caravan corridors, and small dynasties occupy the space between Rome and Arsacid Iran.",
        "preserve local revenues and legitimacy while navigating pressure from both imperial frontiers",
    ),
    "Central Asia": (
        "Oasis cities, irrigated valleys, and mobile confederations link Iran, India, the steppe, and Han exchange.",
        "keep routes open and alliances flexible while preventing stronger neighbours from mastering the oases",
    ),
    "Caucasus": (
        "Mountain corridors and lowland courts divide influence among Rome, Arsacid Iran, and resilient local elites.",
        "control passes and dynastic ties without surrendering autonomy to either great power",
    ),
    "China": (
        "The Western Han realm rests on commanderies, agrarian revenues, court institutions, and guarded frontier corridors.",
        "steady the court, maintain grain and river systems, and keep frontier commands answerable to the centre",
    ),
    "Steppe": (
        "Mobile households, tribute, pasture, and negotiated leadership sustain confederations across Inner Asia.",
        "maintain cohesion and access to pasture and exchange without mistaking alliance for permanent central rule",
    ),
    "Tarim": (
        "Independent oasis courts depend on irrigation and caravan traffic between Han territory and Central Asia.",
        "protect water, merchants, and diplomatic room while meeting tributary obligations selectively",
    ),
    "Korea": (
        "Commanderies, walled settlements, river valleys, and emerging courts compete across the Korean peninsula and Manchuria.",
        "consolidate local communities while choosing carefully between Han contact, northern rivals, and southern exchange",
    ),
    "Japan": (
        "Yayoi communities are regionally divided, with wet-rice agriculture, bronze and iron exchange, and kin leadership.",
        "build durable regional ties through rice cultivation, seaborne exchange, ritual authority, and kin leadership",
    ),
    "India": (
        "The subcontinent contains major courts, republic-like communities, ports, caravan routes, and competing religious traditions.",
        "bind local revenues and exchange to legitimate authority while respecting the region's political diversity",
    ),
    "Lanka": (
        "Anuradhapura links irrigated agriculture, Buddhist institutions, and Indian Ocean exchange.",
        "maintain tanks, monasteries, and ports while keeping the island court coherent",
    ),
    "Germania": (
        "Kin groups, assemblies, war leaders, farms, and exchange routes shape Germania beyond direct Roman rule.",
        "hold followers and neighbours together while keeping authority rooted in assemblies, oaths, hospitality, and personal obligation",
    ),
    "Scandinavia": (
        "Farming, seaborne exchange, and local chiefly networks connect communities around the Baltic approaches.",
        "build influence through exchange and assembly while preserving the autonomy of local communities",
    ),
    "Baltic": (
        "Coastal exchange, amber routes, and dispersed communities connect the eastern Baltic to Central Europe.",
        "protect exchange routes while keeping authority grounded in local consent",
    ),
    "Eastern Europe": (
        "Forest, river, and steppe margins contain dispersed peoples known imperfectly to Mediterranean authors.",
        "preserve river and forest networks while coordinating defence against pressure from mobile neighbours",
    ),
    "Finland": (
        "Small coastal and inland communities depend on fishing, hunting, farming, and northern exchange.",
        "sustain coastal and inland networks through fishing, hunting, farming, portage, and seasonal exchange",
    ),
    "Britain": (
        "Britain is divided among regional peoples, oppida, farmed lowlands, and less centralized upland communities.",
        "manage neighbouring peoples and growing Roman attention while keeping local authority credible",
    ),
    "Ireland": (
        "Hibernian communities rely on cattle, mixed farming, river routes, coastal exchange, and local assemblies.",
        "strengthen local exchange, household alliances, and defensible centres while preserving negotiated authority",
    ),
    "Danube": (
        "Dacian, Getic, Germanic, and Sarmatian powers meet along the Danube and Carpathian approaches.",
        "control routes and alliances while preparing for pressure from Rome and neighbouring confederations",
    ),
    "Southeast Asia": (
        "River valleys, early cities, ports, and forest exchange connect mainland and island Southeast Asia to wider seas.",
        "support settlement, forest exchange, river transport, and maritime ties while balancing local authorities",
    ),
    "Oceania": (
        "Seafaring communities maintain island networks through navigation, kinship, horticulture, and exchange.",
        "sustain voyaging, horticulture, reciprocal exchange, and resilient ties among island communities",
    ),
    "Mesoamerica": (
        "Urban centres and regional communities compete through agriculture, exchange, ritual authority, and monument building.",
        "maintain food, water, and regional legitimacy while navigating rival centres",
    ),
    "Andes": (
        "Coastal valleys and highland basins support distinct communities linked by exchange and ritual landscapes.",
        "coordinate water, labour, exchange, and ritual centres across coastal valleys and highland basins",
    ),
    "Northern Andes": (
        "Highland and intermontane communities combine farming, exchange, and localized political authority.",
        "secure productive landscapes and regional ties through local councils, exchange, and mutual defence",
    ),
    "North America": (
        "Woodland, plains, coastal, desert, and Arctic communities follow diverse subsistence and exchange strategies.",
        "strengthen reciprocal networks, seasonal stores, exchange routes, and trusted community leadership",
    ),
    "Caribbean-Amazon": (
        "River and island communities rely on horticulture, fishing, mobility, and long exchange networks.",
        "protect settlements, fisheries, gardens, river passages, and long-distance exchange",
    ),
}


SPECIAL: dict[str, str] = {
    "ROM": (
        "On 1 January AD 1, Augustus governs the Roman Empire through a Principate that joins republican offices to personal command. "
        "Mediterranean revenues, provincial cities, client courts, and frontier armies make Rome powerful but difficult to balance.\n\n"
        "Keep the legions loyal, feed the great cities, and make provincial government sustainable. Client rulers and local elites must remain useful partners rather than empty dependants, while succession around the imperial household remains a political question."
    ),
    "PAR": (
        "On 1 January AD 1, the Parthian Empire's Arsacid court at Ctesiphon rules through royal prestige, powerful houses, client kings, and the revenues of Mesopotamia and the Iranian plateau. "
        "Its strength is real, but negotiated authority makes every succession and frontier settlement delicate.\n\n"
        "Preserve the allegiance of nobles and sub-kings, protect caravan and river routes, and contest Roman influence without allowing a distant war to fracture the Arsacid realm."
    ),
    "HAN": (
        "On 1 January AD 1, the child Emperor Ping occupies the Western Han throne while Wang Mang directs the regency. "
        "Commanderies, agrarian revenues, court institutions, and frontier corridors sustain the realm, but court factions and concentrated influence threaten the balance of government.\n\n"
        "Steady the court, maintain grain and river systems, and keep provincial and frontier commands answerable to the centre. Reform must strengthen legitimate institutions rather than merely one household."
    ),
    "XIO": (
        "On 1 January AD 1, Wuzhuliu Chanyu leads the Xiongnu Confederation through negotiated allegiance, pasture access, tribute, and the authority of the ruling house. "
        "Peace with Han supports exchange, yet subordinate leaders and distant groups retain their own interests.\n\n"
        "Maintain confederate cohesion, secure pasture and trade, and bargain from strength without treating mobile alliances as permanent administrative provinces."
    ),
    "ARM": (
        "On 1 January AD 1, the Kingdom of Armenia's court at Artaxata occupies the strategic highlands between Roman and Arsacid spheres. "
        "Dynastic ties, noble houses, mountain routes, and the competing expectations of both empires shape every decision.\n\n"
        "Preserve the kingdom's autonomy by balancing external patrons, securing the passes, and keeping Armenian elites invested in the crown."
    ),
    "MCM": (
        "On 1 January AD 1, Maroboduus has established a substantial Marcomannic kingdom in Bohemia. "
        "Its power depends on followers, neighbouring peoples, exchange, and negotiated Germanic leadership rather than a Roman-style administration.\n\n"
        "Hold the coalition together, develop defensible centres, and decide how firmly to oppose or accommodate Roman influence along the Danube."
    ),
    "JUD": (
        "On 1 January AD 1, Herodian Judea governs Jerusalem and its surrounding communities under Roman supremacy. "
        "Temple authority, local law, dynastic legitimacy, taxation, and relations among towns and rural districts make rule exceptionally sensitive.\n\n"
        "Preserve order without severing local legitimacy, meet imperial obligations without ruinous extraction, and keep factional disputes from inviting direct intervention."
    ),
    "NAB": (
        "On 1 January AD 1, Aretas IV rules Nabataea from Petra, linking the settled core to Hegra, northwestern Arabian routes, and Red Sea exchange while accommodating Roman power in the Levant. "
        "Caravan tolls, irrigated settlements, pastoral partners, and a multilingual court sustain the kingdom; the southern edge represented on the campaign map remains deliberately uncertain.\n\n"
        "Protect Petra and Hegra, keep the caravan and water systems productive, and preserve useful autonomy without allowing Roman patronage or rival Arabian routes to dictate Nabataean policy."
    ),
    "SAB": (
        "On 1 January AD 1, Saba remains rooted in Marib's irrigated landscape, temples, and caravan connections. "
        "Its anonymous campaign court faces neighbouring Qataban and the rising Himyarite polity; the map does not project Saba's earlier maximum extent into the present.\n\n"
        "Maintain the Marib waterworks and highland communities, secure incense exchange, and balance dynastic competition without treating every neighbouring settlement as a permanent province."
    ),
    "HIM": (
        "On 1 January AD 1, Himyar is an emerging southwestern Arabian kingdom centred on Zafar. "
        "It is represented separately from Saba, Qataban, and Hadramawt because the conquests that later united much of South Arabia have not yet occurred.\n\n"
        "Strengthen the Zafar court, connect highland agriculture to Red Sea and incense traffic, and compete for alliances without receiving the later Himyarite empire in advance."
    ),
    "QAT": (
        "On 1 January AD 1, Qataban is centred on Timna in the Bayhan valley and participates directly in the South Arabian incense routes. "
        "Its court, temples, irrigated agriculture, and position between stronger neighbours make route access more important than broad territorial uniformity.\n\n"
        "Protect Timna and its caravan corridor, maintain local water and cult institutions, and keep Sabaean or Himyarite pressure from turning Qataban into a mere transit district."
    ),
    "HAD": (
        "On 1 January AD 1, Hadramawt is centred on Shabwa and commands an eastern branch of the incense-producing and caravan landscape. "
        "The kingdom's long valleys, ports, and desert approaches demand negotiated control rather than effortless rule across empty space.\n\n"
        "Keep Shabwa linked to incense country and maritime outlets, secure wells and caravan stages, and prevent rivals from isolating the Hadrami court from either coast or interior."
    ),
    "KIN": (
        "On 1 January AD 1, the Kindah campaign frame is anchored at Qaryat al-Faw on the south-central Arabian caravan crossroads. "
        "It represents a bounded network around the oasis and routes rather than the much later Kindite kingdom or a unified dominion over Najd.\n\n"
        "Sustain the oasis, bargain with mobile kin groups and South Arabian courts, and turn caravan access into durable influence without imposing a premature royal bureaucracy."
    ),
    "THM": (
        "On 1 January AD 1, Thamud is represented across a bounded northwestern Arabian range-and-oasis frame attested by classical ethnography. "
        "The people-name is applied only to groups attested by classical ethnography, and Khaybar serves as the practical campaign anchor.\n\n"
        "Coordinate wells, grazing, and caravan passage through assemblies and local leaders while resisting Nabataean expansion and avoiding claims to a centralized territorial state unsupported by the evidence."
    ),
    "AGR": (
        "On 1 January AD 1, the Agraeans occupy a northern Arabian oasis-route frame anchored at Dumat al-Jandal. "
        "Strabo's ethnography supports a distinct people, but neither fixed borders nor a named campaign-boundary monarch survive.\n\n"
        "Keep the northern wells and caravan passages open, balance neighbouring peoples and Nabataean interests, and build authority through route protection and consent rather than invented royal administration."
    ),
    "GRH": (
        "On 1 January AD 1, Gerrha is a wealthy eastern Arabian trade polity connected to Gulf shipping and overland exchange. "
        "Its exact archaeological identification remains disputed, so al-Ahsa is an explicit gameplay proxy rather than a claim that the ancient city has been located there with certainty.\n\n"
        "Protect oasis agriculture and Gulf access, mediate caravan and maritime commerce, and preserve local autonomy between Arabian interiors and the powers of Mesopotamia."
    ),
    "QTR": (
        "On 1 January AD 1, the Cataraei are represented along a narrow Gulf-coast frame around the Qatar peninsula. "
        "The principal geographic witness is later than the campaign start, so Catara and the al-Bidda anchor remain cautious proxies rather than a reconstructed centralized state.\n\n"
        "Sustain coastal exchange, fishing, and caravan links while keeping local leaders aligned and avoiding unsupported expansion across the Gulf littoral."
    ),
    "OMN": (
        "On 1 January AD 1, the Omanitae campaign frame joins selected northern Omani coast and interior routes. "
        "Classical Omana is not securely identified with Suhar, which serves only as a conservative playable anchor for a region linked to Gulf and Indian Ocean exchange.\n\n"
        "Coordinate coast, oasis, and mountain communities, protect maritime exchange, and keep authority flexible where the evidence supports a people and trading region more clearly than a single court."
    ),
    "BED": (
        "On 1 January AD 1, the Chaulotaeans occupy a bounded north-central Arabian caravan-country frame known from Strabo. "
        "Fayd is a route anchor rather than an attested capital, and the polity does not stand for every mobile or oasis community of interior Arabia.\n\n"
        "Secure seasonal pasture, wells, and passage agreements, maintain cohesion among local leaders, and compete for caravan influence without becoming another peninsula-wide aggregation."
    ),
    "GOG": (
        "On 1 January AD 1, Goguryeo is an emerging northern kingdom centred on Gungnae. "
        "Mountain strongholds, river valleys, neighbouring peoples, and the nearby Han commanderies define its opportunities and dangers.\n\n"
        "Consolidate communities and routes, protect the court, and expand influence without assuming that the peninsula is already politically unified."
    ),
    "SAT": (
        "On 1 January AD 1, Satavahana authority links parts of the Deccan to inland production and western and eastern exchange routes. "
        "Regional elites, rival powers, and valuable ports prevent effortless centralization.\n\n"
        "Secure revenue corridors, maintain legitimacy among local communities, and strengthen the court without flattening the Deccan's political diversity."
    ),
    "KUS": (
        "On 1 January AD 1, the kingdom of Kush at Meroe draws strength from Nile agriculture, royal and temple institutions, iron production, and routes toward the Red Sea and inner Africa. "
        "Relations with Roman Egypt matter, but Kushite priorities remain rooted in the Middle Nile.\n\n"
        "Protect irrigation and exchange, sustain royal legitimacy, and keep frontier diplomacy from subordinating Meroe to northern interests."
    ),
    "AKS": (
        "On 1 January AD 1, Aksum is growing within the northern Horn's highland and Red Sea networks. "
        "Agriculture, caravan exchange, ports, and relations with Arabian communities offer opportunity without guaranteeing later dominance.\n\n"
        "Connect highland production to maritime trade, consolidate local authority, and compete for routes without projecting future conquests into the present."
    ),
    "WAA": (
        "On 1 January AD 1, the Wa polities are divided among Yayoi regional and kin-group communities. "
        "Wet-rice agriculture, bronze and iron exchange, ritual authority, and seaborne contact shape local competition.\n\n"
        "Build durable alliances and productive settlements without assuming a unified Japanese court or knowledge of later centres."
    ),
}

BRITAIN_IRELAND_FOCUS: dict[str, str] = {
    "CAT": "Verlamion and the middle Thames oppida connect coin-using elites to neighbouring southeastern courts",
    "TRI": "Camulodunum and the Thames estuary support exchange while overlapping coin evidence makes the western frontier uncertain",
    "ICE": "the East Anglian lowlands support farming, metal exchange, and dispersed local authority around Venta",
    "BRI": "a large northern network spans Pennine routes and both coasts without implying effortless centralized control",
    "ATB": "Calleva's coin-using court and Channel contacts create both wealth and exposure to continental and Roman influence",
    "SIL": "the southeastern Welsh uplands and Severn approaches reward mobile defence and control of difficult routes",
    "ORD": "the northern Welsh uplands, western coast, and Mona-facing routes favour dispersed strongholds and local assemblies",
    "DUM": "the southwestern peninsula joins tin-bearing landscapes, Atlantic routes, and the Tamar-Isca corridor",
    "BRT": "the Kentish approaches command the shortest Channel crossings and a dense zone of exchange with northern Gaul",
    "REG": "the central south coast links sheltered harbours, farming districts, and neighbouring Atrebatic communities",
    "BLG": "the installed Wessex frame represents a western Belgic network rather than a fixed border around later Venta",
    "DUR": "the Dorset hillfort landscape and Channel coast support agriculture, craft production, and maritime exchange",
    "DOB": "the Severn-Cotswold zone links fertile valleys, Corinium, western routes, and coin-using elites",
    "COR": "the east Midlands and Lincolnshire routes connect mixed farming, river corridors, and Humber exchange",
    "CNV": "the Severn-Deva approaches join fortified uplands, salt and metal routes, and the western Midlands",
    "PBI": "the Humber estuary and Petuaria-facing coast favour maritime exchange while separating local interests from the wider Brigantian frame",
    "CRV": "the Cumbrian valleys and western Pennine approaches sustain a distinct regional network known more securely after the campaign date",
    "DEM": "the southwest Welsh coast and Maridunum-facing valleys connect pasture, metal routes, and Irish Sea exchange",
    "DEC": "the northeast Welsh coast and Canovium-facing corridor form a narrow contested frame between Ordovician and Cornovian neighbours",
    "VOT": "the Forth and eastern border country connect Traprain Law, coastal exchange, and routes toward the Tyne",
    "SEL": "the southern uplands around the Trimontium proxy divide Solway, Tweed, and Forth-facing routes",
    "NOV": "the southwestern peninsula around the Rerigonium proxy looks toward both the Irish Sea and Clyde",
    "DAM": "the Clyde valley and western lowlands connect coastal inlets, pasture, and inland movement",
    "VCN": "the Tay-Fife corridor around the Orrea proxy combines fertile lowlands, river movement, and eastern sea access",
    "TAE": "the northeastern coast around the Devana proxy links farming districts, fisheries, and difficult inland routes",
    "EPD": "the Epidium-facing peninsulas and inner islands depend on seaborne links more than continuous territorial administration",
    "VAC": "the Moray basin and the disputed Tuesis proxy connect fertile lowlands to Highland passages",
    "DCT": "the Ross and Varar-facing frame joins eastern firths to western mountain routes",
    "CAE": "the northwestern mainland frame is sparse and highly uncertain, with authority rooted in local communities",
    "CRE": "the western-island proxy reflects Ptolemy's relative ordering rather than a secure ethnic boundary on Skye",
    "CNA": "the northwestern coastal proxy reflects a named people but no recoverable campaign-boundary court",
    "LGB": "the eastern Sutherland proxy distinguishes Ptolemy's Lugi from similarly named continental peoples",
    "SME": "the far-northern mainland proxy preserves Ptolemy's ordering without inventing a centralized kingdom",
    "NCR": "the Caithness and northern-island frame is a gameplay attachment around Ptolemy's Cornavii, not a claim of uniform island identity",
    "CAL": "the reduced Caledonian forest-core preserves only geography that cannot be assigned more narrowly with confidence",
    "VNI": "the northwestern coast follows Ptolemy's relative order and Atlantic access rather than later political boundaries",
    "RHB": "the Rhobogdium-facing north coast supports maritime contact but no recoverable unitary court",
    "DAR": "the northern coastal proxy distinguishes the Darini from neighbouring Voluntii and Rhobogdii",
    "ERD": "the northwestern interior frame connects lakes, rivers, and Atlantic-facing routes across an uncertain boundary",
    "ULA": "the Voluntian northeastern frame replaces the later blanket Ulaid label and faces the North Channel and Irish Sea",
    "NAG": "the Magnata-facing western frame links Atlantic inlets to inland movement while its exact AD 1 frontier remains uncertain",
    "AUT": "the western Hibernian frame follows Ptolemy's coastal ordering across a landscape of dispersed communities",
    "GAN": "the west-central frame links the Shannon system and Atlantic approaches, with Sligo excluded for the Nagnatae",
    "VEL": "the southwestern peninsula depends on Atlantic routes, pasture, and local strongholds",
    "IVN": "the Iernis-facing southwest combines sheltered waters, farming districts, and maritime exchange",
    "USD": "the south-central frame follows Ptolemy's ordering across the Shannon and Suir-facing interior",
    "IBG": "the southeastern coastal proxy preserves Ptolemy's Irish Brigantes without merging them with the British people",
    "CND": "the southeastern interior proxy is deliberately small because Ptolemy places the Coriondi above the Brigantes",
    "MNP": "the Manapia-facing southeast commands Irish Sea crossings and coastal exchange",
    "CCI": "the eastern coastal frame follows Ptolemy's order between the Manapii and Eblani",
    "EBL": "the Eblana-facing eastern interior links the Boyne-Liffey zone while keeping the Cauci distinct",
}

SOUTHERN_BRITISH_TAGS = frozenset(
    {
        "CAT", "TRI", "ICE", "BRI", "ATB", "SIL", "ORD", "DUM", "BRT",
        "REG", "BLG", "DUR", "DOB", "COR", "CNV", "PBI", "CRV", "DEM", "DEC",
    }
)


def britain_ireland_text(row: dict[str, str]) -> str:
    design = row["tag"]
    focus = BRITAIN_IRELAND_FOCUS[design]
    if design in SOUTHERN_BRITISH_TAGS:
        task = (
            "Strengthen assemblies, productive settlements, hillfort or oppidum "
            "networks, and exchange while deciding how to answer neighbouring "
            "rivals and growing Roman attention."
        )
    elif row["region"] == "Britain":
        task = (
            "Keep local assemblies and route communities aligned, use pasture "
            "and seaborne exchange well, and resist both external pressure and "
            "the fiction of a permanent all-northern confederation."
        )
    else:
        task = (
            "Develop farming, cattle, craft, river, and maritime exchange; "
            "manage raiding and reciprocal obligations through local assemblies "
            "without importing later Irish kingdoms into AD 1."
        )
    return (
        f"On 1 January AD 1, {row['name']} is represented by a bounded campaign "
        f"frame anchored at {row['historical_capital']}; {focus}. Ptolemy's later "
        "and indirect geography does not establish an exact AD 1 frontier or a "
        "single centralized state.\n\n"
        f"{task}"
    )


def read_rows() -> list[dict[str, str]]:
    with POLITIES.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("polity roster is empty")
    tags = [row["tag"] for row in rows]
    if len(tags) != len(set(tags)):
        raise ValueError("polity roster contains duplicate design tags")
    return rows


def engine_tags() -> dict[str, str]:
    value = json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))
    return {
        row["design_tag"]: row["engine_tag"]
        for row in value["entries"]
    }


def role_text(kind: str) -> str:
    return {
        "subject": (
            "This dependent court must preserve local legitimacy while meeting "
            "obligations to its overlord and managing its own elites."
        ),
        "sop": (
            "Its neighbouring communities are joined by seasonal assemblies, "
            "kinship, exchange, ritual obligations, and mutual defence."
        ),
        "country": (
            "Its authority rests on the institutions, assemblies, courts, and "
            "alliances appropriate to its own region."
        ),
    }[kind]


def generic_text(row: dict[str, str]) -> str:
    context, task = REGIONS[row["region"]]
    return (
        f"On 1 January AD 1, {row['name']} is centred on "
        f"{row['historical_capital']}. {context} {role_text(row['kind'])}\n\n"
        f"The immediate task is to {task}. Durable rule will depend on local "
        "alliances, dependable stores, legitimate arbitration, and secure routes."
    )


def entries() -> list[dict[str, str]]:
    tags = engine_tags()
    output: list[dict[str, str]] = []
    for row in read_rows():
        design = row["tag"]
        engine = tags.get(design)
        if not engine:
            raise ValueError(f"missing engine tag for {design}")
        if design in BRITAIN_IRELAND_FOCUS:
            text = britain_ireland_text(row)
        else:
            text = SPECIAL.get(design, generic_text(row))
        output.append(
            {
                "design_tag": design,
                "engine_tag": engine,
                "name": row["name"],
                "tier": row["tier"],
                "kind": row["kind"],
                "region": row["region"],
                "capital": row["historical_capital"],
                "localization_key": f"antq_country_history_{engine}",
                "source": row["source"],
                "confidence": row["confidence"],
                "text": text,
            }
        )
    return output


def render_customizable(values: list[dict[str, str]]) -> str:
    lines = [
        "country_history = {",
        "\ttype = country",
        "",
        "\t# ANTIQVITAS exact AD 1 roster; generated by tools/m12_country_history.py.",
    ]
    for row in sorted(values, key=lambda item: item["engine_tag"]):
        lines.append(
            "\ttext = { localization_key = "
            f"{row['localization_key']} trigger = {{ tag = {row['engine_tag']} }} }}"
            f" # {row['design_tag']} - {row['name']}"
        )
    lines.extend(
        [
            "",
            "\ttext = { localization_key = antq_country_history_fallback fallback = yes }",
            "}",
            "",
        ]
    )
    return "\n".join(lines)


def quote(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def render_localization(values: list[dict[str, str]], language: str) -> str:
    lines = [f"l_{language}:"]
    for row in sorted(values, key=lambda item: item["engine_tag"]):
        lines.append(f' {row["localization_key"]}: "{quote(row["text"])}"')
    lines.append(
        ' antq_country_history_fallback: "On 1 January AD 1, this polity faces '
        'the immediate work of sustaining its communities, authority, and '
        'neighbours through institutions appropriate to its own region."'
    )
    return "\n".join(lines) + "\n"


def render_ledger(values: list[dict[str, str]]) -> str:
    from io import StringIO

    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=tuple(values[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(values)
    return output.getvalue()


def payloads() -> dict[Path, bytes]:
    values = entries()
    result = {
        CUSTOMIZABLE: b"\xef\xbb\xbf"
        + render_customizable(values).encode("utf-8"),
        LEDGER: b"\xef\xbb\xbf" + render_ledger(values).encode("utf-8"),
    }
    for language in LANGUAGES:
        path = (
            ROOT
            / "main_menu"
            / "localization"
            / language
            / f"country_history_l_{language}.yml"
        )
        result[path] = b"\xef\xbb\xbf" + render_localization(
            values, language
        ).encode("utf-8")
    return result


def write() -> None:
    values = entries()
    for path, data in payloads().items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    print(
        "m12_country_history: wrote "
        f"{len(values)} AD 1 agendas / {len(LANGUAGES)} client mirrors"
    )


def check() -> bool:
    failures: list[str] = []
    try:
        values = entries()
        expected = payloads()
    except (OSError, UnicodeError, ValueError, KeyError, csv.Error) as exc:
        print(f"m12_country_history: FAIL\n  - {exc}")
        return False
    for path, data in expected.items():
        if not path.is_file() or path.read_bytes() != data:
            failures.append(f"stale or missing {path.relative_to(ROOT)}")
    keys = [row["localization_key"] for row in values]
    tags = [row["engine_tag"] for row in values]
    if len(keys) != len(set(keys)) or len(tags) != len(set(tags)):
        failures.append("duplicate localization key or engine tag")
    if any(not row["text"].strip() for row in values):
        failures.append("blank agenda text")
    for row in values:
        match = FORBIDDEN.search(row["text"])
        if match:
            failures.append(
                f"{row['design_tag']}: prohibited player text {match.group(0)!r}"
            )
    tier_one = [row for row in values if row["tier"] == "1"]
    if any(row["name"] not in row["text"] for row in tier_one):
        failures.append("tier-one agenda missing its polity name")
    if failures:
        print("m12_country_history: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return False
    print(
        "m12_country_history: PASS "
        f"({len(values)} tags; {len(tier_one)} tier-one contexts; "
        f"{len(LANGUAGES)} mirrors; zero prohibited terms)"
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.write:
            write()
            return 0
        return 0 if check() else 1
    except (OSError, UnicodeError, ValueError, KeyError, csv.Error) as exc:
        print(f"m12_country_history: FAIL\n  - {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
