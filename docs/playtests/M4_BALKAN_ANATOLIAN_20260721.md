# M4 Balkan-Anatolian atlas verification

Date: 2026-07-21

## Scope

The batch adds 50 named Balkan and Anatolian regional frames sourced from
Strabo and a modern Anatolian synthesis. Every frame refines a pre-existing
broad selector through one installed province and remains explicitly contested:
it is not an exact tribal polygon, language census, or political boundary.

## Static evidence

- M4 generation produced 314 culture definitions and 37 religions.
- The 470 source-labelled selectors resolve 12,058 controlled locations across
  292 mapped cultures; the 50 new selectors cover 291 generated population
  locations.
- `tools/popcheck.py` passed: 230,000.000 thousand people over 13,552
  populated controlled locations.
- `make validate` passed the whole project surface before and after the
  runtime-discovered localization repair.

## Runtime evidence

The first enabled-mod smoke reported exactly one new line: a duplicate
`antq_liburnian` localization key shared by the new culture and M7's naval unit.
The culture symbol was changed to `antq_liburnian_culture`, generated content
was rebuilt, and a second enabled-mod smoke completed at
`2026-07-21T18:31:08Z` with `new: []`, `fixed: []`, and two unchanged accepted
baseline lines.

## Result

The repaired batch is accepted as green. It raises M4 to 314 cultures; the
milestone remains open until the plan's 350-500 target and final gate are met.
