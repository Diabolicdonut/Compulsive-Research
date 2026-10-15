#!/usr/bin/env python3
"""Migrate numbered Compulsive Research articles to card-specific hero media.

The migration is intentionally narrow:
- repair the one pre-401 wrong-card hero found by the audit;
- repair every generated entry 401-1000;
- preserve the frozen Eternal Dragon canonical authority;
- preserve one plain thematic heading without a visible card-name label;
- add an explicit CSS fallback lock for migrated pages.
"""
from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

from bs4 import BeautifulSoup

from hero_identity import (
    NUMBERED_RE,
    article_card,
    canonical_art_urls,
    identity_matches,
    metadata_map,
    numbered_files,
)

STYLE_TEMPLATE = """
<style id="hero-identity-contract">
/* Card-specific hero contract. Generated and validated by tools/migrate_hero_identity.py. */
.hero:before{{background-image:url("{art_url}")!important;background-position:center 28%!important}}
.art-break{{background-image:url("{art_url}")!important}}
</style>
""".strip()


def esc_attr(value: str) -> str:
    return html.escape(value, quote=True)


def canonical_hero_img(card: str, art_url: str, normal_url: str) -> str:
    return (
        f'<img class="hero-media" alt="{esc_attr(card)} artwork" loading="eager" '
        f'decoding="async" fetchpriority="high" referrerpolicy="no-referrer" '
        f'data-hero-card="{esc_attr(card)}" src="{esc_attr(art_url)}" '
        f'onerror="this.onerror=null;this.src=\'{esc_attr(normal_url)}\';">'
    )


def replace_header_tag(text: str, card: str) -> str:
    pattern = re.compile(r'<header\b([^>]*\bclass=["\'][^"\']*\bhero\b[^"\']*["\'][^>]*)>', re.I)
    m = pattern.search(text)
    if not m:
        return text
    tag = m.group(0)
    tag = re.sub(r'\sdata-hero-card=["\'][^"\']*["\']', '', tag, flags=re.I)
    tag = tag[:-1] + f' data-hero-card="{esc_attr(card)}">'
    return text[:m.start()] + tag + text[m.end():]


def migrate_file(path: Path, card: str, *, generated: bool, force: bool = False) -> tuple[bool, list[str]]:
    text = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(text, "html.parser")
    art_url, normal_url = canonical_art_urls(soup, card)
    changes: list[str] = []

    hero = soup.select_one("header.hero")
    if not hero:
        return False, ["missing header.hero"]
    hero_img = hero.select_one("img.hero-media")
    needs_img = force or generated or not hero_img or not identity_matches(hero_img.get("src") if hero_img else None, art_url, card)

    if needs_img:
        img_html = canonical_hero_img(card, art_url, normal_url)
        if hero_img:
            # Replace the exact serialized tag within the original text.
            tag_pattern = re.compile(r'<img\b(?=[^>]*\bclass=["\'][^"\']*\bhero-media\b[^"\']*["\'])[^>]*>', re.I)
            text, count = tag_pattern.subn(img_html, text, count=1)
            if not count:
                raise RuntimeError(f"Could not replace hero image in {path.name}")
        else:
            header_pattern = re.compile(r'(<header\b[^>]*\bclass=["\'][^"\']*\bhero\b[^"\']*["\'][^>]*>)', re.I)
            text, count = header_pattern.subn(r'\1' + img_html, text, count=1)
            if not count:
                raise RuntimeError(f"Could not insert hero image in {path.name}")
        changes.append("hero-media")

    text = replace_header_tag(text, card)

    if generated:
        header_match = re.search(r'(<header\b[^>]*\bclass=["\'][^"\']*\bhero\b[^"\']*["\'][^>]*>)(.*?)(</header>)', text, re.I | re.S)
        if not header_match:
            raise RuntimeError(f"Could not locate hero header in {path.name}")
        inner = header_match.group(2)
        h1_match = re.search(r'<h1(?:\s[^>]*)?>(.*?)</h1>', inner, re.I | re.S)
        if not h1_match:
            raise RuntimeError(f"Could not locate hero h1 in {path.name}")
        old_inner = h1_match.group(1)
        # Remove a previous migration wrapper before rebuilding.
        old_soup = BeautifulSoup(old_inner, "html.parser")
        old_title_node = old_soup.select_one(".hero-title")
        editorial_title = old_title_node.get_text(" ", strip=True) if old_title_node else old_soup.get_text(" ", strip=True)
        if editorial_title.startswith(card + ":"):
            editorial_title = editorial_title[len(card) + 1:].strip()
        new_h1 = f'<h1 data-headline-card="{esc_attr(card)}">{html.escape(editorial_title)}</h1>'
        new_inner_header = inner[:h1_match.start()] + new_h1 + inner[h1_match.end():]
        text = text[:header_match.start(2)] + new_inner_header + text[header_match.end(2):]
        changes.append("hero-heading")

    style = STYLE_TEMPLATE.format(art_url=art_url)
    style_pattern = re.compile(r'<style[^>]*id=["\']hero-identity-contract["\'][^>]*>.*?</style>', re.I | re.S)
    if style_pattern.search(text):
        text = style_pattern.sub(style, text, count=1)
    else:
        text = text.replace("</head>", style + "\n</head>", 1)
    changes.append("css-fallback-lock")

    path.write_text(text, encoding="utf-8")
    return True, changes


def patch_generator(root: Path) -> bool:
    """Confirm the generator uses card-specific media and a plain thematic H1.

    The current generator is maintained directly; this migration helper refuses to
    reintroduce the retired visible card-name wrappers.
    """
    path = root / "tools" / "generate_remaining_entries.py"
    text = path.read_text(encoding="utf-8")
    required = [
        "hero_header['data-hero-card']",
        "hero_media['src'] = art_url",
        "from headline_identity import editorial_headline",
        "h1.string = title",
    ]
    missing = [token for token in required if token not in text]
    forbidden = [token for token in ["hero-card-name", "card_name_span", "editorial_span"] if token in text]
    if missing or forbidden:
        raise RuntimeError(
            f"Generator hero contract is stale; missing={missing}, forbidden={forbidden}. "
            "Update tools/generate_remaining_entries.py directly."
        )
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true", help="Report pages that would change without writing.")
    args = parser.parse_args()
    root = args.root.resolve()
    known = metadata_map(root)
    targets: list[tuple[Path, str, bool]] = []
    for path in numbered_files(root):
        entry = int(NUMBERED_RE.match(path.name).group(1))
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        card = article_card(path, soup, known)
        generated = entry >= 401
        if generated or entry == 16:
            targets.append((path, card, generated))

    if args.check:
        print(f"Hero migration target count: {len(targets)}")
        return 0

    changed = 0
    for path, card, generated in targets:
        did_change, _ = migrate_file(path, card, generated=generated, force=(int(NUMBERED_RE.match(path.name).group(1)) == 16))
        changed += int(did_change)
    generator_changed = patch_generator(root)
    print(f"Migrated {changed} numbered article(s).")
    print(f"Generator template updated: {'yes' if generator_changed else 'already current'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
