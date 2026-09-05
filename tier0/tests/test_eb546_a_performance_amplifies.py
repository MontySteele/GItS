"""`EB-546`: a member performance into a foreign aura amplifies, paid or dry.

WHAT THE SEAT SAW (Furina r13, assembled lane, fight 1 turn 2). "The salon log
read: *Crabaletta hit Sludge Spinner for 6 Hydro, and left no aura on it.* The
enemy was wearing Pyro Aura 2, and Crabaletta was at full strength (Encore
paid). Vaporize is printed as *this hit deals 1.5x damage and consumes the
aura* -- so 9. The HP bar moved 24 to 18. **Six.** The aura was consumed; the
multiplier was not applied." And in fight 2 the same card into the same aura
while DRY hit for 6 off a 4.5 base, which is 1.5x. The seat could not reconcile
the two, and neither could the round.

WHAT THIS FILE IS. The row asks for the reproduction first: a performance into
a Pyro aura at Encore paid and at Encore dry, with the amplified number pinned
on both. THE SIM AMPLIFIES ON BOTH -- 9 paid and 6 dry -- so the invariant the
seat expected is the invariant this engine has, and it is held here rather than
re-derived the next time the reading comes back. The mod's arithmetic and its
wiring are pinned in `KleeTests/Prototype/Round19Tests.cs`.

WHAT IT DOES NOT ANSWER, and the row stays open on it: the live 6. Neither
engine's code drops the amplifier on a paid performance, and the paths that
could have -- a dry cut mistaken for a paid one, an aura that had expired, a
second consumer reaching the body first -- are each excluded by one of the
readings the seat wrote down (the log said "left no aura", which is the branch
that reacts; the same fight's dry hit did multiply). The next Furina round owes
the raw log rather than another derivation.

NOTHING MEASURED HERE IS QUOTABLE (R215 B).
"""

from __future__ import annotations

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import effects, furina_reframe
from tier0.engine.state import CombatState
from tier0.tests.conftest import make_enemy

ENEMY_HP = 400
#: Crabaletta's printed performance and the two multipliers the reading turns
#: on. Read off the constants rather than typed, so a retune moves the pins.
PRINTED = C.SALON_MEMBERS["crabaletta"]["tick"]["damage"]
DRY = C.SALON_DRY_DAMAGE_MULT
VAPORIZE = C.VAPORIZE_MULT


@pytest.fixture(autouse=True)
def manual_on(monkeypatch):
    """A member performs on a play only under the reframe's MANUAL leg."""
    for flag in ("FURINA_REFRAME", "FURINA_REFRAME_MANUAL"):
        monkeypatch.setattr(furina_reframe, flag, True)


def _board(encore: int):
    p = loader.build_player("furina")
    p.salon = ["crabaletta"]
    p.powers["salon_member"] = 1
    p.encore = encore
    enemy = make_enemy(hp=ENEMY_HP)
    enemy.aura = "pyro"
    enemy.aura_turns = 2
    return CombatState(player=p, enemies=[enemy], rng=random.Random(3))


def test_a_paid_performance_into_pyro_vaporizes():
    """The seat's own board, played: full strength into a Pyro aura."""
    st = _board(encore=9)
    enemy = st.enemies[0]

    effects.salon_member_act(st, "crabaletta")

    assert enemy.hp == ENEMY_HP - int(PRINTED * VAPORIZE)
    assert enemy.hp == ENEMY_HP - 9, "the number the seat expected and did not get"
    assert enemy.aura is None, "the aura is consumed by the reaction"


def test_a_dry_performance_into_pyro_vaporizes_too():
    """The other half, and the one the seat DID see: the dry cut is a size and
    the amplifier is a separate term, so a member with no Encore still
    multiplies what it deals."""
    st = _board(encore=0)
    enemy = st.enemies[0]

    effects.salon_member_act(st, "crabaletta")

    assert enemy.hp == ENEMY_HP - int(int(PRINTED * DRY) * VAPORIZE)
    assert enemy.hp == ENEMY_HP - 6
    assert enemy.aura is None


def test_the_log_carries_the_landed_number_and_not_the_tick():
    """`EB-511`'s rule, which is what makes the two tests above readable off a
    screen: the row a seat reconciles the fight's HP against is the number that
    LANDED, after the dealer's terms, the amplifier and the target's."""
    st = _board(encore=9)

    effects.salon_member_act(st, "crabaletta")

    hit = next(ev for ev in st.log if ev["event"] == "damage")
    assert hit["base"] == PRINTED
    assert hit["amount"] == int(PRINTED * VAPORIZE)


def test_a_performance_into_a_bare_body_applies_its_own_element():
    """The board the paid reading would look like if the aura had expired, and
    it is here because it is the one reading that produces the seat's 6 without
    a defect -- and it is EXCLUDED by the seat's own log line, which said the
    body was left wearing nothing. A bare body comes out wearing Hydro."""
    st = _board(encore=9)
    enemy = st.enemies[0]
    enemy.aura = None
    enemy.aura_turns = 0

    effects.salon_member_act(st, "crabaletta")

    assert enemy.hp == ENEMY_HP - PRINTED
    assert enemy.aura == "hydro"
