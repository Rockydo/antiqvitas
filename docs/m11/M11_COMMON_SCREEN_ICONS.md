# M11 direct-key religion and institution icons

The installed interface calls `GetReligionIcon(Religion.Self)` and
`GetInstitutionIcon(Institution.Self)`. The installed asset catalog establishes
their direct filename convention: a definition key `x` resolves
`main_menu/gfx/interface/icons/{religion,institutions}/x.dds`. The prior M4
and M8 identifiers had no such files and therefore fell through to
`_default.dds` in every country, pop, tooltip, technology, and institution
surface.

M11 supplies all 37 M4 religion keys and all nine M8 institution keys as
128x128, sRGBA, BC7 DDS textures. `tools/m11_common_icons.py --check` locks
the complete definition-to-texture inventory, verifies the DDS contract, and
requires every remaining transitional religion texture to remain an exact alias
of its reviewed local source while checking every direct ledger chain. Its
`--write` path is the reproducible local build step.

## Religion migration

The religion set moves from installed engine-native aliases to one direct,
ANTIQVITAS-owned illustration per definition key. The completed rows in
`direct_religion_icons.csv` override only their matching key; all other aliases
remain a checked transition while a unique source/master/texture chain is
reviewed. The validator enforces the direct ledger's definition binding, 128px
DDS contract, and source/master uniqueness. The required final state is 37
direct religion illustrations and zero aliases.

The first twelve direct icons cover Roman and Hellenic civic ritual, pre-Nicene
community, Second Temple Jewish community, Iranian sacred-fire, Lankan
Buddhist material contexts, Buddhist travel-and-learning materials, early
South Asian ritual materials, Jain community materials, early Han ceremonial
materials, early Chinese Daoist-adjacent materials, and early Japanese ritual
materials. They are bounded material still lifes rather than depictions of a
named sanctuary, rite, clergy, saint, ruler, city, empire, or historical event.
The reviewed first batch is
[here](DIRECT_RELIGION_ICON_BATCH_01.png).

The second batch uses an uninscribed seven-branched lamp, blank scroll, plain
fire bowl, water vessel, cloth, stupa, palm-leaf bundle, lamp, and alms bowl.
It does not identify a named temple, dynasty, monastery, priest, monk, ruler,
city, group, sect, relic, miracle, scripture, rite, sacrifice, text, or
inscription. The reviewed second batch is
[here](DIRECT_RELIGION_ICON_BATCH_02.png).

The third batch distinguishes a Buddhist travel sleeve and silk strip, a
pre-Puranic South Asian offering set, and Jain study-and-care materials. It
does not identify a named monastery, deity, teacher, temple, priest, monk,
ruler, city, caste, community, scripture, ritual scene, text, or inscription.
The reviewed third batch is [here](DIRECT_RELIGION_ICON_BATCH_03.png).

The fourth batch uses Han bronze, jade, lacquer, bamboo slips, a gourd flask,
evergreen, rice, and unmarked offering materials. It does not identify a named
Heaven, master, school, revelation, kami, shrine, torii, emperor, dynasty,
clan, city, temple, priest, sacrifice, ritual scene, text, or inscription. The
reviewed fourth batch is [here](DIRECT_RELIGION_ICON_BATCH_04.png).

## Fifth Iranian, Korean, Inner Asian, and Tibetan batch

The fifth batch distinguishes an Iranian learning-and-travel material setting,
an early Korean material setting, a broad Inner Asian material setting, and an
early Tibetan highland material setting. It uses only uninscribed study,
travelling, household, cloth, vessel, plant, and stone objects. It identifies
no named community, teacher, deity, symbol, sanctuary, shrine, temple, ruler,
dynasty, city, empire, rite, person, text, or inscription. The reviewed fifth
batch is [here](DIRECT_RELIGION_ICON_BATCH_05.png).

## Sixth Nile, Horn, and Arabian batch

The sixth batch distinguishes Nile Valley, middle-Nile, Horn of Africa, and
Arabian material contexts through uninscribed faience, papyrus, sandstone,
ceramic, fibre, cloth, resin, leather, dates, plant, and stone objects. It
identifies no named deity, animal, temple, shrine, altar, ruler, dynasty,
kingdom, city, pyramid, tomb, stela, Kaaba, rite, person, text, or inscription.
The reviewed sixth batch is [here](DIRECT_RELIGION_ICON_BATCH_06.png).

Until each remaining row is completed, its reviewed installed motif is a broad
readable UI cue, not a claim that the contemporary or historical tradition is
identical to ANTIQVITAS's sourced category.

| ANTIQVITAS definition keys | Reviewed local motif |
|---|---|
| `antq_kemetic`, `antq_kushite_amun`, `antq_aksumite_paganism`, `antq_arabian_polytheism`, `antq_south_arabian_religion`, `antq_punic` | `hellenism_religion` temple |
| `antq_manichaeism` | `manichaeism` wheel |
| `antq_korean_muism`, `antq_siberian` | `shamanism` star motif |
| `antq_tengri`, `antq_bon` | respective installed steppe/highland motifs |
| `antq_celtic_religion`, `antq_germanic_religion` | `norse` northern-folk motif |
| `antq_baltic_slavic`, `antq_finnic` | `romuva`, `muinaisusko` respectively |
| `antq_berber_religion`, `antq_nile_cushitic`, `antq_west_african`, `antq_bantu_religion` | `guanche_religion`, `ajok_religion`, `songhai_religion`, `bantu_religion` respectively |
| `antq_mesoamerican`, `antq_andean`, `antq_north_american`, `antq_caribbean` | `mesoamerican`, `inti`, `great_plains_shamanism`, `tain_feyentun_religion` respectively |
| `antq_austronesian_religion`, `antq_australian_dreaming` | `anitism_religion`, `dreamtime_religion` respectively |

## Institution art

The installed institution art is overwhelmingly medieval or early-modern
(printing press, firearms, industrial machinery, modern globe). The nine M8
definitions therefore use ANTIQVITAS-owned retained sources and reviewed PNG
masters. The nine unique motifs are Hellenistic scroll/olive/ink cup; Roman
wax tablet, measuring cord, and bridge; Han bamboo slips and uninscribed seal;
Buddhist stupa, lamp, and cloth; cataphract armour equipment; handmade-paper
mould and sheets; a late-antique ascetic cell with lamp and cloak; a blank
codex, scroll, lamp, cloth, and stylus; and a civilian settlement still life of
cart wheel, travel bundle, water jar, rope, key, and blank tags.

Theological Orthodoxy and Foederati Statecraft now have separate generated
sources and masters. The validator rejects any shared generated source or
master in the institution set. The former shows only unmarked study materials;
the latter only civilian settlement materials. Neither depicts a named council,
treaty, person, people, battle, flag, weapon, or boundary.

All generated sources live in `assets_queue/generated_sources/`; masters are
in `assets_queue/generated/`; the nine direct-key DDS files are in
`main_menu/gfx/interface/icons/institutions/`. The generated sources were
reviewed, downscaled to the local 128x128 contract, BC7 encoded with
DirectXTex, then decoded into the inspected nine-panel round-trip sheet. The
two replacement masters are reviewed together in
[DIRECT_INSTITUTION_ICON_BATCH_02.png](DIRECT_INSTITUTION_ICON_BATCH_02.png).

Local basis: installed `GetReligionIcon` and `GetInstitutionIcon` GUI uses,
installed religion/institution definition-to-filename pairs, and the local
icon directories. Design basis: master plan sections 11, 15, and 20.
