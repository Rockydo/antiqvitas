#!/usr/bin/env python3
"""Render consequential M11 phase events for the complete M10 chronology.

Each reviewed historical current develops through four dated decision points.
They reuse the current's sourced painting but require a real choice between
costly intervention and accepting political disruption.
"""

from __future__ import annotations

import argparse
import importlib
import re
from dataclasses import dataclass
from pathlib import Path

from dates import AntqDate, M2_MIRROR_LANGUAGES, days_between, load_timeline, offset_date
from m10_history import (
    event_path_variable,
    teutoburg_opponent_capture_lines,
    validate_ai_chance_syntax,
)
from m10_situation_actions import THEME_BY_KEY as SITUATION_THEMES
from m11_first_century_events import CURRENT_EFFECTS, packages_are_unique


ROOT = Path(__file__).resolve().parents[1]
TIMELINE = ROOT / "docs/timeline.csv"
EVENT_OUTPUT = ROOT / "in_game/events/antq_m11_flavor_phases.txt"
LOC_ROOT = ROOT / "main_menu/localization"
M10_EVENT_FILES = tuple(sorted((ROOT / "in_game/events").glob("antq_m10_*.txt")))
START_COUNTRIES = ROOT / "in_game/setup/countries/antq_00_world.txt"
TARGET_TOTAL = 400
WINDOW_DAYS = 62
PHASES = (
    ("conditions", "Conditions Develop"),
    ("pressure", "Pressure Builds"),
    ("contest", "A Contested Moment"),
    ("closing", "The Window Narrows"),
)
PHASE_COSTS = {"conditions": 8, "pressure": 14, "contest": 22, "closing": 12}
THEME_KEYWORDS = (
    ("belief", ("religion", "christian", "buddh", "temple", "council", "conversion", "manichae", "olympic")),
    ("exchange", ("embassy", "mission", "paper", "silk", "trade", "faxian", "learning", "silphium")),
    ("migration", ("migration", "refugee", "settlement", "abandoned", "adventus", "crossing")),
    ("civil_war", ("civil", "succession", "emperors", "three_kingdoms", "eight_princes", "usurp")),
    ("rebellion", ("revolt", "rebellion", "uprising", "turbans", "boudica", "tacfarinas")),
    ("campaign", ("war", "battle", "campaign", "invasion", "conquest", "sack", "frontier", "teutoburg")),
    ("diplomacy", ("settlement", "treaty", "coronation", "annexation", "partition", "embassy")),
)

