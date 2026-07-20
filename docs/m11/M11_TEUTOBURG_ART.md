# M11 Teutoburg Forest illustration

## Asset and scope

The retained source is `assets_queue/generated_sources/antq_teutoburg_source.png`;
its exact 1080x440 derivative is
`assets_queue/generated/antq_teutoburg_1080x440.png`. The game-facing BC7 DDS
is `main_menu/gfx/interface/illustrations/event/antq_teutoburg.dds`.

The text-free image shows a small early-imperial Roman baggage party moving
through a rain-damp oak forest. It depicts no combat, casualties, named person,
Germanic group, banner, exact route, ambush, or battlefield. Review excluded
later Roman frontier architecture or monuments, medieval armour, modern
material, logos, and readable writing.

## Engine verification

`EVENT_IMAGES` in `tools/m10_history.py` owns the `antq_m10.1003` image link.
The texture follows the inspected 1080x440 BC7 country-event form, was
round-tripped to PNG for visual review, and passed `make validate` plus
enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.1, 9, and 20; local EU5
country-event image contract.
