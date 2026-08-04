#!/usr/bin/env python3
"""Produce readable, collision-free AD 1 map labels without character clipping.

The Round-5 ledger deliberately recorded rich cultural and geographic context in
the display value.  Map text needs a concise spoken name instead: this tool
selects complete source words (usually its ancient/local anchor), never slices a
word, and retains longer contextual alternatives only when required to separate
map labels.
"""

from __future__ import annotations

import argparse
import csv
import io
import re
import subprocess
import sys
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from r5_geography_names import (
    DANGLING_PREPOSITION,
    DISPLAY_SEPARATOR,
    DOCS,
    FIELDS,
    GENERIC_LABEL,
    MECHANICAL_MARITIME,
    PLACEHOLDER_LABEL,
    echoed_key_tokens,
    formula_tautology,
    installed_names,
    mechanical_formula,
    normalized_label,
    read_shard,
)


ROOT = Path(__file__).resolve().parents[1]
LIMIT = 29
SHARDS = tuple(sorted(DOCS.glob("names_*.csv")))
WORD = re.compile(r"\S+")
LEADING = {
    "central", "coastal", "eastern", "far", "headwater", "inner", "lower",
    "medial", "middle", "northern", "northeastern", "northwestern", "outer",
    "southern", "southeastern", "southwestern", "upper", "western", "windward",
    "leeward", "outlying",
}
TRAILING = {
    "basin", "bench", "bight", "coast", "country", "crossing", "delta", "dunes",
    "fairway", "fields", "forest", "glade", "grasslands", "heath", "heights", "highlands", "hills",
    "hinterland", "interior", "lands", "lowlands", "marsh", "marshes", "moor", "offing",
    "oases", "open", "passage", "pastures", "plain", "plains", "plateau", "range",
    "reach", "ridges", "riverlands", "routes", "scrub", "sea", "seaway", "settlements",
    "sound", "steppe", "taiga", "terraces", "timberline", "tundra", "uplands", "valleys",
    "waters", "wetlands", "woodland", "woodlands",
}
CONNECTORS = {"and", "at", "de", "del", "des", "in", "of", "the", "to"}
DIRECTION = {
    "central": "Central", "eastern": "East", "northern": "North",
    "northeastern": "Northeast", "northwestern": "Northwest",
    "southern": "South", "southeastern": "Southeast",
    "southwestern": "Southwest", "western": "West", "windward": "Windward",
    "leeward": "Leeward",
}
FEATURE_SYNONYM = {
    "grasslands": "Steppe", "highlands": "Heights", "lowlands": "Vale",
    "marshlands": "Marsh", "woodlands": "Woods", "waters": "Sea",
    "hinterland": "March", "plains": "Plain", "valleys": "Vale",
}
# Direction and terrain prose are excluded above.  Other terms may be the sole
# attested local anchor in a sparse-region ledger, so they stay available.
NON_ANCHOR: set[str] = set()


def clean(words: list[str]) -> str:
    value = " ".join(words).strip(" -–—,:;")
    value = re.sub(r"\s+", " ", value)
    return value


