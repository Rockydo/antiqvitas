# M11 Antonine Wall illustration

The retained source is `assets_queue/generated_sources/antq_antonine_wall_source.png`;
the 1080x440 master is `assets_queue/generated/antq_antonine_wall_1080x440.png`;
the game-facing BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_antonine_wall.dds`.

The text-free image is generic northern-British moorland context: empty heather,
rough grass, weathered boulders, a natural burn, and distant soft hills. It
identifies no wall, fort, ditch, worker, road, Roman material, construction,
person, date, or outcome. It is not a reconstruction of the Antonine Wall.

`EVENT_IMAGES` in `tools/m10_second_century.py` owns the
`antq_m10_second.2008` link. The inspected 1080x440 BC7 texture passed
`make validate` and enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.1, 9, and 20; local EU5
country-event image contract.
