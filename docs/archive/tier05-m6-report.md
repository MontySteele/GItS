# Tier 0.5 M6 — Report (adaptive policy, divergence, relevance, achievability)

> **ARCHIVED (CONSTANTS_VERSION 1).** All four asks below were ruled in
> docs/morning-triage-rulings.md, and every number in this report predates
> three changes that move it: companion archetype tagging (commit f885ea3),
> v1.9 Burst-as-kit, and the CONSTANTS_VERSION 2 skip-threshold retune.
> The current grid lives in **tier05-m7-report.md**. This document stays
> unedited below this banner as the archived v1 snapshot — do not compare
> its numbers against v2 numbers without saying so. Resolution map:
> finding 1 numbers → superseded by tagging fix (reaction was never
> nearly-starved); finding 2 → ruled strict ≥35% floor, clears; finding 3
> → skip threshold retuned + hybrid discriminator run; finding 4 → spark
> decomposed, reaction resolved by v1.9.

**Date:** 2026-07-20. **Input:** tier05-draft-sim-spec.md §§4–6, overnight queue.
145 tests green. All numbers at **1000 runs per policy per archetype** (the spec's
threshold for reading divergence alarms), seed 1, post-compensator.

**Headline: the goodstuff-convergence claim survives.** Divergence shows no
alarm — adaptive drafting does not collapse onto one shape. That was the last
"shipped on faith" claim awaiting a verdict, and it holds.

Three findings need rulings. One of them is uncomfortable.

---

## The confound I hit first, because it changes how to read everything below

The first divergence run said adaptive converges on **demolition in 100% of
runs**. That reads as a devastating goodstuff finding. It was my bug.

Klee's starting deck contains Jumpy Dumpty and Pop, both tagged `demolition`.
Including them put every run at demolition share 1.0 *before the first reward
screen*. The metric was reading the starting deck back to me.

Fixed by measuring commitment over drafted cards only. Rarity separates them
exactly — every starter card is `basic`, and `basic` never appears in the
draftable pool — so this is an exact filter, not a heuristic. Spec §4 asks for
commitment emerging from "what's been drafted"; the starter was not drafted.

Same class of error as the M5 payoff-gating deadlock: a policy artifact wearing
a pool finding's clothes. Regression-tested rather than commented, because a
comment would not have caught it.

**Design note worth keeping:** Klee's starter genuinely does give demolition a
head start in real play. That is intent, not noise — it just isn't evidence
about whether the pool's archetypes pull.

---

## Finding 1 — Divergence: NO ALARM. The pool's archetypes pull. ✓

| shape | share |
|---|---|
| spark | 45.2% |
| demolition | 38.8% |
| reaction | 13.2% |
| goodstuff (never committed) | 2.9% |

Dominance alarm is >55%: top shape is 45.2%, **clear**. Starvation alarm is
<10%: lowest archetype is reaction at 13.2%, **clear**.

Identical across all three assigned targets, which is the correctness check
that adaptive genuinely ignores the target rather than leaking it.

Read plainly: when a drafter with no plan just takes good cards, they still end
up somewhere specific, and all three somewheres are reachable. Goodstuff decks
are 2.9% — commitment is the norm, not the exception. **No action needed.**

## Finding 2 — Relevance misses its claimed band everywhere. Needs a ruling.

Claim was 60–70%. Measured, per assigned target:

| target | relevance |
|---|---|
| demolition | 46.6% |
| spark | 39.3% |
| reaction | 46.3% (adaptive 51.2%) |

Consistently ~15–25 points low, and low in the same direction everywhere,
which points at a definitional gap rather than a pool problem.

I defined "advances the plan" as: the offer strictly increases core progress,
**or** is an on-plan enabler/payoff the deck can still use. Deliberately *not*
"the policy took something" — a screen can be worth drafting from without
advancing the plan (defense quota, raw power), and conflating those measures
the policy instead of the pool. There is a test pinning that separation.

