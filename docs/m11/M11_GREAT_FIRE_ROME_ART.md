# M11 Great Fire of Rome illustration

## Asset and scope

The retained source is
`assets_queue/generated_sources/antq_great_fire_rome_source.png`; its exact
1080x440 derivative is `assets_queue/generated/antq_great_fire_rome_1080x440.png`.
The game-facing BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_great_fire_rome.dds`.

The text-free image is a non-literal early-imperial cityscape at dusk: modest
plaster-and-brick buildings and tiled roofs frame an empty street, while a
small distant smoke column and firelight signal an urban emergency. It names no
neighbourhood, monument, emperor, official, cause, response, victim, action,
course, or outcome. Review excluded people, corpses, soldiers, animals,
specific later monuments (including the Colosseum), religious spectacle,
fantasy architecture, modern material, labels, logos, and readable writing.

## Engine verification

`EVENT_IMAGES` in `tools/m10_history.py` owns the `antq_m10.1017` image link.
The texture follows the inspected 1080x440 BC7 country-event form, was
round-tripped to PNG for visual review, and passed `make validate` plus
enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.1, 9, and 20; local EU5
country-event image contract.
