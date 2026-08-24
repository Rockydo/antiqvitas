#!/usr/bin/env python3
"""Exact-mirror quarantine for mounted post-antique political systems.

EU5 merges definition registries by filename.  A total conversion therefore
cannot remove vanilla privileges, cabinet actions, parliament content, laws,
or reforms with a single late-loading file: every mounted source filename must
be mirrored.  This generator preserves every installed key for script
resolution, but makes each installed definition permanently unavailable
through its native ``potential`` gate.  ANTIQVITAS definitions live in
separate namespaced files and remain available.

The same pass disables installed country interactions, character interactions,
chivalric orders, generic actions, and disasters whose availability predicates
belong to medieval organizations, characters, dynasties, or institutions even
when their visible content is otherwise hidden.
The one annual HRE pulse is guarded because EU5 1.3.11 evaluates it even though
the AD 1 setup has no HRE.  Installed insult predicates are exact-mirrored where
they dereference an optional ruler without first proving that one exists.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from s2_ancient_laws import opening_adapter_policy_blocks

from dead_script_links import (
    sanitize_dead_links,
    sanitize_out_of_campaign_dates,
    validate_inventory,
)
from legacy_institutions import neutralize_references


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
MANIFEST = ROOT / "docs/m12/system_quarantine_manifest.json"
TAG_MAP = ROOT / "docs/world_1ad/tag_map.json"
LEND_UNIT_ICON = Path(
    "main_menu/gfx/interface/icons/unit_actions/lend_unit_to_ally.dds"
)
LEND_UNIT_SOURCE_ICON = Path(
    "main_menu/gfx/interface/icons/unit_ability/lend_unit_to_ally.dds"
)
LAW_COUNTRY_GROUP = re.compile(
    r"(?P<prefix>\blaw_country_group\s*=\s*)(?P<tag>[A-Z0-9]{3})\b"
)
COUNTRY_SCOPE_REF = re.compile(r"\bc:(?P<tag>[A-Z0-9]{3})\b")
EXPLORATION_TRIGGER = "in_game/common/scripted_triggers/exploration_triggers.txt"
INSULTS_RULER_GUARD = "in_game/common/insults/00_insults.txt"
HRE_SPECIAL_STATUSES = (
    "in_game/common/international_organization_special_statuses/hre.txt"
)
SHINTO_RELIGIOUS_FACTIONS = "in_game/common/religious_factions/shinto.txt"
HARDCODED_PRICES = "in_game/common/prices/00_hardcoded.txt"
AI_RIVAL_GUARD = (
    "in_game/common/rival_criteria/zz_antq_ai_rival_replacement_guard.txt"
)
# These tags are created after the opening setup and therefore are not present
# in the AD 1 tag map.  Keep them under the same AI rival-planning policy as
# the opening countries from the instant they are defined.
ANCIENT_DYNAMIC_COUNTRY_TAGS = {
    "CPC",
    "ERO",
    "HNS",
    "MOC",
    "VND",
    "VSG",
    "XNO",
}

SURFACES = {
    "estate_privileges": ("in_game/common/estate_privileges", "potential"),
    "cabinet_actions": ("in_game/common/cabinet_actions", "potential"),
    "parliament_issues": ("in_game/common/parliament_issues", "potential"),
    "parliament_agendas": ("in_game/common/parliament_agendas", "potential"),
    "laws": ("in_game/common/laws", "potential"),
    "government_reforms": ("in_game/common/government_reforms", "potential"),
    "country_interactions": ("in_game/common/country_interactions", "potential"),
    "character_interactions": (
        "in_game/common/character_interactions",
        "potential",
    ),
    "chivalric_orders": ("in_game/common/chivalric_orders", "potential"),
    "generic_actions": ("in_game/common/generic_actions", "potential"),
    "casus_belli": ("in_game/common/casus_belli", "create_visible"),
    "peace_treaties": ("in_game/common/peace_treaties", "potential"),
    "subject_types": (
        "in_game/common/subject_types",
        (
            "creation_visible",
            "subject_creation_enabled",
            "release_country_enabled",
            "visible_through_diplomacy",
            "visible_through_treaty",
        ),
    ),
    "scripted_diplomatic_objectives": (
        "in_game/common/scripted_diplomatic_objectives",
        "actor_trigger",
    ),
    "disasters": ("in_game/common/disasters", "can_start"),
    "formable_countries": ("in_game/common/formable_countries", "potential"),
    # Religious aspects use `visible`, not `potential`, as their registry gate.
    "religious_aspects": ("in_game/common/religious_aspects", "visible"),
}
# Generic actions are covered by the complete mounted filename census below.
# A second targeted pass used to overwrite ``hre_circle_actions.txt`` after
# that census and accidentally resurrect its pruned definitions.
TARGETED_QUARANTINES: dict[str, tuple[str, str]] = {}
EXCLUDED_BY_SURFACE = {
    # ANTIQVITAS retains and validates this engine action so players can move
    # the fully replaced ancient societal-value axes.
    "cabinet_actions": {"change_societal_values.txt"},
    # This exact file is jointly neutralized for legacy institution references
    # by m8_legacy_institution_purge.py.
    "disasters": {"revolution_disaster.txt"},
    # Engine-internal CBs are never player-created. They remain available to
    # hardcoded and event effects while every selectable installed CB is
    # independently classified below.
    "casus_belli": {"00_hardcoded.txt", "01_event_triggered.txt"},
    # These exact filenames are full ANTIQVITAS ancient rewrites maintained by
    # their own generators rather than inherited installed action bodies.
    "generic_actions": {
        "autocephalous_patriarchates.txt",
        "languages.txt",
        "markets.txt",
    },
    # This ancient court-marriage adapter is independently exact-mirrored by
    # m12_hardcoded_startup.py, which removes its one dead medieval character
    # comparison while retaining the otherwise portable interaction.
    "character_interactions": {"marry_noble.txt"},
}
YEARLY_ON_ACTION = "in_game/common/on_action/country_yearly.txt"
ON_ACTION_SCOPE_GUARDS = (
    "in_game/common/on_action/appanage_monthly.txt",
    "in_game/common/on_action/character.txt",
    "in_game/common/on_action/character_death_pulses.txt",
    "in_game/common/on_action/on_country_specific_pulse.txt",
)
TOP_LEVEL = re.compile(r"^\s*[A-Za-z_][A-Za-z0-9_]*\s*=\s*\{")
TOP_LEVEL_KEY = re.compile(r"^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*\{")
HRE_YEARLY_LINK = "\t\tinternational_organization:hre = { circles_are_active = yes }"
HRE_YEARLY_GUARD = "\t\tinternational_organization:hre ?= { circles_are_active = yes }"
TIMUR_YEARLY_DELAYED_EVENT = (
    "\t\tdelay = { months = { 0 36 } } # A bit of jitter to avoid Timur always spawning the same year\n"
    "\t\tflavor_tim.8\n"
)
MARKER = "ANTIQVITAS mounted-system quarantine"
LEGACY_POLICY_MARKER = "ANTIQVITAS legacy-policy quarantine"
MARKET_SCOPE_GUARDS = {
    ("generic_actions", "religious_factions.txt"): 1,
    ("peace_treaties", "sound_toll_exemption.txt"): 1,
}
PARLIAMENT_TARGET_CAPITAL_GUARD = (
    "\t\t\tis_rebel_country = no\n"
    "\t\t\tscope:actor = {\n"
    "\t\t\t\twithin_diplomatic_range = root\n"
    "\t\t\t}\n"
    "\t\t\tcapital = {\n"
    "\t\t\t\tis_discovered_by = scope:actor\n"
    "\t\t\t}\n"
)
DEAD_LINES = {
    ("generic_actions", "D008_fate_of_the_phoenix_actions.txt"): re.compile(
        r"^[ \t]*set_variable\s*=\s*grant_latin_merchants_privileges_variable"
        r"[ \t]*(?:#.*)?\r?\n?",
        re.MULTILINE,
    ),
}
RETAINED_ENGINE_ADAPTERS = {
    # EU5's bookmark initializer requires this category for countries with a
    # succession law. False-gating it produces "has no heir_religion_law"
    # for the roster and can suppress the law UI. Its player-facing text is
    # ancientized separately; retaining the category is an engine contract.
    "laws": {
        "heir_religion_law",
        "marriage_law",
    },
    "country_interactions": {
        "ask_for_access_for_war_side",
        "ask_for_money",
        "assassinate_character",
        "break_others_alliance",
        "give_location_to_subject",
        "give_province_to_subject",
        "give_subject_location_to_other_subject",
        "influence_nation",
        "intervene_in_subject_civil_war",
        "intervene_in_subject_regular_war",
        "invite_artist",
        "invite_prince",
        "invite_royal_family",
        "invite_settlers",
        "lend_unit_to_ally",
        "pay_off_debt",
        "renegotiate_loan",
        "request_loan",
        "request_work_of_art_purchase",
        "sabotage_reputation",
        "seize_location_from_subject",
        "sell_work_of_art",
        "share_maps",
        # Engine lifecycle contract: after twelve months this lets the
        # overwhelmingly weaker half of a civil war capitulate to its
        # opponent.  Quarantining it left hopeless rump states fighting for
        # decades, pinning their rebellious estate at zero satisfaction and
        # driving both successor governments into bankruptcy.
        "surrender_civil_war",
        "steal_maps",
        "steal_technology",
        "subject_embargo",
        "subject_enforce_peace",
        "subject_return_land",
        "take_over_loan",
        "transfer_occupation",
        "transfer_subject",
    },
    # These interactions describe portable actions available to ancient
    # courts and states.  Every omitted mounted definition is culture-,
    # religion-, institution-, or era-specific and is false-gated below.
    "character_interactions": {
        "abdicate",
        "adapt_culture_for_ruler",
        "appoint_as_heir",
        "assign_governor",
        "assume_fort_command",
        "banish_character",
        "commission_art",
        "dismiss_artist",
        "ennoble",
        "execute_character",
        "favor_heir",
        "grant_cabinet_right",
        "make_regent_ruler",
        "marry_lowborn",
        "move_child_to_court",
        "pardon",
        "promote_to_head_of_cabinet",
        "tribal_arrange_marriage",
    },
    # Rebellion uses this engine-internal relationship, but it is not a
    # player-creatable subject contract.
    "subject_types": {"secessionists"},
    # Only mechanically neutral or historically portable actions survive the
    # complete mounted-action census. Profile-specific ancient actions live in
    # namespaced ANTIQVITAS files and are not part of the installed mirror.
    "generic_actions": {
        "add_accepted_culture",
        "add_bureaucracy_action",
        "add_location_to_international_organization",
        "add_religious_aspect",
        "add_tolerated_culture",
        "ask_burghers_for_loan",
        "ask_clergy_for_legitimacy",
        "ask_commoners_for_stability",
        "ask_for_extra_levies",
        "ask_for_larger_levies",
        "ask_for_law_changes",
        "ask_nobility_for_diplomats",
        "ask_tribes_for_manpower",
        "bribe_estate",
        "call_emergency_parliament",
        "call_parliament",
        "change_employment_system",
        "change_military_stance",
        "change_parliament_type",
        "change_primary_culture",
        "change_religious_aspect",
        "contribute_to_organization_treasury",
        "convert_religion",
        "create_building_subject",
        "create_province_subject",
        "delist_unit",
        "extraordinary_taxes",
        "favor_god",
        "garrison_sortie",
        "hire_advisor",
        "hire_artist",
        "improve_our_cultural_view",
        "invite_foreign_cleric",
        "join_international_organization",
        "leave_international_organization",
        "make_unit_available_for_hire",
        "migrate_pop_based_country",
        "negotiate_rebels_accept_demands",
        "negotiate_rebels_buy_off",
        "perform_reduction",
        "pilgrimage_action",
        "prepare_for_war",
        "provoke_rebels",
        "recall_lent_unit",
        "reduce_our_cultural_view",
        "remove_accepted_culture",
        "remove_bureaucracy_action",
        "remove_location_from_international_organization",
        "remove_religious_aspect",
        "remove_tolerated_culture",
        "request_more_taxes",
        "religious_offering",
        "revoke_town_rights",
        "select_omen",
        "select_omen_god",
        "sell_work_of_art_to_estates",
        "set_province_capital",
        "settle_country",
        "stop_favoring_god",
        "take_estate_loan",
        "train_admiral",
        "train_general",
        "tribal_to_monarchy",
        "withdraw_from_organization_treasury",
    },
    # These installed contracts have period-neutral mechanics and text. All
    # colonial, crusading, nationalist, imperialist, revolution, HRE, later
    # Chinese, Japanese, Ottoman, Timurid, and confessional CBs are hidden.
    "casus_belli": {
        "attack_threat",
        "cb_anti_piracy",
        "cb_coalition",
        "cb_conquer_province",
        "cb_disloyal_subject",
        "cb_fabricated_conquer_province",
        "cb_force_migration",
        "cb_independence_war",
        "cb_make_tributary",
        "cb_trade_conflict",
        "cb_tribal_feud",
    },
}
# These actions are referenced by engine caches or loaded registries even when
# their post-antique systems are unavailable.  They must remain resolvable,
# but unlike the portable retained adapters their potential stays false and
# their autonomous scheduler is inert.
GENERIC_ACTION_COMPATIBILITY_ADAPTERS = frozenset({
    "activate_avatar",
    "allow_safe_refuge",
    "appease_nobles_estate_from_shogun_court",
    "baptize_ruler_from_kirishitan",
    "become_shogun_from_imperial_court",
    "crackdown_their_strongholds",
    "create_colonial_charter",
    "demand_extra_payment_from_shogun_court",
    "establish_treaty_with_kirishitan",
    "favor_buddhist_schools_from_religious_sects",
    "favor_kami_worship_from_religious_sects",
    "get_claim_from_imperial_court",
    "get_marriage_from_imperial_court",
    "hire_privateer",
    "hold_public_kirishitan_mass",
    "increase_clergy_satisfaction_from_religious_sects",
    "increase_levies_from_shogun_court",
    "increase_literacy_from_religious_sects",
    "increase_peasant_satisfaction_from_ikko_ikki",
    "increase_tax_income_from_shogun_court",
    "join_sect",
    "keep_kami_and_buddha_balanced_from_religious_sects",
    "limit_movement_of_kirishitan",
    "reduce_rebels_from_ikko_ikki",
    "request_aid",
    # The installed religion localization resolves this key through
    # ShowGenericActionName while the main-menu database is still being
    # constructed. Retain its false-gated compatibility contract so the
    # post-antique mechanic remains unavailable but its UI reference resolves.
    "reform_society_action",
    "sengoku_proclaim_clan_independence",
    "start_exploration",
})
GENERIC_ACTION_HARDCODED_ADAPTERS = frozenset({
    "activate_avatar",
    "add_accepted_culture",
    "add_religious_aspect",
    "add_tolerated_culture",
    "call_parliament",
    "contribute_to_organization_treasury",
    "create_building_subject",
    "create_colonial_charter",
    "create_province_subject",
    "hire_privateer",
    "join_sect",
    "negotiate_rebels_accept_demands",
    "negotiate_rebels_buy_off",
    "request_aid",
    "revoke_town_rights",
    "sengoku_proclaim_clan_independence",
    "start_exploration",
    "withdraw_from_organization_treasury",
})
GENERIC_ACTION_NOOP_DIAGNOSTIC = frozenset()
GENERIC_ACTION_RELAXED_DIAGNOSTIC = frozenset()
GENERIC_ACTION_ALLOW_RELAXED_DIAGNOSTIC = frozenset()
GENERIC_ACTION_SELECTOR_RELAXED_DIAGNOSTIC = frozenset()
PARLIAMENT_SELECTOR_GATE_DIAGNOSTIC = frozenset({3})
GENERIC_ACTION_GLOBAL_ADAPTERS = frozenset({
    "add_accepted_culture",
    "add_tolerated_culture",
    "bribe_estate",
    "change_employment_system",
    "change_primary_culture",
    "convert_religion",
    "create_building_subject",
    "create_province_subject",
    "delist_unit",
    "make_unit_available_for_hire",
    "remove_accepted_culture",
    "remove_tolerated_culture",
    "take_estate_loan",
})
# Post-antique cache adapters stay resolvable but never schedule themselves.
# ``prepare_for_war`` is also manual-only: its separately evaluated country
# and province selectors cannot provide one atomic AI target.  A target that
# entered war between those evaluations produced an invalid generic command in
# the AD 10 Rome observer run, immediately before that same war was declared.
# The player action remains available and ordinary diplomatic AI remains live.
GENERIC_ACTION_AI_DISABLED = (
    GENERIC_ACTION_COMPATIBILITY_ADAPTERS | {"prepare_for_war"}
)

def generic_action_registry_adapters() -> frozenset[str]:
    """Return every portable or engine-referenced mounted action contract."""
    return frozenset(
        RETAINED_ENGINE_ADAPTERS["generic_actions"]
        | GENERIC_ACTION_COMPATIBILITY_ADAPTERS
    )


def generic_action_ai_list_adapters() -> frozenset[str]:
    """Return installed action keys admitted to native AI-list selection."""
    return generic_action_registry_adapters()


# Unavailable cache adapters retain no autonomous selection weight. Portable
# actions retain their installed utility functions.
GENERIC_ACTION_AI_WEIGHT_DISABLED = GENERIC_ACTION_COMPATIBILITY_ADAPTERS
ENGINE_REQUIRED_LAW_POLICIES = {
    "marriage_law": "monogamous_marriage",
    "heir_religion_law": "heir_same_religion",
}


def _consume_block(lines: list[str], start: int, base_depth: int) -> int:
    """Return the first index after a brace block beginning at ``start``."""
    depth = base_depth
    index = start
    while index < len(lines):
        depth += brace_delta(lines[index])
        index += 1
        if depth == base_depth:
            return index
    raise ValueError("unbalanced retained law child block")


def _hide_legacy_policy(block: list[str]) -> list[str]:
    """Keep a referenced installed policy resolvable but never selectable."""
    rendered = [block[0]]
    index = 1
    depth = 1
    replaced_potential = False
    while index < len(block) - 1:
        line = block[index]
        code = structural_code(line)
        child = TOP_LEVEL_KEY.match(code) if depth == 1 else None
        if child and child.group("key") == "potential":
            end = _consume_block(block, index, depth)
            potential = block[index:end]
            if len(potential) == 1:
                rendered.append(
                    re.sub(
                        r"\{",
                        "{ always = no ",
                        potential[0],
                        count=1,
                    ).rstrip()
                    + f" # {LEGACY_POLICY_MARKER}"
                )
            else:
                rendered.append(potential[0].rstrip())
                rendered.append(
                    "\t\t\talways = no "
                    f"# {LEGACY_POLICY_MARKER}"
                )
                rendered.extend(item.rstrip() for item in potential[1:])
            replaced_potential = True
            index = end
            continue
        rendered.append(line.rstrip())
        depth += brace_delta(line)
        index += 1
    if not replaced_potential:
        rendered.insert(
            1,
            "\t\tpotential = { always = no } "
            f"# {LEGACY_POLICY_MARKER}",
        )
    rendered.append(block[-1])
    return rendered


def _adapt_retained_law(block: list[str], key: str, policies: str) -> list[str]:
    """Open an engine law to antiquity while preserving hidden legacy policies."""
    rendered = [block[0]]
    index = 1
    depth = 1
    root_controls = {
        "potential": "\tpotential = { }",
        "allow": "\tallow = { }",
        "locked": "\tlocked = { always = no }",
    }
    while index < len(block) - 1:
        line = block[index]
        code = structural_code(line)
        child = TOP_LEVEL_KEY.match(code) if depth == 1 else None
        if child:
            child_key = child.group("key")
            end = _consume_block(block, index, depth)
            if child_key in root_controls:
                rendered.append(root_controls[child_key])
            elif child_key == ENGINE_REQUIRED_LAW_POLICIES.get(key):
                required = block[index:end]
                opened = [required[0]]
                required_index = 1
                required_depth = 1
                while required_index < len(required) - 1:
                    required_line = required[required_index]
                    required_code = structural_code(required_line)
                    required_child = (
                        TOP_LEVEL_KEY.match(required_code)
                        if required_depth == 1 else None
                    )
                    if required_child and required_child.group("key") in root_controls:
                        required_end = _consume_block(
                            required, required_index, required_depth
                        )
                        opened.append(root_controls[required_child.group("key")])
                        required_index = required_end
                        continue
                    opened.append(required_line.rstrip())
                    required_depth += brace_delta(required_line)
                    required_index += 1
                opened.append(required[-1])
                rendered.extend(opened)
            else:
                rendered.extend(_hide_legacy_policy(block[index:end]))
            index = end
            continue
        rendered.append(line.rstrip())
        depth += brace_delta(line)
        index += 1
    rendered.extend(policies.rstrip().splitlines())
    rendered.append(block[-1])
    return rendered


def replace_retained_law_definitions(text: str) -> tuple[str, set[str]]:
    """Adapt retained law roots inside their original mounted filenames."""
    replacements = {
        **opening_adapter_policy_blocks(),
        **{key: "" for key in ENGINE_REQUIRED_LAW_POLICIES},
    }
    lines = text.splitlines()
    rendered: list[str] = []
    found: set[str] = set()
    index = 0
    depth = 0

    while index < len(lines):
        line = lines[index]
        code = structural_code(line)
        top_level = TOP_LEVEL_KEY.match(code) if depth == 0 else None
        if top_level and top_level.group("key") in replacements:
            key = top_level.group("key")
            if brace_delta(line) <= 0:
                raise ValueError(
                    f"unsupported one-line retained law definition: {key}"
                )
            end = _consume_block(lines, index, 0)
            rendered.extend(
                _adapt_retained_law(lines[index:end], key, replacements[key])
            )
            found.add(key)
            index = end
            continue
        rendered.append(line.rstrip())
        depth += brace_delta(line)
        index += 1

    if depth != 0:
        raise ValueError("unbalanced law source while replacing retained roots")
    return "\n".join(rendered) + "\n", found


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def game_root() -> Path:
    data = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
    return Path(str(data["game_dir"])) / "game"


def active_country_tags() -> frozenset[str]:
    data = json.loads(TAG_MAP.read_text(encoding="utf-8-sig"))
    return frozenset(
        {entry["engine_tag"] for entry in data["entries"]}
        | {"DUMMY", "PIR", "MER"}
    )


def neutralize_removed_law_country_groups(text: str) -> str:
    """Keep installed law groups parseable after medieval tags are removed."""
    active = active_country_tags()
    return LAW_COUNTRY_GROUP.sub(
        lambda match: match.group(0)
        if match.group("tag") in active
        else match.group("prefix") + "DUMMY",
        text,
    )


def neutralize_removed_country_scopes(text: str) -> str:
    """Keep dormant compatibility predicates typed after the AD 1 tag swap."""
    active = active_country_tags()
    return COUNTRY_SCOPE_REF.sub(
        lambda match: match.group(0)
        if match.group("tag") in active
        else "c:DUMMY",
        text,
    )


def mounted_files(relative: str) -> dict[str, Path]:
    """Return the effective base+DLC filename union for one registry."""
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
        for source in sorted(directory.rglob("*.txt")):
            mounted[source.relative_to(directory).as_posix()] = source
    return mounted


def structural_code(line: str) -> str:
    """Remove comments/quoted payload while preserving structural spacing."""
    rendered: list[str] = []
    quoted = False
    escaped = False
    for char in line:
        if escaped:
            rendered.append(" " if quoted else char)
            escaped = False
            continue
        if char == "\\" and quoted:
            rendered.append(" ")
            escaped = True
            continue
        if char == '"':
            quoted = not quoted
            rendered.append(" ")
            continue
        if char == "#" and not quoted:
            break
        rendered.append(" " if quoted else char)
    return "".join(rendered)


def brace_delta(line: str) -> int:
    code = structural_code(line)
    return code.count("{") - code.count("}")


def normalize_generated_script(text: str) -> str:
    """Remove installed whitespace defects without changing script tokens."""
    normalized: list[str] = []
    for line in text.splitlines():
        line = line.rstrip()
        prefix = line[: len(line) - len(line.lstrip(" \t"))]
        if " \t" in prefix:
            columns = len(prefix.expandtabs(4))
            tabs, spaces = divmod(columns, 4)
            line = "\t" * tabs + " " * spaces + line[len(prefix):]
        normalized.append(line)
    while normalized and not normalized[-1]:
        normalized.pop()
    return "\n".join(normalized) + "\n"


def inject_inline_false(line: str) -> str:
    code, marker, comment = line.partition("#")
    closing = code.rfind("}")
    if closing < 0:
        raise ValueError(f"expected an inline trigger block: {line!r}")
    suffix = f" {marker}{comment}" if marker else ""
    return (
        code[:closing]
        + "always = no "
        + code[closing:]
        + f" # {MARKER}"
        + suffix
    )


def collapse_marked_quarantine_gates(
    text: str, gate_names: tuple[str, ...]
) -> str:
    """Replace marked gates, so their unsafe medieval predicates never evaluate."""
    lines = text.splitlines()
    rendered: list[str] = []
    gate = re.compile(
        rf"^(?P<indent>\s*)(?P<key>{'|'.join(re.escape(name) for name in gate_names)})"
        r"\s*=\s*\{"
    )
    index = 0
    while index < len(lines):
        match = gate.match(structural_code(lines[index]))
        if not match:
            rendered.append(lines[index])
            index += 1
            continue
        end = _consume_block(lines, index, 0)
        block = lines[index:end]
        if not any(MARKER in line for line in block):
            rendered.extend(block)
        else:
            rendered.append(
                f"{match.group('indent')}{match.group('key')} = {{ always = no }} "
                f"# {MARKER}"
            )
        index = end
    return "\n".join(rendered) + "\n"


def collapse_nested_law_policy_gates(text: str) -> str:
    """Prevent the UI from evaluating child policies of a quarantined law."""
    lines = text.splitlines()

    def collapse(block: list[str]) -> list[str]:
        rendered = [block[0]]
        index = 1
        gate = re.compile(r"^(?P<indent>\s*)(?P<key>potential|allow)\s*=\s*\{")
        while index < len(block) - 1:
            match = gate.match(structural_code(block[index]))
            if not match:
                rendered.append(block[index])
                index += 1
                continue
            end = _consume_block(block, index, 0)
            if MARKER in block[index]:
                rendered.extend(block[index:end])
                index = end
                continue
            rendered.append(
                f"{match.group('indent')}{match.group('key')} = {{ always = no }} "
                f"# {NESTED_LAW_POLICY_MARKER}"
            )
            index = end
        rendered.append(block[-1])
        return rendered

    rendered: list[str] = []
    index = 0
    depth = 0
    while index < len(lines):
        code = structural_code(lines[index])
        top_level = TOP_LEVEL_KEY.match(code) if depth == 0 else None
        if top_level and brace_delta(lines[index]) > 0:
            end = _consume_block(lines, index, 0)
            block = lines[index:end]
            rendered.extend(collapse(block) if any(MARKER in line for line in block) else block)
            index = end
            continue
        rendered.append(lines[index])
        depth += brace_delta(lines[index])
        index += 1
    return "\n".join(rendered) + "\n"


def guard_absent_legacy_objects(
    text: str,
    gate_name: str | tuple[str, ...],
) -> str:
    """Make missing installed database objects optional inside retained bodies."""
    guarded: list[str] = []
    optional_scope = re.compile(
        r"(?P<link>(?:international_organization|character|dynasty):"
        r"[A-Za-z0-9_]+)\s*=\s*\{"
    )
    rhs_object = re.compile(
        r"(?:!=|\?=|(?<![?!<>])=)\s*(?:character|dynasty):[A-Za-z0-9_]+"
    )
    unsafe_dynamic_rhs = re.compile(
        r"(?:!=|\?=|(?<![?!<>])=)\s*"
        r"(?:root\.)?(?:ruler|heir|ruler_or_heir_if_regent)"
        r"(?:\.[A-Za-z_][A-Za-z0-9_]*)+"
    )
    optional_runtime_scope = re.compile(
        r"(?<![?.A-Za-z0-9_])"
        r"(?P<link>ruler|heir|ruler_or_heir_if_regent)"
        r"\s*=\s*\{"
    )
    optional_runtime_comparison = re.compile(
        r"(?<![?.A-Za-z0-9_])"
        r"(?P<link>government_type)\s*=\s*"
    )
    gates = (gate_name,) if isinstance(gate_name, str) else gate_name
    gate = re.compile(
        rf"^\s*(?:{'|'.join(re.escape(item) for item in gates)})\s*=\s*\{{"
    )
    depth = 0
    trigger_depth: int | None = None
    for line in text.splitlines():
        code = structural_code(line)
        delta = brace_delta(line)
        updated = optional_scope.sub(r"\g<link> ?= {", line)
        updated = re.sub(
            r"\bcapital\.market\s*=\s*\{",
            "capital.market ?= {",
            updated,
        )
        # Disabled registry bodies are still type-checked and some nested
        # policy/allow predicates are evaluated by the UI. Make nullable
        # runtime links safe throughout the quarantined definition, not only
        # in its outer availability gate.
        updated = optional_runtime_scope.sub(r"\g<link> ?= {", updated)
        updated = optional_runtime_comparison.sub(
            r"\g<link> ?= ",
            updated,
        )
        if trigger_depth is not None and (
            rhs_object.search(structural_code(updated))
            or unsafe_dynamic_rhs.search(structural_code(updated))
        ):
            if brace_delta(updated) != 0:
                raise ValueError(
                    f"unsupported multiline legacy-object comparison: {line!r}"
                )
            indent = updated[: len(updated) - len(updated.lstrip())]
            updated = (
                f"{indent}always = no "
                "# ANTIQVITAS absent legacy object comparison"
            )
        guarded.append(updated)
        previous_depth = depth
        depth += delta
        if (
            trigger_depth is None
            and gate.match(code)
            and delta > 0
        ):
            trigger_depth = previous_depth
        elif trigger_depth is not None and depth == trigger_depth:
            trigger_depth = None
    return "\n".join(guarded) + "\n"


def guard_retained_subject_war_links(text: str, source_name: str) -> str:
    """Make nullable war/leader links safe in retained subject interactions.

    Wars can briefly remain in ``every_current_war`` while one leader link is
    being torn down.  The installed interaction assumes both links exist, so
    merely opening or refreshing the subject-action UI can emit a script error.
    Its cached source list can also outlive either leader.  Filter incomplete
    wars up front, use optional link scopes throughout, and require the selected
    defender explicitly instead of treating every non-attacker as a defender.
    """
    if source_name == "intervene_in_subject_war.txt":
        unsafe_source = (
            "\t\t\tscope:recipient = {\n"
            "\t\t\t\tevery_current_war = {\n"
            "\t\t\t\t\tadd_to_list = source\n"
            "\t\t\t\t}\n"
            "\t\t\t}\n"
        )
        safe_source = (
            "\t\t\tscope:recipient = {\n"
            "\t\t\t\tevery_current_war = {\n"
            "\t\t\t\t\tlimit = {\n"
            "\t\t\t\t\t\tattacker_leader ?= { always = yes }\n"
            "\t\t\t\t\t\tdefender_leader ?= { always = yes }\n"
            "\t\t\t\t\t}\n"
            "\t\t\t\t\tadd_to_list = source\n"
            "\t\t\t\t}\n"
            "\t\t\t}\n"
        )
        unsafe_effect = (
            "\t\t\telse = {\n"
            "\t\t\t\tscope:actor = {\n"
            "\t\t\t\t\tjoin_war_as_defender = {\n"
            "\t\t\t\t\t\twar = prev\n"
            "\t\t\t\t\t\treason = intervene\n"
            "\t\t\t\t\t}\n"
            "\t\t\t\t}\n"
            "\t\t\t}\n"
        )
        safe_effect = (
            "\t\t\telse_if = {\n"
            "\t\t\t\tlimit = { defender_leader ?= scope:recipient }\n"
            "\t\t\t\tscope:actor = {\n"
            "\t\t\t\t\tjoin_war_as_defender = {\n"
            "\t\t\t\t\t\twar = prev\n"
            "\t\t\t\t\t\treason = intervene\n"
            "\t\t\t\t\t}\n"
            "\t\t\t\t}\n"
            "\t\t\t}\n"
        )
        for unsafe, safe, label in (
            (unsafe_source, safe_source, "unfiltered current-war source list"),
            (unsafe_effect, safe_effect, "implicit defender fallback"),
        ):
            if text.count(unsafe) != 1:
                raise ValueError(
                    f"{source_name}: expected one {label}, found {text.count(unsafe)}"
                )
            text = text.replace(unsafe, safe)
        links = ("attacker_leader", "defender_leader")
    elif source_name == "intervene_in_subject_civil_war.txt":
        unsafe_effect = (
            "\t\t\t\telse = {\n"
            "\t\t\t\t\tscope:actor = {\n"
            "\t\t\t\t\t\tjoin_war_as_defender = {\n"
            "\t\t\t\t\t\t\twar = prev\n"
            "\t\t\t\t\t\t\treason = intervene\n"
            "\t\t\t\t\t\t}\n"
            "\t\t\t\t\t}\n"
            "\t\t\t\t}\n"
        )
        safe_effect = (
            "\t\t\t\telse_if = {\n"
            "\t\t\t\t\tlimit = { defender_leader ?= scope:side }\n"
            "\t\t\t\t\tscope:actor = {\n"
            "\t\t\t\t\t\tjoin_war_as_defender = {\n"
            "\t\t\t\t\t\t\twar = prev\n"
            "\t\t\t\t\t\t\treason = intervene\n"
            "\t\t\t\t\t\t}\n"
            "\t\t\t\t\t}\n"
            "\t\t\t\t}\n"
        )
        if text.count(unsafe_effect) != 1:
            raise ValueError(
                f"{source_name}: expected one implicit defender fallback, "
                f"found {text.count(unsafe_effect)}"
            )
        text = text.replace(unsafe_effect, safe_effect)
        links = ("civil_war", "attacker_leader", "defender_leader")
    else:
        return text

    for link in links:
        text = re.sub(
            rf"(?m)^(?P<indent>[ \t]+){link}\s*=\s*",
            rf"\g<indent>{link} ?= ",
            text,
        )
    unsafe_links = re.findall(
        rf"(?m)^[ \t]+(?:{'|'.join(links)})\s*=\s*",
        text,
    )
    if unsafe_links:
        raise ValueError(
            f"{source_name}: retained unsafe war links after guard: {unsafe_links}"
        )
    return text


def align_civil_war_surrender_ai(text: str, source_name: str) -> str:
    """Make the retained surrender AI use its own two-to-one allow threshold.

    The installed interaction becomes selectable once the opponent has twice
    the actor's population, but its population AI weight only activates near a
    nine-to-one defeat.  Runtime civil wars therefore remained actionable but
    unused for years.  In a two-country split, 34% of combined population is
    just below the existing two-to-one boundary, so this preserves the engine's
    eligibility rule while making the AI actually exercise it after 12 months.
    """
    if source_name != "surrender_civil_war.txt":
        return text
    unsafe = (
        "\t\t\t\t\t\t\tadd = total_population\n"
        "\t\t\t\t\t\t\tmultiply = 0.1\n"
    )
    safe = (
        "\t\t\t\t\t\t\tadd = total_population\n"
        "\t\t\t\t\t\t\t# Match the select_trigger's two-to-one eligibility floor.\n"
        "\t\t\t\t\t\t\tmultiply = 0.34\n"
    )
    if text.count(unsafe) != 1:
        raise ValueError(
            f"{source_name}: expected one mismatched surrender AI threshold, "
            f"found {text.count(unsafe)}"
        )
    return text.replace(unsafe, safe, 1)


def disable_religious_aspect_ai_race(text: str, source_name: str) -> str:
    """Keep doctrine controls manual while avoiding EU5's multi-target AI race.

    In the V26 AD 1 runtime, the installed monthly AI tick queued every eligible
    religious-aspect target for a country at once. The first command filled the
    remaining slot and every later command then failed as ``perform_generic_action``
    (3,428 invalid commands by AD 4). ANTIQVITAS seeds a complete, faith-specific
    opening package, so the player actions remain useful but their unsafe autonomous
    scheduler must not run.
    """
    if source_name != "general_religion.txt":
        return text
    targets = {"add_religious_aspect", "change_religious_aspect"}
    changed = {key: 0 for key in targets}
    lines = text.splitlines()
    depth = 0
    current: str | None = None
    for index, line in enumerate(lines):
        code = structural_code(line)
        top_level = TOP_LEVEL_KEY.match(code) if depth == 0 else None
        if top_level:
            current = top_level.group("key")
        elif current in targets and depth == 1:
            replacement, count = re.subn(
                r"^(?P<indent>[ \t]*)ai_tick\s*=\s*monthly(?P<tail>[ \t]*(?:#.*)?)$",
                r"\g<indent>ai_tick = never\g<tail>",
                line,
            )
            if count:
                lines[index] = replacement
                changed[current] += count
        depth += brace_delta(line)
        if depth == 0:
            current = None
    if depth != 0 or changed != {key: 1 for key in targets}:
        raise ValueError(
            f"{source_name}: expected one monthly AI tick for each doctrine "
            f"action, found {changed}"
        )
    return "\n".join(lines) + "\n"


def guard_religious_offering_ai(text: str, source_name: str) -> str:
    """Require an owned offering target before the AI queues the action.

    EU5's generic-action planner begins running after its 36-month opening
    grace period.  The installed religious offering has a mandatory work-of-art
    selector but no AI prerequisite proving that the actor owns one, so nearly
    every polity posts an invalid ``perform_generic_action`` once per month.
    Keep the historically portable player action and autonomous use for actual
    art owners while preventing targetless commands.
    """
    if source_name != "purity.txt":
        return text
    needle = (
        "religious_offering = {\n"
        "\ticon = cleansing_ritual_purity\n"
        "\ttype = religious\n"
    )
    replacement = needle + (
        "\n\tai_prerequisite = {\n"
        "\t\tany_work_of_art_in_country = {\n"
        "\t\t\tthis != work_of_art:kusanagi_no_tsurugi\n"
        "\t\t\tthis != work_of_art:yata_no_kagami\n"
        "\t\t\tthis != work_of_art:yasakani_no_magatama\n"
        "\t\t}\n"
        "\t}\n"
    )
    if text.count(needle) != 1:
        raise ValueError(
            f"{source_name}: expected one religious_offering header, "
            f"found {text.count(needle)}"
        )
    guarded = text.replace(needle, replacement, 1)
    head, marker, offering = guarded.partition("religious_offering = {")
    tick = "\tai_tick = monthly\n\tai_tick_frequency = 1"
    if not marker or offering.count(tick) != 1:
        raise ValueError(
            f"{source_name}: expected one autonomous religious-offering tick"
        )
    offering = offering.replace(
        tick,
        "\tai_tick = never\n\tai_tick_frequency = 1",
        1,
    )
    return head + marker + offering


def disable_selected_generic_action_ai(text: str) -> str:
    """Convert selected retained action AI ticks to manual-only operation."""
    lines = text.splitlines()
    depth = 0
    current: str | None = None
    for index, line in enumerate(lines):
        code = structural_code(line)
        top_level = TOP_LEVEL_KEY.match(code) if depth == 0 else None
        if top_level:
            current = top_level.group("key")
        elif depth == 1:
            if current in GENERIC_ACTION_AI_DISABLED:
                lines[index] = re.sub(
                    r"^(?P<indent>[ \t]*)(?P<field>ai_tick|automation_tick)\s*=\s*(?:daily|weekly|monthly|quarterly|yearly)(?P<tail>[ \t]*(?:#.*)?)$",
                    r"\g<indent>\g<field> = never\g<tail>",
                    line,
                )
            if (
                current in generic_action_registry_adapters()
                and re.match(r"^\s*player_automated_category\s*=", code)
            ):
                lines[index] = (
                    "\t# player_automated_category removed: ANTIQVITAS "
                    "target-safe automation quarantine"
                )
        depth += brace_delta(line)
        if depth == 0:
            current = None
    if depth != 0:
        raise ValueError("unbalanced generic-action source during AI isolation")
    return "\n".join(lines) + "\n"


def prune_generic_action_definitions(
    text: str,
) -> tuple[str, int, int]:
    """Remove unavailable installed actions instead of registering dead stubs.

    EU5's generic-action planner evaluates actions merely because they are
    registered in an AI list.  A false ``potential`` and inert scheduler do
    not prevent it from posting the resulting invalid command.  Exact-mirror
    quarantine must therefore remove an unavailable action from both sides of
    the registry/list contract.  Comments and other top-level trivia are kept
    so source provenance remains readable.
    """
    allowed = generic_action_registry_adapters()
    lines = text.splitlines()
    rendered: list[str] = []
    total = 0
    kept = 0
    index = 0
    depth = 0
    while index < len(lines):
        line = lines[index]
        code = structural_code(line)
        top_level = TOP_LEVEL_KEY.match(code) if depth == 0 else None
        if top_level:
            if brace_delta(line) <= 0:
                raise ValueError(
                    "unsupported one-line generic-action definition: "
                    f"{top_level.group('key')}"
                )
            end = _consume_block(lines, index, 0)
            total += 1
            if top_level.group("key") in allowed:
                key = top_level.group("key")
                if key in GENERIC_ACTION_NOOP_DIAGNOSTIC:
                    block = [
                        f"{key} = {{",
                        "\ttype = owncountry",
                        "\tpotential = { always = yes }",
                        "\tallow = { always = yes }",
                        "\teffect = { }",
                        "\tai_tick = never",
                        "\tautomation_tick = never",
                        "\tai_will_do = 0",
                        "}",
                    ]
                else:
                    block = [item.rstrip() for item in lines[index:end]]
                if key in GENERIC_ACTION_RELAXED_DIAGNOSTIC:
                    block = relax_generic_action_validation(block)
                if key in GENERIC_ACTION_ALLOW_RELAXED_DIAGNOSTIC:
                    block = relax_generic_action_allow(block)
                if key in GENERIC_ACTION_SELECTOR_RELAXED_DIAGNOSTIC:
                    block = relax_generic_action_selectors(block)
                if key == "call_parliament":
                    block = guard_call_parliament_issue_ai_source(block)
                if top_level.group("key") in GENERIC_ACTION_AI_WEIGHT_DISABLED:
                    block = disable_generic_action_ai_weight(block)
                rendered.extend(block)
                kept += 1
            index = end
            continue
        rendered.append(line.rstrip())
        depth += brace_delta(line)
        index += 1
    if depth != 0:
        raise ValueError("unbalanced generic-action source during registry pruning")
    return "\n".join(rendered) + "\n", total, kept


def disable_generic_action_ai_weight(block: list[str]) -> list[str]:
    """Force one action block's planner weight to zero without hiding it."""
    rendered = [block[0]]
    index = 1
    depth = 1
    found = False
    pattern = re.compile(r"^\s*ai_will_do\s*=")
    while index < len(block) - 1:
        line = block[index]
        if depth == 1 and pattern.match(structural_code(line)):
            rendered.append(
                "\tai_will_do = 0 # ANTIQVITAS generic-action AI isolation"
            )
            found = True
            if brace_delta(line) > 0:
                index = _consume_block(block, index, depth)
            else:
                index += 1
            continue
        rendered.append(line)
        depth += brace_delta(line)
        index += 1
    if not found:
        rendered.insert(
            1,
            "\tai_will_do = 0 # ANTIQVITAS generic-action AI isolation",
        )
    rendered.append(block[-1])
    return rendered


