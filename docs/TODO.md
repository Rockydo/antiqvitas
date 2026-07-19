# ANTIQVITAS TODO

Tasks are taken top-to-bottom within the current milestone. A milestone closes only
after `make full` and its autonomous driver report are green.

## M0 — Discovery & tooling

- [x] Discover Steam libraries, game/user paths, disk space, and write `config/local_paths.json`.
- [x] Create the repo on the game drive; move the master plan into `docs/`; configure caches and local Python environment.
- [x] Establish mod visibility using user-dir relocation, a directory junction, or direct CLI loading, in that order.
- [x] Build Steam startup, launcher/playset enablement, game driver console tier, vanilla extractor, linter, pop checker, smoke tester, DDS/date/localization tools.
- [x] Capture scrubbed vanilla error baseline with all existing mods disabled.
- [x] Harvest `script_docs`, `dump_data_types`, and `helplog` autonomously. (`helplog` local; documented community fallback for the two non-returning exporters.)
- [x] Clone and analyze EU5-1444-Start-Date read-only.
- [x] Extract vanilla symbols, encodings, setup/content/DLC inventories.
- [x] Complete `docs/ENGINE_FACTS.md`, including every §3 verification item.
- [x] Run `make full`; create `docs/playtests/M0_REPORT.md`; tag `M0-done`.

## M1 — Skeleton loads

- [x] Add valid metadata and thumbnail; enable entirely by tooling.
- [x] Reach the menu with the mod active and zero new errors.
- [x] Run milestone gate and tag `M1-done`.

## M2 — Time itself

- [x] Enable the generated 1.1.1–476.9.4 dates through `tools/dates.py` after M3's setup mirror removes vanilla ruler histories.
- [x] Enable the generated five-age skeletons and placeholder advances with that calendar layer.
- [x] Verify year-one UI and save reload; run milestone gate and tag `M2-done`.

## M3 — Political map

- [x] Create and validate the sourced initial AD 1 polity roster in `docs/world_1ad/`.
- [x] Generate collision-safe country definitions, mirrored names, and M3 placeholder CoAs for every roster polity.
- [x] Add a checked capital-location candidate report and record direct local-map matches.
- [x] Render and smoke-check worldwide AD 1 ownership (157 polities; 13,552 controlled locations and 25 dependencies; 13,535 of 13,576 ownable locations assigned, with 41 documented intentional empties).
- [x] Build a local-raster coordinate index and sourced capital-candidate report.
- [x] Research and create the remaining territorial/SoP coverage with an ordered residual-coverage ledger and an explicit intentional-empty audit.
- [x] Mirror-replace the exact 25 installed start-manager files, removing the vanilla 1337 start layer.
- [ ] Run milestone gate and tag `M3-done` (observer runtime is deferred in `BLOCKERS.md` until M5/M6/M9 replace vanilla systems that require markets, governments/laws, and HRE diplomacy).

## M4 — Peoples & faiths

- [x] Seed and smoke-check the additive culture/religion foundation (69 cultures, 37 religions, 27 culture groups, and 14 religion groups).
- [x] Generate and smoke-check engine-valid ancient dialect/namelist layers (27 language roots, dialects, and localized source-name pools).
- [x] Bind the sourced culture/faith tree to all 157 country profiles (34 regional bases and 45 source-labelled tag overrides).
- [x] Bind the sourced culture/faith tree to global pop data (13,552 base pops; 230,000 thousand total; all section 12.4 macro checks).
- [x] Generate conservative sourced dynamic-name v1 (61 coordinate-verified capital anchors, localized for all supported clients).
- [x] Audit the 680 installed culture templates active in the AD 1 ownership surface, with profile candidates and explicit no-template exceptions.
- [ ] Expand the culture/location remap toward the 350–500-culture target and add reviewed dynamic names beyond capital anchors (deferred in `BLOCKERS.md`: no redistributable global culture dataset yet).
- [ ] Pass the final culture/religion atlas checks; population and raw `-leavepops` checks are green.
- [ ] Run milestone gate and tag `M4-done`.

## M5 — Economy

- [x] Seed and smoke-check 36 source-labelled AD 1 market hubs.
- [x] Localize and anchor the plan-listed ancient raw goods on controlled AD 1 map locations (321 audited corrections).
- [x] Seed and smoke-check 36 source-labelled urban market settlements with engine-valid town setups.
- [x] Run the AD 1 observer foundation probe (map, observer mode, and ten days of market activity).
- [x] Seed and smoke-check 25 source-labelled ancient transport-corridor segments.
- [x] Seed and smoke-check the transparent city/town/road development profile.
- [x] Expand the specialist urban economy with source-led glassware, lacquerware, pottery, water, mint, library, and Pharos building anchors.
- [ ] Implement the remaining goods/RGOs, buildings/town setups, roads, and development.
- [ ] Verify ancient trade flows; run milestone gate and tag `M5-done`.

## M6 — Power

- [ ] Implement governments, reforms, estates, privileges, laws, values, characters, dynasties, and regnal histories.
- [ ] Driver-test Rome, Han, and Parthia; run milestone gate and tag `M6-done`.

## M7 — War

- [ ] Implement ancient units, levies/regulars, mercenaries, forts/limes, and navies; remove gunpowder/oceanic units.
- [ ] Observer-test wars; run milestone gate and tag `M7-done`.

## M8 — Knowledge

- [ ] Implement five complete age trees, roughly 250 advances, institutions, tech tiers, objectives, and abilities.
- [ ] Test AI research and anachronism/dead-end rules; run milestone gate and tag `M8-done`.

## M9 — Nations among nations

- [ ] Implement CBs, wargoals, treaties, subjects, IOs, and known-world sets.
- [ ] Verify ancient diplomatic webs; run milestone gate and tag `M9-done`.

## M10 — History in motion

- [ ] Implement all timeline situations/disasters/formables/tag changes in five century batches.
- [ ] Smoke and observer-test every batch; run milestone gate and tag `M10-done`.

## M11 — Flavor & face

- [ ] Reach event/decision targets; finish flags, icons, illustrations, loading/age art, localization, glossary, and credits.
- [ ] Remove common-screen placeholders; run milestone gate and tag `M11-done`.

## M12 — Ship

- [ ] Balance pacing/growth/inflation and audit AI weights.
- [ ] Run autonomous observer game to 476 with decade screenshots and live log watch.
- [ ] Finish README, known issues, packaging notes, finale verification, and full surface-area audit.
- [ ] Run final `make full`; create M12 report; tag `M12-done`.
