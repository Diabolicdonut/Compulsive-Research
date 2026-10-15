# Canonical Sources Contract

## Authority

The final section of `250-eternal-dragon.html` is the visual and structural authority.

## Required order

Every numbered article and Honorable Mention must end its printing/source section in this order:

```html
<div class="printings">…printing gallery…</div>
<h3>Sources</h3>
<ol class="sources">…source records…</ol>
```

Legacy source-record containers may be preserved during repair, but the visible heading and its position are not optional.

## Locked rules

- The heading is exactly `Sources`.
- It is an `h3`.
- Exactly one canonical Sources heading appears in the printing/source section.
- It follows the printing gallery.
- It immediately precedes the source-record container.
- No paragraph, editor note, status element, gallery tile, or other component appears between the heading and the source records.
- `Research Trail`, `Research sources`, and other variants are forbidden.

## Enforcement

Run:

```bash
python tools/canonicalize_sources_heading.py --check
python tools/validate_archive.py
```

The GitHub Actions workflow runs both checks for every push and pull request.

No loader, placeholder, status, failure, or explanatory component may appear between the printing gallery and `<h3>Sources</h3>`.
