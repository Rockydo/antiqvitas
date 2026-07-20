@echo off
setlocal
set "PYTHON=python"
if exist "%~dp0.venv\Scripts\python.exe" set "PYTHON=%~dp0.venv\Scripts\python.exe"
set "TARGET=%~1"
if "%TARGET%"=="" set "TARGET=validate"
if /I "%TARGET%"=="validate" goto validate
if /I "%TARGET%"=="smoke" goto smoke
if /I "%TARGET%"=="full" goto full
if /I "%TARGET%"=="art-review" goto art_review
echo Unknown target: %TARGET%
exit /b 2

:validate
"%PYTHON%" tools\pdxlint.py || exit /b 1
"%PYTHON%" tools\m6_power.py --check || exit /b 1
"%PYTHON%" tools\world_roster.py || exit /b 1
"%PYTHON%" tools\generate_tag_map.py --check || exit /b 1
"%PYTHON%" tools\generate_m4_definitions.py --check || exit /b 1
"%PYTHON%" tools\generate_dynamic_names.py --check || exit /b 1
"%PYTHON%" tools\culture_template_inventory.py --check || exit /b 1
"%PYTHON%" tools\generate_ancient_goods.py --check || exit /b 1
"%PYTHON%" tools\generate_rgo_remap.py --check || exit /b 1
"%PYTHON%" tools\m7_war.py --check || exit /b 1
"%PYTHON%" tools\m8_knowledge.py --check || exit /b 1
"%PYTHON%" tools\m9_diplomacy.py --check || exit /b 1
"%PYTHON%" tools\m10_history.py --check || exit /b 1
"%PYTHON%" tools\m10_second_century.py --check || exit /b 1
"%PYTHON%" tools\m10_third_century.py --check || exit /b 1
"%PYTHON%" tools\m10_fourth_century.py --check || exit /b 1
"%PYTHON%" tools\m10_final_century.py --check || exit /b 1
"%PYTHON%" tools\m11_age_art.py --check || exit /b 1
"%PYTHON%" tools\m11_advance_icons.py --check || exit /b 1
"%PYTHON%" tools\m11_flavor_events.py --check || exit /b 1
"%PYTHON%" tools\m11_dynamic_coas.py --check || exit /b 1
"%PYTHON%" tools\m11_common_icons.py --check || exit /b 1
"%PYTHON%" tools\m11_decisions.py --check --scope all || exit /b 1
"%PYTHON%" tools\m11_message_overlay.py --check --scope all || exit /b 1
"%PYTHON%" tools\m11_localization.py --check || exit /b 1
"%PYTHON%" tools\generate_country_definitions.py --check || exit /b 1
"%PYTHON%" tools\capital_mapper.py --check || exit /b 1
"%PYTHON%" tools\extract_map_coordinates.py --check || exit /b 1
"%PYTHON%" tools\capital_geography.py --check || exit /b 1
"%PYTHON%" tools\ownership_map.py --check || exit /b 1
"%PYTHON%" tools\territory_coverage.py || exit /b 1
"%PYTHON%" tools\generate_start_mirror.py --check || exit /b 1
"%PYTHON%" tools\dates.py --check-m2 || exit /b 1
"%PYTHON%" tools\popcheck.py || exit /b 1
exit /b 0

:smoke
"%PYTHON%" tools\smoketest.py || exit /b 1
exit /b 0

:full
call "%~f0" validate || exit /b 1
call "%~f0" smoke || exit /b 1
exit /b 0

:art_review
"%PYTHON%" tools\m11_contact_sheet.py || exit /b 1
exit /b 0
