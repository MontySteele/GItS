"""Reaction table tests, including the spec §4.4 critical property:
amplifiers affect ONE hit and consume the aura — never persistent."""

from tier0 import constants as C
from tier0.engine import reactions
from tier0.tests.conftest import make_enemy, make_state


def hit(state, enemy, element, dmg=10):
    return reactions.resolve_hit(state, enemy, element, dmg)


def test_first_element_applies_aura(state):
    e = state.enemies[0]
    assert hit(state, e, "pyro") == 10
    assert e.aura == "pyro"
    assert e.aura_turns_left == C.AURA_DURATION_TURNS


def test_same_element_refreshes(state):
    e = state.enemies[0]
    hit(state, e, "pyro")
    e.aura_turns_left = 1
    hit(state, e, "pyro")
    assert e.aura_turns_left == C.AURA_DURATION_TURNS


def test_vaporize_amplifies_one_hit_and_consumes_aura(state):
    e = state.enemies[0]
    hit(state, e, "hydro")
    amped = hit(state, e, "pyro")
    assert amped == 10 * C.VAPORIZE_MULT
    # CRITICAL: aura consumed, next hit NOT amplified.
    assert e.aura is None
    followup = hit(state, e, "pyro")
    assert followup == 10          # no persistent multiplier, ever
    assert e.aura == "pyro"        # un-reacted element sticks as new aura


def test_melt_mult(state):
    e = state.enemies[0]
    hit(state, e, "cryo")
    assert hit(state, e, "pyro") == 10 * C.MELT_MULT


def test_overload_splashes_all_enemies():
    st = make_state(enemies=[make_enemy(hp=30, name="a"),
                             make_enemy(hp=30, name="b")])
    a, b = st.enemies
    hit(st, a, "electro", 0)
    hit(st, a, "pyro", 5)
    assert a.hp == 30 - C.OVERLOAD_SPLASH   # splash; the 5 resolves in effects.py
    assert b.hp == 30 - C.OVERLOAD_SPLASH


def test_superconduct_applies_vulnerable(state):
    e = state.enemies[0]
    hit(state, e, "cryo", 0)
    hit(state, e, "electro", 5)
    assert e.powers["vulnerable"] == C.SUPERCONDUCT_VULN


def test_electrocharged_applies_dot(state):
    e = state.enemies[0]
    hit(state, e, "hydro", 0)
    hit(state, e, "electro", 5)
    assert e.powers["dot"] == C.ELECTROCHARGED_DOT


def test_frozen_skips_next_intent(state):
    e = state.enemies[0]
    hit(state, e, "hydro", 0)
    hit(state, e, "cryo", 5)
    assert e.frozen


def test_frozen_boss_resist():
    st = make_state(enemies=[make_enemy(hp=100, name="boss", is_boss=True)])
    e = st.enemies[0]
    hit(st, e, "hydro", 0)
    hit(st, e, "cryo", 5)
    assert not e.frozen            # consumed with no effect (DECISIONS.md)
    assert e.aura is None


def test_swirl_copies_aura_to_all():
    st = make_state(enemies=[make_enemy(hp=30, name="a"),
                             make_enemy(hp=30, name="b"),
                             make_enemy(hp=30, name="c")])
    a, b, c = st.enemies
    hit(st, a, "pyro", 0)
    hit(st, a, "anemo", 5)
    assert all(e.aura == "pyro" for e in (a, b, c))


def test_anemo_geo_leave_no_aura(state):
    e = state.enemies[0]
    hit(state, e, "anemo")
    assert e.aura is None
    hit(state, e, "geo")
    assert e.aura is None


def test_crystallize_grants_block(state):
    e = state.enemies[0]
    hit(state, e, "pyro", 0)
    hit(state, e, "geo", 5)
    assert state.player.block == C.CRYSTALLIZE_BLOCK


def test_aura_expiry_logged_as_waste(state):
    e = state.enemies[0]
    hit(state, e, "pyro")
    for _ in range(C.AURA_DURATION_TURNS):
        reactions.tick_auras(state)
    assert e.aura is None
    assert any(ev["event"] == "aura_wasted" for ev in state.log)
