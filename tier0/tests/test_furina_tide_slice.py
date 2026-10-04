"""THE FURINA RESEARCH SLICE (`tier0/engine/furina_tide.py`).

`review/active/furina-research-proposal-2026-10-05.md` sec.10, sec.15 and
sec.16. Pins: the default rules (the curtain call), the old rule kept as
`no_curtain_call`, Rising Applause always spending, the fixed-price cards,
the Drain-and-Repay readers, the new rows, the K3 switches, and the pilot's
reading of each. NOTHING MEASURED HERE IS QUOTABLE.
"""

from __future__ import annotations

import random

from tier0.engine import furina_tide as T
from tier0.engine.state import CombatState, Enemy
from tier0.harness import furina_tide_probe as probe
from tier0.pilot import furina_tide_pilot as P


def _state(variant=T.DEFAULT_VARIANT, hp=78, enemy_hp=200, enemies=1):
    p = T.build_player([], variant=variant)
    p.hp = hp
    st = CombatState(player=p,
                     enemies=[Enemy(hp=enemy_hp, max_hp=enemy_hp,
                                    name="paper",
                                    intents=[{"kind": "block",
                                              "amount": 0}])
                              for _ in range(enemies)],
                     rng=random.Random(0))
    st.turn = 1
    st.current_attack_bonus = 0      # set per play by the engine's play loop
    T.turn_open(st)
    return st


def _drain_then_end_turn(st, n=3):
    assert T.drain(st, n)
    T.end_of_turn(st)


def _play(st, card_id):
    T.resolve_card(st, T.make_card(card_id))


class _Says:
    """A decider that answers every in-card choice the same way."""

    def __init__(self, yes):
        self.yes = yes

    def drain(self, *_):
        return self.yes

    def spend(self, *_):
        return self.yes

    def spend_all(self, *_):
        return self.yes


# ----------------------------------------------------------------------
# The rules.
# ----------------------------------------------------------------------
def test_default_is_the_curtain_call_with_all_switches_off():
    st = _state()
    f = st.player.ftd
    assert T.DEFAULT_VARIANT == "curtain_call"
    assert f.curtain_call and f.line_from_entry and not f.rising_optional
    assert (f.singer, f.singer_rests, f.repay_fanfare) == (2, False, True)
    _drain_then_end_turn(st, 3)
    # Drain 3 printed 3; the Singer Repaid 2 and printed 2 more.
    assert st.player.hp == 78 - 3 + 2
    assert f.drained == 1 and f.fanfare == 5
    assert f.ledger["gained_by"] == {"drain": 3, "repay": 2}


def test_curtain_call_returns_all_drained_hp_at_the_end():
    st = _state(hp=70)
    assert T.drain(st, 5)
    T.close_ledger(st)
    f = st.player.ftd
    assert f.ledger["unrepaid_end"] == 5          # recorded before the return
    assert f.ledger["curtain_repaid"] == 5
    assert st.player.hp == 70 and f.drained == 0


def test_no_curtain_call_keeps_the_old_rule():
    st = _state("no_curtain_call", hp=70)
    assert not st.player.ftd.curtain_call
    assert T.drain(st, 5)
    T.close_ledger(st)
    assert st.player.hp == 65
    assert st.player.ftd.ledger["unrepaid_end"] == 5
    assert st.player.ftd.ledger["curtain_repaid"] == 0


def test_rising_applause_always_spends_all():
    for variant in ("curtain_call", "no_curtain_call"):
        st = _state(variant)
        st.player.ftd.fanfare = 7
        st.player.ftd.decider = _Says(False)        # it is not asked
        _play(st, "ftd_rising_applause")
        assert st.player.ftd.fanfare == 0
        assert st.enemies[0].hp == 200 - 7
        assert st.player.block == 5


def test_legacy_lets_the_pilot_skip_rising_applause():
    st = _state("legacy")
    st.player.ftd.fanfare = 7
    st.player.ftd.decider = _Says(False)
    _play(st, "ftd_rising_applause")
    assert st.player.ftd.fanfare == 7 and st.enemies[0].hp == 200


