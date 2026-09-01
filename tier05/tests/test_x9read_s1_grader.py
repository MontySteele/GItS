"""`X9READ-S1`'s grader, on synthetic fixtures — BEFORE the registered run.

The measurement law's order (`review/records/charge-reads-per-turn-registration
-2026-08-13.md` §5.5, §6): the grader lands as its own commit, tested, before
any number of the registered run is looked at. These fixtures are hand-built
logs, not run output — no number here came off a run, and every threshold
asserted is quoted from §5.3 / §5.4.

Each slot gets its PASS / SPLIT / MISS shape, its UNREACHED rule, and — the
one that would silently corrupt a share — a fixture whose FINAL TURN IS
TRUNCATED, which is §2.1's blind spot made into a test rather than a caveat.
"""

from __future__ import annotations

from tier05 import charge_telemetry as ct

#: Two real sheet ids, so the attack/skill split is the sheet's and not the
#: fixture's opinion: `all_streams_flow` is the cost-1 attack that prints a
#: `1_per_2_charge` rider, `gyorin_formation` is the rare SKILL that prints one
#: (§5.1's table).
ATTACK = "all_streams_flow"
SKILL = "gyorin_formation"


def _reads(turn: int, by_source: dict[str, int]) -> list[dict]:
    return [{"event": "charge_read", "turn": turn, "kind": kind,
             "card": None, "bank": 4}
            for kind, n in by_source.items() for _ in range(n)]


def _turn(turn: int, by_source: dict[str, int], completed: bool = True
          ) -> list[dict]:
    """One player turn's events. `completed=False` is §2.1's truncated turn:
    it opened and its reads resolved, but `turn_close` was never reached, so
    no `charge_reads_turn` sample exists."""
    evs: list[dict] = [{"event": "turn_open", "turn": turn}]
    evs += _reads(turn, by_source)
    if completed:
        evs.append({"event": "charge_reads_turn", "turn": turn,
                    "total": sum(by_source.values()),
                    "by_source": dict(by_source)})
    return evs


def _fight(*turns: list[dict]) -> list[dict]:
    return [ev for t in turns for ev in t]


def _agg(log: list[dict], act_i: int = 0) -> dict:
    return ct.aggregate([ct.trace(log, act_i)])


def _uniform(n_turns: int, by_source: dict[str, int], start: int = 1) -> dict:
    log = _fight(*[_turn(start + i, by_source) for i in range(n_turns)])
    return _agg(log)


def _slot(grades: list[dict], slot: str) -> dict:
    return next(row for row in grades if row["slot"] == slot)


# --- X1: mean reads per turn -------------------------------------------------

def test_x1_predicted_split_and_miss_shapes():
    # Mean inside [1.0, 2.0): a pulse every turn and a Garment on half.
    log = _fight(*[_turn(1 + i, {"kurage_pulse": 1} if i % 2 else
                         {"kurage_pulse": 1, "garment": 1})
                   for i in range(6000)])
    predicted = _agg(log)
    assert predicted["levels"]["mean"] == 1.5
    assert _slot(ct.grade(predicted), "X1")["grade"] == "PREDICTED"

    split = _uniform(6000, {"kurage_pulse": 1, "garment": 1})
    assert split["levels"]["mean"] == 2.0
    assert _slot(ct.grade(split), "X1")["grade"] == "SPLIT"

    miss_high = _uniform(6000, {"kurage_pulse": 1, "garment": 2})
    assert _slot(ct.grade(miss_high), "X1")["grade"] == "MISS"

    # MISS LOW is a different finding — the instrument is not seeing the
    # pulse, and §5.3 calls that read INVALID rather than quiet.
    log = _fight(*[_turn(1 + i, {"garment": 1} if i % 2 else {})
                   for i in range(6000)])
    miss_low = _agg(log)
    assert miss_low["levels"]["mean"] < 1.0
    assert _slot(ct.grade(miss_low), "X1")["grade"] == "MISS"


