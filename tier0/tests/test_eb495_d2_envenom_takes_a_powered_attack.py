"""`EB-495` D2 — `EnvenomPower` reads a POWERED hit, not an Attack card.

THE GAME IS THE TRUTH HERE. `EnvenomPower.AfterDamageGiven` gates on

    dealer == Owner && props.IsPoweredAttack() && result.UnblockedDamage > 0
                                                  (EnvenomPower.cs:22)

and `IsPoweredAttack()` is `ValueProp.Move` without `ValueProp.Unpowered` —
it says nothing about `CardType.Attack`. Every damage clause the mod's
generator emits is `DamageCmd.Attack(...).FromCard(...)`, powered and Move,
so a SKILL that deals damage poisons in the game. The sim returned early on
`source != "attack"` and did not.

The two pins below are the two halves of the repaired predicate, and the
negative one is the one that must never move: a kit verb leaves the mod
through `ElementalHit.Deal`, which passes `ValueProp.Unpowered` with
`dealer: null`, so a performance, a Bomb, a Mine and a Plan have never
poisoned in the game and do not here. That is the atlas's T4 column — ruled
by `EB-343` (R248), `EB-334` (R246) and `EB-588`, all three of which say in
their own words that a kit verb is not a hit.
"""

from __future__ import annotations

import pytest

from tier0.engine import effects
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy, make_state


def _play(card_type: str):
    enemy = make_enemy(hp=200)
    state = make_state(enemies=[enemy])
    state.player.powers["envenom"] = 2
    card = Card(id=f"pin_{card_type}", name="pin", cost=1, type=card_type,
                effects=[{"op": "damage", "amount": 6, "target": "enemy"}])
    effects.resolve_card(state, card)
    return enemy


@pytest.mark.parametrize("card_type", ["attack", "skill", "power"])
def test_a_cards_damage_poisons_whatever_the_card_is_called(card_type):
    """D2, repaired. The printed type is not the question; a powered Move out
    of a card is."""
    assert _play(card_type).powers.get("poison", 0) == 2


def test_a_kit_verbs_hit_does_not_poison():
    """The `Unpowered` half, asserted through the source vocabulary the kit
    verbs actually mint."""
    for source in ("salon", "salon_final_bow", "bomb", "bomb_echo", "plan",
                   "set_off", "casket", "furina_stage/act",
                   "furina_stage/bow", "companion", "burst"):
        enemy = make_enemy(hp=200)
        state = make_state(enemies=[enemy])
        state.player.powers["envenom"] = 2
        effects.deal_damage_to_enemy(state, enemy, 6, source=source)
        assert enemy.powers.get("poison", 0) == 0, source


def test_an_unpowered_card_sourced_hit_does_not_poison():
    """The flag read literally. `powered=False` is the sim's
    `ValueProp.Unpowered`, and `IsPoweredAttack()` is false for it whatever
    the damage came out of."""
    enemy = make_enemy(hp=200)
    state = make_state(enemies=[enemy])
    state.player.powers["envenom"] = 2
    effects.deal_damage_to_enemy(state, enemy, 6, source="attack",
                                 powered=False)
    assert enemy.powers.get("poison", 0) == 0


def test_a_fully_blocked_card_hit_does_not_poison():
    """`UnblockedDamage > 0`, unchanged by this repair and pinned beside it so
    a later edit to the gate cannot drop it silently."""
    enemy = make_enemy(hp=200)
    enemy.block = 50
    state = make_state(enemies=[enemy])
    state.player.powers["envenom"] = 2
    effects.deal_damage_to_enemy(state, enemy, 6, source="card")
    assert enemy.powers.get("poison", 0) == 0
