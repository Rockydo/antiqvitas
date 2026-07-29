#!/usr/bin/env python3
"""Machine-local contract tests for the shared EU5 lease protocol."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

from eu5_slot import (
    ROOT_ENV,
    SlotBusy,
    acquire,
    inspect_owner,
    release_token,
    shared_root,
)

ROOT = Path(__file__).resolve().parents[1]


def peer_root() -> Path:
    config = json.loads(
        (ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig")
    )
    work_drive = Path(str(config["work_drive"]))
    if ROOT.name.lower() == "antiqvitas":
        return work_drive / "EUV mods" / "endore"
    return work_drive / "antiqvitas"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    peer = peer_root()
    require((peer / "config/local_paths.json").is_file(), f"peer repo missing: {peer}")
    import runtime_state

    require(
        Path(runtime_state.__file__).resolve().parent == TOOLS,
        f"foreign runtime_state import: {runtime_state.__file__}",
    )
    test_root = ROOT / ".tmp" / f"eu5-slot-test-{uuid.uuid4().hex}"
    old_override = os.environ.get(ROOT_ENV)
    os.environ[ROOT_ENV] = str(test_root)
    child: subprocess.Popen[bytes] | None = None
    lease = None
    try:
        lease = acquire(
            ROOT,
            "unit-test-owner",
            fingerprint="test",
            allow_inherited=False,
            check_existing_game=False,
        )
        try:
            acquire(
                peer,
                "unit-test-contender",
                allow_inherited=False,
                check_existing_game=False,
            )
        except SlotBusy as exc:
            require(
                exc.owner.get("project") == ROOT.name.lower(),
                "busy owner did not identify the acquiring project",
            )
        else:
            raise AssertionError("second repository acquired an occupied EU5 slot")
        lease.release()
        require(inspect_owner(ROOT) is None, "released lease remained active")

        lease = acquire(
            ROOT,
            "unit-test-handoff",
            fingerprint="test",
            scope="session",
            allow_inherited=False,
            check_existing_game=False,
        )
        child = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        lease.handoff(
            __import__("psutil").Process(child.pid),
            operation="unit-test-eu5-session",
        )
        try:
            acquire(
                peer,
                "unit-test-contender",
                allow_inherited=False,
                check_existing_game=False,
            )
        except SlotBusy as exc:
            require(
                exc.owner.get("owner_pid") == child.pid,
                "handed-off lease did not bind to the child PID",
            )
        else:
            raise AssertionError("handoff did not preserve exclusive ownership")
        child.terminate()
        child.wait(timeout=10)
        child = None
        require(
            inspect_owner(peer, reclaim_stale=True) is None,
            "dead handed-off owner was not reclaimed",
        )

        lease = acquire(
            peer,
            "unit-test-stale",
            fingerprint="test",
            allow_inherited=False,
            check_existing_game=False,
        )
        owner_path = shared_root(peer) / "lease" / "owner.json"
        owner = json.loads(owner_path.read_text(encoding="utf-8"))
        owner["owner_pid"] = 999_999_999
        owner["owner_create_time"] = 0
        owner_path.write_text(
            json.dumps(owner, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        require(
            inspect_owner(ROOT, reclaim_stale=True) is None,
            "synthetic stale owner was not reclaimed",
        )
        lease = None
    finally:
        if child is not None:
            child.terminate()
            try:
                child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                child.kill()
        if lease is not None and not lease.inherited:
            try:
                release_token(ROOT, lease.token)
            except Exception:
                pass
        if old_override is None:
            os.environ.pop(ROOT_ENV, None)
        else:
            os.environ[ROOT_ENV] = old_override
        resolved = test_root.resolve()
        require(
            resolved.is_relative_to((ROOT / ".tmp").resolve()),
            f"unsafe test cleanup target: {resolved}",
        )
        shutil.rmtree(resolved, ignore_errors=True)
    print("eu5_slot_test: PASS (cross-repo exclusion, PID handoff, stale recovery)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
