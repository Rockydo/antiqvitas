# ANTIQVITAS TODO

Tasks are taken top-to-bottom within the current milestone. A milestone closes only
after `make full` and its autonomous driver report are green.

## Active user priorities — 2026-07-22

- [x] Replace all shared/fallback UI visuals with dedicated illustrations for every ANTIQVITAS advance, privilege, building, good, religion, and institution; retain a checked asset ledger and contact-sheet review. (Validated by the 559-chain direct UI ledger and reviewed contact sheet; zero religion or privilege aliases remain.)
  - [x] Start and smoke-check the direct M8 migration: a ledger-driven, one-icon-at-a-time renderer path is live; reviewed Imperial Cult and Public Granaries icons are the first two of 250 direct advance illustrations.

## Manual playtest remediation — 2026-07-24 (resume here)

This section reopens systems that passed earlier file-level gates but failed the
first manual playtest. Take these tasks top-to-bottom before returning to the
milestones below. A parent closes only after its inventory, generator fix,
validator, and short runtime probe pass. "No similar issue" means checking the
complete installed base-game + DLC key union, not only the example observed.
Keep the reduced QA policy: `make validate`, `make smoke`, and small deterministic
subsystem probes; do not substitute multi-year or exhaustive observer runs.

### P0 — Crash and total-conversion leakage barriers

- [x] Replace every vanilla loading-screen mechanical hint, including DLC additions.
  - Fresh AD 1 loads showed ANTIQVITAS quotes above vanilla `Bombard` and
    `Province Capital` explanatory text. These are separate from the completed
    `LOADING_TIP_*` quote union.
  - Harvest the mounted base + DLC hint-key and localization-source union, identify
    the actual load-screen resolver, and exact-name overlay it with concise
    ancient-system guidance. Reject post-476 units, mechanics, ranks, institutions,
    and terminology in every supported client.
  - Acceptance: generated union coverage and anachronism checks are complete; two
    rapid load captures show only ANTIQVITAS quotes and period-appropriate hints.
  - Completed: the exact custom-loading GUI now suppresses the engine's random
    installed-concept panel while preserving the 64 ancient quotes. Two fresh
    non-debug loads showed distinct quotes and no concept text.

- [x] Diagnose and fix the Diseases-tab crash before other runtime work.
  - Preserve the exact evidence bundle at
    `<EU5_USER_DIR>\crashes\Europa Universalis V20260724_145327`
    (manual crash at 16:53 on 2026-07-24). `exception.txt` records an unhandled
    `C0000005 EXCEPTION_ACCESS_VIOLATION` with ANTIQVITAS active; this proves a
    native crash but does not identify the bad disease object or GUI binding.
  - Reproduce from a fresh Rome start with one short driver sequence: open
    Diseases, close it, and open it again. Run one vanilla-only control.
  - Compare the mounted `in_game/common/diseases/*`,
    `in_game/gui/diseases_lateralview.gui`,
    `in_game/gui/shared/diseases_tooltips.gui`, localization, icons, and
    `main_menu/setup/start/19_diseases.txt` against installed 1.3.11.
  - Investigate the strongest concrete lead first: crash `debug.log` says the
    default disease icon could not be found; vanilla has
    `main_menu/gfx/interface/icons/disease/_default.dds`, while the mod does not.
    Determine whether the partial mod asset directory shadows vanilla and mirror
    every required disease icon if so.
  - Fix the missing valid file-magic warning for generated
    `setup/start/19_diseases.txt` per the encoding matrix. The empty manager is
    structurally similar to vanilla and must not be blamed without a control.
  - Do not attribute the earlier market `GoodsMarketEntry` errors or late ambience
    warnings to this crash without a reproducible link.
  - Acceptance: three consecutive open/close cycles in Rome and one in Observer,
    no crash, no new disease/icon/GUI errors, and a normal vanilla control. Archive
    screenshots and delta logs in a focused report.

- [x] Add an installed-content leakage census and mandatory validator.
  - Harvest definitions, unlock references, localization, exact-name source files,
    and art across installed base + all DLC for ages, institutions, advances,
    units, buildings, governments/ranks, pop types, country-history/start text,
    loading tips, and disease UI dependencies.
  - Maintain an allowlist of intentional engine adapters. Every other medieval or
    early-modern definition must be replaced, unreachable, or explicitly disabled
    at both definition and unlock layers. Disabling an advance is insufficient
    when its unit type remains directly recruitable.
  - Scan visible text/references for Renaissance, Feudalism, Redcoats, riflemen,
    grenzer, gunpowder, colonial, absolutism, revolution, enlightenment, and
    post-476 dates. Retain technical identifiers only when locally proven required
    and ensure they never surface to players.
  - Acceptance: compare the current installed union to a generated
    replacement/allowlist union and fail on any uncovered key, including keys added
    by a later DLC or game patch. Store a machine-readable report.

### P1 — Start experience, subjects, recruitment, institutions, and advances

- [x] Remove every vanilla loading quote, including DLC additions.
  - The installed English union has 64 keys: `LOADING_TIP_0` through
    `LOADING_TIP_59` plus `LOADING_TIP_d008_0` through
    `LOADING_TIP_d008_3`; the current generator covers only the 60 numeric keys.
    Harvest the equivalent union for every supported client and exact-name overlay
    every mounted loading-tip source.
  - Update `tools/m12_loading_tips.py` from that ledger. Do not rely on a later
    duplicate localization file; localization mount/first-key precedence is unsafe.
  - Preserve good ancient quotes and record sources/attributions where known.
  - Acceptance: 100% installed-union coverage, every `LOADING_TIP_*` resolves to
    ANTIQVITAS text, and two rapid loading captures under the reduced QA policy
    show distinct ancient quotes with no vanilla text.

- [x] Replace the vanilla bookmark/country-history agenda for every playable start.
  - The Rome report is exactly vanilla
    `main_menu/localization/english/country_history_l_english.yml` key
    `country_history_europe` ("As the Renaissance dawns..."); the mod has no
    exact-name override for that file.
  - Trace which key each of the 157 start countries resolves. Write bespoke,
    sourced AD 1 situations for Tier-1 powers and historically bounded regional
    templates for the rest: immediate conditions, pressures, and plausible period
    goals, without later hindsight stated as contemporary knowledge.
  - Mirror the canonical file in all clients and scan every start/bookmark/
    country-selection localization source for post-476 language.
  - Acceptance: all roster tags resolve to nonempty ANTIQVITAS text; screenshots
    for Rome, Han, Arsacid Iran, one Germanic, one Gallic, one African, and one
    American/Oceanian SoP; prohibited-era text count zero.
  - Completed with 157 exact engine-tag branches, 11 client mirrors, and runtime
    captures for Rome, Han, Parthia, Marcomanni, Atrebates, Kush, and
    Teotihuacan. AD 1 has no independent Gallic roster tag because Gaul is Roman;
    Atrebates is the closest valid Belgic/Celtic playable probe.

- [x] Fix 0% loyalty for Roman subjects and audit all 25 start dependencies.
  - Do not treat 0% as intended. Generated `antq_client_kingdom`, `antq_satrapy`,
    and `antq_tributary` omit a starting `loyalty_to_overlord` modifier, while
    locally inspected vanilla contracts use that field.
  - Verify the exact loyalty/satisfaction calculation and valid fields from local
    subject types and script docs. Record whether the UI value is loyalty, liberty
    desire, or an inverse before selecting numbers.
  - Add a sourced balance ledger with expected start range, autonomy, tribute, war
    duties, relations, and integration rules for Roman clients, Arsacid sub-kings,
    and Han Western Regions tributaries. Preserve meaningful variation.
  - Update `tools/m9_diplomacy.py`; add bounds validation and short tick probes
    for each contract family.
  - Acceptance: no unexplained 0%, all 25 dependencies are within documented
    bands, and Rome/Arsacid/Han subject panels remain stable after a tick.
  - Completed with a 25-row balance ledger, installed-ownable capital gate,
    direct loyalty modifiers, and Rome/Arsacid/Han runtime captures. Batanea's
    invalid mountain-wasteland seat was replaced by an ownable inland proxy;
    fresh Rome retained all 11 subjects after the first tick.

- [x] Quarantine every anachronistic unit and rebuild recruitment availability.
  - [x] Mirror all 31 installed unit-type sources: 311 legacy definitions are
    hidden/non-buildable, 12 locally required copy-chain adapters are allowlisted,
    and 44 ancient definitions remain active.
  - [x] Exact-name disabled all non-ANTIQVITAS definitions and scanned reverse
    references. Installed UI/script inspection proved six slots mandatory; the
    final arc is now Federate Age (376) plus Migrations (395), both bounded by 476.
  - Acceptance: machine-readable active-unit allowlist, zero vanilla unit keys in
    recruitment at every age, and rapid Rome/Germania/Han land/naval captures with
    no missing-definition errors.
  - Completed: 44 active ancient keys, zero inherited recruitables, and clean
    Rome/Han/Germania rapid probes plus smoke.

