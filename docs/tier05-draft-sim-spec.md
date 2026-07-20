# Tier 0.5 — Draft-Level Simulator Spec & Handoff

**Slots after:** pass-3 grid green (Tier 0 frozen as Klee's design baseline). **Before:** any C#.
**Audience:** Claude (in Claude Code). Same drill: commentary first, it explains what to avoid.

---

## 0. Commentary from your chat-instance self

Tier 0 validated card *numbers*; it never validated card *distribution* — the pool math (rarity spreads, 15–20 cards per archetype, the 60–70% reward-advances-your-plan claim, the companion slot's nation weighting) shipped on faith. Meanwhile the loudest lesson of passes 1–2 was that our hand-built test packages were the weakest link in the pipeline: nearly every fix was "add what a human drafter would obviously add." Tier 0.5 exists to kill both problems at once by making decks *emerge from drafting* instead of being authored.

**Scope principle (the whole boundary in one sentence): simulate what WE design; measure what MegaCrit designed with Tier 2 bots on the real game.** Our cards, pools, reward slots, weightings, draft flow → in scope, we're authoritative. Their map pathing, events, gold economy, boss mechanics, relic pools → out of scope; any model of those is guesswork about someone else's system and Tier 1/2 measures the real thing. When tempted to add fidelity, ask which side of that line it's on.

**Known largest fidelity gap, accepted deliberately:** no card upgrades (v1 sheet has no upgrade paths). Log it in DECISIONS.md; do not invent upgrade rules to fill it.

**The confounder we're pre-registering:** draft-policy quality is the pilot-suspect problem one level up. Countermeasures are mandatory, not optional: `draft_regret` instrumentation from day one (before the first finding, not after the second bug), and every headline finding must survive an A/B across two distinct policies before it's believed.

---

## 1. Goals
1. Replace authored test packages with emergent drafted decks; re-run Klee's acceptance grid on them.
2. Validate the distribution claims: reward-relevance rate, archetype achievability, dream-team assembly rate, aura-starvation under real drafts.
3. Detect goodstuff convergence — the "every run plays the same" failure the archetype system exists to prevent.
4. Measure run-level fragility (the thing the A4 saga proved fight-level metrics cannot express): HP trajectory across a full run finally makes "62 HP, reluctant defense" bite.
5. Forward-compat: companion-slot *modes* (standard / choose-1-of-3 / pity-boosted) so Columbina's bricking-mitigation relic and the v2 Wish banner test on this rig without rework.

## 2. Run model (all constants in constants.py, as ever)
A run = 14 nodes, fixed template (no pathing choice — that's their design, not ours):
`N N N E N R N N E N R N B` + one `burst_check` swapped over a mid N (position in constants).
- **N (normal):** drawn from a weighted pool of battery-derived normals (swarm, attrition-lite = 1×45HP unit, punisher-lite = 70% statline). Same frozen statlines, no new tuning.
- **E (elite):** punisher. **B (boss):** tank_boss.
- **R (rest):** heal 30% max HP, OR remove 1 card (policy chooses). Removal is the one economy lever we keep because deck-thinning is deck design, squarely our side of the line.
- HP persists across nodes (this IS the fragility instrument). Death = run over; log node index.

## 3. Rewards (our design — the thing under test)
After each fight: 3 cards rarity-rolled (constants: 60/35/5 common/uncommon/rare as v1 defaults) from the character pool, **plus the companion slot**, skip always allowed.
- Companion slot: nation weighting per principles §4.1 (mechanism implemented even though v0.1 is single-nation), 5-star companions at rare odds only.
- **Slot modes (build all three now):** `standard` (1 offer), `choose3` (pick of three), `pity(k)` (k rewards without a companion taken → next offer upweighted/choose3). Mode set per-config; default standard.
- Signature-companion event: node 2 offers the personal-pool signature (Prune) as a free take-or-skip. (Design decision from chat — see "guaranteed teammates" in round-4 notes; testable here.)

## 4. Draft policy
Two policies, both shipped in M5–M6 (the A/B is structural, not a stretch goal):
- **Assigned:** run is seeded with a target archetype; scores rewards by archetype tags (enabler value decays as the core completes; payoff value gated on core), plus universal terms: defense quota (draft block while deck block-density < threshold — the real-draft principle codified), curve awareness, deck-size penalty, Burst priority once the archetype is reaction.
- **Adaptive:** no seed; pure power/synergy scoring with commitment emerging from what's been drafted. **This is the goodstuff detector:** if adaptive runs converge on one deck shape, the pool has a problem no assigned-mode stat will reveal.
- `draft_regret`: sampled offers re-scored post-run against realized deck performance deltas; report per-policy.

## 5. Metrics & acceptance
- **Reward relevance:** P(≥1 offer advances the run's plan) — claim: 60–70%. Measured per archetype.
- **Achievability:** assigned-mode time-to-online (fights until archetype core assembled; reaction core := 2 appliers + 1 amp payoff + Burst). Alarm if median > 7 fights for any archetype.
- **Divergence:** adaptive-mode archetype distribution over ≥1000 runs; alarm if any single shape > 55% or any archetype < 10%.
- **Dream team:** assembly rate of 2+ five-star companions in one run; expectation: rare (single digits %) under standard slot, deliberately fishable under choose3/pity.
- **Run fragility:** winrate, death-node heatmap, HP trajectory percentile bands. Klee's declared identity finally testable: expect elite/boss death clustering, healthy normal-fight economy. Compare vs REF_IRONCLAD runs (build his reward pool from starter+package cards; he is still the 3.0 anchor).
- **Aura starvation under real drafts** (not injected companions): reaction-committed runs, % with zero reactions at boss. This is the number the injected-config version always flattered.
- Full Klee acceptance grid re-run on emergent decks; bands from round-3 rulings apply.

## 6. Milestones
- **M5:** run loop, rewards (standard slot), assigned policy, draft_regret, REF_IRONCLAD runs, fragility metrics. Determinism test at run granularity.
- **M6:** adaptive policy, divergence/relevance/achievability metrics, A/B harness, acceptance report format.
- **M7:** slot modes (choose3/pity), signature-companion event, dream-team stats, Wish-banner stub (mode behind a flag, economy NOT modeled — gold is their design).
- Each milestone: findings in `docs/tier05-passN-report.md`, same asks-for-chat format. It's been working.

## 7. Non-goals (v1)
Map pathing/branching, events, gold/shop economy (visiting-companion shop offer folded into slot modes instead), relics beyond existing hooks, potions, upgrades (logged gap), multiplayer (Tier 2), and any enemy content beyond re-skinned battery statlines. If a finding seems to require one of these, it's a Tier 1/2 question — write it down, don't build it.

## Addendum (v1.8 ruling) — Featured Banner lands in M7
The reward generator gains the seeded banner roll: 3 limited 5-stars per nation per run (degenerate at v0.1 roster size — no behavior change until the roster grows). Metrics updates: dream-team assembly becomes *conditional* (P(assembly | featured)) plus a banner-variance stat (spread of run outcomes across banner rolls per archetype — the bad-roll-bricking detector that decides whether `standard: true` companions flip to off-banner floor status). Banner is part of the run's seed determinism.
