# M8 institution-birth runtime verification — 2026-07-21

## Scope

Verify the custom institution-origin static-modifier contract exposed by the
first sustained AD 1 observer attempt.

## Procedure

1. Read the installed main-menu static-modifiers institutions file and its
   English localization. They establish the exact institution_birth modifier
   ID, location category, and STATIC_MODIFIER_NAME localization pattern.
2. Generated all nine M8 birth modifiers and their name/description entries
   from the single M8 institution manifest.
3. Ran full static validation and a 90-second enabled-mod smoke, both green
   with zero new error-log lines.
4. Started a fresh AD 1 observer session. The live frame is
   observer_start.png in docs/screens/M8_birth_modifiers_verified.

## Result

The fresh error log contains no missing static modifier for an ANTIQVITAS
institution and no missing STATIC_MODIFIER_NAME or STATIC_MODIFIER_DESC key for
an ANTIQVITAS institution birth modifier. The modifier contract is therefore a
runtime pass.

The session still reports the separately known vanilla coat-of-arms/HRE
fall-through for unset government and international-organization scopes. That
does not invalidate the resolved M8 birth-modifier contract and remains
separate runtime work.
