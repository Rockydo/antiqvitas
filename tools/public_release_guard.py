#!/usr/bin/env python3
"""Reject personal identity and machine-local paths in tracked artifacts."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ALLOW = {"docs/ANTIQVITAS_MASTER_PLAN.md", "config/local_paths.example.json"}
TEXT_SUFFIXES = {
    "", ".acf", ".bat", ".cfg", ".csv", ".gitignore", ".gui", ".json",
    ".log", ".md", ".ps1", ".py", ".toml", ".tsv", ".txt", ".vdf",
    ".yml", ".yaml",
}
PATTERNS = (
    ("Windows user profile", re.compile(rb"[A-Za-z]:[\\/]+Users[\\/]+(?!<USER>)[^\\/\s\"']+", re.I)),
    ("local Steam library", re.compile(rb"[A-Za-z]:[\\/]+(?:SteamLibrary|Steam)[\\/]", re.I)),
    ("local ANTIQVITAS path", re.compile(rb"[A-Za-z]:[\\/]+antiqvitas(?:_user_data|_runtime)?(?:[\\/]|\b)", re.I)),
    ("escaped Windows user profile", re.compile(rb"[A-Za-z]:\\\\Users\\\\(?!<USER>)[^\\\"']+", re.I)),
    ("escaped local Steam library", re.compile(rb"[A-Za-z]:\\\\(?:SteamLibrary|Steam)\\\\", re.I)),
    ("escaped local ANTIQVITAS path", re.compile(rb"[A-Za-z]:\\\\antiqvitas(?:_user_data|_runtime)?(?:\\\\|\b)", re.I)),
)


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
    )
    return [ROOT / raw.decode("utf-8") for raw in result.stdout.split(b"\0") if raw]


def sanitize(files: list[Path]) -> int:
    config_path = ROOT / "config/local_paths.json"
    if not config_path.is_file():
        raise ValueError("config/local_paths.json is required for --write")
    config = json.loads(config_path.read_text(encoding="utf-8-sig"))
    replacements: dict[str, str] = {
        str(config.get("mod_dir", "")): "<MOD_DIR>",
        str(config.get("game_exe", "")): "<GAME_EXE>",
        str(config.get("game_manifest", "")): "<GAME_MANIFEST>",
        str(config.get("game_dir", "")): "<GAME_DIR>",
        str(config.get("repo_dir", "")): "<REPO_DIR>",
        str(config.get("user_dir", "")): "<EU5_USER_DIR>",
        str(config.get("candidate_relocated_user_dir", "")): "<EU5_USER_DIR>",
        str(config.get("original_user_dir", "")): "<EU5_USER_DIR>",
        str(config.get("documents_dir", "")): "<USER_DOCUMENTS>",
        str(config.get("steam_exe", "")): "<STEAM_EXE>",
        str(config.get("steam_dir", "")): "<STEAM_DIR>",
    }
    for library in config.get("steam_libraries", []):
        replacements[str(library)] = "<STEAM_LIBRARY>"
    replacements = {
        source: token for source, token in replacements.items()
        if source and re.match(r"^[A-Za-z]:[\\/]", source)
    }
    changed = 0
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        if relative in ALLOW or not path.is_file() or path.suffix.casefold() not in TEXT_SUFFIXES:
            continue
        data = path.read_bytes()
        rendered = data
        for source, token in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
            pairs = (
                (source, token),
                (source.replace("\\", "\\\\"), token),
                (source.replace("\\", "/"), token),
            )
            for old, new in pairs:
                rendered = rendered.replace(old.encode("utf-8"), new.encode("utf-8"))
        if rendered != data:
            path.write_bytes(rendered)
            changed += 1
    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    files = tracked_files()
    if args.write:
        try:
            changed = sanitize(files)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"public_release_guard: FAIL\n  - {exc}")
            return 1
        print(f"public_release_guard: sanitized {changed} tracked files")
    failures: list[str] = []
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        if relative in ALLOW or not path.is_file() or path.suffix.casefold() not in TEXT_SUFFIXES:
            continue
        data = path.read_bytes()
        for label, pattern in PATTERNS:
            match = pattern.search(data)
            if match:
                line = data.count(b"\n", 0, match.start()) + 1
                failures.append(f"{relative}:{line}: {label}")
    if failures:
        print("public_release_guard: FAIL")
        print("\n".join(f"  - {item}" for item in failures))
        return 1
    print(f"public_release_guard: PASS ({len(files)} tracked files; no local identity/path leakage)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
