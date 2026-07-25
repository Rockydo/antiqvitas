#!/usr/bin/env python3
"""Build and validate ancient character-scene backgrounds from reviewed 2x2 sheets."""

from __future__ import annotations

import argparse
import hashlib
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from dds import convert, identify


ROOT = Path(__file__).resolve().parents[1]
SHEET_SIZE = (1492, 1054)
MASTER_SIZE = (1080, 440)
RESOLVER = ROOT / "in_game/gfx/images/zzz_antq_throne_rooms.txt"
CONTACT = ROOT / "assets_queue/court_backgrounds/court_backgrounds_contact.png"

ROLE_TRIGGER = """\
\t\t\tOR = {
\t\t\t\tis_ruler = yes
\t\t\t\tis_regent = yes
\t\t\t\tis_heir = yes
\t\t\t\tis_consort = yes
\t\t\t\tis_infant = yes
\t\t\t\tis_child = yes
\t\t\t\tis_adolescent = yes
\t\t\t\tis_courtier = yes
\t\t\t\tis_alive = no
\t\t\t}"""


@dataclass(frozen=True)
class CourtArt:
    key: str
    title: str
    sheet: str
    quadrant: tuple[int, int]
    priority: int
    cultures: tuple[str, ...]

    @property
    def source(self) -> Path:
        return ROOT / self.sheet

    @property
    def master(self) -> Path:
        return ROOT / (
            f"assets_queue/court_backgrounds/masters/"
            f"antq_throne_room_{self.key}_1080x440.png"
        )

    @property
    def texture(self) -> Path:
        return ROOT / (
            f"main_menu/gfx/interface/illustrations/government/throne_rooms/"
            f"antq_throne_room_{self.key}.dds"
        )

    @property
    def texture_ref(self) -> str:
        return (
            f"gfx/interface/illustrations/government/throne_rooms/"
            f"antq_throne_room_{self.key}.dds"
        )


SHEET_1 = "assets_queue/court_backgrounds/generated/sheet_01_roman_hellenistic_celtic_germanic.png"
SHEET_2 = "assets_queue/court_backgrounds/generated/sheet_02_iranian_indic_han_near_eastern.png"
SHEET_3 = "assets_queue/court_backgrounds/generated/sheet_03_african_american_oceanian_neutral.png"

COURTS = (
    CourtArt("roman", "Roman and Italic", SHEET_1, (0, 0), 400, (
        "roman_gfx", "north_italian_gfx", "south_italian_gfx",
        "west_mediterranean_gfx", "mediterranean_gfx",
    )),
    CourtArt("hellenistic", "Hellenistic", SHEET_1, (1, 0), 390, (
        "greek_gfx", "east_mediterranean_gfx",
    )),
    CourtArt("celtic", "Celtic and Brittonic", SHEET_1, (0, 1), 380, (
        "celtic_gfx", "gaelic_gfx", "irish_gfx", "welsh_gfx", "breton_gfx",
        "british_gfx", "north_british_gfx", "cornish_gfx", "scottish_gfx",
        "scottish_highland_gfx", "scottish_lowland_gfx",
    )),
    CourtArt("germanic", "Germanic", SHEET_1, (1, 1), 370, (
        "gothic_gfx", "german_gfx", "north_german_gfx", "south_german_gfx",
        "english_gfx", "frisian_gfx", "danish_gfx", "norwegian_gfx",
        "swedish_gfx", "icelandic_gfx",
    )),
    CourtArt("iranian_steppe", "Iranian and Steppe", SHEET_2, (0, 0), 360, (
        "persian_gfx", "persianate_gfx", "central_asian_gfx", "turkic_gfx",
        "mongol_gfx",
    )),
    CourtArt("indic", "Indic", SHEET_2, (1, 0), 350, (
        "indian_gfx", "dravidian_gfx", "tibetan_gfx", "indochina_gfx",
    )),
    CourtArt("han_east_asian", "Han and East Asian", SHEET_2, (0, 1), 340, (
        "east_asian_gfx", "japanese_gfx", "korean_gfx", "ainu_gfx",
    )),
    CourtArt("near_eastern", "Near Eastern", SHEET_2, (1, 1), 330, (
        "middle_east_gfx", "levantine_gfx", "arabian_gfx", "egyptian_gfx",
        "caucasian_gfx", "israelite_gfx", "andalusi_gfx", "maghrebi_gfx",
    )),
    CourtArt("african", "African", SHEET_3, (0, 0), 320, (
        "african_gfx", "east_african_gfx", "bantu_gfx", "nubian_gfx",
        "mande_gfx", "saharan_gfx", "amazigh_gfx", "malagasy_gfx",
    )),
    CourtArt("american", "American", SHEET_3, (1, 0), 310, (
        "american_gfx", "north_american_gfx", "south_american_gfx",
        "amazonian_gfx", "iroquois_gfx", "aztec_gfx",
    )),
    CourtArt("oceanian", "Oceanian", SHEET_3, (0, 1), 300, (
        "austronesian_gfx", "polynesian_gfx", "papuan_gfx",
        "aboriginal_gfx", "negrito_gfx",
    )),
    CourtArt("neutral", "Neutral Ancient Fallback", SHEET_3, (1, 1), 100, ()),
)


