#!/usr/bin/env python3
"""Reject cloned religion mechanics, empty views, and effectless foundations."""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

import generate_m4_definitions as m4


ROOT = Path(__file__).resolve().parents[1]
RELIGIONS = ROOT / "in_game/common/religions/antq_m4_religions.txt"
GROUPS = ROOT / "in_game/common/religion_groups/antq_m4_groups.txt"
ASPECTS = ROOT / "in_game/common/religious_aspects/01_antiquitas_m12_family_doctrines.txt"
INSTITUTION_SPREAD = ROOT / "in_game/common/scripted_triggers/00_antiquitas_m8_institution_spread.txt"
FIRST_CENTURY = ROOT / "in_game/events/antq_m10_first_century.txt"
SECOND_CENTURY = ROOT / "in_game/events/antq_m10_second_century.txt"
THIRD_CENTURY = ROOT / "in_game/events/antq_m10_third_century.txt"


def block(text: str, key: str) -> str:
    match = re.search(rf"(?m)^{re.escape(key)}\s*=\s*\{{", text)
    if not match:
        raise ValueError(f"missing definition {key}")
    depth = 0
    quoted = False
    escaped = False
    for index in range(match.end() - 1, len(text)):
        char = text[index]
        if escaped:
            escaped = False
        elif char == "\\" and quoted:
            escaped = True
        elif char == '"':
            quoted = not quoted
        elif not quoted and char == "{":
            depth += 1
        elif not quoted and char == "}":
            depth -= 1
            if depth == 0:
                return text[match.start():index + 1]
    raise ValueError(f"unclosed definition {key}")


