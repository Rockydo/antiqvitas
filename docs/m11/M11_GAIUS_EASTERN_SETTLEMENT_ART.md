# M11 Gaius Caesar eastern-settlement illustration

## Asset and scope

`assets_queue/generated_sources/antq_gaius_eastern_settlement_source.png` is
the retained source, with an exact 1080×440 derivative in
`assets_queue/generated/`. The game-facing BC7 texture is
`main_menu/gfx/interface/illustrations/event/antq_gaius_eastern_settlement.dds`.

The text-free illustration shows generic Roman and Parthian diplomatic parties
in an Armenian highland setting. It is deliberately not a portrait of Gaius,
an identified ruler, a treaty text, a coronation, a named frontier, or a fixed
settlement outcome. Review excluded later Sasanian/Byzantine regalia, modern
or medieval material, battle imagery, and readable text.

## Engine verification

`EVENT_IMAGES` in `tools/m10_history.py` owns the `antq_m10.1000` image link.
The art follows the inspected 1080×440 BC7 event texture contract, was
round-tripped to PNG for visual review, and passed `make validate` plus
enabled-mod `make smoke` with zero new error-log lines.

Sources: ANTIQVITAS master plan §§8.1, 9, and 20; local EU5 country-event
image contract.
