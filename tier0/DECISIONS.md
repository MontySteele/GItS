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

## R39 -- spark-reading effects see the bank at play time (2026-07-21)

USER RULING, from playtest: "Gleeful Barrage attacks based on the number
of sparks, but if that number is 3+, those sparks are consumed to lower
its cost before the card checks how many attacks to do (potentially
stopping it from attacking). Let's have it check the spark count before
they are consumed instead."

The card fought itself: reaching the threshold that makes it FREE was
exactly what deleted the sparks it counts, so at exactly 3 sparks it
went free AND dropped from 5 hits to 2. This was NOT a port bug -- the
C# mirrored the sim faithfully (the recorded Snap-fix caveat). The law
moved first, then the mod.

MECHANISM: state.sparks_at_play snapshots the bank in play_card before
the spend; the 2_plus_sparks formula reads that instead of
state.player.sparks. BLAST RADIUS IS EXACTLY ONE CARD: only attacks
spend sparks, and both has_spark cards (eager_to_help, patched_dress)
are skills, so nothing else can observe the difference.

The user's own alternative framing -- "or add 3 attacks if the card
costs 0, same effect" -- is NOT equivalent and was not taken: True Spark
Knight / spark_threshold_down make the threshold 2, so a literal +3
would over-pay. The pre-spend read is threshold-agnostic by
construction.

BAND CONSEQUENCE, measured 1000 fights/seed 42 before shipping: at the
ratified 4 damage the buff put spark/tank_boss at 0.701 against a
ceiling of 0.65, and tied A1_frontload with A2_scaling (4.2 vs 4.2),
violating the identity constraint. Two ratified surfaces, so this went
back to the user rather than being re-baselined (DECISIONS 62).

RULED COMPENSATION: gleeful_barrage per-hit damage 4 -> 3. Re-measured:
spark/tank_boss 0.587 (mid-band), identity constraint holds, other three
band cells unmoved (demolition 0.957, reaction tank_boss 0.521, reaction
gauntlet 0.926). The upgrade delta stays {damage: +1}, now 3->4.

SIDE EFFECT WORTH RECORDING: this retires the queued "spark tank_boss
margin" concern. That cell sat at 0.485 against a floor of 0.45 -- 3.5
points of headroom, flagged to the user as uncomfortably thin. It now
sits at 0.587, near the middle of [0.45, 0.65]. The margin was fixed by
a mechanic ruling, not by a balance patch aimed at it.

C# MIRROR: SparkPower.SparksAtPlay (the raw Amount -- our consume runs
in AfterCardPlayed, so during OnPlay the bank has not yet been spent,
which makes the pre-spend read the PLAIN one). SparksAsResolved is kept
and documented as the correct accessor for any future attack that wants
the post-spend view; it currently has no reader.

## R40 -- Furina runner rulings and Salon replacement pass (2026-07-22)

USER RULINGS: the starter carries one Aria of Recompense at 5 Encore
(8 upgraded) and one 0-cost An Invitation; Stage Presence is 5 Block
(8 upgraded); self-Spotlight has a 1.0 numeric multiplier. Encore absorbs
enemy damage only after Block. Generated Guest Stars are selector-v4's
depth-one bricking exception and return the light to Furina after play.

SALON LAW: three active slots. A tick that can pay 1 Encore deals full
damage; a dry tick deals half damage and never overdraws HP. Every overflowed
deployment gives the displaced Member an immediate Hydro final bow at three
times its current tick damage. If the deploying card has a following rider,
replacement triples printed damage or Block, or doubles numeric utility
(Encore, draw, application, healing, or non-Member power) exactly once for
that card, regardless of how many Members it displaced. The replacement flag
resets at the start of every card resolution.

MEASUREMENT: after the direct Salon-number lift, 1,500 realistic runs/plan at
seed 11 moved Salon Act clear 0.13% -> 5.2% and first-elite survival 17.1% ->
40.9%; Spotlight/Fanfare first-elite survival rose only to 24.7%/24.2%, with
Act clear near zero. Deep Salon overshoots in the opposite direction:
tank_boss 99.4%, A2 8.9 against the 7.6 ceiling. A 300-fight source audit
attributes 16.3% of its damage to final bows and 52.3% to ordinary Salon
ticks, so the overshoot is the assembled persistent engine rather than a
cross-card multiplier leak. Disposition: keep this as the measured pass;
further work should redistribute power toward early access/frontload rather
than add more global Salon scaling.

## R41 -- Spotlight two-mode rework and spendable Fanfare (2026-07-22)

USER RULING: test the Spotlight/Fanfare rework before adding more Companion
cards to Furina's starting deck. CENTER STAGE designates Furina: her cards
generate 2 Fanfare per play and receive no numeric Spotlight bonus, including
card-granted bonus powers. GUEST CAST designates the Companion category rather
than one character: every Companion card receives the outward multiplier and
Spotlight texture, while those plays generate no Fanfare. The selector chooses
Guest Cast for a ready Companion in hand and Center Stage otherwise.

FANFARE becomes a cyclic spendable pool. Crescendo spends 10 after resolving
(8 + 1 per 2 pre-spend Fanfare); Florid Cadenza spends 10 (7 upgraded); Flood
of Emotion spends 15 and deals 20; Universal Revelry spends 20 and uses 1 per
2; High Tide spends 15 and deals 22. Rapturous Applause costs 1 Energy. The
resource gate is checked before play and paid once after resolution so the
payoff reads the audience level that funded it.

DRAFT CORE: Spotlight requires two cast-access pieces (Companions or Guest
Star generators) and two machinery pieces. Companions receive explicit
Spotlight draft value; same-character depth is retired.

MEASUREMENT, 1,500 realistic runs/plan seed 11 in the CURRENT WORKTREE
(including the concurrent companion-card number pass): first-elite survival /
Act clear = Salon 42.8% / 5.9%, Spotlight 32.3% / 1.1%, Fanfare 28.9% / 0.2%.
Spotlight drafted at least one Companion before the first elite in 100% of
runs (one 39.2%, two 44.6%, three 16.2%); 100% gained extra cast access,
49.8% found any machinery, and 8.3% completed the full core. Therefore the
starter-Companion injection is HELD: cast access is fixed, machinery density
and payoff efficiency are the remaining bottlenecks.

## R42 -- Spotlight machinery efficiency and starter-density bracket (2026-07-22)

USER DIRECTION: evaluate balance on full Act-1 clears, not merely reaching or
passing the first boss/elite; Klee's current Act target is 40-50%. Current
realistic reference at 1,500 runs, seed 11: Klee Demolition 39.4%, Spark
33.6%, Reaction 40.4%. Furina Spotlight's R41 1.1% therefore represents an
order-of-magnitude delivery failure.

MACHINERY PASS: Limelight, Shared Billing, Guest List, and Encore Performance
refund their setup Energy; Limelight still replaces itself, Stage Lights now
draws 1, Top Billing loses its Spend-2-Encore gate, and Standing Ovation costs
1 (0 upgraded). The Spotlight core is two access pieces (the starter Invitation
plus a Companion/generator) and ONE machinery piece, not two.

RESULT, 1,500 realistic Spotlight runs: Act clear 10.6%, first-elite survival
50.5%, core online 66% overall. Deep package win rates are 79.4% punisher,
100% swarm, 100% attrition, 63.2% tank. The assembled package now delivers;
the realistic run remains diluted by ten starter cards against one-to-three
early drafted Companions.

STARTER DIAGNOSTIC, 1,000 realistic runs/arm, randomized from Fontaine common
Companions on a dedicated RNG stream: unchanged 11.4%; replace one Soloist
with a Companion Attack 26.4%; replace one Stage Presence with a Companion
Support 9.6%; Attack+Support 30.3%; replace TWO Soloists with two distinct
Companion Attacks 46.6%; two Attacks+Support 51.9%. This is diagnostic, NOT YET
A USER RULING. The clean in-band proposal is two randomized common Fontaine
Companion Attacks replacing two Soloist's Solicitations, while all three Stage
Presence cards remain.

## R43 -- Post-Klee companion rerun and Fontaine starter pair (2026-07-22)

POST-COMMIT BASELINE: after aa5277f's shared Companion uplift, but before a
randomized Furina starter, 1,500 realistic runs/plan at seed 11 produced Act
clears of Salon 8.9%, Spotlight 10.7%, and Fanfare 1.2%. Spotlight was
effectively unchanged from R42's 10.6%; Salon and Fanfare rose from 5.9% and
0.2%, respectively, but remained far below the 40-50% Act target. Therefore
the earlier Spotlight diagnosis had already been made in substantially the
buffed-Companion world.

USER RULING: mirror Klee's role-locked random starter, but replace ONE weak
Attack and ONE basic support rather than two Attacks. Furina rolls one of
Chevreuse -- Interdiction Fire / Freminet -- Pers, Deploy! in place of one
Soloist's Solicitation, plus one Fontaine support in place of one Stage
Presence, on the existing dedicated replayable starter RNG stream.

SUPPORT SELECTION: the first pass used Charlotte -- Enduring Frosthelm and
Lynette -- Box Trick. At 1,000 identical seeds per exact pairing, Charlotte
arms cleared 37.8% / 35.5%, while Box Trick arms cleared only 22.9% / 21.6%.
This was structural: Guest Cast amplifies Charlotte's printed Block from 4+4
to 6+6, while its numbers-only law deliberately does not amplify Box Trick's
Draw 2; Box Trick also displaced a 5-Block basic. Lynette -- Enigmatic Feint
was substituted as the defensive support texture. Before any personal-card
nudge its two arms cleared 30.5% / 30.6%, eliminating the severe low roll.

BASE-KIT BRACKET, 1,000 realistic runs/arm with the Charlotte/Enigmatic slate:
the prior Soloist 4 / Stage Presence 5 baseline cleared 32.9%; Soloist 5 alone
fell to 30.4%; Stage Presence 6 alone rose to 39.7%; both changes cleared
37.6%. The damage lift made a still-mediocre Attack attractive enough for the
pilot to spend more Energy on it. SHIPPED DOSE: Stage Presence 6 Block (9
upgraded), with Soloist held at 4.

FINAL SUITE, 1,500 realistic runs/plan at seed 11: Salon 27.3% Act / 76.7%
first-elite survival; Spotlight 39.7% / 82.0%; Fanfare 9.5% / 61.4%.
Spotlight now reaches the lower edge of the Klee-derived target; the same
starter substantially helps the other plans without concealing that Fanfare
is still the next balance problem.

FINAL PAIR MATRIX, 1,000 identical seeds/arm: Chevreuse+Charlotte 44.1%,
Freminet+Charlotte 44.3%, Chevreuse+Lynette 36.6%, Freminet+Lynette 36.4%.
The Attack choice has no measurable value skew (at most 0.2pt); Charlotte is
a meaningful 7.5-7.9pt high roll over Lynette, but both are viable and the
random aggregate is 39.7%. Keep that bounded starter texture rather than add a
second global buff solely to flatten it; revisit after human playtest.

## R44 -- Fanfare conversion diagnosis (2026-07-22)

SCOPE: diagnostic sweep after R43's randomized starter raised the realistic
Fanfare plan to 9.5% Act clears. No card-balance dose is shipped in this
record.

RUNNER FIX: the combat pilot's readable-conditional list omitted
fanfare_at_least_* and encore_at_least_* even though the engine resolved both.
It therefore valued Dramatic Entrance as 6 rather than 9 damage, Showstopper
as 5 rather than 12, and Thunderous Ovation as 3 rather than 7 Block while
their thresholds were live. The predicates are now visible to play selection
and test-locked. This was a real accuracy bug but not the balance cause:
1,500-run Fanfare Act clears remained 9.5%.

RESOURCE TRACE, 1,500 realistic runs at seed 11: per reached fight, Furina
gained 24.6 Fanfare, spent only 3.2, peaked at 22.7, and ended at 21.4.
Threshold reach was 94.1% at 10, 80.8% at 15, 64.8% at 20, and 40.8% at the
30 cap. Generation is therefore abundant. True spender play rates were tiny:
Crescendo 0.05/fight, Flood of Emotion 0.04, Florid Cadenza 0.02, High Tide
0.01; the meter is full because realistic decks rarely own and play a
converter, not because the resource rate is low.

DRAFT-CORE NULL: the generic four-piece definition produced 8.8% Act clears
at 1,000 seeds. Re-defining online as Aria+one piece yielded 9.1%; first
payoff completes yielded 9.9%; treating the native resource as online from
run start yielded 9.8%. The old core@E1 scalar (about 9-10%) badly describes
the live resource, but payoff gating in the assigned drafter is not causing
the balance failure.

PILOT NULL, 1,000 identical seeds/arm: current 8.8%; tempo 0.6/sustain 1.0
8.1%; damage weight 1.4 5.4%; a damage-forward converter profile 5.7%; the
most aggressive profile 4.5%. Furina genuinely needs the current sustain and
tempo play, so the answer is not instructing the pilot to ignore setup.

ASSEMBLED PACKAGE: Fanfare wins 48.4% Punisher, 100% swarm, 100% attrition,
and only 24.6% tank boss, versus Salon 98.8/100/100/99.6 and Spotlight
85.6/100/100/73.6. Its DPT is only 11.0/12.2/9.3/13.4 despite spending
27-88 Fanfare per fight. The full engine can cycle, but conversion is too
Energy- and density-inefficient for single-target fights.

SINGLE-CARD SEED SCREEN, 300 identical seeds/arm, one extra card (directional
because n is deliberately small and the eleventh card pays deck bloat):
Curtain Up and Warm-up Act were the best sub-Rares (+8.3pt and +7.0pt Act);
Rapturous Applause was +3.3pt. Most nominal engine pieces were neutral or
negative, including Crescendo -1.7pt, Showstopper -2.3pt, Ebb and Flow -2.0pt,
Audience Participation -3.3pt, Suffering for Art -3.7pt, and Florid Cadenza
-4.7pt. Regina's Mercy led overall at +8.7pt. The shape favors free activity,
durable scaling, and large actual sustain over more meter generation.

SPENDER-TAX BRACKET, 1,000 identical seeds/arm across Crescendo, Florid
Cadenza, Flood of Emotion, Universal Revelry, and High Tide: current 8.8%;
each costs one less Energy 14.3%; each costs five less Fanfare 9.2%; both
discounts 18.9%. Energy is the binding half of the double cost, while Fanfare
price alone is not. Even both discounts remain far below target, confirming a
second density problem: every true spender is Uncommon or Rare, while the
Common suite is dominated by generation, thresholds, and cycling.

DISPOSITION FOR THE NEXT DESIGN WINDOW: do not increase global Fanfare gain or
lower the cap. Start with spender Energy efficiency, then re-author at least
one Common into a small real converter so early decks can cycle the meter;
separately review the low-output generator/cycler bodies. Rapturous Applause
is the clearest existing model for a payoff that actually helps. Re-run both
realistic Act clears and the Punisher/tank assembled-package cells after a
concrete dose.

## R45 -- Fanfare conversion-efficiency dose and ceiling boundary (2026-07-22)

USER RULING: apply R44's proposed spender-efficiency and Common-converter
patches, then measure before proceeding.

SHIPPED FIRST DOSE:

- Crescendo 2->1 Energy, still Spend 10 Fanfare.
- Florid Cadenza 1->0 Energy, still Draw 3 / Spend 10.
- Flood of Emotion 2->1 Energy, still 20 damage / Spend 15.
- Universal Revelry 3->2 Energy, still scaling AoE / Spend 20.
- High Tide 2->1 Energy, still 22 damage / Spend 15.
- Dramatic Entrance becomes the Common converter: 1 Energy, gated at and
  spending 5 Fanfare after dealing 6+4=10 damage. Its upgrade raises the rider
  4->7.

REALISTIC RESULT, 1,500 runs/plan at seed 11: Fanfare Act clear 9.5%->15.7%,
first-elite survival 61.4%->68.2%, second-elite survival 22.9%->32.3%.
Spending doubled from 3.2 to 6.4 per reached fight; end-of-fight Fanfare moved
only 21.4->20.2, so access remains sparse. Cross-plan movement was healthy:
Salon 27.3%->31.3%, Spotlight 39.7%->42.9%.

ASSEMBLED RESULT, 500 fights/cell: Punisher 48.4%->87.2%, tank boss
24.6%->72.2%, swarm/attrition remain 100%. This nearly matches Spotlight's
85.6%/73.6% single-target ceiling. The payoff package now works when assembled;
the remaining realistic gap must not be repaired by another blanket ceiling
increase.

POST-DOSE SINGLE-CARD SCREEN, 300 identical seeds/arm with one conservative
extra card: High Tide +9.7pt Act, Crescendo +7.7pt, Flood +6.7pt, and Dramatic
Entrance +2.0pt. The spender repairs succeeded. Florid Cadenza remained -5.7pt
and Showstopper -6.7pt; Suffering for Art -5.0pt and Hearts Swelling -3.7pt.
Those identify low-floor cards but do not by themselves authorize global
buffs in an already-healthy assembled package.

REJECTED FOLLOW-UP BRACKET, 1,000 realistic runs/arm:

- "bottom-card repairs" (Florid Spend 5; Showstopper 7+8 at 15; Suffering
  self-damage 1; Hearts cost 1) lifted 15.1%->22.6%, but overheated the deep
  package to 98.0% Punisher / 96.0% tank.
- "common efficiency" (Crowd Work and Ebb Energy refunds; Audience Encore 3;
  Tempo Spend 1 Encore; Thunderous base Block 4) reached only 17.1%, while
  deep rose to 94.8% / 90.8%.
- Combined reached 25.8% realistic but 99.6% Punisher / 100% tank.

DISPOSITION: keep only the first dose. Do not ship the follow-up groups. The
balance problem has changed shape: the assembled ceiling is healthy, while the
realistic floor lacks timely conversion access and is offered several cards
that are poor isolated additions. The next experiment should change access or
draft density/selection without increasing the completed package's power.

## R46 -- Fanfare offer trace and targeted floor repairs (2026-07-23)

USER DIRECTION: identify Fanfare cards that are skipped or underperforming and
buff them selectively rather than applying another package-wide increase.

OFFER/PICK TRACE, 1,500 realistic runs at seed 11: the assigned drafter already
passes most obvious low-output glue. Early pick rates were Dress Rehearsal
5.3%, Curtain Cue 5.3%, Crowd Work 6.0%, Tempo Change 6.6%, and Audience
Participation 9.6%. Those cards do not explain the low result by being forced
into decks; the policy mostly avoids them.

The more important signal was OVERPICKED underperformance. Early take/pass Act
rates when the same card was offered (directional, not randomized) included:
Suffering for Art 11.2%/20.4% at an 81.4% pick rate; Ebb and Flow 11.0%/18.4%
at 84.0%; Hearts Swelling 13.2%/17.9% at 87.1%; Showstopper 9.0%/17.6% at
90.8%; and The Sea Is My Stage 2.4%/18.8% at 72.4%. Florid Cadenza was picked
70.5% and remained negative in the controlled extra-card screen. These
relationships include offer-strength confounding, so the controlled seed and
individual-dose arms remain the ruling evidence.

SAFE-TARGET NULL: Thunderous Ovation and The Sea Is My Stage are absent from
the assembled Fanfare package, so they were tested first. Thunderous base
Block 3->5 moved realistic Act 15.1%->16.1%. Adding 6 Encore to The Sea Is My
Stage, with or without reducing its Energy cost 2->1, was inert at 15.2-15.3%
because the Rare appears in too few runs. Thunderous was retained as a safe
one-point floor repair; the Sea redesign was rejected.

INDIVIDUAL REPAIR MATRIX, 1,000 realistic runs plus 500 Punisher/tank fights
per arm:

