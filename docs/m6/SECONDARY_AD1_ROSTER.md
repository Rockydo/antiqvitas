# M6 secondary AD 1 roster

This focused Tier-1/2 slice promotes eleven people explicitly named in plan
sections 8 and 19. The source-led data is in `characters.csv`, `dynasties.csv`,
and `governments.csv`; `tools/m6_power.py` renders all engine content from
those ledgers.

| Polity | People added | Government adapter | Sources |
| --- | --- | --- | --- |
| Mauretania | Juba II, Cleopatra Selene II | Client Monarchy | P8.1; OCD |
| Nabataea | Aretas IV | Client Monarchy | P8.1; OCD |
| Kush | Natakamani, Amanitore | Kushite Dual Kingship | P8.5; CAH-XI; PLE |
| Xiongnu | Wuzhuliu Chanyu | Steppe Confederation | P8.3; CAH-XI |
| Goguryeo | Yuri | Early Korean Kingdom | P8.3; SAM |
| Marcomanni | Maroboduus | Tribal Kingdom | P8.7; CAH-XI |
| Catuvellauni | Tasciovanus, Cunobelinus | Tribal Kingdom | P8.7; CAH-XI |
| Roman service | Arminius | Court character only | P8.7; CAH-XI |

`OCD`, `CAH-XI`, `PLE`, and `SAM` are defined in the project
[AD 1 source ledger](../world_1ad/SOURCES.md). The independent Korean
chronology cross-check identifies Yuri as the second Goguryeo king, reigning
from 19 BCE to AD 18: [Encyclopedia of Korean Culture](https://encykorea.aks.ac.kr/Article/E0041388).

## Anuradhapura

Bhatikabhaya Abhaya is added as the current Anuradhapura ruler at the AD 1
campaign boundary. The Siddham inscription record identifies him with the
king who granted a canal and places his conventional reign across the boundary;
a scholarly study of the island's irrigation inscriptions likewise records
canal works during his reign. The exact endpoints differ among chronologies,
so the ledger marks the historical range contested and scripts neither an
accession day nor a successor.

The new Anuradhapura Kingship reform, Monastic Patronage privilege, and Royal
Canal Endowments law are deliberately bounded adapters. The `clergy_estate`
is a technical proxy for Buddhist monastic institutions, and the law represents
attested royal endowment rather than a reconstructed Lankan legal code. Sources:
P8.4; CAH-XI; `SRI-BHAT` in the [source ledger](../world_1ad/SOURCES.md).

## Indian ganasanghas

Yaudheya, Arjunayana, and Kuninda now use the installed `republic` government
type with an Indian Ganasangha reform, a leading-clan council privilege, and a
council-governance law. The plan and CAH-XI support their republican political
forms, but the project source set does not securely identify an individual
current leader at the AD 1 boundary. Each therefore retains the engine's
locally verified `ruler = random` contract rather than receiving an invented
name, dynasty, or ruler term.

The republic and the `nobles_estate` council bucket are technical surfaces for
leading warrior clans; neither claims a European-style republic, a hereditary
nobility, an exact constitutional text, or a membership roll. Sources: P8.4;
P13; CAH-XI.

## Intentional limits

The dynasty labels marked `contested` are engine continuity labels where the
historical evidence identifies a royal or aristocratic line but does not supply
a defensible full formal-house reconstruction. The ledger says so directly and
does not fabricate parentage or day-level biography dates.

Natakamani and Amanitore are represented through the engine's ruler/consort
surface solely to make their documented co-rule visible. That technical mapping
does not resolve the debated nature of their personal relationship. Likewise,
the client-monarchy law, the Xiongnu confederation law, and the two tribal
adapters model political relationships rather than claiming a shared written
constitution.

## Herodian tetrarchy

The next client-king slice adds Herod Archelaus for Judea/Samaria, Herod
Antipas for Galilee-Peraea, and Philip for the northern/Batanean tetrarchy.
All three use the existing Herodian dynasty and the previously tested client
monarchy adapter. This preserves the plan's AD 1 division without prematurely
turning Judea into the later directly administered province.

The trio and their territories are required by P8.1 and cross-checked against
the project's OCD entries. An independent reference also describes Archelaus
as ethnarch and Antipas/Philip as tetrarchs after Herod's 4 BCE death:
[Encyclopedia of the Bible](https://www.biblegateway.com/resources/encyclopedia-of-the-bible/Herod).
No parent links, spouses, or day-level biography dates are fabricated here.

The later mechanics slice gives Judea a `clergy_estate` privilege and an
administrative law for the Second Temple priesthood. These use locally verified
estate contracts to express a documented political and religious actor, not a
Christian hierarchy or a complete reconstruction of high-priestly authority.

## Further Roman client courts

Archelaus of Cappadocia, Antiochus III of Commagene, Rhoemetalces I of Thrace,
Pythodoris of Thrace, and Dynamis of Bosporus extend the plan's named Roman
client ring. They use the established client-monarchy adapter rather than
inventing distinct engine types for each client arrangement.

The Cappadocian ruler's AD 1 place is strongly supported by the Oxford
Classical Dictionary's [Archelaus entry](https://academic.oup.com/edited-volume/61673/chapter/548528356),
which dates his Cappadocian reign from 36 BCE to AD 17. The British Museum
identifies Antiochus III as the son of the Commagene king whose death led to
the AD 17 annexation: [collection record](https://www.britishmuseum.org/collection/term/BIOG205268).
The exact Bosporan succession remains contested as required by the master plan;
the data preserves Dynamis without adding unsupported succession links.

## Near Eastern border courts

The next M6 slice replaces four Tier-1 random-ruler profiles with five named
people: Iamblichus II of Emesa, Abgar V Ukkama of Osroene, Ariobarzanes II of
Media Atropatene, and the Armenian co-rulers Tigranes IV and Erato. It adds a
Parthian Sub-Kingdom adapter for Atropatene and a narrowly labelled Buffer
Kingdom adapter for Osroene and Armenia; both are technical representations of
frontier-court politics, not claims of a uniform constitution.

The Emesan and Osroene starts are secure from the project's OCD/Pleiades
source route. The public scholarly cross-checks for the eastern courts are
*Encyclopaedia Iranica* on [Media Atropatene](https://www.iranicaonline.org/articles/azerbaijan-iii/) and
[Armenia and Iran](https://www.iranicaonline.org/articles/armenia-ii/). The
Tigranes IV–Erato succession falls within AD 1, so it remains contested and
open-ended: no death date, successor, or intra-year tag change is pre-scripted.

## Caucasian Iberia

Pharasmanes I now replaces Caucasian Iberia's random ruler through the existing
Buffer Kingdom adapter. The plan places his accession at approximately AD 1;
the source ledger follows Toumanoff's conventional chronology but marks both
the dynastic label and the exact accession timing contested. The engine record
therefore begins at the campaign boundary and scripts neither an accession day
nor a successor.
