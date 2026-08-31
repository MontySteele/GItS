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

from understudy import (local_seat, local_tester, qa_packet, qualify,
                        resource_order, seat, slot_plan, staged_turn,
                        targeting)

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
    """No new board: every item names a packet a closed round already wrote.

    The regression set is held to the same rule — it is unscored, not
    unpinned, and a rotted turn_id in it is still a rotted turn_id.
    """
    for item in qualify.load_battery() + qualify.load_regression():
        assert (QA / item.turn_id / "packet.md").is_file(), item.turn_id


def test_the_battery_draws_on_four_rounds_and_both_characters():
    """A seat tuned on one character's vocabulary may not qualify on it.

    Three rounds until R232 (2026-08-30), four after it: the `costs` re-pick
    reached into `kokomi-slice1` because `klee-slice1-r3` prints no non-zero
    cost but 1 and so asks the ledger nothing.
    """
    items = qualify.load_battery()
    rounds = {local_tester.round_slug([i.turn_id]) for i in items}
    assert rounds == {"kokomi-slice1", "kokomi-slice2",
                      "klee-slice1-r3", "klee-sparks-r1"}
    by_character = {"kokomi": 0, "klee": 0}
    for item in items:
        by_character[item.turn_id.split("-")[0]] += 1
    assert min(by_character.values()) >= 6, by_character


# ------------------------------- R232: the free-claim regression set, kept --
#
# R232 (2026-08-30): "Preserve the old six as a labeled 'free-claim
# regression' set if useful, but remove them from R223 qualification scoring."
# Kept and removed are two claims, so they are two locks.

def test_the_regression_set_is_the_old_six_and_is_still_there():
    """KEPT. The pre-re-pick `costs` selection, whole, by turn_id."""
    kept = {i.turn_id for i in qualify.load_regression()}
    assert kept == {"kokomi-slice2-t02", "kokomi-slice2-t06",
                    "klee-slice1-r3-t03", "klee-slice1-r3-t04",
                    "klee-sparks-r1-t04", "klee-sparks-r1-t05"}


def test_the_regression_set_is_not_scored(monkeypatch):
    """REMOVED FROM SCORING, and pinned on the ids rather than the boards.

    Two of the old six were re-picked into the battery on the new rule, so
    the turn_ids overlap on purpose and only the ITEM ids can carry the
    separation. A run scores the `items:` list and nothing else.
    """
    scored = qualify.load_battery()
    regression = qualify.load_regression()
    assert regression, "the set is supposed to be kept, not emptied"
    assert not ({i.id for i in scored} & {i.id for i in regression})

    monkeypatch.setattr(qualify, "SCORERS",
                        {c: lambda _f, _d: (True, "fixture")
                         for c in qualify.CATEGORIES})
    card = qualify.run_battery(
        scored, reader=lambda i: {"category": i.category},
        threshold=qualify.load_threshold())
    graded = {r["item"] for r in card["items"]}
    assert graded == {i.id for i in scored}
    assert not (graded & {i.id for i in regression})


def test_a_battery_file_with_no_regression_set_still_loads(tmp_path):
    """The key is OPTIONAL: a custom `--battery` file is not obliged to carry
    R232's history, and a missing set is an empty one, never an error."""
    path = tmp_path / "battery.yaml"
    path.write_text("items:\n  - {id: C1, category: costs, "
                    "turn_id: kokomi-slice1-t03, why: x}\n", encoding="utf-8")
    assert qualify.load_regression(path) == []
    assert [i.id for i in qualify.load_battery(path)] == ["C1"]


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
    # EB-211: the RIGHT answer is no longer "said nothing about a price".
    # `{"q1_what_did_you_play": "I blocked"}` PASSED this category until
    # 2026-08-30, which is the whole reason the ledger exists; a pass now
    # costs a ledger the printed costs and the printed bank agree with.
    silent = {"chosen_line": [{"card": "Kaboom!"}, {"card": "Duck and Cover"}],
              "q1_what_did_you_play": "I blocked"}
    ok, why = qualify.score_costs(silent, QA / turn)
    assert not ok and "silent on every price" in why
    priced = dict(silent, price_ledger=[
        {"card": "Kaboom!", "energy_before": 3, "energy_price": 1,
         "energy_after": 2, "spark_before": 1, "spark_price": 0,
         "spark_after": 1},
        {"card": "Duck and Cover", "energy_before": 2, "energy_price": 1,
         "energy_after": 1, "spark_before": 1, "spark_price": 0,
         "spark_after": 1}])
    ok, why = qualify.score_costs(priced, QA / turn)
    assert ok, why

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


