#!/usr/bin/env python3
"""Select period-valid Pleiades name resources for automatic map labels.

Pleiades place titles are resource labels and may be modern excavation names.
Automatic generators must therefore join a place to its associated name records
and select a complete, non-modern form attested across AD 1.
"""
from __future__ import annotations

import csv
import gzip
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

ROOT = Path(__file__).resolve().parents[1]
NAMES_SOURCE = ROOT / ".cache/pleiades/pleiades-names-latest.csv.gz"

MODERN_LANGUAGES = frozenset(
    {
        "ar",
        "arb",
        "bg",
        "ca",
        "de",
        "el",
        "en",
        "es",
        "fa",
        "fr",
        "he",
        "hr",
        "it",
        "ku",
        "ota",
        "pl",
        "pt",
        "ro",
        "ru",
        "sr",
        "tr",
        "uk",
    }
)
BAD_CHARACTERS = frozenset("?*[]()0123456789")
MODERN_SITE_RE = re.compile(
    r"\b(?:archaeological|castle|château|church|excavation|henchir|khirbet|kodra|"
    r"monastery|mosque|necropolis|quarry|ruins?|saint|san|santa|santo|sidi|site|"
    r"tell|tel|tall|tepe|tomb|tumulus|tulul|villa)\b",
    re.IGNORECASE,
)
MODERN_NAME_TYPE_RE = re.compile(r"(?:associated[-_ ]modern|modern)", re.IGNORECASE)
UNCERTAIN_RE = re.compile(r"(?:uncertain|less[-_ ]certain)", re.IGNORECASE)
FRAGMENTARY_RE = re.compile(r"(?:fragment|incomplete)", re.IGNORECASE)

# Pleiades primarily uses BCP-47/ISO language tags. The legacy dump often
# leaves the field blank, so these preferences are bonuses rather than gates.
M4_LANGUAGE_PREFERENCES: dict[str, tuple[str, ...]] = {
    "latin_language": ("la",),
    "greek_language": ("grc", "grc-latn"),
    "aramaic_language": ("arc", "syc", "phn", "hbo"),
    "coptic_language": ("egy", "cop"),
    "nubian_language": ("xmr",),
    "persian_language": ("peo", "pal", "xpr"),
}


@dataclass(frozen=True)
class HistoricalName:
    place_id: str
    name_id: str
    form: str
    language: str
    min_date: float
    max_date: float

    @property
    def source_id(self) -> str:
        return f"{self.place_id}/{self.name_id}"


def normalized(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    asciiish = "".join(char for char in decomposed if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]", "", asciiish.casefold())


def preferred_languages(m4_language: str) -> tuple[str, ...]:
    return M4_LANGUAGE_PREFERENCES.get(m4_language.strip(), ())


def _open(path: Path) -> TextIO:
    if path.suffix.casefold() == ".gz":
        return gzip.open(path, "rt", encoding="utf-8-sig", newline="")
    return path.open(encoding="utf-8-sig", newline="")


def _first(row: dict[str, str], *keys: str) -> str:
    for key in keys:
        value = (row.get(key) or "").strip()
        if value:
            return value
    return ""


def _date(row: dict[str, str], *keys: str) -> float | None:
    raw = _first(row, *keys)
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _place_id(row: dict[str, str]) -> str:
    direct = _first(row, "place_id")
    if direct:
        return direct.rstrip("/").split("/")[-1]
    pid = _first(row, "pid")
    return pid.rstrip("/").split("/")[-1] if pid else ""


def _name_id(row: dict[str, str]) -> str:
    # The legacy CSV exposes a stable name-resource slug as ``id`` and a UUID as
    # ``uid``. The GIS export may expose the full resource id. Keep a short,
    # source-readable final path component in either case.
    raw = _first(row, "id", "uid")
    return raw.rstrip("/").split("/")[-1] if raw else ""


def _safe_row(row: dict[str, str]) -> HistoricalName | None:
    place_id = _place_id(row)
    name_id = _name_id(row)
    form = _first(row, "title", "romanized_form_1", "nameTransliterated")
    language = _first(row, "language_tag", "nameLanguage").casefold()
    min_date = _date(row, "year_after_which", "minDate")
    max_date = _date(row, "year_before_which", "maxDate")
    if not place_id or not name_id or min_date is None or max_date is None:
        return None
    if not min_date <= 1 <= max_date:
        return None
    if not 2 <= len(form) <= 72 or any(char in BAD_CHARACTERS for char in form):
        return None
    if "/" in form or "," in form or form.casefold().startswith(("untitled", "unknown")):
        return None
    if MODERN_SITE_RE.search(form):
        return None
    if language in MODERN_LANGUAGES:
        return None
    if MODERN_NAME_TYPE_RE.search(_first(row, "name_type")):
        return None
    if UNCERTAIN_RE.search(_first(row, "association_certainty")):
        return None
    if FRAGMENTARY_RE.search(_first(row, "transcription_completeness")):
        return None
    period_keys = {
        token.strip().casefold()
        for token in _first(row, "timePeriodsKeys", "time_period_keys").split(",")
        if token.strip()
    }
    if period_keys and period_keys <= {"modern"}:
        return None
    return HistoricalName(place_id, name_id, form, language, min_date, max_date)


class PleiadesNameIndex:
    def __init__(self, entries: dict[str, tuple[HistoricalName, ...]]) -> None:
        self._entries = entries

    @classmethod
    def load(cls, path: Path = NAMES_SOURCE) -> "PleiadesNameIndex":
        if not path.is_file():
            try:
                display = path.relative_to(ROOT)
            except ValueError:
                display = path
            raise FileNotFoundError(f"missing cached Pleiades names snapshot: {display}")
        grouped: dict[str, list[HistoricalName]] = {}
        with _open(path) as handle:
            for row in csv.DictReader(handle):
                entry = _safe_row(row)
                if entry is not None:
                    grouped.setdefault(entry.place_id, []).append(entry)
        if not grouped:
            try:
                display = path.relative_to(ROOT)
            except ValueError:
                display = path
            raise ValueError(f"{display} contains no usable AD 1 name records")
        return cls(
            {
                place_id: tuple(
                    sorted(values, key=lambda value: (value.form.casefold(), value.name_id))
                )
                for place_id, values in grouped.items()
            }
        )

    def best(
        self,
        place_id: str,
        place_title: str = "",
        preferred: tuple[str, ...] = (),
    ) -> HistoricalName | None:
        entries = self._entries.get(str(place_id).strip(), ())
        if not entries:
            return None
        title = normalized(place_title)
        preferred_order = {language.casefold(): index for index, language in enumerate(preferred)}

        def score(entry: HistoricalName) -> tuple[int, int, int, int, int, str, str]:
            language = entry.language.casefold()
            preferred_rank = preferred_order.get(language)
            return (
                int(bool(title) and normalized(entry.form) == title),
                int(preferred_rank is not None),
                -(preferred_rank if preferred_rank is not None else len(preferred_order)),
                int(not language),
                -len(entry.form),
                entry.form.casefold(),
                entry.name_id,
            )

        return max(entries, key=score)
