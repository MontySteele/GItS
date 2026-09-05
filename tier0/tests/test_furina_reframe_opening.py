"""THE OPENING ENCORE (`EB-479`, R258) -- the sim half.

Under the reframe Furina starts every combat with
`furina_reframe.OPENING_ENCORE`, so turn one can pay one thing: a Spotlight
designation or a member performing wet rather than at 3/4. Both of those doors
cost 2, and she had 0. Rounds 5 to 8 each read her first turn as no decision,
and round 9 called the opening "by construction its own weakest version".

WHAT IS PINNED HERE: the amount, the site, the once-per-combat, the character
limb, and the flag off. The mod's twin is `FurinaReframeOpening.GrantEncore`,
on `AfterPlayerTurnStart`, and its own pins are in
`klee-mod/KleeTests/Prototype/FurinaReframeRuleTests.cs`.

NOTHING MEASURED ON A PROTOTYPE ROW IS QUOTABLE (R215 B): these are shape
assertions about an engine, not numbers about a game.
"""

import random

import pytest

from tier0.engine import combat, furina_reframe
from tier0.engine.state import Card, CombatState, Enemy, Player

FR = furina_reframe


@pytest.fixture
def arm(monkeypatch):
    """The MASTER flag and no leg: the opening belongs to the whole reframe,
    which is what `opening_encore` reads and `FurinaReframe.LiveFor` mirrors."""
    monkeypatch.setattr(FR, "FURINA_REFRAME", True)


def _furina(**kw):
    """A Furina with the resource pair. `fanfare_cap` is the marker the
    engine's own Furina telemetry gates on, so a fixture without it is one
    half the log is blind to."""
    return Player(hp=200, max_hp=200, fanfare_cap=99,
                  character_id="furina", **kw)


def _state(player=None, turn=1):
    st = CombatState(player=player or _furina(),
                     enemies=[Enemy(hp=99, max_hp=99, name="paper",
                                    intents=[{"kind": "block", "amount": 0}])],
                     rng=random.Random(0))
    st.turn = turn
    return st


def _fight(player):
    """One real fight, won on the first turn by a 50-damage card, so the
    opening grant is the only thing that ever touches the buffer."""
    finisher = Card(id="finisher", name="Finisher", cost=0, type="attack",
                    effects=[{"op": "damage", "amount": 50, "target": "enemy"}])

    def pilot(s):
        return next((c for c in s.player.hand if c.id == "finisher"
                     and combat.card_playable(s, c)), None)

    player.draw_pile = [finisher]
    return combat.run_fight(
        player,
        [Enemy(hp=5, max_hp=5, name="paper",
               intents=[{"kind": "block", "amount": 0}])],
        pilot, seed=1)


def test_the_arm_opens_the_combat_with_two_encore(arm):
    st = _state()
    FR.grant_opening_encore(st)
    assert st.player.encore == FR.OPENING_ENCORE == 2


def test_the_shipped_kit_opens_on_nothing():
    """FLAG OFF IS THE SHIPPED OPENING, which is zero and always has been."""
    st = _state()
    FR.grant_opening_encore(st)
    assert st.player.encore == 0
    assert FR.opening_encore(st.player) == 0


def test_no_other_seat_is_paid(arm):
    """`is_furina`'s limb: in co-op the other seat may be Klee, and a bare
    flag read would hand him a buffer he has no rule for."""
    st = _state(player=Player(hp=200, max_hp=200, character_id="klee"))
    FR.grant_opening_encore(st)
    assert st.player.encore == 0


def test_it_is_turn_one_and_not_every_turn(arm):
    """`== 1` rather than `<= 1`, the opening Spark's own guard: a second turn
    pays nothing, and an extra first turn cannot pay twice."""
    st = _state(turn=2)
    FR.grant_opening_encore(st)
    assert st.player.encore == 0


def test_a_real_fight_opens_on_two_and_says_so_once(arm):
    """The SITE, through the engine rather than the reader: the grant lands in
    `_player_turn` at the same place `klee_overhaul.turn_start_late` does, so a
    fight that starts is a fight that opens with the buffer filled."""
    st = _fight(_furina())
    opened = [e for e in st.log if e["event"] == "fr_opening_encore"]
    assert [e["amount"] for e in opened] == [2]
    assert st.player.encore == 2          # nothing in the fight spends it


def test_a_real_fight_with_the_flag_off_opens_on_nothing():
    st = _fight(_furina())
    assert [e for e in st.log if e["event"] == "fr_opening_encore"] == []
    assert st.player.encore == 0