# =========================================================== KLEESPARK-R2 ==

R2 = REPO / "understudy" / "turns" / "klee-sparks-r2"


def _r2_turns() -> list:
    return [staged_turn.load(p) for p in sorted(R2.glob("t*.yaml"))]


def test_kleespark_r2s_four_slots_are_all_reachable_on_its_own_boards():
    """THE LOCK on the repaired round, and it is the opposite of `P1`'s.

    `KLEESPARK-R1`'s slot could not be reached by the boards it was registered
    against, and nobody could see it until the pair read. `KLEESPARK-R2` was
    planned the other way round -- the ceilings were computed before the plan
    was accepted -- and this pins the four numbers so an edit to a board
    cannot quietly move one. Every qualifying set is named, because a ceiling
    that stays at 2 while the boards under it change is not the same
    instrument.
    """
    turns = _r2_turns()
    assert len(turns) == 6
    slots = slot_plan.load_slots(R2)
    assert [s.id for s in slots] == ["S1", "S2", "S3", "S4"]
    rows = {r["slot"]: r for r in slot_plan.reachability(slots, turns)}
    expected = {
        "S1": (2, ["klee-sparks-r2-t01", "klee-sparks-r2-t04",
                   "klee-sparks-r2-t06"]),
        "S2": (2, ["klee-sparks-r2-t02", "klee-sparks-r2-t05"]),
        "S3": (2, ["klee-sparks-r2-t04", "klee-sparks-r2-t06"]),
        "S4": (2, ["klee-sparks-r2-t03", "klee-sparks-r2-t06"]),
    }
    for slot_id, (threshold, qualifying) in expected.items():
        row = rows[slot_id]
        assert row["threshold"] == threshold, slot_id
        assert row["qualifying"] == qualifying, slot_id
        assert row["ceiling"] == len(qualifying), slot_id
        assert row["reachable"], slot_id
    assert slot_plan.refusals(rows.values()) == []


def test_the_two_dry_sink_boards_carry_no_spark_generator_in_hand():
    """§11.7 item 2's whole point: round 1's empty banks held Powder Pop.

    A generator in the hand answers the dry-sink question before it is asked,
    so `S2`'s two boards are checked against the SHEETS rather than against
    the manifest's prose -- the same failure mode `EB-202` was about.
    """
    rows = slot_plan.sheet_rows_by_id()
    for turn in _r2_turns():
        if turn.id not in ("klee-sparks-r2-t02", "klee-sparks-r2-t05"):
            continue
        for card_id in turn.board.hand:
            effects = (rows.get(str(card_id)) or {}).get("effects") or []
            ops = [str(e.get("op")) for e in effects if isinstance(e, dict)]
            assert "gain_spark" not in ops, f"{turn.id}: {card_id} gains Sparks"
        assert turn.board.resources.get("sparks") == 0, turn.id


def test_the_bang_bang_board_puts_no_bomb_maker_in_the_hand():
    """`t03` settles §12.8 item 1, and only if nothing can detonate.

    The whole-fight run could not tell "Bang Bang! charged 1" from "Bang Bang!
    charged 2 and a detonation refunded 1", because a Bomb was on the field.
    A board that answers it has no card in hand that places one.
    """
    rows = slot_plan.sheet_rows_by_id()
    turn = next(t for t in _r2_turns() if t.id == "klee-sparks-r2-t03")
    for card_id in turn.board.hand:
        effects = (rows.get(str(card_id)) or {}).get("effects") or []
        ops = [str(e.get("op")) for e in effects if isinstance(e, dict)]
        assert "place_bomb" not in ops, f"{card_id} places a Bomb"


