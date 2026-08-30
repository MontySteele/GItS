"""EB-203 AND EB-202: the two instrument defects `KLEESPARK-R1` surfaced.

Both locks are stated on the ROUND'S OWN SEALED RECORD rather than on a
fixture invented for them, because both defects were invisible to every check
the round ran and visible only in the pair read. A lock written on a synthetic
board would be a lock on the sentence I wrote, not on the failure.

  * **EB-203** -- `t01` and `t07`'s local-seat forms are refused
    `target_missing`, and Duck and Cover's `target: null` on that same `t07`
    line stays legal. The sealed forms are read-only inputs (R101b); nothing
    here writes into the closed directories.
  * **EB-202** -- the eight committed `KLEESPARK-R1` boards refuse `P1` at
    threshold 4 and NAME the ceiling 3, on the same three boards the packet's
    erratum names (`t02`, `t03`, `t06`).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from understudy import (local_tester, qualify, resource_order, slot_plan,
                        staged_turn, targeting)

REPO = Path(__file__).resolve().parents[2]
QA = REPO / "review" / "qa"
SPARKS = REPO / "understudy" / "turns" / "klee-sparks-r1"
LOCAL_FORM = "form-local-qwen3-8-27b-ud-q4-k-xl.json"


def _sealed_line(turn_id: str) -> list[dict]:
    blob = json.loads((QA / turn_id / LOCAL_FORM).read_text(encoding="utf-8"))
    return list(blob["chosen_line"])


# ============================================================== EB-203 =====

def test_the_two_sealed_lines_the_bridge_refused_are_refused_here(tmp_path):
    """THE LOCK. `t01` and `t07` carried a null target on a card that aims.

    These are the two of eight lines `KLEESPARK-R1` sealed and could not
    replay. The refusal names the play, so the reason is actionable off the
    page the reader was shown.
    """
    for turn_id, expected in (("klee-sparks-r1-t01", "Powder Pop"),
                              ("klee-sparks-r1-t07", "Powder Pop")):
        d = QA / turn_id
        summary = targeting.summary(_sealed_line(turn_id),
                                    hand=targeting.packet_titles(d))
        assert summary["refused"], turn_id
        assert expected in [h["card"] for h in summary["findings"]]
        assert "target_missing" in staged_turn.apply_falsifiers(
            turn_id, {"chosen_line": _sealed_line(turn_id)},
            packet_sha=None, closeness=None, targets=summary)


def test_a_no_target_cards_null_is_legal():
    """`target: null` is the RIGHT answer for a card that aims at nobody.

    Duck and Cover is on `t07`'s own refused line with a null target and it is
    not one of the findings -- the refusal is about the aimed card beside it,
    which is the whole difference between this check and "always name an
    enemy".
    """
    line = _sealed_line("klee-sparks-r1-t07")
    duck = [p for p in line if p["card"] == "Duck and Cover"]
    assert duck and duck[0]["target"] is None
    hits = targeting.findings(line)
    assert "Duck and Cover" not in [h["card"] for h in hits]
    # And alone, that play refuses nothing at all.
    assert not targeting.findings(duck)


def test_a_clean_line_is_not_refused():
    """`t02`'s sealed line aims everything it must, and survives the rule."""
    summary = targeting.summary(_sealed_line("klee-sparks-r1-t02"))
    assert not summary["refused"]
    assert not summary["findings"]


def test_the_rule_is_the_effect_spec_and_not_the_card_type():
    """A Skill that aims (Powder Pop) needs a target; an AoE Attack does not.

    Typing the rule off `type: attack` would have been wrong in both
    directions, and both directions are pinned here.
    """
    index = resource_order.card_index()
    assert targeting.takes_a_target("Powder Pop", index=index)      # Skill
    assert targeting.takes_a_target("Kaboom!", index=index)         # Attack
    assert not targeting.takes_a_target("Tinder Toss", index=index)  # AoE
    assert not targeting.takes_a_target("Duck and Cover", index=index)


def test_a_title_no_sheet_prints_refuses_nothing():
    """The same call `resource_order.unresolved` makes: a missing row names
    the harness, not the reading, so it may not refuse a form."""
    assert not targeting.findings([{"card": "A Card That Does Not Exist"}])