- Current: 15.1% Act; deep 87.2% / 72.2%.
- Florid Spend 10->5: 14.9%; deep 89.6% / 74.0% -- reject.
- Showstopper 7+8 at 15: 17.1%; deep 91.4% / 78.6% -- poor ratio.
- Suffering self-damage 2->1: 17.3%; deep 88.4% / 75.6% -- best ratio.
- Hearts Swelling 2->1 Energy: 18.1%; deep 93.4% / 87.0% -- overheats tank.

SHIPPED TARGETED DOSE: Suffering for Art now loses 1 HP and gains 3 Encore;
Thunderous Ovation now Blocks 5 plus 4 at 15 Fanfare. Together they measured
18.2% Act / 69.5% first-elite / 35.0% second-elite at 1,000 seeds, with the
assembled package held to 88.4% Punisher / 75.6% tank.

FINAL SUITE, 1,500 runs/plan: Salon 31.2%, Spotlight 43.6%, Fanfare 18.7%.
This is a controlled +3pt floor improvement over R45 and +9.2pt over the
pre-converter world, but still far below the 40-50% target. The ceiling is
healthy and individual card buffs now have sharply diminishing returns. The
remaining high-impact work is draft selection/access: stop overvaluing harmful
isolated on-plan pieces or improve the chance that a realistic deck finds one
of the already-successful converters, without adding more power to the full
package.

## R47 -- Klee second-playtest card and Burst pass (2026-07-23)

USER FINDING: the starter/Companion uplift made Klee feel materially healthier
and produced the first Act-1 clear, but several one-Energy commons still did
too little, Fantastic Voyage was not worth taking, Burst appeared only near the
Act-1 boss, and Vermillion Pact/Durin overlapped on an amplifying-reaction
payoff Klee rarely triggers through her Pyro saturation.

SHIPPED CARD DOSE:

- Hide and Seek remains 7 Block and gains Scry 2; upgrade remains 10 Block.
- Patched Dress is 6 Block plus 3 with Spark; upgrade raises the floor to 9,
  leaving the online total at 12 rather than removing an almost-free condition.
- Alchemical Curiosity becomes 5 Block / Draw 2; upgrade is 8 Block / Draw 2.
- Bennett — Fantastic Voyage becomes gain 3 Strength, Exhaust (4 upgraded).
- Vermillion Pact moves +25%->+100% amplification (+125% upgraded). This
  doubles the base Vaporize/Melt multiplier; upgraded Melt is x3.9375, just
  below the x4 provenance detector.
- Durin no longer amplifies reactions or applies more Pyro. At end of turn it
  consumes Pyro from each enemy; each aura deals 6 damage and grants 3 Burst
  Energy (8 damage upgraded). This monetizes Klee's Pyro saturation, then
  clears a window for Hydro/Cryo to establish the next reaction.

BURST BRACKET, 500 realistic runs/plan at seed 42:

- meter 30: generic 58.4%, reaction 75.4%; Burst seen 65.8% / 91.2%.
- meter 35: generic 54.8%, reaction 64.2%; Burst seen 42.4% / 79.4%.
- meter 40: generic 51.4%, reaction 59.4%; Burst seen 24.4% / 62.8%.

DISPOSITION: 40 wins. The previous post-starter baseline was approximately
44% generic / 50% reaction, so 40 produces a controlled +7/+9-point Act-1
uplift and a 17x generic / 8x reaction increase in run-level Burst visibility
over the 60 meter, without the 30-meter arm's reaction ceiling. The Burst
payoff remains unchanged at 60 damage over three turns.

The authored 25-card Tier-0 packages are now ceiling-saturated because they
charge a 40-point kit Burst reliably (1000-fight tank reads: demolition 99.9%,
spark 95.5%, reaction 100%). Their old upper bands no longer model real drafts;
Tier 0.5 owns the upper-power comparison, while the authored batteries retain
only their matchup floors. The v0.2 median scorecard at 300 fights/seed 42 is
4.77 / 3.82 / 2.09 / 0.50 / 3.07 / 4.05 / 2.37.

## R48 -- Contextual Fanfare drafting before further card buffs (2026-07-23)

USER RULING: update the runner's Fanfare draft logic before buffing more cards,
then remeasure the realistic plan and preserve the assembled-package ceiling.

RUNNER DIAGNOSIS: the generic assigned scorer defined every non-reaction plan
as four tagged enabler/payoff cards. Furina already starts with Aria of
Recompense (five points of printed Encore/Fanfare movement), but each additional
generator still advanced that false four-card core and received a +3 assembly
bonus. The global 0.5 skip threshold then made nearly every tagged generator a
live pick. Conversely, the definition did not distinguish cards that actually
spent Fanfare for immediate output from cards that merely generated, read, or
cycled the resource.

SHIPPED RUNNER MODEL:

- Fanfare core progress has two structural halves: five points of printed meter
  movement and one direct damage/Block card with a positive Fanfare cost.
- The first output converter receives priority; further converters retain a
  smaller plan bonus.
- Additional generation has sharply diminishing value once the native five
  points are covered. Threshold/scaling readers receive supporting rather than
  core value, and a pure draw spender does not masquerade as the damage/survival
  converter.
- Printed self-damage is charged against the Fanfare-specific score even though
  it moves the meter. Fanfare uses a 1.5 engagement threshold; the other assigned
  archetypes retain the global 0.5 threshold and their existing scoring paths.
- The rule is structural (effects and resource costs), with no card-ID whitelist.

PAIRED A/B, 1,500 identical seeds with relics and potions: the legacy Fanfare
policy cleared 19.3% of Acts, survived E1 69.2% and E2 35.1%, averaged 16.09
cards, and skipped 0.0% of screens. The contextual policy cleared 24.4%,
survived E1 72.7% and E2 40.0%, averaged 15.13 cards, and skipped 8.8%.
There were 197 legacy-loss/contextual-win flips versus 120 flips in the other
direction.

The change did not reduce access to successful converters. Per-run acquisition
rates moved Dramatic Entrance 24.3%->25.0%, Crescendo 17.1%->17.9%, Flood of
Emotion 21.0%->21.4%, and High Tide 4.9%->5.4%. The cards removed from realistic
decks were the surplus generators/cyclers: Suffering for Art 19.3%->0%, Ebb and
Flow 19.0%->0%, Hearts Swelling 16.0%->0%, and Curtain Up 18.3%->0%.
Showstopper fell 17.5%->13.8%, while the self-damaging Sea uncapper fell
4.1%->0%.

THRESHOLD SENSITIVITY, 600 identical seeds: raising the Fanfare cutoff from 1.0
through 3.0 monotonically raised the measured win rate, but the 3.0 arm skipped
74% of rewards and finished with 11.43-card decks. That is the simulator's
known lean-deck pressure, not a credible human drafting policy. Retain the
moderate 1.5 threshold (about 9% skips) rather than optimize the scalar by
refusing nearly every reward.

REGRESSIONS: the final 1,500-run Furina suite is Salon 31.1%, Spotlight 43.9%,
and Fanfare 24.4%. The fixed Fanfare package is unchanged at 88.4% Punisher and
75.6% tank boss, confirming that this is an access/selection improvement rather
than more ceiling power. Klee does not enter any new Fanfare branch; its current
1,500-run assigned results are Demolition 53.4%, Spark 47.5%, and Reaction
61.6%. Reaction's current post-buff result is above the stated 40-50% Act
target, but that is independent balance evidence rather than a regression from
this runner patch.

DISPOSITION: keep the runner correction. It recovers 5.1 Act points without a
card buff and confirms that the old policy was materially understating Furina.
At 24.4%, however, Fanfare remains well below target while its assembled ceiling
is already healthy. Any next dose should improve the floor of cards that the
contextual runner still rationally skips (or broaden converter access), with
the deep Punisher/tank cells held as hard guards.

## R49 -- Thunderous Ovation defensive converter (2026-07-23)

USER RULING: Furina still needs buffs after the runner correction. Ignore the
independent Klee work and test Thunderous Ovation as a defensive Common
converter that broadens early Fanfare access without touching the assembled
Fanfare package.

SHIPPED CARD: Thunderous Ovation now costs 1 Energy plus 5 Fanfare, gains 7
Block plus 4 at the live 5-Fanfare threshold (11 total), and spends its Fanfare
after resolving. Its upgrade raises the base 7->9 for 13 total; the rider and
Fanfare price stay fixed.

The first 5+4=9 Block version succeeded at access but not survival. In a paired
1,500-seed A/B it raised Thunder's early pick rate 66.5%->90.4% and Fanfare
core-online-by-E1 39.1%->49.1%, yet Act clears moved only 24.4%->24.9% and E1
survival fell 72.7%->72.1%. The loss of its unconditional pre-meter fallback
roughly canceled the value of the new conversion route.

BLOCK BRACKET, 800 identical seeds with Spend 5 and every other rule fixed:
9/10/11/12 total Block produced 24.0%/24.4%/25.0%/24.9% Act clears. Eleven is
the smallest saturated value; twelve adds no measured win rate and was
rejected.

FINAL PAIRED A/B, 1,500 identical seeds: the pre-change card produced 24.4%
Act / 72.7% E1 / 40.0% E2. The 11-Block converter produced 25.9% / 72.8% /
41.3%, with 41 old-loss/new-win flips versus 19 in the other direction.
Thunder's early pick rate rose 66.5%->93.7%, and core-online-by-E1 rose
39.1%->49.1%.

FINAL SUITE: Salon 32.4%, Spotlight 44.9%, Fanfare 25.9%. The fixed Fanfare
package remains exactly 88.4% Punisher / 75.6% tank boss, because Thunderous
Ovation is absent from that package. The change is therefore a safe +1.5-point
realistic-floor repair with no measured ceiling movement.

DISPOSITION: retain the 11-Block defensive converter. It is not the whole
Fanfare answer—E1 is flat and Act clears remain far below target—but it
successfully adds a second Common conversion axis and improves later survival.
Continue with targeted floor/card-quality work rather than global Fanfare
power.

## R50 -- Dry Salon floor valve and playtest-ready aggregate (2026-07-23)

USER DIRECTION: raise Salon and Fanfare without making the already-leading
Spotlight plan automatically stronger, then move to real-game feel testing if
the overall Act-1 clear rate approaches 40%.

TESTED FLOOR VALVES:

- Salon: dry Member ticks deal 75% rather than 50% power—3 versus the paid
  tick's 4 damage. Paid ticks, replacement bows, slot count, Encore upkeep,
  and all authored card numbers are unchanged.
- Fanfare: Dramatic Entrance and Thunderous Ovation were tested as fail-soft
  Commons, playable for their 6-damage/7-Block base below 5 Fanfare and paying
  nothing unless fully charged.

ISOLATION, 800 identical seeds: the old Salon/Fanfare rates were 32.9%/25.0%.
Dry ticks alone produced 38.8%/26.0%. Fail-soft Commons alone produced
32.8%/24.1%; combined produced 38.6%/25.5%. The Fanfare fallback is rejected:
the pilot spends Energy on the ordinary branch instead of waiting for a charged
conversion, reducing rather than improving the plan.

A simpler hard-gate price bracket was also rejected. With dry ticks retained,
Common converter Spend 5/4/3 produced 26.0%/26.4%/26.4% Fanfare at 800 seeds.
The gain saturates at four tenths of a point and would make Dramatic Entrance
more efficient inside the already-healthy assembled package.

SHIPPED CHANGE: only `SALON_DRY_DAMAGE_MULT` 0.50->0.75. The Common converters
retain their hard Spend-5 gate and R49 numbers.

FINAL SUITE, 1,500 realistic runs/plan: Salon 38.6%, Spotlight 46.7%, Fanfare
27.5%. The equal-plan aggregate is 37.6%, up from R49's 34.4%. Spotlight gains
only 1.8 points from the universal starter Member while Salon gains 6.2, so its
lead narrows rather than widens.

ASSEMBLED CHECK, 300 fights/cell, old->new dry multiplier:

- Salon: Punisher 98.7%->99.3%; tank 99.3%->99.7%.
- Spotlight: Punisher 86.0%->87.0%; tank 78.3%->78.7%.
- Fanfare: Punisher 88.7%->89.7%; tank 74.3%->75.3%.

The completed Salon package was already ceiling-saturated; the movement is
small and does not create a new matchup result. The realistic gain is
concentrated where intended: incomplete Salon decks that run out of upkeep.

DISPOSITION: Furina is playtest-ready at a 37.6% equal-plan Act aggregate.
Stop simulator tuning here and use real play to judge whether dry Members feel
appropriately weakened, whether hard-gated Common converters create engaging
meter decisions or frustrating dead draws, and whether the 27.5% simulated
Fanfare plan understates a human pilot's ability to wait for charged turns.

## R51 -- Kokomi elite axes: A2+A6, stability band owns the healer fantasy (2026-07-24)

USER RULING (closes kokomi-kickoff-v1 ask 4; routes session ask N2): Kokomi's
elite pair is A2 Scaling + A6 Utility, replacing the kickoff's "A2 + A4
Utility" wording — the A4 terminology clash is discharged. The healer fantasy
moves entirely to the stability band (HP-trajectory flatness) in the act-level
realistic sims, which the kickoff §3 already pre-registered as her acceptance
signature. A4's instrument is NOT redefined: ward prevention stays a reported
telemetry stream (FightStats.prevented) feeding the stability band, never
axis-credited.

TEXTURE CONSTRAINT (user, verbatim intent): Weak and Vulnerable enter her pool
as riders on exhaust / Sly engine pieces — "they go in the kit but as engine
payoffs, not a spammable '1 cost aoe weaken' like Furina gets." The Furina
commanding_gaze pattern (cheap standalone AoE debuff) is explicitly excluded
from her pool. Debuffs are earned by running the exhaust/Sly engine, which
also keeps the hydro-convergence watchlist honest: her A6 texture is
mechanically distinct from Furina's even where the status names overlap.

SCOPE NOTES: measured A6 median is 2.2 in the v0.1 battery, so elite A6 is a
statement about the upcoming full sheet pass (authoring work: Weak/Vuln
riders, application uptime, AoE packaging incl. surging_shoal), not about the
v0.1 roster. Remaining instrument questions — A4/ward credit (N2), starter
weakness (30.5% wr), Gardener-card packaging — are routed to the tier05
act 1-3 realistic sims; tier0 batteries retain unit/anchor/lint duty only.
Also accepted in the same thread: the test_fontaine_rewards 5-star assertion
update (pins the mondstadt-or-inazuma construction) and the in-session
vigil-packaging and domination-lint catches.

## R52 -- Kokomi kickoff asks: batch closure (2026-07-24)

USER RULINGS (closes kickoff asks 1-3, 5-10 and session asks N1, N3, N5;
ask 4 / N2 were closed in R51):

- N1 cadence: CATALYST. Every attack applies hydro — the application-uptime
  third of elite A6 becomes structural rather than authored.
- Ask 8 statline: hp 70 / energy 3 / starter composition (3x waters_edge,
  3x coral_guard, bake_kurage, 2x tactical_recall, tide_reading) with the
  reserved companion slots — pinned as the starting point; numbers stay knobs.
- Ask 2 deck-size grammar: approved as written, Kokomi-pool scope ONLY;
  lint_kokomi_decksize remains the in-suite gate.
- Ask 6 finisher: keep both-with-capstone (Ceremonial Garment kit Burst +
  Nereid's Ascension rate-limited Rare); the act-level sims arbitrate.
- Ask 1 healing: NO amendment — and none planned, ever. Furina already holds
  the mod's one healing amendment; Kokomi's rares pay off a different way.
  CONSEQUENCE: sango_prayer (heal 12, Rare+Exhaust) is cut as authored and
  reworked to a non-heal payoff in the v0.2 sheet pass. The healer heals no
  HP: her sustain fantasy is prevention (ward) plus the stability band.
- Ask 5 Charge accrual: universal exhaust->Charge through the single funnel,
  as implemented.
- Ask 7 SUPPORT_CARRY: conscripted companions count as base kit
  (self-sourced); drafted companion cards count normally. As implemented.
- N3 starter trio: Gorou always enlists (lore ruling). The three-name /
  two-slot asymmetry is intended; no fourth shortlist name.
- N5 conscript rarity: leave natural rarity odds — the Itto 5-star jackpot
  stays in the pool; reconsider only if sims show him busted.
- Ask 3 A1>A2 invariant: the Klee law was Klee-scoped; there is no mod-wide
  invariant. Kokomi's per-identity constraint A2>A1 stands on her own sheet.
- Ask 9 Raiden: playable characters MAY also exist as Rare companion cards,
  and may appear in Kokomi's conscript pool — but only as a Rare payoff.
  Lorewise Kokomi and Raiden are opposed; the flavor must carry that tension.
  (User notes the playable-as-companion ruling may not have been formally
  ratified before; it is ratified here for this case.)
- Ask 10 naming/lore audit: deferred to the full sheet, pre-C-milestone,
  as designed.

Not explicitly addressed: N4 (burst meter 50, KOKOMI_BURST_PER_EXHAUST 2) —
treated under ask 8's "pinned starting point" umbrella: knobs, tuned by sims.

DISPOSITION: every kickoff gate is closed. The v0.2 sheet pass proceeds under
R51's texture constraint (Weak/Vulnerable only as riders on exhaust/Sly
engine pieces), with sango_prayer reworked, Raiden authored as an
opposed-lore conscript-pool Rare, a kokomi-upgrades sheet added (rest-smith
dependency), and the tier05 drafter taught her verbs (DRAFTER_VERSION-
stamped) before any act 1-3 number is read.

## R53 -- Kokomi basics stay at Strike parity; v0.3 committed for review (2026-07-24)

USER RULING: waters_edge does NOT go to kaboom parity (7) -- her basic
attack remains at basic-Strike parity (6). The kaboom-parity arm from the
v0.3 charge-curve grid is rejected; its ~5 act-1 points are not bought
through the basic.

CONTEXT: the rest of the v0.3 charge-curve world (Regent-shape commons,
GARMENT_CHARGE_DIVISOR /2, riptide_strike, fast-cycle Burst meter 10,
starter S3 swaps -- sheetpass report §6) is committed AS PROPOSED for a
later card-by-card review. The user flags that the world may diverge too
far from the character's actual identity; the §6.4 tension (ruled A2>A1
constraint violated by the fast-cycle Garment's frontload signature, median
TOO_STRONG) is the open question that review will decide (options O1-O3 on
file). Nothing in the v0.3 numbers is ratified by this commit.

COMMITTED WORLD (waters_edge 6, re-measured before commit): see report
§6.3 for the final labeled table.

## R54 -- Kokomi v0.4: O4 is the primary arm, O1 rejected, O2 in reserve (2026-07-26)

USER RULING (plan asks 1-3, 5; docs/archive/kokomi-v0.4-plan.md is the governing
doc, ruling answers in its §7):

- **O1 REJECTED.** Accepting the v0.3 world by redefining the instrument or
  re-declaring the elite pair post hoc is not available -- that is the R33
  culture line. The measurement stands; the design moves.
- **O2 = reserve fallback** (Garment splash 7 / turns 2), unexercised.
- **O4 = primary arm, EXECUTED.** The periodic output moves off the Burst
  and onto the summon, where canon keeps it: Bake-Kurage becomes a
  persistent summon that pulses at turn end reading the Charge bank, the
  Garment gains its canon riders (attack-Block + the Tamakushi refresh
  link), and the meter goes back to being a real Burst (10 -> 20).
- **Sequencing W1 -> W2 -> W3 ratified**; knob defaults ratified as
  proposed; meter bracket 15/20/25 ratified; prediction (c)'s acceptance
  band 35-50% confirmed, with Furina 57 / IC 59 as ceiling-side reference
  and NOT a requirement.

MEASUREMENT CONVENTION ESTABLISHED (W1, binding): the Kokomi act numbers of
record are `--realistic` runs at 500 runs / default seed. The committed v0.3
world reproduces its recorded four pairs exactly under that invocation
(priest 32/2.0, commander 49/1.6, generic 26/0.4, assist 20/0.0). The SAME
world at bare loadout reads priest 3% / commander 4% act-1 -- the
relic/potion layer is most of the act-1 clear. Comparing across the two is
comparing two different worlds.

