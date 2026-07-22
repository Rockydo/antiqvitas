# Blockers

## 2026-07-22 - M5 annona routing lacks a demonstrated startup merchant contract

Status: **deferred after two material local market-route attempts; runtime RGO
surface is recovered and green.**

The earlier static `location_templates.txt` blocker is resolved only as a
renderer finding: local `script_docs` documents location-scoped
`change_raw_material`, and a live Roma clay probe proved its effect. The exact
startup overlay now applies all 328 source-led corrections after
`setup_area_preferences = yes`; the static mirror remains source-audit data,
not the runtime mechanism.

The fresh May AD 1 Observer export proves the annona wheat anchors execute:
Tunis produced 4.26409 wheat and Alexandria 2.97279. It has no Roma wheat
import row. The same session proves other economy legs can route goods
(Khambat and Attock import pepper; Meroe imports incense), but it does not yet
show silk westward, pepper to Egypt, or the complete required pattern.

Tried:

1. Added the source-led Egyptian, African, Sicilian, and Sardinian annona
   wheat anchors with bounded local worker capacities. Live production appeared
   at the Egyptian/African source markets but no Roma import did.
2. Used the installed country-scoped `create_trade` effect for a locked
   Faiyum-market to Roma-market wheat order, then repeated it after adding a
   disposable Faiyum wheat stockpile. Neither post-tick export created a Roma
   import row.

Recovery: do not add a fabricated market transfer or claim an automatic route.
Resume only after a materially different local engine contract identifies the
required merchant/market setup, or an installed-build change alters the route
semantics. Preserve the runtime RGO renderer and continue with independent
milestone work. Evidence: `docs/playtests/M5_TRADE_FLOW.md` and
`docs/screens/20260722_m5_annona/`.

## 2026-07-21 - M4 observer/map-mode acceptance is resolved by the boundary-term repair

Status: **resolved 2026-07-21.**

The current 350-culture build passed `make full`; its final enabled-mod smoke at
18:49 UTC recorded zero new normalized `error.log` lines. A fresh driver launch
then reached the responsive EU5 menu, documented by the valid
`docs/screens/20260721_205223/m4_350_menu.png` capture.

Two controlled New Game/observer-start attempts followed. Both process runs
terminated before the AD 1 map or Culture/Religion map modes rendered. The
crash bundles `Europa Universalis V20260721_185453` and
`Europa Universalis V20260721_185750` both report an abnormal termination with
the `NVSDK_NGX_D3D12_Shutdown1` / `ffxFsr2ResourceIsNull` renderer-family
stack. The second run was made after correcting the driver's minimized-window
handling, so the repeated engine crash is not a stale-window or click-target
failure.

The required material condition was the generated AD 1 start data: local
diagnostics showed that every open current `ruler_term` at `1.1.1` was rejected
as a future term, alongside the invalid named-heir/regent reports. The M6
generator now uses date-less current terms paired with native ruler fields for
named non-regency incumbents, while retaining the source ledger. A new autonomous run reached a paused
`08:00, 1 January, 1` observer, then rendered the required Culture (Location)
and Religions (Location) maps. The successful evidence is in
`docs/screens/20260721_boundary_term_fix/` and the accepted report is
`docs/playtests/M4_FINAL_GATE_350_20260721.md`.

The earlier two crash bundles remain valid historical diagnostics, but they no
longer block M4. Separate renderer and long-observer reliability issues remain
open for M12; the successful M4 session was paused and does not claim an
observer-to-476 result.

## 2026-07-21 - M4 culture atlas is partially unblocked by an authored ledger

Status: **M4 density target and final observer/map-mode acceptance are met
2026-07-21.**

The 2026-07-19 evidence review remains valid for a fully automated global
dataset: installed template cultures are not historical AD 1 evidence,
Pleiades is a place gazetteer rather than a culture atlas, and CHGIS cannot be
redistributed in this project. It no longer blocks all M4 work. The authored
`docs/culture_remap.csv` ledger now supplies 506 source-labelled geographic
selectors, resolving 12,058 controlled locations across 329 distinct mapped
cultures without copying external map data. The full M4 catalogue contains 350
cultures, including the non-ledger definitions needed for the Moche chronology
correction.

