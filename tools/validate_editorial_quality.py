#!/usr/bin/env python3
"""Audit specificity, repetition, evidence signals, and Editorial V2 readiness."""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

from lxml import html

GENERIC_PATTERNS = {
    "decision-machine": r"decision machine rather than a reputation",
    "exchange-worth": r"what the exchange is actually worth",
    "famous-turn": r"the turn before the famous turn",
    "preserve-question": r"preserve the question, not only the result",
    "metadata-dossier": r"metadata-grounded dossier",
    "generic-costs": r"costs are paid before effects happen",
    "generic-targets": r"targets, if any, are chosen when",
    "resource-list": r"mana development, combat, hidden information",
}
EXCLUDE_SECTIONS = {"decklists", "printings"}
CLASS = "contains(concat(' ', normalize-space(@class), ' '), ' {name} ')"


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def active_pages(root: Path) -> list[Path]:
    numbered = list(root.glob("[0-9][0-9][0-9]-*.html")) + list(root.glob("[0-9][0-9][0-9][0-9]-*.html"))
    honorable = list(root.glob("honorable-*.html"))
    return sorted(set(numbered + honorable))


def paragraph_texts(tree) -> list[str]:
    article_nodes = tree.xpath(f"//article[{CLASS.format(name='article')}]")
    article = article_nodes[0] if article_nodes else tree
    output = []
    for paragraph in article.xpath(".//p"):
        excluded_section = paragraph.xpath("ancestor::section[@id='decklists' or @id='printings']")
        if excluded_section:
            continue
        if paragraph.xpath("ancestor::details | ancestor::figure"):
            continue
        text = norm(paragraph.text_content())
        if len(text) >= 90:
            output.append(text)
    return output


