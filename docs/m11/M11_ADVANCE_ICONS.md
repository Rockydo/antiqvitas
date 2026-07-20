# M11 advance-icon group pass

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

## Engine and asset verification

The installed build's `main_menu/gfx/interface/advance/` established the
256x256, sRGBA, mipmapped DDS contract. Its `advances_tooltips.gui` uses
`GetAdvanceIcon` and applies the native circular icon mask, so the generated
masters retain a borderless, centered composition. An audit found the first,
second, third, and fifth identifiers as vanilla filenames, but no vanilla
`crown_power_advance_discovery.dds`; the exact M8 identifier is now supplied by
the mod rather than silently falling through.

`tools/m11_advance_icons.py --check` verifies the source/master/texture chain,
the 256x256 DDS contract, and exactly 50 uses of each identifier in the M8
tree. The masters were converted with DirectXTex BC7 and then decoded to a
five-panel round-trip review strip before the live smoke test.

Local basis: installed `advances_tooltips.gui`, installed
`main_menu/gfx/interface/advance/`, and the M8 tree. Design basis: master plan
sections 15 and 20.
