#!/usr/bin/env python3
"""Reject personal identity and machine-local paths in tracked artifacts."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import threading
from collections.abc import Iterable, Iterator
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ALLOW = {"docs/ANTIQVITAS_MASTER_PLAN.md", "config/local_paths.example.json"}
PATTERNS = (
    ("Windows user profile", re.compile(rb"[A-Za-z]:[\\/]+Users[\\/]+(?!<USER>)[^\\/\s\"']+", re.I)),
    ("local Steam library", re.compile(rb"[A-Za-z]:[\\/]+(?:SteamLibrary|Steam)[\\/]", re.I)),
    ("local ANTIQVITAS path", re.compile(rb"[A-Za-z]:[\\/]+antiqvitas(?:_user_data|_runtime)?(?:[\\/]|\b)", re.I)),
    ("escaped Windows user profile", re.compile(rb"[A-Za-z]:\\\\Users\\\\(?!<USER>)[^\\\"']+", re.I)),
    ("escaped local Steam library", re.compile(rb"[A-Za-z]:\\\\(?:SteamLibrary|Steam)\\\\", re.I)),
    ("escaped local ANTIQVITAS path", re.compile(rb"[A-Za-z]:\\\\antiqvitas(?:_user_data|_runtime)?(?:\\\\|\b)", re.I)),
    ("UTF-16 Windows user profile", re.compile(rb"[A-Za-z]\x00:\x00[\\/]\x00U\x00s\x00e\x00r\x00s\x00[\\/]\x00", re.I)),
    ("UTF-16 local Steam library", re.compile(rb"[A-Za-z]\x00:\x00[\\/]\x00S\x00t\x00e\x00a\x00m\x00(?:L\x00i\x00b\x00r\x00a\x00r\x00y\x00)?[\\/]\x00", re.I)),
    ("UTF-16 local ANTIQVITAS path", re.compile(rb"[A-Za-z]\x00:\x00[\\/]\x00a\x00n\x00t\x00i\x00q\x00v\x00i\x00t\x00a\x00s\x00", re.I)),
)
PUBLIC_EMAILS = (
    re.compile(rb"^[^@]+@users\.noreply\.github\.com$", re.I),
    re.compile(rb"^noreply@github\.com$", re.I),
)
LOCAL_USER_TOKENS = {
    value.encode("utf-8")
    for value in (
        os.environ.get("USERNAME", ""),
        os.environ.get("USER", ""),
        Path.home().name,
    )
    if len(value) >= 4 and value.casefold() not in {"user", "users", "runner", "system"}
}
LOCAL_USER_PATTERNS = tuple(
    re.compile(
        rb"(?:user(?:_?name)?|created_?by|author|owner)[\"']?\s*[:=]\s*[\"']?"
        + re.escape(token) + rb"(?![A-Za-z0-9])",
        re.I,
    )
    for token in LOCAL_USER_TOKENS
)
SCAN_CHUNK_SIZE = 1024 * 1024
SCAN_OVERLAP = 4096
PATH_NEEDLES = (
    b"users", b"steam", b"antiqvitas",
    b"u\x00s\x00e\x00r\x00s\x00",
    b"s\x00t\x00e\x00a\x00m\x00",
    b"a\x00n\x00t\x00i\x00q\x00v\x00i\x00t\x00a\x00s\x00",
) + tuple(token.lower() for token in LOCAL_USER_TOKENS)


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
    )
    return [ROOT / raw.decode("utf-8") for raw in result.stdout.split(b"\0") if raw]


def public_identity_failures() -> list[str]:
    failures: list[str] = []
    result = subprocess.run(
        ["git", "log", "--all", "--format=%H%x00%ae%x00%ce"],
        cwd=ROOT, check=True, capture_output=True,
    )
    for row in result.stdout.splitlines():
        fields = row.split(b"\0")
        if len(fields) != 3:
            failures.append("git log returned malformed identity metadata")
            continue
        commit, author, committer = fields
        for role, email in (("author", author), ("committer", committer)):
            email = email.strip()
            if email and not any(pattern.fullmatch(email) for pattern in PUBLIC_EMAILS):
                failures.append(
                    f"commit {commit.decode()[:12]}: non-public {role} email"
                )
    refs = subprocess.run(
        ["git", "for-each-ref", "--format=%(refname)%00%(taggeremail)"],
        cwd=ROOT, check=True, capture_output=True,
    )
    for row in refs.stdout.splitlines():
        ref, _, email = row.partition(b"\0")
        email = email.strip().strip(b"<>")
        if email and not any(pattern.fullmatch(email) for pattern in PUBLIC_EMAILS):
            failures.append(f"{ref.decode()}: non-public tagger email")
    historical_config = subprocess.run(
        ["git", "log", "--all", "--format=%H", "--", "config/local_paths.json"],
        cwd=ROOT, check=True, capture_output=True, text=True,
    ).stdout.strip()
    if historical_config:
        failures.append("config/local_paths.json exists in reachable history")
    return failures


def scan_block(block: bytes, base: int) -> tuple[str, int] | None:
    lowered = block.lower()
    if not any(needle in lowered for needle in PATH_NEEDLES):
        return None
    for label, pattern in PATTERNS:
        match = pattern.search(block)
        if match:
            return label, base + match.start()
    for pattern in LOCAL_USER_PATTERNS:
        match = pattern.search(block)
        if match:
            return "local username", base + match.start()
    return None


def scan_chunks(chunks: Iterable[bytes]) -> tuple[str, int] | None:
    tail = b""
    consumed = 0
    for chunk in chunks:
        block = tail + chunk
        base = consumed - len(tail)
        found = scan_block(block, base)
        if found:
            return found
        consumed += len(chunk)
        tail = block[-SCAN_OVERLAP:]
    return None


def file_chunks(path: Path) -> Iterator[bytes]:
    with path.open("rb") as handle:
        while chunk := handle.read(SCAN_CHUNK_SIZE):
            yield chunk


def historical_blob_failures() -> list[str]:
    result = subprocess.run(
        ["git", "rev-list", "--objects", "--all"],
        cwd=ROOT, check=True, capture_output=True,
    )
    candidates: dict[str, str] = {}
    for row in result.stdout.splitlines():
        oid, separator, raw_path = row.partition(b" ")
        path = (
            raw_path.decode("utf-8", "replace")
            if separator else f"<git-object:{oid.decode()}>"
        )
        if path in ALLOW:
            continue
        candidates.setdefault(oid.decode(), path)

    process = subprocess.Popen(
        ["git", "cat-file", "--batch"], cwd=ROOT,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
    )
    assert process.stdin is not None and process.stdout is not None

    def feed() -> None:
        assert process.stdin is not None
        process.stdin.write("".join(f"{oid}\n" for oid in candidates).encode())
        process.stdin.close()

    writer = threading.Thread(target=feed, daemon=True)
    writer.start()
    failures: list[str] = []
    for _ in candidates:
        header = process.stdout.readline().decode("ascii", "replace").split()
        if len(header) < 3:
            failures.append("git cat-file returned a malformed history header")
            break
        oid, kind, raw_size = header[:3]
        remaining = int(raw_size)
        found: tuple[str, int] | None = None
        tail = b""
        consumed = 0
        while remaining:
            chunk = process.stdout.read(min(remaining, SCAN_CHUNK_SIZE))
            if not chunk:
                failures.append("git cat-file ended inside a history blob")
                remaining = 0
                break
            remaining -= len(chunk)
            if found is None:
                block = tail + chunk
                base = consumed - len(tail)
                found = scan_block(block, base)
                tail = block[-SCAN_OVERLAP:]
                consumed += len(chunk)
        process.stdout.read(1)
        if kind != "blob":
            continue
        if found:
            failures.append(
                f"{candidates[oid]}@byte{found[1]}: historical {found[0]}"
            )
    writer.join()
    if process.wait() != 0:
        failures.append("git cat-file failed while scanning history")
    return failures


def sanitize(files: list[Path]) -> int:
    config_path = ROOT / "config/local_paths.json"
    if not config_path.is_file():
        raise ValueError("config/local_paths.json is required for --write")
    config = json.loads(config_path.read_text(encoding="utf-8-sig"))
    replacements: dict[str, str] = {
        str(config.get("mod_dir", "")): "<MOD_DIR>",
        str(config.get("game_exe", "")): "<GAME_EXE>",
        str(config.get("game_manifest", "")): "<GAME_MANIFEST>",
        str(config.get("game_dir", "")): "<GAME_DIR>",
        str(config.get("repo_dir", "")): "<REPO_DIR>",
        str(config.get("user_dir", "")): "<EU5_USER_DIR>",
        str(config.get("candidate_relocated_user_dir", "")): "<EU5_USER_DIR>",
        str(config.get("original_user_dir", "")): "<EU5_USER_DIR>",
        str(config.get("documents_dir", "")): "<USER_DOCUMENTS>",
        str(config.get("steam_exe", "")): "<STEAM_EXE>",
        str(config.get("steam_dir", "")): "<STEAM_DIR>",
    }
    for library in config.get("steam_libraries", []):
        replacements[str(library)] = "<STEAM_LIBRARY>"
    replacements = {
        source: token for source, token in replacements.items()
        if source and re.match(r"^[A-Za-z]:[\\/]", source)
    }
    changed = 0
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        if relative in ALLOW or not path.is_file() or path.suffix.casefold() not in TEXT_SUFFIXES:
            continue
        data = path.read_bytes()
        rendered = data
        for source, token in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
            pairs = (
                (source, token),
                (source.replace("\\", "\\\\"), token),
                (source.replace("\\", "/"), token),
            )
            for old, new in pairs:
                rendered = rendered.replace(old.encode("utf-8"), new.encode("utf-8"))
        if rendered != data:
            path.write_bytes(rendered)
            changed += 1
    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument(
        "--history", action="store_true",
        help="also scan every unique reachable historical blob",
    )
    args = parser.parse_args()
    files = tracked_files()
    if args.write:
        try:
            changed = sanitize(files)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"public_release_guard: FAIL\n  - {exc}")
            return 1
        print(f"public_release_guard: sanitized {changed} tracked files")
    failures = public_identity_failures()
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        if relative in ALLOW or not path.is_file():
            continue
        found = scan_chunks(file_chunks(path))
        if found:
            failures.append(f"{relative}@byte{found[1]}: {found[0]}")
    if args.history:
        failures.extend(historical_blob_failures())
    if failures:
        print("public_release_guard: FAIL")
        print("\n".join(f"  - {item}" for item in failures))
        return 1
    scope = "tracked files and reachable object history" if args.history else "tracked files and identities"
    print(f"public_release_guard: PASS ({len(files)} {scope}; no local identity/path leakage)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
