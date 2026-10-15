#!/usr/bin/env python3
"""Remove synthetic editorial-study decks and add an honest documentary-gap notice.

The migration uses bounded HTML patterns because the legacy deck components never
nest `<details>` elements. This avoids reparsing more than a thousand very large pages.
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

NOTICE='<p class="deck-research-status">No verified historical tournament registration is currently included in this article. The documentary archive remains open for sourced additions.</p>'
STUDY_RE=re.compile(r'<details\b(?=[^>]*\bdata-deck-kind=["\']editorial-study["\'])[^>]*>.*?</details>',re.I|re.S)
# Some pre-canonical pages identify the shell only through visible provenance.
STUDY_FALLBACK_RE=re.compile(r'<details\b[^>]*class=["\'][^"\']*\bdeck\b[^"\']*["\'][^>]*>.*?Editorial study shell.*?</details>',re.I|re.S)
SECTION_RE=re.compile(r'(<section\b[^>]*id=["\']decklists["\'][^>]*>)(.*?)(</section>)',re.I|re.S)
DOC_RE=re.compile(r'data-deck-kind=["\'](?:tournament-registration|official-digital-deck|curated-example)["\']',re.I)
LEGACY_INTRO_RE=re.compile(r'<p>The original project standard favors documented tournament registrations\..*?</p>\s*<div class="archive-standard-note">.*?</div>',re.I|re.S)
GENERIC_STUDY_P_RE=re.compile(r'<p>[^<]*(?:editorial (?:study|exercise)|teaching (?:model|shell))[^<]*</p>',re.I)
REPLACEMENT='<p>This archive includes only sourced historical registrations, documented official digital lists, or reviewed curated examples. Unverified reconstructions are omitted.</p>'

def process(raw:str):
    new,n1=STUDY_RE.subn('',raw)
    new,n2=STUDY_FALLBACK_RE.subn('',new)
    removed=n1+n2
    if not removed:return raw,0
    new=LEGACY_INTRO_RE.sub(REPLACEMENT,new)
    def fix_section(m):
        start,body,end=m.groups()
        body=GENERIC_STUDY_P_RE.sub(REPLACEMENT,body)
        # Avoid duplicate replacement paragraphs from broad matching.
        body=re.sub(r'(?:'+re.escape(REPLACEMENT)+r'\s*){2,}',REPLACEMENT,body)
        body=re.sub(r'<p class=["\']deck-research-status["\']>.*?</p>','',body,flags=re.I|re.S)
        if not DOC_RE.search(body):
            archive=re.search(r'<div\b[^>]*class=["\'][^"\']*\bdeck-archive\b[^"\']*["\'][^>]*>',body,re.I)
            if archive: body=body[:archive.start()]+NOTICE+body[archive.start():]
            else: body=NOTICE+body
        return start+body+end
    new=SECTION_RE.sub(fix_section,new,count=1)
    return new,removed

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,default=Path.cwd()); ap.add_argument('--check',action='store_true'); ap.add_argument('--report',type=Path,default=None)
    args=ap.parse_args(); root=args.root.resolve(); results=[]
    for page in sorted(root.glob('*.html')):
        if page.name=='index.html':continue
        raw=page.read_text(encoding='utf-8',errors='replace')
        if 'editorial-study' not in raw and 'Editorial study shell' not in raw:continue
        new,removed=process(raw)
        if removed:
            results.append({'file':page.name,'removed':removed})
            if not args.check:page.write_text(new,encoding='utf-8')
    payload={'mode':'check' if args.check else 'apply','affectedFiles':len(results),'removedDecks':sum(r['removed'] for r in results),'status':'FAIL' if args.check and results else 'PASS','results':results}
    report=args.report or root/'audit/editorial-study-deck-removal.json'; report.parent.mkdir(parents=True,exist_ok=True); report.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:payload[k] for k in ['mode','affectedFiles','removedDecks','status']},indent=2))
    return 1 if args.check and results else 0
if __name__=='__main__':raise SystemExit(main())
