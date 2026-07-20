"""Atomic effect resolvers — the card DSL.

v1 ops per tier0-simulator-spec.md §4.2, extended per
klee-character-design.md §6 for the real card sheet: detonate, move_bombs,
modify_bombs, burst_energy, swirl, refresh_all_auras, buff_next_attack,
cost_mod, conditional, repeat_this, formula amounts, companion ops.
"""

from __future__ import annotations

from typing import Optional

from tier0 import constants as C
from tier0.engine import powers, reactions
from tier0.engine.state import Bomb, Card, CombatState, Enemy


def _amount(state: CombatState, val) -> int:
    """Resolve a literal or formula amount (X-cost cards)."""
    if isinstance(val, int):
        return val
    if val == "X":
        return state.current_x
    if val == "X_plus_1":
        return state.current_x + 1
    raise ValueError(f"unknown amount formula {val!r}")


def _pick_targets(state: CombatState, spec: str) -> list[Enemy]:
    living = state.living_enemies
    if not living:
        return []
    if spec in ("enemy", "lowest_hp_enemy"):        # pilot aims at lowest HP
        return [min(living, key=lambda e: e.hp)]
    if spec == "all_enemies":
        return list(living)
    if spec in ("random_enemy", "random_enemies"):
        return [state.rng.choice(living)]
    raise ValueError(f"unknown target spec {spec!r}")


def _element_for(state: CombatState, fx: dict, card: Card) -> Optional[str]:
    """Catalyst cadence (design doc §2.3): every attack applies the
    character's element unless the sheet says applies_element: false.
    Cards with their own element (companions) apply that instead."""
    if "applies_element" in fx:
        return card.element if fx["applies_element"] else None
    if (card.type == "attack" and fx["op"] == "damage"
            and state.player.cadence == "catalyst"):
        return card.element if card.element != "none" else state.player.element
    return None


def deal_damage_to_enemy(state: CombatState, enemy: Enemy, base: float,
                         element: Optional[str] = None,
                         source: str = "card") -> float:
    """Full damage pipeline: strength/weak -> reaction amp -> vulnerable ->
    block -> hp. Returns damage actually dealt to HP (for metrics)."""
    # Solar Isotoma (Crystallize engine): attack hits vs aura'd enemies
    # grant block — checked before the hit can consume the aura.
    if (source == "attack" and enemy.aura
            and state.player.powers.get("solar_isotoma", 0)):
        state.player.block += C.SOLAR_ISOTOMA_BLOCK
    dmg = powers.modify_damage_dealt(state.player, base)
    dmg = reactions.resolve_hit(state, enemy, element, dmg)
    dmg = powers.modify_damage_taken(enemy, dmg)
    dmg = int(dmg)
    if base > 0 and dmg > base * C.AMP_STACK_LIMIT:
        state.emit("amp_stack_warning", base=base, final=dmg, target=enemy.name)
    blocked = min(enemy.block, dmg)
    enemy.block -= blocked
    hp_dmg = dmg - blocked
    was_alive = enemy.alive
    effective = min(hp_dmg, max(0, enemy.hp))   # overkill doesn't count
    enemy.hp -= hp_dmg
    state.emit("damage", target=enemy.name, amount=effective, blocked=blocked,
               base=base, source=source)
    if was_alive and not enemy.alive:
        state.kills_this_card += 1
    if hp_dmg > 0:
        _detonate_bombs_on_hit(state, enemy, source)
    return hp_dmg


def _detonate_bombs_on_hit(state: CombatState, enemy: Enemy, source: str) -> None:
    # Bombs detonate early when the enemy is hit by an Attack card (§4.2).
    if source != "attack" or not enemy.bombs or not enemy.alive:
        return
    detonate_bombs(state, enemy)


