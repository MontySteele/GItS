# S6 — Mutation Audit: Blind-Spot Report

> Surplus-dispatch-2 stream S6 (cloud). 2026-08-05. One Opus agent per module, each in an
> isolated git worktree: apply one small semantic mutation, run the module's targeted tests,
> then the full suite with -x for apparent survivors; revert; verify clean tree. Green
> measures what the tests CHECK — this measures what they'd CATCH.

**114 mutants across 17 modules · 68 killed · 46 SURVIVED · 0 not run.**
A surviving mutant is a behavior no test protects — the code could drift there silently.
Ranked below by how load-bearing the unprotected behavior is.
**Non-goal honored: zero tests were written** — that is a later, gated pass informed by this ranking.

---

## HIGH — core combat/economy numbers can drift silently (31)

### HIGH-1 · engine-combat (tier0/engine/combat.py) · `tier0/engine/combat.py:50 (grant_charged_kit, MAX_HAND_SIZE defer)`
- **Mutation that survived:** `if len(p.hand) >= C.MAX_HAND_SIZE: return` -> `if len(p.hand) > C.MAX_HAND_SIZE: return`
- **Unprotected behavior:** When the Burst meter fills while the hand is already at MAX_HAND_SIZE (10), the kit Burst card is supposed to be DEFERRED to the next check; no test asserts that boundary, so the engine can silently overfill the hand to 11 cards and hand the player a free extra Burst on the turn their hand is full. The docstring's stated contract ("Respects MAX_HAND_SIZE: a full hand defers the grant") is entirely unverified — no test in tier0/tests or tier05/tests constructs a full hand with a charged burst meter.

### HIGH-2 · engine-combat (tier0/engine/combat.py) · `tier0/engine/combat.py:758 (_run_rounds, stall cap)`
- **Mutation that survived:** `while not state.over and state.turn < C.MAX_TURNS:` -> `state.turn <= C.MAX_TURNS`
- **Unprotected behavior:** The MAX_TURNS = 30 stall cap ("hitting it counts as a loss") has no test pinning where the fight actually stops — a fight can run a 31st player turn and enemy round, so every turn-count-derived metric (fight_end turns, HP trajectory length, stall/loss classification, balance curves) can drift by a full round without any test noticing. Nothing asserts the boundary turn number or that a capped fight is recorded as a loss.

### HIGH-3 · engine-effects (tier0/engine/effects.py) · `tier0/engine/effects.py:443 (detonate_bombs)`
- **Mutation that survived:** dmg = bomb.damage + bonus + p.powers.get("bomb_damage_up", 0) -> dmg = bomb.damage + p.powers.get("bomb_damage_up", 0) (the per-detonation `bonus` argument is silently discarded)
- **Unprotected behavior:** The `bonus` rider on the detonate op is never asserted: Remote Detonator's printed `bonus: 2` per bomb (docs/klee-cards.yaml:104) and any bonus passed from move_bombs/other detonation callers can be deleted entirely and the whole suite stays green, so the uncommon's entire payoff over free Quick Fuse is unmeasured.

### HIGH-4 · engine-effects (tier0/engine/effects.py) · `tier0/engine/effects.py:2069 (prevent_damage_exhaust)`
- **Mutation that survived:** prevented = min(incoming, stacks) -> prevented = stacks (removes the clamp of prevention to the incoming damage)
- **Unprotected behavior:** Kokomi's prevention ward is only tested where incoming damage exceeds the ward's stacks, so nothing pins that prevention is capped by the hit; with the clamp gone combat.py:661-667 computes hp_loss = dmg - blocked - prevented as a NEGATIVE number and the player HEALS from being attacked by a small hit.

### HIGH-5 · engine-powers (tier0/engine/powers.py) · `/home/user/GItS/.claude/worktrees/wf_cc7f3b59-1a3-3/tier0/engine/powers.py:120`
- **Mutation that survived:** on_turn_start: `fighter.block += fighter.powers["metallicize"]` -> `fighter.block = fighter.powers["metallicize"]` (Metallicize overwrites block instead of adding to it)
- **Unprotected behavior:** Metallicize's turn-start block is never asserted to ADD to block the fighter already has: combat.py clears block just before this hook (player line 430, enemy line 597), so every test starts the hook from 0 and an overwrite is indistinguishable from an add. The divergence is exactly the cases where block survives the clear or is granted before the hook - Barricade-style retention via refpowers.should_clear_block(p), and block created between the clear and the hook (bomb detonation, _settle_phases, reactions.tick_auras). Under Barricade a Metallicize fighter would silently have its whole carried-over block replaced by the Metallicize amount, and no test would notice.

### HIGH-6 · engine-statuses (tier0/engine/statuses.py) · `tier0/engine/statuses.py:49`
- **Mutation that survived:** In make_status's Card(...): `rarity="basic"` -> `rarity="status"`
- **Unprotected behavior:** Which pools a status card belongs to is entirely unasserted: `filter: "status"` card selection matches on rarity == "status" (effects.py:1389, policy.py:262) while make_status stamps "basic", so status-filtered exhaust effects silently never remove an injected status - and flipping it so they DO is equally invisible to the full suite, despite draft.py pricing that effect at STATIC_STATUS_EXHAUST_VALUE = 1.5.

### HIGH-7 · engine-resources (tier0/engine/resources.py) · `tier0/engine/resources.py:290`
- **Mutation that survived:** spend_encore: `gain_burst(state, spent * C.BURST_PER_ENCORE_SPENT, "encore_spent")` -> `gain_burst(state, C.BURST_PER_ENCORE_SPENT, "encore_spent")` (drops the per-point multiplier on burst income, making it flat per spend EVENT)
- **Unprotected behavior:** Burst energy earned from spending Encore is never asserted at a per-point rate: a 5-Encore spend can silently grant 1 burst energy instead of 5 and every test still passes, so Furina's whole burst-charge rate off her main economy (kickoff §1) can drift by a multiplier undetected. Note the Fanfare grant on the SAME line-block IS asserted (killed mutant 4) - only the burst half of the pair is unguarded, including its `burst_income` amount in tier05/tests/test_burst_telemetry.py.

### HIGH-8 · engine-reactions (tier0/engine/reactions.py) · `tier0/engine/reactions.py:151`
- **Mutation that survived:** Dropped the per-stack multiplier on Catalytic Conversion burst: `resources.gain_burst(state, C.CATALYTIC_BURST_PER_REACTION * bonus, "catalytic")` -> `resources.gain_burst(state, C.CATALYTIC_BURST_PER_REACTION, "catalytic")`.
- **Unprotected behavior:** Catalytic Conversion's bonus burst energy is only ever exercised at one stack, so nothing asserts that a second stack of reaction_bonus_spark_energy doubles the burst per reaction (5 -> 10); the power stacks in practice because docs/klee-cards.yaml grants it via apply_power amount:1, so a second play would silently pay flat burst while still paying double sparks.

### HIGH-9 · engine-reactions (tier0/engine/reactions.py) · `tier0/engine/reactions.py:102`
- **Mutation that survived:** Turned the Crystallize Block gain from accumulation into assignment: `state.player.block += C.CRYSTALLIZE_BLOCK` -> `state.player.block = C.CRYSTALLIZE_BLOCK`.
- **Unprotected behavior:** Crystallize's Block is never asserted as additive on top of Block the player already has: no test triggers a geo reaction while the player is holding Block from a card or from a prior Crystallize, so a change that overwrites Block instead of adding to it (and even discards existing Block) passes the whole suite.

### HIGH-10 · engine-relics (tier0/engine/relics.py) · `tier0/engine/relics.py:224`
- **Mutation that survived:** conditional_power boundary flipped: `met = p.hp <= threshold * p.max_hp` -> `met = p.hp < threshold * p.max_hp`
- **Unprotected behavior:** Red Skull / conditional_power activating at EXACTLY the threshold HP (hp == threshold * max_hp, e.g. 40/80 at 0.5) is never exercised -- every test sits strictly below it (hp=30 or hp=35 of max 80), so the inclusive boundary could silently become exclusive and a player sitting on exactly half HP would lose their +3 strength.

### HIGH-11 · engine-state (tier0/engine/state.py, tier0/engine/refpowers.py) · `tier0/engine/state.py:663 (CombatState.draw)`
- **Mutation that survived:** `if len(p.hand) >= C.MAX_HAND_SIZE: return` -> `if len(p.hand) > C.MAX_HAND_SIZE: return` (off-by-one on the hand cap; draw can now push the hand to 11 cards)
- **Unprotected behavior:** The 10-card hand cap on CombatState.draw is asserted nowhere: a draw effect (or the turn-start hand draw) may overdraw one card past MAX_HAND_SIZE and no test in either suite notices, so every draw-heavy card silently gains up to one extra card per overflowing draw.

### HIGH-12 · engine-potions (tier0/engine/potions.py) · `tier0/engine/potions.py:126 (_intent_damage)`
- **Mutation that survived:** return max(0, int(dmg)) * times  ->  return max(0, int(dmg))  (drop the multi-hit multiplier)
- **Unprotected behavior:** Multi-hit telegraphs (intent "times" > 1) are counted as a single hit when the defensive potion policy estimates incoming damage, so the policy under-estimates a lethal multi-hit turn and lets the player die holding a block/blood potion; no test uses a times>1 intent in the potion path.

### HIGH-13 · engine-potions (tier0/engine/potions.py) · `tier0/engine/potions.py:121-122 (_intent_damage)`
- **Mutation that survived:** amount = intent["amount"] + intent.get("ramp", 0) * max(0, state.turn - intent.get("ramp_after", 0))  ->  amount = intent["amount"]  (drop the ramp term)
- **Unprotected behavior:** Ramping enemy attacks (ramp / ramp_after intents, e.g. late-turn boss scaling) are estimated at their base amount, so the defensive drink trigger and the big-hit threshold ignore all ramp growth; no test drives the potion policy with a ramping intent.

### HIGH-14 · engine-potions (tier0/engine/potions.py) · `tier0/engine/potions.py:186 (_try_defensive)`
- **Mutation that survived:** if p.hp - net > C.POTION_DEFENSIVE_MARGIN: return  ->  if p.hp - net >= C.POTION_DEFENSIVE_MARGIN: return
- **Unprotected behavior:** The exact boundary of the defensive-drink trigger is unasserted: with POTION_DEFENSIVE_MARGIN = 0, a telegraph that lands the player at exactly 0 HP (dead) no longer triggers a defensive potion, and any future margin tuning silently shifts by one HP.

### HIGH-15 · engine-potions (tier0/engine/potions.py) · `tier0/engine/potions.py:214 (_try_offensive)`
- **Mutation that survived:** big >= C.POTION_BIG_HIT_FRACTION * p.max_hp  ->  big >= C.POTION_BIG_HIT_FRACTION * p.hp  (operand swap max_hp -> current hp)
- **Unprotected behavior:** The big-hit threshold is only ever exercised with hp == max_hp, so nothing asserts it is measured against MAX HP rather than current HP; a wounded player would drink weak/fear/strength on much smaller telegraphs and the suite stays green.

### HIGH-16 · engine-potions (tier0/engine/potions.py) · `tier0/engine/potions.py:183 (_try_defensive)`
- **Mutation that survived:** net = estimate_incoming(state) - p.block  ->  net = estimate_incoming(state)  (drop the block subtraction)
- **Unprotected behavior:** Existing player Block is never taken into account in any test of the defensive trigger, so the policy can burn a block/blood potion against a telegraph that the player's already-standing Block would have fully absorbed.

