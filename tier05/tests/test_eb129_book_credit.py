"""The event pilot SEES a pending Book of Five Rings chunk (EB-129, R205).

`EB-111` made the relic PAY for event-granted cards, through one `note_add`
door. It never made the pilot see them: a run holding the Book at 4 cards
added scored an option handing it a fifth exactly as it scored one handing it
a first, so it could walk past a free 20 HP.

R205 settled the design and left only the engineering. The credit lives at
`events.option_value`, beside the other HP terms, and is the REALIZED heal
CLIPPED TO MISSING HP -- no new weight, because option value is already
HP-denominated and the relic prints its own 20.

Three things are pinned here:
  * the credit is PRESENT with the relic at a crossing and ABSENT without it
    (and absent at four cards from the boundary, which is the same offer);
  * the clip is real -- a heal cannot restore HP that is not missing;
  * the door is STILL SINGLE. `_adds_of` forecasts what `resolve` will tick
    into `EventState.note_add`, and one test walks the whole shipped event
    pool asserting forecast == door, option by option. The chunk arithmetic
    itself is not duplicated at all: the valuation asks
    `HeldRelics.book_heal_for`, which is `note_cards_added`'s own arithmetic
    with the payment removed.
"""

from __future__ import annotations

import random

import pytest

from tier0 import roster
from tier0.content import loader
from tier05 import events, model, relics
from tier05.tests.test_relics_runlayer import (  # noqa: F401  (fixtures)
    ARCH, BASE_HP, CHAR, PILOT, SEED, _legacy_spine, _single_act, _win_stub)

BOOK = "book_of_five_rings"
PER = 5            # content: {hook: book_of_five_rings, per: 5, heal: 20}
HEAL = 20


def _starter_deck():
    return list(loader._character_index()[CHAR]["starting_deck"])


def _state(hp=40, max_hp=None, deck_ids=None, cards_added=0):
    st = events.EventState(
        character=CHAR, archetype=ARCH, hp=hp,
        max_hp=BASE_HP if max_hp is None else max_hp, gold=200,
        deck_ids=list(deck_ids if deck_ids is not None else _starter_deck()))
    st.cards_added = cards_added
    return st


def _held(ids=(BOOK,), added=0):
    h = relics.HeldRelics.hold(list(ids), CHAR)
    h.cards_added_total = added
    return h


# One card, flat CARD_HP 8.0 -- against a walk-away worth 90/GOLD_PER_HP =
# 12.0. The add LOSES on its own merits and wins only when a chunk is pending,
# which is the whole behaviour under test.
ADD_ONE = {"label": "take the card", "add_card": _starter_deck()[0]}
WALK = {"label": "take the gold instead", "gold": [90, 90]}


# --- the credit ------------------------------------------------------------

def test_the_fifth_card_is_worth_the_chunk_and_the_first_is_not():
    """R205's own sentence as an assertion: at 4-of-5 the offer is worth the
    heal more than at 0-of-5, and the difference is exactly the relic's."""
    st = _state()
    at_four = events.option_value(ADD_ONE, st, held=_held(added=4))
    at_zero = events.option_value(ADD_ONE, st, held=_held(added=0))
    assert at_four - at_zero == pytest.approx(HEAL)


def test_no_relic_scores_the_same_option_unchanged():
    st = _state()
    bare = events.option_value(ADD_ONE, st)
    assert events.option_value(ADD_ONE, st, held=None) == bare
    # A holder that simply is not the Book pays nothing either.
    assert events.option_value(
        ADD_ONE, st, held=_held(ids=("fishing_rod",), added=4)) == bare
    # And the Book itself pays nothing away from a boundary.
    assert events.option_value(ADD_ONE, st, held=_held(added=0)) == bare


def test_an_option_that_adds_nothing_is_never_credited():
    st = _state()
    for opt in (WALK, {"label": "x", "remove": 1},
                {"label": "x", "upgrade": 1}, {"label": "x", "heal": 5}):
        assert (events.option_value(opt, st, held=_held(added=4))
                == events.option_value(opt, st))


