#!/usr/bin/env python3
"""Canonicalize article hero return links and numbered wave identity.

The landing page/manifest is the single authority for each article's landing
anchor. Every article uses the same visible return-link label, while numbered
articles also use the exact manifest-derived Entry · Wave · Wave Title eyebrow.
The script changes only the hero's .archive-link and, for numbered articles,
its .eyebrow; article prose and all other components are preserved.
"""
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

RETURN_LINK_TEXT = "← Back to Compulsive Research"

HERO_RE = re.compile(
    r"(?P<open><header\b[^>]*\bclass=(?P<q>['\"])[^'\"]*\bhero\b[^'\"]*(?P=q)[^>]*>)(?P<body>.*?)(?P<close></header>)",
    re.IGNORECASE | re.DOTALL,
)
ARCHIVE_RE = re.compile(
    r"<a\b[^>]*\bclass=(?P<q>['\"])[^'\"]*\barchive-link\b[^'\"]*(?P=q)[^>]*>.*?</a>",
    re.IGNORECASE | re.DOTALL,
)
EYEBROW_RE = re.compile(
    r"<div\b[^>]*\bclass=(?P<q>['\"])[^'\"]*\beyebrow\b[^'\"]*(?P=q)[^>]*>.*?</div>",
    re.IGNORECASE | re.DOTALL,
)


def numbered_eyebrow(record: dict) -> str:
    wave = record.get("wave") or {}
    number = int(wave["number"])
    title = str(wave["title"]).strip()
    entry = int(record["entry"])
    return f"Entry {entry:03d} · Wave {number:02d} · {title}"


def replace_identity(raw: str, record: dict, *, numbered: bool) -> tuple[str, list[str]]:
    hero_match = HERO_RE.search(raw)
    if not hero_match:
        return raw, ["missing header.hero"]

    body = hero_match.group("body")
    href = record["landing_return_href"]
    archive_html = (
        f'<a class="archive-link" href="{html.escape(href, quote=True)}">'
        f'{html.escape(RETURN_LINK_TEXT, quote=False)}</a>'
    )

    problems: list[str] = []
    if not ARCHIVE_RE.search(body):
        problems.append("missing .archive-link")
    else:
        body = ARCHIVE_RE.sub(archive_html, body, count=1)

    if numbered:
        if not EYEBROW_RE.search(body):
            problems.append("missing .eyebrow")
        else:
            eyebrow_html = (
                f'<div class="eyebrow">'
                f'{html.escape(numbered_eyebrow(record), quote=False)}</div>'
            )
            body = EYEBROW_RE.sub(eyebrow_html, body, count=1)

    if problems:
        return raw, problems

    updated = (
        raw[: hero_match.start()]
        + hero_match.group("open")
        + body
        + hero_match.group("close")
        + raw[hero_match.end() :]
    )
    return updated, []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true", help="Report drift without changing files.")
    args = parser.parse_args()

    root = args.root.resolve()
    manifest = json.loads((root / "archive-manifest.json").read_text(encoding="utf-8"))
    changed: list[str] = []
    errors: list[str] = []

    records: list[tuple[dict, bool]] = []
    records.extend((record, True) for record in manifest["entries"])
    records.extend((record, False) for record in manifest["honorable_mentions"])

    for record, numbered in records:
        filename = record.get("file")
        if not filename or not record.get("article_present"):
            continue
        path = root / filename
        if not path.is_file():
            continue
        raw = path.read_text(encoding="utf-8")
        updated, problems = replace_identity(raw, record, numbered=numbered)
        if problems:
            errors.append(f"{filename}: {', '.join(problems)}")
            continue
        if updated != raw:
            changed.append(filename)
            if not args.check:
                path.write_text(updated, encoding="utf-8")

    if errors:
        print("HERO IDENTITY ERRORS")
        for item in errors:
            print(f"- {item}")
        return 1

    if args.check and changed:
        print("HERO IDENTITY DRIFT")
        for filename in changed:
            print(f"- {filename}")
        return 1

    verb = "Would update" if args.check else "Updated"
    print(f"{verb} {len(changed)} article(s).")
    if not changed:
        print("All present articles already use the canonical return link; numbered wave identity is also canonical.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
