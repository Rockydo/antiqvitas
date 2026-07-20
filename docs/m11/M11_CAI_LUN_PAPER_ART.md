# M11 paper-standardization illustration

## Asset and scope

The retained source is
`assets_queue/generated_sources/antq_cai_lun_paper_source.png`; its exact
1080x440 derivative is `assets_queue/generated/antq_cai_lun_paper_1080x440.png`.
The game-facing BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_cai_lun_paper.dds`.

The text-free image is deliberately non-literal Eastern Han scholarly-material
context: an unoccupied timber workspace opening onto bamboo, blank pale fiber
sheets, unmarked bamboo slips, a plain ceramic bowl, and a brush holder. It
identifies no person, official, inventor, workshop, technique, process,
inscription, text, date, or outcome. Review excluded people, hands, readable
writing, calligraphy, books, scrolls, seals, banners, maps, papermaking vats,
and later printing or modern material.

## Engine verification

`EVENT_IMAGES` in `tools/m10_second_century.py` owns the
`antq_m10_second.2002` image link. The texture follows the inspected 1080x440
BC7 country-event form, was round-tripped to PNG for visual review, and passed
`make validate` plus enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.3, 9, and 20; SMI-CAI; local EU5
country-event image contract.
