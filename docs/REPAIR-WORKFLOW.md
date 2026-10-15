# Controlled repair workflow

1. Preserve the current project with a Git commit or ZIP backup.
2. Sort `audit/audit-report.csv` by classification, failure count, and issue code.
3. Repair Category B pages in batches of 25–50.
4. Change only the elements named by the report. Preserve prose, research, deck selections, and article-specific visual identity unless an editorial review separately authorizes a rewrite.
5. Rebuild the manifest if `index.html`, filenames, publication status, or archive order changes.
6. Rerun the validator after every batch.
7. Compare the new audit with the previous report before committing.
8. Never convert a mechanical warning into a prose rewrite automatically.

## Recommended first repair batch

Start with archive-wide deterministic changes:

- Replace source-heading variants with the exact heading `Sources`.
- Remove duplicate or embedded `.end-nav` blocks, retaining only the canonical continue-reading navigation.
- Correct the seven landing return links reported by the validator.
- Correct the thirteen top-navigation records reported by the validator.
- Add or restore the one missing card-preview container.

Then review card-link coverage and deck totals individually. Those checks are warnings because automated repair could alter meaning or historical deck records.

- Move `.strategic-legacy-brief` to immediately after `#opening`, and reorder its TOC link accordingly.
- Reject generic or inherited Design Echo headings; pin comparison art to the intended printing.
- Render Sources as `.sources`, not `.printings`.
- Include `preconstructed-decks.css` in every distributable package and verify mobile contrast.
