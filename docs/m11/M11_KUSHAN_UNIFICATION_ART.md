# M11 Kushan Unification illustration

## Asset and scope

The retained source is
`assets_queue/generated_sources/antq_kushan_unification_source.png`; its exact
1080x440 derivative is
`assets_queue/generated/antq_kushan_unification_1080x440.png`. The game-facing
BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_kushan_unification.dds`.

The text-free image shows a generic Central Asian caravan-and-riders gathering
in a broad mountain valley. It does not identify Kujula Kadphises, an oath,
coin, particular Yuezhi group, site, camp, accession, or territorial outcome.
Review excluded later Buddhist monuments, Sasanian, Mongol, Islamic, medieval,
and modern material, plus combat, logos, and readable writing.

## Engine verification

`EVENT_IMAGES` in `tools/m10_history.py` owns the `antq_m10.1008` image link.
The texture follows the inspected 1080x440 BC7 country-event form, was
round-tripped to PNG for visual review, and passed `make validate` plus
enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.4, 9, and 20; local EU5
country-event image contract.