def source_urls(tree) -> list[str]:
    return tree.xpath(
        f"//section[@id='printings']//*[{CLASS.format(name='sources')}]//a[@href]/@href"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--strict-reviewed", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    output = (args.output_dir or root / "audit/editorial-v2").resolve()
    output.mkdir(parents=True, exist_ok=True)

    docs = {}
    frequency = Counter()
    for path in active_pages(root):
        raw_bytes = path.read_bytes()
        raw = raw_bytes.decode("utf-8", errors="replace")
        try:
            tree = html.fromstring(raw_bytes)
        except Exception:
            continue
        paragraphs = paragraph_texts(tree)
        docs[path.name] = (raw, tree, paragraphs)
        frequency.update(paragraphs)

    results = []
    hard_failures = 0
    for filename, (raw, tree, paragraphs) in docs.items():
        body_nodes = tree.xpath("//body")
        body = body_nodes[0] if body_nodes else None
        editorial_status = (body.get("data-editorial-status") if body is not None else "") or "unclassified"
        subject = body.get("data-article-card", "") if body is not None else ""
        generic = [key for key, pattern in GENERIC_PATTERNS.items() if re.search(pattern, raw, re.I)]
        duplicate_instances = sum(1 for paragraph in paragraphs if frequency[paragraph] > 1)
        high_duplication = sum(1 for paragraph in paragraphs if frequency[paragraph] >= 10)
        max_frequency = max((frequency[p] for p in paragraphs), default=0)
        urls = source_urls(tree)
        primary_sources = sum(
            1 for url in urls
            if re.search(r"(?:magic\.wizards\.com|wizards\.com|media\.wizards\.com|mtg\.com)", url, re.I)
        )
        studies = len(tree.xpath("//details[@data-deck-kind='editorial-study']"))
        issues = []
        if studies:
            issues.append({"severity": "FAIL", "code": "EDITORIAL_STUDY_IN_PRODUCTION", "message": f"{studies} synthetic study deck(s) remain."})
        if body is None or body.get("data-editorial-contract") != "v2":
            issues.append({"severity": "WARN", "code": "MISSING_EDITORIAL_STATUS", "message": "No Editorial V2 status metadata."})
        if generic:
            issues.append({"severity": "WARN", "code": "GENERIC_DOSSIER_LANGUAGE", "message": ", ".join(generic)})
        ratio = duplicate_instances / len(paragraphs) if paragraphs else 0
        if ratio >= 0.35:
            issues.append({"severity": "WARN", "code": "HIGH_EXACT_DUPLICATION", "message": f"{ratio:.1%} of substantive paragraphs are duplicated elsewhere."})
        if len(urls) < 3:
            issues.append({"severity": "WARN", "code": "THIN_SOURCE_LIST", "message": f"Only {len(urls)} source link(s) detected."})
        if primary_sources == 0:
            issues.append({"severity": "WARN", "code": "NO_PRIMARY_SOURCE_SIGNAL", "message": "No Wizards/official primary-source URL detected."})
        if args.strict_reviewed and editorial_status in {"reviewed", "benchmark"}:
            if generic:
                issues.append({"severity": "FAIL", "code": "REVIEWED_PAGE_GENERIC_LANGUAGE", "message": "A reviewed page contains prohibited generic dossier language."})
            if ratio >= 0.25:
                issues.append({"severity": "FAIL", "code": "REVIEWED_PAGE_DUPLICATION", "message": "A reviewed page exceeds the duplication threshold."})
        hard_failures += sum(issue["severity"] == "FAIL" for issue in issues)
        results.append({
            "file": filename,
            "cardName": subject,
            "editorialStatus": editorial_status,
            "paragraphs": len(paragraphs),
            "duplicateParagraphInstances": duplicate_instances,
            "highFrequencyParagraphInstances": high_duplication,
            "maxParagraphFrequency": max_frequency,
            "duplicateRatio": round(ratio, 4),
            "sourceLinks": len(urls),
            "primarySourceSignals": primary_sources,
            "genericPatterns": generic,
            "issues": issues,
        })

    payload = {
        "schemaVersion": "2.0",
        "root": str(root),
        "articles": len(results),
        "uniqueParagraphs": len(frequency),
        "paragraphInstances": sum(frequency.values()),
        "duplicatedAtLeastTwice": sum(count for count in frequency.values() if count >= 2),
        "hardFailures": hard_failures,
        "status": "FAIL" if hard_failures else "PASS",
        "results": results,
    }
    (output / "editorial-quality.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (output / "editorial-quality.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["file", "card", "editorial_status", "paragraphs", "duplicate_ratio", "max_frequency", "source_links", "primary_sources", "generic_patterns", "issue_codes"])
        for result in results:
            writer.writerow([
                result["file"], result["cardName"], result["editorialStatus"], result["paragraphs"],
                result["duplicateRatio"], result["maxParagraphFrequency"], result["sourceLinks"],
                result["primarySourceSignals"], ";".join(result["genericPatterns"]),
                ";".join(issue["code"] for issue in result["issues"]),
            ])
    statuses = Counter(result["editorialStatus"] for result in results)
    codes = Counter(issue["code"] for result in results for issue in result["issues"])
    lines = [
        "# Editorial V2 quality audit", "",
        f"- Articles: **{len(results)}**",
        f"- Paragraph instances: **{payload['paragraphInstances']}**",
        f"- Exact unique paragraphs: **{payload['uniqueParagraphs']}**",
        f"- Hard failures: **{hard_failures}**",
        "", "## Editorial status",
    ] + [f"- `{key}`: {value}" for key, value in statuses.most_common()] + [
        "", "## Findings",
    ] + [f"- `{key}`: {value}" for key, value in codes.most_common()]
    (output / "editorial-quality.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "articles": len(results),
        "paragraphInstances": payload["paragraphInstances"],
        "uniqueParagraphs": payload["uniqueParagraphs"],
        "hardFailures": hard_failures,
        "status": payload["status"],
        "issueCounts": dict(codes),
    }, indent=2))
    return 1 if hard_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
