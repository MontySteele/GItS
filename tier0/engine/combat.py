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
from tier0.engine import effects, powers, reactions, resources
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
        return state.player.energy
    cost = card.cost
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
    return cost


def play_card(state: CombatState, card: Card) -> None:
    p = state.player
    cost = card_cost(state, card)
    if (card.type == "attack" and cost == 0
            and p.sparks >= spark_threshold(state) and card.cost != 0):
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
        # each turn; Standing Ovation grants Encore on EVERY one.
        if state.spotlighted_cards_this_turn == 1:
            n = p.powers.get("spotlight_draw", 0)
            if n:
                state.draw(n)
                state.emit("extra_draw", amount=n)
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
    for _ in range(replays):
        effects.resolve_card(state, card)
    if card.kit_card:
        pass                                  # returns to the kit, no pile
    elif card.exhaust or card.type == "power":
        p.exhaust_pile.append(card)
    else:
        p.discard_pile.append(card)
    grant_charged_kit(state)


def _player_turn(state: CombatState, pilot: Pilot) -> None:
    p = state.player
    state.turn += 1
    state.cards_played_this_turn = 0
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
    effects.player_turn_start_triggers(state)
    if not p.alive or state.over:
        return

    p.energy = C.BASE_ENERGY_PER_TURN
    state.draw(C.CARDS_DRAWN_PER_TURN)
    grant_charged_kit(state)                 # turn-start gains + full-hand defer

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

    effects.player_turn_end_triggers(state)      # Oz, Sparks 'n' Splash, ...
    grant_charged_kit(state)     # Salon-tick particles can fill the meter
                                 # at turn end; the Burst's Retain keeps it
    # Burst cards have Retain (principles v1.4): they stay in hand.
    # Ethereal cards (the Spotlight selector) vanish to exhaust instead of
    # discarding -- an unplayed selector must never circulate as loot.
    retained = [c for c in p.hand if "burst" in c.tags]
    p.exhaust_pile.extend(c for c in p.hand
                          if "ethereal" in c.tags and "burst" not in c.tags)
    p.discard_pile.extend(c for c in p.hand
                          if "burst" not in c.tags and "ethereal" not in c.tags)
    p.hand = retained
    powers.on_turn_end(state, p)


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
                             or enemy.powers.get("vulnerable", 0)))

    if kind == "attack":
        amount = intent["amount"] + intent.get("ramp", 0) * max(
            0, state.turn - intent.get("ramp_after", 0))
        for _ in range(intent.get("times", 1)):
            dmg = powers.modify_damage_dealt(enemy, amount)
            if frozen:
                dmg *= C.FROZEN_DAMAGE_MULT
            dmg = powers.modify_damage_taken(state.player, dmg)
            dmg = int(dmg)
            blocked = min(state.player.block, dmg)
            state.player.block -= blocked
            # Encore absorbs after Block, before HP (kickoff §4). Its own
            # event stream credits A4 sustain -- NEVER folded into
            # `blocked` (§2 harness note, Tier 0 binding).
            hp_loss = resources.absorb_into_encore(state, dmg - blocked)
            state.player.hp -= hp_loss
            resources.note_player_hp_loss(state, hp_loss)
            state.emit("player_hit", amount=hp_loss, blocked=blocked)
            if not state.player.alive:
                return
    elif kind == "block":
        enemy.block += intent["amount"]
    elif kind == "buff":
        powers.apply_power(state, enemy, intent.get("power", "strength"),
                           intent["amount"])
    elif kind == "debuff":
        powers.apply_power(state, state.player, intent["power"], intent["amount"])
    elif kind == "summon":
        for spawn in intent["wave"]:
            state.enemies.append(Enemy(hp=spawn["hp"], max_hp=spawn["hp"],
                                       name=spawn.get("name", "add"),
                                       intents=spawn["intents"]))
    else:
        raise ValueError(f"unknown intent kind {kind!r}")

    enemy.advance_intent()
    powers.on_turn_end(state, enemy)


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
    while not state.over and state.turn < C.MAX_TURNS:
        _player_turn(state, pilot)
        if state.over:
            break
        for enemy in list(state.enemies):
            _enemy_turn(state, enemy)
            if state.over:
                break
    won = bool(state.player.alive) and not state.living_enemies
    if won and "heal_after_won_fight" in state.player.relic_hooks:
        # Burning Blood (ruling 1): post-fight, can't affect combat —
        # counts toward the A4 healing metric, not hp_left.
        state.emit("heal", amount=C.BURNING_BLOOD_HEAL, post_fight=True)
    state.emit("fight_end", won=won, turns=state.turn,
               hp_left=max(0, state.player.hp))
    return state
