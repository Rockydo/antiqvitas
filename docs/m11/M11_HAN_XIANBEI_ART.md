# M11 Han-Xianbei War illustration

## Asset and scope

The retained source is
`assets_queue/generated_sources/antq_han_xianbei_source.png`; its exact
1080x440 derivative is `assets_queue/generated/antq_han_xianbei_1080x440.png`.
The game-facing BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_han_xianbei.dds`.

The text-free image is deliberately non-literal northern grassland
environmental context: wind-brushed tawny grass, a shallow reed-fringed
watercourse, weathered stones, and distant low hills. It identifies no war,
migration, alliance, group, site, boundary, person, animal, Han or Xianbei
material, action, date, or outcome. Review excluded people, horses, armies,
camps, carts, fences, walls, forts, later steppe material, readable writing,
labels, and logos.

## Engine verification

`EVENT_IMAGES` in `tools/m10_history.py` owns the `antq_m10.1027` image link.
The texture follows the inspected 1080x440 BC7 country-event form, was
round-tripped to PNG for visual review, and passed `make validate` plus
enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.1, 9, and 20; local EU5
country-event image contract.
