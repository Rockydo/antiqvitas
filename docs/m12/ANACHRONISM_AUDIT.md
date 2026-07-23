# M12 authored-text anachronism audit

This generated audit enforces the plan's Appendix A anachronism sweep against
the player-facing text written by ANTIQVITAS. It reads English localization
values only; it deliberately does not inspect technical identifiers, comments,
or copied exact-name vanilla compatibility overlays. `tools/m11_localization.py`
separately proves the other supported language folders exactly mirror English.

## Checked inventory

- `main_menu/localization/english/antq_m10_final_century_l_english.yml`
- `main_menu/localization/english/antq_m10_first_century_l_english.yml`
- `main_menu/localization/english/antq_m10_fourth_century_l_english.yml`
- `main_menu/localization/english/antq_m10_second_century_l_english.yml`
- `main_menu/localization/english/antq_m10_third_century_l_english.yml`
- `main_menu/localization/english/antq_m11_decision_messages_l_english.yml`
- `main_menu/localization/english/antq_m11_decisions_l_english.yml`
- `main_menu/localization/english/antq_m11_flavor_phases_l_english.yml`
- `main_menu/localization/english/antq_m2_ages_l_english.yml`
- `main_menu/localization/english/antq_m3_countries_l_english.yml`
- `main_menu/localization/english/antq_m4_location_names_l_english.yml`
- `main_menu/localization/english/antq_m4_people_l_english.yml`
- `main_menu/localization/english/antq_m5_goods_l_english.yml`
- `main_menu/localization/english/antq_m5_regional_buildings_l_english.yml`
- `main_menu/localization/english/antq_m5_roman_buildings_l_english.yml`
- `main_menu/localization/english/antq_m6_power_l_english.yml`
- `main_menu/localization/english/antq_m7_war_l_english.yml`
- `main_menu/localization/english/antq_m8_knowledge_l_english.yml`
- `main_menu/localization/english/antq_m9_subjects_l_english.yml`

## Clear post-476 vocabulary

The prohibited vocabulary is deliberately narrow: `absolutism`, `absolutist`, `calvinism`, `calvinist`, `cannon`, `cannons`, `colonial`, `colonialism`, `colonies`, `colonist`, `colonization`, `colonize`, `colonized`, `crusade`, `crusader`, `factory`, `factories`, `habsburg`, `industrial`, `industrialization`, `lutheran`, `lutheranism`, `musket`, `muskets`, `napoleon`, `napoleonic`, `ottoman`, `pistol`, `pistols`, `protestant`, `protestantism`, `railroad`, `railroads`, `railway`, `railways`, `reformation`, `renaissance`, `rifle`, `rifles`, `safavid`, `steam engine`, `steam engines`, `steamship`, `steamships`, `united states`. Context-sensitive
words such as `empire`, `church`, and `feudal` are not blocked because a raw
word match would make unsupported historical assertions rather than improve
the audit.

## Result

19 English files and 5906 quoted player-facing entries contain
zero prohibited terms. The check is pinned in `make validate`; a newly authored
anachronism fails before it can reach a smoke run.
