# Furina Sheet Pass 2 — Report ("The R16 World")

**Date:** 2026-07-20. **Plan:** furina-sheet-pass-2-plan.md (experiments
pre-registered there). **Authorized:** R28. **Governing:** R16–R22, R26,
DECISIONS 69–78, kickoff v0.1, principles v1.10.
**Environment:** CONSTANTS_VERSION 2, DRAFTER_VERSION 2,
RUNTEMPLATE_VERSION 2, **A6_INSTRUMENT_VERSION 2** (new, R18).
Official numbers at 1000 fights/encounter, seed 20260720. Suite: 228
green. Experiment battery: tier05/exp_furina_pass2.py (committed).

## 1. Shipped (all behind tests)

- **R16 card-mediated boosting.** Two new powers through the EXISTING
  `spotlight_mult` pipe — `spotlight_mult_bonus` (combat-scoped
  percentage points) and `spotlight_mult_bonus_turn` (this-turn window),
  plus `spotlight_flat_damage_turn` (this-turn flat rider). §2.2a
  numbers-only is inherited structurally: the helper feeds damage/Block
  and nothing else. The pilot values boost cards and sees the bonus in
  expected damage automatically.
- **Spotlight list re-authored** (counts preserved; 76 cards stays 76):
  **limelight** (common: +25% this turn, draw 1) replaces
  warm_reception; **stage_lights** (common: flat +2 this turn, block 3)
  replaces props_department; **shared_billing** reworked (block 4 +
  +25% this turn); **top_billing** (uncommon power: +25% for the
  combat, two-copy ceiling) replaces constant_star. Generators, the
  two ratified texture lines, duet, standing_ovation, directors_cut,
  blocking_notes, curtain_cue, and all Spotlight rares KEPT — §3A
  proved them load-bearing or harmless; the administration commons were
  the dead slots. ALL re-authored numbers PROPOSED pending red-pen.
- **`SPOTLIGHT_MULT` → `SPOTLIGHT_BASE_MULT`**, measured at **1.0**
  (E1). Pass-1 numbers were taken at 1.5; never compare unlabeled.
- **star_of_the_show ERRATA (found live):** the engine caps a power's
  TOTAL at `max_stacks`; the pass-1 row (amount 3, max_stacks 1)
  silently shipped the card at +1, not its printed +3. Re-encoded
  (max_stacks now counts power units); the upgrade applier bumps
  max_stacks alongside amount for single-application rows so the
  upgraded card actually grants +4. Pass-1 self_carry numbers carried
  the bug (its cells move: punisher 38.0% → 49.3% at the same
  constants — most of that is the honest +3).
- **pit_orchestra errata** (DECISIONS 76 / R26): Encore rider 2 → 1;
  strictly tankier / strictly less flux than macaron_break — neither
  dominates. The pair left the lint's KNOWN set; the lint guards the
  fix.
- **A6 instrument v2** (R18): application uptime (fraction of enemy
  intents taken under an elemental aura) at
  `3.0*(0.5*aoe + 0.3*debuff + 0.2*(1 + uptime − uptime_base))` —
  additive anchoring because the baseline's uptime is 0 (a ratio would
  divide by it). ref_ironclad = 3.00 exactly under v2 (verified).
- **spotlight_weighted A2 band 4.3** landed (R19 schedule: measured 4.0
  + the 0.3 margin convention). Red-pen may adjust.
- Pass-1 experiment script carries an archive note (its fillers named
  re-authored cards; a re-run measures the current sheet, not pass 1).

## 2. E1 — SPOTLIGHT_BASE_MULT sweep × delete-test

**The sweep returned cell-for-cell IDENTICAL results at 1.0 and 1.25 —
the base mult never fires at committed-median.** The depth contest
rationally self-Spotlights (the §3B finding, now load-bearing): every
deck's designation lands on Furina, whose rate is the ratified
`SPOTLIGHT_SELF_MULT`, so the companion base rate is a dead knob in
every median world. The registered rule picks **1.0**: at the drafted
depth-4+ ceiling, where companions DO hold the stage, their
empowerment now comes from her cards alone — R16's intent, exactly.

