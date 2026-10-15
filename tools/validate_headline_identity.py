#!/usr/bin/env python3
"""Validate the canonical Compulsive Research headline convention."""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup

from headline_identity import (
    GENERIC_HEADLINES,
    editorial_headline,
    headline_contains_card_name,
    load_editorial_headlines,
    normalize,
)

NUMBERED_RE = re.compile(r'^(\d{3,4})-.*\.html$')
SUITE_VERSION = '3.0.0'


def load_cards(root: Path) -> dict[int, dict]:
    payload = json.loads((root / 'data' / 'remaining-entry-card-data.json').read_text(encoding='utf-8'))
    return {int(card['entry']): card for card in payload['cards']}


def numbered_files(root: Path) -> list[Path]:
    return sorted(
        (path for path in root.glob('*.html') if NUMBERED_RE.match(path.name)),
        key=lambda path: int(NUMBERED_RE.match(path.name).group(1)),
    )


def extract_headline(soup: BeautifulSoup) -> str:
    h1 = soup.select_one('header.hero h1')
    return normalize(h1.get_text(' ', strip=True)) if h1 else ''


def add_finding(row: dict, finding: str) -> None:
    findings = [item for item in row['findings'].split('|') if item]
    if finding not in findings:
        findings.append(finding)
    row['findings'] = '|'.join(findings)
    row['finding_count'] = len(findings)
    row['status'] = 'FAIL' if findings else 'PASS'


