#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, html, json, re
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse
from bs4 import BeautifulSoup

CSS_START='/* CR_CANONICAL_ARTWORK_SPOTLIGHT_START */'
CSS_END='/* CR_CANONICAL_ARTWORK_SPOTLIGHT_END */'
SCRIPT_SRC='assets/artwork-spotlight.js'
GENERIC_PHRASES=(
 'the original illustration became inseparable from the card’s first strategic identity',
 "the original illustration became inseparable from the card's first strategic identity",
 'article uses scryfall', 'catalog image', 'database image', 'historical starting point',
 'visual identity preserved', 'established the visual identity', 'strategic identity',
 'place in the game', 'mechanical identity', 'modern frame',
)
ARTWORK_CORE_WORDS={
 'art','artwork','illustration','image','imagery','composition','scene','figure','subject','object','setting',
 'silhouette','foreground','background','palette','color','colours','light','lighting','shadow','frame','framing',
 'perspective','horizon','landscape','texture','gesture','pose','motion','atmosphere','mood','field','forms','outline','scale'
}

ARTIST_OVERRIDES={
 'Akroma, Angel of Wrath':'Ron Spears',
 'Exalted Angel':'Michael Sutfin',
}

SET_MAP={
 'Limited Edition Alpha':'lea','Alpha':'lea','Arabian Nights':'arn','Antiquities':'atq','Legends':'leg','The Dark':'drk','Fallen Empires':'fem','Ice Age':'ice','Homelands':'hml','Alliances':'all','Mirage':'mir','Visions':'vis','Weatherlight':'wth','Tempest':'tmp','Stronghold':'sth','Exodus':'exo',
 "Urza's Saga":'usg','Urza’s Saga':'usg',"Urza's Legacy":'ulg','Urza’s Legacy':'ulg',"Urza's Destiny":'uds','Urza’s Destiny':'uds','Mercadian Masques':'mmq','Nemesis':'nem','Prophecy':'pcy','Invasion':'inv','Planeshift':'pls','Apocalypse':'apc','Odyssey':'ody','Torment':'tor','Judgment':'jud','Onslaught':'ons','Legions':'lgn','Scourge':'scg','Mirrodin':'mrd','Darksteel':'dst','Fifth Dawn':'5dn','Champions of Kamigawa':'chk','Betrayers of Kamigawa':'bok','Saviors of Kamigawa':'sok','Ravnica: City of Guilds':'rav','Guildpact':'gpt','Dissension':'dis','Coldsnap':'csp','Time Spiral':'tsp','Planar Chaos':'plc','Future Sight':'fut','Lorwyn':'lrw','Morningtide':'mor','Shadowmoor':'shm','Commander 2013':'c13','Magic 2010':'m10','Modern Horizons 2':'mh2'
}

CSS=r'''/* CR_CANONICAL_ARTWORK_SPOTLIGHT_START */
/* Eternal Dragon is the visual authority for every artwork spotlight. */
.art-break.artwork-spotlight{
  width:100vw!important;max-width:none!important;min-height:min(69vw,720px)!important;
  margin:72px 0 72px calc((var(--reading) - 100vw)/2)!important;transform:none!important;
  position:relative!important;display:flex!important;align-items:flex-end!important;overflow:hidden!important;
  color:white!important;background:none!important;isolation:isolate;
}
.art-break.artwork-spotlight:before{
  content:""!important;position:absolute!important;inset:0!important;z-index:1!important;
  background:linear-gradient(0deg,rgba(4,8,8,.93),rgba(4,8,8,.18) 55%,transparent 76%)!important;pointer-events:none;
}
.artwork-spotlight .art-break-media{
  position:absolute!important;inset:0!important;z-index:0!important;display:block!important;
  width:100%!important;height:100%!important;max-width:none!important;object-fit:cover!important;
  object-position:center 25%!important;transform:none!important;pointer-events:none;
}
.artwork-spotlight .art-caption{
  position:relative!important;z-index:2!important;width:min(var(--wide),calc(100% - 32px))!important;
  margin:auto!important;padding:35px 0!important;color:#ddd!important;
  font:13px/1.55 Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif!important;
  text-shadow:0 2px 18px rgba(0,0,0,.72);
}
.artwork-spotlight .art-caption b{display:block!important;margin-bottom:5px!important;color:white!important;font-size:1rem!important;line-height:1.35!important}
.artwork-spotlight .art-caption-excerpt{display:block}
@media(max-width:750px){
 .art-break.artwork-spotlight{width:100vw!important;max-width:none!important;min-height:72vh!important;margin-left:calc((100% - 100vw)/2)!important;margin-right:0!important}
 .artwork-spotlight .art-break-media{object-position:center 25%!important}
 .artwork-spotlight .art-caption{width:calc(100% - 48px)!important;padding:31px 0!important}
}
/* CR_CANONICAL_ARTWORK_SPOTLIGHT_END */'''