This first batch is deliberately limited to source-qualified regional frames in
Italy, Iberia, Aquitania/Armorica, the Balkans, Anatolia, the Levant, Punic
coasts, South Arabia, northeast Africa, Britain, Ireland, Germania,
Scandinavia, Finland, the Baltic, South Asia, Southeast Asia, Iran, the
Caucasus, Central Asia, the Pontic, Korea, the northeast steppe, Africa, the
Americas, the controlled Oceanian surface, Han China with its southern and
southwestern frontiers, the Roman world, the Venedi SoP frames, core Yayoi Wa,
the Tibetan plateau, interior Arabia, source-qualified South Asian regional
Prakrit, Tamil, Himalayan, source-qualified Germanic tribal, bounded
Amur-Yilou archaeological, bounded Carpathian Dacian/Getic, Korean
Samhan/local-community, Iberian-Colchian Kartvelian, northern-Mesopotamian
Aramaic, Late-Preclassic Petén Maya, lower-Rhine Batavian, Moravian Quadi, and
central-Vietnam Sa Huynh archaeological, interior Gaetulian frames, a bounded
lower-Yik Sarmatian context, Sulawesi Austronesian context, central-Mexican
Teotihuacan context, Bornu Chadic context, Late Nok archaeological horizon,
Omsk Sargat archaeological context, Transdanubian Pannonian context,
Upper-Selenga Xiongnu context, the exact Khotan Oasis frame, the Vyatka and
Kama-Perm archaeological-linguistic contexts, the deliberately narrow
central-Oman Samad archaeological context, the Surgut-Narym Ob Kulay
archaeological context, the exact Kucha Oasis frame, the exact Loulan
city-oasis frame, the exact Yarkand Oasis frame, the exact Aksu Oasis frame,
the exact Kashgar Oasis frame, and the exact Hami and Turpan Oasis frames. A
subsequent Strabo/Pliny primary-source pass adds 38 carefully bounded named
Iberian ethnographic frames through explicit province-over-area refinement. A
second Strabo/Pliny corpus adds 47 bounded Gallic ethnographic frames spanning
Aquitania, Armorica, central/northern Gaul, the Moselle corridor, and
Narbonensis. A third Strabo corpus adds 50 bounded Balkan-Anatolian frames.
A fourth Strabo/Tacitus corpus adds 36 Germanic, Baltic, and Fennian frames;
Tacitus is explicitly a later cross-check, never date-exact placement evidence.
All new rows remain contested proxies rather than uniform ethnic boundaries.
The catalogue now meets the plan's 350-culture lower bound.

The 2026-07-21 M4 gate ran `make full` successfully and, after the separate
boundary-term repair recorded above, reached a fresh AD 1 Observer screen
through the game driver. The current 350-definition build rendered both the
Culture (Location) and Religions (Location) map modes in the paused `08:00,
1 January, 1` session. Do not manufacture additional cultures from installed
template keys merely to increase the number.

Recovery: retain the source-labelled ledger and the accepted M4 evidence.
Future refinements still require a comparably reviewed dataset or bounded
source corpus; do not infer a historical culture directly from a vanilla
template key.

## 2026-07-20 - M12 vanilla-runtime quarantine requires source-preserving overlays

Status: **event portion resolved; adjacent runtime systems remain to audit.**

The AD 1 observer exposed dated vanilla startup references.  Four generated
same-filename overlay variants were tested against the installed build:

1. Empty dated event, situation, disaster, formable, and on-action files
   caused missing event identifiers from the engine's retained generic graph.
2. No-op on actions plus hidden unreachable event stubs removed those missing
   identifiers, but the event manager emitted one orphan diagnostic per stub.
3. A never-dispatched reference action removed orphan diagnostics, but global
   country-event stubs produced scope mismatches at location call sites and
   exposed hundreds of variable/effect dependencies whose setters had been
   removed with the dated events.
4. Parse-valid situation/disaster placeholders confirmed that formable-country
   records use a separate schema; after correcting that branch, the installed
   generic action, building, parliamentary, and scripted-effect graph still
   requires the original event scope types and variable network.

The final experiment therefore would have required reconstructing a large
portion of the removed vanilla historical runtime solely to satisfy loader
diagnostics, contradicting the total-conversion requirement.  No game install
file was modified.  All failed variants reached the rendered menu; evidence is
in the timestamped smoke logs under the configured user directory.

