"""Pins for the P1.5 plumbing that a mutation round (track K, 2026-08-05)
found unprotected.

`test_understudy_p15` pins the three new surfaces at the shapes P1.5's spec
names. This file sits underneath it and pins the parts that are only visible
when something goes WRONG: the refusals, the sentinels, the stop conditions
and the teardown order. Each behaviour below is stated in the module it lives
in -- a docstring, a comment, or the `--max-fights` / `--seed` help text --
and each survived the whole suite when it was reversed.

Same fence as the file above it: none of this is evidence about the game. It
is evidence about whether the recorder records what it says it records.
"""

from __future__ import annotations

import json

import pytest

from understudy import report
from understudy import soak
from understudy import trace_replay as replay

from . import test_understudy_soak as ts


# ======================================================= trace_replay ======

SEED_A = {"record": "seed_read_back", "seed": "ABC", "chosen": "ABC",
          "honoured": True}


def _fight(**over):
    f = soak.FightTelemetry(act=1, floor=2, kind="monster")
    f.cards_played = [[1, "Stage Presence"]]
    f.selectors = [[1, "choose", 0, "Center Stage",
                    ["Center Stage", "Guest Cast"]]]
    f.meters_by_turn = [[1, 4, 1, 3, 6]]
    rec = f.as_record()
    rec.update(over)
    return rec


def _logs(monkeypatch, mapping):
    monkeypatch.setattr(replay, "read_run_log",
                        lambda stamp, i: mapping[stamp])


def test_a_fight_that_changed_kind_is_a_divergence(monkeypatch):
    """`FIGHT_KEYS` is documented as "fields that IDENTIFY a fight within a
    run, as opposed to describing it", and `kind` is one of the three. Two
    recordings of one seed that put a monster and an elite on the same act and
    floor are two different runs of that floor -- the exact thing a
    build-vs-build comparison exists to catch -- and act/floor alone cannot
    see it, because the floor is the same floor.
    """
    _logs(monkeypatch, {"a": [SEED_A, _fight()],
                        "b": [SEED_A, _fight(kind="elite")]})
    findings = replay.compare_runs(("a", 1), ("b", 1))
    assert len(findings) == 1
    assert "kind" in findings[0] and "'monster'" in findings[0]


def test_a_seed_mismatch_reports_the_seed_and_stops_there(monkeypatch):
    """The finding's own text is the contract: "these are two different runs,
    and nothing below is a comparison". So the seed line is the ONLY line --
    a per-field diff printed under it would dress an incomparable pair as a
    measurement, and it would look exactly like a real divergence report.
    """
    other = _fight(kind="elite")
    other["cards_played"] = [[1, "Curtain Call"]]
    _logs(monkeypatch, {
        "a": [{"record": "seed_read_back", "seed": "ABC"}, _fight()],
        "b": [{"record": "seed_read_back", "seed": "XYZ"}, other]})

    findings = replay.compare_runs(("a", 1), ("b", 1))
    assert len(findings) == 1
    assert findings[0].startswith("SEED:")


@pytest.mark.parametrize("longer", ["a", "b"])
def test_a_fight_count_divergence_is_reported_in_either_direction(
        monkeypatch, longer):
    """A comparison of two recordings is symmetric: whichever recording ran
    out first, the fact that they hold different numbers of fights is the
    finding, and the message says `!=` rather than naming a direction. A
    one-sided test would report a build that lost a fight and stay silent
    about a build that gained one.
    """
    short = [SEED_A, _fight()]
    long = [SEED_A, _fight(), _fight(floor=3)]
    _logs(monkeypatch, {"a": long if longer == "a" else short,
                        "b": long if longer == "b" else short})

    findings = replay.compare_runs(("a", 1), ("b", 1))
    assert any(f.startswith("FIGHT COUNT:") for f in findings)


# ------------------------------------- EB-59: acceptance by absence -------
#
# The acceptance condition is an EMPTY FINDING LIST, so every way of getting
# one without comparing anything is a false pass. One test per leg.

def test_two_recordings_that_do_not_exist_are_not_identical(tmp_path,
                                                            monkeypatch):
    """Leg 1 + leg 5. The log dir is gitignored, so a fresh clone's normal
    state is NO LOGS AT ALL -- and the reader that returned `[]` for a missing
    file made that state look exactly like a clean comparison."""
    monkeypatch.setattr(report, "LOG_DIR", tmp_path)
    findings = replay.compare_runs(("nope", 1), ("nope", 2))
    assert len(findings) == 1 and findings[0].startswith("NO RECORDING:")


