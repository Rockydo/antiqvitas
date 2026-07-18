# Blockers

## 2026-07-19 — Local documentation exporters do not complete

Status: fallback in use; does not block other M0 work.

The console and `helplog` are automated successfully. On the installed
1.3.1.1/Steam build 24187685, `script_docs` is listed as
`script_docs(script_documentation)`. Two clean attempts executed the command,
turned the render surface black, consumed roughly five CPU cores and 5 GiB
resident / 8.7 GiB private memory, but produced no file and did not return after
more than ten minutes. Earlier malformed-command diagnostics proved that the
console reports unknown commands immediately, so this is an exporter failure or
pathological runtime rather than a missing command.

`dump_data_types` was then entered exactly in a fresh process and showed the
same signature: console hidden, roughly five cores active, resident/private
memory stabilizing near 5/8.8 GiB, and no output flush during the bounded run.

Tried:

1. Virtual-key and physical scan-code console entry, with screenshot verification.
2. Fresh process, fixed window, exact AZERTY-safe command entry, and an extended
   monitored run. The process stayed responsive and memory-stable but never
   flushed output.
3. A separate fresh `dump_data_types` run with the exact raw virtual-key
   underscore mapping and three minutes of stable high-CPU processing.

Fallback: `docs/engine_docs/community_2025/` contains the MIT-licensed
GlossMod/EU5-Modding-Mcp dump at commit
`90790df9478a61035a2099c115b21ba7f04c3763` (2025-11-07). It predates build
1.3.1.1, so every effect/trigger used by the mod must additionally be confirmed
against current local scripts and smoke-tested. The local `helplog` command list
was harvested successfully as `docs/REF_console_commands.txt`.
