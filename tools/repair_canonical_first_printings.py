#!/usr/bin/env python3
"""Repair false debut records caused by recurring promo-set container dates.

The committed card snapshot remains the input. This tool only changes a record when
its selected debut belongs to a known recurring/promotional container and a plausible
playable paper printing exists. Explicit promo-debut exceptions live in
`data/canonical-first-printing-overrides.json`.
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString

ROOT=Path(__file__).resolve().parents[1]
SUSPICIOUS=re.compile(r'(pro tour promos?|grand prix promos?|judge gift cards?|secret lair|store championships?|oversized|arena league|dci promos?|magic player rewards|media and collaboration promos?|prerelease promos?|release event|world championship promos?|junior super series|new phyrexia promos?|theros promos?|magic 2015 promos?|dark ascension promos?)',re.I)
EXCLUDE_CANDIDATE=re.compile(r'(promos?|secret lair|store championships?|the list|special guests|oversized|judge gift|arena league|player rewards|open the helvault|box topper|championship|junior super series|art series|tokens?)',re.I)

def load_cards(path:Path):
    d=json.loads(path.read_text(encoding='utf-8')); return d, d['cards']

def candidate(card, overrides):
    override=overrides.get(card['articleName'])
    if override:
        return next((p for p in card.get('printings',[]) if p.get('scryfallId')==override.get('scryfallId')),None)
    if not SUSPICIOUS.search(card.get('setName','')): return None
    usable=[p for p in card.get('printings',[]) if not EXCLUDE_CANDIDATE.search(p.get('setName',''))]
    if not usable:return None
    usable.sort(key=lambda p:(p.get('releaseDate','9999'),p.get('setCode',''),p.get('collectorNumber','')))
    return usable[0]

def replace_text(node, old, new):
    if not node or not old or old==new:return
    for text in list(node.find_all(string=True)):
        if old in str(text): text.replace_with(NavigableString(str(text).replace(old,new)))

def fig_caption(soup, record, original):
    cap=soup.new_tag('figcaption'); b=soup.new_tag('b'); year=record.get('releaseDate','')[:4]
    b.string=record.get('setName','Printing')+(f' · {year}' if year else '')
    cap.append(b); cap.append(soup.new_tag('br'))
    prefix='Original printing · ' if original else ''
    tail=record.get('artist','Artist not listed')
    if record.get('collectorNumber'):tail+=f" · {record['collectorNumber']}"
    cap.append(NavigableString(prefix+tail)); return cap

def ensure_figure(soup, grid, record):
    fig=grid.find('figure',attrs={'data-scryfall-id':record.get('scryfallId')})
    if fig:return fig
    fig=soup.new_tag('figure'); fig['class']='printing'; fig['data-card-name']=record['cardName']; fig['data-scryfall-id']=record['scryfallId']; fig['data-set']=record['setCode']; fig['data-collector-number']=record.get('collectorNumber',''); fig['data-identity-status']='verified-editorial-v2-snapshot'
    img=soup.new_tag('img'); img['src']=record['imageUrl']; img['alt']=f"{record['cardName']} — {record['setName']}"; img['loading']='lazy'; img['decoding']='async'; fig.append(img); fig.append(fig_caption(soup,record,False)); grid.append(fig); return fig

def update_page(path:Path, old:dict, new:dict)->bool:
    raw=path.read_text(encoding='utf-8',errors='replace')
    # Do not rewrite pages that already identify the correct original set.
    soup=BeautifulSoup(raw,'html.parser')
    old_set=old['setName']; new_set=new['setName']; old_year=str(old.get('year') or old.get('releaseDate','')[:4]); new_year=new.get('releaseDate','')[:4]
    old_artist=old.get('artist',''); new_artist=new.get('artist','')
    wrong_signal=(old_set in raw or f'data-original-set="{old.get("setCode")}"' in raw)
    if not wrong_signal:return False
    # Head metadata and header.
    meta=soup.find('meta',attrs={'name':'description'})
    if meta and meta.get('content'):
        meta['content']=meta['content'].replace(old_set,new_set).replace(old_year,new_year).replace(old_artist,new_artist)
    hero=soup.select_one('header.hero img.hero-media')
    if hero:
        hero['src']=new['artUrl']; hero['onerror']=f"this.onerror=null;this.src='{new['imageUrl']}';"
    for sel in ['header.hero .deckline','header.hero .byline','#opening','#origin','#memory']:
        node=soup.select_one(sel); replace_text(node,old_set,new_set); replace_text(node,old_year,new_year); replace_text(node,old_artist,new_artist)
    # Lead card object.
    lead=soup.select_one('.card-lead')
    if lead:
        lead['data-scryfall-id']=new['scryfallId']
        img=lead.find('img')
        if img: img['src']=new['imageUrl']
        eye=lead.select_one('.oracle .eyebrow'); replace_text(eye,old_set,new_set)
        for stat in lead.select('.stat'):
            label=stat.find('b').get_text(' ',strip=True).lower() if stat.find('b') else ''
            if 'original set' in label or 'first release' in label or 'first printed' in label:
                b=stat.find('b'); stat.clear(); stat.append(b); stat.append(NavigableString(f'{new_set} · {new_year}'))
            elif 'illustrated by' in label:
                b=stat.find('b'); stat.clear(); stat.append(b); stat.append(NavigableString(new_artist))
    # Artwork spotlight.
    spot=soup.select_one('.artwork-spotlight')
    if spot:
        spot['data-artwork-artist']=new_artist; spot['data-artwork-set']=new['setCode']; spot['data-artwork-set-name']=new_set
        img=spot.select_one('.art-break-media')
        if img:
            img['src']=new['artUrl']; img['data-fallback-src']=new['imageUrl']
        credit=spot.select_one('[data-artwork-credit]')
        if credit: credit.string=f"{new_artist}’s original {new_set} artwork"
    # Printing gallery identity/order.
    grid=soup.select_one('.canonical-printing-gallery')
    if grid:
        grid['data-original-set']=new['setCode']
        old_record=next((p for p in old.get('printings',[]) if p.get('scryfallId')==old.get('scryfallId')),None)
        for fig in grid.find_all('figure',recursive=False):
            classes=[c for c in fig.get('class',[]) if c!='original-printing']; fig['class']=classes or ['printing']
            if old_record and fig.get('data-scryfall-id')==old_record.get('scryfallId'):
                cap=fig.find('figcaption');
                if cap: cap.replace_with(fig_caption(soup,old_record,False))
        new_fig=ensure_figure(soup,grid,new)
        new_fig['class']=list(dict.fromkeys(['printing','original-printing']+[c for c in new_fig.get('class',[]) if c not in {'printing','original-printing'}]))
        cap=new_fig.find('figcaption')
        if cap: cap.replace_with(fig_caption(soup,new,True))
        new_fig.extract(); grid.insert(0,new_fig)
        grid['data-gallery-fallback-count']=str(len(grid.find_all('figure',recursive=False)))
    path.write_text(str(soup),encoding='utf-8'); return True

def update_artwork_metadata(path:Path, changes:dict):
    if not path.exists():return
    d=json.loads(path.read_text(encoding='utf-8'))
    for row in d.get('cards',[]):
        change=changes.get(row.get('articleCard'))
        if change:
            row.update({'setCode':change['setCode'],'setName':change['setName'],'artist':change['artist']})
    path.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,default=ROOT); ap.add_argument('--check',action='store_true'); ap.add_argument('--report',type=Path,default=None)
    args=ap.parse_args(); root=args.root.resolve()
    overrides=json.loads((root/'data/canonical-first-printing-overrides.json').read_text())['cards']
    data_path=root/'data/remaining-entry-card-data.json'; data,cards=load_cards(data_path)
    changes=[]; metadata_changes={}
    for card in cards:
        new=candidate(card,overrides)
        if not new or new.get('scryfallId')==card.get('scryfallId'):continue
        old={k:card.get(k) for k in card}; old['printings']=card.get('printings',[])
        changes.append({'entry':card.get('entry'),'cardName':card['articleName'],'oldSet':card['setName'],'oldDate':card['releaseDate'],'newSet':new['setName'],'newDate':new['releaseDate'],'newScryfallId':new['scryfallId'],'pageUpdated':False})
        if not args.check:
            for p in card.get('printings',[]):p['original']=p.get('scryfallId')==new.get('scryfallId')
            card.update({'setCode':new['setCode'],'setName':new['setName'],'releaseDate':new['releaseDate'],'year':int(new['releaseDate'][:4]),'artist':new['artist'],'scryfallId':new['scryfallId'],'illustrationId':new.get('illustrationId','')})
            metadata_changes[card['articleName']]=new
            matches=sorted(root.glob(f"{int(card['entry']):03d}-*.html"))
            page=matches[0] if matches else None
            if page: changes[-1]['pageUpdated']=update_page(page,old,new)
    if not args.check:
        data_path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        update_artwork_metadata(root/'canonical/artwork-card-metadata.json',metadata_changes)
    payload={'mode':'check' if args.check else 'apply','candidateRepairs':len(changes),'pagesUpdated':sum(c['pageUpdated'] for c in changes),'status':'FAIL' if args.check and changes else 'PASS','changes':changes}
    report=args.report or root/'audit/canonical-first-printing-repairs.json'; report.parent.mkdir(parents=True,exist_ok=True); report.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:payload[k] for k in ['mode','candidateRepairs','pagesUpdated','status']},indent=2))
    return 1 if args.check and changes else 0
if __name__=='__main__': raise SystemExit(main())
