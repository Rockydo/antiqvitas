# S2 Global RGO Screen — 2026-07-27

## Scope

Rapid whole-map verification of the first AD 1 raw-material screen. This pass
targets period/range and environmental impossibilities and establishes a
complete audit baseline; it does not claim site-specific attestation for every
retained staple.

## Coverage and changes

- 13,550/13,550 controlled templates audited.
- 652 actual changes: 539 regional rules, 98 climate rules, and 15 corrected
  direct anchors.
- Two already-correct direct anchors retained.
- Two controlled water/wasteland templates have no RGO and remain
  nonproductive.
- 12,894 period-valid defaults are retained with contested confidence and an
  explicit non-attestation note.

Largest corrected source-good families are cotton 130, silk 110, sugar 73,
wine 69, coal 49, pepper 45, incense 33, saltpeter 32, olives 32, tea 23, rice
20, saffron 11, and coffee 9. The corrected map template and runtime startup
effects derive from the same change set.

## Results

- `make validate`: PASS, 101/101 commands.
- `generate_rgo_remap`: PASS, 652 corrections and 13,550 audited locations.
- `m12_hardcoded_startup`: PASS, all 652 runtime effects accepted.
- Active-goods, building-economy, script lint, startup, and anachronism checks:
  PASS.
- Paired vanilla/mod `make smoke`: PASS, responsive rendered menus and zero
  mod-unique new `error.log` lines.

The generated evidence ledgers are `docs/m5/global_rgo_audit.csv` and
`docs/m5/rgo_remap_report.csv`.
