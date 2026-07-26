# Triage Execution — Report (splash cap, compensator, re-measure, pity)

**Date:** 2026-07-19. **Input:** errata-m5-triage.md. All four rulings executed; 124 tests green, no xfails. One new decision-ready finding at the bottom — the reaction-assembly re-measure decomposed into something more interesting than a pool-odds tweak.

## Ruling 1 — splash cap: ARMED ✓
Constant 3, sheet v0.4's `splash_procs_per_turn` drift-guarded in tests, xfail flipped to a hard pass. Demolition tank_boss at 1000 fights: **96.5%**, exactly the pre-measured value; all winrate bands green; medians moved ≤0.03 so the v0.1 snapshot lock holds unchanged.

## Ruling 2 — cadence/Frozen insight: logged
DECISIONS records it; no repo action. Noted for Furina's sim passes: no Klee-derived Frozen expectations.

## Ruling 3b — PROGRESSION_GAP_COMPENSATOR: frozen at {normal 1.0, elite 0.8, boss 0.7}
Full 48-combo grid on the anchor (300 runs each), then the winner confirmed at 1000 runs: **47.9%** completion (target 45±10). Chosen deliberately over other in-band combos because normals stay at **1.0** — only the two checks that were calibrated as full-HP solo gates get compensated — and deaths spread across E2/boss instead of piling at one wall. Labeled in constants as one-number-not-a-model, per the ruling.

## Ruling 4 — re-measure, then pity: executed, and the confound decomposed

Full-length runs (500 each) transformed the assembly picture exactly as you predicted:

| archetype | assembly (truncated M5) | assembly (full-length) | TTO | run win |
|---|---|---|---|---|
| demolition | 26% | **89%** | 4 | 17.8% |
| spark | 4% | **43%** | 8 | 18.4% |
| reaction | <1% | **5.8%** | 8 | ~11% |

Demolition's watch-item resolves (89% — core defs were fine; truncation was the whole story). Spark at 43%/TTO 8 sits at the alarm line — M6's proper metrics can adjudicate.

Reaction stayed <15%, so the pre-authorized pity escalation ran: **pity(3) and pity(2) both measure ~zero effect** (5.8% → 6.0%). The decomposition explains why, and it's the finding:

**Reaction core assembly = 79% (≥2 appliers) × 71% (amp payoff) × 10% (Burst) ≈ 5.8%.** Two of three components are healthy — the companion slot was *never* the bottleneck, which is why a companion-slot fix can't move the number. (The 71% is after I fixed a genuine policy deadlock the decomposition exposed: my payoff-gating gated amp payoffs on a core that *contains* an amp payoff — amp assembly was 1% before the fix. Policy-confounder flag honored; the fix is the "advancing the core is never a dead pick" term, regression-tested.)

The binding constraint is **`sparks_n_splash` being one of 15 rares at 5% rarity odds**: ~10% of runs ever *see* the Burst. As long as the declared core includes her Burst, no slot mode fixes assembly — the missing component lives in the card pool.

**Options for ruling (not taken locally):**
1. **Burst is innate/granted** — Genshin-faithful (bursts are kit, not loot); mechanically similar to the node-2 signature-companion event already specced for M7. My recommendation, for what it's worth: it also makes the burst-accelerator cards readable in every run instead of 10% of them.
2. Burst-specific acquisition (guaranteed offer by node N, or rarity exception).
3. Redefine the reaction core without the Burst (measurement-side only; assembly would read ~56% and the alarm question moves to spark).

Pity's mechanism stays in the codebase (built, tested) for M7's bricking-mitigation work regardless.

## Status
Everything ruled is executed and locked. M6 (adaptive policy, A/B harness, divergence/relevance metrics, acceptance-on-harvested-decks per ruling 3a) is unblocked *except* that its achievability metric wants the Burst ruling above first — the number it alarms on is currently dominated by that one design question.
