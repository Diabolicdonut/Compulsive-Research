#!/usr/bin/env python3
"""Check the complete canonical corpus's local resources and navigation targets."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from lxml import html

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'audit/internal-navigation')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'archive-manifest.json').read_text())
    records = manifest['entries'] + manifest['honorable_mentions']
    by_file = {r['file']: r for r in records}
    by_anchor = {r['landing_anchor']: r['file'] for r in records}
    failures, links, ids = [], [], {}
    pages = [ROOT / 'index.html'] + [ROOT / r['file'] for r in records]
    landing = html.fromstring(pages[0].read_text(encoding='utf-8'))

    def destination(href: str) -> str | None:
        url = urlsplit(href)
        if url.scheme or url.netloc:
            return None
        if url.path == 'index.html':
            return by_anchor.get(unquote(url.fragment))
        return unquote(url.path) if url.path in by_file else None

    for path in pages:
        tree = html.fromstring(path.read_text(encoding='utf-8'))
        ids[path] = Counter(tree.xpath('//@id'))
        for href in tree.xpath('//a[@href]/@href'):
            url = urlsplit(href)
            if url.scheme or url.netloc:
                continue
            target = (path.parent / unquote(url.path or path.name)).resolve()
            links.append((path.name, href, target, unquote(url.fragment)))
        for value in tree.xpath('//*[@src]/@src | //*[@href]/@href'):
            url = urlsplit(value)
            if url.scheme or url.netloc or not url.path:
                continue
            if not (path.parent / unquote(url.path)).exists():
                failures.append([path.name, 'missing local resource', value])
        if path.name == 'index.html':
            continue
        record = by_file[path.name]
        back = tree.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," archive-link ")]/@href')
        if back != [record['landing_return_href']]:
            failures.append([path.name, 'incorrect return link', back])
        rows = landing.xpath('//*[@id=$anchor]', anchor=record['landing_anchor'])
        if len(rows) != 1 or record['file'] not in rows[0].xpath('self::a/@href | .//a/@href'):
            failures.append([path.name, 'incorrect landing row'])
        expected = [record[k]['file'] for k in ('previous', 'next') if record.get(k)]
        for cls in ('rank-nav', 'end-nav'):
            for nav in tree.xpath('//nav[contains(concat(" ",normalize-space(@class)," "),$cls)]', cls=' ' + cls + ' '):
                hrefs = nav.xpath('.//a/@href')
                actual = [destination(href) for href in hrefs]
                actual = [value for value in actual if value and value != path.name]
                if actual != expected:
                    failures.append([path.name, 'incorrect ' + cls, hrefs, expected])

    for name, href, target, fragment in links:
        if not target.exists():
            failures.append([name, 'missing link target', href])
        elif fragment and target in ids and ids[target][fragment] != 1:
            failures.append([name, 'nonunique or missing fragment', href, ids[target][fragment]])
    retired = [p.name for p in ROOT.glob('honorable-*.html') if re.match(r'honorable-\d{3}-', p.name)]
    if retired:
        failures.append(['corpus', 'retired numbered Honorable Mentions', retired])
    report = {
        'status': 'FAIL' if failures else 'PASS', 'pages': len(pages),
        'numbered': len(manifest['entries']), 'honorable': len(manifest['honorable_mentions']),
        'categories': manifest['honorable_category_count'], 'localLinksChecked': len(links),
        'retiredFiles': len(retired), 'failures': failures,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / 'navigation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())
