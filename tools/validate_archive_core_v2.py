#!/usr/bin/env python3
"""Fast structural release validator for the Editorial V2 archive.

This replaces the legacy all-purpose validator in the default full suite. It checks
high-value release invariants without reparsing each page multiple times or requiring
obsolete external JavaScript shims. Detailed component validators remain separate.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

from lxml import html

CLASS = "contains(concat(' ', normalize-space(@class), ' '), ' {name} ')"
RETURN_TEXT = "← Back to Compulsive Research"


def active_pages(root: Path) -> tuple[list[Path], list[Path]]:
    numbered = sorted(set(
        list(root.glob("[0-9][0-9][0-9]-*.html"))
        + list(root.glob("[0-9][0-9][0-9][0-9]-*.html"))
    ))
    honorable = sorted(root.glob("honorable-*.html"))
    return numbered, honorable


def first(nodes):
    return nodes[0] if nodes else None


def text(node) -> str:
    return " ".join(node.text_content().split()) if node is not None else ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    root = args.root.resolve()
    output = (args.output_dir or root / "audit/archive-core-v2").resolve()
    output.mkdir(parents=True, exist_ok=True)

    manifest = json.loads((root / "archive-manifest.json").read_text(encoding="utf-8"))
    numbered, honorable = active_pages(root)
    results = []

    manifest_numbered = {item.get("file") for item in manifest.get("entries", [])}
    manifest_honorable = {item.get("file") for item in manifest.get("honorable_mentions", [])}
    package_issues = []
    if len(numbered) != 1000:
        package_issues.append({"severity": "FAIL", "code": "NUMBERED_COUNT", "message": f"Expected 1000; found {len(numbered)}."})
    if len(honorable) != 505:
        package_issues.append({"severity": "FAIL", "code": "HONORABLE_COUNT", "message": f"Expected 505; found {len(honorable)}."})
    if {p.name for p in numbered} != manifest_numbered:
        package_issues.append({"severity": "FAIL", "code": "NUMBERED_MANIFEST_PARITY", "message": "Numbered files differ from archive-manifest.json."})
    if {p.name for p in honorable} != manifest_honorable:
        package_issues.append({"severity": "FAIL", "code": "HONORABLE_MANIFEST_PARITY", "message": "Honorable Mention files differ from archive-manifest.json."})

    for path in numbered + honorable:
        issues = []
        try:
            tree = html.fromstring(path.read_bytes())
        except Exception as exc:
            results.append({"file": path.name, "status": "FAIL", "issues": [{"severity": "FAIL", "code": "HTML_PARSE", "message": str(exc)}]})
            continue

        body = first(tree.xpath("//body"))
        subject = body.get("data-article-card", "") if body is not None else ""
        if not subject:
            issues.append({"severity": "FAIL", "code": "MISSING_ARTICLE_CARD", "message": "body[data-article-card] is missing."})
        if body is None or body.get("data-editorial-contract") != "v2":
            issues.append({"severity": "FAIL", "code": "MISSING_EDITORIAL_CONTRACT", "message": "Editorial V2 body metadata is missing."})
        if body is None or not body.get("data-editorial-status") or not body.get("data-research-status"):
            issues.append({"severity": "FAIL", "code": "MISSING_EDITORIAL_STATUS", "message": "Editorial/research status metadata is incomplete."})

        h1 = tree.xpath("//h1")
        if len(h1) != 1:
            issues.append({"severity": "FAIL", "code": "H1_COUNT", "message": f"Expected one h1; found {len(h1)}."})
        hero = first(tree.xpath(f"//header[{CLASS.format(name='hero')}]"))
        if hero is None:
            issues.append({"severity": "FAIL", "code": "MISSING_HERO", "message": "header.hero is missing."})
        else:
            for class_name in ["hero-grid", "hero-inner", "archive-link", "eyebrow", "deckline", "byline"]:
                if not hero.xpath(f".//*[{CLASS.format(name=class_name)}]"):
                    issues.append({"severity": "FAIL", "code": "HERO_COMPONENT", "message": f"Hero lacks .{class_name}."})
            archive_link = first(hero.xpath(f".//*[{CLASS.format(name='archive-link')}]") )
            if archive_link is not None and text(archive_link) != RETURN_TEXT:
                issues.append({"severity": "FAIL", "code": "RETURN_LABEL", "message": text(archive_link)})

        article = first(tree.xpath(f"//article[{CLASS.format(name='article')}]"))
        toc = first(tree.xpath(f"//nav[{CLASS.format(name='toc')}]"))
        if article is None:
            issues.append({"severity": "FAIL", "code": "MISSING_ARTICLE", "message": "article.article is missing."})
            section_ids = set()
        else:
            sections = article.xpath(".//section[@id]")
            section_ids = {section.get("id") for section in sections}
            if len(sections) < 6:
                issues.append({"severity": "FAIL", "code": "SECTION_COUNT_LOW", "message": f"Only {len(sections)} sections."})
            if "opening" not in section_ids:
                issues.append({"severity": "FAIL", "code": "MISSING_OPENING", "message": "section#opening is missing."})
        if toc is None:
            issues.append({"severity": "FAIL", "code": "MISSING_TOC", "message": "nav.toc is missing."})
        else:
            refs = [href[1:] for href in toc.xpath(".//a[starts-with(@href, '#')]/@href")]
            missing = sorted(set(refs) - section_ids)
            if missing:
                issues.append({"severity": "FAIL", "code": "TOC_TARGET", "message": ", ".join(missing[:10])})

        spotlights = tree.xpath(f"//*[{CLASS.format(name='artwork-spotlight')}]")
        if len(spotlights) != 1:
            issues.append({"severity": "FAIL", "code": "ARTWORK_SPOTLIGHT_COUNT", "message": str(len(spotlights))})
        else:
            spot = spotlights[0]
            for attr in ["data-artwork-card", "data-artwork-set", "data-artwork-set-name", "data-artwork-artist"]:
                if not spot.get(attr):
                    issues.append({"severity": "FAIL", "code": "ARTWORK_METADATA", "message": attr})
            if not spot.xpath(f".//*[{CLASS.format(name='art-break-media')} and @src]"):
                issues.append({"severity": "FAIL", "code": "ARTWORK_IMAGE", "message": "Missing spotlight image."})

        if not tree.xpath(f"//*[{CLASS.format(name='design-echo-section')}]"):
            issues.append({"severity": "FAIL", "code": "MISSING_DESIGN_ECHO", "message": "No Design Echo section."})
        if not tree.xpath(f"//*[{CLASS.format(name='canonical-printing-gallery')}]"):
            issues.append({"severity": "FAIL", "code": "MISSING_PRINTING_GALLERY", "message": "No canonical printing gallery."})
        sources_headings = [node for node in tree.xpath("//section[@id='printings']//h3") if text(node) == "Sources"]
        if not sources_headings:
            issues.append({"severity": "FAIL", "code": "MISSING_SOURCES_HEADING", "message": "Sources heading is missing."})

        deck_section = first(tree.xpath("//section[@id='decklists']"))
        if deck_section is None:
            issues.append({"severity": "FAIL", "code": "MISSING_DECK_SECTION", "message": "section#decklists is missing."})
        else:
            production_decks = deck_section.xpath(
                ".//details[contains(concat(' ', normalize-space(@class), ' '), ' deck ') and not(@data-deck-kind='official-mtg-product')]"
            )
            notices = deck_section.xpath(f".//*[{CLASS.format(name='deck-research-status')}]")
            if not production_decks and not notices:
                issues.append({"severity": "FAIL", "code": "DECK_EMPTY_WITHOUT_NOTICE", "message": "No documentary deck and no research notice."})

        for script_id in ["cr-design-echo-runtime", "cr-printing-gallery-runtime"]:
            if not tree.xpath(f"//script[@id='{script_id}']"):
                issues.append({"severity": "FAIL", "code": "MISSING_INLINE_RUNTIME", "message": script_id})

        local_hrefs = tree.xpath("//a[@href]/@href")
        for href in local_hrefs:
            if not href or href.startswith(("#", "http://", "https://", "mailto:", "javascript:")):
                continue
            file_part = href.split("?", 1)[0].split("#", 1)[0]
            if file_part and not (root / file_part).exists():
                issues.append({"severity": "FAIL", "code": "BROKEN_LOCAL_LINK", "message": href})
                break

        status = "FAIL" if any(issue["severity"] == "FAIL" for issue in issues) else "PASS"
        results.append({"file": path.name, "cardName": subject, "status": status, "issues": issues})

    all_issues = package_issues + [issue for result in results for issue in result["issues"]]
    codes = Counter(issue["code"] for issue in all_issues)
    status_counts = Counter(result["status"] for result in results)
    payload = {
        "numberedArticles": len(numbered),
        "honorableArticles": len(honorable),
        "articles": len(results),
        "statusCounts": dict(status_counts),
        "packageIssues": package_issues,
        "issueCounts": dict(codes),
        "status": "FAIL" if package_issues or status_counts.get("FAIL") else "PASS",
        "results": results,
    }
    (output / "archive-core-v2.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [
        "# Archive core V2 validation", "",
        f"- Numbered articles: **{len(numbered)}**",
        f"- Active Honorable Mentions: **{len(honorable)}**",
        f"- Pass: **{status_counts.get('PASS', 0)}**",
        f"- Fail: **{status_counts.get('FAIL', 0)}**",
        "", "## Findings",
    ] + [f"- `{code}`: {count}" for code, count in codes.most_common()]
    (output / "archive-core-v2.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ["numberedArticles", "honorableArticles", "articles", "statusCounts", "issueCounts", "status"]}, indent=2))
    return 1 if payload["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
