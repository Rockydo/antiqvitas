# Blockers

## 2026-07-19 - M6 Han minority-regency start falls back to a generated ruler

Status: **deferred; M6 continues with independent power work and remains
untagged.**

The AD 1 country inspector consistently identifies Western Han (`XAR`) but
shows the generated `Han Zhang` as regent instead of Emperor Ping and Wang
Mang. The country, its Chang'an capital, 57.658M population, Han culture,
Chinese State Cult, and the M6 reform/law counts all load; no corresponding
new `error.log` line exists. This is therefore a silent runtime setup-contract
failure, not a parser or localization error.

Tried:

1. Rendered Ping as `ruler` together with Wang Mang as `active_regent` and a
   campaign-valid ruler term. The driver selected XAR at `08:00, 1 January, 1`
   and the inspector showed `Han Zhang`.
2. Matched the local vanilla minority-regency shape: no simultaneous `ruler`,
   Ping in `heir`, no current Ping term, and native order of regency, regent,
   dates, then heir. The same fresh live probe again showed `Han Zhang`.

Both attempts passed `make validate` and a mod-enabled `make smoke` with zero
new error-log lines. Evidence is in
`docs/screens/20260719_194101/M6_runtime_retry/han_probe.png` and
`docs/screens/20260719_194918/M6_runtime_retry/han_order_second_probe.png`.

Recovery: retain the source-led Han roster and the locally evidenced native
script shape, but do not claim that it yields the intended live regency or
close M6. A later isolated start-manager fixture must identify the hidden
minor/ruler linkage before this profile is accepted. Continue the independent
M6 government, estate, law, roster, and regnal-history work; Rome and Parthia
can still receive their own driver probes.

## 2026-07-19 - M6 Rajuvula cannot be placed at the AD 1 campaign boundary

Status: **deferred; M6 continues with other court and mechanics work.**

P8.4 names Rajuvula in the Northern Satrap context, but that alone does not
support making him ruler of the existing Arjunayana Mathura tag on 1 January
AD 1. Doing so would replace a plan-required ganasangha with a monarch and
would manufacture a chronology rather than reconcile it.

Tried:

1. Checked the local M3/M6 ledgers: Mathura is the existing Arjunayana
   republican anchor, while the separately represented Indo-Scythian realm is
   Azes's Taxila court. No Northern-Satrap AD 1 tag or reviewed boundary exists.
2. Searched Rajuvula-specific numismatic and epigraphic material, then read
   Shailendra Bhandare's Oxford study. It places the Rajuvula/Shodasa Mathura
   sequence c. AD 40-90 and records competing early-first-century readings;
   neither supports a defensible 1 January AD 1 placement.

Recovery: retain the Arjunayana republic and Indo-Scythian Azes court; do not
add Rajuvula as a current ruler or alter ownership. Revisit only in a sourced
M10 dated-history pass that can model an evidence-qualified later arrival.
The tree remains green after this evidence-only review. Source: `OX-MTH` in
`docs/world_1ad/SOURCES.md`.

## 2026-07-19 - M6 southern Arabian AD 1 courts lack defensible named current rulers

Status: **deferred; M6 continues with other court and mechanics work.**

The sourced M3 roster correctly retains Saba, Himyar, and Qataban, but the
available evidence does not identify defensible named officeholders for the
campaign boundary. A Qatabanian ruler attested around the middle of the first
century is not evidence that he ruled on 1 January AD 1. Generating courts
here would therefore turn an evidential gap into false precision.

Tried:

1. Rechecked plan P8.6 and the reviewed M3 polity/profile records. They
   support the three kingdoms and their regional anchors, not AD 1 rulers.
