# M11 Trung Sisters' Revolt illustration

## Asset and scope

The retained source is
`assets_queue/generated_sources/antq_trung_sisters_source.png`; its exact
1080x440 derivative is `assets_queue/generated/antq_trung_sisters_1080x440.png`.
The game-facing BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_trung_sisters.dds`.

The text-free image is a generic Jiaozhi river-delta landscape only. It shows
no person, boat, building, artefact, named figure, or event action, and makes
no claim about the sisters' attire, weaponry, support, location, course, or
outcome. Review excluded later Vietnamese visual symbols, Chinese palace or
temple architecture, medieval and modern material, flags, logos, and writing.

## Engine verification

`EVENT_IMAGES` in `tools/m10_history.py` owns the `antq_m10.1010` image link.
The texture follows the inspected 1080x440 BC7 country-event form, was
round-tripped to PNG for visual review, and passed `make validate` plus
enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.3, 9, and 20; local EU5
country-event image contract.
