.PHONY: validate smoke full

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
