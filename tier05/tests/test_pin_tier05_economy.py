"""Pin tests for the tier 0.5 economy seams: event options.

Two boundaries that no other test in the suite touched, all of them the kind
that a one-character edit moves without turning anything red:

  - an option that LOWERS max HP re-clips current HP, so a run can never walk
    out of an event room with hp above max_hp;
  - an option that would take the run to EXACTLY 0 HP is illegal, not merely
    the ones that go below.
"""

from __future__ import annotations

import random

from tier0.content import loader
from tier05 import events


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
