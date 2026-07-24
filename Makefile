PYTHON ?= .venv/Scripts/python.exe

.PHONY: validate smoke full art-review

validate:
	$(PYTHON) tools/run_checks.py validate

smoke:
	$(PYTHON) tools/run_checks.py smoke

full:
	$(PYTHON) tools/run_checks.py full

art-review:
	$(PYTHON) tools/run_checks.py art-review
