#!/usr/bin/env python3
"""Build and validate the ancient pop-class presentation contract.

EU5's eight pop-type identifiers are engine-facing and heavily hardcoded.  This
tool retains those identifiers, replaces their player-facing language, and
deploys a direct ancient portrait to every installed generic, mapmode, and
graphical-culture resolver path.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from dds import convert, identify


ROOT = Path(__file__).resolve().parents[1]
GAME = Path(r"<GAME_DIR>\game")
ENGINE_POP_TYPES = GAME / "in_game/common/pop_types/00_default.txt"
SHEET_DIR = ROOT / "assets_queue/generated/pop_types/sheets"
MASTER_DIR = ROOT / "assets_queue/generated/pop_types/masters"
REFERENCE_DIR = ROOT / "assets_queue/references/pop_types"
GENERIC_DIR = ROOT / "main_menu/gfx/interface/icons/pops"
MAPMODE_DIR = ROOT / "main_menu/gfx/interface/icons/map_modes"
GRAPHICAL_ROOT = ROOT / "main_menu/gfx/interface/graphical_cultures"
LEDGER = ROOT / "docs/m12/pop_presentation.csv"
CONTACT_SHEET = ROOT / "docs/m12/pop_presentation_contact_sheet.png"
CHROMA_HELPER = (
    Path.home()
    / ".codex/skills/.system/imagegen/scripts/remove_chroma_key.py"
)
CLIENTS = (
    "english", "french", "german", "spanish", "polish", "russian",
    "braz_por", "simp_chinese", "japanese", "korean", "turkish",
)
REGIONS = (
    "generic", "african_gfx", "american_gfx", "east_asian_gfx",
    "indian_gfx", "middle_east_gfx",
)
REGION_FAMILIES = {
    "generic": (
        "european_gfx", "east_mediterranean_gfx",
        "eastern_christian_gfx", "folk_european_gfx",
    ),
    "african_gfx": ("african_gfx",),
    "american_gfx": ("american_gfx",),
    "east_asian_gfx": ("east_asian_gfx",),
    "indian_gfx": ("indian_gfx",),
    "middle_east_gfx": ("middle_east_gfx",),
}
QUADRANTS = ("top_left", "top_right", "bottom_left", "bottom_right")
ICON_SIZE = (128, 128)


@dataclass(frozen=True)
class PopClass:
    key: str
    name: str
    description: str


@dataclass(frozen=True)
class Sheet:
    filename: str
    region: str
    keys: tuple[str, str, str, str]


POP_CLASSES = (
    PopClass(
        "nobles",
        "Landed Elites",
        "The landed, hereditary, and office-holding elites whose households "
        "command wealth, patronage, and access to political authority.",
    ),
    PopClass(
        "clergy",
        "Priesthoods",
        "The priests, ritual specialists, temple personnel, diviners, and "
        "religious teachers who maintain the community's sacred traditions.",
    ),
    PopClass(
        "burghers",
        "Urban Citizens",
        "The merchants, householders, civic notables, and independent producers "
        "whose activity sustains towns, ports, markets, and long-distance exchange.",
    ),
    PopClass(
        "laborers",
        "Artisans and Laborers",
        "The skilled craftspeople, wage workers, carriers, miners, and other "
        "laborers whose work supplies workshops, building sites, and extractive trades.",
    ),
    PopClass(
        "soldiers",
        "Military Households",
        "The communities and dependants that supply professional troops, "
        "retainers, garrisons, sailors, and the logistical base of armed forces.",
    ),
    PopClass(
        "peasants",
        "Cultivators",
        "The tenant farmers, smallholders, herders, and village households who "
        "produce most food and support the countryside's local obligations.",
    ),
    PopClass(
        "tribesmen",
        "Tribal Communities",
        "Rural kin-groups and self-governing communities whose farming, herding, "
        "hunting, or mixed livelihoods remain organized beyond close state control.",
    ),
    PopClass(
        "slaves",
        "Enslaved People",
        "People deprived of legal freedom through war, birth, punishment, or sale, "
        "and compelled to labor in households, agriculture, workshops, mines, or public works.",
    ),
)

SHEETS = (
    Sheet(
        "pop_sheet_01_generic_upper.png", "generic",
        ("nobles", "clergy", "burghers", "laborers"),
    ),
    Sheet(
        "pop_sheet_02_generic_lower.png", "generic",
        ("soldiers", "peasants", "tribesmen", "slaves"),
    ),
    Sheet(
        "pop_sheet_03_african_upper.png", "african_gfx",
        ("nobles", "clergy", "burghers", "laborers"),
    ),
    Sheet(
        "pop_sheet_04_african_lower.png", "african_gfx",
        ("soldiers", "peasants", "tribesmen", "slaves"),
    ),
    Sheet(
        "pop_sheet_05_american_upper.png", "american_gfx",
        ("nobles", "clergy", "burghers", "laborers"),
    ),
    Sheet(
        "pop_sheet_06_american_lower.png", "american_gfx",
        ("soldiers", "peasants", "tribesmen", "slaves"),
    ),
    Sheet(
        "pop_sheet_07_east_asian_upper.png", "east_asian_gfx",
        ("nobles", "clergy", "burghers", "laborers"),
    ),
    Sheet(
        "pop_sheet_08_east_asian_lower.png", "east_asian_gfx",
        ("soldiers", "peasants", "tribesmen", "slaves"),
    ),
    Sheet(
        "pop_sheet_09_indian_upper.png", "indian_gfx",
        ("nobles", "clergy", "burghers", "laborers"),
    ),
    Sheet(
        "pop_sheet_10_indian_lower.png", "indian_gfx",
        ("soldiers", "peasants", "tribesmen", "slaves"),
    ),
    Sheet(
        "pop_sheet_11_middle_east_upper.png", "middle_east_gfx",
        ("nobles", "clergy", "burghers", "laborers"),
    ),
    Sheet(
        "pop_sheet_12_middle_east_lower.png", "middle_east_gfx",
        ("soldiers", "peasants", "tribesmen", "slaves"),
    ),
)

REFERENCE_FILES = (
    "vanilla_generic_pop_icons.png",
    "vanilla_pop_mapmode_icons.png",
    "vanilla_african_gfx_pop_portraits.png",
    "vanilla_american_gfx_pop_portraits.png",
    "vanilla_east_asian_gfx_pop_portraits.png",
    "vanilla_indian_gfx_pop_portraits.png",
    "vanilla_middle_east_gfx_pop_portraits.png",
)

LEDGER_FIELDS = (
    "region", "key", "name", "sheet", "quadrant", "master", "resolver_paths",
    "dimensions", "compression", "source_basis", "status",
)


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def pop_index() -> dict[str, PopClass]:
    return {entry.key: entry for entry in POP_CLASSES}


def art_index() -> dict[tuple[str, str], tuple[Sheet, str]]:
    result: dict[tuple[str, str], tuple[Sheet, str]] = {}
    for sheet in SHEETS:
        if len(sheet.keys) != 4:
            raise ValueError(f"{sheet.filename} must map exactly four icons")
        for quadrant, key in zip(QUADRANTS, sheet.keys, strict=True):
            index = (sheet.region, key)
            if index in result:
                raise ValueError(f"duplicate pop-art mapping: {index}")
            result[index] = (sheet, quadrant)
    return result


def quadrant_box(size: tuple[int, int], quadrant: str) -> tuple[int, int, int, int]:
    width, height = size
    if width != height or width % 2 or height % 2:
        raise ValueError(f"four-up source must be even and square, got {size}")
    half = width // 2
    inset = 4
    return {
        "top_left": (inset, inset, half - inset, half - inset),
        "top_right": (half + inset, inset, width - inset, half - inset),
        "bottom_left": (inset, half + inset, half - inset, height - inset),
        "bottom_right": (half + inset, half + inset, width - inset, height - inset),
    }[quadrant]


def master_path(region: str, key: str) -> Path:
    return MASTER_DIR / region / f"{key}.png"


def resolver_paths(region: str, key: str) -> tuple[Path, ...]:
    if region == "generic":
        generic = (GENERIC_DIR / f"{key}.dds", MAPMODE_DIR / f"{key}.dds")
    else:
        generic = ()
    return generic + tuple(
        GRAPHICAL_ROOT / family / "pops" / f"{key}.dds"
        for family in REGION_FAMILIES[region]
    )


def installed_graphical_families() -> set[str]:
    mounts = [GAME / "main_menu", GAME / "loading_screen"]
    mounts.extend(
        mounted
        for dlc in (GAME / "dlc").glob("*")
        for mounted in (dlc / "main_menu", dlc / "loading_screen")
    )
    return {
        path.parent.name
        for mounted in mounts
        if mounted.is_dir()
        for path in mounted.glob("gfx/interface/graphical_cultures/*/pops")
        if any(path.glob("*.dds"))
    }


def remove_chroma(source: Path, target: Path) -> None:
    if not CHROMA_HELPER.is_file():
        raise ValueError(f"missing image-pipeline chroma helper: {CHROMA_HELPER}")
    subprocess.run(
        [
            sys.executable,
            str(CHROMA_HELPER),
            "--input", str(source),
            "--out", str(target),
            "--auto-key", "border",
            "--soft-matte",
            "--transparent-threshold", "12",
            "--opaque-threshold", "220",
            "--despill",
            "--force",
        ],
        check=True,
    )


def normalize_master(source: Image.Image) -> Image.Image:
    rgba = source.convert("RGBA")
    alpha_box = rgba.getchannel("A").getbbox()
    if alpha_box is None:
        raise ValueError("chroma removal produced an empty portrait")
    subject = rgba.crop(alpha_box)
    subject.thumbnail((124, 124), Image.Resampling.LANCZOS)
    output = Image.new("RGBA", ICON_SIZE, (0, 0, 0, 0))
    x = (ICON_SIZE[0] - subject.width) // 2
    y = ICON_SIZE[1] - subject.height - 1
    output.alpha_composite(subject, (x, y))
    return output


def localization_text(client: str) -> str:
    lines = [f"l_{client}:"]
    for entry in POP_CLASSES:
        name = entry.name.replace('"', '\\"')
        desc = entry.description.replace('"', '\\"')
        lines.append(f' {entry.key}: "{name}"')
        lines.append(f' {entry.key}_desc: "{desc}"')
    lines.append("")
    return "\n".join(lines)


def write_localization() -> None:
    for client in CLIENTS:
        path = ROOT / f"main_menu/localization/{client}/pops_l_{client}.yml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(localization_text(client), encoding="utf-8-sig", newline="\n")


def ledger_rows() -> list[dict[str, str]]:
    classes = pop_index()
    index = art_index()
    rows: list[dict[str, str]] = []
    for region in REGIONS:
        for key in classes:
            sheet, quadrant = index[(region, key)]
            paths = resolver_paths(region, key)
            rows.append({
                "region": region,
                "key": key,
                "name": classes[key].name,
                "sheet": relative(SHEET_DIR / sheet.filename),
                "quadrant": quadrant,
                "master": relative(master_path(region, key)),
                "resolver_paths": ";".join(relative(path) for path in paths),
                "dimensions": "128x128 RGBA",
                "compression": "DXT5 + full mip chain",
                "source_basis": (
                    "installed EU5 pop portrait contact sheet; generated four-up "
                    "ancient material-culture reinterpretation"
                ),
                "status": "complete",
            })
    return rows


def write_csv() -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LEDGER_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(ledger_rows())


def write_contact_sheet() -> None:
    tile, label, columns = 144, 34, 8
    rows = len(REGIONS)
    canvas = Image.new("RGB", (columns * tile, rows * (tile + label)), "#101a2a")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    classes = pop_index()
    for row_index, region in enumerate(REGIONS):
        for column, key in enumerate(classes):
            x = column * tile
            y = row_index * (tile + label)
            checker = Image.new("RGB", (tile - 8, tile - 8), "#17304a")
            with Image.open(master_path(region, key)) as source:
                preview = ImageOps.contain(source.convert("RGBA"), (tile - 8, tile - 8))
            canvas.paste(checker, (x + 4, y + 4))
            canvas.paste(preview, (x + 4, y + 4), preview)
            draw.text((x + 5, y + tile + 2), classes[key].name[:22], fill="#f0e7cf", font=font)
            draw.text((x + 5, y + tile + 17), region, fill="#a9b9ca", font=font)
    CONTACT_SHEET.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(CONTACT_SHEET, format="PNG", optimize=True)


def write() -> None:
    index = art_index()
    expected = {(region, pop.key) for region in REGIONS for pop in POP_CLASSES}
    if set(index) != expected:
        raise ValueError(
            f"pop-art mapping mismatch: missing={sorted(expected - set(index))}; "
            f"extra={sorted(set(index) - expected)}"
        )
    MASTER_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="antq-pop-", dir=ROOT / ".tmp") as temporary:
        work = Path(temporary)
        opened: dict[str, Image.Image] = {}
        try:
            for (region, key), (sheet, quadrant) in index.items():
                source_path = SHEET_DIR / sheet.filename
                if sheet.filename not in opened:
                    opened[sheet.filename] = Image.open(source_path).convert("RGB")
                raw = work / f"{region}_{key}_raw.png"
                keyed = work / f"{region}_{key}_keyed.png"
                opened[sheet.filename].crop(
                    quadrant_box(opened[sheet.filename].size, quadrant)
                ).save(raw, format="PNG")
                remove_chroma(raw, keyed)
                with Image.open(keyed) as transparent:
                    master = normalize_master(transparent)
                target = master_path(region, key)
                target.parent.mkdir(parents=True, exist_ok=True)
                master.save(target, format="PNG", optimize=True)
                destinations = resolver_paths(region, key)
                convert(target, destinations[0], "dxt5", mipmaps=True)
                for destination in destinations[1:]:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(destinations[0].read_bytes())
        finally:
            for image in opened.values():
                image.close()
    write_localization()
    write_csv()
    write_contact_sheet()
    print("m12_pop_presentation: wrote 48 ancient masters, 88 DDS resolvers, and 11 localization mirrors")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def installed_engine_keys() -> set[str]:
    text = ENGINE_POP_TYPES.read_text(encoding="utf-8-sig")
    return {
        line.split("=", 1)[0].strip()
        for line in text.splitlines()
        if line and not line[0].isspace() and "=" in line
    }


def validate() -> bool:
    failures: list[str] = []
    try:
        classes = pop_index()
        expected_keys = set(classes)
        if len(classes) != 8:
            failures.append("pop-class ledger must define exactly eight distinct engine keys")
        if installed_engine_keys() != expected_keys:
            failures.append(
                f"installed pop-type contract changed: {sorted(installed_engine_keys())}"
            )
        index = art_index()
        expected_art = {(region, key) for region in REGIONS for key in expected_keys}
        if set(index) != expected_art:
            failures.append("four-up mapping does not exactly cover 6 regions x 8 pop classes")
        routed_families = {
            family for families in REGION_FAMILIES.values() for family in families
        }
        installed_families = installed_graphical_families()
        if routed_families != installed_families:
            failures.append(
                f"installed graphical pop-family union drifted: "
                f"missing={sorted(installed_families - routed_families)}, "
                f"extra={sorted(routed_families - installed_families)}"
            )
        for filename in REFERENCE_FILES:
            path = REFERENCE_DIR / filename
            if not path.is_file():
                failures.append(f"missing real-EU5 style reference {relative(path)}")
        for sheet in SHEETS:
            path = SHEET_DIR / sheet.filename
            if not path.is_file():
                failures.append(f"missing four-up source {relative(path)}")
                continue
            with Image.open(path) as image:
                if image.format != "PNG" or image.width != image.height or image.width % 2:
                    failures.append(f"invalid four-up geometry {relative(path)}")
        master_hashes: set[str] = set()
        resolver_count = 0
        for region, key in sorted(expected_art):
            master = master_path(region, key)
            if not master.is_file():
                failures.append(f"missing master {relative(master)}")
            else:
                with Image.open(master) as image:
                    if image.format != "PNG" or image.size != ICON_SIZE or image.mode != "RGBA":
                        failures.append(f"invalid master contract {relative(master)}")
                    extrema = image.getchannel("A").getextrema()
                    if extrema[0] != 0 or extrema[1] != 255:
                        failures.append(f"master lacks useful alpha {relative(master)}: {extrema}")
                digest = sha256(master)
                if digest in master_hashes:
                    failures.append(f"semantic portrait alias detected: {relative(master)}")
                master_hashes.add(digest)
            for path in resolver_paths(region, key):
                resolver_count += 1
                if not path.is_file():
                    failures.append(f"missing resolver {relative(path)}")
                    continue
                details = identify(path)
                if (
                    details["format"] != "DDS"
                    or details["width"] != "128"
                    or details["height"] != "128"
                    or "a" not in details["channels"]
                ):
                    failures.append(f"invalid DDS contract {relative(path)}: {details}")
        if resolver_count != 88:
            failures.append(f"expected 88 resolver targets, got {resolver_count}")
        expected_ledger = ledger_rows()
        if not LEDGER.is_file():
            failures.append(f"missing {relative(LEDGER)}")
        else:
            with LEDGER.open(encoding="utf-8-sig", newline="") as handle:
                actual_ledger = list(csv.DictReader(handle))
            if actual_ledger != expected_ledger:
                failures.append(f"stale {relative(LEDGER)}")
        for client in CLIENTS:
            path = ROOT / f"main_menu/localization/{client}/pops_l_{client}.yml"
            if not path.is_file():
                failures.append(f"missing exact pop localization mirror {relative(path)}")
                continue
            raw = path.read_bytes()
            if not raw.startswith(b"\xef\xbb\xbf"):
                failures.append(f"localization lacks UTF-8 BOM: {relative(path)}")
            text = raw.decode("utf-8-sig")
            for entry in POP_CLASSES:
                if f' {entry.key}: "{entry.name}"' not in text:
                    failures.append(f"{relative(path)} lacks ancient name for {entry.key}")
                if f" {entry.key}_desc:" not in text:
                    failures.append(f"{relative(path)} lacks description for {entry.key}")
            for forbidden in ("Burghers", '"Nobles"', '"Clerics"', '"Peasants"', '"Tribesmen"', '"Slaves"'):
                if forbidden in text:
                    failures.append(f"medieval/legacy pop label remains in {relative(path)}: {forbidden}")
        if not CONTACT_SHEET.is_file():
            failures.append(f"missing {relative(CONTACT_SHEET)}")
        else:
            with Image.open(CONTACT_SHEET) as image:
                if image.format != "PNG" or image.width < 1100 or image.height < 1000:
                    failures.append(f"invalid contact sheet {relative(CONTACT_SHEET)}")
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        failures.append(str(exc))
    if failures:
        print("m12_pop_presentation: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return False
    print("m12_pop_presentation: PASS (8 ancient classes; 48 unique masters; 88 direct resolvers; 9 graphical families; 11 clients)")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.write:
            write()
            return 0
        return 0 if validate() else 1
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print(f"m12_pop_presentation: FAIL\n  - {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
