#!/usr/bin/env python3
"""Build archive-manifest.json from the landing page.

Numbered entries retain global sequential navigation. Honorable Mentions use stable,
unnumbered filenames and previous/next navigation scoped to their landing-page
subcategory.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from bs4 import BeautifulSoup

def text(node,selector,default=''):
    found=node.select_one(selector) if node else None
    return found.get_text(' ',strip=True) if found else default

def main()->int:
    parser=argparse.ArgumentParser(); parser.add_argument('root',nargs='?',default=Path(__file__).resolve().parents[1],type=Path); parser.add_argument('--output',type=Path)
    args=parser.parse_args(); root=args.root.resolve(); output=args.output or root/'archive-manifest.json'
    soup=BeautifulSoup((root/'index.html').read_text(encoding='utf-8'),'html.parser')
    waves={}
    for panel in soup.select('details.wave-panel[id]'):
        wave_id=panel.get('id',''); eyebrow=text(panel,'summary .eyebrow')
        number_match=re.search(r'Wave\s+(\d+)',eyebrow,re.I); range_match=re.search(r'Entries\s+(\d+)\s*[–-]\s*(\d+)',eyebrow,re.I)
        waves[wave_id]={'id':wave_id,'number':int(number_match.group(1)) if number_match else None,'entry_start':int(range_match.group(1)) if range_match else None,'entry_end':int(range_match.group(2)) if range_match else None,'title':text(panel,'summary h3'),'description':text(panel,'summary p')}
    entries=[]
    for node in soup.select("[id^='entry-']"):
        anchor=node.get('id',''); match=re.fullmatch(r'entry-(\d{3,4})',anchor)
        if not match or not node.select_one('.entry-name'): continue
        number=int(match.group(1)); panel=node.find_parent('details',class_='wave-panel'); wave_id=panel.get('id') if panel else None; href=node.get('href') if node.name=='a' else None
        entries.append({'entry':number,'landing_anchor':anchor,'card':text(node,'.entry-name'),'lens':text(node,'.entry-lens'),'status':node.get('data-status','unknown'),'file':href,'article_present':bool(href and (root/href).is_file()),'wave':waves.get(wave_id),'landing_return_href':f'index.html?focus={anchor}#{anchor}'})
    entries.sort(key=lambda x:x['entry']); bynum={x['entry']:x for x in entries}
    for item in entries:
        prev=bynum.get(item['entry']-1); nxt=bynum.get(item['entry']+1)
        item['previous']=None if not prev else {'entry':prev['entry'],'card':prev['card'],'landing_anchor':prev['landing_anchor'],'href':prev['landing_return_href'],'file':prev['file']}
        item['next']=None if not nxt else {'entry':nxt['entry'],'card':nxt['card'],'landing_anchor':nxt['landing_anchor'],'href':nxt['landing_return_href'],'file':nxt['file']}
    honorable=[]; categories=[]
    for order,panel in enumerate(soup.select('details.honorable-category-panel[data-honorable-category]')):
        category=panel.get('data-honorable-category','').strip() or text(panel,'summary h4')
        catrec={'name':category,'id':panel.get('id'),'order':order,'description':text(panel,'summary p'),'articles':[]}
        for node in panel.select('a.honorable-entry[id]'):
            href=node.get('href'); card=text(node,'.honorable-name'); anchor=node.get('id')
            rec={'category':category,'category_id':catrec['id'],'landing_anchor':anchor,'card':card,'file':href,'card_types':(node.get('data-card-types') or '').split(),'article_present':bool(href and (root/href).is_file()),'landing_return_href':f'index.html?focus={anchor}#{anchor}'}
            catrec['articles'].append(rec); honorable.append(rec)
        for i,rec in enumerate(catrec['articles']):
            prev=catrec['articles'][i-1] if i else None; nxt=catrec['articles'][i+1] if i+1<len(catrec['articles']) else None
            rec['previous']=None if not prev else {'category':category,'card':prev['card'],'file':prev['file'],'landing_anchor':prev['landing_anchor']}
            rec['next']=None if not nxt else {'category':category,'card':nxt['card'],'file':nxt['file'],'landing_anchor':nxt['landing_anchor']}
        catrec['article_count']=len(catrec['articles']); categories.append(catrec)
    payload={'schema_version':3,'source':'index.html','canonical_article':'250-eternal-dragon.html','numbered_entry_count':len(entries),'present_numbered_article_count':sum(bool(x['article_present']) for x in entries),'honorable_mention_count':len(honorable),'honorable_category_count':len(categories),'honorable_navigation_scope':'category-local','waves':sorted(waves.values(),key=lambda x:x['number'] or 0),'entries':entries,'honorable_categories':categories,'honorable_mentions':honorable}
    output.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    data_payload={'schemaVersion':3,'generatedOn':'2026-08-01','architecture':'stable unnumbered filenames with category-local navigation','navigationScope':'category-local','totalHonorableMentions':len(honorable),'categoryCount':len(categories),'categories':categories}
    data_path=root/'data/honorable-categories.json'; data_path.parent.mkdir(parents=True,exist_ok=True); data_path.write_text(json.dumps(data_payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Wrote {output} and {data_path} with {len(entries)} numbered entries and {len(honorable)} categorized Honorable Mentions'); return 0
if __name__=='__main__': raise SystemExit(main())
