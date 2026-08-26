"""EB-145 (`P11`): the SCORE learns the payout the chooser is about to buy.

`P10` (R211) made the PICK formula-aware and left the SCORE at the base.
`Tide of Names` deals `5 + 2 per exhaust_selection_cost` to ALL enemies, the
selection has not happened at score time, and `effects._calc_amount` reads
`state.exhaust_selection` -- empty while the pilot is deciding -- so the pilot
priced a 2-cost wide attack at 5 per body no matter what it was about to eat.
`pearl_barrage` prints the same shape aimed, at `per: 3`, and was blind in
exactly the same way.

What this file pins:

  * the two carriers score `base + per * chosen_cost`, times the living bodies
    the effect names (R211's multiplicity clause, which `_expected_damage`'s
    per-target loop already applies);
  * the forecast AGREES with the selection the engine goes on to make -- the
    Track C.2 rule, and the only property that makes the number honest;
  * every card printing no selection formula scores through the identical
    arithmetic it scored through before, and the set of rows that print one is
    EXACTLY two;
  * the forecast leaves no trace: `state.exhaust_selection` is restored, so the
    next card scored cannot read a selection that never happened.
"""

import pytest

from tier0.content import loader
from tier0.engine import combat, effects
from tier0.engine.state import Card
from tier0.pilot import policy
from tier0.tests.conftest import make_enemy, make_state


CARRIERS = ("pearl_barrage", "the_tide_remembers")


def card(cid, cost=1, type="skill", effects_=None, **kw):
    return Card(id=cid, name=cid, cost=cost, type=type,
                effects=effects_ if effects_ is not None else
                [{"op": "block", "amount": 1}], **kw)


def board(hand, enemies=1, hp=80):
    state = make_state([make_enemy(hp=hp, name=f"e{i}")
                        for i in range(enemies)])
    state.player.energy = 3
    state.player.hand = list(hand)
    return state


def formula(cid):
    row = loader.get_card(cid)
    for fx in row.effects:
        if fx.get("op") == "damage" and isinstance(fx.get("amount_formula"),
                                                   dict):
            return fx["amount_formula"], fx.get("target")
    raise AssertionError(f"{cid} prints no damage formula")


# --- the two carriers ------------------------------------------------------

def test_exactly_two_shipped_rows_print_a_selection_formula():
    """The blast radius of this repair, enumerable and asserted in both
    directions. A third row printing one is priced here automatically -- and
    is a window's worth of moved numbers that has to be said out loud."""
    printed = sorted(
        c.id for c in loader._card_index().values()
        if any(policy._reads_a_selection(fx)
               for fx in policy._printed_effects(c.effects)))
    assert printed == sorted(CARRIERS)


def test_tide_of_names_scores_base_plus_slope_times_the_chosen_cost():
    tide = loader.get_card("the_tide_remembers")
    fx, target = formula("the_tide_remembers")
    assert target == "all_enemies"
    victim = card("fat", cost=2)
    state = board([tide, victim, card("cheap", cost=0)])

    expected = fx["base"] + fx["per"] * victim.cost
    assert policy._expected_damage(state, tide) == pytest.approx(expected)


def test_the_wide_payout_is_multiplied_by_the_living_bodies():
    """R211's multiplicity clause at the SCORE. It is not a second multiply
    added here: `_expected_damage` already sums an `all_enemies` effect over
    `state.living_enemies`, so making the amount right makes the board right."""
    tide = loader.get_card("the_tide_remembers")
    fx, _ = formula("the_tide_remembers")
    victim = card("fat", cost=2)
    per_body = fx["base"] + fx["per"] * victim.cost

    for n in (1, 3, 5):
        state = board([tide, victim, card("cheap", cost=0)], enemies=n)
        assert policy._expected_damage(state, tide) == pytest.approx(
            per_body * n)


def test_pearl_barrage_was_blind_the_same_way_and_is_fixed_in_the_same_seam():
    """The row asks whether the aimed carrier shares the blindness. It does,
    at a STEEPER slope (`per: 3`), and neither card is named in the fix."""
    pearl = loader.get_card("pearl_barrage")
    fx, target = formula("pearl_barrage")
    assert target == "enemy"
    victim = card("fat", cost=2)
    state = board([pearl, victim, card("cheap", cost=0)], enemies=3)

    expected = fx["base"] + fx["per"] * victim.cost
    # AIMED: one body, however many are standing.
    assert policy._expected_damage(state, pearl) == pytest.approx(expected)


