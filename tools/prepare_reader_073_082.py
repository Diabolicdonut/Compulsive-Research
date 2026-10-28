#!/usr/bin/env python3
"""Prepare ten Reader 073-082 candidates using the validated 063-072 contract.
Do not advance accepted 051-060 or waive 061-070 wave provenance blockers.
"""
from __future__ import annotations
import argparse, hashlib, html, json, re, sys
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import prepare_reader_063_072 as impl

BATCH=ROOT/"research-dossiers/reader-v31-073-082"
PLAN=BATCH/"editorial-candidates.json"
METRICS=ROOT/"validation/reader-v3.1-073-082-candidate-metrics.json"
impl.BATCH=BATCH
impl.PLAN=PLAN
impl.METRICS=METRICS

def ali_curated_deck():
    groups=[
      ("Creatures",[("Ali from Cairo",4),("Wall of Stone",4),("Dragon Whelp",4)]),
      ("Spells",[("Lightning Bolt",4),("Fireball",4),("Disintegrate",4),("Stone Rain",4),("Shatter",4),("Mana Flare",4)]),
      ("Lands",[("Mountain",24)])
    ]
    size=sum(q for _,cards in groups for _,q in cards)
    if size!=60: raise ValueError(f"Red defense model has {size} cards")
    body=['<details class="deck" data-deck-kind="curated-example" data-main-count="60" data-sideboard-count="0" data-legality-as-of="1994" data-reviewed-by="Compulsive Research" open="">',
       '<summary><span><strong>Ali from Cairo — 1994 Red Defense study</strong><small>Curated 1994 kitchen-table rules study · 60-card main deck · not a historical registration</small></span><span class="plus">+</span></summary>',
       '<div class="deck-body"><span class="provenance-badge">Curated instructional model — no claimed player or event</span>',
       '<p>This explicitly authored study uses 60 cards in the main deck, all printed by the end of 1994; it illustrates Ali from Cairo and defensive red spells. No pilot, tournament finish, event, source-verified matchup or sideboard is asserted.</p>',
       '<div class="deck-meta"><div><b>Ali from Cairo — 1994 Red Defense study</b><div class="small">Main deck 60 · No recorded sideboard</div></div></div>',
       '<div class="deck-columns"><div class="deck-col">']
    lines=[]
    for group,cards in groups:
        total=sum(q for _,q in cards)
        body.append('<div class="group"><h4>'+group+' · '+str(total)+'</h4>')
        lines.append(group+' · '+str(total))
        for name,q in cards:
            body.append('<div class="row"><span class="qty">'+str(q)+'</span><span class="card-name" data-card="'+html.escape(name,quote=True)+'" tabindex="0">'+html.escape(name)+'</span></div>')
            lines.append(str(q)+' '+name)
        body.append('</div>')
    body+=['</div></div><pre id="deck-073-ali-study" hidden>'+html.escape(chr(10).join(lines))+'</pre></div></details>']
    return ''.join(body)

def bootstrap(s):
    p=ROOT/f"{s['n']:03d}-{s['slug']}.html"
    raw=p.read_text(encoding="utf-8")
    if 'data-reader-experience="v3"' in raw:return
    if s['n']==73:
       old='<div class="deck-archive"></div>'
       if raw.count(old)!=1:raise ValueError("Ali archive not empty as expected")
       raw=raw.replace(old,'<div class="deck-archive">'+ali_curated_deck()+'</div>')
       raw=raw.replace("No verified historical tournament registration is currently included in this article. The documentary archive remains open for sourced additions.",
         "No verified historical tournament registration is included. The original 60-card study model is clearly curated and makes no claim of event results.")
    # Replace the inherited templated case studies, 073-082, with specific
    # legal game-state sequences from the editorial plan.
    id="case-study"
    new='<section id="case-study"><div class="chapter-number">IX · Close play</div><h2>'+html.escape(s["title"])+'</h2>'+\
      '<p>'+html.escape(s["lesson"])+'</p><p>'+html.escape(s["technical"])+'</p>'+\
      '<p>This is a reviewed, mechanically illustrative scene. The named Deck Archive is a card-pool reference only, not an eyewitness or tournament match transcript.</p></section>'
    raw=impl.replace_section(raw,id,new)
    raw=re.sub(r'(<a href="#case-study">)[^<]*(</a>)',lambda m:m.group(1)+html.escape(s["title"])+m.group(2),raw,count=1)
    # Dedicated final table memory: do not leave stock prose masking the exact mechanics.
    memory='<section id="memory"><div class="chapter-number">XIII · Table memory</div><h2>What the table actually has to count</h2>'+\
        '<p>'+html.escape(s["lesson"])+'</p><p>'+html.escape(s["review"])+'</p>'+\
        '<p>The scene is original editorial reconstruction, and any inherited tournament lists retain separate documentary status.</p></section>'
    raw=impl.replace_section(raw,"memory",memory)
    raw=re.sub(r'(<a href="#memory">)[^<]*(</a>)',lambda m:m.group(1)+"What the table actually has to count"+m.group(2),raw,count=1)
    p.write_text(raw,encoding="utf-8")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--apply",action="store_true")
    args=ap.parse_args()
    specs=json.loads(PLAN.read_text(encoding="utf-8"))["articles"]
    if [s["n"] for s in specs]!=list(range(73,83)):raise ValueError("Wrong range")
    if args.apply:
      records=[]
      for s in specs:
        bootstrap(s)
        records.append(impl.candidate(s))
      impl.write(METRICS,{"scope":"073-082","date":"2026-10-28",
          "status":"ten individual candidate drafts; NOT approved 071-080 or 081-090 checkpoint",
          "acceptedReader":60,"weightedRoadmapPoints":51,"articles":records})
    metrics=impl.read(METRICS)
    if metrics.get("scope")!="073-082":raise ValueError("Mismatched candidate metric scope")
    raise SystemExit(impl.validate(specs,metrics["articles"]))

if __name__=="__main__":
    main()
