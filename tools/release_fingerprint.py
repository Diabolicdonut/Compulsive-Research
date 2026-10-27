#!/usr/bin/env python3
"""Deterministic fingerprint for the Editorial V2 production corpus."""
from __future__ import annotations
import hashlib
from pathlib import Path


def active_article_files(root: Path) -> list[Path]:
    numbered = list(root.glob('[0-9][0-9][0-9]-*.html')) + list(root.glob('[0-9][0-9][0-9][0-9]-*.html'))
    honorable = list(root.glob('honorable-*.html'))
    return sorted(set(numbered + honorable))


def fingerprint_files(root: Path) -> list[Path]:
    files = active_article_files(root)
    for rel in [
        'index.html',
        'archive-manifest.json',
        'data/remaining-entry-card-data.json',
        'data/editorial-status.json',
        'canonical/canonical-lock.json',
        'canonical/250-eternal-dragon.canonical.html',
        'templates/article-content.schema.json',
        'templates/honorable-article-content.schema.json',
        'templates/research-dossier-v2.schema.json',
    ]:
        path = root / rel
        if path.exists():
            files.append(path)
    return sorted(set(files), key=lambda p: p.relative_to(root).as_posix())


def corpus_sha256(root: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    files = fingerprint_files(root)
    for path in files:
        relative = path.relative_to(root).as_posix().encode('utf-8')
        content = path.read_bytes()
        # The single read-only public status mount is delivery chrome, not part
        # of the locked Editorial V2 article/index corpus. Normalize exactly
        # this HTML insertion, at exactly the body boundary, and nothing else;
        # all previous editorial markup remains hash-covered byte-for-byte.
        if relative == b'index.html':
            status_mount = b'<script defer src="./site-progress.js" data-site-progress></script>' + bytes([10])
            if content.count(status_mount) == 1 and (
                b'</script>' + status_mount + b'</body>'
            ) in content:
                content = content.replace(status_mount, b'', 1)
        digest.update(len(relative).to_bytes(4, 'big'))
        digest.update(relative)
        digest.update(len(content).to_bytes(8, 'big'))
        digest.update(content)
    return digest.hexdigest(), len(files)
