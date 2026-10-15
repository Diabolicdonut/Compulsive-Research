#!/usr/bin/env python3
"""Repair and enrich Compulsive Research deck archives.

The row quantities are the sole authority for every displayed deck total. This
prevents the historical concatenation bug (for example, 4+4+1 being rendered as
"441"). The tool also adds a conservative tournament-impact callout derived
from the article's own documentary decklists and installs the official Wizards
static Official Magic the Gathering deck component.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

from bs4 import BeautifulSoup, Tag

DETAIL_RE = re.compile(r'<details\b[^>]*class=(?P<q>["\'])[^"\']*\bdeck\b[^"\']*(?P=q)[^>]*>.*?</details>', re.I | re.S)
SIDE_WORDS = ("sideboard", "side board", "maybeboard")
SIGNIFICANT_EVENT_RE = re.compile(
    r"world championship|pro tour|players championship|mythic championship|"
    r"magic invitational|grand prix|nationals|national championship|"
    r"world magic cup|championship",
    re.I,
)
TOP_PLACEMENT_RE = re.compile(r"^(?:1st|first|winner|champion|championship winner)\b", re.I)
LONG_NUMBER_RE = re.compile(r"\b\d{4,}\b")
DECK_SECTION_RE = re.compile(r'<section\b[^>]*\bid=["\'](?:decklists|decks)["\'][^>]*>.*?</section>', re.I | re.S)


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def text_qty(node: Tag | None) -> int:
    if node is None:
        raise ValueError("missing quantity")
    value = node.get_text(" ", strip=True)
    if not re.fullmatch(r"\d+", value):
        raise ValueError(f"non-integer quantity {value!r}")
    return int(value)


def group_label(heading: Tag | None) -> str:
    if heading is None:
        return "Cards"
    return re.split(r"\s*[·|—-]\s*\d+\s*$", heading.get_text(" ", strip=True), maxsplit=1)[0].strip() or "Cards"


def is_side(label: str) -> bool:
    low = label.casefold()
    return any(word in low for word in SIDE_WORDS)


def row_card_name(row: Tag) -> str:
    card = row.select_one("[data-card]")
    if card and card.get("data-card"):
        return str(card.get("data-card")).strip()
    clone = BeautifulSoup(str(row), "html.parser")
    qty = clone.select_one(".qty")
    if qty:
        qty.decompose()
    return clone.get_text(" ", strip=True)


def direct_first_paragraph(body: Tag) -> Tag | None:
    for child in body.children:
        if isinstance(child, Tag) and child.name == "p" and "small" not in (child.get("class") or []):
            return child
    return None


def deck_kind(deck: Tag) -> str:
    existing = str(deck.get("data-deck-kind") or "")
    badge = deck.select_one(".provenance-badge")
    summary = deck.find("summary")
    paragraph = deck.select_one(".deck-body > p")
    text = " ".join(
        node.get_text(" ", strip=True)
        for node in (badge, summary, paragraph)
        if node is not None
    ).casefold()
    # Digital product/opponent decks are documentary records, but they are not
    # paper tournament registrations. Correct stale generated classifications.
    if "official digital deck" in text or "shandalar" in text or "digital opponent deck" in text:
        return "official-digital-deck"
    if existing:
        return existing
    if "preconstruct" in text or "commercial" in text or "theme deck" in text:
        return "commercial-preconstructed"
    if "supplement" in text or "editorial" in text or "model" in text:
        return "editorial-study"
    return "tournament-registration"


def replace_preserved_size(text: str, kind: str, main: int, side: int) -> str:
    if kind == "commercial-preconstructed":
        suffix = (
            f"The official commercial list contains {main} cards in its main product deck"
            + (f" and {side} cards in its published sideboard." if side else "; it was sold without a tournament sideboard.")
        )
    else:
        suffix = (
            f"The list is preserved at its recorded size: {main} cards in the main deck"
            + (f" and {side} in the sideboard." if side else "; no sideboard was recorded.")
        )
    # Replace only the generated count sentence. Later provenance/fact-check
    # sentences must survive subsequent canonicalization passes.
    patterns = (
        r"The list is preserved at its recorded size:\s*[^.]*\.",
        r"The official commercial list contains\s*[^.]*\.",
        r"It contains\s*[^.]*\.",
    )
    for pattern in patterns:
        replaced, count = re.subn(pattern, suffix, text, count=1, flags=re.I | re.S)
        if count:
            return re.sub(r"\s+", " ", replaced).strip()
    return (text.rstrip() + " " + suffix).strip()


def update_pre_text(pre: Tag, groups: list[tuple[str, int]]) -> None:
    value = pre.get_text("", strip=False)
    for label, total in groups:
        pattern = re.compile(rf"(?m)^(\s*{re.escape(label)}\s*[·|—-]\s*)\d+(\s*)$")
        value, count = pattern.subn(rf"\g<1>{total}\g<2>", value, count=1)
        if count == 0 and is_side(label):
            value = re.sub(r"(?mi)^(\s*(?:sideboard|side board|maybeboard)\s*[·|—-]\s*)\d+(\s*)$", rf"\g<1>{total}\g<2>", value, count=1)
    pre.string = value


@dataclass
class DeckFact:
    player: str
    event: str
    placement: str
    date: str
    copies_main: int
    copies_side: int
    significant: bool
    kind: str


@dataclass
class DeckAudit:
    file: str
    deck_index: int
    main_total: int
    sideboard_total: int
    kind: str
    old_long_number: bool
    groups: dict[str, int]


def parse_fact(deck: Tag, subject: str) -> DeckFact:
    summary = deck.find("summary")
    strong = summary.find("strong") if summary else None
    title = strong.get_text(" ", strip=True) if strong else ""
    if " — " in title:
        player, event = title.split(" — ", 1)
    else:
        player, event = title, title
    small = summary.find("small") if summary else None
    bits = [part.strip() for part in (small.get_text(" ", strip=True) if small else "").split("·")]
    placement = bits[0] if bits else ""
    date = bits[-1] if len(bits) >= 2 else ""
    copies_main = copies_side = 0
    subject_norm = norm(subject)
    for group in deck.select(".group"):
        heading = group.find(["h3", "h4", "h5"])
        side = is_side(group_label(heading))
        for row in group.select(".row"):
            if norm(row_card_name(row)) == subject_norm:
                try:
                    qty = text_qty(row.select_one(".qty"))
                except ValueError:
                    continue
                if side:
                    copies_side += qty
                else:
                    copies_main += qty
    kind = deck_kind(deck)
    significant = kind == "tournament-registration" and (
        bool(TOP_PLACEMENT_RE.search(placement)) or bool(SIGNIFICANT_EVENT_RE.search(event))
    ) and (copies_main + copies_side > 0)
    return DeckFact(player, event, placement, date, copies_main, copies_side, significant, kind)


def repair_deck(fragment: str, subject: str, file_name: str, index: int) -> tuple[str, DeckAudit, DeckFact]:
    old_long = bool(LONG_NUMBER_RE.search(fragment))
    soup = BeautifulSoup(fragment, "html.parser")
    deck = soup.find("details")
    if deck is None:
        raise ValueError("could not parse details.deck")
    groups: list[tuple[str, int]] = []
    main = side = 0
    for group in deck.select(".group"):
        heading = group.find(["h3", "h4", "h5"])
        label = group_label(heading)
        total = sum(text_qty(qty) for row in group.select(".row") if (qty := row.select_one(".qty")) is not None)
        groups.append((label, total))
        if heading:
            heading.clear()
            heading.append(f"{label} · {total}")
        if is_side(label):
            side += total
        else:
            main += total

    kind = deck_kind(deck)
    deck["data-deck-kind"] = kind
    deck["data-main-count"] = str(main)
    deck["data-sideboard-count"] = str(side)

    body = deck.select_one(".deck-body")
    if body:
        paragraph = direct_first_paragraph(body)
        if paragraph:
            paragraph.string = replace_preserved_size(paragraph.get_text(" ", strip=True), kind, main, side)
    meta = deck.select_one(".deck-meta .small")
    if meta:
        meta.string = f"Main deck {main} · " + (f"Sideboard {side}" if side else "No recorded sideboard")
    pre = deck.find("pre", id=True)
    if pre:
        update_pre_text(pre, groups)

    fact = parse_fact(deck, subject)
    audit = DeckAudit(file_name, index, main, side, kind, old_long, dict(groups))
    return str(deck), audit, fact


def impact_markup(subject: str, facts: list[DeckFact]) -> str:
    significant = [f for f in facts if f.significant]
    if not significant:
        return ""
    # Put championship wins first, then other major-event appearances, without pretending the card caused the result.
    significant.sort(key=lambda f: (not bool(TOP_PLACEMENT_RE.search(f.placement)), f.date or "9999"))
    if norm(subject) == norm("Thoughtseize"):
        return (
            '<aside class="tournament-impact" data-tournament-impact="fact-checked">'
            '<b>Tournament impact.</b> Thoughtseize was a four-of in Uri Peleg’s Doran/Junk list that won the individual '
            '2007 World Championship. Contemporary coverage describes Peleg receiving the trophy and an oversized check; '
            'no reliable source located for this audit says that he also received a large Thoughtseize art print, so that '
            'anecdote is not presented as fact. '
            '<a href="https://articles.starcitygames.com/articles/feature-article-winning-worlds-part-1/">Read Peleg’s contemporary winner report</a>.'
            '</aside>'
        )
    clauses = []
    seen: set[tuple[str, str, str]] = set()
    for fact in significant:
        key = (fact.player, fact.event, fact.placement)
        if key in seen:
            continue
        seen.add(key)
        total = fact.copies_main + fact.copies_side
        location = "main deck" if fact.copies_side == 0 else ("sideboard" if fact.copies_main == 0 else "registered 75")
        placement = f"{fact.placement} " if fact.placement else ""
        clauses.append(
            f"{html.escape(subject)} appeared as {total} cop{'y' if total == 1 else 'ies'} in "
            f"{html.escape(fact.player)}’s {html.escape(placement)}list at {html.escape(fact.event)}"
            f" ({html.escape(fact.date)}) in the {location}"
        )
        if len(clauses) == 3:
            break
    if not clauses:
        return ""
    return (
        '<aside class="tournament-impact" data-tournament-impact="derived-from-deck-archive">'
        '<b>Tournament impact.</b> ' + "; ".join(clauses) + '. These are documentary appearances, not a claim that the card alone caused the finishes.'
        '</aside>'
    )


def insert_or_replace_enrichment(raw: str, subject: str, facts: list[DeckFact]) -> tuple[str, bool, bool]:
    """Refresh tournament-impact text without touching the static official-deck section.

    Official product sections are rendered separately by
    tools/render_official_mtg_deck_sections.py from the committed catalogue
    snapshot. This function must never replace them with a runtime loader.
    """
    match = DECK_SECTION_RE.search(raw)
    if not match:
        return raw, False, False
    section_text = match.group(0)
    sec_soup = BeautifulSoup(section_text, "html.parser")
    sec = sec_soup.select_one("#decklists, #decks")
    if sec is None:
        return raw, False, False
    for old in sec.select(".tournament-impact"):
        old.decompose()
    h2 = sec.find("h2")
    impact = impact_markup(subject, facts)
    impact_added = bool(impact)
    if h2 and impact:
        h2.insert_after(BeautifulSoup(impact, "html.parser"))
    official_present = sec.select_one("details.official-mtg-decks") is not None
    new_section = str(sec)
    raw = raw.replace(section_text, new_section, 1)
    if 'href="preconstructed-decks.css"' not in raw and 'href="assets/preconstructed-decks.css"' not in raw:
        raw = re.sub(r"</head>", '<link href="preconstructed-decks.css" rel="stylesheet"/>\n</head>', raw, count=1, flags=re.I)
    raw = re.sub(r'\s*<script\b[^>]*src=["\'](?:assets/)?preconstructed-decks\.js["\'][^>]*>\s*</script>\s*', '\n', raw, flags=re.I)
    return raw, impact_added, official_present


def article_subject(raw: str, path: Path) -> str:
    match = re.search(r'<body\b[^>]*\bdata-article-card=(["\'])(.*?)\1', raw, re.I | re.S)
    if match:
        return html.unescape(match.group(2)).strip()
    soup = BeautifulSoup(raw, "html.parser")
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(" ", strip=True).split(":", 1)[0]
    return path.stem.split("-", 1)[-1].replace("-", " ").title()


def iter_articles(root: Path) -> Iterable[Path]:
    for path in sorted(root.glob("*.html")):
        if path.name == "index.html":
            continue
        raw = path.read_text(encoding="utf-8", errors="replace")
        if re.search(r'<details\b[^>]*class=["\'][^"\']*\bdeck\b', raw, re.I):
            yield path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Article directory")
    parser.add_argument("--check", action="store_true", help="Audit without writing")
    parser.add_argument("--skip-enriched", action="store_true", help="Skip articles already carrying canonical deck counts and the preconstructed catalogue")
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    root = args.root.resolve()
    out = (args.output_dir or (root / "deck-archive-audit")).resolve()
    out.mkdir(parents=True, exist_ok=True)

    audits: list[DeckAudit] = []
    article_rows: list[dict[str, object]] = []
    changed = 0
    failures: list[dict[str, str]] = []

    for path in iter_articles(root):
        raw = path.read_text(encoding="utf-8", errors="replace")
        if args.skip_enriched and "data-main-count=" in raw and "class=\"preconstructed-archive\"" in raw:
            continue
        subject = article_subject(raw, path)
        facts: list[DeckFact] = []
        local_audits: list[DeckAudit] = []
        deck_index = 0

        def repl(match: re.Match[str]) -> str:
            nonlocal deck_index
            opening = match.group(0).split(">", 1)[0]
            if "official-mtg-deck" in opening:
                return match.group(0)
            deck_index += 1
            try:
                new, audit, fact = repair_deck(match.group(0), subject, path.name, deck_index)
                local_audits.append(audit)
                facts.append(fact)
                return new
            except Exception as exc:  # keep the original deck if parsing fails
                failures.append({"file": path.name, "deck": str(deck_index), "error": str(exc)})
                return match.group(0)

        repaired = DETAIL_RE.sub(repl, raw)
        repaired, impact_added, precon_added = insert_or_replace_enrichment(repaired, subject, facts)
        is_changed = repaired != raw
        if is_changed:
            changed += 1
            if not args.check:
                path.write_text(repaired, encoding="utf-8")
        audits.extend(local_audits)
        article_rows.append({
            "file": path.name,
            "card": subject,
            "deck_count": len(local_audits),
            "impact_added": impact_added,
            "preconstructed_catalog_added": precon_added,
            "changed": is_changed,
        })

    payload = {
        "root": str(root),
        "mode": "check" if args.check else "write",
        "articles": len(article_rows),
        "decks": len(audits),
        "articles_changed": changed,
        "decks_with_old_long_number": sum(a.old_long_number for a in audits),
        "failures": failures,
        "article_results": article_rows,
        "deck_results": [asdict(a) for a in audits],
    }
    (out / "deck-archive-audit.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (out / "deck-archive-audit.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["file", "deck_index", "main_total", "sideboard_total", "kind", "old_long_number", "groups"])
        writer.writeheader()
        for a in audits:
            row = asdict(a)
            row["groups"] = json.dumps(row["groups"], ensure_ascii=False, sort_keys=True)
            writer.writerow(row)
    print(json.dumps({k: payload[k] for k in ["articles", "decks", "articles_changed", "decks_with_old_long_number", "failures"]}, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
