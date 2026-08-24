#!/usr/bin/env python3
"""Assert Rome's sourced succession directly from a plaintext EU5 save.

This is deliberately independent of the setup generators.  It reads the
serialized country, character, and ruler-term managers and therefore catches
the class of defect where valid-looking setup script is replaced by an engine
regency, random ruler, early death, or overlapping term.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from save_melt import plaintext_save


ROOT = Path(__file__).resolve().parents[1]
ROMAN_NAMES = {
    "augustus": "antq_augustus",
    "gaius_caesar": "antq_gaius_caesar",
    "tiberius": "antq_tiberius",
    "livia": "antq_livia",
}
ROMAN_VARIABLES = {
    key: f"antq_m6_roman_{key}" for key in ROMAN_NAMES
}
BLOCK_START = re.compile(r"^(\d+)=\{$")
FIELD = re.compile(r"(?m)^\s*([a-zA-Z0-9_]+)=([^\s{}]+)\s*$")


@dataclass(frozen=True, order=True)
class GameDate:
    year: int
    month: int
    day: int

    @classmethod
    def parse(cls, text: str) -> "GameDate":
        # EU5 normally serializes a paused 08:00 save as Y.M.D, but saves
        # taken while a day is advancing may retain the simulation hour as
        # Y.M.D.H.  Succession assertions are day-granular, so accept and
        # validate that fourth component without letting it alter deadlines.
        match = re.fullmatch(r"(-?\d+)\.(\d+)\.(\d+)(?:\.(\d+))?", text.strip())
        if not match:
            raise ValueError(f"invalid EU5 date: {text!r}")
        year, month, day, hour = (
            int(part) if part is not None else None for part in match.groups()
        )
        if hour is not None and not 0 <= hour <= 23:
            raise ValueError(f"invalid EU5 hour in date: {text!r}")
        return cls(year, month, day)

    def __str__(self) -> str:
        return f"{self.year}.{self.month}.{self.day}"


@dataclass
class SaveState:
    date: GameDate
    country_id: int
    country: str
    characters: dict[int, str]
    terms: dict[int, str]


def brace_delta(text: str) -> int:
    """Count structural braces, excluding braces inside quoted strings."""
    delta = 0
    quoted = False
    escaped = False
    for character in text:
        if escaped:
            escaped = False
            continue
        if character == "\\" and quoted:
            escaped = True
        elif character == '"':
            quoted = not quoted
        elif not quoted and character == "{":
            delta += 1
        elif not quoted and character == "}":
            delta -= 1
    return delta


def default_save() -> Path:
    config = json.loads(
        (ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig")
    )
    directory = Path(str(config["user_dir"])) / "save games"
    saves = [path for path in directory.glob("*.eu5") if path.is_file()]
    if not saves:
        raise RuntimeError(f"no EU5 saves found in {directory}")
    return max(saves, key=lambda path: path.stat().st_mtime_ns)


def manager_blocks(path: Path) -> tuple[GameDate, dict[str, dict[int, str]]]:
    """Stream only the three manager block types needed by the assertion."""
    targets = {
        "character_db": {},
        "rulerterm_manager": {},
        "countries": {},
    }
    manager = ""
    manager_depth = 0
    database_depth: int | None = None
    block_id: int | None = None
    block_depth = 0
    block_lines: list[str] = []
    date: GameDate | None = None

    with path.open(encoding="utf-8-sig", errors="replace") as handle:
        for raw in handle:
            line = raw.rstrip("\r\n")
            stripped = line.strip()
            if date is None and stripped.startswith("date="):
                date = GameDate.parse(stripped.removeprefix("date="))

            if block_id is not None:
                block_lines.append(line)
                block_depth += brace_delta(line)
                if block_depth == 0:
                    text = "\n".join(block_lines)
                    keep = (
                        manager == "countries" and 'country_name="XAA"' in text
                    ) or (
                        manager == "character_db"
                        and any(name in text for name in ROMAN_NAMES.values())
                    ) or (
                        manager == "rulerterm_manager"
                        and re.search(r"(?m)^\s*ruled=3\s*$", text) is not None
                    )
                    if keep:
                        targets[manager][block_id] = text
                    block_id = None
                    block_lines = []
                continue

            if not manager:
                candidate = stripped.removesuffix("={")
                if stripped.endswith("={") and candidate in targets:
                    manager = candidate
                    manager_depth = 1
                    database_depth = None
                continue

            before = manager_depth
            start = BLOCK_START.fullmatch(stripped)
            expected_parent = database_depth
            if start and expected_parent is not None and before == expected_parent:
                block_id = int(start.group(1))
                block_lines = [line]
                block_depth = brace_delta(line)
                continue

            if (
                stripped == "database={"
                and database_depth is None
            ):
                database_depth = before + 1
            manager_depth += brace_delta(line)
            if manager_depth == 0:
                manager = ""
                database_depth = None

    if date is None:
        raise RuntimeError(f"no metadata date found in {path}")
    if len(targets["countries"]) != 1:
        raise RuntimeError(
            f"expected exactly one serialized XAA country, found "
            f"{len(targets['countries'])}"
        )

    # The opening Julio-Claudian characters have stable first-name keys, but
    # the guarded successors created after Tiberius accedes are deliberately
    # dynamic.  The first streaming pass cannot know their identities because
    # ``character_db`` precedes ``countries`` in EU5 saves.  Make a second,
    # targeted pass for every character referenced by Rome's government or by
    # a persisted M6 character variable.  This keeps memory bounded while
    # ensuring the validator actually inspects the dynamic ruler/heir records
    # it claims to validate (including the post-AD 37 continuity phase).
    country = next(iter(targets["countries"].values()))
    target_character_ids = {
        int(identity)
        for identity in re.findall(
            r"(?m)^\s*(?:ruler|heir|consort|active_regent)=(\d+)\s*$",
            balanced_named_block(country, "government"),
        )
    }
    target_character_ids.update(variable_characters(country).values())
    missing_character_ids = target_character_ids.difference(targets["character_db"])
    if missing_character_ids:
        targets["character_db"].update(
            targeted_character_blocks(path, missing_character_ids)
        )
    return date, targets


def targeted_character_blocks(path: Path, identities: set[int]) -> dict[int, str]:
    """Return only requested records from the save's character database."""
    if not identities:
        return {}

    result: dict[int, str] = {}
    manager_depth = 0
    database_depth: int | None = None
    block_id: int | None = None
    block_depth = 0
    block_lines: list[str] = []
    in_manager = False

    with path.open(encoding="utf-8-sig", errors="replace") as handle:
        for raw in handle:
            line = raw.rstrip("\r\n")
            stripped = line.strip()

            if block_id is not None:
                block_lines.append(line)
                block_depth += brace_delta(line)
                if block_depth == 0:
                    result[block_id] = "\n".join(block_lines)
                    if identities.issubset(result):
                        break
                    block_id = None
                    block_lines = []
                continue

            if not in_manager:
                if stripped == "character_db={":
                    in_manager = True
                    manager_depth = 1
                continue

            before = manager_depth
            start = BLOCK_START.fullmatch(stripped)
            if (
                start
                and database_depth is not None
                and before == database_depth
                and int(start.group(1)) in identities
            ):
                block_id = int(start.group(1))
                block_lines = [line]
                block_depth = brace_delta(line)
                continue

            if stripped == "database={" and database_depth is None:
                database_depth = before + 1
            manager_depth += brace_delta(line)
            if manager_depth == 0:
                break

    return result