**The ruling I need:** was the 60–70% claim about my stricter definition, or
about the looser "was this screen worth engaging with"? Under the looser
reading the number would be substantially higher, and the honest way to settle
it is for you to say which question the acceptance grid is asking. I did not
pick the flattering definition and then report it as a pass.

## Finding 3 — The assigned policy loses to having no plan at all. Uncomfortable.

Adaptive roughly doubles assigned's winrate across every target:

| target | assigned | adaptive |
|---|---|---|
| demolition | 17.6% | 38.2% |
| spark | 19.8% | 39.5% |
| reaction | 10.8% | 36.3% |

Before reporting that as "our archetype plans are bad", I decomposed it —
adaptive also drafts 4–5 more cards, so deck size was the obvious confound.
Re-running assigned with skipping disabled, at matched deck size:

| policy | winrate | avg deck |
|---|---|---|
| assigned | 18.5% | 14.1 |
| assigned, no skip | 26.0% | 18.2 |
| adaptive | 40.5% | 18.8 |

So the gap splits in two:

- **~7.5 points is over-skipping.** `DRAFT_SKIP_THRESHOLD` is too aggressive;
  assigned passes on cards it should take. That is a tuning fix, and I have
  not made it — changing a draft constant moves every M5 number, and those are
  frozen.
- **~14.5 points is genuine card selection**, at matched deck size. The
  archetype-plan scorer picks materially worse cards than pure power+synergy.

**Three explanations, and I cannot separate them from inside the sim:**
1. The archetype plans really are weaker than goodstuff in this pool.
2. My assigned scoring weights are miscalibrated (they were hand-set in M5).
3. **Most likely, and the reason I'm not calling this a design finding:** Tier
   0.5 models no upgrades and no relics. Archetype payoffs are precisely the
   cards that scale, and this sim truncates scaling — so a plan that pays off
   late is being graded in a world where late never fully arrives. The
   progression compensator patches enemy statlines, not the player's missing
   growth curve.

Explanation 3 predicts exactly this shape of result, and it is the same gap
the M5 triage already identified as confounding. I'd want it ruled out before
anyone concludes the archetypes are weak.

## Finding 4 — Achievability: spark alarms, reaction is still the Burst problem

| target | median TTO | online rate | alarm |
|---|---|---|---|
| demolition | 4 | 90.6% | — |
| spark | **8** | 43.5% | **ALARM** (>7) |
| reaction | 7 | 5.3% | at the line |

Spark's alarm is new and readable — it is not the Burst confound, and its
43.5% online rate says the spark core assembles late and often not at all.
Worth a look on its own terms.

Reaction's 5.3% online rate remains dominated by the known constraint:
`sparks_n_splash` is one of 15 rares at 5% odds, so ~10% of runs ever *see* the
Burst its core requires. **Its achievability number stays uninterpretable until
the Burst-acquisition ruling lands** — flagged in code, not silently reported.

---

## Asks

1. **Relevance definition** (finding 2) — strict "advances the plan" or loose
   "worth engaging with"? Determines whether the 60–70% claim passed or failed.
2. **Finding 3** — do you want the no-upgrades/no-relics gap ruled out before
   the assigned-vs-adaptive result is treated as a statement about the
   archetypes? If yes, that is an M7-scope modelling question, not a tuning one.
3. **`DRAFT_SKIP_THRESHOLD`** is measurably too high (~7.5 winrate points).
   Retuning moves every frozen M5 number, so I left it alone. Say the word.
4. **Burst acquisition** — still open from the triage report, still gating
   reaction achievability. Option 1 (Burst is innate/granted) remains my
   recommendation.

## Not in this milestone
Slot modes beyond pity, signature-companion event, dream-team stats, Wish-banner
economy — all M7 per spec. The v1.8 Featured Banner plumbing landed separately
and is degenerate at the current roster by design.
