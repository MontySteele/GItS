# Tier 0 — Decision log

Per spec §10: open questions decided during implementation, with rationale.
Amend here, not in chat history.

## M1 (2026-07-19)

1. **Hand/draw economy:** StS defaults adopted — 3 energy, draw 5/turn,
   10-card hand cap, hand discards at end of turn. Nothing broke.
2. **Frozen vs bosses:** bosses consume the Frozen aura with **no effect**
   (`FROZEN_BOSS_RESIST = True` in constants.py) rather than a 50%-reduced
   skip. Simpler to reason about, and "skip a boss turn" is exactly the
   effect that warps balance math; a flat no-op keeps Hydro/Cryo honest in
   boss scoring. Revisit if Frozen-archetype decks score dead vs TANK BOSS.
3. **Reaction splash (Overload) ignores block:** applied equally to all
   configurations, keeps the resolver damage-pipeline-free (no recursion
   into strength/vulnerable for splash). Same for Electro-Charged DoT
   (ticks HP directly, poison-like).
4. **Heavy-Blade-like:** STR×3 multiplier is not expressible in the v1 DSL;
   modeled as a flat 14-damage hit (strength still adds once). Fine for a
   reference deck; do NOT copy this pattern for real Klee cards — if a card
   needs strength multipliers, add a DSL op then.
5. **Reactions engine shipped in M1, not M4:** the resolver + full pytest
   table cost ~100 lines and de-risks the mod's one expensive system early.
   M4 still owns: Klee cards, pilot reaction weights, degeneracy detectors
   beyond INFINITE/SUPERLINEAR/AMP_STACK, aura-starvation instrumentation.
6. **PUNISHER statline re-tuned:** spec's 90 HP / atk 9 gave the starter
   deck a 100% winrate. Grid search → **130 HP / atk 9 / ramp +2 after
   turn 3** = 52.6% starter winrate (target 50–60%), package deck 100%.
   NOT frozen — M2 recalibrates against the full battery.
7. **Open (for M2):** avg HP loss vs PUNISHER is ~−40 in winning fights,
   far above the spec's −18 target, while winrate is on target. Both can't
   be hit with this statline; suspect the fix is pilot block-weighting
   (`BLOCK_PANIC_THRESHOLD`), not enemy stats. Decide in M2 calibration.
8. **Determinism contract:** all randomness flows through
   `CombatState.rng` (`random.Random(seed)`), fight *i* uses `seed + i`.
   `test_determinism_same_seed_identical_log` enforces it.

## M2 (2026-07-19)

9. **Pilot block valuation fixed (resolves item 7):** block cards are now
   scored by damage actually prevented this turn (capped at incoming), and
   the generic pilot's block weight moved 0.8 → **1.2**. At 1.6 the pilot
   aced SWARM/ATTRITION chip targets but lost 100% of PUNISHER fights
   (blocking a ramping enemy is a losing race) — 1.2 is the compromise.
   Pilot weights are part of the frozen calibration: changing them
   invalidates the battery.
10. **Battery calibrated and FROZEN** (all with block_w=1.2 pilot):
    - PUNISHER: 115 HP / atk 9 / ramp +2 after 3 → starter 55%.
    - SWARM: 5 × (14 HP, atk **2**) → 6.3 turns, −16.6 HP. Spec's atk 4
      (20 incoming/turn) is mathematically incompatible with the −8..−14
      target; −16.6 accepted as close enough.
    - ATTRITION: 2 × (**75** HP, ...) → 15-turn grind, −17 HP.
    - TANK BOSS: 240 HP, atk **8** / STR **+1** / **4**×3 → starter
      survives to ~turn 14 (A2 needs turn-10 data) and loses ~100% by
      design; the strength-package deck wins 78–93%.
    - BURST CHECK and GAUNTLET unchanged from spec.
    Frozen-battery regression tests in test_axes.py lock these bands.
11. **A5 normalization anchor:** starter generates zero extra draw/energy,
    so a pure ratio would divide by zero. A5 raw includes the base turn
    economy (5 draw + 3 energy = 8); score = 3.0 × (8+extra)/(8+baseline).
12. **A7 pressure delta reported, not folded into the score:** the axis
    score is setup-turns-to-1.5×-baseline-DPT only; the
    punisher-vs-attrition winrate delta prints alongside the scorecard.
13. **DPT curve exponent is negative for every Ironclad config** (late
    fight energy shifts to blocking as bosses ramp). Only relative
    comparisons are meaningful; REF_SILENT (M3) is expected to be the
    first config with a genuinely superlinear shape.
14. **Balance-shape heuristic suppressed for the baseline config** (it is
    flat 3.0 by construction; flags would be noise).

## M3 (2026-07-19)

15. **REF_SILENT validity check: PASSED on shape, softer on magnitudes.**
    Scored (500 fights): A1 2.9, A2 **5.1** (top axis, only config with a
    non-negative DPT curve exponent), A3 4.3, A4 8.0, A5 3.6 (highest of
    any config), A6 **1.8** (the weakness — no AoE), A7 5.1. The spec's
    guesses (A1≈2, A5≈4.5) land softer because the simplified 10-card
    shiv package is leaner than a real Silent engine; axis *ranking*
    matches the Silent identity, which is what the check is for.
16. **Tag-scoped damage powers:** Accuracy-like needed "shivs deal +N", so
    `tag_damage_<tag>` powers add stacks to damage of cards carrying
    `<tag>`. Generic mechanism — Klee cards may reuse it.
17. **Token cards added to hand count as A5 velocity** (a Blade-Dance shiv
    is functionally a drawn card). Tokens to discard are not counted.
18. **A1 0-cost inflation non-issue:** feared that dividing by energy
    *spent* would inflate A1 for 0-cost shiv decks; empirically Silent's
    A1 came out 2.9 (below baseline). Keeping the spec's per-energy-spent
    definition.

## M4 (2026-07-19)

19. **Reaction damage share = amplification delta + splash**, not the full
    amplified hit (the base hit would have happened anyway). Superconduct/
    Electro-Charged contributions flow through Vulnerable/DoT and are not
    attributed to reactions in v1 — the share metric slightly undercounts.
20. **Instrumentation added to every summary line** when reactions occur:
    reactions/fight, reaction damage share, and aura-starved-fight %
    (spec §8 draft-gating check).
21. **Klee placeholder validation:** reaction_package triggers 4–14
    reactions/fight, 16–27% damage share (healthy band 25–45%; low end is
    fine for placeholders), 0% starvation. demolition_package (mono-pyro)
    triggers exactly 0 reactions — Pillar 2 ("reactions are earned")
    holds mechanically; `test_mono_pyro_deck_cannot_react_alone` locks it.
22. **Archetype pilots share the frozen block weight 1.2** — only
    damage/reaction/tempo weights differ. Changing block weight in any
    pilot file invalidates the battery calibration.
23. **Klee statline (60 HP etc.) and all card numbers are placeholders**
    pending the real character doc. The smoke tests assert systems
    behavior (bombs detonate, sparks flow, no INFINITE/AMP_STACK), never
    placeholder balance numbers.
