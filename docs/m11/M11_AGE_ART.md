# M11 age illustrations

The advance interface resolves its age banner through the five exact filenames
below. These replacements use a common 1080x440 BC7 DDS contract and retain a
reviewed generation source plus fixed-size PNG master on the work drive.

| Age key | Display age | Retained source | Engine master | Game-facing replacement |
| --- | --- | --- | --- | --- |
| `age_1_traditions` | Principate | `antq_age_principate_source.png` | `antq_age_principate_1080x440.png` | `age_1_traditions.dds` |
| `age_2_renaissance` | High Empires | `antq_age_high_empires_source_v2.png` | `antq_age_high_empires_1080x440.png` | `age_2_renaissance.dds` |
| `age_3_discovery` | Crisis | `antq_age_crisis_source.png` | `antq_age_crisis_1080x440.png` | `age_3_discovery.dds` |
| `age_4_reformation` | Dominate | `antq_age_dominate_source.png` | `antq_age_dominate_1080x440.png` | `age_4_reformation.dds` |
| `age_5_absolutism` | Migrations | `antq_age_migrations_source.png` | `antq_age_migrations_1080x440.png` | `age_5_absolutism.dds` |

The source and master paths in the table are rooted respectively at
`assets_queue/generated_sources/` and `assets_queue/generated/`. The final
column is rooted at
`main_menu/gfx/interface/illustrations/advances/`.

## Scope and review

The panels are intentionally broad visual frames rather than reconstructions:
Principate uses a generic civic/coastal exchange scene; High Empires a generic
oasis-caravan landscape; Crisis a storm-darkened frontier road; Dominate a
fortified river-city landscape; and Migrations a civilian river-crossing
landscape. They identify no named city, ruler, people, battle, religion,
campaign, or political outcome. The High Empires source was regenerated before
selection to remove a skyline that read as later architecture.

Each selected master and its DDS round trip were inspected as a five-panel
contact sheet for framing, readable text, watermarks, anachronistic landmarks,
and clipping. All selected panels are text-free.

## Technical verification

The local advance view binds its banner texture through
`AdvancesLateralView.GetAgeIllustration`; the installed asset inventory shows
the five corresponding `1080x440` vanilla paths. Each replacement was resized
to that exact dimension, converted with DirectXTex to BC7 sRGB with mipmaps,
and checked with `tools/dds.py`.

`tools/m11_age_art.py --check`, included in `make validate`, requires every
retained source, PNG master, and exact game-facing DDS to exist. It validates
the five active campaign age keys and their DDS dimensions. The sixth vanilla
age remains untouched because it begins after ANTIQVITAS's end date.

Sources: ANTIQVITAS master plan sections 15 and 20; local EU5 advance-view UI
and asset inventory.
