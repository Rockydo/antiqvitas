# M11 Batavian Revolt illustration

## Asset and scope

The retained source is
`assets_queue/generated_sources/antq_batavian_revolt_source.png`; its exact
1080x440 derivative is
`assets_queue/generated/antq_batavian_revolt_1080x440.png`. The game-facing
BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_batavian_revolt.dds`.

The text-free image is a generic Lower Rhine wetland in early autumn: a broad
slow river branch, reed beds, willow and alder, low grassy islands, a grey
horizon, and a faint muddy track. It identifies no Civilis, Batavian group,
army, fort, boat, settlement, campaign, battle, action, or outcome. Review
excluded people, soldiers, animals, boats, weapons, standards, roads, bridges,
destruction, later Dutch material, labels, logos, and readable writing.

## Engine verification

`EVENT_IMAGES` in `tools/m10_history.py` owns the `antq_m10.1022` image link.
The texture follows the inspected 1080x440 BC7 country-event form, was
round-tripped to PNG for visual review, and passed `make validate` plus
enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.1, 9, and 20; local EU5
country-event image contract.
