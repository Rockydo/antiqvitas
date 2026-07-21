.PHONY: validate smoke full art-review

validate:
	.venv/Scripts/python.exe tools/pdxlint.py
	.venv/Scripts/python.exe tools/m6_power.py --check
	.venv/Scripts/python.exe tools/world_roster.py
	.venv/Scripts/python.exe tools/generate_tag_map.py --check
	.venv/Scripts/python.exe tools/generate_m4_definitions.py --check
	.venv/Scripts/python.exe tools/generate_dynamic_names.py --check
	.venv/Scripts/python.exe tools/culture_template_inventory.py --check
	.venv/Scripts/python.exe tools/generate_ancient_goods.py --check
	.venv/Scripts/python.exe tools/generate_rgo_remap.py --check
	.venv/Scripts/python.exe tools/m7_war.py --check
	.venv/Scripts/python.exe tools/m8_knowledge.py --check
	.venv/Scripts/python.exe tools/m9_diplomacy.py --check
	.venv/Scripts/python.exe tools/m10_history.py --check
	.venv/Scripts/python.exe tools/m10_second_century.py --check
	.venv/Scripts/python.exe tools/m10_third_century.py --check
	.venv/Scripts/python.exe tools/m10_fourth_century.py --check
	.venv/Scripts/python.exe tools/m10_final_century.py --check
	.venv/Scripts/python.exe tools/m11_age_art.py --check
	.venv/Scripts/python.exe tools/m11_advance_icons.py --check
	.venv/Scripts/python.exe tools/m11_flavor_events.py --check
	.venv/Scripts/python.exe tools/m11_dynamic_coas.py --check
	.venv/Scripts/python.exe tools/m11_common_icons.py --check
	.venv/Scripts/python.exe tools/m11_decisions.py --check --scope all
	.venv/Scripts/python.exe tools/m11_message_overlay.py --check --scope all
	.venv/Scripts/python.exe tools/m11_localization.py --check
	.venv/Scripts/python.exe tools/m12_disable_missions.py --check
	.venv/Scripts/python.exe tools/m12_game_rules.py --check
	.venv/Scripts/python.exe tools/m12_hardcoded_startup.py --check
	.venv/Scripts/python.exe tools/m12_coa_scope_guard.py --check
	.venv/Scripts/python.exe tools/m12_anachronism_audit.py --check
	.venv/Scripts/python.exe tools/m12_disable_historical_hints.py --check
	.venv/Scripts/python.exe tools/m12_event_quarantine.py --check
	.venv/Scripts/python.exe tools/generate_country_definitions.py --check
	.venv/Scripts/python.exe tools/capital_mapper.py --check
	.venv/Scripts/python.exe tools/extract_map_coordinates.py --check
	.venv/Scripts/python.exe tools/capital_geography.py --check
	.venv/Scripts/python.exe tools/ownership_map.py --check
	.venv/Scripts/python.exe tools/territory_coverage.py
	.venv/Scripts/python.exe tools/generate_start_mirror.py --check
	.venv/Scripts/python.exe tools/dates.py --check-m2
	.venv/Scripts/python.exe tools/popcheck.py

smoke:
	.venv/Scripts/python.exe tools/smoketest.py

full: validate smoke

art-review:
	.venv/Scripts/python.exe tools/m11_contact_sheet.py
