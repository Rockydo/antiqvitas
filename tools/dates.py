#!/usr/bin/env python3
"""Single calendar gateway for every ANTIQVITAS scripted date."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

START = (1, 1, 1)
END = (476, 9, 4)
AUC_OFFSET = 753


@dataclass(frozen=True, order=True)
class AntqDate:
    year: int
    month: int
    day: int

    @classmethod
    def parse(cls, value: str) -> "AntqDate":
        pieces = value.strip().split(".")
        if len(pieces) != 3:
            raise ValueError(f"date must be Y.M.D: {value!r}")
        result = cls(*(int(piece) for piece in pieces))
        result.validate()
        return result

    def validate(self, allow_window: bool = False) -> None:
        if not (1 <= self.month <= 12):
            raise ValueError(f"month out of range: {self}")
        if not (1 <= self.day <= 31):
            raise ValueError(f"day out of range: {self}")
        if not allow_window and not (AntqDate(*START) <= self <= AntqDate(*END)):
            raise ValueError(f"date outside ANTIQVITAS timeline: {self}")

    def engine(self, auc: bool = False) -> str:
        year = self.year + AUC_OFFSET if auc else self.year
        return f"{year}.{self.month}.{self.day}"

    def __str__(self) -> str:
        return f"{self.year}.{self.month}.{self.day}"


def load_timeline(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        value = row.get("date", "")
        if value and value[0].isdigit() and value.count(".") == 2:
            AntqDate.parse(value)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("date", nargs="?")
    parser.add_argument("--auc", action="store_true")
    parser.add_argument("--timeline", type=Path)
    args = parser.parse_args()
    if args.timeline:
        rows = load_timeline(args.timeline)
        print(f"validated {len(rows)} timeline rows")
    elif args.date:
        print(AntqDate.parse(args.date).engine(args.auc))
    else:
        parser.error("provide DATE or --timeline")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
