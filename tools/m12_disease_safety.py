#!/usr/bin/env python3
"""Mirror and validate the installed disease-panel dependency contract.

The native Diseases lateral view requires both a populated start-manager state
and a complete mounted texture family.  The original empty ANTIQVITAS manager
crashed fresh starts, while debug logs also exposed an unresolved dynamic
``_default`` disease icon.  This tool derives the complete panel dependency set
from the installed files, copies the exact engine assets into their original
module roots, and pins both contracts in validation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
MANIFEST = ROOT / "docs/m12/disease_dependency_manifest.json"
REPORT = ROOT / "docs/m12/DISEASE_CRASH_FIX.md"
START = ROOT / "main_menu/setup/start/19_diseases.txt"
MODULES = ("main_menu", "loading_screen", "in_game")
GUI_FILES = (
    "in_game/gui/diseases_lateralview.gui",
    "in_game/gui/shared/diseases_tooltips.gui",
)
TEXTURE = re.compile(r'gfx/[A-Za-z0-9_./-]+\.dds')
DEFINITION = re.compile(r"(?m)^([a-z][a-z0-9_]*)\s*=\s*\{")
PERIOD_ART_DEPENDENCIES = {
    "gfx/interface/icons/location_icons/new/population.dds":
        "tools/m12_ui_resolver_art.py",
}


def game_root() -> Path:
    value = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
    return Path(value["game_dir"]) / "game"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mount_roots(game: Path) -> tuple[tuple[str, Path], ...]:
    roots: list[tuple[str, Path]] = []
    for module in MODULES:
        candidate = game / module
        if candidate.is_dir():
            roots.append((module, candidate))
    dlc = game / "dlc"
    if dlc.is_dir():
        for package in sorted(path for path in dlc.iterdir() if path.is_dir()):
            for module in MODULES:
                candidate = package / module
                if candidate.is_dir():
                    roots.append((module, candidate))
    return tuple(roots)


def disease_definitions(game: Path) -> tuple[str, ...]:
    definitions: set[str] = set()
    sources = [game / "in_game/common/diseases"]
    sources.extend(
        package / "in_game/common/diseases"
        for package in sorted((game / "dlc").glob("*"))
        if package.is_dir()
    )
    for directory in sources:
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*.txt")):
            definitions.update(
                match.group(1)
                for match in DEFINITION.finditer(
                    path.read_text(encoding="utf-8-sig", errors="strict")
                )
            )
    if not definitions:
        raise ValueError("installed disease definition union is empty")
    return tuple(sorted(definitions))


def literal_textures(game: Path) -> tuple[str, ...]:
    textures: set[str] = set()
    for relative in GUI_FILES:
        path = game / relative
        if not path.is_file():
            raise ValueError(f"missing installed disease GUI contract: {path}")
        textures.update(TEXTURE.findall(path.read_text(encoding="utf-8-sig")))
    return tuple(sorted(textures))


def resolve_source(
    roots: tuple[tuple[str, Path], ...], relative: str
) -> tuple[str, Path, tuple[str, ...]]:
    candidates: list[tuple[str, Path]] = []
    for module, root in roots:
        path = root / relative
        if path.is_file():
            candidates.append((module, path))
    if not candidates:
        raise ValueError(f"installed disease dependency has no source: {relative}")
    # No installed DLC currently replaces disease art. Taking the last mounted
    # candidate nevertheless makes a later package addition explicit in the
    # generated manifest instead of silently retaining the base asset.
    module, path = candidates[-1]
    return module, path, tuple(str(item[1]) for item in candidates)


def inventory() -> dict[str, object]:
    game = game_root()
    roots = mount_roots(game)
    definitions = disease_definitions(game)
    requested = set(literal_textures(game))
    requested.add("gfx/interface/icons/disease/_default.dds")
    requested.update(f"gfx/interface/icons/disease/{key}.dds" for key in definitions)

    assets: list[dict[str, object]] = []
    for relative in sorted(requested):
        if relative in PERIOD_ART_DEPENDENCIES:
            module = "main_menu"
            source = ROOT / module / relative
            if not source.is_file():
                raise ValueError(
                    f"period-art disease dependency is missing: {relative}"
                )
            candidates = (str(source),)
            owner = PERIOD_ART_DEPENDENCIES[relative]
        else:
            module, source, candidates = resolve_source(roots, relative)
            owner = "installed exact mirror"
        target = ROOT / module / relative
        assets.append(
            {
                "texture": relative,
                "module": module,
                "source": str(source),
                "source_candidates": list(candidates),
                "target": target.relative_to(ROOT).as_posix(),
                "sha256": sha256(source),
                "bytes": source.stat().st_size,
                "owner": owner,
            }
        )
    return {
        "game_version": "1.3.11",
        "installed_diseases": list(definitions),
        "gui_contracts": list(GUI_FILES),
        "asset_count": len(assets),
        "assets": assets,
        "start_manager": START.relative_to(ROOT).as_posix(),
        "start_encoding": "UTF-8 without BOM",
    }


def canonical_json(value: dict[str, object]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def report_bytes(value: dict[str, object]) -> bytes:
    diseases = ", ".join(f"`{key}`" for key in value["installed_diseases"])
    assets = int(value["asset_count"])
    return f"""<!-- Generated by tools/m12_disease_safety.py; do not edit. -->

