#!/usr/bin/env python3
"""Keep installed vanilla event graphs loader-valid but permanently inert.

EU5 validates event references, scope types, variables, and effect links across
its generic systems. Retain that compile-time graph behind an impossible date
gate, while redirecting removed medieval country tags to the reserved DUMMY
sentinel. No inherited event can become eligible during AD 1--476.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from dates import AntqDate, END, START
from dead_script_links import sanitize_dead_links, validate_inventory
from legacy_institutions import neutralize_references


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
EVENT_ROOT = Path("in_game/events")
PILOT = "in_game/events/random_event.txt"
EVENT_HEADER = re.compile(r"^([A-Za-z][A-Za-z0-9_]*\.[0-9]+)\s*=\s*\{")
_PROVEN_ORPHANED_INSTALLED_EVENTS = frozenset({
    "catholic_flavor.1000",
    "catholic_flavor.1001",
    "catholic_flavor.1002",
    "colonial_revolution.1000",
    "colonial_revolution.1001",
    "colonial_revolution.1002",
    "coup_attempt.4",
    "coup_attempt.6",
    "coup_attempt.9",
    "coup_attempt.7",
    "court_and_country.3",
    "court_and_country.4",
    "court_and_country.5",
    "court_and_country.6",
    "crisis_of_the_chinese_dynasty.6",
    "crisis_of_the_chinese_dynasty.8",
    "crisis_of_the_chinese_dynasty.9",
    "d008_orthodox_events.1",
    "d008_orthodox_events.2",
    "d008_orthodox_events.3",
    "d008_orthodox_events.4",
    "d008_orthodox_events.5",
    "d008_orthodox_events.6",
    "d008_orthodox_events.10",
    "d008_orthodox_events.11",
    "d008_orthodox_events.12",
    "d008_orthodox_events.13",
    "d008_orthodox_events.14",
    "decline_of_empire.7",
    "decline_of_empire.8",
    "fate_of_the_phoenix.8",
    "fate_of_the_phoenix.16",
    "fate_of_the_phoenix.17",
    "fate_of_the_phoenix.18",
    "fate_of_the_phoenix.19",
    "fate_of_the_phoenix.20",
    "flavor_bos.4",
    "flavor_chi.2002",
    "flavor_chi.2021",
    "flavor_glh.1000",
    "flavor_mam.17",
    "flavor_pap.9",
    "french_wars_religion.10",
    "golden_age_of_piracy.100",
    "golden_age_of_piracy.110",
    "golden_age_of_piracy.101",
    "golden_age_of_piracy.102",
    "government_conversion_events.10",
    "guelphs_and_ghibellines.1000",
    "guelphs_and_ghibellines.1100",
    "guelphs_and_ghibellines.1001",
    "guelphs_and_ghibellines.1002",
    "guelphs_and_ghibellines.1101",
    "guelphs_and_ghibellines.1102",
    "guelphs_and_ghibellines.1103",
    "hundred_years_war.206",
    "hundred_years_war.207",
    "hundred_years_war.208",
    "hundred_years_war.209",
    "hundred_years_war.210",
    "hundred_years_war.212",
    "hundred_years_war.213",
    "hundred_years_war.214",
    "hundred_years_war.215",
    "hundred_years_war.216",
    "hundred_years_war.217",
    "hundred_years_war.218",
    "hundred_years_war.230",
    "hundred_years_war.240",
    "imperial_circles.20",
    "imperial_examination_events.1",
    "imperial_examination_events.2",
    "imperial_examination_events.3",
    "imperial_examination_events.4",
    "imperial_examination_events.5",
    "imperial_examination_events.6",
    "italian_wars.4",
    "italian_wars.10",
    "italian_wars.9",
    "nahuatl_events.310",
    "orthodox_flavor.100",
    "orthodox_flavor.101",
    "orthodox_flavor.6",
    "orthodox_flavor.7",
    "orthodox_flavor.8",
    "orthodox_flavor.9",
    "orthodox_flavor.10",
    "reformation.17",
    "reformation.18",
    "reformation.19",
    "reformation.20",
    "reformation.21",
    "rise_of_the_ottomans.100",
    "rise_of_the_ottomans.106",
    "rise_of_the_ottomans.107",
    "rise_of_the_ottomans.108",
    "rise_of_the_ottomans.110",
    "rise_of_the_ottomans.111",
    "rise_of_the_ottomans.112",
    "rise_of_the_ottomans.113",
    "rise_of_the_ottomans.216",
    "rise_of_the_ottomans.217",
    "sengoku.6",
    "sengoku.7",
    "sengoku.8",
    "sengoku.9",
    "sengoku.10",
    "sengoku.11",
    "sengoku.12",
    "sengoku.13",
    "sengoku.14",
    "sengoku.15",
    "sengoku.16",
    "sengoku.17",
    "sengoku.18",
    "sengoku.19",
    "sengoku.20",
    "sengoku.21",
    "sengoku.22",
    "succession_crisis.6",
    "succession_crisis.7",
    "succession_crisis.8",
    "succession_crisis.9",
    "succession_crisis.10",
    "succession_crisis.11",
    "the_revolution.2",
    "the_revolution.3",
    "the_revolution.11",
    "treaty_of_tordesillas.6",
    "treaty_of_tordesillas.7",
    "war_of_the_roses.17",
    "western_schism.1001",
    "western_schism.1002",
})
RUNTIME_ORPHAN_MANIFEST = ROOT / "config/runtime_orphaned_events_eu5_1_3_11.txt"


def runtime_orphan_manifest() -> frozenset[str]:
    """Load the engine-observed orphan inventory captured by this tool.

    Compacting inherited event bodies deliberately severs their medieval event
    chains. EU5's event manager is the authoritative linker for the remaining
    typed registry, including hardcoded entry points that a text-only scan
    cannot see. Keep its exact clean-start inventory as a versioned input.
    """
    # Bootstrap is permitted only so --capture-runtime-orphans can create the
    # versioned inventory. Normal write/check validation rejects an empty set.
    if not RUNTIME_ORPHAN_MANIFEST.is_file():
        return frozenset()
    values: list[str] = []
    for line_number, raw in enumerate(
        RUNTIME_ORPHAN_MANIFEST.read_text(encoding="utf-8-sig").splitlines(),
        start=1,
    ):
        value = raw.strip()
        if not value or value.startswith("#"):
            continue
        if EVENT_HEADER.fullmatch(value + " = {") is None:
            raise ValueError(
                f"runtime orphan manifest line {line_number} is not an event ID: {value}"
            )
        values.append(value)
    if not values or values != sorted(set(values)):
        raise ValueError("runtime orphan manifest must be nonempty, unique, and sorted")
    return frozenset(values)


ORPHANED_INSTALLED_EVENTS = _PROVEN_ORPHANED_INSTALLED_EVENTS
TRIGGER_BLOCK = re.compile(r"^(\s*)trigger\s*=\s*\{")
INLINE_TRIGGER = re.compile(r"^(\s*)trigger\s*=\s*\{\s*(.*?)\s*\}\s*(?:#.*)?$")
DATE = re.compile(r"(?<![0-9])-?[0-9]{1,4}\.[0-9]{1,2}\.[0-9]{1,2}(?![0-9])")
DAMAGE_REGIMENT = re.compile(
    r"^[ \t]*damage_regiment\s*=\s*yes[ \t]*(?:#.*)?\r?\n?",
    re.MULTILINE,
)
BLOCK_HEADER = {
    "center_of_renaissance_variable": re.compile(r"^\s*set_variable\s*=\s*\{"),
    "show_all_event_targets": re.compile(r"^\s*show_all_event_targets\s*=\s*\{"),
    "create_holy_site": re.compile(r"^\s*create_holy_site\s*=\s*\{"),
    "gag_left_hre_guelph_victory": re.compile(r"^\s*set_variable\s*=\s*\{"),
    "act_of_settlement": re.compile(r"^\s*set_variable\s*=\s*\{"),
    "make_into_expedition_leader": re.compile(
        r"^\s*scripted_effect\s+make_into_expedition_leader\s*=\s*\{"
    ),
}
TARGETED_SANITIZATIONS = {
    "in_game/events/DHE/flavor_BYZ.txt": ("center_of_renaissance_variable",),
    "in_game/events/debug/000_johan_debug.txt": ("show_all_event_targets",),
    "in_game/events/situations/guelphs_and_ghibellines.txt": (
        "gag_left_hre_guelph_victory",
    ),
    "in_game/events/DHE/flavor_ENG.txt": ("act_of_settlement",),
    "in_game/events/DHE/flavor_chi_treasure_expedition.txt": (
        "make_into_expedition_leader",
    ),
}


def game_root() -> Path:
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
        root = Path(config["game_dir"]) / "game"
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot resolve installed game root: {exc}") from exc
    if not root.is_dir():
        raise ValueError(f"installed game root is missing: {root}")
    return root


def source_text(relative: str) -> tuple[str, bool]:
    path = game_root() / relative
    if not path.is_file():
        raise ValueError(f"installed source is missing: {relative}")
    raw = path.read_bytes()
    return raw.decode("utf-8-sig"), raw.startswith(b"\xef\xbb\xbf")


def event_definition_count(text: str) -> int:
    return sum(EVENT_HEADER.match(line) is not None for line in text.splitlines())


def event_relatives() -> list[str]:
    """Return every installed event-definition file in stable override order.

    Only files that contain a top-level event definition are mirrored. The
    mod's authored antq_* event files intentionally have no same-name
    counterpart in this list, so this cannot overwrite project content.
    """
    source_root = game_root() / EVENT_ROOT
    if not source_root.is_dir():
        raise ValueError(f"installed event root is missing: {source_root}")
    relatives: list[str] = []
    for path in sorted(source_root.rglob("*.txt")):
        raw = path.read_bytes()
        text = raw.decode("utf-8-sig")
        if event_definition_count(text):
            relatives.append(path.relative_to(game_root()).as_posix())
    if not relatives:
        raise ValueError("installed event inventory contains no event definitions")
    return relatives


def target_relatives() -> list[str]:
    return event_relatives()


def validate_orphan_inventory(files: list[str], *, scan_mounted: bool) -> None:
    """Prove each omitted ID is unique upstream and unreferenced when mounted."""
    counts = {key: 0 for key in ORPHANED_INSTALLED_EVENTS}
    for relative in files:
        text, _bom = source_text(relative)
        for line in text.splitlines():
            header = EVENT_HEADER.match(line)
            if header is not None and header.group(1) in counts:
                counts[header.group(1)] += 1
    drift = sorted(key for key, count in counts.items() if count != 1)
    if drift:
        raise ValueError(
            "orphan-event source inventory drift: "
            + ", ".join(f"{key}={counts[key]}" for key in drift)
        )
    if not scan_mounted:
        return
    token = re.compile(
        r"(?<![A-Za-z0-9_.])(?:"
        + "|".join(re.escape(key) for key in sorted(
            ORPHANED_INSTALLED_EVENTS, key=len, reverse=True
        ))
        + r")(?![A-Za-z0-9_.])"
    )
    references: list[str] = []
    for path in sorted((ROOT / "in_game").rglob("*.txt")):
        text = path.read_text(encoding="utf-8-sig")
        for line_number, line in enumerate(text.splitlines(), start=1):
            # Comment-only documentation does not form an engine reference and
            # must not keep a dead event alive.
            matches = list(token.finditer(line.partition("#")[0]))
            if not matches:
                continue
            header = EVENT_HEADER.match(line)
            if header is not None and header.group(1) in ORPHANED_INSTALLED_EVENTS:
                continue
            references.append(
                f"{path.relative_to(ROOT).as_posix()}:{line_number}:"
                + ",".join(match.group(0) for match in matches)
            )
    if references:
        raise ValueError(
            "omitted orphan events regained mounted references: "
            + "; ".join(references[:10])
        )


def brace_delta(line: str) -> int:
    """Count structural braces, respecting quoted text and comments."""
    delta = 0
    quoted = False
    escaped = False
    for char in line:
        if escaped:
            escaped = False
            continue
        if quoted and char == "\\":
            escaped = True
            continue
        if char == '"':
            quoted = not quoted
            continue
        if not quoted and char == "#":
            break
        if not quoted and char == "{":
            delta += 1
        elif not quoted and char == "}":
            delta -= 1
    return delta


def omit_orphaned_event_definitions(text: str) -> tuple[str, int]:
    """Omit installed events proven to have no mounted inbound reference."""
    lines = text.splitlines(keepends=True)
    rendered: list[str] = []
    index = 0
    removed = 0
    while index < len(lines):
        header = EVENT_HEADER.match(lines[index])
        if header is None or header.group(1) not in ORPHANED_INSTALLED_EVENTS:
            rendered.append(lines[index])
            index += 1
            continue
        depth = brace_delta(lines[index])
        if depth <= 0:
            raise ValueError(f"{header.group(1)}: malformed orphan event header")
        index += 1
        while index < len(lines) and depth > 0:
            depth += brace_delta(lines[index])
            index += 1
        if depth != 0:
            raise ValueError(f"{header.group(1)}: unbalanced orphan event block")
        removed += 1
    return "".join(rendered), removed


def sanitized_date(match: re.Match[str]) -> str:
    value = match.group(0)
    if value.startswith("-"):
        return value
    year = int(value.split(".", 1)[0])
    if year > END[0]:
        return AntqDate(*END).engine()
    return value


def remove_blocks_containing(text: str, needle: str) -> tuple[str, int]:
    """Remove exact obsolete effect blocks while preserving all other source."""
    header = BLOCK_HEADER[needle]
    lines = text.splitlines(keepends=True)
    rendered: list[str] = []
    index = 0
    removed = 0
    while index < len(lines):
        if not header.match(lines[index]):
            rendered.append(lines[index])
            index += 1
            continue
        block: list[str] = []
        depth = 0
        while index < len(lines):
            line = lines[index]
            block.append(line)
            depth += brace_delta(line)
            index += 1
            if depth == 0:
                break
            if depth < 0:
                raise ValueError(f"{needle}: candidate block brace depth became negative")
        block_text = "".join(block)
        if needle in block_text:
            removed += 1
        else:
            rendered.extend(block)
    return "".join(rendered), removed


def render(relative: str) -> bytes:
    text, bom = source_text(relative)
    source_event_count = event_definition_count(text)
    text, omitted_orphans = omit_orphaned_event_definitions(text)
    validate_inventory()
    text, _dead_links = sanitize_dead_links(text, label=relative)
    expected_holy_site_calls = len(re.findall(r"(?m)^\s*create_holy_site\s*=\s*\{", text))
    if expected_holy_site_calls:
        text, count = remove_blocks_containing(text, "create_holy_site")
        if count != expected_holy_site_calls:
            raise ValueError(
                f"{relative}: expected {expected_holy_site_calls} inherited "
                f"create_holy_site blocks, removed {count}"
            )
    for needle in TARGETED_SANITIZATIONS.get(relative, ()):
        text, count = remove_blocks_containing(text, needle)
        if count != 1:
            raise ValueError(f"{relative}: expected one obsolete {needle} block, found {count}")
    if relative == "in_game/events/debug/000_johan_debug.txt":
        text, count = DAMAGE_REGIMENT.subn("", text)
        if count != 1:
            raise ValueError(f"{relative}: expected one obsolete damage_regiment effect, found {count}")
        text, count = re.subn(
            r"levy_setup:levy_a_late_longbowmen",
            "levy_setup:antq_levy_district_spear_muster",
            text,
        )
        if count != 1:
            raise ValueError(f"{relative}: expected one obsolete levy debug link, found {count}")
    lines = text.splitlines(keepends=True)
    rendered: list[str] = []
    depth = 0
    active_event: str | None = None
    saw_events = 0
    inerted_events = 0
    skip_depth: int | None = None

    for line in lines:
        header = EVENT_HEADER.match(line)
        delta = brace_delta(line)

        if skip_depth is not None:
            skip_depth += delta
            if skip_depth == 0:
                skip_depth = None
            elif skip_depth < 0:
                raise ValueError(f"{relative}: child block brace depth became negative")
            continue

        if active_event is None:
            if depth == 0 and header:
                active_event = header.group(1)
                saw_events += 1
            rendered.append(line)
            depth += delta
            continue

        # Direct children of an event are at brace depth one. Nested triggers
        # and effects remain untouched. The time guard is deliberately not a
        # compile-time false constant: EU5 retains the original event's
        # scheduler/reference graph, avoiding orphan and unused-variable
        # diagnostics while making it impossible during AD 1--476.
        child = TRIGGER_BLOCK.match(line) if depth == 1 else None
        if child:
            inline = INLINE_TRIGGER.match(line) if delta == 0 else None
            if inline:
                indent, contents = inline.groups()
                rendered.extend(
                    [
                        f"{indent}trigger = {{\n",
                        f"{indent}\tcurrent_date > {AntqDate(*END).engine()}\n",
                        f"{indent}\t{contents}\n",
                        f"{indent}}}\n",
                    ]
                )
            else:
                rendered.append(line)
                rendered.append(
                    f"{child.group(1)}\tcurrent_date > {AntqDate(*END).engine()}\n"
                )
            inerted_events += 1
            depth += delta
            continue

        if depth == 1 and depth + delta == 0:
            if inerted_events < saw_events:
                rendered.extend(
                    [
                        "\ttrigger = {\n",
                        f"\t\tcurrent_date > {AntqDate(*END).engine()}\n",
                        "\t}\n",
                    ]
                )
                inerted_events += 1
            rendered.append(line)
            depth += delta
            active_event = None
            continue

        rendered.append(line)
        depth += delta
        if depth < 0:
            raise ValueError(f"{relative}: source brace depth became negative")

    if depth != 0 or active_event is not None or skip_depth is not None:
        raise ValueError(f"{relative}: source brace contract changed")
    if saw_events + omitted_orphans != source_event_count:
        raise ValueError(
            f"{relative}: event accounting drift: source={source_event_count}, "
            f"retained={saw_events}, omitted={omitted_orphans}"
        )
    if saw_events and inerted_events != saw_events:
        raise ValueError(
            f"{relative}: expected every one of {saw_events} event definitions to become inert; "
            f"changed {inerted_events}"
        )
    result = DATE.sub(sanitized_date, "".join(rendered))
    result = neutralize_references(result, remap_effects=True)
    if "create_holy_site" in result:
        raise ValueError(f"{relative}: inherited create_holy_site call survived")
    return (b"\xef\xbb\xbf" if bom else b"") + result.encode("utf-8")


def output_path(relative: str) -> Path:
    return ROOT / relative


TYPE_LINE = re.compile(r"^\s*type\s*=\s*(?P<type>[a-z_]+)\b")
NAMESPACE_LINE = re.compile(r"^\s*namespace\s*=\s*[A-Za-z0-9_]+\s*(?:#.*)?$")


def compact_stub_render(relative: str) -> bytes:
    """Render every installed event as an exact-type, permanently inert stub."""
    text, bom = source_text(relative)
    lines = text.splitlines()
    namespaces = [line.strip() for line in lines if NAMESPACE_LINE.match(line)]
    contracts: list[tuple[str, str]] = []
    omitted = 0
    index = 0
    while index < len(lines):
        header = EVENT_HEADER.match(lines[index])
        if header is None:
            index += 1
            continue
        key = header.group(1)
        depth = brace_delta(lines[index])
        index += 1
        event_type: str | None = None
        while index < len(lines) and depth > 0:
            if depth == 1:
                type_match = TYPE_LINE.match(lines[index])
                if type_match is not None:
                    if event_type is not None:
                        raise ValueError(f"{relative}: {key} repeats its event type")
                    event_type = type_match.group("type")
            depth += brace_delta(lines[index])
            index += 1
        if depth != 0:
            raise ValueError(f"{relative}: {key} lacks a closed event contract")
        # The installed parser defaults omitted event types to country scope.
        if key in ORPHANED_INSTALLED_EVENTS:
            omitted += 1
        else:
            contracts.append((key, event_type or "country_event"))
    expected = event_definition_count(text)
    if (
        len(contracts) + omitted != expected
        or len({key for key, _ in contracts}) != len(contracts)
    ):
        raise ValueError(f"{relative}: event ID/type inventory drift")
    rendered = [
        "# Generated by tools/m12_event_quarantine.py --write.",
        "# Typed registry stubs only; inherited event bodies are quarantined.",
    ]
    rendered.extend(namespaces)
    if namespaces:
        rendered.append("")
    for key, event_type in contracts:
        rendered.extend((
            f"{key} = {{",
            f"\ttype = {event_type}",
            "\ttitle = empty_text",
            "\tdesc = empty_text",
            "\toutcome = neutral",
            "\ttrigger = {",
            f"\t\tcurrent_date > {AntqDate(*END).engine()}",
            "\t}",
            "}",
            "",
        ))
    result = "\n".join(rendered)
    return (b"\xef\xbb\xbf" if bom else b"") + result.encode("utf-8")


SOURCE_PRESERVING_RENDER = render
TAG_MAP = ROOT / "docs/world_1ad/tag_map.json"
COUNTRY_SCOPE_REF = re.compile(r"\bc:(?P<tag>[A-Z0-9]{3})\b")
TAG_FIELD = re.compile(
    r"(?P<prefix>\btag\s*=\s*)(?P<tag>[A-Z0-9]{3})\b"
)
DHE_HEADER = re.compile(r"\bdynamic_historical_event\s*=\s*\{")


def active_country_tags() -> frozenset[str]:
    data = json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))
    return frozenset(
        {entry["engine_tag"] for entry in data["entries"]}
        | {"DUMMY", "PIR", "MER"}
    )


def sanitize_dhe_country_tags(text: str, valid: frozenset[str]) -> str:
    """Redirect only DHE registry metadata, never scripted-effect parameters."""
    rendered: list[str] = []
    dhe_depth: int | None = None
    for line in text.splitlines(keepends=True):
        if dhe_depth is None and DHE_HEADER.search(line):
            dhe_depth = 0
        if dhe_depth is not None:
            line = TAG_FIELD.sub(
                lambda match: match.group(0)
                if match.group("tag") in valid
                else match.group("prefix") + "DUMMY",
                line,
            )
            dhe_depth += brace_delta(line)
            if dhe_depth == 0:
                dhe_depth = None
            elif dhe_depth < 0:
                raise ValueError("dynamic_historical_event brace depth became negative")
        rendered.append(line)
    if dhe_depth is not None:
        raise ValueError("unterminated dynamic_historical_event block")
    return "".join(rendered)


def render(relative: str) -> bytes:
    """Render type-correct inert stubs and sever removed-country lookups."""
    raw = SOURCE_PRESERVING_RENDER(relative)
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    valid = active_country_tags()
    text = COUNTRY_SCOPE_REF.sub(
        lambda match: match.group(0) if match.group("tag") in valid else "c:DUMMY",
        text,
    )
    text = sanitize_dhe_country_tags(text, valid)
    return (b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8")


def write() -> None:
    files = target_relatives()
    validate_orphan_inventory(files, scan_mounted=False)
    definitions = 0
    for relative in files:
        content = render(relative)
        destination = output_path(relative)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        definitions += event_definition_count(content.decode("utf-8-sig"))
    validate_orphan_inventory(files, scan_mounted=True)
    print(
        "m12_event_quarantine: wrote source-preserving, country-sanitized overlays for "
        f"{definitions} installed events in {len(files)} files"
    )


def cleanup_expanded() -> None:
    """Remove only verified generated overlays beyond the committed pilot."""
    removed = 0
    for relative in event_relatives():
        if relative == PILOT:
            continue
        destination = output_path(relative)
        if not destination.is_file():
            continue
        if destination.read_bytes() != render(relative):
            raise ValueError(
                f"refusing to remove non-generated event overlay: {relative}"
            )
        destination.unlink()
        removed += 1
    print(f"m12_event_quarantine: removed {removed} verified expanded overlays")


def check() -> bool:
    try:
        files = target_relatives()
        validate_orphan_inventory(files, scan_mounted=False)
        definitions = 0
        stale: list[str] = []
        for relative in files:
            expected = render(relative)
            definitions += event_definition_count(expected.decode("utf-8-sig"))
            destination = output_path(relative)
            if not destination.is_file() or destination.read_bytes() != expected:
                stale.append(relative)
        if not stale:
            validate_orphan_inventory(files, scan_mounted=True)
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        print(f"m12_event_quarantine: FAIL\n  - {exc}")
        return False
    if stale:
        preview = ", ".join(stale[:5])
        suffix = "" if len(stale) <= 5 else f" (+{len(stale) - 5} more)"
        print(f"m12_event_quarantine: FAIL\n  - stale or missing: {preview}{suffix}")
        return False
    print(
        "m12_event_quarantine: PASS "
        f"({definitions} source-preserved inert event IDs in {len(files)} files)"
    )
    return True


def capture_runtime_orphans(log_path: Path) -> None:
    """Capture EU5's clean-start orphan linker output as a sorted manifest."""
    if not log_path.is_file():
        raise ValueError(f"runtime error log is missing: {log_path}")
    pattern = re.compile(
        r"Event (?P<id>[A-Za-z][A-Za-z0-9_]*\.[0-9]+) is orphaned\s*$",
        re.MULTILINE,
    )
    newly_observed = set(
        pattern.findall(log_path.read_text(encoding="utf-8-sig"))
    )
    observed = sorted(newly_observed | set(runtime_orphan_manifest()))
    if not observed:
        raise ValueError("runtime error log contains no orphan-event linker output")
    source_ids: set[str] = set()
    for relative in event_relatives():
        text, _bom = source_text(relative)
        source_ids.update(
            match.group(1)
            for line in text.splitlines()
            if (match := EVENT_HEADER.match(line)) is not None
        )
    unknown = sorted(set(observed) - source_ids)
    if unknown:
        raise ValueError(
            "runtime orphan inventory contains IDs absent from installed source: "
            + ", ".join(unknown[:10])
        )
    config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
    header = [
        "# Generated by tools/m12_event_quarantine.py --capture-runtime-orphans.",
        "# Authoritative EU5 clean-start linker output after compact event quarantine.",
        f"# game_build_id={config.get('game_build_id', 'unknown')}",
    ]
    RUNTIME_ORPHAN_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    RUNTIME_ORPHAN_MANIFEST.write_text(
        "\n".join(header + observed) + "\n", encoding="utf-8"
    )
    print(
        "m12_event_quarantine: captured "
        f"{len(newly_observed)} current / {len(observed)} cumulative runtime orphan IDs "
        f"in {RUNTIME_ORPHAN_MANIFEST}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--cleanup-expanded", action="store_true")
    mode.add_argument("--capture-runtime-orphans", type=Path, metavar="ERROR_LOG")
    args = parser.parse_args()
    if args.write:
        try:
            write()
        except (OSError, ValueError, UnicodeDecodeError) as exc:
            print(f"m12_event_quarantine: FAIL\n  - {exc}")
            return 1
        return 0
    if args.cleanup_expanded:
        try:
            cleanup_expanded()
        except (OSError, ValueError, UnicodeDecodeError) as exc:
            print(f"m12_event_quarantine: FAIL\n  - {exc}")
            return 1
        return 0
    if args.capture_runtime_orphans is not None:
        try:
            capture_runtime_orphans(args.capture_runtime_orphans)
        except (OSError, ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            print(f"m12_event_quarantine: FAIL\n  - {exc}")
            return 1
        return 0
    return 0 if check() else 1


if __name__ == "__main__":
    raise SystemExit(main())
