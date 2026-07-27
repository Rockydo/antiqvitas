# S2 Britain/Ireland Political Depth Evidence — 2026-07-27

## Scope

This tranche adds distinct political games for Trinovantes (`TRI`), Brigantes
(`BRI`), Durotriges (`DUR`), and Iverni (`IVN`). The 35 British and 16
Hibernian map frames already remain intact; this work replaces four important
generic-government fallbacks and does not claim completion of all 51 profiles.

## Installed contract

Each profile has one opening reform, one distinct council, five programmes,
three issues/agendas, six polity-aware social orders, six profile privileges,
and two Age-I alternative reforms.

- Trinovantes: coin kingship; oppidum court or Channel compact.
- Brigantes: hillfort confederacy; kindred compact or hillfort court.
- Durotriges: hillfort-and-coin order; coin-weight council or settlement
  compact.
- Iverni: regional assembly; seaway compact or cattle-gift court.

All twelve reforms explicitly activate the correct council. The four opening
governments use a matching profile privilege, and every base/alternative reform
has one Age-I research route.

## Evidence boundaries

- Dubnovellaunos has a 20 BCE-AD 10 Trinovantian coin horizon, but the exact
  court procedure and reach are contested.
- Brigantian AD 1 unity and Stanwick's role are uncertain; Cartimandua is not
  moved backward from the later Roman-conquest context.
- Durotrigian coinage, pottery, burial, settlement, and enclosure evidence is
  distinctive, but does not prove one central state or continuous occupation
  of every hillfort.
- Ptolemy's Iverni are later evidence and the Irish Iron Age settlement record
  is sparse. No medieval Gaelic offices, ogham administration, or dense
  settlement hierarchy is projected backward.

## Art

Eight dedicated 3x2 archaeological atlases produced 24 political and 24
privilege icons. The first Brigantian political result was rejected because it
contained living cattle and was regenerated as an object/landscape still-life
sheet. Accepted sources have dark-navy backgrounds, crop-safe circular
composition, no people, text, heraldry, Roman military costume, or medieval
motifs. Every final icon has a direct PNG/DDS/GUI/localization ledger chain.

## Focused results

- `s2_ancient_politics`: PASS — 41 councils, 229 programmes, 147 issues, and
  147 agendas.
- `s2_estate_orders`: PASS — 41 profiles, 294 generated profile privileges,
  294 direct icons, and 246 polity-aware order names.
- `m6_power`: PASS — 149 political contracts, 340 total privileges, and 227
  laws.
- `m8_knowledge`: PASS — 931 ancient-system unlocks and all 292 opening
  profiles researchable.
- `s2_british_politics_depth`: PASS — exact opening setups, twelve council
  activations, eight unique Age-I alternatives, 24 profile privileges, and
  complete direct art.
- `m11_ui_asset_ledger`: PASS — 1,306 direct chains across nine surfaces.

## Final QA

- `gmake validate`: PASS — 109/109 commands.
- `gmake smoke`: PASS — vanilla and ANTIQVITAS both reached responsive,
  rendered menus; zero new log lines and zero mod-unique line types.
- Runtime scope follows the reduced QA policy: this is a paired load/error-log
  gate, not a long observer campaign.
