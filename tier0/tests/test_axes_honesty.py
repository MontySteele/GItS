"""The three mechanical repairs to the scorecard instrument (B8, audit sec.2.2).

**Scope, stated first because it is the whole point.** These pin that the
instrument does not INVENT numbers. They deliberately do NOT pin that the
scorecard is right.

D3 (2026-07-26) pulled the scorecard INVARIANTS from this batch -- the
non-elite <= 4.0 cap and the declared-elite-pair identity -- and not for cost.
Encoding "the scorecard must be obeyed" asserts that the scorecard is
directionally correct, and that is the open question the axis-validity session
exists to answer: the bands were ratified against a battery since recognized as
unrealistic, and designs were then tuned until the axes hit those bands, so a
design that "passes" may be passing by construction. Reinstate the invariants
only on that session's verdict.

What is in scope is narrower and uncontroversial. Each of the three defects
below made the instrument report a number it had not measured:

  1. a zero baseline divided by 1e-9, clamped to SCORE_CAP, and printed 10.0
     -- "best possible" and "unmeasurable" were the same output;
  2. a missing `attrition`/`swarm` encounter id silently became a
     whole-battery average, so the axis printed a different quantity;
  3. "no fight reached turn 10" became A2 = 1.0, which against a baseline that
     also read 1.0 printed exactly 3.0: average scaling, from zero samples.

None of these say the axis is correct. All three say it is honest about what
it looked at.
"""

from __future__ import annotations

import pytest

from tier0.harness import axes
from tier0.harness.metrics import FightStats


def _stats(**kw) -> FightStats:
    """A zeroed FightStats; callers set only the fields their axis reads."""
    base = dict(won=True, turns=1, hp_start=80, hp_end=80,
                total_damage_dealt=0, damage_by_turn={}, energy_by_turn={},
                total_block_gained=0, damage_blocked=0, energy_spent=0,
                cards_drawn_extra=0, energy_generated_extra=0, healing=0,
                encore_absorbed=0, debuff_stacks_applied=0,
                debuffed_intents=0, aura_intents=0, total_intents=0,
                reactions=0, reaction_damage=0, auras_wasted=0)
    base.update(kw)
    return FightStats(**base)


# --- 1. the zero-baseline anchor -----------------------------------------

def test_a_zero_baseline_raises_instead_of_scoring_ten():
    """The defect, stated as its symptom: 0 anchor -> 1e9 -> capped 10.0."""
    raw = {ax: 1.0 for ax in axes.AXES}
    raw.update(A6_aoe=1.0, A6_debuff=1.0, A6_app=0.0)
    baseline = dict(raw, A1_frontload=0.0)
    with pytest.raises(ValueError, match="zero anchor"):
        axes.normalize(raw, baseline)


def test_the_a7_inversion_is_guarded_on_the_side_it_divides_by():
    """A7 is the one axis whose divisor is the RAW value, not the baseline.

    A raw of 0 means "peaked before turn 1", which `_turns_to_own_peak` cannot
    produce. Guarding only the baseline would have left exactly one axis able
    to print a free 10.0.
    """
    baseline = {ax: 1.0 for ax in axes.AXES}
    baseline.update(A6_aoe=1.0, A6_debuff=1.0, A6_app=0.0)
    raw = dict(baseline, A7_setup_tax=0.0)
    with pytest.raises(ValueError, match="zero anchor"):
        axes.normalize(raw, baseline)


def test_a6_application_uptime_is_still_allowed_a_zero_baseline():
    """Exempt by construction, and it must STAY exempt.

    The Ironclad applies no auras, so this term's baseline IS zero -- which is
    precisely why R18 anchored it additively rather than as a ratio. A guard
    that swept it up would break the anchor it was written to protect.
    """
    raw = {ax: 1.0 for ax in axes.AXES}
    raw.update(A6_aoe=1.0, A6_debuff=1.0, A6_app=0.0)
    scores = axes.normalize(raw, dict(raw))
    assert scores["A6_utility"] == pytest.approx(3.0)


def test_the_anchor_guard_leaves_ordinary_scoring_untouched():
    """Zero behaviour change wherever the baseline was measurable."""
    raw = {ax: 1.0 for ax in axes.AXES}
    raw.update(A6_aoe=1.0, A6_debuff=1.0, A6_app=0.0)
    doubled = dict(raw, A1_frontload=2.0)
    assert axes.normalize(doubled, raw)["A1_frontload"] == pytest.approx(6.0)
    assert axes.normalize(raw, raw)["A1_frontload"] == pytest.approx(3.0)


# --- 2. named encounter pools --------------------------------------------

def test_a_battery_missing_attrition_fails_loudly():
    with pytest.raises(KeyError, match="attrition"):
        axes.raw_axes({"swarm": [_stats()], "punisher": [_stats()]})


def test_a_battery_missing_swarm_fails_loudly():
    with pytest.raises(KeyError, match="swarm"):
        axes.raw_axes({"attrition": [_stats()], "punisher": [_stats()]})


def test_an_empty_named_pool_is_as_missing_as_an_absent_one():
    """A renamed encounter leaves the key present and the list empty.

    `.get(enc, pooled)` did not catch that at all -- the key existed, so the
    fallback never fired and the axis averaged an empty list to 0.0 instead.
    """
    with pytest.raises(KeyError, match="attrition"):
        axes.raw_axes({"attrition": [], "swarm": [_stats()]})