- [x] Give every active unit a dedicated period-correct icon.
  - Build the ledger from the final active allowlist, not only the current 44 custom
    types. Include land, naval, levy, mercenary, and cultural variants such as Roman
    Marines.
  - Trace vanilla path/dimensions/alpha/mask/fallback behavior. Generate one direct
    icon per key from real archaeological or material references via §20; no
    aliases, default art, medieval kit, or firearms.
  - Acceptance: format/alpha/resolver validator, no active key resolves to
    `_default` or another unit's art, reviewed regional contact sheets, and the
    targeted recruitment captures above.
  - Completed: 44 unique direct illustrations and masks from 11 reviewed
    four-up sheets; exact resolver, contact-sheet, and live recruitment checks pass.

- [x] Replace leaked vanilla institutions and constrain cultural spread.
  - The mod still defines Feudalism, Legalism, and later vanilla institutions in
    exact-name files with `can_spawn = { always = no }`; that stops spawning but
    does not remove them from the UI. Make legacy keys invisible while satisfying
    any locally proven hard references.
  - Inventory base + DLC institution keys across all six engine age slots. Fail if
    the visible set differs from the approved ANTIQVITAS ledger.
  - Redesign every custom institution's birth, eligibility, propagation, and
    embrace rules. `antq_han_bureaucratic_statecraft` currently has generic
    neighbour/trade/market spread, so Rome can acquire it automatically. Keep it in
    appropriate East Asian administrative contexts unless a deliberately authored,
    prerequisite-gated cross-cultural adoption path exists.
  - Acceptance: Rome, Han, and Arsacid panels at every available age show only
    period institutions; Feudalism/Legalism/later vanilla entries are absent; Han
    statecraft cannot reach Rome by ordinary trade; no missing-key errors.
  - Completed: 18 installed institutions are removed from the registry; all 92
    installed reference files are covered by exact overlays. Nine ancient
    institutions gate every birth/spread channel by cultural-region profile;
    Han statecraft has no ordinary trade spread. Rome/Han/Arsacid six-age probes,
    72 checks, and paired smoke pass.

- [x] Rebuild advances as a deep, branching, culture-aware ancient DAG.
  - Create a design ledger for every node: key, age, branch, prerequisites, layout,
    shared/regional eligibility, description, sources, effects, unlocks, AI weight,
    and icon. Preserve the existing advance art that meets the visual bar.
  - Replace straight vertical chains with branching and convergence. Provide shared
    foundations plus substantial Roman/Italic, Hellenic, Celtic, Germanic,
    Iranian/steppe, Indic, Han/East Asian, Near Eastern, African, American, and
    Oceanian paths. Use adoption prerequisites where transfer is plausible rather
    than simplistic culture locks.
  - Every visible node needs a period description and at least one consequential,
    valid modifier or unlock. Tie buildings, units, laws, privileges, reforms,
    diplomacy, economy, events, and institutions into coherent packages.
  - Remove all links to vanilla advances and reverse links from other systems.
    Resolve the sixth slot only after checking the installed age/index contract.
  - Validate acyclicity, reachability, age order, branch/depth targets, active
    unlock targets, complete localization/effects/direct art, and zero post-476
    tokens.
  - Acceptance: focused early/mid/late tree captures for Rome, a Germanic/Celtic
    polity, Han, an Iranian polity, and a non-Eurasian SoP; paths visibly differ
    and offer real choices. No long playthrough required.
  - Completed: 250 nodes form a six-age DAG with 50 roots, 50 branch points,
    20 convergences, and 80 terminal choices across 11 profiles. Exact unlocks
    cover 154 buildings, 44 units, 19 reforms, 24 privileges, 10 CBs, and five
    subject types. Five-profile probes, 72 checks, and paired smoke pass.

### P2 — Population, peoples, polities, and period terminology

- [x] Rebuild population calibration for Italy and major ancient cities.
  - The report is confirmed: generated Rome has one 60.901k Latin peasant pop, an
    artifact of generic density weighting and not an acceptable Augustan metropolis.
  - Create a sourced target/uncertainty ledger distinguishing game location, city
    proper, agglomeration, and hinterland. At minimum audit Rome, Alexandria,
    Antioch, Carthage, Ephesus, Pergamon, Capua, Puteoli, Mediolanum, Athens,
    Corinth, Jerusalem, Seleucia-Ctesiphon, Babylon, Merv, Taxila, Pataliputra,
    Chang'an, Luoyang, and the remaining top locations surfaced by `popcheck`.
  - Add an Italy subregional ledger and rebalance urban/rural shares within the
    existing Roman-world macro target before changing the 47.5m empire total.
    Compare geography and culture separately: Latin is not synonymous with Italy
    or the Roman Empire, so decompose the reported 2m Latin vs 5m Gaul comparison.
  - Expand `docs/m4/population_location_overrides.csv` (currently four unrelated
    Southeast Asian rows) or add a sourced city input; never hand-edit `06_pops.txt`.
  - Acceptance: city min/max checks, Italy/region/culture cross-tables, documented
    macro-total preservation, and top-20 city panel/map captures.
  - Completed: 47 audited city rows provide 45 fixed map targets; seven Italy
    subregions total 7.5m within an unchanged 47.5m Roman Empire and 230m world.
    The capped residual prevents untargeted locations exceeding 75k. Rome is
    1.0m; Alexandria 500k; Jingzhao 650k; Ctesiphon 350k; Pataliputra 300k;
    Antioch 220k; Ephesus 180k. Antioch is now Roman and Hellenophone. Generated
    cross-tables, 73 checks, paired smoke, and a rapid seven-city map probe pass.

- [x] Expand political granularity where residual SoPs create giant blobs.
  - This requires new tags/contracts/capitals/CoAs/ownership, not just detailed
    culture selectors. Reopen the 157-polity roster in priority order:
    (1) Germania and Venedi-facing lands, (2) Gaul/Rome's northern frontier,
    (3) Finnic/Siberian frames, (4) Yayoi Japan, (5) West Africa.
  - Deepen Germania from dated source ledgers: audit Cherusci, Chatti,
    Marcomanni, Quadi, Hermunduri, Semnones, Langobardi, Chauci, Frisii, Batavi,
    and other attested peoples without turning uncertain ethnonyms into fixed
    modern borders or centralized states.
  - Split the gigantic Venedi residual into bounded, source-labeled peoples,
    confederations, or archaeological SoPs. Reassess Venedi, Lugian, Bastarnian,
    Sarmatian, and neighbouring frames; a culture selector is not proof of a state.
  - Use conservative archaeological/cultural SoPs in Finnic/Siberian and West
    African regions where states are unattested. Split unified Japan into multiple
    bounded AD 1 Wa/Yayoi regional or kin-group frames; do not backdate
    third-century Yamatai or a unified Japanese state.
  - Every addition needs the full M3 contract: sources/confidence, government,
    rank display, culture/faith, capital, ownership, ruler if justified, diplomacy,
    CoA, localization, AI, and setup validation.
  - Acceptance: no residual tag controls an implausibly huge multicultural
    macro-region solely for coverage; before/after political captures and
    size/location counts for all five target regions.
  - Completed: added 72 sourced Tier-3 peoples, archaeological horizons, and
    community frames, taking the roster from 157 to 229. Germania/Scandinavia,
    Venedi, Finnic/Siberian, Wa Japan, and West African residuals fell from
    639/997/337/342/367 locations to 72/56/36/9/24. Every addition has an owned
    capital, explicit culture/faith profile, government/rank/AI start, diplomacy,
    regional CoA, localization, agenda, and validation coverage. A fresh AD 1
    selector probe has zero primary-culture or discriminated-estate diagnostics;
    the older Indo-Greek `sagala`/West-African map-key collision is also repaired.
    Full validation passes 74/74 and paired smoke has zero mod-only lines.

- [x] Make Gallic culture/pop assignment genuinely granular.
  - Audit actual culture on every Gallic pop/location, not only definitions and
    selector rows. Broad `antq_gallic` still appears in generated pops (for example
    Romorantin) despite the claimed detailed selector pass.
  - Assign bounded Arvernian, Aeduan, Sequanian, Remian, Belgic, Aquitanian, and
    other supported frames. Distinguish ethnopolitical labels, language continua,
    and Roman administrative geography.
  - Forbid generic `antq_gallic` inside a reviewed specific selector unless the
    fallback is documented. Cross-check primary culture, pop culture, dynamic
    names, and political ownership without assuming all four must be identical.
  - Acceptance: location-level Gaul ledger, aggregate totals, and culture-map
    captures with no unexplained broad blocks.
  - Completed: the generated atlas now assigns 503 reviewed locations across 63
    specific cultures and 15.512m people. All 175 generic base-pop assignments,
    the obsolete `antq_gallic` definition, and its 0.001 compatibility pop are
    gone. Twelve additional peoples and 35 province selectors close the remaining
    broad blocks; the exact atlas validator, 75 checks, paired smoke, and fresh
    culture-map/New Game probes pass with no culture diagnostics.

- [x] Verify and complete Galatian representation in AD 1 Anatolia.
  - Existing data has Tectosagian pops and Tolistobogii/Trocmi definitions; do not
    invent an independent unified Galatia merely for visibility. Research status
    after Roman annexation in 25 BC, continued identity, and settlement geography
    through the plan bibliography, Strabo XII, epigraphic/numismatic evidence,
    CAH/OCD, and modern Anatolian synthesis.
  - Audit all three communities' location assignments and whether Roman ownership,
    administration, or religion erases culture. Remove the stray 0.001 generic
    `antq_galatian` fallback if it is only a compatibility artifact.
  - Acceptance: sourced culture-location ledger, Roman ownership unless a dated
    exception is supported, all justified communities visible, and an Anatolia
    culture-map capture.
  - Completed: the Roman-owned Ancyra/Tectosages, Pessinus/Tolistobogii, and
    Tavium/Trocmi proxies total 269.842k across 19 reviewed locations. The generic
    Galatian fallback is gone; generated ledgers, validation, smoke, and the AD 1
    selector pass. See `docs/playtests/M4_GALATIAN_ATLAS_20260725.md`.

