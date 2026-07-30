#!/usr/bin/env python3
"""Build and validate direct, sourced CoA compositions for every AD 1 polity.

EU5 renders country standards from a solid field and colored-emblem layers.
This audit preserves the individually researched M11 standards, replaces every
regional fallback with an explicit composition, removes exact duplicates, and
renders regional review sheets from the installed emblem textures.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from functools import cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageColor, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "docs/world_1ad/polities.csv"
CORE = ROOT / "docs/m11/core_coas.csv"
THEMES = ROOT / "docs/m11/coa_theme_catalog.csv"
CATALOG = ROOT / "docs/m11/coa_direct_catalog.csv"
REVIEW_DIR = ROOT / "docs/m11/coa_review"
CONFIG = ROOT / "config/local_paths.json"

FIELDS = (
    "tag", "name", "region", "evidence_class", "emblem", "color1", "color2",
    "color3", "emblem_color1", "emblem_color2", "emblem_color3", "position_x",
    "position_y", "scale_x", "scale_y", "source", "confidence", "note",
)
COMPOSITION_FIELDS = (
    "emblem", "color1", "color2", "color3", "emblem_color1", "emblem_color2",
    "emblem_color3", "position_x", "position_y", "scale_x", "scale_y",
)
COLORS = {
    "black": "#17191d",
    "blue": "#254f86",
    "green": "#356a4a",
    "orange": "#b9652d",
    "purple": "#67436f",
    "red": "#87323a",
    "white": "#ded8c7",
    "yellow": "#c7a449",
}

# These are period-compatible material categories, not claims that the named
# communities possessed fixed flags. Every texture is shipped with the
# installed EU5 build and is checked locally before use.
REGION_MOTIFS: dict[str, tuple[str, ...]] = {
    "Africa": (
        "ce_african_ram_horns.dds", "ce_elephant_african.dds",
        "ce_african_sun.dds", "ce_african_crocodile.dds", "ce_bull_head.dds",
        "ce_spear_head_random_small.dds",
    ),
    "Anatolia": (
        "ce_eagle.dds", "ce_bull_head.dds", "ce_pomegranate.dds",
        "ce_stag.dds", "ce_horse_salient.dds",
    ),
    "Balkans": (
        "ce_horse_salient.dds", "ce_boar_head.dds", "ce_eagle.dds",
        "ce_cartwheel.dds",
    ),
    "Caucasus": (
        "ce_mountain.dds", "ce_eagle.dds", "ce_horse_salient.dds",
        "ce_stag.dds", "ce_lion_rampant_wide.dds",
    ),
    "Central Asia": (
        "ce_horse_head.dds", "ce_bow_arrow.dds", "ce_cartwheel.dds",
        "ce_mountain.dds", "ce_spear_head_random_small.dds",
        "ce_deer_kneeling.dds", "ce_spiral.dds",
    ),
    "Danube": (
        "ce_horse_salient.dds", "ce_wolf_head.dds", "ce_stag.dds",
        "ce_boar_passant.dds", "ce_cartwheel.dds", "ce_spear_head_random_small.dds",
    ),
    "Eastern Europe": (
        "ce_deer_kneeling.dds", "ce_boar_head.dds", "ce_spiral.dds",
        "ce_fish_naiant.dds", "ce_spear_head_random_small.dds",
    ),
    "Germania": (
        "ce_boar_passant.dds", "ce_boar_head.dds", "ce_stag.dds",
        "ce_stag_head_antlers_embowed.dds", "ce_wolf_head.dds",
        "ce_wolf_passant.dds", "ce_horse_head.dds", "ce_horse_salient.dds",
        "ce_spear_head_random_small.dds", "ce_bow_arrow.dds",
        "ce_tree_oak_simple.dds", "ce_deer_kneeling.dds", "ce_cartwheel.dds",
        "ce_spiral.dds", "ce_sun_radiant_simple.dds", "ce_bull_head.dds",
        "ce_eagle.dds", "ce_fish_naiant.dds",
    ),
    "India": (
        "ce_elephant_asian.dds", "ce_bull_head.dds", "ce_horse_salient.dds",
        "ce_lion_rampant_wide.dds", "ce_fishes_pandya.dds",
        "ce_auspicious_conch_shell_simple.dds", "ce_stupa_ligor.dds",
        "ce_sudarshana_chakra.dds", "ce_palm_tree_simple.dds",
        "ce_pomegranate.dds", "ce_boat_shield.dds", "ce_cartwheel.dds",
    ),
    "Iran": (
        "ce_horse_salient.dds", "ce_bow_arrow.dds",
        "ce_lion_rampant_wide.dds", "ce_eagle.dds",
        "ce_sun_radiant_persia_random.dds", "ce_pomegranate.dds",
    ),
    "Japan": (
        "ce_sun_radiant_simple.dds", "ce_deer_kneeling.dds",
        "ce_fish_naiant.dds", "ce_boat_shield.dds", "ce_spiral.dds",
        "ce_cartwheel.dds", "ce_spear_head_random_small.dds",
        "ce_horse_head.dds", "ce_circle.dds", "ce_sun_radiant_small.dds",
    ),
    "Korea": (
        "ce_chinese_rosette.dds", "ce_deer_kneeling.dds",
        "ce_horse_head.dds", "ce_spiral.dds", "ce_cartwheel.dds",
        "ce_sun_radiant_simple.dds",
    ),
    "Lanka": (
        "ce_elephant_asian.dds", "ce_auspicious_conch_shell_simple.dds",
        "ce_stupa_ligor.dds",
    ),
    "Levant": (
        "ce_palm_tree_simple.dds", "ce_pomegranate.dds", "ce_eagle.dds",
        "ce_star_08.dds", "ce_ibex_goat_passant.dds",
        "ce_sun_radiant_simple.dds",
    ),
    "Mesoamerica": (
        "ce_glyph_maya_ajaw_kin.dds", "ce_spiral.dds",
        "ce_glyph_maya_jaguar_god.dds", "ce_circle.dds",
        "ce_fish_naiant.dds",
    ),
    "Mesopotamia": (
        "ce_bull_head.dds", "ce_eagle.dds", "ce_star_08.dds",
        "ce_palm_tree_simple.dds", "ce_lion_rampant_wide.dds",
    ),
    "North America": (
        "ce_hopewell_ornament.dds", "ce_hopewell_bear_claw.dds",
        "ce_turner_mound_snake.dds", "ce_hopewell_eagle_claw.dds",
        "ce_hopewell_human_hand.dds",
    ),
    "Oceania": (
        "ce_tonga_ngatu_pattern.dds", "ce_polynesian_turtle.dds",
        "ce_polynesian_makau.dds", "ce_sun_polynesian.dds",
    ),
    "Pontic": (
        "ce_horse_salient.dds", "ce_bow_arrow.dds", "ce_deer_kneeling.dds",
        "ce_cartwheel.dds", "ce_spear_head_random_small.dds",
        "ce_wolf_head.dds",
    ),
    "Scandinavia": (
        "ce_stag.dds", "ce_boar_passant.dds", "ce_sun_radiant_simple.dds",
        "ce_deer_kneeling.dds",
    ),
    "Southeast Asia": (
        "ce_elephant_asian.dds", "ce_boat_shield.dds", "ce_fish_naiant.dds",
        "ce_spiral.dds", "ce_conch_shell.dds", "ce_asian_animist_sun.dds",
        "ce_tiger.dds", "ce_cartwheel.dds",
    ),
    "Steppe": (
        "ce_horse_heads_addorsed.dds", "ce_bow_arrow.dds",
        "ce_spear_head_random_small.dds", "ce_wolf_head.dds",
        "ce_deer_kneeling.dds", "ce_cartwheel.dds", "ce_spiral.dds",
    ),
    "Tarim": (
        "ce_mountain.dds", "ce_horse_head.dds", "ce_stupa_ligor.dds",
        "ce_cartwheel.dds", "ce_auspicious_conch_shell_simple.dds",
        "ce_bow_arrow.dds", "ce_pomegranate.dds",
    ),
    "West Africa": (
        "ce_african_baobab.dds", "ce_african_sun.dds",
        "ce_african_crocodile.dds", "ce_african_ram_horns.dds",
        "ce_african_rising_sun.dds", "ce_spear_head_random_small.dds",
        "ce_bull_head.dds", "ce_elephant_african.dds", "ce_spiral.dds",
        "ce_cartwheel.dds", "ce_circle.dds", "ce_sun_radiant_simple.dds",
    ),
}


@dataclass(frozen=True)
class Standard:
    emblem: str
    color1: str
    color2: str
    color3: str
    emblem_color1: str
    emblem_color2: str
    emblem_color3: str
    position_x: str
    position_y: str
    scale_x: str
    scale_y: str
    source: str
    confidence: str
    note: str


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def standards(path: Path, key: str) -> dict[str, Standard]:
    rows = read_csv(path)
    result: dict[str, Standard] = {}
    fields = (
        "emblem", "color1", "color2", "color3", "emblem_color1",
        "emblem_color2", "emblem_color3", "position_x", "position_y",
        "scale_x", "scale_y", "source", "confidence", "note",
    )
    for number, row in enumerate(rows, start=2):
        name = row.get(key, "").strip()
        if not name or name in result:
            raise ValueError(f"{path.relative_to(ROOT)}:{number}: blank or duplicate {key}")
        missing = [field for field in fields if not row.get(field, "").strip()]
        if missing:
            raise ValueError(
                f"{path.relative_to(ROOT)}:{number}: blank {', '.join(missing)}"
            )
        result[name] = Standard(*(row[field].strip() for field in fields))
    return result


def composition(row: dict[str, str]) -> tuple[str, ...]:
    return tuple(row[field] for field in COMPOSITION_FIELDS)


def palette(theme: Standard, index: int) -> tuple[str, str, str]:
    colors = (theme.color1, theme.color2, theme.color3)
    variants = (
        colors,
        (colors[0], colors[2], colors[1]),
        (colors[1], colors[0], colors[2]),
        (colors[2], colors[0], colors[1]),
        (colors[1], colors[2], colors[0]),
        (colors[2], colors[1], colors[0]),
    )
    return variants[index % len(variants)]


def direct_rows() -> list[dict[str, str]]:
    roster = read_csv(ROSTER)
    core = standards(CORE, "tag")
    themes = standards(THEMES, "region")
    roster_tags = {row["tag"] for row in roster}
    if set(core) - roster_tags:
        raise ValueError(f"unknown core CoA tags: {sorted(set(core) - roster_tags)}")

    missing_regions = sorted({row["region"] for row in roster if row["tag"] not in core})
    absent_pools = sorted(set(missing_regions) - set(REGION_MOTIFS))
    if absent_pools:
        raise ValueError(f"missing material-motif pools: {', '.join(absent_pools)}")

    region_index: Counter[str] = Counter()
    result: list[dict[str, str]] = []
    used: dict[tuple[str, ...], str] = {}
    for row in roster:
        tag = row["tag"]
        if tag in core:
            standard = core[tag]
            evidence = "documented_material_motif"
            note = standard.note
        else:
            region = row["region"]
            index = region_index[region]
            region_index[region] += 1
            theme = themes[region]
            motifs = REGION_MOTIFS[region]
            colors = palette(theme, index // len(motifs))
            standard = replace(
                theme,
                emblem=motifs[index % len(motifs)],
                color1=colors[0],
                color2=colors[1],
                color3=colors[2],
                emblem_color1="color2",
                emblem_color2="color3",
                emblem_color3="color1",
                position_x=f"{0.46 + 0.04 * (index % 3):.2f}",
                position_y=f"{0.46 + 0.04 * ((index // 3) % 3):.2f}",
                scale_x=f"{0.68 + 0.06 * ((index // 9) % 4):.2f}",
                scale_y=f"{0.70 + 0.05 * ((index // 5) % 4):.2f}",
                source=f"{row['source']};{theme.source};P20",
                confidence="contested",
                note=(
                    f"Period-inspired {region} material-motif composition for "
                    f"{row['name']}; an explicitly marked regional UI reconstruction, "
                    "not a historical flag."
                ),
            )
            evidence = "regional_material_reconstruction"
            note = standard.note

        output = {
            "tag": tag,
            "name": row["name"],
            "region": row["region"],
            "evidence_class": evidence,
            **{
                field: str(getattr(standard, field))
                for field in (
                    "emblem", "color1", "color2", "color3", "emblem_color1",
                    "emblem_color2", "emblem_color3", "position_x", "position_y",
                    "scale_x", "scale_y", "source", "confidence",
                )
            },
            "note": note,
        }

        # A few independently researched rows once happened to match standards
        # elsewhere. Give the later row a visibly distinct, region-compatible
        # emblem while retaining its own cited rationale and palette.
        signature = composition(output)
        if signature in used:
            motifs = REGION_MOTIFS.get(row["region"], (standard.emblem,))
            for offset, emblem in enumerate(motifs, start=1):
                candidate = dict(output)
                candidate["emblem"] = emblem
                candidate["position_x"] = f"{0.44 + 0.03 * (offset % 5):.2f}"
                candidate["position_y"] = f"{0.45 + 0.03 * ((offset // 5) % 4):.2f}"
                candidate["scale_x"] = f"{0.70 + 0.04 * (offset % 4):.2f}"
                candidate["scale_y"] = f"{0.72 + 0.04 * ((offset + 1) % 4):.2f}"
                if composition(candidate) not in used:
                    output = candidate
                    output["note"] += (
                        " Exhaustive audit selected a distinct regional material motif "
                        "to prevent an identical standard."
                    )
                    break
            else:
                raise ValueError(f"could not make {tag} distinct from {used[signature]}")
        used[composition(output)] = tag
        result.append(output)

    if len(result) != 463 or len(used) != len(result):
        raise ValueError(f"direct CoA census drift: rows={len(result)} unique={len(used)}")
    return result


def catalog_bytes(rows: list[dict[str, str]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def emblem_dir() -> Path:
    payload = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
    return Path(payload["game_dir"]) / "game/main_menu/gfx/coat_of_arms/colored_emblems"


@cache
def colored_emblem(name: str, colors: tuple[str, str, str]) -> Image.Image:
    path = emblem_dir() / name
    source = Image.open(path).convert("RGBA")
    channels = np.asarray(source, dtype=np.float32) / 255.0
    color_matrix = np.asarray(
        [ImageColor.getrgb(COLORS[color]) for color in colors], dtype=np.float32
    )
    rgb = np.clip(
        channels[:, :, 0:1] * color_matrix[0]
        + channels[:, :, 1:2] * color_matrix[1]
        + channels[:, :, 2:3] * color_matrix[2],
        0,
        255,
    )
    alpha = (channels[:, :, 3:4] * 255.0)
    rendered = np.concatenate((rgb, alpha), axis=2).astype(np.uint8)
    return Image.fromarray(rendered, "RGBA")


def review_sheet(region: str, rows: list[dict[str, str]]) -> bytes:
    tile_w, tile_h = 250, 154
    columns = min(6, max(1, len(rows)))
    lines = (len(rows) + columns - 1) // columns
    canvas = Image.new("RGB", (columns * tile_w, lines * tile_h + 32), "#10161d")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    draw.text((10, 9), f"{region} — {len(rows)} direct AD 1 standards", fill="#e6ddc5", font=font)
    for index, row in enumerate(rows):
        x = (index % columns) * tile_w
        y = 32 + (index // columns) * tile_h
        field = Image.new("RGBA", (210, 112), COLORS[row["color1"]])
        texture = colored_emblem(
            row["emblem"],
            (
                row[row["emblem_color1"]],
                row[row["emblem_color2"]],
                row[row["emblem_color3"]],
            ),
        )
        width = max(1, round(210 * float(row["scale_x"])))
        height = max(1, round(112 * float(row["scale_y"])))
        texture = texture.resize((width, height), Image.Resampling.LANCZOS)
        left = round(210 * float(row["position_x"]) - width / 2)
        top = round(112 * float(row["position_y"]) - height / 2)
        field.alpha_composite(texture, (left, top))
        canvas.paste(field.convert("RGB"), (x + 10, y + 5))
        draw.rectangle((x + 9, y + 4, x + 220, y + 117), outline="#8d7c60", width=1)
        label = f"{row['tag']}  {row['name']}"
        draw.text((x + 10, y + 122), label[:38], fill="#eee6d3", font=font)
        draw.text(
            (x + 10, y + 137),
            row["evidence_class"].replace("_", " ")[:38],
            fill="#9fb0b5",
            font=font,
        )
    stream = io.BytesIO()
    canvas.save(stream, format="PNG", optimize=False)
    return stream.getvalue()


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def review_readme(rows: list[dict[str, str]]) -> bytes:
    evidence = Counter(row["evidence_class"] for row in rows)
    regions = Counter(row["region"] for row in rows)
    lines = [
        "# AD 1 direct CoA review",
        "",
        "Generated by `tools/m11_coa_audit.py --write` from the 463-row direct "
        "catalog and installed EU5 colored-emblem textures.",
        "",
        f"- Direct compositions: {len(rows)}",
        f"- Exact duplicate compositions: {len(rows) - len({composition(row) for row in rows})}",
        f"- Documented material motifs: {evidence['documented_material_motif']}",
        f"- Explicit regional material reconstructions: {evidence['regional_material_reconstruction']}",
        "",
        "| Region | Direct standards | Review sheet |",
        "|---|---:|---|",
    ]
    for region, count in sorted(regions.items()):
        filename = f"{slug(region)}.png"
        lines.append(f"| {region} | {count} | [{filename}]({filename}) |")
    lines.append("")
    lines.append(
        "These are period-inspired interface standards, not claims that ancient "
        "polities used fixed national flags."
    )
    return ("\n".join(lines) + "\n").encode("utf-8")


def expected_outputs() -> dict[Path, bytes]:
    rows = direct_rows()
    outputs = {CATALOG: catalog_bytes(rows), REVIEW_DIR / "README.md": review_readme(rows)}
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["region"]].append(row)
    for region, region_rows in sorted(grouped.items()):
        outputs[REVIEW_DIR / f"{slug(region)}.png"] = review_sheet(region, region_rows)
    return outputs


def validate_sources(rows: list[dict[str, str]]) -> list[str]:
    failures: list[str] = []
    textures = emblem_dir()
    for row in rows:
        if row["confidence"] not in {"secure", "contested"}:
            failures.append(f"{row['tag']}: invalid confidence {row['confidence']}")
        if row["evidence_class"] not in {
            "documented_material_motif", "regional_material_reconstruction"
        }:
            failures.append(f"{row['tag']}: invalid evidence class")
        if any(row[color] not in COLORS for color in ("color1", "color2", "color3")):
            failures.append(f"{row['tag']}: unknown palette color")
        if not (textures / row["emblem"]).is_file():
            failures.append(f"{row['tag']}: missing installed emblem {row['emblem']}")
        if "modern" in row["emblem"].lower():
            failures.append(f"{row['tag']}: anachronistic emblem filename {row['emblem']}")
        if not row["source"].strip() or not row["note"].strip():
            failures.append(f"{row['tag']}: missing source or rationale")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        rows = direct_rows()
        failures = validate_sources(rows)
        expected = expected_outputs()
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"m11_coa_audit: FAIL\n  - {exc}")
        return 1
    if args.write:
        if failures:
            print("m11_coa_audit: FAIL")
            print("\n".join(f"  - {failure}" for failure in failures))
            return 1
        for path, payload in expected.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
        print(
            "m11_coa_audit: wrote 463 direct standards and "
            f"{len(expected) - 2} regional review sheets"
        )
        return 0
    for path, payload in expected.items():
        if not path.is_file() or path.read_bytes() != payload:
            failures.append(f"stale or missing {path.relative_to(ROOT)}")
    if failures:
        print("m11_coa_audit: FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return 1
    counts = Counter(row["evidence_class"] for row in rows)
    print(
        "m11_coa_audit: PASS "
        f"(463 unique direct compositions; {counts['documented_material_motif']} "
        f"documented; {counts['regional_material_reconstruction']} marked reconstructions; "
        f"{len(expected) - 2} regional sheets)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