def test_x1_and_x2_unreached_under_five_thousand_sampled_turns():
    thin = _uniform(4999, {"kurage_pulse": 1})
    grades = ct.grade(thin)
    assert _slot(grades, "X1")["grade"] == "UNREACHED"
    assert _slot(grades, "X2")["grade"] == "UNREACHED"
    # X3 is never UNREACHED: a max is defined on any non-empty sample.
    assert _slot(grades, "X3")["grade"] == "PREDICTED"


# --- X2: p90 -----------------------------------------------------------------

def test_x2_p90_predicted_split_and_miss_shapes():
    quiet = _uniform(6000, {"kurage_pulse": 1, "garment": 2})     # every p90 3
    assert quiet["levels"]["p90"] == 3
    assert _slot(ct.grade(quiet), "X2")["grade"] == "PREDICTED"

    busy = _uniform(6000, {"kurage_pulse": 1, "garment": 3, "bonus_formula": 1})
    assert busy["levels"]["p90"] == 5
    assert _slot(ct.grade(busy), "X2")["grade"] == "SPLIT"

    over = _uniform(6000, {"kurage_pulse": 1, "garment": 4, "bonus_formula": 2})
    assert over["levels"]["p90"] == 7
    assert _slot(ct.grade(over), "X2")["grade"] == "MISS"


# --- X3: max -----------------------------------------------------------------

def test_x3_max_predicted_split_and_miss_shapes():
    base = [_turn(1 + i, {"kurage_pulse": 1}) for i in range(10)]

    def with_spike(total: int) -> dict:
        return _agg(_fight(*base, _turn(11, {"garment": total})))

    assert _slot(ct.grade(with_spike(8)), "X3")["grade"] == "PREDICTED"
    assert _slot(ct.grade(with_spike(9)), "X3")["grade"] == "SPLIT"
    assert _slot(ct.grade(with_spike(13)), "X3")["grade"] == "SPLIT"
    assert _slot(ct.grade(with_spike(14)), "X3")["grade"] == "MISS"


# --- X4 / X5: the composition shares -----------------------------------------

def test_x4_garment_share_predicted_split_and_miss_shapes():
    predicted = _uniform(3000, {"kurage_pulse": 2, "garment": 1})   # 33.3%
    assert _slot(ct.grade(predicted), "X4")["grade"] == "PREDICTED"

    split = _uniform(3000, {"kurage_pulse": 1, "garment": 1})       # 50%
    assert _slot(ct.grade(split), "X4")["grade"] == "SPLIT"

    miss = _uniform(3000, {"kurage_pulse": 1, "garment": 3})        # 75%
    assert _slot(ct.grade(miss), "X4")["grade"] == "MISS"


def test_x5_bonus_formula_share_predicted_split_and_miss_shapes():
    predicted = _uniform(3000, {"kurage_pulse": 9, "bonus_formula": 1})  # 10%
    assert _slot(ct.grade(predicted), "X5")["grade"] == "PREDICTED"

    split = _uniform(3000, {"kurage_pulse": 4, "bonus_formula": 1})      # 20%
    assert _slot(ct.grade(split), "X5")["grade"] == "SPLIT"

    miss = _uniform(3000, {"kurage_pulse": 1, "bonus_formula": 1})       # 50%
    assert _slot(ct.grade(miss), "X5")["grade"] == "MISS"


def test_x4_and_x5_unreached_under_five_thousand_completed_turn_reads():
    thin = _uniform(4999, {"kurage_pulse": 1})
    assert thin["completed_reads"] == 4999
    grades = ct.grade(thin)
    assert _slot(grades, "X4")["grade"] == "UNREACHED"
    assert _slot(grades, "X5")["grade"] == "UNREACHED"


# --- the completed-turn restriction, which is the whole point of the revision -