# Every phrase contains the current's reviewed title, so no two historical
# currents present cloned choices even when they share a broad mechanic family.
CHOICE_TEXT = {
    "campaign": {
        "conditions": ("Survey the approaches for {label}", "Rely on the frontier commands during {label}"),
        "pressure": ("Reinforce the field depots for {label}", "Call allied contingents into {label}"),
        "contest": ("Commit the central reserve to {label}", "Trade ground for time during {label}"),
        "closing": ("Fund the military settlement of {label}", "Entrust the settlement of {label} to provincial commanders"),
    },
    "rebellion": {
        "conditions": ("Investigate the grievances behind {label}", "Demand immediate obedience during {label}"),
        "pressure": ("Offer redress and conditional amnesty in {label}", "Secure loyal garrisons against {label}"),
        "contest": ("Separate negotiators from the leaders of {label}", "Concentrate the field army for {label}"),
        "closing": ("Guarantee the negotiated settlement of {label}", "Impose a punitive settlement after {label}"),
    },
    "civil_war": {
        "conditions": ("Convene the rival courts in {label}", "Recognize one claimant in {label} at once"),
        "pressure": ("Broker offices and guarantees during {label}", "Secure the armies' acclamation during {label}"),
        "contest": ("Finance a constitutional compact for {label}", "Commit the palace reserve to {label}"),
        "closing": ("Bind the victors of {label} to a public settlement", "Let the victorious court settle {label}"),
    },
    "migration": {
        "conditions": ("Survey land and routes for {label}", "Close the principal crossings used in {label}"),
        "pressure": ("Issue grain and travel provisions for {label}", "Channel {label} through guarded corridors"),
        "contest": ("Negotiate service and settlement obligations in {label}", "Mobilize to contain {label}"),
        "closing": ("Register the communities shaped by {label}", "Leave settlement after {label} to frontier patrons"),
    },
    "belief": {
        "conditions": ("Protect inquiry surrounding {label}", "Require a court formula for {label}"),
        "pressure": ("Endow debate and teaching during {label}", "Bind patronage in {label} to one party"),
        "contest": ("Hear the competing communities of {label}", "Call the court to decide {label}"),
        "closing": ("Publish a bounded settlement for {label}", "Leave enforcement of {label} to local sanctuaries"),
    },
    "exchange": {
        "conditions": ("Receive the travelers of {label}", "Confine the knowledge of {label} to the court"),
        "pressure": ("Fund interpreters and archives for {label}", "License selected brokers of {label}"),
        "contest": ("Open workshops and schools to {label}", "Reserve the practices of {label} for state use"),
        "closing": ("Disseminate the record of {label}", "Let regional patrons carry the exchange of {label}"),
    },
    "diplomacy": {
        "conditions": ("Exchange envoys and hostages for {label}", "Issue a binding claim in {label} before talks"),
        "pressure": ("Subsidize a durable settlement for {label}", "Back the ultimatum in {label} with an army"),
        "contest": ("Convene every principal in {label}", "Recognize the strongest claimant in {label}"),
        "closing": ("Guarantee the final compact of {label}", "Accept a narrower settlement for {label}"),
    },
    "statecraft": {
        "conditions": ("Commission records for {label}", "Announce the order of {label} by decree"),
        "pressure": ("Negotiate offices and obligations in {label}", "Dispatch inspectors to enforce {label}"),
        "contest": ("Fund the institutions required by {label}", "Concentrate appointments for {label} at court"),
        "closing": ("Publish the reviewed settlement of {label}", "Permit regional adaptation after {label}"),
    },
    "crisis": {
        "conditions": ("Commission a full account of {label}", "Empower emergency magistrates for {label}"),
        "pressure": ("Fund relief and protected supply during {label}", "Ration stores under guard during {label}"),
        "contest": ("Coordinate local recovery councils for {label}", "Concentrate all reserves against {label}"),
        "closing": ("Endow reconstruction after {label}", "Return recovery from {label} to provincial authorities"),
    },
}
MODULES = (
    "m10_history",
    "m10_second_century",
    "m10_third_century",
    "m10_fourth_century",
    "m10_final_century",
)
# `dynamic_historical_event` validates its tag while the database loads, not
# at the future date. These two later-forming recipients therefore use their
# closest AD 1 current anchor for the optional phase notice. The primary M10
# situation/event remains responsible for the historical formation itself.
FUTURE_RECIPIENT_ANCHORS = {"HNS": "XIO", "ERO": "XAA", "VND": "XAA"}


@dataclass(frozen=True)
class PhaseEvent:
    key: str
    phase: str
    phase_label: str
    date: AntqDate
    close_date: AntqDate
    region: str
    summary: str
    source: str
    label: str
    engine_tag: str
    trigger_tag: str
    image: str
    event_id: int
    theme: str

    @property
    def event_key(self) -> str:
        return f"antq_m11_flavor.{self.event_id}"


def timeline_rows() -> dict[str, dict[str, str]]:
    result = {
        row["key"].strip(): row
        for row in load_timeline(TIMELINE)
        if row["rails_strength"].strip() != "system"
    }
    if len(result) < 84:
        raise ValueError(f"historical-current ledger regressed below 84 records: {len(result)}")
    return result


def m10_currents() -> tuple[tuple[object, str], ...]:
    records: list[tuple[object, str]] = []
    for module_name in MODULES:
        module = importlib.import_module(module_name)
        module_records = tuple(module.currents())
        images = module.EVENT_IMAGES
        keys = {record.key for record in module_records}
        if set(images) != keys:
            raise ValueError(f"{module_name} does not map every current to reviewed event art")
        records.extend((record, images[record.key]) for record in module_records)
    expected_keys = set(timeline_rows())
    actual_keys = {record.key for record, _ in records}
    if actual_keys != expected_keys or len(actual_keys) != len(records):
        raise ValueError(
            f"M10 current inventory/ledger mismatch: "
            f"missing={sorted(expected_keys - actual_keys)}, extra={sorted(actual_keys - expected_keys)}"
        )
    return tuple(sorted(records, key=lambda item: (item[0].date, item[0].key)))


