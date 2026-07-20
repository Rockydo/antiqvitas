# M11 Buddhism at the Han Court illustration

## Asset and scope

The retained source is
`assets_queue/generated_sources/antq_buddhism_han_court_source.png`; its exact
1080x440 derivative is
`assets_queue/generated/antq_buddhism_han_court_1080x440.png`. The game-facing
BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_buddhism_han_court.dds`.

The text-free image is a generic early-Eastern-Han scholarly courtyard: a
timber hall, tiled roof, bamboo, and a desk holding unmarked bamboo slips. It
identifies no capital, palace, emperor, envoy, monk, temple, text, doctrine,
conversion, journey, or outcome. Review excluded people, animals, Buddhas,
idols, pagodas, religious emblems, ceremony, later dynastic architecture,
modern material, labels, logos, and readable writing.

## Engine verification

`EVENT_IMAGES` in `tools/m10_history.py` owns the `antq_m10.1018` image link.
The texture follows the inspected 1080x440 BC7 country-event form, was
round-tripped to PNG for visual review, and passed `make validate` plus
enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.3, 9, 11, and 20; local EU5
country-event image contract.