PREDICTIONS GRADED IN WRITING (plan §2; hits and misses both, report §3):
(a) starter A1 falls below A2 -- **MISS at every meter step**.
(b) TOO_STRONG clears at archetype median -- **HIT** (and the median now
    satisfies A2>A1 outright: 5.2 vs 3.6 at meter 20).
(c) act-1 lands 35-50% at meter 20-25 -- **PARTIAL** (500-run confirm at
    meter 20: commander 45% in band, priest 30% under).
(d) Garment-uptime watchlist retires by construction -- **PARTIAL**
    (priest 57% -> 23% uptime, retired; commander 76% -> 50%, not retired).

The plan's fallback trigger ("misses on (a)/(b) at EVERY meter step -> fall
back to O2") did NOT fire, because (b) hit. O4 therefore stands as landed
and (a) goes back to [USER] as an open ask -- see the report's §4 finding
that (a) is a STARTER-COMPOSITION property, not a Garment property, which
contradicts the v0.3 report's §6.4 diagnosis.

## R55 -- Kokomi lore overlay: the rename batch and the voice law (2026-07-26)

USER RULING (plan ask 4; naming audit is [USER]-only). Landed in W3,
measurement-neutral by construction -- display names and comments only, ids
stable except the one noted:

- **VOICE LAW (binding for the sheet and every future card face):** Exhaust
  in Kokomi's fiction is ROTATION, never sacrifice. Units rotate off the
  field rested and whole; Charge is the strategic position each executed
  maneuver buys. Her doctrine is minimal casualties, and the sacrifice voice
  is the one reading that breaks the character. `tactical_recall` is the
  exemplar; `grand_conscription`'s "the army becomes fuel" was the marked
  counter-example and is rewritten.
- **Conscription family renamed** (forced service is Shogunate behaviour;
  the resistance were volunteers). Op name `conscript` stays internal;
  display moves to Muster/Enlist/Rally: conscription_notice -> "Call to
  Arms", mass_mobilization -> "Rally the Isles", grand_conscription ->
  "General Muster of Watatsumi". to_the_front / field_promotion /
  reinforcements keep their names.
- **`riptide_strike` -> `all_streams_flow`, ID-LEVEL** (the one id rename;
  landed BEFORE W2 so the arm was born with the right name). Riptide is
  Tartaglia's signature mechanic -- a cross-character collision inside
  Genshin. "All Streams Flow to the Sea" is her C5 and means exactly what
  the card does.
- **Other renames:** jade_bulwark -> "Pearl Bulwark" (jade is Liyue-coded;
  Watatsumi is coral and pearl); mercy_of_the_deep -> "Mercy of the
  Currents"; vigil_of_the_deep KEEPS its name (it is the ward's name and it
  is earned); depths_judgment -> "Sango Isshin" ("Judgment" is
  Fontaine-coded; Sango Isshin is her C6, wiki-verified);
  sayu_yoohoo_windwheel -> "Sayu — Yoohoo Art: Fuuin Dash".
- **Private-characterization renames** (the drained introvert, the secret
  novel reader, the wish for quiet): tide_reading -> "Stolen Chapter",
  moon_signal -> "A Moment Alone", and the optional third LANDS --
  undertow_shuffle -> "Daydream of a Quiet Life". Effects unchanged.
- **Relic swap:** the starting relic is displayed as **"Pearl of Wisdom"**
  (NOT the drafted alt "Everlasting Moonglow"). "Tamakushi Casket" moves to
  the mechanic canon actually names -- the Garment-refreshes-Kurage link.
  Relic mechanics unchanged; the hook IDENTIFIER stays `tamakushi_casket`
  (ids are stable across this overlay, and it now sits on the engine
  powering the link it is named for). CONSEQUENCE: the relic took "Pearl of
  Wisdom", so epiphany_of_the_deep could not have it -- it takes **"Song of
  Pearls"**, her wiki-verified 4th Ascension passive.
- **Raiden KEEPS "Musou no Hitotachi"**; the gloss flips from irony to
  RECONCILIATION. The retired reading had Kokomi fishing for the blade that
  executed her people's Visions; the true gloss is the peace's crowning
  proof -- the Shogun's blade defends Watatsumi now.
- **"The pool is the peace, not her army"** lands as a companion-sheet
  framing note: the roster spans every Inazuma faction because it is
  post-Decree Inazuma answering Watatsumi's call, not a resistance muster.

WIKI RE-VERIFY (the plan's header audit ask; the wiki is the instrument,
not anyone's memory): **"The Moon's Beauty" is NOT a Kokomi name** and has
been struck from the sheet's verified list -- the header audit ask was
correct. Confirmed canon: Kurage's Oath (Elemental Skill, which summons the
Bake-Kurage), Nereid's Ascension (Burst), Ceremonial Garment, Tamakushi
Casket (A1 passive: casting Nereid's Ascension refreshes a fielded
Bake-Kurage -- exactly the link O4 models), Song of Pearls (A4), Princess of
Watatsumi (innate), C1 At Water's Edge / C5 All Streams Flow to the Sea /
C6 Sango Isshin. Beta-era sources carry "Kaijin Ceremony" and "Haworthia
Casket" for the Burst and A1 passive; those are pre-release names and are
noted as a trap in the sheet header.

## R56 -- Kokomi v0.4b: the 12-card starter, the x4 bank read, Kurage's Oath (2026-07-26)

USER RULING, same day as R54/R55 and SUPERSEDING their statline conclusions.
R54 chose meter 20 on a 10-card starter with a /4 bank read; this ruling
rebuilds the starting deck and flips the read to a multiplier. R54's act
numbers are a superseded world -- never compare them unlabeled.

**The starter is TWELVE cards, the Silent shape**: 4 Water's Edge + 4 Coral
Guard + 2 companions (Gorou fixed, Sayu-or-Shinobu rolled) + 2 mechanic
cards (Bake-Kurage for Charge, Tactical Retreat for exhaust). Rationale:
her opening deck carries exhaust, so a 10-card self-milling deck risks
decking out; and starters are SUPPOSED to be bad and supposed to leave, so
two more mediocre cards is a real dilution cost that Tactical Retreat's
thinning pays down. Companions are now ADDITIONS, not replacements.

**waterspout and surging_shoal are OUT of the starter.** USER RULING: "no
one starts the game with AoE; if you need it, you draft it." Both stay in
the pool; surging_shoal was in NO package and would have become unreachable
(the vigil defect), so it is now a priest + commander draft-in.

**The Kurage pulse read flips from divisor to MULTIPLIER**:
KURAGE_PULSE_PER_CHARGE = 4 (was: +1 per 4 Charge). Design intent: every
Exhaust is worth about a Silent shiv toss. KURAGE_DURATION 3 -> 1,
KURAGE_PULSE_BASE 2 -> 4, KURAGE_PULSE_BLOCK 2 -> 0.

**THE ASSISTANT'S "x4 IS TOO HOT" OBJECTION WAS WRONG AND IS WITHDRAWN.**
It was argued from the internal §2.2 reader hierarchy and from act-1 clear
measured against STALE anchors. [USER] countered with the StS2 precedent:
Necrobinder starts with a 1-cost "Osty gains 5 HP" and a 1-cost "deal 3 +
Osty's HP" -- unbounded starting-deck scaling is something the actual game
designers ship. Re-measuring the anchors in the current world settled it:
act-1 clear is NOT the binding metric (Klee clears 83% of act 1 and wins
3.4% of runs). On RUN winrate x4 is mid-cast. Standing caveat, [USER]'s
own: Osty's HP can go DOWN with bad play, Charge only goes up -- so this
is watched in act 3, where it does not in fact run away (6% vs Furina 13%).

> **SUPERSEDED BY R73 (Neap Tide v2.1, 2026-07-26; addendum A7 pointer.)**
> The multiplier is now **3**: R73 ruled 4 -> 2, and `exp_neap_tide_e1`
> graded P6 and fired the pre-committed weak-side fallback, so x2 shipped in
> no build. `CONSTANTS_VERSION 4` -- every Kokomi number in this entry is
> archive. The withdrawal above still stands on its own terms (x4 was not
> the runaway the objection claimed), and the cut was made for the reader
> hierarchy rather than for act 3. Note also what R73 did NOT settle: G2
> ratified a stacking `kurage_amp` card, so the coefficient this entry
> treats as fixed is now drafted, and 4-5 is an ordinary in-run read.

**PREDICTION (a) NOW HITS.** R54 graded "starter A1 falls below A2" as a
MISS at every meter step. Under the 12-card starter it PASSES: A1 3.2 vs
A2 4.8. Isolated at x0 (bank read fully OFF) the constraint ALREADY passes
at A1 2.8 vs A2 3.5 -- so the fix is the COMPOSITION, not the multiplier,
confirming the R54 report's §4 finding by direct experiment. waterspout
(10 flat) and surging_shoal (7 AoE) were her frontload. The multiplier
buys A2 depth and clear rate on top. Median passes too (A1 3.7 / A2 5.1).

