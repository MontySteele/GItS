"""`KURAGECAD-S1`'s instrument (`tier05/exp_kurage_cadence_s1.py`), pinned.

The registration is `review/active/kokomi-kurage-memory-2026-08-29.md` §15 and
it was committed before the instrument; the instrument is committed before the
run. What this file pins is the three things a reader of the record has to be
able to trust WITHOUT re-running it:

  1. **The per-turn reduction is §15.2's definitions and not a paraphrase.** A
     turn's state, its queue length, and the separation of her own plays from
     the memory's copy are driven over hand-built logs.
  2. **The observer is EMIT-ONLY.** An observed batch is element-for-element the
     same batch as an unobserved one at the same seeds, and the world is
     restored afterwards -- flag, both patches and the three caches.
  3. **The grader applies §15.4's thresholds and no others.** Each slot is
     driven over its own boundaries with synthetic arm dicts, so a threshold
     that drifts after a number is seen fails here rather than passing quietly.
"""

from __future__ import annotations

from tier0 import constants as C
from tier05 import cells, exp_kurage_cadence_s1 as s1, model


# -- 1. the reduction ---------------------------------------------------------

def _log(*rows):
    return [dict(r) for r in rows]


def test_a_turns_state_is_its_one_memory_event():
    log = _log({"event": "turn_open"},
               {"event": "kurage_memory_fire", "price": 3, "bank": 9,
                "remaining": 2, "card": "x", "rule": "exhaust"},
               {"event": "play", "card": "x"},
               {"event": "play", "card": "own"},
               {"event": "turn_open"},
               {"event": "kurage_memory_blocked", "price": 6, "bank": 1,
                "queued": 4},
               {"event": "turn_open"},
               {"event": "kurage_memory_empty", "bank": 0})
    t = s1.trace(log, act_i=1)
    assert [r["state"] for r in t["turns"]] == ["fire", "blocked", "empty"]
    # §15.2: the length at TURN START -- `remaining` is post-pop, so the fire
    # turn's queue was one longer than what the event reports as left.
    assert [r["qlen"] for r in t["turns"]] == [3, 4, 0]
    assert all(r["act"] == 1 for r in t["turns"])


def test_her_own_plays_are_the_turns_plays_minus_the_turns_fires():
    log = _log({"event": "turn_open"},
               {"event": "kurage_memory_fire", "price": 0, "bank": 4,
                "remaining": 0, "card": "gorou", "rule": "exhaust"},
               {"event": "play", "card": "gorou"},
               {"event": "turn_open"},
               {"event": "kurage_memory_fire", "price": 3, "bank": 4,
                "remaining": 0, "card": "sayu", "rule": "muster"},
               {"event": "play", "card": "sayu"},
               {"event": "play", "card": "her_own"})
    t = s1.trace(log, act_i=0)
    assert [r["own_plays"] for r in t["turns"]] == [0, 1]
    # the memory-only turn is the one where the copy was the whole line
    assert [r["memory_only"] for r in t["turns"]] == [True, False]


def test_enrolments_refusals_and_prices_are_read_off_their_own_events():
    log = _log({"event": "turn_open"},
               {"event": "kurage_remember", "rule": "muster", "price": 3,
                "cost": 1, "card": "a", "queued": 1},
               {"event": "kurage_remember", "rule": "exhaust", "price": 0,
                "cost": 0, "card": "b", "queued": 2},
               {"event": "kurage_memory_refused", "card": "c",
                "rule": "exhaust", "reason": "junk"},
               {"event": "kurage_memory_full", "card": "d"})
    t = s1.trace(log, act_i=2)
    assert [e["rule"] for e in t["enrolments"]] == ["muster", "exhaust"]
    assert [e["price"] for e in t["enrolments"]] == [3, 0]
    assert t["refusals"] == {"junk": 1}
    assert t["full"] == 1


def test_events_before_the_first_turn_open_belong_to_no_turn():
    """Combat setup emits before the first player turn; a turn that does not
    exist cannot be a denominator."""
    t = s1.trace(_log({"event": "play", "card": "x"},
                      {"event": "turn_open"}), act_i=0)
    assert len(t["turns"]) == 1
    assert t["turns"][0]["plays"] == 0


# -- 2. the observer ----------------------------------------------------------

_CELL = s1.CELL.but(runs=3, seed=4242, name="kuragecad-test")


