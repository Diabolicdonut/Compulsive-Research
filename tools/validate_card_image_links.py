#!/usr/bin/env python3
"""Validate deck-card image links and double-faced-card handling.

This validator is intentionally network-free. It verifies that every displayed
card row is interactive and that every article carries the shared runtime that
uses Scryfall card-face objects to distinguish true front/back images.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import unicodedata

from bs4 import BeautifulSoup

REQUIRED_RUNTIME_TOKENS = (
    "card.card_faces",
    "face.image_uris",
    "hydrateLeadCard",
    "preview-track",
    "data-card-name",
)


def issue(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message}

def normalize_name(value: str) -> str:
    value = value.replace("’", "'").replace("‘", "'").replace("–", "-").replace("—", "-")
    return unicodedata.normalize("NFKC", value).casefold().strip()


def inspect(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(raw, "html.parser")
    issues: list[dict[str, str]] = []

    body = soup.find("body")
    subject = str(body.get("data-article-card") or "").strip() if body else ""
    if not subject:
        issues.append(issue("ARTICLE_CARD", "body[data-article-card] is missing."))

    previews = soup.select("#preview")
    if len(previews) != 1:
        issues.append(issue("PREVIEW_COUNT", f"Expected exactly one #preview; found {len(previews)}."))
    elif previews[0].select_one(".preview-track") is None:
        issues.append(issue("PREVIEW_TRACK", "#preview lacks .preview-track."))

    if raw.count("CR_CARD_PREVIEW_RUNTIME_START") != 1 or raw.count("CR_CARD_PREVIEW_RUNTIME_END") != 1:
        issues.append(issue("RUNTIME_MARKERS", "Card-preview runtime markers are missing or duplicated."))
    for token in REQUIRED_RUNTIME_TOKENS:
        if token not in raw:
            issues.append(issue("DFC_RUNTIME", f"Shared card-face runtime is missing token {token!r}."))
    if raw.count("CR_CARD_IMAGE_STANDARD_START") != 1 or raw.count("CR_CARD_IMAGE_STANDARD_END") != 1:
        issues.append(issue("STYLE_MARKERS", "Card-image standard style markers are missing or duplicated."))

    leads = soup.select(".card-lead")
    if not leads:
        issues.append(issue("CARD_LEAD", "Namesake card lead is missing."))
    else:
        lead = leads[0]
        if normalize_name(str(lead.get("data-card-name") or "")) != normalize_name(subject):
            issues.append(issue("LEAD_CARD_NAME", "The lead data-card-name does not match body[data-article-card]."))
        if lead.get("data-dfc-mode") != "auto":
            issues.append(issue("LEAD_DFC_MODE", "The lead must use data-dfc-mode=auto."))
        original = soup.select_one(".printing.original-printing[data-scryfall-id]")
        if original is not None and lead.get("data-scryfall-id") != original.get("data-scryfall-id"):
            issues.append(issue("LEAD_SCRYFALL_ID", "Lead Scryfall ID does not match the original-printing record."))

    row_count = 0
    linked_row_count = 0
    for row in soup.select("details.deck .row, details.official-mtg-deck .row"):
        qty = row.select_one(".qty")
        if qty is None:
            continue
        row_count += 1
        cards = row.select(".card-name")
        if len(cards) != 1:
            issues.append(issue("DECK_ROW_LINK", f"A quantity row has {len(cards)} card links instead of one: {row.get_text(' ', strip=True)!r}."))
            continue
        card = cards[0]
        linked_row_count += 1
        if card.get("data-card-unknown") == "true":
            continue
        data_name = str(card.get("data-card") or "").strip()
        visible = card.get_text(" ", strip=True)
        if not data_name:
            issues.append(issue("CARD_DATA_NAME", f"Deck card link lacks data-card: {visible!r}."))
        if card.get("tabindex") != "0":
            issues.append(issue("CARD_TABINDEX", f"Deck card link lacks tabindex=0: {visible!r}."))
        if data_name and visible and data_name != visible:
            # Exact equality is deliberate: card-name aliases must be resolved before rendering.
            issues.append(issue("CARD_NAME_MISMATCH", f"Visible deck card {visible!r} differs from data-card {data_name!r}."))

    official = soup.select_one("details.official-mtg-decks")
    if official is not None and official.get("data-official-deck-count") == "0":
        small = official.select_one(":scope > summary small")
        shown = small.get_text(" ", strip=True) if small else ""
        if shown != "0":
            issues.append(issue("OFFICIAL_ZERO_LABEL", f"Zero-result official section must show exactly '0'; found {shown!r}."))
    if "No official deck products containing" in raw:
        issues.append(issue("LEGACY_NO_LABEL", "Legacy 'No official deck products containing …' summary text remains."))

    if subject == "Delver of Secrets":
        lead = leads[0] if leads else None
        if lead is None or len(lead.select(".card-face-pair figure")) != 2:
            issues.append(issue("DELVER_FACE_IMAGES", "Delver prototype must statically show two card faces."))
        if lead is None or len(lead.select(".dfc-rules-grid .face-rules")) != 2:
            issues.append(issue("DELVER_FACE_RULES", "Delver prototype must statically show one rules panel per face."))
        back = lead.select_one('.card-face-pair img[alt*="Insectile Aberration"]') if lead else None
        if back is None or "face=back" not in str(back.get("src") or ""):
            issues.append(issue("DELVER_BACK_IMAGE", "Insectile Aberration must use the same card ID with face=back."))

    status = "PASS" if not issues else "FAIL"
    return {
        "file": path.name,
        "card": subject,
        "rows": row_count,
        "linkedRows": linked_row_count,
        "issues": issues,
        "status": status,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()
    root = args.root.resolve()
    out = (args.output_dir or (root / "card-image-link-validation")).resolve()
    out.mkdir(parents=True, exist_ok=True)
    files = sorted(set(list(root.glob("[0-9][0-9][0-9]-*.html")) + list(root.glob("[0-9][0-9][0-9][0-9]-*.html")) + list(root.glob("honorable-*.html"))))
    with ProcessPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        results = list(pool.map(inspect, files, chunksize=8))
    statuses = Counter(r["status"] for r in results)
    codes = Counter(i["code"] for r in results for i in r["issues"])
    payload = {
        "root": str(root),
        "articles": len(results),
        "deckRows": sum(r["rows"] for r in results),
        "linkedDeckRows": sum(r["linkedRows"] for r in results),
        "statusCounts": dict(statuses),
        "issueCodeCounts": dict(codes),
        "results": results,
    }
    (out / "card-image-link-validation.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [
        "# Card-image link validation", "",
        f"- Articles: **{payload['articles']}**",
        f"- Deck rows: **{payload['deckRows']}**",
        f"- Linked deck rows: **{payload['linkedDeckRows']}**",
        f"- Pass: **{statuses.get('PASS', 0)}**",
        f"- Fail: **{statuses.get('FAIL', 0)}**", "", "## Issue counts", "",
    ]
    lines.extend([f"- `{code}`: {count}" for code, count in codes.most_common()] or ["No issues found."])
    (out / "card-image-link-validation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({k: payload[k] for k in ("articles", "deckRows", "linkedDeckRows", "statusCounts", "issueCodeCounts")}, indent=2))
    return 1 if statuses.get("FAIL", 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
