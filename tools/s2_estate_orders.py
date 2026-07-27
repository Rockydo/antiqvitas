#!/usr/bin/env python3
"""Render and audit polity-aware ancient estate identities and privileges."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image

from dates import M2_MIRROR_LANGUAGES
from dds import identify

ROOT = Path(__file__).resolve().parents[1]
PATHS = ROOT / "config/local_paths.json"
SOURCES = ROOT / "assets_queue/estate_orders/sources"
GENERATED_SOURCES = ROOT / "assets_queue/generated_sources"
MASTERS = ROOT / "assets_queue/generated"
DDS_TOOL = ROOT / "tools/dds.py"
CONTENT_LEDGER = ROOT / "docs/m6/estate_order_privileges.csv"
ART_LEDGER = ROOT / "docs/m6/estate_order_art.csv"
CUSTOM_LOC_OUT = ROOT / "in_game/common/customizable_localization/estates.txt"
BASE_CUSTOM_LOC_HASH = "5c91728a9faf2d3f656e15e7321aa3240bf90b14deea49b73ab688ddda420575"
ESTATES = ("crown_estate", "nobles_estate", "clergy_estate", "burghers_estate", "peasants_estate", "tribes_estate")

# profile|reforms|atlas|hash|sources|confidence|evidence boundary|six displayed order names
PROFILE_DATA = r"""
roman|antq_principate~antq_dominate~antq_augustan_dyarchy~antq_provincial_principate|roman_orders_atlas.png|e68c0ea154a1aed7cc33e62febf23601128929cdf72d46b61c5f624d3d01dd12|P8.1;P11;P13;OCD|secure|Orders are engine participation categories; they do not make the Augustan orders equal corporate estates or the Senate a sovereign legislature.|Imperial Household~Senatorial Order~Public Priesthoods~Equestrians and Civic Elites~Citizens and Provincials~Allied Communities
han|antq_han_imperial_bureaucracy~antq_memorialist_han_court~antq_commandery_supervision|han_orders_atlas.png|790add7428c58d7934c5d30264f3583088ec63c5d62e0abd40495f72972816fe|P8.3;P13;BHR;CTP-WM|secure|The categories distinguish court, ritual, registered household, workshop, and exchange interests without imposing European estates on Han institutions.|Imperial House~Court and Great Families~Ritual and Scholarly Officials~Artisans and Merchants~Registered Households~Frontier Communities
iranian|antq_parthian_king_of_kings~antq_parthian_subkingdom~antq_indo_scythian_kingship~antq_sassanid_centralized_monarchy~antq_iranian_great_house_reform~antq_iranian_royal_domain|iranian_orders_atlas.png|8a7927087431399bc0144d1b7e80cfa7b47dfca58e314f0dd539e15a3fa10afd|P8.2;P13;CAH-XI;OCD|secure|The profile models negotiated royal, great-house, cult, caravan, and cultivating interests without asserting one written Arsacid constitution.|Royal House~Great Houses~Temple Networks~Caravan and Urban Houses~Cultivating Communities~Mounted Clans
civic|antq_indo_greek_kingship~antq_settled_town_cluster~antq_boule_magistracy~antq_federal_synedrion|civic_orders_atlas.png|351cbbb537ff56a943566973db2f9edc1cc33628a932b71fc84b6738ec882275|P8.2;P8.5;P11;P13;OCD|secure|The civic profile covers related council, sanctuary, harbor, guild, and household functions without claiming identical constitutions or citizen bodies.|Civic Magistracies~Leading Houses~Sanctuary Custodians~Guilds and Traders~Citizen and Rural Households~Dependent Communities
gana|antq_indian_ganasangha~antq_lineage_rotation~antq_gana_muster_confederacy|gana_orders_atlas.png|512fa08d4a70e66a54c56216f7b1e996579f6862f6a9a684a10ed1afc8279d8c|P8.5;P11;P13;CAH-XI|contested|Clan delegates and assembly offices are bounded gameplay categories; participation, hierarchy, and procedure varied and are incompletely recoverable.|Assembly Magistrates~Clan Delegates~Shrines and Renunciant Houses~Guilds and Caravans~Cultivating Households~Confederated Clans
steppe|antq_steppe_confederation~antq_steppe_wing_confederacy~antq_steppe_gift_court|steppe_orders_atlas.png|173a0512bfd691e9acd21d61c7b9798f343b72e227bea272ad3cf2aaf66cb7c2|P8.6;P8.7;P13;CAH-XI|contested|The engine orders proxy ruling lineages, retinues, ritual custodians, brokers, and herding households without treating all Inner Asian societies as one polity.|Ruling Lineage~Leading Retinues~Ritual Custodians~Caravan Brokers~Herding Households~Confederated Clans
tribal|antq_advanced_chiefdom~antq_tribal_kingdom~antq_elder_moot_kingship~antq_warband_retinue_kingship|tribal_orders_atlas.png|9aa72377a282f3652e13b9fd7ee5bf6b9558256b149172dffcc37e6fc0206a8c|P8.7;P11;P13;CAH-XI|contested|This broad fallback exposes differentiated assembly, retinue, ritual, exchange, and household interests while retaining the need for later regional subdivision.|Leading House~Household Retinues~Sacred Custodians~Exchange Households~Free Cultivators~Kindreds and Clans
sacral|antq_lankan_kingdom~antq_kushite_dual_kingship~antq_temple_endowment_court~antq_irrigation_palace|sacral_orders_atlas.png|60c182e94e8f921acf2f533baafd8f25ebb89a31f80a7e1d8f013c12fb7c063d|P8.4;P8.5;P11;P13;BHR|contested|The profile translates different Lankan and northeast-African court-temple relationships into one engine floor without claiming shared theology or administration.|Consecrated Royal House~Court Lineages~Temple and Monastic Networks~Market and Artisan Houses~Irrigation and Cultivating Households~Frontier Communities
royal|antq_client_monarchy~antq_buffer_kingdom~antq_early_korean_kingdom~antq_regional_kingship~antq_petition_court~antq_frontier_muster_monarchy|royal_orders_atlas.png|03c5d29d261c2c10792377defa0d4ba5840e6f0427daeaa29f2c0b29a11852cd|P8.2;P8.3;P8.4;P8.5;P11;P13;CAH-XI|contested|The royal profile is a regional floor for incomplete evidence; it does not assert common titulature, succession, court offices, or tribute systems.|Royal Household~Dynastic and Regional Elites~Cult and Sanctuary Networks~Town and Caravan Houses~Rural Households~Frontier and Clan Communities
""".strip()

# profile|slug|estate|display name|description
PRIVILEGE_DATA = r"""
roman|senatorial_commissions|nobles_estate|Senatorial Commissions|Recognized senatorial commissions scrutinize provincial accounts and public obligations while preserving the princeps' final authority.
roman|provincial_land_surveys|nobles_estate|Provincial Land Surveys|Elite landholders support surveyed boundaries and assessed estates in return for predictable fiscal treatment and stronger local influence.
roman|collegial_cult_stipends|clergy_estate|Collegial Cult Stipends|Public priestly colleges receive protected stipends for calendars, vows, auspices, and the custody of civic ritual equipment.
roman|equestrian_public_contracts|burghers_estate|Equestrian Public Contracts|Equestrian contractors receive stable terms for transport, tax collection, supplies, and other bounded public undertakings.
roman|recognized_collegia|burghers_estate|Recognized Collegia|Selected craft, burial, and neighborhood associations gain legal recognition while accepting registration and public-service obligations.
roman|petition_and_census_guarantees|peasants_estate|Petition and Census Guarantees|Citizens and provincials receive regular petition channels and predictable census obligations at the cost of slower coercive extraction.
han|palace_memorial_access|nobles_estate|Palace Memorial Access|Court and great families retain regulated channels for authenticated memorials, appointments, and review of commandery reports.
han|registered_estate_returns|nobles_estate|Registered Estate Returns|Powerful households submit land and dependent-household returns in exchange for predictable assessment and recognized status.
han|calendar_and_ritual_consultation|clergy_estate|Calendar and Ritual Consultation|Ritual and scholarly officials receive a formal hearing on calendars, court rites, omens, and the language of imperial measures.
han|commandery_workshop_quotas|burghers_estate|Commandery Workshop Quotas|Registered workshops receive material allotments and stable quotas while their managers accept inspection and production obligations.
han|licensed_long_distance_trade|burghers_estate|Licensed Long-Distance Trade|Merchant households gain licensed routes and protected markets in return for tallies, duties, and scrutiny of bulk movement.
han|predictable_corvee_rotations|peasants_estate|Predictable Corvée Rotations|Registered households receive seasonal limits and rotation rules for labor service, reducing disruption while constraining immediate mobilization.
iranian|great_house_counsel|nobles_estate|Great-House Counsel|Leading houses receive a recognized place in dynastic arbitration and regional consultation while retaining costly political leverage.
iranian|mounted_host_compacts|nobles_estate|Mounted-Host Compacts|Great houses specify mounted followings, equipment, and seasons of service in return for wider command and local autonomy.
iranian|temple_endowment_registers|clergy_estate|Temple Endowment Registers|Temple networks receive protected endowments and inventories while acknowledging royal arbitration over contested grants.
iranian|caravan_toll_compacts|burghers_estate|Caravan Toll Compacts|Urban and caravan houses receive stable toll schedules and recognized weighing practices at the cost of reduced discretionary revenue.
iranian|safe_conduct_guarantees|burghers_estate|Safe-Conduct Guarantees|Merchants gain enforceable escorts and compensation procedures while accepting route registration and royal oversight.
iranian|irrigation_labor_compacts|peasants_estate|Irrigation Labor Compacts|Cultivating communities receive scheduled water and maintenance obligations instead of unlimited demands by local powers.
civic|magistrate_accountability|nobles_estate|Magistrate Accountability|Leading houses accept audited terms, recorded handovers, and council scrutiny in return for secure eligibility for civic office.
civic|euergetic_public_works|nobles_estate|Civic Benefaction Compacts|Wealthy households fund bounded public works and festivals in exchange for honors and a stronger voice in civic priorities.
civic|sanctuary_inventory_rights|clergy_estate|Sanctuary Inventory Rights|Sanctuary custodians retain protected inventories and revenues while accepting civic review of public endowments.
civic|harbor_dues_farming|burghers_estate|Harbor-Dues Farming|Merchant groups receive predictable harbor collection contracts while surrendering part of the city's immediate fiscal flexibility.
civic|recognized_craft_associations|burghers_estate|Recognized Craft Associations|Craft associations gain arbitration and mutual-aid rights in exchange for registered measures, service, and production standards.
civic|grain_and_water_guarantees|peasants_estate|Grain and Water Guarantees|Citizen and rural households receive protected access to civic grain and water systems while accepting maintenance duties.
gana|clan_delegate_rotation|nobles_estate|Clan Delegate Rotation|Recognized clans rotate delegates through the assembly, widening consultation while slowing concentrated executive action.
gana|warrior_household_service|nobles_estate|Warrior-Household Service|Leading warrior households provide equipment and retainers under negotiated quotas rather than an unlimited royal levy.
gana|shrine_hospitality_endowments|clergy_estate|Shrine Hospitality Endowments|Shrines and renunciant houses receive bounded support for hospitality without becoming a single centralized clergy.
gana|road_hospitality_compacts|burghers_estate|Road Hospitality Compacts|Caravan and guild households maintain wells, shelters, and animal facilities in exchange for protected passage and fees.
gana|guild_arbitration_rights|burghers_estate|Guild Arbitration Rights|Recognized craft and merchant bodies arbitrate internal disputes while accepting assembly review in external cases.
gana|communal_granary_shares|peasants_estate|Communal Granary Shares|Cultivating households contribute measured shares to local stores and receive bounded release rights during scarcity.
steppe|wing_council_precedence|nobles_estate|Wing-Council Precedence|Leading retinues receive an ordered place in wing councils and gift distributions, increasing cohesion but constraining the ruler.
steppe|mounted_retinue_quotas|tribes_estate|Mounted-Retinue Quotas|Confederated clans state remount, bow, and retainer quotas in return for negotiated pasture and campaign expectations.
steppe|cauldron_and_rite_custody|clergy_estate|Rite-Custody Grants|Ritual custodians receive protected vessels and offerings without implying one uniform steppe priesthood or rite.
steppe|seasonal_pasture_circuits|tribes_estate|Seasonal Pasture Circuits|Clan circuits receive recognized grazing and watering sequences at the cost of central freedom to redirect herds.
steppe|gift_circulation_obligations|burghers_estate|Gift-Circulation Obligations|Caravan brokers organize cloth, fittings, livestock, and diplomatic gifts while gaining influence over exchange routes.
steppe|herding_household_remounts|peasants_estate|Herding-Household Remounts|Herding households supply measured remounts and products under predictable quotas instead of open-ended requisition.
tribal|elder_assembly_hearing|tribes_estate|Elder Assembly Hearing|Kindreds and leading households receive a regular hearing before major levies, migrations, settlements, or external compacts.
tribal|household_retinue_gifts|nobles_estate|Household-Retinue Gifts|Leading retinues receive arms and prestige goods while accepting explicit service and hospitality obligations.
tribal|grove_custodianship|clergy_estate|Sacred-Place Custodianship|Local ritual custodians receive protected offerings and access without inventing a uniform priesthood or sacred landscape.
tribal|seasonal_cattle_compacts|tribes_estate|Seasonal Cattle Compacts|Kindreds receive recognized grazing, watering, and restitution customs at the cost of stronger central direction.
tribal|river_exchange_protection|burghers_estate|River-Exchange Protection|Exchange households gain protected landing places, measures, and escorts while accumulating influence over scarce imports.
tribal|free_household_muster|peasants_estate|Free-Household Muster|Free cultivating households accept bounded muster and provisioning duties in return for limits on arbitrary extraction.
sacral|treasury_seal_custody|nobles_estate|Treasury Seal Custody|Court lineages share witnessed custody of selected treasury seals and measures, improving accountability while increasing elite leverage.
sacral|granary_endowments|clergy_estate|Granary Endowments|Temple or monastic networks receive measured grain endowments and storage duties without becoming a universal state church.
sacral|reservoir_labor_rotations|peasants_estate|Reservoir Labor Rotations|Cultivating households receive scheduled waterwork labor and allocation rules at the cost of rapid extraordinary mobilization.
sacral|processional_provisioning|clergy_estate|Processional Provisioning|Ritual institutions receive bounded vessels, textiles, and provisions while accepting inventory and calendar oversight.
sacral|scribal_register_custody|burghers_estate|Scribal Register Custody|Literate and artisan households maintain selected store, donation, and labor records in return for recognized office access.
sacral|frontier_hospitality_endowments|tribes_estate|Frontier Hospitality Endowments|Frontier communities maintain water, offerings, and safe lodging while gaining negotiated protection and local influence.
royal|palace_petition_days|nobles_estate|Palace Petition Days|Regional elites receive regular petition hearings and witnessed judgments, improving coordination while strengthening court access.
royal|dynastic_hostage_compacts|nobles_estate|Dynastic Surety Compacts|Elite houses exchange wards, oaths, and sureties under bounded agreements that reduce conflict but preserve their leverage.
royal|sanctuary_patronage|clergy_estate|Sanctuary Patronage|Cult and sanctuary networks receive protected gifts and inventories while accepting royal arbitration of disputed grants.
royal|tribute_assessment_registers|burghers_estate|Tribute Assessment Registers|Town and caravan houses keep witnessed measures and schedules, reducing arbitrary dues at the cost of immediate revenue.
royal|caravan_protection_guarantees|burghers_estate|Caravan Protection Guarantees|Merchants gain escorts and compensation rules while recognized brokers acquire a stronger voice in royal policy.
royal|fortress_grain_and_muster|peasants_estate|Fortress Grain and Muster|Rural households provide measured grain and bounded muster service in return for predictable demands and local defense.
""".strip()


def profiles() -> list[dict[str, object]]:
    result = []
    for line in PROFILE_DATA.splitlines():
        slug, reforms, atlas, digest, source, confidence, note, names = line.split("|")
        result.append({
            "slug": slug, "reforms": tuple(reforms.split("~")), "atlas": atlas,
            "hash": digest, "source": source, "confidence": confidence, "note": note,
            "names": tuple(names.split("~")),
        })
    return result


def privileges_by_profile() -> dict[str, list[dict[str, str]]]:
    result = {str(profile["slug"]): [] for profile in profiles()}
    for line in PRIVILEGE_DATA.splitlines():
        profile, slug, estate, name, description = line.split("|")
        result[profile].append({
            "slug": slug, "estate": estate, "name": name, "description": description,
        })
    return result


POWER = {
    "nobles_estate": "global_nobles_estate_power",
    "clergy_estate": "global_clergy_estate_power",
    "burghers_estate": "global_burghers_estate_power",
    "peasants_estate": "global_peasants_estate_power",
    "tribes_estate": "global_tribes_estate_power",
}
MAX_TAX = {
    "nobles_estate": "nobles_estate_max_tax",
    "clergy_estate": "clergy_estate_max_tax",
    "burghers_estate": "burghers_estate_max_tax",
}


def item_key(profile: dict[str, object], privilege: dict[str, str]) -> str:
    return f"antq_{profile['slug']}_{privilege['slug']}"


def modifiers(profile_index: int, cell: int, estate: str) -> tuple[tuple[str, str], ...]:
    result: list[tuple[str, str]] = [
        (POWER[estate], f"{0.08 + 0.01 * (profile_index % 3):.2f}"),
        (f"{estate}_target_satisfaction", "medium_privilege_target_satisfaction"),
    ]
    if cell == 0:
        result += [
            ("country_cabinet_efficiency", f"{0.020 + 0.0025 * profile_index:.4f}".rstrip("0")),
            ("monthly_towards_centralization" if profile_index in {0, 1, 3, 7, 8} else "monthly_towards_decentralization", "societal_value_minor_monthly_move"),
        ]
    elif cell == 1:
        result += [
            ("global_levy_size_modifier", f"{0.035 + 0.005 * (profile_index % 4):.3f}".rstrip("0")),
            ("land_morale_modifier", f"{0.010 + 0.0025 * (profile_index % 3):.4f}".rstrip("0")),
            ("monthly_towards_decentralization", "societal_value_minor_monthly_move"),
        ]
    elif cell == 2:
        result += [
            ("research_speed_modifier", f"{0.015 + 0.0025 * (profile_index % 4):.4f}".rstrip("0")),
            ("stability_cost_efficiency", "-0.05"),
        ]
    elif cell == 3:
        result += [
            ("global_trade_through_owned_territory_efficiency", f"{0.040 + 0.005 * (profile_index % 3):.3f}".rstrip("0")),
            ("country_cabinet_efficiency", "0.015"),
        ]
    elif cell == 4:
        result += [
            ("global_production_efficiency", f"{0.020 + 0.0025 * (profile_index % 4):.4f}".rstrip("0")),
            ("country_cabinet_efficiency", "0.015"),
        ]
    else:
        result += [
            ("global_pop_food_consumption", f"{-0.006 - 0.001 * (profile_index % 4):.3f}".rstrip("0")),
            ("global_levy_size_modifier", f"{0.020 + 0.005 * (profile_index % 3):.3f}".rstrip("0")),
            ("monthly_towards_free_subjects", "societal_value_minor_monthly_move"),
            ("global_monthly_control", "-0.0005"),
        ]
    if estate in MAX_TAX:
        result.append((MAX_TAX[estate], f"{-0.03 - 0.01 * (cell % 3):.2f}"))
    elif cell != 5:
        result.append(("global_monthly_control", "-0.0005"))
    return tuple(result)


def q(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def csv_text(header: tuple[str, ...], rows: list[tuple[str, ...]]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    return stream.getvalue()


def exclusive_key(profile: dict[str, object], entries: list[dict[str, str]], cell: int) -> str:
    partner = {0: 1, 1: 0, 3: 4, 4: 3}.get(cell)
    if partner is None or entries[cell]["estate"] != entries[partner]["estate"]:
        return ""
    return item_key(profile, entries[partner])


def content_ledger() -> str:
    grouped = privileges_by_profile()
    rows = []
    for profile_index, profile in enumerate(profiles()):
        entries = grouped[str(profile["slug"])]
        for cell, privilege in enumerate(entries):
            mods = "|".join(f"{name}={value}" for name, value in modifiers(profile_index, cell, privilege["estate"]))
            rows.append((
                item_key(profile, privilege), privilege["estate"], privilege["name"],
                privilege["description"], mods, str(profile["source"]), str(profile["confidence"]),
                str(profile["note"]), "|".join(profile["reforms"]), exclusive_key(profile, entries, cell),
            ))
    return csv_text(
        ("key", "estate", "name", "description", "modifiers", "source", "confidence", "note", "potential_reforms", "exclusive_with"),
        rows,
    )


def source_crop_path(key: str) -> Path:
    return GENERATED_SOURCES / f"antq_privilege_{key.removeprefix('antq_')}_source.png"


def master_path(key: str) -> Path:
    return MASTERS / f"antq_privilege_{key.removeprefix('antq_')}_64x90.png"


def texture_path(key: str) -> Path:
    return ROOT / f"main_menu/gfx/interface/icons/privileges/{key}.dds"


def art_ledger() -> str:
    grouped = privileges_by_profile()
    rows = []
    for profile in profiles():
        for cell, privilege in enumerate(grouped[str(profile["slug"])]):
            key = item_key(profile, privilege)
            rows.append((
                key, str(profile["slug"]), privilege["name"], str(profile["source"]), "secure",
                "Direct material-context illustration; no person, writing, polity emblem, universal constitutional claim, or reconstructed ceremony.",
                f"assets_queue/estate_orders/sources/{profile['atlas']}", str(profile["hash"]), str(cell),
                source_crop_path(key).relative_to(ROOT).as_posix(),
                master_path(key).relative_to(ROOT).as_posix(),
                texture_path(key).relative_to(ROOT).as_posix(),
            ))
    return csv_text(
        ("key", "profile", "subject", "source", "confidence", "note", "source_atlas", "source_sha256", "cell", "source_crop", "master", "texture"),
        rows,
    )


def game_custom_loc_source() -> Path:
    data = json.loads(PATHS.read_text(encoding="utf-8-sig"))
    return Path(data["game_dir"]) / "game/in_game/common/customizable_localization/estates.txt"


def custom_estate_localization() -> str:
    source = game_custom_loc_source()
    raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != BASE_CUSTOM_LOC_HASH:
        raise ValueError(f"installed estates custom-localization source drift: {source}")
    rendered = raw.decode("utf-8-sig")
    for estate in ESTATES:
        anchor = f"{estate} = {{\n\ttype = country\n"
        if anchor not in rendered:
            raise ValueError(f"installed estate localization lacks exact anchor {estate}")
        insertion = [anchor.rstrip("\n"), "", "\t# ANTIQVITAS ancient order identities."]
        for profile in profiles():
            insertion += [
                "\ttext = {", f"\t\tlocalization_key = antq_estate_{profile['slug']}_{estate}",
                "\t\ttrigger = {", "\t\t\tOR = {",
                *(f"\t\t\t\thas_reform = government_reform:{reform}" for reform in profile["reforms"]),
                "\t\t\t}", "\t\t}", "\t}", "",
            ]
        rendered = rendered.replace(anchor, "\n".join(insertion), 1)
    return "\n".join(line.rstrip() for line in rendered.splitlines()) + "\n"


def localization(language: str) -> str:
    lines = [f"l_{language}:"]
    for profile in profiles():
        for estate, name in zip(ESTATES, profile["names"], strict=True):
            key = f"antq_estate_{profile['slug']}_{estate}"
            lines += [f' {key}: "{q(name)}"', f' {key}_desc: "{q(name)} in this ancient political profile."']
    return "\n".join(lines) + "\n"


def expected_files() -> dict[Path, str]:
    outputs = {
        CONTENT_LEDGER: content_ledger(), ART_LEDGER: art_ledger(),
        CUSTOM_LOC_OUT: custom_estate_localization(),
    }
    for language in ("english", *M2_MIRROR_LANGUAGES):
        outputs[ROOT / f"main_menu/localization/{language}/antq_s2_estates_l_{language}.yml"] = localization(language)
    return outputs


def build_art() -> None:
    GENERATED_SOURCES.mkdir(parents=True, exist_ok=True)
    MASTERS.mkdir(parents=True, exist_ok=True)
    grouped = privileges_by_profile()
    for profile in profiles():
        atlas = SOURCES / str(profile["atlas"])
        if hashlib.sha256(atlas.read_bytes()).hexdigest() != profile["hash"]:
            raise ValueError(f"source atlas hash drift: {atlas.relative_to(ROOT)}")
        with Image.open(atlas) as image:
            width, height = image.size
            if width % 3 or height % 2 or width < 1200 or height < 1000:
                raise ValueError(f"{atlas.relative_to(ROOT)} is not a usable 3x2 atlas")
            cell_width, cell_height = width // 3, height // 2
            rgb = image.convert("RGB")
            for cell, privilege in enumerate(grouped[str(profile["slug"])]):
                key = item_key(profile, privilege)
                x, y = (cell % 3) * cell_width, (cell // 3) * cell_height
                available_width, available_height = cell_width - 16, cell_height - 16
                target_aspect = 64 / 90
                if available_width / available_height > target_aspect:
                    crop_height = available_height
                    crop_width = round(crop_height * target_aspect)
                else:
                    crop_width = available_width
                    crop_height = round(crop_width / target_aspect)
                left = x + (cell_width - crop_width) // 2
                top = y + (cell_height - crop_height) // 2
                crop = rgb.crop((left, top, left + crop_width, top + crop_height))
                crop.save(source_crop_path(key), format="PNG", optimize=True)
                crop.resize((64, 90), Image.Resampling.LANCZOS).save(master_path(key), format="PNG", optimize=True)
                texture_path(key).parent.mkdir(parents=True, exist_ok=True)
                subprocess.run(
                    [sys.executable, str(DDS_TOOL), "convert", str(master_path(key)), str(texture_path(key)), "--compression", "bc7"],
                    check=True,
                )


def validate() -> list[str]:
    failures = []
    rows = list(csv.DictReader(io.StringIO(content_ledger())))
    if len(rows) != 54 or len({row["key"] for row in rows}) != 54:
        failures.append("estate-order ledger must contain 54 unique privileges")
    if any(len(row["description"]) < 75 for row in rows):
        failures.append("estate-order privilege description is too shallow")
    if len({row["modifiers"] for row in rows}) < 30:
        failures.append("estate-order privileges need at least 30 distinct effect packages")
    for profile in profiles():
        atlas = SOURCES / str(profile["atlas"])
        if not atlas.is_file() or hashlib.sha256(atlas.read_bytes()).hexdigest() != profile["hash"]:
            failures.append(f"missing or drifted source atlas: {atlas.relative_to(ROOT)}")
    for path, expected in expected_files().items():
        if not path.is_file():
            failures.append(f"missing generated file: {path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8-sig") != expected:
            failures.append(f"stale generated file: {path.relative_to(ROOT)}")
    for row in rows:
        key = row["key"]
        crop, master, texture = source_crop_path(key), master_path(key), texture_path(key)
        if not crop.is_file() or not master.is_file() or not texture.is_file():
            failures.append(f"missing direct art chain: {key}")
            continue
        with Image.open(crop) as image:
            if image.width < 350 or image.height < 490 or abs(image.width / image.height - 64 / 90) > 0.01:
                failures.append(f"wrong source crop contract: {crop.relative_to(ROOT)} = {image.size}")
        with Image.open(master) as image:
            if image.size != (64, 90):
                failures.append(f"wrong master dimensions: {master.relative_to(ROOT)}")
        expected_dds = {"format": "DDS", "width": "64", "height": "90", "depth": "8", "channels": "srgba 4.0"}
        if identify(texture) != expected_dds:
            failures.append(f"wrong DDS contract: {texture.relative_to(ROOT)}")
    return failures


def write() -> None:
    build_art()
    for path, rendered in expected_files().items():
        path.parent.mkdir(parents=True, exist_ok=True)
        encoding = "utf-8-sig" if path.suffix == ".yml" or path == CUSTOM_LOC_OUT else "utf-8"
        path.write_text(rendered, encoding=encoding, newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.write:
            write()
        failures = validate()
    except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        failures = [str(exc)]
    if failures:
        print("s2_estate_orders: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("s2_estate_orders: PASS (9 profiles; 54 privileges; 54 direct icons; 54 polity-aware order names)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