def test_the_preregistered_order_covers_every_r2_slot_twice():
    """R221 B's order, pinned: five boards in the first set, `t01` the rest.

    The cover is what raises `--first` from 4 to 5, and a board set whose
    cover changed would change which boards can be recorded UNRUN.
    """
    index = {t.id: t for t in _r2_turns()}
    order = local_tester.preregistered_order(sorted(index), turns=index)
    first, rest = local_tester.split_first(order, 4)
    assert [r["turn_id"] for r in first] == [
        "klee-sparks-r2-t06", "klee-sparks-r2-t04", "klee-sparks-r2-t02",
        "klee-sparks-r2-t03", "klee-sparks-r2-t05"]
    assert [r["turn_id"] for r in rest] == ["klee-sparks-r2-t01"]


# ============================================================== EB-237 =====
#
# THE LOCK IS WRITTEN ON `KLEESPARK-BT1`'s OWN COMMITTED BOARD, not on a
# fixture: the defect was invisible to every check the round ran, and a lock
# on a board I invented would be a lock on the sentence I wrote. The boards
# and `slots.yaml` of that closed round are read-only inputs here (R101b);
# nothing in this file writes into them.

BT1 = REPO / "understudy" / "turns" / "klee-sparks-bt1"


def _bt1(turn_id: str):
    return staged_turn.load(BT1 / f"{turn_id}.yaml")


def test_the_mode_head_price_is_in_t01s_plan():
    """THE LOCK. *Bag of Tricks* prices 3 at a mode head, and the plan says so.

    Before `EB-237` `_spark_prices` read a top-level `spend_spark` and
    nothing else, so the row the whole round was about priced nothing as far
    as every fact below could see: `affordable_spark_uses` read 0 on a board
    holding a priced mode the bank could pay exactly.
    """
    turn = _bt1("t01")
    assert slot_plan._spark_prices(turn) == [3]
    assert slot_plan.FACTS["spark_use_count"](turn) == 1
    assert slot_plan.FACTS["affordable_spark_uses"](turn) == 1
    assert slot_plan.FACTS["min_spark_price"](turn) == 3
    assert slot_plan.FACTS["affordable_spark_price_sum"](turn) == 3


def test_t02s_two_sinks_are_both_counted():
    """`t02` swaps in Firework Finale: two priced uses, both at 3."""
    turn = _bt1("t02")
    assert slot_plan._spark_prices(turn) == [3, 3]
    assert slot_plan.FACTS["affordable_spark_uses"](turn) == 2
    assert slot_plan.FACTS["affordable_spark_price_sum"](turn) == 6


def test_a_bank_below_the_mode_price_affords_nothing():
    """`t03`'s bank of 2 reaches neither the mode nor anything else."""
    turn = _bt1("t03")
    assert slot_plan._spark_prices(turn) == [3]
    assert slot_plan.FACTS["affordable_spark_uses"](turn) == 0


def test_only_a_mode_head_counts_and_nothing_nested():
    """R225's clause is the whole rule: the HEAD of a mode, and no deeper.

    A `spend_spark` sitting second in a mode's effect list is nested by
    construction, and admitting it would turn this into a search for any
    spend anywhere in a row.
    """
    head = {"effects": [{"op": "choose_one", "modes": [
        {"effects": [{"op": "spend_spark", "amount": 2},
                     {"op": "damage", "amount": 9}]}]}]}
    nested = {"effects": [{"op": "choose_one", "modes": [
        {"effects": [{"op": "damage", "amount": 9},
                     {"op": "spend_spark", "amount": 2}]}]}]}
    assert slot_plan.card_spark_prices(head) == [2]
    assert slot_plan.card_spark_prices(nested) == []


# ============================================================== EB-236 =====
#
# THE LOCK IS ON `KLEESPARK-BT1`'s `t02`, UNEDITED. That board's header
# declares, in prose, that "the bank of 3 now buys EXACTLY ONE of two things
# -- the card's priced mode, or the whole of another card", and the shipped
# world buys both three plays later because Klee's starter relic refunds one
# Spark per detonated Bomb. The board file is the committed record of a run
# and graded round and stays exactly as registered (R101b), so the CLAIM it
# made in prose is supplied here, in the machine-readable shape a board
# writes it in today, and the check is run against the board as it stands.