def test_observer_is_emit_only_and_restores_the_world():
    flag_before = C.KURAGE_MEMORY
    patched_before = (model.run_one, model._RunCtx._record_traces)

    observed, obs, arm = s1._observe(True, _CELL)

    assert C.KURAGE_MEMORY == flag_before
    assert (model.run_one, model._RunCtx._record_traces) == patched_before

    # The same batch, run WITHOUT the observer, under the same arm.
    C.KURAGE_MEMORY = True
    s1._clear_caches()
    try:
        plain = _CELL.run()
    finally:
        C.KURAGE_MEMORY = flag_before
        s1._clear_caches()

    assert [r.seed for r in observed] == [r.seed for r in plain]
    assert [r.deck_ids for r in observed] == [r.deck_ids for r in plain]
    assert [r.node_kinds for r in observed] == [r.node_kinds for r in plain]
    assert [r.won for r in observed] == [r.won for r in plain]

    # And it actually observed something: one record per run, one fight record
    # per fight, and the memory did something on at least one turn.
    assert len(obs.runs) == len(observed)
    assert sum(len(r["fights"]) for r in obs.runs) == sum(
        len(r.fight_stats) for r in observed)
    assert arm["turns"] > 0
    assert arm["fire_share"] + arm["blocked_share"] + arm["empty_share"] > 0


def test_the_flag_off_control_never_sees_a_memory_event():
    _, _obs, arm = s1._observe(False, _CELL)
    assert arm["runs"] == _CELL.runs
    assert arm["turns"] > 0
    assert arm["fires"] == 0 and arm["enrolments"] == 0
    assert arm["fire_share"] == 0.0 and arm["blocked_share"] == 0.0
    assert arm["no_state_share"] == 1.0


def test_reduce_reports_every_field_the_slate_grades():
    _, _obs, arm = s1._observe(True, _CELL)
    for key in ("fire_share", "by_act", "rule_share", "blocked_share",
                "memory_play_share", "memory_only_share", "free_fire_share",
                "qlen_median", "qlen_p95", "exhaust_median", "ethereal_decks",
                "ethereal_enrolments", "turns", "fires", "enrolments"):
        assert key in arm, key


# -- 3. the grader ------------------------------------------------------------

def _arm(**over):
    base = {"runs": 600, "fights": 6000, "turns": 30000, "plays": 90000,
            "fire_share": 0.25, "blocked_share": 0.10, "empty_share": 0.60,
            "no_state_share": 0.05,
            "by_act": {"0": {"turns": 12000, "fire_share": 0.20,
                             "blocked_share": 0.1, "empty_share": 0.7},
                       "2": {"turns": 6000, "fire_share": 0.30,
                             "blocked_share": 0.1, "empty_share": 0.6}},
            "enrolments": 4000, "rule_share": {"exhaust": 0.7, "muster": 0.3},
            "memory_play_share": 0.10, "memory_only_share": 0.05,
            "fires": 7000, "free_fire_share": 0.30, "fire_price_median": 3.0,
            "fire_bank_median": 6.0,
            "qlen_median": 2.0, "qlen_p95": 5.0, "qlen_max": 11,
            "exhaust_median": 5.0, "exhaust_mean": 5.2,
            "ethereal_decks": 0, "ethereal_enrolments": 0,
            "fires_per_run_mean": 11.0, "fires_per_run_median": 10.0,
            "fires_per_run_max": 40, "fires_per_fight_mean": 1.2,
            "refusals": {}, "queue_full_events": 0,
            "win_share": 0.02, "decksize_mean": 22.0}
    base.update(over)
    return base


def _grade_of(slot, **over):
    return {g["slot"]: g["grade"] for g in s1._grade(_arm(**over))}[slot]


def test_c1_thresholds():
    assert _grade_of("C1") == "PREDICTED"
    assert _grade_of("C1", fire_share=0.20) == "PREDICTED"
    assert _grade_of("C1", fire_share=0.1999) == "SPLIT"
    assert _grade_of("C1", fire_share=0.05) == "SPLIT"
    assert _grade_of("C1", fire_share=0.0499) == "MISS"
    assert _grade_of("C1", turns=499) == "UNREACHED"


def test_c2_thresholds():
    assert _grade_of("C2") == "PREDICTED"
    # rose, but by less than a quarter
    assert _grade_of("C2", by_act={"0": {"turns": 100, "fire_share": 0.20},
                                   "2": {"turns": 6000,
                                         "fire_share": 0.21}}) == "SPLIT"
    assert _grade_of("C2", by_act={"0": {"turns": 100, "fire_share": 0.30},
                                   "2": {"turns": 6000,
                                         "fire_share": 0.20}}) == "MISS"
    assert _grade_of("C2", by_act={"0": {"turns": 100, "fire_share": 0.2},
                                   "2": {"turns": 199,
                                         "fire_share": 0.9}}) == "UNREACHED"
    assert _grade_of("C2", by_act={"0": {"turns": 100,
                                         "fire_share": 0.2}}) == "UNREACHED"


