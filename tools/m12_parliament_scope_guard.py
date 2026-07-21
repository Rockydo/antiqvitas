#!/usr/bin/env python3
"""Guard absent-government comparisons in installed parliament scripts.

The AD 1 start contains unformed legacy country objects while the parliament
registry is initialized.  The installed peasants-estate template evaluates
eight ordinary ``government_type`` comparisons against those unset objects,
which emits script diagnostics even though the issues are unavailable.  EU5's
locally evidenced optional ``?=`` comparison makes exactly those predicates
false when the scope is absent without changing their result for countries
that do have a government.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
COMPARISON = re.compile(
    r"government_type\s*=\s*government_type:(?P<kind>monarchy|republic|theocracy)"
)
# These are the complete comparisons which the live AD 1 observer log identifies
# as evaluating on an unset country scope.  All other parliament templates stay
# byte-for-byte inherited from the installed scripts.
SOURCES = {
    Path("game/in_game/common/parliament_issues/06_peasants_estate_parliament_issues.txt"): (
        ROOT / "in_game/common/parliament_issues/06_peasants_estate_parliament_issues.txt",
        frozenset((569, 570, 623, 624, 689, 690, 752)),
        Counter({"monarchy": 4, "republic": 3}),
    ),
    Path("game/in_game/common/parliament_issues/07_expansion_parliament_issues.txt"): (
        ROOT / "in_game/common/parliament_issues/07_expansion_parliament_issues.txt",
        frozenset((785,)),
        Counter({"theocracy": 1}),
    ),
}


def source_path(relative: Path) -> Path:
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
        source = Path(str(config["game_dir"])) / relative
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot resolve installed parliament source: {exc}") from exc
    if not source.is_file():
        raise ValueError(f"installed parliament source is missing: {source}")
    return source


def render(relative: Path, targets: frozenset[int], expected_inventory: Counter[str]) -> bytes:
    raw = source_path(relative).read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    lines = raw.decode("utf-8-sig").splitlines(keepends=True)
    rendered: list[str] = []
    guarded: Counter[str] = Counter()

    for line_number, line in enumerate(lines, start=1):
        comparison = COMPARISON.search(line) if line_number in targets else None
        if comparison is None:
            rendered.append(line)
            continue
        kind = comparison.group("kind")
        rendered.append(COMPARISON.sub(f"government_type ?= government_type:{kind}", line, count=1))
        guarded[kind] += 1

    if guarded != expected_inventory:
        raise ValueError(
            f"parliament comparison inventory drift: expected={dict(expected_inventory)} "
            f"found={dict(guarded)}"
        )
    result = "".join(rendered).encode("utf-8")
    return (b"\xef\xbb\xbf" if has_bom else b"") + result


def write() -> None:
    for relative, (output, targets, expected_inventory) in SOURCES.items():
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(render(relative, targets, expected_inventory))
        print(f"m12_parliament_scope_guard: wrote {output.relative_to(ROOT)}")


def check() -> bool:
    try:
        rendered = {
            output: render(relative, targets, expected_inventory)
            for relative, (output, targets, expected_inventory) in SOURCES.items()
        }
    except (OSError, ValueError) as exc:
        print(f"m12_parliament_scope_guard: FAIL\n  - {exc}")
        return False
    stale = [output.relative_to(ROOT) for output, expected in rendered.items()
             if not output.is_file() or output.read_bytes() != expected]
    if stale:
        print("m12_parliament_scope_guard: FAIL\n  - stale or missing " + ", ".join(map(str, stale)))
        return False
    print("m12_parliament_scope_guard: PASS (8 optional-government comparisons in 2 files)")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        try:
            write()
        except (OSError, ValueError) as exc:
            print(f"m12_parliament_scope_guard: FAIL\n  - {exc}")
            return 1
        return 0
    return 0 if check() else 1


if __name__ == "__main__":
    raise SystemExit(main())
