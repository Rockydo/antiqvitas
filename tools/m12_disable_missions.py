#!/usr/bin/env python3
"""Disable installed generic mission packs through exact-name overlays.

The local mission packs contain colonial, Renaissance, Reformation, and other
post-antique gates.  Their keys remain defined for engine references, but each
top-level pack receives an impossible visibility condition.  Source inventory
and content are re-read on every check, so an EU5 update leaves a stale overlay
instead of silently changing mission behaviour.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
OUTPUT_DIR = ROOT / "in_game/common/missions"
INFO_FILE = "____Info.txt"
VISIBLE = re.compile(r"^(?P<indent>\s*)visible\s*=\s*\{")


def source_dir() -> Path:
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
        path = Path(config["game_dir"]) / "game/in_game/common/missions"
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot resolve installed mission directory: {exc}") from exc
    if not path.is_dir():
        raise ValueError(f"installed mission directory is missing: {path}")
    return path


def source_files() -> tuple[Path, ...]:
    files = tuple(sorted(
        (path for path in source_dir().glob("*.txt") if path.name != INFO_FILE),
        key=lambda path: path.name.lower(),
    ))
    if len(files) != 11:
        raise ValueError(f"expected 11 installed mission packs, found {len(files)}")
    return files


def brace_delta(line: str) -> int:
    code = line.split("#", 1)[0]
    return code.count("{") - code.count("}")


def render(source: Path) -> bytes:
    raw = source.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    lines = text.splitlines(keepends=True)
    rendered: list[str] = []
    depth = 0
    gates = 0
    for line in lines:
        code = line.split("#", 1)[0]
        match = VISIBLE.match(code) if depth == 1 else None
        rendered.append(line)
        if match is not None:
            if brace_delta(code) != 1:
                raise ValueError(f"{source.name}: top-level visible contract is not a multiline block")
            newline = "\r\n" if line.endswith("\r\n") else "\n"
            rendered.append(f"{match.group('indent')}\talways = no # M12 disables anachronistic vanilla mission{newline}")
            gates += 1
        depth += brace_delta(line)
        if depth < 0:
            raise ValueError(f"{source.name}: brace depth became negative")
    if depth != 0:
        raise ValueError(f"{source.name}: brace depth ends at {depth}")
    if gates != 1:
        raise ValueError(f"{source.name}: expected one top-level visible gate, found {gates}")
    result = "".join(rendered).encode("utf-8")
    return (b"\xef\xbb\xbf" if has_bom else b"") + result


def outputs() -> dict[Path, bytes]:
    return {OUTPUT_DIR / source.name: render(source) for source in source_files()}


def write() -> None:
    for path, content in outputs().items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        print(f"m12_disable_missions: wrote {path.relative_to(ROOT)}")


def check() -> bool:
    try:
        expected = outputs()
    except (OSError, ValueError) as exc:
        print(f"m12_disable_missions: FAIL\n  - {exc}")
        return False
    actual = set(OUTPUT_DIR.glob("*.txt")) if OUTPUT_DIR.is_dir() else set()
    expected_paths = set(expected)
    failures = [f"missing {path.relative_to(ROOT)}" for path in sorted(expected_paths - actual)]
    failures.extend(f"unexpected {path.relative_to(ROOT)}" for path in sorted(actual - expected_paths))
    for path, content in expected.items():
        if path.is_file() and path.read_bytes() != content:
            failures.append(f"stale {path.relative_to(ROOT)}")
    if failures:
        print("m12_disable_missions: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return False
    print(f"m12_disable_missions: PASS ({len(expected)} exact-name unavailable mission packs)")
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
            print(f"m12_disable_missions: FAIL\n  - {exc}")
            return 1
        return 0
    return 0 if check() else 1


if __name__ == "__main__":
    raise SystemExit(main())