def test_shares_read_completed_turns_only_when_the_final_turn_is_truncated():
    """§2.1's truncation, made a fixture.

    A fight of one completed pulse turn and one TRUNCATED turn whose reads are
    all attack-side. The raw stream says the repeatable sources are 3 of 4
    reads (75%); the completed turns say 0 of 1 (0%). §5.3's revision is that
    the second is what `X4`, `X5` and `W9` Limb A read.
    """
    log = _fight(_turn(1, {"kurage_pulse": 1}),
                 _turn(2, {"garment": 2, "bonus_formula": 1},
                       completed=False))
    m = _agg(log)

    assert m["turns"] == 1                    # one SAMPLE, two turns opened
    assert m["turns_opened"] == 2
    assert m["turns_dropped"] == 1            # R4
    assert m["completed_reads"] == 1
    assert m["raw_total"] == 4                # X7's cross-check sees all four
    assert m["reads_dropped"] == 3

    # The share is taken on the completed turn and on nothing else.
    assert m["share"]["garment"] == 0.0
    assert m["repeatable_share"] == 0.0
    # ... and the raw stream, had it been used, would have said 75%.
    raw_repeatable = sum(m["raw_reads"].get(k, 0)
                         for k in ct.REPEATABLE_KINDS) / m["raw_total"]
    assert raw_repeatable == 0.75


# --- X6: the double read, segmented on PLAY boundaries -----------------------

def _play(turn: int, card: str) -> dict:
    return {"event": "play", "turn": turn, "card": card, "cost": 1}


def test_x6_segments_on_play_boundaries_and_not_on_card_id():
    """The same attack played TWICE in one turn: the first play collects both
    reads, the second only the Garment. Keyed on `card` id the two would
    collide into one segment carrying both; segmented on play boundaries they
    are two plays, one of them double."""
    log = [{"event": "turn_open", "turn": 1},
           _play(1, ATTACK),
           {"event": "charge_read", "turn": 1, "kind": "garment",
            "card": ATTACK, "bank": 4},
           {"event": "charge_read", "turn": 1, "kind": "bonus_formula",
            "card": ATTACK, "bank": 4},
           _play(1, ATTACK),
           {"event": "charge_read", "turn": 1, "kind": "garment",
            "card": ATTACK, "bank": 4},
           {"event": "charge_read", "turn": 1, "kind": "kurage_pulse",
            "card": None, "bank": 4},
           {"event": "charge_reads_turn", "turn": 1, "total": 4,
            "by_source": {"garment": 2, "bonus_formula": 1,
                          "kurage_pulse": 1}}]
    m = _agg(log)
    assert m["attack_plays"] == 2
    assert m["double_plays"] == 1


def test_x6_skill_plays_are_not_attack_plays():
    log = [{"event": "turn_open", "turn": 1},
           _play(1, SKILL),
           {"event": "charge_read", "turn": 1, "kind": "bonus_formula",
            "card": SKILL, "bank": 4},
           {"event": "charge_reads_turn", "turn": 1, "total": 1,
            "by_source": {"bonus_formula": 1}}]
    m = _agg(log)
    assert m["attack_plays"] == 0
    assert m["double_plays"] == 0


def test_x6_predicted_split_and_miss_shapes():
    def deck(n_plays: int, n_double: int) -> dict:
        log: list[dict] = [{"event": "turn_open", "turn": 1}]
        for i in range(n_plays):
            log.append(_play(1, ATTACK))
            log.append({"event": "charge_read", "turn": 1, "kind": "garment",
                        "card": ATTACK, "bank": 4})
            if i < n_double:
                log.append({"event": "charge_read", "turn": 1,
                            "kind": "bonus_formula", "card": ATTACK,
                            "bank": 4})
        log.append({"event": "charge_reads_turn", "turn": 1, "total": 0,
                    "by_source": {}})
        return _agg(log)

    assert _slot(ct.grade(deck(2000, 40)), "X6")["grade"] == "PREDICTED"   # 2%
    assert _slot(ct.grade(deck(2000, 200)), "X6")["grade"] == "SPLIT"     # 10%
    assert _slot(ct.grade(deck(2000, 600)), "X6")["grade"] == "MISS"      # 30%
    # UNREACHED under 1,000 attack plays.
    assert _slot(ct.grade(deck(999, 0)), "X6")["grade"] == "UNREACHED"


# --- X7: the direction of the tail against turn number -----------------------

def _tail(early_per_turn: int, late_per_turn: int, n_late: int = 2500) -> dict:
    early = [_turn(1 + (i % 5), {"garment": early_per_turn})
             for i in range(2500)]
    late = [_turn(6 + (i % 5), {"garment": late_per_turn})
            for i in range(n_late)]
    return _agg(_fight(*early, *late))


