"""Turn loop (spec §3/§4.5). One function: run_fight.

Player turn: bombs detonate -> auras tick -> power hooks -> draw + energy ->
pilot plays until done -> discard hand -> power decay.
Enemy turns: scripted intents, no AI. Asleep enemies skip; frozen enemies
act at -50% damage (Frozen v2, principles v1.5).
"""

from __future__ import annotations

import random
from typing import Callable

from tier0 import constants as C
from tier0.engine import (effects, potions, powers, reactions, refpowers,
                          relics, resources)
from tier0.engine.state import Card, CombatState, Enemy, Player

# A pilot is a callable: (state) -> Card | None (None = end turn).
Pilot = Callable[[CombatState], Card | None]


def spark_threshold(state: CombatState) -> int:
    # True Spark Knight: free attack at 2 sparks instead of 3.
    return max(1, C.SPARKS_FOR_FREE_ATTACK
               - state.player.powers.get("spark_threshold_down", 0))


def grant_charged_kit(state: CombatState) -> None:
    """v1.9: the Burst is kit, not loot. When the meter is full, the kit
    card is granted to hand; casting empties the meter (play_card), so a
    refill re-grants it.

    Two call sites cover every gain: all burst-energy sources (reactions,
    detonation splash, the burst_energy op, skill tags) fire inside the
    player-turn window, either in the turn-start trigger block or during a
    card's resolution -- so checking at turn start and after each play is
    exhaustive without instrumenting the five gain sites individually.

    Respects MAX_HAND_SIZE: a full hand defers the grant to the next check
    rather than dropping it -- the meter stays full, so it cannot be lost.
    """
    p = state.player
    if not p.burst_max or p.burst_energy < p.burst_max:
        return
    for kit in p.kit_cards:
        if any(c.id == kit.id for c in p.hand):
            continue
        if len(p.hand) >= C.MAX_HAND_SIZE:
            return
        p.hand.append(kit)
        state.emit("kit_burst_granted", card=kit.id)


def _revive_player_if_needed(state: CombatState) -> bool:
    """Resolve a held Fairy at combat checkpoints after player HP can move."""
    if state.player.alive or not state.player.potions:
        return False
    return potions.try_fairy_revive(state)


def card_playable(state: CombatState, card: Card) -> bool:
    if card.requires == "burst_energy_full":
        if state.player.burst_energy < state.player.burst_max:
            return False
    elif card.requires:
        raise ValueError(f"unknown requires {card.requires!r}")
    if card.encore_cost and state.player.encore < card.encore_cost:
        return False        # "Spend N Encore:" cost line -- a gate, never
                            # an overdraw (that is the spend_encore op)
    return card_cost(state, card) <= state.player.energy


def card_cost(state: CombatState, card: Card) -> int:
    if card.cost == "X":
        # An X card spends the whole bank and NO cost modifier is consulted --
        # this early return is the game's own shape, not a tier0 shortcut.
        # CardEnergyCost.GetAmountToSpend() opens with
        # `if (CostsX) return Owner.PlayerCombatState?.Energy ?? 0;`, returning
        # before GetWithModifiers; and GetWithModifiers itself opens with
        # `if (CostsX) return num;` BEFORE its
        # `Hook.ModifyEnergyCostInCombat(...)` line. So the ...InCombatLate
        # hook that FreeAttack (Unrelenting) and Corruption implement never
        # runs on an X card, even though each sets modifiedCost = 0
        # unconditionally once reached. Whirlwind is therefore never freed by a
        # FreeAttack stack -- and must not be, since X is the energy actually
        # spent (EnergyCost.CapturedXValue), so a freed Whirlwind would resolve
        # at X = 0 and deal nothing. Same conclusion as the R34 spark exemption
        # below, reached independently. Pinned by
        # test_refpowers.test_free_attack_does_not_zero_an_x_cost_attack.
        return state.player.energy
    cost = card.cost
    if card.cost_reduction_per_attack_this_turn:
        cost = max(0, cost - (card.cost_reduction_per_attack_this_turn
                              * state.attacks_played_this_turn))
    if card.is_companion and state.companion_cost_delta_this_turn:
        cost = max(0, cost + state.companion_cost_delta_this_turn)
    # Leading Role (card-level texture, kickoff §3.2): the FIRST
    # Spotlighted card each turn costs less. This is a Furina-card power
    # granting economy, not the Spotlight baseline -- §2.2a governs the
    # multiplier, and the multiplier has no path here.
    p = state.player
    if (p.spotlight and card.character == p.spotlight
            and state.spotlighted_cards_this_turn == 0):
        cost = max(0, cost - p.powers.get("spotlight_discount", 0))
    if (card.type == "attack"
            and state.player.sparks >= spark_threshold(state)):
        return 0
    # Base-game parity (FreeAttack / Corruption): checked AFTER the spark
    # branch, so a spark-freed attack spends the bank rather than a stack.
    # Precedence pinned by
    # test_refpowers.test_free_attack_and_spark_are_both_consumed.
    if refpowers.free_cost(state, card):
        return 0
    return cost


