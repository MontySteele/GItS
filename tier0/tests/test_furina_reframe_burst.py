"""Furina reframe, R251 / `EB-365` -- the SHIPPED Burst meter retires under
the arm, and only under the arm.

The pick is `review/ruled/furina-reframe-round-1-2026-09-04.md` §6 pick 1,
option (1): the round-one seat's meter read `78/70`, over its own cap, and
*Let the People Rejoice* arrived off that overflow to take the boss from 28 to
14 -- so the run's clutch turn was the shipped kit's and not the reframe's.
R220 B had sequenced the Burst fold last; the new fact is that the shipped
meter sits inside every Furina read until it goes.

ARM-ONLY. The shared retirement (`EB-199`, `EB-200`) still owns the shipped
engines, so every test below comes in a pair: the same board with
`FURINA_REFRAME_BURST` on and with it off, and the OFF half is the only
assertion that can catch the leg leaking into the engine Klee and Kokomi are
still played on.

The mod's twin is `klee-mod/KleeTests/Prototype/FurinaReframeBurstTests.cs`,
in the same order.
"""

import random

import pytest

from tier0.content import loader
from tier0.engine import combat, furina_reframe, resources
from tier0.engine.state import CombatState
from tier0.tests.conftest import make_enemy

FR = furina_reframe


def _state(character="furina", seed=0):
    return CombatState(player=loader.build_player(character),
                       enemies=[make_enemy(hp=300)],
                       rng=random.Random(seed))


@pytest.fixture
def retired(monkeypatch):
    monkeypatch.setattr(FR, "FURINA_REFRAME", True)
    monkeypatch.setattr(FR, "FURINA_REFRAME_BURST", True)


# ======================================================================
# 0. THE FLAG
# ======================================================================

def test_the_leg_is_scoped_to_furina(monkeypatch):
    """One character's redesign, and in co-op the other seat may be Klee or
    Kokomi -- each of whom owns a Burst meter this leg must not touch."""
    monkeypatch.setattr(FR, "FURINA_REFRAME", True)
    monkeypatch.setattr(FR, "FURINA_REFRAME_BURST", True)

    assert FR.burst_retired(loader.build_player("furina"))
    assert not FR.burst_retired(loader.build_player("klee"))
    assert not FR.burst_retired(loader.build_player("kokomi"))


# ======================================================================
# 1. THE FEED -- nothing fills the meter under the arm
# ======================================================================

def test_the_meter_fills_with_the_flag_off():
    st = _state()

    resources.gain_burst(st, 5, "reaction")

    assert st.player.burst_energy == 5
    assert [ev for ev in st.log if ev["event"] == "burst_income"]


def test_nothing_feeds_the_meter_under_the_arm(retired):
    """Klee's `EB-266` and Kokomi's `EB-327` one character over, and fixed at
    the same place: the funnel every source lands in, because the arm's answer
    is "she has no Burst meter" and not "reactions in particular do not feed
    it"."""
    st = _state()

    for source in ("reaction", "skill_tag", "card", "salon_tick"):
        resources.gain_burst(st, 5, source)

    assert st.player.burst_energy == 0
    assert [ev for ev in st.log if ev["event"] == "burst_income"] == []


def test_the_other_two_arms_keep_their_own_guards(retired):
    """The Furina guard is an ADDITIONAL early return at the same funnel, not a
    replacement: Klee's and Kokomi's still answer for their own characters, and
    a Klee in the same co-op combat is unaffected by this flag."""
    st = _state(character="klee")

    resources.gain_burst(st, 5, "reaction")

    assert st.player.burst_energy == 5


# ======================================================================
# 2. THE GRANT -- Let the People Rejoice is never in hand
# ======================================================================

def test_the_kit_card_is_granted_at_a_full_meter_with_the_flag_off():
    st = _state()
    st.player.burst_energy = st.player.burst_max

    combat.grant_charged_kit(st)

    assert [c.id for c in st.player.hand] == ["let_the_people_rejoice"]


def test_the_kit_card_is_never_granted_under_the_arm(retired):
    """Unreachable in play -- nothing fills the meter -- and asserted anyway,
    because "Let the People Rejoice is not part of the reframe" is a rule of
    the arm rather than a consequence of one guard sitting upstream."""
    st = _state()
    st.player.burst_energy = st.player.burst_max

    combat.grant_charged_kit(st)

    assert st.player.hand == []
    assert [ev for ev in st.log if ev["event"] == "kit_burst_granted"] == []


def test_klees_kit_grant_still_fires_under_the_furina_flag(retired):
    st = _state(character="klee")
    st.player.burst_energy = st.player.burst_max

    combat.grant_charged_kit(st)

    assert [c.id for c in st.player.hand] == ["sparks_n_splash"]


# ======================================================================
# 3. NOTHING OUTSIDE THE FLAG MOVED
# ======================================================================

def test_the_shipped_engine_is_byte_identical_with_the_flag_off():
    """The shared retirement (`EB-199`, `EB-200`) owns the shipped engines, so
    the meter, its ceiling and the kit card are all still exactly where they
    were on a tree with the arm off."""
    p = loader.build_player("furina")

    assert p.burst_max == 70
    assert [c.id for c in p.kit_cards] == ["let_the_people_rejoice"]
    assert not FR.burst_retired(p)
