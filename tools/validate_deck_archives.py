#!/usr/bin/env python3
"""Strict deck-archive validation for Compulsive Research.

Every displayed total must be derived from integer row quantities. Official
preconstructed products may legitimately have no sideboard. Tournament-impact
callouts are required when the documentary archive contains a subject-card
appearance at a major event or in a winning list.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
import re
from collections import Counter
from pathlib import Path

from bs4 import BeautifulSoup

from canonicalize_deck_archives import DETAIL_RE, article_subject, deck_kind, group_label, is_side, parse_fact, text_qty

TOTAL_CONTEXT_RE = re.compile(
    r"(?:Main deck|Sideboard|recorded size:|main deck and)\s*\d{4,}", re.I
)


def add(issues: list[dict], severity: str, code: str, message: str, deck: int | None = None) -> None:
    row = {"severity": severity, "code": code, "message": message}
    if deck is not None:
        row["deck"] = deck
    issues.append(row)


def expected_totals(deck) -> tuple[int, int, list[tuple[str, int]]]:
    main = side = 0
    groups: list[tuple[str, int]] = []
    for group in deck.select(".group"):
        heading = group.find(["h3", "h4", "h5"])
        label = group_label(heading)
        total = 0
        for row in group.select(".row"):
            qty = row.select_one(".qty")
            if qty is None:
                # Human-readable rows such as "No complete sideboard supplied" are notes.
                continue
            total += text_qty(qty)
        groups.append((label, total))
        if is_side(label):
            side += total
        else:
            main += total
    return main, side, groups


def inspect(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8", errors="replace")
    subject = article_subject(raw, path)
    issues: list[dict] = []
    facts = []
    decks = [m for m in DETAIL_RE.finditer(raw) if "official-mtg-deck" not in m.group(0).split(">", 1)[0]]
    if not decks:
        if 'class="deck-research-status"' not in raw:
            add(issues, "FAIL", "MISSING_DECKS_OR_RESEARCH_NOTICE", "No documentary deck component and no transparent research-status notice.")
    for index, match in enumerate(decks, start=1):
        fragment = match.group(0)
        soup = BeautifulSoup(fragment, "html.parser")
        deck = soup.find("details")
        if deck is None:
            add(issues, "FAIL", "DECK_PARSE", "Deck component could not be parsed.", index)
            continue
        try:
            main, side, groups = expected_totals(deck)
        except ValueError as exc:
            add(issues, "FAIL", "NONINTEGER_QUANTITY", str(exc), index)
            continue
        facts.append(parse_fact(deck, subject))
        if deck.get("data-main-count") != str(main):
            add(issues, "FAIL", "MAIN_DATA_TOTAL", f"data-main-count is {deck.get('data-main-count')!r}; rows sum to {main}.", index)
        if deck.get("data-sideboard-count") != str(side):
            add(issues, "FAIL", "SIDE_DATA_TOTAL", f"data-sideboard-count is {deck.get('data-sideboard-count')!r}; rows sum to {side}.", index)
        kind = deck_kind(deck)
        if kind not in {"tournament-registration", "commercial-preconstructed", "curated-example", "official-digital-deck"}:
            add(issues, "FAIL", "DECK_KIND", f"Unknown deck kind {kind!r}.", index)
        for label, total in groups:
            headings = [h for h in deck.select(".group h3, .group h4, .group h5") if group_label(h) == label]
            # Duplicate labels are possible; check at least one exact heading for each occurrence below instead.
        for group, (label, total) in zip(deck.select(".group"), groups):
            heading = group.find(["h3", "h4", "h5"])
            shown = heading.get_text(" ", strip=True) if heading else ""
            if not re.search(rf"[·|—-]\s*{total}\s*$", shown):
                add(issues, "FAIL", "GROUP_TOTAL", f"{label!r} heading does not display row sum {total}: {shown!r}.", index)
        meta = deck.select_one(".deck-meta .small")
        if meta:
            shown = meta.get_text(" ", strip=True)
            if f"Main deck {main}" not in shown:
                add(issues, "FAIL", "META_MAIN_TOTAL", f"Metadata does not display Main deck {main}: {shown!r}.", index)
            if side and f"Sideboard {side}" not in shown:
                add(issues, "FAIL", "META_SIDE_TOTAL", f"Metadata does not display Sideboard {side}: {shown!r}.", index)
            if not side and not re.search(r"No (?:recorded )?sideboard", shown, re.I):
                add(issues, "FAIL", "META_NO_SIDEBOARD", f"Zero-sideboard deck is not labeled as such: {shown!r}.", index)
        else:
            add(issues, "WARN", "MISSING_DECK_META", "Deck lacks .deck-meta .small.", index)
        if TOTAL_CONTEXT_RE.search(fragment):
            add(issues, "FAIL", "CONCATENATED_TOTAL", "A four-or-more digit number remains in a deck-total context.", index)
        paragraph = deck.select_one(".deck-body > p")
        if paragraph:
            ptext = paragraph.get_text(" ", strip=True)
            if kind == "commercial-preconstructed":
                if str(main) not in ptext:
                    add(issues, "FAIL", "PROVENANCE_MAIN_TOTAL", "Preconstructed-deck provenance paragraph omits the computed main total.", index)
            elif f"{main} cards in the main deck" not in ptext:
                add(issues, "FAIL", "PROVENANCE_MAIN_TOTAL", "Deck provenance paragraph does not carry the computed main total.", index)
        pre = deck.find("pre", id=True)
        if pre:
            pre_text = pre.get_text("", strip=False)
            for label, total in groups:
                if not re.search(rf"(?m)^\s*{re.escape(label)}\s*[·|—-]\s*{total}\s*$", pre_text):
                    add(issues, "FAIL", "COPY_TOTAL", f"Copy decklist does not display {label} · {total}.", index)
        if kind == "commercial-preconstructed" and side == 0:
            # Explicitly valid: commercial products generally do not use tournament sideboards.
            pass
        elif kind == "tournament-registration" and side not in {0, 15}:
            exception = deck.get("data-source-size-exception")
            if exception:
                ptext = paragraph.get_text(" ", strip=True) if paragraph else ""
                if not re.search(r"source-recorded|published.*(?:16|nonstandard)|preserves?", ptext, re.I):
                    add(issues, "FAIL", "UNDOCUMENTED_SIZE_EXCEPTION", f"Source-size exception {exception!r} lacks an explanatory provenance note.", index)
            else:
                add(issues, "WARN", "UNUSUAL_TOURNAMENT_SIDEBOARD", f"Tournament registration has {side} sideboard cards; verify source rather than coercing it to 15.", index)

    if 'class="preconstructed-archive official-mtg-decks"' not in raw:
        add(issues, "FAIL", "MISSING_OFFICIAL_MTG_SECTION", "Static Official Magic the Gathering deck section is missing.")
    if 'preconstructed-decks.js' in raw:
        add(issues, "FAIL", "LEGACY_PRECON_SCRIPT", "The obsolete runtime preconstructed-decks.js loader is still present.")
    if 'href="preconstructed-decks.css"' not in raw and 'href="assets/preconstructed-decks.css"' not in raw:
        add(issues, "FAIL", "MISSING_PRECON_STYLE", "preconstructed-decks.css is not loaded.")
    if any(f.significant for f in facts) and 'class="tournament-impact"' not in raw:
        add(issues, "FAIL", "MISSING_TOURNAMENT_IMPACT", "A significant documentary result exists but no tournament-impact callout is present.")
    if subject.casefold() == "thoughtseize":
        if "oversized check" not in raw or "not presented as fact" not in raw:
            add(issues, "FAIL", "THOUGHTSEIZE_FACT_CHECK", "Thoughtseize must preserve the verified Worlds result and reject the unverified art-print anecdote.")

    return {
        "file": path.name,
        "card": subject,
        "deck_count": len(decks),
        "significant_results": sum(f.significant for f in facts),
        "issues": issues,
        "status": "FAIL" if any(i["severity"] == "FAIL" for i in issues) else ("WARN" if issues else "PASS"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()
    root = args.root.resolve()
    out = (args.output_dir or (root / "deck-archive-validation")).resolve()
    out.mkdir(parents=True, exist_ok=True)
    files = [p for p in sorted(root.glob("*.html")) if p.name != "index.html" and re.search(r'<details\b[^>]*class=["\'][^"\']*\bdeck\b', p.read_text(encoding="utf-8", errors="replace"), re.I)]
    with ProcessPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        results = list(pool.map(inspect, files, chunksize=8))
    status_counts = Counter(r["status"] for r in results)
    code_counts = Counter(i["code"] for r in results for i in r["issues"])
    payload = {
        "root": str(root),
        "articles": len(results),
        "decks": sum(r["deck_count"] for r in results),
        "status_counts": dict(status_counts),
        "issue_code_counts": dict(code_counts),
        "results": results,
    }
    (out / "deck-validation.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [
        "# Deck archive validation", "",
        f"- Articles: **{payload['articles']}**", f"- Decks: **{payload['decks']}**",
        f"- Pass: **{status_counts.get('PASS', 0)}**", f"- Warn: **{status_counts.get('WARN', 0)}**", f"- Fail: **{status_counts.get('FAIL', 0)}**", "",
        "## Issue counts", "",
    ]
    if code_counts:
        lines += [f"- `{code}`: {count}" for code, count in code_counts.most_common()]
    else:
        lines.append("No issues found.")
    (out / "deck-validation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({k: payload[k] for k in ["articles", "decks", "status_counts", "issue_code_counts"]}, indent=2))
    return 1 if status_counts.get("FAIL", 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
