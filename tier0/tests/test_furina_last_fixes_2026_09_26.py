"""Furina, the Stage: the last fixes from the 2026-09-26 wave-3 seat round
(lane 3, seat b). The C# twin is
`klee-mod/KleeTests/Prototype/FurinaLastFixes20260926Tests.cs`.

1. NAVIA'S BOW READS THE BAR SHE HAD. The seat: "Navia's bow is always worth
   nothing when she dies to a hit or a Spend." The designer's ruling: her Bow
   deals damage equal to the Fanfare she had before whatever emptied her --
   the hit that took her down, the Spend, the payment, Let the People
   Rejoice. Wriothesley's rule 6 ("His Bow on a hit reads the hit that took
   him down") is the precedent.

2. AN ANSWERED CHOOSER IS A TRANSITION, NOT A SCREEN. The seat: "Arkhe
   Alignment's chooser opened twice in a row" with one copy in play. The
   lane's own game log has exactly one `chose cards [...ARKHE_OUSIA_OPTION]`
   per turn, so the game asked once; the page drew the answered chooser a
   second time, in the frame before the game took it off the overlay stack.
"""

from __future__ import annotations

import random

import pytest

from tier0.engine import combat, furina_stage
from tier0.engine.state import CombatState, Enemy, Player
from understudy import blindplay_read

FS = furina_stage


@pytest.fixture
def arm(monkeypatch):
    yield


def _state(stage, hp=100, intents=None):
    player = Player(hp=200, max_hp=200, fanfare_cap=99,
                    character_id="furina")
    player.stage = [list(pair) for pair in stage]
    st = CombatState(player=player, enemies=[
        Enemy(hp=hp, max_hp=hp, name="paper",
              intents=intents or [{"kind": "block", "amount": 0}])],
        rng=random.Random(0))
    st.turn = 2
    return st


# ---- 1. Navia's Bow ----------------------------------------------------------

def test_a_hit_that_empties_navia_bows_her_for_the_bar_she_had(arm):
    st = _state([["navia", 6], ["usher", 3]],
                intents=[{"kind": "attack", "amount": 9}])
    combat._enemy_turn(st, st.enemies[0])
    assert [m for m, _f in st.player.stage] == ["usher"]
    assert st.enemies[0].hp == 100 - 6


def test_a_spend_that_empties_navia_bows_her_for_the_bar_she_had(arm):
    st = _state([["usher", 3], ["navia", 4]])
    assert FS.spend(st, 4) == 4
    assert st.enemies[0].hp == 100 - 4


def test_bravura_and_final_bow_cash_her_out_and_her_bow_still_deals_it(arm):
    st = _state([["usher", 3], ["navia", 7]])
    assert FS.spend_all_of_back(st) == 7
    assert st.enemies[0].hp == 100 - 7
    st = _state([["usher", 3], ["navia", 5]])
    assert FS.final_bow(st) == 5
    assert st.enemies[0].hp == 100 - 5


def test_let_the_people_rejoice_bows_navia_for_the_bar_it_took(arm):
    st = _state([["usher", 3], ["navia", 11]])
    assert FS.collect_all(st) == 14
    FS.bow_and_return(st)
    assert st.enemies[0].hp == 100 - 11
    # And they all return with 1.
    assert st.player.stage == [["usher", FS.SUMMON_FANFARE],
                               ["navia", FS.SUMMON_FANFARE]]


def test_a_payment_that_empties_navia_bows_her_for_what_she_paid(arm):
    """Clorinde takes 1 from each other performer: Navia at 1 is emptied by
    the tax and Bows for the 1 she had."""
    st = _state([["clorinde", 4], ["navia", 1]])
    FS.perform(st, "clorinde")
    assert [m for m, _f in st.player.stage] == ["clorinde"]
    assert st.enemies[0].hp == 100 - FS.ACT_CLORINDE_DAMAGE - 1


def test_her_live_act_still_reads_her_bar(arm):
    st = _state([["navia", 5]])
    FS.perform(st, "navia")
    assert st.enemies[0].hp == 100 - 5
    assert st.player.stage == [["navia", 5]]


# ---- 2. An answered chooser ---------------------------------------------------

def _chooser(answered):
    blob = {"screen_type": "choose", "prompt": "Choose a card.",
            "cards": [{"index": 0, "name": "Ousia"},
                      {"index": 1, "name": "Pneuma"}]}
    if answered is not None:
        blob["answered"] = answered
    return {"state_type": "card_select", "card_select": blob}


def test_an_answered_chooser_is_ridden_out_and_an_open_one_is_a_screen():
    assert blindplay_read.transient(_chooser(True))
    assert not blindplay_read.transient(_chooser(False))
    # An older bridge that does not say is a screen, as before.
    assert not blindplay_read.transient(_chooser(None))


def test_settle_waits_for_the_game_to_take_an_answered_chooser_down():
    class Wire:
        def __init__(self):
            self.reads = 0

        def get_state(self):
            self.reads += 1
            return {"state_type": "monster", "battle": {"is_play_phase": True}}

    wire = Wire()
    state = blindplay_read.settle(_chooser(True), wire, tries=3, delay=0)
    assert state["state_type"] == "monster"
    assert wire.reads == 1


def test_the_bridge_says_whether_the_chooser_took_its_pick():
    from pathlib import Path
    repo = Path(__file__).resolve().parents[2]
    bridge = repo / "vendor" / "STS2_MCP"
    helper = (bridge / "gits" / "GitsChooserAnswered.cs").read_text(
        encoding="utf-8")
    assert '"_screenComplete"' in helper
    state = (bridge / "McpMod.StateBuilder.cs").read_text(encoding="utf-8")
    assert 'state["answered"] = answered' in state
    actions = (bridge / "McpMod.Actions.cs").read_text(encoding="utf-8")
    # A press on an answered chooser is refused, and a press the screen
    # ignored (it drops picks in its first 350 ms) says nothing was chosen.
    assert "GitsChooserAnswered(chooseScreen) == true" in actions
    assert "GitsChooserAnswered(chooseScreen) == false" in actions