def test_fixed_price_cards_are_unplayable_when_the_price_cannot_be_paid():
    st = _state(hp=78)
    crab = T.make_card("ftd_crabaletta")
    quick = T.make_card("ftd_quick_flourish")
    assert T.playable(st, crab) and not T.playable(st, quick)
    st.player.hp = 42                           # line 39: 42 - 5 < 39
    assert not T.playable(st, crab)
    st.player.ftd.fanfare = 4
    assert T.playable(st, quick)
    _play(st, "ftd_quick_flourish")
    assert st.player.ftd.fanfare == 0 and st.enemies[0].hp == 200 - 11


def test_crabaletta_drains_five_and_deals_24():
    st = _state()
    _play(st, "ftd_crabaletta")
    f = st.player.ftd
    assert st.player.hp == 73 and f.drained == 5
    assert st.enemies[0].hp == 200 - 24
    assert f.ledger["fixed_drains"] == 1 and f.ledger["card_drains"] == 0


def test_revelry_multiplies_every_gain_and_critics_darling_reads_drain_and_repay():
    # sec.17: "You gain twice as much Fanfare." Hits count; two copies make
    # it three times. Critics' Darling (probe-only) still reads only a Drain
    # or a Repay.
    st = _state(hp=70)
    f = st.player.ftd
    f.powers["revelry"] = 2                     # two copies: x3
    f.powers["critics_darling"] = 1
    T.on_hp_loss(st, 6)
    assert f.fanfare == 18 and st.enemies[0].hp == 200
    T.drain(st, 3)
    assert f.fanfare == 18 + 9
    assert st.enemies[0].hp == 197
    T.repay(st, 2)
    assert f.fanfare == 27 + 6
    assert st.enemies[0].hp == 195


def test_thunderous_applause_hits_all_once_per_spend():
    st = _state(enemies=2)
    f = st.player.ftd
    f.powers["thunderous"] = 1
    f.fanfare = 9
    _play(st, "ftd_bravura")                     # a spend-all is one Spend
    assert f.ledger["spends"] == 1
    hp = sorted(e.hp for e in st.enemies)
    assert hp[1] == 200 - 3                      # the untargeted one: 3


def test_salons_tab_energy_arrives_next_turn():
    st = _state()
    st.player.ftd.decider = _Says(True)
    st.player.energy = 2
    _play(st, "ftd_salons_tab")
    assert st.player.hp == 74 and st.player.energy == 2
    assert T.energy_kept(st) == 1 and T.energy_kept(st) == 0


def test_neuvillette_deals_the_hp_drained_this_turn_and_drains_nothing():
    st = _state(enemies=2)
    f = st.player.ftd
    f.stage = ["neuvillette"]
    T.drain(st, 3)
    T.drain(st, 2)
    T.act(st, "neuvillette")
    assert f.ledger["drains"] == 2 and st.player.hp == 73
    assert all(e.hp == 200 - 5 - T.NEUVILLETTE_HYDRO_BONUS
               for e in st.enemies)
    st2 = _state()
    st2.player.ftd.stage = ["neuvillette"]
    T.end_of_turn(st2)
    assert st2.player.ftd.ledger["drains"] == 0 and st2.enemies[0].hp == 200


def test_lynettes_line_pays_the_first_hit_again():
    st = _state()
    f = st.player.ftd
    f.stage = ["lynette"]
    T.on_hp_loss(st, 4)
    T.on_hp_loss(st, 3)
    assert f.ledger["gained_by"] == {"hit": 7, "lynette": 4}


def test_singer_of_many_waters_repays_everything_and_exhausts():
    st = _state(hp=70)
    st.player.ftd.drained = 8
    assert T.make_card("ftd_singer").exhaust
    _play(st, "ftd_singer")
    assert st.player.hp == 78 and st.player.ftd.drained == 0


def test_the_draft_pool_is_the_slices_24():
    pool = [c for r in probe.DRAFT_POOL.values() for c in r]
    assert len(pool) == 24 and len(set(pool)) == 24
    assert "ftd_sigewinne" not in pool and "ftd_crowd_gasps" not in pool


# ----------------------------------------------------------------------
# The K3 switches (under the old end-of-fight rule).
# ----------------------------------------------------------------------
def test_singer_rests_skips_the_singer_on_a_turn_she_drained():
    st = _state("singer_rests")
    f = st.player.ftd
    _drain_then_end_turn(st, 3)
    assert st.player.hp == 75 and f.drained == 3
    assert f.ledger["repaid"] == 0 and f.ledger["singer_skipped"] == 1
    st.turn = 2
    T.turn_open(st)
    T.end_of_turn(st)
    assert st.player.hp == 77 and f.drained == 1
    assert f.ledger["gained_by"]["repay"] == 2


