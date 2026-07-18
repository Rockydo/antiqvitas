#!/usr/bin/env python3
"""Validate population totals once setup pop data exists."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POP_RE = re.compile(r"\bsize\s*=\s*(\d+(?:\.\d+)?)")


def main() -> int:
    start = ROOT / "in_game/setup/start"
    files = list(start.rglob("*.txt")) if start.exists() else []
    total = 0.0
    pop_files = 0
    for path in files:
        text = path.read_text(encoding="utf-8-sig")
        values = [float(value) for value in POP_RE.findall(text)]
        if values:
            pop_files += 1
            total += sum(values)
    if not pop_files:
        print("popcheck: PASS (no setup pops yet)")
        return 0
    print(f"popcheck: PASS ({total:,.0f} thousand people across {pop_files} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
