# M11 Antioch earthquake illustration

## Asset and scope

The retained source is
`assets_queue/generated_sources/antq_antioch_earthquake_source.png`; its exact
1080x440 derivative is
`assets_queue/generated/antq_antioch_earthquake_1080x440.png`. The game-facing
BC7 DDS is `main_menu/gfx/interface/illustrations/event/antq_antioch_earthquake.dds`.

The text-free image is deliberately non-literal Orontes-valley environmental
context: a narrow calm river between pale limestone slopes, riparian trees,
reeds, dry grass, and distant hills. It identifies no earthquake, city,
Antioch, building, ruin, victim, person, action, date, or outcome. Review
excluded settlement, debris, cracks, collapse, smoke, fire, disaster spectacle,
readable writing, labels, and logos.

## Engine verification

`EVENT_IMAGES` in `tools/m10_second_century.py` owns the
`antq_m10_second.2004` image link. The texture follows the inspected 1080x440
BC7 country-event form, was round-tripped to PNG for visual review, and passed
`make validate` plus enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.1, 9, and 20; local EU5
country-event image contract.
