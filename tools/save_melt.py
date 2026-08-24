#!/usr/bin/env python3
"""Expose production EU5 saves as strict plaintext audit inputs.

EU5 writes binary Jomini envelopes outside debug mode.  Runtime gates must use
that production mode, so their save assertions need a deterministic melter.
The executable is cached outside the repository and its release archive is
accepted only when its pinned SHA-256 digest matches.
"""

from __future__ import annotations

import contextlib
import hashlib
import re
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile
from collections.abc import Iterator
from pathlib import Path

from runtime_state import directory


ROOT = Path(__file__).resolve().parents[1]
RAKALY_VERSION = "0.8.16"
RAKALY_URL = (
    "https://github.com/rakaly/cli/releases/download/v0.8.16/"
    "rakaly-0.8.16-x86_64-pc-windows-msvc.zip"
)
RAKALY_ARCHIVE_SHA256 = (
    "b39b7b469769ed06ca8aae8e60e28142f93c8860729a37c1e2a8824047bf3a48"
)
ALLOWED_STRINGIFIED_UNKNOWN_KEYS = {
    # EU5 1.3.11 added this key after Rakaly 0.8.16's token table froze.  It is
    # the sole direct child of top-level achievement_data and contains only the
    # engine's whitespace-separated achievement-name set.  Gameplay/runtime
    # state must remain fully token-resolved.
    "0xd57": "achievement_data",
}
UNKNOWN_KEY_RE = re.compile(r"^(\t*)(__unknown_(0x[0-9a-f]+))=\{")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def rakaly_path() -> Path:
    target = directory(ROOT) / "tools" / "rakaly" / RAKALY_VERSION / "rakaly.exe"
    if target.is_file():
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="antq-rakaly-") as temporary:
        archive = Path(temporary) / "rakaly.zip"
        urllib.request.urlretrieve(RAKALY_URL, archive)  # noqa: S310 - pinned hash
        actual = sha256(archive)
        if actual != RAKALY_ARCHIVE_SHA256:
            raise RuntimeError(
                f"Rakaly archive checksum mismatch: {actual} != "
                f"{RAKALY_ARCHIVE_SHA256}"
            )
        with zipfile.ZipFile(archive) as bundle:
            members = [name for name in bundle.namelist() if name.endswith("/rakaly.exe")]
            if len(members) != 1:
                raise RuntimeError(f"unexpected Rakaly archive layout: {members}")
            extracted = Path(bundle.extract(members[0], temporary))
        staged = target.with_suffix(".tmp")
        shutil.copy2(extracted, staged)
        staged.replace(target)
    return target


def is_plaintext_save(path: Path) -> bool:
    with path.open("rb") as handle:
        prefix = handle.read(256)
    newline = prefix.find(b"\n")
    payload = prefix[newline + 1 :] if prefix.startswith(b"SAV") and newline >= 0 else prefix
    payload = payload.lstrip(b"\xef\xbb\xbf\r\n\t ")
    return payload.startswith((b"metadata=", b"meta_data=", b"date=", b"start_of_day="))


def validate_stringified_unknowns(path: Path) -> None:
    """Accept only explicitly documented, metadata-only unknown token slots."""
    found: list[tuple[str, str]] = []
    parent_at_indent: dict[int, str] = {}
    with path.open(encoding="utf-8-sig", errors="strict") as handle:
        for raw in handle:
            stripped = raw.rstrip("\r\n")
            indent = len(stripped) - len(stripped.lstrip("\t"))
            content = stripped.lstrip("\t")
            match = UNKNOWN_KEY_RE.match(stripped)
            if match:
                token = match.group(3)
                parent = parent_at_indent.get(indent - 1, "")
                found.append((token, parent))
            key_match = re.match(r"^([A-Za-z0-9_.:-]+)=\{$", content)
            if key_match:
                parent_at_indent[indent] = key_match.group(1)
                for depth in tuple(parent_at_indent):
                    if depth > indent:
                        parent_at_indent.pop(depth, None)
    if not found:
        raise RuntimeError("stringified save did not expose the reported unknown token")
    rejected = [
        (token, parent)
        for token, parent in found
        if ALLOWED_STRINGIFIED_UNKNOWN_KEYS.get(token) != parent
    ]
    if rejected:
        raise RuntimeError(f"unknown gameplay save tokens are not allowed: {rejected}")


@contextlib.contextmanager
def plaintext_save(path: Path) -> Iterator[Path]:
    """Yield *path* directly when textual, otherwise a strict cached melt."""
    path = path.resolve()
    if is_plaintext_save(path):
        yield path
        return
    cache = directory(ROOT) / "save_melts"
    cache.mkdir(parents=True, exist_ok=True)
    target = cache / f"{path.stem}-{sha256(path)[:20]}.eu5"
    if not target.is_file() or target.stat().st_size == 0:
        staged = target.with_suffix(".tmp")
        command = [
            str(rakaly_path()),
            "melt",
            str(path),
            "--format",
            "eu5",
            "--unknown-key",
            "error",
            "--out",
            str(staged),
        ]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0 or not staged.is_file() or staged.stat().st_size == 0:
            staged.unlink(missing_ok=True)
            detail = (result.stderr or result.stdout).strip()
            if "unknown token:" not in detail:
                raise RuntimeError(f"strict EU5 save melt failed for {path}: {detail}")
            command[command.index("error")] = "stringify"
            fallback = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
            )
            if not staged.is_file() or staged.stat().st_size == 0:
                fallback_detail = (fallback.stderr or fallback.stdout).strip()
                raise RuntimeError(
                    f"stringified EU5 save melt failed for {path}: {fallback_detail}"
                )
            validate_stringified_unknowns(staged)
        staged.replace(target)
    yield target
