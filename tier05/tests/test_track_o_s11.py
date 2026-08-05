"""Track O slice 11: `core_complete` at DRAFTER_VERSION 14 under adversarial
deck compositions.

These pin the properties of the predicate that are UNAMBIGUOUS from its own
docstrings and from `tier0/constants.py`'s v14 stamp -- the ones that would
turn a wrong answer into a silently wrong reported number rather than an
error. `core_complete` gates `model.py`'s `plan_live` and latches
`time_to_online`, and `_core_progress` feeds `score_offer`'s +3.0
core-advance bonus, so a limb that answered differently for the same deck
would move both the drafter and the achievability table with nothing red.

Deck builders live in
`review/redteam/fixtures/track_o/s11_adversarial_cores.py`; this file keeps
its own small copies so the suite has no dependency on the review tree.

NOT pinned here, deliberately -- these are open design questions, not
mechanical facts, and are written up in the slice report instead:
  * whether N COPIES of one card may satisfy a bar that reads like N
    distinct cards (reaction's `appliers >= 2`, spotlight's `access >= 2`);
  * whether a core of DRAFT_CORE_SIZE payoffs and zero enablers is an
    assembled deck (see the characterization test at the end, which pins
    only the docstring's letter).
"""

from __future__ import annotations

import copy
import random

from tier0 import constants as C
from tier0.content import loader
from tier05 import draft

ARCHETYPES = ("reaction", "spotlight", "fanfare", "salon", "demolition",
              "generic")


def _cards(*ids):
    return [loader.get_card(i) for i in ids]


def _battery():
    """(name, deck, archetype) triples that exercise all four limbs."""
    furina = _cards(*loader.starting_deck("furina"))
    klee = _cards(*loader.starting_deck("klee"))
    salon_enablers = _cards("salon_debut", "casting_call",
                            "gentilhomme_usher", "usher_the_waves")
    return [
        ("salon_enablers_only", furina + salon_enablers, "salon"),
        ("salon_online", furina + salon_enablers + _cards("grand_salon"),
         "salon"),
        ("salon_exactly_core", _cards("salon_debut", "casting_call",
                                      "gentilhomme_usher", "grand_salon"),
         "salon"),
        ("salon_one_short", _cards("salon_debut", "casting_call",
                                   "grand_salon"), "salon"),
        ("salon_four_copies_one_card", _cards(*(["grand_salon"] * 4)),
         "salon"),
        ("demolition_online",
         klee + _cards("jumpy_dumpty", "pop", "mine_toss", "double_pop",
                       "remote_detonator"), "demolition"),
        ("reaction_online",
         klee + _cards("dahlia_sacramental_shower", "kaeya_frostgnaw",
                       "sizzle"), "reaction"),
        ("reaction_no_amp",
         klee + _cards("dahlia_sacramental_shower", "kaeya_frostgnaw"),
         "reaction"),
        ("spotlight_online", furina + _cards("lynette_box_trick", "limelight"),
         "spotlight"),
        ("spotlight_access_only", furina + _cards("lynette_box_trick"),
         "spotlight"),
        ("fanfare_online", furina + _cards("rapturous_applause"), "fanfare"),
        ("fanfare_floor_no_reader", furina + _cards("the_sea_is_my_stage"),
         "fanfare"),
        ("fanfare_reader_no_floor", furina + _cards("crescendo"), "fanfare"),
    ]


def test_core_complete_is_a_function_of_the_deck_multiset_not_its_order():
    """A deck is a multiset; `core_complete` counts and sums over it and
    never looks at position. An order-dependent answer would make
    `plan_live` and `time_to_online` depend on the sequence the drafter
    happened to pick cards in -- a wrong number with nothing red, and one
    that would survive every existing pin, because every existing pin builds
    its decks in one fixed order.
    """
    rng = random.Random(20260805)
    for name, deck, arch in _battery():
        expected = draft.core_complete(deck, arch)
        expected_progress = draft._core_progress(deck, arch)
        for _ in range(16):
            shuffled = list(deck)
            rng.shuffle(shuffled)
            assert draft.core_complete(shuffled, arch) is expected, name
            assert draft._core_progress(shuffled, arch) == expected_progress, \
                name