def play_card(state: CombatState, card: Card) -> None:
    p = state.player
    cost = card_cost(state, card)
    # R34: X-cost cards are exempt from spark spend. A Spark-freed X card
    # would resolve at X = 0 -- the mechanic cannot coherently apply, and
    # without the exemption an X attack at 0 energy trips this predicate
    # (paid 0, printed != 0) and whiffs the whole spark bank.
    # R39 (user ruling 2026-07-21): effects that READ the spark bank see it
    # as it was when the card was played, before this card's own spend.
    # Gleeful Barrage ("2 + Sparks hits") otherwise fought itself: reaching
    # the threshold that makes it free is exactly what deleted the sparks it
    # counts, so at exactly 3 sparks it went free AND dropped to 2 hits. Only
    # attacks spend, and the two has_spark cards are skills, so this card is
    # the whole blast radius.
    state.sparks_at_play = p.sparks
    if (card.type == "attack" and cost == 0
            and p.sparks >= spark_threshold(state)
            and card.cost != 0 and card.cost != "X"):
        p.sparks -= spark_threshold(state)
        state.emit("sparks_spent")
    if card.cost == "X":
        state.current_x = cost                # X = energy actually spent
    state.current_card_cost = cost
    p.energy -= cost
    if card.encore_cost:
        resources.spend_encore(state, card.encore_cost)   # gated playable
    p.hand.remove(card)
    state.cards_played_this_turn += 1
    state.emit("play", card=card.id, cost=cost, energy_left=p.energy)
    if p.spotlight and card.character == p.spotlight:
        # Ovation (kickoff §4): each Spotlighted card played is Fanfare.
        # Counted BEFORE resolution so the reserve per-turn cap (OFF by
        # default) can compare against this play's own ordinal.
        state.spotlighted_cards_this_turn += 1
        state.emit("spotlight_card_played", card=card.id)
        resources.gain_fanfare(state, C.FANFARE_PER_SPOTLIGHT_CARD, "ovation")
        # Card-level Spotlight texture (sheet pass 1, ratified design
        # space): Supporting Cast draws on the FIRST Spotlighted card
        # each turn; post-flip Standing Ovation's trickle uses the same
        # first-play window (spotlight_encore_first, pass 3 — the
        # per-play rate was the hot-sustain driver both times it was
        # tried). spotlight_encore (EVERY play) remains engine-supported
        # as the archived pre-flip rate.
        if state.spotlighted_cards_this_turn == 1:
            n = p.powers.get("spotlight_draw", 0)
            if n:
                state.draw(n)
                state.emit("extra_draw", amount=n)
            n = p.powers.get("spotlight_encore_first", 0)
            if n:
                resources.gain_encore(state, n)
        n = p.powers.get("spotlight_encore", 0)
        if n:
            resources.gain_encore(state, n)
    if card.requires == "burst_energy_full":
        p.burst_energy = 0                    # playing the Burst empties it
        state.emit("burst_cast", card=card.id)
    if p.burst_max and "skill_tag" in card.tags:
        p.burst_energy += C.BURST_PER_SKILL_TAG
    replays = 1
    if card.is_companion:
        state.companions_played.append(card.id)
        if state.replay_next_companion > 0:   # Study Buddy
            replays += state.replay_next_companion
            state.replay_next_companion = 0
    # OneTwoPunch resolves the play COUNT once, but Before/AfterCardPlayed fire
    # per play index -- so a doubled attack pays Rage twice, counts twice for
    # Juggling, and burns two FreeAttack stacks.
    replays += refpowers.extra_replays(state, card)
    for _ in range(replays):
        snap = refpowers.before_card_played(state, card)
        effects.resolve_card(state, card)
        refpowers.after_card_played(state, card, snap)
    if card.kit_card:
        pass                                  # returns to the kit, no pile
    else:
        # CardModel.GetResultPileTypeForCardPlay: a played Power card is
        # REMOVED FROM COMBAT (PileType.None), not exhausted. tier0 used to
        # exhaust it, which would have paid out FeelNoPain and DarkEmbrace on
        # all 11 of Ironclad's Power cards (recon BUG 1).
        dest = refpowers.result_pile(state, card)
        if dest == "exhaust":
            refpowers.exhaust_card(state, card)
        elif dest == "discard":
            p.discard_pile.append(card)
    # Selector-v4 Guest Star exception: a generated guest can take the light
    # at depth one, but it is a one-card cameo rather than a persistent partner.
    # Return the Spotlight to Furina after that card performs so the designation
    # cannot strand itself on an absent temporary character. This automatic
    # stage reset is not a player move and therefore triggers no move payoffs.
    if (card.generated_by_guest_star and card.character
            and p.spotlight == card.character and p.character_id):
        p.spotlight = p.character_id
        state.emit("spotlight_returned", character=p.character_id)
    grant_charged_kit(state)
    # Self-damage and Encore overdraw resolve inside a card play rather than
    # the enemy-hit funnel. Give Fairy the same lethal checkpoint, then update
    # HP-threshold relics before the pilot chooses another card.
    _revive_player_if_needed(state)
    if p.relic_effects:
        relics.reevaluate_conditionals(state)


