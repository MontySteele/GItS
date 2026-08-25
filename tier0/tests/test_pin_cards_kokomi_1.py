"""Behaviour pins for the Kokomi sheet cards (block/conscript/Sly/
exhaust-funnel commons, plus the EB-125 ratified bodies) that no other test
file exercises.

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


def test_salvage_the_line_costs_one_and_pays_charge_beside_its_block():
    """`shell_of_sanctuary` was the 2-cost big wall -- 11 Block, no rider.
    W3 (EB-118 Phase 3, R211) rewrote it as "Salvage the Line", KEEPING THE
    ID: cost 2 -> 1, Block 11 -> 4, with a draw, an Exhaust retrieval and a
    Charge line around it.

    This pin is the SLOT, not the retrieval -- the ruled effect ORDER and the
    empty-pile behaviour are pinned in test_eb118_w3_bodies.py, beside the
    ruling that settled them. What belongs here is that the row now costs one
    energy and pays a Charge, which is the arithmetic the rest of this file
    reads."""
    st = kokomi_state()
    play(st, "shell_of_sanctuary")
    assert st.player.block == 4
    assert st.player.energy == 2
    # THREE, not the printed two: the row Exhausts itself and Kokomi's
    # CHARGE_PER_EXHAUST funnel pays the third. That is inherited behaviour
    # rather than anything W3 printed, and it is asserted here so the printed
    # line and the funnel stay separable if either ever moves.
    assert st.player.charge == 3


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

def test_moon_signal_throws_a_chosen_card_and_recalls_one_to_draw():
    """A Moment Alone costs 0: it discards a card you PICK, then puts a card
    from the discard pile on TOP of the draw pile (EB-125 / R202).

    The hand economy is deliberately negative -- the card played and the card
    thrown both leave, and nothing arrives in hand. `_best_card` prefers a
    real Attack, so the seeded Water's Edge is what comes back rather than the
    card just thrown."""
    st = kokomi_state(draw_pile=["coral_guard"])
    st.player.discard_pile.append(loader.get_card("waters_edge"))
    play(st, "moon_signal", hand=["jade_bulwark"], energy=0)
    assert st.player.energy == 0
    assert st.player.hand == []
    assert [c.id for c in st.player.draw_pile] == ["waters_edge",
                                                   "coral_guard"]
    assert [c.id for c in st.player.discard_pile] == ["jade_bulwark",
                                                      "moon_signal"]


def test_moon_signal_recalls_the_card_it_just_threw_on_an_empty_pile():
    """The discard branch of `recall_to_draw` is UNFILTERED (the D3
    self-recall contract, R198), so with nothing else in the pile the card you
    just threw is the only candidate and returns to the top of the draw pile.
    A known consequence of the ratified body, pinned so it stays deliberate."""
    st = kokomi_state(draw_pile=["coral_guard"])
    play(st, "moon_signal", hand=["jade_bulwark"], energy=0)
    assert [c.id for c in st.player.draw_pile] == ["jade_bulwark",
                                                   "coral_guard"]
    assert [c.id for c in st.player.discard_pile] == ["moon_signal"]


def test_moon_signal_upgrade_buys_retain_and_moves_no_effect():
    """The ratified upgrade is `{retain: true}`: it sets a card FIELD and
    inserts nothing, so the printed order is identical between the faces --
    which is the whole reason a draw was refused (an appended draw would take
    back exactly the card the recall placed)."""
    base = loader.get_card("moon_signal")
    up = loader.get_card("moon_signal+")
    assert not base.retain and up.retain
    assert base.effects == up.effects
    assert [fx["op"] for fx in up.effects] == ["discard", "recall_to_draw"]


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
    # Seeded so Moon Signal's recall takes the Attack rather than the Charm it
    # just threw -- the Sly rider is what this pin is about.
    st.player.discard_pile.append(loader.get_card("waters_edge"))
    play(st, "moon_signal", hand=["driftwood_charm"], energy=0)
    assert st.player.charge == 2
    assert "driftwood_charm" in [c.id for c in st.player.discard_pile]


# --- EB-125 ratified bodies (R202): Crane Wing and Tighten the Cords ---

def test_crane_wing_gains_four_block_and_discounts_companions_this_turn():
    """Crane Wing surrenders immediate Block to keep its discount identity
    (EB-125 / R202): 4 Block, and Companion cards cost 1 less this turn. That
    is two under jade_bulwark's printed Block, which is what separates the
    pair on what each card is FOR rather than on a number."""
    st = kokomi_state()
    play(st, "crane_wing")
    assert st.player.block == 4
    assert st.player.energy == 2
    assert loader.get_card("jade_bulwark").effects[0]["amount"] > 4


def test_crane_wing_upgrade_reaches_jade_bulwarks_printed_block():
    """`{block: +2}` is unchanged; the base moved, so the upgraded Crane lands
    level with Pearl Bulwark's PRINTED face instead of above it."""
    up = loader.get_card("crane_wing+")
    assert up.effects[0]["amount"] == 6 == loader.get_card(
        "jade_bulwark").effects[0]["amount"]
    assert up.effects[1]["delta"] == -1        # cost_mod may not deepen


