# Progress

## 2026-07-19 — M3 frontier capital tranche

- Expanded the checked active-capital set from 56 to 81 polities with
  Pleiades-backed classical sites and explicitly documented regional anchors
  across Korea, Britain/Ireland, the Danube/Pontic steppe, and Central Asia.
- The ownership collision gate rejected two anchors inside the Han core; both
  were remapped to non-Han local keys before the game saw them. The source
  tables now resolve 4,178 locations and 21 dependencies.
- `make validate` and real-game smoke are green with zero new error lines.

Next: map the remaining 52 capitals, then extend each regional anchor into
sourced ownership or SoP coverage rather than leaving a one-location polity.

## 2026-07-19 — M3 source-backed dependency slice

- Generated 20 checked dependencies: the active Roman client ring, Arsacid
  sub-kings, and Han Western-Regions tributaries.
- The exact diplomacy-manager mirror uses only locally verified `vassal` and
  `tributary` keys as an interim political-map adapter; M9 owns the ancient
  contract mechanics.
- `make validate` and real-game smoke are green with zero new error lines.

Next: map remaining capitals and source the unfinished client, satellite, and
SoP territorial extents.

## 2026-07-19 — M3 territorial ownership slice

- Added checked area and direct-location source tables, resolving 4,153 unique
  engine-valid locations for 56 AD 1 polities. The Roman, Parthian, and Western
  Han core frames are now territorial rather than one-capital placeholders.
- Corrected three unsafe same-name capital matches through Pleiades/map review:
  Osroene now uses Urfa, Elymais Shush, and Khwarazm is returned to `TBD`.
- `make validate` and a real-game smoke are green. The autonomous AD 1 selector
  visibly shows the new territorial surface; evidence and limits are recorded
  in `M3_TERRITORIAL_SLICE.md`.

Next: map remaining capitals, source subject relations and territorial extents,
then seed SoP coverage rather than treating unassigned map space as settled
states.

## 2026-07-19 — M3 geospatial capital index

- Parsed the installed 16,384×8,192 location raster and all named-location RGB
  values into a build-bound centroid index for 28,573 EU5 locations.
- Added a conservative, sourced historical-coordinate candidate report, then
  improved its global affine fit with nearby-anchor residual correction for
  northern latitudes. It proposes nearby map keys for review without silently
  converting fuzzy geography into ownership.

Next: assess the high-confidence geographic candidates one by one, then expand
the capital-control slice from verified map locations.

## 2026-07-19 — M3 capital-control slice

- Extended the exact start-manager generator from empty roots to 57 sourced
  roster polities with a direct verified capital key. Each controls its capital
  through a collision-safe engine tag.
- A real AD 1 new-game screen shows the initial 34-state version at their map
  locations; the reviewed 57-state expansion remains smoke-clean at zero new
  error lines. The visual and scope judgment are recorded in
  `M3_CAPITAL_SLICE.md`.

Superseded for ownership by the territorial slice above; the remaining capital,
subject, and SoP work continues under its stated limits.

## 2026-07-19 — M2 closed on M3's clean base

- Activated the generated 1 January AD 1–4 September 476 calendar, five live
  age skeletons, and temporary M8 advance scaffolds on the exact M3 mirror.
- `make full` is green with zero new errors. The autonomous driver entered
  AD 1 observer mode, wrote an AD 1 save, and loaded it through the UI at the
  same displayed date. M2 is tagged `M2-done`.
- The report's blank map is intentional: historical countries/ownership remain
  the next M3 content batch, while M2's date and save compatibility are now
  independently clean.

Next: expand verified capital mapping into country/capital/ownership data for
the M3 start manager.

## 2026-07-19 — M3 start-manager purge

- Generated all 25 exact-name start-manager overrides using the locally
  verified manager roots and no-BOM encoding. The validator now fails if a game
  patch changes the installed inventory.
- Real-game smoke accepted the full mirror with zero new error-log lines,
  eliminating the retained vanilla 1337 state (including the M2-blocking ruler
  histories) without touching the game installation.

Next: activate the generated AD 1 calendar against this clean base, then fill
the country/ownership manager from the verified capital data.

## 2026-07-19 — M3 capital mapping pipeline

- Added a checked candidate report derived from the installed base-English
  location names, so direct city matches and unresolved geographic approximations
  are distinguishable in review.
- Recorded ten additional exact capital keys (including Zaranj, Mtskheta,
  Sagala, Rohtak, Kalinganagara, Djenné, Exeter, Teotihuacan, Cahuachi, and
  Tiwanaku). Ambiguous fuzzy matches remain `TBD` rather than becoming map data.

Next: continue sourced capital mapping and use the verified set to generate the
first ownership/capital slice of the M3 start-manager mirror.

## 2026-07-19 — M3 country database foundation

- Generated 133 BOM-safe country definitions from the sourced roster and the
  collision-safe engine-tag map, along with all-language mirrored country-name
  localization and engine-native placeholder CoAs.
- Extended tag isolation to avoid the current build's country, localization,
  and observed hash namespaces. The real smoke found and drove fixes for all
  six database collisions; the accepted run reaches the active mod menu with
  zero new error-log lines.
- M4 remains responsible for replacing the temporary valid culture/religion
  defaults with the historically sourced population-map trees.

Next: map the remaining capitals and build the exact 25-file AD 1 setup
mirror, beginning with a clean country/ownership manager.

## 2026-07-19 — M3 roster foundation

- Created the machine-validated initial AD 1 roster: 133 country, subject, and
  SoP entries across every region named in the design bible, with source and
  confidence fields rather than invented certainty.
- Added `tools/world_roster.py` to the required validation target. It rejects
  duplicate/invalid tags and invalid mapped-capital keys while exposing mapping
  coverage for the next M3 batch.
- Seeded `docs/SURFACE_AREA.md` and logged contested roster decisions with
  sources in ASSUMPTIONS.

Next: map every roster capital to local EU5 locations, generate country
definitions/localization, then construct the exact 25-file M3 setup mirror.

## 2026-07-19 — M3 tag isolation

- Compared all 133 planned roster codes to the 2,339 country definitions in
  the installed build. Sixty-seven names collide with vanilla/releasable tags.
- Added a deterministic generated tag map: non-conflicting design tags stay
  readable; collisions receive stable internal `X..` tags. The map is checked
  against the installed build on every validation run.

Next: use the stable engine-tag map for country definitions and AD 1 setup.

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
