# Printing gallery migration

- Articles processed: 408
- Article files changed: 0
- Existing complete static galleries retained: 2
- Legacy galleries given clean fallback and canonical hydration: 406
- Skipped/exception records: 0

## Root cause

The archive still contained one-card placeholder markup, but the inline loader that formerly replaced it had been removed during an earlier canonicalization pass. The placeholder therefore remained permanently visible.

## Permanent rule

New articles must ship with a finished static gallery. Migrated legacy articles use a clean original-printing fallback plus the queued cached runtime; visible loading and failure boxes are forbidden.


## Validation performed

- Dedicated gallery validation: 408/408 articles passed.
- Visible `.printing-status` elements: 0.
- Visible loading/failure gallery copy: 0.
- Embedded runtime and shared runtime asset: present throughout the archive.
- Browser runtime test with a mocked five-printing catalog: the legacy one-card fallback was replaced by four printing figures, the gallery reached the `ready` state, and no status box appeared.
- Full mechanical audit: A = 264, B = 144, C = 0; no new issue signatures versus the preserved baseline.
