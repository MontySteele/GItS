"""Track O red-team, slice 12: pins on the Track H aura/payoff counters.

Only behaviour that is UNAMBIGUOUS from the shipped docstrings is pinned here.
The defects slice 12 found (the gauntlet merge's unit collision, absent-vs-zero
collapse, and `merge_stages` mutating its input) are NOT pinned -- pinning a
defect as correct is how it becomes law. They are reproduced by
`review/redteam/fixtures/track_o/s12-pooling-fixture.py` and written up in the
slice report.
"""
from __future__ import annotations

import copy

from tier0.engine import effects, reactions
from tier0.engine.state import Card
from tier0.harness import metrics

from .conftest import make_enemy, make_state


def _stub(**kw) -> metrics.FightStats:
    base = dict(
        won=True, turns=3, hp_start=80, hp_end=80, total_damage_dealt=0,
        damage_by_turn={}, energy_by_turn={}, total_block_gained=0,
        damage_blocked=0, energy_spent=0, cards_drawn_extra=0,
        energy_generated_extra=0, healing=0, encore_absorbed=0,
        debuff_stacks_applied=0, debuffed_intents=0, aura_intents=0,
        total_intents=0, reactions=0, reaction_damage=0, auras_wasted=0)
    base.update(kw)
    return metrics.FightStats(**base)


# --- aura_profile is a read, not a write ----------------------------------

def test_aura_profile_does_not_mutate_the_fights_it_pools():
    """`_pool` builds a new dict per attribute. A pooling hook that wrote back
    into its inputs would make every aggregate order- and call-count-dependent
    (which is exactly what `merge_stages` does -- see the slice report)."""
    a = _stub(aura_ops={"swirl": 2},
              aura_applications_by_source={"hit": 3},
              aura_applications_by_element={"pyro": 3},
              reactions_by_name={"melt": 1},
              conditional_evaluated={"p": 2}, conditional_fired={"p": 1})
    b = _stub(aura_ops={"apply_aura": 1},
              aura_applications_by_source={"swirl_spread": 5},
              aura_applications_by_element={"cryo": 5},
              reactions_by_name={"swirl": 1},
              conditional_evaluated={"q": 4}, conditional_fired={})
    before = (copy.deepcopy(a.__dict__), copy.deepcopy(b.__dict__))
    metrics.aura_profile([a, b])
    metrics.payoff_profile([a, b])
    metrics.aura_profile([a, b])          # twice: pooling must be idempotent
    assert (a.__dict__, b.__dict__) == before


def test_aura_profile_pooling_is_order_independent():
    a = _stub(aura_ops={"swirl": 2},
              aura_applications_by_source={"hit": 3},
              aura_applications_by_element={"pyro": 3})
    b = _stub(aura_ops={"apply_aura": 1, "swirl": 1},
              aura_applications_by_source={"swirl_spread": 5},
              aura_applications_by_element={"cryo": 5})
    fwd, rev = metrics.aura_profile([a, b]), metrics.aura_profile([b, a])
    assert fwd == rev
    assert fwd["aura_ops"] == {"swirl": 3, "apply_aura": 1}
    assert fwd["applications"] == 8


def test_merge_stages_counter_addition_is_order_independent():
    """The six Track H dicts merge by key-wise ADDITION, so stage order cannot
    move them. Deep copies per direction because merge_stages writes into
    stages[0] -- reusing the same objects would compound the two merges."""
    a = _stub(aura_ops={"swirl": 2},
              aura_applications_by_source={"hit": 3},
              aura_applications_by_element={"pyro": 3},
              reactions_by_name={"melt": 1},
              conditional_evaluated={"p": 2}, conditional_fired={"p": 1})
    b = _stub(aura_ops={"apply_aura": 5},
              aura_applications_by_source={"hit": 1, "swirl_spread": 2},
              aura_applications_by_element={"pyro": 1, "cryo": 2},
              reactions_by_name={"melt": 1, "swirl": 2},
              conditional_evaluated={"p": 1, "q": 3}, conditional_fired={"q": 3})
    attrs = ("aura_ops", "aura_applications_by_source",
             "aura_applications_by_element", "reactions_by_name",
             "conditional_evaluated", "conditional_fired")
    fwd = metrics.merge_stages([copy.deepcopy(a), copy.deepcopy(b)])
    rev = metrics.merge_stages([copy.deepcopy(b), copy.deepcopy(a)])
    for attr in attrs:
        assert getattr(fwd, attr) == getattr(rev, attr), attr
    assert fwd.aura_applications == rev.aura_applications == 6


# --- the declared source vocabulary is wider than the reachable one --------

def test_an_anemo_application_is_never_recorded_under_any_source_label():
    """`apply_aura` gates on AURA_ELEMENTS (reactions.py) BEFORE it emits, so
    the `source` label cannot rescue a non-sticking element. Consequence, and
    the reason this is pinned: `swirl_op` -- one of the four sources the
    FightStats comment and tier0/README declare -- is passed only at
    effects.py's `_op_swirl` with element='anemo', and is therefore unreachable.
    Its absence from a report is structural, not a measurement of Swirl."""
    enemy = make_enemy(hp=40)
    state = make_state(enemies=[enemy])
    reactions.apply_aura(state, enemy, "anemo", "swirl_op")
    reactions.apply_aura(state, enemy, "geo", "swirl_op")
    stats = metrics.extract(state, state.player.hp)
    assert stats.aura_applications == 0
    assert "swirl_op" not in stats.aura_applications_by_source


def test_a_swirl_op_on_a_clean_board_is_an_op_with_no_swirl_op_application():
    """Same point through the op rather than the resolver: the verb resolves,
    `aura_ops` sees it, and no `swirl_op` application exists to see."""
    state = make_state(enemies=[make_enemy(hp=40)])
    card = Card(id="s12_swirl", name="S12", type="skill", cost=0,
                effects=[{"op": "swirl", "target": "enemy"}])
    effects.resolve_card(state, card)
    stats = metrics.extract(state, state.player.hp)
    assert stats.aura_ops == {"swirl": 1}
    assert stats.aura_applications_by_source == {}


def test_refresh_all_auras_counts_as_an_op_on_a_clean_board():
    """"An op that resolves into nothing still counts here and not below"
    (FightStats, aura_ops). refresh_all_auras with nothing to refresh is the
    purest case of that rule."""
    state = make_state(enemies=[make_enemy(hp=40)])
    card = Card(id="s12_refresh", name="S12", type="skill", cost=0,
                effects=[{"op": "refresh_all_auras"}])
    effects.resolve_card(state, card)
    stats = metrics.extract(state, state.player.hp)
    assert stats.aura_ops == {"refresh_all_auras": 1}
    assert stats.aura_applications == 0


# --- aura_ops is not a denominator for applications -----------------------

def test_one_aura_op_can_produce_many_applications():
    """`aura_ops` counts VERB RESOLUTIONS; applications count auras that
    LANDED, one per body. A single op onto three bodies is 1 op and up to 3
    applications, so applications/aura_ops is not a landing rate and nothing
    in the repo computes one."""
    enemies = [make_enemy(hp=40, name=n) for n in "abc"]
    state = make_state(enemies=enemies)
    card = Card(id="s12_apply", name="S12", type="skill", cost=0,
                effects=[{"op": "apply_aura", "element": "pyro",
                          "target": "all_enemies"}])
    effects.resolve_card(state, card)
    stats = metrics.extract(state, state.player.hp)
    assert sum(stats.aura_ops.values()) == 1
    assert stats.aura_applications == 3
    assert stats.aura_applications_by_source == {"apply_aura_op": 3}
