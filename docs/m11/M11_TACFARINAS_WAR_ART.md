# M11 Tacfarinas' War illustration

## Asset and scope

The retained source is
`assets_queue/generated_sources/antq_tacfarinas_war_source.png`; its exact
1080x440 derivative is
`assets_queue/generated/antq_tacfarinas_war_1080x440.png`. The game-facing BC7
DDS is
`main_menu/gfx/interface/illustrations/event/antq_tacfarinas_war.dds`.

The text-free image shows a generic semi-arid North African landscape with a
small early-imperial patrol, modest roadside shelter, and distant mounted
travellers. It does not identify Tacfarinas, a tribe, a Roman unit, a site,
route, battle, or outcome. Review excluded combat, casualties, later Roman
stone fortification or monuments, medieval and modern material, flags, logos,
and readable writing.

## Engine verification

`EVENT_IMAGES` in `tools/m10_history.py` owns the `antq_m10.1006` image link.
The texture follows the inspected 1080x440 BC7 country-event form, was
round-tripped to PNG for visual review, and passed `make validate` plus
enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.1, 9, and 20; local EU5
country-event image contract.
