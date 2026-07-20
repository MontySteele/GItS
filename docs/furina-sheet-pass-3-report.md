# Furina Sheet Pass 3 — Report ("The Designation World")

**Date:** 2026-07-20. **Plan:** furina-sheet-pass-3-plan.md
(pre-registered). **Authorized:** R32 + R33 (furina-pass3-rulings.md;
renumbered from the chat draft — see that doc's collision table).
**Governing:** R16–R22, R26, R29–R33, DECISIONS 69–93.
**Environment:** CONSTANTS_VERSION 2, DRAFTER_VERSION 2,
RUNTEMPLATE_VERSION 2, A6_INSTRUMENT_VERSION 2,
**SPOTLIGHT_SELECTOR_VERSION 3** (new — never compare selector-v2 and
v3 numbers unlabeled; every pass-1/2 number is a v2, self-Spotlight
world). Official numbers at 1000 fights/encounter, seed 20260720;
dire-floor delete-test cells at the pre-declared 4000-fight resolver.
Suite: green. Experiments: tier05/exp_furina_pass3.py (w0 / world /
floors4k / a6 / cap).

## 1. Shipped (all behind tests)

- **R33 executed**: SPOTLIGHT_BASE_MULT record vetoed → PLACEHOLDER
  1.5 (pass-1 geometry restored; constants comment carries the
  re-scoped E1 record); DECISIONS 79 correction banner; the
  **knob-exercise counter law** (DECISIONS 87) implemented in
  effects.KNOB_READS + engine tests.
- **W0 forced-designation oracle** (SPOTLIGHT_FORCE, R14 diagnostic —
  never ships) + the pre-registered ceiling experiment (§2).
- **Selector v3** (§3) under full instrument discipline.
- **standing_ovation FLIP** (§4): spend-payoff + first-play trickle;
  spend lines limelight (overdraw 1) and top_billing (encore_cost 2);
  engine on-spend hook + first-play income window.
- **Rider swaps** (§5): shared_billing → hydro application,
  stage_lights → mass Weak; blocking_notes 7 (A3 rehome);
  usher_the_waves + Weak (salon debuff line). Upgrades re-authored to
  match. ALL numbers PROPOSED pending red-pen.
- FANFARE_CAP re-checked post-flip: **0.5 CONFIRMED** (fanfare
  punisher 37.6%, inside [10, 55]; the flip is spotlight-scoped).

## 2. W0 — Ceiling designation experiment (R33)

Validity gates PASSED on the exercise-counter law's first use:
forced-companion cells read the knob 55k–128k times, forced-self
cells **0** — E1's failure mode is now structurally excluded.

| dose | punisher | swarm | attrition | tank_boss | mean |
|---|---|---|---|---|---|
| depth5 self (ref) | 2.3% | 100% | 85.4% | 10.0% | — |
| depth5 comp ×1.25 | −2.0pt | 0 | +2.4pt | −10.0pt | −2.40pt |
| depth5 comp ×1.50 | −1.5pt | 0 | **+12.5pt** | −10.0pt | **+0.25pt** |
| depth3 comp ×1.25 | −3.5pt | 0 | −11.6pt | −15.1pt | −7.55pt |
| depth3 comp ×1.50 | −3.5pt | 0 | −7.0pt | −15.1pt | −6.40pt |

**Registered reading:** outward designation is VALUE-RATIONAL at
(full-kit depth, mult 1.5) — and it is **encounter-contingent**: it
wins crowds and grinds (attrition 85.4% → 97.9%) and loses duels
(tank_boss zeroed). Not a dead knob, not a dominant strategy — a real
draft-gated ceiling that must be aimed. Dose evidence favors 1.5 for
the placeholder (1.25 is nowhere value-rational); **ratification is
red-pen's**. The registered consequence fired → selector v3.

## 3. Selector v3 (instrument change; archive table)

Value-aware threshold: deepest companion iff per-character depth ≥ 4
(full kit; W0 brackets (2, 4]) AND ≥ 2 living enemies; else self;
last-resort any-companion only with zero self cards. Both constants
PROPOSED pending red-pen.

v2 → v3 world shift (1000 fights, pre-W1 sheet; the archive row is
pass-2's world): spotlight_weighted attrition 85.4% → **95.2%** (the
W0 niche, captured by the heuristic), tank_boss **held 10.0%** (duel
protection is the design), punisher 2.3% unchanged; delete-test PASS
(+7.0 attrition, +9.3 tank_boss) against a STRONGER probe (it now
designates its own kit in crowds: 69.0% → 88.2% attrition).
Salon/fanfare/Klee worlds untouched (threshold unreachable).

## 4. W1 — The flip, and the dose record that matters

Landed: `ovation_spend_boost` 10 (two-copy cap 20; grants
spotlight_mult_bonus_turn through the same §2.2a pipe on every Encore
spend EVENT) + `spotlight_encore_first` 1 (first Spotlighted play per
turn — activity-gated; the no-passive-accrual law holds). Limelight
spends 1 by overdraw (an encore_cost gate bricked opening hands);
top_billing gates at 2.

| dose | spotlight A4 | tank_boss | punisher (4k where run) |
|---|---|---|---|
| pass-2 generator (2/play) | 7.7 | 10.0% | 2.3% |
| pure sink | 2.1 | 0.3% | 0.2% |
| flip + 1/play trickle | 9.5 | 8.6% | 1.55% (−0.38 vs probe, FAIL) |
| flip + 2/turn trickle | 8.2 | 4.4% | 0.5% |
| **flip + 1/turn trickle (landed)** | **4.6→4.3 final** | 0.4% | 0.07% |

**The structural finding:** absorption COMPOUNDS with survival —
longer fights mean more income mean more absorption — so **no income
dose puts A4 on the declaration while absorption still funds the
single-target floors.** Prevention texture (W2/W3) is the only
sustain replacement that bills honestly. This is the pass's central
measurement.

## 5. W2 + W3 — Rider swaps and the utility lift

W2 (shared_billing → hydro aura, single-target — the freeze cell is
untouched; stage_lights → Weak): A4 landed 4.2; A3 dipped 2.4 → 1.9
(the plan's axis-dip branch fired — the +1 rehome under-covered 7
points of stripped rider block); A6 +0.1 only. W3 (usher_the_waves +
Weak; stage_lights Weak → ALL; blocking_notes 7): salon rose for free
(punisher 92.8% → 94.3%, tank_boss 61.0% → **68.5%**), A6 median
+0.15. blocking_notes 7 ties Klee's Hide and Seek with a rider on top
— **[USER] cross-sheet parity flag**.

## 6. Statline vs declaration (1000 fights; selector v3 world)

| Axis | Target | Starter | Median | Verdict |
|---|---|---|---|---|
| A1 Frontload | 1.0–1.5 | **1.2** | 2.6 | Starter EXACT |
| A2 Scaling | ~3.0 | 4.9 | 4.5 | **spotlight 4.5 > ratified band 4.3 — ask 3** |
| A3 Block | ~2.5 | 3.7 | 1.9 | **Under by 0.6 — ask 4** |
| A4 Sustain | **4.3** | **4.4** | **4.3** | **MEDIAN EXACT — the pass headline** |
| A5 Velocity | 3.7 | 3.0 | 3.2 | Unchanged (levers still un-spent, R19) |
| A6 Utility | **4.2** | 2.0 | 3.5 | Under by 0.7 — mechanism now known, ask 2 |
| A7 Setup tax | ~2.0 | 1.0 | 1.5 | Weakness intact |

Shape heuristic passes on starter AND median; A4>A1 holds everywhere;
all ratified WINRATE bands hold; Klee's world verified unchanged.

## 7. Delete-test — final record (pre-declared 4000-fight resolver)

attrition **+7.0pt PASS**, swarm level, punisher **−1.85pt FAIL**
(0.07% vs 1.93%), tank_boss **−0.50pt FAIL** (0.35% vs 0.85%). In the
A4-corrected world her machinery decisively earns its slots in crowds
and grinds and no longer buys single-target survival — the §4
coupling at full resolution. Both floor cells are dire on BOTH arms
(everything under 2%). Disposition is red-pen's (ask 1); the
recorded options: (a) accept crowd-scoped machinery value and band
the floors accordingly; (b) authorize single-target machinery content
(a duel-shaped Spotlight payoff); (c) package-level defense (e.g.
fortissimo_guard displacing measured-negative encore_performance —
interacts with the OPEN EP ask, so it is NOT prejudged here).

## 8. A6 — the shortfall's mechanism (term decomposition, 1000 fights)

| deck | aoe-term | debuff-term | uptime-term | A6 v2 |
|---|---|---|---|---|
| (baseline sums to) | 1.50 | 0.90 | 0.60 | 3.00 |
| salon | 2.38 | **0.14** | 1.00 | 3.52 |
| spotlight | 2.17 | **0.46** | 0.95 | 3.58 |
| fanfare | 2.48 | **0.09** | 0.68 | 3.24 |

The debuff term is nearly dead: ref_ironclad is a DEBUFF-HEAVY anchor
(Bash-grade Vulnerable volume), so her texture-grain Weak riders are
ratio-invisible — W3's three debuff edits moved the median +0.15.
Uptime is near its practical ceiling (+0.2 headroom). Closing 0.7
needs **number-grain volume** (AoE damage or mass debuff on
repeatables at uncommon/rare — with A1/A2-band knock-ons), or an
**anchoring ruling**: debuffs are ratio-anchored against a high
baseline while uptime got additive anchoring precisely because its
baseline is degenerate — an applier-identity character reads low on
debuff ratio BY ANCHOR CHOICE. Both routes are red-pen's (ask 2).

## 9. Honest gaps

- Spotlight single-target floors are dire on every arm measured
  (≤2%); the pass made them honest, not good.
- The A2 band violation (4.5 > 4.3) is a boost-cadence effect: spend
  events add scaling the banded world never had. Deck bands were
  measured in a struck world (R33) — but ratified bands are law until
  the user moves them, so it is reported, not re-banded.
- The v3 selector constants (depth 4, crowd 2) are W0-bracketed, not
  swept; depth 3 vs 4 was not dosed (only 2 and 4 exist in the arms).
- E4/EP comparisons carry the pass-2 package; this pass did not touch
  EP or its slot (open ask preserved).
- Fanfare A4 10.0 saturation untouched (R32.4 — out of scope).

## 10. Asks (decision-ready)

1. **Delete-test floors disposition** (§7): accept crowd-scoped
   machinery + band accordingly / authorize duel-shaped content /
   package defense (EP-slot interaction noted)?
2. **A6 route** (§8): number-grain volume pass, or debuff-anchoring
   ruling (additive like uptime), or re-declare? ("Re-declare" was
   rejected by R31 — presented only for completeness.)
3. **A2 spotlight re-band**: 4.3 → 4.6ish in the flip world, or
   nominate a scaling trim (ovation boost 10 → 5 is the natural dial)?
4. **A3 repair route**: more block in spotlight/generic glue collides
   with Klee-parity pins (graceful_retreat's stays-under;
   blocking_notes now TIES Hide and Seek — ratify or revert that +1?).
5. **W0 knobs**: SPOTLIGHT_BASE_MULT 1.5 placeholder → ratify?
   Selector v3 constants (depth ≥ 4, crowd ≥ 2) → ratify?
6. **Standing items** (unchanged, still open): EP disposition +
   re-cost (pass-2 ask 3); spotlight rows red-pen (now includes the
   flip row); naming/lore eyes-on pass (R29d); winrate band proposals
   (deferred per R32 — the world moved twice again as predicted).
