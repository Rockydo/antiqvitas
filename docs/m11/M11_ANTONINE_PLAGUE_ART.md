# M11 Antonine Plague illustration

The retained source is `assets_queue/generated_sources/antq_antonine_plague_source.png`;
the 1080x440 master is `assets_queue/generated/antq_antonine_plague_1080x440.png`;
the game-facing BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_antonine_plague.dds`.

The text-free image is generic Mediterranean upland context: empty dry meadow,
olive trees, weathered limestone, a natural spring channel, and distant low
hills. It identifies no person, illness, polity, settlement, medical material,
date, or outcome. It is not a reconstruction of the Antonine Plague.

`EVENT_IMAGES` in `tools/m10_second_century.py` owns the
`antq_m10_second.2012` link. The inspected 1080x440 BC7 texture passed
`make validate` and enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.1, 8.3, 9, and 20; local EU5
country-event image contract.
