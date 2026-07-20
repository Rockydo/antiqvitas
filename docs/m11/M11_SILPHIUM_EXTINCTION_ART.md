# M11 Silphium Extinction illustration

## Asset and scope

The retained source is
`assets_queue/generated_sources/antq_silphium_extinction_source.png`; its exact
1080x440 derivative is
`assets_queue/generated/antq_silphium_extinction_1080x440.png`. The
game-facing BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_silphium_extinction.dds`.

The text-free image is a generic Cyrenaican limestone upland above the
Mediterranean: low scrub, sun-bleached stones, wind-bent grass, tiny
unidentified wildflowers, distant sea, and haze. It identifies no silphium
specimen, field, crop, harvest, trade, town, port, person, date, mechanism, or
outcome. Review excluded named plants, botanical diagrams, fantasy flowers,
silphium symbols, farming, animals, ruins, later material, labels, logos, and
readable writing.

## Engine verification

`EVENT_IMAGES` in `tools/m10_history.py` owns the `antq_m10.1014` image link.
The texture follows the inspected 1080x440 BC7 country-event form, was
round-tripped to PNG for visual review, and passed `make validate` plus
enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.5, 9, 12.1, and 20; local EU5
country-event image contract.
