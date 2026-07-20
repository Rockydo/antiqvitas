# M11 Christianity-founded illustration

## Asset and scope

The retained source is
`assets_queue/generated_sources/antq_christianity_foundation_source.png`; its
exact 1080x440 derivative is
`assets_queue/generated/antq_christianity_foundation_1080x440.png`. The
game-facing BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_christianity_foundation.dds`.

The text-free image is a generic first-century Judean hill landscape with olive
trees, terraces, and non-identifying travellers. It depicts no sacred figure,
sacred event, religious emblem, ritual, city, temple, or theological claim. The
landscape-only treatment is contextual rather than devotional or a literal
reconstruction. Review excluded crosses, crucifixion imagery, halos, miracles,
later church architecture, medieval and modern material, flags, logos, and
readable writing.

## Engine verification

`EVENT_IMAGES` in `tools/m10_history.py` owns the `antq_m10.1009` image link.
The texture follows the inspected 1080x440 BC7 country-event form, was
round-tripped to PNG for visual review, and passed `make validate` plus
enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.1, 9, and 20; local EU5
country-event image contract.
