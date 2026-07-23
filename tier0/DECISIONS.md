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
    kickoff declares (~2.0 weak by design). (d) ~~Naming/lore audit
    CLEARED per the red-pen naming section~~ **AMENDED by R29
    (2026-07-20): audit PREPARED (talent/summon names pre-verified,
    theatrical names on register, constellation namespace reserved
    §3.6) — but a document citing another document cannot close a
    [USER] gate (the v1.7 lesson). User eyes-on naming/lore pass OWED
    BEFORE SHIP; the pass itself is the closure.** (a)-(c) ratified by
    R29; veto window closed.
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
