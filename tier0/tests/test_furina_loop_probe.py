"""Furina's infinite-loop probe (`tier0/harness/furina_loop_probe.py`) on the
Salon's Tab slice (2026-10-05).

The 2026-10-04 loop audit fixed Interval Bell's Spend mode to give its Energy
NEXT turn. The probe must still see what that fix closed with the fix taken
out (`pre_fix=True`): Interval Bell, Pneuma Refrain and Soloist's
Solicitation pay for each other when Bell's Energy comes at once.

The post-fix sweep finds no productive loop. Until 2026-10-05 it found one
per guest: an upgraded Guest Star (cost 0) cycled by two Salon's Tab+ (then
0: draw 2) acted forever, because a guest summoned while on stage acts and
stays. The main session's ruling made the Tab cost 1 (Draw 2 [3]; Drain 4:
also gain 2 Energy next turn), so every cycle through it is paid for out of
this turn's Energy; the pins below hold that.
"""

from __future__ import annotations

import copy

import pytest

from tier0.engine import combat
from tier0.engine import furina_stage as FS
from tier0.harness import furina_loop_probe as P

#: The loop the Bell fix closed, as the current pool spells it.
PRE_FIX_LOOP = ("proto_fs_interval_bell", "proto_fs_pneuma_refrain",
                "proto_fs_soloists_solicitation")


def _try(combo, pre_fix, power=None):
    return P.try_combo(P.variants(pre_fix), tuple(sorted(combo)), power)


def test_pre_fix_bell_pneuma_and_solicitation_loop():
    hit = _try(PRE_FIX_LOOP, pre_fix=True)
    assert hit is not None and hit.productive
    assert hit.growth["fanfare"] > 0


def test_with_the_fix_bell_pneuma_and_solicitation_do_not_loop():
    hit = _try(PRE_FIX_LOOP, pre_fix=False)
    assert hit is None or not hit.productive


def test_interval_bells_energy_is_owed_not_paid():
    st = P._state((), {}, 0, take=True)
    pool = P.variants(False)
    st.player.hand = [copy.deepcopy(pool["proto_fs_interval_bell+"])]
    st.player.discard_pile = [copy.deepcopy(pool["proto_fs_soloists_solicitation"])]
    combat.play_card(st, st.player.hand[0])
    assert st.player.energy == P.START_ENERGY
    assert st.player.ftd.energy_next == 1
    assert st.player.ftd.fanfare == P.START_FANFARE - 2


def test_the_body_is_real_so_the_drain_room_bounds_a_drain_loop():
    # Salon's Tab x2, with Energy to spare, drains to the line and no
    # further: 78 -> 42 (nine Drains of 4), then it only draws.
    st = P._state((), {}, 0, take=True)
    st.player.energy = 60
    pool = P.variants(False)
    st.player.hand = [copy.deepcopy(pool["proto_fs_salons_tab"])
                      for _ in range(2)]
    for _ in range(60):
        options = [c for c in st.player.hand if combat.card_playable(st, c)]
        combat.play_card(st, options[0])
    assert st.player.hp == 42
    assert st.player.ftd.drained == 36


def test_the_tab_costs_energy_so_a_guest_and_two_tabs_stop():
    """The 2026-10-05 ruling: a 1-cost Tab ends the Guest+ / Tab+ cycle when
    the turn's Energy runs out."""
    pool = P.variants(False)
    for g in FS.GUESTS:
        guest = f"proto_fs_guest_star_{g}+"
        cards = [pool[guest], pool[TAB_UP], pool[TAB_UP]]
        for order in ((guest, TAB_UP), (TAB_UP, guest)):
            run = P.play_out(cards, list(order), take=True, plays=600)
            assert not run.productive, (g, order)
            assert run.plays < 600, (g, order)


@pytest.mark.parametrize("combo,pre_fix", [
    (PRE_FIX_LOOP, True),
    (("proto_fs_interval_bell",), False)])
def test_the_screen_passes_every_loop_found(combo, pre_fix):
    pool = P.variants(pre_fix)
    assert P.could_cycle([P.profile(pool[c]) for c in combo], {})


#: Inert cycles: 0-cost card draw that refills the hand and grows nothing.
#: The pool to 75 adds Soothing Waters (0: Repay 2, draw 1) to them.
KNOWN_INERT = {("proto_fs_interval_bell",), ("proto_fs_interval_bell+",),
               ("proto_fs_soothing_waters",), ("proto_fs_soothing_waters+",)}

#: THE POOL TO 75 (2026-10-09). The ruled batch, built as written, gave the
#: sweep 81 productive cycles over 16 thin-deck card sets, every set but one
#: holding Overdraft (0: Drain 4, gain 1 Energy) or Sold Out's Energy. The
#: main session's ruling gave both their Energy next turn (Interval Bell's
#: fix, 2026-10-04), and the sweep is clean again.


def _base_set(cards) -> frozenset:
    return frozenset(c.rstrip(P.UP) for c in cards)

TAB_UP = "proto_fs_salons_tab+"


@pytest.mark.battery
def test_the_post_fix_sweep_finds_no_productive_cycle():
    found = P.search_env(False, None)
    assert {_base_set(f.cards) for f in found if f.productive} == set()
    assert {f.cards for f in found if not f.productive} == KNOWN_INERT


def test_overdraft_and_pneuma_refrain_no_longer_cycle():
    """The smallest of the pool to 75's findings before the 2026-10-09
    ruling: Overdraft (Drain 4, then +1 Energy NOW) and two Pneuma Refrains
    (Repay 5, draw 2) looped with her HP flat. With the Energy owed next
    turn the turn's Energy runs out."""
    pool = P.variants(False)
    cards = [pool["proto_fs_overdraft"], pool["proto_fs_pneuma_refrain"],
             pool["proto_fs_pneuma_refrain"]]
    run = P.play_out(cards, ["proto_fs_overdraft", "proto_fs_pneuma_refrain"],
                     take=True, plays=200)
    assert not run.productive and run.plays < 200