- [x] Replace medieval pop-class presentation with ancient terminology and art.
  - Inventory all eight engine keys (`nobles`, `clergy`, `burghers`, `laborers`,
    `soldiers`, `peasants`, `tribesmen`, `slaves`) and every hardcoded script,
    estate, economy, GUI, localization, portrait, and icon dependency.
  - Test whether new pop keys are safely extensible. If not, retain technical keys
    but relocalize to broad ancient semantics: landed elites, priesthoods, urban
    citizens, laborers/artisans, military households, cultivators, tribal
    communities, and enslaved people. Add Roman/Hellenic/Han/etc. scoped names only
    if local customizable localization supports them; do not impose Roman classes
    worldwide.
  - Replace all pop icons/portraits with dedicated ancient imagery and trace every
    fallback. Represent slavery precisely and soberly.
  - Acceptance: no medieval Burgher/Noble presentation in Roman, Germanic, Gallic,
    Han, or West African samples; eight distinct period assets; stable economy and
    save/reload.
  - Completed: all eight hardwired engine keys retain compatibility but resolve
    to ancient terms and 56 direct, region-aware DDS targets derived from 48
    reviewed masters. Exact resolver checks, contact-sheet review, validation,
    paired smoke, and focused UI checks pass.

- [x] Replace "County" and other medieval rank presentation for tribes/SoPs.
  - The generator assigns `rank_county` to SoPs and vanilla's default localization
    is "County". Vanilla has contextual `rank_county_tribe`, but the current custom
    government/reform context is not selecting it.
  - Trace the installed rank/customizable-localization resolver. Preserve numeric
    rank if required while displaying a roster-led period term: tribe, people,
    confederation, league, city-state, kingdom, chiefdom, or archaeological SoP.
    Do not globally rename every county to Tribe.
  - Audit ruler titles and rank-up actions/tooltips so Count, Duke, Duchy, and
    medieval elevation language do not leak from adjacent UI.
  - Acceptance: every current and newly added tag resolves to a documented period
    label in selection, diplomacy, map tooltips, and rank panel; no tribal/SoP
    sample shows County.
  - Completed: all 229 design/engine tags resolve through 12 documented ancient
    presentation classes while retaining required technical ranks. Raw fallbacks,
    ruler labels, and elevation actions are neutralized in all 11 clients; the
    New Game probe shows `People of Venedi`, `Leader`, and `Realm of Roxolani`.

- [x] Reopen player-facing location-name accuracy beyond mere key coverage.
  - The existing validator proves that all 28,573 map keys have a display label,
    but 26,230 are synthetic Tier-3 forms. Coverage alone does not prove that a
    visible name is correct for AD 1.
  - Prioritize every capital, the calibrated top cities, Italy and the Roman
    provinces, Germania/Venedi-facing lands, Gaul, Anatolia, Han cores, India,
    Japan, and West Africa. Classify names as attested, securely reconstructed,
    conservative regional proxy, or engine-only fallback; never present a
    synthetic Latin-looking form as sourced.
  - Audit direct and dynamic names together, including diacritics, duplicate
    settlements, renamed proxy locations, map labels, country-selection views,
    and culture/language fallbacks. Reject medieval, modern-national, colonial,
    or post-476 names unless the physical feature genuinely retained the same
    ancient name and the ledger records it.
  - Acceptance: source/confidence coverage for every high-visibility location,
    prohibited-era and unexplained-modern-name count zero in the priority
    regions, and rapid regional map captures rather than a 22,000-location manual
    sweep.
  - Completed: a generated 1,932-field priority ledger covers all 229 capitals,
    all 45 calibrated cities, all 72 urban nodes, Italy, Roman provincial
    theatres, Germania, Gaul, Anatolia, Han macro-regions, India, Japan, Sahel,
    and Guinea. It replaces 1,010 non-Roman synthetic forms with attested names
    or explicit geographic/territorial proxies, while 202 unresolved Roman
    fields deliberately retain the stricter Roman audit's vanilla pass-through;
    priority Tier-3 runtime count is zero.

### P3 — Roman economy and cohesive ancient interface art

- [ ] Deepen and audit the Roman building/trade-good system before freezing art.
  - Treat the existing 154 active building families and 1,804 placements as a
    starting inventory, not proof of engaging gameplay. Trace actual availability,
    costs, inputs, outputs, staffing, profitability, infrastructure, urban-rank,
    advance, privilege, law, and AI conditions from the local engine files.
  - Build layered Roman/Italic development around households and estates,
    workshops, markets and fora, ports and river trade, roads and cursus publicus,
    warehouses and the annona, baths and water supply, temples and civic display,
    mines/quarries, ceramics, glass, metalwork, textiles, wine/oil, military
    supply, castra, coloniae, and frontier logistics. Give provincial economies
    distinct strengths without turning every historical structure into a unique
    building.
  - Audit every active raw and processed good against AD 1 production geography
    and trade use. Reuse valid engine goods; add a new good only when it supports
    a real production/trade decision and can receive complete RGO, building,
    market, localization, AI, and art contracts. Check especially grain/annona,
    wine, olive oil, fish products, salt, timber, iron/copper/lead, marble and
    other stone, ceramics, linen/wool/silk, papyrus, glass, incense, horses,
    camels, slaves, and luxury imports.
  - Acceptance: Rome/Italy and at least ten contrasting Roman provinces offer
    multiple viable, period-specific development paths; all buildings have useful
    effects or production roles and sensible AI access; trade-good map and market
    captures show plausible regional specialization; static economic assertions,
    a short construction/market tick probe, validation, and smoke pass.
  - [x] First economy tranche: 23 Roman families, 509 placements across 15
    profiles, eight processed goods, 31 direct assets, and exact quarantine of
    450 legacy buildings. All 75 checks and paired smoke pass; a fresh Rome run
    reached 31 January without building/market-scope errors.
  - [x] Freeze the active goods/building registry and replace all 15 temporary
    installed adapters. All 465 installed building definitions are quarantined;
    eight namespaced replacements have direct checked art and the start now has
    2,415 non-duplicate placements.
  - [ ] Finish acceptance with an established-market production/export capture
    and construction-choice probe. The repeated debug-renderer limit is recorded
    in `BLOCKERS.md`; resume only through a durable non-debug/current-save route.

- [ ] Re-art the complete active building-icon set in one circle-safe style.
  - Freeze the final active building ledger, including Roman named, regional,
    economic-family, and advance-unlocked content.
  - Inspect vanilla dimensions, alpha, circle mask, compression, and in-widget crop.
    Canonical spec: deep desaturated dark-blue background, circle-safe composition,
    consistent value/contrast/scale, no square card edge, no generic yellow filter,
    and no medieval architecture.
  - Record a real reconstruction, surviving structure, plan, coin, relief, or
    materially comparable dated reference and visual rationale before generating
    each icon. Use §20 contact sheets, then export one direct asset per active key.
  - Validate dimensions/format, aliases/fallbacks, transparent corners, circular
    safe-zone occupancy, background range, and perceptual duplicates. Review
    circular-mask previews, not only square sources.
  - Acceptance: reviewed complete contact sheets and building-grid captures for
    Rome, Germania/Gaul, Han, India, and one African polity; no square edge, clipped
    subject, style outlier, alias, or fallback.

- [ ] Replace medieval character/court backgrounds across graphical cultures.
  - Trace the exact live texture from screenshots rather than assuming it is the 3D
    portrait. Inventory country-selection, character, ruler, event-portrait, and
    court-scene fallbacks across base + DLC graphical-culture paths.
  - Create cohesive 2D ancient backdrops for Roman/Italic, Hellenistic, Celtic,
    Germanic, Iranian/steppe, Indic, Han/East Asian, Near Eastern, African,
    American, and Oceanian contexts using real material/architectural references.
    Do not touch audio or add unsupported 3D models.
  - Acceptance: resolver ledger has no medieval/default fallback and at least eight
    graphical-culture captures show correct ancient settings on every live surface.

### P4 — Focused regression closeout

- [ ] Add one rapid regression route for this remediation section.
  - Script a deterministic 10-15 minute route: loading screen -> Rome description
    -> start -> subjects -> city/pop -> buildings -> recruitment -> institutions
    -> advances -> Diseases open/close -> save/reload.
  - Repeat only culture-variable subsystem screens for one Germanic/Gallic country
    and Han; use static setup/resolver validation for the rest.
  - Require `make validate`, `make smoke`, zero new `error.log` lines against the
    accepted baseline, no crash, and a small screenshot manifest. Do not run an
    extreme 1-476 campaign or multi-century observer soak.
  - Before closing, rerun the installed-content leakage census and ensure every
    manual symptom above has a specific passing assertion.

## M0 — Discovery & tooling

