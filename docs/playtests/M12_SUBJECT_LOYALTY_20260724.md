# M12 Subject Loyalty Probe — 2026-07-24

## Result

PASS under the reduced rapid-probe policy.

- Static ledger: 25 unique dependencies across client kingdom, satrapy, and
  tributary contracts; every subject capital is installed-proven ownable.
- Rome: 11 subjects at 1 January and 11 at 4 January; visible loyalty
  61.94–84.22%. The engine trigger confirmed XAC/Batanea remained Rome's subject.
- Parthia: nine satrapies retained; eight displayed at 58.70–72.91% with one
  collapsed behind the row expander.
- Han: five tributaries at 65.31–65.77%.
- Root cause removed: the prior log line `Dependency with non-existent subject
  (XAC)` came from Batanea's mountain-wasteland seat, not the loyalty formula.
- `make validate`: 70/70 PASS. `make smoke`: PASS, zero mod-only new lines.

Evidence: `docs/screens/M12_subject_loyalty/rome_subjects_after_tick_fixed.png.png`,
`subject_trigger_xac_true.png.png`, `parthia_subject_row_clean.png`, and
`han_subject_row.png`.
