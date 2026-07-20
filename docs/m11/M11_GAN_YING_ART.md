# M11 Gan Ying's Mission illustration

## Asset and scope

The retained source is
`assets_queue/generated_sources/antq_gan_ying_source.png`; its exact 1080x440
derivative is `assets_queue/generated/antq_gan_ying_1080x440.png`. The
game-facing BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_gan_ying.dds`.

The text-free image is deliberately non-literal Persian Gulf environmental
context: pale rocky shoreline, calm blue-green water, salt-tolerant scrub, and
low dry hills. It identifies no traveler, ship, boat, port, route, destination,
Han, Roman, Persian material, person, action, date, or outcome. Review excluded
people, vessels, harbors, trade goods, buildings, maps, readable writing,
labels, logos, and modern shore development.

## Engine verification

`EVENT_IMAGES` in `tools/m10_second_century.py` owns the
`antq_m10_second.2000` image link. The texture follows the inspected 1080x440
BC7 country-event form, was round-tripped to PNG for visual review, and passed
`make validate` plus enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.2, 9, and 20; local EU5
country-event image contract.