def crop_quadrant(image: Image.Image, quadrant: tuple[int, int]) -> Image.Image:
    """Extract one panel, then center-crop it to EU5's 1080:440 composition."""
    qx, qy = quadrant
    panel_width, panel_height = 730, 510
    left = 8 + qx * 744
    top = 10 + qy * 524
    panel = image.crop((left, top, left + panel_width, top + panel_height))
    target_ratio = MASTER_SIZE[0] / MASTER_SIZE[1]
    crop_height = round(panel_width / target_ratio)
    trim = (panel_height - crop_height) // 2
    panel = panel.crop((0, trim, panel_width, trim + crop_height))
    return panel.resize(MASTER_SIZE, Image.Resampling.LANCZOS)


def entry(asset: CourtArt) -> str:
    if asset.cultures:
        culture_or = "\n".join(
            f"\t\t\t\t\tgfx_culture_applicable = {culture}" for culture in asset.cultures
        )
        trigger = (
            f"{ROLE_TRIGGER}\n"
            "\t\t\temployer ?= {\n"
            "\t\t\t\tOR = {\n"
            f"{culture_or}\n"
            "\t\t\t\t}\n"
            "\t\t\t}"
        )
    else:
        trigger = "			always = yes"
    return (
        f"\t# {asset.title}\n"
        "\tillustration_image = {\n"
        f'\t\ttexture_file = "{asset.texture_ref}"\n'
        f"\t\tpriority = {asset.priority}\n"
        "\t\tscope = character\n"
        "\t\ttrigger = {\n"
        f"{trigger}\n"
        "\t\t}\n"
        "\t}\n"
    )


def resolver_text() -> str:
    body = "\n".join(entry(asset) for asset in COURTS)
    return (
        "# ANTIQVITAS ancient character-scene resolver.\n"
        "# Priorities exceed the installed vanilla/DLC throne_room maximum (52).\n"
        "antq_throne_room_overrides = {\n"
        '\ttag = "throne_room"\n\n'
        f"{body}"
        "}\n"
    )


def dhash(path: Path) -> int:
    with Image.open(path) as image:
        gray = image.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
        pixels = list(gray.tobytes())
    value = 0
    for y in range(8):
        for x in range(8):
            value = (value << 1) | (pixels[y * 9 + x] > pixels[y * 9 + x + 1])
    return value


def hamming(left: int, right: int) -> int:
    return (left ^ right).bit_count()


def write_contact() -> None:
    margin, gap, label = 24, 16, 34
    thumb = (540, 220)
    canvas = Image.new("RGB", (2 * thumb[0] + 2 * margin + gap, 6 * (thumb[1] + label) + 2 * margin), "#101820")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default(size=20)
    for index, asset in enumerate(COURTS):
        col, row = index % 2, index // 2
        x = margin + col * (thumb[0] + gap)
        y = margin + row * (thumb[1] + label)
        with Image.open(asset.master) as image:
            canvas.paste(image.convert("RGB").resize(thumb, Image.Resampling.LANCZOS), (x, y))
        draw.text((x + 8, y + thumb[1] + 5), asset.title, fill="#e9dfc6", font=font)
    CONTACT.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(CONTACT)


