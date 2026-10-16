#!/usr/bin/env python3
"""Validate the review records and research schemas for entries 051–060."""
from pathlib import Path
import hashlib
import json

from bs4 import BeautifulSoup
from jsonschema import Draft202012Validator, FormatChecker
from reader_experience_v3 import editorial_word_count, reading_time_minutes
from validate_deck_archives import inspect

ROOT = Path(__file__).resolve().parents[1]


def main():
    metrics = json.loads((ROOT/'validation/reader-v3.1-entries-051-060-metrics.json').read_text())
    ledger = json.loads((ROOT/'research-dossiers/READER-V3.1-NUMBERED-WAVE-02-STORY-LEDGER.json').read_text())
    schema = json.loads((ROOT/'templates/research-dossier-v2.schema.json').read_text())
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = []
    if [x['entry'] for x in metrics['records']] != list(range(51,61)):
        errors.append('Metrics must contain exactly entries 051–060')
    stories = {x['entry']:x for x in ledger['stories']}
    for row in metrics['records']:
        path = ROOT/row['file']
        soup = BeautifulSoup(path.read_text(),'lxml')
        story = soup.select_one('#opening > .play-vignette')
        if hashlib.sha256(path.read_bytes()).hexdigest() != row['finalSha256']:
            errors.append(f'{path.name}: metrics hash differs from article')
        if editorial_word_count(soup) != row['articleEditorialWords']:
            errors.append(f'{path.name}: stale word count')
        if reading_time_minutes(editorial_word_count(soup)) != row['readTimeMinutes']:
            errors.append(f'{path.name}: stale reading time')
        record = stories.get(row['entry'],{})
        if record.get('story') != story.find('p').get_text(' ',strip=True):
            errors.append(f'{path.name}: story ledger differs from visible story')
        if record.get('payments') != json.loads(story.select_one('.vignette-mana-data').string):
            errors.append(f'{path.name}: payment ledger differs from article')
        dossier_path = ROOT/'research-dossiers/numbered-wave-02'/path.with_suffix('.json').name
        dossier = json.loads(dossier_path.read_text())
        errors.extend(f'{dossier_path.name}: {e.message}' for e in validator.iter_errors(dossier))
        errors.extend(f'{path.name}: {e["code"]}' for e in inspect(path)['issues'] if e['severity']=='FAIL')
    result = {'status':'FAIL' if errors else 'PASS','articles':len(metrics['records']),'dossiers':len(metrics['records']),'errors':errors}
    print(json.dumps(result,indent=2))
    return 1 if errors else 0


if __name__=='__main__':
    raise SystemExit(main())