# --- the clip --------------------------------------------------------------

def test_the_credit_is_clipped_to_missing_hp():
    """A heal cannot restore HP that is not missing. Missing 5, the crossing
    is worth 5 -- not the relic's printed 20."""
    st = _state(hp=BASE_HP - 5)
    credited = (events.option_value(ADD_ONE, st, held=_held(added=4))
                - events.option_value(ADD_ONE, st))
    assert credited == pytest.approx(5.0)


def test_a_full_hp_run_is_credited_nothing():
    st = _state(hp=BASE_HP)
    assert (events.option_value(ADD_ONE, st, held=_held(added=4))
            == events.option_value(ADD_ONE, st))


def test_two_chunks_pay_twice_when_the_hp_is_there_to_take():
    """Ten adds off a fresh ledger cross two boundaries, and the clip binds on
    the total rather than on each chunk."""
    st = _state(hp=1)
    opt = {"label": "x", "pick_cards": {"of": 10, "take": 10}}
    credited = (events.option_value(opt, st, held=_held(added=0))
                - events.option_value(opt, st))
    assert credited == pytest.approx(2 * HEAL)


# --- the pilot actually changes its pick -----------------------------------

def _probe_event():
    return {"id": "eb129_probe", "options": [ADD_ONE, WALK]}


def test_the_pilot_takes_the_chunk_at_four_and_declines_it_at_zero():
    """The acceptance test the row names: same offer, same state, two ledger
    positions."""
    ev = _probe_event()
    st = _state()
    assert events.choose(random.Random(0), ev, st, held=_held(added=0)) is WALK
    assert events.choose(random.Random(0), ev, st,
                         held=_held(added=4)) is ADD_ONE
    # ... and a run without the relic never sees the difference.
    assert events.choose(random.Random(0), ev, st) is WALK


def test_mid_visit_adds_move_the_ledger_the_pilot_reads():
    """The ledger is in two pieces during a visit: `held.cards_added_total`
    absorbs the visit's tally only when the visit ENDS, so an earlier rung of
    an escalation ladder is countable only on `EventState.cards_added`."""
    ev = _probe_event()
    held = _held(added=2)
    st = _state()
    assert events.choose(random.Random(0), ev, st, held=held) is WALK
    st.note_add(2)                      # two rungs already taken this visit
    assert events.choose(random.Random(0), ev, st, held=held) is ADD_ONE
    assert held.cards_added_total == 2  # the pilot read it; nothing paid yet


# --- the quote never becomes a second payment ------------------------------

def test_book_heal_for_is_read_only():
    held = _held(added=4)
    before = (held.cards_added_total, held._book_chunks_healed)
    assert held.book_heal_for(1) == HEAL
    assert held.book_heal_for(1) == HEAL          # idempotent: still pending
    assert (held.cards_added_total, held._book_chunks_healed) == before
    assert held.book_heal_for(0) == 0
    assert held.book_heal_for(-3) == 0
    assert _held(ids=("fishing_rod",), added=4).book_heal_for(1) == 0


def test_the_quote_and_the_payout_agree_over_a_whole_ledger():
    """One arithmetic, two callers. Walk twenty adds one at a time and assert
    the quote predicted every payment before it happened."""
    held = _held()
    hp, max_hp = 1, 10_000
    for _ in range(20):
        quoted = held.book_heal_for(1)
        after = held.note_cards_added(1, hp, max_hp)
        assert after - hp == quoted
        hp = after
    assert held.cards_added_total == 20
    assert hp == 1 + 4 * HEAL


# --- the door is still single ---------------------------------------------

def _take_first(rng, deck, offers, archetype):
    """A drafter that never skips, so a card screen adds exactly one card.

    `_adds_of` is exact everywhere except a screen the shipped drafter
    declines (`DRAFT_SKIP_THRESHOLD`), where it is an upper bound. Pinning the
    forecast against the door is a statement about the SITES, so the skip is
    held still rather than left to vary card by card.
    """
    return offers[0] if offers else None


