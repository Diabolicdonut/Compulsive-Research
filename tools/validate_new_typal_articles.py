#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, re, sys
from pathlib import Path
from bs4 import BeautifulSoup

CARD_LIST = Path('/mnt/data/tribal_319_categories.json')
CARD_DATA = Path('/mnt/data/tribal_319_card_data.json')


def norm(s: str) -> str:
    return re.sub(r'\s+', ' ', (s or '')).strip()


def deck_total(col) -> int:
    total = 0
    for row in col.select('.row'):
        q = row.select_one('.qty')
        if q:
            try: total += int(norm(q.get_text()))
            except ValueError: pass
    return total


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('root', nargs='?', default='.')
    args = ap.parse_args()
    root = Path(args.root).resolve()
    archive = json.loads((root/'archive-manifest.json').read_text(encoding='utf-8'))
    hm_by_card = {x['card']: x for x in archive['honorable_mentions']}
    wanted_by_cat = json.loads(CARD_LIST.read_text(encoding='utf-8'))
    wanted = [(cat, card) for cat, cards in wanted_by_cat.items() for card in cards]
    data_by_name = json.loads(CARD_DATA.read_text(encoding='utf-8'))['cards']
    rows=[]; errors=[]; seen_headlines={}
    for expected_cat, card in wanted:
        entry = hm_by_card.get(card)
        item_errors=[]
        if not entry:
            errors.append(f'{card}: absent from archive-manifest.json')
            continue
        filename=entry['file']; path=root/filename
        if not path.exists():
            errors.append(f'{card}: missing {filename}')
            continue
        if re.match(r'honorable-\d{3}-', filename):
            item_errors.append('numbered filename')
        soup=BeautifulSoup(path.read_text(encoding='utf-8',errors='replace'),'html.parser')
        body=soup.body; h1=soup.select_one('.hero h1'); hero=soup.select_one('img.hero-media')
        headline=norm(h1.get_text(' ',strip=True) if h1 else '')
        if not body or body.get('data-article-card') != card: item_errors.append('body card mismatch')
        if not body or body.get('data-honorable-category') != expected_cat: item_errors.append('body category mismatch')
        if not headline: item_errors.append('missing headline')
        if card.casefold() in headline.casefold(): item_errors.append('headline contains full card name')
        key=headline.casefold()
        if headline and key in seen_headlines: item_errors.append(f'duplicate headline with {seen_headlines[key]}')
        elif headline: seen_headlines[key]=card
        if not hero: item_errors.append('missing hero image')
        else:
            src=hero.get('src',''); alt=hero.get('alt','')
            expected_id=(data_by_name.get(card) or {}).get('original',{}).get('scryfallId','')
            if expected_id and expected_id not in src: item_errors.append('hero Scryfall ID mismatch')
            if card.casefold() not in alt.casefold(): item_errors.append('hero alt mismatch')
        header=soup.select_one('header.hero')
        if not header or header.get('data-hero-card') != card: item_errors.append('hero identity mismatch')
        focus=f'honorable-{entry["landing_anchor"].removeprefix("honorable-")}'
        ret=soup.select_one('.archive-link')
        if not ret or ret.get('href') != f'index.html?focus={focus}#{focus}': item_errors.append('landing return mismatch')
        # Category-local previous/next contract, top and bottom.
        expected_prev=entry.get('previous',{}).get('file') if entry.get('previous') else None
        expected_next=entry.get('next',{}).get('file') if entry.get('next') else None
        for nav_sel in ('.rank-nav','.end-nav'):
            nav=soup.select_one(nav_sel)
            if not nav: item_errors.append(f'missing {nav_sel}'); continue
            hrefs=[a.get('href') for a in nav.find_all('a',href=True)]
            expected=[x for x in (expected_prev,expected_next) if x]
            if hrefs != expected: item_errors.append(f'{nav_sel} neighbor mismatch')
        spot=soup.select('.artwork-spotlight')
        if len(spot)!=1: item_errors.append(f'artwork spotlight count {len(spot)}')
        echo=soup.select('.canonical-inline-image')
        if len(echo)!=1: item_errors.append(f'design echo count {len(echo)}')
        # Documentary deck evidence is optional; synthetic study shells are forbidden.
        decks=soup.select('#decklists details.deck')
        deck_totals=[]
        for d in decks:
            kind=(d.get('data-deck-kind') or '').strip()
            if kind == 'editorial-study' or 'Editorial study shell' in d.get_text(' ',strip=True):
                item_errors.append('synthetic editorial study deck present')
            if kind not in {'tournament-registration','official-digital-deck','curated-example'}:
                item_errors.append(f'unsupported deck kind {kind or "(missing)"}')
            cols=d.select('.deck-columns > .deck-col')
            if len(cols)<1:
                item_errors.append('deck columns missing'); continue
            main=deck_total(cols[0]); side=deck_total(cols[1]) if len(cols)>1 else 0
            deck_totals.append((main,side))
        if not decks and not soup.select_one('#decklists .deck-research-status'):
            item_errors.append('missing documentary deck or research-status notice')
        gallery=soup.select_one('.canonical-printing-gallery')
        figures=gallery.select('figure.printing') if gallery else []
        if not gallery: item_errors.append('missing printing gallery')
        if not (1 <= len(figures) <= 12): item_errors.append(f'printing count {len(figures)}')
        if gallery and gallery.get('data-card') != card: item_errors.append('gallery card mismatch')
        for fig in figures:
            if fig.get('data-card-name') != card: item_errors.append('printing card mismatch'); break
        expected_id=(data_by_name.get(card) or {}).get('original',{}).get('scryfallId','')
        first_id=figures[0].get('data-scryfall-id','') if figures else ''
        if expected_id and first_id != expected_id: item_errors.append('original printing ID mismatch')
        sources=soup.select('#printings h3 + ul.sources li')
        if not sources: item_errors.append('sources missing')
        # Approximate visible main text count for editorial QA.
        main_el=soup.find('main') or soup.select_one('.article-shell') or soup
        clone=BeautifulSoup(str(main_el),'html.parser')
        for x in clone.select('script,style,nav,pre'):
            x.decompose()
        word_count=len(re.findall(r"\b[\w’'-]+\b",clone.get_text(' ',strip=True)))
        status='PASS' if not item_errors else 'FAIL'
        rows.append({
            'card':card,'category':expected_cat,'filename':filename,'headline':headline,
            'word_count':word_count,'printing_count':len(figures),'deck_count':len(decks),
            'deck_totals':' | '.join(f'{a}/{b}' for a,b in deck_totals),
            'status':status,'findings':' ; '.join(item_errors)
        })
        errors.extend(f'{card}: {x}' for x in item_errors)
    audit=root/'audit'; audit.mkdir(exist_ok=True)
    csv_path=audit/'new-typal-articles-validation.csv'
    with csv_path.open('w',newline='',encoding='utf-8') as f:
        fields=['card','category','filename','headline','word_count','printing_count','deck_count','deck_totals','status','findings']
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    summary={
        'status':'PASS' if not errors and len(rows)==319 else 'FAIL',
        'expectedArticles':319,'validatedArticles':len(rows),
        'passed':sum(r['status']=='PASS' for r in rows),'failed':sum(r['status']=='FAIL' for r in rows),
        'uniqueHeadlines':len(seen_headlines),'errors':errors
    }
    (audit/'new-typal-articles-validation.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
    md=[
        '# New typal Honorable Mention validation', '',
        f"**Status:** {summary['status']}", '',
        f"- Expected articles: {summary['expectedArticles']}",
        f"- Validated articles: {summary['validatedArticles']}",
        f"- Passed: {summary['passed']}",
        f"- Failed: {summary['failed']}",
        f"- Unique thematic headlines: {summary['uniqueHeadlines']}",
        '- Required deck structure: sourced documentary decks when available; otherwise an explicit research-status notice. Synthetic study shells are forbidden.',
        '- Required media structure: one card-specific hero, one original-art spotlight, one canonical Design Echo',
        '- Navigation boundary: immediate neighbors inside the same category only', '',
    ]
    if errors:
        md += ['## Findings',''] + [f'- {e}' for e in errors]
    else:
        md += ['No validation findings were recorded.']
    (audit/'new-typal-articles-validation.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    return 0 if summary['status']=='PASS' else 1

if __name__=='__main__':
    raise SystemExit(main())
