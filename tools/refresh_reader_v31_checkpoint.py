#!/usr/bin/env python3
"""Bind a completed Reader V3.1 checkpoint to its current HTML and baseline.

This refreshes review metadata; it never rewrites an article or an earlier ledger.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import subprocess

from bs4 import BeautifulSoup
from reader_experience_v3 import editorial_word_count, reading_time_minutes
from validate_reader_experience_v3 import opening_prefix

ROOT = Path(__file__).resolve().parents[1]


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def collect(start, end, baseline):
    rows, stories = [], []
    specs_path = ROOT / f'research-dossiers/reader-v31-{start:03d}-{end:03d}/stories.json'
    specs = {x['entry']: x for x in json.loads(specs_path.read_text())}
    for n in range(start, end + 1):
        path, = ROOT.glob(f'{n:03d}-*.html')
        soup = BeautifulSoup(path.read_text(), 'lxml')
        v = soup.select_one('#opening > .play-vignette')
        if not v or soup.body.get('data-reader-experience') != 'v3':
            raise ValueError(f'{path.name}: incomplete Reader V3.1 article')
        old = subprocess.check_output(['git', 'show', f'{baseline}:{path.name}'], cwd=ROOT)
        story = v.find('p').get_text(' ', strip=True)
        words = editorial_word_count(soup)
        ref = v['data-vignette-deck-reference']
        row = dict(entry=n, file=path.name, card=soup.body['data-article-card'],
                   storyTitle=v.find('h3').get_text(' ', strip=True),
                   storyWords=len(re.findall(r"\b[\w’'-]+\b", story)),
                   openingMode=v['data-vignette-opening'], normalizedOpeningSixWords=opening_prefix(story),
                   era=v['data-vignette-era'], matchup=v['data-vignette-matchup'], deckReference=ref,
                   deckReferenceFoundInArticle=ref in {x.get_text(' ', strip=True) for x in soup.select('details.deck summary strong')},
                   scenario=v['data-vignette-scenario'], articleEditorialWords=words,
                   readTimeMinutes=reading_time_minutes(words),
                   originalSha256=hashlib.sha256(old).hexdigest(),
                   finalSha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                   storyBeforeStrategicLegacy=v.parent.find_next_sibling('section').get('id') == 'strategic-legacy-brief')
        rows.append(row)
        story_record = dict(row, story=story, manualReview=specs[n]['review'],
                            payments=json.loads(v.select_one('script.vignette-mana-data').string),
                            review=json.loads(v.select_one('script.vignette-review-data').string))
        turn_ledger = v.select_one('script.vignette-sequence-data')
        if turn_ledger:
            story_record['sequenceLedger'] = json.loads(turn_ledger.string)
        stories.append(story_record)
    return rows, stories


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--start', type=int, default=51)
    ap.add_argument('--end', type=int, default=60)
    ap.add_argument('--baseline', default='d70eb643b7bcb4fcbb3b5c5c95b142ff4d21f498')
    args = ap.parse_args()
    scope = f'{args.start:03d}-{args.end:03d}'
    rows, stories = collect(args.start, args.end, args.baseline)
    if not all(r['deckReferenceFoundInArticle'] and r['storyBeforeStrategicLegacy'] for r in rows):
        raise ValueError('Incomplete deck binding or story order')
    summary = dict(articleCount=len(rows), storyCount=len(stories),
                   uniqueNormalizedSixWordOpenings=len({r['normalizedOpeningSixWords'] for r in rows}),
                   storyWordRange=[min(r['storyWords'] for r in rows), max(r['storyWords'] for r in rows)],
                   editorialWordTotal=sum(r['articleEditorialWords'] for r in rows),
                   readTimeRangeMinutes=[min(r['readTimeMinutes'] for r in rows), max(r['readTimeMinutes'] for r in rows)])
    checkpoint = dict(checkpointId=f'reader-v31-{scope}-2026-10-16', range=scope, date='2026-10-16',
                      baselineCommit=args.baseline, nextArticle=args.end + 1, metrics=summary, records=rows,
                      reviewScope='Reader layout, complete visible prose, new gameplay stories, dated claims and documentary deck references. Retained archive-wide warning queues are not closed by this checkpoint.')
    write_json(ROOT / f'validation/reader-v3.1-entries-{scope}-metrics.json', checkpoint)
    lines = [f'# Reader V3.1 entries {scope}', '',
             f'- Articles and stories: {len(rows)}; distinct six-word story openings: {summary["uniqueNormalizedSixWordOpenings"]}.',
             f'- Editorial words: {summary["editorialWordTotal"]:,}; reading time at 200 words/minute.', '',
             '| Entry | Card | Story | Story words | Editorial words | Minutes |',
             '|---:|---|---|---:|---:|---:|']
    lines += [f'| {r["entry"]:03d} | {r["card"]} | {r["storyTitle"]} | {r["storyWords"]} | {r["articleEditorialWords"]} | {r["readTimeMinutes"]} |' for r in rows]
    (ROOT / f'validation/reader-v3.1-entries-{scope}-metrics.md').write_text('\n'.join(lines) + '\n')
    write_json(ROOT / f'research-dossiers/READER-V3.1-NUMBERED-WAVE-02-STORY-LEDGER.json',
               dict(range=scope, method='Representative reconstructions, not match transcripts or eyewitness quotations.', stories=stories))
    ledger_path = ROOT / 'READER-V3.1-MIGRATION-LEDGER.json'
    ledger = json.loads(ledger_path.read_text())
    continuations = [x for x in ledger.get('continuationCheckpoints', []) if x.get('range') != scope]
    continuations.append(checkpoint)
    ledger['continuationCheckpoints'] = continuations
    ledger['latestCheckpoint'] = checkpoint['checkpointId']
    ledger['nextAction'] = f'Reader V3.1 entries {args.end + 1:03d}-{args.end + 10:03d}; begin {args.end + 1:03d}.'
    write_json(ledger_path, ledger)
    body = ''.join('<tr><td>'+str(r['entry'])+'</td><td><a href="'+html.escape(r['file'],quote=True)+'">'+html.escape(r['card'])+'</a></td><td>'+html.escape(r['storyTitle'])+'</td><td>'+str(r['storyWords'])+'</td><td>'+str(r['readTimeMinutes'])+'</td></tr>' for r in rows)
    (ROOT / f'READER-V3.1-ENTRIES-{scope}-REVIEW-INDEX.html').write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>Reader V3.1 {scope} review index</title><body><h1>Reader V3.1 {scope}</h1>'
        '<p>Review metadata. Stories are representative reconstructions, not recorded matches.</p>'
        '<table><thead><tr><th>Entry</th><th>Card</th><th>Story</th><th>Story words</th><th>Minutes</th></tr></thead><tbody>'+body+'</tbody></table></body></html>')
    print(f'Refreshed {scope}: {summary}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