The source-preserving renderer now covers all 7,440 definitions in the 347
installed event files. It retains each event's type, scheduler, scope, options,
variables, and effects, but adds `current_date > 476.9.4` inside its direct
eligibility trigger. That dynamic date guard is unreachable in the campaign
without making the loader classify the event as orphaned. All external dates
are normalized through `tools/dates.py`. Full static validation and a settled
enabled-mod smoke both returned zero new error-log lines on 2026-07-21.

This resolves the event graph portion of the former blocker. Situations,
disasters, formables, and on-action callers remain separate runtime surfaces;
their need for an exact-name override is to be established from future observer
evidence rather than assumed from the old failed blank-overlay experiment.

The first live follow-up isolated one such on-action caller: the installed
hardcoded startup handler unconditionally addressed Catholic and Shinto IO
instances that ANTIQVITAS intentionally does not create, then executed
China/Majapahit/Byzantium-era country setup on empty legacy tags. Its
source-preserving exact-name overlay now makes the five absent-IO references
safe and dynamically gates eight dated startup blocks after the campaign end.
The generated overlay, full validation, and enabled-mod smoke are green. A
fresh AD 1 observer initialization recorded zero of all six former hardcoded
error signatures; see docs/playtests/M12_HARDCODED_STARTUP_20260721.md.

That distinct coat-of-arms surface is now also resolved by a second
source-preserving exact-name overlay: four installed government comparisons
use the locally evidenced optional comparison form, and three HRE
special-status predicates first establish that an HRE instance exists. A fresh
observer initialization has zero government-scope, invalid-comparison, or HRE
special-status errors. Evidence is in docs/playtests/M12_COA_SCOPE_20260721.md.

The remaining flag diagnostic was a single direct Sitges-capital comparison in
the installed Catalan flag definition. A third exact-name renderer changes it
to the locally evidenced optional capital comparison form. Full validation and
smoke are green, and a fresh AD 1 observer initialization now reports zero
script-system errors in total. The screenshots and log count are recorded in
docs/playtests/M12_CLEAN_INITIALIZATION_20260721.md.

This closes the currently evidenced startup, on-action, CoA, and flag-runtime
fall-through surface. It does not close the renderer-bound sustained-playback
gate, the Han regency presentation gap, or the separate M5 trade-flow result.

## 2026-07-21 - Observer playback remains renderer-bound after two renewed attempts

Status: **deferred after two material renderer-profile attempts; menu baseline remains green.**

The current event-quarantine commit passed full static validation and an
enabled-mod 90-second smoke with zero new lines. Fresh New Game sessions on two
material renderer profiles reached the AD 1 selector, entered Observer Mode,
and rendered the active map. The corrected play-control target advances time:
the supported 1920x1080 profile reached about 1 June at maximum speed before
the renderer fault recurred.

The former 960x540 request is rejected by this game build and persisted as
2560x1440, so the driver now uses a locally supported 1920x1080 windowed mode.
The installed Graphics UI also verified that both Upscale Method and Upscale
Quality were already disabled. Its 70-percent Render Scale setting was then
persisted and passed full static validation plus a 90-second enabled-mod smoke.
That second material profile reached 4 January after ten seconds of ordinary
play and 1 June after ten seconds at maximum speed, but the game exited before
the next 20-second screenshot.

The latest crash bundle is
`G:\antiqvitas_user_data\crashes\Europa Universalis V20260720_235625`.
It records `Unhandled Exception C0000005` in the `ffxFsr2ResourceIsNull` /
renderer stack, including the FSR and NGX shutdown frames. The same stack also
occurred on the full-scale profile with 14.6 GB free RAM and 17.3 GB free
pagefile, so neither reduced rendering nor the earlier low-pagefile observation
explains the failure.

The crash logs also exposed nonfatal AD 1 runtime work. The nine generated
institution birth modifiers, legacy hardcoded startup/CoA/flag fall-through,
and the M8/M4 government-law compatibility surface were subsequently fixed and
fresh-observer verified. There is no event-quarantine loader error. The clean
initialization checkpoint does not replace the sustained-playback gate: keep
the bounded renderer reproduction in
`docs/playtests/M12_OBSERVER_RETRY_20260721.md` as the controlling blocker.