# Diseases lateral-view crash repair

The 24 July manual crash and autonomous fresh-start reproduction both ended in
native `C0000005` immediately after opening Diseases. A vanilla-only fresh-start
control rendered the same panel normally. Mirroring the icon family did not
repair an old save created with the empty manager, whereas a genuinely fresh
AD 1 start with the populated manager survived four Rome cycles and one Observer
cycle. The empty disease manager is therefore the reproduced state fault; the
complete icon mirror closes the separate unresolved `_default` dependency
reported by debug logs.

The checked installed 1.3.11 union contains {len(value["installed_diseases"])}
disease definitions: {diseases}. The generated manifest mirrors {assets} exact
engine textures, including every dynamic disease icon, `_default.dds`, and every
literal DDS dependency requested by the installed disease panel/tooltips.
The shared population-summary dependency is intentionally owned by
`tools/m12_ui_resolver_art.py`, so the crash contract retains a complete texture
while displaying the ancient-period population group rather than vanilla
Renaissance figures. The
generated start manager is UTF-8 without BOM, initializes every installed disease
object, and seeds endemic malaria.

Runtime acceptance is recorded separately in
`docs/playtests/M12_DISEASE_PANEL_20260724.md`.
""".encode("utf-8")


def write() -> None:
    value = inventory()
    for asset in value["assets"]:
        source = Path(str(asset["source"]))
        target = ROOT / str(asset["target"])
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.resolve() != target.resolve():
            shutil.copy2(source, target)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_bytes(canonical_json(value))
    REPORT.write_bytes(report_bytes(value))
    print(
        "m12_disease_safety: wrote "
        f"{value['asset_count']} mounted dependencies for "
        f"{len(value['installed_diseases'])} diseases"
    )


def check() -> bool:
    failures: list[str] = []
    try:
        value = inventory()
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"m12_disease_safety: FAIL\n  - {exc}")
        return False

    start_raw = START.read_bytes()
    if start_raw.startswith(b"\xef\xbb\xbf"):
        failures.append(f"{START.relative_to(ROOT)} must not use a UTF-8 BOM")
    else:
        try:
            start_text = start_raw.decode("utf-8")
        except UnicodeDecodeError:
            failures.append(f"{START.relative_to(ROOT)} is not valid UTF-8")
            start_text = ""
        if not re.search(r"(?m)^disease_outbreak_manager\s*=\s*\{", start_text):
            failures.append(f"{START.relative_to(ROOT)} lacks disease_outbreak_manager")
        seeded = set(re.findall(r"(?m)^\s*type\s*=\s*([a-z0-9_]+)\s*$", start_text))
        missing_seeded = sorted(set(value["installed_diseases"]) - seeded)
        if missing_seeded:
            failures.append(
                f"{START.relative_to(ROOT)} does not initialize {missing_seeded}"
            )
        if "add_disease_outbreaks" not in start_text:
            failures.append(
                f"{START.relative_to(ROOT)} lacks an endemic disease seed"
            )
    if not MANIFEST.is_file() or MANIFEST.read_bytes() != canonical_json(value):
        failures.append(f"stale or missing {MANIFEST.relative_to(ROOT)}")
    if not REPORT.is_file() or REPORT.read_bytes() != report_bytes(value):
        failures.append(f"stale or missing {REPORT.relative_to(ROOT)}")
    for asset in value["assets"]:
        target = ROOT / str(asset["target"])
        if not target.is_file():
            failures.append(f"missing disease dependency {target.relative_to(ROOT)}")
        elif sha256(target) != asset["sha256"]:
            failures.append(f"stale disease dependency {target.relative_to(ROOT)}")
    if failures:
        print("m12_disease_safety: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return False
    print(
        "m12_disease_safety: PASS "
        f"({value['asset_count']} assets; "
        f"{len(value['installed_diseases'])} installed diseases)"
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        try:
            write()
        except (OSError, UnicodeError, ValueError) as exc:
            print(f"m12_disease_safety: FAIL\n  - {exc}", file=sys.stderr)
            return 1
        return 0
    return 0 if check() else 1


if __name__ == "__main__":
    raise SystemExit(main())
