# Progress

## 2026-07-19 — M6 Herodian client tetrarchy

- Added Herod Archelaus, Herod Antipas, and Philip the Tetrarch to a shared
  Herodian dynasty and installed them in Judea/Samaria, Galilee-Peraea, and
  Batanea respectively. Each uses the checked Roman client-monarchy adapter;
  their distinct historical titles remain in source notes rather than being
  collapsed into a new, unverified engine type.
- `make validate` is green with 13 dynasties, 23 characters, and 13 government
  profiles. The enabled-mod `make smoke` reached a rendered menu with zero new
  error-log lines.

Next: continue the named Roman client-ruler and Tier-1/2 roster coverage while
leaving Judean priestly mechanics for their own sourced M6 pass.

## 2026-07-19 — M6 secondary AD 1 rulers and government forms

- Added eleven named secondary AD 1 people and nine explicitly qualified
  dynastic labels: Maroboduus, Arminius, Juba II, Cleopatra Selene II, Aretas
  IV, Natakamani, Amanitore, Wuzhuliu Chanyu, Yuri, Tasciovanus, and
  Cunobelinus.
- Mauretania and Nabataea now use client-monarchy adapters; Kush has named
  Natakamani-Amanitore co-rule; Xiongnu uses the installed steppe-horde type;
  Goguryeo has an early kingdom adapter; and Marcomanni/Catuvellauni use the
  installed tribal type. The scoped source and uncertainty record is in the
  [secondary roster note](m6/SECONDARY_AD1_ROSTER.md).
- `make validate` is green with 12 dynasties, 20 characters, 10 governments,
  10 privileges, and 9 laws. The enabled-mod `make smoke` also reached a
  rendered menu with zero new `error.log` lines.

Next: continue the Tier-1/2 ruler and government coverage rather than treating
this focused secondary roster as the complete M6 character pass.

## 2026-07-19 — M6 core political mechanics

- Extended the checked M6 power ledger with five source-labelled estate
  privileges, four laws, and distinct societal-value positions for Rome,
  Western Han, and Parthia. The generator now validates every referenced local
  estate, modifier, law option, and country-start assignment before it renders
  the exact installed script contracts and full localization mirrors.
- Rome now begins with its senatorial/annona/military adapters and civic-status
  and professional-legion laws; Western Han with a palace-bureau adapter and
  commandery administration; Parthia with great-house autonomy and compact.
  The documented technical and historical limits are in
  [M6 core foundation](m6/CORE_FOUNDATION.md).
- `make validate` and the enabled-mod `make smoke` are green. The smoke test
  reached the rendered menu and reported zero new `error.log` lines versus the
  accepted baseline.

Next: extend the same checked data model to the remaining Tier-1/2 rulers and
government forms, while retaining the targeted inspector-driver gap as open.

## 2026-07-19 — M6 core power foundation

- Added a checked data-to-script pipeline for three core historical government
  profiles, three dynasties, and nine named AD 1 characters. Rome now has the
  Principate reform with Augustus, Livia, and Gaius Caesar as explicit heir;
  Tiberius is deliberately not an heir. Western Han has Emperor Ping and Wang
  Mang's dated regency; Parthia has Phraates V and Musa. The source and
  chronology ledger is [M6 core foundation](m6/CORE_FOUNDATION.md).
- The character-date gateway now allows constrained signed B.C.E. biography
  dates only in `birth_date`/`death_date`; campaign time remains constrained to
  AD 1–476. The build uses the locally verified five government types as
  technical adapters, with new historical reforms rather than invented types.
- Corrected Western Han's AD 1 capital from Luoyang to Chang'an through the
  existing Jingzhao/Xi'an anchor; the rebuilt geographical review is 4.4 px
  from the sourced coordinate and the dynamic-name layer now has 62 anchors.
- `make validate` and the enabled-mod `make smoke` are green with zero new
  menu-log lines. An observer game reached `08:00, 1 January, 1`; the detailed
  partial runtime record is [M6 core playtest](playtests/M6_CORE_FOUNDATION.md).

Next: extend the M6 ledger across the remaining Tier-1/2 governments and
rosters while the country-inspector driver coverage issue remains recorded.

## 2026-07-19 — M5 Han Taixue anchor

- Added the Taixue at Chang'an through the engine-valid `confucian_academy`
  proxy. The careful source-led placement distinguishes Han's capital
  institution from later academy/examination systems. The ledger now has 17
  specialist buildings; rationale and source are in `docs/m5/M5_TAIXUE.md`.