- [x] Discover Steam libraries, game/user paths, disk space, and write `config/local_paths.json`.
- [x] Create the repo on the game drive; move the master plan into `docs/`; configure caches and local Python environment.
- [x] Establish mod visibility using user-dir relocation, a directory junction, or direct CLI loading, in that order.
- [x] Build Steam startup, launcher/playset enablement, game driver console tier, vanilla extractor, linter, pop checker, smoke tester, DDS/date/localization tools.
- [x] Harden the game driver's early-exit reporting and exact-install crash-reporter cleanup so failed launches leave usable autonomous evidence.
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
- [x] Enable the generated five-age skeletons and interim placeholder advances with that calendar layer (the placeholders were retired once M8 supplied the full tree).
- [x] Verify year-one UI and save reload; run milestone gate and tag `M2-done`.

## M3 — Political map

- [x] Create and validate the sourced initial AD 1 polity roster in `docs/world_1ad/`.
- [x] Generate collision-safe country definitions, mirrored names, and M3 placeholder CoAs for every roster polity.
- [x] Add a checked capital-location candidate report and record direct local-map matches.
- [x] Render and smoke-check worldwide AD 1 ownership (157 polities; 13,552 controlled locations and 25 dependencies; 13,535 of 13,576 ownable locations assigned, with 41 documented intentional empties).
- [x] Build a local-raster coordinate index and sourced capital-candidate report.
- [x] Research and create the remaining territorial/SoP coverage with an ordered residual-coverage ledger and an explicit intentional-empty audit.
- [x] Mirror-replace the exact 25 installed start-manager files, removing the vanilla 1337 start layer.
- [x] Run the M3 political-map gate, pass `make full`, and tag `M3-done` (22 July 2026; the 157-polity/25-manager census and fresh paused AD 1 Observer map are recorded in `docs/playtests/M3_REPORT.md`).

- [x] Make sure every single location (there are 22,000) has a period appropriate name, there should in theory be no vanilla names left (as far I know, perhaps some hold up). (28,573 map keys now have an explicit period display label: 2,343 sourced or qualified Tier 1/2 names and 26,230 clearly-marked synthetic Tier 3 forms.)
	- [x] This is a colossal task so some shortcuts will obviously be needed, here's how you will proceed :
		- You will prioritize size and location to define tiers of how historically accurate and checked things need to be
		- What increases a tier ?
			- If the location is in Roman or in Europe/North Africa/the Levant where most people will play. Asia is less important. Americas and Oceania a lot less important
			- Population : higher population locations (ie town, cities, megalopolises, etc) get more priority
		- Based on the tier you will either :
		- [x] Tier 1 : Do as you've been doing so far, check historical sources
		- [x] Tier 2 : Very light check, the goal is to go fast and cover a lot, make unverified assumptions, invent a little if needed
		- [x] Tier 3 : No check at all, either keep vanilla if its a location that hasn't really changed (ie ancient theoretical tribal names or whatever). Otherwise just use the vanilla name and latinize it/ greekicize it/ ancient germanizeit, etc so it doesn't look too modern
		- Overall you'll need to be doing large batches of hundreds/thousands of locations at a time per commit to cover the full 22,000ish location map
		
## M4 — Peoples & faiths

- [x] Seed and smoke-check the additive culture/religion foundation (69 cultures, 37 religions, 27 culture groups, and 14 religion groups).
- [x] Generate and smoke-check engine-valid ancient dialect/namelist layers (27 language roots, dialects, and localized source-name pools).
- [x] Bind the sourced culture/faith tree to all 157 country profiles (34 regional bases and 48 source-labelled tag overrides).
- [x] Bind the sourced culture/faith tree to global pop data (13,552 base pops; 230,000 thousand total; all section 12.4 macro checks).
- [x] Generate conservative sourced dynamic-name v1 (61 coordinate-verified capital anchors, localized for all supported clients).
- [x] Audit the 680 installed culture templates active in the AD 1 ownership surface, with profile candidates and explicit no-template exceptions.
- [x] Probe the paused AD 1 Observer culture and location-religion map modes; both render sourced regional atlases without script-system diagnostics.
- [x] Add a source-labelled geography-selector culture ledger: 47 reviewed regional selectors resolve 1,406 exact controlled locations, and 22 new culture definitions bring the catalog to 91.
- [x] Extend the selector ledger across Britain, Ireland, Germania, Scandinavia, Finland, and the Baltic: 46 further selectors resolve 1,482 locations, bringing the audited atlas to 2,888 locations across 37 mapped cultures.
- [x] Extend the selector ledger through South Asia and Southeast Asia: 29 further selectors resolve 1,320 locations and add 11 culture definitions, bringing the audited atlas to 4,208 locations across 52 mapped cultures.
- [x] Extend the selector ledger through Iran, the Caucasus, Central Asia, and the Pontic: 25 further selectors resolve 1,093 locations and add 5 culture definitions, bringing the audited atlas to 5,301 locations across 68 mapped cultures.
- [x] Extend the selector ledger through Korea and the northeast steppe: 15 further selectors resolve 365 locations and add 5 culture definitions, bringing the audited atlas to 5,666 locations across 74 mapped cultures.
- [x] Extend the selector ledger through Africa: 13 further selectors resolve 533 locations and add 8 culture definitions, bringing the audited atlas to 6,199 locations across 85 mapped cultures.
- [x] Extend the selector ledger through the Americas: 17 further selectors resolve 344 locations and add 5 culture definitions, bringing the audited atlas to 6,543 locations across 94 mapped cultures.
- [x] Extend the selector ledger across the controlled Oceanian surface: 6 further selectors resolve 12 locations and add 4 culture definitions, bringing the audited atlas to 6,555 locations across 98 mapped cultures.
- [x] Extend the selector ledger through Han China and its southern/southwestern frontiers: 32 further selectors resolve 1,807 locations and add 15 culture definitions, bringing the audited atlas to 8,362 locations across 113 mapped cultures.
- [x] Extend the selector ledger through the Roman world: 39 further selectors resolve 838 locations and add 4 culture definitions, bringing the audited atlas to 9,200 locations across 120 mapped cultures.
- [x] Extend the selector ledger through the source-led Venedi SoP frames: 2 further selectors resolve 845 locations and add 2 culture definitions, bringing the audited atlas to 10,045 locations across 122 mapped cultures.
- [x] Extend the selector ledger through core Yayoi Wa, the Tibetan plateau, and interior Arabia: 13 further selectors resolve 714 locations, bringing the audited atlas to 10,759 locations across 125 mapped cultures.
- [x] Extend the selector ledger through bounded South Asian Prakrit, Tamil, and Himalayan frames: 14 further selectors resolve 467 locations and add 2 culture definitions, bringing the audited atlas to 11,226 locations across 127 mapped cultures.
- [x] Refine source-led Germanic tribal frames and map Marcomannic Bohemia: 1 further selector resolves 40 locations and adds 7 culture definitions, bringing the audited atlas to 11,266 locations across 134 mapped cultures.
- [x] Extend the bounded Amur-Yilou archaeological frame through the middle/lower Amur and Ussuri-Maritime: 3 further selectors resolve 125 locations and bring the audited atlas to 11,391 locations across 135 mapped cultures.
- [x] Add bounded intra-Carpathian Dacian and lower-Danube Getic frames: 2 further selectors resolve 77 locations and add 1 culture definition, bringing the audited atlas to 11,468 locations across 137 mapped cultures.
- [x] Complete the remaining Korean peninsula surface with Samhan and guarded generic-Korean frames: 3 further selectors resolve 52 locations, bringing the audited atlas to 11,520 locations across 138 mapped cultures.
- [x] Map the bounded Iberian-Colchian Kartvelian continuum across the remaining Georgia area: 1 further selector resolves 49 locations, bringing the audited atlas to 11,569 locations across 139 mapped cultures.
- [x] Extend the bounded northern-Mesopotamian Aramaic proxy through Jazira: 1 further selector resolves 48 locations, bringing the audited atlas to 11,617 locations across 139 mapped cultures.
- [x] Expand the culture/location remap to the plan's 350-culture density floor with reviewed regional primary-source corpora; the 506 selectors resolve 12,058 controlled locations across 329 mapped cultures, and no AD 1 identity was inferred from a vanilla template key.
- [x] Add reviewed dynamic names beyond capital anchors: 24 secure direct toponyms extend the 61 coordinate-verified capital anchors, with each dynamic-language lookup and source recorded in `docs/m4/dynamic_location_name_overrides.csv`.
- [x] Add source-keyed Roman-world naming passes: 28 further Italian and Sicilian locations now render direct AD 1 forms from exact Pleiades city points, bringing the checked layer to 61 capitals plus 51 curated names.
- [x] Add the Late-Preclassic Petén lowland Maya frame: 1 further selector resolves 4 locations, bringing the audited atlas to 11,621 locations across 139 mapped cultures.
- [x] Add a bounded lower-Rhine Batavian proxy for the wholly Batavian Holland scope: 1 further selector resolves 18 locations and adds 1 culture definition, bringing the audited atlas to 11,639 locations across 140 mapped cultures.
- [x] Add the bounded Moravian Quadi frame: 1 further selector resolves 16 locations and adds 1 culture definition, bringing the audited atlas to 11,655 locations across 141 mapped cultures.
- [x] Add the archaeology-first central-Vietnam Sa Huynh frame: 1 further selector resolves 29 locations and adds 1 culture definition, bringing the audited atlas to 11,684 locations across 142 mapped cultures.
- [x] Add the bounded interior Gaetulian high-plateau frame: 1 further selector resolves 30 locations, bringing the audited atlas to 11,714 locations across 142 mapped cultures.
- [x] Correct the backdated Moche AD 1 start: replace it with a contested Gallinazo Moche-Valley SoP, use a generic non-uniform Andes scaffold, and create plural Moche Polities through the sourced AD 100 historical current (165 culture definitions; the 313-selector atlas remains at 11,714 locations).
- [x] Add the cautious lower-Yik Sarmatian material-cultural frame: 1 further selector resolves 33 locations, bringing the audited atlas to 11,747 locations across 142 mapped cultures.
- [x] Add the cautious Sulawesi Austronesian frame: 1 further selector resolves 57 locations, bringing the audited atlas to 11,804 locations across 143 mapped cultures.
- [x] Add the contested Central Mexican Teotihuacan-rise frame: 1 further selector resolves 45 locations, bringing the audited atlas to 11,849 locations across 144 mapped cultures.
- [x] Add the cautious southern-Lake-Chad Chadic Basin frame: 1 further selector resolves 18 locations and adds 1 culture definition, bringing the audited atlas to 11,867 locations across 145 mapped cultures.
- [x] Add the fading late-Nok central-Nigerian horizon: 1 further selector resolves 21 locations and adds 1 culture definition, bringing the audited atlas to 11,888 locations across 146 mapped cultures.
- [x] Add the cautious Omsk-Irtysh Sargat frame: 1 further selector resolves 28 locations and adds 1 culture definition, bringing the audited atlas to 11,916 locations across 147 mapped cultures.
- [x] Add the cautious Transdanubian Pannonian frame: 1 further selector resolves 31 locations, bringing the audited atlas to 11,947 locations across 147 mapped cultures.
- [x] Add the contested Upper-Selenga Xiongnu core frame: 1 further selector resolves 23 locations, bringing the audited atlas to 11,970 locations across 147 mapped cultures.
- [x] Add the exact Khotan Oasis frame: 1 further selector resolves 1 location and adds 1 culture definition, bringing the audited atlas to 11,971 locations across 148 mapped cultures.
- [x] Add the cautious Vyatka Permic frame: 1 further selector resolves 18 locations and adds 1 culture definition, bringing the audited atlas to 11,989 locations across 149 mapped cultures.
- [x] Add the cautious Kama-Perm Permic frame: 1 further selector resolves 22 locations, bringing the audited atlas to 12,011 locations across 149 mapped cultures.
- [x] Add the cautious central-Oman Samad archaeological frame: 1 further selector resolves 7 locations and adds 1 culture definition, bringing the audited atlas to 12,018 locations across 150 mapped cultures.
- [x] Add the bounded Surgut-Narym Ob Kulay archaeological frame: 3 further selectors resolve 12 locations and add 1 culture definition, bringing the audited atlas to 12,030 locations across 151 mapped cultures.
- [x] Add the exact Kucha Oasis frame: 1 further selector resolves 1 location and adds 1 culture definition, bringing the audited atlas to 12,031 locations across 152 mapped cultures.
- [x] Add the exact Loulan city-oasis frame: 1 further selector resolves 1 location and adds 1 culture definition, bringing the audited atlas to 12,032 locations across 153 mapped cultures.
- [x] Add the exact Yarkand Oasis frame: 1 further selector resolves 1 location and adds 1 culture definition, bringing the audited atlas to 12,033 locations across 154 mapped cultures.
- [x] Add the exact Aksu Oasis frame: 1 further selector resolves 1 location and adds 1 culture definition, bringing the audited atlas to 12,034 locations across 155 mapped cultures.
- [x] Add the exact Kashgar Oasis frame: 1 further selector resolves 1 location and adds 1 culture definition, bringing the audited atlas to 12,035 locations across 156 mapped cultures.
- [x] Add the exact Hami and Turpan Oasis frames: 2 further selectors resolve 2 locations and add 2 culture definitions, bringing the audited atlas to 12,037 locations across 158 mapped cultures.
- [x] Refine the Iberian atlas with 38 named primary-source ethnographic frames: 38 province selectors now refine broad regional proxies, leaving 373 reviewed selectors resolving 12,037 locations across 196 mapped cultures and raising the catalogue to 217 definitions.
- [x] Refine the Gallic atlas with 47 named primary-source ethnographic frames: 47 province selectors now refine broad regional proxies, leaving 420 reviewed selectors resolving 12,037 locations across 243 mapped cultures and raising the catalogue to 264 definitions.
- [x] Refine the Balkan-Anatolian atlas with 50 named primary-source ethnographic frames: 50 province selectors now refine broad regional proxies, leaving 470 reviewed selectors resolving 12,058 locations across 292 mapped cultures and raising the catalogue to 314 definitions.
- [x] Refine the Germanic and Baltic atlas with 36 cautiously bounded source frames: 36 province/location selectors now refine broad regional proxies, leaving 506 reviewed selectors resolving 12,058 locations across 329 mapped cultures and raising the catalogue to the plan's 350-definition floor.
- [x] Run the initial M4 full and observer gate; preserve the two failed pre-repair startup attempts as historical evidence rather than relaxing the no-template-inference rule.
- [x] Final M4 acceptance: the current build reaches a paused AD 1 observer at `08:00, 1 January, 1`; Culture (Location) and Religions (Location) both render from the 350-culture/37-religion atlas.
- [x] Pass the final culture/religion atlas checks and complete the current `make full` gate with zero new smoke lines.
- [x] Run milestone gate and tag `M4-done`.

