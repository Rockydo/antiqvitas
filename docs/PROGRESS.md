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

M1 added metadata, a project-generated 512x512 thumbnail, empty valid content
roots, and a linter gate for both thumbnail placements and their size. The
engine rejected the UI-formatted `1.3.1.1` metadata value but accepted `1.3.11`;
that internal comparator distinction is recorded in ENGINE_FACTS. ANTIQVITAS
was enabled only through the backed-up `playsets.json` automation, reached the
mod-active menu twice, and has an independently reviewed screenshot. M1 closed
with a green `make full` and zero new normalized `error.log` line types.

Next: M2 calendar defines, five age skeletons and placeholder advances, then a
year-one new-game/save-reload verification.

## 2026-07-19 — M2 runtime probe

- Added a checked-in date timeline and expanded `tools/dates.py` to generate
  M2's calendar, ages, scaffold advances, and mirrored BOM-safe localization.
- Verified the engine's five live age boundaries and its required sixth,
  post-end compatibility key. Verified that current-build age/advance/defines
  common files require UTF-8 BOM and extended pdxlint accordingly.
- Drove New Game to a visible `08:00, 1 January, 1` and `Age of Principate`;
  saved an AD 1 observer session and reloaded it through the UI at the same
  date. The driver now supports normalized clicks and hotkeys.
- Deferred the generated M2 game-visible layer before commit: vanilla 1337
  ruler-term data produces 868 runtime errors at year 1. M3's required complete
  setup mirror is the correct fix; evidence and recovery are in BLOCKERS.

Next: begin M3's AD 1 setup mirror, which unblocks M2's clean runtime gate.