def test_the_refusal_prints_the_hands_aimed_cards():
    """Half a message is not actionable: the refusal lists what takes a target."""
    d = QA / "klee-sparks-r1-t07"
    summary = targeting.summary(_sealed_line("klee-sparks-r1-t07"),
                                hand=targeting.packet_titles(d))
    assert summary["hand_takes_a_target"] == ["Firework Finale", "Fwoosh!",
                                              "Powder Pop"]
    assert "Duck and Cover" not in summary["hand_takes_a_target"]


def test_the_derivation_is_recorded_because_the_packet_has_none():
    """The packet carries NO targeting field, so the summary says where the
    fact came from. A refusal whose source is unrecorded is unarguable."""
    summary = targeting.summary([{"card": "Kaboom!"}])
    assert "card sheets" in summary["derived_from"]
    assert "M63" in summary["repair"]
    hand = json.loads((QA / "klee-sparks-r1-t07" /
                       "packet.json").read_text(encoding="utf-8"))
    for card in hand["board"]["hand"]:
        assert "target" not in card


def test_the_grade_carries_the_reading_even_when_it_survives(tmp_path):
    """`targets` rides every verdict, so a clean form records that it ran."""
    qa = tmp_path / "qa"
    (qa / "t").mkdir(parents=True)
    verdict = staged_turn.grade("t", {
        "grader": {"id": "x"},
        "chosen_line": [{"card": "Duck and Cover", "target": None}],
        "q1_what_did_you_play": "a", "q2_other_line_considered": "b",
        "q3_what_it_gave_up": "c", "q4_different_intent": "yes"},
        root=qa)
    assert verdict["verdict"] == "SURVIVES"
    assert verdict["targets"]["refused"] is False


def test_the_falsifier_is_named_in_the_table():
    """Every refusal this funnel can make is data a reader can find."""
    assert "target_missing" in staged_turn.FALSIFIERS
    assert "aim" in staged_turn.FALSIFIERS["target_missing"]


# ============================================================== EB-202 =====

def _sparks_turns() -> list:
    return [staged_turn.load(p) for p in sorted(SPARKS.glob("t*.yaml"))]


def test_p1s_threshold_of_four_is_refused_at_a_ceiling_of_three():
    """THE LOCK, on the committed board set and its own registered threshold.

    The packet's erratum counted three boards that could pose `P1` at all --
    `t02`, `t03`, `t06` -- against a threshold of four. The check has to reach
    the same three and name the same number.
    """
    turns = _sparks_turns()
    assert len(turns) == 8
    slots = slot_plan.load_slots(SPARKS)
    assert [s.id for s in slots] == ["P1"]
    row = slot_plan.ceiling(slots[0], turns)
    assert row["threshold"] == 4
    assert row["ceiling"] == 3
    assert row["qualifying"] == ["klee-sparks-r1-t02", "klee-sparks-r1-t03",
                                 "klee-sparks-r1-t06"]
    assert not row["reachable"]
    refusals = slot_plan.refusals([row])
    assert len(refusals) == 1
    assert "threshold 4" in refusals[0] and "ceiling of 3" in refusals[0]


@pytest.mark.parametrize("turn_id,why", [
    ("klee-sparks-r1-t07", "a bank of 4 pays 3 + 1 outright"),
    ("klee-sparks-r1-t01", "bank 0: nothing is reachable"),
    ("klee-sparks-r1-t04", "the Rare Power prices no Sparks"),
])
def test_the_boards_that_cannot_pose_the_question_do_not_qualify(turn_id, why):
    """The three shapes the erratum names, each for its own reason."""
    slot = slot_plan.load_slots(SPARKS)[0]
    turn = next(t for t in _sparks_turns() if t.id == turn_id)
    assert not slot.qualifies(turn), why


def test_an_undefined_fact_makes_a_clause_false_rather_than_raising():
    """A board that cannot be ASKED does not qualify, and does not explode.

    `t04`'s hand prices no Spark use, so `min_spark_price` is undefined; the
    clause is false and the board is simply not counted.
    """
    turn = next(t for t in _sparks_turns() if t.id == "klee-sparks-r1-t04")
    assert slot_plan.FACTS["min_spark_price"](turn) is None
    assert slot_plan.FACTS["spark_bank"](turn) == 3


