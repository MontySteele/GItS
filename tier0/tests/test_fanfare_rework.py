"""Engine pins for the Fanfare rework (2026-07-28), Tracks C and D.

Track A and Track B's gates live in test_furina.py beside the resource tests
they extend; this file covers the three card redesigns and the bow probe --
the mechanics that did not exist before this sprint.

THE NEGATIVE FLOOR is the load-bearing one. The Final Verdict digs the floor
out from under the meter, which is RULED, and the PROPOSED semantics are that
readers clamp at zero so effects shut off rather than invert. Every reader
therefore has to be pinned, not just the one the card obviously touches --
a rider that paid negative damage would be an attack that heals the enemy,
and a Focus term that went negative would chip her own stage.
"""

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, effects, resources
from tier0.engine.state import Card, CombatState
from tier0.tests.conftest import make_enemy


def furina_state(enemies=None, seed=0):
    p = loader.build_player("furina")
    return CombatState(player=p, enemies=enemies or [make_enemy(hp=300)],
                       rng=random.Random(seed))


def _card(**kw):
    d = dict(id="fr_test", name="t", cost=0, type="skill",
             character="furina")
    d.update(kw)
    return Card(**d)


# ======================================================================
# Track C.2 -- the Hyperbeam and the negative floor
# ======================================================================

def test_the_hyperbeam_reads_the_meter_then_crashes_it():
    """The card's whole shape in one play: damage equal to Fanfare, and then
    a house that is quieter than it started.

    ORDER IS THE POINT. If the crash resolved first the card would always
    deal zero, so this asserts the damage NUMBER rather than just that the
    floor moved -- the failure mode is silent and arithmetically total.
    """
    st = furina_state()
    p = st.player
    resources.gain_fanfare(st, 24, "test")
    hp0 = st.enemies[0].hp

    p.hand.append(loader.get_card("the_final_verdict"))
    p.energy = 3
    combat.play_card(st, p.hand[-1])

    assert hp0 - st.enemies[0].hp == 24
    assert p.fanfare_floor == -30
    assert p.fanfare == -30


def test_the_floor_goes_negative_and_decay_clamps_to_it():
    """RULED: the floor may go below zero, and it is a hole rather than a
    reset. Decay's floor clamp is what makes it a hole -- without it the
    meter would drift back to 0 on its own and the price would be free."""
    st = furina_state()
    p = st.player
    resources.drop_fanfare_to_floor(st, 18, "test")
    assert (p.fanfare, p.fanfare_floor) == (-18, -18)

    for turn in range(2, 8):
        st.turn = turn
        resources.decay_fanfare(st)
    assert p.fanfare == -18, "decay must not drift a negative meter upward"


def test_generation_climbs_out_of_the_hole():
    """The other half of "a hole the player climbs out of": activity has to
    actually count against the debt, or the card is a combat-ending cost
    rather than a priced one."""
    st = furina_state()
    p = st.player
    resources.drop_fanfare_to_floor(st, 10, "test")

    resources.gain_fanfare(st, 4, "test")
    assert p.fanfare == -6
    resources.gain_fanfare(st, 20, "test")
    assert p.fanfare == 14


@pytest.mark.parametrize("meter", [-25, -1, 0])
def test_every_reader_clamps_at_zero(meter):
    """PROPOSED semantics (Track C.2), pinned across ALL FOUR readers.

    Parametrized over the boundary rather than one value: -1 and 0 are where
    a `max(0, x)` and a bare `x` stop agreeing, and -25 is the realistic
    post-Hyperbeam depth. A reader that inverted instead of shutting off
    would show up as negative damage, negative Block, a chipped stage, or a
    threshold that passes while the house is silent.
    """
    st = furina_state()
    p = st.player
    p.fanfare_floor = min(0, meter)
    p.fanfare = meter

    # 1. bonus_formula on damage/block -- an attack that healed the enemy.
    assert effects._bonus_formula(st, "1_per_2_fanfare") == 0
    # 2. the Salon Focus term -- members must not chip the stage.
    assert effects._salon_amount(st, 6) == 6
    # 3. the fanfare_at_least predicate.
    assert effects._predicate(st, "fanfare_at_least_1") is False
    # 4. Rapturous Applause's attack-power read.
    p.powers["fanfare_attack_per10"] = 2
    attack = Card(id="fr_hit", name="t", cost=1, type="attack",
                  character="furina",
                  effects=[{"op": "damage", "amount": 5, "target": "enemy"}])
    assert effects.flat_attack_bonus(st, attack, cost=1) == 0


