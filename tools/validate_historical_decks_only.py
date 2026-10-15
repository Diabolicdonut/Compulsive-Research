#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from bs4 import BeautifulSoup

DETAIL_RE = re.compile(r'<details\b[^>]*class=(?P<q>["\'])[^"\']*\bdeck\b[^"\']*(?P=q)[^>]*>.*?</details>', re.I|re.S)
TOTAL_CONTEXT_RE = re.compile(r'(?:Main deck|Sideboard|recorded size:|main deck and)\s*\d{4,}', re.I)
SIDE_WORDS=('sideboard','side board','maybeboard')
ALLOWED={'tournament-registration','curated-example','official-digital-deck'}

def label(h):
    if not h:return 'Cards'
    return re.split(r'\s*[·|—-]\s*\d+\s*$',h.get_text(' ',strip=True),maxsplit=1)[0].strip() or 'Cards'
def side(s):return any(x in s.casefold() for x in SIDE_WORDS)
def qty(n):
    t=n.get_text(' ',strip=True)
    if not re.fullmatch(r'\d+',t):raise ValueError(t)
    return int(t)
def inspect(path):
    raw=path.read_text(encoding='utf-8',errors='replace'); issues=[]; count=0
    for m in DETAIL_RE.finditer(raw):
        frag=m.group(0)
        if re.search(r'<details\b[^>]*class=["\'][^"\']*\bofficial-mtg-deck\b',frag,re.I):continue
        count+=1; s=BeautifulSoup(frag,'lxml'); d=s.find('details'); idx=count
        if d is None: issues.append(('FAIL','PARSE',idx));continue
        main=sb=0; groups=[]
        try:
            for g in d.select('.group'):
                h=g.find(['h3','h4','h5']); lab=label(h); total=sum(qty(r.select_one('.qty')) for r in g.select('.row') if r.select_one('.qty') is not None)
                groups.append((lab,total))
                if side(lab):sb+=total
                else:main+=total
                shown=h.get_text(' ',strip=True) if h else ''
                if not re.search(rf'[·|—-]\s*{total}\s*$',shown):issues.append(('FAIL','GROUP_TOTAL',idx))
        except ValueError:issues.append(('FAIL','NONINTEGER',idx));continue
        if d.get('data-main-count')!=str(main):issues.append(('FAIL','MAIN_DATA',idx))
        if d.get('data-sideboard-count')!=str(sb):issues.append(('FAIL','SIDE_DATA',idx))
        if d.get('data-deck-kind') not in ALLOWED:issues.append(('FAIL','KIND',idx))
        meta=d.select_one('.deck-meta .small')
        if meta:
            txt=meta.get_text(' ',strip=True)
            if f'Main deck {main}' not in txt:issues.append(('FAIL','META_MAIN',idx))
            if sb and f'Sideboard {sb}' not in txt:issues.append(('FAIL','META_SIDE',idx))
            if not sb and not re.search(r'No (?:recorded )?sideboard',txt,re.I):issues.append(('FAIL','META_ZERO',idx))
        else:issues.append(('FAIL','META_MISSING',idx))
        p=d.select_one('.deck-body > p')
        if p and f'{main} cards in the main deck' not in p.get_text(' ',strip=True):issues.append(('FAIL','PROVENANCE',idx))
        pre=d.find('pre',id=True)
        if not pre:issues.append(('FAIL','PRE_MISSING',idx))
        else:
            text=pre.get_text('',strip=False)
            for lab,total in groups:
                if not re.search(rf'(?m)^\s*{re.escape(lab)}\s*[·|—-]\s*{total}\s*$',text):issues.append(('FAIL','COPY_TOTAL',idx))
        if TOTAL_CONTEXT_RE.search(frag):issues.append(('FAIL','CONCAT',idx))
    if count == 0 and 'class="deck-research-status"' not in raw: issues.append(('FAIL','MISSING_DECKS_OR_RESEARCH_NOTICE',0))
    status='FAIL' if issues else 'PASS'
    return {'file':path.name,'deckCount':count,'status':status,'issues':[{'severity':a,'code':b,'deck':c} for a,b,c in issues]}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path.cwd());ap.add_argument('--output-dir',type=Path);ap.add_argument('--jobs',type=int,default=4);a=ap.parse_args()
    root=a.root.resolve();out=(a.output_dir or root/'historical-deck-validation').resolve();out.mkdir(parents=True,exist_ok=True)
    files=sorted(set(list(root.glob('[0-9][0-9][0-9]-*.html')) + list(root.glob('[0-9][0-9][0-9][0-9]-*.html')) + list(root.glob('honorable-*.html'))))
    with ProcessPoolExecutor(max_workers=max(1,a.jobs)) as pool:res=list(pool.map(inspect,files,chunksize=8))
    st=Counter(r['status'] for r in res);codes=Counter(i['code'] for r in res for i in r['issues'])
    payload={'articles':len(res),'decks':sum(r['deckCount'] for r in res),'statusCounts':dict(st),'issueCodeCounts':dict(codes),'results':res}
    (out/'historical-deck-validation.json').write_text(json.dumps(payload,indent=2)+'\n')
    (out/'historical-deck-validation.md').write_text('\n'.join(['# Historical deck validation','',f"- Articles: **{payload['articles']}**",f"- Decks: **{payload['decks']}**",f"- Pass: **{st.get('PASS',0)}**",f"- Fail: **{st.get('FAIL',0)}**",'', 'No issues found.' if not codes else '\n'.join(f'- `{k}`: {v}' for k,v in codes.items())])+'\n')
    print(json.dumps({k:payload[k] for k in ['articles','decks','statusCounts','issueCodeCounts']},indent=2));return 1 if st.get('FAIL') else 0
if __name__=='__main__':raise SystemExit(main())
