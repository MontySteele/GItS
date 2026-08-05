"""Pin tests for the tier 0.5 economy seams: event options and the banner roll.

Three boundaries that no other test in the suite touched, all of them the kind
that a one-character edit moves without turning anything red:

  - an option that LOWERS max HP re-clips current HP, so a run can never walk
    out of an event room with hp above max_hp;
  - an option that would take the run to EXACTLY 0 HP is illegal, not merely
    the ones that go below;
  - a 5-star roster sitting exactly at BANNER_FEATURED_SLOTS features all of
    it without touching the run's Random, so seeded runs stay replayable.
"""

from __future__ import annotations

import random
from unittest import mock

from tier0 import constants as C
from tier0.content import loader
from tier0.engine.state import Card
from tier05 import events, rewards


def _deck(n=8):
    ids = sorted(loader.character_packages("ref_ironclad")
                 .get("archetype_package", []))
    return (ids * 3)[:n]


def _st(**kw):
    base = dict(character="ref_ironclad", archetype="generic", hp=70,
                max_hp=80, gold=200, deck_ids=_deck())
    base.update(kw)
    return events.EventState(**base)


# --- max-HP costs re-clip current HP ---------------------------------------


def test_max_hp_cost_clips_current_hp_down_to_the_new_maximum():
    """Paying max HP for an event reward can never leave the run holding more
    current HP than max HP: after the max is lowered, current HP is clipped to
    it, so a max-HP cost is always felt as real health lost."""
    st = _st(hp=70, max_hp=70)
    events.resolve(random.Random(0), {"id": "unrest_site"},
                   {"label": "Kill the Trees", "max_hp": -8}, st)
    assert st.max_hp == 62
    assert st.hp == 62


def test_max_hp_cost_leaves_current_hp_alone_when_it_is_already_below():
    """The clip is a ceiling, not an assignment: a run already below the new
    maximum keeps the current HP it had, so a max-HP cost never heals and
    never double-charges."""
    st = _st(hp=40, max_hp=70)
    events.resolve(random.Random(0), {"id": "unrest_site"},
                   {"label": "Kill the Trees", "max_hp": -8}, st)
    assert st.max_hp == 62
    assert st.hp == 40


# --- the lethal-option guard, at the boundary ------------------------------


def test_option_that_would_leave_exactly_zero_hp_is_not_available():
    """An event option is illegal as soon as it would take the run to 0 HP --
    exactly 0 counts as lethal, not just going below it. Nothing in the run
    model survives 0 HP, so the events pool never offers the killing choice."""
    event = {"id": "lethal_probe", "options": [
        {"label": "Walk Away"},
        {"label": "Reach Deeper", "hp": -5},
    ]}
    labels = [o["label"] for o in events.available(event, _st(hp=5))]
    assert labels == ["Walk Away"]


def test_option_that_leaves_one_hp_is_still_available():
    """The other side of the same boundary: surviving on 1 HP is legal, so an
    option is only withheld when it is actually fatal."""
    event = {"id": "lethal_probe", "options": [
        {"label": "Walk Away"},
        {"label": "Reach Deeper", "hp": -5},
    ]}
    labels = [o["label"] for o in events.available(event, _st(hp=6))]
    assert labels == ["Walk Away", "Reach Deeper"]


# --- the banner roll at exactly the slot count -----------------------------


def _fake_roster(n: int, nation: str = "mondstadt") -> list[Card]:
    return [Card(id=f"star5_{i}", name=f"Five Star {i}", cost=2, type="power",
                 rarity="rare", role_c="buffer", star=5, nation=nation)
            for i in range(n)]


def test_roster_exactly_at_the_slot_count_features_all_without_consuming_rng():
    """A nation with exactly BANNER_FEATURED_SLOTS designed 5-stars features
    all of them directly -- it does not go through the sampler. The featured
    set would be identical either way, but sampling would advance the run's
    single Random, so every downstream roll of a seeded run depends on this
    boundary staying where it is."""
    fake = _fake_roster(C.BANNER_FEATURED_SLOTS)
    with mock.patch.object(rewards, "five_star_roster", lambda n: fake):
        rng = random.Random(7)
        banner = rewards.roll_banner(rng, nations=("mondstadt",))
    assert banner == frozenset(c.id for c in fake)
    assert rng.random() == random.Random(7).random(), \
        "the roll consumed rng at the feature-all boundary"


def test_roster_one_over_the_slot_count_samples_and_consumes_rng():
    """The control for the boundary above: one 5-star past the cap and the
    roll does sample -- exactly BANNER_FEATURED_SLOTS featured, and the run's
    Random has moved."""
    fake = _fake_roster(C.BANNER_FEATURED_SLOTS + 1)
    with mock.patch.object(rewards, "five_star_roster", lambda n: fake):
        rng = random.Random(7)
        banner = rewards.roll_banner(rng, nations=("mondstadt",))
    assert len(banner) == C.BANNER_FEATURED_SLOTS
    assert rng.random() != random.Random(7).random()