def _player_turn(state: CombatState, pilot: Pilot) -> None:
    p = state.player
    state.turn += 1
    state.cards_played_this_turn = 0
    state.in_player_turn = True              # StS2 CombatState.CurrentSide
    refpowers.reset_turn_counters(state)
    # StS2 site A (BeforeSideTurnStart) -- BEFORE the block clear and BEFORE
    # the draw. Aggression pulls Attacks out of the discard pile here; running
    # it after the draw would over-fill the hand versus the real game.
    refpowers.side_turn_start_early(state)
    if refpowers.should_clear_block(p):      # Barricade suppresses the clear
        p.block = 0

    state.companion_cost_delta_this_turn = 0     # Friendly Visit expires
    state.replay_next_companion = 0              # Study Buddy expires
    state.splash_procs_this_turn = 0             # detonation_splash cap
    state.reactions_this_turn = 0                # Chevreuse predicate window
    state.spotlighted_cards_this_turn = 0        # Ovation / reserve cap
    state.spotlight_moved_this_turn = False      # selector-payoff window

    for enemy in list(state.living_enemies):     # bombs from last turn go off
        if enemy.bombs:
            effects.detonate_bombs(state, enemy)
    reactions.tick_auras(state)
    powers.on_turn_start(state, p)
    _revive_player_if_needed(state)             # player DoT can be lethal
    if not p.alive or state.over:
        return
    effects.player_turn_start_triggers(state)
    _revive_player_if_needed(state)             # Salon upkeep can overdraw HP
    if not p.alive or state.over:
        return

    p.energy = refpowers.energy_for_turn(state)      # site C, + Pyre
    state.draw(C.CARDS_DRAWN_PER_TURN, from_hand_draw=True)   # site D
    # StS2 sites E/F (AfterPlayerTurnStart, AfterSideTurnStart) -- AFTER the
    # draw. tier0's powers.on_turn_start above is a PRE site; anything that
    # reads the hand or must land post-draw belongs here instead.
    refpowers.player_turn_start_late(state)
    _revive_player_if_needed(state)             # Inferno / Mantle self-damage
    if not p.alive or state.over:
        return
    grant_charged_kit(state)                 # turn-start gains + full-hand defer

    # Combat-side relics (dead branch on the battery). combat_start_* fires
    # once, HERE on turn 1 -- AFTER the block clear / energy reset / draw above,
    # so combat-start block survives the clear and the turn-1-only energy/draw
    # riders stack on the turn's own refill and draw. Per-turn hooks
    # (every_n_turns_*, conditional_power re-eval) run every turn.
    if p.relic_effects:
        if state.turn == 1:
            relics.apply_combat_start(state)
        relics.on_player_turn_start(state, state.turn)

    # Combat-side potions (dead branch on the battery: potions empty). Bounded
    # greedy use-policy at turn start, AFTER the draw/energy/relic setup so a
    # defensive block or an offensive strength lands on this turn's real state.
    if p.potions:
        potions.try_use_potions(state)
        if p.relic_effects:
            # Blood Potion can cross Red Skull's HP threshold after its normal
            # turn-start evaluation and before the first card is chosen.
            relics.reevaluate_conditionals(state)

    seen_states: set[tuple] = set()
    while not state.over:
        if state.cards_played_this_turn >= C.MAX_CARDS_PER_TURN:
            state.emit("degeneracy", kind="INFINITE", reason="card_cap")
            break
        snapshot = (tuple(sorted(c.id for c in p.hand)), len(p.draw_pile),
                    len(p.discard_pile), p.energy)
        if snapshot in seen_states:
            state.emit("degeneracy", kind="INFINITE", reason="state_repeat")
            break
        card = pilot(state)
        if card is None:
            break
        seen_states.add(snapshot)
        play_card(state, card)

    # StS2 site I (BeforeSideTurnEndEarly). PlatingPower's own source comment:
    # "We do this in early so that it triggers before end-of-turn damage
    # effects" -- which is precisely what player_turn_end_triggers holds.
    refpowers.before_side_turn_end_early(state)
    effects.player_turn_end_triggers(state)      # Oz, Sparks 'n' Splash, ...
    _revive_player_if_needed(state)
    grant_charged_kit(state)     # Salon-tick particles can fill the meter
                                 # at turn end; the Burst's Retain keeps it
    # Burst cards have Retain (principles v1.4): they stay in hand.
    # Ethereal cards (the Spotlight selector) vanish to exhaust instead of
    # discarding -- an unplayed selector must never circulate as loot.
    retained = [c for c in p.hand if "burst" in c.tags or c.retain]
    ethereal = [c for c in p.hand
                if "ethereal" in c.tags
                and "burst" not in c.tags and not c.retain]
    p.discard_pile.extend(c for c in p.hand
                          if "burst" not in c.tags and not c.retain
                          and "ethereal" not in c.tags)
    p.hand = retained
    for c in ethereal:
        # DarkEmbrace counts ethereal exhausts instead of drawing on them; the
        # deferred draw is flushed in powers.on_turn_end below, i.e. AFTER this
        # hand flush -- which is the stated reason the source defers it.
        refpowers.exhaust_card(state, c, caused_by_ethereal=True)
    state.in_player_turn = False
    powers.on_turn_end(state, p)
    _revive_player_if_needed(state)


