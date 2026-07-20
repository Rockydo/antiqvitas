# M11 *Immensum Bellum* event illustration

## Asset

`assets_queue/generated_sources/antq_immensum_bellum_source.png` is the
preserved image-generation master. Its exact 1080×440 derivative is
`assets_queue/generated/antq_immensum_bellum_1080x440.png`; the game-facing
texture is
`main_menu/gfx/interface/illustrations/event/antq_immensum_bellum.dds`.

The prompt requested a text-free, wide AD 1 scene of a compact Roman column
and scout beside a Rhine frontier river crossing in damp broadleaf forest. It
required early-imperial equipment and excluded a named battle, Teutoburg,
later limes, medieval armour, modern objects, logos, and readable writing. The
master and DDS round-trip were visually inspected before use.

## Historical scope

The image illustrates the plan's AD 1 *Immensum Bellum* historical current;
it is not an identification of a particular march, unit, riverbank, commander,
or engagement. It deliberately represents campaign movement rather than
combat and does not anticipate the AD 9 Teutoburg disaster or later frontier
architecture.

## Engine attachment and verification

The local `earthquake_events.txt` contract establishes `image = "...dds"` on
a country event. `tools/m10_history.py` now owns the reviewed image mapping so
regeneration retains the `antq_m10.1001` reference rather than relying on a
hand edit. The local vanilla earthquake sample establishes the 1080×440 BC7
texture form. `tools/dds.py` uses the local work-drive DirectXTex encoder for
BC7, with the full mip chain; the resulting texture identifies as 1080×440,
8-bit sRGBA, BC7 and was round-tripped to PNG for review.

`make validate` passed, then enabled-mod `make smoke` reached the menu with
zero new `error.log` lines.

Sources: ANTIQVITAS master plan §§9 and 20; local EU5 country-event and
`earthquake.dds` asset contracts.
