#!/usr/bin/env python3
"""Guard ANTIQVITAS's authored English text against clear post-476 vocabulary.

The campaign deliberately retains technical vanilla keys and exact-name
compatibility overlays.  Those are not player-facing authored claims.  This
audit therefore examines only values in the mod's English-first localization
files, where anachronistic language would actually reach the player.  The M11
mirror validator separately proves that every supported client receives these
same values.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENGLISH_DIR = ROOT / "main_menu/localization/english"
REPORT = ROOT / "docs/m12/ANACHRONISM_AUDIT.md"
ENTRY = re.compile(
    r'^\s*(?P<key>[^:#\s][^:]*):(?:\d+)?\s+"(?P<value>(?:\\.|[^"\\])*)"\s*(?:#.*)?$'
)

# These are unambiguously outside the 1--476 campaign when used as a
# player-facing campaign concept. Broader terms such as "feudal", "empire",
# or "church" are intentionally not prohibited: their historical meanings
# are contextual and the design bible itself uses several of them.
FORBIDDEN_TERMS = (
    "absolutism",
    "absolutist",
    "calvinism",
    "calvinist",
    "cannon",
    "cannons",
    "colonial",
    "colonialism",
    "colonies",
    "colonist",
    "colonization",
    "colonize",
    "colonized",
    "crusade",
    "crusader",
    "factory",
    "factories",
    "habsburg",
    "industrial",
    "industrialization",
    "lutheran",
    "lutheranism",
    "musket",
    "muskets",
    "napoleon",
    "napoleonic",
    "ottoman",
    "pistol",
    "pistols",
    "protestant",
    "protestantism",
    "railroad",
    "railroads",
    "railway",
    "railways",
    "reformation",
    "renaissance",
    "rifle",
    "rifles",
    "safavid",
    "steam engine",
    "steam engines",
    "steamship",
    "steamships",
    "united states",
)
FORBIDDEN = re.compile(
    r"\b(?:" + "|".join(re.escape(term) for term in FORBIDDEN_TERMS) + r")\b",
    re.IGNORECASE,
)


def english_files() -> tuple[Path, ...]:
    files = tuple(sorted(ENGLISH_DIR.glob("antq_*_l_english.yml")))
    if not files:
        raise ValueError("no ANTIQVITAS English localization files found")
    return files


def audit() -> tuple[tuple[Path, ...], int]:
    files = english_files()
    entries = 0
    failures: list[str] = []
    for path in files:
        raw = path.read_bytes()
        if not raw.startswith(b"\xef\xbb\xbf"):
            failures.append(f"{path.relative_to(ROOT)}: missing UTF-8 BOM")
            continue
        lines = raw.decode("utf-8-sig").splitlines()
        if not lines or lines[0] != "l_english:":
            failures.append(f"{path.relative_to(ROOT)}: invalid English header")
            continue
        for number, line in enumerate(lines[1:], start=2):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            match = ENTRY.match(line)
            if match is None:
                failures.append(
                    f"{path.relative_to(ROOT)}:{number}: unparsed localization entry"
                )
                continue
            entries += 1
            forbidden = FORBIDDEN.search(match.group("value"))
            if forbidden is not None:
                failures.append(
                    f"{path.relative_to(ROOT)}:{number} {match.group('key')}: "
                    f"forbidden player-facing term {forbidden.group()!r}"
                )
    if failures:
        raise ValueError("\n".join(failures))
    if entries == 0:
        raise ValueError("no quoted localization entries found")
    return files, entries


def render(files: tuple[Path, ...], entries: int) -> str:
    terms = ", ".join(f"`{term}`" for term in FORBIDDEN_TERMS)
    inventory = "\n".join(f"- `{path.relative_to(ROOT).as_posix()}`" for path in files)
    return f"""# M12 authored-text anachronism audit

This generated audit enforces the plan's Appendix A anachronism sweep against
the player-facing text written by ANTIQVITAS. It reads English localization
values only; it deliberately does not inspect technical identifiers, comments,
or copied exact-name vanilla compatibility overlays. `tools/m11_localization.py`
separately proves the other supported language folders exactly mirror English.

## Checked inventory

{inventory}

## Clear post-476 vocabulary

The prohibited vocabulary is deliberately narrow: {terms}. Context-sensitive
words such as `empire`, `church`, and `feudal` are not blocked because a raw
word match would make unsupported historical assertions rather than improve
the audit.

## Result

{len(files)} English files and {entries} quoted player-facing entries contain
zero prohibited terms. The check is pinned in `make validate`; a newly authored
anachronism fails before it can reach a smoke run.
"""


def write() -> None:
    files, entries = audit()
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(render(files, entries), encoding="utf-8", newline="\n")
    print(f"m12_anachronism_audit: wrote {REPORT.relative_to(ROOT)}")


def check() -> bool:
    try:
        files, entries = audit()
        expected = render(files, entries)
    except (OSError, ValueError) as exc:
        print(f"m12_anachronism_audit: FAIL\n  - {exc}")
        return False
    if not REPORT.is_file() or REPORT.read_text(encoding="utf-8") != expected:
        print(f"m12_anachronism_audit: FAIL\n  - stale or missing {REPORT.relative_to(ROOT)}")
        return False
    print(
        f"m12_anachronism_audit: PASS ({len(files)} English files; "
        f"{entries} player-facing entries; zero prohibited terms)"
    )
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
            print(f"m12_anachronism_audit: FAIL\n  - {exc}")
            return 1
        return 0
    return 0 if check() else 1


if __name__ == "__main__":
    raise SystemExit(main())