def _enemy_turn(state: CombatState, enemy: Enemy) -> None:
    if not enemy.alive:
        return
    if enemy.sleep_turns > 0:
        enemy.sleep_turns -= 1
        state.emit("enemy_sleep", enemy=enemy.name)
        return
    enemy.block = 0
    powers.on_turn_start(state, enemy)
    if not enemy.alive:
        return
    intent = enemy.current_intent()
    kind = intent["kind"]
    # Frozen v2 (v1.5): the enemy still acts, but its action deals -50%
    # damage. Consumed by acting (or by Shatter before this turn).
    frozen = enemy.frozen
    if frozen:
        enemy.frozen = False
        state.emit("frozen_action", enemy=enemy.name, kind=kind,
                   by_companion=enemy.frozen_by_companion)
    state.emit("intent", enemy=enemy.name, kind=kind,
               debuffed=bool(enemy.powers.get("weak", 0)
                             or enemy.powers.get("vulnerable", 0)),
               # A6 v2 (R18): application uptime = intents taken while
               # carrying an elemental aura. ref_ironclad applies
               # nothing, so the baseline's uptime is 0 by construction.
               aura=enemy.aura is not None)

    if kind == "attack":
        # Snapshot before resolving the action. The latch is spent only after
        # the hit loop so a multi-hit intent receives one coherent modifier.
        bomb_suppressed = (
            bool(enemy.bombs) and not enemy.bomb_suppression_spent
        )
        amount = intent["amount"] + intent.get("ramp", 0) * max(
            0, state.turn - intent.get("ramp_after", 0))
        for _ in range(intent.get("times", 1)):
            dmg = powers.modify_damage_dealt(enemy, amount)
            if frozen:
                dmg *= C.FROZEN_DAMAGE_MULT
            # `enemy` is passed as the dealer so Colossus can read ITS
            # Vulnerable (ColossusPower halves only what a Vulnerable attacker
            # lands on its owner).
            dmg = powers.modify_damage_taken(state.player, dmg, enemy)
            dmg = int(dmg)
            block_before = state.player.block
            blocked = min(state.player.block, dmg)
            state.player.block -= blocked
            # Encore absorbs after Block, before HP (kickoff §4). Its own
            # event stream credits A4 sustain -- NEVER folded into
            # `blocked` (§2 harness note, Tier 0 binding).
            hp_loss = resources.absorb_into_encore(state, dmg - blocked)
            state.player.hp -= hp_loss
            resources.note_player_hp_loss(state, hp_loss)
            # Combat-side relic on_first_hp_loss_draw (dead branch on the
            # battery). Fires at most once per combat, on real HP loss.
            if hp_loss > 0 and state.player.relic_effects:
                relics.note_hp_loss(state)
            state.emit("player_hit", amount=hp_loss, blocked=blocked,
                       block_before=block_before)
            # AfterDamageReceived fires per HIT, not per intent -- FlameBarrier
            # retaliates against every hit of a multi-hit attack. Inferno and
            # Rupture are silent here: both require CurrentSide == Owner.Side,
            # and state.in_player_turn is False.
            refpowers.on_damage_received(state, state.player,
                                         unblocked=dmg - blocked, dealer=enemy,
                                         powered_attack=True)
            if not state.player.alive:
                # Fairy in a Bottle (dead branch on the battery: potions
                # empty). Passive revive at the lethal hit; if it saves the
                # player the turn continues and a later hit of a multi-hit
                # intent can still kill (the fairy is spent).
                if not _revive_player_if_needed(state):
                    return
            if not enemy.alive:
                break               # FlameBarrier can kill the dealer
        if bomb_suppressed:
            enemy.bomb_suppression_spent = True
            state.emit("bomb_suppression_spent", enemy=enemy.name)
    elif kind == "block":
        enemy.block += intent["amount"]
    elif kind == "buff":
        powers.apply_power(state, enemy, intent.get("power", "strength"),
                           intent["amount"])
    elif kind == "debuff":
        # applier=enemy: Vicious must NOT draw off an enemy-applied Vulnerable.
        powers.apply_power(state, state.player, intent["power"],
                           intent["amount"], applier=enemy)
    elif kind == "summon":
        for spawn in intent["wave"]:
            state.enemies.append(Enemy(hp=spawn["hp"], max_hp=spawn["hp"],
                                       name=spawn.get("name", "add"),
                                       intents=spawn["intents"],
                                       counts_for_fatal=False))
    else:
        raise ValueError(f"unknown intent kind {kind!r}")

    enemy.advance_intent()
    powers.on_turn_end(state, enemy)


