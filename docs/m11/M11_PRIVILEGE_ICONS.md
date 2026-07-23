# M11 direct estate-privilege icons

The installed estate UI calls `GetEstatePrivilegeIcon(EstatePrivilege.Self)`
for every privilege surface. Its native icons are 64x90 DDS textures under
`main_menu/gfx/interface/icons/privileges/`, addressed by definition key.

ANTIQVITAS's 24 M6 privilege keys now migrate through
`direct_privilege_icons.csv`. Each completed row requires a unique generated
source, exact 64x90 PNG master, and direct BC7 DDS texture. The final state is
24 direct illustrations and zero fallback-resolved privilege keys; the staged
validator deliberately reports the remaining work rather than treating a
generic installed privilege image as ANTIQVITAS art.

## First Rome batch

The first three direct icons distinguish landed administration, equestrian
service, and public-priestly material contexts. They are material still lifes,
not depictions of a senator, eques, priest, temple, estate, battle, horse,
office hierarchy, or ritual. The reviewed portrait contact sheet is
[here](DIRECT_PRIVILEGE_ICON_BATCH_01.png).

## Second Rome-and-Han batch

The next three icons distinguish public grain provision, military-household
payment materials, and early Han court administration. They remain uninscribed
object studies, not depictions of a distribution, tax, unit, battle, emperor,
palace, official, document, or seal impression. The reviewed portrait contact
sheet is [here](DIRECT_PRIVILEGE_ICON_BATCH_02.png).

## Third Han, Arsacid, and client-court batch

The next three icons distinguish Han regency materials, an ancient Iranian
court household, and a Mediterranean client court. They remain uninscribed
object studies rather than depictions of a Wang person, great house, king,
emperor, court official, palace, territory, battle, constitutional formula, or
seal impression. The reviewed portrait contact sheet is
[here](DIRECT_PRIVILEGE_ICON_BATCH_03.png).

## Fourth Kushite, steppe, and Korean court batch

The next three icons distinguish a Kushite court household, early steppe clan
household materials, and an early Korean court household. They remain
uninscribed object studies rather than depictions of a ruler, person, dynasty,
palace, territory, battle, mounted force, constitutional formula, or seal
impression. The reviewed portrait contact sheet is
[here](DIRECT_PRIVILEGE_ICON_BATCH_04.png).

## Fifth tribal, Brittonic, and regional-Iranian batch

The next three icons distinguish a tribal household, a deliberately non-ritual
Brittonic religious-specialist material grouping, and an ancient Iranian
regional court. They remain uninscribed object studies rather than depictions
of an elder, druid, king, person, tribe, temple, palace, rite, territory,
battle, constitutional formula, or seal impression. The reviewed portrait
contact sheet is [here](DIRECT_PRIVILEGE_ICON_BATCH_05.png).

## Sixth frontier, regional, chiefly, and town-household batch

The next four icons distinguish a frontier court, an otherwise unassigned
regional court, an early African chiefly household, and a settled town-cluster
household. They remain uninscribed object studies rather than depictions of a
court, ruler, chief, person, polity, town, building, map, battle, constitutional
formula, or seal impression. The reviewed portrait contact sheet is
[here](DIRECT_PRIVILEGE_ICON_BATCH_06.png).

## Seventh and final South Asian, Lankan, and Judean batch

The final five icons distinguish northwestern Indian regional and urban
households, a leading-clan household, a deliberately non-ritual Buddhist
monastic material grouping, and an ancient Judean priesthood material grouping.
They remain uninscribed object studies rather than depictions of a satrap,
Greek city elite, assembly, monk, Buddha, priest, Temple, person, polity,
building, map, battle, constitutional formula, or seal impression. The reviewed
portrait contact sheet is [here](DIRECT_PRIVILEGE_ICON_BATCH_07.png). With this
batch, each of the 24 ANTIQVITAS M6 privilege keys has its own source, PNG
master, and native-contract DDS; no privilege UI fallback remains.
