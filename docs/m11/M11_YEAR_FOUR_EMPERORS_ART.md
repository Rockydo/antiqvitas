# M11 Year of the Four Emperors illustration

## Asset and scope

The retained source is
`assets_queue/generated_sources/antq_year_four_emperors_source.png`; its exact
1080x440 derivative is
`assets_queue/generated/antq_year_four_emperors_1080x440.png`. The game-facing
BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_year_four_emperors.dds`.

The text-free image is a generic early-imperial civic square after rainfall:
rain-wet paving, a simple covered portico, tiled roofs, closed shutters, and
distant low buildings. It identifies no claimant, ruler, legion, institution,
specific forum, monument, battle, action, chronology, or outcome. Review
excluded people, soldiers, animals, weapons, standards, portraits, crowns,
political symbols, fire, destruction, late architecture, labels, logos, and
readable writing.

## Engine verification

`EVENT_IMAGES` in `tools/m10_history.py` owns the `antq_m10.1021` image link.
The texture follows the inspected 1080x440 BC7 country-event form, was
round-tripped to PNG for visual review, and passed `make validate` plus
enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.1, 9, and 20; local EU5
country-event image contract.
