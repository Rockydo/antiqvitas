#!/usr/bin/env python3
"""Maintain the M12 engine-required culture-presence compatibility ledger."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/m12/culture_presence.csv"
M4_SYMBOLS = ROOT / "docs/m4/definition_symbols.json"
VANILLA_CULTURES = ROOT / "docs/vanilla_symbols/culture.json"
WARNING = re.compile(r"Culture has no pops in the setup:\s*([A-Za-z0-9_]+)")
# The final probe suppresses this one warning; its prior unseeded probe remains
# the locally verified evidence for retaining it in the ledger.
PROVEN_ABSENT = {"antq_galatian"}


def known_cultures() -> set[str]:
    vanilla = set(json.loads(VANILLA_CULTURES.read_text(encoding="utf-8-sig")))
    m4 = set(json.loads(M4_SYMBOLS.read_text(encoding="utf-8"))["cultures"])
    return vanilla | m4


def read() -> list[str]:
    with OUTPUT.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(line for line in handle if not line.startswith("#"))
        if tuple(reader.fieldnames or ()) != ("culture",):
            raise ValueError(f"{OUTPUT.relative_to(ROOT)} must contain only a culture column")
        rows = [row["culture"].strip() for row in reader]
    if not rows or any(not row for row in rows) or rows != sorted(set(rows)):
        raise ValueError(f"{OUTPUT.relative_to(ROOT)} must be non-empty, sorted, and unique")
    unknown = sorted(set(rows) - known_cultures())
    if unknown:
        raise ValueError(f"{OUTPUT.relative_to(ROOT)} has unknown culture(s): {unknown[:8]}")
    return rows


def write() -> int:
    config = json.loads((ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig"))
    log = Path(str(config["user_dir"])) / "logs/error.log"
    existing = set(read()) if OUTPUT.is_file() else set()
    cultures = existing | set(WARNING.findall(log.read_text(encoding="utf-8-sig", errors="replace"))) | PROVEN_ABSENT
    unknown = sorted(cultures - known_cultures())
    if unknown:
        raise ValueError(f"live initializer reported unknown culture(s): {unknown[:8]}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        "# EU5 1.3.11 AD 1 initializer no-pop diagnostics, harvested 2026-07-24.\n"
        "culture\n" + "".join(f"{culture}\n" for culture in sorted(cultures)),
        encoding="utf-8-sig",
        newline="\n",
    )
    print(f"m12_culture_presence: wrote {len(cultures)} cultures")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.write:
            return write()
        print(f"m12_culture_presence: PASS ({len(read())} initializer-required cultures)")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"m12_culture_presence: FAIL\n  - {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