def test_a_positive_meter_is_unaffected_by_the_clamp():
    """The control. `readable` must be identity above zero, or the clamp
    quietly re-prices every card in the pool that reads Fanfare."""
    st = furina_state()
    st.player.fanfare = 27
    assert resources.readable(st.player) == 27
    assert effects._bonus_formula(st, "1_per_2_fanfare") == 13
    assert effects._salon_amount(st, 6) == 6 + 27 // C.SALON_FOCUS_PER


def test_the_crash_does_not_lower_the_cap():
    """Deliberate, and stated on the sheet: the floor falling is the price.
    A ceiling that fell too would make the SECOND cast in a combat quietly
    worse than the first, which is a different card than the one ruled."""
    st = furina_state()
    cap0 = st.player.fanfare_cap
    resources.drop_fanfare_to_floor(st, 30, "test")
    assert st.player.fanfare_cap == cap0


def test_the_pilot_reads_the_clamped_meter_too():
    """THE PILOT'S COPY of the predicate, which is a SECOND implementation.

    `policy._active_effects` re-implements `fanfare_at_least_*` so it can
    forecast which branch a conditional will take before playing the card.
    Two implementations of one rule is two chances to disagree, and this one
    is easy to forget because nothing in the engine's own test suite touches
    it.

    IT WAS ALSO A REAL BUG, caught by the sprint's own battery and not by any
    unit test: routing the pilot through `resources.readable` left
    `resources` unimported in policy.py, so every run holding a Fanfare
    conditional died with `NameError` inside a worker process. Nothing at
    import time noticed, because the name is only touched on the branch a
    Furina deck with a threshold card reaches. This test walks that branch.
    """
    from tier0.pilot import policy

    st = furina_state()
    p = st.player
    gated = _card(effects=[{"op": "conditional", "if": "fanfare_at_least_5",
                            "then": [{"op": "block", "amount": 9}]}])

    p.fanfare = 12
    assert [fx["op"] for fx in policy._active_effects(st, gated.effects)] \
        == ["block"]

    # Below the bar, and BELOW ZERO. The negative case is the one the clamp
    # exists for: an unclamped `>=` comparison happens to give the same
    # answer here, so this pins the import path and the semantics together.
    p.fanfare_floor, p.fanfare = -30, -30
    assert list(policy._active_effects(st, gated.effects)) == []


# ======================================================================
# Track C.1 -- Slip Backstage, the spender
# ======================================================================

def test_slip_backstage_converts_the_buffer_and_prints_fanfare_for_it():
    """The card is three things at once and the sprint priced it as three:
    Block, an Encore sink, and -- under Track A -- a Fanfare source, because
    the spend itself is a reduction."""
    st = furina_state()
    p = st.player
    p.encore = 12
    p.hand.append(loader.get_card("graceful_retreat"))
    p.energy = 3
    combat.play_card(st, p.hand[-1])

    assert (p.encore, p.block) == (7, 10)
    assert p.fanfare == 5 * C.FANFARE_PER_ENCORE_SPENT


def test_slip_backstage_on_an_empty_buffer_costs_true_hp_and_still_pays():
    """The risk line, and why the card uses spend_encore (the OVERDRAW
    primitive) rather than an encore_cost gate: it is always PLAYABLE, and
    playing it dry is a decision with a price rather than a dead card.

    The wound itself prints Fanfare through the hp_lost leg, so the two
    payment routes both pay -- which is the Track A invariant showing up
    somewhere it was not designed for.
    """
    st = furina_state()
    p = st.player
    p.encore = 0
    p.hand.append(loader.get_card("graceful_retreat"))
    p.energy = 3
    combat.play_card(st, p.hand[-1])

    assert p.block == 10
    assert p.hp == p.max_hp - 5
    assert p.fanfare == 5 * C.FANFARE_PER_HP_LOST


def test_slip_backstage_retains():
    """Retain is what makes the sink schedulable -- she holds it until the
    buffer is deep enough to pay without the wound. Asserted on the card
    rather than through a turn cycle so a codegen or loader regression that
    dropped the field fails HERE and not as a subtle pilot behaviour."""
    assert loader.get_card("graceful_retreat").retain is True


# ======================================================================
# Track C.3 -- Blocking Notes, the Companion slope
# ======================================================================

