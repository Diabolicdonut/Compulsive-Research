#!/usr/bin/env python3
"""Refresh Reader V3.1 Numbered Wave 1 review metadata from current HTML.

This keeps the story ledger, migration metrics, review index, and package manifest
bound to the actual article files after a localized correction.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from bs4 import BeautifulSoup

from reader_experience_v3 import editorial_word_count, reading_time_minutes
from validate_reader_experience_v3 import STOCK_MEMORY_OPENING, opening_prefix

ROOT = Path(__file__).resolve().parents[1]
START, END = 11, 50
WORD_RE = re.compile(r"\b[\w’'-]+\b")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def article_path(entry: int) -> Path:
    matches = list(ROOT.glob(f"{entry:03d}-*.html"))
    if len(matches) != 1:
        raise RuntimeError(f"entry {entry:03d}: expected one article, found {len(matches)}")
    return matches[0]


def collect(existing: dict[int, dict]) -> list[dict]:
    rows: list[dict] = []
    for entry in range(START, END + 1):
        path = article_path(entry)
        soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="ignore"), "lxml")
        body = soup.body
        vignette = soup.select_one("#opening > .play-vignette")
        strategic = soup.find("section", id="strategic-legacy-brief")
        opening = soup.find("section", id="opening")
        if body is None or vignette is None or opening is None:
            raise RuntimeError(f"{path.name}: missing Reader V3.1 structure")
        story_p = vignette.find("p")
        story = story_p.get_text(" ", strip=True) if story_p else ""
        title_node = vignette.find("h3")
        deck_ref = (vignette.get("data-vignette-deck-reference") or "").strip()
        deck_titles = {n.get_text(" ", strip=True) for n in soup.select("details.deck summary strong")}
        count = editorial_word_count(soup)
        old = existing.get(entry, {})
        row = {
            "entry": entry,
            "file": path.name,
            "card": body.get("data-article-card") or path.stem,
            "storyTitle": title_node.get_text(" ", strip=True) if title_node else "",
            "storyWords": len(WORD_RE.findall(story)),
            "openingMode": (vignette.get("data-vignette-opening") or "").strip(),
            "normalizedOpeningSixWords": opening_prefix(story),
            "stockMemoryCue": bool(STOCK_MEMORY_OPENING.search(story)),
            "era": (vignette.get("data-vignette-era") or "").strip(),
            "matchup": (vignette.get("data-vignette-matchup") or "").strip(),
            "deckReference": deck_ref,
            "deckReferenceFoundInArticle": deck_ref in deck_titles,
            "scenario": (vignette.get("data-vignette-scenario") or "").strip(),
            "articleEditorialWords": count,
            "readTimeMinutes": reading_time_minutes(count),
            "storyBeforeStrategicLegacy": vignette.parent is opening and opening.find_next_sibling("section") is strategic,
            "strategicLegacyImmediatelyAfterOpening": opening.find_next_sibling("section") is strategic,
            "originalSha256": old.get("originalSha256", ""),
            "finalSha256": sha256(path),
            "originalBytes": old.get("originalBytes", 0),
            "finalBytes": path.stat().st_size,
        }
        if vignette.select_one("script.vignette-sequence-data[type='application/json']"):
            row["sequenceLedger"] = True
            row["sequenceLedgerSchemaVersion"] = 1
        rows.append(row)
    return rows


def aggregates(rows: list[dict]) -> dict:
    story_words = [r["storyWords"] for r in rows]
    article_words = [r["articleEditorialWords"] for r in rows]
    times = [r["readTimeMinutes"] for r in rows]
    return {
        "articleCount": len(rows),
        "storyCount": len(rows),
        "storyWordRange": {
            "min": min(story_words),
            "max": max(story_words),
            "average": round(sum(story_words) / len(story_words), 2),
        },
        "articleEditorialWordRange": {
            "min": min(article_words),
            "max": max(article_words),
            "average": round(sum(article_words) / len(article_words), 2),
            "total": sum(article_words),
        },
        "readTimeRangeMinutes": {
            "min": min(times),
            "max": max(times),
            "average": round(sum(times) / len(times), 2),
            "distribution": {str(k): v for k, v in sorted(Counter(times).items())},
        },
        "uniqueNormalizedOpeningSixWords": len({r["normalizedOpeningSixWords"] for r in rows}),
        "stockMemoryCueCount": sum(bool(r["stockMemoryCue"]) for r in rows),
        "exactDeckReferencesFound": sum(bool(r["deckReferenceFoundInArticle"]) for r in rows),
        "strategicLegacyImmediatelyAfterOpening": sum(bool(r["strategicLegacyImmediatelyAfterOpening"]) for r in rows),
    }


def refresh_metrics(rows: list[dict], summary: dict) -> None:
    path = ROOT / "validation" / "reader-v3.1-entries-011-050-metrics.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data.update(summary)
    data["generatedAt"] = dt.datetime.now(dt.timezone.utc).isoformat()
    data["records"] = rows
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Reader V3.1 entries 011–050 metrics",
        "",
        f"- Articles: **{len(rows)}**",
        f"- Story word range: **{summary['storyWordRange']['min']}–{summary['storyWordRange']['max']}**",
        f"- Editorial word range: **{summary['articleEditorialWordRange']['min']:,}–{summary['articleEditorialWordRange']['max']:,}**",
        f"- Read-time range: **{summary['readTimeRangeMinutes']['min']}–{summary['readTimeRangeMinutes']['max']} minutes**",
        f"- Unique normalized six-word story openings: **{summary['uniqueNormalizedOpeningSixWords']}**",
        f"- Stock memory cues: **{summary['stockMemoryCueCount']}**",
        f"- Exact Deck Archive references found: **{summary['exactDeckReferencesFound']}/{len(rows)}**",
        "",
        "| # | Card | Story title | Story words | Editorial words | Read time | Deck Archive reference |",
        "|---:|---|---|---:|---:|---:|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['entry']:03d} | {r['card']} | {r['storyTitle']} | {r['storyWords']} | "
            f"{r['articleEditorialWords']:,} | {r['readTimeMinutes']} min | {r['deckReference']} |"
        )
    (ROOT / "validation" / "reader-v3.1-entries-011-050-metrics.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def refresh_migration_ledger(rows: list[dict]) -> None:
    path = ROOT / "READER-V3.1-MIGRATION-LEDGER.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["records"] = rows
    note = "Hypnotic Specter framing and vignette chronology corrected; mechanics-claim and early-turn regression validation added."
    notes = data.setdefault("contentNotes", [])
    if note not in notes:
        notes.append(note)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def refresh_story_ledger(rows: list[dict]) -> None:
    path = ROOT / "research-dossiers" / "READER-V3.1-NUMBERED-WAVE-01-STORY-LEDGER.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    stories = []
    for r in rows:
        soup = BeautifulSoup((ROOT / r["file"]).read_text(encoding="utf-8"), "lxml")
        vignette = soup.select_one("#opening > .play-vignette")
        story = vignette.find("p").get_text(" ", strip=True)
        rec = {
            "entry": r["entry"],
            "file": r["file"],
            "card": r["card"],
            "title": r["storyTitle"],
            "era": r["era"],
            "matchup": r["matchup"],
            "deckReference": r["deckReference"],
            "scenario": r["scenario"],
            "openingMode": r["openingMode"],
            "wordCount": r["articleEditorialWords"],
            "readingMinutes": r["readTimeMinutes"],
            "story": story,
        }
        if r.get("sequenceLedger"):
            rec["sequenceLedger"] = True
            rec["sequenceLedgerSchemaVersion"] = 1
        stories.append(rec)
    data["stories"] = stories
    data["method"] = (
        "Each visible story is a representative first-person reconstruction grounded in the exact Deck Archive title "
        "recorded in hidden article metadata. It is not a quotation or a claim that a documented match followed the "
        "narrated sequence word for word. Accelerated openings that continue across turns carry a hidden sequence ledger."
    )
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def refresh_review_index(rows: list[dict]) -> None:
    path = ROOT / "READER-V3.1-ENTRIES-011-050-REVIEW-INDEX.html"
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "lxml")
    tbody = soup.find("tbody")
    if tbody is None:
        raise RuntimeError("review index missing tbody")
    tbody.clear()
    for r in rows:
        tr = soup.new_tag("tr")
        values = [
            f"{r['entry']:03d}",
            None,
            r["storyTitle"],
            str(r["storyWords"]),
            f"{r['articleEditorialWords']:,}",
            f"{r['readTimeMinutes']} min",
            r["deckReference"],
        ]
        for idx, value in enumerate(values):
            td = soup.new_tag("td")
            if idx == 1:
                a = soup.new_tag("a", href=r["file"])
                a.string = r["card"]
                td.append(a)
            else:
                td.string = value
            tr.append(td)
        tbody.append(tr)
    path.write_text(soup.decode(formatter="minimal"), encoding="utf-8")


def refresh_package_manifest(rows: list[dict], summary: dict) -> None:
    path = ROOT / "PACKAGE-MANIFEST-READER-V3.1-011-050.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["contentMetrics"] = summary
    data["fortyArticles"] = [
        {
            "entry": r["entry"],
            "file": r["file"],
            "card": r["card"],
            "storyTitle": r["storyTitle"],
            "editorialWords": r["articleEditorialWords"],
            "readTimeMinutes": r["readTimeMinutes"],
            "sha256": r["finalSha256"],
        }
        for r in rows
    ]
    additions = [
        "008-mox-emerald.html",
        "tools/refine_oral_history_vignettes.py",
        "tools/test_reader_experience_v3_regressions.py",
        "tools/refresh_reader_v31_wave01_metadata.py",
        "validation/hypnotic-specter-correction-2026-08-05/reader-experience-final.txt",
        "validation/hypnotic-specter-correction-2026-08-05/reader-layout-final.txt",
    ]
    files = data.setdefault("deltaPackageFiles", [])
    for item in additions:
        if item not in files:
            files.append(item)
    files.sort()
    data["deltaPackageFileCount"] = len(files)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    metrics_path = ROOT / "validation" / "reader-v3.1-entries-011-050-metrics.json"
    old = json.loads(metrics_path.read_text(encoding="utf-8"))
    existing = {int(r["entry"]): r for r in old.get("records", [])}
    rows = collect(existing)
    summary = aggregates(rows)
    refresh_metrics(rows, summary)
    refresh_migration_ledger(rows)
    refresh_story_ledger(rows)
    refresh_review_index(rows)
    refresh_package_manifest(rows, summary)
    print(
        f"Refreshed Reader V3.1 Wave 1 metadata: {len(rows)} articles, "
        f"story words {summary['storyWordRange']['min']}-{summary['storyWordRange']['max']}, "
        f"editorial total {summary['articleEditorialWordRange']['total']:,}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
