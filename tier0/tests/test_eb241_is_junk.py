"""`EB-241`: `Card.is_junk` reads rarity, type and the id namespace.

A rarity-only read let an enemy-injected status through: `statuses.make_status`
builds Dazed, Wound and the rest at type "status" and rarity "basic", so the
rotation-law pools, Recall's exhaust pool and the pilot's junk bonus all
treated a Dazed as one of the player's own cards.
"""

from __future__ import annotations

import pytest

from tier0.content import loader
from tier0.engine import kokomi_plan, statuses
from tier0.engine.state import Card


def _card(**kw) -> Card:
    base = {"id": "probe", "name": "Probe", "cost": 1, "type": "skill",
            "rarity": "common"}
    base.update(kw)
    return Card(**base)


@pytest.mark.parametrize("status_id", statuses.status_ids())
def test_every_synthesized_status_is_junk(status_id):
    card = statuses.make_status(status_id)
    assert card.rarity == "basic"          # the shape that slipped through
    assert card.is_junk


def test_type_alone_is_enough():
    assert _card(type="status").is_junk
    assert _card(type="curse").is_junk


def test_rarity_alone_is_enough():
    assert _card(rarity="curse").is_junk
    assert loader.get_card("confiscated").is_junk


def test_the_id_namespace_alone_is_enough():
    assert _card(id="status_probe").is_junk
    assert _card(id="curse_probe").is_junk
    # The sheet row that needs it: a skill-typed curse.
    assert loader.get_card("curse_spore_mind").is_junk


def test_a_personal_card_is_not_junk():
    assert not _card().is_junk
    assert not _card(id="statue", type="attack", rarity="basic").is_junk


def test_kokomis_status_reader_is_the_one_predicate():
    dazed = statuses.make_status("dazed")
    assert kokomi_plan.is_status_or_curse(dazed)
    assert not kokomi_plan.is_status_or_curse(_card())
    assert not kokomi_plan.is_status_or_curse(None)