# `t02`'s header sentence, as a `resource_round:` block would say it.
BT1_T02_CLAIM = slot_plan.ResourceRound(
    claim="the bank of 3 buys EXACTLY ONE of two things",
    exclusive=[slot_plan.Use("proto_spark_mode_bombs", 2),
               slot_plan.Use("proto_spark_finisher")])


def test_bt1s_declined_half_is_bought_by_a_sequence_it_never_registered():
    """THE LOCK. The both-buyable order is found, and it is THE order.

    Priced mode (bank 3 -> 0, three Bombs), a detonator (the relic pays one
    Spark per Bomb, bank 0 -> 3), the rival sink (bank 3 -> 0). 15 + 18.
    """
    orders = slot_plan.buying_orders(_bt1("t02"), BT1_T02_CLAIM)
    assert orders, "the exclusive pair is bought by no order at all"
    assert ["proto_spark_mode_bombs (mode 2)", "quick_fuse",
            "proto_spark_finisher"] in orders


def test_the_refund_is_what_buys_the_second_half():
    """Take the relic away and the same board's claim holds.

    Not a board this repo has -- a control, so the finding is attributed to
    the relic and not to the arithmetic being wrong somewhere else.
    """
    without = slot_plan.ResourceRound(
        claim=BT1_T02_CLAIM.claim, exclusive=list(BT1_T02_CLAIM.exclusive),
        relic_hooks=[])
    assert slot_plan.buying_orders(_bt1("t02"), without) == []


@pytest.mark.parametrize("turn_id", ["t01", "t02", "t03", "t04"])
def test_every_bt1_board_lets_the_energy_pay_for_the_whole_hand(turn_id):
    """The weaker half, and it is the round's RETURN.

    One enemy, a fixed telegraph, three Energy and at most two Energy-costed
    cards: the whole hand is always playable, so the telegraph forces no
    trade and question four is honestly answered "no".
    `intent_insensitive` refused SEVEN OF EIGHT forms on this construction.
    """
    turn = _bt1(turn_id)
    assert slot_plan.hand_is_wholly_playable(turn)
    assert any("no_forced_trade" in f
               for f in slot_plan.board_design_findings(turn))


def test_an_exclusive_pair_of_one_is_refused_rather_than_read():
    """One use is not a claim about anything."""
    with pytest.raises(slot_plan.BoardDesignError) as exc:
        slot_plan.parse_resource_round({"exclusive": [{"card": "kaboom"}]})
    assert "TWO OR MORE" in str(exc.value)


def test_a_pair_naming_a_card_that_is_not_in_hand_is_refused():
    """A claim about a card the board does not hold is not a claim."""
    spec = slot_plan.ResourceRound(
        exclusive=[slot_plan.Use("proto_spark_finisher"),
                   slot_plan.Use("proto_spark_blast")])
    with pytest.raises(slot_plan.BoardDesignError):
        slot_plan.buying_orders(_bt1("t02"), spec)


# ------------------------------ EB-236, on the REPAIRED round -------------

BT2 = REPO / "understudy" / "turns" / "klee-sparks-bt2"


def _bt2_turns() -> list:
    return [staged_turn.load(p) for p in sorted(BT2.glob("t*.yaml"))]


def test_the_repaired_boards_pass_the_check():
    """THE OTHER HALF OF THE LOCK: `KLEESPARK-BT2` is clean.

    Its `t02` claims the same exclusivity `KLEESPARK-BT1`'s `t02` did and
    HOLDS it, because the only Attack in that hand is the rival sink itself
    and it has to be paid for before it can pop anything.
    """
    turns = _bt2_turns()
    assert [t.id for t in turns] == ["klee-sparks-bt2-t01",
                                     "klee-sparks-bt2-t02",
                                     "klee-sparks-bt2-t03"]
    assert slot_plan.check_board_design(turns) == []


