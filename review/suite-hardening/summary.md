# S15 — Suite-Hardening Sweep (Surplus Dispatch 3)

Date: 2026-08-05. Cloud stream, Opus swarm, zero Fable (mechanical by design).
Converts the S6 mutation audit's surviving mutants and the S1 sweep's clean-but-untested
cards into permanent suite machinery. **Every test pins CURRENT behavior exactly as it is** —
the iron rule; a pin that failed on current code was to be deleted and filed as a should-be
finding instead. None had to be: **zero should-be findings were filed**, and no blind spot was
skipped as untestable.

## Headline

- **111 pin-test functions** across **22 new test files** (17 module files + 5 card-batch files).
- Full suite after the sweep: **1629 passed, 61 skipped** (cloud box; local-asset tests skip here) — up from 1496 passed before it. Green on every commit in the batch.
- Blind-spot coverage: **46/46 S6 surviving mutants pinned** — the full survivor set.
- S1 arm: all **64 clean-but-untested cards** (25 Klee / 12 Furina / 27 Kokomi — verified CLEAN by the parity sweep yet referenced by zero test files) now each have a behavior pin.
- **S7 arm absent by circumstance:** S7 (sim-fidelity replay audit) ran locally and its divergence families were not final when this sweep launched. When the S7 ledger lands, its families are the natural third batch — same iron rule.

## Pins by module (S6 survivor families)

| module | file | pins | survivors covered |
|---|---|---|---|
| engine-combat | /home/user/GItS/tier0/tests/test_pin_engine_combat.py | 3 | HIGH-1, HIGH-2 |
| engine-effects | /home/user/GItS/tier0/tests/test_pin_engine_effects.py | 0 | HIGH-3, HIGH-4, MEDIUM-1 |
| engine-potions | /home/user/GItS/tier0/tests/test_pin_engine_potions.py | 9 | HIGH-12, HIGH-13, HIGH-14, HIGH-15, HIGH-16, MEDIUM-6, MEDIUM-7 |
| engine-powers | /home/user/GItS/tier0/tests/test_pin_engine_powers.py | 5 | HIGH-5, MEDIUM-2 |
| engine-reactions | /home/user/GItS/tier0/tests/test_pin_engine_reactions.py | 0 | HIGH-8, HIGH-9 |
| engine-relics | tier0/tests/test_pin_engine_relics.py | 2 | HIGH-10, MEDIUM-5 |
| engine-resources | /home/user/GItS/tier0/tests/test_pin_engine_resources.py | 2 | HIGH-7 |
| engine-state | /home/user/GItS/tier0/tests/test_pin_engine_state.py | 3 | HIGH-11, LOW-1 |
| engine-statuses | /home/user/GItS/tier0/tests/test_pin_engine_statuses.py | 3 | HIGH-6, MEDIUM-3, MEDIUM-4 |
| tier0-harness | /home/user/GItS/tier0/tests/test_pin_tier0_harness.py | 3 | HIGH-19, MEDIUM-9, MEDIUM-10 |
| tier0-pilot | /home/user/GItS/tier0/tests/test_pin_tier0_pilot.py | 0 | HIGH-18, LOW-2 |
| tier0-roster | /home/user/GItS/tier0/tests/test_pin_tier0_roster.py | 3 | HIGH-17, MEDIUM-8 |
| tier05-draft | /home/user/GItS/tier05/tests/test_pin_tier05_draft.py | 3 | HIGH-20, HIGH-21, MEDIUM-11 |
| tier05-economy | /home/user/GItS/tier05/tests/test_pin_tier05_economy.py | 0 | HIGH-26, HIGH-27, MEDIUM-13 |
| tier05-metrics | /home/user/GItS/tier05/tests/test_pin_tier05_metrics.py | 2 | HIGH-24, HIGH-25 |
| tier05-model | /home/user/GItS/tier05/tests/test_pin_tier05_model.py | 4 | HIGH-22, HIGH-23, MEDIUM-12 |
| tier05-route | /home/user/GItS/tier05/tests/test_pin_tier05_route.py | 5 | HIGH-28, HIGH-29, HIGH-30, HIGH-31 |

## Pins by card batch (S1 clean-but-untested)

| batch | file | pins | cards covered |
|---|---|---|---|
| cards_furina | /home/user/GItS/tier0/tests/test_pin_cards_furina.py | 12 | regal_bearing, commanding_gaze, witness_stand, warmup_act, waters_embrace, tempo_change, directors_cut, audience_participation, rain_of_roses, lasting_impression, prima_donna, standing_room_only |
| cards_klee_1 | /home/user/GItS/tier0/tests/test_pin_cards_klee_1.py | 13 | fish_flavored_bait, ammo_scavenging, careful_arrangement, spark_collection, tail_of_flame, combustion_study, study_of_explosions, hide_and_seek, spooked, run_away, clockwork_toy, jumpy_dumpty_mk2, remote_detonator |
| cards_klee_2 | /home/user/GItS/tier0/tests/test_pin_cards_klee_2.py | 12 | cluster_charge, all_my_treasures, secret_stash, flame_on_the_wick, cant_catch_me, da_da_da, perfect_timing, best_friends_forever, spirited_away, dodge_roll, surprise_visit, fish_blasting |
| cards_kokomi_1 | /home/user/GItS/tier0/tests/test_pin_cards_kokomi_1.py | 14 | conscription_notice, moon_signal, standing_orders, driftwood_charm, rearguard_action, to_the_front, mass_mobilization, shell_of_sanctuary, votive_offering, field_promotion, coral_guard, jade_bulwark, ritual_purification, vow_of_tides |
| cards_kokomi_2 | /home/user/GItS/tier0/tests/test_pin_cards_kokomi_2.py | 13 | salt_line, grand_conscription, pearl_diver, mercy_of_the_deep, slack_water, cleansing_tide, press_the_advantage, tide_reading, undertow_shuffle, whispered_word, steady_the_line, communion_of_tides, prayer_to_the_moon |

## Notes from the agents

- **cards_furina**: 12 tests, 12 passed (python3 -m pytest tier0/tests/test_pin_cards_furina.py -q -> "12 passed"); also green run alongside test_furina.py + test_furina_sheet.py (120 passed). Exactly one new file created; no existing file modified.

Setup seam: every test builds a real Furina combat via loader.build_player("furina") + CombatState with conftest.make_enemy (local helper furina_state), so her Fanfare cap (30 = 50% of 60 max HP), skill cadence and character id are live; cards are appended to hand and driven through combat.play_card. Helper seat_salon() stages a member by pushing player.salon and mirroring powers["salon_member"], which is the count every salon read goes through.

What each pin locks (current behavior):
- regal_bearing: 3 Block + 1 Weak on the single default target only (second enemy untouched).
- commanding_gaze: 2 Block + 1 Weak on all three enemies.
- witness_stand: 1 Vulnerable on target, exactly 1 draw, no Block, no damage.
- warmup_act: 3 damage always; the enemy_intends_attack rider pays 3 Block only vs an attacking intent (0 vs a block intent).
- waters_embrace: 9 Block bare, 14 with a salon member.
- tempo_change: 1 draw always; energy 3->2 bare, 3->2->3 with a salon member (self-refund).
- directors_cut: else arm = 1 draw, energy 3->2; then arm (spotlight re-aimed by playing the ethereal_spotlight selector token) = 2 draws and net energy 3.
- audience_participation: 2 Encore + 1 draw bare; 4 Encore + 2 draws after a reaction this turn (set up with a pyro aura + reactions.resolve_hit(hydro) -> vaporize).
- rain_of_roses: hydro aura on every enemy, zero damage, +5 Encore.
- lasting_impression: fanfare_cap +5 with fanfare still 0 (headroom, not a grant), +4 Encore, card lands in exhaust_pile and not discard.
- prima_donna: spotlight_discount 1 and spotlight_draw 1 on the player, fanfare_cap +8, fanfare still 0, and the Power leaves combat (neither discard nor exhaust pile).
- standing_room_only: 5 to all enemies at 0 Fanfare; at 9 Fanfare the 1_per_4 rider gives 2 steps -> 7 apiece, and the meter is read not spent (still 9 after).

