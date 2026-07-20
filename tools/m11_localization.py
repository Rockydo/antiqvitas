#!/usr/bin/env python3
"""Enforce ANTIQVITAS's English-first localization mirror contract."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from dates import M2_MIRROR_LANGUAGES


ROOT = Path(__file__).resolve().parents[1]
LOCALIZATION = ROOT / "main_menu/localization"
FORBIDDEN = re.compile(r"\b(?:todo|tbd|placeholder|lorem ipsum)\b", re.IGNORECASE)
ENTRY = re.compile(r"(?m)^\s+[^\s:#][^:]*:\s*\"")


def read_checked(path: Path, language: str) -> str:
    raw = path.read_bytes()
    if not raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"localization is missing a UTF-8 BOM: {path}")
    text = raw.decode("utf-8-sig")
    if re.match(rf"\Al_{re.escape(language)}:\r?\n", text) is None:
        raise ValueError(f"localization has an invalid language header: {path}")
    forbidden = FORBIDDEN.search(text)
    if forbidden is not None:
        raise ValueError(f"forbidden localization stub {forbidden.group()!r}: {path}")
    return text


def mirror_name(english_name: str, language: str) -> str:
    if not english_name.endswith("_l_english.yml"):
        raise ValueError(f"English localization filename has no language suffix: {english_name}")
    return english_name.removesuffix("_l_english.yml") + f"_l_{language}.yml"


def normalized_header(text: str, language: str) -> str:
    return re.sub(
        rf"\Al_{re.escape(language)}:\r?\n", "l_LANGUAGE:\n", text, count=1,
    )


def validate() -> None:
    english_dir = LOCALIZATION / "english"
    english_paths = sorted(english_dir.glob("*.yml"))
    if not english_paths:
        raise ValueError("no ANTIQVITAS English localization files found")
    english = {path.name: read_checked(path, "english") for path in english_paths}
    entries = sum(len(ENTRY.findall(text)) for text in english.values())
    if entries == 0:
        raise ValueError("English localization contains no quoted entries")
    for language in M2_MIRROR_LANGUAGES:
        directory = LOCALIZATION / language
        actual = {path.name for path in directory.glob("*.yml")}
        expected = {mirror_name(name, language) for name in english}
        if actual != expected:
            raise ValueError(
                f"{language} localization inventory drift: "
                f"missing={sorted(expected - actual)}, extra={sorted(actual - expected)}"
            )
        for english_name, english_text in english.items():
            mirror = directory / mirror_name(english_name, language)
            mirrored_text = read_checked(mirror, language)
            if normalized_header(mirrored_text, language) != normalized_header(english_text, "english"):
                raise ValueError(f"{language} localization content diverges from English: {mirror}")
    print(
        f"m11_localization: PASS ({len(english)} English files; "
        f"{len(M2_MIRROR_LANGUAGES)} exact mirrors; {entries} quoted entries; zero stubs)"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate localization mirrors")
    parser.parse_args()
    validate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