- [x] Canonicalize the master-plan culture completion: fold all 23 promised definitions and assignments into the primary M4 ledgers; remove the temporary secondary generator and staging ledgers.
- [x] Finalize Britain and Ireland in detail: 34 British and 16 Hibernian culture definitions, complete controlled-province coverage, narrow frontier overrides, matching polity profiles, and canonical generated outputs.

## M5 — Economy

- [x] Replace generic Roman civic/economic proxies with a source-led named building pass: 28 direct-icon specials now cover water, public grain storage, Forum Romanum/Augusti, Basilica Aemilia, macellum, Horrea Galbana, baths, Theatre of Marcellus, Mars Ultor cult, Tabularium, Circus, mint, workshops, mill/bakery, Villa Liviae, the Pantheum, Saepta, Diribitorium, the Palatine Temple of Apollo and library, Curia Iulia, Porticus Octaviae, Tiber Emporium, Aqua Alsietina, the naval bases at Rome and Ravenna, and the Mogontiacum frontier camp. See `docs/m5/roman_buildings.csv` and `M5_ROMAN_CIVIC_BUILDINGS.md`.
- [x] Add the source-led naval-supply pass: Navalia Romae is now a named, direct-icon special tied to tar, naval supplies, tools, lumber, and cloth, with modest sailor/repair effects and an explicitly contested Augustan configuration.
- [x] Add the securely dated Augustan naval-base pass: Classis Ravennatis is now a named Ravenna special, tied to direct military-port evidence at nearby Classe and the same bounded naval-supply goods.
- [x] Add the securely dated Augustan frontier-camp pass: Castrum Mogontiacum is now a named Mainz special with the installed low non-propagating fort contract, a dedicated icon, and no reconstructed garrison roster.
- [x] Add three securely dated Campus Martius civic specials: Agrippa's Pantheum (c. 27 BC), Saepta Iulia (26 BC), and the Diribitorium (7 BC), with direct art and period-appropriate upkeep goods.
- [x] Add the Palatine Apollo complex as two bounded Rome specials: the 28 BC Temple of Apollo and the Greek-and-Latin library in use by about 23 BC, with direct art, separate contracts, and a scroll-collection goods proxy.
- [x] Add two Augustan civic-space specials: the Curia Iulia (29 BC) and Porticus Octaviae restoration (27–23 BC), with distinct government/cultural contracts and direct art that avoids later reconstruction claims.
- [x] Add two trade-and-water specials: the contested-named Porticus Aemilia Emporium warehouse and the partly reconstructed Aqua Alsietina, with period-appropriate demand for staple goods, containers, construction goods, and water infrastructure.
- [x] Add further Roman frontier infrastructure only where a specific AD 1 source and a locally verified building contract support it; keep the existing M7 castra/limes proxies conservative and do not backdate Castra Praetoria (AD 21-23). (Eleven source-led Augustan camp/supply anchors are active under the verified low-fort contract; no Castra Praetoria backdate.)
- [x] Catalogue and smoke-check 42 source-labelled AD 1 market/urban hubs; the installed pre-game market-manager seeds are deferred after a first-month runtime assertion, while every source-led urban and harbor anchor remains active (see `BLOCKERS.md` and `DECISIONS.md`).
- [x] Localize and anchor the plan-listed ancient raw goods on controlled AD 1 map locations (328 audited corrections).
- [x] Source-qualify the plan-listed alum emphasis at the direct installed Melos anchor; the existing alum value is retained.
- [x] Audit the plan-listed “Laurion fading” note as a documented non-anchor; no active AD 1 silver RGO is asserted.
- [x] Seed and smoke-check 42 source-labelled urban market settlements with engine-valid town setups.
- [x] Run the AD 1 observer foundation probe (map, observer mode, and ten days of market activity).
- [x] Seed and smoke-check 25 source-labelled ancient transport-corridor segments.
- [x] Seed and smoke-check the transparent city/town/road development profile.
- [x] Expand the specialist urban economy with source-led glassware, lacquerware, pottery, water, mint, library, and Pharos building anchors.
- [x] Add the source-backed Roma annona granary as an engine-valid city-scale public grain-store proxy.
- [x] Add the source-backed Han Taixue at Chang'an through the engine-valid Confucian-academy proxy.
- [x] Add five distinct, source-labelled ancient raw goods (papyrus, silphium, naphtha/bitumen, jade, and camels), their full UI-art/modifier contracts, and five audited RGO anchors.
- [x] Add plan-listed civic/infrastructure anchors for the Circus Maximus, Alexandria harbor, Dujiangyan, and Anuradhapura reservoirs.
- [x] Add the plan-listed Taxila market and urban node through its reviewed Attock proxy, reaching 40 market hubs.
- [x] Extend the road network with the Via Appia and Taxila–Mathura Uttarapatha legs (29 audited segments).
- [x] Extend the western Roman road corridor through the reviewed Massilia-to-Tarraco anchors (36 audited segments).
- [x] Add the source-qualified Via Flaminia eastern-branch proxy through the available Narni-Spoleto anchors (37 audited segments).
- [x] Extend the Via Aemilia through the reviewed Rimini-Piacenza corridor (41 audited segments).
- [x] Add a bounded Via Popilia regional corridor without substituting unavailable Adria or Altino (43 audited segments).
- [x] Model Muza's active commercial roadstead with a market-warehouse proxy, explicitly avoiding a false harbor tier.
- [x] Add the plan-required AD 1 Second Temple at Jerusalem and its guarded AD 70 building-destruction current.
- [x] Add a source-qualified Buddhist monastic proxy at Anuradhapura without applying a later Christian building identity.
- [x] Add a source-qualified Prima Porta villa proxy without claiming a latifundium census or slave-labor measure.
- [x] Add a source-qualified Roman-period Faiyum irrigation proxy at the direct installed hydraulic-agricultural location.
- [x] Add the Forum Romanum through the verified marketplace proxy without inventing a forum-specific building key or a reconstruction of its physical plan.
- [x] Complete the independent M5 market, urban, building, harbor, road, and development surface: 42 market/urban nodes, eight source-labelled harbor tiers, Muza's roadstead warehouse, the historic-building anchors, and 43 audited road segments are present.
- [x] Apply the 328 source-led RGO corrections through the locally proven runtime startup effect; register and locally seed all five custom goods.
- [x] Add 100 more new full buildings with their icons for Europe, North Africa and the Middle East. Not too many unique buildings. Don't be afraid to add new trade goods as well if needed as outputs/inputs for these buildings. Economy is core to this time period. (112 placements across 10 direct-art reusable antique production families; existing era goods provide the inputs.)