def test_the_round_check_runs_over_a_directory_and_refuses_it():
    """A round is a DIRECTORY: checking one board would give a ceiling of one."""
    report, bad = slot_plan.check_round(_sparks_turns())
    assert [r["slot"] for r in report] == ["P1"]
    assert len(bad) == 1


def test_a_round_with_no_slot_file_is_legal():
    """Absent is legal: every round committed before EB-202 carries none."""
    other = REPO / "understudy" / "turns" / "kokomi-slice-2"
    assert slot_plan.load_slots(other) == []


def test_a_reachable_threshold_passes():
    """Lower the threshold to what the set can produce and it stops refusing."""
    turns = _sparks_turns()
    slot = slot_plan.load_slots(SPARKS)[0]
    slot.threshold = 3
    row = slot_plan.ceiling(slot, turns)
    assert row["reachable"] and not slot_plan.refusals([row])


@pytest.mark.parametrize("blob,fragment", [
    ({"slots": [{"id": "P", "predicate": [{"left": 1, "op": "<",
                                           "right": 2}]}]}, "threshold"),
    ({"slots": [{"id": "P", "threshold": 1}]}, "predicate"),
    ({"slots": [{"id": "P", "threshold": 1,
                 "predicate": [{"left": "spark_bank", "op": "~",
                                "right": 1}]}]}, "not a comparison"),
    ({"slots": [{"id": "P", "threshold": 1,
                 "predicate": [{"left": "vibes", "op": "<",
                                "right": 1}]}]}, "neither an integer"),
])
def test_the_schema_refuses_rather_than_coerces(blob, fragment):
    """A slot nobody can read is worse than no slot file: prose is what let a
    threshold of four ride on a ceiling of three."""
    with pytest.raises(slot_plan.SlotError) as exc:
        slot_plan.parse_slots(blob)
    assert fragment in str(exc.value)


def test_the_slot_file_is_not_read_as_a_turn():
    """`check` would call `slots.yaml` a BAD turn; `all_turns` skips it."""
    assert staged_turn.SLOT_FILE_NAME == slot_plan.SLOT_FILE
    assert not [p for p in staged_turn.all_turns()
                if p.name == slot_plan.SLOT_FILE]


def test_check_returns_nonzero_on_an_unreachable_slot(capsys):
    """`staged_turn check` is where a plan is validated, so it must refuse."""
    assert staged_turn.slot_report(_sparks_turns()) == 1
    out = capsys.readouterr()
    assert "ceiling 3 of 8" in out.out
    assert "EB-202" in out.err


# ================================================== the battery's shape ====

def test_the_battery_covers_every_category_to_its_floor():
    items = qualify.load_battery()
    assert set(qualify.CATEGORIES) == {"targets", "costs", "intent"}
    for cat, n in qualify.coverage(items).items():
        assert n >= qualify.MIN_ITEMS_PER_CATEGORY, cat
    assert qualify.thin_categories(items) == []


def test_every_battery_packet_is_a_sealed_one_already_on_disk():
    """No new board: every item names a packet a closed round already wrote."""
    for item in qualify.load_battery():
        assert (QA / item.turn_id / "packet.md").is_file(), item.turn_id


def test_the_battery_draws_on_three_rounds():
    """A seat tuned on one character's vocabulary may not qualify on it."""
    rounds = {local_tester.round_slug([i.turn_id])
              for i in qualify.load_battery()}
    assert rounds == {"kokomi-slice2", "klee-slice1-r3", "klee-sparks-r1"}


# ============================================ R223: the pass mark applied ====
#
# [USER], 2026-08-29, answering the pick list: "targets 6/6, others >= 4/6
# works for me". Per category, all three holding, no total to trade against.

def _graded(passes: dict, monkeypatch, threshold=None):
    """A scorecard in which each category passes exactly `passes[cat]` items.

    The scorers themselves are locked above, board by board, on the sealed
    record; what is under test HERE is the pass mark applied to the counts, so
    the counts are the fixture and the boards are not re-read.
    """
    budget = dict(passes)

    def scorer(form, _turn_dir):
        cat = form["category"]
        if budget[cat] > 0:
            budget[cat] -= 1
            return True, "fixture pass"
        return False, "fixture fail"

    monkeypatch.setattr(qualify, "SCORERS",
                        {c: scorer for c in qualify.CATEGORIES})
    return qualify.run_battery(qualify.load_battery(),
                               reader=lambda i: {"category": i.category},
                               threshold=threshold)


