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
    assert a.powers["weak"] == C.OVERLOAD_WEAK
    assert "weak" not in b.powers           # stagger belongs to reacted target


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


def test_frozen_soft_control(state):
    # Frozen v2 (principles v1.5): no skip — the action deals -50% damage.
    # NC-7 (R116): the freeze is a TIMER, so acting no longer consumes it;
    # the clock at the end of the enemy side does.
    from tier0.engine.combat import _enemy_turn
    e = state.enemies[0]
    e.intents = [{"kind": "attack", "amount": 10}]
    hit(state, e, "hydro", 0)
    hit(state, e, "cryo", 5)
    assert e.frozen == 1
    hp = state.player.hp
    _enemy_turn(state, e)
    assert state.player.hp == hp - int(10 * C.FROZEN_DAMAGE_MULT)
    assert e.frozen == 1                    # acting does NOT spend it
    e.frozen -= 1                           # the side-end clock does
    hp = state.player.hp
    _enemy_turn(state, e)
    assert state.player.hp == hp - 10       # back to full damage


def test_frozen_stacking_extends_the_timer(state):
    """NC-7 (R116): stacking EXTENDS. Two applications, two halved actions.

    This is the half the sim adopted from the mod, whose FrozenPower was
    already a Counter. Under the old boolean a second freeze was inert.
    """
    from tier0.engine.combat import _enemy_turn
    e = state.enemies[0]
    e.intents = [{"kind": "attack", "amount": 10}]
    hit(state, e, "hydro", 0)
    hit(state, e, "cryo", 5)
    hit(state, e, "hydro", 0)
    hit(state, e, "cryo", 5)
    assert e.frozen == 2
    for _ in range(2):
        hp = state.player.hp
        _enemy_turn(state, e)
        assert state.player.hp == hp - int(10 * C.FROZEN_DAMAGE_MULT)
        e.frozen -= 1                       # one enemy side each
    assert e.frozen == 0
    hp = state.player.hp
    _enemy_turn(state, e)
    assert state.player.hp == hp - 10


def test_the_frozen_clock_does_not_ask_whether_the_enemy_acted():
    """NC-7 (R116): the tick is unconditional, because the mod's is.

    A sleeping enemy loses its freeze anyway. Stated as a test because the
    conditional version is the natural thing to write and would be a second
    ruling rather than an implementation of this one.
    """
    from tier0.engine.combat import _run_rounds
    st = make_state(enemies=[make_enemy(hp=400, name="sleeper")])
    e = st.enemies[0]
    e.intents = [{"kind": "attack", "amount": 1}]
    e.frozen = 1
    e.sleep_turns = 3                       # it will not act at all
    st.player.hand = []
    st.player.draw_pile = []
    st.player.discard_pile = []
    _run_rounds(st, lambda _state: None)    # a pilot that plays nothing
    assert e.sleep_turns < 3                # the enemy side did run
    assert e.frozen == 0


def test_shatter_clears_the_whole_timer(state):
    """NC-7 (R116): Shatter removes the status, not one turn of it -- the
    mod's `PowerCmd.Remove` takes every stack with it, and a Shatter that
    left a stack standing would be a freeze the player paid to end and did
    not."""
    from tier0.engine.effects import deal_damage_to_enemy
    e = state.enemies[0]
    hit(state, e, "hydro", 0)
    hit(state, e, "cryo", 5)
    hit(state, e, "hydro", 0)
    hit(state, e, "cryo", 5)
    assert e.frozen == 2
    deal_damage_to_enemy(state, e, 5, element=None, source="attack")
    assert e.frozen == 0


def test_shatter_on_attack_hit(state):
    # v1.5: while Frozen, the first Attack hit Shatters — bonus damage,
    # removes Frozen. The freezing hit itself must NOT shatter.
    from tier0.engine.effects import deal_damage_to_enemy
    e = state.enemies[0]
    hit(state, e, "hydro", 0)
    hp_before = e.hp
    deal_damage_to_enemy(state, e, 5, element="cryo", source="attack")
    assert e.frozen                         # freezing hit didn't self-shatter
    assert e.hp == hp_before - 5
    hp_before = e.hp
    deal_damage_to_enemy(state, e, 5, element=None, source="attack")
    assert not e.frozen
    assert e.hp == hp_before - 5 - C.SHATTER_DAMAGE
    assert any(ev["event"] == "shatter" for ev in state.log)


def test_frozen_boss_becomes_vulnerable():
    # Round-3 ruling (decision-2 contingency triggered): bosses consume
    # Frozen for Vulnerable 2 instead of a skipped intent.
    st = make_state(enemies=[make_enemy(hp=100, name="boss", is_boss=True)])
    e = st.enemies[0]
    hit(st, e, "hydro", 0)
    hit(st, e, "cryo", 5)
    assert not e.frozen
    assert e.powers["vulnerable"] == C.FROZEN_BOSS_VULN
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
