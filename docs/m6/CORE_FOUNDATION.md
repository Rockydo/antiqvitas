# M6 core dynasties, people, and governments

This first M6 slice replaces the M3 random-ruler scaffolding for Rome, Western
Han, and Parthia. The CSV ledgers are the source of every generated character,
dynasty, and government reference; `tools/m6_power.py` validates their dates
through `tools/dates.py` and `tools/generate_start_mirror.py` installs the
start-state managers.

## Historical basis

- Plan §§8.1–8.3 and §19 are the project requirements for Augustus/Gaius,
  Emperor Ping/Wang Mang, and Phraates V/Musa.
- The *Oxford Classical Dictionary* (`OCD`) and *Cambridge Ancient History*,
  vol. XI (`CAH-XI`) are the project's Roman and Parthian synthesis sources,
  registered in [the AD 1 source ledger](../world_1ad/SOURCES.md).
- Columbia University's excerpt and introduction to Ban Gu's *Book of the
  Former Han* identifies Liu Ping's reign (1 BCE–9 CE) and Wang Mang's role as
  chief minister/regent before the usurpation: [Pan Ku's *Book of the Former
  Han*](https://www.columbia.edu/itc/religion/f2001/docs/pan_ku.html).
- Mark Edward Lewis's ANU chronology gives Ping's accession/death frame and
  treats Wang Mang as acting/regent emperor before the Xin usurpation:
  [*The Emperor of Han Dynasty China*, chronology](https://openresearch-repository.anu.edu.au/server/api/core/bitstreams/3df5d9aa-26db-44c1-8372-14d21d5a4250/content).
- Marek Jan Olbrycht's peer-reviewed *Encyclopaedia Iranica* article establishes
  Phraates V's 3/2 BCE–4 CE reign, his joint rule with Musa, and the bounds on
  his birth date: [“Phraates V”](https://www.iranicaonline.org/articles/phraates-v/).

The day-level dates marked `contested` in `characters.csv` are not presented as
new historical claims: `1 January` is a documented engine representation for an
attested year whose day/month is unknown. Musa and Phraates V deliberately have
no scripted biography date because the cited evidence does not justify one.

## Regnal-history boundary

`regnal_histories.csv` retains the source-labelled Augustus and continuous
Western Han succession sequences, including the two short Lu-regency reigns and
Liu He. It is historical reference data, not a pre-campaign script calendar.
`ruler_terms.csv` renders one current-ruler `ruler_term` for every implemented
government profile, all beginning at `1.1.1` through `AntqDate`. A signed
pre-campaign term parses at the menu, but the existing live AD 1 start probe
already demonstrated that the engine validates historic terms against the new
campaign boundary. The generator therefore prevents an out-of-range term from
being emitted, while retaining the cited reign spans for later succession
situations. This is intentional date safety, not a claim that every ruler
acceded on 1 January AD 1.

## Technical adapter

EU5 1.3.1.1 exposes only `monarchy`, `republic`, `steppe_horde`, `theocracy`,
and `tribe` as government types. The three M6 historical systems are therefore
unique reforms on the installed `monarchy` type, never claims that their
institutions were generic early-modern monarchies. Their modifiers use only
keys found in the local government-reform registry. Rome's successor is Gaius
Caesar; Tiberius remains a non-heir character until the planned AD 4 event path.

The later M6 regional slice adds two equally narrow `monarchy` reforms:
Parthian Sub-Kingdom for Ariobarzanes II's Media Atropatene and Buffer Kingdom
for Osroene and Armenia. The first represents a regional Iranian court's
relationship to the Arsacid political world; the second represents frontier
balancing. Neither establishes a bespoke subject contract; that belongs to the
M9 satrapy/client mechanics pass.

The second core slice renders five source-labelled privileges, four laws, and
per-profile societal-value positions from CSV ledgers. It uses only installed
estate keys, law categories, government groups, modifier keys, and country
start syntax harvested from build 24187685. The technical `nobles_estate` and
`burghers_estate` adapters stand in for Roman senators/urban plebs, Han court
personnel, and Parthian great houses; they do not classify those historical
groups as medieval estates. The Roman civic-status and recruitment laws, Han
commandery administration, and Parthian great-house compact are constrained
gameplay representations, not reconstructions of a uniform written legal code.
Each source row records the relevant plan section and synthesis source; the
historically interpretive proxies are marked `contested` in their ledger.

The Judean profile adds a narrower `clergy_estate` adapter for the Second
Temple priesthood. Its verified power and satisfaction modifiers make the
Temple's civic and religious weight playable alongside Archelaus's client
court. This is a UI proxy, not a Christian clerical hierarchy or a claim to
reconstruct the high priesthood's exact legal jurisdiction; its associated
privilege and administrative law say so explicitly.

The Legion estate feasibility review found that the local estate registry is
global and exposes no safe country-scoped attachment point in setup or scripted
effects. Creating a new estate would therefore add an unproven system-wide UI,
event, and population contract rather than a Rome-only political actor. M6
keeps the verified Praetorian Donatives privilege as the plan's fallback; M10
will add the dated legionary succession/crisis interactions when its event and
disaster systems are implemented.

## Coinage standards

Rome's socioeconomic law uses the installed gold-and-silver minting contract
for an Augustan aureus-and-denarius standard. Western Han uses the corresponding
copper contract for cast Wuzhu cash. Both are baseline AD 1 monetary surfaces:
their exact denomination ratios, circulation, and fiscal administration remain
outside the adapter, while dated debasement and Wang Mang's later coin changes
belong to M10 history work. The source ledger records the relevant British
Museum objects alongside P8.1/P8.3, P13, OCD, and BHR.

## Mandate adapter

The Han reform now uses the installed monarchy `monthly_legitimacy` surface to
make the Mandate of Heaven visible in the current government profile. This is
a deliberately conservative starting-state support value, not an assertion
that the Mandate was a generic European legitimacy system. Its historically
contingent loss in the Wang Mang, flood, and civil-war arc remains M10 work.

## Anuradhapura court adapter

Anuradhapura receives Bhatikabhaya Abhaya as its source-qualified current AD 1
ruler, with an explicitly contested conventional reign range rather than an
invented exact accession. Its new monarchy reform applies only verified crown
power and cabinet-efficiency contracts. The associated monastic-patronage
privilege and canal-endowments law make the documented court, Buddhist
institutions, and irrigation patronage legible without treating either estate
or law labels as a reconstructed ancient constitution.

## Secondary AD 1 roster

The next slice adds Maroboduus, Arminius, Juba II, Cleopatra Selene II, Aretas
IV, Natakamani, Amanitore, Wuzhuliu Chanyu, Yuri of Goguryeo, Tasciovanus, and
Cunobelinus. It gives Mauretania, Nabataea, Kush, the Xiongnu, Goguryeo,
Marcomanni, and Catuvellauni source-labelled start profiles. The detailed
source and uncertainty record is [the secondary roster note](SECONDARY_AD1_ROSTER.md).
