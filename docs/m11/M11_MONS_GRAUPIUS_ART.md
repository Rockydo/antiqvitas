# M11 Mons Graupius illustration

## Asset and scope

The retained source is
`assets_queue/generated_sources/antq_mons_graupius_source.png`; its exact
1080x440 derivative is `assets_queue/generated/antq_mons_graupius_1080x440.png`.
The game-facing BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_mons_graupius.dds`.

The text-free image is deliberately non-literal Caledonian environmental
context: empty heather and coarse grass across a low granite upland, with
shallow peaty ground, a weathered ridge, and mist-softened hills. It identifies
no battle, army, commander, route, site, fort, Roman material, Caledonian
group, person, animal, action, date, or outcome. Review excluded people,
horses, military material, settlement, roads, medieval or modern Scottish
imagery, readable writing, labels, and logos.

## Engine verification

`EVENT_IMAGES` in `tools/m10_history.py` owns the `antq_m10.1025` image link.
The texture follows the inspected 1080x440 BC7 country-event form, was
round-tripped to PNG for visual review, and passed `make validate` plus
enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.1, 9, and 20; local EU5
country-event image contract.
