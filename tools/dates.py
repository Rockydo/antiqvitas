#!/usr/bin/env python3
"""Single calendar gateway for every ANTIQVITAS scripted date."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START = (1, 1, 1)
END = (476, 9, 4)
AUC_OFFSET = 753
# Character biographies can legitimately predate the playable calendar: the
# AD 1 roster includes, for example, Augustus (born 63 BCE).  This deliberately
# narrow range is *not* a second campaign calendar.  All dates that drive game
# time continue to use AntqDate below.
BIOGRAPHY_START_YEAR = -1000
BIOGRAPHY_END_YEAR = END[0]
M2_TIMELINE_KEYS = (
    "start",
    "age_principate",
    "age_high_empires",
    "age_crisis",
    "age_dominate",
    "age_migrations",
    "end",
)
TIMELINE_CONTENT_TYPES = frozenset({"situation", "disaster", "event", "tagswitch", "formation"})
TIMELINE_RAILS = frozenset({"Strong", "Mild", "Off", "system"})
M2_LOCALIZATIONS = {
    "age_1_traditions": "Principate",
    "age_1_traditions_desc": "The Mediterranean and East Asian imperial orders enter the first century of ANTIQVITAS.",
    "age_2_renaissance": "High Empires",
    "age_2_renaissance_desc": "Large imperial systems, trade routes, and literate institutions reach a mature imperial balance.",
    "age_3_discovery": "Crisis",
    "age_3_discovery_desc": "War, epidemic disease, fiscal pressure, and contested succession reshape the old imperial order.",
    "age_4_reformation": "Dominate",
    "age_4_reformation_desc": "New state structures, religious institutions, and frontier armies consolidate late-antique power.",
    "age_5_absolutism": "Migrations",
    "age_5_absolutism_desc": "Migration, federate settlement, and successor kingdoms transform the Roman world.",
}
M2_MIRROR_LANGUAGES = (
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


@dataclass(frozen=True, order=True)
class BiographyDate:
    """Validate a signed historical date used only in character biographies."""

    year: int
    month: int
    day: int

    @classmethod
    def parse(cls, value: str) -> "BiographyDate":
        pieces = value.strip().split(".")
        if len(pieces) != 3:
            raise ValueError(f"biography date must be Y.M.D: {value!r}")
        result = cls(*(int(piece) for piece in pieces))
        result.validate()
        return result

    def validate(self) -> None:
        if not (BIOGRAPHY_START_YEAR <= self.year <= BIOGRAPHY_END_YEAR) or self.year == 0:
            raise ValueError(f"biography year outside supported historical range: {self}")
        if not (1 <= self.month <= 12):
            raise ValueError(f"month out of range: {self}")
        if not (1 <= self.day <= 31):
            raise ValueError(f"day out of range: {self}")

    def engine(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"{self.year}.{self.month}.{self.day}"


def load_timeline(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("timeline must contain at least one row")
    keys: set[str] = set()
    previous: AntqDate | None = None
    for row in rows:
        key = row.get("key", "").strip()
        value = row.get("date", "").strip()
        if not key or not value:
            raise ValueError("timeline rows require both key and date")
        if key in keys:
            raise ValueError(f"duplicate timeline key: {key}")
        keys.add(key)
        start = AntqDate.parse(value)
        if previous is not None and start < previous:
            raise ValueError(f"timeline key {key} is out of chronological order")
        previous = start
        end_value = row.get("end_date", "").strip()
        if end_value:
            end = AntqDate.parse(end_value)
            if end <= start:
                raise ValueError(f"timeline window for {key} must end after its start")
        content_type = row.get("type", "").strip()
        if content_type and content_type not in TIMELINE_CONTENT_TYPES:
            raise ValueError(f"timeline key {key} has unsupported type {content_type!r}")
        rails = row.get("rails_strength", "").strip()
        if rails and rails not in TIMELINE_RAILS:
            raise ValueError(f"timeline key {key} has unsupported rails strength {rails!r}")
        if content_type and (not row.get("region", "").strip() or not row.get("summary", "").strip()):
            raise ValueError(f"timeline key {key} requires region and summary")
    return rows


def indexed_timeline(path: Path) -> dict[str, AntqDate]:
    result: dict[str, AntqDate] = {}
    for row in load_timeline(path):
        key = row.get("key", "").strip()
        value = row.get("date", "").strip()
        if key and value:
            if key in result:
                raise ValueError(f"duplicate timeline key: {key}")
            result[key] = AntqDate.parse(value)
    missing = [key for key in M2_TIMELINE_KEYS if key not in result]
    if missing:
        raise ValueError(f"timeline missing M2 keys: {', '.join(missing)}")
    if result["start"] != AntqDate(*START) or result["end"] != AntqDate(*END):
        raise ValueError("timeline start/end do not match ANTIQVITAS constants")
    ordered = [result[key] for key in M2_TIMELINE_KEYS]
    if ordered != sorted(ordered):
        raise ValueError("M2 timeline dates must be chronological")
    return result


def m2_defines(timeline: dict[str, AntqDate], auc: bool = False) -> str:
    return (
        "# Generated by tools/dates.py --write-m2; do not hand-edit dates.\n"
        "NGame = {\n"
        f'\tSTART_DATE = "{timeline["start"].engine(auc)}"\n'
        f'\tEND_DATE = "{timeline["end"].engine(auc)}"\n'
        "}\n"
    )


def m2_ages(timeline: dict[str, AntqDate], auc: bool = False) -> str:
    # `victory_card` is the installed age-objective contract; `unique` is the
    # locally verified age-ability contract.  M8 supplies the advances that
    # make those broad era abilities historically specific.
    ages = (
        ("age_1_traditions", "age_principate", 0, "cultural_tradition_modifier", "0.05"),
        ("age_2_renaissance", "age_high_empires", 1, "diplomatic_capacity_modifier", "0.10"),
        ("age_3_discovery", "age_crisis", 2, "global_war_score_efficiency", "0.05"),
        ("age_4_reformation", "age_dominate", 3, "global_pop_conversion_speed_modifier", "0.10"),
        ("age_5_absolutism", "age_migrations", 4, "global_integration_speed_modifier", "0.10"),
    )
    blocks = [
        "# Generated by tools/dates.py --write-m2; five playable ANTIQVITAS ages.",
        "# Vanilla age keys are intentionally retained for current database compatibility.",
    ]
    for key, timeline_key, victory_card, ability, value in ages:
        date = timeline[timeline_key]
        year = date.year + (AUC_OFFSET if auc else 0)
        blocks.extend(
            (
                f"{key} = {{",
                f"\tyear = {year}",
                "\tprice_stability = 0.1",
                "\tmax_price = 3",
                "\tknown_goods_demand_threshold = 100",
                "\tburgher_max_trade_range = 600",
                "\tmonths_for_exploration_spread = 1800",
                f"\tunique = {{ {ability} = {value} }}",
                "\tefficiency = 1.0",
                f"\tvictory_card = {victory_card}",
                "}",
            )
        )
    compatibility_year = timeline["end"].year + 1 + (AUC_OFFSET if auc else 0)
    blocks.extend(
        (
            "# Engine compatibility only: vanilla files reference this key; it begins after END_DATE.",
            "age_6_revolutions = {",
            f"\tyear = {compatibility_year}",
            "\tprice_stability = 0.1",
            "\tmax_price = 3",
            "\tknown_goods_demand_threshold = 100",
            "\tburgher_max_trade_range = 600",
            "\tmonths_for_exploration_spread = 1800",
            "\tefficiency = 1.0",
            "\tvictory_card = 5",
            "}",
        )
    )
    return "\n".join(blocks) + "\n"


def m2_localization(language: str) -> str:
    lines = [f"l_{language}:"]
    lines.extend(
        f' {key}: "{value.replace(chr(34), chr(39))}"'
        for key, value in M2_LOCALIZATIONS.items()
    )
    return "\n".join(lines) + "\n"


def m2_outputs(root: Path, timeline: dict[str, AntqDate], auc: bool = False) -> dict[Path, str]:
    outputs = {
        root / "loading_screen/common/defines/antq_dates.txt": m2_defines(timeline, auc),
        root / "in_game/common/age/00_default.txt": m2_ages(timeline, auc),
    }
    for language in ("english", *M2_MIRROR_LANGUAGES):
        path = root / f"main_menu/localization/{language}/antq_m2_ages_l_{language}.yml"
        outputs[path] = m2_localization(language)
    return outputs


def write_m2(root: Path, timeline: dict[str, AntqDate], auc: bool = False) -> None:
    outputs = m2_outputs(root, timeline, auc)
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8-sig", newline="\n")
        print(f"wrote {path.relative_to(root)}")


def check_m2(root: Path, timeline: dict[str, AntqDate], auc: bool = False) -> bool:
    failures: list[str] = []
    for path, expected in m2_outputs(root, timeline, auc).items():
        if not path.is_file():
            failures.append(f"missing {path.relative_to(root)}")
        elif path.read_text(encoding="utf-8-sig") != expected:
            failures.append(f"stale {path.relative_to(root)}")
    if failures:
        print("dates: M2 FAIL")
        print("\n".join(f"  - {failure}" for failure in failures))
        return False
    print("dates: M2 PASS (calendar, five ages, and mirrored localization)")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("date", nargs="?")
    parser.add_argument("--auc", action="store_true")
    parser.add_argument(
        "--biography",
        metavar="DATE",
        help="validate a signed character-biography date; campaign dates remain AntqDate-only",
    )
    parser.add_argument("--timeline", type=Path)
    parser.add_argument(
        "--write-m2",
        action="store_true",
        help="generate M2 date and age scripts from docs/timeline.csv",
    )
    parser.add_argument(
        "--check-m2",
        action="store_true",
        help="verify M2 generated scripts match docs/timeline.csv",
    )
    args = parser.parse_args()
    timeline_path = args.timeline or ROOT / "docs/timeline.csv"
    if args.write_m2 and args.check_m2:
        parser.error("--write-m2 and --check-m2 are mutually exclusive")
    if args.write_m2:
        write_m2(ROOT, indexed_timeline(timeline_path), args.auc)
    elif args.check_m2:
        return 0 if check_m2(ROOT, indexed_timeline(timeline_path), args.auc) else 1
    elif args.timeline:
        rows = load_timeline(args.timeline)
        print(f"validated {len(rows)} timeline rows")
    elif args.biography:
        if args.date:
            parser.error("provide either DATE or --biography DATE, not both")
        print(BiographyDate.parse(args.biography).engine())
    elif args.date:
        print(AntqDate.parse(args.date).engine(args.auc))
    else:
        parser.error("provide DATE or --timeline")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
