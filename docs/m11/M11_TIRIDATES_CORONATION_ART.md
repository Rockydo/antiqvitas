# M11 Tiridates' Coronation illustration

## Asset and scope

The retained source is
`assets_queue/generated_sources/antq_tiridates_coronation_source.png`; its
exact 1080x440 derivative is
`assets_queue/generated/antq_tiridates_coronation_1080x440.png`. The
game-facing BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_tiridates_coronation.dds`.

The text-free image is a generic Armenian highland valley: a stone-paved road,
river, dry grass, sparse trees, and distant snow-streaked ridges frame an
indistinct hilltop enclosure. It identifies no coronation, Tiridates, Roman or
Armenian official, capital, palace, route, treaty, date, action, or outcome.
Review excluded people, soldiers, animals, crowns, flags, armies, religious
symbols, churches, temples, battle, ritual, later architecture, modern
material, labels, logos, and readable writing.

## Engine verification

`EVENT_IMAGES` in `tools/m10_history.py` owns the `antq_m10.1019` image link.
The texture follows the inspected 1080x440 BC7 country-event form, was
round-tripped to PNG for visual review, and passed `make validate` plus
enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.2, 9, and 20; local EU5
country-event image contract.