def audit_rows() -> list[dict[str, str]]:
    with m4.RELIGION_MECHANICS_AUDIT.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def check() -> int:
    failures: list[str] = []
    definitions = m4.definitions(m4.RELIGIONS)
    known = {row.key for row in definitions}
    rows = audit_rows()
    if len(rows) != len(definitions) or {row["religion"] for row in rows} != known:
        failures.append("religion mechanics audit does not cover the full catalog")
    profiles = {row["profile"] for row in rows}
    if len(profiles) < 20:
        failures.append(f"religion mechanics expose only {len(profiles)} profiles")
    if {row["slots"] for row in rows} != {"1", "2", "3"}:
        failures.append("religion aspect-slot ladder is incomplete")
    if {row["influence"] for row in rows} != {"yes", "no"}:
        failures.append("religious influence access is not differentiated")
    modifier_sets = {row["modifiers"] for row in rows}
    if len(modifier_sets) < 20:
        failures.append("religion definition modifiers remain mechanically cloned")
    conversion = {
        match.group(1)
        for row in rows
        if (match := re.search(r"global_pop_conversion_speed_modifier=([-0-9.]+)", row["modifiers"]))
    }
    if not any(value.startswith("-") for value in conversion) or not any(
        not value.startswith("-") and float(value) > 0 for value in conversion
    ):
        failures.append("conversion profiles do not span bounded/missionary behavior")
    if sum("monthly_legitimacy=" in row["modifiers"] for row in rows) < 6:
        failures.append("state-temple authority profiles are underrepresented")

    text = RELIGIONS.read_text(encoding="utf-8-sig")
    enable_rows: dict[str, str] = {}
    opinion_values: set[str] = set()
    rendered_opinions: dict[str, dict[str, str]] = {}
    for row in definitions:
        rendered = block(text, row.key)
        mechanics = m4.religion_mechanics(row)
        if f"group = {m4.native_religion_group(row)}" not in rendered:
            failures.append(f"{row.key}: native mechanics group drifted")
        if f"religious_aspects = {mechanics.slots}" not in rendered:
            failures.append(f"{row.key}: aspect slots drifted")
        if mechanics.influence != ("has_religious_influence = yes" in rendered):
            failures.append(f"{row.key}: influence capability drifted")
        enable = re.search(r"(?m)^\s*enable\s*=\s*([0-9.]+)", rendered)
        if enable:
            enable_rows[row.key] = enable.group(1)
        if re.search(r"opinions\s*=\s*\{\s*\}", rendered, re.S):
            failures.append(f"{row.key}: empty opinion block survived")
        pairs = dict(
            re.findall(
                r"(?m)^\s*(antq_[A-Za-z0-9_]+)\s*=\s*"
                r"(kindred|positive|negative|enemy)\s*$",
                rendered,
            )
        )
        rendered_opinions[row.key] = pairs
        opinion_values.update(pairs.values())
        if row.key in pairs:
            failures.append(f"{row.key}: self-directed religious opinion survived")
        unknown_targets = set(pairs) - known
        if unknown_targets:
            failures.append(
                f"{row.key}: religious opinions reference unknown targets "
                f"{sorted(unknown_targets)}"
            )
    expected_dates = {
        key: value[0].engine() for key, value in m4.religion_availability().items()
    }
    if enable_rows != expected_dates:
        failures.append(f"religion enable dates drifted: {enable_rows}")
    if not {"kindred", "positive", "negative"}.issubset(opinion_values):
        failures.append("interfaith views lack kindred/positive/negative distinctions")
    for source, targets in rendered_opinions.items():
        for target, value in targets.items():
            reciprocal = rendered_opinions.get(target, {}).get(source)
            if reciprocal != value:
                failures.append(
                    f"{source}/{target}: asymmetric religious opinion "
                    f"({value!r} versus {reciprocal!r})"
                )
    if "group = christian" not in block(text, "antq_early_christianity"):
        failures.append("early Christianity is not in the populated native Christian group")
    if "group = folk_se_asian_group" not in block(text, "antq_mainland_southeast_asian_traditions"):
        failures.append("mainland local traditions still inherit Buddhist mechanics")
    if GROUPS.read_text(encoding="utf-8-sig").count("= {"):
        failures.append("empty custom religion-group adapters returned")

    aspect_text = ASPECTS.read_text(encoding="utf-8-sig")
    aspects_by_religion: dict[str, list[str]] = defaultdict(list)
    for aspect_key in re.findall(r"(?m)^(antq_doctrine_[A-Za-z0-9_]+)\s*=\s*\{", aspect_text):
        rendered = block(aspect_text, aspect_key)
        religion_match = re.search(r"(?m)^\s*religion\s*=\s*(antq_[A-Za-z0-9_]+)", rendered)
        if religion_match:
            aspects_by_religion[religion_match.group(1)].append(rendered)
    for religion in known - {"antq_religio_romana"}:
        aspect_blocks = aspects_by_religion[religion]
        if len(aspect_blocks) != 4:
            failures.append(f"{religion}: expected four sourced doctrine choices")
        elif any("modifier = {" not in item or "opinions = {" not in item for item in aspect_blocks):
            failures.append(f"{religion}: empty doctrine mechanics survived")

    spread = INSTITUTION_SPREAD.read_text(encoding="utf-8-sig")
    if spread.count("religion_group:christian") < 2 or "antq_christian_group" in spread:
        failures.append("Christian institutions do not use the populated native group")
    foundation_contracts = (
        (FIRST_CENTURY, "location:jerusalem", "fraction = 0.02 religion = religion:antq_early_christianity"),
        (SECOND_CENTURY, "location:chengdu", "fraction = 0.03 religion = religion:antq_daoism"),
        (THIRD_CENTURY, "capital = {", "fraction = 0.02 religion = religion:antq_manichaeism"),
    )
    for path, anchor, seed in foundation_contracts:
        payload = path.read_text(encoding="utf-8-sig")
        if anchor not in payload or seed not in payload:
            failures.append(f"{path.name}: religion foundation does not seed a bounded pop")

    if failures:
        print("s4_religion_profiles: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(
        "s4_religion_profiles: PASS "
        f"({len(rows)} religions; {len(profiles)} profiles; "
        f"{len(modifier_sets)} modifier sets; 3 dated foundations)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(check())
