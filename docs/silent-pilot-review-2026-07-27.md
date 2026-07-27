# Silent pilot review — the act-1 regression, explained (2026-07-27)

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

## 2. (a) The A3 weights: a dead lever, now measured

The runner flies real_silent on the GENERIC pilot; the `silent` weights
block has never touched an anchor number. Forcing the A/B (1000 runs,
same seeds): generic 24.2%, silent-weights 24.5% — noise. With the full
pool drafted by the current policy, combat-play ordering moves nothing.

**PROPOSED:** A3's weights stay PLACEHOLDER and the runner keeps the
generic mapping. Tuning them now would tune a lever the measurement just
showed is disconnected; the live lever is the draft scorer.
**RULING: ___**

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
**RULING: ___**

## 4. What this review leaves standing

- The completed-pool anchor reading is **22% act-1 clear** (300 runs,
  seed 11) / 24.2% (1000 runs), bare world, generic pilot — quotable now
  that the engine and scorer defects above are fixed, with A3 still
  PLACEHOLDER (D4 caveat stands for silent-pilot-derived numbers only).
- real_ironclad control: 26%, unchanged.
- The draft-scorer pass (skip/redundancy) is the named next lever, and
  the lift table above is its acceptance evidence: Survivor's and
  Neutralize's lifts should move toward zero when the scorer learns to
  say no.
