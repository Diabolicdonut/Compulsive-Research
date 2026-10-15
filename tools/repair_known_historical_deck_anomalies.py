#!/usr/bin/env python3
"""Apply sourced corrections to a small set of historical deck transcriptions.

This tool deliberately does *not* force every historical list to 60/15. It fixes
only anomalies for which the audit found documentary support, and marks a
published nonstandard registration when no defensible card-level correction is
known.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from bs4 import BeautifulSoup, Tag

from canonicalize_deck_archives import (
    DETAIL_RE,
    article_subject,
    group_label,
    is_side,
    repair_deck,
)

BEN_TITLE = "Ben Rubin — Pro Tour New York 2000"
JUSTIN_TITLE = "Justin Gary — Pro Tour Rome 1998"
OLIVIERI_TITLE = "Nicolas Olivieri — Pro Tour Osaka 2002"
THOUGHT_INVOKER_TITLE = "Thought Invoker"

BEN_NOTE = (
    " This audit follows the 15-card sideboard reproduced in Star City Games’ "
    "retrospective deck archive (two sideboard copies of Lin Sivvi) rather than "
    "the conflicting 16-card transcription found in another database."
)
JUSTIN_NOTE = (
    " The surviving published deck archive explicitly records a 16-card "
    "sideboard; the audit preserves that source-recorded anomaly instead of "
    "silently deleting a card."
)
OLIVIERI_NOTE = (
    " The source labels a 15-card sideboard but names only fourteen cards; the "
    "unidentified fifteenth slot is retained as “Unknown card” rather than "
    "being invented."
)
DIGITAL_NOTE = (
    " This is an official digital opponent deck from MicroProse’s Shandalar, "
    "not a paper tournament registration."
)


def title_of(deck: Tag) -> str:
    strong = deck.select_one("summary strong")
    return strong.get_text(" ", strip=True) if strong else ""


def first_provenance(deck: Tag) -> Tag | None:
    body = deck.select_one(".deck-body")
    if body is None:
        return None
    for child in body.children:
        if isinstance(child, Tag) and child.name == "p" and "small" not in (child.get("class") or []):
            return child
    return None


def append_note(deck: Tag, note: str) -> bool:
    p = first_provenance(deck)
    if p is None:
        return False
    text = p.get_text(" ", strip=True)
    needle = re.sub(r"\s+", " ", note.strip())
    if needle.casefold() not in re.sub(r"\s+", " ", text).casefold():
        p.string = text.rstrip() + note
        return True
    return False


def side_group(deck: Tag) -> Tag | None:
    for group in deck.select(".group"):
        heading = group.find(["h3", "h4", "h5"])
        if is_side(group_label(heading)):
            return group
    return None


def repair_fragment(fragment: str, subject: str, file_name: str, deck_index: int) -> tuple[str, list[str]]:
    soup = BeautifulSoup(fragment, "html.parser")
    deck = soup.find("details")
    if deck is None:
        return fragment, []
    title = title_of(deck)
    actions: list[str] = []

    if title == BEN_TITLE:
        group = side_group(deck)
        if group is not None:
            for row in group.select(".row"):
                card = row.select_one('[data-card="Lin Sivvi, Defiant Hero"]')
                qty = row.select_one(".qty")
                if card is not None and qty is not None:
                    if qty.get_text(" ", strip=True) != "2":
                        qty.string = "2"
                        actions.append("Ben Rubin sideboard Lin Sivvi corrected from 3 to 2")
                    break
        note_added = append_note(deck, BEN_NOTE)
        if deck.get("data-source-resolution") != "scg-retrospective-15-card-sideboard":
            deck["data-source-resolution"] = "scg-retrospective-15-card-sideboard"
            actions.append("Ben Rubin source resolution marker added")
        elif note_added:
            actions.append("Ben Rubin source resolution note added")

    elif title == JUSTIN_TITLE:
        changed = False
        if deck.get("data-source-size-exception") != "published-16-card-sideboard":
            deck["data-source-size-exception"] = "published-16-card-sideboard"
            changed = True
        if append_note(deck, JUSTIN_NOTE):
            changed = True
        if changed:
            actions.append("Justin Gary published 16-card sideboard preserved and marked")

    elif title == OLIVIERI_TITLE:
        group = side_group(deck)
        if group is not None and not group.select_one('[data-card-unknown="true"]'):
            row_soup = BeautifulSoup(
                '<div class="row source-unknown-card"><span class="qty">1</span>'
                '<span class="card-name unresolved-card" data-card-unknown="true">'
                'Unknown card (not identified in surviving source)</span></div>',
                "html.parser",
            )
            group.append(row_soup.div)
            actions.append("Nicolas Olivieri unidentified fifteenth sideboard slot added")
        if deck.get("data-source-resolution") != "published-15-with-one-unknown-card":
            deck["data-source-resolution"] = "published-15-with-one-unknown-card"
            actions.append("Nicolas Olivieri source resolution marker added")
        if append_note(deck, OLIVIERI_NOTE):
            actions.append("Nicolas Olivieri source resolution note added")

    elif title == THOUGHT_INVOKER_TITLE:
        changed = False
        if deck.get("data-deck-kind") != "official-digital-deck":
            deck["data-deck-kind"] = "official-digital-deck"
            changed = True
        badge = deck.select_one(".provenance-badge")
        if badge is not None and badge.get_text(" ", strip=True) != "Official digital deck":
            badge.string = "Official digital deck"
            changed = True
        if append_note(deck, DIGITAL_NOTE):
            changed = True
        if changed:
            actions.append("Thought Invoker reclassified as official digital deck")

    if not actions and title not in {BEN_TITLE, JUSTIN_TITLE, OLIVIERI_TITLE, THOUGHT_INVOKER_TITLE}:
        return fragment, []

    # Recompute every total and all duplicated total surfaces from the edited rows.
    repaired, _, _ = repair_deck(str(deck), subject, file_name, deck_index)
    return repaired, actions


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path.cwd())
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    root = args.root.resolve()

    changed_files = 0
    actions: list[tuple[str, str]] = []
    for path in sorted(root.glob("*.html")):
        if path.name == "index.html":
            continue
        raw = path.read_text(encoding="utf-8", errors="replace")
        if not any(name in raw for name in (BEN_TITLE, JUSTIN_TITLE, OLIVIERI_TITLE, THOUGHT_INVOKER_TITLE)):
            continue
        subject = article_subject(raw, path)
        index = 0
        local_actions: list[str] = []

        def repl(match: re.Match[str]) -> str:
            nonlocal index
            index += 1
            new, found = repair_fragment(match.group(0), subject, path.name, index)
            local_actions.extend(found)
            return new

        new_raw = DETAIL_RE.sub(repl, raw)
        if new_raw != raw:
            changed_files += 1
            if not args.check:
                path.write_text(new_raw, encoding="utf-8")
        for action in local_actions:
            actions.append((path.name, action))

    print({
        "mode": "check" if args.check else "write",
        "changed_files": changed_files,
        "actions": len(actions),
    })
    for file_name, action in actions:
        print(f"- {file_name}: {action}")
    return 1 if args.check and changed_files else 0


if __name__ == "__main__":
    raise SystemExit(main())
