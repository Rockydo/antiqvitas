# M11 Rome-Parthia War over Armenia illustration

## Asset and scope

The retained source is
`assets_queue/generated_sources/antq_armenian_war_source.png`; its exact
1080x440 derivative is `assets_queue/generated/antq_armenian_war_1080x440.png`.
The game-facing BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_armenian_war.dds`.

The text-free image is a generic late-autumn Armenian mountain gorge: a narrow
stone-and-earth track beside a turbulent stream, bare slopes, basalt outcrops,
and misted distant ridges. It identifies no battle, commander, army, camp,
capital, route, treaty, boundary, date, action, or outcome. Review excluded
people, soldiers, horses, animals, weapons, standards, settlements, crowns,
religious emblems, later architecture, modern material, labels, logos, and
readable writing.

## Engine verification

`EVENT_IMAGES` in `tools/m10_history.py` owns the `antq_m10.1015` image link.
The texture follows the inspected 1080x440 BC7 country-event form, was
round-tripped to PNG for visual review, and passed `make validate` plus
enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.2, 9, and 20; local EU5
country-event image contract.