def test_repay_no_fanfare_repays_hp_but_prints_nothing():
    st = _state("repay_no_fanfare")
    f = st.player.ftd
    _drain_then_end_turn(st, 3)
    assert st.player.hp == 77 and f.ledger["repaid"] == 2
    assert f.fanfare == 3                      # the Drain's 3 only
    assert "repay" not in f.ledger["gained_by"]
    T.on_hp_loss(st, 4)
    assert f.ledger["gained_by"]["hit"] == 4


def test_both_switches_together():
    st = _state("both")
    f = st.player.ftd
    assert f.singer_rests and not f.repay_fanfare
    _drain_then_end_turn(st, 3)
    assert f.ledger["repaid"] == 0 and f.fanfare == 3
    st.turn = 2
    T.turn_open(st)
    T.end_of_turn(st)
    assert f.ledger["repaid"] == 2 and f.fanfare == 3


def test_singer1_repays_one():
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
        assert p.ftd.curtain_call == (v == "curtain_call")


# ----------------------------------------------------------------------
# The pilot.
# ----------------------------------------------------------------------
def test_pilot_curtain_call_drain_has_no_permanent_cost():
    cur = _state(hp=70, enemy_hp=20)
    old = _state("no_curtain_call", hp=70, enemy_hp=20)
    cur.player.ftd.drained = old.player.ftd.drained = 8
    assert P.unrepaid_share(cur, 5) == 0.0
    assert P.unrepaid_share(old, 5) > 0.0
    assert P.drain_cost(cur, 5) < P.drain_cost(old, 5)
    # On the killing play nothing is charged: the net is the gain alone.
    assert P.drain_cost(cur, 5, kills=True) == -(
        P._loop_gain_value(cur, 5) + P._drain_triggers(cur, 5))
    assert P.drain_cost(old, 5, kills=True) > P.drain_cost(cur, 5, kills=True)


def test_pilot_values_rising_applause_spend_whether_or_not_it_pays():
    st = _state()
    st.player.ftd.fanfare = 10
    card = T.make_card("ftd_rising_applause")
    v = P.value(st, card, [card], P.DECIDERS["never"])
    assert v == (P._block_value(5, P.need(st))
                 + P._single(st, 10) - P.spend_cost(st, 10))


def test_never_pilot_never_plays_a_fixed_drain_card():
    st = _state()
    crab = T.make_card("ftd_crabaletta")
    assert P.allowed(st, crab, P.DECIDERS["judged"])
    assert not P.allowed(st, crab, P.DECIDERS["never"])
    st.player.hp = 42
    assert not P.allowed(st, crab, P.DECIDERS["always"])


def test_pilot_charges_the_forfeited_singer_only_on_the_first_drain():
    st = _state("singer_rests", hp=70, enemy_hp=20)   # a short fight
    st.player.ftd.drained = 8
    first = P.forfeit_cost(st, 3)
    assert first > 0
    assert P.drain_cost(st, 3) > P.drain_cost(_twin(st, "entry"), 3)
    T.drain(st, 3)                       # this turn's Singer is now gone
    assert P.forfeit_cost(st, 3) == 0.0
    assert P.forfeit_cost(_twin(st, "entry"), 3) == 0.0


def test_pilot_values_repay_without_fanfare_under_the_switch():
    on = _state("no_curtain_call", hp=70)
    off = _state("repay_no_fanfare", hp=70)
    on.player.ftd.drained = off.player.ftd.drained = 5
    assert P.repay_value(off, 3) == 3 * P.hp_value(off)
    assert P.repay_value(on, 3) > P.repay_value(off, 3)


def test_take_rate_counts_modal_card_drains_only():
    st = _state()
    st.player.ftd.decider = _Says(True)
    _play(st, "ftd_crabaletta")
    _play(st, "ftd_curtain_rise")
    L = st.player.ftd.ledger
    assert L["drains"] == 2 and L["card_drains"] == 1
    assert L["fixed_drains"] == 1 and L["drain_offers"] == 1


def _twin(st, variant):
    tw = _state(variant, hp=st.player.hp, enemy_hp=st.enemies[0].hp)
    tw.player.ftd.drained = st.player.ftd.drained
    return tw
