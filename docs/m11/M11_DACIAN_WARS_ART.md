# M11 Dacian Wars illustration

## Asset and scope

The retained source is
`assets_queue/generated_sources/antq_dacian_wars_source.png`; its exact
1080x440 derivative is `assets_queue/generated/antq_dacian_wars_1080x440.png`.
The game-facing BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_dacian_wars.dds`.

The text-free image is deliberately non-literal Carpathian environmental
context: mixed autumn woodland, rounded rock outcrops, a small clear stream,
an open valley, and distant blue foothills. It identifies no war, battle,
commander, capital, route, fortification, Roman or Dacian material, person,
animal, action, date, or outcome. Review excluded people, military material,
settlement, roads, later architecture, readable writing, labels, and logos.

## Engine verification

`EVENT_IMAGES` in `tools/m10_history.py` owns the `antq_m10.1026` image link.
The texture follows the inspected 1080x440 BC7 country-event form, was
round-tripped to PNG for visual review, and passed `make validate` plus
enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.1, 9, and 20; local EU5
country-event image contract.
