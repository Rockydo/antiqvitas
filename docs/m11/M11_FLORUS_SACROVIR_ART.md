# M11 Florus and Sacrovir illustration

## Asset and scope

The retained source is
`assets_queue/generated_sources/antq_florus_sacrovir_source.png`; its exact
1080x440 derivative is
`assets_queue/generated/antq_florus_sacrovir_1080x440.png`. The game-facing
BC7 DDS is
`main_menu/gfx/interface/illustrations/event/antq_florus_sacrovir.dds`.

The text-free image shows a generic first-century Gallic river quay, modest
bridge, cargo boats, fields, and non-identifying travellers. It does not
identify Florus, Sacrovir, a tribe, a city, a Roman unit, a route, battle, or
outcome. Review excluded combat, casualties, medieval castles or boats, later
Roman monumental architecture, modern material, flags, logos, and readable
writing.

## Engine verification

`EVENT_IMAGES` in `tools/m10_history.py` owns the `antq_m10.1007` image link.
The texture follows the inspected 1080x440 BC7 country-event form, was
round-tripped to PNG for visual review, and passed `make validate` plus
enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 8.1, 9, and 20; local EU5
country-event image contract.
