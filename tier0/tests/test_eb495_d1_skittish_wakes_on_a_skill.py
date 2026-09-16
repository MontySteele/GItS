"""`EB-495` D1 — a Skill's damage wakes `SkittishPower`, in BOTH engines now.

THE GAME IS THE TRUTH HERE and the sim was the model that had drifted.
`SkittishPower.AfterAttack` gates on

    command.DamageProps.HasFlag(ValueProp.Move)
        && command.ModelSource is CardModel          (SkittishPower.cs:58)

and never reads the card's printed `type:`. The mod's generator emits EVERY
damage clause — a Skill's and a Power's alike — as
`DamageCmd.Attack(...).FromCard(...)`, so all 17 non-Attack cards that deal
damage wake Skittish when they land. tier0 asked `source == "attack"`, which
is `card.type == "attack"`, and did not.

The repair is `effects.CARD_DAMAGE_SOURCES`, the sim's spelling of
"`ModelSource is CardModel`": the two literals `_op_damage` mints off a card.
The negative half matters as much as the positive one — a kit verb leaves the
mod through `ElementalHit.Deal`, which carries no `ModelSource` at all, so a
Bomb, a Plan and a performance still do NOT wake it. That whole column is the
atlas's wall of `none`, ruled by `EB-343` (R248), `EB-334` (R246) and
`EB-588`.

The census in `test_eb495_kit_verb_triggers.py` answers the same question one
`source` literal at a time. This file answers it the way a player meets it:
by playing a card.
"""

from __future__ import annotations

import pytest

from tier0.engine import effects
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy, make_state


def _hit(card_type: str):
    """Play one card of `card_type` that deals 5, into a Skittish 3 body."""
    enemy = make_enemy(hp=200)
    enemy.skittish = 3
    state = make_state(enemies=[enemy])
    card = Card(id=f"pin_{card_type}", name="pin", cost=1, type=card_type,
                effects=[{"op": "damage", "amount": 5, "target": "enemy"}])
    effects.resolve_card(state, card)
    return enemy


@pytest.mark.parametrize("card_type", ["attack", "skill", "power"])
def test_any_card_that_deals_damage_wakes_skittish(card_type):
    """D1, repaired. The printed type is not the question; being a card is."""
    enemy = _hit(card_type)
    assert enemy.skittish_fired is True
    assert enemy.block == 3


def test_a_kit_verbs_hit_still_does_not_wake_skittish():
    """The other side of the same gate, and the one that must not move: the
    one door (`ElementalHit.Deal`) hands the game no `ModelSource`, so a
    performance, a Bomb and a Plan are invisible to Skittish in both engines.
    """
    for source in ("salon", "bomb", "plan", "set_off", "furina_stage/act",
                   "companion", "burst"):
        enemy = make_enemy(hp=200)
        enemy.skittish = 3
        state = make_state(enemies=[enemy])
        effects.deal_damage_to_enemy(state, enemy, 5, source=source)
        assert enemy.skittish_fired is False, source
        assert enemy.block == 0, source
