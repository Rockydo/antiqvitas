# Progress

## 2026-07-19 — M4 global-population foundation

- Generated one culture-and-faith-checked base pop at each of the 13,552
  controlled locations. The resulting AD 1 setup totals exactly 230,000
  thousand people: Rome 47,500, Han 57,671, Parthia 9,000, India 40,000, and
  every other section 12.4 macro sits within its prescribed range.
- The generator scales the installed game's population density only as a
  geographic weighting template; targets and regional allocations remain
  source-labelled CSV inputs. `popcheck` independently tokenizes the generated
  script and validates every location's ownership, culture, faith, macro, and
  total instead of trusting the generator's calculation.
- `make validate`, standard `make smoke`, and explicit normal plus
  `-leavepops` menu launches all passed with zero new `error.log` line types.

Next: replace the current broad regional culture scaffold with the location
remap/dynamic-name layer, while retaining this checked population ledger.

## 2026-07-19 — M4 country-profile binding

- Replaced all temporary vanilla culture/religion country-definition references
  with M4's source-labelled profiles. The catalogue supplies 34 regional bases
  for all 157 active polities and 45 reviewed tag-level overrides for states
  whose profile is materially clearer than its regional scaffold.
- The generator now validates complete regional coverage, roster-tag validity,
  and M4 culture/religion symbols before it writes anything. Existing M3 map
  colors and placeholder flags remain deliberately separate from the historical
  profile data.
- `make validate` and a real menu `make smoke` both passed, with zero new
  `error.log` line types. The smoke detector now uses a 30-second minimum plus
  15 seconds of debug-log quiescence, which completed successfully in the
  constrained automation slice.

Next: allocate source-labelled AD 1 population totals through the ownership
ledger, then verify the raw and adjusted setup with the required `-leavepops`
and ordinary runs.

## 2026-07-19 — M3 American SoP coverage

- Added the explicitly required Plains/Coastal and Pacific Coast SoP families,
  then conservative Mesoamerican, Andean, northern-Andean, and North American
  frames for the named roster entities. The resolver rejected the Pacific Coast
  broad area because it has no vanilla-ownable locations; its direct geographic
  anchor is retained without inventing a territory row.
- The live M3 setup now contains 138 polities, 8,442 resolved locations, and
  25 dependencies. Empty and late-settlement lands remain outside ownership
  expansion and are reserved for M4's zero-pop audit.
- `make validate` and a real-game smoke are green with zero new error lines.

Next: implement checked residual coverage for still-unassigned ownable land,
assigning it only to an explicit documented SoP or recording it as intentionally
empty; then render a new AD 1 political-map evidence capture.

## 2026-07-19 — M3 African SoP coverage

- Added the design-bible's West African iron-age, Bantu-expansion, and
  Barbaria/Horn SoP families as explicit roster entities rather than assigning
  their areas to nearby settled states. The African pass also adds conservative
  Mauretanian, Garamantian, Blemmyan, and Aksumite regional frames.
- The active political-map roster is now 136 polities with 8,084 resolved
  locations and 25 dependencies. The collision-safe tag generator now retains
  committed allocations when new roster rows are inserted.
- `make validate` and a real-game smoke are green with zero new error lines.

Next: give the Americas their equivalent explicitly named SoP coverage, then
introduce checked residual coverage for remaining broad regions without turning
empty late-settlement lands into period states.

## 2026-07-19 — M3 Han-world territorial pass

- Added reviewed regional frames for Cappadocia/Commagene, Media Atropatene,
  Persis, Sakastan, Khwarazm, Wusun, the Korean roster, Buyeo/Wuhuan, and the
  AD 1 Xiongnu/Xianbei/Dingling steppe groups. Areas that contain rival capital
  anchors were left untouched instead of assigning an artificial single owner.
- The source tables now resolve 7,522 locations for 133 active roster polities
  and 25 dependencies. The entire addition is marked `contested` where local
  map geometry cannot express a historical frontier precisely.
- `make validate` and a real-game smoke are green with zero new error lines.

Next: cover the remaining documented African and American SoP/state frames,
then introduce a checked residual-coverage ledger for the genuinely broad SoP
regions that cannot be honestly partitioned by a modern map-area boundary.

## 2026-07-19 — M3 Barbaricum territorial pass

- Added source-labelled frames for the Caledonian and Hibernian SoPs, selected
  British polities, Marcomannic Bohemia, named Germanic groups, Scandinavia,
  the Venedi, Danubian groups, Armenia/Caucasus, and the Pontic Sarmatian
  frontier. The exact-capital and no-overlap guards remain in force.
