"""Furina's infinite-loop probe (`tier0/harness/furina_loop_probe.py`) on the
Salon's Tab slice (2026-10-05).

The 2026-10-04 loop audit fixed Interval Bell's Spend mode to give its Energy
NEXT turn. The probe must still see what that fix closed with the fix taken
out (`pre_fix=True`): today, Interval Bell, Salon's Tab+ and Surging Waters
paid for each other (Bell's Energy bought Surging Waters, whose Repay reopened
the Drain room Salon's Tab spends).

The post-fix sweep's productive loops are pinned by name (`KNOWN_OPEN`):
reported to the main session, not fixed here (cards are not changed to fix a
loop), so a new one fails this file and a fix moves the pin. Every one is an
upgraded Guest Star (cost 0) cycled by two Salon's Tab+ (0: draw 2): a guest
summoned while on stage acts and stays, so it acts forever.
"""

from __future__ import annotations

import copy

import pytest

from tier0.engine import combat
from tier0.engine import furina_stage as FS
from tier0.harness import furina_loop_probe as P

BELL_TAB_WATERS = ("proto_fs_interval_bell", "proto_fs_salons_tab+",
                   "proto_fs_surging_waters")


def _try(combo, pre_fix, power=None):
    return P.try_combo(P.variants(pre_fix), tuple(sorted(combo)), power)


def test_pre_fix_bell_tab_and_surging_waters_loop():
    hit = _try(BELL_TAB_WATERS, pre_fix=True)
    assert hit is not None and hit.productive
    assert hit.growth["fanfare"] > 0


def test_with_the_fix_bell_tab_and_surging_waters_do_not_loop():
    hit = _try(BELL_TAB_WATERS, pre_fix=False)
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
    # Salon's Tab x2 drains to the line and no further: 78 -> 42 (nine
    # Drains of 4), then it only draws.
    st = P._state((), {}, 0, take=True)
    pool = P.variants(False)
    st.player.hand = [copy.deepcopy(pool["proto_fs_salons_tab"])
                      for _ in range(2)]
    for _ in range(60):
        options = [c for c in st.player.hand if combat.card_playable(st, c)]
        combat.play_card(st, options[0])
    assert st.player.hp == 42
    assert st.player.ftd.drained == 36


@pytest.mark.parametrize("combo,pre_fix", [
    (BELL_TAB_WATERS, True),
    (("proto_fs_guest_star_charlotte+", "proto_fs_salons_tab+"), False),
    (("proto_fs_interval_bell",), False)])
def test_the_screen_passes_every_loop_found(combo, pre_fix):
    pool = P.variants(pre_fix)
    assert P.could_cycle([P.profile(pool[c]) for c in combo], {})


#: Inert cycles: 0-cost card draw that refills the hand and, once the Drain
#: line is reached, grows nothing.
KNOWN_INERT = {
    ("proto_fs_interval_bell",), ("proto_fs_interval_bell+",),
    ("proto_fs_salons_tab",), ("proto_fs_salons_tab+",),
}

#: Two Salon's Tab+ (0: draw 2) carry an upgraded Guest Star (0) forever: a
#: second summon of a seated guest makes it act and stay.
TAB_UP = "proto_fs_salons_tab+"
GUESTS_UP = {"proto_fs_guest_star_" + g + "+" for g in FS.GUESTS}
KNOWN_OPEN = {tuple(sorted((g, TAB_UP))) for g in GUESTS_UP}

#: Productive in the probe's 60-play window and bounded past it: the Drain
#: line ends the Drains (or the Fanfare runs out). Reported, not open.
KNOWN_BOUNDED = {
    ("proto_fs_salons_tab+", "proto_fs_soloists_solicitation"),
    ("proto_fs_salons_tab+", "proto_fs_soloists_solicitation+"),
    ("proto_fs_interval_bell", "proto_fs_quick_cue", "proto_fs_salons_tab+"),
    ("proto_fs_interval_bell", "proto_fs_quick_cue+", "proto_fs_salons_tab+"),
    ("proto_fs_interval_bell+", "proto_fs_quick_cue", "proto_fs_salons_tab+"),
    ("proto_fs_interval_bell+", "proto_fs_quick_cue+", "proto_fs_salons_tab+"),
}


@pytest.mark.battery
def test_the_post_fix_sweep_finds_only_the_known_cycles():
    found = P.search_env(False, None)
    productive = {f.cards for f in found if f.productive}
    inert = {f.cards for f in found if not f.productive}
    assert productive == KNOWN_OPEN | KNOWN_BOUNDED
    assert inert == KNOWN_INERT


@pytest.mark.battery
@pytest.mark.parametrize("combo", sorted(KNOWN_OPEN))
def test_the_open_loops_are_unbounded(combo):
    pool = P.variants(False)
    cards = [pool[c] for c in combo] + [pool[TAB_UP]]
    for order in ((combo[0], combo[1]), (combo[1], combo[0])):
        run = P.play_out(cards, list(order), take=True, plays=600)
        if run.productive:
            return
    pytest.fail(f"{combo} stopped growing within 600 plays")


@pytest.mark.battery
@pytest.mark.parametrize("combo", sorted(KNOWN_BOUNDED))
def test_the_bounded_loops_stop_growing(combo):
    import itertools
    pool = P.variants(False)
    for copies in itertools.product((1, 2), repeat=len(combo)):
        cards = [pool[c] for c, n in zip(combo, copies) for _ in range(n)]
        for order in itertools.permutations(combo):
            for take in (True, False):
                run = P.play_out(cards, list(order), take=take, plays=600)
                assert not run.productive, (combo, copies, order, take)
