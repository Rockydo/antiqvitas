#!/usr/bin/env python3
"""Tier-0 structural validator; extended as engine symbols are harvested."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAME_TREES = ("in_game", "main_menu", "loading_screen")
DATE_RE = re.compile(r"(?<![\w.])(\d{1,4})\.(\d{1,2})\.(\d{1,2})(?![\w.])")


def balanced_script(text: str) -> tuple[bool, str]:
    depth = 0
    quoted = False
    escaped = False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
            continue
        if char == '"':
            quoted = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth < 0:
                return False, "closing brace without opener"
    if quoted:
        return False, "unterminated quoted string"
    if depth:
        return False, f"brace depth ends at {depth}"
    return True, ""


def expected_bom(path: Path) -> bool | None:
    relative = path.relative_to(ROOT).as_posix()
    if "/setup/start/" in f"/{relative}":
        return False
    if "/setup/countries/" in f"/{relative}" or "/setup/templates/" in f"/{relative}":
        return True
    if path.suffix.lower() == ".yml":
        return True
    return None


def validate() -> list[str]:
    failures: list[str] = []
    config = ROOT / "config/local_paths.json"
    if not config.is_file():
        failures.append("missing config/local_paths.json; run tools/find_game.py")
    else:
        try:
            paths = json.loads(config.read_text(encoding="utf-8-sig"))
            game_dir = Path(paths["game_dir"])
            if not (game_dir / "binaries/eu5.exe").is_file():
                failures.append("configured game_dir does not contain binaries/eu5.exe")
            if Path(paths["repo_dir"]).resolve() != ROOT:
                failures.append("configured repo_dir does not match repository root")
        except (KeyError, json.JSONDecodeError) as exc:
            failures.append(f"invalid local_paths.json: {exc}")

    for tree in GAME_TREES:
        root = ROOT / tree
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".txt", ".gui", ".gfx", ".yml"}:
                continue
            raw = path.read_bytes()
            bom = raw.startswith(b"\xef\xbb\xbf")
            required = expected_bom(path)
            if required is not None and bom != required:
                failures.append(f"{path.relative_to(ROOT)}: UTF-8 BOM must be {required}")
            try:
                text = raw.decode("utf-8-sig")
            except UnicodeDecodeError as exc:
                failures.append(f"{path.relative_to(ROOT)}: invalid UTF-8: {exc}")
                continue
            if path.suffix.lower() != ".yml":
                okay, reason = balanced_script(text)
                if not okay:
                    failures.append(f"{path.relative_to(ROOT)}: {reason}")
            for match in DATE_RE.finditer(text):
                year, month, day = (int(value) for value in match.groups())
                if not (1 <= year <= 476 and 1 <= month <= 12 and 1 <= day <= 31):
                    failures.append(
                        f"{path.relative_to(ROOT)}: out-of-range scripted date {match.group(0)}"
                    )
    metadata = ROOT / ".metadata/metadata.json"
    if metadata.exists():
        try:
            value = json.loads(metadata.read_text(encoding="utf-8"))
            for key in ("name", "id", "version", "supported_game_version"):
                if key not in value:
                    failures.append(f".metadata/metadata.json: missing {key}")
        except json.JSONDecodeError as exc:
            failures.append(f".metadata/metadata.json: invalid JSON: {exc}")
    return failures


def main() -> int:
    failures = validate()
    if failures:
        print("pdxlint: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("pdxlint: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
