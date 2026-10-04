"""THE FURINA RESEARCH SLICE (`tier0/engine/furina_tide.py`): the K3 switches.

`review/active/furina-research-proposal-2026-10-05.md` sec.10, K3. A Drain the
Singer fully repays costs no HP and prints Fanfare twice; the probe variants
in `furina_tide.VARIANT_SWITCHES` price it. One pin per switch, plus the
default (`entry`), which must stay the paper's rules, and the pilot's reading
of each switch. NOTHING MEASURED HERE IS QUOTABLE.
"""

from __future__ import annotations

import random

from tier0.engine import furina_tide as T
from tier0.engine.state import CombatState, Enemy
from tier0.pilot import furina_tide_pilot as P


def _state(variant=T.DEFAULT_VARIANT, hp=78, enemy_hp=200):
    p = T.build_player([], variant=variant)
    p.hp = hp
    st = CombatState(player=p,
                     enemies=[Enemy(hp=enemy_hp, max_hp=enemy_hp,
                                    name="paper",
                                    intents=[{"kind": "block",
                                              "amount": 0}])],
                     rng=random.Random(0))
    st.turn = 1
    T.turn_open(st)
    return st


def _drain_then_end_turn(st, n=3):
    assert T.drain(st, n)
    T.end_of_turn(st)


def test_default_is_the_papers_rules_all_switches_off():
    st = _state()
    f = st.player.ftd
    assert (f.singer, f.singer_rests, f.restore_fanfare) == (2, False, True)
    _drain_then_end_turn(st, 3)
    # Drain 3 printed 3; the Singer Restored 2 and printed 2 more.
    assert st.player.hp == 78 - 3 + 2
    assert f.drained == 1 and f.fanfare == 5
    assert f.ledger["gained_by"] == {"drain": 3, "restore": 2}


def test_singer_rests_skips_the_singer_on_a_turn_she_drained():
    st = _state("singer_rests")
    f = st.player.ftd
    _drain_then_end_turn(st, 3)
    assert st.player.hp == 75 and f.drained == 3
    assert f.ledger["restored"] == 0 and f.ledger["singer_skipped"] == 1
    # The next turn has no Drain: the Singer Restores 2.
    st.turn = 2
    T.turn_open(st)
    T.end_of_turn(st)
    assert st.player.hp == 77 and f.drained == 1
    assert f.ledger["gained_by"]["restore"] == 2


def test_singer_rests_counts_neuvillettes_drain():
    st = _state("singer_rests")
    st.player.ftd.stage = ["neuvillette"]
    T.end_of_turn(st)
    f = st.player.ftd
    assert f.ledger["drains"] == 1 and f.ledger["restored"] == 0
    assert f.ledger["singer_skipped"] == 1


def test_restore_no_fanfare_restores_hp_but_prints_nothing():
    st = _state("restore_no_fanfare")
    f = st.player.ftd
    _drain_then_end_turn(st, 3)
    assert st.player.hp == 77 and f.ledger["restored"] == 2
    assert f.fanfare == 3                      # the Drain's 3 only
    assert "restore" not in f.ledger["gained_by"]
    # An enemy hit still prints Fanfare.
    T.on_hp_loss(st, 4)
    assert f.ledger["gained_by"]["hit"] == 4


def test_both_switches_together():
    st = _state("both")
    f = st.player.ftd
    assert f.singer_rests and not f.restore_fanfare
    _drain_then_end_turn(st, 3)
    assert f.ledger["restored"] == 0 and f.fanfare == 3
    st.turn = 2
    T.turn_open(st)
    T.end_of_turn(st)
    assert f.ledger["restored"] == 2 and f.fanfare == 3


def test_singer1_restores_one():
    st = _state("singer1")
    f = st.player.ftd
    assert f.singer == 1 and f.line_from_entry
    _drain_then_end_turn(st, 3)
    assert st.player.hp == 76 and f.drained == 2 and f.fanfare == 4


def test_the_switches_keep_the_entry_line():
    for v in T.VARIANT_SWITCHES:
        p = T.build_player([], hp=60, variant=v)
        assert p.ftd.line_from_entry and p.ftd.entry_hp == 60
        assert T.half_line(p) == 30


def test_pilot_charges_the_forfeited_singer_only_on_the_first_drain():
    st = _state("singer_rests", hp=70, enemy_hp=20)   # a short fight
    st.player.ftd.drained = 8
    first = P.forfeit_cost(st, 3)
    assert first > 0
    assert P.drain_cost(st, 3) > P.drain_cost(_twin(st, "entry"), 3)
    T.drain(st, 3)                       # this turn's Singer is now gone
    assert P.forfeit_cost(st, 3) == 0.0
    # Off the switch the term is always zero.
    assert P.forfeit_cost(_twin(st, "entry"), 3) == 0.0


def test_pilot_values_restore_without_fanfare_under_the_switch():
    on = _state(hp=70)
    off = _state("restore_no_fanfare", hp=70)
    on.player.ftd.drained = off.player.ftd.drained = 5
    assert P.restore_value(off, 3) == 3 * P.hp_value(off)
    assert P.restore_value(on, 3) > P.restore_value(off, 3)


def test_take_rate_counts_card_drains_only():
    # Neuvillette's act is a Drain but never an offer, so it stays out of
    # the card count the probe's take rate reads.
    st = _state()
    st.player.ftd.stage = ["neuvillette"]
    T.end_of_turn(st)
    assert st.player.ftd.ledger["drains"] == 1
    assert st.player.ftd.ledger["card_drains"] == 0


def _twin(st, variant):
    tw = _state(variant, hp=st.player.hp, enemy_hp=st.enemies[0].hp)
    tw.player.ftd.drained = st.player.ftd.drained
    return tw
