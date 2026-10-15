#!/usr/bin/env python3
"""Regression fixtures for catalog-driven card-reference discovery."""
from __future__ import annotations

from bs4 import BeautifulSoup

from card_reference_engine import display_map_from_catalog, discover_section_matches, match_counter


def discover(text: str, catalog_names: list[str], aliases: dict[str, str] | None = None):
    aliases = aliases or {}
    soup = BeautifulSoup(f'<section class="design-echo-section"><p>{text}</p></section>', 'html.parser')
    catalog = {name.casefold(): name for name in catalog_names}
    matches = discover_section_matches(
        soup.section,
        display_map_from_catalog(catalog, aliases),
        subject='Subject Card',
        aliases=aliases,
    )
    return match_counter(matches)


def main() -> int:
    failures: list[str] = []

    result = discover(
        'Animate Dead, Exhume, Necromancy, Persist, Unburial Rites, and modern spells.',
        ['Animate Dead', 'Exhume', 'Necromancy', 'Persist', 'Unburial Rites'],
    )
    if result['Persist'] != 1:
        failures.append('Persist was not discovered in a high-confidence card list')

    result = discover(
        'Tainted Pact, Spoils of the Vault, Plunge into Darkness, and Oracle-based combo decks.',
        ['Tainted Pact', 'Spoils of the Vault', 'Plunge into Darkness'],
    )
    if result['Plunge into Darkness'] != 1:
        failures.append('Plunge into Darkness was not discovered')

    result = discover(
        'Cryptolith Rite, Jaheira, Friend of the Forest, and Springleaf Drum preserve the idea.',
        ['Cryptolith Rite', 'Jaheira, Friend of the Forest', 'Forest', 'Springleaf Drum'],
    )
    if result['Jaheira, Friend of the Forest'] != 1 or result['Forest']:
        failures.append('longest-name-first matching did not prevent partial Forest linking')

    result = discover(
        'Hunted Horror, Kroxa, Uro, and Rotting Regisaur continue the pattern.',
        ['Hunted Horror', "Kroxa, Titan of Death's Hunger", "Uro, Titan of Nature's Wrath", 'Rotting Regisaur'],
        {'Kroxa': "Kroxa, Titan of Death's Hunger", 'Uro': "Uro, Titan of Nature's Wrath"},
    )
    if result["Kroxa, Titan of Death's Hunger"] != 1 or result["Uro, Titan of Nature's Wrath"] != 1:
        failures.append('shortened-name aliases were not resolved')

    result = discover(
        'Deadly Dispute-style sacrifice economics changed the rate.',
        ['Deadly Dispute'],
        {'Deadly Dispute': 'Deadly Dispute'},
    )
    if result['Deadly Dispute'] != 1:
        failures.append('hyphen-suffixed card name was not discovered')

    result = discover('The forest remained dark, and balance returned later.', ['Forest', 'Balance'])
    if result:
        failures.append('ambiguous ordinary words were linked without card-list context')

    if failures:
        for failure in failures:
            print('FAIL:', failure)
        return 1
    print('PASS: card-reference discovery regression fixtures')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