JS=r'''(() => {
  "use strict";
  const artistOf = card => card?.artist || [...new Set((card?.card_faces || []).map(face => face.artist).filter(Boolean))].join(" & ");
  async function hydrate(spotlight){
    const credit=spotlight.querySelector("[data-artwork-credit]");
    if(!credit || spotlight.dataset.artworkArtist) return;
    const cardName=spotlight.dataset.artworkCard, setCode=spotlight.dataset.artworkSet;
    if(!cardName) return;
    const key=`cr-artwork:${cardName}:${setCode||""}`;
    let card=null;
    try{const cached=sessionStorage.getItem(key);if(cached) card=JSON.parse(cached)}catch(_){}
    if(!card){
      const params=new URLSearchParams({exact:cardName});if(setCode)params.set("set",setCode);
      try{const response=await fetch(`https://api.scryfall.com/cards/named?${params}`,{headers:{Accept:"application/json"}});if(!response.ok)return;card=await response.json();try{sessionStorage.setItem(key,JSON.stringify(card))}catch(_){}}catch(_){return}
    }
    const artist=artistOf(card);if(!artist)return;
    const setName=card.set_name||spotlight.dataset.artworkSetName||"first-printing";
    spotlight.dataset.artworkArtist=artist;
    credit.textContent=`${artist}’s original ${setName} artwork`;
    const image=spotlight.querySelector(".art-break-media");if(image)image.alt=`${cardName} artwork by ${artist}`;
  }
  const run=()=>document.querySelectorAll(".artwork-spotlight").forEach(hydrate);
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",run,{once:true});else run();
})();
'''

def clean(s): return re.sub(r'\s+',' ',s or '').strip()
def ea(s): return html.escape(s,quote=True)

def balanced_div(raw,start):
    depth=0
    for m in re.finditer(r'<div\b|</div\s*>',raw[start:],re.I):
        if m.group(0).lower().startswith('<div'): depth+=1
        else:
            depth-=1
            if depth==0:
                end=start+m.end();return end,raw[start:end]
    raise ValueError('unbalanced div')

def remove_legacy_inset_override(raw):
    legacy='.art-break{width:min(1100px,calc(100vw - 32px))!important;max-width:calc(100vw - 32px)!important;margin-left:50%!important;transform:translateX(-50%)!important}\n'
    return raw.replace(legacy,'')

def add_css(raw):
    pat=re.compile(re.escape(CSS_START)+r'.*?'+re.escape(CSS_END),re.S)
    if pat.search(raw): return pat.sub(CSS,raw)
    i=raw.lower().rfind('</style>')
    if i<0: raise ValueError('missing style')
    return raw[:i]+'\n\n'+CSS+'\n'+raw[i:]

def add_script(raw):
    if SCRIPT_SRC in raw:return raw
    tag=f'<script defer src="{SCRIPT_SRC}"></script>\n'
    i=raw.lower().rfind('</body>')
    return raw[:i]+tag+raw[i:] if i>=0 else raw+'\n'+tag

def ensure_body_card(raw,card):
    m=re.search(r'<body\b[^>]*>',raw,re.I)
    if not m or 'data-article-card' in m.group(0):return raw
    rep=m.group(0)[:-1]+f' data-article-card="{ea(card)}">'
    return raw[:m.start()]+rep+raw[m.end():]

