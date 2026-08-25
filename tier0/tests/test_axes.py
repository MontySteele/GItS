"""M2: axis computation, gauntlet stage-merge, frozen-battery regression."""

import pytest

from tier0.harness import axes, metrics
from tier0.harness.runner import (BASELINE, run_battery, run_full_battery,
                                  score_config)

FIGHTS = 150   # small but stable enough for the wide bounds below
SEED = 11


@pytest.fixture(scope="module")
def baseline():
    return score_config("ref_ironclad", "starter", "generic", FIGHTS, SEED)


@pytest.fixture(scope="module")
def package():
    return score_config("ref_ironclad", "archetype_package", "generic",
                        FIGHTS, SEED)


@pytest.mark.battery
def test_shared_anchor_battery_scores_identically(package):
    """score_character hands ONE baseline battery to every deck it scores
    instead of re-running it per deck. The anchor is a deterministic
    function of (fights, seed) and nothing mutates it, so that must be a
    pure saving -- if it ever is not, every archived scorecard silently
    depends on how many decks were scored beside it."""
    shared = run_full_battery(*BASELINE, "generic", FIGHTS, SEED)
    passed_in = score_config("ref_ironclad", "archetype_package", "generic",
                             FIGHTS, SEED, shared)
    assert passed_in["scores"] == package["scores"]
    assert passed_in["raw"] == package["raw"]
    assert passed_in["curve_exponent"] == package["curve_exponent"]
    assert passed_in["pressure_delta"] == package["pressure_delta"]


@pytest.mark.battery
def test_baseline_scores_are_exactly_three(baseline):
    for ax, v in baseline["scores"].items():
        assert v == pytest.approx(3.0), ax


@pytest.mark.battery
def test_baseline_has_no_heuristic_flags(baseline):
    assert baseline["heuristic_flags"] == []


@pytest.mark.battery
def test_package_deck_scales_better_than_starter(package):
    # Strength ramp is the package's whole identity: A2 must move up.
    # (The raw curve exponents are both slightly negative and within
    # noise of each other at test fight counts — the score is the claim.)
    assert package["scores"]["A2_scaling"] > 3.0


@pytest.mark.battery
def test_package_deck_beats_starter_on_tank_boss(package):
    wr = metrics.summarize(package["stats"]["tank_boss"])["winrate"]
    assert wr > 0.5


@pytest.mark.battery
def test_gauntlet_merges_stages():
    stats = run_battery("ref_ironclad", "starter", "gauntlet", "generic",
                        20, SEED)
    swarm = run_battery("ref_ironclad", "starter", "swarm", "generic",
                        20, SEED)
    # Gauntlet fights must be longer than swarm alone (second stage exists)
    assert (sum(s.turns for s in stats) / 20
            > sum(s.turns for s in swarm) / 20)
    # HP carryover: gauntlet is strictly harder than punisher alone.
    punisher = run_battery("ref_ironclad", "starter", "punisher", "generic",
                           200, SEED)
    gauntlet = run_battery("ref_ironclad", "starter", "gauntlet", "generic",
                           200, SEED)
    assert (metrics.summarize(gauntlet)["winrate"]
            < metrics.summarize(punisher)["winrate"])


# --- frozen battery regression (recalibrating requires editing these) ---

@pytest.mark.battery
@pytest.mark.parametrize("enc,lo,hi", [
    ("punisher", 0.40, 0.70),      # target 50-60%
    ("swarm", 0.95, 1.01),
    ("attrition", 0.95, 1.01),
    ("tank_boss", -0.01, 0.10),    # starter loses to the boss by design
])
def test_frozen_battery_starter_winrates(enc, lo, hi):
    stats = run_battery("ref_ironclad", "starter", enc, "generic", 300, SEED)
    wr = metrics.summarize(stats)["winrate"]
    assert lo < wr < hi, f"{enc}: {wr} outside frozen calibration band"


