# ANTIQVITAS TODO

Tasks are taken top-to-bottom within the current milestone. A milestone closes only
after `make full` and its autonomous driver report are green.

## Active user priorities — 2026-07-22

- [ ] Continue the rich, source-led Roman building system with frontier infrastructure only where a specific AD 1 source and engine-safe contract support it; retain conservative proxies rather than backdating later castra.
- [ ] Expand the AD 1 dynamic-location naming layer beyond anchors, prioritizing the Roman world and every player-facing map location with a secure period form.
- [ ] Replace all shared/fallback UI visuals with dedicated illustrations for every ANTIQVITAS advance, privilege, building, good, religion, and institution; retain a checked asset ledger and contact-sheet review.
  - [x] Start and smoke-check the direct M8 migration: a ledger-driven, one-icon-at-a-time renderer path is live; reviewed Imperial Cult and Public Granaries icons are the first two of 250 direct advance illustrations.

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

## M5 — Economy

- [x] Replace generic Roman civic/economic proxies with a source-led named building pass: 22 direct-icon specials now cover water, public grain storage, Forum Romanum/Augusti, Basilica Aemilia, macellum, Horrea Galbana, baths, Theatre of Marcellus, Mars Ultor cult, Tabularium, Circus, mint, workshops, mill/bakery, Villa Liviae, the Pantheum, Saepta, Diribitorium, the naval bases at Rome and Ravenna, and the Mogontiacum frontier camp. See `docs/m5/roman_buildings.csv` and `M5_ROMAN_CIVIC_BUILDINGS.md`.
- [x] Add the source-led naval-supply pass: Navalia Romae is now a named, direct-icon special tied to tar, naval supplies, tools, lumber, and cloth, with modest sailor/repair effects and an explicitly contested Augustan configuration.
- [x] Add the securely dated Augustan naval-base pass: Classis Ravennatis is now a named Ravenna special, tied to direct military-port evidence at nearby Classe and the same bounded naval-supply goods.
- [x] Add the securely dated Augustan frontier-camp pass: Castrum Mogontiacum is now a named Mainz special with the installed low non-propagating fort contract, a dedicated icon, and no reconstructed garrison roster.
- [x] Add three securely dated Campus Martius civic specials: Agrippa's Pantheum (c. 27 BC), Saepta Iulia (26 BC), and the Diribitorium (7 BC), with direct art and period-appropriate upkeep goods.
- [ ] Add further Roman frontier infrastructure only where a specific AD 1 source and a locally verified building contract support it; keep the existing M7 castra/limes proxies conservative and do not backdate Castra Praetoria (AD 21-23).
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
- [ ] Verify ancient trade flows; run milestone gate and tag `M5-done`. Runtime RGO works, but both pre-seeded and automatic runtime-market paths now reproduce `Getting relation with itself`; M5 remains deferred pending a locally supported market/merchant contract, documented in `BLOCKERS.md`.

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
- [ ] Driver-test Rome, Han, and Parthia; run milestone gate and tag `M6-done`. Rome and Parthia pass the current-term probe; Han's three-probe minority-regency fallback and the new anonymous-XDP ruler-term overlap are recorded in `BLOCKERS.md`.

## M7 — War

- [x] Implement ancient units, levies/regulars, mercenaries, forts/limes, and navies; remove gunpowder/oceanic units.
- [ ] Observer-test wars; run milestone gate and tag `M7-done`. Observer now
  starts and a controlled Rome-Parthia AI war is created, but sustained
  high-speed playback reaches the renderer crash recorded in `BLOCKERS.md`.

## M8 — Knowledge

- [x] Generate and validate the required birth-location static-modifier contract for all nine custom institutions.
- [x] Implement five complete age trees, roughly 250 advances, institutions, tech tiers, objectives, and abilities.
- [x] Restore a fresh paused AD 1 observer start with zero removed-law and invalid-estate diagnostics. Removing the inherited vanilla setup templates reduced the archived 213 removed laws plus 227 invalid estate privileges to zero in the fresh driver-observer run; evidence: `docs/playtests/AD1_STARTUP_DEFAULTS_20260721.md`.
- [ ] Test AI research and anachronism/dead-end rules; run milestone gate and tag `M8-done`. (The enabled AD 1 selector and zero-new-line menu smoke are recorded; observer runtime remains blocked by the renderer condition in `BLOCKERS.md`.)

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
- [ ] Smoke and observer-test every batch; run milestone gate and tag `M10-done`.

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

## M12 — Ship

- [x] Complete the static pacing/growth/inflation and AI-weight audit; restore bounded local-contract priorities to the seven active M9 CBs.
- [x] Quarantine all 7,440 installed vanilla event definitions in 347 files through a source-preserving, date-gated overlay that retains the loader's scheduler/scope/effect graph.
- [x] Guard the five absent-IO and eight dated country-startup branches in the installed hardcoded on-game-start handler through a checked exact-name overlay; fresh AD 1 observer initialization has zero former hardcoded runtime errors.
- [x] Guard four optional-government and three HRE special-status CoA predicates through a checked exact-name overlay; fresh AD 1 observer initialization has zero former CoA scope errors.
- [x] Guard the installed Catalan Sitges-capital flag predicate through a checked exact-name overlay; a fresh AD 1 observer initialization has zero script-system errors.
- [ ] Complete runtime pacing/growth/inflation balance from observer measurements. The checkpointed normal-renderer driver now resumes the latest autosave through the documented menu route; it still needs its first renderer-exit recovery and decade-scale balance evidence.
- [ ] Run the checkpointed autonomous observer game to 476 with decade screenshots and live log watch. The AD 39 checkpoint campaign reached AD 41, then stopped on the repeated market self-relation assertion; resolve or locally neutralize that runtime market contract before resuming the chronology.
- [x] Finish README, known issues, packaging notes, static finale verification, and the full surface-area inventory audit.
- [x] Disable the eleven installed anachronistic generic mission packs through checked exact-name visibility overlays; retain their keys for engine references.
- [x] Pin a static player-facing anachronism audit across all 17 English localization files, with the client-language mirror contract checked separately.
- [x] Resolve the observer country-change rule through a menu-smoked, exact-name installed-file overlay; the driver can now enter Observer without altering any historical or AI rule.
- [x] Complete the M12 tutorial/hint audit: retain evidence-safe generic surfaces and disable 33 dated/dynastic vanilla hints through a menu-smoked, verified exact-name contract.
- [ ] Eliminate every fresh AD 1 culture/religion no-pop diagnostic without weakening the accepted baseline. The initial country-selection probe found 327 vanilla culture and 123 religion diagnostic types; the shipped culture suppressor has been rejected twice by the live parser, so the remaining solution must be an engine-accepted start-data contract.
- [x] Run and record the final static/menu `make full` gate (rerun 2026-07-21:
      all checks pass and the enabled-mod smoke has zero new lines).
- [x] Run the current full gate and record its report: `make full` is green at 350 cultures, 37 religions, 416 historical-current events, and the 230,000.000-thousand population target, with zero new smoke lines.
- [ ] Tag `M12-done`: complete the checkpointed AD 1-to-476 Observer chronology, its decade evidence, and the remaining runtime balance checks.
