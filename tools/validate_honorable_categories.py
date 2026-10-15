#!/usr/bin/env python3
"""Validate the category-based, unnumbered Honorable Mentions archive."""
from __future__ import annotations
import argparse,csv,json,re,sys
from pathlib import Path
from collections import defaultdict
from bs4 import BeautifulSoup

UNNUMBERED_RE=re.compile(r'^honorable-(?!\d{3}-)([a-z0-9][a-z0-9-]*)\.html$')
NUMBERED_RE=re.compile(r'^honorable-\d{3}-.+\.html$')
VISIBLE_ORDINAL_RE=re.compile(r'\bHonorable(?: Mention)?\s+\d+\b|\b\d+\s+of\s+\d+\b',re.I)
VALID_TYPES={'creature','artifact','enchantment','instant','sorcery','land','planeswalker','battle','kindred'}

def text(node,selector,default=''):
    n=node.select_one(selector) if node else None
    return n.get_text(' ',strip=True) if n else default

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',type=Path,default=Path(__file__).resolve().parents[1]); ap.add_argument('--csv',type=Path); ap.add_argument('--json',type=Path)
    args=ap.parse_args(); root=args.root.resolve(); issues=[]; rows=[]
    def add(file,code,msg,severity='ERROR'): issues.append({'severity':severity,'file':file,'code':code,'message':msg})
    old=list(root.glob('honorable-[0-9][0-9][0-9]-*.html'))
    for p in old: add(p.name,'NUMBERED_FILENAME','Numbered Honorable Mention filename remains')
    files=sorted(p for p in root.glob('honorable-*.html') if UNNUMBERED_RE.match(p.name))
    index_path=root/'index.html'
    if not index_path.is_file(): add('index.html','MISSING_INDEX','Landing page missing'); soup=None
    else: soup=BeautifulSoup(index_path.read_text(encoding='utf-8',errors='replace'),'lxml')
    landing={}; category_order=[]; category_members=defaultdict(list)
    if soup:
        panels=soup.select('details.honorable-category-panel[data-honorable-category]')
        if not panels: add('index.html','NO_CATEGORIES','No Honorable Mention category panels found')
        for panel in panels:
            cat=panel.get('data-honorable-category','').strip(); category_order.append(cat)
            entries=panel.select(':scope > .honorable-list > a.honorable-entry') or panel.select('a.honorable-entry')
            if not entries: add('index.html','EMPTY_CATEGORY',f'Category {cat!r} has no entries')
            for a in entries:
                href=a.get('href',''); name=text(a,'.honorable-name'); anchor=a.get('id',''); types=set((a.get('data-card-types') or '').split())
                if not href or not (root/href).is_file(): add('index.html','BROKEN_HREF',f'{name}: missing file {href}')
                if NUMBERED_RE.match(href): add('index.html','NUMBERED_HREF',f'{name}: numbered href {href}')
                if href in landing: add('index.html','DUPLICATE_HREF',f'{href} appears more than once')
                if not types.issubset(VALID_TYPES): add('index.html','BAD_CARD_TYPE',f'{name}: invalid types {sorted(types-VALID_TYPES)}')
                landing[href]={'name':name,'category':cat,'anchor':anchor,'types':sorted(types)}; category_members[cat].append(href)
        if len(landing)!=len(files): add('index.html','COUNT_MISMATCH',f'Landing has {len(landing)} entries; filesystem has {len(files)}')
    headline_map=defaultdict(list)
    article_meta={}
    for p in files:
        raw=p.read_text(encoding='utf-8',errors='replace'); s=BeautifulSoup(raw,'lxml'); body=s.body
        name=(body.get('data-article-card','').strip() if body else '')
        cat=(body.get('data-honorable-category','').strip() if body else '')
        h1=text(s,'.hero h1'); headline_map[h1.casefold()].append(p.name)
        errs_before=len(issues)
        if p.name not in landing: add(p.name,'NOT_ON_LANDING','Article absent from categorized landing page')
        else:
            if landing[p.name]['name']!=name: add(p.name,'LANDING_NAME_MISMATCH',f'Landing says {landing[p.name]["name"]!r}; body says {name!r}')
            if landing[p.name]['category']!=cat: add(p.name,'LANDING_CATEGORY_MISMATCH',f'Landing says {landing[p.name]["category"]!r}; body says {cat!r}')
        if not name: add(p.name,'MISSING_CARD_IDENTITY','body[data-article-card] missing')
        if not cat: add(p.name,'MISSING_CATEGORY','body[data-honorable-category] missing')
        anchor=(body.get('data-landing-anchor','').strip() if body else '')
        if p.name in landing and anchor!=landing[p.name]['anchor']: add(p.name,'LANDING_ANCHOR_MISMATCH',f'Body anchor {anchor!r}; landing anchor {landing[p.name]["anchor"]!r}')
        scope=(body.get('data-navigation-scope','').strip() if body else '')
        if scope!='category-local': add(p.name,'BAD_NAVIGATION_SCOPE',f'Expected category-local, found {scope!r}')
        if not h1: add(p.name,'MISSING_HEADLINE','Hero headline missing')
        elif name and name.casefold() in h1.casefold(): add(p.name,'CARD_NAME_IN_HEADLINE','Hero headline contains full card name')
        if VISIBLE_ORDINAL_RE.search(s.get_text(' ',strip=True)): add(p.name,'VISIBLE_NUMBERING','Visible Honorable Mention numbering remains')
        badge=text(s,'.honorable-badge')
        if cat and cat not in badge: add(p.name,'BAD_BADGE',f'Category {cat!r} not present in badge')
        # top and end nav hrefs only
        top=s.select_one('nav.rank-nav'); end=s.select_one('nav.end-nav')
        for nav,label in ((top,'top'),(end,'end')):
            if nav and nav.get('data-navigation-scope')!='category-local': add(p.name,'NAV_SCOPE_ATTRIBUTE',f'{label} nav lacks category-local scope')
        if not top: add(p.name,'MISSING_TOP_NAV','Category top navigation missing')
        if not end: add(p.name,'MISSING_END_NAV','Category end navigation missing')
        top_links=[a.get('href','') for a in top.select('a[href]')] if top else []
        end_links=[a.get('href','') for a in end.select('a[href]')] if end else []
        if top_links!=end_links: add(p.name,'NAV_DISAGREEMENT',f'Top links {top_links} differ from end links {end_links}')
        for href in top_links:
            if href not in landing: add(p.name,'NAV_MISSING_TARGET',f'Navigation target {href} absent')
            elif landing[href]['category']!=cat: add(p.name,'CROSS_CATEGORY_NAV',f'{href} belongs to {landing[href]["category"]}, not {cat}')
        # required hero identity
        hero=s.select_one('.hero[data-hero-card]')
        if not hero or hero.get('data-hero-card','')!=name: add(p.name,'HERO_IDENTITY_MISMATCH','Hero identity does not match article card')
        media=s.select_one('.hero .hero-media')
        if not media or not media.get('src'): add(p.name,'MISSING_HERO_MEDIA','Visible hero image missing')
        article_meta[p.name]={'name':name,'category':cat,'headline':h1,'nav':top_links,'errors':len(issues)-errs_before}
    for h,fs in headline_map.items():
        if h and len(fs)>1:
            for f in fs: add(f,'DUPLICATE_HEADLINE',f'Headline shared by {len(fs)} articles')
    # exact local neighbor contract based on landing order
    for cat,members in category_members.items():
        for i,fn in enumerate(members):
            expected=[x for x in ([members[i-1]] if i else [])+([members[i+1]] if i+1<len(members) else [])]
            actual=article_meta.get(fn,{}).get('nav',[])
            if actual!=expected: add(fn,'NEIGHBOR_MISMATCH',f'Expected {expected}, found {actual}')
    # Categories are maintained alphabetically so insertion changes only local neighbors.
    for cat,members in category_members.items():
        names=[landing[x]['name'] for x in members]
        if names!=sorted(names,key=str.casefold): add('index.html','CATEGORY_NOT_ALPHABETICAL',f'{cat} is not alphabetically ordered')
    # Generated manifests must agree with the landing page.
    for mf in (root/'archive-manifest.json',root/'data/honorable-categories.json'):
        if not mf.is_file(): add(str(mf.relative_to(root)),'MISSING_MANIFEST','Generated Honorable Mention manifest missing'); continue
        try: data=json.loads(mf.read_text(encoding='utf-8'))
        except Exception as exc: add(str(mf.relative_to(root)),'BAD_MANIFEST_JSON',str(exc)); continue
        count=data.get('honorable_mention_count',data.get('totalHonorableMentions'))
        cats=data.get('honorable_category_count',data.get('categoryCount'))
        scope=data.get('honorable_navigation_scope',data.get('navigationScope'))
        if count!=len(landing): add(str(mf.relative_to(root)),'MANIFEST_COUNT_MISMATCH',f'{count} != {len(landing)}')
        if cats!=len(category_members): add(str(mf.relative_to(root)),'MANIFEST_CATEGORY_MISMATCH',f'{cats} != {len(category_members)}')
        if scope!='category-local': add(str(mf.relative_to(root)),'MANIFEST_SCOPE_MISMATCH',f'Expected category-local, found {scope!r}')
    # filename uniqueness and no stale old references
    for p in list(root.glob('*.html')):
        raw=p.read_text(encoding='utf-8',errors='ignore')
        m=re.search(r'honorable-\d{3}-[a-z0-9-]+\.html',raw)
        if m: add(p.name,'STALE_NUMBERED_REFERENCE',f'Stale reference {m.group(0)}')
    status='PASS' if not any(i['severity']=='ERROR' for i in issues) else 'FAIL'
    summary={'status':status,'honorableArticles':len(files),'landingEntries':len(landing),'categories':len(category_members),'errors':sum(i['severity']=='ERROR' for i in issues),'warnings':sum(i['severity']=='WARNING' for i in issues),'categoryCounts':{k:len(v) for k,v in category_members.items()},'issues':issues}
    outjson=args.json or root/'audit/honorable-category-validation.json'; outcsv=args.csv or root/'audit/honorable-category-validation.csv'; outjson.parent.mkdir(parents=True,exist_ok=True)
    outjson.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with outcsv.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['severity','file','code','message']); w.writeheader(); w.writerows(issues)
    print(json.dumps({k:v for k,v in summary.items() if k!='issues'},indent=2))
    if issues:
        for i in issues[:30]: print(f"{i['severity']} {i['file']} {i['code']}: {i['message']}")
        if len(issues)>30: print(f'... {len(issues)-30} more')
    return 0 if status=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
