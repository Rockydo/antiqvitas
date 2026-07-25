from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from io import StringIO
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "docs/world_1ad/polities.csv"
PROFILES = ROOT / "docs/m4/tag_profiles.csv"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
START_POPS = ROOT / "main_menu/setup/start/06_pops.txt"
OUTPUT = ROOT / "docs/m3/political_granularity.csv"
POP_CULTURE = re.compile(
    r"(?m)^\t(?P<location>[a-z0-9_]+) = \{\r?\n"
    r"\t\tdefine_pop = \{[^\r\n]*\bculture = (?P<culture>[a-z0-9_]+)"
)

GROUPS = {
    "Germania-Scandinavia": {
        "baseline": ("GER", "SUI"),
        "before": 639,
        "cap": 100,
        "new": "CHC CLC CPS VRN MUG SBN BRC SGM CTU GMB CMB RDN AVN SRD EUD SIT SUE NAR LUG NHR MSI BUU MIM HLV HRI HLS ZUM GTL SKN SNR NNR".split(),
    },
    "Venedi-facing eastern Europe": {
        "baseline": ("VEN",),
        "before": 997,
        "cap": 75,
        "new": "PRZ ILM SMD BLR ZRB PDL DNP".split(),
    },
    "Finnic-Uralic-western Siberia": {
        "baseline": ("FIN", "SIB"),
        "before": 337,
        "cap": 50,
        "new": "BLF MOK UVF WHT MRV RZM KRL PRM VLF SUG SMY SRG KUL UGR".split(),
    },
    "Yayoi Japan and Ryukyu": {
        "baseline": ("WAA",),
        "before": 342,
        "cap": 25,
        "new": "HOK SHK OHW RYS KYU IZM KBI TKW EHW".split(),
    },
    "West Africa": {
        "baseline": ("WAF",),
        "before": 367,
        "cap": 50,
        "new": "NOK LCH MNG WGD VLT SNG AKF LNC GUR MUP AIR".split(),
    },
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(line for line in handle if not line.startswith("#")))


def render() -> tuple[str, int, int]:
    roster = {row["tag"]: row for row in rows(ROSTER)}
    profiles = {row["tag"]: row["culture"] for row in rows(PROFILES)}
    ownership = rows(OWNERSHIP)
    counts = Counter(row["tag"] for row in ownership)
    owned = {(row["tag"], row["location"]) for row in ownership}
    pop_cultures = {
        match.group("location"): match.group("culture")
        for match in POP_CULTURE.finditer(START_POPS.read_text(encoding="utf-8-sig"))
    }
    cultures_by_tag: dict[str, set[str]] = {}
    for row in ownership:
        culture = pop_cultures.get(row["location"])
        if culture:
            cultures_by_tag.setdefault(row["tag"], set()).add(culture)
    errors: list[str] = []
    output_rows: list[dict[str, str | int]] = []
    seen_new: set[str] = set()

    for target, spec in GROUPS.items():
        new_tags = spec["new"]
        seen_new.update(new_tags)
        missing = [tag for tag in new_tags if tag not in roster]
        if missing:
            errors.append(f"{target}: missing roster tags {', '.join(missing)}")
        missing_profiles = [tag for tag in new_tags if tag not in profiles]
        if missing_profiles:
            errors.append(f"{target}: missing tag profiles {', '.join(missing_profiles)}")
        empty = [tag for tag in new_tags if counts[tag] == 0]
        if empty:
            errors.append(f"{target}: tags without territory {', '.join(empty)}")
        for tag in new_tags:
            row = roster.get(tag)
            if row and (tag, row["map_capital"]) not in owned:
                errors.append(f"{tag}: capital {row['map_capital']} is not owned")
            if row and (row["tier"] != "3" or row["kind"] != "sop"):
                errors.append(f"{tag}: archaeological/community additions must be Tier-3 SoPs")
            if tag in profiles and profiles[tag] not in cultures_by_tag.get(tag, set()):
                errors.append(
                    f"{tag}: primary culture {profiles[tag]} is absent from owned populations"
                )

        after = sum(counts[tag] for tag in spec["baseline"])
        if after > spec["cap"]:
            errors.append(f"{target}: residual {after} exceeds cap {spec['cap']}")
        largest_tag = max(new_tags, key=lambda tag: counts[tag])
        largest_count = counts[largest_tag]
        if largest_count > 120:
            errors.append(f"{target}: {largest_tag} remains oversized at {largest_count}")
        output_rows.append(
            {
                "target": target,
                "baseline_tags": "+".join(spec["baseline"]),
                "before_locations": spec["before"],
                "after_locations": after,
                "new_polities": len(new_tags),
                "largest_new_tag": largest_tag,
                "largest_new_locations": largest_count,
                "residual_cap": spec["cap"],
            }
        )

    if len(seen_new) != 72:
        errors.append(f"expected 72 distinct additions, found {len(seen_new)}")
    if errors:
        raise ValueError("\n".join(errors))

    stream = StringIO(newline="")
    writer = csv.DictWriter(
        stream,
        fieldnames=(
            "target",
            "baseline_tags",
            "before_locations",
            "after_locations",
            "new_polities",
            "largest_new_tag",
            "largest_new_locations",
            "residual_cap",
        ),
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(output_rows)
    return stream.getvalue(), len(seen_new), sum(int(row["after_locations"]) for row in output_rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("provide exactly one of --write or --check")
    try:
        content, additions, residual = render()
    except (FileNotFoundError, KeyError, ValueError) as exc:
        print(f"political_granularity: FAIL\n  - {exc}")
        return 1
    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(content, encoding="utf-8-sig", newline="")
        print(f"political_granularity: wrote {OUTPUT.relative_to(ROOT)}")
        return 0
    if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8-sig") != content:
        print("political_granularity: FAIL\n  - stale report; run --write")
        return 1
    print(f"political_granularity: PASS ({additions} additions; {residual} residual locations)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