def test_a_log_with_unparseable_lines_refuses_rather_than_reads_short(
        tmp_path, monkeypatch):
    """Leg 5. A dropped line is a hole in the record. `read_run_log` counts it
    and refuses; the morning report, which must still render, reads the same
    file through `read_run_log_checked` and PRINTS the count instead."""
    monkeypatch.setattr(report, "LOG_DIR", tmp_path)
    (tmp_path / "soak-X-run001.jsonl").write_text(
        json.dumps(SEED_A) + "\n{not json}\n", encoding="utf-8")

    log = report.read_run_log_checked("X", 1)
    assert log.unreadable == 1 and not log.sound and log.records == [SEED_A]
    with pytest.raises(report.UnreadableRunLog):
        report.read_run_log("X", 1)


def test_a_missing_log_raises_where_a_claim_is_being_made(tmp_path,
                                                          monkeypatch):
    monkeypatch.setattr(report, "LOG_DIR", tmp_path)
    assert report.read_run_log_checked("X", 1).missing
    with pytest.raises(report.MissingRunLog):
        report.read_run_log("X", 1)


def test_the_morning_report_says_which_logs_it_could_not_read(tmp_path,
                                                              monkeypatch):
    """The report renders over a damaged night rather than crashing -- but it
    says so above the defects, because the counts below it are then taken over
    what survived and not over the runs the index claims."""
    monkeypatch.setattr(report, "LOG_DIR", tmp_path)
    (tmp_path / "soak-X-index.json").write_text(json.dumps(
        {"stamp": "X", "character": "furina", "policy": "p",
         "requested_runs": 2,
         "runs": [{"run": 1, "seed": "A"}, {"run": 2, "seed": "B"}]}),
        encoding="utf-8")
    (tmp_path / "soak-X-run001.jsonl").write_text(
        json.dumps(SEED_A) + "\n", encoding="utf-8")

    out = report.render("X")
    assert "could not be read whole" in out
    assert "run 2" in out and "no run log at" in out


def test_two_runs_with_no_seed_on_either_side_are_not_compared(monkeypatch):
    """Leg 2. The seed guard was `seed_a != seed_b`, and `None != None` is
    False -- so the one path where the harness does NOT know what it ran was
    the path that skipped the check and compared anyway."""
    _logs(monkeypatch, {"a": [_fight()], "b": [_fight()]})
    findings = replay.compare_runs(("a", 1), ("b", 1))
    assert len(findings) == 1 and findings[0].startswith("SEED:")
    assert "neither run recorded a seed" in findings[0]


def test_two_runs_with_no_fights_are_not_identical(monkeypatch):
    """Leg 3's other half, at the run level: `zip` over two empty lists
    iterates zero times, and zero comparisons is not agreement."""
    _logs(monkeypatch, {"a": [SEED_A], "b": [SEED_A]})
    findings = replay.compare_runs(("a", 1), ("b", 1))
    assert len(findings) == 1 and findings[0].startswith("NO FIGHTS:")


def test_a_recorder_with_no_column_does_not_agree_with_an_empty_one(
        monkeypatch):
    """Leg 3. Two recordings of one seed, one of them written by a build that
    never had the selector column: that is a fact about the two builds, which
    is the entire subject of this comparison."""
    old = _fight()
    del old["selectors"]
    _logs(monkeypatch, {"a": [SEED_A, old],
                        "b": [SEED_A, _fight(selectors=[])]})
    findings = replay.compare_runs(("a", 1), ("b", 1))
    assert len(findings) == 1 and "selectors diverges" in findings[0]
    assert "(not recorded)" in findings[0]


@pytest.mark.parametrize("key,value", [("outcome", "died"), ("turns", 9)])
def test_a_fight_that_ended_differently_is_reported(monkeypatch, key, value):
    """Leg 4. `outcome` and `turns` are still outside the trace IDENTITY --
    they are output, like hp and damage -- but the undeclared version of that
    rule let a won 2-turn fight and a lost 5-turn fight print IDENTICAL.
    Declared and reported: the comparison names the field and lets the reader
    read it."""
    _logs(monkeypatch, {"a": [SEED_A, _fight()],
                        "b": [SEED_A, _fight(**{key: value})]})
    findings = replay.compare_runs(("a", 1), ("b", 1))
    assert len(findings) == 1 and f": {key} " in findings[0]


