# M11 Three Kingdoms illustration

The retained source is `assets_queue/generated_sources/antq_three_kingdoms_source.png`;
the 1080x440 master is `assets_queue/generated/antq_three_kingdoms_1080x440.png`;
the game-facing BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_three_kingdoms.dds`.

The text-free image is generic late-summer north-Chinese river-valley context:
an unoccupied natural river, wooded low hills, reeds, pale stone, willows, and
distant mist. It identifies no ruler, court, partition, battle, polity, city,
palace, date, or outcome. It is not a reconstruction of the Han abdication, the
Three Kingdoms, or Jin reunification.

`EVENT_IMAGES` in `tools/m10_third_century.py` owns the
`antq_m10_third.3003` link. The inspected 1080x440 BC7 texture passed
`make validate` and enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.3, 9, 17.3, and 20; local EU5
country-event image contract.