def test_the_slope_is_read_off_the_card_not_hardcoded():
    """Change what the card prints and the score changes with it -- the same
    derivation test `formula_aware_payout` carries for the pick."""
    victim = card("fat", cost=2)
    probe = card("probe", cost=1, type="attack", effects_=[
        {"op": "exhaust_from", "amount": 1, "select": "chosen"},
        {"op": "damage", "target": "enemy",
         "amount_formula": {"base": 1, "per": 7,
                            "count": "exhaust_selection_cost"}}])
    state = board([probe, victim])
    assert policy._expected_damage(state, probe) == pytest.approx(
        1 + 7 * victim.cost)


def test_a_selection_count_with_no_marginal_still_reads_the_engines_rule():
    """`exhaust_selection_size` is a count the engine defines and the score
    reads through `exhaust_selection_counts`, not through a copy of it: one
    victim contributes exactly one."""
    probe = card("probe", cost=1, type="attack", effects_=[
        {"op": "exhaust_from", "amount": 1, "select": "chosen"},
        {"op": "damage", "target": "enemy",
         "amount_formula": {"base": 4, "per": 5,
                            "count": "exhaust_selection_size"}}])
    state = board([probe, card("any", cost=1)])
    assert policy._expected_damage(state, probe) == pytest.approx(4 + 5)


# --- the forecast agrees with what happens ---------------------------------

def test_the_forecast_is_the_selection_the_engine_actually_makes():
    """Track C.2, applied to a pool instead of a predicate: the pilot's
    forecast of what it will eat cannot disagree with what it eats. Both sides
    build the pool with `effects.exhaust_pool` and pick with the same chooser,
    so this is agreement by construction rather than by coincidence."""
    tide = loader.get_card("the_tide_remembers")
    hand = [tide, card("fat", cost=2), card("mid", cost=1),
            card("cheap", cost=0)]
    state = board(hand)

    forecast = policy._forecast_exhaust_selection(state, tide)
    predicted = policy._expected_damage(state, tide)

    combat.play_card(state, tide)
    assert state.exhaust_selection == forecast
    dealt = sum(row["amount"] for row in state.log
                if row["event"] == "damage")
    assert dealt == pytest.approx(predicted)


def test_the_forecast_excludes_the_card_being_played():
    """At resolution the played card has already left hand; at score time it
    has not. `exhaust_pool(exclude=...)` is what makes the two agree, and a
    card that could eat ITSELF would forecast a payout it can never buy."""
    pearl = loader.get_card("pearl_barrage")
    state = board([pearl])
    assert policy._forecast_exhaust_selection(state, pearl) == []
    fx, _ = formula("pearl_barrage")
    assert policy._expected_damage(state, pearl) == pytest.approx(fx["base"])


def test_the_forecast_respects_kokomis_rotation_law():
    """The pool the engine offers her never holds junk, so neither does the
    pool the score forecasts off. One definition, two consumers."""
    tide = loader.get_card("the_tide_remembers")
    junk = Card(id="status_burn", name="Burn", cost=2, type="status",
                rarity="status", effects=[])
    state = board([tide, junk, card("mid", cost=1)])
    state.player.relic_hooks.append("tamakushi_casket")

    forecast = policy._forecast_exhaust_selection(state, tide)
    assert [d["id"] for d in forecast] == ["mid"]


def test_the_forecast_follows_the_eb118_switch(monkeypatch):
    """With `PILOT_POLICIES_ENABLED` off the engine takes `_worst_card`'s pick,
    so a forecast that asked the chooser anyway would price a victim the engine
    is not going to take -- and the W4 gate claim would become false at the
    scorer. Same gate, same fallback."""
    monkeypatch.setattr(policy, "PILOT_POLICIES_ENABLED", False)
    tide = loader.get_card("the_tide_remembers")
    hand = [tide, card("fat", cost=2), card("cheap", cost=0)]
    state = board(hand)

    forecast = policy._forecast_exhaust_selection(state, tide)
    predicted = policy._expected_damage(state, tide)

    combat.play_card(state, tide)
    assert state.exhaust_selection == forecast
    assert sum(row["amount"] for row in state.log
               if row["event"] == "damage") == pytest.approx(predicted)


