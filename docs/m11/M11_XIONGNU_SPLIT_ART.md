# M11 Xiongnu Split illustration

## Asset and scope

The retained source is
`assets_queue/generated_sources/antq_xiongnu_split_source.png`; its exact
1080x440 derivative is `assets_queue/generated/antq_xiongnu_split_1080x440.png`.
The game-facing BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_xiongnu_split.dds`.

The text-free image is a generic eastern Eurasian steppe with pale grassland,
a braided stream, low stones, distant hills, and two unmarked tracks diverging
toward separate horizons. It identifies no chanyu, group, migration, army,
camp, route, boundary, alliance, battle, action, or outcome. Review excluded
people, horses, tents, carts, weapons, animals, banners, emblems, walls,
settlement, Mongol-era motifs, later material, labels, logos, and readable
writing.

## Engine verification

`EVENT_IMAGES` in `tools/m10_history.py` owns the `antq_m10.1013` image link.
The texture follows the inspected 1080x440 BC7 country-event form, was
round-tripped to PNG for visual review, and passed `make validate` plus
enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.3, 9, and 20; local EU5
country-event image contract.
