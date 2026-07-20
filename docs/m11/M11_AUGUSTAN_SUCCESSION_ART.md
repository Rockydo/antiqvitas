# M11 Augustan Succession illustration

## Asset and scope

The retained master is
`assets_queue/generated_sources/antq_augustan_succession_source.png`; its
1080x440 derivative and the game-facing BC7 DDS are retained under
`assets_queue/generated/` and
`main_menu/gfx/interface/illustrations/event/` respectively.

The scene is a generic AD 14 early-imperial Roman civic gathering. It does not
identify Augustus, Tiberius, a funeral, a proclamation, or a specific Forum
view. The review excludes legible text, later monuments, modern or medieval
material, battle imagery, and anachronistic imperial symbols.

## Engine verification

The first-century M10 renderer owns the `antq_m10.1005` texture reference. The
DDS uses the inspected 1080x440 BC7 event form, was round-tripped to PNG for
review, and passed `make validate` plus enabled-mod `make smoke` with zero new
error-log lines.

Sources: ANTIQVITAS master plan sections 8.1, 9, and 20; local EU5
country-event image contract.