# --- the forecast leaves no trace ------------------------------------------

def test_the_live_selection_is_restored_after_a_score():
    tide = loader.get_card("the_tide_remembers")
    state = board([tide, card("fat", cost=2)])
    state.exhaust_selection = [{"id": "earlier", "cost": 9, "type": "skill",
                                "rarity": "common", "companion": False,
                                "upgraded": False}]
    policy._expected_damage(state, tide)
    assert [d["id"] for d in state.exhaust_selection] == ["earlier"]


def test_the_selection_is_restored_even_when_the_formula_raises(monkeypatch):
    tide = loader.get_card("the_tide_remembers")
    state = board([tide, card("fat", cost=2)])
    before = state.exhaust_selection

    def boom(*args, **kwargs):
        raise RuntimeError("formula")

    monkeypatch.setattr(effects, "_calc_amount", boom)
    with pytest.raises(RuntimeError):
        policy._expected_damage(state, tide)
    assert state.exhaust_selection is before


# --- everything else is byte-identical -------------------------------------

def test_a_card_printing_no_selection_formula_never_reaches_the_chooser(
        monkeypatch):
    """The archive-scope claim, made mechanically rather than argued. Every
    other formula-bearing row in the repo is scored with the chooser rigged to
    explode; the two carriers are the only rows that trip it."""
    def boom(*args, **kwargs):
        raise AssertionError("the chooser was consulted")

    monkeypatch.setattr(policy, "_forecast_exhaust_selection", boom)
    state = board([], enemies=2)
    tripped = []
    for row in loader._card_index().values():
        state.player.hand = [row]
        for term in (policy._expected_damage, policy._raw_block):
            try:
                term(state, row)
            except AssertionError:
                tripped.append(row.id)
                break
            except Exception:
                pass            # unrelated to this seam; other tests own it
    assert sorted(set(tripped)) == sorted(CARRIERS)


def test_no_shipped_row_prints_a_selection_reading_BLOCK_formula():
    """`_raw_block` reads formulas through the same seam, so a Block that
    counted a selection would be priced correctly today. None is printed --
    stated so that the damage-only wording above is a fact about the sheet and
    not a gap in the repair."""
    for row in loader._card_index().values():
        for fx in policy._printed_effects(row.effects):
            if fx.get("op") == "block":
                assert not policy._reads_a_selection(fx), row.id


def test_the_chooser_itself_is_unchanged_by_this_window():
    """`exhaust_future_value` SUSPENDS the forecast, so a candidate that prints
    its own selection payout is still valued at its BASE. That keeps `P10`'s
    ratified pick byte-identical and terminates the recursion -- the forecast
    asks the chooser, the chooser values candidates, and one of the two has to
    stop."""
    pearl = loader.get_card("pearl_barrage")
    fx, _ = formula("pearl_barrage")
    state = board([card("host", cost=1), pearl, card("fat", cost=2)])

    with policy._forecast_suspended():
        base_only = policy._expected_damage(state, pearl)
    assert base_only == pytest.approx(fx["base"])

    # ... and that is the number the chooser prices it at, unsuspended.
    scale = 1.0 + policy.EXHAUST_COST_EFFICIENCY_WEIGHT * pearl.cost
    assert policy.exhaust_future_value(state, pearl) == pytest.approx(
        (base_only + policy._block_value(state, pearl)
         + policy._scaling_value(state, pearl)
         + policy._tempo_value(state, pearl)
         + policy._sustain_value(state, pearl)) / scale)


def test_two_carriers_in_one_hand_terminate():
    """The recursion the latch exists for, exercised rather than reasoned
    about: each card forecasts a pool that holds the other."""
    pearl = loader.get_card("pearl_barrage")
    tide = loader.get_card("the_tide_remembers")
    state = board([pearl, tide, card("fat", cost=2)])
    assert policy._expected_damage(state, pearl) > 0
    assert policy._expected_damage(state, tide) > 0
