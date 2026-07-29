"""Guards for the salon_stoker's machinery term (pilot-gap sprint 2026-07-28).

Each test here reconstructs a behaviour the GREEDY pilot demonstrably lacks,
so it fails against the pre-sprint policy as well as against a plausible
mis-implementation -- the house rule that a gate is only trusted once it has
been seen to fail against the real defect. The two headline ones:

- `test_a_deploy_does_not_decay_as_the_fight_wears_on` fails against the
  greedy valuation by construction: a deploy is an `apply_power` on self, so
  `_scaling_value` is its only pricing and that term multiplies by
  `max(0, 1 - turn/12)`. At turn 12 the greedy pilot prices a member at
  exactly zero, and a member fielded on turn 12 still ticks every remaining
  turn.
- `test_the_last_pilot_standing_is_the_only_one_that_reads_stoke` is the
  isolation gate: it fails the moment `stoke` stops defaulting to 0.0, which
  is the only way this sprint could contaminate the frozen anchor tables.
"""

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine.state import Card
from tier0.pilot import policy
from tier0.tests.conftest import make_enemy, make_state


def _deploy(amount=1, member="crabaletta"):
    return Card(
        id="probe_deploy", name="Probe Deploy", cost=1, type="skill",
        effects=[{"op": "apply_power", "power": "salon_member",
                  "amount": amount, "member": member}],
    )


def _encore(amount=3):
    return Card(
        id="probe_encore", name="Probe Encore", cost=1, type="skill",
        effects=[{"op": "gain_encore", "amount": amount}],
    )


def _stage(members=0, encore=0, cap_up=0):
    st = make_state([make_enemy(hp=50)])
    st.player.salon = ["crabaletta"] * members
    st.player.powers["salon_member"] = members
    if cap_up:
        st.player.powers["salon_cap_up"] = cap_up
    st.player.encore = encore
    return st


# --- behaviour 1: deploy early ------------------------------------------

def test_an_open_slot_is_worth_more_than_a_bow_trigger():
    """A full stage turns a deploy into a REPLACEMENT -- the oldest member
    bows out. Real value, but a different decision, and the brief asks the
    stoker to tell them apart rather than to spam deploys."""
    open_stage = policy._stoke_value(_stage(members=1), _deploy())
    full_stage = policy._stoke_value(
        _stage(members=C.SALON_MEMBER_SLOTS), _deploy())

    assert open_stage == pytest.approx(policy.STOKE_DEPLOY_OPEN)
    assert full_stage == pytest.approx(policy.STOKE_DEPLOY_FULL)
    assert open_stage > full_stage


def test_a_multi_deploy_splits_across_the_slots_it_actually_fills():
    """Full Ensemble's three deploys into one open slot are one addition and
    two replacements, and pricing all three at the open rate would make the
    stoker overvalue exactly the card that is worth least on a full stage."""
    st = _stage(members=C.SALON_MEMBER_SLOTS - 1)

    assert policy._stoke_value(st, _deploy(amount=3)) == pytest.approx(
        policy.STOKE_DEPLOY_OPEN + 2 * policy.STOKE_DEPLOY_FULL)


def test_the_live_cap_is_read_not_the_constant():
    """A12 made the cap a per-player stat. A stoker that read
    C.SALON_MEMBER_SLOTS would stop valuing deploys the moment Casting Call
    landed -- on the deck most likely to have drafted it."""
    st = _stage(members=C.SALON_MEMBER_SLOTS, cap_up=2)

    assert policy._stoke_value(st, _deploy()) == pytest.approx(
        policy.STOKE_DEPLOY_OPEN)


def test_a_deploy_does_not_decay_as_the_fight_wears_on():
    """THE GREEDY GAP, reconstructed. `_scaling_value` decays a self-power by
    max(0, 1 - turn/12), which is right for a one-shot buff and wrong for a
    member that ticks every remaining turn. Pinning both halves so the
    regression is legible: greedy really does reach zero, and stoke does
    not move."""
    early, late = _stage(members=0), _stage(members=0)
    late.turn = 12
    card = _deploy()

    assert policy._scaling_value(early, card) > 0
    assert policy._scaling_value(late, card) == 0.0
    assert (policy._stoke_value(late, card)
            == policy._stoke_value(early, card) > 0)


# --- behaviour 2: fuel the stage ----------------------------------------

