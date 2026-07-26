# S2 Germania, Baltic, and northern-Europe probe — 2026-07-26

Status: PASS for the bounded Germania/Baltic regional batch under the reduced
rapid-subsystem policy.

## Mounted content

- The disconnected 24-location GER catch-all is gone. Rome owns both Alsace
  provinces, while the Angrivarii hold one contiguous 13-location
  Hanover–Lüneburg frame.
- The former 152-location Aestii superstate is split into Aestii (16), West
  Balt Barrow Culture (15), Brushed Pottery Culture (50), West Lithuanian
  Stone-Circle Culture (27), and Early Tarand-Grave Horizon (29). The
  Lower-Vistula Gutones hold a separate 21-location frame.
- Suebi, Gutae, Chaedini, Dauciones, Hilleviones, and Fenni replace six
  player-facing generic northern labels. Later names remain explicitly
  contested in the research ledger.
- Six direct-art privileges, six laws, four government overlays, and four
  direct-art regional unit types distinguish assembly, retinue, grove, amber,
  hillfort, and mortuary systems without asserting one Germanic constitution
  or one Baltic ethnic state.

## Focused runtime evidence

A fresh enabled New Game reached the AD 1 selector at 08:00 on 1 January 1.
The selector independently resolved:

- Angrivarii — 13 locations, Angrivarian culture;
- Aestii — 16 locations, Aestian culture;
- Brushed Pottery Culture — 50 locations, Brushed Pottery Baltic culture;
- Early Tarand-Grave Horizon — 29 locations, Early Tarand-Grave culture;
- Gutae — 39 locations in the southern Scandinavian interior;
- Fenni — 32 locations on the Finnic coast.

Each displayed a distinct direct standard, owned capital, period religion,
bounded rank presentation, and non-generic country name. Evidence is under
`docs/screens/S2_NORTHERN_GRANULARITY_20260726/`.

The selector appended one normalized diagnostic type only:
`initialize_from_bookmark.cpp:320: HRE doesn't exists in game`. This is the
already-pinned hardcoded absent-HRE notice in `docs/BLOCKERS.md`; no northern
content, script-system, unit, government, privilege, law, culture, ownership,
or localization error appeared.

## Gates

- `make validate`: PASS, 96/96.
- paired-control `make smoke`: PASS with zero mod-only normalized lines.
- six rapid selector probes: PASS.
- no observer campaign or long playthrough was run.
