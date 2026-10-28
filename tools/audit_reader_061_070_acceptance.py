#!/usr/bin/env python3
"""Audit Reader 061-070 wave acceptance against current candidate evidence.

This is a blocking audit, not an acceptance shortcut. It deliberately returns
success when accurately reporting a blocked wave, so release CI can continue.
Only independent, event-specific evidence should clear deck attribution blockers.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
from bs4 import BeautifulSoup
from reader_experience_v3 import editorial_word_count, reading_time_minutes

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"audit/reader-v31-061-070"
METRICS=OUT/"ACCEPTANCE-AUDIT.json"
REPORT=OUT/"ACCEPTANCE-AUDIT.md"
FILES=["061-maze-of-ith.html","062-the-tabernacle-at-pendrell-vale.html",
"063-moat.html","064-nether-void.html","065-the-abyss.html",
"066-land-tax.html","067-sylvan-library.html","068-concordant-crossroads.html",
"069-eureka.html","070-candelabra-of-tawnos.html"]
def load(p):return json.loads(p.read_text(encoding="utf-8"))
def render():
    rows=[];blockers=[]
    for i,name in enumerate(FILES):
        n=i+61; p=ROOT/name
        html=p.read_text(encoding="utf-8")
        soup=BeautifulSoup(html,"lxml")
        intro=soup.select_one("#opening > aside.play-vignette")
        decks=soup.select("details.deck")
        dossier=load(ROOT/"research-dossiers/numbered-wave-02"/name.replace(".html",".json"))
        words=editorial_word_count(soup)
        sourceids={x["sourceId"] for x in dossier.get("sources",[])}
        source_verification_status="source-scoped" if n in (61,62) else "printing-and-mechanics-only"
        deck_evidence=dossier.get("deckEvidence",[])
        unresolved=[x.get("deckName","unnamed") for x in deck_evidence if x.get("sourceId")=="archived-deck-candidate"]
        if unresolved:
           blockers.append({"entry":n,"kind":"deck-event-provenance",
               "reason":"Deck archive snapshot is not a source verifying player/date/event/finish. Verify each documentary registration against its contemporaneous record.",
               "names":unresolved})
        if not intro or soup.body.get("data-reader-experience")!="v3":
           blockers.append({"entry":n,"kind":"reader-structure","reason":"Missing Reader V3 story or experience flag"})
        if not (intro and intro.get("data-vignette-deck-reference") in {d.select_one("summary strong").get_text(" ",strip=True) for d in decks if d.select_one("summary strong")}):
           blockers.append({"entry":n,"kind":"vignette-deck","reason":"Story deck missing from its own archive"})
        if intro and n>=63:
           # The 063-070 focused migration does not verify the full inherited
           # editorial article, only core mechanics and first printing.
           blockers.append({"entry":n,"kind":"full-editorial-claim-review",
               "reason":"Remaining inherited sections/tournament claims not independently audited. Focused source checks alone do not meet roadmap wave acceptance."})
        rows.append({"entry":n,"file":name,"card":soup.body.get("data-article-card"),
          "articleSha256":hashlib.sha256(p.read_bytes()).hexdigest(),
          "readerV3":bool(intro),"storyTitle":intro.select_one("h3").get_text(" ",strip=True) if intro else None,
          "editorialWords":words,"readMinutes":reading_time_minutes(words),
          "visibleArchiveDecks":len(decks),"sourceIds":sorted(sourceids),
          "candidateEvidenceClass":source_verification_status,"unverifiedInheritedDeckRows":len(unresolved)})
    state=load(ROOT/"CURRENT-STATE.json");progress=load(ROOT/"site-progress.json")
    if state.get("readerV31LatestCheckpoint",{}).get("nextArticle")!=61 or progress["progress"]["completed"]!=60:
       raise ValueError("Accepted baseline changed before wave-level sign-off")
    result={"scope":"061-070","asOf":"2026-10-28","acceptanceStatus":"blocked",
      "originalBaselineReader":"051-060","currentAcceptedReaderCount":60,
      "archiveCountExpected":1505,"candidateArticles":len(rows),"blockerCount":len(blockers),
      "eventProvenanceGaps":sum(x["unverifiedInheritedDeckRows"] for x in rows),
      "articles":rows,"blockers":blockers,
      "acceptancePrerequisites":[
        "Bind every retained claimed tournament registration to event-specific sources; label unverifiable decks as curated examples instead of silently granting false registration.",
        "Complete factual editorial read and independent claim evidence for inherited sections in 063-070, checking old printings, legality and period rules.",
        "Generate accepted 061-070 ten-page migration/story ledger, baseline-to-current hashes, unique opening and source review report.",
        "Run all quick/refresh/full/link/browser tests and verify post-merge Pages before advancing accepted checkpoint to 070.",
        "Update roadmap, CURRENT-STATE.json and site-progress only after sign-off, without granting partial 12-point gate weights."]}
    return result
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--apply",action="store_true");args=ap.parse_args()
    result=render()
    if args.apply:
       OUT.mkdir(parents=True,exist_ok=True)
       METRICS.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
       l=["# Reader V3.1 061-070 acceptance gate — evidence audit (2026-10-28)","",
         "**Decision: BLOCKED.** Ten individually updated pages exist, but this does not yet meet the documented source-provenance and complete-claim standards of a validated migration checkpoint.",
         "","- Accepted numbered Reader checkpoint: **051-060** (60/100); new **candidate** pages: **10**.",
         f"- Unresolved event-provenance deck rows: **{result['eventProvenanceGaps']}** across source-repaired dossiers.",
         f"- Open evidence items: **{result['blockerCount']}**. No implied completion of the 061-070 migration ledger.",
         "", "| Entry | Card | Words | Decks | Event source gaps | SHA-256 |",
         "|---:|---|---:|---:|---:|---|"]
       for x in result["articles"]:
          l.append(f"| {x['entry']:03d} | {x['card']} | {x['editorialWords']} | {x['visibleArchiveDecks']} | {x['unverifiedInheritedDeckRows']} | `{x['articleSha256']}` |")
       l+=["","## Blockers"]
       for b in result["blockers"]:
          l.append(f"- **{b['entry']:03d}: {b['kind']}** — {b['reason']}"+(" ("+", ".join(b["names"])+")" if b.get("names") else ""))
       l+=["","## Required acceptance steps"]
       l += [f"{i}. {x}" for i,x in enumerate(result["acceptancePrerequisites"],1)]
       l+=["","This is a preservation-oriented **negative acceptance decision**. CI that validates the audit must not conflate a clean site build with approval of all underlying research."]
       REPORT.write_text("\n".join(l)+"\n",encoding="utf-8")
    else:
       if not METRICS.exists() or load(METRICS)!=result:
          raise ValueError("061-070 acceptance audit missing or out of sync")
       if result["acceptanceStatus"]!="blocked" or not result["blockers"]:
          raise ValueError("Unreviewed checkpoint incorrectly promoted")
    print(f"PASS 061-070 acceptance evidence audited: {len(result['articles'])} candidates, {len(result['blockers'])} blockers, {result['eventProvenanceGaps']} unbound inherited deck rows; acceptance remains 60/100.")
if __name__=="__main__":main()
