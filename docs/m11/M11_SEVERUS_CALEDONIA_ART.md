# M11 Severus in Caledonia illustration

The retained source is `assets_queue/generated_sources/antq_severus_caledonia_source.png`;
the 1080x440 master is `assets_queue/generated/antq_severus_caledonia_1080x440.png`;
the game-facing BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_severus_caledonia.dds`.

The text-free image is generic northern Caledonian upland context: an
unoccupied natural burn, heather moor, rough stone, scattered birches, and low
cloud over distant ridges. It identifies no person, Severus, campaign, polity,
fort, wall, settlement, road, date, or outcome. It is not a reconstruction of
Severus' campaign in Caledonia.

`EVENT_IMAGES` in `tools/m10_third_century.py` owns the
`antq_m10_third.3000` link. The inspected 1080x440 BC7 texture passed
`make validate` and enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.7, 9, and 20; local EU5
country-event image contract.
