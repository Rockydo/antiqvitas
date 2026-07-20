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

- [x] Seed and smoke-check 42 source-labelled AD 1 market hubs.
- [x] Localize and anchor the plan-listed ancient raw goods on controlled AD 1 map locations (328 audited corrections).
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
- [x] Model Muza's active commercial roadstead with a market-warehouse proxy, explicitly avoiding a false harbor tier.
- [x] Add the plan-required AD 1 Second Temple at Jerusalem and its guarded AD 70 building-destruction current.
- [x] Add a source-qualified Buddhist monastic proxy at Anuradhapura without applying a later Christian building identity.
- [x] Add a source-qualified Prima Porta villa proxy without claiming a latifundium census or slave-labor measure.
- [ ] Implement the remaining goods/RGOs, buildings/town setups, roads, and development beyond this first dedicated-goods pass. The plan-listed Ephesus and Oc Eo growth hubs, Noricum iron anchor, eight source-labelled harbor tiers, Muza's roadstead-market tier, the Second Temple transformation, Anuradhapura and Prima Porta historic-building anchors, and a 36-segment road network now extend the building/transport surfaces; RGO runtime application is deferred in `BLOCKERS.md`, while other independent M5 surfaces may continue.
- [ ] Verify ancient trade flows; run milestone gate and tag `M5-done`. (Blocked until a runtime-effective RGO surface is found.)

## M6 — Power

- [x] Establish a checked, sourced Rome/Han/Parthia core: historical reforms, dynasties, nine named characters, Gaius Caesar as Rome's heir, Wang Mang's regency, and the AD 1 Chang'an capital correction.
- [x] Add source-labelled core estate adapters, privileges, laws, and societal values for the Rome/Han/Parthia profiles through locally verified engine contracts.
- [x] Add the first Tier-1/2 secondary-ruler slice: eleven named AD 1 figures, seven country profiles, and source-labelled client, Kushite, steppe, Korean, and tribal-government adapters.
- [x] Add the AD 1 Herodian client tetrarchy: Archelaus in Judea, Antipas in Galilee-Peraea, and Philip in Batanea.
- [x] Add the next named Roman client rulers: Archelaus of Cappadocia, Antiochus III of Commagene, Rhoemetalces I of Thrace, and Dynamis of Bosporus.
- [x] Render campaign-valid current `ruler_term` records for every implemented non-regency government and retain source-led Augustus/Western Han regnal back-history without scripting pre-AD-1 campaign dates.
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
- [ ] Expand that foundation to the plan's governments, estates, privileges, laws, societal values, full Tier-1/2 rosters, and regnal histories. (250 source-led characters and 24 privilege adapters currently.)
- [ ] Driver-test Rome, Han, and Parthia; run milestone gate and tag `M6-done`.

## M7 — War

- [x] Implement ancient units, levies/regulars, mercenaries, forts/limes, and navies; remove gunpowder/oceanic units.
- [ ] Observer-test wars; run milestone gate and tag `M7-done`. (Two current
  driver confirmation attempts are recorded in `BLOCKERS.md`; continue M8.)

## M8 — Knowledge

- [x] Implement five complete age trees, roughly 250 advances, institutions, tech tiers, objectives, and abilities.
- [ ] Test AI research and anachronism/dead-end rules; run milestone gate and tag `M8-done`. (The enabled AD 1 selector and zero-new-line menu smoke are recorded; observer input remains blocked by the confirmation issue in `BLOCKERS.md`.)

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
- [ ] Verify ancient diplomatic webs; run milestone gate and tag `M9-done`.

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
        18 currents, including the AD 192 dynamic Champa release from the
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
- [ ] Smoke and observer-test every batch; run milestone gate and tag `M10-done`.

## M11 — Flavor & face

- [x] Generate, dimension-check, round-trip review, and smoke-test the first AD 1 Rome loading-screen master and DDS override.
- [x] Generate, dimension-check, round-trip review, wire, and smoke-test the first M10 event illustration for AD 1 *Immensum Bellum*.
- [ ] Reach event/decision targets; finish flags, icons, illustrations, loading/age art, localization, glossary, and credits.
- [ ] Remove common-screen placeholders; run milestone gate and tag `M11-done`.

## M12 — Ship

- [ ] Balance pacing/growth/inflation and audit AI weights.
- [ ] Run autonomous observer game to 476 with decade screenshots and live log watch.
- [ ] Finish README, known issues, packaging notes, finale verification, and full surface-area audit.
- [ ] Run final `make full`; create M12 report; tag `M12-done`.
