#!/usr/bin/env python3
"""Validate numbered article identity against the committed canonical snapshot."""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from lxml import html

SUSPICIOUS = re.compile(
    r"(pro tour promos?|grand prix promos?|judge gift cards?|secret lair|store championships?|"
    r"oversized|arena league|dci promos?|magic player rewards|media and collaboration promos?|"
    r"prerelease promos?|release event|world championship promos?|junior super series)",
    re.I,
)
CLASS = "contains(concat(' ', normalize-space(@class), ' '), ' {name} ')"


def norm_name(value: Any) -> str:
    return re.sub(r"[’‘`´]", "'", str(value or "")).strip()


def first(nodes):
    return nodes[0] if nodes else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    root = args.root.resolve()
    output = (args.output_dir or root / "audit/canonical-identity-v2").resolve()
    output.mkdir(parents=True, exist_ok=True)

    snapshot = json.loads((root / "data/remaining-entry-card-data.json").read_text(encoding="utf-8"))["cards"]
    by_entry = {int(card["entry"]): card for card in snapshot}
    overrides = json.loads((root / "data/canonical-first-printing-overrides.json").read_text(encoding="utf-8"))["cards"]

    files = sorted(set(
        list(root.glob("[0-9][0-9][0-9]-*.html"))
        + list(root.glob("[0-9][0-9][0-9][0-9]-*.html"))
    ))
    results = []
    for path in files:
        match = re.match(r"^(\d{3,4})-", path.name)
        if not match:
            continue
        card = by_entry.get(int(match.group(1)))
        if not card:
            continue
        issues = []
        try:
            tree = html.fromstring(path.read_bytes())
        except Exception as exc:
            results.append({
                "file": path.name, "cardName": card.get("articleName", ""),
                "setCode": card.get("setCode", ""), "setName": card.get("setName", ""),
                "issues": [{"severity": "FAIL", "code": "HTML_PARSE_ERROR", "message": str(exc)}],
                "status": "FAIL",
            })
            continue

        body = first(tree.xpath("//body"))
        name = body.get("data-article-card") if body is not None else ""
        if norm_name(name) != norm_name(card.get("articleName")):
            issues.append({"severity": "FAIL", "code": "ARTICLE_CARD_MISMATCH", "message": f"{name} != {card.get('articleName')}"})

        hero = first(tree.xpath(f"//header[{CLASS.format(name='hero')}]"))
        if hero is not None and hero.get("data-hero-card") and norm_name(hero.get("data-hero-card")) != norm_name(name):
            issues.append({"severity": "FAIL", "code": "HERO_CARD_MISMATCH", "message": hero.get("data-hero-card")})

        spot = first(tree.xpath(f"//*[{CLASS.format(name='artwork-spotlight')}]"))
        if spot is None:
            issues.append({"severity": "FAIL", "code": "MISSING_ARTWORK_SPOTLIGHT", "message": "No canonical spotlight."})
        else:
            if norm_name(spot.get("data-artwork-card")) != norm_name(name):
                issues.append({"severity": "FAIL", "code": "SPOTLIGHT_CARD_MISMATCH", "message": spot.get("data-artwork-card")})
            if spot.get("data-artwork-set") and spot.get("data-artwork-set") != card.get("setCode"):
                issues.append({"severity": "FAIL", "code": "SPOTLIGHT_SET_MISMATCH", "message": f"{spot.get('data-artwork-set')} != {card.get('setCode')}"})
            if spot.get("data-artwork-artist") and spot.get("data-artwork-artist") != card.get("artist"):
                issues.append({"severity": "FAIL", "code": "SPOTLIGHT_ARTIST_MISMATCH", "message": f"{spot.get('data-artwork-artist')} != {card.get('artist')}"})

        grid = first(tree.xpath(f"//*[{CLASS.format(name='canonical-printing-gallery')}]"))
        if grid is None:
            issues.append({"severity": "FAIL", "code": "MISSING_PRINTING_GALLERY", "message": "No gallery."})
        elif grid.get("data-original-set") and grid.get("data-original-set") != card.get("setCode"):
            issues.append({"severity": "FAIL", "code": "GALLERY_ORIGINAL_SET_MISMATCH", "message": f"{grid.get('data-original-set')} != {card.get('setCode')}"})

        lead = first(tree.xpath(f"//*[{CLASS.format(name='card-lead')} and @data-scryfall-id]"))
        if lead is not None and lead.get("data-scryfall-id") != card.get("scryfallId"):
            issues.append({"severity": "FAIL", "code": "LEAD_PRINTING_MISMATCH", "message": f"{lead.get('data-scryfall-id')} != {card.get('scryfallId')}"})

        if SUSPICIOUS.search(card.get("setName", "")) and card.get("articleName") not in overrides:
            issues.append({"severity": "WARN", "code": "SUSPICIOUS_DEBUT_CONTAINER", "message": card.get("setName")})

        status = "FAIL" if any(issue["severity"] == "FAIL" for issue in issues) else ("WARN" if issues else "PASS")
        results.append({
            "file": path.name,
            "cardName": name,
            "setCode": card.get("setCode"),
            "setName": card.get("setName"),
            "issues": issues,
            "status": status,
        })

    counts = Counter(result["status"] for result in results)
    codes = Counter(issue["code"] for result in results for issue in result["issues"])
    payload = {
        "articles": len(results),
        "statusCounts": dict(counts),
        "issueCounts": dict(codes),
        "status": "FAIL" if counts.get("FAIL") else "PASS",
        "results": results,
    }
    (output / "canonical-identity.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [
        "# Canonical identity V2 validation", "",
        f"- Articles: **{len(results)}**",
        f"- Pass: **{counts.get('PASS', 0)}**",
        f"- Warn: **{counts.get('WARN', 0)}**",
        f"- Fail: **{counts.get('FAIL', 0)}**",
        "", "## Findings",
    ] + [f"- `{code}`: {count}" for code, count in codes.most_common()]
    (output / "canonical-identity.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "articles": len(results), "statusCounts": dict(counts),
        "issueCounts": dict(codes), "status": payload["status"],
    }, indent=2))
    return 1 if counts.get("FAIL") else 0


if __name__ == "__main__":
    raise SystemExit(main())
