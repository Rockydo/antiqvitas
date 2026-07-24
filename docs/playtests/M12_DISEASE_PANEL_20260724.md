# M12 Diseases panel regression — 2026-07-24

## Evidence

- Manual crash: `Europa Universalis V20260724_145327`; autonomous reproductions:
  `Europa Universalis V20260724_160811` and `...162111`. All terminate with native
  `C0000005` when Diseases opens from an empty-manager save.
- Vanilla-only fresh 1337 control rendered all seven installed diseases and stayed
  alive (`docs/screens/M12_disease_vanilla_control/disease_open.png`).
- Fresh AD 1 Rome after manager initialization rendered all seven diseases,
  endemic malaria, and per-disease resistance values. Territory→Diseases cycles
  1–4 survived; a fifth cycle after `observe` survived.
- Screens: `docs/screens/M12_disease_fresh_manager/disease_cycle1_survived.png`,
  `disease_cycle2.png`–`disease_cycle4.png`, and
  `observer_disease_verified.png`.
- The current run ended with `error.log` at 0 bytes and no later crash bundle.

## Result

PASS. The deterministic crash route is repaired. The installed-definition and
literal-GUI texture union is now generated, mirrored, hashed, and mandatory in
`make validate`; old saves made with the empty disease manager remain invalid
test fixtures.
