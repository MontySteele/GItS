"""The Ancient acquisition door and the leaks around it (EB-30m / R127).

The three Ancients are reachable through exactly one option in the whole run
layer: the act-2 Darv event's Dusty Tome. Everything else about them is an
ABSENCE -- `rarity: ancient` has no row in `C.RARITY_ODDS`, and that is what
keeps them out of reward screens, shop stock and transform results without a
single filter naming them.

An absence is a poor thing to trust silently, which is what this file is for.
It sweeps the door from both sides: nothing else opens it, and it opens
correctly for every roster character (and for no one else).
"""

from __future__ import annotations

import random

import pytest

from tier0 import constants as C, roster
from tier0.content import loader, upgrades
from tier05 import events, rewards, shop

ANCIENT_IDS = frozenset(roster.ANCIENTS.values())
ANCIENT_IDS_UPGRADED = frozenset(i + upgrades.SUFFIX for i in ANCIENT_IDS)


def _st(character="furina", **kw):
    base = dict(character=character, archetype="salon", hp=60, max_hp=80,
                gold=200, deck_ids=["strike", "defend", "defend"])
    base.update(kw)
    return events.EventState(**base)


# --- nothing but the door --------------------------------------------------

@pytest.mark.parametrize("character", sorted(roster.ANCIENTS))
def test_no_reward_screen_or_shop_ever_offers_an_ancient(character):
    """Seed-swept, because a rarity roll that never lands on Ancient by luck
    is indistinguishable from one that cannot -- until the seed that lands."""
    for seed in range(120):
        rng = random.Random(seed)
        offers = rewards.roll_rewards(rng, character)
        assert not {c.id for c in offers} & ANCIENT_IDS
        stock = shop.shop_offer(random.Random(seed), character)
        assert not {c.id for c in stock} & ANCIENT_IDS


def test_the_rarity_has_no_odds_row_and_that_is_the_mechanism():
    """Stated as its own assertion so that adding an `ancient` row to
    RARITY_ODDS -- the plausible "completeness" edit -- fails here with the
    reason attached, rather than quietly putting Ancients in every pool."""
    assert "ancient" not in C.RARITY_ODDS
    assert "ancient" in C.ACQUISITION_ONLY_RARITIES


def test_an_ancient_in_the_deck_is_never_chosen_for_transform():
    """The one-way leak the transform branch would otherwise be: an Ancient's
    rarity has no pool, so the `.get(rarity) or <whole pool>` fallback would
    trade a once-per-run card for a random common."""
    st = _st(deck_ids=["all_the_worlds_a_stage+"])
    opt = {"label": "probe", "transform": 1}
    for seed in range(60):
        clone = _st(deck_ids=list(st.deck_ids))
        events.resolve(random.Random(seed), events.get_event("bugslayer"),
                       opt, clone)
        assert clone.deck_ids == ["all_the_worlds_a_stage+"]


def test_removal_still_reaches_a_held_ancient():
    """The other side of the same coin, and deliberately NOT symmetric with
    transform: giving an Ancient up is a real choice the game allows, so
    `remove:` must keep seeing it."""
    st = _st(deck_ids=["all_the_worlds_a_stage+"])
    events.resolve(random.Random(0), events.get_event("bugslayer"),
                   {"label": "probe", "remove": 1}, st)
    assert st.deck_ids == []


def test_the_ref_ironclad_pool_drops_off_table_rarities_instead_of_refiling():
    """His branch used to remap any unknown rarity to `common`, which is a
    silent promotion. Base-game Ancients (Break, Corruption) are real cards
    in the extracted pools, so this is not a hypothetical."""
    pool = rewards.character_pool("ref_ironclad")
    assert set(pool) <= set(C.RARITY_ODDS)


def test_the_companion_slot_agrees_with_the_character_slot():
    pool = rewards.companion_pool()
    assert set(pool) <= set(C.RARITY_ODDS)


# --- the door itself -------------------------------------------------------

def test_darv_is_an_act_two_event():
    assert "darv" in [e["id"] for e in events.pool_for(1)]
    assert "darv" not in [e["id"] for e in events.pool_for(0)]


@pytest.mark.parametrize("character", sorted(roster.ANCIENTS))
def test_the_tome_grants_exactly_that_character_s_ancient_upgraded(character):
    """The Tome upgrades what it grants (C# DustyTome.AfterObtained), which
    is why ANCIENT_WITNESS pins the upgraded numbers."""
    st = _st(character, deck_ids=["strike"])
    ev = events.get_event("darv")
    opt = events.choose(random.Random(0), ev, st)
    assert opt.get("add_ancient")           # the walk-away is worth 0
    events.resolve(random.Random(0), ev, opt, st)
    added = [cid for cid in st.deck_ids if cid != "strike"]
    assert added == [roster.ANCIENTS[character] + upgrades.SUFFIX]
    assert loader.peek_card(added[0]) is not None


def test_walking_away_grants_nothing():
    st = _st(deck_ids=["strike"])
    ev = events.get_event("darv")
    walk = [o for o in ev["options"] if not o.get("add_ancient")][0]
    events.resolve(random.Random(0), ev, walk, st)
    assert st.deck_ids == ["strike"]


def test_the_option_is_priceable():
    """`option_value` returning 0 for the take would make the walk-away win
    on declaration order, and the door would be dead content."""
    st = _st()
    take = events.get_event("darv")["options"][0]
    assert events.option_value(take, st) == events.CARD_HP


# --- gating: only characters who have an Ancient can meet the Tome ---------

@pytest.mark.parametrize("character", ["ref_ironclad", "real_ironclad",
                                       "real_silent"])
def test_a_character_with_no_ancient_never_rolls_darv(character):
    """The reference anchors have no entry in `roster.ANCIENTS`. Hiding the
    event is what keeps the C# softlock's sim analogue impossible -- and it
    also stops the event consuming one of their Unknown rooms for nothing."""
    for act in (0, 1, 2):
        assert "darv" not in [e["id"]
                              for e in events.pool_for(act, character)]
    seen: set[str] = set()
    for seed in range(200):
        ev = events.roll_event(random.Random(seed), 1, seen, character)
        assert ev is None or ev["id"] != "darv"


@pytest.mark.parametrize("character", sorted(roster.ANCIENTS))
def test_a_roster_character_can_roll_darv(character):
    """The other direction: a gate that hides the event from EVERYONE would
    pass every test above and ship dead content."""
    assert "darv" in [e["id"] for e in events.pool_for(1, character)]


def test_pool_for_without_a_character_is_the_unfiltered_view():
    """The content sweeps ask "what can this act hold", not "what can this
    run meet". Defaulting to unfiltered keeps those two questions apart."""
    assert "darv" in [e["id"] for e in events.pool_for(1)]


def test_granting_an_ancient_to_a_character_who_has_none_is_loud():
    """Unreachable through `visit` -- the gate above sees to that -- so the
    failure this guards is someone calling `resolve` directly, or a future
    gate regression. A silent no-grant would hide both."""
    st = _st("ref_ironclad", deck_ids=["strike"])
    ev = events.get_event("darv")
    with pytest.raises(KeyError, match="EB-30m"):
        events.resolve(random.Random(0), ev, ev["options"][0], st)
