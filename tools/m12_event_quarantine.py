#!/usr/bin/env python3
"""Keep installed vanilla event files loader-valid while disabling eligibility.

This is a deliberately narrow engine-contract pilot.  EU5 validates event
references, scope types, and variable/effect links across its generic systems
at load time.  Replacing a dated event file with empty stubs loses that graph;
instead, this renderer preserves each installed event definition, its scheduler,
and its scope/effect graph while adding an impossible-in-era date condition to
its direct eligibility.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from dates import AntqDate, END, START


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
EVENT_ROOT = Path("in_game/events")
PILOT = "in_game/events/random_event.txt"
EVENT_HEADER = re.compile(r"^([A-Za-z][A-Za-z0-9_]*\.[0-9]+)\s*=\s*\{")
TRIGGER_BLOCK = re.compile(r"^(\s*)trigger\s*=\s*\{")
INLINE_TRIGGER = re.compile(r"^(\s*)trigger\s*=\s*\{\s*(.*?)\s*\}\s*(?:#.*)?$")
DATE = re.compile(r"(?<![0-9])-?[0-9]{1,4}\.[0-9]{1,2}\.[0-9]{1,2}(?![0-9])")


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


def sanitized_date(match: re.Match[str]) -> str:
    value = match.group(0)
    if value.startswith("-"):
        return value
    year = int(value.split(".", 1)[0])
    if year > END[0]:
        return AntqDate(*END).engine()
    return value


def render(relative: str) -> bytes:
    text, bom = source_text(relative)
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
    if saw_events == 0 or inerted_events != saw_events:
        raise ValueError(
            f"{relative}: expected every one of {saw_events} event definitions to become inert; "
            f"changed {inerted_events}"
        )
    result = DATE.sub(sanitized_date, "".join(rendered))
    return (b"\xef\xbb\xbf" if bom else b"") + result.encode("utf-8")


def output_path(relative: str) -> Path:
    return ROOT / relative


def write() -> None:
    files = target_relatives()
    definitions = 0
    for relative in files:
        content = render(relative)
        destination = output_path(relative)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        definitions += event_definition_count(content.decode("utf-8-sig"))
    print(
        "m12_event_quarantine: wrote source-preserving date-gated overlays for "
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
        definitions = 0
        stale: list[str] = []
        for relative in files:
            expected = render(relative)
            definitions += event_definition_count(expected.decode("utf-8-sig"))
            destination = output_path(relative)
            if not destination.is_file() or destination.read_bytes() != expected:
                stale.append(relative)
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
        f"({definitions} date-gated installed events in {len(files)} files)"
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--cleanup-expanded", action="store_true")
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
    return 0 if check() else 1


if __name__ == "__main__":
    raise SystemExit(main())
