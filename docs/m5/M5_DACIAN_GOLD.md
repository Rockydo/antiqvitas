# M5 Dacian gold anchor

## Evidence

Ioane and Bedelean's chapter, ["Ancient Gold Mining in Roșia
Montana"](https://bibliotecadigital.ipb.pt/bitstream/10198/6495/7/Natural%20Heritage.pdf),
identifies the Apuseni/Roșia Montană district as a gold-mining landscape with
exploitation of river sediments or shallow veins before the Roman conquest and
with major Roman intensification after AD 106. That supports a Dacian-period
gold district at campaign start; it does not establish its output, mine plan,
or an exact location-by-location operation on 1 January AD 1.

## Engine representation

Roșia Montană's coordinates (46.307 N, 23.130 E) project closest to installed
`baia_de_aries`, already controlled by the AD 1 Dacian tag. Its raw material
is therefore changed from vanilla `beeswax` to installed `goods_gold`. This is
a deliberately small geographic proxy, not an assertion that Baia de Arieș is
the historical mine or that the later Roman mining complex exists before
Trajan's conquest.

## Verification

`tools/generate_rgo_remap.py --write` reports 327 corrections, including the
new `beeswax -> goods_gold` anchor. `make validate` passed and enabled-mod
`make smoke` reached the menu with zero new `error.log` lines against the
accepted baseline.

Sources: `SPR-ROS-GOLD`; P8.7; P12.1.