- The reviewed setup now resolves 6,811 locations for all 133 roster polities,
  with all coarse geography rows marked `contested` rather than being presented
  as final ancient borders.
- `make validate` and a real-game smoke are green with zero new error lines.

Next: extend source-conservative regional coverage across the Middle East,
Central Asia, East Asia, Africa, and the Americas; then audit all remaining
unassigned ownable map locations as either a sourced SoP frame or a documented
intentional empty land.

## 2026-07-19 — M3 Indian Ocean territorial pass

- Expanded only source-labelled, coarse local geography frames for the AD 1
  Indian and Southeast Asian roster: Indo-Scythian north-west, Satavahana
  Deccan, Kalinga, Chera, Anuradhapura, Jiaozhi, and the named Pyu, Mon,
  Khmer, Malay, Javanese, Philippine, and Bornean society frames.
- The ownership resolver now produces 5,575 non-overlapping locations for all
  133 roster polities and retains 25 source-recorded dependencies.
- `make validate` and a real-game smoke are green with zero new error lines.

Next: make the same source-conservative territorial pass through Barbaricum,
the steppe, Africa, and the Americas; do not use a local-map area as an
unlabelled substitute for a period border.

## 2026-07-19 — M3 full capital-anchor coverage

- Completed the collision-checked local-map anchor registry for all 133 AD 1
  roster polities. The setup generator now creates an active country and an
  explicit capital-control seed for each; the ownership resolver produces
  4,230 non-overlapping locations and 25 source-recorded dependencies.
- Added transparent regional-anchor assumptions for non-state societies and
  places without a one-to-one EU5 local key. They are map geometry adapters,
  not assertions of a formal ancient capital or final territorial extent.
- `make validate` and a real-game smoke are green with zero new error lines.
  The foreground-guarded driver also captured a clean mod-menu checkpoint.

Next: replace one-location anchors with researched territorial extents and SoP
coverage, beginning with the regions still outside the Roman, Parthian, and Han
core frames.

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

## 2026-07-19 - M3 global territory coverage and runtime boundary

- Completed the global political surface: 157 sourced AD 1 polities own or
  control 13,552 locations. The coverage audit accounts for all 13,576
  installed ownable locations as 13,535 assigned plus 41 deliberately empty
  post-period/remote locations; the 25 sourced dependencies remain intact.
- The residual-coverage ledger only fills still-unclaimed ownable locations and
  runs after named territorial rows, preserving the resolver's no-overlap rule.
  All broad SoP frames remain explicitly contested historical proxies.
- A real AD 1 selector showed the world political map at `08:00, 1 January, 1`;
  the driver enabled observer mode, started an actual observer game, and
  advanced it through its first month. The captures are retained in
  `docs/screens/M3_global_coverage/`.
- `make full` is green at the menu. The observer log exposed calls from
  untouched vanilla market/building, government/law, formable, and HRE systems;
  the failed milestone gate and bounded remediation attempts are recorded in
  `BLOCKERS.md`. M3 remains untagged rather than accepting those new lines.

Next: start M4's sourced people-and-faith data while the M3 runtime dependency
waits for its owning M5/M6/M9 replacement work.

## 2026-07-19 - M4 culture and religion foundation

- Added machine-checked, source-labelled catalogues for 69 ancient-culture and
  37 religion definitions, 34 regional population profiles, unique map colors,
  and English-mirrored localization. The definitions load additively and retain
  contested regional frames as documented scaffolding rather than settled fact.
- The local smoke exposed that culture records need graphical tags, unique named
  colors, and a nested dialect rather than a language root; religions need a
  real modifier; and culture/religion localization keys share one namespace.
  The generator now enforces the first three engine constraints and has a
  clean menu smoke with zero new errors.
- The language catalogue remains data-only until the dialect/namelist pass can
  provide source-based engine-valid dialect keys. No M3 country profile or pop
  has been silently switched to the new cultural scaffolding.

Next: generate the verified dialect and namelist layer, extend the source
profiles to country/pop coverage, and only then render the M4 global pop pass.

## 2026-07-19 - M4 ancient dialect and namelist layer

- Added 27 source-labelled language roots and dialects, with male, female, and
  dynasty pools rendered through namespaced localization keys. All 69 M4
  culture definitions now use those engine-valid dialects rather than a root
  language key.
- A bounded game probe established that the language-family registry is fixed
  and that every name-list item must be localized. The generator enforces both
  rules, and the repaired result passes `make validate` plus a clean real-game
  smoke with zero new lines.

Next: bind sourced profiles to every active country and render populations from
the territorial ownership ledger against the section 12.4 targets.
