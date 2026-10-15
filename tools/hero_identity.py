#!/usr/bin/env python3
"""Shared hero-image identity helpers for Compulsive Research."""
from __future__ import annotations

import html
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlencode, urlparse, urlunparse

from bs4 import BeautifulSoup

NUMBERED_RE = re.compile(r"^(\d{3,4})-.*\.html$")
UUID_RE = re.compile(r"/cards/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})(?:\?|$)", re.I)
SET_NUMBER_RE = re.compile(r"/cards/([^/?#]+)/([^/?#]+)(?:\?|$)", re.I)
URL_RE = re.compile(r"https://api\.scryfall\.com/cards/[^\"'\)\s;]+(?:&amp;[^\"'\)\s;]+)*", re.I)


def normalize_name(value: str) -> str:
    value = html.unescape(unquote(value or ""))
    value = unicodedata.normalize("NFKC", value)
    value = value.replace("’", "'").replace("‘", "'").replace("`", "'")
    value = value.replace("–", "-").replace("—", "-")
    value = re.sub(r"\s+", " ", value).strip().casefold()
    return value


def metadata_map(root: Path) -> dict[str, str]:
    path = root / "canonical" / "artwork-card-metadata.json"
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {row["file"]: row.get("articleCard") or row.get("name") or "" for row in payload.get("cards", [])}


def article_card(path: Path, soup: BeautifulSoup, known: dict[str, str] | None = None) -> str:
    if known and known.get(path.name):
        return known[path.name]
    body = soup.body
    if body and body.get("data-article-card"):
        return body["data-article-card"].strip()
    for img in soup.find_all("img"):
        alt = (img.get("alt") or "").strip()
        for suffix in (" card image", " from ", " artwork by "):
            if suffix in alt:
                candidate = alt.split(suffix, 1)[0].strip()
                if candidate:
                    return candidate
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    if ":" in title:
        return title.split(":", 1)[0].strip()
    if " — " in title:
        return title.split(" — ", 1)[0].strip()
    return path.stem.split("-", 1)[-1].replace("-", " ").title()


def is_scryfall_image(url: str | None) -> bool:
    return bool(url and "api.scryfall.com/cards/" in html.unescape(url))


def set_version(url: str, version: str) -> str:
    url = html.unescape(url)
    parsed = urlparse(url)
    query = parse_qs(parsed.query, keep_blank_values=True)
    query["format"] = ["image"]
    query["version"] = [version]
    clean_query = urlencode([(key, item) for key, values in query.items() for item in values])
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, clean_query, parsed.fragment))


def named_image_url(card: str, version: str) -> str:
    return f"https://api.scryfall.com/cards/named?exact={quote(card, safe='')}&format=image&version={version}"


def canonical_card_image(soup: BeautifulSoup, card: str) -> str:
    """Find an existing image URL that is demonstrably for the article card."""
    norm = normalize_name(card)
    candidates: list[tuple[int, str]] = []
    for idx, img in enumerate(soup.find_all("img")):
        if "hero-media" in (img.get("class") or []):
            continue
        src = html.unescape(img.get("src") or "")
        if not is_scryfall_image(src):
            continue
        alt = normalize_name(img.get("alt") or "")
        data_name = normalize_name(img.get("data-card-name") or "")
        parent = img.find_parent(attrs={"data-card-name": True})
        parent_name = normalize_name(parent.get("data-card-name") if parent else "")
        score = 0
        src_identity = identity(src)
        # Never trust a mislabeled image whose named endpoint identifies another card.
        if src_identity and src_identity[0] == "name" and src_identity[1] != norm:
            continue
        if src_identity and src_identity[0] == "name" and src_identity[1] == norm:
            score += 1000
        if data_name == norm or parent_name == norm:
            score += 100
        if alt == norm or alt.startswith(norm + " card image") or alt.startswith(norm + " from "):
            score += 1200
        elif alt.startswith(norm + " artwork") or alt.startswith(norm + " - ") or alt.startswith(norm + " — ") or alt.startswith(norm + ","):
            score += 800
        if "art-break-media" in (img.get("class") or []):
            score += 25
        if "version=art_crop" in src:
            score += 10
        if score:
            candidates.append((score * 10000 - idx, src))
    if candidates:
        return max(candidates)[1]
    return named_image_url(card, "normal")


def canonical_art_urls(soup: BeautifulSoup, card: str) -> tuple[str, str]:
    base = canonical_card_image(soup, card)
    return set_version(base, "art_crop"), set_version(base, "normal")


def identity(url: str | None) -> tuple[str, str] | None:
    if not url:
        return None
    decoded = html.unescape(url).strip().strip('"\'')
    parsed = urlparse(decoded)
    if "api.scryfall.com" not in parsed.netloc:
        return None
    m = UUID_RE.search(parsed.path + ("?" + parsed.query if parsed.query else ""))
    if m:
        return ("uuid", m.group(1).lower())
    m = SET_NUMBER_RE.search(parsed.path + ("?" + parsed.query if parsed.query else ""))
    if m and m.group(1).lower() not in {"named", "search", "random"}:
        return ("printing", f"{unquote(m.group(1)).casefold()}/{unquote(m.group(2)).casefold()}")
    query = parse_qs(parsed.query)
    if parsed.path.rstrip("/").endswith("/named"):
        name = (query.get("exact") or query.get("fuzzy") or [""])[0]
        return ("name", normalize_name(name))
    return ("url", re.sub(r"(?:^|&)version=[^&]*", "", parsed.query))


def identity_matches(url: str | None, expected_url: str, card: str) -> bool:
    actual = identity(url)
    expected = identity(expected_url)
    if actual and expected and actual == expected:
        return True
    if actual and actual[0] == "name" and actual[1] == normalize_name(card):
        return True
    if expected and expected[0] == "name" and expected[1] == normalize_name(card):
        # A printing-specific actual URL may still be correct; compare URL to known page sources elsewhere.
        return actual == expected
    return False


def header_css_urls(text: str, header_classes: list[str] | None = None) -> list[str]:
    """Return likely effective hero CSS URLs, strongest/most specific last."""
    urls: list[str] = []
    # CSS variable used by a group of legacy pages.
    for m in re.finditer(r"--hero-art\s*:\s*url\([\"']?([^\)\"']+)", text, re.I):
        urls.append(html.unescape(m.group(1)))
    # Generic hero selectors.
    for m in re.finditer(r"\.hero(?::before|::before)?\s*\{[^{}]*?url\([\"']?([^\)\"']+)", text, re.I | re.S):
        urls.append(html.unescape(m.group(1)))
    # Specific classes on the header win over generic selectors.
    for cls in header_classes or []:
        if cls == "hero":
            continue
        pattern = rf"\.hero\.{re.escape(cls)}(?::before|::before)?\s*\{{[^{{}}]*?url\([\"']?([^\)\"']+)"
        for m in re.finditer(pattern, text, re.I | re.S):
            urls.append(html.unescape(m.group(1)))
    # Explicit migration lock is always last/effective.
    lock = re.search(r"<style[^>]*id=[\"']hero-identity-contract[\"'][^>]*>(.*?)</style>", text, re.I | re.S)
    if lock:
        lock_urls = URL_RE.findall(html.unescape(lock.group(1)))
        urls.extend(lock_urls)
    return urls


def numbered_files(root: Path) -> list[Path]:
    files = [p for p in root.glob("*.html") if NUMBERED_RE.match(p.name)]
    return sorted(files, key=lambda p: int(NUMBERED_RE.match(p.name).group(1)))
