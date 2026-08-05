"""Last Call, track H: the aura + payoff counters, pinned.

Track D asked what share of the damage reactions carry. Track H asks the two
questions sitting either side of that one:

H1 -- how often do aura-applying OPS fire, and what actually puts an aura on
the board (an op, an element-tagged attack, or Swirl copying one across)?

H2 -- how often do the reaction PAYOFF riders trigger? The 2026-07-26 audit
asserts they are unused, at roughly zero triggers. That claim had never had a
count behind it, and a count is the only thing that can settle it.

Same fence as track D and for the same reason: everything here is log-side,
every number REPORTS and none of them GRADES, and the fight must be bit-identical
with the counters in place. The engine gains two emit-only things -- an
`aura_op` row and a `source` key on `aura_applied` -- and nothing else moves.
"""

from __future__ import annotations

from tier0.engine import effects, reactions
from tier0.engine.state import Card
from tier0.harness import metrics
from tier0.harness.runner import run_battery

from .conftest import make_enemy, make_state

# Klee's reaction package is the one battery config that lights every branch of
# the aura decomposition (op application, hit application, Swirl spread) AND
# carries reaction-payoff riders. Same arm track D pins on, deliberately.
REACTIVE = ("klee", "reaction_weighted", "punisher", "reaction")


def _battery(fights=40, seed=7):
    return run_battery(*REACTIVE, fights, seed)


# --- H0: the instrument does not move the fight --------------------------

def test_the_counters_did_not_move_the_fight():
    """The load-bearing one. `aura_op` and the `source` key are emits; the
    outcome figures stay a pure function of the seed."""
    one = run_battery(*REACTIVE, 25, 99)
    two = run_battery(*REACTIVE, 25, 99)
    assert [(s.won, s.turns, s.hp_end, s.total_damage_dealt, s.reactions)
            for s in one] == \
           [(s.won, s.turns, s.hp_end, s.total_damage_dealt, s.reactions)
            for s in two]


def test_track_d_figures_are_untouched_by_track_h():
    """D1's decomposition is ratified-adjacent (it is what a design session
    will quote). Track H may not perturb it."""
    for s in _battery():
        assert s.reaction_damage == (s.reaction_damage_amp
                                     + s.reaction_damage_splash)
        assert s.damage_from_reactions == (s.reaction_damage_amp
                                           + s.reaction_damage_splash
                                           + s.reaction_damage_dot)


# --- H1: aura ops and aura applications ----------------------------------

def test_aura_applications_split_by_source_and_element_agree():
    """Two cuts of one event stream. They must total the same number, or one
    of them is dropping rows."""
    for s in _battery():
        assert (sum(s.aura_applications_by_source.values())
                == sum(s.aura_applications_by_element.values())
                == s.aura_applications)


def test_only_aura_elements_are_ever_recorded_as_applied():
    """Anemo and Geo trigger and never stick (design doc §2.1). If either
    shows up as an application, the resolver changed underneath the counter."""
    for s in _battery():
        assert set(s.aura_applications_by_element) <= reactions.AURA_ELEMENTS


def test_sources_are_the_declared_vocabulary():
    known = {"hit", "apply_aura_op", "swirl_op", "swirl_spread"}
    for s in _battery():
        assert set(s.aura_applications_by_source) <= known


def test_an_aura_op_that_lands_nothing_still_counts_as_an_op():
    """The whole point of counting the op separately from its effect: a Swirl
    into a clean board fires and applies nothing. `aura_ops` sees it,
    `aura_applications` does not."""
    state = make_state(enemies=[make_enemy(hp=40)])
    card = Card(id="probe_swirl", name="Probe", type="skill", cost=0,
                effects=[{"op": "swirl", "target": "enemy"}])
    effects.resolve_card(state, card)
    stats = metrics.extract(state, state.player.hp)
    assert stats.aura_ops.get("swirl") == 1
    assert stats.aura_applications == 0


def test_swirl_spread_is_attributed_to_swirl_and_not_to_the_hit():
    """Swirl copies the consumed aura across the board. Those copies are the
    reaction's doing, not the triggering card's element. The resolver spreads
    to every LIVING enemy including the one that was swirled, so two bodies
    means two spread applications -- pinned as-is, not as an opinion about
    whether that re-application is correct."""
    enemies = [make_enemy(hp=40, name="a"), make_enemy(hp=40, name="b")]
    state = make_state(enemies=enemies)
    reactions.apply_aura(state, enemies[0], "pyro", "apply_aura_op")
    reactions.resolve_hit(state, enemies[0], "anemo", 0, "swirl_op")
    stats = metrics.extract(state, state.player.hp)
    assert stats.aura_applications_by_source.get("apply_aura_op") == 1
    assert stats.aura_applications_by_source.get("swirl_spread") == 2
    assert "hit" not in stats.aura_applications_by_source
    assert stats.reactions_by_name.get("swirl") == 1


def test_reactions_by_name_sums_to_the_reaction_count():
    for s in _battery():
        assert sum(s.reactions_by_name.values()) == s.reactions


def test_aura_profile_pools_and_reports_no_verdict():
    stats = _battery()
    prof = metrics.aura_profile(stats)
    assert prof["applications"] == sum(s.aura_applications for s in stats)
    assert prof["aura_ops_total"] == sum(sum(s.aura_ops.values())
                                         for s in stats)
    assert prof["reactions"] == sum(s.reactions for s in stats)
    # No grade, no band, no pass/fail -- the track D fence, restated.
    for key in ("verdict", "grade", "ok", "healthy", "band", "target"):
        assert key not in prof


