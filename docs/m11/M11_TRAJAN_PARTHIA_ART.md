# M11 Trajan's Parthian War illustration

## Asset and scope

The retained source is
`assets_queue/generated_sources/antq_trajan_parthia_source.png`; its exact
1080x440 derivative is
`assets_queue/generated/antq_trajan_parthia_1080x440.png`. The game-facing BC7
DDS is `main_menu/gfx/interface/illustrations/event/antq_trajan_parthia.dds`.

The text-free image is deliberately non-literal Mesopotamian environmental
context: a slow broad river, reed fringe, dry alluvial earth, sparse scrub, and
distant low brown hills. It identifies no war, siege, campaign, revolt,
commander, city, route, boundary, Roman or Parthian material, person, animal,
action, date, or outcome. Review excluded people, military material, boats,
bridges, roads, forts, walls, cities, irrigation works, readable writing,
labels, and logos.

## Engine verification

`EVENT_IMAGES` in `tools/m10_second_century.py` owns the
`antq_m10_second.2003` image link. The texture follows the inspected 1080x440
BC7 country-event form, was round-tripped to PNG for visual review, and passed
`make validate` plus enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.2, 9, and 20; WIL-TPW; IRAN-TRAJ;
local EU5 country-event image contract.
