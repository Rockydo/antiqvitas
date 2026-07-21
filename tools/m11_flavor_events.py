#!/usr/bin/env python3
"""Render source-preserving M11 phase events for the complete M10 chronology.

The master plan calls for at least 400 events but only about 80 shared event
illustrations.  Each existing M10 historical current therefore receives four
additional, date-windowed review events that reuse its reviewed painting.  The
events carry no mechanical effect: they report a documented current without
forcing a historical outcome in a sandbox campaign.
"""

from __future__ import annotations

import argparse
import importlib
import re
from dataclasses import dataclass
from pathlib import Path

from dates import AntqDate, M2_MIRROR_LANGUAGES, days_between, load_timeline, offset_date


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

    @property
    def event_key(self) -> str:
        return f"antq_m11_flavor.{self.event_id}"


def timeline_rows() -> dict[str, dict[str, str]]:
    result = {
        row["key"].strip(): row
        for row in load_timeline(TIMELINE)
        if row["rails_strength"].strip() != "system"
    }
    if len(result) != 84:
        raise ValueError(f"expected 84 non-system historical currents, found {len(result)}")
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
    if len(records) != 84 or len({record.key for record, _ in records}) != len(records):
        raise ValueError("M10 current inventory must contain 84 unique records")
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


def event_script(items: tuple[PhaseEvent, ...]) -> str:
    lines = [
        "# Generated by tools/m11_flavor_events.py --write; M11 source-preserving current phases.",
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
            "\toption = {",
            f"\t\tname = {item.event_key}.a",
            "\t}",
            "}",
            "",
        ))
    return "\n".join(lines)


def localization(items: tuple[PhaseEvent, ...], language: str) -> str:
    lines = [f"l_{language}:"]
    for item in items:
        title = f"{item.label}: {item.phase_label}"
        description = (
            f"{item.summary} remains a documented historical current in {item.region}. "
            "This review marks a point in its sourced time window without predetermining the campaign's outcome."
        )
        lines.extend((
            f' {item.event_key}.title: "{title}"',
            f' {item.event_key}.desc: "{description}"',
            f' {item.event_key}.a: "Respond to the changing circumstances."',
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
    expected = 83 * len(PHASES)
    if len(items) != expected:
        raise ValueError(f"expected {expected} M11 phase events, found {len(items)}")
    if len({item.event_id for item in items}) != len(items):
        raise ValueError("M11 flavor-event IDs must be unique")
    if len({(item.key, item.phase) for item in items}) != len(items):
        raise ValueError("M11 current phases must be unique")
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
        f"m11_flavor_events: PASS ({len(items)} phase events; "
        f"{source_event_count() + len(items)} total section 18 events)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