def relax_generic_action_validation(block: list[str]) -> list[str]:
    """Keep native cache metadata while making one diagnostic action harmless."""
    rendered = [block[0]]
    index = 1
    depth = 1
    select_depth: int | None = None
    direct_blocks = {"potential", "allow", "ai_prerequisite"}
    while index < len(block) - 1:
        line = block[index]
        code = structural_code(line)
        delta = brace_delta(line)
        direct = re.match(
            r"^\s*(?P<field>potential|allow|ai_prerequisite|price|effect)\s*=",
            code,
        ) if depth == 1 else None
        if direct:
            field = direct.group("field")
            replacement = (
                f"\t{field} = {{ always = yes }}"
                if field in direct_blocks
                else "\tprice = 0"
                if field == "price"
                else "\teffect = { }"
            )
            rendered.append(replacement)
            if delta > 0:
                index = _consume_block(block, index, depth)
            else:
                index += 1
            continue
        if depth == 1 and re.match(r"^\s*select_trigger\s*=\s*\{", code):
            select_depth = depth + delta
        selector_gate = (
            re.match(r"^\s*(visible|enabled|show_if)\s*=", code)
            if select_depth is not None and depth == select_depth
            else None
        )
        if selector_gate:
            field = selector_gate.group(1)
            rendered.append(f"\t\t{field} = {{ always = yes }}")
            if delta > 0:
                index = _consume_block(block, index, depth)
            else:
                index += 1
            continue
        rendered.append(line)
        depth += delta
        index += 1
        if select_depth is not None and depth < select_depth:
            select_depth = None
    rendered.append(block[-1])
    return rendered


