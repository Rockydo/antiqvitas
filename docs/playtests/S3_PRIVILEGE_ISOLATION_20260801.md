# S3 privilege isolation gate - 2026-08-01

- Fresh profiles: Parthia Great Houses (2), Rome Senatorial Order (2), Suebi
  Free Cultivators (1), Teotihuacan Household Retinues (1).
- Every displayed grant belongs to the active profile; no foreign or installed
  privilege appeared.
- Static union: 463 starts, 376 custom grants, exactly six profile grants per
  tag, 261 installed grants quarantined, 6-19 total visible per tag.
- Root cause fixed: 270 opening profile grants were also research unlocks.
  Their later advance entries are removed and permanently rejected.
- Captures: `docs/screens/S3_PRIVILEGE_ISOLATION_20260801_B/`.
