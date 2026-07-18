#!/usr/bin/env python3
"""Discover Steam, EU5, storage, and user-data paths without user input."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import string
import sys
from datetime import datetime, timezone
from pathlib import Path

if os.name == "nt":
    import winreg

GAME_NAME = "Europa Universalis V"
GAME_EXE = Path("binaries/eu5.exe")
GAME_ROOT_SENTINELS = (
    Path("game/in_game"),
    Path("game/main_menu"),
    Path("game/loading_screen"),
)


def registry_value(hive: object, key: str, value: str) -> str | None:
    if os.name != "nt":
        return None
    try:
        with winreg.OpenKey(hive, key) as handle:
            result, _ = winreg.QueryValueEx(handle, value)
            return os.path.expandvars(str(result))
    except OSError:
        return None


def steam_root() -> Path:
    candidates: list[Path] = []
    if os.name == "nt":
        for value in ("SteamPath", "InstallPath"):
            found = registry_value(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", value)
            if found:
                candidates.append(Path(found))
        found = registry_value(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\WOW6432Node\Valve\Steam",
            "InstallPath",
        )
        if found:
            candidates.append(Path(found))
    candidates.extend(
        [
            Path(r"C:\Program Files (x86)\Steam"),
            Path(r"C:\Program Files\Steam"),
        ]
    )
    for candidate in candidates:
        if (candidate / "steam.exe").is_file():
            return candidate.resolve()
    raise RuntimeError("Steam installation could not be discovered")


def parse_library_paths(vdf: Path) -> list[Path]:
    text = vdf.read_text(encoding="utf-8", errors="replace")
    found = [
        Path(bytes(match, "utf-8").decode("unicode_escape"))
        for match in re.findall(r'"path"\s+"([^"]+)"', text)
    ]
    unique: list[Path] = []
    for path in found:
        resolved = path.resolve()
        if resolved not in unique:
            unique.append(resolved)
    return unique


def drive_candidates() -> list[Path]:
    if os.name != "nt":
        return []
    result = []
    for letter in "DG" + string.ascii_uppercase:
        root = Path(f"{letter}:\\")
        if root.exists() and root not in result:
            result.append(root)
    return result


def is_game_dir(path: Path) -> bool:
    return (path / GAME_EXE).is_file() and all((path / item).is_dir() for item in GAME_ROOT_SENTINELS)


def discover_game(steam: Path) -> tuple[Path, Path, list[Path]]:
    vdf = steam / "steamapps/libraryfolders.vdf"
    libraries = parse_library_paths(vdf) if vdf.is_file() else []
    for root in drive_candidates():
        library = root / "SteamLibrary"
        if library.exists() and library.resolve() not in libraries:
            libraries.append(library.resolve())
    priority = sorted(
        libraries,
        key=lambda path: (
            0 if path.drive.upper() in {"D:", "G:"} else 1,
            0 if path.drive.upper() == "G:" else 1,
            str(path).lower(),
        ),
    )
    for library in priority:
        candidate = library / "steamapps/common" / GAME_NAME
        if is_game_dir(candidate):
            return candidate.resolve(), library.resolve(), priority
    raise RuntimeError(f"{GAME_NAME} was not found in {len(priority)} Steam libraries")


def documents_dir() -> Path:
    if os.name == "nt":
        value = registry_value(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders",
            "Personal",
        )
        if value:
            return Path(value).resolve()
    return (Path.home() / "Documents").resolve()


def ascii_safe(path: Path) -> bool:
    try:
        str(path).encode("ascii")
        return True
    except UnicodeEncodeError:
        return False


def free_bytes(path: Path) -> int:
    return shutil.disk_usage(path.anchor or path).free


def app_manifest(library: Path) -> dict[str, str]:
    manifests = (library / "steamapps").glob("appmanifest_*.acf")
    for manifest in manifests:
        text = manifest.read_text(encoding="utf-8", errors="replace")
        if re.search(r'"name"\s+"Europa Universalis V"', text):
            pairs = dict(re.findall(r'"([^"]+)"\s+"([^"]*)"', text))
            pairs["manifest_path"] = str(manifest.resolve())
            return pairs
    return {}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "config/local_paths.json",
    )
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    steam = steam_root()
    game, library, libraries = discover_game(steam)
    documents = documents_dir()
    user_dir = documents / "Paradox Interactive" / GAME_NAME
    work_drive = Path(game.anchor)
    manifest = app_manifest(library)
    data = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "steam_dir": str(steam),
        "steam_exe": str((steam / "steam.exe").resolve()),
        "steam_libraries": [str(item) for item in libraries],
        "game_dir": str(game),
        "game_exe": str((game / GAME_EXE).resolve()),
        "game_build_id": manifest.get("buildid", ""),
        "game_app_id": manifest.get("appid", ""),
        "game_manifest": manifest.get("manifest_path", ""),
        "work_drive": str(work_drive),
        "repo_dir": str(repo),
        "documents_dir": str(documents),
        "user_dir": str(user_dir),
        "user_dir_ascii_safe": ascii_safe(user_dir),
        "candidate_relocated_user_dir": str(repo.parent / "antiqvitas_user_data"),
        "mod_dir": "",
        "mod_visibility": "unconfigured",
        "free_bytes": {
            "work_drive": free_bytes(work_drive),
            "system_drive": free_bytes(Path(os.environ.get("SystemDrive", "C:") + "\\")),
        },
    }
    if not is_game_dir(game):
        raise RuntimeError("GAME_DIR sentinel validation failed")
    if game.drive.upper() == "C:":
        raise RuntimeError("EU5 unexpectedly resolved to C:, violating the storage requirement")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(data, indent=2))
    if not data["user_dir_ascii_safe"]:
        print("WARNING: USER_DIR contains non-ASCII characters", file=sys.stderr)
    if data["free_bytes"]["system_drive"] < 5 * 1024**3:
        print("WARNING: system drive has less than 5 GiB free", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
