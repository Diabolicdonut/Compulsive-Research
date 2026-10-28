#!/usr/bin/env python3
"""Prepare and verify ten *candidate* Reader V3.1 articles 063-072.

This does not accept the complete 061-070 or 071-080 editorial waves.
The historical 001-060 acceptance ledger and site-progress counters remain unchanged.
Run --apply on a clean staging branch, then --check before each final release.
"""
from __future__ import annotations
import argparse, hashlib, html, json, re
from pathlib import Path
from bs4 import BeautifulSoup
from jsonschema import Draft202012Validator, FormatChecker
from reader_experience_v3 import editorial_word_count, reading_time_minutes

ROOT=Path(__file__).resolve().parents[1]
BATCH=ROOT/"research-dossiers/reader-v31-063-072"
PLAN=BATCH/"editorial-candidates.json"
METRICS=ROOT/"validation/reader-v3.1-063-072-candidate-metrics.json"
EXAMPLE=(ROOT/"062-the-tabernacle-at-pendrell-vale.html").read_text(encoding="utf-8")
STYLE=re.search(r'<style id="cr-reader-experience-v3">[\s\S]*?</style>',EXAMPLE)
if not STYLE: raise RuntimeError("missing accepted Reader V3 stylesheet")
CARD_TEMPLATE=STYLE.group()
SCHEMA=json.loads((ROOT/"templates/research-dossier-v2.schema.json").read_text(encoding="utf-8"))

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))
def write(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def tagged(txt):
    txt=html.escape(txt,quote=False)
    return re.sub(r'\[\[([^\]]+)\]\]', lambda m:
      '<span class="card-name" data-card="'+html.escape(m[1],quote=True)+'" tabindex="0">'+m[1]+'</span>',txt)
def replace_section(s,id,body):
    pat=r'<section id="'+re.escape(id)+r'"[^>]*>[\s\S]*?</section>'
    s,n=re.subn(pat,lambda _:body,s,count=1)
    if n!=1: raise ValueError("missing or multiply found section "+id)
    return s

def curated_power_deck():
    groups=[
     ("Artifacts and enchantments", [("Power Artifact",4),("Basalt Monolith",4),("Grim Monolith",4)]),
     ("Spells", [("Force of Will",4),("Counterspell",4),("Impulse",4),("Brainstorm",4),("Stroke of Genius",2),("Morphling",2)]),
     ("Lands", [("Island",20),("City of Traitors",4),("Ancient Tomb",4)])
    ]
    total=sum(q for _,cards in groups for _,q in cards)
    assert total==60,(total,groups)
    details=['<details class="deck" data-deck-kind="curated-example" data-main-count="60" data-sideboard-count="0" data-legality-as-of="2000" data-reviewed-by="Compulsive Research" open="">',
      '<summary><span><strong>Power Artifact — Basalt Monolith study deck</strong><small>2000-era casual blue artifact model · 60 cards · no tournament registration</small></span><span class="plus">+</span></summary>',
      '<div class="deck-body"><span class="provenance-badge">Curated illustrative model, not historical result</span>',
      '<p>An explicitly authored demonstration of 60 cards in the main deck with Power Artifact, Basalt Monolith and Grim Monolith, using cards available by 2000. No historical pilot, event, placement or sideboard is asserted.</p>',
      '<div class="deck-meta"><div><b>Power Artifact — Basalt Monolith study deck</b><div class="small">Main deck 60 · No sideboard</div></div></div>',
      '<div class="deck-columns"><div class="deck-col">']
    for title,cards in groups:
       details.append('<div class="group"><h4>'+title+' · '+str(sum(q for _,q in cards))+'</h4>')
       for name,q in cards: details.append('<div class="row"><span class="qty">'+str(q)+'</span><span class="card-name" data-card="'+name+'" tabindex="0">'+name+'</span></div>')
       details.append('</div>')
    details+=['</div></div>']
    lines=[]
    for title,cards in groups:
       lines.append(title+' · '+str(sum(q for _,q in cards)))
       for name,q in cards: lines.append(str(q)+' '+name)
    details+=['<pre id="deck-072-power-artifact-study" hidden>'+html.escape(chr(10).join(lines))+'</pre></div></details>']
    return ''.join(details)

def candidate(s):
    n=s['n'];slug=s['slug'];card=s['card'];article=ROOT/f"{n:03d}-{slug}.html"
    raw=article.read_text(encoding="utf-8")
    if 'data-reader-experience="v3"' in raw:
        if not (BATCH/f"{n:03d}-story-candidate.json").exists():
            raise ValueError(f"already altered 0{n} without story artifact")
        return
    soup=BeautifulSoup(raw,"lxml")
    opener=soup.select_one('#opening')
    lead=opener.select_one('.card-lead') if opener else None
    if lead is None: raise ValueError(f"{article.name}: card-lead missing")
    intro_title=opener.select_one('h2').get_text(" ",strip=True)
    lead_html=str(lead)
    # Correct major Oracle error present before the migration.
    if n==71:
        lead_html=lead_html.replace("As an additional cost to cast this spell, sacrifice an artifact. Search your library for an artifact card.",
         "Sacrifice an artifact. If you do, search your library for an artifact card.")
    oracle=BeautifulSoup(lead_html,"lxml").select_one('.card-lead .oracle p')
    if n==71 and oracle and 'As an additional cost' in oracle.get_text(' ',strip=True):
        raise ValueError('Transmute Artifact main Oracle lead still asserts incorrect additional cost')
    # Case-specific factual text fully replaces inherited generic sections.
    story=tagged(s['story'])
    vignette='<aside class="play-vignette" aria-label="First-person table story for '+html.escape(card,quote=True)+'"'+\
      ' data-featured-card="'+html.escape(card,quote=True)+'" data-vignette-deck-reference="'+html.escape(s['deck'],quote=True)+'"'+\
      ' data-vignette-era="'+html.escape(s['era'],quote=True)+'" data-vignette-matchup="'+html.escape(s['matchup'],quote=True)+'"'+\
      ' data-vignette-opening="'+s['mode']+'" data-vignette-scenario="representative-recollection"'+\
      ' data-vignette-voice="first-person-recollection"><div class="vignette-label">A story from the table</div><h3>'+html.escape(s['title'])+'</h3><p>'+story+'</p>'
    if s.get('payments'):
       vignette+='<script class="vignette-mana-data" type="application/json">'+json.dumps({"schema_version":1,"costs":s["payments"]},ensure_ascii=False)+'</script>'
    vignette+='<script class="vignette-review-data" type="application/json">'+json.dumps({
      "reviewed":"2026-10-27","basis":s["review"],
      "scenario":"representative reconstruction; not a recorded match, quotation or eyewitness account"
     },ensure_ascii=False)+'</script></aside>'
    opening='<section id="opening"><div class="chapter-number">I · The central bargain</div><h2>'+html.escape(intro_title)+'</h2>'+\
      '<p class="opening dropcap">'+html.escape(s['intro'])+'</p><p>'+html.escape(s['lesson'])+'</p>'+\
      '<p>What follows separates the original printed card, the exact modern rules object and illustrative play from attributed deck evidence. The first-person scene is a teaching reconstruction, not a match transcript.</p>'+lead_html+vignette+'</section>'
    raw=replace_section(raw,"opening",opening)
    for id,chapter,title,text in [
     ("origin","II · Origin","The original printing and its bargain",s['origin']),
     ("mechanics","III · Rules texture","The governing rule, not the remembered shorthand",s['lesson']+" "+s['technical']),
     ("history","IV · Tournament evolution","What the documented card pool actually proves",s['history']),
     ("technical","VI · Technical play","The line that requires exact sequencing",s['technical'])]:
       old=soup.select_one("section#"+id)
       if old is None: raise ValueError("section missing: "+id)
       original=old.get_text(" ",strip=True)
       new='<section id="'+id+'"><div class="chapter-number">'+html.escape(chapter)+'</div><h2>'+html.escape(title)+'</h2>'+\
         '<p>'+html.escape(text)+'</p><p>Any additional play line in this article is a rules illustration. Its publication establishes neither a particular match result nor a named player’s actions unless an independently cited record actually does so.</p></section>'
       raw=replace_section(raw,id,new)
       raw=raw.replace('<a href="#'+id+'">'+html.escape(old.select_one('h2').get_text(' ',strip=True))+'</a>',
                      '<a href="#'+id+'">'+html.escape(title)+'</a>',1)
    # 071 and 072 have stock case study content. Replace with detailed verified sequences.
    if n in (71,72):
       casestudy='<section id="case-study"><div class="chapter-number">IX · Close play</div><h2>'+html.escape(s['title'])+'</h2>'+\
            '<p>'+html.escape(s['lesson'])+'</p><p>'+html.escape(s['technical'])+'</p>'+\
            '<p>This particular scene is a constructed instructional game state. The deck source is identified in the opening, not a claimed eyewitness transcript.</p></section>'
       raw=replace_section(raw,"case-study",casestudy)
       raw=re.sub(r'(<a href="#case-study">)[^<]*(</a>)',lambda m:m.group(1)+html.escape(s["title"])+m.group(2),raw,count=1)
    if n==70:
        raw=raw.replace("a legal Legacy choice today","a historical Legacy card, banned since June 29, 2026")
    if n==71:
       raw=raw.replace("As an additional cost to cast this spell, sacrifice an artifact. Search your library for an artifact card.",
                         "Sacrifice an artifact. If you do, search your library for an artifact card.")
       raw=raw.replace("the sacrifice as an additional cost","the artifact sacrifice during spell resolution")
       raw=raw.replace("sacrificing an artifact as an additional cost","sacrificing an artifact during spell resolution")
    if n==72:
        # This article genuinely has no tournament deck; use a clearly nonhistorical model.
        old='<div class="deck-archive"></div>'
        if raw.count(old)!=1: raise ValueError("power archive is not empty as expected")
        raw=raw.replace(old,'<div class="deck-archive">'+curated_power_deck()+'</div>')
        raw=raw.replace('No verified historical tournament registration is currently included in this article. The documentary archive remains open for sourced additions.',
          'No verified historical tournament registration is currently included. One clearly labeled, original 60-card teaching model demonstrates Power Artifact + Basalt Monolith; it has no claimed pilot, placement, event or sideboard.')
    original_card_soup=BeautifulSoup(raw,"lxml")
    titles={x.get_text(" ",strip=True) for x in original_card_soup.select('details.deck summary strong')}
    if s["deck"] not in titles: raise ValueError(f"{n} deck title not found: {s['deck']}")
    raw=raw.replace("</style></head>","</style>"+CARD_TEMPLATE+"</head>",1)
    raw=raw.replace('data-research-status="complete"','data-reader-experience="v3" data-research-status="in-research" data-vignette-specificity="period-grounded-oral-history"',1)
    raw=re.sub(r'<span class="pill"[^>]*>Approximately \d+ minute read</span>',
         '<span class="pill" data-reading-word-count="0" data-reading-time-wpm="200">Approximately 0 minute read</span>',raw,count=1)
    # Append a printed-source citation, without treating a generic deck site as verified play-by-play.
    source_items='<li><a href="'+html.escape(s['url'],quote=True)+'">'+html.escape(card)+' — first printing and Oracle record</a><span>Original '+html.escape(s['set'])+' printing, credited artist and rules; original text and later Oracle wording are separate historical objects.</span></li>'+\
      '<li><a href="https://magic.wizards.com/en/rules">Wizards Comprehensive Rules</a><span>Current timing, payments, targets and game actions checked for the reconstructed play.</span></li>'
    if s.get("extraSource"):
        source_items+='<li><a href="'+html.escape(s['extraSource'],quote=True)+'">Dated Wizards primary historical/rules update</a><span>Specific rules-change or ban-list event described in this article.</span></li>'
    raw=raw.replace('</ul>\n<p class="editor-note">The gallery begins with the original printing',
                     source_items+'</ul>\n<p class="editor-note">The gallery begins with the original printing',1)
    if s["url"] not in raw: raise ValueError("source insertion missing")
    # Update source-specific V2 dossier instead of pretending all old secondary listings are verified.
    path=ROOT/f"research-dossiers/numbered-wave-02/{n:03d}-{slug}.json"
    dossier=read(path)
    dossier['canonicalIdentity'].pop("originalPrintedText",None)
    dossier['canonicalIdentity']['identityNotes']="Original "+s['set']+" "+s['date']+" credited to "+s["artist"]+"; printing ID remains from accepted snapshot. Modern Oracle text is not misidentified as original printed wording. Verified focused mechanics source: "+s["url"]
    if n==71:
       dossier["canonicalIdentity"]["currentOracleText"]="Sacrifice an artifact. If you do, search your library for an artifact card. If that card's mana value is less than or equal to the sacrificed artifact's mana value, put it onto the battlefield. If it's greater, you may pay {X}, where X is the difference. If you do, put it onto the battlefield. If you don't, put it into its owner's graveyard. Then shuffle."
    dossier['originalContext']={"setEnvironment":s['set']+" original printing, "+s['date'],
      "designPurpose":s["intro"],"initialReception":"No invented contemporary launch reception. Narrative interpretation is separated from published historical evidence.","sourceIds":["original-printing","official-rules"]}
    dossier['loreContext']={"scope":"flavor-only","summary":"Original artwork credit "+s['artist']+"; no undocumented canonical story or attributed quote invented.","relatedStoryCards":[],"sourceIds":["original-printing"]}
    dossier['competitiveTimeline']=[{"date":s["date"],"event":s["set"]+" initial release","significance":s["card"]+" initial printed identity; original artist "+s["artist"]+".","sourceIds":["original-printing"]}]
    if n==70: dossier['competitiveTimeline'].append({"date":"2026-06-29","format":"Legacy","significance":"Wizards bans Candelabra of Tawnos from Legacy, effective the same day. Older deck examples are historical only.","sourceIds":["dated-primary"]})
    if n==72: dossier['competitiveTimeline'].append({"date":"2006-07-14","significance":"Wizards formally removed power-level errata preventing Basalt Monolith from untapping itself; modern Power Artifact cost reduction supports unlimited colorless mana.","sourceIds":["dated-primary"]})
    dossier["playbook"]={
      "role":s["intro"],"deckRequirements":"Check color requirements, actual mana producers and supporting card pool; do not infer a historical player from an illustrative scene.",
      "copyCount":"Consult documentary deck rows for exact observed counts; illustrative models do not prove event popularity.",
      "mulligans":"Do not treat a combo or lock piece as a mana source or early threat without the cards required to support it.",
      "sequencing":s["technical"],"sideboarding":"Specific opponent-dependent decisions require real format/date and opposing deck evidence.",
      "commonMistakes":s["lesson"]}
    dossier["counterplay"]={
      "directAnswers":"Appropriate counterspells or removal at the legal timing window, or attacking the enabling cards and resources.",
      "engineDisruption":"Check the supporting artifacts, enchantments, creatures or mana engine separately from the featured card.",
      "timingWindows":s["technical"],"racing":"Compare the setup cost with opposing clock and available mana.","sideboarding":"No blanket sideboard advice without a verified deck pairing."}
    if n==72:
       dossier['deckEvidence']=[{"deckKind":"curated-example","deckName":s["deck"],"format":"2000-era casual Type I teaching pool","date":"2000","sourceId":"original-printing","reviewedBy":"Compulsive Research: explicitly invented 60-card model, no historical event"}]
    dossier["claims"]=[{"claimId":"printing-identity","summary":s["set"]+" "+s["date"]+", credited artist "+s["artist"]+".","sourceIds":["original-printing"],"confidence":"high","asOf":"2026-10-27"},
      {"claimId":"mechanics-sequence","summary":s["lesson"]+" "+s["technical"],"sourceIds":["original-printing","official-rules"],"confidence":"high","asOf":"2026-10-27"}]
    if s.get("extraSource"): dossier["claims"].append({"claimId":"dated-update","summary":s["history"],"sourceIds":["dated-primary"],"confidence":"high","asOf":"2026-10-27"})
    dossier["sources"]=[
      {"sourceId":"original-printing","title":card+" original printing and rulings","url":s["url"],"sourceType":"database","accessedDate":"2026-10-27","supports":"Original date, printed card, artist and explicit rulings."},
      {"sourceId":"official-rules","title":"Magic Comprehensive Rules","url":"https://magic.wizards.com/en/rules","sourceType":"primary","accessedDate":"2026-10-27","supports":"Current triggered ability, costs, timing, targeting, casting and resolution mechanics."}
    ]
    if s.get("extraSource"):dossier["sources"].append({"sourceId":"dated-primary","title":card+" dated historical ruling / policy","url":s["extraSource"],"sourceType":"contemporary-secondary" if "mtgprintrun.com" in s["extraSource"] else "primary","accessedDate":"2026-10-27","supports":"Specifically dated historical update, not general deck provenance."})
    # Point inherited lists to *their own internal archive snapshot*, never to
    # the original-printing/rules source as fake proof of tournament attribution.
    dossier["sources"].append({"sourceId":"archived-deck-candidate",
       "title":"Preserved Compulsive Research deck-archive entry — external verification pending",
       "url":"https://github.com/Diabolicdonut/Compulsive-Research/blob/main/"+article.name,
       "sourceType":"database","accessedDate":"2026-10-27",
       "supports":"Only the text of a preserved candidate deck list, NOT verification of player, date, registration or placement."})
    for deck in dossier.get("deckEvidence",[]):
       deck["sourceId"]="archived-deck-candidate"
       deck["reviewedBy"]="Inherited or newly authored candidate; independent historical attribution is unverified"
    if n==72:
       dossier["deckEvidence"][0]["reviewedBy"]="Explicitly authored 60-card demonstration, NOT an actual historical registration"
    dossier["researchStatus"]="in-research"
    dossier["review"]={"historicalReviewDate":"2026-10-27","currentInformationAsOf":"2026-10-27",
      "editorialReviewer":"Compulsive Research focused 063-072 candidate preparation",
      "openQuestions":["Verify inherited third-party tournament registrations and older article sections separately. These core-mechanics fixes alone do not accept the complete Reader migration wave."]}
    problems=list(Draft202012Validator(SCHEMA,format_checker=FormatChecker()).iter_errors(dossier))
    if problems: raise ValueError(str(n)+" dossier errors: "+"; ".join(x.message for x in problems[:4]))
    path.write_text(json.dumps(dossier,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    # Derive metadata without counting decklists, printing galleries or embedded JSON.
    parsed=BeautifulSoup(raw,"lxml")
    words=editorial_word_count(parsed); minutes=reading_time_minutes(words)
    raw,n1=re.subn(r'<span class="pill"[^>]*>Approximately \d+ minute read</span>',
      lambda _:f'<span class="pill" data-reading-word-count="{words}" data-reading-time-wpm="200">Approximately {minutes} minute read</span>',raw,count=1)
    raw,n2=re.subn(r'(<article class="article" data-expanded-word-count=")\d+(")',
      lambda m:m.group(1)+str(words)+m.group(2),raw,count=1)
    if n1!=1 or n2!=1: raise ValueError(f"article {n} derived reader counter not replaced")
    article.write_text(raw,encoding="utf-8")
    rec={"entry":n,"card":card,"file":article.name,"title":s["title"],"deckReference":s["deck"],
       "era":s["era"],"matchup":s["matchup"],"openingMode":s["mode"],
       "story":BeautifulSoup(story,"lxml").get_text(" ",strip=True),
       "storyWords":len(re.findall(r"\b[\w’'-]+\b",BeautifulSoup(story,"lxml").get_text(" ",strip=True))),
       "payments":s.get("payments"),"review":s["review"],"sources":[s["url"],"https://magic.wizards.com/en/rules"]+([s["extraSource"]] if s.get("extraSource") else []),
       "claim":"representative reconstruction; not a historical match or quotation",
       "candidateStatus":"not accepted; pending ten-article checkpoint and deeper deck research"}
    write(BATCH/f"{n:03d}-story-candidate.json",rec)
    write(BATCH/f"{n:03d}-review.json",{"entry":n,"card":card,"date":"2026-10-27","sourceEvidence":rec["sources"],"scene":rec["review"],"namedDeck":s["deck"],
      "deckStatus":"curated model, not a historic registration" if n in (69,71,72) else "inherited named deck archive; source attribution still requires individual verification",
      "status":"candidate only, not batch accepted"})
    return {"entry":n,"card":card,"editorialWords":words,"readMinutes":minutes,"storyWords":rec["storyWords"],
       "deck":s["deck"],"sourceCount":len(rec["sources"]),
       "sha256":hashlib.sha256(raw.encode("utf-8")).hexdigest(),"status":"review candidate, NOT accepted Reader checkpoint"}

def validate(specs,expected):
    errors=[];rows=[]
    for s in specs:
       n=s["n"];a=ROOT/f"{n:03d}-{s['slug']}.html";data=a.read_text(encoding="utf-8")
       soup=BeautifulSoup(data,"lxml")
       v=soup.select_one("#opening > aside.play-vignette")
       if not v or v.get("data-featured-card")!=s["card"]:errors.append(f"{n} story missing/mismatched");continue
       if s["deck"] not in {x.get_text(" ",strip=True) for x in soup.select("details.deck summary strong")}:errors.append(f"{n} named deck missing")
       text=v.select_one("p").get_text(" ",strip=True) if v.select_one("p") else ""
       count=len(re.findall(r"\b[\w’'-]+\b",text))
       if not 70<=count<=170:errors.append(f"{n} story words {count} outside 70-170")
       if len({x.get("data-card") for x in v.select(".card-name[data-card]")})<3:errors.append(f"{n} fewer than 3 named cards")
       if "opponent" not in text.lower() or not re.search(r"\b(?:I|my|me)\b",text,re.I):errors.append(f"{n} not specific first-person")
       if not re.search(r"\b(?:turn|upkeep|combat|attack|resolve|cast|draw step|main phase)\b",text,re.I):errors.append(f"{n} no time anchor")
       if not v.select_one("script.vignette-review-data"):errors.append(f"{n} missing review")
       pill=soup.select_one(".byline .pill");words=editorial_word_count(soup);mins=reading_time_minutes(words)
       if not pill or pill.get("data-reading-word-count")!=str(words) or pill.get_text(" ",strip=True)!=f"Approximately {mins} minute read":errors.append(f"{n} reading time out of sync")
       dos=read(ROOT/f"research-dossiers/numbered-wave-02/{n:03d}-{s['slug']}.json")
       issues=list(Draft202012Validator(SCHEMA,format_checker=FormatChecker()).iter_errors(dos))
       if issues:errors.append(f"{n} invalid research dossier "+issues[0].message)
       story=read(BATCH/f"{n:03d}-story-candidate.json")
       if story["story"]!=text or story["storyWords"]!=count:errors.append(f"{n} story record out of sync")
       for c in dos.get("claims",[]):
         if not set(c.get("sourceIds",[])).issubset({x["sourceId"] for x in dos["sources"]}):errors.append(f"{n} unbound source")
       row={"entry":n,"card":s["card"],"editorialWords":words,"readMinutes":mins,"storyWords":count,"deck":s["deck"],
           "sourceCount":len(story["sources"]),"sha256":hashlib.sha256(data.encode("utf-8")).hexdigest(),"status":"review candidate, NOT accepted Reader checkpoint"}
       rows.append(row)
    if len(rows)!=10:errors.append("Expected exactly ten candidate records")
    if rows!=expected:errors.append("Saved metrics out of sync with ten current articles")
    accepted=read(ROOT/"CURRENT-STATE.json")
    if accepted.get("readerV31LatestCheckpoint",{}).get("nextArticle")!=61:errors.append("Accepted Reader checkpoint unexpectedly moved")
    public=read(ROOT/"site-progress.json")
    if public.get("progress",{}).get("completed")!=60:errors.append("Reader accepted progress prematurely increased")
    if errors:
      print("FAIL Reader V3.1 063-072 candidates: "+str(len(errors)))
      for x in errors: print(" - "+x)
      return 1
    print(f"PASS ten Reader V3.1 candidate stories/dossiers, {sum(x['editorialWords'] for x in rows)} editorial words; accepted Reader stays 60")
    return 0

def main():
    p=argparse.ArgumentParser();p.add_argument("--apply",action="store_true");args=p.parse_args()
    plan=read(PLAN);specs=plan["articles"]
    if [x["n"] for x in specs]!=list(range(63,73)):raise ValueError("Expected exact 063-072 editorial order")
    if args.apply:
       rows=[candidate(s) for s in specs]
       write(METRICS,{"scope":"063-072","date":"2026-10-27","status":"ten individual candidate drafts; NOT approved 061-070 or 071-080 checkpoint",
          "acceptedReader":60,"weightedRoadmapPoints":51,"articles":rows})
    expected=read(METRICS)["articles"]
    raise SystemExit(validate(specs,expected))

if __name__=="__main__":
    main()
