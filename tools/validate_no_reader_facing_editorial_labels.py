#!/usr/bin/env python3
"""Reject internal editorial-workflow labels that are visible to article readers."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from lxml import html

PATTERNS = {
    "EDITORIAL_V2_VISIBLE": re.compile(r"\beditorial\s+v2\b", re.I),
    "REVIEWED_UNDER_EDITORIAL": re.compile(r"\breviewed\s+under\s+editorial\b", re.I),
    "REVIEWED_WAVE_VISIBLE": re.compile(r"\breviewed\s+wave\s+\d+\b", re.I),
    "EDITORIAL_STATUS_VISIBLE": re.compile(r"\beditorial\s+status\s*:\s*reviewed\b", re.I),
    "RESEARCH_STATUS_VISIBLE": re.compile(r"\bresearch\s+status\s*:\s*(?:complete|reviewed)\b", re.I),
}


def active_pages(root: Path) -> list[Path]:
    numbered = list(root.glob("[0-9][0-9][0-9]-*.html")) + list(root.glob("[0-9][0-9][0-9][0-9]-*.html"))
    honorable = list(root.glob("honorable-*.html"))
    return sorted(set(numbered + honorable))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    root = args.root.resolve()
    findings: list[dict[str, str]] = []
    parse_failures: list[dict[str, str]] = []

    for path in active_pages(root):
        try:
            tree = html.fromstring(path.read_bytes())
        except Exception as exc:
            parse_failures.append({"file": path.name, "error": str(exc)})
            continue
        # Metadata, scripts, styles, comments, and attributes are intentionally excluded.
        for text_node in tree.xpath("//text()[not(ancestor::script) and not(ancestor::style)]"):
            text = " ".join(str(text_node).split())
            if not text:
                continue
            for code, pattern in PATTERNS.items():
                if pattern.search(text):
                    findings.append({
                        "file": path.name,
                        "code": code,
                        "tag": getattr(text_node.getparent(), "tag", ""),
                        "text": text[:500],
                    })

    payload = {
        "schemaVersion": "1.0",
        "root": str(root),
        "articles": len(active_pages(root)),
        "parseFailures": parse_failures,
        "findings": findings,
        "status": "PASS" if not findings and not parse_failures else "FAIL",
    }
    output = (args.output or root / "audit" / "reader-facing-editorial-labels.json").resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "articles": payload["articles"],
        "findings": len(findings),
        "parseFailures": len(parse_failures),
        "status": payload["status"],
        "output": str(output),
    }, indent=2))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
