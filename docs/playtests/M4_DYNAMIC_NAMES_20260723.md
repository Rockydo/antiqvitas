# M4 exact Italian dynamic-name probe - 2026-07-23

## Scope

This rapid subsystem gate covers nine additional Pleiades-backed Italian
settlement labels: Ancona, Bellunum, Caesena, Consentia, Cremona, Matera,
Parma, Tarvisium, and Verona. Each has a direct active-at-AD-1 settlement point
and an installed location-key review in `docs/m4/ROMAN_TOPONYM_EXPANSION.md`.

## Static gate

`gmake validate` passed. The dynamic-name renderer reports 61
coordinate-verified capital anchors plus 105 curated direct anchors across all
eleven supported localization clients. The M12 audit was regenerated after the
additional localization entries and passed with zero prohibited terms.

## Menu smoke

The bounded `gmake smoke` control launched vanilla to the menu, then launched
the enabled ANTIQVITAS playset to the menu. Its normalized comparison reported:

`smoketest: PASS (zero new lines; 0 baseline line types absent)`

No observer chronology was run: this is a display-name-only generated-localization
change, so the project testing policy calls for static generation checks and a
short menu/log comparison.
