#!/usr/bin/env python3
"""Inspect vanilla asset classes so generated art never guesses dimensions."""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLASSES = {
    "advance_icons": "main_menu/gfx/interface/advance",
    "building_icons": "main_menu/gfx/interface/icons/buildings",
    "estate_icons": "main_menu/gfx/interface/icons/estates",
    "event_illustrations": "main_menu/gfx/interface/illustrations/event",
    "goods_icons": "main_menu/gfx/interface/icons/trade_goods",
    "government_icons": "main_menu/gfx/interface/icons/government_types",
    "institution_icons": "main_menu/gfx/interface/icons/institutions",
    "religion_icons": "main_menu/gfx/interface/icons/religion",
    "loading_screens": "loading_screen/gfx/loadingscreens",
}


def identify(magick: Path, path: Path) -> tuple[str, int, int, int, str]:
    result = subprocess.run(
        [
            str(magick),
            "identify",
            "-format",
            "%m|%w|%h|%z|%[channels]",
            str(path),
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    fmt, width, height, depth, channels = result.stdout.split("|", 4)
    return fmt, int(width), int(height), int(depth), channels


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=12)
    parser.add_argument(
        "--output", type=Path, default=ROOT / "docs/vanilla_symbols/asset_manifest.json"
    )
    args = parser.parse_args()
    config = json.loads(
        (ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig")
    )
    game = Path(config["game_dir"]) / "game"
    magick = ROOT / ".tools/ImageMagick/magick.exe"
    if not magick.is_file():
        magick = Path("magick")
    manifest: dict[str, object] = {}
    for name, relative in CLASSES.items():
        directory = game / relative
        files = sorted(directory.rglob("*.dds")) if directory.exists() else []
        sample = files[: args.samples]
        formats: Counter[str] = Counter()
        examples = []
        for path in sample:
            try:
                fmt, width, height, depth, channels = identify(magick, path)
            except subprocess.CalledProcessError as exc:
                examples.append(
                    {"path": path.relative_to(game).as_posix(), "identify_error": exc.stderr}
                )
                continue
            key = f"{fmt} {width}x{height} {depth}-bit {channels}"
            formats[key] += 1
            examples.append(
                {
                    "path": path.relative_to(game).as_posix(),
                    "format": fmt,
                    "width": width,
                    "height": height,
                    "depth": depth,
                    "channels": channels,
                }
            )
        manifest[name] = {
            "directory": relative,
            "file_count": len(files),
            "sample_count": len(sample),
            "sample_formats": dict(formats),
            "examples": examples,
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value["sample_formats"] for key, value in manifest.items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
