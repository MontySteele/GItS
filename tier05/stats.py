"""The repo's ONE percentile and ONE binomial interval.

WHY THIS FILE EXISTS (sim-hygiene sprint, 2026-07-29). Before it, five
hand-rolled `_percentile` copies were spread over tier05 and tools, under TWO
INCOMPATIBLE CONVENTIONS -- and two of the copies carried docstrings swearing
they matched a third that they did not match:

    tier05/run_metrics.py            linear interpolation   (canonical)
    tools/realistic_axis_scores.py   linear interpolation
    tools/real_battery_calibration.py linear interpolation
    tier05/elite_blitz.py            NEAREST-RANK, docstring claimed linear
    tier05/kurage_telemetry.py       NEAREST-RANK, docstring claimed linear

Both of the wrong ones said the same thing in their own words: "two percentile
definitions in one report is how a moved tail gets argued about instead of
acted on." They were right, and they were the second definition.

THE CONVENTION IS LINEAR INTERPOLATION (numpy's default, type 7), for three
reasons in this order: it is what the oldest and most-read surface
(`run_metrics.survival_profile`, whose HP bands are quoted in every survival
report on record) has always computed; it is what the two nearest-rank copies
DECLARED they were computing, so honouring it is honouring their intent rather
than their arithmetic; and it is the standard definition, so an outside reader
does not need this file to interpret a number that came out of it.

NO RATIFIED BAND MOVED. The stop-condition for this unification was "a locked
band whose input is a percentile" -- there is none. Every ratified band in the
repo is a WINRATE band, and winrate is a ratio, not a quantile. What did move
is Kokomi PULSE TELEMETRY, which is reported and has never been ratified: the
two nearest-rank readers (`elite_blitz.aggregate`'s `p95_pulse` and
`kurage_telemetry.aggregate`'s `p50`/`p95`) now interpolate. The two unit
tests that pinned the old arithmetic were re-homed with the change named in
them, not deleted. See docs/sprint-sim-hygiene-log-2026-07-29.md.
"""

from __future__ import annotations

import math


def percentile(values, q: float) -> float:
    """The q-quantile of `values` by LINEAR INTERPOLATION (type 7).

    `q` is a fraction in [0, 1], not a percentage. An empty sample returns
    0.0 rather than raising: every caller here is a report line, and a report
    that crashes on a cohort that met no elites is worse than one that prints
    a zero next to a visible `n`.
    """
    if not values:
        return 0.0
    s = sorted(values)
    if len(s) == 1:
        return float(s[0])
    idx = q * (len(s) - 1)
    lo = int(idx)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (idx - lo)


def wilson95(successes: int, trials: int,
             z: float = 1.96) -> tuple[float, float]:
    """95% Wilson score interval -- the repo's standard read for a winrate.

    Wilson rather than normal-approximation because this repo measures cells
    that legitimately win zero runs out of 600, where the normal interval is
    the degenerate (0, 0) and says nothing. Returns (lo, hi) ONLY: the point
    estimate is `successes / trials` and every caller already has it, so
    returning it here just gave two call sites two different tuple shapes.

    The bounds are clamped into [0, 1]. Analytically the Wilson interval is
    already inside the unit interval, so the clamp is a float-error guard and
    never a correction -- one of the two unified implementations had it and
    the other did not, and keeping it is the cheaper of two identical answers.
    """
    if trials <= 0:
        return 0.0, 0.0
    p = successes / trials
    denom = 1 + z * z / trials
    center = (p + z * z / (2 * trials)) / denom
    half = (z * math.sqrt(p * (1 - p) / trials
                          + z * z / (4 * trials * trials)) / denom)
    return max(0.0, center - half), min(1.0, center + half)


# ---------------------------------------------------------------------------
# PAIRED arithmetic (EB-17p, 2026-08-10)
#
# Two arms run on the SAME seeds are not two independent samples, and reading
# them with `wilson95` throws away the whole reason the pairing was bought.
# These live here, beside the other two, for the reason this file exists at
# all: the five hand-rolled `_percentile` copies were five because there was
# nowhere for the first one to go. An experiment script that hand-rolls a
# McNemar is the same mistake with a different name.
# ---------------------------------------------------------------------------