def relax_generic_action_allow(block: list[str]) -> list[str]:
    """Replace only a cached action's top-level allow trigger for diagnosis."""
    rendered = [block[0]]
    index = 1
    depth = 1
    replaced = 0
    while index < len(block) - 1:
        line = block[index]
        code = structural_code(line)
        delta = brace_delta(line)
        if depth == 1 and re.match(r"^\s*allow\s*=", code):
            rendered.append("\tallow = { always = yes }")
            replaced += 1
            if delta > 0:
                index = _consume_block(block, index, depth)
            else:
                index += 1
            continue
        rendered.append(line)
        depth += delta
        index += 1
    rendered.append(block[-1])
    if replaced != 1:
        raise ValueError(f"expected one top-level allow trigger, found {replaced}")
    return rendered


def relax_generic_action_selectors(block: list[str]) -> list[str]:
    """Relax selector gates without altering action availability or effects."""
    rendered = [block[0]]
    index = 1
    depth = 1
    select_depth: int | None = None
    seen = 0
    replaced = 0
    while index < len(block) - 1:
        line = block[index]
        code = structural_code(line)
        delta = brace_delta(line)
        if depth == 1 and re.match(r"^\s*select_trigger\s*=\s*\{", code):
            select_depth = depth + delta
        gate = (
            re.match(r"^\s*(visible|enabled|show_if)\s*=", code)
            if select_depth is not None and depth == select_depth
            else None
        )
        if gate:
            seen += 1
            if seen in PARLIAMENT_SELECTOR_GATE_DIAGNOSTIC:
                rendered.append(f"\t\t{gate.group(1)} = {{ always = yes }}")
                replaced += 1
                if delta > 0:
                    index = _consume_block(block, index, depth)
                else:
                    index += 1
                continue
        rendered.append(line)
        depth += delta
        index += 1
        if select_depth is not None and depth < select_depth:
            select_depth = None
    rendered.append(block[-1])
    if seen != 3 or replaced != len(PARLIAMENT_SELECTOR_GATE_DIAGNOSTIC):
        raise ValueError(
            "parliament selector gate inventory drift: "
            f"seen={seen} replaced={replaced}"
        )
    return rendered