@pytest.mark.battery
def test_frozen_battery_fight_lengths():
    swarm = metrics.summarize(run_battery(
        "ref_ironclad", "starter", "swarm", "generic", 300, SEED))
    assert 5 <= swarm["avg_turns"] <= 7.5
    attr = metrics.summarize(run_battery(
        "ref_ironclad", "starter", "attrition", "generic", 300, SEED))
    assert attr["avg_turns"] >= 12
    boss = metrics.summarize(run_battery(
        "ref_ironclad", "starter", "tank_boss", "generic", 300, SEED))
    assert boss["avg_turns"] >= 10     # A2 needs turn-10 data


@pytest.mark.battery
def test_a7_self_referential_sanity(baseline):
    # Review ruling #3: REF_IRONCLAD starter reaches 70% of its own peak
    # window within the first few turns (no engine to assemble).
    assert baseline["raw"]["A7_setup_tax"] < 6


def test_a6_v2_uptime_component_and_anchor():
    """A6 instrument v2 (R18): application uptime credits the axis
    ADDITIVELY (the baseline applies nothing, so its uptime is 0 and a
    ratio anchor would divide by it). Anchor: identical raws score 3.0;
    50% uptime over baseline adds exactly 3.0 * 0.2 * 0.5 = 0.3."""
    assert axes.A6_INSTRUMENT_VERSION == 2
    base = {ax: 2.0 for ax in axes.AXES}
    base.update(A6_aoe=10.0, A6_debuff=2.0, A6_app=0.0)
    assert axes.normalize(dict(base), base)["A6_utility"] == pytest.approx(3.0)
    lifted = dict(base, A6_app=0.5)
    assert (axes.normalize(lifted, base)["A6_utility"]
            == pytest.approx(3.3))


def test_heuristic_flag_logic():
    flat = {ax: 3.0 for ax in axes.AXES}
    assert any("FLAT" in f for f in axes.heuristic_flags(flat))
    assert any("NO_WEAKNESS" in f for f in axes.heuristic_flags(flat))
    healthy = dict(flat, A1_frontload=4.5, A6_utility=4.2, A2_scaling=1.5)
    assert axes.heuristic_flags(healthy) == []


# --- EB-50: the two declared invariants, as report flags -----------------
#
# `klee-pass-4-plan.md` §0: elite pair A1 4.5 + A6 4.0, A2 capped ≤4.0. The
# flags REPORT; `test_axes_honesty.py` pins that they never assert.

def _conforming() -> dict[str, float]:
    """A reading that satisfies both: elite on exactly A1+A6, A2 under."""
    return dict({ax: 3.0 for ax in axes.AXES},
                A1_frontload=4.5, A6_utility=4.2, A2_scaling=1.5)


# The pass-4 measurement that motivated the ask (1000 fights, seed 42,
# archetype-deck median). It breaches BOTH invariants and flagged nothing.
_KLEE_PASS_4 = dict({ax: 3.0 for ax in axes.AXES},
                    A1_frontload=4.117, A2_scaling=4.097, A6_utility=3.587,
                    A5_velocity=3.043, A7_setup_tax=2.102)


def test_a_conforming_reading_raises_neither_invariant_flag():
    assert axes.invariant_flags(_conforming()) == []


def test_the_measurement_that_prompted_the_ask_now_flags_both():
    flags = axes.invariant_flags(_KLEE_PASS_4)
    assert len(flags) == 2
    assert flags[0].startswith("A2_CEILING") and "4.10" in flags[0]
    # Her measured elite pair was A1+A2, not the declared A1+A6.
    assert flags[1].startswith("ELITE_PAIRING")
    assert "'A2_scaling'" in flags[1] and "'A6_utility'" in flags[1]


def test_the_a2_ceiling_is_a_ceiling_and_not_a_bound():
    """`≤4.0` — exactly 4.0 conforms, and only above it breaches."""
    assert not any(f.startswith("A2_CEILING")
                   for f in axes.invariant_flags(dict(_conforming(),
                                                      A2_scaling=4.0)))
    assert any(f.startswith("A2_CEILING")
               for f in axes.invariant_flags(dict(_conforming(),
                                                  A2_scaling=4.01)))


