# S2 Germanic Political Depth Evidence — 2026-07-27

## Scope

This tranche replaces the generic political floor for four Tier-1 western
Germanic polities: Cherusci (`CRU`), Chatti (`CHT`), Batavi (`BTV`), and
Semnones (`SEM`). It does not claim completion of all Germanic content.

## Implemented contract

Each profile has:

- one distinct opening reform and one distinct council;
- five profile-specific administrative programmes;
- three issues and three matching agendas;
- six polity-aware social-order identities;
- six reform-gated privileges;
- two Age-I alternative reforms with distinct effect contracts;
- direct, non-aliased art for its council, programmes, and privileges.

The opening governments are Cheruscan Kindred Assembly, Chattian Host Order,
Batavian Rhine Compact, and Semnonian Sacred Confederacy. Alternative paths
cover coalition versus retinue leadership, elder-host versus chosen-warrior
authority, auxiliary treaty versus island assembly, and grove delegation
versus district muster.

## Art review

Eight 3x2 source atlases were generated and visually reviewed. They use
centered archaeological still lifes on the established dark-navy surface,
without people, faces, readable writing, medieval heraldry, Viking motifs, or
painted UI borders. The crop pipeline produced 24 political masters and 24
privilege masters with complete PNG, DDS, GUI, localization, and ledger chains.

Source atlases:

- `cheruscan_coalition_council_atlas.png`
- `chattian_host_council_atlas.png`
- `batavian_island_council_atlas.png`
- `semnonian_grove_council_atlas.png`
- `cheruscan_orders_atlas.png`
- `chattian_orders_atlas.png`
- `batavian_orders_atlas.png`
- `semnonian_orders_atlas.png`

## Static and focused checks

- `s2_ancient_politics`: PASS — 37 councils, 209 programmes, 135 issues,
  and 135 agendas.
- `s2_estate_orders`: PASS — 37 profiles, 270 generated profile privileges,
  270 direct icons, and 222 polity-aware order names.
- `m6_power`: PASS — 137 political contracts, 316 total privileges, and 227
  laws.
- `m8_knowledge`: PASS — 895 ancient-system unlocks and all 292 opening
  profiles researchable.
- `s2_germanic_politics_depth`: PASS — exact profile breadth, twelve correct
  council activations, four opening assignments, eight unique Age-I reform
  unlocks, 24 profile privileges, and complete direct art.
- `m11_ui_asset_ledger`: PASS — 1,258 direct UI chains across nine surfaces.

## Historical boundary

Tacitus is a late-first-century, literary witness. The implementation uses his
specific Batavian, Chattian, and Semnonian distinctions and his general
assembly/retinue frame, but does not treat *Germania* as a literal AD 1
constitution. Exact procedures, office names, territorial reach, and the
Semnonian hundred-canton figure remain contested. Cheruscan coalition play does
not assign Arminius as an invented AD 1 king.

## Final QA

- `gmake validate`: PASS, 108/108 registered commands.
- `gmake smoke`: PASS. Vanilla and ANTIQVITAS both reached responsive,
  rendered menus; the paired comparison found zero new `error.log` lines and
  no line types unique to the mod.

This follows the reduced QA policy: comprehensive static validation plus a
short paired launcher smoke, without a long observer campaign.
