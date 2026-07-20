# M11 Illyrian Revolt illustration

## Asset and scope

The retained source is
`assets_queue/generated_sources/antq_illyrian_revolt_source.png`; its exact
1080x440 derivative is
`assets_queue/generated/antq_illyrian_revolt_1080x440.png`. The game-facing
BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_illyrian_revolt.dds`.

The text-free illustration shows a generic early-imperial Roman column and
pack animals moving through a rocky Balkan pass. It does not identify a named
commander, local people, pass, engagement, route, or campaign outcome. Review
excluded combat, gore, later Roman frontier architecture or monuments,
medieval armour, modern material, logos, and readable writing.

## Engine verification

`EVENT_IMAGES` in `tools/m10_history.py` owns the `antq_m10.1002` image link.
The texture follows the inspected 1080x440 BC7 country-event form, was
round-tripped to PNG for visual review, and passed `make validate` plus
enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.1, 9, and 20; local EU5
country-event image contract.
