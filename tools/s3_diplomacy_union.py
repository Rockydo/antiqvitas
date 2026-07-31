#!/usr/bin/env python3
"""Audit the complete mounted diplomacy/action union and ancientize retained text."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
from collections import Counter
from pathlib import Path

from dates import M2_MIRROR_LANGUAGES
import m12_system_quarantine as quarantine
import m9_diplomacy
from s3_diplomacy_text import ANCIENT_TEXT


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs/s3/diplomacy_union.csv"
SUMMARY = ROOT / "docs/s3/DIPLOMACY_UNION.md"
LOC_ROOT = ROOT / "main_menu/localization"
LANGUAGES = ("english", *M2_MIRROR_LANGUAGES)
SURFACES = {
    "country_interactions": "in_game/common/country_interactions",
    "generic_actions": "in_game/common/generic_actions",
    "casus_belli": "in_game/common/casus_belli",
    "peace_treaties": "in_game/common/peace_treaties",
    "subject_types": "in_game/common/subject_types",
    "scripted_diplomatic_objectives": (
        "in_game/common/scripted_diplomatic_objectives"
    ),
    "wargoals": "in_game/common/wargoals",
}
BANNED_VISIBLE = re.compile(
    r"\b("
    r"appanage|beylik|catholic|colon(?:y|ial)|condottier|crusad|"
    r"excommunicat|feudal|gun|hre|hussit|imperialis[mt]|jihad|"
    r"lutheran|mamluk|nationalis[mt]|ottoman|papal|protestant|"
    r"reformation|revolution|shogun|timurid|tordesillas"
    r")\b",
    re.IGNORECASE,
)


def root_keys(path: Path) -> list[str]:
    keys: list[str] = []
    depth = 0
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        code = quarantine.structural_code(line)
        match = quarantine.TOP_LEVEL_KEY.match(code)
        if depth == 0 and match:
            keys.append(match.group("key"))
        depth += quarantine.brace_delta(line)
    if depth != 0:
        raise ValueError(f"unbalanced script {path}")
    return keys


def installed_records() -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    retained = quarantine.RETAINED_ENGINE_ADAPTERS
    excluded = quarantine.EXCLUDED_BY_SURFACE
    for surface, relative in SURFACES.items():
        for filename, source in sorted(quarantine.mounted_files(relative).items()):
            if filename.casefold() == "readme.txt":
                continue
            for key in root_keys(source):
                if surface == "wargoals":
                    disposition = "backend_contract"
                    visible = "no"
                    note = "Not independently selectable; retained for CB/event references."
                elif filename in excluded.get(surface, set()):
                    if surface == "casus_belli":
                        disposition = "engine_internal"
                        visible = "no"
                        note = "Hardcoded or event-created CB; not player-created."
                    else:
                        disposition = "ancient_rewrite"
                        visible = "yes"
                        note = "Exact filename is maintained by an ANTIQVITAS rewrite."
                elif key in retained.get(surface, set()):
                    disposition = "retained_neutral"
                    visible = "yes"
                    note = "Installed mechanic is portable to AD 1 and explicitly allowlisted."
                else:
                    disposition = "quarantined"
                    visible = "no"
                    note = "Mounted post-antique or profile-unsafe definition is false-gated."
                records.append(
                    {
                        "origin": "installed",
                        "surface": surface,
                        "key": key,
                        "file": filename,
                        "disposition": disposition,
                        "player_visible": visible,
                        "localization": "installed",
                        "note": note,
                    }
                )
    return records


def custom_records() -> list[dict[str, str]]:
    records: list[dict[str, str]] = []

    def add(surface: str, key: str, filename: str, visible: bool, note: str) -> None:
        records.append(
            {
                "origin": "antiquitas",
                "surface": surface,
                "key": key,
                "file": filename,
                "disposition": "active_ancient" if visible else "dated_dormant",
                "player_visible": "yes" if visible else "no",
                "localization": "antiquitas",
                "note": note,
            }
        )

    for path in sorted((ROOT / "in_game/common/generic_actions").glob("antq*.txt")):
        text = path.read_text(encoding="utf-8-sig")
        for key in root_keys(path):
            pattern = re.compile(
                rf"(?ms)^\s*{re.escape(key)}\s*=\s*\{{.*?"
                r"^\s*potential\s*=\s*\{(?P<potential>.*?)^\s*\}"
            )
            match = pattern.search(text)
            if not match or not match.group("potential").strip():
                raise ValueError(f"{path.name}:{key} lacks a nonempty potential gate")
            add(
                "generic_actions",
                key,
                path.name,
                True,
                "Namespaced ancient action with an explicit availability gate.",
            )
    for record in m9_diplomacy.contracts():
        add(
            "subject_types",
            record.key,
            m9_diplomacy.SUBJECT_OUTPUT.name,
            True,
            "Ancient subject contract.",
        )
    for record in m9_diplomacy.cb_records():
        add(
            "casus_belli",
            record.key,
            m9_diplomacy.CB_OUTPUT.name,
            record.key not in m9_diplomacy.DORMANT_CB_KEYS,
            "Ancient CB; later unification contracts remain dormant until events.",
        )
    for record in m9_diplomacy.peace_records():
        add(
            "peace_treaties",
            record.key,
            m9_diplomacy.PEACE_OUTPUT.name,
            True,
            "Ancient subject or tribute settlement.",
        )
    for key in (
        "antq_punitive_superiority",
        "antq_raid_superiority",
        "antq_frontier_recovery",
        "antq_client_capital",
        "antq_tribute_capital",
        "antq_succession_capital",
        "antq_holy_superiority",
        "antq_unification_superiority",
    ):
        add(
            "wargoals",
            key,
            m9_diplomacy.WARGOAL_OUTPUT.name,
            False,
            "Backend objective used only by a namespaced ancient CB.",
        )
    return records


def localization_keys(directory: Path) -> set[str]:
    keys: set[str] = set()
    if not directory.is_dir():
        return keys
    pattern = re.compile(r"^\s*([^:#][^:]*)\s*:(?:\d+)?\s+")
    for path in directory.rglob("*.yml"):
        for line in path.read_text(
            encoding="utf-8-sig", errors="strict"
        ).splitlines()[1:]:
            match = pattern.match(line)
            if match:
                keys.add(match.group(1).strip())
    return keys


def mounted_localization_keys(language: str) -> set[str]:
    game = quarantine.game_root()
    keys = localization_keys(game / "main_menu/localization" / language)
    for package in sorted((game / "dlc").glob("*")):
        keys.update(
            localization_keys(
                package / "main_menu/localization" / language
            )
        )
    keys.update(localization_keys(LOC_ROOT / language))
    return keys


def localizations() -> dict[Path, str]:
    # Exact country-interaction mirrors are owned by m12_rank_presentation.py;
    # this audit verifies their canonical ancient text without duplicating keys.
    return {}


def rendered() -> tuple[str, str, dict[Path, str]]:
    records = installed_records() + custom_records()
    identities = [(row["origin"], row["surface"], row["key"]) for row in records]
    if len(identities) != len(set(identities)):
        raise ValueError("diplomacy union contains duplicate origin/surface/key rows")

    loc_outputs = localizations()
    for language in LANGUAGES:
        mod_keys = mounted_localization_keys(language)
        for path, content in loc_outputs.items():
            if path.parent.name != language:
                continue
            for line in content.splitlines()[1:]:
                mod_keys.add(line.split(":", 1)[0].strip())
        for row in records:
            if row["player_visible"] != "yes" or row["surface"] == "wargoals":
                continue
            if row["key"] not in mod_keys or f"{row['key']}_desc" not in mod_keys:
                raise ValueError(
                    f"{language} lacks label/description for "
                    f"{row['surface']}:{row['key']}"
                )

    english_values: dict[str, str] = {}
    value_pattern = re.compile(r'^\s*([^:#][^:]*)\s*:(?:\d+)?\s+"(.*)"\s*$')
    english_roots = [
        quarantine.game_root() / "main_menu/localization/english",
        LOC_ROOT / "english",
    ]
    english_roots.extend(
        package / "main_menu/localization/english"
        for package in sorted((quarantine.game_root() / "dlc").glob("*"))
    )
    for root in english_roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*.yml"):
            for line in path.read_text(encoding="utf-8-sig").splitlines()[1:]:
                match = value_pattern.match(line)
                if match:
                    english_values[match.group(1).strip()] = match.group(2)
    english_values.update(
        {
            field: value
            for key, pair in ANCIENT_TEXT.items()
            for field, value in ((key, pair[0]), (f"{key}_desc", pair[1]))
        }
    )
    for row in records:
        if row["player_visible"] != "yes":
            continue
        values = (
            english_values.get(row["key"], ""),
            english_values.get(f"{row['key']}_desc", ""),
        )
        if row["origin"] == "antiquitas" and not all(values):
            raise ValueError(f"visible ancient key {row['key']} lacks English text")
        if match := BANNED_VISIBLE.search(" ".join(values)):
            raise ValueError(
                f"visible diplomacy text {row['key']} contains {match.group(0)!r}"
            )

    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=tuple(records[0]),
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(
        sorted(records, key=lambda row: (row["surface"], row["origin"], row["key"]))
    )
    counts = Counter(
        (row["surface"], row["disposition"]) for row in records
    )
    visible = Counter(
        row["surface"] for row in records if row["player_visible"] == "yes"
    )
    summary = [
        "# Mounted Diplomacy Union",
        "",
        "Generated from the installed base+DLC filename union and ANTIQVITAS.",
        "",
        f"- {len(records):,} definitions classified.",
        f"- {sum(visible.values()):,} player-visible definitions.",
        f"- {sum(row['disposition'] == 'quarantined' for row in records):,} "
        "installed definitions false-gated.",
        f"- {len(ANCIENT_TEXT):,} retained interactions ancientized in all "
        f"{len(LANGUAGES)} clients.",
        "",
        "## Surface totals",
        "",
    ]
    for surface in SURFACES:
        total = sum(1 for row in records if row["surface"] == surface)
        dispositions = ", ".join(
            f"{disposition} {count}"
            for (candidate, disposition), count in sorted(counts.items())
            if candidate == surface
        )
        summary.append(
            f"- {surface}: {total:,}; visible {visible[surface]:,}; {dispositions}."
        )
    summary.extend(
        (
            "",
            "Wargoals remain backend contracts only. Hardcoded/event CBs remain",
            "resolvable but cannot be player-created. Every other inherited",
            "definition is either explicitly portable or false-gated.",
            "",
        )
    )
    return output.getvalue(), "\n".join(summary), loc_outputs


def outputs() -> dict[Path, tuple[str, str]]:
    ledger, summary, loc = rendered()
    result = {
        LEDGER: (ledger, "utf-8-sig"),
        SUMMARY: (summary, "utf-8"),
    }
    result.update({path: (value, "utf-8-sig") for path, value in loc.items()})
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        expected = outputs()
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"s3_diplomacy_union: FAIL\n  - {exc}")
        return 1
    if args.write:
        for path, (content, encoding) in expected.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding=encoding, newline="\n")
        print(
            f"s3_diplomacy_union: wrote {len(expected)} outputs / "
            f"{sum(1 for _ in csv.DictReader(io.StringIO(expected[LEDGER][0])))} rows"
        )
        return 0
    failures = [
        f"stale or missing {path.relative_to(ROOT)}"
        for path, (content, encoding) in expected.items()
        if not path.is_file() or path.read_text(encoding=encoding) != content
    ]
    if failures:
        print("s3_diplomacy_union: FAIL\n  - " + "\n  - ".join(failures))
        return 1
    print(f"s3_diplomacy_union: PASS ({len(expected)} outputs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