def test_an_index_with_no_runs_compares_nothing_and_says_so(monkeypatch):
    """Leg 1 at the top of the funnel: the per-run loop runs zero times over
    an empty index, and the verdict line printed a clean bill anyway."""
    monkeypatch.setattr(replay, "load", lambda stamp: {"runs": []})
    out = replay.render_compare("a", "b")
    assert "VERDICT: nothing compared" in out
    assert "identical" not in out


def test_the_verdict_says_identical_only_when_nothing_diverged(monkeypatch):
    """`compare_runs`' docstring makes the empty list the acceptance
    condition, and `render_compare` is where a person reads it. The verdict
    line is the whole output for a clean comparison, so a report that prints
    the wrong one is a report that says the opposite of what it measured.
    """
    monkeypatch.setattr(replay, "load", lambda stamp: {"runs": [{"index": 1}]})

    _logs(monkeypatch, {"a": [SEED_A, _fight()], "b": [SEED_A, _fight()]})
    assert "VERDICT: identical traces" in replay.render_compare("a", "b")

    _logs(monkeypatch, {"a": [SEED_A, _fight()],
                        "b": [SEED_A, _fight(kind="elite")]})
    out = replay.render_compare("a", "b")
    assert "VERDICT: traces diverge" in out
    assert "VERDICT: identical traces" not in out


def test_a_log_with_no_seed_record_reports_a_chosen_seed_of_none(monkeypatch):
    """`seed_of`'s docstring: "`chosen` is None on a read-back run ... and
    `honoured` is None when nothing was chosen -- a run that asked for nothing
    cannot have been refused". None and empty-string are both falsy and both
    print the same, so the difference only surfaces where a reader asks `is
    None` to tell "no seed was chosen" from "a seed was chosen and it was
    blank".
    """
    monkeypatch.setattr(replay, "read_run_log", lambda stamp, i: [_fight()])
    assert replay.seed_of("a", 1) == {"seed": None, "chosen": None,
                                      "honoured": None}


def test_a_truncated_row_from_an_older_log_is_read_not_crashed_on():
    """The reconstruction's stated rule for old logs is that a missing field
    "reads as empty rather than raising: ... the honest report on that is
    'this run recorded no selector answers', not a crash". Rows written by an
    older recorder are the same case as keys written by one, and both readers
    pad rather than index blindly -- `selector_lines` over a short selector
    row, and `describe_run` over a meter row with no Encore column.
    """
    short_selector = _fight()
    short_selector["selectors"] = [[1, "choose"]]
    lines = replay.selector_lines(short_selector)
    assert len(lines) == 1 and "no cards on the wire" in lines[0]

    short_meters = _fight()
    short_meters["meters_by_turn"] = [[1, 4, 1, 3]]      # pre-Encore column
    assert replay.trace(short_meters)["meters_by_turn"] == [[1, 4, 1, 3]]


def test_describe_run_reads_a_short_meter_row_as_unseen(monkeypatch):
    """The same row, through the reader that prints it. A meter row with no
    Encore column is a row from a recorder that had no Encore column, which is
    the definition of unseen."""
    rec = _fight()
    rec["meters_by_turn"] = [[1, 4, 1, 3]]
    monkeypatch.setattr(replay, "read_run_log", lambda stamp, i: [SEED_A, rec])
    assert "encore=UNSEEN" in replay.describe_run("a", 1)


# ============================================================ soak =========

def test_a_resource_map_carrying_a_zero_encore_reads_zero():
    """soak.py states the rule twice for this column: "UNSEEN, NOT EMPTY", and
    "a live combat with a resources map but no Encore in it is not an unseen
    meter -- it is a player who has no Encore. Only the ABSENCE of the map
    leaves the column unseen." A truthiness test on the resource value
    collapses the two: a spent meter reading 0 would be logged as a meter
    nobody could see, which is the error the -1 convention exists to prevent
    and would put a phantom blind spot in the fights where Encore was
    demonstrably empty.
    """
    state = {"state_type": "monster", "battle": {"round": 1},
             "player": {"hp": 40, "max_hp": 60, "status": [],
                        "resources": {"KLEEMOD_ENCORE": 0,
                                      "KLEEMOD_FANFARE": 0}}}
    meters = soak._meters(state)
    assert meters[3] == 0 and meters[3] != soak.METER_UNSEEN
    assert meters[0] == 0


