#!/usr/bin/env python3
"""ImageMagick wrapper for inspected PNG/DDS conversion and validation."""

from __future__ import annotations

import argparse
import json
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def magick() -> Path:
    local = ROOT / ".tools/ImageMagick/magick.exe"
    if local.is_file():
        return local
    return Path("magick")


def texconv() -> Path | None:
    """Return the optional local DirectXTex encoder used for BC7 surfaces."""
    local = ROOT / ".tools/DirectXTex/texconv.exe"
    return local if local.is_file() else None


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


def mipmap_dimensions(width: int, height: int) -> list[tuple[int, int]]:
    """Return classic DDS levels, halving dimensions with floor division."""
    levels = [(width, height)]
    while width != 1 or height != 1:
        width = max(1, width // 2)
        height = max(1, height // 2)
        levels.append((width, height))
    return levels


def convert_level(source: Path, target: Path, compression: str, width: int, height: int) -> None:
    command = [
        str(magick()),
        str(source),
        "-resize",
        f"{width}x{height}!",
        "-define",
        "dds:mipmaps=0",
        "-define",
        f"dds:compression={compression}",
        str(target),
    ]
    subprocess.run(command, check=True)


def write_mipmapped_dds(source: Path, target: Path, compression: str) -> None:
    """Build a complete DDS chain, including non-power-of-two textures.

    ImageMagick only creates automatic DDS mipmaps for power-of-two source
    dimensions.  EU5 streams the 1080x440 trade-good illustrations and
    requires a chain there as well, so each level is compressed by
    ImageMagick and their DDS payloads are assembled under one standard DDS
    header.
    """
    details = identify(source)
    width = int(details["width"])
    height = int(details["height"])
    levels = mipmap_dimensions(width, height)
    temp_root = ROOT / ".tmp"
    temp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="dds-mips-", dir=temp_root) as temporary:
        work = Path(temporary)
        encoded: list[bytes] = []
        for index, (level_width, level_height) in enumerate(levels):
            level = work / f"level_{index}.dds"
            convert_level(source, level, compression, level_width, level_height)
            raw = level.read_bytes()
            if not raw.startswith(b"DDS ") or len(raw) < 128:
                raise RuntimeError(f"ImageMagick did not create a standard DDS level: {level}")
            encoded.append(raw)
    header = bytearray(encoded[0][:128])
    flags = struct.unpack_from("<I", header, 8)[0] | 0x00020000
    caps = struct.unpack_from("<I", header, 108)[0] | 0x00000008 | 0x00400000
    struct.pack_into("<I", header, 8, flags)
    struct.pack_into("<I", header, 28, len(encoded))
    struct.pack_into("<I", header, 108, caps)
    target.write_bytes(bytes(header) + b"".join(raw[128:] for raw in encoded))


def convert(source: Path, target: Path, compression: str, mipmaps: bool) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    normalized = compression.casefold()
    if normalized in {"bc7", "bc7_srgb", "bc7_unorm_srgb"}:
        encoder = texconv()
        if encoder is None:
            raise RuntimeError(
                "BC7 conversion requires .tools/DirectXTex/texconv.exe; "
                "install the reviewed DirectXTex tool on the work drive"
            )
        temp_root = ROOT / ".tmp"
        temp_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="dds-bc7-", dir=temp_root) as temporary:
            output = Path(temporary)
            command = [
                str(encoder),
                "-nologo",
                "-y",
                "-f",
                "BC7_UNORM_SRGB",
                "-m",
                "0" if mipmaps else "1",
                "-o",
                str(output),
                str(source),
            ]
            subprocess.run(command, check=True)
            encoded = output / f"{source.stem}.dds"
            if not encoded.is_file():
                raise RuntimeError(f"DirectXTex did not create DDS: {encoded}")
            shutil.move(str(encoded), target)
    elif mipmaps:
        write_mipmapped_dds(source, target, compression)
    else:
        details = identify(source)
        convert_level(source, target, compression, int(details["width"]), int(details["height"]))
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
