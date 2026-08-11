"""The paired arithmetic in `tier05/stats.py` (EB-17p prerequisite 5).

`mcnemar_exact` and `paired_bootstrap_delta` live in stats.py rather than in
the experiment script for the reason the module's own docstring gives: the
repo already learned what happens when a piece of arithmetic has nowhere to
go, and got five `_percentile` copies under two incompatible conventions. A
McNemar hand-rolled in a sweep script is that lesson with a new name.

These pin the answers against cases where the right answer is known by hand
or by symmetry, not against a previous run of the same code.
"""

from __future__ import annotations

import random

import pytest

from tier05 import stats


# --- discordant_counts -----------------------------------------------------

def test_the_2x2_table_is_the_2x2_table():
    pairs = [(1, 1), (1, 0), (1, 0), (1, 0), (0, 1), (0, 0), (0, 0)]
    b, c, both, neither = stats.discordant_counts(pairs)
    assert (b, c, both, neither) == (3, 1, 1, 2)
    assert b + c + both + neither == len(pairs)


def test_the_table_reads_truthiness_not_ints():
    """Callers pass `RunResult.won`, which is a bool."""
    assert stats.discordant_counts([(True, False), (False, True)])[:2] == (1, 1)


def test_swapping_the_arms_swaps_b_and_c():
    pairs = [(1, 0), (1, 0), (0, 1), (1, 1)]
    b, c, both, neither = stats.discordant_counts(pairs)
    rb, rc, rboth, rneither = stats.discordant_counts(
        [(k, t) for t, k in pairs])
    assert (rb, rc) == (c, b)
    assert (rboth, rneither) == (both, neither)


# --- mcnemar_exact ---------------------------------------------------------

def test_no_discordant_pairs_is_p_equals_one():
    """The arms never once disagreed. That is no evidence of a difference --
    it is emphatically not a zero p-value, and a report that printed one
    would be read as the strongest result in the sweep."""
    assert stats.mcnemar_exact(0, 0) == 1.0


def test_a_single_discordant_pair_is_p_equals_one():
    # Two-sided exact binomial on n=1: 2 * 0.5 = 1.0. One disagreement can
    # never be significant, at any effect size.
    assert stats.mcnemar_exact(1, 0) == pytest.approx(1.0)


def test_hand_computable_cases():
    # n = 2, k = 0: 2 * (1 * 0.25) = 0.5
    assert stats.mcnemar_exact(2, 0) == pytest.approx(0.5)
    # n = 3, k = 0: 2 * (1 * 0.125) = 0.25
    assert stats.mcnemar_exact(3, 0) == pytest.approx(0.25)
    # n = 4, k = 1: 2 * ((1 + 4) * 0.0625) = 0.625
    assert stats.mcnemar_exact(3, 1) == pytest.approx(0.625)
    # n = 10, k = 0: 2 * 0.5**10
    assert stats.mcnemar_exact(10, 0) == pytest.approx(2 * 0.5 ** 10)


def test_it_is_symmetric_in_b_and_c():
    """The test says the arms differ, not which one is better -- the sign
    lives in the delta, and reading direction off a p-value is how a null
    becomes a claim."""
    for b, c in ((7, 3), (30, 12), (100, 99), (5, 0)):
        assert stats.mcnemar_exact(b, c) == stats.mcnemar_exact(c, b)


def test_an_even_split_is_never_significant_and_never_over_one():
    """b == c doubles a tail that already contains the centre. Clamped."""
    for n in (2, 10, 100, 501):
        assert stats.mcnemar_exact(n, n) == 1.0


def test_a_lopsided_table_is_significant():
    assert stats.mcnemar_exact(40, 10) < 0.05
    assert stats.mcnemar_exact(30, 20) > 0.05


def test_p_stays_in_the_unit_interval():
    for b in range(0, 25):
        for c in range(0, 25):
            p = stats.mcnemar_exact(b, c)
            assert 0.0 <= p <= 1.0, (b, c)


def test_negative_counts_are_refused():
    with pytest.raises(ValueError):
        stats.mcnemar_exact(-1, 3)


# --- paired_bootstrap_delta ------------------------------------------------

def test_an_empty_sample_returns_zeros_rather_than_raising():
    """The `percentile` convention: a report line for a cohort of nothing
    prints a zero beside a visible n rather than crashing the sweep."""
    assert stats.paired_bootstrap_delta([], random.Random(1)) == (0.0, 0.0)