def test_tighten_the_cords_pays_metallicize_only_over_the_exhaust_bar():
    """The ratified body gates the Metallicize on the exhaust pile, which is
    what separates it from gorou_heart_of_the_clan's unconditional stack. The
    Block half is always live."""
    st = kokomi_state()
    play(st, "tighten_the_cords")
    assert st.player.block == 5
    assert "metallicize" not in st.player.powers

    st = kokomi_state()
    for _ in range(3):
        st.player.exhaust_pile.append(loader.get_card("coral_guard"))
    play(st, "tighten_the_cords")
    assert st.player.block == 5
    assert st.player.powers["metallicize"] == 1


def test_tighten_the_cords_upgrade_moves_the_always_live_half():
    """R58: on a threshold card the always-live half moves and the bar cannot
    drift down. Here that is the Block (5 -> 7); the exhaust bar stays put."""
    up = loader.get_card("tighten_the_cords+")
    assert up.effects[0] == {"op": "block", "amount": 7}
    assert up.effects[1]["if"] == "exhaust_pile_at_least_3"
    assert up.effects[1]["then"][0]["amount"] == 1
    assert up.archetypes == ["priest"] and up.role == "payoff"


# --- R208 / W2b ratified bodies: Undertow and Sango Isshin ---

def test_undertow_keeps_its_slope_and_draws_over_the_exhaust_bar():
    """The R208 revision is EXACTLY two changes on a card that keeps its
    shape: formula base 4 -> 5, and an `exhaust_pile_at_least_3` draw
    appended. The slope, the Sly energy rider and the labels are untouched,
    and the U-A access rewrite that would have replaced the slope with a bar
    was rejected under R199's no-label-for-count guardrail."""
    shallow = kokomi_state(draw_pile=["coral_guard"])
    shallow.player.exhaust_pile.append(loader.get_card("coral_guard"))
    play(shallow, "undertow")
    assert shallow.enemies[0].hp == 300 - (5 + 1)     # base 5, pile 1
    assert shallow.player.hand == []                  # no draw under the bar

    deep = kokomi_state(draw_pile=["coral_guard"])
    for _ in range(3):
        deep.player.exhaust_pile.append(loader.get_card("coral_guard"))
    play(deep, "undertow")
    assert deep.enemies[0].hp == 300 - (5 + 3)        # base 5, pile 3
    assert [c.id for c in deep.player.hand] == ["coral_guard"]

    card = loader.get_card("undertow")
    assert card.sly == [{"op": "energy", "amount": 1}]
    assert card.archetypes == ["assist"] and card.role == "payoff"


def test_undertow_upgrade_still_buys_the_base_not_the_slope():
    """`{formula_base: +3}` is UNCHANGED by the revision; the printed base
    moved under it, so the upgraded face reads 8 + 1 per exhausted card and
    the bar-3 draw rides along untouched."""
    up = loader.get_card("undertow+")
    assert up.effects[0]["amount_formula"] == {"base": 8, "per": 1,
                                               "count": "exhaust_pile"}
    assert up.effects[1] == {"op": "conditional",
                             "if": "exhaust_pile_at_least_3",
                             "then": [{"op": "draw", "amount": 1}]}
    assert up.sly == [{"op": "energy", "amount": 1}]


def test_sango_isshin_buys_a_wall_only_over_an_eight_deep_pile():
    """R208's W2b body takes the DIVIDEND job: the Rare stops being a fourth
    slope over one count and makes the pile pay something other than damage.
    Below the bar it is a flat 14; at eight exhausted cards it also walls for
    8. The bar is 8 by R209 (2026-08-25): the ratified 6 fired on 38.4% of
    clean priest attack plays -- a regular feature -- where 8 fires 24.2%,
    the earned-moment rate the ratification described."""
    shallow = kokomi_state()
    for _ in range(7):
        shallow.player.exhaust_pile.append(loader.get_card("coral_guard"))
    play(shallow, "depths_judgment")
    assert shallow.enemies[0].hp == 286
    assert shallow.player.block == 0

    deep = kokomi_state()
    for _ in range(8):
        deep.player.exhaust_pile.append(loader.get_card("coral_guard"))
    play(deep, "depths_judgment")
    assert deep.enemies[0].hp == 286               # damage no longer scales
    assert deep.player.block == 8


def test_sango_isshin_upgrade_moves_the_always_live_damage():
    """`{damage: +4}` replaces the retired `{formula_per: +1}`: the flat 14
    -> 18, and under R58 the bar cannot drift down on upgrade."""
    up = loader.get_card("depths_judgment+")
    assert up.effects[0] == {"op": "damage", "amount": 18, "target": "enemy"}
    assert up.effects[1]["if"] == "exhaust_pile_at_least_8"
    assert up.effects[1]["then"] == [{"op": "block", "amount": 8}]
    assert up.archetypes == ["priest"] and up.role == "payoff"


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
