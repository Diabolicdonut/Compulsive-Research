#!/usr/bin/env python3
"""Build source-scoped Reader V3.1 individual drafts for 083-092.

User editorial approval of previous 073-082 is separate from formal accepted
checkpoint 051-060; never grant checkpoint weights without archival evidence.
"""
from __future__ import annotations
import argparse, html, json, re, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import prepare_reader_063_072 as impl
BATCH=ROOT/"research-dossiers/reader-v31-083-092"
PLAN=BATCH/"editorial-candidates.json"
METRICS=ROOT/"validation/reader-v3.1-083-092-candidate-metrics.json"
impl.BATCH=BATCH;impl.PLAN=PLAN;impl.METRICS=METRICS

def goblin_study_deck():
    groups=[
      ("Creatures",[("Goblin Balloon Brigade",4),("Mons's Goblin Raiders",4),
           ("Goblin King",4),("Goblin Chirurgeon",4)]),
      ("Spells",[("Goblin Grenade",4),("Lightning Bolt",4),("Fireball",4),
           ("Shatter",4),("Stone Rain",4)]),
      ("Lands",[("Mountain",24)])]
    total=sum(q for _,cards in groups for _,q in cards)
    assert total==60
    parts=['<details class="deck" data-deck-kind="curated-example" data-main-count="60" data-sideboard-count="0" data-legality-as-of="1994" data-reviewed-by="Compulsive Research" open="">',
       '<summary><span><strong>Goblin Grenade — 1994 Goblin burn study</strong><small>Original 1994 teaching model · 60 cards · not a tournament registration</small></span><span class="plus">+</span></summary>',
       '<div class="deck-body"><span class="provenance-badge">Curated 1994 card-pool study, not historical event evidence</span>',
       '<p>This 60 cards in the main deck illustration is an original educational model using cards printed no later than Fallen Empires in November 1994. It has no claimed historical player, tournament event, result, opponent, registration or sideboard.</p>',
       '<div class="deck-meta"><div><b>Goblin Grenade — 1994 Goblin burn study</b><div class="small">Main deck 60 · No recorded sideboard</div></div></div>',
       '<div class="deck-columns"><div class="deck-col">']
    lines=[]
    for category,cards in groups:
       n=sum(q for _,q in cards)
       parts.append('<div class="group"><h4>'+category+' · '+str(n)+'</h4>')
       lines.append(category+' · '+str(n))
       for name,qty in cards:
          parts.append('<div class="row"><span class="qty">'+str(qty)+'</span><span class="card-name" data-card="'+html.escape(name,quote=True)+'" tabindex="0">'+html.escape(name)+'</span></div>')
          lines.append(str(qty)+' '+name)
       parts.append('</div>')
    parts+=['</div></div><pre id="deck-091-goblin-grenade-study" hidden>'+html.escape(chr(10).join(lines))+'</pre></div></details>']
    return ''.join(parts)

def bootstrap(spec):
    n=spec["n"];path=ROOT/f"{n:03d}-{spec['slug']}.html"
    raw=path.read_text(encoding="utf-8")
    if 'data-reader-experience="v3"' in raw:return
    if n==91:
       old='<div class="deck-archive"></div>'
       if raw.count(old)!=1:raise ValueError("Goblin Grenade empty archive changed; do not duplicate a deck")
       raw=raw.replace(old,'<div class="deck-archive">'+goblin_study_deck()+'</div>')
       raw=raw.replace('No verified historical tournament registration is currently included in this article. The documentary archive remains open for sourced additions.',
          'No verified historical tournament registration is included. The added 1994 60-card model is explicitly an original teaching deck and not a reported tournament result.')
    section='<section id="case-study"><div class="chapter-number">IX · Close play</div><h2>'+html.escape(spec["title"])+'</h2>'+\
         '<p>'+html.escape(spec["lesson"])+'</p><p>'+html.escape(spec["technical"])+'</p>'+\
         '<p>The board position is an original instructional reconstruction. The named archive deck is evidence of a period card pool, not eyewitness match testimony.</p></section>'
    raw=impl.replace_section(raw,"case-study",section)
    raw=re.sub(r'(<a href="#case-study">)[^<]*(</a>)',
       lambda m:m.group(1)+html.escape(spec["title"])+m.group(2),raw,count=1)
    memory='<section id="memory"><div class="chapter-number">XIII · Table memory</div><h2>The choice the rules actually created</h2>'+\
       '<p>'+html.escape(spec["lesson"])+'</p><p>'+html.escape(spec["review"])+'</p>'+\
       '<p>Only verified original card identity and explicitly inspected source evidence support documentary claims; this hypothetical sequence is not attributed to a historical player.</p></section>'
    raw=impl.replace_section(raw,"memory",memory)
    raw=re.sub(r'(<a href="#memory">)[^<]*(</a>)',
       lambda m:m.group(1)+"The choice the rules actually created"+m.group(2),raw,count=1)
    path.write_text(raw,encoding="utf-8")

def main():
    p=argparse.ArgumentParser();p.add_argument("--apply",action="store_true");args=p.parse_args()
    data=impl.read(PLAN);specs=data["articles"]
    if [s["n"] for s in specs]!=list(range(83,93)):raise ValueError("Article range must be exactly 083-092")
    if args.apply:
       rows=[]
       for s in specs:
          bootstrap(s)
          rows.append(impl.candidate(s))
       impl.write(METRICS,{"scope":"083-092","date":"2026-10-28",
         "status":"individual Reader 083-092 candidates only; not formal 081-090 or 091-100 acceptance",
         "priorUserEditorialApproval":"073-082","acceptedReader":60,
         "weightedRoadmapPoints":51,"articles":rows})
    expected=impl.read(METRICS)
    if expected.get("scope")!="083-092":raise ValueError("Metrics from wrong editorial range")
    raise SystemExit(impl.validate(specs,expected["articles"]))

if __name__=="__main__":main()
