# M11 Mauretania Annexation illustration

## Asset and scope

The retained source is
`assets_queue/generated_sources/antq_mauretania_annexation_source.png`; its
exact 1080x440 derivative is
`assets_queue/generated/antq_mauretania_annexation_1080x440.png`. The
game-facing BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_mauretania_annexation.dds`.

The text-free image shows a generic Mauretanian coastal-upland landscape with
olive groves, a track, and an indistinct roadside structure. It identifies no
person, city, ruler, Roman unit, exact fort, annexation act, revolt, campaign,
or outcome. Review excluded people, combat, casualties, triumphal monuments,
medieval and modern material, flags, logos, and readable writing.

## Engine verification

`EVENT_IMAGES` in `tools/m10_history.py` owns the `antq_m10.1011` image link.
The texture follows the inspected 1080x440 BC7 country-event form, was
round-tripped to PNG for visual review, and passed `make validate` plus
enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.1, 9, and 20; local EU5
country-event image contract.