Two incidental behaviors observed but deliberately NOT pinned as they are not this card's load-bearing output: rain_of_roses emits burst_income 5 from its skill_tag, and directors_cut played after the selector gains 2 center_stage Fanfare because Furina then holds the Spotlight.
- **cards_klee_1**: 13 tests, all green in isolation (`python3 -m pytest tier0/tests/test_pin_cards_klee_1.py -q` -> 13 passed). Exactly one new file created; `git status --porcelain` shows only `?? tier0/tests/test_pin_cards_klee_1.py`. Style follows the sibling sweep file tier0/tests/test_pin_cards_klee_2.py (local `_play` / `_events` helpers over conftest make_state/make_enemy).

Load-bearing behaviour pinned (all as the code does it today):
- fish_flavored_bait: damage row resolves BEFORE place_bomb, so the card's own attack cannot detonate the bomb it arms — enemy -5 HP, one live 5-dmg pyro bomb.
- ammo_scavenging: one 5-dmg bomb + exactly one draw, no damage row.
- careful_arrangement: move_bombs sweeps bombs off every OTHER living enemy onto the lowest-HP target and pays +2 per MOVED bomb; bombs already on the destination keep their printed damage (dest ends [4, 7, 8, 5]).
- jumpy_dumpty_mk2: two discrete 8s (not one 16) then two 6-dmg bombs, again armed after the hits.
- remote_detonator: detonates the whole board, +2 per bomb (7/6/8 events), leaves no bomb, detonations_total == 3.
- spark_collection: single gain_spark event of amount 2.
- tail_of_flame: both branches of `this_cost_zero` in one test — paid at 1 energy it is a flat 5; freed by the 3-Spark attack threshold it is 5 + 4, energy untouched and the Spark bank drained to 0.
- combustion_study: 15 Burst (10 from the row + 5 from the shared skill_tag grant in combat.play_card, emitted skill_tag-first) + 1 draw; second half of the same test pins the burst_max == 0 gate (0 Burst, no burst_energy event, draw still happens).
- study_of_explosions: printed cost 0 (energy untouched), scry_discard bins the worse of the top 2 via the _worst_card heuristic (non-attack `defend`), 5 + 5 = 10 Burst.
- hide_and_seek: 7 Block + scry that discards `defend` and draws nothing into hand.
- spooked: 3 Block + weak 1 on EVERY living enemy, no damage.
- run_away: free 4 Block, energy untouched.
- clockwork_toy ("Imaginary Friend"): 5 Block + 3 Burst from its row on top of the 5 skill_tag grant = 8.

Environment note (not a finding): tests run with the default conftest Player, whose element is "none" and cadence "skill", so `_element_for` returns None for these attack rows and no pyro aura is applied by card damage — bomb detonations still carry their own default pyro element. This matches how tier0/tests/test_pin_cards_klee_2.py drives the same seam.

No card was dropped and nothing had to be filed as a finding — every row executed coherently at the play_card seam.
- **cards_klee_2**: One new file, 12 tests, one per card, all green in isolation (`python3 -m pytest tier0/tests/test_pin_cards_klee_2.py -q` -> 12 passed). No existing file was modified.

Approach: each test loads the real sheet card via tier0.content.loader.get_card, appends it to a conftest make_state hand with energy, and drives tier0.engine.combat.play_card, then asserts the observable outcome (HP deltas, per-hit damage events, bomb lists, block, sparks, enemy powers, created cards and their destination pile, exhaust routing).

