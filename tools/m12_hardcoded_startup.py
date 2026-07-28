#!/usr/bin/env python3
"""Guard obsolete startup branches and apply generated AD 1 raw-material effects.

EU5's generic hardcoded startup handler retains several country-specific 1337
initializers and assumes that Catholic and Shinto IO instances always exist.
ANTIQVITAS replaces the start managers and deliberately has neither instance
at AD 1.  This renderer preserves the installed source byte-for-byte except
for safe-scope operators on those absent IO lookups and dynamic post-campaign
date gates around the dated country setup blocks.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

from dates import AntqDate, END
from generate_rgo_remap import rendered as rendered_rgo_remap
from generate_rgo_remap import runtime_worker_seeds
from legacy_institutions import neutralize_references


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
SOURCE_RELATIVE = Path("game/in_game/common/on_action/_hardcoded.txt")
OUTPUT = ROOT / "in_game/common/on_action/_hardcoded.txt"
COUNTRY_STATIC_RELATIVE = Path("game/main_menu/common/static_modifiers/country.txt")
COUNTRY_STATIC_OUTPUT = ROOT / "main_menu/common/static_modifiers/country.txt"
BANKRUPTCY_STATIC_OUTPUT = ROOT / "main_menu/common/static_modifiers/antq_bankruptcy.txt"
ECONOMY_GUI_RELATIVE = Path("game/in_game/gui/economy_lateralview.gui")
ECONOMY_GUI_OUTPUT = ROOT / "in_game/gui/economy_lateralview.gui"
CREDIT_GUI_RELATIVE = Path("game/in_game/gui/credit.gui")
CREDIT_GUI_OUTPUT = ROOT / "in_game/gui/credit.gui"
LOC_ROOT = ROOT / "main_menu/localization"
MIRROR_LANGUAGES = (
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
START_HEADER = re.compile(r"^\s*on_game_start\s*=\s*\{\s*(?:#.*)?$")
COUNTRY_HEADER = re.compile(r"^(?P<indent>\s*)c:(?P<tag>[A-Z]{3})\s*=\s*\{\s*(?:#.*)?$")
SAFE_SCOPE = re.compile(
    r"^(?P<indent>\s*)(?P<scope>religion:catholic|"
    r"international_organization:catholic_church|"
    r"international_organization:shinto)\s*=\s*\{"
)
RGO_SETUP_ANCHOR = re.compile(r"^\s*setup_area_preferences\s*=\s*yes\s*(?:#.*)?$")
EXPECTED_COUNTRY_GATES = Counter({
    "CHI": 1,
    "MAJ": 1,
    "JAP": 1,
    "BYZ": 2,
    "VER": 1,
    "TEU": 1,
    "BUL": 1,
})
EXPECTED_SAFE_SCOPES = Counter({
    "religion:catholic": 1,
    "international_organization:catholic_church": 2,
    "international_organization:shinto": 2,
})
EXPECTED_RGO_CHANGE_COUNT = 657
EXPECTED_CUSTOM_RGO_GOODS = frozenset({
    "antq_barley",
    "antq_camels",
    "antq_jade",
    "antq_naphtha",
    "antq_papyrus",
    "antq_silphium",
})
EXPECTED_ANNONA_SEED_LOCATIONS = frozenset({"cagliari", "faiyum", "sousse", "syracuse"})
LEGACY_INSTITUTION_CALLBACK = """#root = country, scope:target = institution
on_institution_embraced = {
	effect = {
		if = {
			limit = { scope:target = institution:scientific_revolution }
			root = { trigger_event_non_silently = institution_events.139 }
		}
		if = {
			limit = { scope:target = institution:artillery_institution }
			root = { trigger_event_non_silently = institution_events.115 }
		}
		if = {
			limit = { scope:target = institution:printing_press }
			root = { add_country_modifier = { modifier = printing_press_books years = -1 } }
		}
	}
}"""
ANTIQUE_INSTITUTION_CALLBACK = """#root = country, scope:target = institution
on_institution_embraced = {
	effect = {
		# ANTIQVITAS: retain unreachable registry anchors for two installed events.
		if = {
			limit = { always = no }
			root = { trigger_event_non_silently = institution_events.139 }
		}
		if = {
			limit = { always = no }
			root = { trigger_event_non_silently = institution_events.115 }
		}
	}
}"""


def source_path() -> Path:
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
        source = Path(str(config["game_dir"])) / SOURCE_RELATIVE
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot resolve installed hardcoded startup handler: {exc}") from exc
    if not source.is_file():
        raise ValueError(f"installed hardcoded startup handler is missing: {source}")
    return source


def installed_path(relative: Path) -> Path:
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
        source = Path(str(config["game_dir"])) / relative
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot resolve installed source {relative}: {exc}") from exc
    if not source.is_file():
        raise ValueError(f"installed source is missing: {source}")
    return source


def brace_delta(line: str) -> int:
    code = line.split("#", 1)[0]
    return code.count("{") - code.count("}")


def newline_for(line: str) -> str:
    return "\r\n" if line.endswith("\r\n") else "\n"


def runtime_rgo_effects(newline: str) -> list[str]:
    """Render the M5 ledger as effects at the one proven runtime surface.

    Location-template files are parsed but not instantiated by the installed
    build at bookmark creation.  ``change_raw_material`` is locally documented
    and console-proven against a vanilla good, while ``on_game_start`` is the
    earliest source-pinned effect context after AD 1 locations exist.
    """
    _, _, changes = rendered_rgo_remap()
    if len(changes) != EXPECTED_RGO_CHANGE_COUNT:
        raise ValueError(
            "runtime RGO inventory drift: "
            f"expected {EXPECTED_RGO_CHANGE_COUNT}, found {len(changes)}"
        )
    locations = [location for location, _, _, _, _ in changes]
    if len(locations) != len(set(locations)):
        raise ValueError("runtime RGO ledger contains duplicate location effects")
    custom_goods = {replacement_good for _, _, _, _, replacement_good in changes if replacement_good.startswith("antq_")}
    if custom_goods != EXPECTED_CUSTOM_RGO_GOODS:
        raise ValueError(
            "runtime custom-good inventory drift: "
            f"expected {sorted(EXPECTED_CUSTOM_RGO_GOODS)}, found {sorted(custom_goods)}"
        )
    annona_seeds = runtime_worker_seeds()
    if {location for location, *_ in annona_seeds} != EXPECTED_ANNONA_SEED_LOCATIONS:
        raise ValueError(
            "runtime annona-seed inventory drift: "
            f"expected {sorted(EXPECTED_ANNONA_SEED_LOCATIONS)}, "
            f"found {sorted(location for location, *_ in annona_seeds)}"
        )
    effects = [
        f"\t\t# ANTIQVITAS M5 runtime RGO remap; generated from docs/m5 source ledgers.{newline}",
    ]
    for location, _region, _operation, _source_good, replacement_good in sorted(changes):
        if replacement_good.startswith("antq_"):
            effects.extend(
                (
                    f"\t\tlocation:{location} = {{{newline}",
                    f"\t\t\tchange_raw_material = goods:{replacement_good}{newline}",
                    "\t\t\tchange_max_raw_material_workers = 1 "
                    f"# Seed one localized RGO level for a runtime-added good.{newline}",
                    f"\t\t}}{newline}",
                )
            )
        else:
            effects.append(
                f"\t\tlocation:{location} = {{ change_raw_material = goods:{replacement_good} }}{newline}"
            )
    effects.append(f"\t\t# ANTIQVITAS M5 annona grain capacity seeds; source ledger: docs/m5/annona_grain_anchors.csv.{newline}")
    for location, good, workers, _source, _confidence, _note in annona_seeds:
        effects.extend(
            (
                f"\t\tlocation:{location} = {{{newline}",
                f"\t\t\tchange_raw_material = goods:{good}{newline}",
                f"\t\t\tchange_max_raw_material_workers = {workers}{newline}",
                f"\t\t}}{newline}",
            )
        )
    return effects


def han_regency_effect(newline: str) -> list[str]:
    """Bind the source-led Wang Mang regent after the bookmark state exists.

    ``set_regent`` is the installed runtime API used by the native regency
    implementations.  It avoids inventing a pre-campaign ruler term solely to
    satisfy the bookmark loader's 1337-era succession-history assumption.
    """
    return [
        f"\t\t# ANTIQVITAS M6: source-led Wang Mang regency at the AD 1 bookmark.{newline}",
        f"\t\tc:XAR = {{ set_regent = character:antq_wang_mang }}{newline}",
    ]


def ancient_parliament_effect(newline: str) -> list[str]:
    """Assign the deliberative institution paired with each active M6 reform.

    History setup adds reforms directly and does not reliably fire their
    ``on_activate`` effect.  The installed ``on_game_start`` callback is the
    earliest locally proven country-effect surface after governments exist.
    """
    parliament_by_reforms = (
        ("antq_roman_senate", ("antq_principate", "antq_dominate")),
        ("antq_han_court_conference", ("antq_han_imperial_bureaucracy",)),
        ("antq_iranian_great_council", (
            "antq_parthian_king_of_kings", "antq_parthian_subkingdom",
            "antq_indo_scythian_kingship", "antq_sassanid_centralized_monarchy",
        )),
        ("antq_civic_assembly", ("antq_indo_greek_kingship", "antq_settled_town_cluster")),
        ("antq_gana_assembly", ("antq_indian_ganasangha",)),
        ("antq_confederation_council", ("antq_steppe_confederation",)),
        ("antq_tribal_assembly", ("antq_advanced_chiefdom", "antq_tribal_kingdom")),
        ("antq_sacral_court", ("antq_lankan_kingdom", "antq_kushite_dual_kingship")),
        ("antq_royal_council", (
            "antq_client_monarchy", "antq_buffer_kingdom",
            "antq_regional_kingship", "antq_early_korean_kingdom",
        )),
    )
    lines = [
        f"\t\t# ANTIQVITAS S2: establish each reform's source-bounded ancient council.{newline}",
        f"\t\tevery_country = {{{newline}",
    ]
    for parliament, reforms in parliament_by_reforms:
        lines.extend((f"\t\t\tif = {{{newline}", f"\t\t\t\tlimit = {{{newline}", f"\t\t\t\t\tOR = {{{newline}"))
        lines.extend(
            f"\t\t\t\t\t\thas_reform = government_reform:{reform}{newline}"
            for reform in reforms
        )
        lines.extend((
            f"\t\t\t\t\t}}{newline}",
            f"\t\t\t\t}}{newline}",
            f"\t\t\t\tset_parliament_type = parliament_type:{parliament}{newline}",
            f"\t\t\t}}{newline}",
        ))
    lines.append(f"\t\t}}{newline}")
    return lines


def replace_top_level_block(text: str, key: str, replacement: str) -> str:
    """Replace one top-level Clausewitz block while preserving surrounding text."""
    header = re.compile(rf"(?m)^{re.escape(key)}\s*=\s*\{{\s*(?:#.*)?$")
    matches = list(header.finditer(text))
    if len(matches) != 1:
        raise ValueError(f"expected one top-level {key} block, found {len(matches)}")
    start = matches[0].start()
    depth = 0
    end: int | None = None
    for match in re.finditer(r"[{}]", text[matches[0].start():]):
        depth += 1 if match.group() == "{" else -1
        if depth == 0:
            end = matches[0].start() + match.end()
            break
    if end is None:
        raise ValueError(f"top-level {key} block does not close")
    return text[:start] + replacement + text[end:]


def neutral_country_static() -> bytes:
    """Neutralize the engine's year-one epoch bankruptcy pseudo-modifier."""
    source = installed_path(COUNTRY_STATIC_RELATIVE)
    raw = source.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    replacement = newline.join(
        (
            "is_bankrupt = {",
            "\tgame_data = {",
            "\t\tcategory = country",
            "\t}",
            "",
            "\t# ANTIQVITAS: EU5 treats its minimum date as a recent-bankruptcy",
            "\t# timestamp. Genuine bankruptcies receive the complete effects",
            "\t# through antq_genuine_bankruptcy in on_bankruptcy instead.",
            "}",
        )
    )
    result = replace_top_level_block(text, "is_bankrupt", replacement)
    return (b"\xef\xbb\xbf" if bom else b"") + result.encode("utf-8")


