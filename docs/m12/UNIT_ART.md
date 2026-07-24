# M12 ancient unit illustrations

The active allowlist has 44 units. Eleven generated four-up regional sheets
yield 44 unique square masters, 44 three-frame recruitment strips, and 44 direct
masks. `docs/m12/unit_art_ledger.csv` records every source-to-texture chain;
`unit_art_contact_sheet.png` is the review surface.

Installed `00_naming_convention.info` resolves
`[unit_category]_[unit_type]` before age, culture, gfx, or default art. The mod
therefore owns that exact 1080x440 DXT1 path and mask for every active key.
Each strip repeats its subject across the installed three-frame grid; black
masks prevent invented country-colour livery. No active unit uses `_default`,
another unit's texture, or a medieval/firearm image.

Generation used extracted EU5 infantry, cavalry, East Asian, Middle Eastern,
and naval illustrations as direct style references. Subjects were constrained
by the M7 historical ledger and generated four at a time; the source sheets and
unmodified style references remain under `assets_queue/`. The selected set was
reviewed for text, heraldry, firearms, plate armour, stirrups, pseudo-writing,
crop safety, regional equipment, and duplicated images.

`tools/m12_unit_art.py --check` binds the art set to the quarantine allowlist,
requires 11 four-up sources and 44 unique direct texture hashes, and verifies
every PNG/DDS dimension, mask, ledger row, and contact sheet.

Sources: master plan sections 14 and 20; installed EU5
`main_menu/gfx/interface/illustrations/units/00_naming_convention.info`;
`docs/m7/units.csv`.