### HIGH-17 · tier0-roster (tier0/roster.py, tier0/constants.py) · `tier0/constants.py:651`
- **Mutation that survived:** MAP_TREASURE_FLOOR = 8  ->  7  (off-by-one on the fixed all-Treasure floor; wiki floor 9)
- **Unprotected behavior:** The act map's fixed-floor LAYOUT is never pinned to its wiki-real index: every map test reads C.MAP_TREASURE_FLOOR back out of constants, so the treasure floor can slide to any index (here one floor earlier, and adjacent to the boss-side spacing the composition arithmetic assumes) with the whole run-layer economy shifting and no test failing.

### HIGH-18 · tier0-pilot (tier0/pilot/policy.py) · `tier0/pilot/policy.py:673 (_incoming_damage)`
- **Mutation that survived:** `total += int(per_hit) * intent.get("times", 1)` -> `total += int(per_hit)` (dropped the multi-hit multiplier from the incoming-damage forecast)
- **Unprotected behavior:** The pilot's incoming-damage forecast counts a multi-hit enemy intent as ONE hit and no test notices, so both the block-panic trigger and every Block valuation can under-read the real swing by up to 5x against the many multi-hit intents in the pools (act1 Peck 3x3, act3 Unload! 5x3, Furious Pummeling 4x4, Maelstrom 4x6, Multi-Claw 3x10) - the pilot blocks against the wrong number in exactly the fights that kill it.

### HIGH-19 · tier0-harness (tier0/harness/axes.py, tier0/harness/metrics.py, tier0/harness/runner.py) · `tier0/harness/axes.py:169 (_turns_to_own_peak)`
- **Mutation that survived:** A7 setup-tax threshold: `threshold = 0.7 * max(windows.values())` -> `0.5 * max(...)`
- **Unprotected behavior:** The 70%-of-own-peak definition of "when your plan comes online" is unasserted: A7 setup tax can be re-defined to any fraction of a config's own peak DPT window and every test still passes, so the whole A7 axis (and any constraint or band comparing against it) can silently shift for every character at once.

### HIGH-20 · tier05-draft (tier05/draft.py) · `tier05/draft.py:563 (_static_power.effect_power, all_enemies damage line)`
- **Mutation that survived:** `total += amt * times * STATIC_AOE_MULT` -> `total += amt * times` (dropped the AoE multiplier, reintroducing the v6 'AoE blindness' defect)
- **Unprotected behavior:** No test asserts that an `all_enemies` damage line is scored at STATIC_AOE_MULT (2.0x) its single-target value, so AoE cards can silently be repriced as single-target and the whole v6 swarm-damage fix could be deleted without any test noticing.

### HIGH-21 · tier05-draft (tier05/draft.py) · `tier05/draft.py:1243 (assigned_policy, late-run lean gate)`
- **Mutation that survived:** `if n >= DRAFT_LEAN_CAP:` -> `if n > DRAFT_LEAN_CAP:` (off-by-one on the deck size at which the v5 late-run discipline engages)
- **Unprotected behavior:** Nothing pins the exact deck size at which the lean gate starts filtering offers down to Powers/tempo/Block+rares, so the DRAFT_LEAN_CAP=15 boundary can drift by a card without a failing test - the gate could even be moved off by one screen and the measured lean15 deck-size/act-2-death result would silently change.

### HIGH-22 · tier05-model (tier05/model.py, tier05/acts.py) · `tier05/model.py:474`
- **Mutation that survived:** Removed the max_hp clamp on the rest-site heal: `hp = min(max_hp, hp + round(C.REST_HEAL_FRACTION * max_hp))` -> `hp = hp + round(C.REST_HEAL_FRACTION * max_hp)`
- **Unprotected behavior:** A campfire heal is never asserted to be capped at max HP, so a run can leave a rest above its maximum (heal is 30% of max and the pre-fight heal band reaches 90%, so overheal is reachable at almost every rest) and carry over-max HP into every later fight.

### HIGH-23 · tier05-model (tier05/model.py, tier05/acts.py) · `tier05/model.py:431`
- **Mutation that survived:** Dropped the gold debit on a shop relic purchase: removed `gold -= C.SHOP_RELIC_PRICE` while leaving the `gold >= C.SHOP_RELIC_PRICE` affordability check and the 150g purchase-log entry intact
- **Unprotected behavior:** Shop relics on grant_relics runs are effectively free: no test asserts that gold actually drops by SHOP_RELIC_PRICE (150) after a relic is bought, even though the purchase log still claims the price was paid.

### HIGH-24 · tier05-metrics (tier05/run_metrics.py, tier05/stats.py) · `tier05/run_metrics.py:150`
- **Mutation that survived:** act_funnel() reached boundary off-by-one: `r.death_node >= a * tpl` -> `r.death_node > a * tpl` (a run that dies on the exact first floor of act `a` is no longer counted as having reached that act)
- **Unprotected behavior:** A run that dies on the very first floor of an act still counts as having REACHED that act, and no test pins that boundary — reached/reached_rate for every act can be off by the entire cohort of runs that died on floor 0 of an act without any test noticing.

### HIGH-25 · tier05-metrics (tier05/run_metrics.py, tier05/stats.py) · `tier05/run_metrics.py:120`
- **Mutation that survived:** route_profile() §11 elite target band widened: `sum(v for k, v in dist.items() if 1 <= k <= 4)` -> `if 1 <= k <= 5` (acts with 5 elites now score as in-band)
- **Unprotected behavior:** The §11 routing acceptance range is 1-4 elites per act, but nothing asserts that in_target_band actually excludes acts with 5 or more elites — the band literal can drift wider and the routing instrument will keep reporting a healthy in-band share for a policy that overloads acts with elites.

### HIGH-26 · tier05-economy (tier05/events.py, tier05/rewards.py, tier05/shop.py) · `tier05/events.py:378`
- **Mutation that survived:** resolve(): deleted the clamp `st.hp = min(st.hp, st.max_hp)` that follows `st.max_hp = max(1, st.max_hp + opt["max_hp"])`
- **Unprotected behavior:** An event option that LOWERS max HP (unrest_site -8, tablet_of_truth ladder -3/-6/-12/-24) never re-clips current HP, so a run can leave the event with hp above max_hp permanently (verified: hp 70 / max_hp 62) — free effective health that inflates every survivability number and is never asserted for any max-HP-cost option.

### HIGH-27 · tier05-economy (tier05/events.py, tier05/rewards.py, tier05/shop.py) · `tier05/events.py:309`
- **Mutation that survived:** available(): `if st.hp + min(0, opt.get("hp", 0)) <= 0:` -> `if st.hp + min(0, opt.get("hp", 0)) < 0:` (lethal-option guard weakened by one HP)
- **Unprotected behavior:** The rule that an event option which would take the run to exactly 0 HP is illegal is never asserted at the boundary: with the guard at `< 0` the exactly-lethal option becomes selectable and the greedy policy actually takes it (colossal_flower "Reach Deeper" -5 at hp 5, colossal_flower_2 -6 at hp 6, whispering_hollow "Hug the Tree" -9 at hp 9), killing the run in an event room the model is documented to never let you die in.

### HIGH-28 · tier05-route (tier05/route.py, tier05/maps.py, tier05/cells.py) · `tier05/route.py:100`
- **Mutation that survived:** In _make_value, the elite repulsion constant: `return -8.0` -> `return -1.0` (elites stay repellent but only weakly when elite_ok is False)
- **Unprotected behavior:** Only the SIGN of the elite-avoidance penalty is protected, never its magnitude: shrinking it from -8 to -1 leaves a hurt hunter and a cautious run walking a different lane on ~15% of maps (44/300 at hp_frac<=0.45, 38/300 for cautious), visiting different shops, rests and unknown rooms — so gold and event exposure drift — while the elite count, the only thing the routing tests measure, stays byte-identical.

### HIGH-29 · tier05-route (tier05/route.py, tier05/maps.py, tier05/cells.py) · `tier05/route.py:128`
- **Mutation that survived:** Hard per-act elite cap in hunter: `elite_ok = st.hp_frac >= bar and st.elites_taken < 4` -> `... and st.elites_taken < 3`
- **Unprotected behavior:** The top of the declared 1-4 elites-per-act range is unasserted: lowering the cap to 3 wipes out every four-elite run on a healthy deck (42 of 300 maps drop from 4 elites to 3, mean 2.26 -> 2.17) and the suite stays green, because test_hunter_hits_the_player_behaviour_target only checks that 1+2+3+4 together exceed 90% of runs and that the mean sits within +/-0.35 of 2.5 — neither notices that the 4-elite bucket has emptied.

### HIGH-30 · tier05-route (tier05/route.py, tier05/maps.py, tier05/cells.py) · `tier05/maps.py:131`
- **Mutation that survived:** Lateral column bound in path carving: `steps = [c for c in (col - 1, col, col + 1) if 0 <= c < width]` -> `... if 0 <= c < width - 1`
- **Unprotected behavior:** Nothing asserts that a generated map actually USES its full board: clipping one column off the carve narrows every floor above the first to 5 usable lanes and cuts elite ROOMS per map from 3.85 to 3.43 (-11%), yet the shape tests only bound width from above (max width <= MAP_MAX_FLOOR_WIDTH) and floor 1 still shows 6 columns from the spread starts, so the map silently shrinks under a green suite — this is the exact 'connectivity, not room count, is the binding constraint' failure mode the generator's own docstring says it was rewritten to prevent.

### HIGH-31 · tier05-route (tier05/route.py, tier05/maps.py, tier05/cells.py) · `tier05/cells.py:228`
- **Mutation that survived:** Act-1 clear rate in Cell.arm(): `"act1": sum(r.acts_completed >= 1 for r in results) / n` -> `sum(r.acts_completed > 1 for r in results) / n`
- **Unprotected behavior:** Cell.arm() — THE consolidated summary row that every exp_*.py script reports its headline numbers from — has no test whatsoever, so the act-1 clear rate can be silently redefined as 'cleared act 2 or more' (and win / acts / decksize / fights are equally unguarded) while all 1516 tests pass; the in-code comment 'acts_completed counts boss wins, so >= 1 IS the act-1 clear' is the only thing pinning the definition.

---

## MEDIUM — edge-case behavior unprotected (13)

### MEDIUM-1 · engine-effects (tier0/engine/effects.py) · `tier0/engine/effects.py:485 (_add_token)`
- **Mutation that survived:** if zone == "hand" and len(state.player.hand) < C.MAX_HAND_SIZE: -> <= C.MAX_HAND_SIZE (created cards may push the hand to 11)
- **Unprotected behavior:** The hand-size ceiling on CREATED cards is never asserted: every token/generator/conscript-create path (add_card, generate_from_pool, guest star, copy-in-hand) can overflow MAX_HAND_SIZE by one instead of diverting to the discard pile, so the 'created card goes to discard when hand is full' rule is unprotected.

