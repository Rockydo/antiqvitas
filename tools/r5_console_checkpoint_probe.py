#!/usr/bin/env python3
"""Bounded exact-save console-load proof for the Round-5 population gate."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def driver(*arguments: str) -> None:
    subprocess.run([sys.executable, "tools/gamedriver.py", *arguments], cwd=ROOT, check=True)


def save_dir() -> Path:
    config = json.loads((ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig"))
    return Path(str(config["user_dir"])) / "save games"


def read_date(path: Path) -> str:
    with path.open(encoding="utf-8-sig", errors="replace") as handle:
        for number, raw in enumerate(handle, 1):
            line = raw.strip()
            if line.startswith("start_of_day="):
                return line.removeprefix("start_of_day=")
            if number >= 250_000:
                break
    raise RuntimeError(f"no start_of_day in {path}")


def save_and_wait(stem: str) -> Path:
    target = save_dir() / f"{stem}.eu5"
    if target.exists():
        target.unlink()
    driver("console", f"save {stem}", "--paste", "--settle", "8")
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        if target.is_file() and target.stat().st_size > 1_000_000:
            return target
        time.sleep(1)
    raise RuntimeError(f"console save did not appear: {target}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", default="r5_population_normal_end")
    parser.add_argument("--output", default="r5_population_console_loaded")
    parser.add_argument("--session", default="R5_CONSOLE_CHECKPOINT_20260803")
    args = parser.parse_args()
    checkpoint = save_dir() / f"{args.checkpoint}.eu5"
    if not checkpoint.is_file():
        raise RuntimeError(f"checkpoint missing: {checkpoint}")
    expected = read_date(checkpoint)
    driver("launch", "--mode", "mod")
    try:
        driver("wait", "--timeout", "300", "--minimum", "35", "--quiet-seconds", "20")
        driver("capture-new-game-loading", "--session", args.session, "--x", "0.14", "--y", "0.382", "--percentages", "5", "--minimum-captures", "1", "--timeout", "480", "--interval", "0.05")
        driver("start-observer", "--session", args.session, "--country-selection-settle", "5", "--observer-enable-settle", "8", "--live-timeout", "90")
        # The local console resolves neither a bare stem nor a relative .eu5
        # filename against this redirected user directory.  Keep the complete
        # quoted path inside ``subprocess.run`` so the embedded space is not
        # split by the host shell before pyperclip supplies it to EU5.
        driver("console", f'load "{checkpoint.as_posix()}"', "--paste", "--settle", "2", "--leave-open")
        driver("screenshot", "console_load_command", "--session", args.session)
        driver("key", "0x29", "--scan", "--settle", "1")
        driver("wait-loading-complete", "--timeout", "300", "--stable-frames", "5", "--require-loading-plate", "--session", args.session)
        driver("screenshot", "console_load_complete", "--session", args.session)
        loaded = save_and_wait(args.output)
        actual = read_date(loaded)
        result = {"checkpoint": str(checkpoint), "expected": expected, "loaded": str(loaded), "actual": actual}
        (ROOT / "docs/r5/console_checkpoint_probe.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2))
        if actual != expected:
            raise RuntimeError(f"console load changed checkpoint date: {expected} -> {actual}")
    finally:
        subprocess.run([sys.executable, "tools/gamedriver.py", "stop"], cwd=ROOT, check=False)
    print("r5_console_checkpoint_probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
