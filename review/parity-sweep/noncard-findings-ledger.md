# S14 — Non-Card Parity Sweep: Findings Ledger

Date: 2026-08-05. Surplus Dispatch 3, cloud stream — the sequel to S1's 219-card sweep,
same format so the triage memos merge. One Opus agent per entity group; every entity gets
a verdict, CLEAN included, so coverage is provable. Every finding cites file:line on both
sides; all 174 findings passed a mechanical citation audit (every cited file exists and
every cited line is in range). Triage: `noncard-triage-memo.md` beside this file.
**Zero design authority: no fixes, no suggestions — verification only.**

**Coverage:** 173 entities — powers 25, relics 42, potions 9, events 24, companions 51, constants 22.
**Verdicts:** 75 CLEAN, 98 with findings (174 findings: low 83, medium 65, high 26).
**Families:** semantic_drift 45, other 37, sim_vs_csharp_divergence 36, sheet_vs_sim_divergence 25, text_ops_mismatch 18, missing_leg 13.

## powers

### klee-mod/KleeCode/Powers/AuraPower.cs — CLEAN
*legs read: klee-mod/KleeCode/Powers/AuraPower.cs:1-208 (full class + 4 element subclasses); klee-mod/KleeCode/Powers/ElementalApplication.cs:1-283 (KleeElementalHooks.BeforeDamageReceived application listener + AuraCmd.Duration/Apply/Refresh); klee-mod/KleeCode/Powers/ElementalHit.cs:1-88 (unpowered elemental pipeline: Deal / ApplyOnly); klee-mod/KleeCode/Powers/ReactionEffects.cs:120-313 (Resolve funnel: burst grant, Superconduct, Overload, Swirl, Crystallize, Frozen); klee-mod/KleeCode/Elements/ReactionTable.cs:1-129 (ReactionConstants + Lookup + AmplifierMultiplier overloads); klee-mod/KleeCode/Elements/Element.cs:1-48 (Element enum, IElementalCard, LeavesAura)*

### klee-mod/KleeCode/Powers/BombPower.cs — 3 finding(s)
*legs read: klee-mod/KleeCode/Powers/BombPower.cs:1-518 (full class: Localization, suppression latch, Place/DetonateOn/DetonateAll/ModifyAll/MoveAllTo, BeforeSideTurnStart, AfterDamageReceived, Detonate, RecordDetonation, NotifyDetonationListeners); klee-mod/KleeCode/Powers/DemolitionPowers.cs:41-200 (BombDamageUpPower, DetonationSplashPower, DetonationVulnPower IsDead guard at :149, BombAndSparkPerTurn); klee-mod/KleeCode/Powers/ElementalHit.cs:26-57 (Deal — the detonation damage pipeline); tier0/engine/effects.py:350-436 (deal_damage_to_enemy, _detonate_bombs_on_hit), 439-460 (detonate_bombs), 882-922 (_op_place_bomb/_op_detonate/_op_move_bombs/_op_modify_bombs), 1699-1711 (_op_chance_bomb_per_detonation), 2377-2385 (bomb_and_spark_per_turn); tier0/engine/state.py:291-307 (Bomb dataclass, Enemy.alive); tier0/engine/powers.py:42-54 (modify_damage_dealt bomb suppression), tier0/engine/combat.py:435-448 (turn-start detonation), 620-700 (_enemy_turn latch)*
1. **[MEDIUM · sim_vs_csharp_divergence]** BombPower's early-detonation listener has no death guard, while the sim explicitly refuses to early-detonate a bomb on an enemy the hit just killed — so a killing blow on a bombed enemy pays out detonation riders in C# that the sim never pays.
   - `klee-mod/KleeCode/Powers/BombPower.cs:360-373 (AfterDamageReceived guards only target==Owner, IsPoweredAttack, cardSource Type==Attack, result.UnblockedDamage>0 — no target.IsDead check before `await Detonate(choiceContext)`)`
   - `tier0/engine/effects.py:432-436 (`def _detonate_bombs_on_hit(...): if source != "attack" or not enemy.bombs or not enemy.alive: return`)`
   - `tier0/engine/effects.py:380 (`enemy.hp -= hp_dmg`) and tier0/engine/effects.py:411-412 (`if hp_dmg > 0: _detonate_bombs_on_hit(state, enemy, source)`) — the guard is evaluated AFTER HP is deducted, so `alive` means 'survived this hit'`
   - `tier0/engine/state.py:306-307 (`def alive(self) -> bool: return self.hp > 0`)`
   - `klee-mod/KleeCode/Powers/DemolitionPowers.cs:149 (`if (target.IsDead) return;` — the sibling detonation listener DOES carry the sim's `if enemy.alive` discipline)`
   - `tier0/engine/combat.py:444 (turn-start sweep iterates `state.living_enemies`, so a corpse's bombs are never detonated on that path either)`
   - note: Realization depends on whether the engine broadcasts AfterDamageReceived on a creature the hit just killed — the repo records that premise as contested and unverified (klee-mod/DECISIONS.md:1623-1627), which is why I graded this medium rather than high. The code-level asymmetry is unambiguous on both sides regardless.
2. **[MEDIUM · other]** The repo's own decision record and playtest checklist state the sim's corpse-detonation behavior backwards, which inverts the stated stakes and the pass/fail mapping of the only open parity test on bombs.
   - `klee-mod/DECISIONS.md:1629-1634 ("STAKES ...: the sim detonates unconditionally. If the game suppresses on death and the sim does not, then every sim bomb-damage measurement taken against a KILLABLE enemy overcounts")`
   - `tier0/engine/effects.py:434 (`if source != "attack" or not enemy.bombs or not enemy.alive: return` — the sim does NOT detonate unconditionally; it suppresses on death)`
   - `klee-mod/DECISIONS.md:1639-1640 ("Spark appears -> hook fires on death, sim and game agree, close it. / No Spark -> real divergence, opens a sim-side correction.")`
   - `docs/open-playtest-items.md:44 ("Spark → sim and game agree, close it. No Spark → **every sim bomb number taken against a killable enemy overcounts**.")`
   - note: Family `other` because the disagreeing surface is a decision record / playtest checklist rather than a spec yaml, so neither sheet_vs_sim nor text_ops fits cleanly. This is not a stale-comment nit: it is the recorded settlement criterion for an item the repo marks 'OPEN. Do not baseline bomb numbers against it until settled.'
3. **[MEDIUM · text_ops_mismatch]** The Bomb badge and smart tooltip display the raw sum of bomb charges, excluding BombDamageUpPower, so with Explosives Workshop in play the number shown under the enemy is lower than the damage the detonation will deal — contradicting the class doc's explicit guarantee.
   - `klee-mod/KleeCode/Powers/BombPower.cs:184 (`public int PendingDamage => _damages.Sum(c => c.Damage);`) and :188 (`public override int DisplayAmount => PendingDamage;`)`
   - `klee-mod/KleeCode/Powers/BombPower.cs:66-71 (smartDescription: "Detonates at the start of your turn for {Damage} total damage ({Amount} Bomb{Amount:plural:|s}).")`
   - `klee-mod/KleeCode/Powers/BombPower.cs:196-199 ("The badge and the tooltip both derive from _damages -- the same list detonation consumes -- so the displayed number can never diverge from what will actually hit.")`
   - `klee-mod/KleeCode/Powers/BombPower.cs:460-461 (`var damageUp = applier?.Powers.OfType<BombDamageUpPower>().FirstOrDefault()?.Amount ?? 0;`) and :479-481 (`await ElementalHit.Deal(..., damage + bonus + damageUp, applier);`)`
   - `tier0/engine/effects.py:443 (`dmg = bomb.damage + bonus + p.powers.get("bomb_damage_up", 0)`)`
   - `docs/klee-cards.yaml:107-108 (explosives_workshop: `{op: apply_power, power: bomb_damage_up, amount: 2, target: self}`)`
   - note: Display-layer only; the damage actually dealt matches the sim exactly (per-bomb, pre-amplification), so gameplay is correct. Graded medium rather than high because no combat number is wrong — only the number the player plans against. Two on-screen surfaces contradict each other: Explosives Workshop's own tooltip promises +Amount per Bomb while the Bomb badge never reflects it. Remote Detonator's transient `bonus` (BombPower.cs:246) is legitimately absent from the display since it exists only during that card's resolution; bomb_damage_up is a standing power (stack cap 4, docs/klee-character-design.md:47) and is not.

### klee-mod/KleeCode/Powers/BurstResource.cs — CLEAN
*legs read: klee-mod/KleeCode/Powers/BurstResource.cs:1-267 (BurstConstants, ISkillTagCard, KleeBurstResource: ApplySharedModification/CanAfford/Spend/DrainOnPlay/Find/AmountFor/Gain/GainPreResolution/SyncGauge, retired BurstMeterPower); klee-mod/KleeCode/Powers/ElementalApplication.cs:61-155 (BeforeCardPlayed drain + skill-tag grant, AfterCardPlayed SyncGauge + kit grant, turn-start/turn-end grant sites); klee-mod/KleeCode/Powers/KitBurst.cs:1-160 (KitBurstConstants, SparksNSplashPower volley, KitGrant.GrantIfCharged reading BurstConstants.KleeMax); klee-mod/KleeCode/Powers/ReactionEffects.cs:151-188 (per-reaction +5 to Klee/Furina/Kokomi + Catalytic Conversion); klee-mod/KleeCode/Powers/FurinaResources.cs:88-94, 232-275, 766-790, 1057-1100 (parallel FurinaBurstResource); klee-mod/KleeCode/Powers/KokomiResources.cs:40-120, 162-250, 320-360, 444-512 (parallel KokomiBurstResource)*

### klee-mod/KleeCode/Powers/CompanionPowers.cs — 3 finding(s)
*legs read: klee-mod/KleeCode/Powers/CompanionPowers.cs:1-530 (full file); klee-mod/KleeCode/Powers/SimDamagePipeline.cs:1-53; klee-mod/KleeCode/Powers/ElementalHit.cs:24-90; klee-mod/KleeCode/Powers/FontainePowers.cs:50-120 (NightVigilPower mirror); klee-mod/KleeCode/Powers/FrozenPower.cs:60-130 (ShatterBonusPower consumer); klee-mod/KleeCode/Powers/ElementalApplication.cs:80-95 (CompanionPlays.Record site)*
1. **[HIGH · sim_vs_csharp_divergence]** Witch's Flame's per-aura damage is dealt as a raw Unpowered, dealer-less hit in C#, so it skips the Strength/Weak/Vulnerable modifiers the sim's deal_damage_to_enemy applies to it.
   - `tier0/engine/effects.py:2560 — `damage = p.powers["witchs_flame"]``
   - `tier0/engine/effects.py:2566-2567 — `deal_damage_to_enemy(state, enemy, damage, element=None, source="companion")` (full pipeline, not a raw `hp -=`)`
   - `tier0/engine/effects.py:362 — `dmg = powers.modify_damage_dealt(state.player, base)``
   - `tier0/engine/effects.py:367 — `dmg = powers.modify_damage_taken(enemy, dmg, from_card=source in ("card", "attack"))``
   - `tier0/engine/powers.py:42-54 — modify_damage_dealt adds Strength, then Weak x0.75`
   - `tier0/engine/powers.py:57-61 — modify_damage_taken applies Vulnerable x1.5`
   - note: The neighbouring Unpowered hits in this repo are correct precisely because their sim counterparts are raw `hp -=` (detonation splash, Shatter, reaction splash). witchs_flame is the one companion payout that goes through the full sim pipeline and is the one that was translated as a raw hit.
2. **[HIGH · sim_vs_csharp_divergence]** Solar Isotoma pays Block on any powered damage the owner deals, including non-Attack cards; the sim gates it on source == "attack", i.e. only cards whose type is attack. The printed text also says "Your Attacks".
   - `tier0/engine/effects.py:358-360 — `if (source == "attack" and enemy.aura and state.player.powers.get("solar_isotoma", 0)): state.player.block += C.SOLAR_ISOTOMA_BLOCK``
   - `tier0/engine/effects.py:500 — `source = "attack" if card.type == "attack" else "card"` (a Skill that deals damage is never source "attack")`
   - `klee-mod/KleeCode/Powers/CompanionPowers.cs:302-313 — BeforeDamageReceived checks only `dealer != Owner`, `props.IsPoweredAttack()` and `AuraCmd.Find(target) == null`; there is no `cardSource is { Type: CardType.Attack }` guard`
   - `klee-mod/KleeCode/Powers/FontainePowers.cs:103-105 — NightVigilPower, documented at FontainePowers.cs:73-83 as the "DELIBERATE MIRROR of SolarIsotomaPower" with "the identical ordering constraint", DOES carry `if (cardSource is not { Type: CardType.Attack }) return 0m;``
   - `tier0/engine/effects.py:604 — night_vigil's sim gate is `if enemy.aura and card.type == "attack"`, the same shape solar_isotoma's `source == "attack"` has`
   - `klee-mod/KleeCode/Cards/Generated/ShinobuSanctifyingRing.cs:77 — `: base(2, CardType.Skill, …, TargetType.AllEnemies, …)``
   - note: Pure add — the sim never pays here, so this is a C#-only Block gift, and it also contradicts the power's own printed text. The pre-hit read ordering (BeforeDamageReceived, before AuraPower consumes the aura) is correct and matches effects.py:358's "checked before the hit can consume the aura"; only the card-type scope diverges.
3. **[MEDIUM · sim_vs_csharp_divergence]** MetallicizePower grants its Block with ValueProp.Move (the powered card/monster-move block class), so Dexterity scales it and Frail reduces it; the sim adds Metallicize block raw and both sim modules explicitly classify it as Unpowered/passive block that must not be touched by that funnel.
   - `tier0/engine/powers.py:118-120 — `def on_turn_start(...): if fighter.powers.get("metallicize", 0): fighter.block += fighter.powers["metallicize"]` (direct add, no funnel)`
   - `tier0/engine/powers.py:75-81 — modify_block_gained docstring: "The single funnel every card-block site routes through … so passive/power block (Metallicize, Crystallize, Solar Isotoma) is deliberately NOT reduced here", with Dexterity/Frail both guarded by IsPoweredCardOrMonsterMoveBlock`
   - `tier0/engine/refpowers.py:182-185 — gain_block docstring: "`card_sourced` mirrors StS2's `props.IsCardOrMonsterMove()` … Passive block (Plating, CrimsonMantle, Rage, FeelNoPain, Metallicize) is Unpowered and is not."`
   - `klee-mod/KleeCode/Powers/CompanionPowers.cs:528 — `await CreatureCmd.GainBlock(Owner, Amount, ValueProp.Move, null);``
   - `klee-mod/KleeCode/Powers/CompanionPowers.cs:310-312 — SolarIsotomaPower, a power-block sibling in the same file, uses `ValueProp.Unpowered``
   - `klee-mod/KleeCode/Powers/CompanionPowers.cs:361-363 — CelestialGiftPower's turn-start Block also uses `ValueProp.Unpowered``
   - note: Every other passive-block site in this file and in SalonPowers picks Unpowered; Metallicize is the odd one out. The class doc at CompanionPowers.cs:499-511 defends the turn-START timing against the tabletop convention but says nothing about the block class, so this reads as an oversight rather than a ruling.

### klee-mod/KleeCode/Powers/CurtainCallPowers.cs — 4 finding(s)
*legs read: klee-mod/KleeCode/Powers/CurtainCallPowers.cs:1-395 (full file); klee-mod/KleeCode/Powers/FurinaResources.cs:750-1000 (FurinaResourceHooks: BeforeCardPlayed, AfterCardPlayed, BeforeSideTurnStart, AfterPlayerTurnStart, BeforeSideTurnEnd, AfterDamageReceived); klee-mod/KleeCode/Powers/ReactionEffects.cs:55-175; klee-mod/KleeCode/Powers/SalonPowers.cs:205-260 (Bow), 330-370 (Deploy), 413-455 (upkeep); klee-mod/KleeCode/Cards/Furina/Generated/BlockingNotes.cs:40-80; klee-mod/KleeCode/Powers/AuraPower.cs:100-140*
1. **[HIGH · sim_vs_csharp_divergence]** CurtainCallHooks counts companion_plays_this_turn once per replay, but the sim counts it once per card PLAY (the increment sits outside the replay loop). The C# comment asserting it "shares the sim's site" is factually wrong about that site.
   - `tier0/engine/combat.py:268-270 — inside `_finish_play`: `if card.is_companion: state.companions_played.append(card.id); state.companion_plays_this_turn += 1``
   - `tier0/engine/combat.py:271-275 — the sim's own note on this exact line: "Fires once per CARD PLAY, here beside companions_played, not once per replay inside the loop below -- Study Buddy's replay is one card being resolved twice"`
   - `tier0/engine/combat.py:281-289 — the Study Buddy replays are added AFTER the increment and the loop `for _ in range(replays): before_card_played / resolve_card / after_card_played` runs below it`
   - `klee-mod/KleeCode/Powers/CurtainCallPowers.cs:200-209 — "Counted here rather than in a Companion-specific hook so it shares the sim's site: the sim increments in combat._finish_play … IsFirstInSeries is NOT tested, deliberately", then `CompanionPlays[owner] = Get(CompanionPlays, owner) + 1;``
   - `klee-mod/KleeCode/Powers/FurinaResources.cs:811 — `await CurtainCallHooks.NoteCardPlayed(choiceContext, cardPlay);` inside FurinaResourceHooks.AfterCardPlayed, which fires per play index (cf. CurtainCallPowers.cs:173-175 gating on IsLastInSeries and CompanionPowers.cs:449-455 gating on IsFirstInSeries precisely because it fires per replay)`
   - `klee-mod/KleeCode/Powers/CurtainCallPowers.cs:96-98 — CompanionPlaysThisTurn is documented as mirroring state.companion_plays_this_turn`
   - note: Second, currently-unreachable half of the same mismatch: the sim increments BEFORE resolve_card (effects.py:83-88 records the resulting off-by-one as a decision — a Companion that grants Block would count itself), while the C# increments in AfterCardPlayed, i.e. after resolution. effects.py:85-87 notes there are no such cards today, so only the replay half is live. The Best Friends Forever ledger in the sibling file (CompanionPowers.cs:57-98, recorded at ElementalApplication.cs:90-93 under IsFirstInSeries) uses the correct once-per-play rule, so the two C# companion-play trackers disagree with each other.
2. **[MEDIUM · semantic_drift]** The Gallery Stirs' draw is deferred out of the Encore-spend moment; on a Salon-upkeep spend the flush and the spend are scheduled in the SAME AfterPlayerTurnStart broadcast, so on the unfavourable ordering the turn-start draw does not land until the player's first card play (or turn end).
   - `tier0/engine/resources.py:309-313 — inside spend_encore: `n = p.powers.get("encore_spend_draw", 0); if n and state.encore_spend_draws_this_turn == 0: state.encore_spend_draws_this_turn = 1; state.draw(n)` — drawn synchronously at the spend`
   - `tier0/engine/effects.py:2415 — salon_tick's upkeep calls `resources.spend_encore(state, C.SALON_TICK_ENCORE_COST)` from player_turn_start_triggers, so in the sim the draw happens during turn-start upkeep`
   - `klee-mod/KleeCode/Powers/CurtainCallPowers.cs:163-170 — NoteEncoreSpent only records `PendingDraws`; no draw is issued`
   - `klee-mod/KleeCode/Powers/CurtainCallPowers.cs:174-182 — FlushPendingDraws is the only place the draw is issued`
   - `klee-mod/KleeCode/Powers/FurinaResources.cs:914 — the turn-start flush lives in FurinaResourceHooks.AfterPlayerTurnStart`
   - `klee-mod/KleeCode/Powers/SalonPowers.cs:413-428 — SalonMemberPower's upkeep spend (`FurinaResources.SpendEncore(Owner, SalonConstants.TickEncoreCost)`) also lives in AfterPlayerTurnStart`
   - note: The card is never lost (BeforeSideTurnEnd flushes), so this is a timing/ordering drift rather than a lost draw. The same reasoning the file applies to ResetTurn (moved to the strictly-earlier BeforeSideTurnStart) was not applied to the flush. On card-play spends the drift is smaller but still real: the sim draws at cost settle, before the card resolves (combat.py:206 `resources.spend_encore(state, card.encore_cost)` precedes _finish_play), while the C# flush runs after resolution.
3. **[LOW · text_ops_mismatch]** The Gallery Stirs and Quick Change print "card" with no plural form, but both powers upgrade to amount 2, so the upgraded tooltips read "draw 2 card" / "draws 2 card".
   - `klee-mod/KleeCode/Powers/CurtainCallPowers.cs:373-374 — `"The first time you spend Encore each turn, draw {Amount} card."``
   - `klee-mod/KleeCode/Powers/CurtainCallPowers.cs:388-389 — `"The first Attack you play each turn draws {Amount} card."``
   - `docs/furina-upgrades.yaml:58 — `crowd_work: {power_amount: +1}    # first-spend draw 1->2``
   - `docs/furina-upgrades.yaml:137 — `quick_change: {power_amount: +1}    # first-Attack draw 1->2``
   - `klee-mod/KleeCode/Powers/CompanionPowers.cs:151-152 — the mod's plural idiom: `"played {Amount} extra time{Amount:plural:|s}."``
   - `klee-mod/KleeCode/Powers/CompanionPowers.cs:205 — `"Lasts {Amount} more turn{Amount:plural:|s}."``
   - note: Same class as the sibling powers in CompanionPowers.cs that do use {Amount:plural:|s}; no behavioural effect.
4. **[LOW · sim_vs_csharp_divergence]** RefreshAllAuras only tops auras UP to the current full duration; the sim's _op_refresh_all_auras hard-SETS the remaining turns, so an aura sitting above the current duration would be shortened by the sim and left alone by the C#.
   - `tier0/engine/effects.py:949-952 — `def _op_refresh_all_auras(...): for e in state.living_enemies: if e.aura: e.aura_turns_left = reactions.aura_duration(state)` (assignment, not max)`
   - `klee-mod/KleeCode/Powers/CurtainCallPowers.cs:242-244 — `var full = AuraCmd.Duration(owner); if (aura.Amount >= full) continue;` then ModifyAmount by the difference`
   - note: Not reachable on today's content — nothing removes ancient_sea_authority mid-combat, so full is never below an existing aura's remaining turns. Recorded for coverage, not as a live defect. Everything else in this helper matches, including reusing AuraCmd.Duration so relic/power extensions are honoured.

### klee-mod/KleeCode/Powers/DemolitionPowers.cs — 1 finding(s)
*legs read: klee-mod/KleeCode/Powers/DemolitionPowers.cs:1-205 (full file); klee-mod/KleeCode/Powers/BombPower.cs:1-518; klee-mod/KleeCode/Powers/SparkKitPowers.cs:15-42 (SparkPerTurnPower text idiom); klee-mod/KleeCode/Powers/ElementalHit.cs:24-57; tier0/engine/effects.py:412 (_detonate_bombs_on_hit call), 432-476 (detonate_bombs), 2390-2400 (bomb_and_spark_per_turn in player_turn_start_triggers); tier0/engine/combat.py:430-446 (turn-top resets incl. splash_procs_this_turn, then detonate_bombs, then player_turn_start_triggers)*
1. **[LOW · text_ops_mismatch]** Playtime Forever's description hardcodes one Bomb and one Spark and never renders {Amount}, but the implementation loops Amount times, so a stacked power does more than the tooltip promises.
   - `klee-mod/KleeCode/Powers/DemolitionPowers.cs:174-177 — `"At the start of your turn, place a 5-damage [gold]Bomb[/gold] on a random enemy and gain 1 [gold]Spark[/gold]."` (no {Amount} anywhere)`
   - `klee-mod/KleeCode/Powers/DemolitionPowers.cs:188-203 — `for (var i = 0; i < Amount; i++) { … BombPower.Place(…, PlaytimeBombDamage, …); await SparkPower.Gain(choiceContext, Owner, 1, …); }``
   - `tier0/engine/effects.py:2392-2400 — `n = p.powers.get("bomb_and_spark_per_turn", 0); for _ in range(n): … enemy.bombs.append(Bomb(damage=C.PLAYTIME_BOMB_DAMAGE …)); gain_sparks(state, 1)` (same per-stack loop, so the behaviour is correct; only the text is not)`
   - `klee-mod/KleeCode/Powers/SparkKitPowers.cs:20-30 — the sibling turn-start power in the same archetype pass renders `"At the start of your turn, gain {Amount} [gold]Spark[/gold]{Amount:plural:|s}."``
   - `docs/klee-upgrades.yaml:51 — `explosives_workshop: {power_amount: +1}   # +2->+3 per copy; duplicate Powers stack without a cap`, i.e. duplicate demolition Powers stacking is expected`
   - note: Behaviour matches the sim exactly (per-stack loop, Spark granted unconditionally even with no living enemy, bomb placed only if a living enemy exists). Text-only.

### klee-mod/KleeCode/Powers/ElementalApplication.cs — 1 finding(s)
*legs read: klee-mod/KleeCode/Powers/ElementalApplication.cs:1-283 (full); klee-mod/KleeCode/Powers/AuraPower.cs:1-207 (full); klee-mod/KleeCode/Powers/ReactionEffects.cs:1-320 (full); klee-mod/KleeCode/Powers/BurstResource.cs:72-241; klee-mod/KleeCode/Powers/BombPower.cs:239-470; klee-mod/KleeCode/Powers/CompanionPowers.cs:57-98,140-190,430-460*
1. **[MEDIUM · sim_vs_csharp_divergence]** KleeElementalHooks.BeforeCardPlayed applies the Burst-meter head (requires-full drain + the +5 skill-tag gain) to EVERY card play including auto-plays, while tier0 puts both inside play_card's head, which resolve_free_play (CardCmd.AutoPlay) deliberately enters below — so an auto-played skill-tagged card gains 5 Burst Energy in the mod and 0 in the sim, and an auto-played kit Burst empties the meter in the mod and not in the sim.
   - `klee-mod/KleeCode/Powers/ElementalApplication.cs:70-95 — BeforeCardPlayed gates only on cardPlay.IsFirstInSeries, calls KleeBurstResource.DrainOnPlay then GainPreResolution(BurstConstants.PerSkillTag); no autoplay/free-play exclusion`
   - `klee-mod/KleeCode/Powers/ElementalApplication.cs:79-81 — the method's own comment ('Owner is null on autoplay/token paths … This hook fires for every card every player plays') confirms the hook is reached on the autoplay path`
   - `klee-mod/KleeCode/Powers/BurstResource.cs:143-152 — the drain was moved OUT of the cost machinery precisely because 'CardCmd.AutoPlay does NOT call SpendResources', i.e. the mod deliberately makes autoplay pay the meter`
   - `tier0/engine/combat.py:247-252 — the drain (`p.burst_energy = 0`) and `if p.burst_max and "skill_tag" in card.tags: gain_burst(C.BURST_PER_SKILL_TAG)` live in play_card's head, immediately before _finish_play`
   - `tier0/engine/combat.py:358-363 — resolve_free_play: 'NOT ONLY THE COST IS SKIPPED: this enters at _finish_play, below play_card's whole head -- so spotlight counting, burst-per-skill-tag gain and burst-cast emptying do not run either… the day a roster card auto-plays a skill_tag card, that card gains no burst unless this boundary moves.'`
   - `tier0/engine/combat.py:353-356 — the same docstring establishes the C# side of the disagreement: 'the base game runs an auto-play through the same CardModel.OnPlayWrapper as a manual play, so an auto-played card fires BeforeCardPlayed/AfterCardPlayed'`
   - note: Unreachable today in both directions: grep shows no mod card calls CardCmd.AutoPlay (klee-mod/KleeCode has only two AutoPlay mentions, both in comments — BurstResource.cs:146, KokomiResources.cs:486), and reference characters carry no Burst meter. Filed as medium rather than high because the sim itself flags the boundary as a known future hazard; the mod's half of it is undocumented, so the first auto-play card to land would diverge silently. Everything else in this file checks out: the drain-before-skill-tag order matches combat.py:247-251; CompanionPlays.Record fires pre-resolution like combat.py:269's companions_played.append and its (owner,id) dedupe matches the sim's only reader, `dict.fromkeys` at effects.py:1731; MarkTurnStart at AfterSideTurnEnd(Enemy) is a strictly earlier broadcast than bomb detonation and so reproduces combat.py:436's reset-before-detonate ordering; AuraCmd.Duration/Apply/Refresh are exact ports of reactions.py:39-58,81 including the trigger-only Anemo/Geo rule; and the BeforeDamageReceived/AfterDamageReceived phase split reproduces resolve_hit's apply/refresh/consume branches for single- and multi-hit cards alike.

### klee-mod/KleeCode/Powers/ElementalHit.cs — CLEAN
*legs read: klee-mod/KleeCode/Powers/ElementalHit.cs:1-88 (full); klee-mod/KleeCode/Powers/SimDamagePipeline.cs:1-53 (full); klee-mod/KleeCode/Powers/AuraPower.cs:100-187; klee-mod/KleeCode/Powers/ReactionEffects.cs:122-320; klee-mod/KleeCode/Powers/BombPower.cs:342-470; tier0/engine/effects.py:351-430 (deal_damage_to_enemy)*

### klee-mod/KleeCode/Powers/FontainePowers.cs — 2 finding(s)
*legs read: klee-mod/KleeCode/Powers/FontainePowers.cs:1-200 (full); klee-mod/KleeCode/Powers/CompanionPowers.cs:25-35 (MasqueBondBlock); klee-mod/KleeCode/Cards/Generated/NaviaCannonFireSupport.cs:1-77 (full); klee-mod/KleeCode/Cards/Generated/ArlecchinoMasqueRedDeath.cs:33-78; tier0/engine/combat.py:263-282 (_finish_play companion half); tier0/engine/effects.py:520-560 (_op_damage attack riders), :594-610 (night_vigil), :2355-2375 (turn-start), :2465-2490 (turn-end bond)*
1. **[HIGH · sheet_vs_sim_divergence]** tier0 still gives masque_red_death a flat +Amount damage rider on every player Attack — a leftover from the pre-2026-07-25 draft ('+4 damage on Attacks; you can no longer be healed') that the sheet's redesign replaced. The sheet's ops and the C# power both grant only the per-turn Strength and the Bond of Life, so the sim over-deals by the power's stack count on every Attack for the rest of the combat (and double-dips with the Strength it also grants).
   - `tier0/engine/effects.py:546-550 — inside `if card.type == "attack"`: '# Arlecchino, Masque of the Red Death: flat rider on YOUR Attacks.' … `base += state.player.powers.get("masque_red_death", 0)``
   - `docs/fontaine-companions.yaml:145-146 — the card's only op is `{op: apply_power, power: masque_red_death, amount: 1, target: self, note: "at the start of each turn gain 1 Strength; your Bond of Life eats the first 5 Block you gain each turn"}` — no damage rider`
   - `docs/fontaine-companions.yaml:151 — 'REDESIGNED 2026-07-25 [USER], replacing "+4 damage on Attacks; you can no longer be healed"'`
   - `klee-mod/KleeCode/Powers/FontainePowers.cs:166-200 — MasqueRedDeathPower implements only AfterPlayerTurnStart (StrengthPower) and BeforeSideTurnEnd (LoseBlock); it declares no ModifyDamageAdditive/ModifyDamageMultiplicative override at all`
   - `klee-mod/KleeCode/Cards/Generated/ArlecchinoMasqueRedDeath.cs:51 — printed text is 'At the start of each turn, gain {PowerAmount:diff()} Strength. Each turn your Bond of Life consumes the first 5 Block you gain.' — no damage clause`
   - note: Simultaneously a sim_vs_csharp_divergence: the game deals base+Strength where the sim deals base+Strength+stacks on every Attack. Nothing pins the rider — tier0/tests/test_fontaine.py:319-378 covers only the Strength ratchet, the Bond, the clamp, the Navia interaction and the Kokomi Charge conversion; no test asserts the damage bonus, which is consistent with it being dead code the redesign forgot to delete. The other two sim readers of the power (effects.py:2371 Strength, effects.py:2485 Bond) both have exact C# counterparts (FontainePowers.cs:182-188 and :190-199, with CompanionConstants.MasqueBondBlock == C.MASQUE_BOND_BLOCK == 5).
2. **[HIGH · sim_vs_csharp_divergence]** CannonFireSupportPower pays Navia's own card play. The power is applied during NaviaCannonFireSupport.OnPlay and then observes that same play in AfterCardPlayed — the card is itself an ICompanionCard and the guards (owner, IsFirstInSeries) all pass — so the player gains 3 Block (5 upgraded) on the turn she is played. tier0 places the grant before resolve_card specifically so this cannot happen, and the behaviour is test-pinned.
   - `klee-mod/KleeCode/Powers/FontainePowers.cs:59-68 — `AfterCardPlayed`: returns only on `Card is not ICompanionCard`, a non-owner, or `!IsFirstInSeries`, then `CreatureCmd.GainBlock(Owner, Amount, …)`; there is no guard excluding the play that granted the power`
   - `klee-mod/KleeCode/Cards/Generated/NaviaCannonFireSupport.cs:33 — `public sealed class NaviaCannonFireSupport : CustomCardModel, ICompanionCard` (her own card satisfies the trigger)`
   - `klee-mod/KleeCode/Cards/Generated/NaviaCannonFireSupport.cs:70 — `PowerCmd.Apply<CannonFireSupportPower>(…)` runs inside OnPlay, i.e. before the AfterCardPlayed broadcast for that same play`
   - `tier0/engine/combat.py:274-280 — '# Sitting before resolve_card also means Navia's own play does not pay itself: the power is not up yet.' … `navia = p.powers.get("cannon_fire_support", 0); if navia: p.block += navia``
   - `tier0/tests/test_fontaine.py:239-243 — `_play(st, "navia_cannon_fire_support")` then `assert st.player.block == 0` with the comment 'Her own play does not pay itself'`
   - `tier0/engine/refpowers.py:589-593 — the decompile-derived note that Afterimage/SerpentForm/Strangle 'keep a Dictionary<CardModel,int> filled at BeforeCardPlayed and drained at AfterCardPlayed. The indirection is not decoration: it is what stops a card that GRANTS one of these powers from paying itself on the very play that granted it' — i.e. the engine does dispatch AfterCardPlayed to a power created during that play, which is why the base game needs the snapshot the mod power does not take`
   - note: The class doc at FontainePowers.cs:36-38 records the Before/After ordering divergence but scopes it wrongly — 'The two orders differ only for a companion card that READS the player's Block during its own resolution' — the self-pay case is the one it misses, and it is not hypothetical because Navia's own card is a Companion. Fix shape is out of scope; flagged only as the disagreement. The rest of the file checks out: NightVigilPower's ModifyDamageAdditive gates (owner's powered card Attacks, aura read pre-consumption) mirror effects.py:604-606 including the amp interaction pinned at test_fontaine.py:258-277; AncientSeaAuthorityPower.ExtraTurnsFrom is read at the single AuraCmd.Duration chokepoint that every apply/refresh/swirl site routes through (ElementalApplication.cs:228-230, AuraPower.cs:143, ReactionEffects.cs:279, ElementalEcstasy.cs:68, CurtainCallPowers.cs:242), matching reactions.py:39-48; and the Masque Bond's end-of-turn deduction with a min() clamp matches effects.py:2485-2488 exactly (its one behavioural gap, a card that reads Block mid-turn, is identically documented on both sides and unreachable).

### klee-mod/KleeCode/Powers/FrozenPower.cs — 4 finding(s)
*legs read: klee-mod/KleeCode/Powers/FrozenPower.cs:1-120; klee-mod/KleeCode/Powers/ReactionEffects.cs:1-260; klee-mod/KleeCode/Powers/AuraPower.cs:1-200; klee-mod/KleeCode/Powers/ElementalApplication.cs:195-260; klee-mod/KleeCode/Powers/CompanionPowers.cs:470-500; klee-mod/KleeCode/Elements/ReactionTable.cs:45-55*
1. **[MEDIUM · sim_vs_csharp_divergence]** C# FrozenPower is a stacking Counter power that expires by duration tick, while tier0 models Frozen as a single boolean flag. A second freeze landing on an already-Frozen enemy therefore weakens TWO enemy turns and grants TWO Shatter windows in C#, where the sim's `enemy.frozen = True` is idempotent and always spent by the very next enemy action.
   - `klee-mod/KleeCode/Powers/FrozenPower.cs:43`
   - `klee-mod/KleeCode/Powers/FrozenPower.cs:112-119`
   - `klee-mod/KleeCode/Powers/ReactionEffects.cs:217-219`
   - `tier0/engine/state.py:425-426`
   - `tier0/engine/reactions.py:121-129`
   - `tier0/engine/combat.py:621-623`
   - note: PowerCmd.Apply<T> is additive for Counter powers in this codebase — AuraCmd.Apply is guarded by an explicit `if (AuraCmd.Find(target) != null) return;` at ElementalApplication.cs:201-203 precisely because a second Apply would stack. ReactionEffects.cs:217 has no such guard. Double-freeze is reachable in normal play (a hydro-on-cryo reaction and a cryo-on-hydro reaction on the same enemy in one turn). The class's own tooltip at FrozenPower.cs:36-38 says 'This creature's NEXT action deals 50% less damage', which is only true at one stack.
2. **[MEDIUM · semantic_drift]** tier0 consumes Frozen when the enemy ACTS, after the asleep/dead early-returns, so an enemy that skips its turn keeps its freeze. C# ticks the power down at AfterSideTurnEnd(Enemy) unconditionally, so a sleeping or otherwise skipping enemy loses Frozen without ever having its action weakened, and a freeze applied after that enemy already acted is wiped before it can ever apply.
   - `klee-mod/KleeCode/Powers/FrozenPower.cs:108-119`
   - `tier0/engine/combat.py:590-595`
   - `tier0/engine/combat.py:620-623`
   - note: tier0 ships a sleeping enemy in the battery (tier0/content/encounters/battery.yaml:29-35, `sleeper` with sleep_turns: 3), so freeze-then-sleep is a modelled shape, not hypothetical. Also relevant: C#'s ModifyDamageMultiplicative (FrozenPower.cs:45-55) fires for ANY damage the owner deals while Frozen is up, whereas tier0 applies FROZEN_DAMAGE_MULT only inside the `kind == "attack"` branch of the enemy's own turn (tier0/engine/combat.py:643-644).
3. **[LOW · sim_vs_csharp_divergence]** tier0 snapshots `was_frozen` before the reaction resolves and gates Shatter on both the snapshot and the live flag, so the same hit that applies Frozen can never Shatter it. FrozenPower.AfterDamageReceived carries no equivalent pre-hit snapshot, so a freshly applied FrozenPower has nothing preventing it from Shattering the very hit that created it.
   - `klee-mod/KleeCode/Powers/FrozenPower.cs:80-88`
   - `tier0/engine/effects.py:361`
   - `tier0/engine/effects.py:387`
   - note: Filed low because reachability depends on whether the host's power-list broadcast delivers AfterDamageReceived to a power applied during that same broadcast (AuraPower.AfterDamageReceived at AuraPower.cs:128-158 is what applies the freeze, via ReactionEffects.Resolve). No decompiled BaseLib is present in the tree, so I could not confirm the iteration semantics either way. The guard's absence relative to a guard tier0 documents explicitly is the finding.
4. **[LOW · semantic_drift]** FrozenPower's class doc asserts the round-3 ruling that 'Bosses take Vulnerable instead'. tier0 implements that per-ENEMY via `enemy.is_boss`; the C# application site tests the ROOM (`RoomType.Boss`), so every creature in a boss room — including summoned adds and minions that carry no boss flag — receives Vulnerable instead of Frozen.
   - `klee-mod/KleeCode/Powers/FrozenPower.cs:21-23`
   - `klee-mod/KleeCode/Powers/ReactionEffects.cs:207-219`
   - `tier0/engine/state.py:423`
   - `tier0/engine/reactions.py:123-129`
   - note: The divergent line lives in ReactionEffects.cs (another entity's file); filed here because FrozenPower.cs:21-23 is what states the ruling this implementation is supposed to satisfy. Unobservable in tier0 today — the only is_boss encounter is the single-enemy tank_boss (tier0/content/encounters/battery.yaml:37-51) — but live in the real game's multi-body boss rooms.

### klee-mod/KleeCode/Powers/FurinaResources.cs — 5 finding(s)
*legs read: klee-mod/KleeCode/Powers/FurinaResources.cs:1-1202; klee-mod/KleeCode/Powers/SpotlightSystem.cs:55-70,340-360; klee-mod/KleeCode/Cards/Furina/Generated/UnheardConfession.cs:40-80; klee-mod/KleeCode/Cards/Furina/AllTheWorldsAStage.cs:1-70; tier0/engine/resources.py:1-407; tier0/engine/combat.py:30-70,180-320,400-520,530-560,655-700,780-845*
1. **[MEDIUM · semantic_drift]** FanfareCap is computed from the creature's CURRENT MaxHp, so it grows whenever Furina gains max HP during a run. tier0 derives fanfare_cap once from the character sheet's printed starting hp and rewinds to that snapshot at every fight start, never recomputing it against the run's grown max_hp — so the two engines disagree about the ceiling for any Furina who has taken a max-HP gain.
   - `klee-mod/KleeCode/Powers/FurinaResources.cs:348-352`
   - `tier0/content/loader.py:441-442`
   - `tier0/content/loader.py:484-485`
   - `tier0/engine/combat.py:806`
   - `tier05/model.py:544-553`
   - note: Furina prints hp 60 (tier0/content/characters/furina.yaml:9), so the sim's cap is pinned at 30 for the whole run while C# rises with MaxHp. tier05/model.py:553 assigns the run's grown max_hp AFTER build_player_from_ids has already frozen fanfare_cap from spec['hp'], and tier05 does grow max HP (tier05/events.py:376-378, tier05/draft.py:476). Impact is bounded by the F-A5 demotion of the cap to a non-binding rail (FurinaResources.cs:342-347), but the C# comment claims to mirror the sim's formula and does not.
2. **[LOW · semantic_drift]** The comment above the three play-time resource steps says the sim's order is 'the requires-full drain first, then the skill-tag bonus, then the Encore cost line', and the C# implements exactly that. tier0's play_card does the Encore cost FIRST, then the requires-full drain, then the skill-tag bonus — the Encore line is first in the sim, not last.
   - `klee-mod/KleeCode/Powers/FurinaResources.cs:764-766`
   - `klee-mod/KleeCode/Powers/FurinaResources.cs:781-786`
   - `tier0/engine/combat.py:207-208`
   - `tier0/engine/combat.py:247-248`
   - `tier0/engine/combat.py:250-251`
   - note: No behavioural difference today: the only requires-full card, let_the_people_rejoice (docs/furina-cards.yaml:662-663), carries no encore_cost, and skill-tag vs encore-spend Burst gains commute. It becomes a real divergence the moment a card carries both — sim would zero the meter after the Encore spend credited it, C# credits it after the zero. Same doc block also cites 'combat.py play_card line 180' at FurinaResources.cs:103-104; play_card starts at line 182 and the spend is at 208.
3. **[LOW · other]** Two consecutive `<summary>` blocks are stacked on DropFanfareToFloor: the first is GainEncore's documentation ('Fill the buffer. Prints NO Fanfare...'), the second is the Hyperbeam settle's. GainEncore itself (the method the first block describes, and tier0's gain_encore counterpart) is left with no doc comment, and DropFanfareToFloor's IDE/API doc leads with a sentence about filling the Encore buffer that is false for a method that crashes the Fanfare meter.
   - `klee-mod/KleeCode/Powers/FurinaResources.cs:521-526`
   - `klee-mod/KleeCode/Powers/FurinaResources.cs:551`
   - `klee-mod/KleeCode/Powers/FurinaResources.cs:572`
   - `tier0/engine/resources.py:264-273`
   - `tier0/engine/resources.py:191-212`
   - note: Behaviour is unaffected — DropFanfareToFloor's own body matches resources.drop_fanfare_to_floor. This is the Track A rewrite leaving the gain_encore mirror-doc orphaned when the GainFanfare call was removed from it.
4. **[LOW · semantic_drift]** EncorePerTurnPower's class doc says its grant is routed through FurinaResources.GainEncore 'so the Fanfare mint, gauge refresh and salon dry-badge all behave exactly like any other gain'. There is no Fanfare mint on GainEncore any more — Track A deleted the encore_gained leg on both sides, as this same file states 12 lines from the method.
   - `klee-mod/KleeCode/Powers/FurinaResources.cs:1104-1111`
   - `klee-mod/KleeCode/Powers/FurinaResources.cs:521-524`
   - `klee-mod/KleeCode/Powers/FurinaResources.cs:572-582`
   - `tier0/engine/resources.py:264-276`
   - note: The same stale claim appears on the card at klee-mod/KleeCode/Cards/Furina/AllTheWorldsAStage.cs:24 ('every point gained mints Fanfare'). Player-facing text is correct — the FanfareMeterPower tooltip (FurinaResources.cs:1045-1049) and the card description carry the single-leg wording. tier0/tests/test_furina.py:452-465 pins the deletion at the funnel.
5. **[LOW · sim_vs_csharp_divergence]** tier0's crash settles the meter with `max(floor, min(fanfare, floor))`, which is unconditionally the new floor — it raises a sub-floor meter up onto the floor as well as dropping a high one. The C# uses `Math.Min(before, floor.Amount)`, which only ever moves the meter down, so a meter already below the floor stays below it.
   - `klee-mod/KleeCode/Powers/FurinaResources.cs:556-561`
   - `tier0/engine/resources.py:216-219`
   - note: I could not construct a reachable state where Fanfare sits below its floor — GainFanfareFloor raises the cap alongside the floor (FurinaResources.cs:479-481, tier0/engine/resources.py:164-166), so the cap clamp cannot strand the meter under the floor. Recorded for coverage rather than as a live defect. Also noting, without filing: the Salon-upkeep vs EncorePerTurnPower same-broadcast ordering race is a known, deliberately-open ruling ask (docs/sprint-bugfix-log-2026-07-29.md:248-275, docs/backlog-2026-07-29.md:63) with no tier0 counterpart to disagree with — All the World's a Stage is Ancient, game-side-only content by DECISIONS 2026-07-23, so its absence from tier0 is CLEAN, not a missing leg. EncoreMeterPower and FurinaBurstMeterPower are C#-only save-compat shells that nothing applies (FurinaResources.cs:1006-1011, 1056-1060): CLEAN. Constants BurstPerSkillTag 5 / BurstPerReaction 5 / BurstPerEncoreSpent 1 / BurstPerSalonTick 2 / BurstMax 70 / FanfarePerHpLost 1 / FanfarePerEncoreSpent 1 / FanfarePerEncoreAbsorbed 1 / FanfareDecayFraction 0.20 all match tier0/constants.py:69-70,180-182,208,303-305 and furina.yaml:14. Decay rounding (ToEven vs Python round), the turn<2 gate, the min-1 floor, the four NoteFanfareChanged call sites, the Unpowered A7 payout, the Unblockable self-damage exclusion from AbsorbDamage, and FurinaKitGrant's full-hand defer all verified equivalent.

### klee-mod/KleeCode/Powers/GuestStarGenerator.cs — 2 finding(s)
*legs read: klee-mod/KleeCode/Powers/GuestStarGenerator.cs:1-56; klee-mod/KleeCode/Cards/Generated/CompanionRoster.cs:1-60; klee-mod/KleeCode/Cards/Furina/Generated/GuestStarRoster.cs:1-23; klee-mod/KleeCode/Cards/Furina/Generated/AnInvitation.cs:40-70; klee-mod/KleeCode/Cards/Furina/Generated/GuestList.cs:40-70; klee-mod/KleeCode/Cards/Furina/Generated/CommandPerformance.cs:40-70*
1. **[MEDIUM · sheet_vs_sim_divergence]** The upgraded generators are specified as Discovery parity — the guest costs 0 this turn — and the C# implements exactly that with EnergyCost.SetThisTurn. tier0's _generate assigns `pick.cost = fx['cost_override']` on the token itself, which is permanent for the token's whole combat life, so a guest held past the turn it was created still costs 0 in the sim and costs its printed price in-game.
   - `klee-mod/KleeCode/Powers/GuestStarGenerator.cs:48-51`
   - `tier0/engine/effects.py:1205-1206`
   - `docs/furina-upgrades.yaml:79`
   - `docs/furina-upgrades.yaml:128`
   - `docs/furina-upgrades.yaml:162`
   - `klee-mod/KleeCode/Cards/Furina/Generated/AnInvitation.cs:47`
   - note: tier0's own inline comment on the assignment reads '# upgraded form: 0 this turn', so the sim's code contradicts its own comment as well as the sheet. The sheet is the intent authority here and it says 'kickoff §9 upgrade grammar VERBATIM' / 'Discovery parity', which is StS Discovery's 'it costs 0 this turn' — the C# is the side that matches. Affects an_invitation+, guest_list+ and command_performance+ (2 guests). The same tier0 line serves generate_from_pool, so the drift is not Furina-only.
2. **[LOW · sim_vs_csharp_divergence]** tier0's guest_star_generation_pool filters `(c.is_companion or c.guest_star) and c.rarity == rarity and not c.kit_card`. The C# pool is CompanionRoster.All concat GuestStarRoster.All filtered by rarity only — the kit-card exclusion that tier0 states as one of the four structural guardrails has no counterpart in the generator.
   - `klee-mod/KleeCode/Powers/GuestStarGenerator.cs:32-36`
   - `tier0/content/loader.py:293-295`
   - note: Currently inert: I enumerated both rosters (CompanionRoster.cs:22-60+, GuestStarRoster.cs:17-22) and neither contains a kit card, so the two pools agree today. Filed low as a latent guardrail gap — the C# relies on roster membership discipline where the sim relies on an explicit predicate. Also verified CLEAN and not filed: the equal-rarity clause (GuestStarGenerator.cs:22-34 vs loader.py:293-295) matches; the `to`/zone parameter and the `upgraded` flag that tier0's _generate supports (effects.py:1198-1207) are unused by all three generate_guest_star rows (docs/furina-cards.yaml:298, 520, 801), so hardcoding PileType.Hand is correct; the OrderBy(Id) vs sorted(key=id) difference only affects each engine's own RNG determinism, not cross-engine parity, since the streams differ regardless.

### klee-mod/KleeCode/Powers/IBombDetonationListener.cs — 1 finding(s)
*legs read: klee-mod/KleeCode/Powers/IBombDetonationListener.cs:1-25 (whole file); klee-mod/KleeCode/Powers/BombPower.cs:441-540 (Detonate + NotifyDetonationListeners); klee-mod/KleeCode/Powers/DemolitionPowers.cs:60-152 (DetonationSplashPower, DetonationVulnPower); klee-mod/KleeCode/Relics/PoundingSurprise.cs:25-80; klee-mod/KleeCode/Relics/UpgradedStarterRelics.cs:110-175 (ExplosiveFrags); tier0/engine/effects.py:432-476 (_detonate_bombs_on_hit, detonate_bombs)*
1. **[LOW · other]** The interface's "Known subscribers" doc lists only PoundingSurprise and Blazing Delight's splash, but four types implement IBombDetonationListener today -- the ExplosiveFrags (Dodoco Tales) relic and DetonationVulnPower are both live subscribers and are unlisted, so the file that exists to document the event bus under-reports it by half.
   - `klee-mod/KleeCode/Powers/IBombDetonationListener.cs:14-15 ("Known subscribers: PoundingSurprise (+1 Spark); Blazing Delight's splash joins when its power lands (C3).")`
   - `klee-mod/KleeCode/Relics/UpgradedStarterRelics.cs:118 (public sealed class ExplosiveFrags : CustomRelicModel, IBombDetonationListener)`
   - `klee-mod/KleeCode/Powers/DemolitionPowers.cs:129-130 (public sealed class DetonationVulnPower : PowerModel, ILocalizationProvider, IBombDetonationListener)`
   - `tier0/engine/effects.py:473-475 (vuln = p.powers.get("detonation_vuln", 0)  # Explosive Frags -- the sim's per-bomb vuln leg the C# routes through this bus)`
   - note: Comment-only drift; behaviour is correct. Everything else on this entity verified CLEAN: the "once PER BOMB" claim holds (BombPower.cs:466-486 fires the notify inside the per-payload foreach, matching the sim's per-bomb loop at effects.py:442-475), and the "discovered by interface test over the applying player's relics and creature powers, no registration step" claim holds (BombPower.cs:501-517). The `damage` argument is documented as "That single bomb's payload" and is indeed the raw payload, excluding the Explosives Workshop bonus and bomb_damage_up that the sim folds in at effects.py:443 -- no divergence today because no listener reads the argument, so not filed. No tier0 counterpart is expected: the sim inlines the spark/splash/vuln legs directly in detonate_bombs, so this interface is a C#-side structural device, not a missing sim leg.

### klee-mod/KleeCode/Powers/KitBurst.cs — 1 finding(s)
*legs read: klee-mod/KleeCode/Powers/KitBurst.cs:1-165 (whole file); tier0/constants.py:11 (MAX_HAND_SIZE), :73-74 (SPARKS_N_SPLASH_HITS/HIT_DMG); tier0/engine/effects.py:2463-2501 (player_turn_end_triggers, sparks_n_splash block); tier0/engine/effects.py:351-429 (deal_damage_to_enemy), :1320-1400 (_op_discard/_op_exhaust_from), :1474-1496 (_op_discard_for_sparks), :1222-1241 (_op_copy_spotlighted_in_hand), :2140-2150 (_op_remember_card); tier0/engine/combat.py:30-52 (grant_charged_kit), :296-320, :460-475, :525-570 (three call sites + turn-end order); tier0/engine/powers.py:26-72 (_floor, modify_damage_dealt/taken)*
1. **[MEDIUM · sim_vs_csharp_divergence]** The kit-card invariant KitGrant.NotKitCard exists to enforce is applied only at discard/exhaust-from-hand sites, but the sim also exempts kit cards from the spotlight-copy pool; C# Encore Performance has no such filter, so Furina's kit Burst can be duplicated into hand -- the copy is then undiscardable (NotKitCard) and permanently clogs a hand slot, and it also blocks the hand-only re-grant dedup.
   - `tier0/engine/effects.py:1231-1232 (targets = [c for c in p.hand if is_spotlighted(state, c) and not c.kit_card])`
   - `klee-mod/KleeCode/Cards/Furina/Generated/EncorePerformance.cs:64-65 (var spotlightTargets = CardPile.Get(PileType.Hand, Owner)?.Cards.Where(SpotlightSystem.IsSpotlighted).ToList(); -- no kit filter)`
   - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:214-221 (IsSpotlighted returns true for any ICharacterCard{CharacterId:"furina"} under Center Stage)`
   - `klee-mod/KleeCode/Cards/Furina/LetThePeopleRejoice.cs:21-26 (kit Burst is ICharacterCard with CharacterId => "furina")`
   - `klee-mod/KleeCode/Powers/KitBurst.cs:141-144 (NotKitCard, the C# home of the kit exemption, is not consulted at that site)`
   - `klee-mod/KleeCode/Powers/FurinaResources.cs:1092 (grant dedup is hand-only, so a stray copy suppresses re-grants)`
   - note: Flagged on this entity because KitGrant.NotKitCard (KitBurst.cs:134-144) is the C# owner of the v1.9 kit invariant; the code site that needs the filter lives in another group's file (EncorePerformance.cs). Everything else on KitBurst.cs verified CLEAN and is worth recording: VolleyHits=4 / VolleyHitDamage=5 match tier0/constants.py:73-74 and are pinned by tools/lint_constant_parity.py:131-132; the volley-then-tick order matches effects.py:2493-2500 (hits loop, then p.powers["sparks_n_splash"] -= 1) including the all-enemies-dead break-then-still-tick case; per-hit re-snapshot of HittableEnemies mirrors the sim's per-iteration state.living_enemies read; BeforeSideTurnEnd is the right phase (combat.py:538-539 puts player_turn_end_triggers after site I BeforeSideTurnEndEarly and before the flush); the grant gate resource >= 40 matches klee.yaml:11 burst_max: 40 via BurstConstants.KleeMax (BurstResource.cs:28); hand-full defer matches MAX_HAND_SIZE=10 (constants.py:11) and the sim's `return` rather than drop (combat.py:48-51); the three grant check sites match combat.py:316/472/555; NotKitCard's three types are exactly the three kit_card rows in the sheets (klee-cards.yaml:186, furina-cards.yaml:662, kokomi-cards.yaml:514). The "single truncation" claim in the class doc also holds -- tier0 _floor (powers.py:26-39) is a zero-clamp, not an integer floor, so effects.py:374 int(dmg) is the only truncation, matching ElementalHit.cs:54-56. Power tooltip text matches the sheet note and the card face (SparksNSplash.cs:42-47).

### klee-mod/KleeCode/Powers/KleePowerIcons.cs — 1 finding(s)
*legs read: klee-mod/KleeCode/Powers/KleePowerIcons.cs:1-177 (whole file; switch cases 28-127, IconExempt 130-139, Harmony patches 142-176); klee-mod/KleeCode/Diagnostics/KleeSelfCheck.cs:50-120, 384-436 (R13 CheckPowerIcons, Fail); klee-mod/KleeCode/KleePck.cs:26-65 (Path existence gate); klee-mod/KleeCode/Powers/*.cs class declarations (enumerated all concrete PowerModel subclasses in KleeCode.csproj: CompanionPowers.cs:106-512, SalonPowers.cs:57-515, SpotlightSystem.cs:395-599, KuragePowers.cs:30-380, FontainePowers.cs:45-166, FurinaResources.cs:1012-1185, AuraPower.cs:34-204, SparkKitPowers.cs:20-85, KokomiResources.cs:421, ReactionKitPowers.cs:31-54, KitBurst.cs:57, CurtainCallPowers.cs:284-383, FrozenPower.cs:30, BurstResource.cs:251, SparkPower.cs:41, BombPower.cs:47, DemolitionPowers.cs:41-169); art/plan.tsv (power-icon rows), art/SOURCES.tsv*
1. **[MEDIUM · missing_leg]** Twelve concrete PowerModel subclasses in this assembly have neither a case in PathFor nor an IconExempt entry, so they fall through `_ => null` and render the base-game placeholder -- the exact failure this file exists to prevent -- and each one trips R13 at every boot. The whole of Kokomi's Kurage/Ceremonial Garment set and the entire Fontaine power set are affected.
   - `klee-mod/KleeCode/Powers/KleePowerIcons.cs:127 (`_ => null,` -- the fall-through)`
   - `klee-mod/KleeCode/Powers/KleePowerIcons.cs:130-139 (IconExempt lists only EncoreMeterPower, FurinaBurstMeterPower, SpotlightPower, and its doc asserts "R13 fails on any other iconless PowerModel in this assembly")`
   - `klee-mod/KleeCode/Powers/KleePowerIcons.cs:122-126 ("EncoreMeterPower and FurinaBurstMeterPower are absent on purpose" -- claims those are the only deliberate absences)`
   - `klee-mod/KleeCode/Diagnostics/KleeSelfCheck.cs:399-402 (R13 enumerates every non-abstract PowerModel in the assembly minus IconExempt)`
   - `klee-mod/KleeCode/Diagnostics/KleeSelfCheck.cs:421-426 (Fail("R13", ... "no icon mapping, so it renders the base-game placeholder"))`
   - `klee-mod/KleeCode/Powers/KuragePowers.cs:30 (KurageSummonPower), :176 (KurageWardPower), :227 (KurageAmpPower), :272 (CeremonialGarmentPower), :380 (PreventExhaustWardPower)`
   - note: All twelve are `public sealed class X : PowerModel, ILocalizationProvider` with no declared constructor, so Activator.CreateInstance succeeds and R13's skip-on-no-parameterless-ctor branch (KleeSelfCheck.cs:410-418) does NOT cover them; every one reaches the Fail at KleeSelfCheck.cs:423. Findings are logged as errors and counted rather than thrown (KleeSelfCheck.cs:102-104), so this is degraded art plus permanent boot-log noise, not a crash -- hence medium rather than high. Verified CLEAN on the rest of the file: 46 named cases, no base-before-derived shadowing (the only inheritance in play is the abstract SpotlightPower, which has no case, and AuraPower at :119 whose four concrete subclasses are matched by the pattern itself); the Harmony prefixes at :142-176 correctly return true on a null path so a missing PNG falls through to the original getter, which is what makes the wire-paths-ahead-of-art policy safe. No tier0/tier05 or sheet leg is expected for this entity -- it is a pure C#-side UI helper with no sim or spec counterpart, so its one-sided existence is CLEAN by the group rule.

### klee-mod/KleeCode/Powers/KokomiConscript.cs — CLEAN
*legs read: klee-mod/KleeCode/Powers/KokomiConscript.cs:1-167; tier0/engine/effects.py:1997-2039 (_op_conscript); tier0/engine/effects.py:483-493 (_add_token); tier0/engine/effects.py:2196 (op table); tier0/engine/state.py:141-145 (Card.conscripted); tier0/engine/refpowers.py:285-294 (exhaust funnel muster bucket)*

### klee-mod/KleeCode/Powers/KokomiResources.cs — 1 finding(s)
*legs read: klee-mod/KleeCode/Powers/KokomiResources.cs:1-554; klee-mod/KleeCode/Relics/UpgradedStarterRelics.cs:224-300; klee-mod/KleeCode/Powers/BurstResource.cs:22; klee-mod/KleeCode/Powers/ReactionEffects.cs:160-186; tier0/constants.py:69-70,310-370,401-403,479-492; tier0/content/characters/kokomi.yaml:1-60*
1. **[MEDIUM · missing_leg]** Kokomi's upgraded starter doubles her per-exhaust Charge AND Burst accrual game-side, but tier0 has no way to express that: the exhaust funnel hardcodes the base constants and relics.py exposes no hook for an accrual-rate change, so every simulated Kokomi run is measured at the un-upgraded rate.
   - `klee-mod/KleeCode/Relics/UpgradedStarterRelics.cs:241-242`
   - `klee-mod/KleeCode/Powers/KokomiResources.cs:312-320`
   - `tier0/engine/refpowers.py:290-294`
   - `tier0/engine/relics.py:43-50`
   - note: C#: ExhaustCharge/ExhaustBurst return PearlOfInsightRelic.ChargePerExhaust (=2) / BurstPerExhaust (=4) whenever the relic is held. tier0: after_card_exhausted always grants C.CHARGE_PER_EXHAUST (1) and C.KOKOMI_BURST_PER_EXHAUST (2), and relics.COMBAT_HOOKS contains no rate hook a `starting_relic_effects` row could use. Contrast Klee, whose upgraded starter IS expressible (tier0/engine/relics.py:137-155, combat_start_spark) — so the asymmetry is a gap rather than a general 'sim models no upgraded starters' rule. Consequence is measurement-side, not a wrong in-game number: burst_max 20 was picked against a W2 bracket (tier0/content/characters/kokomi.yaml burst_max block) that can never contain a doubled-accrual run.

### klee-mod/KleeCode/Powers/KuragePowers.cs — 5 finding(s)
*legs read: klee-mod/KleeCode/Powers/KuragePowers.cs:1-514; klee-mod/KleeCode/Cards/Kokomi/CeremonialGarment.cs:95-145; klee-mod/KleeCode/Cards/Kokomi/Generated/VigilOfTheDeep.cs:40-68; klee-mod/KleeCode/Cards/Kokomi/Generated/NereidsAscension.cs:1-100; tier0/engine/effects.py:2041-2071 (prevent_damage_exhaust); tier0/engine/effects.py:2507-2556 (kurage pulse)*
1. **[HIGH · sim_vs_csharp_divergence]** prevent_exhaust_ward is capped at 6 by the sheet and honoured by tier0, but PreventExhaustWardPower declares no cap at all (plain Counter stacking), so a second Vigil of the Deep doubles the ward game-side while the sim holds it at the cap.
   - `docs/kokomi-cards.yaml:544`
   - `tier0/engine/effects.py:803`
   - `tier0/engine/powers.py:167-169`
   - `klee-mod/KleeCode/Powers/KuragePowers.cs:393`
   - `klee-mod/KleeCode/Cards/Kokomi/Generated/VigilOfTheDeep.cs:62`
   - `tools/gen_klee_cards.py:452-455`
   - note: Failure: draft two copies of Vigil of the Deep. tier0 — _op_apply_power reads `cap = fx.get('max_stacks')` (6) and apply_power clamps `new = min(new, max_stacks)`, so the ward stays at 6. C# — VigilOfTheDeep.OnPlay calls PowerCmd.Apply<PreventExhaustWardPower>(…, 6) with no cap argument and the power class has no MaxAmount/cap const, only PowerStackType.Counter, so the ward reaches 12 (or 14 with an upgraded second copy, OnUpgrade +2). The generator registry entry is `("PreventExhaustWardPower", 6, …)` and its own drift check (gen_klee_cards.py:1144-1150) only compares the sheet against the registry — 'caps are enforced in the power class' per tools/lint_handwritten_parity.py:102-105 — so nothing checks the C# side, which is why this stayed green. prevent_exhaust_ward is the ONLY capped entry in APPLY_POWERS.
2. **[HIGH · sim_vs_csharp_divergence]** The ward's reduction is applied in the pre-Block additive phase in C# but post-Block in tier0, so a fully-blocked attack burns the once-per-turn latch and mills a draw-pile card game-side while the sim leaves the ward untouched.
   - `klee-mod/KleeCode/Powers/KuragePowers.cs:462-472`
   - `klee-mod/KleeCode/Powers/KuragePowers.cs:445-453`
   - `klee-mod/KleeCode/Powers/KuragePowers.cs:482-513`
   - `tier0/engine/combat.py:650-661`
   - `tier0/engine/effects.py:2059-2070`
   - `tier0/engine/powers.py:27-29`
   - note: Failure: player has 10 Block and Vigil 6; enemy attacks for 8. tier0 — combat.py:651-652 blocks all 8, so prevent_damage_exhaust is called with `dmg - blocked` = 0 and returns at effects.py:2059-2060 without setting prevention_used_this_turn and without exhausting anything; the ward is still live for a later hit that same round. C# — ModifyDamageAdditive runs before Block (powers.py:27-29 states the whole modifier chain resolves 'BEFORE the number ever reaches Creature.DamageBlockInternal', and KuragePowers.cs:469 asserts the same), so it returns -6 on the raw 8; then AfterDamageReceived reads `_incomingThisHit` = 8 (the RAW amount captured at KuragePowers.cs:452, pre-Block), passes the `incoming <= 0` test at :492, sets `_usedThisTurn = true` at :506 and exhausts a random draw-pile card at :507-512. The player loses a card and the round's prevention to an attack that never reached them, and the exhaust additionally pays Charge/Burst through the funnel.
3. **[MEDIUM · semantic_drift]** Because the C# ward subtracts before Block instead of after it, Block is consumed against the already-reduced number, leaving the player with Block the sim spends.
   - `klee-mod/KleeCode/Powers/KuragePowers.cs:471`
   - `tier0/engine/combat.py:651-661`
   - `tier0/engine/powers.py:27-29`
   - note: Failure: 10 Block, Vigil 6, incoming 10. tier0 — blocked = min(10,10) = 10, block drops to 0, unblocked 0, ward does not proc. C# — additive phase takes 10 down to 4, Block absorbs 4, player keeps 6 Block AND (per the previous finding) burns the ward plus a card. Same family of phase error as the finding above but a separately observable number: the resource the player ends the enemy turn holding differs between the two legs even when HP loss agrees.
4. **[MEDIUM · text_ops_mismatch]** Vigil's tooltip and the sheet both scope the ward to 'unblocked attack damage', and tier0 only ever calls it from the enemy attack branch, but the C# implementation filters on neither attack-ness nor source and so fires on any damage the owner receives.
   - `klee-mod/KleeCode/Powers/KuragePowers.cs:385-388`
   - `klee-mod/KleeCode/Powers/KuragePowers.cs:462-472`
   - `docs/kokomi-cards.yaml:544`
   - `tier0/engine/combat.py:634-661`
   - `tier0/engine/combat.py:545-553`
   - note: tier0 calls prevent_damage_exhaust only inside `if kind == 'attack':` (combat.py:634 → :661). Injected Burn/Wither end-of-turn damage is applied directly against Block and HP at combat.py:546-551 with no ward call, and card self-damage is a raw `state.player.hp -=` (effects.py:502-505). The C# ModifyDamageAdditive at KuragePowers.cs:462-472 checks only `target != Owner`, the latch, `amount > 0` and fuel — no `props.IsPoweredAttack()` and no `cardSource.Type == Attack` filter, both of which the sibling power in the same file uses (CeremonialGarmentPower, KuragePowers.cs:318-319). So a Burn tick or a self-damage card triggers the ward, contradicting the printed text and consuming a draw-pile card the sheet never priced.
5. **[LOW · other]** CeremonialGarmentPower's doc comment says Nereid's Ascension also enters the Garment state; neither leg applies the power from that card any more.
   - `klee-mod/KleeCode/Powers/KuragePowers.cs:244-246`
   - `klee-mod/KleeCode/Cards/Kokomi/Generated/NereidsAscension.cs:53-60`
   - `docs/kokomi-cards.yaml:532-533`
   - note: Comment drift, no behavioural consequence. Nereid's Ascension's OnPlay only runs DamageCmd.Attack, and the sheet row's effects list is a single damage op with bonus_formula 1_per_2_charge. The Garment is entered solely by the kit card (docs/kokomi-cards.yaml:514-516). Reads as leftover from the pre-R74 'Shape A capstone' design.

### klee-mod/KleeCode/Powers/ReactionEffects.cs — 4 finding(s)
*legs read: klee-mod/KleeCode/Powers/ReactionEffects.cs:1-320 (full); klee-mod/KleeCode/Powers/FrozenPower.cs:1-120 (full); klee-mod/KleeCode/Powers/ElementalHit.cs:1-88 (full); klee-mod/KleeCode/Powers/ElementalApplication.cs:110-185, 234-282; klee-mod/KleeCode/Powers/AuraPower.cs:34-100, 155-180; klee-mod/KleeCode/Elements/ReactionTable.cs:28-129*
1. **[HIGH · sim_vs_csharp_divergence]** Frozen's boss substitution (Vulnerable instead of Frozen) is scoped to the ROOM in C# but to the individual CREATURE in tier0 and in the design doc, so every non-boss add sharing a boss room is un-freezable in game and freezable in the sim.
   - `klee-mod/KleeCode/Powers/ReactionEffects.cs:208`
   - `tier0/engine/reactions.py:123`
   - `docs/teyvat-spire-design-principles.md:48`
   - `klee-mod/KleeCode/Cards/KleeCardTooltips.cs:51`
   - `tier0/engine/state.py:423`
   - note: The design doc row reads 'Bosses: Vulnerable 2 instead' — a creature-level statement — and tier0 backs it with a per-Enemy `is_boss` field (state.py:423, set from the encounter yaml). tier0's own battery cannot distinguish the two scopes (tank_boss is the only is_boss encounter and it is single-enemy, tier0/content/encounters/battery.yaml:39-52), which is plausibly why the room-level shortcut survived. C# is internally consistent (impl and tooltip use the same predicate); the disagreement is with the sim and the sheet.
2. **[MEDIUM · sim_vs_csharp_divergence]** Frozen is a stacking Counter on a turn-end clock in C# but a one-shot boolean consumed by the enemy's action in tier0, so double-freezing extends the debuff in game and a sleeping enemy loses it in game but keeps it in the sim.
   - `klee-mod/KleeCode/Powers/ReactionEffects.cs:217`
   - `klee-mod/KleeCode/Powers/FrozenPower.cs:43`
   - `klee-mod/KleeCode/Powers/FrozenPower.cs:112`
   - `tier0/engine/reactions.py:128`
   - `tier0/engine/combat.py:621`
   - `tier0/engine/combat.py:593`
   - note: FrozenPower.ModifyDamageMultiplicative returns the flat 0.5 regardless of Amount, so damage is not double-reduced — only the duration diverges. The application site is in my file; the stacking/expiry rules live in FrozenPower.cs, which may also be another agent's entity.
3. **[LOW · sim_vs_csharp_divergence]** Crystallize's Block bypasses both of tier0's block funnels and emits no block event, while C# routes it through CreatureCmd.GainBlock and the engine's block hooks.
   - `tier0/engine/reactions.py:102`
   - `klee-mod/KleeCode/Powers/ReactionEffects.cs:298`
   - `tier0/engine/refpowers.py:194`
   - `tier0/engine/effects.py:729`
   - note: Constant value itself is correct on both sides (CRYSTALLIZE_BLOCK 4 == ReactionConstants.CrystallizeBlock). Low because shadowmeld is a base-game parity ref-power that a Klee/Furina/Kokomi deck cannot obtain today; the accounting gap (crystallize block missing from the block axis) is the concrete effect.
4. **[LOW · sim_vs_csharp_divergence]** The Catalytic Conversion bonus Burst is credited only to Klee's meter in C#, while the flat +5 on the same funnel fans out to all three meters and tier0 credits both through the same character-agnostic gain_burst.
   - `klee-mod/KleeCode/Powers/ReactionEffects.cs:183`
   - `klee-mod/KleeCode/Powers/ReactionEffects.cs:159`
   - `tier0/engine/reactions.py:150`
   - `tier0/engine/reactions.py:145`
   - note: Latent, not live: catalytic_conversion is a Klee-only sheet entry (docs/klee-cards.yaml:155) and its Spark half is Klee's resource anyway, so no character can currently reach the asymmetric path. Filed because the two grants sit four lines apart on the same funnel with opposite fan-out, and the flat +5's own comment argues the rule is universal.

### klee-mod/KleeCode/Powers/ReactionKitPowers.cs — 2 finding(s)
*legs read: klee-mod/KleeCode/Powers/ReactionKitPowers.cs:1-67 (full); klee-mod/KleeCode/Powers/ReactionEffects.cs:151-188; klee-mod/KleeCode/Elements/ReactionTable.cs:94-129; klee-mod/KleeCode/Powers/SparkPower.cs:55-120; klee-mod/KleeCode/Cards/Generated/CatalyticConversion.cs:1-69 (full); tier0/engine/reactions.py:28-40, 131-155*
1. **[LOW · other]** The 'NO UPGRADE PATH / marked UNAPPLIABLE' note on ReactionBonusSparkEnergyPower is stale: catalytic_conversion left UNAPPLIABLE at R37, the sheet gives it an Innate upgrade, and the generated card already ships it.
   - `klee-mod/KleeCode/Powers/ReactionKitPowers.cs:26`
   - `docs/klee-upgrades.yaml:63`
   - `tier0/content/upgrades.py:57`
   - `tier0/content/upgrades.py:72`
   - `klee-mod/KleeCode/Cards/Generated/CatalyticConversion.cs:65`
   - note: Shipped behavior is correct on both sides; only the doc comment is wrong. The sibling claim it leans on ('same disposition as hot_hands') should be re-checked separately — it is outside this group.
2. **[LOW · text_ops_mismatch]** The Catalytic Conversion tooltip mixes a stack-scaled term with a per-stack rate under one trailing 'per stack', so the Spark half over-promises at 2+ stacks.
   - `klee-mod/KleeCode/Powers/ReactionKitPowers.cs:36`
   - `klee-mod/KleeCode/Powers/ReactionEffects.cs:182`
   - `klee-mod/KleeCode/Powers/ReactionEffects.cs:184`
   - `tier0/engine/reactions.py:149`
   - note: Values are correct on both sides — Sparks = Amount, Burst = 5 x Amount, matching CATALYTIC_BURST_PER_REACTION = 5. Purely a wording collision, and only visible once a duplicate is drafted (the card has no Amount-raising upgrade). The generated card's own face text (CatalyticConversion.cs:39) hardcodes '1 extra Spark and 5 extra Burst Energy' and does not have the problem. AmpReactionUpPower (Vermillion Pact) was checked and is CLEAN: 'amplify {Amount}% more' with base * (1 + pct/100) matches ReactionTable.cs:118 and reactions.py:33-36, and the +25 upgrade (docs/klee-upgrades.yaml:86) puts Melt at 3.9375, just under AmpStackLimit 4.0 exactly as both comments claim.

### klee-mod/KleeCode/Powers/SalonPowers.cs — 3 finding(s)
*legs read: klee-mod/KleeCode/Powers/SalonPowers.cs:1-531 (full); klee-mod/KleeCode/Powers/CurtainCallPowers.cs:263-323; klee-mod/KleeCode/Powers/FurinaResources.cs:85-95, 285-360, 460-640, 838-910; klee-mod/KleeCode/Powers/ElementalHit.cs:26-88; klee-mod/KleeCode/Powers/ElementalApplication.cs:118-131; tier0/engine/effects.py:700-800, 1118-1150, 2330-2440*
1. **[MEDIUM · semantic_drift]** Salon upkeep resolves in a different turn-start phase: tier0 ticks the salon BEFORE the hand draw, C# ticks it in AfterPlayerTurnStart, which this codebase documents as firing AFTER the hand draw.
   - `klee-mod/KleeCode/Powers/SalonPowers.cs:413`
   - `klee-mod/KleeCode/Powers/ElementalApplication.cs:120`
   - `tier0/engine/effects.py:2352`
   - `tier0/engine/combat.py:453`
   - `tier0/engine/combat.py:463`
   - `tier0/engine/combat.py:466`
   - note: Ordinary turns land on the same totals; the divergence bites at the hand-size cap and in any read that samples between the two phases. Ordering relative to bomb detonation is fine on both sides (bombs at combat.py:446-448 / BeforeSideTurnStart, both strictly before the salon). Everything else in the tick was verified equal: the pay-or-dry gate, 0.75 truncation, per-member break on dead player / no living enemies, random hydro target for Crabaletta and Chevalmarin, Usher block, and SALON_TICK_BURST 2 per tick and per bow.
2. **[LOW · other]** tier0 still documents the Salon tick as an HP-overdraw site in two places; neither engine has done that since the dry-tick rule, and both now pay-or-go-dry.
   - `tier0/engine/resources.py:318`
   - `tier0/engine/effects.py:2412`
   - `tier0/engine/combat.py:454`
   - `klee-mod/KleeCode/Powers/SalonPowers.cs:423`
   - note: Sim and C# agree on behavior; this is stale prose inside tier0 describing v1 salon upkeep. Filed under this entity because it is the salon-upkeep leg's documentation.
3. **[LOW · other]** WillReplace's closed-form proof comment still reasons in the base constant MemberSlots after A12 promoted the cap to the per-player SlotsFor, so the comment's stated answer is wrong whenever Casting Call is in play.
   - `klee-mod/KleeCode/Powers/SalonPowers.cs:281`
   - `klee-mod/KleeCode/Powers/SalonPowers.cs:274`
   - `klee-mod/KleeCode/Powers/SalonPowers.cs:288`
   - `tier0/engine/effects.py:783`
   - note: The remarks block immediately above (SalonPowers.cs:261-268) correctly describes the A12 promotion, which is what makes the surviving MemberSlots algebra three lines later a pure editing miss. All salon constants were checked against tier0/constants.py:285-304 and match exactly (slots 3, focus-per 10, replace mults 2/3, tick cost 1, dry 0.75, 6/14, 3/9, 2/-, bow encore 3), as do the FIFO displacement, leftmost on-demand bow, per-deploy Fortissimo Guard, and post-burst unscaled Stagehands ordering. SalonDamageUpPower and SalonCapUpPower are CLEAN against salon_damage_up / salon_cap_up. CompanyOf, SyncSlotsDisplay, PurgeCompany, TickValue and BaseTick are C#-only UI/preview helpers with no sim counterpart needed — CLEAN, not missing_leg.

### klee-mod/KleeCode/Powers/SimDamagePipeline.cs — CLEAN
*legs read: klee-mod/KleeCode/Powers/SimDamagePipeline.cs:1-53; klee-mod/KleeCode/Powers/ElementalHit.cs:1-88 (sole consumer); klee-mod/KleeCode/Elements/ReactionTable.cs:28-58 (ReactionConstants); klee-mod/KleeCode/Powers/BombPower.cs:460-500; klee-mod/KleeCode/Powers/KitBurst.cs:80-100; klee-mod/KleeCode/Powers/CompanionPowers.cs:215-235*

### klee-mod/KleeCode/Powers/SparkKitPowers.cs — CLEAN
*legs read: klee-mod/KleeCode/Powers/SparkKitPowers.cs:1-98; klee-mod/KleeCode/Cards/Generated/SparkKnightStyle.cs:1-66; klee-mod/KleeCode/Cards/Generated/EndlessFireworks.cs:59; klee-mod/KleeCode/Cards/Generated/TrueSparkKnight.cs:59; klee-mod/KleeCode/Powers/KleePowerIcons.cs:28-37; tier0/engine/combat.py:24-27 (spark_threshold)*

### klee-mod/KleeCode/Powers/SparkPower.cs — 3 finding(s)
*legs read: klee-mod/KleeCode/Powers/SparkPower.cs:1-205; klee-mod/KleeCode/Powers/SparkKitPowers.cs:85-98; klee-mod/KleeCode/Powers/KleePowerIcons.cs:28; klee-mod/KleeCode/Cards/Generated/GleefulBarrage.cs:70, PatchedDress.cs:60, EagerToHelp.cs:60, Snap.cs:75, DaDaDa.cs:75, TrueSparkKnight.cs:59; klee-mod/DECISIONS.md:545-570, 963-968, 1242-1247; tier0/engine/combat.py:24-27, 122-182, 186-206, 330-400*
1. **[MEDIUM · text_ops_mismatch]** SparkPower's tooltip hardcodes the threshold as 3 on both clauses, but the implementation reads a live threshold that True Spark Knight lowers to 2 (floored at 1) -- so with SparkThresholdDownPower on the board the Spark tooltip states a number the game is not using, for both the free-attack gate and the spend.
   - `klee-mod/KleeCode/Powers/SparkPower.cs:60-62 -- ("description", "At 3 [gold]Sparks[/gold], your Attacks cost 0. " + "Playing one consumes 3 [gold]Sparks[/gold].") -- static text, no DynamicVar`
   - `klee-mod/KleeCode/Powers/SparkPower.cs:52-55 -- CurrentThreshold => Math.Max(1, Threshold - SparkThresholdDownPower.Amount), used by AppliesTo (:84) and by the spend snapshot (:125)`
   - `tier0/engine/combat.py:24-27 -- spark_threshold() returns max(1, SPARKS_FOR_FREE_ATTACK - spark_threshold_down), read at combat.py:172 (gate) and combat.py:199-201 (spend)`
   - `docs/klee-cards.yaml:202 -- true_spark_knight applies spark_threshold_down 1, note: "free attack at 2 sparks instead of 3"`
   - `klee-mod/KleeCode/Powers/SparkKitPowers.cs:90-92 -- SparkThresholdDownPower's own text does say "{Amount} fewer Spark(s) ... (minimum 1)"`
   - note: The MECHANIC is correct on both sides -- gate and spend both go through the same CurrentThreshold, exactly as the sim reads spark_threshold(state) at both sites. This is purely the Spark counter's own tooltip going stale under a power that is shipped and Rare-reachable. Grep found no separate Spark keyword loc row (no KleeKeywords entry, nothing spark-related in klee-mod/**/*.json beyond card manifests), so this description is the only place the player is told the threshold; the composite reading with True Spark Knight's own text is what keeps this at medium rather than high.
2. **[LOW · text_ops_mismatch]** The tooltip's "Playing one consumes 3 Sparks" applies unconditionally to "your Attacks", but two shipped attack classes never consume: printed-0 attacks (guarded by EnergyCost.Canonical != 0) and X-cost attacks (guarded by !CostsX). A player at threshold playing Flame on the Wick or Da-da-da! keeps the full bank, contrary to the text.
   - `klee-mod/KleeCode/Powers/SparkPower.cs:61-62 -- "At 3 [gold]Sparks[/gold], your Attacks cost 0. Playing one consumes 3 [gold]Sparks[/gold]."`
   - `klee-mod/KleeCode/Powers/SparkPower.cs:120-126 -- spend decision requires cardPlay.Card.EnergyCost.Canonical != 0, and AppliesTo (:83-87) requires !card.EnergyCost.CostsX`
   - `tier0/engine/combat.py:198-200 -- the sim's spend predicate carries the same two guards: `and card.cost != 0 and card.cost != "X"``
   - `docs/klee-cards.yaml:132-133 -- flame_on_the_wick, cost: 0, type: attack (shipped uncommon)`
   - `docs/klee-cards.yaml:203-204 -- da_da_da, cost: 0, type: attack (shipped rare)`
   - note: Behaviour is IDENTICAL to the sim and deliberate (SparkPower.cs:27-29 states the rule: "a free attack should not eat the charge"). Filed only as an under-specified-text item, and it errs in the player's favour, hence low. Not a sim divergence.
3. **[LOW · other]** SparkPower's class doc still advertises an X-cost divergence from the sim that R34 closed, and still claims Klee's X-cost cards are C3-blocked -- both statements were superseded by the mod's own DECISIONS log, so the file's stated rationale contradicts the shipped sim and the shipped codegen.
   - `klee-mod/KleeCode/Powers/SparkPower.cs:35-39 -- "The sim does apply sparks to X-attacks; divergence recorded in DECISIONS finding 26 rather than silently shipped. Klee's two X-cost cards are C3-blocked, so nothing observable differs yet."`
   - `tier0/engine/combat.py:198-200 -- the sim's spend predicate now ends `and card.cost != "X"`, i.e. the sim does NOT apply sparks to X-attacks`
   - `tier0/engine/combat.py:124-138 -- card_cost returns state.player.energy for an X card before the spark branch at :171-173, so an X attack is never spark-freed either`
   - `klee-mod/DECISIONS.md:559-566 -- "CLOSED by R34 (user-ratified 2026-07-20): the sim adopts the C# exemption ... No divergence remains."`
   - `klee-mod/DECISIONS.md:963-968 -- "R34 executed (X-cost spark exemption) ... The finding-26 divergence entry is CLOSED"`
   - `klee-mod/DECISIONS.md:1242-1247 -- "X cost (controlled_demolition; R34). HasEnergyCostX => true + ResolveEnergyXValue() ... SparkPower.AppliesTo already carried the R34 exemption (!CostsX)." -- X-cost has landed C#-side, so the C3-blocked claim is stale too`
   - note: Comment drift only: the CODE is correct and the two sides agree (both exempt X from gate and spend). klee-mod/DECISIONS.md:554-557 carries the same stale prose but is immediately corrected by its CLOSED blockquote at :559-566; SparkPower.cs has no such correction, so a reader of the class alone is told a divergence exists that does not.

### klee-mod/KleeCode/Powers/SpotlightSystem.cs — 5 finding(s)
*legs read: klee-mod/KleeCode/Powers/SpotlightSystem.cs:1-609 (full class: SpotlightSystem, CenterStagePower, GuestCastPower, SpotlightPower base, SpotlightDiscountPower, SpotlightDrawPower, SpotlightMultBonusPower, SpotlightMultBonusTurnPower, SpotlightFlatDamagePower, SpotlightFlatDamageTurnPower, OvationSpendBoostPower, SpotlightEncoreFirstPower); klee-mod/KleeCode/Powers/FurinaResources.cs:590-625 (SpendEncore -> OnEncoreSpent), 740-800 (FurinaResourceHooks.BeforeCardPlayed -> NotePlay; AfterCardPlayed -> ResolvePendingDraw), 860-920 (BeforeSideTurnStart / AfterPlayerTurnStart -> SpotlightSystem.ResetTurn); klee-mod/KleeCode/Powers/SalonPowers.cs:400-455 (SalonMemberPower.AfterPlayerTurnStart spends Encore); klee-mod/KleeCode/Powers/CurtainCallPowers.cs:55-100 (CurtainCallHooks.ResetTurn broadcast-site rationale); klee-mod/KleeCode/Powers/KleePowerIcons.cs:60-140 (Spotlight icon family + NoIconRationale); klee-mod/KleeCode/Relics/UpgradedStarterRelics.cs:330-400 (CurtainNeverFalls)*
1. **[HIGH · sim_vs_csharp_divergence]** The Standing Ovation spend-boost window is cleared in the SAME broadcast that feeds it. C# holds the boost in SpotlightSpendBoostResource and zeroes it from SpotlightSystem.ResetTurn, which runs in FurinaResourceHooks.AfterPlayerTurnStart -- the same broadcast in which SalonMemberPower.AfterPlayerTurnStart spends Encore for Salon upkeep. tier0 instead resets its turn windows at the top of the turn and lets the boost expire at turn END, so every Salon-upkeep spend reliably grants the boost for the whole turn.
   - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:300-307 (ResetTurn: `if (spendBoost != null) spendBoost.Amount = 0;`)`
   - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:387-392 (OnEncoreSpent feeds SpotlightSpendBoostResource)`
   - `klee-mod/KleeCode/Powers/FurinaResources.cs:906-911 (`public override async Task AfterPlayerTurnStart(...)` -> `SpotlightSystem.ResetTurn(player.Creature);`)`
   - `klee-mod/KleeCode/Powers/SalonPowers.cs:413-428 (`public override async Task AfterPlayerTurnStart(...)` -> `FurinaResources.SpendEncore(Owner, SalonConstants.TickEncoreCost)`)`
   - `klee-mod/KleeCode/Powers/FurinaResources.cs:611 (SpendEncore -> SpotlightSystem.OnEncoreSpent)`
   - `klee-mod/KleeCode/Powers/CurtainCallPowers.cs:60-68 (the same hazard, named: "Salon upkeep is itself an AfterPlayerTurnStart hook that SPENDS Encore. Resetting in the same broadcast as the thing that feeds the latch would make the Gallery Stirs draw depend on undefined intra-broadcast power ordering.")`
   - note: Two separable defects. (a) CERTAIN: the clear sites differ -- C# clears at the player's turn START, tier0 at the player's turn END, so the C# window additionally survives the whole enemy turn. (b) ORDERING-DEPENDENT and the player-visible half: if SalonMemberPower's AfterPlayerTurnStart runs before FurinaResourceHooks', every Salon-upkeep Encore spend's Ovation boost is wiped before a single card can read it, so Standing Ovation pays nothing for upkeep spends while tier0 always pays. Intra-broadcast power ordering is documented as undefined in this codebase (CurtainCallPowers.cs:66-67), and CurtainCallHooks.ResetTurn was deliberately moved to BeforeSideTurnStart to escape exactly this; SpotlightSystem.ResetTurn was not. SalonPowers.cs:427 is the only Encore spend in the codebase outside card resolution.
2. **[MEDIUM · semantic_drift]** Supporting Cast's first-Spotlighted-play draw lands at a different point in the card play in the two engines: C# defers it to AfterCardPlayed (after the played card has fully resolved), tier0 draws it inside play_card before the card resolves. Every other NotePlay payout (Fanfare, spotlight_encore_first Encore, the play counters, the discount window) is immediate on both sides -- only the draw is asymmetric.
   - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:363-368 (NotePlay only RECORDS `PendingDraws[cardPlay] = new PendingDraw(draw, CombatOf(cardPlay))`)`
   - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:371-385 (ResolvePendingDraw performs the CardPileCmd.Draw)`
   - `klee-mod/KleeCode/Powers/FurinaResources.cs:762,787 (NotePlay is called from BeforeCardPlayed)`
   - `klee-mod/KleeCode/Powers/FurinaResources.cs:791-794 (`public override async Task AfterCardPlayed(...)` -> `await SpotlightSystem.ResolvePendingDraw(choiceContext, cardPlay);`)`
   - `tier0/engine/combat.py:236-240 (`if state.spotlighted_cards_this_turn == 1: n = p.powers.get("spotlight_draw", 0); if n: state.draw(n)`)`
   - `tier0/engine/combat.py:252 (`_finish_play(state, card)` -- called AFTER the draw above)`
   - note: Reachable divergence: with Supporting Cast installed, if Encore Performance (docs/furina-cards.yaml:669-670, `copy_spotlighted_in_hand`) is the turn's first Spotlighted play, tier0 draws first so the newly drawn card is a legal copy target, while C# copies before the draw arrives. It also flips draw ORDER for any Spotlighted card that draws (Director's Cut, Curtain Cue), which matters at the hand cap. The deferral is mechanically forced on the C# side -- BeforeCardPlayed carries no PlayerChoiceContext -- but the resulting timing gap versus the sim is nowhere acknowledged in the file.
3. **[LOW · other]** The SpotlightPower base-class doc comment is stale on both of its stated justifications: it claims KleePowerIcons keys the Spotlight icon off the base type and that "every Spotlight power lives here", but KleePowerIcons deliberately has NO base-class case and names all ten powers individually, and two of the Spotlight powers in this very file do not derive from SpotlightPower at all.
   - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:436-439 ("That emptied CappedSpotlightPower, so it is gone and every Spotlight power lives here. KleePowerIcons keys its Spotlight icon off this base type, so keeping the common base ... keeps the icon match a single case.")`
   - `klee-mod/KleeCode/Powers/KleePowerIcons.cs:112-117 ("NO SpotlightPower base case, deliberately. A future subclass added without an icon should fall to `_ => null` ...")`
   - `klee-mod/KleeCode/Powers/KleePowerIcons.cs:80-89 (all ten Spotlight powers matched individually)`
   - `klee-mod/KleeCode/Powers/KleePowerIcons.cs:74-79 ("the six that derive from SpotlightPower MUST precede any base-class pattern" -- six, not ten)`
   - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:532-533 (`public sealed class SpotlightMultBonusTurnPower : PowerModel, ILocalizationProvider`)`
   - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:565-566 (`public sealed class SpotlightFlatDamageTurnPower : PowerModel, ILocalizationProvider`)`
   - note: Comment drift only -- no behavioural consequence. KleePowerIcons.cs:138 already registers SpotlightPower in NoIconRationale as "abstract base; every concrete subclass is named", which is the correct statement of the situation.
4. **[LOW · sim_vs_csharp_divergence]** The Guest Cast multiplier is computed in decimal in C# (Math.Truncate over decimal) and in binary float in tier0 (int() over float), so the two engines truncate to different integers at some reachable bonus/printed-value pairs.
   - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:60 (`public const decimal GuestCastBaseMultiplier = 1.5m;`)`
   - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:241-245 (`return GuestCastBaseMultiplier + percentagePoints / 100m;`)`
   - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:250 (`var scaled = Math.Truncate(amount * OutwardMultiplier(card));`)`
   - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:298 (`Math.Truncate(amount * OutwardMultiplier(card))`)`
   - `tier0/engine/effects.py:338-344 (`base = C.SPOTLIGHT_BASE_MULT` ... `return base + bonus / 100.0`)`
   - `tier0/engine/effects.py:346-348 (`return int(amount * m) if m != 1.0 else amount`)`
   - note: Verified by exhaustive comparison of int(a*(1.5+n/100.0)) against decimal ROUND_DOWN over n in 0..300 step 5 and a in 1..60: the pairs that disagree are (bonus 55, printed 60) 122 vs 123, (80, 50) 114 vs 115, (130, 45) 125 vs 126, (260, 30/50/60) each 1 low in tier0. Needs both a large accumulated percentage bonus and a large printed number, so it is unlikely to bite at shipped card values -- but docs/furina-fanfare-parity-vectors.json shows numeric parity is actively pinned, and a float-vs-decimal base is the kind of thing that pins wrong.
5. **[LOW · missing_leg]** SpotlightSystem.BothModes / MovedThisTurn's always-on branch (the CurtainNeverFalls upgraded starter) has no sim counterpart at all: tier0's spotlight is a single Optional[str] target that cannot represent both modes being live, and tier05 has no relic row for it, so the relic's effect on Spotlight is unmeasured on the sim side.
   - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:133-135 (`BothModes` = holds Relics.CurtainNeverFalls)`
   - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:139-145 (CenterStageActive / GuestCastActive both true under BothModes)`
   - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:157-159 (`MovedThisTurn` returns true unconditionally under BothModes)`
   - `klee-mod/KleeCode/Relics/UpgradedStarterRelics.cs:341-348 ("SIM PARITY: NOT MODELLED ... tier05 has no Spotlight-mode model to make always-on ... That is a real gap")`
   - `tier0/engine/state.py:390 (`spotlight: Optional[str] = None   # THE per-player registry: one`)`
   - `tier0/engine/effects.py:307-318 (is_spotlighted/is_outward_spotlighted branch on the single target; the two modes are mutually exclusive by construction)`
   - note: Recorded, not silent -- both sides name the gap in prose and assign it to the pool-sweep pass, which is why this is low rather than higher. Listed for coverage: the C# behaviour (both halves live, selector-payoff predicates permanently true for curtain_cue/directors_cut) is genuinely unpriced by any sim run.

## relics

### amethyst_aubergine — 1 finding(s)
*legs read: /home/user/GItS/tier05/content/relics.yaml:81-91; /home/user/GItS/tier0/engine/relics.py:42-75 (RUN_HOOKS: gold_per_fight ignored by the combat engine, no alarm); /home/user/GItS/tier05/relics.py:160-186, 293-345, 440-455; /home/user/GItS/tier05/model.py:613-641; /home/user/GItS/tier05/tests/test_relics_runlayer.py:118-128; /home/user/GItS/review/potion-relic-gallery/gallery.md:669-682*
1. **[LOW · other]** The frozen base-mechanics record for amethyst_aubergine names a class that does not exist: it says the run layer applies gold_per_fight in `RunRelics.post_fight`, but the dataclass in tier05/relics.py is `HeldRelics` (the same gallery elsewhere invents a third name, `RelicSet`, for the same class). Line number and behaviour cited are correct; only the type name is drift.
   - `/home/user/GItS/review/potion-relic-gallery/gallery.md:670 ("The run layer applies it in RunRelics.post_fight (tier05/relics.py:446)")`
   - `/home/user/GItS/tier05/relics.py:294 (`class HeldRelics:`)`
   - `/home/user/GItS/tier05/relics.py:440-447 (`def post_fight(...)` → `for fx in self._run("gold_per_fight"): gold += int(fx["amount"])`)`
   - `/home/user/GItS/review/potion-relic-gallery/gallery.md:733 (same class called "RelicSet.combat_effects_for")`
   - note: Cosmetic only — the hook, the amount (15), the won-fight gate and the all-node-kinds scope all match: model.py:613 `if fight_won:` → model.py:623-625 `held.post_fight(kind, ...)`, and gold_per_fight is engine-ignored (tier0/engine/relics.py:54). Neow weight 3 at tier05/relics.py:182 matches the gallery.

### anchor — 1 finding(s)
*legs read: /home/user/GItS/tier05/content/relics.yaml:12-15; /home/user/GItS/tier0/engine/relics.py:92-114, 159-162; /home/user/GItS/tier0/engine/combat.py:474-482, 812-816; /home/user/GItS/tier05/relics.py:41-51, 160-186, 344-364; /home/user/GItS/tier0/tests/test_relics_combat_start.py:21-44; /home/user/GItS/tier0/harness/metrics.py:114-140, 211*
1. **[LOW · other]** Anchor's 10 Block is invisible to the harness's block tally: the combat_start_block branch adds to p.block directly and emits `relic_block`, while metrics.extract only accumulates `block` events into FightStats.total_block_gained (the "block" column the runner reports). Every other block source in the engine emits `block`.
   - `/home/user/GItS/tier0/engine/relics.py:110-114 (`p.block += amt` then `state.emit("relic_block", amount=amt)`)`
   - `/home/user/GItS/tier0/harness/metrics.py:136-137 (`elif e == "block": block += ev["amount"]`)`
   - `/home/user/GItS/tier0/harness/metrics.py:211 (`total_block_gained=block`)`
   - `/home/user/GItS/tier0/engine/effects.py:637 (card block emits `state.emit("block", amount=amount)`)`
   - `/home/user/GItS/tier0/harness/runner.py:224 (`"block": s.total_block_gained`)`
   - note: Report-only. The A3 axis reads `damage_blocked` (tier0/harness/axes.py:117), which is unaffected because the Block itself is real and absorbs damage, and tier05 run stats never read block at all. Timing/amount parity is otherwise exact: apply_combat_start fires once, on turn 1, after the block clear (combat.py:479-481), so the 10 survives into turn 1 and decays at turn 2 — matching relics.yaml:15 and the gallery text.

### astrolabe — 1 finding(s)
*legs read: /home/user/GItS/tier05/content/relics.yaml:139-176; /home/user/GItS/tier05/relics.py:41-51, 101-119, 129-148, 160-196, 230-244, 319-334, 368-401; /home/user/GItS/tier0/engine/relics.py:42-75 (grant_random_common deliberately absent from both engine sets; never reaches combat); /home/user/GItS/tier05/model.py:255-324, 379-390, 626-633, 739-744; /home/user/GItS/tools/realistic_axis_scores.py:127, /home/user/GItS/tools/encounter_audit.py:91 (all combat builds go through combat_effects_for — no hook leak); /home/user/GItS/review/potion-relic-gallery/gallery.md:981-982*
1. **[MEDIUM · semantic_drift]** run_one documents a hard invariant that seeded (relics=[...]) runs with grant_relics=False never accrue relics because "the granting sites are ALL gated on grant_relics, never on `held`" — but astrolabe's grant_random_common resolves inside apply_pickups, which runs unconditionally on the seeded set before the grant_relics branch, so seeding astrolabe grants an extra Common relic (and cascades its pickup payouts) on a grant_relics=False run.
   - `/home/user/GItS/tier05/model.py:266-268 ("Seeded (relics=[...]) runs with grant_relics=False keep the W1 behaviour unchanged: the granting sites are ALL gated on grant_relics, never on `held`.")`
   - `/home/user/GItS/tier05/model.py:316-317 ("All accrual is gated on grant_relics, so a seeded run with grant_relics=False never grants -- the W1 world is intact.")`
   - `/home/user/GItS/tier05/model.py:310-312 (`if relics: held = HeldRelics.hold(...); held.apply_pickups(...)` — outside the `if grant_relics:` block at 313)`
   - `/home/user/GItS/tier05/relics.py:394-400 (`elif hook == "grant_random_common": rid = roll_relic_reward(rng, self, self.character); ... self.add(rid, ...)`)`
   - `/home/user/GItS/tier05/relics.py:101-111 (`get_relic` resolves neow ids, so "astrolabe" is a legal seed)`
   - `/home/user/GItS/tier05/content/relics.yaml:173-176`
   - note: Narrow: reachable only by explicitly seeding a Neow-pool relic. On the normal grant_relics=True path the behaviour matches the spec exactly — one roll from unowned_common, owner-gated, no duplicates, no-op on an exhausted pool, cascading pickup effects via add(). The hook is correctly kept out of tier0's vocabularies (tier05/relics.py:44-51) so it never trips the engine's UNIMPLEMENTED alarm, and every combat build routes through combat_effects_for.

### bag_of_marbles — CLEAN
*legs read: /home/user/GItS/tier05/content/relics.yaml:37-40; /home/user/GItS/tier0/engine/relics.py:43-49, 129-132; /home/user/GItS/tier0/engine/powers.py:19-23, 57-61, 139-151, 153-179; /home/user/GItS/tier0/engine/state.py:635-637 (living_enemies); /home/user/GItS/tier0/engine/combat.py:474-482; /home/user/GItS/tier0/tests/test_relics_combat_start.py:128-135*

### bag_of_preparation — CLEAN
*legs read: /home/user/GItS/tier05/content/relics.yaml:32-35; /home/user/GItS/tier0/engine/relics.py:43-49, 124-128, 178-201; /home/user/GItS/tier0/engine/combat.py:462-482; /home/user/GItS/tier0/engine/state.py:649-679 (draw / from_hand_draw); /home/user/GItS/tier0/tests/test_relics_combat_start.py:107-125; /home/user/GItS/tier05/relics.py:160-186, 344-364*

### blood_vial — CLEAN
*legs read: /home/user/GItS/tier05/content/relics.yaml:22-25; /home/user/GItS/tier0/engine/relics.py:43-49, 118-119, 164-171; /home/user/GItS/tier0/engine/combat.py:474-482; /home/user/GItS/tier0/tests/test_relics_combat_start.py:61-81; /home/user/GItS/tier0/harness/metrics.py:153-154 (heal event is counted; source="relic"); /home/user/GItS/tier05/model.py:552-553, 599 (run hp is seeded into and read back out of the fight, so the 2 HP carries)*

### book_of_five_rings — 1 finding(s)
*legs read: /home/user/GItS/tier05/content/relics.yaml:118-121; /home/user/GItS/tier0/engine/relics.py:52-57 (RUN_HOOKS: engine-inert, no alarm); /home/user/GItS/tier05/relics.py:293-303, 336-342, 418-436; /home/user/GItS/tier05/model.py:408-415, 488-512, 714-717; /home/user/GItS/tier05/events.py:387-420, 444-468, 503-519; /home/user/GItS/tier05/content/events.yaml:16-28, 94-255*
1. **[MEDIUM · sheet_vs_sim_divergence]** The hook is specced as "every 5 cards ADDED to the deck, heal 20", but the counter is only ticked at two of the run's card-add sites (reward-screen picks and shop card purchases). Every card an EVENT adds — named add_card, curses, random_card, pick_cards, card_reward/card_screens, transform replacements, and duplicate_deck — appends to the deck without calling note_cards_added, so those adds never advance cards_added_total and the 20 HP heal is under-paid on any run that meets a card-adding event.
   - `/home/user/GItS/tier05/content/relics.yaml:118-121 (`{hook: book_of_five_rings, per: 5, heal: 20}`)`
   - `/home/user/GItS/docs/archive/relic-potion-layer-plan.md:163 ("Book of Five Rings | every 5 cards added, heal 20 | run-layer counter")`
   - `/home/user/GItS/tier05/relics.py:420-436 (`note_cards_added` is the ONLY writer of `cards_added_total`)`
   - `/home/user/GItS/tier05/model.py:412 (shop purchases: `hp = held.note_cards_added(added, hp, max_hp)`)`
   - `/home/user/GItS/tier05/model.py:717 (reward pick: `hp = held.note_cards_added(1, hp, max_hp)`)`
   - `/home/user/GItS/tier05/events.py:408 (`st.deck_ids.append(opt["curse"])` — no note_cards_added)`
   - note: The event layer (§11) post-dates the relic layer, and the frozen base-mechanics record already enumerates only the two counted sites (review/potion-relic-gallery/gallery.md:801), so the gap looks like drift rather than a deliberate rule — the yaml/plan wording is unconditional "cards added". Everything else is exact: chunk accounting never double-pays (_book_chunks_healed), the heal is clamped to max_hp, a batch add pays every threshold it crosses, the counter never resets across the run, and the engine correctly ignores the hook (tier0/engine/relics.py:55).

### booming_conch — CLEAN
*legs read: /home/user/GItS/tier05/content/relics.yaml:139-158 (neow pool, booming_conch spec); /home/user/GItS/tier0/engine/relics.py:43-57 (COMBAT_HOOKS / RUN_HOOKS; elite_combat_start is a recognised run hook); /home/user/GItS/tier0/engine/relics.py:92-163 (apply_combat_start: combat_start_draw/energy, TURN 1 only); /home/user/GItS/tier05/relics.py:344-364 (combat_effects_for: E-node injection of draw 2 / energy 1); /home/user/GItS/tier05/relics.py:160-194 (_NEOW_HOOK_WEIGHT elite_combat_start=9); /home/user/GItS/tier05/model.py:528-551 (relic_fx = held.combat_effects_for(kind, just_rested))*

### bronze_scales — CLEAN
*legs read: /home/user/GItS/tier05/content/relics.yaml:280-295 (skip: block, bronze_scales, name + missing only, no effects list); /home/user/GItS/tier05/relics.py:58-112 (_pool warns per skip id; common/neow/ancient/event pools exclude skip; get_relic raises KeyError for a skip id); /home/user/GItS/tier05/relics.py:129-148 (roll_relic_reward draws from common_pool only); /home/user/GItS/tier05/events.py:471-487 (event relic grants: rolled from common pool, or a named relic_id); /home/user/GItS/tier05/content/events.yaml:31,185 (only named event relic is pollinous_core); /home/user/GItS/tier05/shop.py:284-289 (relic slot is a documented no-op stub)*

### centennial_puzzle — 1 finding(s)
*legs read: /home/user/GItS/tier05/content/relics.yaml:69-72; /home/user/GItS/tier0/engine/relics.py:26-31,43-49,81-90,239-251; /home/user/GItS/tier0/engine/combat.py:544-553,664-674,812-816; /home/user/GItS/tier0/engine/effects.py:495-506; /home/user/GItS/tier0/engine/statuses.py:14-51; /home/user/GItS/tier0/engine/state.py:333,680-686*
1. **[MEDIUM · semantic_drift]** The relic is specified and documented as firing on the FIRST HP loss of a combat, but relics.note_hp_loss() is wired to exactly one call site — the enemy powered-attack loop. Every other player HP-loss path in tier0 (enemy-injected Burn/Wither end-of-turn ticks, self-damage card ops, power ticks, status-on-draw damage) reduces HP without ever offering the relic a chance to fire, so the trigger scope is narrower than both the yaml hook name and the engine's own first docstring line.
   - `/home/user/GItS/tier05/content/relics.yaml:72 — `- {hook: on_first_hp_loss_draw, amount: 3}``
   - `/home/user/GItS/tier0/engine/relics.py:240 — docstring: "on_first_hp_loss_draw: the FIRST time the player loses HP this combat, draw."`
   - `/home/user/GItS/tier0/engine/combat.py:671-672 — the ONLY call: `if hp_loss > 0 and state.player.relic_effects: relics.note_hp_loss(state)`, inside the enemy-attack loop`
   - `/home/user/GItS/tier0/engine/combat.py:550-551 — injected Burn/Wither end-of-turn damage: `p.hp -= dmg - blocked; resources.note_player_hp_loss(...)` with no relics.note_hp_loss call`
   - `/home/user/GItS/tier0/engine/effects.py:503-505 — `{op: damage, target: self}`: `state.player.hp -= fx["amount"]` with no relics.note_hp_loss call`
   - `/home/user/GItS/tier0/engine/state.py:684-685 — status_draw_damage HP loss, same omission`
   - note: Half-disclosed: the engine docstring's closing line (relics.py:241) does say "Called from the enemy-damage site", and the gallery record (review/potion-relic-gallery/gallery.md:593) describes the narrow behaviour accurately. The spec yaml's hook name and the docstring's leading sentence are what over-promise. Medium, not high: requires burn/wither injection or a self-damage card to be the first HP loss of a combat.

### diamond_diadem — 1 finding(s)
*legs read: /home/user/GItS/tier05/content/relics.yaml:178-186,254-259; /home/user/GItS/tier0/engine/relics.py:43-49,92-114; /home/user/GItS/tier05/relics.py:58-68,85-88,197-227 (ancient pool, offer/pick, combat_start_block weight 6 at line 177); /home/user/GItS/tier0/engine/combat.py:474-482 (block applied AFTER the turn-start block clear, so it covers exactly one enemy turn); /home/user/GItS/docs/act2-act3-roster-research.md:205-218; /home/user/GItS/docs/run-model-rework-plan.md:358,739-786*
1. **[LOW · other]** The yaml ships a knowingly approximated relic (the real Diadem's block survives into the next turn; here it is plain start-of-combat block that the next turn's clear wipes) and cites §10.9 as the tracking home — but §10.9's living skip backlog contains no Diamond Diadem / block-retention row, and unlike the `skip:` block this approximation produces no runtime UNIMPLEMENTED warning.
   - `/home/user/GItS/tier05/content/relics.yaml:255-259 — "# UNIMPLEMENTED (§10.9): the real Diadem's block survives into the next turn; modeled as plain start-of-combat block." followed by `- {hook: combat_start_block, amount: 20}``
   - `/home/user/GItS/docs/run-model-rework-plan.md:739-786 — the §10.9 skip backlog list: Ancient-boon riders tracked there are Blessed Antler and Philosopher's Stone only; no diadem/block-retention entry exists`
   - `/home/user/GItS/tier05/relics.py:63-68 — `_pool()` emits its loud warning only for ids under `skip:`, so an approximated ancient-pool relic loads silently`
   - `/home/user/GItS/tier0/engine/relics.py:110-114 — combat_start_block is a plain `p.block += amt`, and combat.py:474-482 applies it after the turn-start block clear, so the 20 covers one enemy turn only`
   - note: The deviation itself is honestly disclosed inline in the yaml and in docs/act2-act3-roster-research.md:212 ("20 start-block; 1-turn retention skipped"), which is why this is low rather than medium. The number (20) and the pool (ancient/Nonupeipe) match the research harvest exactly; the sim/spec legs agree with each other.

### festive_popper — 1 finding(s)
*legs read: /home/user/GItS/tier05/content/relics.yaml:47-50; /home/user/GItS/tier0/engine/relics.py:24,43-49,92-137; /home/user/GItS/tier0/engine/refpowers.py:97-124 (unpowered_damage: block applies, no Strength/Vulnerable, kill counter); /home/user/GItS/tier0/engine/combat.py:63-93 (_settle_phases contract), 444-493 (turn-1 ordering); /home/user/GItS/tier05/content/act3_pool.yaml:232-250 (the only phased enemy: test_subject, phase-1 hp 100); /home/user/GItS/tier0/tests/test_relics_combat_start.py:161-179*
1. **[LOW · other]** _settle_phases' contract states it is called at every site that can drop enemy HP, but the combat-start relic AoE site (the only thing combat_start_aoe does) is not covered — the potion block immediately below it is, for exactly the reason that applies here too.
   - `/home/user/GItS/tier0/engine/combat.py:67-70 — _settle_phases docstring: "Called at every site that can drop enemy HP -- after each card play, the bomb-detonation sweep, turn-start potion use, the player-turn-end triggers, and each enemy turn ... always BEFORE the loop re-reads state.over"`
   - `/home/user/GItS/tier0/engine/combat.py:479-482 — `if p.relic_effects: if state.turn == 1: relics.apply_combat_start(state)` with no _settle_phases call after it`
   - `/home/user/GItS/tier0/engine/combat.py:487-489 — the potion block directly below does call `_settle_phases(state)  # an offensive potion can drop a phased boss``
   - `/home/user/GItS/tier0/engine/relics.py:133-136 — combat_start_aoe: `for enemy in list(state.living_enemies): refpowers.unpowered_damage(state, enemy, amt)` — a genuine enemy-HP-dropping site`
   - `/home/user/GItS/tier05/content/act3_pool.yaml:233-241 — the only phased enemy in the shipped content is test_subject at 100 phase-1 HP`
   - note: Everything else on this relic checks out across all legs: amount 9 matches docs/archive/relic-potion-layer-plan.md:150, the Unpowered path (no Strength, no Vulnerable, Block still applies, no Bomb detonation/Shatter) matches the gallery's frozen description and tier0/tests/test_relics_combat_start.py:163-179, and there is no run-layer component. No C# leg is expected.

### fishing_rod — CLEAN
*legs read: /home/user/GItS/tier05/content/relics.yaml:148-152; /home/user/GItS/tier0/engine/relics.py:53-57 (fishing_rod in RUN_HOOKS: recognised and silently ignored in combat, no UNIMPLEMENTED alarm); /home/user/GItS/tier05/relics.py:50-51,293-303,438-463 (post_fight: N-only counter, every `per`-th win, _fishing_upgrade); /home/user/GItS/tier05/relics.py:179 (_NEOW_HOOK_WEIGHT fishing_rod=4); /home/user/GItS/tier0/content/upgrades.py:89-96 (has_upgrade excludes already-suffixed ids, so the every-3rd upgrade cannot double-suffix a card); /home/user/GItS/tier05/model.py:613-625 (post_fight called only on a WON fight, with the run's single rng)*

### golden_pearl — 1 finding(s)
*legs read: /home/user/GItS/tier05/content/relics.yaml:154-157,168-171; /home/user/GItS/tier0/engine/relics.py:53-57 (gold_on_pickup in RUN_HOOKS: zero combat behaviour); /home/user/GItS/tier05/relics.py:185 (weight 2), 239-244 (neow_pick tie-break), 293-334 (HeldRelics, add() idempotent per id), 366-401 (_apply_pickup_fx: gold += amount); /home/user/GItS/tier05/model.py:305-325 (run-start apply_pickups / Neow add); /home/user/GItS/tier05/tests/test_relics_runlayer.py:109-115 (+150 gold delta); /home/user/GItS/tier05/tests/test_neow_and_shop.py:134-139 (tie vs hand_of_greed breaks to golden_pearl)*
1. **[LOW · other]** The gallery's frozen-mechanics record for golden_pearl names a class that does not exist in the repo — it calls the pickup path RelicSet._apply_pickup_fx / RelicSet.add(), while the actual dataclass is HeldRelics; the cited line range for _apply_pickup_fx also stops short of the function's real end.
   - `/home/user/GItS/review/potion-relic-gallery/gallery.md:925 — "It fires exactly once, at acquisition, in RelicSet._apply_pickup_fx (tier05/relics.py:377-389) ... or mid-run via RelicSet.add()"`
   - `/home/user/GItS/tier05/relics.py:293-294 — `@dataclass` / `class HeldRelics:` (grep for `RelicSet` across all .py in the repo returns zero hits)`
   - `/home/user/GItS/tier05/relics.py:377-401 — `_apply_pickup_fx` actually spans to line 401, not 389`
   - note: Purely cosmetic/doc drift. The three real legs agree: yaml amount 150 (relics.yaml:157) matches the wiki harvest (docs/archive/relic-potion-layer-plan.md:186), the sim grants it once and only once (add() early-returns on a held id, relics.py:327-328), the test asserts the +150 delta, and no C# leg is expected for a base-pool relic.

### gorget — CLEAN
*legs read: tier05/content/relics.yaml:52-57; tier0/engine/relics.py:43-49,92-161 (combat_start_power at 115-117); tier0/engine/refpowers.py:1185-1189,1232-1248; tier0/engine/combat.py:458-482,535-538; tier0/tests/test_relics_combat_start.py:182-193; tier0/tests/test_refpowers.py:670-690*

### hand_of_greed — 1 finding(s)
*legs read: tier05/content/relics.yaml:154-157,168-171; tier05/relics.py:101-111,160-194,230-244,377-401; tier0/engine/relics.py:53-57; tier05/model.py:310-323; tier05/tests/test_neow_and_shop.py:125-141,196-215*
1. **[MEDIUM · semantic_drift]** hand_of_greed is defined as the strictly larger sibling of golden_pearl (250 vs 150 gold), but the Neow valuation is amount-blind and its tie-break deterministically prefers golden_pearl — with the shipped 6-boon pool and k=3 offers, hand_of_greed can NEVER be the pilot's pick, so the 250-gold boon is unreachable content in any grant_relics run.
   - `tier05/content/relics.yaml:168-171 — hand_of_greed: {hook: gold_on_pickup, amount: 250}, commented "bigger gold boon (> golden_pearl's 150)"`
   - `tier05/content/relics.yaml:154-157 — golden_pearl: {hook: gold_on_pickup, amount: 150}`
   - `tier05/relics.py:185 — "gold_on_pickup": 2 (one weight for the hook; the amount is never read)`
   - `tier05/relics.py:244 — return max(sorted(offer), key=lambda rid: _neow_value(rid, character)) — max() keeps the FIRST maximum, and sorted() puts golden_pearl before hand_of_greed`
   - `tier05/relics.py:230-236 — neow_offer samples k=3 distinct ids from the 6-entry neow pool`
   - `tier05/tests/test_neow_and_shop.py:138-139 — the tie is pinned as golden_pearl`
   - note: Verified empirically over all 20 three-of-six offers: the only ids neow_pick ever returns are astrolabe, booming_conch, fishing_rod, ossified_relic; hand_of_greed and golden_pearl win zero combinations (hand_of_greed's value 2 is the pool minimum, and the only other value-2 boon sorts ahead of it). hand_of_greed is still reachable by explicit seeding (relics=[...] via HeldRelics.hold/apply_pickups, which tests use), so the gold_on_pickup implementation itself (tier05/relics.py:389-390, gold += 250, idempotent per id) is correct — the divergence is spec intent vs. the interpreter's pick. Mitigating context: tier05/relics.py:158-160 documents the table as a deliberately STATIC per-hook valuation (spec §3), so amount-blindness is by design; what the design does not appear to intend is a pool entry that is structurally unobtainable.

### happy_flower — CLEAN
*legs read: tier05/content/relics.yaml:59-62; tier0/engine/relics.py:26,43-49,178-201; tier0/engine/combat.py:458-482; tier0/tests/test_relics_dynamic.py:48-66; tier05/relics.py:41,264-284; docs/archive/relic-potion-layer-plan.md:152*

### juzu_bracelet — CLEAN
*legs read: tier05/content/relics.yaml:280-318 (skip block; juzu_bracelet 310-318); tier05/relics.py:58-111 (_pool warn 63-67, pool accessors 71-98, get_relic 101-111); tier05/relics.py:129-134,204-208,230-236,251-261; tier05/content/events.yaml:31,185 (only relic_id in event content is pollinous_core); tier05/model.py:310-323,379-391,416-438,733-744; review/potion-relic-gallery/gallery.md:1284-1290*

### lantern — CLEAN
*legs read: tier05/content/relics.yaml:27-30; tier0/engine/relics.py:22,43-49,92-128 (combat_start_energy 120-123); tier0/engine/combat.py:458-464,474-482; tier0/tests/test_relics_combat_start.py:84-104; tier05/relics.py:41,264-284,344-364; docs/archive/relic-potion-layer-plan.md:145*

### looming_fruit — 1 finding(s)
*legs read: tier05/content/relics.yaml:178-186,244-247; tier05/relics.py:85-88,101-111,160-194,204-227,319-334,377-401; tier0/engine/relics.py:53-57; tier05/model.py:310-312,733-744; tier05/tests/test_multiact.py:150; review/potion-relic-gallery/gallery.md:1148-1149*
1. **[LOW · semantic_drift]** The Ancient pool's per-entry act attribution is inert: looming_fruit is labelled an Act-3 (Nonupeipe) boon, but unowned_ancient/ancient_offer take no act argument and model.py offers the whole flat pool after EVERY non-final act boss, so a +31 max-HP Act-3 boon is offerable at the Act-1→Act-2 boundary.
   - `tier05/content/relics.yaml:245 — name: "Looming Fruit"  # Nonupeipe (Act 3): +31 max HP`
   - `tier05/content/relics.yaml:193,216,221,226 — sibling entries labelled "(Act 2)" in the same flat pool`
   - `tier05/relics.py:204-208 — unowned_ancient(held_ids, character) filters on held + owner only; no act parameter`
   - `tier05/relics.py:211-219 — ancient_offer(rng, held, character, k=3) samples from that unfiltered list`
   - `tier05/model.py:733-744 — `if kind == "B" and not final_act:` calls ancient_offer/ancient_pick at every non-final act boundary with no act discriminator`
   - note: Filed low, not medium, because the section header at tier05/content/relics.yaml:178-186 explicitly ratifies a single flat pool offered "after each NON-FINAL act boss" — so the per-entry "(Act 2)"/"(Act 3)" strings read as source provenance rather than a gate the interpreter fails to honour. Flagging it because the labels are the only place the two real-game Ancients are distinguished, and a reader can take them for a constraint. The effect itself is correct on every leg: on_pickup_maxhp 31 is run-scoped (tier0/engine/relics.py:53-57 ignores it without alarm) and tier05/relics.py:385-388 does max_hp += 31; hp += 31, applied after model.py:738's `hp = max_hp` so the holder ends at full HP. Reachability checked empirically: looming_fruit wins 6 of the 84 three-of-nine Ancient offers, so it is not dead content.

### meal_ticket — CLEAN
*legs read: tier05/content/relics.yaml:92-95; tier0/engine/relics.py:53-57 (shop_heal in RUN_HOOKS, ignored without alarm); tier05/relics.py:50-51,264-284,338-342,470-471; tier05/model.py:392-415,454; tier05/tests/test_relics_runlayer.py:142-151; docs/archive/relic-potion-layer-plan.md:157*

### oddly_smooth_stone — 1 finding(s)
*legs read: /home/user/GItS/tier05/content/relics.yaml:280-318 (skip block; entry at :296-309, name+missing only, no `effects:` key); /home/user/GItS/tier05/relics.py:58-111 (_pool() warns at :63-67; common/neow/ancient/event accessors exclude `skip`; get_relic raises KeyError at :108-110); /home/user/GItS/tier05/relics.py:251-284 (_relic_effects/split_effects both route through get_relic, so a skip id cannot produce effects); /home/user/GItS/tier0/engine/relics.py:43-57, 92-162 (combat_start_power exists and is honored; dexterity would ride it); /home/user/GItS/tier0/engine/powers.py:75-100 (modify_block_gained: Dexterity additive BEFORE Frail x0.75 — matches the gallery's claim); /home/user/GItS/klee-mod/KleeCode/Relics/ (4 files: EtherealSpotlightRelic, PearlOfWisdom, PoundingSurprise, UpgradedStarterRelics) + grep of all *.cs for 'Oddly Smooth'/'SmoothStone' — zero hits; no C# leg expected for a vanilla StS2 relic the mod does not reimplement*
1. **[LOW · other]** The gallery entry's sole surviving mapping still carries its pre-cut ranking prose: Lumitoile is published as '### 1' (and the checklist says '1 kept'), but its rationale ends 'Ranked third because ... Sango Pearl and Guyun both earn the block metaphor more directly' — and neither Sango Pearl nor Guyun appears anywhere in this entry.
   - `/home/user/GItS/review/potion-relic-gallery/gallery.md:66 — checklist row: `- [ ] `oddly_smooth_stone` — Lumitoile (1 kept)``
   - `/home/user/GItS/review/potion-relic-gallery/gallery.md:1270 — heading `### 1. Lumitoile``
   - `/home/user/GItS/review/potion-relic-gallery/gallery.md:1275 — 'Ranked third because the pressure-of-the-deep framing edges toward composure rather than deflection, and Sango Pearl and Guyun both earn the block metaphor more directly.'`
   - note: Text-layer only; no mechanical claim is wrong. The entry's mechanical description (skip-block, get_relic KeyError, combat_start_power + Dexterity-before-Frail ordering) checks out line-for-line against relics.yaml:296-309, relics.py:63-110 and powers.py:75-100.

### ossified_relic — CLEAN
*legs read: /home/user/GItS/tier05/content/relics.yaml:139-176 (neow pool; ossified_relic at :163-166, {hook: on_pickup_maxhp, amount: 8}, no owner gate); /home/user/GItS/tier05/relics.py:76-78, 160-186, 230-244 (neow_pool, _NEOW_HOOK_WEIGHT on_pickup_maxhp=5, neow_offer/neow_pick); /home/user/GItS/tier05/relics.py:319-334, 368-401 (HeldRelics.add idempotent at :327-328; _apply_pickup_fx :385-388 does max_hp += amt AND hp += amt exactly once); /home/user/GItS/tier0/engine/relics.py:53-57, 63-75 (on_pickup_maxhp is in RUN_HOOKS, so _validate ignores it silently; no combat branch consumes it); /home/user/GItS/tier05/model.py:305-324 (seeded apply_pickups then Neow add; both one-shot); /home/user/GItS/tier05/tests/test_neow_and_shop.py:173-181*

### paels_blood — CLEAN
*legs read: /home/user/GItS/tier05/content/relics.yaml:178-259 (ancient pool; paels_blood at :225-228, {hook: every_n_turns_draw, n: 1, amount: 1}); /home/user/GItS/tier0/engine/relics.py:178-201 (on_player_turn_start: every_n_turns_draw fires when turn % n == 0; n=1 => every player turn, turn 1 included; state.draw(amt) + emit extra_draw); /home/user/GItS/tier0/engine/combat.py:411-482 (state.turn incremented at :413 so the first player turn is turn=1; relics.on_player_turn_start called at :482, AFTER the turn's own energy reset :459 and hand draw :465-466, and after apply_combat_start on turn 1 — so it stacks with the turn-1-only combat_start_draw family rather than replacing it); /home/user/GItS/tier05/relics.py:160-186 (every_n_turns_draw weight 8), :204-227 (unowned_ancient/ancient_offer/ancient_pick); /home/user/GItS/docs/act2-act3-roster-research.md:203-210 ('Pael's Blood (+1 draw/turn)'); /home/user/GItS/review/potion-relic-gallery/gallery.md:1097-1112*

### pendulum — CLEAN
*legs read: /home/user/GItS/tier05/content/relics.yaml:64-67 ({hook: every_n_turns_draw, n: 3, amount: 1}, common pool, no owner gate); /home/user/GItS/tier0/engine/relics.py:43-49 (every_n_turns_draw in COMBAT_HOOKS), :178-201 (fires on turn % 3 == 0 => turns 3/6/9, never turn 1); /home/user/GItS/tier05/relics.py:41, 129-148, 264-284 (COMBAT_HOOKS imported from the engine; split_effects routes it to the combat list; unowned_common makes it rollable loot); /home/user/GItS/tier0/tests/test_relics_dynamic.py:48-82 (test_pendulum_draw_only_on_turn_multiples_of_three pins turns 1,2 = nothing; 3 = +1; 4,5 = nothing; 6 = +1); /home/user/GItS/docs/archive/relic-potion-layer-plan.md:153 ('Pendulum | every 3 turns, draw 1 | every_n_turns_draw ✓'); /home/user/GItS/review/potion-relic-gallery/gallery.md:576-586*

### pollinous_core — CLEAN
*legs read: /home/user/GItS/tier05/content/relics.yaml:261-278 (closed event pool; pollinous_core at :272-278, {hook: every_n_turns_draw, n: 4, amount: 2}, comment pins turns 4/8/12); /home/user/GItS/tier0/engine/relics.py:188-200 (turn % 4 == 0 -> state.draw(2) + emit extra_draw); /home/user/GItS/tier05/relics.py:90-111 (event_pool deliberately unreachable from unowned_common/neow_offer/unowned_ancient; get_relic still resolves it); /home/user/GItS/tier05/content/events.yaml:180-185 (colossal_flower_3 'Enter the Center', hp: -7, relic_id: pollinous_core) and :168-179 (escalation chain); /home/user/GItS/tier05/events.py:482-487 (named relic_id grant via held.add, guarded on `rid not in held.ids`), :288, :516 (escalate resolution); /home/user/GItS/tier05/tests/test_events_acts23.py:63-82 (named-relic-in-event-pool and event-relics-are-never-loot)*

### potion_belt — 2 finding(s)
*legs read: /home/user/GItS/tier05/content/relics.yaml:123-129 ({hook: potion_slots, amount: 2}, common pool); /home/user/GItS/tier05/relics.py:50-51 (potion_slots added to tier05 RUN_HOOKS only), :264-284 (split_effects keeps it out of combat_effects), :473-477 (potion_slot_bonus); /home/user/GItS/tier0/engine/relics.py:43-57 (potion_slots is in NEITHER engine set — correctly never rides in relic_effects, so the UNIMPLEMENTED alarm at :63-75 is never tripped); /home/user/GItS/tier05/model.py:55-62 (_potion_slots), :328-331 (bag construction), :445 (shop refresh), :542 (fight-build refresh), :639 (post-fight-drop refresh), :488-506 (event branch — no refresh); /home/user/GItS/tier05/events.py:188-198 (EventState.potion_slots field), :278-292 (option_value), :488-491 (potion grant); /home/user/GItS/tier05/potions.py:115-137 (PotionBag.slots/full/add + discarded overflow log)*
1. **[MEDIUM · sheet_vs_sim_divergence]** Potion Belt's +2 capacity is not honored on the event-layer potion-grant path: every other consumer of the bag refreshes bag.slots from the held relic set first, but the event branch does not, so an event potion grant is tested against a stale (pre-belt) cap and the potion is discarded.
   - `/home/user/GItS/tier05/model.py:57-58 — _potion_slots docstring: 'Recomputed at each use site so a Potion Belt granted MID-RUN raises the cap immediately.'`
   - `/home/user/GItS/tier05/model.py:445 — shop path refreshes: `bag.slots = _potion_slots(held)``
   - `/home/user/GItS/tier05/model.py:542 — fight-build path refreshes: `bag.slots = _potion_slots(held)``
   - `/home/user/GItS/tier05/model.py:639 — post-fight drop refreshes: `bag.slots = _potion_slots(held)` (but only inside the `rng.random() < C.POTION_DROP_CHANCE` branch)`
   - `/home/user/GItS/tier05/model.py:501-506 — the event branch builds EventState and calls `events.visit(rng, act_i, est, seen_events, held=held, bag=bag, policy=policy)` with NO `bag.slots = _potion_slots(held)` line`
   - `/home/user/GItS/tier05/events.py:488-491 — `if opt.get("potion") and bag is not None: ... if not bag.full(): bag.add(...)` — gates on the stale bag.slots`
   - note: The shop path is safe (refresh at :445 precedes the buy loop) and the fight path is safe (:542). The hole is exactly the Unknown/event node, whose resolver is otherwise handed a full snapshot.
2. **[LOW · missing_leg]** EventState.potion_slots is written but never read — the event layer is handed the belt-adjusted cap and then ignores it, so no event valuation or gating can react to Potion Belt.
   - `/home/user/GItS/tier05/model.py:505 — `potion_slots=bag.slots if bag else 0` (the only writer)`
   - `/home/user/GItS/tier05/events.py:194 — `potion_slots: int = 0` (field declared on EventState; grep of the repo finds no reader of `st.potion_slots` / `.potion_slots` on an EventState)`
   - `/home/user/GItS/tier05/events.py:285 — `v += POTION_HP * opt.get("potion", 0)` — the option valuation credits a potion grant with no capacity check`
   - `/home/user/GItS/tier05/events.py:488-491 — the one site that needs the cap reaches around the snapshot to `bag.full()` instead`
   - note: This dangling field is the direct cause of the medium finding above: the capacity leg exists on the snapshot but nothing consumes it, so the refresh discipline model.py keeps at :445/:542/:639 has no counterpart inside the event resolver.

### prismatic_gem — 1 finding(s)
*legs read: /home/user/GItS/tier05/content/relics.yaml:230-242 (ancient pool; {hook: every_n_turns_energy, n: 1, amount: 1}; the 'card rewards show other colors' rider documented as a faithful no-op); /home/user/GItS/tier0/engine/relics.py:186-193 (every_n_turns_energy: turn % n == 0 -> p.energy += amount, emit relic_energy; n=1 => every player turn incl. turn 1); /home/user/GItS/tier0/engine/combat.py:459 (p.energy = refpowers.energy_for_turn(state)) then :482 (relics.on_player_turn_start) — the +1 lands on top of the turn's refill, so it stacks and does not replace; /home/user/GItS/tier05/relics.py:160-186 (every_n_turns_energy weighted 12, above combat_start_energy's 10 — matches the comment's stated intent), :204-227 (ancient offer/pick); /home/user/GItS/tier0/engine/relics.py:129-132 (combat_start_enemy_power) and /home/user/GItS/tier0/engine/powers.py:43 (enemy strength folds into damage dealt); /home/user/GItS/docs/act2-act3-roster-research.md:214-217; /home/user/GItS/docs/run-model-rework-plan.md:594-600, 769-773*
1. **[LOW · other]** The prismatic_gem block's backlog justification is stale: it says Philosopher's Stone ('enemies +1 Str') 'needs new hooks', but combat_start_enemy_power already exists, is already used by two shipped relics, and enemy Strength is already folded into enemy damage — so that boon maps 1:1 onto an existing hook by the same ratified sampling rule the comment invokes.
   - `/home/user/GItS/tier05/content/relics.yaml:239-240 — 'Antler (3 Dazed at combat start) and Stone (enemies +1 Str) need new hooks: §10.9 backlog, never faked.'`
   - `/home/user/GItS/tier0/engine/relics.py:129-132 — `elif hook == "combat_start_enemy_power": for enemy in state.living_enemies: powers.apply_power(state, enemy, fx["power"], int(fx["amount"]), applier=p)` — any power, all enemies, at combat start`
   - `/home/user/GItS/tier0/engine/relics.py:43-49 — combat_start_enemy_power is in COMBAT_HOOKS`
   - `/home/user/GItS/tier05/content/relics.yaml:37-45 — bag_of_marbles and red_mask already ship on that hook (vulnerable / weak)`
   - `/home/user/GItS/tier0/engine/powers.py:43 — `dmg = base + attacker.powers.get("strength", 0)` in modify_damage_dealt, which /home/user/GItS/tier0/engine/combat.py:642 calls with the enemy as attacker — enemy Strength is live`
   - `/home/user/GItS/docs/run-model-rework-plan.md:771-772 — the same stale claim, 'Philosopher's Stone (all enemies +1 Str at combat start — needs an enemy-side relic hook)'`
   - note: Blessed Antler's half of the same sentence ('3 Dazed at combat start') is genuinely unshippable — no card/status-inject relic hook exists. Only the Philosopher's Stone half is stale. This is exactly the failure mode the same file polices for skip reasons at relics.yaml:287-295 and :298-309 ('a stale skip reason is the quiet lie this list exists to prevent'); the backlog note escaped that discipline. Implementation of prismatic_gem itself is exact against the spec.

### red_mask — CLEAN
*legs read: /home/user/GItS/tier05/content/relics.yaml:42-45; /home/user/GItS/tier0/engine/relics.py:17-49,92-133; /home/user/GItS/tier0/engine/powers.py:15-23,118-179; /home/user/GItS/tier0/engine/combat.py:470-483; /home/user/GItS/tier0/tests/test_relics_combat_start.py:145-158; /home/user/GItS/klee-mod/KleeCode/KleeRelicPool.cs:1-49*

### red_skull — CLEAN
*legs read: /home/user/GItS/tier05/content/relics.yaml:131-137; /home/user/GItS/tier0/engine/relics.py:30,43-49,59-75,159-161,178-232; /home/user/GItS/tier0/engine/combat.py:318-324,470-493,808-818; /home/user/GItS/tier05/relics.py:114-119,129-134,251-284; /home/user/GItS/tier0/tests/test_relics_dynamic.py:118-167; /home/user/GItS/tier05/tests/test_relic_granting.py:133-152*

### regal_pillow — 1 finding(s)
*legs read: /home/user/GItS/tier05/content/relics.yaml:97-100; /home/user/GItS/tier0/engine/relics.py:51-57; /home/user/GItS/tier05/relics.py:50-51,338-342,467-468; /home/user/GItS/tier05/model.py:102-150,455-487; /home/user/GItS/tier05/tests/test_relics_runlayer.py:130-140; /home/user/GItS/docs/archive/relic-potion-layer-plan.md:159*
1. **[MEDIUM · semantic_drift]** Regal Pillow's post_rest_heal fires on EVERY campfire node regardless of the action taken, not only when the pilot actually Rests. The hook is named post_rest_heal and the spec table describes the relic as "heal +15 on Rest", but tier05/model.py applies the +15 outside the action branch, so a campfire resolved as a card removal or a rest-site smith still pays the heal.
   - `/home/user/GItS/tier05/content/relics.yaml:100 — `- {hook: post_rest_heal, amount: 15}` (hook name asserts the heal is post-REST)`
   - `/home/user/GItS/docs/archive/relic-potion-layer-plan.md:159 — `| Regal Pillow | heal +15 on Rest | run-layer at `R` ✓ |``
   - `/home/user/GItS/tier05/model.py:473-478 — the three mutually exclusive campfire outcomes (`if action == "heal"` / `elif action == "remove"` / `else:` smith)`
   - `/home/user/GItS/tier05/model.py:479-484 — `if held is not None: heal = held.post_rest_heal(); if heal: hp = min(max_hp, hp + heal)` sits AFTER and OUTSIDE that if/elif/else, at the same indent level, so it runs for all three actions`
   - `/home/user/GItS/tier05/model.py:124-150 — `rest_action` really does return "remove" and "upgrade" (rest-site smithing), so the non-heal branches are live, not dead`
   - `/home/user/GItS/tier05/relics.py:467-468 — `post_rest_heal()` is an unconditional sum over the run effects; it carries no rest-action gate of its own`
   - note: The gallery entry (/home/user/GItS/review/potion-relic-gallery/gallery.md:710) explicitly documents this as frozen intended behaviour ("it fires regardless of which rest action the pilot picked (even a remove or an upgrade)"), so this is drift between the hook name + plan-doc wording and the interpreter rather than an undiscovered bug — filed as medium, not high, for that reason. No C# leg exists or is expected (klee-mod borrows SilentRelicPool wholesale; see KleeRelicPool.cs:36-40).

### sand_castle — CLEAN
*legs read: /home/user/GItS/tier05/content/relics.yaml:184-191; /home/user/GItS/tier0/engine/relics.py:51-57; /home/user/GItS/tier05/relics.py:43-51,85-87,180,204-227,264-284,319-334,377-416; /home/user/GItS/tier05/model.py:736-744; /home/user/GItS/docs/act2-act3-roster-research.md:209-211; /home/user/GItS/review/potion-relic-gallery/gallery.md:998-999*

### signet_ring — 1 finding(s)
*legs read: /home/user/GItS/tier05/content/relics.yaml:249-252; /home/user/GItS/tier0/engine/relics.py:51-57; /home/user/GItS/tier05/relics.py:85-87,185,204-227,377-401; /home/user/GItS/tier05/model.py:303,386-390,400-407,432-439,508-527,620-651,736-758; /home/user/GItS/tier05/tests/test_multiact.py:142-155; /home/user/GItS/docs/act2-act3-roster-research.md:211*
1. **[LOW · other]** The +999 gold Signet Ring grants at an act boundary lands in the run's local `gold` but is never written back to `RunResult.gold` at that site, so a run that dies before the next node that assigns `res.gold` under-reports its gold by 999.
   - `/home/user/GItS/tier05/content/relics.yaml:252 — `- {hook: gold_on_pickup, amount: 999}``
   - `/home/user/GItS/tier05/relics.py:389-390 — `elif hook == "gold_on_pickup": gold += int(fx["amount"])` (the value is returned to the caller, not stored)`
   - `/home/user/GItS/tier05/model.py:742-744 — the Ancient pick site: `hp, max_hp, gold = held.add(pick, character, hp, max_hp, gold, deck_ids, rng)` with no `res.gold = gold` following it`
   - `/home/user/GItS/tier05/model.py:641 — the last `res.gold = gold` before it, executed inside the won-fight block earlier in the same boss-node iteration (i.e. BEFORE the 999 is added)`
   - `/home/user/GItS/tier05/model.py:643-650 — the death exit writes res.death_node/deck_ids/relics/potions_end but never res.gold`
   - `/home/user/GItS/tier05/model.py:753-758 — the run-end tail sets res.won/deck_ids/relics/potions_end and likewise never res.gold`
   - note: Contrast the other two mid-run `held.add` sites, which DO refresh the field: model.py:386-390 (Neow/shop shelf) and model.py:432-439. On a surviving run the next won fight (model.py:641), shop (407/439) or event (526) refreshes res.gold from the same cumulative local, so the divergence is confined to death runs and to any consumer reading res.gold between the act boundary and the next such write — hence low. Everything else about signet_ring checks out: ancient-pool membership, no owner lock, idempotent one-shot grant via HeldRelics.add, weight 2 in _NEOW_HOOK_WEIGHT matching the test pin at test_multiact.py:150-152. No C# leg exists or is expected.

### strawberry — CLEAN
*legs read: /home/user/GItS/tier05/content/relics.yaml:81-85; /home/user/GItS/tier0/engine/relics.py:51-57; /home/user/GItS/tier05/relics.py:50-51,178,264-284,310-334,368-401; /home/user/GItS/tier05/model.py:296-316,426-439; /home/user/GItS/tier05/tests/test_relics_runlayer.py:94-107; /home/user/GItS/tier05/tests/test_neow_and_shop.py:192-214*

### strike_dummy — CLEAN
*legs read: /home/user/GItS/tier05/content/relics.yaml:74-79; /home/user/GItS/tier0/engine/relics.py:29,43-49,254-268; /home/user/GItS/tier0/engine/effects.py:498,540-558,2152-2156; /home/user/GItS/tier0/content/cards/ironclad_starter.yaml:1-5; /home/user/GItS/tier0/content/cards/ironclad_package.yaml:27-28; /home/user/GItS/tier0/tests/test_relics_dynamic.py:100-115*

### touch_of_orobas_klee — 1 finding(s)
*legs read: tier05/content/relics.yaml:193-214 (ancient pool entry, owner: [klee], combat_start_spark 3); tier05/relics.py:158-194 (_NEOW_HOOK_WEIGHT + _neow_value); tier05/relics.py:204-227 (unowned_ancient / ancient_offer / ancient_pick); tier05/relics.py:251-284 (owner gate + split_effects); tier05/model.py:735-744 (the only Ancient acquisition site); tier0/engine/relics.py:43-49, 92-161 (COMBAT_HOOKS, apply_combat_start, combat_start_spark branch)*
1. **[HIGH · sheet_vs_sim_divergence]** combat_start_spark has no row in the Ancient/Neow valuation table, so touch_of_orobas_klee is valued at 0 and the tier05 pilot can never pick it — the boon is declared, owner-gated and offerable but unreachable in every run.
   - `tier05/content/relics.yaml:193-214 — ancient pool entry `touch_of_orobas_klee` with `owner: [klee]` and `- {hook: combat_start_spark, amount: 3}``
   - `tier05/relics.py:160-186 — `_NEOW_HOOK_WEIGHT` lists 19 hooks (combat_start_energy 10 … gold_on_pickup 2) and contains no `combat_start_spark` key`
   - `tier05/relics.py:193-194 — `return sum(_NEOW_HOOK_WEIGHT.get(fx.get("hook"), 0) for fx in ...)` silently defaults the unknown hook to 0`
   - `tier05/relics.py:222-227 — `ancient_pick` returns `max(sorted(offer), key=lambda rid: _neow_value(rid, character))`, so a 0-valued boon loses to every other Ancient (lowest competing value is signet_ring at 2)`
   - `tier05/model.py:740-743 — `offer = relic_pool.ancient_offer(...); pick = relic_pool.ancient_pick(...)` is the only path that ever calls `held.add(pick, ...)` for an Ancient boon`
   - `tier0/engine/relics.py:137-158 — the `combat_start_spark` branch exists and works, so the relic is implemented but never delivered`
   - note: Empirically confirmed read-only: `relic_pool.unowned_ancient([], 'klee')` includes touch_of_orobas_klee, and _neow_value scores it 0 against diamond_diadem 6 / looming_fruit 5 / paels_blood 8 / prismatic_gem 12 / sand_castle 4 / signet_ring 2 / very_hot_cocoa 10 / yummy_cookie 4. Over 2000 seeded ancient_offer+ancient_pick draws for klee the pick distribution was prismatic_gem 654, very_hot_cocoa 511, paels_blood 362, diamond_diadem 229, looming_fruit 145, sand_castle 83, yummy_cookie 16, touch_of_orobas_klee 0. Consequences: (a) relics.yaml:210-212 records a ratified measurement ("spark +2.3pt, demolition +7.1, reaction +5.0") for a boon no tier05 anchor can now acquire; (b) tools/lint_constant_parity.py:88-89 mirrors ExplosiveFrags.OpeningSparks against a yaml row the sim never exercises. Note the zero is produced by table omission, not by a ranking judgment — which is the one silent-default in a module whose header (tier05/relics.py:18-19) states "a run hook this module does not recognise raises a loud warnings.warn rather than being silently dropped". Everything else on this relic checks out: owner gating works (a furina holder warns loudly and gets [] via tier05/relics.py:256-260), amount 3 == C# OpeningSparks 3, the sim keeps spark_on_detonation at 1/detonation (tier0/engine/effects.py:448) exactly as ExplosiveFrags.SparksPerDetonation = 1 (UpgradedStarterRelics.cs:126), and the C# fires the bank at AfterPlayerTurnStart TurnNumber==1 (UpgradedStarterRelics.cs:202-209) which is the same moment as apply_combat_start (tier0/engine/relics.py:92-103). Out of scope for this entity but adjacent: UpgradedStarterRelics.cs:340-347 self-documents that Furina's Orobas variant has no tier05 row at all.

### vajra — CLEAN
*legs read: tier05/content/relics.yaml:17-20 (common pool, combat_start_power strength 1); tier0/engine/relics.py:43-49, 108-117 (COMBAT_HOOKS, combat_start_power branch); tier0/engine/powers.py:153-179 (apply_power); tier05/relics.py:264-284 (split_effects); tier05/model.py:531-551 (per-fight relic_effects seam); tier0/tests/test_relics_combat_start.py:47-58*

### venerable_tea_set — CLEAN
*legs read: tier05/content/relics.yaml:102-105 (common pool, post_rest_energy 2); tier0/engine/relics.py:53-57 (post_rest_energy in RUN_HOOKS — recognised, not alarmed); tier05/relics.py:346-364 (combat_effects_for injects combat_start_energy on just_rested); tier05/model.py:332, 479-485, 531-536 (just_rested set at the rest node, consumed and cleared at the next fight); tier0/engine/relics.py:120-123 (combat_start_energy applied turn 1 after the energy reset); tier05/tests/test_relics_runlayer.py:216-235*

### very_hot_cocoa — CLEAN
*legs read: tier05/content/relics.yaml:220-223 (ancient pool, combat_start_energy 4); tier0/engine/relics.py:43-49, 120-123 (combat_start_energy, turn-1 only, applied after the turn's own refill); tier05/relics.py:161, 189-194, 222-227 (weight 10; reachable via ancient_pick); tier05/model.py:740-743 (Ancient acquisition); tier05/tests/test_multiact.py:148-154; docs/act2-act3-roster-research.md:209-210*

### war_paint — CLEAN
*legs read: tier05/content/relics.yaml:107-111 (common pool, pickup_upgrade kind: skill count: 2); tier05/relics.py:43-51 (pickup_upgrade added to the tier05 RUN_HOOKS set only); tier05/relics.py:319-334, 368-416 (add / apply_pickups / _apply_pickup_fx / _pickup_upgrade); tier0/content/upgrades.py:36-96 (UPGRADE_SHEETS, has_upgrade, SUFFIX); tier0/engine/relics.py:53-57 (pickup_upgrade absent from engine RUN_HOOKS — verified unreachable there, see notes); tier05/model.py:312, 386, 632 (pickup sites)*

### whetstone — CLEAN
*legs read: tier05/content/relics.yaml:113-116 (common pool, pickup_upgrade kind: attack count: 2); tier05/relics.py:403-416 (_pickup_upgrade: has_upgrade filter, card.type == kind, rng.shuffle, cands[:count]); tier0/content/upgrades.py:89-96 (has_upgrade); tier05/model.py:312, 386, 632 (pickup sites); docs/archive/relic-potion-layer-plan.md:162*

### yummy_cookie — CLEAN
*legs read: tier05/content/relics.yaml:215-218 (ancient pool, pickup_upgrade count: 4, no kind); tier05/relics.py:180 (pickup_upgrade weight 4), 222-227 (ancient_pick), 391-393, 403-416 (kind=None -> any card type); tier05/model.py:740-743 (Ancient acquisition applies the pickup once via held.add); tier05/relics.py:319-334 (add is idempotent per id, so the upgrade cannot double-fire); docs/act2-act3-roster-research.md:209*

## potions

### block_potion — 2 finding(s)
*legs read: /home/user/GItS/tier05/content/potions.yaml:1-37; /home/user/GItS/tier0/engine/potions.py:1-251; /home/user/GItS/tier0/constants.py:501-518; /home/user/GItS/tier0/engine/powers.py:41-180; /home/user/GItS/tier0/engine/refpowers.py:97-240; /home/user/GItS/tier0/engine/effects.py:615-650*
1. **[LOW · semantic_drift]** block_potion writes Block with a bare field increment, bypassing BOTH engine block funnels and emitting no `block` event, so its 12 Block is the only block source in the engine that is invisible to FightStats.total_block_gained and to every AfterBlockGained/multiplicative block hook — while its sibling blood_potion does emit its event and IS counted.
   - `/home/user/GItS/tier0/engine/potions.py:73-74`
   - `/home/user/GItS/tier0/engine/refpowers.py:178-199`
   - `/home/user/GItS/tier0/engine/refpowers.py:223-231`
   - `/home/user/GItS/tier0/engine/powers.py:75-115`
   - `/home/user/GItS/tier0/engine/effects.py:630-637`
   - `/home/user/GItS/tier0/harness/metrics.py:136-137`
   - note: refpowers.gain_block:180 calls itself "the single chokepoint for block gains that powers can see" and _after_block_gained:230-231 says Juggernaut "fires on EVERY block gain ... that is why block has to be one chokepoint rather than six patched sites"; potions.py:74 is an unpatched seventh site. The behavioural half (Juggernaut / Shadowmeld) is currently unreachable — grep of tier0/content/*.yaml finds no card or enemy granting `juggernaut` or `shadowmeld` — which is why this is low, not medium. Dexterity/Frail NOT applying is correct, not drift: powers.modify_block_gained:75-92 is deliberately card-block-only. Timing verified correct: block is cleared at combat.py:429-430 and the potion drink runs later at combat.py:484-488, so the 12 Block survives into the enemy turn (pinned by test_potion_policy.py:59-65).
2. **[LOW · sheet_vs_sim_divergence]** The yaml's stated rarity intent ("common frequent, uncommon middling") inverts per potion under the interpreter's roll: roll_potion picks a tier by weight then a potion UNIFORMLY inside it, so each of the 6 common ids (block_potion among them) rolls at 0.65/6 = 10.83% while each of the 2 uncommon ids rolls at 0.30/2 = 15.0% — an individual common potion is rarer than an individual uncommon one.
   - `/home/user/GItS/tier05/content/potions.yaml:12-14`
   - `/home/user/GItS/tier05/content/potions.yaml:16-22`
   - `/home/user/GItS/tier05/content/potions.yaml:24-26`
   - `/home/user/GItS/tier05/content/potions.yaml:31-36`
   - `/home/user/GItS/tier05/potions.py:86-111`
   - note: Pool-shape property shared by all five common-tier potions in this group; filed on each so per-entity coverage is provable. The yaml itself performs the tier-weight -> per-item-scarcity inference at line 12-14 ("rare holds ONLY fairy_in_a_bottle, so the low rare weight is what makes the revive the scarce prize"), which is what makes the same inference applied to common vs uncommon a spec-vs-sim mismatch rather than a wording quibble. Shop stock (tier05/model.py:446-452) and post-fight drops (tier05/model.py:637-640) both route through roll_potion, so both surfaces inherit it consistently — no shop/reward-vs-yaml weight divergence found.

### blood_potion — 1 finding(s)
*legs read: /home/user/GItS/tier05/content/potions.yaml:1-37; /home/user/GItS/tier0/engine/potions.py:1-251; /home/user/GItS/tier0/constants.py:501-518; /home/user/GItS/tier0/engine/combat.py:480-500; /home/user/GItS/tier0/harness/metrics.py:114-215; /home/user/GItS/tier05/model.py:530-560*
1. **[LOW · sheet_vs_sim_divergence]** The yaml's stated rarity intent ("common frequent, uncommon middling") inverts per potion under the interpreter's roll: roll_potion picks a tier by weight then a potion UNIFORMLY inside it, so each of the 6 common ids (blood_potion among them) rolls at 0.65/6 = 10.83% while each of the 2 uncommon ids rolls at 0.30/2 = 15.0% — an individual common potion is rarer than an individual uncommon one.
   - `/home/user/GItS/tier05/content/potions.yaml:12-14`
   - `/home/user/GItS/tier05/content/potions.yaml:16-22`
   - `/home/user/GItS/tier05/content/potions.yaml:24-26`
   - `/home/user/GItS/tier05/content/potions.yaml:31-36`
   - `/home/user/GItS/tier05/potions.py:86-111`
   - note: Pool-shape property shared by all five common-tier potions in this group; filed on each so per-entity coverage is provable. This is the ONLY finding on blood_potion — the potion itself is clean on every leg: yaml:19 "heal 20% of max HP" matches POTION_BLOOD_HEAL_FRACTION=0.20 (constants.py:507) and potions.py:78-82 (int() floor of MAX HP, clamped by min(heal, max_hp - hp)); the heal emits `heal` so metrics.py:153-154 counts it; the run layer reads the healed HP back at tier05/model.py:598 so it carries across fights; and the anti-waste guard at potions.py:193 (`p.hp < p.max_hp`) is real and pinned by test_potion_policy.py:77-86.

### energy_potion — 3 finding(s)
*legs read: tier05/content/potions.yaml:1-36; tier0/engine/potions.py:1-250; tier0/constants.py:503-518,729-731; tier05/potions.py:1-139; tier05/model.py:436-452,478-525,634-640; tier05/events.py:365-392,478-500*
1. **[HIGH · sheet_vs_sim_divergence]** An event's `spend_potion` cost is never actually paid: the resolver pops from a throwaway copy of the bag and the run layer never copies potions back, so the reward is granted free and the potion is retained.
   - `tier05/content/events.yaml:33 — "spend_potion: true requires a held potion; consumes it"`
   - `tier05/content/events.yaml:269-270 — `the_future_of_potions` in the `all:` pool (events.yaml:250)`
   - `tier05/events.py:384-385 — `st.potions.pop(rng.randrange(len(st.potions)))` mutates EventState only`
   - `tier05/model.py:504 — `potions=list(bag.potions) if bag else [],` (snapshot copy)`
   - `tier05/model.py:508-510 — copy-back omits `est.potions``
   - `tier05/model.py:489-492 — comment claims potions results are copied back`
   - note: SYSTEMIC — identical finding filed on all four ids in this group.
2. **[MEDIUM · missing_leg]** energy_potion is declared drinkable by the use policy but NO policy branch ever selects it: neither the defensive nor the offensive ladder mentions it, so a bought/dropped Energy Potion is held for the whole run, permanently occupying one of three bag slots.
   - `tier0/engine/potions.py:45-49 — `# Potions the use-policy may proactively DRINK (fairy is passive; excluded).` / `DRINKABLE = frozenset({..., "energy_potion"})``
   - `tier0/engine/potions.py:34-36 — "USE POLICY: a bounded greedy heuristic ... try_use_potions runs at the player's turn start"`
   - `tier0/engine/potions.py:178-194 — `_try_defensive` handles only block_potion and blood_potion`
   - `tier0/engine/potions.py:197-231 — `_try_offensive` handles only fire_potion, weak_potion, fear_potion, strength_potion`
   - `tier05/model.py:446-452 — the shop nevertheless auto-buys it for `C.POTION_PRICE` (50 gold, tier0/constants.py:731) whenever it rolls and a slot is free`
   - `tier05/model.py:637-640 — and drops can hand it out after every won N/E fight`
   - note: The effect implementation itself is correct and correctly timed (`p.energy += C.POTION_ENERGY` at potions.py:92-93, C.POTION_ENERGY = 2 at constants.py:512, drunk after the turn's energy reset at combat.py:458 per combat.py:484-486), so the gap is purely the missing policy leg. Known-but-unfixed: recorded as a factual note in review/potion-relic-gallery/gallery.md:271 ("the id is listed in DRINKABLE, but the greedy use policy never actually selects it") and gallery.md:196; NOT documented in the engine, whose DRINKABLE comment still asserts the opposite. swift_potion (outside this group) has the same gap.
3. **[MEDIUM · sheet_vs_sim_divergence]** energy_potion is labelled 'uncommon' but rolls at 15% (0.30/2), strictly MORE often than any 'common frequent' potion at 10.83% (0.65/6).
   - `tier05/content/potions.yaml:12-14 — "common frequent, uncommon middling, rare scarce"`
   - `tier05/content/potions.yaml:24-26 — uncommon tier holds exactly two ids`
   - `tier05/content/potions.yaml:31-36 — weights common 0.65 / uncommon 0.30 / rare 0.05, "Common-heavy ... mirrors the StS potion-rarity feel"`
   - `tier05/potions.py:86-93,103-111 — weighted tier pick then uniform `rng.choice` within the tier`
   - note: Compounds the missing-policy finding: the never-drunk potion is also the joint-most-frequent roll in the pool.

### fairy_in_a_bottle — 3 finding(s)
*legs read: tier05/content/potions.yaml:1-36; tier0/engine/potions.py:1-52,238-250; tier0/constants.py:503-518; tier05/potions.py:1-139; tier05/model.py:478-525,600-650,755-765; tier05/events.py:225-330,365-392,478-500*
1. **[HIGH · sheet_vs_sim_divergence]** An event's `spend_potion` cost is never actually paid: the resolver pops from a throwaway copy of the bag and the run layer never copies potions back, so the reward is granted free and the potion is retained.
   - `tier05/content/events.yaml:33 — "spend_potion: true requires a held potion; consumes it"`
   - `tier05/content/events.yaml:269-270 — `the_future_of_potions` in the `all:` pool (events.yaml:250)`
   - `tier05/events.py:384-385 — `st.potions.pop(rng.randrange(len(st.potions)))` mutates EventState only`
   - `tier05/model.py:504 — `potions=list(bag.potions) if bag else [],` (snapshot copy)`
   - `tier05/model.py:508-510 — copy-back omits `est.potions``
   - `tier05/model.py:489-492 — comment claims potions results are copied back`
   - note: SYSTEMIC — identical finding filed on all four ids in this group.
2. **[LOW · semantic_drift]** The yaml describes Fairy in a Bottle as an unqualified passive revive, but the revive exists only inside combat; the run layer's out-of-combat death path never consults it, and the event layer's own justification for refusing lethal options asserts that nothing in the run model can survive lethal HP loss.
   - `tier05/content/potions.yaml:29 — `fairy_in_a_bottle: {name: "Fairy in a Bottle"}  # passive revive at 30% max HP` (no combat scoping)`
   - `tier0/engine/potions.py:30-32 — the engine's honest scoping: "PASSIVE: on lethal damage, revive at POTION_FAIRY_REVIVE_FRACTION of max HP (see try_fairy_revive, called from combat HP checkpoints)"`
   - `tier0/engine/potions.py:238-249 — try_fairy_revive is only ever reached from combat.py checkpoints`
   - `tier05/model.py:513-523 — `if hp <= 0:  # an event CAN kill (real rule)` returns a death result while `bag.potions` (possibly holding the fairy) is merely recorded into res.potions_end`
   - `tier05/events.py:306-311 — "A lethal option stays legal in the real game; ours refuses, because nothing in the run model can survive it (no Lizard Tail)" / `if st.hp + min(0, opt.get("hp", 0)) <= 0: continue``
   - note: No player-visible effect today: the two gaps cancel — events.py:309 filters every lethal option, so model.py:513 is unreachable via the `hp:` cost path (max_hp costs clamp to hp>=1 at events.py:376-378). Comment/scope drift only. Combat-side wiring is thorough and correct: try_fairy_revive is called at 7 checkpoints (combat.py:322,450,454,469,554,587,687) covering DoT, Salon overdraw, self-damage, turn-end status damage and per-hit enemy attacks, and the revive value matches spec exactly (potions.yaml:29 30% == C.POTION_FAIRY_REVIVE_FRACTION 0.30, constants.py:513, applied at potions.py:248).
3. **[LOW · semantic_drift]** The event `spend_potion` cost picks a held potion uniformly at random and values it at a flat POTION_HP, so the rare revive the pool designates as its scarce prize is traded on exactly the same terms as a common Block Potion.
   - `tier05/events.py:384-385 — `st.potions.pop(rng.randrange(len(st.potions)))` — uniform over held ids, no rarity or id awareness`
   - `tier05/events.py:286-287 — `if opt.get("spend_potion"): v -= POTION_HP` — flat 6.0 (tier05/events.py:221) regardless of which potion is at risk`
   - `tier05/content/potions.yaml:12-14 — "rare holds ONLY fairy_in_a_bottle, so the low rare weight is what makes the revive the scarce prize the design asks for"`
   - `tier05/potions.py:86-89 — the same claim restated in roll_potion's docstring: "rare holds only fairy_in_a_bottle, so its low weight is what makes the revive scarce"`
   - note: Currently MASKED by the high-severity finding above — since the pop never reaches the real bag, no fairy is actually lost today. Filed as latent: fixing the copy-back without adding rarity awareness here would immediately make a 5%-rate revive spendable at a common potion's valuation.

### fear_potion — 4 finding(s)
*legs read: tier05/content/potions.yaml:1-36; tier0/engine/potions.py:1-250; tier0/constants.py:503-518,28-30; tier05/potions.py:1-139; tier05/model.py:436-452,478-525,634-640; tier05/events.py:225-330,365-392,478-500*
1. **[HIGH · sheet_vs_sim_divergence]** An event's `spend_potion` cost is never actually paid: the resolver pops from a throwaway copy of the bag and the run layer never copies potions back, so the reward is granted free and the potion (fear_potion included) is retained.
   - `tier05/content/events.yaml:33 — "spend_potion: true requires a held potion; consumes it"`
   - `tier05/content/events.yaml:269-270 — the only consumer, `the_future_of_potions`, in the `all:` pool (events.yaml:250)`
   - `tier05/events.py:384-385 — `st.potions.pop(rng.randrange(len(st.potions)))` mutates EventState only`
   - `tier05/model.py:504 — `potions=list(bag.potions) if bag else [],` (snapshot copy)`
   - `tier05/model.py:508-510 — copy-back of hp/max_hp/gold/deck_ids/log with no `est.potions` write-back`
   - `tier05/model.py:489-492 — comment claims "pure over deck/HP/gold/relics/potions ... its results are copied back"`
   - note: SYSTEMIC — identical finding filed on all four ids in this group.
2. **[MEDIUM · sim_vs_csharp_divergence]** The understudy wire arm aims fear_potion with a different helper than the sim's own branch used, so the target sent to the live game can be a different enemy than the sim decided to hit.
   - `tier0/engine/potions.py:222-226 — sim's choice: `if "fear_potion" in p.potions and (big_hit or _has_boss(state)): target = attacker if big_hit else _highest_hp_enemy(state)``
   - `understudy/policy_v1.py:333-337 — wire's aim: `if pid in t0potions._TARGETED: tgt = (t0potions._biggest_attacker(cs)[0] if pid in ("weak_potion", "fear_potion") else t0potions._lowest_hp_enemy(cs))``
   - `understudy/policy_v1.py:338-339 — fallback `if tgt is None: tgt = t0potions._lowest_hp_enemy(cs)``
   - `understudy/policy_v1.py:310-314 — the claim being broken: "the target is recovered by asking the sim's own target-choosing helpers with the same state it just saw"`
   - note: Divergence window: boss present with no big telegraph (big_hit False) — the sim targets the highest-HP enemy, the wire targets the biggest attacker, or the LOWEST-HP enemy when nothing is attacking. On a boss+minions board those are routinely different enemies. weak_potion is unaffected (the sim also uses `attacker`, potions.py:218).
3. **[MEDIUM · sheet_vs_sim_divergence]** fear_potion is labelled 'uncommon' but rolls at 15% (0.30/2), strictly MORE often than any potion in the 'common frequent' tier at 10.83% (0.65/6).
   - `tier05/content/potions.yaml:12-14 — "common frequent, uncommon middling, rare scarce"`
   - `tier05/content/potions.yaml:24-26 — the uncommon tier holds exactly two ids (`fear_potion`, `energy_potion`)`
   - `tier05/content/potions.yaml:31-36 — "Common-heavy ... mirrors the StS potion-rarity feel"; weights 0.65/0.30/0.05`
   - `tier05/potions.py:86-93,103-111 — tier picked by weight, then `rng.choice(tiers_map[chosen])` uniform within the tier`
   - note: Same root cause as the weak_potion frequency finding, seen from the over-represented side.
4. **[LOW · semantic_drift]** apply_potion's fallback target for an untargeted call is the lowest-HP enemy, contradicting fear_potion's stated job of racing the boss / the dangerous enemy.
   - `tier0/engine/potions.py:54,67-68 — `_TARGETED` includes fear_potion; `target = _lowest_hp_enemy(state)` when none is passed`
   - `tier0/engine/potions.py:221-223 — "# 3. fear_potion (Vulnerable) races a dangerous enemy or the boss" / `target = attacker if big_hit else _highest_hp_enemy(state)``
   - note: Latent — unreachable via try_use_potions. Numbers clean: potions.yaml:25 '3 Vulnerable' == C.POTION_FEAR_VULN = 3 (constants.py:511) applied at potions.py:89-91; VULNERABLE_TAKEN_MULT 1.50 (constants.py:29) via powers.modify_damage_taken (powers.py:60-61).

### fire_potion — 2 finding(s)
*legs read: /home/user/GItS/tier05/content/potions.yaml:1-37; /home/user/GItS/tier0/engine/potions.py:1-251; /home/user/GItS/tier0/constants.py:501-518; /home/user/GItS/tier0/engine/refpowers.py:97-124; /home/user/GItS/tier0/engine/combat.py:64-95; /home/user/GItS/tier0/engine/combat.py:480-500*
1. **[MEDIUM · semantic_drift]** The offensive policy's "close a kill outright" gate for fire_potion tests raw enemy HP only (`0 < e.hp <= POTION_FIRE_DAMAGE`) and ignores enemy Block, but the effect it fires goes through refpowers.unpowered_damage, which subtracts Block before HP. Against an enemy holding Block the potion is consumed and the enemy survives — the one case the policy explicitly claims it is spending the potion to avoid.
   - `/home/user/GItS/tier0/engine/potions.py:197-210`
   - `/home/user/GItS/tier0/engine/refpowers.py:107-118`
   - `/home/user/GItS/tier0/engine/potions.py:76`
   - `/home/user/GItS/tier0/engine/combat.py:694-695`
   - `/home/user/GItS/tier0/engine/combat.py:597`
   - `/home/user/GItS/tier0/engine/combat.py:613-616`
   - note: Reachability is explicit in the engine: combat.py:597 clears enemy Block at the start of that enemy's OWN turn, and combat.py:613-616 states in-comment that block gained there "survive[s] into the player's next turn" — which is exactly when combat.py:484-488 runs try_use_potions. So an enemy that telegraphed a `block` intent (combat.py:695) is standing at the drink site with Block up. Concrete: enemy at hp 15 with block 10 passes the killable filter (15 <= 20), fire deals 20 -> 10 absorbed, 10 to HP, enemy alive at 5 and the potion is gone. refpowers.py:107 states "Block still applies (Unpowered is not Unblockable)", so the two sides of this disagreement are both documented, just never reconciled. The flat-damage / no-Strength / no-Vulnerable half is correct and pinned (test_potion_effects.py:46-55), and the untargeted lowest-HP default matches the yaml (test_potion_effects.py:58-64).
2. **[LOW · sheet_vs_sim_divergence]** The yaml's stated rarity intent ("common frequent, uncommon middling") inverts per potion under the interpreter's roll: roll_potion picks a tier by weight then a potion UNIFORMLY inside it, so each of the 6 common ids (fire_potion among them) rolls at 0.65/6 = 10.83% while each of the 2 uncommon ids rolls at 0.30/2 = 15.0%.
   - `/home/user/GItS/tier05/content/potions.yaml:12-14`
   - `/home/user/GItS/tier05/content/potions.yaml:16-22`
   - `/home/user/GItS/tier05/content/potions.yaml:24-26`
   - `/home/user/GItS/tier05/content/potions.yaml:31-36`
   - `/home/user/GItS/tier05/potions.py:86-111`
   - note: Pool-shape property shared by all five common-tier potions in this group; filed on each so per-entity coverage is provable.

### strength_potion — 2 finding(s)
*legs read: /home/user/GItS/tier05/content/potions.yaml:1-37; /home/user/GItS/tier0/engine/potions.py:1-251; /home/user/GItS/tier0/constants.py:501-518; /home/user/GItS/tier0/engine/powers.py:1-180; /home/user/GItS/tier0/content/characters/kokomi.yaml:50; /home/user/GItS/tier0/engine/refpowers.py:275-290*
1. **[MEDIUM · text_ops_mismatch]** Both spec surfaces state strength_potion grants "+2 Strength this combat", and the use-policy spends it on the stated rationale "races an elite/boss (combat-scoped +Strength)" — but for Kokomi the apply_power chokepoint converts ALL positive player Strength to Charge, so on Kokomi the potion never grants a single point of Strength. tamakushi_casket is not an acquirable relic: it is an innate character relic_hook, so this holds for every Kokomi run, not an edge case.
   - `/home/user/GItS/tier05/content/potions.yaml:20`
   - `/home/user/GItS/tier0/engine/potions.py:24-25`
   - `/home/user/GItS/tier0/engine/potions.py:83-84`
   - `/home/user/GItS/tier0/engine/potions.py:228-231`
   - `/home/user/GItS/tier0/engine/powers.py:156-168`
   - `/home/user/GItS/tier0/content/characters/kokomi.yaml:50`
   - note: powers.py:156-162 documents the conversion as intentional and names potions as one of the four inbound paths, and review/potion-relic-gallery/gallery.md:163 carries the caveat — but neither the pool spec (potions.yaml:20) nor the engine's own POTION VOCABULARY block (potions.py:24-25) nor the policy comment that justifies drinking it (potions.py:228) mentions it, so the three surfaces a reader would consult for this potion's payload all promise Strength. Reachable: tier05 realistic cells run grant_potions=True together with the full roster (tier05/cells.py:202). Secondary note (not filed): potions.py:24 also says Strength "decays with the combat like any power", while powers.DECAYING at powers.py:19-20 deliberately excludes strength — the sentence is defensible as "combat-scoped" (the run layer rebuilds the player per fight at tier05/model.py:544-547), so I did not file it.
2. **[LOW · sheet_vs_sim_divergence]** The yaml's stated rarity intent ("common frequent, uncommon middling") inverts per potion under the interpreter's roll: roll_potion picks a tier by weight then a potion UNIFORMLY inside it, so each of the 6 common ids (strength_potion among them) rolls at 0.65/6 = 10.83% while each of the 2 uncommon ids rolls at 0.30/2 = 15.0%.
   - `/home/user/GItS/tier05/content/potions.yaml:12-14`
   - `/home/user/GItS/tier05/content/potions.yaml:16-22`
   - `/home/user/GItS/tier05/content/potions.yaml:24-26`
   - `/home/user/GItS/tier05/content/potions.yaml:31-36`
   - `/home/user/GItS/tier05/potions.py:86-111`
   - note: Pool-shape property shared by all five common-tier potions in this group; filed on each so per-entity coverage is provable.

### swift_potion — 2 finding(s)
*legs read: /home/user/GItS/tier05/content/potions.yaml:1-37; /home/user/GItS/tier0/engine/potions.py:1-251; /home/user/GItS/tier0/constants.py:501-518; /home/user/GItS/tier0/engine/state.py:649-680; /home/user/GItS/tier05/potions.py:86-140; /home/user/GItS/tier05/model.py:425-460*
1. **[MEDIUM · missing_leg]** swift_potion is listed in DRINKABLE — the set the file defines as "Potions the use-policy may proactively DRINK" — but no branch of the use policy ever references it: _try_defensive considers only block_potion and blood_potion, and _try_offensive only fire/weak/fear/strength. Under autoplay (the only way this simulator runs) swift_potion is rolled from the common tier, bought or dropped into the bag, occupies a slot for the rest of the run and is never drunk. Its use-policy leg is absent.
   - `/home/user/GItS/tier0/engine/potions.py:45-49`
   - `/home/user/GItS/tier0/engine/potions.py:165-176`
   - `/home/user/GItS/tier0/engine/potions.py:178-195`
   - `/home/user/GItS/tier0/engine/potions.py:197-231`
   - `/home/user/GItS/tier05/content/potions.yaml:21`
   - `/home/user/GItS/tier05/model.py:446-452`
   - note: The effect itself is correct and pinned (potions.py:85-86 -> state.draw(3), POTION_SWIFT_DRAW=3 at constants.py:509, test_potion_effects.py:99-107), so this is purely the missing policy leg. Cost is real, not cosmetic: the bag is 3 slots (constants.py:503) and tier05/potions.py:131-139 DISCARDS an incoming drop when the bag is full, so an un-drinkable held potion actively evicts drinkable ones. Known/documented at review/potion-relic-gallery/gallery.md:182, which states the same fact verbatim — I file it anyway because DRINKABLE's own docstring at potions.py:45 still asserts the opposite. Same gap exists for energy_potion (potions.py:48, gallery.md:271), which is outside this group.
2. **[LOW · sheet_vs_sim_divergence]** The yaml's stated rarity intent ("common frequent, uncommon middling") inverts per potion under the interpreter's roll: roll_potion picks a tier by weight then a potion UNIFORMLY inside it, so each of the 6 common ids (swift_potion among them) rolls at 0.65/6 = 10.83% while each of the 2 uncommon ids rolls at 0.30/2 = 15.0%.
   - `/home/user/GItS/tier05/content/potions.yaml:12-14`
   - `/home/user/GItS/tier05/content/potions.yaml:16-22`
   - `/home/user/GItS/tier05/content/potions.yaml:24-26`
   - `/home/user/GItS/tier05/content/potions.yaml:31-36`
   - `/home/user/GItS/tier05/potions.py:86-111`
   - note: Pool-shape property shared by all five common-tier potions in this group; filed on each so per-entity coverage is provable.

### weak_potion — 3 finding(s)
*legs read: tier05/content/potions.yaml:1-36; tier0/engine/potions.py:1-250; tier0/constants.py:503-518,729-731,28-30; tier05/potions.py:1-139; tier05/model.py:49-70,249-276,325-331,436-452,478-525,537-549,600-650,755-765; tier05/events.py:181-197,211-222,225-330,365-392,478-500,500-520*
1. **[HIGH · sheet_vs_sim_divergence]** An event's `spend_potion` cost is never actually paid: the event resolver pops from a THROWAWAY COPY of the potion bag, and the run layer never copies potions back, so "The Future of Potions?" hands out 3 upgraded card rewards while the potion (any id, weak_potion included) stays in the bag.
   - `tier05/content/events.yaml:33 — `#   spend_potion: true requires a held potion; consumes it``
   - `tier05/content/events.yaml:269-270 — `- {label: "Insert Potion", spend_potion: true, card_reward: 3, upgraded: true}` (under the `all:` pool, events.yaml:250, so reachable in every act)`
   - `tier05/events.py:384-385 — `if opt.get("spend_potion") and st.potions: st.potions.pop(rng.randrange(len(st.potions)))` (mutates EventState.potions only)`
   - `tier05/model.py:504 — `potions=list(bag.potions) if bag else [],` (EventState is built from a COPY of bag.potions)`
   - `tier05/model.py:508-510 — `hp, max_hp, gold = est.hp, est.max_hp, est.gold` / `deck_ids = est.deck_ids` / `res.events.extend(est.log)` — the copy-back omits `est.potions`, and no other line assigns `bag.potions = est.potions``
   - `tier05/model.py:489-492 — the comment that makes this a contract breach: "The resolver is pure over deck/HP/gold/relics/potions, so it is handed a snapshot and its results are copied back"`
   - note: SYSTEMIC potion-layer defect, identical for all four ids in this group — dedupe across entities if the parent merges. Player-visible: the option is valued at -POTION_HP + CARD_HP*3/3 = +2 (tier05/events.py:286-287,264) so the policy takes it, gets the reward for free, and res.potions_end over-reports the bag. Also desyncs the other way: a potion granted mid-visit via bag.add is invisible to a later `spend_potion` availability gate (tier05/events.py:300).
2. **[MEDIUM · sheet_vs_sim_divergence]** The pool's stated rarity semantics invert for weak_potion: as a 'common frequent' potion it rolls at 0.65/6 = 10.83%, strictly LESS often than either 'uncommon' potion at 0.30/2 = 15%, because roll_potion picks a tier by weight then uniformly within the tier and the uncommon tier holds only two ids.
   - `tier05/content/potions.yaml:12-14 — "Rarity: common frequent, uncommon middling, rare scarce -- and rare holds ONLY fairy_in_a_bottle, so the low rare weight is what makes the revive the scarce prize"`
   - `tier05/content/potions.yaml:16-22 — six commons including `weak_potion` (line 22)`
   - `tier05/content/potions.yaml:24-26 — two uncommons only (`fear_potion`, `energy_potion`)`
   - `tier05/content/potions.yaml:31-36 — "Common-heavy, rare scarce -- mirrors the StS potion-rarity feel"; weights common 0.65 / uncommon 0.30 / rare 0.05`
   - `tier05/potions.py:86-93 — docstring: "pick a tier by its weight, then a potion uniformly within that tier"`
   - `tier05/potions.py:103-111 — the implementation: weighted tier pick then `rng.choice(tiers_map[chosen])` (uniform within tier), giving 10.83% per common vs 15% per uncommon`
   - note: The yaml header reasons explicitly about pool size for the RARE tier (1 member x 0.05 = 5% < 10.83%, so the check passes there) but the same reasoning was not applied to the 2-member uncommon tier, where it inverts. No test pins per-id frequency (tier05/tests/test_potion_runlayer.py pins only the drop rate and slot cap).
3. **[LOW · semantic_drift]** apply_potion's fallback target for an untargeted call is the LOWEST-HP enemy, which for weak_potion is the opposite of the potion's stated job (blunting the biggest telegraphed hit).
   - `tier0/engine/potions.py:54 — `_TARGETED = frozenset({"fire_potion", "weak_potion", "fear_potion"})``
   - `tier0/engine/potions.py:67-68 — `if pid in _TARGETED and target is None: target = _lowest_hp_enemy(state)``
   - `tier0/engine/potions.py:216-218 — the policy's own statement of intent: "# 2. weak_potion blunts a big telegraphed hit (-25% damage dealt)" / `_drink(state, "weak_potion", attacker)` where `attacker` is `_biggest_attacker(state)[0]` (potions.py:213)`
   - note: Latent, not reachable through try_use_potions (the policy always passes an explicit target, potions.py:218). Only a direct apply_potion caller hits the lowest-HP default. Same fallback mis-fits fear_potion. Numbers themselves are clean: potions.yaml:22 '3 Weak' == C.POTION_WEAK = 3 (tier0/constants.py:510) applied at potions.py:88, and the -25% claim matches C.WEAK_DEALT_MULT = 0.75 (tier0/constants.py:28) via powers.modify_damage_dealt (tier0/engine/powers.py:52-53). Timing is correct: drunk at player turn start (combat.py:484-488), weak ticks at the OWNER's turn end (powers.py:19-20,139-142), so 3 stacks cover 3 enemy turns.

## events

### aroma_of_chaos — CLEAN
*legs read: docs/sts2-events-harvest.txt:38-40; docs/sts2-map-and-events-research.md:210; tier05/content/events.yaml:132-136; tier05/events.py:397-406 (transform), :428-436 (upgrade, on-plan first, skips already-upgraded via upgrades.has_upgrade), :279-281 (valuation); review/event-gallery/gallery.md:111-140, 1564-1565, 1707; klee-mod/ (grep: no AromaOfChaos implementation or reference)*

### brain_leech — 3 finding(s)
*legs read: docs/sts2-events-harvest.txt:48-50; docs/sts2-map-and-events-research.md:211,266,430,575; tier05/content/events.yaml:86-95; tier05/events.py:103-127 (also_acts), 263-266 (valuation), 357-362 (_random_pool_cards), 444-468 (pick_cards / card_reward screens); tier05/rewards.py:230-238; tier0/constants.py:772 (REWARD_CARD_OFFERS = 3)*
1. **[MEDIUM · text_ops_mismatch]** Every shipped gallery variant of the Rip branch promises TWO colorless/companion cards, but the shipped option is one 3-wide screen from which the drafter keeps exactly one card.
   - `review/event-gallery/gallery.md:192 ("Gain a Colorless 2 card reward -- two loose companion (Colorless) cards salvaged...")`
   - `review/event-gallery/gallery.md:200 ("two companion (Colorless) charms shaken from its belt")`
   - `review/event-gallery/gallery.md:17 ("which all three drafts gloss as *two* cards")`
   - `tier05/content/events.yaml:95 (`{label: "Rip the Leech Off", hp: -5, card_reward: 3}`)`
   - `tier05/events.py:457-468 (`screens = ([opt["card_reward"]] ...)`; one pick appended per screen -- `card_screens`, not `card_reward`, is the multi-reward op)`
   - note: The harvest's "Colorless 2" (docs/sts2-events-harvest.txt:50) is almost certainly a template-strip artifact of the StS2 wiki link -- the same trailing "2" appears on "random Power 2" (harvest:209), "Foul Potions 2" (harvest:221) and "Uncommon Potion 2" (harvest:222) -- so the yaml's one-screen reading is the defensible one and the gallery gloss is the wrong side. Either way the two surfaces disagree on the card count. Flagged as a [USER] decision at gallery.md:184, gallery.md:1569. The hp -5, pick_cards {of:5,take:1} and also_acts:[2] legs are all exact vs harvest:48-49 and pool_for (events.py:118-126, pinned by test_events_acts23.py:132-134).
2. **[LOW · semantic_drift]** The Rip branch's reward pool is the character pool, not a colorless pool, so the option's card COLOUR diverges from the harvest -- and this second flagged approximation contradicts the file's own header rule and its bottom-list claim that Room Full of Cheese is the only exception.
   - `docs/sts2-events-harvest.txt:50 ("Gain a ... Colorless ... card reward")`
   - `tier05/content/events.yaml:89-92 ("APPROXIMATION, flagged ... it draws from the character pool like any other screen. Shape right, colour wrong.")`
   - `tier05/content/events.yaml:4-5 ("No option is ever approximated to get an event in")`
   - `tier05/content/events.yaml:272-274 ("The one pre-existing exception is Room Full of Cheese above")`
   - `tier05/events.py:357-362 + 460 (`rewards.character_pool(st.character)` is the only source for event screens)`
   - `docs/sts2-map-and-events-research.md:575 (limitation stated)`
   - note: Fully disclosed in three places; filed low as rule-vs-content drift rather than a hidden defect.
3. **[LOW · semantic_drift]** "Choose 1 of 5 random cards" is sampled WITH replacement, so the 5-card screen can show the same card more than once and offer fewer than 5 distinct choices.
   - `tier05/content/events.yaml:94 (`pick_cards: {of: 5, take: 1}`)`
   - `tier05/events.py:357-362 (`return [flat[rng.randrange(len(flat))] for _ in range(n)]` -- independent draws, no dedupe)`
   - `tier05/events.py:446 (`offers = _random_pool_cards(rng, st, spec["of"])`)`
   - `docs/sts2-events-harvest.txt:49 ("Choose 1 of 5 random cards")`
   - `docs/sts2-map-and-events-research.md:217 (the sibling pick screen is recorded as "choose 2 of 8 random cards (no duplicates)")`
   - note: Systemic to the interpreter rather than to this entry -- tier05/rewards.py:233-238 draws post-fight offers the same way -- so the event screen is at least internally consistent with the sim's own reward screens. With take:1 the effect is narrowed choice, not a wrong card count.

### bugslayer — CLEAN
*legs read: docs/sts2-events-harvest.txt:52-54; tier05/content/events.yaml:161,197-207; tier05/events.py:58-70,239-292,317-336,409-410; tier0/content/cards/colorless_event.yaml:1-40; docs/sts2-map-and-events-research.md:227-241,563-570; tier05/tests/test_events_acts23.py:176-190*

### byrdonis_nest — 2 finding(s)
*legs read: docs/sts2-events-harvest.txt:56-58; docs/sts2-map-and-events-research.md:212,287; tier05/content/events.yaml:1-44,138-143,273-293; tier05/events.py:239-336,365-501; tier05/relics.py:377-401; review/event-gallery/gallery.md:235-262,1574-1575,1711*
1. **[MEDIUM · missing_leg]** Byrdonis Nest ships as a ONE-option event in the sim; the harvested base event has two options — the [Take the Egg] branch (add Byrdonis Egg to deck) is absent, so the event presents no choice at all.
   - `docs/sts2-events-harvest.txt:56-58 — '### [act1] Byrdonis Nest / [Eat the Egg] Gain 7 Max HP. / [Take the Egg] Add Byrdonis Egg to deck.'`
   - `tier05/content/events.yaml:138-143 — id: byrdonis_nest, options: single entry {label: "Eat the Egg", max_hp: 7}`
   - `tier05/content/events.yaml:284-286 — skip list: 'Quest cards are not modeled: ... Byrdonis Nest's Take-the-Egg branch (the event ships one-option)'`
   - `review/event-gallery/gallery.md:235-236 — gallery FLAG on the same branch; gallery.md:245/252/259 still render a second option ('Add Bathysmal/Windfalcon/Reef Egg (Byrdonis Egg) to deck') that events.yaml has no op for`
   - note: Option-count divergence 2 -> 1, which the sweep brief classes as a finding. It is DECLARED, not silent: the skip list and the gallery flag both name the missing quest-card hook, and gallery.md:1574 explicitly forbids reconciling by dropping the option from the drafts. Downrank on triage if declared-scope divergences are out of scope. Note the second-order effect: with one option, choose()/available() (tier05/events.py:295-336) can only return that option or None, so this event contributes nothing to the option-split telemetry the module header (tier05/events.py:9-14) says exists to expose policy bias.
2. **[MEDIUM · semantic_drift]** 'Gain 7 Max HP' raises max HP without raising current HP in the event resolver, while the repo's own relic layer implements the identical 'gain max HP on pickup' phrase as max_hp AND hp — so the same worded effect pays 7 HP less when it comes from this event.
   - `tier05/content/events.yaml:143 — {label: "Eat the Egg", max_hp: 7}`
   - `tier05/events.py:376-378 — 'if opt.get("max_hp"): st.max_hp = max(1, st.max_hp + opt["max_hp"]); st.hp = min(st.hp, st.max_hp)' (hp only ever follows a LOSS down; a gain never raises hp)`
   - `tier05/relics.py:385-388 — 'if hook == "on_pickup_maxhp": amt = int(fx["amount"]); max_hp += amt; hp += amt'`
   - `tier05/content/events.yaml:13 — grammar comment 'max_hp: +-N move max HP (hp follows a loss down)' documents the asymmetry but does not source it`
   - note: The harvest text is silent on whether a max-HP gain also heals (docs/sts2-events-harvest.txt:57), so the base-game side is inference, not quoted text; the load-bearing evidence is the intra-repo inconsistency between the two surfaces that implement the same phrase. Same code path affects morphic_grove's max_hp: 5 (tier05/content/events.yaml:130), so this is a whole-file pattern, filed once here. If the no-heal reading is intended, the divergence is that relics.py heals, not that events.py does not.

### colossal_flower — 1 finding(s)
*legs read: docs/sts2-events-harvest.txt:83-91; docs/sts2-map-and-events-research.md:231-232,423-424,477-486,530-536; tier05/content/events.yaml:9-43,161-186; tier05/events.py:103-127,239-336,365-392,503-519; tier05/model.py:488-525; tier05/tests/test_events_acts23.py:86-157*
1. **[MEDIUM · sheet_vs_sim_divergence]** The spec grammar (and the run layer) both state that an event HP cost can kill 'that is the real game's rule', but the interpreter refuses any option whose HP cost would reach 0 — so the ladder's rungs silently vanish at low HP instead of being offered, and the run layer's event-death branch is unreachable.
   - `tier05/content/events.yaml:12 — grammar: 'hp: -N   lose N HP (can kill; that is the real game's rule)'`
   - `tier05/content/events.yaml:171 — {label: "Reach Deeper", hp: -5, escalate: colossal_flower_2}`
   - `tier05/events.py:306-310 — '# A lethal option stays legal in the real game; ours refuses ... if st.hp + min(0, opt.get("hp", 0)) <= 0: continue'`
   - `tier05/model.py:513 — 'if hp <= 0:   # an event CAN kill (real rule)' — a branch available() can never produce, since every surviving option leaves hp > 0`
   - note: Concretely: at 5 HP the sim removes 'Reach Deeper' from the level-1 screen entirely (base game offers it and lets it kill), and the same rule at level 3 removes 'Enter the Center' below 8 HP, making Pollinous Core unobtainable on a low-HP run. Root cause is one guard, filed once here rather than repeated on colossal_flower_2/_3. The interpreter documents its own deviation, but the yaml grammar and model.py both assert the opposite, so two of three surfaces are wrong about shipped behavior. All harvested NUMBERS on this ladder are exact: 35/75/135 gold at 5/6/7 HP plus Pollinous Core (harvest:84-91 vs events.yaml:170-185), payouts are alternatives not cumulative, and escalation/hidden wiring is pinned by tier05/tests/test_events_acts23.py:86-97. Separately noted, NOT filed: docs/sts2-map-and-events-research.md:530-533 records that the policy takes 135 gold over Pollinous Core 81/81 times — a valuation finding already owned by the research doc, not a parity divergence.

### colossal_flower_2 — CLEAN
*legs read: docs/sts2-events-harvest.txt:86-88; tier05/content/events.yaml:173-178; tier05/events.py:103-127,288-292,503-519; tier05/tests/test_events_acts23.py:86-97,140-156; review/event-gallery/gallery.md:310-313,325-328; klee-mod (grep: absent, expected)*

### colossal_flower_3 — CLEAN
*legs read: docs/sts2-events-harvest.txt:89-91; tier05/content/events.yaml:180-185; tier05/events.py:283-284,480-487,503-519; tier05/content/relics.yaml:265-278; tier0/engine/relics.py:27,179-196; tier05/tests/test_events_acts23.py:63-84,236-243*

### infested_automaton — CLEAN
*legs read: docs/sts2-events-harvest.txt:207-209; docs/sts2-map-and-events-research.md:234,424; tier05/content/events.yaml:20-21,187-195; tier05/events.py:227-236,270,295-314,411-416; tier05/rewards.py:31-60; tier05/tests/test_events_acts23.py:158-176*

### jungle_maze_adventure — 1 finding(s)
*legs read: docs/sts2-events-harvest.txt:211-213; docs/sts2-map-and-events-research.md:214,264,494; tier05/content/events.yaml:1-50; tier05/events.py:239-292 (option_value); tier05/events.py:295-314 (available); tier05/events.py:365-401 (resolve costs)*
1. **[MEDIUM · semantic_drift]** Solo Quest's 18 HP cost is silently withdrawn instead of being a lethal choice: `available()` drops any option whose hp cost would reach 0, so at hp<=18 the event becomes one-option -- while the run layer's own comment asserts the opposite ("an event CAN kill (real rule)"), making that death branch unreachable.
   - `tier05/content/events.yaml:49 (`{label: "Solo Quest", gold: [135, 165], hp: -18}`)`
   - `tier05/events.py:306-310 ("A lethal option stays legal in the real game; ours refuses" + `if st.hp + min(0, opt.get("hp", 0)) <= 0: continue`)`
   - `tier05/model.py:513 (`if hp <= 0:  # an event CAN kill (real rule)`)`
   - `tier05/events.py:517 (`if not nxt or st.hp <= 0: return` -- also unreachable)`
   - `docs/sts2-events-harvest.txt:212 ([Solo Quest] Gain 135-165 Gold. Lose 18 HP.)`
   - note: The numbers themselves are exact: gold band [135,165]/[35,65] inclusive via rng.randint (events.py:381-383), hp -18 via events.py:374-375, option count 2 -- those match harvest:212-213 and gallery:565-567 exactly. The divergence is availability-only, is deliberate and commented in the interpreter, but is NOT in the doc's stated limitations (docs/sts2-map-and-events-research.md:555-576) and is directly contradicted by model.py:513.

### luminous_choir — 1 finding(s)
*legs read: docs/sts2-events-harvest.txt:215-218; docs/sts2-map-and-events-research.md:215,278,559; tier05/content/events.yaml:14,34,145-150; tier05/events.py:239-314,365-392,472-479; tier0/content/cards/curses.yaml:40-46; review/event-gallery/gallery.md:578-612*
1. **[MEDIUM · semantic_drift]** 'Offer Tribute' is gated at 149 gold — the TOP of the 99-149 payment band — so the sim hides the option for any run holding 99-148 gold, whereas the base event rolls one price in that band and offers it whenever the player can afford that rolled price.
   - `docs/sts2-events-harvest.txt:217 — '[Offer Tribute] Pay 99-149 Gold. Obtain a random Relic.'`
   - `docs/sts2-map-and-events-research.md:215 — 'pay 99–149 gold → random relic'`
   - `tier05/content/events.yaml:149-150 — {label: "Offer Tribute", gold: [-149, -99], relic: true, requires_gold: 149}`
   - `tier05/events.py:298 — 'if opt.get("requires_gold", 0) > st.gold: continue' (gate is checked against the flat 149)`
   - `tier05/events.py:381-383 — the actual price is rolled AFTER the gate: 'lo, hi = opt["gold"]; st.gold = max(0, st.gold + rng.randint(...))', and the max(0,...) clamp already prevents negative gold, so the top-of-band gate is not load-bearing for solvency`
   - note: Player-visible as an availability difference over a 50-gold window: at 120 gold the sim never offers the relic branch, the base game offers it whenever the rolled price is <= 120. The gate value itself is defensible-conservative (it also prevents the discount case where the max(0,...) clamp would let a poorer player buy the relic for less than the rolled price), but it is a divergence from the harvested band and worth an explicit decision rather than a silent constant. Everything else on this event is exact: remove: 2 + curse_spore_mind matches harvest:216, and tier05/events.py:392/407-408 removes before appending the curse so the fresh curse cannot be removed by its own option.

### morphic_grove — 1 finding(s)
*legs read: docs/sts2-events-harvest.txt:219-221; docs/sts2-map-and-events-research.md:216; tier05/content/events.yaml:126-130; tier05/events.py:239-292 (option_value, incl. :257 max_hp*1.2 and :281 transform), :374-406 (resolve: gold_all 379-380, transform 397-406), :376-378 (max_hp); tier05/relics.py:377-401 (_apply_pickup_fx / on_pickup_maxhp); tier05/content/relics.yaml:85,166,247 (on_pickup_maxhp users)*
1. **[MEDIUM · semantic_drift]** 'Loner' (+5 Max HP) raises only the cap and grants no current HP, while the run layer's own max-HP grants heal by the same amount — so the same '+N Max HP' effect is worth 5 fewer HP when it comes from an event than when it comes from a relic.
   - `tier05/content/events.yaml:130 — {label: "Loner", max_hp: 5}`
   - `tier05/events.py:376-378 — max_hp branch only does st.max_hp += amt then st.hp = min(st.hp, st.max_hp); no heal on a POSITIVE amount`
   - `tier05/relics.py:385-388 — on_pickup_maxhp does 'max_hp += amt; hp += amt', the repo's other implementation of gaining max HP (used by tier05/content/relics.yaml:85,166,247)`
   - `tier05/events.py:257 — 'v += opt.get("max_hp", 0) * 1.2  # max HP outlives the heal', i.e. the option policy prices +5 Max HP at 6.0 HP-equivalent on the stated assumption that a heal comes with it`
   - `docs/sts2-events-harvest.txt:221 — '[Loner] Gain 5 Max HP.'`
   - note: The loss direction is right (max-HP costs re-clip current HP, pinned by tier05/tests/test_pin_tier05_economy.py:41-60); only the gain direction is asymmetric. Same code path affects byrdonis_nest's 'Eat the Egg' max_hp: 7 (tier05/content/events.yaml:143), outside this group. The 'Group' option (gold_all + transform 2) matches the harvest exactly.

### reflections — CLEAN
*legs read: docs/sts2-events-harvest.txt:238-240; tier05/content/events.yaml:217,237-247; tier05/events.py:271-280,388-391,407-408,418-442; tier0/content/upgrades.py:54,89-96; tier0/content/cards/curses.yaml:47; tier05/tests/test_events_acts23.py:192-216*

### room_full_of_cheese — 3 finding(s)
*legs read: docs/sts2-events-harvest.txt:247-251 (base text, act tags); docs/sts2-map-and-events-research.md:191,217,430,439-440,458; tier05/content/events.yaml:97-105 (entry), :9-43 (effect grammar); tier05/events.py:239-292 (option_value), :295-314 (available), :357-362 (_random_pool_cards), :365-500 (resolve, esp. 444-454 pick_cards and 470-487 relic grants); tier05/rewards.py:32-57 (character_pool is rarity-keyed); klee-mod/KleeCode/KleeMod.cs:243-257 (CreateForReward blacklist + 'Gorge asks for 8 Commons')*
1. **[HIGH · sim_vs_csharp_divergence]** Gorge offers 8 COMMON cards in the base game and in the C# reference, but the sim draws its 8 offers from the character's entire reward pool (common+uncommon+rare), so the option can hand the run two rares.
   - `docs/sts2-events-harvest.txt:248 — '[Gorge] Choose 2 of 8 random Cards rarity:Common Common 2 cards to add to your Deck.'`
   - `klee-mod/KleeCode/KleeMod.cs:256-257 — 'RoomFullOfCheese.Gorge asks for 8 Commons against her 14 and survives, but only by margin.' (14 = Klee's COMMON count, not her generatable pool)`
   - `tier05/content/events.yaml:101 — {label: "Gorge", pick_cards: {of: 8, take: 2}} carries no rarity filter`
   - `tier05/events.py:446 — offers = _random_pool_cards(rng, st, spec["of"])`
   - `tier05/events.py:357-362 — _random_pool_cards flattens rewards.character_pool(...) across every rarity key`
   - `tier05/rewards.py:32-33 — character_pool returns 'rarity -> character cards eligible as fight rewards', i.e. a common-only slice is expressible and simply is not used`
   - note: pick_cards is documented in the yaml grammar (tier05/content/events.yaml:20) as 'choose N of M random pool cards', so sheet and interpreter agree with each other; the disagreement is against the harvest and the C# reference. option_value (tier05/events.py:265-266) also prices the option at a flat CARD_HP*take=16, independent of the rarity actually offered.
2. **[MEDIUM · sim_vs_csharp_divergence]** The 8 Gorge offers are duplicate-free in the base game (C# blacklists each pick before the next draw); the sim samples with replacement, so the same card can occupy several of the 8 slots and the effective choice narrows.
   - `docs/sts2-events-harvest.txt:249 — '* The 8 cards will not contain any duplicates.'`
   - `klee-mod/KleeCode/KleeMod.cs:248-249 — 'CardFactory.CreateForReward(player, cardCount, options) loops cardCount times against an accumulating blacklist.'`
   - `klee-mod/KleeCode/Diagnostics/KleeSelfCheck.cs:246-248 — 'CreateForReward draws cardCount times, adding each pick to a blacklist that is subtracted from the pool before the next draw.'`
   - `tier05/events.py:362 — return [flat[rng.randrange(len(flat))] for _ in range(n)]  (independent draws, replacement allowed)`
   - `tier05/content/events.yaml:101 — pick_cards: {of: 8, take: 2}`
   - `review/event-gallery/gallery.md:1626 — repo's own open item: 'The no duplicates among the 8 clause is a property of pick_cards {of: 8, take: 2}; confirm the sampler is without-replacement before flavor asserts it to players.' (it is not)`
   - note: The shipped variant text already asserts the property to players: gallery.md:755 'The eight wheels offered are never duplicates', :763 'The eight crocks never repeat', :771 'No two trays hold the same strain'. Same defect also reaches brain_leech's pick_cards {of: 5, take: 1} (not in this group), where it is harmless because take=1.
3. **[MEDIUM · semantic_drift]** Search pays 14 HP for a plain random relic from the run pool instead of the named The Chosen Cheese (+1 Max HP at end of combat), so the option's payout and the policy's valuation of it are both wrong versus the base event.
   - `docs/sts2-events-harvest.txt:250-251 — '[Search] Lose 14 HP. Obtain The Chosen Cheese (relic). * The Chosen Cheese: At the end of combat, gain 1 Max HP.'`
   - `tier05/content/events.yaml:105 — {label: "Search", hp: -14, relic: true}`
   - `tier05/events.py:472-479 — opt['relic'] path rolls roll_relic_reward(...) from the run's relic pool`
   - `tier05/events.py:283 — v += RELIC_HP * int(opt.get('relic') or 0), i.e. the option is valued at a full 20 HP-equivalent relic`
   - `review/event-gallery/gallery.md:757,765,773 — every shipped variant still promises '(The Chosen Cheese): at the end of combat, gain 1 Max HP'`
   - note: DISCLOSED, not silent: flagged in place at tier05/content/events.yaml:102-105, in the skip list at :277-279 and :307-310, in docs/sts2-map-and-events-research.md:439-440 and :458, and in review/event-gallery/gallery.md:749. Recorded here for parity coverage; severity reflects that a random relic is materially stronger than the named one. The 14 HP cost and the also_acts:[2] act tagging (harvest act1/act1-alt/act2, with act1-alt out of scope by tier05/content/events.yaml header and events.py:105-114) are both correct.

### slippery_bridge — 4 finding(s)
*legs read: docs/sts2-events-harvest.txt:264-272; tier05/content/events.yaml:4-7,10-35,162-186,249,257-264; tier05/events.py:58-70,278,288-291,343-354,392-396,503-519; docs/sts2-map-and-events-research.md:202,270*
1. **[HIGH · semantic_drift]** "Hold On" removes a card in the sim — and the drafter's own worst card, targeted — while in the harvested event Hold On removes nothing at all: it only re-randomizes which card the Overcome option is offering, and the event loops back to the same two choices.
   - `docs/sts2-events-harvest.txt:266 ("[Hold On] Lose 3 HP. The card in the above option is randomized.")`
   - `docs/sts2-events-harvest.txt:268 ("Choosing Hold On replaces the listed card with another chosen at random, and the event continues to ask you to choose between these options until you choose Overcome.")`
   - `tier05/content/events.yaml:264 (- {label: "Hold On", hp: -3, remove: 1})`
   - `tier05/events.py:392-393 (for cid in _worst_cards(st, opt.get("remove", 0)): st.deck_ids.remove(cid)) with _worst_cards at tier05/events.py:343-354 (curses first, then the draft valuation's lowest — a targeted removal, not a random one)`
   - `tier05/events.py:516-518 (nxt = opt.get("escalate"); if not nxt ... return — with no escalate key the visit ends after this one resolution)`
   - note: Net effect: the sim sells a fully targeted card removal for a flat 3 HP, an outcome the real event never offers as a single purchase. events.yaml:259-261 documents the substitution openly, but it contradicts the file's own curation rule at events.yaml:4-7 ("an event ships only if every one of its options is expressible with real ops. No option is ever approximated to get an event in"). The valuation encodes the same asymmetry: REMOVE_HP * remove vs REMOVE_HP * remove_random * 0.5 at tier05/events.py:278.
2. **[MEDIUM · missing_leg]** The Hold On loop and its escalating cost (+1 HP per selection) are absent: the sim charges a flat 3 HP once and terminates, even though the `escalate` ladder machinery this exact shape needs already exists and is used by two other events.
   - `docs/sts2-events-harvest.txt:269 ("Each time Hold On is selected, the HP cost increases by 1.")`
   - `docs/sts2-events-harvest.txt:268 ("the event continues to ask you to choose between these options until you choose Overcome")`
   - `tier05/content/events.yaml:262-264 (both options; neither carries `escalate`, and Hold On's cost is the constant hp: -3)`
   - `tier05/content/events.yaml:35 (grammar: "escalate: <id>     after resolving, offer this event again (the ladder)")`
   - `tier05/content/events.yaml:162-186 (colossal_flower / colossal_flower_2 / colossal_flower_3 — the escalating-cost ladder modeled with hidden stages, the precedent this event does not follow)`
   - `tier05/events.py:288-291,516-519 (escalation lookahead and the visit loop that re-enters get_event(nxt))`
   - note: With the ladder absent, the run can never pay 3+4+5... HP to walk toward a chosen card, which is the real event's only economy.
3. **[MEDIUM · semantic_drift]** "Overcome"'s remove_random draws uniformly over the entire deck, so Basic-rarity starters (Strike/Defend) are as likely as anything else; the harvest states the first card offered is never Basic rarity, is drawn only from cards without Eternal, and is never re-offered.
   - `docs/sts2-events-harvest.txt:270-272 ("The card is chosen randomly from all your cards without Eternal." / "The first card chosen will never be Basic rarity (unless all of your cards are Basic). Basic cards can be chosen during rerolls." / "The same card will never be chosen twice ...")`
   - `tier05/content/events.yaml:263 (- {label: "Overcome", remove_random: 1})`
   - `tier05/events.py:394-396 (for _ in range(opt.get("remove_random", 0)): if st.deck_ids: st.deck_ids.pop(rng.randrange(len(st.deck_ids))) — a flat uniform index over the whole deck, with no rarity, Eternal, or already-offered filter)`
   - `tier0/content/cards/ironclad_starter.yaml:6,16,26 (rarity: basic — the starters the real event's first offer excludes)`
   - note: Direction is a buff: an early-act deck is roughly half Basic, so the sim's Overcome frequently hands the player the free Strike/Defend thin that the real event's first offer specifically withholds. Eternal is unimplemented repo-wide (tier0/content/cards/curses.yaml:54 flags it as §10.9 backlog), so that clause is unenforceable rather than mis-implemented.
4. **[LOW · other]** `remove_random` is used by this entry but is missing from the effect grammar the events.yaml header publishes, even though that header claims to enumerate the grammar of tier05/events.py.
   - `tier05/content/events.yaml:9-35 ("# Effect grammar (tier05/events.py):" followed by the full key list — `remove: N` appears at :22, `remove_random` appears nowhere)`
   - `tier05/content/events.yaml:263 (remove_random: 1 — the only use of the key in the whole pool)`
   - `tier05/events.py:64 (OPTION_KEYS includes "remove", "remove_random", so the loader accepts it silently)`
   - note: Documentation drift only; the key is read and interpreted. Flagged because events.py:47-50 makes the reader/allowlist pairing an explicit house rule and this header is the third surface that was supposed to move with it.

### tablet_of_truth — 1 finding(s)
*legs read: docs/sts2-events-harvest.txt:294-303; docs/sts2-map-and-events-research.md:219,265,482-490; tier05/content/events.yaml:1-7,52-61,240-300 (skip list); tier05/events.py:239-292,365-380,428-442,503-519; tier0/content/upgrades.py:54,89-96 (has_upgrade excludes already-upgraded ids); review/event-gallery/gallery.md:959-980,1647-1649,1735*
1. **[LOW · other]** The file's own curation rule says a partial event never ships and every skip lives in the bottom skip list / research doc §3, but Tablet of Truth ships with its stage-5 option dropped and that skip appears ONLY as an inline comment -- it is absent from the bottom skip list and from the research doc's skip/backlog sections.
   - `tier05/content/events.yaml:4-7 ("an event ships only if every one of its options is expressible with real ops. No option is ever approximated to get an event in -- the skipped list is at the bottom of this file and in the research doc §3")`
   - `tier05/content/events.yaml:54-57 (inline "Stage 5 ... is SKIPPED, flagged")`
   - `tier05/content/events.yaml:271-300 (skip list: no Tablet of Truth entry; enumerates Enchant/quest/Divine/relic-hook events only)`
   - `docs/sts2-map-and-events-research.md:219 (§2.2 states stage 5 as real content) and docs/sts2-map-and-events-research.md:439-470 (§3.7.2 skip accounting: no Tablet entry)`
   - note: Doc-consistency only; no player-visible number is wrong. Stage-1 body itself is exact vs harvest:295-296: Smash heal 20 (events.py:494-495, capped at max), Decipher max_hp -3 + upgrade_random 1 + escalate (events.py:376-378, 437-442, 516-519). Every op in the entry is interpreted.

### tablet_of_truth_2 — CLEAN
*legs read: docs/sts2-events-harvest.txt:294-303 (** Stage 2: Lose 6 Max HP. Upgrade a random card.); tier05/content/events.yaml:63-69; tier05/events.py:103-127 (pool_for skips hidden), 288-292 (escalation lookahead), 376-378, 437-442, 503-519*

### tablet_of_truth_3 — CLEAN
*legs read: docs/sts2-events-harvest.txt:299 (** Stage 3: Lose 12 Max HP. Upgrade a random card.); tier05/content/events.yaml:71-77; tier05/events.py:103-127, 288-292, 376-378, 437-442, 503-519*

### tablet_of_truth_4 — 2 finding(s)
*legs read: docs/sts2-events-harvest.txt:294-303; docs/sts2-map-and-events-research.md:219; tier05/content/events.yaml:79-84; tier05/events.py:295-314 (available), 365-380 (resolve max_hp clamp), 437-442, 503-519; review/event-gallery/gallery.md:961 (FLAG), 1735*
1. **[MEDIUM · missing_leg]** The escalation ladder is truncated: harvest gives five stages, the sim's terminal stage 4 has no `escalate`, so stage 5 (lose all-but-1 max HP, upgrade the WHOLE deck) is unreachable content -- an option-count divergence from the harvested event.
   - `docs/sts2-events-harvest.txt:301 ("** Stage 5: Lose [all but 1] Max HP. Upgrade ALL cards in your deck.")`
   - `tier05/content/events.yaml:79-84 (tablet_of_truth_4: Give Up / Decipher max_hp -24 upgrade_random 1, no `escalate`, and no tablet_of_truth_5 entry exists)`
   - `tier05/content/events.yaml:54-57 (the omission, flagged in-file)`
   - `review/event-gallery/gallery.md:1735 ("tier05/content/events.yaml deliberately omits Stage 5 ... the Stage 5 flavor above is written to the harvest but is currently unreachable in the sim")`
   - note: Disclosed, not silent: flagged in yaml and in the gallery. Practical impact is near-zero because the greedy policy stops climbing after rung 2 (docs/sts2-map-and-events-research.md:482-486), but the shipped ladder is 4 rungs where the source has 5. Stage 4's own numbers (-24 max HP, one random upgrade) are exact.
2. **[LOW · semantic_drift]** At max_hp <= 24 the Decipher option is withdrawn entirely rather than clamping, which makes resolve()'s own max(1, ...) floor unreachable for this stage.
   - `tier05/events.py:311-312 (`if st.max_hp + min(0, opt.get("max_hp", 0)) <= 0: continue`)`
   - `tier05/events.py:376-378 (`st.max_hp = max(1, st.max_hp + opt["max_hp"]); st.hp = min(st.hp, st.max_hp)`)`
   - `tier05/content/events.yaml:84 (`max_hp: -24`)`
   - `docs/sts2-events-harvest.txt:300 ("** Stage 4: Lose 24 Max HP.")`
   - note: Same availability-vs-clamp shape as the jungle_maze_adventure lethal guard. Rarely reachable state; filed low. Note the clamp at events.py:378 IS present, so the mutation-audit's HIGH-26 note (review/mutation-audit/blind-spot-report.md:119) describes a surviving mutant, not current behavior -- checked, not a finding.

### the_future_of_potions — 5 finding(s)
*legs read: docs/sts2-events-harvest.txt:310-321; tier05/content/events.yaml:10-35,249,266-271; tier05/events.py:58-70,286-287,295-314,384-385,455-468; tier05/rewards.py:32-70,164-170,197-237; tier0/constants.py:772-773; tier05/content/potions.yaml:1-32*
1. **[HIGH · semantic_drift]** The event's entire mechanic — the inserted potion's rarity determines the rarity of the card reward, and each option is restricted to a card type slice — is dropped: the sim gives one unconstrained 3-offer reward screen no matter which potion is consumed.
   - `docs/sts2-events-harvest.txt:311-316 (Insert Common -> Upgraded Common [Attack/Skill]; Insert Uncommon -> Upgraded Uncommon [Attack/Skill/Power]; Insert Rare -> Upgraded Rare; Insert Event -> Upgraded Rare; Insert Token -> Upgraded Common [Attack/Skill])`
   - `docs/sts2-events-harvest.txt:320-321 ("The rarity of the card reward depends on the rarity of the potion inserted." / "Each option randomly specifies whether it gives an Attack, Skill, or Power card reward.")`
   - `tier05/content/events.yaml:269-270 (- {label: "Insert Potion", spend_potion: true, card_reward: 3, upgraded: true} — no rarity or type key of any kind)`
   - `tier05/events.py:455-468 (screens are built from _random_pool_cards with no rarity or type filter; `upgraded` only maps ids to id+SUFFIX)`
   - `tier05/events.py:384-385 (spend_potion consumes a potion without reading its rarity at all)`
   - `tier05/content/potions.yaml:1,32 (the potion pool DOES carry rarity/tiers, so the coupling is expressible, not blocked)`
   - note: Consequence: inserting a Common potion can return a Rare card and vice versa, so the event's whole risk/reward gradient is flat. Secondary caveat on the same option: `upgraded: true` silently leaves cards with no upgrade path un-upgraded (tier05/events.py:461-463), while harvest:311-316 promises an Upgraded card every time. This also violates the file's own no-approximation curation rule at tier05/content/events.yaml:4-7.
2. **[MEDIUM · semantic_drift]** Which potion is spent is a random pop in the sim; the harvest builds up to three explicit options from the first three potions in the player's slots and lets the player choose which one to insert.
   - `docs/sts2-events-harvest.txt:319 ("The first 3 potions in your potion slots are chosen as options to insert, prioritizing the leftmost potions. This can include multiple potions of the same rarity.")`
   - `tier05/content/events.yaml:269 (a single generic "Insert Potion" option)`
   - `tier05/events.py:384-385 (if opt.get("spend_potion") and st.potions: st.potions.pop(rng.randrange(len(st.potions))) — a uniform random pop over the whole bag, not a chosen or leftmost one)`
   - `tier05/events.py:300-301 (available() only gates on whether ANY potion is held)`
   - note: Option count also collapses: up to 3 insert options in the source become 1. Because the option carries no rarity, the random pop is currently reward-neutral — but it is the same defect as the finding above seen from the cost side, and it makes the choice the real event is built on unavailable to the policy.
3. **[MEDIUM · sheet_vs_sim_divergence]** `card_reward: 3` does not yield "an ordinary reward screen" as the grammar header states: the offers are drawn uniformly from the flattened character pool, ignoring C.RARITY_ODDS, so rares surface at ~16-24% instead of 5%.
   - `tier05/content/events.yaml:16 ("card_reward: N     an ordinary reward screen, N offers, drafter picks")`
   - `tier05/content/events.yaml:269 (card_reward: 3)`
   - `tier05/events.py:457-460 (screens = [opt["card_reward"]] ...; offers = _random_pool_cards(rng, st, width))`
   - `tier05/events.py:357-362 (_random_pool_cards: flat = [c for cs in pool.values() for c in cs]; uniform rng.randrange over flat)`
   - `tier05/rewards.py:164-170,234-237 (the ordinary screen rolls rarity first via _roll_rarity, then picks within pool[rarity])`
   - `tier0/constants.py:773 (RARITY_ODDS = {"common": 0.60, "uncommon": 0.35, "rare": 0.05})`
   - note: Measured: rewards.character_pool gives klee {32/25/14}, furina {23/35/18}, kokomi {27/19/9} — uniform rare fractions 0.197 / 0.237 / 0.164 against the intended 0.05. Compounds the rarity finding above: the reward is not merely uncoupled from the potion, it is systematically richer than any real reward screen.
4. **[LOW · other]** The sim adds a "Leave" option the harvested option list does not contain.
   - `docs/sts2-events-harvest.txt:310-317 (the page's options are the five Insert-<rarity>-Potion branches; no leave/decline option is listed)`
   - `tier05/content/events.yaml:271 (- {label: "Leave"})`
   - `tier05/events.py:295-314 (available() applies no gate to a keyless option, so Leave is always offered)`
   - note: Functionally a safety valve — without it a potion-less run would have no legal option and choose() would return None (tier05/events.py:300-301,329-336) — but it is an option-count change against the authority file and it is not flagged in place the way the other substitutions in this file are.
5. **[LOW · other]** `upgraded` is used by this entry but is missing from the effect grammar the events.yaml header publishes.
   - `tier05/content/events.yaml:9-35 ("# Effect grammar (tier05/events.py):" and the full key list — `upgraded` appears nowhere in it)`
   - `tier05/content/events.yaml:269-270 (card_reward: 3, upgraded: true — the only use of the key in the whole pool)`
   - `tier05/events.py:65 (OPTION_KEYS includes "upgraded", so the loader accepts it silently)`
   - `tier05/events.py:461-463 (the reader that implements it)`
   - note: Documentation drift only; the key is read. Same class as slippery_bridge's remove_random gap, and the same house rule at tier05/events.py:47-50 is what makes the header a surface that was supposed to move with the reader.

### the_trial — 1 finding(s)
*legs read: docs/sts2-events-harvest.txt:346-356; tier05/content/events.yaml:10-35,217-235; tier05/events.py:138-165,357-362,397-410,428-436,455-479; tier05/rewards.py:32-70,164-170,197-237; tier0/constants.py:772-773; tier05/tests/test_events_acts23.py:245-263*
1. **[MEDIUM · sheet_vs_sim_divergence]** Nondescript Guilty's `card_screens: 2` does not produce "an ordinary reward screen" as the grammar header promises: the event resolver draws offers uniformly from the flattened character pool, ignoring C.RARITY_ODDS, so rare offers appear at ~16-24% instead of the 5% a real reward screen rolls.
   - `tier05/content/events.yaml:17 ("card_screens: N    N INDEPENDENT reward screens (\"gain 2 card rewards\")") and events.yaml:16 ("card_reward: N     an ordinary reward screen, N offers, drafter picks")`
   - `tier05/content/events.yaml:234 ({label: "DECIDE: Guilty", curse: curse_doubt, card_screens: 2})`
   - `tier05/events.py:457-460 (screens += [C.REWARD_CARD_OFFERS] * card_screens; offers = _random_pool_cards(rng, st, width))`
   - `tier05/events.py:357-362 (_random_pool_cards flattens pool.values() and picks flat[rng.randrange(len(flat))] — no rarity roll)`
   - `tier05/rewards.py:164-170,234-237 (the real reward screen: rarity = card_rarity or _roll_rarity(rng); pool[rarity])`
   - `tier0/constants.py:773 (RARITY_ODDS = {"common": 0.60, "uncommon": 0.35, "rare": 0.05})`
   - note: Measured pool composition via rewards.character_pool: klee {common 32, uncommon 25, rare 14} -> uniform draw is 19.7% rare; furina 23.7% rare; kokomi 16.4% rare, against the 5% RARITY_ODDS a post-combat screen uses. Engine-wide (same code path serves card_reward and pick_cards), not specific to The Trial, but it is the payout of this option. Everything else in this entity is exact: harvest:349-356 Merchant Guilty (Regret + 2 random Relics) = events.yaml:226 curse_regret/relic: 2; Merchant Innocent (Shame + Upgrade 2) = :227; Noble Guilty (Heal 10) = :230; Noble Innocent (Regret + 300 Gold) = :231 gold [300,300]; Nondescript Innocent (Doubt + Transform 2) = :235. One-of-three variant selection matches harvest:347 and is implemented at events.py:150-165 and pinned at test_events_acts23.py:245-253.

### this_or_that — 1 finding(s)
*legs read: docs/sts2-events-harvest.txt:16-19,358-360; tier05/content/events.yaml:249-255; tier05/events.py:103-127,282-284,374-383,407-408,472-479; tier0/content/cards/curses.yaml:19; docs/sts2-map-and-events-research.md:197-204*
1. **[LOW · other]** The harvest tags this event `[?]` — "the page states no location" — and distinguishes that from the `[all]` tag it gives true all-acts events; the sim files it under `all:`, making it rollable in every act on an inference rather than on the source's own act line.
   - `docs/sts2-events-harvest.txt:358 ("### [?] This or That_") with the tag legend at docs/sts2-events-harvest.txt:16-19 ("`?` means the page states no location")`
   - `docs/sts2-events-harvest.txt:264 ("### [all] Slippery Bridge") and :310 ("### [all] The Future of Potions_") — the harvest does use an explicit `all` tag when the page states it`
   - `tier05/content/events.yaml:249-251 ("# --- all acts ---" / "all:" / "- id: this_or_that")`
   - `tier05/events.py:119-126 (pool_for: everything under the `all` key is appended to every act's pool)`
   - `docs/sts2-map-and-events-research.md:197-204 (§2.1 "All acts" table lists This or That? alongside the genuinely all-acts events)`
   - note: Not a contradiction of a stated act — the wiki page states none — but it is an unstated widening relative to the authority file, and it is the one thing in this entity that is not read straight off the harvest. Outcomes themselves are exact: harvest:359-360 [This] Lose 6 HP / Gain 57 Gold = events.yaml:254 (hp: -6, gold: [57, 57], a degenerate [57,57] band so rng.randint returns exactly 57 at events.py:381-383); [That] Add Clumsy / random Relic = events.yaml:255 (curse: curse_clumsy, curse authored at tier0/content/cards/curses.yaml:19; relic: true -> int() -> exactly one roll at events.py:472-473). The harvest's trailing underscore in "This or That_" is a template-stripping artifact (harvest:22), not a name change.

### unrest_site — CLEAN
*legs read: docs/sts2-events-harvest.txt:393-395; docs/sts2-map-and-events-research.md:222; tier05/content/events.yaml:113-117; tier05/events.py:376-378 (max_hp cost re-clips hp), :470-479 (relic grant), :493-498 (heal_frac resolves last, to full); tier0/content/cards/curses.yaml:32-38 (curse_poor_sleep exists, retain:true); tier05/tests/test_pin_tier05_economy.py:41-60 (max-HP cost pins on this event)*

### wellspring — CLEAN
*legs read: docs/sts2-events-harvest.txt:422-424; docs/sts2-map-and-events-research.md:223; tier05/content/events.yaml:107-111; tier05/events.py:295-314 (available), :365-500 (resolve: remove 392, curse 407-408, potion 488-491); tier0/content/cards/curses.yaml:26-30 (curse_guilty exists); review/event-gallery/gallery.md:1424-1458*

### whispering_hollow — CLEAN
*legs read: docs/sts2-events-harvest.txt:426-428; docs/sts2-map-and-events-research.md:224; tier05/content/events.yaml:119-124; tier05/events.py:295-314 (requires_gold gate, boundary is >, so exactly 50 gold still qualifies), :374-383 (hp then gold), :397-406 (transform), :488-491 (potion, slot-limited); review/event-gallery/gallery.md:1453-1490; klee-mod/ (grep: no WhisperingHollow implementation or reference)*

## companions

### albedo_solar_isotoma — CLEAN
*legs read: docs/mondstadt-companions.yaml:71-72; docs/klee-upgrades.yaml:108; tier0/constants.py:85 (SOLAR_ISOTOMA_BLOCK = 3); tier0/engine/effects.py:352-362 (isotoma check before the hit consumes the aura), :2573-2574 (end-of-turn decrement); tier0/content/upgrades.py:454-474 (duration key); klee-mod/KleeCode/Cards/Generated/AlbedoSolarIsotoma.cs:1-77*

### arlecchino_masque_red_death — 2 finding(s)
*legs read: docs/fontaine-companions.yaml:1-10,120-160; docs/furina-upgrades.yaml:1-6,185-200; tier0/engine/effects.py:498-560 (_op_damage); tier0/engine/effects.py:1243-1252 (_op_heal); tier0/engine/effects.py:2331-2380 (player_turn_start_triggers); tier0/engine/effects.py:2463-2492 (player_turn_end_triggers)*
1. **[HIGH · sim_vs_csharp_divergence]** tier0 still grants a flat +N damage rider on every player Attack while masque_red_death is active — a leftover of the card's RETIRED first design — on top of the ratified Strength ratchet. The C# power grants no damage at all, so every Attack in a deck holding Arlecchino deals 1 more (2 more upgraded) in the sim than in the mod.
   - `tier0/engine/effects.py:546-550 — inside `if card.type == "attack"`: `base += state.player.powers.get("masque_red_death", 0)`, commented 'flat rider on YOUR Attacks'`
   - `klee-mod/KleeCode/Powers/FontainePowers.cs:166-199 — MasqueRedDeathPower implements ONLY AfterPlayerTurnStart (StrengthPower) and BeforeSideTurnEnd (LoseBlock); there is no ModifyDamageAdditive override`
   - `docs/fontaine-companions.yaml:146 — sheet effect note is 'at the start of each turn gain 1 Strength; your Bond of Life eats the first 5 Block you gain each turn' (no damage clause)`
   - `docs/fontaine-companions.yaml:151 — 'REDESIGNED 2026-07-25 [USER], replacing "+4 damage on Attacks; you can no longer be healed"'`
   - `klee-mod/KleeCode/Cards/Generated/ArlecchinoMasqueRedDeath.cs:51 — face text is Strength-per-turn + Bond of Life only`
   - `tier0/engine/effects.py:1243-1252 — _op_heal has NO masque branch any more (the retired design's other half WAS removed here; only the damage rider survived)`
   - note: Measured in-repo: with the power applied, guest_neuvillette_tears (printed 5) deals 6; a second, independent attack also gains +1. No test in tier0/tests/test_fontaine.py:319-380 asserts the damage rider — the four masque tests cover only the Strength ratchet, the Bond deduction, the zero-clamp and the Kokomi Strength->Charge conversion, so the orphaned line is unpinned on both sides. git show d1083cf shows line 550 was introduced together with the now-deleted heal block, confirming it as redesign residue.
2. **[LOW · other]** The generated card face hardcodes the Bond number '5' while the power's own description interpolates CompanionConstants.MasqueBondBlock, so the sheet's claim that the number is a constant 'mirrored C#-side' holds for the power tooltip but not for the card text.
   - `klee-mod/KleeCode/Cards/Generated/ArlecchinoMasqueRedDeath.cs:51 — literal 'consumes the first 5 [gold]Block[/gold]'`
   - `tools/gen_klee_cards.py:507-510 — the emitter template hardcodes 'the first 5 [gold]Block[/gold]'`
   - `klee-mod/KleeCode/Powers/FontainePowers.cs:173-175 — power description uses $"{CompanionConstants.MasqueBondBlock}"`
   - `docs/fontaine-companions.yaml:149 — 'the Bond is the flat MASQUE_BOND_BLOCK constant, mirrored C#-side and parity-lint watched'`
   - note: Cosmetic today (tier0/constants.py:87 and CompanionPowers.cs:30 both read 5); it is a drift hazard only if the constant is ever retuned.

### barbara_melody — 1 finding(s)
*legs read: docs/mondstadt-companions.yaml:26-30; docs/klee-upgrades.yaml:96 (block: +2); tier0/engine/effects.py:615-639 (_op_block), 925-934 (_op_burst_energy); tier0/engine/resources.py:370-397 (gain_burst); tier0/content/characters/klee.yaml:11, furina.yaml:14, kokomi.yaml:25 (burst_max); tier0/content/upgrades.py:165-167, 446-449*
1. **[HIGH · sim_vs_csharp_divergence]** The card's `burst_energy: 4` rider fires for ANY character with a Burst meter in tier0, but the generated C# routes it through KleeBurstResource.Gain, which no-ops unless the owner's character is Klee. A Furina or Kokomi player who takes Barbara — Soothing Melody from the companion reward slot gains 0 Burst Energy while the printed card text still promises 'Gain 4 [gold]Burst Energy[/gold]'.
   - `docs/mondstadt-companions.yaml:29 — effects: [{op: block, amount: 6}, {op: burst_energy, amount: 4}]`
   - `tier0/engine/effects.py:925-926 — `def _op_burst_energy(...)` / `if state.player.burst_max:` — the only gate is owning a meter, not being Klee`
   - `tier0/content/characters/furina.yaml:14 — `burst_max: 70`; tier0/content/characters/kokomi.yaml:25 — `burst_max: 20` (both non-zero, so both pass the tier0 gate)`
   - `klee-mod/KleeCode/Cards/Generated/BarbaraMelody.cs:73 — `await KleeBurstResource.Gain(choiceContext, Owner.Creature, 4, this);``
   - `klee-mod/KleeCode/Powers/BurstResource.cs:181 — `if (owner?.Character is not Klee) return null;` inside `Find`, and BurstResource.cs:206-208 — `var resource = Find(player); if (resource == null) return Task.CompletedTask;``
   - `klee-mod/KleeCode/Cards/Generated/BarbaraMelody.cs:51 — ("description", "Gain {CalculatedBlock:diff()} [gold]Block[/gold]. Gain 4 [gold]Burst Energy[/gold].")`
   - note: Verified empirically against the interpreter: building the tier0 player for klee/furina/kokomi and resolving barbara_melody yields burst_energy 4 in all three cases (burst_max 40/70/20). The C# leg is the one that diverges. Root cause is the codegen emitter, not this card, so it is shared with sucrose_astable (and, off-group, bennett_passion / combustion_study / study_of_explosions and the other burst_energy rows). Filed as sim_vs_csharp_divergence rather than text_ops_mismatch because the text is right on the Klee leg and only the non-Klee runtime contradicts it; the misleading-text symptom is a consequence of the same defect. Sheet↔C# value parity itself is machine-clean (`python3 tools/gen_klee_cards.py --check --character all` reports "up to date"), and the block half (6, +2 on upgrade) agrees across all three legs.

### barbara_shining_idol — CLEAN
*legs read: docs/mondstadt-companions.yaml:31-33; docs/klee-upgrades.yaml:97 (block: +2; cantrip + aura untouched); tier0/engine/effects.py:615-639 (_op_block), 874-880 (_op_apply_aura), 652-666 (_op_draw); tier0/content/upgrades.py:165-167, 206-214 (draw dispatch — not triggered here); klee-mod/KleeCode/Cards/Generated/BarbaraShiningIdol.cs:34-98; klee-mod/KleeCode/Powers/ElementalHit.cs:59-87*

### bennett_fantastic_voyage — 1 finding(s)
*legs read: docs/mondstadt-companions.yaml:59-64; docs/klee-upgrades.yaml:104; tier0/engine/effects.py:802-872 (_op_apply_power), :2287-2325, :2570-2575; tier0/content/upgrades.py:454-474; klee-mod/KleeCode/Cards/Generated/BennettFantasticVoyage.cs:1-80; klee-mod/KleeCode/Powers/CompanionPowers.cs:366-399 (AttackUpThisTurnPower)*
1. **[LOW · semantic_drift]** AttackUpThisTurnPower is titled and documented as Bennett's "Fantastic Voyage" (a this-turn attack buff), but bennett_fantastic_voyage grants permanent Strength in both the sheet and the generated card; no content on either side applies attack_up_this_turn.
   - `klee-mod/KleeCode/Powers/CompanionPowers.cs:368-377 ("/// Bennett burst (Fantastic Voyage): attacks +Amount for the REST OF THIS TURN" and Localization title "Fantastic Voyage", description "Your Attacks deal {Amount} more damage this turn.")`
   - `klee-mod/KleeCode/Cards/Generated/BennettFantasticVoyage.cs:73 (PowerCmd.Apply<StrengthPower>(... DynamicVars["PowerAmount"].IntValue ...))`
   - `docs/mondstadt-companions.yaml:61 (effects: [{op: apply_power, power: strength, amount: 3, target: self}])`
   - `tier0/engine/effects.py:2575 (p.powers.pop("attack_up_this_turn", None)   # Bennett burst)`
   - note: Naming/comment drift only: the power is unreachable (no card or sheet row emits attack_up_this_turn), so no player-visible number moves. The mechanics leg itself (Strength 3, +1 on upgrade, Exhaust, cost 1, Uncommon) matches across sheet/sim/C#.

### bennett_passion — CLEAN
*legs read: docs/mondstadt-companions.yaml:57-58; docs/klee-upgrades.yaml:103; tier0/engine/effects.py:925-958 (_op_burst_energy, _op_buff_next_attack), :2235-2262 (next_attack_up pop in resolve_card), :2287-2325 (flat_attack_bonus); tier0/content/upgrades.py:454-474 (buff key binds first top-level apply_power/buff_next_attack); klee-mod/KleeCode/Cards/Generated/BennettPassion.cs:1-78; klee-mod/KleeCode/Powers/CompanionPowers.cs:400-455 (NextAttackUpPower)*

### charlotte_enduring_frosthelm — 1 finding(s)
*legs read: docs/fontaine-companions.yaml:1-8,33-45; docs/furina-upgrades.yaml:164-176; klee-mod/KleeCode/Cards/Generated/CharlotteEnduringFrosthelm.cs:1-80; klee-mod/KleeCode/Powers/CompanionPowers.cs:459-470; tier0/engine/effects.py:615-650,2331-2352; tier0/content/upgrades.py:165-167,419-425*
1. **[MEDIUM · text_ops_mismatch]** The card face prints the next-turn Block as a hard literal ('gain 4 Block') while the amount actually banked is Spotlight-scaled, so a Guest-Cast-Spotlighted Frosthelm grants 6 next-turn Block while its own text still says 4 — on the same card whose first Block number DOES scale on the face.
   - `klee-mod/KleeCode/Cards/Generated/CharlotteEnduringFrosthelm.cs:51`
   - `klee-mod/KleeCode/Cards/Generated/CharlotteEnduringFrosthelm.cs:73`
   - `klee-mod/KleeCode/Cards/Generated/CharlotteEnduringFrosthelm.cs:59`
   - `tools/gen_klee_cards.py:3546`
   - `tools/gen_klee_cards.py:3908`
   - `tier0/engine/effects.py:645`
   - note: Value parity is fine: tier0 _op_block_next_turn spotlight-scales the banked amount (effects.py:649) and C# banks SpotlightSystem.PrintedBlock(this, 4) (line 73), so both grant int(4*1.5)=6 under Guest Cast. Only the printed string is static. Internal evidence that this is a defect rather than convention: the first Block on the same card renders through CalculatedBlockVar().WithMultiplier(PrintedBlockDelta) (line 59) and therefore does scale on the face. The codegen comment at gen_klee_cards.py:3906-3907 justifies the literal only by the upgrade binding ('the block delta binds to the plain block op'), never by Spotlight. Non-findings checked and clean: cost 1 / Skill / Common / Self and star=4, nation=fontaine, PersonalPool=null (yaml:37 vs .cs:38-44,66); base 4 + 4 split (yaml:38 vs .cs:57,73); upgrade block +2 moving ONLY the first block op (furina-upgrades.yaml:172, upgrades.py:165-167 _bump_first over `block` ops, vs .cs:78 CalculationBase +2 with the next-turn literal untouched); next-turn payout landing after the turn-start block reset with no carry-over (effects.py:2344-2351 pop vs CompanionPowers.cs:460-466 BlockNextTurnPower/AfterBlockCleared); raw (Frail/Dexterity-exempt) payout on both sides (effects.py:2346-2350 vs the Unpowered note at CompanionPowers.cs:466); starter-slot membership matching (tier0/content/characters/furina.yaml:85 vs KleeStartingCompanions.cs:82).

### charlotte_freezing_point — CLEAN
*legs read: docs/fontaine-companions.yaml:34-36; docs/furina-upgrades.yaml:171; tier0/engine/effects.py:498-613 (_op_damage), :652-665 (_op_draw), :264-287 (_element_for); tier0/content/upgrades.py:158-164; klee-mod/KleeCode/Cards/Generated/CharlotteFreezingPoint.cs:1-97; klee-mod/KleeCode/Cards/Generated/CompanionRoster.cs:31*

### charlotte_snappy_silhouette — CLEAN
*legs read: docs/fontaine-companions.yaml:43-45; docs/furina-upgrades.yaml:173; klee-mod/KleeCode/Cards/Generated/CharlotteSnappySilhouette.cs:1-80; tier0/engine/effects.py:802-871,652-665; tier0/content/upgrades.py:450-453; tier0/engine/powers.py:57-72,153-179*

### chevreuse_bursting_grenades — CLEAN
*legs read: docs/fontaine-companions.yaml:17-19; docs/furina-upgrades.yaml:167; tier0/engine/effects.py:498-613 (_op_damage, target all_enemies), :244-263 (_pick_targets); tier0/content/upgrades.py:158-164; klee-mod/KleeCode/Cards/Generated/ChevreuseBurstingGrenades.cs:1-94; klee-mod/KleeCode/Cards/Generated/CompanionRoster.cs:33*

### chevreuse_interdiction_fire — CLEAN
*legs read: docs/fontaine-companions.yaml:10-12; docs/furina-upgrades.yaml:165; tier0/engine/effects.py:264-300 (_element_for), :498-613 (_op_damage), :351-430 (deal_damage_to_enemy); tier0/content/upgrades.py:158-164 ('damage' key); tier0/content/characters/furina.yaml:84; klee-mod/KleeCode/Cards/Generated/ChevreuseInterdictionFire.cs:1-94*

### chevreuse_vanguards_valor — CLEAN
*legs read: docs/fontaine-companions.yaml:13-16; docs/furina-upgrades.yaml:166; tier0/engine/effects.py:955-957 (_op_buff_next_attack), :1510-1520 (_op_conditional), :1596-1599 (reaction_triggered_this_turn), :2245-2270 + :2287-2326 (next_attack_up pop / flat_attack_bonus); tier0/engine/combat.py:425-445 (reactions_this_turn reset before start-of-turn bomb detonation); tier0/engine/reactions.py:130-142; tier0/content/upgrades.py:454-474 ('buff' key)*

### clorinde_impale_the_night — 1 finding(s)
*legs read: docs/fontaine-companions.yaml:103-126; docs/furina-upgrades.yaml:180-188; klee-mod/KleeCode/Cards/Generated/ClorindeImpaleTheNight.cs:1-95; klee-mod/KleeCode/Powers/FontainePowers.cs:71-108; klee-mod/KleeCode/Powers/CompanionPowers.cs:279-322; tier0/engine/effects.py:351-363,498-612,802-850*
1. **[LOW · semantic_drift]** The sheet documents night_vigil as sharing 'the same hook in deal_damage_to_enemy' with Albedo's solar_isotoma, but in the sim the two live in different functions: solar_isotoma is checked inside deal_damage_to_enemy while night_vigil is added in _op_damage before the call.
   - `docs/fontaine-companions.yaml:120`
   - `tier0/engine/effects.py:358`
   - `tier0/engine/effects.py:604`
   - `tier0/engine/effects.py:605`
   - note: Comment/design-note drift only — there is no behavioural difference today, because the only call site that passes source="attack" into deal_damage_to_enemy is _op_damage itself (effects.py:500,611; chain_attack routes through _op_damage at effects.py:1834-1841), so the two predicates cover exactly the same hits. Filed low because the note is the thing a future reader would trust when adding a third attack-damage path: a new op that calls deal_damage_to_enemy with source="attack" directly would pick up Albedo's Block and silently miss Clorinde's damage. Non-findings checked and clean: cost 2 / Attack / Rare / AnyEnemy, star 5, electro, fontaine (yaml:103 vs .cs:38-48,76); 20 damage + night_vigil 6 self (yaml:104-105 vs .cs:67,88); applies_element true wired as IElementalCard + AppliesElectro keyword + hover tip (.cs:34,37,50-54) against _element_for's explicit-flag branch (effects.py:276-277); the rider read BEFORE the hit consumes the aura it keys on, on both sides (effects.py:598-605 ahead of deal_damage_to_enemy vs the ModifyDamageAdditive-before-AuraPower.AfterDamageReceived ordering at FontainePowers.cs:80-82,98-107 and AuraPower.cs:128-157); 'your Attacks' meaning card Attacks only, so bombs/summon pulses do not collect it (effects.py:604 `card.type == "attack"` vs the cardSource/IsPoweredAttack pair at FontainePowers.cs:103-104, pinned at test_fontaine.py:279-287); Clorinde's own body not boosted by her own power (effect order in yaml:104-105 vs OnPlay order .cs:83-88); upgrade damage +3 -> 23 with the +6 rider deliberately static (furina-upgrades.yaml:180-188, upgrades.py:158-164, vs .cs:88,93); flat-before-multiplicative placement matching (effects.py:605 into `base` ahead of powers.modify_damage_dealt/vulnerable vs the additive phase in C#).

### dahlia_favonian_favor — CLEAN
*legs read: docs/mondstadt-companions.yaml:20-21; docs/klee-upgrades.yaml:93 (block: +2); tier0/engine/effects.py:615-639 (_op_block), 874-880 (_op_apply_aura), 244-262 (_pick_targets random_enemy); tier0/engine/reactions.py:51-88; tier0/content/upgrades.py:165-167; klee-mod/KleeCode/Cards/Generated/DahliaFavonianFavor.cs:34-96*

### dahlia_sacramental_shower — CLEAN
*legs read: docs/mondstadt-companions.yaml:1-19 (header rules + row); docs/klee-upgrades.yaml:92 (damage: +2); tier0/engine/effects.py:498-614 (_op_damage), 264-290 (_element_for), 351-430 (deal_damage_to_enemy), 232-262 (_pick_targets), 321-350 (spotlight scaling); tier0/engine/reactions.py:22, 51-88 (apply_aura/resolve_hit); tier0/content/upgrades.py:115-167 (damage/block dispatch); tier0/content/loader.py:100-140, 200-250, 288-315 (nation/character derivation, reaction-fuel, pools)*

### diona_icy_paws — CLEAN
*legs read: docs/mondstadt-companions.yaml:67-68; docs/klee-upgrades.yaml:106; tier0/engine/effects.py:244-261, :615-639 (_op_block), :874-880 (_op_apply_aura); tier0/engine/reactions.py:70-95 (resolve_hit); tier0/content/upgrades.py:165-167 (block key); klee-mod/KleeCode/Cards/Generated/DionaIcyPaws.cs:1-97*

### durin_witchs_flame — 3 finding(s)
*legs read: docs/mondstadt-companions.yaml:1-16 (header), :73-74; docs/klee-upgrades.yaml:109; tier0/constants.py:84 (WITCHS_FLAME_BURST = 3); tier0/engine/effects.py:352-380 (deal_damage_to_enemy pipeline), :2556-2572 (witchs_flame end-of-turn block); tier0/engine/powers.py:42-72 (modify_damage_dealt / modify_damage_taken); tier0/content/upgrades.py:15-22, 56-72, 454-474*
1. **[HIGH · sim_vs_csharp_divergence]** The per-consumed-aura ping runs the full sim damage pipeline in tier0 (Strength added, Weak x0.75, Vulnerable x1.5) but is dealt as a raw, unmodified Unpowered hit with dealer:null in the mod, so the two sides print different damage whenever the player has Strength/Weak or the target is Vulnerable.
   - `tier0/engine/effects.py:2565-2568 (deal_damage_to_enemy(state, enemy, damage, element=None, source="companion"))`
   - `tier0/engine/effects.py:361-368 (deal_damage_to_enemy: dmg = powers.modify_damage_dealt(state.player, base) ... dmg = powers.modify_damage_taken(enemy, dmg, from_card=...))`
   - `tier0/engine/powers.py:42-54 (modify_damage_dealt: base + strength, then WEAK_DEALT_MULT)`
   - `klee-mod/KleeCode/Powers/CompanionPowers.cs:269-272 (await CreatureCmd.Damage(choiceContext, target, (int)Amount, ValueProp.Unpowered, dealer: null, cardSource: null) -- Amount used raw, no SimDamagePipeline call)`
   - `klee-mod/KleeCode/Powers/SimDamagePipeline.cs:8-42 (the mod's own doctrine: "tier0 deal_damage_to_enemy runs EVERY hit through modify_damage_dealt ... so the modifiers the sim DOES apply to these hits must be mirrored here explicitly")`
   - `klee-mod/KleeCode/Powers/ElementalHit.cs:31, 54-56 (the sibling non-attack sources -- bombs, the Burst volley, Oz -- do route through SimDamagePipeline.DealerMods/TargetMods)`
   - note: Concrete case: Durin base 6, player at Strength 3 (trivially reachable -- bennett_fantastic_voyage grants 3, nicole_celestial_gift ratchets Strength every turn), target Vulnerable. Sim deals int((6+3)*1.5) = 13 per consumed Pyro aura; the mod deals 6. tier0/tests/test_klee.py:185-200 only exercises the zero-Strength case, so nothing pins the difference.
2. **[MEDIUM · sheet_vs_sim_divergence]** The companion sheet header names durin_witchs_flame as a member of the sim's UNAPPLIABLE set and states it does not upgrade, but the sim's UNAPPLIABLE set is empty, the upgrade sheet carries a delta, and the sim and the mod both upgrade the card.
   - `docs/mondstadt-companions.yaml:10-12 ("The only companions that still do not upgrade are the sim's own UNAPPLIABLE set (durin_witchs_flame, nicole_celestial_gift), which is a per-card fact, not a pool law.")`
   - `tier0/content/upgrades.py:72 (UNAPPLIABLE: frozenset[str] = frozenset())`
   - `docs/klee-upgrades.yaml:109 (durin_witchs_flame: {power_amount: +2}   # consumed-Pyro damage 6->8)`
   - `tier0/tests/test_upgrades.py:71-72 (loader.get_card("durin_witchs_flame+") ... assert durin.effects[0]["amount"] == 8)`
   - `klee-mod/KleeCode/Cards/Generated/DurinWitchsFlame.cs:73-76 (protected override void OnUpgrade() { DynamicVars["PowerAmount"].UpgradeValueBy(2m); })`
   - note: The sheet header is stamped G2 2026-07-26 and reads as current pool law, so a reader takes the no-upgrade claim as live; all three implementation surfaces contradict it (manifest.json's upgrades.no_upgrade_path is also empty).
3. **[LOW · other]** tier0/content/upgrades.py's module docstring still describes UNAPPLIABLE as listing Durin's ping among constants-encoded deltas the DSL cannot express, while the same module defines the set as empty and the applier expresses Durin's delta through the power_amount/duration/buff branch.
   - `tier0/content/upgrades.py:15-22 ("UNAPPLIABLE lists the sheet entries whose deltas target numbers the engine encodes as CONSTANTS ... Durin's ping ... Those upgrades exist in the design and cannot yet be expressed per-card in the Tier 0 DSL.")`
   - `tier0/content/upgrades.py:72 (UNAPPLIABLE: frozenset[str] = frozenset())`
   - `tier0/content/upgrades.py:454-474 (the power_amount branch that does express it)`
   - note: Comment drift inside one module; no behavioural effect.

### fischl_nightrider — CLEAN
*legs read: docs/mondstadt-companions.yaml:22-23; docs/klee-upgrades.yaml:94 (damage: +2); tier0/engine/effects.py:498-614, 264-290, 351-430; tier0/content/upgrades.py:158-164; klee-mod/KleeCode/Cards/Generated/FischlNightrider.cs:34-93; klee-mod/KleeCode/Powers/ElementalApplication.cs:180-205*

### fischl_oz — CLEAN
*legs read: docs/mondstadt-companions.yaml:24-25; docs/klee-upgrades.yaml:95 (duration: +1); tier0/engine/effects.py:802-872 (_op_apply_power), 2501-2506 (oz_summon end-of-turn tick); tier0/constants.py:83 (OZ_DMG = 3); tier0/engine/refpowers.py:325-340 (power cards leave combat, not exhaust); tier0/content/upgrades.py:454-474 (duration/power_amount dispatch)*

### freminet_pers_deploy — CLEAN
*legs read: docs/fontaine-companions.yaml:47-52; docs/furina-upgrades.yaml:174; klee-mod/KleeCode/Cards/Generated/FreminetPersDeploy.cs:1-94; tier0/engine/effects.py:264-287,351-430,498-612; tier0/content/upgrades.py:158-164; tier0/content/characters/furina.yaml:84-85*

### freminet_pressurized_floe — 1 finding(s)
*legs read: docs/fontaine-companions.yaml:53-57; docs/furina-upgrades.yaml:175; klee-mod/KleeCode/Cards/Generated/FreminetPressurizedFloe.cs:1-86; tier0/engine/effects.py:264-287,351-430,615-637; tier0/engine/powers.py:75-116; klee-mod/KleeCode/Powers/FrozenPower.cs:56-106*
1. **[MEDIUM · text_ops_mismatch]** The Block half of the face renders an unscaled BlockVar(6) while OnPlay grants SpotlightSystem.PrintedBlock(this, 6), so a Spotlighted Backstroke gives 9 Block behind a face that still reads 6 — next to a damage number on the same card that does scale.
   - `klee-mod/KleeCode/Cards/Generated/FreminetPressurizedFloe.cs:51`
   - `klee-mod/KleeCode/Cards/Generated/FreminetPressurizedFloe.cs:60`
   - `klee-mod/KleeCode/Cards/Generated/FreminetPressurizedFloe.cs:79`
   - `klee-mod/KleeCode/Cards/Generated/FreminetPressurizedFloe.cs:59`
   - `tools/gen_klee_cards.py:1827`
   - `tools/gen_klee_cards.py:1830`
   - note: Value parity holds — tier0 _op_block spotlight-scales the printed Block (effects.py:631) and the C# OnPlay wraps the same base in PrintedBlock (line 79) — so this is a face-vs-effect drift, not a wrong grant. Root cause is structural and already half-acknowledged in the generator: spotlight_block_rider excludes a card whose damage already claims the single CalculationBase var and names freminet_pressurized_floe as 'the only one' (gen_klee_cards.py:1827-1830), but that note stops at 'its damage conversion wins' and does not record that the Block face is then left unscaled while the grant is not. The card is a companion, so Guest Cast Spotlight (x1.5, constants.py:91) is reachable. Non-findings checked and clean: cost 2 / Attack / Common / AnyEnemy, star 4, cryo, fontaine (yaml:53 vs .cs:38-44,67); 10 damage + 6 Block (yaml:54 vs .cs:57,60); applies_element:false honoured by the absence of IElementalCard/AppliesCryo on the C# class and by _element_for's explicit-flag branch (effects.py:276-277 vs .cs:33 — no IElementalCard, contrast FreminetPersDeploy.cs:34), pinned sim-side at test_fontaine.py:213-220; upgrade damage +2 hitting only the damage op and leaving Block at 6 (furina-upgrades.yaml:175, upgrades.py:158-164, vs .cs:84); Shatter cashing gated on attack-card source and on the enemy surviving, unblockable and unamplified on both sides (effects.py:385-403 vs FrozenPower.cs:80-105); Frail applying to this Block on both sides (powers.modify_block_gained at effects.py:633 vs ValueProp.Move at .cs:79).

### freminet_shattering_pressure — CLEAN
*legs read: docs/fontaine-companions.yaml:58-62; docs/furina-upgrades.yaml:176; klee-mod/KleeCode/Cards/Generated/FreminetShatteringPressure.cs:1-77; klee-mod/KleeCode/Powers/CompanionPowers.cs:471-495; klee-mod/KleeCode/Powers/FrozenPower.cs:56-106; tier0/engine/effects.py:385-403,802-850*

### gorou_heart_of_the_clan — CLEAN
*legs read: docs/inazuma-companions.yaml:30-32; docs/kokomi-upgrades.yaml:148; tier0/engine/effects.py:615-639 (_op_block), 802-873 (_op_apply_power); tier0/engine/powers.py:118-137 (on_turn_start metallicize), 153-179 (apply_power); tier0/content/upgrades.py:452-476; klee-mod/KleeCode/Cards/Generated/GorouHeartOfTheClan.cs:1-81*

### gorou_inuzaka_charge — 1 finding(s)
*legs read: docs/inazuma-companions.yaml:1-33; docs/kokomi-upgrades.yaml:144-146; tier0/engine/effects.py:264-290 (_element_for), 498-614 (_op_damage); tier0/content/loader.py:200-245; tier0/content/upgrades.py:400-500; tier0/content/characters/kokomi.yaml:80-110*
1. **[LOW · sheet_vs_sim_divergence]** The sheet comment labels this card a randomized_starter slot card, but the interpreter's character spec puts it in the authored starting deck and its randomized_starter block covers only the support slot.
   - `docs/inazuma-companions.yaml:26 — 'Starter attack-slot card (randomized_starter).'`
   - `tier0/content/characters/kokomi.yaml:89 — gorou_inuzaka_charge is listed literally in `starting_deck``
   - `tier0/content/characters/kokomi.yaml:103-104 — `randomized_starter:` contains only `support: {replace: sayu_daruma_gift, choices: [...]}``
   - `tier0/content/characters/kokomi.yaml:99-101 — 'so Gorou sits in the authored list directly (he was always the only attack-slot choice)'`
   - note: Comment drift only; no behavioural difference. Card body is parity-clean: 0 cost / Common / Attack / 6 damage / Exhaust / no element application (docs/inazuma-companions.yaml:23-24 vs GorouInuzakaCharge.cs:38,46-47,60,69 and tier0 loader dump exh=True, applies_element False, archetypes []). Upgrade agrees: docs/kokomi-upgrades.yaml:145 {damage:+3} -> tier0 6->9, GorouInuzakaCharge.cs:85 CalculationBase.UpgradeValueBy(3m).

### gorou_war_banner — CLEAN
*legs read: docs/inazuma-companions.yaml:27-29; docs/kokomi-upgrades.yaml:147; tier0/engine/effects.py:615-639 (_op_block), 955-957 (_op_buff_next_attack), 2287-2330 (flat_attack_bonus), 2244-2256 (next_attack_up pop); tier0/content/upgrades.py:452-476 (buff/power_amount key); klee-mod/KleeCode/Cards/Generated/GorouWarBanner.cs:1-81; klee-mod/KleeCode/Powers/CompanionPowers.cs:410-455 (NextAttackUpPower)*

### guest_neuvillette_droplets — 1 finding(s)
*legs read: docs/fontaine-companions.yaml:196-209; docs/mondstadt-companions.yaml:67-68 (Diona parity claim); tier0/engine/effects.py:244-262 (_pick_targets), 615-640 (_op_block), 874-881 (_op_apply_aura); tier0/engine/powers.py:75-116 (modify_block_gained); tier0/content/loader.py:107-145,200-300; tier05/rewards.py:70-100*
1. **[LOW · other]** The generated file's provenance header names the wrong source sheet (and the wrong upgrade sheet), and its 'Flagged in manifest' claim is not backed by the manifest.
   - `klee-mod/KleeCode/Cards/Furina/Generated/GuestNeuvilletteDroplets.cs:2 — 'Generated by tools/gen_roster_cards.py from docs/furina-cards.yaml'`
   - `docs/fontaine-companions.yaml:206 — the guest_neuvillette_droplets row lives in the Fontaine companions sheet`
   - `klee-mod/KleeCode/Cards/Furina/Generated/GuestStarRoster.cs:2 — sibling roster header correctly names docs/fontaine-companions.yaml`
   - `klee-mod/KleeCode/Cards/Furina/Generated/GuestNeuvilletteDroplets.cs:95 — 'no ratified delta in klee-upgrades.yaml. Flagged in manifest.'`
   - `docs/furina-upgrades.yaml:3 — Guest Stars are excluded by furina-upgrades.yaml, the authority for this card`
   - `klee-mod/KleeCode/Cards/Furina/Generated/manifest.json:110-112 — upgrades.no_upgrade_path is {}`
   - note: Mechanics agree: block 4 then a random-enemy Hydro application, in that order, on both sides (docs/fontaine-companions.yaml:207 vs GuestNeuvilletteDroplets.cs:79-90 and tier0/engine/effects.py:615-639 + 874-880). Shape is byte-for-byte the Diona precedent (DionaIcyPaws.cs:76-90, TargetType.AllEnemies included), and the sheet's 'Diona Icy Paws parity minus 1 block' claim checks out (docs/mondstadt-companions.yaml:68 = 5 block).

### guest_neuvillette_judgment — 1 finding(s)
*legs read: docs/fontaine-companions.yaml:196-220; docs/fontaine-companions.yaml:10-20 (Chevreuse bursting_grenades comparison); tier0/engine/effects.py:498-512 (self-damage branch), 244-262 (_pick_targets); tier0/engine/resources.py:399-407 (note_player_hp_loss); tier0/content/loader.py:286-300; tier05/rewards.py:70-100*
1. **[LOW · other]** The generated file's provenance header names the wrong source sheet (and the wrong upgrade sheet), and its 'Flagged in manifest' claim is not backed by the manifest.
   - `klee-mod/KleeCode/Cards/Furina/Generated/GuestNeuvilletteJudgment.cs:2 — 'Generated by tools/gen_roster_cards.py from docs/furina-cards.yaml'`
   - `docs/fontaine-companions.yaml:210 — the guest_neuvillette_judgment row lives in the Fontaine companions sheet`
   - `klee-mod/KleeCode/Cards/Furina/Generated/GuestStarRoster.cs:2 — sibling roster header correctly names docs/fontaine-companions.yaml`
   - `klee-mod/KleeCode/Cards/Furina/Generated/GuestNeuvilletteJudgment.cs:94 — 'no ratified delta in klee-upgrades.yaml. Flagged in manifest.'`
   - `docs/furina-upgrades.yaml:3 — Guest Stars excluded by furina-upgrades.yaml`
   - `klee-mod/KleeCode/Cards/Furina/Generated/manifest.json:110-112 — upgrades.no_upgrade_path is {}`
   - note: Numbers and ordering agree: 3 self HP loss BEFORE the 7-damage Hydro AoE on both sides (docs/fontaine-companions.yaml:211 vs GuestNeuvilletteJudgment.cs:83-89 vs tier0/engine/effects.py:502-506). The HP cost is block-bypassing and Encore-bypassing in tier0 (raw `state.player.hp -=`) and Unblockable|Unpowered in C#, and both mint Fanfare from it (tier0/engine/resources.py:399-407 vs klee-mod/KleeCode/Powers/FurinaResources.cs:983-1000), matching the sheet's 'Fanfare flux BY DESIGN' note at docs/fontaine-companions.yaml:214.

### guest_neuvillette_tears — 1 finding(s)
*legs read: docs/fontaine-companions.yaml:196-205; docs/furina-upgrades.yaml:1-6; docs/mondstadt-companions.yaml:22-23 (Fischl Nightrider parity claim); tier0/engine/effects.py:264-290 (_element_for), 498-614 (_op_damage); tier0/content/loader.py:200-300, 286-300 (guest_star_generation_pool); tier05/rewards.py:70-100*
1. **[LOW · other]** The generated file's provenance header names the wrong source sheet (and the wrong upgrade sheet), and its 'Flagged in manifest' claim is not backed by the manifest.
   - `klee-mod/KleeCode/Cards/Furina/Generated/GuestNeuvilletteTears.cs:2 — 'Generated by tools/gen_roster_cards.py from docs/furina-cards.yaml'`
   - `docs/fontaine-companions.yaml:203 — the guest_neuvillette_tears row actually lives in the Fontaine companions sheet, which is where tools/gen_klee_cards.py:5348-5358 reads it from`
   - `klee-mod/KleeCode/Cards/Furina/Generated/GuestStarRoster.cs:2 — the sibling roster header correctly names docs/fontaine-companions.yaml`
   - `klee-mod/KleeCode/Cards/Furina/Generated/GuestNeuvilletteTears.cs:92 — 'R24: NO upgrade path -- no ratified delta in klee-upgrades.yaml. Flagged in manifest.'`
   - `docs/furina-upgrades.yaml:3 — the authority for this card is furina-upgrades.yaml ('Guest Stars excluded'), not klee-upgrades.yaml`
   - `klee-mod/KleeCode/Cards/Furina/Generated/manifest.json:110-112 — the 'upgrades' block's no_upgrade_path is {} (empty), so nothing is in fact flagged there`
   - note: Behaviourally clean otherwise: 1 cost / Common / Attack / 5 damage / applies Hydro matches docs/fontaine-companions.yaml:203-204 and tier0 (loader dump: damage 5, applies_element True); no upgrade exists on either side, which is correct per docs/furina-upgrades.yaml:3-4. The 'Fischl Nightrider parity' comment checks out (docs/mondstadt-companions.yaml:23 = 5 damage). Reward exclusion is enforced on both sides (tier05/rewards.py:78-82 skips guest_star; the card is absent from CompanionRoster.cs and present only in GuestStarRoster.cs).

### itto_superlative_superstrength — 2 finding(s)
*legs read: /home/user/GItS/docs/inazuma-companions.yaml:77-81; /home/user/GItS/docs/kokomi-upgrades.yaml:159; /home/user/GItS/docs/teyvat-spire-design-principles.md:101-107; /home/user/GItS/tier0/engine/effects.py:321-348,498-670; /home/user/GItS/tier0/content/loader.py:105-140,286-315; /home/user/GItS/tier0/content/upgrades.py:110-200*
1. **[MEDIUM · text_ops_mismatch]** Itto's card face prints a flat 6 Block while the play actually grants the Spotlight-scaled amount: the Block half is emitted as a plain BlockVar (no multiplier) but resolved through SpotlightSystem.PrintedBlock. The damage half of the same card prints its scaled value, so under GuestCast the face reads '17 damage, 6 Block' while the card grants 9 Block (1.5x).
   - `/home/user/GItS/klee-mod/KleeCode/Cards/Generated/IttoSuperlativeSuperstrength.cs:51 — description `"Deal {CalculatedDamage:diff()} damage. Gain {Block:diff()} [gold]Block[/gold]."``
   - `/home/user/GItS/klee-mod/KleeCode/Cards/Generated/IttoSuperlativeSuperstrength.cs:60 — `new BlockVar(6m, ValueProp.Move)` — no `.WithMultiplier(... PrintedBlockDelta ...)`, so `{Block}` renders the raw 6`
   - `/home/user/GItS/klee-mod/KleeCode/Cards/Generated/IttoSuperlativeSuperstrength.cs:79 — `GainBlock(Owner.Creature, new BlockVar(SpotlightSystem.PrintedBlock(this, DynamicVars.Block.BaseValue), ...))` — the granted number IS scaled`
   - `/home/user/GItS/klee-mod/KleeCode/Powers/SpotlightSystem.cs:286-297 — PrintedBlockDelta/PrintedBlock exist precisely so face and gain agree; :265-272 states the failure mode being avoided ('the card printing its base while Spotlight silently scaled the hit')`
   - `/home/user/GItS/tools/gen_klee_cards.py:1838-1842 — spotlight_block_rider returns None when `any(calc_rider(card, e) is not None ...)`, which is now true for EVERY companion damage card via spotlight_calc_rider (gen_klee_cards.py:1792-1815), so the block face var is suppressed`
   - `/home/user/GItS/tier0/engine/effects.py:631 — tier0 scales companion Block the same way (`amount = _spotlight_scale(state, card, raw)`), confirming the resolved value is right and only the printed face is wrong`
   - note: Behaviour matches the sim; the divergence is face-vs-resolve inside C#. Same shape on thoma_crimson_ooyoroi (ThomaCrimsonOoyoroi.cs:61/70/89) and shinobu_sanctifying_ring, so this is a generator-wide widening: gen_klee_cards.py:1827-1831 still claims 'freminet_pressurized_floe is the only one' excluded, which stopped being true when the spotlight damage rider landed.
2. **[LOW · semantic_drift]** Itto is tagged role_c: trigger, but his card has no aura interaction whatsoever — geo damage with applies_element: false plus Block — so he neither applies, consumes nor keys off an aura. The principles doc defines Triggers as cards that act on existing auras, and tier0's derived reaction-fuel test gives him none of the markers it looks for.
   - `/home/user/GItS/docs/inazuma-companions.yaml:77-78 — `role_c: trigger, element: geo, ... effects: [{op: damage, amount: 14, target: enemy, applies_element: false}, {op: block, amount: 6}]``
   - `/home/user/GItS/docs/teyvat-spire-design-principles.md:105 — '**Triggers** act on existing auras (Prune's Swirl, Albedo's Crystallize).'`
   - `/home/user/GItS/tier0/content/loader.py:130-140 — `_is_reaction_fuel` returns True only for applies_element / apply_aura / swirl / consumes_aura / summon_element / AMP_PAYOFF_POWERS; Itto matches none, so he gets no 'reaction' archetype`
   - `/home/user/GItS/tier0/engine/effects.py:276-277 — `if "applies_element" in fx: return card.element if fx["applies_element"] else None` — his geo never reaches the reaction table, so no Crystallize trigger either`
   - note: Cosmetic in effect: role_c is read only by state.py:245 (is_companion) and draft.py:150 (applier check), so no number moves. C# carries no role_c at all (ICompanionCard exposes Star/CompanionElement/PersonalPool/Nation only), so nothing propagates. Base numbers and upgrade are clean three ways: sheet 14 dmg + 6 block, cost 2, rare, star 5 == IttoSuperlativeSuperstrength.cs:57/60/67 == kokomi-upgrades.yaml:159 {damage: +3} == OnUpgrade UpgradeValueBy(3m) with Block held at 6. The sheet's 'no taunt verb' log is honoured on both legs.

### kaeya_frostgnaw — CLEAN
*legs read: docs/mondstadt-companions.yaml:65-66; docs/klee-upgrades.yaml:105; tier0/engine/effects.py:244-261 (_pick_targets), :264-280 (_element_for), :352-380 (deal_damage_to_enemy), :498-613 (_op_damage); tier0/content/upgrades.py:158-164 (damage key); klee-mod/KleeCode/Cards/Generated/KaeyaFrostgnaw.cs:1-93; klee-mod/KleeCode/Powers/ElementalHit.cs:1-88*

### lynette_astonishing_shift — CLEAN
*legs read: docs/fontaine-companions.yaml:28-31; docs/furina-upgrades.yaml:170; tier0/engine/effects.py:264-287 (_element_for, explicit applies_element:false), :498-613 (_op_damage, source="card" for a Skill), :351-437 (shatter/bomb gating on source=="attack"), :936-947 (_op_swirl); tier0/content/upgrades.py:158-164; klee-mod/KleeCode/Cards/Generated/LynetteAstonishingShift.cs:1-90; klee-mod/KleeCode/Powers/FrozenPower.cs:88 (Shatter gated on cardSource Type Attack)*

### lynette_box_trick — CLEAN
*legs read: docs/fontaine-companions.yaml:25-27; docs/furina-upgrades.yaml:169; tier0/engine/effects.py:652-665 (_op_draw); tier0/content/upgrades.py:206-214 ('draw' key); klee-mod/KleeCode/Cards/Generated/LynetteBoxTrick.cs:1-77; klee-mod/KleeCode/Cards/Generated/CompanionRoster.cs:52*

### lynette_enigmatic_feint — CLEAN
*legs read: docs/fontaine-companions.yaml:22-24; docs/furina-upgrades.yaml:168; tier0/engine/effects.py:936-947 (_op_swirl), :615-638 (_op_block); tier0/content/upgrades.py:165-167 ('block' key); tier0/content/characters/furina.yaml:85; klee-mod/KleeCode/Cards/Generated/LynetteEnigmaticFeint.cs:1-85*

### navia_cannon_fire_support — 1 finding(s)
*legs read: docs/fontaine-companions.yaml:64-101; docs/furina-upgrades.yaml:178-179; klee-mod/KleeCode/Cards/Generated/NaviaCannonFireSupport.cs:1-77; klee-mod/KleeCode/Powers/FontainePowers.cs:19-69; tier0/engine/combat.py:255-291; tier0/engine/effects.py:802-850*
1. **[HIGH · sim_vs_csharp_divergence]** Navia's own play pays her power in C# but not in tier0: the sim grants the Block in _finish_play strictly BEFORE resolve_card (so the power is not up yet when her own play is observed), while CannonFireSupportPower fires on AfterCardPlayed, a broadcast that begins after OnPlay has already applied the power — and its guards (ICompanionCard, owner, IsFirstInSeries) do not exclude the card that applied it. Playing Navia yields 0 Block in the sim and 3 (5 upgraded) in the mod.
   - `tier0/engine/combat.py:271`
   - `tier0/engine/combat.py:276`
   - `tier0/engine/combat.py:277`
   - `tier0/engine/combat.py:290`
   - `tier0/tests/test_fontaine.py:240`
   - `tier0/tests/test_fontaine.py:242`
   - note: The sim side is deliberate and pinned by a test whose comment states it outright ('Her own play does not pay itself: the hook runs before resolution'); the assertion is `st.player.block == 0` after playing her (test_fontaine.py:239-243). The C# side records an ORDERING DIVERGENCE at FontainePowers.cs:32-43 but scopes it to 'a companion card that READS the player's Block during its own resolution' — the self-pay case is not in that enumeration, i.e. it was never analysed. The claim depends on the engine broadcasting Hook.AfterCardPlayed over the power list as it stands after OnPlay (the power is applied at NaviaCannonFireSupport.cs:70, inside OnPlay, and AfterCardPlayed is a separate later broadcast); no decompile of the dispatch is in-repo, so that one step is inference rather than read. Non-findings checked and clean: cost 1 / Power / Rare / Self, star 5, geo, fontaine, PersonalPool null (yaml:89 vs .cs:38-44,64); amount 3 (yaml:90 vs .cs:57); upgrade power_amount +2 -> 5 on both sides (furina-upgrades.yaml:179, upgrades.py:454-474 first apply_power, vs .cs:75); trigger keyed on card type not element, ignoring non-companions (combat.py:268-280 `if card.is_companion` vs FontainePowers.cs:62, pinned at test_fontaine.py:251-255); once per card PLAY not per Study Buddy replay (combat.py:271-274 placement outside the replay loop vs IsFirstInSeries at .cs:64); Frail-exempt Block on both sides (raw `p.block +=` at combat.py:279 vs ValueProp.Unpowered at .cs:67); face text matching the sheet note (yaml:90 vs .cs:51).

### neuvillette_ancient_sea_authority — 1 finding(s)
*legs read: docs/fontaine-companions.yaml:128-143; docs/furina-upgrades.yaml:189-196; klee-mod/KleeCode/Cards/Generated/NeuvilletteAncientSeaAuthority.cs:1-77; klee-mod/KleeCode/Powers/FontainePowers.cs:110-138; klee-mod/KleeCode/Powers/ElementalApplication.cs:183-282; klee-mod/KleeCode/Powers/AuraPower.cs:124-187*
1. **[LOW · text_ops_mismatch]** The generated card face prints 'last 1 extra turn(s).' — the only '(s)' string on any generated card — while the power's own tooltip for the identical effect pluralizes properly as 'last {Amount} extra turn{Amount:plural:|s}', so the card and its power read differently for the same fixed value of 1.
   - `klee-mod/KleeCode/Cards/Generated/NeuvilletteAncientSeaAuthority.cs:51`
   - `tools/gen_klee_cards.py:506`
   - `klee-mod/KleeCode/Powers/FontainePowers.cs:126`
   - `klee-mod/KleeCode/Powers/FontainePowers.cs:127`
   - note: Cosmetic only — the number and the meaning are right on both surfaces, and since the upgrade is cost-only the value can never leave 1, so the parenthetical can never be correct. Every other entry in the same codegen description table either carries no count or uses the {X:plural:|s} token. Non-findings checked and clean: cost 1 / Power / Rare / Self, star 5, hydro, fontaine, PersonalPool null and no guest_star (yaml:128 vs .cs:38-44,64); amount 1 self (yaml:129 vs .cs:70); duration read through ONE helper on both sides so application and refresh cannot disagree (reactions.aura_duration at reactions.py:39-48 used at :55 and :81, vs AuraCmd.Duration at ElementalApplication.cs:228-230 used at :246-262 and in Refresh :279, pinned at test_fontaine.py:290-306); base AURA_DURATION_TURNS 2 mirrored (constants.py:44 vs ReactionTable.cs:30); swirl-spread auras also extended on both sides (reactions.py:98-99 via apply_aura vs ReactionEffects.cs:279-286 passing the dealer as applier); the power applies no element of its own (test_fontaine.py:309-316; no IElementalCard on the C# class and no hook on AncientSeaAuthorityPower — it is a pure marker read at the one duration site, FontainePowers.cs:134-137); tick-down at player turn start on both sides (reactions.tick_auras vs AuraPower.AfterSideTurnStart(Player), AuraPower.cs:179-186); upgrade cost -1 -> 0 rather than magnitude (furina-upgrades.yaml:189-196, upgrades.py:130-131, vs EnergyCost.UpgradeBy(-1) at .cs:75); banner separation from the three Guest Star cameos intact (loader.py:286-298 guest_star/rarity filters, manifest companions list).

### nicole_celestial_gift — 3 finding(s)
*legs read: docs/mondstadt-companions.yaml:1-16 (header), :75-87; docs/klee-upgrades.yaml:110; tier0/constants.py:86 (CELESTIAL_GIFT_BLOCK = 4); tier0/engine/effects.py:2287-2325 (flat_attack_bonus, celestial_gift removal note), :2358-2367 (turn-start Strength + Block); tier0/content/upgrades.py:56-72 (UNAPPLIABLE history), :128-131 (cost key); klee-mod/KleeCode/Cards/Generated/NicoleCelestialGift.cs:1-77*
1. **[MEDIUM · sheet_vs_sim_divergence]** The companion sheet header names nicole_celestial_gift as a non-upgrading UNAPPLIABLE companion, contradicting its own per-card comment 18 lines later, the empty UNAPPLIABLE set, the ratified {cost: -1} delta, and the generated card's OnUpgrade.
   - `docs/mondstadt-companions.yaml:10-12 ("The only companions that still do not upgrade are the sim's own UNAPPLIABLE set (durin_witchs_flame, nicole_celestial_gift)")`
   - `docs/mondstadt-companions.yaml:82-83 (same file: "Block is a constant (CELESTIAL_GIFT_BLOCK) because nothing on the card scales it and the upgrade is cost-only.")`
   - `tier0/content/upgrades.py:72 (UNAPPLIABLE: frozenset[str] = frozenset())`
   - `docs/klee-upgrades.yaml:110 (nicole_celestial_gift: {cost: -1}   # 2 -> 1. RATIFIED 2026-07-26 with the redesign.)`
   - `klee-mod/KleeCode/Cards/Generated/NicoleCelestialGift.cs:73-76 (OnUpgrade() { EnergyCost.UpgradeBy(-1); })`
   - note: Verified live: loader.get_card("nicole_celestial_gift+").cost == 1 in the sim, matching the mod's -1 energy upgrade. The header claim is the stale surface.
2. **[LOW · other]** The UNAPPLIABLE retirement comment records Nicole's delta as having moved to {buff: +2} bound by the buff grammar, but the ratified sheet delta is {cost: -1}, which the applier handles on a different branch entirely.
   - `tier0/content/upgrades.py:60-65 ("nicole_celestial_gift LEFT this set with G-C2 (2026-07-25) ... its delta moved from {block_per_turn: +2} ... to {buff: +2}, which the `buff` grammar already binds to the first top-level apply_power.")`
   - `docs/klee-upgrades.yaml:110 (nicole_celestial_gift: {cost: -1}   # 2 -> 1. RATIFIED 2026-07-26 with the redesign.)`
   - `tier0/content/upgrades.py:128-131 (the cost branch that actually runs for this row)`
   - note: Comment drift: the {buff: +2} step was superseded a day later by the 2026-07-26 redesign; the module docstring at :15-22 likewise still lists "Nicole's per-turn block" as unexpressible.
3. **[LOW · semantic_drift]** CelestialGiftPower's class summary still describes the retired design ("your attack cards deal +Amount per hit ... tier0 resolve_card adds celestial_gift into current_attack_bonus"), which the same class body and the sim both explicitly removed at the 2026-07-26 redesign.
   - `klee-mod/KleeCode/Powers/CompanionPowers.cs:325-328 ("/// Nicole: your attack cards deal +Amount per hit (tier0 resolve_card adds /// celestial_gift into current_attack_bonus, which lands on every hit's /// base)")`
   - `klee-mod/KleeCode/Powers/CompanionPowers.cs:344-350 ("ModifyDamageAdditive is GONE, and its absence is the redesign ... the sim's flat_attack_bonus dropped its celestial_gift term in the same change")`
   - `tier0/engine/effects.py:2305-2312 ("celestial_gift LEFT this sum at the 2026-07-26 red-pen redesign ... bonus = (p.powers.get(\"next_attack_up\", 0) + p.powers.get(\"attack_up_this_turn\", 0))")`
   - note: Doc-comment only; the executable halves (turn-start Strength then 4 Block) agree across sim and mod, including ordering.

### prune_witch_hunt — 2 finding(s)
*legs read: docs/mondstadt-companions.yaml:1-97 (header rules + entry at :89-97); docs/klee-upgrades.yaml:107; tier0/engine/effects.py:264-300 (_element_for), :351-495 (deal_damage_to_enemy), :615-665 (_op_block/_op_draw), :936-1010 (_op_swirl/_op_gain_spark), :1150-1220 (_op_generate_guest_star/_generation_pool/_generate), :1510-1680 (_op_conditional + predicates), :2240-2330 (resolve_card/flat_attack_bonus); tier0/content/loader.py:1-340 (_card_index docs-sheet post-processing, _is_reaction_fuel, guest_star_generation_pool, companion_pool); tier0/content/upgrades.py:1-525 (dispatch incl. 'spark' key at :356-358); tier0/engine/state.py:100-250 (Card fields, is_companion)*
1. **[MEDIUM · text_ops_mismatch]** The card face prints a hard "gain 5 Block" for the else-branch, but the Block actually gained is Spotlight-scaled (PrintedBlock(this, 5m)), so under Guest Cast the resolved Block exceeds the number the description shows. Every other block-bearing companion in the same sprint was converted to a CalculatedBlockVar whose face and gain read one value; Prune's conditional-branch literal was not.
   - `klee-mod/KleeCode/Cards/Generated/PruneWitchHunt.cs:55`
   - `klee-mod/KleeCode/Cards/Generated/PruneWitchHunt.cs:83`
   - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:297`
   - `klee-mod/KleeCode/Cards/Generated/LynetteEnigmaticFeint.cs:63`
   - `tier0/engine/effects.py:631`
   - `docs/archive/furina-legibility-sprint-log.md:310`
   - note: tier0 and C# agree on the RESOLVED value (both spotlight-scale the printed 5); only the displayed text diverges, so this is a face/implementation mismatch rather than a sim/C# split. Corroborated as a known-and-logged gap in the legibility sprint log, but it is still live in the shipped card. Reachable only when the card is Spotlighted, i.e. in a Furina run — which is itself only possible via the generation path in the second finding.
2. **[MEDIUM · sheet_vs_sim_divergence]** The sheet declares Prune a Klee personal-pool card explicitly "not in shared pool", and the Guest Star guardrail (d) says generation pulls from the SHARED companion pool plus the Guest Star set; but neither layer filters personal_pool out of the generation pool, so Furina's uncommon generators (The Guest List, Command Performance) can put a Klee-only companion into a Furina hand.
   - `docs/mondstadt-companions.yaml:89`
   - `docs/mondstadt-companions.yaml:90`
   - `docs/fontaine-companions.yaml:177`
   - `tier0/content/loader.py:114`
   - `tier0/engine/effects.py:1155`
   - `klee-mod/KleeCode/Powers/GuestStarGenerator.cs:32`
   - note: Verified live: loader.guest_star_generation_pool('uncommon') returns 17 cards and prune_witch_hunt is one of them. The tier0 op's own docstring asserts the opposite invariant — "playable characters' personal cards are structurally absent because they are neither companions nor guest_star rows" (tier0/engine/effects.py:1155-1157) — which is false for a personal_pool COMPANION row. tier0 and C# behave identically, so this is spec-vs-implementation, not a sim/C# split. Every other consumer does filter (tier05/rewards.py:241-246, tier05/shop.py:145, klee-mod/KleeCode/CompanionPool.cs:88-91). Related latent gap, not filed separately because no content reaches it: loader.companion_pool (tier0/content/loader.py:122-136) documents itself as "every ordinary SHARED Companion of the nation" and also omits a personal_pool filter, but every conscript row defaults to nation inazuma (tier0/engine/effects.py:2018) where no personal_pool companion exists, and the C# twin is hard-pinned to Inazuma (klee-mod/KleeCode/Powers/KokomiConscript.cs:57).

### raiden_musou_no_hitotachi — 1 finding(s)
*legs read: /home/user/GItS/docs/inazuma-companions.yaml:83-117; /home/user/GItS/docs/kokomi-upgrades.yaml:160-169; /home/user/GItS/tier0/engine/effects.py:244-262,264-288,498-560,802-872,2214-2290; /home/user/GItS/tier0/content/upgrades.py:110-200; /home/user/GItS/tier0/tests/test_kokomi.py:610-618; /home/user/GItS/tier05/rewards.py:85-165*
1. **[MEDIUM · sim_vs_csharp_divergence]** The Vulnerable rider re-aims in tier0 when the 40 damage kills its target: each op independently calls _pick_targets, which returns the lowest-HP LIVING enemy, so on a multi-enemy board the kill hands the free Vulnerable 2 to a second, untouched enemy. C# applies it to the fixed cardPlay.Target, i.e. the corpse — nothing. The sheet's own gloss claims StS Bash ordering, which is same-target.
   - `/home/user/GItS/docs/inazuma-companions.yaml:89-90 — `{op: damage, amount: 40, target: enemy, applies_element: true},` / `{op: apply_power, power: vulnerable, amount: 2, target: enemy}``
   - `/home/user/GItS/docs/inazuma-companions.yaml:104 — '# - Vulnerable is applied AFTER the damage (StS Bash ordering), so the 40 does NOT amplify itself.'`
   - `/home/user/GItS/tier0/engine/effects.py:244-256 — `_pick_targets` recomputes `living = state.living_enemies` and returns `min(living, key=lambda e: e.hp)` on every call; there is no per-play target memory (resolve_card, effects.py:2222-2285, snapshots no target)`
   - `/home/user/GItS/tier0/engine/effects.py:868-871 — `for enemy in _pick_targets(state, target): powers.apply_power(state, enemy, fx["power"], amount, ...)` — the rider re-picks after the damage op resolved`
   - `/home/user/GItS/klee-mod/KleeCode/Cards/Generated/RaidenMusouNoHitotachi.cs:83-88 — `DamageCmd.Attack(...).Targeting(cardPlay.Target)` then `PowerCmd.Apply<VulnerablePower>(choiceContext, cardPlay.Target, 2, ...)` — one fixed target for both halves`
   - note: Structural to the damage+debuff family, but Raiden is the extreme case: at 40 base (50 upgraded) the aimed enemy is dead far more often than not, so the sim measures a spread debuff the mod never delivers. Everything else is clean three ways: cost 3 / 40 damage / Vulnerable 2 / applies electro / Exhaust == RaidenMusouNoHitotachi.cs:51 (CardKeyword.Exhaust, AppliesElectro), :71 (CalculationBase 40m), :76 (base(3, CardType.Attack, CardRarity.Rare)), :88 (Vulnerable 2 after the hit); upgrade {damage: +10} (kokomi-upgrades.yaml:160) == OnUpgrade UpgradeValueBy(10m) with the rider untouched; rare/star-5/pool membership pinned by test_kokomi.py:611-615, manifest.json:108 and CompanionRoster.cs:58.

### sara_crowfeather_cover — 1 finding(s)
*legs read: docs/inazuma-companions.yaml:66-70; docs/kokomi-upgrades.yaml:157; tier0/engine/effects.py:955-957 (_op_buff_next_attack), :2246-2267 (consumption at play), :2286-2320 (flat_attack_bonus), :498-545; tier0/content/upgrades.py:454-474 (buff key); tier0/engine/powers.py (apply_power); klee-mod/KleeCode/Cards/Generated/SaraCrowfeatherCover.cs:1-77*
1. **[LOW · other]** The generated file's provenance header names the wrong sheets: docs/klee-cards.yaml and docs/klee-upgrades.yaml, instead of docs/inazuma-companions.yaml and docs/kokomi-upgrades.yaml.
   - `klee-mod/KleeCode/Cards/Generated/SaraCrowfeatherCover.cs:2 — `//     Generated by tools/gen_klee_cards.py from docs/klee-cards.yaml.``
   - `klee-mod/KleeCode/Cards/Generated/SaraCrowfeatherCover.cs:6 — `//     Upgrade deltas come from docs/klee-upgrades.yaml (R24 2026-07-20: the``
   - `docs/inazuma-companions.yaml:67 — `- {id: sara_crowfeather_cover, name: "Kujou Sara — Crowfeather Cover", ...}``
   - `docs/kokomi-upgrades.yaml:157 — `sara_crowfeather_cover:  {buff: +2}      # +4->+6 (bennett_passion-parity)``
   - `tools/gen_klee_cards.py:4966-4980 — KLEE_PROFILE branch hardcodes both header strings`
   - note: Comment-only, systemic across all companion files. Everything executable is in three-way parity: buff_next_attack 4 (yaml:68) == `new DynamicVar("PowerAmount", 4m)` (.cs:57) == `_op_buff_next_attack` applying next_attack_up 4 (effects.py:955-956); upgrade {buff: +2} -> 6 on both legs (upgrades.py:454-474 binds `buff` to the top-level buff_next_attack op vs .cs:75 `DynamicVars["PowerAmount"].UpgradeValueBy(2m)`), and the face carries {PowerAmount:diff()} (.cs:51) so the upgraded number renders; cost 0 / Skill / Common / Self (yaml:67 vs .cs:64); card text matches the power's own tooltip (.cs:51 vs CompanionPowers.cs:414). Timing/scope semantics agree exactly: the buff pays every hit of one Attack card and is consumed by the FIRST resolution of that card, not the last — tier0 pops `next_attack_up` at play under `if card.type == "attack"` (effects.py:2251-2253) and folds it into the per-hit base (effects.py:540-541, :2311), while the C# gates ModifyDamageAdditive on `cardSource is { Type: CardType.Attack }` (CompanionPowers.cs:427-429) and removes on `IsFirstInSeries` (CompanionPowers.cs:451-455, with the 2026-07-21 correction documented against the sim). The `bennett_passion-parity` claim in the delta comment checks out: docs/mondstadt-companions.yaml:58 prints buff_next_attack 4 and docs/klee-upgrades.yaml:103 gives it {buff: +2}; the two cards are not strict duplicates because Bennett also carries burst_energy 5, and tools/lint_strict_domination.py reports CLEAN.

### sara_tengu_stormcall — 1 finding(s)
*legs read: /home/user/GItS/docs/inazuma-companions.yaml:1-117 (header rules + row 70-75); /home/user/GItS/docs/kokomi-upgrades.yaml:1-40,144-170; /home/user/GItS/tier0/engine/effects.py:244-430,498-670,802-880,2214-2300; /home/user/GItS/tier0/engine/powers.py:42-75,120-180; /home/user/GItS/tier0/content/loader.py:1-330; /home/user/GItS/tier0/content/upgrades.py:1-230*
1. **[MEDIUM · sim_vs_csharp_divergence]** Sara is a Skill-typed card that deals damage, and the two engines disagree about whether that hit counts as an "Attack": C#'s SolarIsotomaPower gates only on IsPoweredAttack, so Sara's hit on an aura'd enemy grants 3 Block in the mod, while tier0 classifies her damage as source="card" (not "attack") and grants nothing. Every other attack-gated power in the mod carries the extra CardType.Attack check that Solar Isotoma is missing.
   - `/home/user/GItS/docs/inazuma-companions.yaml:70 — `- {id: sara_tengu_stormcall, ... cost: 1, type: skill,` with `{op: damage, amount: 4, target: enemy, applies_element: true}` on line 71`
   - `/home/user/GItS/tier0/engine/effects.py:500 — `source = "attack" if card.type == "attack" else "card"` (Sara is type: skill -> source "card")`
   - `/home/user/GItS/tier0/engine/effects.py:358-360 — Solar Isotoma block is gated `if (source == "attack" and enemy.aura and state.player.powers.get("solar_isotoma", 0))``
   - `/home/user/GItS/klee-mod/KleeCode/Cards/Generated/SaraTenguStormcall.cs:76 — `: base(1, CardType.Skill, CardRarity.Uncommon, TargetType.AnyEnemy, autoAdd: false)``
   - `/home/user/GItS/klee-mod/KleeCode/Cards/Generated/SaraTenguStormcall.cs:83 — `await DamageCmd.Attack(DynamicVars.CalculatedDamage)` (a powered attack despite CardType.Skill)`
   - `/home/user/GItS/klee-mod/KleeCode/Powers/CompanionPowers.cs:306-312 — SolarIsotomaPower.BeforeDamageReceived checks only `dealer`, `props.IsPoweredAttack()` and `AuraCmd.Find(target)`; no CardType.Attack gate`
   - note: Root cause is in Albedo's power, but it is only observable through Skill-typed damage companions; Sara is one (shinobu_sanctifying_ring is the other in this sheet). Everything else on Sara checks out three ways: sheet 4 dmg/electro-applied/Strength 2 self == tier0 ops == C# (SaraTenguStormcall.cs:67 CalculationBase 4m, :88 StrengthPower 2); upgrade {damage: +2} (kokomi-upgrades.yaml:158) == OnUpgrade UpgradeValueBy(2m) with Strength untouched; Flawless Strategy Strength->Charge conversion exists on both chokepoints (powers.py:156-166 vs KokomiResources.cs:390-407) and the 'silent' tooltip is deliberate on both sides.

### sayu_daruma_gift — 2 finding(s)
*legs read: docs/inazuma-companions.yaml:1-20 (header rules), :38-41 (entry); docs/kokomi-upgrades.yaml:1-10 (header), :150; tier0/engine/effects.py:614-649 (_op_block, _op_block_next_turn), :2330-2352 (turn-start payout), :315-348 (spotlight scaling); tier0/content/upgrades.py:110-135, :155-165, :419-425; tier0/content/loader.py:200-245, :288-315, :490-513; tier0/content/characters/kokomi.yaml:85-105*
1. **[HIGH · sim_vs_csharp_divergence]** The `block_next_turn: +2` half of Muji-Muji Daruma's upgrade is inert in C#. The sim's Daruma+ banks 6 Block for next turn; the mod's Daruma+ banks 4 and its face still prints 4. OnUpgrade bumps a DynamicVar that nothing reads — OnPlay and the description both hardcode the literal 4.
   - `docs/inazuma-companions.yaml:39 — `effects: [{op: block, amount: 4}, {op: block_next_turn, amount: 4}]``
   - `docs/kokomi-upgrades.yaml:150 — `sayu_daruma_gift:        {block: +2, block_next_turn: +2}   # 4+4 -> 6+6 (v0.4: the next-turn half moves too)``
   - `tier0/content/upgrades.py:419-425 — the `block_next_turn` key `_bump_first(... fx.get("op") == "block_next_turn"), "amount", val)`, so tier0 really does raise the banked Block to 6`
   - `tier0/engine/effects.py:640-649 — `_op_block_next_turn` reads `fx["amount"]` (the upgraded 6) and applies it as the `block_next_turn` power`
   - `klee-mod/KleeCode/Cards/Generated/SayuDarumaGift.cs:80 — `DynamicVars["BlockNextTurn"].UpgradeValueBy(2m);``
   - `klee-mod/KleeCode/Cards/Generated/SayuDarumaGift.cs:74 — `await PowerCmd.Apply<BlockNextTurnPower>(choiceContext, Owner.Creature, (int)SpotlightSystem.PrintedBlock(this, 4), applier: Owner.Creature, cardSource: this);` — literal 4, never reads DynamicVars["BlockNextTurn"]`
   - note: Root cause is in the generator, not a hand-edit: tools/gen_klee_cards.py:3544-3546 emits `amount = str(int(eff["amount"]))` for the block_next_turn OnPlay path and :3905-3910 emits the literal into the description, while :4489 registers `DynamicVars["BlockNextTurn"]` as the upgrade target — the var has no reader. The generator's own comment at :3906-3907 ("Literal: the `block` delta binds to the plain block op") is the stale assumption, and it is false for exactly this card, whose sheet moves both halves. Identical shape was already recorded on kokomi:tideline_watch (review/parity-sweep/findings-ledger.md:729-739), which explicitly names SayuDarumaGift as the second instance but could not file it (S1 was cards-only). Player-visible: Daruma+ is a 12-Block card in the sim and a 10-Block card in the mod. Contrast the correctly-wired plain-block half on the same file (CalculationBase 4 -> 6 at :57/:79, read by OnPlay at :73 and by the face's {CalculatedBlock:diff()}). Non-findings checked and clean: cost/type/rarity/target (yaml:38 vs .cs:67); Star/Element/Nation/PersonalPool (.cs:38-44 vs sheet header + loader.py:217-221 nation-from-filename); next-turn payout timing after the block reset (effects.py:2344-2350 pop vs CompanionPowers.cs:461-466 AfterBlockCleared); Spotlight scaling of both halves at play time (effects.py:346-348 and :646-648 vs SpotlightSystem.cs:291-297); randomized-starter roll parity (kokomi.yaml:103-104 rng.choice over [sayu_daruma_gift, shinobu_grass_ring_bond] vs KleeStartingCompanions.cs:121-123 NextBool over the same pair, same replace-in-place index discipline).
2. **[LOW · other]** The generated file's provenance header names the wrong sheets: it says the card came from docs/klee-cards.yaml and that its upgrade delta lives in docs/klee-upgrades.yaml, but the row is in docs/inazuma-companions.yaml and the delta is in docs/kokomi-upgrades.yaml (neither Klee sheet contains this id).
   - `klee-mod/KleeCode/Cards/Generated/SayuDarumaGift.cs:2 — `//     Generated by tools/gen_klee_cards.py from docs/klee-cards.yaml.``
   - `klee-mod/KleeCode/Cards/Generated/SayuDarumaGift.cs:6 — `//     Upgrade deltas come from docs/klee-upgrades.yaml (R24 2026-07-20: the``
   - `docs/inazuma-companions.yaml:38 — `- {id: sayu_daruma_gift, name: "Sayu — Muji-Muji Daruma", ...}` (the actual sheet entry)`
   - `docs/kokomi-upgrades.yaml:150 — `sayu_daruma_gift:        {block: +2, block_next_turn: +2}` (the actual delta)`
   - `tools/gen_klee_cards.py:4966-4980 — the KLEE_PROFILE branch hardcodes both header strings; companions are generated under that profile regardless of which nation sheet they came from`
   - note: Comment-only; no executable value is affected. Systemic to every companion file in klee-mod/KleeCode/Cards/Generated/ (all three nation sheets), so this should cluster in triage rather than be read as a per-card regression. Filed because the header actively misdirects: a maintainer told to "change the sheet instead" would open docs/klee-upgrades.yaml and find no such id.

### sayu_naptime — 1 finding(s)
*legs read: docs/inazuma-companions.yaml:42-44; docs/kokomi-upgrades.yaml:151; tier0/engine/effects.py:614-638 (_op_block), :650-663 (_op_draw), :315-348; tier0/content/upgrades.py:206-215 (draw key); tier0/content/loader.py:106-140 (_is_reaction_fuel), :288-315; klee-mod/KleeCode/Cards/Generated/SayuNaptime.cs:1-81*
1. **[LOW · other]** The generated file's provenance header names the wrong sheets: it says the card came from docs/klee-cards.yaml and that its upgrade delta lives in docs/klee-upgrades.yaml, but the row is in docs/inazuma-companions.yaml and the delta is in docs/kokomi-upgrades.yaml.
   - `klee-mod/KleeCode/Cards/Generated/SayuNaptime.cs:2 — `//     Generated by tools/gen_klee_cards.py from docs/klee-cards.yaml.``
   - `klee-mod/KleeCode/Cards/Generated/SayuNaptime.cs:6 — `//     Upgrade deltas come from docs/klee-upgrades.yaml (R24 2026-07-20: the``
   - `docs/inazuma-companions.yaml:42 — `- {id: sayu_naptime, name: "Sayu — Naptime", star: 4, rarity: uncommon, ...}``
   - `docs/kokomi-upgrades.yaml:151 — `sayu_naptime:            {draw: +1}      # 1->2, still free``
   - `tools/gen_klee_cards.py:4966-4980 — KLEE_PROFILE branch hardcodes both header strings`
   - note: Comment-only, systemic across all companion files. Everything executable on this card is in three-way parity: sheet block 3 + draw 1 (yaml:43) == CalculationBase 3 / CardsVar(1) (.cs:57,60) == tier0 ops; upgrade {draw: +1} moves only the draw on both legs (upgrades.py:206-215 hits every draw op vs .cs:79 `DynamicVars.Cards.UpgradeValueBy(1m)`, block untouched on both); cost 0 / Skill / Uncommon / Self (yaml:42 vs .cs:67); block converts through CalculatedBlockVar so the face is Spotlight-legible (.cs:59 + :73, matching effects.py:626-635); no applies_element op, so correctly not IElementalCard and correctly not tagged reaction fuel (loader.py:130-139). The uncommon-strictly-dominates-moon_signal relation is a ratified allowlist entry (tools/lint_strict_domination.py:119-121), not a defect.

### sayu_yoohoo_windwheel — 1 finding(s)
*legs read: docs/inazuma-companions.yaml:34-37; docs/kokomi-upgrades.yaml:149; tier0/engine/effects.py:232-262 (_default_target/_pick_targets), 498-614 (_op_damage), 936-947 (_op_swirl); tier0/content/loader.py:107-145 (_is_reaction_fuel); tier0/content/upgrades.py:400-500; klee-mod/KleeCode/Cards/Generated/SayuYoohooWindwheel.cs:1-90*
1. **[MEDIUM · sim_vs_csharp_divergence]** tier0 can resolve this one card against TWO different enemies — the damage at the lowest-HP enemy and the Swirl at a different, aura-bearing enemy — while the shipped card resolves both halves against the single chosen target, so the sim extracts value the real card cannot.
   - `tier0/engine/effects.py:940-946 — _op_swirl re-aims: 'if fx.get("target") == "enemy" and targets and not targets[0].aura' it switches to the lowest-HP AURA'D enemy`
   - `tier0/engine/effects.py:249-256 — _pick_targets('enemy'), used by the damage op on the same card, returns the lowest-HP living enemy with no aura consideration`
   - `klee-mod/KleeCode/Cards/Generated/SayuYoohooWindwheel.cs:77-82 — DamageCmd.Attack(...).Targeting(cardPlay.Target) then ElementalHit.ApplyOnly(choiceContext, cardPlay.Target, ...): one target for both halves`
   - `docs/inazuma-companions.yaml:35-37 — the sheet prints one card: 4 damage to an enemy plus a Swirl, with no split-target grammar`
   - note: Measured: in a two-enemy state (20 HP no aura, 100 HP Hydro aura) tier0's log shows damage->'low' and reaction swirl->'aura' from a single resolve_card. The re-pick across ops is documented as a model caveat at tier0/engine/effects.py:236-239, but the swirl re-aim at 940-946 is an additional deliberate override, and it is the only companion card in this group that carries both a single-target damage op and a single-target swirl op. Everything else is parity-clean: 4 damage untagged + Swirl (Anemo ApplyOnly is the established C# idiom, cf. LynetteEnigmaticFeint.cs:78), upgrade docs/kokomi-upgrades.yaml:149 {damage:+2} -> tier0 4->6 and SayuYoohooWindwheel.cs:87 CalculationBase.UpgradeValueBy(2m).

### shinobu_grass_ring_bond — 1 finding(s)
*legs read: docs/inazuma-companions.yaml:8-10, :51-53; docs/kokomi-upgrades.yaml:153; tier0/engine/effects.py:614-638, :315-348; tier0/content/upgrades.py:159-162 (block key); tier0/content/loader.py:200-245, :490-513; tier0/content/characters/kokomi.yaml:103-104*
1. **[LOW · other]** The generated file's provenance header names the wrong sheets: docs/klee-cards.yaml and docs/klee-upgrades.yaml, instead of docs/inazuma-companions.yaml and docs/kokomi-upgrades.yaml.
   - `klee-mod/KleeCode/Cards/Generated/ShinobuGrassRingBond.cs:2 — `//     Generated by tools/gen_klee_cards.py from docs/klee-cards.yaml.``
   - `klee-mod/KleeCode/Cards/Generated/ShinobuGrassRingBond.cs:6 — `//     Upgrade deltas come from docs/klee-upgrades.yaml (R24 2026-07-20: the``
   - `docs/inazuma-companions.yaml:51 — `- {id: shinobu_grass_ring_bond, name: "Shinobu — Grass Ring of Sanctification", ...}``
   - `docs/kokomi-upgrades.yaml:153 — `shinobu_grass_ring_bond: {block: +2}     # v0.4: 4->6 at 0 cost, the honest wall thickens``
   - `tools/gen_klee_cards.py:4966-4980 — KLEE_PROFILE branch hardcodes both header strings`
   - note: Comment-only, systemic across all companion files. Everything executable is in three-way parity: single block 4 (yaml:52) == CalculationBase 4 (.cs:57) == _op_block; upgrade {block: +2} -> 6 on both legs (upgrades.py:159-162 vs .cs:77); cost 0 / Skill / Common / Self (yaml:51 vs .cs:66); the block converts through CalculatedBlockVar so the face and the resolved gain read one Spotlight-scaled number (.cs:59 + :72 vs effects.py:632); no applies_element op so correctly not IElementalCard and not reaction-tagged; the header's dropped self-HP errata (yaml:8-10) is honoured on both legs. Randomized-starter parity holds: it is the alternate support-slot pick in both engines (tier0/content/characters/kokomi.yaml:104 `choices: [sayu_daruma_gift, shinobu_grass_ring_bond]` vs KleeStartingCompanions.cs:121-123).

### shinobu_sanctifying_ring — 2 finding(s)
*legs read: docs/inazuma-companions.yaml:8-10 (self-HP errata), :47-50; docs/kokomi-upgrades.yaml:152; tier0/engine/effects.py:498-612 (_op_damage incl. AoE targeting + element), :264-287 (_element_for), :614-638, :351-395 (deal_damage_to_enemy); tier0/content/upgrades.py:150-158 (damage key); tier0/content/loader.py:106-140; klee-mod/KleeCode/Cards/Generated/ShinobuSanctifyingRing.cs:1-96*
1. **[LOW · text_ops_mismatch]** The Block half of the card prints its unscaled base while the resolved gain is Spotlight/GuestCast-scaled, on a card whose damage half IS scaled on the face — so under a Furina Guest Cast the card shows "Deal 5 damage to ALL enemies. Gain 4 Block" and actually grants more than 4.
   - `klee-mod/KleeCode/Cards/Generated/ShinobuSanctifyingRing.cs:61 — `("description", "Deal {CalculatedDamage:diff()} damage to ALL enemies. Gain {Block:diff()} [gold]Block[/gold].")``
   - `klee-mod/KleeCode/Cards/Generated/ShinobuSanctifyingRing.cs:70 — `new BlockVar(4m, ValueProp.Move)` — a plain var with no Spotlight multiplier, so the face renders the flat 4`
   - `klee-mod/KleeCode/Cards/Generated/ShinobuSanctifyingRing.cs:89 — `await CreatureCmd.GainBlock(Owner.Creature, new BlockVar(SpotlightSystem.PrintedBlock(this, DynamicVars.Block.BaseValue), ValueProp.Move), cardPlay);` — the resolved gain IS scaled`
   - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:297 — `public static decimal PrintedBlock(CardModel card, decimal amount) => Math.Truncate(amount * OutwardMultiplier(card));``
   - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:232-239 — OutwardMultiplier is live for any `ICompanionCard` that is spotlighted under an active Guest Cast, so this card is reachable`
   - `tools/gen_klee_cards.py:1827-1832 and :1840 — the generator deliberately excludes a block op from CalculatedBlockVar when the card's damage already converts (`if any(calc_rider(card, e) is not None for e in effects): return None`), because CalculationBase is a single shared var`
   - note: NOT a sim/C# divergence — tier0 scales this Block identically (effects.py:632 `amount = _spotlight_scale(state, card, raw)`), so both engines grant the same number; only the printed face disagrees, and only while spotlighted. The generator documents the exclusion as an accepted mechanical limit (one CalculationBase per card), so this is a known legibility gap rather than a regression; filed low because the Legibility-sprint contract quoted at SpotlightSystem.cs:269-272 ("the face, the enemy hover and the resolved hit then read one value") is met by the damage half and not the block half of the same card. Everything else is in three-way parity: damage 3 to all_enemies + block 4 (yaml:48) == CalculationBase 3 / BlockVar 4 (.cs:67,70) == the ops; upgrade {damage: +2} moves damage only and Block stays 4 on both legs (kokomi-upgrades.yaml:152 vs upgrades.py:150-158 vs .cs:94); cost 2 / Skill / Common / AllEnemies (yaml:47 vs .cs:77); applies_element: true == IElementalCard + AppliesElectro keyword + per-target aura application (.cs:37,51 + ElementalApplication.cs:196-204 vs effects.py:276-277 and the per-enemy `deal_damage_to_enemy(..., element=element)` loop at :594-612); the header's dropped self-HP cost (yaml:8-10) is honoured — no self-damage op on either leg. Card-type gating agrees on both legs for a damage-dealing Skill: NextAttackUpPower needs `cardSource is { Type: CardType.Attack }` (CompanionPowers.cs:427-429) exactly as tier0 gates `current_attack_bonus` on `card.type == "attack"` (effects.py:540), and Shatter is likewise Attack-gated on both (FrozenPower.cs:88 vs effects.py:387).
2. **[LOW · other]** The generated file's provenance header names the wrong sheets: docs/klee-cards.yaml and docs/klee-upgrades.yaml, instead of docs/inazuma-companions.yaml and docs/kokomi-upgrades.yaml.
   - `klee-mod/KleeCode/Cards/Generated/ShinobuSanctifyingRing.cs:2 — `//     Generated by tools/gen_klee_cards.py from docs/klee-cards.yaml.``
   - `klee-mod/KleeCode/Cards/Generated/ShinobuSanctifyingRing.cs:6 — `//     Upgrade deltas come from docs/klee-upgrades.yaml (R24 2026-07-20: the``
   - `docs/inazuma-companions.yaml:47 — `- {id: shinobu_sanctifying_ring, name: "Shinobu — Sanctifying Ring", ...}``
   - `docs/kokomi-upgrades.yaml:152 — `shinobu_sanctifying_ring: {damage: +2}   # 3->5 all; Block stays 4``
   - `tools/gen_klee_cards.py:4966-4980 — KLEE_PROFILE branch hardcodes both header strings`
   - note: Comment-only, systemic across all companion files.

### shinobu_thundergrust — 1 finding(s)
*legs read: docs/inazuma-companions.yaml:54-56; docs/kokomi-upgrades.yaml:154; tier0/engine/effects.py:498-612, :264-287, :351-395; tier0/content/upgrades.py:150-158; tier0/content/loader.py:106-140; klee-mod/KleeCode/Cards/Generated/ShinobuThundergrust.cs:1-94*
1. **[LOW · other]** The generated file's provenance header names the wrong sheets: docs/klee-cards.yaml and docs/klee-upgrades.yaml, instead of docs/inazuma-companions.yaml and docs/kokomi-upgrades.yaml.
   - `klee-mod/KleeCode/Cards/Generated/ShinobuThundergrust.cs:2 — `//     Generated by tools/gen_klee_cards.py from docs/klee-cards.yaml.``
   - `klee-mod/KleeCode/Cards/Generated/ShinobuThundergrust.cs:6 — `//     Upgrade deltas come from docs/klee-upgrades.yaml (R24 2026-07-20: the``
   - `docs/inazuma-companions.yaml:54 — `- {id: shinobu_thundergrust, name: "Shinobu — Thundergrust", star: 4, rarity: uncommon, ...}``
   - `docs/kokomi-upgrades.yaml:154 — `shinobu_thundergrust:    {damage: +2}    # 7->9``
   - `tools/gen_klee_cards.py:4966-4980 — KLEE_PROFILE branch hardcodes both header strings`
   - note: Comment-only, systemic across all companion files. Everything executable is in three-way parity: single-target damage 7 (yaml:55) == CalculationBase 7 (.cs:67) == _op_damage; upgrade {damage: +2} -> 9 on both legs (upgrades.py:150-158 vs .cs:92); cost 1 / Attack / Uncommon / AnyEnemy (yaml:54 vs .cs:76); applies_element: true == IElementalCard Electro + AppliesElectro keyword + aura application (.cs:37,51 + ElementalApplication.cs:196-204 vs effects.py:276-277); damage renders through CalculatedDamageVar so face, hover and hit read one Spotlight-scaled value (.cs:69 vs effects.py:533); as an Attack it both consumes and collects NextAttackUp on both legs (CompanionPowers.cs:427-429/451-454 vs effects.py:540-541 and :2252-2253). The four allowlisted cross-sheet domination relations (tools/lint_strict_domination.py:122-134) are ratified design, not parity defects; the lint runs CLEAN.

### sucrose_astable — 1 finding(s)
*legs read: docs/mondstadt-companions.yaml:36-45 (row + R62 note); docs/klee-upgrades.yaml:99 (burst_energy: +4); tier0/engine/effects.py:936-948 (_op_swirl), 925-934 (_op_burst_energy); tier0/engine/resources.py:370-397 (gain_burst, uncapped); tier0/engine/refpowers.py:325-340 (exhaust disposal); tier0/content/upgrades.py:446-449*
1. **[HIGH · sim_vs_csharp_divergence]** The card's `burst_energy: 8` payload (12 upgraded) is granted to any character with a Burst meter in tier0, but the generated C# routes it through KleeBurstResource.Gain, which no-ops unless the owner is Klee. For a Furina or Kokomi player the card resolves to 'Swirl, then Exhaust for nothing' while the face still reads 'Gain 8 [gold]Burst Energy[/gold]' — and because the card Exhausts, the loss is permanent for that copy.
   - `docs/mondstadt-companions.yaml:37 — effects: [{op: swirl, target: enemy}, {op: burst_energy, amount: 8}] (row also carries `exhaust: true`, line 36)`
   - `tier0/engine/effects.py:925-926 — `if state.player.burst_max:` is the only gate on the burst_energy op`
   - `tier0/content/characters/furina.yaml:14 — `burst_max: 70`; tier0/content/characters/kokomi.yaml:25 — `burst_max: 20``
   - `klee-mod/KleeCode/Cards/Generated/SucroseAstable.cs:79 — `await KleeBurstResource.Gain(choiceContext, Owner.Creature, DynamicVars["BurstEnergy"].IntValue, this);``
   - `klee-mod/KleeCode/Powers/BurstResource.cs:181 — `if (owner?.Character is not Klee) return null;` and BurstResource.cs:206-208 — Gain returns immediately when Find is null`
   - `klee-mod/KleeCode/Cards/Generated/SucroseAstable.cs:58 — ("description", "[gold]Swirl[/gold] an enemy's aura. Gain {BurstEnergy:diff()} [gold]Burst Energy[/gold].")`
   - note: Verified empirically: resolving sucrose_astable in tier0 as klee/furina/kokomi yields +8 burst in all three cases. The upgrade path is equally affected — docs/klee-upgrades.yaml:99 (`burst_energy: +4`) and SucroseAstable.cs:84 (`DynamicVars["BurstEnergy"].UpgradeValueBy(4m)`) agree on 8->12, but the whole 12 is dropped for non-Klee owners. Same root cause as the barbara_melody finding (codegen emitter, not the card row). Everything else on this card is three-way clean: cost 0, Exhaust (sheet `exhaust: true` -> tier0 refpowers.result_pile "exhaust" -> CardKeyword.Exhaust), and the swirl leg (tier0 _op_swirl == ElementalHit.ApplyOnly, with anemo excluded from AURA_ELEMENTS on both sides).

### sucrose_catalyst_conversion — 1 finding(s)
*legs read: docs/mondstadt-companions.yaml:1-97 (entry at :46-56, header rules :1-16); docs/klee-upgrades.yaml:91-110 (entry at :100-101); tier0/content/loader.py:1-330 (DOCS_CARD_SHEETS :25-28, nation/character derivation :212-232, _is_reaction_fuel :106-140, companion_pool :301-315); tier0/content/upgrades.py:1-72, 115-524 (draw key :206-214); tier0/engine/effects.py:652-700 (_op_draw, _op_energy); klee-mod/KleeCode/Cards/Generated/SucroseCatalystConversion.cs:1-81*
1. **[MEDIUM · sheet_vs_sim_divergence]** The card's sheet note states the §4.7 shop channel is UNBUILT and that the card "reaches players only through the free reward slot", but the shop companion channel is built and this card is exactly the kind of row slot 1 draws (Mondstadt, uncommon).
   - `docs/mondstadt-companions.yaml:54-56 ("NOTE: §4.7 calls this 'reliably shoppable at shop slot-1'. That shop channel is UNBUILT -- see the header of §4.7 ... Today this card reaches players only through the free reward slot, like every other companion.")`
   - `docs/teyvat-spire-design-principles.md:121-123 (the very header the note cites: "STATUS: BUILT 2026-07-25, with three amendments. The shop carries companions in both slots, in the mod and in tier 0.5.")`
   - `tier05/shop.py:99-168 (companion_shop_offer; :151-154 slot 0 = home nation, :171-180 _roll_companion_rarity is Uncommon-or-Rare only)`
   - `docs/mondstadt-companions.yaml:46 (id/rarity/nation-by-file: uncommon Mondstadt companion, i.e. eligible for the home-nation Uncommon-floor slot 1)`
   - note: Design-text staleness, not an in-combat number. The sheet note's own cited source now says the opposite; the acquisition claim ("free reward slot only") is false for tier 0.5 runs.

### sucrose_gust — CLEAN
*legs read: docs/mondstadt-companions.yaml:34-35; docs/klee-upgrades.yaml:98 (draw: +1); tier0/engine/effects.py:936-948 (_op_swirl), 652-666 (_op_draw); tier0/engine/reactions.py:22 (AURA_ELEMENTS excludes anemo), 51-57 (apply_aura no-ops for anemo), 90-130 (_react swirl branch); tier0/content/upgrades.py:206-214; klee-mod/KleeCode/Cards/Generated/SucroseGust.cs:34-83*

### thoma_blazing_barrier — 1 finding(s)
*legs read: docs/inazuma-companions.yaml:58-61; docs/kokomi-upgrades.yaml:155; tier0/engine/effects.py:614-649, :2330-2352, :315-348; tier0/content/upgrades.py:159-162, :419-425; klee-mod/KleeCode/Cards/Generated/ThomaBlazingBarrier.cs:1-80; klee-mod/KleeCode/Powers/CompanionPowers.cs:455-470*
1. **[LOW · other]** The generated file's provenance header names the wrong sheets: docs/klee-cards.yaml and docs/klee-upgrades.yaml, instead of docs/inazuma-companions.yaml and docs/kokomi-upgrades.yaml.
   - `klee-mod/KleeCode/Cards/Generated/ThomaBlazingBarrier.cs:2 — `//     Generated by tools/gen_klee_cards.py from docs/klee-cards.yaml.``
   - `klee-mod/KleeCode/Cards/Generated/ThomaBlazingBarrier.cs:6 — `//     Upgrade deltas come from docs/klee-upgrades.yaml (R24 2026-07-20: the``
   - `docs/inazuma-companions.yaml:59 — `- {id: thoma_blazing_barrier, name: "Thoma — Blazing Barrier", ...}``
   - `docs/kokomi-upgrades.yaml:155 — `thoma_blazing_barrier:   {block: +2}     # 5->7; the lingering ember stays 2``
   - `tools/gen_klee_cards.py:4966-4980 — KLEE_PROFILE branch hardcodes both header strings`
   - note: Comment-only, systemic across all companion files. Explicitly checked for the sayu_daruma_gift defect class and this card is CLEAN of it: the sheet's upgrade moves only the plain block (`{block: +2}`, "the lingering ember stays 2"), tier0's `block` key bumps only the first block op (upgrades.py:159-162) leaving block_next_turn at 2, and the C# correspondingly emits NO BlockNextTurn DynamicVar (gen_klee_cards.py:2071 gates the var on block_next_turn_upgrade), hardcodes 2 in both OnPlay (.cs:73) and the face (.cs:51), and upgrades only CalculationBase 5 -> 7 (.cs:57/:78). Literal and sheet agree, so the hardcode is correct here. Rest of the three-way parity: cost 1 / Skill / Common / Self (yaml:59 vs .cs:66); block converts through CalculatedBlockVar (.cs:59 + :72); the banked half is Spotlight-scaled at play on both legs (SpotlightSystem.cs:297 vs effects.py:646-648) and paid out after the turn-start block reset on both (CompanionPowers.cs:461-466 AfterBlockCleared vs effects.py:2344-2350 pop); no applies_element op so correctly not IElementalCard.

### thoma_crimson_ooyoroi — 2 finding(s)
*legs read: docs/inazuma-companions.yaml:62-65; docs/kokomi-upgrades.yaml:156; tier0/engine/effects.py:498-638, :264-287, :351-395; tier0/content/upgrades.py:150-162; tier0/content/loader.py:106-140; klee-mod/KleeCode/Cards/Generated/ThomaCrimsonOoyoroi.cs:1-96*
1. **[LOW · text_ops_mismatch]** The Block half prints its unscaled base while the resolved gain is Spotlight/GuestCast-scaled, on a card whose damage half IS scaled on the face — under a Furina Guest Cast the card shows "Deal 10 damage. Gain 3 Block" and actually grants more than 3.
   - `klee-mod/KleeCode/Cards/Generated/ThomaCrimsonOoyoroi.cs:61 — `("description", "Deal {CalculatedDamage:diff()} damage. Gain {Block:diff()} [gold]Block[/gold].")``
   - `klee-mod/KleeCode/Cards/Generated/ThomaCrimsonOoyoroi.cs:70 — `new BlockVar(3m, ValueProp.Move)` — plain var, no Spotlight multiplier, so the face renders the flat 3`
   - `klee-mod/KleeCode/Cards/Generated/ThomaCrimsonOoyoroi.cs:89 — `await CreatureCmd.GainBlock(Owner.Creature, new BlockVar(SpotlightSystem.PrintedBlock(this, DynamicVars.Block.BaseValue), ValueProp.Move), cardPlay);` — the resolved gain IS scaled`
   - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:232-239 — OutwardMultiplier is live for any spotlighted `ICompanionCard` under an active Guest Cast`
   - `tools/gen_klee_cards.py:1827-1832 and :1840 — the generator excludes the block op from CalculatedBlockVar because the card's damage already converts through the single CalculationBase var`
   - note: NOT a sim/C# divergence — tier0 scales this Block identically (effects.py:632), so both engines grant the same number; only the printed face disagrees, and only while spotlighted. Documented generator limitation, same shape as shinobu_sanctifying_ring. Everything else is in three-way parity: damage 8 + block 3 (yaml:63) == CalculationBase 8 / BlockVar 3 (.cs:67,70); upgrade {damage: +2} -> 10 with Block held at 3 on both legs (kokomi-upgrades.yaml:156 vs upgrades.py:150-158 vs .cs:94); cost 2 / Attack / Uncommon / AnyEnemy (yaml:62 vs .cs:77); applies_element: true == IElementalCard Pyro + AppliesPyro keyword + aura application (.cs:37,51 + ElementalApplication.cs:196-204 vs effects.py:276-277); op order damage-then-block matches on both legs.
2. **[LOW · other]** The generated file's provenance header names the wrong sheets: docs/klee-cards.yaml and docs/klee-upgrades.yaml, instead of docs/inazuma-companions.yaml and docs/kokomi-upgrades.yaml.
   - `klee-mod/KleeCode/Cards/Generated/ThomaCrimsonOoyoroi.cs:2 — `//     Generated by tools/gen_klee_cards.py from docs/klee-cards.yaml.``
   - `klee-mod/KleeCode/Cards/Generated/ThomaCrimsonOoyoroi.cs:6 — `//     Upgrade deltas come from docs/klee-upgrades.yaml (R24 2026-07-20: the``
   - `docs/inazuma-companions.yaml:62 — `- {id: thoma_crimson_ooyoroi, name: "Thoma — Crimson Ooyoroi", star: 4, rarity: uncommon, ...}``
   - `docs/kokomi-upgrades.yaml:156 — `thoma_crimson_ooyoroi:   {damage: +2}    # 8->10``
   - `tools/gen_klee_cards.py:4966-4980 — KLEE_PROFILE branch hardcodes both header strings`
   - note: Comment-only, systemic across all companion files.

## constants

### BANNER_FEATURED_SLOTS (Featured Banner) — CLEAN
*legs read: tier0/constants.py:786-791; tier05/rewards.py:86-161; klee-mod/KleeCode/CompanionBanner.cs:1-131; klee-mod/KleeCode/CompanionPool.cs:93-119; klee-mod/KleeCode/Cards/Generated/CompanionRoster.cs:18-48*

### BURST_* — 1 finding(s)
*legs read: tier0/constants.py:67-90,300-306; tier0/content/characters/furina.yaml:1-30; tier0/engine/combat.py:247-252; tier0/engine/reactions.py:139-155; tier0/engine/effects.py:2426-2434,716-750; tier0/engine/resources.py:370-397*
1. **[LOW · text_ops_mismatch]** The Burst Energy meter text says Salon ATTACKS grant the SALON_TICK_BURST 2, but the constant is credited once per member TICK of any kind — the Usher's Block tick included — and again on every final bow, which the constant's own comment states outright.
   - `klee-mod/KleeCode/Powers/FurinaResources.cs:1067`
   - `klee-mod/KleeCode/Powers/SalonPowers.cs:452`
   - `klee-mod/KleeCode/Powers/SalonPowers.cs:238`
   - `tier0/constants.py:303`
   - `tier0/engine/effects.py:739`
   - note: Reachability caveat, stated honestly: FurinaBurstMeterPower was RETIRED as a display on 2026-07-24 and is kept registered only for save compatibility (FurinaResources.cs:1056-1060), so a new run never renders this string; Burst's ambient home is now the overhead gauge, which carries no prose. Filed low for that reason.

### CHARGE_* — 1 finding(s)
*legs read: tier0/constants.py:308-450; tier0/engine/resources.py:356-368; tier0/engine/refpowers.py:265-295; tier0/engine/powers.py:153-179; tier0/engine/effects.py:2240-2266,2287-2326,2507-2556; klee-mod/KleeCode/Powers/KokomiResources.cs:1-555*
1. **[LOW · semantic_drift]** CHARGE_PER_EXHAUST (and the Strength->Charge conversion that feeds the same meter) is RELIC-scoped in the sim — every accrual site is gated on `"tamakushi_casket" in relic_hooks` — but CHARACTER-scoped in C#, where the exhaust funnel and Law 3 gate only on IsKokomi and never consult the relic.
   - `tier0/engine/refpowers.py:282`
   - `tier0/engine/resources.py:358`
   - `tier0/engine/powers.py:164`
   - `klee-mod/KleeCode/Powers/KokomiResources.cs:281`
   - `klee-mod/KleeCode/Powers/KokomiResources.cs:396`
   - note: UNOBSERVABLE TODAY, stated plainly: the sim ships tamakushi_casket in furina-style character relic_hooks for every Kokomi, and tier05 models no Kokomi starter-relic upgrade at all, so no current run reaches the divergent state. Filed low because it is a scope difference in where the constant's accrual law is anchored, and the C# file's own comment (KokomiResources.cs:247-251) asserts the sim's relic gate while implementing a character gate.

### ENCORE_* — CLEAN
*legs read: tier0/constants.py:164-182,300-306,540-560; tier0/engine/resources.py:264-354; tier0/engine/effects.py:1008-1020,2399-2434; tier0/engine/powers.py:18-24,139-150; tier0/pilot/policy.py:440-520,595-660; klee-mod/KleeCode/Powers/FurinaResources.cs:97-128,572-663,1006-1025*

### FANFARE_* — 2 finding(s)
*legs read: tier0/constants.py:164-274; tier0/engine/resources.py:1-262; tier0/engine/combat.py:195-252,410-500,788-843; tier0/content/loader.py:430-486; tier0/engine/state.py:352-410; tier05/model.py:535-570*
1. **[MEDIUM · other]** FANFARE_CAP_FRACTION (0.5) has no C# constant at all — the mod encodes it as the bare literal `MaxHp / 2`, which the parity lint structurally cannot see (its CONST_RE only matches `const` declarations), so it is in neither MIRRORED nor UNMIRRORED and a sim-side retune of the fraction would drift silently.
   - `tier0/constants.py:166`
   - `tier0/content/loader.py:441`
   - `klee-mod/KleeCode/Powers/FurinaResources.cs:351`
   - `tools/lint_constant_parity.py:284`
   - `tools/lint_constant_parity.py:123`
   - note: Sibling non-int Furina numbers (FANFARE_DECAY_FRACTION, SALON_DRY_DAMAGE_MULT, SPOTLIGHT_BASE_MULT) were deliberately widened into MIRRORED during the §4.7 shop sprint; the cap fraction is the one member of that family that was never given a C# const to widen to.
2. **[MEDIUM · semantic_drift]** Same 0.5, different scope: the sim applies FANFARE_CAP_FRACTION ONCE to the character sheet's BASE hp at player construction and never recomputes it (run-layer max-HP changes overwrite player.max_hp but not fanfare_cap), while C# recomputes the cap LIVE off creature.MaxHp on every read.
   - `tier0/content/loader.py:485`
   - `tier05/model.py:553`
   - `tier0/engine/state.py:407`
   - `tier0/engine/combat.py:806`
   - `klee-mod/KleeCode/Powers/FurinaResources.cs:348`
   - `tier05/content/events.yaml:84`
   - note: Both the constant's own comment ("Fanfare cap = fraction of maxHP", tier0/constants.py:166) and furina.yaml:17 describe the C# behaviour, so the drifted leg here is arguably the sim — but tier0 is declared source of truth, so the mod is playing to a ceiling no simulation endorsed. Verified the rest of the Fanfare block is faithful: decay is proportional-only with the banker's-rounding pin honoured on both sides (resources.py:114 vs FurinaResources.cs:511-515), the three FanfarePer* legs preserve "every point past Block prints exactly 1 Fanfare" (resources.py:288,351,407 vs FurinaResources.cs:608,661,997), Center Stage mints pre-resolution on both sides (combat.py:227 vs SpotlightSystem.cs:354), the deleted constants (FANFARE_PER_ENCORE_GAINED, FANFARE_DECAY_PER_TURN, FANFARE_FLOOR_PER_POWER/_RARE) are absent from BOTH engines and from the lint tables, and every Fanfare READER in C# goes through ReadableFanfare (clamped) as the sim's readable() requires.

### FANFARE_CAP_FRACTION — 2 finding(s)
*legs read: tier0/constants.py:164-182; tier0/content/loader.py:430-486; tier0/engine/state.py:350-380; tier05/model.py:540-556; tier05/events.py:374-378; tier05/relics.py:378-392*
1. **[MEDIUM · semantic_drift]** Same 0.5, different base and timing: the sim fixes the Fanfare cap at build time from the character's PRINTED hp and never revisits it, while the mod recomputes it live from current MaxHp — so any run that gains max HP raises the mod's ceiling and not the sim's.
   - `tier0/constants.py:166 — `FANFARE_CAP_FRACTION = 0.5    # Fanfare cap = fraction of maxHP.``
   - `tier0/content/loader.py:485-486 — `fanfare_cap=(int(C.FANFARE_CAP_FRACTION * spec["hp"]) if spec.get("fanfare") else 0)` (printed hp, computed once)`
   - `tier0/content/loader.py:441-442 — same expression on the tier0 build path`
   - `tier05/model.py:550-553 — `player = loader.build_player_from_ids(...)` then `player.max_hp = max_hp` (the run's max HP is assigned AFTER the cap was computed, so it never feeds it)`
   - `klee-mod/KleeCode/Powers/FurinaResources.cs:348-351 — `return creature.MaxHp / 2 + (FanfareCapBonusFor(creature)?.Amount ?? 0);` (live MaxHp, every read)`
   - `tier05/events.py:376-377 — `st.max_hp = max(1, st.max_hp + opt["max_hp"])` (runs do raise max HP)`
   - note: Furina is 60 HP on both sides (tier0/content/characters/furina.yaml:9, klee-mod/KleeCode/Furina.cs:40), so both start at cap 30 and the floors/rounding agree (Python int() and C# int division both floor). After a single Looming Fruit the mod's cap is 45 and the sim's is still 30. Severity held at medium because the constant is documented as a demoted safety rail that does not bind under decay (tier0/constants.py:167-174, FurinaResources.cs:341-346).
2. **[MEDIUM · missing_leg]** The mod expresses FANFARE_CAP_FRACTION as a bare `/ 2` literal rather than a constant, so it is in neither MIRRORED nor UNMIRRORED and the parity gate cannot see it — unlike every other float in the same Furina resource block.
   - `klee-mod/KleeCode/Powers/FurinaResources.cs:351 — `creature.MaxHp / 2` (no `const` declared anywhere for the fraction)`
   - `tools/lint_constant_parity.py:284-286 — CONST_RE matches only declared `const int|float|double|decimal` members, so a literal in an expression is invisible`
   - `tools/lint_constant_parity.py:106-110,123 — the sibling floats (VaporizeMult, MeltMult, AmpStackLimit, FanfareDecayFraction) are all mirrored constants`
   - `tier0/constants.py:166 — FANFARE_CAP_FRACTION is a live tier0 knob (swept in tier05/exp_furina_sheetpass.py:206-208 and tier05/exp_furina_pass2.py:147-153)`
   - note: This is the class the lint's own docstring (tools/lint_constant_parity.py:272-280) says was the reason for widening past `int`: a headline float that a sim-side retune would drift silently. A move to 0.4 in tier0 would change nothing in the mod and produce no finding.

### SALON_* — CLEAN
*legs read: tier0/constants.py:275-306; tier0/engine/effects.py:515-540,615-650,652-665,700-790,800-880,1005-1015,2352-2434; klee-mod/KleeCode/Powers/SalonPowers.cs:1-531; klee-mod/KleeCode/Cards/Furina/Generated/GentilhommeUsher.cs:40-110; klee-mod/KleeCode/Cards/SalonMemberTips.cs:95-140; tools/lint_constant_parity.py:54-58,162-173*

### SPARK_* — 1 finding(s)
*legs read: tier0/constants.py:67-89,540-541; tier0/engine/combat.py:22-28,168-205; tier0/engine/effects.py:479-520,2493-2500; klee-mod/KleeCode/Powers/SparkPower.cs:1-205; klee-mod/KleeCode/Powers/SparkKitPowers.cs:85-98; klee-mod/KleeCode/Powers/KitBurst.cs:21-100*
1. **[LOW · text_ops_mismatch]** The Spark power's player-facing text hard-codes SPARKS_FOR_FREE_ATTACK as the literal "3" twice, but the implementation right above it reads a LIVE threshold that True Spark Knight lowers, so the tooltip states a threshold the ops do not use.
   - `klee-mod/KleeCode/Powers/SparkPower.cs:61`
   - `klee-mod/KleeCode/Powers/SparkPower.cs:52`
   - `tier0/engine/combat.py:26`
   - note: Partially mitigated: SparkThresholdDownPower's own text says "You need {Amount} fewer Spark ... (minimum 1)" (SparkKitPowers.cs:91), so the true number is derivable by adding two tooltips. Filed low for that reason.

### SPOTLIGHT_* — 1 finding(s)
*legs read: tier0/constants.py:90-162,550-558; tier0/engine/effects.py:302-348,1035-1060; tier0/engine/combat.py:212-246; tier0/engine/powers.py:18-24,139-150; tier0/engine/resources.py:292-303; tier0/pilot/policy.py:200-215,470-515*
1. **[LOW · sim_vs_csharp_divergence]** SPOTLIGHT_BASE_MULT is a binary FLOAT in the sim and a DECIMAL in C#, and both engines TRUNCATE the product, so the scaled number differs by 1 wherever the float product lands just under an integer — a cross-language rounding hazard the sibling FANFARE_DECAY_FRACTION pins explicitly and this one does not.
   - `tier0/engine/effects.py:338`
   - `tier0/engine/effects.py:348`
   - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:60`
   - `klee-mod/KleeCode/Powers/SpotlightSystem.cs:250`
   - `klee-mod/KleeCode/Powers/FurinaResources.cs:70`
   - note: Verified by brute force over bonus 0..100 x printed 1..60: 6 divergent cells, all at bonus >= 55 with printed >= 25, always the mod one point higher. Rare configuration, one point, hence low — but it is exactly the class of hazard FurinaResourceConstants.FanfareDecayFraction was given a written rounding pin for (FurinaResources.cs:70-74), and the Spotlight multiplier has no such pin.

### STOKE_* — CLEAN
*legs read: tier0/constants.py:1-1013 (grep: no STOKE_* symbol); tier0/pilot/policy.py:568-660; tier0/content/pilots/archetypes.yaml:47-105; tier0/engine/effects.py:1160-1220,1390-1400; klee-mod/KleeCode (grep: no Stoke constant or class)*

### act map + run template (MAP_FLOORS, MAP_TREASURE_FLOOR, MAP_REST_FLOOR, MAP_BOSS_FLOOR, MAP_MAX_EDGES, MAP_ROOM_ODDS, MAP_MAX_FLOOR_WIDTH, MAP_PATHS, MAP_UNKNOWN_BASE, MAP_UNKNOWN_STEP, RUNTEMPLATE_VERSION, RUN_NODE_TEMPLATE, RUN_ACTS) — CLEAN
*legs read: tier0/constants.py:578-678; tier05/maps.py:1-190*

### base_game_parity_powers_line_block — CLEAN
*legs read: tier0/constants.py:13-21, 39-41 (INTANGIBLE_DAMAGE_CAP, DOUBLE_DAMAGE_MULT, OUTBREAK_POISON_THRESHOLD, COLOSSUS_TAKEN_MULT, JUGGLING_ATTACK_TRIGGER); tier0/engine/refpowers.py:730-755 (juggling), 990-1005 (outbreak), 1030-1090 (cruelty/colossus/tracking/double-damage/intangible cap); tools/lint_constant_parity.py:80-270 (no C# counterparts declared, and none exist); klee-mod/KleeCode (grep: no Intangible/DoubleDamage/Outbreak/Colossus/Juggling const)*

### harness, detector and draft/pilot policy floats (DEFAULT_FIGHTS_PER_ENCOUNTER, DEFAULT_SEED, WINRATE_BAND_MIN_FIGHTS, RUNAWAY_SCALING_RATIO, MAX_TURNS, MAX_CARDS_PER_TURN, BLOCK_PANIC_THRESHOLD, PILOT_*, DRAFT_*, ADAPTIVE_COMMIT_THRESHOLD, DIVERGENCE_*, RELEVANCE_FLOOR, ACHIEVABILITY_ALARM_FIGHTS, DRAFT_REGRET_SAMPLE, CONTROL_UPTIME_CARRY, AMP_PAYOFF_POWERS, CONSTANTS_VERSION, DRAFTER_VERSION) — CLEAN
*legs read: tier0/constants.py:23-25,521-576,568-576,918-948; tools/lint_constant_parity.py:83-267; klee-mod/KleeCode (full `const` census via grep, 80 declarations)*

### potion constants (POTION_SLOTS, POTION_BELT_BONUS_SLOTS, POTION_BLOCK, POTION_FIRE_DAMAGE, POTION_BLOOD_HEAL_FRACTION, POTION_STRENGTH, POTION_SWIFT_DRAW, POTION_WEAK, POTION_FEAR_VULN, POTION_ENERGY, POTION_FAIRY_REVIVE_FRACTION, POTION_DEFENSIVE_MARGIN, POTION_BIG_HIT_FRACTION, POTION_DROP_CHANCE, POTION_PRICE) — CLEAN
*legs read: tier0/constants.py:499-519,726-731; tier0/engine/potions.py:61-110,165-250; tier05/potions.py:44-140; tier05/content/potions.yaml:1-37; tier05/model.py:56-60,325-335,440-455,500-510,630-645; tier0/content/loader.py:444-465*

### reaction_damage_numbers — 3 finding(s)
*legs read: tier0/constants.py:43-60 (AURA_DURATION_TURNS…SHATTER_DAMAGE), 570 (AMP_STACK_LIMIT); tier0/engine/reactions.py:1-179 (whole resolver); tier0/engine/effects.py:340-405 (deal_damage_to_enemy, amp guard, shatter); tier0/engine/combat.py:440-520 (bomb→tick_auras order), 600-680 (frozen action); tier0/engine/powers.py:116-140 (dot tick + decay); klee-mod/KleeCode/Elements/ReactionTable.cs:1-129*
1. **[HIGH · semantic_drift]** FROZEN_BOSS_VULN is gated per-CREATURE in the sim (`enemy.is_boss`) but per-ROOM in C# (`RoomType.Boss`), so every non-boss creature standing in a boss room — the Kaiser Crab's second claw, and any summoned add — receives Vulnerable 2 in game where the sim Freezes it, silently deleting the freeze-control payoff (-50% next action + Shatter 6) on half of a shipped boss fight.
   - `tier0/engine/reactions.py:123-129 — `if enemy.is_boss: powers.apply_power(state, enemy, "vulnerable", C.FROZEN_BOSS_VULN)` else `enemy.frozen = True` (per-creature flag, set from content at tier0/content/loader.py:546)`
   - `klee-mod/KleeCode/Powers/ReactionEffects.cs:208-220 — `if (target.CombatState?.Encounter?.RoomType == RoomType.Boss)` → VulnerablePower(FrozenBossVuln), else FrozenPower (per-room)`
   - `tier05/content/act2_pool.yaml:245-247 — `- name: kaiser_crusher` … `is_boss: true``
   - `tier05/content/act2_pool.yaml:258 — `- name: kaiser_rocket` with NO `is_boss` key, i.e. freezable in the sim, unfreezable in game`
   - `tier0/engine/combat.py:704-708 — summon intent builds `Enemy(...)` with no is_boss (defaults False at tier0/engine/state.py:423), so mid-boss adds are freezable in the sim too`
   - `klee-mod/KleeCode/KleeMod.cs:148-150 — the shipped tooltip states 'Bosses cannot be Frozen. Hydro plus Cryo is consumed and applies 2 Vulnerable instead', which is not what the room-scoped check does`
   - note: Constants: FROZEN_BOSS_VULN (2, value-identical on both sides so the lint passes), FROZEN_DAMAGE_MULT (0.5), SHATTER_DAMAGE (6). Same number, different scope — and the tooltip text at KleeMod.cs:149 promises the creature-scoped rule the sim implements, not the room-scoped rule the mod implements.
2. **[MEDIUM · semantic_drift]** ELECTROCHARGED_DOT_TURNS (2) is implemented by neither engine: both apply a decaying 4-stack DoT/Poison whose duration is the amount, so the effect actually runs 4 turns for 10 total damage, while the constant, its C# mirror and the design study all describe 4x2=8 over 2 turns.
   - `tier0/constants.py:50-51 — `ELECTROCHARGED_DOT = 4` / `ELECTROCHARGED_DOT_TURNS = 2``
   - `tier0/engine/reactions.py:118-120 — `powers.apply_power(state, enemy, "dot", C.ELECTROCHARGED_DOT)` — no duration argument; _DOT_TURNS has zero readers in tier0/ or tier05/`
   - `tier0/engine/powers.py:119-134 — the dot ticks its full Amount then `fighter.powers["dot"] = dot - 1`, i.e. 4+3+2+1 = 10 damage over 4 turns`
   - `klee-mod/KleeCode/Powers/ReactionEffects.cs:253-260 — `PowerCmd.Apply<PoisonPower>(… ReactionConstants.ElectroChargedDot …)` — ElectroChargedDotTurns is declared and never read anywhere in klee-mod`
   - `klee-mod/KleeCode/Elements/ReactionTable.cs:45 — `public const int ElectroChargedDotTurns = 2; // ELECTROCHARGED_DOT_TURNS``
   - `tools/lint_constant_parity.py:96 — mirrors the pair, asserting parity between two numbers no engine consumes`
   - note: Constants: ELECTROCHARGED_DOT (4, live and correct on both sides), ELECTROCHARGED_DOT_TURNS (2, dead on both sides). The player-facing tooltip is honest ('a 4-damage decaying damage-over-time effect', KleeMod.cs:142-143), so the harm is to the design record and to the lint's coverage claim, not to the played number — hence medium. Retuning _DOT_TURNS would change nothing while the lint reports it green.
3. **[LOW · semantic_drift]** AMP_STACK_LIMIT (4.0) measures two different quantities: the sim's detector compares FINAL damage to base damage (so Strength, Vulnerable and Slow all count toward the 4x), while C# compares the Vaporize/Melt amplifier multiplier alone, so the two provenance logs fire on disjoint sets of hits.
   - `tier0/constants.py:570 — `AMP_STACK_LIMIT = 4.0         # single hit > 4x base damage -> log provenance``
   - `tier0/engine/effects.py:375-376 — `if base > 0 and dmg > base * C.AMP_STACK_LIMIT:` where `dmg` is post-Strength, post-amp, post-Vulnerable, post-Slow and already truncated`
   - `klee-mod/KleeCode/Elements/ReactionTable.cs:118-125 — `var mult = baseMult * (1m + pct / 100m); if (mult > ReactionConstants.AmpStackLimit) Log.Warn(...)` — amplifier multiplier only`
   - `klee-mod/KleeCode/Elements/ReactionTable.cs:106-108 — the doc claims 'This overload also owns the sim's amp-cap detector (AMP_STACK_LIMIT)'`
   - note: Concretely: upgraded Vermillion Pact Melt (1.75 × 2.25 = 3.9375) into a Vulnerable target is ~5.9x base in the sim → sim warns, C# does not; conversely a huge-Strength unamplified hit trips the sim and is invisible to C#. Diagnostic/log-only, no player-visible number, hence low. Verified clean in the same pass and NOT filed: AURA_DURATION_TURNS (tick site order bombs→auras matches, tier0/engine/combat.py:444-448 vs AuraPower.cs:179-186; Neuvillette extension mirrored at reactions.py:47 vs ElementalApplication.cs:227-229), OVERLOAD_SPLASH/OVERLOAD_WEAK (reactions.py:106-114 vs ReactionEffects.cs:229-251, block-ignoring + Weak on the reacted target both faithful), SUPERCONDUCT_VULN (reactions.py:115-117 vs ReactionEffects.cs:197-201 plus the triggering-hit x1.5 mirror at AuraPower.cs:100-122), CRYSTALLIZE_BLOCK (raw player block vs Unpowered GainBlock), VAPORIZE_MULT/MELT_MULT and the percent-boost formula (reactions.py:30-36 vs ReactionTable.cs:110-128), SHATTER_DAMAGE (effects.py:386-397 vs FrozenPower.cs:80-106, both unblockable direct HP after block, attack-gated, dead-target-gated), FROZEN_DAMAGE_MULT (combat.py:644 vs FrozenPower.cs:45-55).

### relic run-layer numbers (BURNING_BLOOD_HEAL, ancient-pool hooks incl. touch_of_orobas_klee) — CLEAN
*legs read: tier0/constants.py:495-497; tier0/engine/combat.py:815-835; tier05/model.py:615-625; tier05/content/relics.yaml:1-60,185-255; klee-mod/KleeCode/Relics/UpgradedStarterRelics.cs:1-140; tools/lint_constant_parity.py:67-89*

### rest-site policy fractions (REST_HEAL_FRACTION, REST_HEAL_THRESHOLD, REST_SMITH_DANGER, REST_PREFIGHT_HEAL_THRESHOLD) — CLEAN
*legs read: tier0/constants.py:739-751; tier05/model.py:100-145,470-480*

### reward slot rarity + nation weighting (RARITY_ODDS, SAME_NATION_REWARD_SHARE, NATION_WEIGHTS, REWARD_CARD_OFFERS) — 2 finding(s)
*legs read: tier0/constants.py:771-791; tier05/rewards.py:1-262; klee-mod/KleeCode/CompanionSlot.cs:1-175; klee-mod/KleeCode/Relics/PoundingSurprise.cs:85-113; tools/lint_constant_parity.py:113-120*
1. **[LOW · semantic_drift]** NATION_WEIGHTS is a per-nation TABLE read per card in the sim, but a single scalar applied uniformly to every card in C#; the lint mirrors only the "mondstadt" entry, so a future non-1.0 weight for fontaine or inazuma would diverge in play while the gate still passes.
   - `tier0/constants.py:782 — `NATION_WEIGHTS = {"mondstadt": 1.0, "fontaine": 1.0, "inazuma": 1.0}``
   - `tier05/rewards.py:181 — `w_all = [C.NATION_WEIGHTS.get(c.nation or "", 1.0) for c in cards]` (per-card lookup)`
   - `tier05/rewards.py:186-190 — `total = sum(w_all)` and `(1 - share) * w / total + ...` (per-card w)`
   - `klee-mod/KleeCode/CompanionSlot.cs:60 — `private const double NationWeight = 1.0;` (one scalar for all nations)`
   - `klee-mod/KleeCode/CompanionSlot.cs:155 — `var total = cards.Count * NationWeight;` (assumes uniform weight)`
   - `klee-mod/KleeCode/CompanionSlot.cs:157 — `(1.0 - SameNationShare) * NationWeight / total + ...``
   - note: Inert today (all three weights are 1.0) and disclosed in the C# doc comment ("every nation 1.0 today"). SAME_NATION_REWARD_SHARE (0.5) and RARITY_ODDS's cumulative walk are faithful: tier05/rewards.py:164-171 vs CompanionSlot.cs:111-117 produce the same 0.60/0.95 cutpoints, and the 0.05 rare tier is correctly the residual on both sides. REWARD_CARD_OFFERS=3 is consistent with the mod's reward text ("a fourth Companion choice", CompanionSlot.cs:49-50) since the companion is appended to the option list rather than granted alongside it (PoundingSurprise.cs:85-90 vs tier05/rewards.py:232-261).
2. **[LOW · sim_vs_csharp_divergence]** The empty-tier fallthrough ladder that RARITY_ODDS feeds is not the same function on the two sides: the sim's ladder only walks DOWN (rare->uncommon->common) and raises KeyError if the common tier is empty, while C# walks a Common roll UP to Uncommon.
   - `tier05/rewards.py:258-259 — `while rarity not in comps: rarity = {"rare": "uncommon", "uncommon": "common"}[rarity]` (a "common" miss is a KeyError, not a substitution)`
   - `tier05/rewards.py:235-236 — same ladder for the card offers`
   - `tier05/shop.py:93-94 — same ladder again for shop stock`
   - `klee-mod/KleeCode/CompanionSlot.cs:97 — `if (forcedRarity == null && !tiers.ContainsKey(rarity)) rarity = CardRarity.Uncommon;` (a Common roll with an empty Common tier is promoted upward)`
   - `klee-mod/KleeCode/CompanionSlot.cs:98 — `if (forcedRarity == null && !tiers.ContainsKey(rarity)) rarity = CardRarity.Common;``
   - note: Unreachable at today's roster (4-star companions fill the common tier on both sides), so no player-visible effect; filed because the two ladders are described as mirrors ("Ordinary rolls fall through when a tier is empty (tier0 roll_rewards)", CompanionSlot.cs:94-96) and are not. Forced-rarity behaviour DOES match: strict on both sides (rewards.py:251-256 vs CompanionSlot.cs:97-99), and the post-boss forced-Rare companion gate matches (PoundingSurprise.cs:106-109 vs rewards.py:250).

### run economy (GOLD_START, GOLD_INCOME, TREASURE_GOLD, SHOP_CARD_PRICE, SHOP_REMOVAL_PRICE, SHOP_REMOVAL_PRICE_STEP, SHOP_CARD_OFFERS, SHOP_RELIC_PRICE) — 1 finding(s)
*legs read: tier0/constants.py:680-724; tier05/shop.py:72-96,229-281; tier05/model.py:608-625; klee-mod/KleeCode/Klee.cs:70-90; klee-mod/KleeCode/Furina.cs:38-52; klee-mod/KleeCode/Kokomi.cs:58-72*
1. **[LOW · missing_leg]** GOLD_START is mirrored three times in C# as a property override rather than a const, so the parity lint's pattern never sees it and the three copies are ungated against tier0 and against each other.
   - `tier0/constants.py:681 — `GOLD_START = 99                  # StS default starting gold``
   - `klee-mod/KleeCode/Klee.cs:77 — `public override int StartingGold => 99;``
   - `klee-mod/KleeCode/Furina.cs:42 — `public override int StartingGold => 99;``
   - `klee-mod/KleeCode/Kokomi.cs:62 — `public override int StartingGold => 99;``
   - `tools/lint_constant_parity.py:284-286 — CONST_RE requires the `const` keyword; an expression-bodied property override does not match`
   - note: All four values agree at 99, so this is a coverage gap, not a drift. The rest of the group has no mod-side surface to diverge from: GOLD_INCOME ({N 10, E 25, B 100}, applied once per won fight at tier05/model.py:620), TREASURE_GOLD (40), SHOP_CARD_PRICE (60, tier05/shop.py:230), SHOP_REMOVAL_PRICE/STEP (75 + 25 per prior removal, tier05/shop.py:72-74), SHOP_CARD_OFFERS (3, tier05/shop.py:77-96) and SHOP_RELIC_PRICE (150) all model the base game's own economy, which the mod does not reimplement — verified by searching KleeCode for Gold/Price/Removal/Treasure call sites and finding only the three StartingGold overrides.

### shop companion channel (SHOP_COMPANION_SLOTS, SHOP_COMPANION_RARITY_ODDS, SHOP_COMPANION_PRICE) — 2 finding(s)
*legs read: tier0/constants.py:700-724; tier05/shop.py:99-180; tier05/exp_shop_companion_channel.py:1-40,60-140; klee-mod/KleeCode/Patches/MerchantCompanionSlots.cs:1-238; klee-mod/KleeCode/CompanionPool.cs:85-140; docs/teyvat-spire-design-principles.md:171-177*
1. **[HIGH · sim_vs_csharp_divergence]** SHOP_COMPANION_RARITY_ODDS is consumed for BOTH companion shop slots in the sim but only for slot 2 in the mod: the mod hard-wires slot 1 to Uncommon, so its home-nation slot can never offer a Rare (5-star) companion and never charges the Rare price band, while the sim rolls it Rare 12.5% of the time. The lint passes because the one compared value (0.875) matches.
   - `tier05/shop.py:151 — `for slot in range(C.SHOP_COMPANION_SLOTS):``
   - `tier05/shop.py:153 — `nation = home if slot == 0 else None``
   - `tier05/shop.py:154 — `rarity = _roll_companion_rarity(rng)` (rolled for EVERY slot, slot 1 included)`
   - `tier05/shop.py:129-133 — "It now designs four, so her slot 1 answers a Rare roll from her own nation."`
   - `tier05/shop.py:167 — `offers.append((loader.get_card(pick.id), C.SHOP_COMPANION_PRICE[rarity]))` (slot 1 can therefore be priced 150)`
   - `klee-mod/KleeCode/Patches/MerchantCompanionSlots.cs:125-126 — `AddSlot(__instance, player, entries, CardRarity.Uncommon, CompanionPool.HomeNation(player), slot: 1);` (literal rarity, no roll)`
   - note: Constants examined: SHOP_COMPANION_SLOTS (2), SHOP_COMPANION_RARITY_ODDS ({uncommon 0.875, rare 0.125}), SHOP_COMPANION_PRICE ({uncommon 75, rare 150}). In C# slot 1 can only reach Rare via AddSlot's failure ladder (MerchantCompanionSlots.cs:196-205), which logs a warning that it "crosses the R59 rarity floor and should be treated as a roster gap, not as intended behaviour" — i.e. the one path that produces a slot-1 Rare in the mod is the path the mod itself declares abnormal. The sim's P1 acceptance cell was measured in the rolled world.
2. **[LOW · missing_leg]** SHOP_COMPANION_PRICE has no C# constant at all — the mod defers to the base game's MerchantCardEntry.GetCost bands — so the parity gate (which is keyed on C# `const` declarations) cannot see a sim-side reprice of the channel whose whole balance story is its price.
   - `tier0/constants.py:720 — `SHOP_COMPANION_PRICE = {"uncommon": 75, "rare": 150}``
   - `tier05/shop.py:167 — sim charges from that dict`
   - `klee-mod/KleeCode/Patches/MerchantCompanionSlots.cs:42-50 — "PRICING IS NATIVE ... MerchantCardEntry.GetCost is 50/75/150 by rarity" (no mod-side constant declared)`
   - `tools/lint_constant_parity.py:284-286 — CONST_RE only matches declared C# `const` members, so a tier0 number with no C# const is outside the gate`
   - `tools/lint_constant_parity.py:196-267 — UNMIRRORED is keyed by C# constant name and cannot record a tier0-only number`
   - note: Values agree today (75/150) and the divergence-from-base ~15% colorless surcharge loss is recorded on both sides (MerchantCompanionSlots.cs:42-50 and tier0/constants.py:716-719). Filed only as a coverage gap, not a value mismatch.

### status_multipliers_weak_vulnerable_frail_block — 2 finding(s)
*legs read: tier0/constants.py:28-41 (WEAK_DEALT_MULT, VULNERABLE_TAKEN_MULT, FRAIL_BLOCK_MULT, COLOSSUS_TAKEN_MULT); tier0/engine/powers.py:26-134 (modify_damage_dealt/taken, modify_block_gained, on_turn_start metallicize); tier0/engine/refpowers.py:178-208 (gain_block chokepoint), 1030-1090; tier0/engine/effects.py:2255-2270 (garment attack block), 2540-2560 (kurage pulse block); klee-mod/KleeCode/Powers/SimDamagePipeline.cs:1-53; klee-mod/KleeCode/Powers/BombPower.cs:167*
1. **[HIGH · semantic_drift]** Power-sourced Block that the sim adds raw (exempt from FRAIL_BLOCK_MULT and Dexterity by design) is granted in C# as powered card/move-scoped Block at three sites — Metallicize, Kokomi's Ceremonial Garment attack rider, and the Kurage pulse — so in game those Block gains are cut 25% by Frail and inflated by Dexterity while the sim's are untouched.
   - `tier0/engine/powers.py:78-81 — modify_block_gained docstring: 'passive/power block (Metallicize, Crystallize, Solar Isotoma) is deliberately NOT reduced here'`
   - `tier0/engine/powers.py:119-120 — `if fighter.powers.get("metallicize", 0): fighter.block += fighter.powers["metallicize"]` (raw, bypasses the Frail/Dex funnel)`
   - `klee-mod/KleeCode/Powers/CompanionPowers.cs:528 — `await CreatureCmd.GainBlock(Owner, Amount, ValueProp.Move, null);` (MetallicizePower; Move = powered card/monster-move block, the exact predicate FrailPower and DexterityPower guard on)`
   - `tier0/engine/effects.py:2263-2264 — garment rider: `p.block += C.GARMENT_ATTACK_BLOCK` (raw)`
   - `klee-mod/KleeCode/Powers/KuragePowers.cs:358-360 — `await CreatureCmd.GainBlock(owner!, KokomiConstants.GarmentAttackBlock, ValueProp.Move, cardPlay);``
   - `tier0/engine/effects.py:2549-2552 — kurage pulse: `blk = C.KURAGE_PULSE_BLOCK + p.powers.get("kurage_ward", 0)` then `p.block += blk` (raw)`
   - note: Constants involved: FRAIL_BLOCK_MULT (0.75) plus the mirrored KokomiConstants.GarmentAttackBlock / KuragePulseBlock. Values match; the SCOPE the multiplier is applied at does not. Under Frail a Metallicize 3 is 3 in the sim and 2 in game; with Dexterity the divergence runs the other way. The mod's own Unpowered idiom at the sibling sites is what makes these three read as unintended.
2. **[MEDIUM · missing_leg]** WEAK_DEALT_MULT has no mirrored C# constant at all — it is consumed twice as the bare literal 0.75m — so the parity lint cannot see it and a sim-side retune of Weak would drift silently, unlike its sibling VULNERABLE_TAKEN_MULT which is a named mirrored const on the adjacent method.
   - `tier0/constants.py:28 — `WEAK_DEALT_MULT = 0.75        # Weak: -25% damage dealt``
   - `tier0/engine/powers.py:53 — `dmg *= C.WEAK_DEALT_MULT``
   - `klee-mod/KleeCode/Powers/SimDamagePipeline.cs:39 — `damage *= 0.75m;` (magic literal, in the method whose own doc at SimDamagePipeline.cs:24-26 says it 'mirrors tier0 constants WEAK_DEALT_MULT (0.75) and VULNERABLE_TAKEN_MULT (1.5)')`
   - `klee-mod/KleeCode/Powers/BombPower.cs:167 — `return hasRealWeak ? 1m : 0.75m;` (bomb suppression, the sim's `bomb_suppressed` branch at tier0/engine/powers.py:44-53, same rate, second literal)`
   - `klee-mod/KleeCode/Elements/ReactionTable.cs:39 — `public const decimal VulnerableTakenMult = 1.5m;` mirrored at tools/lint_constant_parity.py:109, showing the intended shape the Weak rate does not have`
   - note: Constants: WEAK_DEALT_MULT (0.75), VULNERABLE_TAKEN_MULT (1.5, mirrored and clean), FRAIL_BLOCK_MULT (0.75, no C# leg because the native power owns it). Behavioural parity is currently correct — both literals equal 0.75 — so this is medium, not high: the failure is that the gate is blind to it, exactly the class of silent drift lint_constant_parity.py:1-27 exists to prevent.

### turn_economy_constants — 1 finding(s)
*legs read: tier0/constants.py:1-60; tier0/engine/combat.py:440-520 (draw/energy/cap), 700-780 (inject overflow, _run_rounds), 790-850 (won/stall); tier0/engine/state.py:640-690 (draw + MAX_HAND_SIZE gate); tier0/engine/effects.py:475-495 (_add_token), 675-695; tier0/engine/refpowers.py:730-755, 1353; tier0/harness/axes.py:44,168,173*
1. **[LOW · semantic_drift]** MAX_CARDS_PER_TURN is documented as a detector that only *flags* a fight, but the implementation also breaks the play loop, so it is a hard play cap that truncates the player's turn at exactly 25 cards and can convert a legitimate long turn into a stall/loss.
   - `tier0/constants.py:25 — `MAX_CARDS_PER_TURN = 25   # beyond this the infinite detector flags the fight``
   - `tier0/engine/combat.py:507-509 — `if state.cards_played_this_turn >= C.MAX_CARDS_PER_TURN: state.emit("degeneracy", ...); break` (emits AND terminates the card loop)`
   - `tier0/engine/combat.py:758 — `while not state.over and state.turn < C.MAX_TURNS` with `won` computed at combat.py:823 from surviving enemies, so a truncated turn feeds the loss scoring`
   - note: Comment says 'beyond this'; the guard fires AT the value (>=), so 25 is the last playable card, not the first flagged one. No C# leg exists for this constant (correctly — it is sim instrumentation), so the drift is comment-vs-code only, hence low.