### MEDIUM-2 · engine-powers (tier0/engine/powers.py) · `/home/user/GItS/.claude/worktrees/wf_cc7f3b59-1a3-3/tier0/engine/powers.py:171`
- **Mutation that survived:** apply_power: `new = min(new, max_stacks)` -> `new = min(new, max_stacks + 1)` (stack cap off by one)
- **Unprotected behavior:** The sheet-v0.2 stack cap in apply_power is never exercised as an actual clamp: no test applies a capped power twice and asserts the total stops at the cap. The only shipped row that passes max_stacks is Kokomi's vigil_of_the_deep (prevent_exhaust_ward, amount 6 / max_stacks 6, docs/kokomi-cards.yaml:544) and it uses the single-application encoding where cap == amount, so one application lands at 6 either way. A second application should stay 6 but the mutant reaches 7, and both the targeted files (including test_kokomi.py) and the full suite pass. The upgrade path that bumps the cap (tier0/content/upgrades.py:469-473) is checked only as data shape (test_kokomi.py::682, test_furina_sheet.py::729), never as engine behavior - test_furina_sheet.py:735 itself says the branch is unexercised by live content.

### MEDIUM-3 · engine-statuses (tier0/engine/statuses.py) · `tier0/engine/statuses.py:48`
- **Mutation that survived:** In make_status's Card(...): `cost=0` -> `cost=1`
- **Unprotected behavior:** Injected status cards are supposed to cost 0, but nothing asserts it - combat.card_playable short-circuits on `type == "status"` (combat.py:103) before any energy check, so the cost field could drift to any value and no test, energy accounting, or draft valuation would notice.

### MEDIUM-4 · engine-statuses (tier0/engine/statuses.py) · `tier0/engine/statuses.py:49`
- **Mutation that survived:** In make_status's Card(...): `tags=list(spec.get("tags", []))` -> `tags=spec.get("tags", [])` (dropped the defensive copy, so every injected copy aliases the module-level _SPECS list)
- **Unprotected behavior:** The per-instance independence of a status card's tag list is unprotected: nothing asserts that two injected Dazed cards hold distinct tag lists, so any in-combat tag mutation would leak across every copy and permanently corrupt the _SPECS template for the rest of the process (the freshness test only checks Card object identity, never the mutable fields inside it).

### MEDIUM-5 · engine-relics (tier0/engine/relics.py) · `tier0/engine/relics.py:266`
- **Mutation that survived:** card_name_damage_bonus name-match dropped: `if sub in card.id or sub in (card.name or ""):` -> `if sub in card.id:`
- **Unprotected behavior:** The card NAME half of the card_name_damage_bonus match is never exercised: both tests use card id 'pommel_strike'/'thwack' and the only shipped relic (tier05/content/relics.yaml:79) uses substring 'strike' which already hits the id, so a relic whose substring appears only in a card's display name (different casing, spaces, or an id that was renamed away from the name) would silently grant +0 damage instead of its flat rider.

### MEDIUM-6 · engine-potions (tier0/engine/potions.py) · `tier0/engine/potions.py:208 (_try_offensive)`
- **Mutation that survived:** if 0 < e.hp <= C.POTION_FIRE_DAMAGE  ->  if 0 < e.hp < C.POTION_FIRE_DAMAGE  (off-by-one on the fire kill range)
- **Unprotected behavior:** An enemy sitting at exactly POTION_FIRE_DAMAGE (20) HP is the boundary case for "fire_potion closes a kill" and no test covers it; the kill-range bound can slip by one without the suite noticing (the existing test uses POTION_FIRE_DAMAGE - 5).

### MEDIUM-7 · engine-potions (tier0/engine/potions.py) · `tier0/engine/potions.py:174 (try_use_potions)`
- **Mutation that survived:** if p.node_kind in ("elite", "boss"):  ->  if p.node_kind in ("elite", "boss", ""):  (widen the offensive gate to the default/battery node context)
- **Unprotected behavior:** The node_kind gate is only asserted for the literal "normal" string; the default/battery context "" (what loader-built and non-fight players carry) is never checked, so widening the offensive branch to the frozen-battery context passes the whole suite.

### MEDIUM-8 · tier0-roster (tier0/roster.py, tier0/constants.py) · `tier0/roster.py:144`
- **Mutation that survived:** IDS: tuple[str, ...] = tuple(c.id for c in ROSTER)  ->  tuple(sorted(c.id for c in ROSTER))  (ship order klee,furina,kokomi becomes alphabetical furina,klee,kokomi)
- **Unprotected behavior:** The roster's declared ship ORDER is documented as stable and meaningful ('Append; never reorder' -- several reports print the roster in it), but nothing asserts roster.IDS equals the declared ROSTER order, so a reorder silently permutes every roster-ordered report and every roster.IDS-parametrized sweep without failing anything.

### MEDIUM-9 · tier0-harness (tier0/harness/axes.py, tier0/harness/metrics.py, tier0/harness/runner.py) · `tier0/harness/metrics.py:199 (extract)`
- **Mutation that survived:** control-uptime denominator: `enemy_actions = total_intents + sleeps` -> `enemy_actions = total_intents` (drop the sleep-skip term)
- **Unprotected behavior:** Scripted enemy self-sleeps are supposed to count as enemy actions in the §2.2a control-uptime denominator, but nothing asserts it: dropping them inflates both summarize()['control_uptime'] and the per-fight SUPPORT_CARRY detector against the CONTROL_UPTIME_CARRY=0.40 threshold, so a sleep-heavy encounter could be mislabeled as companion-carried with no test noticing.

### MEDIUM-10 · tier0-harness (tier0/harness/axes.py, tier0/harness/metrics.py, tier0/harness/runner.py) · `tier0/harness/runner.py:99-100 (score_config)`
- **Mutation that survived:** pressure_delta operands swapped: `punisher_winrate - attrition_winrate` -> `attrition_winrate - punisher_winrate` (sign flip on the reported matchup-texture delta)
- **Unprotected behavior:** The SIGN of pressure_delta is unprotected - the only test touching it (tier0/tests/test_axes.py:36) asserts two runs agree with each other, never that a positive value means the config does better against punisher than against attrition, so the reported burst-vs-attrition texture could be printed backwards on every scorecard.

### MEDIUM-11 · tier05-draft (tier05/draft.py) · `tier05/draft.py:1564 (draft_regret, regret comparison)`
- **Mutation that survived:** `if any(v > picked_score + 1.0 ...)` -> `if any(v > picked_score ...)` (removed the additive 'full point' regret margin)
- **Unprotected behavior:** The documented rule that a decision only regrets when another offer outscores the pick by a FULL POINT is unasserted; the margin can be removed entirely, turning draft_regret from a coarse instrument into a near-always-true counter, and no test catches it.

### MEDIUM-12 · tier05-model (tier05/model.py, tier05/acts.py) · `tier05/model.py:146`
- **Mutation that survived:** Off-by-one on the rest-site defense quota: `(n_block - 1) / max(1, len(deck) - 1) >= C.DRAFT_BLOCK_DENSITY_MIN` -> `n_block / max(1, len(deck) - 1) >= C.DRAFT_BLOCK_DENSITY_MIN`
- **Unprotected behavior:** The "only thin a basic block card if the defense quota survives" rule is never checked post-removal — nothing pins that the quota is evaluated on the deck AS IT WOULD BE after the cut, so a rest can drop block density below DRAFT_BLOCK_DENSITY_MIN.

### MEDIUM-13 · tier05-economy (tier05/events.py, tier05/rewards.py, tier05/shop.py) · `tier05/rewards.py:148`
- **Mutation that survived:** roll_banner(): `if len(roster) <= C.BANNER_FEATURED_SLOTS:` -> `if len(roster) < C.BANNER_FEATURED_SLOTS:` (off-by-one on the feature-all-vs-sample boundary)
- **Unprotected behavior:** A nation whose 5-star roster is exactly BANNER_FEATURED_SLOTS long (mondstadt today: 3 of 3) must feature all of them WITHOUT consuming rng; no test pins that boundary, so pushing it through rng.sample yields an identical banner set but advances the run's single Random (verified: banner size 8 both ways, next rng.random() 0.6509 -> 0.8213), silently desynchronising every downstream roll of every seeded run against archived numbers.

---

## LOW — cosmetic/telemetry (2)

### LOW-1 · engine-state (tier0/engine/state.py, tier0/engine/refpowers.py) · `tier0/engine/state.py:646 (CombatState.shuffle_discard_into_draw)`
- **Mutation that survived:** `draw_pile = discard_pile + draw_pile` -> `draw_pile = draw_pile + discard_pile` (swapped concatenation operands, i.e. reshuffled discard goes to the BOTTOM instead of the top)
- **Unprotected behavior:** Nothing pins the position the reshuffled discard pile is spliced into the draw pile — but note this is very likely an EQUIVALENT mutant: all three call sites (state.py:661, effects.py:2061, effects.py:2089) guard with `if not p.draw_pile`, so draw_pile is always empty when this runs and both orderings produce identical decks. Real exposure is only to a future caller that reshuffles with cards still in the draw pile.

### LOW-2 · tier0-pilot (tier0/pilot/policy.py) · `tier0/pilot/policy.py:338 (_scaling_value, self apply_power cap)`
- **Mutation that survived:** `val += min(amount, 6) * 3` -> `val += min(amount, 7) * 3` (off-by-one on the per-power stacking cap)
- **Unprotected behavior:** The per-power cap of 6 on self-buff scaling value is never exercised by any test - and a YAML scan shows no shipped card grants 6+ self power stacks or a formulaic (X / hand_size) self stack, so the cap is currently unreachable content-wise; the day a big-stack or X-amount self power ships, a wrong or missing cap will silently let percent-stack powers (Vermillion Pact, Durin) dwarf every other scorer term with nothing failing.

---

## What IS protected (kill table)