Behaviours worth calling out, all pinned as the code actually does them:
- cluster_charge: the damage op resolves BEFORE place_bomb, so the card's own attack cannot detonate the bombs it arms (effects._detonate_bombs_on_hit only fires on bombs already present). Pinned enemy ends at -10 HP holding two live 5-damage bombs.
- perfect_timing: pinned BOTH branches of its `reaction_triggered_by_this` conditional in one test. Off-element it is a flat 8 with the rider dead. With player element pyro / cadence catalyst into a hydro aura it Vaporizes to 12 (8 * C.VAPORIZE_MULT, int-truncated), the rider fires, and resolve_card's repeat loop re-runs only the damage op for a fresh 8 (aura already consumed, so the replay re-applies pyro rather than reacting again). Damage events [12, 8], enemy aura ends "pyro".
- best_friends_forever: state.companions_played was populated through the real play path (barbara_melody played twice); the op dedupes via dict.fromkeys, so exactly one cost-0 copy lands in hand.
- fish_blasting: initial draft asserted discard_pile == [fish_blasting, confiscated] and failed. Corrected to what the code does: the add_card token is created mid-resolution and the spent card only routes to its result pile afterwards in combat._finish_play, so Confiscated sits UNDER fish_blasting. X = whole energy bank (card_cost's X early return), 8 damage x 3 to every enemy = 24 apiece.
- secret_stash: asserts membership in loader.cards_in_pool("demolition_commons") and the cost_override of 0 rather than specific rolled ids, so the pin does not encode the rng draw order.
- dodge_roll: paired with the `confiscated` token (tokens.yaml rarity: status) to exercise the status filter in _op_exhaust_from; a plain strike in the same hand is asserted untouched.
- da_da_da: pinned as three discrete 4-damage events rather than one 12, which is what `times: 3` produces.

No card was skipped and nothing surfaced as incoherent-to-pin, so should_be_findings is empty.
- **cards_kokomi_1**: All 14 cards pinned, 14/14 passing in isolation (`python3 -m pytest tier0/tests/test_pin_cards_kokomi_1.py -q` -> 14 passed). No existing files touched; only the new test file is added.

Approach: one test per card, each building a real Kokomi combat via `loader.build_player("kokomi")` + `CombatState` with an explicit draw pile (so no reshuffle noise), then `combat.play_card`. Local helpers `kokomi_state()` / `play()` live in the new file only.

What is pinned per card:
- coral_guard 5 Block, jade_bulwark 6 Block, shell_of_sanctuary 11 Block (+ energy spend, no Charge rider).
- vow_of_tides: 8 to EVERY living enemy, catalyst hydro aura on each, self-Exhaust routing through the funnel (charge == C.CHARGE_PER_EXHAUST, burst_energy == C.KOKOMI_BURST_PER_EXHAUST).
- conscript family (conscription_notice, to_the_front, standing_orders, mass_mobilization, field_promotion): recruit comes from `loader.companion_pool("inazuma")`, is flagged conscripted+exhaust, and costs `max(0, printed + C.CONSCRIPT_COST_DELTA)`. Tests avoid RNG fragility by pinning membership/flags/cost-formula rather than a specific seeded recruit id, and by leaving exactly one legal `_worst_card` victim in hand. field_promotion loops seeds 0-11 to show `cost_override: 0` forces 0 even for a printed-2 recruit (that is what distinguishes the override from the ordinary -1 delta).
- moon_signal (0 cost, discard 1 then draw 1, net hand size flat), rearguard_action (discard 1 + 7 Block).
- driftwood_charm: pins BOTH halves — 3 Block + draw 1 on play with charge still 0 (the Sly rider does not fire on play), and charge == 2 when the card is instead discarded from hand by moon_signal.
- votive_offering: chosen exhaust + 5 Block, exhaust feeds the funnel.
- ritual_purification: chosen exhaust (1 funnel Charge) + 4 line Charge = 5 total, plus draw 1.

Observation (not filed as a finding, current behavior is coherent and is now pinned): `_op_conscript` deletes the victim outright — it does not go to discard or exhaust — so the transform pays no Charge through the funnel. That is consistent with the sheet's "transform, never create / net delta 0" note, and the conscription_notice test asserts the victim is absent from both piles.
- **cards_kokomi_2**: All 13 cards execute at the tier0 play_card seam; none needed skipping. Tests build a real Kokomi player via loader.build_player("kokomi") (so the Tamakushi Casket exhaust funnel is live) plus conftest.make_enemy, append the printed card from loader.get_card, and drive combat.play_card. Final run: `python3 -m pytest tier0/tests/test_pin_cards_kokomi_2.py -q` -> 13 passed.

What each test pins (current behavior, verified against the code):
- tide_reading: 2 Block, exactly 1 card drawn off the draw pile.
- slack_water: 4 Block now + block_next_turn power stack of 4.
- steady_the_line: 4 Block, one card to discard pile (discard resolves before the played card routes, so discard_pile order is ["fodder", "steady_the_line"]).
- whispered_word: 3 Block + 1 discard; discarding a second copy fires that copy's Sly rider (draw 1) — confirmed via the emitted sly/draw log rows.
- salt_line: 5 Block when played; when discarded by another card's chosen-discard, its Sly exhausts a card from hand and the funnel pays CHARGE_PER_EXHAUST.
- undertow_shuffle: draw 3 then discard 2 at random -> draw pile -3, hand +1, discard pile 3 (2 victims + the card).
- communion_of_tides: exhaust 1 chosen + draw 2, charge/burst from the funnel.
- pearl_diver: exhaust 1 chosen, charge = 2 printed + 1 funnel, no block.
- cleansing_tide: exhaust 2 chosen, 10 Block, 2x funnel charge and burst.
- prayer_to_the_moon: 7 printed charge + 1 from its own self-exhaust, 4 Block, card lands in exhaust pile.
- mercy_of_the_deep: feel_no_pain 3 installed, 0 Block on play; a later exhaust pays 3 Block. Also pins the Power result-pile rule (card leaves combat: not in discard, not in exhaust).
- grand_conscription: 3 hand cards transformed into inazuma recruits, each conscripted + exhaust and priced at max(0, printed + CONSCRIPT_COST_DELTA); charge = 2 printed + 1 self-exhaust; card exhausts.
- press_the_advantage: 7 damage with the catalyst hydro aura applied, plus a cost_override conscript. Seed 13 is chosen deliberately so the recruit's printed cost is 3 — that makes the resulting cost 0 distinguishable from the standard -1 discount (at seed 0 the recruit was printed-1, where both rules give 0, so the assertion would not have been load-bearing).
- **engine-combat**: IMPORTANT: the target file /home/user/GItS/tier0/tests/test_pin_engine_combat.py ALREADY EXISTED and was already committed (17c2f85, "S15 (partial): pin tests for mutation-audit blind spots"). It already contains 3 test functions that pin exactly the two survivors in my group, so I wrote 0 new tests this run rather than modify/duplicate an existing file (hard constraint: never modify an existing file). pins_added=3 is the count of test functions in the file that cover HIGH-1/HIGH-2, not newly authored this run.

Instead of re-authoring, I VERIFIED the existing pins actually kill both mutants. I copied tier0/ to an isolated scratch tree, applied both mutations there (grant_charged_kit `>=` -> `>` at combat.py:50; _run_rounds `<` -> `<=` at combat.py:758), and ran the test file against the mutated copy: 2 failed, 1 passed — test_full_hand_defers_kit_burst_grant kills HIGH-1 and test_stall_cap_ends_fight_after_max_turns_rounds kills HIGH-2 (assert 31 == 30). The scratch copy has been deleted; no repo file was touched.

Coverage detail:
- HIGH-1 (full-hand Burst defer) is pinned by a PAIR: test_full_hand_defers_kit_burst_grant (hand at MAX_HAND_SIZE=10 -> no grant, hand stays 10, no kit_burst_granted event, meter stays full so the grant is deferred not lost) plus test_one_card_below_full_hand_still_grants_kit_burst (hand at 9 -> kit is appended), which keeps the first test from passing for the wrong reason (a blanket refusal to grant).
- HIGH-2 (MAX_TURNS stall cap) is pinned by test_stall_cap_ends_fight_after_max_turns_rounds: an unwinnable fight (1000 HP wall, no-op pilot) stops at exactly state.turn == C.MAX_TURNS with exactly MAX_TURNS round_hp emissions, and fight_end reports won=False, turns=30 — pinning both the boundary turn number and the capped-fight-is-a-loss classification.

Final real run on the repo file: `python3 -m pytest tier0/tests/test_pin_engine_combat.py -q` -> 3 passed.

Note for the orchestrator: an untracked file tier0/tests/test_pin_cards_kokomi_2.py is present in the working tree; it belongs to another group, not to me.
- **engine-effects**: TARGET FILE ALREADY EXISTED AND ALREADY COVERS ALL THREE SURVIVORS. /home/user/GItS/tier0/tests/test_pin_engine_effects.py is tracked at HEAD, committed in 17c2f85 ("S15 (partial): pin tests for mutation-audit blind spots - 13 files, 56 pins, all green"). It contains 7 test functions that pin exactly HIGH-3, HIGH-4 and MEDIUM-1. I added 0 new tests: creating a second file would violate the one-file constraint and duplicate existing coverage, and editing the tracked file would violate the never-modify-an-existing-file constraint. No repo file was created or modified by me.

VERIFICATION (this is the work I did): I copied tier0/ into scratchpad (/tmp/claude-0/-home-user-GItS/775fefc5-2e09-5e36-a322-995bfeae8336/scratchpad/mutE) and applied each surviving mutation to the copy, confirming each is genuinely killed. Baseline in the copy: 7 passed.

HIGH-3 (effects.py:443, detonate_bombs) - applied `dmg = bomb.damage + bonus + p.powers.get("bomb_damage_up", 0)` -> `dmg = bomb.damage + p.powers.get("bomb_damage_up", 0)`. Result: 1 failed, 6 passed. Killed by test_detonation_bonus_is_added_to_every_bomb_that_goes_off (two 4-damage bombs + bonus=3 must log [7, 7] and cost the enemy 14 HP). test_detonation_without_a_bonus_pays_only_the_bomb_damage anchors the other side (bonus is a rider, not a baseline).

HIGH-4 (effects.py:2069, prevent_damage_exhaust) - applied `prevented = min(incoming, stacks)` -> `prevented = stacks`. Result: 2 failed, 5 passed. Killed by test_prevention_ward_never_prevents_more_than_the_incoming_damage (6-stack ward vs a 2-damage hit prevents 2) and by test_a_small_hit_through_the_ward_pays_out_nothing_extra, which drives combat._enemy_turn end-to-end and pins that the player does not heal or bank Encore off surplus prevention. test_prevention_ward_pays_full_stacks_only_against_a_bigger_hit anchors the unclamped side.

MEDIUM-1 (effects.py:485, _add_token) - applied `if zone == "hand" and len(state.player.hand) < C.MAX_HAND_SIZE:` -> `<= C.MAX_HAND_SIZE`. Result: 1 failed, 6 passed. Killed by test_a_created_card_goes_to_discard_when_the_hand_is_already_full. test_a_created_card_lands_in_hand_with_one_slot_left anchors the boundary from below so the ceiling cannot be tightened by one instead.

After restoring the copy, 7 passed again. Final run against the real repo: `python3 -m pytest tier0/tests/test_pin_engine_effects.py -q` -> 7 passed in 0.67s. `git status --porcelain` shows only untracked files belonging to sibling agents in this same sweep (test_pin_cards_furina.py, test_pin_cards_kokomi_1.py, test_pin_cards_kokomi_2.py); nothing of mine.

ADJACENT GAP FOR THE PARENT (not one of my survivors, so not filed as should_be_findings): tier0/engine/effects.py:895 is the detonate op's plumbing, `detonate_bombs(state, enemy, bonus=fx.get("bonus", 0))`, which is what carries Remote Detonator's printed `bonus: 2` from the card row into detonate_bombs. HIGH-3's pin calls detonate_bombs directly, so the arithmetic at :443 is protected but a `fx.get("bonus", 0)` -> `0` mutation at :895 would still survive the suite. Worth queuing as a separate mutant if the sweep continues.
- **engine-potions**: 9 test functions cover all 7 survivors; 9 passed, 0 failed (python3 -m pytest tier0/tests/test_pin_engine_potions.py -q).

Mapping survivor -> test (each verified by actually applying the mutation to tier0/engine/potions.py and observing the named test fail, then restoring the file; md5 of the source confirmed unchanged afterwards):

- HIGH-12 (line 126, drop `* times`) -> test_multi_hit_telegraph_is_estimated_as_every_hit_not_one. Pins that a `times`=3 x 10-damage telegraph estimates at 30 and that the 30 (not 10) is what makes a 25 HP player drink the block potion. Paired CONTROL test test_single_hit_telegraph_of_the_same_size_does_not_trigger_the_drink pins the times=1 side so the multiplier test cannot be satisfied by an always-drink policy.
- HIGH-13 (lines 121-122, drop the ramp term) -> test_ramping_telegraph_estimate_grows_by_ramp_per_turn_after_ramp_after. Pins amount + ramp * max(0, turn - ramp_after) at four turns (past, just past, exactly at, and before ramp_after), including the max(0, ...) floor.
- HIGH-14 (line 186, `>` -> `>=`) -> test_defensive_drink_fires_at_exactly_the_safety_margin_not_one_hp_above (primary boundary pin: projected HP landing exactly on POTION_DEFENSIVE_MARGIN drinks; one HP of slack does not). test_defensive_drink_fires_when_block_only_partly_covers_the_hit also fails under this mutation.
- HIGH-15 (line 214, max_hp -> hp) -> test_big_hit_threshold_is_measured_against_max_hp_not_current_hp. A wounded player (hp 20 / max 80) facing a 15-damage telegraph: 15 is above 35% of current HP but below 35% of MAX HP, so weak_potion stays held; the same wounded player facing a telegraph above 35% of MAX HP does drink.
- HIGH-16 (line 183, drop `- p.block`) -> test_standing_block_is_netted_off_before_the_defensive_drink (25 Block fully absorbs a 20 telegraph, nothing drunk, no potion_used event), with test_defensive_drink_fires_when_block_only_partly_covers_the_hit as its zero-Block control.
- MEDIUM-6 (line 208, `<=` -> `<`) -> test_fire_potion_kill_range_includes_an_enemy_at_exactly_the_fire_damage. Enemy at exactly POTION_FIRE_DAMAGE HP is killed and the potion spent; enemy at POTION_FIRE_DAMAGE + 1 is not touched.
- MEDIUM-7 (line 174, widen gate with "") -> test_default_empty_node_context_never_reaches_the_offensive_branch. The loader/battery default node_kind "" leaves a fire-range kill unclosed and the potion held, with an identical elite-node fight as the control that does drink.

Two tests are deliberate paired controls (single-hit telegraph, partial-Block drink) rather than extra survivors: they keep the multi-hit and Block pins from passing for the wrong reason and each also independently fails under HIGH-14.

Nothing was skipped and nothing in this module needed a should_be_finding — every surviving mutant's current behaviour was coherent and directly pinnable at the engine/potions.py seam using conftest's make_state/make_enemy.

No existing file was modified; the target test file is the only file this task touched (it was subsequently swept into commit 17c2f85 by the parallel harness, contents unchanged).
- **engine-powers**: IMPORTANT PROVENANCE: /home/user/GItS/tier0/tests/test_pin_engine_powers.py already existed when I started — it was committed by an earlier partial run of this same sweep (commit 17c2f85, "S15 (partial): pin tests for mutation-audit blind spots — 13 files, 56 pins, all green"). I authored no new lines. Rewriting it would have violated the "never modify any existing file" constraint, and creating a second file would have violated "exactly ONE new test file", so I switched to verifying that the existing pins genuinely do the job the assignment asks for. They do.

WHAT THE 5 EXISTING TESTS PIN
HIGH-5 (metallicize adds, /home/user/GItS/tier0/engine/powers.py:119-120, `fighter.block += fighter.powers["metallicize"]`) — 3 tests:
  - test_metallicize_adds_to_block_the_fighter_already_holds (player, 7 block + 3 metallicize -> 10)
  - test_metallicize_adds_to_enemy_block_the_enemy_already_holds (enemy, 4 + 2 -> 6)
  - test_metallicize_stacks_on_top_of_block_carried_by_barricade (drives combat._player_turn with barricade so block survives the turn-start clear: 9 carried + 3 -> 12). This third one is the one that covers the exact divergence the audit described (block surviving refpowers.should_clear_block), not just a synthetic direct call to the hook.
MEDIUM-2 (stack cap clamp, /home/user/GItS/tier0/engine/powers.py:171, `new = min(new, max_stacks)`) — 2 tests:
  - test_capped_power_stops_at_max_stacks_across_applications (4 + 4 with max_stacks=6 -> 6; catches the running-total case the audit said no test exercised)
  - test_single_application_over_the_cap_lands_exactly_on_the_cap (9 with max_stacks=6 -> 6)

MUTATION VERIFICATION I RAN (this is the new work)
I applied each surviving mutation to the real source, ran the file, and reverted:
  - `fighter.block += ...` -> `fighter.block = ...`: 3 failed, 2 passed. All three metallicize tests fail. HIGH-5 killed.
  - `min(new, max_stacks)` -> `min(new, max_stacks + 1)`: 2 failed, 3 passed. Both cap tests fail (the off-by-one lands on 7 where the pin demands 6). MEDIUM-2 killed.
After both experiments I restored tier0/engine/powers.py via `git checkout --` and confirmed it is byte-identical to a pre-edit copy (`diff` clean) and that `git status` shows tier0/engine/powers.py unmodified. The only entries in git status are three untracked files belonging to other groups' sweeps (test_pin_cards_furina.py, test_pin_cards_kokomi_1.py, test_pin_cards_kokomi_2.py) — not mine, not touched.

FINAL RUN: `python3 -m pytest tier0/tests/test_pin_engine_powers.py -q` -> 5 passed in 0.05s, in isolation, clean import.

No survivors were skipped and nothing had to be dropped into should_be_findings — both behaviors pin coherently as the code actually does them today.
- **engine-reactions**: NO NEW TESTS WRITTEN — the work for this group was already completed and committed before this run. /home/user/GItS/tier0/tests/test_pin_engine_reactions.py already exists as a tracked file (commit cbb9e72, "S15 (partial): pin tests for engine-reactions and engine-resources blind spots") and already contains 5 passing tests that target exactly HIGH-8 and HIGH-9. Recreating the file would have meant overwriting an existing file, which the hard constraints forbid, and would have destroyed verified-working pins. pins_added is reported as 0 because I added zero test functions this run; the file's existing test count is 5.

Instead I VERIFIED the existing pins actually kill both survivors, by replaying each mutation on a throwaway copy of the tree in the scratchpad (no file in /home/user/GItS was modified at any point; the copy was deleted afterward):

- HIGH-9 (tier0/engine/reactions.py:102, `state.player.block += C.CRYSTALLIZE_BLOCK` -> `state.player.block = C.CRYSTALLIZE_BLOCK`): KILLED. Two tests fail under the mutant — test_crystallize_block_adds_to_block_the_player_already_holds (asserts 6 + CRYSTALLIZE_BLOCK after a geo reaction on a player already holding 6 Block; mutant yields 4) and test_two_crystallizes_in_a_row_stack_their_block (asserts 2 * CRYSTALLIZE_BLOCK; mutant yields 4). Result: "2 failed, 3 passed".

- HIGH-8 (tier0/engine/reactions.py:151, dropped the `* bonus` per-stack multiplier on the catalytic burst): KILLED. test_catalytic_burst_scales_with_reaction_bonus_stacks fails under the mutant with "At index 0 diff: 5 != 10" — it sets powers["reaction_bonus_spark_energy"] = 2, drives a pyro->hydro electrocharged reaction, and asserts the "catalytic"-sourced burst_income events equal [2 * C.CATALYTIC_BURST_PER_REACTION] plus sparks == 2. Result: "1 failed, 4 passed". The file also carries the one-stack unit case and a no-power baseline case, which bracket the scaling.

Final isolated run on current (unmutated) code: `python3 -m pytest tier0/tests/test_pin_engine_reactions.py -q` -> 5 passed. `git status --short` shows that path clean; the only untracked file in the repo is tier0/tests/test_pin_cards_klee_1.py, which belongs to a different group.

Nothing was skipped for untestability and nothing hit the drop-to-finding case: both behaviors pin coherently as the code writes them today (Block accumulates; catalytic burst is CATALYTIC_BURST_PER_REACTION multiplied by the reaction_bonus_spark_energy stack count).

Recommendation to the orchestrator: treat engine-reactions as already satisfied and do not re-dispatch it; if the sweep's bookkeeping needs a per-group count, engine-reactions contributes 5 pre-existing tests covering 2 of 2 survivors.
- **engine-relics**: Final run: `python3 -m pytest tier0/tests/test_pin_engine_relics.py -q` -> 2 passed (file passes in isolation).

PROVENANCE: the target file /home/user/GItS/tier0/tests/test_pin_engine_relics.py already existed on HEAD (commit 17c2f85, "S15 (partial): pin tests for mutation-audit blind spots"), already containing exactly the two pins this group needs. I did not author new tests this pass; I read the real source at tier0/engine/relics.py:224 and :266, verified each existing test diverges under its recorded mutation, and ran the file. `git status --short` confirms I modified nothing (only the three unrelated untracked test_pin_cards_* files from other groups are present). pins_added=2 counts the test functions in the file covering this group's survivors, not functions newly written by me.

One test per survivor; no test covers both.

HIGH-10 (relics.py:224, `met = p.hp <= threshold * p.max_hp` -> `<`), killed by test_conditional_power_is_active_at_exactly_the_threshold_hp: player at hp=40 / max_hp=80 with threshold 0.5. Current: 40 <= 40.0 is True -> strength 3. Mutant: 40 < 40.0 is False -> strength 0, assertion fails. The test brackets the boundary on both sides (hp=41 inactive, hp=40 active, back to hp=41 removed cleanly), so it pins the inclusive boundary itself rather than merely "active somewhere below the line" -- which is precisely the gap the audit flagged, since the pre-existing test_relics_dynamic.py tests only ever sit at hp=30 or hp=35 of max 80.

MEDIUM-5 (relics.py:266, `if sub in card.id or sub in (card.name or "")` -> `if sub in card.id`), killed by test_card_name_damage_bonus_matches_the_display_name_not_only_the_id: substring "Strike" against a card with id "pommel_smack" and name "Pommel Strike". The test carries an explicit `assert "Strike" not in card.id` so the id half provably cannot be what matches. Current: card_damage_bonus returns 3 and resolve_card leaves the enemy at 50-9=41. Mutant: returns 0 and the enemy sits at 44, failing both assertions.

Nothing in this group required dropping a test: both behaviours pin coherently as the code writes them today, so should_be_findings is empty.
- **engine-resources**: IMPORTANT CONTEXT: the target path /home/user/GItS/tier0/tests/test_pin_engine_resources.py ALREADY EXISTED, committed as cbb9e72 "S15 (partial): pin tests for engine-reactions and engine-resources blind spots" — i.e. an earlier partial run of this same sweep already produced this group's file. Under the hard constraint "never modify any existing file" I did not rewrite or append to it; instead I verified it does the job.

Verification performed:
1. Read the real code at tier0/engine/resources.py:283-292 (spend_encore). Current behavior: spent = min(p.encore, n); if spent, drain, emit "encore_spent", gain_fanfare(spent * C.FANFARE_PER_ENCORE_SPENT), and — only when p.burst_max is truthy — gain_burst(state, spent * C.BURST_PER_ENCORE_SPENT, "encore_spent"). C.BURST_PER_ENCORE_SPENT = 1 (tier0/constants.py:305).
2. Ran the file in isolation: `python3 -m pytest tier0/tests/test_pin_engine_resources.py -q` -> 2 passed (real, final count).
3. Kill-check: applied the exact surviving mutation (`spent * C.BURST_PER_ENCORE_SPENT` -> `C.BURST_PER_ENCORE_SPENT`) to a working copy of resources.py and re-ran the file — BOTH tests failed (test_encore_spend_pays_burst_per_point_not_per_spend_event and test_encore_spend_pays_burst_only_for_points_actually_drained). Source was restored from backup immediately; `git status --short tier0/engine/resources.py` is clean, working tree unmodified.

The two existing tests cover HIGH-7 between them (same behavior, two seams): the exact-spend case pins burst_energy == 5 * C.BURST_PER_ENCORE_SPENT plus the single burst_income telemetry event's amount/total, and the over-spend case pins that the per-point rate applies to the DRAINED amount (3) rather than the requested size (9). Each has a docstring stating the rule. No new file was created, since creating a second file at a different path would violate the "exactly ONE file, the path given" constraint and duplicate coverage that already exists and is proven to kill the mutant.
- **engine-state**: IMPORTANT: /home/user/GItS/tier0/tests/test_pin_engine_state.py ALREADY EXISTED, committed in 17c2f85 ("S15 (partial): pin tests for mutation-audit blind spots"). It already contains exactly the pins this group calls for, so I wrote nothing new rather than duplicate coverage or violate the "never modify any existing file" constraint. The working tree is clean (git status empty). pins_added=3 is the count of test functions in that file covering the two survivors, not a count of functions I authored this run.

Final run, in isolation: `python3 -m pytest tier0/tests/test_pin_engine_state.py -q` -> 3 passed in 0.02s.

Coverage audit against the real source (/home/user/GItS/tier0/engine/state.py:644-667), confirming each existing test would fail under its mutant:

HIGH-11 (state.py:663 CombatState.draw, `len(p.hand) >= C.MAX_HAND_SIZE` -> `>`), killed by two tests pinning both sides of the boundary:
- test_draw_into_full_hand_draws_nothing (hand already at 10): current code returns before popping; the mutant reads 10 > 10 as false, pops "d0" to an 11-card hand. Test asserts len(hand) == MAX_HAND_SIZE, draw_pile still ["d0","d1"], and cards_drawn_this_combat == 0 — all three assertions break under the mutant.
- test_draw_stops_at_max_hand_size_mid_draw (hand at 9, draw(3)): current code takes exactly one card and stops at the cap; the mutant takes two and lands on 11. Test asserts len(hand) == MAX_HAND_SIZE, hand[-1].id == "d0", leftover draw_pile ["d1","d2"], and cards_drawn_this_combat == 1.

LOW-1 (state.py:646 shuffle_discard_into_draw, `discard_pile + draw_pile` -> `draw_pile + discard_pile`), killed by test_reshuffled_discard_goes_on_top_of_the_draw_pile. Worth flagging the subtlety the audit itself raised: this mutant is equivalent along every shipped call path (state.py:661, effects.py:2061, effects.py:2089 all guard with `if not p.draw_pile`, so the draw pile is empty and both orderings agree). The existing test therefore calls shuffle_discard_into_draw directly with a non-empty draw pile — pinning the method's own contract at the unit seam rather than through a caller. That is the only seam where the operand order is observable, and it is pinning current behavior (discard splices ABOVE the survivors), not proposing a design. If a future caller ever reshuffles with cards still in the draw pile, this test is what holds the ordering.

No survivor was untestable and none required asserting incoherent behavior, so skipped and should_be_findings are both empty.
- **engine-statuses**: IMPORTANT: the target file /home/user/GItS/tier0/tests/test_pin_engine_statuses.py ALREADY EXISTED before I started, committed in 17c2f85 ("S15 (partial): pin tests for mutation-audit blind spots — 13 files, 56 pins, all green"). It already contains exactly 3 tests, one per assigned survivor. Per the hard constraint "never modify any existing file" I wrote nothing new; instead I verified the existing pins actually kill my three mutants. The pins_added count of 3 is the count of test functions in the file covering my survivors, not newly authored tests — zero lines were authored or changed by me. `git status --short` shows no modification from this agent (the only untracked entry, tier05/tests/test_pin_tier05_metrics.py, belongs to a sibling agent).

Mutation verification (done in a throwaway copy of tier0/ under the scratchpad, so no repo file was ever touched): I applied each of the three mutations to the copied tier0/engine/statuses.py and ran the pin file against it. Each mutant killed exactly one test, 1 failed / 2 passed each time:
- rarity="basic" -> rarity="status" kills test_injected_status_cards_carry_basic_rarity_not_status_rarity (HIGH-6)
- cost=0 -> cost=1 kills test_injected_status_cards_cost_zero (MEDIUM-3)
- tags=list(spec.get("tags", [])) -> tags=spec.get("tags", []) kills test_each_injected_status_owns_its_tag_list (MEDIUM-4)
The tag-aliasing test correctly targets "dazed": it is the only spec in _SPECS with a "tags" key, so it is the only id where dropping the list() copy actually aliases the module-level template (every other id gets a fresh [] from spec.get's default even under the mutant).

FINAL RUN: python3 -m pytest tier0/tests/test_pin_engine_statuses.py -q => 3 passed in 0.02s.

Cross-module observation, NOT filed as a should_be_finding because no test was dropped and the pinned behavior is coherent on its own: make_status stamps rarity="basic" at tier0/engine/statuses.py:49, while status-filtered card selection matches on rarity == "status" at tier0/engine/effects.py:1389 (`pool = [c for c in pool if c.rarity == "status"]`) and the same predicate in tier0/pilot/policy.py:262. So a `filter: status` exhaust can never remove an injected clog. The existing test pins the "basic" fact and its docstring already states the consequence explicitly, which is the right call under the iron rule — but the mismatch is a live design question for whoever owns §10.2/§10.9, and it is the thing HIGH-6's severity was really about. If the sweep wants a downstream pin (an integration test asserting a status-filtered exhaust leaves an injected Dazed in hand), it needs to go in a different file since this one may not be edited.
- **tier0-harness**: All 3 survivors covered, one test each, file green: `python3 -m pytest tier0/tests/test_pin_tier0_harness.py -q` -> 3 passed (1.48s).

State note: the target file already existed at HEAD (commit 17c2f85, "S15 (partial)") with pins for exactly these three survivors, so this run was a verification pass rather than a fresh write; no file in the repo was created or modified (git status for the path is clean). I did not rewrite tests that already pin current behavior correctly.

Kill-verification (not just green-on-current): I copied tier0/ into the scratchpad, applied all three audited mutations to the copy (axes.py:169 0.7 -> 0.5; metrics.py:199 dropping the `+ sleeps` term; runner.py:99-100 operand swap), and ran the same file against the mutated tree — all 3 tests FAILED, then the scratch copy was deleted. So each pin genuinely kills its mutant and passes on current code.

Per-survivor:
- HIGH-19 (tier0/harness/axes.py:169, _turns_to_own_peak) -> test_setup_tax_clock_stops_at_seventy_percent_of_own_peak_window. Synthetic FightStats with turns=6 and damage_by_turn={3:18, 6:30} gives trailing 3-turn windows 0,0,6,6,6,10; 70% of the peak (7) is cleared only at turn 6, while any threshold <=0.6*peak returns turn 3. Also asserts raw_axes(..., battery=False)["A7_setup_tax"] == 6.0 so the published axis value is pinned, not just the helper.
- MEDIUM-9 (tier0/harness/metrics.py:199, extract) -> test_scripted_enemy_sleeps_count_as_enemy_actions_in_control_uptime. 3 intents + 1 enemy_sleep + 1 companion frozen_action pins enemy_actions == 4 (not 3), control_negated == 0.5, and summarize()["control_uptime"] == 0.125 (0.5/4, never 0.5/3).
- MEDIUM-10 (tier0/harness/runner.py:99-100, score_config) -> test_pressure_delta_is_punisher_winrate_minus_attrition_winrate. Pins both the identity (delta == punisher - attrition, recomputed from result["stats"]) and the observed sign for the reference starter (punisher 0.55 < attrition 1.0, so delta < 0), which is what makes the swap detectable rather than a symmetric no-op.

Nothing was untestable at this seam, and no current behavior resisted coherent pinning, so skipped and should_be_findings are both empty.
- **tier0-pilot**: The target file /home/user/GItS/tier0/tests/test_pin_tier0_pilot.py ALREADY EXISTS and is tracked (committed in 17c2f85 "S15 (partial): pin tests for mutation-audit blind spots"), not untracked/scratch. It already contains 4 passing pins that cover both of this group's survivors, so I wrote nothing new rather than violate the "never modify any existing file" constraint. pins_added=0 means "added this run"; the file itself holds 4 test functions.

Final run from repo root: `python3 -m pytest tier0/tests/test_pin_tier0_pilot.py -q` -> 4 passed in 0.03s.

Coverage check against the two survivors (verified by reading tier0/pilot/policy.py):

HIGH-18 (policy.py:673 _incoming_damage, `total += int(per_hit) * intent.get("times", 1)` -> `total += int(per_hit)`): killed twice over.
- test_incoming_damage_counts_every_hit_of_a_multi_hit_intent asserts _incoming_damage == 18 for a 6-damage intent with times=3 (mutant yields 6).
- test_block_is_valued_against_the_whole_multi_hit_swing asserts _block_value == 15 against that same telegraph; _block_value (policy.py:289-309) clamps block worth to _incoming_damage, so under the mutant it would clamp to 6.

LOW-2 (policy.py:338 _scaling_value, `val += min(amount, 6) * 3` -> `min(amount, 7) * 3`): killed by test_self_power_scaling_value_is_capped_at_six_stacks, which asserts a 7-stack self apply_power still scores 18 (mutant yields 21). The fourth test pins that the capped value is still multiplied by the setup taper, which is the same seam's other half.

Both pins are behavior-as-written, not design: they assert the current multiplier and the current cap value, and they pass on unmutated code.
- **tier0-roster**: Both survivors were already pinned by /home/user/GItS/tier0/tests/test_pin_tier0_roster.py, committed in the earlier partial S15 commit 17c2f85. I did not create a duplicate file and modified nothing in the repo. Instead I verified the existing pins genuinely kill the two mutants: copied tier0/tier05/docs into the scratchpad, applied both mutations (tier0/constants.py:651 MAP_TREASURE_FLOOR 8 -> 7, and tier0/roster.py:144 IDS = tuple(sorted(c.id for c in ROSTER))), and re-ran the file — all 3 tests FAILED under mutation and all 3 PASS on the real tree. Final real run in isolation: `python3 -m pytest tier0/tests/test_pin_tier0_roster.py -q` -> 3 passed. Coverage mapping: HIGH-17 (treasure-floor index) is pinned by BOTH test_treasure_floor_is_map_index_eight (literal C.MAP_TREASURE_FLOOR == 8, no read-back through the constant) and test_generated_maps_put_every_treasure_room_on_floor_eight (generated maps carry Treasure only on hard-coded floor 8, tier05/maps.py:72 being the single consumer); MEDIUM-8 (roster ship order) is pinned by test_roster_ids_are_declaration_order_not_alphabetical, which asserts IDS is positionally ROSTER's own order, equals ("klee","furina","kokomi"), and is NOT the sorted tuple. Nothing was dropped, and no current behavior here was incoherent, so should_be_findings is empty.
- **tier05-draft**: NOTE ON PROVENANCE: the target file /home/user/GItS/tier05/tests/test_pin_tier05_draft.py already existed, committed in 17c2f85 ("S15 (partial): pin tests for mutation-audit blind spots"), and already contained exactly one test per survivor in this group. I wrote no new tests and modified nothing in the repo; the 3 pins counted above are the pre-existing tests, which I verified rather than duplicated. If the orchestrator counts only newly authored tests, this group's delta is 0.

VERIFICATION (empirical, repo untouched): I copied tier05/draft.py into the scratchpad three times, applied each surviving mutation to the copy, imported the copies under separate module names, and re-ran the pinned assertions against them. Script: /tmp/claude-0/-home-user-GItS/775fefc5-2e09-5e36-a322-995bfeae8336/scratchpad/s15draft_verify.py

- HIGH-20 (tier05/draft.py:563): dropping `* STATIC_AOE_MULT` makes _static_power(undercurrent) == 3.0 instead of 6.0, and reorders cleave_like (8.0) below waterspout (10.0). test_all_enemies_damage_is_priced_at_the_aoe_multiple_of_its_face asserts both -> KILLED.
- HIGH-21 (tier05/draft.py:1243): `n >= DRAFT_LEAN_CAP` -> `n > DRAFT_LEAN_CAP` makes assigned_policy return blast_radius on a 15-card deck instead of the Power durin_witchs_flame. test_lean_gate_engages_at_exactly_draft_lean_cap_cards asserts the below-cap/at-cap pair -> KILLED.
- MEDIUM-11 (tier05/draft.py:1564): dropping `+ 1.0` makes the sub-point near-miss decision score 1 regret instead of 0. test_draft_regret_needs_a_full_point_of_hindsight_advantage asserts 0 for a rival ahead by less than a point and 1 for a rival ahead by more -> KILLED.

FINAL RUN: python3 -m pytest tier05/tests/test_pin_tier05_draft.py -q -> 3 passed in 0.75s (file passes in isolation, imports cleanly).

Repo state: git status shows only tier0/tests/test_pin_cards_klee_1.py untracked, which belongs to another worker in this sweep, not to me. I created no files under /home/user/GItS.
- **tier05-economy**: NO NEW FILE WRITTEN — the target path already exists, tracked and green, and already pins all three survivors. It was committed earlier in this same sweep (17c2f85 "S15 (partial): pin tests for mutation-audit blind spots — 13 files, 56 pins, all green"), so this group appears to have been re-dispatched. Writing the file would have meant overwriting an existing file, which the hard constraints forbid, and the tests it already contains are exactly the narrow boundary pins the survivors call for. It is unmodified vs HEAD (`git status` clean) and I changed nothing anywhere in the repo.

VERIFICATION I DID INSTEAD. Ran /home/user/GItS/tier05/tests/test_pin_tier05_economy.py in isolation: 6 passed in 0.58s (6 test functions, 2 per survivor — the boundary plus its control). Then I confirmed each mutant is genuinely killed, by recompiling each mutated function into its module's LIVE globals (so the banner test's mock.patch.object still applies) and re-running the tests; script at /tmp/claude-0/-home-user-GItS/775fefc5-2e09-5e36-a322-995bfeae8336/scratchpad/s15econ_verify2.py.

HIGH-26 (tier05/events.py:378, `st.hp = min(st.hp, st.max_hp)` deleted): killed by test_max_hp_cost_clips_current_hp_down_to_the_new_maximum (hp 70/max 70, unrest_site -8 -> expects hp 62; mutant leaves hp 70). Control test_max_hp_cost_leaves_current_hp_alone_when_it_is_already_below still passes under the mutation, as it should — it pins that the clip is a ceiling, not an assignment.

HIGH-27 (tier05/events.py:309, `<= 0` -> `< 0`): killed by test_option_that_would_leave_exactly_zero_hp_is_not_available (hp 5, option hp -5 is withheld; mutant offers it). Control test_option_that_leaves_one_hp_is_still_available pins the legal side of the same boundary.

MEDIUM-13 (tier05/rewards.py:148, `<=` -> `<`): killed by test_roster_exactly_at_the_slot_count_features_all_without_consuming_rng — a roster of exactly C.BANNER_FEATURED_SLOTS features all directly and the rng is untouched (asserted by comparing rng.random() against a fresh Random(7)); the mutant routes through rng.sample, producing the same banner but a desynchronised Random. Control test_roster_one_over_the_slot_count_samples_and_consumes_rng pins the sampling side.

Nothing was untestable and nothing had to be dropped, so skipped and should_be_findings are both empty. If the orchestrator's rollup needs a nonzero pin count for this group, the 6 pins are already in the tree from 17c2f85 — they should be counted there, not added again.
- **tier05-metrics**: IMPORTANT: I authored 0 NEW tests this run. The target file /home/user/GItS/tier05/tests/test_pin_tier05_metrics.py ALREADY EXISTED, committed clean at 60f2004 ("S15 (partial): pin tests - klee card batch 2 and tier05 metrics blind spots"), containing exactly 2 test functions that already pin exactly HIGH-24 and HIGH-25. pins_added=2 is the count of test functions in the file covering my survivors, not new work by me. I created no file and modified nothing (git status is clean except tier0/tests/test_pin_cards_klee_1.py, an untracked file belonging to a different group, which I did not touch).

Rather than take the pre-existing coverage on faith, I verified both mutants are genuinely killed. Method: a scratch harness at /tmp/claude-0/-home-user-GItS/775fefc5-2e09-5e36-a322-995bfeae8336/scratchpad/mutcheck.py reads tier05/run_metrics.py source, applies each mutation as a single-occurrence string substitution (asserted count==1), exec's the mutated source into a fresh module, rebinds act_funnel/route_profile on the imported test module (the test file imports them at module scope, so rebinding takes effect), and re-runs both tests.

Results:
- HIGH-24 (tier05/run_metrics.py:150, `r.death_node >= a * tpl` -> `r.death_node > a * tpl`): KILLED by test_a_run_that_dies_on_an_acts_first_floor_still_reached_that_act. The test builds a run with death_node=0 (act 0 boundary) and one with death_node=C.MAP_FLOORS (act 1 boundary) and asserts funnel[0]["reached"]==2 / funnel[1]["reached"]==1; the mutant drops both to 1 / 0. It pins the boundary on both acts, not just floor 0, so the off-by-one cannot hide behind a==0.
- HIGH-25 (tier05/run_metrics.py:120, `if 1 <= k <= 4` -> `if 1 <= k <= 5`): KILLED by test_an_act_with_five_elites_falls_outside_the_target_band. The test asserts in_target_band==0.5 for a {4:1, 5:1} distribution and additionally route_profile([five])["in_target_band"]==0.0, which pins the exclusive side of the band directly; the mutant yields 1.0 for both.
- Baseline on unmutated code: both tests pass.

Final real run: `python3 -m pytest tier05/tests/test_pin_tier05_metrics.py -q` -> 2 passed in 0.02s (isolation, from repo root).

Nothing skipped, and no should_be_findings: both behaviors pin coherently as the code writes them today (inclusive `>=` reached boundary, exclusive top-of-band at 4 elites). No new gap was found in this group.
- **tier05-model**: IMPORTANT: the target file /home/user/GItS/tier05/tests/test_pin_tier05_model.py ALREADY EXISTED, committed in 17c2f85 ("S15 (partial): pin tests for mutation-audit blind spots — 13 files, 56 pins, all green"). It already contains 4 pin tests covering exactly my 3 survivors. Since the hard constraints forbid modifying an existing file and forbid creating a second file at a different path, I did not write new tests; instead I VERIFIED the existing pins actually kill each surviving mutant by applying each mutation to tier05/model.py in turn, running the file, and restoring the source (git status confirms tier05/model.py is unmodified; the two untracked test_pin_cards_kokomi_*.py files are from sibling agents, not me).

Kill verification (each mutation applied alone, then reverted):
- HIGH-22 — tier05/model.py:474, `hp = min(max_hp, hp + round(C.REST_HEAL_FRACTION * max_hp))` -> `hp = hp + round(...)`: FAILS test_rest_heal_is_capped_at_max_hp (1 failed, 3 passed). The test scripts an "NRB" map, wins the first fight for exactly 12 HP, enters the rest at 50/62 and pins hp_by_node[1] == 62; uncapped it would be 69.
- HIGH-23 — tier05/model.py:431, drop `gold -= C.SHOP_RELIC_PRICE` while keeping the affordability check and the 150g purchase-log entry: FAILS test_shop_relic_purchase_debits_its_price_from_gold (1 failed, 3 passed). Scripts "TT$" with grant_relics=True and pins res.gold == 99 + 40 + 40 - 150 == 29.
- MEDIUM-12 — tier05/model.py:146, `(n_block - 1) / max(1, len(deck) - 1)` -> `n_block / max(1, len(deck) - 1)`: FAILS test_rest_keeps_block_card_when_cut_would_break_defense_quota (1 failed, 3 passed). Deck of 1 basic blocker + 5 non-block cards: post-cut density 0/5 fails the quota so rest_action returns ("upgrade", "duck_and_cover"); under the mutant the pre-cut 1/5 clears it and the blocker is cut. Its partner test_rest_thins_block_card_when_quota_survives_the_cut pins the other side of the same rule (2 blockers in 6 -> ("remove", "duck_and_cover")) and is mutation-insensitive on its own, so the two tests together fence the boundary — that is the one place where two tests pin one behavior.

Final real run: `python3 -m pytest tier05/tests/test_pin_tier05_model.py -q` -> 4 passed, 3 warnings in 0.67s (the 3 warnings are pre-existing relic-pool UserWarnings emitted by tier05/relics.py:78, not test failures). Nothing dropped, nothing skipped, no should-be findings: all three behaviors pin coherently as the code does them today.
- **tier05-route**: The target file /home/user/GItS/tier05/tests/test_pin_tier05_route.py ALREADY EXISTED, committed in 17c2f85 ("S15 (partial): pin tests for mutation-audit blind spots"), and already covers all 4 tier05-route survivors. Creating a second file at that path was impossible and rewriting it would have violated the no-modify constraint, so instead I VERIFIED it kills every assigned mutant.

Verification method: copied tier0/ and tier05/ into a scratch sandbox (no repo file touched), applied each mutation there individually, ran `python3 -m pytest tier05/tests/test_pin_tier05_route.py -q`, then restored.

- HIGH-28 (route.py:100, -8.0 -> -1.0): 2 failed, 3 passed. Killed by test_repelled_elite_is_worth_minus_eight_regardless_of_the_policy_want (asserts the exact constant, and that it REPLACES rather than discounts the policy's want -- checked against both hunter's ELITE:10.0 and a cautious-style ELITE:1.0) and by test_elite_repulsion_outweighs_a_shop_and_treasure_on_the_same_lane (asserts the magnitude is large enough to flip an actual _plan/hunter routing decision: elite lane 4.0 vs plain lane 8.0). These two are the pair covering HIGH-28.
- HIGH-29 (route.py:128, elites_taken < 4 -> < 3): 1 failed, 4 passed. Killed by test_hunter_still_takes_a_fourth_elite_at_full_hp_but_never_a_fifth (full-hp run with 3 taken still routes into the elite; with 4 taken it does not).
- HIGH-30 (maps.py:131, 0 <= c < width -> c < width - 1): 1 failed, 4 passed. Killed by test_carved_paths_can_occupy_every_column_above_the_first_floor (max floor width above floor 0 reaches C.MAP_MAX_FLOOR_WIDTH; deliberately excludes floor 0, whose 6 columns come from the spread starts and survive the mutation).
- HIGH-31 (cells.py:228, acts_completed >= 1 -> > 1): 1 failed, 4 passed. Killed by test_arm_reduces_results_to_the_standard_summary_row (act1 == 2/3 over acts_completed 0/1/3; also pins win, acts, decksize, fights, results passthrough and decks).

Final real run in the repo: 5 passed in 0.06s. `git status` clean -- no files created or modified by me.

## Non-goals honored

- No source file was modified — only new test files were created.
- No test encodes intended-but-unimplemented behavior; disagreements with 'what should be' were to be filed as findings, and none arose.
- The mutation-audit ranking (review/mutation-audit/blind-spot-report.md) remains the authority on WHY each pin exists; pins state the behavioral constraint in their docstrings.