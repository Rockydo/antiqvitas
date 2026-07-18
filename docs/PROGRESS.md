# Progress

## 2026-07-19

- Read the complete master plan and reread Part I for this session.
- Created the repository on the EU5 installation drive at `G:\antiqvitas`.
- Moved the master plan to `docs/ANTIQVITAS_MASTER_PLAN.md`.
- Discovered EU5 build 24187685 (displayed in-game as 1.3.1.1 Pavia) at
  `G:\SteamLibrary\steamapps\common\Europa Universalis V`.
- Confirmed the `--user_dir=` engine argument and relocated user data to
  `G:\antiqvitas_user_data`; wired the repo with a G:-local junction.
- Installed the Python driver environment and ImageMagick on G:.
- Built the initial path, link, Steam, playset, date, DDS, localization, lint,
  population, smoke, and game-driver tools.
- Reached and screenshot-verified the clean vanilla menu autonomously.
- Captured the vanilla error baseline. Its only normalized messages are repeated
  store-backend misses for unavailable DLC item IDs 3865300 and 3699010.
- Extracted 28,573 locations and the current symbols/content/encoding/DLC
  inventories into `docs/vanilla_symbols/`.
- Verified the start/end-date defines and the build's actual split setup layout
  against local files and the read-only 1444 precedent.
- Harvested the local console command list. The current build's
  `script_docs`/`dump_data_types` exporters do not return; captured a documented
  community fallback and recorded the stricter local-script+smoke rule.
- Completed `make full`: static validation green, clean vanilla menu reached,
  zero new normalized errors.
- Closed M0 with `docs/playtests/M0_REPORT.md`.

Next: M1 metadata, thumbnail, link restoration, fully scripted mod enablement,
and a mod-active zero-new-error menu smoke.
