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

## Klee pass 1 (2026-07-19, post-review)

24. **Review rulings 1-3 applied:** calibration deviations blessed as-is;
    Frozen-on-bosses stays (revisit flagged for the v0.2 Cryo/Hydro
    character); **A7 redefined self-referentially** — first turn the
    3-turn-window DPT reaches 70% of the config's OWN peak window.
    Battery/pilots untouched (not unfrozen). Regression tests added.
25. **Baseline pilot pinned to `generic` in score_config** — previously
    the baseline ran under the target's archetype pilot, silently moving
    the 3.0 anchor between runs (caught via inconsistent A7 baselines).
26. **The docs sheets are the card source of truth:** loader reads
    docs/klee-cards.yaml + docs/mondstadt-companions.yaml directly; no
    copies into tier0/content. Placeholder Klee content deleted.
27. **Full §6 DSL implemented, nothing stubbed** (incl. the companion-copy
    trio the review said could wait) — Reaction rows are readable in
    pass 1. Strict schema kept; whitelist extended (requires, star,
    role_c, personal_pool, formula fields, cost: X).
28. **Pilot bomb sequencing (review #6):** attacks resolve before new
    placements within a turn; early detonation valued at bomb damage only
    when the target dies this turn. pilot_regret instrumentation still
    deferred.
29. **Catalyst cadence implemented character-level** (element+cadence on
    Player): attacks with no explicit applies_element apply the card's
    element, falling back to the character's. Companion cards keep their
    own element. Skill-grade characters (v0.2) will simply not set it.
30. **Underspecified card numbers decided** (all in constants.py):
    Playtime Forever bomb = 5; Sparks 'n' Splash = 4x5 pyro hits/turn,
    3 turns; Oz = 3 electro end-of-turn; Durin end-of-turn hit = 4 pyro;
    Solar Isotoma = 3 block per attack-hit vs aura'd enemy, 3 turns;
    Celestial Gift = +2 attacks / 4 block; Catalytic Conversion = +1
    spark +5 burst per reaction. Amp %: multiplicative on base, additive
    with each other (melt x1.75 x1.55 = 2.71 < 4x cap).
31. **Pass 1 verdict recorded in docs/klee-pass-1-report.md** — headline:
    watchlist all clean, dream team strong-not-dominant, A1/A3/A7 near
    declared; A4/A6 metric definitions need chat-side rulings; A2-solo
    and spark-A3 are real sheet findings; Burst cards likely need Retain.

## Pass 2 (2026-07-19, round-2 rulings)

32. **All five round-2 rulings implemented:** A4 = healing/fight (Burning
    Blood anchors baseline; 0.5 floor; barbara_injection probe), A6 =
    baseline-anchored 0.7 AoE + 0.3 debuff-stacks composite, A2 early
    window 2-4 + max_stacks engine support + N_per_detonation formulas,
    Burst Retain (burst-tagged cards keep hand slot), pilot_regret.
33. **Overkill clamped in damage logs** (combat unchanged): without it,
    big single hits out-scored real AoE on A6 (Heavy Blade vs 14-HP
    swarmlings). Uniform across configs; ruling 2's ordering anchor
    (Silent < Ironclad-pkg < Klee on AoE) only holds with the clamp.
34. **pilot_regret defined as:** another playable card had strictly
    higher immediate value (expected damage + effective block/heal) at
    no greater cost. No rng consumed (determinism preserved). Caught two
    pilot bugs on first run: phantom reaction value on elemental heals,
    and a missing heal term (heals now valued like block, capped by
    missing HP). Reaction decks' residual ~25% is partly definitional
    (setup sacrifices immediate value).
35. **Pilot values the Burst payoff explicitly** (sparks_n_splash ~ 48
    expected damage): Retain alone didn't cast it — per-character burst
    cards need bespoke pilot valuation.
36. **skip_and_hop conditional experiment: NULL** (A3 4.05 -> 4.03);
    sheet reverted, residual confirmed structural. Escalated.
37. **Global common-attack shave NOT armed:** demolition tank_boss 95.4%
    (trigger was ~98%) and the band miss is a spread (spark 69%,
    reaction 2%), which a global shave would worsen. Escalated with the
    A2-knob and reaction-boss-collapse questions (see pass-2 report).

## Pass 3 (2026-07-19, round-3 rulings)

38. **Frozen-on-boss -> Vulnerable 2** (decision-2 contingency formally
    triggered). Measured consequence: reaction tank_boss 58% vs the
    trail's predicted ~37% — the hydro+cryo companion pair now sustains
    boss Vulnerable uptime. Floors met; flagged in pass-3 report for an
    optional identity ruling (co-op-primary framing vs 1-stack knob).
39. **Identity is judged on starter + archetype-deck MEDIAN** (hard
    heuristic + A1>A2), with per-deck A2 bands (demo 4.8 / spark 4.5 /
    reaction 3.5); packages themselves warn instead of fail. Monoculture
    packages are dead as identity evidence — codified from ask 4:
    **archetype test packages must model plausible drafts.**
40. **reaction_burst reconstructed** (chat-Claude's canonical list lived
    only in their clone): 6 companions, sizzle x2 / fischl x2 for early
    pressure, reworked Boom, Burst + combustion_study, 2 defense cards.
    Tuned to the stated acceptance (A2 3.4 <= 3.5, tank_boss 58% >= 35,
    gauntlet 92% >= 75), not to maximize winrate.
41. **Splash proc-cap: implemented, DORMANT.** Trigger (median A2 drag)
    did not fire; armed behavior locked by test.
42. **Spark band deviation left standing** (56% vs 65-85): 8-variant
    trail shows plausible-draft spark clusters 44-61% and block riders
    are load-bearing vs bosses (dropping them: 56 -> 44). The band was
    derived from a monoculture measurement; ratification asked, deck not
    forced.
43. **v0.1 scorecard baseline recorded in docs/klee-pass-3-report.md**;
    freezes on ratification of the two band asks.

## Errata pass (2026-07-19, pass-3 ratification + furina-predesign Part 1)

44. **Frozen v2 implemented** (principles v1.5 §2.2): non-boss Frozen no
    longer skips — the enemy's next action deals -50% damage
    (FROZEN_DAMAGE_MULT), and while Frozen the first Attack hit Shatters
    it (SHATTER_DAMAGE 6, removes Frozen). Shatter is direct HP damage
    (like reaction splash), Attack-source hits only, and a hit can never
    shatter the freeze it just applied (snapshot at pipeline entry).
    Boss path (Vulnerable 2) unchanged — the ratification kept it.
45. **control_uptime detector** (§2.2a): enemy actions = intents + sleep
    skips; a frozen ATTACK action counts (1 - FROZEN_DAMAGE_MULT) = 0.5
    negated, credited only when the freeze-triggering card was a
    companion (provenance on Enemy.frozen_by_companion). Won fights
    above CONTROL_UPTIME_CARRY (0.40) flag SUPPORT_CARRY. Under Frozen
    v2 the flag needs >80% frozen-attack uptime, so it is quiet by
    design today — it exists to police future payoff-tier stuns.
46. **Errata null result, logged as the trail demands:** solo-battery
    Frozen fires 0.01x/fight on punisher — Klee's pyro cadence consumes
    hydro/cryo auras (overload 2.4, vaporize 1.7/fight) before a freeze
    pair can meet. Pre/post-errata reaction hp-delta is identical
    (punisher -38.5 vs -38.6). The predicted elite drop nulled because
    the skip was never load-bearing SOLO; the mispricing is a co-op
    concern, now guarded by the detector + §2.2a pricing rule.
47. **Ratified winrate bands codified** in klee.yaml (winrate_bands:
    tank_boss demo 85-97 / spark 45-65 / reaction >=35; gauntlet
    reaction >=75), checked in score_character only at >=1000 fights
    (WINRATE_BAND_MIN_FIGHTS — the ratification's noise process fix).
    Matchup texture is archetype identity now, and regression-locked.
48. **Demolition tank_boss 97.4% at 1000 fights** — exceeds the widened
    97 cap; the ratification pre-registered this as "real and comes
    back." Measured the designated damper preemptively: splash proc-cap
    3 lands it at 96.5% with swarm 100 / gauntlet 99.4 unharmed. NOT
    armed (its round-3 trigger was A2 drag, not winrate); test xfailed
    pending ruling. Ask filed in docs/klee-errata-report.md.
49. **v0.1 median identity regression-locked** (test_errata.V01_MEDIAN,
    300 fights / seed 42, +-0.3): errata moved every median axis by
    <=0.05. Companion-heal Exhaust (Barbara/Bennett, sheet v0.3.1)
    loads through the existing Card.exhaust field; the barbara_injection
    A4 probe still clears its raw-healing floor, so its expectation
    needed no recalibration after all.