def test_the_pairing_flag_catches_a_declared_elite_that_fell_short():
    """The half `heuristic_flags` cannot see: right COUNT, wrong axes.

    Two axes ≥4.0 and one ≤2.0 is the balance heuristic's picture of health,
    so it stays silent while the declared identity has quietly swapped A6 for
    A3.
    """
    swapped = dict(_conforming(), A6_utility=3.9, A3_block=4.4)
    assert axes.heuristic_flags(swapped) == []
    flags = axes.invariant_flags(swapped)
    assert len(flags) == 1 and flags[0].startswith("ELITE_PAIRING")


def test_a_reading_with_no_elite_axis_at_all_is_a_pairing_breach():
    assert any(f.startswith("ELITE_PAIRING")
               for f in axes.invariant_flags({ax: 3.0 for ax in axes.AXES}))


def test_the_declared_pair_is_a_parameter():
    """It is declared per character and lives in prose, not the yamls."""
    swapped = dict(_conforming(), A6_utility=3.9, A3_block=4.4)
    assert axes.invariant_flags(
        swapped, elite_pair=("A1_frontload", "A3_block")) == []


@pytest.mark.battery
def test_the_anchor_is_not_scored_against_a_declared_identity(baseline):
    """REF_IRONCLAD starter is flat 3.0 BY CONSTRUCTION and declares no elite
    pair, so `None` (out of scope) is the honest reading — an empty list would
    claim the invariants were checked and held."""
    assert baseline["invariant_flags"] is None


@pytest.mark.battery
def test_a_package_deck_is_out_of_scope_like_the_shape_heuristic(package):
    assert package["invariant_flags"] is None


@pytest.mark.battery
def test_a_character_starter_gets_a_real_reading():
    klee = score_config("klee", "starter", "generic", 40, SEED)
    assert isinstance(klee["invariant_flags"], list)


# --- R204: the demoted declared-identity comparison ------------------------

def test_a_holding_identity_reports_the_verdict_and_no_flag():
    """`[]` is the verdict "checked, it holds" -- not silence."""
    holds = dict({ax: 3.0 for ax in axes.AXES}, A1_frontload=4.5,
                 A2_scaling=2.0)
    assert axes.identity_flags(holds, ["A1_frontload>A2_scaling"]) == []


def test_a_breaching_identity_names_the_comparison_and_both_numbers():
    breaches = dict({ax: 3.0 for ax in axes.AXES}, A1_frontload=2.0,
                    A2_scaling=4.5)
    flags = axes.identity_flags(breaches, ["A1_frontload>A2_scaling"])
    assert len(flags) == 1
    assert flags[0].startswith("DECLARED_IDENTITY")
    assert "A1_frontload>A2_scaling" in flags[0]
    assert "2.0" in flags[0] and "4.5" in flags[0]


def test_the_comparison_is_strict_so_a_tie_breaches():
    """`>` is the yaml's own operator: equal axes do not satisfy it."""
    tied = {ax: 3.0 for ax in axes.AXES}
    assert len(axes.identity_flags(tied, ["A1_frontload>A2_scaling"])) == 1


def test_no_declared_identity_is_none_not_an_empty_list():
    """The anchor declares none, and `[]` there would claim a check that
    never happened -- the same convention `invariant_flags` uses."""
    assert axes.identity_flags({ax: 3.0 for ax in axes.AXES}, []) is None


@pytest.mark.battery
def test_the_anchors_package_declares_no_identity_so_it_reads_none(package):
    """`ref_ironclad` declares no `constraints:`, so BOTH readings are out of
    scope on it -- `None` and not `[]`, which would claim a check that never
    happened."""
    assert package["invariant_flags"] is None
    assert package["identity_flags"] is None


@pytest.mark.battery
def test_a_character_package_deck_still_gets_an_identity_reading():
    """R204 DEMOTED the comparison rather than narrowing it, and the two
    scopes now differ on purpose. The scorecard invariants are out of scope on
    a monoculture package (it reads extreme on both and teaches nothing). The
    identity comparison is NOT: it reported on every deck when it was a gate
    -- `warn (package deck)` -- so it still reports on every deck now that it
    is only a report."""
    klee = score_config("klee", "demolition_weighted", "demolition", 40, SEED)
    assert klee["invariant_flags"] is None
    assert isinstance(klee["identity_flags"], list)