def balanced_named_block(text: str, name: str) -> str:
    match = re.search(rf"(?m)^\s*{re.escape(name)}=\{{\s*$", text)
    if not match:
        raise RuntimeError(f"missing {name} block")
    start = match.start()
    depth = 0
    consumed = 0
    for line in text[start:].splitlines(keepends=True):
        depth += brace_delta(line)
        consumed += len(line)
        if depth == 0:
            return text[start:start + consumed]
    raise RuntimeError(f"unterminated {name} block")


def scalar(block: str, name: str) -> int | None:
    match = re.search(rf"(?m)^\s*{re.escape(name)}=(\d+)\s*$", block)
    return int(match.group(1)) if match else None


def character_name(block: str) -> str:
    match = re.search(r'(?m)^\s*first_name="?([^"\s]+)"?\s*$', block)
    if not match:
        raise RuntimeError("target Roman character lacks first_name")
    return match.group(1)


def variable_characters(country: str) -> dict[str, int]:
    result: dict[str, int] = {}
    pattern = re.compile(
        r"flag=(antq_m6_(?:roman_[a-z_]+|opening_ruler))\s+data=\{\s+"
        r"type=char\s+identity=(\d+)\s+\}",
        re.MULTILINE,
    )
    for flag, identity in pattern.findall(country):
        result[flag] = int(identity)
    return result


