# Pass-2 Rulings — Round 3 Handoff

From chat-Claude. I pulled e50e9bb and ran the ruling candidates through the harness before ruling — this round produced several null results and one major reframe, all documented below because the negatives are as binding as the positives. Sheet ships as **v0.3** (one change vs v0.2: boom_goes_the_dynamite reworked; my experimental bomb-cap 3 reverted to your committed 4 after measuring null).

## Ask 3 first (reaction boss collapse) — it's neither a hole nor a designed weakness as framed. Ruling: co-op-primary archetype with a solo floor.

Empirical trail, in order (all 400-fight tank_boss runs, seed 42):
1. Original reaction_weighted: **1.8%**. Generic pilot: **1.0%** → NOT the pilot (third "pilot suspect first" check; first one to exonerate it).
2. Rebuilt as a real draft (6 companions + Klee carry cards): **1.0%** → not the deck list either.
3. + defense package (real drafters draft block before a boss): **14.8%**.
4. + her Burst and accelerator — the actual hole found: **the archetype that charges the meter fastest had no Burst in any test deck**: **33.5%**.
5. + boom_goes_the_dynamite reworked into the amp-nuke (Deal 16; if this triggers a reaction, repeat — the payoff amps were multiplying 7-damage hits, which is not how Vaporize kills bosses in the source material): **36.8%**, with gauntlet at 84.5%.

That ~35–37% is the archetype's structural ceiling under the iron rules: per-hit amps + uncommon-capped companions + no scaling mathematically cap DPT ≈ 18–21 vs a race line of ~26 (demolition wins at 28.5; spark survives instead at DPT 20 via its block density — that contrast was the diagnostic key). **Adopted:** (a) Frozen-on-boss → Vulnerable 2 (decision-2 contingency formally triggered; my prototype is in reactions.py locally — implement properly with a test), (b) canonical reaction_weighted := the "reaction_burst" package I left in klee.yaml (real-draft principle below), (c) the boom rework (sheet v0.3). **Accepted:** solo reaction floors at ≥35% tank_boss / ≥75% gauntlet (both met). The archetype's home is co-op — where the partner is the boss plan and Klee is the amp — which Tier 0 cannot model; add a `# TIER2-VALIDATE: reaction co-op` marker. Do not buff further toward 50%: swarm/attrition are already 100% and the next buff breaks enabler-not-carry.

## Ask 1 (A2 knob) — both pre-authorized knobs measured NULL; ruling restructures the constraint instead.
- Gleeful Barrage spark-cap: **inert** — sparks are *spent* at 3 by the free-attack mechanic, so `min(sparks,4)` never binds. The report's suspected driver doesn't operate; spark's A2 comes from free-attack energy smoothing (late-turn surplus), i.e., honest engine texture.
- bomb_damage_up cap 4→3: **inert** (A2 4.7 unmoved). Reverted.
- **Ruling:** the error was evaluating the two-strong-axes heuristic and the A1>A2 constraint on deliberately-extreme monoculture packages. Both now evaluate on **starter + the median across archetype decks**; per-deck A2 bands: demolition ≤4.8, spark ≤4.5, reaction ≤3.5 (all currently met). A1>A2 demotes from hard CONSTRAINT to warning on package decks, stays hard on starter+median. One untested candidate remains if demolition's median drags: Blazing Delight splash **proc cap 3/turn** — surgical (early turns rarely exceed 3 detonations, so it hits only the late window, unlike the flat shave that cost A1 last round). Test it only if the median check fails.

## Ask 2 (spark A3) — accept 4.1 as texture.
The sanctioned experiment nulled (Δ0.02) and shave elasticity is ~0.075/point across two waves. The surplus-energy driver is the archetype working as designed: her free attacks fund small blocks. Identity survives with a better sentence: *demolition and reaction Klee is fragile (A3 1.7 / 0.4); spark Klee can't be caught.* Design doc updated. No further edits; remove the ≤3.5 spark target from acceptance.

## Ask 4 (demolition A6 3.4) — accept, and codify the general principle it revealed.
**Archetype test packages must model plausible drafts, not monocultures** — this round's biggest lesson (the reaction fix chain was mostly "add what a human would obviously draft": defense, the Burst, an AoE common). Add to each package the 3–5 natural cross-archetype draft-ins (blast_radius for demolition, etc.), note the principle in DECISIONS.md, and re-run the full grid once under the final packages so pass-3 numbers are all on the new canon.

## Pass-3 checklist
1. Implement: Frozen→Vuln 2 (+test), splash proc-cap support (dormant until triggered), heuristic/constraint restructure (starter+median), package updates per ask 4.
2. Re-run full grid (all decks × battery) on sheet v0.3 + new packages; expected all-green under the revised bands: demolition 85–96 tank_boss, spark 65–85, reaction ≥35 / gauntlet ≥75.
3. If green: Tier 0 is DONE for Klee v0.1 — freeze the scorecard as the design baseline, and the project pivots to the fun part: BaseLib/C# implementation (Tier 1 AutoSlay soak testing is next in the plan). Anything still red comes back to chat with the same empirical-trail format — it's been working.
