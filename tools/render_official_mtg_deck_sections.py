#!/usr/bin/env python3
"""Render static Official Magic the Gathering deck sections from a snapshot.

The resulting outer section and every product deck are collapsed by default.
No browser fetch is used. Run with --check to verify that committed article
markup exactly matches the current catalogue snapshot.
"""
from __future__ import annotations

import argparse
import html
import json
import math
import re
import unicodedata
from collections import OrderedDict, defaultdict
from pathlib import Path
from typing import Any

BOARD_KEYS = ("mainBoard", "sideBoard", "commander", "displayCommander", "planes", "schemes")
ZONE_LABELS = {
    "mainBoard": "Main deck", "sideBoard": "Sideboard", "commander": "Commander",
    "displayCommander": "Display commander", "planes": "Planar deck", "schemes": "Scheme deck",
}
CATEGORY_ORDER = ["Creatures", "Planeswalkers", "Instants", "Sorceries", "Artifacts", "Enchantments", "Battles", "Lands", "Other cards"]
DIGITAL_TYPES = {
    "Arena Promotional Deck", "Arena Starter Deck", "Duel Of The Planeswalkers Deck", "Halfdeck",
    "Historic Brawl Precon Deck", "MTGO Commander Deck", "MTGO Duel Deck", "MTGO Theme Deck",
}
ARTICLE_CARD_RE = re.compile(r'<body\b[^>]*\bdata-article-card=(["\'])(.*?)\1', re.I | re.S)
MARKED_RE = re.compile(r'<!--\s*CR_OFFICIAL_MTG_DECKS_START\s*-->.*?<!--\s*CR_OFFICIAL_MTG_DECKS_END\s*-->', re.I | re.S)
LEGACY_RE = re.compile(r'<details\b[^>]*class=["\'][^"\']*\bpreconstructed-archive\b[^"\']*["\'][^>]*>.*?</details>(?=\s*</section>)', re.I | re.S)
LEGACY_SCRIPT_RE = re.compile(r'\s*<script\b[^>]*src=["\'](?:assets/)?preconstructed-decks\.js["\'][^>]*>\s*</script>\s*', re.I)


def norm(value: Any) -> str:
    text = str(value or "").replace("’", "'").replace("‘", "'").replace("–", "-").replace("—", "-")
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().casefold()
    return re.sub(r"[^a-z0-9]+", "", text)


def classify(type_line: str) -> str:
    t = str(type_line or "")
    if "Creature" in t: return "Creatures"
    if "Planeswalker" in t: return "Planeswalkers"
    if "Battle" in t: return "Battles"
    if "Instant" in t: return "Instants"
    if "Sorcery" in t: return "Sorceries"
    if "Artifact" in t: return "Artifacts"
    if "Enchantment" in t: return "Enchantments"
    if "Land" in t: return "Lands"
    return "Other cards"


def total(zone: list[list[Any]]) -> int:
    return sum(int(count) for _, count in zone)


def aggregate(zone: list[list[Any]], cards: dict[str, dict]) -> list[dict[str, Any]]:
    out: OrderedDict[str, dict[str, Any]] = OrderedDict()
    for uuid, count in zone:
        info = cards[str(uuid)]
        name = str(info["name"])
        if name not in out:
            out[name] = {"name": name, "count": 0, "type": str(info.get("type") or "")}
        out[name]["count"] += int(count)
    return list(out.values())


def category_groups(zone: list[list[Any]], cards: dict[str, dict]) -> list[tuple[str, list[dict[str, Any]]]]:
    buckets = {label: [] for label in CATEGORY_ORDER}
    for item in aggregate(zone, cards):
        buckets[classify(item["type"])].append(item)
    return [(label, values) for label in CATEGORY_ORDER if (values := buckets[label])]


def split_groups(groups: list[tuple[str, list[dict[str, Any]]]]) -> tuple[list, list]:
    if not groups:
        return [], []
    weights = [max(1, len(items)) for _, items in groups]
    total_weight = sum(weights)
    best_i, best_delta, acc = 1, math.inf, 0
    for i, weight in enumerate(weights[:-1], start=1):
        acc += weight
        delta = abs(total_weight - 2 * acc)
        if delta < best_delta:
            best_i, best_delta = i, delta
    return groups[:best_i], groups[best_i:]


def row_html(item: dict[str, Any]) -> str:
    name = str(item["name"])
    return '<div class="row">' + f'<span class="qty">{int(item["count"])}</span>' + f'<span class="card-name" data-card="{html.escape(name, quote=True)}" tabindex="0">{html.escape(name)}</span>' + '</div>'


