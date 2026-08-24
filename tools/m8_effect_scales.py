#!/usr/bin/env python3
"""Reviewed display-safe magnitude catalogue for ANTIQVITAS advances.

EU5 stores most percentage modifiers as fractions, but a few important advance
effects use different presentation contracts.  Disease resistance is a
zero-decimal percentage; monthly literacy is already expressed in percentage
points; monthly control is a normal percentage despite being a monthly rate.
Keeping those units explicit prevents tiny numeric literals from rendering as
zero or as generator-shaped hundredths of a percent.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


ROLES = ("minor", "standard", "major", "capstone")


@dataclass(frozen=True)
class EffectScale:
    unit: str
    decimals: int
    minor: str
    standard: str
    major: str
    capstone: str
    vanilla_advance_min: str
    vanilla_advance_max: str
    rationale: str

    def values(self) -> tuple[str, ...]:
        return (self.minor, self.standard, self.major, self.capstone)


# Vanilla ranges are taken from the pinned local EU5 advance database rather
# than all static modifiers.  ANTIQVITAS has many more visible nodes, so its
# minor/standard bands are deliberately below most single vanilla cards while
# remaining visible and consequential in the actual UI.
ADVANCE_EFFECT_SCALES: dict[str, EffectScale] = {
    "army_logistics_distance_modifier": EffectScale("percent", 2, "0.03", "0.05", "0.075", "0.10", "0.05", "0.25", "Route knowledge supports larger values than ordinary administrative efficiencies."),
    "army_maintenance_efficiency": EffectScale("percent", 2, "0.01", "0.02", "0.03", "0.05", "0.10", "0.20", "Repeated regional nodes remain below vanilla's large maintenance cards."),
    "country_cabinet_efficiency": EffectScale("percent", 2, "0.01", "0.02", "0.03", "0.05", "0.05", "0.20", "One percent is visible; later capstones reach the vanilla minimum."),
    "cultural_influence_modifier": EffectScale("percent", 2, "0.01", "0.02", "0.03", "0.05", "0.05", "0.20", "Influence rewards use whole percentage-point steps."),
    "discipline": EffectScale("percent", 2, "0.01", "0.015", "0.02", "0.03", "0.025", "0.05", "Discipline is unusually strong, so capstones remain inside vanilla's lower band."),
    "export_efficiency": EffectScale("percent", 2, "0.01", "0.02", "0.03", "0.05", "0.025", "0.20", "Whole percentage steps replace unresolved tiny/small constants on generated cards."),
    "global_disease_resistance": EffectScale("percent", 0, "0.03", "0.05", "0.07", "0.10", "0.03", "0.15", "The panel displays no decimals, so three percent is the smallest reviewed advance reward."),
    "global_institution_growth_modifier": EffectScale("percent", 2, "0.02", "0.05", "0.075", "0.10", "0.05", "0.25", "Institution growth can use broader steps without vanishing in long campaigns."),
    "global_manpower_modifier": EffectScale("percent", 2, "0.01", "0.025", "0.05", "0.075", "0.05", "0.20", "Identity nodes gain useful manpower without matching large static bonuses."),
    "global_monthly_control": EffectScale("percent", 2, "0.001", "0.002", "0.003", "0.005", "0.001", "0.003", "Monthly control uses the vanilla 0.1-0.3 percentage-point cadence, with a rare capstone above it."),
    "global_monthly_literacy": EffectScale("already_percent", 2, "0.01", "0.02", "0.03", "0.05", "0.01", "0.02", "This field is already percentage points; vanilla's 0.01 is the minimum safe step."),
    "global_pop_assimilation_speed_modifier": EffectScale("percent", 2, "0.01", "0.02", "0.03", "0.05", "0.05", "0.20", "Whole percentage steps are legible while keeping cultural change gradual."),
    "global_pop_promotion_speed_modifier": EffectScale("percent", 2, "0.01", "0.02", "0.03", "0.05", "0.05", "0.20", "Promotion rewards follow the same bounded demographic cadence."),
    "global_population_capacity_modifier": EffectScale("percent", 2, "0.01", "0.02", "0.03", "0.05", "0.05", "0.20", "Capacity effects are visible but smaller than major infrastructure modifiers."),
    "global_trade_through_owned_territory_efficiency": EffectScale("percent", 2, "0.02", "0.03", "0.05", "0.075", "0.05", "0.25", "Transit networks merit larger effects than generic merchant upkeep."),
    "import_efficiency": EffectScale("percent", 2, "0.01", "0.02", "0.03", "0.05", "0.025", "0.20", "Generated values resolve to explicit whole percentage steps."),
    "land_morale_modifier": EffectScale("percent", 2, "0.01", "0.02", "0.03", "0.05", "0.05", "0.20", "Repeated nodes remain below most vanilla morale advances."),
    "legislative_efficiency": EffectScale("percent", 2, "0.02", "0.03", "0.05", "0.075", "0.05", "0.20", "Administrative capstones can approach vanilla strength without micro-values."),
    "levy_recovery_modifier": EffectScale("percent", 2, "0.02", "0.03", "0.05", "0.075", "0.05", "0.10", "Recovery needs multi-point values to matter over an ordinary campaign season."),
    "merchant_maintenance_efficiency": EffectScale("percent", 2, "0.01", "0.02", "0.03", "0.05", "0.05", "0.20", "Whole percentage steps replace fractional generator fingerprints."),
    "research_speed_modifier": EffectScale("percent", 2, "0.01", "0.02", "0.03", "0.05", "0.025", "0.20", "Research is cumulative, so minor nodes begin at one percent and cap at vanilla's common value."),
    "stability_cost_efficiency": EffectScale("percent", 2, "0.02", "0.03", "0.05", "0.075", "0.05", "0.20", "Stability investment rewards use a noticeable but bounded cadence."),
    "tax_income_efficiency": EffectScale("percent", 2, "0.01", "0.02", "0.03", "0.05", "0.02", "0.20", "Explicit values replace tiny/small constants and keep fiscal steps readable."),
    "trade_range_modifier": EffectScale("percent", 2, "0.03", "0.05", "0.075", "0.10", "0.10", "0.50", "Range must change actual reach; even minor nodes therefore grant three percent."),
}


def effect_value(field: str, role: str) -> str:
    if field not in ADVANCE_EFFECT_SCALES:
        raise ValueError(f"advance effect {field} has no reviewed scale")
    if role not in ROLES:
        raise ValueError(f"unknown advance-effect role {role}")
    return getattr(ADVANCE_EFFECT_SCALES[field], role)


def resolved_decimal(field: str, value: str) -> Decimal:
    if field not in ADVANCE_EFFECT_SCALES:
        raise ValueError(f"advance effect {field} has no reviewed scale")
    try:
        return Decimal(value)
    except Exception as exc:  # pragma: no cover - defensive error context
        raise ValueError(f"advance effect {field} is not an explicit numeric value: {value}") from exc


def displayed_value(field: str, value: str) -> str:
    scale = ADVANCE_EFFECT_SCALES[field]
    number = resolved_decimal(field, value)
    if scale.unit == "percent":
        number *= Decimal("100")
    elif scale.unit != "already_percent":
        raise ValueError(f"unsupported advance-effect unit {scale.unit} for {field}")
    quantum = Decimal("1").scaleb(-scale.decimals)
    rendered = number.quantize(quantum, rounding=ROUND_HALF_UP)
    return f"{rendered:.{scale.decimals}f}%"


def is_displayed_zero(field: str, value: str) -> bool:
    return Decimal(displayed_value(field, value).removesuffix("%")) == 0