def test_blocking_notes_scales_with_companions_played_this_turn():
    st = furina_state()
    st.companion_plays_this_turn = 3
    card = loader.get_card("blocking_notes")
    effects.resolve_card(st, card)
    assert st.player.block == 5 + 2 * 3


def test_the_companion_count_is_per_turn_not_per_combat():
    """`companions_played` (per combat) already existed and is NOT what this
    reads. A slope that counted the whole combat would make the card a
    late-fight blowout instead of a tempo payoff, and the two fields look
    close enough that the wrong one is an easy mistake."""
    st = furina_state()
    st.companions_played = ["a", "b", "c", "d"]
    st.companion_plays_this_turn = 1
    effects.resolve_card(st, loader.get_card("blocking_notes"))
    assert st.player.block == 5 + 2


def test_a_generated_guest_star_counts_toward_the_slope():
    """THE RULING, pinned. B2's lesson -- a cost-<=0 play neither benefits
    nor consumes -- is about DISCOUNTS. This is a PAYOFF, and a payoff blind
    to generated Companions would punish the deck that generates them.

    Driven through play_card so the counter is exercised at its real site
    rather than by setting the field, which is the only way this test can
    disagree with the engine.
    """
    st = furina_state()
    p = st.player
    token = loader.get_card("chevreuse_interdiction_fire")
    assert token.is_companion
    token.cost = 0                      # as a generated token would arrive
    p.hand.append(token)
    p.energy = 3
    combat.play_card(st, token)

    assert st.companion_plays_this_turn == 1


def test_the_companion_count_resets_each_turn():
    st = furina_state()
    st.companion_plays_this_turn = 4
    combat._player_turn(st, lambda *a, **k: None)
    assert st.companion_plays_this_turn == 0


# ======================================================================
# Track D -- the on-demand bow probe
# ======================================================================

def test_the_bow_probe_bows_the_LEFTMOST_member():
    """Leftmost is the same end of the FIFO queue a deploy into a full stage
    displaces, so the card teaches no new rule. Asserted with a stage whose
    members are DISTINCT -- with three Crabalettas any pop looks correct.
    """
    st = furina_state()
    p = st.player
    p.salon = ["chevalmarin", "usher", "crabaletta"]
    p.powers["salon_member"] = 3
    p.encore = 0

    effects.resolve_card(st, loader.get_card("take_your_bow"))

    assert p.salon == ["usher", "crabaletta"]
    assert p.powers["salon_member"] == 2
    # Chevalmarin's bow grants Encore -- proof the member's UNIQUE payoff
    # fired, not merely that the queue got shorter.
    assert p.encore == C.SALON_MEMBERS["chevalmarin"]["bow"]["encore"]


def test_the_bow_probe_is_inert_on_an_empty_stage():
    """A no-op, never an error. The card must not be unplayable and must not
    raise -- the stage is on screen, so the player can see it coming."""
    st = furina_state()
    st.player.salon = []
    st.player.powers["salon_member"] = 0

    effects.resolve_card(st, loader.get_card("take_your_bow"))

    assert st.player.salon == []
    assert st.player.powers["salon_member"] == 0


def test_the_bow_probe_fires_every_bow_rider():
    """The probe's value is the bow, and a bow is not just the member's own
    payoff -- Stagehands pays on the EVENT. If the probe missed the riders it
    would measure something narrower than the thing being probed."""
    st = furina_state()
    p = st.player
    p.salon = ["usher"]
    p.powers["salon_member"] = 1
    p.powers["salon_bow_block"] = 5
    p.powers["salon_bow_encore"] = 2
    p.encore = 0

    effects.resolve_card(st, loader.get_card("take_your_bow"))

    assert p.encore == 2                       # the Stagehands rider
    assert p.block >= 5                        # rider + usher's own bow block


def test_the_bow_probe_stops_at_an_empty_stage_rather_than_over_bowing():
    """`amount` is a count of bows, not a demand. A three-bow card on a
    one-member stage takes one bow -- the loop breaks rather than popping
    from an empty list, and the counter follows the queue."""
    st = furina_state()
    p = st.player
    p.salon = ["usher"]
    p.powers["salon_member"] = 1

    effects.resolve_card(st, _card(
        effects=[{"op": "salon_bow", "amount": 3}]))

    assert p.salon == []
    assert p.powers["salon_member"] == 0
