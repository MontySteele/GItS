"""Pin tests for the combat turn loop: the MAX_TURNS stall cap."""

from tier0 import constants as C
from tier0.engine.combat import run_fight
from tier0.engine.state import Card, Enemy, Player


def _filler_hand(n):
    return [Card(id=f"filler{i}", name="f", cost=9, type="skill")
            for i in range(n)]


def test_stall_cap_ends_fight_after_max_turns_rounds():
    """A fight that never resolves stops after exactly MAX_TURNS player
    rounds -- no 31st round -- and the capped fight is reported as a loss on
    the final turn number.

    THE DECK IS WHY THIS FIGHT REACHES THE CAP AT ALL (`EB-256`). The pin used
    to be built on an EMPTY deck, and an empty deck against a wall that does
    nothing is the no-progress loop the stall detector now ends at round 11 --
    so the same construction pins the detector today, one file over
    (`test_eb256_stall_detector`), and this pin needs a fight that is
    genuinely going somewhere. Forty filler cards cycling draw -> discard is
    that fight: nobody's HP or Block moves, but the piles do, so the
    fingerprint never repeats and the CAP is what stops it. The cap's own
    guarantee is unchanged and that is the point of keeping the case."""
    player = Player(hp=80, max_hp=80)
    player.draw_pile = _filler_hand(40)
    enemy = Enemy(hp=1000, max_hp=1000, name="wall",
                  intents=[{"kind": "block", "amount": 0}])

    st = run_fight(player, [enemy], lambda s: None, seed=0)

    assert st.stalled is False
    assert st.turn == C.MAX_TURNS
    assert sum(ev["event"] == "round_hp" for ev in st.log) == C.MAX_TURNS
    end = st.log[-1]
    assert end["event"] == "fight_end"
    assert end["won"] is False
    assert end["turns"] == C.MAX_TURNS


def test_the_frozen_fight_stops_at_the_stall_and_not_at_the_cap():
    """`EB-256`, and the case the pin above was quietly carrying: with NO
    deck there is nothing left that can change, so the fight is over as a
    question long before turn 30. It now ends as a recorded stall a third of
    the way in, and `won` is still False -- the word beside it is what is
    new, not the word itself."""
    player = Player(hp=80, max_hp=80)
    enemy = Enemy(hp=1000, max_hp=1000, name="wall",
                  intents=[{"kind": "block", "amount": 0}])

    st = run_fight(player, [enemy], lambda s: None, seed=0)

    assert st.stalled is True
    assert st.turn < C.MAX_TURNS
    assert [ev["event"] for ev in st.log].count("fight_stall") == 1
    assert st.log[-1]["won"] is False
