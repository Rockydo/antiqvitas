#!/usr/bin/env python3
"""Paired one-year Round-5 population runtime and save audit."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POP_TYPES = {
    "nobles", "clergy", "burghers", "peasants", "laborers", "soldiers",
    "slaves", "tribesmen",
}


def save_directory() -> Path:
    config = json.loads(
        (ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig")
    )
    return Path(str(config["user_dir"])) / "save games"


def driver(*arguments: str) -> None:
    subprocess.run(
        [sys.executable, "tools/gamedriver.py", *arguments],
        cwd=ROOT,
        check=True,
    )


def launch(leavepops: bool) -> None:
    command = [sys.executable, "tools/gamedriver.py", "launch", "--mode", "mod"]
    if leavepops:
        command.append("--leavepops")
    for attempt in range(20):
        result = subprocess.run(command, cwd=ROOT, check=False)
        if result.returncode == 0:
            return
        if result.returncode != 75:
            result.check_returncode()
        time.sleep(15)
    raise RuntimeError("shared EU5 slot did not clear")


def save_path(stem: str) -> Path:
    return save_directory() / f"{stem}.eu5"


def save_date(path: Path) -> str:
    with path.open(encoding="utf-8-sig", errors="replace") as handle:
        for line_number, raw in enumerate(handle, 1):
            line = raw.strip()
            for prefix in ("start_of_day=", "date="):
                if line.startswith(prefix):
                    return line.removeprefix(prefix)
            if line_number >= 250_000:
                break
    raise RuntimeError(f"no date in {path}")


def verified_save(stem: str, settle: float = 8) -> Path:
    target = save_path(stem)
    if target.exists():
        target.unlink()
    driver("console", f"save {stem}", "--paste", "--settle", str(settle))
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        if target.is_file() and target.stat().st_size > 1_000_000:
            return target
        time.sleep(1)
    raise RuntimeError(f"console save was not created: {target}")


def pop_shares(path: Path) -> dict[str, float]:
    totals = {token: 0.0 for token in POP_TYPES}
    pending = ""
    remaining = 0
    with path.open(encoding="utf-8-sig", errors="replace") as handle:
        for raw in handle:
            line = raw.strip()
            if line.startswith("type="):
                candidate = line.removeprefix("type=")
                pending = candidate if candidate in POP_TYPES else ""
                remaining = 40 if pending else 0
                continue
            if pending and line.startswith("size="):
                totals[pending] += float(line.removeprefix("size="))
                pending = ""
                remaining = 0
            elif pending:
                remaining -= 1
                if remaining <= 0:
                    pending = ""
    total = sum(totals.values())
    if total <= 0:
        raise RuntimeError(f"no population blocks parsed from {path}")
    return {token: value / total for token, value in sorted(totals.items())}


def run_mode(mode: str, seconds: int) -> dict[str, object]:
    leavepops = mode == "leavepops"
    session = f"R5_POPULATION_{mode.upper()}_20260803"
    start_stem = f"r5_population_{mode}_start"
    end_stem = f"r5_population_{mode}_end"
    launch(leavepops)
    try:
        driver("wait", "--timeout", "300", "--minimum", "35", "--quiet-seconds", "20")
        driver(
            "capture-new-game-loading", "--session", session,
            "--x", "0.14", "--y", "0.382", "--percentages", "5",
            "--minimum-captures", "1", "--timeout", "480", "--interval", "0.05",
        )
        driver(
            "start-observer", "--session", session,
            "--country-selection-settle", "5", "--observer-enable-settle", "8",
            "--live-timeout", "90",
        )
        start = verified_save(start_stem)
        driver(
            "observer", "--seconds", str(seconds), "--maximum-speed",
            "--capture-interval", "30", "--status-interval", "15",
            "--session", session,
        )
        driver("screenshot", "one_year_end", "--session", session)
        # Pause before serializing.  Besides preventing date drift during a
        # 120 MB save, this restores the same proven console state as the
        # successful opening snapshot.
        driver("key", "0x39", "--scan", "--settle", "2")
        driver("screenshot", "one_year_end_paused", "--session", session)
        end = verified_save(end_stem)
    finally:
        subprocess.run(
            [sys.executable, "tools/gamedriver.py", "stop"], cwd=ROOT, check=False
        )
    return {
        "mode": mode,
        "start_date": save_date(start),
        "end_date": save_date(end),
        "start_shares": pop_shares(start),
        "end_shares": pop_shares(end),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=int, default=90)
    parser.add_argument("--mode", choices=("normal", "leavepops", "both"), default="both")
    args = parser.parse_args()
    modes = ("normal", "leavepops") if args.mode == "both" else (args.mode,)
    results = [run_mode(mode, args.seconds) for mode in modes]
    target = ROOT / "docs/r5/population_runtime.json"
    target.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    for result in results:
        share = result["end_shares"]["tribesmen"]
        print(
            f"{result['mode']}: {result['start_date']} -> {result['end_date']}; "
            f"tribesmen={share:.3%}"
        )
        year = int(str(result["end_date"]).split(".", 1)[0])
        if year < 2:
            raise RuntimeError(f"{result['mode']} did not complete one year")
        if not 0.20 <= share <= 0.26:
            raise RuntimeError(f"{result['mode']} tribesmen share drifted: {share:.3%}")
    print("r5_population_runtime: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