def group_html(label: str, items: list[dict[str, Any]]) -> str:
    qty = sum(int(item["count"]) for item in items)
    return f'<div class="group"><h4>{html.escape(label)} · {qty}</h4>' + ''.join(row_html(item) for item in items) + '</div>'


def board_text(label: str, zone: list[list[Any]], cards: dict[str, dict]) -> list[str]:
    items = aggregate(zone, cards)
    if not items:
        return []
    lines = [f'{label} · {sum(item["count"] for item in items)}']
    lines.extend(f'{item["count"]} {item["name"]}' for item in items)
    lines.append('')
    return lines


def subject_copies(product: dict, subject_uuids: set[str]) -> int:
    return sum(int(count) for key in BOARD_KEYS for uuid, count in product["zones"][key] if str(uuid) in subject_uuids)


def render_product(product: dict, subject: str, subject_uuids: set[str], index: int, cards: dict[str, dict]) -> str:
    zones = product["zones"]
    counts = {key: total(zones[key]) for key in BOARD_KEYS}
    copies = subject_copies(product, subject_uuids)
    groups = category_groups(zones["mainBoard"], cards)
    extras = []
    for key in ("sideBoard", "commander", "displayCommander", "planes", "schemes"):
        items = aggregate(zones[key], cards)
        if items:
            extras.append((ZONE_LABELS[key], items))
    left, right = split_groups(groups)
    right = right + extras
    if not right and len(left) > 1:
        left, right = left[:-1], left[-1:]

    deck_id = f'official-mtg-{norm(subject)}-{index:03d}-{product["id"][-6:]}'
    copy_lines = [f'{product["name"]} — {product["type"]}', f'{product["setName"]} ({product["setCode"]}) · {product["releaseDate"]}', '']
    for key in BOARD_KEYS:
        copy_lines.extend(board_text(ZONE_LABELS[key], zones[key], cards))
    copy_text = '\n'.join(copy_lines).strip()

    zone_bits = [f'Main deck {counts["mainBoard"]}', f'Sideboard {counts["sideBoard"]}' if counts["sideBoard"] else 'No sideboard']
    for key in ("commander", "displayCommander", "planes", "schemes"):
        if counts[key]:
            zone_bits.append(f'{ZONE_LABELS[key]} {counts[key]}')
    context = 'Official digital Magic deck' if product["type"] in DIGITAL_TYPES else 'Official commercial Magic deck'
    note = f'This {product["type"].lower()} contains {copies} cop{"y" if copies == 1 else "ies"} of {subject}. Its published deck contains {counts["mainBoard"]} cards in the main deck' + (f' and {counts["sideBoard"]} in the sideboard.' if counts["sideBoard"] else ' and no published sideboard.')
    if counts["commander"]: note += f' The product also identifies {counts["commander"]} commander card{"s" if counts["commander"] != 1 else ""}.'
    if counts["planes"]: note += f' Its planar deck contains {counts["planes"]} cards.'
    if counts["schemes"]: note += f' Its scheme deck contains {counts["schemes"]} cards.'
    source_html = ''
    if str(product.get("source") or '').startswith(('http://', 'https://')):
        source_html = f'<p class="small">Product-list source: <a href="{html.escape(product["source"], quote=True)}">open the documented deck record</a></p>'
    summary_small = f'{product["type"]} · {product["setName"]} · {product["releaseDate"]} · {copies}× {subject}'
    parts = [
        f'<details class="deck official-mtg-deck" data-deck-kind="official-mtg-product" data-product-id="{product["id"]}" data-main-count="{counts["mainBoard"]}" data-sideboard-count="{counts["sideBoard"]}" data-commander-count="{counts["commander"]}" data-display-commander-count="{counts["displayCommander"]}" data-plane-count="{counts["planes"]}" data-scheme-count="{counts["schemes"]}" data-subject-copies="{copies}" data-product-type="{html.escape(product["type"], quote=True)}">',
        '<summary><span>', f'<strong>{html.escape(product["name"])}</strong>', f'<small>{html.escape(summary_small)}</small>', '</span><span class="plus">+</span></summary>',
        '<div class="deck-body">', f'<span class="provenance-badge">{html.escape(context)}</span>', f'<p>{html.escape(note)}</p>', '<div class="deck-meta"><div>',
        f'<b>{html.escape(product["name"])}</b><div class="small">{html.escape(" · ".join(zone_bits))}</div>', f'</div><button class="copy" data-target="{deck_id}" type="button">Copy decklist</button></div>',
        '<div class="deck-columns">', '<div class="deck-col">' + ''.join(group_html(label, items) for label, items in left) + '</div>', '<div class="deck-col">' + ''.join(group_html(label, items) for label, items in right) + '</div>', '</div>',
        f'<pre hidden id="{deck_id}">{html.escape(copy_text)}</pre>', source_html, '</div></details>',
    ]
    return ''.join(parts)


