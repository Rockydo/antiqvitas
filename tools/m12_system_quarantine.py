#!/usr/bin/env python3
"""Exact-mirror quarantine for mounted post-antique political systems.

EU5 merges definition registries by filename.  A total conversion therefore
cannot remove vanilla privileges, cabinet actions, parliament content, laws,
or reforms with a single late-loading file: every mounted source filename must
be mirrored.  This generator preserves every installed key for script
resolution, but makes each installed definition permanently unavailable
through its native ``potential`` gate.  ANTIQVITAS definitions live in
separate namespaced files and remain available.

The same pass disables installed country interactions, generic actions, and
disasters whose availability predicates dereference medieval organizations,
characters, or dynasties even when their visible content is otherwise hidden.
The one annual HRE pulse is guarded because EU5 1.3.11 evaluates it even though
the AD 1 setup has no HRE.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from legacy_institutions import neutralize_references


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
MANIFEST = ROOT / "docs/m12/system_quarantine_manifest.json"

SURFACES = {
    "estate_privileges": ("in_game/common/estate_privileges", "potential"),
    "cabinet_actions": ("in_game/common/cabinet_actions", "potential"),
    "parliament_issues": ("in_game/common/parliament_issues", "potential"),
    "parliament_agendas": ("in_game/common/parliament_agendas", "potential"),
    "laws": ("in_game/common/laws", "potential"),
    "government_reforms": ("in_game/common/government_reforms", "potential"),
    "country_interactions": ("in_game/common/country_interactions", "potential"),
    "disasters": ("in_game/common/disasters", "can_start"),
    "formable_countries": ("in_game/common/formable_countries", "potential"),
    # Religious aspects use `visible`, not `potential`, as their registry gate.
    "religious_aspects": ("in_game/common/religious_aspects", "visible"),
}
TARGETED_QUARANTINES = {
    "hre_generic_actions": (
        "in_game/common/generic_actions/hre_circle_actions.txt",
        "potential",
    ),
}
EXCLUDED_BY_SURFACE = {
    # This exact file is jointly neutralized for legacy institution references
    # by m8_legacy_institution_purge.py.
    "disasters": {"revolution_disaster.txt"},
}
YEARLY_ON_ACTION = "in_game/common/on_action/country_yearly.txt"
TOP_LEVEL = re.compile(r"^\s*[A-Za-z_][A-Za-z0-9_]*\s*=\s*\{")
TOP_LEVEL_KEY = re.compile(r"^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*\{")
HRE_YEARLY_LINK = "\t\tinternational_organization:hre = { circles_are_active = yes }"
HRE_YEARLY_GUARD = "\t\tinternational_organization:hre ?= { circles_are_active = yes }"
MARKER = "ANTIQVITAS mounted-system quarantine"
RETAINED_ENGINE_ADAPTERS = {
    # EU5's bookmark initializer requires this category for countries with a
    # succession law. False-gating it produces "has no heir_religion_law"
    # for the roster and can suppress the law UI. Its player-facing text is
    # ancientized separately; retaining the category is an engine contract.
    "laws": {"heir_religion_law"},
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def game_root() -> Path:
    data = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
    return Path(str(data["game_dir"])) / "game"


def mounted_files(relative: str) -> dict[str, Path]:
    """Return the effective base+DLC filename union for one registry."""
    game = game_root()
    rel = Path(relative)
    roots = [game / rel]
    roots.extend(
        package / rel
        for package in sorted((game / "dlc").glob("*"))
        if package.is_dir()
    )
    mounted: dict[str, Path] = {}
    for directory in roots:
        if not directory.is_dir():
            continue
        for source in sorted(directory.rglob("*.txt")):
            mounted[source.relative_to(directory).as_posix()] = source
    return mounted


def structural_code(line: str) -> str:
    """Remove comments/quoted payload while preserving structural spacing."""
    rendered: list[str] = []
    quoted = False
    escaped = False
    for char in line:
        if escaped:
            rendered.append(" " if quoted else char)
            escaped = False
            continue
        if char == "\\" and quoted:
            rendered.append(" ")
            escaped = True
            continue
        if char == '"':
            quoted = not quoted
            rendered.append(" ")
            continue
        if char == "#" and not quoted:
            break
        rendered.append(" " if quoted else char)
    return "".join(rendered)


def brace_delta(line: str) -> int:
    code = structural_code(line)
    return code.count("{") - code.count("}")


def normalize_generated_script(text: str) -> str:
    """Remove installed whitespace defects without changing script tokens."""
    normalized: list[str] = []
    for line in text.splitlines():
        line = line.rstrip()
        prefix = line[: len(line) - len(line.lstrip(" \t"))]
        if " \t" in prefix:
            columns = len(prefix.expandtabs(4))
            tabs, spaces = divmod(columns, 4)
            line = "\t" * tabs + " " * spaces + line[len(prefix):]
        normalized.append(line)
    while normalized and not normalized[-1]:
        normalized.pop()
    return "\n".join(normalized) + "\n"


def inject_inline_false(line: str) -> str:
    code, marker, comment = line.partition("#")
    closing = code.rfind("}")
    if closing < 0:
        raise ValueError(f"expected an inline trigger block: {line!r}")
    suffix = f" {marker}{comment}" if marker else ""
    return (
        code[:closing]
        + "always = no "
        + code[closing:]
        + f" # {MARKER}"
        + suffix
    )


def guard_absent_legacy_objects(text: str, gate_name: str) -> str:
    """Make missing installed database objects optional inside retained bodies."""
    guarded: list[str] = []
    optional_scope = re.compile(
        r"(?P<link>(?:international_organization|character|dynasty):"
        r"[A-Za-z0-9_]+)\s*=\s*\{"
    )
    rhs_object = re.compile(
        r"(?:!=|\?=|(?<![?!<>])=)\s*(?:character|dynasty):[A-Za-z0-9_]+"
    )
    unsafe_dynamic_rhs = re.compile(
        r"(?:!=|\?=|(?<![?!<>])=)\s*"
        r"(?:root\.)?(?:ruler|heir|ruler_or_heir_if_regent)"
        r"(?:\.[A-Za-z_][A-Za-z0-9_]*)+"
    )
    optional_runtime_scope = re.compile(
        r"(?<![?.A-Za-z0-9_])"
        r"(?P<link>ruler|heir|ruler_or_heir_if_regent)"
        r"\s*=\s*\{"
    )
    optional_runtime_comparison = re.compile(
        r"(?<![?.A-Za-z0-9_])"
        r"(?P<link>government_type)\s*=\s*"
    )
    gate = re.compile(rf"^\s*{re.escape(gate_name)}\s*=\s*\{{")
    depth = 0
    trigger_depth: int | None = None
    for line in text.splitlines():
        code = structural_code(line)
        delta = brace_delta(line)
        updated = optional_scope.sub(r"\g<link> ?= {", line)
        updated = re.sub(
            r"\bcapital\.market\s*=\s*\{",
            "capital.market ?= {",
            updated,
        )
        # Disabled registry bodies are still type-checked and some nested
        # policy/allow predicates are evaluated by the UI. Make nullable
        # runtime links safe throughout the quarantined definition, not only
        # in its outer availability gate.
        updated = optional_runtime_scope.sub(r"\g<link> ?= {", updated)
        updated = optional_runtime_comparison.sub(
            r"\g<link> ?= ",
            updated,
        )
        if trigger_depth is not None and (
            rhs_object.search(structural_code(updated))
            or unsafe_dynamic_rhs.search(structural_code(updated))
        ):
            if brace_delta(updated) != 0:
                raise ValueError(
                    f"unsupported multiline legacy-object comparison: {line!r}"
                )
            indent = updated[: len(updated) - len(updated.lstrip())]
            updated = (
                f"{indent}always = no "
                "# ANTIQVITAS absent legacy object comparison"
            )
        guarded.append(updated)
        previous_depth = depth
        depth += delta
        if (
            trigger_depth is None
            and gate.match(code)
            and delta > 0
        ):
            trigger_depth = previous_depth
        elif trigger_depth is not None and depth == trigger_depth:
            trigger_depth = None
    return "\n".join(guarded) + "\n"


def render_quarantine(
    source: Path,
    surface: str,
    gate_name: str = "potential",
) -> tuple[bytes, int]:
    """False-gate every top-level definition while preserving its body."""
    raw = source.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    rendered = [
        f"# Generated by tools/m12_system_quarantine.py --write ({surface}).",
        f"# Installed source SHA256: {sha256(raw)}",
        "# Definitions stay resolvable but cannot enter AD 1 gameplay.",
    ]
    depth = 0
    root_open = False
    root_has_gate = False
    root_retained = False
    definitions = 0
    retained_definitions = 0
    gate = re.compile(rf"^\s*{re.escape(gate_name)}\s*=\s*\{{")

    for line in text.splitlines():
        code = structural_code(line)
        delta = brace_delta(line)
        top_level = TOP_LEVEL_KEY.match(code)
        if depth == 0 and top_level:
            if delta <= 0:
                raise ValueError(
                    f"{source.name}: unsupported one-line top-level definition"
                )
            definitions += 1
            root_open = True
            root_has_gate = False
            root_retained = top_level.group("key") in RETAINED_ENGINE_ADAPTERS.get(surface, set())
            if root_retained:
                retained_definitions += 1
            rendered.append(line.rstrip())
            depth += delta
            continue
        if root_open and not root_retained and depth == 1 and gate.match(code):
            if delta == 0:
                rendered.append(inject_inline_false(line.rstrip()))
            else:
                rendered.append(line.rstrip())
                source_indent = code[: len(code) - len(code.lstrip())]
                indent_level = max(
                    1,
                    (len(source_indent.expandtabs(4)) + 3) // 4,
                )
                child_indent = "\t" * (indent_level + 1)
                rendered.append(f"{child_indent}always = no # {MARKER}")
            root_has_gate = True
            depth += delta
            continue
        if root_open and not root_retained and depth == 1 and delta < 0 and not root_has_gate:
            rendered.append(f"\t{gate_name} = {{ always = no }} # {MARKER}")
            root_has_gate = True
        rendered.append(line.rstrip())
        depth += delta
        if root_open and depth == 0:
            root_open = False

    if depth != 0 or root_open:
        raise ValueError(f"{source.name}: unbalanced source while quarantining")
    if definitions == 0:
        raise ValueError(f"{source.name}: no top-level definitions")
    quarantined = guard_absent_legacy_objects(
        "\n".join(rendered) + "\n",
        gate_name,
    )
    quarantined = neutralize_references(
        quarantined,
        remap_effects=True,
    )
    quarantined = normalize_generated_script(quarantined)
    output = quarantined.encode(
        "utf-8-sig" if has_bom else "utf-8"
    )
    guarded_definitions = definitions - retained_definitions
    if output.decode("utf-8-sig").count(MARKER) != guarded_definitions:
        raise ValueError(f"{source.name}: quarantine marker count drift")
    return output, guarded_definitions


def render_yearly_guard(source: Path) -> bytes:
    raw = source.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    if text.count(HRE_YEARLY_LINK) != 1:
        raise ValueError(
            "installed country_yearly.txt no longer has the expected HRE pulse link"
        )
    guarded = normalize_generated_script(
        text.replace(HRE_YEARLY_LINK, HRE_YEARLY_GUARD)
    )
    header = (
        "# Generated by tools/m12_system_quarantine.py --write.\n"
        f"# Installed source SHA256: {sha256(raw)}\n"
        "# The AD 1 setup has no HRE; its optional scope must fail quietly.\n"
    )
    output = (header + guarded).encode("utf-8-sig" if has_bom else "utf-8")
    return output


def expected_outputs() -> tuple[dict[Path, bytes], dict[str, object]]:
    outputs: dict[Path, bytes] = {}
    records: list[dict[str, object]] = []
    totals: dict[str, int] = {}

    for surface, (relative, gate_name) in SURFACES.items():
        sources = mounted_files(relative)
        definitions = 0
        for name, source in sorted(sources.items()):
            # Registry readmes contain examples, not mounted definitions.
            if name.casefold() == "readme.txt":
                continue
            if name in EXCLUDED_BY_SURFACE.get(surface, set()):
                continue
            source_text = source.read_text(encoding="utf-8-sig")
            if not any(
                TOP_LEVEL.match(structural_code(line))
                for line in source_text.splitlines()
            ):
                continue
            output = ROOT / relative / name
            payload, count = render_quarantine(source, surface, gate_name)
            outputs[output] = payload
            definitions += count
            records.append(
                {
                    "surface": surface,
                    "relative": name,
                    "source": str(source),
                    "source_sha256": sha256(source.read_bytes()),
                    "definition_count": count,
                    "output": output.relative_to(ROOT).as_posix(),
                    "output_sha256": sha256(payload),
                }
            )
        totals[surface] = definitions

    for surface, (relative, gate_name) in TARGETED_QUARANTINES.items():
        source = game_root() / relative
        output = ROOT / relative
        payload, count = render_quarantine(source, surface, gate_name)
        outputs[output] = payload
        records.append(
            {
                "surface": surface,
                "relative": Path(relative).name,
                "source": str(source),
                "source_sha256": sha256(source.read_bytes()),
                "definition_count": count,
                "output": output.relative_to(ROOT).as_posix(),
                "output_sha256": sha256(payload),
            }
        )
        totals[surface] = count

    yearly_source = game_root() / YEARLY_ON_ACTION
    yearly_output = ROOT / YEARLY_ON_ACTION
    yearly_payload = render_yearly_guard(yearly_source)
    outputs[yearly_output] = yearly_payload
    records.append(
        {
            "surface": "hre_yearly_scope_guard",
            "relative": "country_yearly.txt",
            "source": str(yearly_source),
            "source_sha256": sha256(yearly_source.read_bytes()),
            "definition_count": 1,
            "output": yearly_output.relative_to(ROOT).as_posix(),
            "output_sha256": sha256(yearly_payload),
        }
    )
    totals["hre_yearly_scope_guard"] = 1

    manifest = {
        "schema": 1,
        "policy": (
            "Preserve installed keys for reference resolution; false-gate every "
            "mounted post-antique definition, retain required engine adapters, "
            "and guard the HRE yearly pulse."
        ),
        "totals": totals,
        "files": records,
    }
    return outputs, manifest


def write() -> None:
    outputs, manifest = expected_outputs()
    previous: set[Path] = set()
    if MANIFEST.is_file():
        old = json.loads(MANIFEST.read_text(encoding="utf-8"))
        previous = {ROOT / str(record["output"]) for record in old.get("files", [])}
    for stale in sorted(previous - set(outputs)):
        if stale.is_file():
            stale.unlink()
    for output, payload in sorted(outputs.items()):
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(payload)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        "m12_system_quarantine: wrote "
        f"{len(outputs)} exact mirrors / "
        f"{sum(manifest['totals'].values())} guarded definitions"
    )


def check() -> bool:
    try:
        outputs, manifest = expected_outputs()
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"m12_system_quarantine: FAIL\n  - {exc}")
        return False
    errors: list[str] = []
    for output, payload in sorted(outputs.items()):
        if not output.is_file() or output.read_bytes() != payload:
            errors.append(f"stale or missing {output.relative_to(ROOT)}")
    expected_manifest = json.dumps(
        manifest, indent=2, ensure_ascii=False
    ) + "\n"
    if (
        not MANIFEST.is_file()
        or MANIFEST.read_text(encoding="utf-8") != expected_manifest
    ):
        errors.append(f"stale or missing {MANIFEST.relative_to(ROOT)}")
    if errors:
        print("m12_system_quarantine: FAIL")
        for error in errors[:30]:
            print(f"  - {error}")
        if len(errors) > 30:
            print(f"  - ... {len(errors) - 30} more")
        return False
    totals = manifest["totals"]
    print(
        "m12_system_quarantine: PASS "
        f"({len(outputs)} mirrors; "
        f"{sum(totals.values())} guarded definitions)"
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        try:
            write()
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
            print(f"m12_system_quarantine: FAIL\n  - {exc}")
            return 1
        return 0
    return 0 if check() else 1


if __name__ == "__main__":
    raise SystemExit(main())