def write() -> None:
    opened: dict[Path, Image.Image] = {}
    try:
        for asset in COURTS:
            if asset.source not in opened:
                opened[asset.source] = Image.open(asset.source).convert("RGB")
            asset.master.parent.mkdir(parents=True, exist_ok=True)
            crop_quadrant(opened[asset.source], asset.quadrant).save(asset.master)
            convert(asset.master, asset.texture, "dxt5", True)
    finally:
        for image in opened.values():
            image.close()
    RESOLVER.parent.mkdir(parents=True, exist_ok=True)
    RESOLVER.write_text(resolver_text(), encoding="utf-8-sig", newline="\n")
    write_contact()


def png_size(path: Path) -> tuple[int, int]:
    with Image.open(path) as image:
        if image.format != "PNG":
            raise ValueError(f"court-art source/master is not PNG: {path}")
        return image.size


def validate() -> None:
    if len(COURTS) != 12 or len({asset.key for asset in COURTS}) != len(COURTS):
        raise ValueError("court-art catalog must contain twelve unique entries")
    for source in {asset.source for asset in COURTS}:
        if not source.is_file() or png_size(source) != SHEET_SIZE:
            raise ValueError(f"missing or malformed reviewed court-art sheet: {source}")
    for asset in COURTS:
        for path, role in ((asset.master, "master"), (asset.texture, "texture")):
            if not path.is_file():
                raise ValueError(f"{asset.title} court-art {role} is missing: {path}")
        if png_size(asset.master) != MASTER_SIZE:
            raise ValueError(f"{asset.title} master has wrong dimensions: {asset.master}")
        details = identify(asset.texture)
        expected = {
            "format": "DDS", "width": "1080", "height": "440",
            "depth": "8", "channels": "srgba 4.0",
        }
        if details != expected:
            raise ValueError(f"{asset.title} DDS has unexpected format: {details}")
    hashes = [hashlib.sha256(asset.master.read_bytes()).hexdigest() for asset in COURTS]
    if len(set(hashes)) != len(hashes):
        raise ValueError("court-art masters contain a byte-identical duplicate")
    perceptual = [(asset.title, dhash(asset.master)) for asset in COURTS]
    for index, (left_name, left_hash) in enumerate(perceptual):
        for right_name, right_hash in perceptual[index + 1:]:
            if hamming(left_hash, right_hash) < 5:
                raise ValueError(f"court-art masters are perceptually near-identical: {left_name}, {right_name}")
    if min(asset.priority for asset in COURTS[:-1]) <= 52:
        raise ValueError("culture-specific court priorities no longer outrank installed vanilla/DLC")
    if COURTS[-1].key != "neutral" or COURTS[-1].priority <= 52 or COURTS[-1].cultures:
        raise ValueError("neutral ancient fallback must remain unconditional and above vanilla priority")
    cultures = [culture for asset in COURTS for culture in asset.cultures]
    if len(cultures) != len(set(cultures)):
        raise ValueError("a gfx culture is assigned to more than one court family")
    expected_resolver = resolver_text()
    if (
        not RESOLVER.is_file()
        or not RESOLVER.read_bytes().startswith(b"\xef\xbb\xbf")
        or RESOLVER.read_text(encoding="utf-8-sig") != expected_resolver
    ):
        raise ValueError(f"court-art resolver is stale: run {Path(__file__).name} --write")
    if not CONTACT.is_file():
        raise ValueError("court-art review contact sheet is missing")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="build masters, DDS textures, resolver, and contact sheet")
    parser.add_argument("--check", action="store_true", help="validate the fixed court-art set")
    args = parser.parse_args()
    if args.write:
        write()
    validate()
    print(f"m11_court_backgrounds: PASS ({len(COURTS)} reviewed ancient character scenes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
