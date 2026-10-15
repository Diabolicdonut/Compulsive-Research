#!/usr/bin/env python3
"""Apply the Compulsive Research deck-card and double-faced-card image standard.

The migration is deterministic and network-free. Runtime Scryfall JSON lookups are
used only when a reader opens a card preview or a namesake lead card; this lets the
same code display both physical faces for transform/modal double-faced cards while
leaving split/adventure cards as a single printed image.
"""
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

CSS_BLOCK = r'''<style id="cr-card-image-standard">
/* CR_CARD_IMAGE_STANDARD_START */
#preview .preview-track{display:grid;grid-template-columns:1fr;gap:10px}
#preview.double-faced{width:min(620px,86vw)}
#preview.double-faced .preview-track{grid-template-columns:repeat(2,minmax(0,1fr))}
#preview .preview-face{min-width:0}
#preview .preview-face-label{display:block;padding:7px 9px 8px;text-align:center;background:#101917;color:#f1eee5;border-radius:0 0 10px 10px;font:800 11px/1.35 Inter,system-ui,sans-serif;letter-spacing:.06em;text-transform:uppercase}
#preview.double-faced img{border-radius:4.8% 4.8% 0 0}
.card-face-pair{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;align-items:start}
.card-face-pair figure{margin:0;min-width:0}
.card-face-pair img{width:100%;border-radius:4.8%;filter:drop-shadow(0 22px 28px rgba(0,0,0,.28));background:#ded8cc}
.card-face-pair figcaption{margin-top:10px;text-align:center;font:12.5px/1.4 Inter,sans-serif;color:var(--muted);letter-spacing:.03em;text-transform:uppercase}
.card-face-pair .face-label{display:block;color:var(--ink);font-weight:800;font-size:.78rem;letter-spacing:.12em}
.card-lead.dfc-lead{grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);width:min(1120px,calc(100vw - 32px))}
.dfc-rules-grid{display:grid;grid-template-columns:1fr;gap:16px}
.oracle.face-rules{margin:0}
.oracle.face-rules h3{margin:.35em 0 .45em}
.oracle.face-rules .face-oracle-text{white-space:pre-line}
.card-name{touch-action:manipulation}
@media(max-width:750px){
  #preview.double-faced{width:min(94vw,620px)}
  .card-face-pair{grid-template-columns:1fr 1fr;gap:10px}
  .card-lead.dfc-lead{grid-template-columns:1fr}
  .dfc-rules-grid{grid-template-columns:1fr}
}
/* CR_CARD_IMAGE_STANDARD_END */
</style>'''

