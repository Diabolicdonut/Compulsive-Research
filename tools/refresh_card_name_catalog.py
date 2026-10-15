#!/usr/bin/env python3
"""Refresh or verify the checked-in Oracle card-name catalog.

Normal CI uses ``--check`` and never depends on network access. Maintainers may
run the script without ``--check`` to replace the local snapshot with Scryfall's
complete nontoken English card-name catalog.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "canonical" / "card-name-catalog.json"
SUPPLEMENT_PATH = ROOT / "canonical" / "card-link-supplement.json"
ENDPOINT = "https://api.scryfall.com/catalog/card-names"


def clean_names(values: object) -> list[str]:
    if not isinstance(values, list):
        raise ValueError("catalog data must be an array")
    output: list[str] = []
    seen: set[str] = set()
    for item in values:
        if not isinstance(item, str) or not item.strip():
            continue
        name = " ".join(item.strip().split())
        key = name.replace("’", "'").casefold()
        if key not in seen:
            seen.add(key)
            output.append(name)
    if not output:
        raise ValueError("catalog contains no usable card names")
    return output


def supplement_names() -> list[str]:
    if not SUPPLEMENT_PATH.exists():
        return []
    data = json.loads(SUPPLEMENT_PATH.read_text(encoding="utf-8"))
    return clean_names(data.get("names", []))


def load_input(path: Path | None) -> dict:
    if path:
        return json.loads(path.read_text(encoding="utf-8"))
    request = urllib.request.Request(
        ENDPOINT,
        headers={
            "User-Agent": "CompulsiveResearchArchive/1.0 (+https://github.com/diabolicdonut)",
            "Accept": "application/json;q=0.9,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def validate_payload(payload: dict) -> list[str]:
    if not isinstance(payload, dict):
        raise ValueError("catalog response must be an object")
    names = clean_names(payload.get("data"))
    reported = payload.get("total_values")
    if isinstance(reported, int) and reported != len(names):
        raise ValueError(f"reported total_values={reported} but parsed {len(names)} names")
    # A complete Oracle catalog is far larger than the project-local snapshot.
    if len(names) < 20_000:
        raise ValueError(f"refusing incomplete authoritative catalog with only {len(names)} names")
    return names


def check_current() -> int:
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    names = clean_names(data.get("names", []))
    problems: list[str] = []
    if data.get("count") != len(names):
        problems.append(f"count field {data.get('count')} does not match {len(names)} names")
    if len({name.replace('’', "'").casefold() for name in names}) != len(names):
        problems.append("catalog contains normalized duplicate names")
    required = {"Persist", "Plunge into Darkness"}
    missing = sorted(required - set(names) - set(supplement_names()))
    if missing:
        problems.append("required regression fixtures missing: " + "; ".join(missing))
    if problems:
        for problem in problems:
            print("FAIL:", problem)
        return 1
    print(json.dumps({
        "status": "PASS",
        "catalog_mode": data.get("catalog_mode", "unknown"),
        "catalog_names": len(names),
        "supplement_names": len(supplement_names()),
    }, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate the committed snapshot without network access")
    parser.add_argument("--input", type=Path, help="read a previously downloaded Scryfall catalog response")
    args = parser.parse_args()
    if args.check:
        return check_current()

    payload = load_input(args.input)
    names = validate_payload(payload)
    # The supplement may contain newly previewed names between catalog refreshes.
    merged = clean_names(names + supplement_names())
    result = {
        "schema_version": 3,
        "purpose": "Authoritative Oracle card-name catalog for deterministic Compulsive Research linking.",
        "source": ENDPOINT if not args.input else str(args.input),
        "catalog_mode": "authoritative_scryfall_plus_editorial_overrides",
        "refresh_endpoint": ENDPOINT,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(merged),
        "names": sorted(merged, key=lambda value: (-len(value), value.casefold())),
    }
    CATALOG_PATH.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {CATALOG_PATH} with {len(merged)} names")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