- `make validate` is green, reporting the 17-building ledger, and real
  enabled-mod `make smoke` is green with zero new error-log lines.

Next: continue source-led M5 infrastructure anchors while M5's RGO runtime
surface remains deferred.

## 2026-07-19 — M5 Roma annona granary

- Added a sourced `granary` anchor at Roma as the engine-valid city-scale proxy
  for Augustan public grain storage and distribution. The special-building
  ledger now contains 16 entries, with the scholarly rationale in
  `docs/m5/M5_ANNONA_GRANARY.md` and the historical modelling assumption in
  `ASSUMPTIONS.md`.
- `make validate` is green and reports the 16-building ledger; the enabled-mod
  `make smoke` is green with zero new `error.log` lines.

Next: continue the remaining independent M5 infrastructure while the
runtime-effective RGO discovery remains deferred.

## 2026-07-19 — M5 trade-flow export probe and RGO boundary

- A live observer run reached late May AD 1. Build-provided console exports
  show established market capacity and real pepper transfers: Attock imported
  11.63 pepper while the Malabar producers remained surplus. The same exports
  show silk and incense production at their expected eastern/southern sources,
  but no westward/northward transfer at this early point.
- The probe also found Roma locally surplus in wheat, contrary to the required
  annona pattern. A source-led clay substitution in the generated location
  template, followed by a fresh observer export, did not alter Roma's wheat
  production. A second fresh-start test using the locally observed
  `replace_path` metadata array was likewise ineffective, although its menu
  smoke stayed green.
- The experiment was restored to the prior green tree. M5 is not claimed as
  complete; its exact runtime limitation, evidence, and recovery route are in
  `docs/playtests/M5_TRADE_FLOW.md`, `BLOCKERS.md`, and `KNOWN_ISSUES.md`.

Next: take the highest-priority unblocked M6 power-system foundation task while
keeping the M5 RGO/trade gate open.

## 2026-07-19 — M5 Via Appia and Uttarapatha expansion

- Added four checked road segments: the Via Appia from Rome through the
  available Benevento, Taranto, and Brindisi proxies, plus a high-level
  Attock/Taxila–Mathura Uttarapatha connection. The M5 road manager now has 29
  source-labelled segments.
- `make validate` and an enabled-playset `make smoke` are green with zero new
  error-log lines.

Next: continue the remaining M5 economy anchors and begin the focused
trade-flow verification rather than treating this sparse network as a survey.

## 2026-07-19 — M5 Taxila market correction

- Added the plan-listed Taxila market and city node at the pre-existing
  coordinate-reviewed Attock proxy in the Indo-Scythian polity. This removes a
  specific omission from the market list and raises the generated M5 manager to
  40 markets and 40 urban nodes.
- `make validate` and a real enabled-playset `make smoke` are green with zero
  new error-log lines.

Next: continue the named ancient transport corridors and remaining economy
anchors before assessing the M5 trade-flow gate.

## 2026-07-19 — M5 civic and hydraulic infrastructure anchors

- Expanded the checked source ledger from 11 to 15 AD 1 specialist buildings:
  a Circus Maximus proxy at Rome, Alexandria's maritime-emporium harbor,
  Dujiangyan irrigation at Chengdu, and the Abhayawewa reservoir complex at
  Anuradhapura.
- Used only locally verified building keys and the existing owner/urban-site
  validation. `make validate` reports all 15 entries; the real menu smoke is
  green with zero new error-log lines.

Next: continue the remaining M5 building, road, development, and dated-goods
work before the trade-flow milestone gate.

## 2026-07-19 — M5 dedicated ancient raw goods

- Added five real raw-goods definitions instead of mislabelling vanilla goods:
  papyrus (Alexandria), silphium (Barca/Cyrenaica proxy), naphtha and bitumen
  (Hit), jade (Khotan), and camels (Medina). The checked RGO pass now records
  326 corrections.
- Generated the complete locally verified engine contract for each good: eight
  modifier types, neutral vanilla fallback modifier icons, name/description
  localization in all supported client files, unique RGB goods colors, and
  both 128x128 item icons and 1080x440 illustrations. The generated DDS layer
  includes full mip chains, including the non-power-of-two illustration size.
