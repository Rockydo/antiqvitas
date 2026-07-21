#!/usr/bin/env python3
"""Validate M11's non-placeholder standards for scripted future polities."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"


@dataclass(frozen=True)
class DynamicCoa:
    filename: str
    tag: str
    emblem: str


COAS = (
    DynamicCoa("antq_m10_transformations.txt", "KSH", "ce_auspicious_conch_shell_simple.dds"),
    DynamicCoa("antq_m10_transformations.txt", "XSO", "ce_horse_salient.dds"),
    DynamicCoa("antq_m10_transformations.txt", "XNO", "ce_horse_salient.dds"),
    DynamicCoa("antq_m10_second_century.txt", "CPC", "ce_auspicious_conch_shell_simple.dds"),
    DynamicCoa("antq_m10_second_century.txt", "MOC", "ce_andean_small_bird.dds"),
    DynamicCoa("antq_m10_third_century.txt", "ALM", "ce_boar_passant.dds"),
    DynamicCoa("antq_m10_third_century.txt", "SAS", "ce_horse_salient.dds"),
    DynamicCoa("antq_m10_third_century.txt", "FRK", "ce_boar_passant.dds"),
    DynamicCoa("antq_m10_fourth_century.txt", "HNS", "ce_horse_salient.dds"),
    DynamicCoa("antq_m10_fourth_century.txt", "WRE", "ce_eagle.dds"),
    DynamicCoa("antq_m10_fourth_century.txt", "ERO", "ce_eagle.dds"),
    DynamicCoa("antq_m10_final_century.txt", "VSG", "ce_boar_passant.dds"),
    DynamicCoa("antq_m10_final_century.txt", "VND", "ce_boar_passant.dds"),
    DynamicCoa("antq_m10_final_century.txt", "ODO", "ce_eagle.dds"),
)


def matching_block(text: str, open_brace: int) -> str:
    depth = 0
    for index, character in enumerate(text[open_brace:], open_brace):
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                return text[open_brace:index + 1]
    raise ValueError("unterminated coat-of-arms block")


def coa_block(path: Path, tag: str) -> str:
    text = path.read_text(encoding="utf-8-sig")
    found = re.search(rf"(?m)^{re.escape(tag)}\s*=\s*\{{", text)
    if found is None:
        raise ValueError(f"M11 dynamic CoA {tag} is missing from {path}")
    return matching_block(text, found.end() - 1)


def validate() -> None:
    game_dir = Path(json.loads(CONFIG.read_text(encoding="utf-8"))["game_dir"])
    colored_emblems = game_dir / "game/main_menu/gfx/coat_of_arms/colored_emblems"
    seen = set()
    for asset in COAS:
        if asset.tag in seen:
            raise ValueError(f"duplicate M11 dynamic CoA tag: {asset.tag}")
        seen.add(asset.tag)
        path = ROOT / "main_menu/common/coat_of_arms/coat_of_arms" / asset.filename
        block = coa_block(path, asset.tag)
        if 'pattern = "pattern_solid.dds"' not in block:
            raise ValueError(f"M11 dynamic CoA {asset.tag} lost the checked base pattern")
        if "colored_emblem" not in block or f'texture = "{asset.emblem}"' not in block:
            raise ValueError(f"M11 dynamic CoA {asset.tag} lacks its reviewed emblem")
        if not all(f"color{index} =" in block for index in (1, 2, 3)):
            raise ValueError(f"M11 dynamic CoA {asset.tag} lacks a full color contract")
        if not (colored_emblems / asset.emblem).is_file():
            raise ValueError(f"M11 dynamic CoA {asset.tag} references missing local emblem {asset.emblem}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate M11 dynamic standards")
    parser.parse_args()
    validate()
    print(f"m11_dynamic_coas: PASS ({len(COAS)} reviewed scripted-formation standards)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
