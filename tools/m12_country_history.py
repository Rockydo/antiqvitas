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
        "strengthen settlement and exchange without projecting later states onto the present landscape",
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
        "build durable regional ties without assuming a unified court or later political order",
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
        "hold followers and neighbours together without turning a negotiated people into an anachronistic bureaucracy",
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
        "preserve local networks and avoid false centralization while responding to pressure from mobile neighbours",
    ),
    "Finland": (
        "Small coastal and inland communities depend on fishing, hunting, farming, and northern exchange.",
        "sustain local networks across a sparse landscape without imposing later ethnic borders",
    ),
    "Britain": (
        "Britain is divided among regional peoples, oppida, farmed lowlands, and less centralized upland communities.",
        "manage neighbouring peoples and growing Roman attention while keeping local authority credible",
    ),
    "Ireland": (
        "Hibernian communities are represented through a cautious regional frame because surviving geography is late and imprecise.",
        "strengthen local exchange and leadership without converting uncertain names into fixed borders",
    ),
    "Danube": (
        "Dacian, Getic, Germanic, and Sarmatian powers meet along the Danube and Carpathian approaches.",
        "control routes and alliances while preparing for pressure from Rome and neighbouring confederations",
    ),
    "Southeast Asia": (
        "River valleys, early cities, ports, and forest exchange connect mainland and island Southeast Asia to wider seas.",
        "support settlement and exchange while keeping political claims no stronger than the evidence",
    ),
    "Oceania": (
        "Seafaring communities maintain island networks through navigation, kinship, horticulture, and exchange.",
        "sustain voyaging and local resilience without projecting later island kingdoms backward",
    ),
    "Mesoamerica": (
        "Urban centres and regional communities compete through agriculture, exchange, ritual authority, and monument building.",
        "maintain food, water, and regional legitimacy while navigating rival centres",
    ),
    "Andes": (
        "Coastal valleys and highland basins support distinct communities linked by exchange and ritual landscapes.",
        "coordinate water, labour, and exchange without assuming later imperial institutions",
    ),
    "Northern Andes": (
        "Highland and intermontane communities combine farming, exchange, and localized political authority.",
        "secure productive landscapes and regional ties without backdating later confederations",
    ),
    "North America": (
        "Woodland, plains, coastal, desert, and Arctic communities follow diverse subsistence and exchange strategies.",
        "strengthen reciprocal networks while keeping authority appropriate to local evidence",
    ),
    "Caribbean-Amazon": (
        "River and island communities rely on horticulture, fishing, mobility, and long exchange networks.",
        "protect settlement and exchange while avoiding later external categories",
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
            "This playable frame represents a bounded network of communities, "
            "not a claim of uniform centralized statehood."
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
        f"The immediate task is to {task}. Choices should strengthen this "
        "position through period institutions, local alliances, and sustainable "
        "resources rather than knowledge of later history."
    )


def entries() -> list[dict[str, str]]:
    tags = engine_tags()
    output: list[dict[str, str]] = []
    for row in read_rows():
        design = row["tag"]
        engine = tags.get(design)
        if not engine:
            raise ValueError(f"missing engine tag for {design}")
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
