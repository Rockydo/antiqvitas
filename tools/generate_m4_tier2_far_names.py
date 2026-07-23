#!/usr/bin/env python3
"""Generate the explicitly far, lowest-confidence Pleiades adapter band."""
from __future__ import annotations
import argparse
import generate_m4_tier2_remote_names as remote

remote.OUTPUT = remote.ROOT / "docs/m4/tier2_far_location_name_overrides.csv"
remote.MIN_OFFSET_PX = 6.00
remote.MAX_OFFSET_PX = 12.00
remote.LABEL = "Far"
remote.SOURCE_SUFFIX = "T2F"
remote.EXTRA_LEDGER_PATHS = (remote.ROOT / "docs/m4/tier2_remote_location_name_overrides.csv",)

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--write", action="store_true"); parser.add_argument("--check", action="store_true"); args = parser.parse_args()
    if args.write == args.check: parser.error("provide exactly one of --write or --check")
    try: expected = remote.render()
    except (OSError, ValueError) as exc: print(f"m4_tier2_far_names: FAIL\n  - {exc}"); return 1
    if args.write:
        remote.OUTPUT.write_text(expected, encoding="utf-8-sig", newline=""); print(f"m4_tier2_far_names: wrote {remote.OUTPUT.relative_to(remote.ROOT)}"); return 0
    if not remote.OUTPUT.is_file() or remote.OUTPUT.read_text(encoding="utf-8-sig") != expected:
        print(f"m4_tier2_far_names: FAIL\n  - stale or missing {remote.OUTPUT.relative_to(remote.ROOT)}"); return 1
    print(f"m4_tier2_far_names: PASS ({max(0, len(expected.splitlines()) - 1)} far lower-confidence adapters)"); return 0
if __name__ == "__main__": raise SystemExit(main())
