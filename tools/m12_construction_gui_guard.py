#!/usr/bin/env python3
"""Guard the build-location selector's empty civil-construction badge.

The installed row template binds index zero of every location's civil
construction model even when that model is empty.  Visibility does not defer
GUI data-context evaluation, so every visible empty location emits an
out-of-range ``Construction`` diagnostic.

Render an exact-name, source-preserving overlay which represents the first
construction as a zero-safe one-item data model.  The badge count and its full
construction tooltip remain unchanged whenever an item exists.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
RELATIVE_SOURCE = Path("game/in_game/gui/build_location_lateralview.gui")
OUTPUT = ROOT / "in_game/gui/build_location_lateralview.gui"


def source_file(relative: Path = RELATIVE_SOURCE) -> Path:
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
        path = Path(config["game_dir"]) / relative
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot resolve installed construction GUI: {exc}") from exc
    if not path.is_file():
        raise ValueError(f"installed construction GUI is missing: {path}")
    return path


def render() -> bytes:
    source = source_file()
    raw = source.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    context_token = 'datamodel = "[Location.GetCivilConstructions]"'
    if text.count(context_token) != 1:
        raise ValueError(
            f"{source.name}: expected one unsafe civil-construction model, "
            f"found {text.count(context_token)}"
        )
    context_index = text.index(context_token)
    block_start = text.rfind("text_single = {", 0, context_index)
    if block_start < 0:
        raise ValueError(f"{source.name}: civil-construction badge was not found")
    opening = text.index("{", block_start)
    block_end = matching_brace(text, opening) + 1
    line_start = text.rfind("\n", 0, block_start) + 1
    indent = text[line_start:block_start]
    if indent.strip():
        raise ValueError(f"{source.name}: unexpected badge indentation")
    safe = (
        "hbox = {" + newline
        + indent + '\tdatacontext = "[LocationToBuildItem.GetLocation]"' + newline
        + indent + '\tdatamodel = "[DataModelFirst(Location.GetCivilConstructions, \'(int32)1\')]"' + newline
        + indent + "\titem = {" + newline
        + indent + "\t\ttext_single = {" + newline
        + indent + "\t\t\tautoresize = yes" + newline
        + indent + "\t\t\tusing = Font_Size_Very_Small" + newline
        + indent + '\t\t\traw_text = "(#L +[GetDataModelSize(Location.GetCivilConstructions)]#! @construction!)"' + newline
        + indent + "\t\t\ttooltipwidget = {" + newline
        + indent + "\t\t\t\tusing = Construction_tooltip" + newline
        + indent + "\t\t\t}" + newline
        + indent + "\t\t}" + newline
        + indent + "\t}" + newline
        + indent + "}"
    )
    text = text[:block_start] + safe + text[block_end:]
    marker = "# ANTIQVITAS guards empty civil-construction row models; do not hand-edit."
    text = marker + newline + text
    result = text.encode("utf-8")
    return (b"\xef\xbb\xbf" if has_bom else b"") + result


def matching_brace(text: str, opening: int) -> int:
    depth = 0
    for index in range(opening, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return index
    raise ValueError("unterminated GUI block")


def write() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(render())
    print(f"m12_construction_gui_guard: wrote {OUTPUT.relative_to(ROOT)}")


def check() -> bool:
    try:
        expected = render()
    except (OSError, ValueError) as exc:
        print(f"m12_construction_gui_guard: FAIL\n  - {exc}")
        return False
    if not OUTPUT.is_file():
        print(f"m12_construction_gui_guard: FAIL\n  - missing {OUTPUT.relative_to(ROOT)}")
        return False
    actual = OUTPUT.read_bytes()
    failures: list[str] = []
    if actual != expected:
        failures.append(f"stale {OUTPUT.relative_to(ROOT)}")
    decoded = actual.decode("utf-8-sig", errors="replace")
    if "datacontext_from_model" in decoded[decoded.find("GetCivilConstructions") : decoded.find("GetCivilConstructions") + 900]:
        failures.append("unsafe civil-construction index access remains")
    if "DataModelFirst(Location.GetCivilConstructions, '(int32)1')" not in decoded:
        failures.append("zero-safe civil-construction model is missing")
    if failures:
        print("m12_construction_gui_guard: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return False
    print(
        "m12_construction_gui_guard: PASS "
        "(exact installed GUI; empty civil-construction rows guarded)"
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        write()
    if args.check:
        return 0 if check() else 1
    if not args.write:
        parser.error("choose --write and/or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