def test_no_limb_is_vacuously_complete_on_an_empty_deck():
    """Every bar is >= 1, so "nothing to satisfy" can never read as
    "satisfied". The unknown-archetype rows matter too: an archetype string
    the sheets do not carry falls through to the generic limb, and must
    report an empty core rather than a finished one.
    """
    for arch in ARCHETYPES + ("no_such_archetype", ""):
        assert not draft.core_complete([], arch), arch
        assert draft._core_progress([], arch) == 0.0, arch
    assert C.DRAFT_CORE_SIZE >= 1
    assert draft.GENERIC_PAYOFF_COVERAGE >= 1
    assert draft.FANFARE_GENERATION_COVERAGE >= 1
    assert draft.FANFARE_FLOOR_COVERAGE >= 1
    assert draft.FANFARE_PAYOFF_COVERAGE >= 1


def test_progress_reaches_one_exactly_when_the_core_is_complete_every_limb():
    """`_generic_core_counts` exists so the predicate and the progress meter
    "cannot drift apart" (draft.py, v14) -- the v10 fanfare fix had to move
    both halves for the same reason. test_m5 pins that agreement on the
    salon limb only; the other three limbs have the same contract and no
    pin, and `_core_progress` is the half with teeth (score_offer's +3.0).
    """
    for name, deck, arch in _battery():
        assert (draft._core_progress(deck, arch) == 1.0) \
            is draft.core_complete(deck, arch), name


def test_core_complete_does_not_mutate_the_deck_it_is_handed():
    """model.py feeds it `loader.peek_card` results -- SHARED prototypes, not
    copies (loader.py: "Read-only callers that only score a deck should use
    `peek_card`"). Any write to `effects`, `archetypes` or `role` here would
    poison the card index for the rest of the process, and every later
    `core_complete` in every later run would answer a different question
    with nothing raised.
    """
    deck = _cards("salon_debut", "casting_call", "gentilhomme_usher",
                  "grand_salon", "rapturous_applause", "the_sea_is_my_stage",
                  "crescendo", "limelight")
    before = copy.deepcopy([(c.id, c.role, list(c.archetypes), c.rarity,
                             c.effects) for c in deck])
    for arch in ARCHETYPES:
        draft.core_complete(deck, arch)
        draft._core_progress(deck, arch)
    after = [(c.id, c.role, list(c.archetypes), c.rarity, c.effects)
             for c in deck]
    assert before == after


def test_a_spotlight_access_card_is_never_also_counted_as_machinery():
    """`_is_spotlight_machinery` ends in `not _is_spotlight_access(card)`, and
    that guard is load-bearing: three content cards (an_invitation,
    guest_list, command_performance) are Companions/guest-star generators
    that ALSO carry the spotlight tag with an enabler/payoff role. Without
    the guard, two copies of one of them would satisfy both limbs at once and
    a two-card deck would read ONLINE.
    """
    dual = [c for c in loader._card_index().values()
            if draft._is_spotlight_access(c) and "spotlight" in c.archetypes
            and c.role in ("enabler", "payoff")]
    assert dual, "premise: content still has access cards with the tag"
    for card in dual:
        assert not draft._is_spotlight_machinery(card), card.id
    deck = _cards(dual[0].id, dual[0].id)
    assert sum(1 for c in deck if draft._is_spotlight_access(c)) == 2
    assert not draft.core_complete(deck, "spotlight")


def test_generic_bar_as_written_counts_payoffs_toward_both_limbs():
    """CHARACTERIZATION of the docstring's letter, not an endorsement.

    `core_complete`: "DRAFT_CORE_SIZE on-plan enabler/payoff cards, AT LEAST
    ONE of which is a payoff". A payoff is an on-plan enabler-or-payoff card,
    so DRAFT_CORE_SIZE payoffs and ZERO enablers satisfy both limbs -- the
    exact mirror of the deck v14 exists to reject. This test pins today's
    answer so that the mirror case is a DECISION next time and not a
    silently moved bar; whether it should stay is a draft-reach question for
    the design side (Track O slice 11).
    """
    payoff_only = _cards(*(["grand_salon"] * C.DRAFT_CORE_SIZE))
    on_plan, payoffs = draft._generic_core_counts(payoff_only, "salon")
    assert (on_plan, payoffs) == (C.DRAFT_CORE_SIZE, C.DRAFT_CORE_SIZE)
    assert draft.core_complete(payoff_only, "salon")
    assert draft._core_progress(payoff_only, "salon") == 1.0

    enabler_only = _cards("salon_debut", "casting_call", "gentilhomme_usher",
                          "usher_the_waves")
    assert draft._generic_core_counts(enabler_only, "salon") == \
        (C.DRAFT_CORE_SIZE, 0)
    assert not draft.core_complete(enabler_only, "salon")
