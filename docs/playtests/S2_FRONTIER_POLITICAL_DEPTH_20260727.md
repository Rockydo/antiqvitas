# S2 Frontier Political Depth Evidence — 2026-07-27

## Scope

This tranche replaces the generic political floor for Aestii (`AES`), Frisii
(`FRI`), the divided Dacian kingdoms (`DAC`), and Garamantes (`GAR`). It is a
bounded depth pass over four high-value frontier starts, not a completion claim
for every Baltic, Germanic, Danubian, or Saharan polity.

## Installed contract

Each profile has one opening reform, one distinct council, five programmes,
three issue/agenda pairs, six polity-aware social orders, six profile
privileges, and two Age-I alternative reforms.

- Aestii: amber-coast order; shore-exchange compact or woodland assembly.
- Frisii: terp-community order; tidal compact or frontier council.
- Dacians: divided kingships; hillfort compact or mountain court.
- Garamantes: oasis state; irrigation court or caravan compact.

All twelve reforms explicitly activate the correct council. Every opening
government receives a matching profile privilege, and each base or alternative
reform has one checked Age-I research route.

## Evidence boundaries

- Tacitus's Aestii are evidence from about AD 98, not a literal AD 1
  constitution. Amber, coast, cultivation and offering-place mechanics do not
  assert a centralized kingdom, named ruler, or fixed frontier.
- Frisian terp settlement and Roman contact are secure. The AD 28 ox-hide
  tribute crisis informs a pressure mechanic but is not back-projected as an
  opening revolt or permanent treaty.
- Strabo supports post-Burebista division. No unified Decebalan crown,
  centralized priesthood, or later territorial maximum is imposed on AD 1.
- Garamantian oasis urbanism, irrigation, mobility, cultivation, craft and
  exchange are secure; office titles, ruler identity, allocation procedure and
  exact state reach remain anonymous and contested.

## Art

Eight accepted 1536x1024 archaeological 3x2 atlases produced 24 political and
24 privilege icons. Five earlier trials were rejected: two had incorrect square
geometry, one Dacian sheet looked medieval/fantasy, one Aestian sheet included
rune-like marks, one inserted a boat contrary to the brief, and one Garamantian
sheet introduced a pseudo-inscribed measuring rod. Accepted sources use
crop-safe object-and-landscape compositions with no people, living animals,
text, runes, heraldry, or medieval motifs.

Accepted source SHA-256:

- `aestian_council_atlas.png`:
  `cac9391c02c6bd9d86d3449c5dc434ca404b0ba4f99e91fd77cdd09af3f9d7fb`
- `frisian_council_atlas.png`:
  `216654b1d02f97182af2509bce83b23ef8b10bf1d7934e6f20cf929b0cc0ea20`
- `dacian_council_atlas.png`:
  `90ccb887d6f47f06f248b07317bcf2365fb316492e508b44b302ffbbf5826e60`
- `garamantian_council_atlas.png`:
  `42a86c05372a36a344390343fc93f7af5671fec64d0024f9fe49ffb26fe58fd2`
- `aestian_orders_atlas.png`:
  `e5876709451c75450bd5bc105d8fea07b45564cfafa46fc81371005ec6944d99`
- `frisian_orders_atlas.png`:
  `2f83730ed5c01fb6ee5ec6208a5fda9e52f716161cedcdcf53b4bc34bf457a9e`
- `dacian_orders_atlas.png`:
  `a38c92e36a19c5c745c76cbe01047cefb0c1d14c5a6d8870d685b5ce5af72f2d`
- `garamantian_orders_atlas.png`:
  `5c7c64aa201850e92db029ae8372c0ae5139af450920eebc3df49e8c00cbfc7d`

## Focused results

- `s2_ancient_politics`: PASS — 45 councils, 249 programmes, 159 issues, and
  159 agendas.
- `s2_estate_orders`: PASS — 45 profiles, 318 generated profile privileges,
  318 direct icons, and 270 polity-aware order names.
- `m6_power`: PASS — 161 political contracts, 364 total privileges, and 227
  laws.
- `m8_knowledge`: PASS — 967 ancient-system unlocks and all 292 opening
  profiles researchable.
- `s2_frontier_politics_depth`: PASS — exact opening setups, twelve council
  activations, eight unique Age-I alternatives, 24 profile privileges, and
  complete direct art.
- `m11_ui_asset_ledger`: PASS — 1,354 direct chains across nine surfaces.

## Final QA

- `gmake validate`: PASS — 110/110 commands.
- `gmake smoke`: PASS — vanilla and ANTIQVITAS both reached responsive,
  rendered menus; zero new log lines and zero mod-unique line types.
- Runtime scope follows the reduced QA policy: paired load/error-log evidence
  plus focused deterministic regressions, with no long observer campaign.
