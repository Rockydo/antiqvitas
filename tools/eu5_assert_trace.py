#!/usr/bin/env python3
"""Trace the native caller of EU5's relation-to-self assertion.

This diagnostic attaches to the configured game-driver process, hooks the
non-mutating assertion-report sink, and records only stack addresses when the
specific ``Getting relation with itself`` message passes through it.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import frida

from runtime_state import directory as runtime_state_directory


ROOT = Path(__file__).resolve().parents[1]
STATE = runtime_state_directory(ROOT) / "gamedriver_session.json"
ASSERT_SINK_OFFSET = 0x370A900
RELATION_CALLER_OFFSET = 0x431C310
UNIT_MOVE_CALLER_OFFSET = 0x45CCE60
MESSAGE = "Getting relation with itself"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=float, default=360)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    state = json.loads(STATE.read_text(encoding="utf-8"))
    pid = int(state["pid"])
    session = frida.attach(pid)
    source = f"""
const module = Process.getModuleByName('eu5.exe');
const sink = module.base.add({ASSERT_SINK_OFFSET});
const relationCaller = module.base.add({RELATION_CALLER_OFFSET});
const unitMoveCaller = module.base.add({UNIT_MOVE_CALLER_OFFSET});
Interceptor.attach(unitMoveCaller, {{
  onEnter(args) {{
    try {{
      const actor = args[0].add(0x920).readS32();
      const targetOwner = args[2].add(0xb10).readS32();
      const targetLocation = args[2].add(0x20).readS32();
      if (actor !== targetOwner || targetLocation !== 15100) return;
      send({{
        own_location_candidate: true,
        country_id: actor,
        origin_location_id: args[1].add(0x20).readS32(),
        origin_owner_id: args[1].add(0xb10).readS32(),
        origin_controller_id: args[1].add(0xb18).readS32(),
        target_location_id: targetLocation,
        target_owner_id: targetOwner,
        target_controller_id: args[2].add(0xb18).readS32(),
        rule_flags: args[3].readByteArray(0x38)
      }});
    }} catch (_) {{}}
  }}
}});
Interceptor.attach(relationCaller, {{
  onEnter(args) {{
    let source = -1;
    let target = -2;
    try {{
      source = args[0].add(0x920).readS32();
      target = args[1].add(0xb10).readS32();
    }} catch (_) {{ return; }}
    if (source !== target) return;
    send({{
      relation_self: true,
      country_id: source,
      target_location_id: args[1].add(0x20).readS32(),
      target_controller_id: args[1].add(0xb18).readS32(),
      thread: this.threadId,
      stack: Thread.backtrace(this.context, Backtracer.ACCURATE)
        .map(address => DebugSymbol.fromAddress(address).toString())
    }});
  }}
}});
Interceptor.attach(sink, {{
  onEnter(args) {{
    let value = '';
    try {{ value = args[0].readUtf8String(); }} catch (_) {{ return; }}
    if (value !== {json.dumps(MESSAGE)}) return;
    send({{
      message: value,
      thread: this.threadId,
      module_base: module.base.toString(),
      stack: Thread.backtrace(this.context, Backtracer.ACCURATE)
        .map(address => DebugSymbol.fromAddress(address).toString())
    }});
  }}
}});
send({{ready: true, pid: Process.id, module_base: module.base.toString(), sink: sink.toString()}});
"""
    records: list[dict[str, object]] = []

    def on_message(message: dict[str, object], _data: bytes | None) -> None:
        records.append(message)
        print(json.dumps(message), flush=True)

    script = session.create_script(source)
    script.on("message", on_message)
    script.load()
    deadline = time.monotonic() + args.timeout
    try:
        while time.monotonic() < deadline and session.is_detached is False:
            time.sleep(0.25)
            if any(
                item.get("type") == "send"
                and isinstance(item.get("payload"), dict)
                and item["payload"].get("message") == MESSAGE
                for item in records
            ):
                break
    finally:
        if not session.is_detached:
            session.detach()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    return 0 if any(
        item.get("type") == "send"
        and isinstance(item.get("payload"), dict)
        and item["payload"].get("message") == MESSAGE
        for item in records
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