def surface_innate(draw_pile: list) -> None:
    """Innate (R37): innate cards surface to the TOP of the shuffled draw
    pile, so the first hand contains them (base-game semantics; hand-size
    overflow degrades to "drawn first", which is also base-game). Order
    among innate cards stays shuffle-relative -- no hidden second sort."""
    innate = [c for c in draw_pile if c.innate]
    if innate:
        draw_pile[:] = innate + [c for c in draw_pile if not c.innate]


def _run_rounds(state: CombatState, pilot: Pilot) -> None:
    while not state.over and state.turn < C.MAX_TURNS:
        _player_turn(state, pilot)
        if state.over:
            break
        for enemy in list(state.enemies):
            _enemy_turn(state, enemy)
            if state.over:
                break
        # AfterSideTurnEnd(side == Enemy): the once-per-round enemy tick. This
        # is where FlameBarrier is removed and Colossus decrements -- doing
        # either at the PLAYER's turn end instead makes Flame Barrier do
        # literally nothing.
        refpowers.after_enemy_side_turn_end(state)


def run_fight(player: Player, enemies: list[Enemy], pilot: Pilot,
              seed: int) -> CombatState:
    state = CombatState(player=player, enemies=enemies,
                        rng=random.Random(seed))
    # Per-combat resources (v1.6: the reset IS the safety on unbounded
    # Encore). Spotlight designation likewise re-aims fresh each combat.
    player.encore = 0
    player.fanfare = 0
    player.spotlight = None
    state.rng.shuffle(player.draw_pile)
    surface_innate(player.draw_pile)
    # Combat-side relics: clear per-combat counters at true fight start. Dead
    # branch on the battery (relic_effects empty); the combat_start_* effects
    # themselves fire on the first player turn (see _player_turn).
    if player.relic_effects:
        relics.reset_combat(state)
    # Bound so refpowers can recover the dealer/applier identity that
    # effects.py cannot pass; try/finally so a raising fight never leaks a
    # stale state into the next one.
    outer = refpowers.bind(state)
    try:
        _run_rounds(state, pilot)
    finally:
        refpowers.bind(outer)
    won = bool(state.player.alive) and not state.living_enemies
    if won and "heal_after_won_fight" in state.player.relic_hooks:
        # Burning Blood (ruling 1): post-fight, can't affect combat —
        # counts toward the A4 healing metric, not hp_left.
        state.emit("heal", amount=C.BURNING_BLOOD_HEAL, post_fight=True)
    state.emit("fight_end", won=won, turns=state.turn,
               hp_left=max(0, state.player.hp))
    return state
