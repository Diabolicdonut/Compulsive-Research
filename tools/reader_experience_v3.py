#!/usr/bin/env python3
"""Shared reader-experience helpers for Compulsive Research articles.

The displayed read time is derived from editorial prose rather than raw HTML.
Expandable decklists, card galleries, source records, hidden copy buffers, scripts,
and styles are excluded because readers scan those reference components rather
than reading them as continuous prose.
"""
from __future__ import annotations

import math
import re
from bs4 import BeautifulSoup

WORDS_PER_MINUTE = 200
EXCLUDED_SELECTORS = (
    "details.deck",
    ".canonical-printing-gallery",
    "ol.sources",
    "[hidden]",
    "script",
    "style",
    "button",
)
WORD_RE = re.compile(r"\b[\w’'-]+\b", re.UNICODE)


def editorial_word_count(soup: BeautifulSoup) -> int:
    """Count continuous reader-facing prose in the main article."""
    article = soup.select_one("article.article")
    if article is None:
        return 0
    clone = BeautifulSoup(str(article), "lxml")
    for selector in EXCLUDED_SELECTORS:
        for node in clone.select(selector):
            node.decompose()
    text = clone.get_text(" ", strip=True)
    return len(WORD_RE.findall(text))


def reading_time_minutes(word_count: int, words_per_minute: int = WORDS_PER_MINUTE) -> int:
    return max(1, math.ceil(word_count / words_per_minute))


def normalized_text(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.lower()))
