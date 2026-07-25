#!/usr/bin/env python3
"""Run ANTIQVITAS validation, smoke, and art-review targets.

This module is the single source of truth for repository check ordering.  The
Makefile and make.cmd wrappers deliberately delegate here so the Windows and
make entry points cannot silently drift apart.
"""
from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Command:
    script: str
    args: tuple[str, ...] = ()

    @property
    def path(self) -> Path:
        return ROOT / self.script

    def argv(self) -> list[str]:
        return [sys.executable, str(self.path), *self.args]

    def display(self) -> str:
        return shlex.join([sys.executable, self.script, *self.args])


VALIDATE_COMMANDS = (
    Command("tools/pdxlint.py"),
    Command("tools/m6_power.py", ("--check",)),
    Command("tools/world_roster.py"),
    Command("tools/generate_tag_map.py", ("--check",)),
    Command("tools/generate_m4_definitions.py", ("--check",)),
    Command("tools/generate_m4_tier2_names.py", ("--check",)),
    Command("tools/generate_m4_tier2_wide_names.py", ("--check",)),
    Command("tools/generate_m4_tier2_remote_names.py", ("--check",)),
    Command("tools/generate_m4_tier2_far_names.py", ("--check",)),
    Command("tools/generate_m4_tier2_ultra_names.py", ("--check",)),
    Command("tools/generate_m4_tier3_names.py", ("--check",)),
    Command("tools/generate_m4_roman_names.py", ("--check",)),
    Command("tools/m4_priority_location_names.py", ("--check",)),
    Command("tools/generate_dynamic_names.py", ("--check",)),
    Command("tools/generate_m4_location_name_corrections.py", ("--check",)),
    Command("tools/m4_roman_location_name_audit.py", ("--check",)),
    Command("tools/m4_gallic_atlas.py", ("--check",)),
    Command("tools/m4_galatian_atlas.py", ("--check",)),
    Command("tools/culture_template_inventory.py", ("--check",)),
    Command("tools/m5_roman_economy_art.py", ("--check",)),
    Command("tools/m5_building_circle_reart.py", ("--check",)),
    Command("tools/m5_building_icon_audit.py", ("--check",)),
    Command("tools/generate_ancient_goods.py", ("--check",)),
    Command("tools/generate_rgo_remap.py", ("--check",)),
    Command("tools/m5_roman_buildings.py", ("--check",)),
    Command("tools/m5_ancient_building_replacements.py", ("--check",)),
    Command("tools/m5_tenth_buildings.py", ("--check",)),
    Command("tools/m5_eleventh_buildings.py", ("--check",)),
    Command("tools/m5_twelfth_buildings.py", ("--check",)),
    Command("tools/m5_roman_economy.py", ("--check",)),
    Command("tools/m5_regional_buildings.py", ("--check",)),
    Command("tools/m5_building_quarantine.py", ("--check",)),
    Command("tools/m5_market_scope_guard.py", ("--check",)),
    Command("tools/m5_building_audit.py"),
    Command("tools/m5_roman_economy_audit.py", ("--check",)),
    Command("tools/m7_war.py", ("--check",)),
    Command("tools/m7_levy_scope_guard.py", ("--check",)),
    Command("tools/m8_knowledge.py", ("--check",)),
    Command("tools/m8_legacy_institution_purge.py", ("--check",)),
    Command("tools/m9_diplomacy.py", ("--check",)),
    Command("tools/m10_history.py", ("--check",)),
    Command("tools/m10_second_century.py", ("--check",)),
    Command("tools/m10_third_century.py", ("--check",)),
    Command("tools/m10_fourth_century.py", ("--check",)),
    Command("tools/m10_final_century.py", ("--check",)),
    Command("tools/m11_age_art.py", ("--check",)),
    Command("tools/m11_court_backgrounds.py", ("--check",)),
    Command("tools/m11_loading_screens.py", ("--check",)),
    Command("tools/m12_loading_tips.py", ("--check",)),
    Command("tools/m12_frontend_assets.py"),
    Command("tools/m12_country_history.py", ("--check",)),
    Command("tools/m12_pop_presentation.py", ("--check",)),
    Command("tools/m12_rank_presentation.py", ("--check",)),
    Command("tools/m12_unit_quarantine.py", ("--check",)),
    Command("tools/m12_unit_art.py", ("--check",)),
    Command("tools/m12_disease_safety.py", ("--check",)),
    Command("tools/m12_installed_content_census.py", ("--check",)),
    Command("tools/m11_advance_icons.py", ("--check",)),
    Command("tools/m11_flavor_events.py", ("--check",)),
    Command("tools/m11_dynamic_coas.py", ("--check",)),
    Command("tools/m11_common_icons.py", ("--check",)),
    Command("tools/m11_privilege_icons.py", ("--check",)),
    Command("tools/m11_ui_asset_ledger.py", ("--check",)),
    Command("tools/m11_ui_asset_contact_sheet.py", ("--check",)),
    Command("tools/m11_decisions.py", ("--check", "--scope", "all")),
    Command("tools/m11_message_overlay.py", ("--check", "--scope", "all")),
    Command("tools/m11_localization.py", ("--check",)),
    Command("tools/m12_disable_missions.py", ("--check",)),
    Command("tools/m12_game_rules.py", ("--check",)),
    Command("tools/m12_hardcoded_startup.py", ("--check",)),
    Command("tools/m12_coa_scope_guard.py", ("--check",)),
    Command("tools/m12_parliament_scope_guard.py", ("--check",)),
    Command("tools/m12_country_loc_scope_guard.py", ("--check",)),
    Command("tools/m12_flag_capital_guard.py", ("--check",)),
    Command("tools/m12_marriage_policy_guard.py", ("--check",)),
    Command("tools/m12_anachronism_audit.py", ("--check",)),
    Command("tools/m12_disable_historical_hints.py", ("--check",)),
    Command("tools/m12_event_quarantine.py", ("--check",)),
    Command("tools/m12_culture_presence.py", ("--check",)),
    Command("tools/p4_manual_regression.py", ("--check",)),
    Command("tools/generate_country_definitions.py", ("--check",)),
    Command("tools/capital_mapper.py", ("--check",)),
    Command("tools/extract_map_coordinates.py", ("--check",)),
    Command("tools/capital_geography.py", ("--check",)),
    Command("tools/ownership_map.py", ("--check",)),
    Command("tools/territory_coverage.py"),
    Command("tools/generate_start_mirror.py", ("--check",)),
    Command("tools/m3_political_map.py"),
    Command("tools/dates.py", ("--check-m2",)),
    Command("tools/popcheck.py"),
)

