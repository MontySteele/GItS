"""`EB-328`: the sim's side of "every modifier in the hit's order, once".

THE ROW. "The card face composes modifiers wrong: under Weak 1 and a
Strength-style buff the printed number disagrees with the dealt number in some
pairs." The C# side is `klee-mod/KleeCode/Powers/HitOrder.cs`, which records
the engine's order as decompiled off sts2.dll 0.111.0 and is pinned by
`klee-mod/KleeTests/HitOrderPinTests.cs` (the pairs, run against the game's own
hook methods) and `KleeTests/Prototype/Eb328FaceOrderTests.cs` (the face
shapes). The defect there was a folding card face multiplying the target's
Vulnerable over the top of `Hook.ModifyDamage`'s answer, which had already
folded it whenever the game named a body.

THE ORDER, and it is the same order in both engines:

    enchantment additive, enchantment multiplicative,
    EVERY additive term, EVERY multiplicative term, the cap, floor at 0

tier0 splits that chain across `powers.modify_damage_dealt` (the dealer's
additive Strength, then the dealer's multiplicative Weak) and
`powers.modify_damage_taken` (the target's multiplicative Vulnerable), with the
reaction amplifier between them and ONE truncation at the end.

WHAT THIS FILE PINS. One pin per modifier PAIR, each two-sided: the number the
order gives, and the number the WRONG order gives -- because a pin that only
asserted the right answer would pass on a build where the two collide. Then
the same pairs through the sim's own delivery, so "printed equals dealt" is a
statement about a hit and not about a formula. The Plan half and the Block
pair close it out.
"""

from __future__ import annotations

import pytest

from tier0 import constants as C
from tier0.engine import powers
from tier0.engine.state import CombatState


def _seat(**stacks):
    """A player Fighter carrying the named power stacks."""
    from tier0.tests.conftest import make_state

    state = make_state()
    for name, amount in stacks.items():
        state.player.powers[name] = amount
    return state


def _enemy(state: CombatState, **stacks):
    enemy = state.enemies[0]
    for name, amount in stacks.items():
        enemy.powers[name] = amount
    return enemy


def _composed(state, enemy, base: float) -> float:
    """The whole chain, in the engine's order, with no amplifier."""
    return powers.modify_damage_taken(
        enemy, powers.modify_damage_dealt(state.player, base))


# ---------------------------------------------------------------- the phases


def test_the_constants_are_the_ones_the_mod_mirrors():
    """No number in this file is typed twice: 0.75 and 1.5 are read off the
    constants `SimDamagePipeline` names as its own source."""
    assert C.WEAK_DEALT_MULT == 0.75
    assert C.VULNERABLE_TAKEN_MULT == 1.5


def test_every_additive_term_lands_before_every_multiplicative_one():
    """`Hook.ModifyDamage` runs the whole additive phase before the first
    multiplier, so Strength is inside the Weak reduction and not beside it."""
    state = _seat(strength=5, weak=1)
    assert powers.modify_damage_dealt(state.player, 4) == pytest.approx(6.75)
    # The other order, which is the shape of a face that reduces the printed
    # number and adds the buff afterwards.
    assert 4 * C.WEAK_DEALT_MULT + 5 == pytest.approx(8.0)


# ---------------------------------------------------------------- the pairs


def test_pair_weak_x_strength_is_the_sum_reduced_once():
    """The row's own example: `Slack Water` under Weak 1 and a flat +5 dealt 6
    -- (4 + 5) x 0.75 -- while its face printed 3, which is the base reduced
    with the buff dropped."""
    state = _seat(strength=5, weak=1)
    assert int(powers.modify_damage_dealt(state.player, 4)) == 6
    assert int(powers.modify_damage_dealt(_seat(weak=1).player, 4)) == 3


