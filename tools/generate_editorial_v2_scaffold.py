#!/usr/bin/env python3
"""Create a non-publishable Editorial V2 research dossier scaffold.

This tool copies canonical identity from the committed snapshot but deliberately
leaves research prose as explicit TODO fields. It never invents history or decks.
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('card'); ap.add_argument('--root',type=Path,default=ROOT); ap.add_argument('--output',type=Path,default=None); ap.add_argument('--article-class',default='tournament-pillar')
    args=ap.parse_args(); root=args.root.resolve(); data=json.loads((root/'data/remaining-entry-card-data.json').read_text())['cards']
    card=next((c for c in data if c['articleName'].casefold()==args.card.casefold()),None)
    if not card:raise SystemExit(f'Card not found in committed snapshot: {args.card}')
    ident={'oracleId':card['oracleId'],'oracleName':card['canonicalName'],'firstPrintingSetCode':card['setCode'],'firstPrintingSetName':card['setName'],'releaseDate':card['releaseDate'],'scryfallId':card['scryfallId'],'illustrationId':card.get('illustrationId',''),'originalArtist':card['artist'],'originalPrintedText':'TODO: transcribe from verified original printing','currentOracleText':card.get('oracleText',''),'promotionalDebut':bool(re.search(r'promo|book',card['setName'],re.I)),'identityNotes':'Verify this committed identity against the canonical identity contract before research approval.'}
    todo='TODO: research and cite card-specific evidence.'
    dossier={'schemaVersion':'2.0','cardName':card['articleName'],'articleClass':args.article_class,'secondaryClasses':[],'thesis':'TODO: write a card-specific thesis of at least eighty characters explaining why this card belongs in the archive.','canonicalIdentity':ident,'originalContext':{'setEnvironment':todo,'designPurpose':todo,'initialReception':todo,'sourceIds':[]},'loreContext':{'scope':'none-documented','summary':todo,'depictedMoment':'','relatedStoryCards':[],'sourceIds':[]},'competitiveTimeline':[],'playbook':{'role':todo,'deckRequirements':todo,'copyCount':todo,'mulligans':todo,'sequencing':todo,'sideboarding':todo,'commonMistakes':todo},'counterplay':{'directAnswers':todo,'engineDisruption':todo,'timingWindows':todo,'racing':todo,'sideboarding':todo},'deckEvidence':[],'claims':[{'claimId':'identity-debut','summary':f"{card['articleName']} first appeared in {card['setName']} on {card['releaseDate']}.",'sourceIds':[],'confidence':'medium','notes':'Bind a primary or authoritative database source before approval.'}],'sources':[],'researchStatus':'scaffold','review':{'historicalReviewDate':'2026-08-02','currentInformationAsOf':'2026-08-02','editorialReviewer':'Unassigned','openQuestions':['Verify canonical first printing.','Identify primary sources.','Determine article class and documentary deck evidence.']}}
    out=args.output or root/'research-dossiers'/f"{card['entry']:03d}-{re.sub(r'[^a-z0-9]+','-',card['articleName'].lower()).strip('-')}.json"; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(dossier,indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); print(out); return 0
if __name__=='__main__':raise SystemExit(main())
