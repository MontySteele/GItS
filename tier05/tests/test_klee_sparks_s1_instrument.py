"""`KLEESPARK-S1`'s instrument (`tier05/exp_klee_sparks_s1.py`), pinned.

The registration is `review/active/klee-sparks-2026-08-29.md` §17 and it was
committed before the instrument; the instrument was committed before the run.
What this file pins is the three things a reader of the record has to be able
to trust WITHOUT re-running it:

  1. **The arm is the arm §17.2 registered.** The flag is on, the excluded
     Rare is excluded, the three `EB-218` twins and PICK 4's five conversions
     are offerable, and Rummage is NOT -- which is `S5`'s registered instrument
     check and the reason it is a check rather than a reading.
  2. **The observer is EMIT-ONLY.** An observed batch is element-for-element
     the same batch as an unobserved one at the same seeds, and the world is
     restored afterwards -- flag, substitution map and all four patches.
  3. **The grader applies §17.4's thresholds and no others.** Each slot is
     driven over its own boundaries with synthetic arm dicts, so a threshold
     that drifts after a number is seen fails here rather than passing quietly.
"""

from __future__ import annotations

import contextlib
import copy

from tier0 import constants as C
from tier0.content import loader
from tier05 import cells, exp_klee_sparks_s1 as s1, model, rewards


@contextlib.contextmanager
def _arm_world():
    """§17.2's arm, for a read that needs the arm's cards to exist.

    A `proto_` id resolves through `loader._substituted_card_index`, which is
    EMPTY with the flag off, so any sheet read of a prototype row has to sit
    inside this window -- which is also why `_observe` reduces inside its own.
    """
    original = dict(C.SPARK_ALT_POOL_SUBS)
    C.SPARK_ALT_COST_ENABLED = True
    C.SPARK_ALT_POOL_SUBS.pop(s1.EXCLUDED_SUB_KEY, None)
    s1._clear_caches()
    try:
        yield
    finally:
        C.SPARK_ALT_COST_ENABLED = False
        C.SPARK_ALT_POOL_SUBS.clear()
        C.SPARK_ALT_POOL_SUBS.update(original)
        s1._clear_caches()


# -- 1. the arm ---------------------------------------------------------------

def test_flag_on_pool_offers_the_registered_arm_and_not_rummage():
    """§17.2's arm, read off the same seam the drafter reads."""
    with _arm_world():
        pool = rewards.character_pool("klee")
        ids = {c.id for cards in pool.values() for c in cards}

    # the three EB-218 twins -- the only reachable non-damage sinks
    for cid in ("proto_powder_charge_spark", "proto_hold_the_line_spark",
                "proto_smoke_and_sparks_spark"):
        assert cid in ids, cid
    # PICK 4's five one-for-one conversions
    for cid in ("proto_spark_strike", "proto_spark_double_tap",
                "proto_spark_sweep", "proto_spark_blast",
                "proto_spark_finisher"):
        assert cid in ids, cid
    # EXCLUDED on §12.2's grounds, exactly as KLEESPARK-W2 excluded it, and
    # the shipped Rare is back in its slot so the tier's odds are untouched.
    assert "proto_true_spark_knight" not in ids
    assert "true_spark_knight" in ids
    # S5's registered instrument check: Rummage has no pool seam at all.
    assert s1.RUMMAGE not in ids
    assert s1.RUMMAGE not in C.SPARK_ALT_POOL_SUBS.values()


def test_maker_and_sink_reads_are_the_sheet_and_not_play():
    with _arm_world():
        _maker_and_sink_body()


def _maker_and_sink_body():
    assert s1._is_maker("proto_pop_spark")
    assert not s1._is_sink("proto_pop_spark")
    assert s1._is_sink("proto_kaboom_sink")
    assert not s1._is_maker("proto_kaboom_sink")
    assert s1._makers_sinks(["proto_pop_spark", "proto_kaboom_sink",
                             "proto_kaboom_sink"]) == (1, 2)
    assert s1._ratio(["proto_pop_spark", "proto_kaboom_sink"]) == 1.0
    # §17.4: a deck with no sink has no ratio and is excluded, not counted 0.
    assert s1._ratio(["proto_pop_spark"]) is None


def test_peak_bank_is_the_max_printed_total():
    log = [{"event": "gain_spark", "total": 1},
           {"event": "gain_spark", "total": 3},
           {"event": "spend_spark", "total": 1},
           {"event": "damage", "total": 99}]
    assert s1._peak_bank(log) == 3
    assert s1._peak_bank([]) == 0
    assert s1._peak_bank([{"event": "damage", "total": 9}]) == 0


# -- 2. the observer ----------------------------------------------------------

_CELL = s1.CELL.but(runs=3, seed=4242, name="s1-test")


def test_observer_is_emit_only_and_restores_the_world():
    flag_before = C.SPARK_ALT_COST_ENABLED
    subs_before = copy.deepcopy(C.SPARK_ALT_POOL_SUBS)
    patched_before = (model.run_one, model.run_fight,
                      model._RunCtx.mark_hindsight, model.make_pilot)

    observed, obs, _arm_read = s1._observe(True, _CELL)

    assert C.SPARK_ALT_COST_ENABLED == flag_before
    assert C.SPARK_ALT_POOL_SUBS == subs_before
    assert (model.run_one, model.run_fight, model._RunCtx.mark_hindsight,
            model.make_pilot) == patched_before

    # The same batch, run WITHOUT the observer, under the same arm.
    with _arm_world():
        plain = _CELL.run()

    assert [r.seed for r in observed] == [r.seed for r in plain]
    assert [r.deck_ids for r in observed] == [r.deck_ids for r in plain]
    assert [r.node_kinds for r in observed] == [r.node_kinds for r in plain]
    assert [r.won for r in observed] == [r.won for r in plain]

    # And it actually observed something: one record per run, per-floor deck
    # snapshots, and a fight record for every fight the runs fought.
    assert len(obs.runs) == len(observed)
    assert sum(len(r["fights"]) for r in obs.runs) == sum(
        len(r.fight_stats) for r in observed)
    assert any(run["floors"] for run in obs.runs)