def test_c3_thresholds():
    assert _grade_of("C3") == "PREDICTED"
    assert _grade_of("C3", rule_share={"exhaust": 0.9,
                                       "muster": 0.1}) == "SPLIT"
    assert _grade_of("C3", rule_share={"exhaust": 0.4,
                                       "muster": 0.6}) == "SPLIT"
    assert _grade_of("C3", rule_share={"exhaust": 0.4,
                                       "muster": 0.1}) == "MISS"
    assert _grade_of("C3", enrolments=199) == "UNREACHED"


def test_c4_thresholds():
    assert _grade_of("C4") == "PREDICTED"
    assert _grade_of("C4", blocked_share=0.25) == "PREDICTED"
    assert _grade_of("C4", blocked_share=0.2501) == "SPLIT"
    assert _grade_of("C4", blocked_share=0.50) == "SPLIT"
    assert _grade_of("C4", blocked_share=0.5001) == "MISS"


def test_c5_thresholds():
    assert _grade_of("C5") == "PREDICTED"
    assert _grade_of("C5", memory_play_share=0.26) == "SPLIT"
    assert _grade_of("C5", memory_only_share=0.11) == "SPLIT"
    assert _grade_of("C5", memory_play_share=0.4,
                     memory_only_share=0.5) == "MISS"
    assert _grade_of("C5", turns=499) == "UNREACHED"


def test_c6_thresholds():
    assert _grade_of("C6") == "PREDICTED"
    assert _grade_of("C6", free_fire_share=0.50) == "PREDICTED"
    assert _grade_of("C6", free_fire_share=0.5001) == "SPLIT"
    assert _grade_of("C6", free_fire_share=0.75) == "SPLIT"
    assert _grade_of("C6", free_fire_share=0.7501) == "MISS"
    assert _grade_of("C6", fires=99) == "UNREACHED"


def test_c7_thresholds():
    assert _grade_of("C7") == "PREDICTED"
    assert _grade_of("C7", qlen_median=3.0001) == "SPLIT"
    assert _grade_of("C7", qlen_p95=8.1) == "SPLIT"
    assert _grade_of("C7", qlen_median=9.0, qlen_p95=30.0) == "MISS"
    assert _grade_of("C7", turns=499) == "UNREACHED"


def test_c8_thresholds():
    assert _grade_of("C8") == "PREDICTED"
    assert _grade_of("C8", exhaust_median=4.0) == "PREDICTED"
    assert _grade_of("C8", exhaust_median=3.9) == "SPLIT"
    assert _grade_of("C8", exhaust_median=2.0) == "SPLIT"
    assert _grade_of("C8", exhaust_median=1.9) == "MISS"


def test_c9_is_an_instrument_check():
    assert _grade_of("C9") == "PREDICTED"
    assert _grade_of("C9", ethereal_decks=1) == "MISS"
    assert _grade_of("C9", ethereal_enrolments=1) == "MISS"


def test_cell_is_serial_because_the_observer_cannot_reach_a_worker():
    assert s1.CELL.jobs == 1
    assert s1.CELL.character == "kokomi" and s1.CELL.archetype == "commander"
    assert s1.CELL.runs == cells.CANONICAL.runs
    assert s1.CELL.seed == cells.CANONICAL.seed
    assert s1.CELL.realistic is True
    assert s1.main(["--runs", "1", "--seed", "1"]) is not None


def test_ethereal_is_unreachable_in_this_arm_which_is_c9s_whole_point():
    """§15.2's seam read, taken off the sheets rather than off a run."""
    from tier05 import rewards
    C.KURAGE_MEMORY = True
    s1._clear_caches()
    try:
        pool = rewards.character_pool("kokomi")
        ids = {c.id for cards in pool.values() for c in cards}
        ids |= set(loader_starting_ids())
        assert not any(s1._is_ethereal(cid) for cid in ids)
        # and the pool swap the arm depends on IS in place
        assert C.KURAGE_MEMORY_POOL_ADD in ids
        assert C.KURAGE_MEMORY_POOL_DROP not in ids
    finally:
        C.KURAGE_MEMORY = False
        s1._clear_caches()


def loader_starting_ids():
    from tier0.content import loader
    return loader.starting_deck("kokomi")
