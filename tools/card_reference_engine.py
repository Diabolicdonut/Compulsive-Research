#!/usr/bin/env python3
"""Shared deterministic card-reference discovery for Compulsive Research.

The engine deliberately separates two concerns:

* the catalog says which phrases are real Magic card names;
* context rules decide when a matching phrase in prose should become a link.

Multiword exact names are safe by default. One-word names are linked when they
were explicitly supplied as an editorial hint/alias, or when they appear in a
high-confidence comma-separated Design Echo card list. This catches names such
as ``Persist`` without turning ordinary uses of ambiguous card-name words into
links.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
import html
import json
import re
from pathlib import Path
from typing import Iterable, Iterator

from bs4 import BeautifulSoup, NavigableString, Tag

APOSTROPHES = {"’": "'", "‘": "'", "`": "'", "´": "'"}
SKIP_TAGS = {"a", "pre", "code", "script", "style", "h1", "h2", "h3", "h4", "summary", "button"}
SKIP_CLASSES = {
    "card-name", "deck", "sources", "archive-link", "rank-nav", "toc",
    "chapter-number", "eyebrow", "art-caption", "printing", "oracle",
}
TITLE_CONNECTORS = {"of", "the", "into", "from", "to", "for", "in", "on", "at", "with", "without", "and"}
# These exact one-word names are too common in ordinary prose to infer without
# an explicit editorial declaration or alias. This is intentionally small;
# the list-context rule does most of the false-positive prevention.
AMBIGUOUS_SINGLE_WORDS = {
    "a", "an", "the", "balance", "charge", "memory", "opportunity", "restore",
    "forest", "island", "mountain", "plains", "swamp", "later", "none", "even",
    "five", "wrath", "lands", "workshop", "type", "eternal", "commander",
    "legacy", "vintage", "modern", "historic", "standard", "extended",
}


def normalize_apostrophes(value: str) -> str:
    for src, dst in APOSTROPHES.items():
        value = value.replace(src, dst)
    return value


def clean_name(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = re.sub(r"\s+", " ", html.unescape(str(value)).strip())
    return normalize_apostrophes(cleaned) if cleaned else None


def norm_key(value: str) -> str:
    return re.sub(r"\s+", " ", normalize_apostrophes(value).strip()).casefold()


def unique_names(values: Iterable[str]) -> list[str]:
    out: dict[str, str] = {}
    for value in values:
        cleaned = clean_name(value)
        if cleaned:
            out.setdefault(norm_key(cleaned), cleaned)
    return list(out.values())


def load_json_list_attribute(tag: Tag | None, attribute: str) -> list[str]:
    if tag is None:
        return []
    raw = tag.get(attribute)
    if not raw:
        return []
    try:
        value = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return []
    if not isinstance(value, list):
        return []
    return unique_names(x for x in value if isinstance(x, str))


def load_json_map_attribute(tag: Tag | None, attribute: str) -> dict[str, str]:
    if tag is None:
        return {}
    raw = tag.get(attribute)
    if not raw:
        return {}
    try:
        value = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return {}
    if not isinstance(value, dict):
        return {}
    out: dict[str, str] = {}
    for display, canonical in value.items():
        d, c = clean_name(display), clean_name(canonical)
        if d and c:
            out[d] = c
    return out


def ancestor_skipped(node: NavigableString) -> bool:
    parent = node.parent
    while isinstance(parent, Tag):
        if parent.name in SKIP_TAGS:
            return True
        if set(parent.get("class", [])) & SKIP_CLASSES:
            return True
        parent = parent.parent
    return False


def iter_eligible_text_nodes(section: Tag) -> Iterator[NavigableString]:
    for node in section.find_all(string=True):
        if isinstance(node, NavigableString) and node.strip() and not ancestor_skipped(node):
            yield node


@lru_cache(maxsize=128)
def _compile_matcher_cached(items: tuple[tuple[str, str], ...]) -> tuple[re.Pattern[str] | None, dict[str, str]]:
    lookup: dict[str, str] = {}
    patterns: list[tuple[int, str]] = []
    for display, canonical in items:
        d, c = clean_name(display), clean_name(canonical)
        if not d or not c or len(d) < 2:
            continue
        lookup[norm_key(d)] = c
        pattern = re.escape(d).replace("\\'", "['’]").replace("'", "['’]")
        patterns.append((len(d), pattern))
    if not patterns:
        return None, lookup
    patterns.sort(key=lambda item: (-item[0], item[1]))
    regex = re.compile(r"(?<![\w’'])((?:" + "|".join(p for _, p in patterns) + r"))(?!\w)")
    return regex, lookup


def compile_matcher(display_to_canonical: dict[str, str]) -> tuple[re.Pattern[str] | None, dict[str, str]]:
    """Compile one longest-name-first exact-case matcher, cached by map."""
    return _compile_matcher_cached(tuple(display_to_canonical.items()))


def looks_embedded_in_longer_title(text: str, start: int, end: int, display: str) -> bool:
    """Reject unsafe one-word matches inside an unknown longer card title."""
    if len(display.split()) != 1:
        return False
    before, after = text[:start], text[end:]
    # Possessive and -style endings refer to the matched name, not a longer title.
    if re.match(r"^(?:['’]s\b|-style\b)", after):
        after = ""
    if before and before[-1] in ",;:—–(\n":
        before = ""
    if after and after[0] in ",;:—–).\n":
        after = ""
    prev_match = re.search(r"([A-Za-zÀ-ÖØ-öø-ÿ'’\-]+)\s+$", before)
    next_match = re.match(r"^\s+([A-Za-zÀ-ÖØ-öø-ÿ'’\-]+)", after)
    if prev_match:
        previous = prev_match.group(1)
        # A preceding capitalized word suggests that this one-word match is
        # only the tail of an unknown longer title. Lowercase grammar words
        # such as “and”, “into”, or “the” do not by themselves make a title.
        if previous[:1].isupper():
            return True
    if next_match and next_match.group(1)[:1].isupper():
        return True
    return False


def _nearest_nonspace(text: str, index: int, direction: int) -> str:
    i = index
    while 0 <= i < len(text) and text[i].isspace():
        i += direction
    return text[i] if 0 <= i < len(text) else ""


def single_word_list_context(text: str, start: int, end: int, raw_candidates: list["CardMatch"]) -> bool:
    """Return True for a capitalized one-word name in a card-list context."""
    display = text[start:end]
    if not display[:1].isupper() or norm_key(display) in AMBIGUOUS_SINGLE_WORDS:
        return False
    left = _nearest_nonspace(text, start - 1, -1)
    right = _nearest_nonspace(text, end, 1)
    punctuated = left in {",", ";", ":", "("} or right in {",", ";", ":", ")"}
    # Require at least one other unambiguous card candidate in the same text
    # node. This recognizes “Necromancy, Persist, Unburial Rites” while not
    # treating an isolated capitalized English word as a card.
    strong_others = [
        candidate for candidate in raw_candidates
        if candidate.start != start and (
            len(candidate.display.split()) > 1 or candidate.explicit or candidate.alias
        )
    ]
    # A comma/semicolon plus another known card is the strongest signal. A
    # dense sentence containing at least two other unambiguous card titles is
    # also safe and covers prose such as “Frozen Aether and Kismet ... Back to
    # Basics ... Vorinclex”.
    return (punctuated and bool(strong_others)) or len(strong_others) >= 2


@dataclass(frozen=True)
class CardMatch:
    start: int
    end: int
    display: str
    canonical: str
    explicit: bool = False
    alias: bool = False


def raw_matches(
    text: str,
    matcher: re.Pattern[str] | None,
    lookup: dict[str, str],
    explicit_keys: set[str],
    alias_keys: set[str],
) -> list[CardMatch]:
    if matcher is None:
        return []
    result: list[CardMatch] = []
    for match in matcher.finditer(text):
        display = match.group(1)
        key = norm_key(display)
        canonical = lookup.get(key)
        if canonical:
            result.append(CardMatch(match.start(1), match.end(1), display, canonical, key in explicit_keys, key in alias_keys))
    return result


def accepted_matches(
    text: str,
    matcher: re.Pattern[str] | None,
    lookup: dict[str, str],
    subject_key: str,
    explicit_keys: set[str],
    alias_keys: set[str],
) -> list[CardMatch]:
    raw = raw_matches(text, matcher, lookup, explicit_keys, alias_keys)
    accepted: list[CardMatch] = []
    for candidate in raw:
        if norm_key(candidate.canonical) == subject_key:
            continue
        # Explicit editorial hints and aliases are allowed to resolve an
        # otherwise ambiguous one-word title. Longest-name-first matching has
        # already protected against partial links inside a known longer title.
        if candidate.alias or candidate.explicit:
            accepted.append(candidate)
            continue
        if looks_embedded_in_longer_title(text, candidate.start, candidate.end, candidate.display):
            continue
        if len(candidate.display.split()) > 1:
            accepted.append(candidate)
            continue
        if single_word_list_context(text, candidate.start, candidate.end, raw):
            accepted.append(candidate)
    return accepted


def discover_section_matches(
    section: Tag,
    display_to_canonical: dict[str, str],
    subject: str,
    explicit_names: Iterable[str] = (),
    aliases: dict[str, str] | None = None,
) -> list[tuple[NavigableString, list[CardMatch]]]:
    aliases = aliases or {}
    matcher, lookup = compile_matcher(display_to_canonical)
    explicit_keys = {norm_key(x) for x in explicit_names if clean_name(x)}
    alias_keys = {norm_key(x) for x in aliases}
    subject_key = norm_key(subject or "")
    result: list[tuple[NavigableString, list[CardMatch]]] = []
    for node in iter_eligible_text_nodes(section):
        matches = accepted_matches(str(node), matcher, lookup, subject_key, explicit_keys, alias_keys)
        if matches:
            result.append((node, matches))
    return result


def unwrap_card_spans(section: Tag) -> list[str]:
    """Unwrap existing links so the final prose is processed from scratch."""
    linked: list[str] = []
    for span in list(section.select("span.card-name")):
        canonical = clean_name(span.get("data-card"))
        if canonical:
            linked.append(canonical)
        span.unwrap()
    section.smooth()
    return linked


def link_matches(node: NavigableString, matches: list[CardMatch]) -> int:
    if not matches:
        return 0
    text = str(node)
    soup: BeautifulSoup | None = None
    parent: Tag | BeautifulSoup | None = node.parent
    while parent and parent.parent is not None:
        parent = parent.parent
    if isinstance(parent, BeautifulSoup):
        soup = parent
    if soup is None:
        return 0
    cursor = 0
    pieces: list[object] = []
    linked = 0
    for item in matches:
        if item.start < cursor:
            continue
        if item.start > cursor:
            pieces.append(NavigableString(text[cursor:item.start]))
        span = soup.new_tag("span")
        span["class"] = ["card-name"]
        span["data-card"] = item.canonical
        span["tabindex"] = "0"
        span.string = item.display
        pieces.append(span)
        cursor = item.end
        linked += 1
    if cursor < len(text):
        pieces.append(NavigableString(text[cursor:]))
    for piece in reversed(pieces):
        node.insert_after(piece)
    node.extract()
    return linked


def match_counter(matches_by_node: list[tuple[NavigableString, list[CardMatch]]]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for _, matches in matches_by_node:
        counter.update(match.canonical for match in matches)
    return counter


def clone_without_links(section: Tag) -> Tag:
    clone_soup = BeautifulSoup(str(section), "html.parser")
    clone = clone_soup.find(section.name) or clone_soup
    for span in list(clone.select("span.card-name")):
        span.unwrap()
    clone.smooth()
    return clone


def display_map_from_catalog(catalog: dict[str, str], aliases: dict[str, str]) -> dict[str, str]:
    result = {canonical: canonical for canonical in catalog.values()}
    result.update(aliases)
    return result
