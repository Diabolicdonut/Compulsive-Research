#!/usr/bin/env python3
"""Validate Compulsive Research articles against the Eternal Dragon contract.

This validator is intentionally mechanical. It can detect structural drift, broken
anchors, missing components, navigation errors, malformed card-preview markup,
empty image URLs, artwork-spotlight drift, deck-copy wiring, rough deck totals, and reading-time mismatch.
It cannot prove that historical claims, quotations, or deck provenance are true.
Those require editorial and source review.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import csv
import hashlib
import json
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from bs4 import BeautifulSoup, Tag

WORD_RE = re.compile(r"\b[\w’'-]+\b", re.UNICODE)
NUMBERED_RE = re.compile(r"^(\d{3,4})-(.+)\.html$")
HONORABLE_RE = re.compile(r"^honorable-(?!\d{3}-)([a-z0-9][a-z0-9-]*)\.html$")
RETURN_LINK_TEXT = "← Back to Compulsive Research"
ARTWORK_CORE_WORDS = {
    "art", "artwork", "illustration", "image", "imagery", "composition", "scene",
    "figure", "subject", "object", "setting", "silhouette", "foreground", "background",
    "palette", "color", "colours", "light", "lighting", "shadow", "frame", "framing",
    "perspective", "horizon", "landscape", "texture", "gesture", "pose", "motion",
    "atmosphere", "mood", "field", "forms", "outline", "scale",
}
ARTWORK_BANNED_PHRASES = (
    "article uses scryfall", "catalog image", "database image", "historical starting point",
    "first strategic identity", "strategic identity", "visual identity preserved",
    "established the visual identity", "place in the game", "mechanical identity",
    "modern frame", "reinterpreted the creature for the modern frame",
    "original illustration became inseparable", "visual counterpart to the card",
)


@dataclass
class Issue:
    severity: str
    code: str
    message: str


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def hrefs(nodes: Iterable[Tag]) -> list[str]:
    return [node.get("href", "") for node in nodes if node.get("href")]


def add(issues: list[Issue], severity: str, code: str, message: str) -> None:
    issues.append(Issue(severity, code, message))


def visible_word_count(article: Tag | None) -> int:
    if not article:
        return 0
    clone = BeautifulSoup(str(article), "lxml")
    for selector in ["pre", "script", "style", ".sources", ".printings"]:
        for node in clone.select(selector):
            node.decompose()
    return len(WORD_RE.findall(clone.get_text(" ", strip=True)))


def declared_read_time(soup: BeautifulSoup) -> int | None:
    text = " ".join(node.get_text(" ", strip=True) for node in soup.select(".byline, .pill"))
    match = re.search(r"(?:approximately\s+)?(\d+)\s*(?:-|–)?\s*minute\s+read", text, re.I)
    return int(match.group(1)) if match else None


def deck_totals(deck: Tag) -> tuple[int, int]:
    main = side = 0
    for group in deck.select(".group"):
        heading = group.find(["h3", "h4", "h5"])
        label = heading.get_text(" ", strip=True).casefold() if heading else ""
        total = 0
        for row in group.select(".row"):
            qty = row.select_one(".qty")
            if not qty:
                continue
            match = re.search(r"\d+", qty.get_text(" ", strip=True))
            if match:
                total += int(match.group())
        if any(word in label for word in ["sideboard", "side board", "maybeboard"]):
            side += total
        else:
            main += total
    return main, side


def find_subject(record: dict, soup: BeautifulSoup, path: Path) -> str:
    if record.get("card"):
        return record["card"]
    body = soup.body
    if body and body.get('data-article-card'):
        return body.get('data-article-card')
    footer = soup.select_one("footer.footer")
    if footer:
        parts = [part.strip() for part in footer.get_text(" ", strip=True).split("·")]
        if len(parts) >= 4:
            return parts[-2]
        if len(parts) >= 3:
            return parts[2]
    return path.stem.split("-", 1)[-1].replace("-", " ").title()


def inspect_article(path: Path, record: dict, canonical_name: str) -> dict:
    raw = path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(raw, "lxml")
    issues: list[Issue] = []
    is_honorable = path.name.startswith("honorable-")
    subject = find_subject(record, soup, path)

    # Basic document and locked component structure.
    h1s = soup.find_all("h1")
    if len(h1s) != 1:
        add(issues, "FAIL", "H1_COUNT", f"Expected one h1; found {len(h1s)}.")
    hero = soup.select_one("header.hero")
    if not hero:
        add(issues, "FAIL", "MISSING_HERO", "Missing header.hero.")
    else:
        for selector in [".hero-grid", ".hero-inner", ".archive-link", ".eyebrow", ".deckline", ".byline"]:
            if not hero.select_one(selector):
                add(issues, "FAIL", "HERO_COMPONENT", f"Hero is missing {selector}.")

        # The visible hero return label is identical across numbered and
        # Honorable Mention articles. Its href remains article-specific and is
        # validated against the manifest in the navigation checks below.
        archive_node = hero.select_one(".archive-link")
        actual_archive_text = archive_node.get_text(" ", strip=True) if archive_node else "missing"
        if actual_archive_text != RETURN_LINK_TEXT:
            add(issues, "FAIL", "HERO_RETURN_LINK_TEXT", f"Expected '{RETURN_LINK_TEXT}'; found '{actual_archive_text}'.")

        # Numbered wave identity remains a separate manifest-derived eyebrow.
        if not is_honorable and record.get("wave"):
            wave = record["wave"]
            expected_eyebrow_text = f"Entry {int(record['entry']):03d} · Wave {int(wave['number']):02d} · {wave['title']}"
            eyebrow_node = hero.select_one(".eyebrow")
            actual_eyebrow_text = eyebrow_node.get_text(" ", strip=True) if eyebrow_node else "missing"
            if actual_eyebrow_text != expected_eyebrow_text:
                add(issues, "FAIL", "HERO_WAVE_EYEBROW", f"Expected '{expected_eyebrow_text}'; found '{actual_eyebrow_text}'.")

    article = soup.select_one("article.article")
    toc = soup.select_one("nav.toc")
    shell = soup.select_one(".article-shell")
    if not shell:
        add(issues, "FAIL", "MISSING_ARTICLE_SHELL", "Missing .article-shell.")
    if not article:
        add(issues, "FAIL", "MISSING_ARTICLE", "Missing article.article.")
    if not toc:
        add(issues, "FAIL", "MISSING_TOC", "Missing nav.toc.")

    id_values = re.findall(r"\bid\s*=\s*['\"]([^'\"]+)['\"]", raw, flags=re.I)
    duplicate_ids = sorted(value for value, count in Counter(id_values).items() if count > 1)
    if duplicate_ids:
        add(issues, "FAIL", "DUPLICATE_IDS", "Duplicate IDs: " + ", ".join(duplicate_ids[:12]))

    sections = article.find_all("section", recursive=False) if article else []
    descendant_sections = article.select("section[id]") if article else []
    if len(descendant_sections) < 6:
        add(issues, "FAIL", "SECTION_COUNT_LOW", f"Only {len(descendant_sections)} article sections were found.")
    if len(sections) != len(descendant_sections):
        add(issues, "WARN", "SECTION_NESTING", "Some article sections are not direct children of article.article.")
    section_ids = [node.get("id") for node in descendant_sections if node.get("id")]
    for node in descendant_sections:
        sid = node.get("id", "(missing)")
        if not node.select_one(":scope > .chapter-number"):
            add(issues, "WARN", "SECTION_CHAPTER", f"Section #{sid} lacks a direct .chapter-number.")
        if not node.select_one(":scope > h2"):
            add(issues, "WARN", "SECTION_H2", f"Section #{sid} lacks a direct h2.")

    if toc:
        toc_links = toc.select("a[href^='#']")
        toc_refs = [link.get("href", "")[1:] for link in toc_links]
        missing_targets = sorted(set(toc_refs) - set(section_ids))
        omitted_sections = sorted(set(section_ids) - set(toc_refs))
        if missing_targets:
            add(issues, "FAIL", "TOC_MISSING_TARGET", "TOC targets do not exist: " + ", ".join(missing_targets))
        if omitted_sections:
            add(issues, "WARN", "TOC_OMITS_SECTION", "Sections omitted from TOC: " + ", ".join(omitted_sections))
        if len(toc_refs) != len(set(toc_refs)):
            add(issues, "FAIL", "TOC_DUPLICATE_TARGET", "TOC contains duplicate fragment targets.")

    if article and not article.select_one("#opening"):
        add(issues, "FAIL", "MISSING_OPENING_ID", "Missing canonical section#opening.")

    # Canonical artwork spotlight. Eternal Dragon is the geometry and markup authority.
    spotlights = article.select(":scope > .art-break.artwork-spotlight") if article else []
    all_spotlights = soup.select(".artwork-spotlight")
    if len(all_spotlights) != 1:
        add(issues, "FAIL", "ARTWORK_SPOTLIGHT_COUNT", f"Expected exactly one artwork spotlight; found {len(all_spotlights)}.")
    elif len(spotlights) != 1:
        add(issues, "FAIL", "ARTWORK_SPOTLIGHT_PLACEMENT", "Artwork spotlight must be a direct child of article.article.")
    else:
        spotlight = spotlights[0]
        preceding_sections = [node for node in spotlight.find_previous_siblings() if getattr(node, "name", None) == "section"]
        if len(preceding_sections) != 2:
            add(issues, "FAIL", "ARTWORK_SPOTLIGHT_PLACEMENT", f"Artwork spotlight must follow the second substantive article section; found {len(preceding_sections)} preceding sections.")
        media = spotlight.select_one(":scope > .art-break-media")
        caption = spotlight.select_one(":scope > .art-caption")
        credit = caption.select_one("[data-artwork-credit]") if caption else None
        excerpt = caption.select_one(".art-caption-excerpt") if caption else None
        if not media or not (media.get("src") or "").strip():
            add(issues, "FAIL", "ARTWORK_SPOTLIGHT_IMAGE", "Artwork spotlight lacks a nonempty .art-break-media image.")
        else:
            src = media.get("src", "")
            if "version=art_crop" not in src:
                add(issues, "FAIL", "ARTWORK_SPOTLIGHT_CROP", "Artwork spotlight image must use the original-printing art_crop endpoint.")
        for attr in ["data-artwork-card", "data-artwork-set", "data-artwork-set-name", "data-artwork-artist"]:
            if not (spotlight.get(attr) or "").strip():
                add(issues, "FAIL", "ARTWORK_SPOTLIGHT_METADATA", f"Artwork spotlight lacks required static {attr} metadata.")
        if not caption:
            add(issues, "FAIL", "ARTWORK_SPOTLIGHT_CAPTION", "Artwork spotlight lacks .art-caption.")
        artist = (spotlight.get("data-artwork-artist") or "").strip()
        set_name = (spotlight.get("data-artwork-set-name") or "").strip()
        credit_text = credit.get_text(" ", strip=True) if credit else ""
        if not credit_text:
            add(issues, "FAIL", "ARTWORK_SPOTLIGHT_CREDIT", "Artwork spotlight lacks a visible artist/original-set credit.")
        elif artist and set_name:
            expected_credit = f"{artist}’s original {set_name} artwork"
            if credit_text != expected_credit:
                add(issues, "FAIL", "ARTWORK_SPOTLIGHT_CREDIT_FORMAT", f"Credit must be exactly ‘{expected_credit}’; found ‘{credit_text}’.")
        excerpt_text = excerpt.get_text(" ", strip=True) if excerpt else ""
        if len(excerpt_text) < 55:
            add(issues, "FAIL", "ARTWORK_SPOTLIGHT_EXCERPT", "Artwork spotlight excerpt must contain at least 55 characters of image-focused commentary.")
        elif any(phrase in excerpt_text.casefold() for phrase in ARTWORK_BANNED_PHRASES):
            add(issues, "FAIL", "ARTWORK_SPOTLIGHT_GENERIC", "Artwork spotlight uses prohibited strategic, publication, catalog, or identity boilerplate.")
        else:
            excerpt_words = {word.casefold() for word in WORD_RE.findall(excerpt_text)}
            if not (excerpt_words & ARTWORK_CORE_WORDS):
                add(issues, "FAIL", "ARTWORK_SPOTLIGHT_NOT_VISUAL", "Artwork spotlight excerpt must explicitly discuss visible imagery, composition, light/color, framing, motion, texture, scale, or atmosphere.")
        if artist and media:
            alt = (media.get("alt") or "").strip()
            if artist not in alt:
                add(issues, "WARN", "ARTWORK_SPOTLIGHT_ALT_ARTIST", "Artwork image alt text should include the verified artist name.")
    if "CR_CANONICAL_ARTWORK_SPOTLIGHT_START" not in raw:
        add(issues, "FAIL", "ARTWORK_SPOTLIGHT_STYLE", "Canonical artwork-spotlight CSS lock is missing.")
    if not soup.select_one('script[src="assets/artwork-spotlight.js"]'):
        add(issues, "FAIL", "ARTWORK_SPOTLIGHT_SCRIPT", "Canonical artwork-spotlight metadata script is missing.")

    # Deck system. Alternate old IDs are repairable, not rewrite-level failures.
    deck_section = article.select_one("#decklists") if article else None
    alternative_deck = article.select_one("#decks") if article else None
    if not deck_section:
        if alternative_deck:
            add(issues, "FAIL", "NONCANONICAL_DECK_ID", "Deck archive uses #decks instead of #decklists.")
            deck_section = alternative_deck
        else:
            add(issues, "FAIL", "MISSING_DECK_SECTION", "No deck archive section was found.")
    decks = soup.select("details.deck")
    if not decks:
        add(issues, "FAIL", "MISSING_DECK_COMPONENTS", "No details.deck components were found.")
    deck_summaries: list[dict] = []
    for index, deck in enumerate(decks, start=1):
        if not deck.find("summary") or not deck.select_one(".deck-body"):
            add(issues, "FAIL", "DECK_STRUCTURE", f"Deck {index} is missing summary or .deck-body.")
        button = deck.select_one("button.copy[data-target]")
        if not button:
            add(issues, "WARN", "DECK_COPY_BUTTON", f"Deck {index} lacks a canonical copy button.")
        else:
            target = button.get("data-target")
            if not soup.find(id=target):
                add(issues, "FAIL", "DECK_COPY_TARGET", f"Deck {index} copy target #{target} does not exist.")
        main_total, side_total = deck_totals(deck)
        deck_summaries.append({"index": index, "main": main_total, "sideboard": side_total})
        # Row quantities are the sole authority. Every visible/hidden total must
        # equal integer addition of those rows; concatenated quantity strings are fatal.
        if deck.get("data-main-count") != str(main_total):
            add(issues, "FAIL", "DECK_MAIN_DATA_TOTAL", f"Deck {index} data-main-count is {deck.get('data-main-count')!r}; rows sum to {main_total}.")
        if deck.get("data-sideboard-count") != str(side_total):
            add(issues, "FAIL", "DECK_SIDE_DATA_TOTAL", f"Deck {index} data-sideboard-count is {deck.get('data-sideboard-count')!r}; rows sum to {side_total}.")
        for group in deck.select(".group"):
            heading = group.find(["h3", "h4", "h5"])
            shown = heading.get_text(" ", strip=True) if heading else ""
            group_total = 0
            for row in group.select(".row"):
                qty = row.select_one(".qty")
                if not qty:
                    continue
                value = qty.get_text(" ", strip=True)
                if not re.fullmatch(r"\d+", value):
                    add(issues, "FAIL", "DECK_NONINTEGER_QUANTITY", f"Deck {index} has a non-integer quantity {value!r}.")
                    continue
                group_total += int(value)
            if heading and not re.search(rf"[·|—-]\s*{group_total}\s*$", shown):
                add(issues, "FAIL", "DECK_GROUP_TOTAL", f"Deck {index} heading {shown!r} does not match row sum {group_total}.")
        meta = deck.select_one(".deck-meta .small")
        if meta:
            meta_text = meta.get_text(" ", strip=True)
            if f"Main deck {main_total}" not in meta_text:
                add(issues, "FAIL", "DECK_META_MAIN_TOTAL", f"Deck {index} metadata does not show Main deck {main_total}.")
            if side_total and f"Sideboard {side_total}" not in meta_text:
                add(issues, "FAIL", "DECK_META_SIDE_TOTAL", f"Deck {index} metadata does not show Sideboard {side_total}.")
            if not side_total and not re.search(r"No (?:recorded )?sideboard", meta_text, re.I):
                add(issues, "FAIL", "DECK_META_NO_SIDEBOARD", f"Deck {index} has no sideboard but is not labeled that way.")
        if re.search(r"(?:Main deck|Sideboard|recorded size:)\s*\d{4,}", str(deck), re.I):
            add(issues, "FAIL", "DECK_CONCATENATED_TOTAL", f"Deck {index} contains a four-or-more digit number in a total context.")
        if main_total and main_total not in {40, 60, 61, 62, 63, 75, 99, 100}:
            add(issues, "WARN", "DECK_MAIN_TOTAL", f"Deck {index} visible main-deck total is {main_total}; verify the historical registration.")
        if side_total not in {0, 15}:
            add(issues, "WARN", "DECK_SIDE_TOTAL", f"Deck {index} visible sideboard total is {side_total}; verify the historical registration.")

    official = soup.select_one("details.preconstructed-archive.official-mtg-decks[data-card][data-official-deck-count]")
    if not official:
        add(issues, "FAIL", "MISSING_OFFICIAL_MTG_DECK_ARCHIVE", "Missing static Official Magic the Gathering deck section.")
    elif official.has_attr("open"):
        add(issues, "FAIL", "OFFICIAL_MTG_SECTION_OPEN", "Official Magic deck section must be collapsed by default.")
    if "preconstructed-decks.js" in raw:
        add(issues, "FAIL", "LEGACY_PRECONSTRUCTED_SCRIPT", "Obsolete runtime preconstructed-decks.js loader remains.")
    if raw.count("CR_OFFICIAL_MTG_DECKS_START") != 1 or raw.count("CR_OFFICIAL_MTG_DECKS_END") != 1:
        add(issues, "FAIL", "OFFICIAL_MTG_BUILD_MARKERS", "Static official-deck build markers are missing or duplicated.")

    # Printings and sources.
    printings_section = article.select_one("#printings") if article else None
    source_container = printings_section
    if not printings_section and article:
        source_container = article.select_one("#sources")
        if source_container:
            add(issues, "FAIL", "NONCANONICAL_PRINTINGS_ID", "Printings/source section uses #sources instead of #printings.")
        else:
            add(issues, "FAIL", "MISSING_PRINTINGS_SECTION", "No printings/source section was found.")
    if source_container:
        source_headings = [
            heading for heading in source_container.find_all(["h3", "h4"])
            if heading.get_text(" ", strip=True).casefold() in {"sources", "research sources", "research trail"}
        ]
        exact_source_headings = [
            heading for heading in source_headings
            if heading.name == "h3" and heading.get_text(" ", strip=True) == "Sources"
        ]
        if len(exact_source_headings) != 1 or len(source_headings) != 1:
            variants = [h.get_text(" ", strip=True) for h in source_headings]
            add(issues, "FAIL", "SOURCES_HEADING", "Printings/source section must contain exactly one <h3>Sources</h3>. Found: " + ("; ".join(variants) if variants else "no source heading"))
        sources_heading = exact_source_headings[0] if len(exact_source_headings) == 1 else None
        source_list = source_container.select_one(".sources")
        if not source_list:
            alternative_source_list = source_container.select_one(".source-list")
            if alternative_source_list and alternative_source_list.find_all("a", href=True):
                add(issues, "FAIL", "NONCANONICAL_SOURCE_LIST", "Source records use .source-list instead of the canonical .sources list.")
                source_list = alternative_source_list
            elif source_container.find_all("a", href=True):
                add(issues, "FAIL", "NONCANONICAL_SOURCE_LIST", "Source records are present but use a noncanonical container instead of .sources.")
                source_list = None
                if sources_heading:
                    candidate = sources_heading.find_next_sibling()
                    while candidate is not None:
                        if candidate.find("a", href=True) or (candidate.name == "a" and candidate.get("href")):
                            source_list = candidate
                            break
                        candidate = candidate.find_next_sibling()
                if source_list is None:
                    source_list = source_container
            else:
                add(issues, "FAIL", "MISSING_SOURCE_LIST", "No nonempty source list was found.")
        elif not source_list.find_all(["li", "a"]):
            add(issues, "FAIL", "MISSING_SOURCE_LIST", "The .sources list is empty.")

        if sources_heading and source_list:
            previous_tag = source_list.find_previous_sibling()
            if previous_tag is not sources_heading:
                add(issues, "FAIL", "SOURCES_HEADING_POSITION", "<h3>Sources</h3> must immediately precede the source-record container.")

        printing_component = source_container.select_one(".printings")
        if printing_component:
            printing_text = printing_component.get_text(" ", strip=True)
            printing_classes = printing_component.get("class", [])
            printing_figures = printing_component.select("figure.printing")
            if printing_component.select_one(".printing-status") or re.search(r"loading (?:the |at least |distinct-art|iconic)|could not load", printing_text, re.I):
                add(issues, "FAIL", "PRINTING_LOADING_COPY", "Printing gallery exposes loading/failure status copy.")
            if "canonical-printing-gallery" not in printing_classes:
                add(issues, "FAIL", "PRINTING_COMPONENT_CLASS", "Printing gallery lacks .canonical-printing-gallery.")
            if printing_component.get("data-gallery-mode") != "hydrate":
                add(issues, "FAIL", "PRINTING_MODE", "Printing gallery does not use verified hydrate mode.")
            if printing_component.get("data-gallery-max") != "12":
                add(issues, "FAIL", "PRINTING_MAX", "Printing gallery maximum is not twelve.")
            if printing_component.get("data-identity-policy") != "exact-name-and-oracle-id":
                add(issues, "FAIL", "PRINTING_IDENTITY_POLICY", "Printing gallery lacks exact name plus Oracle-ID policy.")
            if printing_component.get("data-selection-policy") != "unique-artwork-first":
                add(issues, "FAIL", "PRINTING_ART_POLICY", "Printing gallery lacks unique-artwork-first policy.")
            if not 1 <= len(printing_figures) <= 12:
                add(issues, "FAIL", "PRINTING_FIGURES", "Printing fallback must contain one to twelve figures.")
            expected_card = printing_component.get("data-card")
            if not expected_card or not printing_component.get("data-original-set"):
                add(issues, "FAIL", "PRINTING_METADATA", "Printing gallery lacks data-card or data-original-set.")
            seen_fallback_ids = set()
            fallback_oracle_ids = set()
            for printing_figure in printing_figures:
                if printing_figure.get("data-card-name") != expected_card:
                    add(issues, "FAIL", "PRINTING_CARD_IDENTITY", "A printing fallback lacks the exact article card name.")
                    break
                scryfall_id = printing_figure.get("data-scryfall-id")
                if scryfall_id:
                    if scryfall_id in seen_fallback_ids:
                        add(issues, "FAIL", "PRINTING_DUPLICATE_ID", "Printing fallback repeats a Scryfall printing ID.")
                        break
                    seen_fallback_ids.add(scryfall_id)
                oracle_id = printing_figure.get("data-oracle-id")
                if oracle_id:
                    fallback_oracle_ids.add(oracle_id)
                image = printing_figure.find("img")
                caption = printing_figure.find("figcaption")
                if not image or not image.get("src", "").strip():
                    add(issues, "FAIL", "PRINTING_IMAGE", "A printing fallback lacks an image URL.")
                    break
                if not caption or not caption.get_text(" ", strip=True):
                    add(issues, "FAIL", "PRINTING_CAPTION", "A printing fallback lacks a caption.")
                    break
            if len(fallback_oracle_ids) > 1:
                add(issues, "FAIL", "PRINTING_MIXED_ORACLE", "Printing fallback contains multiple Oracle IDs.")
            if re.search(r"include(?::|%3A)extras", raw, re.I):
                add(issues, "FAIL", "PRINTING_INCLUDE_EXTRAS", "include:extras may admit unrelated extra cards.")
            if "CR_PRINTING_GALLERY_RUNTIME_START" not in raw:
                add(issues, "FAIL", "PRINTING_RUNTIME", "Printing gallery lacks the embedded canonical runtime.")
            for token, code in [
                ("canonical.prints_search_uri", "PRINTING_SEARCH_URI"),
                ("card.oracle_id===canonical.oracle_id", "PRINTING_ORACLE_FILTER"),
                ("MAX_PRINTINGS=12", "PRINTING_MAX_RUNTIME"),
                ("unique-artwork-first", "PRINTING_ART_RUNTIME"),
            ]:
                if token not in raw:
                    add(issues, "FAIL", code, f"Printing runtime lacks required token: {token}")
        else:
            add(issues, "FAIL", "MISSING_PRINTINGS_COMPONENT", "Missing .printings component.")
        if sources_heading:
            descendants = [node for node in source_container.descendants if getattr(node, "name", None)]
            try:
                heading_index = descendants.index(sources_heading)
            except ValueError:
                heading_index = -1
            gallery_candidates = [
                node for node in source_container.select("#printing-grid, .printings")
                if node is not source_list
            ]
            if heading_index < 0 or not any(node in descendants and descendants.index(node) < heading_index for node in gallery_candidates):
                add(issues, "FAIL", "SOURCES_HEADING_ORDER", "<h3>Sources</h3> must appear after the printing gallery.")

    # Card-reference markup.
    card_refs = soup.select(".card-name")
    for index, ref in enumerate(card_refs, start=1):
        if not ref.get("data-card", "").strip():
            add(issues, "FAIL", "CARD_DATA", f"Card reference {index} lacks data-card.")
        if ref.get("tabindex") != "0":
            add(issues, "WARN", "CARD_TABINDEX", f"Card reference {index} lacks tabindex=0.")
    body_refs = []
    if article:
        for ref in article.select(".card-name"):
            if not ref.find_parent("details", class_="deck"):
                body_refs.append(ref)
    subject_links = [ref for ref in body_refs if normalize(ref.get("data-card", "")) == normalize(subject)]
    if subject_links:
        add(issues, "WARN", "SUBJECT_CARD_LINKED", f"Subject card is linked {len(subject_links)} time(s) outside decklists.")
    if visible_word_count(article) >= 2400 and len(body_refs) < 5:
        add(issues, "WARN", "LOW_CARD_LINK_COVERAGE", f"Only {len(body_refs)} card-reference links occur outside decklists; inspect for unlinked secondary card mentions.")

    # Navigation sourced from manifest.
    own_href = record.get("landing_return_href")
    archive_link = soup.select_one(".archive-link")
    if own_href and (not archive_link or archive_link.get("href") != own_href):
        actual = archive_link.get("href") if archive_link else "missing"
        add(issues, "FAIL", "LANDING_RETURN", f"Expected {own_href}; found {actual}.")

    if is_honorable:
        expected_neighbors = []
        if record.get("previous"):
            expected_neighbors.append(record["previous"]["file"])
        if record.get("next"):
            expected_neighbors.append(record["next"]["file"])
    else:
        expected_neighbors = []
        if record.get("previous"):
            expected_neighbors.append(record["previous"]["href"])
        if record.get("next"):
            expected_neighbors.append(record["next"]["href"])
    top_actual = hrefs(soup.select(".rank-nav a"))
    end_actual = hrefs(soup.select(".end-nav a"))
    if sorted(top_actual) != sorted(expected_neighbors):
        add(issues, "FAIL", "TOP_NAV", f"Expected neighbor hrefs {expected_neighbors}; found {top_actual}.")
    if sorted(end_actual) != sorted(expected_neighbors):
        add(issues, "FAIL", "END_NAV", f"Expected neighbor hrefs {expected_neighbors}; found {end_actual}.")

    if not soup.select_one("footer.footer"):
        add(issues, "FAIL", "MISSING_FOOTER", "Missing footer.footer.")
    preview = soup.select_one("#preview")
    if not preview or not preview.find("img"):
        add(issues, "FAIL", "MISSING_PREVIEW", "Missing #preview with an img child.")

    # Image URL syntax (network availability is intentionally not tested).
    bad_images = []
    for image in soup.find_all("img"):
        src = (image.get("src") or "").strip()
        if not src or src.casefold() in {"undefined", "null", "about:blank"}:
            # The canonical preview image begins empty and is populated by JS.
            if not image.find_parent(id="preview"):
                bad_images.append(image.get("alt", "(no alt)"))
    if bad_images:
        add(issues, "FAIL", "EMPTY_IMAGE_SRC", "Images with empty/invalid src: " + ", ".join(bad_images[:8]))
    if re.search(r"url\(\s*(['\"]?)\s*\1\s*\)", raw, re.I):
        add(issues, "FAIL", "EMPTY_CSS_URL", "Found an empty CSS url().")

    # Locked CSS and JavaScript capabilities. Exact hashes are recorded but not
    # required for legacy pages because article-specific art rules create variants.
    style_text = "\n".join(tag.get_text() for tag in soup.find_all("style"))
    css_href_values = hrefs(soup.find_all("link", href=True))
    external_css = any(value.endswith("assets/compulsive-research.css") or value == "assets/compulsive-research.css" for value in css_href_values)
    required_css_tokens = [".hero", ".rank-nav", ".article-shell", ".toc", ".card-name", ".deck", ".printings", "#preview"]
    if not external_css:
        missing_css = [token for token in required_css_tokens if token not in style_text]
        if missing_css:
            add(issues, "FAIL", "CSS_CAPABILITY", "Missing canonical CSS selectors: " + ", ".join(missing_css))
        if "max-width:750px" not in style_text.replace(" ", ""):
            add(issues, "WARN", "MOBILE_BREAKPOINT", "Canonical 750px mobile breakpoint was not detected.")

    script_text = "\n".join(tag.get_text() for tag in soup.find_all("script") if not tag.get("src"))
    script_srcs = [tag.get("src", "") for tag in soup.find_all("script") if tag.get("src")]
    external_js = any(value.endswith("assets/compulsive-research.js") or value == "assets/compulsive-research.js" for value in script_srcs)
    if not external_js:
        required_js_tokens = ["closest('.card-name')", "navigator.clipboard", "IntersectionObserver", "updateProgress", "matchMedia('(hover:none)')"]
        missing_js = [token for token in required_js_tokens if token not in script_text]
        if missing_js:
            add(issues, "FAIL", "JS_CAPABILITY", "Missing canonical JS behavior: " + ", ".join(missing_js))

    # Length and reading-time diagnostics.
    words = visible_word_count(article)
    estimated_minutes = max(1, round(words / 225))
    declared_minutes = declared_read_time(soup)
    if words < 1800:
        add(issues, "FAIL", "TOO_SHORT", f"Only {words} visible article words were detected.")
    if declared_minutes is None:
        add(issues, "WARN", "MISSING_READ_TIME", "No declared reading time was detected.")
    elif abs(declared_minutes - estimated_minutes) > 8:
        add(issues, "WARN", "READ_TIME_MISMATCH", f"Declared {declared_minutes} minutes; estimated about {estimated_minutes} minutes from {words} words.")

    severe_codes = {"MISSING_HERO", "MISSING_ARTICLE", "H1_COUNT", "SECTION_COUNT_LOW", "TOO_SHORT", "MISSING_DECK_COMPONENTS", "MISSING_SOURCE_LIST"}
    severe = any(issue.code in severe_codes and issue.severity == "FAIL" for issue in issues)
    actionable = any(issue.severity in {"FAIL", "WARN"} for issue in issues)
    if path.name == canonical_name and not severe:
        classification = "A"
    elif severe:
        classification = "C"
    elif actionable:
        classification = "B"
    else:
        classification = "A"

    return {
        "file": path.name,
        "kind": "honorable" if is_honorable else "numbered",
        "entry": record.get("entry") or record.get("number"),
        "card": subject,
        "classification": classification,
        "word_count": words,
        "declared_read_minutes": declared_minutes,
        "estimated_read_minutes": estimated_minutes,
        "section_count": len(descendant_sections),
        "toc_link_count": len(toc.select("a[href^='#']")) if toc else 0,
        "card_reference_count": len(card_refs),
        "body_card_reference_count": len(body_refs),
        "deck_count": len(decks),
        "deck_totals": deck_summaries,
        "source_item_count": len(source_container.select(".sources li, .source-list li, .source-list > a")) if source_container else 0,
        "uses_shared_css": external_css,
        "uses_shared_js": external_js,
        "css_sha256": hashlib.sha256(style_text.encode("utf-8")).hexdigest() if style_text else None,
        "js_sha256": hashlib.sha256(script_text.encode("utf-8")).hexdigest() if script_text else None,
        "issues": [asdict(issue) for issue in issues],
    }


def write_outputs(root: Path, results: list[dict], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    counts = Counter(result["classification"] for result in results)
    code_counts = Counter(issue["code"] for result in results for issue in result["issues"])
    severity_counts = Counter(issue["severity"] for result in results for issue in result["issues"])

    payload = {
        "schema_version": 1,
        "canonical_article": "250-eternal-dragon.html",
        "scope": "Mechanical validation only; factual accuracy and source reliability require editorial review.",
        "article_count": len(results),
        "classification_counts": dict(sorted(counts.items())),
        "severity_counts": dict(sorted(severity_counts.items())),
        "issue_code_counts": dict(code_counts.most_common()),
        "results": results,
    }
    (output_dir / "audit-report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
        "file", "kind", "entry", "card", "classification", "word_count",
        "declared_read_minutes", "estimated_read_minutes", "section_count",
        "toc_link_count", "card_reference_count", "body_card_reference_count",
        "deck_count", "source_item_count", "uses_shared_css", "uses_shared_js",
        "fail_count", "warning_count", "issue_codes", "issue_messages",
    ]
    with (output_dir / "audit-report.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            fails = [issue for issue in result["issues"] if issue["severity"] == "FAIL"]
            warnings = [issue for issue in result["issues"] if issue["severity"] == "WARN"]
            writer.writerow({
                **{key: result.get(key) for key in fieldnames if key in result},
                "fail_count": len(fails),
                "warning_count": len(warnings),
                "issue_codes": "; ".join(issue["code"] for issue in result["issues"]),
                "issue_messages": " | ".join(f"{issue['code']}: {issue['message']}" for issue in result["issues"]),
            })

    numbered = [r for r in results if r["kind"] == "numbered"]
    honorable = [r for r in results if r["kind"] == "honorable"]
    c_files = [r for r in results if r["classification"] == "C"]
    a_files = [r for r in results if r["classification"] == "A"]
    b_files = [r for r in results if r["classification"] == "B"]
    present_numbers = sorted(r["entry"] for r in numbered if isinstance(r["entry"], int))
    gaps = []
    if present_numbers:
        for number in range(min(present_numbers), max(present_numbers) + 1):
            if number not in set(present_numbers):
                gaps.append(number)

    if len(present_numbers) == 1000 and present_numbers == list(range(1, 1001)):
        numbered_scope = "The project package contains the complete numbered sequence from entry 001 through entry 1000 with no gaps."
    elif gaps:
        preview = ", ".join(str(number) for number in gaps[:20])
        suffix = "…" if len(gaps) > 20 else ""
        numbered_scope = f"The numbered sequence has {len(gaps)} gap(s): {preview}{suffix}. Gaps describe package state and are not automatically article defects."
    else:
        numbered_scope = f"The package contains {len(numbered)} numbered article(s), spanning entries {present_numbers[0] if present_numbers else '—'} through {present_numbers[-1] if present_numbers else '—'}."

    lines = [
        "# Compulsive Research archive audit",
        "",
        "## Scope",
        "",
        f"The validator inspected **{len(results)} article files**: {len(numbered)} numbered articles and {len(honorable)} honorable mentions.",
        numbered_scope,
        "",
        "This is a mechanical audit. It does not certify historical claims, quotations, deck provenance, or source reliability.",
        "",
        "## Classification",
        "",
        f"- **A — Compliant:** {len(a_files)}",
        f"- **B — Repairable:** {len(b_files)}",
        f"- **C — Rewrite required/candidate:** {len(c_files)}",
        "",
        "Category C is reserved for severe structural failure or obviously incomplete length. A factual rewrite should never be ordered solely from this validator.",
        "",
        "## Most common repair signals",
        "",
    ]
    for code, count in code_counts.most_common(15):
        lines.append(f"- `{code}` — {count} article(s)")
    lines.extend([
        "",
        "## Canonical status",
        "",
        "`250-eternal-dragon.html` is forced to Category A unless a severe structural failure is detected, because it is the frozen authority. Its exact snapshot and SHA-256 digest are stored in `canonical/`.",
        "",
        "## Shared-asset migration",
        "",
        f"- Articles already using `assets/compulsive-research.css`: {sum(r['uses_shared_css'] for r in results)}",
        f"- Articles already using `assets/compulsive-research.js`: {sum(r['uses_shared_js'] for r in results)}",
        "- Existing pages remain inline and unchanged in this freeze. Shared assets are established for future generation and controlled batch migration.",
        "",
        "## Category C candidates",
        "",
    ])
    if c_files:
        for result in c_files:
            codes = ", ".join(issue["code"] for issue in result["issues"] if issue["severity"] == "FAIL")
            lines.append(f"- `{result['file']}` — {codes}")
    else:
        lines.append("No article met the validator’s severe automatic rewrite threshold.")
    lines.extend([
        "",
        "## Files",
        "",
        "- `audit-report.csv` — sortable repair queue",
        "- `audit-report.json` — complete machine-readable findings",
        "- `representative-sample.md` — stratified 20-article mechanical sample",
        "",
        "Run the audit again with:",
        "",
        "```bash",
        "python tools/build_manifest.py",
        "python tools/validate_archive.py",
        "```",
    ])
    (output_dir / "audit-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    sample_numbers = [1, 20, 50, 75, 100, 125, 150, 175, 200, 225, 246, 250, 275, 300, 325, 350, 375, 400, 605]
    sample = []
    by_entry = {r["entry"]: r for r in numbered}
    for number in sample_numbers:
        if number in by_entry:
            sample.append(by_entry[number])
    if honorable:
        sample.append(honorable[0])
    sample_lines = [
        "# Representative 20-article mechanical sample",
        "",
        "This stratified sample spans the current archive and includes the canonical article, the out-of-sequence entry 605, and one honorable mention. It is not a factual-source review.",
        "",
        "| File | Card | Class | Words | Sections | Decks | Main findings |",
        "|---|---|:---:|---:|---:|---:|---|",
    ]
    for result in sample:
        findings = ", ".join(issue["code"] for issue in result["issues"][:6]) or "None"
        sample_lines.append(f"| `{result['file']}` | {result['card']} | {result['classification']} | {result['word_count']} | {result['section_count']} | {result['deck_count']} | {findings} |")
    (output_dir / "representative-sample.md").write_text("\n".join(sample_lines) + "\n", encoding="utf-8")


def inspect_article_task(args: tuple[Path, dict, str]) -> dict:
    path, record, canonical_name = args
    return inspect_article(path, record, canonical_name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=Path(__file__).resolve().parents[1], type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--jobs", type=int, default=1, help="Parallel article workers (default: 1).")
    args = parser.parse_args()
    root = args.root.resolve()
    output_dir = (args.output_dir or root / "audit").resolve()

    manifest = json.loads((root / "archive-manifest.json").read_text(encoding="utf-8"))
    numbered_records = {item["file"]: item for item in manifest["entries"] if item.get("file")}
    honorable_records = {item["file"]: item for item in manifest["honorable_mentions"] if item.get("file")}

    paths = sorted(
        [path for path in root.glob("*.html") if NUMBERED_RE.match(path.name) or HONORABLE_RE.match(path.name)],
        key=lambda path: (0 if NUMBERED_RE.match(path.name) else 1, path.name),
    )
    tasks = [
        (path, numbered_records.get(path.name) or honorable_records.get(path.name) or {}, manifest["canonical_article"])
        for path in paths
    ]
    if args.jobs > 1:
        with ProcessPoolExecutor(max_workers=args.jobs) as executor:
            results = list(executor.map(inspect_article_task, tasks))
    else:
        results = [inspect_article_task(task) for task in tasks]
    write_outputs(root, results, output_dir)
    counts = Counter(result["classification"] for result in results)
    print(f"Validated {len(results)} articles: " + ", ".join(f"{key}={value}" for key, value in sorted(counts.items())))
    print(f"Reports written to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
