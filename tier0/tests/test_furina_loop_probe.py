"""Furina's infinite-loop probe (`tier0/harness/furina_loop_probe.py`) on the
Salon's Tab slice (2026-10-05).

The 2026-10-04 loop audit fixed Interval Bell's Spend mode to give its Energy
NEXT turn; the sweep (2026-10-14) cut the Bell, so no pin on that fix is left.

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

#: The sweep (2026-10-14) cut Interval Bell, Soloist's Solicitation,
#: Soothing Waters and Overdraft, and with them the pins on the Bell fix and
#: on the pool to 75's Overdraft finding: no card is left to show either.


def test_the_body_is_real_so_her_hp_bounds_a_drain_loop():
    # Salon's Tab x2, with Energy to spare. Since the Drain line rule
    # (2026-10-09) a Drain may go past the line (59 from 78), never to 0 HP:
    # 78 -> 2 (nineteen Drains of 4), then it only draws. 19 of the 76
    # drained HP was taken at or above the line (78 down to 59), the other
    # 57 past it.
    st = P._state((), {}, 0, take=True)
    st.player.energy = 60
    pool = P.variants(False)
    st.player.hand = [copy.deepcopy(pool["proto_fs_salons_tab"])
                      for _ in range(2)]
    for _ in range(60):
        options = [c for c in st.player.hand if combat.card_playable(st, c)]
        combat.play_card(st, options[0])
    assert st.player.hp == 2
    assert st.player.ftd.drained == 76
    assert st.player.ftd.drained_above == 19
    assert st.player.ftd.drained_past == 57


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


#: Inert cycles: 0-cost card draw that refills the hand and grows nothing.
#: The pool to 75 adds Soothing Waters (0: Repay 2, draw 1) to them. The
#: Repay floor as first built gave it Vigor on an empty Repay, which made it
#: grow without end; the main session's ruling (2026-10-09) took its floor
#: off, and it is inert again.
#: Tutti!+ (0: each guest acts, draw 1) alone cycles inert too. The sweep
#: (2026-10-14) cut Interval Bell and Soothing Waters.
KNOWN_INERT = {("proto_fs_tutti+",)}

#: ACCEPTED LOOPS: productive cycles the sweep finds and [USER] has accepted,
#: by base card set, each with its reason. A productive cycle not listed here
#: fails the sweep.
#:
#: THE DIVERSITY PASS (2026-10-11). Tutti!+ costs 0 and draws 1, so with any
#: 0-cost draw-1 card (Interval Bell, Soothing Waters) and nothing
#: else in the deck, every guest acts forever. [USER]: "Theoretical infinite
#: loops in thin decks aren't automatically a problem - it's a problem if
#: they are tirivial to assemble and execute". This one needs a deck thinned
#: to those two cards, so it is not trivial, and the paper's 0-cost upgrade
#: stands. (Encore! left this list on 2026-10-12: it no longer draws.)
_TUTTI_THIN_DECK = ("[USER], 2026-10-11: a theoretical loop in a thin deck "
                    "is not a problem unless trivial to assemble; this one "
                    "needs a deck thinned to Tutti!+ and the draw card")
#: THE SWEEP, SECOND SET (2026-10-14): The Show's Not Over+ without Exhaust
#: made 13 thin-deck loops with an HP-losing draw card; the design call kept
#: its Exhaust (the upgrade is 3 Energy instead), and none is left.
ACCEPTED_LOOPS: dict = {}

#: CLOSED LOOPS: found, then fixed by a design call, each with its reason.
#: The probe must no longer find them.
#: (Stand-In's, 2026-10-14, left with the first set's cards.)
CLOSED_LOOPS: dict = {}

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
    productive = {_base_set(f.cards) for f in found if f.productive}
    assert productive - set(ACCEPTED_LOOPS) == set(), "an unrecorded loop"
    assert productive == set(ACCEPTED_LOOPS), "an accepted loop is gone"
    assert {f.cards for f in found if not f.productive} == KNOWN_INERT


@pytest.mark.battery
@pytest.mark.parametrize("name", sorted(P.NAMED))
def test_no_named_combination_is_a_productive_loop(name):
    """The pool to 75's sec.6 combinations: none grows anything in its
    best single-turn run. (The six-turn runs are reported by `--named`, not
    pinned here.)"""
    row = P.named_report(name)
    if name in ACCEPTED_NAMED:
        # The accepted loop, and only through Tutti!+ (0 cost).
        assert row["single_turn"]["productive"], name
        assert "proto_fs_tutti+" in row["single_turn"]["cards"], name
        return
    assert not row["single_turn"]["productive"], name


#: Named combinations whose best run is an accepted loop. Since the diversity
#: pass (2026-10-11), two Tutti!+ (0: each guest acts, draw 1) with
#: Charlotte's draw on stage cycle in a deck thinned to them; the same
#: thin-deck loop as ACCEPTED_LOOPS, under the same ruling.
ACCEPTED_NAMED = {"tutti_showstopper_house": _TUTTI_THIN_DECK}
