# M11 AD 1 Rome loading screen

## Asset

`assets_queue/generated_sources/antq_loading_rome_ad1.png` is the preserved
image-generation master. Its checked, engine-sized derivative is
`assets_queue/generated/antq_loading_rome_ad1_1920x1080.png`; the game-facing
texture is `loading_screen/gfx/loadingscreens/startscreen.dds`.

The master prompt requested a text-free, muted painterly AD 1 Roman civic
panorama: early-imperial architecture, a civilian procession, the Tiber port,
and no later monuments, modern objects, heraldry, logos, or readable text.
The master and the DDS round-trip were visually inspected before use.

## Historical scope

This is an evocative loading illustration, not an archaeological reconstruction
or a claim that its architecture represents one exact sightline in the Forum.
It presents a sober early-imperial civic setting appropriate to the start date;
the image deliberately omits the Colosseum, Trajanic monuments, Constantinople,
and later Christian imperial imagery.

## Technical verification

The local asset manifest identifies the vanilla `startscreen.dds` target as
1920×1080, 8-bit sRGBA. The final replacement was resized to that exact size,
converted through `tools/dds.py` with DXT5 compression and mipmaps, then
converted back to PNG for a visual round-trip check. `make validate` passed,
and enabled-mod `make smoke` reached the menu with zero new `error.log` lines.
