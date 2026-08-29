"""Kokomi's stability band, and the fact that it lands DARK. (E1.)

missed-requirements sec.1.3: R51 moved her healer fantasy *entirely* to this
instrument — "the healer fantasy moves entirely to the stability band
(HP-trajectory flatness) in the act-level realistic sims" — and the instrument
did not exist. `survival_profile` answers how LOW her HP gets; flatness is a
different question, and no metric anywhere answered it.

The DARK part is the load-bearing part and is pinned first. The acceptance band
is a [USER] ruling, and it is not on record yet.

The gate was originally BLIND declaration — the band recorded before any
playtest HP data was reviewed. **D5 (2026-07-27) amends it**: HP-trajectory
data was reviewed during the Kokomi playtest sprint, so blind declaration is no
longer possible. That playtest is EXPLORATORY and grades nothing; the band gets
declared from DESIGN INTENT, informed by those observations and recorded as
such, BEFORE the post-rework confirmatory playtest that grades it; and it may
not be revised against that grading playtest. The surviving protection is that
last clause — the band stays blind with respect to the measurement that judges
it, which was always the load-bearing half. Drawing the target around the shot
is the exact failure the axis-validity session (D3) exists to investigate one
instrument over, and there is no reason to build a second instance of it while
the first is still open.

`band is None` therefore stays pinned below: the instrument stays dark until
the D5 declaration lands, and it never judges regardless.
"""

from __future__ import annotations

import math

import pytest

from tier05 import run_metrics


class _Fight:
    """The two fields the band reads, plus the ruled telemetry feed."""

    def __init__(self, hp_start, hp_end, prevented=0):
        self.hp_start = hp_start
        self.hp_end = hp_end
        self.prevented = prevented


class _Run:
    def __init__(self, fights):
        self.fight_stats = fights


# --- the gate ------------------------------------------------------------

def test_the_band_is_none_until_a_ruling_declares_it():
    """The instrument reports; it does not judge. That is the whole gate."""
    runs = [_Run([_Fight(80, 70), _Fight(70, 55)])]
    profile = run_metrics.stability_profile(runs, 80)
    assert "band" in profile
    assert profile["band"] is None, (
        "a band appeared in the instrument. Bands are user-ratified (house "
        "rule) and this one is declared from design intent under D5, BEFORE "
        "the confirmatory playtest that grades it -- see R51, D5, and "
        "missed-requirements sec.1.3.")


def test_the_instrument_asserts_nothing_about_what_is_acceptable():
    """No pass/fail verb anywhere in the returned shape.

    Guarded structurally rather than by reading the source: the day someone
    adds `"ok": True` to this dict, the instrument has started ruling.
    """
    runs = [_Run([_Fight(80, 40)])]
    profile = run_metrics.stability_profile(runs, 80)
    forbidden = {"ok", "pass", "passed", "fail", "failed", "verdict",
                 "acceptable", "within_band"}
    assert not (forbidden & set(profile)), forbidden & set(profile)


# --- flatness is not fragility -------------------------------------------

def test_flatness_separates_two_cohorts_that_share_a_median():
    """The reason this exists at all, stated as a test.

    A character who ends every fight down 20% and one who alternates 5% and
    35% have the same mean loss and nothing else in common -- and the second
    is the one whose fantasy is broken. `survival_profile` cannot tell them
    apart; that is what this adds.
    """
    flat = [_Run([_Fight(100, 80) for _ in range(10)])]
    jagged = [_Run([_Fight(100, 95 if i % 2 else 65) for i in range(10)])]

    a = run_metrics.stability_profile(flat, 100)
    b = run_metrics.stability_profile(jagged, 100)

    assert a["hp_loss_mean_pct"] == pytest.approx(b["hp_loss_mean_pct"])
    assert a["hp_loss_sd_pct"] == pytest.approx(0.0)
    assert b["hp_loss_sd_pct"] > 0.10
    assert b["hp_loss_cv"] > a["hp_loss_cv"]


def test_the_worst_fight_is_per_run_then_averaged():
    """The kickoff's literal "max HP-loss", which is a per-RUN quantity.

    Pooling every fight and taking one global max would report the single
    unluckiest fight in 600 runs, which is an extreme-value statistic and
    moves on noise. Each run's own worst fight, averaged, is the spike rate
    the fantasy actually forbids.
    """
    runs = [_Run([_Fight(100, 90), _Fight(100, 60)]),      # worst 40%
            _Run([_Fight(100, 80), _Fight(100, 80)])]      # worst 20%
    profile = run_metrics.stability_profile(runs, 100)
    assert profile["worst_fight_loss_pct"] == pytest.approx(0.30)


def test_everything_is_a_fraction_of_max_hp():
    """So a band declared for Kokomi (80) reads against Klee (62) and the
    REF_IRONCLAD anchor (80) without rescaling -- the survival_profile rule."""
    small = run_metrics.stability_profile([_Run([_Fight(50, 25)])], 50)
    large = run_metrics.stability_profile([_Run([_Fight(100, 50)])], 100)
    assert small["hp_loss_mean_pct"] == pytest.approx(large["hp_loss_mean_pct"])


# --- the ruled telemetry feed --------------------------------------------

def test_prevented_rides_here_and_is_never_axis_credited():
    """R51: ward prevention is "a reported telemetry stream
    (FightStats.prevented) feeding the stability band, never axis-credited".

    It has been extracted since the kickoff and read by NOTHING (audit sec.6
    lists it among the metrics no report prints). This is the report.
    """
    runs = [_Run([_Fight(100, 90, prevented=10),
                  _Fight(100, 90, prevented=30)])]
    profile = run_metrics.stability_profile(runs, 100)
    assert profile["prevented_per_fight"] == pytest.approx(20.0)
    # 40 prevented against 20 actually lost.
    assert profile["prevented_share"] == pytest.approx(40 / 60)


def test_prevented_is_absent_not_zero_for_characters_without_a_ward():
    """A fight object with no `prevented` must not raise; it contributes 0."""
    class Bare:
        hp_start, hp_end = 100, 80
    profile = run_metrics.stability_profile([_Run([Bare()])], 100)
    assert profile["prevented_per_fight"] == 0.0


# --- degenerate inputs ---------------------------------------------------

def test_no_runs_and_no_fights_are_distinguishable_from_a_flat_cohort():
    """Empty must not read as "perfectly stable", which is what a bare 0.0
    SD would say. Same argument banner_variance makes for `degenerate`."""
    assert run_metrics.stability_profile([], 80) == {}
    empty = run_metrics.stability_profile([_Run([])], 80)
    assert empty["fights"] == 0
    assert "hp_loss_sd_pct" not in empty


def test_a_zero_max_hp_does_not_divide():
    assert run_metrics.stability_profile([_Run([_Fight(1, 0)])], 0) == {}


def test_healing_above_start_does_not_report_negative_loss():
    """A fight that ends higher than it started is 0 loss, not -x.

    Kokomi converts heals to Block under LAW 2, but relics and potions can
    still end a fight up, and a negative "loss" would drag the SD in a
    direction that reads as stability while meaning the opposite.
    """
    profile = run_metrics.stability_profile([_Run([_Fight(50, 70)])], 100)
    assert profile["hp_loss_mean_pct"] == 0.0
    assert not math.isnan(profile["hp_loss_sd_pct"])
