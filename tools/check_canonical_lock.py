#!/usr/bin/env python3
"""Fail when the frozen Eternal Dragon authority changes unintentionally."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    lock = json.loads((root / "canonical" / "canonical-lock.json").read_text(encoding="utf-8"))
    published = root / lock["canonical_article"]
    snapshot = root / lock["snapshot"]
    expected = lock["sha256"]
    published_hash = digest(published)
    snapshot_hash = digest(snapshot)
    failures = []
    if published_hash != expected:
        failures.append(f"{published.name}: expected {expected}, found {published_hash}")
    if snapshot_hash != expected:
        failures.append(f"{snapshot}: expected {expected}, found {snapshot_hash}")
    if published.read_bytes() != snapshot.read_bytes():
        failures.append("Published canonical article and frozen snapshot are not byte-identical.")
    if failures:
        print("CANONICAL LOCK FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"Canonical lock verified: {published.name} ({expected})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
