# Tier 0.5 M7 — Report (v1.9 Burst-as-kit, upgrades, CONSTANTS_VERSION 2)

> **ARCHIVED 2026-07-20 — drafter-v1 / template-v1 snapshot.** The
> m7-rulings execution (tier05-m8-report.md) superseded this world twice:
> DRAFTER_VERSION 2 (assigned adopts the power term; the §4/§7 gap story
> INVERTS — assigned now beats adaptive everywhere) and
> RUNTEMPLATE_VERSION 2 (real campfire economy; §6's natural-uptake
> numbers were measured in a 2-rest world). **Correction of record (M8
> §1): §6's dose-controlled inversion was a dose artifact** — at matched
> upgrade dose the inversion vanishes; do not cite "committed drafting
> beats goodstuff by 13–17 under scaling" from this document. Everything
> else stands as the archived v1 measurement.

**Date:** 2026-07-20. **Input:** morning-triage-rulings.md (all six rulings),
upgrade-conventions.md, klee-upgrades.yaml v0.6, sheet v0.5, principles v1.9.
160 tests green. All numbers at 1000 runs per cell unless noted;
**CONSTANTS_VERSION 2** (DRAFT_SKIP_THRESHOLD 0.5). The v1 grid is archived in
tier05-m6-report.md and is not comparable without saying so.

**Headline: every ruled re-measure landed, and the uncomfortable M6 finding
dissolved into three named causes — none of which is "the archetypes are
weak."** The assigned-vs-adaptive gap decomposes completely: deck volume
(skip threshold, fixed), truncated upgrade scaling (confirmed by inversion,
below), and the reaction scorer's weights (isolated, needs a tuning pass).

---

## 1. Burst-as-kit re-measure: reaction achievability is transformed ✓

v1.9 in one row (assigned mode, v2 constants):

| | online rate | median TTO | alarm |
|---|---|---|---|
| M6 (Burst as 1-of-15 rare, in core) | 5.3% | 7 | at the line |
| M7 (Burst as kit, core = 2 appliers + amp) | **64.3%** | **5** | **clear** |

The 5.8% = 79% × 71% × 10% decomposition predicted exactly this: the 10%
"ever saw the Burst" factor is gone because there is nothing to see — the
Burst arrives by charging. The kit grant fires in the fight engine (granted
on meter-fill, returns to kit on cast, re-grants on refill; Retain v1.4
unchanged), so every archetype now has reliable Burst access.

Divergence under the full v1.9 + v2 world is stable and healthy:
**reaction 41.5 / spark 27.9 / demolition 24.8 / goodstuff 5.8 — no
alarms**, identical across assigned targets (the adaptive-ignores-target
correctness check still holds — and was tightened this milestone: a
review-workflow pass caught rest-site smithing consulting the assigned
label in adaptive runs, fixed and regression-tested; adaptive numbers
below are post-fix).

## 2. Relevance: the ruled ≥35% floor clears everywhere ✓ — with one definitional finding

Strict advances-the-live-plan, v2 constants: **demolition 47.6 / spark 39.9
/ reaction 47.3** (adaptive: 47.0 / 40.4 / 50.3). All clear the floor.

**Finding:** the loose "worth engaging" secondary measures within noise of
the strict number everywhere (e.g. demolition 47.3 vs 47.6), not the
expected 60–75. Reason: the loose definition (strict OR an on-plan
enabler/payoff is on offer) collapses into the strict one on tagged
archetypes — the same subsumption that motivated the strict definition in
the first place. A loose number in the 60–75 band would need a genuinely
different question ("would a competent drafter take anything here" —
defense quota, raw power, companions). Reported as measured rather than
redefined until ruled; the enforced floor is unaffected.

## 3. Skip threshold: 1.0 was pessimal. Retuned to 0.5 (CONSTANTS_VERSION 2)

Sweep at 1000 runs/cell, identical seeds (full grid in the sweep artifact):

| threshold | demolition (asgn/adpt) | spark | reaction |
|---|---|---|---|
| 0.0 | 26.6 / 31.2 | 29.8 / 33.0 | 12.1 / 27.3 |
| **0.5** | **26.6 / 31.2** | **29.8 / 33.0** | **12.1 / 27.3** |
| 1.0 (v1) | 17.7 / 31.2 | 18.8 / 33.0 | 9.9 / 27.3 |
| 2.0 | 20.0 / 30.2 | 11.7 / 32.9 | **20.2** / 26.8 |

