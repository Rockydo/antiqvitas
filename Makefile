.PHONY: validate smoke full

validate:
	.venv/Scripts/python.exe tools/pdxlint.py
	.venv/Scripts/python.exe tools/world_roster.py
	.venv/Scripts/python.exe tools/popcheck.py

smoke:
	.venv/Scripts/python.exe tools/smoketest.py

full: validate smoke
