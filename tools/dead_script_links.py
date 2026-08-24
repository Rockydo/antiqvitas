#!/usr/bin/env python3
"""Remove proven post-antique variable links from quarantined vanilla scripts.

EU5's linker intentionally ignores setters/readers inside definitions which can
never execute.  That is useful diagnostics: after ANTIQVITAS false-gates the
medieval systems, it exposes variable operations whose opposite endpoint is no
longer reachable.  Keeping those operations serves no compatibility purpose and
produces misleading database warnings.  This module removes only the exact
EU5-1.3.11 linker inventory observed after the source-preserving event quarantine.
"""

from __future__ import annotations

import re

from dates import AntqDate, END


DATE_LITERAL = re.compile(
    r"(?<![0-9])-?[0-9]{1,4}\.[0-9]{1,2}\.[0-9]{1,2}(?![0-9])"
)


def sanitize_out_of_campaign_dates(text: str) -> tuple[str, int]:
    """Clamp inherited positive dates after AD 476 to the campaign boundary.

    Quarantined installed definitions remain source-shaped so EU5 can resolve
    their compile-time keys and scope graph.  Their post-antique date literals
    are not part of that contract and are rejected by the total-conversion
    lint, including biography dates inside permanently unreachable effects.
    Negative/BCE dates and dates already inside ANTIQVITAS remain byte-stable.
    """

    replacement = AntqDate(*END).engine()
    changed = 0

    def sanitize(match: re.Match[str]) -> str:
        nonlocal changed
        value = match.group(0)
        if value.startswith("-") or int(value.split(".", 1)[0]) <= END[0]:
            return value
        changed += 1
        return replacement

    return DATE_LITERAL.sub(sanitize, text), changed


USED_NEVER_SET = frozenset({
    "chinese_expedition_expedition_leader",
    "chinese_treasure_start_location",
    "chinese_treasure_target_area",
    "chinese_treasure_target_location",
    "chinese_treasure_voyage_cargo",
    "chinese_treasure_voyage_running",
    "cmd_restored_stability_variable",
    "cmd_strengthened_crown_variable",
    "completed_tax_revision_variable",
    "count_military_reforms_variable",
    "demanded_exemption_longterm_variable",
    "disfavoring_sect",
    "eligible_for_reform_society_disaster_variable",
    "gift_value",
    "gifts_received",
    "has_received_imperial_bribe",
    "has_received_imperial_bribe_timeout",
    "hostage_character_country",
    "is_chinese_expedition_expedition_leader",
    "original_outbreak",
    "promoting_sect",
    "reform_cavalry_variable",
    "reform_galley_variable",
    "reform_infantry_variable",
    "reform_merchant_fleet_variable",
    "reform_school_of_admirals_variable",
    "reform_thema_headquarters_variable",
    "reformed_the_cabinet_variable",
    "rot_conquest_ambition",
    "rot_has_selected_core_region",
    "sect_supporters",
    "unlocked_government_reform_timurid_empire",
    "unlocked_policy_timurid_court_policy",
    "war_of_religions_join_variable",
    "war_of_religions_left_variable",
})

SET_NEVER_USED = frozenset({
    "bribe_amount",
    "cargo_lost",
    "enable_turkic_migration_variable",
    "gag_force_switched_faction_penalty",
    "hre_diet_location",
    "io_parliaments_called_list",
    "lower_cooldown_campaign_in_italy_variable",
    "recently_destroyed_a_league_variable",
    "recently_elevanted_stronghold_variable",
    "recently_won_a_war",
    "shugo_capital_locations",
    "tribute_cost",
    "var_tordesillas_moved_the_line",
    "wotr_bribe_garrison_variable",
})