RUNTIME = r'''/* CR_CARD_PREVIEW_RUNTIME_START */
const preview=document.getElementById('preview'),previewTrack=preview?preview.querySelector('.preview-track'):null;let pinned=false;const cardObjectCache=new Map();
function imgURL(n){return 'https://api.scryfall.com/cards/named?exact='+encodeURIComponent(n)+'&format=image&version=normal'}
function idImgURL(id,back=false){return 'https://api.scryfall.com/cards/'+encodeURIComponent(id)+'?format=image&version=normal'+(back?'&face=back':'')}
function cardApiURL(name,id){return id?'https://api.scryfall.com/cards/'+encodeURIComponent(id):'https://api.scryfall.com/cards/named?exact='+encodeURIComponent(name)}
function place(x,y){if(!preview)return;if(matchMedia('(max-width:750px)').matches){preview.style.left='50%';preview.style.top='50%';return}const pad=14,w=preview.offsetWidth||305,h=preview.offsetHeight||425;let l=x+18,t=y+18;if(l+w>innerWidth-pad)l=x-w-18;if(t+h>innerHeight-pad)t=innerHeight-h-pad;l=Math.max(pad,Math.min(l,innerWidth-w-pad));t=Math.max(pad,Math.min(t,innerHeight-h-pad));preview.style.left=l+'px';preview.style.top=t+'px'}
function imageFaces(card,fallbackName,fallbackId){const faces=(card&&card.card_faces||[]).map(face=>({name:face.name,url:face.image_uris&&face.image_uris.normal})).filter(face=>face.url);if(faces.length>1)return faces;const direct=card&&card.image_uris&&card.image_uris.normal;if(direct)return[{name:card.name||fallbackName,url:direct}];return[{name:fallbackName,url:fallbackId?idImgURL(fallbackId,false):imgURL(fallbackName)}]}
async function resolveCardObject(name,id){const key=id||name;if(cardObjectCache.has(key))return cardObjectCache.get(key);const promise=fetch(cardApiURL(name,id),{headers:{Accept:'application/json'}}).then(r=>{if(!r.ok)throw new Error('card lookup failed');return r.json()});cardObjectCache.set(key,promise);try{return await promise}catch(err){cardObjectCache.delete(key);throw err}}
function renderFaces(faces){if(!previewTrack)return;previewTrack.innerHTML='';faces.forEach((face,index)=>{const wrap=document.createElement('div');wrap.className='preview-face';const img=document.createElement('img');img.src=face.url;img.alt=face.name||'Card face';wrap.appendChild(img);if(faces.length>1){const label=document.createElement('span');label.className='preview-face-label';label.textContent=(index===0?'Front · ':'Back · ')+(face.name||'Card face');wrap.appendChild(label)}previewTrack.appendChild(wrap)});preview.classList.toggle('double-faced',faces.length>1)}
async function resolveFaces(el){const name=el.dataset.card,id=el.dataset.scryfallId||'';try{return imageFaces(await resolveCardObject(name,id),name,id)}catch(_){return[{name:name,url:id?idImgURL(id,false):imgURL(name)}]}}
function showCard(el,x,y,p=false){if(!preview||!previewTrack||!el||!el.dataset.card)return;const name=el.dataset.card,id=el.dataset.scryfallId||'';const token=name+'|'+Date.now();preview.dataset.request=token;renderFaces([{name:name,url:id?idImgURL(id,false):imgURL(name)}]);preview.classList.add('show');place(x,y);pinned=p;resolveFaces(el).then(faces=>{if(preview.dataset.request!==token)return;renderFaces(faces);place(x,y)})}
function hideCard(){if(preview&&!pinned)preview.classList.remove('show')}
function cardTarget(event){return event.target&&event.target.closest?event.target.closest('.card-name'):null}
document.addEventListener('mouseover',event=>{const el=cardTarget(event);if(!el||el.contains(event.relatedTarget))return;showCard(el,event.clientX,event.clientY)});
document.addEventListener('mousemove',event=>{if(cardTarget(event))place(event.clientX,event.clientY)});
document.addEventListener('mouseout',event=>{const el=cardTarget(event);if(!el||el.contains(event.relatedTarget))return;hideCard()});
document.addEventListener('focusin',event=>{const el=cardTarget(event);if(!el)return;const r=el.getBoundingClientRect();showCard(el,r.right,r.top)});
document.addEventListener('focusout',event=>{if(cardTarget(event))hideCard()});
document.addEventListener('click',event=>{const el=cardTarget(event);if(el&&matchMedia('(hover:none)').matches){event.preventDefault();showCard(el,innerWidth/2,innerHeight/3,true);return}if(preview&&pinned&&!el){pinned=false;preview.classList.remove('show')}});
document.addEventListener('click',async event=>{const b=event.target&&event.target.closest?event.target.closest('.copy[data-target]'):null;if(!b)return;const target=document.getElementById(b.dataset.target);if(!target)return;const text=target.textContent;try{await navigator.clipboard.writeText(text)}catch(_){const a=document.createElement('textarea');a.value=text;document.body.appendChild(a);a.select();document.execCommand('copy');a.remove()}const old=b.textContent;b.textContent='Copied';setTimeout(()=>b.textContent=old,1200)});
function faceStat(container,label,value){if(value===undefined||value===null||value==='')return;const item=document.createElement('div');item.className='stat';const strong=document.createElement('b');strong.textContent=label;item.appendChild(strong);item.appendChild(document.createTextNode(String(value)));container.appendChild(item)}
function buildFaceRules(face,index,card){const panel=document.createElement('div');panel.className='oracle face-rules '+(index===0?'front-rules':'back-rules');const eye=document.createElement('div');eye.className='eyebrow';eye.textContent=(index===0?'Front face':'Back face')+(card.set_name?' · '+card.set_name:'');panel.appendChild(eye);const h=document.createElement('h3');h.textContent=face.name||card.name;panel.appendChild(h);if(face.type_line){const type=document.createElement('p');const b=document.createElement('b');b.textContent=face.type_line;type.appendChild(b);panel.appendChild(type)}const rules=document.createElement('p');rules.className='face-oracle-text';rules.textContent=face.oracle_text||'No rules text.';panel.appendChild(rules);const stats=document.createElement('div');stats.className='stats';faceStat(stats,'Mana cost',face.mana_cost||'None');faceStat(stats,'Mana value',card.cmc);if(face.power!==undefined||face.toughness!==undefined)faceStat(stats,'Power / toughness',(face.power||'—')+' / '+(face.toughness||'—'));if(face.loyalty!==undefined)faceStat(stats,'Loyalty',face.loyalty);if(face.defense!==undefined)faceStat(stats,'Defense',face.defense);faceStat(stats,'Face',index===0?'Front':'Back');panel.appendChild(stats);return panel}
async function hydrateLeadCard(){const lead=document.querySelector('.card-lead[data-card-name]');if(!lead||lead.querySelector('.card-face-pair'))return;const name=lead.dataset.cardName,id=lead.dataset.scryfallId||'';if(!name)return;let card;try{card=await resolveCardObject(name,id)}catch(_){return}const faces=(card.card_faces||[]).filter(face=>face.image_uris&&face.image_uris.normal);if(faces.length<2)return;lead.classList.add('dfc-lead');const pair=document.createElement('div');pair.className='card-face-pair';faces.slice(0,2).forEach((face,index)=>{const figure=document.createElement('figure');const img=document.createElement('img');img.src=face.image_uris.normal;img.alt=(face.name||name)+' '+(index===0?'front':'back')+' face';img.loading=index===0?'eager':'lazy';figure.appendChild(img);const cap=document.createElement('figcaption');const label=document.createElement('span');label.className='face-label';label.textContent=index===0?'Front face':'Back face';cap.appendChild(label);cap.appendChild(document.createTextNode(face.name||name));figure.appendChild(cap);pair.appendChild(figure)});const oldImage=Array.from(lead.children).find(child=>child.tagName==='IMG');if(oldImage)oldImage.replaceWith(pair);else lead.insertBefore(pair,lead.firstChild);const grid=document.createElement('div');grid.className='dfc-rules-grid';faces.slice(0,2).forEach((face,index)=>grid.appendChild(buildFaceRules(face,index,card)));const oldOracle=Array.from(lead.children).find(child=>child.classList&&child.classList.contains('oracle'));if(oldOracle)oldOracle.replaceWith(grid);else lead.appendChild(grid)}
hydrateLeadCard();
const sections=[...document.querySelectorAll('.article section[id]')],links=[...document.querySelectorAll('.toc a')];if('IntersectionObserver' in window){const ob=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting)links.forEach(a=>a.classList.toggle('active',a.getAttribute('href')==='#'+e.target.id))}),{rootMargin:'-16% 0px -72% 0px'});sections.forEach(s=>ob.observe(s))}
function updateProgress(){const d=document.documentElement,max=d.scrollHeight-innerHeight,pct=max>0?(scrollY/max)*100:0;document.body.style.setProperty('--progress',pct+'%')}addEventListener('scroll',updateProgress,{passive:true});updateProgress();
/* CR_CARD_PREVIEW_RUNTIME_END */'''

