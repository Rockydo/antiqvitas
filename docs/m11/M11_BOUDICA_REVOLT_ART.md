# M11 Boudica's Revolt illustration

## Asset and scope

The retained source is
`assets_queue/generated_sources/antq_boudica_revolt_source.png`; its exact
1080x440 derivative is `assets_queue/generated/antq_boudica_revolt_1080x440.png`.
The game-facing BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_boudica_revolt.dds`.

The text-free image is a generic eastern-British lowland with stream, bracken,
meadow, oak, and distant hills. It identifies no Boudica, tribe, town, Roman
unit, route, battle, action, or outcome. Review excluded people, chariots,
weapons, settlement, roads, forts, conflict, later material, flags, logos, and
readable writing.

## Engine verification

`EVENT_IMAGES` in `tools/m10_history.py` owns the `antq_m10.1016` image link.
The texture follows the inspected 1080x440 BC7 country-event form, was
round-tripped to PNG for visual review, and passed `make validate` plus
enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.7, 9, and 20; local EU5
country-event image contract.
