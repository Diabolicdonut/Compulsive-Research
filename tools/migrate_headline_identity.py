#!/usr/bin/env python3
"""Migrate generated article hero headlines to unique card-specific titles."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

from headline_identity import editorial_headline

NUMBERED_RE = re.compile(r'^(\d{3,4})-.*\.html$')


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_cards(root: Path) -> dict[int, dict]:
    payload = json.loads((root / 'data' / 'remaining-entry-card-data.json').read_text(encoding='utf-8'))
    return {int(card['entry']): card for card in payload['cards']}


def update_page(path: Path, card: dict, headline: str) -> bool:
    before = path.read_text(encoding='utf-8')
    soup = BeautifulSoup(before, 'lxml')
    entry = int(card['entry'])
    card_name = card['articleName']

    if soup.title:
        soup.title.string = f'{card_name}: {headline} — Compulsive Research'

    meta = soup.find('meta', attrs={'name': 'article-headline'})
    if not meta:
        meta = soup.new_tag('meta')
        meta['name'] = 'article-headline'
        if soup.head:
            soup.head.append(meta)
    meta['content'] = headline

    if soup.body and entry >= 401:
        soup.body['data-article-card'] = card_name

    hero = soup.select_one('header.hero')
    if not hero:
        raise RuntimeError(f'{path.name}: missing header.hero')
    hero['data-headline-card'] = card_name

    h1 = hero.find('h1')
    if not h1:
        raise RuntimeError(f'{path.name}: missing hero h1')
    h1['data-headline-card'] = card_name

    h1.clear()
    h1.string = headline

    opening = soup.select_one('article #opening h2') or soup.select_one('#opening h2')
    if opening:
        opening.string = headline

    toc_link = soup.select_one('nav.toc a[href="#opening"]')
    if toc_link:
        toc_link.string = headline

    after = '<!DOCTYPE html>\n' + str(soup.html)
    if after != before:
        path.write_text(after, encoding='utf-8')
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--report', type=Path, default=None)
    args = parser.parse_args()
    root = args.root.resolve()
    cards = load_cards(root)

    targets = list(range(401, 1001))
    targets.append(273)  # Resolve the only duplicate inherited from entries 001–400.
    targets.sort()

    rows = []
    for entry in targets:
        card = cards[entry]
        matches = sorted(root.glob(f'{entry:03d}-*.html')) if entry < 1000 else sorted(root.glob(f'{entry}-*.html'))
        if len(matches) != 1:
            raise RuntimeError(f'Entry {entry}: expected one article, found {len(matches)}')
        path = matches[0]
        old_hash = digest(path)
        headline = editorial_headline(card)
        changed = update_page(path, card, headline)
        rows.append({
            'entry': entry,
            'file': path.name,
            'card': card['articleName'],
            'headline': headline,
            'changed': changed,
            'before_sha256': old_hash,
            'after_sha256': digest(path),
        })

    report = args.report or (root / 'audit' / 'headline-migration' / 'headline-migration.json')
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps({
        'migration': 'thematic-headlines-without-card-names',
        'target_count': len(targets),
        'changed_count': sum(bool(row['changed']) for row in rows),
        'preserved_handcrafted_title_entry': 605,
        'rows': rows,
    }, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'Updated {sum(bool(row["changed"]) for row in rows)} of {len(rows)} target articles.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
