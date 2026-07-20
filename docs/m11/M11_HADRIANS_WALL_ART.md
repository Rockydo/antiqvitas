# M11 Hadrian's Wall illustration

The retained source is `assets_queue/generated_sources/antq_hadrians_wall_source.png`;
the 1080x440 master is `assets_queue/generated/antq_hadrians_wall_1080x440.png`;
the game-facing BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_hadrians_wall.dds`.

The text-free image is generic northern-British upland context: empty heather,
grass, stone, a shallow beck, and distant hills. It identifies no wall, fort,
worker, road, Roman material, construction, person, date, or outcome. It is not
a reconstruction of Hadrian's Wall.

`EVENT_IMAGES` in `tools/m10_second_century.py` owns the
`antq_m10_second.2005` link. The inspected 1080x440 BC7 texture passed
`make validate` and enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.1, 9, and 20; local EU5
country-event image contract.