2. Searched specialist reference material. The Oxford Classical Dictionary's
   [Himyar entry](https://academic.oup.com/edited-volume/61673/chapter-abstract/548062792)
   establishes first-century competition with Saba but no dated current king.
   A recent epigraphic study, [*Two Old South Arabian Inscriptions: Early and
   Late*](https://abgad.journals.ekb.eg/article_55744_3863aa70f25af459bb9fd21541fe81c4.pdf),
   places Qataban's Yuhargib III only in the middle of the first century.

Recovery: retain the sourced M3/M4 profiles and the anonymous M6 regional-
kingship profiles; add named courts only when a source places an individual at
the AD 1 boundary. Later attested figures can enter through dated M10 content.
The tree remains green after this evidence-only pass.

## 2026-07-19 - M6 Elymais and Gordyene AD 1 courts lack defensible named current rulers

Status: **deferred; M6 continues with other court and mechanics work.**

The sourced M3 roster correctly retains both Elymais and Gordyene as Parthian
subordinate polities, but the available evidence does not support assigning a
named current ruler to either on 1 January AD 1. A generated court would turn
an evidence gap into false precision.

Tried:

1. Rechecked the project's P8.2/OCD/Pleiades roster route and M3 profiles. It
   supports the two polities and their map anchors, not AD 1 officeholders.
2. Searched specialist reference material. *Encyclopaedia Iranica*'s
   [Elymais entry](https://www.iranicaonline.org/articles/elymais/) establishes
   the polity's longer semi-independent history but leaves a gap between the
   late-first-century-BCE evidence and the AD 36 political episode. A targeted
   Gordyene search produced no scholarly source placing a named ruler at the
   campaign boundary.

Recovery: retain the sourced polity and anonymous Parthian-facing M6 profile
and add a named court only on a source that places an individual in office at
the AD 1 boundary. Later regional figures can enter through dated M10 content.
The tree is green after the independent Persis court slice.

## 2026-07-19 - M6 Adiabenian AD 1 court cannot be named without false precision

Status: **deferred; M6 continues with other court and mechanics work.**

The M3 roster correctly retains Adiabene as a Parthian subordinate realm, but
the available evidence does not establish a defensible named ruler on 1 January
AD 1. A source-led M6 character would therefore invent the very court chronology
the project is meant to qualify.

Tried:

1. Rechecked the project's P8.2/OCD/Pleiades roster route and the generated AD
   1 profile. It establishes the polity and Arbela anchor, not a dated start
   ruler.
2. Checked two independent *Encyclopaedia Iranica* entries: [Adiabene](https://www.iranicaonline.org/articles/adiabene/) and [Arbela](https://www.iranicaonline.org/articles/arbela-assyrian-arbailu-old/). They describe the earliest recorded Izates as succeeded about AD 30 by Monobazus I and place the reconstituted vassal state only at an unspecified point in the first quarter of the century.

Recovery: add a named Adiabenian court only if a source supports its status at
the campaign boundary; otherwise retain the sourced polity and anonymous
Parthian-facing M6 profile and cover its later Monobazus/Izates II sequence
through dated M10 content. The tree is green after this evidence-only pass.

## 2026-07-19 — M5 location-template RGO overrides are not runtime-effective

Status: **deferred; M5 remains untagged.**

The generated `in_game/map_data/location_templates.txt` is an exact copy of
the installed map-template file with 326 checked alterations. It parses and
the menu smoke is clean, but a fresh AD 1 observer session continues to use
vanilla raw materials. `export_goods_by_market wheat` reports Roma producing
roughly 23.46 wheat with no imports even after its generated template was
changed to clay; `antq_papyrus` likewise has no producer. The intended RGO
corrections therefore cannot yet be claimed as game-effective.

Tried:

1. Same-filename full-file override, which is the locally proven mechanism for
   the start managers. It left the fresh observer's Roma wheat output intact.
2. The exact DLC-manifest metadata shape, `"replace_path":
   ["in_game/map_data/location_templates.txt"]`. The menu still loaded with
   zero new lines, but the fresh observer export again reported the same Roma
   wheat output; the field was removed because it did not demonstrate
   replacement.

Recovery: identify a current-build, runtime-effective raw-material setup
surface (or a working mod-level directory replacement contract) using local
files and console exports. Until then retain the source-led RGO ledger as
static design data only, do not tag M5, and continue with M6's independent
government/character work. Evidence: `docs/playtests/M5_TRADE_FLOW.md`.

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

M6 update: the initial Rome/Han/Parthia core now supplies three sourced
government profiles, three dynasties, and nine characters; an AD 1 observer
run contains no new M6 identifier. The shared runtime boundary remains because
the rest of M6's government/law/character surface and M9's IO/HRE replacements
are still incomplete. The M6 inspector-UI coverage gap is in `KNOWN_ISSUES.md`.

M5 update: a subsequent AD 1 observer probe reached 11 January with market
construction notifications and no market, town-setup, RGO, or road errors.
The remaining active categories are unset capital/government and
international-organization/HRE references, so M3's shared runtime dependency
is now confined to M6/M9. Evidence: `docs/playtests/M5_RUNTIME_FOUNDATION.md`.

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

Recovery: M6 must replace the government, law, character, capital, and formable
dependencies; M9 must replace HRE interactions/objectives and international
organizations. Re-run the M3 observer capture and tag only after that shared
runtime surface produces zero new normalized lines.

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

## 2026-07-19 - M7 observer confirmation is ignored by the current game driver

Status: **deferred after two bounded attempts; M7 milestone gate remains open.**

The enabled mod reached the live AD 1 selector at `08:00, 1 January, 1`, with
the total-conversion world visible in
`docs/screens/M7_war_probe/m7_selector_ready_retry.png`. Selecting Observer
opened the irreversible country-change confirmation. The first normalized
pointer click targeted the visible OK control and left the dialog unchanged;
the second attempt used the driver's foreground-safe Enter key and likewise
left it unchanged. The process remained responsive throughout. Screenshots are
`m7_observer_started.png`, `m7_observer_confirm_retry.png`, and
`m7_observer_after_enter.png` in the same session directory.

The runtime log has no `antq_` unit, `unit_manager`, `antq_legionaries`,
`antq_liburnian`, or fort-proxy error identifier. The only matched `antq_`
lines concern existing religion-pop coverage, not M7. `make validate` and the
post-content enabled-mod menu smoke were green before this probe.

Recovery: revalidate the observer-confirmation click sequence after the next
driver/UI adjustment or game patch, then run the planned high-speed war
observation. Continue independent M8 work now; no human action is required.
