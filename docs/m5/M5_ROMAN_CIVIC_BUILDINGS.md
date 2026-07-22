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
- **DAR-TABULARIUM** — Digital Augustan Rome, [Tabularium](https://www.digitalaugustanrome.org/records/tabularium/).  Supports the physical building while requiring a contested confidence for the exact archival interpretation.
- **DAR-CIRCUS** — Digital Augustan Rome, [Circus Maximus](https://www.digitalaugustanrome.org/records/circus-maximus/).  Records its long-standing public-entertainment functions.
- **DAR-NAVALIA** — Digital Augustan Rome, [Navalia](https://www.digitalaugustanrome.org/records/navalia/).  Records the Republican-period Tiberine naval arsenal and ship sheds; the precise Augustan configuration remains debated.
- **MET-ROMAN** — Metropolitan Museum of Art, [The Roman World](https://www.metmuseum.org/pt/-/media/files/learn/for-educators/publications-for-educators/roman.pdf).  Used only for the broad, well-attested class of urban Roman milling and baking, not for a precise Rome-site attribution.
- **OCD-ANNONA**, **ITA-LIVIA**, **P12.1**, **P12.3**, and **P8.1** remain the plan's reviewed source identifiers for annona, the Prima Porta proxy, technical craft anchors, special-building seeding, and civic coinage respectively.

## Technical mapping

The definitions use only contracts read from the installed build's
`game/in_game/common/building_types/`: the existing category keys,
employment-size keys, construction-time keys, goods, and modifiers.  They are
special (not normally constructible) one-level buildings, so they provide a
named AD 1 layer without replacing the game's broader building progression.
Their start-state presence is rendered through the existing verified
`building_manager` contract.

## Art review

Four source sheets under `assets_queue/generated_sources/` plus a dedicated
Navalia, Classis Ravennatis, and Castrum Mogontiacum source images were visually reviewed, cropped to 128px masters,
converted to direct BC7 DDS files, and compiled into [the contact sheet](ROMAN_BUILDING_ICON_CONTACT_SHEET.png).
The generator rejects a missing, wrong-size, or non-RGBA direct building icon;
the ledger's `icon_subject` column records the subject of each illustration.

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