- `make validate` and a real `make smoke` are green with zero new lines. An
  enabled-playset observer session reached `11:00, 3 January, 1`; the runtime
  log had no custom-good, texture, or modifier match. Evidence is in
  `docs/playtests/M5_CUSTOM_GOODS.md`.

Next: expand the remaining dated/gated goods and production anchors, then run
the longer M5 trade-flow gate.

## 2026-07-19 — M5 specialist buildings and production anchors

- Expanded the M5 ledgers to 39 source-labelled markets and urban nodes. Sidon,
  Cologne, and Chengdu now supply period-appropriate specialist trade anchors
  alongside the original hub set.
- Added a checked `special_buildings.csv` generator layer that resolves each
  installation's exact AD 1 owner tag and refuses an unknown building, map key,
  uncontrolled site, non-urban site, duplicate, malformed level, or missing
  source. It seeds 11 period-safe buildings: Rome's aqueduct/mint and pottery
  proxy, Alexandria's library/Pharos/glass, Sidon and Cologne glassware, and
  Chang'an/Luoyang/Chengdu lacquerware.
- `make validate`, a real `make smoke`, and an autonomous observer probe are
  green for this surface. The probe reached `16:00, 7 January, 1` with AI
  market activity; no new specialist-building errors appeared. Evidence is in
  `docs/playtests/M5_SPECIALIST_BUILDINGS.md`.

Next: implement the genuinely missing custom-good and later-period-gated
economy work without using misleading vanilla substitutions, then expand road
and development density before the M5 trade-flow gate.

## 2026-07-19 — M5 development foundation

- Generated the installed development manager's first AD 1 profile: zero
  inferred regional base, +2 for a road, +4 for a town, and +10 for a city.
  The input table is small on purpose and rejects duplicate, unknown, or
  uncontrolled selectors and out-of-range values.
- This is engine scaling attached to the already source-labelled urban and
  transport layers, not a substitute for M4's population history or a claim of
  precise urban output. `make validate` and a real `make smoke` are green with
  zero new error lines.

Next: expand remaining ancient goods/buildings and repeat a longer observer
trade-flow check before considering M5 complete.

## 2026-07-19 — M5 ancient transport corridors

- Generated 25 source-labelled road segments for the Via Aurelia, Via Egnatia,
  Via Maris, Syrian and Royal-Road corridors, Tarim/Transoxianian links, Han
  trunks, and the Indian northern/western trade axes.
- The generator validates installed map endpoints, AD 1 ownership, confidence,
  and duplicate undirected links before emitting the exact bare-endpoint syntax
  used by the installed road start manager.
- `make validate` and a real `make smoke` are green with zero new error lines.

Next: generate the development pass and expand the remaining era-specific goods
and buildings before a longer observer trade-flow check.

## 2026-07-19 — M5 observer foundation probe

- The autonomous driver loaded the active AD 1 world at `08:00, 1 January, 1`,
  entered Observer Mode, and advanced the clock to `13:00, 11 January, 1`.
  Captured frames show the intended political map plus AI market-construction
  notifications while time is running.
- No market, town-setup, RGO, or road errors appeared in the observer log. The
  remaining runtime errors are the already tracked unset capital/government and
  international-organization/HRE surfaces, now narrowed to M6 and M9.
- The detailed, screenshot-linked record is `docs/playtests/M5_RUNTIME_FOUNDATION.md`.

Next: add source-labelled roads and development, expand the remaining ancient
goods/buildings, then repeat the longer trade-flow observer test.

## 2026-07-19 — Runtime-driver readiness repair

- An inspected M5 driver screenshot revealed that the former log-quiescence
  heuristic could accept a black, hung EU5 window as menu-ready. The driver now
  requires a responsive Windows handle and a non-black rendered client frame
  before it reports readiness.
- The corrected driver captured the real game menu and passed a subsequent
  `make validate` plus real `make smoke` with zero new error lines. This restores
  screenshot evidence as a meaningful runtime gate for the upcoming observer
  work.

## 2026-07-19 — M5 anchored ancient production

- Added a higher-priority source-anchor layer over the regional goods rules.
  It gives the plan's named sites their intended goods where the installed map
  was wrong: Huelva/Rio Tinto silver, Cornwall tin, Sidon purple-dye proxy,
  Muza/Adulis incense proxies, Chang'an and Chengdu silk, and Muziris pepper.
- The RGO report now identifies every change as either a regional rule or an
  explicit anchor. It validates anchor uniqueness, installed map keys, AD 1
  control, good keys, sources, and confidence labels before rendering.
