# Blockers

## 2026-07-19 — M4 full culture remap lacks a redistributable historical dataset

Status: **deferred; M4 remains untagged.**

The plan requires a 350–500-culture, location-level AD 1 atlas. The current
69-culture M4 foundation, 61 reviewed dynamic capital names, and 680-row active
template audit are green, but they are not a defensible substitute for the
regional historical data required to split every template culture.

Tried:

1. Parsed every installed template used by the 13,552 controlled locations.
   The 680 active labels repeatedly span incompatible ancient profiles (for
   example `greek_culture` occurs under Latin, Greek, and Aramaic profiles), so
   an automatic vanilla-key translation would manufacture historical claims.
2. Audited the available source pipeline. The cached Pleiades release supplies
   ancient places, names, and coordinates, not a worldwide ethnic/cultural map.
   CHGIS supplies a valuable China-only historical GIS, but its V4 terms forbid
   redistribution, so its layers cannot be copied into the mod's committed data.

Recovery: acquire or author a source-labelled, redistributable regional culture
dataset (beginning with a licensed Han commandery layer and reviewed regional
atlases), then add mappings in geographic batches through the existing audit.
The tree is green (`make validate` and the last game-visible smoke are clean);
move to M5's independent economy scaffolding and revisit this task when that
evidence exists.

## 2026-07-19 - M3 observer runtime reaches vanilla systems not yet owned

Status: **deferred to M5/M6/M9; M3 remains untagged.**

The autonomous driver loaded the full AD 1 political map, entered observer
mode, started an actual observer session, and advanced it a month. Its runtime
log has new lines for unset `market`, `international_organization`, and
`character` links plus evaluations in vanilla `common_building_types`, HRE
country interactions, formables, steppe-horde reforms, common laws, and an
Athens DHE event. These are consequences of M3 deliberately not yet replacing
the plan-owned M5 economy, M6 government/law/character, and M9 diplomacy/IO
systems, not a menu-load failure.

Tried:

1. Exact-name blank overrides for the vanilla generic-action, building, and
   HRE surfaces. The menu then produced required-action/building failures
   (`mason`, missing AI-list actions, and an HRE-objective parse failure), so
   this was removed rather than suppressing data the engine still requires.
2. Narrow inert language/market action definitions and an empty HRE-objective
   override. The menu smoke returned green, but an actual observer session
   still emitted the runtime system errors above. The overlays were removed;
   `make full` is again green at the required menu-smoke boundary.

Recovery: M5 must seed valid ancient markets/buildings/town setups and replace
the vanilla market automation; M6 must replace the government, law, character,
and formable dependencies; M9 must replace HRE interactions/objectives and
international organizations. Re-run the M3 observer capture and tag only after
that shared runtime surface produces zero new normalized lines.

## 2026-07-19 — M2 calendar waits on M3's full setup mirror

Status: **resolved 2026-07-19.** M3 now mirrors all 25 start-manager files;
M2 is active, smoke-clean, save/reload verified, committed, and tagged
`M2-done`. The following is the historical reproduction record.

`tools/dates.py --write-m2` generated an AD 1 to AD 476 calendar, five campaign
ages, the required non-playable sixth-key compatibility sentinel, placeholder
advances, and mirrored localization. The real game reached a new-game map at
`08:00, 1 January, 1`, displayed `Age of Principate`, saved successfully, and
reloaded that save through the Load Game UI at the same date. Screenshots are
preserved under `docs/screens/M2/`.

However, the vanilla 1337 setup snapshot that M2 is explicitly permitted to
retain contains ruler-term histories. At a year-one start the engine validates
them as simultaneously active and emits 868 distinct new
`ruler_term_container.cpp:109` lines. The direct M2 runtime probe therefore
cannot meet the project-wide zero-new-error requirement until M3 mirror-replaces
the setup managers and supplies AD 1 characters/ruler histories.

Tried:

1. Defined only five age keys. The engine required the vanilla-referenced
   `age_6_revolutions` key, producing an immediate reference-error cascade.
2. Added a year-477, never-playable compatibility key and fixed the local
   UTF-8-BOM requirements. Menu smoke then returned clean, and the AD 1 UI plus
   save/reload both succeeded.

Recovery: the generated game-visible M2 files are removed before committing,
returning the tree to a clean menu smoke. The generator, timeline, linter
coverage, driver improvements, and visual evidence are retained. Re-run
`tools/dates.py --write-m2` as part of M3 once the setup mirror is in place,
then close M2 with a full runtime log check.

Resolution: the exact M3 mirror was accepted by smoke, then the generated M2
layer was restored. `make full` now passes with zero new lines; observer mode
shows 1 January 1 / Age of Principate and a newly written save reloads at that
same date. See `docs/playtests/M2_REPORT.md`.

## 2026-07-19 — Local documentation exporters do not complete

Status: fallback in use; does not block other M0 work.

The console and `helplog` are automated successfully. On the installed
1.3.1.1/Steam build 24187685, `script_docs` is listed as
`script_docs(script_documentation)`. Two clean attempts executed the command,
turned the render surface black, consumed roughly five CPU cores and 5 GiB
resident / 8.7 GiB private memory, but produced no file and did not return after
more than ten minutes. Earlier malformed-command diagnostics proved that the
console reports unknown commands immediately, so this is an exporter failure or
pathological runtime rather than a missing command.

`dump_data_types` was then entered exactly in a fresh process and showed the
same signature: console hidden, roughly five cores active, resident/private
memory stabilizing near 5/8.8 GiB, and no output flush during the bounded run.

Tried:

1. Virtual-key and physical scan-code console entry, with screenshot verification.
2. Fresh process, fixed window, exact AZERTY-safe command entry, and an extended
   monitored run. The process stayed responsive and memory-stable but never
   flushed output.
3. A separate fresh `dump_data_types` run with the exact raw virtual-key
   underscore mapping and three minutes of stable high-CPU processing.

Fallback: `docs/engine_docs/community_2025/` contains the MIT-licensed
GlossMod/EU5-Modding-Mcp dump at commit
`90790df9478a61035a2099c115b21ba7f04c3763` (2025-11-07). It predates build
1.3.1.1, so every effect/trigger used by the mod must additionally be confirmed
against current local scripts and smoke-tested. The local `helplog` command list
was harvested successfully as `docs/REF_console_commands.txt`.
