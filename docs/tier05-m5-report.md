# Tier 0.5 M5 — Report (run loop, rewards, assigned policy, fragility)

**Date:** 2026-07-19. **Input:** tier05-draft-sim-spec.md §§2–6 (M5 slice). 120 tests across both tiers (1 xfail = the pending demolition ruling). M5 is built and instrumented; two structural findings below need your eyes before M6's metrics get built on top of them.

## Built per spec

- `tier05/` package riding on the Tier 0 engine untouched: fixed node template (burst_check swapped in at node 6), HP persistence, rest = heal-30%-or-remove (policy: heal under 65% HP, else thin a basic — attacks first, block only if the defense quota survives), battery-derived normals (attrition-lite 1×45, punisher-lite 70% — mechanical derivation, zero new tuning; test-locked against the frozen statlines).
- Rewards §3: 3 rarity-rolled character offers (60/35/5) + companion slot (standard mode; 5★ **only** at rare odds; nation weighting implemented as a mechanism, all-Mondstadt v0.1). REF_IRONCLAD's pool = his own kit, no companion slot — still the anchor.
- Assigned draft policy §4: enabler decay / payoff gating on core, defense quota, curve awareness, deck-size penalty, Burst priority for reaction; skip is a real pick. `draft_regret` shipped day-one (sampled decisions re-scored post-run in final-deck context, dedicated rng stream so sampling can't perturb runs).
- Fragility metrics: run winrate, death-node heatmap, per-node HP percentile bands (over runs that reached the node), time-to-online. Determinism test at run granularity. CLI: `python -m tier05.runner --character klee --archetype demolition --runs 500`.
- Two spec notes, logged: the template string `N N N E N R N N E N R N B` is 13 nodes though §2's header says 14 — implemented the literal template. And the assigned policy as specced has **no generic power term**, which left the anchor (untagged `*_like` cards) drafting nothing; I added a static (damage+block)/cost proxy **for the generic archetype only** — flagged as confounder-relevant, and exactly the kind of thing M6's A/B harness exists to check.

## Finding 1 — the run model, as specced, completes ~0% of runs (everyone)

300 runs each, seed 42, spec constants:

| config | run win | E1 deaths | E2 | boss | final deck | TTO (online%) |
|---|---|---|---|---|---|---|
| ref/generic | 0.0% | 192 | 72 | 8 | 14.3 | — |
| klee/demolition | 0.3% | 150 | 97 | 11 | 12.3 | 4 (26%) |
| klee/spark | 0.0% | 140 | 108 | 7 | 12.8 | 6 (4%) |
| klee/reaction | 0.0% | 196 | 66 | 7 | 14.2 | 6 (<1%) |

The instrument itself works — elite/boss death clustering is exactly your predicted signature, and the HP bands make "62 HP, reluctant defense" legible for the first time. But the absolute level is a wall, and the knob trail says it's structural, not a constant miss:

- **rest 50%** (ours to tune): ~+1.5pt. **elite at 85% statline**: deaths migrate from E-nodes to the boss. **Both**: 3% (Klee) / 10.5% (ref) — the boss then kills 117/200 alone.
- Mechanism: the battery's punisher/tank_boss were calibrated as full-HP solo checks against 25-card authored decks. In-run decks arrive at ~60% HP with 12–14 cards, because the model's ONLY power growth is ~8 card picks — no upgrades, no relics, no potions. **The accepted no-upgrade fidelity gap is first-order, not a rounding error.** Logged per your commentary; I did not invent upgrade rules.

**Recommendation for ruling:** treat run winrate as *not an acceptance metric* in v1. Fragility (death distribution, HP bands, TTO) is comparative and works now; for M6's "re-run the acceptance grid on emergent decks," harvest decks *as-of reaching the boss node* (win not required) into the Tier 0 battery. Alternative: bless an in-run elite/boss statline scale (a new constant, but it's re-derivation territory — your call, not mine). The E1/E2/E3 knob measurements above are ready if you want them.

## Finding 2 — reaction can't assemble its core from real drops (pre-firing M6's alarm)

Core := 2 appliers + 1 amp payoff + Burst. In 8 reward screens with one companion slot each: **<1% of reaction runs get online** (demolition 26%, spark 4% — all below any reasonable achievability bar; your M6 alarm is median TTO > 7 *fights*, and reaction's true median is "never"). The archetype whose enablers live in the companion pool gets exactly one companion lottery ticket per screen at 60/35/5 odds. This is the pool-math the spec said shipped on faith — first empirical read says the faith was misplaced for reaction, and choose3/pity (M7) or a fatter slot is where the fix lives. No action taken; M6's metrics will quantify properly.

## Status

M5 deliverables: **done** (run loop ✓, rewards ✓, assigned policy ✓, draft_regret ✓, REF runs ✓, fragility ✓, determinism ✓). M6 (adaptive policy, A/B, divergence/relevance/achievability, acceptance format) is next and its design should absorb the two findings above — especially whether acceptance runs on boss-reached decks.