Recovery: renderer-profile experimentation is paused after the two material
attempts. Retain the smoke-green 1920x1080, 70-percent profile and continue
with the independent government, coat-of-arms, and international-organization
runtime audit exposed by the live session. Do not claim observer-to-476
coverage until a separately evidenced engine or driver change makes another
attempt material.

## 2026-07-20 - M5 Nubian-gold key lacks a defensible AD 1 site-date match

Status: **deferred; M5 continues with other source-led work.**

P12.1 names Nubian gold, but the accessible evidence does not yet connect a
specific installed EU5 location to securely active AD 1 extraction. Adding a
generic desert gold RGO would turn a regional fact into false site-level
precision; the static RGO override also remains separately runtime-ineffective.

Tried:

1. Reviewed Klemm and Klemm's *Gold and Gold Mining in Ancient Egypt and
   Nubia*, whose catalogue establishes ancient gold-mining landscapes and
   Ptolemaic/Roman chronological categories across the Egyptian and Sudanese
   Eastern Deserts, but whose accessible record does not date one candidate
   map cell to AD 1.
2. Reviewed the exact installed `deraheib` candidate through Cambridge's
   *Deraheib Gold Mines* and later archaeological summaries. They identify the
   Wadi Allaqi gold-mining site but leave its ancient working phase disputed
   between Ptolemaic, possible Roman, and much better attested medieval use.

