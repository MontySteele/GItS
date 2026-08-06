> **MOVED 2026-08-06 — Clear the Stage, Track R-B resumption (R121 `Q20`, MOVE-WITH-RESOLVER; charter R119, rail 1).**
> Old path: `docs/silent-pilot-review-2026-07-27.md` — new path: `docs/archive/silent-pilot-review-2026-07-27.md`.
> Verbatim move: everything below this banner is byte-identical to the
> pre-move file. Live citers repointed in the move commit; ledger and other
> frozen citations keep the old path on purpose (rail 1: ledger bytes are
> never rewritten) and resolve through the moved-path resolver table,
> `docs/registry/identifiers.md` §17. Per-file map:
> `review/stage-clear/rb-move-manifest.tsv`.

# Silent pilot review — the act-1 regression, explained (2026-07-27)

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

The SCHEDULED REVIEW from `tier0/content/pilots/archetypes.yaml` (trigger:
pool completion — FIRED). Ruled order: (b) explain the regression first,
then (a) the weights, then (c) the scorer question. Protocol throughout:
tier 0.5, seed 11, RT7/D10/P3/C4, bare loadout; 300 runs for continuity
readings, 1000 for diagnostics. Everything here is post-P0-fix (the WLP
twin-delete, sprint log §15) and post the two scorer crash fixes below.

## 0. Two latent breaks found by re-running the instrument

Nobody re-ran tier05 after pass 6 landed, so the first re-measurement of
this review found both:

1. **Malaise crashed every run that drafted it.** Its X-cost debuff carries
   the STRING "X" (`-X` for the strength half) and `_scaling_value` did raw
   arithmetic on the field. Same class of crash one term later in
   `_tempo_value` (Calculated Gamble's `discards_this_card`). Both routed
   through the scorer's own `_est` estimator, which now knows `hand_size`
   (exact at score time) and `discards_this_card` (hand minus itself);
   `"-X"` falls to 0 deliberately — a negative enemy amount is a *benefit*
   the scaling term cannot price, which is (c)'s territory, not a crash
   site. Pinned in test_si_pass6.

## 1. (b) The regression, decomposed

The recorded sequence was 46% → 31% → 39% → 35% (27 → 75 cards). Three
findings replace it:

**The instrument is stable.** real_ironclad, same protocol: 26% act-1
clear, exactly his recorded reading. Whatever moved, moved on Silent only.

**The 35% reading was inflated by the WLP bug.** The 75-card pool state
(reconstructed by subtracting the pass-6 layer), re-run on the FIXED
engine: **27%**, not 35%. The bug deleted equal-twin cards from combat —
accidental deck-thinning, and thin decks win fights. WLP entered the pool
in pass 5, so only the 35% reading is contaminated; the corrected sequence
is 46 → 31 → 39 → ~27 → **22** (completed pool, 300 runs; 24.2% at 1000).

**The remaining fall tracks the draft, and the lift table names it.**
**[TABLE SUPERSEDED — see §1a: the top two rows are a starter-removal
artifact, and the skip-all control overturns the dilution framing.]**
Per-card act-1 clear lift over 1000 runs (clear-with minus clear-without;
survivorship bias can only flatter a card, so the negative tail is the
strong signal):

| card | in decks | clear with | clear without | lift |
|---|---|---|---|---|
| si_survivor | 99.2% | 23.9% | 62.5% | **−38.6** |
| si_neutralize | 83.2% | 18.3% | 53.6% | **−35.3** |
| si_anticipate | 12.6% | 11.1% | 26.1% | −15.0 |
| si_scare | 4.9% | 10.2% | 24.9% | −14.7 |
| si_ricochet | 3.7% | 10.8% | 24.7% | −13.9 |
| si_pinpoint | 3.5% | 11.4% | 24.7% | −13.2 |
| si_echoing_slash | 3.7% | 13.5% | 24.6% | −11.1 |

The assigned draft policy takes 85–89% of screens and puts **Survivor in
99% of decks and Neutralize in 83%** — flat commons whose signatures the
scorer prices high (plain block; damage-plus-weak) and which convert no
plan. The eight decks that dodged Survivor cleared 62.5%. Meanwhile the
poison package the scorer allegedly can't see posts *positive* lifts
under the same policy (noxious_fumes +29.7, poisoned_stab +12.4,
deadly_poison +0.5): the policy drafts them anyway, and they work.

**Explanation on the record:** as coverage rose, the offer pool filled
with weak commons; a near-indiscriminate draft policy diluted every deck
with them (12 → ~18 cards by the act-1 boss); clear rate fell in
proportion. The regression was never about combat play and never about
the A3 weights — it is the draft scorer's flat-common overvaluation, plus
one engine bug flattering the 75-card reading.

## 1a. CORRECTION (same day, before the scorer pass) — the table above
## carried an estimator artifact, and the control flips one claim

Re-examined when the scorer pass took the lift table as its acceptance
evidence. Two defects in the original measurement, both mine:

**The top two rows are starters, not draft picks.** `si_survivor` and
`si_neutralize` are BASIC cards in her twelve-card starting deck, and
`roll_rewards` never offers basics — the scorer cannot say yes or no to
them. The lift script's starter guard was an every-deck intersection, so
any starter REMOVED (rest smith / shop removal) in even one run escaped
it and entered the table carrying a removal-selection confound: the
rest policy only removes when HP is healthy enough not to heal, so the
"without" cohorts are disproportionately healthy runs. Their −38.6/−35.3
"lifts" were never draft evidence. (Their removal cohorts do clear
62.5%/55.1% vs 23% — deck-thinning value, but confounded, and a REMOVAL
policy question if it is anything.)

**The skip-all control refutes net dilution.** Never-draft-anything on
the completed pool: **7.9%** act-1 clear (deck 12.2) vs the assigned
policy's **23.3%** (deck 17.3, 88.4% of screens taken; 1000 runs, seed
11, same seeds). The draft is strongly net-POSITIVE — "dilution sinking
runs" was the wrong headline. What the corrected, offerable-cards-only
lift table shows instead is a DISCRIMINATION failure, in both tails:

| drafted card | in decks | lift | | drafted card | in decks | lift |
|---|---|---|---|---|---|---|
| si_anticipate | 128 | **−16.9** | | si_leg_sweep | 121 | **+31.8** |
| si_up_my_sleeve | 49 | −15.9 | | si_assassinate | 33 | +32.3 |
| si_scare | 44 | −12.5 | | si_escape_plan | 41 | +29.1 |
| si_ricochet | 35 | −21.2 | | si_dash | 79 | +25.6 |
| si_pinpoint | 33 | −14.7 | | si_deflect | 135 | +25.3 |
| | | | | si_footwork | 94 | +23.6 |

(Observational — drafted-card cohorts still self-select — but the
per-card sign at n ≥ 100 is the actionable signal, and survivorship can
only flatter a card, so the negative tail remains the strong claim.)

**What survives of §1:** the corrected clear sequence, the WLP-bug
finding, the Ironclad control, and "the draft is the live lever." What
changes: the mechanism is not "stop taking so many cards," it is "take
the STRONG common instead of the weak one" — the same skip/redundancy
scorer work, but its acceptance evidence is the drafted-card tails
above and the act-1 clear, NOT the starter rows, which no scorer change
can move. §§2–3's rulings are unaffected: the weights A/B and the
poison-card lifts (deadly_poison +0.3 here) were never built on the
artifact rows.

## 2. (a) The A3 weights: a dead lever, now measured

The runner flies real_silent on the GENERIC pilot; the `silent` weights
block has never touched an anchor number. Forcing the A/B (1000 runs,
same seeds): generic 24.2%, silent-weights 24.5% — noise. With the full
pool drafted by the current policy, combat-play ordering moves nothing.

**PROPOSED:** A3's weights stay PLACEHOLDER and the runner keeps the
generic mapping. Tuning them now would tune a lever the measurement just
showed is disconnected; the live lever is the draft scorer.
**RULING: RATIFIED [USER] 2026-07-27** — "let's continue the policy work
before worrying about thresholds." Weights stay PLACEHOLDER; the
draft-scorer pass proceeds first. Recorded as R83.

## 3. (c) The poison term: evidence says no, for a measured reason

The scorer has no poison term, and the review expected that to cost
wins. Measured: poison cards carry neutral-to-strongly-positive lifts
under the term-blind policy (it drafts them for their riders and bodies).
A poison term would raise their pick rates from already-working levels
while doing nothing about the cards actually sinking runs.

**PROPOSED:** no poison term. The scorer work that would move the anchor
is the opposite side: stop overpaying for flat commons (a skip threshold,
or a redundancy discount against cards already in deck — the same
"thing plus some Block" phenomenon the distinctness gate measures on
pools, showing up as draft behavior). That is draft-scorer design work,
proposed as its own pass, not smuggled into this review.
**RULING: RATIFIED [USER] 2026-07-27** — no poison term; the
skip/redundancy draft-scorer pass is the authorized policy work.
Recorded as R83.

## 4. What this review leaves standing

- The completed-pool anchor reading is **22% act-1 clear** (300 runs,
  seed 11) / 24.2% (1000 runs), bare world, generic pilot — quotable now
  that the engine and scorer defects above are fixed, with A3 still
  PLACEHOLDER (D4 caveat stands for silent-pilot-derived numbers only).
