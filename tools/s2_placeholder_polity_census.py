#!/usr/bin/env python3
"""Generate and validate the remaining player-facing placeholder-polity census."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "docs/world_1ad/polities.csv"
TAG_MAP = ROOT / "docs/world_1ad/tag_map.json"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
LEDGER = ROOT / "docs/m12/placeholder_polity_census.csv"
LANGUAGES = (
    "english", "french", "german", "spanish", "polish", "russian",
    "braz_por", "simp_chinese", "japanese", "korean", "turkish",
)
PLACEHOLDER = re.compile(
    r"\b(?:societies|land of|generic|placeholder)\b",
    re.IGNORECASE,
)
FIELDS = (
    "design_tag", "engine_tag", "name", "region", "map_capital",
    "location_count", "source", "confidence",
)


def csv_rows(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8-sig")
    payload = "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith("#")
    )
    return list(csv.DictReader(io.StringIO(payload)))


def expected() -> tuple[list[dict[str, str]], list[str]]:
    failures: list[str] = []
    roster = csv_rows(ROSTER)
    ownership = csv_rows(OWNERSHIP)
    counts = Counter(row["tag"] for row in ownership)
    tag_map = {
        row["design_tag"]: row["engine_tag"]
        for row in json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))["entries"]
    }
    rows: list[dict[str, str]] = []
    for polity in roster:
        if not PLACEHOLDER.search(polity["name"]):
            continue
        tag = polity["tag"]
        if tag not in tag_map:
            failures.append(f"{tag} lacks a collision-safe engine tag")
            continue
        if counts[tag] < 1:
            failures.append(f"{tag} placeholder frame has no owned locations")
        if polity["confidence"] not in {"secure", "contested"} or not polity["source"]:
            failures.append(f"{tag} placeholder frame lacks source/confidence metadata")
        rows.append({
            "design_tag": tag,
            "engine_tag": tag_map[tag],
            "name": polity["name"],
            "region": polity["region"],
            "map_capital": polity["map_capital"],
            "location_count": str(counts[tag]),
            "source": polity["source"],
            "confidence": polity["confidence"],
        })
    rows.sort(key=lambda row: (-int(row["location_count"]), row["design_tag"]))

    for language in LANGUAGES:
        path = ROOT / (
            f"main_menu/localization/{language}/antq_m3_countries_l_{language}.yml"
        )
        text = path.read_text(encoding="utf-8-sig")
        for row in rows:
            key = row["engine_tag"]
            match = re.search(
                rf'(?m)^\s*{re.escape(key)}:\s+"(?P<value>[^"]*)"', text
            )
            if match is None:
                failures.append(f"{language} lacks placeholder census key {key}")
            elif not PLACEHOLDER.search(match.group("value")):
                failures.append(
                    f"{language} {key} diverges from roster placeholder classification"
                )
    return rows, failures


def render(rows: list[dict[str, str]]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        rows, failures = expected()
        content = render(rows)
        if args.write and not failures:
            LEDGER.parent.mkdir(parents=True, exist_ok=True)
            LEDGER.write_text(content, encoding="utf-8-sig", newline="")
            print(
                "s2_placeholder_polity_census: wrote "
                f"{LEDGER.relative_to(ROOT)} ({len(rows)} placeholders)"
            )
            return 0
        if args.check:
            if not LEDGER.is_file():
                failures.append(f"missing {LEDGER.relative_to(ROOT)}")
            elif LEDGER.read_text(encoding="utf-8-sig") != content:
                failures.append(f"stale {LEDGER.relative_to(ROOT)}")
        if failures:
            print("s2_placeholder_polity_census: FAIL")
            for failure in failures:
                print(f"  - {failure}")
            return 1
        largest = max((int(row["location_count"]) for row in rows), default=0)
        print(
            "s2_placeholder_polity_census: PASS "
            f"({len(rows)} remaining placeholders; largest {largest}; "
            "11-client localization)"
        )
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"s2_placeholder_polity_census: FAIL\n  - {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