def genuine_bankruptcy_static() -> bytes:
    """Reproduce the installed bankruptcy consequences under a safe custom key."""
    text = """antq_genuine_bankruptcy = {
	game_data = {
		category = country
	}

	total_loan_capacity_modifier = -0.5
	global_estate_target_satisfaction = small_permanent_target_satisfaction_penalty
	global_crown_estate_power = -0.9
	global_pop_promotion_speed = -0.05
	global_pop_demotion_speed = 0.20
	land_morale_modifier = -0.9
	naval_morale_modifier = -0.9
	research_speed_modifier = -0.9
	global_construction_speed = -0.9
	monthly_towards_traditional_economy = societal_value_huge_monthly_move
}
"""
    return b"\xef\xbb\xbf" + text.encode("utf-8")


def bankruptcy_gui(relative: Path) -> bytes:
    """Show the native bankruptcy banner only for a real bankruptcy callback."""
    source = installed_path(relative)
    raw = source.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    native_visibility = 'visible = "[GetPlayer.GetEconomy.IsDuringBankruptcy]"'
    custom_visibility = (
        "visible = "
        '"[GetPlayer.MakeScope.GetVariable(\'antq_genuine_bankruptcy\').IsSet]"'
    )
    if text.count(native_visibility) != 1:
        raise ValueError(
            f"{relative}: expected one native bankruptcy-banner visibility"
        )
    if text.count("ShowModifierEffect('is_bankrupt')") != 1:
        raise ValueError(f"{relative}: expected one native bankruptcy tooltip")
    text = text.replace(native_visibility, custom_visibility, 1)
    text = text.replace(
        "ShowModifierEffect('is_bankrupt')",
        "ShowModifierEffect('antq_genuine_bankruptcy')",
        1,
    )
    return (b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8")


def bankruptcy_localization(language: str) -> bytes:
    text = (
        f"l_{language}:\n"
        ' STATIC_MODIFIER_NAME_antq_genuine_bankruptcy: "Bankruptcy"\n'
        ' STATIC_MODIFIER_DESC_antq_genuine_bankruptcy: "A genuine state default '
        'has disrupted credit, administration, morale, and construction."\n'
    )
    return b"\xef\xbb\xbf" + text.encode("utf-8")


def render() -> bytes:
    source = source_path()
    raw = source.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    lines = raw.decode("utf-8-sig").splitlines(keepends=True)
    rendered: list[str] = []
    depth = 0
    in_start = False
    gated_depth: int | None = None
    country_gates: Counter[str] = Counter()
    safe_scopes: Counter[str] = Counter()
    out_of_campaign = AntqDate(*END).engine()
    rgo_injected = False

    for line in lines:
        code = line.split("#", 1)[0]
        if depth == 0 and START_HEADER.match(code):
            in_start = True

        country = COUNTRY_HEADER.match(code) if in_start and gated_depth is None else None
        safe = SAFE_SCOPE.match(code) if in_start and gated_depth is None else None

        if in_start and not rgo_injected and RGO_SETUP_ANCHOR.match(code):
            rendered.append(line)
            rendered.extend(runtime_rgo_effects(newline_for(line)))
            rendered.extend(han_regency_effect(newline_for(line)))
            rendered.extend(ancient_parliament_effect(newline_for(line)))
            rgo_injected = True
            depth += brace_delta(code)
            continue

        if country is not None and country.group("tag") in EXPECTED_COUNTRY_GATES:
            indent = country.group("indent")
            rendered.append(line)
            depth += brace_delta(code)
            gated_depth = depth
            newline = newline_for(line)
            rendered.append(f"{indent}\tif = {{{newline}")
            rendered.append(
                f"{indent}\t\tlimit = {{ current_date > {out_of_campaign} }} "
                "# ANTIQVITAS guards dated vanilla startup\n"
            )
            country_gates[country.group("tag")] += 1
            continue

        if safe is not None:
            scope = safe.group("scope")
            rendered.append(line.replace(" =", " ?=", 1))
            safe_scopes[scope] += 1
            depth += brace_delta(code)
        elif gated_depth is not None and depth == gated_depth and code.strip() == "}":
            indent = line[: len(line) - len(line.lstrip())]
            rendered.append(f"{indent}\t}}{newline_for(line)}")
            rendered.append(line)
            depth += brace_delta(code)
            gated_depth = None
        elif gated_depth is not None:
            rendered.append(f"\t{line}" if line.strip() else line)
            depth += brace_delta(code)
        else:
            rendered.append(line)
            depth += brace_delta(code)

        if depth < 0:
            raise ValueError("hardcoded startup handler brace depth became negative")
        if in_start and depth == 0:
            in_start = False

    if depth != 0:
        raise ValueError(f"hardcoded startup handler brace depth ends at {depth}")
    if gated_depth is not None:
        raise ValueError("dated country setup block did not close")
    if not rgo_injected:
        raise ValueError("installed startup handler is missing the runtime RGO insertion anchor")
    if country_gates != EXPECTED_COUNTRY_GATES:
        raise ValueError(
            f"dated startup-country inventory drift: expected={dict(EXPECTED_COUNTRY_GATES)} "
            f"found={dict(country_gates)}"
        )
    if safe_scopes != EXPECTED_SAFE_SCOPES:
        raise ValueError(
            f"startup IO scope inventory drift: expected={dict(EXPECTED_SAFE_SCOPES)} "
            f"found={dict(safe_scopes)}"
        )
    text = "".join(rendered)
    newline = "\r\n" if "\r\n" in text else "\n"
    legacy_callback = LEGACY_INSTITUTION_CALLBACK.replace("\n", newline)
    antique_callback = ANTIQUE_INSTITUTION_CALLBACK.replace("\n", newline)
    if text.count(legacy_callback) != 1:
        raise ValueError("installed post-antique institution callback inventory drift")
    text = text.replace(legacy_callback, antique_callback)
    bankruptcy_anchor = (
        f"on_bankruptcy = {{{newline}"
        f"\teffect = {{{newline}"
    )
    if text.count(bankruptcy_anchor) != 1:
        raise ValueError("installed on_bankruptcy callback inventory drift")
    bankruptcy_adapter = (
        bankruptcy_anchor
        + f"\t\t# ANTIQVITAS: distinguish a real default from the year-one epoch ghost.{newline}"
        f"\t\tset_variable = {{ name = antq_genuine_bankruptcy value = yes years = 5 }}{newline}"
        f"\t\tif = {{{newline}"
        f"\t\t\tlimit = {{ has_variable = antq_genuine_bankruptcy }}{newline}"
        f"\t\t\tadd_country_modifier = {{ modifier = antq_genuine_bankruptcy years = 5 }}{newline}"
        f"\t\t}}{newline}"
    )
    text = text.replace(bankruptcy_anchor, bankruptcy_adapter, 1)
    result = neutralize_references(text, remap_effects=False).encode("utf-8")
    return (b"\xef\xbb\xbf" if has_bom else b"") + result


def write() -> None:
    outputs = {
        OUTPUT: render(),
        COUNTRY_STATIC_OUTPUT: neutral_country_static(),
        BANKRUPTCY_STATIC_OUTPUT: genuine_bankruptcy_static(),
        ECONOMY_GUI_OUTPUT: bankruptcy_gui(ECONOMY_GUI_RELATIVE),
        CREDIT_GUI_OUTPUT: bankruptcy_gui(CREDIT_GUI_RELATIVE),
    }
    for language in MIRROR_LANGUAGES:
        outputs[
            LOC_ROOT / language / f"antq_m12_bankruptcy_l_{language}.yml"
        ] = bankruptcy_localization(language)
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        print(f"m12_hardcoded_startup: wrote {path.relative_to(ROOT)}")


def check() -> bool:
    try:
        expected = render()
    except (OSError, ValueError) as exc:
        print(f"m12_hardcoded_startup: FAIL\n  - {exc}")
        return False
    expected_outputs = {
        OUTPUT: expected,
        COUNTRY_STATIC_OUTPUT: neutral_country_static(),
        BANKRUPTCY_STATIC_OUTPUT: genuine_bankruptcy_static(),
        ECONOMY_GUI_OUTPUT: bankruptcy_gui(ECONOMY_GUI_RELATIVE),
        CREDIT_GUI_OUTPUT: bankruptcy_gui(CREDIT_GUI_RELATIVE),
    }
    for language in MIRROR_LANGUAGES:
        expected_outputs[
            LOC_ROOT / language / f"antq_m12_bankruptcy_l_{language}.yml"
        ] = bankruptcy_localization(language)
    stale = [
        path.relative_to(ROOT)
        for path, content in expected_outputs.items()
        if not path.is_file() or path.read_bytes() != content
    ]
    if stale:
        print(
            "m12_hardcoded_startup: FAIL\n"
            "  - stale or missing " + ", ".join(map(str, stale))
        )
        return False
    print(
        "m12_hardcoded_startup: PASS "
        f"(5 safe absent-IO scopes; 8 dated country-startup gates; "
        f"{EXPECTED_RGO_CHANGE_COUNT} runtime RGO corrections; "
        "1 low-year bankruptcy epoch adapter)"
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
        except (OSError, ValueError) as exc:
            print(f"m12_hardcoded_startup: FAIL\n  - {exc}")
            return 1
        return 0
    return 0 if check() else 1


if __name__ == "__main__":
    raise SystemExit(main())