- 0.5 and 0.0 are measurement-identical (nothing scores in between), so
  0.5 is not knife-edge and keeps skip a real pick.
- At 0.5, assigned's deck size matches adaptive's (~18.3 vs ~18.6): the
  deck-volume confound is gone from every future A/B.
- **~9–11 of the "14.5-point selection gap" was the threshold**, not
  selection: assigned was passing on ~4 cards of deck volume.
- **Reaction is the deliberate exception we did not chase:** it uniquely
  prefers a high threshold (20.2% at lean 13.4-card decks, 77% online).
  Reaction wants deck density — few appliers, multiplied hard. That is a
  drafter-scorer question, not a global-constant question.

## 4. Hybrid discriminator: explanation 2 wins the residual — and hybrid beats both parents

Hybrid = assigned's archetype scorer + adaptive's raw-power term (share
synergy deliberately excluded — assigned already prices fit off its
target). Natural world, v2 + upgrades live, matched deck sizes:

| target | assigned | adaptive | hybrid |
|---|---|---|---|
| demolition | 25.0% | 28.8% | **39.3%** |
| spark | 26.9% | 30.8% | **36.6%** |
| reaction | 10.7% | 25.9% | **34.8%** |

Hybrid does not close the gap — it overshoots it by 6–10 points in all
three archetypes. Committed-plan drafting **with power awareness** is the
best drafter in the pool, which is itself evidence the archetypes pull
(consistent with divergence). The residual assigned-vs-adaptive gap on
demolition/spark (~4 pts) is the missing power term; **reaction's
residual (+15.2) is its scorer's weights** — the one place hand-set
weights are genuinely miscalibrated.

## 5. Spark decomposition: the prediction is REFUTED — the constraint is marginal supply, not engines

Predicted binding component: engine-uncommon availability. Measured
(1000 assigned-spark runs):

- Engines offered in 47.7% of runs, **drafted in 41.6%** — an 87%
  conversion rate. When the pool shows an engine, the drafter takes it.
  Engines are not the bottleneck.
- The core (≥4 on-plan) binds at the margin: P(≥3 drafted) = 69.4%,
  **P(≥4) = 43.4% = the online rate exactly.** Median on-plan drafted: 3.
- Of 566 never-online runs, 260 had exactly 3 on-plan and 198 had 2 —
  **81% of failures are one to two cards short**, not plan-less.
- Supply side: 0.46 spark on-plan offers per screen (0.269 common /
  0.150 uncommon / 0.045 rare) ≈ 6.4 expected sightings per full run,
  against competition from defense quota and the companion slot.

The decomposition picks: **fixes that add one on-plan card at the margin**
— a common-tier enabler (raises the 0.269/screen supply) or any-engine-
counts core widening (the 47.7% who see an engine mostly clear). Design
call, chat-side.

## 6. M7 upgrades: the sheet applies, and the ceiling test inverts the gap

**Mechanics.** klee-upgrades.yaml applies through a per-key dispatch
(`tier0/content/upgrades.py`); upgraded cards travel as `<id>+` so deck
lists stay strings. Unknown keys and unmatched deltas are loud errors —
the exhaustiveness test applies every sheet row. The engine grew two
sheet-driven inches (X_plus_N; copy_companion cost_override). **Three
deltas are declared UNAPPLIABLE** rather than approximated, because they
target engine constants, not card fields: catalytic_conversion's
per-reaction energy, Durin's ping, Nicole's per-turn block. DSL gap; the
rest policy refuses to burn a rest on them.

**Natural uptake is ~zero, and that is a finding about the run, not the
policy.** Runs reach 1.4 of 2 rest nodes on average and arrive under the
40% danger line at 95% of them: 0.06 smiths/run. At these tuning points
the healthy-rest smith also mildly underperforms the old basic-thinning
(−1 to −3 winrate pts) — early removal beats early upgrading here, which
is orthodox StS wisdom reproduced from first principles. **The run
template as modeled cannot deliver upgrades; the real game needs upgrade
access beyond two bruising rests** (StS1 gives ~6 campfires per act plus
events). Design-layer item.

