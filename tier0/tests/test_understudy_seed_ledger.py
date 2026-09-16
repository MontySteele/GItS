"""EB-208 (c): the seed ledger — which seed stages which encounter.

No game and no launch. Every test here reads a turn directory that was staged
long ago and sealed, or a synthetic one built in `tmp_path`; nothing writes
into `review/qa/` (R101b) and nothing here finds a seed, because FINDING one
is game time and is what the row still owes.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from understudy import seed_ledger as S

REPO = Path(__file__).resolve().parents[2]
SEALED_TURN = "klee-sparks-r1-t04"


def _turn(tmp_path: Path, *, seed: str = "SEEDSEED11",
          enemies=("Fuzzy Wurm Crawler",), character: str = "Klee",
          turn_id: str = "t01") -> Path:
    """A SYNTHETIC staged turn, in `observed.json`'s real shape."""
    d = tmp_path / turn_id
    d.mkdir(parents=True, exist_ok=True)
    d.joinpath("observed.json").write_text(json.dumps({
        "turn_id": turn_id, "run_seed": seed,
        "state": {"state_type": "monster",
                  "run": {"act": 1, "floor": 4},
                  "player": {"character": character},
                  "battle": {"enemies": [{"name": n} for n in enemies]}},
    }), encoding="utf-8")
    return tmp_path


# ------------------------------------------------------------- the key -----

def test_the_encounter_key_counts_the_bodies():
    """The thing a turn file wants to pin is THREE BODIES. A key that dropped
    the count would answer a one-body seed to a three-body question, which is
    the whole failure `EB-208` is about."""
    one = S.encounter_key(["Fuzzy Wurm Crawler"])
    three = S.encounter_key(["Fuzzy Wurm Crawler"] * 3)
    assert one != three
    assert three == "fuzzy_wurm_crawler_x3"


def test_the_key_does_not_depend_on_the_order_the_wire_printed():
    """The wire's order is the board's left-to-right and is not part of what
    a turn file asked for."""
    assert (S.encounter_key(["Slug", "Nibbit", "Slug"])
            == S.encounter_key(["Slug", "Slug", "Nibbit"]))
    assert S.encounter_key(["Nibbit", "Slug", "Slug"]) == "nibbit_x1+slug_x2"


def test_an_encounter_with_no_enemies_is_not_an_encounter():
    with pytest.raises(S.SeedLedgerError):
        S.encounter_key([])


# ------------------------------------------------------------ the turn -----

def test_a_row_is_read_off_the_live_board_and_the_seed_the_game_used(tmp_path):
    """`observed.json` is the file with both halves: `run_seed` is what the
    game actually used, and `state` is the board that seed produced. Nothing
    is inferred from the DECLARED board -- what is recorded is what the seed
    DID."""
    qa = _turn(tmp_path, seed="XT4BE7LFY5XH",
               enemies=("Fuzzy Wurm Crawler",) * 3)
    row = S.row_from_turn("t01", build="0.2.3352+proto", qa_dir=qa,
                          why="the three-body board")
    assert row["seed"] == "XT4BE7LFY5XH"
    assert row["character"] == "klee"
    assert row["encounter"] == "fuzzy_wurm_crawler_x3"
    assert row["enemy_count"] == 3
    assert row["build"] == "0.2.3352+proto"
    assert row["turn_id"] == "t01"


def test_a_row_without_a_build_is_refused(tmp_path):
    """A seed is a seed for the generator the PACKAGE hands the game. A row
    with no build answers a question about a world that has moved, which is
    the failure `EB-208` (a) was built to make visible rather than to
    reintroduce here."""
    qa = _turn(tmp_path)
    with pytest.raises(S.SeedLedgerError, match="BUILD"):
        S.row_from_turn("t01", build="  ", qa_dir=qa)


def test_a_turn_with_no_recorded_seed_is_refused(tmp_path):
    """A board staged on a seed nobody wrote down cannot be reached again."""
    qa = _turn(tmp_path, seed="")
    with pytest.raises(S.SeedLedgerError, match="run_seed"):
        S.row_from_turn("t01", build="0.2", qa_dir=qa)


def test_this_tool_never_stages_a_board(tmp_path):
    """It reads a turn that has ALREADY been staged, and says so rather than
    quietly producing an empty row."""
    with pytest.raises(S.SeedLedgerError, match="never stages one"):
        S.row_from_turn("no-such-turn", build="0.2", qa_dir=tmp_path)


def test_a_sealed_turn_reads_without_being_written_to(tmp_path):
    """Against a REAL closed turn directory, which is read-only (R101b): the
    row comes out and the directory is untouched."""
    before = sorted(p.name for p in (REPO / "review" / "qa"
                                     / SEALED_TURN).iterdir())
    row = S.row_from_turn(SEALED_TURN, build="0.2.3352+proto")
    assert row["seed"] and row["character"] == "klee"
    assert row["enemy_count"] >= 1
    after = sorted(p.name for p in (REPO / "review" / "qa"
                                    / SEALED_TURN).iterdir())
    assert before == after


# ---------------------------------------------------------- the ledger -----

