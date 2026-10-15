#!/usr/bin/env python3
"""Fail only when a page gains mechanical issue signatures not in the baseline.

Removed issues are allowed. This lets repairs improve the archive without requiring
an immediate baseline rewrite, while blocking newly introduced drift.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def signatures(report: dict) -> dict[str, set[str]]:
    output: dict[str, set[str]] = {}
    for result in report.get("results", []):
        output[result["file"]] = {
            f"{issue['severity']}:{issue['code']}"
            for issue in result.get("issues", [])
        }
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline", type=Path)
    parser.add_argument("current", type=Path)
    args = parser.parse_args()
    baseline = signatures(json.loads(args.baseline.read_text(encoding="utf-8")))
    current = signatures(json.loads(args.current.read_text(encoding="utf-8")))
    regressions = []
    for filename, current_issues in current.items():
        new = current_issues - baseline.get(filename, set())
        if new:
            regressions.append((filename, sorted(new)))
    if regressions:
        print("AUDIT REGRESSION DETECTED")
        for filename, new in regressions:
            print(f"- {filename}: {', '.join(new)}")
        return 1
    print("No new mechanical issue signatures were introduced.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
