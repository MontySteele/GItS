"""Pin tests for the status-card factory (tier0/engine/statuses.py).

Injected status cards are built by hand rather than loaded from a sheet, so
every field `make_status` stamps is a behavioural constant that nothing else
in the engine re-derives. These tests pin the stamped fields and the
per-instance independence of the mutable ones.
"""

from tier0.engine import statuses


def test_injected_status_cards_cost_zero():
    """Every injected status card is stamped cost 0. The cards are
    unplayable, so no energy check ever reads the field -- it is pinned here
    because nothing else in the engine would notice it drifting."""
    for sid in statuses.status_ids():
        card = statuses.make_status(sid)
        assert card.cost == 0, sid
        assert card.type == "status", sid


def test_injected_status_cards_carry_basic_rarity_not_status_rarity():
    """Injected status cards carry rarity "basic". The "status" rarity is a
    separate, sheet-only category (the `confiscated` token), and it is what
    the `filter: status` card selection in effects/policy matches on -- so an
    injected clog is NOT a member of that selection pool."""
    for sid in statuses.status_ids():
        card = statuses.make_status(sid)
        assert card.rarity == "basic", sid
        assert card.rarity != "status", sid


def test_each_injected_status_owns_its_tag_list():
    """Each call to make_status returns a card whose `tags` list is its own
    object, copied off the spec template. Mutating one injected copy's tags
    must not reach any other copy, nor the template later calls read from."""
    first = statuses.make_status("dazed")
    second = statuses.make_status("dazed")
    assert first.tags == ["ethereal"]
    assert second.tags == ["ethereal"]
    assert first.tags is not second.tags

    first.tags.append("scratch")
    assert second.tags == ["ethereal"]
    assert statuses.make_status("dazed").tags == ["ethereal"]