def test_the_shipped_ledger_is_empty_and_says_why():
    """WHAT IS OWED, IN THE ARTIFACT. The format and the recorder are built;
    the Klee three-body seed hunt is game time and is not done. A reader who
    opens this file before the hunt has run should find out why it is empty
    rather than assume it is broken."""
    ledger = S.load()
    assert ledger["rows"] == []
    assert ledger["schema_version"] == S.SCHEMA_VERSION
    assert "OWED" in ledger["note"] and "EB-208" in ledger["note"]


def test_recording_the_same_turn_twice_writes_one_row(tmp_path):
    """A ledger that counted one seed twice would read as two independent
    confirmations of it."""
    qa = _turn(tmp_path / "qa")
    path = tmp_path / "ledger.json"
    row = S.row_from_turn("t01", build="0.2", qa_dir=qa)
    ledger, new = S.record(row, path)
    assert new and len(ledger["rows"]) == 1
    ledger, new = S.record(dict(row), path)
    assert not new and len(ledger["rows"]) == 1


def test_a_second_seed_for_the_same_key_is_a_second_row(tmp_path):
    """More than one seed staging an encounter is the useful case, not a
    duplicate."""
    path = tmp_path / "ledger.json"
    qa_a = _turn(tmp_path / "a", seed="AAAAAAAAAA")
    qa_b = _turn(tmp_path / "b", seed="BBBBBBBBBB")
    S.record(S.row_from_turn("t01", build="0.2", qa_dir=qa_a), path)
    ledger, new = S.record(S.row_from_turn("t01", build="0.2", qa_dir=qa_b),
                           path)
    assert new and {r["seed"] for r in ledger["rows"]} == {"AAAAAAAAAA",
                                                          "BBBBBBBBBB"}


def test_the_note_stops_claiming_the_ledger_is_empty_once_it_is_not(tmp_path):
    """A banner contradicting the file it sits at the top of is the thing
    `CLAUDE.md` calls a supersession banner."""
    path = tmp_path / "ledger.json"
    qa = _turn(tmp_path / "qa")
    ledger, _new = S.record(S.row_from_turn("t01", build="0.2", qa_dir=qa),
                            path)
    assert "EMPTY BY DESIGN" not in ledger["note"]


def test_find_narrows_on_every_part_of_the_key(tmp_path):
    path = tmp_path / "ledger.json"
    for i, (seed, char, enemies, build) in enumerate((
            ("AAAAAAAAAA", "Klee", ("Wurm",) * 3, "0.2"),
            ("BBBBBBBBBB", "Klee", ("Wurm",), "0.2"),
            ("CCCCCCCCCC", "Kokomi", ("Wurm",) * 3, "0.2"),
            ("DDDDDDDDDD", "Klee", ("Wurm",) * 3, "0.3"))):
        qa = _turn(tmp_path / f"q{i}", seed=seed, character=char,
                   enemies=enemies)
        S.record(S.row_from_turn("t01", build=build, qa_dir=qa), path)
    got = S.find(character="klee", build="0.2",
                 encounter="wurm_x3", path=path)
    assert [r["seed"] for r in got] == ["AAAAAAAAAA"]
    assert len(S.find(character="klee", path=path)) == 3
    assert [r["seed"] for r in S.find(enemy_count=3, build="0.3", path=path)
            ] == ["DDDDDDDDDD"]


def test_a_ledger_from_a_future_schema_is_refused_rather_than_guessed(
        tmp_path):
    """A reader that guessed which fields a row has would answer a seed
    against the wrong key."""
    path = tmp_path / "ledger.json"
    path.write_text(json.dumps({"schema_version": S.SCHEMA_VERSION + 1,
                                "rows": []}), encoding="utf-8")
    with pytest.raises(S.SeedLedgerError, match="schema_version"):
        S.load(path)


# ------------------------------------------------------------- the CLI -----

def test_the_cli_records_and_finds(tmp_path, capsys):
    qa = _turn(tmp_path / "qa", seed="ZZZZZZZZZZ", enemies=("Wurm",) * 3)
    path = tmp_path / "ledger.json"
    assert S.main(["record", "t01", "--build", "0.2.3352+proto",
                   "--qa-dir", str(qa), "--ledger", str(path)]) == 0
    assert "recorded: ZZZZZZZZZZ" in capsys.readouterr().out
    # Twice is idempotent and SAYS so.
    S.main(["record", "t01", "--build", "0.2.3352+proto",
            "--qa-dir", str(qa), "--ledger", str(path)])
    assert "already recorded" in capsys.readouterr().out
    assert S.main(["find", "--encounter", "wurm_x3",
                   "--ledger", str(path)]) == 0
    assert "ZZZZZZZZZZ" in capsys.readouterr().out


def test_a_find_that_matches_nothing_exits_nonzero_and_says_which(tmp_path,
                                                                  capsys):
    """An empty ANSWER and an empty LEDGER are different facts, and a caller
    about to spend a launch needs to know which one it got."""
    path = tmp_path / "ledger.json"
    assert S.main(["find", "--character", "klee", "--ledger", str(path)]) == 1
    out = capsys.readouterr().out
    assert "the ledger holds 0" in out and "OWED" in out


def test_the_cli_refuses_a_record_with_no_build(tmp_path, capsys):
    """`--build` is required by the parser itself, so the refusal is the
    parser's and cannot be bypassed by a caller that forgot."""
    with pytest.raises(SystemExit):
        S.main(["record", "t01", "--ledger", str(tmp_path / "l.json")])
