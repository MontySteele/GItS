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
