#!/usr/bin/env python3
"""Rebuild hidden copy-decklist text from the visible canonical deck rows."""
from __future__ import annotations
import argparse
import re
from pathlib import Path
from bs4 import BeautifulSoup
from canonicalize_deck_archives import DETAIL_RE, group_label, text_qty, row_card_name


def rebuild(fragment: str) -> tuple[str, bool]:
    soup = BeautifulSoup(fragment, "html.parser")
    deck = soup.find("details")
    if deck is None:
        return fragment, False
    pre = deck.find("pre", id=True)
    if pre is None:
        return fragment, False
    lines: list[str] = []
    summary = deck.find("summary")
    strong = summary.find("strong") if summary else None
    small = summary.find("small") if summary else None
    if strong:
        lines.append(strong.get_text(" ", strip=True))
    if small:
        lines.append(small.get_text(" ", strip=True))
    if lines:
        lines.append("")
    for group in deck.select(".group"):
        heading = group.find(["h3", "h4", "h5"])
        label = group_label(heading)
        rows = []
        total = 0
        for row in group.select(".row"):
            qty = row.select_one(".qty")
            if qty is None:
                note = row.get_text(" ", strip=True)
                if note:
                    rows.append(note)
                continue
            count = text_qty(qty)
            total += count
            rows.append(f"{count} {row_card_name(row)}")
        lines.append(f"{label} · {total}")
        lines.extend(rows)
        lines.append("")
    new_text = "\n".join(lines).rstrip()
    changed = pre.get_text("", strip=False) != new_text
    pre.string = new_text
    return str(deck), changed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path.cwd())
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    root = args.root.resolve()
    files = decks = changed_files = changed_decks = 0
    for path in sorted(root.glob("*.html")):
        if path.name == "index.html":
            continue
        raw = path.read_text(encoding="utf-8", errors="replace")
        if not re.search(r'<details\b[^>]*class=["\'][^"\']*\bdeck\b', raw, re.I):
            continue
        files += 1
        local_changed = False
        def repl(m):
            nonlocal decks, changed_decks, local_changed
            decks += 1
            new, changed = rebuild(m.group(0))
            if changed:
                changed_decks += 1
                local_changed = True
            return new
        new_raw = DETAIL_RE.sub(repl, raw)
        if local_changed:
            changed_files += 1
            if not args.check:
                path.write_text(new_raw, encoding="utf-8")
    print({"articles": files, "decks": decks, "changed_articles": changed_files, "changed_decks": changed_decks, "mode": "check" if args.check else "write"})
    return 1 if args.check and changed_decks else 0

if __name__ == "__main__":
    raise SystemExit(main())
