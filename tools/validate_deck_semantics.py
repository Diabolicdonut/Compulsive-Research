#!/usr/bin/env python3
"""Validate production deck provenance and low-false-positive semantic errors.

This validator intentionally does not attempt to solve deckbuilding. It rejects
synthetic production kinds, verifies subject-card presence, checks date coherence,
and catches the strongest color-production impossibility: a deck whose land section
contains only one basic-land name while known spells require other colors.

Official Wizards product components are validated by validate_official_mtg_decks.py
and are skipped here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from lxml import html

BASIC = {"Plains": "W", "Island": "U", "Swamp": "B", "Mountain": "R", "Forest": "G"}
CLASS = "contains(concat(' ', normalize-space(@class), ' '), ' {name} ')"


def norm_name(value: Any) -> str:
    text = re.sub(r"[’‘`´]", "'", str(value or ""))
    text = re.sub(r"[‐‑‒–—―]", "-", text)
    text = ''.join(ch for ch in unicodedata.normalize('NFKD', text) if not unicodedata.combining(ch))
    return text.strip()


def load_card_index(root: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for filename in [
        "remaining-entry-card-data.json",
        "honorable-legacy-expansion-card-data.json",
        "honorable-vintage-expansion-card-data.json",
        "honorable-typal-card-data.json",
    ]:
        path = root / "data" / filename
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        for card in payload.get("cards", []):
            name = card.get("articleName") or card.get("canonicalName") or card.get("name")
            if not name:
                continue
            out[norm_name(name)] = {
                "colors": set(card.get("colors") or []),
                "releaseDate": card.get("releaseDate", ""),
            }
    return out


def year_of(text: str) -> int | None:
    match = re.search(r"\b(?:19|20)\d{2}\b", text or "")
    return int(match.group()) if match else None


def text_content(node) -> str:
    return " ".join(node.text_content().split())


def deck_rows(deck) -> list[tuple[int, str, str]]:
    result: list[tuple[int, str, str]] = []
    for row in deck.xpath(f".//*[{CLASS.format(name='row')}]"):
        qty_nodes = row.xpath(f".//*[{CLASS.format(name='qty')}]")
        card_nodes = row.xpath(f".//*[{CLASS.format(name='card-name')} and @data-card]")
        if not qty_nodes or not card_nodes:
            continue
        try:
            count = int(text_content(qty_nodes[0]))
        except ValueError:
            continue
        name = card_nodes[0].get("data-card", "")
        group_heading = ""
        groups = row.xpath(f"ancestor::*[{CLASS.format(name='group')}][1]")
        if groups:
            headings = groups[0].xpath(".//h3 | .//h4 | .//h5")
            if headings:
                group_heading = text_content(headings[0])
        result.append((count, name, group_heading))
    return result


def deck_fingerprint(items: list[tuple[int, str, str]]) -> str:
    pairs = sorted((norm_name(name), count) for count, name, _ in items)
    return hashlib.sha256("|".join(f"{name}:{count}" for name, count in pairs).encode()).hexdigest()


def active_pages(root: Path) -> list[Path]:
    numbered = list(root.glob("[0-9][0-9][0-9]-*.html")) + list(root.glob("[0-9][0-9][0-9][0-9]-*.html"))
    honorable = list(root.glob("honorable-*.html"))
    return sorted(set(numbered + honorable))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    root = args.root.resolve()
    output = (args.output_dir or root / "audit/deck-semantics").resolve()
    output.mkdir(parents=True, exist_ok=True)
    card_index = load_card_index(root)

    results = []
    fingerprints: dict[str, list[tuple[str, str, int, str]]] = defaultdict(list)

    for path in active_pages(root):
        try:
            tree = html.fromstring(path.read_bytes())
        except Exception as exc:
            results.append({"file": path.name, "cardName": "", "decks": [], "parseError": str(exc)})
            continue
        body_nodes = tree.xpath("//body")
        body = body_nodes[0] if body_nodes else None
        subject = body.get("data-article-card", "") if body is not None else ""
        deck_results = []
        deck_nodes = tree.xpath(f"//details[{CLASS.format(name='deck')}]")
        production_index = 0
        for deck in deck_nodes:
            kind = (deck.get("data-deck-kind") or "").strip()
            classes = set((deck.get("class") or "").split())
            official_parent = bool(deck.xpath(f"ancestor::*[{CLASS.format(name='official-mtg-decks')}]") )
            if kind == "official-mtg-product" or "official-mtg-deck" in classes or official_parent:
                continue
            production_index += 1
            issues = []
            items = deck_rows(deck)
            names = [norm_name(name) for _, name, _ in items]

            if kind == "editorial-study":
                issues.append({"severity": "FAIL", "code": "EDITORIAL_STUDY_FORBIDDEN", "message": "Synthetic study deck remains in production."})
            if kind not in {"tournament-registration", "official-digital-deck", "curated-example"}:
                issues.append({"severity": "FAIL", "code": "UNKNOWN_PRODUCTION_DECK_KIND", "message": kind or "(missing)"})
            if subject and norm_name(subject) not in names:
                issues.append({"severity": "FAIL", "code": "SUBJECT_CARD_ABSENT", "message": subject})

            if kind == "curated-example":
                if not deck.get("data-legality-as-of"):
                    issues.append({"severity": "FAIL", "code": "CURATED_MISSING_LEGALITY_DATE", "message": "data-legality-as-of required."})
                if not deck.get("data-reviewed-by"):
                    issues.append({"severity": "FAIL", "code": "CURATED_MISSING_REVIEWER", "message": "data-reviewed-by required."})

            if kind == "tournament-registration":
                external = deck.get("data-source-url") or deck.xpath(".//a[starts-with(@href, 'http')]/@href")
                if not external:
                    issues.append({"severity": "WARN", "code": "DECK_SOURCE_NOT_BOUND", "message": "No machine-readable source URL is bound to this deck component."})

            deck_text = text_content(deck)
            event_year = year_of(deck_text)
            if event_year:
                for _, name, _ in items:
                    release = card_index.get(norm_name(name), {}).get("releaseDate", "")
                    if release and release[:4].isdigit() and int(release[:4]) > event_year:
                        issues.append({
                            "severity": "FAIL",
                            "code": "CARD_AFTER_EVENT_DATE",
                            "message": f"{name} released {release}, while deck text indicates {event_year}.",
                        })

            land_names = [norm_name(name) for _, name, heading in items if re.search(r"\bLands?\b", heading, re.I)]
            unique_lands = set(land_names)
            if len(unique_lands) == 1 and next(iter(unique_lands), None) in BASIC:
                only_land = next(iter(unique_lands))
                available = {BASIC[only_land]}
                needed: set[str] = set()
                for name in names:
                    if name not in BASIC:
                        needed.update(card_index.get(name, {}).get("colors", set()))
                off_colors = needed - available
                if off_colors:
                    issues.append({
                        "severity": "WARN",
                        "code": "MONOBASIC_COLOR_WARNING",
                        "message": f"Only {only_land} is present, but known spells require {','.join(sorted(off_colors))}.",
                    })

            fingerprint = deck_fingerprint(items)
            fingerprints[fingerprint].append((path.name, subject, production_index, kind))
            deck_results.append({
                "deck": production_index,
                "kind": kind,
                "cards": sum(count for count, _, _ in items),
                "issues": issues,
                "status": "FAIL" if any(i["severity"] == "FAIL" for i in issues) else ("WARN" if issues else "PASS"),
            })
        results.append({"file": path.name, "cardName": subject, "decks": deck_results})

    reused = {fp: uses for fp, uses in fingerprints.items() if len({norm_name(use[1]) for use in uses}) > 1}
    lookup = {(result["file"], deck["deck"]): deck for result in results for deck in result["decks"]}
    for uses in reused.values():
        for filename, _subject, index, _kind in uses:
            deck = lookup[(filename, index)]
            deck["issues"].append({
                "severity": "WARN",
                "code": "CROSS_ARTICLE_DECK_FINGERPRINT",
                "message": f"Deck fingerprint appears in {len(uses)} components across unrelated article subjects.",
            })
            deck["status"] = "FAIL" if any(i["severity"] == "FAIL" for i in deck["issues"]) else "WARN"

    all_issues = [issue for result in results for deck in result["decks"] for issue in deck["issues"]]
    codes = Counter(issue["code"] for issue in all_issues)
    statuses = Counter(deck["status"] for result in results for deck in result["decks"])
    payload = {
        "articles": len(results),
        "decks": sum(len(result["decks"]) for result in results),
        "statusCounts": dict(statuses),
        "issueCounts": dict(codes),
        "reusedFingerprints": len(reused),
        "status": "FAIL" if statuses.get("FAIL") else "PASS",
        "results": results,
    }
    (output / "deck-semantics.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [
        "# Deck semantics validation", "",
        f"- Articles: **{payload['articles']}**",
        f"- Decks: **{payload['decks']}**",
        f"- Pass: **{statuses.get('PASS', 0)}**",
        f"- Warn: **{statuses.get('WARN', 0)}**",
        f"- Fail: **{statuses.get('FAIL', 0)}**",
        "", "## Findings",
    ] + [f"- `{code}`: {count}" for code, count in codes.most_common()]
    (output / "deck-semantics.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ["articles", "decks", "statusCounts", "issueCounts", "reusedFingerprints", "status"]}, indent=2))
    return 1 if statuses.get("FAIL") else 0


if __name__ == "__main__":
    raise SystemExit(main())
