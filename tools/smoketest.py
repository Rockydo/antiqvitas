#!/usr/bin/env python3
"""Launch EU5, reach the menu, and reject every new normalized error line."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venv/Scripts/python.exe"
TIMESTAMP = re.compile(r"^\[\d\d:\d\d:\d\d\]")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [str(PYTHON), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    if check and result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(args)}")
    return result


def normalize(path: Path) -> set[str]:
    if not path.exists():
        return set()
    lines = []
    for raw in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = TIMESTAMP.sub("", raw).strip().replace("\\", "/")
        if line:
            lines.append(line)
    return set(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-only", action="store_true")
    parser.add_argument("--leavepops", action="store_true")
    parser.add_argument("--accept", action="store_true")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="wait for an already-launched game, then stop and diff its log",
    )
    parser.add_argument("--menu-minimum", type=int, default=30)
    parser.add_argument("--quiet-seconds", type=int, default=15)
    parser.add_argument("--timeout", type=int, default=480)
    args = parser.parse_args()
    config = json.loads(
        (ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig")
    )
    baseline_only = args.baseline_only or not (ROOT / ".metadata/metadata.json").exists()
    baseline = ROOT / "baselines/vanilla_error.log"
    accepted = ROOT / "baselines/last_accepted_error.log"
    if not baseline.is_file():
        print("smoketest: FAIL (vanilla baseline not captured)", file=sys.stderr)
        return 1
    if not args.resume:
        if not baseline_only and not Path(str(config["mod_dir"])).exists():
            subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ROOT / "tools/link_mod.ps1"),
                ],
                cwd=ROOT,
                check=True,
            )
        mode = "--vanilla" if baseline_only else "--enable"
        run("tools/enable_mod.py", mode)
        launch = ["tools/gamedriver.py", "launch", "--mode"]
        launch.append("vanilla" if baseline_only else "mod")
        if args.leavepops:
            launch.append("--leavepops")
        run(*launch)
    try:
        ready = run(
            "tools/gamedriver.py",
            "wait",
            "--timeout",
            str(args.timeout),
            "--minimum",
            str(args.menu_minimum),
            "--quiet-seconds",
            str(args.quiet_seconds),
            check=False,
        )
        if ready.returncode:
            raise RuntimeError("game did not reach the menu")
    finally:
        run("tools/gamedriver.py", "stop", check=False)
    actual_path = Path(str(config["user_dir"])) / "logs/error.log"
    actual = normalize(actual_path)
    reference = normalize(baseline if baseline_only else accepted)
    new = sorted(actual - reference)
    fixed = sorted(reference - actual)
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "vanilla" if baseline_only else "mod",
        "new": new,
        "fixed": fixed,
        "actual_unique_lines": len(actual),
        "reference_unique_lines": len(reference),
    }
    target = ROOT / "baselines/runtime/last_smoke.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if new:
        print("smoketest: FAIL — NEW error.log lines")
        for line in new:
            print(f"  {line}")
        return 1
    if args.accept:
        shutil.copy2(actual_path, accepted)
    print(f"smoketest: PASS (zero new lines; {len(fixed)} baseline line types absent)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
