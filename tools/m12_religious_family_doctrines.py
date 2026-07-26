#!/usr/bin/env python3
"""Generate four sourced doctrine choices for every non-Roman ANTIQVITAS faith."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs/m12/religious_family_doctrines.csv"
MANIFEST = ROOT / "docs/m12/religious_family_doctrines_manifest.json"
SCRIPT = (
    ROOT
    / "in_game/common/religious_aspects/01_antiquitas_m12_family_doctrines.txt"
)
START_POPS = ROOT / "main_menu/setup/start/06_pops.txt"
RELIGION_DATA = ROOT / "docs/m4/religions.csv"
RELIGIONS = ROOT / "in_game/common/religions/antq_m4_religions.txt"
ADVANCE_ART = ROOT / "main_menu/gfx/interface/advance"
RELIGION_ART = ROOT / "main_menu/gfx/interface/icons/religion"
ICON_DIR = ROOT / "main_menu/gfx/interface/icons/religious_aspects"
MASTER_DIR = ROOT / "assets_queue/religious_family_doctrines/masters"
CONTACT_SHEET = (
    ROOT / "docs/m12/religious_family_doctrines_contact_sheet.png"
)
ROMAN_ICON_DIR = ROOT / "main_menu/gfx/interface/icons/religious_aspects"
DDS = ROOT / "tools/dds.py"
LANGUAGES = (
    "english",
    "french",
    "german",
    "spanish",
    "polish",
    "russian",
    "braz_por",
    "simp_chinese",
    "japanese",
    "korean",
    "turkish",
)
FIELDS = (
    "religion",
    "source",
    "confidence",
    "choice_1",
    "choice_2",
    "choice_3",
    "choice_4",
)
PACKAGES = {
    "ritual": (
        ("stability_cost_efficiency", "0.05"),
        ("monthly_religious_influence", "0.05"),
    ),
    "authority": (
        ("monthly_legitimacy", "0.03"),
        ("country_cabinet_efficiency", "0.02"),
    ),
    "learning": (
        ("research_speed_modifier", "0.02"),
        ("global_max_literacy", "0.03"),
    ),
    "community": (
        ("tolerance_own", "1"),
        ("global_monthly_prosperity", "0.02"),
    ),
    "ancestor": (
        ("monthly_legitimacy", "0.03"),
        ("cultural_tradition_modifier", "0.05"),
    ),
    "purity": (
        ("global_life_expectancy", "0.02"),
        ("global_population_growth", "0.02"),
    ),
    "martial": (
        ("land_morale_modifier", "0.025"),
        ("regiment_reinforcement_speed", "0.05"),
    ),
    "pilgrimage": (
        ("global_pop_conversion_speed_modifier", "0.05"),
        ("tolerance_heathen", "1"),
    ),
    "prosperity": (
        ("global_monthly_prosperity", "0.02"),
        ("global_monthly_food_modifier", "0.03"),
    ),
    "nature": (
        ("global_monthly_food_modifier", "0.03"),
        ("global_hostile_attrition", "0.05"),
    ),
}


@dataclass(frozen=True)
class Doctrine:
    key: str
    name: str
    religion: str
    source: str
    confidence: str
    note: str
    package: str
    motif_name: str

    @property
    def motif(self) -> Path:
        return ADVANCE_ART / self.motif_name

    @property
    def badge(self) -> Path:
        return RELIGION_ART / f"{self.religion}.dds"

    @property
    def master(self) -> Path:
        return MASTER_DIR / f"{self.key}_128.png"

    @property
    def texture(self) -> Path:
        return ICON_DIR / f"{self.key}.dds"

    @property
    def modifiers(self) -> tuple[tuple[str, str], ...]:
        return PACKAGES[self.package]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def active_religions() -> set[str]:
    import re

    return set(
        re.findall(
            r"\breligion\s*=\s*(antq_[A-Za-z0-9_]+)",
            START_POPS.read_text(encoding="utf-8-sig"),
        )
    )


def known_religions() -> set[str]:
    with RELIGION_DATA.open(encoding="utf-8-sig", newline="") as handle:
        return {row["key"].strip() for row in csv.DictReader(handle)}


def rows() -> tuple[Doctrine, ...]:
    with LEDGER.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError(
                f"{LEDGER.relative_to(ROOT)} must use header {','.join(FIELDS)}"
            )
        raw = list(reader)
    doctrines: list[Doctrine] = []
    seen_religions: set[str] = set()
    seen_keys: set[str] = set()
    seen_motifs: set[str] = set()
    known = known_religions()
    for number, family in enumerate(raw, start=2):
        religion = (family["religion"] or "").strip()
        source = (family["source"] or "").strip()
        confidence = (family["confidence"] or "").strip()
        if (
            religion in seen_religions
            or religion not in known
            or religion == "antq_religio_romana"
            or not source
            or confidence not in {"secure", "contested"}
        ):
            raise ValueError(f"{LEDGER.relative_to(ROOT)}:{number}: invalid family")
        for index in range(1, 5):
            value = family[f"choice_{index}"] or ""
            parts = [part.strip() for part in value.split("|")]
            if len(parts) != 5:
                raise ValueError(
                    f"{LEDGER.relative_to(ROOT)}:{number}: choice_{index} "
                    "must be slug|name|package|motif|note"
                )
            slug, name, package, motif, note = parts
            key = (
                "antq_doctrine_"
                f"{religion.removeprefix('antq_')}_{slug}"
            )
            if (
                not slug
                or not name
                or package not in PACKAGES
                or not motif.endswith(".dds")
                or not note
                or key in seen_keys
                or motif in seen_motifs
            ):
                raise ValueError(
                    f"{LEDGER.relative_to(ROOT)}:{number}: invalid choice_{index}"
                )
            doctrines.append(
                Doctrine(
                    key=key,
                    name=name,
                    religion=religion,
                    source=source,
                    confidence=confidence,
                    note=note,
                    package=package,
                    motif_name=motif,
                )
            )
            seen_keys.add(key)
            seen_motifs.add(motif)
        seen_religions.add(religion)
    expected = known - {"antq_religio_romana"}
    if seen_religions != expected:
        raise ValueError(
            "family doctrine roster differs from the religion catalog: "
            f"missing={sorted(expected - seen_religions)} "
            f"extra={sorted(seen_religions - expected)}"
        )
    if len(doctrines) != 4 * len(expected):
        raise ValueError("every non-Roman ANTIQVITAS religion needs four choices")
    return tuple(doctrines)


def verify_components(row: Doctrine) -> None:
    if not row.motif.is_file():
        raise ValueError(f"missing reviewed motif for {row.key}: {row.motif}")
    if not row.badge.is_file():
        raise ValueError(f"missing direct religion badge for {row.key}: {row.badge}")


def render_script(doctrines: tuple[Doctrine, ...]) -> bytes:
    lines = [
        "# Generated by tools/m12_religious_family_doctrines.py --write.",
        "# Sourced doctrine choices for every non-Roman ANTIQVITAS religion.",
    ]
    for row in doctrines:
        lines.extend(
            (
                "",
                f"{row.key} = {{ # {row.source}; {row.confidence}; {row.note}",
                f"\ticon = {row.key}",
                f"\treligion = {row.religion}",
                "",
                "\tmodifier = {",
                *(f"\t\t{field} = {value}" for field, value in row.modifiers),
                "\t}",
                "",
                "\topinions = {",
                f"\t\t{row.key} = 10",
                "\t}",
                "}",
            )
        )
    return ("\ufeff" + "\n".join(lines) + "\n").encode("utf-8")


def localization_path(language: str) -> Path:
    return (
        ROOT
        / "main_menu/localization"
        / language
        / f"antq_m12_religious_family_doctrines_l_{language}.yml"
    )


def render_localization(
    doctrines: tuple[Doctrine, ...], language: str
) -> bytes:
    lines = [f"l_{language}:"]
    for row in doctrines:
        name = row.name.replace('"', '\\"')
        note = row.note.replace('"', '\\"')
        lines.extend(
            (
                f' {row.key}: "{name}"',
                f' {row.key}_desc: "{note}"',
            )
        )
    return ("\ufeff" + "\n".join(lines) + "\n").encode("utf-8")


def fit(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    rgba = image.convert("RGBA")
    rgba.thumbnail(size, Image.Resampling.LANCZOS)
    result = Image.new("RGBA", size, (0, 0, 0, 0))
    result.alpha_composite(
        rgba,
        ((size[0] - rgba.width) // 2, (size[1] - rgba.height) // 2),
    )
    return result


def render_master(row: Doctrine) -> Image.Image:
    verify_components(row)
    with Image.open(row.motif) as source:
        master = fit(source, (128, 128))
    with Image.open(row.badge) as source:
        badge = fit(source, (34, 34))
    draw = ImageDraw.Draw(master)
    draw.ellipse((84, 84, 126, 126), fill=(12, 24, 42, 238))
    draw.ellipse((86, 86, 124, 124), outline=(218, 191, 126, 255), width=2)
    master.alpha_composite(badge, (88, 88))
    for point in ((0, 0), (127, 0), (0, 127), (127, 127)):
        master.putpixel(point, (0, 0, 0, 0))
    return master


def image_bytes(image: Image.Image, mode: str = "RGBA") -> bytes:
    output = io.BytesIO()
    image.convert(mode).save(output, format="PNG", optimize=False)
    return output.getvalue()


def render_contact_sheet(doctrines: tuple[Doctrine, ...]) -> Image.Image:
    columns = 10
    cell_width = 176
    cell_height = 168
    rows_count = (len(doctrines) + columns - 1) // columns
    sheet = Image.new(
        "RGB",
        (columns * cell_width, rows_count * cell_height),
        (13, 24, 42),
    )
    draw = ImageDraw.Draw(sheet)
    for index, row in enumerate(doctrines):
        x = (index % columns) * cell_width
        y = (index // columns) * cell_height
        with Image.open(row.master) as source:
            icon = source.convert("RGBA")
        sheet.paste(icon, (x + 24, y + 4), icon)
        label = row.name if len(row.name) <= 24 else row.name[:23] + "…"
        draw.text((x + 4, y + 134), label, fill=(235, 226, 197))
        family = row.religion.removeprefix("antq_")
        family = family if len(family) <= 25 else family[:24] + "…"
        draw.text((x + 4, y + 149), family, fill=(145, 166, 194))
    return sheet


def dds_details(path: Path) -> dict[str, str]:
    result = subprocess.run(
        [sys.executable, str(DDS), "identify", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def manifest_value(doctrines: tuple[Doctrine, ...]) -> dict[str, object]:
    return {
        "ledger": LEDGER.relative_to(ROOT).as_posix(),
        "ledger_sha256": sha256(LEDGER.read_bytes()),
        "covered_religions": sorted({row.religion for row in doctrines}),
        "starting_religions": sorted(
            active_religions() - {"antq_religio_romana"}
        ),
        "choice_count": len(doctrines),
        "choices_per_religion": 4,
        "choices": [
            {
                "key": row.key,
                "religion": row.religion,
                "source": row.source,
                "confidence": row.confidence,
                "motif": row.motif.relative_to(ROOT).as_posix(),
                "motif_sha256": sha256(row.motif.read_bytes()),
                "badge": row.badge.relative_to(ROOT).as_posix(),
                "badge_sha256": sha256(row.badge.read_bytes()),
                "master_sha256": (
                    sha256(row.master.read_bytes())
                    if row.master.is_file()
                    else None
                ),
                "texture_sha256": (
                    sha256(row.texture.read_bytes())
                    if row.texture.is_file()
                    else None
                ),
            }
            for row in doctrines
        ],
    }


def canonical_json(value: dict[str, object]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write() -> None:
    doctrines = rows()
    SCRIPT.parent.mkdir(parents=True, exist_ok=True)
    SCRIPT.write_bytes(render_script(doctrines))
    for language in LANGUAGES:
        target = localization_path(language)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(render_localization(doctrines, language))
    MASTER_DIR.mkdir(parents=True, exist_ok=True)
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    for row in doctrines:
        row.master.write_bytes(image_bytes(render_master(row)))
        subprocess.run(
            [
                sys.executable,
                str(DDS),
                "convert",
                str(row.master),
                str(row.texture),
                "--compression",
                "dxt5",
            ],
            check=True,
            stdout=subprocess.DEVNULL,
        )
    CONTACT_SHEET.write_bytes(
        image_bytes(render_contact_sheet(doctrines), "RGB")
    )
    MANIFEST.write_bytes(canonical_json(manifest_value(doctrines)))
    print(
        "m12_religious_family_doctrines: wrote "
        f"{len(doctrines)} choices for "
        f"{len({row.religion for row in doctrines})} religions"
    )


def check() -> bool:
    try:
        doctrines = rows()
        errors: list[str] = []
        if not SCRIPT.is_file() or SCRIPT.read_bytes() != render_script(doctrines):
            errors.append(f"stale or missing {SCRIPT.relative_to(ROOT)}")
        for language in LANGUAGES:
            target = localization_path(language)
            if (
                not target.is_file()
                or target.read_bytes() != render_localization(doctrines, language)
            ):
                errors.append(f"stale or missing {target.relative_to(ROOT)}")
        religion_text = RELIGIONS.read_text(encoding="utf-8-sig")
        for religion in sorted({row.religion for row in doctrines}):
            start = religion_text.index(f"{religion} = {{")
            end = religion_text.index("\n}", start)
            block = religion_text[start:end]
            if "religious_aspects = 2" not in block:
                errors.append(f"{religion} does not expose two doctrine slots")
            if "has_religious_influence = yes" not in block:
                errors.append(
                    f"{religion} does not expose religious influence"
                )
        texture_hashes: set[str] = set()
        roman_hashes = {
            sha256(path.read_bytes())
            for path in ROMAN_ICON_DIR.glob("antq_roman_*.dds")
        }
        for row in doctrines:
            verify_components(row)
            expected_master = image_bytes(render_master(row))
            if not row.master.is_file() or row.master.read_bytes() != expected_master:
                actual_hash = (
                    sha256(row.master.read_bytes())
                    if row.master.is_file()
                    else "missing"
                )
                errors.append(
                    f"stale or missing master for {row.key}: "
                    f"expected={sha256(expected_master)} actual={actual_hash} "
                    f"motif={sha256(row.motif.read_bytes())} "
                    f"badge={sha256(row.badge.read_bytes())}"
                )
                continue
            if not row.texture.is_file():
                errors.append(f"missing direct texture for {row.key}")
                continue
            with Image.open(row.master) as source:
                rgba = source.convert("RGBA")
                if rgba.size != (128, 128):
                    errors.append(f"{row.key} master is not 128x128")
                if any(
                    rgba.getpixel(point)[3] != 0
                    for point in ((0, 0), (127, 0), (0, 127), (127, 127))
                ):
                    errors.append(f"{row.key} lacks transparent corners")
            details = dds_details(row.texture)
            if (
                details.get("format") != "DDS"
                or details.get("width") != "128"
                or details.get("height") != "128"
                or details.get("channels") != "srgba 4.0"
            ):
                errors.append(f"{row.key} DDS contract is invalid: {details}")
            texture_hash = sha256(row.texture.read_bytes())
            if texture_hash in texture_hashes or texture_hash in roman_hashes:
                errors.append(f"{row.key} duplicates another doctrine texture")
            texture_hashes.add(texture_hash)
        expected_sheet = image_bytes(render_contact_sheet(doctrines), "RGB")
        if (
            not CONTACT_SHEET.is_file()
            or CONTACT_SHEET.read_bytes() != expected_sheet
        ):
            errors.append(f"stale or missing {CONTACT_SHEET.relative_to(ROOT)}")
        expected_manifest = canonical_json(manifest_value(doctrines))
        if not MANIFEST.is_file() or MANIFEST.read_bytes() != expected_manifest:
            errors.append(f"stale or missing {MANIFEST.relative_to(ROOT)}")
        if errors:
            print("m12_religious_family_doctrines: FAIL")
            for error in errors:
                print(f"  - {error}")
            return False
    except (
        OSError,
        ValueError,
        csv.Error,
        json.JSONDecodeError,
        subprocess.CalledProcessError,
    ) as exc:
        print(f"m12_religious_family_doctrines: FAIL\n  - {exc}")
        return False
    print(
        "m12_religious_family_doctrines: PASS "
        f"({len(doctrines)} choices; "
        f"{len({row.religion for row in doctrines})} religions; "
        f"{len(doctrines)} distinct direct icons; {len(LANGUAGES)} clients)"
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
        except (
            OSError,
            ValueError,
            csv.Error,
            json.JSONDecodeError,
            subprocess.CalledProcessError,
        ) as exc:
            print(f"m12_religious_family_doctrines: FAIL\n  - {exc}")
            return 1
    return 0 if check() else 1


if __name__ == "__main__":
    raise SystemExit(main())
