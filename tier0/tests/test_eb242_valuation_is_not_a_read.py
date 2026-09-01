"""EB-242: the pilot's estimates are not reads.

THE DEFECT. `resources.note_charge_read` has always DECLARED the two pilot
valuation sites out of scope -- its own docstring says so, and §2 of
`review/records/charge-reads-per-turn-registration-2026-08-13.md` says
deliberation is deliberately NOT counted. The code did not implement the
declaration: `_bonus_formula`'s `N_per_M_charge` branch ticked the instrument
on every call, and `policy._expected_damage` and `policy._raw_block` call that
helper on purpose, so that the pilot's price for a card cannot drift from what
resolving it pays. The result was an instrument reporting the pilot's
deliberation as if it were the player's turn: `X9READ-S1` pooled 13,198
`bonus_formula` reads of which 9,893 (74.96%) were nobody's turn at all.

WHAT THE FIX IS, AND WHAT IT DELIBERATELY IS NOT. The tick moved behind the
call's own declaration of what it is: `_bonus_formula(..., valuation=True)` is
an estimate and tallies nothing, and every other caller -- the two engine
resolve sites and the direct probes in the suite -- is a resolution and tallies
exactly what it always did. What a RESOLVED play tallies is untouched, which
is the half of this that would have been easy to break: the point of the
instrument is the double read a card that prints its own rider AND collects the
Garment's takes, and a fix that muted one leg of that would be a second defect
wearing the first one's clothes.
"""

import random

import pytest

from tier0.content import loader
from tier0.engine import effects, resources
from tier0.engine.state import Card, CombatState
from tier0.pilot import policy
from tier0.tests.conftest import make_enemy


CHARGE_RIDER = {"op": "damage", "amount": 5, "target": "enemy",
                "bonus_formula": "1_per_2_charge"}
BLOCK_RIDER = {"op": "block", "amount": 6, "bonus_formula": "1_per_2_charge"}


def _state(charge: int = 8) -> CombatState:
    st = CombatState(player=loader.build_player("kokomi"),
                     enemies=[make_enemy(hp=300)], rng=random.Random(0))
    st.player.charge = charge
    return st


def _card(**kw) -> Card:
    d = dict(id="eb242_probe", name="probe", cost=1, type="attack",
             character="kokomi", rarity="common")
    d.update(kw)
    return Card(**d)


def test_the_pilots_damage_estimate_tallies_no_read():
    """`policy._expected_damage` prices the rider through the engine's own
    helper -- that shared helper is why the pilot's price cannot drift from
    what resolves -- and pricing a card is not playing it."""
    st = _state()
    card = _card(effects=[CHARGE_RIDER])
    assert policy._expected_damage(st, card) > 5      # the rider IS read
    assert st.charge_reads_this_turn == {}
    assert [ev for ev in st.log if ev["event"] == "charge_read"] == []


def test_the_pilots_block_estimate_tallies_no_read():
    """The second site, `policy._raw_block`. Same rider grammar, same
    reason, and it was tallying too."""
    st = _state()
    card = _card(type="skill", effects=[BLOCK_RIDER])
    assert policy._raw_block(st, card) > 6
    assert st.charge_reads_this_turn == {}


def test_a_whole_pilot_turn_of_deliberation_tallies_nothing():
    """The shape the instrument actually saw. A pilot scores every card in
    hand every play, so one turn's deliberation over a hand of readers was
    tens of reads against a turn in which the player played none."""
    st = _state()
    hand = [_card(id=f"eb242_probe_{i}", effects=[CHARGE_RIDER])
            for i in range(4)]
    st.player.hand = list(hand)
    st.player.energy = 3
    pilot = policy.make_pilot(loader.pilot_weights("priest"))
    assert pilot(st) is not None, "a hand of playable readers must be scored"
    assert st.charge_reads_this_turn == {}


def test_what_a_resolved_play_tallies_is_untouched():
    """The other direction, and the one a careless fix breaks: resolving a
    card that prints the rider still tallies exactly one `bonus_formula`
    read, tagged with the card that read it."""
    st = _state()
    card = _card(effects=[CHARGE_RIDER])
    effects.resolve_card(st, card)
    assert st.charge_reads_this_turn == {"bonus_formula": 1}
    ev = next(e for e in st.log if e["event"] == "charge_read")
    assert ev["kind"] == "bonus_formula" and ev["card"] == "eb242_probe"


def test_the_direct_probe_of_the_primitive_is_still_a_read():
    """A caller that says nothing is a resolution, because every caller in
    the engine is one. The exemption is DECLARED by the estimate, which is
    what keeps a new resolve path from silently opting out of the tally."""
    st = _state()
    assert effects._bonus_formula(st, "1_per_2_charge") == 4
    assert st.charge_reads_this_turn == {"bonus_formula": 1}
    assert effects._bonus_formula(st, "1_per_2_charge", valuation=True) == 4
    assert st.charge_reads_this_turn == {"bonus_formula": 1}


def test_the_fanfare_leg_of_the_same_helper_is_not_in_scope():
    """EB-242 is the CHARGE instrument. `note_fanfare_read` is a different
    instrument with a different registration, and a fix that quietly retuned
    it would be an undeclared change to a published measurement's source."""
    st = CombatState(player=loader.build_player("furina"),
                     enemies=[make_enemy(hp=300)], rng=random.Random(0))
    st.player.fanfare = st.player.fanfare_cap
    st.log.clear()
    effects._bonus_formula(st, "1_per_2_fanfare", valuation=True)
    assert [ev["event"] for ev in st.log] == ["fanfare_read"]
