# S2 West Africa Granularity Verification — 28 July 2026

## Scope

This focused gate verifies the replacement of the disconnected West African
Iron-Age Societies placeholder. It does not claim runtime proof of long-term
AI balance and does not require an observer campaign.

## Deterministic evidence

- `tools/s2_west_africa_granularity.py --check` passes.
- Eight disjoint frames own exactly 24 locations: Kebbi River 7, Zamfara
  Plateau 5, Katsina Plain 4, Gobir Tarka 4, and four one-location
  Nsukka-Lejja, Lower Oueme, Volta-Cong, and Bosumtwi frames.
- The old WAF `guinea_region` and `sahel_region` residual selectors are absent.
- All eight frames have owned capitals, culture/religion profiles, one of
  three West African reforms, direct code-native standards, and localization
  in all eleven generated clients.
- The generated global census contains 315 playable polities and 23 remaining
  literal placeholder countries. No literal African placeholder remains.
- Full `gmake validate` passes all 115 checks.

## Runtime smoke

`gmake smoke` ran the paired control on 28 July 2026:

- Vanilla reached a responsive, rendered menu.
- ANTIQVITAS reached a responsive, rendered menu.
- Total paired duration was 198.5 seconds.
- The vanilla control contained four archived-baseline delta line types.
- None was unique to ANTIQVITAS.
- Result: PASS, zero mod-only normalized `error.log` lines.

## Judgment

PASS for this bounded map-and-systems tranche. The split removes a false
two-region superstate without substituting later Hausa, Ketu, Kong, Kumasi, or
Asante political identities. The remaining `mande_language` name-generator
fallback is explicitly documented as technical debt and not a historical
classification.