@lru_cache(maxsize=None)
def _phrase_candidates(value: str) -> tuple[str, ...]:
    """Rank complete-word, meaningful alternatives from a rich ledger label."""
    surface_words = WORD.findall(value)
    words = list(surface_words)
    while words and words[0].casefold().strip("-–—") in LEADING:
        words.pop(0)
    while words and words[-1].casefold().strip("-–—") in TRAILING:
        words.pop()
    candidates: list[tuple[int, str]] = []

    def add(rank: int, candidate_words: list[str]) -> None:
        candidate = clean(candidate_words)
        if not candidate or len(candidate) > LIMIT:
            return
        lowered = candidate.casefold()
        if lowered.split()[0] in CONNECTORS or lowered.split()[-1] in CONNECTORS:
            return
        if not any(char.isalpha() for char in candidate):
            return
        candidates.append((rank, candidate))

    # Prefer the leading historic/local anchor, extending it only while it fits.
    for end in range(len(words), 0, -1):
        add(1000 + end, words[:end])
    # En-dash pairs commonly contain two attested neighboring communities; retain
    # either whole side before falling back to a later word sequence.
    for index, word in enumerate(words):
        if "–" in word or "—" in word:
            pieces = [piece for piece in re.split(r"[–—]", word) if piece]
            for piece in pieces:
                add(900, [piece])
            add(950, [word])
        if "-" in word and not word.startswith("-"):
            pieces = [piece for piece in word.split("-") if piece]
            for piece in pieces:
                add(800, [piece])
    # Complete contiguous phrases provide collision-safe alternatives; they are
    # sorted after the primary anchor so map names remain natural where possible.
    for start in range(len(words)):
        if words[start].casefold().strip("-–—") in LEADING | CONNECTORS | TRAILING:
            continue
        for end in range(len(words), start, -1):
            add(500 + (end - start), words[start:end])
    # Remove conjunctions and terrain-only prose when two neighboring ancient
    # anchors together make the clearest compact map name (for example,
    # "Dardania–Moesia Scordisci").
    anchor_words = [
        piece for word in words
        if word.casefold().strip("-–—") not in CONNECTORS | TRAILING | LEADING
        for piece in re.split(r"[-–—]", word) if piece
    ]
    for end in range(len(anchor_words), 1, -1):
        add(650 + end, anchor_words[:end])
    for first in range(len(anchor_words)):
        for second in range(first + 1, len(anchor_words)):
            add(625, [anchor_words[first], anchor_words[second]])
    # A few inherited research rows are intentionally pure directional terrain
    # adapters (for example, a previously unnamed southern lowland).  Retain a
    # complete directional terrain phrase rather than inventing or clipping one.
    for start in range(len(surface_words)):
        for end in range(len(surface_words), start, -1):
            phrase = surface_words[start:end]
            if any(word.casefold().strip("-–—") not in LEADING for word in phrase):
                add(100 + (end - start), phrase)
    direction = next(
        (DIRECTION[word.casefold().strip("-–—")] for word in surface_words
         if word.casefold().strip("-–—") in DIRECTION),
        "",
    )
    if direction:
        # Direction is meaningful only where the concise ancestral anchor would
        # otherwise collide with a neighboring map location.
        for rank, candidate in list(candidates):
            if rank >= 500:
                add(750, [direction, candidate])
    # Water and terrain nouns are short, readable disambiguators.  Attach one
    # only to an otherwise concise historic anchor when neighboring labels share
    # that anchor ("Fortunate-Isles Tideway", not a clipped sentence).
    suffixes = [
        word for word in surface_words
        if word.casefold().strip("-–—") in TRAILING
    ]
    for _rank, candidate in list(candidates):
        for suffix in suffixes:
            add(700, [candidate, suffix])
            synonym = FEATURE_SYNONYM.get(suffix.casefold().strip("-–—"))
            if synonym:
                add(675, [candidate, synonym])
    # A single unusually long compound cannot be silently abbreviated.
    if not candidates:
        raise ValueError(f"no complete-word compact label under {LIMIT}: {value!r}")
    chosen: dict[str, tuple[int, str]] = {}
    for rank, candidate in candidates:
        key = normalized_label(candidate)
        prior = chosen.get(key)
        if prior is None or rank > prior[0] or (rank == prior[0] and len(candidate) < len(prior[1])):
            chosen[key] = (rank, candidate)
    return tuple(item[1] for item in sorted(chosen.values(), key=lambda item: (-item[0], len(item[1]), item[1])))


def phrase_candidates(value: str) -> list[str]:
    return list(_phrase_candidates(value))


def head_rows(path: Path) -> list[dict[str, str]]:
    """Read the pre-compaction committed research shard without altering HEAD."""
    relative = path.relative_to(ROOT).as_posix()
    payload = subprocess.check_output(["git", "show", f"HEAD:{relative}"], cwd=ROOT)
    if payload.startswith(b"\xef\xbb\xbf") or b"\r" in payload:
        raise ValueError(f"HEAD:{relative} violates research-shard encoding")
    reader = csv.DictReader(io.StringIO(payload.decode("utf-8"), newline=""))
    if tuple(reader.fieldnames or ()) != FIELDS:
        raise ValueError(f"HEAD:{relative} has unexpected schema")
    return [{key: (value or "").strip() for key, value in row.items()} for row in reader]


def rows_by_shard(*, from_head: bool = False) -> dict[Path, list[dict[str, str]]]:
    reader = head_rows if from_head else read_shard
    return {path: reader(path) for path in SHARDS}


def acceptable(row: dict[str, str], candidate: str, vanilla: dict[tuple[str, str], str]) -> bool:
    """Keep all existing canonical-name guardrails during compaction."""
    normalized = normalized_label(candidate)
    if normalized == normalized_label(row["key"]):
        return False
    installed = vanilla.get((row["granularity"], row["key"]))
    if installed and candidate.casefold() == installed.casefold():
        return False
    if GENERIC_LABEL.search(candidate) or DISPLAY_SEPARATOR.search(candidate):
        return False
    if MECHANICAL_MARITIME.search(candidate) or DANGLING_PREPOSITION.search(candidate):
        return False
    if PLACEHOLDER_LABEL.search(candidate) or formula_tautology(candidate) or mechanical_formula(candidate):
        return False
    def anchors(value: str) -> list[str]:
        return [
            word for word in WORD.findall(value.casefold())
            if word.strip("-–—") not in LEADING | TRAILING | CONNECTORS | NON_ANCHOR
        ]
    # A rich source-led construction with two or more proper/local anchors may
    # lose terrain prose, but not collapse to a disconnected single adjective or
    # a bare ethnonym.  One-anchor forms remain valid for genuine single-name
    # places and waters.
    candidate_anchors = anchors(candidate)
    directional_anchor = any(
        word.casefold().strip("-–—") in DIRECTION
        for word in WORD.findall(candidate)
    )
    if (
        len(anchors(row["ad1_name"])) >= 2
        and len(candidate_anchors) < 2
        and not (directional_anchor and len(candidate_anchors) == 1)
    ):
        return False
    historical_sources = [
        part for part in row["source"].split(";")
        if part != "GEO-PROXY" and not part.startswith("installed:")
    ]
    if echoed_key_tokens(row["key"], candidate) and not historical_sources:
        return False
    return True


