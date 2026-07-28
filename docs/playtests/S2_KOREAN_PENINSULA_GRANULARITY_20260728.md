# Korean peninsula granularity smoke - 2026-07-28

- `make validate`: PASS, 129/129 commands.
- Confirming `make smoke`: PASS; vanilla and mod menus rendered and remained
  responsive.
- Normalized mod-only `error.log` delta: zero new lines.
- World contract: 450 polities; 13,549 controlled/populated locations; nine
  remaining placeholders.
- Focus: `KRS` absent; 50 former fields and 16 erroneous Hoseo assignments are
  pinned by the permanent validator.
- Lelang contract: Han owns all 14 commandery fields while exact population
  overrides preserve their indigenous-majority culture and faith.
- The first paired run logged one nondeterministic global `AudioArena` allocator
  line; it did not recur, and this batch touches no audio.