def guard_call_parliament_issue_ai_source(block: list[str]) -> list[str]:
    """Keep AI enumeration stable while filtering the interactive issue list.

    EU5's hardcoded parliament scheduler requires the installed, unfiltered
    issue enumeration. Filtering that AI source can produce targetless
    ``perform_generic_action`` commands. The player list may safely exclude
    unavailable issues, and queued targets must remain visible after selection.
    """
    text = "\n".join(block)
    ai_source_pattern = re.compile(
        r"\t\tai_interaction_source_list = \{\n"
        r"\t\t\tscope:actor = \{\n"
        r"\t\t\t\tevery_possible_parliament_issue = \{\n"
        r"(?P<body>.*?)"
        r"\t\t\t\t\}\n"
        r"\t\t\t\}\n"
        r"\t\t\}",
        re.DOTALL,
    )
    ai_matches = list(ai_source_pattern.finditer(text))
    if len(ai_matches) != 1 or "add_to_list = source" not in ai_matches[0].group("body"):
        raise ValueError(
            "call_parliament AI issue-source inventory drift: expected one "
            "unfiltered every_possible_parliament_issue enumeration"
        )
    player_source = (
        "\t\tinteraction_source_list = {\n"
        "\t\t\tscope:actor = {\n"
        "\t\t\t\tevery_possible_parliament_issue = {\n"
        "\t\t\t\t\tadd_to_list = source\n"
        "\t\t\t\t}\n"
        "\t\t\t}\n"
        "\t\t}"
    )
    guarded_player_source = (
        "\t\tinteraction_source_list = {\n"
        "\t\t\tscope:actor = {\n"
        "\t\t\t\tevery_possible_parliament_issue = {\n"
        "\t\t\t\t\tif = {\n"
        "\t\t\t\t\t\tlimit = { is_available_for = scope:actor }\n"
        "\t\t\t\t\t\tadd_to_list = source\n"
        "\t\t\t\t\t}\n"
        "\t\t\t\t}\n"
        "\t\t\t}\n"
        "\t\t}"
    )
    if text.count(player_source) != 1:
        raise ValueError(
            "call_parliament player issue-source inventory drift: "
            f"found {text.count(player_source)}"
        )
    text = text.replace(player_source, guarded_player_source, 1)
    visible = (
        "\t\tvisible = {\n"
        "\t\t\tis_available_for = scope:actor\n"
        "\t\t}"
    )
    queued_safe_visible = (
        "\t\tvisible = {\n"
        "\t\t\talways = yes # targets are constrained by the ancient/player source lists\n"
        "\t\t}"
    )
    if text.count(visible) != 1:
        raise ValueError(
            "call_parliament issue visibility inventory drift: "
            f"found {text.count(visible)}"
        )
    text = text.replace(visible, queued_safe_visible, 1)
    return text.splitlines()