def test_the_repaired_exclusive_board_declares_its_claim_in_the_file():
    """A claim that lives only in a header comment is what BT1 shipped."""
    turn = next(t for t in _bt2_turns() if t.id == "klee-sparks-bt2-t02")
    spec = turn.resource_round
    assert spec.exclusive == [slot_plan.Use("proto_spark_mode_bombs", 2),
                              slot_plan.Use("proto_spark_finisher")]
    assert slot_plan.buying_orders(turn, spec) == []


def test_the_repaired_rounds_ceilings_read_the_mode_price():
    """`EB-237` is what lets these predicates say what they mean."""
    turns = _bt2_turns()
    rows = {r["slot"]: r for r in
            slot_plan.reachability(slot_plan.load_slots(BT2), turns)}
    assert rows["C1"]["threshold"] == 2
    assert rows["C1"]["qualifying"] == ["klee-sparks-bt2-t01",
                                        "klee-sparks-bt2-t02"]
    assert rows["C2"]["threshold"] == 1
    assert rows["C2"]["qualifying"] == ["klee-sparks-bt2-t03"]
    assert slot_plan.refusals(rows.values()) == []


# ------------------------------------------- EB-236 (d): the forecast ------

def test_the_forecast_is_asked_at_the_top_of_the_page_and_counted():
    """`EB-229`'s staged twin: a field to count, asked BEFORE the line.

    The schema carried nothing of the sort -- a form is four PAST-TENSE
    questions -- so a registration that wanted a prediction had nowhere to
    put it, and `KURAGEMEM002` graded three slots UNREACHED for exactly that
    reason: not because the display failed but because the question was
    never asked.
    """
    turn = next(t for t in _bt2_turns() if t.id == "klee-sparks-bt2-t01")
    assert len(turn.forecast) == 3
    packet = qa_packet.build(
        {"state_type": "battle",
         "player": {"hp": 42, "max_hp": 62, "block": 0, "energy": 3,
                    "hand": [], "status": [], "relics": []},
         "battle": {"round": 4, "enemies": []}},
        turn.id, forecast=list(turn.forecast))
    page = qa_packet.render(packet)
    assert "## Before you decide" in page
    assert page.index("## Before you decide") < page.index("## Your hand")
    # A form that skips it is answering a different board.
    base = {"grader": {"id": "x"}, "chosen_line": [{"card": "Kaboom!"}],
            "q1_what_did_you_play": "a", "q2_other_line_considered": "b",
            "q3_what_it_gave_up": "c", "q4_different_intent": "yes"}
    assert "forecast_missing" in staged_turn.apply_falsifiers(
        turn.id, base, packet_sha=None, closeness=None, forecast_asks=3)
    answered = dict(base, forecast=["0", "3", "0"])
    assert "forecast_missing" not in staged_turn.apply_falsifiers(
        turn.id, answered, packet_sha=None, closeness=None, forecast_asks=3)
    # And a board that asks nothing is graded exactly as it was before.
    assert staged_turn.apply_falsifiers(
        turn.id, base, packet_sha=None, closeness=None) == []


def test_the_next_turn_reading_is_opt_in_and_ends_the_turn():
    """`EB-236` item (e). A delayed refund needs one more reading."""
    sit = next(t for t in _bt2_turns() if t.id == "klee-sparks-bt2-t03")
    now = next(t for t in _bt2_turns() if t.id == "klee-sparks-bt2-t01")
    form = {"chosen_line": [{"card": "Bag of Tricks"}]}
    assert sit.replay_next_turn and not now.replay_next_turn
    verbs = [v for v, _ in staged_turn.execute_steps(sit, form)]
    assert verbs[-2:] == ["end_turn", "read"]
    assert "end_turn" not in [v for v, _ in staged_turn.execute_steps(now, form)]


# --------------------- EB-239: the forecast's FORM half, and its lock ------

def _strict_schema_refusals(schema: dict, blob: dict) -> list[str]:
    """A minimal reader of the ONE schema rule this lock is about.

    `form_schema()` is handed to codex as `--output-schema` and printed into
    the local tester's prompt, and both enforce it strictly: a key that is
    not a declared property may not appear, and every `required` key must.
    There is no `jsonschema` in this environment, so the rule is read here
    rather than imported -- and it is read the way the two seats read it,
    which is all this lock needs to say.
    """
    bad = []
    if schema.get("additionalProperties") is False:
        bad += [f"undeclared:{k}" for k in blob
                if k not in schema["properties"]]
    bad += [f"missing:{k}" for k in schema.get("required", [])
            if k not in blob]
    return sorted(bad)


