# S2 population-summary and artillery resolver probe

Date: 26 July 2026  
Installed game: EU5 1.3.11, build 24187685  
Result: PASS

## Static installed-union proof

`tools/m12_ui_resolver_art.py --check` discovers and validates every installed
DDS whose filename belongs to the population-summary or artillery families:

- 30 artillery paths across category, text, battle, siege, modifier, button,
  advance, building, institution, reform, and wide unit/institution art;
- 19 population paths across location, growth, decline, alert, modifier, sort,
  resource, map-mode, button, and quarantined fallback art.

Every path has an exact mod mirror with the installed dimensions, DXT5 mip chain,
a non-vanilla hash, a pinned generated source, and reviewed alpha/safe-area
coverage. The complete visual review is
`docs/m12/ui_resolver_art_contact_sheet.png`; it contains no cannon, firearm,
Renaissance clothing, or clipped torsion engine.

## Focused live proof

A non-debug ANTIQVITAS launch resumed the fresh AD 1 autosave into live Observer
on 17 March AD 1. The driver right-clicked Roman territory, centered on the
capital, opened Roma's location context, selected **Population in Roma**, and
captured the actual Society/People panel:

- `docs/screens/S2_UI_RESOLVERS_20260726/roma_population_panel.png`

The panel displays the ancient population-growth group and the regional ancient
class portraits in the player-facing surface that previously exposed the vanilla
Renaissance couple. Germanic and Han views use these same global summary
textures; their class rows continue to resolve the separately validated regional
portrait sets, so repeated navigation would not exercise a different summary
asset.

No active ANTIQVITAS unit uses the engine `army_artillery` category, and all 311
installed legacy units are hidden or non-buildable. There is therefore no honest
recruitment row from which to capture the shared artillery category at present;
the exact 30-path mounted resolver census is the applicable proof rather than a
fabricated recruitable unit.

## Gates

- `make validate`: PASS, 93/93 checks.
- Paired vanilla/mod `make smoke`: PASS, zero mod-only `error.log` lines.
- Focused live Roma population panel: PASS.
