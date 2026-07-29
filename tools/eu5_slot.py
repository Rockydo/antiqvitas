#!/usr/bin/env python3
"""Cross-repository, process-safe ownership of the single EU5 test slot.

ENDÓRË and ANTIQVITAS have isolated repositories and user directories, but
share one Steam installation, renderer, and desktop.  This module provides a
small filesystem lease protocol that serializes only real game sessions.
Static validation remains completely independent.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psutil

PROTOCOL_VERSION = 1
EX_TEMPFAIL = 75
TOKEN_ENV = "EU5_SLOT_TOKEN"
SCOPE_ENV = "EU5_SLOT_SCOPE"
ROOT_ENV = "EU5_SLOT_ROOT"
GAME_VISIBLE_ROOTS = (".metadata", "in_game", "main_menu", "loading_screen")


class SlotProtocolError(RuntimeError):
    """The shared state is malformed or does not match this implementation."""


class SlotBusy(RuntimeError):
    """Another live process owns EU5, or an unmanaged EU5 process exists."""

    def __init__(self, owner: dict[str, Any]):
        self.owner = owner
        super().__init__(busy_message(owner))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_config(root: Path) -> dict[str, Any]:
    return json.loads(
        (root / "config/local_paths.json").read_text(encoding="utf-8-sig")
    )


def project_name(root: Path) -> str:
    config = load_config(root)
    return Path(str(config.get("repo_dir", root))).name.lower()


def shared_root(root: Path) -> Path:
    override = os.environ.get(ROOT_ENV)
    if override:
        return Path(override)
    config = load_config(root)
    return Path(str(config["work_drive"])) / "eu5_runtime" / "slot"


def runtime_state_directory(root: Path) -> Path:
    config = load_config(root)
    configured = config.get("runtime_state_dir")
    if configured:
        return Path(str(configured))
    return (
        Path(str(config["work_drive"]))
        / f"{project_name(root)}_runtime"
        / "state"
    )


def _lease_dir(root: Path) -> Path:
    return shared_root(root) / "lease"


def _owner_path(root: Path) -> Path:
    return _lease_dir(root) / "owner.json"


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.parent / f".{path.name}.{uuid.uuid4().hex}.tmp"
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _read_owner(root: Path, *, retry_initialization: bool = True) -> dict[str, Any] | None:
    path = _owner_path(root)
    attempts = 20 if retry_initialization else 1
    for _ in range(attempts):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            if not _lease_dir(root).exists():
                return None
            time.sleep(0.01)
            continue
        except (OSError, json.JSONDecodeError) as exc:
            raise SlotProtocolError(f"could not read EU5 slot owner: {exc}") from exc
        if int(value.get("protocol", -1)) != PROTOCOL_VERSION:
            raise SlotProtocolError(
                "EU5 slot protocol mismatch: "
                f"owner={value.get('protocol')!r}, local={PROTOCOL_VERSION}"
            )
        return value
    return None


def _process_matches(pid: object, create_time: object) -> bool:
    try:
        process = psutil.Process(int(pid))
        return abs(process.create_time() - float(create_time)) < 0.01
    except (psutil.AccessDenied, psutil.NoSuchProcess, TypeError, ValueError):
        return False


def owner_is_live(owner: dict[str, Any]) -> bool:
    return _process_matches(owner.get("owner_pid"), owner.get("owner_create_time"))


def _quarantine_stale(root: Path) -> bool:
    lease = _lease_dir(root)
    if not lease.exists():
        return True
    stale = shared_root(root) / f"stale-{uuid.uuid4().hex}"
    try:
        os.replace(lease, stale)
    except (FileNotFoundError, PermissionError, OSError):
        return False
    shutil.rmtree(stale, ignore_errors=True)
    return True


def inspect_owner(root: Path, *, reclaim_stale: bool = True) -> dict[str, Any] | None:
    if not _lease_dir(root).exists():
        return None
    owner = _read_owner(root)
    if owner is not None and owner_is_live(owner):
        return owner
    if reclaim_stale:
        _quarantine_stale(root)
        return None
    return owner


def configured_game_processes(root: Path) -> list[psutil.Process]:
    expected = Path(str(load_config(root)["game_exe"])).resolve()
    result: list[psutil.Process] = []
    for process in psutil.process_iter(("pid", "exe")):
        try:
            executable = process.info.get("exe")
            if executable and Path(str(executable)).resolve() == expected:
                result.append(process)
        except (psutil.AccessDenied, psutil.NoSuchProcess, OSError):
            continue
    return result


def _unmanaged_owner(processes: list[psutil.Process]) -> dict[str, Any]:
    process = processes[0]
    try:
        created = process.create_time()
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        created = None
    return {
        "protocol": PROTOCOL_VERSION,
        "project": "unmanaged",
        "operation": "existing EU5 session",
        "owner_pid": process.pid,
        "owner_create_time": created,
        "acquired_at": None,
        "unmanaged": True,
    }


def busy_message(owner: dict[str, Any]) -> str:
    return (
        "EU5 slot busy"
        f" (project={owner.get('project', 'unknown')},"
        f" operation={owner.get('operation', 'unknown')},"
        f" pid={owner.get('owner_pid', 'unknown')},"
        f" since={owner.get('acquired_at', 'unknown')})"
    )


@dataclass
class SlotLease:
    root: Path
    token: str
    scope: str
    inherited: bool = False
    released: bool = False

    def child_environment(self) -> dict[str, str]:
        environment = os.environ.copy()
        environment[TOKEN_ENV] = self.token
        environment[SCOPE_ENV] = self.scope
        environment[ROOT_ENV] = str(shared_root(self.root))
        return environment

    def update(self, **fields: Any) -> dict[str, Any]:
        return update_owner(self.root, self.token, **fields)

    def handoff(self, process: psutil.Process, *, operation: str) -> dict[str, Any]:
        owner = self.update(
            owner_pid=process.pid,
            owner_create_time=process.create_time(),
            eu5_pid=process.pid,
            eu5_create_time=process.create_time(),
            operation=operation,
            handed_off_at=utc_now(),
        )
        self.inherited = True
        return owner

    def release(self) -> None:
        if self.released or self.inherited:
            return
        release_token(self.root, self.token)
        self.released = True

    def __enter__(self) -> "SlotLease":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.release()


def acquire(
    root: Path,
    operation: str,
    *,
    fingerprint: str | None = None,
    scope: str = "transaction",
    allow_inherited: bool = True,
    check_existing_game: bool = True,
) -> SlotLease:
    """Acquire immediately or raise SlotBusy; this function never waits."""
    root = root.resolve()
    inherited_token = os.environ.get(TOKEN_ENV) if allow_inherited else None
    if inherited_token:
        owner = require_token(root, inherited_token)
        if Path(str(owner.get("repo", root))).resolve() != root:
            raise SlotProtocolError("inherited EU5 slot belongs to a different repository")
        return SlotLease(
            root=root,
            token=inherited_token,
            scope=os.environ.get(SCOPE_ENV, "transaction"),
            inherited=True,
        )

    base = shared_root(root)
    base.mkdir(parents=True, exist_ok=True)
    token = uuid.uuid4().hex
    process = psutil.Process()
    owner = {
        "protocol": PROTOCOL_VERSION,
        "token": token,
        "project": project_name(root),
        "repo": str(root),
        "user_dir": str(load_config(root)["user_dir"]),
        "game_exe": str(load_config(root)["game_exe"]),
        "game_build_id": str(load_config(root).get("game_build_id", "")),
        "operation": operation,
        "scope": scope,
        "owner_pid": process.pid,
        "owner_create_time": process.create_time(),
        "acquired_at": utc_now(),
        "tree_fingerprint": fingerprint,
    }
    for _ in range(3):
        try:
            _lease_dir(root).mkdir()
        except FileExistsError:
            current = inspect_owner(root, reclaim_stale=True)
            if current is not None:
                raise SlotBusy(current)
            continue
        _atomic_json(_owner_path(root), owner)
        unmanaged = configured_game_processes(root) if check_existing_game else []
        if unmanaged:
            release_token(root, token)
            raise SlotBusy(_unmanaged_owner(unmanaged))
        return SlotLease(root=root, token=token, scope=scope)
    current = inspect_owner(root, reclaim_stale=False) or {
        "project": "unknown",
        "operation": "slot transition",
        "owner_pid": "unknown",
        "acquired_at": "unknown",
    }
    raise SlotBusy(current)


def require_token(root: Path, token: str) -> dict[str, Any]:
    owner = inspect_owner(root, reclaim_stale=False)
    if owner is None:
        raise SlotProtocolError("EU5 slot is not owned")
    if owner.get("token") != token:
        raise SlotProtocolError("EU5 slot token does not match the active owner")
    if not owner_is_live(owner):
        raise SlotProtocolError("EU5 slot owner process is no longer alive")
    return owner


def update_owner(root: Path, token: str, **fields: Any) -> dict[str, Any]:
    owner = require_token(root, token)
    owner.update(fields)
    owner["updated_at"] = utc_now()
    _atomic_json(_owner_path(root), owner)
    return owner


def release_token(root: Path, token: str) -> bool:
    owner = _read_owner(root, retry_initialization=False)
    if owner is None:
        return False
    if owner.get("token") != token:
        raise SlotProtocolError("refusing to release another EU5 slot owner")
    lease = _lease_dir(root)
    stale = shared_root(root) / f"released-{uuid.uuid4().hex}"
    try:
        os.replace(lease, stale)
    except FileNotFoundError:
        return False
    shutil.rmtree(stale, ignore_errors=True)
    return True


def game_visible_fingerprint(root: Path) -> str:
    """Hash HEAD plus every dirty/untracked game-visible file."""

    def git(*args: str) -> bytes:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode:
            raise RuntimeError(
                f"git {' '.join(args)} failed: "
                + result.stderr.decode("utf-8", errors="replace")
            )
        return result.stdout

    digest = hashlib.sha256()
    digest.update(b"eu5-game-tree-v1\0")
    digest.update(git("rev-parse", "HEAD").strip())
    pathspec = ("--", *GAME_VISIBLE_ROOTS)
    tracked = git(
        "diff",
        "--name-only",
        "-z",
        "--diff-filter=ACDMRTUXB",
        "HEAD",
        *pathspec,
    )
    untracked = git(
        "ls-files",
        "--others",
        "--exclude-standard",
        "-z",
        *pathspec,
    )
    paths = {
        item.decode("utf-8", errors="surrogateescape")
        for item in (tracked + untracked).split(b"\0")
        if item
    }
    for relative in sorted(paths):
        digest.update(b"\0path\0")
        digest.update(relative.encode("utf-8", errors="surrogateescape"))
        path = root / relative
        if not path.is_file():
            digest.update(b"\0deleted")
            continue
        digest.update(b"\0file\0")
        with path.open("rb") as handle:
            while block := handle.read(1024 * 1024):
                digest.update(block)
    return digest.hexdigest()


def pending_path(root: Path) -> Path:
    return runtime_state_directory(root) / "pending_eu5_gate.json"


def mark_pending(
    root: Path,
    operation: str,
    fingerprint: str,
    owner: dict[str, Any],
) -> Path:
    target = pending_path(root)
    _atomic_json(
        target,
        {
            "protocol": PROTOCOL_VERSION,
            "project": project_name(root),
            "operation": operation,
            "requested_at": utc_now(),
            "tree_fingerprint": fingerprint,
            "blocked_by": {
                key: owner.get(key)
                for key in (
                    "project",
                    "operation",
                    "owner_pid",
                    "owner_create_time",
                    "acquired_at",
                    "unmanaged",
                )
            },
        },
    )
    return target


def clear_pending(root: Path) -> None:
    target = pending_path(root)
    try:
        target.unlink()
    except FileNotFoundError:
        pass


def smoke_report_path(root: Path) -> Path:
    return runtime_state_directory(root) / "last_smoke.json"


def assert_smoked(root: Path) -> tuple[bool, str]:
    report_path = smoke_report_path(root)
    if not report_path.is_file():
        return False, "no smoke report exists"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    expected = game_visible_fingerprint(root)
    actual = report.get("tree_fingerprint")
    if report.get("new"):
        return False, "last smoke report is red"
    if actual != expected:
        return (
            False,
            f"last smoke covered {actual or 'no fingerprint'}, current tree is {expected}",
        )
    return True, f"last smoke covers current game-visible tree {expected}"


def _status_payload(root: Path) -> dict[str, Any]:
    owner = inspect_owner(root, reclaim_stale=True)
    return {
        "protocol": PROTOCOL_VERSION,
        "available": owner is None and not configured_game_processes(root),
        "owner": owner,
        "unmanaged_eu5_pids": [
            process.pid for process in configured_game_processes(root)
        ],
        "pending": (
            json.loads(pending_path(root).read_text(encoding="utf-8"))
            if pending_path(root).is_file()
            else None
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=("status", "fingerprint", "assert-smoked"),
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.command == "status":
        print(json.dumps(_status_payload(root), indent=2))
        return 0
    if args.command == "fingerprint":
        print(game_visible_fingerprint(root))
        return 0
    valid, message = assert_smoked(root)
    print(f"eu5_slot: {'PASS' if valid else 'FAIL'} — {message}")
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
