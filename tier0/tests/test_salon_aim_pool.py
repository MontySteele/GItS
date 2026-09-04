"""`EB-451`: a Salon member's roll skips a Minion while a non-Minion stands.

THE FIND (Furina r7, fight 7). The run's ONE paid performance -- members had
gone dry, at three-quarters and no Encore, in every earlier fight -- rolled the
6-HP Eye with Teeth, whose own status line says it revives at full, while the
body that mattered stood beside it. The rule was printed and the outcome still
handed the Encore economy's payoff to the roll at the moment it was worth most.

R250'S SHAPE, ONE ROLLER OVER. That ruling made a Plan aim a non-Minion unless
it is aimed, over the same evidence, and `kokomi_plan.front_enemy` reads
`is_minion` for it. The r7 packet's §4 applies the same shape to the member
roll as an F default at its stated default.

BOTH ROLLERS, and there are exactly two: the tick (`salon_member_act`) and the
bow (`_salon_bow`). The C# twin is `SalonMemberPower.AimPool`, which
`PerformMember` and `Bow` both draw from.
"""

from __future__ import annotations

import inspect

from tier0.engine import effects
from tier0.engine.state import Enemy


def _enemy(name: str, minion: bool = False) -> Enemy:
    return Enemy(name=name, hp=20, max_hp=20, is_minion=minion)


def test_a_minion_is_out_of_the_pool_while_a_non_minion_stands():
    eye = _enemy("eye_with_teeth", minion=True)
    kin = _enemy("kin")

    assert effects.salon_aim_pool([eye, kin]) == [kin]


def test_board_order_survives_the_filter():
    first, decoy, last = _enemy("a"), _enemy("d", minion=True), _enemy("b")

    assert effects.salon_aim_pool([first, decoy, last]) == [first, last]


def test_an_all_minion_board_keeps_every_body():
    """`kokomi_plan.front_enemy`'s fallback, and the same argument: a
    performance that lands on nothing is worse than one that lands on the
    decoy. Without this the Salon would go silent on a board of adds."""
    adds = [_enemy("a", minion=True), _enemy("b", minion=True)]

    assert effects.salon_aim_pool(adds) == adds


def test_an_empty_board_answers_empty():
    """`salon_member_act` uses the living list as its "can the stage act at
    all" test before it rolls, so the empty answer has to stay empty."""
    assert effects.salon_aim_pool([]) == []


def test_both_rollers_draw_from_the_pool():
    """SOURCE-READ, and deliberately: `state.rng.choice` over the raw
    `living_enemies` is the exact line the find is about, and a behavioural
    test would have to pin an RNG stream to say which body it reached. There
    are two rollers and a fix on one of them is half a fix."""
    for fn in (effects.salon_member_act, effects._salon_bow):
        source = inspect.getsource(fn)
        assert "salon_aim_pool(state.living_enemies)" in source, fn.__name__
        assert "choice(state.living_enemies)" not in source, fn.__name__
