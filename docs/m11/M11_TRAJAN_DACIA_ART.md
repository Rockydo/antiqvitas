# M11 Trajan's Dacian Wars illustration

## Asset and scope

The retained source is
`assets_queue/generated_sources/antq_trajan_dacia_source.png`; its exact
1080x440 derivative is `assets_queue/generated/antq_trajan_dacia_1080x440.png`.
The game-facing BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_trajan_dacia.dds`.

The text-free image is deliberately non-literal Danube–Carpathian environmental
context: a calm wooded river bend, pebbled bank, willows, weathered stone, and
distant forested foothills. It identifies no war, annexation, commander,
crossing, route, bridge, capital, Roman or Dacian material, person, animal,
action, date, or outcome. Review excluded people, boats, roads, forts, walls,
settlements, military material, later infrastructure, readable writing, labels,
and logos.

## Engine verification

`EVENT_IMAGES` in `tools/m10_second_century.py` owns the
`antq_m10_second.2001` image link. The texture follows the inspected 1080x440
BC7 country-event form, was round-tripped to PNG for visual review, and passed
`make validate` plus enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.1, 9, and 20; local EU5
country-event image contract.
