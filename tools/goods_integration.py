"""Shared source-led bindings for the S2 goods-integration tranche."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs/s2/goods_integration.csv"
FIELDS = (
    "surface", "target", "good", "mechanic", "value",
    "source", "confidence", "note",
)


@dataclass(frozen=True)
class Binding:
    surface: str
    target: str
    good: str
    mechanic: str
    value: str
    source: str
    confidence: str
    note: str


@lru_cache(maxsize=1)
def bindings() -> tuple[Binding, ...]:
    with LEDGER.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError(
                f"{LEDGER.relative_to(ROOT)} header does not match the binding contract"
            )
        rows = tuple(
            Binding(*((row[field] or "").strip() for field in FIELDS))
            for row in reader
        )
    return rows


def for_target(surface: str, target: str) -> tuple[Binding, ...]:
    return tuple(
        row for row in bindings()
        if row.surface == surface and row.target == target
    )


def modifier_name(row: Binding) -> str:
    if row.mechanic == "output_modifier":
        return f"global_{row.good}_output_modifier"
    if row.mechanic == "pop_demand":
        return f"global_{row.good}_pop_demand"
    raise ValueError(
        f"{row.surface}/{row.target}/{row.good}: unsupported modifier mechanic "
        f"{row.mechanic}"
    )


def modifier_additions(surface: str, target: str) -> tuple[tuple[str, str], ...]:
    return tuple(
        (modifier_name(row), row.value)
        for row in for_target(surface, target)
    )


UNIT_BASE_PACKAGES = {
    "a_age_1_traditions_light_infantry": "light_infantry",
    "a_age_1_traditions_heavy_infantry": "heavy_infantry",
    "a_age_1_traditions_light_cavalry": "light_cavalry",
    "a_age_1_traditions_heavy_cavalry": "heavy_cavalry",
    "a_age_4_reformation_heavy_infantry": "heavy_infantry",
    "n_age_1_traditions_galley": "galley",
    "n_age_1_traditions_light_ship": "light_ship",
    "n_age_1_traditions_transport": "transport",
    "n_age_1_traditions_heavy_ship": "heavy_ship",
}


def unit_package(unit_key: str, copy_from: str) -> str:
    if "elephant" in unit_key:
        return "elephant"
    if "camel" in unit_key:
        return "camel"
    if "horse_archer" in unit_key or "parthian_horse" in unit_key:
        return "horse_archer"
    try:
        return UNIT_BASE_PACKAGES[copy_from]
    except KeyError as exc:
        raise ValueError(f"{unit_key}: no goods-demand package for {copy_from}") from exc


def decision_market_rows(target: str) -> tuple[tuple[str, str, str], ...]:
    parsed: list[tuple[str, str, str]] = []
    for row in for_target("decision_market", target):
        if row.mechanic != "threshold_supply" or row.value.count("|") != 1:
            raise ValueError(
                f"decision_market/{target}/{row.good}: expected threshold|supply"
            )
        threshold, supply = row.value.split("|", 1)
        parsed.append((row.good, threshold, supply))
    return tuple(parsed)


def event_effect_lines(target: str) -> tuple[str, ...]:
    """Return country-option effects at the indentation used by M10 renderers."""
    lines: list[str] = []
    market_rows = for_target("event_market", target)
    if market_rows:
        lines.append("\t\tcapital.market = {")
        for row in market_rows:
            if row.mechanic != "supply":
                raise ValueError(
                    f"event_market/{target}/{row.good}: unsupported {row.mechanic}"
                )
            lines.extend((
                "\t\t\tadd_goods_supply = {",
                f"\t\t\t\tgoods = goods:{row.good}",
                f"\t\t\t\tamount = {row.value}",
                "\t\t\t}",
            ))
        lines.append("\t\t}")
    for row in for_target("event_rgo", target):
        if (
            row.mechanic != "change_raw_material"
            or row.good != "antq_silphium"
        ):
            raise ValueError(
                f"event_rgo/{target}/{row.good}: unsupported RGO transition"
            )
        lines.extend((
            "\t\tlocation:barca = {",
            f"\t\t\tchange_raw_material = goods:{row.value}",
            "\t\t}",
        ))
    return tuple(lines)
