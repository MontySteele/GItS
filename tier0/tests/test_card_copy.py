"""Card.__deepcopy__ is a PERFORMANCE rewrite of copy.deepcopy, so the whole
contract is "indistinguishable from the generic one".

Card copying is the simulator's hottest operation -- every `loader.get_card`,
every in-combat clone (Dual Wield, conscript, Armaments) -- and the generic
deepcopy spent its time walking ~40 immutable scalar fields through the memo
machinery. The hand-rolled version copies only the container-valued fields.
That is only safe while two things hold, and both are pinned here: the field
list is complete, and card payloads stay plain yaml-shaped data.
"""

from __future__ import annotations

import copy
import dataclasses

from tier0.content import loader, upgrades
from tier0.engine.state import Card, _copy_plain, _MUTABLE_FIELDS


def _all_cards():
    return list(loader._card_index().values())


def test_mutable_field_list_covers_every_container_field():
    """The list is hand-maintained; a new list/dict field must join it.

    Miss one and the copy SHARES it with the prototype -- a mutation would
    then leak backwards into every future `get_card` of that id, which is
    exactly the class of bug this whole file exists to prevent.
    """
    container = set()
    for f in dataclasses.fields(Card):
        default = f.default_factory() if f.default_factory is not dataclasses \
            .MISSING else f.default
        if isinstance(default, (list, dict)) or f.type in (
                "list[dict]", "list[str]", "Optional[dict]"):
            container.add(f.name)
    assert container == set(_MUTABLE_FIELDS)


def test_deepcopy_is_equal_to_the_generic_one_for_every_card():
    for card in _all_cards():
        assert copy.deepcopy(card) == card
        # Same object graph the generic implementation would have produced.
        assert dataclasses.asdict(copy.deepcopy(card)) == dataclasses.asdict(card)


def test_copies_share_no_mutable_state_with_the_prototype():
    for card in _all_cards():
        clone = copy.deepcopy(card)
        for name in _MUTABLE_FIELDS:
            original, copied = getattr(card, name), getattr(clone, name)
            if original is None:
                assert copied is None
                continue
            assert copied is not original
            # Nested containers must be fresh too -- `effects` holds dicts,
            # and conditional effects hold lists of dicts inside those.
            for a, b in zip(_walk(original), _walk(copied)):
                assert a is not b


def _walk(val):
    """Every container reachable inside a card payload, prototype order."""
    if isinstance(val, dict):
        yield val
        for v in val.values():
            yield from _walk(v)
    elif isinstance(val, list):
        yield val
        for v in val:
            yield from _walk(v)


def test_effect_mutation_does_not_reach_the_prototype():
    # Rampage's grow_damage mutates the effect dict on the live instance.
    card = loader.get_card("strike")
    card.effects[0]["amount"] += 99
    card.tags.append("scratch")
    assert loader.get_card("strike").effects[0]["amount"] == 6
    assert "scratch" not in loader.get_card("strike").tags


def test_copy_plain_leaves_scalars_alone_and_freshens_containers():
    payload = {"a": 1, "b": [1, 2, {"c": "x"}], "d": None}
    out = _copy_plain(payload)
    assert out == payload
    assert out is not payload
    assert out["b"] is not payload["b"]
    assert out["b"][2] is not payload["b"][2]


# --- the read-only door ---------------------------------------------------

def test_peek_card_is_shared_and_get_card_is_not():
    assert loader.peek_card("strike") is loader.peek_card("strike")
    assert loader.get_card("strike") is not loader.get_card("strike")
    assert loader.get_card("strike") == loader.peek_card("strike")


def test_peek_card_resolves_upgrades_like_get_card():
    upgradable = next(c.id for c in _all_cards() if upgrades.has_upgrade(c.id))
    uid = upgradable + upgrades.SUFFIX
    assert loader.peek_card(uid) == loader.get_card(uid)
    assert loader.peek_card(uid).id == uid


def test_reset_caches_drops_the_prototype_cache_too():
    """`_card_prototype` is derived from `_card_index`; clearing one without
    the other would serve prototypes built from a stale content tree."""
    before = loader.peek_card("strike")
    loader.reset_caches()
    assert loader.peek_card("strike") is not before
    assert loader.peek_card("strike") == before
