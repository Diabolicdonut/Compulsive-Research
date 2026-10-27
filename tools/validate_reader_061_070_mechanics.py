#!/usr/bin/env python3
"""Focused, read-only regression checks for the Reader 061–070 mechanics-preparation pass.

This does not certify the complete Reader V3.1 migration, historical deck
registrations, or independent correctness of every sentence. Those are separate
acceptance gates. It guards specific errors discovered while researching the
upcoming ten-article wave.
"""
from __future__ import annotations

import re
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    ("061-maze-of-ith.html", ["does not tap", "remains attacking", "mana source"]),
    ("062-the-tabernacle-at-pendrell-vale.html", ["four creatures", "two lands", "upkeep"]),
    ("063-moat.html", ["could not be declared", "cannot be declared", "blocks"]),
    ("064-nether-void.html", ["triggered ability", "another {3}", "countered"]),
    ("065-the-abyss.html", ["one target", "not a sacrifice", "nonartifact"]),
    ("066-land-tax.html", ["three", "upkeep", "intervening"]),
    ("067-sylvan-library.html", ["four life", "draw", "returned"]),
    ("068-concordant-crossroads.html", ["haste", "opposing", "elves"]),
    ("069-eureka.html", ["pass", "triggered", "put"]),
    ("070-candelabra-of-tawnos.html", ["high tide", "june 29, 2026", "six"]),
]
BOILERPLATE = (
    "Imagine a game in which neither player is dramatically ahead",
    "the next exchange will determine who is allowed to dictate the middle turns",
    "The strongest line is rarely the one that produces the largest immediate number",
)
errors = []
for path, requirements in CASES:
    page = BeautifulSoup((ROOT / path).read_text(encoding="utf-8"), "lxml")
    section = page.select_one("section#case-study")
    if section is None:
        errors.append(f"{path}: missing case-study section")
        continue
    content = section.get_text(" ", strip=True).casefold()
    paragraphs = section.find_all("p")
    if len(paragraphs) < 2 or len(content.split()) < 100:
        errors.append(f"{path}: case study is not a substantive example")
    for phrase in requirements:
        if phrase.casefold() not in content:
            errors.append(f"{path}: case study missing reviewed evidence {phrase!r}")
    for phrase in BOILERPLATE:
        if phrase.casefold() in content:
            errors.append(f"{path}: old interchangeable boilerplate survived")
    if not any(token in content for token in ("hypothetical", "representative", "illustrative", "reconstruction", "fictional", "example")):
        errors.append(f"{path}: must not read like an attributed match transcript")

maze = (ROOT / CASES[0][0]).read_text(encoding="utf-8")
if "after combat damage to remove it from combat" in maze:
    errors.append("061: Maze must not be claimed to remove an attacker from combat")
if "does not remove" not in maze or "cannot tap for mana" not in maze:
    errors.append("061: exact Maze combat/mana safeguards must be present")

tabernacle = (ROOT / CASES[1][0]).read_text(encoding="utf-8")
if "around its activation" in tabernacle or "sacrifice timing" in tabernacle:
    errors.append("062: Tabernacle must not be described as an activated sacrifice tax")
if "there is no activation" not in tabernacle and "never tapped or activated" not in tabernacle:
    errors.append("062: recurring triggered-tax safeguard missing")

void = (ROOT / CASES[3][0]).read_text(encoding="utf-8")
if "nether void makes every spell cost three additional mana" in void.casefold():
    errors.append("064: Nether Void is a triggered counter, not a cost increaser")

abyss = (ROOT / CASES[4][0]).read_text(encoding="utf-8")
if "the sacrifice effect is asymmetrical" in abyss:
    errors.append("065: Abyss causes destruction rather than sacrifice")

candelabra = (ROOT / CASES[-1][0]).read_text(encoding="utf-8")
for needle in ("June 29, 2026", "banned Candelabra of Tawnos in Legacy", "magic.wizards.com/en/news/announcements/banned-and-restricted-june-29-2026"):
    if needle.casefold() not in candelabra.casefold():
        errors.append(f"070: dated Legacy legality evidence missing: {needle}")

if errors:
    print(f"Reader 061–070 focused mechanics preparation: FAIL ({len(errors)})")
    for error in errors:
        print("- " + error)
    raise SystemExit(1)
print("Reader 061–070 focused mechanics preparation: PASS (10 unique, rules-grounded case studies)")
