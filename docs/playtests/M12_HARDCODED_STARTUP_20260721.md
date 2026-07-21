# M12 hardcoded startup compatibility - 2026-07-21

## Objective

Verify the exact-name overlay of the installed hardcoded on-game-start handler against the absent-IO and legacy-country runtime errors observed in AD 1.

## Contract

The renderer re-reads the installed handler and preserves it except for five safe scope operators around absent Catholic/Shinto IO references and dynamic date gates after 476.9.4 around eight China, Majapahit, Japan, Byzantium, Verona, Teutonic, and Bulgarian legacy startup blocks.

The campaign-end value is rendered from tools/dates.py. The generator rejects a source inventory mismatch, and the date validator exemption applies only to this exact re-rendered compatibility file.

## Automated verification

- Full make validate passed, including the source-overlay check.
- The enabled ANTIQVITAS playset completed a rendered 90-second smoke with zero new error-log lines.
- The driver reached the AD 1 selector, enabled Observer, and started a live map. Evidence: docs/screens/m12_hardcoded_probe/selector_loaded.png, docs/screens/m12_hardcoded_probe/observer_enabled.png, and docs/screens/m12_hardcoded_probe/observer_start.png.
- The resulting error log contains zero invalid international-organization event-target scopes, add-country-to-international-organization invalid scopes, hardcoded-handler source locations, and China/Majapahit/Byzantine startup-effect identifiers.

## Result

Pass for this compatibility surface. The earlier targeted generic startup errors are resolved. The same observer initialization still reports a separate vanilla coat-of-arms-template failure: it evaluates government_type and IO scopes on blank legacy countries. That independent contract remains open.
