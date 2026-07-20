# M11 Great Jewish Revolt illustration

## Asset and scope

The retained source is
`assets_queue/generated_sources/antq_great_jewish_revolt_source.png`; its exact
1080x440 derivative is
`assets_queue/generated/antq_great_jewish_revolt_1080x440.png`. The
game-facing BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_great_jewish_revolt.dds`.

The text-free image is a generic Judean hill landscape after light rain:
limestone terraces, low olive shrubs, a dry-stone retaining wall, a narrow
seasonal channel, and pale hills. It identifies no revolt participant, army,
town, Temple, synagogue, sacred figure, ritual, campaign, action, course, or
outcome. Review excluded people, soldiers, animals, weapons, camps,
settlements, religious symbols, destruction, later architecture, modern
material, labels, logos, and readable writing.

## Engine verification

`EVENT_IMAGES` in `tools/m10_history.py` owns the `antq_m10.1020` image link.
The texture follows the inspected 1080x440 BC7 country-event form, was
round-tripped to PNG for visual review, and passed `make validate` plus
enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.1, 9, 11, and 20; local EU5
country-event image contract.