def artist_from(soup):
    for stat in soup.select('.stat'):
        b=stat.find('b')
        if b and 'illustrated by' in clean(b.get_text(' ',strip=True)).casefold():
            vals=list(stat.stripped_strings); a=clean(' '.join(vals[1:]));
            if a:return a,'article-stat'
    b=soup.select_one('.art-caption b');txt=clean(b.get_text(' ',strip=True)) if b else ''
    if txt:
        m=re.match(r"(.+?)[’']s\s+",txt)
        if m and not m.group(1).casefold().endswith(('card','artwork')):return clean(m.group(1)),'existing-caption'
        parts=[clean(x) for x in re.split(r'\s*[·—]\s*',txt) if clean(x)]
        if len(parts)>=2:
            cand=parts[1]
            if not re.search(r'\b(artwork|showcase|printing|edition|alpha|beta|unlimited|revised|masters|set|19\d{2}|20\d{2})\b',cand,re.I) and len(cand.split())<=6:
                return cand,'existing-caption'
    return None,None

def set_name_from(soup):
    for node in soup.select('.byline span'):
        t=clean(node.get_text(' ',strip=True))
        if t and t not in {'·','A Compulsive Research essay'} and 'minute read' not in t.casefold() and re.search(r'\b(?:19|20)\d{2}\b',t):
            return re.split(r'\s*[,·]\s*(?=(?:19|20)\d{2}\b)',t,maxsplit=1)[0].strip()
    for stat in soup.select('.stat'):
        b=stat.find('b')
        if b and any(k in clean(b.get_text(' ',strip=True)).casefold() for k in ('first printed','first release')):
            vals=list(stat.stripped_strings);t=clean(' '.join(vals[1:]));return re.split(r'\s*[·,]\s*(?=(?:19|20)\d{2}\b|[A-Z][a-z]+\s+(?:19|20)\d{2})',t,maxsplit=1)[0].strip()
    return 'first-printing'

def url_set_code(url):
    if not url:return ''
    u=html.unescape(url)
    q=parse_qs(urlparse(u).query).get('set')
    if q:return unquote(q[0]).lower()
    m=re.search(r'/cards/([a-z0-9_]+)/[^/?]+',u,re.I)
    return m.group(1).lower() if m else ''

def css_url_for_class(raw,cls):
    urls=[]
    patterns=[
      rf'\.{re.escape(cls)}\s*\{{[^{{}}]]*',
    ]
    # More tolerant scan over each class rule.
    for m in re.finditer(rf'\.{re.escape(cls)}\s*\{{(.*?)\}}',raw,re.I|re.S):
        body=m.group(1)
        u=re.search(r'(?:background-image|background)\s*:[^;}}]*url\(["\']?([^"\')]+)',body,re.I|re.S)
        if u:urls.append(html.unescape(u.group(1)))
    return urls[-1] if urls else ''

def choose_art_url(soup,raw,card):
    art=soup.select_one('.art-break')
    if art:
        media=art.select_one('.art-break-media')
        if media and media.get('src'):return html.unescape(media['src'])
        for cls in reversed(art.get('class',[])):
            if cls!='art-break':
                u=css_url_for_class(raw,cls)
                if u:return u
        # Last .art-break rule is normally the card-specific override.
        u=css_url_for_class(raw,'art-break')
        if u and 'cards/scg/12' not in u:return u
    hero=soup.select_one('.hero-media')
    if hero and hero.get('src'):return html.unescape(hero['src'])
    # Card-specific hero override.
    for selector in ['hero:before','hero']:
        u=css_url_for_class(raw,selector)
        if u and 'cards/scg/12' not in u:return u
    img=soup.select_one('[data-article-card-image], .card-lead img')
    if img and img.get('src'):return html.unescape(img['src'])
    return ''

def set_code_from(soup,art_url,set_name,card):
    n=soup.select_one('[data-original-set]')
    if n and n.get('data-original-set'):return n['data-original-set'].lower()
    code=url_set_code(art_url)
    if code:return code
    if card=='Rishadan Port':return 'mmq'
    return SET_MAP.get(set_name,'')

def normalize_urls(url,card,set_code):
    if not url:
        q=f'exact={quote(card,safe="")}' + (f'&set={quote(set_code,safe="")}' if set_code else '')
        url=f'https://api.scryfall.com/cards/named?{q}&format=image&version=art_crop'
    if 'version=normal' in url:url=url.replace('version=normal','version=art_crop')
    elif 'version=large' in url:url=url.replace('version=large','version=art_crop')
    elif 'format=image' in url and 'version=' not in url:url += '&version=art_crop'
    if 'version=art_crop' in url:fallback=url.replace('version=art_crop','version=normal')
    else:
        q=f'exact={quote(card,safe="")}' + (f'&set={quote(set_code,safe="")}' if set_code else '')
        fallback=f'https://api.scryfall.com/cards/named?{q}&format=image&version=normal'
    return url,fallback

