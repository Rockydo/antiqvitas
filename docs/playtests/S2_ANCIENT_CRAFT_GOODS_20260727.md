# S2 Ancient Craft Goods — 27 July 2026

## Scope

This focused acceptance covers the first production-chain differentiation
tranche: twelve new processed goods, their direct art, pop demand, workshop
producers, and the first downstream shipyard inputs. It follows the reduced QA
rule: generated subsystem checks, one complete static regression, and one
paired-control smoke launch. No observer campaign was run.

## Content and economic contracts

- Added Fine Ceramics, Glasswares, Iron Hardware, Leather Goods, Cordage,
  Parchment, Lacquerware, Amber Ornaments, Glass Beads, Woven Carpets, Felt
  Goods, and Sailcloth.
- Rebound 27 historically named workshop families from generic pottery, glass,
  tools, leather, naval supplies, books, furniture, jewelry, or cloth outputs
  to the new finished goods.
- Shipyards now consume finished cordage and sailcloth alongside timber, tar,
  and iron.
- Every good has nonzero pop demand and at least one productive family. The
  active economy contains 77 reviewed goods, 265 buildings, 143 productive
  families, and 66 distinct recipe signatures.
- The regional-building validator independently prices every input and output
  from the pinned local engine plus the custom-good ledger. Every recipe remains
  within the required 19–21% default-price guild margin.

## Art

Two retained 1536×1024 six-up archaeological still-life atlases produce twelve
circle-safe RGBA masters, twelve 128×128 DXT5 icons, and twelve 1080×440 DXT5
illustrations. Source hashes, atlas geometry, cell mapping, retained masters,
texture uniqueness, and output presence are checked by
`tools/m5_ancient_goods_expansion.py`.

The dedicated contact sheet was visually reviewed: subjects are centered,
distinct at 128px, and contain no text, heraldry, people, modern equipment, or
medieval objects. The whole-project direct-art inventory rises from 880 to 892
chains across eight surfaces.

## Validation

- `m5_ancient_goods_expansion.py --check`: **PASS** — 12 goods from two pinned
  atlases.
- `generate_ancient_goods.py --check`: **PASS** — 25 custom goods, including 20
  processed goods, with eleven localization mirrors.
- `m5_goods_system_audit.py --check`: **PASS** — 77 active goods, 265 active
  buildings, 143 productive families.
- `m5_regional_buildings.py --check`: **PASS** — all 143 productive recipes
  satisfy the calibrated-margin contract.
- `m11_ui_asset_ledger.py --check`: **PASS** — 892 direct UI chains.
- `m12_anachronism_audit.py --check`: **PASS** — 61,886 player-facing English
  entries and zero prohibited terms.
- `make validate`: **PASS (103/103)**.

## Runtime smoke

The vanilla control and ANTIQVITAS each reached a responsive rendered menu.
Four archived-baseline delta types were present in the current vanilla control
and therefore excluded. Result: **PASS — zero mod-unique `error.log` lines**.

## Verdict

PASS. The tranche replaces conspicuous placeholder production identities with
real finished-goods chains and complete UI presentation. Broader raw-material,
food-processing, military-supply, and cross-system economic integration remain
open under S2-P2.