def test_aura_profile_is_empty_not_exploding_on_no_fights():
    assert metrics.aura_profile([]) == {}
    assert metrics.payoff_profile([]) == {}


# --- H2: the payoff riders ------------------------------------------------

def test_payoff_predicates_are_all_real_predicates():
    """A typo in the audit list would read as `absent` -- i.e. as evidence for
    the very claim being tested. Pin the names against the DSL."""
    from tier0.engine.effects import is_known_predicate
    for name in (metrics.REACTION_PAYOFF_PREDICATES
                 + metrics.AURA_PAYOFF_PREDICATES):
        assert is_known_predicate(name), name


def test_fired_never_exceeds_evaluated():
    for s in _battery():
        for pred, n in s.conditional_fired.items():
            assert n <= s.conditional_evaluated[pred]


def test_payoff_profile_slices_agree_with_the_per_predicate_table():
    prof = metrics.payoff_profile(_battery())
    for key, names in (("reaction_payoff", metrics.REACTION_PAYOFF_PREDICATES),
                       ("aura_payoff", metrics.AURA_PAYOFF_PREDICATES)):
        sl = prof[key]
        assert sl["evaluated"] == sum(prof["by_predicate"][p]["evaluated"]
                                      for p in names
                                      if p in prof["by_predicate"])
        assert sl["fired"] == sum(prof["by_predicate"][p]["fired"]
                                  for p in names if p in prof["by_predicate"])
        assert set(sl["absent"]) == {p for p in names
                                     if p not in prof["by_predicate"]}


def test_absent_and_zero_are_kept_apart():
    """"No card carried it" and "cards carried it and it never fired" are two
    different findings. A profile that collapses them cannot answer the
    audit's question either way."""
    ref = run_battery("ref_ironclad", "starter", "punisher", "generic", 10, 3)
    prof = metrics.payoff_profile(ref)
    # The reference Ironclad has no reaction riders at all: absent, not 0/0.
    assert set(prof["reaction_payoff"]["absent"]) == set(
        metrics.REACTION_PAYOFF_PREDICATES)
    assert prof["reaction_payoff"]["predicates"] == {}


def test_a_payoff_rider_that_fires_is_counted_as_fired():
    """Constructive: build the state the rider reads and assert the counter
    sees it. Guards against a profile that is all zeroes because the event
    key drifted rather than because the riders are dead."""
    enemies = [make_enemy(hp=200)]
    state = make_state(enemies=enemies)
    reactions.apply_aura(state, enemies[0], "hydro", "apply_aura_op")
    card = Card(id="probe_payoff", name="Probe", type="attack", cost=1,
                element="pyro",
                effects=[{"op": "damage", "amount": 6, "target": "enemy",
                          "applies_element": True},
                         {"op": "conditional",
                          "if": "reaction_triggered_by_this",
                          "then": [{"op": "block", "amount": 3}]}])
    effects.resolve_card(state, card)
    stats = metrics.extract(state, state.player.hp)
    assert stats.conditional_evaluated["reaction_triggered_by_this"] == 1
    assert stats.conditional_fired["reaction_triggered_by_this"] == 1


# --- merge: a gauntlet is one fight ---------------------------------------

def test_gauntlet_merge_adds_the_counters_key_wise():
    a = metrics.FightStats(
        won=True, turns=3, hp_start=80, hp_end=70, total_damage_dealt=30,
        damage_by_turn={1: 30}, energy_by_turn={}, total_block_gained=0,
        damage_blocked=0, energy_spent=0, cards_drawn_extra=0,
        energy_generated_extra=0, healing=0, encore_absorbed=0,
        debuff_stacks_applied=0, debuffed_intents=0, aura_intents=0,
        total_intents=0, reactions=1, reaction_damage=0, auras_wasted=0,
        aura_ops={"swirl": 2}, aura_applications_by_source={"hit": 3},
        aura_applications_by_element={"pyro": 3},
        reactions_by_name={"overload": 1},
        conditional_evaluated={"reaction_triggered_by_this": 4},
        conditional_fired={"reaction_triggered_by_this": 1})
    b = metrics.FightStats(
        won=True, turns=2, hp_start=70, hp_end=60, total_damage_dealt=20,
        damage_by_turn={1: 20}, energy_by_turn={}, total_block_gained=0,
        damage_blocked=0, energy_spent=0, cards_drawn_extra=0,
        energy_generated_extra=0, healing=0, encore_absorbed=0,
        debuff_stacks_applied=0, debuffed_intents=0, aura_intents=0,
        total_intents=0, reactions=2, reaction_damage=0, auras_wasted=0,
        aura_ops={"swirl": 1, "apply_aura": 5},
        aura_applications_by_source={"hit": 1, "swirl_spread": 2},
        aura_applications_by_element={"pyro": 1, "cryo": 2},
        reactions_by_name={"overload": 1, "melt": 1},
        conditional_evaluated={"reaction_triggered_by_this": 2,
                               "has_spark": 1},
        conditional_fired={"has_spark": 1})
    m = metrics.merge_stages([a, b])
    assert m.aura_ops == {"swirl": 3, "apply_aura": 5}
    assert m.aura_applications_by_source == {"hit": 4, "swirl_spread": 2}
    assert m.aura_applications_by_element == {"pyro": 4, "cryo": 2}
    assert m.reactions_by_name == {"overload": 2, "melt": 1}
    assert m.conditional_evaluated == {"reaction_triggered_by_this": 6,
                                       "has_spark": 1}
    assert m.conditional_fired == {"reaction_triggered_by_this": 1,
                                   "has_spark": 1}
    assert m.aura_applications == 6