def test_the_pass_mark_is_r223s_and_is_read_from_the_battery_file():
    """The mark lives beside the boards it grades, and the tool only applies it."""
    mark = qualify.load_threshold()
    assert mark.per_category == {"targets": 6, "costs": 4, "intent": 4}
    assert mark.owner == "R223"
    assert qualify.unreachable_marks(qualify.load_battery(), mark) == []


_NO_BLOCK = ""
_MISSING_CATEGORY = """threshold:
  owner: R223
  targets: 6
  costs: 4
"""
_A_RATE_NOT_A_COUNT = """threshold:
  owner: R223
  targets: 1.0
  costs: 4
  intent: 4
"""
_A_FOURTH_AXIS = """threshold:
  owner: R223
  targets: 6
  costs: 4
  intent: 4
  vibes: 3
"""


@pytest.mark.parametrize("block, why", [
    (_NO_BLOCK, "a battery with no threshold block grades nothing"),
    (_MISSING_CATEGORY,
     "R223 is per category, so a missing category is not a pass"),
    (_A_RATE_NOT_A_COUNT, "a mark is a count of items, not a rate"),
    (_A_FOURTH_AXIS, "an unknown category is a typo, not a fourth axis"),
])
def test_a_threshold_the_tool_cannot_apply_is_refused(tmp_path, block, why):
    body = (REPO / "understudy" / "battery" / "battery.yaml").read_text(
        encoding="utf-8").split("threshold:")[0]
    path = tmp_path / "battery.yaml"
    path.write_text(body + block, encoding="utf-8")
    with pytest.raises(qualify.BatteryError):
        qualify.load_threshold(path)
    assert why


def test_a_mark_the_battery_cannot_reach_is_refused_before_the_seat_runs():
    """R222 A's lesson: an unreachable threshold is an instrument, not a MISS."""
    items = qualify.load_battery()
    tall = qualify.Threshold({"targets": 7, "costs": 4, "intent": 4}, "test")
    assert qualify.unreachable_marks(items, tall) == ["targets asks 7 of 6 item(s)"]


def test_a_seat_that_meets_every_category_passes(monkeypatch):
    card = _graded({"targets": 6, "costs": 6, "intent": 6}, monkeypatch)
    assert card["pass"] is True
    assert card["total"] == {"items": 18, "passed": 18, "pass": True}
    assert all(v["pass"] for v in card["per_category"].values())
    assert card["threshold"] == {"targets": 6, "costs": 4, "intent": 4}
    assert card["threshold_owner"] == "R223"
    assert "PASS" in qualify.one_line(card)


def test_one_short_on_targets_fails_and_the_other_two_cannot_buy_it_back(
        monkeypatch):
    """17 of 18, and it still FAILS: targets is scored at par (EB-203)."""
    card = _graded({"targets": 5, "costs": 6, "intent": 6}, monkeypatch)
    assert card["total"]["passed"] == 17
    assert card["pass"] is False
    assert card["per_category"]["targets"] == {"items": 6, "passed": 5,
                                               "required": 6, "pass": False}
    assert card["per_category"]["costs"]["pass"] is True
    assert card["per_category"]["intent"]["pass"] is True
    assert "FAIL" in qualify.one_line(card)


def test_three_of_six_on_intent_fails_even_with_both_other_categories_full(
        monkeypatch):
    card = _graded({"targets": 6, "costs": 6, "intent": 3}, monkeypatch)
    assert card["pass"] is False
    assert card["per_category"]["intent"]["pass"] is False
    assert card["per_category"]["targets"]["pass"] is True


