#!/usr/bin/env python3
"""Expand sourced road corridors into installed-map-adjacent location steps."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
from collections import defaultdict, deque
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
COORDINATES = ROOT / "docs/vanilla_symbols/location_coordinates.json"
OWNERSHIP = ROOT / "docs/world_1ad/ownership_resolved.csv"
CORRIDORS = ROOT / "docs/m5/road_segments.csv"
OUTPUT = ROOT / "docs/m5/road_segments_topology.csv"
EXCLUSIONS = ROOT / "docs/m5/road_topology_exclusions.csv"
FIELDS = (
    "corridor_origin", "corridor_destination", "step", "origin",
    "destination", "corridor", "source", "confidence", "note",
)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(line for line in handle if not line.startswith("#")))


def game_map() -> Path:
    config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
    return Path(config["game_dir"]) / "game/in_game/map_data/locations.png"


def installed_roads() -> Path:
    config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
    return Path(config["game_dir"]) / "game/main_menu/setup/start/09_roads.txt"


class Topology:
    def __init__(
        self, controlled: set[str], excluded_edges: frozenset[tuple[str, str]]
    ) -> None:
        Image.MAX_IMAGE_PIXELS = None
        self.image = Image.open(game_map())
        if self.image.mode != "RGB":
            self.image = self.image.convert("RGB")
        self.pixels = self.image.load()
        self.width, self.height = self.image.size
        payload = json.loads(COORDINATES.read_text(encoding="utf-8-sig"))
        expected = payload["image_size"]
        if (expected["width"], expected["height"]) != self.image.size:
            raise ValueError("harvested location coordinates do not match locations.png")
        self.coordinates: dict[str, dict[str, float]] = payload["locations"]
        self.controlled = controlled
        self.excluded_edges = excluded_edges
        installed_road_text = installed_roads().read_text(encoding="utf-8-sig")
        self.engine_proven_edges = frozenset(
            tuple(sorted(match.groups()))
            for match in re.finditer(
                r"(?m)^\s*([a-z0-9_]+)\s*=\s*([a-z0-9_]+)\s*$",
                installed_road_text,
            )
        )
        self.by_color: defaultdict[tuple[int, int, int], list[str]] = defaultdict(list)
        for key, value in self.coordinates.items():
            point = (round(value["x"]) % self.width, round(value["y"]))
            self.by_color[self.pixels[point]].append(key)
        # locations.png legitimately reuses RGB values for disconnected map
        # components (including land/sea pairs such as kos/icarian_sea).  A
        # centroid-only lookup therefore invents land adjacency across water.
        # Label reused-color components lazily from their actual pixels.
        self.component_by_pixel: dict[tuple[int, int], tuple[str, ...]] = {}
        self.cache: dict[str, frozenset[str]] = {}

    def component_location(
        self, color: tuple[int, int, int], x: int, y: int, current: str
    ) -> str | None:
        candidates = self.by_color.get(color, ())
        if not candidates:
            return None
        if len(candidates) == 1:
            return candidates[0]
        options = self.component_by_pixel.get((x, y))
        if options is None:
            pending = deque([(x, y)])
            component = {(x, y)}
            while pending:
                px, py = pending.popleft()
                for nx, ny in (
                    ((px - 1) % self.width, py),
                    ((px + 1) % self.width, py),
                    (px, py - 1),
                    (px, py + 1),
                ):
                    point = (nx, ny)
                    if (
                        ny < 0
                        or ny >= self.height
                        or point in component
                        or self.pixels[nx, ny] != color
                    ):
                        continue
                    component.add(point)
                    pending.append(point)

            seeded = []
            for key in candidates:
                value = self.coordinates[key]
                point = (round(value["x"]) % self.width, round(value["y"]))
                if point in component:
                    seeded.append(key)
            options = tuple(seeded or candidates)
            for point in component:
                self.component_by_pixel[point] = options

        # Some reused colors are contiguous in the raster even though nodes.dat
        # divides them into separate logical land/sea locations.  Only the
        # installed road graph is authoritative in that ambiguous case.  It is
        # a positive engine-adjacency proof, not a medieval route constraint.
        if len(options) == 1:
            return options[0]
        proven = [
            key for key in options
            if tuple(sorted((current, key))) in self.engine_proven_edges
        ]
        if len(proven) > 1:
            raise ValueError(
                f"reused RGB boundary has multiple engine-proven identities: "
                f"{current} -> {proven}"
            )
        if not proven:
            return None
        resolved = proven[0]
        return resolved

    def neighbors(self, key: str) -> frozenset[str]:
        cached = self.cache.get(key)
        if cached is not None:
            return cached
        value = self.coordinates[key]
        start = (round(value["x"]) % self.width, round(value["y"]))
        color = self.pixels[start]
        pending = deque([start])
        visited = {start}
        result: set[str] = set()
        while pending:
            x, y = pending.popleft()
            for nx, ny in (
                ((x - 1) % self.width, y),
                ((x + 1) % self.width, y),
                (x, y - 1),
                (x, y + 1),
            ):
                if ny < 0 or ny >= self.height:
                    continue
                adjacent_color = self.pixels[nx, ny]
                if adjacent_color == color:
                    point = (nx, ny)
                    if point not in visited:
                        visited.add(point)
                        pending.append(point)
                    continue
                neighbor = self.component_location(adjacent_color, nx, ny, key)
                pair = tuple(sorted((key, neighbor))) if neighbor else None
                if (
                    neighbor in self.controlled
                    and neighbor != key
                    and pair not in self.excluded_edges
                ):
                    result.add(neighbor)
        rendered = frozenset(result)
        self.cache[key] = rendered
        return rendered

    def shortest_path(self, origin: str, destination: str) -> list[str]:
        pending = deque([origin])
        previous: dict[str, str | None] = {origin: None}
        while pending:
            current = pending.popleft()
            if current == destination:
                break
            for neighbor in sorted(self.neighbors(current)):
                if neighbor not in previous:
                    previous[neighbor] = current
                    pending.append(neighbor)
        if destination not in previous:
            raise ValueError(f"no controlled-land topology path: {origin}-{destination}")
        path: list[str] = []
        current: str | None = destination
        while current is not None:
            path.append(current)
            current = previous[current]
        return list(reversed(path))


def expected() -> tuple[str, int, int]:
    controlled = {
        row["location"]
        for row in rows(OWNERSHIP)
        if row.get("location")
    }
    corridors = rows(CORRIDORS)
    if not corridors:
        raise ValueError("road corridor ledger is empty")
    exclusion_rows = rows(EXCLUSIONS)
    excluded_edges = frozenset(
        tuple(sorted((row["origin"].strip(), row["destination"].strip())))
        for row in exclusion_rows
    )
    if len(excluded_edges) != len(exclusion_rows):
        raise ValueError("road topology exclusions contain a duplicate edge")
    topology = Topology(controlled, excluded_edges)
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    edge_count = 0
    longest = 0
    for corridor in corridors:
        origin = corridor["origin"].strip()
        destination = corridor["destination"].strip()
        if origin not in controlled or destination not in controlled:
            raise ValueError(f"road endpoint is not under AD 1 control: {origin}-{destination}")
        path = topology.shortest_path(origin, destination)
        longest = max(longest, len(path) - 1)
        for step, (left, right) in enumerate(zip(path, path[1:]), start=1):
            if right not in topology.neighbors(left):
                raise ValueError(f"non-adjacent generated road step: {left}-{right}")
            writer.writerow({
                "corridor_origin": origin,
                "corridor_destination": destination,
                "step": step,
                "origin": left,
                "destination": right,
                "corridor": corridor["corridor"],
                "source": corridor["source"],
                "confidence": corridor["confidence"],
                "note": corridor["note"],
            })
            edge_count += 1
    return output.getvalue(), edge_count, longest


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        content, edges, longest = expected()
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"m5_road_topology: FAIL\n  - {exc}")
        return 1
    if args.write:
        OUTPUT.write_text(content, encoding="utf-8-sig", newline="")
    if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8-sig") != content:
        print("m5_road_topology: FAIL\n  - stale road_segments_topology.csv")
        return 1
    print(
        f"m5_road_topology: PASS ({len(rows(CORRIDORS))} cited corridors; "
        f"{edges} adjacent steps; longest {longest})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
