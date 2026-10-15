"""YAE MIKO, Publish after elites and bosses (ruled 2026-10-14,
`review/active/yae-design-axes-2026-10-14.md`).

Meditations of a Yako: "After an elite or boss fight, you may Publish an
Annotation." It was a rest-site option that competed with Smith. Three
halves, pinned here: the sim twin (`tier0/engine/yae_shrine.py`), the run
harness (`tools/yae_expansion_sim.py`) and the seat page (the reward row and
the grid it opens). The C# pins are `YaePrototypeTests`.

NOTHING MEASURED HERE IS QUOTABLE: shape assertions about rules and pages.
"""

from __future__ import annotations

import inspect

import pytest

from tier0.engine import yae_shrine as Y
from understudy import blindplay


# ---------------------------------------------------------------------------
# 1. The sim twin
# ---------------------------------------------------------------------------

def test_offered_after_an_elite_or_boss_and_never_after_a_normal_fight():
    assert Y.offers_publish("elite") and Y.offers_publish("boss")
    for room in ("monster", "event", "rest", "shop"):
        assert not Y.offers_publish(room)
    assert not Y.offers_publish("boss", final_boss=True)
    assert not Y.offers_publish("elite", gives_rewards=False)


def test_a_normal_fight_publishes_nothing_even_with_drafts():
    published: dict = {}
    assert Y.publish_after_fight("monster", {0: Y.SAKURA_SEAL}, published) == []
    assert published == {}


def test_no_offer_when_nothing_is_annotated():
    published: dict = {}
    assert Y.publish_choices({}, published) == []
    assert Y.publish_after_fight("elite", {}, published) == []
    assert published == {}


def test_the_offer_includes_cards_already_published():
    # Review r3, pick 2 (a): a Published card is offered again; the pick
    # joins its stack (the Masterpiece).
    drafts = {0: Y.RED_INK, 3: Y.FOOTNOTE, 5: Y.SAKURA_SEAL}
    assert Y.publish_choices(drafts, {5: [Y.SAKURA_SEAL]}) == [0, 3, 5]
    published = {5: [Y.SAKURA_SEAL]}
    out = Y.publish_after_fight("elite", drafts, published,
                                pick=lambda choices, d: [5])
    assert out == [(5, Y.SAKURA_SEAL)]
    assert published == {5: [Y.SAKURA_SEAL, Y.SAKURA_SEAL]}


def test_the_chosen_copy_is_the_one_published():
    """Two Strikes, slots 0 and 1: the slot picked is the one kept."""
    drafts = {0: Y.RED_INK, 1: Y.FOX_FIRE}
    published: dict = {}
    out = Y.publish_after_fight("elite", drafts, published,
                                pick=lambda choices, d: [1])
    assert out == [(1, Y.FOX_FIRE)] and published == {1: [Y.FOX_FIRE]}


def test_skip_publishes_nothing():
    published: dict = {}
    assert Y.publish_after_fight("boss", {0: Y.RED_INK}, published,
                                 pick=lambda choices, d: []) == []
    assert published == {}


def test_the_default_reading_keeps_the_best_and_the_upgrade_keeps_two():
    drafts = {0: Y.RED_INK, 1: Y.SAKURA_SEAL, 2: Y.FOOTNOTE}
    one: dict = {}
    assert Y.publish_after_fight("elite", drafts, one) == [(1, Y.SAKURA_SEAL)]
    two: dict = {}
    assert Y.publish_after_fight("elite", drafts, two,
                                 relic=Y.MEDITATIONS_UPGRADED) == [
        (1, Y.SAKURA_SEAL), (2, Y.FOOTNOTE)]


# ---------------------------------------------------------------------------
# 2. The run harness: a rest only rests
# ---------------------------------------------------------------------------

def test_the_harness_rest_site_no_longer_publishes():
    from tools import yae_expansion_sim as S
    assert not hasattr(S, "_publish_at_rest")
    src = inspect.getsource(S.run)
    assert "publish_after_fight" in src
    assert 'rests.append(("rest", None, None))' in src


# ---------------------------------------------------------------------------
# 3. The seat page: the reward row, then the grid it opens
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _fresh_fight():
    blindplay.forget_fight()
    yield
    blindplay.forget_fight()


PUBLISH_ROW = {"index": 2, "type": "publish",
               "description": "Publish an Annotation"}
GOLD_ROW = {"index": 0, "type": "gold", "description": "30 Gold",
            "gold_amount": 30}


def _rewards(items):
    return {"state_type": "rewards",
            "player": {"character": "yae", "potions": [],
                       "max_potion_slots": 3},
            "rewards": {"can_proceed": True, "items": list(items)}}


def _grid(can_cancel=True):
    red_ink = {"id": "RED_INK_ANNOTATION", "name": "Red Ink",
               "description": "This card deals 3 more damage.",
               "amount": 1, "shows_amount": False}
    blob = {"screen_type": "NSimpleCardSelectScreen",
            "prompt": "Choose a card to Publish.", "can_skip": False,
            "can_cancel": can_cancel, "preview_showing": False,
            "can_confirm": False, "selection_known": True,
            "cards": [{"index": 0, "name": "Strike", "id": "STRIKE_YAE",
                       "description": "Deal 6 damage.", "type": "Attack",
                       "cost": "1", "selected": False,
                       "enchantment": red_ink}]}
    return {"state_type": "card_select",
            "player": {"character": "yae", "potions": [], "relics": [],
                       "max_potion_slots": 3},
            "card_select": blob}


def test_the_reward_screen_shows_the_publish_row_and_a_choose_verb():
    page = blindplay.observe(_rewards([GOLD_ROW, PUBLISH_ROW]))
    assert "Publish an Annotation" in page
    assert 'choose "<reward>"' in page


def test_the_publish_grid_shows_each_cards_annotation_and_can_be_skipped():
    page = blindplay.observe(_grid())
    assert "Choose a card to Publish." in page
    assert "Strike" in page and "Red Ink" in page
    assert 'choose "<card title>"' in page
    assert "skip" in page.split("What you can say")[-1]
