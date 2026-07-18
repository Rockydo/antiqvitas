#!/usr/bin/env python3
"""ImageMagick wrapper for inspected PNG/DDS conversion and validation."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def magick() -> Path:
    local = ROOT / ".tools/ImageMagick/magick.exe"
    if local.is_file():
        return local
    return Path("magick")


def identify(path: Path) -> dict[str, str]:
    command = [
        str(magick()),
        "identify",
        "-format",
        "%m|%w|%h|%z|%[channels]",
        str(path),
    ]
    result = subprocess.run(command, check=True, text=True, capture_output=True)
    fmt, width, height, depth, channels = result.stdout.split("|", 4)
    return {
        "format": fmt,
        "width": width,
        "height": height,
        "depth": depth,
        "channels": channels,
    }


def convert(source: Path, target: Path, compression: str, mipmaps: bool) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    command = [str(magick()), str(source)]
    if mipmaps:
        command += ["-define", "dds:mipmaps=0"]
    command += ["-define", f"dds:compression={compression}", str(target)]
    subprocess.run(command, check=True)
    if identify(target)["format"] != "DDS":
        raise RuntimeError(f"ImageMagick did not create DDS: {target}")


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    inspect_parser = sub.add_parser("identify")
    inspect_parser.add_argument("path", type=Path)
    convert_parser = sub.add_parser("convert")
    convert_parser.add_argument("source", type=Path)
    convert_parser.add_argument("target", type=Path)
    convert_parser.add_argument("--compression", default="dxt5")
    convert_parser.add_argument("--no-mipmaps", action="store_true")
    args = parser.parse_args()
    if args.command == "identify":
        print(json.dumps(identify(args.path), indent=2))
    else:
        convert(args.source, args.target, args.compression, not args.no_mipmaps)
        print(json.dumps(identify(args.target), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