def parse_save(path: Path) -> SaveState:
    date, managers = manager_blocks(path)
    country_id, country = next(iter(managers["countries"].items()))
    return SaveState(
        date=date,
        country_id=country_id,
        country=country,
        characters=managers["character_db"],
        terms=managers["rulerterm_manager"],
    )


def assert_state(state: SaveState) -> dict[str, object]:
    errors: list[str] = []
    government = balanced_named_block(state.country, "government")
    ruler = scalar(government, "ruler")
    heir = scalar(government, "heir")
    consort = scalar(government, "consort")
    regent = scalar(government, "active_regent")
    variables = variable_characters(state.country)
    characters_by_name = {
        character_name(block): identity
        for identity, block in state.characters.items()
    }

    def identity(key: str, required_variable: bool = True) -> int | None:
        flag = ROMAN_VARIABLES[key]
        from_variable = variables.get(flag)
        from_name = characters_by_name.get(ROMAN_NAMES[key])
        if required_variable and from_variable is None:
            errors.append(f"missing serialized source identity {flag}")
        if from_variable is not None and from_name is not None and from_variable != from_name:
            errors.append(
                f"{flag} points to {from_variable}, but named character is {from_name}"
            )
        return from_variable if from_variable is not None else from_name

    opening_day = state.date == GameDate(1, 1, 1)
    augustus = identity(
        "augustus",
        state.date < GameDate(14, 8, 19) and not opening_day,
    )
    gaius = identity("gaius_caesar", state.date < GameDate(4, 3, 21))
    tiberius_release = GameDate(37, 4, 1)
    tiberius = identity("tiberius", state.date < tiberius_release)
    livia = identity("livia", state.date < GameDate(14, 9, 19))
    succession_reserve = variables.get("antq_m6_roman_succession_reserve")

    def alive(character_id: int | None, label: str) -> bool:
        if character_id is None:
            errors.append(f"missing {label} character record")
            return False
        block = state.characters.get(character_id)
        if block is None:
            errors.append(f"missing character block {character_id} for {label}")
            return False
        result = "alive_data={" in block and "death_data={" not in block
        if not result:
            errors.append(f"{label} ({character_id}) is not alive")
        return result

    # Year one cannot serialize Augustus's BCE birth in bookmark history, and
    # EU5 assigns the setup ruler character ID zero.  Character ID zero is the
    # engine's null sentinel for persisted scope variables, so the opening-day
    # adapter is asserted from the actual government and character records.
    # The age-63 target must already exist and be queued for the clean next-day
    # term; all later saves require the normal persisted Augustus variable.
    opening_target = variables.get("antq_m6_opening_ruler")
    if opening_day:
        if ROMAN_VARIABLES["augustus"] in variables:
            errors.append("opening Augustus unexpectedly serialized through the ID-zero sentinel")
        if augustus != ruler:
            errors.append(f"opening named Augustus is {augustus}, but active ruler is {ruler}")
        if opening_target is None:
            errors.append("missing serialized age-63 Augustus handoff target")
        elif opening_target == ruler:
            errors.append("opening Augustus handoff target aliases the active ruler")
        else:
            target_block = state.characters.get(opening_target, "")
            if not target_block:
                errors.append(f"missing opening Augustus handoff character {opening_target}")
            else:
                if character_name(target_block) != "antq_m6_placeholder_ruler":
                    errors.append("age-63 Augustus target is visible before the handoff")
                if not re.search(r"(?m)^\s*birth_date=-62\.1\.1\s*$", target_block):
                    errors.append("opening Augustus handoff target is not age 63")
                alive(opening_target, "age-63 Augustus handoff target")
        ruler_block = state.characters.get(ruler, "") if ruler is not None else ""
        if ROMAN_NAMES["augustus"] != character_name(ruler_block):
            errors.append("opening ruler does not persist the Augustus name key")
        if "modifier=antq_m6_historical_lifespan_guard" not in ruler_block:
            errors.append("opening Augustus lacks the mortality guard")
        livia_id = variables.get(ROMAN_VARIABLES["livia"])
        livia_block = state.characters.get(livia_id, "") if livia_id is not None else ""
        for field in ("religion", "culture", "dynasty"):
            if scalar(ruler_block, field) != scalar(livia_block, field):
                errors.append(f"opening Augustus {field} does not match the Julio-Claudian court")

    early_end = GameDate(4, 2, 21)
    gaius_deadline = GameDate(4, 3, 21)
    augustus_death = GameDate(14, 8, 19)
    augustus_deadline = GameDate(14, 9, 19)
    phase: str
    if state.date < early_end:
        phase = "Augustus / Gaius"
        expected_ruler, expected_heir, expected_consort = augustus, gaius, livia
        for character_id, label in (
            (augustus, "Augustus"), (gaius, "Gaius Caesar"),
            (tiberius, "Tiberius"), (livia, "Livia"),
        ):
            alive(character_id, label)
    elif state.date <= gaius_deadline:
        phase = "Gaius transition window"
        expected_ruler, expected_consort = augustus, livia
        expected_heir = heir
        alive(augustus, "Augustus")
        alive(tiberius, "Tiberius")
        alive(livia, "Livia")
        if heir not in {gaius, tiberius}:
            errors.append(f"transition-window heir {heir} is neither Gaius nor Tiberius")
    elif state.date < augustus_death:
        phase = "Augustus / Tiberius"
        expected_ruler, expected_heir, expected_consort = augustus, tiberius, livia
        for character_id, label in (
            (augustus, "Augustus"), (tiberius, "Tiberius"), (livia, "Livia"),
        ):
            alive(character_id, label)
        if gaius is not None:
            gaius_block = state.characters.get(gaius, "")
            if "alive_data={" in gaius_block:
                errors.append(f"Gaius Caesar ({gaius}) survived past the AD 4 transition")
    elif state.date <= augustus_deadline:
        phase = "Augustus transition window"
        expected_ruler, expected_heir, expected_consort = ruler, heir, consort
        if ruler not in {augustus, tiberius}:
            errors.append(f"transition-window ruler {ruler} is neither Augustus nor Tiberius")
    elif state.date < tiberius_release:
        phase = "Tiberius / succession reserve"
        expected_ruler = tiberius
        expected_heir = succession_reserve
        expected_consort = consort
        alive(tiberius, "Tiberius")
        if succession_reserve is None:
            errors.append("missing protected Roman succession reserve")
        else:
            alive(succession_reserve, "Roman succession reserve")
    else:
        phase = "post-Tiberius continuity"
        expected_ruler, expected_heir, expected_consort = ruler, succession_reserve, consort
        if ruler is None:
            errors.append("Rome has no ruler after the Tiberius chronology horizon")
        else:
            alive(ruler, "post-Tiberius ruler")
        if succession_reserve is None:
            errors.append("Rome has no protected designated successor")
        else:
            alive(succession_reserve, "Roman succession reserve")

    if ruler != expected_ruler:
        errors.append(f"ruler is {ruler}, expected {expected_ruler}")
    if heir != expected_heir:
        errors.append(f"heir is {heir}, expected {expected_heir}")
    if consort != expected_consort:
        errors.append(f"consort is {consort}, expected {expected_consort}")
    if regent is not None:
        errors.append(f"unexpected active regent {regent}")

    # Every occupied government slot must point to a distinct living character.
    slots = {"ruler": ruler, "heir": heir, "consort": consort}
    occupied = [value for value in slots.values() if value is not None]
    if len(occupied) != len(set(occupied)):
        errors.append(f"government slots are not distinct: {slots}")
    for label, character_id in slots.items():
        if character_id is not None:
            alive(character_id, label)

    if ruler is not None and consort is not None:
        ruler_block = state.characters.get(ruler, "")
        consort_block = state.characters.get(consort, "")
        ruler_spouses = {
            int(value)
            for group in re.findall(r"spouse=\{([^}]*)\}", ruler_block)
            for value in re.findall(r"\d+", group)
        }
        consort_spouses = {
            int(value)
            for group in re.findall(r"spouse=\{([^}]*)\}", consort_block)
            for value in re.findall(r"\d+", group)
        }
        if consort not in ruler_spouses or ruler not in consort_spouses:
            errors.append(
                f"ruler/consort marriage is not reciprocal: {ruler_spouses}, {consort_spouses}"
            )

    terms_match = re.search(r"ruler_terms=\{([^}]*)\}", government)
    if not terms_match:
        errors.append("government lacks ruler_terms")
        term_ids: list[int] = []
    else:
        term_ids = [int(value) for value in re.findall(r"\d+", terms_match.group(1))]
    missing_terms = [term_id for term_id in term_ids if term_id not in state.terms]
    if missing_terms:
        errors.append(f"Rome ruler_terms missing from term manager: {missing_terms}")
    active_terms = [
        (term_id, block)
        for term_id, block in state.terms.items()
        if "end_date=" not in block
    ]
    if len(active_terms) != 1:
        errors.append(f"Rome has {len(active_terms)} active ruler terms, expected exactly one")
        active_term_id = None
    else:
        active_term_id, active_block = active_terms[0]
        term_character = scalar(active_block, "character")
        if active_term_id not in term_ids:
            errors.append(f"active ruler term {active_term_id} is absent from government list")
        if term_character != ruler:
            errors.append(
                f"active ruler term character is {term_character}, government ruler is {ruler}"
            )

    report = {
        "date": str(state.date),
        "phase": phase,
        "country_id": state.country_id,
        "ruler": ruler,
        "heir": heir,
        "consort": consort,
        "regent": regent,
        "active_ruler_term": active_term_id,
        "source_identities": {
            "augustus": augustus,
            "gaius_caesar": gaius,
            "tiberius": tiberius,
            "livia": livia,
            "succession_reserve": succession_reserve,
            "opening_handoff_target": opening_target,
        },
        "errors": sorted(set(errors)),
    }
    if errors:
        raise RuntimeError("\n".join(report["errors"]))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Assert Rome ruler/heir/consort/term integrity from an EU5 save"
    )
    parser.add_argument("save", nargs="?", type=Path, help="save; defaults to newest")
    parser.add_argument("--json", type=Path, help="optional report output")
    args = parser.parse_args()
    save = (args.save or default_save()).resolve()
    if not save.is_file():
        raise FileNotFoundError(save)
    try:
        with plaintext_save(save) as source:
            report = assert_state(parse_save(source))
    except (RuntimeError, ValueError) as exc:
        print(f"m6_ruler_runtime: FAIL ({save})", file=sys.stderr)
        print(exc, file=sys.stderr)
        return 1
    report["save"] = str(save)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    print("m6_ruler_runtime: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