def discordant_counts(pairs) -> tuple[int, int, int, int]:
    """Split seed-matched binary pairs into the 2x2 McNemar table.

    `pairs` is a sequence of `(treated, control)` outcomes, each truthy for a
    win. Returns `(b, c, both, neither)`:

        b   treated won, control lost
        c   control won, treated lost
        both / neither   the CONCORDANT pairs

    All four are returned because a delta printed without its discordant
    counts cannot be checked: `b=3, c=1` and `b=300, c=100` give the same
    point estimate on wildly different evidence, and the concordant counts are
    what tell a reader how much of the pairing actually bit.
    """
    b = c = both = neither = 0
    for t, k in pairs:
        if t and k:
            both += 1
        elif t and not k:
            b += 1
        elif k and not t:
            c += 1
        else:
            neither += 1
    return b, c, both, neither


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided EXACT McNemar p-value on the discordant counts.

    Under the null the `b + c` discordant pairs are a fair coin, so the test
    is the two-sided exact binomial at p = 0.5. Exact rather than the usual
    chi-square approximation because this repo measures cells with winrates in
    the single-digit percent, where the discordant count can be small enough
    for the approximation to be the wrong shape -- and an exact test costs
    nothing at these sizes.

    No discordant pairs at all returns 1.0: the arms never once disagreed, so
    there is no evidence of a difference. It is NOT a zero p-value and it is
    not an error.
    """
    if b < 0 or c < 0:
        raise ValueError(f"discordant counts must be non-negative: {b}, {c}")
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) * 0.5 ** n
    # Doubling the smaller tail is the standard two-sided construction for a
    # symmetric null; clamped because at b == c the two tails overlap on the
    # centre and the doubled sum exceeds 1.
    return min(1.0, 2.0 * tail)


def paired_bootstrap_delta(pairs, rng, resamples: int = 10000,
                           conf: float = 0.95) -> tuple[float, float]:
    """Percentile bootstrap interval on the PAIRED delta, resampling PAIRS.

    `pairs` is a sequence of `(treated, control)` values; the statistic is
    `mean(treated) - mean(control)`. The resampling unit is the PAIR, not the
    run: resampling the two arms independently would reconstruct the unpaired
    interval and quietly undo the design.

    The values may be the booleans `discordant_counts` takes (a winrate
    delta) or any real number (acts completed, deck size, fights). One
    function for both because it is the same estimator either way, and a
    second copy for the continuous case is exactly how this file's five
    `_percentile` copies started. The BINARY case additionally gets
    `mcnemar_exact` as its test; the continuous case has this interval only.

    `rng` is passed in and never constructed here. Bootstrap resampling is NEW
    sampling, and the repo's rule (`exp_reactions_corpus`) is that new sampling
    runs on its own dedicated stream with its own seed, never the run seed --
    a bootstrap sharing a stream with the sim is a bootstrap that can move a
    fight. Making the caller supply the generator is how that rule is kept
    visible at the call site instead of buried in a default.

    Returns `(lo, hi)`. An empty sample returns `(0.0, 0.0)`, the `percentile`
    convention: a report line for a cohort of nothing prints a zero beside a
    visible `n` rather than crashing.
    """
    rows = [(float(t), float(k)) for t, k in pairs]
    n = len(rows)
    if n == 0:
        return 0.0, 0.0
    if resamples <= 0:
        raise ValueError(f"resamples must be positive: {resamples}")
    deltas = []
    for _ in range(resamples):
        s_t = s_k = 0.0
        for _ in range(n):
            t, k = rows[rng.randrange(n)]
            s_t += t
            s_k += k
        deltas.append((s_t - s_k) / n)
    alpha = (1.0 - conf) / 2.0
    return percentile(deltas, alpha), percentile(deltas, 1.0 - alpha)