def test_pair_weak_x_vulnerable_is_one_product_not_two():
    """Both are multiplicative terms, so they compose into ONE product."""
    state = _seat(weak=1)
    enemy = _enemy(state, vulnerable=2)
    assert _composed(state, enemy, 4) == pytest.approx(4.5)
    # The C# defect, written in the sim's own vocabulary: the target's term a
    # second time over a number that already carried it.
    doubled = powers.modify_damage_taken(enemy, _composed(state, enemy, 4))
    assert doubled == pytest.approx(6.75)
    assert int(doubled) != int(_composed(state, enemy, 4))


def test_pair_strength_x_vulnerable_adds_then_multiplies_once():
    state = _seat(strength=5)
    enemy = _enemy(state, vulnerable=2)
    assert _composed(state, enemy, 4) == pytest.approx(13.5)
    doubled = powers.modify_damage_taken(enemy, _composed(state, enemy, 4))
    assert doubled == pytest.approx(20.25)


def test_pair_weak_x_strength_x_vulnerable_is_one_chain():
    """All three at once, which is the board the row was filed from."""
    state = _seat(strength=5, weak=1)
    enemy = _enemy(state, vulnerable=2)
    assert _composed(state, enemy, 4) == pytest.approx(10.125)


def test_pair_frail_x_dexterity_adds_before_it_multiplies():
    """The Block twin, and `modify_block_gained`'s own docstring pair: at 5
    block the two orders agree at 6 and at 11 they do not."""
    state = _seat(dexterity=3, frail=1)
    assert powers.modify_block_gained(state.player, 5) == 6
    assert powers.modify_block_gained(state.player, 11) == 10
    # Multiplying first and adding Dexterity after gives 11 -- a whole point,
    # and the direction that over-promises a seat's defence.
    assert int(11 * C.FRAIL_BLOCK_MULT + 3) == 11


# ------------------------------------------------- printed equals dealt


@pytest.mark.parametrize(
    "stacks,enemy_stacks,expected",
    [
        ({}, {}, 4),                                   # plain
        ({"weak": 1}, {}, 3),                          # Weak alone
        ({"strength": 5}, {}, 9),                      # a flat buff alone
        ({"strength": 5, "weak": 1}, {}, 6),           # Weak x Strength
        ({"weak": 1}, {"vulnerable": 2}, 4),           # Weak x Vulnerable
        ({"strength": 5}, {"vulnerable": 2}, 13),      # Strength x Vulnerable
        ({"strength": 5, "weak": 1}, {"vulnerable": 2}, 10),
    ],
)
def test_the_number_the_sim_delivers_is_the_composed_one(
        stacks, enemy_stacks, expected):
    """THE ACCEPTANCE, on a real hit: what leaves the enemy's HP is the chain
    composed once per modifier. A double-folded Vulnerable would show up here
    as 6 where the table says 4.

    The hit is aura-free and reaction-free (`element=None` keeps the amplifier
    at 1), so the only things in the number are the pair under test.
    """
    from tier0.engine import effects

    state = _seat(**stacks)
    enemy = _enemy(state, **enemy_stacks)
    enemy.aura = None
    hp = enemy.hp
    effects.deal_damage_to_enemy(state, enemy, 4, element=None,
                                 source="attack")
    assert hp - enemy.hp == expected
    assert int(_composed(state, enemy, 4)) == expected


# ------------------------------------------------------------- the Plan half


def test_the_plan_half_folds_hers_in_the_engine_s_order():
    """R246 pick 1 / `EB-599`: a Plan line folds her enchantment and her
    Strength at WRITING time and nothing of the target's. `EB-328` only has
    the order to say about it, and the order is the engine's -- the
    enchantment is applied ahead of the additive phase, so a multiplicative
    rider scales the printed number and not the Strength added after it.

    C# twin: `KokomiPlan.Hers`, pinned in `Eb328FaceOrderTests`."""
    from tier0.engine import kokomi_plan

    state = _seat(strength=3)
    assert kokomi_plan.hers(state, None, 4) == 7
    # Weak is deliberately absent, which is the one judgement `hers` makes
    # against `modify_damage_dealt` (round four-c's finding).
    assert kokomi_plan.hers(_seat(strength=3, weak=1), None, 4) == 7
