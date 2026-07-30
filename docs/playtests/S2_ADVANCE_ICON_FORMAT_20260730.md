# S2 advance icon format probe - 30 July 2026

## Scope

Verify the corrected advance-asset contract in installed GUI definitions and
the live Advances panel.

## Result

Pass.

- Installed build 24187685 exposes 16 advance-art calls across nine contexts.
- All 365 current icons pass RGBA, transparent-perimeter, safe-area, BC7 sRGB,
  mipmap, and hash-chain checks.
- The live Roman Advances panel shows circular Imperial Archives, Legionary
  Logistics, and River Port Dues art without square-edge leakage:
  `docs/screens/s2_advance_icon_format_20260730/advances_panel_runtime.png`.
- `make validate`: 139/139.
- Paired `make smoke`: zero mod-unique lines; tree fingerprint
  `3739fe5a53e96bca7f9f6a0f96489bbb67f7e4ac467b5267a56e0c3f43f4fdc0`.