**NEW CARD -- Kurage's Oath** (Common power, 1 cost, `kurage_ward`): while
it holds, every Kurage pulse also grants Block. This drafts back the
mending half of the canon Bake-Kurage ("deals Hydro DMG and heals nearby
characters at set intervals") after the baseline pulse Block was zeroed --
the healer fantasy becomes an opt-in build rather than a freebie. Upgrade
buys INNATE ONLY; the Block does not move.
NUMBER IS MEASURED, NOT REASONED: drafted at 5 by ratio off Regent, it was
a TRAP PICK (priest run 3.8% WITH it vs 5.8% without). Bracket: ward 5 ->
3.8%/5.4%, ward 8 -> 4.8%/5.8%, ward 12 -> 6.2%/5.8%. The ratio had to go
UP for the cheaper trigger: Regent's finisher is played reliably, while
Bake-Kurage is one copy in a growing deck pulsing ONCE per play at
duration 1. **RULED at 12, with [USER]'s flag on the record: "I feel like
that's too strong, but we can rebalance later."** First knob back.

**MEASURED WORLD (500 runs/plan, --realistic, DRAFTER v8):**
priest 6.2% run (act 56/27/6); commander 5.8% (65/37/6); generic 2.0%
(46/16/2); assist 1.6% (44/14/2). Anchors re-measured same world: Furina
13.4%, real_ironclad 3.6%, Klee 3.4%, ref_ironclad 0.6%. She lands above
Klee/Ironclad and below Furina on every stage.
Meter 20 re-checked in the new world and KEPT (15 -> 9.3/8.7% run,
20 -> 6.7/7.7%, 25 -> 4.0/6.0%).

**OPEN, logged not acted on:** [USER] -- "maybe the Burst needs to be
reworked entirely; refreshing something that never expires was also a dud."
The Tamakushi Casket link is inert at KURAGE_DURATION 1 (a fielded Kurage
is always at exactly 1, so refresh-to-full is a no-op). The mechanic stays
in code and stays test-pinned via a raised duration, so restoring a longer
duration is safe; the Burst rework itself is a future conversation.

## R57 -- Playtest sprint Track P: pins, telemetry, and a world that moved (2026-07-25)

Track P of the Kokomi Playtest Build sprint. Scope as ratified: pins and
telemetry only, zero balance changes (the sprint's freeze rule -- the
variable under test is the MEDIUM, not the numbers). Everything below is
instrumentation or measurement; no dial moved.

**P1 -- the Oath coupling pin (LANDED).** `kurage_ward` 12 pays out once per
Kurage pulse, so its real value is (ward x pulses per play). It owns only the
first factor: the second lives in `KURAGE_DURATION` and the bake_kurage
`kurage_turns: +1` delta, neither of which the Oath's own tests touch. A
duration change therefore reprices a Common power that already carries a
[USER] "maybe too strong" flag, silently and from another file.
`test_oath_ward_is_pinned_to_the_pulse_frequency_it_was_measured_at` now fails
on that edit, and reciprocal notes sit at BOTH ends (the sheet row and the
constant) because the person raising the duration reads constants.py, not the
Oath's row. Pin verified to fire: forcing KURAGE_DURATION to 2 fails it.

**P2 -- runaway telemetry (LANDED).** `kurage_pulse` is emitted at the pulse
site with its size and the bank that produced it; `tier05/kurage_telemetry.py`
reports p50/p95/max by act. Report-only, and silent for every character that
never fields a Kurage. Rationale: the runaway failure mode is INVISIBLE in win
rate (a kit that one-shots act-3 elites still reports a win, and reports it as
success), so [USER]'s standing "watch act 3" caveat becomes a column instead of
a thing someone has to remember. Pulses into an empty board are counted --
they are samples of the CURVE, and dropping them biases the tail down exactly
when fights end fast.
First reading (500 runs, --realistic, current world), act1 / act2 / act3 p95:
priest 64 / 116 / 152; commander 56* / 128 (act 3 p95); generic 44 / 108;
assist 44 / 100. Mean bank at pulse time reaches 16.6 in act 3 (priest).
The curve roughly doubles act 1 -> act 3 and then flattens. NOT a runaway on
this evidence; the tail is now watched by construction.

**P3 -- commander Garment-uptime criterion (WRITTEN).** The v0.4 watchlist was
carried forward with no terms, which makes it un-retireable. Terms, registered
here and not to be redefined mid-sprint:
  RETIRE  if long-fight uptime holds < 60% through the Burst rework.
  ESCALATE if it goes past 70% (a permanent multiplier wearing a Burst's
           clothes -- the v0.3 failure mode, restated).
  Neither -> stays a watchlist entry, unchanged.
Current value stands at the v0.4 measurement (50.1% overall / 58.7% in long
fights), i.e. just under the retire line and not yet retired. The playtest
supplies the felt half (protocol item 2).

**P4 -- skeleton-test debt: INVESTIGATED, NOT REPRODUCIBLE.** Went further
than "log it as debt", and the result is a null.
FIRST, a real defect in the plan's own premise: the `wip-safety-net` tag named
as the reproduction handle DID NOT EXIST. The stash was empty, and commit
`deba245` was reachable from no ref and no reflog entry -- a dangling object
awaiting gc, i.e. the handle the plan proposed to preserve was already gone.
Re-created as an annotated tag before it could be pruned; it now anchors the
entire pre-merge Kokomi WIP tree (12 files).
SECOND, with the handle restored, `test_build_kokomi_skeleton` PASSES at
deba245 and passes at HEAD. The only tree that ever exhibited the failure was
the CONFLICTED MERGE working tree, which was never committed by anyone, so
there is no artifact that reproduces it and there never will be. Logged as
CLOSED-UNREPRODUCIBLE rather than as standing debt: leaving it open would
imply an investigation that no preserved state can support. Do not delete the
tag until someone decides that WIP tree is worthless.

**P5 -- deck-size survivorship split (LANDED, and it answers its question).**
`avg_final_deck` now reports won/lost alongside the pooled figure. The 21.7-24.2
soft-cap ride was ambiguous by construction: heavy decks and short deaths push
the mean in opposite directions. Split, it is unambiguous --
  priest 25.4 (won 33.5 / lost 24.8); commander 25.0 (31.7 / 24.3);
  generic 24.5 (33.8 / 23.9); assist 23.1 (31.2 / 22.9).
WINNERS' DECKS ARE UNIFORMLY THE BIG ONES, by 7-10 cards. The soft-cap ride is
survivorship, not bloat: runs that live longer draft more. Deck size is not a
cause of death in any lane. LAW 4 needs no action.

**THE FINDING -- the world moved, and the R56 numbers are stale.**
Nobody touched Kokomi. RUNTEMPLATE 7 (acts 2-3 event pools) and DRAFTER 9
landed on main from the Furina workstream, and the whole roster inflated.
Re-measured, same command, 500 runs, --realistic:
| lane / anchor | R56 (DRAFTER v8) | now (DRAFTER v9 + RUNTEMPLATE 7) |
|---|---|---|
| Kokomi commander | 5.8% | **9.6%** |
| Kokomi priest    | 6.2% | **7.0%** |
| Kokomi generic   | 2.0% | **6.8%** |
| Kokomi assist    | 1.6% | **2.0%** |
| Furina salon     | 13.4% | 18.2% |
| Klee demolition  | 3.4% | 9.2% |
| real_ironclad    | 3.6% | 8.0% |
| ref_ironclad     | 0.6% | **7.4%** |
Her ABSOLUTE numbers rose; her RELATIVE position did not improve -- against
real_ironclad she went from 1.7x to 0.9x (priest) and 1.6x to 1.2x
(commander), and against Furina from 0.46x to 0.38x. She remains mid-pack:
at or just above the Ironclad anchors, far below Furina. **The freeze rule is
therefore SAFE on the evidence** -- she does not need a rebalance to be worth
playtesting, and the playtest is still the right next instrument.
SEPARATE CONCERN, flagged for the Furina/roster workstream and NOT acted on
here: `ref_ironclad` moved 0.6% -> 7.4%, a 12x swing in the FROZEN reference
battery. A reference anchor that moves that far invalidates cross-world
comparison against every archived number in this file, including R56's. That
is a roster-level instrument question, not a Kokomi one.

**ANOMALY, recorded because burying it would be worse.** The first
instrumented 500-run priest cell read 8.4%; every subsequent run of the same
command on the same tree -- six of them, including four with varied
PYTHONHASHSEED -- reads 7.0%. Instrumentation was verified INERT by
revert-and-compare (removing only the emit reproduces 7.0% exactly), and
RunResult is keyword-constructed so the added field cannot shift anything.
Cause NOT established. A concurrent session was writing the repo during that
window (mod-side files only, per mtimes), which is suggestive but unproven.
Recorded as an open trust question about single-cell measurement, in the same
family as the `--realistic` catch that nearly caused a false regression call.
Treat any single 500-run cell as provisional until repeated.

## R58 -- Kokomi v0.5 partial fill: the pool was half-sized (2026-07-25)

**[USER] CATCH, and the repo could not have made it.** Mid-sprint, [USER]
asked how many cards Kokomi was getting: "the other decks were scoped for
75-80 in total." Her personal pool was **38** against Klee 76 and Furina 78 --
short at every rarity (common 13 vs 32, uncommon 12 vs 25, rare 8 vs 15).
Nothing had regressed: the sheet has been 38 rows since the v0.2 pass and
every R56/R57 number was measured against it. That is exactly why no
instrument reported it. The run sim measures winrate, and a thin pool does not
lower winrate -- it lowers VARIETY, which only a human at the table feels.
Same family as the reserved-card-names catch (see the structurally-invisible
defects note): a check that needs data the repo does not hold.

**RULING ([USER]): fill partway with cards that make logical sense; carry the
rest to a design pass AFTER early playtest results.** Executed as +12 common
(13 -> 25) and +8 uncommon (12 -> 20), 3 per lane at common and 2 per lane at
uncommon so the fill does not silently re-weight the archetypes. Rares
deliberately untouched at 8: draft variety is felt where the offers come from,
and rares are the slot most likely to be redesigned once play says which of
her lanes is real. Personal pool 38 -> 58.

**STILL OPEN (post-playtest design pass):** common 25/~32, uncommon 20/25,
rare 8/15 -- roughly 20 cards short of roster parity. Art bill rises with it:
53 personal faces today, ~91 at parity, against the ~8 clean large
illustrations that forced the widened-source ruling.

**FREEZE RULE.** Not violated, not quietly widened: no existing row is edited.
New rows carry new numbers, which is unavoidable, so this is logged as an
explicit [USER]-directed exception rather than folded in. All new numbers are
PROPOSED and all new NAMES are AUTHORED-NOT-AUDITED (the naming audit is
[USER]-only; it ran at v0.4 and has not run on this block).

**NEW GRAMMAR: threshold predicates.** `charge_at_least_N` (new) and
`exhaust_pile_at_least_N` (existed sim-side, taught to codegen). A threshold
is NOT a §2.2 proportional read -- it pays a flat printed bonus once a bar is
cleared and then stops, so it cannot feed the multiplicative-read risk the
per-point readers are rate-limited for. Charge bars are uncommon+ only. Both
threshold cards are encoded base-plus-bonus rather than either/or so the
upgrade moves the always-live half and the BAR CANNOT DRIFT DOWN -- lowering a
threshold is a resource-curve move, which the Klee R1 law forbids. Pinned by
`test_threshold_bars_do_not_move_on_upgrade`.

### Four defects the fill surfaced. Three were already shipped.

1. **Sly branches were never checked by `blocked_reason`.** It read `effects`
   and nothing else. `tidal_lure`'s sheet says Vulnerable 1 to a RANDOM enemy;
   the apply_power emitter treats anything-but-"enemy" as all-enemies; the
   guard that would have caught it never looked. The card generated, compiled,
   and debuffed the whole room. FIXED both ways: the Sly view now runs through
   `blocked_reason` like any other card, and apply_power learned
   `random_enemy`. An unchecked branch is not a smaller surface, it is the
   same surface with the alarm disconnected.
2. **Sly branches reused the played face's DynamicVars.** `drifting_lantern`
   (played 4 / Sly 4, upgrade +2) upgraded its Sly Block to 6, which the sim
   never does; `driftglass` would have dealt 8 on discard instead of 5; and
   `quiet_harbor`/`whispered_word` referenced a `Cards` var their cards do not
   declare at all. FIXED: `_sly_view` stamps `_sly_branch` and every amount in
   a Sly branch renders LITERAL, which is what the sim does (no sly-delta key
   exists in the applier).
3. **No Sly card's FACE mentioned Sly.** `drifting_lantern` -- the sheet's
   self-declared "Sly teaching card" -- printed "Gain 4 Block." and taught
   nothing. FIXED: the face now carries a `[gold]Sly[/gold]: ...` clause built
   from the same text emitter. A mechanic a player cannot read does not exist
   at the table.
4. **LAW 4's accounting had a hole.** `tools/lint_kokomi_decksize.py` knew
   three card-minting ops; the copy family was invisible, so a Common carrying
   `copy_companion_in_hand` would have netted +1 and passed clean. FIXED: the
   copy family is enumerated, and the unbounded
   `copy_companions_played_this_combat` counts as the whole hand rather than
   being guessed at 1. Guarded by `test_decksize_lint_counts_the_card_copying_ops`.

Two pre-existing codegen blockers also cleared, both over-broad guards rather
than missing machinery: `exhaust_from amount > 1` is expressible on the CHOSEN
branch (one multi-select prompt IS the sim's pick-worst-repeat; only the
random re-pool loop was never built), which unblocked `cleansing_tide` -- a
COMMON that had been shipping with no C# card at all. Kokomi codegen is now
**57 of 58**, the remainder being the kit Burst.

### Measurement (500 runs/lane, --realistic, post-fill)

| lane | pre-fill (R57) | post-fill | Wilson 95% |
|------|------|------|------|
| priest    | 7.0% | 8.4% | 6.3-11.2% |
| commander | 9.6% | 8.8% | 6.6-11.6% |
| generic   | 6.8% | 7.0% | 5.1-9.6% |
| assist    | 2.0% | 1.4% | 0.7-2.9% |

**READ THIS AS A NULL.** Every interval overlaps its pre-fill value; +20 cards
moved no lane outside noise. That is the expected and desired result -- the
fill was for a HUMAN-felt property the sim does not measure, and a fill that
had moved winrates would have meant the new cards were mispriced. The priest
cell reading 8.4% is noted only because R57's unexplained anomaly produced
that same number; nothing is inferred from it, and R57's standing rule holds:
treat any single 500-run cell as provisional until repeated.

**ONE SIGNAL WORTH THE NEXT PASS:** assist stays a distant last (1.4% against
7-9%, online in 20% of runs, median 11 fights) and did NOT move despite taking
5 of the 20 new cards. The sheet declares the lane "LOW INTERNAL PAYOFF BY
DESIGN" (Box Trick philosophy), but a 6x spread is a different claim from a
low payoff. Flagged for the post-playtest design pass, not acted on inside the
freeze.

## R59 -- Shop slot 2 floor: Uncommon (2026-07-25)

Slot 2 is wildcard-nation, **Uncommon-or-Rare** at renormalized reward odds.
Preserves the premium-paid-channel thesis: base slot 2 is a guaranteed Rare, so
a wildcard at full reward odds (~60% Common) would make the mod's shop *worse*
than base at the exact slot whose whole argument is that it is premium. Matches
the companion-value study's finding that StS2 colorless has **no common tier**.

The tiebreaker was banner robustness. A guaranteed-Rare slot 2 interacts badly
with nation-scoped banner gating: runs where the banner thins a nation's Rare
tier leave a guaranteed-Rare slot drawing from a near-empty eligible set. Base
StS2 never had this problem because base colorless has no banner. Guaranteed-
Rare rejected as brittle; as-written (full reward odds) rejected as
self-contradicting.

**Live instance, not hypothetical: Fontaine ships ZERO Rare companions today**
(Mondstadt 3, Inazuma 2, Fontaine 0). Furina's home-nation slot 1 already
cannot roll a Rare regardless of banner state.

## R60 -- Base colorless pool: shop-only override now, removal deferred (2026-07-25)

Phase 1 (this sprint): the merchant's colorless entries draw from the companion
pool. `ColorlessCardPool` **stays populated** for its six non-shop consumers,
including all three `GetDistinctForCombat` sites. Emptying it is the exact
empty-draw softlock class already paid for once (Dusty Tome ->
`lint_ancient_coverage.py`); full removal demands a seven-consumer audit plus
per-site invariant tests, which is a sprint of its own. §4.7's rejection of the
"additive model" argued *reward-economy* fantasy dilution, which does not
automatically extend to Discovery-style in-combat generation the player never
drafts.

**Deferred, not rejected:** whether base colorless surfacing via in-combat
generation is a fantasy leak worth phase 2's blast radius is a taste call.
[USER] grades it after phase 1 is live at the table. Until graded, phase 2 is
not scheduled and no prep work rides along.

## R61 -- The sim models the shop channel (2026-07-25)

Companions become shoppable in `tier05/shop.py` (slot 1 nation-filtered +
Uncommon floor, slot 2 per R59, gold pricing by drawn rarity). §4.7's thesis is
that *pricing is the balance governor*; an unmeasured governor is a design
claim with no instrument attached.

Distinguished from R2's relic exemption: that is a static effect, this is an
economy channel. This also answers the compounding question the plan doc
raised -- the exemption series stops at two. **Tier 0.5 models economy
channels.**

## R62 -- `sucrose_astable`: free + Exhaust, restoring the v1.11a numbers (2026-07-25)

The card returns to **cost 0, Exhaust**, superseding main's interim rebalance.
The 2026-07-26 merge resolved a collision in main's favour on recency, which
silently dropped the Exhaust; the sheet flagged it as *absent rather than
rejected* and this is the ruling that closes the flag.

**[USER] grading:** Bursts are not currently priced strongly enough for the
multi-copy-battery worry to bind -- replaying the card to buy a Burst is not
worth the energy it costs -- so the guard costs nothing to keep and the
free-cost reprice stands on its own merits. The guard is **retained as cheap
insurance against a future Burst reprice, not because it currently binds.**

Mechanical: `docs/mondstadt-companions.yaml` cost 1 -> 0 plus `exhaust: true`;
`docs/klee-upgrades.yaml` comment corrected; §4.7 changelog gains a v1.11b
supersession note. Sheet remains sole source of truth; codegen regenerated.

## R63 -- §4.7 shop channel executed: three amendments and a purse that never binds (2026-07-25)

Execution record for the R59-R62 sprint. Full log:
`docs/archive/shop-companion-channel-sprint-log.md`.

**AMENDMENT 1 -- Track A shipped as a query surface, not a `CardPoolModel`.**
The plan called the pool class the prerequisite. It is not one: a
`MerchantCardEntry` takes a plain `IEnumerable<CardModel>`, so the shop needs
no pool object. More importantly the reasoning inverted twice and both halves
are on file. `KleeOffPoolCards.cs` carried a signed finding that a standalone
pool "could never work" (no registration hook in `ModelDb.AllSharedCardPools`,
which is a hardcoded array of 7). **That finding is now STALE and was nearly
re-asserted:** BaseLib ships `ModelDbSharedCardPoolsPatch`, a postfix that
appends any `CustomCardPoolModel` declaring `IsShared`. It would work today.
It was still not built, on COST: `CardModel.Pool` must resolve to exactly one
pool and supplies the card frame, so registering one migrates 47 companions
out of three character pools and repaints every companion card -- with an
init-order dependency no C# test can check, because there is no C# test
project. Feasible, deferred, [USER]-owned. The stale comment is corrected in
place.

**AMENDMENT 2 -- no banner gating in the shop.** §4.2 gating was scoped as
"wiring, not design". Wiring it would have made the two channels disagree
about a rule neither can exercise: `BANNER_FEATURED_SLOTS` is 3 and no nation
designs more than 3 Rare companions, so the banner features every 5-star
everywhere and is exactly a no-op -- which is why the reward slot already
skips it by standing ruling. It goes live in both channels together, when a
nation ships a 4th Rare.

**AMENDMENT 3 -- companions do not collect the colorless price surcharge.**
`MerchantCardEntry.GetCost` is 50/75/150 by rarity (so the plan's "verify
before reuse" is answered: it DOES price off rarity) and then multiplies by
1.15 iff `card.Pool is ColorlessCardPool` -- a type check on the concrete
class, which companions are not. The mod's premium channel is therefore ~15%
cheaper than the base channel it replaces. Sim mirrors the same bands, so the
two sides agree with each other and both undercut base.

**THE MEASUREMENT CONTRADICTS §4.7's CENTRAL CLAIM.** 500 runs/arm x 3
characters, realistic, 3 acts. Winrate delta is a NULL (-0.20pp mean; +1.2 /
-1.8 / 0.0 with every interval overlapping its control). P1's slot-1 buy rate
came in at 49.2% against a predicted 10-35%.

The band's own diagnosis for a high buy rate is "under-priced relative to
card-remove/relic competition". A crowd-out check says that is the wrong
reading:

| door | off | on | change |
|---|---|---|---|
| removals bought | 0 | 0 | -- |
| relics bought | 1356 | 958 | **-29.4%** |
| gold unspent at run end | 332277 | 334174 | +0.6% |

Card removal is not a competitor at all in tier 0.5 (zero removals either arm:
`is_known_dead` only fires on curses and unupgradable basic filler, and all
three characters ship clean decks). The channel trades a relic for a companion
at par, ~30% of them, and moves no winrate. And **unspent gold does not
change** -- runs end holding ~220 gold.

**A price cannot govern a purse that does not bind.** "Gold price is the
balance governor" is not currently true in the sim; the governor is the shelf.
NO KNOB WAS TURNED -- the plan's retune order starts at gold bands, and the
evidence says a gold-band change would be aimed at the wrong mechanism. This
goes to [USER] as a design question (should the shop's purse ever bind?)
rather than as a tuning pass. Also recorded: `visit_shop` buys cards before
removal and `model.py` offers relics later still, so companions get first
claim on the purse by construction -- the buy rate is partly an ordering
artifact, which is why the crowd-out table and not P1 is the load-bearing
evidence.

**RIDE-ALONG: the constant-parity gate was only reading `public const int`.**
Adding one C# constant surfaced that eight non-integer balance constants were
escaping a lint whose docstring promises that every balance number lives
twice -- among them VaporizeMult 1.5, MeltMult 1.75, AmpStackLimit 4.0,
FanfareDecayFraction 0.20, SalonDryDamageMultiplier 0.75 and
GuestCastBaseMultiplier 1.5. Headline tuning numbers, any of which could have
drifted in silence. The lint now reads int/float/double/decimal and private as
well as public: **58 -> 71 mirrored, 3 -> 13 unmirrored, and every newly
watched value already matched.** No drift had happened; the gate was not
looking.

## R64 -- The Featured Banner goes live (2026-07-25)

Fontaine's Rare roster goes to four, exceeding `BANNER_FEATURED_SLOTS` (3) for
the first time anywhere. The banner therefore becomes selective, and is wired
in the same sprint across all three surfaces at once -- C# reward slot, C# shop
slot 1, and a sim call-site audit -- so no channel ever disagrees about a now
real rule.

Rejected: (b) capping the roster at 3, which defers the gap-fix the sprint
exists for; (c) raising `BANNER_FEATURED_SLOTS`, which preserves the no-op by
construction and means the banner never earns its keep as seeded run-variance.

**The C# side named its own trigger and it was honoured.** Both channels
carried a written ruling that the banner was skipped *because* it was exactly a
no-op, ending "It goes live in both channels together, when a nation ships a
4th Rare." It did, so it does, and neither channel was wired alone.

**What the call-site audit found, which predates this ruling.**
`roll_banner`'s `nations` defaulted to the literal `("mondstadt",)` and the run
model's single call site passed no argument. Every run of every character
rolled a Mondstadt-only banner, and `_banner_filtered` then dropped every other
nation's 5-stars from the reward slot AND the shop. Measured before the fix:
across 400 Kokomi seeds she was offered Albedo, Durin and Nicole and never Itto
or Raiden -- Inazuma's own Rares, one of them written as "the conscription
jackpot", unreachable in Inazuma runs since the day Inazuma got a 5-star. The
nation set is now DERIVED from the sheets (`rewards.designed_nations()`), so it
cannot go stale by omission again.

**Parity is structural, not numeric.** The sim and the game use different
generators, so which three of Fontaine's four are featured differs between
layers for the same nominal seed. What is mirrored is the rule -- per nation,
feature min(roster, slots) without replacement, fixed for the run, per player
in co-op, 4-stars never gated -- and `BANNER_FEATURED_SLOTS` is parity-lint
watched. The C# banner is a pure function of the player's rng seed, so it needs
no persistence and survives save/load by construction.

`test_v18_banner`'s "roster <= cap" invariant is RETIRED: it was a tripwire for
exactly this day, and keeping it would assert the sprint had not happened.

## R65 -- Unreleased-nation placement rule (2026-07-25)

Characters whose home nation is not yet a designed nation sheet are placed in
their nation of residence/operation until their home nation ships:
**Arlecchino -> Fontaine** (House of the Hearth), and as recorded precedent,
**Childe/Tartaglia -> Liyue** when he is designed (precedent only -- no Liyue
work in this sprint).

Extends the standing nation-precedence rule (same action = same nation over
faction) with a release-state clause. If and when Snezhnaya ships as a sheet,
migration of its natives is a [USER] call at that time, not an automatic move.

## D2 -- Neuvillette dual identity: resolved by standing ruling (2026-07-25)

No new number. The Fontaine sheet's Guest Star block already rules it: guest
cameos are Furina-personal-pool only, reached exclusively through her Guest
Star generators, never in shared rewards -- and "his shared-pool 5-star Rare
remains banner-governed and is a DIFFERENT card." Mechanically the separation
is already enforced: `five_star_roster` filters both `guest_star` and
`personal_pool`, so the new companion card enters the banner roster and the
cameos never do. The WATCHLIST convergence cell containing
`guest_neuvillette_judgment` is untouched by this sprint.

The separation is now asserted directly rather than vacuously. The test that
covered it used to assert Fontaine's 5-star roster was EMPTY, which proved the
exclusion only because no shared Rares existed; it would have stayed green if a
guest leaked the moment real Rares landed.

## R66 -- Kokomi archetype vocabulary: the sheet is canonical (2026-07-26)

The canonical archetype vocabulary for Kokomi is the ratified sheet's:
**priest / commander / assist**, plus `generic` as the non-archetype filler
tag, matching the Klee and Furina conventions. The `("garment", "ward",
"conscript")` tuple in `tier05/draft.py` was an orphan: it matched ZERO
cards, predated the v0.2 sheet pass, and its `conscript` term had already
been retired independently by the lore pass (muster/rally/enlist).

Two registries in one repo disagreed about her vocabulary. The sheet wins.

**What the mismatch cost, and why it was invisible.** `dominant_archetype()`
returned `goodstuff` for every Kokomi deck ever built. Adaptive (free-draft)
Kokomi therefore scored plans as pure static power with no synergy term at
all, and shop/rest/event plans degraded the same way. None of that crashed,
failed a test, or looked wrong in a report: it produced numbers that were
indistinguishable from correct numbers.

This is the SECOND time this exact defect has been fixed. POLICY_VERSION 2
(G-E3) existed to remove it for Furina, and it left Kokomi's entry naming
three tags that did not exist -- so she kept the defect the bump was written
to remove. The general lesson is now a test:
`test_every_registered_archetype_exists_on_a_real_card` checks every
character's tuple against the tags actually carried by cards in her pool.

**Scope of the fix.** `draft.py`'s tuple; `dominant_archetype`, adaptive plan
scoring and shop/rest/event plans all self-correct with no code change once
the tuple matches real tags. Separately, `ab.py`'s starvation alarm now keys
on `ROSTER_ARCHETYPES[character]` rather than the module-level `ARCHETYPES`
(Klee's) -- a latent bug for EVERY non-Klee character, not a Kokomi special
case, so it is fixed generally.

**Stamp.** POLICY_VERSION 2 -> 3. Klee's and Furina's tuples are untouched
and their numbers do not move. Every adaptive/free-draft Kokomi number ever
taken was measured through the broken registry and is ARCHIVED. Assigned-plan
Kokomi numbers (the R56 battery) STAND -- they route through `runner.py`'s
plan registry, which was always correct.

**Landed as EPOCH 1**, batched with the other stamped behavior fixes (audit
s1.7 splash clamping, s2.4 survival_profile, s1.4 Tamakushi): one commit
group, one archive event, one re-baseline. The `_static_power` repricing
(audit s2.5, DRAFTER 11) was deferred by [USER] to a design session and
becomes EPOCH 2 when ruled; it was deliberately NOT waited on.

**Pre-registered predictions, graded 1 of 3.** Full record in
`docs/epoch-1-log-2026-07-26.md`; the summary is that the ruling was right
and two of its three predictions were wrong.

- **P1 (spurious starvation alarms -> exactly zero): FAIL as written.** The
  spurious ones did vanish -- `garment/ward/conscript` were unfalsifiable,
  since tags no card carries can never reach the 10% floor. What replaced
  them is a REAL signal at the same threshold: `commander` 2.8%, `assist`
  8.5%. The instrument went from "always fires, means nothing" to "fires,
  and means something", and the prediction assumed the alarm's only content
  was the artifact.
- **P2 (adaptive winrate moves UP; direction committed): FAIL.** 15.8% ->
  10.8%, i.e. -5.0pt, the wrong way. Recorded as a null-discipline result.
  Narrow reading only: both arms score through `_static_power`, which prices
  21.2% of her draftable pool at exactly 0.0, so this measures a synergy term
  layered over a partly-blind pricer, not "does synergy help". The confound
  is EPOCH 2. The fix remains correct regardless of direction -- a registry
  naming tags no card carries is broken either way, and the pre-R66 15.8%
  was never a number about drafting Kokomi.
- **P3 (dominant_archetype returns priest in >=80% of runs): PASS.** 85.8%,
  against a pre-fix 0.0%. The mechanism self-corrected exactly as ruled.

Two findings fell out that belong to the pool-sweep pass, not here: the
adaptive drafter converges on priest in 85.8% of runs (also tripping the
0.55 dominance alarm), and `commander`/`assist` are starved as emergent
shapes. Both are claims about her card pool.

**Playtest interaction: none.** The Kokomi playtest freeze (R56 numbers ship
untouched; the variable under test is the medium) is unaffected -- the
playtest is real players on assigned kits, not the adaptive drafter. The sim
re-baseline happened at the epoch landing, not before the playtest.

## R67 -- Dead-knob deletion and the sweep-harness KNOB_READS gate (2026-07-26)

All nine dead constants named in audit s6 are DELETED, not DEAD-KNOB-marked:
`PROGRESSION_GAP_COMPENSATOR`, `SPOTLIGHT_SELF_MULT`,
`FANFARE_DECAY_PER_TURN`, `SPOTLIGHT_SELECTOR_VERSION`,
`PILOT_REGRET_SAMPLE_RATE`, `ATTRITION_LITE_HP`, `PUNISHER_LITE_SCALE`,
`NORMAL_POOL_WEIGHTS`, `NORMAL_ATTRITION_SCALE`.

The DEAD-KNOB comment marking was the correct halfway step for an audit
session and is the wrong end state: an unreadable knob left in the file
invites exactly the false-evidence sweeps of audit s2.1. Each deletion keeps
its record as a tombstone comment where the constant stood -- what it was
for, what it measured, and what is untested rather than disproved by its
removal.

Deleting `FANFARE_DECAY_PER_TURN` also removes the unreachable flat-decay
branch in `resources._decay_amount` and the docstring assertions that argued
for it. **The ruled world is 20% proportional, full stop.** Note that
`FANFARE_DECAY_FRACTION` is now a RATE, not a switch: there is no "off", and
adding an `if fraction <= 0: return 0` guard to give it one would recreate
precisely the unreachable branch this deletes.

**Sweep disposition.** The two contaminated sweep blocks are deleted with
their knobs: `exp_furina_sheetpass.py` block C2 (`SPOTLIGHT_SELF_MULT`, three
guaranteed-identical rows) and `exp_furina_decay.py`'s flat magnitude sweep
(five guaranteed-identical rows). Any row sourced from either block reads as
**instrument error, never as a null result**. This is narrower than
invalidating those scripts' other blocks, which swept live knobs and stand.
`exp_furina_decay`'s `prop` block loses its flat comparison cells -- the
shape they compared against no longer exists -- and keeps its proportional
sweep; the historical flat-vs-proportional table that decided the 20% ruling
is preserved in the `FANFARE_DECAY_FRACTION` comment as a record.

**Generalization: the third instance, so it becomes a lint (house rule).**
The read-nothing instrument class has now appeared three times -- R33's
selector circularity, and the two sweeps here. The KNOB_READS counter
therefore graduates from opt-in to GATE. `tier05/sweeps.py` is the shared
harness: it resets `effects.reset_knob_reads()` per cell and refuses loudly
if a swept knob records zero reads, failing on the FIRST such cell rather
than collecting a grid nobody can cite. **No sweep may be run outside the
gated harness**, and every surviving live-knob sweep was moved onto it.

R33's exercise-counter law carries over verbatim: **the gate may not be
satisfied by adding artificial reads.** The mechanism is built so that it
cannot be -- `tier0/constants.py` gains a PEP 562 module `__getattr__` that
serves armed sweep values and counts each access, so what is counted is the
real attribute read from real engine code on the real read path. A knob
nothing reads records zero, and no amount of instrumenting the knob changes
that. (This works because every consumer in this repo reads knobs as module
attributes; a `from tier0.constants import X` would bind at import time and
slip the hook. Do not introduce one.)

**Class: SAFE + TESTS. No numbers move.** `tier05/tests/test_sweep_gate.py`
carries the ruling's negative test (sweep a deliberately dead knob, assert
refusal) plus the positive control that makes it mean anything, restoration
on the exception path, and a pin that all nine constants are gone.

## R68 -- Canonical cell object and mandatory run stamps (2026-07-26)

The ratified-cell configuration -- 600 runs, seed 11, hunter, RT7 / DRAFTER
10 / POLICY 2 / C3 -- was a sentence in a sprint doc and existed in no code
object. It is now a frozen `Cell` dataclass in `tier05/cells.py`, the single
source of truth for cell identity.

Version fields are NOT stored: they are read from the live stamps in
`tier0/constants.py` at call time, so the canonical cell always describes the
world it is about to run in. R66's epoch landing moved POLICY to 3 and the
canonical cell followed with nothing edited. A stored stamp goes stale
silently at the next bump, which is exactly what the ghost check did to
itself one bump after it was written.

**Requirements, all landed.**

- Experiment scripts construct their configuration from `Cell`, as the base
  or as explicit `but(...)` deltas. A derived cell RENAMES itself, so its
  stamp stops claiming to be the cell it came from.
- The three drifted `_arm()` clones (`exp_roster_anchors`,
  `exp_furina_ghostcheck`, `exp_free_draft_cell`) consolidate into
  `Cell.arm()`, and the three byte-identical argument parsers wrapped around
  them into `cells.parse_overrides`. Byte-identical when copied is how the
  bodies drifted without anyone noticing they had.
- Scripts resolve plan -> pilot exclusively through `runner.resolve_plan`;
  the bypass path is gone. `Cell` validates through it at construction, so a
  cell naming an archetype its character does not have cannot be built.
- `print_run_report` emits a mandatory stamp line
  (`cell=<name> seed=<s> runs=<n> RT<x>/D<y>/P<z>/C<w>`). It is a
  keyword-only REQUIRED argument, so omitting it is a TypeError at the call
  site rather than a slightly thinner report that reads fine and cannot be
  checked. **A report without a stamp is not citable in a sprint doc or a
  ruling.**
- `exp_furina_achievability.py` (hardcoded `SCREENS = 10` from RUNTEMPLATE 2
  -- it runs, prints numbers, and describes no world that exists) moves to
  `tools/archive/` rather than being ported, together with its self-declared
  siblings `exp_furina_modes.py` and `exp_furina_pass3.py`.

**Class: SAFE, mechanical, zero numbers move.** Archived scripts keep their
hand-rolled configs deliberately -- those ARE the historical record. R68
governs anything run from today forward.

## R69 -- The Orobas relic upgrade is renamed "Dodoco Tales" (2026-07-26)

The Klee upgraded-starter relic that displayed as "Explosive Frags" is
renamed **Dodoco Tales**. The Rare Power card `explosive_frags`
(`docs/klee-cards.yaml:193`) keeps its name unchanged: the card was the prior
arrival and the ratified sheet artifact, so the relic yields.

Lore basis: Dodoco Tales is Klee's signature catalyst, which keeps the relic
in her personal register alongside Pounding Surprise, and it still satisfies
the base-game convention of a DISTINCT name for an upgraded starter rather
than a "+" suffix (Burning Blood -> Black Blood).

**No mechanical change of any kind rides on this ruling.** The C# TYPE is
deliberately still `ExplosiveFrags`: relic identity is BaseLib's, not this
repo's, so a renamed type risks moving the runtime relic id -- and in
deterministic-lockstep co-op that is a desync, not a cosmetic diff. The
player-facing string is what the ruling renamed and what was renamed.

Red-pen Part 1 item 5's measurement table, quoted in the relic's doc comment,
grades the same object under the new name, and the doc comment now says so
explicitly: the +2.3 / +7.1 / +5.0 figures are the RELIC's, measured as the
Orobas upgrade, and item 5's ratification at 3 opening Sparks is the relic's
ratification. That closes the ambiguity the audit flagged.

**Gating the class, not the instance.** `lint_unique_names.py` extends to
relic display names: the namespace it checks is "names the player sees", and
relics were always in that namespace -- the lint's SCOPE was merely narrower
than its PURPOSE. Relic names are read out of the emitted C# `("title", ...)`
entries, which is where they are actually defined; a lint reading a manifest
instead of the shipped source is the one-layer-lint failure this repo has
been bitten by before. The reader raises rather than returning an empty list
if the relic directory is missing, so it cannot pass by scanning nothing.

Both "Dodoco Tales" and "Explosive Frags" enter
`docs/reserved-card-names.txt`, annotated with the kind that OWNS each, so
neither can be re-minted on the other side of the card/relic line. The
annotation is load-bearing: without it, reserving both sides would fail the
very card and relic that legitimately hold those names, and the obvious fix
for that (drop the entries) is what lets the collision re-form.

**Class: SAFE (rename + doc comment) + TESTS.** The extended lint carries the
ruling's negative test -- a deliberate card/relic display-name collision must
fail -- plus the converse pin that an owner is not failed by its own reserved
entry, and an assertion that the lint is actually seeing relics at all.

## R70 -- Manifest version policy: MAJOR.AUTO with overwrite refusal (2026-07-26)

`manifest.json`'s version becomes two-part, **MAJOR-AUTO**.

**MAJOR** is bumped deliberately, by [USER], as part of a release sprint's
close-out. It is a ratified artifact like a sheet and no tooling touches it.
The current world ships as MAJOR **0.2**, unchanged; the first deliberate
bump happens at the next release sprint, not retroactively.

**AUTO** is generated at deploy time and exists to prevent duplication and
build-identity disconnects. The mechanism is the commit count
(`git rev-list --count HEAD`) -- stateless, monotonic, and comparable. Two
co-op players comparing versions can see not just THAT they differ but WHO IS
BEHIND, which is the diagnostic that matters for deterministic-lockstep
desyncs and the one a timestamp cannot give. *(The auto mechanism is the one
knob in this ruling [USER] may swap without a new R-number; a timestamp or a
stored counter would satisfy the policy's intent at the cost of
comparability or statelessness respectively.)*

**Enforcement -- the load-bearing part.**

- `deploy.ps1` REFUSES to overwrite an existing `dist/klee-v<version>.zip`.
  With AUTO in the name this can only fire on a same-commit rebuild, which
  is exactly the case where two zips share a name and can differ, so refusal
  is correct rather than an inconvenience.
- Deploys from a dirty working tree append `+dirty` to AUTO and log loudly,
  listing the offending files. Loud but not fatal: building dirty is normal
  while iterating; handing that build to a co-op partner is not.
- **S3 stops being decorative.** `validate.ps1` compares the staged
  manifest's version against the computed MAJOR-AUTO and fails on mismatch,
  so the manifest can no longer silently fossilize -- 134 commits at 0.2.0
  was the presenting symptom. In the same visit, the `min_version 3.3.6` and
  `min_game_version 0.107.1` pins are wired to actual comparisons (audit
  s3.5): the same "asserts presence, measures nothing" class. The game's real
  version is read from `release_info.json`, NOT from `SlayTheSpire2.exe`'s
  VersionInfo, which reports a placeholder `1.0.0.0`.
- Version comparison is numeric, not lexical, and an unparseable version
  reports as unparseable rather than passing. A check that quietly passes on
  garbage is the original defect wearing a comparison's clothes.

The comparisons live in `klee-mod/build/version.ps1` as `Test-VersionPolicy`,
which `validate.ps1`'s S3 calls. That placement is deliberate: `validate.ps1`
as a whole cannot be run quickly -- its S7 game_ref verification takes
minutes -- and a gate nobody can afford to run is the failure class this
ruling closes. `deploy.ps1` and `validate.ps1` both dot-source that one file,
so the stamp and the gate that checks it cannot compute the version
differently.

The deployed-pck stamp convention (`<timestamp>+<short-sha>`, already in use
in `open-playtest-items.md`) continues unchanged: it identifies a BUILD,
while the manifest version identifies a RELEASE LINEAGE. Both appear in the
deploy log line.

**Class: RULING (this document) + SAFE + TESTS.**
`tier0/tests/test_manifest_version_gate.py` carries a negative test each for
version mismatch and min-version violation, positive controls for both, and
the min-game-version pair.

## R71 -- SPOTLIGHT_BASE_MULT 1.5 and Selector v3 constants ratified (2026-07-26)

`SPOTLIGHT_BASE_MULT = 1.5` is RATIFIED. The `PLACEHOLDER` marking is
removed from `tier0/constants.py`; the constant now cites this R-number as
its ratification record.

This ruling makes law of a result already committed to. The W0 forced-arm
sweep {1.25, 1.5} was the PRE-REGISTERED decision procedure -- the word
"decides" was written into the constant's own comment before the sweep ran
-- and it returned dose evidence favouring 1.5 at pass 3
(`furina-pass3-rulings.md`). What was missing was the record, not the
evidence: the value has been 1.5 in the tree throughout, so **zero numbers
move with this ruling** and nothing needs re-measuring.

No R14 conflict. W0's oracle mode (`SPOTLIGHT_FORCE`) remains a diagnostic
that never ships. What is ratified is the sweep's verdict on the LIVE knob,
not an oracle cell as an acceptance target -- the distinction R14 exists to
protect.

**The Selector v3 constants (depth >= 4, crowd >= 2) are ratified in the
same stroke** -- same ask (pass-3 ask 5), same evidence window, same
discipline (shipped under full instrument protocol per the pass-3 report).

**Executor's note, and it matters for how this one was landed.** The v3
constants no longer exist. `SPOTLIGHT_COMPANION_DEPTH_MIN = 4` and
`SPOTLIGHT_COMPANION_MIN_ENEMIES = 2` were deleted on 2026-07-23 by the
selector v5 rework (commit b4b4434), which replaced character-depth
targeting outright with the two-mode Center Stage / Guest Cast design.
Ratification therefore landed as a RECORD, in the selector history block
that survived R67: the numbers are written down, attributed, and marked as
the values to restore v3's geometry with, but no constant was resurrected.
Reintroducing two constants nothing reads would have manufactured exactly
the dead-knob class R67 deleted nine of three days earlier, and the
exercise-counter law would have condemned them on arrival.

The general shape is worth naming, because it will recur: **a ruling can
arrive after the code has moved past what it rules on.** Three days passed
between the pass-3 ask and the sitting, and the v5 rework happened inside
that window. The ruling is still honoured -- ratifying a superseded design's
numbers costs nothing and preserves the reasoning -- but it is honoured as
history, and the record says so rather than quietly implying v3 is live.

**Class: SAFE** (comment and marking changes only). Also closes the
`SPOTLIGHT_BASE_MULT` ratification item in `docs/missed-requirements.md`
Tier 3.

## R72 -- Kaboom Beetle Swarm: bombed-state snapshots at cast (2026-07-26)

Option (b) of the three put to ruling: the vs-bombed bonus is determined by
a **bombed-state snapshot taken at cast**, the Sizzle idiom. This restores
the original design intent. Hit 1's detonation no longer strips the bonus
from hits 2-3; a target bombed at cast pays the +3 on every hit of the
series.

The presenting report (playtest, 2026-07-20) was that subsequent hits never
got the bonus. That was never a port bug -- both engines agreed on [8, 5, 5]
-- so per house law it was a DESIGN question, and it sat QUEUED until now.
The mechanism was self-defeating in a specific way worth recording: the
card's own detonation is the payoff the rider rewards, and reading state the
card had already consumed made the rider partly unreachable. That is the
same failure Sizzle's aura predicate was written to avoid, which is why the
idiom transfers cleanly rather than being invented here.

**What landed, both engines, one commit group:**

1. **tier0.** `_op_damage` builds `bombed_at_cast` before the hit loop and
   the rider tests membership in it. Taken once per cast, so a replay
   re-snapshots -- correct, because a replay IS a new cast.
2. **C#.** `KaboomBeetleSwarm.OnPlay` snapshots into `_bombedAtCast` before
   the damage series and clears it in a `finally`;
   `ModifyDamageAdditive` consults the snapshot. Outside a play it falls
   back to the live read -- damage previews ask what the card would do to
   the CURRENT board, which is a different question from what a cast in
   progress is paying, and returning 0 there would have blanked the bonus
   out of the preview.
3. **The test was REWRITTEN, not deleted**, as ruled.
   `test_beetle_swarm_bonus_snapshots_bombed_state_at_cast` pins [8, 8, 8]
   vs a single bombed enemy and asserts the detonation still happens (a run
   where the bombs never popped would prove nothing). Two more land with
   it: the negative -- bombs placed after the damage op buy nothing, without
   which "snapshot" could be implemented as "read once, whenever" and still
   pass -- and a two-target discrimination test proving the snapshot is
   per-enemy rather than a single "someone was bombed" flag. The C# phase
   half is `test_beetle_swarm_snapshots_bombed_state_at_cast` in
   `test_roster_runtime_contracts`, a source-text check for the same reason
   the bomb-suppression latch above it is one: WHEN the state is read is
   invisible to any simulator run, and a silent revert to the live read
   compiles, plays, and differs from the sim by exactly the +6 this ruling
   restored.
4. **Card text: FLAGGED, not reworded.** "Bombed enemies take X more per
   hit" reads as live state, and under the snapshot the enemy stops being
   Bombed after hit 1 while still paying on hits 2-3. The sheet is
   ratified, so the wording is a red-pen call; queued at
   `docs/open-playtest-items.md` 6.2 with a pointer comment in the C#.

**Exposure note (not part of the ruling).** `bonus_vs_aura`, the sibling
rider, still reads live. It has zero exposure to this class today -- all
three cards carrying it are single-hit per target -- so it was left alone
rather than changed on speculation. If a multi-hit `bonus_vs_aura` card is
ever printed, it inherits this bug on day one.

**Stamp.** This moves Klee demolition numbers upward, slightly. It landed
INSIDE EPOCH 1, which was already archiving Klee-touching A6/DPT numbers;
no third epoch was created.

**Pre-registered prediction, graded with EPOCH 1's** (see
`docs/epoch-1-log-2026-07-26.md` for the full grading): "demolition-plan
winrate delta from this change alone is small (< +1.0pt on the canonical
Cell) -- if it's larger, that's evidence the card was load-bearing and it
goes on the balance watch list."

**PASS.** 7.5% -> 7.5% (45/600 both arms) on
`cell=r72-grading seed=11 runs=600 RT7/D10/P3/C3`, klee/demolition. Not on
the balance watch list.

The two arms were two WORKING TREES, the BEFORE arm being the same repo at
the commit before R72, so that "this change alone" is literally true. The
alternative -- an in-process toggle -- would have meant shipping a knob
whose only reader is a grading script, one ruling after R67 deleted nine of
those.

**A 0.0pt delta needs its own proof of exercise, and this one has it.** The
graded cell drafts the card into 6.3% of decks (38/600) and the ratified
`demolition_weighted` battery package does not contain it at all, so the
cell is nearly blind to this card and a null could mean either "small
effect" or "instrument never saw it" -- the two readings R67 spent a ruling
separating. A forced-carrier arm (two copies in every deck, 400 gauntlet
fights, 498 casts) resolves it: turns/fight 4.185 -> 4.160 and HP lost/fight
17.622 -> 17.410. Real, directionally correct, and small. Note that TOTAL
DAMAGE DEALT is useless here and was discarded mid-measurement: a won fight
deals exactly the enemies' HP, so it read 37000 in both arms no matter what
the card did.

**Class: RULING + behavior (both engines) + TESTS.**

## D3 -- Pass-4 ask A5 deferred pending the axis-validity session (2026-07-26)

No new number; a scope decision with a paper trail.

[USER] declines to encode the scorecard invariants (non-elite <= 4.0 cap,
declared-elite-pair identity) at this time. The seven-axis bands were
ratified against a battery since recognized as unrealistic, and the open
question is whether the instrument is even DIRECTIONALLY correct or whether
the design loop has been overfitting to it -- designs tuned until axes hit
bands measured on the same battery the bands were ratified against.
"Passing by coincidence" may be Goodhart, not luck.

Encoding the invariants now would assert the scorecard is right, and that is
precisely what is unknown. This is a deferral on grounds of validity, not
cost.

**Consequences, effective immediately:**

1. The scorecard-invariant items are **pulled from the pin batch** (audit
   §9 step 2). The mechanical repairs in `axes.py` -- eps guard on
   zero-baseline axes, loud failure on missing `attrition`/`swarm`
   encounter ids, the `or 1.0` turn-10 default -- **remain** in the pin
   batch: they make the instrument honest without asserting it is right.
2. A dedicated **axis-validity design session** is opened on the horizon
   list (audit §10), sequenced at both ends. **After EPOCH 1 lands**,
   because A6 splash and `survival_profile` were known instrument errors
   and re-litigating the framework on contaminated readings decides the
   wrong question -- EPOCH 1 landed the same day, so this end is clear.
   **Before the Zhongli deep dive**, because slot 4 must not declare elite
   axes against a framework nobody trusts. Candidate agenda, non-binding:
   directional-validity tests via holdouts the designs were never tuned
   against -- the tier-0.5 realistic gates, and co-op playtest outcomes,
   which no design loop has ever seen.
3. Until that session rules, seven-axis numbers are **reportable but not
   load-bearing**: no new band may be ratified, and no design may be
   accepted or rejected on axis evidence alone. This standing is recorded
   in `axes.py`'s module docstring, where the numbers are produced, and in
   `calibration-notes.md`, whose three parked "next levers" all assume the
   framework is sound and are therefore parked harder -- extending an
   instrument is the wrong move while its validity is the open question.

**Class: RULING** (this record) -- no code beyond the pin-batch scope change
and the docstring that carries the standing.

## D4 -- Instrument-visibility law for predictions (2026-07-27)

A standing discipline rule, not a number. It governs how predictions are
registered and how quantitative claims may be used as rationale.

**The law, in three clauses:**

1. **A pre-registered prediction must name its instrument.** Not "winrate
   moves up" but "winrate moves up *as measured by <cell / harness / pin /
   play session>*". A prediction without a named instrument is not
   registered.
2. **Registration must confirm the instrument models the changed object.**
   Naming an instrument is not enough; the registrar must state that the
   instrument can see the thing being changed. C#-only changes get C#-side
   verification -- pins, and play -- and **never** sim predictions. The sim
   is tier-0.5; it does not execute the mod's C#, and it models one seat, so
   co-op-scoped and mod-side-only changes are invisible to it *by
   construction*.
3. **Any quantitative claim used as rationale in a ruling or a sprint doc
   must carry a measurement or be marked `UNMEASURED`.** A number offered as
   a reason is a load-bearing number. If it was not measured, the claim may
   still be made -- but it must wear the label, so a later reader can tell an
   observation from a guess.

**Origin.** Two independent failures in Serenitea Sweep I, same root:

*Sweep-I Track D.* Three predictions were registered against the canonical
tier-0.5 cell. **Two of the three were structurally unmeasurable by that
instrument.** D1 (Pearl of Insight funnel + relic-pool membership) and D2
(`BombPower.DetonationsThisCombat` per-owner) are both C#-only fixes; the
canonical cell cannot execute them, and D2 is co-op-scoped besides, which the
one-seat model cannot represent at all. Both duly measured **0.0pt**, and the
log had to record D1 as PREDICTION FAILED and D2 as *met, but VACUOUSLY*.
Neither grade carries information about the fix. The instrument was never
capable of producing one, and that was knowable at registration time -- which
is exactly where this law now puts the check.

*Sweep-I C6.* `validate.ps1` carried, as the stated rationale for an R70
design decision, the claim that the gate "cannot be run quickly (S7's
`game_ref` verification takes minutes)". When finally measured, that
verification was **0.17s -- 0.2% of an 84.0s gate**; the cost was the pytest
suite (78.4s) the whole time. An unmeasured number survived as design
rationale for the file's entire life because nobody printed it. A number
nobody prints is a number somebody will guess.

**Consequences, effective immediately:**

1. Prediction tables in sprint docs gain an **instrument column**, and the
   registration is incomplete without it. The grading rule column stays.
2. A prediction whose instrument cannot see the change is not registered as
   a prediction. It is either re-pointed at an instrument that can (a pin, a
   play session, a C#-side harness) or recorded as **NOT PREDICTED --
   no instrument**, which is an honest state and costs nothing.
3. `UNMEASURED` is a first-class marker. Marking a claim is never a failure
   condition; leaving an unmarked unmeasured claim in a ruling is.

**Class: RULING** (this record) -- discipline, no behavior change.

## D5 -- Kokomi stability band: provenance and schedule (2026-07-27)

An amendment to the E1 gate, forced by events. It does not declare the band;
it rules where the band may come from and when it may be graded.

**Background.** R51 moved Kokomi's healer fantasy *entirely* to the stability
band, and Serenitea Sweep I's E1 built the instrument
(`run_metrics.stability_profile`) with `band = None` and every value reported
rather than asserted. The gate attached to it was blind declaration: the
acceptance band must be recorded BEFORE any playtest HP data is reviewed,
because a threshold chosen from output you already have is the target drawn
around the shot.

**What changed.** HP-trajectory data was subsequently reviewed during the
Kokomi playtest sprint on the feature branch. The blind gate is therefore no
longer satisfiable as written -- not by anybody's fault, and not recoverable
by pretending the data was not seen.

**The ruling:**

1. The observed playtest is designated **EXPLORATORY**. It is a source of
   understanding, not a grade. Nothing may be graded against it.
2. The band **will be declared** -- from **design intent**, informed by the
   exploratory observations, and **recorded as such**. The provenance is part
   of the record, not a footnote: a reader must be able to tell that this band
   was declared with some data already seen, and which data.
3. Declaration happens **BEFORE the post-rework confirmatory playtest**, which
   grades it.
4. **The band may not be revised against the playtest that grades it.** A
   grading instrument that moves to fit its result is not an instrument. If
   the confirmatory playtest says the band is wrong, that is a finding, and it
   is ruled on separately and afterwards -- not folded back into the threshold
   before the grade is written down.

**Why this and not a re-blind.** The alternative -- declare blind by ignoring
what was already seen -- is unenforceable and would put a false claim on the
record. Declaring from design intent with the contamination stated is weaker
evidence than a blind declaration would have been, and it says so out loud,
which is the honest form. Clause 4 is what preserves the part of the gate that
still can be preserved: the grading playtest is unseen at declaration time,
so the band is blind with respect to *the measurement that grades it*, which
was always the load-bearing half.

**Relation to D4.** The exploratory designation is a D4 instrument statement:
the confirmatory playtest is the named instrument for the band, and the
exploratory one is explicitly named as *not* it. Any number carried out of the
exploratory playtest into the declaration rationale is a quantitative claim
used as rationale, and wears its measurement or the `UNMEASURED` marker
accordingly.

**Carriers.** The blind wording is stated at both places it is read --
`tier05/run_metrics.py`'s `stability_profile` docstring and
`tier0/tests/test_stability_band.py` -- and both are amended to point here.
`band is None` stays pinned: the instrument still does not judge, and it stays
dark until the declaration lands. The Sweep-I log's account is left as
written; it was true on its date.

**Class: RULING** (this record) -- provenance and schedule, no behavior change.

## R81 -- Distinctness gate ratified on the two-anchor floor (2026-07-27)

Full evidence and derivation: docs/a2-gate-ratification-2026-07-27.md
(supersedes silent-anchor-sprint-log s6.5). Ask A2 is CLOSED.

**Ruled.** (1) `top%` and `vocab` carry NO GATE, permanently: themed
concentration is design, and the official idea-count edge is the phenomenon
`uniq%` already enforces from the other side -- double-gating one phenomenon
invites gaming the metric. Both remain report columns and pool-sweep
guidance. (2) Hard thresholds recalibrated to the official FLOOR with
modding headroom: uniq >= 70 (floor 72), maxclu <= 5 (floor 5), neardup
<= 0.40/card (floor 0.36). `--gate` prints the official band (uniq 72-86,
maxclu 4-5, neardup 0.24-0.36/card) as advisory so "passes" is never read
as "matches Ironclad".

**Standing lesson, recorded.** Partial-pool anchors can only loosen a
threshold's credibility, never certify it. Both of s6.5's would-be
certifications (maxclu <= 4, neardup <= 0.33 "cleared by both anchors")
were overturned when the second anchor completed.

**Enforcement.** The gate is now a red test
(tier0/tests/test_distinctness_gate.py): breaches outside its curated
known-failing list fail the suite immediately; the curated list (klee uniq;
furina uniq+neardup; kokomi uniq+maxclu) is debt for the pool-sweep pass,
and a staleness test forces entries out as they clear, so the list only
shrinks. The roster-wide uniq gap (8-16 points under the official floor)
is the pool-sweep pass's acceptance target.

**Class: RULING** ([USER] 2026-07-27) -- thresholds + enforcement; no
engine behavior change.

## R82 -- Enchantments: the rider ships, the subsystem stays out, the space stays open (2026-07-27)

Full evidence and derivation: docs/enchantments-design-2026-07-27.md.
Ruled by [USER] with one amendment to the proposal.

**Ruled.** (1) Blade Of Ink lands as the MINIMAL RIDER: two per-instance
fields on the Card object (`enchant_damage`, `enchant_effects`), attached
by the `enchant:` block of the add_card op that creates its tokens -- the
pass-6 "state on the CARD OBJECT" pattern, no registry, no enchantment
vocabulary. (2) The run-wide enchantment SUBSYSTEM (deck-enchant screens,
rest options, granting relics, the ~20-type model hierarchy) is outside
the parity world with relics and events; the refusal is recorded once, in
the extractor, as the standing triage category. (3) AMENDMENT -- the
proposal's "not offered to house design" fence is STRUCK: the rider IS
open design space, because the house is actively expanding existing
characters toward the official ones' breadth. What exists today is still
only Inky's two hooks.

**Landed.** Engine hooks in _op_damage / resolve_card / _op_add_card
(plus the target_all_if_power widen on apply_power -- Inky's Weak follows
the card's LIVE TargetType under Fan of Knives); behavior pins in
tier0/tests/test_si_pass7.py; silent_pool_pass7.yaml registered in loader
and builder. THE SILENT POOL IS COMPLETE: 86 of 86 draftable cards, 87
rows with the Shiv token. Gate re-read at 87 rows: uniq 72 / maxclu 5 /
neardup 0.356 -- PASS, no new breaches.

**Class: RULING** ([USER] 2026-07-27) -- design ratification + the
implementing engine change.

## R83 -- Pilot review ruled: weights stay PLACEHOLDER, no poison term, the scorer pass runs (2026-07-27)

Full evidence: docs/silent-pilot-review-2026-07-27.md (including its s1a
correction and s5 execution record). Ruled by [USER]: "let's continue the
policy work before worrying about thresholds."

**Ruled.** (1) A3's weights stay PLACEHOLDER and the runner keeps the
generic mapping -- the A/B measured them as a dead lever (24.2% vs 24.5%,
1000 runs). (2) No poison term -- poison cards post positive lifts under
the term-blind scorer. (3) The draft-scorer pass is the authorized policy
work.

**Correction on the record (s1a).** The review's original lift table
carried an estimator artifact: si_survivor/si_neutralize are BASIC
starters the reward roll never offers; their -38.6/-35.3 "lifts" were
removal-selection confounds. The skip-all control (7.9% vs 23.3%) refutes
net dilution outright -- the draft HELPS; the defect is discrimination
between strong and weak commons. Standing lesson: an every-deck
intersection is not a starter filter; exclude by offerability (rarity in
RARITY_ODDS).

**Executed (s5), numbers PROPOSED.** DRAFTER_VERSION 11, scoped to
archetype == "generic" (anchors only): the ratified skip/redundancy
levers measured weak-to-backwards; the measured lever is
GENERIC_PLAN_BONUS_MULT -- the anchor sheets' role labels collected +3-4
points of plan value that does not track generic worth. Winner (mult
0.25, skip 1.5, redundancy 0.0 dead dial): real_silent 23.3% -> 28.8%,
real_ironclad 26.9% -> 33.3% act-1 clear at 1000 paired-seed runs, take
tails aligned to the measured lifts. Residual: _static_power is
power-blind (Footwork), named as the next lever. Anchor 3-act readings
predate v11 and must be re-measured before being quoted.

**Class: RULING** ([USER] 2026-07-27, three rulings) **+ MEASUREMENT**
(the v11 constants are PROPOSED pending number ratification).

## R84 -- DRAFTER v11 ratified; the power-aware static term and a fresh 3-act roster ordered (2026-07-27)

Ruled by [USER]: "the constants in the draft.py look fine at first
glance, approved. Let's take on _static_power and then redo the 3-act
roster for a full fresh recalculation."

**Ruled.** (1) The DRAFTER_VERSION 11 constants are RATIFIED as measured
(GENERIC_PLAN_BONUS_MULT 0.25, GENERIC_SKIP_THRESHOLD 1.5,
GENERIC_REDUNDANCY_PENALTY 0.0 dead dial). (2) The power-aware
`_static_power` term -- the Footwork residual R83 named -- is the
authorized next pass. (3) The 3-act roster gets a FULL FRESH
RECALCULATION once that term lands; nothing recorded before it may be
quoted in a roster comparison.

**Executed (docs/silent-pilot-review-2026-07-27.md s6).**
DRAFTER_VERSION 12: `_static_power` learns permanent self Dexterity at
the Strength mirror (STATIC_DEXTERITY_VALUE 2.0; `temp_dexterity`
deliberately excluded -- Anticipate carries a -16.9 lift). Footwork
taken 21% -> 74% against its +23.6 lift; real_silent 28.8% -> 29.1%,
real_ironclad 33.3% unmoved by construction (1000 paired seeds). The
flat engine credit (STATIC_POWER_ENGINE_VALUE) measured a DEAD DIAL --
hurt at every swept value, kept documented at 0.0: a flat credit cannot
tell Noxious Fumes (+29.7) from junk engines at the same price. The
value of the pass is the mechanism, not the point estimate. Universal
term; only ref-vocabulary cards newly touched, house numbers unmoved.

**Two defects found by the ordered re-run.** (1) The pass-4 amount
grammar widening (8712bb5) crashed every fight that played Elemental
Ecstasy: `_op_draw` ran the missing flat `amount` through `_amount()`
before the `per_aura` branch could fire. Fixed; engine-path pin added
(the old per_aura test only exercised the SCORER's view). No number
taken today crossed it. (2) The v11 session changed the scorer without
bumping DRAFTER_VERSION -- the stamp read 10 while the scorer was v11.
Both bumps now recorded; no experiment script ran in the gap, so no
published stamp mislabels its world. Standing lesson: a scorer change
IS a version bump, in the same edit, or the stamp rule is decoration.

**Class: RULING** ([USER] 2026-07-27) **+ MEASUREMENT** (the D12
constants are landed with the sweep as evidence; the fresh 3-act roster
table lives in the review doc s7 -- the only quotable roster table).

## R85 -- "Curtain Call": the register convention lands and the Furina pool takes the official shape (2026-07-27)

Ruled by [USER] in chat, 2026-07-27, in three parts. (1) The pre-registered
Curtain Call sweep is ratified to execute ("if there are no open questions,
please proceed"), with the register convention (§3: salon / archon /
private), the trial-card register moves and the two-Rare Focalors cap
already RATIFIED in the morning's rulings. (2) The counting check FAILED as
written -- warmup_act and dramatic_entrance were already attacks and
pit_orchestra already uncommon on the sheet of record, so the §7 worklist
could not reach the §4 targets -- and [USER] ruled the SESSION AUTHORS the
extra moves to land §4 exactly (against the alternatives of re-deriving §4
down or holding for per-card red-pen). (3) The two deferred slots:
quick_change is the 5th power (florid_cadenza keeps its F-B1 threshold
design); showstopper is the 4th rare.

**Executed** (docs/curtain-call-sprint-log-2026-07-27.md, the log of
record; Tracks A / B / C+E plus the shrink amendment). The reconciled move
set landed EXACTLY on §4 (Attack 17 / Skill 46 / Power 15, C 22 / U 32 /
R 19 at frozen pool 78) -- and then §4's own pre-registered shrink clause
fired on the cell-3 hydro-uptime breach, reverting the two authored
retypes that carried the most application (flood_of_emotion,
matinee_performance, rewrites and rarity moves intact). FINAL shape:
Attack 15 / Skill 48 / Power 15, rarities as ratified -- the type
deviation is logged with the clause as its authority. Register census: every card tagged, nine renamed (ids
stable), lint (tools/lint_furina_registers) at zero violations with the
Focalors cap holding at exactly {the_sea_is_my_stage, reginas_mercy}.
`register` joins the SHARED card schema (state.py) -- Columbina and every
future character inherit the column; the value vocabulary stays
per-character and the third-instance rule governs generalizing the lint.

**The gate debt is PAID.** R81's named defect -- uniq 62 / neardup 0.94,
the worst on the roster -- re-reads at cell 3 as **uniq 76 / neardup 0.15
/ maxclu 3 / vocab 34**: inside the official band on every gated metric
and past the pool-sweep vocab guidance. The furina KNOWN_FAILING entries
are removed (the staleness test forced them); klee/kokomi rows remain the
roster debt.

New engine vocabulary, all precedent-argued and pinned in
test_curtain_call: five activity-triggered powers (deploy-block, bow
payout, first-spend draw, first-attack draw, first-reaction
cross-examination -- never per-turn, per the accrual law), the
`salon_members` CalculatedVar read (Mirage's power-stack precedent), and
`N_per_M_encore` on bonus_formula (Body Slam's defensive-pool read).
C# parity for all of it is DEFERRED to the consolidation sprint by the
sprint's own §9 (FURINA_DEFERRED_TO_CONSOLIDATION, twelve cards, each
refused by name in blocked_reason; manifest 65 generated / 13 blocked).

Cell results, predictions graded in writing, the environment caveat on the
real anchors (game_ref absent on fresh clones -- ten of twelve roster arms
reproduce byte-identically, the two real-anchor rows need a local re-run
before the consolidation sprint quotes them), and the named follow-ons
(salon-trim pre-registration per prediction 5; the archetype-scorer
question for the new self-powers) live in the sprint log.

**Class: RULING** ([USER] 2026-07-27, three chat ratifications) **+
MEASUREMENT** (cells 0-3 + seed-12 rider; D12 frozen throughout -- no
scorer or drafter constant moved).

## R86 -- "Take a Bow": the Curtain Call deferral is paid off and deleted (2026-07-27)

R85 shipped Curtain Call's mechanics in Python and deferred C# parity for
twelve cards to a named consolidation sprint (§9,
`FURINA_DEFERRED_TO_CONSOLIDATION`, manifest 65 generated / 13 blocked).
This is that sprint. **Manifest is now 78 total / 77 generated / 1 blocked**,
the one blocked card being the hand-written kit Burst -- implemented, just
not by codegen. The deferral set is DELETED rather than emptied: an empty set
is an invitation, and the positive "every non-kit card is emitted" assertion
already carries the invariant it existed to state. The next deferral gets a
fresh set with its own written gate.

Nothing in tier0 moved. The Python side was the frozen reference this sprint
copied FROM, and no sim cell was run -- the suite was the gate, because there
was nothing to measure.

**Six PowerModels** (not five: `pit_orchestra` carries `salon_bow_block` AND
`salon_bow_encore`, and `blocked_reason` only ever reported the first), each
wired to the site mirroring its tier0 hook. Two needed judgment, both
recorded in `Powers/CurtainCallPowers.cs`:

- `encore_spend_draw`'s draw is DEFERRED, because `SpendEncore` is
  synchronous and holds no `PlayerChoiceContext`; it flushes from every async
  Furina hook that can follow a spend, the same deferral SpotlightSystem
  already uses for its first-play draw.
- The per-turn windows reset in `BeforeSideTurnStart`, not
  `AfterPlayerTurnStart` -- Salon upkeep SPENDS Encore in that second
  broadcast, so resetting there would make the Gallery Stirs draw depend on
  undefined intra-broadcast power ordering.

`cross_examination` reads the DEALER, not a global player. The reaction
counters are deliberately global (red-pen R1: a reaction is a fact about the
shared board), but a power is owned by a creature, so "did Courtroom Drama
fire" can only be asked of whoever caused the reaction. Solo -- the only
configuration the sim models -- the dealer IS the player, so this is the
sim's read exactly; co-op inherits the Best Friends Forever lesson for free.

**Two latent generator defects surfaced on real cards**, both of the class
that only appears when a new card shape arrives:

- Compose Herself draws at top level AND inside a branch, and tier0's draw
  delta bumps ALL draw ops -- so both numbers are upgradeable and both need a
  var. `Cards` was taken, so branch draws now get their own name.
- Matinee Performance is the pool's first card with two top-level damage ops
  and both declared `"Damage"`. That is a `DynamicVarSet` constructor throw
  inside `CardFactory.CreateForReward` -- **a reward-screen softlock on
  whatever run rolls the card**, the same shape as the 2026-07-23 incident.
  `damage_var_effect` now binds the var to the one effect tier0 actually
  upgrades, exactly as `power_upgrade_effect` already did for powers.

**The register column is fenced off by a lint** (`lint_register_isolation.py`,
wired into `test_sheet_lints`): nothing under `tier0/engine` or `tier05` may
read it, `state.py`'s declaration excepted, and `tools/` is deliberately not
scanned because guiding art selection is the entire point of having a
register. Cell 1 PROVED the isolation empirically -- renames plus registers,
byte-identical -- but a measurement only speaks for the code that existed
when it ran. The coupling this forbids: with a register-aware engine, moving
a card from the salon voice to the archon one, an ART decision taken on art
grounds, would silently move win rate. Codegen is separately proven to ignore
the field by a byte-identity test against a stripped sheet.

Parity vectors extended with the card-body READS (riders and thresholds),
derived through the sim's own `_bonus_formula` and `_predicate` so the table
cannot be fudged into agreement with a bug. Both new gates were verified RED
before being trusted.

**Class: MECHANICAL** -- zero design decisions, per the sprint's own charter.
No balance, body, cost, name, type, rarity or register changed; D12 stays
frozen; no sheet edit. Suite 1280 passed / 1 skipped; Release build clean;
pck 114 resources; `validate: OK`; deployed 0.2-217.

**OPEN, and NOT closed by this entry:** gate G1 (contact-sheet eyes-on for
the four REHUNT picks plus the `standing_room_only` overturn) and gate G2
(in-game screenshot review of the twelve cards and the A0 smoke run). Both
are [USER] and both are eyes-on by nature. Six power icons are declared art
debt in `$pckDeferred`.

## R87 -- The sweep backlog ruled: three deferrals, a rework, a DRAFTER world, and a design pass (2026-07-29)

Ruled by [USER] in session against `docs/backlog-2026-07-29.md` §3 (the
consolidated owed-item register produced by the four read-only sweeps of
2026-07-29). Four rulings, taken together in one sitting, exactly as §3
asked for. No code, no sheet and no number moved with them.

**(1) Items 1-3 DEFERRED, behind one playtest with a pre-registered
question.** The Furina strength lever + legibility pair, the
dead-archetype question (fanfare stopped at 1.8% against its 2.0% floor;
Spotlight sits at 2.0-2.3% with nothing ever aimed at it) and the salon
leak lever (10.8% against the ruled 7.8% anchor) all wait on a Furina
playtest. **The question that playtest must answer first is written down
before it runs:** is the pilot simply BETTER at Salon than at the other
archetypes, or does everything feed Salon BY CONSTRUCTION? The three
items are one question wearing three hats, and answering them separately
costs three sprints. Standing consequence until it runs: no Furina
balance value moves, the fanfare STOP holds, and every Furina row on
record stays a pilot-limited floor (Guardrail 7).

**(2) Item 4 -> full REWORK, and the A7 decay ruling is MOOTED.** On
re-read of `unheard_confession`: *"on second read, this does way too
much."* The card goes to a design pass, not to a turn-order fix. The A7
question as filed -- should the sim's decay/Block-clear order move so the
card's "pays on the way down" half pays, or should the C# stay faithful
to the sim (`docs/sprint-art-and-a7-log-2026-07-29.md` §B.3) -- is a
question about which engine should pay a card that is being rewritten, so
it is withdrawn rather than answered. It returns, if it returns at all,
as a consequence of the rework and not as its premise. The same-day C#
bug-fix pass was fenced off the decay path explicitly and touched nothing
there (that log, "Still owed" §E). Options for the red pen:
`docs/brief-unheard-confession-rework.md` -- a brief, with no
recommendation.

**(3) Item 6 ACCEPTED: the drafter repricing proceeds now, as a DRAFTER
13 world.** The drafter prices 42 of the engine's 56 ops at exactly zero
at offer time (`tier05/draft.py`), which biases every run-layer winrate
we quote. The scheduling question WAS the ruling and the answer is *now*,
**in parallel with the playtest** -- the playtest question (1) is about
the sim's pilot and the mod's table and does not read the drafter's price
list, so the two do not collide. Consequence, and it is the expensive
half: on the stamp bump every drafter-layer number taken under DRAFTER 12
becomes archive and must be re-measured before it is quoted again. World
after the bump: RUNTEMPLATE 7 / CONSTANTS 4 / DRAFTER 13.

**(4) Item 8 -> a design pass, taken TOGETHER with the rework.** The two
co-op charter items -- Fanfare partner-flux with its mandatory Hot Hands
anti-farm audit (`furina-kickoff-v0.1.md` §4), and cross-player Spotlight
selector passing (§3.1 / §11.5) -- were deferred behind conditions that
have since lapsed: co-op is live and has been played twice. They are
ruled to be DESIGN, not backlog, and they ride with the
`unheard_confession` rework because both passes ask the same question
about how much a single Furina card or hook should be doing. Brief:
`docs/brief-coop-charter-items.md`.

**Recorded as context, not ruled.** The same-day C# bug-fix pass landed
and deployed while this sitting ran: `29f5ce6`, artefact **0.2-247**, log
`docs/sprint-bugfix-log-2026-07-29.md`. It is MECHANICAL by its own
charter -- ten confirmed defects plus three extra NRE-class sites, no
balance value, sheet, sim constant or piece of art touched -- and carries
no ruling of its own. It appears here only because ruling (2) is what
fenced it away from the decay path, and because the Furina playtest that
rulings (1) and (3) both refer to runs on that build.

**Class: RULING** ([USER] 2026-07-29, four rulings on one backlog). No
measurement; nothing in tier0 or tier05 moved with this entry.

## R88 (DRAFT -- reconstructed, needs [USER] countersign) -- Zhongli takes roster slot 4; Itto becomes Inazuma-companion eligible

**Reconstructed 2026-07-29 from the archival record. The RULING is real
and dated 2026-07-23; only this RECORD is new, and it is unsigned.** The
kickoff directed "Record in DECISIONS.md" and no entry was ever written
(`docs/missed-requirements.md` Tier 5, first item). Do not read this as
ratified text until [USER] countersigns it; read it as the best available
reconstruction of a ruling whose consequences were built.

**Source of record:** `docs/kokomi-kickoff-v1.md` §0, third bullet
("Slot-4 ruling (this thread): Zhongli takes slot 4. Supersedes the
Itto-vs-Zhongli open item in A1. Consequence: Itto is now eligible for
the Inazuma companion pool (mirror of the Neuvillette-reserved pattern in
reverse). Record in DECISIONS.md."), corroborated by the comment at
`docs/inazuma-companions.yaml:4`.

**Ruled (as reconstructed).** (1) **Slot 4 is Zhongli.** This supersedes
roster amendment A1's open Itto-vs-Zhongli item, which is closed by this
and by no later doc. (2) **Itto is therefore eligible for the Inazuma
companion pool**, by the reserved-character pattern read in reverse: a
character reserved for a playable slot may not appear as a companion, so
a character who LOSES the slot is released to the companion pool.
Neuvillette is the forward instance of the same rule.

**Built, unrecorded.** The consequence shipped -- Itto is authored in
`docs/inazuma-companions.yaml` -- while the record was not, which is the
exact failure class this reconstruction exists to close. Nothing here
pre-commits how Zhongli's slot-4 archetype scales
(`docs/fontaine-rares-banner-sprint-log.md` flags that separately), and
the pre-Zhongli registry gate (slot 4 must not declare elite axes before
it) stays exactly where the Serenitea Sweep put it.

**Class: RULING (DRAFT)** -- [USER] 2026-07-23 per the kickoff;
countersign owed. Tracked at `docs/backlog-2026-07-29.md` §3 item 9.

## R89 (DRAFT -- reconstructed, needs [USER] countersign) -- Furina legibility: the preview-truth fix, and why the doc's own migration was the wrong one

**Reconstructed 2026-07-29 from the archival record. The sprint SHIPPED
on 2026-07-24 and is deployed; only this RECORD is new, and it is
unsigned.** The sprint's own open item 3 deferred the entry "until
commit" and it never landed -- a whole shipped C#/codegen sprint with no
decision record (`docs/missed-requirements.md` Tier 5, second item).
Source of record: `docs/archive/furina-legibility-sprint-log.md` plus the
commit trail it cites (`a1bca0d`, `a22c6dd`, `b8bf790`, `6af7a71`,
`4f0c3c8`, `16d3273`, `0b33ffd`).

**The premise the sprint was opened on was false, and that is the first
thing worth recording.** The governing doc's leading hypothesis -- "her
cards ship static localized strings" -- did not survive the first audit:
every Furina card already shipped on DynamicVars with `:diff()`. The real
defect was a **split value path**. A number greens iff something raised
its `PreviewValue`, and `PreviewValue` is reachable only through
`Hook.ModifyDamage` (DamageVar) or `Calculate` (CalculatedVar); Furina's
Spotlight / Fanfare / Salon modifiers reached neither, living in
`SpotlightSystem.PrintedDamage` and in per-card `OnPlay` arithmetic. The
face showed the base; the hit resolved larger.

**Ruled at the time ([USER] 2026-07-24), as reconstructed.** (1) Adopt
the modifier-path migration as the sprint's spine, replacing the doc's
L-B "static-to-DynamicVar conversion" framing. (2) Ship "the safe half
globally" first. (3) Both blocked salon items ratified later the same
day.

**And then the doc's own named fix was ruled WRONG on inspection, which
is the load-bearing finding.** `Hook.ModifyDamage` runs ALL additive
before ALL multiplicative, whereas `PrintedDamage` is
`Truncate(printed x mult) + flat` on the printed number AHEAD of Strength
and Vulnerable -- so a hook-based Spotlight folds Strength into the 1.5x
and CHANGES RESOLVED DAMAGE. What shipped instead is a
`CalculatedDamageVar` whose multiplier CALLS Spotlight
(`base + 1 x (PrintedDamage(base) - base)` is identically
`PrintedDamage(base)`), so no number can move. A legibility sprint that
had taken its own doc's advice would have shipped a silent balance
change.

**Landed (all deployed).** The fanfare `N_per_M_fanfare` rider trio via
`tools/gen_klee_cards.py` (3 cards) and by hand for the kit Burst;
single-target `bonus_vs_aura` to CalculatedDamageVar -- with **AoE aura
riders deliberately NOT converted**, pinned by
`test_aoe_aura_riders_stay_per_target`, because AttackCommand resolves a
CalculatedDamageVar ONCE with `singleTarget == null` and converting would
collapse a per-enemy decision into one board-wide value; the damage half
(11 companion cards) and the block half (7 cards, on the game's own
`CalculatedBlockVar`); the salon multiplier (6 cards) with
`SalonMemberPower.StageIsFull` as the ONE expression of the replacement
rule; and the L-C tip re-homing (5 cards, `Cards/FurinaRiderTips.cs`)
under the shipped rule: re-home a rider's arithmetic IFF it now renders
inside the printed number, and unconverted riders KEEP their sentence
because the text is the only place their number can be read. Suite 648 at
close.

**Standing traps recorded by that sprint** (they have already caught
readers): `DynamicVar.IntValue` is `(int)BaseValue`, and a CalculatedVar's
BaseValue is only its base term -- always call `Calculate()`; the draw var
is `DrawCards`, not `Cards`; CalculatedDamageVar and CalculatedBlockVar
both take their base from the single `CalculationBase` var, so a card
doing both can convert only one.

**Class: MECHANICAL + RULING (DRAFT)** -- zero design decisions and zero
sheet/sim movement by charter; the [USER] rulings are the migration spine
and the "safe half globally" sequencing. Countersign owed; tracked at
`docs/backlog-2026-07-29.md` §3 item 9.

## R90 -- Track A's P1 null: the lint stays a counting tool, the Fanfare question moves to Track B, the floors are re-derived (2026-08-04)

Countersigned package, filed verbatim at
`docs/axis-validity-countersign-2026-08-04.md`; this is Ruling 1 (a-c) of
three. Discharges the STOP the charter's binding null put on Track A
(`docs/sprint-axis-validity-track-a-log-2026-08-04.md` §0).

**What the null actually was.** P1 predicted the first coverage run would fail
Furina on (fanfare x frontload x fight-early) and (fanfare x scaling x
fight-late). It failed nothing: Furina cleared every cell, two of them by 59
and 36 points, while Klee and Kokomi posted 30 findings on the same
instrument. The playtest's verdict was *"Fanfare is too slow early and too
small late"* -- a claim about SIZE and TIMING -- and a coverage lint counts
cards. **The payoff cards exist; they pay too little.** The prediction was
registered against an instrument that could not see the hypothesis. That is a
specification error upstream of the code, not a defect in the taxonomy: the
same tool discriminated correctly on the other two pools.

**1a -- the lint stays, as a counting tool.** Its whole job is "does a card
for this job exist at this point in the fight?" It gets no magnitude gate, now
or later; a magnitude gate would be authoring balance numbers. The Klee and
Kokomi findings are REAL and stay pinned in `docs/role-tempo-debt.tsv`; the
gate fails only on NEW findings. The debt list is deleted when the reworks
address the gaps, not before.

**1b -- the Fanfare size-and-timing question moves to Track B**, re-registered
in the playtest's own words. Track B measures produced damage and block per
turn against demanded per turn, which is the instrument that can see "too slow
early, too small late". **P1's ledger line reads: "prediction aimed at the
wrong instrument; withdrawn and re-registered, not failed."** It is not graded
as a failed prediction and it is not quietly deleted either.

**1c -- the floors are re-derived from canon PACKAGES.** The first pass
compared a GItS archetype (11-32 cards, all one plan) against a whole canon
character (88 cards spread across everything). An archetype's per-cell density
is structurally higher, so the bar was generous BY CONSTRUCTION -- that is why
Furina cleared floors by 40-60 points, and it is a property of the population,
not a verdict on her pool. The comparison population is now the canon package:
the cards that touch one mechanic layer, **on both sides** (the card that
applies Poison and the card that reads the stack are both poison cards).
Packages run 8-41 cards. Membership is structural, off the decompiled body, so
no hand-drawn card list enters the repo.

Executed: `tools/canon_role_tempo.py::PACKAGES` (five), `ARCHETYPE_ANCHORS`
(eight archetypes named to the canon package shaped like them),
`derive_package_floors`, `check_package_floors`. The standing stop-and-surface
rule -- *a floor that would fail the canon population it came from means the
derivation is wrong* -- is asserted on every run rather than argued: an
anchored package clears its own floor with equality and nothing else.

An archetype with NO named anchor falls back to `min over all five packages`,
which is the old min-of-canon safety rule with the population repaired. Those
absences silence findings, so each is stated in the table rather than left to
be discovered: the three `generic` buckets are glue and canon has no analogue
for "the cards that hold the deck together", and `kokomi/assist` is co-op,
where there is no canon support package to anchor to at all.

**Class: RULING** -- [USER] countersigned 2026-08-04. No balance value moved,
no card was authored or reworked.

## R91 -- A-G1 closes: the seven entities confirmed, the salon double-credit kept with a bounded-meter property, meter-reading damage ruled, sustain bounded (2026-08-04)

Ruling 2 (a-d) of the same package. This is the gate the charter deferred at
§7 ("tag review, esp. tag-through targets"), and closing it is what let the
tags LAND on the three sheets -- the REVIEW column retires with it.

**2a -- the seven `ENTITY_PAYOFFS` CONFIRMED as proposed.** Chevalmarin
sustain; Crabaletta frontload; Usher block; the bomb frontload at mid/late;
the spark frontload + velocity; the Bake-Kurage block + frontload + scaling;
the Spotlight scaling at mid/late. Each already carried one line of provenance
quoting the sheet that defines it, and none read lore-wrong. No code moved for
this ruling and that is the correct outcome of a confirmation.

**2b -- the `salon_member` double-credit is KEPT, with an amendment.**
Deploying a member creates two real things: the member, who acts, and a higher
member count, which other cards read. Both are payoffs of the same play and
crediting one would understate the card either way. [USER]'s amendment: the
Salon caps at THREE, so a count-reading card may really be *frontload after a
setup tax* rather than true scaling -- which depends on how fast the Salon
fills, and that is unmeasured. **Resolution: tags stay as proposed, and every
meter gains a bounded/unbounded property whose cap is READ FROM
`tier0/constants.py`** (`tools/role_tempo.py::METERS`, `meter_cap`). Bounded:
`salon_member` 3 (`SALON_MEMBER_SLOTS`, whose own comment already read
"Defect-orb shape"), `fanfare` (derived, `FANFARE_CAP_FRACTION` x maxHP),
`spark` 3 (`SPARKS_FOR_FREE_ATTACK`). Unbounded: `encore` ("no cap constant by
design", verbatim), `charge`, `burst`, `exhaust_pile`. Canon's precedents are
the ones the ruling names: orb slots bounded, Focus and Strength unbounded.
A cap that lives in a comment is a cap that drifts, so none of these is
retyped.

**Pre-registered in Track B by this ruling:** the Salon fill-time measurement
-- the turn the Salon first fills, and the fraction of fight-turns it sits
full. If bounded-meter readers plateau early on Track B's output curves, the
`scaling` tag for those readers is revisited WITH DATA IN HAND. Not before,
and not on intuition.

**2c -- a damage card that reads a meter is `scaling`; it is ALSO `frontload`
only if it deals damage with the meter at zero.** "Deal 6, plus 1 per 4
Fanfare" is both. "Deal 1 per 4 Fanfare" is scaling only. The sheets said all
three things in different places (applause_line vs crescendo vs
all_streams_flow) and that inconsistency predates this track. Implemented as a
SUGGESTER RULE, not a hand-ruling per card, because pays-at-zero is checkable
straight off the sheet: a printed positive `amount` on a line that is not
sitting behind a gate. A gated line pays nothing at meter zero by definition,
and `amount: 0` with a bonus_formula is the sheets' own explicit "this pays
nothing on an empty meter" idiom -- suffering_for_art says so out loud. **19
cards moved**: 15 gained `scaling` beside their `frontload`, and 4 lost
`frontload` outright (the_final_verdict, pearl_barrage, undertow,
depths_judgment) because they deal nothing on an empty meter.

**2d -- `sustain` means in-combat healing and prevention of YOUR OWN HP, and
nothing else.** The boundary, as clarified in review: your own HP ledger =
sustain (heals, max HP, Buffer-style prevention); the ENEMY's output = disrupt
(Weak, Frail); absorbing a hit this turn = block. They are kept apart because
they play differently -- in co-op one player's Weak protects the whole party
while block and heals protect one seat. Silent is the worked example: zero
sustain, excellent mitigation through 0-cost Weak, and that is her identity
rather than a gap. **Consequence: `sustain` joins `utility` and `support` on
the never-linted list** (`tools/role_tempo.py::NEVER_LINTED`); under the
structural definition canon carries 0.0-2.3%, so a sustain floor would measure
noise. **Zero sustain is a legal identity.** The charter's earlier "Ironclad
15%" counted between-fight healing, which a combat taxonomy rightly ignores.

**Recorded, not silently collapsed:** `disrupt` gets no `solve` value of its
own in this implementation. Weak and Frail are the sheets' `utility` voice and
`utility` is protected free space, so the ruling's load-bearing half -- *they
are not sustain* -- already holds. Minting a sixth lintable role would be a
new vocabulary value on three ratified sheets and is outside this repair's
scope. The pointer is in `tools/role_tempo.py` beside `NEVER_LINTED`, and the
question the sixth role would have answered -- how well a character preserves
HP -- is a derived outcome across sustain + disrupt + block that Track B's HP
trajectory measures directly.

**Class: RULING** -- [USER] countersigned 2026-08-04 (2b with amendment, 2d
with clarification). The tags landed on all three sheets in the same pass; no
balance value moved and no card was authored or reworked.

## R92 -- Track A housekeeping: the canon count corrected, tempo_band takes its cross-session note, the support gap goes to Kokomi (2026-08-04)

Ruling 3 (a-c) of the same package, ACKNOWLEDGED rather than argued.

**3a -- "402 canon cards" was an arithmetic slip.** The charter's own per-pool
wiki figures sum to 456; the DLL prints **439**, of which **410** are
draftable (5 x 82 common+uncommon+rare). Header corrected. No percentage
anywhere moves, because every percentage in the charter is within-pool.

**3b -- the cross-session note comes BEFORE `tempo_band` lands, not after.**
The sheet schema is read by `tier0/content/loader.py` (through
`Card.from_dict`, which hard-fails on an unknown field) AND by the C# codegen
(`tools/gen_klee_cards.py::CARD_FIELDS`, which blocks a card carrying a field
it does not understand). Two readers, one surface, so this is a shared-surface
change and takes its note first. Note filed at
`docs/sprint-axis-validity-track-a-log-2026-08-04.md` (CROSS-SESSION NOTE
section, house pattern per `docs/animation-sprint-2-log.md`), mirrored in
`docs/roster-codegen.md`. The field landed after it, in a later commit, which
is the ordering the rule exists to produce. **This is the one shared-schema
change this repair was authorized to make.**

`tempo_band` is inert on both readers by design: two orthogonal scales
(`fight: early|mid|late`, `run: early|late`), descriptive metadata like
`register` and `solve` beside it, nothing emitted and nothing simulated. The
suite proves both readers handle it.

**3c -- the support gap is a Kokomi rework input, not a lint cell.** `support`
reads **0% on all three GItS sheets** against 2.3% in every canon pool. No
GItS row has an ally target, an ally op, or a co-op constraint, so there is
nothing for a classifier to find -- the finding is structural absence, not
mis-tagging. Kokomi's Assist archetype is where those cards belong and none
exist anywhere. Filed to `docs/brief-kokomi-pool-fill.md`, marked NOT LINTED
(the sim is one-seat; D4) and REWORK-INPUT. It is not a gate and must not
become one through this door.

**Class: MECHANICAL + RULING** -- [USER] acknowledged 2026-08-04. No balance
value moved.

## R93 -- Understudy policy_v1: all seven revisions approved, the card-name log elevated to a P1 blocker, the block-panic insight routed to the pilot backlog (2026-08-04)

Ruling 1 of the Understudy Phase-0 skim response, countersigned verbatim at
`docs/understudy-countersign-2026-08-04.md`. The gate the Phase-0 report
stopped at was "[USER] skims the policy_v1 list before the soak", and it
passed unamended: **all seven proceed.**

The list, and what each closes, is in the report
(`docs/understudy-phase0-report.md`, "policy_v1 -- PROPOSED revisions"). What
this entry records is the two notes the signature attached.

**#7 is a P1 BLOCKER, not a nicety.** The Phase-0 log stores `card_index`, so
a sequencing divergence can only be categorised by reading the human's prose
`why` field. That is exactly how this pass produced its 53%/28% table -- by
hand, over 191 lines. A thousand-run soak cannot be read that way, and a log
that cannot be analysed automatically **produces heat, not data**. So no soak
launches until resolved card NAMES are in the log. This is the same structural
rule the house already applies to prose caveats on numbers: a fact that lives
only in prose does not survive contact with volume.

**#2's insight belongs to the sim as well, and is routed rather than acted
on.** Gating the block-panic rung on whether the block on offer can
meaningfully dent the incoming, and preferring a lethal line when killing a
body removes more incoming than the block prevents, deliberately makes
Understudy's policy **smarter than the tier05 pilot it is a reduction of**.
That direction is intended -- Understudy is not required to be a faithful
mirror once the measurement it was built for is taken. But the same gap is
real inside `tier0/pilot/policy.py`, where the rung fires on the ratio of
incoming to HP alone and will buy 4 block against 39 incoming every time.
**Nobody changes `tier0/pilot/policy.py` for it now.** It is filed as a note
on the pilot-improvement backlog (`docs/backlog-2026-07-29.md`), and it stays
a note until a session is chartered to open it. Changing the sim's pilot
mid-sprint would move every tier-0.5 number in the repo on the strength of
one nine-floor observation.

**Scope, restated because the boundary is the whole point:** every one of the
seven lives in `understudy/`. Nothing in `tier0/`, `tier05/`, the drafter or
any sheet is touched by this ruling.

**Class: RULING** -- [USER] countersigned 2026-08-04, unamended.

## R94 -- Phase 2's default tier is amended from draft sampling to hard-state turn sampling (2026-08-04)

Ruling 2 of the same package. This one overrides a pre-registration on the
evidence the pre-registration itself produced, so the reasoning is recorded
in full rather than summarised.

The kickoff brief pre-registered M3 ("one full LLM-driven run completes in a
single Code session") with a consequence attached: **if false, Phase 2's
sampled-decision tier drops to draft-picks-only by default.** M3 FAILED --
the run reached Act 1 floor 9 of 16 -- so that fallback was technically in
force the moment the report was written.

**It is amended, and the amendment comes from the same run.** M2 measured
where the cheap policy and the LLM actually disagree:

| category | agree% | share of all decisions |
|---|---|---|
| draft (card reward) | 60% (3 of 5) | 3% |
| sequencing (combat card play) | 53% overall, **28%** on independent turn-openers | 88% |

Draft is the category the two arms agree on **most**, and it is 5 decisions
in 9 floors. Sequencing is where all the disagreement lives and where nearly
nine tenths of the decisions are. **A tier that samples only draft picks
would spend the LLM budget where it helps least** -- it would buy judgment
for the question the heuristic already answers.

**Amended default: hard-state turn sampling.** The LLM tier engages at
turn-openings in states flagged hard by cheap triggers computable straight
off the wire -- incoming above a set fraction of HP, more than one enemy
alive, lethal within reach. The economics that make this affordable are M1's
second finding: **117 of 167 decisions were later steps of a planned turn**,
issued with no fresh state read. One state read plans a whole turn, so the
marginal cost of judgment is paid per *turn*, not per *card*.

Draft sampling is **dropped from the default and retained as an option**, not
deleted -- the 5-decision sample it was judged on is small enough that a
later run could move it.

**The trigger thresholds are P2 design work and are NOT set here.** This
ruling fixes the tier's shape; the numbers that decide "hard" are a later
session's, with data in hand.

**Class: RULING** -- [USER] countersigned 2026-08-04. Supersedes the M3
fallback clause in `docs/understudy-kickoff-brief.md` (P2 section), which is
left standing as written so the pre-registration reads as it was registered.

## R95 -- The seed fork: read-back seeds launch P1, chosen seeds are gated at the first cross-build comparison (2026-08-04)

Ruling 3 of the same package, and the one that decides what P1 can and cannot
be quoted for.

The Phase-0 report's first stop-and-surface is that **the bridge cannot start
a chosen-seed run through the singleplayer path**: `menu_select` with a `seed`
requires `charSelect.Lobby != null`, and the Custom-run screen where a seed
would be entered is not modelled by the bridge at all (selecting it soft-locks
to a `menu_screen: "main"` with no options and no accepted verb, including
`back`). Three ways out existed: add a Custom-screen arm to our fork, route
through the multiplayer lobby, or accept game-generated seeds read back after
the fact.

**Now, for the P1 launch: read-back.** The soak runs N runs on seeds the game
generates, and records each one per run from `GET /api/v1/compendium`. For
what P1 is *for* -- jank filtering, crash and softlock detection, telemetry
harvest -- N random recorded seeds are statistically fine, and this unblocks
the soak immediately instead of spending the session on a screen arm.

**Before any build-vs-build number is quoted (P1.5): the Custom-screen arm is
MANDATORY.** Comparing an old build to a new build requires running the SAME
seed on both, because one variable per measurement window is the house's
standing discipline and a seed is the biggest variable in a roguelike. Random
seeds cannot do that. So the Custom arm is gated **exactly** there: not a
launch blocker, and not optional the moment a cross-build comparison is
proposed. **A P1 soak number is never comparable to another build's P1 soak
number.**

**Noted, not chosen: the lobby route.** Heavier than the Custom arm, but it is
the one option that pays twice -- Phase 3's two-seat co-op needs the lobby
modelled anyway. If the Custom arm turns out ugly, **evaluate the lobby before
building around the ugliness.**

**Class: RULING** -- [USER] countersigned 2026-08-04.

## R96 -- The three sim observations from Phase 0 are ROUTED to their chartered streams, not opened here (2026-08-04)

Ruling 4 of the same package. The Phase-0 report recorded three things that
look like findings about the SIM rather than about the bot apparatus. None of
them becomes a new finding or a new ruling: **each goes to the stream already
chartered to handle its family**, and each is a note in a queue until that
stream sits down.

1. **`tier05.draft.score_offer` returns exactly 0.0** for The Gallery Stirs, a
   Power reading "the first time you spend Encore each turn, draw 1 card.
   Fanfare Cap +5", in a deck whose three Salon members spend Encore every
   turn. -> **the DRAFTER 13 stream**, as a **regression fixture**. R87(3)
   already established that DRAFTER 12 prices 42 of 56 ops at zero at offer
   time; this is almost certainly one of the 42, observed in the wild rather
   than in a table. The acceptance form the routing note takes: **DRAFTER 13
   is not done while The Gallery Stirs scores 0.0 at offer.**
2. **`score_offer` prices Vulnerable as a flat debuff** (`amount * 2` through
   `_static_power`), so it cannot see a multiplier applied to an engine
   already producing damage every turn. -> the **`_static_power` repricing
   session**, as an exhibit alongside the one it already has.
3. **`tier0.pilot.policy._reaction_value` has no defensive term**, so Frozen
   -- which halves an incoming attack -- is priced only as expected damage.
   -> the **reactions-promotion session**. This is "reactions are weather, not
   strategy" appearing inside the pilot's own head, which makes it a **third
   independent sighting of the same disease** rather than a new one.

**Why routing and not acting.** Each observation is a claim about the sim made
from one nine-floor run. Acting on any of them from here would move tier-0.5
numbers on single-observation evidence, and would do it inside a sprint whose
non-goals say in as many words that nothing here touches the sim, the drafter
or any sheet.

**Class: ROUTING** -- [USER] countersigned 2026-08-04. No code changed in
`tier0/`, `tier05/` or any sheet under this entry. Notes filed at the
locations named in `docs/sprint-understudy-p1-log-2026-08-04.md` (routed
findings).

## R97 -- Understudy housekeeping: the readiness check, the leftover run, the merge order, and the adapter-defect list (2026-08-04)

Ruling 5 of the same package, ACKNOWLEDGED rather than argued. Recorded
because three of the four are cheap now and expensive to rediscover.

**5a -- the soak launcher's readiness check watches the `options` key in the
menu state, NEVER the HTTP health endpoint.** The bridge's HTTP server answers
about 5 seconds after launch; the main menu has no buttons for another ~20.
`GET /` returning ok is therefore not "the game is ready", and a launcher that
treats it as such acts into an empty menu. Written into the P1 spec while it
is cheap, and implemented in `understudy/soak.py::wait_for_menu`.

**5b -- the floor-9 run on the local profile (seed `SSRWEGLNRG`) may be
abandoned at any time.** The measurement it carried is fully captured in
`understudy/logs/phase0-SSRWEGLNRG.jsonl`; nothing depends on the live save.
The soak's setup consequently abandons ANY resumable run it finds rather than
negotiating with it.

**5c -- merge sequencing: Track A's repair fast-forwards main first, then
Understudy goes on top.** No race, and no rebase of one stream over another
stream's unlanded work.

**5d -- the five adapter defects stay recorded as MEASUREMENT HISTORY, not as
open defects.** All five are fixed. They are kept in
`docs/understudy-phase0-report.md` because **any future adapter against this
wire meets the same five** -- enemies under `battle`, intent damage only in
the label, the hand's `target_type`, the aura as `"Cryo Aura"` rather than
`"cryo"`, and the label already carrying the attacker's Strength. The list is
the map, and a regression test would not have caught any of them because each
was a fact about the wire rather than about our code.

**Class: MECHANICAL + RULING** -- [USER] acknowledged 2026-08-04. No balance
value moved.

## R98 -- P1 is VALIDATED: the clean N=3 landed, debt #2 is deleted, and the eleventh harness defect is the same class as the other ten (2026-08-04)

Recorded per the hand-back note of 2026-08-04 (evening),
`docs/handback-note-2026-08-04.md`, which set the acceptance in advance:
"clean completion -> mark P1 VALIDATED in the ledger and delete debt #2."
This entry is that mark. No balance value moved and no policy changed -- the
soak that earned it ran current main code with read-back seeds and nothing
else, which was the whole condition.

**The number.** Three runs, 18 fights, 656 posted actions, **zero defects
filed**; reversibility REVERTED on all four ledger entries; `fast_mode`
captured as `Fast` at setup, which is the leak check the previous soak's
NOT-REVERTED speed entry made worth running. Log stamp `20260804-222105`
(gitignored, per-machine).

**It took two attempts, and the first attempt is why this entry is not just a
tick.** The first N=3 filed `bridge_unreachable` at act 1 floor 6 -- a
HARNESS-side kind. It was not the harness's wire: the game died inside a Punch
Off event, the socket reset under the next request, and `session.alive()`,
asked in the same millisecond, still read True because the OS had not reaped a
process that was mid-crash. **The instrument filed a build defect against
itself**, and two of those halt a soak -- so the failure mode is a night that
stops on exactly the thing the soak exists to find.

Fixed as `Session.died(grace)`, the slow twin of `alive()`, asked only where a
failure has already happened; `alive()` stays instantaneous because the
per-action watchdog calls it on a hot path. Defect records now carry
`proc_exit_code`. Two red tests, one per direction -- a still-crashing process
must read as dead, and a live game with a dead socket must still read as the
wire.

**Class: the traversal/wire layer.** This is the eleventh defect of the family
R97/5d already named ("any future adapter against this wire meets the same
five") and P1's stop-and-surface #1 restated ("the wire's screen protocol is
the expensive half of this apparatus"). It is expected-class and is NOT new
information; debt #1 stands unchanged.

**What the failed attempt found in the BUILD is filed, not fixed.**
`godot.log` ends mid-backtrace on `PunchOff.PunchEachOther` ->
`CreatureCmd.TriggerAnim` -> `NCreature.SetAnimationTrigger` (the GItS
animation-router patch is on the stack) -> `CreatureAnimator.SetNextState`,
with `Signal '_internal_spine_objects_invalidated' is already connected`. One
observation, seed `8B97LMCL2F`. Routed to the animation stream and to [USER]'s
gate package; nothing in Vfx was touched here, because diagnosing a visual
subsystem from one crash inside a measurement pass is how a session acquires
a second, unrelated bug.

**Class: MECHANICAL** -- acceptance recorded against a written, pre-agreed
condition. Debt #2 struck from `docs/sprint-understudy-p1-log-2026-08-04.md`;
debts #1 and #3 stand.

## R99 -- The validation gate's first four items: the build ships, Punch Off is SUSPECTED-OURS, 13/14 go to the next traversal pass, and deck-intent gets both instruments (2026-08-04)

Signed package, verbatim:
`docs/track-b-validation-gate-countersign-2026-08-04.md` (seven items,
countersigned 2026-08-04 late). Execution record:
`docs/sprint-track-b-gate-log-2026-08-05.md`. This entry carries items 1-4;
R100 carries 5-7. No balance value, no card, no floor and no tag moved under
either entry -- the gate package's own scope note says so, and the pass held
it.

**1. Build 0.2-289 KEEP, and the zip is a courtesy contract as much as an
artifact.** The build is content-identical to 0.2-247 plus a read-only
telemetry hook, so the co-op zip goes out for the next table session. The
condition attached to it is not a formality: **[USER] tells the table the build
writes local telemetry to their own machines BEFORE the session.** A
measurement nobody was told about is the same file either way; the difference
is whether the people generating it agreed. The zip this pass packages is the
FINAL build of the pass rather than 0.2-289, because items 5 and 6a land in
between -- handing the table the older one would hand them a build whose
records cannot say who won.

**2. The Punch Off crash is SUSPECTED-OURS, and the validation headline takes
an asterisk.** `Signal '_internal_spine_objects_invalidated' is already
connected` with `NCreature.SetAnimationTrigger` -- the GItS animation-router
patch -- on the stack reads as our patch double-connecting on event-screen
re-entry, and **validation attempt #1 crashed inside Punch Off as well**: two
observations of the same event, not one. Seed `8B97LMCL2F` is the regression
case. Routed to the animation stream's queue in the consolidated backlog
register; nothing in `Vfx` was touched here.

The cost of this ruling is paid where the claim lives:
`docs/sprint-understudy-p1-log-2026-08-04.md`'s "zero defects attributable to
the GItS build" now carries a dated asterisk. **This is the apparatus's first
suspected mod-side catch** -- which is the soak doing the job it was built for,
and a headline that had quietly become a boast is now a headline with a
footnote. If it proves game-side, the routing note flips and nothing is lost.

**3. Harness defects 13 and 14 -- routing ACCEPTED, and they stay unfixed on
purpose.** Both are traversal-class (debt #1's family): 13, the bridge
answering with no `state_type` mid-transition; 14, the wire timing out while
the process stayed alive. Filed with what reproduction exists, owned by the
next traversal pass. A harness every pass re-opens is a harness nobody can
quote a clean run from, and R98's clean N=3 is exactly what would be spent
re-earning it.

**4. Deck intent gets BOTH instruments, in cost order, because they answer
different halves of the same null.** R90/1b's Fanfare early-half prediction was
NOT GRADED by Track B for an instrument reason, not a volume one: B2 measures
cards, and every bot deck is a mixed deck (224 of 299 turn-1 plays `generic`).

  * **(a) Declared intent, human feed.** A session may declare an archetype in
    one line; the hook stamps it on every record and `tools/track_b_curves.py`
    cuts B2 by it. The mechanism is a one-word file, `intent.txt`, beside the
    telemetry logs -- zero friction was a requirement of the hook and stays one
    of the declaration.
  * **(b) The archetype-committed draft arm, bot feed.** A FLAGGED, seeded
    policy variant that drafts with declared-archetype priority. **The flag is
    the only delta from baseline**, and a pinning test proves it by replaying
    recorded states through both settings. Baseline soak behaviour is
    untouched, so R98's numbers stay comparable.

The committed arm is a **policy variant behind a flag, not a policy change**.
It serves two open questions with one instrument: the Fanfare early-half claim
becomes gradeable against a deck that actually is one, and Salon fill time gets
re-measured with the bot-doesn't-build-salons confound removed. Until it
reports, the 0-of-56 fill result stands recorded as **AMBIGUOUS** -- design
finding versus policy gap, undecided -- and **R91/2b's revisit stays open**.
What the committed arm reports is a number for [USER] to rule on; this pass
reports it and revisits no tag.

**Class: MECHANICAL** for items 1 and 3 (a signed disposition recorded as
signed). **Class: SUBSTANTIVE** for item 2 (a defect changes owner and a
published headline changes) and item 4 (a new measurement instrument enters the
apparatus).

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
