"""Behaviour pins for fourteen Kokomi sheet cards (block/conscript/Sly/
exhaust-funnel commons) that no other test file exercises.

Each test builds a minimal Kokomi combat, plays exactly one card, and
asserts the observable result the engine produces today: Block gained,
damage dealt, cards moved between piles, and Charge/Burst income.
"""

import random

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat
from tier0.engine.state import CombatState
from tier0.tests.conftest import make_enemy

INAZUMA_COSTS = {c.id: c.cost for c in loader.companion_pool("inazuma")}


def kokomi_state(enemies=None, seed=0, draw_pile=()):
    """Kokomi in combat with an explicit draw pile (no reshuffle surprises)."""
    p = loader.build_player("kokomi")
    p.draw_pile = [loader.get_card(cid) for cid in draw_pile]
    return CombatState(player=p, enemies=enemies or [make_enemy(hp=300)],
                       rng=random.Random(seed))


def play(state, card_id, hand=(), energy=3):
    """Put `hand` plus the card under test into hand and play the card."""
    for cid in hand:
        state.player.hand.append(loader.get_card(cid))
    card = loader.get_card(card_id)
    state.player.hand.append(card)
    state.player.energy = energy
    combat.play_card(state, card)
    return card


# --- plain Block bodies ---

def test_coral_guard_gains_five_block():
    """Coral Guard is a 1-cost skill that grants 5 Block and nothing else."""
    st = kokomi_state()
    play(st, "coral_guard")
    assert st.player.block == 5
    assert st.player.energy == 2
    assert st.player.charge == 0
    assert [c.id for c in st.player.discard_pile] == ["coral_guard"]


def test_jade_bulwark_gains_six_block():
    """Pearl Bulwark is a 1-cost skill that grants 6 Block and nothing else."""
    st = kokomi_state()
    play(st, "jade_bulwark")
    assert st.player.block == 6
    assert st.player.energy == 2
    assert st.player.hand == []


def test_shell_of_sanctuary_gains_eleven_block():
    """Shell of Sanctuary is the 2-cost big wall: 11 Block, no rider."""
    st = kokomi_state()
    play(st, "shell_of_sanctuary")
    assert st.player.block == 11
    assert st.player.energy == 1
    assert st.player.charge == 0


# --- attack ---

def test_vow_of_tides_hits_every_enemy_and_exhausts_itself():
    """Vow of the Tides deals 8 to EVERY living enemy, applies Kokomi's
    catalyst hydro aura to each, and Exhausts itself — and that self-exhaust
    pays through the Charge funnel."""
    st = kokomi_state(enemies=[make_enemy(hp=300, name="a"),
                               make_enemy(hp=300, name="b")])
    play(st, "vow_of_tides")
    assert [e.hp for e in st.enemies] == [292, 292]
    assert [e.aura for e in st.enemies] == ["hydro", "hydro"]
    assert [c.id for c in st.player.exhaust_pile] == ["vow_of_tides"]
    assert st.player.discard_pile == []
    assert st.player.charge == C.CHARGE_PER_EXHAUST
    assert st.player.burst_energy == C.KOKOMI_BURST_PER_EXHAUST


# --- conscript family ---

def test_conscription_notice_transforms_a_card_and_replaces_itself():
    """Call to Arms turns one card in hand into a random Inazuma recruit
    (cheaper by the conscript delta, Exhaust-flagged) and then draws 1, so
    hand size is unchanged by the transform and grows by the draw."""
    st = kokomi_state(draw_pile=["coral_guard"])
    play(st, "conscription_notice", hand=["jade_bulwark"])
    recruit, drawn = st.player.hand
    assert drawn.id == "coral_guard"
    assert recruit.id in INAZUMA_COSTS
    assert recruit.is_companion and recruit.conscripted and recruit.exhaust
    assert recruit.cost == max(0, INAZUMA_COSTS[recruit.id]
                               + C.CONSCRIPT_COST_DELTA)
    # net deck delta of the transform itself is zero: jade_bulwark is gone
    # from every pile, not moved to one.
    assert "jade_bulwark" not in [c.id for c in st.player.discard_pile]
    assert "jade_bulwark" not in [c.id for c in st.player.exhaust_pile]


def test_to_the_front_conscripts_for_free():
    """To the Front! costs 0 energy and its whole body is one conscript:
    the card in hand is replaced in place, with no draw and no Block."""
    st = kokomi_state()
    play(st, "to_the_front", hand=["jade_bulwark"], energy=0)
    assert st.player.energy == 0
    (recruit,) = st.player.hand
    assert recruit.id in INAZUMA_COSTS
    assert recruit.conscripted and recruit.exhaust
    assert st.player.block == 0