def quarantine_installed_parliament_issue_runtime(
    text: str,
    source_name: str,
) -> str:
    """Remove post-antique issues from hardcoded scheduler weighting.

    ``call_parliament`` must enumerate the complete installed issue registry or
    EU5 posts targetless generic-action commands. Consequently, a false
    ``potential`` alone is insufficient: the hardcoded scheduler can still
    weight and queue those definitions. Give every installed compatibility
    issue zero selection weight while preserving its registry references;
    removing the effects themselves makes engine-owned static modifiers appear
    unused at load. Namespaced ANTIQVITAS issues live in a separate generated
    file and are unaffected.
    """
    lines = text.splitlines()
    rendered: list[str] = []
    index = 0
    definitions = 0
    replacement = [
        "\tchance = {",
        "\t\tadd = 0 # ANTIQVITAS runtime quarantine",
        "\t}",
    ]
    while index < len(lines):
        code = structural_code(lines[index])
        top_level = TOP_LEVEL_KEY.match(code)
        if not top_level:
            rendered.append(lines[index])
            index += 1
            continue
        end = _consume_block(lines, index, 0)
        block = lines[index:end]
        transformed = [block[0]]
        block_index = 1
        depth = 1
        seen = False
        while block_index < len(block) - 1:
            line = block[block_index]
            direct = (
                re.match(
                    r"^\s*chance\s*=",
                    structural_code(line),
                )
                if depth == 1
                else None
            )
            if direct:
                transformed.extend(replacement)
                seen = True
                if brace_delta(line) > 0:
                    block_index = _consume_block(block, block_index, depth)
                else:
                    block_index += 1
                continue
            transformed.append(line)
            depth += brace_delta(line)
            block_index += 1
        if depth != 1:
            raise ValueError(
                f"{source_name}:{top_level.group('key')}: unbalanced issue body"
            )
        if not seen:
            transformed.extend(replacement)
        transformed.append(block[-1])
        rendered.extend(transformed)
        definitions += 1
        index = end
    if definitions == 0:
        raise ValueError(f"{source_name}: no parliament issues to quarantine")
    result = "\n".join(rendered) + "\n"
    if result.count("add = 0 # ANTIQVITAS runtime quarantine") != definitions:
        raise ValueError(f"{source_name}: parliament issue weight quarantine drift")
    return result


def render_quarantine(
    source: Path,
    surface: str,
    gate_name: str | tuple[str, ...] = "potential",
    *,
    preserve_generic_registry: bool = False,
) -> tuple[bytes, int]:
    """False-gate every top-level definition while preserving its body."""
    raw = source.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    source_definitions: int | None = None
    source_retained: int | None = None
    if surface == "laws":
        text, _ = replace_retained_law_definitions(text)
    elif surface == "generic_actions" and not preserve_generic_registry:
        text, source_definitions, source_retained = (
            prune_generic_action_definitions(text)
        )
    rendered = [
        f"# Generated by tools/m12_system_quarantine.py --write ({surface}).",
        f"# Installed source SHA256: {sha256(raw)}",
        (
            "# Unavailable definitions are omitted from the mounted registry."
            if surface == "generic_actions" and not preserve_generic_registry
            else "# Definitions stay resolvable but cannot enter AD 1 gameplay."
        ),
    ]
    depth = 0
    root_open = False
    root_has_gates: set[str] = set()
    root_retained = False
    definitions = 0
    retained_definitions = 0
    gates = (gate_name,) if isinstance(gate_name, str) else gate_name
    gate_patterns = {
        name: re.compile(rf"^\s*{re.escape(name)}\s*=\s*\{{")
        for name in gates
    }

    for line in text.splitlines():
        code = structural_code(line)
        delta = brace_delta(line)
        top_level = TOP_LEVEL_KEY.match(code)
        if depth == 0 and top_level:
            if delta <= 0:
                raise ValueError(
                    f"{source.name}: unsupported one-line top-level definition"
                )
            definitions += 1
            root_open = True
            root_has_gates = set()
            root_retained = (
                top_level.group("key")
                in RETAINED_ENGINE_ADAPTERS.get(surface, set())
                or (
                    surface == "generic_actions"
                    and top_level.group("key")
                    in GENERIC_ACTION_HARDCODED_ADAPTERS
                )
            )
            if root_retained:
                retained_definitions += 1
            rendered.append(line.rstrip())
            depth += delta
            continue
        matched_gate = next(
            (
                name for name, pattern in gate_patterns.items()
                if pattern.match(code)
            ),
            None,
        )
        if (
            surface in {"generic_actions", "character_interactions"}
            and root_open
            and not root_retained
            and depth == 1
        ):
            # The planner can enqueue a registered action before rechecking
            # its false potential. Quarantine therefore has to disable the
            # scheduler as well as the player-facing availability gate.
            line = re.sub(
                r"^(?P<indent>[ \t]*)(?P<field>ai_tick|automation_tick)\s*=\s*(?:daily|weekly|monthly|quarterly|yearly)(?P<tail>[ \t]*(?:#.*)?)$",
                r"\g<indent>\g<field> = never\g<tail>",
                line,
            )
        if (
            root_open
            and not root_retained
            and depth == 1
            and matched_gate is not None
        ):
            if delta == 0:
                rendered.append(inject_inline_false(line.rstrip()))
            else:
                rendered.append(line.rstrip())
                source_indent = code[: len(code) - len(code.lstrip())]
                indent_level = max(
                    1,
                    (len(source_indent.expandtabs(4)) + 3) // 4,
                )
                child_indent = "\t" * (indent_level + 1)
                rendered.append(f"{child_indent}always = no # {MARKER}")
            root_has_gates.add(matched_gate)
            depth += delta
            continue
        if root_open and not root_retained and depth == 1 and delta < 0:
            for missing_gate in gates:
                if missing_gate not in root_has_gates:
                    rendered.append(
                        f"\t{missing_gate} = {{ always = no }} # {MARKER}"
                    )
                    root_has_gates.add(missing_gate)
        if (
            surface == "disasters"
            and root_open
            and not root_retained
            and "has_complacency_effects" in line
        ):
            # Quarantined disasters must not populate the live complacency
            # tooltip (Majapahit/Mali/Delhi/Tsardom on AD 1 Rome).
            line = re.sub(
                r"has_complacency_effects\s*=\s*yes",
                "has_complacency_effects = no",
                line,
            )
        rendered.append(line.rstrip())
        depth += delta
        if root_open and depth == 0:
            root_open = False

    if depth != 0 or root_open:
        raise ValueError(f"{source.name}: unbalanced source while quarantining")
    if (
        definitions == 0
        and not (
            surface == "generic_actions"
            and not preserve_generic_registry
        )
    ):
        raise ValueError(f"{source.name}: no top-level definitions")
    if retained_definitions:
        rendered[2] = (
            "# Unretained definitions stay resolvable but cannot enter AD 1 gameplay."
        )
    quarantined = guard_absent_legacy_objects(
        neutralize_removed_country_scopes("\n".join(rendered) + "\n"),
        gate_name,
    )
    quarantined = neutralize_references(
        quarantined,
        remap_effects=True,
    )
    if surface == "chivalric_orders":
        # Disabled order definitions do not need their specialized predicates
        # evaluated at all. Character interactions deliberately retain their
        # original predicate text behind the leading false gate: some dormant
        # installed event helpers instantiate matching unlock-variable setters,
        # and EU5 diagnoses those setters as unused if their declared reads are
        # removed from the mounted interaction registry.
        quarantined = collapse_marked_quarantine_gates(quarantined, gates)
    if surface == "parliament_issues":
        quarantined = quarantine_installed_parliament_issue_runtime(
            quarantined,
            source.name,
        )
    if surface == "country_interactions":
        quarantined = guard_retained_subject_war_links(quarantined, source.name)
        quarantined = align_civil_war_surrender_ai(quarantined, source.name)
    if surface == "generic_actions":
        mounted_actions = (
            RETAINED_ENGINE_ADAPTERS["generic_actions"]
            - set(GENERIC_ACTION_AI_DISABLED)
        )
        if {
            "add_religious_aspect",
            "change_religious_aspect",
        } & mounted_actions:
            quarantined = disable_religious_aspect_ai_race(
                quarantined, source.name
            )
        if "religious_offering" in mounted_actions:
            quarantined = guard_religious_offering_ai(
                quarantined, source.name
            )
        quarantined = disable_selected_generic_action_ai(quarantined)
    if (
        surface == "generic_actions"
        and source.name == "hire_advisor.txt"
        and "hire_advisor" not in GENERIC_ACTION_AI_DISABLED
    ):
        # EU5 1.3.11 evaluates the final conditional inside create_character
        # before the new character object is valid.  Moving the optional trait
        # application immediately after creation preserves eunuch advisers but
        # prevents a null-character trigger error on the retained AI action.
        unsafe = (
            "\t\t\t\t\tif = {\n"
            "\t\t\t\t\t\tlimit = { exists = scope:spawn_eunuch_trigger_scope }\n"
            "\t\t\t\t\t\tadd_trait = trait:eunuch\n"
            "\t\t\t\t\t}\n"
            "\t\t\t\t\tsave_scope_as = new_character\n"
            "\t\t\t\t}\n"
        )
        safe = (
            "\t\t\t\t\tsave_scope_as = new_character\n"
            "\t\t\t\t}\n"
            "\t\t\t\tif = {\n"
            "\t\t\t\t\tlimit = { exists = scope:spawn_eunuch_trigger_scope }\n"
            "\t\t\t\t\tscope:new_character ?= { add_trait = trait:eunuch }\n"
            "\t\t\t\t}\n"
        )
        if quarantined.count(unsafe) != 1:
            raise ValueError(
                "hire_advisor.txt: expected one unsafe in-construction eunuch trait block"
            )
        quarantined = quarantined.replace(unsafe, safe)
    if (
        surface == "generic_actions"
        and source.name == "parliament.txt"
        and "prepare_for_war" not in GENERIC_ACTION_AI_DISABLED
    ):
        # ``prepare_for_war`` enumerates every country in diplomatic range,
        # including temporary or defeated country objects with no capital.
        # The installed trigger dereferences that optional link while building
        # the council action's target list, producing one script error per
        # landless candidate whenever the Government/Council view refreshes.
        # Preserve the retained action, but exclude those invalid candidates
        # before testing whether their capital is discovered.
        safe = PARLIAMENT_TARGET_CAPITAL_GUARD.replace(
            "\t\t\tcapital = {\n",
            "\t\t\texists = capital\n\t\t\tcapital = {\n",
            1,
        )
        if quarantined.count(PARLIAMENT_TARGET_CAPITAL_GUARD) != 1:
            raise ValueError(
                "parliament.txt: expected one unsafe prepare_for_war capital scan"
            )
        quarantined = quarantined.replace(PARLIAMENT_TARGET_CAPITAL_GUARD, safe)
    if surface == "laws":
        quarantined = neutralize_removed_law_country_groups(quarantined)
    dead_line = DEAD_LINES.get((surface, source.name))
    if dead_line is not None and dead_line.search(quarantined):
        quarantined, changed = dead_line.subn("", quarantined)
        if changed != 1:
            raise ValueError(
                f"{source.name}: expected one orphaned institution variable "
                f"setter, found {changed}"
            )
    market_guard_count = MARKET_SCOPE_GUARDS.get((surface, source.name), 0)
    if market_guard_count and "market = {" in quarantined:
        quarantined, changed = re.subn(
            r"(?m)^(?P<indent>[ \t]+)market\s*=\s*\{",
            r"\g<indent>market ?= {",
            quarantined,
        )
        if changed != market_guard_count:
            raise ValueError(
                f"{source.name}: expected {market_guard_count} unsafe market "
                f"links, found {changed}"
            )
    quarantined = normalize_generated_script(quarantined)
    output = quarantined.encode(
        "utf-8-sig" if has_bom else "utf-8"
    )
    guarded_definitions = definitions - retained_definitions
    if surface == "generic_actions" and not preserve_generic_registry:
        if source_definitions is None or source_retained is None:
            raise AssertionError("generic-action pruning census was not recorded")
        guarded_definitions = source_definitions - retained_definitions
    expected_markers = (
        (definitions - retained_definitions) * len(gates)
        if surface == "generic_actions" and not preserve_generic_registry
        else guarded_definitions * len(gates)
    )
    if output.decode("utf-8-sig").count(MARKER) != expected_markers:
        raise ValueError(f"{source.name}: quarantine marker count drift")
    return output, guarded_definitions


