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


def launch_and_capture(
    mode: str,
    *,
    leavepops: bool,
    timeout: int,
    menu_minimum: int,
    quiet_seconds: int,
) -> set[str]:
    """Reach the menu in one playset and return its normalized current log."""
    run("tools/enable_mod.py", "--vanilla" if mode == "vanilla" else "--enable")
    launch = ["tools/gamedriver.py", "launch", "--mode", mode]
    if leavepops:
        launch.append("--leavepops")
    run(*launch)
    try:
        ready = run(
            "tools/gamedriver.py",
            "wait",
            "--timeout",
            str(timeout),
            "--minimum",
            str(menu_minimum),
            "--quiet-seconds",
            str(quiet_seconds),
            check=False,
        )
        if ready.returncode:
            raise RuntimeError(f"{mode} game did not reach the menu")
    finally:
        run("tools/gamedriver.py", "stop", check=False)
    config = json.loads((ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig"))
    return normalize(Path(str(config["user_dir"])) / "logs/error.log")


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
    parser.add_argument(
        "--menu-minimum",
        type=int,
        default=90,
        help="hold the rendered menu through the post-splash resource-load phase",
    )
    parser.add_argument("--quiet-seconds", type=int, default=15)
    parser.add_argument("--timeout", type=int, default=480)
    args = parser.parse_args()
    baseline_only = args.baseline_only or not (ROOT / ".metadata/metadata.json").exists()
    baseline = ROOT / "baselines/vanilla_error.log"
    accepted = ROOT / "baselines/last_accepted_error.log"
    if not baseline.is_file():
        print("smoketest: FAIL (vanilla baseline not captured)", file=sys.stderr)
        return 1
    if not args.resume:
        if not baseline_only:
            config = json.loads((ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig"))
            if not Path(str(config["mod_dir"])).exists():
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
        if baseline_only:
            actual = launch_and_capture(
                "vanilla",
                leavepops=args.leavepops,
                timeout=args.timeout,
                menu_minimum=args.menu_minimum,
                quiet_seconds=args.quiet_seconds,
            )
            vanilla_actual = actual
        else:
            # Every enabled-mod smoke has a same-machine vanilla control.  This
            # prevents a driver/runtime update (such as the reproducible DX12
            # Options8 assertion) from being misclassified as a mod regression.
            vanilla_actual = launch_and_capture(
                "vanilla",
                leavepops=args.leavepops,
                timeout=args.timeout,
                menu_minimum=args.menu_minimum,
                quiet_seconds=args.quiet_seconds,
            )
            actual = launch_and_capture(
                "mod",
                leavepops=args.leavepops,
                timeout=args.timeout,
                menu_minimum=args.menu_minimum,
                quiet_seconds=args.quiet_seconds,
            )
    else:
        config = json.loads((ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig"))
        actual_path = Path(str(config["user_dir"])) / "logs/error.log"
        actual = normalize(actual_path)
        vanilla_actual = set()
    reference = normalize(baseline if baseline_only else accepted)
    effective_reference = reference | vanilla_actual
    new = sorted(actual - effective_reference)
    fixed = sorted(reference - actual)
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "vanilla" if baseline_only else "mod",
        "new": new,
        "unmodded_new": sorted(vanilla_actual - reference),
        "fixed": fixed,
        "actual_unique_lines": len(actual),
        "reference_unique_lines": len(reference),
        "unmodded_unique_lines": len(vanilla_actual),
    }
    target = ROOT / "baselines/runtime/last_smoke.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if new:
        print("smoketest: FAIL — NEW error.log lines")
        for line in new:
            print(f"  {line}")
        return 1
    if not baseline_only and vanilla_actual - reference:
        print(
            "smoketest: current vanilla control contains "
            f"{len(vanilla_actual - reference)} archived-baseline delta line type(s); "
            "none are unique to the mod"
        )
    if args.accept:
        shutil.copy2(actual_path, accepted)
    print(f"smoketest: PASS (zero new lines; {len(fixed)} baseline line types absent)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