**The controlled test (the payoff of the whole pass).** Acquisition
removed: picks arrive pre-upgraded, no rest cost.

- *Everything upgraded:* 95–99% winrate for every policy — saturation.
  A fully-upgraded deck trivializes the current encounter grid (upgrades
  are collectively worth roughly the whole compensator). No discrimination
  at the ceiling.
- *Dose-controlled — ON-PLAN picks only:*

| target | assigned | adaptive | hybrid | gap (adpt − asgn) |
|---|---|---|---|---|
| demolition | **47.4%** | 34.0% | 54.2% | **−13.4** (inverts) |
| spark | **58.2%** | 41.0% | 64.4% | **−17.2** (inverts) |
| reaction | 40.9% | 51.0% | 60.5% | +10.1 (persists) |

**When on-plan cards scale, the archetype plan beats goodstuff drafting by
13–17 points.** Explanation 3 confirmed for demolition and spark: the
pre-M7 sim graded plans in a world where the scaling that commitment buys
never arrived. (Prediction said demolition gains most; spark actually
does — reported as measured.) Reaction's gap survives even here, which
convicts its scorer weights a second, independent time.

## 7. The M6 "uncomfortable finding," fully decomposed

"Assigned loses ~20 points to having no plan at all" is now three named,
separately-measured causes:

1. **~9–11 pts: skip threshold** starved assigned of deck volume. Fixed
   (CONSTANTS_VERSION 2).
2. **~4–5 pts (demolition/spark): truncated upgrade scaling.** Confirmed
   by inversion under the dose-controlled test.
3. **Reaction's ~15 pts: scorer weights.** Survives every intervention;
   hybrid closes it. Reaction also uniquely prefers lean decks (§3).

No evidence anywhere that the archetype designs are weak — under scaling,
committed drafting is the best strategy in the pool.

---

## Asks

1. **Spark margin-supply fix** (§5): common-tier enabler vs any-engine
   core widening. Sheet-side design call.
2. **Reaction scorer retune** (§4, §6): authorize a weights pass on
   assigned-reaction (its applier/amp valuation), or adopt hybrid's power
   term into assigned mode wholesale. Sim-side; blocked on nothing.
3. **Upgrade access design** (§6): rest-smithing cannot carry upgrade
   acquisition at 2 bruising rests. Options: more rest nodes, cheaper
   smith (smith+partial heal), upgrade rewards after elites (StS1 shape),
   or event-driven Talent Training (already logged as v2 for Bursts).
4. **Loose-relevance definition** (§2): keep reporting the collapsed
   two-clause secondary, or re-spec "worth engaging" as policy-facing?
   Nothing enforced hinges on it.
5. **Sheet asks carried forward:** barbara_shining_idol exhaust-policy
   audit (upgrade sheet note); structured fields for albedo_solar_isotoma
   (`consumes_aura`) and fischl_oz (element on summon effects) so their
   reaction tags can derive honestly.
6. **C3 implication:** the mod now owes the kit-Burst grant behavior in
   C# (granted-on-charge, not draftable) — same mechanism the sim
   implements, listed for the C3 sweep.

## Tier 0 winrate bands (kit-Burst regression check)

Full character report at 1000 fights, kit grant live in every fight:
**✓ all ratified winrate bands hold, ✓ median statline passes heuristic +
identity constraints.** The watched numbers specifically:

- **demolition tank_boss 95.7%** — did NOT re-break the 97 ceiling. The
  Burst-energy-gain-rate conversation stays unopened.
- **reaction tank_boss 52.1%** (band ≥35) — up strongly, which is the kit
  Burst arriving in every fight instead of ~never, plus the deck no longer
  carrying it as a dead card pre-charge.
- **reaction gauntlet 92.6%** (band ≥75) — clear.

The reaction_weighted deck list changed with v1.9 (the Burst left it), so
its numbers are v1.9-basis; the sheet-level comparison is the band, and
the band holds.

## Not in this milestone

Slot modes beyond pity, signature-companion event, dream-team stats,
Wish-banner economy (M7-spec items still unbuilt); relic modeling beyond
the progression compensator; multi-act structure.
