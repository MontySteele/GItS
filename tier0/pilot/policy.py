"""Rule-based greedy pilot (spec §6).

1. If lethal is playable this turn, play toward it.
2. Else if incoming damage >= BLOCK_PANIC_THRESHOLD of remaining HP,
   prioritize block until covered.
3. Else weighted scoring per pilots/*.yaml.

Deliberately dumb; both Klee and reference decks use the same pilot.
"""

from __future__ import annotations

from typing import Optional

from tier0 import constants as C
from tier0.engine import powers
from tier0.engine.combat import card_cost, card_playable
from tier0.engine.state import Card, CombatState


def _places_bombs(card: Card) -> bool:
    return any(fx["op"] == "place_bomb" for fx in card.effects)


def make_pilot(weights: dict):
    def pilot(state: CombatState) -> Optional[Card]:
        playable = [c for c in state.player.hand if card_playable(state, c)]
        if not playable:
            return None

        lethal = _lethal_card(state, playable)
        if lethal is not None:
            return lethal

        incoming = _incoming_damage(state)
        if (incoming >= C.BLOCK_PANIC_THRESHOLD * max(1, state.player.hp)
                and state.player.block < incoming):
            blockers = [c for c in playable if _raw_block(c) > 0]
            if blockers:
                return max(blockers, key=_raw_block)

        scored = [(_score(state, c, weights), -i, c) for i, c in enumerate(playable)]
        best_score, _, best = max(scored, key=lambda t: t[:2])
        if best_score <= 0:
            return None
        # Bomb sequencing: attacks resolve BEFORE new placements, so this
        # turn's attacks don't pop bombs placed this turn (forfeiting
        # next-turn detonation + Pounding Surprise sparks).
        if _places_bombs(best):
            attacks = [(s, i, c) for s, i, c in scored
                       if c.type == "attack" and s > 0]
            if attacks:
                return max(attacks, key=lambda t: t[:2])[2]
        return best

    return pilot


def _est(state: CombatState, val, default: int = 0) -> float:
    """Estimate a possibly-formulaic amount for scoring purposes."""
    if isinstance(val, (int, float)):
        return val
    if val in ("X", "X_plus_1"):        # X-cards spend all remaining energy
        return state.player.energy + (1 if val == "X_plus_1" else 0)
    return default


def _expected_damage(state: CombatState, card: Card) -> float:
    total = 0.0
    living = state.living_enemies
    for fx in card.effects:
        if fx["op"] == "damage":
            if fx.get("target") == "self":
                total -= fx["amount"] * 0.5          # HP loss is a cost
                continue
            n_targets = len(living) if fx.get("target") == "all_enemies" else 1
            times = _est(state, fx.get("times", 1), 1)
            if fx.get("times_formula") == "2_plus_sparks":
                times = 2 + state.player.sparks
            per_hit = powers.modify_damage_dealt(state.player,
                                                 _est(state, fx["amount"]))
            if fx.get("bonus_formula") == "3_per_detonation_this_combat":
                per_hit += 3 * state.detonations_total
            total += per_hit * times * n_targets
        elif fx["op"] == "place_bomb":
            total += fx["bomb_damage"] * _est(state, fx.get("amount", 1), 1)
        elif fx["op"] == "detonate":
            # Early detonation realizes bomb damage now but forfeits the
            # next-turn detonation it would get anyway — value it only
            # when the target would die this turn (review ruling #6).
            for e in living:
                pending = sum(b.damage for b in e.bombs)
                if pending and pending >= e.hp + e.block:
                    total += pending
                if fx.get("target") != "all_enemies":
                    break
    return total


def _raw_block(card: Card) -> float:
    return sum(fx["amount"] for fx in card.effects if fx["op"] == "block")


def _block_value(state: CombatState, card: Card) -> float:
    # Block is worth the damage it actually prevents this turn, not its
    # printed number — otherwise the pilot never blocks chip damage.
    raw = _raw_block(card)
    if raw == 0:
        return 0.0
    prevented = max(0.0, _incoming_damage(state) - state.player.block)
    return min(raw, prevented)


def _scaling_value(state: CombatState, card: Card) -> float:
    val = 0.0
    for fx in card.effects:
        if fx["op"] == "apply_power" and fx.get("target", "self") == "self":
            # Cap per-power contribution: percent-stack powers (Vermillion
            # Pact 25, Durin 30) would otherwise dwarf everything.
            val += min(fx["amount"], 6) * 3
        elif fx["op"] == "apply_power":                  # enemy debuff
            val += fx["amount"] * 2
    # Setup is worth less as the fight winds down.
    return val * max(0.0, 1.0 - state.turn / 12.0) if val else 0.0


def _card_element(state: CombatState, card: Card) -> Optional[str]:
    if card.element != "none":
        return card.element
    if card.type == "attack" and state.player.cadence == "catalyst":
        return state.player.element
    return None


def _reaction_value(state: CombatState, card: Card) -> float:
    elem = _card_element(state, card)
    swirls = any(fx["op"] == "swirl" for fx in card.effects)
    applies = elem is not None or swirls or any(
        fx["op"] == "apply_aura" for fx in card.effects)
    if not applies:
        return 0.0
    # Triggering beats seeding: any living enemy holding a reactable aura.
    for e in state.living_enemies:
        if e.aura and (swirls or (elem and e.aura != elem)):
            return 6.0
    return 2.0


def _tempo_value(card: Card) -> float:
    val = 0.0
    for fx in card.effects:
        if fx["op"] in ("draw", "energy"):
            val += fx.get("amount", 1)
        elif fx["op"] == "gain_spark":
            val += fx.get("amount", 1) * 0.7    # sparks -> free attacks
        elif fx["op"] == "burst_energy":
            val += fx["amount"] / 10
    return val


def _score(state: CombatState, card: Card, w: dict) -> float:
    cost = card_cost(state, card)
    return (w["damage"] * _expected_damage(state, card)
            + w["block"] * _block_value(state, card)
            + w["scaling"] * _scaling_value(state, card)
            + w["reaction"] * _reaction_value(state, card)
            + w["tempo"] * _tempo_value(card)
            - w["cost"] * cost)


def _incoming_damage(state: CombatState) -> float:
    total = 0.0
    for e in state.living_enemies:
        if e.sleep_turns > 0 or e.frozen:
            continue
        intent = e.current_intent()
        if intent["kind"] == "attack":
            amount = intent["amount"] + intent.get("ramp", 0) * max(
                0, state.turn - intent.get("ramp_after", 0))
            per_hit = powers.modify_damage_dealt(e, amount)
            per_hit = powers.modify_damage_taken(state.player, per_hit)
            total += int(per_hit) * intent.get("times", 1)
    return total


def _lethal_card(state: CombatState, playable: list[Card]) -> Optional[Card]:
    """Single-card lethal check only — cheap and good enough (spec: dumb ok)."""
    remaining = sum(e.hp + e.block for e in state.living_enemies)
    for card in playable:
        if _expected_damage(state, card) >= remaining:
            return card
    return None
