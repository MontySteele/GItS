# Klee Tier 0 Pass 3 — Report (& v0.1 scorecard baseline)

**Date:** 2026-07-19. **Input:** sheet v0.3 + round-3 rulings. 96 tests green. Everything on the pass-3 checklist is implemented; the grid is green except **two tank_boss band deviations**, documented below with trails per protocol. Requesting band ratification — everything else is done.

## Implemented per checklist

- **Frozen→Vulnerable 2 on bosses** (decision-2 contingency, +test). Consequence measured below — it's bigger than the trail anticipated.
- **Splash proc-cap**: engine support landed, **dormant** (constant `None`), armed test proves 3-cap behavior. The trigger condition (demolition median A2 drag) did not fire — median passes without it.
- **Heuristic/constraint restructure**: shape heuristic + A1>A2 now evaluate on starter and the archetype-deck **median** (hard); packages get warnings + per-deck A2 band checks. `--report-character` CLI runs the whole canon.
- **Plausible-draft packages**: demolition/spark got their 3 draft-ins; canonical `reaction_weighted` reconstructed as the reaction_burst build (chat-Claude's exact list lived only in their clone — composition re-derived from the trail: 6 companions + amp payoffs incl. reworked Boom + Burst&accelerator + defense, tuned to the stated acceptance: A2 ≤3.5 with floors met).

## The frozen v0.1 scorecard baseline (500 fights, seed 42)

**Median identity (the canon):** A1 **4.2** | A2 **3.9** | A3 **2.2** | A4 **0.5** | A5 3.0 | A6 **3.6** | A7 2.4 — passes heuristic + A1>A2, and sits within ±0.5 of every declared target (A1 4.5, A3 2.0, A4 ~0.5, A6 4.0; A5 3.0 vs declared 3.5 is the one soft spot, noted).

Per-deck: demolition A2 4.4/≤4.8 ✓, spark 3.9/≤4.5 ✓, reaction 3.4/≤3.5 ✓. Reaction is her cleanest statline (A1 4.5 / A6 4.0 / A3 1.1) and passes the shape heuristic standalone. Pilot regret: spark 4%, demolition 14%, reaction 25% (stable archetype baselines).

Grid (winrates): all decks 93–100% on swarm/punisher/attrition/burst_check. Gauntlet: demolition 99, spark 95, reaction 92 (floor 75 ✓). Tank_boss: demolition 96.8, spark 56, reaction **57.8** (floor 35 ✓), starter 56, dream_team 53 (still < demolition 97: enabler-not-carry ✓).

## The two band deviations (asks)

1. **demolition tank_boss 96.8% vs band 85–96** — 0.8pt over, binomial noise at 500 fights is ±1.5pt; statistically indistinguishable from the ceiling. Ask: widen to 85–97 or accept as-is.
2. **spark tank_boss 56% vs band 65–85** — real, and instructive. Trail (8 variants tested): plausible-draft spark builds cluster 44–61%. Dropping block riders makes it WORSE (56→44%) — your own diagnostic ("spark survives via block density") confirmed: the riders are load-bearing vs the boss. Burst-feeder draft-ins reached 61% but wrecked A1 (3.1) and crowded the A2 band. **The 65–85 prediction was derived from pass-2's 69% — a monoculture measurement, the exact test-deck style round 3 abolished.** Under real drafts, spark's honest boss line is ~55%. Ask: revise the band to ~50–70 rather than force an implausible deck.

3. **Flag, not an ask: Frozen→Vuln overshot the trail.** Reaction tank_boss landed at **57.8%**, not the predicted ~35–37%: the ruling's own Frozen change gives her hydro+cryo companion pair repeating Vulnerable-2 uptime on bosses, compounding with the Boom rework. All stated floors/bands are met (floors have no ceiling), but "solo reaction floors at ~35%, co-op-primary" now under-describes her — solo reaction is merely boss-mediocre, not boss-weak. If the co-op-primary framing is load-bearing for character identity, Frozen-boss-Vuln may want to be 1 stack; if the framing was descriptive, celebrate and move on. The TIER2-VALIDATE co-op marker stands either way.

## Status

Tier 0 for Klee v0.1 is **done pending the two band ratifications** (and the optional Frozen flag ruling). On ratification this scorecard freezes as the design baseline and the project pivots to BaseLib/C# (Tier 1 AutoSlay soak next).
