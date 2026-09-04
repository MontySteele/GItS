"""THE FURINA REFRAME'S STARTER SEAM (QUARANTINED, `furina_reframe.
FURINA_REFRAME`) -- R254, round 4 pick 1, 2026-09-04.

[USER], ruling `review/ruled/furina-reframe-round-4-2026-09-04.md` sec.6:
"maybe a reader in the starter deck? I still want to leave it at just 2 'good'
cards, but they can be stronger." Her two kit starters stay two and ONE of them
reads Fanfare -- Aria of Recompense, under the arm only: "Gain 5 Encore. If you
have at least 6 Fanfare, gain 5 more." Both numbers are lifted rather than
picked (the 5 is Aria's own printed Encore, the 6 the bar the four rider copies
already carry), so nothing here is a number this engine decided.

The seam is `furina_reframe.STARTER_SUBS`, read by `loader._starter_ids` -- the
ONE function `build_player` (the tier-0 battery) and `starting_deck` (the tier
0.5 run) both go through, so the battery and the run cannot disagree about what
she opens with. Its C# twin is `FurinaReframeRoster.StarterAria`, wired into
`Furina.StartingDeck` beside Kokomi's slot eleven.

TWO FACTS, and they are the two the mod pins as well
(`klee-mod/KleeTests/Prototype/FurinaReframeStarterTests.cs`): the arm deals
the copy and the flag-off run deals the shipped card, and the copy pays 5 below
the bar and 10 at it. NOTHING MEASURED HERE IS QUOTABLE (R215 B) -- these are
shape and arithmetic assertions about a prototype row, not numbers about a
game.
"""

import random

import pytest

from tier0.content import loader
from tier0.engine import combat, furina_reframe as fr
from tier0.engine.state import CombatState
from tier0.tests.conftest import make_enemy

SHIPPED = "aria_of_recompense"
COPY = "proto_fr_aria_of_recompense"


@pytest.fixture
def reframe(monkeypatch):
    """The master flag on, with the id-resolving caches cleared on the way in
    and out -- `test_furina_reframe_pool.reframe`'s fixture, for its reasons.
    The starter is read through `loader.build_player`, which resolves ids off
    the same memoized index the pool seam does."""
    loader.reset_caches()
    monkeypatch.setattr(fr, "FURINA_REFRAME", True)
    yield
    loader.reset_caches()


def _state(fanfare: int = 0):
    """A Furina in combat with the meter pre-set and the cap open.

    The cap is opened explicitly because `fanfare_cap` gates every meter write
    -- a state built with cap 0 swallows the pre-set silently and the bar
    assertions below would pass for the wrong reason. That is
    `test_fanfare_compensation._furina_state`'s own warning, and it applies
    here for the same reason.
    """
    st = CombatState(player=loader.build_player("furina"),
                     enemies=[make_enemy(hp=300)], rng=random.Random(0))
    st.player.fanfare_cap = 30
    st.player.fanfare = fanfare
    st.player.encore = 0
    return st


def _play(st, card_id: str) -> None:
    card = loader.get_card(card_id)
    st.player.hand.append(card)
    st.player.energy = 3
    combat.play_card(st, card)


# --------------------------------------------------------------------------
# (1) WHICH CARD THE RUN IS DEALT.
# --------------------------------------------------------------------------

def test_the_arm_off_deals_the_shipped_aria_and_no_prototype():
    """The acceptance condition on the flag, pinned rather than intended: with
    the arm off `_starter_ids` returns the printed ten and nothing else."""
    loader.reset_caches()
    deck = loader.starting_deck("furina")
    assert SHIPPED in deck
    assert COPY not in deck


def test_the_arm_on_deals_the_copy_in_the_shipped_cards_slot(reframe):
    """ONE CARD FOR ONE CARD, which is what keeps this a substitution rather
    than a starter rework: the copy stands in the shipped card's own slot, the
    deck is still ten, and the other nine ids do not move.

    The flag-off order is read off the character sheet's `starting_deck:`,
    which is flag-blind, rather than by flipping the fixture's flag back --
    what is being asserted is that the ARM moved exactly one slot of the
    PRINTED ten.
    """
    loader.reset_caches()
    printed = list(loader._character_index()["furina"]["starting_deck"])
    dealt = list(loader.starting_deck("furina"))
    slot = printed.index(SHIPPED)
    assert len(dealt) == len(printed) == 10
    assert dealt[slot] == COPY
    assert SHIPPED not in dealt
    assert dealt[:slot] == printed[:slot]
    assert dealt[slot + 1:] == printed[slot + 1:]


def test_the_battery_and_the_run_are_dealt_the_same_ten(reframe):
    """`build_player` and `starting_deck` are the two readers of the printed
    starter, and `_starter_ids` exists so they cannot disagree. Two arms that
    each rewrote the starter behind their own entry point is exactly the
    disagreement that seam was written to prevent, so it is checked."""
    loader.reset_caches()
    battery = [c.id for c in loader.build_player("furina").draw_pile]
    run = list(loader.starting_deck("furina"))
    assert sorted(battery) == sorted(run)
    assert battery.count(COPY) == 1


def test_no_other_character_is_dealt_a_furina_row(reframe):
    """Every leg of this arm is character-scoped (`is_furina`), and the starter
    seam is no exception: in co-op the other seat may be Klee."""
    for other in ("klee", "kokomi"):
        loader.reset_caches()
        assert COPY not in loader.starting_deck(other)


# --------------------------------------------------------------------------
# (2) WHAT THE COPY PAYS. The bar is 6; 5 is one under it.
# --------------------------------------------------------------------------

def test_the_copy_pays_five_below_the_bar(reframe):
    st = _state(fanfare=5)
    _play(st, COPY)
    assert st.player.encore == 5


def test_the_copy_pays_ten_at_the_bar(reframe):
    st = _state(fanfare=6)
    _play(st, COPY)
    assert st.player.encore == 10


def test_the_bar_is_the_riders_own_and_the_reader_is_the_only_new_clause(
        reframe):
    """The copy is the shipped row plus ONE conditional, and the condition is
    the bar the four rider copies already print. Derived from both sheets so a
    silent edit to either side is a red test rather than a face that drifts."""
    shipped = loader.get_card(SHIPPED)
    copy = loader.peek_card(COPY)
    assert copy.rarity == shipped.rarity == "basic"
    assert copy.cost == shipped.cost
    assert copy.type == shipped.type
    assert copy.effects[0] == shipped.effects[0]
    rider = copy.effects[1]
    assert rider["op"] == "conditional"
    assert rider["if"] == "fanfare_at_least_6"
    assert rider["then"] == [shipped.effects[0]]
    assert len(copy.effects) == 2


def test_the_shipped_card_still_ignores_the_meter_with_the_arm_off():
    """The R130 veto stands where it was ruled. Track 2.4 -- "the starter gets
    no payoff" -- was [USER]'s 2026-08-07 veto on the SHIPPED sheet, and R254
    moves a prototype arm rather than reversing it: a flag-off Furina still
    gains 5 off a full meter. `test_fanfare_compensation.test_the_starter_does_
    not_read_the_meter` is the same pin from the other file; this one asserts
    the two rulings coexist."""
    loader.reset_caches()
    st = _state(fanfare=16)
    _play(st, SHIPPED)
    assert st.player.encore == 5
