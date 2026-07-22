# M11 advance-icon migration

The complete M8 tree has 250 advances in five age groups of 50. Its existing
five icon identifiers are retained, but all now resolve to ANTIQVITAS-owned,
reviewed 256x256 DDS textures rather than vanilla surfaces or a missing path.

| Age group | Advances | Icon identifier | Motif | Source/master | Game texture |
|---|---:|---|---|---|---|
| Principate | 50 | `abacus_advance` | wax tablets, stylus, counting board | `antq_advance_principate_source.png` / `antq_advance_principate_256.png` | `abacus_advance.dds` |
| High Empires | 50 | `legalism_advance` | scroll, scales, blank seal | `antq_advance_high_empires_source.png` / `antq_advance_high_empires_256.png` | `legalism_advance.dds` |
| Crisis | 50 | `road_advance_1` | blank milestone and dispatch | `antq_advance_crisis_source.png` / `antq_advance_crisis_256.png` | `road_advance_1.dds` |
| Dominate | 50 | `crown_power_advance_discovery` | plain circlet, purple textile, blank seal | `antq_advance_dominate_source.png` / `antq_advance_dominate_256.png` | `crown_power_advance_discovery.dds` |
| Migrations | 50 | `expansionism` | wagon wheel, travel bundle, water jar | `antq_advance_migrations_source.png` / `antq_advance_migrations_256.png` | `expansionism.dds` |

Sources are under `assets_queue/generated_sources/`; reviewed masters are under
`assets_queue/generated/`; game textures are under
`main_menu/gfx/interface/advance/`.

## Scope review

These are broad, non-reconstructive UI motifs, not claims about a named person,
polity, event, artifact, or settlement. They contain no lettering, flags,
heraldry, religious signs, weapons, ethnic costume, or recognizable monument.
The migration motif is intentionally civilian, and the Dominate circlet is a
plain band rather than a medieval crown.

## Direct-icon migration

The five age-group motifs remain a checked **transitional fallback** while the
project moves to one dedicated player-facing illustration per advance. A
completed row in `direct_advance_icons.csv` replaces only its matching M8
advance binding; the remaining advances continue to use their age-group motif
until their individually reviewed asset chains exist. This prevents a missing
or speculative illustration from appearing in game while making every finished
icon visible immediately.

The first five direct icons are `antq_imperial_cult`, a restrained
early-imperial civic altar; `antq_public_granaries`, an uninscribed grain-store
facade; `antq_provincial_census`, an uninscribed counting table;
`antq_tax_registers`, a wax-tablet and storage-jar still life; and
`antq_road_milestones`, a blank roadside milestone. They are broad cult,
provisioning, administrative, and road-maintenance contexts, not depictions of
a named god, altar, priest, monument, horreum, census figure, tax regime,
inscription, route, ruler, or state doctrine. The direct ledger records the
subject, confidence, status, and non-reconstructive boundary for every future
row. The required final state is 250 completed direct rows and no remaining
transitional binding.

### Batch two review

The Provincial Census and Tax Registers illustrations use deliberately blank
wax tablets, tally stones, cords, jars, weights, and a reed stylus. They do
not depict paper, a codex, readable writing, a coin legend, a seal, a counted
population, a tax rate, or an identifiable court. The Road Milestones icon
uses a completely blank cylindrical stone with a dispatch pouch and survey
tools beside an antique road; it does not identify an emperor, city, route,
distance, monument, or road network. The reviewed three-icon source/master
batch is [here](DIRECT_ADVANCE_ICON_BATCH_02.png).

## Engine and asset verification

The installed build's `main_menu/gfx/interface/advance/` established the
256x256, sRGBA, mipmapped DDS contract. Its `advances_tooltips.gui` uses
`GetAdvanceIcon` and applies the native circular icon mask, so the generated
masters retain a borderless, centered composition. An audit found the first,
second, third, and fifth identifiers as vanilla filenames, but no vanilla
`crown_power_advance_discovery.dds`; the exact M8 identifier is now supplied by
the mod rather than silently falling through.

`tools/m11_advance_icons.py --check` verifies the source/master/texture chain,
the 256x256 DDS contract, the direct ledger's advance and age binding, one
tree use per direct icon, and the remaining fallback count for each age. The
masters are converted with DirectXTex BC7 and inspected before the live smoke
test.

Local basis: installed `advances_tooltips.gui`, installed
`main_menu/gfx/interface/advance/`, and the M8 tree. Design basis: master plan
sections 15 and 20.
