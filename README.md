# Compulsive Research — Magic: The Gathering card-history archive

An editorial archive of 1,000 numbered Magic cards and 505 active Honorable Mentions across 22 categories. The site entry point is `index.html`.

> **Migration notice (October 15, 2026):** The GitHub `main` branch was last updated on August 3, 2026, and is **not** yet synchronized with the newer, validated Reader V3.1 project. Do not edit or regenerate articles from this older branch as though it were the latest editorial state.

## Authoritative project checkpoint

The most recently verified complete package is `Compulsive-Research-Reader-V3.1-Audit-Checkpoint-01-2026-09-24.zip` (September 24, 2026). Its `Compulsive-Research-main/` directory is the authoritative working source until a newer validated checkpoint replaces it. That package contains the complete 1,505-article site, editorial contracts, testing scripts, research, audit reports, and corrected historical articles. **The ZIP itself is not checked into this older branch.**

Before continuing editorial work, synchronize from the latest accepted complete package; do not overwrite newer edits with the stale website here. See `AGENTS.md` for Work-session safeguards.

## Publishing architecture

- Numbered pages: `001-*.html` through `1000-*.html`, exactly 1,000 files.
- Active Honorable Mentions: `honorable-<card-slug>.html`, exactly 505 files.
- Retired `honorable-001-*.html` through `honorable-180-*.html` pages are not canonical and must not be reintroduced.
- Landing page: `index.html`.
- Structural benchmark: `250-eternal-dragon.html`.

The September checkpoint reports a passing quick suite, 11/11 full release checks, and 54 Reader V3.1 article validations. That validation **does not apply to this older GitHub branch**.

## GitHub Work sessions

Use the connected GitHub repository `Diabolicdonut/Compulsive-Research`. Read the verified checkpoint's `CURRENT-STATE.json`, `audit.md`, editorial contracts, and validation scripts before making changes. Commit small, validated batches to a branch and open a pull request; merge to `main` only after confirming the intended deployed state.