DEAD_EVENT_TARGETS = frozenset({"selected_country"})
ALL_DEAD_VARIABLES = USED_NEVER_SET | SET_NEVER_USED
TOKEN = re.compile(
    r"(?<![A-Za-z0-9_])(?:"
    + "|".join(re.escape(value) for value in sorted(ALL_DEAD_VARIABLES, key=len, reverse=True))
    + r")(?![A-Za-z0-9_])"
)
USED_TOKEN = re.compile(
    r"(?<![A-Za-z0-9_])(?:"
    + "|".join(re.escape(value) for value in sorted(USED_NEVER_SET, key=len, reverse=True))
    + r")(?![A-Za-z0-9_])"
)
VARIABLE_OPERATION = re.compile(
    r"\b(?:set|change|add_to|subtract_from|remove|clear)_"
    r"(?:global_|local_)?variable(?:_list)?\s*=|"
    r"\b(?:is_target_in|has|remove_from)_(?:global_)?variable_list\s*="
)
HAS_VARIABLE = re.compile(
    r"\bhas_(?:global_)?variable(?:_list)?\s*=\s*(?P<name>[A-Za-z_][A-Za-z0-9_]*)"
)
VAR_SCOPE = re.compile(
    r"(?:\bglobal_var:|\blocal_var:|(?:\b[A-Za-z_][A-Za-z0-9_]*\.)*\bvar:)"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)"
)
FALSEABLE_INLINE_BLOCK = re.compile(
    r"^(?P<indent>\s*)(?P<key>limit|trigger|potential|allow|visible|can_start)\s*=\s*\{"
)
ARGUMENT_OWNER = re.compile(
    r"^\s*(?:add_casus_belli|add_migration|change_amount_of_treasure_voyage|"
    r"country_has_recently_joined_situation_faction|"
    r"country_has_recently_left_situation_faction|disease_outbreak_presence|"
    r"every_in_list|give_gold_to_expedition)\s*=\s*\{"
)
DYNAMIC_DEAD_UNLOCK = re.compile(
    r"\bhas_unlocked_(?:government_reform|policy)_trigger\s*=\s*\{\s*"
    r"type\s*=\s*(?:timurid_empire|timurid_court_policy)\s*\}"
)


def structural_code(line: str) -> str:
    """Return structural text before an unquoted Clausewitz comment."""
    quoted = False
    escaped = False
    rendered: list[str] = []
    for char in line:
        if escaped:
            rendered.append(char)
            escaped = False
            continue
        if quoted and char == "\\":
            rendered.append(char)
            escaped = True
            continue
        if char == '"':
            quoted = not quoted
            rendered.append(char)
            continue
        if char == "#" and not quoted:
            break
        rendered.append(char)
    return "".join(rendered)


def brace_delta(line: str) -> int:
    code = structural_code(line)
    quoted = False
    escaped = False
    delta = 0
    for char in code:
        if escaped:
            escaped = False
        elif quoted and char == "\\":
            escaped = True
        elif char == '"':
            quoted = not quoted
        elif not quoted and char == "{":
            delta += 1
        elif not quoted and char == "}":
            delta -= 1
    return delta


def _consume_statement(lines: list[str], start: int) -> int:
    """Return the first line after a balanced statement beginning at start."""
    delta = brace_delta(lines[start])
    if delta <= 0:
        return start + 1
    depth = delta
    index = start + 1
    while index < len(lines) and depth > 0:
        depth += brace_delta(lines[index])
        index += 1
    if depth != 0:
        raise ValueError(f"dead-link statement at line {start + 1} is unbalanced")
    return index


def _remove_variable_operations(lines: list[str]) -> tuple[list[str], int]:
    rendered: list[str] = []
    removed = 0
    index = 0
    while index < len(lines):
        code = structural_code(lines[index])
        if VARIABLE_OPERATION.search(code) is None:
            rendered.append(lines[index])
            index += 1
            continue
        end = _consume_statement(lines, index)
        statement = "".join(structural_code(line) for line in lines[index:end])
        if TOKEN.search(statement) is None:
            rendered.extend(lines[index:end])
        else:
            removed += 1
        index = end
    return rendered, removed


def _contains_dead_reference(statement: str) -> bool:
    return TOKEN.search(statement) is not None or any(
        re.search(rf"\bscope:{re.escape(target)}\b", statement)
        for target in DEAD_EVENT_TARGETS
    )


