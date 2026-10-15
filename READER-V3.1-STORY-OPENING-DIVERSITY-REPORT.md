# Reader V3.1 Story-Opening Diversity Update

## Problem corrected

The first ten table stories repeatedly began with “I remember,” “I still remember,” or equivalent recollection cues. This made individually specific scenes sound mechanically generated.

## Changes

- Rewrote the opening sentences and, where needed, the surrounding rhythm of entries 001–010.
- Preserved first-person voice, one-opponent framing, exact historical card sequencing, and raw endings.
- Added hidden `data-vignette-opening` modes to all ten pilot stories.
- Removed the validator requirement for an explicit recollection marker.
- Added wave-level checks for repeated six-word opening prefixes.
- Limited stock memory-cue openings to one per 50-entry production wave.
- Added opening-mode rotation guidance to the schemas, templates, generation prompt, reader policy, handoff, and continuation prompt.

## Pilot opening modes

1. Black Lotus — opponent before first turn
2. Ancestral Recall — board state
3. Time Walk — life total
4. Mox Pearl — table dialogue
5. Mox Sapphire — sudden threat
6. Mox Jet — revealed information
7. Mox Ruby — opening hand
8. Mox Emerald — counterintuitive play
9. Timetwister — battlefield asymmetry
10. Sol Ring — opponent curve

## Validation

- Reader Experience V3: 10/10 PASS
- Quick suite: PASS
- Full bounded release suite: PASS
- Corpus fingerprint: `16ea321df68eb064dcb446959f0c2c009c0cc36201b83bdd805032c325ff2621`
