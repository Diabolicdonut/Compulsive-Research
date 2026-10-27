# Compulsive Research — Magic: The Gathering card-history archive

> **Current approved project-wide roadmap (2026-10-27):** [Full active-archive/Reader V3.1 delivery scope and evidence](ROADMAP-COVERAGE.md) tracks **51/100 accepted weighted points (51%)**, independently of the narrower **60/100 opening Reader V3.1 article checkpoint**. The next authorized content remains article 061 Maze of Ith; source and protected 1,505-article archive remain unchanged.


An editorial archive of 1,000 numbered Magic cards and 505 active Honorable Mentions across 22 categories. The site entry point is `index.html`.

> **Recovery completed (October 15, 2026):** The accepted September 24 Reader V3.1 project has been restored to this repository and validated. Read `CURRENT-STATE.json`, `audit.md`, and `audit/github-migration/REPORT.md` before continuing. Newer validated GitHub commits take precedence over older ZIP snapshots.

The latest Reader V3.1 editorial checkpoint is **051–060**. It preserves the first 50 articles and all 505 Honorable Mentions, adds ten individually grounded table stories, and corrects rules, chronology, and deck provenance in the ten features. See `audit/reader-v31-051-060/REPORT.md`, the migration ledger, and the new review index. The exact next article is **061 — Maze of Ith**, beginning the 061–070 checkpoint. A checkpoint becomes accepted when its reviewed PR reaches `main` with passing Actions; an unmerged branch is a candidate.

## Authoritative project checkpoint

The recovery source is `Compulsive-Research-Reader-V3.1-Audit-Checkpoint-01-2026-09-24.zip` (September 24, 2026). Its complete source tree is now checked in: the 1,505-article site, editorial contracts, testing scripts, research, audit reports, and corrected historical articles. The ZIP is retained externally as a recovery source; it is not duplicated in Git.

Future Work sessions should start from current GitHub `main`, inspect the state and audit, and preserve newer validated commits. See `AGENTS.md` for safeguards.

## Long-term roadmap and live progress

[`ROADMAP-COVERAGE.md`](ROADMAP-COVERAGE.md) is the governing project development roadmap. It covers the preserved full archive, future Reader V3.1 modernization through the remaining 900 numbered articles and 505 Honorable Mentions, historical fact-checking, deck provenance, artwork/rights/accessibility, site experience and full release acceptance. Milestone acceptance conditions and evidence are defined there; no future worker should substitute an old one-wave handoff for this scope.

The landing page displays an expandable read-only **Rev / Roadmap** indicator. Its structured source is `site-progress.json`; `site-progress.js` calculates the weighted overall percentage and separately reports progress on the initial Reader 001–100 phase. The current published baseline is **51/100 accepted roadmap points** and **60/100 initial Reader features**. Overall weighted progress intentionally stays unchanged while a gate is partial; a passing structural suite is not evidence every historical claim has been individually verified.

Every accepted milestone or scope change must review and update the roadmap, audit/checkpoint and the published status together. Run `python tools/validate_site_progress.py` to verify the roadmap gate table, published manifest, accepted Reader checkpoint and site mount agree; GitHub Actions runs this same check before archive/browser validation.

## Publishing architecture

- Numbered pages: `001-*.html` through `1000-*.html`, exactly 1,000 files.
- Active Honorable Mentions: `honorable-<card-slug>.html`, exactly 505 files.
- Retired `honorable-001-*.html` through `honorable-180-*.html` pages are not canonical and must not be reintroduced.
- Landing page: `index.html`.
- Structural benchmark: `250-eternal-dragon.html`.

The recovery passed the 10-check quick suite, nine archive-refresh stages, and all 11 full release checks. The navigation validator also checks every local link and manifest-derived previous/next/return target. Browser checks run in GitHub Actions at desktop and mobile widths. Existing deck-evidence and legacy migration warnings remain separate review queues.

## GitHub Work sessions

Use the connected GitHub repository `Diabolicdonut/Compulsive-Research`. Read the verified checkpoint's `CURRENT-STATE.json`, `audit.md`, editorial contracts, and validation scripts before making changes. Commit small, validated batches to a branch and open a pull request; merge to `main` only after confirming the intended deployed state.
