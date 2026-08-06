"""Track O slice 08 pins: GRANTED PLAYS against the Track D / Track H counters.

Family A (`docs/archive/s7-probe-c.md`) was an after-state gate in `understudy/soak.py`
that dropped a play whose resolution moved the state off a plain combat screen
-- so overlay plays and killing blows were never written down. The obvious
place for a cousin is the GRANTED play: a card played by another card's effect
rather than from hand, which resolves in the middle of the granting card.

These pins record the answer this slice measured: on the tier 0 side there is
no cousin. Every Track D (D1 reaction split) and Track H (H1 aura provenance,
H2 payoff predicates) counter is read by `metrics.extract` off the event log,
and `combat.resolve_free_play` emits the same events a manual play does. The
pins exist because that equality is load-bearing and invisible: a granted play
routed around `_finish_play`, or a `play` event emitted without `free=True`, or
a killing granted play short-circuited before its emit, would each change a
published cohort number with nothing going red.

Source of truth for every assertion below, cited before it was pinned:
`effects._free_play`'s CONTRACT docstring (items 1, 4 and 5) and
`combat.resolve_free_play`'s own docstring -- "the base game runs an auto-play
through the same CardModel.OnPlayWrapper as a manual play, so an auto-played
card ... is recorded by History as a card play".
"""

from __future__ import annotations

import random

from tier0.engine import combat, reactions
from tier0.engine.state import Card, CombatState, Enemy, Player
from tier0.harness import metrics

# Every counter Track D and Track H added to FightStats, plus the two older
# fields a free play is allowed to differ on.
D_AND_H = ("reactions", "reaction_damage_amp", "reaction_damage_splash",
           "reaction_damage_dot", "aura_ops", "aura_applications_by_source",
           "aura_applications_by_element", "reactions_by_name",
           "conditional_evaluated", "conditional_fired")


def _probe_card(cid: str = "probe") -> Card:
    """One card that exercises all three instruments at once: an element-tagged
    attack (D1 amp + H1 `hit` provenance), an aura VERB (H1 `aura_ops`), and a
    payoff conditional (H2)."""
    return Card(id=cid, name=cid, type="attack", cost=1, element="pyro",
                effects=[
                    {"op": "damage", "amount": 8, "target": "enemy",
                     "applies_element": True},
                    {"op": "apply_aura", "element": "hydro",
                     "target": "enemy"},
                    {"op": "conditional", "if": "reaction_triggered_by_this",
                     "then": [{"op": "block", "amount": 3}]},
                ])


def _state(enemy_hp: int = 10_000) -> CombatState:
    st = CombatState(
        player=Player(hp=80, max_hp=80),
        enemies=[Enemy(hp=enemy_hp, max_hp=enemy_hp, name="dummy",
                       intents=[{"kind": "attack", "amount": 0}])],
        rng=random.Random(0))
    st.player.energy = 3
    st.player.element = "pyro"
    st.player.cadence = "catalyst"
    return st


def test_a_granted_play_moves_every_track_d_and_h_counter_like_a_hand_play():
    """`resolve_free_play`'s docstring: an auto-play runs through the same
    wrapper as a manual play and "is recorded by History as a card play". So
    the two paths must produce the same reaction split, the same aura
    provenance and the same payoff evaluations from the same card -- the
    ONLY difference being the cost bookkeeping the contract says is skipped
    (item 1: "no energy deduction").
    """
    manual = _state()
    reactions.apply_aura(manual, manual.enemies[0], "hydro")
    card = _probe_card()
    manual.player.hand = [card]
    combat.play_card(manual, card)
    m = metrics.extract(manual, hp_start=80)

    granted = _state()
    reactions.apply_aura(granted, granted.enemies[0], "hydro")
    combat.resolve_free_play(granted, _probe_card())
    g = metrics.extract(granted, hp_start=80)

    # The card really did exercise all three instruments, or the pin is vacuous.
    assert m.reactions == 1 and m.reaction_damage_amp > 0
    assert m.aura_ops and m.conditional_evaluated

    for field in D_AND_H:
        assert getattr(m, field) == getattr(g, field), field
    assert m.total_damage_dealt == g.total_damage_dealt
    assert m.cards_played == g.cards_played == 1
    # ...and the declared difference, in the declared direction.
    assert m.energy_spent == 1 and g.energy_spent == 0


def test_a_granted_play_is_one_play_event_carrying_the_free_flag():
    """Contract item 5: a free play "increment[s] cards_played_this_turn and
    emit[s] play(cost=0, free=True), so MAX_CARDS_PER_TURN can see free
    plays". Both halves matter downstream: `metrics.cards_played` counts
    `play` events, and `free` is the only thing in the record that separates
    a granted play from a 0-cost one.
    """
    st = _state()
    combat.resolve_free_play(st, _probe_card("granted"))

    plays = [e for e in st.log if e["event"] == "play"]
    assert len(plays) == 1
    assert plays[0]["card"] == "granted"
    assert plays[0]["cost"] == 0
    assert plays[0]["free"] is True
    assert st.cards_played_this_turn == 1
    assert metrics.extract(st, hp_start=80).cards_played == 1


def test_one_grantor_of_three_plays_is_four_plays_and_three_of_each_rider():
    """`_op_autoplay_from_draw` is Cascade's shape: it queues N cards and then
    plays each through `_free_play`. Four cards were played, so
    `cards_played` is 4 -- and each granted card's own riders fire once per
    grant, which is what makes `aura_ops` and `conditional_evaluated`
    per-resolution counts rather than per-hand-play counts.
    """
    st = _state()
    reactions.apply_aura(st, st.enemies[0], "hydro")
    st.player.draw_pile = [_probe_card(f"granted{i}") for i in range(3)]
    grantor = Card(id="grantor", name="Grantor", type="skill", cost=1,
                   effects=[{"op": "autoplay_from_draw", "amount": 3}])
    st.player.hand = [grantor]
    combat.play_card(st, grantor)

    s = metrics.extract(st, hp_start=80)
    assert s.cards_played == 4
    assert [e.get("free", False) for e in st.log if e["event"] == "play"] == \
        [False, True, True, True]
    assert s.aura_ops == {"apply_aura": 3}
    assert s.conditional_evaluated == {"reaction_triggered_by_this": 3}
    assert s.reactions_by_name == {"vaporize": 3}


def test_a_granted_play_that_lands_the_killing_blow_is_still_recorded():
    """Family A's exact case, on the granted path: the play that ends the
    fight. `metrics.extract` reads a log the fight's end cannot retract, so
    the killing granted play keeps its `play` row and its damage -- which is
    the property `understudy/soak.py`'s R101/1b fix had to be changed to get.
    """
    st = _state(enemy_hp=6)
    combat.resolve_free_play(st, _probe_card("finisher"))

    assert st.over
    s = metrics.extract(st, hp_start=80)
    assert s.cards_played == 1
    assert [e["card"] for e in st.log if e["event"] == "play"] == ["finisher"]
    # Overkill stays clamped out of the accounting (the EPOCH 1 rule).
    assert s.total_damage_dealt == 6
