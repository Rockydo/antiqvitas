#!/usr/bin/env python3
"""Build and exercise the Round-5 six-level geography runtime sample."""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "docs/r5/geography_names.csv"
LEDGER = ROOT / "docs/r5/geography_runtime_samples.csv"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
LEVELS = ("location", "province", "area", "region", "subcontinent", "continent")


def read_rows(path: Path) -> list[dict[str, str]]:
    lines = [
        line for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line and not line.startswith("#")
    ]
    return list(csv.DictReader(lines))


def sample_rows() -> list[dict[str, str]]:
    rows = read_rows(CANONICAL)
    by_token = {(row["granularity"], row["key"]): row for row in rows}
    owned = {row["location"] for row in read_rows(OWNERSHIP)}
    locations_by_region: dict[str, list[dict[str, str]]] = defaultdict(list)
    for location in (row for row in rows if row["granularity"] == "location"):
        province = by_token[("province", location["parent"])]
        area = by_token[("area", province["parent"])]
        region = by_token[("region", area["parent"])]
        locations_by_region[region["key"]].append(location)
    samples: list[dict[str, str]] = []
    confidence_order = {"high": 0, "medium": 1, "low": 2}
    kind_order = {"land": 0, "lake": 1, "sea": 2}
    for region in sorted(
        (row for row in rows if row["granularity"] == "region"),
        key=lambda row: row["key"],
    ):
        candidates = locations_by_region[region["key"]]
        location = min(
            candidates,
            key=lambda row: (
                0 if row["key"] in owned else 1,
                kind_order.get(row["kind"], 9),
                confidence_order.get(row["confidence"].casefold(), 9),
                len(row["ad1_name"]),
                row["key"],
            ),
        )
        chain = {"location": location}
        for level, parent_level in zip(LEVELS, LEVELS[1:]):
            chain[parent_level] = by_token[(parent_level, chain[level]["parent"])]
        samples.append({
            "sample": f"region_{len(samples) + 1:02d}",
            "region_key": region["key"],
            "location_key": location["key"],
            "location_kind": location["kind"],
            "owned": "yes" if location["key"] in owned else "no",
            **{
                f"{level}_name": chain[level]["ad1_name"]
                for level in LEVELS
            },
            "source": location["source"],
            "confidence": location["confidence"],
        })
    if len(samples) != 82 or len({row["region_key"] for row in samples}) != 82:
        raise RuntimeError("runtime ledger does not cover the exact 82-region union")
    return samples


def write_ledger(samples: list[dict[str, str]]) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(samples[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(samples)


def driver(*arguments: str) -> None:
    command = [sys.executable, "tools/gamedriver.py", *arguments]
    for attempt in range(1, 4):
        result = subprocess.run(command, cwd=ROOT, check=False)
        if result.returncode == 0:
            return
        if attempt < 3:
            print(
                f"DRIVER_RETRY {attempt}/3 after exit {result.returncode}: "
                f"{' '.join(arguments)}",
                flush=True,
            )
            time.sleep(2)
    result.check_returncode()


def launch_with_retry(retries: int) -> None:
    for attempt in range(1, retries + 1):
        result = subprocess.run(
            [sys.executable, "tools/gamedriver.py", "launch", "--mode", "mod"],
            cwd=ROOT,
            check=False,
        )
        if result.returncode == 0:
            return
        if result.returncode != 75:
            result.check_returncode()
        print(f"RUNTIME_DEFERRED shared EU5 slot {attempt}/{retries}", flush=True)
        time.sleep(15)
    raise RuntimeError("shared EU5 slot did not clear within bounded retries")


def capture(samples: list[dict[str, str]], session: str) -> None:
    # Camera.Goto resets the camera scale for every jump.  At that scale a
    # centre click selects the owning country or a neighbouring sea zone.
    # Re-pin every regional jump to maximum detail before selecting it.
    driver(
        "console", f"Camera.Goto {samples[0]['location_key']}",
        "--paste", "--settle", "0.5",
    )
    driver("key", "0x1B", "--settle", "0.3")
    driver("scroll", "40", "--x", "0.50", "--y", "0.52", "--settle", "1")
    for index, sample in enumerate(samples, start=1):
        location = sample["location_key"]
        capture_name = f"region_{index:02d}_{sample['region_key']}"
        existing = ROOT / "docs/screens" / session / f"{capture_name}.png"
        if existing.is_file():
            print(
                f"REGION_REUSE {index:02d}/82 {sample['region_key']} -> {existing}",
                flush=True,
            )
            continue
        driver("console", f"Camera.Goto {location}", "--paste", "--settle", "0.35")
        driver("key", "0x1B", "--settle", "0.2")
        driver("scroll", "40", "--x", "0.50", "--y", "0.52", "--settle", "0.6")
        driver(
            "click", "0.50", "0.52", "--settle", "0.35",
            "--capture", capture_name,
            "--session", session,
        )
        print(
            f"REGION_PASS {index:02d}/82 {sample['region_key']} -> {location}",
            flush=True,
        )
    driver("console", "Camera.Goto rome", "--paste", "--settle", "0.5")
    driver("key", "0x1B", "--settle", "0.3")
    driver(
        "scroll", "-40", "--x", "0.55", "--y", "0.50", "--settle", "1",
        "--capture", "zoom_1_continent", "--session", session,
    )
    for index, level in enumerate(LEVELS[-2::-1], start=2):
        driver(
            "scroll", "8", "--x", "0.55", "--y", "0.50", "--settle", "1",
            "--capture", f"zoom_{index}_{level}", "--session", session,
        )
def full_runtime(samples: list[dict[str, str]], session: str, retries: int) -> None:
    launch_with_retry(retries)
    try:
        driver(
            "wait", "--timeout", "300", "--minimum", "35",
            "--quiet-seconds", "20",
        )
        driver(
            "capture-new-game-loading", "--session", session,
            "--x", "0.14", "--y", "0.382", "--percentages", "2", "5",
            "--minimum-captures", "1", "--timeout", "480", "--interval", "0.05",
        )
        driver(
            "start-observer", "--session", session,
            "--country-selection-settle", "5", "--observer-enable-settle", "8",
            "--live-timeout", "90",
        )
        capture(samples, session)
    finally:
        subprocess.run(
            [sys.executable, "tools/gamedriver.py", "stop"],
            cwd=ROOT,
            check=False,
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--capture", action="store_true")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--slot-retries", type=int, default=20)
    parser.add_argument("--session", default="R5_GEOGRAPHY_RUNTIME_20260803")
    args = parser.parse_args()
    samples = sample_rows()
    if args.write:
        write_ledger(samples)
    elif not LEDGER.is_file():
        raise RuntimeError("runtime sample ledger is missing; run with --write")
    if args.full:
        full_runtime(samples, args.session, args.slot_retries)
    elif args.capture:
        capture(samples, args.session)
    print(
        f"r5_geography_runtime: PASS ({len(samples)} regions; six hierarchy levels)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
