# M11 AD 476 finale illustration

The retained source is `assets_queue/generated_sources/antq_odoacer_finale_source.png`; the 1080x440 master is `assets_queue/generated/antq_odoacer_finale_1080x440.png`; the game-facing BC7 DDS is `main_menu/gfx/interface/illustrations/event/antq_odoacer_finale.dds`.

The text-free image is generic early-autumn northern-Italian lowland context: a slow side channel through reed beds and pale-gold meadow, scattered willow and poplar, shallow wet ground, distant blue-grey foothills, and a soft-clouded sky. It identifies no Odoacer, Romulus Augustulus, deposition, Rome, city, emperor, court, person, date, or outcome. It is not a reconstruction of the AD 476 finale.

`EVENT_IMAGES` in `tools/m10_final_century.py` owns `antq_m10_final.5012`. The inspected 1080x440 BC7 texture passed `make validate` and enabled-mod `make smoke` with zero new error-log lines. The generator now rejects any final-century current that lacks a reviewed image mapping.

Sources: ANTIQVITAS master plan sections 9, 17.5, and 20; local EU5 country-event image contract.
