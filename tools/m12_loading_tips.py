#!/usr/bin/env python3
"""Render and verify the ancient loading-tip overlay for every EU5 client."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/local_paths.json"
LANGUAGES = (
    "braz_por", "english", "french", "german", "japanese", "korean",
    "polish", "russian", "simp_chinese", "spanish", "turkish",
)

# Short display translations/adaptations, paired with their primary ancient
# source.  They deliberately replace every inherited key, never append to it.
TIPS = (
    ("Know yourself.", "Delphic maxim"),
    ("Nothing in excess.", "Delphic maxim"),
    ("The beginning is the most important part of any work.", "Plato, Republic"),
    ("The city exists by nature, and man is by nature a political animal.", "Aristotle, Politics"),
    ("The unexamined life is not worth living.", "Plato, Apology"),
    ("No one is willingly unjust.", "Plato, Protagoras"),
    ("Friendship is one soul dwelling in two bodies.", "Aristotle, Nicomachean Ethics"),
    ("Death is nothing to us.", "Epicurus, Letter to Menoeceus"),
    ("A people must either be ruled or rule.", "Aristotle, Politics; adapted"),
    ("A city is secure when its citizens obey the laws.", "Demosthenes; adapted"),
    ("Fortune favors the bold.", "Virgil, Aeneid"),
    ("Perhaps even this will one day be remembered with pleasure.", "Virgil, Aeneid"),
    ("Seize the day; trust tomorrow as little as you can.", "Horace, Odes"),
    ("The welfare of the people is the highest law.", "Cicero, On the Laws"),
    ("By harmony small states grow; by discord the greatest fall.", "Sallust, Jugurthine War"),
    ("We cannot bear our vices or their remedies.", "Livy, History of Rome"),
    ("The whole of Gaul is divided into three parts.", "Julius Caesar, Gallic War"),
    ("Time, the devourer of all things.", "Ovid, Metamorphoses"),
    ("No possession is as precious as a friend who is wise.", "Seneca; adapted"),
    ("Where they make a desert, they call it peace.", "Tacitus, Agricola"),
    ("It is not things that disturb people, but their judgments about things.", "Epictetus, Enchiridion"),
    ("The universe is change; life is shaped by judgment.", "Marcus Aurelius, Meditations"),
    ("The best physician is also a philosopher.", "Galen, That the Best Physician Is Also a Philosopher"),
    ("Character is fate.", "Heraclitus; traditional rendering"),
    ("War is the father of all things.", "Heraclitus; traditional rendering"),
    ("Justice, justice shall you pursue.", "Deuteronomy 16:20"),
    ("If I am not for myself, who will be for me?", "Hillel, Pirkei Avot"),
    ("If not now, when?", "Hillel, Pirkei Avot"),
    ("The world stands on justice, truth, and peace.", "Shimon ben Gamliel, Pirkei Avot"),
    ("Do not stand idly by the blood of your neighbor.", "Leviticus 19:16"),
    ("Learn and practice what you have learned: is that not a pleasure?", "Confucius, Analects"),
    ("The superior person understands what is right; the small person understands profit.", "Confucius, Analects"),
    ("To govern is to set things right.", "Confucius, Analects; adapted"),
    ("The people are the foundation of a state.", "Mencius; adapted"),
    ("A journey of a thousand li begins beneath one's feet.", "Daodejing; adapted"),
    ("Knowing others is intelligence; knowing oneself is wisdom.", "Daodejing"),
    ("Know the enemy and know yourself, and danger will not attend a hundred battles.", "Sunzi, Art of War"),
    ("In war, avoid what is strong and strike what is weak.", "Sunzi, Art of War; adapted"),
    ("The ruler's happiness lies in the happiness of the people.", "Arthashastra; adapted"),
    ("Action alone is yours; never its fruits.", "Bhagavad Gita"),
    ("All conditioned things are impermanent.", "Dhammapada"),
    ("Conquer anger through non-anger.", "Dhammapada"),
    ("All people are my children.", "Ashoka, Rock Edict"),
    ("There is no wealth like contentment.", "Tirukkural; adapted"),
    ("Speak what is true and kind.", "Tirukkural; adapted"),
    ("May Ahura Mazda protect this land from hostile armies, famine, and the Lie.", "Darius, Persepolis inscription"),
    ("You who may live hereafter: be happy while you live.", "Darius, Behistun inscription; adapted"),
    ("Do not be proud because of your learning.", "Instruction of Ptahhotep"),
    ("A good name is better than fine wealth.", "Instruction of Amenemope"),
    ("The sun has risen; darkness has fled.", "Great Hymn to the Aten; adapted"),
    ("The earth is kind and gentle, and welcomes the hands of mortals.", "Pliny the Elder, Natural History; adapted"),
    ("There is no greater wealth than health.", "Pliny the Elder, Natural History; adapted"),
    ("The sea joins lands that distance separates.", "Periplus of the Erythraean Sea; adapted"),
    ("The Nile's gift is renewal.", "Diodorus Siculus on Egypt; adapted"),
    ("A house is judged by the welcome it gives.", "Homeric tradition; adapted"),
    ("The gods help those who work with prudence.", "Hesiod, Works and Days; adapted"),
    ("A just ruler guards the weak as well as the strong.", "Xenophon, Cyropaedia; adapted"),
    ("Custom is the king of all.", "Pindar; traditional rendering"),
    ("No great thing is created suddenly.", "Epictetus, Discourses; adapted"),
    ("The measure of prosperity is peace within the household.", "Columella, On Agriculture; adapted"),
    ("The courage of citizens is a city's strongest wall.", "Thucydides; adapted"),
    ("The whole inhabited world is one community.", "Stoic tradition; adapted"),
    ("The sea is a road between peoples.", "Strabo, Geography; adapted"),
    ("A harbor is a city's gate to distant lands.", "Strabo, Geography; adapted"),
)

TIP_KEYS = tuple(f"LOADING_TIP_{index}" for index in range(60)) + tuple(
    f"LOADING_TIP_d008_{index}" for index in range(4)
)
TIP_KEY_PATTERN = re.compile(r"(?m)^\s*(LOADING_TIP_[A-Za-z0-9_]+)\s*:")


def installed_tip_keys() -> tuple[str, ...]:
    config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
    game = Path(config["game_dir"]) / "game"
    roots = [game / "loading_screen/localization/english"]
    roots.extend(
        package / "loading_screen/localization/english"
        for package in sorted((game / "dlc").glob("*"))
        if package.is_dir()
    )
    keys: set[str] = set()
    for root in roots:
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*.yml")):
            keys.update(TIP_KEY_PATTERN.findall(path.read_text(encoding="utf-8-sig")))
    return tuple(sorted(keys))


def targets(language: str) -> tuple[Path, Path]:
    """Mount the canonical file name from both participating client modules.

    The loader resolves duplicate localization keys on first definition.  Both
    mounts therefore use the original ``load_tips`` VFS name, rather than a
    late, differently named overlay that can never take precedence.
    """
    return (
        ROOT / "loading_screen" / "localization" / language / f"load_tips_l_{language}.yml",
        ROOT / "main_menu" / "localization" / language / f"load_tips_l_{language}.yml",
    )


def rendered(language: str) -> str:
    lines = [f"l_{language}:"]
    for key, (quote, source) in zip(TIP_KEYS, TIPS, strict=True):
        escaped_quote = quote.replace('"', r'\"')
        lines.append(
            f' {key}: " #T \\"{escaped_quote}\\"#! \\n #tooltip_subheading — {source}#!"'
        )
    return "\ufeff" + "\n".join(lines) + "\n"


def write() -> None:
    for language in LANGUAGES:
        legacy_overlay = (
            ROOT / "main_menu" / "localization" / language
            / f"antq_loading_tips_l_{language}.yml"
        )
        # This file was generated by an earlier probe and is not part of the
        # content contract.  Remove only that known generated artifact.
        if legacy_overlay.exists():
            legacy_overlay.unlink()
        content = rendered(language)
        for path in targets(language):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")


def validate() -> None:
    installed = installed_tip_keys()
    if installed != tuple(sorted(TIP_KEYS)):
        missing = sorted(set(installed) - set(TIP_KEYS))
        stale = sorted(set(TIP_KEYS) - set(installed))
        raise ValueError(
            f"installed loading-tip union changed; missing overrides={missing}, "
            f"stale overrides={stale}"
        )
    if len(TIPS) != len(TIP_KEYS):
        raise ValueError(
            f"expected {len(TIP_KEYS)} installed LOADING_TIP keys, "
            f"found {len(TIPS)} texts"
        )
    for language in LANGUAGES:
        content = rendered(language)
        for path in targets(language):
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                raise ValueError(f"stale or missing loading-tip mirror: {path}")
    if any("AD " in quote or "CE" in quote for quote, _ in TIPS):
        raise ValueError("loading tips must not contain era-marker abbreviations")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        write()
    if args.check or not args.write:
        validate()
    print(
        f"m12_loading_tips: PASS ({len(TIPS)} ancient tips; "
        f"{len(LANGUAGES)} client mirrors; 2 exact-name overlays)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