def _remove_argument_owner_statements(lines: list[str]) -> tuple[list[str], int]:
    """Remove whole effects/triggers when a required argument is a dead link."""
    rendered: list[str] = []
    removed = 0
    index = 0
    while index < len(lines):
        code = structural_code(lines[index])
        if ARGUMENT_OWNER.match(code) is None:
            rendered.append(lines[index])
            index += 1
            continue
        end = _consume_statement(lines, index)
        statement = "".join(structural_code(line) for line in lines[index:end])
        if _contains_dead_reference(statement):
            removed += 1
        else:
            rendered.extend(lines[index:end])
        index = end
    return rendered, removed


def sanitize_dead_links(text: str, *, label: str) -> tuple[str, int]:
    """Strip exact dead variable/target operations while preserving braces."""
    source_depth = sum(brace_delta(line) for line in text.splitlines())
    if source_depth != 0:
        raise ValueError(f"{label}: source brace contract is unbalanced")
    lines, changed = _remove_argument_owner_statements(text.splitlines(keepends=True))
    lines, operation_changes = _remove_variable_operations(lines)
    changed += operation_changes
    rendered: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        code = structural_code(line)
        if DYNAMIC_DEAD_UNLOCK.search(code) is not None:
            changed += 1
            index += 1
            continue
        # A missing variable is exactly false in has-variable predicates. This
        # preserves surrounding NOT/OR logic instead of deleting the predicate.
        def false_has(match: re.Match[str]) -> str:
            nonlocal changed
            if match.group("name") not in ALL_DEAD_VARIABLES:
                return match.group(0)
            changed += 1
            return "always = no"

        line = HAS_VARIABLE.sub(false_has, line)
        code = structural_code(line)
        dead_scopes = [
            match for match in VAR_SCOPE.finditer(code)
            if match.group("name") in ALL_DEAD_VARIABLES
        ]
        dead_target = any(
            re.search(rf"\bscope:{re.escape(target)}\b", code)
            for target in DEAD_EVENT_TARGETS
        )
        if not dead_scopes and not dead_target:
            rendered.append(line)
            index += 1
            continue
        delta = brace_delta(line)
        if delta > 0:
            index = _consume_statement(lines, index)
            changed += 1
            continue
        inline = FALSEABLE_INLINE_BLOCK.match(code)
        if inline is not None:
            newline = "\r\n" if line.endswith("\r\n") else "\n"
            rendered.append(
                f"{inline.group('indent')}{inline.group('key')} = {{ always = no }}"
                f" # ANTIQVITAS dead late-era variable link{newline}"
            )
        else:
            # Effects/assignments involving a nonexistent variable or event
            # target are no-ops inside an already quarantined definition.
            pass
        changed += 1
        index += 1
    result = "".join(rendered)
    if sum(brace_delta(line) for line in result.splitlines()) != 0:
        raise ValueError(f"{label}: dead-link sanitization changed brace balance")

    # Any surviving operational reference is a new syntax form and must be
    # audited rather than silently accepted.
    survivors: list[str] = []
    for line_number, line in enumerate(result.splitlines(), start=1):
        code = structural_code(line)
        if (
            TOKEN.search(code)
            and (
                VARIABLE_OPERATION.search(code)
                or HAS_VARIABLE.search(code)
                or VAR_SCOPE.search(code)
            )
        ):
            survivors.append(f"{line_number}:{code.strip()}")
        if any(re.search(rf"\bscope:{re.escape(target)}\b", code) for target in DEAD_EVENT_TARGETS):
            survivors.append(f"{line_number}:{code.strip()}")
    if survivors:
        raise ValueError(
            f"{label}: dead script links survived: " + "; ".join(survivors[:10])
        )
    return result, changed


def validate_inventory() -> None:
    if len(USED_NEVER_SET) != 35 or len(SET_NEVER_USED) != 14:
        raise ValueError(
            "dead script-link inventory drift: "
            f"used={len(USED_NEVER_SET)}, set={len(SET_NEVER_USED)}"
        )
    if USED_NEVER_SET & SET_NEVER_USED:
        raise ValueError("dead script-link inventories overlap")