def test_standing_orders_conscripts_and_gains_four_block():
    """Standing Orders is the armoured conscript: one transform in hand plus
    4 Block, no draw."""
    st = kokomi_state()
    play(st, "standing_orders", hand=["jade_bulwark"])
    assert st.player.block == 4
    (recruit,) = st.player.hand
    assert recruit.id in INAZUMA_COSTS
    assert recruit.conscripted and recruit.exhaust


def test_mass_mobilization_conscripts_twice_and_grants_charge():
    """Rally the Isles costs 2 and transforms TWO cards in hand into recruits,
    plus 1 bonus Charge."""
    st = kokomi_state()
    play(st, "mass_mobilization", hand=["jade_bulwark", "shell_of_sanctuary"])
    assert st.player.energy == 1
    assert len(st.player.hand) == 2
    for recruit in st.player.hand:
        assert recruit.id in INAZUMA_COSTS
        assert recruit.conscripted and recruit.exhaust
    assert st.player.charge == 1


def test_field_promotion_conscripts_at_cost_zero_and_draws():
    """Field Promotion's recruit arrives at cost 0 outright — the printed
    cost of the pulled companion is overridden, not merely discounted — and
    the card replaces itself with a draw."""
    seen_expensive = False
    for seed in range(12):
        st = kokomi_state(seed=seed, draw_pile=["coral_guard"])
        play(st, "field_promotion", hand=["jade_bulwark"])
        recruit, drawn = st.player.hand
        assert drawn.id == "coral_guard"
        assert recruit.id in INAZUMA_COSTS
        assert recruit.conscripted and recruit.exhaust
        assert recruit.cost == 0
        if INAZUMA_COSTS[recruit.id] >= 2:
            seen_expensive = True
    # a printed-2 recruit landing at 0 is what separates the override from
    # the ordinary -1 conscript delta.
    assert seen_expensive


# --- Sly / discard lane ---

def test_moon_signal_discards_then_draws_for_free():
    """A Moment Alone costs 0: it discards a card from hand at random and
    then draws one, so hand size is unchanged."""
    st = kokomi_state(draw_pile=["coral_guard"])
    play(st, "moon_signal", hand=["jade_bulwark"], energy=0)
    assert st.player.energy == 0
    assert [c.id for c in st.player.hand] == ["coral_guard"]
    assert [c.id for c in st.player.discard_pile] == ["jade_bulwark",
                                                      "moon_signal"]


def test_rearguard_action_discards_a_card_for_seven_block():
    """Rearguard Action pays a random discard from hand and gives 7 Block."""
    st = kokomi_state()
    play(st, "rearguard_action", hand=["jade_bulwark"])
    assert st.player.block == 7
    assert st.player.hand == []
    assert [c.id for c in st.player.discard_pile] == ["jade_bulwark",
                                                      "rearguard_action"]


def test_driftwood_charm_blocks_and_draws_and_its_sly_pays_charge():
    """Driftwood Charm gives 3 Block and draws 1 when played; when it is
    instead DISCARDED from hand its Sly rider grants 2 Charge."""
    st = kokomi_state(draw_pile=["coral_guard"])
    play(st, "driftwood_charm")
    assert st.player.block == 3
    assert [c.id for c in st.player.hand] == ["coral_guard"]
    assert st.player.charge == 0        # the Sly rider does NOT fire on play

    st = kokomi_state(draw_pile=["coral_guard", "coral_guard"])
    play(st, "moon_signal", hand=["driftwood_charm"], energy=0)
    assert st.player.charge == 2
    assert "driftwood_charm" in [c.id for c in st.player.discard_pile]


# --- priest exhaust lane ---

def test_votive_offering_exhausts_a_chosen_card_for_five_block():
    """Votive Offering exhausts one chosen card out of hand and grants 5
    Block; the exhaust itself feeds the Charge funnel."""
    st = kokomi_state()
    play(st, "votive_offering", hand=["jade_bulwark"])
    assert st.player.block == 5
    assert [c.id for c in st.player.exhaust_pile] == ["jade_bulwark"]
    assert st.player.hand == []
    assert st.player.charge == C.CHARGE_PER_EXHAUST
    assert st.player.burst_energy == C.KOKOMI_BURST_PER_EXHAUST


def test_ritual_purification_exhausts_for_five_total_charge_and_draws():
    """Ritual Purification exhausts a chosen card (1 Charge through the
    funnel), grants 4 more Charge on its own line for 5 total, and draws 1."""
    st = kokomi_state(draw_pile=["coral_guard"])
    play(st, "ritual_purification", hand=["jade_bulwark"])
    assert st.player.charge == C.CHARGE_PER_EXHAUST + 4
    assert [c.id for c in st.player.exhaust_pile] == ["jade_bulwark"]
    assert [c.id for c in st.player.hand] == ["coral_guard"]
    assert st.player.burst_energy == C.KOKOMI_BURST_PER_EXHAUST
    assert st.player.block == 0