def active_quarantined_generic_ai_keys(text: str) -> set[str]:
    """Return unretained top-level actions that still own an active AI tick."""
    active: set[str] = set()
    retained = RETAINED_ENGINE_ADAPTERS["generic_actions"]
    depth = 0
    current: str | None = None
    for line in text.splitlines():
        code = structural_code(line)
        top_level = TOP_LEVEL_KEY.match(code) if depth == 0 else None
        if top_level:
            current = top_level.group("key")
        elif (
            current is not None
            and current not in retained
            and depth == 1
            and re.match(
                r"^\s*(?:ai_tick|automation_tick)\s*=\s*(?:daily|weekly|monthly|quarterly|yearly)\b",
                code,
            )
        ):
            active.add(current)
        depth += brace_delta(line)
        if depth == 0:
            current = None
    if depth != 0:
        raise ValueError("unbalanced rendered generic actions during AI audit")
    return active


def active_quarantined_character_ai_keys(text: str) -> set[str]:
    """Return disabled character interactions with a live AI scheduler."""
    active: set[str] = set()
    retained = RETAINED_ENGINE_ADAPTERS["character_interactions"]
    depth = 0
    current: str | None = None
    for line in text.splitlines():
        code = structural_code(line)
        top_level = TOP_LEVEL_KEY.match(code) if depth == 0 else None
        if top_level:
            current = top_level.group("key")
        elif (
            current is not None
            and current not in retained
            and depth == 1
            and re.match(
                r"^\s*(?:ai_tick|automation_tick)\s*=\s*"
                r"(?:daily|weekly|monthly|quarterly|yearly)\b",
                code,
            )
        ):
            active.add(current)
        depth += brace_delta(line)
        if depth == 0:
            current = None
    if depth != 0:
        raise ValueError(
            "unbalanced rendered character interactions during AI audit"
        )
    return active


def render_exploration_trigger_guard(source: Path) -> bytes:
    """Disable the post-antique exploration entry point without stubbing helpers."""
    raw = source.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    lines = raw.decode("utf-8-sig").splitlines()
    rendered: list[str] = []
    replaced = 0
    index = 0
    while index < len(lines):
        code = structural_code(lines[index])
        match = TOP_LEVEL_KEY.match(code)
        if match and match.group("key") == "country_can_start_exploration_trigger":
            end = _consume_block(lines, index, 0)
            rendered.extend(
                (
                    "country_can_start_exploration_trigger = {",
                    "\talways = no # ANTIQVITAS post-antique exploration quarantine",
                    "}",
                )
            )
            replaced += 1
            index = end
            continue
        rendered.append(lines[index])
        index += 1
    if replaced != 1:
        raise ValueError(
            "installed exploration trigger must contain exactly one country entry point"
        )
    header = (
        "# Generated by tools/m12_system_quarantine.py --write.\n"
        f"# Installed source SHA256: {sha256(raw)}\n"
    )
    output = normalize_generated_script(header + "\n".join(rendered) + "\n")
    return output.encode("utf-8-sig" if has_bom else "utf-8")


def render_hardcoded_price_guard(source: Path) -> bytes:
    """Remove the inherited stability race from AI rival replacement.

    Rival selection remains fully enabled.  Only its medieval five-stability
    price is removed: rival changes in the AD 1 political model are ordinary
    diplomatic realignments, and charging a mutable resource lets two valid AI
    plans invalidate one another between posting and execution.  A combined
    51.258 years of matched stock 1.3.11 controls produced no ``replace_rival``
    rejection, while R35 produced one in 20.192 ANTIQVITAS years.  Keep that
    command family actionable and fix the price instead of baselining it.
    """
    raw = source.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    lines = raw.decode("utf-8-sig").splitlines()
    rendered: list[str] = []
    replaced = 0
    index = 0
    while index < len(lines):
        code = structural_code(lines[index])
        match = TOP_LEVEL_KEY.match(code)
        if match and match.group("key") == "replace_rival":
            end = _consume_block(lines, index, 0)
            original = [
                structural_code(line).strip()
                for line in lines[index + 1:end - 1]
                if structural_code(line).strip()
            ]
            if original != ["stability = 5"]:
                raise ValueError(
                    "installed replace_rival price contract changed: "
                    f"expected stability = 5, found {original}"
                )
            rendered.extend(
                (
                    "replace_rival = {",
                    "\t# ANTIQVITAS diplomatic realignment: no mutable-resource price.",
                    "}",
                )
            )
            replaced += 1
            index = end
            continue
        rendered.append(lines[index])
        index += 1
    if replaced != 1:
        raise ValueError(
            "installed hardcoded prices must contain exactly one replace_rival entry"
        )
    header = (
        "# Generated by tools/m12_system_quarantine.py --write.\n"
        f"# Installed source SHA256: {sha256(raw)}\n"
        "# Rival replacement is free in ANTIQVITAS to avoid an AI stability-price race.\n"
    )
    output = normalize_generated_script(header + "\n".join(rendered) + "\n")
    return output.encode("utf-8-sig" if has_bom else "utf-8")


def render_ai_rival_replacement_guard() -> tuple[bytes, int]:
    """Prevent the hardcoded AI rival-replacement command from racing.

    EU5 plans ``replace_rival`` asynchronously.  Even with its mutable
    stability price removed, the command can become invalid before execution
    when a war begins or either rival relation changes.  The warning does not
    identify the actor and the command has no script callsite to guard.

    Rival criteria are explicitly AI-only.  Blocking every ANTIQVITAS country
    here therefore removes the unsafe hardcoded AI planner while preserving
    player rival controls, scripted ``add_rival``/``remove_rival`` effects,
    historical rivalry checks, and the mod's ancient rivalry situations.
    """
    tag_map = json.loads(TAG_MAP.read_text(encoding="utf-8"))
    entries = tag_map.get("entries")
    if not isinstance(entries, list):
        raise ValueError("AD 1 tag map has no entries list")
    tags = {
        str(entry.get("engine_tag", ""))
        for entry in entries
        if isinstance(entry, dict)
    }
    tags.update(ANCIENT_DYNAMIC_COUNTRY_TAGS)
    invalid = sorted(tag for tag in tags if not re.fullmatch(r"[A-Z0-9]{3}", tag))
    if invalid:
        raise ValueError(f"invalid AI rival-guard country tags: {invalid}")
    expected = int(tag_map.get("entry_count", -1))
    mapped = {
        str(entry.get("engine_tag", ""))
        for entry in entries
        if isinstance(entry, dict)
    }
    if len(entries) != expected or len(mapped) != expected:
        raise ValueError(
            "AD 1 rival-guard tag inventory drift: "
            f"entries={len(entries)}, unique_engine_tags={len(mapped)}, declared={expected}"
        )
    lines = [
        "# Generated by tools/m12_system_quarantine.py --write.",
        "# EU5 rival criteria are AI-only; `always = yes` blocks the listed",
        "# country from choosing any hardcoded replacement target. Player and",
        "# scripted ancient rival controls remain available.",
        "",
    ]
    for tag in sorted(tags):
        lines.extend(
            (
                f"{tag} = {{",
                "\tai_rule = {",
                "\t\talways = yes",
                "\t}",
                "}",
                "",
            )
        )
    return normalize_generated_script("\n".join(lines)).encode("utf-8-sig"), len(tags)


def render_insults_ruler_guard(source: Path) -> bytes:
    """Guard the installed low-stat insult before it reads recipient.ruler."""
    raw = source.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    pattern = re.compile(
        r"(?m)^(?P<indent>[ \t]+)has_regent\s*=\s*no\s*$"
        r"(?=\n(?P=indent)OR\s*=\s*\{\n"
        r"(?P=indent)[ \t]+ruler\.adm\s*<\s*30\n"
        r"(?P=indent)[ \t]+ruler\.dip\s*<\s*30)"
    )
    guarded, count = pattern.subn(
        r"\g<indent>has_regent = no\n"
        r"\g<indent>has_ruler = yes # ANTIQVITAS optional-ruler insult guard",
        text,
    )
    if count != 1:
        raise ValueError(
            "installed low-stat insult contract changed: expected one unsafe ruler read, "
            f"found {count}"
        )
    header = (
        "# Generated by tools/m12_system_quarantine.py --write.\n"
        f"# Installed source SHA256: {sha256(raw)}\n"
    )
    output = normalize_generated_script(header + guarded)
    return output.encode("utf-8-sig" if has_bom else "utf-8")


def render_hre_special_status_guard(source: Path) -> bytes:
    """Stop absent-HRE status scans from invoking a country-typed IO trigger."""
    raw = source.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    pattern = re.compile(
        r"(?m)^(?P<indent>[ \t]+)"
        r"hre_country_fulfills_imperial_religion_requirement\s*=\s*"
        r"\{\s*type\s*=\s*(?:electorship|general)\s*\}\s*$"
    )
    guarded, count = pattern.subn(
        r"\g<indent>always = no # ANTIQVITAS absent-HRE special-status guard",
        text,
    )
    if count != 5:
        raise ValueError(
            f"installed HRE special-status contract changed: expected 5 unsafe calls, found {count}"
        )
    header = (
        "# Generated by tools/m12_system_quarantine.py --write.\n"
        f"# Installed source SHA256: {sha256(raw)}\n"
    )
    output = normalize_generated_script(header + guarded)
    return output.encode("utf-8-sig" if has_bom else "utf-8")


def render_yearly_guard(source: Path) -> bytes:
    raw = source.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    if text.count(HRE_YEARLY_LINK) != 1:
        raise ValueError(
            "installed country_yearly.txt no longer has the expected HRE pulse link"
        )
    if text.count(TIMUR_YEARLY_DELAYED_EVENT) != 1:
        raise ValueError(
            "installed country_yearly.txt no longer has the expected delayed Timur event"
        )
    guarded = normalize_generated_script(neutralize_removed_country_scopes(
        text.replace(HRE_YEARLY_LINK, HRE_YEARLY_GUARD).replace(
            TIMUR_YEARLY_DELAYED_EVENT,
            (
                "\t\t# Direct reference prevents an orphan warning; its quarantined\n"
                "\t\t# current_date > 476.9.4 trigger is unreachable in ANTIQVITAS.\n"
                "\t\tflavor_tim.8\n"
            ),
        )
    ))
    header = (
        "# Generated by tools/m12_system_quarantine.py --write.\n"
        f"# Installed source SHA256: {sha256(raw)}\n"
        "# The AD 1 setup has no HRE; its optional scope must fail quietly.\n"
        "# The yearly pulse cannot repeatedly queue the delayed post-antique Timur event.\n"
    )
    output = (header + guarded).encode("utf-8-sig" if has_bom else "utf-8")
    return output


def render_on_action_scope_guard(source: Path) -> bytes:
    """Exact-mirror an on-action while typing every removed country scope."""
    raw = source.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    guarded = neutralize_removed_country_scopes(text)
    if guarded == text:
        raise ValueError(
            f"installed on-action no longer contains a removed country scope: {source}"
        )
    header = (
        "# Generated by tools/m12_system_quarantine.py --write.\n"
        f"# Installed source SHA256: {sha256(raw)}\n"
        "# Removed country scopes resolve through the typed AD 1 DUMMY sentinel.\n"
    )
    output = normalize_generated_script(header + guarded)
    return output.encode("utf-8-sig" if has_bom else "utf-8")


