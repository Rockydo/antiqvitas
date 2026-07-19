#!/usr/bin/env python3
"""Extract named EU5 location centroids from the installed location raster."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/vanilla_symbols/location_coordinates.json"
COLOR_LINE = re.compile(r"^\s*([^#=\s]+)\s*=\s*([0-9a-fA-F]+)\s*(?:#.*)?$")
ROW_HEIGHT = 64


def game_dir() -> Path:
    config = json.loads((ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig"))
    return Path(config["game_dir"])


def named_colors(source: Path) -> dict[str, int]:
    result: dict[str, int] = {}
    seen_colors: dict[int, str] = {}
    for path in sorted(source.rglob("*.txt")):
        for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
            match = COLOR_LINE.match(line)
            if not match:
                continue
            key, raw_color = match.groups()
            color = int(raw_color, 16)
            if key in result and result[key] != color:
                raise ValueError(f"{path}:{number}: duplicate location key {key}")
            if color in seen_colors and seen_colors[color] != key:
                raise ValueError(
                    f"{path}:{number}: color {raw_color} shared by {seen_colors[color]} and {key}"
                )
            result[key] = color
            seen_colors[color] = key
    if not result:
        raise ValueError(f"no named location colors under {source}")
    return result


def extract() -> dict[str, object]:
    base = game_dir() / "game/in_game/map_data"
    names = named_colors(base / "named_locations")
    ordered = sorted((color, key) for key, color in names.items())
    colors = np.asarray([item[0] for item in ordered], dtype=np.uint32)
    keys = [item[1] for item in ordered]
    counts = np.zeros(len(keys), dtype=np.uint64)
    sum_x = np.zeros(len(keys), dtype=np.float64)
    sum_y = np.zeros(len(keys), dtype=np.float64)
    Image.MAX_IMAGE_PIXELS = None
    with Image.open(base / "locations.png") as image:
        image = image.convert("RGB")
        width, height = image.size
        for top in range(0, height, ROW_HEIGHT):
            bottom = min(top + ROW_HEIGHT, height)
            pixels = np.asarray(image.crop((0, top, width, bottom)), dtype=np.uint8)
            packed = (
                (pixels[:, :, 0].astype(np.uint32) << 16)
                | (pixels[:, :, 1].astype(np.uint32) << 8)
                | pixels[:, :, 2].astype(np.uint32)
            ).reshape(-1)
            positions = np.arange(packed.size, dtype=np.uint32)
            found = np.searchsorted(colors, packed)
            valid = found < len(colors)
            valid &= colors[np.minimum(found, len(colors) - 1)] == packed
            if not valid.any():
                continue
            indices = found[valid]
            pixel_positions = positions[valid]
            counts += np.bincount(indices, minlength=len(keys)).astype(np.uint64)
            sum_x += np.bincount(
                indices, weights=(pixel_positions % width), minlength=len(keys)
            )
            sum_y += np.bincount(
                indices, weights=(top + pixel_positions // width), minlength=len(keys)
            )
    locations = {
        key: {
            "x": round(float(sum_x[index] / counts[index]), 3),
            "y": round(float(sum_y[index] / counts[index]), 3),
            "pixels": int(counts[index]),
        }
        for index, key in enumerate(keys)
        if counts[index]
    }
    config = json.loads((ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig"))
    return {
        "game_build": config["game_build_id"],
        "image_size": {"width": width, "height": height},
        "named_location_count": len(names),
        "mapped_location_count": len(locations),
        "locations": locations,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    if args.write:
        payload = extract()
        OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(
            f"map_coordinates: wrote {OUTPUT.relative_to(ROOT)} "
            f"({payload['mapped_location_count']} locations)"
        )
        return 0
    if not OUTPUT.is_file():
        print("map_coordinates: FAIL (missing coordinate index)")
        return 1
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    config = json.loads((ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig"))
    if payload.get("game_build") != config["game_build_id"]:
        print("map_coordinates: FAIL (coordinate index is from another game build)")
        return 1
    print(
        f"map_coordinates: PASS ({payload.get('mapped_location_count', 0)} locations; "
        f"{payload.get('image_size', {}).get('width')}x{payload.get('image_size', {}).get('height')})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
