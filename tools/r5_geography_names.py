#!/usr/bin/env python3
"""Merge and validate source-led Round 5 AD 1 geography research shards."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/r5"
OUTPUT = DOCS / "geography_names.csv"
COVERAGE = DOCS / "geography_name_coverage.json"
CONFIG = ROOT / "config/local_paths.json"
SYMBOLS = ROOT / "docs/vanilla_symbols"
LOC_ROOT = ROOT / "main_menu/localization"
CLIENTS = (
    "english", "french", "german", "spanish", "polish", "russian",
    "turkish", "braz_por", "simp_chinese", "japanese", "korean",
)
FIELDS = (
    "granularity", "key", "parent", "kind", "ad1_name", "language",
    "method", "source", "confidence", "note", "unchanged_verified",
)
LEVELS = (
    ("continent", "continents.json"),
    ("subcontinent", "subcontinents.json"),
    ("region", "regions.json"),
    ("area", "areas.json"),
    ("province", "provinces.json"),
    ("location", "locations.json"),
)
KINDS_BY_LEVEL = {
    "continent": {"land", "marine"},
    "subcontinent": {"land", "marine"},
    "region": {"land", "marine"},
    "area": {"land", "marine"},
    "province": {"land", "marine", "sea"},
    "location": {"land", "sea", "lake"},
}
ASSIGNED_SHARD = re.compile(r"^names_(areas|provinces|locations)_(\d+)_(\d+)\.csv$")
LOC_LINE = re.compile(r'^\s*([^#\s][^:]*):(?:\d+)?\s+"(.*)"\s*$')
GENERIC_LABEL = re.compile(
    r"\b(?:communit(?:y|ies)|groups?|indigenous|unsettled)\b",
    re.IGNORECASE,
)
POSTCLASSICAL_LABEL = re.compile(
    r"\b(?:"
    r"Saint|Sainte|Victoria|Prince|Princess|King|Queen|George|Elizabeth|"
    r"James|Charles|"
    r"San Pedro|San Juan|San Gabriel|San Jacinto|Santa Cruz|Santa Barbara|"
    r"Prince Rupert|Victoria River|Victoria[- ]Nile|French[- ]River|"
    r"Flinders|Norman Gulf|Roebuck[- ]King"
    r")\b",
    re.IGNORECASE,
)
COLONIAL_GEOGRAPHY_LABEL = re.compile(
    r"\b(?:"
    r"Aberdeen|Alaska|America|American|Amazon|Australia|Australian|Baffin|"
    r"Baker|Basswood|Bering|Buchanan|Burdekin|Cabot|Canadian|Carnegie|"
    r"Caroline|Carpentaria|Charleston|Churchill|Colombia|"
    r"Colombian|Columbia|Cook|Cooper|Darling|Diamantina|Falkland|Fitzroy|"
    r"Cork|Cowan|Cree|Crescent Lake|Cross Lake|Florida|Fausse Pointe|Fraser|"
    r"Georgina|Greenland|Hudson|Iceland|Kimberley|Labrador|"
    r"Lynn|Mackenzie|Madeira|Magellan|Malheur|Mauritius|Mexico|Mexican|"
    r"Murchison|Murray|Nelson|New Zealand|Norton|Patagonia|Pennsylvania|"
    r"Peru|Peruvian|Schuylkill|Seward|Stuart|Tasman|Thompson|Uninhabited|"
    r"Unpeopled|Venezuela|Victoria|Whitsunday|Yukon|Zealandia"
    r")\b",
    re.IGNORECASE,
)
NUMERIC_SHORTCUT_LABEL = re.compile(r"(?:\d+|\b[IVXLCDM]{2,}\b)")
COMPASS_ABBREVIATION = re.compile(
    r"\b(?:N|S|E|W|NE|NW|SE|SW|NNE|NNW|ENE|ESE|SSE|SSW|WSW|WNW)\b"
)
GENERIC_ERA_FORMULA = re.compile(
    r"\b(?:Formative-Era|Iron-Age|Early-Historic|High-Wilds|Low-Wilds|"
    r"Mid-Wilds|Sand-Waste)\b",
    re.IGNORECASE,
)
LATIN_COMPASS_PROXY = re.compile(r"\b(?:Austral|Boreal|Hesperian)\b", re.IGNORECASE)
GENERIC_FALLBACK_NOUN = re.compile(r"\b(?:Tract|Wilds)\b", re.IGNORECASE)
MECHANICAL_MARITIME = re.compile(
    r"(?:\bWaters\b.{0,45}\bReach(?:es)?\b|"
    r"\bReach(?:es)?\b.{0,45}\bWaters\b|"
    r"\b(?:Cape|Coastal|Littoral|Mouth|Point|Promontory|Shore)\s+Reach\b)",
    re.IGNORECASE,
)
DISPLAY_SEPARATOR = re.compile(r"[,;:]|\s+-\s+")
POSITION_TERMS = {
    "central", "east", "eastern", "far", "high", "inner", "lower", "low",
    "mid", "near", "north", "northeast", "northeastern", "northern",
    "northwest", "northwestern", "outer", "south", "southeast",
    "southeastern", "southern", "southwest", "southwestern", "upper",
    "west", "western",
}
SEMANTIC_FAMILIES = {
    "arid": {"desert", "deserts", "dune", "dunes", "sandland", "sandlands", "wasteland", "wastelands"},
    "elevation": {"height", "heights", "highland", "highlands", "mountain", "mountains", "peak", "peaks", "upland", "uplands"},
    "river": {
        "river", "rivers", "riverland", "riverlands", "stream", "streams",
    },
    "landform": {
        "atoll", "atolls", "basin", "basins", "country", "forest", "forests",
        "height", "heights", "highland", "highlands", "hill", "hills", "island",
        "islands", "land", "lands", "lowland", "lowlands", "marsh", "marshes",
        "marshland", "marshlands", "mountain", "mountains", "plain", "plains",
        "plateau", "plateaus", "upland", "uplands", "woodland", "woodlands",
    },
    "waterbody": {
        "bay", "bays", "gulf", "gulfs", "lake", "lakes", "mare", "ocean",
        "oceans", "sea", "seas", "water", "waters",
    },
    "harbour": {
        "harbor", "harbors", "harbour", "harbours", "limen", "port", "ports",
        "portus", "roadstead", "roadsteads", "sea", "seas", "water", "waters",
    },
}
STACKED_COMPASS = re.compile(
    r"\b(?:north|south|east|west)[a-z]*-(?:north|south|east|west)[a-z]*\b",
    re.IGNORECASE,
)
DANGLING_PREPOSITION = re.compile(r"\b(?:at|in|of|on)\s*$", re.IGNORECASE)
LOWERCASE_FEATURE_SUFFIX = re.compile(
    r"\b(?:bay|basin|bight|channel|coast|country|current|forest|heights|hills|"
    r"highlands|island|islands|lands|lake|lowlands|marshes|marshlands|ocean|"
    r"offing|passage|plain|plains|plateau|range|sea|steppe|strait|uplands|"
    r"waters|woodland|woodlands)\s*$"
)
FORMULA_SPLIT = re.compile(r"\s+(?:-|–|—)\s+|:\s+")
TAUTOLOGY_TERMS = {
    "atoll", "bay", "basin", "cape", "channel", "coast", "delta",
    "desert", "estuary", "forest", "gulf", "highland", "hill", "lake",
    "land", "lowland", "marsh", "mountain", "ocean", "plain", "plateau",
    "reef", "river", "salt", "sea", "shore", "strait", "valley", "water",
}
PLACEHOLDER_LABEL = re.compile(r"(?:_SHORT\b|\b(?:TODO|TBD|placeholder)\b)", re.IGNORECASE)
SUSPICIOUS_RETAINED_ROOT_NOTE = re.compile(
    r"\b(?:medieval|modern|postdates?|later (?:city|name|settlement|town)|"
    r"without projecting (?:a )?later|before (?:a )?later)\b",
    re.IGNORECASE,
)
GENERIC_KEY_TOKENS = {
    "area", "basin", "bay", "cape", "central", "channel", "coast",
    "continent", "country", "current", "desert", "east", "eastern",
    "forest", "forests", "great", "gulf", "harbor", "harbour", "high",
    "highland", "highlands", "hill", "hills", "inner", "island", "islands",
    "lake", "lakes", "land", "lands", "low", "lower", "lowland",
    "lowlands", "marsh", "marshes", "middle", "mountain", "mountains",
    "north", "northeast", "northern", "northwest", "ocean", "outer",
    "plain", "plains", "plateau", "point", "province", "region", "river",
    "rivers", "sea", "south", "southeast", "southern", "southwest", "steppe",
    "strait", "sub", "upper", "upland", "uplands", "valley", "wasteland",
    "west", "western", "wetland", "wetlands", "wilds", "woodland",
    "woodlands", "woods", "zone", "zones",
}


def expected_sets() -> dict[str, tuple[str, ...]]:
    return {
        level: tuple(json.loads((SYMBOLS / filename).read_text(encoding="utf-8-sig")))
        for level, filename in LEVELS
    }


def expected_parents(expected: dict[str, tuple[str, ...]]) -> dict[tuple[str, str], str]:
    hierarchy = json.loads(
        (SYMBOLS / "geography_hierarchy.json").read_text(encoding="utf-8-sig")
    )
    parents: dict[tuple[str, str], str] = {
        ("continent", key): "world" for key in expected["continent"]
    }
    for index in range(1, len(LEVELS)):
        level = LEVELS[index][0]
        parent_level = LEVELS[index - 1][0]
        allowed = set(expected[level])
        for parent in expected[parent_level]:
            for child in hierarchy.get(parent, []):
                if child in allowed:
                    token = (level, child)
                    if token in parents:
                        raise ValueError(f"multiple {level} parents for {child}")
                    parents[token] = parent
        missing = sorted(key for key in allowed if (level, key) not in parents)
        if missing:
            raise ValueError(f"missing {level} parents: {missing[:12]}")
    return parents


def read_shard(path: Path) -> list[dict[str, str]]:
    payload = path.read_bytes()
    if payload.startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"{path.name}: research shards must be UTF-8 without BOM")
    if b"\r" in payload:
        raise ValueError(f"{path.name}: research shards must use LF line endings")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError(f"{path.name}: schema {reader.fieldnames} != {FIELDS}")
        return [{key: (value or "").strip() for key, value in row.items()} for row in reader]


def shard_assignment(path: Path, expected: dict[str, tuple[str, ...]]) -> set[tuple[str, str]] | None:
    if path.name == "names_coarse_continents_subcontinents.csv":
        return {
            (level, key)
            for level in ("continent", "subcontinent")
            for key in expected[level]
        }
    if path.name == "names_regions_a.csv":
        return {("region", key) for key in sorted(expected["region"])[:41]}
    if path.name == "names_regions_b.csv":
        return {("region", key) for key in sorted(expected["region"])[41:]}
    match = ASSIGNED_SHARD.match(path.name)
    if match:
        plural, first, last = match.groups()
        level = plural[:-1] if plural.endswith("s") else plural
        keys = sorted(expected[level])[int(first) - 1:int(last)]
        return {(level, key) for key in keys}
    return None


def shard_order(path: Path, expected: dict[str, tuple[str, ...]]) -> list[tuple[str, str]] | None:
    if path.name == "names_coarse_continents_subcontinents.csv":
        return [
            (level, key)
            for level in ("continent", "subcontinent")
            for key in expected[level]
        ]
    if path.name == "names_regions_a.csv":
        return [("region", key) for key in sorted(expected["region"])[:41]]
    if path.name == "names_regions_b.csv":
        return [("region", key) for key in sorted(expected["region"])[41:]]
    match = ASSIGNED_SHARD.match(path.name)
    if match:
        plural, first, last = match.groups()
        level = plural[:-1] if plural.endswith("s") else plural
        return [
            (level, key)
            for key in sorted(expected[level])[int(first) - 1:int(last)]
        ]
    return None


def normalized_label(value: str) -> str:
    folded = unicodedata.normalize("NFKD", value.casefold())
    comparable = folded.encode("ascii", errors="ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", comparable).strip()


def echoed_key_tokens(key: str, value: str) -> list[str]:
    key_words = {
        word for word in normalized_label(key).split()
        if len(word) >= 4 and word not in GENERIC_KEY_TOKENS and not word.isdigit()
    }
    value_words = set(normalized_label(value).split())
    return sorted(key_words & value_words)


def formula_tautology(value: str) -> list[str]:
    parts = FORMULA_SPLIT.split(value)
    if len(parts) < 2:
        return []
    seen: set[str] = set()
    repeated: set[str] = set()
    for part in parts:
        terms: set[str] = set()
        for word in re.findall(r"[A-Za-z]+", part.casefold()):
            if word == "waters":
                word = "water"
            elif word == "lands":
                word = "land"
            elif word == "estuaries":
                word = "estuary"
            elif word.endswith("s") and word[:-1] in TAUTOLOGY_TERMS:
                word = word[:-1]
            if word in TAUTOLOGY_TERMS:
                terms.add(word)
        repeated.update(seen & terms)
        seen.update(terms)
    return sorted(repeated)


def mechanical_formula(value: str) -> list[str]:
    words = re.findall(r"[A-Za-z]+", value.casefold())
    failures: list[str] = []
    positions = [word for word in words if word in POSITION_TERMS]
    if len(positions) >= 3:
        failures.append("stacked-position:" + ",".join(positions))
    for family, terms in SEMANTIC_FAMILIES.items():
        matches = [word for word in words if word in terms]
        if len(matches) >= 2:
            failures.append(f"semantic-{family}:" + ",".join(matches))
    return failures


def installed_names() -> dict[tuple[str, str], str]:
    game = Path(json.loads(CONFIG.read_text(encoding="utf-8-sig"))["game_dir"]) / "game"
    english = game / "main_menu/localization/english"
    paths = [
        (("continent", "subcontinent", "region"), english / "region_names_l_english.yml"),
        (("area",), english / "area_l_english.yml"),
        (("province",), english / "province_names_l_english.yml"),
        (("location",), *sorted((english / "location_names").glob("*.yml"))),
    ]
    values: dict[tuple[str, str], str] = {}
    for levels, *level_paths in paths:
      for path in level_paths:
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            match = LOC_LINE.match(line)
            if match:
                for level in levels:
                    values[(level, match.group(1))] = match.group(2)
    return values


def canonical_rows() -> tuple[list[dict[str, str]], dict[str, object]]:
    expected = expected_sets()
    parents = expected_parents(expected)
    vanilla = installed_names()
    source_catalog = (ROOT / "docs/world_1ad/SOURCES.md").read_text(encoding="utf-8-sig")
    level_order = {level: index for index, (level, _filename) in enumerate(LEVELS)}
    rows_by_token: dict[tuple[str, str], dict[str, str]] = {}
    failures: list[str] = []
    shard_files = sorted(
        path for path in DOCS.glob("names_*.csv")
        if path.name != OUTPUT.name and not path.name.startswith("names_holy")
    )
    for path in shard_files:
        rows = read_shard(path)
        token_order = [(row["granularity"], row["key"]) for row in rows]
        tokens = set(token_order)
        assigned = shard_assignment(path, expected)
        assigned_order = shard_order(path, expected)
        if assigned is None:
            failures.append(f"unrecognized research shard filename: {path.name}")
        elif tokens != assigned:
            failures.append(
                f"{path.name}: assigned-set mismatch missing={len(assigned - tokens)} "
                f"extra={len(tokens - assigned)}"
            )
        elif token_order != assigned_order:
            failures.append(f"{path.name}: rows are not in exact canonical key order")
        for row in rows:
            token = (row["granularity"], row["key"])
            if token in rows_by_token:
                failures.append(f"duplicate researched token {token} in {path.name}")
                continue
            if row["granularity"] not in expected or row["key"] not in expected.get(row["granularity"], ()):
                failures.append(f"{path.name}: unknown geography token {token}")
                continue
            canonical_parent = parents[token]
            if row["parent"] != canonical_parent:
                failures.append(
                    f"{path.name}: {token} parent {row['parent']!r} != {canonical_parent!r}"
                )
            for field in ("kind", "ad1_name", "language", "method", "source", "confidence", "note"):
                if not row[field]:
                    failures.append(f"{path.name}: {token} lacks {field}")
            if row["kind"] not in KINDS_BY_LEVEL[row["granularity"]]:
                failures.append(
                    f"{path.name}: {token} has invalid kind {row['kind']!r}"
                )
            if row["confidence"].lower() not in {"high", "medium", "low"}:
                failures.append(f"{path.name}: {token} has invalid confidence")
            unchanged = row["unchanged_verified"].lower() in {"1", "true", "yes"}
            if (
                normalized_label(row["key"]) == normalized_label(row["ad1_name"])
                and not unchanged
            ):
                failures.append(f"{path.name}: raw-key humanization for {token}")
            if GENERIC_LABEL.search(row["ad1_name"]):
                failures.append(f"{path.name}: generic Community/Group label for {token}")
            if POSTCLASSICAL_LABEL.search(row["ad1_name"]):
                failures.append(f"{path.name}: post-classical geography label for {token}")
            if COLONIAL_GEOGRAPHY_LABEL.search(row["ad1_name"]):
                failures.append(f"{path.name}: colonial/eponymic geography label for {token}")
            if NUMERIC_SHORTCUT_LABEL.search(row["ad1_name"]):
                failures.append(f"{path.name}: numeric shortcut geography label for {token}")
            if COMPASS_ABBREVIATION.search(row["ad1_name"]):
                failures.append(f"{path.name}: abbreviated compass geography label for {token}")
            if GENERIC_ERA_FORMULA.search(row["ad1_name"]):
                failures.append(f"{path.name}: generic era/formula geography label for {token}")
            if LATIN_COMPASS_PROXY.search(row["ad1_name"]):
                failures.append(f"{path.name}: Latinized compass proxy geography label for {token}")
            if GENERIC_FALLBACK_NOUN.search(row["ad1_name"]):
                failures.append(f"{path.name}: generic fallback-noun geography label for {token}")
            if MECHANICAL_MARITIME.search(row["ad1_name"]):
                failures.append(f"{path.name}: mechanical maritime geography label for {token}")
            if DISPLAY_SEPARATOR.search(row["ad1_name"]):
                failures.append(f"{path.name}: prose separator in geography label for {token}")
            if STACKED_COMPASS.search(row["ad1_name"]):
                failures.append(f"{path.name}: stacked compass geography label for {token}")
            if DANGLING_PREPOSITION.search(row["ad1_name"]):
                failures.append(f"{path.name}: dangling preposition in geography label for {token}")
            if "$" in row["ad1_name"]:
                failures.append(f"{path.name}: unresolved substitution in geography label for {token}")
            if LOWERCASE_FEATURE_SUFFIX.search(row["ad1_name"]):
                failures.append(f"{path.name}: lowercase feature suffix in geography label for {token}")
            if len(re.findall(r"\bof\b", row["ad1_name"], re.IGNORECASE)) >= 2:
                failures.append(f"{path.name}: chained-of prose geography label for {token}")
            repeated_terms = formula_tautology(row["ad1_name"])
            if repeated_terms:
                failures.append(
                    f"{path.name}: tautological geography label for {token}: "
                    f"{','.join(repeated_terms)}"
                )
            mechanical_terms = mechanical_formula(row["ad1_name"])
            if mechanical_terms:
                failures.append(
                    f"{path.name}: mechanical geography label for {token}: "
                    f"{';'.join(mechanical_terms)}"
                )
            # Map labels are read at several zoom levels.  Every label must fit
            # below thirty characters, using a complete compact anchor rather
            # than a clipped construction.
            if len(row["ad1_name"]) > 29:
                failures.append(
                    f"{path.name}: overlong geography label for {token} "
                    f"({len(row['ad1_name'])} characters)"
                )
            word_count = len(re.findall(r"[^\W\d_]+", row["ad1_name"], re.UNICODE))
            if word_count > 7:
                failures.append(
                    f"{path.name}: prose-like geography label for {token} "
                    f"({word_count} words)"
                )
            if "?" in row["ad1_name"] or "\ufffd" in row["ad1_name"]:
                failures.append(f"{path.name}: corrupted character in label for {token}")
            if (
                "â€" in row["ad1_name"]
                or "Â\u00a0" in row["ad1_name"]
                or re.search(r"Ã[^\x00-\x7f]", row["ad1_name"])
            ):
                failures.append(f"{path.name}: mojibake in label for {token}")
            if PLACEHOLDER_LABEL.search(row["ad1_name"]):
                failures.append(f"{path.name}: placeholder text in label for {token}")
            if token in vanilla and row["ad1_name"].casefold() == vanilla[token].casefold():
                if not unchanged:
                    failures.append(f"{path.name}: unexplained vanilla-equal name for {token}")
            elif unchanged:
                failures.append(f"{path.name}: false unchanged_verified flag for {token}")
            source_tokens = [part.strip() for part in row["source"].split(";")]
            historical_sources = [
                part for part in source_tokens
                if part != "GEO-PROXY" and not part.startswith("installed:")
            ]
            echoed = echoed_key_tokens(row["key"], row["ad1_name"])
            if echoed and not historical_sources:
                failures.append(
                    f"{path.name}: unsupported raw-key root for {token}: "
                    f"{','.join(echoed)}"
                )
            elif (
                echoed
                and SUSPICIOUS_RETAINED_ROOT_NOTE.search(row["note"])
                and row["confidence"].lower() != "high"
            ):
                failures.append(
                    f"{path.name}: insufficiently proven retained later root for "
                    f"{token}: {','.join(echoed)}"
                )
            if not all(
                part.startswith(("http://", "https://", "installed:"))
                or part == "GEO-PROXY"
                or re.search(rf"`{re.escape(part)}`|^- `{re.escape(part)}`:", source_catalog, re.MULTILINE)
                for part in source_tokens
            ):
                failures.append(f"{path.name}: unresolved source token for {token}")
            row["parent"] = canonical_parent
            row["unchanged_verified"] = "true" if unchanged else "false"
            rows_by_token[token] = row

    siblings: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for (level, key), row in rows_by_token.items():
        siblings[(level, row["parent"], row["ad1_name"].casefold())].append(key)
    for (level, parent, name), keys in siblings.items():
        if len(keys) > 1:
            failures.append(f"sibling collision {level}/{parent}/{name}: {sorted(keys)}")
    location_labels: dict[str, list[str]] = defaultdict(list)
    for (level, key), row in rows_by_token.items():
        if level == "location":
            location_labels[normalized_label(row["ad1_name"])].append(key)
    for name, keys in location_labels.items():
        if len(keys) > 1:
            failures.append(f"global location-label collision {name}: {sorted(keys)}")
    key_levels: dict[str, list[str]] = defaultdict(list)
    for level, values in expected.items():
        for key in values:
            key_levels[key].append(level)
    collision_report: dict[str, object] = {}
    for key, levels in sorted(key_levels.items()):
        if len(levels) < 2:
            continue
        researched = [rows_by_token[(level, key)] for level in levels if (level, key) in rows_by_token]
        labels = sorted({row["ad1_name"] for row in researched})
        resolved = len(researched) == len(levels) and len(labels) == 1
        collision_report[key] = {
            "levels": levels,
            "researched_levels": [row["granularity"] for row in researched],
            "labels": labels,
            "resolved": resolved,
        }
        if len(researched) > 1 and len(labels) != 1:
            failures.append(
                f"cross-level localization collision {key} has divergent labels {labels}"
            )
    if failures:
        raise ValueError("\n  - ".join(["geography research validation failed", *failures]))

    rows = sorted(
        rows_by_token.values(),
        key=lambda row: (level_order[row["granularity"]], row["key"]),
    )
    counts = Counter(row["granularity"] for row in rows)
    total_expected = sum(len(values) for values in expected.values())
    report: dict[str, object] = {
        "complete": len(rows) == total_expected,
        "researched_rows": len(rows),
        "expected_rows": total_expected,
        "distinct_researched_keys": len({row["key"] for row in rows}),
        "expected_distinct_keys": len({key for values in expected.values() for key in values}),
        "levels": {
            level: {"researched": counts[level], "expected": len(expected[level])}
            for level, _filename in LEVELS
        },
        "cross_level_collisions": collision_report,
        "shards": [path.name for path in shard_files],
    }
    return rows, report


def csv_bytes(rows: list[dict[str, str]]) -> bytes:
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return handle.getvalue().encode("utf-8-sig")


def coverage_bytes(report: dict[str, object]) -> bytes:
    return (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8")


def externally_owned_keys(client: str) -> set[str]:
    owned: set[str] = set()
    own_path = localization_path(client)
    for path in sorted((LOC_ROOT / client).rglob("*.yml")):
        if path == own_path:
            continue
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            match = LOC_LINE.match(line)
            if match:
                owned.add(match.group(1))
    return owned


def localization_bytes(
    client: str,
    rows: list[dict[str, str]],
    externally_owned: set[str],
) -> bytes:
    values: dict[str, str] = {}
    for row in rows:
        prior = values.get(row["key"])
        if prior is not None and prior != row["ad1_name"]:
            raise ValueError(
                f"cross-level key {row['key']} cannot localize both {prior!r} "
                f"and {row['ad1_name']!r}"
            )
        values[row["key"]] = row["ad1_name"]
    lines = [f"l_{client}:"]
    for key, value in values.items():
        if key in externally_owned:
            continue
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f' {key}:0 "{escaped}"')
    return ("\n".join(lines) + "\n").encode("utf-8-sig")


def localization_path(client: str) -> Path:
    return LOC_ROOT / client / f"zzz_antq_r5_geography_l_{client}.yml"


def effective_mod_localization(client: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for path in sorted((LOC_ROOT / client).rglob("*.yml")):
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            match = LOC_LINE.match(line)
            if match:
                values[match.group(1)] = match.group(2)
    return values


def localization_owners(client: str) -> dict[str, list[Path]]:
    owners: dict[str, list[Path]] = defaultdict(list)
    for path in sorted((LOC_ROOT / client).rglob("*.yml")):
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            match = LOC_LINE.match(line)
            if match:
                owners[match.group(1)].append(path)
    return owners


def write_upstream_location_owners() -> None:
    from generate_dynamic_names import outputs as dynamic_outputs
    from generate_m4_location_name_corrections import (
        correction_entries,
        outputs as correction_outputs,
    )

    for path, (content, encoding) in dynamic_outputs().items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding=encoding, newline="\n")
    for path, content in correction_outputs(correction_entries()).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def write() -> None:
    rows, report = canonical_rows()
    OUTPUT.write_bytes(csv_bytes(rows))
    COVERAGE.write_bytes(coverage_bytes(report))
    write_upstream_location_owners()
    for client in CLIENTS:
        path = localization_path(client)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(localization_bytes(client, rows, externally_owned_keys(client)))
    print(
        f"r5_geography_names: merged {len(rows)}/{report['expected_rows']} sourced rows "
        f"and wrote {len(CLIENTS)} localization mirrors"
    )


def check() -> None:
    rows, report = canonical_rows()
    if not OUTPUT.is_file() or OUTPUT.read_bytes() != csv_bytes(rows):
        raise ValueError(f"stale {OUTPUT.relative_to(ROOT)}")
    if not COVERAGE.is_file() or COVERAGE.read_bytes() != coverage_bytes(report):
        raise ValueError(f"stale {COVERAGE.relative_to(ROOT)}")
    reference: bytes | None = None
    for client in CLIENTS:
        path = localization_path(client)
        expected = localization_bytes(client, rows, externally_owned_keys(client))
        if not path.is_file() or path.read_bytes() != expected:
            raise ValueError(f"stale {path.relative_to(ROOT)}")
        normalized = expected.replace(f"l_{client}:".encode(), b"l_CLIENT:")
        if reference is None:
            reference = normalized
        elif normalized != reference:
            raise ValueError(f"geography localization diverges for {client}")
        owners = localization_owners(client)
        ownership_failures = [
            row["key"] for row in rows
            if len(owners.get(row["key"], ())) != 1
        ]
        if ownership_failures:
            raise ValueError(
                f"{client}: researched geography keys do not have exactly one "
                f"localization owner {ownership_failures[:12]}"
            )
        effective = effective_mod_localization(client)
        mismatches = [
            row["key"] for row in rows
            if effective.get(row["key"]) != row["ad1_name"]
        ]
        if mismatches:
            raise ValueError(
                f"{client}: later localization overrides researched geography "
                f"{mismatches[:12]}"
            )
    print(
        f"r5_geography_names: PASS ({len(rows)}/{report['expected_rows']} sourced "
        f"hierarchy rows; 11 clients; complete={report['complete']})"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        write()
    if args.check or not args.write:
        check()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(f"r5_geography_names: FAIL\n  - {exc}", file=sys.stderr)
        raise SystemExit(1)