def validate_on_action_scope_union() -> list[str]:
    """Reject any mounted removed-tag on-action not covered by an exact mirror."""
    active = active_country_tags()
    sources = mounted_files("in_game/common/on_action")
    mounted_removed: set[str] = set()
    for relative, source in sources.items():
        tags = set(COUNTRY_SCOPE_REF.findall(
            source.read_text(encoding="utf-8-sig")
        ))
        if tags - active:
            mounted_removed.add(relative)
    expected = {
        "_hardcoded.txt",
        "country_monthly.txt",
        "country_yearly.txt",
        *(Path(relative).name for relative in ON_ACTION_SCOPE_GUARDS),
    }
    errors: list[str] = []
    if mounted_removed != expected:
        errors.append(
            "removed-country on-action inventory drift: expected="
            f"{sorted(expected)} mounted={sorted(mounted_removed)}"
        )
    for relative in sorted(expected):
        output = ROOT / "in_game/common/on_action" / relative
        if not output.is_file():
            errors.append(f"missing removed-country on-action mirror {relative}")
            continue
        tags = set(COUNTRY_SCOPE_REF.findall(
            output.read_text(encoding="utf-8-sig")
        ))
        removed = sorted(tags - active)
        if removed:
            errors.append(
                f"{relative} retains removed country scopes: {removed}"
            )
    return errors


def render_generic_action_ai_list(source: Path) -> tuple[bytes, int, int, int]:
    """Mirror an installed AI list while removing unavailable action keys."""
    raw = source.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    # The engine's special global list automatically absorbs any registered
    # action that is not assigned elsewhere.  Keep that list empty and route
    # the retained global actions through our ordinary dedicated list instead;
    # this prevents unrelated hardcoded actions from entering its slow path.
    allowed = (
        frozenset()
        if source.name.casefold() == "global_list.txt"
        else generic_action_ai_list_adapters()
    )
    lines = source.read_text(encoding="utf-8-sig").splitlines()
    rendered = [
        "# Generated by tools/m12_system_quarantine.py --write (generic_action_ai_lists).",
        f"# Installed source SHA256: {sha256(raw)}",
        "# Only runtime-retained ANTIQVITAS-safe action adapters remain registered.",
    ]
    depth = 0
    actions_depth: int | None = None
    list_count = 0
    kept = 0
    removed = 0
    removed_keys: list[str] = []
    for line in lines:
        code = structural_code(line)
        delta = brace_delta(line)
        if depth == 0 and TOP_LEVEL_KEY.match(code):
            list_count += 1
        if depth == 1 and re.match(r"^\s*actions\s*=\s*\{", code):
            actions_depth = depth + delta
            rendered.append(line.rstrip())
            depth += delta
            continue
        if actions_depth is not None and depth == actions_depth:
            action = re.fullmatch(
                r"\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*",
                code,
            )
            if action:
                if action.group("key") in allowed:
                    rendered.append(line.rstrip())
                    kept += 1
                else:
                    removed += 1
                    removed_keys.append(action.group("key"))
                depth += delta
                continue
        rendered.append(line.rstrip())
        depth += delta
        if actions_depth is not None and depth < actions_depth:
            actions_depth = None
    if depth != 0 or list_count == 0:
        raise ValueError(f"{source.name}: malformed generic-action AI list")
    payload = normalize_generated_script("\n".join(rendered) + "\n")
    encoded = payload.encode("utf-8-sig" if has_bom else "utf-8")
    return encoded, list_count, kept, removed


def render_portable_global_action_ai_list() -> bytes:
    """Schedule portable global actions without activating EU5's global list.

    In EU5 1.3.11, making the special installed ``global_list`` non-empty also
    admits unlisted hardcoded market actions.  Those actions repeatedly post
    invalid ``change_trade_capacity`` commands in both vanilla and the total
    conversion.  A normal dedicated list preserves the portable actions'
    autonomous utility evaluation without entering that engine-only path.
    """
    lines = [
        "# Generated by tools/m12_system_quarantine.py --write.",
        "# Dedicated list avoids EU5 1.3.11's invalid unlisted-market global path.",
        "antq_portable_global_action_list = {",
        "\tpotential = { always = yes }",
        "\tactions = {",
        *(f"\t\t{key}" for key in sorted(
            GENERIC_ACTION_GLOBAL_ADAPTERS & generic_action_registry_adapters()
        )),
        "\t}",
        "}",
        "",
    ]
    return normalize_generated_script("\n".join(lines)).encode("utf-8-sig")