def test_perfectly_concordant_pairs_give_a_zero_width_interval():
    """Every pair agrees, so every resample has delta exactly zero. There is
    nothing for the bootstrap to find and it must not invent width."""
    pairs = [(1, 1)] * 50 + [(0, 0)] * 50
    lo, hi = stats.paired_bootstrap_delta(pairs, random.Random(7),
                                          resamples=200)
    assert lo == 0.0 and hi == 0.0


def test_a_total_effect_gives_a_delta_of_one():
    pairs = [(1, 0)] * 60
    lo, hi = stats.paired_bootstrap_delta(pairs, random.Random(7),
                                          resamples=200)
    assert lo == pytest.approx(1.0) and hi == pytest.approx(1.0)


def test_the_interval_brackets_the_observed_delta():
    pairs = ([(1, 0)] * 30 + [(0, 1)] * 10 + [(1, 1)] * 60 + [(0, 0)] * 100)
    observed = (sum(t for t, _ in pairs) - sum(k for _, k in pairs)) / len(pairs)
    lo, hi = stats.paired_bootstrap_delta(pairs, random.Random(11),
                                          resamples=2000)
    assert lo < observed < hi


def test_it_is_reproducible_from_its_own_stream():
    """Same generator seed, same interval. The stream is the caller's, so an
    experiment can reproduce a published interval without re-running the sim.
    """
    pairs = [(1, 0)] * 20 + [(0, 1)] * 8 + [(0, 0)] * 72
    a = stats.paired_bootstrap_delta(pairs, random.Random(4242), resamples=500)
    b = stats.paired_bootstrap_delta(pairs, random.Random(4242), resamples=500)
    assert a == b


def test_it_consumes_the_caller_stream_and_nothing_else():
    """The bootstrap must never touch a run seed. Proof that it draws from
    the generator it is handed: that generator's state moves, and a fresh
    generator elsewhere is unaffected."""
    rng = random.Random(4242)
    before = rng.getstate()
    stats.paired_bootstrap_delta([(1, 0), (0, 0)], rng, resamples=10)
    assert rng.getstate() != before


def test_a_wider_confidence_level_is_a_wider_interval():
    pairs = [(1, 0)] * 15 + [(0, 1)] * 10 + [(0, 0)] * 175
    lo95, hi95 = stats.paired_bootstrap_delta(pairs, random.Random(3),
                                              resamples=1500, conf=0.95)
    lo50, hi50 = stats.paired_bootstrap_delta(pairs, random.Random(3),
                                              resamples=1500, conf=0.50)
    assert (hi95 - lo95) >= (hi50 - lo50)


def test_pairing_is_not_thrown_away():
    """THE reason this function exists.

    The same two marginal winrates, arranged two ways: once perfectly
    correlated pair-by-pair (every disagreement in one direction), once
    scrambled so the arms disagree both ways. The marginals -- and therefore
    any unpaired interval -- are identical. The paired interval is not, and
    the correlated arrangement is the tighter one. An implementation that
    resampled the two arms independently would return the same width twice.
    """
    tight = [(1, 0)] * 20 + [(0, 0)] * 180
    loose = [(1, 0)] * 20 + [(0, 1)] * 20 + [(1, 1)] * 0 + [(0, 0)] * 160
    # Same treated marginal (20/200); loose has a higher control marginal, so
    # compare widths, which is what the pairing buys.
    w_tight = stats.paired_bootstrap_delta(tight, random.Random(5),
                                           resamples=1500)
    w_loose = stats.paired_bootstrap_delta(loose, random.Random(5),
                                           resamples=1500)
    assert (w_tight[1] - w_tight[0]) < (w_loose[1] - w_loose[0])


def test_it_also_takes_continuous_values():
    """§6.2's secondaries -- acts completed, deck size, fights -- are the same
    paired estimator on real numbers, and must not need a second copy of this
    function to get an interval."""
    pairs = [(3.0, 2.0)] * 40 + [(1.0, 2.0)] * 10 + [(2.0, 2.0)] * 50
    observed = (sum(t for t, _ in pairs) - sum(k for _, k in pairs)) / len(pairs)
    lo, hi = stats.paired_bootstrap_delta(pairs, random.Random(9),
                                          resamples=1500)
    assert lo < observed < hi
    assert hi > 0.0


def test_zero_resamples_is_refused():
    with pytest.raises(ValueError):
        stats.paired_bootstrap_delta([(1, 0)], random.Random(1), resamples=0)
