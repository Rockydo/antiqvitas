# P4 manual-remediation regression

- The deterministic route is frozen in `docs/m12/rapid_regression_route.csv`:
  twelve bounded stages, eight accepted visual records, and no long campaign.
- Runtime evidence is reused where the subsystem did not change: Rome/Han/
  Marcomanni recruitment, institutions, advances, Diseases open/close, and the
  short non-debug save/reload. The current batch separately reached the AD 1
  selector and paused live Observer.
- `tools/p4_manual_regression.py` maps all 20 reported symptom classes to 27
  mandatory validators and exact evidence. It also asserts roster granularity,
  loyalty, population, Gallic/Galatian setup, unit art, ancient institutions,
  advance density, disease dependencies, court scenes, and leakage coverage.
- The closeout deliberately uses rapid static/setup checks plus paired smoke;
  no AD 1-476 playthrough or multi-century soak is required.

Result: PASS. Full validation is green at 90/90; the fresh paired vanilla/mod
smoke reached stable rendered menus and found zero mod-only `error.log` lines.