def detonate_bombs(state: CombatState, enemy: Enemy, bonus: int = 0) -> None:
    bombs, enemy.bombs = enemy.bombs, []
    p = state.player
    for bomb in bombs:
        dmg = bomb.damage + bonus + p.powers.get("bomb_damage_up", 0)
        state.detonations_total += 1
        state.emit("bomb_detonation", target=enemy.name, damage=dmg)
        deal_damage_to_enemy(state, enemy, dmg, element=bomb.element,
                             source="bomb")
        if "spark_on_detonation" in p.relic_hooks:
            gain_sparks(state, 1)
        splash = p.powers.get("detonation_splash", 0)     # Blazing Delight
        if splash:
            for other in state.living_enemies:
                other.hp -= splash
                state.emit("damage", target=other.name, amount=splash,
                           source="detonation_splash")
            if p.burst_max:
                p.burst_energy += C.DETONATION_SPLASH_BURST
        vuln = p.powers.get("detonation_vuln", 0)         # Explosive Frags
        if vuln and enemy.alive:
            powers.apply_power(state, enemy, "vulnerable", vuln)


def gain_sparks(state: CombatState, n: int) -> None:
    state.player.sparks += n
    state.emit("gain_spark", amount=n, total=state.player.sparks)


def _add_token(state: CombatState, card: Card, zone: str) -> None:
    if zone == "hand" and len(state.player.hand) < C.MAX_HAND_SIZE:
        state.player.hand.append(card)
    else:
        state.player.discard_pile.append(card)
    state.emit("add_card", card=card.id, to=zone)


# --- ops ---

def _op_damage(state: CombatState, fx: dict, card: Card) -> None:
    element = _element_for(state, fx, card)
    source = "attack" if card.type == "attack" else "card"

    if fx.get("target") == "self":            # Hot Hands / No Holding Back
        state.player.hp -= fx["amount"]       # HP loss, ignores block
        state.emit("self_damage", amount=fx["amount"])
        return

    times = fx.get("times", 1)
    if "times_formula" in fx:
        if fx["times_formula"] != "2_plus_sparks":
            raise ValueError(f"unknown times_formula {fx['times_formula']!r}")
        times = 2 + state.player.sparks       # Gleeful Barrage
    times = _amount(state, times)

    base = _amount(state, fx["amount"])
    if "bonus_formula" in fx:                 # Grand Finale: N_per_detonation
        formula = fx["bonus_formula"]
        n, _, rest = formula.partition("_per_")
        if rest != "detonation_this_combat" or not n.isdigit():
            raise ValueError(f"unknown bonus_formula {formula!r}")
        base += int(n) * state.detonations_total
    if card.type == "attack":
        base += state.current_attack_bonus
    # tag_damage_<tag> powers (Accuracy-like -> shiv) add per-hit.
    base += sum(state.player.powers.get(f"tag_damage_{t}", 0)
                for t in card.tags)

    for _ in range(times):
        for enemy in _pick_targets(state, fx.get("target", "enemy")):
            hit = base
            if fx.get("bonus_vs_bombed") and enemy.bombs:
                hit += fx["bonus_vs_bombed"]
            if fx.get("bonus_vs_aura") and enemy.aura:
                hit += fx["bonus_vs_aura"]
            deal_damage_to_enemy(state, enemy, hit, element=element,
                                 source=source)


def _op_block(state: CombatState, fx: dict, card: Card) -> None:
    state.player.block += fx["amount"]
    state.emit("block", amount=fx["amount"])


def _op_draw(state: CombatState, fx: dict, card: Card) -> None:
    n = fx.get("amount")
    if fx.get("amount_formula") == "per_aura":     # Elemental Ecstasy
        n = sum(1 for e in state.living_enemies if e.aura)
    state.draw(n)
    state.emit("extra_draw", amount=n)   # A5 velocity accounting


def _op_energy(state: CombatState, fx: dict, card: Card) -> None:
    state.player.energy += fx["amount"]
    state.emit("energy", amount=fx["amount"])


def _op_apply_power(state: CombatState, fx: dict, card: Card) -> None:
    cap = fx.get("max_stacks")
    if fx.get("target", "self") == "self":
        powers.apply_power(state, state.player, fx["power"], fx["amount"],
                           max_stacks=cap)
    else:
        for enemy in _pick_targets(state, fx["target"]):
            powers.apply_power(state, enemy, fx["power"], fx["amount"],
                               max_stacks=cap)


def _op_apply_aura(state: CombatState, fx: dict, card: Card) -> None:
    for enemy in _pick_targets(state, fx.get("target", "enemy")):
        reactions.resolve_hit(state, enemy, fx["element"], 0)


