# Klee Tier 0 Pass 2 — Report

**Date:** 2026-07-19. **Input:** sheet v0.2 + all five round-2 rulings implemented (A4 healing metric + Burning Blood anchor + floor, A6 baseline-anchored composite, A2 window 2–4 + `max_stacks`, Burst Retain, `pilot_regret`). 90 tests green. Battery untouched. One measurement-fidelity fix applied uniformly: **damage logs now clamp overkill** (combat unchanged; without it, Heavy-Blade overkill on 14-HP swarmlings out-scored actual AoE on the A6 AoE term).

## Scorecards (500 fights/enc, seed 42; baseline REF_IRONCLAD starter/generic = 3.0)

| Axis | Target (pass 2) | starter | demolition | spark | reaction | barbara_inj |
|---|---|---|---|---|---|---|
| A1 | 4.0–4.7, > A2 | 4.1 ✓ | 4.2 ✓ | 3.6 ▼ | 3.6 ✓* | 4.0 ✓ |
| A2 | ≤4.0 | 3.0 ✓ | **4.7 ✗** | **4.4 ✗** | 3.5 ✓ | 3.4 ✓ |
| A3 | ≤2.5 (spark ≤3.5) | 2.3 ✓ | 1.7 ✓ | **4.1 ✗** | 1.5 ✓ | 1.0 ✓ |
| A4 | ≈0.5 solo; rises w/ Barbara | 0.5 ✓ | 0.5 ✓ | 0.5 ✓ | 5.1 ✓† | **6.6 ✓** |
| A5 | — | 3.0 | 3.1 | 3.1 | 3.0 | 3.0 |
| A6 | ≥3.5 | 3.0 | 3.4 ▼ | 2.6 | 3.5 ✓ | 3.4 |
| A7 | — | 3.3 | 1.7 | 2.3 | 2.6 | 3.0 |

\* reaction A1 3.6 > A2 3.5 — constraint holds but by a hair. † reaction_weighted carries 2 Barbara cards by design.
**Identity constraint A1 > A2: VIOLATED by demolition (4.2 vs 4.7) and spark (3.6 vs 4.4)** — the scorecard flags fire as wired.

## Ruling outcomes

- **Ruling 1 (A4) — WORKS.** Solo decks floor at 0.5 by construction; Burning Blood anchors baseline at exactly 3.0; barbara_injection lifts A4 to 6.6 (raw ~10 healing/fight). Companion sustain-patching validated. TOO_STRONG flags cleared for demolition exactly as predicted.
- **Ruling 2 (A6) — WORKS**, with the overkill clamp as a required companion fix. Ordering anchor holds: Silent < Ironclad-package < Klee on the AoE term. Reaction hits 3.5; demolition lands 3.4 (hair under target — mine_toss/bomb_voyage spread damage, but the deck lacks blast_radius; adding one common AoE card at draft would clear it).
- **Ruling 3 (A2) — PARTIAL. Escalation needed.** Window shift + stack caps landed, but demolition A2 = 4.7 and spark = 4.4 against the ≤4.0 target, violating A1 > A2 in both. The pre-authorized knob (Playtime Forever 5→4) is **inapplicable — Playtime isn't in either deck**. Suspected drivers: demolition — bomb_damage_up at cap 4 still nearly doubles bombs (5→9) and Blazing Delight splash scales with detonation count; spark — Gleeful Barrage's `2_plus_sparks` times has no cap and Endless Fireworks feeds it every turn. Candidate knobs for round 3 (not applied): cap Gleeful Barrage times (e.g. ≤6), bomb_damage_up cap 4→3, or Blazing Delight splash 3→2.
- **Ruling 4 (A3/spark) — NULL RESULT on the sanctioned experiment.** Conditional skip_and_hop moved A3 by 0.02 (4.05 → 4.03); the sheet reverted. The residual is confirmed structural (free-attack energy surplus buys block across ALL the deck's block cards). ≤3.5 is unreachable by single-card edits; needs a ruling: accept ~4.1 as archetype texture, or shave all spark block riders again (−1 each moved it 4.4→4.1 last time, so expect ~3.7).
- **Ruling 5 (Retain) — WORKS.** Sparks 'n' Splash cast rate went from ~0% to >50% of full-meter fights (locked by test). Required teaching the pilot the Burst's payoff value (60 dmg over 3 turns) — burst cards need bespoke pilot valuation per character; noted for the v0.2 character.

## pilot_regret (the demanded instrument) — immediately earned its keep

Rates: spark 3–5%, starter 6%, demolition 10–15%, **reaction 24–29%**. The instrument caught two real pilot bugs on its first run, both fixed this pass: (1) elemental-flavored heals (Barbara's Melody) scored phantom reaction value and were overplayed; (2) the pilot had **no heal term at all**, so after fix #1 it never played heals — now valued like block (HP economy, capped by missing HP). Residual reaction-deck regret is partly definitional (setup plays sacrifice immediate value, which is what the metric measures) — treat ~25% as the archetype's baseline, not a defect.

## Tank_boss acceptance band (78–93%) — MISSED IN BOTH DIRECTIONS

demolition **95.4%** (above), spark **69%** (below), reaction **2.0%** (collapsed). Gauntlet: 98.8% / 96.0% / 56.0%.

- The global common-attack −1 shave is **not armed**: the trigger was ~98%, demolition is 95.4%, and the problem is a *spread*, not a level — a global shave would push spark/reaction further under while barely denting demolition.
- **Reaction vs bosses is the real finding:** enabler companions (4–5 dmg) can't race a ramping 240-HP boss, amplifiers are per-hit by iron rule, and Frozen is a no-op vs bosses (decision #2) — the archetype's control tools are all boss-blunted simultaneously. Either this is Klee's intended "folds to sustained pressure" weakness expressing correctly (in which case the band shouldn't apply per-archetype), or Reaction needs a boss plan (Superconduct/EC scale better vs high-HP; Vermillion-style amp is the payoff slot). Needs a ruling.

## Asks for round 3

1. A2 knob selection for demolition & spark (Playtime knob inapplicable; candidates above).
2. Spark A3: accept ~4.1 as texture, or second shave wave (~3.7 expected)?
3. Tank_boss band: per-archetype bands vs one number? And is reaction's boss collapse the designed weakness or a hole?
4. Demolition A6 3.4: accept, or expect blast_radius in demolition drafts (deck-list question, not sheet)?
