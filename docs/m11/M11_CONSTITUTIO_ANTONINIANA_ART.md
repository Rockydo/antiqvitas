# M11 Constitutio Antoniniana illustration

The retained source is `assets_queue/generated_sources/antq_constitutio_antoniniana_source.png`;
the 1080x440 master is `assets_queue/generated/antq_constitutio_antoniniana_1080x440.png`;
the game-facing BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_constitutio_antoniniana.dds`.

The text-free image is generic Roman civic context: an unoccupied municipal
colonnade, pale paving, plain fountain basin, plane trees, and low rooflines.
It identifies no edict, inscription, ruler, official, legal act, place, date,
or outcome. It is not a reconstruction of the Constitutio Antoniniana.

`EVENT_IMAGES` in `tools/m10_third_century.py` owns the
`antq_m10_third.3001` link. The inspected 1080x440 BC7 texture passed
`make validate` and enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.1, 9, 13, and 20; local EU5
country-event image contract.
