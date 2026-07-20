# M11 pepper good-art override

## Asset and scope

`assets_queue/generated_sources/antq_pepper_chromakey_source.png` is the
retained built-in image-generation source; its locally chroma-keyed alpha
derivative is `assets_queue/generated/antq_pepper.png`. The game-facing DXT5
files are the exact native names:

- `main_menu/gfx/interface/icons/trade_goods/icon_goods_pepper.dds` (128x128)
- `main_menu/gfx/interface/icons/trade_goods/illustrations/icon_goods_pepper.dds` (1080x440)

The final prompt requested an isolated basket of black peppercorns with a
short vine sprig and unripe clusters, on a flat magenta chroma-key background.
It excluded people, ships, ports, buildings, maps, labels, packaging, logos,
watermarks, borders, modern objects, and text. The background was removed with
the reviewed local chroma-key helper, then the alpha source and both DDS forms
were visually inspected after round-trip conversion.

## Historical scope

This is a generic commodity illustration. It does not identify a plantation,
port, merchant, vessel, harvest date, or trade route. It visually supports the
already native `pepper` good; no duplicate custom good or new economic claim
was introduced.

## Engine verification

The installed game contains same-named native pepper textures at 128x128 and
1080x440. The mod supplies exact same-path DXT5 DDS overrides, preserving the
existing good key and engine lookup convention. `make validate` passed and
enabled-mod `make smoke` reached the menu with zero new error-log lines.

Sources: ANTIQVITAS master plan sections 12.1 and 20; local EU5 pepper-good
asset contract.
