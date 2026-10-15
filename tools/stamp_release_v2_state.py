#!/usr/bin/env python3
"""Bind passing Editorial V2 reports to the exact production corpus."""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from release_fingerprint import corpus_sha256

ROOT=Path(__file__).resolve().parents[1]
REPORTS={
 'canonicalIdentity':'audit/canonical-identity-v2/canonical-identity.json',
 'deckSemantics':'audit/deck-semantics/deck-semantics.json',
 'editorialQuality':'audit/editorial-v2/editorial-quality.json',
 'archiveCore':'audit/archive-core-v2/archive-core-v2.json',
 'deckArchives':'audit/deck-archives/deck-validation.json',
 'officialMtgDecks':'audit/official-mtg-decks/official-mtg-deck-validation.json',
 'cardImageLinks':'audit/card-image-links/card-image-link-validation.json',
}

def report_pass(name,data):
 if name in {'canonicalIdentity','deckSemantics','editorialQuality','archiveCore'}:
  return data.get('status')=='PASS'
 if name=='deckArchives':
  return not data.get('issue_code_counts') and not data.get('status_counts',{}).get('FAIL')
 return not data.get('issueCodeCounts') and not data.get('statusCounts',{}).get('FAIL')

def main():
 rows={}; failures=[]
 for name,rel in REPORTS.items():
  path=ROOT/rel
  if not path.exists(): failures.append(f'{name}: missing {rel}'); continue
  data=json.loads(path.read_text(encoding='utf-8'))
  if not report_pass(name,data): failures.append(f'{name}: report is not passing')
  rows[name]={'path':rel,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
 corpus,count=corpus_sha256(ROOT)
 payload={'schemaVersion':'2.0','generatedAt':datetime.now(timezone.utc).isoformat(),'corpusSha256':corpus,'fingerprintedFiles':count,'reports':rows,'status':'FAIL' if failures else 'PASS','failures':failures}
 out=ROOT/'audit/release-v2-validation-state.json'; out.write_text(json.dumps(payload,indent=2)+'\n')
 print(json.dumps({k:payload[k] for k in ['corpusSha256','fingerprintedFiles','status','failures']},indent=2))
 return 1 if failures else 0
if __name__=='__main__': raise SystemExit(main())
