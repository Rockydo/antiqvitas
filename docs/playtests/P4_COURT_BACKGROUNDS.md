# P4 court-background rapid probe

Date: 2026-07-25

- `make validate`: PASS, 79/79.
- Paired vanilla/mod `make smoke`: PASS, zero mod-only error lines.
- First smoke exposed the required UTF-8 BOM for `gfx/images`; corrected and
  re-smoked green.
- Non-debug New Game rendered the AD 1 selector and Celtic ruler popup.
- Physical-Escape recovery reached paused live Observer; scaled map targeting
  then opened a sea-zone panel, so the full culture matrix was not repeated.
- Static review covers all twelve 1080x440 outputs and the resolver covers 79
  unique graphical-culture keys plus an unconditional ancient fallback.

Result: PASS under the reduced smoke/rapid-check policy. Optional live
culture-by-culture captures remain deferred.