- [x] (Second Pass) Add 100 more new full buildings with their icons for Europe, North Africa and the Middle East. Not too many unique buildings. Don't be afraid to add new trade goods as well if needed as outputs/inputs for these buildings. Economy is core to this time period. (154 direct-art reusable antique production families now seed 1,804 regional AD 1 placements; existing era goods provide the calibrated inputs and outputs.)
- [x] Building audit : Currently it looks like a lof of the buildings are just adding local modifiers and consuming ressources but not producing any ressources. It's fine to have some of these, but like at least 50-80% of buildings should actually be producing stuff. (Validated: 1,912 placements total; 1,497 productive (78.3%) and 1,804 scalable (94.4%).)
		- Please audit every single building added by the mod and make sure the whole system is coherent with that logic. DO NOT BE AFRAID TO ADD NEW MANUFACTURED GOODS FOR THAT PERIOD.
		- Please make sure that 80% of buildings added are not "unique" buildings which can only be built once, or at max_level = 1. I want my buildings to scale for proper empire building as they do in the base game (and even more so)
		- Make a final pass to ensure everything is balanced and coherent
- [x] Verify ancient trade flows; run milestone gate and tag `M5-done`. Rapid AD 1 RGO/custom-good and positive-trade probes pass; the unsupported exact market assertion remains documented.

## M6 — Power

- [x] Establish a checked, sourced Rome/Han/Parthia core: historical reforms, dynasties, nine named characters, Gaius Caesar as Rome's heir, Wang Mang's regency, and the AD 1 Chang'an capital correction.
- [x] Add source-labelled core estate adapters, privileges, laws, and societal values for the Rome/Han/Parthia profiles through locally verified engine contracts.
- [x] Add the first Tier-1/2 secondary-ruler slice: eleven named AD 1 figures, seven country profiles, and source-labelled client, Kushite, steppe, Korean, and tribal-government adapters.
- [x] Add the AD 1 Herodian client tetrarchy: Archelaus in Judea, Antipas in Galilee-Peraea, and Philip in Batanea.
- [x] Add the next named Roman client rulers: Archelaus of Cappadocia, Antiochus III of Commagene, Rhoemetalces I of Thrace, and Dynamis of Bosporus.
- [x] Render date-less current `ruler_term` records for every implemented non-regency government and retain source-led Augustus/Western Han regnal back-history without scripting a pre-AD-1 accession date.
- [x] Add named Near Eastern courts for Emesa, Osroene, Media Atropatene, and contested AD 1 Armenia with qualified regional government adapters.
- [x] Add Pharasmanes I's contested AD 1 Caucasian Iberian court without inventing an intra-year accession date.
- [x] Add a bounded Second Temple priesthood adapter to Herodian Judea through verified estate and law contracts.
- [x] Add source-qualified AD 1 coinage standards for Augustan Rome and Western Han through verified socioeconomic-law contracts.
- [x] Make the Han Mandate of Heaven explicit through a verified legitimacy adapter while deferring its dated collapse cycle.
- [x] Verify Legion-estate feasibility and retain the plan's privilege-plus-M10-disaster fallback where the engine lacks a safe country-specific estate surface.
- [x] Add Bhatikabhaya Abhaya's Anuradhapura court with explicit source-qualified monastic and canal-patronage adapters.
- [x] Add a bounded Roman legal-status baseline using the locally verified slavery-law contract.
- [x] Add a bounded AD 1 Roman civic-cult law and defer later persecution/toleration changes to history content.
- [x] Add Yaudheya, Arjunayana, and Kuninda as source-qualified ganasangha republics without inventing individual rulers.
- [x] Add Attambelos II's source-qualified Characenian court with a contested coin-based reign record.
- [x] Add Nambed's source-qualified Persid court from a broad academic numismatic date range.
- [x] Add source-qualified Indo-Scythian and late Indo-Greek courts for the plan's Azes and Strato II starts.
- [x] Record and defer the South Arabian named-court gap rather than inventing AD 1 rulers for Saba, Himyar, or Qataban.
- [x] Add anonymous, source-qualified tribal government profiles for 19 northern Tier-1 polities where no AD 1 incumbent is defensible.
- [x] Add anonymous, source-qualified tribal government profiles for nine Brittonic and Irish Tier-1 polities where no AD 1 incumbent is defensible.
- [x] Add a bounded regional-kingship adapter and anonymous source-qualified Tarim Buyeo and eastern-confederacy profiles.
- [x] Add anonymous source-qualified Iranian Caucasian and South Arabian profiles while preserving named-court evidence blockers.
- [x] Add anonymous source-qualified Indian/African profiles with distinct Aksum chiefdom and Djenné-Djenno town-cluster adapters.
- [x] Give every 107 Tier-1/2 roster tag a source-qualified M6 government profile without fabricating unknown AD 1 rulers.
- [x] Add Pythodoris of Pontus as the source-qualified Colchian ruler without inventing biography or succession dates.
- [x] Add Daeso's traditionally dated Buyeo court while explicitly retaining the Northern/Eastern Buyeo continuity question as contested.
- [x] Add Aspurgus as a contested Bosporan court claimant without resolving the plan's Dynamis start anchor.
- [x] Run and record two evidence-based Han minority-regency runtime probes; defer the silent generated-ruler fallback in `BLOCKERS.md`.
- [x] Add Lucius Caesar and Germanicus to the source-led Julio-Claudian court without inventing an AD 1 office command or a second heir slot.
- [x] Add Agrippa Postumus, Julia the Younger, and Agrippina the Elder as bounded Augustan household figures without importing later adoptions, marriages, or careers.
- [x] Add Ptolemy of Mauretania to Juba II and Cleopatra Selene's court without projecting his later succession into an AD 1 heir appointment.
- [x] Driver-test the Parthian profile: Phraates V, Ctesiphon, nine subjects, one reform, and fifteen laws rendered in the AD 1 Country panel.
- [x] Correct the Han Wang-clan dynasty labels and add the bounded Wang Shun court record from the *Book of Han* source route.
- [x] Add the Rome-hosted Arsacid prince Vonones without anticipating his later Parthian or Armenian reigns.
- [x] Add Vonones's three Rome-hosted Arsacid brothers without fabricating offices or succession claims.
- [x] Add Kong Guang as a bounded senior Han court figure without turning a source office into an unsupported engine role.
- [x] Add the named Han regency-circle officials Zhen Feng, Zhen Han, Ping Yan, and Liu Xin as court-only records.
- [x] Replace Atrebates' anonymous government ruler with coin-attested Tincomarus, without projecting later British succession.
- [x] Add Salome I to the Herodian Judean court without converting her settlement holdings into a separate state.
- [x] Extend the directly attested Han regency circle with Wang Yi, Sun Jian, Zhen Xun, Liu Fen, Cui Fa, and Chen Chong without synthesizing offices or genealogies.
- [x] Add a bounded, source-qualified druidic-authority privilege to the eight pre-conquest Brittonic polity profiles without asserting a pan-British constitution.
- [x] Driver-test the Roman government panel: ROM renders Roma, one reform, nineteen laws, and all five Roman estate adapters, including Equestrian Service and Priestly Colleges.
- [x] Add five contested, accession-credited Han court figures without translating titles, residence, kinship, or later offices into start-state mechanics.
- [x] Add Artaxias III and Polemo II as bounded Pythodorid family-court figures without projecting later Armenian or Pontic reigns into AD 1.
- [x] Add Emperor Ping's named maternal Wei family and Wang Yu's named early Yuan Shi circle without inferring offices, careers, or future punishments.
- [x] Add the coin-attested Nabataean Queen Huldu as Aretas IV's documented AD 1 consort without inventing a constitutional role or genealogy.
- [x] Complete the evidence-bounded Tier-1/2 power foundation: all 107 government profiles, 250 source-led characters, 32 named active heads, 75 explicitly anonymous/collective profiles, 24 privilege adapters, and campaign-valid regnal histories. The generated M6 coverage report preserves the source boundary rather than inventing rulers.
- [x] Bind Wang Mang through the installed start-time `set_regent` contract; the fresh AD 1 Western Han selector and player start retain the named regent. Run the milestone gate and tag `M6-done`.