def excerpt_is_valid(excerpt):
    text=clean(excerpt); low=text.casefold()
    if len(text)<55 or any(phrase in low for phrase in GENERIC_PHRASES):return False
    ws=set(re.findall(r"[a-z]+",low))
    return bool(ws & ARTWORK_CORE_WORDS)

def excerpt_from(soup,card):
    cap=soup.select_one('.art-caption')
    if cap:
        ex_node=cap.select_one('.art-caption-excerpt')
        if ex_node:
            ex=clean(ex_node.get_text(' ',strip=True))
        else:
            b=cap.find('b');whole=clean(cap.get_text(' ',strip=True));head=clean(b.get_text(' ',strip=True)) if b else ''
            ex=clean(whole[len(head):]) if whole.startswith(head) else whole
        if excerpt_is_valid(ex):return ex,True
    raise ValueError(
        f'{card}: missing an authored image-focused artwork excerpt. Populate the canonical template '
        'or run tools/refine_artwork_captions.py with verified card metadata; this layout tool will not invent strategic boilerplate.'
    )

def markup(card,set_code,set_name,artist,art,fallback,excerpt):
    credit=f'{artist}’s original {set_name} artwork' if artist else f'Original {set_name} artwork'
    alt=f'{card} artwork by {artist}' if artist else f'{card} original artwork'
    return (f'<div class="art-break artwork-spotlight" data-artwork-card="{ea(card)}" data-artwork-set="{ea(set_code)}" data-artwork-set-name="{ea(set_name)}" data-artwork-artist="{ea(artist or "")}">\n'
      f'<img class="art-break-media" alt="{ea(alt)}" loading="lazy" src="{ea(art)}" onerror="this.onerror=null;this.src=\'{ea(fallback)}\';"/>\n'
      f'<div class="art-caption"><b data-artwork-credit aria-live="polite">{html.escape(credit)}</b><span class="art-caption-excerpt">{html.escape(excerpt)}</span></div>\n</div>')

def insert_after_second_section(raw,block):
    m=re.search(r'<article\b[^>]*class=["\'][^"\']*\barticle\b[^"\']*["\'][^>]*>',raw,re.I)
    if not m:raise ValueError('missing article')
    closes=list(re.finditer(r'</section\s*>',raw[m.end():],re.I))
    if not closes:raise ValueError('missing sections')
    c=closes[1] if len(closes)>1 else closes[0];i=m.end()+c.end()
    return raw[:i]+'\n'+block+raw[i:]

def migrate(path,card):
    raw=path.read_text(encoding='utf-8',errors='replace');soup=BeautifulSoup(raw,'lxml')
    set_name=set_name_from(soup);art0=choose_art_url(soup,raw,card);set_code=set_code_from(soup,art0,set_name,card);art,fallback=normalize_urls(art0,card,set_code)
    artist,source=artist_from(soup)
    if not artist and card in ARTIST_OVERRIDES:
        artist=ARTIST_OVERRIDES[card];source='verified-override'
    if not artist:
        raise ValueError(f'{card}: verified exact-printing artist is required as static metadata; runtime lookup is noncanonical.')
    excerpt,preserved=excerpt_from(soup,card);block=markup(card,set_code,set_name,artist,art,fallback,excerpt)
    m=re.search(r'<div\b[^>]*class=["\'][^"\']*\bart-break\b[^"\']*["\'][^>]*>',raw,re.I);inserted=not bool(m)
    if m:
        end,_=balanced_div(raw,m.start());raw=raw[:m.start()]+raw[end:]
    raw=insert_after_second_section(raw,block)
    raw=ensure_body_card(raw,card);raw=remove_legacy_inset_override(raw);raw=add_css(raw);raw=add_script(raw);path.write_text(raw,encoding='utf-8')
    return {'file':path.name,'card':card,'set_code':set_code,'set_name':set_name,'artist':artist,'artist_source':source or 'static-article-metadata','spotlight_inserted':inserted,'specific_excerpt_preserved':preserved,'excerpt_replaced_or_created':not preserved,'art_url':art}

def replace_css_file(path):
    text=path.read_text(encoding='utf-8');pat=re.compile(re.escape(CSS_START)+r'.*?'+re.escape(CSS_END),re.S)
    text=pat.sub(CSS,text) if pat.search(text) else text.rstrip()+'\n\n'+CSS+'\n';path.write_text(text,encoding='utf-8')