ROW_PLAIN_RE = re.compile(r'(<div class="row">\s*<span class="qty">[^<]+</span>)([^<]+)(</div>)')
CARD_NAME_RE = re.compile(r'class="printings[^>]*\bdata-card="([^"]+)"')
ORIGINAL_ID_RE = re.compile(r'class="printing original-printing"[^>]*\bdata-scryfall-id="([^"]+)"')
HERO_ID_RE = re.compile(r'https://api\.scryfall\.com/cards/([0-9a-f-]{36})\?')
LEAD_RE = re.compile(r'<div class="card-lead(?P<rest>[^"]*)"(?P<attrs>[^>]*)>')
RUNTIME_RE = re.compile(r'/\* CR_CARD_PREVIEW_RUNTIME_START \*/.*?/\* CR_CARD_PREVIEW_RUNTIME_END \*/', re.S)
CSS_RE = re.compile(r'<style id="cr-card-image-standard">.*?</style>', re.S)
PREVIEW_RE = re.compile(r'<div(?:\s+class="preview")?\s+id="preview"[^>]*>\s*(?:<img[^>]*?/?>|<div class="preview-track"></div>)\s*</div>')
EMPTY_SUMMARY_RE = re.compile(r'<small>No official deck products containing.*?</small>', re.S)


