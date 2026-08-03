#!/usr/bin/env python3
"""Runtime-stress every mounted fixed loading panorama and restore bindings."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from collections import OrderedDict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET_ROOT = (
    ROOT / "loading_screen/gfx/loading_screen_assets/00/images"
).resolve()
LAYER_ROOT = (
    ROOT / "loading_screen/gfx/loading_screen_assets/antq/layers"
).resolve()
ASSIGNMENTS = OrderedDict((
    ("rossbach", "germanic_rhine"),
    ("florence", "pompeii"),
    ("zheng_he", "changan"),
    ("martin_luther", "forum"),
    ("damascus_ambassadors", "palmyra"),
    ("deccan", "arikamedu"),
    ("aztec", "teotihuacan"),
    ("iroquois_ambush", "monte_alban"),
    ("ashanti", "jenne"),
    ("white_mountain", "camulodunum"),
    ("hansa", "ephesus"),
))


def run(*arguments: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, *arguments]
    return subprocess.run(command, cwd=ROOT, text=True, check=check)


def launch_with_retry(retries: int) -> None:
    for attempt in range(1, retries + 1):
        result = run("tools/gamedriver.py", "launch", "--mode", "mod", check=False)
        if result.returncode == 0:
            return
        if result.returncode != 75:
            result.check_returncode()
        print(
            f"STRESS_DEFERRED shared EU5 slot; retry {attempt}/{retries}",
            flush=True,
        )
        time.sleep(15)
    raise RuntimeError("shared EU5 slot did not clear within bounded retries")


def force_panorama(screen_key: str) -> None:
    """Point all exact selector textures at one reviewed fixed stack."""
    if not TARGET_ROOT.is_dir() or not LAYER_ROOT.is_dir():
        raise RuntimeError("loading-screen roots are missing")
    for scene_name in ASSIGNMENTS:
        for index in range(8):
            target = TARGET_ROOT / f"loading_screen_{scene_name}_{index:02d}.dds"
            source = LAYER_ROOT / f"{screen_key}_{index:02d}.dds"
            if target.parent.resolve() != TARGET_ROOT:
                raise RuntimeError(f"unsafe loading target: {target}")
            if not source.is_file() or source.parent.resolve() != LAYER_ROOT:
                raise RuntimeError(f"missing or unsafe loading source: {source}")
            target.unlink(missing_ok=True)
            os.link(source, target)


def manifest_passed(session: str) -> bool:
    path = ROOT / "docs/screens" / session / "loading_capture.json"
    if not path.is_file():
        return False
    report = json.loads(path.read_text(encoding="utf-8"))
    return bool(report.get("saw_loading")) and len(report.get("captured", ())) >= 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suffix", default="20260803")
    parser.add_argument("--menu-y", type=float, default=0.382)
    parser.add_argument("--slot-retries", type=int, default=20)
    args = parser.parse_args()
    failures: list[str] = []
    try:
        run("tools/m11_loading_screens.py", "--check")
        for scene_name, screen_key in ASSIGNMENTS.items():
            session = f"R5_LOADING_FIXED_{scene_name}_{screen_key}_{args.suffix}"
            print(
                f"STRESS_BEGIN scene={scene_name} screen={screen_key}",
                flush=True,
            )
            force_panorama(screen_key)
            try:
                launch_with_retry(args.slot_retries)
                run(
                    "tools/gamedriver.py", "wait", "--timeout", "300",
                    "--minimum", "35", "--quiet-seconds", "20",
                )
                run(
                    "tools/gamedriver.py", "capture-new-game-loading",
                    "--session", session, "--x", "0.14", "--y", str(args.menu_y),
                    "--percentages", "2", "5", "25", "--minimum-captures", "2",
                    "--timeout", "240", "--interval", "0.05",
                )
                if not manifest_passed(session):
                    raise RuntimeError("loading manifest lacks two captured frames")
                print(
                    f"STRESS_PASS scene={scene_name} screen={screen_key}",
                    flush=True,
                )
            except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
                failures.append(f"{scene_name}/{screen_key}: {error}")
                print(
                    f"STRESS_FAIL scene={scene_name} screen={screen_key}: {error}",
                    file=sys.stderr,
                    flush=True,
                )
            finally:
                run("tools/gamedriver.py", "stop", check=False)
    finally:
        try:
            run("tools/m11_loading_screens.py", "--write")
            run("tools/m11_loading_screens.py", "--check")
        except (OSError, subprocess.CalledProcessError) as error:
            failures.append(f"canonical restoration: {error}")
    if failures:
        for failure in failures:
            print(f"r5_loading_stress: FAIL: {failure}", file=sys.stderr)
        return 1
    print(f"r5_loading_stress: PASS ({len(ASSIGNMENTS)} mounted panoramas)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
