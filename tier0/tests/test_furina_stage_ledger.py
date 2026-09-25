"""FURINA, THE STAGE -- the Fanfare ledger adds up.

`furina_stage.book_gain` / `book_loss` / `book_paid` count the Stage's
Fanfare economy at each writer, and `tools/furina_stage_report.py` prints it
(report 6). The one thing a ledger must do is balance: whatever the stage
holds at the end of a fight is what it started with, plus every door Fanfare
came in by, minus every door it left by.

    start + gained - spent - paid_other - left - faded - hit == end

INSTRUMENT ONLY: nothing here is a balance claim (R215 B).
"""

import random

import pytest

from tier0.content import loader
from tier0.engine import combat, furina_stage
from tier0.engine.state import CombatState, Enemy, Player

FS = furina_stage


@pytest.fixture
def arm(monkeypatch):
    monkeypatch.setattr(FS, "FURINA_STAGE", True)


def _state(turn=1):
    st = CombatState(
        player=Player(hp=200, max_hp=200, fanfare_cap=99,
                      character_id="furina"),
        enemies=[Enemy(hp=99, max_hp=99, name="paper",
                       intents=[{"kind": "block", "amount": 0}])],
        rng=random.Random(0))
    st.turn = turn
    return st


def _balances(st):
    return FS.ledger_expected_end(st.stage_ledger) == FS.total_fanfare(st.player)


def test_with_the_flag_off_the_ledger_stays_empty():
    st = _state()
    FS.open_combat(st)
    FS.summon(st, "usher")
    FS.raise_fanfare(st, 5)
    FS.end_of_turn_acts(st)
    assert st.stage_ledger == {}


def test_a_scripted_fight_adds_up_door_by_door(arm):
    st = _state()
    FS.open_combat(st)                      # usher 3             opening +3
    FS.summon(st, "chevalmarin")            # chev 1              summon +1
    FS.summon(st, "crabaletta")             # crab 1              summon +1
    FS.raise_fanfare(st, 10)                # crab 11             card  +10
    st.turn = 2
    FS.turn_start_regen(st)                 # usher 4             regen +1
    assert FS.spend(st, 3) == 3             # crab 8              spent  3
    assert FS.absorb(st, 2) == 2            # usher 2             hit    2
    FS.end_of_turn_acts(st)                 # crab 8 -> 7         faded  1
    assert FS.final_bow(st) == 7            # crab leaves with 7  left   7
    assert FS.absorb(st, 5) == 2            # usher emptied       hit    2
    FS.settle_hit(st)                       # his bow: Block, no Fanfare
    assert FS.stage(st.player) == [["chevalmarin", 1]]
    assert FS.collect_all(st) == 1          # the Rare            spent  1
    FS.bow_and_return(st)                   # chev back at 1      return +1
    FS.raise_fanfare(st, 4)                 # chev 5              card  +4
    # THE OTHER-PAYER HOOK, as a guest will use it: book, then take.
    FS.book_paid(st, 2, payer="guest")
    FS.back(st.player)[1] -= 2              # chev 3              other  2
    assert FS.spend_all_of_back(st) == 3    # Bravura, chev bows  spent  3
    assert FS.stage(st.player) == []
    FS.raise_fanfare(st, 4)                 # empty-stage summon  +4

    led = st.stage_ledger
    assert led["start"] == 0
    assert led["gained"] == {
        "opening": 3, "regen": 1, "card": 14, "bow": 0, "power": 0,
        "summon": 2, "empty_summon": 4, "return": 1}
    assert led["spent"] == 7
    assert led["paid_other"] == {"guest": 2}
    assert led["left"] == 7
    assert led["faded"] == 1
    assert led["hit"] == 4
    assert led["back_at_turn_end"] == [7]
    assert FS.total_fanfare(st.player) == 4
    assert _balances(st)


def test_the_bow_and_power_doors_book_where_they_raise(arm):
    st = _state()
    FS.open_combat(st)
    FS.summon(st, "chevalmarin")
    p = st.player
    # Thunderous Applause: a Bow's Raise.
    p.powers[FS.THUNDEROUS_APPLAUSE] = 2
    p.stage_power_copies[FS.THUNDEROUS_APPLAUSE] = 1
    FS.raise_fanfare(st, 4)                 # chev 5
    FS.spend(st, 5)                         # chev bows; applause Raises 2
    # A Rapt Audience: a power's Raise off what the lead lost.
    FS.summon(st, "crabaletta")
    p.powers[FS.RAPT_AUDIENCE] = 50
    FS.absorb(st, 2)
    led = st.stage_ledger
    assert led["gained"]["bow"] == 2
    assert led["gained"]["power"] == 1
    assert _balances(st)


@pytest.mark.parametrize("deck", ["natural", "preserve", "expend"])
def test_real_fights_balance_every_time(arm, deck):
    from tools import furina_stage_report as report

    ids = dict(report.ARMS)[deck]
    for seed in range(6):
        player = (loader.build_player("furina") if ids is None else
                  loader.build_player_from_ids("furina", report.BASICS + ids))
        st = combat.run_fight(player, loader.build_encounter("attrition"),
                              _pilot(), seed=seed)
        led = st.stage_ledger
        assert led["gained"]["opening"] == 3
        assert led["back_at_turn_end"], "no turn-end sample was taken"
        assert _balances(st), (seed, led, FS.stage(st.player))


def _pilot():
    from tier0.pilot.policy import make_pilot
    return make_pilot(loader.pilot_weights("salon"))


# ---------------------------------------------------------------------------
# RULE 1: the performers are pets and live one combat. Every fight opens with
# Usher alone at 3, and every fight's ledger is its own.
# ---------------------------------------------------------------------------

def _opening(st):
    """The fight's first Stage event, which must be the relic's Usher."""
    return next(r for r in st.log if r["event"].startswith("stage_"))


def test_a_reused_player_opens_fight_two_with_usher_alone_at_three(arm):
    """THE WORST CASE: one Player object through two fights. `open_combat`
    fields Usher only onto an empty stage, so a stage that outlived fight one
    would open fight two on fight one's cast; `run_fight` clears it."""
    player = loader.build_player("furina")
    first = combat.run_fight(player, loader.build_encounter("attrition"),
                             _pilot(), seed=3)
    assert first.player.alive and FS.stage(player), \
        "fight one must end with a cast standing, or this pins nothing"
    second = combat.run_fight(player, loader.build_encounter("attrition"),
                              _pilot(), seed=4)
    opening = _opening(second)
    assert (opening["event"], opening["member"], opening["fanfare"]) \
        == ("stage_open", "usher", 3)
    assert second.stage_ledger is not first.stage_ledger
    assert second.stage_ledger["start"] == 0
    assert second.stage_ledger["gained"]["opening"] == 3
    assert _balances(second)


def test_the_run_path_opens_every_fight_with_usher_alone_at_three(arm,
                                                                  monkeypatch):
    """The harness's two-fight gauntlet (swarm, then punisher, HP carried)."""
    from tier0.harness import runner

    states = []

    def recording(*a, **kw):
        st = combat.run_fight(*a, **kw)
        states.append(st)
        return st

    monkeypatch.setattr(runner, "run_fight", recording)
    runner.run_battery("furina", "starter", "gauntlet", "salon", 3, 11)
    assert len(states) >= 4, "the gauntlet should reach its second fight"
    for st in states:
        opening = _opening(st)
        assert (opening["event"], opening["member"], opening["fanfare"]) \
            == ("stage_open", "usher", 3)
        assert st.stage_ledger["start"] == 0
        assert _balances(st)
