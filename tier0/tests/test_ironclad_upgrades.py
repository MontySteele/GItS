"""Local real-Ironclad upgrade coverage and the new generic delta shapes.

Like test_real_ironclad, this module skips on a bare clone: every value and
card id comes from gitignored game_ref artifacts rather than committed game
data. The assertions pin mechanics, completeness, and provenance boundaries.
"""

import pytest
import yaml

from tier0.content import loader, upgrades
from tier0.engine import effects, refpowers
from tier0.tests.conftest import make_state
from tier05 import model, shop


UPGRADE_PATH = upgrades.EXTERNAL_UPGRADE_SHEETS[0]
pytestmark = pytest.mark.skipif(
    not UPGRADE_PATH.exists(),
    reason="real Ironclad upgrades are a local game_ref artifact",
)


def _walk(effects_list):
    for fx in effects_list:
        yield fx
        for branch in ("then", "else"):
            if isinstance(fx.get(branch), list):
                yield from _walk(fx[branch])


@pytest.fixture(scope="module")
def deltas():
    return yaml.safe_load(UPGRADE_PATH.read_text())


def _card_with(deltas, key):
    cid, delta = next((cid, delta) for cid, delta in deltas.items()
                      if key in delta)
    return loader.get_card(cid), loader.get_card(cid + upgrades.SUFFIX), delta


@pytest.mark.parametrize(
    ("key", "op", "field"),
    [("energy", "energy", "amount"),
     ("times", "damage", "times"),
     ("max_hp", "gain_max_hp", "amount")],
)
def test_numeric_external_delta_shapes_apply(deltas, key, op, field):
    base, upgraded, delta = _card_with(deltas, key)
    before = next(fx for fx in _walk(base.effects)
                  if fx.get("op") == op and field in fx)
    after = next(fx for fx in _walk(upgraded.effects)
                 if fx.get("op") == op and field in fx)
    assert after[field] == before[field] + delta[key]


@pytest.mark.parametrize(
    ("key", "op", "field"),
    [("upgrade_scope", "upgrade_in_hand", "scope"),
     ("exhaust_select", "exhaust_from", "select")],
)
def test_behavioral_external_delta_shapes_apply(deltas, key, op, field):
    base, upgraded, delta = _card_with(deltas, key)
    before = next(fx for fx in _walk(base.effects) if fx.get("op") == op)
    after = next(fx for fx in _walk(upgraded.effects) if fx.get("op") == op)
    assert before.get(field) != delta[key]
    assert after[field] == delta[key]


def test_upgraded_upgrade_in_hand_card_upgrades_every_eligible_card(deltas):
    _, card, _ = _card_with(deltas, "upgrade_scope")
    state = make_state()
    candidates = [c for c in loader._card_index().values()
                  if c.character == "real_ironclad"
                  and upgrades.has_upgrade(c.id)][:2]
    assert len(candidates) == 2
    state.player.hand = candidates

    effects.resolve_card(state, card)

    assert all(c.id.endswith(upgrades.SUFFIX) for c in state.player.hand)


def test_aggression_recalls_a_real_card_in_its_upgraded_form():
    state = make_state()
    attack = next(c for c in loader._card_index().values()
                  if c.character == "real_ironclad" and c.type == "attack")
    state.player.hand = []
    state.player.discard_pile = [attack]
    state.player.powers["aggression"] = 1

    refpowers.side_turn_start_early(state)

    assert [c.id for c in state.player.hand] == [attack.id + upgrades.SUFFIX]
    assert not [event for event in state.log
                if event["event"] == "UNIMPLEMENTED"
                and event.get("power") == "aggression"]


def test_run_layer_can_smith_and_does_not_misclassify_basics_as_dead():
    player = loader.build_player("real_ironclad")
    starter = list(player.draw_pile)
    ids = [card.id for card in starter]

    action, target = model.rest_action(ids, hp=80, max_hp=80,
                                       archetype="generic")

    assert action == "upgrade"
    assert target in ids and upgrades.has_upgrade(target)
    assert not any(shop.is_known_dead(card) for card in starter)
