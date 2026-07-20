#!/usr/bin/env python3
"""Validate and render ANTIQVITAS's M7 ancient-war foundation.

The generated advance overrides retain vanilla non-unit advances but strip every
vanilla unit and levy unlock.  M8 replaces that interim compatibility layer
with the complete ancient advance trees.  This is deliberately exact-filename
replacement, the locally verified override mechanism for EU5 setup/content.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path

from dates import M2_MIRROR_LANGUAGES

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/m7"
UNITS = DATA / "units.csv"
ARMIES = DATA / "armies.csv"
FORTS = DATA / "forts.csv"
UNIT_OUTPUT = ROOT / "in_game/common/unit_types/00_antiquitas_m7_units.txt"
ADVANCE_OUTPUT = ROOT / "in_game/common/advances"
M8_TREE = ADVANCE_OUTPUT / "00_antiquitas_m8_tree.txt"
LOC_ROOT = ROOT / "main_menu/localization"

UNIT_FIELDS = (
    "key", "name", "kind", "copy_from", "status", "age", "tags", "gfx_tags",
    "modifiers", "combat", "source", "confidence", "note",
)
ARMY_FIELDS = ("key", "kind", "country", "location", "unit_type", "strength", "source", "confidence", "note")
FORT_FIELDS = ("key", "location", "building", "level", "source", "confidence", "note")
TOKEN = re.compile(r"^[a-z][a-z0-9_]*$")
IDENTIFIER = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
NUMBER = re.compile(r"^-?(?:\d+(?:\.\d+)?|\.\d+)$")
UNLOCK = re.compile(r"^\s*unlock_(?:unit|levy)\s*=", re.IGNORECASE | re.MULTILINE)
LAND_BASES = frozenset((
    "a_age_1_traditions_light_infantry", "a_age_1_traditions_heavy_infantry",
    "a_age_1_traditions_light_cavalry", "a_age_1_traditions_heavy_cavalry",
    "a_age_4_reformation_heavy_infantry",
))
NAVY_BASES = frozenset((
    "n_age_1_traditions_galley", "n_age_1_traditions_light_ship",
    "n_age_1_traditions_transport", "n_age_1_traditions_heavy_ship",
))
AGES = frozenset((
    "age_1_traditions", "age_2_renaissance", "age_3_discovery",
    "age_4_reformation", "age_5_absolutism",
))
STAT_KEYS = frozenset((
    "morale_damage_taken", "strength_damage_taken", "morale_damage_done", "strength_damage_done",
    "supply_weight", "attrition_loss", "food_storage_per_strength", "food_consumption_per_strength",
    "movement_speed", "max_strength", "combat_speed", "initiative", "frontage", "combat_power",
    "flanking_ability", "secure_flanks_defense", "transport_capacity", "maritime_presence",
    "crew_size", "blockade_capacity", "hull_size",
))
TERRAIN = frozenset(("grasslands", "hills", "forest", "desert", "jungle", "coastal", "river", "mountains"))


@dataclass(frozen=True)
class Unit:
    key: str
    name: str
    kind: str
    copy_from: str
    status: str
    age: str
    tags: tuple[str, ...]
    gfx_tags: tuple[str, ...]
    modifiers: tuple[tuple[str, str], ...]
    combat: tuple[tuple[str, str], ...]
    source: str
    confidence: str
    note: str


def read_rows(path: Path, fields: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != fields:
            raise ValueError(f"{path.relative_to(ROOT)} header does not match required field order")
        return [{key: (value or "").strip() for key, value in row.items()} for row in reader]


def tokens(value: str, label: str) -> tuple[str, ...]:
    values = tuple(value.split("|")) if value else ()
    if any(not IDENTIFIER.fullmatch(item) for item in values):
        raise ValueError(f"{label} has an invalid script token")
    return values


def assignments(value: str, label: str, allowed: frozenset[str]) -> tuple[tuple[str, str], ...]:
    if not value:
        return ()
    parsed: list[tuple[str, str]] = []
    for part in value.split("|"):
        if part.count("=") != 1:
            raise ValueError(f"{label} has invalid assignment {part!r}")
        key, assigned = part.split("=", 1)
        if key not in allowed or not NUMBER.fullmatch(assigned):
            raise ValueError(f"{label} has unsafe assignment {part!r}")
        parsed.append((key, assigned))
    if len({key for key, _ in parsed}) != len(parsed):
        raise ValueError(f"{label} repeats an assignment key")
    return tuple(parsed)


def tag_map() -> dict[str, str]:
    entries = json.loads((ROOT / "docs/world_1ad/tag_map.json").read_text(encoding="utf-8-sig"))["entries"]
    return {entry["design_tag"]: entry["engine_tag"] for entry in entries}


def locations() -> set[str]:
    return set(json.loads((ROOT / "docs/vanilla_symbols/locations.json").read_text(encoding="utf-8-sig")))


def load_units() -> tuple[Unit, ...]:
    mapped_tags = tag_map()
    seen: set[str] = set()
    units: list[Unit] = []
    failures: list[str] = []
    for row in read_rows(UNITS, UNIT_FIELDS):
        key = row["key"]
        try:
            if any(not row[field] for field in UNIT_FIELDS if field not in {"gfx_tags", "modifiers", "combat"}):
                raise ValueError("blank required field")
            if not TOKEN.fullmatch(key):
                raise ValueError(f"invalid unit key {key!r}")
            if not key.startswith("antq_"):
                raise ValueError(f"unit key {key} must be namespaced antq_")
            if key in seen:
                raise ValueError(f"duplicate unit key {key}")
            if row["kind"] not in {"land", "navy"}:
                raise ValueError(f"{key} has invalid kind {row['kind']}")
            if row["status"] not in {"regular", "levy", "mercenary"}:
                raise ValueError(f"{key} has invalid status {row['status']}")
            if row["age"] not in AGES:
                raise ValueError(f"{key} has invalid age {row['age']}")
            base_set = LAND_BASES if row["kind"] == "land" else NAVY_BASES
            if row["copy_from"] not in base_set:
                raise ValueError(f"{key} uses an invalid {row['kind']} base {row['copy_from']}")
            tags = tokens(row["tags"], f"{key} tags")
            if not tags or any(tag not in mapped_tags for tag in tags):
                unknown = sorted(set(tags) - set(mapped_tags))
                raise ValueError(f"{key} has missing or unknown roster tags {unknown}")
            gfx_tags = tokens(row["gfx_tags"], f"{key} gfx_tags")
            modifiers = assignments(row["modifiers"], f"{key} modifiers", STAT_KEYS)
            combat = assignments(row["combat"], f"{key} combat", TERRAIN)
            if row["confidence"] not in {"secure", "contested"}:
                raise ValueError(f"{key} has invalid confidence")
            units.append(Unit(
                key, row["name"], row["kind"], row["copy_from"], row["status"], row["age"], tags,
                gfx_tags, modifiers, combat, row["source"], row["confidence"], row["note"],
            ))
            seen.add(key)
        except ValueError as exc:
            failures.append(f"units.csv {key or '<blank>'}: {exc}")
    if failures:
        raise ValueError("\n".join(failures))
    land = {unit.key for unit in units if unit.kind == "land"}
    navy = {unit.key for unit in units if unit.kind == "navy"}
    required_land = {"antq_legionaries", "antq_auxilia", "antq_han_crossbow_infantry", "antq_cataphracts", "antq_steppe_horse_archers", "antq_comitatenses", "antq_limitanei"}
    required_navy = {"antq_liburnian", "antq_trireme", "antq_quinquereme", "antq_merchant_roundship", "antq_monsoon_dhow", "antq_austronesian_outrigger"}
    if not required_land <= land or not required_navy <= navy:
        raise ValueError("units.csv is missing a plan-required M7 roster entry")
    if any(unit.kind == "navy" and dict(unit.modifiers).get("cannons") for unit in units):
        raise ValueError("M7 navy data must never define cannons")
    return tuple(units)


def validate_start_ledgers(units: tuple[Unit, ...]) -> None:
    unit_map = {unit.key: unit for unit in units}
    mapped_tags = tag_map()
    installed_locations = locations()
    failures: list[str] = []
    groups: dict[str, tuple[str, str, str]] = {}
    for row in read_rows(ARMIES, ARMY_FIELDS):
        key = row["key"]
        try:
            if any(not row[field] for field in ARMY_FIELDS):
                raise ValueError("blank required field")
            if not TOKEN.fullmatch(key) or row["kind"] not in {"army", "navy"}:
                raise ValueError("invalid manager key or kind")
            if row["country"] not in mapped_tags or row["location"] not in installed_locations:
                raise ValueError("unknown country or installed location")
            unit = unit_map.get(row["unit_type"])
            if unit is None:
                raise ValueError(f"unknown M7 unit {row['unit_type']}")
            if (row["kind"] == "army") != (unit.kind == "land"):
                raise ValueError("manager kind does not match unit kind")
            if row["country"] not in unit.tags:
                raise ValueError("starting country is outside the unit's bounded availability")
            strength = float(row["strength"])
            if not 0.05 <= strength <= 1.0:
                raise ValueError("strength must be 0.05 through 1.0")
            if row["confidence"] not in {"secure", "contested"}:
                raise ValueError("invalid confidence")
            identity = (row["kind"], row["country"], row["location"])
            if key in groups and groups[key] != identity:
                raise ValueError("manager key must retain one kind/country/location")
            groups[key] = identity
        except (ValueError, TypeError) as exc:
            failures.append(f"armies.csv {key or '<blank>'}: {exc}")
    forts = read_rows(FORTS, FORT_FIELDS)
    with (ROOT / "docs/world_1ad/ownership_resolved.csv").open(encoding="utf-8-sig", newline="") as handle:
        owners = {
            row["location"]
            for row in csv.DictReader(line for line in handle if not line.startswith("#"))
            if row["location"]
        }
    buildings = set(json.loads((ROOT / "docs/vanilla_symbols/building.json").read_text(encoding="utf-8-sig")))
    seen_forts: set[tuple[str, str]] = set()
    for row in forts:
        key = row["key"]
        try:
            if any(not row[field] for field in FORT_FIELDS):
                raise ValueError("blank required field")
            if not TOKEN.fullmatch(key) or row["building"] != "stockade":
                raise ValueError("M7 forts must use a namespaced key and the verified stockade proxy")
            if row["location"] not in installed_locations or row["location"] not in owners:
                raise ValueError("fort location is not controlled in the AD 1 start")
            if row["building"] not in buildings or int(row["level"]) != 1:
                raise ValueError("fort must use installed level-one stockade")
            if (row["location"], row["building"]) in seen_forts:
                raise ValueError("duplicate fort building location")
            if row["confidence"] not in {"secure", "contested"}:
                raise ValueError("invalid confidence")
            seen_forts.add((row["location"], row["building"]))
        except ValueError as exc:
            failures.append(f"forts.csv {key or '<blank>'}: {exc}")
    if not forts:
        failures.append("forts.csv has no M7 fort entries")
    if failures:
        raise ValueError("\n".join(failures))


def unit_script(units: tuple[Unit, ...]) -> str:
    tags = tag_map()
    lines = [
        "# Generated by tools/m7_war.py --write; M7 ancient unit roster.",
        "# Vanilla unit and levy unlocks are pruned in the matching advance overrides.",
    ]
    for unit in units:
        lines.extend((f"{unit.key} = {{", "\tis_special = yes", f"\tcopy_from = {unit.copy_from}", "\thide = no"))
        if unit.status == "regular":
            lines.append("\tbuildable = yes")
        elif unit.status == "levy":
            lines.extend(("\tbuildable = no", "\tlevy = yes"))
        else:
            lines.extend(("\tbuildable = no", "\tmercenaries_per_location = { pop_type = peasants multiply = 0.01 }"))
        lines.append(f"\tage = {unit.age}")
        if unit.kind == "navy":
            lines.append("\tcannons = 0")
        lines.extend(f"\t{key} = {value}" for key, value in unit.modifiers)
        if unit.combat:
            lines.append("\tcombat = { " + " ".join(f"{key} = {value}" for key, value in unit.combat) + " }")
        lines.extend(("\tcountry_potential = {", "\t\tOR = {"))
        lines.extend(f"\t\t\thas_or_had_tag = {tags[tag]}" for tag in unit.tags)
        lines.extend(("\t\t}", "\t}"))
        if unit.gfx_tags:
            lines.append("\tgfx_tags = { " + " ".join(unit.gfx_tags) + " }")
        lines.extend((f"\t# {unit.source}; {unit.note}", "}", ""))
    return "\n".join(lines)


def localization(units: tuple[Unit, ...], language: str) -> str:
    lines = [f"l_{language}:"]
    for unit in units:
        lines.append(f' {unit.key}: "{unit.name}"')
        lines.append(f' {unit.key}_desc: "{unit.note}"')
    return "\n".join(lines) + "\n"


def advance_overrides() -> dict[Path, str]:
    # M8 owns the complete exact-name advance replacement.  Retaining this
    # interim M7 layer after it is active would overwrite M8's clean blanks.
    if M8_TREE.is_file():
        return {}
    config = json.loads((ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig"))
    source = Path(config["game_dir"]) / "game/in_game/common/advances"
    if not source.is_dir():
        raise ValueError(f"installed advance directory is missing: {source}")
    outputs: dict[Path, str] = {}
    for path in source.glob("*.txt"):
        raw = path.read_text(encoding="utf-8-sig", errors="strict")
        if not UNLOCK.search(raw):
            continue
        if path.name == "readme.txt":
            continue
        retained = [line for line in raw.splitlines() if not UNLOCK.match(line)]
        outputs[ADVANCE_OUTPUT / path.name] = "\n".join((
            "# Generated by tools/m7_war.py --write; M7 removes vanilla unit and levy unlocks.",
            "# Non-unit advance content is retained verbatim until M8 replaces the full tree.",
            *retained,
            "",
        ))
    if not outputs:
        raise ValueError("no installed advance files contained unit or levy unlocks")
    return outputs


def outputs(units: tuple[Unit, ...]) -> dict[Path, str]:
    rendered = {UNIT_OUTPUT: unit_script(units), **advance_overrides()}
    for language in ("english", *M2_MIRROR_LANGUAGES):
        rendered[LOC_ROOT / language / f"antq_m7_war_l_{language}.yml"] = localization(units, language)
    return rendered


def write(units: tuple[Unit, ...]) -> None:
    for path, content in outputs(units).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8-sig", newline="\n")
        print(f"m7_war: wrote {path.relative_to(ROOT)}")


def check(units: tuple[Unit, ...]) -> bool:
    failures: list[str] = []
    expected = outputs(units)
    for path, content in expected.items():
        if not path.is_file():
            failures.append(f"missing {path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8-sig") != content:
            failures.append(f"stale {path.relative_to(ROOT)}")
        elif path != UNIT_OUTPUT and UNLOCK.search(path.read_text(encoding="utf-8-sig")):
            failures.append(f"unit unlock survived in {path.relative_to(ROOT)}")
    if failures:
        print("m7_war: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return False
    override_count = len(advance_overrides())
    layer = "M8 owns complete advance replacement" if M8_TREE.is_file() else f"{override_count} vanilla advance overrides"
    print(f"m7_war: PASS ({len(units)} ancient unit types; {layer}; no vanilla unit or levy unlocks)")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        units = load_units()
        validate_start_ledgers(units)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"m7_war: FAIL\n  - {exc}")
        return 1
    if args.write:
        write(units)
        return 0
    return 0 if check(units) else 1


if __name__ == "__main__":
    raise SystemExit(main())
