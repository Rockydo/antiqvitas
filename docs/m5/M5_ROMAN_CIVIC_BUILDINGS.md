# Roman civic, commercial, and naval buildings at the AD 1 start

`roman_buildings.csv` is the canonical data ledger for the named special
buildings seeded at the installed `rome`, `ravenna`, or `mainz` location. Every entry is a
subject-specific ANTIQVITAS building type, with a dedicated UI icon contract,
localized English name and description, a locally verified EU5 category,
employment, construction, and modifier contract, and its own source note.

The effects are intentionally conservative.  They are gameplay proxies for
known civic functions, not a numerical reconstruction of the Augustan economy.
The `goods` column identifies the relevant ancient inputs/services; maintenance
creates modest market demand for those goods rather than claiming recorded
quantities.

## Source key

- **SOV-AQUA-VIRGO** — Sovrintendenza Capitolina, [Acquedotto Vergine](https://www.sovraintendenzaroma.it/node/10770).  The Aqua Virgo was inaugurated by Agrippa in 19 BC.
- **TR-BATHS-AGRIPPA** — Turismo Roma, [Via dell'Arco della Ciambella and the Baths of Agrippa](https://www.turismoroma.it/en/node/81041).  Dates the public bath complex to 25–19 BC and identifies its Aqua Virgo supply.
- **PARC-FORUM** — Parco archeologico del Colosseo, [Foro Romano](https://www.colosseo.it/en/area/roman-forum-palatine-hill/).  Used for the enduring civic, commercial, and legal role of the Forum Romanum.
- **DAR-FORUM-AUG** — Digital Augustan Rome, [Forum Augusti](https://www.digitalaugustanrome.org/records/forum-augusti/).  Dates the complex and Temple of Mars Ultor to 2 BC and records its civic, ritual, diplomatic, and judicial uses.
- **PARCO-AEMILIA** — Parco archeologico del Colosseo, [Basilica Aemilia restoration record](https://colosseo.it/en/parco-green/a-green-worksite-at-the-colosseum-the-restoration-of-the-basilica-aemilias-architectural-elements/).  Records the 179 BC foundation, 14 BC fire, and Augustan rebuilding.
- **DAR-MACELLUM** — Digital Augustan Rome, [Macellum (Forum Romanum)](https://www.digitalaugustanrome.org/records/macellum-forum-romanum/).  Places the food market and gives its 179 BC rebuilding date.
- **DAR-HORREA-GALBANA** — Digital Augustan Rome, [Horrea Galbana](https://www.digitalaugustanrome.org/records/horrea-galbana/).  Identifies the extensive Emporium warehouse complex as securely pre-AD 1.
- **TR-THEATRE-MARCELLUS** — Turismo Roma, [The Theatre of Marcellus](https://www.turismoroma.it/en/places/theatre-marcellus).  Gives the Caesarian/Augustan construction sequence and 13/11 BC inauguration.
- **DAR-THEATRUM-BALBUS** — Digital Augustan Rome, [Theatrum Balbus](https://www.digitalaugustanrome.org/records/theatrum-balbus/). Records L. Cornelius Balbus's Campus Martius stone theatre and its dedication in 13 BC.
- **DAR-TABULARIUM** — Digital Augustan Rome, [Tabularium](https://www.digitalaugustanrome.org/records/tabularium/).  Supports the physical building while requiring a contested confidence for the exact archival interpretation.
- **DAR-CIRCUS** — Digital Augustan Rome, [Circus Maximus](https://www.digitalaugustanrome.org/records/circus-maximus/).  Records its long-standing public-entertainment functions.
- **DAR-NAVALIA** — Digital Augustan Rome, [Navalia](https://www.digitalaugustanrome.org/records/navalia/).  Records the Republican-period Tiberine naval arsenal and ship sheds; the precise Augustan configuration remains debated.
- **MET-ROMAN** — Metropolitan Museum of Art, [The Roman World](https://www.metmuseum.org/pt/-/media/files/learn/for-educators/publications-for-educators/roman.pdf).  Used only for the broad, well-attested class of urban Roman milling and baking, not for a precise Rome-site attribution.
- **OCD-ANNONA**, **ITA-LIVIA**, **P12.1**, **P12.3**, and **P8.1** remain the plan's reviewed source identifiers for annona, the Prima Porta proxy, technical craft anchors, special-building seeding, and civic coinage respectively.

- **DAR-ARA-PACIS** â€” Digital Augustan Rome, [Pax Augusta, Ara](https://www.digitalaugustanrome.org/records/pax-augusta-ara/). Records the Senate's 13 BC decree and 30 January 9 BC dedication of the Ara Pacis Augustae.
- **DAR-MAUSOLEUM** â€” Digital Augustan Rome, [Mausoleum: Augustus](https://www.digitalaugustanrome.org/records/mausoleum-augustus/). Records a pre-AD 1 Campus Martius tomb and public grove/walk context, while retaining uncertainty about the exact construction sequence.

### Campus Martius civic additions

`DAR-PANTHEUM` is Digital Augustan Rome's [Pantheum record](https://www.digitalaugustanrome.org/records/pantheum/): Agrippa's temple was erected around 27 BC, but its original form is only partly recoverable beneath Hadrian's later rebuilding. `DAR-SAEPTA` is its [Saepta Iulia record](https://www.digitalaugustanrome.org/records/saepta-iulia/): Agrippa dedicated the great porticoed tribal-voting enclosure in 26 BC. `DAR-DIRIBITORIUM` is its [Diribitorium record](https://www.digitalaugustanrome.org/records/diribitorium/): Augustus completed the vote-counting hall in 7 BC, with exceptional long timber roof trusses.

The three Rome specials are limited city-point proxies. Pantheum Agrippae does not use the later Hadrianic rotunda; Saepta Iulia does not import its later luxury-market use; and the Diribitorium does not reconstruct a ballot procedure, staff, or count. Their modest upkeep distinguishes stone, marble, timber, cloth, tools, incense, wine, pottery, and beeswax as relevant ancient goods or services without treating the values as a historical inventory.

### Palatine temple and library additions

`DAR-APOLLO-PAL` is Digital Augustan Rome's [Apollo Templum (Palatium) record](https://www.digitalaugustanrome.org/records/apollo-templum-palatium/): Augustus' Temple of Apollo was dedicated on 9 October 28 BC and was built in Luna marble. `DAR-BIBLIOTHECA-PAL` is its [Bibliotheca Latina Graecaque record](https://www.digitalaugustanrome.org/records/bibliotheca-latina-graecaque/): the Palatine library held Greek and Latin collections, likely opened after 28 BC and was probably in use by 23 BC; it was also used for some Senate meetings.

The Temple of Apollo is a modest cult-complex proxy only; it does not rebuild its lost interior programme, priesthood, rites, or the later imperial palace. The library's pre-AD 1 function is retained while its uncertain plan and opening sequence are explicitly marked contested. Its `books` input is an engine-good proxy for scroll collections, not a claim for codices, a surviving catalogue, or stock volume; beeswax stands only for the ordinary tablet-and-record context. The two separate direct illustrations deliberately omit named persons, inscriptions, later buildings, and Christian imagery.

### Senate house and public-portico additions

`DAR-CURIA-IULIA` is Digital Augustan Rome's [Curia Iulia record](https://www.digitalaugustanrome.org/records/curia-iulia/): the Senate house was essentially built by Augustus in 29 BC, while the adjacent Chalcidicum's identification remains debated. `DAR-PORTICUS-OCTAVIAE` is its [Porticus Octaviae record](https://www.digitalaugustanrome.org/records/porticus-octaviae/): the Republican portico was restored between 27 and 23 BC with a library, `schola`, and `curia`, though the construction sponsor and detailed arrangement are contested.

The Curia Iulia uses a narrow government-and-records proxy rather than setting a Senate membership, law, vote, or later restoration. Porticus Octaviae is a cultural public-space proxy, not a collapsed group of temples, a commerce arcade, or a copied library building. Both use restrained material and service goods as upkeep demand; no value claims an ancient budget or stock. Their reviewed direct art distinguishes the rectangular senate hall from the open quadriporticus and omits inscriptions, named figures, later reconstructions, and religious anachronisms.

### Emporium warehouse and Alsietina waterwork additions

`DAR-PORTICUS-AEMILIA` is Digital Augustan Rome's [Porticus Aemilia (Emporium) record](https://www.digitalaugustanrome.org/records/porticus-aemilia-emporium/): the vast Tiber-side warehouse's role and scale are archaeologically secure, but its traditional name is debated. `DAR-AQUA-ALSIETINA` is its [Aqua Alsietina record](https://www.digitalaugustanrome.org/records/aqua-alsietina/): Augustus' water channel supplied the 2 BC Naumachia, irrigation in Trans Tiberim, and emergency water, although much of its course is reconstructed from Frontinus.

Porticus Aemilia uses a trade contract with a broad but deliberately non-quantified handling demand for grain, wine, olives, fish, salt, pottery, lumber, and tools. It does not claim a particular annual cargo, ship type, warehouse plan, or a settled debate over the building's ancient name. Aqua Alsietina uses only modest capacity and food context with masonry, tools, and pottery upkeep; it does not construct a Naumachia, assign water volume, or reproduce a distribution network. Their direct illustrations distinguish the active river warehouse from low practical water infrastructure.

### Naumachia and solar-calendar additions

`DAR-NAUMACHIA` is Digital Augustan Rome's [Naumachia record](https://www.digitalaugustanrome.org/records/naumachia/): Augustus' Trans-Tiberim basin was dedicated in 2 BC for aquatic displays, with a central island and a bridge reported in the sources. `DAR-HOROLOGIUM` is its [Horologium Augusti record](https://www.digitalaugustanrome.org/records/horologium-augusti/): the 10 BC Campus Martius monument used an obelisk gnomon and bronze meridian line, but its complete layout is debated.

The Naumachia is only a public aquatic-display proxy with modest cultural and upkeep context. It does not script a battle, capacity, spectator list, or a reconstruction of the basin. The Horologium is only an open solar-calendar-space proxy; copper is the engine-good stand-in for bronze, not a material inventory, and the special does not claim a full clock, calendar marks, or plaza plan.

### Theatre of Balbus addition

`DAR-THEATRUM-BALBUS` records the small Campus Martius stone theatre built by
L. Cornelius Balbus and dedicated in 13 BC. The special uses the same verified
cultural-building contract as the Theatre of Marcellus, but its lower modifiers
and upkeep keep it a distinct modest cultural node. Wine, cloth, and pottery
are gameplay demand proxies for public performance and maintenance, not a
recorded stock list, performance calendar, or audience size. Its direct art is
a generic theatre silhouette because the theatre's plan and decoration remain
only partly recoverable; it does not portray a crowd, statue, inscription,
ritual, named patron, or the Crypta Balbi as an asserted reconstruction.

### Ara Pacis and Mausoleum additions

`DAR-ARA-PACIS` records the Ara Pacis Augustae's Senate decree in 13 BC and
dedication on 30 January 9 BC. It is therefore a secure AD 1 Campus Martius
anchor. The special is only a modest open-air cult-space proxy: it deliberately
omits the historical procession frieze, named family members, a rite, and a
complete plaza reconstruction.

`DAR-MAUSOLEUM` records Augustus' monumental Campus Martius tomb and public
groves/walks before AD 1, while preserving the scholarly uncertainty over its
exact construction sequence. The special is a cultural-landscape proxy only:
it does not determine the tomb's internal plan, occupants, sculpture, complete
landscaping, or later ruin state. Both direct icons use restrained exterior
silhouettes rather than invented scenes.

## Technical mapping

The definitions use only contracts read from the installed build's
`game/in_game/common/building_types/`: the existing category keys,
employment-size keys, construction-time keys, goods, and modifiers.  They are
special (not normally constructible) one-level buildings, so they provide a
named AD 1 layer without replacing the game's broader building progression.
Their start-state presence is rendered through the existing verified
`building_manager` contract.

## Art review

The direct Pantheum Agrippae, Saepta Iulia, Diribitorium, Temple of Apollo, Palatine Library, Curia Iulia, Porticus Octaviae, Emporium warehouse, Aqua Alsietina, Naumachia, Horologium, and Theatre of Balbus source images were
visually reviewed, cropped to 128px masters, converted to direct BC7 DDS
files, and added to [the contact sheet](ROMAN_BUILDING_ICON_CONTACT_SHEET.png)
alongside the existing named-building set.
The generator rejects a missing, wrong-size, or non-RGBA direct building icon;
the ledger's `icon_subject` column records the subject of each illustration.
Ara Pacis and Mausoleum source images were reviewed under the same contract;
the refreshed sheet now contains all 34 named Roman specials.

## Ravenna military-port source and boundary

`MIC-CLASSE` is the Italian Ministry of Culture's [Civitas Classis / Classe record](https://catalogo.beniculturali.it/detail/ibc/ArchaeologicalProperty/156046), which records Augustus' military fleet and port development at Ravenna. `RA-CLASSE` is [Ravenna Turismo's Ancient Port of Classe record](https://www.turismo.ra.it/en/myravenna/wave/ancient-port-of-classe/), which dates the military-port order to 27 BC.

`Classis Ravennatis` uses the verified naval/dock contract as a modest
port-base maintenance proxy. Its Ravenna city point does not reconstruct the
nearby Classe lagoon, ship total, naval order of battle, or supply volume.

## Mogontiacum camp source and boundary

`MZ-MOG` is the City of Mainz's [Roman Mainz history](https://www.mainz.de/en/angebote-entdecken/kultur/stadtgeschichte/roemisches-mainz/roemisches-mainz), which identifies Mogontiacum as a strategic legionary camp opposite the Main under Drusus. `MZ-DRUSUS` is the City of Mainz's [Drusus Stone history](https://www.mainz.de/pl/angebote-entdecken/zu-gast-in-mainz/sehenswertes/drususstein), which dates the base-camp founding to 13 BC.

`Castrum Mogontiacum` uses the installed stockade's low fort-level raw contract
and modest garrison/unrest modifiers. It is expressly timber-and-earth rather
than a later stone fortress, and it does not encode a legion count, unit roster,
frontier line, or stone-wall reconstruction.

## Augusta Raurica camp source and boundary

`AR-COLONIA` is Augusta Raurica's official
[colony-foundation record](https://www.augustaraurica.ch/archaeologie/koloniegruendung).
It states that, after a refoundation, construction of Augusta Raurica began
under Augustus after 15 BC; it also identifies a wood-built military camp on
the Rhine plain at Kaiseraugst. The installed map contains no Augst or
Kaiseraugst point, but its `basel` point is securely Roman-controlled in the
AD 1 ownership ledger.

`Augusta Raurica Camp` therefore uses the same locally verified low
`defense_category`/`stockade_employment`/`small_fort_building` contract as the
Mogontiacum exception, with smaller garrison and unrest effects. It is a
bounded near-site timber-and-earth camp proxy only: the display name is a
functional identifier rather than a recovered Roman fort title, and it claims
no legion, stone fortress, limes line, or complete camp plan.