def article_identity(text: str) -> tuple[str | None, str | None]:
    m = CARD_NAME_RE.search(text)
    name = html.unescape(m.group(1)) if m else None
    m = ORIGINAL_ID_RE.search(text)
    sid = m.group(1) if m else None
    if not sid:
        m = HERO_ID_RE.search(text)
        sid = m.group(1) if m else None
    return name, sid


def link_plain_rows(text: str) -> tuple[str, int]:
    count = 0
    def repl(m: re.Match[str]) -> str:
        nonlocal count
        raw = m.group(2)
        name = html.unescape(raw.strip())
        if not name:
            return m.group(0)
        count += 1
        return m.group(1) + '<span class="card-name" data-card="' + html.escape(name, quote=True) + '" tabindex="0">' + raw.strip() + '</span>' + m.group(3)
    return ROW_PLAIN_RE.sub(repl, text), count


def annotate_lead(text: str, name: str | None, sid: str | None) -> str:
    if not name:
        return text
    def repl(m: re.Match[str]) -> str:
        attrs = m.group('attrs')
        if 'data-card-name=' in attrs:
            return m.group(0)
        extra = ' data-card-name="' + html.escape(name, quote=True) + '" data-dfc-mode="auto"'
        if sid:
            extra += ' data-scryfall-id="' + sid + '"'
        return '<div class="card-lead' + m.group('rest') + '"' + extra + attrs + '>'
    return LEAD_RE.sub(repl, text, count=1)


def migrate_text(text: str) -> tuple[str, dict[str, int]]:
    stats = {'linked_rows': 0, 'zero_summaries': 0, 'runtime_replaced': 0, 'preview_replaced': 0, 'lead_annotated': 0}
    name, sid = article_identity(text)
    before = text
    text, stats['linked_rows'] = link_plain_rows(text)
    stats['zero_summaries'] = len(EMPTY_SUMMARY_RE.findall(text))
    text = EMPTY_SUMMARY_RE.sub('<small>0</small>', text)

    if CSS_RE.search(text):
        text = CSS_RE.sub(CSS_BLOCK, text)
    elif '</head>' in text:
        text = text.replace('</head>', CSS_BLOCK + '\n</head>', 1)

    n = len(PREVIEW_RE.findall(text))
    if n:
        text = PREVIEW_RE.sub('<div id="preview"><div class="preview-track"></div></div>', text, count=1)
        stats['preview_replaced'] = 1

    if RUNTIME_RE.search(text):
        text = RUNTIME_RE.sub(RUNTIME, text, count=1)
        stats['runtime_replaced'] = 1

    old = text
    text = annotate_lead(text, name, sid)
    stats['lead_annotated'] = int(text != old)
    return text, stats


def candidate_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    return sorted(p for p in root.rglob('*.html') if p.name != 'index.html')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('root', type=Path, nargs='?', default=Path('.'))
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--report', type=Path)
    args = ap.parse_args()
    totals = {'files': 0, 'changed': 0, 'linked_rows': 0, 'zero_summaries': 0, 'runtime_replaced': 0, 'preview_replaced': 0, 'lead_annotated': 0}
    changed_files: list[str] = []
    for path in candidate_files(args.root):
        original = path.read_text(encoding='utf-8')
        migrated, stats = migrate_text(original)
        totals['files'] += 1
        for k, v in stats.items(): totals[k] += v
        if migrated != original:
            totals['changed'] += 1
            changed_files.append(str(path))
            if not args.check:
                path.write_text(migrated, encoding='utf-8')
    result = {'status': 'FAIL' if args.check and totals['changed'] else 'PASS', **totals, 'changedFiles': changed_files[:100]}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
    return 1 if args.check and totals['changed'] else 0

if __name__ == '__main__':
    raise SystemExit(main())