def test_flag_off_control_holds_no_prototype_row():
    _, _obs, arm = s1._observe(False, _CELL)
    assert arm["decks_with_any_proto_share"] == 0.0
    assert arm["runs_with_rummage"] == 0
    assert arm["runs"] == _CELL.runs


def test_reduce_reports_every_field_the_slate_grades():
    _, _obs, arm = s1._observe(True, _CELL)
    for key in ("peak_median", "peak_ge2_share", "turns_nd_affordable_share",
                "decks_with_nd_sink_share", "ratio_median", "ratio_n",
                "runs_with_rummage", "fights", "turns", "runs"):
        assert key in arm, key
    assert set(arm["ratio_median"]) == {"5", "10", "15"}


# -- 3. the grader ------------------------------------------------------------

def _arm(**over):
    base = {"runs": 600, "fights": 4000, "turns": 20000,
            "peak_median": 2.0, "peak_ge2_share": 0.7, "peak_mean": 2.0,
            "peak_hist": {}, "turns_nd_affordable": 4000,
            "turns_nd_affordable_share": 0.2,
            "turns_nd_playable_share": 0.2, "turns_any_affordable_share": 0.4,
            "decks_with_nd_sink": 400, "decks_with_nd_sink_share": 0.66,
            "decks_with_any_proto_share": 0.9,
            "ratio_median": {"5": 1.0, "10": 0.8, "15": 0.5},
            "ratio_n": {"5": 600, "10": 400, "15": 200},
            "runs_with_rummage": 0, "rummage_share": 0.0,
            "win_share": 0.05, "decksize_mean": 18.0}
    base.update(over)
    return base


def _grade_of(slot, **over):
    return {g["slot"]: g["grade"] for g in s1._grade(_arm(**over))}[slot]


def test_s1_thresholds():
    assert _grade_of("S1") == "PREDICTED"
    assert _grade_of("S1", peak_median=1.0) == "SPLIT"
    assert _grade_of("S1", peak_ge2_share=0.59) == "SPLIT"
    assert _grade_of("S1", peak_median=1.0, peak_ge2_share=0.1) == "MISS"
    assert _grade_of("S1", fights=99) == "UNREACHED"


def test_s2_thresholds():
    assert _grade_of("S2", turns_nd_affordable_share=0.15) == "PREDICTED"
    assert _grade_of("S2", turns_nd_affordable_share=0.1499) == "SPLIT"
    assert _grade_of("S2", turns_nd_affordable_share=0.05) == "SPLIT"
    assert _grade_of("S2", turns_nd_affordable_share=0.0499) == "MISS"
    # UNREACHED is the OFFER's fault, not the bank's -- §17.4's own rule.
    assert _grade_of("S2", decks_with_nd_sink=0,
                     turns_nd_affordable_share=0.0) == "UNREACHED"


def test_s3_thresholds():
    assert _grade_of("S3", decks_with_nd_sink_share=0.50) == "PREDICTED"
    assert _grade_of("S3", decks_with_nd_sink_share=0.4999) == "SPLIT"
    assert _grade_of("S3", decks_with_nd_sink_share=0.20) == "SPLIT"
    assert _grade_of("S3", decks_with_nd_sink_share=0.1999) == "MISS"


def test_s4_thresholds_and_the_inherited_ratio():
    assert _grade_of("S4") == "PREDICTED"
    # fell, but outside the band
    assert _grade_of("S4", ratio_median={"5": 1.0, "10": 1.0,
                                         "15": 0.9}) == "SPLIT"
    # in the band, but did not fall
    assert _grade_of("S4", ratio_median={"5": 0.4, "10": 0.4,
                                         "15": 0.5}) == "SPLIT"
    assert _grade_of("S4", ratio_median={"5": 0.1, "10": 0.2,
                                         "15": 0.9}) == "MISS"
    assert _grade_of("S4", ratio_n={"5": 600, "10": 400,
                                    "15": 29}) == "UNREACHED"
    assert _grade_of("S4", ratio_median={"5": 1.0, "10": 0.8,
                                         "15": None}) == "UNREACHED"


def test_s5_is_an_instrument_check():
    assert _grade_of("S5") == "PREDICTED"
    assert _grade_of("S5", runs_with_rummage=1, rummage_share=0.002) == "MISS"


def test_cell_is_serial_because_the_observer_cannot_reach_a_worker():
    assert s1.CELL.jobs == 1
    assert s1.CELL.character == "klee" and s1.CELL.archetype == "demolition"
    assert s1.CELL.runs == cells.CANONICAL.runs
    assert s1.CELL.seed == cells.CANONICAL.seed
    assert s1.CELL.realistic is True
    assert s1.main(["--runs", "1", "--seed", "1"]) is not None


def test_non_damage_sink_list_is_section_16_4s():
    """§16.4 named four; three are reachable under this arm's pool."""
    assert set(s1.NON_DAMAGE_SINKS) == {
        "proto_powder_charge_spark", "proto_hold_the_line_spark",
        "proto_smoke_and_sparks_spark", "proto_spark_priced_draw"}
    assert len(s1.DAMAGE_SINKS) == 6
    with _arm_world():
        for cid in s1.NON_DAMAGE_SINKS + s1.DAMAGE_SINKS:
            loader.peek_card(cid)  # every id resolves under the arm's flag
