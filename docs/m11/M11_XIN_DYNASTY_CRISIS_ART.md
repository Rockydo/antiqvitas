# M11 Xin Dynasty Crisis illustration

## Asset and scope

The retained master is
`assets_queue/generated_sources/antq_xin_dynasty_crisis_source.png`; its
1080×440 derivative and the game-facing BC7 DDS are retained under
`assets_queue/generated/` and
`main_menu/gfx/interface/illustrations/event/` respectively.

The scene is a generic AD 9 court-transition setting at Chang'an. It does not
identify Wang Mang, an emperor, a proclamation, a literal document, or a
specific palace room. The review excludes legible text, later dynastic costume,
modern imagery, battle, and anachronistic imperial symbols.

## Engine verification

The first-century M10 renderer owns the `antq_m10.1004` texture reference. The
DDS uses the inspected 1080×440 BC7 event form, was round-tripped to PNG for
review, and passed `make validate` plus enabled-mod `make smoke` with zero new
error-log lines.

Sources: ANTIQVITAS master plan §§8.3, 9, and 20; local EU5 country-event
image contract.
