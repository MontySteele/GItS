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
31. **Pass 1 verdict recorded in docs/archive/klee-pass-1-report.md** — headline:
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
43. **v0.1 scorecard baseline recorded in docs/archive/klee-pass-3-report.md**;
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
    pending ruling. Ask filed in docs/archive/klee-errata-report.md.
49. **v0.1 median identity regression-locked** (test_errata.V01_MEDIAN,
    300 fights / seed 42, +-0.3): errata moved every median axis by
    <=0.05. Companion-heal Exhaust (Barbara/Bennett, sheet v0.3.1)
    loads through the existing Card.exhaust field; the barbara_injection
    A4 probe still clears its raw-healing floor, so its expectation
    needed no recalibration after all.

## Tier 0.5 M5 (2026-07-19, tier05-draft-sim-spec.md)

50. **tier05/ package built on the Tier 0 engine untouched.** One rng
    stream per run (fight seeds, reward rolls) — determinism at run
    granularity, test-locked. Spec discrepancy logged: the template
    string is 13 nodes; §2's header says "14 nodes." Implemented the
    literal template (burst_check swapped over node 6).
51. **No card upgrades** — the spec's accepted fidelity gap, logged here
    as mandated. M5 measured it as FIRST-ORDER (see 54), not cosmetic.
52. **Lite normals are mechanical derivations** (punisher x0.70 on hp &
    attack amounts, attrition 1x45), never tuned; test asserts they track
    the frozen statlines by formula.
53. **Generic-anchor power proxy added to the assigned policy** — the
    spec's §4 scoring has no power term, and REF_IRONCLAD's untagged
    cards scored 0, so the anchor drafted NOTHING (pick rate 0%).
    Added static (damage+block)/cost for archetype=="generic" only.
    Flagged confounder-relevant; M6's mandatory A/B covers it.