def _all_pool_options():
    for section in events._pool().values():
        for ev in section:
            for opt in events.options_of(ev):
                if opt.get("add_ancient") and CHAR not in roster.ANCIENTS:
                    continue
                yield ev, opt


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_the_forecast_equals_the_door_for_every_shipped_option(seed):
    """`_adds_of` forecasts `note_add`, and there is exactly one `note_add`.
    If a new event key ever adds a card without a line in `_adds_of`, the Book
    credit under-pays silently -- this is the test that refuses to let that
    happen."""
    checked = 0
    for ev, opt in _all_pool_options():
        st = _state()
        forecast = events._adds_of(opt, st)
        events.resolve(random.Random(seed), ev, opt, st,
                       policy=_take_first, policy_rng=random.Random(seed))
        assert st.cards_added == forecast, (ev["id"], opt.get("label"))
        checked += 1
    assert checked > 40          # the pool is not accidentally empty


def test_the_forecast_covers_every_add_site_the_door_has():
    """Site by site, in the shapes `test_book_event_adds` proves tick."""
    deck = _starter_deck()
    cases = [
        ({"add_card": "curse_guilty"}, 1),
        ({"curse": "curse_guilty"}, 1),
        ({"add_ancient": True}, 1),
        ({"random_card": {"n": 3}}, 3),
        ({"card_reward": 3}, 1),
        ({"card_screens": 2}, 2),
        ({"pick_cards": {"of": 5, "take": 2}}, 2),
        ({"duplicate_deck": True}, len(deck)),
        ({"transform": 1}, 1),
        ({"remove": 2}, 0),
        ({"upgrade": 1}, 0),
    ]
    for body, expected in cases:
        st = _state(deck_ids=deck)
        assert events._adds_of({"label": "x", **body}, st) == expected, body


# --- end to end: the run layer pays exactly what the pilot was promised ----

def _scripted_visit(ev, target):
    """A visit that walks the ledger up to `target` through the REAL door
    first, then lets the pilot choose. `target = PER - 1` leaves the run one
    card short of a chunk with nothing yet healed.

    It is a TARGET rather than a count because the run has already taken a
    card reward off the act's first fight, and that add is on the ledger too.
    """
    def visit(rng, act, st, seen, held=None, bag=None, policy=None,
              policy_rng=None):
        if held is not None:
            st.hp = held.note_cards_added(
                max(0, target - held.cards_added_total), st.hp, st.max_hp)
        opt = events.choose(rng, ev, st, held=held)
        events.resolve(rng, ev, opt, st, held=held, bag=bag, policy=policy,
                       policy_rng=policy_rng)
        st.log.append({"event": ev["id"], "option": opt["label"]})
    return visit


def test_a_run_banks_the_heal_the_valuation_credited(monkeypatch,
                                                     scripted_map):
    """Seeing side and paying side in one run: at 4-of-5 the pilot takes the
    card it declined at 0-of-5, and the run layer pays the chunk."""
    ev = _probe_event()
    monkeypatch.setattr(model, "run_fight", _win_stub(20))
    scripted_map(["N", "event", "B"])

    monkeypatch.setattr(events, "visit", _scripted_visit(ev, 0))
    at_zero = model.run_one(CHAR, ARCH, PILOT, _take_first, SEED,
                            relics=[BOOK])
    monkeypatch.setattr(events, "visit", _scripted_visit(ev, PER - 1))
    at_four = model.run_one(CHAR, ARCH, PILOT, _take_first, SEED,
                            relics=[BOOK])

    assert at_zero.events[-1]["option"] == WALK["label"]
    assert at_four.events[-1]["option"] == ADD_ONE["label"]
    assert at_four.hp_by_node[1] == at_zero.hp_by_node[1] + HEAL
