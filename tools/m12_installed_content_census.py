#!/usr/bin/env python3
"""Pin and classify the complete installed total-conversion leakage surface.

``--write`` is the explicit review/acceptance action.  ``--check`` compares the
current base+DLC union, hashes, definitions, references, localization, and art
contracts to that accepted snapshot, so a game patch or DLC addition fails the
normal validation loop until it is deliberately classified.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
METADATA = ROOT / ".metadata/metadata.json"
REPORT = ROOT / "docs/m12/installed_content_leakage.json"
SUMMARY = ROOT / "docs/m12/INSTALLED_CONTENT_CENSUS.md"
POLITIES = ROOT / "docs/world_1ad/polities.csv"

SURFACES = {
    "ages": "in_game/common/age",
    "institutions": "in_game/common/institution",
    "advances": "in_game/common/advances",
    "units": "in_game/common/unit_types",
    "buildings": "in_game/common/building_types",
    "government_types": "in_game/common/government_types",
    "country_ranks": "in_game/common/country_ranks",
    "location_ranks": "in_game/common/location_ranks",
    "pop_types": "in_game/common/pop_types",
    "estate_privileges": "in_game/common/estate_privileges",
    "cabinet_actions": "in_game/common/cabinet_actions",
    "parliament_issues": "in_game/common/parliament_issues",
    "parliament_agendas": "in_game/common/parliament_agendas",
    "laws": "in_game/common/laws",
    "government_reforms": "in_game/common/government_reforms",
    "religious_aspects": "in_game/common/religious_aspects",
}
POLICY = {
    "ages": "engine_slot_adapter",
    "institutions": "exact_disabled_legacy",
    "advances": "exact_disabled_legacy",
    "units": "exact_hidden_legacy",
    "buildings": "exact_hidden_legacy",
    "government_types": "engine_adapter_pending_presentation",
    "country_ranks": "engine_adapter_period_presentation_complete",
    "location_ranks": "engine_adapter_pending_presentation",
    "pop_types": "engine_adapter_ancient_presentation_complete",
    "estate_privileges": "exact_disabled_legacy",
    "cabinet_actions": "exact_disabled_legacy",
    "parliament_issues": "exact_disabled_legacy",
    "parliament_agendas": "exact_disabled_legacy",
    "laws": "exact_disabled_legacy",
    "government_reforms": "exact_disabled_legacy",
    "religious_aspects": "exact_disabled_legacy",
}
EXACT_REQUIRED = {
    "ages",
    "institutions",
    "advances",
    "units",
    "buildings",
    "estate_privileges",
    "cabinet_actions",
    "parliament_issues",
    "parliament_agendas",
    "laws",
    "government_reforms",
    "religious_aspects",
}
VISIBLE_DEBT = {
    "government_types",
    "location_ranks",
}
FORBIDDEN = (
    "renaissance",
    "feudalism",
    "redcoat",
    "riflemen",
    "grenzer",
    "gunpowder",
    "colonial",
    "absolutism",
    "revolution",
    "enlightenment",
)
DEFINITION = re.compile(r"(?m)^([A-Za-z][A-Za-z0-9_]*)\s*=\s*\{")
INDENTED_DEFINITION = re.compile(
    r"(?m)^([ \t]+)([A-Za-z][A-Za-z0-9_]*)\s*=\s*\{"
)
REFERENCE = re.compile(
    r"(?m)^\s*(unlock_[a-z_]+|requires|age|copy_from|building|unit_type)"
    r"\s*=\s*\"?([A-Za-z0-9_:.|-]+)"
)
TEXTURE = re.compile(r"gfx/[A-Za-z0-9_./-]+\.dds")
ICON = re.compile(r"(?m)^\s*icon\s*=\s*\"?([A-Za-z0-9_./-]+)")
LOC = re.compile(r"(?m)^\s*([A-Za-z0-9_.-]+)\s*:")
TIP = re.compile(r"(?m)^\s*(LOADING_TIP_[A-Za-z0-9_]+)\s*:")
HISTORY_TRIGGER = re.compile(
    r"localization_key\s*=\s*(antq_country_history_[A-Za-z0-9_]+)"
    r"\s+trigger\s*=\s*\{\s*tag\s*=\s*([A-Za-z0-9_]+)\s*\}"
)
CLIENT_LANGUAGES = (
    "english",
    "french",
    "german",
    "spanish",
    "polish",
    "russian",
    "braz_por",
    "simp_chinese",
    "japanese",
    "korean",
    "turkish",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def config() -> dict[str, object]:
    return json.loads(CONFIG.read_text(encoding="utf-8-sig"))


def game_root() -> Path:
    return Path(str(config()["game_dir"])) / "game"


def mounted_files(relative: str, suffixes: tuple[str, ...]) -> dict[str, Path]:
    game = game_root()
    rel = Path(relative)
    roots = [game / rel]
    roots.extend(
        package / rel
        for package in sorted((game / "dlc").glob("*"))
        if package.is_dir()
    )
    mounted: dict[str, Path] = {}
    for directory in roots:
        if not directory.is_dir():
            continue
        for path in sorted(item for item in directory.rglob("*") if item.is_file()):
            if path.suffix.lower() in suffixes:
                mounted[path.relative_to(directory).as_posix()] = path
    return mounted


def source_record(surface: str, relative: str, source: Path) -> dict[str, object]:
    raw = source.read_bytes()
    text = raw.decode("utf-8-sig")
    definitions = sorted(set(DEFINITION.findall(text)))
    # One installed religious-aspect source currently indents its sole
    # top-level definition.  Recognize the shallowest indentation only, so
    # nested blocks are not promoted to definitions on every audited surface.
    if surface == "religious_aspects" and not definitions:
        indented = INDENTED_DEFINITION.findall(text)
        if indented:
            shallowest = min(len(indent.expandtabs(4)) for indent, _ in indented)
            definitions = sorted(
                {
                    key
                    for indent, key in indented
                    if len(indent.expandtabs(4)) == shallowest
                }
            )
    references = sorted(f"{kind}={value}" for kind, value in REFERENCE.findall(text))
    art = sorted(set(TEXTURE.findall(text)).union(ICON.findall(text)))
    mod = ROOT / SURFACES[surface] / relative
    mirrored = mod.is_file()
    status = POLICY.get(surface, "unclassified")
    if surface in EXACT_REQUIRED and definitions and not mirrored:
        status = "uncovered"
    elif not definitions:
        status = "installed_reference_document"
    if surface == "units" and mirrored and definitions:
        mounted_text = mod.read_text(encoding="utf-8-sig")
        unit_manifest = json.loads(
            (ROOT / "docs/m12/unit_quarantine_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        adapters = set(unit_manifest["engine_adapter_definitions"])
        expected_markers = len(set(definitions) - adapters)
        if (
            mounted_text.count("ANTIQVITAS installed-unit quarantine")
            != expected_markers
        ):
            status = "uncovered"
    if surface == "buildings" and mirrored and definitions:
        mounted_text = mod.read_text(encoding="utf-8-sig")
        building_manifest = json.loads(
            (ROOT / "docs/m5/building_quarantine_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        adapters = set(building_manifest["engine_adapter_definitions"])
        expected_markers = len(set(definitions) - adapters)
        if (
            mounted_text.count("ANTIQVITAS installed-building quarantine")
            != expected_markers
        ):
            status = "uncovered"
    return {
        "relative": relative,
        "source": str(source),
        "source_sha256": sha256(raw),
        "mod_mirror": mod.relative_to(ROOT).as_posix() if mirrored else None,
        "mod_sha256": sha256(mod.read_bytes()) if mirrored else None,
        "status": status,
        "definition_count": len(definitions),
        "definitions": definitions,
        "reference_count": len(references),
        "references_sha256": sha256("\n".join(references).encode("utf-8")),
        "art_reference_count": len(art),
        "art_references_sha256": sha256("\n".join(art).encode("utf-8")),
    }


def localization_contract() -> dict[str, object]:
    loading = mounted_files(
        "loading_screen/localization/english", (".yml",)
    )
    tips: set[str] = set()
    for source in loading.values():
        tips.update(TIP.findall(source.read_text(encoding="utf-8-sig")))
    tip_targets = (
        ROOT / "loading_screen/localization/english/load_tips_l_english.yml",
        ROOT / "main_menu/localization/english/load_tips_l_english.yml",
    )
    overridden: set[str] = set()
    for target in tip_targets:
        if target.is_file():
            overridden.update(TIP.findall(target.read_text(encoding="utf-8-sig")))

    history_source = (
        game_root()
        / "main_menu/localization/english/country_history_l_english.yml"
    )
    history_keys = (
        sorted(set(LOC.findall(history_source.read_text(encoding="utf-8-sig"))))
        if history_source.is_file()
        else []
    )
    history_target = (
        ROOT / "main_menu/localization/english/country_history_l_english.yml"
    )
    history_override_keys = (
        sorted(set(LOC.findall(history_target.read_text(encoding="utf-8-sig"))))
        if history_target.is_file()
        else []
    )
    history_selector = (
        ROOT / "in_game/common/customizable_localization/country_history.txt"
    )
    history_triggers = (
        sorted(
            (tag, key)
            for key, tag in HISTORY_TRIGGER.findall(
                history_selector.read_text(encoding="utf-8-sig")
            )
        )
        if history_selector.is_file()
        else []
    )
    history_ledger = ROOT / "docs/m12/country_history_agendas.csv"
    history_rows: list[dict[str, str]] = []
    if history_ledger.is_file():
        with history_ledger.open(encoding="utf-8-sig", newline="") as handle:
            history_rows = list(csv.DictReader(handle))
    expected_history = sorted(
        (row.get("engine_tag", ""), row.get("localization_key", ""))
        for row in history_rows
    )
    with POLITIES.open(encoding="utf-8-sig", newline="") as handle:
        roster_count = sum(1 for _ in csv.DictReader(handle))
    expected_keys = {key for _, key in expected_history}
    client_coverage: dict[str, int] = {}
    clients_complete = True
    for language in CLIENT_LANGUAGES:
        target = (
            ROOT
            / "main_menu"
            / "localization"
            / language
            / f"country_history_l_{language}.yml"
        )
        keys = (
            set(LOC.findall(target.read_text(encoding="utf-8-sig")))
            if target.is_file()
            else set()
        )
        client_coverage[language] = len(expected_keys & keys)
        clients_complete &= expected_keys <= keys
    history_complete = (
        history_target.is_file()
        and history_selector.is_file()
        and len(history_rows) == roster_count
        and len(expected_keys) == roster_count
        and len({tag for tag, _ in expected_history}) == roster_count
        and history_triggers == expected_history
        and expected_keys <= set(history_override_keys)
        and clients_complete
    )
    return {
        "loading_tip_installed_keys": sorted(tips),
        "loading_tip_override_keys": sorted(overridden),
        "loading_tip_complete": tips == overridden,
        "country_history_source": str(history_source),
        "country_history_keys": history_keys,
        "country_history_exact_override": history_target.is_file(),
        "country_history_override_keys": history_override_keys,
        "country_history_roster_count": len(history_rows),
        "country_history_trigger_count": len(history_triggers),
        "country_history_client_coverage": client_coverage,
        "country_history_complete": history_complete,
        "country_history_status": (
            f"complete_{roster_count}_tag_exact_override"
            if history_complete
            else "uncovered"
        ),
    }


def visible_text_hits() -> list[dict[str, object]]:
    hits: list[dict[str, object]] = []
    roots = (
        ROOT / "in_game/localization/english",
        ROOT / "main_menu/localization/english",
        ROOT / "loading_screen/localization/english",
    )
    pattern = re.compile(r"\b(" + "|".join(map(re.escape, FORBIDDEN)) + r")\b", re.I)
    for directory in roots:
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*.yml")):
            for number, line in enumerate(
                path.read_text(encoding="utf-8-sig").splitlines(), 1
            ):
                # Loc keys may retain engine identifiers; only quoted display
                # values are player-facing for this barrier.
                value = line.split(":", 1)[1] if ":" in line else ""
                for match in pattern.finditer(value):
                    if (
                        match.group(0).lower() == "revolution"
                        and "sassanid revolution" in value.lower()
                    ):
                        continue
                    hits.append(
                        {
                            "file": path.relative_to(ROOT).as_posix(),
                            "line": number,
                            "token": match.group(0),
                        }
                    )
    return hits


def inventory() -> dict[str, object]:
    metadata = json.loads(METADATA.read_text(encoding="utf-8-sig"))
    surfaces: dict[str, object] = {}
    definition_total = 0
    reference_total = 0
    art_total = 0
    uncovered: list[str] = []
    status_counts: Counter[str] = Counter()
    for name, relative in SURFACES.items():
        records = [
            source_record(name, rel, source)
            for rel, source in sorted(mounted_files(relative, (".txt",)).items())
        ]
        keys = sorted(
            {key for record in records for key in record["definitions"]}
        )
        definition_total += len(keys)
        reference_total += sum(int(record["reference_count"]) for record in records)
        art_total += sum(int(record["art_reference_count"]) for record in records)
        for record in records:
            status_counts[str(record["status"])] += 1
            if record["status"] == "uncovered":
                uncovered.append(f"{name}:{record['relative']}")
        surfaces[name] = {
            "policy": POLICY[name],
            "known_visible_debt": name in VISIBLE_DEBT,
            "file_count": len(records),
            "definition_count": len(keys),
            "definitions": keys,
            "files": records,
        }
    localization = localization_contract()
    if not bool(localization["loading_tip_complete"]):
        uncovered.append("localization:loading_tips")
    if not bool(localization["country_history_complete"]):
        uncovered.append("localization:country_history")
    disease_manifest = ROOT / "docs/m12/disease_dependency_manifest.json"
    disease = (
        json.loads(disease_manifest.read_text(encoding="utf-8"))
        if disease_manifest.is_file()
        else {}
    )
    hits = visible_text_hits()
    return {
        "game_version": metadata["supported_game_version"],
        "game_build_id": str(config()["game_build_id"]),
        "policy": POLICY,
        "surface_count": len(surfaces),
        "installed_definition_count": definition_total,
        "installed_reference_count": reference_total,
        "installed_art_reference_count": art_total,
        "status_counts": dict(sorted(status_counts.items())),
        "uncovered": sorted(uncovered),
        "visible_forbidden_tokens": list(FORBIDDEN),
        "visible_forbidden_hits": hits,
        "localization": localization,
        "disease_ui": {
            "installed_diseases": disease.get("installed_diseases", []),
            "asset_count": disease.get("asset_count", 0),
            "manifest_sha256": (
                sha256(disease_manifest.read_bytes())
                if disease_manifest.is_file()
                else None
            ),
        },
        "surfaces": surfaces,
    }


def canonical(value: dict[str, object]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def summary_bytes(value: dict[str, object]) -> bytes:
    loc = value["localization"]
    lines = [
        "<!-- Generated by tools/m12_installed_content_census.py; do not edit. -->",
        "",
        "# Installed-content leakage census",
        "",
        f"- Game/build: {value['game_version']} / {value['game_build_id']}",
        f"- Surfaces: {value['surface_count']}",
        f"- Installed definitions: {value['installed_definition_count']}",
        f"- Installed unlock/reference records: {value['installed_reference_count']}",
        f"- Installed art references: {value['installed_art_reference_count']}",
        f"- Uncovered sources: {len(value['uncovered'])}",
        f"- Player-visible prohibited-token hits: {len(value['visible_forbidden_hits'])}",
        (
            "- Loading tips: "
            f"{len(loc['loading_tip_override_keys'])}/"
            f"{len(loc['loading_tip_installed_keys'])} exact keys"
        ),
        (
            "- Country-history agenda: "
            f"{loc['country_history_status']} "
            f"({loc['country_history_roster_count']} roster tags; "
            f"{len(loc['country_history_client_coverage'])} clients)"
        ),
        "",
        "Every installed source hash and key union is pinned in "
        "`installed_content_leakage.json`; a base-game or DLC change makes "
        "`make validate` fail until `--write` explicitly accepts a reviewed "
        "classification.",
        "",
    ]
    return "\n".join(lines).encode("utf-8")


def write() -> None:
    value = inventory()
    if value["uncovered"]:
        raise ValueError(f"cannot accept uncovered sources: {value['uncovered']}")
    if value["visible_forbidden_hits"]:
        raise ValueError(
            "cannot accept player-visible prohibited tokens: "
            f"{value['visible_forbidden_hits'][:12]}"
        )
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_bytes(canonical(value))
    SUMMARY.write_bytes(summary_bytes(value))
    print(
        "m12_installed_content_census: wrote "
        f"{value['installed_definition_count']} definitions across "
        f"{value['surface_count']} surfaces"
    )


def check() -> bool:
    failures: list[str] = []
    try:
        value = inventory()
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"m12_installed_content_census: FAIL\n  - {exc}")
        return False
    if value["uncovered"]:
        failures.append(f"uncovered installed sources: {value['uncovered']}")
    if value["visible_forbidden_hits"]:
        failures.append(
            "player-visible prohibited tokens: "
            f"{value['visible_forbidden_hits'][:12]}"
        )
    if not REPORT.is_file() or REPORT.read_bytes() != canonical(value):
        failures.append(
            "installed union/classification changed; review and regenerate "
            f"{REPORT.relative_to(ROOT)}"
        )
    if not SUMMARY.is_file() or SUMMARY.read_bytes() != summary_bytes(value):
        failures.append(f"stale or missing {SUMMARY.relative_to(ROOT)}")
    if failures:
        print("m12_installed_content_census: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return False
    print(
        "m12_installed_content_census: PASS "
        f"({value['installed_definition_count']} definitions; "
        f"{value['installed_reference_count']} references; "
        f"{value['installed_art_reference_count']} art links; zero uncovered)"
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.write:
            write()
            return 0
        return 0 if check() else 1
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"m12_installed_content_census: FAIL\n  - {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