def phase_dates(start: AntqDate, end: AntqDate) -> tuple[tuple[AntqDate, AntqDate], ...]:
    span = days_between(start, end)
    result: list[tuple[AntqDate, AntqDate]] = []
    for numerator in range(1, len(PHASES) + 1):
        phase_start = offset_date(start, (span * numerator) // (len(PHASES) + 1))
        phase_end = min(offset_date(phase_start, WINDOW_DAYS), end)
        if not start < phase_start < phase_end <= end:
            raise ValueError(f"invalid derived flavor-event window: {start} to {end}")
        result.append((phase_start, phase_end))
    if len({date for date, _ in result}) != len(result):
        raise ValueError(f"derived duplicate flavor-event dates for {start} to {end}")
    return tuple(result)


def current_theme(current: object, row: dict[str, str]) -> str:
    """Classify a sourced current into a reviewed gameplay mechanic family."""
    if current.kind == "disaster":
        return "crisis"
    situation_theme = SITUATION_THEMES.get(getattr(current, "script_key", ""))
    if situation_theme:
        return "campaign" if situation_theme == "frontier" else situation_theme
    haystack = " ".join(
        (current.key, row["label"], row["summary"], row["region"])
    ).lower()
    for theme, keywords in THEME_KEYWORDS:
        if any(keyword in haystack for keyword in keywords):
            return theme
    return "statecraft"


def records() -> tuple[PhaseEvent, ...]:
    rows = timeline_rows()
    result: list[PhaseEvent] = []
    for current, image in m10_currents():
        row = rows.get(current.key)
        if row is None:
            raise ValueError(f"M10 current {current.key} is missing from the chronology ledger")
        if not row["end_date"].strip():
            # The terminal 4 September 476 finale has no post-end campaign
            # window. Its primary M10 event remains the only correct event.
            if current.key != "odoacer_finale" or current.date.engine() != "476.9.4":
                raise ValueError(f"only the terminal finale may omit an end date: {current.key}")
            continue
        if AntqDate.parse(row["date"]) != current.date or AntqDate.parse(row["end_date"]) != current.end_date:
            raise ValueError(f"M10 current {current.key} no longer matches dates.py timeline data")
        for (phase, phase_label), (start, end) in zip(PHASES, phase_dates(current.date, current.end_date)):
            trigger_tag = FUTURE_RECIPIENT_ANCHORS.get(current.engine_tag, current.engine_tag)
            result.append(PhaseEvent(
                key=current.key,
                phase=phase,
                phase_label=phase_label,
                date=start,
                close_date=end,
                region=row["region"].strip(),
                summary=row["summary"].strip(),
                source=row["source"].strip(),
                label=row["label"].strip(),
                engine_tag=current.engine_tag,
                trigger_tag=trigger_tag,
                image=image,
                event_id=6000 + len(result),
                theme=current_theme(current, row),
            ))
    return tuple(result)


def source_event_count() -> int:
    count = 0
    pattern = re.compile(r"(?m)^antq_m10(?:_[a-z]+)?\.\d+\s*=\s*\{")
    for path in M10_EVENT_FILES:
        count += len(pattern.findall(path.read_text(encoding="utf-8-sig")))
    return count


def start_tags() -> frozenset[str]:
    text = START_COUNTRIES.read_text(encoding="utf-8-sig")
    return frozenset(re.findall(r"(?m)^([A-Z0-9]{3})\s*=\s*\{", text))


def branch_variable(item: PhaseEvent, branch: str) -> str:
    return f"antq_m11_{item.key}_{branch}_path"


def primary_path_variable(item: PhaseEvent, branch: str) -> str:
    return f"antq_m10_{item.key}_{branch}_path"


def branch_initialization_lines(
    item: PhaseEvent, *, indent: str = "\t\t"
) -> tuple[str, ...]:
    """Initialize both persistent counters before any ``var:`` comparison."""
    directed = branch_variable(item, "directed")
    delegated = branch_variable(item, "delegated")
    return (
        f"{indent}if = {{",
        f"{indent}\tlimit = {{ NOT = {{ has_variable = {directed} }} }}",
        f"{indent}\tset_variable = {{ name = {directed} value = 0 }}",
        f"{indent}}}",
        f"{indent}if = {{",
        f"{indent}\tlimit = {{ NOT = {{ has_variable = {delegated} }} }}",
        f"{indent}\tset_variable = {{ name = {delegated} value = 0 }}",
        f"{indent}}}",
    )


def branch_seed_lines(item: PhaseEvent) -> tuple[str, ...]:
    """Carry the primary decision forward and make both counters readable.

    Clausewitz reports a script error when ``var:name`` is compared before the
    variable exists.  Every continuation choice compares both branch counters,
    including the counter for the choice the player did not take.  Seed a
    historical branch when one exists, then explicitly initialize either
    missing counter to zero before the event options can be evaluated.
    """
    directed = branch_variable(item, "directed")
    delegated = branch_variable(item, "delegated")
    return (
        "\timmediate = {",
        "\t\tif = {",
        f"\t\t\tlimit = {{ NOT = {{ has_variable = {directed} }} NOT = {{ has_variable = {delegated} }} }}",
        "\t\t\tif = {",
        "\t\t\t\tlimit = {",
        "\t\t\t\t\tOR = {",
        f"\t\t\t\t\t\thas_variable = {primary_path_variable(item, 'chronicle')}",
        f"\t\t\t\t\t\thas_variable = {primary_path_variable(item, 'command')}",
        "\t\t\t\t\t}",
        "\t\t\t\t}",
        f"\t\t\t\tset_variable = {{ name = {directed} value = 1 }}",
        "\t\t\t}",
        "\t\t\telse_if = {",
        f"\t\t\t\tlimit = {{ has_variable = {primary_path_variable(item, 'compact')} }}",
        f"\t\t\t\tset_variable = {{ name = {delegated} value = 1 }}",
        "\t\t\t}",
        "\t\t}",
        *branch_initialization_lines(item),
        "\t}",
    )


def branch_effects(item: PhaseEvent, *, directed: bool) -> tuple[str, ...]:
    """Return thematic costs and payoffs for one persistent phase branch."""
    phase = item.phase
    cost = PHASE_COSTS[phase]
    strong = "mild" if phase in {"contest", "closing"} else "weak"
    override = CURRENT_EFFECTS.get(item.key)
    if override:
        themed = list(override["directed" if directed else "delegated"])
        common: list[str] = []
    elif directed:
        common = [f"\t\tadd_gold = -{cost}"]
        themed = {
            "campaign": [
                "\t\tadd_manpower = { value = monthly_manpower multiply = -0.75 }",
                f"\t\tadd_army_tradition = army_tradition_{strong}_bonus",
            ],
            "rebellion": [
                f"\t\tadd_stability = stability_{strong}_bonus",
                "\t\tadd_prestige = prestige_weak_penalty",
            ],
            "civil_war": [
                f"\t\tadd_legitimacy = legitimacy_{strong}_bonus",
                "\t\tadd_stability = stability_weak_bonus",
            ],
            "migration": [
                f"\t\tadd_stability = stability_{strong}_bonus",
                "\t\tadd_manpower = { value = monthly_manpower multiply = -0.25 }",
            ],
            "belief": [
                "\t\tadd_religious_influence_if_valid = { VALUE = religious_influence_weak_bonus }",
                "\t\tadd_stability = stability_weak_penalty",
            ],
            "exchange": [
                f"\t\tadd_research_progress = research_progress_{strong}_bonus",
                "\t\tadd_prestige = prestige_weak_bonus",
            ],
            "diplomacy": [
                f"\t\tadd_legitimacy = legitimacy_{strong}_bonus",
                "\t\tadd_stability = stability_weak_bonus",
            ],
            "statecraft": [
                f"\t\tadd_research_progress = research_progress_{strong}_bonus",
                "\t\tadd_stability = stability_weak_bonus",
            ],
            "crisis": [
                f"\t\tadd_stability = stability_{strong}_bonus",
                "\t\tadd_manpower = { value = monthly_manpower multiply = -0.5 }",
            ],
        }[item.theme]
    else:
        common = [f"\t\tadd_gold = -{max(2, cost // 2)}"]
        themed = {
            "campaign": [
                "\t\tadd_war_exhaustion = war_exhaustion_weak_bonus",
                "\t\tadd_prestige = prestige_weak_bonus",
            ],
            "rebellion": [
                "\t\tadd_manpower = { value = monthly_manpower multiply = -0.5 }",
                "\t\tadd_stability = stability_weak_penalty",
                "\t\tadd_army_tradition = army_tradition_weak_bonus",
            ],
            "civil_war": [
                "\t\tadd_manpower = { value = monthly_manpower multiply = -0.75 }",
                "\t\tadd_stability = stability_weak_penalty",
                "\t\tadd_prestige = prestige_weak_bonus",
            ],
            "migration": [
                "\t\tadd_manpower = { value = monthly_manpower multiply = -0.5 }",
                "\t\tadd_prestige = prestige_weak_penalty",
            ],
            "belief": [
                f"\t\tadd_legitimacy = legitimacy_{strong}_bonus",
                "\t\tadd_religious_influence_if_valid = { VALUE = religious_influence_weak_penalty }",
            ],
            "exchange": [
                f"\t\tadd_legitimacy = legitimacy_{strong}_bonus",
                "\t\tadd_prestige = prestige_weak_penalty",
            ],
            "diplomacy": [
                "\t\tadd_manpower = { value = monthly_manpower multiply = -0.5 }",
                "\t\tadd_prestige = prestige_weak_bonus",
                "\t\tadd_stability = stability_weak_penalty",
            ],
            "statecraft": [
                f"\t\tadd_legitimacy = legitimacy_{strong}_bonus",
                "\t\tadd_stability = stability_weak_penalty",
            ],
            "crisis": [
                "\t\tadd_manpower = { value = monthly_manpower multiply = -0.75 }",
                f"\t\tadd_legitimacy = legitimacy_{strong}_bonus",
                "\t\tadd_prestige = prestige_weak_penalty",
            ],
        }[item.theme]
    branch = "directed" if directed else "delegated"
    opposite = "delegated" if directed else "directed"
    lines = [
        *common,
        *themed,
        "\t\tif = {",
        f"\t\t\tlimit = {{ NOT = {{ has_variable = {branch_variable(item, branch)} }} }}",
        f"\t\t\tset_variable = {{ name = {branch_variable(item, branch)} value = 0 }}",
        "\t\t}",
        f"\t\tchange_variable = {{ name = {branch_variable(item, branch)} add = 1 }}",
    ]
    if phase != "conditions":
        lines.extend((
            "\t\tif = {",
            # The engine evaluates option limits before an event's immediate block
            # on some UI/AI paths.  A direct var: comparison on an absent counter
            # therefore logs a script error even though the immediate block later
            # seeds it.  Guard every read; this also makes a saved/in-flight event
            # safe if its originating phase has been removed or superseded.
            f"\t\t\tlimit = {{ has_variable = {branch_variable(item, branch)} var:{branch_variable(item, branch)} >= 2 }}",
            "\t\t\tadd_prestige = prestige_weak_bonus",
            "\t\t}",
            "\t\tif = {",
            f"\t\t\tlimit = {{ has_variable = {branch_variable(item, opposite)} var:{branch_variable(item, opposite)} >= 2 }}",
            "\t\t\tadd_stability = stability_weak_penalty",
            "\t\t}",
        ))
    if phase == "closing":
        lines.extend((
            f"\t\tremove_variable = {branch_variable(item, 'directed')}",
            f"\t\tremove_variable = {branch_variable(item, 'delegated')}",
            f"\t\tif = {{ limit = {{ has_variable = {primary_path_variable(item, 'chronicle')} }} remove_variable = {primary_path_variable(item, 'chronicle')} }}",
            f"\t\tif = {{ limit = {{ has_variable = {primary_path_variable(item, 'compact')} }} remove_variable = {primary_path_variable(item, 'compact')} }}",
            f"\t\tif = {{ limit = {{ has_variable = {primary_path_variable(item, 'command')} }} remove_variable = {primary_path_variable(item, 'command')} }}",
        ))
    return tuple(lines)


def ai_chance_lines(item: PhaseEvent, *, directed: bool) -> tuple[str, ...]:
    cost = PHASE_COSTS[item.phase]
    if directed:
        return (
            "\t\tai_chance = {",
            "\t\t\tbase = 58",
            f"\t\t\tmodifier = {{ factor = 0.3 gold < {cost * 2} }}",
            "\t\t\tmodifier = { factor = 1.25 stability < 0 }",
            "\t\t}",
        )
    return (
        "\t\tai_chance = {",
        "\t\t\tbase = 42",
        f"\t\t\tmodifier = {{ factor = 1.7 gold < {cost * 2} }}",
        "\t\t\tmodifier = { factor = 1.2 at_war = yes }",
        "\t\t}",
    )


def event_script(items: tuple[PhaseEvent, ...]) -> str:
    lines = [
        "# Generated by tools/m11_flavor_events.py --write; consequential current phases.",
        "# Dates are derived only through tools/dates.py from docs/timeline.csv windows.",
        "namespace = antq_m11_flavor",
        "",
    ]
    for item in items:
        lines.extend((
            f"# {item.label} — {item.phase_label}; {item.source}; recipient={item.engine_tag}; trigger={item.trigger_tag}",
            f"{item.event_key} = {{",
            "\ttype = country_event",
            f"\ttitle = {item.event_key}.title",
            f"\tdesc = {item.event_key}.desc",
            "\toutcome = neutral",
            "\tfire_only_once = yes",
            f'\timage = "{item.image}"',
            "\tdynamic_historical_event = {",
            f"\t\ttag = {item.trigger_tag}",
            f"\t\tfrom = {item.date.engine()}",
            f"\t\tto = {item.close_date.engine()}",
            "\t\tmonthly_chance = 100",
            "\t}",
        ))
        if item.key == "teutoburg":
            if item.phase == "closing":
                trigger_lines = (
                    "\ttrigger = {",
                    "\t\thas_variable = antq_teutoburg_battle_resolved",
                    "\t\tNOT = { has_variable = antq_teutoburg_aftermath_seen }",
                    "\t}",
                    "\timmediate = {",
                    "\t\tset_variable = antq_teutoburg_aftermath_seen",
                    *branch_initialization_lines(item),
                    "\t}",
                )
            else:
                trigger_lines = (
                    "\ttrigger = {",
                    "\t\tantq_teutoburg_campaign_ready_trigger = yes",
                    "\t\tNOT = { has_variable = antq_teutoburg_battle_resolved }",
                    "\t}",
                    "\timmediate = {",
                    "\t\tset_variable = antq_teutoburg_chain_active",
                    *teutoburg_opponent_capture_lines(indent="\t\t"),
                    *branch_initialization_lines(item),
                    "\t}",
                )
            lines.extend(trigger_lines)
        else:
            lines.extend(branch_seed_lines(item))
        lines.extend((
            "\toption = {",
            f"\t\tname = {item.event_key}.a",
            *ai_chance_lines(item, directed=True),
            *branch_effects(item, directed=True),
            "\t}",
            "\toption = {",
            f"\t\tname = {item.event_key}.b",
            *ai_chance_lines(item, directed=False),
            *branch_effects(item, directed=False),
            "\t}",
            "}",
            "",
        ))
    return "\n".join(lines)


def localization(items: tuple[PhaseEvent, ...], language: str) -> str:
    lines = [f"l_{language}:"]
    for item in items:
        if item.key == "teutoburg":
            titles = {
                "conditions": "Varus and the Germanic Campaign",
                "pressure": "Strain Along the Northern Roads",
                "contest": "The Forest Corridors Narrow",
                "closing": "After the Varian Disaster",
            }
            descriptions = {
                "conditions": "Varus remains alive in Roman service, and a real war against a Germanic frontier polity has drawn the northern command beyond routine policing. Scouts, roads, and auxiliary loyalties now matter.",
                "pressure": "The campaign is active rather than ceremonial: dispersed columns, uncertain supply routes, and contested local alliances are placing the Roman field command under pressure.",
                "contest": "With Roman and Germanic forces committed to the same frontier war, the wooded corridors can become a battlefield. The result is not predetermined, but delay now carries military risk.",
                "closing": "A qualifying frontier campaign has culminated in the Varian disaster. Rome must absorb the losses and decide how the Rhine and the forward districts are to be governed afterward.",
            }
            title = titles[item.phase]
            description = descriptions[item.phase]
        else:
            title = f"{item.label}: {item.phase_label}"
            description = (
                f"{item.summary} remains a documented historical current in {item.region}. "
                "Earlier choices in this chain shape the cost of changing course; "
                "consistent direction earns political confidence, while reversal creates strain."
            )
        directed_text, delegated_text = (
            text.format(label=item.label)
            for text in CHOICE_TEXT[item.theme][item.phase]
        )
        lines.extend((
            f' {item.event_key}.title: "{title}"',
            f' {item.event_key}.desc: "{description}"',
            f' {item.event_key}.a: "{directed_text}."',
            f' {item.event_key}.b: "{delegated_text}."',
            f' {item.event_key}.entry: "{title}"',
            f' {item.event_key}.entry_short: "{title}"',
        ))
    return "\n".join(lines) + "\n"


def outputs(items: tuple[PhaseEvent, ...]) -> dict[Path, str]:
    rendered = {EVENT_OUTPUT: event_script(items)}
    for language in ("english", *M2_MIRROR_LANGUAGES):
        rendered[LOC_ROOT / language / f"antq_m11_flavor_phases_l_{language}.yml"] = localization(items, language)
    return rendered


def validate(items: tuple[PhaseEvent, ...]) -> None:
    # The terminal 4 September 476 finale has no post-end window and therefore
    # correctly remains an M10-only event. Every other historical current gets
    # the complete review-phase set.
    expected = sum(
        bool(row["end_date"].strip()) for row in timeline_rows().values()
    ) * len(PHASES)
    if len(items) != expected:
        raise ValueError(f"expected {expected} M11 phase events, found {len(items)}")
    if len({item.event_id for item in items}) != len(items):
        raise ValueError("M11 flavor-event IDs must be unique")
    if len({(item.key, item.phase) for item in items}) != len(items):
        raise ValueError("M11 current phases must be unique")
    covered_keys = {item.key for item in items if item.date.year <= 200}
    missing = sorted(covered_keys - set(CURRENT_EFFECTS))
    extra = sorted(set(CURRENT_EFFECTS) - covered_keys)
    if missing or extra:
        raise ValueError(f"early-current effect coverage mismatch missing={missing} extra={extra}")
    package_failures = packages_are_unique()
    if package_failures:
        raise ValueError("; ".join(package_failures))
    known_start_tags = start_tags()
    for item in items:
        if not item.region or not item.summary or not item.source or not item.image:
            raise ValueError(f"M11 flavor event lacks sourced context: {item.key}/{item.phase}")
        if not (ROOT / "main_menu" / item.image).is_file():
            raise ValueError(f"M11 flavor event art is missing: {item.image}")
        if not item.date < item.close_date:
            raise ValueError(f"M11 flavor event has invalid date window: {item.event_key}")
        if item.trigger_tag not in known_start_tags:
            raise ValueError(
                f"M11 flavor event uses a dynamic-historical tag absent at AD 1: "
                f"{item.event_key} -> {item.trigger_tag}"
            )
    rendered = event_script(items)
    validate_ai_chance_syntax(rendered, source=str(EVENT_OUTPUT.relative_to(ROOT)))
    if "add_cultural_influence" in rendered:
        raise ValueError("country-scoped phase event contains culture-scoped add_cultural_influence")
    if rendered.count("\toption = {") != len(items) * 2:
        raise ValueError("every phase event must have two player choices")
    if rendered.count("\t\tchange_variable = { name = antq_m11_") != len(items) * 2:
        raise ValueError("phase choices lost their persistent branch state")
    if rendered.count("gold < ") != len(items) * 2:
        raise ValueError("phase AI weights lost their treasury-aware conditions")
    continuations = sum(item.phase != "conditions" for item in items)
    guarded_var_limits = re.findall(
        # Tags and geography-derived current keys may include non-ASCII letters
        # (for example ``aksum_meroë``), so match a script token rather than a
        # restrictive ASCII identifier here.
        r"\t\t\tlimit = \{ has_variable = (antq_m11_\S+) "
        r"var:\1 >= 2 \}",
        rendered,
    )
    if len(guarded_var_limits) != continuations * 4:
        raise ValueError("later phases lost branch-consistency and reversal consequences")
    if re.search(r"\t\t\tlimit = \{ var:antq_m11_", rendered):
        raise ValueError("unguarded M11 branch counter comparison can log at runtime")
    # Check the rendered event contract, including Teutoburg's custom immediate
    # blocks: every phase must create both counters before its first option and
    # any var: comparison can execute.
    for item in items:
        marker = f"\n{item.event_key} = {{\n"
        if marker not in rendered:
            raise ValueError(f"rendered phase event is missing: {item.event_key}")
        before_options = rendered.split(marker, 1)[1].split("\n\toption = {\n", 1)[0]
        for branch in ("directed", "delegated"):
            expected_line = (
                f"\t\t\tset_variable = {{ name = {branch_variable(item, branch)} "
                "value = 0 }"
            )
            if expected_line not in before_options:
                raise ValueError(
                    f"phase branch counter lacks safe initialization: "
                    f"{item.event_key}/{branch}"
                )
    english = localization(items, "english")
    if (
        "Commit resources to shape the response" in english
        or "Accept the immediate political strain" in english
    ):
        raise ValueError("generic phase-choice prose survived the authored pass")
    choice_values = [
        match.group(1)
        for line in english.splitlines()
        if (match := re.match(
            r'\s*antq_m11_flavor\.\d+\.[ab]:\s*"([^"]+)"', line
        ))
    ]
    if len(choice_values) != len(items) * 2 or len(set(choice_values)) != len(choice_values):
        raise ValueError("phase choice localization is missing or cloned")
    represented_themes = {item.theme for item in items}
    if represented_themes != set(CHOICE_TEXT):
        raise ValueError(
            f"phase mechanic-family coverage changed: {sorted(represented_themes)}"
        )
    for item in items:
        for directed in (True, False):
            effects = branch_effects(item, directed=directed)
            if len(effects) < 4 or not any("add_gold" in line for line in effects):
                raise ValueError(f"thin phase branch: {item.event_key}/{directed}")
    primary_script = "\n".join(
        path.read_text(encoding="utf-8-sig") for path in M10_EVENT_FILES
    )
    validate_ai_chance_syntax(primary_script, source="generated M10 event batches")
    primary_choices: list[str] = []
    for path in sorted((LOC_ROOT / "english").glob("antq_m10*_l_english.yml")):
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            match = re.match(
                r'\s*antq_m10(?:_[a-z]+)?\.\d+\.[abc]:\s*"([^"]+)"',
                line,
            )
            if match:
                primary_choices.append(match.group(1))
    expected_primary_choices = source_event_count() * 3
    if (
        len(primary_choices) != expected_primary_choices
        or len(set(primary_choices)) != len(primary_choices)
    ):
        raise ValueError("primary historical-current choices are missing or cloned")
    for current, _ in m10_currents():
        if current.key == "odoacer_finale":
            continue
        for branch in ("chronicle", "compact", "command"):
            variable = event_path_variable(current, branch)
            if f"set_variable = {variable}" not in primary_script:
                raise ValueError(f"primary current lost persistent branch: {variable}")
    if source_event_count() + len(items) < TARGET_TOTAL:
        raise ValueError(
            f"M11 flavor pass misses the section 18 event target: "
            f"{source_event_count()} M10 + {len(items)} M11 < {TARGET_TOTAL}"
        )


def write(rendered: dict[Path, str]) -> None:
    for path, content in rendered.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8-sig")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="render M11 flavor phase events")
    parser.add_argument("--check", action="store_true", help="check rendered M11 flavor phase events")
    args = parser.parse_args()
    if not args.write and not args.check:
        parser.error("one of --write or --check is required")
    items = records()
    validate(items)
    rendered = outputs(items)
    if args.write:
        write(rendered)
    if args.check:
        stale = [str(path) for path, content in rendered.items() if not path.is_file() or path.read_text(encoding="utf-8-sig") != content]
        if stale:
            raise ValueError(f"M11 flavor outputs are stale: {stale}")
    print(
        f"m11_flavor_events: PASS ({len(items)} consequential phase events; "
        f"{source_event_count() + len(items)} total section 18 events)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