## M7 — War

- [x] Implement ancient units, levies/regulars, mercenaries, forts/limes, and navies; remove gunpowder/oceanic units.
- [x] Recheck all Roman, Parthian and germanic units, make sure there's enough diversity (the generated M7 audit requires six Roman, four Arsacid, and four Marcomannic roles to be both country-available and seeded at AD 1).
- [x] Recheck all mercenaries (the generated M7 audit requires twelve companies across foot-skirmisher, heavy-foot, and mounted profiles).


## M8 — Knowledge

- [x] Generate and validate the required birth-location static-modifier contract for all nine custom institutions.
- [x] Implement five complete age trees, roughly 250 advances, institutions, tech tiers, objectives, and abilities.
- [x] Restore a fresh paused AD 1 observer start with zero removed-law and invalid-estate diagnostics. Removing the inherited vanilla setup templates reduced the archived 213 removed laws plus 227 invalid estate privileges to zero in the fresh driver-observer run; evidence: `docs/playtests/AD1_STARTUP_DEFAULTS_20260721.md`.
- [x] Test AI research and anachronism/dead-end rules; run milestone gate and tag `M8-done`. (The enabled AD 1 selector, generated 250-advance no-dead-end contract, and zero-new-line menu smoke are recorded; `M8-done` remains accepted under the rapid-test policy.)

## M9 — Nations among nations

- [x] Implement CBs, wargoals, treaties, subjects, IOs, and known-world sets.
  - [x] Add the generated AD 1 client-kingdom, satrapy, tributary, foederati,
        and autonomous-city contracts; map the sourced Roman, Arsacid, and Han
        dependency web onto the first three.
  - [x] Add the plan's punitive, client-king, tribute, frontier, raid,
        succession, late-religious, and dormant historical-unification CBs;
        their wargoals and three subject-imposition peace terms.
  - [x] Add the plan's Han, Xiongnu, Games, and Church IO surfaces plus
        validated discovery profiles for every AD 1 polity.
- [x] Inspect paused live diplomacy/country panels for Rome, Western Han, and Parthia; retain screenshots and the country/tag/capital/subject evidence in `docs/playtests/M9_DIPLOMACY.md`.
- [x] Verify the ancient diplomatic webs, pass `make full`, and tag `M9-done` (22 July 2026; 11 Roman clients, 9 Arsacid satrapies, and 5 Han tributaries match the reviewed AD 1 ledger).

## M10 — History in motion

- [x] Implement all timeline situations/disasters/formables/tag changes in five century batches.
  - [x] Normalize the plan's complete history spine into the validated
        `docs/timeline.csv` ledger, including its disaster calendar and
        silphium window.
  - [x] Render and menu-smoke the AD 1-96 current layer: 14 situations, two
        disasters, nine date-driven events, and the first formation/tag-switch
        event surfaces.
  - [x] Apply the locally verified in-place transformation adapter to Kushan
        formation and the Southern-Xiongnu outcome, with generated temporary
        colors, CoAs, and localization.
  - [x] Add a source-led Northern-Xiongnu polity release to complete the AD 48
        split after its dynamic-country setup contract is locally verified.
    - [x] Render, source-check, and menu-smoke the AD 97-199 history batch:
          19 currents, including the AD 100 dynamic Moche release from the
          reviewed Gallinazo local proxy and the AD 192 Champa release from the
          reviewed Han-Rinan local mesh.
  - [x] Render, source-check, and menu-smoke the AD 200-299 history batch:
        10 currents, including citizenship, Sassanid, and Dominate transition
        adapters and source-qualified Germanic formation identities.
  - [x] Render, source-check, and menu-smoke the AD 300-399 history batch:
        14 currents, including Christianization, Hunnic arrival, and the
        source-qualified East-West Roman transition ledger.
  - [x] Render, source-check, and menu-smoke the AD 400-476 finale batch:
        13 currents, including Visigothic/Vandal successor proxies and the
        source-qualified terminal Odoacer identity transition.
- [x] Smoke and observer-test every batch; run milestone gate and tag `M10-done`. (All five batches are statically date/symbol/localization checked and menu-smoked; the revised policy accepts rapid subsystem probes rather than a 476-year observer run.)

## M11 — Flavor & face

