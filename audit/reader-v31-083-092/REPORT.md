# Reader V3.1 articles 083–092 — ten individual candidates (October 28, 2026)

## Recovery and user editorial approval

The authoritative `main` at session start was `8696de4d7844fbc99604934c0c5f00730e84c5bd`; full archive and GitHub Pages deployment were green. The existing corpus contains exactly **1,000 numbered articles** and **505 canonical Honorable Mentions**. The formally accepted Reader checkpoint remains **051–060**, with **60/100 accepted** first-100 Reader articles and **51/100 accepted weighted roadmap points**.

The user explicitly **accepted the previous articles 073–082**. This is recorded as user editorial sign-off in `CURRENT-STATE.json`. It does not imply event-source certification or resolve the existing 061–070 formal wave blockers; those remain independently recorded in `audit/reader-v31-061-070/ACCEPTANCE-AUDIT.md`.

## Exact next ten, distinguishing archived records from invented examples

| Entry | First printing and primary identity | Actual source reference / gameplay review |
|---:|---|---|
| 083 Millstone | Antiquities (1994), Kaja Foglio | Michael Loconto — Pro Tour New York 1996; pay {2}, tap, mill top two, then understand empty-library **draw** loss rather than immediate loss. |
| 084 Ivory Tower | Antiquities, Margaret Organ-Kean | Bo Bell — Mind Twist/Rack Control; 7 hand cards at upkeep trigger give 3 life, **before** normal draw. Preserve documented 65-card original main deck rather than normalizing it. |
| 085 Zuran Orb | Ice Age (1995), Sandra Everingham | Alexander Blumke — Rack Control; sacrifice two lands before Armageddon resolves, gain four life; costs are sacrificed, not tapped. |
| 086 Hymn to Tourach | Fallen Empires (1994), **Susan Van Camp original 38a art variant** | Alexander Blumke — Rack Control; pay {B}{B}, two **random** cards from a three-card hand discarded. Other original illustrations have other credited artists. |
| 087 Order of Leitbur | Fallen Empires, Bryon Wackwitz | Tom Chanpheng — 1996 World Championship; 2/1 pays {W} for first strike plus {W}{W} for +1/+0, destroys blocking 5/3 Juggernaut in first-strike damage. |
| 088 Order of the Ebon Hand | Fallen Empires, Melissa A. Benson | Dennis Bentley — Necropotence; pay {B}+{B}{B} to beat a Kird Ape powered by Taiga's Forest type. Protection from white is a separate ability. |
| 089 Icatian Javelineers | Fallen Empires, Melissa A. Benson | Nicholas Lovett — 2006 Worlds; Javelineers controlled since previous turn taps/removes javelin counter to kill 1/1 Llanowar Elves even if answered by Shock. |
| 090 Aeolipile | Fallen Empires, Heather Hudson | George Baxter — Titania's Lock, with Aeolipile in **main deck**; {1}, {T}, sacrifice are activation costs; two damage takes out White Knight. |
| 091 Goblin Grenade | Fallen Empires **56a** original, Ron Spencer | **Explicitly authored 1994 60-card curated Goblin burn study**, no claimed historical player or result. Sacrifice Goblin **as additional spellcasting cost**; countering Grenade doesn't restore it. |
| 092 High Tide | Fallen Empires **18a** original Drew Tucker; other original variations by Anson Maddocks and Amy Weber | Federico Dato — Pro Tour Rome 1998; first Island pays to cast Tide and doesn't get retroactive bonus; after resolution Islands tap for double mana **for both players**; Turnabout untaps four Islands for eight blue afterward. |

Every new opening story is a **first-person representative gameplay reconstruction**, not a transcript or attributed eyewitness quotation. Historic deck lists supply a documentary card pool, never an invented precise match. The inherited registration records have their own provenance classification and require additional event-specific verification if not already supported.

## Files and preserved editorial contracts

