#!/usr/bin/env python3
"""Inventory every displayed location name inside the generated AD 1 Roman realm.

The audit is intentionally read-only. It resolves the same source precedence as
``generate_dynamic_names.py`` and emits a compact Roman-only table that can be
reviewed without loading the 13,000-row ownership file through GitHub's UI.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
DYNAMIC = ROOT / "docs/m4/dynamic_location_names.csv"
CORRECTIONS = ROOT / "docs/m4/location_name_corrections.csv"
ROOT_FALLBACKS = ROOT / "docs/m4/tier3_map_name_fallbacks.csv"

OUTPUT_FIELDS = (
    "location",
    "historical_name",
    "layer",
    "anchor_kind",
    "culture",
    "source",
    "confidence",
    "review_status",
    "audit_flags",
    "note",
)

# These terms are not an automatic rejection. They identify entries whose
# Pleiades resource title is likely a modern excavation/site label rather than
# an ancient name resource and therefore require name-level verification.
MODERN_SITE_RE = re.compile(
    r"(?:\b(?:caer|castle|chateau|château|church|fort|henchir|kodra|monte|mont|"
    r"nossa|qal(?:a|at)|san|santa|santo|sidi|steinheim|tell|tel|tulul|umm)\b|"
    r"\b(?:di|della|des|les|sur|veche)\b|(?:abad|abad$)|(?:grad|gorod)$|"
    r"(?:\bS\.|\bSt\.)\s)",
    re.IGNORECASE,
)
ARCHAEOLOGY_RE = re.compile(
    r"\b(?:archaeological|excavation|necropolis|tomb|temple|villa|site|ruins?)\b",
    re.IGNORECASE,
)


def rows(path: Path, *, comments: bool = False) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        lines = (line for line in handle if not comments or not line.startswith("#"))
        return list(csv.DictReader(lines))


def roman_locations() -> list[str]:
    result = sorted(
        row["location"].strip()
        for row in rows(OWNERSHIP, comments=True)
        if row.get("tag", "").strip() == "ROM" and row.get("location", "").strip()
    )
    if not result:
        raise ValueError("ownership_resolved.csv contains no ROM locations")
    duplicates = [key for key, count in Counter(result).items() if count > 1]
    if duplicates:
        raise ValueError("duplicate ROM ownership rows: " + ", ".join(duplicates))
    return result


def unique_by_location(path: Path) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for number, row in enumerate(rows(path), start=2):
        location = row.get("location", "").strip()
        if not location:
            raise ValueError(f"{path.relative_to(ROOT)}:{number}: blank location")
        if location in result:
            raise ValueError(f"{path.relative_to(ROOT)}:{number}: duplicate {location}")
        result[location] = {key: (value or "").strip() for key, value in row.items()}
    return result


def layer_for(entry: dict[str, str]) -> str:
    kind = entry.get("anchor_kind", "")
    source = entry.get("source", "")
    if kind == "tier2":
        if ";T2W" in source:
            return "tier2_wide"
        return "tier2_bounded"
    return {
        "capital": "capital",
        "curated": "curated",
        "qualified": "qualified",
        "tier2_remote": "tier2_remote",
        "tier2_far": "tier2_far",
        "tier2_ultra": "tier2_ultra",
        "tier3": "tier3_population",
    }.get(kind, kind or "unknown")


def flags_for(name: str, layer: str, source: str, confidence: str) -> tuple[str, ...]:
    flags: list[str] = []
    if confidence == "tier3" or layer.startswith("tier3"):
        flags.append("synthetic")
    if layer in {"tier2_far", "tier2_ultra"}:
        flags.append("unsafe_distance")
    elif layer == "tier2_remote":
        flags.append("remote_proxy")
    if layer.startswith("tier2") and MODERN_SITE_RE.search(name):
        flags.append("possible_modern_site_title")
    if ARCHAEOLOGY_RE.search(name):
        flags.append("archaeology_descriptor")
    if source.startswith("T3M:"):
        flags.append("installed_label_derivative")
    return tuple(dict.fromkeys(flags))


def status_for(layer: str, confidence: str, flags: tuple[str, ...]) -> str:
    severe = {"unsafe_distance", "possible_modern_site_title", "archaeology_descriptor"}
    if severe.intersection(flags):
        return "replace"
    if confidence == "tier3" or layer.startswith("tier3"):
        return "review"
    if layer.startswith("tier2"):
        return "verify"
    return "retain"


def audit_rows() -> list[dict[str, str]]:
    corrections = unique_by_location(CORRECTIONS)
    dynamic = unique_by_location(DYNAMIC)
    roots = unique_by_location(ROOT_FALLBACKS)
    output: list[dict[str, str]] = []
    missing: list[str] = []
    for location in roman_locations():
        if location in corrections:
            entry = corrections[location]
            layer = "correction"
            anchor_kind = "correction"
            culture = entry.get("culture", "")
        elif location in dynamic:
            entry = dynamic[location]
            layer = layer_for(entry)
            anchor_kind = entry.get("anchor_kind", "")
            culture = entry.get("culture", "")
        elif location in roots:
            entry = roots[location]
            layer = "tier3_root"
            anchor_kind = "root"
            culture = ""
        else:
            missing.append(location)
            continue
        name = entry.get("historical_name", "").strip()
        source = entry.get("source", "").strip()
        confidence = entry.get("confidence", "").strip()
        if not name:
            raise ValueError(f"blank effective name for Roman location {location}")
        flags = flags_for(name, layer, source, confidence)
        output.append(
            {
                "location": location,
                "historical_name": name,
                "layer": layer,
                "anchor_kind": anchor_kind,
                "culture": culture,
                "source": source,
                "confidence": confidence,
                "review_status": status_for(layer, confidence, flags),
                "audit_flags": ";".join(flags),
                "note": entry.get("note", "").strip(),
            }
        )
    if missing:
        raise ValueError("Roman locations without an effective name: " + ", ".join(missing))
    return output


def write_csv(path: Path, values: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(values)


def summary(values: list[dict[str, str]]) -> dict[str, object]:
    return {
        "roman_locations": len(values),
        "layers": dict(sorted(Counter(row["layer"] for row in values).items())),
        "confidence": dict(sorted(Counter(row["confidence"] for row in values).items())),
        "review_status": dict(sorted(Counter(row["review_status"] for row in values).items())),
        "flags": dict(
            sorted(
                Counter(
                    flag
                    for row in values
                    for flag in row["audit_flags"].split(";")
                    if flag
                ).items()
            )
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        values = audit_rows()
        output_dir = args.output_dir.resolve()
        write_csv(output_dir / "roman_location_name_audit.csv", values)
        (output_dir / "roman_location_name_audit_summary.json").write_text(
            json.dumps(summary(values), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except (OSError, ValueError, csv.Error, json.JSONDecodeError) as exc:
        print(f"m4_roman_location_name_audit: FAIL\n  - {exc}")
        return 1
    print(f"m4_roman_location_name_audit: PASS ({len(values)} Roman locations)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