- real_ironclad control: 26%, unchanged.
- The draft-scorer pass (skip/redundancy) is the named next lever.
  ACCEPTANCE EVIDENCE CORRECTED BY §1a: the starter rows cannot move
  under any scorer change (basics are never offered). The pass is
  accepted on the drafted-card tails — the negative tail (anticipate,
  up_my_sleeve, scare) shrinking, the positive tail's cards being taken
  when offered — and on act-1 clear itself, against the completed-pool
  baseline of 23.3% (1000 runs, seed 11).

## 5. The scorer pass, executed (same day) — the ratified levers measured
## weak, and the measurement named the real one

DRAFTER_VERSION 11. All levers scoped to `archetype == "generic"`, so
only the two anchors move; every house plan drafts under its own
archetype and keeps its measured numbers. Protocol: 300-run cells at
seed 11, winners confirmed at 1000 paired-seed runs on BOTH anchors,
with per-card take-when-offered as the mechanism check.

**Round 1 — the two proposed levers are weak, and one cuts backwards.**
A skip-threshold × redundancy-discount grid moved nothing outside noise
(best cell +1.3 ± 1.9 points). The mechanism check showed why: under a
raised bar the GOOD cards got skipped (deflect taken 25.6% → 13.8%,
escape_plan 24.4% → 16.3%) while the weak enablers held — because the
weak cards SCORE HIGH. Score decomposition on the starter deck:
anticipate (role: enabler) scores 6.25 with 0.00 static power; deflect
(role: glue) scores 2.83. The anchor sheets' role labels collect +3–4
points of plan bonuses that do not track generic value; a bare bar or a
twin-discount acts downstream of that misprice. The redundancy discount
additionally punishes plain block cards hardest — the measured-good
ones — and never helped in any cell (kept as a dead dial at 0.0).

**Round 2 — quiet the labels.** `GENERIC_PLAN_BONUS_MULT` scales the
role-label plan bonuses on generic anchors. Grid over mult × skip;
winner **mult 0.25, skip 1.5**, confirmed at 1000 runs:

| | baseline (1.0 / 0.5) | winner (0.25 / 1.5) |
|---|---|---|
| real_silent act-1 clear | 23.3% | **28.8%** |
| real_ironclad act-1 clear | 26.9% | **33.3%** |
| final deck (silent) | 17.3 | 17.1 |
| anticipate taken when offered | 30.6% | 5.7% |
| up_my_sleeve taken | 31.4% | 8.9% |
| scare taken | 33.1% | 12.1% |
| deflect taken | 25.6% | 46.2% |
| leg_sweep taken | 81.0% | 90.8% |
| dash taken | 51.5% | 80.5% |

Both anchors up ~5–6 points on the same seeds, and the take tails
finally align with §1a's lift tails. Zeroing the labels entirely
(mult 0.0) measured slightly worse on both anchors than the
quarter-weight prior.

**Known residual, on the record:** `_static_power` cannot see
self-powers, so with the labels quieted Footwork's take rate fell
70% → 21% against a +23.6 measured lift. A power-aware static term is
the named next lever for a future pass — not smuggled into this one.

**Status:** constants live in tier05/draft.py as DRAFTER_VERSION 11.
**RULING: RATIFIED [USER] 2026-07-27** — "the constants in the draft.py
look fine at first glance, approved" (GENERIC_PLAN_BONUS_MULT 0.25,
GENERIC_SKIP_THRESHOLD 1.5, GENERIC_REDUNDANCY_PENALTY 0.0 dead dial).
Recorded as R84, which also orders the two follow-ons: the power-aware
`_static_power` term (the Footwork residual) and a full fresh 3-act
roster recalculation once it lands — no anchor 3-act reading recorded
before that recalculation may be quoted.

## 6. The power-aware static term, executed (same day) — DRAFTER_VERSION 12

R84's second order. Two structural proxies were built into
`_static_power` and swept (16-cell grid, 300 runs/cell, seed 11, bare
1-act, serial workers; winners confirmed at 1000 paired-seed runs on
both anchors; the (0, 0) cell reproduces the v11 world at 28.0%):

**Permanent Dexterity works, and it is the whole fix.**
`STATIC_DEXTERITY_VALUE` mirrors the v4 Strength line (amount × 2.0, two
future Block gains). It helps monotonically across the grid, and the
mechanism check shows exactly the residual closing: Footwork's
take-when-offered recovered **21% → 74%** against its +23.6 measured
lift, while the v11 tails held (anticipate 5.2% taken, deflect 45.9%,
leg_sweep 90.8%). 2.0 / 3.0 / 4.0 are indistinguishable at n=1000
(29.1 / 29.4 / 29.7-at-300), so the shipped value keeps the Strength
mirror at **2.0** rather than chasing a noise peak. `temp_dexterity` is
deliberately excluded: a one-turn grant is not future scaling, and the
card that prints it (Anticipate, −16.9 lift) is the one v11 just taught
the scorer to decline.