def check_current(root,items):
    failures=[]
    for filename,card in items:
        path=root/filename
        raw=path.read_text(encoding='utf-8',errors='replace')
        soup=BeautifulSoup(raw,'lxml')
        spots=soup.select('article.article > .art-break.artwork-spotlight')
        if len(spots)!=1:
            failures.append(f'{filename}: expected one direct artwork spotlight; found {len(spots)}')
            continue
        spot=spots[0]
        preceding=sum(1 for n in spot.find_previous_siblings() if getattr(n,'name',None)=='section')
        if preceding!=2:failures.append(f'{filename}: spotlight follows {preceding} sections, not 2')
        image=spot.select_one(':scope > .art-break-media')
        if not image or 'version=art_crop' not in (image.get('src') or ''):failures.append(f'{filename}: missing original art_crop image')
        credit=spot.select_one('.art-caption [data-artwork-credit]')
        artist=clean(spot.get('data-artwork-artist')); set_name=clean(spot.get('data-artwork-set-name'))
        if not credit:failures.append(f'{filename}: missing credit')
        elif artist and set_name and clean(credit.get_text(' ',strip=True)) != f'{artist}’s original {set_name} artwork':
            failures.append(f'{filename}: credit is not exactly artist + original set')
        excerpt=spot.select_one('.art-caption-excerpt')
        if not excerpt or not excerpt_is_valid(excerpt.get_text(' ',strip=True)):failures.append(f'{filename}: excerpt is not image-focused or uses prohibited boilerplate')
        if not all((spot.get(k) or '').strip() for k in ('data-artwork-card','data-artwork-set','data-artwork-set-name','data-artwork-artist')):failures.append(f'{filename}: incomplete static artwork metadata')
        if CSS_START not in raw:failures.append(f'{filename}: canonical CSS lock missing')
        if SCRIPT_SRC not in raw:failures.append(f'{filename}: metadata script missing')
        if 'width:min(1100px,calc(100vw - 32px))!important' in raw:failures.append(f'{filename}: legacy narrow inset override remains')
    if failures:
        print('Artwork spotlight check failed:')
        for failure in failures[:100]:print('-',failure)
        if len(failures)>100:print(f'... and {len(failures)-100} more')
        return 1
    print(f'Artwork spotlight check passed: {len(items)} articles')
    return 0

def main():
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path,nargs='?',default=Path(__file__).resolve().parents[1]);ap.add_argument('--check',action='store_true');args=ap.parse_args();root=args.root.resolve()
    man=json.loads((root/'archive-manifest.json').read_text());items=[(e['file'],e['card']) for e in man['entries'] if e.get('article_present') and e.get('file')]+[(e['file'],e['card']) for e in man['honorable_mentions'] if e.get('article_present') and e.get('file')]
    if args.check:raise SystemExit(check_current(root,items))
    results=[migrate(root/f,c) for f,c in items]
    for f in ['assets/compulsive-research.css','assets/canonical-eternal-dragon.css']:replace_css_file(root/f)
    (root/SCRIPT_SRC).write_text(JS,encoding='utf-8')
    audit=root/'audit';audit.mkdir(exist_ok=True);(audit/'artwork-spotlight-migration.json').write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n')
    inserted=sum(r['spotlight_inserted'] for r in results);static=sum(r['artist_source']!='scryfall-runtime' for r in results);repl=sum(r['excerpt_replaced_or_created'] for r in results)
    summary=f'''# Artwork spotlight canonicalization\n\n- Articles inspected: **{len(results)}**\n- Existing spotlights normalized: **{len(results)-inserted}**\n- Missing spotlights inserted: **{inserted}**\n- Artist credits embedded from existing verified article metadata: **{static}**\n- Articles lacking required static artist metadata: **{len(results)-static}**\n- Existing specific artwork excerpts preserved: **{len(results)-repl}**\n- Generic or missing excerpts replaced with card-specific excerpts: **{repl}**\n\nEvery article now uses the Eternal Dragon full-bleed geometry, `object-fit: cover`, the shared `center 25%` crop, the same mobile `72vh` treatment, a lower gradient, and an artist credit plus excerpt over the image.\n'''
    (audit/'artwork-spotlight-migration.md').write_text(summary);print(summary)
if __name__=='__main__':main()
