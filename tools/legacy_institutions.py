#!/usr/bin/env python3
"""Shared removal helpers for the installed post-antique institution registry."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SYMBOLS = ROOT / "docs/vanilla_symbols/institution.json"
REFERENCE_SINK = "antq_hellenism"


def legacy_keys() -> tuple[str, ...]:
    values = json.loads(SYMBOLS.read_text(encoding="utf-8-sig"))
    if not isinstance(values, list) or len(values) != 18:
        raise ValueError("harvested legacy institution inventory must contain 18 keys")
    keys = tuple(str(value) for value in values)
    if len(keys) != len(set(keys)):
        raise ValueError("harvested legacy institution inventory contains duplicates")
    return keys


def reference_pattern() -> re.Pattern[str]:
    keys = "|".join(re.escape(key) for key in legacy_keys())
    return re.compile(rf"\b(?:institution|institution_progress):(?:{keys})\b")


def legacy_references(text: str) -> tuple[str, ...]:
    return tuple(sorted(set(reference_pattern().findall(text))))


def neutralize_predicates(text: str) -> str:
    """Make queries for removed institutions evaluate false without a symbol lookup."""
    keys = "|".join(re.escape(key) for key in legacy_keys())
    result = re.sub(
        rf"\b(?:has_embraced_institution|knows_about_institution|has_institution)"
        rf"\s*=\s*institution:(?:{keys})\b",
        "always = no",
        text,
    )
    result = re.sub(
        rf"\bscope:target\s*=\s*institution:(?:{keys})\b",
        "always = no",
        result,
    )
    result = re.sub(
        rf"\binstitution_progress:(?:{keys})\s*(?:<=|>=|<|>|=)\s*"
        r"[^}\r\n#]+",
        "always = no",
        result,
    )
    return result


def neutralize_references(text: str, *, remap_effects: bool) -> str:
    """Remove query references and optionally bind unreachable residual effects.

    Remaining references are effect ``type`` values or institution scopes.
    Callers may remap those only after they have independently made their
    containing gameplay surface unreachable.
    """
    result = neutralize_predicates(text)
    if remap_effects:
        keys = "|".join(re.escape(key) for key in legacy_keys())
        result = re.sub(
            rf"\binstitution_progress:(?:{keys})\b",
            f"institution_progress:{REFERENCE_SINK}",
            result,
        )
        result = re.sub(
            rf"\binstitution:(?:{keys})\b",
            f"institution:{REFERENCE_SINK}",
            result,
        )
    remaining = legacy_references(result)
    if remaining:
        raise ValueError(f"legacy institution references remain: {remaining}")
    return result
