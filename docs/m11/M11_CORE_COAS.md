# M11 core emblem standards

`docs/m11/core_coas.csv` is the generated source ledger for the Rome, Han, and
Parthia country CoAs. `tools/generate_country_definitions.py` now validates that
each listed tag is in the AD 1 roster and that its `ce_*.dds` colored-emblem
texture exists in the locally installed EU5 asset catalogue before emitting it.
The generated CoAs use the engine's verified solid-pattern, named-colour,
colored-emblem, and positioned-instance contract.

Rome uses the locally installed generic eagle on a purple field, Han a generic
Chinese rosette on red, and Parthia a generic horse on deep red. They are
period-inspired UI standards selected under the master plan's emblem-on-field
design language, not reconstructions of historical flags, vexilla, court
banners, or state standards. They retain direct-country priority over the
regional standards subsequently documented in `M11_COA_STANDARDS.md`.

The generator, `make validate`, and enabled-mod `make smoke` passed with zero
new error-log lines.

Sources: ANTIQVITAS master plan sections 8.1-8.3 and 20; local installed EU5
CoA definitions and colored-emblem texture catalogue.