def test_an_overlay_records_no_selector_answer():
    """`SELECTOR_SCREENS` excludes `overlay` on purpose -- "it is the shape a
    soft-lock takes ... and a screen nobody can answer has no choice to
    record". `test_the_selector_screen_set_excludes_overlay` pins the tuple;
    this pins the USE of it, because widening the condition at the call site
    to `MID_FIGHT` re-admits the overlay without touching the tuple at all.
    """
    d = ts._driver()
    d.fight = soak.FightTelemetry(act=1, floor=3, kind="monster")
    d.fight.turns = 2
    before = {"state_type": "overlay", "overlay": {"cards": []}}
    after = {"state_type": "monster"}

    d._observe(before, after, {"screen_type": "overlay"},
               {"action": "confirm"})
    assert d.fight.selectors == []

    d._observe({"state_type": "card_select", "card_select": {"cards": []}},
               after, {"screen_type": "choose"}, {"action": "select_card"})
    assert len(d.fight.selectors) == 1


def _bounded_driver(fights, max_fights, open_fight=False):
    d = ts._driver()
    d.max_fights = max_fights
    d.fights = [soak.FightTelemetry(act=1, floor=i + 1, kind="monster")
                for i in range(fights)]
    d.fight = (soak.FightTelemetry(act=1, floor=9, kind="elite")
               if open_fight else None)
    d._settle_transient = lambda state: state
    d._check = lambda state: None
    return d


def test_a_bounded_run_stops_at_the_nth_fight_and_not_the_n_plus_first():
    """`--max-fights N` is documented as "stop the run cleanly after N closed
    fights". N closed fights is the stop, so the bound is reached AT N: a
    strict comparison runs one extra fight in every bounded run, and a
    build-vs-build comparison of two recordings each one fight longer than
    they claim is still self-consistent and still wrong.
    """
    d = _bounded_driver(fights=2, max_fights=2)
    outcome, detail = d._drive({"state_type": "game_over",
                                "game_over": {"victory": False}})
    assert outcome == "bounded"
    assert "2 fight(s)" in detail


def test_a_bounded_run_never_stops_with_a_fight_still_open():
    """The stop is justified by the records it leaves: "the fight that is open
    has already closed by the time the count reaches the bound, so the records
    the comparison reads are complete records". Dropping the open-fight guard
    keeps the count right and lets the run end mid-fight, so the last record
    in the log is a fight that was interrupted rather than played -- and the
    comparison on the other side has no way to tell.
    """
    d = _bounded_driver(fights=2, max_fights=2, open_fight=True)
    outcome, _detail = d._drive({"state_type": "game_over",
                                 "game_over": {"victory": False}})
    assert outcome != "bounded"
    assert d.fight is None and len(d.fights) == 3


class _SeedSession:
    """A session that records when the seed channel was declared."""

    exit_code = None

    def __init__(self):
        self.declared = []

    def alive(self):
        return True

    def note_seed_channel(self):
        self.declared.append("note_seed_channel")


def test_a_run_that_reads_back_another_seed_files_a_defect(monkeypatch):
    """The read-back IS the verification, and the module says why it is a
    defect rather than a warning: "a chosen-seed soak whose runs quietly
    rolled their own seeds is the exact failure that a build-vs-build
    comparison cannot survive and cannot detect afterwards". Inverting the
    comparison files the defect on every HONOURED seed and passes silently on
    every refused one, which is the same instrument pointed backwards.
    """
    fake = ts._FakeBridge()
    monkeypatch.setattr(soak, "bridge", fake)

    d = ts._driver()
    d.session = _SeedSession()
    d.chosen_seed = "SSRWEGLNRG"
    d.log = None
    d.emit = lambda record: None
    d._to_main_menu = lambda: fake.get_state()
    d._embark = lambda state: state
    d._drive = lambda state: ("won", "")

    summary = d.run()
    assert fake.current_seed() != "SSRWEGLNRG"       # the game rolled its own
    assert summary["outcome"] == "defect"
    assert [x["kind"] for x in d.defects] == ["seed_not_honoured"]
    assert "seed_not_honoured" in soak._HARNESS_SIDE


