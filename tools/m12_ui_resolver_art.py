#!/usr/bin/env python3
"""Replace every installed population-summary and artillery UI resolver.

The engine does not use the pop-type portraits everywhere.  Location summaries,
alerts, sorting, modifier tooltips, and font icons resolve a separate collection
of generic textures.  Artillery has the same problem: its cannon is repeated
through category, battle, siege, modifier, institution, and illustration paths.

This tool treats both collections as installed-union contracts.  A game patch
that adds another matching DDS makes ``--check`` fail until the generated ledger
and exact-path mirror are refreshed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from dds import convert, identify


ROOT = Path(__file__).resolve().parents[1]
GAME_UI = Path(json.loads((ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig"))["game_dir"]) / "game/main_menu/gfx/interface"
MOD_UI = ROOT / "main_menu/gfx/interface"
SOURCE_DIR = ROOT / "assets_queue/ui_resolvers"
RENDER_DIR = SOURCE_DIR / "rendered"
BALLISTA_SOURCE = SOURCE_DIR / "antq_torsion_ballista.png"
POPULATION_SOURCE = SOURCE_DIR / "antq_population_summary.png"
LEDGER = ROOT / "docs/m12/ui_resolver_art.csv"
CONTACT_SHEET = ROOT / "docs/m12/ui_resolver_art_contact_sheet.png"

SOURCE_HASHES = {
    BALLISTA_SOURCE: "af815992163c1252c219a9ef626a0d2b4b63e9b865079a24438d4b5b01f39a5a",
    POPULATION_SOURCE: "c6ecc67e73f2d71ca560765e3ba84f8e5db184df8030a66b6a3fe0a34d1fda06",
}
LEDGER_FIELDS = (
    "family", "variant", "resolver_path", "dimensions", "compression",
    "render_source", "installed_source", "installed_sha256", "output_sha256",
    "historical_basis", "status",
)


@dataclass(frozen=True)
class Target:
    family: str
    relative_path: Path
    width: int
    height: int
    variant: str

    @property
    def installed(self) -> Path:
        return GAME_UI / self.relative_path

    @property
    def rendered(self) -> Path:
        return RENDER_DIR / self.relative_path.with_suffix(".png")

    @property
    def output(self) -> Path:
        return MOD_UI / self.relative_path

    @property
    def wide(self) -> bool:
        return self.width / self.height > 1.8


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def installed_relative(path: Path) -> str:
    return path.relative_to(GAME_UI).as_posix()


def population_variant(path: Path) -> str:
    value = path.as_posix().casefold()
    if "depopulation" in value:
        return "decline"
    if "pops_wanting" in value:
        return "warning"
    if "overpopulation" in value:
        return "overcrowding"
    if "population_growth" in value or "global_population_growth" in value:
        return "growth"
    if "population_old" in value:
        return "legacy"
    if "capacity" in value:
        return "capacity"
    if "pacify_population" in value:
        return "unrest"
    if "population_needs" in value:
        return "needs"
    if "peasant_population" in value:
        return "cultivators"
    return "summary"


def artillery_variant(path: Path) -> str:
    value = path.as_posix().casefold()
    if "reinforce" in value:
        return "reinforcement"
    if "maintenance" in value:
        return "maintenance"
    if "build_cost" in value:
        return "construction"
    if "bonus_vs_fort" in value or "artillery_bonus" in value:
        return "fortification"
    if "power" in value:
        return "power"
    if "barrage" in value or "siege_occupation" in value:
        return "barrage"
    if "institution" in value:
        return "knowledge"
    if "building" in value or "yard" in value or "academy" in value:
        return "workshop"
    if "advance" in value or value.startswith("advance/"):
        return "advance"
    return "category"


def installed_targets() -> tuple[Target, ...]:
    if not GAME_UI.is_dir():
        raise ValueError(f"installed UI root is missing: {GAME_UI}")
    candidates: dict[Path, str] = {}
    for path in GAME_UI.rglob("*.dds"):
        name = path.name.casefold()
        family = ""
        if "artillery" in name:
            family = "artillery"
        elif "population" in name or "pops_wanting" in name:
            family = "population"
        if family:
            candidates[path.relative_to(GAME_UI)] = family
    targets: list[Target] = []
    for path, family in sorted(candidates.items(), key=lambda item: item[0].as_posix()):
        details = identify(GAME_UI / path)
        targets.append(Target(
            family=family,
            relative_path=path,
            width=int(details["width"]),
            height=int(details["height"]),
            variant=(
                artillery_variant(path)
                if family == "artillery"
                else population_variant(path)
            ),
        ))
    return tuple(targets)


def subject(source: Image.Image, maximum: tuple[int, int]) -> Image.Image:
    rgba = source.convert("RGBA")
    bounds = rgba.getchannel("A").getbbox()
    if bounds is None:
        raise ValueError("generated resolver source has no visible subject")
    cropped = rgba.crop(bounds)
    cropped.thumbnail(maximum, Image.Resampling.LANCZOS)
    return cropped


def rounded_field(size: tuple[int, int], *, opacity: int = 210) -> Image.Image:
    width, height = size
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    inset = max(1, round(min(width, height) * 0.035))
    radius = max(3, round(min(width, height) * 0.18))
    draw.rounded_rectangle(
        (inset, inset, width - inset - 1, height - inset - 1),
        radius=radius,
        fill=(12, 30, 52, opacity),
        outline=(151, 114, 50, min(235, opacity + 20)),
        width=max(1, round(min(width, height) * 0.018)),
    )
    return canvas


def draw_arrow(
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
    *,
    upward: bool,
    color: tuple[int, int, int, int],
) -> None:
    scale = min(width, height)
    x0 = round(width * 0.58)
    x1 = round(width * 0.88)
    if upward:
        points = (
            (x0, round(height * 0.75)),
            (round(width * 0.68), round(height * 0.65)),
            (round(width * 0.75), round(height * 0.52)),
            (round(width * 0.68), round(height * 0.47)),
            (x1, round(height * 0.30)),
            (round(width * 0.84), round(height * 0.55)),
            (round(width * 0.78), round(height * 0.50)),
            (round(width * 0.69), round(height * 0.70)),
        )
    else:
        points = (
            (x0, round(height * 0.28)),
            (round(width * 0.68), round(height * 0.38)),
            (round(width * 0.75), round(height * 0.51)),
            (round(width * 0.68), round(height * 0.56)),
            (x1, round(height * 0.73)),
            (round(width * 0.84), round(height * 0.48)),
            (round(width * 0.78), round(height * 0.53)),
            (round(width * 0.69), round(height * 0.33)),
        )
    draw.polygon(points, fill=color)
    draw.line(points + (points[0],), fill=(246, 224, 175, 230), width=max(1, scale // 64))


def add_population_state(image: Image.Image, variant: str) -> None:
    draw = ImageDraw.Draw(image)
    width, height = image.size
    scale = min(width, height)
    if variant in {"growth", "capacity"}:
        draw_arrow(draw, width, height, upward=True, color=(69, 160, 100, 245))
    elif variant == "decline":
        draw_arrow(draw, width, height, upward=False, color=(176, 64, 54, 245))
    elif variant == "warning":
        stem = max(2, scale // 12)
        x = round(width * 0.84)
        draw.rounded_rectangle(
            (x - stem // 2, round(height * 0.25), x + stem // 2, round(height * 0.65)),
            radius=max(1, stem // 3), fill=(199, 66, 52, 250),
        )
        dot = max(2, scale // 16)
        draw.ellipse(
            (x - dot, round(height * 0.72) - dot, x + dot, round(height * 0.72) + dot),
            fill=(199, 66, 52, 250),
        )
    elif variant == "overcrowding":
        x, y = round(width * 0.79), round(height * 0.72)
        arm = max(3, scale // 8)
        thick = max(2, scale // 22)
        draw.rounded_rectangle((x - arm, y - thick, x + arm, y + thick), thick, fill=(186, 65, 54, 245))
        draw.rounded_rectangle((x - thick, y - arm, x + thick, y + arm), thick, fill=(186, 65, 54, 245))
    elif variant in {"needs", "unrest"}:
        flame = (
            (round(width * 0.78), round(height * 0.77)),
            (round(width * 0.70), round(height * 0.58)),
            (round(width * 0.78), round(height * 0.43)),
            (round(width * 0.77), round(height * 0.27)),
            (round(width * 0.91), round(height * 0.47)),
            (round(width * 0.87), round(height * 0.65)),
        )
        draw.polygon(flame, fill=(207, 114, 42, 245))
        draw.polygon(
            (
                (round(width * 0.80), round(height * 0.68)),
                (round(width * 0.77), round(height * 0.56)),
                (round(width * 0.83), round(height * 0.48)),
                (round(width * 0.87), round(height * 0.61)),
            ),
            fill=(240, 192, 76, 250),
        )


def render_population(target: Target, source: Image.Image) -> Image.Image:
    size = (target.width, target.height)
    canvas = rounded_field(size)
    maximum = (round(target.width * 0.86), round(target.height * 0.88))
    people = subject(source, maximum)
    if target.variant == "legacy":
        gray = ImageOps.grayscale(people.convert("RGB")).convert("RGBA")
        gray.putalpha(people.getchannel("A").point(lambda value: round(value * 0.68)))
        people = gray
    x = (target.width - people.width) // 2
    y = target.height - people.height - max(1, target.height // 32)
    canvas.alpha_composite(people, (x, y))
    add_population_state(canvas, target.variant)
    return canvas


def add_artillery_state(image: Image.Image, variant: str) -> None:
    draw = ImageDraw.Draw(image)
    width, height = image.size
    scale = min(width, height)
    if variant in {"barrage", "power"}:
        for index in range(3):
            radius = max(2, scale // 18)
            x = round(width * (0.72 + index * 0.075))
            y = round(height * (0.25 + index * 0.045))
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(62, 69, 78, 245))
    elif variant == "fortification":
        base_y = round(height * 0.80)
        left = round(width * 0.69)
        right = round(width * 0.94)
        draw.rectangle((left, round(height * 0.56), right, base_y), fill=(138, 126, 103, 245))
        merlon = max(2, scale // 14)
        for x in range(left, right, merlon * 2):
            draw.rectangle((x, round(height * 0.49), min(x + merlon, right), round(height * 0.58)), fill=(161, 148, 121, 245))
    elif variant in {"construction", "maintenance"}:
        cx, cy = round(width * 0.82), round(height * 0.69)
        radius = max(3, scale // 9)
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=(190, 146, 57, 245), outline=(247, 221, 143, 245), width=max(1, scale // 64))
        draw.ellipse((cx - radius // 2, cy - radius // 2, cx + radius // 2, cy + radius // 2), outline=(117, 75, 24, 245), width=max(1, scale // 52))
    elif variant == "reinforcement":
        draw_arrow(draw, width, height, upward=True, color=(70, 138, 127, 245))


def wide_artillery(target: Target, source: Image.Image) -> Image.Image:
    width, height = target.width, target.height
    canvas = Image.new("RGBA", (width, height), (12, 27, 46, 255))
    pixels = canvas.load()
    for y in range(height):
        for x in range(width):
            nx = (x - width / 2) / max(1.0, width / 2)
            ny = (y - height / 2) / max(1.0, height / 2)
            vignette = min(1.0, math.sqrt(nx * nx + ny * ny))
            grain = ((x * 17 + y * 31) % 19) - 9
            pixels[x, y] = (
                max(5, round(19 - vignette * 8 + grain * 0.12)),
                max(10, round(43 - vignette * 14 + grain * 0.15)),
                max(18, round(70 - vignette * 18 + grain * 0.18)),
                255,
            )
    draw = ImageDraw.Draw(canvas)
    horizon = round(height * 0.77)
    draw.rectangle((0, horizon, width, height), fill=(33, 33, 31, 255))
    wall_left = round(width * 0.06)
    wall_right = round(width * 0.32)
    wall_top = round(height * 0.31)
    draw.rectangle((wall_left, wall_top, wall_right, horizon), fill=(66, 67, 64, 255))
    merlon_w = max(12, width // 38)
    for x in range(wall_left, wall_right, merlon_w * 2):
        draw.rectangle((x, wall_top - height // 12, min(x + merlon_w, wall_right), wall_top), fill=(79, 80, 76, 255))
    machine = subject(source, (round(width * 0.48), round(height * 0.75)))
    x = round(width * 0.47)
    y = horizon - machine.height + round(height * 0.015)
    canvas.alpha_composite(machine, (x, y))
    draw.line((round(width * 0.38), round(height * 0.12), round(width * 0.38), round(height * 0.88)), fill=(165, 121, 47, 180), width=max(2, width // 360))
    return canvas


def render_artillery(target: Target, source: Image.Image) -> Image.Image:
    if target.wide:
        return wide_artillery(target, source)
    size = (target.width, target.height)
    canvas = rounded_field(size)
    machine = subject(source, (round(target.width * 0.90), round(target.height * 0.82)))
    x = (target.width - machine.width) // 2
    y = target.height - machine.height - max(1, target.height // 24)
    canvas.alpha_composite(machine, (x, y))
    add_artillery_state(canvas, target.variant)
    return canvas


def render(target: Target, sources: dict[str, Image.Image]) -> Image.Image:
    if target.family == "artillery":
        return render_artillery(target, sources["artillery"])
    return render_population(target, sources["population"])


def historical_basis(target: Target) -> str:
    if target.family == "artillery":
        return (
            "Two-armed torsion stone-thrower; Vitruvius, De architectura "
            "10.10-12; Marsden, Greek and Roman Artillery (1969)."
        )
    return (
        "Regional-neutral ancient household group; clothing and material culture "
        "bounded to the ANTIQVITAS AD 1-476 presentation contract."
    )


def ledger_rows(targets: tuple[Target, ...]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for target in targets:
        rows.append({
            "family": target.family,
            "variant": target.variant,
            "resolver_path": f"gfx/interface/{target.relative_path.as_posix()}",
            "dimensions": f"{target.width}x{target.height}",
            "compression": "DXT5 + full mip chain",
            "render_source": relative(
                BALLISTA_SOURCE if target.family == "artillery" else POPULATION_SOURCE
            ),
            "installed_source": installed_relative(target.installed),
            "installed_sha256": sha256(target.installed),
            "output_sha256": sha256(target.output) if target.output.is_file() else "",
            "historical_basis": historical_basis(target),
            "status": "exact-path ancient mirror",
        })
    return rows


def write_csv(rows: list[dict[str, str]]) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LEDGER_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_contact_sheet(targets: tuple[Target, ...]) -> None:
    tile = (280, 170)
    columns = 4
    rows = math.ceil(len(targets) / columns)
    sheet = Image.new("RGB", (columns * tile[0], rows * tile[1]), "#0c1726")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for index, target in enumerate(targets):
        x = (index % columns) * tile[0]
        y = (index // columns) * tile[1]
        with Image.open(target.rendered) as source:
            preview = ImageOps.contain(source.convert("RGBA"), (260, 125), Image.Resampling.LANCZOS)
        field = Image.new("RGBA", preview.size, "#111d2d")
        field.alpha_composite(preview)
        sheet.paste(field.convert("RGB"), (x + (tile[0] - preview.width) // 2, y + 4))
        draw.text((x + 7, y + 133), target.relative_path.as_posix(), fill="#eee2c6", font=font)
        draw.text((x + 7, y + 148), f"{target.family} / {target.variant} / {target.width}x{target.height}", fill="#9eb0bf", font=font)
    CONTACT_SHEET.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(CONTACT_SHEET, format="PNG", optimize=True)


def write() -> None:
    targets = installed_targets()
    for source_path, expected_hash in SOURCE_HASHES.items():
        if not source_path.is_file() or sha256(source_path) != expected_hash:
            raise ValueError(f"generated source pin changed: {relative(source_path)}")
    sources = {
        "artillery": Image.open(BALLISTA_SOURCE).convert("RGBA"),
        "population": Image.open(POPULATION_SOURCE).convert("RGBA"),
    }
    try:
        for target in targets:
            image = render(target, sources)
            target.rendered.parent.mkdir(parents=True, exist_ok=True)
            image.save(target.rendered, format="PNG", optimize=True)
            convert(target.rendered, target.output, "dxt5", mipmaps=True)
    finally:
        for image in sources.values():
            image.close()
    write_csv(ledger_rows(targets))
    write_contact_sheet(targets)
    families = {family: sum(target.family == family for target in targets) for family in ("artillery", "population")}
    print(
        "m12_ui_resolver_art: wrote "
        f"{families['artillery']} artillery + {families['population']} population exact-path mirrors"
    )


def alpha_coverage(path: Path) -> float:
    with Image.open(path) as image:
        alpha = image.convert("RGBA").getchannel("A")
        bounds = alpha.getbbox()
        if bounds is None:
            return 0.0
        return ((bounds[2] - bounds[0]) * (bounds[3] - bounds[1])) / (image.width * image.height)


def validate() -> bool:
    failures: list[str] = []
    try:
        targets = installed_targets()
        if not targets:
            failures.append("installed resolver census is empty")
        family_counts = {
            family: sum(target.family == family for target in targets)
            for family in ("artillery", "population")
        }
        if family_counts["artillery"] < 30:
            failures.append(f"artillery installed-union census shrank unexpectedly: {family_counts}")
        if family_counts["population"] < 19:
            failures.append(f"population installed-union census shrank unexpectedly: {family_counts}")
        for source_path, expected_hash in SOURCE_HASHES.items():
            if not source_path.is_file():
                failures.append(f"missing generated source {relative(source_path)}")
            elif sha256(source_path) != expected_hash:
                failures.append(f"generated source pin changed: {relative(source_path)}")
        expected_rows = ledger_rows(targets)
        if not LEDGER.is_file():
            failures.append(f"missing {relative(LEDGER)}")
        else:
            with LEDGER.open(encoding="utf-8-sig", newline="") as handle:
                actual_rows = list(csv.DictReader(handle))
            if actual_rows != expected_rows:
                failures.append(f"stale installed-union ledger {relative(LEDGER)}")
        for target in targets:
            if not target.rendered.is_file():
                failures.append(f"missing rendered source {relative(target.rendered)}")
                continue
            with Image.open(target.rendered) as image:
                if image.format != "PNG" or image.size != (target.width, target.height):
                    failures.append(f"wrong rendered PNG contract: {relative(target.rendered)}")
            coverage = alpha_coverage(target.rendered)
            if target.wide:
                if coverage < 0.99:
                    failures.append(f"wide illustration is not fully framed: {relative(target.rendered)}")
            elif not 0.65 <= coverage <= 1.0:
                failures.append(f"icon alpha safe-area coverage out of range: {relative(target.rendered)} = {coverage:.3f}")
            if not target.output.is_file():
                failures.append(f"missing exact-path resolver mirror {relative(target.output)}")
                continue
            details = identify(target.output)
            if (
                details["format"] != "DDS"
                or details["width"] != str(target.width)
                or details["height"] != str(target.height)
                or details["depth"] != "8"
                or "".join(details["channels"].split()) != "srgba4.0"
            ):
                failures.append(f"wrong DDS contract: {relative(target.output)} = {details}")
            elif sha256(target.output) == sha256(target.installed):
                failures.append(f"resolver still aliases vanilla source: {relative(target.output)}")
        if not CONTACT_SHEET.is_file():
            failures.append(f"missing {relative(CONTACT_SHEET)}")
        else:
            with Image.open(CONTACT_SHEET) as image:
                expected_height = math.ceil(len(targets) / 4) * 170
                if image.format != "PNG" or image.size != (1120, expected_height):
                    failures.append(f"stale contact sheet geometry: {relative(CONTACT_SHEET)}")
    except (OSError, ValueError, KeyError) as exc:
        failures.append(str(exc))
    if failures:
        print("m12_ui_resolver_art: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return False
    print(
        "m12_ui_resolver_art: PASS "
        f"({len(targets)} installed population/artillery resolvers exact-mirrored)"
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        write()
    return 0 if not args.check or validate() else 1


if __name__ == "__main__":
    raise SystemExit(main())