def _op_place_bomb(state: CombatState, fx: dict, card: Card) -> None:
    for _ in range(_amount(state, fx.get("amount", 1))):
        for enemy in _pick_targets(state, fx.get("target", "random_enemy")):
            enemy.bombs.append(Bomb(damage=fx["bomb_damage"],
                                    element=fx.get("element", "pyro"),
                                    turn_placed=state.turn))
            state.emit("bomb_placed", target=enemy.name,
                       damage=fx["bomb_damage"])


def _op_detonate(state: CombatState, fx: dict, card: Card) -> None:
    for enemy in _pick_targets(state, fx.get("target", "enemy")):
        if enemy.bombs:
            detonate_bombs(state, enemy, bonus=fx.get("bonus", 0))


def _op_move_bombs(state: CombatState, fx: dict, card: Card) -> None:
    # Careful Arrangement: gather all bombs onto one enemy, +bonus each.
    targets = _pick_targets(state, fx.get("target", "enemy"))
    if not targets:
        return
    dest = targets[0]
    moved = []
    for e in state.living_enemies:
        if e is not dest:
            moved.extend(e.bombs)
            e.bombs = []
    for bomb in moved:
        bomb.damage += fx.get("bonus", 0)
        dest.bombs.append(bomb)
    if moved:
        state.emit("bombs_moved", count=len(moved), to=dest.name)


def _op_modify_bombs(state: CombatState, fx: dict, card: Card) -> None:
    scope = fx.get("scope", "all")
    for e in state.living_enemies:
        for bomb in e.bombs:
            if scope == "all" or (scope == "placed_this_turn"
                                  and bomb.turn_placed == state.turn):
                bomb.damage += fx["bonus"]


def _op_burst_energy(state: CombatState, fx: dict, card: Card) -> None:
    if state.player.burst_max:
        state.player.burst_energy += fx["amount"]
        state.emit("burst_energy", amount=fx["amount"],
                   total=state.player.burst_energy)


def _op_swirl(state: CombatState, fx: dict, card: Card) -> None:
    for enemy in _pick_targets(state, fx.get("target", "enemy")):
        reactions.resolve_hit(state, enemy, "anemo", 0)


def _op_refresh_all_auras(state: CombatState, fx: dict, card: Card) -> None:
    for e in state.living_enemies:
        if e.aura:
            e.aura_turns_left = C.AURA_DURATION_TURNS


def _op_buff_next_attack(state: CombatState, fx: dict, card: Card) -> None:
    powers.apply_power(state, state.player, "next_attack_up", fx["amount"])


def _op_cost_mod(state: CombatState, fx: dict, card: Card) -> None:
    if fx.get("scope") != "companion_cards":
        raise ValueError(f"unknown cost_mod scope {fx.get('scope')!r}")
    state.companion_cost_delta_this_turn += fx["delta"]   # reset at turn start


def _op_gain_spark(state: CombatState, fx: dict, card: Card) -> None:
    gain_sparks(state, fx.get("amount", 1))


def _op_heal(state: CombatState, fx: dict, card: Card) -> None:
    p = state.player
    healed = min(fx["amount"], p.max_hp - p.hp)
    p.hp += healed
    state.emit("heal", amount=healed)


def _op_add_card(state: CombatState, fx: dict, card: Card) -> None:
    from tier0.content import loader                # late import avoids cycle
    zone = fx.get("zone") or fx.get("to", "discard")
    n = fx.get("amount", 1)
    if "pool" in fx:                                # Secret Stash
        pool_cards = loader.cards_in_pool(fx["pool"])
        picks = [state.rng.choice(pool_cards) for _ in range(n)]
        ids = [c.id for c in picks]
    else:
        ids = [fx.get("card_id") or fx["card"]] * n
    for cid in ids:
        token = loader.get_card(cid)
        if "cost_override" in fx:
            token.cost = fx["cost_override"]
        _add_token(state, token, zone)


def _op_discard(state: CombatState, fx: dict, card: Card) -> None:
    for _ in range(fx.get("amount", 1)):
        if not state.player.hand:
            return
        victim = state.rng.choice(state.player.hand)
        state.player.hand.remove(victim)
        state.player.discard_pile.append(victim)
        state.emit("discard", card=victim.id)