- `research-dossiers/reader-v31-083-092/editorial-candidates.json` is the source-authored ten-story plan: artist, date, era, named deck reference, legal action sequence and specific review.
- `tools/prepare_reader_083_092.py --apply` creates only these ten Reader V3.1 HTML candidate edits and their individual dossier/story/review evidence; ordinary no-argument execution revalidates visible story, article hashes, sources, word counts and date/format constraints.
- `validation/reader-v3.1-083-092-candidate-metrics.json` binds article SHA-256, derived editorial word counts, 200-wpm reading estimates and per-story length.
- `research-dossiers/numbered-wave-02/083-092-*.json` contain scoped card-printing and rules evidence; `research-dossiers/reader-v31-083-092/NNN-review.json` and `NNN-story-candidate.json` hold manual action/source assessments.
- The Goblin Grenade deck meets the established 60-card, copy-buffer, group total, no-sideboard and explicitly-curated deck validators, with 1994-printed creature/spell/land pool only.

## Verified candidate metrics and full release evidence

The isolated [GitHub Actions run 40727377754](https://github.com/Diabolicdonut/Compulsive-Research/actions/runs/40727377754) **completed successfully** after generating and validating all ten Reader 083–092 candidates, applying the source-specific dossier/scene/metrics rules, confirming previous 061/062, 063–072 and 073–082 records, auditing blocked wave 061–070, checking the Reader layout contract, checking historical deck archives, refreshing V2 release fingerprints, and passing the full publication and navigation suites.

**28,216 derived editorial words**, with approximate reading time at 200 words per minute:

| # | Card | Editorial words | Read time | Scene words |
|---:|---|---:|---:|---:|
| 083 | Millstone | 2,722 | 14 min | 93 |
| 084 | Ivory Tower | 2,783 | 14 min | 95 |
| 085 | Zuran Orb | 2,834 | 15 min | 94 |
| 086 | Hymn to Tourach | 2,864 | 15 min | 101 |
| 087 | Order of Leitbur | 2,920 | 15 min | 95 |
| 088 | Order of the Ebon Hand | 2,909 | 15 min | 98 |
| 089 | Icatian Javelineers | 2,778 | 14 min | 95 |
| 090 | Aeolipile | 2,771 | 14 min | 94 |
| 091 | Goblin Grenade | 2,808 | 15 min | 100 |
| 092 | High Tide | 2,827 | 15 min | 101 |

Individual current article SHA-256 values and the exact source/deck references are in `validation/reader-v3.1-083-092-candidate-metrics.json`; ten hidden story records and ten review notes are under `research-dossiers/reader-v31-083-092`. The new Goblin Grenade 1994 deck is expressly categorized as **curated-example**, passes group/main/copy metadata, and does not pretend to be a tournament registration.

This validation **does not** accept previously blocked 061–070 documentary provenance or waive separate acceptance of the 081–090 and 091–100 checkpoints. The temporary write-enabled refresh workflow must be removed before the PR merges; the standard desktop/mobile browser CI must pass on its final head.

## Acceptance and QA

The next ten are split by formal editorial checkpoint boundary: **083–090** finish the source-scoped **081–090** candidate set; **091–092** begin **091–100**. The user's previous 073–082 editorial approval is honored, but neither this approval nor candidate source/structural validation automatically closes any wave's historical attribution blockers.

Required before merging: compile/generate the new source-bound records; run all prior Reader and archival dossier validators; verify exact 1,505 article count, historical deck totals, story and source integrity; regenerate Editorial V2 fingerprints and full archive QA; run internal navigation and desktop/mobile browser smoke; record actual metrics and run IDs only on successful completion. Remove the one-off write-enabled workflow before merge.

**Published roadmap stays 51/100 weighted; accepted Reader stays 60/100.** Next untouched entry **093 — Merchant Scroll**. Source-provenance clearance of 061–070 remains the highest-priority independent acceptance milestone.