**The flat engine credit is a measured dead dial.**
`STATIC_POWER_ENGINE_VALUE` (flat credit per otherwise-unpriced
self-power on a Power-type card) HURT at every swept value on every
dexterity level (28.0% → 25.7% by 2.25): a flat credit cannot tell
Noxious Fumes (+29.7 lift) from the junk engines it drags in at the same
price. Kept in the code at 0.0, documented, so the next pass starts from
the measurement — a discriminating engine term needs per-power evidence,
not a constant.

| | v11 (D11) | D12 (dex 2.0, engine 0.0) |
|---|---|---|
| real_silent act-1 clear (1000) | 28.8% | **29.1%** |
| real_ironclad act-1 clear (1000) | 33.3% | **33.3%** (no dexterity cards; unmoved by construction) |
| footwork taken when offered | 21.0% | **73.9%** |

The headline number barely moves — the value of this pass is the
mechanism (a +23.6-lift card is no longer systematically declined), not
the point estimate. `_static_power` is a universal term, but the only
committed cards it newly touches are ref-vocabulary
(`metallicize_like`, `accuracy_like`); no Klee/Furina/Kokomi card prints
an unpriced self-power, so house numbers do not move.

**Found by the re-run, fixed on the spot:** the pass-4 amount-grammar
widening (8712bb5, this morning) routed `_op_draw`'s missing `amount`
through `_amount()` BEFORE the `per_aura` branch could fire, so every
fight that played Elemental Ecstasy crashed. The scorer-side per_aura
test never exercised the engine path; it does now
(test_effects.py::test_per_aura_draw_needs_no_flat_amount). No number
taken today crossed it (the v11/v12 sweeps are anchor-only worlds), and
the roster table below is post-fix.

**Also found by the re-run:** the v11 session changed the scorer but
never bumped `DRAFTER_VERSION` (the stamp still read 10). Both bumps are
now recorded in tier0/constants.py; no experiment script ran in the gap,
so no published stamp mislabels its world.

## 7. The fresh 3-act roster (R84's third order) — the only quotable table

`python -m tier05.exp_roster_anchors`, widened to the FULL roster
(Kokomi's three plans and both real anchors joined the arms). One
invocation, every row from the same world:

```
cell=roster-anchors seed=11 runs=600 RT7/D12/P3/C4
route hunter, policy assigned, relics + potions, all registered acts

    character         plan     win   act-1   acts   deck  fights
         klee   demolition   7.5%  82.0%   1.16   25.2    15.3
         klee        spark   6.8%  79.5%   1.09   24.7    14.8
         klee     reaction  11.7%  85.8%   1.29   22.1    16.4
       furina        salon  17.2%  62.8%   1.13   23.8    14.2
       furina    spotlight   4.2%  68.5%   0.92   23.6    12.8
       furina      fanfare   2.8%  57.5%   0.75   21.0    11.4
       kokomi       priest   2.8%  43.3%   0.57   21.5     9.6
       kokomi    commander   2.5%  52.7%   0.69   22.5    10.9
       kokomi       assist   0.0%  34.7%   0.38   20.0     8.1
 ref_ironclad      generic  10.2%  68.0%   1.13   22.3    15.1
real_ironclad      generic   7.8%  68.0%   1.01   21.8    13.8
  real_silent      generic   2.0%  60.8%   0.76   21.4    11.8
```

Readings, not rulings:

- **Salon is still the roster's ceiling** (17.2% full-run win; the next
  plan anywhere is Klee reaction at 11.7%). The standing salon question
  (trim vs ratify) now has a D12 denominator.
- **The anchor pair spread is 10.2 / 7.8 / 2.0** (ref_IC / real_IC /
  real_silent). real_silent's 60.8% act-1 against a 2.0% full run says
  her problem is not the draft anymore — it is acts 2–3 (acts 0.76 mean).
  Note these full-run rows are a REALISTIC world (relics + potions);
  they are not comparable to the review's bare 1-act instrument numbers
  (§5–6), and the act-1 column here (60.8%) vs the bare instrument
  (29.1%) shows how much the loadout is worth.
- **Kokomi is below the roster floor on every plan**, and assist won
  ZERO of 600 runs (34.7% act-1, 0.38 mean acts). Consistent with the
  Neap Tide finding; the pre-registered lever waits on playtest three.
- The old v6-world table (salon 9.0 / klee 6.0 / ref_IC 4.6 / real_IC
  4.4) is ARCHIVE everywhere it appears; nothing in it may be quoted
  against this one — six drafter versions, the WLP twin-delete fix and
  the realistic-loadout default all moved between them.
