#!/usr/bin/env python3
"""Verify that every local HTML asset reference resolves inside the production root."""
from __future__ import annotations
import argparse, json, re
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit, unquote

REF_RE=re.compile(r'<(?P<tag>script|img|link|source|video|audio|iframe)\b[^>]*?\b(?P<attr>src|href)=["\'](?P<value>[^"\']+)["\']',re.I)
SKIP=('http:','https:','data:','mailto:','tel:','javascript:')

def resolve(page:Path,value:str,root:Path):
    value=value.strip()
    if not value or value.startswith('#') or value.lower().startswith(SKIP):return None
    path=unquote(urlsplit(value).path)
    if not path:return None
    return (root/path.lstrip('/')).resolve() if path.startswith('/') else (page.parent/path).resolve()

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path.cwd());ap.add_argument('--output',type=Path,default=None)
    a=ap.parse_args();root=a.root.resolve();issues=[];checked=0;pages=sorted(root.glob('*.html'))
    for page in pages:
        raw=page.read_text(encoding='utf-8',errors='replace')
        for m in REF_RE.finditer(raw):
            value=m.group('value');target=resolve(page,value,root)
            if target is None:continue
            checked+=1
            try:target.relative_to(root)
            except ValueError:issues.append({'file':page.name,'code':'OUTSIDE_ROOT','reference':value});continue
            if not target.exists():issues.append({'file':page.name,'code':'MISSING_LOCAL_ASSET','reference':value,'resolved':str(target.relative_to(root))})
    payload={'root':str(root),'pages':len(pages),'localReferencesChecked':checked,'status':'PASS' if not issues else 'FAIL','issueCounts':dict(Counter(i['code'] for i in issues)),'issues':issues}
    out=a.output or root/'audit/local-assets.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:payload[k] for k in ['pages','localReferencesChecked','status','issueCounts']},indent=2))
    return 1 if issues else 0
if __name__=='__main__':raise SystemExit(main())