def validate_generator(root: Path) -> list[str]:
    path = root / 'tools' / 'generate_remaining_entries.py'
    text = path.read_text(encoding='utf-8')
    required = [
        'from headline_identity import editorial_headline',
        'return editorial_headline(card)',
        "soup.body['data-article-card'] = card['articleName']",
        "headline_meta['content'] = title",
        "hero_header['data-headline-card'] = card['articleName']",
        "h1['data-headline-card'] = card['articleName']",
        'h1.string = title',
    ]
    failures = [f'GENERATOR_MISSING:{token}' for token in required if token not in text]
    forbidden = [
        'hero-card-name',
        'card_name_span',
        'editorial_span',
        "h1.extend([card_name_span, editorial_span])",
    ]
    failures.extend(f'GENERATOR_FORBIDDEN_VISIBLE_CARD_LABEL:{token}' for token in forbidden if token in text)
    if re.search(r"return\s+ROLE_TITLES", text):
        failures.append('GENERATOR_STILL_RETURNS_SHARED_ROLE_TITLE')
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output-dir', type=Path, default=None)
    args = parser.parse_args()
    root = args.root.resolve()
    output = (args.output_dir or (root / 'audit' / 'headline-convention')).resolve()
    output.mkdir(parents=True, exist_ok=True)

    cards = load_cards(root)
    canonical = load_editorial_headlines(root)
    rows: list[dict] = []
    for path in numbered_files(root):
        entry = int(NUMBERED_RE.match(path.name).group(1))
        card = cards[entry]
        card_name = card['articleName']
        soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'lxml')
        headline = extract_headline(soup)
        expected = editorial_headline(card, root)
        findings: list[str] = []

        if not headline:
            findings.append('MISSING_HERO_HEADLINE')
        if headline != expected:
            findings.append('HEADLINE_DOES_NOT_MATCH_CANONICAL_BANK')
        if headline in GENERIC_HEADLINES:
            findings.append('SHARED_GENERIC_HEADLINE')
        if headline_contains_card_name(headline, card_name):
            findings.append('HEADLINE_CONTAINS_FULL_CARD_NAME')
        if headline.startswith('How '):
            findings.append('HOW_CARD_HEADLINE_CONVENTION')
        if len(headline.split()) > 12:
            findings.append('HEADLINE_EXCEEDS_TWELVE_WORDS')

        hero = soup.select_one('header.hero')
        h1 = soup.select_one('header.hero h1')
        if not hero or not h1:
            findings.append('MISSING_HERO_STRUCTURE')
        else:
            if h1.select_one('.hero-card-name'):
                findings.append('VISIBLE_CARD_NAME_LABEL_PRESENT')
            if h1.select_one('.hero-title'):
                findings.append('LEGACY_HERO_TITLE_WRAPPER_PRESENT')
            if entry >= 401:
                for node, code in [
                    (hero, 'HERO_HEADLINE_CARD_MISMATCH'),
                    (h1, 'H1_HEADLINE_CARD_MISMATCH'),
                ]:
                    if not node or normalize(node.get('data-headline-card') or '').casefold() != normalize(card_name).casefold():
                        findings.append(code)

        meta = soup.find('meta', attrs={'name': 'article-headline'})
        if entry >= 401:
            if not meta or normalize(meta.get('content') or '') != headline:
                findings.append('HEADLINE_META_MISMATCH')
        elif meta and normalize(meta.get('content') or '') != headline:
            findings.append('HEADLINE_META_MISMATCH')
        if soup.title and headline not in soup.title.get_text(' ', strip=True):
            findings.append('DOCUMENT_TITLE_HEADLINE_MISMATCH')

        # Generated continuation pages mirror the hero title in the opening chapter.
        if entry >= 401:
            opening = soup.select_one('#opening h2')
            if not opening or normalize(opening.get_text(' ', strip=True)) != headline:
                findings.append('OPENING_HEADING_MISMATCH')
            toc = soup.select_one('nav.toc a[href="#opening"]')
            if not toc or normalize(toc.get_text(' ', strip=True)) != headline:
                findings.append('OPENING_TOC_MISMATCH')

        rows.append({
            'file': path.name,
            'entry': entry,
            'card': card_name,
            'headline': headline,
            'expected_headline': expected,
            'word_count': len(headline.split()),
            'status': 'PASS' if not findings else 'FAIL',
            'finding_count': len(findings),
            'findings': '|'.join(findings),
        })

    headline_groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        headline_groups[normalize(row['headline']).casefold()].append(row)
    duplicate_groups = []
    for key, group in headline_groups.items():
        if key and len(group) > 1:
            duplicate_groups.append({
                'headline': group[0]['headline'],
                'files': [row['file'] for row in group],
                'cards': [row['card'] for row in group],
            })
            for row in group:
                add_finding(row, 'DUPLICATE_HERO_HEADLINE')

    generator_failures = validate_generator(root)
    counts = {
        'numbered_files': len(rows),
        'canonical_bank_entries': len(canonical),
        'unique_headlines': len([key for key in headline_groups if key]),
        'duplicate_headline_groups': len(duplicate_groups),
        'card_name_leaks': sum('HEADLINE_CONTAINS_FULL_CARD_NAME' in row['findings'] for row in rows),
        'visible_card_name_labels': sum('VISIBLE_CARD_NAME_LABEL_PRESENT' in row['findings'] for row in rows),
        'passed': sum(row['status'] == 'PASS' for row in rows),
        'failed': sum(row['status'] == 'FAIL' for row in rows),
        'entries_001_400_passed': sum(row['status'] == 'PASS' and row['entry'] <= 400 for row in rows),
        'entries_001_400_failed': sum(row['status'] == 'FAIL' and row['entry'] <= 400 for row in rows),
        'entries_401_1000_passed': sum(row['status'] == 'PASS' and row['entry'] >= 401 for row in rows),
        'entries_401_1000_failed': sum(row['status'] == 'FAIL' and row['entry'] >= 401 for row in rows),
        'generator_failures': len(generator_failures),
    }
    passed = (
        len(rows) == 1000
        and len(canonical) == 1000
        and counts['failed'] == 0
        and not duplicate_groups
        and not generator_failures
    )

    csv_path = output / 'headline-convention-validation.csv'
    with csv_path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    payload = {
        'suite': 'Compulsive Research Headline Convention Validator Suite',
        'suite_version': SUITE_VERSION,
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'result': 'PASS' if passed else 'FAIL',
        'counts': counts,
        'generator_failures': generator_failures,
        'duplicate_groups': duplicate_groups,
        'failed_pages': [row for row in rows if row['status'] == 'FAIL'],
    }
    (output / 'headline-convention-validation.json').write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8'
    )

    report = [
        '# Headline Convention Validator Suite',
        '',
        f"**Result:** {payload['result']}",
        f"**Suite version:** {SUITE_VERSION}",
        f"**Numbered articles scanned:** {counts['numbered_files']}",
        '',
        '## Results',
        '',
        f"- Canonical title-bank entries: {counts['canonical_bank_entries']}.",
        f"- Unique hero headlines: {counts['unique_headlines']} of 1,000.",
        f"- Duplicate headline groups: {counts['duplicate_headline_groups']}.",
        f"- Full card-name leaks: {counts['card_name_leaks']}.",
        f"- Visible hero card-name labels: {counts['visible_card_name_labels']}.",
        f"- Entries 001–400: {counts['entries_001_400_passed']} passed, {counts['entries_001_400_failed']} failed.",
        f"- Entries 401–1000: {counts['entries_401_1000_passed']} passed, {counts['entries_401_1000_failed']} failed.",
        f"- Generator contract failures: {counts['generator_failures']}.",
        '',
        '## Enforced convention',
        '',
        '1. Every numbered article uses its canonical thematic essay title.',
        '2. No two numbered articles share the same normalized hero headline.',
        '3. The complete card name may not appear inside the thematic headline.',
        '4. Generated pages may not display a separate card-name label above the headline.',
        '5. Hero, browser title, headline metadata, opening chapter, and table of contents agree.',
        '6. Headlines are limited to twelve words for the established mobile presentation.',
        '7. The generator reads the canonical title bank and emits a plain thematic H1.',
    ]
    if generator_failures:
        report.extend(['', '## Generator failures', ''] + [f'- {item}' for item in generator_failures])
    if payload['failed_pages']:
        report.extend(['', '## Failed pages', ''] + [f"- `{row['file']}`: {row['findings']}" for row in payload['failed_pages']])
    (output / 'HEADLINE-CONVENTION-VALIDATION-REPORT.md').write_text('\n'.join(report) + '\n', encoding='utf-8')

    print(json.dumps(counts, indent=2))
    print(f"Headline Convention Validator Suite: {payload['result']}")
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