| module | mutant | killed by |
|---|---|---|
| engine-combat (tier0/engine/combat.py) | tier0/engine/combat.py:644 (_enemy_turn, frozen attack damage) — `dmg *= C.FROZEN_DAMAGE_MULT` -> `dmg *= 1.0` (drop the Frozen v2 -50% multiplier) | `tier0/tests/test_reactions.py::test_frozen_soft_control` |
| engine-combat (tier0/engine/combat.py) | tier0/engine/combat.py:172 (card_cost, spark free-attack gate) — `state.player.sparks >= spark_threshold(state)` -> `>` (off-by-one the free-attack spark threshold) | `tier0/tests/test_klee.py::test_sparks_make_attack_free` |
| engine-combat (tier0/engine/combat.py) | tier0/engine/combat.py:236 (play_card, Spotlight first-play window) — `if state.spotlighted_cards_this_turn == 1:` -> `>= 1` (first-Spotlighted-play window becomes every play) | `tier0/tests/test_furina_sheet.py::test_supporting_cast_draws_on_first_spotlighted_play_only` |
| engine-combat (tier0/engine/combat.py) | tier0/engine/combat.py:78 (_settle_phases, boss phase-revive threshold) — `while e.phases and e.hp <= 0:` -> `e.hp < 0` (an enemy landing on exactly 0 HP dies instead of phasing) | `tier0/tests/test_multiact_ops.py::test_phase_down_revives_with_fresh_bar_moves_and_cleared_powers` |
| engine-effects (tier0/engine/effects.py) | tier0/engine/effects.py:256 (_pick_targets) — return [min(living, key=lambda e: e.hp)] -> return [max(living, key=lambda e: e.hp)] (single-target aim flips  | `tier0/tests/test_silent.py::test_silent_frontload_not_above_baseline (assert A1_frontload 3.034 <= 3.0)` |
| engine-effects (tier0/engine/effects.py) | tier0/engine/effects.py:373 (deal_damage_to_enemy, Slow amp) — dmg *= 1 + enemy.slow * state.cards_played_this_turn / 100.0 -> dmg *= 1 + enemy.slow / 100.0 (drops the per-c | `tier0/tests/test_multiact_ops.py::test_slow_amps_attack_damage_per_card_played_this_turn` |
| engine-effects (tier0/engine/effects.py) | tier0/engine/effects.py:783 (_deploy_salon_members) — if len(p.salon) >= salon_slots(p): -> if len(p.salon) > salon_slots(p): (stage holds one member over cap befor | `tier0/tests/test_curtain_call.py::test_stagehands_pay_on_the_final_bow_not_the_deploy` |
| engine-powers (tier0/engine/powers.py) | /home/user/GItS/.claude/worktrees/wf_cc7f3b59-1a3-3/tier0/engine/powers.py:39 — _floor: `return dmg if dmg > 0 else 0.0` -> `return dmg` (remove the zero clamp on the damage chain) | `tier0/tests/test_refpowers.py::test_mangle_cannot_drive_an_intent_below_zero_damage` |
| engine-powers (tier0/engine/powers.py) | /home/user/GItS/.claude/worktrees/wf_cc7f3b59-1a3-3/tier0/engine/powers.py:52 — modify_damage_dealt: `attacker.powers.get("weak", 0) > 0` -> `> 1` (one stack of Weak stops reducing damage) | `tier0/tests/test_effects.py::test_weak_reduces_damage` |
| engine-powers (tier0/engine/powers.py) | /home/user/GItS/.claude/worktrees/wf_cc7f3b59-1a3-3/tier0/engine/powers.py:114 — modify_block_gained: `int(amount * C.FRAIL_BLOCK_MULT)` -> `round(amount * C.FRAIL_BLOCK_MULT)` (Frail block r | `tier0/tests/test_frail.py::test_frail_helper_reduces_amount` |
| engine-powers (tier0/engine/powers.py) | /home/user/GItS/.claude/worktrees/wf_cc7f3b59-1a3-3/tier0/engine/powers.py:104 — modify_block_gained: `amount = max(0, amount + dex)` -> `amount = amount + dex` (drop the zero clamp on negati | `tier0/tests/test_si_effects.py::test_negative_dexterity_floors_at_zero_block` |
| engine-statuses (tier0/engine/statuses.py) | tier0/engine/statuses.py:28-29 — Swapped the two end-of-turn damage values in _SPECS: `"burn": {..., "eot": 2}, "wither": {..., "eot": 3}` -> ` | `tier0/tests/test_multiact_ops.py::test_status_eot_damage_eats_block_first (assert p.block == 7, got 8)` |
| engine-statuses (tier0/engine/statuses.py) | tier0/engine/statuses.py:30 — `"toxic": {"name": "Toxic", "draw": 2}` -> `"draw": 1` (halved the on-draw HP loss) | `tier0/tests/test_multiact_ops.py::test_toxic_costs_hp_on_draw (assert st.player.hp == hp0 - 2, got hp 79)` |
| engine-statuses (tier0/engine/statuses.py) | tier0/engine/statuses.py:25 — `"dazed": {"name": "Dazed", "tags": ["ethereal"]}` -> `"tags": []` (dropped the ethereal tag) | `tier0/tests/test_multiact_ops.py::test_burn_and_wither_tick_at_turn_end_blockable_dazed_is_ethereal (assert any(c.id == "status_dazed" for c in p.exhaust_pile))` |
| engine-resources (tier0/engine/resources.py) | tier0/engine/resources.py:114 — _decay_amount: `return max(1, round(p.fanfare * C.FANFARE_DECAY_FRACTION))` -> `return max(0, round(...))` (re | `tier0/tests/test_furina.py::test_proportional_decay_takes_its_cut_and_still_clamps_at_the_floor` |
| engine-resources (tier0/engine/resources.py) | tier0/engine/resources.py:133 — decay_fanfare: `if not p.fanfare_cap or state.turn < 2:` -> `state.turn < 1` (off-by-one on the "decay only fr | `tier0/tests/test_furina.py::test_fanfare_decays_each_turn_but_never_below_the_floor` |
| engine-resources (tier0/engine/resources.py) | tier0/engine/resources.py:80 — gain_fanfare: `p.fanfare = min(p.fanfare_cap, p.fanfare + n)` -> `p.fanfare = p.fanfare + n` (removes the cap  | `tier0/tests/test_a7_port.py::test_a_gain_that_lands_entirely_at_the_cap_is_not_a_change` |
| engine-resources (tier0/engine/resources.py) | tier0/engine/resources.py:288 — spend_encore: `gain_fanfare(state, spent * C.FANFARE_PER_ENCORE_SPENT, "encore_spent")` -> drops the `spent *` | `tier0/tests/test_fanfare_rework.py::test_slip_backstage_converts_the_buffer_and_prints_fanfare_for_it` |
| engine-resources (tier0/engine/resources.py) | tier0/engine/resources.py:310 — spend_encore: `if n and state.encore_spend_draws_this_turn == 0:` -> `if n:` (removes the once-per-turn latch  | `tier0/tests/test_curtain_call.py::test_gallery_stirs_draws_on_first_spend_only` |
| engine-resources (tier0/engine/resources.py) | tier0/engine/resources.py:238 — readable: `return max(0, player.fanfare)` -> `return player.fanfare` (removes the zero clamp at the single rea | `tier0/tests/test_fanfare_rework.py::test_every_reader_clamps_at_zero[-25]` |
| engine-resources (tier0/engine/resources.py) | tier0/engine/resources.py:165 — gain_fanfare_floor: deleted `p.fanfare_cap += n` (floor grant no longer raises the ceiling alongside the floor | `tier0/tests/test_furina.py::test_a_floor_grant_raises_floor_cap_and_current_together` |
| engine-resources (tier0/engine/resources.py) | tier0/engine/resources.py:218 — drop_fanfare_to_floor: `p.fanfare = max(p.fanfare_floor, min(p.fanfare, p.fanfare_floor))` -> `min(p.fanfare,  | `tier0/tests/test_fanfare_rework.py::test_the_hyperbeam_reads_the_meter_then_crashes_it` |
| engine-resources (tier0/engine/resources.py) | tier0/engine/resources.py:260 — note_fanfare_read: `at_cap=p.fanfare >= p.fanfare_cap` -> `at_cap=p.fanfare > p.fanfare_cap` (saturation gate  | `tier0/tests/test_furina.py::test_every_read_is_instrumented_at_the_moment_it_reads` |
| engine-reactions (tier0/engine/reactions.py) | tier0/engine/reactions.py:31 — In _amp_mult, swapped the amplifier selector: `base = C.VAPORIZE_MULT if name == "vaporize" else C.MELT_MULT`  | `tier0/tests/test_reactions.py::test_vaporize_amplifies_one_hit_and_consumes_aura (assert 17.5 == 10 * 1.5)` |
| engine-reactions (tier0/engine/reactions.py) | tier0/engine/reactions.py:65 — In tick_auras, off-by-one on the expiry bound: `if e.aura_turns_left <= 0:` -> `if e.aura_turns_left < 0:`, gi | `tier0/tests/test_reactions.py::test_aura_expiry_logged_as_waste (aura still 'pyro' after AURA_DURATION_TURNS ticks)` |
| engine-reactions (tier0/engine/reactions.py) | tier0/engine/reactions.py:99 — In the swirl branch of _react, swapped the spread element operand: `apply_aura(state, other, aura)` -> `apply_ | `tier0/tests/test_reactions.py::test_swirl_copies_aura_to_all` |
| engine-reactions (tier0/engine/reactions.py) | tier0/engine/reactions.py:141 — Loosened the Cross Examination first-reaction gate: `if n and state.reactions_this_turn == 1:` -> `if n and st | `tier0/tests/test_curtain_call.py::test_cross_examination_debuffs_first_reaction_target_once` |
| engine-relics (tier0/engine/relics.py) | tier0/engine/relics.py:168 — _heal overheal clamp removed: `healed = min(amount, p.max_hp - p.hp)` -> `healed = amount` | `tier0/tests/test_relics_combat_start.py::test_blood_vial_heal_capped_at_max_hp` |
| engine-relics (tier0/engine/relics.py) | tier0/engine/relics.py:190 — every_n_turns_energy cadence off-by-one: `if n > 0 and turn % n == 0:` -> `if n > 0 and (turn + 1) % n == 0:` | `tier0/tests/test_relics_dynamic.py::test_happy_flower_energy_only_on_turn_multiples_of_three` |
| engine-relics (tier0/engine/relics.py) | tier0/engine/relics.py:156 — combat_start_spark economy gate removed: `if amt > 0 and "spark_on_detonation" in p.relic_hooks:` -> `if amt > | `tier0/tests/test_relics_combat_start.py::test_combat_start_spark_is_inert_without_the_spark_economy` |
| engine-relics (tier0/engine/relics.py) | tier0/engine/relics.py:243 — on_first_hp_loss_draw once-per-combat guard removed: `if not p.relic_effects or p.first_hp_loss_fired:` -> `if | `tier0/tests/test_relics_dynamic.py::test_centennial_puzzle_draws_three_on_first_hp_loss_only` |
| engine-relics (tier0/engine/relics.py) | tier0/engine/relics.py:130 — combat_start_enemy_power targeting narrowed: `for enemy in state.living_enemies:` -> `for enemy in state.livin | `tier0/tests/test_relics_combat_start.py::test_bag_of_marbles_vulnerable_all_enemies` |
| engine-relics (tier0/engine/relics.py) | tier0/engine/relics.py:229 — conditional_power stacking clobbers existing stacks: `p.powers[power] = p.powers.get(power, 0) + delta` -> `p. | `tier0/tests/test_relics_dynamic.py::test_red_skull_strength_tracks_hp_threshold` |
| engine-state (tier0/engine/state.py, tier0/engine/refpowers.py) | tier0/engine/state.py:498 (Enemy.ramped_amount) — `amount += ramp * max(0, elapsed)` -> `amount += ramp * elapsed` (removed the negative-elapsed clamp, so a ram | `tier0/tests/test_multiact_ops.py::test_unphased_ramp_still_counts_from_combat_start` |
| engine-state (tier0/engine/state.py, tier0/engine/refpowers.py) | tier0/engine/refpowers.py:217 (_apply_unmovable) — `if state.block_gain_card_plays_this_turn >= n: return amount` -> `> n` (Unmovable's per-turn doubling allowan | `tier0/tests/test_refpowers.py::test_unmovable_doubles_only_card_block_and_only_n_plays_per_turn` |
| engine-state (tier0/engine/state.py, tier0/engine/refpowers.py) | tier0/engine/refpowers.py:1188 (player_turn_start_late) — `if p.powers.get("plating", 0) and state.turn != 1:` -> `if p.powers.get("plating", 0):` (dropped the PlayerCo | `tier0/tests/test_refpowers.py::test_plating_blocks_at_turn_end_and_skips_the_turn_one_decrement` |
| engine-state (tier0/engine/state.py, tier0/engine/refpowers.py) | tier0/engine/refpowers.py:1041 (modify_damage_taken, Cruelty) — `dmg *= (C.VULNERABLE_TAKEN_MULT + cruelty / 100.0) / C.VULNERABLE_TAKEN_MULT` -> `dmg *= (C.VULNERABLE_TAKEN_ | `tier0/tests/test_refpowers.py::test_cruelty_adds_percentage_points_to_vulnerable_only` |
| engine-state (tier0/engine/state.py, tier0/engine/refpowers.py) | tier0/engine/refpowers.py:738 (after_card_played, Juggling) — `if n and state.attacks_played_this_turn == C.JUGGLING_ATTACK_TRIGGER:` -> `>= C.JUGGLING_ATTACK_TRIGGER` (Jug | `tier0/tests/test_refpowers.py::test_juggling_fires_on_exactly_the_third_attack` |
| engine-potions (tier0/engine/potions.py) | tier0/engine/potions.py:74 (apply_potion, block_potion branch) — p.block += C.POTION_BLOCK  ->  p.block += C.POTION_BLOCK - 1  (control mutant, to prove the harness kills) | `tier0/tests/test_potion_effects.py::test_block_potion_gains_twelve_block (assert 11 == 12)` |
| tier0-roster (tier0/roster.py, tier0/constants.py) | tier0/roster.py:139 — kokomi archetypes=("priest", "commander", "assist")  ->  ("commander", "priest", "assist") | `tier0/tests/test_epoch1_fixes.py::test_kokomis_archetypes_are_the_sheets` |
| tier0-roster (tier0/roster.py, tier0/constants.py) | tier0/constants.py:301 — SALON_DRY_DAMAGE_MULT = 0.75  ->  1.0  (removes the no-Encore haircut on Salon member ticks) | `tier0/tests/test_furina_sheet.py::test_sheet_comments_match_numbers` |
| tier0-roster (tier0/roster.py, tier0/constants.py) | tier0/constants.py:366 — GARMENT_CHARGE_DIVISOR = 2  ->  3  (Ceremonial Garment gives +1 attack damage per this much Charge) | `tier0/tests/test_sheet_lints.py::test_mirrored_constants_match_the_sim` |
| tier0-roster (tier0/roster.py, tier0/constants.py) | tier0/constants.py:1003 — _arm_knob: `if name not in g:` -> `if name in g:` (inverts the does-this-constant-exist gate) | `tier05/tests/test_sweep_gate.py::test_sweeping_a_dead_knob_is_refused_on_the_first_cell` |
| tier0-pilot (tier0/pilot/policy.py) | tier0/pilot/policy.py:687 (_lethal_card) — `if d >= remaining:` -> `if d > remaining:` (off-by-one on the exact-lethal boundary) | `tier0/tests/test_potion_policy.py::test_anchor_and_baseline_still_exact (assertion in tier0/tests/test_anchor_lock.py:59, winrate 0.515 vs locked 0.525)` |
| tier0-pilot (tier0/pilot/policy.py) | tier0/pilot/policy.py:45 (pilot, block-panic gate) — `incoming >= C.BLOCK_PANIC_THRESHOLD * max(1, state.player.hp)` -> `incoming >= C.BLOCK_PANIC_THRESHOLD` (drop | `tier0/tests/test_combat.py::test_starter_vs_punisher_is_competitive (winrate collapsed to 0.0)` |
| tier0-pilot (tier0/pilot/policy.py) | tier0/pilot/policy.py:213 (_expected_damage) — `total += per_hit * times * n_targets` -> `total += per_hit * times` (AoE damage priced as single-target) | `tier0/tests/test_pass3.py::test_per_deck_a2_bands (reaction_weighted A2_scaling 3.588 > cap 3.5)` |
| tier0-pilot (tier0/pilot/policy.py) | tier0/pilot/policy.py:312 (_block_value) — `val += min(raw, prevented) + min(pulse, prevented)` -> `val += raw + min(pulse, prevented)` (removed the clam | `tier0/tests/test_potion_policy.py::test_anchor_and_baseline_still_exact (assertion in tier0/tests/test_anchor_lock.py:59, winrate 0.505 vs locked 0.525)` |
| tier0-pilot (tier0/pilot/policy.py) | tier0/pilot/policy.py:616 (_stoke_value, Encore fuel split) — `closes = min(n, shortfall)` -> `closes = n` (removed the runway clamp, so every point of Encore is priced at  | `tier0/tests/test_pilot_stoke_value.py::test_encore_is_worth_more_when_the_runway_is_short` |
| tier0-harness (tier0/harness/axes.py, tier0/harness/metrics.py, tier0/harness/runner.py) | tier0/harness/axes.py:97 — A2 scaling sample gate: `if s.turns >= 10:` -> `if s.turns > 10:` (off-by-one on which fights count as scaling | `tier0/tests/test_axes_honesty.py::test_the_a2_denominator_is_reported_alongside_the_axis (assert raw["A2_samples"] == 1, got 0.0)` |
| tier0-harness (tier0/harness/axes.py, tier0/harness/metrics.py, tier0/harness/runner.py) | tier0/harness/axes.py:219 (normalize, A6_utility branch) — A6 v2 composite weights: `3.0 * (0.5*aoe + 0.3*deb + 0.2*app)` -> `3.0 * (0.5*aoe + 0.2*deb + 0.3*app)` (swap  | `tier0/tests/test_axes.py::test_a6_v2_uptime_component_and_anchor (expected 3.3, got 3.45)` |
| tier0-harness (tier0/harness/axes.py, tier0/harness/metrics.py, tier0/harness/runner.py) | tier0/harness/axes.py:130 (raw_axes, A5) — A5 velocity numerator: `sum(s.cards_drawn_extra + s.energy_generated_extra ...)` -> `sum(s.energy_generated_ex | `tier0/tests/test_silent.py::test_silent_velocity_above_baseline (A5_velocity 3.0, expected > 3.2)` |
| tier0-harness (tier0/harness/axes.py, tier0/harness/metrics.py, tier0/harness/runner.py) | tier0/harness/metrics.py:164 (extract, apply_power branch) — A6 debuff crediting guard inverted: `ev["target"] != "player"` -> `ev["target"] == "player"` (credit debuffs l | `tier0/tests/test_errata.py::test_v02_median_scorecard_locked (A6_utility 4.63 vs locked 4.05 +/- 0.3)` |
| tier05-draft (tier05/draft.py) | tier05/draft.py:287 (core_complete, reaction limb) — `return appliers >= 2 and amps >= 1` -> `return appliers >= 1 and amps >= 1` (off-by-one on the reaction core' | `tier05/tests/test_m5.py::test_payoff_gated_beyond_core` |
| tier05-draft (tier05/draft.py) | tier05/draft.py:651 (_static_power, Bomb guard credit) — `if has_bomb and not has_enemy_weak:` -> `if has_bomb:` (inverted/removed the Weak-overlap guard so the Bomb g | `tier05/tests/test_m5.py::test_drafter_v3_values_klee_visible_utility` |
| tier05-draft (tier05/draft.py) | tier05/draft.py:261 (_drafted_readers, basic exclusion) — `sum(1 for c in deck if c.rarity != "basic" and _reads_fanfare(c))` -> `sum(1 for c in deck if _reads_fanfare( | `tier0/tests/test_fanfare_compensation.py::test_the_starter_reader_does_not_close_the_drafts_reader_limb` |
| tier05-model (tier05/model.py, tier05/acts.py) | tier05/model.py:126 — Inverted the pre-fight lookahead guard: `if next_fight and hp < C.REST_PREFIGHT_HEAL_THRESHOLD * max_hp:` -> ` | `tier05/tests/test_multiact.py::test_two_act_run_walks_both_acts_and_heals_at_the_boundary` |
| tier05-model (tier05/model.py, tier05/acts.py) | tier05/acts.py:220 — Off-by-one on the easy-pool boundary in ActDraw.encounter_for: `if i < min(self._easy_fights, len(self._easy)) | `tier05/tests/test_burning_blood_runlayer.py::test_no_relic_no_run_layer_heal` |
| tier05-model (tier05/model.py, tier05/acts.py) | tier05/acts.py:132 — Off-by-one on the act's easy-fight allowance: `return int(C.RUN_ACTS[act]["easy_fights"])` -> `return int(C.RU | `tier05/tests/test_multiact.py::test_second_act_uses_its_own_easy_fights_rule` |
| tier05-model (tier05/model.py, tier05/acts.py) | tier05/acts.py:228-229 — Dropped the never-twice-in-a-row elite constraint: `choices = [e for e in self._elite_pool if e["id"] != self. | `tier05/tests/test_m5.py::test_elite_pool_draws_two_distinct_and_boss_draws_from_pool` |
| tier05-metrics (tier05/run_metrics.py, tier05/stats.py) | tier05/stats.py:57 — percentile() interpolation term dropped: `return s[lo] + (s[hi] - s[lo]) * (idx - lo)` -> `return s[lo] + (s[h | `tier05/tests/test_m5.py::test_survival_profile_keeps_dead_runs_in_later_fight_cohorts (assert [0.0, 0.0] == [0.5, 0.5])` |
| tier05-metrics (tier05/run_metrics.py, tier05/stats.py) | tier05/stats.py:79 — wilson95() center term halved-denominator dropped: `center = (p + z * z / (2 * trials)) / denom` -> `center =  | `tier05/tests/test_m5.py::test_summarize_runs_fragility_shape (assert lo <= winrate <= hi: 0.0438 <= 0.0)` |
| tier05-metrics (tier05/run_metrics.py, tier05/stats.py) | tier05/run_metrics.py:221 — survival_profile() near-death guard inverted at the zero boundary: `any(0 < h <= floor for h in r.hp_by_node)` | `tier05/tests/test_m5.py::test_survival_profile_reads_the_curve_it_is_given (assert 1.0 == 0.0)` |
| tier05-metrics (tier05/run_metrics.py, tier05/stats.py) | tier05/run_metrics.py:467 — trajectory_profile() lethal-round exclusion neutered: `while rounds and rounds[-1] <= 0.0:` -> `while rounds a | `tier05/tests/test_stability_trajectory.py::test_the_lethal_round_is_excluded_from_every_column (assert 0 == 1)` |
| tier05-economy (tier05/events.py, tier05/rewards.py, tier05/shop.py) | tier05/shop.py:74 — removal_price(): `return C.SHOP_REMOVAL_PRICE + C.SHOP_REMOVAL_PRICE_STEP * removal_uses` -> `return C.SHOP_RE | `tier05/tests/test_shop_economy.py::test_removal_removes_a_known_dead_card` |
| tier05-economy (tier05/events.py, tier05/rewards.py, tier05/shop.py) | tier05/shop.py:153 — companion_shop_offer(): `nation = home if slot == 0 else None` -> `nation = home if slot == 1 else None` (off- | `tier05/tests/test_shop_companion_channel.py::test_slot_one_is_home_nation_when_the_nation_can_supply_it` |
| tier05-economy (tier05/events.py, tier05/rewards.py, tier05/shop.py) | tier05/rewards.py:189 — _nation_weighted_choice(): `+ (share / n_home if c.nation == home_nation else 0.0)` -> `... if c.nation != hom | `tier05/tests/test_fontaine_rewards.py::test_klee_offers_concentrate_on_mondstadt` |
| tier05-route (tier05/route.py, tier05/maps.py, tier05/cells.py) | tier05/route.py:104 — Rest urgency multiplier: `want[REST] * min(1.0, 2.0 * (1.0 - st.hp_frac))` -> `want[REST] * min(1.0, 1.0 * (1. | `tier05/tests/test_maps_and_routing.py::test_elite_count_responds_to_run_state (assert rests_hurt > rests_healthy + 0.5: 2.01 > 2.125 failed)` |
| tier05-route (tier05/route.py, tier05/maps.py, tier05/cells.py) | tier05/route.py:127 — Escalating HP bar in hunter: `bar = 0.55 + 0.15 * st.elites_taken` -> `bar = 0.55` (drops the additive escalat | `tier05/tests/test_maps_and_routing.py::test_elite_count_responds_to_run_state (assert mean(hurt) < mean(healthy) - 0.5: 2.105 < 1.815 failed)` |

## Module notes (baselines, coverage observations)

### engine-combat (tier0/engine/combat.py) (baseline green: True)
Targeted test set was derived by grepping tier0/tests and tier05/tests for `engine.combat` imports, direct `combat.<fn>` usages, and `run_fight` references — 43 files (30 in tier0/tests, 13 in tier05/tests). Unmutated targeted baseline: 817 passed, 16 skipped in 126s. Full suite in this worktree: 1516 passed, 61 skipped in ~235s (the task brief said 1496/61; the extra 20 are worktree-local, and the run is green either way).

Kill rate 4/6. The four kills all landed on numbers that a dedicated, name-matching test asserts directly (Frozen multiplier, spark threshold, Spotlight first-play window, phase-down at hp == 0) — those rules are genuinely fenced, not just executed.

Both survivors are CAP/BOUNDARY constants that tests exercise only from the interior, never at the edge:
- grant_charged_kit's MAX_HAND_SIZE defer (combat.py:50) — the only MAX_HAND_SIZE reference anywhere in the test tree is tier0/tests/test_refpowers.py:718, which is about a different code path (retain-at-flush filler cards), not the Burst grant. The kit-grant hand-cap branch is executed but never asserted.
- _run_rounds' MAX_TURNS stall cap (combat.py:758) — MAX_TURNS appears in no test file at all. Fights in the battery evidently end on win/loss before the cap, so the cap's own boundary is dead to the suite.

Both are high load-bearing: each is a place where a core combat number can drift a full unit (one extra card in hand, one extra combat round) with the suite still green. A third area worth flagging without a mutant spent on it: the `prevented` term in the Encore absorb call (combat.py:665) sits at the intersection of Kokomi's ward and Furina's Encore, a character combination no content produces today — any mutation there would survive for reachability reasons rather than coverage reasons, so it is not a meaningful blind spot to file.

END STATE VERIFIED: every mutation was reverted with `git checkout -- tier0/engine/combat.py` immediately after its run. Final `git diff --stat` is empty and `git status --porcelain` is empty — the worktree is clean, no test files were written or modified, and no files outside tier0/engine/combat.py were touched.

### engine-effects (tier0/engine/effects.py) (baseline green: True)
Baseline: targeted set (tier0/tests/{test_effects,test_combat,test_klee,test_silent,test_ic_effects,test_si_effects,test_reactions,test_powers,test_curtain_call,test_furina,test_kokomi,test_pass2,test_pass3,test_frail,test_epoch1_fixes,test_multiact_ops,test_upgrades,test_ironclad_upgrades,test_errata,test_furina_fanfare_parity}.py) = 336 passed, 8 skipped in 2m35s, green before any mutation. Full-suite confirmations for the two survivors that reached step (c) each ran 1516 passed / 61 skipped in ~3m50s (mutant 3 and mutant 6); mutant 5 likewise passed the full suite.

Kill quality note: 3 of 6 mutants died, but only two died to a test that actually names the rule (Slow ramp, salon overflow bow). The targeting flip (min->max) was caught solely by a statistical axis band in test_silent.py drifting 0.03 over a 3.0 ceiling — reorder or retune that band and tier0's entire single-target aim becomes unprotected.

Survivor theme: the three survivors are all SECOND-ORDER terms on an otherwise well-tested pipeline — an optional rider argument (detonate bonus), a boundary on a creation path (hand cap), and a clamp on a defensive number. Tests assert the headline effect happened (bombs detonated, card created, prevention emitted) but not the modifier or the bound. The prevention-ward survivor is the worst of the three: it converts an enemy attack into player healing with no test noticing.

END STATE: git diff is empty and git status --porcelain is empty — all six mutations were reverted with `git checkout -- tier0/engine/effects.py` and verified after each. No test files were written or modified; no files outside tier0/engine/effects.py were touched.

### engine-powers (tier0/engine/powers.py) (baseline green: True)
Baseline: targeted set of 23 files (test_powers, test_frail, test_refpowers, test_si_powers, test_si_effects, test_si_pass4/5/6/7, test_ic_effects, test_a7_port, test_furina, test_furina_sheet, test_kokomi, test_klee, test_curtain_call, test_reaction_phase_parity, test_reactions, test_epoch1_fixes, test_errata, test_anchor_lock, test_pilot_stoke_value, tier05/test_multiact) = 558 passed in 67s, green. Full suite confirmed green at 1516 passed / 61 skipped in ~3m48s during mutant runs.

Targeting note worth acting on: I selected the targeted set by grepping for imports of powers' public names, and it MISSED tier0/tests/test_effects.py, which turned out to hold the only assertion on the Weak damage rate (mutant 2). After mutant 2 I added test_effects.py to the targeted set for mutants 3-6. Files that route through powers via effects.resolve_card rather than importing it are invisible to a name-based grep - relevant to how any later per-module pass picks its targeted set.

Score: 6 mutants, 4 killed (3 by targeted files, 1 only by the full suite), 2 survived. Both survivors are stacking/accumulation rules - Metallicize adding to existing block, and the apply_power cap actually clamping a second application. The heavily-commented parity invariants (the _floor clamp, Frail's floor, Dexterity's zero clamp, Dexterity-before-Frail ordering) are all genuinely pinned by tests, and killed fast.

END STATE: `git status --porcelain` and `git diff --stat` both return empty - the worktree is clean, every mutation was reverted with `git checkout -- tier0/engine/powers.py` after its run, and no test file was written or modified.

### engine-statuses (tier0/engine/statuses.py) (baseline green: True)
Targeted test file: /home/user/GItS/.claude/worktrees/wf_cc7f3b59-1a3-4/tier0/tests/test_multiact_ops.py (the only file in tier0/tests or tier05/tests that imports or exercises tier0.engine.statuses). Baseline: 18 passed in that file; full suite in this worktree is 1516 passed, 61 skipped in ~3m50s (slightly higher count than the 1496 quoted, same green state).

Score: 6 mutants, 3 killed by targeted tests, 3 survived the FULL suite. Every killed mutant died on a number the tests assert directly (burn/wither eot, toxic draw, dazed ethereal); everything about the status Card's *identity fields* (cost, rarity, tag-list ownership) is completely unprotected.

Sharpest finding: mutant 5 exposes a live cross-module rule gap independent of the tests. make_status stamps rarity="basic", but tier0/engine/effects.py:1389-1390 (_op_exhaust_from) and tier0/pilot/policy.py:262-263 select the `filter: "status"` pool with `c.rarity == "status"`. So no injected status card is ever matched by a status-filtered exhaust today, and tier05/draft.py:457 prices that effect with STATIC_STATUS_EXHAUST_VALUE=1.5 as if it worked. Flipping the rarity either way is invisible to all 1516 tests, so whichever direction is the intended rule, nothing pins it.

A secondary note on mutant 1: test_burn_and_wither_tick_at_turn_end asserts only the SUM (hp0 - 5) with both cards in hand, so swapping burn/wither damage slips past it; the swap was caught only incidentally by test_status_eot_damage_eats_block_first, which happens to hold wither alone and checks residual block. Per-status eot damage is pinned for wither and unpinned for burn in isolation.

END STATE: all mutations reverted with `git checkout -- tier0/engine/statuses.py` after each run; `git diff` is EMPTY and `git status --porcelain` reports nothing. Targeted tests re-run clean (18 passed) on the restored file. No test files were written or modified; no file outside tier0/engine/statuses.py was touched.

### engine-resources (tier0/engine/resources.py) (baseline green: True)
Baseline in this worktree: targeted set of 12 files = 275 passed in ~5s, green. Targeted set was tier0/tests/{test_fanfare_rework,test_a7_port,test_furina,test_furina_sheet,test_curtain_call,test_fanfare_compensation,test_furina_fanfare_parity,test_track_b_curves,test_kokomi}.py plus tier05/tests/{test_fanfare_telemetry,test_encore_telemetry,test_burst_telemetry}.py.

10 mutants run (protocol asked 4-6; the targeted suite runs in ~1s so I extended the sweep after the first six all died, specifically to hunt for a survivor - which the 10th found). 9 killed by targeted tests, 1 survived the full suite.

Full-suite run for the surviving mutant: 1516 passed, 61 skipped in 231s (0:03:51). Note this is 1516, not the 1496 quoted in the task brief - worth a sanity check by the orchestrator, but the run was green with the mutation applied, which is the finding.

Verdict on coverage: the Fanfare half of this module is genuinely well protected - decay shape, the min-1 decay floor, the turn-2 bound, the cap clamp, the floor-grant triple move, the negative-floor settle, the reader zero-clamp, the read-instrumentation pin flags, and the per-point Fanfare rate on spend all have assertions that catch a one-token change. The blind spot is the BURST leg of spend_encore: burst income from Encore spend is emitted and observed as an event but its magnitude is never tied to the amount spent.

END STATE: `git checkout -- tier0/engine/resources.py` after every mutant; final `git status --porcelain` and `git diff` both empty. Tree is clean. No test files were written or modified; no files outside tier0/engine/resources.py were touched.

### engine-reactions (tier0/engine/reactions.py) (baseline green: True)
Baseline in this worktree: 242 passed / 27 skipped over the 19 targeted files (94s); full suite 1516 passed / 61 skipped / 3 warnings (~3m50s). Targeted set was every test file under tier0/tests and tier05/tests that greps for reactions/resolve_hit/apply_aura/tick_auras or a reaction name: test_reactions, test_epoch1_fixes, test_errata, test_curtain_call, test_fontaine, test_pilot_reaction_value, test_reaction_phase_parity, test_axes_honesty, test_klee, test_pass2, test_upgrades, test_track_b_curves, test_real_ironclad, test_real_silent, test_canonical_model_misuse, test_creature_facing_contract, test_harmony_bootstrap_contract, tier05 test_m6, tier05 test_stability_trajectory.

Kill rate 4/6. The core reaction table is well defended: amplifier identity, aura lifetime, swirl spread, and the Curtain Call once-per-turn latch each died on a named, specific assertion, and every kill came from the targeted set (no mutant needed the full suite to catch it).

Both survivors are the same shape of gap - a reaction's *secondary payout* is checked once, in isolation, at the smallest possible magnitude:
- Catalytic Conversion (line 151) is only ever tested at one stack, so the per-stack scaling of burst is unverified while the spark side of the same `if bonus:` block does scale. Note the sparks line (`p.sparks += bonus`) is what pins bonus's meaning; the burst line rides along untested.
- Crystallize (line 102) is only ever tested from Block 0, so nothing distinguishes "gain 4 Block" from "set Block to 4". This is the more dangerous of the two: assignment silently *destroys* pre-existing Block, and geo triggers are exactly the case where a player is likely already blocking.

Neither survivor is dead code - reaction_bonus_spark_energy is granted by a real Klee card (docs/klee-cards.yaml:155) via apply_power, which stacks on repeat plays.

END STATE: `git diff` is empty and `git status --porcelain` is empty - verified after the final revert. All six mutations were applied and reverted one at a time with `git checkout -- tier0/engine/reactions.py`, with a clean-tree check between each. No test files were written or modified, and no file outside tier0/engine/reactions.py was touched.

### engine-relics (tier0/engine/relics.py) (baseline green: True)
Baseline: targeted files tier0/tests/test_relics_combat_start.py, tier0/tests/test_relics_dynamic.py, tier0/tests/test_starter_relic_upgrades.py, tier05/tests/test_relics_runlayer.py, tier05/tests/test_relic_granting.py -> 53 passed in 4.4s, green. Full-suite baseline in this worktree is 1516 passed / 61 skipped in ~4 min (higher than the 1496 quoted in the brief, still fully green).

8 mutants run, 6 killed by targeted tests (all within 0.2s), 2 survived the FULL suite (tier0/tests tier05/tests: 1516 passed, 61 skipped, both times). This module is well covered on the hook-dispatch rules: the max_hp heal clamp, every-N-turn cadence, once-per-combat HP-loss latch, all-enemies targeting, the Spark-economy gate, and the conditional_power delta accounting all have tests that catch a one-token change.

The two blind spots are both boundary/branch cases rather than main-path math:
1. relics.py:224 -- conditional_power's inclusive `<=` at the HP threshold. The test at tier0/tests/test_relics_dynamic.py:128 even carries the comment "at/below 50% (40 == threshold*max)" but then sets p.hp = 30, so the equality case it names is the one case never run. Highest-value gap: a `<=` -> `<` drift silently turns Red Skull off for a player at exactly half HP.
2. relics.py:266 -- the `or sub in (card.name or "")` half of card_name_damage_bonus. No test and no shipped content distinguishes id-match from name-match (the only content relic uses substring "strike", which matches ids like "pommel_strike" directly), so that clause is currently untested code that a future relic keyed off a display name would depend on.

END STATE: `git checkout -- tier0/engine/relics.py` was run after every mutant; final `git status --porcelain` and `git diff --stat` both produced empty output. The worktree is clean and no test file was written or modified.

### engine-state (tier0/engine/state.py, tier0/engine/refpowers.py) (baseline green: True)
END STATE: `git diff`, `git diff --stat` and `git status --porcelain` are all empty — no mutation is left applied and no test file was written or modified.

BASELINE. Targeted set (19 files, ~15s): tier0/tests/{test_refpowers, test_real_ironclad, test_real_silent, test_si_powers, test_si_effects, test_si_pass4, test_si_pass5, test_si_pass6, test_si_pass7, test_ic_effects, test_ic_pass6, test_card_copy, test_combat, test_powers, test_effects, test_multiact_ops, test_klee, test_kokomi, test_furina}.py -> 428 passed, 27 skipped, green. Full suite in this worktree reports 1516 passed / 61 skipped in ~3m49s (slightly more than the 1496 quoted in the brief — worktree is at commit e07fb4c).

SCORE: 7 mutants, 5 killed (all by targeted tests, all within 0.4s — refpowers' own test file is fast and sharp), 2 survived the full suite. Note that state.py:646 is probably an equivalent mutant (see its entry), so the one real blind spot found is state.py:663.

SHAPE OF THE GAP. refpowers.py is unusually well protected: every parity rule I attacked (Unmovable's allowance boundary, Plating's turn-1 exemption, Cruelty's delta-fold, Juggling's exact ==3) has a named test that asserts the exact number, and each failed with a readable diff naming the rule. The tests read as if they were written from the same decompiled source as the code.

state.py is the softer half, and the boundary between them is telling: it is described in its own docstring as "no rules logic here — just data and the pile-manipulation primitives", and the primitives are exactly what nothing asserts. `CombatState.draw` carries three game rules (the NoDraw gate, the empty-pile reshuffle, and the MAX_HAND_SIZE cap) and only the first two are pinned. The hand cap is checked in four separate places in the codebase (combat.py:50, combat.py:723, refpowers.py:749, refpowers.py:1113, effects.py:485/2341) and tests exist for the Juggling and token-add overflow redirects — but the copy of the rule inside `draw` itself, the one every draw effect in the game funnels through, has no test at all. A reviewer adding a draw op would get no signal if it overdrew.

There is no tier0/tests/test_state.py despite state.py:37 and state.py:277 both referring to one by name for the deepcopy/_MUTABLE_FIELDS pins; those pins actually live in tier0/tests/test_card_copy.py. Worth correcting the comments or naming the file, since a future auditor will look for the wrong path.

Two areas I probed but did not mutate, both plausible follow-ups for the gated missing-test pass: Card.__deepcopy__'s per-instance field sharing (covered by test_card_copy, so likely fine) and `Enemy.advance_intent`'s intent_uses keying, which feeds ramp_per_use.

### engine-potions (tier0/engine/potions.py) (baseline green: True)
Baseline: `python3 -m pytest tier0/tests/test_potion_effects.py tier0/tests/test_potion_policy.py tier05/tests/test_potion_runlayer.py -q` -> 41 passed (green). Targeted files were chosen by grepping tier0/tests + tier05/tests for `engine.potions` / `potions.` usage; test_potion_effects.py is the only test that imports the module directly, test_potion_policy.py drives it through combat, test_potion_runlayer.py covers the tier0.5 bag half.

Result: 7 of 7 real mutants SURVIVED (each one passed targeted AND the full 1516-test suite, ~3m50s per full run); the 8th was a deliberate control that died instantly, proving the harness and edits take effect.

Shape of the blind spot: the tests assert the flat PAYLOADS exhaustively (block 12, fire 20, blood 20% + cap, strength 2, draw 3, weak 3, vuln 3, energy 2, fairy revive) and assert the coarse elite/normal gating with one hardcoded string each. Nothing asserts the DECISION MATH that decides when those payloads fire: `_intent_damage` (ramp term, times multiplier), the block subtraction in `_try_defensive`, the `> MARGIN` boundary, the `<= POTION_FIRE_DAMAGE` kill-range bound, or that the big-hit threshold is a fraction of max_hp. All potion-policy tests use single-hit, non-ramping intents on a full-HP, zero-Block player, which is exactly the input region where every one of these mutations is invisible.

Files: /home/user/GItS/.claude/worktrees/wf_cc7f3b59-1a3-8/tier0/engine/potions.py, /home/user/GItS/.claude/worktrees/wf_cc7f3b59-1a3-8/tier0/tests/test_potion_policy.py, /home/user/GItS/.claude/worktrees/wf_cc7f3b59-1a3-8/tier0/tests/test_potion_effects.py, /home/user/GItS/.claude/worktrees/wf_cc7f3b59-1a3-8/tier05/tests/test_potion_runlayer.py.

END STATE: every mutant was reverted with `git checkout -- tier0/engine/potions.py` immediately after its run; final `git diff` is empty and `git status --porcelain` is empty. No test file was written or modified; no file outside tier0/engine/potions.py was touched.

### tier0-roster (tier0/roster.py, tier0/constants.py) (baseline green: True)
END STATE: `git status --porcelain` and `git diff --stat` are both empty; a post-revert re-run of the roster/sheet-lint/sweep-gate/map tests is green (137 passed). No test file was written or modified.

BASELINE: targeted set green before mutation (269 passed, 1 skipped, ~15s). Targeted files: tier0/tests/{test_roster_registry, test_roster_runtime_contracts, test_roster_codegen, test_stale_band_annotations, test_tier1_roster, test_kokomi, test_furina, test_furina_sheet, test_pulse_multiplier_claims}.py + tier05/tests/{test_sweep_gate, test_maps_and_routing, test_shop_economy}.py. After M2 escaped the targeted set I added tier0/tests/test_epoch1_fixes.py, and after M4 escaped it I added tier0/tests/test_sheet_lints.py, for the remaining mutants. Full-suite baseline in this worktree is 1516 passed / 61 skipped in ~3m48s (higher than the 1496 quoted in the task; nothing red).

STRUCTURAL FINDING THAT MATTERS MORE THAN THE INDIVIDUAL MUTANTS. Both constants that WERE killed were killed by PARITY LINTS, not by behavioural tests:
  - SALON_DRY_DAMAGE_MULT died to tools/lint_sheet_comments.py (a comment-cites-the-right-number check on docs/furina-cards.yaml).
  - GARMENT_CHARGE_DIVISOR died to tools/lint_constant_parity.py (the C#-mirror check).
The behavioural tests that look like they pin these numbers do not: tier0/tests/test_furina_sheet.py:254 `test_dry_salon_ticks_resolve_at_three_quarters_without_overdraw` computes its expectation as `int(CRAB_TICK * C.SALON_DRY_DAMAGE_MULT)`, i.e. it reads the constant it is meant to protect and moves with any edit to it. Same self-referential shape in tier05/tests/test_maps_and_routing.py (lines 36, 37, 79, 225, 226), which is exactly why MAP_TREASURE_FLOOR survived. So for tier0/constants.py the real coverage boundary is not tier0-behaviour-vs-not, it is MIRRORED-into-the-mod-or-lint-file vs not: run-layer/tier05-only numbers (map floors, shop/economy steps, rest thresholds, reward shares) have essentially zero value-pinning, because the tests that name them read them.

CONSEQUENCE FOR THE LATER GATED PASS. The two survivors point at one missing test shape each, and it is the same shape: an assertion written against a LITERAL, not against the constant. (a) roster.IDS == ("klee", "furina", "kokomi") as a literal, protecting the documented ship order. (b) the map's fixed floors asserted at their literal wiki-real indices (treasure 8, rest 14, boss 15) in one place, so the layout is pinned once rather than re-derived from itself in five. I did not write either -- flagged only.

MUTANT SELECTION NOTE. tier0/constants.py is ~1000 lines of which only ~35 are executable logic (the PEP-562 sweep hook and _arm_knob/_disarm_knob); everything else is a value binding, so five of six mutants are necessarily value edits and one is the only real control-flow mutation available in the module. Comments were never mutated, and the several constants documented as DELETED/dead (SPOTLIGHT_SELF_MULT, FANFARE_DECAY_PER_TURN, PROGRESSION_GAP_COMPENSATOR, etc.) were skipped as dead code per protocol.

### tier0-pilot (tier0/pilot/policy.py) (baseline green: True)
Baseline: 17 targeted files (tier0/tests/test_combat.py, test_fanfare_rework.py, test_furina.py, test_ic_effects.py, test_ic_pass6.py, test_klee.py, test_kokomi.py, test_multiact_ops.py, test_pass2.py, test_pilot_reaction_value.py, test_pilot_stoke_value.py, test_potion_policy.py, test_real_ironclad.py, test_real_silent.py, test_si_pass6.py, tier05/tests/test_encore_telemetry.py, test_m6.py) = 321 passed, 27 skipped in 46s. 7 mutants run, 5 killed, 2 survived the FULL suite (1516 passed, 61 skipped, ~3m55s each).

Kill structure: most of the killing power comes from two coarse whole-battery locks, not from pilot-behavior assertions — tier0/tests/test_anchor_lock.py::test_ref_ironclad_battery_numbers_locked (exact winrate 0.525 at seed 7, re-run via test_potion_policy::test_anchor_and_baseline_still_exact) and tier0/tests/test_pass3.py::test_per_deck_a2_bands. Those catch that a number moved, but they name no rule; a reviewer looking at a red anchor lock learns nothing about WHICH pilot rule broke. Only one kill (the stoke fuel split) came from a test that actually states the rule it is protecting.

Coverage gap worth noting for the later pass: test_pass3.py is NOT reachable from any grep of my module's names, yet it was the only thing that killed mutant 3 (AoE n_targets). The targeted set is a weaker net than the full suite by a wide margin.

END STATE: `git checkout -- tier0/pilot/policy.py` after every mutant; final `git status --porcelain` and `git diff --stat` both produced empty output. The worktree is clean and no test files were created or modified.

### tier0-harness (tier0/harness/axes.py, tier0/harness/metrics.py, tier0/harness/runner.py) (baseline green: True)
Baseline: targeted files (tier0/tests/{test_axes,test_axes_honesty,test_klee,test_pass2,test_errata,test_combat,test_pass3,test_silent,test_anchor_lock,test_relics_dynamic,test_potion_policy,test_furina}.py + tier05/tests/{test_stability_trajectory,test_runner,test_neow_and_shop}.py) = 222 passed in 2m46s, green. Full suite in this worktree = 1516 passed, 61 skipped in ~4m (higher count than the 1496 quoted; same green status).

7 mutants run, one at a time, each reverted with `git checkout --` and verified before the next. 4 killed, 3 survived.

Pattern in what got killed: the axis PIPELINE is well protected wherever a frozen number rides on it. A2's sample-window bound, the A6 v2 weight vector, the A5 velocity numerator, and the A6 debuff target-side guard all die fast, mostly against value-locked regression tests (tier0/tests/test_errata.py's V02_MEDIAN scorecard lock, tier0/tests/test_silent.py's per-axis thresholds, tier0/tests/test_axes.py's hand-computed A6 arithmetic). Those locks are doing heavy lifting: three of the four kills came from a frozen numeric expectation, not from a test that states the rule.

Pattern in what survived: everything that is a THRESHOLD or a DERIVED REPORT rather than an axis input. A7's 0.7 own-peak fraction, control_uptime's denominator, and pressure_delta's sign all move freely. The common shape is that no test pins the semantic direction or magnitude of these — test_axes.py:36 checks only that pressure_delta is equal across two runs (determinism), never that it is punisher-minus-attrition. Note that the surviving mutants sit exactly where the file's own docstring (D3 standing) says the instrument is reportable-but-not-load-bearing, so the blind spot is consistent with the declared posture; it is still a blind spot for anyone who later promotes these numbers.

END STATE: `git status --porcelain` empty and `git diff` empty. Tree is clean; no mutation left applied, no test file written or modified, nothing touched outside the three module files.

### tier05-draft (tier05/draft.py) (baseline green: True)
Baseline: targeted set = the 23 test files under tier0/tests and tier05/tests that reference tier05.draft or draft policy names (test_epoch1_fixes, test_fanfare_compensation, test_ic_effects, test_ic_pass6, test_real_ironclad, test_real_silent, test_roster_registry, test_sheet_lints, test_understudy_rng, and tier05 test_cells, test_m5, test_m6, test_m7, test_multiact, test_neow_and_shop, test_overlap_telemetry, test_parallel_runs, test_potion_runlayer, test_relic_granting, test_relics_runlayer, test_shop_companion_channel, test_shop_economy, test_v18_banner). Unmutated targeted run: 284 passed, 27 skipped in 31s -- green. Full suite in this worktree reads 1516 passed, 61 skipped, ~4 min (the brief's 1496 was presumably taken elsewhere); it was green on every survivor run.

Score: 3 killed / 3 survived out of 6. The kills are all in the areas that have dedicated named tests (the reaction core definition, the Klee bomb/Weak overlap, the Furina starter-reader exclusion) -- those blind spots were already closed by earlier post-mortems, and the tests are precise.

The survivors cluster in a recognisable shape: the SCORER'S NUMBERS are asserted, but the SCORER'S CONTROL FLOW AND MULTIPLIERS are not. Every survived mutant is a term that changes what the drafter picks without changing any invariant a test states.
  * The AoE multiplier (line 563) is the single highest-value survivor: it is the fix an entire version bump (v6, the Furina-0% diagnosis) exists to encode, and it can be deleted silently. A test asserting score(all_enemies card) == 2x score(single_target twin) would kill it.
  * The lean-gate boundary (line 1243) and the regret margin (line 1564) are both threshold constants used in comparisons that nothing exercises at the boundary; each is a one-character edit away from moving a measured run-layer number.
Notably `assigned_policy`'s lean-gate body (the Powers/tempo/Block/rare-bar filter) appears to be reached by no test at all in this suite -- both a boundary shift there and, by implication, most of its predicate went unpunished.

END STATE: all six mutations were reverted with `git checkout -- tier05/draft.py` immediately after their run. Final `git status --short`, `git diff`, and `git diff --stat` all produce empty output -- the worktree is clean and no test file was written or modified.

### tier05-model (tier05/model.py, tier05/acts.py) (baseline green: True)
Baseline: targeted set = tier05/tests (whole dir) + tier0/tests/test_multiact_ops.py + tier0/tests/test_content_boundaries.py, selected by grepping both test trees for tier05.model / tier05.acts imports and for run_one/run_many/rest_action/ActDraw/build_node_encounter/easy_fights/boss_pool/spawn usages. Baseline GREEN: 357 passed in 28s. Full suite in this worktree: 1516 passed, 61 skipped, ~4 min.

7 mutants run (one over the 4-6 guidance, deliberately): the acts.py:220 easy-pool boundary mutant died by IndexError rather than by any semantic assertion, which answers nothing about whether the easy/hard progression rule is actually checked — so I re-probed the same rule with a non-crashing variant (acts.py:132, easy_fights - 1). That one died to a real identity assertion, confirming the rule IS protected. Both are reported.

Score: 3 survived / 4 killed. All three survivors are in tier05/model.py's run-layer economy and rest policy; every acts.py mutant died. The pattern: acts.py has direct unit tests that assert draw identity, while model.py's run-layer arithmetic (HP clamps, gold debits, quota math) is only ever observed through aggregate run outcomes, which absorb the drift. Both HIGH survivors are silent-drift-in-a-core-number cases: uncapped rest healing and un-debited 150g relic purchases both make runs strictly stronger with no test noticing.

Two survivors are worth flagging as asymmetric: the rest-heal clamp and the shop-relic debit both fail in the player's FAVOR, so they would show up as an unexplained win-rate lift in calibration rather than as a crash.

END STATE: `git status --porcelain` empty, `git diff` empty, `git diff --stat` empty — verified after the final revert. No mutation left applied, no test file written or modified, no file outside tier05/model.py and tier05/acts.py touched.

### tier05-metrics (tier05/run_metrics.py, tier05/stats.py) (baseline green: True)
Worktree: /home/user/GItS/.claude/worktrees/wf_cc7f3b59-1a3-16. Baseline for the targeted set (tier0/tests/test_stability_band.py, tier0/tests/test_epoch1_fixes.py, tier05/tests/test_stability_trajectory.py, tier05/tests/test_m5.py, tier05/tests/test_elite_blitz.py, tier05/tests/test_kurage_telemetry.py, tier05/tests/test_cells.py, tier05/tests/test_v18_banner.py, tier05/tests/test_runner.py) was green: 123 passed in 5.4s. Full suite in this worktree: 1516 passed, 61 skipped, ~3m50s. 4 of 6 mutants were killed, all by the targeted set alone and all within the FIRST failing test — the statistics core (tier05/stats.py percentile interpolation and Wilson center) and the two explicitly-argued judgement calls in run_metrics.py (the "dead is not near-death" guard at :221, the lethal-round exclusion at :467) are genuinely well pinned, each by a test that names the reasoning it protects. The 2 survivors share a shape worth naming: both are boundary CONSTANTS inside derived report shares — act_funnel's reached boundary and route_profile's in_target_band range — where every test asserts the surrounding dict's keys, types and 0..1 range but never the specific value against a hand-computed cohort. in_target_band in particular is the §11 acceptance instrument's headline number and its band literal (1..4) is the target stated in the module docstring, yet no test distinguishes it from 1..5. NOT a mutant but noticed while reading: run_metrics.py:35 and :190 and :596 each independently recompute n_nodes from results[0].n_acts, and stability_profile at :334 divides by fights_total with no guard, though the earlier `if not losses` return makes it unreachable in practice. END STATE VERIFIED: git status --porcelain and git diff are both empty — no mutation left applied, no test written or modified, no file outside the module touched.

### tier05-economy (tier05/events.py, tier05/rewards.py, tier05/shop.py) (baseline green: True)
Baseline: targeted set (12 tier05 + 9 tier0 test files exercising events/rewards/shop directly and through the run layer) ran green at 358 passed / 35 skipped in 33s. Full suite green at 1516 passed / 61 skipped in ~3m50s.

6 mutants, one at a time, each reverted before the next: 3 killed by targeted tests, 3 survived the FULL suite (tier0/tests + tier05/tests). Every survivor was independently verified reachable before being scored — I ran the mutated code directly to confirm it produces a real behavioural difference rather than being an equivalent mutant (rewards.py:148 shifts the rng stream while leaving the banner set identical; events.py:378 produces hp 70 > max_hp 62; events.py:309 makes the greedy policy pick an exactly-lethal option in 5 distinct event/state combinations).

Pattern across the three survivors: the tests protect WHAT is chosen (which nation, which slot, which price tier) but not the CLAMPS AND BOUNDARIES around those choices. Both events.py survivors are guards whose whole stated purpose in their own comments ("a max-HP change earlier must not clip them", "a policy that suicides is noise, not agency") is unasserted, and the rewards.py survivor is an rng-consumption contract that determinism tests would need a fixed-seed archived value to catch.

END STATE: `git diff` is empty and `git status --porcelain` is empty — verified after the final revert. No test files were written or modified; no files outside tier05/{events,rewards,shop}.py were touched.

### tier05-route (tier05/route.py, tier05/maps.py, tier05/cells.py) (baseline green: True)
Baseline: targeted set = tier05/tests/{test_maps_and_routing,test_cells,test_m5,test_m6,test_multiact,test_runner,test_neow_and_shop,test_relic_granting,test_relics_runlayer,test_potion_runlayer,test_shop_economy}.py + tier0/tests/test_understudy_policy_v1.py -> 180 passed in ~21s, green. Full suite in this worktree is 1516 passed / 61 skipped in ~3m45s (20 more tests than the 1496 quoted in the brief; all green unmutated and under every surviving mutant).

Score: 6 mutants, 2 killed (both by the single test tier05/tests/test_maps_and_routing.py::test_elite_count_responds_to_run_state), 4 survived. Every kill in this module came from ONE test. test_hunter_hits_the_player_behaviour_target (the file's self-declared "load-bearing test") killed nothing: its mean tolerance is +/-0.35 and its band check lumps 1..4 together, so it tolerates both a narrowed map and a lowered elite cap.

Two structural blind spots worth naming: (a) the routing tests only ever measure ELITE and REST counts, so any mutation that changes WHICH lane a run walks without changing its elite count is invisible (mutant 1); (b) tier05/cells.py has 14 tests covering identity/stamp/derivation and ZERO covering Cell.arm(), the consolidated summary row that every exp_*.py reports from — win/act1/acts/decksize/fights are all unasserted.

Non-equivalence was verified numerically for all four survivors (not just "tests passed"): mutant 1 changes the chosen path on 44/300 maps at low HP; mutant 4 converts 42/300 four-elite healthy runs into three-elite runs; mutant 5 drops elite rooms per map 3.85 -> 3.43.

END STATE: all mutations reverted with `git checkout --` after each run. Final `git diff` is empty and `git status --porcelain` is empty. No test file was written or modified; no file outside tier05/{route,maps,cells}.py was touched.