def test_encore_is_worth_more_when_the_runway_is_short():
    """The runway the D7 ribbon draws: held Encore against the stage's
    per-turn bill. _sustain_value prices Encore at a flat 0.8/point and can
    see none of this."""
    starving = _stage(members=3, encore=0)
    fed = _stage(members=3, encore=99)
    card = _encore(amount=3)

    assert (policy._stoke_value(starving, card)
            == pytest.approx(3 * policy.STOKE_FUEL_HUNGRY))
    assert (policy._stoke_value(fed, card)
            == pytest.approx(3 * policy.STOKE_FUEL_SATED))
    assert policy._sustain_value(starving, card) == pytest.approx(
        policy._sustain_value(fed, card))


def test_a_gain_that_straddles_the_runway_is_priced_on_both_sides():
    """Otherwise the term is a cliff: one point below the threshold the whole
    card is hungry, one point above it the whole card is sated, and the
    pilot's preference between two Encore cards flips on a point that
    changes almost nothing."""
    bill = 3 * C.SALON_TICK_ENCORE_COST
    want = policy.STOKE_RUNWAY_TURNS * bill
    st = _stage(members=3, encore=int(want) - 2)

    assert policy._stoke_value(st, _encore(amount=5)) == pytest.approx(
        2 * policy.STOKE_FUEL_HUNGRY + 3 * policy.STOKE_FUEL_SATED)


def test_an_empty_stage_has_no_runway_to_close():
    """With no members there is nothing to starve, so every point scores at
    the sated rate. This is what makes the stoker deploy BEFORE it fuels
    without a sequencing rule being written -- the ordering falls out of the
    bill being zero."""
    assert policy._stoke_value(_stage(members=0), _encore(4)) == pytest.approx(
        4 * policy.STOKE_FUEL_SATED)


# --- isolation ----------------------------------------------------------

def test_the_stoker_revalues_nothing_but_its_own_machinery():
    """Brief Track 1.4. A stoker that also priced damage or block better
    would make the sprint's gap unattributable -- 'the engine rewards
    stoking' and 'this pilot is simply better' would produce the same
    number."""
    st = _stage(members=1)
    attack = Card(id="probe_hit", name="Probe Hit", cost=1, type="attack",
                  effects=[{"op": "damage", "amount": 9, "target": "enemy"}])
    blocker = Card(id="probe_blk", name="Probe Blk", cost=1, type="skill",
                   effects=[{"op": "block", "amount": 9}])

    assert policy._stoke_value(st, attack) == 0.0
    assert policy._stoke_value(st, blocker) == 0.0


def test_no_pilot_an_archetype_can_reach_declares_a_stoke_weight():
    """THE contamination gate.

    Pinning "only salon_stoker has stoke" is the wrong invariant -- the
    sprint's own ablation arms declare it too, and a gate that has to be
    edited every time an arm is added stops being a gate. The invariant that
    actually protects the frozen tables is about REACHABILITY: every anchor
    number on record was flown by a pilot that `resolve_plan` returned for
    some (character, archetype), and the stoker family is deliberately
    unreachable that way -- no character yaml names it, so it can only be
    passed by hand, deliberately, by a script that means to.
    """
    from tier05.runner import CHARACTER_PLANS

    reachable = {pilot for plans in CHARACTER_PLANS.values()
                 for pilot in plans.values()}
    contaminated = {pid for pid in reachable
                    if loader.pilot_weights(pid).get("stoke", 0.0)}

    assert contaminated == set()
    assert "salon_stoker" not in reachable


def test_a_zero_stoke_weight_is_arithmetically_dead():
    """Not just unused -- unreachable. `_score` skips the term entirely, so
    no rounding, no ordering change, nothing for an anchor diff to catch."""
    st = _stage(members=1, encore=0)
    card = _deploy()
    salon = loader.pilot_weights("salon")

    assert "stoke" not in salon
    assert policy._score(st, card, salon) == pytest.approx(
        policy._score(st, card, dict(salon, stoke=0.0)))
    assert policy._score(st, card, dict(salon, stoke=1.0)) > policy._score(
        st, card, salon)


def _all_pilot_ids() -> list[str]:
    import yaml

    from tier0.content.loader import CONTENT_DIR

    path = CONTENT_DIR / "pilots" / "archetypes.yaml"
    rows = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [row["id"] for row in rows] + ["generic"]
