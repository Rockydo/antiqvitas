#!/usr/bin/env python3
"""Produce a reviewable bridge from historical capitals to EU5 location keys."""

from __future__ import annotations

import argparse
import csv
import difflib
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "docs/world_1ad/polities.csv"
LOCATIONS = ROOT / "docs/vanilla_symbols/locations.json"
OUTPUT = ROOT / "docs/world_1ad/capital_candidates.csv"
LOCATION_LOC = (
    "game/main_menu/localization/english/location_names/location_names_l_english.yml"
)
LOC_LINE = re.compile(r'^\s*([\w.-]+):\s*"([^"]+)"')

# Only spelling/exonym bridges. A geographic approximation must be researched
# and entered in polities.csv by hand; it may not be silently generated here.
ALIASES = {
    "roma": "rome",
    "aksum": "axum",
    "turfan": "turpan",
    "teotihuacan": "tehotihuacan",  # installed key spelling
}


def normalize(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", ascii_value.lower())


def game_dir() -> Path:
    config = json.loads((ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig"))
    return Path(config["game_dir"])


def location_names() -> dict[str, str]:
    names: dict[str, str] = {}
    for line in (game_dir() / LOCATION_LOC).read_text(encoding="utf-8-sig").splitlines():
        match = LOC_LINE.match(line)
        if match:
            names[match.group(1)] = match.group(2)
    known_locations = set(json.loads(LOCATIONS.read_text(encoding="utf-8-sig")))
    return {key: label for key, label in names.items() if key in known_locations}


def candidate_rows() -> tuple[list[dict[str, str]], list[str]]:
    with ROSTER.open(encoding="utf-8-sig", newline="") as handle:
        roster = list(csv.DictReader(handle))
    names = location_names()
    by_normalized_label: dict[str, list[str]] = {}
    by_normalized_key: dict[str, list[str]] = {}
    for key, label in names.items():
        by_normalized_label.setdefault(normalize(label), []).append(key)
        by_normalized_key.setdefault(normalize(key), []).append(key)
    fuzzy_buckets: dict[str, set[str]] = {}
    for normalized in (*by_normalized_label, *by_normalized_key):
        # An initial-bigram bucket keeps the exploratory report fast enough to
        # run in `make validate`; cross-language/exonym matches stay TBD until
        # researched rather than being suggested on superficial similarity.
        fuzzy_buckets.setdefault(normalized[:2], set()).add(normalized)
    failures: list[str] = []
    candidates: list[dict[str, str]] = []
    for row in roster:
        capital = row["historical_capital"]
        current = row["map_capital"]
        if current != "TBD" and current not in names:
            failures.append(f"{row['tag']}: map_capital {current} is not a location with a base English name")
        query = normalize(capital)
        exact = list(dict.fromkeys(by_normalized_label.get(query, []) + by_normalized_key.get(query, [])))
        alias = ALIASES.get(query)
        if alias and alias in names:
            exact = [alias, *[value for value in exact if value != alias]]
        if exact:
            kind = "exact"
            choices = exact
        else:
            pool = sorted(
                value
                for value in fuzzy_buckets.get(query[:2], set())
                if abs(len(value) - len(query)) <= 6
            )
            labels = difflib.get_close_matches(query, pool, n=3, cutoff=0.68)
            keys = labels
            choices = list(dict.fromkeys(
                key
                for normalized in [*labels, *keys]
                for key in (by_normalized_label.get(normalized, []) + by_normalized_key.get(normalized, []))
            ))[:5]
            kind = "fuzzy" if choices else "none"
        candidates.append(
            {
                "tag": row["tag"],
                "historical_capital": capital,
                "current_map_capital": current,
                "match_kind": kind,
                "candidates": "; ".join(
                    f"{key} ({names[key]})" for key in choices
                ),
            }
        )
    return candidates, failures


def rendered() -> tuple[str, list[str]]:
    rows, failures = candidate_rows()
    fieldnames = ("tag", "historical_capital", "current_map_capital", "match_kind", "candidates")
    from io import StringIO

    handle = StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return handle.getvalue(), failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    expected, failures = rendered()
    if args.write:
        if not failures:
            OUTPUT.write_text(expected, encoding="utf-8-sig", newline="")
            print(f"capital_mapper: wrote {OUTPUT.relative_to(ROOT)}")
        else:
            print("capital_mapper: FAIL", file=sys.stderr)
            print("\n".join(f"  - {failure}" for failure in failures), file=sys.stderr)
            return 1
        return 0
    if not OUTPUT.is_file():
        failures.append(f"missing generated report {OUTPUT.relative_to(ROOT)}")
    elif OUTPUT.read_text(encoding="utf-8-sig") != expected:
        failures.append("capital candidate report is stale; run tools/capital_mapper.py --write")
    if failures:
        print("capital_mapper: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return 1
    rows, _ = candidate_rows()
    exact = sum(row["match_kind"] == "exact" for row in rows)
    fuzzy = sum(row["match_kind"] == "fuzzy" for row in rows)
    mapped = sum(row["current_map_capital"] != "TBD" for row in rows)
    print(f"capital_mapper: PASS ({mapped} mapped; {exact} exact candidates; {fuzzy} fuzzy candidates)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
