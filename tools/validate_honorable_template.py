#!/usr/bin/env python3
"""Validate the reusable categorized Honorable Mention template and schema."""
from __future__ import annotations
import json,re,sys
from pathlib import Path
from bs4 import BeautifulSoup

def main()->int:
    root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
    t=root/'templates/honorable-article-shell.html'; s=root/'templates/honorable-article-content.schema.json'; errors=[]
    if not t.is_file(): errors.append('missing honorable-article-shell.html')
    if not s.is_file(): errors.append('missing honorable-article-content.schema.json')
    if errors: print('\n'.join(errors)); return 1
    raw=t.read_text(encoding='utf-8'); soup=BeautifulSoup(raw,'html.parser')
    required_placeholders=['{{CARD_NAME}}','{{CARD_SLUG}}','{{CATEGORY}}','{{THEMATIC_HEADLINE_WITHOUT_CARD_NAME}}','{{PREVIOUS_IN_CATEGORY_OR_PLACEHOLDER}}','{{NEXT_IN_CATEGORY_OR_PLACEHOLDER}}','{{SHARED_HONORABLE_STYLES}}','{{SHARED_HONORABLE_SCRIPTS}}']
    for x in required_placeholders:
        if x not in raw: errors.append(f'missing placeholder {x}')
    if re.search(r'honorable-\d{3}-|\d+\s+of\s+\d+',raw,re.I): errors.append('template contains global numbering')
    body=soup.body
    if not body or body.get('data-navigation-scope')!='category-local': errors.append('body navigation scope is not category-local')
    if not body or body.get('data-landing-anchor')!='honorable-{{CARD_SLUG}}': errors.append('stable landing anchor contract missing')
    for selector in ('nav.rank-nav','nav.end-nav'):
        nav=soup.select_one(selector)
        if not nav or nav.get('data-navigation-scope')!='category-local': errors.append(f'{selector} missing category-local scope')
    schema=json.loads(s.read_text(encoding='utf-8'))
    for field in ('slug','cardName','category','cardTypes','searchTerms','landingAnchor','landingReturnHref','navigationScope','navigation'):
        if field not in schema.get('required',[]): errors.append(f'schema does not require {field}')
    if schema.get('properties',{}).get('navigationScope',{}).get('const')!='category-local': errors.append('schema navigationScope is not fixed to category-local')
    pat=schema.get('properties',{}).get('slug',{}).get('pattern','')
    if '(?![0-9]{3}-)' not in pat and '(?!\\d{3}-)' not in pat: errors.append('schema does not reject numbered filenames')
    status='PASS' if not errors else 'FAIL'
    out={'status':status,'errors':errors}
    audit=root/'audit'; audit.mkdir(exist_ok=True); (audit/'honorable-template-validation.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out,indent=2)); return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