def test_the_seats_first_live_scorecard_reads_FAIL_under_R223(monkeypatch):
    """The requalification run of 2026-08-29: 10/18, targets 2, costs 5, intent 3.

    Costs alone clears its mark. Under a total of 15/18 this would have been a
    FAIL too, but under R223 it fails on the two categories that matter most:
    the blind spot that returned the seat, and the falsifier that caught it.
    """
    card = _graded({"targets": 2, "costs": 5, "intent": 3}, monkeypatch)
    assert card["total"]["passed"] == 10
    assert card["pass"] is False
    assert card["per_category"]["targets"]["pass"] is False
    assert card["per_category"]["costs"]["pass"] is True
    assert card["per_category"]["intent"]["pass"] is False


@pytest.mark.parametrize("passes, rc", [
    ({"targets": 6, "costs": 4, "intent": 4}, 0),
    ({"targets": 5, "costs": 6, "intent": 6}, 1),
    ({"targets": 2, "costs": 5, "intent": 3}, 1),
])
def test_the_verdict_is_the_exit_code(tmp_path, monkeypatch, passes, rc):
    """PASS exits 0 and FAIL exits 1; only an unrunnable battery exits 2."""
    budget = dict(passes)

    def scorer(form, _turn_dir):
        cat = form["category"]
        if budget[cat] > 0:
            budget[cat] -= 1
            return True, "fixture pass"
        return False, "fixture fail"

    monkeypatch.setattr(qualify, "SCORERS",
                        {c: scorer for c in qualify.CATEGORIES})
    monkeypatch.setattr(local_tester, "_client", lambda _a: object())

    def fake_read(turn_id, **kw):
        form = Path(kw["land_dir"]) / "form.json"
        form.write_text(json.dumps({"category": _CATEGORY_OF[turn_id]}),
                        encoding="utf-8")
        return {"form": str(form)}

    monkeypatch.setattr(local_tester, "read_turn", fake_read)
    land = tmp_path / "land"
    assert local_tester.main(["qualify", "--land-dir", str(land),
                              "--out", str(tmp_path / "card.json")]) == rc
    card = json.loads((tmp_path / "card.json").read_text(encoding="utf-8"))
    assert card["pass"] is (rc == 0)
    # R101b: the sealed directories are untouched; the reads land where told.
    assert land.is_dir()


_CATEGORY_OF = {i.turn_id: i.category for i in qualify.load_battery()}


def test_a_refusal_is_a_failed_item_and_never_a_skipped_one():
    card = qualify.run_battery(qualify.load_battery()[:1],
                               reader=lambda _i: None)
    assert card["items"][0]["passed"] is False
    assert "filed no form" in card["items"][0]["why"]


def test_each_category_scores_the_failure_it_was_written_for():
    """One fake seat per category, answering wrongly, then rightly."""
    items = {i.category: i for i in qualify.load_battery()}

    bad_targets = {"chosen_line": _sealed_line("klee-sparks-r1-t07")}
    ok, _ = qualify.score_targets(bad_targets, QA / "klee-sparks-r1-t07")
    assert not ok
    good = [dict(p, target="Sludge Spinner") if p["card"] != "Duck and Cover"
            else p for p in bad_targets["chosen_line"]]
    ok, _ = qualify.score_targets({"chosen_line": good},
                                  QA / "klee-sparks-r1-t07")
    assert ok

    turn = items["costs"].turn_id
    ok, why = qualify.score_costs(
        {"q1_what_did_you_play": "Duck and Cover is free so I played it"},
        QA / turn)
    assert not ok or "Duck and Cover" not in why  # only fires where priced
    ok, _ = qualify.score_costs({"q1_what_did_you_play": "I blocked"},
                                QA / turn)
    assert ok

    ok, _ = qualify.score_intent({"q4_different_intent": "no"}, QA / turn)
    assert not ok
    ok, _ = qualify.score_intent({"q4_different_intent": "yes, a block "
                                                        "intent flips it"},
                                 QA / turn)
    assert ok


def test_an_aimed_card_named_at_nobody_and_a_targetless_one_named_at_someone():
    """Both directions of the targets category, which is the whole item.

    `t03`'s own sealed form names an enemy on Bang Bang!, which hits at
    random -- the second direction, found in the record rather than invented.
    """
    ok, why = qualify.score_targets(
        {"chosen_line": _sealed_line("klee-sparks-r1-t03")},
        QA / "klee-sparks-r1-t03")
    assert not ok
    assert "aims at nobody" in why