def render_section(subject: str, products: list[dict], subject_uuids: set[str], catalogue: dict) -> str:
    count = len(products)
    escaped = html.escape(subject)
    if products:
        decks = ''.join(render_product(p, subject, subject_uuids, i + 1, catalogue["cards"]) for i, p in enumerate(products))
        body = f'<p class="preconstructed-status"><b>{count}</b> official Magic deck product{"s" if count != 1 else ""} contain {escaped}. Each complete published decklist is embedded here for offline viewing. Products without sideboards remain without sideboards.</p><p class="small official-deck-scope-note">Included records are ready-to-play commercial, introductory, commemorative replica, or official digital decks. Redemption sets, randomized or fixed card assortments, Deck Builder’s Toolkit modules, ordinary Secret Lair drops, and collector sets are excluded.</p><div class="official-mtg-deck-results">{decks}</div>'
        small = f'{count} official deck product{"s" if count != 1 else ""} containing {escaped}'
    else:
        body = f'<p class="preconstructed-status official-mtg-empty">{catalogue["emptyState"]}</p>'
        small = '0'
    return f'<!-- CR_OFFICIAL_MTG_DECKS_START --><details class="preconstructed-archive official-mtg-decks" data-loaded="true" data-card="{html.escape(subject, quote=True)}" data-official-deck-count="{count}" data-catalogue-snapshot="{catalogue["snapshotDate"]}"><summary><span><strong>{catalogue["sectionLabel"]}</strong><small>{small}</small></span><span class="plus">+</span></summary><div class="preconstructed-body">{body}</div></details><!-- CR_OFFICIAL_MTG_DECKS_END -->'


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--catalogue', type=Path, default=None)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    root = args.root.resolve()
    catalogue_path = (args.catalogue or (Path(__file__).resolve().parents[1] / 'data' / 'official-mtg-deck-catalogue.json')).resolve()
    catalogue = json.loads(catalogue_path.read_text(encoding='utf-8'))
    products = {p['id']: p for p in catalogue['products']}
    inverted: dict[str, set[str]] = defaultdict(set)
    for product in catalogue['products']:
        for key in BOARD_KEYS:
            for uuid, count in product['zones'][key]:
                if int(count) > 0: inverted[str(uuid)].add(product['id'])
    names: dict[str, set[str]] = defaultdict(set)
    for uuid, card in catalogue['cards'].items():
        for name in (card.get('name'), card.get('faceName')):
            if name: names[norm(name)].add(uuid)

    changed, failures = 0, []
    for path in sorted(p for p in root.glob('*.html') if p.name != 'index.html'):
        raw = path.read_text(encoding='utf-8', errors='replace')
        match = ARTICLE_CARD_RE.search(raw)
        if not match:
            failures.append(f'{path.name}: missing data-article-card')
            continue
        subject = html.unescape(match.group(2)).strip()
        subject_uuids = names.get(norm(subject), set())
        ids = set()
        for uuid in subject_uuids: ids.update(inverted.get(uuid, set()))
        selected = sorted((products[pid] for pid in ids), key=lambda p: (p.get('releaseDate') or '9999', p.get('type') or '', p.get('name') or '', p.get('setCode') or '', p['id']))
        section = render_section(subject, selected, subject_uuids, catalogue)
        current = MARKED_RE.search(raw)
        if current:
            updated = raw[:current.start()] + section + raw[current.end():]
        else:
            legacy = LEGACY_RE.search(raw)
            if not legacy:
                failures.append(f'{path.name}: official section not found')
                continue
            updated = raw[:legacy.start()] + section + raw[legacy.end():]
        updated = LEGACY_SCRIPT_RE.sub('\n', updated)
        if updated != raw:
            changed += 1
            if not args.check: path.write_text(updated, encoding='utf-8')
    print(json.dumps({'articlesChanged': changed, 'failures': failures, 'mode': 'check' if args.check else 'write'}, indent=2))
    return 1 if failures or (args.check and changed) else 0


if __name__ == '__main__':
    raise SystemExit(main())
