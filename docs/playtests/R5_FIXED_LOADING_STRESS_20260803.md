# R5 fixed-loading stress proof

- Driver: `tools/r5_loading_stress.py`; corrected New Game coordinate `y=0.382`.
- Scope: all 11 mounted selector/panorama assignments; each panorama was forced
  across all selectors, launched with the mod, and captured during New Game load.
- Observed: 97-100% cached-load frames for all 11 assignments; visual review found
  no ghosts, holes, seams, alpha blocks, blurred patches, or mismatched scenes.
- Cleanup: every run stops its owned EU5 process; the outer `finally` regenerates
  canonical bindings. The 16-screen/eight-plane static contract passes afterward.
- Restored fingerprint:
  `9eee7240af472557f4bf502f969be2be0dfca87c4957498080c9ba6ca484c895`.
- Evidence: `docs/screens/R5_LOADING_FIXED_*_20260803B/`.
