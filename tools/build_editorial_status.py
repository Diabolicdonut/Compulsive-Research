#!/usr/bin/env python3
"""Create separate mechanical/editorial/research status records for active pages."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from bs4 import BeautifulSoup

BENCHMARKS={'001-black-lotus.html','250-eternal-dragon.html','605-grief.html'}

def classify(path:Path, raw:str)->tuple[str,str,list[str]]:
    notes=[]
    if re.search(r'data-editorial-status=[\"\']reviewed-v2[\"\']', raw, re.I):
        return 'reviewed-v2','complete',['Page is explicitly approved under Editorial V2.']
    if path.name in BENCHMARKS:
        return 'benchmark','complete',['Approved benchmark or manually rebuilt exemplar.']
    m=re.match(r'^(\d{3,4})-',path.name)
    if m:
        entry=int(m.group(1))
        if entry>=401:
            notes.append('Generated continuation cohort requires card-specific historical rewrite.')
            return 'rewrite-required','scaffold',notes
        notes.append('Pre-continuation article requires evidence and duplication audit.')
        return 'audit-required','draft',notes
    # Honorable Mentions are intentionally not presumed complete.
    if 'metadata-grounded dossier' in raw.lower() or 'editorial study shell' in raw.lower():
        notes.append('Generic dossier/study-shell language detected.')
        return 'rewrite-required','scaffold',notes
    notes.append('Honorable Mention requires class-specific editorial review.')
    return 'audit-required','draft',notes

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,default=Path.cwd()); ap.add_argument('--apply-body-attributes',action='store_true')
    args=ap.parse_args(); root=args.root.resolve(); records=[]
    for path in sorted(root.glob('*.html')):
        if path.name=='index.html':continue
        raw=path.read_text(encoding='utf-8',errors='replace')
        soup=BeautifulSoup(raw,'html.parser'); body=soup.body
        card=(body.get('data-article-card') if body else None) or (soup.title.get_text().split(':')[0] if soup.title else path.stem)
        editorial,research,notes=classify(path,raw)
        records.append({'file':path.name,'cardName':card,'mechanicalStatus':'unassessed','editorialStatus':editorial,'researchStatus':research,'releaseStatus':'production','notes':notes})
        if args.apply_body_attributes and body:
            body['data-editorial-status']=editorial; body['data-research-status']=research; body['data-editorial-contract']='v2'
            path.write_text(str(soup),encoding='utf-8')
    payload={'schemaVersion':'2.0','generatedOn':'2026-08-02','records':records,'counts':{k:sum(r['editorialStatus']==k for r in records) for k in ['benchmark','reviewed-v2','audit-required','rewrite-required']}}
    out=root/'data/editorial-status.json'; out.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'articles':len(records),'counts':payload['counts'],'bodyAttributesApplied':args.apply_body_attributes},indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
