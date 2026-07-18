#!/usr/bin/env python3
"""Generate BOM-safe localization stubs and optional English mirrors."""

from __future__ import annotations

import argparse
from pathlib import Path

LANGUAGES = (
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


def write(path: Path, language: str, entries: list[tuple[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"l_{language}:"]
    lines.extend(f' {key}: "{value}"' for key, value in entries)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("keys", nargs="+")
    parser.add_argument("--mirror", action="store_true")
    args = parser.parse_args()
    entries = [(key, f"TODO {key}") for key in args.keys]
    write(args.output, "english", entries)
    if args.mirror:
        for language in LANGUAGES:
            path = args.output.with_name(
                args.output.name.replace("_l_english.yml", f"_l_{language}.yml")
            )
            write(path, language, entries)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