SMOKE_COMMANDS = (Command("tools/smoketest.py"),)
ART_REVIEW_COMMANDS = (
    Command("tools/m11_contact_sheet.py"),
    Command("tools/m11_ui_asset_contact_sheet.py", ("--write",)),
)


def run_commands(label: str, commands: tuple[Command, ...], *, dry_run: bool) -> int:
    if not dry_run:
        missing = [command.script for command in commands if not command.path.is_file()]
        if missing:
            print(f"{label}: FAIL", file=sys.stderr)
            for script in missing:
                print(f"  - missing check script {script}", file=sys.stderr)
            return 2

    print(f"{label}: {len(commands)} command(s)")
    for index, command in enumerate(commands, start=1):
        print(f"[{index}/{len(commands)}] {command.display()}")
        if dry_run:
            continue
        completed = subprocess.run(command.argv(), cwd=ROOT, check=False)
        if completed.returncode:
            print(
                f"{label}: FAIL ({command.script} exited {completed.returncode})",
                file=sys.stderr,
            )
            return completed.returncode
    print(f"{label}: PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", choices=("validate", "smoke", "full", "art-review"))
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the canonical command sequence without executing it",
    )
    args = parser.parse_args()

    if args.target == "validate":
        return run_commands("validate", VALIDATE_COMMANDS, dry_run=args.dry_run)
    if args.target == "smoke":
        return run_commands("smoke", SMOKE_COMMANDS, dry_run=args.dry_run)
    if args.target == "art-review":
        return run_commands("art-review", ART_REVIEW_COMMANDS, dry_run=args.dry_run)

    result = run_commands("validate", VALIDATE_COMMANDS, dry_run=args.dry_run)
    if result:
        return result
    return run_commands("smoke", SMOKE_COMMANDS, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
