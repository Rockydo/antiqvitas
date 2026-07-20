# M11 Vesuvius illustration

## Asset and scope

The retained source is
`assets_queue/generated_sources/antq_vesuvius_source.png`; its exact 1080x440
derivative is `assets_queue/generated/antq_vesuvius_1080x440.png`. The
game-facing BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_vesuvius.dds`.

The text-free image is deliberately non-literal Campanian environmental
context: a dark volcanic mountain beyond low vine rows, dry grass, stone field
walls, and distant Mediterranean water. It identifies no eruption, plume,
Pompeii, Herculaneum, town, villa, person, animal, victim, fire, lava, ash,
damage, action, date, or outcome. Review excluded disaster spectacle,
destruction, archaeological reconstruction, readable writing, labels, logos,
and later or modern settlement material.

## Engine verification

`EVENT_IMAGES` in `tools/m10_history.py` owns the `antq_m10.1024` image link.
The texture follows the inspected 1080x440 BC7 country-event form, was
round-tripped to PNG for visual review, and passed `make validate` plus
enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.1, 9, and 20; local EU5
country-event image contract.