- [x] Generate, dimension-check, round-trip review, and smoke-test the first AD 1 Rome loading-screen master and DDS override.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the first M10 event illustration for AD 1 *Immensum Bellum*.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 1-4 Gaius Caesar eastern-settlement event illustration.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 9 Xin Dynasty Crisis event illustration.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 14 Augustan Succession event illustration.
- [x] Generate, chroma-key review, dimension-check, round-trip review, and smoke-test the native pepper-good icon and illustration overrides.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 6-9 Illyrian Revolt event illustration.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 9 Teutoburg Forest event illustration.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 30 Kushan Unification event illustration.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 17 Tacfarinas' War event illustration.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 21 Florus and Sacrovir revolt event illustration.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 30 Christianity-founded event illustration through a respectful landscape-only treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 40 Trung Sisters' Revolt event illustration through a landscape-only Jiaozhi treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 40 Mauretania Annexation event illustration through a non-literal coastal landscape treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 43 Claudian Invasion of Britain event illustration through a landscape-only Channel-coast treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 48 Xiongnu Split event illustration through a non-literal eastern-steppe fragmentation-context treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 54 Silphium Extinction event illustration through a non-botanical Cyrenaican ecological-context treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 58 Rome-Parthia War over Armenia event illustration through a non-literal late-autumn Armenian frontier-context treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 60 Boudica's Revolt event illustration through a landscape-only eastern-Britain treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 64 Great Fire of Rome event illustration through a restrained non-literal urban context treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 65 Buddhism at the Han Court event illustration through a non-literal Eastern Han scholarly-courtyard context treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 66 Tiridates' Coronation event illustration through a non-literal Armenian highland diplomacy-context treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 66 Great Jewish Revolt event illustration through a landscape-only Judean environmental-context treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 69 Batavian Revolt event illustration through a non-literal Lower Rhine wetland-context treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 68 Year of the Four Emperors event illustration through a non-literal rain-wet Roman civic-context treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 79 Vesuvius event illustration through a non-literal Campanian volcanic-landscape treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 70 Second Temple transformation event illustration through a landscape-only Judean environmental-context treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 83 Mons Graupius event illustration through a landscape-only Caledonian upland-context treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 85 Dacian Wars event illustration through a non-literal Carpathian foothill-context treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 89 Han-Xianbei War event illustration through a landscape-only northern grassland-context treatment.
- [x] Complete the reviewed illustration mapping across all 28 generated M10 first-century currents.
- [x] Extend the generated second-century event-art contract and smoke-test the AD 97 Gan Ying's Mission illustration through a non-literal Persian Gulf coastal-context treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 101 Trajan's Dacian Wars event illustration through a non-literal Danube-Carpathian river-context treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 105 paper-standardization event illustration through a non-literal Eastern Han scholarly-material treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 113 Trajan's Parthian War event illustration through a non-literal Mesopotamian river-plain treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 115 Antioch earthquake event illustration through a landscape-only Orontes-valley treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 122 Hadrian's Wall event illustration through a landscape-only northern-British upland treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 127 Kanishka-apogee event illustration through a landscape-only Central-Asian highland treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 132 Bar Kokhba revolt event illustration through a landscape-only Judean limestone treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 142 Antonine Wall event illustration through a landscape-only northern-British moorland treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 142 Celestial Masters event illustration through a landscape-only inland-Chinese woodland treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 160 Gothic Migration event illustration through a landscape-only northern-Pontic steppe treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 161 Verus' Parthian War event illustration through a landscape-only Mesopotamian river-margin treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 165 Antonine Plague event illustration through a landscape-only Mediterranean upland treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 166 Daqin Embassy event illustration through a landscape-only South-China-Sea coastal treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 166-180 Marcomannic Wars event illustration through a landscape-only Danubian floodplain treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 184 Yellow Turbans event illustration through a landscape-only North China Plain treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 192 Champa formation event illustration through a landscape-only tropical central-Vietnam treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 100 Moche-emergence event illustration through a bounded north-coast Peruvian river-valley treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 193 Severan Settlement event illustration through a landscape-only central-Italian lowland treatment.
- [x] Extend the generated third-century event-art contract and smoke-test the AD 208-211 Severus in Caledonia illustration through a landscape-only northern-Caledonian treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 212 Constitutio Antoniniana illustration through a generic Roman civic-context treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 213 Alemanni formation illustration through a landscape-only Upper-Rhine treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 220 Three Kingdoms illustration through a landscape-only north-Chinese river-valley treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 224 Sassanid Revolution illustration through a landscape-only Fars highland treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 235 Crisis of the Third Century illustration through a landscape-only central-Italian foothill treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 240 Manichaeism illustration through a landscape-only western-Iranian river-margin treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 250 Frankish formation illustration through a landscape-only Lower-Rhine floodplain treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 284 Diocletian and the Dominate illustration through a landscape-only central-Balkan upland treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 291 War of the Eight Princes illustration through a landscape-only north-Chinese loess-valley treatment.
- [x] Complete reviewed illustration mapping across all ten generated M10 third-century currents and enforce it in the renderer.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 301 Armenian Conversion illustration through a landscape-only Armenian-highland treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 306 Constantine's Civil Wars illustration through a landscape-only central-Italian foothill treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 325 Council of Nicaea illustration through a landscape-only Bithynian lakeshore treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 337 Shapur II and Julian illustration through a landscape-only upper-Mesopotamian river-valley treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 350 Aksum and Meroë illustration through a landscape-only middle-Nile river-margin treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 365 Crete earthquake and tsunami illustration through a landscape-only southern-Cretan coastal treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 370 Hunnic Arrival illustration through a landscape-only Volga-steppe treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 376–382 Gothic Refugee Crisis illustration through a landscape-only lower-Danube riparian treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 380 Edict of Thessalonica illustration through a landscape-only northern-Aegean coastal treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 383–440 Fei River and Northern Wei illustration through a landscape-only inland north-Chinese river-plain treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 391–413 Gwanggaeto the Great illustration through a landscape-only Korean upland river-valley treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 393 Olympic Games Sunset illustration through a landscape-only western-Peloponnese river-valley treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 394–395 East-West Roman Division illustration through a landscape-only central-Balkan river-and-foothill treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 399–413 Faxian and Gupta Apogee illustration through a landscape-only northern-Indian river-plain treatment.
- [x] Complete reviewed illustration mapping across all fourteen generated M10 fourth-century currents and enforce it in the renderer.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 405–406 Crossing of the Rhine illustration through a landscape-only lower-Rhine floodplain treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 407–410 Britain Abandoned illustration through a landscape-only south-British Channel-coast treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 410 Sack of Rome illustration through a landscape-only central-Italian treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 418 Visigothic Settlement illustration through a landscape-only southwestern-Gaul river-plain treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 429–439 Vandal Conquest of Africa illustration through a landscape-only North-African littoral treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 434–453 Attila illustration through a landscape-only Pannonian grassland treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 440–460 Hephthalites illustration through a landscape-only Inner-Asian foothill river treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 447 Constantinople Earthquake illustration through a landscape-only Marmara-coast treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 449 Adventus Saxonum illustration through a landscape-only eastern-British coastal-wetland treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 451 Chalcedon and Avarayr illustration through a landscape-only Armenian-highland valley treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 455 Vandal Sack of Rome illustration through a landscape-only lower-Tiber floodplain treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 468 Cape Bon illustration through a landscape-only northeastern-Tunisian coast treatment.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the AD 476 finale illustration through a landscape-only northern-Italian lowland treatment.
- [x] Enforce complete reviewed illustration coverage for all 13 final-century generated currents.
- [x] Render and review the maintained M11 event-art contact sheet (84 retained 1080x440 masters).
- [x] Replace all 157 AD 1 solid-colour CoA placeholders with validated, explicitly non-reconstructed standards; retain direct Rome, Han, and Parthia reviews above the regional catalog.
- [x] Remove the obsolete M2 no-op age-scaffold definitions and their mirrored localization after M8's complete advance tree superseded them.
- [x] Add the source-keyed concept glossary and project credits, including Pleiades attribution in game-visible metadata.
- [x] Replace the five active age-view illustrations with reviewed, non-reconstructive 1080x440 DDS panels and retain their source/master chain.
- [x] Replace the five M8 age-group icon surfaces used by all 250 advances; validate the source/master/DDS chain and the 50-per-group bindings.
- [x] Establish and smoke-check the direct M8 advance-icon migration, beginning with Imperial Cult; completion remains open until every advance has its dedicated checked asset.
- [x] Reach the section 18 event target with 416 sourced-window events using 84 reviewed shared paintings without inventing historical incidents.
- [x] Replace the 14 scripted-formation and successor-state solid-color CoAs with reviewed non-reconstructive standards and generation checks.
- [x] Replace the `_default` fallbacks on every direct-key M4 religion and M8 institution screen surface with checked, source/master/DDS contracts.
- [x] Complete the plan-permitted shared-icon fallback coverage: five reviewed advance icons cover all 250 advances, and 84 reviewed paintings cover all 416 historical-current events.
- [x] Complete the English-first localization audit: fifteen source files mirror exactly across all ten supported clients, with no game-visible stub text.
- [x] Reach the decision target with 40 source-led own-country actions, exact action-message localization, and bounded player-only effects.
- [x] Resolve the M11 generic-action message-registry blocker through a one-action exact-name pilot and a pinned full 40-action overlay; the source ledger is retained in `docs/m11/decisions.csv`.
- [x] Remove common-screen placeholders; run milestone gate and tag `M11-done`.


## M12 — Aesthetic and flavor polish

- [x] Recheck player-facing tooltips/tutorials: all four installed tutorials are non-automatic, 33 dated/dynastic hints remain disabled through exact-name guards, and the authored-text audit has zero prohibited post-476 terms across every mirrored client.
- [x] Audit safe period-facing UI surfaces: retain the validated direct ancient art on 559 content-facing chains (advances, buildings, privileges, faiths, institutions, CoAs, ages, and events); do not replace the shared core window-frame templates without a locally verified skin contract.
- [X] Replace the universal county fallback with checked country ranks: Rome, Han, and Parthia render as empires; sovereign/client courts as kingdoms; collective societies as tribes; and the republican examples retain republic titles.
- [x] Make sure all loading screens and loading screen quotes are period appropriate, add some diversity
- [x] Rebuild the direct main-menu background and title surfaces as ANTIQVITAS art while retaining the verified shared frame contract.

## M13 — Ship

- [x] Complete the static pacing/growth/inflation and AI-weight audit; restore bounded local-contract priorities to the seven active M9 CBs.
- [x] Quarantine all 7,440 installed vanilla event definitions in 347 files through a source-preserving, date-gated overlay that retains the loader's scheduler/scope/effect graph.
- [x] Guard the five absent-IO and eight dated country-startup branches in the installed hardcoded on-game-start handler through a checked exact-name overlay; fresh AD 1 observer initialization has zero former hardcoded runtime errors.
- [x] Guard four optional-government and three HRE special-status CoA predicates through a checked exact-name overlay; fresh AD 1 observer initialization has zero former CoA scope errors.
- [x] Guard the installed Catalan Sitges-capital flag predicate through a checked exact-name overlay; a fresh AD 1 observer initialization has zero script-system errors.
- [x] Finish README, known issues, packaging notes, static finale verification, and the full surface-area inventory audit.
- [x] Disable the eleven installed anachronistic generic mission packs through checked exact-name visibility overlays; retain their keys for engine references.
- [x] Pin a static player-facing anachronism audit across all 17 English localization files, with the client-language mirror contract checked separately.
- [x] Resolve the observer country-change rule through a menu-smoked, exact-name installed-file overlay; the driver can now enter Observer without altering any historical or AI rule.
- [x] Complete the M12 tutorial/hint audit: retain evidence-safe generic surfaces and disable 33 dated/dynastic vanilla hints through a menu-smoked, verified exact-name contract.
- [x] Eliminate every fresh AD 1 culture/religion no-pop diagnostic without weakening the accepted baseline. The additive one-person compatibility ledger is engine-proven, population-offset, and rapid-probe clean.
- [x] Run and record the final static/menu `make full` gate (rerun 2026-07-21:
      all checks pass and the enabled-mod smoke has zero new lines).
- [x] Run the current full gate and record its report: `make full` is green at 350 cultures, 37 religions, 416 historical-current events, and the 230,000.000-thousand population target, with zero new smoke lines.
- [x] Run the checkpointed autonomous observer game to 476 with decade screenshots and live log watch. (Superseded by the revised rapid-test acceptance policy: a full observer is optional evidence, not a ship gate.)
