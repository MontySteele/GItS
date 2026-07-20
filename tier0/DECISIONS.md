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
    ~8 card picks. Recommendation filed (docs/tier05-m5-report.md):
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
    options (innate Burst recommended) in docs/triage-execution-report.md.
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
    kickoff declares (~2.0 weak by design). (d) Naming/lore audit
    CLEARED per the red-pen naming section: talent/summon names
    pre-verified (sheet header), authored theatrical names on register,
    constellation namespace correctly reserved for upgrades (§3.6).
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
