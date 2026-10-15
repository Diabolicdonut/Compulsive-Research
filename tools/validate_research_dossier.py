#!/usr/bin/env python3
"""Validate an Editorial V2 research dossier before article generation."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT=Path(__file__).resolve().parents[1]
SCHEMA=ROOT/'templates/research-dossier-v2.schema.json'

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('dossier',type=Path)
    ap.add_argument('--schema',type=Path,default=SCHEMA)
    args=ap.parse_args()
    data=json.loads(args.dossier.read_text(encoding='utf-8'))
    schema=json.loads(args.schema.read_text(encoding='utf-8'))
    errors=sorted(Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(data),key=lambda e:list(e.path))
    payload={'dossier':str(args.dossier),'schema':str(args.schema),'status':'PASS' if not errors else 'FAIL','errors':[{'path':'/'.join(map(str,e.path)) or '$','message':e.message} for e in errors]}
    print(json.dumps(payload,indent=2,ensure_ascii=False))
    return 1 if errors else 0
if __name__=='__main__': raise SystemExit(main())
