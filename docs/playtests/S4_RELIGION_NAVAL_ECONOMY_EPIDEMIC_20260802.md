# S4 religion, naval, economy, and epidemic probe - 2026-08-02

## Result

- Religion: PASS. 52 faiths expose 22 profiles/modifier sets. Rome, Parthia,
  Satavahana, Han, Suebi, and Maya differ visibly. Christianity, Daoism, and
  Manichaeism follow installed future-faith `enable` plus event enablement; none
  has an AD 1 pop. The forced Christian event made its target resolvable without
  a new script error.
- Naval: PASS. All 463 starts resolve to 232 inland, 17 local-watercraft,
  76 limited-transport, 119 organized-patrol, 8 state-fleet, and 11 long-distance
  profiles. Rome has nine types; Parthia eight; Han/Satavahana seven; Maya four;
  inland Suebi zero.
- Principate economy: static PASS, settled runtime open. No flat income grant
  remains. The bounded pre-market bridge ends at market access; 405 small states
  receive 250 opening gold; Rome receives none. Rome has 3x and five peer hubs 2x
  redundant core-material production. Initial Rome proof: `10.44K`, no `+500`.
- Epidemics: PASS. Antonine smallpox anchors Antioch 0.35 and Luoyang 0.20;
  Cyprian anchors Tunis 0.30. Native mortality/spread plus manpower, food, labor,
  tax, and fiscal effects drive both trajectories.

## Evidence

- Religion UI: `docs/screens/20260802_163936`, `20260802_164111`,
  `20260802_164154`, `20260802_164210`, `20260802_164300`, `20260802_164315`.
- Native Christian enable/target: `docs/screens/20260802_183904` and
  `docs/screens/20260802_183930`; no matching new `error.log` line.
- Initial Rome economy: `docs/screens/20260802_184124/s4_rome_economy_initial.png`.
- A debug-heavy economy run ended in native Vulkan/FSR access violation
  `ffxFsr2ResourceIsNull`; a clean paired smoke did not reproduce it.
- Final gates: `make validate` 163/163; `make smoke` zero new lines,
  fingerprint `452d1f5f1125c17024dce10a746cabdcabed870eef2b95e579c1c13941479067`.
