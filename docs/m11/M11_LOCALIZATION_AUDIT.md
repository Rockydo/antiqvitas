# M11 localization audit

ANTIQVITAS v1.0 is English-first: the ten supported non-English clients must
receive English text rather than raw localization keys. The audit found no
`TODO`, `TBD`, placeholder, or lorem-ipsum string in the game-visible
localization tree.

The current contract has fifteen English source files mirrored exactly to
Brazilian Portuguese, French, German, Japanese, Korean, Polish, Russian,
Simplified Chinese, Spanish, and Turkish. Each mirror has the correct language
header and UTF-8 BOM; after normalizing that header, every file matches the
English source byte-for-byte in text. This includes the 328 M11 phase-event
notifications and all M2-M10 material.

`tools/m11_localization.py --check` now enforces that inventory, BOM/header
rule, exact English content mirror, and stub-free text on every `make validate`.
The task does not pretend to provide a translation; it preserves the plan's
explicit English-only scope reliably for all supported clients.