54. **M5 headline finding: run completion ~0% for anchor and all
    archetypes at spec constants.** Death clustering at full-statline
    E/B nodes (the spec's predicted signature — instrument works).
    Knob trail: rest 50% -> +1.5pt; elite 85% -> deaths migrate to
    boss; both -> 3-10% with the boss killing 117/200. Cause: in-run
    decks (12-14 cards, ~60% HP) face battery checks calibrated for
    full-HP 25-card authored decks; the only power growth modeled is
    ~8 card picks. Recommendation filed (docs/archive/tier05-m5-report.md):
    run winrate is not a v1 acceptance metric; M6 harvests
    boss-reached decks into the Tier 0 battery. No unilateral tuning.
55. **Reaction achievability pre-alarm:** <1% of reaction runs assemble
    the core (2 appliers + amp payoff + Burst) from 8 screens x 1
    companion slot (demolition 26%, spark 4%). The pool-math that
    "shipped on faith" fails first contact for the archetype whose
    enablers live in the companion pool. For M6 metrics / M7 slot
    modes; no action taken.

## Triage execution (2026-07-19, errata-m5-triage.md)

56. **Splash proc-cap ARMED** (triage ruling 1): constant 3, sheet v0.4
    codifies splash_procs_per_turn on blazing_delight, drift guard in
    test_errata, xfail flipped. Re-measured: demolition tank_boss 96.5%
    at 1000 fights (in band, exactly the pre-measured value); 1000-fight
    band flags all clear; medians moved <=0.03 (V01 snapshot holds).
    Trigger definition extended per ruling: the cap is the sanctioned
    demolition ceiling knob for band violations as well as A2 drag.
57. **PROGRESSION_GAP_COMPENSATOR frozen at {normal 1.0, elite 0.8,
    boss 0.7}** (triage 3b): 48-combo grid on the anchor, winner
    confirmed 47.9% completion at 1000 runs (target 45+-10). Normals
    deliberately untouched — only the full-HP-calibrated solo gates
    (punisher/tank_boss) are compensated in run context.
58. **Draft-policy deadlock found & fixed via the ruling-4 decomposition:**
    payoff gating gated reaction's amp payoffs on a core that CONTAINS
    an amp payoff (amp assembly 1%). Fix: cards that advance the core
    are never dead picks (+3.0, regression-tested). Post-fix, full-length
    assembly: demolition 89% (watch-item resolved — truncation was the
    whole story), spark 43%, reaction 5.8%.
59. **Pity escalation executed per pre-authorization; NULL result with a
    decomposition:** pity(3)/pity(2) move reaction assembly ~0 because
    assembly = 79% appliers x 71% amp x 10% Burst — the companion slot
    was never the bottleneck. Binding constraint: sparks_n_splash is a
    1-of-15 rare at 5% odds (~10% of runs SEE the Burst). Escalated with
    options (innate Burst recommended) in docs/archive/triage-execution-report.md.
    Pity mechanism kept in-code for M7.
60. **A4 instrument replaced (R8 healing-law ruling): barbara_injection →
    sustain_probe.** The conjunctive healing law (true heal = Rare AND
    Exhausts; no 4-star companion may true-heal) converted every pool
    heal to block/meter, so a card-based A4 probe can no longer exist in
    Mondstadt. New instrument: the anchor's exempt relic trickle
    (heal_after_won_fight) injected probe-only via package_relic_hooks —
    never on starter, never in Tier 0.5 runs, leak-guarded by test.
    A4 raw for the probe changes class and magnitude (card heals
    ~10-12/fight → relic 6/fight): A4 numbers are NOT continuous across
    R8, by design. Klee solo A4 = 0.5 re-derived (still floor — now
    ecosystem-wide by law, not merely by draft).

## Furina sprint 1 redpen (2026-07-20, furina-sprint-1-redpen.md)

61. **Selector cadence does NOT count toward A5** (ruling a): the
    Ethereal Spotlight selector is kit-delivery machinery, same class as
    the kit-Burst grant — counting it would award Furina +1 card/turn by
    existing, structurally inflating A5 toward elite against her
    declared sub-elite 3.7. Implementation confirmed as ruled: emits
    `selector_granted`, never `add_card`. Kickoff §2 A5 rationale edited
    to match.
62. **Lock-retuning guardrail codified** (ruling b): small-n heuristic
    locks (like test_m5's n=40 fragility shape) MAY be retuned to
    measured-noise reality with a dated comment and disclosure in the
    next report. Ratified 1000-fight bands may NEVER be retuned this
    way — they change only by ruling, with archives. The 0.6→0.5
    majority-clustering relaxation is blessed (0.588 measured, binomial
    sd ~0.12 at n=40).
63. **Spotlight baseline (+50% relic-delivered) carried into sheet pass
    with pre-registered instrumentation** (ruling a2): the sheet-pass
    Tier 0 report MUST measure the Spotlight baseline delta —
    median-deck winrate, relic disabled vs enabled. Watch-items: the two
    AoE appliers under 1.5× (chevreuse_bursting_grenades,
    guest_neuvillette_judgment — both 7→10 all + element). Knob order if
    hot, pre-committed: (1) SPOTLIGHT_MULT, (2) selector economics
    (cost-1 to aim / effect begins next turn), (3) self-rate. Companion
    card numbers are NEVER the knob — the shared pool does not pay for
    one character's multiplier. Delete-test note: with the mult
    relic-sourced, criterion #2 genuinely bites; if boosted companions
    alone win, that signals card-mediated boosting (the Columbina
    shape), not a carve-out.
64. **EP-prototype registration held open** (ruling ask-4): prediction 2
    (duplication separates median from ceiling) is unmeasurable by the
    sprint-1 scaffolding — not failed, not confirmed. Re-test at sheet
    pass with the real Encore Performance card AND combat coupled; the
    same experiment measures the Guest Star draw-variance value that
    offer geometry cannot see. One experiment, two registrations.

## Furina sheet pass 1 (2026-07-20, furina-sheet-pass-1-plan.md)

65. **Salon ticks at the START of the player turn** (Klee-bomb timing,
    not Oz timing). Measured cause: end-of-turn upkeep drained the Encore
    buffer BEFORE enemy hits, so the DEFAULT archetype zeroed her elite
    A4 (salon deck A4 0.5-0.8 vs the 4.3 target — the constraint warn
    fired). Start-of-turn ticks let absorption take first bite; upkeep
    eats what survived the night. The overdraw identity is unchanged
    (dry buffer still drains true HP).
66. **Salon economy numbers** (all PROPOSED pending sheet red-pen):
    SALON_MEMBER_DMG 4 (may out-tick Oz's 3 — the upkeep is what Oz
    doesn't pay), SALON_TICK_ENCORE_COST 1, SALON_TICK_BURST 2,
    BURST_PER_ENCORE_SPENT 1. burst_max declared 70.
67. **Inline-upgrade schema tolerance** (coordination incident): a
    parallel M9 session added `upgrade:` fields to klee-cards.yaml rows
    mid-day, which hard-failed Card.from_dict and bricked the loader for
    every session. Card now carries an IGNORED `upgrade` field; Tier 0
    upgrades continue to load from *-upgrades.yaml via content/upgrades.py.
    The two conventions duplicate each other on the rows seen
    (sparkly_treasure/spark_collection inline entries == existing
    klee-upgrades.yaml deltas) and MUST be reconciled by ruling — flagged
    in the sheet-pass report.
68. **character_pool gains the personal-sheet filter** (tier05/rewards):
    with two personal sheets loaded, Klee's card rewards would have
    offered Furina's cards — same bug class as the Prune catch, one slot
    over. Cards tagged with another character's name are never offered.
    Guarded by test_personal_card_pools_do_not_cross_characters.

## Furina pass-1 rulings executed (2026-07-20, furina-pass1-rulings.md
## + furina-sheet-redpen.md)

69. **R16 — card-mediated boosting** (criterion-2 direction, the
    centerpiece): the empowerment moves from the relic's passive
    multiplier into her cards. The §3A decomposition decided it — the
    relic's measured value for her decks is the Ovation-Fanfare economy,
    while the damage multiplier's biggest beneficiary was the
    companions-only probe, the exact deck the delete-test convicts (the
    always-on mult was a subsidy paid to the failure mode). The relic
    keeps selector delivery, the registry, and the Ovation-Fanfare
    hooks; the passive baseline is swept over {1.0, 1.25} at pass 2;
    her commons/uncommons grant Spotlight boosts through the EXISTING
    spotlight_mult pipe (no new keyword; §2.2a numbers-only applies
    identically). Delete-test then passes by construction. The Spotlight
    card list is re-authored under this at pass 2 (deliberately NOT
    red-penned as-is, R22); salon/fanfare/basics lists are NOT gated.
    Median self-Spotlight (§3B) accepted as the depth floor working —
    re-measure the framing under card-mediation before worrying further.
70. **R17 — knobs ratified**: SPOTLIGHT_SELF_MULT 1.25 promoted from
    placeholder to MEASURED DESIGN CONSTANT (the sweep proved the
    reduced rate is the anti-self-buff lever; 1.5x companion parity
    borderline-fails criterion 1). FANFARE_CAP_FRACTION 0.5 ratified
    (re-check under R16 — Ovation economics shift). hp 60, burst_max 70
    ratified. Constants/yaml comments updated in place.
71. **R18 — A6 instrument v2 authorized** (pass-2 scope): aura uptime
    has no axis credit anywhere — the mod's core system is invisible to
    the utility axis, and every applier-identity character after Furina
    would misread the same way. A6 v2 adds an application-uptime
    component; ref_ironclad stays the 3.0 anchor (he applies nothing —
    the composite must preserve him); Klee's A6 re-derived under v2;
    numbers discontinuous BY DESIGN, labeled, old snapshots archived
    (the R8 A4-probe-v2 pattern). Co-op value staying Tier-2-invisible:
    accepted scope.
72. **R19 — A2 deck bands**: salon_weighted 7.6 and fanfare_weighted 4.2
    RATIFIED under the lag-not-growth reading (exponents 0.07–0.28; the
    ratio instrument structurally inflates A1-dreadful engines; Klee
    precedent). spotlight_weighted's band HELD until the R16 re-author —
    banding a known-broken archetype freezes the wrong world. A5/A7
    shortfalls deliberately left un-spent (their levers interact with
    R16's re-costing). Winrate bands remain PROPOSALS, not ratified.
73. **R20 — upgrade convention: separate *-upgrades.yaml sheets WIN**;
    inline `upgrade:` fields on card sheets are deprecated. Executed:
    loader tolerance promoted from silent-ignore to a loud per-sheet
    warning, plus test_no_inline_upgrades_on_docs_sheets with
    klee-cards.yaml TEMPORARILY allowlisted until the M9 session reverts
    its inline fields (their file, their revert; the deltas already live
    in klee-upgrades.yaml). WORKING AGREEMENT (standing): schema changes
    to shared loaders require a cross-session note BEFORE landing.
74. **R21 + R22 + sheet-redpen dispositions**: EP registration (i) stays
    OPEN — graded-encounter battery approved for pass 2; never summarize
    it as "EP showed no effect". Sheet red-pen: basics RATIFIED as a
    set; salon/fanfare/generic approved as measured. Executed from the
    flags: comment/number lint (tools/lint_sheet_comments.py + suite
    test) — caught exactly the predicted class (hearts_swelling "Eight"
    over 6, reginas_mercy "twelve" over 10; both fixed, plus the
    grand_gala rider-covers-upkeep arithmetic); undercurrent added to
    the hydro+cryo convergence CELL = {undercurrent, rain_of_roses,
    guest_neuvillette_judgment} — one measurement covers the full
    mass-application set. Watch items logged, no change now:
    suffering_for_art free-value (the cap governs its ceiling),
    ebb_and_flow/audience_participation as the sheet's closest twins
    (first cut if a slot is needed), universal_revelry × uncapper
    ceiling (re-check under R16), warmup_act's Crackle-parity comment
    goes stale when R10 lands. [USER] items open for the user's own
    pass: commanding_gaze mass-Weak parity, uncapper self-damage 4 vs 6,
    house_call's conditional ceiling, naming/lore audit (v1.7).
    (Resolved same day — see 75.)
75. **Red-pen [USER] items resolved from the docs** (2026-07-20, user
    directive: "all of those items should be answered in the docs").
    (a) commanding_gaze mass-Weak parity VERIFIED: Klee's ratified
    common Spooked! is 1-cost / 3 block / Weak 1 to ALL enemies;
    commanding_gaze is the same shape at 2 block — strictly not-stronger
    than an already-ratified common. KEPT at common, comment records the
    verification. (b) the_sea_is_my_stage self-damage 4 → 6: kickoff §4
    is law ("Rare uncappers at NASTY setup cost") and the red-pen's own
    analysis shows 4 fails it — blood that is itself Fanfare flux
    self-subsidizes, so the cost must overshoot to stay nasty; 6 = 10%
    of maxHP. The R16-world cap re-sweep will re-measure the archetype
    with this price in place. Upgrade keeps the blood at 6 (never
    upgrades away the law). (c) house_call KEPT at 5+3: red-pen flag 9's
    own finding — consistent with the ratified threshold family's
    flat-base + kicker grammar and priced by the A7 setup tax the
    kickoff declares (~2.0 weak by design). (d) ~~Naming/lore audit
    CLEARED per the red-pen naming section~~ **AMENDED by R29
    (2026-07-20): audit PREPARED (talent/summon names pre-verified,
    theatrical names on register, constellation namespace reserved
    §3.6) — but a document citing another document cannot close a
    [USER] gate (the v1.7 lesson). User eyes-on naming/lore pass OWED
    BEFORE SHIP; the pass itself is the closure.** (a)-(c) ratified by
    R29; veto window closed.

    > **R29d IS STILL OWED (cross-reference added 2026-07-29).** No
    > naming/lore eyes-on pass has run. The ride-along instance
    > (`lasting_impression`) was ratified 2026-07-26; the GENERAL pass
    > was not, and it is on no live playtest list -- it is desk work,
    > not table work. Tracked at `docs/missed-requirements.md` Tier 5
    > and at `docs/backlog-2026-07-29.md` §3 item 9 (the ratification
    > batch). This note records the debt at its own entry so a reader
    > of R29 cannot mistake "(a)-(c) ratified" for full closure; it
    > does NOT close anything.
76. **Strict-domination lint built** (2026-07-20, assigned via
    klee-session-worknote item 2; this session owns tools/lint_*).
    tools/lint_strict_domination.py + suite gate
    (test_sheet_lints.py) over all DOCS_CARD_SHEETS: same-cost
    cross-rarity pairs, benefits superset-with-all->= AND costs
    subset-with-all-<= (self-damage/discard/spend_encore count as
    costs — without that split the first run false-flagged three
    ratified bigger-with-a-twist shapes: hot_hands, bright_idea,
    quick_change). Basics excluded (starters are outclassed by
    design). Confirms both known hits (cant_catch_me>warm_glow —
    KNOWN, errata queued behind R10 window; pit_orchestra>
    macaron_break — KNOWN, resolves Furina pass 2). **NEW findings,
    NEEDS RULING (Klee sheet — their session's file, no edits made):**
    (a) dodge_roll (uncommon, block 8 + exhaust-a-status) strictly
    dominates hide_and_seek (common, block 7) — the CCM shape exactly;
    (b) sparkly_explosion (rare, 18 dmg + on-kill riders) strictly
    dominates big_badda_boom (common, 12 dmg) at cost 2 — may be ruled
    acceptable as rare-payoff-obsoletes-common, but the CCM law as
    stated ("rarity does not excuse strict supersets") flags it. Both
    sit in the lint's PENDING_RULING tier: printed loudly, exit stays
    0 so the shared suite doesn't go red on an unruled finding.
    NOTE: M9's inline-upgrade revert is IN THE WORKING TREE (loader
    warning silent) but uncommitted — the test_upgrades allowlist
    entry comes out only after their commit lands, to keep every
    commit green on clean checkout. (Both resolved same day — see 77.)
77. **R26 — domination law scoped to ADJACENT rarities** (2026-07-20).
    The law protects draft decisions between cards competing at
    similar weight — common<->uncommon and uncommon<->rare. Two-step
    gaps (rare over common) downgrade to informational lint lines:
    rares are the designated power spike, and a rare obsoleting a
    common's slot is the rarity ladder working. sparkly_explosion >
    big_badda_boom CLEARED under the scoped law (removed from
    PENDING_RULING; stays visible as an informational line).
    sparkly_explosion stays as-is — ratified, banded, live in C#.
    Style note for FUTURE authoring, not retroactive law: base StS
    attaches twists to big rares (Ethereal, Exhaust, wounds) rather
    than printing pure supersets; prefer that shape. dodge_roll >
    hide_and_seek is adjacent-rarity and remains PENDING_RULING.
78. **R27 — inline-upgrade allowlist dropped** (2026-07-20). The M9
    revert landed as commit 587a902; INLINE_UPGRADE_ALLOWLIST in
    test_upgrades.py is now EMPTY (its steady state) and the R20
    convention is fully enforced on every docs sheet. Sequencing
    endorsed by R27: the drop follows the revert in commit history, so
    every commit is green on clean checkout. (Origin push pending —
    interactive auth; user pushes.)

## Furina pass 2 executed (2026-07-20, R28 GO; plan + report in docs/)

79. **CORRECTION (2026-07-20, R33 — the M7 banner precedent): the
    "MEASURED at 1.0" record below is VETOED, errata-grade.** E1's
    identical cells were GUARANTEED by selector heuristic v2 (the
    companion branch is unreachable at ~20 self cards vs 3–5-card
    kits), not informative about the knob: the swept constant was
    never read in any cell. E1 is RE-SCOPED to a valid median-depth
    null; the "dead knob" generalization is struck — never summarize
    E1 as "the knob is dead." Recording 1.0 also inverted the R17
    lever (self 1.25 > companion 1.0 makes the degenerate play optimal
    BY CONSTANT). SPOTLIGHT_BASE_MULT returned to PLACEHOLDER at 1.5
    (pass-1 geometry); window-zero ceiling experiment pre-registered
    in furina-pass3-rulings.md. The R16 shipping record and the
    delete-test result below STAND — only the knob record is struck.
    **R16 card-mediated boosting SHIPPED**: spotlight_mult_bonus /
    spotlight_mult_bonus_turn / spotlight_flat_damage_turn powers read
    inside the existing spotlight_mult pipe (numbers-only inherited
    structurally). Spotlight list re-authored: limelight, stage_lights,
    top_billing in; warm_reception, props_department, constant_star
    out; shared_billing reworked. SPOTLIGHT_MULT renamed
    SPOTLIGHT_BASE_MULT and MEASURED at 1.0: the pre-registered E1
    sweep {1.0, 1.25} was cell-for-cell identical — the depth contest
    self-Spotlights at committed-median, so the companion base rate
    never fires there; 1.0 makes her cards the only companion
    empowerment at the drafted ceiling. **§8 criterion-2 delete-test
    now PASSES** (attrition +16.4pt, tank_boss +9.3pt over the
    companions-only probe; pass-1's headline FAIL reversed). Pass-1
    Spotlight numbers were taken at base 1.5 — never compare unlabeled.
80. **star_of_the_show max_stacks errata (live bug)**: the engine caps
    a power's TOTAL at max_stacks; the pass-1 row (amount 3,
    max_stacks 1) silently shipped +1. Convention codified: max_stacks
    is in POWER UNITS; single-application rows encode max_stacks ==
    amount, and the upgrade applier bumps max_stacks alongside amount
    for such rows (an upgraded row must not silently cap at the old
    value). Pass-1 self_carry cells carried the bug (punisher 38.0% ->
    49.3% post-fix, same constants). User ratification: report ask 5.
    (RATIFIED by R30, 2026-07-20 — the +3/3 encoding is what the sheet
    always said; convention codified; no sweep invalidated.)
81. **A6 INSTRUMENT v2 LANDED** (R18): application-uptime component
    (aura'd enemy intents / total intents) at 0.5 aoe + 0.3 debuff +
    0.2 uptime, uptime anchored ADDITIVELY (baseline uptime is 0).
    A6_INSTRUMENT_VERSION = 2 stamped; v1 numbers archived in the
    pass-2 report §4 table. ref anchor exactly 3.00 under v2; Klee
    re-derived 3.52 -> 3.61 median (all Klee bands hold); Furina 3.39
    -> 3.31 median. HEADLINE: the sighted instrument says her declared
    A6 4.2 is genuinely short (fanfare deck 12.7% uptime is the drag)
    — sheet-real gap, report ask 2.
82. **R21 graded-encounter EP battery RUN**: the graded ladder resolves
    pass-1's quantization; at committed depth-5, +EP scores mean 0.45
    grades / P90 1 vs warm-body control 0.57 / 2 — duplication is
    MEASURED-NEGATIVE at current cost (not "no effect"). Registration
    (i) disposition proposed to red-pen: close as measured-negative and
    re-cost Encore Performance (report ask 3).
83. **E2 cap confirmation + spotlight band**: FANFARE_CAP_FRACTION 0.5
    re-confirmed under the R16 world with the 6-blood uncapper
    (punisher 37.6%, inside the registered [10,55] band; cells match
    pass 1 — the deeper blood is invisible at deck scale, no ask).
    spotlight_weighted A2 BANDED at 4.3 (measured 4.0 + the R19/Klee
    0.3 margin) per R19's pass-2 schedule; red-pen may adjust.
    pit_orchestra errata landed (encore 2 -> 1, domination broken,
    pair removed from lint KNOWN). Winrate bands for spotlight/fanfare
    PROPOSED in report §7, not landed.

## Furina pass 3 rulings (2026-07-20, furina-pass3-rulings.md — chat-
## ratified; chat draft numbered R28–R32, renumbered R29–R33 here per
## the collision convention: R28 was already the pass-2 GO)

84. **R29 — DECISIONS 75 veto window CLOSED, with one amendment**:
    (a) commanding_gaze, (b) blood 6, (c) house_call all RATIFIED as
    resolved. (d) AMENDED — "naming audit CLEARED" struck from the 75
    record (banner in place): audit prepared; user eyes-on
    naming/lore pass owed before ship. A document citing another
    document cannot close a [USER] gate (the v1.7 lesson).
85. **R30 — star_of_the_show errata RATIFIED** (note added to entry
    80). max_stacks convention codified as law: POWER UNITS;
    single-application rows encode max_stacks == amount; applier
    bumps both. No sweep invalidated.
86. **R31 — instrument gaps resolved PATH 2: the declarations are
    DEFENDED.** Report asks 1+2 closed together against
    accept-the-world: "good at surviving" is not the identity and
    clashes with spend-buffer-for-power. A4 4.3 / A6 4.2 two-elite
    shape STANDS; the R16 measurements are design defects. Root cause
    on record: standing_ovation is a generator in the only archetype
    with NO Encore sinks (spend-line census: fanfare 7, salon 2,
    spotlight 0) — under structurally-guaranteed self-Spotlight it
    reads "2–4 Encore per card played", spend rate zero, absorption
    pools into A4 (correctly credited). Secondary: R16 glue commons
    carry BLOCK riders. Median math: A6 4.2 needs at least TWO decks
    >= 4.2 (the statistic is the middle deck of three).
87. **R33 — SPOTLIGHT_BASE_MULT 1.0 record VETOED (errata-grade)**;
    see the correction banner on entry 79. New lint-law from the
    catch (the 6th, first against a MEASUREMENT record): dead-knob
    claims require an EXERCISE COUNTER — a sweep concluding "no
    effect" must show the swept constant was read >= once per cell,
    instrument-side. E1 would have failed it loudly. Executed:
    knob-read counter in effects.spotlight_mult's companion branch +
    engine test; constant restored to PLACEHOLDER 1.5 (un-inverts the
    R17 lever; measurement-neutral TODAY precisely because the
    counter proves the branch never runs under selector v2).
    Window-zero ceiling experiment pre-registered (forced-self vs
    forced-companion, oracle-style, mult {1.25, 1.5} on the companion
    arm; R14 — diagnostics feeding a ruling, no acceptance targets).
    Selector v3 is a follow-on BEHIND window zero, full instrument
    discipline if built. "Director offstage" content hook stays on
    the user's shelf.
88. **R32 — pass-3 scope, RESEQUENCED under R33**: window zero first;
    then (1) standing_ovation FLIP generator -> spend-payoff (the A4
    lever AND identity fix; rate-tune 2->1 is fallback only), (2)
    shared_billing/stage_lights block riders -> application/debuff
    riders with an A3 rehoming check, (3) salon+spotlight A6 lift
    (two decks >= 4.2; freeze-cell steering HARD: nothing routes
    through undercurrent/rain_of_roses/guest_neuvillette_judgment).
    Fanfare saturation (A4 10.0) NOTED, NOT IN SCOPE — no touch
    without a new ruling. Binding: FANFARE_CAP re-check inside the
    pass-3 battery (E2 valid only pre-flip); Encore absorption stays
    A4-credited (content-side fix only); §7 band ratification
    DEFERRED to post-pass-3 (salon's ratified bands remain law);
    success = A4 4.3-shaped at median, A6 4.2 at median, A3 held,
    A1/A7 weaknesses intact.

## Furina pass 3 executed (2026-07-20, furina-sheet-pass-3-plan.md /
## -report.md)

89. **W0 ceiling designation experiment RUN** (R33 registration;
    tier05/exp_furina_pass3.py w0, 1000 fights/cell). Validity gates
    PASS on first use of the exercise-counter law: forced-companion
    cells read SPOTLIGHT_BASE_MULT 55k-128k times, forced-self cells
    exactly 0 — the E1 failure mode is now structurally excluded.
    RESULT: at full-kit depth (best companion 4 cards) and mult 1.5,
    forced-companion clears the registered bar (battery-mean +0.25pt)
    carried by attrition +12.5pt (85.4% -> 97.9%) against tank_boss
    -10.0pt (10.0% -> 0.0%) and punisher -1.5pt; at mult 1.25 mean
    -2.40pt (attrition niche +2.4pt survives); at depth 2 a clean no
    at both mults. READING: outward designation is REAL but
    ENCOUNTER-CONTINGENT — it wins crowds and grinds, loses duels.
    The registered consequence fired: selector v3 justified. Dose
    evidence favors 1.5 as the placeholder value (1.25 is not
    value-rational anywhere); ratification is red-pen's.
90. **Selector v3 BUILT** (registered follow-on; full instrument
    discipline: SPOTLIGHT_SELECTOR_VERSION = 3 stamped in constants
    with the v1/v2 archive note; never compare selector-v2 and v3
    numbers unlabeled). Value-aware threshold: designate the deepest
    companion iff its per-character depth >=
    SPOTLIGHT_COMPANION_DEPTH_MIN (4 = full kit; W0 brackets the
    threshold in (2, 4]) AND the stage holds >=
    SPOTLIGHT_COMPANION_MIN_ENEMIES (2) living enemies; otherwise the
    kickoff self fallback; last-resort any-companion only when zero
    self cards exist (any stage beats none). v3-world baseline
    (pre-W1, archived in pass-3 report): delete-test PASS (+7.0pt
    attrition, +9.3pt tank_boss — a HARDER bar, the probe now
    designates its own kit in crowds and reads the base mult),
    spotlight attrition 85.4% -> 95.2% (the W0 niche captured),
    tank_boss floor HELD at 10.0% (the duel protection is the point),
    salon/fanfare worlds untouched (threshold unreachable), A2 4.1
    inside the ratified 4.3 band, median A4 7.7 / A6 3.4. Both new
    constants PROPOSED pending red-pen.
91. **W1 — standing_ovation FLIP LANDED after a four-dose window**
    (R32.1; the dose record is the window's real finding). Landed row:
    ovation_spend_boost 10 (two-copy cap 20, §2.2a pipe via
    spotlight_mult_bonus_turn) + spotlight_encore_first 1 (first
    Spotlighted play each turn — activity-gated, the sheet's
    no-passive-accrual law holds). Spend lines: limelight spend_encore
    1 (overdraw op — an encore_cost gate bricked opening hands),
    top_billing encore_cost 2. DOSE RECORD: pure sink A4 2.1 (starter
    level, delete-test collapses); per-play trickle A4 9.5 with a
    REAL punisher deficit (-0.38pt at the pre-declared 4000-fight
    resolver); first-play trickle 2 A4 8.2; first-play trickle 1
    A4 4.6 -> landed. STRUCTURAL FINDING: absorption COMPOUNDS with
    survival (longer fights -> more income -> more absorption), so no
    income dose gives A4-at-declaration AND absorption-funded
    tank_boss floors simultaneously — long-fight survival must come
    from prevention texture (the R32.2/3 windows), not buffer volume.
    Engine: on-spend hook in resources.spend_encore, first-play
    window in combat.play_card; spotlight_encore (per-play) stays
    engine-supported as the archived fallback rate.
92. **W2 — rider swap EXECUTED** (R32.2): shared_billing block 4 ->
    apply_aura hydro random_enemy (single-target, freeze cell
    untouched); stage_lights block 3 -> weak 1; blocking_notes 5 -> 6
    (rehome). Measured: spotlight A4 4.2 ON the declaration; A3
    median dipped 2.4 -> 1.9 (the +1 rehome under-covered losing 7
    rider block — the axis-dip branch of the plan fired); A6 moved
    only +0.1 (single-target texture is dilute); punisher 0.5% ->
    0.0%. Upgrades re-authored (shared_billing mined cost line).
93. **W3 + final battery** (R32.3): usher_the_waves + weak 1 (salon
    debuff line), stage_lights weak -> ALL enemies (ratified mass-weak
    common grammar), blocking_notes 6 -> 7 (A3 repair; [USER] flag —
    ties Klee's Hide and Seek with a rider on top). FINAL WORLD:
    **A4 median 4.3 EXACT on the declaration** (the pass headline;
    starter 4.4 unchanged); A1 2.6 / A7 1.5 weaknesses intact; salon
    lifted for free (punisher 92.8 -> 94.3, tank_boss 61.0 -> 68.5);
    all ratified WINRATE bands hold; Klee verified; FANFARE_CAP 0.5
    re-confirmed post-flip (fanfare punisher 37.6%, the flip is
    spotlight-scoped). SHORTFALLS, quantified: A6 median 3.5 vs 4.2 —
    the term decomposition shows the debuff term nearly dead (salon
    0.14 / spotlight 0.46 / fanfare 0.09 vs the baseline's 0.90;
    ref_ironclad is a DEBUFF-HEAVY anchor, so texture-grain riders are
    ratio-invisible) and uptime near ceiling — closing it needs
    number-grain AoE/debuff volume OR an anchoring ruling (report
    ask). A3 median 1.9 vs ~2.5 (rehome under-covered; further block
    collides with Klee-parity pins — ask). A2 spotlight 4.5 exceeds
    the ratified 4.3 band (the boost-cadence world scales harder;
    re-band ask — deck bands were measured in a struck world).
    Delete-test FINAL RECORD (pre-declared 4000-fight resolver):
    attrition +7.0pt PASS, swarm level, punisher -1.85pt FAIL,
    tank_boss -0.50pt FAIL — in the A4-corrected world the machinery
    no longer buys single-target survival (the 91 coupling, at
    resolution). Disposition is red-pen's (report ask 1).

> **VOLUME POINTER (Track R-D, "Clear the Stage", 2026-08-06).** The
> **R39-R99 range** that lived at this point in the file -- 2,943 lines,
> including the interleaved D-series entries D2-D5 -- is now
> **`tier0/DECISIONS-archive-R39-R99.md`**, moved verbatim (byte-identical
> below that volume's banner; R101b -- nothing in any ruling's text changed).
> R1-R38 were never headed entries and remain not mechanically resolvable
> (queue s.4); no entries were invented. This file keeps the pre-R39 prose
> record above and R100+ below. Range -> volume table:
> `docs/registry/identifiers.md` s.3. Layout notice:
> `docs/registry/ledger-layout-note-2026-08-06.md`.

## Current-law digest (GENERATED -- do not hand-edit)

<!-- BEGIN GENERATED current-law digest -- tools/gen_decisions_digest.py -- DO NOT HAND-EDIT -->

**83 rulings across the volumes — 69 OPERATIVE, 1 OPERATIVE-NARROWED (operative, with the scope [USER] stated on the row), 13 moved by an explicit citation, 0 DOUBT.** **OPERATIVE is an absence claim** — no citable superseder was found, with the search scope recorded in the row — and not a finding that a ruling is beyond re-opening. A moved status names the citing ruling and states how much of the entry the move covers; **DOUBT** means supersession is arguable and the row is a live [USER] queue item. Statuses and evidence: `tier0/decisions-status.tsv`; the pass that set them: `docs/registry/status-pass-digest-2026-08-06.md`. Volume resolution: `docs/registry/identifiers.md` §3.

- **R39** (2026-07-21) — spark-reading effects see the bank at play time — `OPERATIVE`
- **R40** (2026-07-22) — Furina runner rulings and Salon replacement pass — `OPERATIVE`
- **R41** (2026-07-22) — Spotlight two-mode rework and spendable Fanfare — `OPERATIVE`
- **R42** (2026-07-22) — Spotlight machinery efficiency and starter-density bracket — `OPERATIVE`
- **R43** (2026-07-22) — Post-Klee companion rerun and Fontaine starter pair — `OPERATIVE`
- **R44** (2026-07-22) — Fanfare conversion diagnosis — `OPERATIVE`
- **R45** (2026-07-22) — Fanfare conversion-efficiency dose and ceiling boundary — `OPERATIVE`
- **R46** (2026-07-23) — Fanfare offer trace and targeted floor repairs — `OPERATIVE`
- **R47** (2026-07-23) — Klee second-playtest card and Burst pass — `OPERATIVE`
- **R48** (2026-07-23) — Contextual Fanfare drafting before further card buffs — `OPERATIVE`
- **R49** (2026-07-23) — Thunderous Ovation defensive converter — `OPERATIVE`
- **R50** (2026-07-23) — Dry Salon floor valve and playtest-ready aggregate — `OPERATIVE`
- **R51** (2026-07-24) — Kokomi elite axes: A2+A6, stability band owns the healer fantasy — `OPERATIVE`
- **R52** (2026-07-24) — Kokomi kickoff asks: batch closure — `OPERATIVE`
- **R53** (2026-07-24) — Kokomi basics stay at Strike parity; v0.3 committed for review — `OPERATIVE`
- **R54** (2026-07-26) — Kokomi v0.4: O4 is the primary arm, O1 rejected, O2 in reserve — `AMENDED-BY:R56`
- **R55** (2026-07-26) — Kokomi lore overlay: the rename batch and the voice law — `AMENDED-BY:R56`
- **R56** (2026-07-26) — Kokomi v0.4b: the 12-card starter, the x4 bank read, Kurage's Oath — `SUPERSEDED-BY:R73`
- **R57** (2026-07-25) — Playtest sprint Track P: pins, telemetry, and a world that moved — `OPERATIVE`
- **R58** (2026-07-25) — Kokomi v0.5 partial fill: the pool was half-sized — `OPERATIVE`
- **R59** (2026-07-25) — Shop slot 2 floor: Uncommon — `SUPERSEDED-BY:R116`
- **R60** (2026-07-25) — Base colorless pool: shop-only override now, removal deferred — `OPERATIVE`
- **R61** (2026-07-25) — The sim models the shop channel — `OPERATIVE`
- **R62** (2026-07-25) — `sucrose_astable`: free + Exhaust, restoring the v1.11a numbers — `OPERATIVE`
- **R63** (2026-07-25) — §4.7 shop channel executed: three amendments and a purse that never binds — `OPERATIVE`
- **R64** (2026-07-25) — The Featured Banner goes live — `OPERATIVE`
- **R65** (2026-07-25) — Unreleased-nation placement rule — `OPERATIVE`
- **R66** (2026-07-26) — Kokomi archetype vocabulary: the sheet is canonical — `OPERATIVE`
- **R67** (2026-07-26) — Dead-knob deletion and the sweep-harness KNOB_READS gate — `OPERATIVE`
- **R68** (2026-07-26) — Canonical cell object and mandatory run stamps — `OPERATIVE`
- **R69** (2026-07-26) — The Orobas relic upgrade is renamed "Dodoco Tales" — `OPERATIVE`
- **R70** (2026-07-26) — Manifest version policy: MAJOR.AUTO with overwrite refusal — `OPERATIVE`
- **R71** (2026-07-26) — SPOTLIGHT_BASE_MULT 1.5 and Selector v3 constants ratified — `OPERATIVE`
- **R72** (2026-07-26) — Kaboom Beetle Swarm: bombed-state snapshots at cast — `OPERATIVE`
- **R73** — `KURAGE_PULSE_PER_CHARGE` 4 -> 2 -> 3. — `OPERATIVE`
- **R74** — Ceremonial Garment loses its entry splash; pure state-entry. — `OPERATIVE`
- **R75** — Honor Guard drops the conscript, gains Exhaust, and is — `OPERATIVE`
- **R76** — Charge gauge styling + infield Kurage sprite -> animation sprint 2. — `OPERATIVE`
- **R77** — Surging Shoal 7 -> 6 (upgrade 8). Vow of the Tides CONFIRMED — `OPERATIVE`
- **R78** — Muster is a keyword. Nine cards each restated ~90 characters of — `OPERATIVE`
- **R79** — Verb-partition law, executed on the narrow (self-Exhaust) — `OPERATIVE`
- **R80** — Charge is never spent. Standing law, healing-law register. Already — `OPERATIVE`
- **R81** (2026-07-27) — Distinctness gate ratified on the two-anchor floor — `OPERATIVE`
- **R82** (2026-07-27) — Enchantments: the rider ships, the subsystem stays out, the space stays open — `OPERATIVE`
- **R83** (2026-07-27) — Pilot review ruled: weights stay PLACEHOLDER, no poison term, the scorer pass runs — `OPERATIVE`
- **R84** (2026-07-27) — DRAFTER v11 ratified; the power-aware static term and a fresh 3-act roster ordered — `AMENDED-BY:R107`
- **R85** (2026-07-27) — "Curtain Call": the register convention lands and the Furina pool takes the official shape — `OPERATIVE`
- **R86** (2026-07-27) — "Take a Bow": the Curtain Call deferral is paid off and deleted — `OPERATIVE`
- **R87** (2026-07-29) — The sweep backlog ruled: three deferrals, a rework, a DRAFTER world, and a design pass — `AMENDED-BY:R107`
- **R88** — (DRAFT -- reconstructed, needs [USER] countersign) -- Zhongli takes roster slot 4; Itto becomes Inazuma-companion eligible — `AMENDED-BY:R118`
- **R89** — ~~(DRAFT -- reconstructed, needs [USER] countersign)~~ **SIGNED 2026-08-06** -- Furina legibility: the preview-truth fix, and why the doc's own migration was the wrong one — `OPERATIVE`
- **R90** (2026-08-04) — Track A's P1 null: the lint stays a counting tool, the Fanfare question moves to Track B, the floors are re-derived — `AMENDED-BY:R118`
- **R91** (2026-08-04) — A-G1 closes: the seven entities confirmed, the salon double-credit kept with a bounded-meter property, meter-reading damage ruled, sustain bounded — `OPERATIVE`
- **R92** (2026-08-04) — Track A housekeeping: the canon count corrected, tempo_band takes its cross-session note, the support gap goes to Kokomi — `OPERATIVE`
- **R93** (2026-08-04) — Understudy policy_v1: all seven revisions approved, the card-name log elevated to a P1 blocker, the block-panic insight routed to the pilot backlog — `OPERATIVE`
- **R94** (2026-08-04) — Phase 2's default tier is amended from draft sampling to hard-state turn sampling — `OPERATIVE`
- **R95** (2026-08-04) — The seed fork: read-back seeds launch P1, chosen seeds are gated at the first cross-build comparison — `OPERATIVE`
- **R96** (2026-08-04) — The three sim observations from Phase 0 are ROUTED to their chartered streams, not opened here — `AMENDED-BY:R107`
- **R97** (2026-08-04) — Understudy housekeeping: the readiness check, the leftover run, the merge order, and the adapter-defect list — `OPERATIVE`
- **R98** (2026-08-04) — P1 is VALIDATED: the clean N=3 landed, debt #2 is deleted, and the eleventh harness defect is the same class as the other ten — `OPERATIVE`
- **R99** (2026-08-04) — The validation gate's first four items: the build ships, Punch Off is SUSPECTED-OURS, 13/14 go to the next traversal pass, and deck-intent gets both instruments — `OPERATIVE`
- **R100** (2026-08-04) — Win visibility lands on a first-party hook rather than a Harmony patch, the meters were already there, and R98 stays MECHANICAL — `OPERATIVE`
- **R101** (2026-08-05) — The S7 counter defect is confirmed and fixed at the writer, and every curve it fed is annotated rather than rewritten — `OPERATIVE`
- **R102** (2026-08-05) — The four fanfare conclusions go into escrow, in both directions, until the C2 probe reports — `DISCHARGED-BY:R113`
- **R103** (2026-08-05) — The three probes are approved in cost order, and what each one is allowed to touch — `OPERATIVE-NARROWED`
- **R104** (2026-08-05) — P1.5 is promoted to next in the Understudy queue: three demands converge on one bridge fork — `OPERATIVE`
- **R105** (2026-08-05) — The patch sentinel is accepted as shipped, and the cheapest way to shrink "not watched" is queued — `OPERATIVE`
- **R106** (2026-08-05) — The merge train is acknowledged and HELD, and its stated order is not achievable as an order — `OPERATIVE`
- **R107** (2026-08-06) — The S4 hygiene report is approved entire, and its two HIGH findings give three dangling items a governing condition again — `AMENDED-BY:R118`
- **R108** (2026-08-06) — G1 is COUNTERSIGNED: Zhongli takes roster slot 4, and the deep dive is unblocked — `AMENDED-BY:R118`
- **R109** (2026-08-06) — S13 yields two rarity laws, each arriving with a mechanical audit attached — `OPERATIVE`
- **R110** (2026-08-06) — S13's three ratified changes: Encore Performance, replay_next_companion, and the spotlight fallback — `OPERATIVE`
- **R111** (2026-08-06) — S13's other nine families: what is not changing, and what "watching" obliges — `OPERATIVE`
- **R112** (2026-08-06) — The two swarm findings are docketed, and the [USER]-side queue is restated without growing — `OPERATIVE`
- **R113** (2026-08-06) — The C2 escrow is RELEASED: the four fanfare marks are struck as instrument-vindicated, and the residual's one real term is filed — `OPERATIVE`
- **R114** (2026-08-06) — The four held flags are RULED: one intended, two ratified changes, and a curse whose root is still one word away — `OPERATIVE`
- **R115** (2026-08-06) — The fork was never evaluated, the Kokomi gates re-anchor, and a five-playtest table item becomes an instrument — `OPERATIVE`
- **R116** (2026-08-06) — S14 canonicity: five questions ruled, a register for future card work, and Errata Batch 2 is constituted — `AMENDED-BY:R117`
- **R117** (2026-08-06) — Q13/Q14/Q15 are ruled in three words, and the shop-odds rider is minted as Q16 — `OPERATIVE`
- **R118** (2026-08-06) — The sitting batch 2026-08-06(b): eleven replies execute, and R88 loses its twisted clause — `OPERATIVE`
- **R119** (2026-08-06) — Two charters are SIGNED: Class-P authority operates, and "Clear the Stage" is authorized in full — `OPERATIVE`
- **R120** (2026-08-06) — Dispatch (d): four replies execute -- the Klee rename, the art release, a staged drafter change, and probe (d)'s countersign — `OPERATIVE`
- **R121** (2026-08-06) — Dispatch (e): six replies execute -- a registration is countersigned, the anchor is shielded, the moves get a resolver, and the last three DOUBT rows resolve — `OPERATIVE`

<!-- END GENERATED current-law digest -->

## R100 -- Win visibility lands on a first-party hook rather than a Harmony patch, the meters were already there, and R98 stays MECHANICAL (2026-08-04)

Items 5-7 of the signed package
(`docs/track-b-validation-gate-countersign-2026-08-04.md`). Execution record:
`docs/sprint-track-b-gate-log-2026-08-05.md`.

**5. Win visibility -- ACCEPTED, and the seam is NOT the one the package
named.** The package authorised "Harmony-patch EndCombatInternal (or the
correct combat-end seam -- verify the actual method via local decompile, never
guess)". Verified, and the guess would have been wrong in the cheap direction:
**the game has first-party combat-end hooks, and our model already receives
them.** `CombatManager.EndCombatInternal` calls
`Hook.AfterCombatEnd(runState, combatState, room)` and then
`Hook.AfterCombatVictory(...)`, both of which walk
`runState.IterateHookListeners(combatState)` -- the same iteration that already
delivers `BeforeCombatStart` to `PlayTelemetryHooks`. So win visibility ships
as two `AbstractModel` overrides, with **no Harmony patch, no async
continuation of our own, and no new patch surface in a lockstep co-op game**.

The corollary is a correction to the record: the human feed's declared blind
spot ("the game exposes no first-party combat-END hook" --
`docs/sprint-track-b-curves-log-2026-08-04.md` and `understudy/README.md`) was
**wrong about the game, not about the consequence**. The consequence was real
-- won fights read `interrupted` -- and it is now closed.

One asymmetry stays, documented rather than papered over: the LOSS path never
runs `EndCombatInternal` (`CheckWinCondition` processes a pending loss and
returns first), so there is no combat-end hook on a death. `died` was already
exact from the player's own death, and it remains the observation that labels
it.

**6a. Furina's meters on the human feed -- ALREADY SHIPPED; this pass verified
rather than built.** `PlayTelemetry.OpenTurn` has recorded
`[round, fanfare, salon_members, salon_cap, encore]` since the Track B landing,
and `FurinaResources.Encore` reads the CustomResource directly -- which is the
whole reason the human feed can see a meter the bridge serialises as `-1`. The
item is recorded as met by run-verification. Building it twice would have been
the more expensive way of agreeing with the package.

**6b. The bridge fork is NOT authorised and was not built.** It stays P1.5
work, gated exactly where the package puts it: required before any Furina-meter
claim is graded from the BOT feed, not before.

**7. R98 stays MECHANICAL.** The pre-agreed condition was met and the debt was
struck as agreed; a ruling that grades itself upward for having been kept is
the failure mode the two-tier ledger exists to prevent. No action beyond this
line and the reversibility ledger note.

**Class: SUBSTANTIVE** for item 5 (the mod takes a new hook on the combat
lifecycle, and a published limitation is retracted). **Class: MECHANICAL** for
6a, 6b and 7.

## R101 -- The S7 counter defect is confirmed and fixed at the writer, and every curve it fed is annotated rather than rewritten (2026-08-05)

Signed package of 2026-08-05, Ruling 1 (items 1a and 1b), executed in this
pass. Audit: `docs/s7-fidelity-audit.md` and `docs/s7-classification.md`
(family A). Probe read: `docs/s7-probe-c.md`.

**No probe was needed to confirm the defect, because the log disagrees with
itself.** `fight.cards_played` under-counts the `play_card` actions **the same
writer posted in the same file**, on 139 of 139 fights. A record that
contradicts its own action stream is an instrument fault by construction; no
comparison against the engine is required to say so, and none was made.

**1a -- the footnote lands NOW, before the curves are read again.**
`docs/track-b-curves.md` carries a banner under B2 stating the defect, its
direction (**one-way undercount, never an overcount**) and its reach: every
bot-feed play-count cell in section 2 and every attribution in section 2b is
affected, because both read `cards_played`. B1's demand cells are **not**
affected -- they read telegraphed intents and the enemy HP pool and never touch
the counter -- and that was verified against `tools/track_b_curves.py` rather
than assumed. The largest single term is Furina's own most-played card: **707
Ethereal Spotlights**, granted by her starter relic once a turn, missing in
their entirety.

**1b -- the fix is one defect at the writer, and history is annotated rather
than regenerated.** `understudy/soak.py` now records a play on the state it was
decided against instead of on the state the game happened to land in
afterwards. Four tests pin it. **No historical row is rewritten**: the numbers
on record stay exactly as measured and carry the banner instead. Rewriting them
would replace a measured number with a reconstructed one and lose the fact that
the corpus behind them no longer exists in one piece.

The C# writer (`klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs`) does **not**
share the defect -- it counts off the game's own `AfterCardPlayed` hook -- so
nothing is owed to a build here.

**Class: MECHANICAL.** An instrument is repaired and a published table is
annotated. No balance value, card, floor, tag or grade moves under this entry.

## R102 -- The four fanfare conclusions go into escrow, in both directions, until the C2 probe reports (2026-08-05)

Signed package of 2026-08-05, Ruling 2. Trigger: family C2 of
`docs/s7-classification.md` -- a candidate infidelity in tier0's Fanfare
accounting, direction "tier0 pessimistic", **unconfirmed**.

**The four conclusions the classification names are marked PROVISIONAL --
instrument under audit (R102, C2 escrow):**

1. the threshold-reach table (94.1% at 10, 80.8% at 15, 64.8% at 20, 40.8% at
   the cap) -- R44, annotated in place;
2. the compensation STOP at 1.8% against the 2.0% floor -- R87(1), annotated in
   place;
3. the Fanfare early-half grade "prediction NOT SUPPORTED" --
   `docs/sprint-track-b-gate-log-2026-08-05.md` GRADE (a), annotated in place;
4. the R91/2b revisit posture -- R99(4), annotated in place.

**PROVISIONAL means: not citable as load-bearing, not shipped against, AND not
redesigned against.** Nothing moves in either direction until the C2 probe
reports. If C2 confirms, those items re-open formally, each with its own
re-grade against the corrected sim. If C2 is written off, the PROVISIONAL marks
are struck and the grades stand exactly as ratified. Either outcome is one
clean ledger operation.

**The principle, recorded once for reuse:** a binding null presumes a sound
instrument; a confirmed instrument defect re-opens what it graded -- a
suspected one escrows it.

**Class: SUBSTANTIVE.** Four ratified conclusions change status. None changes
value, and the escrow is symmetric on purpose: an audit that could only ever
loosen a verdict is not an audit.

## R103 -- The three probes are approved in cost order, and what each one is allowed to touch (2026-08-05)

Signed package of 2026-08-05, Ruling 3. Candidates as filed in
`docs/s7-classification.md` section 4.

**(c) The granted-cards writer read goes FIRST**, because it settles the
mechanism of R101's fix and costs a code read. **Done in this pass**:
`docs/s7-probe-c.md`. It reports one gate, not the hypothesised deck-residency
key.

**(a) The no-relic scripted block fight goes next**, to discriminate C1 (the +2
block offset). Its exposure is written down before it runs, so the result
cannot be read wider than it is: **relative arm comparisons survive C1 either
way** -- a symmetric over-block moves every arm together -- and **absolute
floor rulings inherit PROVISIONAL only if C1 confirms**. Nothing is escrowed on
C1's account today.

**(b) The selector-recorded fanfare trace is GATED on P1.5** (R104). It cannot
run before the bridge records the Center Stage / Guest Cast choice, because
that choice is the channel the reconstruction is blind to.

**Class: MECHANICAL.** A work order, in an order, with its exposure declared.

## R104 -- P1.5 is promoted to next in the Understudy queue: three demands converge on one bridge fork (2026-08-05)

Signed package of 2026-08-05, Ruling 4. P1.5 was gated at "the first cross-build
comparison" (R95, restated by R100/6b). **It is now NEXT in the Understudy
queue**, because three independent demands land on the same fork:

1. **chosen seeds** -- the same seed on two builds, one variable per
   measurement window (R95's original gate);
2. **resource/meter visibility on the wire** -- required before any
   Furina-meter claim is graded from the BOT feed (R100/6b's condition, still
   binding);
3. **selector recording** -- the C2 probe (R103(b)) and family B's blind turn-1
   fanfare channel both need the Center Stage / Guest Cast choice on the wire.

**One work item, three payoffs. The scope does not grow with the promotion**:
it stays the fork as previously described, and nothing rides along. Queue sites
updated: `docs/backlog-2026-07-29.md`,
`docs/sprint-understudy-p1-log-2026-08-04.md`,
`docs/sprint-track-b-gate-log-2026-08-05.md`, `understudy/soak.py`.

**Class: MECHANICAL.** A priority moves; no scope and no design moves with it.

## R105 -- The patch sentinel is accepted as shipped, and the cheapest way to shrink "not watched" is queued (2026-08-05)

Signed package of 2026-08-05, Ruling 5. **S12's sentinel
(`tools/patch_sentinel.py`, `docs/patch-sentinel.md`) is ACCEPTED as shipped**
-- it is this repo's standing answer to a silent defect class: the baseline
stops describing the shipped game and nothing fails. It arrives with the merge
train (R106), not with this entry.

**One queued item, next local session:** `char_facts` baselines for the three
characters that have a card baseline and no character one -- Defect,
Necrobinder and Regent. The sentinel's `characters` surface watches only the
two that have one and reports the rest as "not watched" rather than as clean.
The item is cheap, it is not a design question, and every fact sheet it adds
converts a note into a check. Filed in `docs/backlog-2026-07-29.md`.

**Class: MECHANICAL.** An acceptance and a queue entry.

## R106 -- The merge train is acknowledged and HELD, and its stated order is not achievable as an order (2026-08-05)

Signed package of 2026-08-05, Ruling 6 -- acknowledged, **not run by this
pass**. The train waits on S14 closing remotely.

**The discovered topology, recorded because it changes what "S15 first" can
mean.** The cloud streams are **not** one branch per stream: S1, S6, S8, S9,
S10, S11, S13 and S15 are all **sequential commits on a single branch**,
`claude/surplus-week-dispatch-lg7k0c`, interleaved in the order they were
written -- S15's four partials sit below S13's tip, with S11's atlas commits
threaded between S1's. There is no commit range that isolates one stream
without rewriting history. **Consequence: the whole branch merges as one unit
once S14 closes**, and "S15 first" is already satisfied by where S15 sits on it
rather than by a merge order anyone can choose. The local findings branches
(`review/s7-fidelity-audit`, `review/s12-patch-sentinel`,
`review/enemy-dossiers`, `review/s5-animation-peek`) are separate and do merge
in a chosen order; S7 stays last, adjacent to the B2 footnote this pass landed.

**Class: MECHANICAL.** Nothing merged, nothing pushed; a plan meets the shape of
the thing it plans over.

## R107 -- The S4 hygiene report is approved entire, and its two HIGH findings give three dangling items a governing condition again (2026-08-06)

Sitting of 2026-08-06, section 1. Source: `review/ledger-audit/hygiene-report.md`
(S4 -- seventeen findings F1-F17, 2 HIGH / 8 MEDIUM / 7 LOW, "STRICTLY
READ-ONLY -- nothing was amended; every resolution below is PROPOSED, NOT
EXECUTED"). Transcript of the sitting: `docs/sitting-record-predraft-2026-08-06.md`.

**Verbatim: "F1-F17 approved as proposed."** All seventeen repairs are approved
AS PROPOSED and unlocked for mechanical execution -- the strikes, banners and
cross-references exactly as each finding's own PROPOSED paragraph words them.
Nothing wider is authorised by this entry: approving a proposal approves *that*
proposal, and where a proposal's text does not say what to change, the repair
does not happen and is reported back rather than guessed.

**F1 -- the Furina deferral chain gets a governing condition back.** R87(1)'s
trigger (the Furina playtest) fired, and the condition it converted into (the
Track A lint finding fanfare floors to fill toward) can never be met, because
the lint found none and R90/1b moved the question out of Track A entirely.
Backlog items 1-3 -- strength lever + legibility, dead-archetype question,
salon leak -- and **the fanfare STOP** therefore **re-point to Track B /
B-G1**, as F1 proposes. This is a re-pointing of a condition, not a release:
the STOP holds, and it now holds against a gate that can actually discharge it.

**F2 + G8 -- the Gallery Stirs fixture re-homes, and the owed DRAFTER 13 entry
lands as ratified.** The acceptance fixture ("DRAFTER 13 is not done while The
Gallery Stirs scores 0.0 at offer", R96 item 1) was bound to a stream whose
mechanism cannot clear it: the zero comes from `_static_power`'s power-name
blindness, not from the op enumeration D13 repaired. It **re-homes to the
`_static_power` repricing session**, where R96 item 2 already sits. **G8 is
DISCHARGED** by clause (a) below.

**(a) The DRAFTER 13 repricing entry, owed since 2026-07-29, is written here
rather than as a new D-number** -- the D-series in this file is the difficulty
series (D2-D5) and "D13" in the sim-hygiene log is a DRAFTER world stamp; two
numbering systems sharing a token is exactly the hygiene F2 exists to stop.
RATIFIED as measured: `tier05/draft.py::STATIC_OP_PRICING` classifies **all 56
engine ops** (`lint_op_parity`: "56 registered ops, 56 priced"), taking cards
priced at exactly 0.0 by the offer-time scorer from **187 of 461 to 133** --
**54 cards became visible to the drafter**. World stamp `RT7 / D13 / P3 / C4`,
landed 2026-07-29, `tier0/constants.py` `DRAFTER_VERSION = 13`. The PROPOSED
mark is lifted from the repricing and from the paired D12/D13 roster-anchor
columns **as measurements**. What is NOT ratified, because the repo already
corrected it: the n=600 table's per-arm deltas. The n=3000 re-read on seed
20260729 found the fanfare "+1.0" to be **-0.1** and every other arm consistent
with zero. The honest ratified finding is the one that survived five times the
sample -- **the repricing made 54 cards visible and bought no measurable run
winrate anywhere**.

**(b) Historical rows are annotated, never rewritten** (R101b). Every F-repair
that touches a landed number or a superseded claim lands as strikethrough plus
a dated banner carrying the correcting reference. No measured value is edited
into a different value anywhere in this batch.

**Class: SUBSTANTIVE** for F1's re-pointed governing condition and F2(a)'s
ratification of the DRAFTER 13 repricing. **Class: MECHANICAL** for the other
fifteen repairs, which move paper and no value.

## R108 -- G1 is COUNTERSIGNED: Zhongli takes roster slot 4, and the deep dive is unblocked (2026-08-06)

Sitting of 2026-08-06, section 2. **Verbatim: "Zhongli for slot 4."**

R88 has stood in DRAFT since 2026-07-29 ("reconstructed, needs [USER]
countersign") and was the recorded blocker on the Zhongli deep dive -- S4's
gate G1. It is **countersigned**: Zhongli takes roster slot 4, and R88's
eligibility record is resolved with it.

**The deep dive is unblocked but NOT scheduled.** Track J's dossier
(`docs/zhongli-dossier-2026-08-05.md` -- canon kit inventory, StS2/Downfall
precedent scan, open questions, the Crystallize fence honored) is on main and
is the session's opening exhibit. Scheduling is [USER]'s, post-week-off.
Nothing in the kit is decided here: a slot is filled, not a character designed.

**Class: SUBSTANTIVE.** A DRAFT ruling becomes law and a roster slot is
occupied.

> **ADDENDUM CLAUSE, 2026-08-06 -- Itto's disposition is settled, and it is not
> a slot.** Second sitting of 2026-08-06 (sixth-wave brief, Track Y item Y-5;
> transcribed verbatim at `docs/sitting-record-predraft-2026-08-06.md` §7).
>
> **Verbatim: "Itto enters as a COMPANION CARD, not a character."**
>
> R108 above filled slot 4 and, in doing so, left Itto's status inferred rather
> than stated: R88's record has him losing the Itto-vs-Zhongli item and being
> "released to the companion pool" by the reserved-character rule read in
> reverse, which is an inference from a rule that is itself in tension with
> ratified R52 (`docs/slot5-candidates-2026-08-05.md` §2.2/§2.3, caveat [J1]).
> This clause replaces the inference with a ruling: **Itto's registration is
> COMPANION CARD.** He is not a playable character, he holds no roster slot, and
> he is not a slot-5 candidate.
>
> **What this clause does NOT do.** It does not draft a card -- **no card is
> drafted tonight**, no rarity is assigned, no kit is designed, and nothing is
> added to `docs/inazuma-companions.yaml` beyond what already ships there. It
> does not resolve the R88-vs-R52 tension over the reserved-character rule
> generally; it settles ONE name, by direct ruling, so that the tension can no
> longer be load-bearing for Itto specifically. And it does not disturb R108's
> own subject: Zhongli still holds slot 4.
>
> Cross-noted, dated, at `docs/slot5-candidates-2026-08-05.md` §2.3 and §2.5.

> **DATED NOTE, 2026-08-06 (R118, §5 row 10.8).** The addendum above stands
> unchanged. Its "released to the companion pool" justification — inherited
> from R88's reserved-character rule read in reverse — is **superseded by the
> cleaner principle**: [USER], verbatim, *"A character may be playable and
> still have a companion card."* Release was never needed. Nothing is
> re-decided by this note; Itto's registration is COMPANION CARD as ruled.

## R109 -- S13 yields two rarity laws, each arriving with a mechanical audit attached (2026-08-06)

Sitting of 2026-08-06, section 3, families X2 and X7. Source:
`review/redteam/exploit-ledger.md` (71 lines, 71/71 replay-verified, 14
mechanism families). Pins: `tier0/tests/test_s13_exploit_pins.py`.

**X2 -- self-replacing 0-cost companions. Verbatim: "Not a problem; power in
line with existing Uncommon Colorless... infinite cycling engines gated to
Uncommon rarity or higher. If this is Common, it needs a bump."**

NEW LAW, stated as the verdict states it: **an infinite cycling engine is gated
to Uncommon rarity or higher.** A card that is hand- and energy-neutral and
replaces itself is a cycling engine whatever else it does. MECHANICAL AUDIT
attached: rarity check on `sayu_naptime` and on every self-replacing 0-cost
non-exhaust companion in the committed pools; Common instances are **flagged
for a rarity bump**, not bumped by the auditor -- the audit reports, the bump
is priced where bumps get priced.

**X7 -- the Klee spark economy. Verbatim: "Gate repeatable spark generation
behind Uncommon or make sure no card below Rare is both 'sparks + draw
enabler'"**

NEW LAW, and the disjunction is load-bearing and is preserved as stated: EITHER
repeatable spark generation sits at Uncommon or higher, OR no card below Rare
is simultaneously a spark source and a draw enabler. Two ways to satisfy it;
the law is not silently collapsed to one. MECHANICAL AUDIT attached: a sweep of
the Klee pool for cards violating both limbs, findings to the Klee-rework
docket (`docs/dockets/klee-rework.md`).

**Neither audit is run by this entry, and neither audit may fix what it finds.**
An audit that repaired its own findings would be a design session wearing a
checklist. Findings land in the docket; the bumps are a sitting item.

**Class: SUBSTANTIVE.** Two standing laws enter the constitution's orbit; no
card value moves under this entry.

> **[USER] ANNOTATION 2026-08-06 -- X7 limb (a), the reading is fixed.** The
> audit returned two counts for limb (a) and asked which reading the law meant
> (broad = 6 Common violations, strict = 0;
> `docs/track-t-audits-2026-08-06.md` §T-2.2, open one-liner (4) of
> `docs/surplus-week-manifest-2026-08-05.md`). **Verbatim: "infinite sparks
> must not be achievable at Common" -- some Common spark generation is fine.**
>
> The original text above is unchanged (R101b: annotate, never rewrite). What
> this annotation settles is the CRITERION, not the count: limb (a) is not a
> ban on Commons that mint sparks, and it is not the strict loop-only reading
> either. It is an **unboundedness** test. A Common spark card violates limb
> (a) when some Common-or-lower deck reaches UNBOUNDED spark generation with
> it; a Common that mints sparks against a real bound does not violate.
>
> **Re-read executed 2026-08-06 (Track W)** against exactly that criterion,
> by the S13 evidentiary standard: a candidate is a violation only where a
> committed, replay-verified line demonstrates the infinite on a Common-or-
> lower deck. Lines: `review/redteam/exploit-lines-x7a.json`, results
> `review/redteam/replay-results-x7a.json`. Verdicts and the bound that clears
> each survivor: `docs/dockets/klee-rework.md` §2b. **3 violations**
> (`crackle`, `skip_and_hop`, `sparkly_treasure` -- the 0-cost Commons),
> **3 cleared** (`snap`, `spark_collection`, `warm_glow` -- the 1-cost
> Commons, bounded by the energy budget). Findings only; no card moved, and
> the audit still may not fix what it finds.

## R110 -- S13's three ratified changes: Encore Performance, replay_next_companion, and the spotlight fallback (2026-08-06)

Sitting of 2026-08-06, section 3, families X3, X11 and X14. Each is a RATIFIED
CHANGE: the verdict names the fix, so there is nothing left to decide and
everything left to implement.

**X3 -- Encore Performance closes over itself. Verbatim: "Remove the energy
rider and make it free to play instead."**

Card-sheet change: the upgrade **loses `copy_cost_override: 0`**, and the base
card **becomes 0-cost**. The energy-positive loop dies with the rider; the card
keeps its identity by being free rather than by paying itself back.

**X11 -- replay_next_companion stacking. Verbatim: "Cap those effects to 'same
turn only'"**

The counter is **scoped to the turn**. Write-side or spend-side is the
implementer's call, decided by a parity check against the C# mod, because the
two engines must agree on where the scope lives and neither reading is a design
question. The Study Buddy / Duet parity twins are **both** covered -- they
write one counter, so one scope closes both.

**X14 leg (b) -- ethereal-spotlight starvation. Verbatim: "Add a fallback: if
the hand is full, one random card is discarded before the spotlight is
added."**

RATIFIED for **leg (b) only**. The relic that exists to guarantee Furina a play
stops being the thing a full hand starves.

**HELD -- FLAG-2 (X3's two adjacent closures).** The ruling cleanly kills the
energy-positive loop; two closures in the same family remain undisposed and are
recorded here as questions, not as work:
  (i) a copied `sucrose_catalyst_conversion` regenerates faster than its
      Exhaust bound removes it -- the sheet's stated bound is deleted by the
      copy op. Whether the copy op should respect printed bounds is a design
      call and is HELD.
  (ii) `cost_override` writes to the card instance with no turn scoping, so
      "temporary" 0-cost copies are permanently free (S14 cross-ledger: this
      rides a known parity defect). It reads as a straight bug with an
      unambiguous fix -- turn-scope the override -- and becomes mechanical the
      moment it is blessed. It is not blessed yet. HELD.

**HELD -- FLAG-4 (X14's other two legs).** Leg (a): `curse_poor_sleep` is typed
both `status` (unplayable) and `retain: true` (unflushable), so ten copies are
a permanent hand jam -- this looks like a data-typo-class bug, a curse that
retains forever. Leg (c): Powers route to `result_pile: none`, so an all-Power
deck erases itself into 27 empty turns -- this may be intended StS-like
behaviour. One-line verdict each is requested; neither is probed, pre-drafted
or fixed here.

**Class: SUBSTANTIVE.** Three card/engine behaviours are ruled changed. The
held legs change nothing until they are ruled.

## R111 -- S13's other nine families: what is not changing, and what "watching" obliges (2026-08-06)

Sitting of 2026-08-06, section 3, families X1, X4, X5, X6, X8, X9, X10, X12,
X13. Verdicts verbatim; routing is this entry's.

**X1 -- the companion cost-delta accumulator. Verbatim: "Let's make a note of
this for the Klee rework"** -- NOTE, to `docs/dockets/klee-rework.md`. **See
FLAG-1, HELD, below.**

**X4 -- Guest Cast unfiltered 1.5x. Verbatim: "Seems totally fine as a
damage-boosting power... may need to limit to 'damage only' if the block
scaling gets absurd."** -- WATCH ITEM. Revisit trigger, as stated: **the block
side getting absurd.** The telemetry that would show it is block-side Guest
Cast readings; the register entry names the reading so the trigger is
falsifiable rather than a feeling.

**X5 -- fanfare floor stacking. Verbatim: "Likewise seems fine; cycling at
uncommon does not feel problematic."** -- **HELD FOR CLARIFICATION, FLAG-3.**
Nothing is executed, probed or pre-drafted on X5 by this batch.

**X6 -- salon displacement double-pay. Verbatim: "As a strategy, totally fine
(Defect does the exact same thing) -- it's the power level we need to watch."**
-- WATCH ITEM. The strategy is blessed; the **power level** is the watched
quantity, and that is the distinction the register entry records.

**X8 -- bomb damage, two uncapped terms. Verbatim: "Not a problem at higher
rarity -- need to check these cards."** -- MECHANICAL AUDIT: rarity check on
the carrier cards of both terms; findings to the Klee-rework docket.

**X9 -- the Kokomi charge bank. Verbatim: "Probably too strong as-is and needs
to be parsed carefully. Review during the next kit workshop."** -- NOTE to the
Kokomi kit-workshop / pool-rework docket, which is already queued third. Not
opened early: the verdict names the venue.

**X10 -- the Metallicize treadmill. Verbatim: "10 of the same Companion at
common seems exceptionally unlikely. May be worth moving to Uncommon and
adjusting power up."** -- **CANDIDATE, NOT RATIFIED.** "May be worth" is not a
ratification, and this entry does not upgrade it into one. Filed to the
companion-pricing docket as a candidate: `gorou_heart_of_the_clan` Uncommon
promotion plus a power adjustment, **priced at a sitting**, not here.

**X12 -- cross-element reaction splashes. Verbatim: "Seems probably fine; half
the fun of co-op. Check actual potency in co-op playthroughs."** -- WATCH ITEM,
with an instrument caveat: the Track H reactions corpus is the instrument, and
it is not usable for this until its denominator defect (O-1, see R112) is
repaired and the corpus re-read.

**X13 -- the 14-relic weakness eraser. Verbatim: "Also seems fine; odds of a
specific relic combo are low."** -- **NO ACTION.** The finding's open
drop-rate question is recorded as **answered by judgment**: the odds argument
is the answer, and no drop-rate measurement is owed.

**HELD -- FLAG-1 (X1's second enabler).** The accumulator has two run-plausible
enablers riding one piece of shared uncapped state
(`companion_cost_delta_this_turn`): Klee's `friendly_visit` (common) **and**
Kokomi's `honor_guard` (printed 0-cost). A Klee-rework-only note leaves the
Kokomi leg live. Questions, held: should the note also ride the Kokomi
pool-rework docket, and/or should the accumulator itself -- shared machinery,
uncapped, floored at 0 -- take a structural disposition at a systems session?
Recorded, not answered.

**HELD -- FLAG-3 (what X5's verdict covers).** The verdict's language ("cycling
at uncommon") maps onto the family's *cantrip leg* -- upgraded `tempo_change`,
cost 1, draw 2, +1 refund, infinite. The family's core is different machinery:
**stacked fanfare floors permanently delete the 20%/turn decay that is the
meter's only sink** (one-card 240, turn-2 boss kill, unloseable stall, turn-3
boss kill on commons-only income). Question: does "seems fine" cover the
decay-proof floor stacking, or only the cantrip leg? Held rather than guessed,
per the no-supplied-assumptions norm.

**What a WATCH ITEM is, recorded once for reuse.** It is not a deferral and not
a queue entry. It is a blessing of the mechanism plus a named quantity and a
named trigger: the item does not come back until the trigger fires, and when it
fires it comes back with a reading, not with an argument.

**Class: SUBSTANTIVE** for X13's no-action and for the four blessings that
close their families. **Class: MECHANICAL** for the notes, the routings and the
register. No number moves anywhere in this entry.

## R112 -- The two swarm findings are docketed, and the [USER]-side queue is restated without growing (2026-08-06)

Sitting of 2026-08-06, sections 5 and 6. **No verdicts were requested on either
finding**, and none is recorded here; this entry exists so neither is lost.

**O-1 (instrument, HIGH) -- the reactions corpus denominator.** `run_battery`
merges the gauntlet's two stages into one `FightStats` while rates divide by
records, so **every published Track H per-fight reaction rate overstates**:
all-row aura applications per fight **7.70 -> 6.60, an overstatement of
16.7%**. The defect is unambiguous, so the repair and a corrected corpus
re-read are **MECHANICAL** and queued as such, pinned per the Track K idiom. It
is also the blocking dependency on X12's watch item (R111), which is why the
two are cross-referenced in both directions.

**N-1 (lore, HIGH) -- a live miss inside a verified set.** The `gorget` gallery
rationale cites Concealed Unguis as Bathysmal Vishap material; it is a Riftwolf
drop (The Chasm). The retroactive audit found what the original S8 pass
cleared, which is the interesting half: a verified set is a claim about a pass,
not about a fact. Routed to [USER]'s N-ledger review with the other four
TOP-5s. **This batch does not repair N-ledger lore**, by standing instruction.

**Carried on [USER]'s side, restated, not grown:** the R102 escrow countersign
(pre-draft ready, one strike operation); the S2 event-gallery checkboxes; the
S14 canonicity rulings (NC-1, shop slot 1, Frozen, `spend_potion`); the G6
Kokomi stability-band declaration; the four merge-train paperwork one-liners;
the N/O TOP-5 review; the Ancients and boss-pool galleries whenever inspiration
strikes. Nothing was added to this list by the sitting, and nothing was
silently dropped from it.

**Class: MECHANICAL.** Two findings take a docket and a queue is copied
forward. Nothing is graded, priced or decided.

## R113 -- The C2 escrow is RELEASED: the four fanfare marks are struck as instrument-vindicated, and the residual's one real term is filed (2026-08-06)

Sitting of 2026-08-06, third sitting, Track AA. **Verbatim: *"agreed -
signed."*** Recorded before execution
(`docs/sitting-record-predraft-2026-08-06.md` §8).

R102 escrowed four conclusions "in both directions, until the C2 probe
reports", and stated its own two outcomes: **if C2 confirms, they re-open; if
C2 is written off, the PROVISIONAL marks are struck and the grades stand
exactly as ratified.** Both probes have reported
(`docs/probe-a-block-offset.md`, `docs/probe-b-fanfare-residual.md`;
`docs/sitting-prep-2026-08-05.md` §10.11). **C2 is written off as a family-C
infidelity**, so the second branch is the one that fires. This entry fires it.

**The four PROVISIONAL marks are STRUCK, and the grades stand exactly as
ratified.** Enumerated here in R102's own order and words, so the strike cannot
be read as covering more or less than the escrow did:

1. **the threshold-reach table** (94.1% at 10, 80.8% at 15, 64.8% at 20, 40.8%
   at the cap) -- R44, banner struck in place;
2. **the compensation STOP at 1.8%** against the 2.0% floor -- R87(1), banner
   struck in place;
3. **the Fanfare early-half grade "prediction NOT SUPPORTED"** --
   `docs/sprint-track-b-gate-log-2026-08-05.md` GRADE (a), banner struck in
   place;
4. **the R91/2b revisit posture** -- R99(4), banner struck in place.

**No number moves and no grade is re-read upward.** A strike restores the
status these four had before the escrow; it is not a re-ratification and it is
not new evidence for any of them. What the probe supplies is the negative:
tier0's Fanfare generation and decay are at parity, so the instrument that
produced them was sound, so the escrow's condition is discharged.

### Companion clauses C-a ... C-d

**C-a -- term 3 is filed to the S7 ledger as bounded and direction-known, and
its fix is QUEUEABLE, not executed.** Probe (b) localized the residual into
three terms: (1) the unrecorded Spotlight selector -- a family-B reconstruction
gap, not a sim fact; (2) the turn-open sampling seam; (3) **the fight's first
Spotlight -- tier0 credits the play that SETS the designation, the engine does
not: exactly +2 Fanfare per combat, once, in tier0's favour**
(`docs/probe-b-fanfare-residual.md` Ledger 2, 26 of 27 plays agree exactly).
Term 3 is the only genuine tier0-side term, it is **bounded** (+2/fight) and
its **direction is known** (tier0-optimistic, the opposite of the direction
R102 worried about). It is filed to `docs/s7-classification.md` family C as a
named, bounded, direction-known item. **The fix candidate -- credit only plays
covered by a standing designation -- is formally QUEUEABLE and joins the next
errata batch as item 1** (Errata Batch 2, §10 of the sitting record). It is
not executed by this entry and no constant, card or sheet moves under it.

**C-b -- the blind-replay column re-read rule.** Any S7 column produced by a
reconstruction that did **not** carry the recorded status strip and the
recorded Spotlight selector is a **reconstruction reading, not a fidelity
reading**, and may not be cited as evidence of a tier0 infidelity without being
re-read selector-aware and status-loaded first. Named instances, because a rule
with no instances is a slogan: `l2.block_at_turn_end` (probe (a): "the S7
`l2.block_at_turn_end` column should be read that way"; 7/38 -> 33/38 agreement
once status-loaded), and `l2.fanfare_after_turn` /
`l2.fanfare_next_open_post_decay` (probe (b): both "compare across a seam
containing two income channels the replayed turn does not contain", and neither
is the fair column S7 was looking for). The rule is stated once here so it does
not have to be re-derived at every future citation.

**C-c -- S13 re-verification against `S7-C1`/`S7-C2`: NO.** The 71-line S13
corpus is **not** re-verified, and the caveat stands as written. Attached as the
evidence, per the order this clause carried: the **Family-A dependency scan
returned zero hits** (`docs/sitting-prep-2026-08-05.md` §10.12) -- no S13
metric verdict quotes `cards_played` or anything derived from it; the 40 metric
verdicts use seven other metric names, and the remaining 31 read the engine's
own degeneracy detector. The structural reason is recorded with it: Family A is
a defect in the soak writer, and the S13 harness never loads it. **This clause
discharges two open asks at once** -- `docs/sitting-prep-2026-08-05.md` §10.12
("accept the null as closing the C-c order": accepted, no wider derivation test
is ordered) and paperwork one-liner 4 of §8 / `docs/registry/user-queue.md` §6
("proceed on the caveat as written").

**C-d -- the probes' standing limits are carried onto the annotations.** The
strike is only as wide as the measurement behind it, so the measurement's own
declared limits ride with it wherever a struck mark is now cited: **bot-limited**
(Guardrail 7 -- every engine number came from a bot or a fixed script; nothing
in either probe is a balance finding); **salon empty throughout** (every
`salon_members` reading is 0, as in every measurement to date -- Fanfare
interactions with a populated salon are untested); **one character** (Furina
only); and **the Encore split is unreadable on this wire** (absorption vs
upkeep, bounding the boundary reconciliation at +/-2). A struck mark is a mark
that is no longer frozen. It is not a mark that has been re-measured on a
broader corpus.

### What was reconstructed, and from what

Track AA's text cites a pre-draft, `ruling-predraft-r102-escrow-2026-08-05.md`,
**which does not exist in this repo on any branch.** Recorded rather than
smoothed over, because a ruling that cites a missing source should say so. The
clauses above are reconstructed from the paper that does exist, and each names
its source: the enumeration of the four marks from **R102's own text**
(verified word-for-word against it, and against probe (b)'s "For the ruling
session" restatement); C-a from **probe (b) Ledger 2** and the sitting record's
Errata Batch 2; C-b from **probe (a)'s closing section** and **probe (b)'s
"Mechanically, what it means"**; C-c from **§10.12** and its grep manifest;
C-d from **both probes' declared confounder sections**. No clause was invented,
and nothing in the brief's C-a...C-d parenthetical is left unlanded.

**Class: SUBSTANTIVE.** Four ratified conclusions change status, in the
direction R102 pre-committed to. **No value moves anywhere in this entry**, and
the one real defect the probes found is filed and queued rather than fixed.

## R114 -- The four held flags are RULED: one intended, two ratified changes, and a curse whose root is still one word away (2026-08-06)

Sitting of 2026-08-06, third and fourth sittings, Track AB. Verdicts verbatim;
routing is this entry's. FLAG-1...FLAG-4 were opened by R110/R111 and carried
into `docs/registry/user-queue.md` §3 under the docket house rule that nothing
may be built against a held flag. **All four are discharged here.** Every fix
named below is **queued to Errata Batch 2 and executed by no part of this
entry** -- the paper track implements nothing in engine code.

### FLAG-3 (`S13-X5`) -- RESOLVED, INTENDED. X5 closes fully, both legs.

**Verbatim: *"We deliberately allowed for powers to raise the fanfare floor
(without decaying) as a sort of strength-style scaling effect. I think this is
fine."***

FLAG-3 asked whether "seems fine" covered the decay-proof floor stacking or
only the cantrip leg. **It covers both, and the answer arrives with its
design intent stated:** the floor is a **strength-style scaling effect**, and
its immunity to decay is the point of it rather than an oversight in it. The
question the flag was holding is answered, so **X5 leaves the held register and
takes a disposition.**

**The disposition is X6's, exactly: the strategy is blessed, the power level is
watched.** A new watch item (`W4`, `docs/dockets/watch-items.md`) rides the
register with the magnitudes the S13 replay actually verified as its named
quantity -- **240 damage from one card** (`furina_fanfare_2`) and a **turn-2
boss kill** (`furina_fanfare_3`). Those two lines are what a future reading is
compared against; they are recorded so the trigger is falsifiable rather than a
feeling, per R111's definition of a watch item.

**Pin transition, and it is the first one in this corpus.** The X5 pin in
`tier0/tests/test_s13_exploit_pins.py` **converts from `xfail(strict=True)` to a
documented-behaviour test**: it now asserts that the mechanism **REPRODUCES**,
with no marker, citing this ruling. The polarity flip is the whole content of
the change -- the other thirteen pins assert the correct behaviour and are
xfail because the exploit is live; X5's behaviour **is** the correct behaviour
now, so the assertion that would have been the alarm becomes the assertion that
is the record. If X5 ever stops reproducing, that pin goes red, and it should:
a ruled-intended mechanism disappearing is a regression, not a repair.

### FLAG-1 (`S13-X1`) -- RESOLVED, RATIFIED CHANGE. The accumulator scopes to the writing turn.

**Verbatim: *"Limit the cost discount to the current turn? Yes."***

`state.companion_cost_delta_this_turn` is additive and uncapped, and its
discount currently outlives the turn that wrote it. **The accumulator scopes to
the writing turn, in both engines, mirroring the X11 boundary** that R110
already ratified for `replay_next_companion`. One boundary idiom, now used
twice.

**Distinct from FLAG-2(ii), and they may not be conflated.** `cost_override`
(FLAG-2(ii)) is a different mechanism with a different fix; two mechanisms, two
fixes, one shared boundary idiom. The flag's other half -- whether the note also
rides the Kokomi pool-rework docket, given `honor_guard` is the second enabler
-- is answered by the ruling being **engine-wide** rather than kit-local: a
turn-scoped accumulator closes the Klee leg and the Kokomi leg in one move, so
there is no live leg left for a second docket to carry.

**What the change does NOT close, stated because the finding invites the
mistake.** The **within-turn** free-companion loop survives this change **by
design**. A same-turn bound does not touch a mechanism that accumulates and
spends inside one turn -- the same shape R110's X11 errata already hit, and the
same shape the X11 pin still reports. That loop is governed by the **X2 rarity
law** (R109: infinite cycling engines gate to Uncommon or higher), and its
engines now sit at Uncommon, which is consistent with the X2 framework rather
than an exception to it. **Pin behaviour: report, do not force.** The X1 pin
stays `xfail(strict=True)` and its docstring says why.

**Implementation: Errata Batch 2 item 7.** Both engines.

### FLAG-2 (`S13-X3`) -- RESOLVED, BOTH FIXES RATIFIED.

**Verbatim: *"Yes."*** -- to both halves.

**(i) Copy ops inherit the printed card's bounds.** A copied
`sucrose_catalyst_conversion` respects its Exhaust limit; the copy op no longer
deletes the sheet's stated bound. This was the half R110 called a design call,
and the design call is made: **the printed bound travels with the copy.**

**(ii) `cost_override` aligns to the sheet and C# semantics -- "costs 0 *this
turn*".** This is **NC-12 / `SYS-3`'s sim-side fix**, and its direction is worth
recording: **C# is already correct**, so (ii) is a **sim-only parity repair**,
not a design change. tier0 writes `pick.cost = 0` permanently on the token where
sheet and mod both scope it to the turn.

**Implementation: Errata Batch 2 item 8.** (ii) sim-only; (i) as the batch
scopes it.

**STAGED, one word owed -- `AB-s1`.** NC-12's adjacent inversion is **not**
ruled here: C#'s Encore Performance does **not** exclude kit cards from the
copy pool, where the sheet and the sim both do, so a copied kit Burst clogs a
hand slot in game. It is a sheet-vs-mod parity fix and the fix is mod-side --
staged rather than landed because it is a **mod behaviour change** that has not
been explicitly blessed. Full draft text: `docs/awaiting-user-slots-2026-08-06.md`
slot 6.

> **[USER] RULING 2026-08-06 — `AB-s1` APPROVED: the mod's copy pool excludes kit
> cards, matching the sheet and the sim.** *(Q9, verbatim reply "Yes."; the
> slot-6 YES form, landed verbatim per R118. The mod code change itself is Track
> V's this wave; this annotation is the ruling of record.)*
>
> C#'s Encore Performance adopts the sim's exclusion: **kit cards are not legal
> copy targets.** The sheet was always the specification here and both other
> surfaces already implement it; this closes the third. The undiscardable
> copied kit Burst that clogs a hand slot in game stops being reachable.
>
> **Class: this is a MOD BEHAVIOUR CHANGE, recorded as one and not as a parity
> repair.** It ships with the next errata batch that touches C#, with parity
> vectors updated; it does not ride the paper. No sim behaviour moves, because
> the sim was already correct.

### FLAG-4 (`S13-X14`) -- leg (a) clarified with its root staged; leg (c) RULED intended.

**Leg (a) -- clarification recorded, root staged.** [USER]'s fallback
restatement **matches the shipped `S-3` spotlight path**, which is R110's leg
(b) and is already in the code. **Leg (a)'s root is a different thing and the
clarification does not reach it:** `curse_poor_sleep` is typed both `status`
(unplayable) and `retain: true` (never flushed). **The jam is the typing, not
the spotlight.** No fallback on the spotlight path can unjam a hand held by ten
cards that are unplayable and unflushable by their own type.

**STAGED, one word owed -- `AB-s2`.** Two options, drafted in full and neither
landed: **(α)** drop `retain` from the curse -- narrow, one card, a data repair;
**(β)** rule that status-typed cards always flush at end of turn, engine-wide,
on the StS precedent -- broad, a law, and it would close every future instance
of this typing class at once. Full text:
`docs/awaiting-user-slots-2026-08-06.md` slot 7.

> **[USER] RULING 2026-08-06 — `AB-s2` DECLINED: the typing stands.** *(Q10,
> verbatim reply "Neither - leave it alone."; the slot-7 NEITHER form, landed
> verbatim per R118.)*
>
> A card may be both unplayable and unflushable, and a hand jammed by ten
> copies of one curse is the run the player drafted. Recorded plainly because
> it is the cost of this answer: `stall_softlock_3` stays live and its S13 pin
> stays `xfail(strict=True)` forever, which is a legitimate state but should be
> a chosen one.
>
> **The reason, ecosystem fact, verbatim:** *"I recognize that card (it's from
> an event) - it's not possible to duplicate in normal play, so this whole
> concern is a false positive."* Consequences per R118: `curse_poor_sleep`
> keeps both typings; a single stuck copy is accepted behaviour; the multi-copy
> jam is annotated a false positive at `S13-X14` in the exploit ledger; **BETA
> was declined, not deferred** — a future status+retain card is a new row, not
> a re-ask. The surface-only verification of X14's acquisition vector is
> delegated to Track V.

**Leg (c) -- RULED, INTENDED. Verbatim: *"You deck out... don't do that."***

An all-Power deck erases itself into empty turns because Power cards route to
`result_pile: none` -- removed from combat, not exhausted. **This is intended
and takes the StS-precedent shrug: no guard is added.** Decking out is a thing
the player does to themselves, and the engine is not obliged to prevent it.
Recorded as **documented behaviour** in two places, so the next reader of
`refpowers.result_pile` does not re-file it: the function's own docstring, and
the X14 entry in `review/redteam/exploit-ledger.md`. **Leg (c) drops from the
queue.**

**The X14 pin does NOT convert.** Its representative line is
`stall_softlock_3` -- leg (a), the curse jam -- which is still governed by the
staged `AB-s2` and is not ruled. Only the ruled-intended leg would have earned
a conversion, and it is not the leg the pin runs. The pin stays
`xfail(strict=True)`.

### Version-stamp questions, surfaced per precedent

FLAG-1 and FLAG-2(ii) are **sim combat-math changes** when they land: a
turn-scoped accumulator and a turn-scoped `cost_override` both change what a
tier0 run costs and therefore what it measures. Surfaced here, decided by the
batch that lands them, per the R101/`CONSTANTS_VERSION` precedent -- the paper
track does not stamp a version for code it has not written. NC-7 raises the
same question at greater breadth and is surfaced with it (R115).

**Class: SUBSTANTIVE.** One mechanism is ruled intended and re-registered as a
watch item; three engine behaviours are ruled changed and queued. **No engine
code moves under this entry**, and the two staged items move nothing at all.

## R115 -- The fork was never evaluated, the Kokomi gates re-anchor, and a five-playtest table item becomes an instrument (2026-08-06)

Sitting of 2026-08-06, third and fourth sittings, Track AC, items `AC-1`
through `AC-5`. Records and reclassifications; **no lever is pulled and no
value moves anywhere in this entry.**

### AC-1 -- the `NT-G5` fork: INCONCLUSIVE BY NON-OBSERVATION, and the record shows its own correction

Two readings arrived on the same day and the second supersedes the first. Both
are on the record at `klee-mod/DECISIONS.md`, beneath the pre-registration,
the earlier one struck and kept (R101b).

**The superseded reading, verbatim: *"nothing stood out besides the charge
stacking / missing animation; let's review next playtest."*** Recorded at the
time as: no Neap Tide weakness observed, evaluation deferred.

**The operative reading, verbatim: *"I don't remember seeing the card during
the playtest, so it did not stand out one way or another."***

**Why the difference is the whole content of the correction.** The first
reading treats "nothing stood out" as a favourable read -- the hands did not
call her weak. The second says the card **was not exercised**: it did not stand
out because it was not seen. The pre-registration is explicit that **the hand
is the tiebreaker, not the sim**, so a session in which the hand never touched
the card cannot evaluate the fork at all. **Playtest three did not exercise
Neap Tide.** The fork's evaluation was not deferred; it was **not possible**.

**New record: the fork is OPEN, and its evaluation re-anchors to the next
Kokomi playtest WITH AN EXPLICIT OBSERVATION TASK.** Neap Tide is to be
deliberately drawn, played, and reported. The task is written into
`docs/kokomi-playtest-protocol.md` as **`OT-1`**, with its own Answers row,
rather than carried as an intention -- because the failure this record corrects
was exactly an intention nobody executed. "Never offered" is recorded as a
legitimate third outcome, structural rather than evaluative.

**Candidate alternative, recorded and NOT chosen:** fold the fork's evaluation
into the queued Kokomi pool-rework session instead of anchoring it to a
playtest. It is a real option and it is written down so the choice is visible
rather than defaulted into. **The observation task is the default, the fold-in
is the candidate, and the preference is [USER]'s -- an open queue row, not a
decision taken here.**

**Unchanged, and restated because two evaluations in one day invite the
mistake:** no lever is pulled by either reading. The fine-branch's **logged
sim-calibration offset for exhaust-loop kits** remains unwritten and is still
owed by the eventual evaluation. `S4-G13`'s fork half stays open.

### AC-2 -- `S4-G6` and `S4-G14` re-anchor to the post-rework Kokomi build

**Verbatim: *"deferral APPROVED -- land staged slot (b): stability band +
protocol playtest re-anchor to the post-rework Kokomi build; declare-before-
playtest law intact."***

The YES form pre-drafted at `docs/awaiting-user-slots-2026-08-06.md` slot 5
(Y-9(b)) is landed verbatim at all three of its named sites: `DEC-D5` (a dated
annotation beneath clause 4), `docs/kokomi-playtest-protocol.md`'s header, and
the queue. **`DEC-D5` clauses 2-4 survive intact** -- declared from design
intent with provenance, declared BEFORE the grading playtest, never revised
against the playtest that grades it. The re-anchor moves **which** playtest is
confirmatory and moves nothing about the order of operations, which is the
whole value of the gate.

**Recorded because the reply's own words invite the misreading:** "deferral
APPROVED" approves the **re-anchor**, not a postponement of the band. No band
is declared here, nothing is graded, and neither gate is discharged. The
co-op session of 2026-08-01/02 and playtest 4 are designated **EXPLORATORY** in
clause 1's existing sense -- which is a statement about what may be graded, not
a demotion of what they found.

### AC-3 -- `S4-G5` / `B-G1`: STILL AWAITING, and it stays a queue row

The narrow-to-Fanfare-axis disposition (slot 4, Y-9(a)) has **no reply**.
Recorded here so a reader of this batch does not infer that everything staged
by Y-9 landed: slot 5 landed, **slot 4 did not**. The row keeps its
plain-language form and nothing is built against it.

### AC-4 -- corpse detonation converts from table-luck to instrument, STAGED

**Verbatim, on the odds of the table item closing on its own: *"who knows when
it closes."***

`S4-G15` has been a *"~10 seconds at the table"* settlement since 2026-07-21
and has survived at least five playtests unanswered -- nobody has been holding
Pounding Surprise, on the bombed enemy, on the killing turn, while remembering
to look. **The question does not change; the way of answering it does.** A
bridge-driven scripted probe is registered:
`docs/probe-e-corpse-detonation-registration-draft.md` -- scripted fight, a
known bomb count on a killable enemy, the killing blow landed deliberately,
**two independent tells** (the relic spark and the HP deltas on the wire), a
negative-control arm, and the sim's behaviour read off the sim rather than off
the ledger's prose, which `NC-18` reports as backwards.

**The registration is STAGED FOR COUNTERSIGN and nothing has been run.** A new
probe is a pre-registered question under standing law, so it is paper until it
is signed. **The `S4-G15` table item survives as FALLBACK ONLY** and is not
retired -- if the probe is declined or stops short, the eyes-on check still
closes the question the moment somebody is holding the relic on the right turn.

### AC-5 -- the S2 event gallery becomes INSPIRATION-OPTIONAL

The event-gallery curation sitting (47 events, 141 drafted variants -> 130 kept
/ 11 cut, 4 demotions) **leaves the active-ask section of the queue** and joins
the Ancients and boss-pool galleries in the inspiration-optional section.
**Nothing is blocked on it**, which is the whole content of the
reclassification: the event layer's conversion pass no longer waits on a
checkbox sitting, and the gallery is read when somebody wants to read it.

Two things this does NOT do. It does not cut, keep or demote anything -- the
gallery's own recommendations stay exactly as drafted and unratified -- and it
does not retire the gallery. One cross-reference rides with it: `NC-15`'s Brain
Leech mismatch (shipped gallery text promises two cards, the option grants a
pick-1-of-3) is the same event as the S2 flag, so whenever either is answered
both are.

**Class: MECHANICAL** for `AC-2`, `AC-4` and `AC-5` -- an annotation landed
from a pre-drafted form, a registration staged, a status changed.
**Class: SUBSTANTIVE** for `AC-1`, because a recorded evaluation is withdrawn
and replaced, which changes what the fork is waiting on.

## R116 -- S14 canonicity: five questions ruled, a register for future card work, and Errata Batch 2 is constituted (2026-08-06)

Sitting of 2026-08-06, fourth sitting and final dispatch, Track AC item
`AC-6`. Source: `review/parity-sweep/noncard-triage-memo.md` (S14, 174 findings
across 173 entities). Verdicts verbatim; routing is this entry's. **Every fix
named below is an Errata Batch 2 item and none is executed here** -- the paper
track implements nothing in engine code.

### NC-1 -- companion and power damage scales with the player. SIM CANONICAL; the mod is the defect.

**Verbatim: *"They are supposed to also scale with you like your own cards."***

tier0 routes companion-power damage through the full damage pipeline --
Strength, Weak x0.75, Vulnerable x1.5 -- and the mod deals it as raw,
dealer-less hits. **The sim is right.** C# routes companion-power damage
through the full pipeline; **parity vectors are updated with the fix**, and
`NC-1`'s own line evidence (Durin's Witch's Flame, found independently from
both the companion and the powers side) **becomes the regression test.**

**Implementation: Errata Batch 2 item 3.** Mod-only.

**Explicitly NOT covered by this verdict: `NC-11`.** The verdict says so
itself, and the reason it has to is that the two look like one question and cut
opposite ways. Ruled separately below.

### NC-7 -- Frozen is the timer, applied per-creature. Each engine adopts the other's half.

**Verbatim: *"Ticks down per-turn, applies per-creature."***

Frozen was two different mechanics. **Canonical Frozen, as ruled:** a
**duration counter** that decrements at the end of the enemy side each turn,
with stacking extending it -- which is **the mod's** semantics, so **the sim
adopts the timer** and drops its one-shot boolean. And the boss substitution is
**per-creature** -- which is **the sim's** semantics, so **the mod adopts
per-creature**, and Kaiser Crab's boss-room adds become freezable in game where
they are currently not.

**Each engine gives up its own half.** Recorded that way deliberately: this is
not "one side was right", and reading it as a win for either engine will
produce the wrong fix.

**Shipped-boss-fight impact is real and is noted in the batch**, not
discovered by it: this touches a boss encounter that has shipped.
**Version-stamp question surfaced per precedent** -- this changes sim combat
math wherever Frozen appears, which is broader than any card. The stamp is
decided by the batch that lands it, not by the paper.

**Implementation: Errata Batch 2 item 5.** Both engines.

> **REQUIRED ANNOTATION, 2026-08-06 (R117, Q13).** This ruling's stated
> consequence — Kaiser Crab's second claw remaining freezable ("Kaiser Crab's
> boss-room adds become freezable in game", above) — is **overridden
> deliberately** by [USER]'s α selection on Q13, verbatim *"I'd say A"*,
> 2026-08-06. Under α (minions only: a boss-room creature carrying the game's
> `MinionPower` gets Frozen, every other creature gets the Vulnerable
> substitution) the second claw takes **Vulnerable, not Frozen**. This is a
> chosen reading, not a missed example: chat flagged the contradiction to
> [USER] before the dispatch was drafted, and the α selection stands with that
> consequence stated. No re-litigation. Mirrored on the `NC-7` execution note
> in `review/parity-sweep/noncard-triage-memo.md`.

### NC-10 -- the shop slots are specified, and both engines are defective against the spec

**Verbatim: *"Slot 1 should be 'Uncommon or higher from the home region'; slot
2 should be 'any companion card'; this is a defect."***

Neither engine implements that. The sim rolls `SHOP_COMPANION_RARITY_ODDS` for
both slots; the mod hard-wires slot 1 to Uncommon. **Both engines implement the
spec:** slot 1 filters the home-region pool to **Uncommon or higher**, slot 2
is **unrestricted**.

**One implementation question is surfaced and deliberately NOT chosen here.**
Rarity-odds renormalization *within* the Uncommon+ pool has at least two
readable answers -- condition the existing `SHOP_COMPANION_RARITY_ODDS` on
>= Uncommon, or state a fresh split -- and the implementer **surfaces the
candidate readings rather than picking one**. A renormalization chosen by an
implementer is a balance value chosen by an implementer.

**Cross-noted to the companion-pricing docket:** the shop is now a **real Rare
source in both slots' math**, which changes the acquisition assumptions that
docket prices against. `R59`'s slot-2 floor and `R60`'s override live in the
same neighbourhood and are named so the docket reads them together.

**Implementation: Errata Batch 2 item 6.** Both engines.

### NC-11 -- power-sourced block stays raw. SIM CANONICAL; the mod is the defect side.

**Verbatim: *"I think that the answer is no; my recollection is that
power-sourced block in the base game's kits ignores both of those."***

`NC-11` was minted as a **new** question by the fourth sitting, precisely
because `NC-1` was ruled and this one was named as not covered by it. It is
ruled here.

The sim's documented funnel exemption (`tier0/engine/powers.py:75-81`) is
**canonical**: Metallicize, the Ceremonial Garment rider and the Kurage pulse
add block **raw**, exempt from Frail and Dexterity. The mod is the defect side
and stops routing all three through Frail/Dexterity.

**The register this pair creates, recorded once for future card work**, because
the two rulings are adjacent, opposite, and will be misremembered otherwise:

> **Power-sourced DAMAGE runs the damage pipeline (`NC-1`).
> Power-sourced BLOCK is raw (`NC-11`).**

That is not an inconsistency; it is the base game's own shape, and a future
card that grants both from one power obeys both lines.

**Cross-note on `X10`, which this ruling closes.** S14 filed a caveat against
S13's Metallicize treadmill: *"the exploit's numbers are sim-side; in the mod,
Frail alone changes the wall's arithmetic."* **Post-fix that caveat resolves**
-- the mod stops applying Frail to power-sourced block, so the treadmill's
sim-side numbers hold in the mod too. The caveat is struck at its site with a
banner citing this ruling; `X10`'s own disposition (CANDIDATE, not ratified,
R111) is untouched.

**Implementation: Errata Batch 2 item 4.** Mod-only.

### NC-8 -- potions are actually consumed. RULED by inclusion.

`NC-8` -- the event resolver pops the potion from a **throwaway copy** of the
bag, so "The Future of Potions?" grants its reward free and the potion is
retained -- carried a **presumptive** answer in the queue ("potions are
consumed") awaiting one word. **The final dispatch supplies it by listing the
fix as Errata Batch 2 item 2**, which is a ruling in the operative sense: the
fix is ratified and executable.

Recorded as ruled rather than as still-presumptive, and recorded *why*, so the
next reader does not re-open it looking for a quoted sentence: **inclusion in a
ratified batch is the answer**, and the presumptive reading was the one
included.

**Implementation: Errata Batch 2 item 2.** Sim-only (`tier05/events.py`).

### Errata Batch 2 is constituted, ordered, and owned by a later track

**One batch, both engines where applicable, suite green at each boundary.**
Contents in the dispatch's own order:

| # | item | engines |
|---|---|---|
| 1 | term-3 fanfare credit -- tier0 credits only plays covered by a standing designation (R113 clause C-a's queued fix) | sim only |
| 2 | `NC-8` -- potions actually consumed (`tier05/events.py`) | sim only |
| 3 | `NC-1` -- companion-power damage through the full pipeline | mod only |
| 4 | `NC-11` -- power-sourced block raw | mod only |
| 5 | `NC-7` -- Frozen unified: sim adopts the timer, mod adopts per-creature | both |
| 6 | `NC-10` -- shop slot spec; odds renormalization surfaced, not chosen | both |
| 7 | `FLAG-1` -- companion cost-delta accumulator scoped to the writing turn (R114) | both |
| 8 | `FLAG-2` (i)/(ii) -- copies inherit printed bounds; `cost_override` = "this turn" (R114) | (i) as scoped; (ii) sim only |

**After the batch:** parity vectors plus all lints; **S13 harness
characterization on the affected lines -- report transitions, do not grade**;
version-stamp questions surfaced in one place (`NC-7` at minimum, and R114
surfaced FLAG-1/FLAG-2(ii) alongside it).

**Two paper items land with the paper and are NOT batch items**, stated so the
batch does not re-do them: FLAG-4 leg (c)'s documented-behaviour note (landed,
R114) and the FLAG-3 / `X5` pin conversion (landed, R114).

**Still staged or awaiting, and NOT in this batch:** `AB-s1`, `AB-s2`, `AC-3`,
`AC-4`'s probe registration, and the Neap Tide fork's anchoring preference.

**Class: SUBSTANTIVE.** Five parity questions take a canonical side and one
standing register enters the constitution's orbit. **No engine code moves under
this entry**, and the one implementation question with a balance shape
(`NC-10`'s renormalization) is surfaced rather than answered.

## R117 -- Q13/Q14/Q15 are ruled in three words, and the shop-odds rider is minted as Q16 (2026-08-06)

Wave-8 dispatch of 2026-08-06, landed at
`docs/dispatch-2026-08-06-q13-q14-q15.md` (REFERENCE). **Verbatim, [USER],
2026-08-06:**

> ***"14) Yes · 13) I'd say A · 15) Widen"***

**Q14 -- YES: the world stamp goes up.** `CONSTANTS_VERSION` **5 -> 6**.
Archive banners go on every published number below the stamp, **where it is
published** -- nothing rewritten (R101b). Affected surfaces per the batch's own
naming: all pre-batch combat numbers (Frozen rules changed) and the tier-0.5
shop maths in both engines (`NC-10`). **Execution is code-side and is Track
V's this wave**; this entry is the ruling of record.

**Q13 -- α (minions only).** The stopped mod half of `NC-7` completes: in boss
rooms, a creature carrying the game's `MinionPower` gets Frozen; every other
creature gets the Vulnerable substitution. The sim predicate **aligns to α
semantics** (parity, not design) and a parity vector is added for a boss room
with (a) a minion and (b) a non-minion helper. **The required annotation is
placed on R116's NC-7 section and mirrored on the execution note in
`review/parity-sweep/noncard-triage-memo.md`:** R116's stated consequence --
Kaiser Crab's second claw remaining freezable -- is **overridden deliberately**
by the α selection; under α the second claw takes Vulnerable. A chosen
reading, not a missed example; chat flagged the contradiction before the
dispatch was drafted; no re-litigation. **Code execution is Track V's.**

**Q15 -- WIDEN.** The citation lint's sweep extends to `tools/*.py`, and the
three occurrences in `tools/lint_role_tempo_coverage.py` are repaired to
satisfy it. Blast radius per the queue row: comments and docstrings only -- no
behaviour, no number, no test. **Lint-scope and repair execution is Track
V's** (widening a lint's scope is a code change; the paper track does not
touch it).

**The Q14 rider is NOT answered by "Yes" and is minted as `Q16`** in
`docs/registry/user-queue.md`, exactly as the dispatch specifies: inside the
shop's new Uncommon-or-higher pool, do the existing
`SHOP_COMPANION_RARITY_ODDS` simply renormalize over >=Uncommon (CONDITION),
or does [USER] state a fresh split (FRESH-SPLIT)? Not to be built against
until answered; chat's recommendation (CONDITION, the one-variable reading) is
carried into the row. *Same-wave note: Q16 was answered by the second
dispatch's "Condition." and is struck in the same commit that minted it --
both kept visible so the record shows the rider was asked and answered.*

**Ordering and the measurement window, as the dispatch states it:** all three
items land inside the same v6 window, before any re-measurement. The α scope
change is itself a Frozen-rules change, so v6 means "Frozen unified + α
boss-room scope + shop-slot spec" as one batch boundary. No v6 re-baseline
sweep and no new quotable combat or shop number until Q14's stamp and Q13's α
are both green. Q15 is orthogonal and may land in any order.

**Class: RULING** -- [USER] 2026-08-06, verbatim above. Paper lands here; code
is Track V's; the v6 re-baseline is Track M's.

## R118 -- The sitting batch 2026-08-06(b): eleven replies execute, and R88 loses its twisted clause (2026-08-06)

Wave-8 dispatch of 2026-08-06, landed at
`docs/dispatch-2026-08-06b-eleven-replies.md` (REFERENCE). Replies are
[USER]'s, verbatim; routing is this entry's. Zero new design authority beyond
the answers.

### §1 one-worders

**Q7 -- Verbatim: *"Yes."*** The drafted YES form (slot 4 of
`docs/awaiting-user-slots-2026-08-06.md`) lands verbatim at its three named
sites (R90 clause 1b annotation; `docs/axis-validity-session-charter.md` §7;
queue row `S4-G5`). Six axes close permanently as informational -- numbers
stay publishable as description, never acceptance targets; the Fanfare axis
survives as the whole of `S4-G5`/`B-G1`; the R107/F1 fence re-points to the
narrowed gate. **Unfenced by this stroke:** Furina backlog items 1-3 and the
fanfare STOP (`S4-G7`).

**Q11 -- Verbatim: *"Countersign."*** Probe E (corpse detonation, scripted)
converts from paper to work under its own registration
(`docs/probe-e-corpse-detonation-registration-draft.md`): two tells,
negative-control arm, nine confounders, cost ceiling, stop-and-re-register
tripwire. The table check survives as fallback until the probe reports;
`S4-G15` remains open until either answers. **The run itself is Track M's**
and, per the wave's sequencing note, happens after the v6 code lands.

**Q9 -- Verbatim: *"Yes."*** The mod-side kit-exclusion fix for Encore
Performance's copy pool lands; game matches sheet and sim. Blast radius: one
card's copy pool; no sim number, no test flip expected -- if one flips, stop
and surface. The slot-6 YES form lands at its named sites; **the mod code
change itself is Track V's.**

**Q10 -- Verbatim: *"Neither - leave it alone."* Rationale, verbatim:** *"I
recognize that card (it's from an event) - it's not possible to duplicate in
normal play, so this whole concern is a false positive."* The slot-7 NEITHER
form lands with the ecosystem fact attached as the reason. Consequences:
`curse_poor_sleep` keeps both typings and a single stuck copy is accepted
behaviour; `S13-X14` is annotated in the exploit ledger (multi-copy jam is a
false positive per the ecosystem ruling, quoted verbatim); **BETA
(status-beats-retain law) was declined, not deferred** -- a future status+retain
card is a new row, not a re-ask. **Verification task, surface-only, delegated
to Track V:** check what X14's recipe actually uses to acquire multiple
copies; if it reaches ten copies through normal-play acquisition, that
contradicts the false-positive premise -- come back with the finding as a
question, never bury or re-litigate.

**Q6 -- Verbatim: *"Repair."*** Drop the `+` from
`furina_salon_3_gala_bow_storm`'s upgraded set; re-verify at the card's
now-printed 0 cost; the pin returns from SKIP to a live verdict. X6's
mechanism remains R111's watch item. **Editing the exploit corpus and the pin
is instrument/code work: Track V's.**

**Q5 -- Verbatim: *"Playtest."*** The default stands confirmed: `OT-1` on the
next Kokomi protocol playtest is the fork's venue and its only accepted input.
The POOL-REWORK alternative is struck with the reply attached, in the queue
and at the fork block's records (`klee-mod/DECISIONS.md`).

**Q16 -- Verbatim: *"Condition."*** `SHOP_COMPANION_RARITY_ODDS` renormalizes
over the >=Uncommon pool; both engines; no new numbers stated. Lands inside
the v6 window with the rest of `NC-10`'s completion, before the re-baseline
sweep. **Code is Track V's.**

**Animation -- Verbatim: *"Let's do FREE-SPIKE and reconsider if the results
disappoint."*** The Path B (Skeleton2D) spike becomes a normal Code sprint:
Kokomi pilot, the computed-weights-from-layer-masks idea attached, Path C
layered remains the shipped fallback throughout. **The reconsider trigger,
recorded verbatim as the dispatch requires: disappointing spike results
re-open the Spine licence question ($379 Pro; Essential cannot author meshes)
without a new sitting.** The "animation path session" leaves the design queue;
the sprint is docketed (`docs/dockets/engineering-backlog.md`).

### §2 short picks

**10.2 -- Verbatim: *"Yes, and rider yes."*** The roster-anchor v14 n=3000
table is designated the quotable standing table -- **as re-produced under
v6**: the designation names the recipe and its v6 re-run, not the archived v5
read. Rider: `ref_ironclad`'s `archetype_package` gains `Card.archetypes`
tags. [USER]'s stated reason, on record: the tags are needed so the
instrumentation reads the anchor properly -- confirmed correct; without them
the core-attainment/payoff-reach columns cannot see the anchor at all. **The
tag change is Track V's; the v6 re-run is Track M's.**

**10.7 -- Verbatim: *"Let's yes to both and see if it turns up on local."***
(a) Search-and-repair authorized for the payoff-reach/`RARITY_ODDS`
registration -- sweep local worktrees first per [USER]'s note, then all
branches again (**in flight this wave as Track S2**). (b) `RA-G1`/`RA-G2`
core-attainment columns are **QUARANTINED** until the document is found or
re-established. If truly lost: re-register **before** any new number is read,
never retro-fit a registration to existing reads.

**10.8 -- ruled by principle. Verbatim: *"This is a prior ruling that seems to
have gotten twisted. A character may be playable and still have a companion
card."*** Executed: **R88 is amended** -- the exclusivity clause ("reserved
for a playable slot may not appear as a companion") is struck at R88 itself,
strikethrough + dated banner, never deleted. Consequences, recorded at the
amendment: (1) the Neuvillette contradiction dissolves and R52 needs no
amendment; (2) the four Fontaine Burst-name reservations stop being
rule-enforced -- future use is a taste question then, not a rule violation
now; (3) R108's Itto addendum stands unchanged with a dated note that its
"released to the companion pool" justification is superseded by the cleaner
principle (release was never needed).

### §3 paperwork trio -- Verbatim: *"correct, correct, repoint"*

(1) The S15 pin-table headline and per-module rows are corrected to the
counted **133** (`review/suite-hardening/summary.md`; the stale headline read
111 and four per-module rows read 0 for files that carry tests). (2) The S8
gallery header is corrected to **51** (`review/potion-relic-gallery/gallery.md`;
was "42 items"). (3) The `review/enemy-dossiers` branch pointer: the correct
single target is unambiguous -- **`28759f0`** (which contains `ec15028`;
`28759f0` is the pure-rename repair of `ec15028`'s misfiled files) -- and the
queue row is corrected to say so. **The branch move itself is BLOCKED and
surfaced, not silently skipped:** the branch is checked out in another live
worktree, so `git branch -f` refuses from this one, and the remote still
points at `e07fb4c`. The move (`git branch -f review/enemy-dossiers 28759f0`
+ push) is owed once that worktree is gone.

**Class: RULING** -- [USER] 2026-08-06, verbatim throughout. Paper lands with
this entry; every code-side execution is named to its track above; nothing
quotable until the v6 sweep is green.

## R119 -- Two charters are SIGNED: Class-P authority operates, and "Clear the Stage" is authorized in full (2026-08-06)

Mid-turn messages of 2026-08-06, same sitting day as R117/R118.

**(1) The Class-P charter (`docs/class-p-charter-2026-08-06.md`) is SIGNED.**
[USER], verbatim: ***"Oops - yes, charter is AUTHORIZEd"***. The charter's §5
R-draft becomes law by this entry, with that verbatim signature attached:

> **R-draft (Class-P authority).** Items passing all five §2 tests may be
> resolved recommend-and-proceed by agents, recorded in the P-ledger with
> attestation and revert handle, subject to per-batch digest and unlimited
> no-argument veto. Silence after digest ratifies a batch. Doubt on any test
> disqualifies. Taste, numbers, behaviour, laws, money, probes, and gated
> items are never eligible. The standing triage rule of §4 takes effect on
> signature.

The §4 standing triage rule takes effect from this ruling. The purge swarm
(P-A / P-B / P-C) is authorized to run. Queue row `Q17` (the signature ask)
was minted and struck in the same commit, Q16 precedent, so the record shows
the ask and its answer together.

**(2) The "Clear the Stage" /docs refactor charter
(`docs/clear-the-stage-charter-2026-08-06.md`) is delivered FULLY
AUTHORIZED.** [USER]'s framing line, verbatim: ***"And another cleanup pass
after thatg - also fully AUTHORIZEd:"*** (typo preserved). Against the
charter's own §6 three-option form, "fully AUTHORIZEd" = **AUTHORIZE, all
tracks including R-D** (ledger volumization). **Sequencing, per the charter's
own §5 non-goals: the refactor does not operate inside the open v6
measurement window -- execution begins after the v6 re-baseline sweep is
green** (the sweep is in flight this wave as Tracks V/M).

**Class: RULING** -- [USER] 2026-08-06, both signatures verbatim above. Two
charters move from draft to operating law; no design authority is created
beyond what their own texts define, and both texts bind their swarms to zero
design decisions.

## R120 -- Dispatch (d): four replies execute -- the Klee rename, the art release, a staged drafter change, and probe (d)'s countersign (2026-08-06)

Fourth dispatch of 2026-08-06, delivered with the verbatim framing line
*"Thanks! One more batch for you from the design chat -"*; landed at
`docs/dispatch-2026-08-06d-four-replies.md` (REFERENCE). Replies are
[USER]'s, verbatim; routing is this entry's. Zero new design authority beyond
the answers.

**Klee rename -- Verbatim: *"yes, we can slightly tweak the Klee card to keep
them separate (Catalytic Converter?)"*** RENAME-POWER executes with
**"Catalytic Converter"** as the chosen string: the Klee card, its upgrade
(`Catalytic Converter+`), the mod power class title, the constants comment,
R37 cell labels, and test docstrings all follow in one string pass. Two notes
were flagged to [USER] in-channel before landing, neither blocking, recorded
here: (1) the name is also the automotive emissions device -- read as an
intentional Klee-flavored pun unless [USER] says otherwise; (2) the
separation from Sucrose's "Catalyst Conversion" is partial (both remain
Cataly\*-Conver\*-shaped). The pass is cheap to re-run; one word swaps the
string at any time. **Sucrose's card is untouched -- it was always correct.**
**The string pass (both engines + docs) is Track V's this wave.**

**10.1 -- Verbatim: *"let's go with a)"*** `grand_gala` releases Opera
Epiclese; `standing_room_only`'s overturn lands on it with a clean lint.
`grand_gala` enters the re-hunt flow (art_fetch -> contact sheet); its
replacement candidates join the `S4-G12` eyes-on so [USER] picks once, not
twice. The other four lint failures stay as noted per-item in the review page
(no ruling owed unless a listed fallback is picked). **The art
release/overturn/re-hunt is Track AR's this wave**; the paper mints the
`grand_gala` art-debt row.

**10.3 -- Verbatim: *"Yes"* -- and the change is STAGED, NOT LANDED, on its
own sequencing rail, recorded in full.** Payoff-presence extends to the
spotlight limb (`tier05/draft.py`); `limelight` alone stops satisfying the
limb. This is a **drafter behaviour change, i.e. DRAFTER 15, with a
re-baseline sweep under stamp law.** The payoff-reach sprint's
pre-registration (whereabouts unknown; the 10.7 search is running as Track
S2) was registered against a specific drafter version. Until that document is
found and its pinned version read, landing D15 could invalidate a blind
pre-registration -- the exact thing the escrow discipline exists to prevent.
So: the change sits staged with this note; it lands as D15 immediately after
10.7 resolves, either after the sprint runs under its registered version or
after a clean re-registration if the document is truly lost. No prediction is
read, nothing re-litigated. **The staged branch is Track V's (pushed,
unmerged, never landing this wave); the hold is docketed as a
staged-pending-10.7 row in `docs/dockets/engineering-backlog.md`, not the
user queue.**

**10.13 -- Verbatim: *"countersigned"*** Probe (d) (`Aria of Recompense`'s
unreconstructed Block, `docs/probe-d-registration-draft.md`) converts from
paper to work under its own registration: confounder list, cost ceiling,
stop-and-re-register tripwire all as written. **Results adjudicate B2's
declared residual and nothing else; Guardrail 7 unchanged.** **The run itself
is Track M's**, under the registration as countersigned -- the runner
respects the registration's own harness design.

**Queue hygiene, as the dispatch orders it:** all four rows struck with their
verbatim replies where they live (10.1 / 10.3 / 10.13 in the queue's §5; the
Klee rename lived un-rowed inside the N-ledger's near-collision cluster and
is recorded as answered in the queue's answered table); `grand_gala` gains an
art-debt row; D15 gains its staged-pending-10.7 engineering-backlog row.

**Class: RULING** -- [USER] 2026-08-06, verbatim throughout. Paper lands with
this entry; the string pass, the art work, the staged branch and the probe
run are named to their tracks above. No card sheet, code or art moves under
this entry.

## R121 -- Dispatch (e): six replies execute -- a registration is countersigned, the anchor is shielded, the moves get a resolver, and the last three DOUBT rows resolve (2026-08-06)

Fifth dispatch of 2026-08-06, landed at
`docs/dispatch-2026-08-06e-six-replies.md` (REFERENCE). Replies are [USER]'s,
verbatim; routing is this entry's. Zero new design authority beyond the
answers. **Paper lands with this entry; the Q19 code shield/re-measurement and
the Q20 file moves are named to follow-up tracks below and land nowhere near
this commit.**

**`Q18` -- Verbatim: *"agreed, countersigned, tto quarantined."*** The
payoff-reach / `RARITY_ODDS` re-registration
(`docs/payoff-reach-reregistration-draft-2026-08-06.md`) converts **from DRAFT
to the sprint's registration**, pinned **DRAFTER 14**, predictions still blank
by design. The dispatch's execution order is law and is recorded verbatim:

> Execution order, strictly: (1) the tto columns join the RA-G1/RA-G2
> quarantine under the same banner; (2) at sprint kickoff, predictions are
> authored design-side and appended to the registration as their own commit --
> before any measurement runs; (3) the sprint runs under D14; (4) blind-first
> grading; (5) staged D15 (EB-43) lands with its re-baseline; (6) the
> quarantine -- now including tto -- lifts on the graded read. No step
> reorders.

**Step (1) executes with this entry**: the `tto` column joins the
`RA-G1`/`RA-G2` core-attainment quarantine **under the same banner** -- a dated
addendum on the existing quarantine banner in
`docs/roster-anchor-v14-v6-2026-08-06.md`, not a second banner. Steps (2)-(6)
are recorded and **not executed**: they are future sprint steps, and the order
is not reorderable by any track. The registration converts **in place** (the
`-draft` filename is retained): frozen records already cite the path -- the
quarantine banner, `EB-43`, the queue -- and rail 1 forbids repointing a
citation inside a frozen record, so renaming would strand them permanently.
The document's own banner, not its filename, carries its status.

**`Q19` -- Verbatim: *"let's shield it, plus a note for any future sim work to
take a look and figure out what went wrong (why did winrate go down,
basically)."*** **SHIELD executes:** `score_offer`'s core-advance bonus is made
blind to the anchor arm's tags (instrumentation continues to read them); the
`ref_ironclad` arm **alone** is re-measured under the same recipe; the quotable
table's row is republished with a dated note. **The tripwire is [USER]'s and is
recorded as stated: if the shielded re-measurement does not restore the
archived ordering, stop and surface -- that would mean the mover wasn't the
tags.** The investigation question is minted verbatim in the engineering
backlog as **`EB-46`**: *why did tag-visible scoring lower the anchor's winrate
(11.13% -> 7.50%)?* -- a diagnosis question for future sim work, **no deadline,
no design authority**. **The code change, the re-measurement and the
republished row are a follow-up track's; this entry is paper only.**

> **DATED ADDENDUM, 2026-08-06 (`Q19`) -- the tripwire FIRED, and [USER]
> released the republication anyway.** The follow-up track
> (`findings/track-e5-shield`) landed the shield and re-measured the
> `ref_ironclad` arm alone under the table's own recipe (n=3000, seed
> 20260729, `RT7/D14/P3/C6`; checkpoint
> `review/r121-shield/shielded-arm-9.json`). The shielded reading is **win
> 13.83% [12.6, 15.1]**, and it does **not** restore the archived ordering --
> it **overshoots** it: **z = +3.16 vs the archived 11.13%** (past the
> sweep's 12-arm Bonferroni bar of 2.87) and **z = +3.08 vs `furina/salon`
> 11.20%**, whose interval it no longer overlaps, so the anchor moves from
> archived co-leader to **sole leader**. Per the tripwire the track stopped
> and surfaced without republishing.
>
> **Three options were posed and one was chosen.** (a) land the shield as-is
> and republish 13.83% with a dated note naming the CONSTANTS 5 / CONSTANTS 6
> confound, making **untagged-under-C6 the honest baseline**; (b) hold the
> row pending the `EB-46` diagnosis; (c) revert to ACCEPT and keep the tagged
> 7.50%. **[USER], verbatim (2026-08-06): *"Yeah, I think A) is
> defensible here."*** **Option (a) executes.**
>
> **The confound, recorded because it is the whole reason (a) needs saying
> out loud:** the archived 11.13% is a **CONSTANTS 5** number and every
> shielded reading is **CONSTANTS 6**, so "the tags moved the anchor" and
> "C5->C6 moved the anchor" are not separated by the paired halves -- the
> sweep's attribution rested on the other eleven arms being unmoved, which
> does not establish that this arm was. An untagged-under-C6 reading did not
> exist before this one. A second, diagnostic-only measurement that shields
> the WHOLE of `score_offer` (`review/r121-shield/probe-full-shield.json`;
> **not** committed behaviour) reads **13.20%**, z = +2.45 vs 11.13% -- so
> the residual is not a leftover tag-reading term in the scorer.
>
> **What this addendum discharges and what it does not.** The stop-and-surface
> clause is **DISCHARGED for this measurement**: the row republishes, with its
> dated note, in `docs/roster-anchor-v14-v6-2026-08-06.md`. **`EB-46` remains
> the live diagnosis question**, now posed cleanly -- separate the tag effect
> from the v6 effect on this arm. `DRAFTER_VERSION` is **not** bumped and the
> non-bump is flagged at the constant (the shield restores the behaviour v14
> was stamped for; step (3) of `Q18`'s order runs under D14; 15 is claimed by
> staged `EB-43`). Nothing in the quarantine banner moves.

**`Q20` -- Verbatim: *"agreed, MOVE-WITH-RESOLVER."*** Track R-B resumes: the
**45 held ledger-cited files** move to `docs/archive/` verbatim-under-banner;
`docs/registry/identifiers.md` gains an **old-path -> new-path resolver
table**; the citation lint learns to resolve ledger paths through it -- **a
stale path that resolves is green; one that doesn't is a failure**. **Ledger
bytes untouched, per rail 1.** The charter's acceptance count is re-run when
the moves are done. **The moves, the resolver table and the lint change are
Track R-B's; this entry is paper only.**

**`R59` -- Verbatim: *"superceded but flag it for future design discussions
(SHOULD it be rarity limited to avoid serving up crap cards, or is it fine to
offer commons?) - this might need empirical data during a future round on the
companion cards."*** (typo preserved.) The sidecar row moves to
**`SUPERSEDED-BY:R116`**, **scope limited to the slot-2 floor clause**, with
the reply verbatim in the evidence column. The design question is **minted onto
the `S4-G10` / `M11` shop close-out agenda** -- its natural home -- as: *should
slot 2 carry a rarity floor at all*, with the recorded note that the answer
**wants empirical data (Common offer / pick / skip rates) from a future
companion-card measurement round, not an a priori ruling**. The agenda gains an
item, not an answer; `S4-G10` stays OPEN and [USER]-gated.

**`R103` -- Verbatim: *"OPERATIVE-NARROWED."*** The sidecar row records the
narrowed scope as briefed: **R103(b)'s gate still binds any future
selector-recorded fanfare trace**, and **the escrow strike stands unaffected**
-- different question, different instrument. **No re-litigation of R113.**
`OPERATIVE-NARROWED` enters the sidecar's status vocabulary by this entry: it
is an OPERATIVE row whose operating scope is stated, counted with OPERATIVE in
the generated digest because nothing was superseded, amended or discharged.

**`R107` -- Verbatim: *"AMENDED-BY:R118."*** The sidecar row moves to
**`AMENDED-BY:R118`**, scope **"fence target only."** R90's banner and R118's
re-point are now formally reconciled **as amendment, zero behavioural
difference**.

**Queue hygiene, as the dispatch orders it:** the three DOUBT rows resolve and
the **`S4-G9`-riding queue row closes** -- `S4-G9`'s sitting shrinks by one;
`Q18`/`Q19`/`Q20` strike verbatim with their replies attached; the generated
status digest is regenerated (`python tools/gen_decisions_digest.py --write`;
CI fails stale); the suite is green at every boundary. The status-pass digest
(`docs/registry/status-pass-digest-2026-08-06.md`) gains a dated resolution
note rather than a rewrite of its tables -- **the pass's record of what it
refused to guess stays exactly as delivered.**

**Class: RULING** -- [USER] 2026-08-06, verbatim throughout. Paper lands with
this entry. No number moved, no measurement ran, and no ledger byte inside a
frozen entry was rewritten. **Zero DOUBT rows remain in the sidecar.**