def test_the_seed_channel_is_on_the_ledger_before_the_seed_is_set(monkeypatch):
    """`note_seed_channel` is documented as being triggered by the first
    CHOICE rather than by setup, precisely so that `--no-setup` -- which makes
    no game-dir changes and runs no setup -- still carries the undo for a
    global, sticky property it set. An entry written after the endpoint fires
    is an entry that does not exist for the one failure it is for: the
    endpoint answering and the harness dying in the same breath.
    """
    fake = ts._FakeBridge()
    order: list[str] = []
    session = _SeedSession()
    session.declared = order
    fake.set_seed = lambda seed: (order.append("set_seed")
                                  or {"status": "ok", "route": "lobby",
                                      "chosen": seed})
    monkeypatch.setattr(soak, "bridge", fake)
    monkeypatch.setattr(soak, "SETTLE_S", 0)

    d = ts._driver()
    d.session = session
    d.chosen_seed = "SSRWEGLNRG"
    d._embark(fake.get_state())

    assert order == ["note_seed_channel", "set_seed"]


def test_the_seed_channel_is_declared_once_for_a_whole_soak(tmp_path):
    """"Idempotent -- N runs share one entry." A ledger that grows an entry
    per run is a ledger nobody reads to the bottom, and the teardown walks it
    in reverse: N copies of one undo would fire the release N times and report
    N results for one change.
    """
    sess = soak.Session.__new__(soak.Session)
    sess.ledger = soak.Reversibility(tmp_path / "rev.json")
    sess._seed_entry = None

    sess.note_seed_channel()
    sess.note_seed_channel()
    sess.note_seed_channel()
    assert len(sess.ledger.entries) == 1


def test_the_seed_release_is_the_first_step_of_teardown(tmp_path):
    """"THE SEED RELEASE GOES FIRST, and it runs unconditionally." The
    `debug_override` route is a global, sticky property on NGame: left set,
    every later run in the session -- including one a person starts by hand --
    is the same run. Every other teardown step can take the game away
    (stopping the process, removing the bridge), and a release that runs after
    them is a release with nothing left to talk to.
    """
    sess = soak.Session.__new__(soak.Session)
    sess.ledger = soak.Reversibility(tmp_path / "rev.json")
    sess.dir = tmp_path
    order: list[str] = []

    sess._seed_entry = sess.ledger.record("seed", "seed:null")
    sess._speed_entry = sess.ledger.record("speed", "enabled:false")
    sess._launch_entry = sess.ledger.record("launch", "terminate")
    sess._bridge_entry = sess.ledger.record("bridge", "-Remove")
    sess._appid_entry = sess.ledger.record("appid", "delete")

    sess._release_seed = lambda: order.append("seed") or "released"
    sess._restore_speed = lambda: order.append("speed") or "restored"
    sess._stop_game = lambda: order.append("stop") or "terminated"
    sess._remove_bridge = lambda: order.append("bridge") or "removed"
    sess.teardown()

    assert order[0] == "seed", order
    assert order == ["seed", "speed", "stop", "bridge"]


def test_run_one_takes_the_first_named_seed(monkeypatch, tmp_path):
    """"run i takes seed i, cycling if fewer seeds than runs were named."
    Run 1 takes `--seed`'s first value. An index that skips it means every
    recording is filed under a run number whose seed belongs to a different
    run -- two soaks compared run-by-run would still agree with each other and
    disagree with the seeds printed on them.
    """
    seen: list[str | None] = []

    class _Session:
        ledger = soak.Reversibility(tmp_path / "rev.json")

        def __init__(self, *a, **kw):
            pass

        def setup(self):
            pass

        def teardown(self):
            pass

        def alive(self):
            return True

    class _Driver:
        def __init__(self, session, i, stamp, character, commit=None,
                     chosen_seed=None, max_fights=None):
            seen.append(chosen_seed)
            self.defects = []

        def run(self):
            return {"outcome": "won", "seed": seen[-1], "actions": 1,
                    "fights": 1, "defects": 0}

    monkeypatch.setattr(soak, "LOG_DIR", tmp_path)
    monkeypatch.setattr(soak, "Session", _Session)
    monkeypatch.setattr(soak, "RunDriver", _Driver)

    soak.soak(3, soak.DEFAULT_CHARACTER, do_setup=False,
              seeds=["FIRST", "SECOND"])
    assert seen == ["FIRST", "SECOND", "FIRST"]
