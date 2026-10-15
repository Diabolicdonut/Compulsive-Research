#!/usr/bin/env python3
"""Canonical thematic headline helpers for Compulsive Research.

The numbered archive uses editorial essay titles that describe the card without
repeating the card's name.  Canonical titles live in data/editorial-headlines.json.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

GENERIC_HEADLINES = {
    'A Body With Immediate Consequences',
    'The Mana Base as Strategy',
    'One Card Becoming a Longer Game',
    'The Card That Rewards Exact Sequencing',
    'A Permanent With Several Clocks',
    'The Exchange That Sets the Terms',
    'A Second Hand Below the Table',
    'Mana That Changes the Curve',
    'Breaking the Price of a Spell',
    'More Material Than One Card',
    'The Difference Between Drawing and Finding',
    'Damage as Removal and Clock',
    'Consistency With a Cost',
    'Turning Loss Into an Engine',
    'The Right to Say No',
    'The Threat That Demands the Right Answer',
    'Information Before Action',
    'Small Marks, Compounding Consequences',
    'The Value of Doing It Again',
}

STYLE_NAME = 'thematic-editorial-headline-without-card-name'


def normalize(value: str) -> str:
    return re.sub(r'\s+', ' ', value or '').strip()


def normalized_words(value: str) -> str:
    return re.sub(r'[^a-z0-9]+', ' ', normalize(value).casefold()).strip()


def headline_contains_card_name(headline: str, card_name: str) -> bool:
    """Return True when the complete normalized card name appears in a headline."""
    headline_key = normalized_words(headline)
    card_key = normalized_words(card_name)
    return bool(card_key and card_key in headline_key)


def _root_from_module() -> Path:
    return Path(__file__).resolve().parents[1]


@lru_cache(maxsize=4)
def load_editorial_headlines(root: str | Path | None = None) -> dict[int, dict[str, Any]]:
    project_root = Path(root).resolve() if root else _root_from_module()
    path = project_root / 'data' / 'editorial-headlines.json'
    payload = json.loads(path.read_text(encoding='utf-8'))
    if payload.get('style') != STYLE_NAME:
        raise RuntimeError(f'{path}: unsupported headline style {payload.get("style")!r}')
    entries = {int(row['entry']): row for row in payload.get('entries', [])}
    if len(entries) != 1000:
        raise RuntimeError(f'{path}: expected 1,000 canonical headlines, found {len(entries)}')
    return entries


def draft_headline_without_name(card: Mapping[str, Any]) -> str:
    """Conservative fallback for a future card not yet in the canonical title bank.

    The archive validator intentionally treats this as a draft: it must still be
    reviewed for uniqueness before publication.
    """
    card_type = normalize(str(card.get('type') or 'Card'))
    oracle = normalize(str(card.get('oracleText') or '')).casefold()
    if 'land' in card_type.casefold():
        return 'The Land Drop With a Second Strategic Job'
    if 'planeswalker' in card_type.casefold():
        return 'The Permanent That Turned Loyalty Into Several Clocks'
    if 'creature' in card_type.casefold():
        if 'graveyard' in oracle:
            return 'The Creature That Made the Graveyard Part of the Battlefield'
        if 'draw a card' in oracle:
            return 'The Creature That Turned Board Presence Into Cards'
        return 'The Creature That Made Its Text Matter Beyond Combat'
    if 'instant' in card_type.casefold() or 'sorcery' in card_type.casefold():
        return 'The Spell That Made Sequencing the Real Cost'
    if 'artifact' in card_type.casefold():
        return 'The Artifact That Turned One Slot Into an Engine'
    if 'enchantment' in card_type.casefold():
        return 'The Enchantment That Changed the Rules of Every Turn'
    return 'The Card That Changed the Shape of the Next Decision'


def editorial_headline(card: Mapping[str, Any], root: str | Path | None = None) -> str:
    entry = int(card.get('entry') or 0)
    canonical = load_editorial_headlines(root)
    row = canonical.get(entry)
    if row:
        expected_card = normalize(str(row.get('card') or ''))
        actual_card = normalize(str(card.get('articleName') or card.get('cardName') or ''))
        if expected_card and actual_card and expected_card.casefold() != actual_card.casefold():
            raise RuntimeError(
                f'Entry {entry}: headline bank expects {expected_card!r}, received {actual_card!r}'
            )
        return normalize(str(row['headline']))
    return draft_headline_without_name(card)
