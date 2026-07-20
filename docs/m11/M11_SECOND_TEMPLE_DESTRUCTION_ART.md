# M11 Second Temple transformation illustration

## Asset and scope

The retained source is
`assets_queue/generated_sources/antq_second_temple_destruction_source.png`;
its exact 1080x440 derivative is
`assets_queue/generated/antq_second_temple_destruction_1080x440.png`. The
game-facing BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_second_temple_destruction.dds`.

The text-free image is deliberately non-literal Judean environmental context:
an unoccupied folded limestone valley with olive shrubs, low dry-stone
terraces, dry grass, and distant hazy ridges. It identifies no Temple,
Jerusalem, shrine, city, building, person, religious figure, symbol, ritual,
fire, violence, damage, archaeology, action, date, or outcome. Review
excluded destruction spectacle, historical reconstruction, readable writing,
labels, logos, and later or modern settlement material.

## Engine verification

`EVENT_IMAGES` in `tools/m10_history.py` owns the `antq_m10.1023` image link.
The texture follows the inspected 1080x440 BC7 country-event form, was
round-tripped to PNG for visual review, and passed `make validate` plus
enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.1, 9, 11, and 20; local EU5
country-event image contract.
