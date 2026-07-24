# M12 installed-content census and unit quarantine

## Static evidence

- Installed union: 3,992 definitions, 6,891 references, 1,116 art links across
  nine surfaces; zero uncovered source files/keys.
- Units: 31 exact-name mirrors, 323 installed definitions, 311 hidden and
  non-buildable, 12 technical copy-chain adapters, 44 active ancient units.
- Loading tips: all 64 base+DLC keys (`0`-`59`, `d008_0`-`d008_3`) in all 11
  clients and both mounted localization layers.

## Rapid runtime evidence

- `M12_unit_quarantine_final3/recruit_final.png`: Rome exposes Roman Sagittarii,
  Comitatenses, Limitanei, Roman Alae, and Roman Exploratores.
- `M12_unit_quarantine_regions/rome_naval_recruitment.png`: Rome exposes
  Liburnian, Trireme, Quinquereme, and Merchant Roundship.
- `M12_unit_quarantine_regions/han_recruitment_open.png`: Han exposes only Han
  Crossbow Infantry.
- `M12_unit_quarantine_regions/han_naval_recruitment.png`: Han exposes only the
  ancient Merchant Roundship.
- `M12_unit_quarantine_regions/marcomanni_recruitment.png`: the Marcomannic
  regular builder exposes no legacy regular units. Its ancient Germanic roles
  remain levy-only; fresh-start levy presentation stays in the open parent task.
- `M12_unit_quarantine_final3/ok_clicked.png` and
  `M12_unit_quarantine_regions/loading_tip_2.png`: distinct ancient Deuteronomy
  and *Periplus of the Erythraean Sea* quotations, with ancient panoramas.
- Targeted log scan: zero matches for missing/subunit errors, Redcoats,
  experimental riflemen, Grenzer, or Pandur.

## Gates

- `make validate`: PASS (69/69).
- `make smoke`: PASS, zero new mod-only error lines.

Result: installed-content census and loading-tip replacement pass. The broader
unit parent remains open for fresh Germanic levy presentation, every-age probes,
and the dedicated icon batch.