def test_x7_predicted_split_and_miss_shapes():
    # A rise of exactly one read is the SPLIT boundary (gap >= 1.0).
    rise_small = _agg(_fight(
        *[_turn(1 + (i % 5), {"garment": 1}) for i in range(2500)],
        *[_turn(6 + (i % 5), {"garment": 1, "kurage_pulse": 1})
          for i in range(1250)],
        *[_turn(6 + (i % 5), {"garment": 1}) for i in range(1250)]))
    assert 0 < rise_small["gap"] < 1.0
    assert _slot(ct.grade(rise_small), "X7")["grade"] == "PREDICTED"

    assert _slot(ct.grade(_tail(1, 2)), "X7")["grade"] == "SPLIT"
    assert _slot(ct.grade(_tail(2, 2)), "X7")["grade"] == "MISS"   # flat
    assert _slot(ct.grade(_tail(2, 1)), "X7")["grade"] == "MISS"   # falls


def test_x7_unreached_under_two_thousand_late_turns():
    thin = _tail(1, 2, n_late=1999)
    assert _slot(ct.grade(thin), "X7")["grade"] == "UNREACHED"


# --- W9 ----------------------------------------------------------------------

def test_w9_limb_a_fires_alone_on_the_composition_share():
    m = _uniform(3000, {"kurage_pulse": 1, "garment": 2})     # repeatable 2/3
    w9 = ct.evaluate_w9(m)
    assert w9["fired"] and w9["limb_a"] and not w9["limb_b"]
    assert abs(w9["limb_a_margin"] - (2 / 3 - 0.5)) < 1e-9


def test_w9_limb_b_fires_alone_on_the_double_read_share():
    log: list[dict] = [{"event": "turn_open", "turn": 1}]
    for i in range(100):
        log.append(_play(1, ATTACK))
        log.append({"event": "charge_read", "turn": 1, "kind": "garment",
                    "card": ATTACK, "bank": 4})
        if i < 60:
            log.append({"event": "charge_read", "turn": 1,
                        "kind": "bonus_formula", "card": ATTACK, "bank": 4})
    log.append({"event": "charge_reads_turn", "turn": 1, "total": 1,
                "by_source": {"kurage_pulse": 1}})
    w9 = ct.evaluate_w9(_agg(log))
    assert w9["fired"] and w9["limb_b"] and not w9["limb_a"]


def test_w9_does_not_fire_and_records_both_margins():
    m = _uniform(3000, {"kurage_pulse": 3, "garment": 1})      # repeatable 25%
    w9 = ct.evaluate_w9(m)
    assert not w9["fired"]
    assert w9["limb_a_margin"] < 0 and w9["limb_b_margin"] < 0
    assert w9["turns_without_pulse"] == 0


def test_w9_severity_indicator_rides_the_p50_and_gates_nothing():
    quiet = ct.evaluate_w9(_uniform(3000, {"kurage_pulse": 1, "garment": 2}))
    assert quiet["fired"] and quiet["severity"] == "quiet"

    loud = ct.evaluate_w9(_uniform(3000, {"kurage_pulse": 1, "garment": 5}))
    assert loud["p50"] > ct.DERIVED_CEILING
    assert loud["fired"] and loud["severity"] == "loud"

    # A p50 above the ceiling with a quiet composition still does not fire:
    # the level LABELS a firing, it never causes one.
    level_only = ct.evaluate_w9(_uniform(3000, {"kurage_pulse": 7,
                                                "garment": 1}))
    assert level_only["p50"] > ct.DERIVED_CEILING
    assert not level_only["fired"]


# --- R1-R4, recorded and graded by nothing -----------------------------------

def test_recorded_not_graded_fields_are_present():
    log = _fight(_turn(1, {"kurage_pulse": 1, "garment": 1}),
                 _turn(2, {"kurage_pulse": 1}, completed=False))
    m = _agg(log, act_i=2)
    assert set(m["per_kind"]) == set(ct.READ_KINDS)          # R2
    assert m["bank_median"]["garment"] == 4                  # R3
    assert m["turns_dropped"] == 1                           # R4
    assert m["by_act"]["2"]["turns"] == 1                    # R1's act split