**§8 criterion-2 delete-test: PASSES** (pass-1 headline FAIL,
reversed): spotlight_weighted vs companions-only probe — punisher 2.3%
vs 2.0% (+0.3pt), swarm 100% vs 100%, **attrition 85.4% vs 69.0%
(+16.4pt), tank_boss 10.0% vs 0.7% (+9.3pt)**. Her machinery cards now
earn their slots; the tank_boss floor rose 0.4% → 10.0% vs pass 1.
Criterion 1 holds everywhere (self_carry 49.3% punisher vs salon
92.8%; the rise from pass-1's 38.0% is the star_of_the_show errata).

## 3. E2 — Fanfare cap confirmation (6-blood uncapper)

punisher 2.4% / **37.6%** / 63.0% at 0.25 / **0.5** / 0.75 —
cell-for-cell the pass-1 sweep. The deeper blood price is invisible at
deck scale (the uncapper is one rare among 17 cards) and 0.5 sits
squarely inside the registered [10%, 55%] sanity band. **Ratified 0.5
CONFIRMED; no ask.**

## 4. E3 — A6 v1 → v2 (discontinuous BY DESIGN; archive table)

| config | uptime | A6 v1 | A6 v2 |
|---|---|---|---|
| ref_ironclad/starter | 0.0% | 3.00 | **3.00** (anchor) |
| klee/starter | 79.2% | 2.96 | 3.19 |
| klee/demolition | 79.3% | 3.52 | 3.61 |
| klee/spark | 87.4% | 3.01 | 3.27 |
| klee/reaction | 62.1% | 4.11 | 3.92 |
| furina/starter | 39.0% | 1.45 | 1.99 |
| furina/salon | 64.9% | 3.39 | 3.42 |
| furina/spotlight | 58.0% | 3.22 | 3.31 |
| furina/fanfare | 12.7% | 3.56 | 3.24 |

Klee archetype-median: 3.52 → **3.61**. Furina archetype-median: 3.39
→ **3.31**. **The honest headline: an instrument that can finally see
her says her declared-elite A6 (4.2) is genuinely short, not
instrument-blind.** The fanfare deck applies almost nothing (12.7%
uptime) and drags the median; salon/spotlight sit at ~60% uptime but
their AoE/debuff terms are midling. Ask 2. Klee's world verified: all
of Klee's ratified bands hold under v2 (1000-fight report).

## 5. E4 — Graded-encounter EP battery (R21, registration (i))

The graded ladder (tank_boss × HP {0.6–1.4}, score = grades cleared,
400 seeds/arm) RESOLVES pass-1's quantization — and the answer is
negative: **+EP mean 0.45 grades, P90 1; warm-body control
(courtroom_drama) mean 0.57, P90 2.** At committed depth-5 (full
Chevreuse kit + Lynette in deck — the DEEP world, not the median-2
world), duplication is worth LESS than a generic debuff common: it
does not lift the ceiling, it drags both ends. This is a measured
negative, not "no effect." **Proposed disposition (ask 3): close
registration (i) as MEASURED-NEGATIVE at current cost, and route
Encore Performance's re-cost (R16 said generators/EP/texture get
re-costed in this world) through red-pen.** Both arms' medians are 0 —
tank_boss even at 0.6× HP defeats most seeds; the spotlight deck's
heavy-hitter floor remains its identity weakness.

## 6. Statline vs declaration (1000 fights; A6 under v2)

| Axis | Target | Starter | Median | Verdict |
|---|---|---|---|---|
| A1 Frontload | 1.0–1.5 | **1.2** | 2.6 | Starter EXACT |
| A2 Scaling | ~3.0 | 4.9 | 4.0 | Deck-banded (7.6/4.2/4.3); all under band |
| A3 Block | ~2.5 | 3.7 | **2.4** | Median on target |
| A4 Sustain | **4.3** | **4.4** | 8.0 | Starter EXACT; **median HOT — ask 1** |
| A5 Velocity | 3.7 | 3.0 | 3.2 | Still under by 0.5 (levers still un-spent) |
| A6 Utility | **4.2** | 2.0 | 3.3 | Under by 0.9 **with a sighted instrument** — ask 2 |
| A7 Setup tax | ~2.0 | 1.0 | 1.5 | Weakness over-delivers (accepted direction, R19) |

Shape heuristic passes on starter AND median; A4>A1 holds everywhere.
Curve exponents ≤ 0.28 (no superlinearity). All ratified bands
(salon 7.6 / fanfare 4.2 A2; salon winrates) hold; the new spotlight
band 4.3 holds at its own measurement.

**A4 median 8.0 note:** the median moved 5.2 → 8.0 because the middle
deck changed — the re-authored spotlight deck sustains at 8.0 (longer
lived via boosts + standing_ovation throughput; fanfare saturates at
10.0 as before). Elite was declared 4.3; 8.0 is a different animal.
The candidate levers are hers (standing_ovation stacks, shared_billing
block), but A4 interacts with the Encore economy everywhere — flagged
for red-pen rather than tuned unilaterally (ask 1).

## 7. Winrate band proposals (ratification is red-pen's)

Now that the R16 world is the world: spotlight_weighted attrition
floor 0.75, tank_boss [0.05, 0.30], swarm floor 0.95 (punisher left
unbanded — 2.3% is a dire floor, not an identity; see honest gaps);
fanfare_weighted punisher [0.25, 0.50], swarm/attrition floor 0.95.
Salon's ratified bands unchanged and holding.

## 8. Honest gaps

- **Spotlight punisher floor 2.3%** — unchanged by R16; the deck still
  folds to burst pressure. Its defense is thin by construction; the
  boost cards scale damage, not toughness. Candidate: shared_billing/
  stage_lights block numbers (red-pen scope).
- Selector aiming remains heuristic v2 (raw depth, not value).
- A5 3.2 vs 3.7 and A7 1.5 vs 2.0 remain deliberately un-spent (R19).
- E4's ladder never exercised grades above 1.0× for most seeds; a
  gentler ladder (or a non-tank_boss graded set) would resolve finer
  once the floor rises.
- Co-op value stays Tier-2-invisible (accepted, R18).

## 9. Asks (decision-ready)

1. **A4 median 8.0 vs declared 4.3** — accept as the R16 world's shape
   (fanfare already saturated at 10 in pass 1), or nominate the lever
   (standing_ovation max_stacks, shared_billing block) for pass 3?
2. **A6 3.3 vs declared 4.2 under the sighted instrument** — the gap
   is sheet-real now: add application texture (the fanfare deck's
   12.7% uptime is the drag; her skill_tag density is the dial), or
   re-declare A6 down toward ~3.5?
3. **Registration (i) disposition** — close as MEASURED-NEGATIVE at
   current cost and re-cost Encore Performance (proposal: cost 0, or
   rider "the copy costs 0"), or hold open pending a depth-6+ drafted
   instrument?
4. **Re-authored Spotlight numbers red-pen** — limelight/stage_lights/
   shared_billing/top_billing rows + the winrate band proposals in §7.
5. **star_of_the_show errata ratification** — the +3 encoding is what
   the sheet always SAID; pass-1 measurements carried +1. No sweep was
   invalidated (self_carry cells move as noted), but the record should
   say the user saw it.