def _bt2_answered_form() -> dict:
    """`KLEESPARK-BT2`'s own `t01` reply, as it would have had to be written
    to answer the three questions the page printed."""
    return {
        "turn_id": "klee-sparks-bt2-t01",
        "packet_sha256": "0" * 64,
        "grader": {"id": "x", "kind": "llm", "model": "m",
                   "designed_these_cards": False},
        "chosen_line": [{"card": "Bag of Tricks", "target": "Seapunk",
                         "exhaust": None,
                         "choose": "Spend 3 Sparks: place 3 Bombs dealing 5."}],
        "q1_what_did_you_play": "a", "q2_other_line_considered": "b",
        "q3_what_it_gave_up": "c", "q4_different_intent": "yes",
        "q4_changed": True,
        "forecast": ["0", "3", "0"],
        # EB-211, and it rides the same rule as `forecast`: declared on the
        # strict schema, so a reply that carries it is not refused
        # `undeclared:` and one that omits it is refused `missing:`.
        "price_ledger": [{"card": "Bag of Tricks", "energy_before": 3,
                          "energy_price": 1, "energy_after": 2,
                          "spark_before": 3, "spark_price": 3,
                          "spark_after": 0}],
    }


def test_the_reply_schema_can_carry_a_forecast():
    """`EB-239`. `KLEESPARK-BT2` refused all six of its forms
    `forecast_missing` (§24.4) because the packet asked a question the REPLY
    had no field to answer into: `form_schema()` was strict, nine named
    properties, and `forecast` was not one of them. Declared, not loosened --
    `additionalProperties` stays `False` and the field joins `target` on the
    nullable-and-required rule.

    Seen to FAIL before the fix: the answered form below was refused
    `undeclared:forecast` by the seat's own schema, which is exactly the
    reply codex was not allowed to emit.
    """
    schema = seat.form_schema()
    assert schema["additionalProperties"] is False
    assert schema["properties"]["forecast"]["type"] == ["array", "null"]
    assert "forecast" in schema["required"]
    assert _strict_schema_refusals(schema, _bt2_answered_form()) == []
    # A board that asks nothing still has somewhere to say so.
    assert _strict_schema_refusals(
        schema, dict(_bt2_answered_form(), forecast=None)) == []


def test_a_form_that_omits_the_forecast_is_still_refused_on_an_asking_board():
    """The other half of the same lock: declaring the field must not make
    the falsifier stop biting. `EB-236` item (d)'s refusal is what makes the
    forecast a PRE-commitment rather than a courtesy."""
    form = dict(_bt2_answered_form())
    form.pop("forecast")
    assert _strict_schema_refusals(seat.form_schema(), form) == [
        "missing:forecast"]
    assert "forecast_missing" in staged_turn.apply_falsifiers(
        "klee-sparks-bt2-t01", form, packet_sha=None, closeness=None,
        forecast_asks=3)
    # And short counts, not just absent ones.
    short = dict(_bt2_answered_form(), forecast=["0", ""])
    assert "forecast_missing" in staged_turn.apply_falsifiers(
        "klee-sparks-bt2-t01", short, packet_sha=None, closeness=None,
        forecast_asks=3)
    assert "forecast_missing" not in staged_turn.apply_falsifiers(
        "klee-sparks-bt2-t01", _bt2_answered_form(), packet_sha=None,
        closeness=None, forecast_asks=3)


def test_the_local_tester_reads_the_same_schema_as_the_codex_seat():
    """One schema, two seats: `local_seat` prints `seat.form_schema()` into
    its prompt verbatim, which is why `KLEESPARK-BT2`'s shadow chair was
    refused for the same structural reason as the deciding one -- and why
    one fix repairs both."""
    prompt = local_seat.build_grade_prompt("PACKET", "0" * 64)
    assert '"forecast"' in prompt
    assert json.dumps(seat.form_schema(), indent=1) in prompt
