"""The per-turn channel of a sealed blind-play record.

The blind prompt REQUIRES a `thinking` sentence on every answer and the reply
schema enforces it, but until `notes` existed nothing carried that sentence
into the committed record — so a record could not evidence a claim about what
the tester said IN ADVANCE of a play, which is what a legibility slate grades.
These lock the channel and, more importantly, lock the thing that would make it
worthless: a second post-hoc writer silently truncating the first one's block.
"""
from __future__ import annotations

import json

from understudy import blindplay


def _session(tmp_path, turns):
    log = tmp_path / "sess"
    for i, (command, thinking) in enumerate(turns, 1):
        d = log / f"turn-{i:03d}"
        d.mkdir(parents=True)
        (d / "reply.json").write_text(
            json.dumps({"command": command, "thinking": thinking}),
            encoding="utf-8")
    return log


def test_every_answered_turn_carries_its_own_sentence(tmp_path):
    log = _session(tmp_path, [("end turn", "the front is blocked"),
                              ('play "Coral Guard"', "bank it for the front")])
    rows = blindplay.turn_notes(log)
    assert [r[0] for r in rows] == ["turn-001", "turn-002"]
    assert rows[0][1] == "end turn"
    assert rows[1][2] == "bank it for the front"


def test_a_turn_with_no_reply_is_skipped_not_faked(tmp_path):
    log = _session(tmp_path, [("end turn", "a note")])
    (log / "turn-002").mkdir()
    (log / "turn-003").mkdir()
    (log / "turn-003" / "reply.json").write_text("{ not json",
                                                 encoding="utf-8")
    assert [r[0] for r in blindplay.turn_notes(log)] == ["turn-001"]


def test_a_pipe_in_the_tester_words_does_not_break_the_table(tmp_path):
    log = _session(tmp_path, [("end turn", "block | or attack")])
    md = blindplay.notes_markdown(blindplay.turn_notes(log))
    assert r"block \| or attack" in md
    assert len([l for l in md.splitlines() if l.startswith("| `turn")]) == 1


def test_an_empty_session_says_so_rather_than_printing_a_table(tmp_path):
    md = blindplay.notes_markdown([])
    assert "No answered turn carried a note." in md
    assert "|---|" not in md


def test_the_audit_does_not_truncate_the_notes_and_the_notes_keep_the_audit(
        tmp_path):
    record = tmp_path / "record.md"
    record.write_text("# Blind play session `x`\n\nthe fight records\n",
                      encoding="utf-8")

    blindplay._splice(record, "## Leak audit", "## Leak audit\n\nfirst\n")
    blindplay._splice(record, "## Turn by turn", "## Turn by turn\n\nnotes\n")
    text = record.read_text(encoding="utf-8")
    assert "the fight records" in text and "notes" in text and "first" in text
    # order is fixed, not insertion order
    assert text.index("## Turn by turn") < text.index("## Leak audit")

    blindplay._splice(record, "## Leak audit", "## Leak audit\n\nsecond\n")
    text = record.read_text(encoding="utf-8")
    assert "notes" in text, "the audit re-run dropped the per-turn channel"
    assert "second" in text and "first" not in text
