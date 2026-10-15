#!/usr/bin/env python3
"""Confirm that every article already contains one canonical Design Echo section.

Legacy completion is intentionally no longer generative.  New articles must be
built from the canonical template; existing articles were migrated once and
are now protected from a second tool rebuilding the component with obsolete
image URLs or geometry.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]

def main()->int:
    parser=argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    failures=[]; articles=0; panels=0
    for path in sorted(ROOT.glob('*.html')):
        if path.name=='index.html': continue
        articles+=1
        soup=BeautifulSoup(path.read_text(encoding='utf-8'),'html.parser')
        sections=soup.select('section.design-echo-section')
        if not sections:
            failures.append(f'{path.name}: canonical Design Echo section missing')
            continue
        section_panels=0
        for section in sections:
            found=section.select('.inline-image.canonical-inline-image')
            section_panels+=len(found)
            if not found:
                failures.append(f"{path.name} section #{section.get('id','?')}: canonical panel missing")
        panels+=section_panels
    report={'articles':articles,'panels':panels,'failures':failures}
    (ROOT/'audit'/'design-echo-completion-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
    return 1 if failures else 0

if __name__=='__main__':
    raise SystemExit(main())
