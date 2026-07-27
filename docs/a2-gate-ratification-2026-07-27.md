# A2 Gate Ratification — Ruling Update (complete two-anchor data)

Date: 2026-07-27. Supersedes silent-anchor-sprint-log §6.5, whose draft was
written against a 22-card partial Silent and self-suspended pending coverage
≥ ~70%. That condition is met: Silent extracted at 85/86 (99%), and today's
excluded-pointer fixes left every number byte-identical (seventh reading).
This document was ratified by [USER] on 2026-07-27; marks at the RULING
lines.

## The complete two-anchor table (the evidence)

| anchor | cards | vocab | top% | uniq% | maxclu | neardup/card |
|---|---|---|---|---|---|---|
| OFFICIAL:ironclad | 76 | 40 | 57%* | 86% | 4 | 0.24 |
| OFFICIAL:silent (99%) | 86 | 50 | 31% | 72% | 5 | 0.36 |

\*Ironclad's top% is inflated by his generalist shape (damage on 43/76);
Silent is the themed-character read.

**Official variance is the finding:** 14 points of uniq%, one full cluster
size, and 0.12 neardup/card separate two official pools. A gate is a floor
against the official band, not a portrait of Ironclad.

## What the complete data overturns from §6.5

- §6.5's "maxclu ≤ 4 cleared by both anchors, may ratify" — **FALSE at full
  coverage:** Silent posts 5. The partial-pool ratification would have
  shipped a threshold an official character fails.
- §6.5's "neardup ≤ 0.33 cleared by both anchors" — **FALSE:** Silent posts
  0.36.
- §6.5's refusal to ratify uniq ≥ 75 — **CONFIRMED and strengthened:** the
  coverage defense is spent, and the second anchor still fails 75.

**Standing lesson, recorded:** partial-pool anchors can only loosen a
threshold's credibility, never certify it. Both §6.5 errors were
certifications from incomplete anchors.

## §6.4's concentration question — CLOSED

Complete Silent: vocab 50 (largest on the roster), top% 31% — identical to
Furina's 31%, under Klee's 36%. The vocab-9 artifact that made the partial
50% reading unsafe is gone. The most archetype-concentrated official
character concentrates exactly like our themed characters.

**RULING (proposed):** top% and vocab carry NO GATE, permanently. Themed
concentration is design, not defect; and the official idea-count edge
(40–50 vs our 21–34) is the same phenomenon uniq% enforces from the other
side — de-cloning cores raises both, and double-gating one phenomenon
invites gaming the metric. vocab/top% remain REPORT columns and pool-sweep
guidance (Furina's 26 should drift toward the mid-30s as her clone families
are broken), never pass/fail.

**RULING: RATIFIED [USER] 2026-07-27**

## The recalibrated gate (proposed for ratification)

Principle: hard thresholds sit at the official FLOOR with modest modding
headroom; the official band is printed as an advisory line so "passes the
gate" is never mistaken for "matches Ironclad."

| metric | old (PROPOSED, single-anchor) | new (two-anchor) | derivation |
|---|---|---|---|
| uniq% | ≥ 75 | ≥ 70 | official floor 72, −2 headroom |
| maxclu | ≤ 4 | ≤ 5 | official floor is 5 |
| neardup/card | ≤ 0.33 | ≤ 0.40 | official floor 0.36, +headroom |
| vocab, top%, rider%, decide% | no gate | no gate | non-divergent or ruled above |

Advisory band printed by `--gate`: uniq 72–86 · maxclu 4–5 · neardup
0.24–0.36 ("official territory").

**RULING: RATIFIED [USER] 2026-07-27**

## Where the roster lands under the recalibrated gate

| pool | uniq ≥70 | maxclu ≤5 | neardup ≤0.40/c | reading |
|---|---|---|---|---|
| klee | FAIL (61) | pass (5) | pass (0.34) | one defect: signature repetition |
| furina | FAIL (62) | pass (5) | FAIL (0.94) | the 12-family + F-B1 cluster, as felt |
| kokomi | FAIL (56) | FAIL (7) | pass\* (0.38) | the 7x block cluster |

\*0.38 at 61 cards — inside headroom, worth an eyebrow at her next pass.

This is the recalibration's real argument: the old thresholds failed
everyone on everything; the new ones point each pool at its own
characteristic defect. Klee is a de-cloning pass from clean; Furina's work
is the named families; Kokomi's is one cluster plus breadth. The uniq% gap
remains the roster-wide finding — every pool sits 8–16 points under the
official FLOOR — and is the pool-sweep pass's acceptance target.

## Rides-along (from the vocabulary audit, for the record)

- Op-difference audit: verified real, none are agent-splits (remember_card
  ≠ recall_to_draw; draw_while ≠ draw_to_hand_size by exit condition;
  block_next_turn op/power is one engine path). No action.
- copy family is at third instance (copy_companion_in_hand /
  copy_companions_played_this_combat / copy_spotlighted_in_hand) — the
  house catch→generalize trigger fires: a parameterized copy op is a
  legitimate pool-sweep design item. Backlogged, not started.
- discard_for_sparks fused-op: ratified content, noted for the record only.
- GATE_MIN_POOL invisibility fix confirmed landed (skips now print).

## On ratification, the executor applies

- Tool thresholds + docstring: two-anchor derivation, uniq marked
  two-anchor-derived (retiring the single-anchor caveat), advisory band in
  `--gate` output.
- `--gate` into the suite as a red test (pools currently failing get a
  curated known-failing list with this doc as the pointer, so the gate
  bites on NEW regressions immediately and on existing debt via the
  pool-sweep pass).
- DECISIONS entry; kickoff/principles pointer; A2 closed in the
  silent-anchor log with a forward reference here.
