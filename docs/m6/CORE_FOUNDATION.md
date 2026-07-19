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

## Technical adapter

EU5 1.3.1.1 exposes only `monarchy`, `republic`, `steppe_horde`, `theocracy`,
and `tribe` as government types. The three M6 historical systems are therefore
unique reforms on the installed `monarchy` type, never claims that their
institutions were generic early-modern monarchies. Their modifiers use only
keys found in the local government-reform registry. Rome's successor is Gaius
Caesar; Tiberius remains a non-heir character until the planned AD 4 event path.

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
