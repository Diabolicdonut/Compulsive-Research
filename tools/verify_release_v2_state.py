#!/usr/bin/env python3
"""Verify that passing Editorial V2 reports match the current corpus exactly."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from release_fingerprint import corpus_sha256

ROOT=Path(__file__).resolve().parents[1]
def main():
 state_path=ROOT/'audit/release-v2-validation-state.json'
 failures=[]
 if not state_path.exists():
  print('Release V2 validation state is missing. Run the V2 validators and stamp_release_v2_state.py.')
  return 1
 state=json.loads(state_path.read_text(encoding='utf-8'))
 current,count=corpus_sha256(ROOT)
 if state.get('status')!='PASS': failures.append('Stamped state is not PASS.')
 if state.get('corpusSha256')!=current: failures.append(f"Corpus fingerprint changed: {state.get('corpusSha256')} != {current}")
 if state.get('fingerprintedFiles')!=count: failures.append(f"Fingerprint file count changed: {state.get('fingerprintedFiles')} != {count}")
 for name,row in state.get('reports',{}).items():
  path=ROOT/row['path']
  if not path.exists(): failures.append(f'{name}: report missing'); continue
  found=hashlib.sha256(path.read_bytes()).hexdigest()
  if found!=row.get('sha256'): failures.append(f'{name}: report hash changed')
 payload={'corpusSha256':current,'fingerprintedFiles':count,'reportsVerified':len(state.get('reports',{})),'status':'FAIL' if failures else 'PASS','failures':failures}
 print(json.dumps(payload,indent=2))
 return 1 if failures else 0
if __name__=='__main__': raise SystemExit(main())