def _op_exhaust_from(state: CombatState, fx: dict, card: Card) -> None:
    hand = state.player.hand
    pool = hand
    if fx.get("filter") == "status":
        pool = [c for c in hand if c.rarity == "status"]
    for _ in range(fx.get("amount", 1)):
        if not pool:
            break
        victim = state.rng.choice(pool)
        pool = [c for c in pool if c is not victim]
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
    worst = max(top, key=lambda c: (c.type != "attack",
                                    c.cost if isinstance(c.cost, int) else 99))
    state.player.draw_pile.remove(worst)
    state.player.discard_pile.append(worst)
    state.emit("scry_discard", card=worst.id)


def _op_conditional(state: CombatState, fx: dict, card: Card) -> None:
    branch = fx["then"] if _predicate(state, fx["if"]) else fx.get("else", [])
    _resolve_effects(state, branch, card)


def _predicate(state: CombatState, name: str) -> bool:
    if name == "this_cost_zero":
        return state.current_card_cost == 0
    if name == "has_spark":
        return state.player.sparks > 0
    if name == "target_has_nonpyro_aura":
        # Snapshotted at card start — the card's own first hit may consume
        # the aura via reaction, which is exactly what the bonus rewards.
        return state.target_had_offelement_aura
    if name == "reaction_triggered_by_this":
        return state.reactions_this_card > 0
    if name == "killed_target":
        return state.kills_this_card > 0
    if name == "enemy_intends_attack":
        return any(e.current_intent()["kind"] == "attack"
                   and not e.frozen and e.sleep_turns == 0
                   for e in state.living_enemies)
    raise ValueError(f"unknown predicate {name!r}")


def _op_repeat_this(state: CombatState, fx: dict, card: Card) -> None:
    state.repeat_requested = fx.get("times", 1)     # honored by resolve_card


def _op_chance_bomb_per_detonation(state: CombatState, fx: dict,
                                   card: Card) -> None:
    # Chained Reactions: per detonation caused by this card so far, a
    # chance to place a fresh bomb on a random enemy.
    n = state.detonations_total - state.detonations_at_card_start
    for _ in range(n):
        if state.rng.random() < fx["chance"] and state.living_enemies:
            enemy = state.rng.choice(state.living_enemies)
            enemy.bombs.append(Bomb(damage=fx["bomb_damage"],
                                    turn_placed=state.turn))
            state.emit("bomb_placed", target=enemy.name,
                       damage=fx["bomb_damage"])


def _op_copy_companion_in_hand(state: CombatState, fx: dict, card: Card) -> None:
    import copy as _copy
    comps = [c for c in state.player.hand if c.is_companion]
    if not comps:
        return
    for _ in range(fx.get("amount", 1)):
        chosen = _copy.deepcopy(state.rng.choice(comps))
        _add_token(state, chosen, "hand")


def _op_replay_next_companion(state: CombatState, fx: dict, card: Card) -> None:
    state.replay_next_companion += fx.get("times", 1)   # reset at turn start


def _op_copy_companions_played(state: CombatState, fx: dict, card: Card) -> None:
    from tier0.content import loader
    for cid in dict.fromkeys(state.companions_played):  # unique, in order
        token = loader.get_card(cid)
        if "cost_override" in fx:
            token.cost = fx["cost_override"]
        _add_token(state, token, fx.get("zone", "hand"))


OPS = {
    "damage": _op_damage,
    "block": _op_block,
    "draw": _op_draw,
    "energy": _op_energy,
    "apply_power": _op_apply_power,
    "apply_aura": _op_apply_aura,
    "place_bomb": _op_place_bomb,
    "detonate": _op_detonate,
    "move_bombs": _op_move_bombs,
    "modify_bombs": _op_modify_bombs,
    "burst_energy": _op_burst_energy,
    "swirl": _op_swirl,
    "refresh_all_auras": _op_refresh_all_auras,
    "buff_next_attack": _op_buff_next_attack,
    "cost_mod": _op_cost_mod,
    "gain_spark": _op_gain_spark,
    "heal": _op_heal,
    "add_card": _op_add_card,
    "discard": _op_discard,
    "exhaust_from": _op_exhaust_from,
    "scry_discard": _op_scry_discard,
    "conditional": _op_conditional,
    "repeat_this": _op_repeat_this,
    "chance_bomb_per_detonation": _op_chance_bomb_per_detonation,
    "copy_companion_in_hand": _op_copy_companion_in_hand,
    "replay_next_companion": _op_replay_next_companion,
    "copy_companions_played_this_combat": _op_copy_companions_played,
}


