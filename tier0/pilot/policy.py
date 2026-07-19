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
from tier0.engine.combat import card_cost
from tier0.engine.state import Card, CombatState


def make_pilot(weights: dict):
    def pilot(state: CombatState) -> Optional[Card]:
        playable = [c for c in state.player.hand
                    if card_cost(state, c) <= state.player.energy]
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
        return best

    return pilot


def _expected_damage(state: CombatState, card: Card) -> float:
    total = 0.0
    for fx in card.effects:
        if fx["op"] == "damage":
            n_targets = len(state.living_enemies) if fx.get("target") == "all_enemies" else 1
            per_hit = powers.modify_damage_dealt(state.player, fx["amount"])
            total += per_hit * fx.get("times", 1) * n_targets
        elif fx["op"] == "place_bomb":
            total += fx["bomb_damage"] * fx.get("amount", 1)
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
            val += fx["amount"] * 3
        elif fx["op"] == "apply_power":                  # enemy debuff
            val += fx["amount"] * 2
    # Setup is worth less as the fight winds down.
    return val * max(0.0, 1.0 - state.turn / 12.0) if val else 0.0


def _reaction_value(state: CombatState, card: Card) -> float:
    if card.element == "none":
        return 0.0
    # Triggering beats seeding: any living enemy holding a different aura.
    for e in state.living_enemies:
        if e.aura and e.aura != card.element:
            return 6.0
    return 2.0 if any(fx.get("applies_element") or fx["op"] == "apply_aura"
                      for fx in card.effects) else 0.0


def _tempo_value(card: Card) -> float:
    return sum(fx["amount"] for fx in card.effects
               if fx["op"] in ("draw", "energy"))


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