- `make validate` and a real `make smoke` are green with zero new error lines.

Next: source and generate roads and development, then expand the era-specific
goods and building catalogue before trade-flow observer verification.

## 2026-07-19 — M5 urban-market foundation

- Generated a 36-row city/town ledger keyed one-to-one to the active ancient
  market hubs. Its profile and source checks reject missing markets, unowned
  locations, unknown map keys, invalid ranks, and invalid confidence labels.
- Market cities receive only engine-valid M5 proxy buildings (temple,
  marketplace, entrepot, granary, mason); market towns receive the smaller
  temple/marketplace/entrepot profile. The profiles are deliberately compact
  until the dedicated ancient building reskin is implemented.
- The live game established that `common/town_setups` requires UTF-8 BOM. The
  generator now writes and validates that encoding. After the correction,
  `make validate` and a real `make smoke` are green with zero new error lines.

Next: source and generate roads and development, then expand the era-specific
goods and building catalogue before trade-flow observer verification.

## 2026-07-19 — M5 raw-material anachronism pass

- Added an auditable `docs/goods_remap.csv` rule table and deterministic generator for the full
  installed location-template surface. It preserves every unlisted template
  field and corrects only controlled AD 1 locations: 9 coffee, 23 tea, 64
  sugar, 32 saltpeter, 110 silk, 33 incense, 41 pepper, and 2 war-elephant
  occurrences.
- Coffee and saltpeter are removed globally; silk is localized to China,
  incense to Arabia/Horn proxies, pepper to India, war elephants to India and
  Southeast Asia, tea to China, sugar to India and Southeast Asia, and American
  crops remain eligible only in the Americas. `docs/m5/rgo_remap_report.csv`
  is the complete output ledger, while the generator rejects unknown goods,
  regions, or duplicate rules.
- `make validate` and a real `make smoke` are green with zero new error lines.

Next: add the plan's era-specific goods and then compatible towns, buildings,
roads, and development before attempting trade-flow observer verification.

## 2026-07-19 — M5 ancient market foundation

- Added 36 source-labelled AD 1 market hubs across the Mediterranean, Indian
  Ocean, Silk Road, East Asia, Southeast Asia, and the Americas. Every market
  uses an installed location key checked by the generator.
- `make validate` and a real `make smoke` are green with zero new error lines.
  The market manager is now a valid foundation for the later RGO, town, road,
  and development layers that the earlier M3 observer blocker requires.

Next: build the source-labelled goods/RGO remap from the installed location
template surface, then seed compatible town setups and buildings.

## 2026-07-19 — M4 culture-remap evidence gap

- Completed two bounded evidence checks: the active-map audit proves installed
  culture labels cannot be mechanically re-dated, and the available Pleiades
  cache is a place/name gazetteer rather than a global culture map. CHGIS is
  useful for research but not redistributable as committed mod data.
- Recorded the gap in `BLOCKERS.md` without changing game content; the tree
  remains green. M4 is intentionally not tagged complete.

Next: proceed with M5's independent economy scaffolding, then return to the
location culture atlas when licensed source data has been assembled.

## 2026-07-19 — M4 active culture-geography audit

- Generated a deterministic audit of 680 installed culture templates actually
  used by the 13,552 controlled AD 1 locations. Each row records its frequency,
  candidate M4 profile cultures, regional distribution, and sample map keys.
- Three controlled map proxies have no installed culture template; their
  source-labelled exceptions are explicit and retain their reviewed tag profile
  until a local historical culture decision is made.
- `make validate` is green. This audit is evidence for the location remap, not
  a claim that the installed later-period culture labels describe AD 1 peoples.

Next: make the remap in source-labelled regional batches from this audit.

## 2026-07-19 — M4 dynamic-name v1

- Added 61 conservative dynamic historical capital names from secure,
  coordinate-reviewed anchors. The generated report records each location,
  culture, language/dialect key, tag, and source; broad SoP proxies and
  contested anchors remain intentionally untouched.
- Every client localization receives the same English historical name. Both
  language-root and dialect keys are emitted, matching the installed game’s
  `location.language` naming convention and the M4 dialect culture contract.
- `make validate` and a real `make smoke` passed with zero new error-log lines.

Next: create the much denser, source-reviewed culture/location remap; do not
mistake this auditable capital layer for the final M4 atlas.

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
