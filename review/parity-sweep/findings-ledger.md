# S1 — Three-Way Card Parity Sweep: Findings Ledger

> Surplus-week stream S1 (cloud). 2026-08-05. One Opus agent per card (219 total:
> 76 Klee, 82 Furina, 61 Kokomi). Three legs per card: design sheet + upgrade delta
> (docs/*.yaml), tier0 engine op semantics (tier0/engine/), klee-mod C# implementation.
> Every finding carries two-leg file:line evidence; claims without evidence were invalid
> by protocol. NO FIXES anywhere — verdicts only. Triage memo: triage-memo.md alongside.

**Verdicts: 219/219 · CLEAN 147 · with findings 72 · raw findings 111**
By family: other 46, text_ops_mismatch 32, sim_vs_csharp_divergence 22, upgrade_delta_drift 11. By severity: low 76, medium 26, high 9.

## Klee — 76 cards, 15 with findings

### klee:kaboom
- **[low] other** — The Kaboom class doc comment states the sheet's damage is 6, but the design sheet prints 7 and the class's own CanonicalVars declares 7 — a stale comment that misstates the card's own printed number.
  - `klee-mod/KleeCode/Cards/Kaboom.cs:18 — "/// Klee's basic attack. Sheet: cost 1, damage 6, single target."`
  - `docs/klee-cards.yaml:8 — "effects: [{op: damage, amount: 7, target: enemy}]"`
  - `klee-mod/KleeCode/Cards/Kaboom.cs:55 — "new List<DynamicVar> { new DamageVar(7m, ValueProp.Move) };"`
  - _Comment-only drift; no player-visible effect. Runtime behavior (7 base) is correct and agrees with the sheet and the sim._

### klee:chain_fuse
- **[medium] text_ops_mismatch** — The C# card text reads as a turn-long standing effect ("Bombs placed this turn deal 3 more damage") immediately followed by "Place a Bomb ... dealing 4 damage", but both engines implement the buff as a one-time snapshot mutation of bombs that already exist at cast, applied BEFORE the card's own place_bomb. The bomb this very card places — which is unambiguously "placed this turn" — is not buffed, so the second sentence's 4 stays 4 (7 expected by the printed text). Same wording tension the repo already flagged for Kaboom Beetle Swarm, left un-reviewed here.
  - `klee-mod/KleeCode/Cards/Generated/ChainFuse.cs:47 — ("description", "[gold]Bombs[/gold] placed this turn deal {Bonus:diff()} more damage. Place a [gold]Bomb[/gold] on a random enemy dealing {Damage:diff()} damage.")`
  - `docs/klee-cards.yaml:33 — effects: [{op: modify_bombs, scope: placed_this_turn, bonus: 3}, {op: place_bomb, amount: 1, target: random_enemy, bomb_damage: 4}] — modify precedes place, so the card's own bomb is outside the buffed set`
  - `tier0/engine/effects.py:916-921 — _op_modify_bombs iterates only bombs already on state.living_enemies at call time and mutates bomb.damage in place; nothing hooks future placements`
  - `klee-mod/KleeCode/Cards/Generated/ChainFuse.cs:67-75 — BombPower.ModifyAll(...) runs first, then the BombPower.Place loop; the newly placed charge is created after the mutation pass`
  - `klee-mod/KleeCode/Powers/BombPower.cs:267-293 — ModifyAll is a pure one-shot mutation over existing _damages entries, not a registered listener`
  - `klee-mod/DECISIONS.md:1153-1155 — precedent: "The card's printed text still reads as live state and is flagged for [USER] wording review, not silently reworded."`
  - _Not a sim-vs-C# divergence: tier0 and the C# agree exactly (snapshot semantics, modify-before-place). The disagreement is text vs ops, present identically in both engines. DECISIONS.md:1158-1160 records the ordering as intentional and "sim-exact", but says nothing about the card text; downgraded to medium rather than high because the behavior is ratified and only the wording misleads._

### klee:sizzle
- **[low] other** — The C# class doc comment states the sheet numbers as "7 damage; +5 more", but the sheet (and the class's own CanonicalVars) are 8 base damage and +6 conditional. Stale pre-survival-sprint numbers in the summary comment; the executable values are correct.
  - `klee-mod/KleeCode/Cards/Sizzle.cs:19 — "/// Sheet: common attack, cost 1, 7 damage; +5 more if the target has a"`
  - `klee-mod/KleeCode/Cards/Sizzle.cs:56-57 — new DamageVar(8m, ValueProp.Move), new ExtraDamageVar(6m)`
  - `docs/klee-cards.yaml:68-69 — effects: [{op: damage, amount: 8, target: enemy}, {op: conditional, if: target_has_nonpyro_aura, then: [{op: damage, amount: 6, target: enemy}]}]`
  - `docs/archive/klee-survival-sprint-plan.md:84 — "| Sizzle | damage 7 -> 8; aura rider 5 -> 6 |"`
  - _Cosmetic only: no player-visible number is wrong. Same class of stale doc-comment drift exists on Kaboom.cs:19 ("damage 6" vs DamageVar(7m)), so this looks like a repo-wide comment-maintenance gap rather than a Sizzle-specific regression._
- **[low] sim_vs_csharp_divergence** — Overkill edge case: if the first hit kills the target, the C# suppresses the aura bonus entirely (IsAlive guard), while tier0 re-picks the aim between ops and lands the 6-damage bonus on the next lowest-HP living enemy.
  - `klee-mod/KleeCode/Cards/Sizzle.cs:79 — "if (hadOffElementAura && cardPlay.Target.IsAlive)"`
  - `tier0/engine/effects.py:594-595 — "for _ in range(times): for enemy in _pick_targets(state, target):" (the then-branch damage op re-resolves its own target)`
  - `tier0/engine/effects.py:245-247 — "CAVEAT ... across ops the aim is RE-picked, so a hit that kills the aimed enemy hands the rider to whoever is lowest-HP next, not to a corpse."`
  - `klee-mod/KleeCode/Cards/Generated/TailOfFlame.cs:75 — the sibling conditional-damage card has no IsAlive guard, so the guard is Sizzle-specific`
  - _Only observable in multi-enemy fights where hit 1 is lethal; single-enemy fights agree (sim has no living target, so the branch deals nothing). tier0 documents the re-pick as an accepted engine-wide model caveat shared with Bash/Uppercut, so this is arguably sweep baseline rather than a Sizzle defect — filed low for that reason. The predicate itself is in exact parity: both legs snapshot the off-element aura BEFORE the first hit (effects.py:2243-2244 and :1590-1593 vs Sizzle.cs:70-71)._

### klee:controlled_demolition
- **[low] other** — The card's sheet comment still carries the pre-verification telemetry claim ("demolition arm measured 4.7% at 600 runs -- unchanged ... within noise"), which the repo's own red-pen record explicitly retracts as measured in-repo at 4.7% -> 7.0% (+2.3pt, "the largest single-card movement in this whole ratification"). Comment-only drift; the ops, upgrade delta, sim semantics and C# all agree.
  - `docs/klee-cards.yaml:123 — "# Post-edit demolition arm measured 4.7% at 600 runs -- unchanged, which is the expected result for"`
  - `docs/klee-cards.yaml:124 — "# one uncommon and is within noise rather than evidence of nothing happening."`
  - `docs/red-pen-2026-07-26.md:227 — "### `controlled_demolition` is not \"unchanged\". It is +2.3pt."`
  - `docs/red-pen-2026-07-26.md:231 — "(`bomb_damage` 5 → 7, count back to `X+1`) moves demolition **4.7% → 7.0%**,"`
  - _Not a three-leg parity defect: no player-visible number or behavior is affected. Filed at low because a future red-pen reader taking the sheet comment at face value would use the retracted figure; docs/red-pen-2026-07-26.md:239 asks for the card to be re-read with 7.0% in hand._

### klee:kaboom_beetle_swarm
- **[medium] text_ops_mismatch** — The C# printed description says the +N rider is paid by "Bombed enemies ... per hit" (live state), but both the sim and the C# snapshot bombed-state at cast, so an enemy whose bombs are detonated by hit 1 stops being Bombed and still collects the rider on hits 2 and 3. Against a single bombed enemy the card reads as 8/5/5 and actually does 8/8/8.
  - `klee-mod/KleeCode/Cards/KaboomBeetleSwarm.cs:56 — description: "[gold]Bombed[/gold] enemies take {ExtraDamage:diff()} more per hit."`
  - `klee-mod/KleeCode/Cards/KaboomBeetleSwarm.cs:93-97 — inside the series the snapshot (_bombedAtCast) is the authority, not target.Powers.OfType<BombPower>()`
  - `klee-mod/KleeCode/Cards/KaboomBeetleSwarm.cs:109-111 — _bombedAtCast taken once at the top of OnPlay, before any hit`
  - `tier0/engine/effects.py:579-581 — bombed_at_cast = {id(e) for e in state.enemies if e.bombs}, taken once per cast`
  - `tier0/engine/effects.py:596-597 — per hit the rider is keyed on bombed_at_cast membership, never on live e.bombs`
  - `tier0/tests/test_klee.py:556-558 — pins hits == [8, 8, 8] with a detonation occurring on hit 1`
  - `klee-mod/KleeCode/Powers/BombPower.cs:60 — "Detonates early if this enemy takes unblocked [gold]Attack[/gold] damage." (so hit 1 clears Bombed in normal play)`
  - _Known and tracked, not new drift: the card's own comment flags it (klee-mod/KleeCode/Cards/KaboomBeetleSwarm.cs:45-50) and the rewording is queued as an open item awaiting user countersign at docs/open-playtest-items.md:235-240 (R72 item 4). Mechanically the three legs agree exactly — this is a text-vs-ops disagreement only. Reported so the parent can dedupe against the tracked item rather than treat it as unnoticed._

### klee:gleeful_barrage
- **[medium] text_ops_mismatch** — The card's printed description says all of its hits land on "a random enemy" (singular, one target), but both the sheet op and both implementations re-roll the random target on EVERY hit, so the 2+Sparks hits are spread across enemies. Every sibling multi-hit random-target card in the same generator uses the plural "random enemies ... N times" phrasing; only the times_formula branch hardcodes the singular, and its hit count is never less than 2.
  - `klee-mod/KleeCode/Cards/Generated/GleefulBarrage.cs:50 — ("description", "Deal {Damage:diff()} damage to a random enemy, 2+[gold]Sparks[/gold] times.")`
  - `klee-mod/KleeCode/Cards/Generated/GleefulBarrage.cs:70-72 — .WithHitCount(2 + SparkPower.SparksAtPlay(...)) ... .TargetingRandomOpponents(CombatState!) (random target per hit, count always >= 2)`
  - `docs/klee-cards.yaml:141 — {op: damage, amount: 3, target: random_enemy, times_formula: 2_plus_sparks}`
  - `tier0/engine/effects.py:593-594 — `for _ in range(times): for enemy in _pick_targets(state, target):` — the target is re-picked inside the hit loop`
  - `tier0/engine/effects.py:259-260 — _pick_targets("random_enemy") returns a fresh state.rng.choice(living) on each call`
  - `tools/gen_klee_cards.py:3953-3957 — times_formula branch hardcodes "to a random enemy, 2+[gold]Sparks[/gold] times" and `continue`s, bypassing the plural rule`
  - `tools/gen_klee_cards.py:3993 — the general rule the branch bypasses: plural = "random enemies" if times > 1 else "a random enemy"`
  - `klee-mod/KleeCode/Cards/Generated/RapidFire.cs:50 — sibling multi-hit random card reads "Deal {Damage:diff()} damage to random enemies four times."`
  - `klee-mod/KleeCode/Cards/Generated/PocketFireworks.cs:50 — "Deal {Damage:diff()} damage to random enemies twice."`
  - _Sim and C# agree with each other (per-hit reroll, confirmed by the round-trip mapping in tools/extract_base_game_pool.py:940-941 where TargetingRandomOpponents + WithHitCount(n) decodes to target random_enemy + times n). Only the displayed text disagrees with the ops. Player-visible in any multi-enemy fight (expected single-target burst, actually spread damage), hence medium rather than low._
- **[low] other** — Leg-3 in-repo documentation still describes Gleeful Barrage's hit count as reading the POST-spend spark bank (SparksAsResolved), which is the pre-R39 behavior; the shipped card reads the PRE-spend bank (SparksAtPlay). Comment drift only — the executable code matches the sheet/R39 ruling.
  - `klee-mod/KleeCode/KleeCardPool.cs:122-125 — "// Formula batch: 2+Sparks hit count (SparksAsResolved -- the // post-spend bank) ..." immediately above ModelDb.Card<GleefulBarrage>()`
  - `klee-mod/DECISIONS.md:1249-1256 — "2_plus_sparks reads the NEW SparkPower.SparksAsResolved -- the bank minus the pending spend ... a spark-freed Gleeful Barrage counts sparks the sim already spent"`
  - `klee-mod/KleeCode/Cards/Generated/GleefulBarrage.cs:70 — .WithHitCount(2 + SparkPower.SparksAtPlay(Owner.Creature))`
  - `klee-mod/KleeCode/Powers/SparkPower.cs:146-152 — "R39 NARROWED ITS SCOPE (2026-07-21): ... that card now deliberately reads the PRE-spend bank instead (SparksAtPlay)"`
  - `tier0/engine/effects.py:516-519 — times = 2 + state.sparks_at_play, "the bank as it was at play time, NOT the post-spend bank"`
  - `tier0/DECISIONS.md:739-757 — R39 ruling text`
  - _No player-visible effect; filed as cosmetic/comment drift per the severity rubric._

### klee:catalytic_conversion
- **[low] other** — The live XML doc comment on ReactionBonusSparkEnergyPower still declares Catalytic Conversion has NO upgrade path and is marked UNAPPLIABLE by the sim's upgrade engine, but R37 gave the card a real, sim-expressible upgrade that both the sim and the generated C# card implement. The comment also instructs future maintainers 'do not invent an upgrade game-side' while the sibling generated card in the same mod does exactly that.
  - `klee-mod/KleeCode/Powers/ReactionKitPowers.cs:26-29 -- "NO UPGRADE PATH: the sim's upgrade engine marks catalytic_conversion UNAPPLIABLE (CATALYTIC_BURST_PER_REACTION is a constant, upgrades.py), so its sheet upgrade was never measured. Same disposition as hot_hands -- awaiting user ruling; do not invent an upgrade game-side."`
  - `tier0/content/upgrades.py:57-59 -- "catalytic_conversion LEFT this set with R37 (2026-07-20): its upgrade is now {innate: true}, which IS sim-expressible"; tier0/content/upgrades.py:71 -- UNAPPLIABLE is now an empty frozenset`
  - `docs/klee-upgrades.yaml:63 -- catalytic_conversion: {innate: true}  # R37`
  - `klee-mod/KleeCode/Cards/Generated/CatalyticConversion.cs:62-65 -- OnUpgrade() { AddKeyword(CardKeyword.Innate); }`
  - `klee-mod/DECISIONS.md:807-812 (earlier log entry carrying the same stale claim) vs klee-mod/DECISIONS.md:992-1002 ("R37 executed (Catalytic Conversion upgrade = Innate) ... catalytic_conversion left UNAPPLIABLE")`
  - _Pure documentation drift: not player-visible. All behavioral legs agree -- sheet amount 1 / target self matches CatalyticConversion.cs:59 (1 stack on Owner.Creature); reactions.py:146-152 (bonus Sparks + CATALYTIC_BURST_PER_REACTION*bonus Burst, immediately after the flat +5) matches ReactionEffects.cs:174-188 (catalytic Sparks + CatalyticBurstPerReaction*catalytic Burst in the same single funnel); ReactionKitConstants.CatalyticBurstPerReaction = 5 (ReactionKitPowers.cs:15) matches the sim constant and the card text at CatalyticConversion.cs:40; upgrade innate matches upgrades.py:140-144 + combat.py:747-754. The DECISIONS.md:807 instance is arguably acceptable as a chronological log entry superseded at :992; the ReactionKitPowers.cs:26-29 instance is a live source-file doc comment and is the substance of this finding. The hot_hands cross-reference in the same comment is likewise stale (docs/klee-upgrades.yaml:57 {retain: true}, implemented at klee-mod/KleeCode/Cards/Generated/HotHands.cs:63-66)._

### klee:borrowed_brilliance
- **[low] other** — The design sheet declares `temp: true` on borrowed_brilliance's copy_companion_in_hand, but neither the tier0 sim nor the C# card implements any temporary/ethereal behaviour — the generated copy persists for the rest of the combat in both legs.
  - `docs/klee-cards.yaml:165 — `effects: [{op: copy_companion_in_hand, amount: 1, temp: true, cost_override: 0}]``
  - `tier0/engine/effects.py:1713-1722 — `_op_copy_companion_in_hand` reads only `amount` and `cost_override`; `temp` is never consulted, and `_add_token` (tier0/engine/effects.py:484-493) appends the copy to hand permanently`
  - `klee-mod/KleeCode/Cards/Generated/BorrowedBrilliance.cs:66-70 — `CreateCard(...)` + `EnergyCost.SetThisCombat(0)` + `CardPileCmd.AddGeneratedCardToCombat(copyToken, PileType.Hand, Owner)`; no Ethereal keyword, no end-of-turn removal`
  - `tools/gen_klee_cards.py:1165-1168 — validator comment: "`temp` accepted and IGNORED: tier0 _op_copy_companion_in_hand never reads it (the copy persists)"`
  - _Both implementation legs agree with each other, and the divergence from the sheet field is explicitly ratified at klee-mod/DECISIONS.md:1345-1348 ("`temp: true` accepted and IGNORED because tier0 ignores it (sim is LAW)"). Filed only as sheet-vs-implementation dead-field drift, not a behavioural mismatch between sim and C#; the C# description text also never promises a temporary copy, so nothing player-facing is wrong. Everything else on this card is clean: cost 1 / Skill / Uncommon / TargetType.Self match docs/klee-cards.yaml:164 vs BorrowedBrilliance.cs:52-53; random companion-in-hand pick and cost-0 override match tier0/engine/effects.py:1715-1721 vs BorrowedBrilliance.cs:60-68; the upgrade delta `add: {op: draw, amount: 1}` (docs/klee-upgrades.yaml:66, appended by tier0/content/upgrades.py:138-139) matches the IsUpgraded-gated `CardPileCmd.Draw(..., DynamicVars.Cards.BaseValue, ...)` at BorrowedBrilliance.cs:72-75 with CanonicalVars `new CardsVar(1)` at :41-45 and the "{IfUpgraded:show:Draw 1 card.|}" text at :40 (singular, correct); no keywords/tooltips are expected for this op set per tools/gen_klee_cards.py:4879-4899 and :4909-4918._

### klee:flame_dance
- **[low] other** — The FlameDance.cs class summary comment states the sheet's base damage as 7, but the design sheet and the card's own CanonicalVars both say 9. Non-player-visible comment drift only: every shipped number (9 base, +4 aura rider, +2 upgrade) matches the sheet.
  - `docs/klee-cards.yaml:169 — effects: [{op: damage, amount: 9, target: all_enemies, bonus_vs_aura: 4}]`
  - `klee-mod/KleeCode/Cards/FlameDance.cs:19 — "/// Sheet: uncommon attack, cost 2, 7 damage to ALL enemies, +4 vs enemies"`
  - `klee-mod/KleeCode/Cards/FlameDance.cs:52 — new DamageVar(9m, ValueProp.Move)`
  - _Everything else is clean. Sheet 9/all_enemies/bonus_vs_aura 4 == CanonicalVars DamageVar(9m)+ExtraDamageVar(4m) (FlameDance.cs:52-54); cost 2 / Attack / Uncommon / TargetType.AllEnemies (FlameDance.cs:58) matches the sheet row. Upgrade delta docs/klee-upgrades.yaml:68 {damage: +2} == OnUpgrade UpgradeValueBy(2m) with the rider untouched (FlameDance.cs:79-83), and the sheet-side pin tier0/tests/test_klee.py:103,114 agrees (11 / rider 4). Element: sheet header declares catalyst-grade (all attacks apply pyro), tier0 effects.py:277-279 auto-applies card element for attack damage ops under catalyst cadence, and FlameDance.cs:31,33-34 declares Element.Pyro + KleeKeywords.AppliesPyro. Targeting/timing: tier0 effects.py:594-599 reads enemy.aura per target BEFORE deal_damage_to_enemy consumes it; FlameDance.cs:62-67 reads AuraCmd.Find(target) in ModifyDamageAdditive, which runs pre-hit-resolution (same idiom documented at Powers/FontainePowers.cs:80) and returns 0 for other cards' damage — same per-target, non-consuming, live read. Description text at FlameDance.cs:45-46 matches the ops (AoE + per-enemy aura bonus); {ExtraDamage} correctly lacks :diff() because the rider never upgrades. R72's snapshot rule applies only to bonus_vs_bombed and explicitly leaves bonus_vs_aura live (DECISIONS.md:2362-2367), and flame_dance is single-hit-per-target so the multi-hit exposure it warns about does not apply. Blocked/hand-written status is declared in manifest.json:126 and is not itself a defect. Non-finding worth noting for the sweep owner: the AoE-aura correctness guard tier0/tests/test_roster_codegen.py:316-334 asserts on gen.emit(flame_dance) output ('foreach (var auraTarget'), not on the shipped hand-written FlameDance.cs, so it does not actually cover the artifact the game loads — but the shipped code IS per-target, so there is no behavioral disagreement to file._

### klee:sparks_n_splash
- **[low] other** — SparksNSplash.cs's own XML/inline comments assert the card is never in KleeCardPool.GenerateAllCards and 'deliberately NOT in KleeCardPool either', but the card IS a pool member: KleeOffPoolCards.All includes it and GenerateAllCards concatenates that list. The real invariant (never draftable/transformable) is enforced one layer up, in FilterThroughEpochs/GetUnlockedCards. Behavior is correct; the comments are stale and misdescribe the mechanism a future editor would rely on.
  - `klee-mod/KleeCode/Cards/SparksNSplash.cs:18-22 — "Hand-written: its lifecycle is machinery, not ops. NEVER in KleeCardPool.GenerateAllCards"`
  - `klee-mod/KleeCode/Cards/SparksNSplash.cs:60-62 — "autoAdd: false -- and deliberately NOT in KleeCardPool either (kit is never draftable)."`
  - `klee-mod/KleeCode/KleeOffPoolCards.cs:77 — ModelDb.Card<SparksNSplash>() inside KleeOffPoolCards.BuildAll()`
  - `klee-mod/KleeCode/KleeCardPool.cs:170-173 — GenerateAllCards returns pooled.Concat(RosterAncientCards.Klee).Concat(KleeOffPoolCards.All)`
  - `klee-mod/KleeCode/KleeCardPool.cs:43-48 — FilterThroughEpochs strips KleeOffPoolCards.Ids from GetUnlockedCards (the actual non-draftable gate)`
  - _Cosmetic/comment drift only, filed at low per the severity rubric. No player-visible effect: the sim's kit-exclusion invariant (tier0/engine/combat.py:303 kit_card -> no pile; tier0/tests/test_pass2.py:76 asserts sparks_n_splash in no pile) is still honored._

### klee:sparkly_explosion
- **[medium] text_ops_mismatch** — SparklyExplosion places Bombs and names "[gold]Bombs[/gold]" in its printed description, but ships with includesBombRules: false, so the Bomb rules hover tooltip is never attached — every other bomb-placing Klee card passes true. Root cause: the codegen's includes_bomb_rules scan only walks TOP-LEVEL effects, and this card's place_bomb lives inside the conditional's then-branch.
  - `docs/klee-cards.yaml:196 — effects: [{op: damage, amount: 18, target: enemy}, {op: conditional, if: killed_target, then: [{op: gain_spark, amount: 3}, {op: place_bomb, amount: 2, target: random_enemies, bomb_damage: 6}]}]`
  - `klee-mod/KleeCode/Cards/Generated/SparklyExplosion.cs:43 — KleeCardTooltips.ForCard(base.ExtraHoverTips, this, Element.Pyro, includesBombRules: false);`
  - `klee-mod/KleeCode/Cards/Generated/SparklyExplosion.cs:50 — description "... place 2 [gold]Bombs[/gold] on random enemies, each dealing 6 damage."`
  - `klee-mod/KleeCode/Cards/Generated/SparklyExplosion.cs:85 — await BombPower.Place(choiceContext, bombTarget, 6, Owner.Creature, this);`
  - `klee-mod/KleeCode/Cards/Generated/ClusterCharge.cs:43 — same-shaped Pyro attack that places 2 random bombs passes includesBombRules: true`
  - `klee-mod/KleeCode/Cards/KleeCardTooltips.cs:29-32 — the Bomb keyword tip is emitted only when includesBombRules is true`
  - `tools/gen_klee_cards.py:4723-4726 — includes_bomb_rules = any(e.get("op") in {...} for e in card.get("effects", [])) — no recursion into conditional then/else branches`
  - _Cross-check of the rest of the card is clean: damage 18 (yaml:196 vs .cs:56), upgrade +5 -> 23 (klee-upgrades.yaml:79 vs .cs:92), gain_spark 3 then place 2 bombs @6 in sheet order (.cs:79-87 vs effects.py:1510-1520), per-bomb reroll of the random target matches _op_place_bomb + _pick_targets(random_enemies) (effects.py:882-889, 259-260), no-living-enemy edge case matches (candidates.Count == 0 break vs _pick_targets returning []), gain_sparks is uncapped in the sim (effects.py:479-481) as in SparkPower.Gain, and the killed_target read via enemiesAtStart.Any(e => e.IsDead) is the same house idiom used for the other killed_target card (Showstopper.cs:61,69) matching state.kills_this_card > 0 (effects.py:405,1600-1601). Pyro application is the standard IElementalCard/AppliesPyro path required by the sheet header (klee-cards.yaml:2) and matches _element_for's catalyst branch (effects.py:274-281). The literal 6 for bomb damage (rather than an ExtraDamageVar) is an accepted codegen idiom for nested bombs with no bomb_damage delta — ChainedReactions.cs:71 does the same — so it is not filed._

### klee:true_spark_knight
- **[medium] text_ops_mismatch** — The Spark power's tooltip hardcodes the threshold as 3 in both clauses, so once True Spark Knight resolves the player sees "At 3 Sparks, your Attacks cost 0. Playing one consumes 3 Sparks" while the live threshold and the spend are both 2 — the displayed numbers disagree with what the ops actually do.
  - `docs/klee-cards.yaml:202 — {op: apply_power, power: spark_threshold_down, amount: 1, target: self, note: "free attack at 2 sparks instead of 3"}`
  - `tier0/engine/combat.py:24-27 — spark_threshold() returns max(1, SPARKS_FOR_FREE_ATTACK - spark_threshold_down), i.e. 2 with one stack; read at both the gate (combat.py:171-173) and the spend (combat.py:199-201)`
  - `klee-mod/KleeCode/Powers/SparkPower.cs:52-55 — CurrentThreshold = Math.Max(1, 3 - SparkThresholdDownPower.Amount), correctly 2`
  - `klee-mod/KleeCode/Powers/SparkPower.cs:61-62 — ("description", "At 3 [gold]Sparks[/gold], your Attacks cost 0. " + "Playing one consumes 3 [gold]Sparks[/gold].") — static literal 3, no DynamicVar, never reflects CurrentThreshold`
  - `klee-mod/KleeCode/Cards/Generated/TrueSparkKnight.cs:59 — PowerCmd.Apply<SparkThresholdDownPower>(..., 1, ...) is the only thing that makes the tooltip stale`
  - _Behavior is correct on both legs (gate and spend both read CurrentThreshold, matching the sim's two spark_threshold(state) call sites). The defect is purely the displayed number on the Spark power tooltip after this card is played. No acknowledgement of this staleness exists in klee-mod/DECISIONS.md:803-806, which only records the marker-power design. Severity kept at medium rather than high because no game number is computed wrongly — only shown wrongly._
- **[low] text_ops_mismatch** — The card face and the power tooltip it grants describe the same effect with different text: the card omits the "(minimum 1)" floor clause and the plural token that the power's own description carries.
  - `klee-mod/KleeCode/Cards/Generated/TrueSparkKnight.cs:40 — ("description", "You need 1 fewer [gold]Spark[/gold] for your Attacks to cost 0.")`
  - `klee-mod/KleeCode/Powers/SparkKitPowers.cs:88-91 — ("description", "You need {Amount} fewer [gold]Spark[/gold]{Amount:plural:|s} " + "for your Attacks to cost 0 (minimum 1).")`
  - `tools/gen_klee_cards.py:429-430 — codegen template "You need {X} fewer [gold]Spark[/gold] for your Attacks to cost 0." (card side is faithful to the registry; the power hand-adds the floor)`
  - _Cosmetic only. Neither string is false at the shipped amount of 1 (floor max(1, 3-1)=2 never binds, and singular "Spark" is correct), and the card's CanonicalVars being empty matches the convention for other generated power cards (EndlessFireworks.cs:41-46). Filed as low drift, not a functional defect._

### klee:vermillion_pact
- **[low] sim_vs_csharp_divergence** — The 4x amp-cap detector that this card's sheet note tells the reader to watch measures a different quantity in each leg: tier0 fires it on FINAL damage vs base after the whole pipeline (strength, amp, vulnerable, slow), while the C# fires it on the amplifier multiplier alone. The C# claims to own the sim's detector, but it is strictly narrower and cannot see amp-stack runaway produced by non-amp multipliers.
  - `docs/klee-cards.yaml:215 — sheet note on the apply_power row: "PERCENT: doubles the base Vaporize/Melt amplifier. Watch the 4x amp-cap detector."`
  - `tier0/constants.py:570 — AMP_STACK_LIMIT = 4.0  # single hit > 4x base damage -> log provenance`
  - `tier0/engine/effects.py:375 — `if base > 0 and dmg > base * C.AMP_STACK_LIMIT:` fires amp_stack_warning on the FINAL post-pipeline damage (after reactions.resolve_hit at :363, powers.modify_damage_taken at :367 incl. Vulnerable, and the slow multiplier at :372)`
  - `klee-mod/KleeCode/Elements/ReactionTable.cs:120 — `if (mult > ReactionConstants.AmpStackLimit)` where `mult` is only `baseMult * (1m + pct / 100m)` computed at :118 — no target mods, no strength, no slow`
  - `klee-mod/KleeCode/Elements/ReactionTable.cs:106-108 — doc comment asserts parity: "This overload also owns the sim's amp-cap detector (AMP_STACK_LIMIT)"`
  - `klee-mod/DECISIONS.md:816-818 — "it now owns the 4x amp-cap detector (moved from AuraPower; the boosted multiplier is the one that can run away)"`
  - `klee-mod/KleeCode/Powers/SimDamagePipeline.cs:1-53 — the C# damage pipeline contains no AmpStackLimit check at all, so there is no post-pipeline equivalent of effects.py:375`
  - `tier0/tests/test_klee.py:617-628 — the sim's detector is the acceptance gate for this exact card (`state.player.powers["amp_reaction_up"] = 125`; asserts no amp_stack_warning)`
  - _Concrete split: upgraded Vermillion Pact (125) into Melt = 3.9375x. Add Vulnerable on the target (VULNERABLE_TAKEN_MULT / VulnerableTakenMult = 1.5, tier0/constants.py and ReactionTable.cs:39) and the hit lands at ~5.9x base. tier0/engine/effects.py:375 emits amp_stack_warning; klee-mod/KleeCode/Elements/ReactionTable.cs:120 stays silent because 3.9375 < 4.0. Diagnostic/log only — no player-visible number changes — hence low. Everything else on this card is clean: sheet amount 100 (docs/klee-cards.yaml:215) == CanonicalVars PowerAmount 100m (VermillionPact.cs:46); upgrade {amp_percent: +25} (docs/klee-upgrades.yaml:86) == UpgradeValueBy(25m) (VermillionPact.cs:64), and amp_percent is a ratified power-amount key (docs/upgrade-conventions.md:20, tier0/content/upgrades.py:454, tools/gen_klee_cards.py:630); description string matches the codegen registry template character-for-character (tools/gen_klee_cards.py:431-432 vs VermillionPact.cs:40 and ReactionKitPowers.cs:57-61); formula parity base*(1+pct/100) (tier0/engine/reactions.py:36 vs ReactionTable.cs:118); both C# amp sites pass the dealer (AuraPower.cs:113, ElementalHit.cs:48) and in tier0 every resolve_hit caller is player-dealt, so the player-vs-dealer power lookup is not observably divergent; stacking is uncapped on both sides (registry cap None at gen_klee_cards.py:431, PowerStackType.Counter at ReactionKitPowers.cs:67, no max_stacks in the sheet row). The stale "vermillion_pact upgrades 25->30" line at docs/upgrade-conventions.md:33 is explicitly superseded by the correction block at :20 in the same file, so it is not filed as a defect._

### klee:playtime_forever
- **[low] other** — klee-mod/DECISIONS.md documents BombAndSparkPerTurnPower as having a stack cap of 1, but no cap exists in any of the three legs (the sheet declares no max_stacks, the sim stacks freely, and the mod has no stack-cap mechanism at all). The code is consistent with the sheet SSOT; the design-log line is stale.
  - `klee-mod/DECISIONS.md:794 — "`BombAndSparkPerTurnPower` (Playtime Forever, cap 1): turn-start bomb ..."`
  - `klee-mod/KleeCode/Powers/DemolitionPowers.cs:169-203 — class BombAndSparkPerTurnPower declares Type/StackType/AfterPlayerTurnStart only; no cap field or clamp (grep for MaxStacks/StackCap/MaxAmount across klee-mod/KleeCode returns nothing)`
  - `klee-mod/KleeCode/Cards/Generated/PlaytimeForever.cs:59 — PowerCmd.Apply<BombAndSparkPerTurnPower>(..., 1, ...) passes no cap argument`
  - `docs/klee-cards.yaml:217 — effects: [{op: apply_power, power: bomb_and_spark_per_turn, amount: 1, target: self}] with no max_stacks key (contrast _op_apply_power's cap read at tier0/engine/effects.py:803)`
  - `tier0/tests/test_pass2.py:29-32 — playing the card twice asserts st.player.powers["bomb_and_spark_per_turn"] == 2, i.e. the sim is explicitly uncapped`
  - _Comment/doc drift only, not player-visible. The same DECISIONS.md passage makes equally stale cap-4 claims for BombDamageUpPower and ZeroCostAttacksUpPower (contradicted by tier0/tests/test_pass2.py:22 and :27), so this is a character-wide doc issue surfaced while verifying this card, not a defect in the card's own three-leg parity. The cap idea originates as a proposal in docs/archive/pass1-rulings-round2.md:18 ("needs engine support"), which was never landed._

### klee:no_holding_back
- **[low] other** — Stale sim comment: tier0/engine/effects.py names No Holding Back as an example of the `target: self` HP-loss branch, but the card carries no self-damage effect on the design sheet any more (HP loss removed in the live-playtest patch), so the named example is documentation drift.
  - `tier0/engine/effects.py:502 — `if fx.get("target") == "self":            # Hot Hands / No Holding Back``
  - `docs/klee-cards.yaml:220-221 — card entry's only effect is `{op: damage, amount: 14, target: all_enemies}`; no `target: self` row`
  - `docs/klee-upgrades.yaml:89 — `no_holding_back:   {damage: +4}   # 14->18; the base HP loss was removed in the live-playtest patch``
  - `tier0/tests/test_pass2.py:47-49 — `no_holding = loader.get_card("no_holding_back")` / `assert not any(fx.get("target") == "self" for fx in no_holding.effects)``
  - _Comment-only; no behavioral divergence. The self-damage branch itself is still live and correct for Hot Hands. Player-visible behavior is unaffected._
- **[low] other** — Context, not a defect (recorded for the sweep): all three legs agree on substance — sheet 14 dmg to all_enemies at cost 1 rare attack, sim _op_damage with target all_enemies applying pyro under catalyst cadence, C# TargetType.AllEnemies + DamageVar(14m) + Element.Pyro + AppliesPyro keyword, and upgrade +4 matching UpgradeValueBy(4m).
  - `docs/klee-cards.yaml:220-221 vs klee-mod/KleeCode/Cards/Generated/NoHoldingBack.cs:56,63,69-71`
  - `docs/klee-upgrades.yaml:89 vs klee-mod/KleeCode/Cards/Generated/NoHoldingBack.cs:79`
  - `docs/klee-cards.yaml:2 (catalyst-grade: all attacks apply pyro, applies_element omitted = true) vs tier0/engine/effects.py:278-281 and klee-mod/KleeCode/Cards/Generated/NoHoldingBack.cs:37,40 with klee-mod/KleeCode/Powers/ElementalApplication.cs:196-201`
  - _No disagreement found. Included only so the parity evidence is on record alongside the single low-severity comment drift; do not treat as a defect._

**CLEAN (61):** duck_and_cover, jumpy_dumpty, pop, mine_toss, fish_flavored_bait, quick_fuse, double_pop, ammo_scavenging, big_badda_boom, blast_radius, careful_arrangement, bomb_voyage, sparkly_treasure, pocket_fireworks, crackle, spark_collection, tail_of_flame, eager_to_help, skip_and_hop, rapid_fire, warm_glow, snap, combustion_study, alchemical_curiosity, boom_goes_the_dynamite, study_of_explosions, friendly_visit, hide_and_seek, sorry_jean, spooked, clockwork_toy, run_away, patched_dress, jumpy_dumpty_mk2, remote_detonator, bombs_away, explosives_workshop, cluster_charge, trip_wire, spark_knight_style, endless_fireworks, flame_on_the_wick, hot_hands, cant_catch_me, sugar_rush, perfect_timing, elemental_ecstasy, study_buddy, spirited_away, dodge_roll, bright_idea, surprise_visit, blazing_delight, chained_reactions, explosive_frags, all_my_treasures, fish_blasting, da_da_da, grand_finale, secret_stash, best_friends_forever

## Furina — 82 cards, 30 with findings

### furina:aria_of_recompense
- **[medium] text_ops_mismatch** — The Fanfare-rider hover tip shown on Aria of Recompense reads "+1 damage per 4 Fanfare you hold" (and "+N damage, already counted in the number above"), but the card's only rider op grants Block and the card deals no damage at all. FurinaRiderTips.FanfareBody hardcodes the noun "damage" and has no grantsBlock flag, unlike its sibling SalonBody which takes one.
  - `docs/furina-cards.yaml:64 — effects list is `{op: block, amount: 0, bonus_formula: 1_per_4_fanfare}`; the card has no damage op (docs/furina-cards.yaml:62-64)`
  - `tier0/engine/effects.py:623-624 — the 1_per_4_fanfare rider is added to `raw` inside `_op_block`, i.e. it is Block, not damage`
  - `klee-mod/KleeCode/Cards/Furina/Generated/AriaOfRecompense.cs:40-41 — `FurinaRiderTips.ForCard(base.ExtraHoverTips, this, fanfarePer: 1, fanfareStep: 4)` wires the tip onto this card`
  - `klee-mod/KleeCode/Cards/FurinaRiderTips.cs:87 — `var rate = $"+{per} damage per {step} Fanfare you hold.";``
  - `klee-mod/KleeCode/Cards/FurinaRiderTips.cs:92-93 — `return $"{rate} You hold {fanfare} Fanfare: +{fanfare / step * per} " + "damage, already counted in the number above.";``
  - `klee-mod/KleeCode/Cards/FurinaRiderTips.cs:71 and :105 — the Salon rider body does take `salonGrantsBlock` and switches the noun (`var noun = grantsBlock ? "Block" : "damage";`), showing the Block/damage distinction is otherwise honored`
  - `klee-mod/KleeCode/Cards/Furina/Generated/AriaOfRecompense.cs:48 — the card face itself correctly says "Gain {CalculatedBlock:diff()} [gold]Block[/gold]", so the tip contradicts the face it is attached to`
  - _Shared-helper defect: the same wrong noun lands on every Fanfare-rider Block card (HeldBreath.cs:41, HeartsSwelling.cs:43, SufferingForArt.cs:41, ThunderousOvation.cs:41), but it is in scope here because Aria is a pure Block card. Everything else on this card is three-way clean: gain_encore 5 / block 0 +1-per-4-fanfare (docs/furina-cards.yaml:63-64) vs CanonicalVars base 0m / extra 1m / ReadableFanfare/4 and GainEncore(5) (AriaOfRecompense.cs:56-58, :70-71); upgrade {encore: +3, innate: true} (docs/furina-upgrades.yaml:42) vs `IsUpgraded ? 8 : 5` and `AddKeyword(CardKeyword.Innate)` (AriaOfRecompense.cs:70, :77); readable-clamp semantics match (tier0/engine/resources.py:238 vs FurinaResources.cs:569); one starting-deck copy in both (tier0/content/characters/furina.yaml:76 vs klee-mod/KleeCode/Furina.cs:62)._

### furina:salon_debut
- **[high] text_ops_mismatch** — Upgraded Salon Début prints a flat "Gain 2 Encore." but actually grants 4 Encore whenever the deploy bows a member out; every other salon-deploy card previews the replacement-doubled number on its face via a CalculatedVar, so this card alone under-reports what it does.
  - `klee-mod/KleeCode/Cards/Furina/Generated/SalonDebut.cs:51 — description is the literal "{IfUpgraded:show:Gain 2 [gold]Encore[/gold].|}" with no dynamic var`
  - `klee-mod/KleeCode/Cards/Furina/Generated/SalonDebut.cs:54-58 — CanonicalVars is empty, so no {Encore:diff()} can be rendered`
  - `klee-mod/KleeCode/Cards/Furina/Generated/SalonDebut.cs:73 — FurinaResources.GainEncore(Owner.Creature, 2 * (salonReplacements > 0 ? 2 : 1)) resolves to 4 after a replacement`
  - `docs/furina-upgrades.yaml:43 — salon_debut: {add: {op: gain_encore, amount: 2}}`
  - `tier0/engine/effects.py:1012-1013 — _op_gain_encore multiplies the amount by C.SALON_REPLACE_NUMERIC_MULT when state.salon_replacements_this_card is set (sim agrees with the C# resolution, not with the printed 2)`
  - `tier0/engine/effects.py:784 — the deploy that lands on a full stage sets state.salon_replacements_this_card`
  - `klee-mod/KleeCode/Cards/Furina/Generated/GrandGala.cs:51,59,72 — sibling pattern: face prints "Gain {Encore:diff()} Encore" backed by SalonMemberPower.ReplacementDelta(card, 4, SalonConstants.ReplacementNumericMultiplier)`
  - `klee-mod/KleeCode/Cards/Furina/Generated/SurintendanteChevalmarin.cs:51,59 — same {Encore:diff()} pattern on a 1-deploy card`
  - `klee-mod/KleeCode/Cards/Furina/Generated/OverflowingHospitality.cs:51,59 — same pattern`
  - `klee-mod/KleeCode/Powers/SalonPowers.cs:296-303 — ReplacementDelta exists precisely so "the same number these cards already resolved" is "now also the number they print"`
  - _Ops and sim agree (both double); it is the printed face that disagrees. Direction is under-promise (says 2, grants 4), but it is a starter card present in every run, and the replacement case is routine once the 3-slot stage fills. Root cause looks like the codegen path for an `add: {op: gain_encore}` upgrade delta emitting an IsUpgraded-gated literal instead of the CalculatedVar path used for base-effect riders; SalonDebut appears to be the only salon-deploy card whose scaled numeric arrives via an upgrade `add`._
- **[low] other** — SalonDebut hardcodes the replacement multiplier as a bare literal 2 instead of reading SalonConstants.ReplacementNumericMultiplier, so it sits outside the constant-parity gate that keeps the C# and tier0 salon constants in step.
  - `klee-mod/KleeCode/Cards/Furina/Generated/SalonDebut.cs:73 — 2 * (salonReplacements > 0 ? 2 : 1), literal multiplier`
  - `klee-mod/KleeCode/Powers/SalonPowers.cs:34 — public const int ReplacementNumericMultiplier = 2`
  - `tier0/constants.py:298 — SALON_REPLACE_NUMERIC_MULT = 2`
  - `klee-mod/KleeCode/Cards/Furina/Generated/GrandGala.cs:59 — sibling threads the named constant through ReplacementDelta`
  - _Values agree today (2 == 2 == 2), so there is no current behavioral divergence; filed low because the literal is the one salon numeric on this sheet that a repricing of the constant would silently leave behind._

### furina:suffering_for_art
- **[medium] text_ops_mismatch** — The Fanfare rider hover tip on Suffering for Art tells the player the rider is worth damage, but the sheet op the rider rides on is Block. FurinaRiderTips.FanfareBody hardcodes the noun "damage" and has no block variant, unlike its sibling SalonBody which takes a grantsBlock flag and switches the noun. On this card the tip renders "+1 damage per 4 Fanfare you hold. You hold N Fanfare: +N/4 damage, already counted in the number above." while the number above is Block and the card deals no damage to an enemy at all.
  - `docs/furina-cards.yaml:189 — {op: block, amount: 0, bonus_formula: 1_per_4_fanfare} (the rider is on Block; the only damage op is line 188 {op: damage, amount: 1, target: self})`
  - `klee-mod/KleeCode/Cards/Furina/Generated/SufferingForArt.cs:41 — FurinaRiderTips.ForCard(base.ExtraHoverTips, this, fanfarePer: 1, fanfareStep: 4)`
  - `klee-mod/KleeCode/Cards/FurinaRiderTips.cs:87 — var rate = $"+{per} damage per {step} Fanfare you hold."`
  - `klee-mod/KleeCode/Cards/FurinaRiderTips.cs:92-93 — $"{rate} You hold {fanfare} Fanfare: +{fanfare / step * per} " + "damage, already counted in the number above."`
  - `klee-mod/KleeCode/Cards/FurinaRiderTips.cs:104 — SalonBody's contrasting, correct treatment: var rate = $"+{per} {noun} per Salon member on stage." with noun = grantsBlock ? "Block" : "damage"`
  - `klee-mod/KleeCode/Cards/Furina/Generated/SufferingForArt.cs:57 — the rider feeds CalculatedBlockVar, confirming Block is the quantity being scaled`
  - _The ForCard signature (FurinaRiderTips.cs:41-47) has salonGrantsBlock but no fanfare equivalent, so this is structural: every base-0/base-N Furina card whose Fanfare rider grants Block hits it (AriaOfRecompense.cs:41, HeldBreath.cs:41, ThunderousOvation.cs:41, HeartsSwelling.cs:41). Reported here only for this card per the card's scope. Text-only; the arithmetic in SufferingForArt.cs:57 is correct._
- **[low] text_ops_mismatch** — The sheet explicitly directs that this card's face print the rate and NOT a zero ("The face reads 'Gain 1 Block per 4 Fanfare' -- no zero is printed"), but the C# description binds a {CalculatedBlock:diff()} token which renders the live computed value, i.e. literally "Gain 0 Block." out of combat and any time Fanfare is under 4 — the exact printed zero the sheet ruled against — with the rate rehomed to a hover tip instead.
  - `docs/furina-cards.yaml:198-202 — "BASE 0 IS INTENTIONAL AND IT IS THE PRICE... The face reads \"Gain 1 Block per 4 Fanfare\" -- no zero is printed."`
  - `klee-mod/KleeCode/Cards/Furina/Generated/SufferingForArt.cs:48 — ("description", "Lose {HpLoss} HP. Gain {IfUpgraded:show:4|3} [gold]Encore[/gold]. Gain {CalculatedBlock:diff()} [gold]Block[/gold]. Scales with [gold]Fanfare[/gold].")`
  - `klee-mod/KleeCode/Cards/Furina/Generated/SufferingForArt.cs:55-57 — CalculationBaseVar(0m) + CalculationExtraVar(1m) x ReadableFanfare/4, so the bound token evaluates to 0 below 4 Fanfare`
  - `docs/serenitea-sweep-log-2026-07-26.md:215 — "the face is a bound {Var:diff()} token" (the token renders the live number, it is not a rate string)`
  - _Partly explained by the Legibility sprint Track L-C rehoming documented at klee-mod/KleeCode/Cards/FurinaRiderTips.cs:9-21, which deliberately moves rate arithmetic off the face and into the hover tip — but that rehoming does not cover the printed zero the sheet line specifically forbids, and the tip it rehomes to is the one carrying the wrong noun (finding 1). Cosmetic; shared with the other base-0 rider cards (AriaOfRecompense.cs:48)._

### furina:ebb_and_flow
- **[medium] sim_vs_csharp_divergence** — The 1-Encore cost line is a hard, unmodifiable gate in tier0 but a discountable cost in C#: EncoreResource is the only custom-resource cost in the mod that does NOT override CanAfford to compare against the canonical value, and the spend reads the post-modifier GetAmountToSpend(). With a Leading Role / Prima Donna stack up (SpotlightDiscountPower), Ebb and Flow's Encore cost is reduced to 0, so the card becomes playable at 0 Encore and spends 0 Encore -- minting no encore_spent Fanfare and no burst -- while the sim still requires and drains a full 1.
  - `/home/user/GItS/tier0/engine/combat.py:117 -- `if card.encore_cost and state.player.encore < card.encore_cost: return False` gates on the RAW printed encore_cost; no cost-modifier path reaches it (card_cost() at :121-179 modifies energy only)`
  - `/home/user/GItS/tier0/engine/combat.py:207-208 -- `if card.encore_cost: resources.spend_encore(state, card.encore_cost)` spends the RAW printed value, which mints Fanfare/burst via resources.py:279-291`
  - `/home/user/GItS/klee-mod/KleeCode/Cards/Furina/Generated/EbbAndFlow.cs:58 -- `CustomResources<EncoreResource>.SetCanonicalCost(this, 1);``
  - `/home/user/GItS/klee-mod/KleeCode/Powers/FurinaResources.cs:111-128 -- EncoreResource overrides only ApplySharedModification and a no-op Spend; there is NO CanAfford override`
  - `/home/user/GItS/klee-mod/KleeCode/Powers/FurinaResources.cs:781-786 -- the actual spend reads `CustomResources<EncoreResource>.Cost(card)?.GetAmountToSpend() ?? 0` and calls SpendEncore(owner, cost), i.e. the post-modifier amount, not the canonical 1`
  - `/home/user/GItS/klee-mod/KleeCode/Powers/BurstResource.cs:107-121 -- the mod's own statement of the exposure and the fix: 'BaseLib's default CanAfford compares against the cost AFTER modifiers, and CustomResourceCost.GetWithModifiers pipes custom costs through Hook.ModifyEnergyCostInCombat... ApplySharedModification closes the SetToFree half of that exposure; this closes the hook half', followed by the CanAfford override`
  - `/home/user/GItS/klee-mod/KleeCode/Powers/FurinaResources.cs:245-251 -- FurinaBurstResource carries that same CanAfford override ('Gate on the CANONICAL 70, never a discounted number'); EncoreResource does not`
  - `/home/user/GItS/klee-mod/KleeCode/Powers/SpotlightSystem.cs:492-506 -- SpotlightDiscountPower.TryModifyEnergyCostInCombat(card, originalCost, out modifiedCost) filters on owner / IsSpotlighted / first-qualifying-play only; it has no resource-type filter, so it fires on the Encore cost object of any Spotlighted Furina card`
  - `/home/user/GItS/klee-mod/KleeCode/Cards/Furina/Generated/EbbAndFlow.cs:35-36 -- the card is an ICharacterCard with CharacterId "furina", so under Center Stage it IS Spotlighted and in range of that discount`
  - _EncoreResource's own doc comment (FurinaResources.cs:117-120) asserts the invariant this gap breaks: 'card_playable compares against the printed encore_cost, so a "free" effect must not waive it.' ApplySharedModification=false closes only the SetToFreeThisTurn/Combat half. Same exposure applies to the sheet's other encore_cost card, dress_rehearsal (DressRehearsal.cs:67). BaseLib itself is not vendored in this repo, so the pipe-through-the-hook mechanism is taken from the mod's own three concurring doc comments (BurstResource.cs:107-116, FurinaResources.cs:245-250, KokomiResources.cs:471-479) rather than from BaseLib source._
- **[low] other** — C# doc drift: the FanfareResource summary still lists 'Encore gained' as a Fanfare generation source, which Track A deleted in both engines. The executable code is correct (GainEncore mints nothing), so this is comment-only, but it is the exact claim a reader of Ebb and Flow's 'Gain 3 Encore' line would check.
  - `/home/user/GItS/klee-mod/KleeCode/Powers/FurinaResources.cs:134-135 -- 'Generation is activity-based only -- HP lost, Encore gained, Encore spent, a Center Stage card played.'`
  - `/home/user/GItS/docs/furina-cards.yaml:24-25 -- 'The four sources are hp_lost, encore_spent, encore_absorbed (NEW...) and center_stage. `encore_gained` is DELETED in both engines'`
  - `/home/user/GItS/tier0/engine/resources.py:265-276 -- gain_encore docstring 'Prints NO Fanfare (Track A, RULED 2026-07-28)' and the body emits only gain_encore`
  - `/home/user/GItS/klee-mod/KleeCode/Powers/FurinaResources.cs:572-582 -- GainEncore mints no Fanfare, matching the sim`
  - _Cosmetic only; no player-visible effect._
- **[low] other** — Sheet comment drift on the card's own row: 'rings the flux bell BOTH ways' describes the pre-Track-A world where gaining Encore also minted Fanfare. Post-Track-A only the Spend 1 rings, so the row's justification contradicts the file's own header.
  - `/home/user/GItS/docs/furina-cards.yaml:241 -- '# Spend 1, gain 3: net buffer growth that rings the flux bell BOTH ways. The Fanfare engine's idle animation.'`
  - `/home/user/GItS/docs/furina-cards.yaml:24-25 -- 'Fanfare prints when Encore goes DOWN, never when it goes up... `encore_gained` is DELETED in both engines'`
  - `/home/user/GItS/tier0/engine/resources.py:265-276 -- gain_encore prints no Fanfare`
  - _Related stale arithmetic lives in the archived G-D4 ruling (docs/archive/playtest-2026-07-25-coop-a0.md:63-66, 'mints 4 Fanfare -- 1 for the Encore spent, 3 for the Encore gained'); today the play mints 1. Archive doc, recorded as context only. Numbers, upgrade delta and card text are all in three-way agreement: sheet gain_encore 3 / draw 1 / encore_cost 1 (docs/furina-cards.yaml:239-240) vs upgrades {encore: +1} (docs/furina-upgrades.yaml:69) vs C# (IsUpgraded ? 4 : 3), CardsVar(1), SetCanonicalCost 1 (EbbAndFlow.cs:44-63)._

### furina:held_breath
- **[medium] text_ops_mismatch** — The Fanfare rider hover tip on this pure-Block card tells the player it grants DAMAGE. The sheet's only effect is {op: block, amount: 4, bonus_formula: 1_per_4_fanfare} and the C# card only calls CreatureCmd.GainBlock, but FurinaRiderTips.FanfareBody hardcodes the noun "damage" with no Block variant, so the tooltip reads "+1 damage per 4 Fanfare you hold. You hold N Fanfare: +N/4 damage, already counted in the number above."
  - `docs/furina-cards.yaml:274 — effects: [{op: block, amount: 4, bonus_formula: 1_per_4_fanfare}] (no damage op on this card)`
  - `klee-mod/KleeCode/Cards/Furina/Generated/HeldBreath.cs:68 — await CreatureCmd.GainBlock(Owner.Creature, DynamicVars.CalculatedBlock.Calculate(...)) — Block only`
  - `klee-mod/KleeCode/Cards/Furina/Generated/HeldBreath.cs:41 — FurinaRiderTips.ForCard(base.ExtraHoverTips, this, fanfarePer: 1, fanfareStep: 4) — no block-noun flag exists to pass`
  - `klee-mod/KleeCode/Cards/FurinaRiderTips.cs:87 — var rate = $"+{per} damage per {step} Fanfare you hold."`
  - `klee-mod/KleeCode/Cards/FurinaRiderTips.cs:92-93 — $"{rate} You hold {fanfare} Fanfare: +{fanfare / step * per} " + "damage, already counted in the number above."`
  - `klee-mod/KleeCode/Cards/FurinaRiderTips.cs:103-104 — SalonBody's contrast: var noun = grantsBlock ? "Block" : "damage"; the Salon rider has the noun switch the Fanfare rider lacks`
  - _Numbers are correct (+1 per 4 readable Fanfare); only the noun is wrong, so severity is misleading-text rather than wrong-number. Systemic to every Fanfare-rider Block card (thunderous_ovation, aria_of_recompense, hearts_swelling, suffering_for_art use the same helper), but it is player-visible on this card's face. The card body itself is clean: base 4 (HeldBreath.cs:54) vs sheet 4 (furina-cards.yaml:274); rate 1 per 4 via CalculationExtraVar(1m) + ReadableFanfare/4 (HeldBreath.cs:55-56) vs _bonus_formula's int(n) * (resources.readable(player) // int(m)) (effects.py:90-97) with identical zero-clamp semantics (resources.py:225-238 vs FurinaResources.cs:569); upgrade +3 (furina-upgrades.yaml:75) vs UpgradeValueBy(3m) on the base only (HeldBreath.cs:73), 4->7 with the rate untouched, matching the stated reader-card grammar; cost/type/rarity 1/skill/common match (HeldBreath.cs:62); Spotlight is correctly absent from the C# vars because tier0's _spotlight_scale resolves to 1.0 for a non-Companion Furina card in both Center Stage and Guest Cast (effects.py:307-318, 333-334)._

### furina:an_invitation
- **[medium] sim_vs_csharp_divergence** — The upgraded cost override has a different lifetime in the two engines: tier0 makes the generated Guest Star cost 0 for the whole combat (permanent mutation of the token's cost), while the C# scopes it to the current turn only (EnergyCost.SetThisTurn). Every other cost_override implementation in the mod uses SetThisCombat, so GuestStarGenerator is the odd one out; the sheet's own upgrade grammar says 'costs 0 this turn'.
  - `tier0/engine/effects.py:1205`
  - `tier0/engine/effects.py:1206`
  - `tier0/content/upgrades.py:434`
  - `tier0/content/upgrades.py:441`
  - `klee-mod/KleeCode/Powers/GuestStarGenerator.cs:48`
  - `klee-mod/KleeCode/Powers/GuestStarGenerator.cs:50`
  - `klee-mod/KleeCode/Cards/Furina/Generated/AnInvitation.cs:65`
  - `docs/fontaine-companions.yaml:182`
  - `docs/furina-upgrades.yaml:79`
  - `klee-mod/KleeCode/Cards/Generated/SecretStash.cs:81`
  - `klee-mod/KleeCode/Cards/Generated/BorrowedBrilliance.cs:69`
  - _Manifests whenever the generated guest is not played the turn it arrives: tier0 tokens persist (effects.py:484-488 puts them in hand/discard, nothing restores cost), so a guest redrawn on a later turn is still free in sim but back to printed cost (1-2 Energy) in C#. effects.py:1205's own inline comment reads 'upgraded form: 0 this turn' while the code it annotates is combat-permanent, and tier0/content/upgrades.py:434-435 calls it 'costs 0 this combat' - the sim leg is internally inconsistent about which it means._
- **[low] text_ops_mismatch** — The upgraded description uses a plural pronoun for a single generated card: the ops generate exactly one card (amount: 1) but the text reads 'They cost 0 this turn.'
  - `docs/furina-cards.yaml:298`
  - `klee-mod/KleeCode/Cards/Furina/Generated/AnInvitation.cs:47`
  - `klee-mod/KleeCode/Cards/Furina/Generated/CommandPerformance.cs:47`
  - _The same shared string is correct on the amount:2 generator (CommandPerformance.cs:47, sheet docs/furina-cards.yaml:801), so the template was written for the plural case and reused verbatim on the singular one. Cosmetic only; the first sentence correctly says 'Add 1 ... card'._

### furina:shared_billing
- **[medium] other** — shared_billing is a COMMON that upgrades its cost 1->0, which the delta-grammar authority explicitly forbids for the common tier; it is the only common on either Furina or Klee sheet with a cost reduction, and its own comment cites the 'mined cost line' that excludes commons.
  - `docs/furina-cards.yaml:311 (rarity: common)`
  - `docs/furina-upgrades.yaml:81 (shared_billing: {cost: -1}  # 1->0 ... mined cost line)`
  - `docs/upgrade-conventions.md:8 ("92 cost upgrades: 52 rare, 32 uncommon, 2 common. ... Rule: commons never upgrade cost; it's the rare-tier 'your payoff gets cheaper' move.")`
  - `docs/upgrade-conventions.md:28 ("Commons: exactly one number bump per grammar row 1/2. Zero common cost reductions.")`
  - `docs/furina-upgrades.yaml:110 / docs/furina-cards.yaml:423 (full_ensemble cost -1, uncommon)`
  - `docs/furina-upgrades.yaml:126,130,132 / docs/furina-cards.yaml:506,525,539 (leading_role, top_billing, standing_ovation cost -1, all uncommon)`
  - `docs/furina-upgrades.yaml:144,146,152 / docs/furina-cards.yaml:680,706,755 (unheard_confession, endless_waltz, prima_donna cost -1, all rare)`
  - `klee-mod/KleeCode/Cards/Furina/Generated/SharedBilling.cs:62 (base(1, CardType.Skill, CardRarity.Common, ...))`
  - `klee-mod/KleeCode/Cards/Furina/Generated/SharedBilling.cs:87 (EnergyCost.UpgradeBy(-1))`
  - _Not upgrade_delta_drift: the upgrades sheet and the C# agree exactly (1 -> 0, EnergyCost.UpgradeBy(-1)). The disagreement is between the delta and the stated delta-grammar authority for the card's rarity tier. Filed as 'other' because the sheet's own rationale invokes the mined cost line, which is the very rule that reserves cost reduction for uncommon/rare. Player-visible outcome (a free common that seeds Hydro, grants +25% Spotlight and refunds Energy), hence medium rather than low._
- **[low] sim_vs_csharp_divergence** — No divergence found on any op; recorded here only as the verified-clean baseline for the three ops. apply_aura/apply_power/energy semantics match one-for-one between tier0 and the C#.
  - `docs/furina-cards.yaml:312 (effects: apply_aura hydro random_enemy; apply_power spotlight_mult_bonus_turn 25 self; energy 1)`
  - `tier0/engine/effects.py:874-880 (_op_apply_aura -> reactions.resolve_hit(state, enemy, element, 0)) vs klee-mod/KleeCode/Cards/Furina/Generated/SharedBilling.cs:83 (ElementalHit.ApplyOnly)`
  - `tier0/engine/effects.py:259 (random_enemy -> state.rng.choice(living)) vs klee-mod/KleeCode/Cards/Furina/Generated/SharedBilling.cs:77-80 (HittableEnemies + Rng.CombatTargets.NextItem, empty-list guarded, identical to the sibling at klee-mod/KleeCode/Cards/Furina/Generated/OverflowingHospitality.cs:77-80)`
  - `tier0/engine/powers.py:23 (spotlight_mult_bonus_turn in EXPIRING) vs klee-mod/KleeCode/Powers/SpotlightSystem.cs:546-551 (AfterSideTurnEnd removes on player turn end)`
  - `tier0/engine/effects.py:693-698 (_op_energy) vs klee-mod/KleeCode/Cards/Furina/Generated/SharedBilling.cs:86 (PlayerCmd.GainEnergy(1, Owner))`
  - _Reported as a low-severity informational row, not a defect: aura apply/refresh/consume-and-react branching matches (tier0/engine/reactions.py resolve_hit vs ElementalHit.ApplyOnly), op ORDER matches the sheet, the salon-replacement multiplier at tier0/engine/effects.py:876 cannot fire on this card (no salon_member op; counter reset per card at effects.py:2237), the SKILL-grade cadence header rule at docs/furina-cards.yaml:14 is inert here (no damage op), keywords/description/tooltips at SharedBilling.cs:37-52 match the ops with correct numbers and target wording, and the card is in the generated manifest (manifest.json:69) and roster (FurinaCardRoster.cs:73). If the parent wants only true disagreements, drop this row and treat the card as otherwise clean._

### furina:blocking_notes
- **[high] upgrade_delta_drift** — The ruled upgrade delta `bonus_slope: +1` (slope +2 -> +3 Block per Companion played this turn) is not implemented in C#: BlockingNotes.OnUpgrade is empty, so the upgraded card still pays +2 per Companion while tier0 pays +3. Upgraded Blocking Notes with 3 Companions played: sim 5 + 3*3 = 14 Block, C# 5 + 2*3 = 11 Block.
  - `docs/furina-upgrades.yaml:83 — `blocking_notes:        {bonus_slope: +1}` with comment (83-88) 'the upgrade buys the SLOPE, +2 -> +3 Block per Companion played, exactly as the ruling worded it. Base 5 unchanged'`
  - `docs/furina-cards.yaml:319 — `effects: [{op: block, amount: 5, bonus_formula: 2_per_companion_played_this_turn}]``
  - `tier0/content/upgrades.py:505-516 — `elif key in ("bonus_per_detonation", "bonus_slope"): ... hit["bonus_formula"] = f"{int(n) + val}_per_{rest}"` (the sim really does steepen 2_per_ -> 3_per_)`
  - `klee-mod/KleeCode/Cards/Furina/Generated/BlockingNotes.cs:71-74 — `protected override void OnUpgrade() { // R24: NO upgrade path -- None. Flagged in manifest. }``
  - `klee-mod/KleeCode/Cards/Furina/Generated/BlockingNotes.cs:55 — the slope lives in `new CalculationExtraVar(2m)` and is never upgraded`
  - _Not an exclusion: furina-upgrades.yaml:3-4 excludes only bursts/kit and Guest Stars, and blocking_notes is a common Skill listed in manifest 'generated' (klee-mod/KleeCode/Cards/Furina/Generated/manifest.json:19), not 'blocked'. Root cause is visible in the generator: `bonus_slope` is declared expressible (tools/gen_klee_cards.py:724) and detected (tools/gen_klee_cards.py:2236-2238), but the OnUpgrade emitter has a branch only for the OLD key name — tools/gen_klee_cards.py:4597-4599 `if "bonus_per_detonation" in deltas: ... DynamicVars["BonusPer"].UpgradeValueBy(...)` — and no branch for `bonus_slope`/CalculationExtra. Precedent for the emitted form: klee-mod/KleeCode/Cards/Generated/GrandFinale.cs:78-81._
- **[medium] other** — BlockingNotes.cs asserts its missing upgrade path is 'Flagged in manifest', but the Furina manifest's no_upgrade_path is empty, so the coverage lint that reads exactly that dict cannot see the gap — the dropped upgrade ships silently and green.
  - `klee-mod/KleeCode/Cards/Furina/Generated/BlockingNotes.cs:73 — `// R24: NO upgrade path -- None. Flagged in manifest.``
  - `klee-mod/KleeCode/Cards/Furina/Generated/manifest.json:112 — `"no_upgrade_path": {}` (under `"upgrades"`, whose _comment says 'A generated card listed below ships without an upgrade until its full delta is expressible')`
  - `tools/lint_upgrade_coverage.py:134-140 — `gaps = blocked.get("upgrades", {}).get("no_upgrade_path", {})` is the only source of the [L2] 'ships with NO upgrade path' finding`
  - `tools/lint_upgrade_coverage.py:88 — `CODEGEN_DEBT: dict[str, str] = {}` (no curated exemption covering blocking_notes either)`
  - _Contrast the three Guest Star cards that carry the same R24 comment for a genuine reason ('no ratified delta', e.g. klee-mod/KleeCode/Cards/Furina/Generated/GuestNeuvilletteTears.cs:92) — those are excluded by docs/furina-upgrades.yaml:3-4. blocking_notes HAS a ratified delta._
- **[medium] sim_vs_csharp_divergence** — Companion-play counting disagrees on replayed Companions: tier0 increments companion_plays_this_turn ONCE per card play (outside the replay loop), while the C# hook fires per play index in a series and deliberately does not test IsFirstInSeries, so a Duet-replayed Companion counts twice. Duet + one Companion + Blocking Notes: sim 5 + 2*1 = 7 Block, C# 5 + 2*2 = 9 Block.
  - `tier0/engine/combat.py:268-270 — `if card.is_companion: state.companions_played.append(card.id); state.companion_plays_this_turn += 1`, with the adjacent comment (271-275) stating this site 'Fires once per CARD PLAY ... not once per replay inside the loop below'`
  - `tier0/engine/combat.py:284-291 — `# ... Before/AfterCardPlayed fire per play index` then `for _ in range(replays): ... resolve_card ... after_card_played(...)`, i.e. the increment is above the replay loop`
  - `klee-mod/KleeCode/Powers/CurtainCallPowers.cs:203-209 — `// IsFirstInSeries is NOT tested, deliberately ... a Study Buddy'd Companion really is two Companion cards hitting the table` then `if (cardPlay.Card is ICompanionCard) { CompanionPlays[owner] = Get(CompanionPlays, owner) + 1; }``
  - `klee-mod/KleeCode/Powers/FurinaResources.cs:791+/811 — NoteCardPlayed is invoked from `public override async Task AfterCardPlayed(...)`, the per-play-index hook`
  - `klee-mod/KleeCode/Powers/CompanionPowers.cs:159-176 — ReplayNextCompanionPower.ModifyCardPlayCount ('the extra plays are a series on one CardPlay') and its own AfterCardPlayed guarding on `IsLastInSeries`, proving AfterCardPlayed fires once per series member`
  - `docs/furina-cards.yaml:536-537 — `duet ... effects: [{op: replay_next_companion, times: 1, duration: this_turn}, ...]` (the reachable in-archetype replay source)`
  - `klee-mod/KleeCode/Powers/CurtainCallPowers.cs:93-98 — the doc comment claims this counter 'Mirrors the sim's state.companion_plays_this_turn'`
  - _Sheet is silent on replays, so this is a sim-vs-C# disagreement rather than a sheet violation; both legs agree Guest Star token plays DO count (docs/furina-cards.yaml:325-329, effects.py:77-88 via Card.is_companion, CurtainCallPowers.cs:206 via ICompanionCard). Second, unobservable-today direction of the same op: the sim increments BEFORE resolve_card (so a Companion that itself granted Block would count itself — effects.py:82-87 records this as a deliberate off-by-one), whereas the C# increments in AfterCardPlayed, after resolution. No Companion grants Block today, so nothing player-visible turns on it. Checked and CLEAN: base 5 / slope 2 (docs/furina-cards.yaml:319 vs BlockingNotes.cs:54-56), cost 1 / Skill / Common / Self (BlockingNotes.cs:61-63), turn reset (combat.py:432 vs CurtainCallPowers.cs:70-78), Spotlight never scales this card in either leg (effects.py:315-343 vs SpotlightSystem.cs:214-221/292-297 — both gate the outward multiplier on Companion cards, and Blocking Notes is ICharacterCard 'furina'), and the 'Scales with Companions' face text plus the rate-bearing hover tip (BlockingNotes.cs:47, FurinaRiderTips.cs:129-150) follow the same convention as DinnerService.cs:48._

### furina:swelling_overture
- **[low] text_ops_mismatch** — The card face renders the Encore keyword unhighlighted ("If you have at least 8 Encore") while every other Encore reference in the Furina pool -- and the sibling resource-threshold predicates in the very same codegen function -- render it as a [gold] keyword. Mechanics are correct; only the keyword styling is inconsistent, so this one card presents Encore as plain body text.
  - `klee-mod/KleeCode/Cards/Furina/Generated/SwellingOverture.cs:44 -- ("description", "Draw {Cards:diff()} card{Cards:plural:|s}. If you have at least 8 Encore: draw {DrawThen:diff()} card{DrawThen:plural:|s}.") -- no [gold] around Encore`
  - `tools/gen_klee_cards.py:378 -- return f"If you have at least {hit.group(1)} Encore" (the _ENCORE_BAR branch of predicate_text, the source of the string above)`
  - `tools/gen_klee_cards.py:368 -- return f"If you have at least {hit.group(1)} [gold]Fanfare[/gold]" (the _FANFARE_BAR branch, same function, golds its resource)`
  - `tools/gen_klee_cards.py:371 -- return f"If you have at least {hit.group(1)} [gold]Charge[/gold]" (the _CHARGE_BAR branch, same function, golds its resource)`
  - `klee-mod/KleeCode/Cards/Furina/Generated/MacaronBreak.cs:44 -- "Gain {IfUpgraded:show:3|2} [gold]Encore[/gold]. ..." (pool convention)`
  - `klee-mod/KleeCode/Cards/Furina/Generated/EbbAndFlow.cs:44 -- "Spend 1 [gold]Encore[/gold]. Gain {IfUpgraded:show:4|3} [gold]Encore[/gold]. ..." (pool convention)`
  - `docs/furina-cards.yaml:375 -- effects: [{op: draw, amount: 2}, {op: conditional, if: encore_at_least_8, then: [{op: draw, amount: 1}]}] (the predicate whose text this is)`
  - _Cosmetic only, and partially mitigated: docs/card_keywords.json:24 still marks the encore tooltip as "(Reserved -- future companion mechanic; do not ship a tooltip yet.)", so an un-golded Encore may be intentional at the staging-doc level -- but ~25 shipped Furina card faces gold it anyway, and this is the pool's only encore_at_least card, so the divergence shows on exactly one face. Reported at low per the cosmetic-drift rule; no mechanical impact._

### furina:grand_salon
- **[low] other** — C# doc comment on FanfareCapBonusResource still describes RaiseFanfareCap as retired grammar with no sheet user, while grand_salon (and ~15 other Furina cards) print the raise_fanfare_cap op; the same file contradicts itself 100 lines earlier.
  - `docs/furina-cards.yaml:431 — grand_salon effects: {op: raise_fanfare_cap, amount: 5}`
  - `docs/furina-cards.yaml:28-29 — Track B keyword "Fanfare Cap +X" op: raise_fanfare_cap, printed on commons/uncommons`
  - `klee-mod/KleeCode/Powers/FurinaResources.cs:191-192 — "Mirroring that shape means FurinaResources.RaiseFanfareCap (retired grammar, no sheet user) stays expressible without a rewrite."`
  - `klee-mod/KleeCode/Powers/FurinaResources.cs:84 — "(FurinaResources.RaiseFanfareCap, un-retired for the job)"`
  - `klee-mod/KleeCode/Cards/Furina/Generated/GrandSalon.cs:64 — FurinaResources.RaiseFanfareCap(Owner.Creature, DynamicVars["FanfareCap"].IntValue)`
  - _Comment-only drift; behaviour is correct and matches resources.raise_fanfare_cap (headroom only, inert without the resource). No player-visible effect._
- **[low] other** — The grand_salon upgrade-sheet comment asserts "cap 6 unchanged" for the salon_damage_up stack, but both the design sheet and the C# power document that six-point (two-stack) cap as DROPPED by the 2026-07-24 uncap-all ruling.
  - `docs/furina-upgrades.yaml:111 — "grand_salon: {power_amount: +1}    # A10 (2026-07-28): +1->+2, cap 6 unchanged"`
  - `docs/furina-cards.yaml:437 — "CAP DROPPED (user ruling 2026-07-24, uncap-all): +3/copy is a flat additive to member ticks, linear in copies."`
  - `klee-mod/KleeCode/Powers/SalonPowers.cs:486-488 — "The six-point (two-stack) cap was dropped 2026-07-24 (uncap-all ruling)"`
  - `tier0/engine/effects.py:849-850 — powers.apply_power(..., max_stacks=cap) with cap=fx.get("max_stacks"), absent on grand_salon, i.e. uncapped`
  - `klee-mod/KleeCode/Cards/Furina/Generated/GrandSalon.cs:69 — DynamicVars["PowerAmount"].UpgradeValueBy(1m)`
  - _The delta VALUE agrees on all three legs (1 -> 2, Fanfare Cap 5 unchanged); only the trailing comment's cap claim is stale. Mechanics verified aligned: sim _salon_amount (effects.py:705,713) and C# Scaled (SalonPowers.cs:169-172) both add salon_damage_up to every member numeric including Usher's Block tick and all bows._

### furina:crashing_waves
- **[medium] text_ops_mismatch** — The +5 aura rider is added inline at resolve time instead of rendering into the card's number, so the card face and the enemy damage preview show only the base 8 (10 upgraded) while the hit that lands against an aura'd enemy is 13 (15 upgraded). Both the Klee parity twin and the Furina sibling with the same sheet rider render it; this card does neither and also ships no aura hover tip.
  - `docs/furina-cards.yaml:450 — effects: [{op: damage, amount: 8, target: all_enemies, bonus_vs_aura: 5}]`
  - `tier0/engine/effects.py:598-599 — `if fx.get("bonus_vs_aura") and enemy.aura: hit += fx["bonus_vs_aura"]` (per-target, resolved into the hit)`
  - `klee-mod/KleeCode/Cards/Furina/Generated/CrashingWaves.cs:49 — `new DamageVar(8m, ValueProp.Move)` is the only var, so `{Damage:diff()}` always renders 8/10`
  - `klee-mod/KleeCode/Cards/Furina/Generated/CrashingWaves.cs:64 — `DamageCmd.Attack(SpotlightSystem.PrintedDamage(this, DynamicVars.Damage.BaseValue + (AuraCmd.Find(auraTarget) != null ? 5 : 0)))` adds the rider only inside OnPlay`
  - `klee-mod/KleeCode/Cards/Furina/Generated/TorrentialTurn.cs:56 — sibling bonus_vs_aura card renders its rider via `new CalculatedDamageVar(...).WithMultiplier(... AuraCmd.Find(target) != null ? 1 : 0)``
  - `klee-mod/KleeCode/Cards/Furina/Generated/TorrentialTurn.cs:41 — sibling also ships `FurinaRiderTips.ForCard(base.ExtraHoverTips, this, auraBonus: 3)`; CrashingWaves.cs has no ExtraHoverTips override at all`
  - `klee-mod/KleeCode/Cards/FlameDance.cs:62-66 — Klee parity twin routes the identical rider through `ModifyDamageAdditive` so, per its own doc comment at FlameDance.cs:22-26, "each enemy's hit (and its damage preview) picks up the bonus"`
  - _Resolved damage is correct (inline addition and the additive hook both land ahead of Strength/Vulnerable). The defect is display-only: the printed/previewed number understates the actual hit by 5 on every aura'd target. The description text does disclose the +5, which is why this is medium rather than high._
- **[low] text_ops_mismatch** — The description phrases a per-target rider on an AoE attack in the singular ("if the enemy has an elemental aura"), which reads as a single all-or-nothing condition, whereas the op checks each enemy independently and bonuses only the aura'd ones.
  - `docs/furina-cards.yaml:450 — target: all_enemies with bonus_vs_aura: 5`
  - `tier0/engine/effects.py:596-599 — the rider is inside `for enemy in _pick_targets(...)`, evaluated per enemy`
  - `klee-mod/KleeCode/Cards/Furina/Generated/CrashingWaves.cs:44 — "Deal {Damage:diff()} damage to ALL enemies. +5 damage if the enemy has an elemental aura."`
  - `klee-mod/KleeCode/Cards/FlameDance.cs:43-45 — the parity twin with the same all_enemies + per-target rider words it plurally: "Deal {Damage:diff()} damage to ALL enemies. Enemies with an aura take {ExtraDamage} more."`
  - _C# behavior (CrashingWaves.cs:62-64) is per-target and matches the sheet; only the wording is misleading._
- **[low] sim_vs_csharp_divergence** — Spotlight multiplier ordering differs: tier0 multiplies the printed base and adds the aura rider afterwards (rider explicitly excluded from the multiplier), while the C# folds the rider inside PrintedDamage so it would be multiplied too.
  - `tier0/engine/effects.py:530-532 — `base = _spotlight_scale(state, card, base)` with the comment "Spotlight scales the card's own printed damage -- ... and before per-target riders (v1 boring baseline; riders logged as design room)"`
  - `tier0/engine/effects.py:598-599 — the aura rider is added after that scaling`
  - `klee-mod/KleeCode/Cards/Furina/Generated/CrashingWaves.cs:64 — `SpotlightSystem.PrintedDamage(this, DynamicVars.Damage.BaseValue + (aura ? 5 : 0))` passes base+rider into the multiplier`
  - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:232-245 — OutwardMultiplier returns 1m unless the card `is ICompanionCard``
  - `klee-mod/KleeCode/Cards/Furina/Generated/CrashingWaves.cs:34 — the class implements ICharacterCard, not ICompanionCard`
  - _Currently unreachable/masked: OutwardMultiplier and PrintedDamage's flat-bonus branch are both gated on ICompanionCard, and tier0's is_outward_spotlighted (effects.py:315-318) likewise excludes the character's own cards, so both legs evaluate to identity today. Filed low because no number differs at present; the structural ordering rule the sim states is nevertheless not the one the C# encodes._

### furina:overflowing_hospitality
- **[medium] text_ops_mismatch** — On a full Salon the card applies Hydro TWICE (two independently rolled random enemies), but nothing on the card face or in any tooltip says so — the description prints a fixed, singular "Apply Hydro to a random enemy." with no dynamic var, while the sibling Encore number on the same card does surface its doubling via {Encore:diff()}.
  - `klee-mod/KleeCode/Cards/Furina/Generated/OverflowingHospitality.cs:51 — description: "Add 1 [gold]Surintendante Chevalmarin[/gold] to your [gold]Salon[/gold]. Apply [gold]Hydro[/gold] to a random enemy. Gain {Encore:diff()} [gold]Encore[/gold]." (aura clause is static and singular)`
  - `klee-mod/KleeCode/Cards/Furina/Generated/OverflowingHospitality.cs:74 — `for (var salonRepeat = 0; salonRepeat < (salonReplacements > 0 ? 2 : 1); salonRepeat++)` wraps the aura block at lines 76-86, so the ApplyOnly at line 83 runs twice with a fresh Rng.CombatTargets.NextItem roll each pass (line 80)`
  - `tier0/engine/effects.py:874-879 — `_op_apply_aura` sets `times = C.SALON_REPLACE_NUMERIC_MULT if state.salon_replacements_this_card else 1` and re-calls `_pick_targets` per iteration, i.e. the sim doubles it identically`
  - `klee-mod/KleeCode/Cards/Furina/Generated/OverflowingHospitality.cs:59 — the Encore numeric IS surfaced dynamically (`CalculatedVar("Encore").WithMultiplier(... ReplacementDelta ...)`), showing the codegen has a display path for replacement-scaled values that the aura clause does not use`
  - `klee-mod/KleeCode/Cards/SalonMemberTips.cs:132-150 — SalonRulesBody prints slots, bow order, Fanfare-Focus and the dry-tick rule, but never mentions that a replacement doubles the deploying card's own effects`
  - `docs/furina-cards.yaml:454 — sheet op list `{op: apply_aura, element: hydro, target: random_enemy}` is a single application; the doubling is engine-side replacement scaling the printed face never discloses`
  - _Sim and C# agree behaviourally (both double, both re-roll per pass); the defect is that the printed text under-describes the ops. This is the only card in the pool carrying both a salon_member deploy and an apply_aura, so it is the only face where a replacement-scaled effect has no dynamic-var display. Design context (not itself a defect): docs/archive/furina-salon-rework-plan.md:44-45 words the rule as "doubles the card's OTHER numerics / triples its damage riders", and the sibling Fanfare-Focus discipline at lines 34-37 states "Auras and the Encore rider do not scale (numbers-only)" — so whether an aura should be in scope at all is arguable, but both engines currently scale it in lockstep._
- **[low] other** — The C# aura repeat count is a hardcoded literal 2 instead of SalonConstants.ReplacementNumericMultiplier, so this one site escapes the cross-engine constant-parity gate that every other replacement-scaled value on the card goes through.
  - `klee-mod/KleeCode/Cards/Furina/Generated/OverflowingHospitality.cs:74 — `salonReplacements > 0 ? 2 : 1` (literal)`
  - `klee-mod/KleeCode/Cards/Furina/Generated/OverflowingHospitality.cs:59 — same card, same rule, sourced from the constant: `SalonConstants.ReplacementNumericMultiplier``
  - `klee-mod/KleeCode/Powers/SalonPowers.cs:34 — `public const int ReplacementNumericMultiplier = 2;``
  - `tier0/engine/effects.py:875 — sim reads `C.SALON_REPLACE_NUMERIC_MULT``
  - `tier0/constants.py:298 — `SALON_REPLACE_NUMERIC_MULT = 2  # deploy card's OTHER numerics on replacement``
  - _NO current behavioural divergence — both sides evaluate to 2 today. Filed low purely because the literal would silently desync from the sim if SALON_REPLACE_NUMERIC_MULT were ever repriced, which is the exact failure mode SalonMemberTips.cs:20-27 cites the constant-parity gate as existing to prevent._

### furina:pit_orchestra
- **[low] other** — C# doc comment on FanfareCapBonusResource still describes FurinaResources.RaiseFanfareCap as "retired grammar, no sheet user", but pit_orchestra (and every other Furina Power under the R7 keyword law) is a live sheet user of raise_fanfare_cap, and the same file's own constants block already records the op as un-retired. Comment-only drift; the code path itself is correct.
  - `/home/user/GItS/klee-mod/KleeCode/Powers/FurinaResources.cs:191-192 — "Mirroring that shape means <see cref=\"FurinaResources.RaiseFanfareCap\"/> (retired grammar, no sheet user) stays expressible without a rewrite."`
  - `/home/user/GItS/docs/furina-cards.yaml:499 — "{op: raise_fanfare_cap, amount: 5}" printed on pit_orchestra`
  - `/home/user/GItS/docs/furina-cards.yaml:33-38 — R7: EVERY Power prints a Fanfare keyword; non-rare Powers print "Fanfare Cap +X"`
  - `/home/user/GItS/klee-mod/KleeCode/Powers/FurinaResources.cs:84-85 — "(FurinaResources.RaiseFanfareCap, un-retired for the job)"`
  - `/home/user/GItS/klee-mod/KleeCode/Cards/Furina/Generated/PitOrchestra.cs:65 — FurinaResources.RaiseFanfareCap(Owner.Creature, DynamicVars["FanfareCap"].IntValue);`
  - _Two comments in the same file contradict each other; no player-visible effect. All three legs agree on behavior._

### furina:leading_role
- **[medium] sim_vs_csharp_divergence** — On the turn Leading Role is played (first copy, under Center Stage), the C# discount is live for a later Spotlighted card that same turn, while tier0's window has already been burned by Leading Role's own play. tier0 keeps the B2 window in global combat state (state.spotlighted_paid_cards_this_turn), incremented in play_card for every paid Spotlighted play BEFORE effect resolution — so Leading Role, itself a printed-cost-1 Spotlighted Furina card, ticks the counter to 1 before it applies its own power, and no card is discounted until the next turn. In C# the window is per-power-instance (_qualifyingPlaysThisTurn), and NotePlay runs in BeforeCardPlayed — before OnPlay creates the power — so the freshly applied SpotlightDiscountPower starts at 0 and the next paid Spotlighted card that same turn is discounted. Verified by running the sim: after combat.play_card(leading_role) with p.spotlight == character_id, spotlighted_paid_cards_this_turn == 1 and card_cost(stage_presence) == 1 (no discount).
  - `tier0/engine/combat.py:169 (`and state.spotlighted_paid_cards_this_turn == 0):`) — gate on global counter`
  - `tier0/engine/combat.py:224 (`state.spotlighted_paid_cards_this_turn += 1`) — incremented in play_card, before _finish_play/resolve_card`
  - `tier0/engine/combat.py:290 (`effects.resolve_card(state, card)` inside _finish_play — power lands after the counter tick)`
  - `tier0/tests/test_furina_sheet.py:840-843 (window is spent once a paid Spotlighted card goes; later cost back to 1)`
  - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:481 (`private int _qualifyingPlaysThisTurn;` — per-power-instance, starts at 0)`
  - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:338-345 (NotePlay ticks only `owner.Powers.OfType<SpotlightDiscountPower>()` — no instance exists yet on the play that creates it)`
  - `klee-mod/KleeCode/Powers/FurinaResources.cs:787 (`SpotlightSystem.NotePlay(cardPlay);` inside BeforeCardPlayed)`
  - `klee-mod/KleeCode/Cards/Furina/Generated/LeadingRole.cs:62 (`await PowerCmd.Apply<SpotlightDiscountPower>(...)` in OnPlay, i.e. after NotePlay)`
  - _Same asymmetry applies to any ordering where the power is applied after a paid Spotlighted play in the same turn (paid Spotlighted card, then Leading Role, then another Spotlighted card): tier0 refuses the discount, C# grants it. A SECOND copy behaves identically in both engines (the instance already exists, so NotePlay ticks it). All other legs agree: sheet ops apply_power spotlight_discount 1 + raise_fanfare_cap 5 (docs/furina-cards.yaml:507-508) match LeadingRole.cs:62-63 and CanonicalVars FanfareCap 5m (LeadingRole.cs:50); upgrade delta {cost: -1} (docs/furina-upgrades.yaml:126) matches EnergyCost.UpgradeBy(-1) (LeadingRole.cs:68) and tier0/content/upgrades.py:130-131; the R7 'every Power prints a Fanfare keyword' header rule is honored by the printed 'Fanfare Cap +5'._

### furina:supporting_cast
- **[low] text_ops_mismatch** — Upgraded Supporting Cast prints an ungrammatical/incorrect singular: the description hardcodes "card" with no plural token while PowerAmount upgrades 1 -> 2, so the upgraded face reads "draws 2 card." The same defect reaches the power tooltip when SpotlightDrawPower stacks above 1 (upgrade or a second copy, which the sheet's cap-drop ruling explicitly allows).
  - `docs/furina-upgrades.yaml:127 — supporting_cast: {power_amount: +1}    # first Spotlighted card draws 1->2`
  - `klee-mod/KleeCode/Cards/Furina/Generated/SupportingCast.cs:44 — ("description", "The first [gold]Spotlighted[/gold] card each turn draws {PowerAmount:diff()} card. ...") — no {PowerAmount:plural:|s}`
  - `klee-mod/KleeCode/Cards/Furina/Generated/SupportingCast.cs:69 — DynamicVars["PowerAmount"].UpgradeValueBy(1m)`
  - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:508-519 — SpotlightDrawPower description "...draws " + "{Amount} card."`
  - `tools/gen_klee_cards.py:539-540 — "spotlight_draw": ("SpotlightDrawPower", None, "The first [gold]Spotlighted[/gold] card each turn draws {X} card.") — singular template, no plural token`
  - `klee-mod/KleeCode/Cards/Furina/Generated/FloridCadenza.cs:44 — comparator that DOES use the idiom: "Draw {Cards:diff()} card{Cards:plural:|s}."`
  - `tools/gen_klee_cards.py:3913 — comment: "{Cards:plural:|s} pluralizes off the LIVE value"`
  - _Cosmetic only; the number itself (2) is correct and matches the sheet delta. Note the fixed-at-1 sibling PrimaDonna.cs:44 is unaffected because its SpotlightDrawPower application is a literal 1 and its upgrade only touches cost._
- **[medium] sim_vs_csharp_divergence** — spotlight_draw fires at a different point in the card-play pipeline in the two engines: tier0 draws INLINE during play_card, before the triggering card's own effects resolve; the C# mod defers the draw to AfterCardPlayed, i.e. after the triggering card fully resolves. Under Center Stage the first Spotlighted card each turn is simply the first Furina card played, so any first-play card that itself draws/discards/reshuffles (e.g. Florid Cadenza, Director's Cut) resolves its pile interactions in the opposite order between sim and mod.
  - `tier0/engine/combat.py:236-240 — if state.spotlighted_cards_this_turn == 1: n = p.powers.get("spotlight_draw", 0) ... state.draw(n)`
  - `tier0/engine/combat.py:252 — _finish_play(state, card)  (called AFTER the draw above)`
  - `tier0/engine/combat.py:290 — effects.resolve_card(state, card)  (inside _finish_play, i.e. the card's own effects run after the spotlight draw)`
  - `klee-mod/KleeCode/Powers/FurinaResources.cs:761,787 — BeforeCardPlayed ... SpotlightSystem.NotePlay(cardPlay)  (only queues)`
  - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:363-368 — var draw = PowerAmount<SpotlightDrawPower>(owner); ... PendingDraws[cardPlay] = new PendingDraw(draw, CombatOf(cardPlay))`
  - `klee-mod/KleeCode/Powers/FurinaResources.cs:791-794 — public override async Task AfterCardPlayed(...) { await SpotlightSystem.ResolvePendingDraw(choiceContext, cardPlay); }`
  - _The first-play WINDOW itself agrees (tier0 combat.py:236 spotlighted_cards_this_turn == 1 vs SpotlightSystem.cs:331 var first = plays.Amount == 0), as do stacking (uncapped Counter, SpotlightSystem.cs:441-446, tier0 test_furina_sheet.py:684-699) and the Fanfare Cap +5 half (docs/furina-cards.yaml:516 vs SupportingCast.cs:51,64). Only the resolution point differs. The C# deferral looks like a deliberate engine-integration choice (SpotlightSystem.cs:64-90 documents the PendingDraws lifecycle), and FurinaResources.cs:764 elsewhere explicitly claims to mirror "Sim order (combat.py play_card)" — so one of the two legs is the one that should move; flagging the mismatch, not prescribing the fix._

### furina:guest_list
- **[high] sim_vs_csharp_divergence** — The upgraded cost override has a different lifetime in the two engines: tier0 overwrites the generated token's PRINTED cost for the rest of the combat, while the C# sets it for this turn only. An upgraded Guest List's generated Companion held to a later turn costs 0 forever in the sim and its printed cost (1-2 Energy) in the mod.
  - `tier0/engine/effects.py:1205-1206 — `if "cost_override" in fx:  # upgraded form: 0 this turn` / `pick.cost = fx["cost_override"]` — this assigns the token's base `cost` field, not a per-turn delta`
  - `tier0/engine/combat.py:124-152 — card_cost() reads `card.cost` plus cost_delta_this_turn/this_combat; only combat.py:433 resets a turn-scoped cost field (companion_cost_delta_this_turn), nothing ever restores `card.cost`, so the 0 persists all combat`
  - `tier0/content/upgrades.py:434-441 — applier comment states the ruled reading explicitly: "Discovery-parity upgrade: the generated card costs 0 this combat (kickoff §9 upgrade grammar)"`
  - `klee-mod/KleeCode/Powers/GuestStarGenerator.cs:48-51 — `if (costOverride is int cost) { generated.EnergyCost.SetThisTurn(cost); }``
  - `klee-mod/KleeCode/Cards/Furina/Generated/GuestList.cs:65 — `await GuestStarGenerator.Generate(choiceContext, this, "uncommon", 1, IsUpgraded ? 0 : (int?)null);``
  - `klee-mod/KleeCode/Cards/Furina/Generated/GuestList.cs:47 — printed text says "They cost 0 this turn."`
  - `docs/furina-upgrades.yaml:128 — `guest_list: {generate_cost_override: 0}   # Discovery parity``
  - _Both legs are internally consistent (C# text at GuestList.cs:47 matches SetThisTurn; tier0 comment at upgrades.py:434-436 says this combat and the code implements permanent), so the disagreement is squarely cross-leg. The sheet's own note is "Discovery parity", and base-game Discovery is a this-turn discount, which points at tier0 as the drifting leg. Note also that every other cost_override path in the mod uses SetThisCombat (klee-mod/DECISIONS.md:1269, BorrowedBrilliance.cs:69, SecretStash.cs:81, EncorePerformance.cs:75), and the generator's own text emitter prints "this combat" for add_card overrides (tools/gen_klee_cards.py:4324) but "this turn" for generate_guest_star (tools/gen_klee_cards.py:4210-4211) — the guest-star path is the lone this-turn case. Systemic: AnInvitation.cs and CommandPerformance.cs share GuestStarGenerator and inherit the same divergence._
- **[low] text_ops_mismatch** — Upgraded description uses the plural "They" for a single generated card; the ops generate exactly 1 card and the same description's first sentence says "1 ... card" (singular).
  - `docs/furina-cards.yaml:520 — `effects: [{op: generate_guest_star, rarity: uncommon, amount: 1}, {op: energy, amount: 1}]``
  - `klee-mod/KleeCode/Cards/Furina/Generated/GuestList.cs:47 — "Add 1 random Uncommon [gold]Companion[/gold] card to your hand. {IfUpgraded:show:They cost 0 this turn.|} Gain 1 Energy."`
  - `tools/gen_klee_cards.py:4204-4211 — the emitter pluralizes the noun from amount (`noun = "card" if amount == 1 else "cards"`) but hard-codes the plural pronoun clause "They cost 0 this turn." regardless of amount`
  - _Cosmetic only; the number generated, its rarity and the Energy refund all match the sheet. The hard-coded clause also ignores the delta's value (it always prints 0), which happens to be correct here since generate_cost_override is 0._

### furina:top_billing
- **[low] other** — The top_billing upgrade-sheet comment asserts a "two-copy ceiling" on the +25% boost that no leg implements: the card sheet ruled the cap DROPPED (uncap-all), the tier0 engine applies no max_stacks, and the C# power declares no stack cap. A related stale line inside standing_ovation's comment block cites "top_billing's cap grammar" as the source of a two-copy ceiling, contradicting the CAP DROPPED line four lines above it.
  - `docs/furina-upgrades.yaml:130 — `top_billing: {cost: -1}  # 1->0 (mined power-cost line); the boost and its two-copy ceiling stay``
  - `docs/furina-cards.yaml:532 — `# CAP DROPPED (user ruling 2026-07-24, uncap-all). THE COMPOUNDING ONE: ... +25% per copy on ALL Spotlighted numbers``
  - `docs/furina-cards.yaml:553 — `# ... Boost has a two-copy ceiling (10+10, top_billing's cap grammar); ...` vs docs/furina-cards.yaml:546 `# CAP DROPPED (user ruling 2026-07-24, uncap-all): ovation_spend_boost was the other compounding ceiling``
  - `tier0/engine/effects.py:803 — `cap = fx.get("max_stacks")`; the sheet row at docs/furina-cards.yaml:526 carries no `max_stacks`, so tier0/engine/powers.py:170-171 never clamps`
  - `tier0/tests/test_furina_sheet.py:714-720 — four copies of top_billing assert `spotlight_mult_bonus == 4 * 25``
  - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:441-446 — `abstract class SpotlightPower : PowerModel` declares only Type/StackType, no max; klee-mod/KleeCode/Powers/SpotlightSystem.cs:520-530 SpotlightMultBonusPower adds none`
  - _Comment-only drift inside leg 1. The delta itself ({cost: -1}) matches klee-mod/KleeCode/Cards/Furina/Generated/TopBilling.cs:68 `EnergyCost.UpgradeBy(-1)`, and behaviour is identical across all three legs. No player-visible number is wrong._

### furina:duet
- **[low] other** — Furina's Duet grants a buff whose displayed title and icon are Klee's card "Study Buddy", breaking the otherwise universal convention on this roster that a power's title equals the name of the card that grants it. In a Furina run the player sees a buff named "Study Buddy" with klee/powers/study_buddy.png art after playing Duet; the sheet's card name is "Duet" and its comment calls the Klee link mechanical parity only.
  - `docs/furina-cards.yaml:536 — `- {id: duet, name: "Duet", register: salon, cost: 1, type: skill, rarity: uncommon, ...}``
  - `docs/furina-cards.yaml:538 — `# Study Buddy parity: the next companion performs twice. Star-agnostic — works on any guest.` (parity is stated for the mechanic, not the displayed name)`
  - `klee-mod/KleeCode/Cards/Furina/Generated/Duet.cs:62 — `await PowerCmd.Apply<ReplayNextCompanionPower>(choiceContext, Owner.Creature, 1, applier: Owner.Creature, cardSource: this);``
  - `klee-mod/KleeCode/Powers/CompanionPowers.cs:149 — `("title", "Study Buddy"),``
  - `klee-mod/KleeCode/Powers/KleePowerIcons.cs:56 — `ReplayNextCompanionPower => KleePck.Path("klee/powers/study_buddy.png"),``
  - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:513 — `("title", "Supporting Cast"),` (convention: power title = granting Furina card)`
  - `klee-mod/KleeCode/Powers/CurtainCallPowers.cs:288 — `("title", "Fortissimo Guard"),` (same convention)`
  - _Cosmetic/naming only — the power's own description text is mechanically accurate for Duet and matches the ops. ReplayNextCompanionPower is the ONLY cross-character, non-Furina-titled power any Furina generated card applies (all 20 others in Cards/Furina/Generated are Furina- or status-named). KleePowerIcons.cs:63-68 records that Furina powers rendering Klee textures was treated as a tracked defect and closed in Sprint 2 Track E; this one sits above that block and was not swept. No decision record covers the shared title (DECISIONS.md:1342-1348 discusses ReplayNextCompanionPower's mechanics only)._

### furina:standing_ovation
- **[low] other** — The design sheet's own comment block contradicts itself on the ovation_spend_boost stack ceiling, and the surviving 'two-copy ceiling' sentence disagrees with both implementations, which are uncapped.
  - `docs/furina-cards.yaml:546-547 — "CAP DROPPED (user ruling 2026-07-24, uncap-all): ovation_spend_boost was the other compounding ceiling ...; uncapped with top_billing"`
  - `docs/furina-cards.yaml:553-554 — "Boost has a two-copy ceiling (10+10, top_billing's cap grammar)"`
  - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:420-445 — SpotlightPower is "a Buff counter with NO stack ceiling"; OvationSpendBoostPower (SpotlightSystem.cs:587-596) derives from it with no cap`
  - `tier0/engine/effects.py (op) applies with no max_stacks; tier0/tests/test_furina_sheet.py:702-722 asserts standing_ovation stacks ovation_spend_boost to 4*10=40 uncapped`
  - _Comment-only drift: the effects list (docs/furina-cards.yaml:540) carries no max_stacks, so the executable half of the sheet agrees with both engines. Nothing player-visible is wrong; the stale sentence is a reading hazard only. The same stale rationale is repeated in docs/furina-upgrades.yaml:133-134 ("would outgrow the two-copy cap (20 != amount ...)") and docs/furina-upgrades.yaml:130 (top_billing, out of scope for this card)._
- **[low] sim_vs_csharp_divergence** — The turn-scoped spend boost expires at a different site in each engine: tier0 pops it at the player's TURN END, while C# clears the SpotlightSpendBoostResource at the next player TURN START, so the C# boost survives the whole enemy turn.
  - `tier0/engine/resources.py:299-303 — spend adds into p.powers["spotlight_mult_bonus_turn"]; tier0/engine/powers.py:23 lists it in EXPIRING and tier0/engine/powers.py:139-144 (on_turn_end) pops it at the owner's turn end`
  - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:387-392 (OnEncoreSpent) writes SpotlightSpendBoostResource; it is zeroed only in ResetTurn at klee-mod/KleeCode/Powers/SpotlightSystem.cs:300-307, which is invoked from AfterPlayerTurnStart at klee-mod/KleeCode/Powers/FurinaResources.cs:905-910`
  - `Intra-C# contrast: the sibling turn-window power SpotlightMultBonusTurnPower removes itself at klee-mod/KleeCode/Powers/SpotlightSystem.cs:579-584 (AfterSideTurnEnd, CombatSide.Player) — the same "this turn" grammar unwound one broadcast earlier`
  - _No reachable functional consumer found: OutwardMultiplier (SpotlightSystem.cs:232-246) is only reached via PrintedDamage/PrintedBlock on a CardModel, and Companion cards are only played on the player's turn; the resource is cleared before the first play of the next turn. The observable delta is confined to card-face rendering (PrintedDamageDelta, SpotlightSystem.cs:280-285) during the enemy turn. Filed as a mechanism-level timing divergence, not a wrong number._

### furina:quick_change
- **[low] text_ops_mismatch** — The upgraded card reads "draws 2 card": QuickChange's description hard-codes the singular noun with no plural directive, even though the upgrade delta takes the draw count to 2. Every other upgradeable draw line in the pool uses the {Var:plural:|s} directive.
  - `docs/furina-upgrades.yaml:137 — quick_change: {power_amount: +1}  # first-Attack draw 1->2`
  - `klee-mod/KleeCode/Cards/Furina/Generated/QuickChange.cs:44 — ("description", "The first Attack you play each turn draws {PowerAmount:diff()} card. ...") — singular, no {PowerAmount:plural:|s}`
  - `klee-mod/KleeCode/Cards/Furina/Generated/QuickChange.cs:69 — DynamicVars["PowerAmount"].UpgradeValueBy(1m) so the live value is 2 when upgraded`
  - `klee-mod/KleeCode/Cards/Furina/Generated/DirectorsCut.cs:44 — contrast: "draw {Cards:diff()} card{Cards:plural:|s}"`
  - `klee-mod/KleeCode/Powers/CurtainCallPowers.cs:389 — FirstAttackDrawPower tooltip repeats the singular: "draws {Amount} card."`
  - `tools/gen_klee_cards.py:4163 — apply_power path: template.replace("{X}", x) with no plural suffix, vs tools/gen_klee_cards.py:3923 — draw path: f"Draw {{{v}:diff()}} card{{{v}:plural:|s}}."`
  - _Purely cosmetic/grammatical; the op behaviour is correct on both sides. Systemic to the apply_power description template, so the sibling cards CrowdWork.cs:44 and SupportingCast.cs:44 carry the same wording — reported here only as it manifests on quick_change. Everything else on this card is clean: sheet effects [apply_power first_attack_draw amount 1 target self; raise_fanfare_cap 5] match QuickChange.cs:63-64 in order and value; cost 1 / Power / Uncommon / TargetType.Self match QuickChange.cs:57; the uncommon "Fanfare Cap +5" satisfies the header's R7 every-Power rule and the +5 common/uncommon magnitude; sim refpowers.py:728-737 (increment then == 1, per play not per series, reset at refpowers.py:1327) matches CurtainCallPowers.cs:213-220 plus ResetTurn at :70-77; resources.raise_fanfare_cap (cap only, inert for non-Furina) matches FurinaResources.RaiseFanfareCap:685-689._

### furina:curtain_up
- **[low] text_ops_mismatch** — The printed description says "Look at the top 1 cards of your draw pile" — the plural noun disagrees with the op's amount of 1. The description template hardcodes "cards" with no singular branch, and curtain_up is the only card on any sheet with scry_discard amount 1 (Klee's two scry cards both use 2), so it is the only face that renders the ungrammatical string.
  - `docs/furina-cards.yaml:629 — effects: [{op: gain_encore, amount: 2}, {op: scry_discard, amount: 1}]`
  - `klee-mod/KleeCode/Cards/Furina/Generated/CurtainUp.cs:44 — ("description", "Gain {IfUpgraded:show:3|2} [gold]Encore[/gold]. Look at the top 1 cards of your draw pile; discard one.")`
  - `tools/gen_klee_cards.py:4294-4296 — f'Look at the top {int(eff["amount"])} cards of your draw ' "pile; discard one." (no pluralization branch)`
  - `klee-mod/KleeCode/Cards/Generated/HideAndSeek.cs:40 — same template at amount 2, where "cards" is correct`
  - _Numbers, ordering and behavior are all correct; this is purely the displayed noun. Cosmetic only._

### furina:crowd_work
- **[low] text_ops_mismatch** — The Gallery Stirs' printed draw count is never pluralized, so the upgraded card and its power tooltip read "draw 2 card" — the repo's own codegen convention requires the {Var:plural:|s} token exactly for counts an upgrade moves off 1.
  - `docs/furina-upgrades.yaml:58 — `crowd_work: {power_amount: +1}   # first-spend draw 1->2`, so the displayed count becomes 2 on upgrade`
  - `klee-mod/KleeCode/Cards/Furina/Generated/CrowdWork.cs:44 — description is "The first time you spend Encore each turn, draw {PowerAmount:diff()} card." with a hardcoded singular "card" and no {PowerAmount:plural:|s}`
  - `klee-mod/KleeCode/Cards/Furina/Generated/CrowdWork.cs:69 — OnUpgrade does DynamicVars["PowerAmount"].UpgradeValueBy(1m), confirming the var renders as 2`
  - `klee-mod/KleeCode/Powers/CurtainCallPowers.cs:374 — EncoreSpendDrawPower tooltip repeats the same singular: "The first time you spend Encore each turn, draw {Amount} card."`
  - `tier0/tests/test_roster_codegen.py:943-944 — the pinned convention: "# The plural token, not a hardcoded \"s\": Crackle+ discards 2." / assert "{Discards:plural:|s}" in crackle`
  - `klee-mod/KleeCode/Cards/Furina/Generated/TempoChange.cs:44 — the same generator emits "Draw {Cards:diff()} card{Cards:plural:|s}." for draw ops, showing the token is the house style`
  - _Source is the generator's APPLY_POWERS template table (tools/gen_klee_cards.py:573-576), so the same singular also affects quick_change (upgrades yaml:137) and supporting_cast (:127); it is grammar only — the drawn count itself is correct on both legs._
- **[low] other** — Noted and NOT filed as a defect (recorded for the sweep): the C# draw is deferred out of the spend site to the next async Furina hook while tier0 draws inside spend_encore, so a card that spends Encore and then inspects hand during its own effects would see a different hand in the two engines. This is explicitly ruled and documented, not drift.
  - `tier0/engine/resources.py:309-313 — sim draws immediately inside spend_encore: `state.draw(n)` under the once-per-turn latch`
  - `klee-mod/KleeCode/Powers/CurtainCallPowers.cs:157-169 — NoteEncoreSpent only records PendingDraws; the comment states SpendEncore is synchronous and holds no PlayerChoiceContext`
  - `klee-mod/KleeCode/Powers/FurinaResources.cs:818 / :914 / :944 — FlushPendingDraws sites (AfterCardPlayed, AfterPlayerTurnStart, BeforeSideTurnEnd)`
  - `tier0/DECISIONS.md:2778-2781 — R86 rules the deferral: "encore_spend_draw's draw is DEFERRED, because SpendEncore is synchronous and holds no PlayerChoiceContext"`
  - _Everything else matches three ways: cost 1 / Power / Uncommon / self (docs/furina-cards.yaml:648 vs CrowdWork.cs:57); apply_power encore_spend_draw 1 (yaml:649 vs CrowdWork.cs:50,63); raise_fanfare_cap 5 = headroom only, inert without the resource (yaml:650 vs resources.py:172-186 vs FurinaResources.cs:685-689); once-per-turn latch and dry-spend no-draw (resources.py:309-313 + test_curtain_call.py:97-116 vs CurtainCallPowers.cs:165-169 + FurinaResources.cs:597-600); latch reset strictly before Salon upkeep in both (combat.py:441 vs CurtainCallPowers.cs:70-77 + FurinaResources.cs:874-880); upgrade power_amount +1 bumps only the apply_power amount in both (upgrades.py:453-467 vs CrowdWork.cs:67-70). R7 keyword requirement satisfied — the Power prints Fanfare Cap +5, the ruled uncommon magnitude._

### furina:let_the_people_rejoice
- **[low] text_ops_mismatch** — The hand-written card prints the AppliesHydro badge and really does apply a Hydro aura, but it is the only Hydro-applying Furina card that never chains KleeCardTooltips.ForCard(..., Element.Hydro, ...) into ExtraHoverTips, so it shows no reaction-preview hover tips when an aura'd enemy is on the board.
  - `klee-mod/KleeCode/Cards/Furina/LetThePeopleRejoice.cs:41 (CanonicalKeywords => { CardKeyword.Retain, KleeKeywords.AppliesHydro })`
  - `klee-mod/KleeCode/Cards/Furina/LetThePeopleRejoice.cs:46-48 (ExtraHoverTips => FurinaRiderTips.ForCard(base.ExtraHoverTips, this, fanfarePer: 1, fanfareStep: 4) -- base tips passed straight through, no element trigger)`
  - `klee-mod/KleeCode/Cards/Furina/Generated/HighTide.cs:46-47 (same rider helper, but wrapping KleeCardTooltips.ForCard(base.ExtraHoverTips, this, Element.Hydro, includesBombRules: false))`
  - `klee-mod/KleeCode/Cards/Furina/Generated/MatineePerformance.cs:46-47, RainOfRoses.cs:43-44, FloodOfEmotion.cs:46-47, OverflowingHospitality.cs:43-44, SharedBilling.cs:43-44, GuestNeuvilletteTears.cs:54-55 (every other AppliesHydro Furina card chains the element tooltip)`
  - `tools/gen_klee_cards.py:4693-4696 and 4907-4917 (generator contract: a card whose damage applies the element gets preview_element_cs set and emits KleeCardTooltips.ForCard(..., Element.Hydro, ...) alongside the AppliesHydro keyword)`
  - `klee-mod/KleeCode/Cards/KleeCardTooltips.cs:39-58 (trigger == Element.None short-circuits, so the reaction-preview tips are simply never yielded)`
  - `docs/furina-cards.yaml:16 (cadence rule: burst-tag cards apply hydro) and docs/furina-cards.yaml:662 (tags: [burst]) -- the ops do apply hydro, so the missing tip is a display gap, not a behavior gap`
  - _Display-only. Aura application itself is correct: klee-mod/KleeCode/Cards/Furina/LetThePeopleRejoice.cs:22-24 implements IElementalCard/Hydro and klee-mod/KleeCode/Powers/ElementalApplication.cs:196-203 applies the aura off that interface, matching tier0/engine/effects.py:278-286 (_element_for, burst tag under skill cadence)._

### furina:encore_performance
- **[high] sim_vs_csharp_divergence** — The C# copy-target pool omits the mod's own kit-card exemption, so Encore Performance can select and duplicate Furina's kit Burst (Let the People Rejoice) out of hand; the tier0 op filters kit cards out of the pool unconditionally.
  - `tier0/engine/effects.py:1231-1232 — targets = [c for c in p.hand if is_spotlighted(state, c) and not c.kit_card]`
  - `klee-mod/KleeCode/Cards/Furina/Generated/EncorePerformance.cs:64-65 — CardPile.Get(PileType.Hand, Owner)?.Cards.Where(SpotlightSystem.IsSpotlighted).ToList() (no KitGrant.NotKitCard filter)`
  - `klee-mod/KleeCode/Powers/KitBurst.cs:133-144 — KitGrant.NotKitCard exists precisely for this invariant and names LetThePeopleRejoice`
  - `klee-mod/KleeCode/Cards/Furina/LetThePeopleRejoice.cs:22-26 — the Burst is a CustomCardModel/ICharacterCard with CharacterId "furina", and it is Retained in hand while the meter is full (LetThePeopleRejoice.cs:33-40 CanonicalKeywords includes Retain)`
  - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:214-221 — IsSpotlighted returns true for any ICharacterCard{CharacterId:"furina"} while Center Stage is active, i.e. for the Burst in hand`
  - `tools/gen_klee_cards.py:3379-3400 — the copy_spotlighted_in_hand emitter that produced those lines never emits the KitGrant.NotKitCard filter (contrast tools/gen_klee_cards.py:3310-3324, where the discard emitter does)`
  - _Reachable in normal play: Center Stage designated + full Burst meter (the kit card is granted to hand and Retained). Consequences C#-side: the Burst can be the chosen copy (and is the only choice when it is the sole Furina card in hand, where the sim produces nothing), the extra copy lands in a pile-visible hand slot that KitGrant's hand dedup then reads, and upgraded Encore Performance sets that copy's energy cost to 0. Even when other targets exist, the kit card inflates the random pool, changing selection odds versus the sim._
- **[medium] sim_vs_csharp_divergence** — The copy's provenance differs: tier0 deep-copies the chosen hand instance (so an upgraded Spotlighted card yields an upgraded copy, and instance cost state carries), while the C# rebuilds a fresh instance from the base CardModel by id, producing an unupgraded copy.
  - `tier0/engine/effects.py:1236 — chosen = _copy.deepcopy(state.rng.choice(targets)) (the in-hand instance, upgrade suffix/effects included)`
  - `klee-mod/KleeCode/Cards/Furina/Generated/EncorePerformance.cs:71-72 — CombatState!.CreateCard(ModelDb.GetById<CardModel>(selectedSpotlight.Id), Owner)`
  - `vendor/STS2_MCP/McpMod.StateBuilder.cs:1245,1252 — card.Id.Entry and card.IsUpgraded are independent fields, so the model id carries no upgrade state`
  - `vendor/STS2_MCP/McpMod.Helpers.cs:53-63 — upgrading is instance-level (MutableClone + UpgradeInternal), confirming a model-id rebuild starts unupgraded`
  - `tier0/engine/effects.py:1253-1259 — the engine's own add_card 'card: self' branch documents that a clone must inherit the playing instance's upgrade state, the same expectation the deepcopy here encodes`
  - _Player-visible whenever the Spotlighted target is upgraded (e.g. a copied High Tide+ resolves at its base numbers C#-side but upgraded in the sim). Systemic to the copy emitters rather than Furina-specific — the same ModelDb.GetById rebuild appears at klee-mod/KleeCode/Cards/Generated/BorrowedBrilliance.cs:68 and klee-mod/KleeCode/Cards/Kokomi/Generated/ShoulderToShoulder.cs:82 — and the generator comment at tools/gen_klee_cards.py:3343-3345 calls it a 'fresh copy', so intent may be deliberate; reported because the two legs still resolve different cards. The upgrade delta itself is clean: docs/furina-upgrades.yaml:142 {copy_cost_override: 0} matches tier0/content/upgrades.py:490-497 and EncorePerformance.cs:74-76 (EnergyCost.SetThisCombat(0)) plus the {IfUpgraded:show:...} text at EncorePerformance.cs:44._

### furina:the_sea_is_my_stage
- **[low] other** — The sheet's own card comment describes a grant total that the sheet header explicitly deleted: it says the card 'ALSO earns the rarity grant, so it lands as a permanent baseline of 15 plus the standard rare-Power grant on top', but the Fanfare Rework Track B deleted the invisible per-Power ('rares 8') automatic. Both implementation legs grant exactly 15 (20 upgraded), matching the effects list, so this is stale documentation inside LEG 1, not a behavioral divergence — but read literally it implies a 23-point baseline that no leg produces.
  - `docs/furina-cards.yaml:731-732 ("Being a Rare Power it ALSO earns the rarity grant, so it lands as a permanent baseline of 15 plus the standard rare-Power grant on top")`
  - `docs/furina-cards.yaml:27 ("TRACK B -- PRINTED KEYWORDS. The invisible \"every Power grants 5 floor, rares 8\" automatic is DELETED.")`
  - `tier0/engine/combat.py:292-302 ("THE AUTOMATIC POWER FLOOR GRANT USED TO LIVE HERE. Deleted by the Fanfare rework ... There is deliberately NO card-type branch left in this function")`
  - `klee-mod/KleeCode/Cards/Furina/Generated/TheSeaIsMyStage.cs:49 (new DynamicVar("FanfareFloor", 15m)) and :63 (FurinaResources.GainFanfareFloor(..., DynamicVars["FanfareFloor"].IntValue)) — 15 only, no rarity top-up`
  - _Comment drift only; no player-visible number is wrong._

### furina:the_final_verdict
- **[high] upgrade_delta_drift** — The ruled upgrade delta `floor_drop: -10` (crash 30 -> 20) is applied by the tier0 sim but is silently dropped by the C# card: TheFinalVerdict+ still crashes the Fanfare floor by 30, and its face still renders FloorDrop 30.
  - `docs/furina-upgrades.yaml:155 — `the_final_verdict:     {floor_drop: -10}` with the comment "floor drop 30 -> 20"`
  - `docs/furina-cards.yaml:779 — base effect `{op: crash_fanfare, amount: 30}``
  - `tier0/content/upgrades.py:410-418 — `elif key == "floor_drop": ... _bump_first((fx for fx in top if fx.get("op") == "crash_fanfare"), "amount", val)`, and tier0/content/upgrades.py:72 `UNAPPLIABLE: frozenset[str] = frozenset()` (nothing blocks it), so the simulated upgraded card crashes by 20`
  - `klee-mod/KleeCode/Cards/Furina/Generated/TheFinalVerdict.cs:57 — `new DynamicVar("FloorDrop", 30m)``
  - `klee-mod/KleeCode/Cards/Furina/Generated/TheFinalVerdict.cs:78-81 — `protected override void OnUpgrade() { // R24: NO upgrade path -- None. Flagged in manifest. }` (empty body: no FloorDrop bump)`
  - `klee-mod/KleeCode/Cards/Furina/Generated/TheFinalVerdict.cs:75 — `FurinaResources.DropFanfareToFloor(Owner.Creature, DynamicVars["FloorDrop"].IntValue);` consumes the un-upgraded 30`
  - _Root cause is reproducible, not a stale checked-in file: tools/gen_klee_cards.py:728 puts "floor_drop" in EXPRESSIBLE_DELTAS and tools/gen_klee_cards.py:2241 marks it available on any card with a crash_fanfare op, so upgrade_plan returns (deltas, None); but the OnUpgrade emitter has no floor_drop branch — tools/gen_klee_cards.py:4616-4623 emits only FanfareCap and FanfareFloor bumps — so the upgrade line list comes back empty and tools/gen_klee_cards.py:4785-4789 falls through to the "NO upgrade path" comment. Regenerating produces the same wrong card._
- **[medium] other** — The card's own comment says the missing upgrade path is "Flagged in manifest", but the generated manifest's no_upgrade_path is empty, so the R24 safety net that is supposed to make "the sim can upgrade this and the mod cannot" visible does not cover this card; the reason string is also the literal placeholder "None".
  - `klee-mod/KleeCode/Cards/Furina/Generated/TheFinalVerdict.cs:80 — `// R24: NO upgrade path -- None. Flagged in manifest.``
  - `klee-mod/KleeCode/Cards/Furina/Generated/manifest.json:117-120 — `"upgrades": { "_comment": "...A generated card listed below ships without an upgrade until its full delta is expressible...", "no_upgrade_path": {} }` (empty; the_final_verdict appears only in the generated list at manifest.json:84)`
  - `docs/furina-upgrades.yaml:155 — the ruled delta that was dropped without a flag`
  - `tools/gen_klee_cards.py:5137-5139 — `_, upgrade_reason = upgrade_plan(card); if upgrade_reason: no_upgrade[card["id"]] = upgrade_reason` (only cards whose plan reports a reason are flagged; this card's plan reports None)`
  - _Contrast the honest form used by cards with a genuinely inexpressible delta, e.g. klee-mod/KleeCode/Cards/Furina/Generated/GuestNeuvilletteTears.cs:92 ("no ratified delta in klee-upgrades.yaml"), which does correspond to a real absence of delta._

### furina:command_performance
- **[medium] sim_vs_csharp_divergence** — The upgraded cost override has different duration in the two engines: tier0 makes each generated guest cost 0 for the REST OF COMBAT (it overwrites the token's base cost), while the C# mod makes it cost 0 for THIS TURN ONLY (EnergyCost.SetThisTurn), which is also what the printed description says.
  - `tier0/engine/effects.py:1205-1206 — `if "cost_override" in fx:  # upgraded form: 0 this turn` / `pick.cost = fx["cost_override"]` (writes the token's permanent base cost; the engine's per-turn window is the separate `cost_delta_this_turn` field consulted at tier0/engine/combat.py:142-152, which this path never touches)`
  - `klee-mod/KleeCode/Powers/GuestStarGenerator.cs:48-51 — `if (costOverride is int cost) { generated.EnergyCost.SetThisTurn(cost); }``
  - `klee-mod/KleeCode/Cards/Furina/Generated/CommandPerformance.cs:47 — description `"...{IfUpgraded:show:They cost 0 this turn.|}"` (C# text matches C# behavior, not sim behavior)`
  - `docs/furina-upgrades.yaml:162 — `command_performance:   {generate_cost_override: 0}   # both guests cost 0 (Discovery parity)` (delta states no duration)`
  - `tier0/content/upgrades.py:435-436 — `# Discovery-parity upgrade: the generated card costs 0 this` / `# combat (kickoff §9 upgrade grammar).` (sim's own doc says COMBAT, contradicting the effects.py comment and the C# text)`
  - _Command Performance+ adds 2 guests at once, so the held-over card is the normal case, not a corner: in tier0 a guest kept for a later turn is still free (and stays free even after cycling through discard/draw), in the mod it reverts to its printed cost at end of turn. The divergence is systemic to the generate_cost_override path (an_invitation, guest_list share it), but it lands on this card's upgraded value. Everything else on this card matches across all three legs: cost 1 / Skill / Rare / Exhaust, rarity=uncommon amount=2 to hand, pool identity (17 uncommon entries on both sides — 16 companions + guest_neuvillette_judgment), random-with-replacement selection over an id-sorted pool, and lint compliance (rare generator producing uncommon, exhaust present)._
- **[low] other** — Comment drift on the equal-rarity guardrail: the sim (and the C# helper's doc-comment) describe the Guest Star pool as filtered to the GENERATOR's own printed rarity, which this card contradicts — it is a Rare that generates Uncommons. The sheet states the correct rule (the clause reads the GENERATED rarity); all code actually filters on the effect's `rarity` field, so behavior is fine.
  - `docs/furina-cards.yaml:800-803 — card is `rarity: rare` with `effects: [{op: generate_guest_star, rarity: uncommon, amount: 2}]`, comment: "the equal-rarity clause reads the GENERATED rarity, and this card's own grammar keeps it under the banner"`
  - `tier0/engine/effects.py:1152-1155 — docstring: "equal-rarity (the pool is filtered to fx['rarity'] == the generator's own printed rarity)" — false for this card (fx rarity uncommon, generator rare)`
  - `tier0/content/loader.py:287-289 — "shared companions plus the purpose-built Guest Star set, at EXACTLY the generator's rarity"`
  - `klee-mod/KleeCode/Powers/GuestStarGenerator.cs:14-16 — "filtered to exactly the generator's rarity"`
  - _Cosmetic only — the lint at tools/gen_klee_cards.py:1310-1314 encodes the real rule (generated rarity may not EXCEED generator rarity), and both engines filter on the effect's rarity field._

### furina:reginas_mercy
- **[low] other** — Stale doc comment in the C# resource layer asserts that RaiseFanfareCap is 'retired grammar, no sheet user', but reginas_mercy (and lasting_impression) are live sheet users of raise_fanfare_cap after the 2026-07-28 Fanfare rework Track B. Comment drift only; the runtime behavior is correct and matches the sim.
  - `klee-mod/KleeCode/Powers/FurinaResources.cs:192`
  - `docs/furina-cards.yaml:805`
  - `docs/furina-cards.yaml:39`
  - `klee-mod/KleeCode/Cards/Furina/Generated/ReginasMercy.cs:66`
  - _The sibling doc block on the method itself (klee-mod/KleeCode/Powers/FurinaResources.cs:675-688) was correctly updated for the reintroduction ('The ruling was reopened, on 2026-07-28, and this is the reintroduction'), so only the FanfareCapBonusResource class comment is stale. Contradictory comments in one file about the same op. No player-visible effect._

### furina:thunderous_ovation
- **[medium] text_ops_mismatch** — The card's Fanfare rider hover tip tells the player the rider is worth extra DAMAGE, but Thunderous Ovation is a self-target Skill whose only op is `block` — it deals no damage at all. The shared FanfareBody helper hard-codes the noun "damage" and, unlike the Salon rider, has no block/damage noun switch.
  - `docs/furina-cards.yaml:816 — `effects: [{op: block, amount: 6, bonus_formula: 1_per_2_fanfare}]` (block only, no damage op)`
  - `tier0/engine/effects.py:615-637 — `_op_block` adds `_bonus_formula(...)` to Block and emits `state.emit("block", ...)`; nothing damages`
  - `klee-mod/KleeCode/Cards/Furina/Generated/ThunderousOvation.cs:41 — `FurinaRiderTips.ForCard(base.ExtraHoverTips, this, fanfarePer: 1, fanfareStep: 2)` (no block noun argument exists for the fanfare rider)`
  - `klee-mod/KleeCode/Cards/Furina/Generated/ThunderousOvation.cs:68 — OnPlay calls only `CreatureCmd.GainBlock(...)``
  - `klee-mod/KleeCode/Cards/FurinaRiderTips.cs:87 — `var rate = $"+{per} damage per {step} Fanfare you hold.";``
  - `klee-mod/KleeCode/Cards/FurinaRiderTips.cs:92-93 — `return $"{rate} You hold {fanfare} Fanfare: +{fanfare / step * per} " + "damage, already counted in the number above.";``
  - `klee-mod/KleeCode/Cards/FurinaRiderTips.cs:46 and :105-106 — the SALON rider does carry a noun switch (`bool salonGrantsBlock`, `var noun = grantsBlock ? "Block" : "damage";`), showing the fanfare path is the one missing it`
  - `tools/gen_klee_cards.py:1673-1674 — fanfare rider emits only `fanfarePer`/`fanfareStep`, while :1680-1681 emits `salonGrantsBlock: true` for a block-op salon rider`
  - _Numbers themselves are correct on every leg: sheet base 6 + 1 per 2 Fanfare (docs/furina-cards.yaml:816) == C# CalculationBaseVar(6m)/CalculationExtraVar(1m)/multiplier ReadableFanfare/2 (ThunderousOvation.cs:54-56); upgrade block +2 (docs/furina-upgrades.yaml:65) == OnUpgrade UpgradeValueBy(2m) (ThunderousOvation.cs:73); the zero-clamp on a negative meter matches (tier0/engine/resources.py:225 vs FurinaResources.cs:569); cost/type/rarity/target match (yaml:815 vs ThunderousOvation.cs:62). The tip helper is shared, so this same wording defect will surface on every fanfare-reading block card (held_breath, hearts_swelling, suffering_for_art, aria_of_recompense); reported here because it is player-visible on this card's face-inspect._

### furina:rapturous_applause
- **[medium] sim_vs_csharp_divergence** — The Fanfare read that feeds this card's power is a per-card SNAPSHOT in tier0 but a LIVE per-hit read in C#, so an attack card that moves Fanfare during its own resolution boosts its own damage in the mod and not in the sim.
  - `tier0/engine/effects.py:2250 — `bonus = flat_attack_bonus(state, card, state.current_card_cost)` is computed BEFORE the card's effects run`
  - `tier0/engine/effects.py:2267 — `state.current_attack_bonus = bonus``
  - `tier0/engine/effects.py:2269 — `_resolve_effects(state, card.effects, card)` runs only after the snapshot`
  - `tier0/engine/effects.py:2317-2320 — `n = p.powers.get("fanfare_attack_per10", 0)` … `bonus += n * (resources.readable(p) // 10)` (evaluated inside the snapshot helper)`
  - `klee-mod/KleeCode/Powers/FurinaResources.cs:1145-1146 — "Fanfare is read per hit, so spending or gaining it changes later attacks immediately."`
  - `klee-mod/KleeCode/Powers/FurinaResources.cs:1155-1162 — `ModifyDamageAdditive(...) { … return Amount * (FurinaResources.ReadableFanfare(Owner) / 10); }` evaluated at damage-resolution time`
  - `klee-mod/KleeCode/Cards/Furina/Generated/Breathless.cs:60-69 — `await FurinaResources.SpendEncoreOrHp(…, 4, this);` then `await DamageCmd.Attack(...).Execute(choiceContext);``
  - `klee-mod/KleeCode/Powers/FurinaResources.cs:595-608 — `SpendEncore` calls `GainFanfare(creature, spent * FanfarePerEncoreSpent)` synchronously during that spend`
  - `tier0/engine/resources.py:279-288 — sim's `spend_encore` likewise calls `gain_fanfare(state, spent * C.FANFARE_PER_ENCORE_SPENT, "encore_spent")``
  - `docs/furina-cards.yaml:281-282 — breathless `effects: [{op: spend_encore, amount: 4}, {op: damage, amount: 9, target: enemy}]``
  - _Concrete case: Rapturous Applause active (PowerAmount 1), Fanfare at 8, play Breathless. Sim snapshots bonus = 1*(8//10) = 0 and deals 9. Mod spends 4 Encore first, meter reads 12 at damage time, bonus = 1, deals 10 (2 apart at PowerAmount 2 / upgraded). Same class of gap for the HP-overdraw path (spend_encore_or_hp prints Fanfare via hp loss) and for any future multi-hit attack that moves the meter mid-card. DECISIONS.md:1470-1477 rules on the snapshot only with respect to the repeat_this tail; it does not address a mid-card Fanfare mover. the_final_verdict (docs/furina-cards.yaml:778-779) is NOT affected — its crash_fanfare is ordered after its damage in both engines._
- **[low] upgrade_delta_drift** — The upgrade delta's trailing comment still asserts a 2-stack cap on this power, which both the design sheet and the C# power record as dropped; the numeric delta itself (+1) is correct on every leg.
  - `docs/furina-upgrades.yaml:123 — `rapturous_applause:    {power_amount: +1}    # +1->+2 per 10 Fanfare, cap 2 unchanged``
  - `docs/furina-cards.yaml:846-847 — "CAP DROPPED (user ruling 2026-07-24, uncap-all): +1/copy per 10 Fanfare is additive in copies."`
  - `klee-mod/KleeCode/Powers/FurinaResources.cs:1138-1140 — "The two-stack cap was dropped 2026-07-24 (uncap-all ruling): +1/copy per 10 Fanfare is additive in copies"`
  - `docs/furina-cards.yaml:836-837 — sheet effect carries no `max_stacks`, so tier0/content/upgrades.py:472-474 (`if hit.get("max_stacks") == hit["amount"]`) never fires`
  - `klee-mod/KleeCode/Cards/Furina/Generated/RapturousApplause.cs:69-71 — `OnUpgrade() { DynamicVars["PowerAmount"].UpgradeValueBy(1m); }` (1 -> 2, no cap)`
  - _Comment-only drift: no engine, sheet op, or C# value implements a cap, so no player-visible number changes. Recorded because the comment is a factual claim about this card's cap that the other two legs contradict, not an R-number context citation._

**CLEAN (52):** soloists_solicitation, stage_presence, regal_bearing, casting_call, gentilhomme_usher, surintendante_chevalmarin, mademoiselle_crabaletta, dinner_service, usher_the_waves, house_call, lasting_impression, warmup_act, applause_line, breathless, limelight, stage_lights, curtain_cue, graceful_retreat, commanding_gaze, macaron_break, undercurrent, take_your_bow, full_ensemble, many_waters_melody, dress_rehearsal, waters_embrace, crescendo, florid_cadenza, hearts_swelling, directors_cut, fortissimo_guard, courtroom_drama, deep_breath, torrential_turn, dramatic_entrance, witness_stand, audience_participation, tempo_change, poised_riposte, matinee_performance, standing_room_only, singer_of_many_waters, unheard_confession, endless_waltz, grand_gala, universal_revelry, star_of_the_show, prima_donna, high_tide, rain_of_roses, flood_of_emotion, showstopper

## Kokomi — 61 cards, 27 with findings

### kokomi:waters_edge
- **[low] other** — WatersEdge.cs's XML doc comment on the Element member states Furina's SKILL-grade cadence rule ("damaging Skills, Burst-tagged cards, and skill-tagged cards apply Hydro"), which contradicts Kokomi's ruled CATALYST cadence in the sheet header (every attack applies Hydro). Runtime behaviour is correct — the card is an Attack, carries KleeKeywords.AppliesHydro, and the generator profile is cadence="catalyst_attack" — so this is comment-only drift from the generator's non-Klee branch hardcoding Furina's sentence.
  - `docs/kokomi-cards.yaml:52 — "# Element: hydro | Cadence: CATALYST (RULED R52, ask N1): every attack applies hydro"`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/WatersEdge.cs:37 — "/// <summary>Sheet cadence: damaging Skills, Burst-tagged cards, and skill-tagged cards apply Hydro.</summary>"`
  - `tools/gen_klee_cards.py:4838-4842 — non-Klee profiles unconditionally emit the skill-grade sentence`
  - `tools/gen_klee_cards.py:141-153 — KOKOMI_PROFILE declares cadence="catalyst_attack"`
  - `tier0/engine/effects.py:279-281 — catalyst branch: any attack's damage op applies the character element`
  - _Roster-wide (all 18 elemental Kokomi generated cards carry the identical string), not specific to this card. No player-visible effect: CanonicalKeywords at WatersEdge.cs:43-44 is AppliesHydro and matches the sim._

### kokomi:bake_kurage
- **[low] other** — The sheet's own comment on bake_kurage cites `amount: 3` as mirroring KURAGE_DURATION, but the effects line ships `amount: 1` and KURAGE_DURATION is 1 — a stale leftover from the pre-v0.4-starter-rework duration (3). All three legs actually agree on 1; only the comment is wrong, so a reader auditing the sheet against the constant is told to expect a mismatch that does not exist (or, worse, 'fixes' the ops line to 3).
  - `docs/kokomi-cards.yaml:117 — "# fight-1 survival math that meter 10 was buying. The `amount: 3` mirrors KURAGE_DURATION (test-pinned)."`
  - `docs/kokomi-cards.yaml:109 — "effects: [{op: summon_kurage, amount: 1}, {op: gain_charge, amount: 1}]"`
  - `tier0/constants.py:375 — "KURAGE_DURATION = 1" (comment on :379-381 records the v0.4 starter rework 3 -> 1)`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/BakeKurage.cs:57 — "new DynamicVar(\"KurageTurns\", 1m)"`
  - _No player-visible effect: sim turns=1, C# KurageTurns=1, upgrade +1 on both sides. Comment drift only._
- **[low] other** — The sheet's bake_kurage comment still describes the pulse with the retired DIVISOR grammar ('KURAGE_PULSE_BASE + Charge/KURAGE_PULSE_DIVISOR damage ... and KURAGE_PULSE_BLOCK Block'). The engine multiplies (KURAGE_PULSE_BASE + charge * KURAGE_PULSE_PER_CHARGE), KURAGE_PULSE_DIVISOR no longer exists anywhere in live code, and KURAGE_PULSE_BLOCK is 0 so the 'Block' clause describes a baseline that is off. The C# side matches the engine, not the sheet comment.
  - `docs/kokomi-cards.yaml:111-113 — "# body is replaced by a persistent summon that holds for KURAGE_DURATION turns and pulses at each turn end / # for KURAGE_PULSE_BASE + Charge/KURAGE_PULSE_DIVISOR damage, hydro application, and KURAGE_PULSE_BLOCK / # Block."`
  - `tier0/engine/effects.py:2521-2522 — "multiplier = C.KURAGE_PULSE_PER_CHARGE + amp" / "dmg = C.KURAGE_PULSE_BASE + p.charge * multiplier"`
  - `tier0/constants.py:403-409 — "KURAGE_PULSE_PER_CHARGE = 3 ... the read flips from a DIVISOR (+1 per 4 Charge) to a MULTIPLIER (+N per Charge)"`
  - `tier0/constants.py:479 — "KURAGE_PULSE_BLOCK = 0 ... v0.4 starter rework ([USER]) turned this OFF (was 2)"`
  - `klee-mod/KleeCode/Powers/KuragePowers.cs:52-54 — "PulseDamage(...) => KokomiConstants.KuragePulseBase + PulseMultiplier(owner) * KokomiResources.GetCharge(owner)"`
  - `tools/role_tempo.py:383-387 — live (non-archive) tool quotes the same stale sheet string as its bake_kurage rationale`
  - _Sheet-comment vs sim/C# documentation drift; the shipped arithmetic is in parity (base 4, x3 per Charge, block 0 + kurage_ward on both sides). Flagged because the stale string has already been copied into tools/role_tempo.py._

### kokomi:tactical_retreat
- **[low] text_ops_mismatch** — The C# description renders the discard count with a literal "card(s)" parenthetical instead of the codebase's plural directive, so the card always displays "Discard 1 random card(s)" / "Discard 2 random card(s)" even though the count is a resolved DynamicVar that the house template pluralizes.
  - `docs/kokomi-cards.yaml:122 — effects: [{op: draw, amount: 1}, {op: discard, amount: 1}] (a definite count of 1, 2 after upgrade — nothing indefinite for "(s)" to cover)`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/TacticalRetreat.cs:44 — ("description", "Draw {Cards:diff()} card{Cards:plural:|s}. Discard {Discards:diff()} random card(s).")`
  - `klee-mod/KleeCode/Cards/Generated/Crackle.cs:50 — the same "Discards" DynamicVar is rendered "Discard {Discards:diff()} card{Discards:plural:|s}", the convention this card's own first sentence also follows`
  - _Cosmetic only: the same sentence's Cards half uses {Cards:plural:|s}, so the inconsistency is internal to one line. Mechanics are unaffected — TacticalRetreat.cs:64 loops DynamicVars["Discards"].IntValue times over a kit-card-filtered hand pool with Rng.CombatTargets.NextItem, which matches tier0/engine/effects.py:1307-1339 (random default, kit cards exempt via `not c.kit_card`, re-poll the pool each iteration, break on empty hand). Draw-then-discard ordering matches the sheet's effects order on both legs. Upgrade legs agree exactly: docs/kokomi-upgrades.yaml:22 {draw: +1, discard: +1} vs TacticalRetreat.cs:76-77 Cards.UpgradeValueBy(1m) / Discards.UpgradeValueBy(1m), and both delta keys are expressible in tier0/content/upgrades.py:206-214 and :359-377. Cost 0 / Skill / Basic / TargetType.Self and the title all match docs/kokomi-cards.yaml:121._

### kokomi:waterspout
- **[low] upgrade_delta_drift** — The waterspout row in the upgrades sheet carries a stale base in its inline annotation: it reads "# 7->10" while the card's ratified base has been 10 since the v0.3 repricing, so the delta {damage: +3} actually produces 10->13 (which is what both the sim applier and the C# do). The delta VALUE is correct on all three legs; only the annotation is wrong, and it is wrong in the confusable direction — "10" is the card's unupgraded number, so the sheet's own note describes an upgraded card that is identical to the base card.
  - `docs/kokomi-upgrades.yaml:35 — `waterspout:        {damage: +3}          # 7->10, still burns itself``
  - `docs/kokomi-cards.yaml:161-162 — waterspout row with `effects: [{op: damage, amount: 10, target: enemy}]`, and the row comment at :163 `# Self-consuming swing: v0.3 7 -> 10 ...` records that the base moved off 7`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/Waterspout.cs:60 — `new DamageVar(10m, ValueProp.Move)` (base 10)`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/Waterspout.cs:82 — `DynamicVars.Damage.UpgradeValueBy(3m);` (upgraded 13, not 10)`
  - `docs/kokomi-upgrades.yaml:47-50 — the surging_shoal entry documents this exact defect class in this exact file ("The old comment here read '4->6', which had been stale since the v0.3 repricing to 7 -- two bases out of date, in the file whose whole job is to say what a card becomes"), i.e. the same v0.3 repricing pass that moved waterspout's base was already known to have left stale annotations behind`
  - _Cosmetic/documentation only — no player-visible number is wrong. The waterspout row in kokomi-cards.yaml:163 carries a `(lint-ok: v0.3 history)` marker for its own 7->10 history note; the upgrades-sheet comment has no such marker and is asserting a current fact, not history._

### kokomi:surging_shoal
- **[low] other** — The generated C# class doc comment on the Element member states Kokomi's cadence is the SKILL-grade cadence ("damaging Skills, Burst-tagged cards, and skill-tagged cards apply Hydro"), which contradicts the sheet's character-wide ruling that her cadence is CATALYST (every attack applies hydro). Runtime behaviour is correct on both legs -- this is documentation-only drift emitted by the generator for every non-Klee profile.
  - `docs/kokomi-cards.yaml:51 -- "# Element: hydro | Cadence: CATALYST (RULED R52, ask N1): every attack applies hydro"`
  - `docs/kokomi-cards.yaml:201 -- card's own note: "Catalyst cadence makes this mass hydro application"`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/SurgingShoal.cs:37 -- "/// <summary>Sheet cadence: damaging Skills, Burst-tagged cards, and skill-tagged cards apply Hydro.</summary>"`
  - `tools/gen_klee_cards.py:4838-4843 -- the else-branch that emits the skill-cadence sentence for every non-KLEE_PROFILE roster`
  - `tier0/engine/effects.py:277-279 -- catalyst branch: attack + damage op applies card.element`
  - `klee-mod/KleeCode/Powers/ElementalApplication.cs:196 -- application keys off `cardSource is IElementalCard`, with no card-type gate, so the attack does apply Hydro`
  - _Cosmetic only; no player-visible effect. Present identically on all 18 Kokomi generated elemental cards, so it is a generator-template issue rather than something specific to this card._
- **[low] sim_vs_csharp_divergence** — Ceremonial Garment's per-attack Block rider is granted at a different point in the play on the two legs: tier0 adds the Block BEFORE the card's damage resolves (explicitly, "so it is up in time for the same turn's enemy swing"), while the C# hook grants it in AfterCardPlayed, i.e. after this AoE's damage has already resolved.
  - `tier0/engine/effects.py:2258-2266 -- garment block added in the pre-resolution attack setup, before `_resolve_effects(state, card.effects, card)` at tier0/engine/effects.py:2269`
  - `klee-mod/KleeCode/Powers/KuragePowers.cs:350-361 -- `KokomiGarmentHooks.AfterCardPlayed` calls `CreatureCmd.GainBlock` only after the card play completes`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/SurgingShoal.cs:70-79 -- OnPlay resolves the all-enemies damage inside the card play, so the C# Block lands after every hit`
  - `docs/kokomi-cards.yaml:186-187 -- the card is an all_enemies attack, so it is one of the plays that trips this ordering`
  - _No observable difference for this card in isolation (both land within the player's turn, before the enemy swing, and nothing in this card reads player Block). Ordering only becomes observable with a mid-play Block reader or a thorns/retaliation effect. Reported because the sim comment makes the pre-damage placement a stated intent; it is a shared-power ordering issue, not a per-card one. Base damage 6, upgrade +2 -> 8, cost 1, Attack/Common, AllEnemies targeting and Hydro application all agree across the three legs._

### kokomi:pulsing_current
- **[low] upgrade_delta_drift** — The upgrades-sheet comment for pulsing_current states a stale base and a stale upgraded value ("6->9, snap-exact"); the card's actual base is 7, so the delta produces 7->10 in both the sheet and the C#. The delta value itself (+3) is correct and matches C#, so this is comment-only drift — the same stale-base class the file's own surging_shoal note (docs/kokomi-upgrades.yaml:40-43) records as a defect worth fixing.
  - `docs/kokomi-upgrades.yaml:45 — `pulsing_current:   {damage: +3}          # 6->9, snap-exact``
  - `docs/kokomi-cards.yaml:210 — `effects: [{op: damage, amount: 7, target: enemy}, {op: gain_charge, amount: 1}]``
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/PulsingCurrent.cs:60 — `new DamageVar(7m, ValueProp.Move)``
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/PulsingCurrent.cs:83 — `DynamicVars.Damage.UpgradeValueBy(3m);``
  - `docs/klee-cards.yaml:65 / docs/klee-upgrades.yaml:33 — snap is 6->9, so the "snap-exact" claim now holds only for the delta, not for the base/result pair`
  - _No player-visible number is wrong: sheet 7 -> C# 7, delta +3 -> C# +3 (upgraded 10 on both legs). Severity low, comment/record drift only. The sheet's own v0.3 note at docs/kokomi-cards.yaml:211-213 documents the 6->7 reprice that this comment predates._
- **[low] other** — The generated C# card carries an XML doc comment describing the SKILL cadence (Furina's: only damaging Skills / Burst-tagged / skill-tagged cards apply the element), while Kokomi's sheet and the generator's own manifest rule her cadence CATALYST (every Attack applies Hydro). Under the comment's stated rule this Attack would not apply Hydro at all; the code is correct (IElementalCard Element => Hydro plus the AppliesHydro keyword), so this is a wrong-cadence comment, not wrong behavior.
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/PulsingCurrent.cs:37 — `/// <summary>Sheet cadence: damaging Skills, Burst-tagged cards, and skill-tagged cards apply Hydro.</summary>``
  - `docs/kokomi-cards.yaml:51 — `# Element: hydro | Cadence: CATALYST (RULED R52, ask N1): every attack applies hydro``
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/manifest.json:6 — `"cadence": "CATALYST (R52 ask N1): every Attack applies Hydro. Application uptime is structural, not authored per card."``
  - `tier0/engine/effects.py:279-281 — catalyst branch: `if (card.type == "attack" and fx["op"] == "damage" and state.player.cadence == "catalyst")` returns the element`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/PulsingCurrent.cs:38 — `public Element Element => Element.Hydro;` (with CanonicalKeywords AppliesHydro at :44), i.e. behavior follows CATALYST`
  - _Systemic, not card-local: the identical line appears on all 18 elemental Kokomi generated cards (e.g. WatersEdge.cs:37, SurgingShoal.cs:37, Waterspout.cs:37), so it is a generator template string. Not player-visible; no runtime divergence found._

### kokomi:signal_arrow
- **[low] text_ops_mismatch** — The generated C# card's Element doc-comment states Kokomi's cadence as the SKILL cadence ("damaging Skills, Burst-tagged cards, and skill-tagged cards apply Hydro"), which contradicts the sheet's ruled CATALYST cadence (every Attack applies Hydro) and contradicts the card's own AppliesHydro keyword — Signal Arrow is an Attack, so under the comment's rule it would not apply Hydro at all.
  - `docs/kokomi-cards.yaml:51 ("Element: hydro | Cadence: CATALYST (RULED R52, ask N1): every attack applies hydro")`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/SignalArrow.cs:37 ("/// <summary>Sheet cadence: damaging Skills, Burst-tagged cards, and skill-tagged cards apply Hydro.</summary>")`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/manifest.json:6 (profile cadence: "CATALYST (R52 ask N1): every Attack applies Hydro")`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/SignalArrow.cs:43-44 (CanonicalKeywords => KleeKeywords.AppliesHydro)`
  - `tier0/engine/effects.py:278-280 (catalyst branch: card.type == "attack" and op == "damage" applies element)`
  - _Comment-only drift: runtime behavior is correct (Element.Hydro + IElementalCard is what ElementalApplication.cs:184 reads, so the attack does apply Hydro). Not card-specific — the same stale summary line is emitted by tools/gen_roster_cards.py on all 18 damaging Kokomi cards (AllStreamsFlow.cs:37 ... Waterspout.cs:37), so it is a generator-template defect surfacing on this card, not a hand-edit._

### kokomi:shoulder_to_shoulder
- **[high] sim_vs_csharp_divergence** — The copy is rebuilt from the CANONICAL card model in C#, so it drops the conscript discount and the per-instance Exhaust that the tier0 sim's deepcopy preserves. For the card's designed use (copying a mustered recruit), the mod's copy costs 1 more energy than the sim's at base, and in BOTH base and upgraded forms it does not Exhaust on play — so it never feeds the Charge/burst funnel and stays reusable in the discard pile.
  - `tier0/engine/effects.py:1713-1722 — `_op_copy_companion_in_hand`: `chosen = _copy.deepcopy(state.rng.choice(comps))` copies the LIVE hand instance, carrying its mutated `cost`, `exhaust=True` and `conscripted=True`; only an explicit `cost_override` overwrites the cost`
  - `tier0/engine/effects.py:2020-2027 — `_op_conscript` mutates the recruit INSTANCE: `recruit.cost = max(0, recruit.cost + C.CONSCRIPT_COST_DELTA)` (tier0/constants.py:492 = -1), `recruit.exhaust = True`, `recruit.conscripted = True``
  - `tier0/engine/refpowers.py:289-294 — the exhaust funnel reads `Card.conscripted` and pays `CHARGE_PER_EXHAUST` (+ KOKOMI_BURST_PER_EXHAUST) whenever such a card exhausts, so a sim copy of a recruit is worth Charge on play`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/ShoulderToShoulder.cs:81-87 — `var copyToken = CombatState!.CreateCard(ModelDb.GetById<CardModel>(pickedCompanion.Id), Owner);` then only `if (IsUpgraded) copyToken.EnergyCost.SetThisCombat(0);` — a fresh instance off the canonical model, with no cost delta and no ExhaustOnNextPlay at base`
  - `klee-mod/KleeCode/Powers/KokomiConscript.cs:150-164 — the discount is `recruit.EnergyCost.AddThisCombat(delta, ...)` and the Exhaust is `recruit.ExhaustOnNextPlay = true`, both explicitly INSTANCE-scoped ('mutating the canonical model would discount every future copy in the run'), i.e. exactly the state `ModelDb.GetById` cannot return`
  - `klee-mod/KleeCode/Powers/KokomiConscript.cs:161-164 is the ONLY `ExhaustOnNextPlay` assignment in the whole mod (grep over klee-mod/KleeCode), so nothing re-stamps a generated companion copy`
  - `docs/kokomi-cards.yaml:270-271 — the card row `{op: exhaust_from, amount: 1, select: chosen}, {op: copy_companion_in_hand, amount: 1}` with the sheet comment 'it whiffs with no companion in hand', i.e. the copy target is the mustered recruit`
  - _The copy-by-Id pattern is house-wide (klee-mod/KleeCode/Cards/Generated/BorrowedBrilliance.cs:67-69, klee-mod/KleeCode/Cards/Furina/Generated/EncorePerformance.cs:71-75), where it is dormant: Klee's companions in hand are unmutated deck cards and Borrowed Brilliance forces cost 0 unconditionally. It only bites on Kokomi, whose companions in hand are conscript-mutated instances. Not filed: the exhaust-selection heuristic gap (tier0 `_worst_card` at tier0/engine/effects.py:1416 vs the player prompt at ShoulderToShoulder.cs:63-67) — that is the documented deliberate divergence recorded at klee-mod/KleeCode/Powers/KokomiConscript.cs:37-51 and the sim's own 'instrument surface' comment._
- **[low] upgrade_delta_drift** — No drift: docs/kokomi-upgrades.yaml:68 `{copy_cost_override: 0}` is expressed correctly on both sides — recorded here only as the checked-and-clean upgrade leg, not as a defect (see notes).
  - `docs/kokomi-upgrades.yaml:68 — `shoulder_to_shoulder: {copy_cost_override: 0}``
  - `tier0/content/upgrades.py:491-497 — dispatch sets `hit['cost_override'] = 0` on the `copy_companion_in_hand` op, consumed at tier0/engine/effects.py:1719-1721`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/ShoulderToShoulder.cs:83-86 + :44 — `if (IsUpgraded) copyToken.EnergyCost.SetThisCombat(0);` with the text swapping via `{IfUpgraded:show:...|...}` (upgraded branch first, per klee-mod/KleeCode/Cards/Furina/Generated/RainOfRoses.cs:51)`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/manifest.json upgrades block — `no_upgrade_path: {}`, so the delta is not blocked`
  - _IGNORE FOR SCORING IF THE HARNESS COUNTS FINDINGS AS DEFECTS — this row asserts agreement, not disagreement. The only upgrade-side consequence of the real defect above is folded into finding 1 (the upgraded copy costs 0 on both legs, but still lacks Exhaust in C#)._

### kokomi:tideline_watch
- **[high] upgrade_delta_drift** — Tideline Watch+ grants and displays 8 next-turn Block instead of the sheet's 12: the C# upgrade bumps a DynamicVar that nothing reads, while OnPlay and the description both hard-code the literal 8.
  - `docs/kokomi-upgrades.yaml:75 — `tideline_watch:    {block_next_turn: +4} # 8->12 next turn; the exhaust stays exactly one card``
  - `docs/kokomi-cards.yaml:291 — `effects: [{op: exhaust_from, amount: 1, select: chosen}, {op: block_next_turn, amount: 8}]``
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/TidelineWatch.cs:78 — `DynamicVars["BlockNextTurn"].UpgradeValueBy(4m);``
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/TidelineWatch.cs:73 — `await PowerCmd.Apply<BlockNextTurnPower>(choiceContext, Owner.Creature, 8, applier: Owner.Creature, cardSource: this);` (literal 8, never reads DynamicVars["BlockNextTurn"])`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/TidelineWatch.cs:44 — description `"...At the start of your next turn, gain 8 [gold]Block[/gold]."` (literal 8, no {BlockNextTurn:diff()} token, so the upgraded face still prints 8)`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/TidelineWatch.cs:50 — `new DynamicVar("BlockNextTurn", 8m)` is declared but referenced only by OnUpgrade`
  - `tier0/content/upgrades.py:419-425 — the sim's `block_next_turn` key bumps the op's `amount`, so tier0 Tideline Watch+ really does bank 12`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/manifest.json:64 — tideline_watch is in `generated` (not `blocked`), and manifest `upgrades.no_upgrade_path` is empty, i.e. the delta is declared fully expressible`
  - _Root cause is in the generator, not hand-edits: tools/gen_klee_cards.py:3543-3545 emits `amount = str(int(eff["amount"]))` for the block_next_turn OnPlay path and :3905-3910 emits the literal into the description, while :4489 registers `DynamicVars["BlockNextTurn"]` as the upgrade target — the var has no reader. Same inert-upgrade shape is visible on the Klee-side precedent SayuDarumaGift.cs:60/73/86 (var +2, OnPlay literal 4, description literal 4), so this is systemic rather than card-specific; filed here because the sweep is per-card and the miss is player-visible on this card. Contrast with the correctly-wired plain-block path on the same character (CoralGuard.cs:52/64/70, VotiveOffering.cs:50/84/89) where OnPlay reads DynamicVars.Block and the face carries {Block:diff()}. Non-findings checked and clean: cost/type/rarity/target (kokomi-cards.yaml:290 vs TidelineWatch.cs:56); exhaust_from ordering, count, kit-card exemption and empty-hand no-op (effects.py:1382-1391 pool filter + :1400-1406 `if not pool: break` vs TidelineWatch.cs:63-71 CardSelectCmd.FromHand + KitGrant.NotKitCard); next-turn payout timing after the block reset (effects.py:2344-2350 pop vs CompanionPowers.cs:461-466 AfterBlockCleared); absence of SpotlightSystem.PrintedBlock is correct since spotlight_capable is companion/Furina-only (gen_klee_cards.py:2897) and spotlight_mult returns 1.0 for non-spotlighted cards (effects.py:333-334). The sim's `select: chosen` auto-pick via _worst_card (effects.py:1416-1422) vs the C# player prompt is a declared pilot heuristic/instrument surface, not a divergence._

### kokomi:scattering_spray
- **[low] other** — The generated C# class carries FURINA's cadence sentence as its XML doc comment on the Element property, contradicting Kokomi's ruled CATALYST cadence (and Kokomi's own generator manifest profile). Comment-only drift — runtime application is driven by IElementalCard.Element regardless of card type, so behavior is correct; the documentation on the file is not.
  - `docs/kokomi-cards.yaml:51 — "# Element: hydro | Cadence: CATALYST (RULED R52, ask N1): every attack applies hydro"`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/ScatteringSpray.cs:37 — "/// <summary>Sheet cadence: damaging Skills, Burst-tagged cards, and skill-tagged cards apply Hydro.</summary>"`
  - `klee-mod/KleeCode/Cards/Furina/Generated/manifest.json (profile.cadence) — "damage on Skill, skill_tag, or burst_tag cards applies Hydro; plain Attacks do not" — the rule the comment actually states`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/manifest.json (profile.cadence) — "CATALYST (R52 ask N1): every Attack applies Hydro." — what the comment should state`
  - `klee-mod/KleeCode/Powers/ElementalApplication.cs:196-203 — application reads `cardSource is IElementalCard elemental ? elemental.Element` with no card-type gate, so this Attack does apply Hydro despite the comment`
  - _Not card-specific: the identical sentence appears on all 18 elemental Kokomi generated cards (grep "Sheet cadence" under klee-mod/KleeCode/Cards/Kokomi/Generated), i.e. a codegen template that emits Furina's cadence string for Kokomi. Filed here because it is present on this card's file; the fix is repo-wide, not per-card._

### kokomi:ebb_tide
- **[low] text_ops_mismatch** — The unupgraded card face reads "Exhaust 1 cards from your hand." — a hardcoded plural on a value that is 1 at base. Because ebb_tide is the only card whose exhaust count is upgradeable, the description emitter substitutes the dynamic var "{Exhausts:diff()}" and its plural test (`plural = "" if str(n) == "1" else "s"`) can never match, so the plural is pinned to "s" while the printed number is 1. The repo already has the correct idiom for dynamic counts (`card{Cards:plural:|s}`), and the static-count siblings render correctly ("Exhaust 1 card" / "Exhaust 2 cards").
  - `docs/kokomi-cards.yaml:321 — effects: [{op: discard, amount: 1}, {op: exhaust_from, amount: 1, select: chosen}] (base exhaust count = 1)`
  - `docs/kokomi-upgrades.yaml:80 — ebb_tide: {exhaust: +1}  # exhaust 1 -> 2 CHOSEN cards (so base face must read "1 card")`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/EbbTide.cs:44 — ("description", "Discard a random card. [gold]Exhaust[/gold] {Exhausts:diff()} cards from your hand.")`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/EbbTide.cs:50 — new DynamicVar("Exhausts", 1m) (renders as 1 unupgraded)`
  - `tools/gen_klee_cards.py:4299-4306 — n = "{Exhausts:diff()}" if exhaust_upgrade(card) ... plural = "" if str(n) == "1" else "s" (never "1" on the dynamic branch)`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/CommunionOfTides.cs:44 and MoonSignal.cs:44 — the repo's correct dynamic-plural idiom: "card{Cards:plural:|s}"`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/VotiveOffering.cs:44 ("Exhaust 1 card") vs CleansingTide.cs:44 ("Exhaust 2 cards") — static branch pluralizes correctly`
  - _Cosmetic/grammar only; the number itself and the behavior are correct. Upgraded face ("Exhaust 2 cards") reads correctly._

### kokomi:tideturn
- **[low] other** — The generated XML doc comment on Tideturn's Element property states Furina's SKILL cadence rule ("damaging Skills, Burst-tagged cards, and skill-tagged cards apply Hydro"), which contradicts Kokomi's ruled CATALYST cadence (every attack applies hydro) and contradicts the card's own AppliesHydro keyword nine lines below it. Behavior is correct — the comment is drift from the shared codegen template (it is verbatim identical on Furina's generated cards, where it is accurate).
  - `docs/kokomi-cards.yaml:51 — "# Element: hydro | Cadence: CATALYST (RULED R52, ask N1): every attack applies hydro"`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/Tideturn.cs:37 — "/// <summary>Sheet cadence: damaging Skills, Burst-tagged cards, and skill-tagged cards apply Hydro.</summary>"`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/Tideturn.cs:43-44 — CanonicalKeywords => new[] { KleeKeywords.AppliesHydro } on a CardType.Attack`
  - `klee-mod/KleeCode/Cards/Furina/Generated/FloodOfEmotion.cs:37 — identical comment text on the skill-cadence roster, showing the line is a shared template constant`
  - `tier0/engine/effects.py:278-280 — catalyst branch: card.type == "attack" and fx["op"] == "damage" -> applies card/player element`
  - _Comment-only; not player-visible. Template-wide across all klee-mod/KleeCode/Cards/Kokomi/Generated/*.cs (18 files carry the same line), not specific to this card._

### kokomi:all_streams_flow
- **[low] text_ops_mismatch** — The generated Kokomi attack carries a doc-comment stating Furina's SKILL-grade cadence rule ("damaging Skills, Burst-tagged cards, and skill-tagged cards apply Hydro"), which contradicts the sheet-ruled CATALYST cadence for Kokomi (every Attack applies Hydro). Comment-only: the emitted code (Element.Hydro + KleeKeywords.AppliesHydro) and the sim both apply Hydro on this Attack, so no player-visible number moves.
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/AllStreamsFlow.cs:37`
  - `docs/kokomi-cards.yaml:51`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/manifest.json:6`
  - `tier0/engine/effects.py:278-280`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/AllStreamsFlow.cs:38`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/AllStreamsFlow.cs:43-44`
  - _Root is generator-wide, not hand-edited: tools/gen_klee_cards.py:4833-4843 branches only on KLEE_PROFILE and the else-branch hardcodes the Furina sentence, so every generated Kokomi elemental card (e.g. NereidsAscension.cs:36) carries the same wrong cadence text._
- **[low] text_ops_mismatch** — The card's own Charge rate (sheet: bonus_formula 1_per_2_charge) is displayed on no surface. The face keeps only the Track L-C marker "Scales with [gold]Charge[/gold]." on the promise that the rate "moves to the hover tip", but rider_tip_args recognizes only fanfare / salon_member / companion formulas, so no charge rate tip is emitted and the card ships with the marker and no rate anywhere.
  - `docs/kokomi-cards.yaml:366`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/AllStreamsFlow.cs:54`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/AllStreamsFlow.cs:46-47`
  - `tools/gen_klee_cards.py:3995-3999`
  - `tools/gen_klee_cards.py:1667-1674`
  - `klee-mod/KleeCode/Cards/Furina/Generated/Crescendo.cs:41`
  - _Arithmetic itself is correct and honest on the face (CalculatedDamage renders 5 + Charge/2), so this is a display-policy gap, not a wrong number. Same gap on the sibling reader NereidsAscension.cs:47. KokomiRiderTips.cs:14-18 argues Kokomi only needs tips for reads that cannot render in the face, which is the likely intent, but Furina's converted riders render in the face too and still get the rate tip._
- **[low] text_ops_mismatch** — While the Ceremonial Garment is up, the only on-screen text stating a "1 per 2 Charge" rate for this card is the Garment tip, which ends with "Not included in the number above." Because the card's OWN identically-rated 1-per-2-Charge rider is unnamed on the face (see previous finding), the tip's disclaimer is readable as saying this card's Charge scaling is excluded from the printed number, when in fact the printed number already includes it and the Garment bonus is a second, separate addend.
  - `klee-mod/KleeCode/Cards/KokomiRiderTips.cs:103-109`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/AllStreamsFlow.cs:46-47`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/AllStreamsFlow.cs:54`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/AllStreamsFlow.cs:60-62`
  - `tier0/engine/effects.py:526-527`
  - `tier0/engine/effects.py:2323-2325`
  - _Both legs agree that the two riders stack additively: the sim adds the card rider in _op_damage (effects.py:526-527) and the Garment rider separately through flat_attack_bonus (effects.py:2323-2325), matching the C# split between CalculatedDamage and CeremonialGarmentPower.ChargeBonus (KuragePowers.cs:295-321). The tip is factually accurate; the hazard is ambiguity created by the missing rate label on the card's own rider._

### kokomi:reinforcements
- **[medium] text_ops_mismatch** — The Muster keyword tooltip attached to Reinforcements defines Muster N as transforming N cards out of the player's hand, but this card's conscript op runs in create mode and consumes nothing from hand — so the hovered rules text describes a net -1 card play where the ops deliver net +1, the card's entire designed identity.
  - `docs/kokomi-cards.yaml:378 — effects: [{op: exhaust_from, amount: 1, select: chosen}, {op: conscript, amount: 2, mode: create}] (sheet comment at 379-380 calls it the kickoff §1.4 sample 'Exhaust 1, create 2': net +1 card)`
  - `tier0/engine/effects.py:2027-2029 — in create mode `_add_token(state, recruit, "hand")` then `continue`: the victim-selection block below (2030-2038) is never reached, so no hand card is transformed and nothing is 'chosen'`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/Reinforcements.cs:41 — ExtraHoverTips => KokomiRiderTips.ForMuster(base.ExtraHoverTips, this) (the generic keyword tip is attached unconditionally, create mode included)`
  - `klee-mod/KleeCode/Cards/KokomiRiderTips.cs:67-70 — tip body: "[gold]Muster N[/gold]: transform N cards in your hand into random Inazuma [gold]Companion[/gold] cards. Each costs {cheaper} less and [gold]Exhausts[/gold]. Kit cards and Companions you already hold are never chosen."`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/Reinforcements.cs:48 — face text "[gold]Exhaust[/gold] 1 card from your hand. [gold]Muster[/gold] 2, adding the units to your hand." — the deviation clause states only WHERE the units land, never that the transform is skipped`
  - `klee-mod/KleeCode/Powers/KokomiConscript.cs:68-73 — createMode branch calls AddGeneratedCardToCombat(PileType.Hand) and continues, bypassing the Eligible()/CardSelectCmd transform path at 83-101, confirming the C# behaviour matches the sim and not the tooltip`
  - _Reinforcements is the pool's only create-mode conscript (grep 'mode: create' in docs/kokomi-cards.yaml returns line 378 only; grep 'createMode: true' under klee-mod/KleeCode/Cards returns Reinforcements.cs:77 only), so the shared keyword definition is never otherwise exercised against create mode. The generator authors this deliberately (tools/gen_klee_cards.py:2780-2790, 'The deviation is WHERE the units land, not what they are'), but the tooltip's 'transform N cards in your hand' and 'Kit cards and Companions you already hold are never chosen' are both false on this card. Held at medium rather than high because the face's own deviation clause partially patches the destination; the contradiction and the 2-card delta misstatement remain player-visible. Everything else on this card is three-way clean: cost 2 (yaml:377 / Reinforcements.cs:60), exhaust_from 1 chosen + kit-card exemption (effects.py:1388-1400 vs Reinforcements.cs:67-75), conscript amount 2 and costOverride null (effects.py:2020-2026 vs KokomiConscript.cs:151-158, CONSCRIPT_COST_DELTA -1 in tier0/constants.py:492 == KokomiResources.cs:116), full-hand overflow to discard (effects.py:485-488 vs DECISIONS.md:870), and the upgrade delta {cost: -1} (kokomi-upgrades.yaml:50) == EnergyCost.UpgradeBy(-1) (Reinforcements.cs:82)._

### kokomi:pearl_barrage
- **[low] upgrade_delta_drift** — The pearl_barrage upgrade comment states the upgraded card as "3 + 2/exhausted card", but the base has been 5 since v0.3, so the upgraded card is 5 + 2/exhausted card. The delta key itself ({formula_per: +1}) is correct and matches the C#; only the stated result is stale — the same class of defect this file already flags on surging_shoal ("two bases out of date, in the file whose whole job is to say what a card becomes", docs/kokomi-upgrades.yaml:44-46).
  - `docs/kokomi-upgrades.yaml:52 — `pearl_barrage:     {formula_per: +1}     # 3 + 2/exhausted card (gleeful_barrage-class scaling bump)``
  - `docs/kokomi-cards.yaml:387 — `effects: [{op: damage, amount_formula: {base: 5, per: 1, count: exhaust_pile}, target: enemy}]``
  - `docs/kokomi-cards.yaml:388 — `# Ashen-Strike rail: 5 + 1 per exhausted card (v0.3: base 3 -> 5 ...)``
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/PearlBarrage.cs:60 — `new CalculationBaseVar(5m),``
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/PearlBarrage.cs:84 — `DynamicVars.ExtraDamage.UpgradeValueBy(1m);` (matches formula_per +1: 1 -> 2)`
  - _Comment-only drift; no player-visible number is wrong. Base (5) and slope (1 -> 2 on upgrade) agree across all three legs: sheet base 5/per 1, C# CalculationBaseVar(5m)/ExtraDamageVar(1m) with OnUpgrade +1, tier0 _calc_amount = base + per * count._
- **[low] other** — The tier0 suite documents pearl_barrage as having no floor — "deals only `N per exhausted card`, so at an empty pile it deals nothing and is scaling ONLY" — which is false against the op both the sheet and the C# implement: base 5 means it deals 5 with an empty exhaust pile. The scaling-only tag survives only because the classifier's pays-at-zero test requires a literal `amount` key and never inspects `amount_formula.base`, so a formula base is invisible to it.
  - `tier0/tests/test_role_tempo_coverage.py:263-265 — "`pearl_barrage` deals only `N per exhausted card`, so at an empty pile it deals nothing and is scaling ONLY."`
  - `docs/kokomi-cards.yaml:387 — `amount_formula: {base: 5, per: 1, count: exhaust_pile}` with `solve: [scaling]` at docs/kokomi-cards.yaml:386`
  - `tier0/engine/effects.py:216-218 — `return (formula.get("base", 0) + formula.get("per", 1) * _runtime_count(...))` → 5 at len(exhaust_pile)==0`
  - `tools/role_tempo.py:583-586 — `pays_at_zero = (not gated and isinstance(fx.get("amount"), (int, float)) and fx["amount"] > 0)` (never reads amount_formula.base)`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/PearlBarrage.cs:60-62 — CalculationBaseVar(5m) + ExtraDamageVar(1m) × ExhaustPileCount → 5 on an empty pile`
  - _Empty-pile edge case: sim and C# agree with each other (both deal 5 at zero pile — tier0 effects.py:216 vs KokomiResources.cs:208-213 returning 0 for an empty/absent pile), so this is not a sim-vs-C# divergence. The defect is an internal-documentation/tagging claim contradicting the op it describes; it also affects the solve-coverage lint's view of the card. No player-visible number is wrong._

### kokomi:exposing_current
- **[low] other** — The generated C# card carries Furina's SKILL-cadence doc comment verbatim, which states the opposite of Kokomi's ruled CATALYST cadence. Comment-only: the emitted behavior (Element.Hydro + KleeKeywords.AppliesHydro on a type:attack card) is catalyst-correct, so no player-visible effect.
  - `docs/kokomi-cards.yaml:51 — "# Element: hydro | Cadence: CATALYST (RULED R52, ask N1): every attack applies hydro"`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/ExposingCurrent.cs:37 — "/// <summary>Sheet cadence: damaging Skills, Burst-tagged cards, and skill-tagged cards apply Hydro.</summary>"`
  - `docs/furina-cards.yaml:13 — the SKILL-grade cadence line the C# summary paraphrases ("plain attacks never do"), i.e. the wrong character's rule`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/ExposingCurrent.cs:39 — Element => Element.Hydro, and :44 CanonicalKeywords includes KleeKeywords.AppliesHydro on a CardType.Attack (:68), which is the catalyst behavior the sheet actually asks for`
  - _Generator-wide, not card-specific: the identical summary appears at line 37 of every Kokomi generated card (AllStreamsFlow, WatersEdge, Waterspout, ... ) as well as Furina's, so the fix belongs in the generator's doc-comment template. Reported once here for this card's leg._

### kokomi:read_the_current
- **[low] other** — The generated C# card's XML doc comment on the Element member states Kokomi's SKILL-grade cadence ("damaging Skills, Burst-tagged cards, and skill-tagged cards apply Hydro"), contradicting the sheet's character-wide CATALYST ruling (every attack applies hydro) that this card — an Attack — actually runs under. Comment-only drift: the runtime behaviour is correct (IElementalCard + BeforeDamageReceived tags every powered card hit, and tier0 _element_for takes the catalyst branch for attack+damage), and the card's own manifest profile states CATALYST. The generator hardcodes a two-branch comment (Klee = catalyst wording, everything else = Furina's skill wording), so Kokomi falls into the wrong branch.
  - `docs/kokomi-cards.yaml:51 — "Element: hydro | Cadence: CATALYST (RULED R52, ask N1): every attack applies hydro"`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/ReadTheCurrent.cs:37 — "/// <summary>Sheet cadence: damaging Skills, Burst-tagged cards, and skill-tagged cards apply Hydro.</summary>"`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/manifest.json:6 — "cadence": "CATALYST (R52 ask N1): every Attack applies Hydro."`
  - `tier0/engine/effects.py:278-280 — catalyst branch: card.type == "attack" and fx["op"] == "damage" -> applies element`
  - `tools/gen_klee_cards.py:4838-4842 — non-Klee profiles emit the skill-cadence sentence unconditionally`
  - _Not player-visible (source comment only), and it is generator-wide across all 18 elemental Kokomi generated cards, not specific to this card. Reported because the sheet header cadence rule is exactly the kind of character-wide law the other legs must honor in what they claim._

### kokomi:quiet_harbor
- **[low] upgrade_delta_drift** — The quiet_harbor row in the upgrades sheet annotates its delta as 'played 6->9', but the card's printed Block is 5 on the design sheet and 5 in C#, so the +3 delta actually produces 5->8. The delta value itself is correct and consistent on both sides; only the stated before/after numbers in the comment are wrong (base has been 5 in every revision of the card sheet per git history).
  - `docs/kokomi-upgrades.yaml:116 — quiet_harbor:      {block: +3}           # played 6->9; the Sly draw stays 2 (header gap note)`
  - `docs/kokomi-cards.yaml:473 — effects: [{op: block, amount: 5}]`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/QuietHarbor.cs:50 — new BlockVar(5m, ValueProp.Move)`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/QuietHarbor.cs:67 — DynamicVars.Block.UpgradeValueBy(3m)`
  - _Same defect class the file itself calls out for surging_shoal at docs/kokomi-upgrades.yaml:40-43 ('two bases out of date, in the file whose whole job is to say what a card becomes'). No player-visible number is wrong: sheet, tier0 applier (tier0/content/upgrades.py:165-167, 'block' bumps the first block op in card.effects only) and C# all land on 8. Cosmetic/documentation drift only._

### kokomi:driftglass
- **[medium] sim_vs_csharp_divergence** — The Sly hit collects the Ceremonial Garment Charge bonus in the C# mod but not in tier0. In C#, CeremonialGarmentPower.ModifyDamageAdditive keys off the damage's cardSource being a CardType.Attack, and the Sly hit is dealt with FromCard(this) where `this` is Driftglass (an Attack), so it gains Charge/2 extra damage. In tier0 the Garment bonus is computed only in resolve_card and stashed in state.current_attack_bonus for the card BEING PLAYED; Kokomi's authored sly list is resolved inline at the discard site (_resolve_effects, not a card play), so the 5-damage Sly hit reads the DISCARDING card's bonus instead of Driftglass's — 0 whenever the discard outlet is a Skill, which is every discard outlet in her pool. Driftglass is the only damaging Sly branch on the sheet, so this is unique to this card.
  - `docs/kokomi-cards.yaml:478 (sly: [{op: damage, amount: 5, target: random_enemy}])`
  - `tier0/engine/effects.py:1354-1356 (sly resolved via _resolve_effects at the discard site, not a card play)`
  - `tier0/engine/effects.py:2251 and 2267 (flat_attack_bonus computed and stored in state.current_attack_bonus only in resolve_card)`
  - `tier0/engine/effects.py:2324-2325 (Garment term: bonus += p.charge // GARMENT_CHARGE_DIVISOR, inside flat_attack_bonus)`
  - `tier0/engine/effects.py:541 (base += state.current_attack_bonus — the Sly hit reads the outer card's value)`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/Driftglass.cs:90-94 (DamageCmd.Attack(5m).FromCard(this) in AfterCardDiscarded)`
  - `klee-mod/KleeCode/Powers/KuragePowers.cs:313-320 (ModifyDamageAdditive gates only on cardSource Type == Attack, then adds Charge/GarmentChargeDivisor)`
  - `tier0/constants.py:366 and klee-mod/KleeCode/Powers/KokomiResources.cs:115 (divisor 2 on both sides — the gap is presence, not rate)`
  - _Only the DAMAGE half diverges. The Garment's 2 Block rider matches: tier0 grants it in the card-play path (effects.py:2262-2264) and C# grants it in KokomiGarmentHooks.AfterCardPlayed (KuragePowers.cs:352-360), so neither pays it on a discard. Hydro application also matches: tier0 _element_for gives the Sly hit Hydro (attack + damage + catalyst, effects.py:278-280) and C# applies it off IElementalCard on any powered attack from the card (ElementalApplication.cs:196-201)._
- **[low] other** — Driftglass.cs's Element doc comment states Furina's SKILL cadence rule, not Kokomi's ruled CATALYST cadence. The sheet header rules that every Kokomi attack applies Hydro; the generated comment says only damaging Skills, Burst-tagged and skill-tagged cards do — which, if believed, says this Attack applies nothing. The behavior is correct (Element => Element.Hydro, applied to any powered attack from the card); only the comment is wrong. Generator-side: the non-Klee branch emits the Furina string unconditionally, so all 18 Kokomi generated cards carry it.
  - `docs/kokomi-cards.yaml:51 (Element: hydro | Cadence: CATALYST ... every attack applies hydro)`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/Driftglass.cs:37 ("Sheet cadence: damaging Skills, Burst-tagged cards, and skill-tagged cards apply Hydro.")`
  - `tools/gen_klee_cards.py:4835-4842 (KLEE_PROFILE gets the catalyst string; the else branch hardcodes the skill-cadence string for every other profile)`
  - `tier0/engine/effects.py:278-280 (catalyst branch: card.type == attack and op == damage applies the element)`
  - _Cosmetic XML doc comment, not player-visible; roster-wide rather than card-specific. Recorded because it is a generator template bug, not authored text._

### kokomi:undertow
- **[low] other** — Undertow.cs's Element doc comment states the SKILL-grade cadence ("damaging Skills, Burst-tagged cards, and skill-tagged cards apply Hydro"), which contradicts Kokomi's ruled CATALYST cadence ("every attack applies hydro"). The comment is copied from the Furina/skill-cadence branch of the generator and, read literally, says this Attack does NOT auto-apply Hydro. Behaviour is unaffected — the card declares Element.Hydro + KleeKeywords.AppliesHydro and ElementalApplication applies an aura on any powered attack from an IElementalCard — so this is comment drift only, and it is generator-wide (all 18 Kokomi attack cards carry the identical wrong line).
  - `docs/kokomi-cards.yaml:51 — "# Element: hydro | Cadence: CATALYST (RULED R52, ask N1): every attack applies hydro"`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/manifest.json:6 — "cadence": "CATALYST (R52 ask N1): every Attack applies Hydro."`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/Undertow.cs:37 — "/// <summary>Sheet cadence: damaging Skills, Burst-tagged cards, and skill-tagged cards apply Hydro.</summary>"`
  - `tools/gen_klee_cards.py:4838-4841 — the non-Klee else-branch emits that skill-cadence string for every elemental character, Kokomi included`
  - _Cosmetic/comment only; the CanonicalKeywords (Undertow.cs:43-44) and ElementalApplication.cs:196 path give catalyst-correct behaviour matching tier0/engine/effects.py:278-280._

### kokomi:pearl_current
- **[low] other** — The pearl_current upgrade delta's justifying comment cites a parity that does not exist: it takes {power_amount: +2} "(mercy_of_the_deep-parity slope)", but mercy_of_the_deep — the same cost-1 uncommon Power with the same base-3 power stack and the same solve:[block] — takes {power_amount: +1}. The mined delta grammar also puts base 1-3 power stacks at +1. All three legs agree on the shipped number (3 -> 5), so no player-visible value is wrong; only the stated rationale is self-contradicted by the file it cites.
  - `/home/user/GItS/docs/kokomi-upgrades.yaml:123 — pearl_current: {power_amount: +2}    # metallicize 3->5 (mercy_of_the_deep-parity slope)`
  - `/home/user/GItS/docs/kokomi-upgrades.yaml:51 — mercy_of_the_deep: {power_amount: +1}    # feel_no_pain 3->4`
  - `/home/user/GItS/docs/kokomi-cards.yaml:500-501 vs /home/user/GItS/docs/kokomi-cards.yaml:382-383 — both cost 1, type power, rarity uncommon, solve [block], base amount 3`
  - `/home/user/GItS/docs/upgrade-conventions.md:8 — "Power stacks: +1 at base 1-3, +2 at base 4-6."`
  - `/home/user/GItS/klee-mod/KleeCode/Cards/Kokomi/Generated/PearlCurrent.cs:67 — DynamicVars["PowerAmount"].UpgradeValueBy(2m) (C# faithfully implements the sheet's +2)`
  - _Comment/rationale drift only, filed under 'other' because the upgrade_delta_drift family is defined as sheet-vs-C# disagreement and here the sheet and C# agree (3 -> 5 both sides). Adjacent context, not filed: docs/kokomi-upgrades.yaml:124 (before_sun_and_moon) explicitly contrasts itself with "the +2 pearl_current takes", so the +2 is a deliberate authored value even though the cited parity partner is +1._

### kokomi:the_tide_remembers
- **[low] other** — The generated C# doc comment on TheTideRemembers' Element member states Kokomi's cadence as the Furina 'skill-grade' rule (only damaging Skills / Burst-tagged / skill-tagged cards apply Hydro), which is the opposite of the sheet's ruled CATALYST cadence for Kokomi (every Attack applies Hydro). The card is an Attack, so the comment describes a rule under which this card would apply no element at all. Runtime behavior is correct (Element.Hydro is returned and ElementalApplication tags any powered attack), so this is comment-only drift.
  - `docs/kokomi-cards.yaml:51-52 -- 'Element: hydro | Cadence: CATALYST (RULED R52, ask N1): every attack applies hydro'`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/TheTideRemembers.cs:37 -- '/// <summary>Sheet cadence: damaging Skills, Burst-tagged cards, and skill-tagged cards apply Hydro.</summary>'`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/manifest.json:6 -- '"cadence": "CATALYST (R52 ask N1): every Attack applies Hydro..."'`
  - `tools/gen_klee_cards.py:4834-4843 -- the emitter special-cases only KLEE_PROFILE, so every non-Klee profile (Furina and Kokomi alike) receives the skill-cadence string`
  - `tier0/engine/effects.py:278-280 -- catalyst branch: card.type == 'attack' and op == 'damage' applies the character element`
  - _Systemic: the identical string appears on all 18 Kokomi generated cards (AllStreamsFlow.cs:37, DepthsJudgment.cs:37, ... Waterspout.cs:37), so it is a generator template leak rather than a per-card edit. Not player-visible._

### kokomi:ceremonial_garment
- **[low] other** — The C# CeremonialGarmentPower doc-comment asserts that Nereid's Ascension also enters the Garment state; neither the sheet's nereids_ascension effects list nor the generated C# card does anything of the kind.
  - `klee-mod/KleeCode/Powers/KuragePowers.cs:243-245 — "The Ceremonial Garment: her Burst's state (kit card <see cref=\"Cards.Kokomi.CeremonialGarment\"/>; Nereid's Ascension enters it too)."`
  - `docs/kokomi-cards.yaml:532-533 — nereids_ascension effects are only [{op: damage, amount: 12, target: all_enemies, bonus_formula: 1_per_2_charge}]; no apply_power ceremonial_garment`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/NereidsAscension.cs:72-79 — OnPlay is a bare DamageCmd.Attack; no PowerCmd.Apply<CeremonialGarmentPower>`
  - `klee-mod/KleeCode/Powers/KuragePowers.cs:289,356 + klee-mod/KleeCode/Cards/Kokomi/CeremonialGarment.cs:117 — the only three references to CeremonialGarmentPower in the whole mod are IsUp, the block hook, and the kit card's own Apply`
  - _Comment-only drift; no runtime behaviour differs between legs. Flagged because it is a false statement about this card's power in the file that is the power's documentation of record, and it names a second entry point a reader would go looking for._
- **[low] other** — The ceremonial_garment sheet comment still prints the pre-v0.4 meter size ("Meter 10", "Two bake plays fill it"), while the character sheet, tier0 and the C# constant bridge all carry burst_max 20 — so the row that explains what the meter costs states half the real cost.
  - `docs/kokomi-cards.yaml:527-529 — "Cost 0: the charged meter IS the cost (Klee/Furina precedent). Meter 10 (v0.3, PROPOSED — the pass's decisive lever...) ... Two bake plays fill it."`
  - `tier0/content/characters/kokomi.yaml:25 — "burst_max: 20            # v0.4 O4 salvage (PROPOSED, plan §1.2): 10 -> 20."`
  - `klee-mod/KleeCode/Powers/KokomiResources.cs:117 — public const int BurstMax = 20;`
  - `klee-mod/KleeCode/Powers/KokomiResources.cs:52 — bridge table row "| BurstMax | characters/kokomi.yaml burst_max: 20 |"`
  - `tier0/constants.py:69 — BURST_PER_SKILL_TAG = 5, so two bake_kurage plays yield 10, not a full meter`
  - _The (lint-ok: engine constants, not this row) marker on docs/kokomi-cards.yaml:529 covers the particle-rate figures, not the "Meter 10" claim on line 527 or the "Two bake plays fill it" arithmetic. Executable legs are in full agreement at 20; this is prose drift only. Note also that docs/kokomi-cards.yaml:519 ("burst_max UNTOUCHED") is true of R74 and is not itself the defect._

### kokomi:nereids_ascension
- **[low] upgrade_delta_drift** — The upgrades-sheet inline comment for nereids_ascension still describes the pre-v0.3 base: it reads "10->14 all" while the card row prints 12 and both the C# and tier0 legs agree on 12 (upgraded 16). The delta value itself (+4) is correct on every leg; only the stated before/after pair is stale.
  - `docs/kokomi-upgrades.yaml:136 — `nereids_ascension: {damage: +4}          # 10->14 all; the 1-per-2-Charge read never moves (resource-curve law)``
  - `docs/kokomi-cards.yaml:533 — `effects: [{op: damage, amount: 12, target: all_enemies, bonus_formula: 1_per_2_charge}]}``
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/NereidsAscension.cs:60 — `new CalculationBaseVar(12m),``
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/NereidsAscension.cs:84 — `DynamicVars.CalculationBase.UpgradeValueBy(4m);``
  - `tier0/tests/test_kokomi.py:314 — `assert hp0 - e.hp == 12 + 10 // 2      # v0.3 base 12``
  - _Exactly the failure mode the same file calls out one screen earlier for surging_shoal (docs/kokomi-upgrades.yaml:64-66: "two bases out of date, in the file whose whole job is to say what a card becomes"). Not player-visible: the upgraded card really reads 12->16 on both implementation legs._
- **[low] other** — The design sheet's own worked example for this card is stale against the row directly above it: it says a banked 20 Charge yields "20-to-all", which is base 10 + 20/2. At the printed base 12 the correct worked value is 22-to-all.
  - `docs/kokomi-cards.yaml:535 — `# rate limit ships: Rare, Exhaust (which is itself one more Charge), cost 2. At a banked 20 Charge: 20-to-all, (lint-ok: banked-Charge worked example)``
  - `docs/kokomi-cards.yaml:533 — `effects: [{op: damage, amount: 12, target: all_enemies, bonus_formula: 1_per_2_charge}]}``
  - `tier0/engine/effects.py:100-103 — charge branch of `_bonus_formula`: `return int(n) * (state.player.charge // int(m))`, i.e. 12 + 20//2 = 22`
  - _Same base-10 era as the upgrades comment above, so the two stale comments corroborate each other. The `lint-ok` marker suppresses the number-in-comment lint on the grounds that it is a worked example; it does not make the example arithmetic correct._
- **[low] other** — The generated C# class carries a cadence doc-comment describing Furina's SKILL cadence ("damaging Skills, Burst-tagged cards, and skill-tagged cards apply Hydro") on a Kokomi Attack whose ruled cadence is CATALYST (every Attack applies Hydro). The comment contradicts both the sheet header and the generator's own manifest profile.
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/NereidsAscension.cs:37 — `/// <summary>Sheet cadence: damaging Skills, Burst-tagged cards, and skill-tagged cards apply Hydro.</summary>``
  - `docs/kokomi-cards.yaml:51 — `# Element: hydro | Cadence: CATALYST (RULED R52, ask N1): every attack applies hydro``
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/manifest.json — profile.cadence: "CATALYST (R52 ask N1): every Attack applies Hydro. Application uptime is structural, not authored per card."`
  - `tier0/engine/effects.py:279-280 — catalyst branch: `if (card.type == "attack" and fx["op"] == "damage" and state.player.cadence == "catalyst")` returns hydro`
  - _Behaviour is correct on both implementation legs — the card declares KleeKeywords.AppliesHydro (NereidsAscension.cs:43-44) and Element.Hydro, matching tier0's catalyst branch. This is a generator-template string copied from the Furina emitter (identical line at klee-mod/KleeCode/Cards/Furina/Generated/FloodOfEmotion.cs:37) and it lands on all 18 generated Kokomi cards, so it is template-wide rather than specific to this card._

### kokomi:vigil_of_the_deep
- **[high] sim_vs_csharp_divergence** — The ward's prevention is applied BEFORE Block in C# (an additive damage modifier) but AFTER Block in tier0, so partially-blocked hits leave different Block and different HP on the board.
  - `/home/user/GItS/tier0/engine/combat.py:658-661 — `blocked = min(state.player.block, dmg); state.player.block -= blocked; ... prevented = effects.prevent_damage_exhaust(state, dmg - blocked)` (ward reads only the UNBLOCKED residual, after Block has already been spent)`
  - `/home/user/GItS/tier0/engine/effects.py:2069 — `prevented = min(incoming, stacks)` where incoming is `dmg - blocked``
  - `/home/user/GItS/klee-mod/KleeCode/Powers/KuragePowers.cs:462-471 — `ModifyDamageAdditive(... amount ...) { ... return -Math.Min(amount, Amount); }`, with the comment at :468-470 conceding 'the engine applies Block after additive modifiers'`
  - `/home/user/GItS/docs/kokomi-cards.yaml:544 — note: "first unblocked hit each turn: prevent up to 6"`
  - _Worked example, ward 6, Block 8, incoming 10: tier0 spends all 8 Block, prevents the residual 2, HP -0, Block left 0. C# reduces 10 to 4 first, Block absorbs 4, HP -0, Block left 4. A second 10-damage hit in the same turn then lands for 10 in the sim and 6 in the mod. The C# comment claims parity with the sim's post-Block read but the code implements a pre-Block read._
- **[high] sim_vs_csharp_divergence** — On a hit that Block fully absorbs, the C# ward still burns its once-per-turn latch and Exhausts a random draw-pile card (and thereby banks Charge); tier0 does not proc at all.
  - `/home/user/GItS/tier0/engine/effects.py:2058-2061 — `stacks = p.powers.get(...); if (stacks <= 0 or incoming <= 0 or state.prevention_used_this_turn): return 0` with incoming == `dmg - blocked` from /home/user/GItS/tier0/engine/combat.py:661, so a fully-blocked hit passes 0 and the ward neither latches nor exhausts`
  - `/home/user/GItS/klee-mod/KleeCode/Powers/KuragePowers.cs:445-453 — `BeforeDamageReceived(... decimal amount ...) { if (target == Owner) _incomingThisHit = amount; }` captures the RAW incoming, with no Block awareness`
  - `/home/user/GItS/klee-mod/KleeCode/Powers/KuragePowers.cs:486-511 — `var incoming = _incomingThisHit; ... if (target != Owner || _usedThisTurn || incoming <= 0) return; ... _usedThisTurn = true; ... await CardCmd.Exhaust(choiceContext, victim);``
  - `/home/user/GItS/klee-mod/KleeCode/Cards/Kokomi/Generated/VigilOfTheDeep.cs:44 — description promises the proc on "the first time you would take unblocked attack damage each turn"`
  - _Player-visible: a card leaves the draw pile and the once-per-turn window is spent on a hit that dealt nothing, so the ward is already latched when a real unblocked hit lands later in the same turn. Also a text mismatch with the card's own "unblocked" wording on both the card (VigilOfTheDeep.cs:44) and the power (KuragePowers.cs:386)._
- **[medium] sim_vs_csharp_divergence** — The C# ward fires on any damage received, not just attack damage — it never tests `props.IsPoweredAttack()`, while tier0 only reaches the ward from the enemy 'attack' intent branch, and both descriptions say "attack damage".
  - `/home/user/GItS/tier0/engine/combat.py:634 — `if kind == "attack":` is the only branch that reaches the ward call at /home/user/GItS/tier0/engine/combat.py:661; other player HP-loss paths (/home/user/GItS/tier0/engine/effects.py:503, /home/user/GItS/tier0/engine/powers.py:135, /home/user/GItS/tier0/engine/refpowers.py:367, /home/user/GItS/tier0/engine/state.py:685) never call prevent_damage_exhaust`
  - `/home/user/GItS/klee-mod/KleeCode/Powers/KuragePowers.cs:445-452 and :462-471 and :482-492 — all three hooks take `ValueProp props` and none of them inspects it`
  - `/home/user/GItS/klee-mod/KleeCode/Powers/ElementalApplication.cs:189 — `if (!props.IsPoweredAttack()) return;` is the house predicate for exactly this distinction (same pattern at /home/user/GItS/klee-mod/KleeCode/Powers/CompanionPowers.cs:308)`
  - `/home/user/GItS/klee-mod/KleeCode/Powers/KuragePowers.cs:386 — "The first time you would take unblocked attack damage each turn"`
  - _Any unpowered/non-attack damage to Kokomi (HP costs, bomb/splash-class damage, status damage) will consume the ward's turn latch and a draw-pile card in the mod but never does in the sim._
- **[medium] sim_vs_csharp_divergence** — The sheet's `max_stacks: 6` (8 upgraded) single-application cap is enforced in tier0 and registered in codegen, but PreventExhaustWardPower implements no cap, so a second copy of the rare stacks the ward to 12 in the mod versus 6 in the sim.
  - `/home/user/GItS/docs/kokomi-cards.yaml:544 — `{op: apply_power, power: prevent_exhaust_ward, amount: 6, target: self, max_stacks: 6}`; /home/user/GItS/docs/kokomi-cards.yaml:547 — "max_stacks 6: does NOT stack — the magnitude is the knob, not the copy count"`
  - `/home/user/GItS/tier0/engine/powers.py:170-171 — `if max_stacks is not None: new = min(new, max_stacks)` (fed from /home/user/GItS/tier0/engine/effects.py:803 `cap = fx.get("max_stacks")`)`
  - `/home/user/GItS/tools/gen_klee_cards.py:452 — registry entry `"prevent_exhaust_ward": ("PreventExhaustWardPower", 6, ...)` and /home/user/GItS/klee-mod/DECISIONS.md:820 — "Stack caps are enforced in TryModifyPowerAmountReceived ... the C# const enforces"`
  - `/home/user/GItS/klee-mod/KleeCode/Powers/KuragePowers.cs:380-513 — the whole class: `StackType => PowerStackType.Counter` at :393 and no `TryModifyPowerAmountReceived` override anywhere (the mod's only two overrides are /home/user/GItS/klee-mod/KleeCode/Powers/SalonPowers.cs:468 and /home/user/GItS/klee-mod/KleeCode/Powers/KokomiResources.cs:391)`
  - _Upgrade amounts themselves agree (docs/kokomi-upgrades.yaml:138 `{power_amount: +2}` vs VigilOfTheDeep.cs:67 `UpgradeValueBy(2m)` -> 8), so this is not upgrade_delta_drift; what does not exist on the C# side is the cap the upgrade note says "rides along", and tier0/content/upgrades.py:469-473 does move it to 8 for the sim._

### kokomi:depths_judgment
- **[low] upgrade_delta_drift** — The depths_judgment upgrade comment states the upgraded card as "8 + 3 per 2 exhausted", but both the sheet row and the C# implementation give base 10 with the per-term applied once per exhausted card (upgraded: 10 + 3 x exhaust-pile count). The delta key {formula_per: +1} itself is correct and matches the C#; only the annotation is wrong, on two counts (stale base 8, and a bogus "per 2" halved rate).
  - `docs/kokomi-upgrades.yaml:140 — depths_judgment:   {formula_per: +1}     # 8 + 3 per 2 exhausted (the pile-reader's ceiling climbs, base fixed)`
  - `docs/kokomi-cards.yaml:556 — effects: [{op: damage, amount_formula: {base: 10, per: 2, count: exhaust_pile}, target: enemy}]`
  - `docs/kokomi-cards.yaml:557 — # The pile-reader's ceiling: 10 + 2 per exhausted card, single target, REPEATABLE`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/DepthsJudgment.cs:60 — new CalculationBaseVar(10m)`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/DepthsJudgment.cs:84 — DynamicVars.ExtraDamage.UpgradeValueBy(1m);`
  - `tools/gen_klee_cards.py:4560 — comment: the PER term of an amount_formula lives in ExtraDamage (base + per * count)`
  - `tier0/engine/effects.py:211-218 — _calc_amount returns base + per * _runtime_count(count), per applied once per exhaust-pile card`
  - _Previously logged as REAL DRIFT in docs/serenitea-sweep-log-2026-07-26.md:920 (then "8 + 2 per exhausted card"); the base-8 half survives, and the edit introduced the new "per 2" error. Base moved 8->10 at the v0.2 sheet pass (docs/archive/kokomi-sheetpass-v0.2-report.md:189). No player-visible effect: the numbers on both executable legs agree._
- **[low] text_ops_mismatch** — The generated class's cadence doc comment describes Furina's SKILL cadence ("damaging Skills, Burst-tagged cards, and skill-tagged cards apply Hydro") on a Kokomi card that is an Attack. Under the text as written this Attack would not apply Hydro, yet the class carries KleeKeywords.AppliesHydro; the sheet header and the generator's own manifest both rule CATALYST (every Attack applies Hydro), which is what the code actually does.
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/DepthsJudgment.cs:37 — /// <summary>Sheet cadence: damaging Skills, Burst-tagged cards, and skill-tagged cards apply Hydro.</summary>`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/DepthsJudgment.cs:43-44 — CanonicalKeywords => new[] { KleeKeywords.AppliesHydro } on a CardType.Attack (ctor line 68)`
  - `docs/kokomi-cards.yaml:51 — # Element: hydro | Cadence: CATALYST (RULED R52, ask N1): every attack applies hydro`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/manifest.json:5 — "cadence": "CATALYST (R52 ask N1): every Attack applies Hydro."`
  - `tier0/engine/effects.py:279-281 — catalyst branch: card.type == "attack" and op == "damage" applies the character element`
  - _Code comment only, not player-visible; behavior on all three legs agrees (Hydro is applied). Shared generator boilerplate — the identical string appears on all 19 Kokomi generated damage cards (e.g. PearlBarrage.cs:37, WatersEdge.cs:37), so this is one generator template defect rather than a per-card authoring slip._

### kokomi:epiphany_of_the_deep
- **[low] text_ops_mismatch** — The C# description renders the fixed draw count with a placeholder plural — "draw 1 card(s)." — where the sheet op is a hard amount: 1 that no upgrade can move (the only delta is cost: -1), and every other card in the mod that prints a literal 1 writes "draw 1 card." Cosmetic only; the behavior is correct.
  - `docs/kokomi-cards.yaml:560 — effects: [{op: apply_power, power: dark_embrace, amount: 1, target: self}]`
  - `docs/kokomi-upgrades.yaml:141 — epiphany_of_the_deep: {cost: -1}  (no amount delta, so the count is permanently 1)`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/EpiphanyOfTheDeep.cs:44 — ("description", "Whenever a card is [gold]Exhausted[/gold], draw 1 card(s).")`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/PearlDiver.cs:44 — "...{IfUpgraded:show:Draw 1 card.|}" (literal-1 convention, singular)`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/WhisperedWord.cs:44 — "[gold]Sly[/gold]: Draw 1 card." (same convention)`
  - `klee-mod/KleeCode/Cards/Kokomi/Generated/CommunionOfTides.cs:44 — "Draw {Cards:diff()} card{Cards:plural:|s}." (the plural helper used when the count is variable)`
  - _This is the only "card(s)" for a fixed count anywhere under klee-mod/KleeCode/Cards; the other "(s)" instance (TacticalRetreat.cs:44 "random card(s)") sits on a count that does move on upgrade. Everything else on this card agrees across all three legs: cost 2 / power / rare / TargetType.Self (EpiphanyOfTheDeep.cs:56) matches the sheet row (docs/kokomi-cards.yaml:559); OnPlay applies 1 DarkEmbrace to the owner (EpiphanyOfTheDeep.cs:62) matching op apply_power dark_embrace amount 1 target self and tier0's self-branch (effects.py:849 -> powers.py:169-174, no max_stacks, no Flawless-Strategy conversion since the power is not strength); OnUpgrade EnergyCost.UpgradeBy(-1) (EpiphanyOfTheDeep.cs:66) matches the upgrades delta (kokomi-upgrades.yaml:141) and honors the resource-curve law (kokomi-upgrades.yaml:3-5) since no charge/draw number moves; tier0's dark_embrace draws n on every non-ethereal exhaust and defers ethereal ones to the post-hand-flush (refpowers.py:266-315, 1293-1299), which is the base-game DarkEmbracePower the C# reuses, so no sim/C# divergence; the played Power card itself cannot self-trigger because result_pile sends powers to "none" (refpowers.py:319-330), matching CardType.Power. Card is listed as generated (manifest.json:27), not blocked._

**CLEAN (34):** coral_guard, tide_reading, conscription_notice, to_the_front, votive_offering, ritual_purification, cleansing_tide, undertow_shuffle, moon_signal, drifting_lantern, jade_bulwark, kurages_oath, before_sun_and_moon, standing_orders, vow_of_tides, pearl_diver, whispered_word, driftwood_charm, salt_line, slack_water, steady_the_line, mass_mobilization, field_promotion, mercy_of_the_deep, communion_of_tides, rearguard_action, shell_of_sanctuary, tidal_lure, honor_guard, press_the_advantage, moonlit_offering, sango_prayer, grand_conscription, prayer_to_the_moon

