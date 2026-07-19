"""Turn loop (spec §3/§4.5). One function: run_fight.

Player turn: bombs detonate -> auras tick -> power hooks -> draw + energy ->
pilot plays until done -> discard hand -> power decay.
Enemy turns: scripted intents, no AI. Frozen/asleep enemies skip.
"""

from __future__ import annotations

import random
from typing import Callable

from tier0 import constants as C
from tier0.engine import effects, powers, reactions
from tier0.engine.state import Card, CombatState, Enemy, Player

# A pilot is a callable: (state) -> Card | None (None = end turn).
Pilot = Callable[[CombatState], Card | None]


def spark_threshold(state: CombatState) -> int:
    # True Spark Knight: free attack at 2 sparks instead of 3.
    return max(1, C.SPARKS_FOR_FREE_ATTACK
               - state.player.powers.get("spark_threshold_down", 0))


def card_playable(state: CombatState, card: Card) -> bool:
    if card.requires == "burst_energy_full":
        if state.player.burst_energy < state.player.burst_max:
            return False
    elif card.requires:
        raise ValueError(f"unknown requires {card.requires!r}")
    return card_cost(state, card) <= state.player.energy


def card_cost(state: CombatState, card: Card) -> int:
    if card.cost == "X":
        return state.player.energy
    cost = card.cost
    if card.is_companion and state.companion_cost_delta_this_turn:
        cost = max(0, cost + state.companion_cost_delta_this_turn)
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
    p.hand.remove(card)
    state.cards_played_this_turn += 1
    state.emit("play", card=card.id, cost=cost, energy_left=p.energy)
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
    if card.exhaust or card.type == "power":
        p.exhaust_pile.append(card)
    else:
        p.discard_pile.append(card)


def _player_turn(state: CombatState, pilot: Pilot) -> None:
    p = state.player
    state.turn += 1
    state.cards_played_this_turn = 0
    p.block = 0

    state.companion_cost_delta_this_turn = 0     # Friendly Visit expires
    state.replay_next_companion = 0              # Study Buddy expires

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
    p.discard_pile.extend(p.hand)
    p.hand = []
    powers.on_turn_end(state, p)


def _enemy_turn(state: CombatState, enemy: Enemy) -> None:
    if not enemy.alive:
        return
    if enemy.sleep_turns > 0:
        enemy.sleep_turns -= 1
        state.emit("enemy_sleep", enemy=enemy.name)
        return
    if enemy.frozen:
        enemy.frozen = False
        enemy.advance_intent()
        state.emit("enemy_frozen_skip", enemy=enemy.name)
        return

    enemy.block = 0
    powers.on_turn_start(state, enemy)
    if not enemy.alive:
        return
    intent = enemy.current_intent()
    kind = intent["kind"]
    state.emit("intent", enemy=enemy.name, kind=kind,
               debuffed=bool(enemy.powers.get("weak", 0)
                             or enemy.powers.get("vulnerable", 0)))

    if kind == "attack":
        amount = intent["amount"] + intent.get("ramp", 0) * max(
            0, state.turn - intent.get("ramp_after", 0))
        for _ in range(intent.get("times", 1)):
            dmg = powers.modify_damage_dealt(enemy, amount)
            dmg = powers.modify_damage_taken(state.player, dmg)
            dmg = int(dmg)
            blocked = min(state.player.block, dmg)
            state.player.block -= blocked
            state.player.hp -= dmg - blocked
            state.emit("player_hit", amount=dmg - blocked, blocked=blocked)
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
    state.emit("fight_end", won=won, turns=state.turn,
               hp_left=max(0, state.player.hp))
    return state
