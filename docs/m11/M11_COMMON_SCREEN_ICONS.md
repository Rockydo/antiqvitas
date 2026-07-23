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
requires every religion texture to remain an exact alias of its reviewed local
source. Its `--write` path is the reproducible local build step.

## Religion migration

The religion set moves from installed engine-native aliases to one direct,
ANTIQVITAS-owned illustration per definition key. The completed rows in
`direct_religion_icons.csv` override only their matching key; all other aliases
remain a checked transition while a unique source/master/texture chain is
reviewed. The validator enforces the direct ledger's definition binding, 128px
DDS contract, and source/master uniqueness. The required final state is 37
direct religion illustrations and zero aliases.

The first three direct icons cover Roman civic ritual, Hellenic civic ritual,
and pre-Nicene community context. They are bounded material still lifes rather
than depictions of a deity, sanctuary, rite, church, clergy, saint, ruler, or
historical event. The reviewed three-icon batch is
[here](DIRECT_RELIGION_ICON_BATCH_01.png).

Until each remaining row is completed, its reviewed installed motif is a broad
readable UI cue, not a claim that the contemporary or historical tradition is
identical to ANTIQVITAS's sourced category.

| ANTIQVITAS definition keys | Reviewed local motif |
|---|---|
| `antq_religio_romana`, `antq_hellenic`, `antq_kemetic`, `antq_kushite_amun`, `antq_aksumite_paganism`, `antq_arabian_polytheism`, `antq_south_arabian_religion`, `antq_punic` | `hellenism_religion` temple |
| `antq_early_christianity` | `catholic` Christian UI marker |
| `antq_judaism` | `judaism` menorah |
| `antq_arsacid_zoroastrianism` | `zoroastrian` winged motif |
| `antq_manichaeism` | `manichaeism` wheel |
| `antq_theravada`, `antq_mahayana` | respective installed Buddhist motifs |
| `antq_brahmanism`, `antq_jainism` | respective installed Indian motifs |
| `antq_chinese_state_cult`, `antq_daoism` | `sanjiao` balance motif |
| `antq_kami` | `shinto` gate |
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
