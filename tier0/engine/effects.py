"""Atomic effect resolvers — the card DSL (spec §4.2).

Each op is a function (state, effect_dict, source_card) -> None registered
in OPS. Extend only when a designed card demands it.
"""

from __future__ import annotations

from typing import Optional

from tier0 import constants as C
from tier0.engine import powers, reactions
from tier0.engine.state import Bomb, Card, CombatState, Enemy


def _pick_targets(state: CombatState, spec: str) -> list[Enemy]:
    living = state.living_enemies
    if not living:
        return []
    if spec in ("enemy", "lowest_hp_enemy"):        # pilot aims at lowest HP
        return [min(living, key=lambda e: e.hp)]
    if spec == "all_enemies":
        return list(living)
    if spec == "random_enemy":
        return [state.rng.choice(living)]
    raise ValueError(f"unknown target spec {spec!r}")


def deal_damage_to_enemy(state: CombatState, enemy: Enemy, base: float,
                         element: Optional[str] = None,
                         source: str = "card") -> float:
    """Full damage pipeline: strength/weak -> reaction amp -> vulnerable ->
    block -> hp. Returns damage actually dealt to HP (for metrics)."""
    dmg = powers.modify_damage_dealt(state.player, base)
    dmg = reactions.resolve_hit(state, enemy, element, dmg)
    dmg = powers.modify_damage_taken(enemy, dmg)
    dmg = int(dmg)
    if base > 0 and dmg > base * C.AMP_STACK_LIMIT:
        state.emit("amp_stack_warning", base=base, final=dmg, target=enemy.name)
    blocked = min(enemy.block, dmg)
    enemy.block -= blocked
    hp_dmg = dmg - blocked
    enemy.hp -= hp_dmg
    state.emit("damage", target=enemy.name, amount=hp_dmg, blocked=blocked,
               base=base, source=source)
    if hp_dmg > 0:
        _detonate_bombs_on_hit(state, enemy, source)
    return hp_dmg


def _detonate_bombs_on_hit(state: CombatState, enemy: Enemy, source: str) -> None:
    # Bombs detonate early when the enemy is hit by an Attack card (spec §4.2).
    if source != "attack" or not enemy.bombs or not enemy.alive:
        return
    detonate_bombs(state, enemy)


def detonate_bombs(state: CombatState, enemy: Enemy) -> None:
    bombs, enemy.bombs = enemy.bombs, []
    for bomb in bombs:
        state.emit("bomb_detonation", target=enemy.name, damage=bomb.damage)
        deal_damage_to_enemy(state, enemy, bomb.damage, element=bomb.element,
                             source="bomb")
        if "spark_on_detonation" in state.player.relic_hooks:
            gain_sparks(state, 1)


def gain_sparks(state: CombatState, n: int) -> None:
    state.player.sparks += n
    state.emit("gain_spark", amount=n, total=state.player.sparks)


# --- ops ---

def _op_damage(state: CombatState, fx: dict, card: Card) -> None:
    times = fx.get("times", 1)
    element = card.element if fx.get("applies_element") else None
    source = "attack" if card.type == "attack" else "card"
    # Generic per-tag scaler: a power named tag_damage_<tag> adds its
    # stacks to damage of cards carrying <tag> (e.g. Accuracy-like -> shiv).
    tag_bonus = sum(state.player.powers.get(f"tag_damage_{t}", 0)
                    for t in card.tags)
    for _ in range(times):
        for enemy in _pick_targets(state, fx.get("target", "enemy")):
            deal_damage_to_enemy(state, enemy, fx["amount"] + tag_bonus,
                                 element=element, source=source)


def _op_block(state: CombatState, fx: dict, card: Card) -> None:
    state.player.block += fx["amount"]
    state.emit("block", amount=fx["amount"])


def _op_draw(state: CombatState, fx: dict, card: Card) -> None:
    state.draw(fx["amount"])
    state.emit("extra_draw", amount=fx["amount"])   # A5 velocity accounting


def _op_energy(state: CombatState, fx: dict, card: Card) -> None:
    state.player.energy += fx["amount"]
    state.emit("energy", amount=fx["amount"])


def _op_apply_power(state: CombatState, fx: dict, card: Card) -> None:
    if fx.get("target", "self") == "self":
        powers.apply_power(state, state.player, fx["power"], fx["amount"])
    else:
        for enemy in _pick_targets(state, fx["target"]):
            powers.apply_power(state, enemy, fx["power"], fx["amount"])


def _op_apply_aura(state: CombatState, fx: dict, card: Card) -> None:
    for enemy in _pick_targets(state, fx.get("target", "enemy")):
        reactions.resolve_hit(state, enemy, fx["element"], 0)


def _op_place_bomb(state: CombatState, fx: dict, card: Card) -> None:
    for _ in range(fx.get("amount", 1)):
        targets = _pick_targets(state, fx.get("target", "random_enemy"))
        for enemy in targets:
            enemy.bombs.append(Bomb(damage=fx["bomb_damage"],
                                    element=fx.get("element", "pyro")))
            state.emit("bomb_placed", target=enemy.name, damage=fx["bomb_damage"])


def _op_gain_spark(state: CombatState, fx: dict, card: Card) -> None:
    gain_sparks(state, fx.get("amount", 1))


def _op_heal(state: CombatState, fx: dict, card: Card) -> None:
    p = state.player
    healed = min(fx["amount"], p.max_hp - p.hp)
    p.hp += healed
    state.emit("heal", amount=healed)


def _op_add_card(state: CombatState, fx: dict, card: Card) -> None:
    from tier0.content.loader import get_card    # late import avoids cycle
    token = get_card(fx["card_id"])
    dest = fx.get("to", "discard")
    if dest == "hand" and len(state.player.hand) < C.MAX_HAND_SIZE:
        state.player.hand.append(token)
    else:
        state.player.discard_pile.append(token)
    state.emit("add_card", card=token.id, to=dest)


def _op_exhaust_from(state: CombatState, fx: dict, card: Card) -> None:
    hand = state.player.hand
    if not hand:
        return
    for _ in range(fx.get("amount", 1)):
        if not hand:
            break
        victim = state.rng.choice(hand)          # choice-as-random (spec §4.2)
        hand.remove(victim)
        state.player.exhaust_pile.append(victim)
        state.emit("exhaust", card=victim.id)


def _op_scry_discard(state: CombatState, fx: dict, card: Card) -> None:
    # Look at top N, discard the "worst" by a cheap heuristic: highest cost
    # non-attack first (pilot heuristic placeholder; spec allows dumb).
    n = fx.get("amount", 1)
    top = state.player.draw_pile[:n]
    if not top:
        return
    worst = max(top, key=lambda c: (c.type != "attack", c.cost if isinstance(c.cost, int) else 99))
    state.player.draw_pile.remove(worst)
    state.player.discard_pile.append(worst)
    state.emit("scry_discard", card=worst.id)


OPS = {
    "damage": _op_damage,
    "block": _op_block,
    "draw": _op_draw,
    "energy": _op_energy,
    "apply_power": _op_apply_power,
    "apply_aura": _op_apply_aura,
    "place_bomb": _op_place_bomb,
    "gain_spark": _op_gain_spark,
    "heal": _op_heal,
    "add_card": _op_add_card,
    "exhaust_from": _op_exhaust_from,
    "scry_discard": _op_scry_discard,
}


def resolve_card(state: CombatState, card: Card) -> None:
    for fx in card.effects:
        if fx["op"] not in OPS:
            raise ValueError(f"card {card.id!r}: unknown op {fx['op']!r}")
        OPS[fx["op"]](state, fx, card)