def test_synthetic_callers_must_declare_themselves():
    """`battery=False` is a call-site declaration, never a default."""
    raw = axes.raw_axes({"x": [_stats(damage_blocked=6, energy_spent=2)]},
                        battery=False)
    assert raw["A3_block"] == pytest.approx(3.0)
    with pytest.raises(KeyError):
        axes.raw_axes({"x": [_stats()]})


# --- 3. the A2 zero-sample default ---------------------------------------

def test_no_fight_reaching_turn_ten_no_longer_reads_as_average_scaling():
    """`_avg(ratios) or 1.0` made zero samples indistinguishable from 1.0x."""
    raw = axes.raw_axes({"attrition": [_stats(turns=4)],
                         "swarm": [_stats(turns=4)]})
    assert raw["A2_samples"] == 0
    assert raw["A2_scaling"] == 0.0, (
        "zero turn-10 samples must not synthesise a scaling ratio")


def _measurable_battery() -> dict[str, list[FightStats]]:
    """A battery where every ratio axis has a nonzero anchor.

    Built deliberately rather than by repeating one object under both keys:
    the pooled axes see the union, so handing the SAME fight to `attrition`
    and `swarm` doubles the A2 sample count and quietly makes the assertions
    below about a different battery than the one they name.
    """
    long_fight = _stats(
        turns=10, energy_spent=10, damage_blocked=30, healing=6,
        cards_drawn_extra=2, energy_generated_extra=1,
        total_damage_dealt=90, debuff_stacks_applied=3,
        aura_intents=2, total_intents=10,
        energy_by_turn={1: 3, 2: 3, 3: 3},
        damage_by_turn={1: 5, 2: 10, 3: 10, 4: 10, 8: 20, 9: 20, 10: 20})
    swarm_fight = _stats(
        turns=3, energy_spent=6, damage_blocked=5, healing=2,
        total_damage_dealt=45, debuff_stacks_applied=1,
        aura_intents=1, total_intents=3,
        energy_by_turn={1: 3, 2: 3}, damage_by_turn={1: 15, 2: 15, 3: 15})
    return {"attrition": [long_fight], "swarm": [swarm_fight]}


def test_the_a2_denominator_is_reported_alongside_the_axis():
    """n is visible, so a reader can tell 1.0x from unmeasured."""
    raw = axes.raw_axes(_measurable_battery())
    assert raw["A2_samples"] == 1
    assert raw["A2_scaling"] == pytest.approx(2.0)


def test_a2_samples_is_not_an_axis():
    """It rides in the raw dict; every scorecard consumer must ignore it."""
    assert "A2_samples" not in axes.AXES
    raw = axes.raw_axes(_measurable_battery())
    scores = axes.normalize(raw, dict(raw))
    assert set(scores) == set(axes.AXES)
    # And the anchor holds: baseline against itself is 3.0 on every axis.
    for ax, score in scores.items():
        assert score == pytest.approx(3.0), ax


def test_an_unmeasured_a2_baseline_now_fails_instead_of_printing_three():
    """The two repairs composing, which is where the old silence lived.

    Baseline with no turn-10 fight: A2 raw was 1.0, target A2 raw was 1.0,
    and the scorecard printed 3.0 -- "average scaling" from nothing on either
    side. Now the baseline is 0.0 and the anchor guard says so.
    """
    short = axes.raw_axes({"attrition": [_stats(turns=4)],
                           "swarm": [_stats(turns=4)]})
    with pytest.raises(ValueError, match="zero anchor"):
        axes.normalize(dict(short), short)


# --- scope guard ----------------------------------------------------------

def test_the_pulled_invariants_are_still_pulled():
    """D3 is a standing ruling, and this file is where it would be violated.

    If a later pass reinstates the non-elite cap or the elite-pair identity,
    it has to delete this test -- and deleting it means reading why it is
    here. `heuristic_flags` may still REPORT shape; what it must not do is
    become an assertion anywhere in the suite.
    """
    flags = axes.heuristic_flags({ax: 3.0 for ax in axes.AXES})
    assert "FLAT (no axis >= 4: boring)" in flags
    assert "NO_WEAKNESS (no axis <= 2: broken)" in flags
    # Reported as advice, never raised: nothing in heuristic_flags asserts.
    assert isinstance(flags, list)


def test_the_invariants_report_and_do_not_assert():
    """EB-50 answers ask A5's *which* the only way D3 leaves open.

    `axes.invariant_flags` encodes the two invariants the test above keeps
    pulled -- and encodes them as OUTPUT. That distinction is the whole
    ruling: the scorecard may now SAY that a reading breaches the <= 4.0 A2
    ceiling or is not the declared A1+A6 pair, and may not DECIDE anything by
    it. So a reading that fires both flags has to leave the suite green, which
    is what this test is -- it breaches both and nothing goes red.

    A later pass that makes either invariant fail a run has to delete this
    test and the one above it, and deleting them means reading why they exist.
    """
    breaching = dict({ax: 3.0 for ax in axes.AXES},
                     A1_frontload=4.1, A2_scaling=4.1, A6_utility=3.6)
    flags = axes.invariant_flags(breaching)
    assert isinstance(flags, list) and len(flags) == 2
    # Both invariants are broken here, both said so, and this test passes.
    # That is the closure, stated as an executable sentence.