def _resolve_effects(state: CombatState, effects: list[dict],
                     card: Card) -> None:
    for fx in effects:
        if fx["op"] not in OPS:
            raise ValueError(f"card {card.id!r}: unknown op {fx['op']!r}")
        OPS[fx["op"]](state, fx, card)


def resolve_card(state: CombatState, card: Card) -> None:
    state.reactions_this_card = 0
    state.kills_this_card = 0
    state.detonations_at_card_start = state.detonations_total
    state.repeat_requested = 0
    # Predicate snapshot: does the default target hold an off-element aura?
    living = state.living_enemies
    tgt = min(living, key=lambda e: e.hp) if living else None
    state.target_had_offelement_aura = bool(
        tgt and tgt.aura and tgt.aura != state.player.element)
    # Per-card flat attack bonus (Bennett's next_attack_up consumed here;
    # Nicole's celestial_gift, Bennett-burst attack_up_this_turn, and
    # Spark Knight Style's zero-cost rider all add per attack card).
    bonus = 0
    if card.type == "attack":
        p = state.player
        bonus = (p.powers.pop("next_attack_up", 0)
                 + p.powers.get("celestial_gift", 0)
                 + p.powers.get("attack_up_this_turn", 0))
        if state.current_card_cost == 0:
            bonus += p.powers.get("zero_cost_attacks_up", 0)
    state.current_attack_bonus = bonus

    _resolve_effects(state, card.effects, card)
    if state.repeat_requested:                          # Perfect Timing
        times, state.repeat_requested = state.repeat_requested, 0
        for _ in range(times):
            _resolve_effects(
                state,
                [fx for fx in card.effects if fx["op"] != "repeat_this"
                 and not (fx["op"] == "conditional"
                          and any(e.get("op") == "repeat_this"
                                  for e in fx.get("then", [])))],
                card)


# --- player-side power triggers, called from the combat loop ---

def player_turn_start_triggers(state: CombatState) -> None:
    p = state.player
    if p.powers.get("celestial_gift", 0):               # Nicole
        p.block += C.CELESTIAL_GIFT_BLOCK
    n = p.powers.get("spark_per_turn", 0)               # Endless Fireworks
    if n:
        gain_sparks(state, n)
    n = p.powers.get("bomb_and_spark_per_turn", 0)      # Playtime Forever
    for _ in range(n):
        if state.living_enemies:
            enemy = state.rng.choice(state.living_enemies)
            enemy.bombs.append(Bomb(damage=C.PLAYTIME_BOMB_DAMAGE,
                                    turn_placed=state.turn))
            state.emit("bomb_placed", target=enemy.name,
                       damage=C.PLAYTIME_BOMB_DAMAGE)
        gain_sparks(state, 1)


def player_turn_end_triggers(state: CombatState) -> None:
    p = state.player
    if p.powers.get("sparks_n_splash", 0):              # the Burst
        for _ in range(C.SPARKS_N_SPLASH_HITS):
            if not state.living_enemies:
                break
            enemy = state.rng.choice(state.living_enemies)
            deal_damage_to_enemy(state, enemy, C.SPARKS_N_SPLASH_HIT_DMG,
                                 element="pyro", source="burst")
        p.powers["sparks_n_splash"] -= 1
    if p.powers.get("oz_summon", 0):                    # Fischl
        if state.living_enemies:
            enemy = state.rng.choice(state.living_enemies)
            deal_damage_to_enemy(state, enemy, C.OZ_DMG,
                                 element="electro", source="companion")
        p.powers["oz_summon"] -= 1
    if p.powers.get("witchs_flame", 0):                 # Durin (permanent)
        if state.living_enemies:
            enemy = state.rng.choice(state.living_enemies)
            deal_damage_to_enemy(state, enemy, C.WITCHS_FLAME_DMG,
                                 element="pyro", source="companion")
    if p.powers.get("solar_isotoma", 0):                # Albedo, 3 turns
        p.powers["solar_isotoma"] -= 1
    p.powers.pop("attack_up_this_turn", None)           # Bennett burst
