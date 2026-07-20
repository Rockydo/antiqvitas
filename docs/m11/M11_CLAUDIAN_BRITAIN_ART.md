# M11 Claudian Britain illustration

## Asset and scope

The retained source is
`assets_queue/generated_sources/antq_claudian_britain_source.png`; its exact
1080x440 derivative is `assets_queue/generated/antq_claudian_britain_1080x440.png`.
The game-facing BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_claudian_britain.dds`.

The text-free image is a generic southern British Channel coast with chalk
cliffs, grassy headlands, sea, and seabirds. It identifies no landing place,
commander, British polity, Roman unit, ship, city, fort, battle, or outcome.
Review excluded people, landing imagery, combat, casualties, later buildings,
flags, logos, and readable writing.

## Engine verification

`EVENT_IMAGES` in `tools/m10_history.py` owns the `antq_m10.1012` image link.
The texture follows the inspected 1080x440 BC7 country-event form, was
round-tripped to PNG for visual review, and passed `make validate` plus
enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.7, 9, and 20; local EU5
country-event image contract.
