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
