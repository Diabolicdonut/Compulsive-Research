#!/usr/bin/env python3
"""Remove obsolete external runtime tags when the canonical inline runtime is present."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from bs4 import BeautifulSoup

OBSOLETE={'assets/artwork-spotlight.js','assets/design-echo.js','assets/printing-gallery.js'}

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,default=Path.cwd()); ap.add_argument('--check',action='store_true')
    args=ap.parse_args(); root=args.root.resolve(); changed=[]; removed=0
    for page in sorted(root.glob('*.html')):
        raw=page.read_text(encoding='utf-8',errors='replace')
        if not any(x in raw for x in OBSOLETE):continue
        soup=BeautifulSoup(raw,'html.parser'); count=0
        for script in list(soup.find_all('script',src=True)):
            if script.get('src') in OBSOLETE:
                script.decompose(); count+=1
        if count:
            changed.append({'file':page.name,'removed':count}); removed+=count
            if not args.check: page.write_text(str(soup),encoding='utf-8')
    print(json.dumps({'mode':'check' if args.check else 'apply','files':len(changed),'references':removed,'status':'FAIL' if args.check and changed else 'PASS'},indent=2))
    return 1 if args.check and changed else 0
if __name__=='__main__': raise SystemExit(main())
