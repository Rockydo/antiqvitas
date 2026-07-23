# M11 selectable loading-screen collection

## Engine contract

EU5 has two distinct visual paths. The retained
`loading_screen/gfx/loadingscreens/startscreen.dds` replacement is the
hard-coded 1920x1080 startup splash. Normal loading screens instead use the
engine-provided `GetCurrentLoadingScreen` layered scene contract.

The installed scene file declares eleven selectable, engine-recognised scene
keys, each with eight illustration layers at 3840x2160. Those script files are
additive in this build, so ANTIQVITAS deliberately leaves the engine-owned
declarations alone. Instead it VFS-overrides the exact vanilla DDS paths below
`loading_screen/gfx/loading_screen_assets/00/images/`. Every inherited layer
therefore resolves to its assigned reviewed panorama and no random vanilla
scene can appear.

`tools/m11_loading_screens.py` owns the VFS texture links, validates all
masters and DDS contracts, and renders the review sheet
`docs/m11/loading_screens_contact_sheet.png`. Its eight source PNGs and exact
3840x2160 review masters are retained under `assets_queue/`; its eight
game-facing DDS files use the inspected vanilla 3840x2160 BC1/sRGB class with
mipmaps.

## Reviewed scenes

| Scene | Period and visual boundary |
| --- | --- |
| Ostia | AD 1 port labour and cargo shipping; not Trajan's later harbour. |
| Augustan Forum | Rome AD 1; no Colosseum, Trajanic forum, or Christian fabric. |
| Alexandria | AD 1 Great Harbour trade and the already-standing Pharos. |
| Chang'an | AD 1 Han granary and administrative-market scene; no Tang architecture. |
| Meroë | AD 1 Kushite riverine ironworking and trade; not a generic pharaonic scene. |
| Lower Rhine | AD 1 Germanic riverside settlement and Roman-border exchange; no Viking imagery. |
| Teotihuacan | c. AD 100 urban construction and obsidian work; no Aztec or contact-period elements. |
| Campus Martius | Rome AD 1 civic water infrastructure and Agrippan public-building setting; no Hadrianic Pantheon dome. |

The unreleased Ctesiphon and Petra drafts remain only as untracked source
experiments. They are deliberately absent from every declaration, derivative,
and ledger because their visual vocabulary was not sufficiently period-specific.

## Sources and scope

The images are evocative loading illustrations, not archaeological
reconstructions or claims about exact street plans, costumes, workforce sizes,
or specific buildings beyond the deliberately bounded anchors above. Historical
scope and links are recorded in `docs/ASSUMPTIONS.md`.

## Verification

The local game contract was inspected before implementation:

- `game/loading_screen/gui/loading_screen.gui` obtains the scene through
  `GetCurrentLoadingScreen`.
- `game/loading_screen/gfx/scenes/00_loading_screens.txt` supplies its eleven
  selectable scene definitions.
- `game/loading_screen/gfx/images/*.txt` supplies eight texture layers per
  definition.

`tools/m11_loading_screens.py --check` verifies eight reviewed 3840x2160 PNG
masters, eight canonical 3840x2160 DDS textures, the 88 inherited VFS texture
overrides, and assignments for all eleven installed selectable scenes. It is part of
`make validate`; menu smoke remains the runtime check.