def expected_outputs() -> tuple[dict[Path, bytes], dict[str, object]]:
    outputs: dict[Path, bytes] = {}
    records: list[dict[str, object]] = []
    totals: dict[str, int] = {}

    for surface, (relative, gate_name) in SURFACES.items():
        sources = mounted_files(relative)
        definitions = 0
        available_keys: set[str] = set()
        for name, source in sorted(sources.items()):
            # Registry readmes contain examples, not mounted definitions.
            if name.casefold() == "readme.txt":
                continue
            if name in EXCLUDED_BY_SURFACE.get(surface, set()):
                continue
            source_text = source.read_text(encoding="utf-8-sig")
            depth = 0
            for line in source_text.splitlines():
                code = structural_code(line)
                top_level = TOP_LEVEL_KEY.match(code)
                if depth == 0 and top_level:
                    available_keys.add(top_level.group("key"))
                depth += brace_delta(line)
            if not any(
                TOP_LEVEL.match(structural_code(line))
                for line in source_text.splitlines()
            ):
                continue
            output = ROOT / relative / name
            payload, count = render_quarantine(source, surface, gate_name)
            if surface == "generic_actions":
                unsafe_ai = active_quarantined_generic_ai_keys(
                    payload.decode("utf-8-sig")
                )
                if unsafe_ai:
                    raise ValueError(
                        f"{name}: quarantined actions retain active AI ticks: "
                        + ", ".join(sorted(unsafe_ai))
                    )
            if surface == "character_interactions":
                unsafe_ai = active_quarantined_character_ai_keys(
                    payload.decode("utf-8-sig")
                )
                if unsafe_ai:
                    raise ValueError(
                        f"{name}: quarantined character interactions retain "
                        "active AI ticks: " + ", ".join(sorted(unsafe_ai))
                    )
            if (
                surface == "generic_actions"
                and name == "hire_advisor.txt"
                and "hire_advisor" not in GENERIC_ACTION_AI_DISABLED
            ):
                rendered = payload.decode("utf-8-sig")
                if (
                    "scope:new_character ?= { add_trait = trait:eunuch }" not in rendered
                    or rendered.index("save_scope_as = new_character")
                    > rendered.index("scope:new_character ?= { add_trait = trait:eunuch }")
                ):
                    raise ValueError(
                        "hire_advisor retained adapter lost its post-creation trait guard"
                    )
            if (
                surface == "generic_actions"
                and name == "parliament.txt"
                and "prepare_for_war" not in GENERIC_ACTION_AI_DISABLED
            ):
                rendered = payload.decode("utf-8-sig")
                if rendered.count(
                    "\t\t\texists = capital\n\t\t\tcapital = {\n"
                    "\t\t\t\tis_discovered_by = scope:actor"
                ) != 1:
                    raise ValueError(
                        "parliament retained adapter lost its target-capital existence guard"
                    )
            if (
                surface == "generic_actions"
                and name == "general_religion.txt"
                and {
                    "add_religious_aspect",
                    "change_religious_aspect",
                }
                & (
                    RETAINED_ENGINE_ADAPTERS["generic_actions"]
                    - set(GENERIC_ACTION_AI_DISABLED)
                )
            ):
                rendered = payload.decode("utf-8-sig")
                if rendered.count("ai_tick = never") < 3:
                    raise ValueError(
                        "general_religion retained adapter lost its doctrine AI race guard"
                    )
            if (
                surface == "generic_actions"
                and name == "purity.txt"
                and "religious_offering" not in GENERIC_ACTION_AI_DISABLED
            ):
                rendered = payload.decode("utf-8-sig")
                offering = rendered.split("religious_offering = {", 1)[-1]
                if (
                    rendered.count("any_work_of_art_in_country = {") != 1
                    or offering.count("ai_tick = never") != 1
                ):
                    raise ValueError(
                        "purity retained adapter lost its offering-target AI guard"
                    )
            if surface == "country_interactions" and name in {
                "intervene_in_subject_war.txt",
                "intervene_in_subject_civil_war.txt",
            }:
                rendered = payload.decode("utf-8-sig")
                links = (
                    ("attacker_leader", "defender_leader")
                    if name == "intervene_in_subject_war.txt"
                    else ("civil_war", "attacker_leader", "defender_leader")
                )
                if re.search(
                    rf"(?m)^[ \t]+(?:{'|'.join(links)})\s*=\s*",
                    rendered,
                ):
                    raise ValueError(
                        f"{name}: retained adapter lost its optional war-link guards"
                    )
                if not re.search(
                    r"else_if\s*=\s*\{\s*limit\s*=\s*\{\s*"
                    r"defender_leader\s*\?=",
                    rendered,
                ):
                    raise ValueError(
                        f"{name}: retained adapter lost its explicit defender guard"
                    )
                if name == "intervene_in_subject_war.txt" and (
                    "every_current_war = {\n\t\t\t\t\tlimit = {\n"
                    "\t\t\t\t\t\tattacker_leader ?= { always = yes }\n"
                    "\t\t\t\t\t\tdefender_leader ?= { always = yes }"
                    not in rendered
                ):
                    raise ValueError(
                        "intervene_in_subject_war.txt: retained adapter lost its "
                        "complete-war source filter"
                    )
            if surface == "country_interactions" and name == "surrender_civil_war.txt":
                rendered = payload.decode("utf-8-sig")
                if MARKER in rendered or "surrender_civil_war = {" not in rendered:
                    raise ValueError(
                        "surrender_civil_war.txt: core civil-war termination "
                        "contract was quarantined or removed"
                    )
                if not all(
                    contract in rendered
                    for contract in (
                        "war_length >= 12",
                        "civil_war_opponent = {",
                        "multiply = 0.34",
                        "annex_country = {",
                        "reason = CivilWar",
                    )
                ):
                    raise ValueError(
                        "surrender_civil_war.txt: retained lifecycle contract drift"
                    )
            outputs[output] = payload
            definitions += count
            records.append(
                {
                    "surface": surface,
                    "relative": name,
                    "source": "<GAME_ROOT>/" + source.relative_to(game_root()).as_posix(),
                    "source_sha256": sha256(source.read_bytes()),
                    "definition_count": count,
                    "output": output.relative_to(ROOT).as_posix(),
                    "output_sha256": sha256(payload),
                }
            )
        totals[surface] = definitions
        unknown_retained = (
            RETAINED_ENGINE_ADAPTERS.get(surface, set()) - available_keys
        )
        if unknown_retained:
            raise ValueError(
                f"{surface} retains unknown mounted keys: "
                + ", ".join(sorted(unknown_retained))
            )

    ai_list_definitions = 0
    ai_list_kept = 0
    ai_list_removed = 0
    for name, source in sorted(
        mounted_files("in_game/common/generic_action_ai_lists").items()
    ):
        if name.casefold() == "readme.txt":
            continue
        payload, list_count, kept, removed = render_generic_action_ai_list(source)
        output = ROOT / "in_game/common/generic_action_ai_lists" / name
        outputs[output] = payload
        ai_list_definitions += list_count
        ai_list_kept += kept
        ai_list_removed += removed
        records.append(
            {
                "surface": "generic_action_ai_lists",
                "relative": name,
                "source": "<GAME_ROOT>/" + source.relative_to(game_root()).as_posix(),
                "source_sha256": sha256(source.read_bytes()),
                "definition_count": list_count,
                "kept_action_references": kept,
                "removed_action_references": removed,
                "output": output.relative_to(ROOT).as_posix(),
                "output_sha256": sha256(payload),
            }
        )
    if ai_list_definitions == 0 or ai_list_removed == 0:
        raise ValueError("generic-action AI-list quarantine found no mounted actions")
    portable_global_output = (
        ROOT
        / "in_game/common/generic_action_ai_lists"
        / "antq_portable_global_actions_list.txt"
    )
    portable_global_payload = render_portable_global_action_ai_list()
    outputs[portable_global_output] = portable_global_payload
    portable_actions = GENERIC_ACTION_GLOBAL_ADAPTERS & generic_action_registry_adapters()
    ai_list_kept += len(portable_actions)
    ai_list_definitions += 1
    records.append(
        {
            "surface": "generic_action_ai_lists",
            "relative": portable_global_output.name,
            "source": "<GENERATED>/manual-global-actions",
            "source_sha256": sha256(
                "\n".join(sorted(portable_actions)).encode("utf-8")
            ),
            "definition_count": 1,
            "kept_action_references": len(portable_actions),
            "removed_action_references": 0,
            "output": portable_global_output.relative_to(ROOT).as_posix(),
            "output_sha256": sha256(portable_global_payload),
        }
    )
    totals["generic_action_ai_lists"] = ai_list_definitions
    totals["generic_action_ai_references_kept"] = ai_list_kept
    totals["generic_action_ai_references_removed"] = ai_list_removed

    shinto_sources = mounted_files("in_game/common/religious_factions")
    shinto_source = shinto_sources.get("shinto.txt")
    if shinto_source is None:
        raise ValueError("mounted Shinto religious-faction registry is missing")
    shinto_raw = shinto_source.read_bytes()
    shinto_payload = (
        "# Generated by tools/m12_system_quarantine.py --write.\n"
        f"# Installed source SHA256: {sha256(shinto_raw)}\n"
        "# ANTIQVITAS has no medieval Shinto faction action registry.\n"
    ).encode("utf-8-sig" if shinto_raw.startswith(b"\xef\xbb\xbf") else "utf-8")
    shinto_output = ROOT / SHINTO_RELIGIOUS_FACTIONS
    outputs[shinto_output] = shinto_payload
    records.append(
        {
            "surface": "shinto_religious_faction_quarantine",
            "relative": "shinto.txt",
            "source": "<GAME_ROOT>/" + shinto_source.relative_to(game_root()).as_posix(),
            "source_sha256": sha256(shinto_raw),
            "definition_count": 5,
            "output": shinto_output.relative_to(ROOT).as_posix(),
            "output_sha256": sha256(shinto_payload),
        }
    )
    totals["shinto_religious_faction_quarantine"] = 5

    prices_source = game_root() / HARDCODED_PRICES
    prices_output = ROOT / HARDCODED_PRICES
    prices_payload = render_hardcoded_price_guard(prices_source)
    outputs[prices_output] = prices_payload
    records.append(
        {
            "surface": "rival_replacement_price_guard",
            "relative": "00_hardcoded.txt",
            "source": "<GAME_ROOT>/" + prices_source.relative_to(game_root()).as_posix(),
            "source_sha256": sha256(prices_source.read_bytes()),
            "definition_count": 1,
            "output": prices_output.relative_to(ROOT).as_posix(),
            "output_sha256": sha256(prices_payload),
        }
    )
    totals["rival_replacement_price_guard"] = 1

    rival_ai_output = ROOT / AI_RIVAL_GUARD
    rival_ai_payload, rival_ai_tags = render_ai_rival_replacement_guard()
    outputs[rival_ai_output] = rival_ai_payload
    records.append(
        {
            "surface": "ai_rival_replacement_guard",
            "relative": Path(AI_RIVAL_GUARD).name,
            "source": "<GENERATED>/AD-1-and-dynamic-ancient-country-tags",
            "source_sha256": sha256(
                (
                    TAG_MAP.read_text(encoding="utf-8")
                    + "\n"
                    + "\n".join(sorted(ANCIENT_DYNAMIC_COUNTRY_TAGS))
                ).encode("utf-8")
            ),
            "definition_count": rival_ai_tags,
            "output": rival_ai_output.relative_to(ROOT).as_posix(),
            "output_sha256": sha256(rival_ai_payload),
        }
    )
    totals["ai_rival_replacement_guard"] = rival_ai_tags

    for surface, (relative, gate_name) in TARGETED_QUARANTINES.items():
        source = game_root() / relative
        output = ROOT / relative
        payload, count = render_quarantine(source, surface, gate_name)
        outputs[output] = payload
        records.append(
            {
                "surface": surface,
                "relative": Path(relative).name,
                "source": "<GAME_ROOT>/" + source.relative_to(game_root()).as_posix(),
                "source_sha256": sha256(source.read_bytes()),
                "definition_count": count,
                "output": output.relative_to(ROOT).as_posix(),
                "output_sha256": sha256(payload),
            }
        )
        totals[surface] = count

    yearly_source = game_root() / YEARLY_ON_ACTION
    yearly_output = ROOT / YEARLY_ON_ACTION
    yearly_payload = render_yearly_guard(yearly_source)
    outputs[yearly_output] = yearly_payload
    records.append(
        {
            "surface": "hre_yearly_scope_guard",
            "relative": "country_yearly.txt",
            "source": "<GAME_ROOT>/" + yearly_source.relative_to(game_root()).as_posix(),
            "source_sha256": sha256(yearly_source.read_bytes()),
            "definition_count": 1,
            "output": yearly_output.relative_to(ROOT).as_posix(),
            "output_sha256": sha256(yearly_payload),
        }
    )
    totals["hre_yearly_scope_guard"] = 1

    on_action_scope_count = 0
    for relative in ON_ACTION_SCOPE_GUARDS:
        source = game_root() / relative
        output = ROOT / relative
        payload = render_on_action_scope_guard(source)
        outputs[output] = payload
        records.append(
            {
                "surface": "on_action_country_scope_guard",
                "relative": Path(relative).name,
                "source": "<GAME_ROOT>/" + source.relative_to(game_root()).as_posix(),
                "source_sha256": sha256(source.read_bytes()),
                "definition_count": 1,
                "output": output.relative_to(ROOT).as_posix(),
                "output_sha256": sha256(payload),
            }
        )
        on_action_scope_count += 1
    totals["on_action_country_scope_guard"] = on_action_scope_count

    exploration_source = game_root() / EXPLORATION_TRIGGER
    exploration_output = ROOT / EXPLORATION_TRIGGER
    exploration_payload = render_exploration_trigger_guard(exploration_source)
    outputs[exploration_output] = exploration_payload
    records.append(
        {
            "surface": "exploration_trigger_guard",
            "relative": "exploration_triggers.txt",
            "source": "<GAME_ROOT>/" + exploration_source.relative_to(game_root()).as_posix(),
            "source_sha256": sha256(exploration_source.read_bytes()),
            "definition_count": 1,
            "output": exploration_output.relative_to(ROOT).as_posix(),
            "output_sha256": sha256(exploration_payload),
        }
    )
    totals["exploration_trigger_guard"] = 1

    insults_source = game_root() / INSULTS_RULER_GUARD
    insults_output = ROOT / INSULTS_RULER_GUARD
    insults_payload = render_insults_ruler_guard(insults_source)
    outputs[insults_output] = insults_payload
    records.append(
        {
            "surface": "insults_optional_ruler_guard",
            "relative": "00_insults.txt",
            "source": "<GAME_ROOT>/" + insults_source.relative_to(game_root()).as_posix(),
            "source_sha256": sha256(insults_source.read_bytes()),
            "definition_count": 1,
            "output": insults_output.relative_to(ROOT).as_posix(),
            "output_sha256": sha256(insults_payload),
        }
    )
    totals["insults_optional_ruler_guard"] = 1

    hre_status_source = game_root() / HRE_SPECIAL_STATUSES
    hre_status_output = ROOT / HRE_SPECIAL_STATUSES
    hre_status_payload = render_hre_special_status_guard(hre_status_source)
    outputs[hre_status_output] = hre_status_payload
    records.append(
        {
            "surface": "hre_special_status_guard",
            "relative": "hre.txt",
            "source": "<GAME_ROOT>/" + hre_status_source.relative_to(game_root()).as_posix(),
            "source_sha256": sha256(hre_status_source.read_bytes()),
            "definition_count": 5,
            "output": hre_status_output.relative_to(ROOT).as_posix(),
            "output_sha256": sha256(hre_status_payload),
        }
    )
    totals["hre_special_status_guard"] = 5

    validate_inventory()
    sanitized_outputs: dict[Path, bytes] = {}
    post_campaign_dates = 0
    for output, payload in outputs.items():
        if output.suffix.lower() != ".txt":
            sanitized_outputs[output] = payload
            continue
        has_bom = payload.startswith(b"\xef\xbb\xbf")
        text, _changed = sanitize_dead_links(
            payload.decode("utf-8-sig"),
            label=output.relative_to(ROOT).as_posix(),
        )
        text, date_changes = sanitize_out_of_campaign_dates(text)
        post_campaign_dates += date_changes
        sanitized_outputs[output] = (
            (b"\xef\xbb\xbf" if has_bom else b"") + text.encode("utf-8")
        )
    outputs = sanitized_outputs
    # Round 5 owns the entire inherited situation registry and performs its
    # own date clamping. None of the remaining M12-owned system mirrors should
    # contain a post-campaign date; pin that separation of ownership.
    if post_campaign_dates != 0:
        raise ValueError(
            "mounted-system post-campaign date inventory drift: "
            f"expected 0, sanitized {post_campaign_dates}"
        )
    totals["post_campaign_dates_sanitized"] = post_campaign_dates
    by_relative = {
        output.relative_to(ROOT).as_posix(): payload
        for output, payload in outputs.items()
    }
    for record in records:
        relative = str(record["output"])
        if relative in by_relative:
            record["output_sha256"] = sha256(by_relative[relative])

    manifest = {
        "schema": 1,
        "policy": (
            "Preserve installed keys for reference resolution; false-gate every "
            "mounted post-antique definition, retain required engine adapters, "
            "guard optional installed scopes, and guard the HRE yearly pulse."
        ),
        "totals": totals,
        "files": records,
    }
    return outputs, manifest


def write() -> None:
    outputs, manifest = expected_outputs()
    previous: set[Path] = set()
    if MANIFEST.is_file():
        old = json.loads(MANIFEST.read_text(encoding="utf-8"))
        previous = {ROOT / str(record["output"]) for record in old.get("files", [])}
    for stale in sorted(previous - set(outputs)):
        if stale.is_file():
            stale.unlink()
    for output, payload in sorted(outputs.items()):
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(payload)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        "m12_system_quarantine: wrote "
        f"{len(outputs)} exact mirrors / "
        f"{sum(manifest['totals'].values())} guarded definitions"
    )


def check() -> bool:
    try:
        outputs, manifest = expected_outputs()
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"m12_system_quarantine: FAIL\n  - {exc}")
        return False
    errors: list[str] = []
    for output, payload in sorted(outputs.items()):
        if not output.is_file() or output.read_bytes() != payload:
            errors.append(f"stale or missing {output.relative_to(ROOT)}")
    expected_manifest = json.dumps(
        manifest, indent=2, ensure_ascii=False
    ) + "\n"
    if (
        not MANIFEST.is_file()
        or MANIFEST.read_text(encoding="utf-8") != expected_manifest
    ):
        errors.append(f"stale or missing {MANIFEST.relative_to(ROOT)}")
    errors.extend(validate_on_action_scope_union())
    # EU5 1.3.11 renders the retained lend-unit adapter through the unit-action
    # icon directory, while its shipped texture lives under unit_ability.  A
    # total conversion must bridge that engine path mismatch or merely opening
    # an army emits a VFS missing-texture error.
    runtime_icon = ROOT / LEND_UNIT_ICON
    source_icon = game_root() / LEND_UNIT_SOURCE_ICON
    if not source_icon.is_file():
        errors.append(f"missing installed lend-unit source icon {source_icon}")
    elif not runtime_icon.is_file():
        errors.append(f"missing retained-adapter icon {LEND_UNIT_ICON.as_posix()}")
    elif runtime_icon.read_bytes() != source_icon.read_bytes():
        errors.append(
            f"stale retained-adapter icon {LEND_UNIT_ICON.as_posix()}"
        )
    if errors:
        print("m12_system_quarantine: FAIL")
        for error in errors[:30]:
            print(f"  - {error}")
        if len(errors) > 30:
            print(f"  - ... {len(errors) - 30} more")
        return False
    totals = manifest["totals"]
    print(
        "m12_system_quarantine: PASS "
        f"({len(outputs)} mirrors; "
        f"{sum(totals.values())} guarded definitions)"
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        try:
            write()
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
            print(f"m12_system_quarantine: FAIL\n  - {exc}")
            return 1
        return 0
    return 0 if check() else 1


if __name__ == "__main__":
    raise SystemExit(main())
