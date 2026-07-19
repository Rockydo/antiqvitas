#!/usr/bin/env python3
"""Match unresolved roster capitals to the cached official Pleiades CSV."""

from __future__ import annotations

import argparse
import csv
import difflib
import gzip
import re
import unicodedata
from collections import defaultdict
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "docs/world_1ad/polities.csv"
SOURCE = ROOT / ".cache/pleiades/pleiades-places-latest.csv.gz"
OUTPUT = ROOT / "docs/world_1ad/pleiades_capital_candidates.csv"
WORD = re.compile(r"[a-z0-9]+")

# Scholarly/transliteration variants used only to find a Pleiades record; the
# final coordinate and local-map key remain an explicit reviewed roster edit.
ALIASES = {
    "roma": "rome",
    "caesarea philippi": "caesarea paneas",
    "artaxata": "artaxata",
    "gungnae": "gungnae",
    "ura iyur": "uraiyur",
}


def normalize(value: str) -> str:
    return " ".join(WORD.findall(unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()))


def title_forms(value: str) -> set[str]:
    return {normalize(part) for part in re.split(r"[/,;()]", value) if normalize(part)}


def dataset() -> tuple[list[dict[str, str]], dict[str, set[int]]]:
    entries: list[dict[str, str]] = []
    index: dict[str, set[int]] = defaultdict(set)
    with gzip.open(SOURCE, "rt", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            title = row.get("title", "")
            if not title or not row.get("reprLat") or not row.get("reprLong"):
                continue
            entry = {
                "title": title,
                "lat": row["reprLat"],
                "lon": row["reprLong"],
                "precision": row.get("locationPrecision", ""),
                "period": row.get("timePeriodsRange", ""),
                "path": row.get("path", ""),
                "forms": " | ".join(sorted(title_forms(title))),
            }
            position = len(entries)
            entries.append(entry)
            for token in set(normalize(title).split()):
                if len(token) >= 4:
                    index[token].add(position)
    return entries, index


def score(query: str, entry: dict[str, str]) -> float:
    choices = title_forms(entry["title"])
    return max(difflib.SequenceMatcher(None, query, value).ratio() for value in choices)


def rendered() -> str:
    if not SOURCE.is_file():
        raise FileNotFoundError(f"missing cached source {SOURCE}; see docs/world_1ad/SOURCES.md")
    with ROSTER.open(encoding="utf-8-sig", newline="") as handle:
        roster = list(csv.DictReader(handle))
    entries, index = dataset()
    output: list[dict[str, str]] = []
    for row in roster:
        if row["map_capital"] != "TBD":
            continue
        historical = row["historical_capital"]
        query = normalize(ALIASES.get(historical.lower(), historical))
        tokens = [token for token in query.split() if len(token) >= 4]
        candidates = set().union(*(index.get(token, set()) for token in tokens)) if tokens else set()
        ranked = sorted(
            ((score(query, entries[position]), entries[position]) for position in candidates),
            key=lambda item: (-item[0], item[1]["title"]),
        )[:5]
        rendered_candidates = "; ".join(
            f"{entry['title']} [{entry['lat']},{entry['lon']}; {entry['precision']}; {entry['period']}; {entry['path']}; {value:.2f}]"
            for value, entry in ranked
            if value >= 0.36
        )
        output.append(
            {
                "tag": row["tag"],
                "historical_capital": historical,
                "roster_source": row["source"],
                "pleiades_candidates": rendered_candidates,
            }
        )
    stream = StringIO(newline="")
    stream.write("# Source: Pleiades places CSV snapshot downloaded 2026-07-19; candidates require human-agent review.\n")
    writer = csv.DictWriter(
        stream,
        fieldnames=("tag", "historical_capital", "roster_source", "pleiades_candidates"),
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(output)
    return stream.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if not args.write:
        parser.error("provide --write")
    text = rendered()
    OUTPUT.write_text(text, encoding="utf-8-sig", newline="")
    print(f"pleiades_candidates: wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