Recovery: add a source-qualified anchor only when a site publication securely
places a reviewed installed key in production at the campaign boundary. Until
then retain no Nubian-gold correction rather than projecting a later gold rush
into AD 1. Sources reviewed: [Klemm and Klemm](https://link.springer.com/book/10.1007/978-3-642-22508-6), [NewBold](https://www.cambridge.org/core/journals/antiquity/article/deraheib-gold-mines/08FAF70EAD381341D1D84EB3473D74DF), and [the Oxford Handbook survey](https://academic.oup.com/edited-volume/35472/chapter-abstract/303804653).

## 2026-07-21 - M6 Han minority-regency start still falls back to a generated ruler

Status: **deferred; M6 continues with independent power work and remains
untagged.**

The AD 1 country inspector consistently identifies Western Han (`XAR`) but
does not bind the sourced minority ruler. The earlier probes showed `Han
Zhang`; the current post-template-repair probe shows generated `Wang Guangwu,
35` rather than Emperor Ping. The country, Chang'an capital, population,
Han culture, Chinese State Cult, and M6 reform/law profile load without a
corresponding new `error.log` line. This is a silent runtime setup-contract
failure, not a parser or localization error.

Tried:

1. The 2026-07-19 native forms were tested both with Ping as `ruler` and with
   the installed minority form (Ping as `heir`, no simultaneous ruler/current
   term). Both fresh XAR panels showed `Han Zhang`.
2. The 2026-07-21 installed-start inspection established that named ordinary
   incumbents require a paired, date-less `ruler_term`: it binds Augustus and
   Phraates V without asserting an unsupported pre-campaign accession date.
   Applying that term to Ping while retaining the native heir/regency shape,
   then repeating Ping as both `ruler` and `heir`, each produced `Wang
   Guangwu, 35` in a fresh live XAR Government panel.
3. A 2026-07-22 clean-start fixture rendered Ping's directly attested maternal
   link and an analogous Gaius link (`mother = antq_julia_elder` and
   `mother = antq_wei_ji`), with the parents emitted before their children.
   The fresh mod-enabled observer reached 1 January AD 1, but its
   `debug.log` still reported `Invalid heir` for Gaius and Ping and `Invalid
   regent` for Wang Mang. The fixture therefore rules out a sole direct-parent
   link as the hidden start-loader condition; it was fully reverted rather
   than turning a narrow source record into unused gameplay data.

Every attempt passed `make validate` and a mod-enabled `make smoke` with zero
new error-log lines. Evidence is retained in
`docs/screens/20260719_194101/M6_runtime_retry/han_probe.png`,
`docs/screens/20260719_194918/M6_runtime_retry/han_order_second_probe.png`,
`docs/screens/20260721_m6_termless/termless_han_panel.png`, and
`docs/screens/20260721_m6_han_final/han_final_government.png`; the reverted
parent-link fixture is retained locally in
`docs/screens/20260722_m6_parent_link/`.

Recovery: retain the source-led Han roster and the locally evidenced native
heir/regency shape, but do not serialize the failed Ping current term or repeat
him as `ruler`. A later isolated start-manager fixture must identify the hidden
minor/ruler linkage before this profile is accepted. The verified date-less
current-term contract remains in place for the 31 non-regency incumbents. M6
cannot be tagged while this exact Han condition is unresolved; proceed with the
next unblocked milestone work.

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

Status: **superseded as a runtime-renderer blocker on 2026-07-22; the separate
M5 market-route acceptance blocker remains open.**

The generated `in_game/map_data/location_templates.txt` is an exact copy of
the installed map-template file with 327 checked alterations. It parses and
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

Status: **resolved by the M3 political-map gate on 2026-07-22.**

M6 update: the initial Rome/Han/Parthia core now supplies three sourced
government profiles, three dynasties, and nine characters; an AD 1 observer
run contains no new M6 identifier. The remaining Han minority-regency
presentation gap is separately recorded under M6 and does not change M3's
political-map criterion.

M5 update: a subsequent AD 1 observer probe reached 11 January with market
construction notifications and no market, town-setup, RGO, or road errors.
The remaining active categories were unset capital/government and
international-organization/HRE references. Subsequent exact-name M12 guards
and the accepted M9 foundation now own the demonstrated startup/diplomacy
surface. Evidence: `docs/playtests/M5_RUNTIME_FOUNDATION.md`,
`docs/playtests/M9_DIPLOMACY.md`, and
`docs/playtests/M12_CLEAN_INITIALIZATION_20260721.md`.

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

Resolution: the current M3 census confirms 157 roster polities, 157 AD 1
starts and country definitions, all 25 exact start-manager mirrors, and 13,552
sourced controlled locations. A fresh driver run reached the country-selection
map and a paused live Observer session at `08:00, 1 January, 1`; see
`docs/playtests/M3_REPORT.md`. The prior long-observer integration result
remains historical evidence for later milestones, not an M3 acceptance block.

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

## 2026-07-19 - M7 observer confirmation diagnosis (superseded)

Status: **superseded by the resolved country-change game-rule overlay.**

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

The later game-rule audit established that these inputs did reach the UI: the
dialog was rejecting them because `country_change` defaulted to prohibited.
The exact-name overlay documented below now defaults it to allowed. The
2026-07-22 replay entered Observer Mode and reached high speed; its distinct
war-playback result is recorded next.

## 2026-07-22 - M7 AI-war playback reaches the renderer crash boundary

Status: **deferred after two bounded runtime findings; M7 remains untagged.**

The country-change overlay now lets the driver enable Observer and start a live
session. A maximum-speed observer capture advanced from 4 January to 15 March
AD 1 in 35 seconds. To exercise a real conflict rather than wait for an
uncertain early AI declaration, the driver used the generated engine tags
(`XAA` Rome, `XAH` Parthia), declared the controlled Rome-Parthia test war from
the active Rome player context, and returned to Observer. The live War Viewer
listed Roman Commonwealth as attacker against Parthia, Characene, Elymais,
Media Atropatene, Adiabene, Osroene, Gordyene, Sakastan, and Margiana.

Tried:

1. In Observer Mode, tested the locally harvested `declarewar` console contract
   with default and explicit country arguments. The empty War Viewer established
   that it needs an active player context; this was a command-scope finding,
   not a warfare parser failure.
2. Started an active random country, switched with the checked `XAA` engine
   tag, issued `declarewar XAH`, verified the populated War Viewer, then ran
   both sides under the AI Observer at maximum speed. Before the first periodic
   capture the game exited and produced crash bundle
   `Europa Universalis V20260721_221809`. Its exception is the existing
   renderer-family `ffxFsr2ResourceIsNull` / `NVSDK_NGX_D3D12_Shutdown1`
   access violation, not an ANTIQVITAS M7 reference. The crash log contains
   zero matches for `antq_legionaries`, `antq_liburnian`,
   `antq_han_crossbow_infantry`, `antq_cataphracts`, `antq_warbands`,
   `unit_manager`, or `stockade`.

Evidence is retained in `docs/screens/20260721_m7_observer_retest/` and
`docs/screens/20260721_m7_player_war/`; the detailed report is
`docs/playtests/M7_WAR.md`.

Recovery: do not repeat the same renderer profile. The existing M12 renderer
blocker already has two profile attempts, and this M7 replay reproduces the
same engine crash after successfully creating the AI war. Retry M7 only after a
material driver, renderer, or game-build change; then capture the evolving War
Viewer and map at periodic high-speed intervals.

## 2026-07-20 - M8 AI-research observer verification (confirmation finding superseded)

Status: **deferred at the shared renderer boundary; M8 milestone gate remains open.**

The M8 enabled-mod run reached the live AD 1 selector and replayed the visible
OK target of the same irreversible Observer confirmation. The later exact-name
game-rule overlay established that the input was received but country change
was prohibited by the installed default. A 2026-07-22 M7 retest now enters
Observer and runs at maximum speed, but sustained playback reaches the shared
FSR renderer access violation before periodic evidence can be captured. The
implementation is otherwise green (`make validate`, M8 graph checks, and a
zero-new-line menu smoke); see `docs/playtests/M8_KNOWLEDGE.md`.

Recovery: after a material renderer, driver, or game-build change, observe AI
research at high speed. Continue with independent work now; no human input is
required.

## 2026-07-20 - M11 generic-action message registration does not load additively

Status: **resolved through an exact-name, source-pinned overlay.**

The installed build accepted the generated `owncountry` action syntax, the
reviewed tag scopes, `gold` trigger, `add_gold`, and weak prestige/legitimacy/
stability effects. Its enabled-mod menu load nevertheless requires an explicit
`PERFORM_antq_<action>_ACTION` message type for every action. A source-led
40-row decision ledger and renderer are retained in `docs/m11/decisions.csv`
and `tools/m11_decisions.py`.

Tried:

1. Rendered actions with UTF-8 BOM and action localization only. The engine
   parsed the action contract but emitted one missing-message-type line per
   action.
2. Mirrored the locally installed message localization bundle, then rendered
   each `PERFORM_*_ACTION` definition in a BOM-safe additive
   `main_menu/gui/antq_m11_messagetypes.txt` using the exact local schema.
   The menu still reported the same missing types, showing that this GUI
   registry is not additively loaded by this build.

Resolution: `tools/m11_message_overlay.py` made the prescribed one-action
exact-name pilot by copying the configured build's registry byte-for-byte and
appending `PERFORM_antq_endow_public_games_ACTION`. The pilot reached the menu
with zero new error-log lines. The tool then expanded the same pinned overlay
to all 40 ledger entries. It verifies build `24187685`, SHA-256
`610D35361A27253F93EBF6EC3F74247124C998A859B0E6D2BC8908D8741BBD1F`, final
newline behaviour, and the 1,348-definition vanilla inventory before it writes
anything. The full registry passed `make validate` and a clean-retry menu smoke
with zero new lines. Two later full-gate launches exited at the renderer layer
with `ErrorOutOfDeviceMemory` and no parser, registry, or `antq_` log line;
one 960x540 fixed-window retry did not alter that outcome and was reverted.
The successful full-registry menu smoke remains the content acceptance result;
the intermittent Vulkan-memory condition is retained as an M12 long-run
driver-risk, not a reason to retry additive GUI files. Use the guarded
exact-name overlay for future changes.

## 2026-07-20 - M12 historical-hint overlay cannot receive a menu smoke

Status: **deferred after four bounded smoke attempts across two materially
different driver profiles; no hint overlay is retained.**

The local audit identified 32 dated or dynasty-specific vanilla hints (Black
Death, Ottomans, Reformation, Tordesillas, colonial revolution, later regional
dynasties, and comparable situations) and built an exact-name overlay that
made only their `priority` triggers impossible. Static validation passed,
including the source inventory and all existing M0--M11 checks.

The original two enabled-mod smoke attempts exited before the menu at the same
Vulkan `ErrorOutOfDeviceMemory` assertion. After the driver was corrected to
use the installed 960x540 very-low profile and a 90-second post-splash gate,
the overlay was rebuilt from the current source and static validation passed.
Two new smoke attempts again exited at 42--57 seconds during resource loading;
neither `error.log` nor the loader output contained a hint key, script parse
error, or ANTIQVITAS content error. Repeating the unchanged launch would not
distinguish the UI overlay from the established renderer instability, so the
uncommitted overlay and its validator were removed and the last menu-smoked
tree was restored.

Recovery: after a material driver/renderer change yields stable menu launches,
recreate the narrow source-checked overlay and test it once before committing.
Keep generic economy, war, stability, estate, and research hints; the separate
tutorial audit confirms all four installed tutorial chains are non-automatic.

## 2026-07-20 - Observer confirmation root cause is resolved

Status: **resolved through a menu-smoked exact-name game-rule overlay.**

Visual inspection of `docs/screens/M7_war_probe/m7_observer_confirm_retry.png`
shows that the prior Observer confirmation did receive input: it reports
"Country change is prohibited by game rule." The installed
`country_change` rule defaults to `country_change_prohibited`, so the old
normalized-click and Enter attempts could not start an Observer session.

A narrow exact-name overlay retains every installed game-rule definition and
changes only that default to `country_change_allowed`. The prior two smokes
were renderer-bound, not rule errors. After the driver was repaired to emit the
installed very-low graphics contract, the regenerated overlay passed full
validation and an enabled-mod menu smoke with zero new error-log lines. The
guarded generator is retained as `tools/m12_game_rules.py`.

Recovery completed: replay the Observer selection with the now-active rule.
The old normalized-click and Enter attempts remain superseded by the explicit
rule diagnosis rather than counted as a UI-input limitation.

## 2026-07-20 - Two institution-icon prompts returned no image artifact

Status: **resolved through reviewed shared-asset fallbacks; no game-visible
placeholder remains.**

The built-in image pipeline returned no output on two bounded prompts for the
Theological Orthodoxy blank-codex motif, including a simplified
scholarly-consensus rewording. It likewise returned no output on two bounded
Foederati Statecraft clasp-and-cord prompts, including a simplified isolated
object request. The preceding seven institution prompts completed and were
reviewed normally. The image-generation skill forbids silently switching to
its API/CLI fallback without explicit authorization.

Recovery: the static direct-key contract uses the reviewed Hellenistic
scroll/olive icon as a deliberately generic literature proxy for theological
orthodoxy and the reviewed civilian Migrations wagon/bundle icon as a
settlement proxy for foederati. `docs/m11/M11_COMMON_SCREEN_ICONS.md` records
both as non-reconstructive shared assets. Reconsider unique replacements only
after a material image-service change or explicit authorization for its CLI
fallback; do not repeat the same built-in prompts.

## 2026-07-21 - Player-context legacy UI scope audit is deferred

Status: **deferred after two evidence-producing attempts; plain Observer
initialization remains clean.**

The paused `tag XIO` audit starts from the clean AD 1 Observer map and never
advances time, but opening the Xiongnu player context makes the engine evaluate
legacy HRE, Curia, Middle-Kingdom, dynastic-disaster, and steppe-reform UI
availability scripts. The first run recorded 212 `jomini_script_system`
errors: 196 absent international-organization scopes, seven absent-dynasty
comparisons, and nine absent-character/dynasty disaster predicates. Evidence
is retained in `G:\antiqvitas_user_data\logs\error.player_context_pre_guard_20260721_0402.log`
and `docs/screens/player_context_audit/xiongnu_player.png`.

The second attempt generated 18 exact-name local overlays, adding the shared
post-campaign date gate from `tools/dates.py` to all 60 direct availability
blocks in the observed files. Static validation passed, but the same paused
Xiongnu test still emitted all 212 errors: this UI path evaluates nested
scopes despite the enclosing unavailable condition. The overlays and their
validator were removed rather than committed. The confirming log is
`G:\antiqvitas_user_data\logs\error.player_context_guard_attempt_20260721_0409.log`.

Recovery: retain the clean Observer-only checkpoint for initialization and
M9 country-card verification. Do not repeat the same date-gate approach.
Resume this audit only with a materially different engine contract, such as a
locally demonstrated optional scope operator valid for the affected nested
UI predicates, or after a game patch changes the evaluator.
