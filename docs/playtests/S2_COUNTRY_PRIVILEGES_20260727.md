# S2 Country-Specific Privileges — 2026-07-27

## Scope

This rapid subsystem probe covers the first exact-country privilege tranche.
It does not substitute a long campaign for deterministic availability,
exclusivity, art, localization, and startup checks.

## Content

Six opening states receive two mutually exclusive privileges:

- Rome: Senatorial Fiscal Review / Equestrian Collection Concessions.
- Western Han: Court Remonstrance Access / Commandery Fiscal Discretion.
- Arsacid Parthia: Royal-Domain Review / Great-House Levy Exemptions.
- Xiongnu: Wing Gift Precedence / Pasture-Circuit Autonomy.
- Meroitic Kush: Royal Seal Inspection / Temple Storehouse Immunity.
- Anuradhapura: Reservoir Audit Grants / Monastic Endowment Immunity.

Every privilege uses an exact collision-safe `has_or_had_tag` potential gate.
Each paired alternative blocks the other through the locally verified
`allow = { NOT = { has_estate_privilege = ... } }` contract and retains the
engine's ordinary empty `can_revoke` block. Each has five effects drawn from
locally harvested modifier keys.

## Art

Two reviewed 3×2 archaeological still-life atlases were generated:

- `assets_queue/estate_orders/sources/major_privileges_west_atlas.png`
  (`82822073adad217060082ead7964cfa35ed9ac785cdddb2032f02009f3ea906f`)
- `assets_queue/estate_orders/sources/major_privileges_east_atlas.png`
  (`ec3f9e9429eb216c3c36bfe2dd958025e55f246449df4b672117475af6d499fd`)

The prompt family required a charcoal-navy field, centered isolated
archaeological objects, portrait-safe crops, and no people, modern display
furniture, text, pseudo-writing, heraldry, or medieval equipment. Visual review
confirmed the requested cell order and clean subject centering. The generator
then produced twelve unique 64×90 masters and twelve direct BC7 textures.

## Results

- `s2_estate_orders`: PASS — 13 profiles, 90 generated grants, 90 direct icons.
- `m6_power`: PASS — 136 total ancient privileges.
- `m8_knowledge`: PASS — 623 ancient-system unlocks and all 292 opening
  profiles researchable.
- `m11_privilege_icons`: PASS — 136/136 direct privilege icons.
- `m11_ui_asset_ledger`: PASS — 820 direct UI chains.
- `p4_manual_regression`: PASS — 20 symptoms and 27 mandatory validators.
- Full validation: PASS — 102/102 commands.
- Paired vanilla/mod smoke: PASS — both rendered responsive menus; zero
  mod-unique `error.log` line types.

The smoke is intentionally a menu/startup and log-diff probe under the reduced
QA policy; no extreme or multi-century observer run was performed.