def compact(rows: list[dict[str, str]]) -> tuple[dict[int, str], dict[str, int]]:
    """Assign each over-limit label a unique complete-phrase alternative."""
    replacements: dict[int, str] = {}
    vanilla = installed_names()
    occupied_locations: set[str] = set()
    occupied_siblings: set[tuple[str, str, str]] = set()
    for index, row in enumerate(rows):
        label = row["ad1_name"]
        if len(label) > LIMIT:
            continue
        name = normalized_label(label)
        if row["granularity"] == "location":
            occupied_locations.add(name)
        occupied_siblings.add((row["granularity"], row["parent"], name))

    # All cross-level same-key collisions already share one label and must retain
    # one replacement.  Grouping them makes that invariant explicit.
    clusters: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        if len(row["ad1_name"]) > LIMIT:
            clusters[row["key"]].append(index)
    valid: dict[str, tuple[str, ...]] = {}
    for key, indices in clusters.items():
        values = {rows[index]["ad1_name"] for index in indices}
        if len(values) != 1:
            raise ValueError(f"cross-level key has divergent long labels: {key}")
        original = next(iter(values))
        valid[key] = tuple(
            candidate for candidate in phrase_candidates(original)
            if all(acceptable(rows[index], candidate, vanilla) for index in indices)
        )
        if not valid[key]:
            raise ValueError(f"no valid compact label under {LIMIT}: {key}={original!r}")
    ordered = sorted(
        clusters.values(),
        key=lambda indices: (len(valid[rows[indices[0]]["key"]]), rows[indices[0]]["key"]),
    )
    strategy: defaultdict[str, int] = defaultdict(int)
    for indices in ordered:
        values = {rows[index]["ad1_name"] for index in indices}
        if len(values) != 1:
            raise ValueError(f"cross-level key has divergent long labels: {rows[indices[0]]['key']}")
        original = values.pop()
        candidates = valid[rows[indices[0]]["key"]]
        selected = ""
        for candidate in candidates:
            normalized = normalized_label(candidate)
            if any(rows[index]["granularity"] == "location" and normalized in occupied_locations for index in indices):
                continue
            if any((rows[index]["granularity"], rows[index]["parent"], normalized) in occupied_siblings for index in indices):
                continue
            selected = candidate
            break
        if not selected:
            raise ValueError(
                f"no collision-free compact label under {LIMIT}: {rows[indices[0]]['key']}={values}"
            )
        strategy["anchor" if selected == candidates[0] else "contextual"] += len(indices)
        normalized = normalized_label(selected)
        for index in indices:
            replacements[index] = selected
            if rows[index]["granularity"] == "location":
                occupied_locations.add(normalized)
            occupied_siblings.add((rows[index]["granularity"], rows[index]["parent"], normalized))
    return replacements, dict(strategy)


def compacted_by_shard(*, from_head: bool = False) -> tuple[dict[Path, list[dict[str, str]]], dict[str, int], dict[Path, list[dict[str, str]]]]:
    grouped = rows_by_shard(from_head=from_head)
    flat: list[dict[str, str]] = []
    ownership: list[Path] = []
    for path in SHARDS:
        for row in grouped[path]:
            flat.append(dict(row))
            ownership.append(path)
    replacements, strategy = compact(flat)
    for index, value in replacements.items():
        flat[index]["ad1_name"] = value
    result: dict[Path, list[dict[str, str]]] = defaultdict(list)
    for path, row in zip(ownership, flat):
        result[path].append(row)
    return dict(result), strategy, grouped


def shard_bytes(rows: list[dict[str, str]]) -> bytes:
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return handle.getvalue().encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument(
        "--from-head",
        action="store_true",
        help="regenerate from the committed pre-compaction research ledger",
    )
    args = parser.parse_args()
    compacted, strategy, source = compacted_by_shard(from_head=args.from_head)
    changed = sum(
        sum(before["ad1_name"] != after["ad1_name"] for before, after in zip(source[path], compacted[path]))
        for path in SHARDS
    )
    # Only already-short labels are retained verbatim.  Every label at least 30
    # characters long is replaced by a collision-safe complete phrase of 29
    # characters or fewer.
    remaining = [
        row for rows in compacted.values() for row in rows if len(row["ad1_name"]) > LIMIT
    ]
    if remaining:
        raise ValueError(f"{len(remaining)} labels remain above {LIMIT}: {remaining[:3]}")
    if args.write:
        for path in SHARDS:
            path.write_bytes(shard_bytes(compacted[path]))
    print(f"r5_compact_geography_labels: {changed} compacted to <= {LIMIT}; {strategy}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        print(f"r5_compact_geography_labels: FAIL\n  - {error}", file=sys.stderr)
        raise SystemExit(1)
