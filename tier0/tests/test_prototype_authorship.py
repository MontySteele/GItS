"""EB-190: recorded authorship, and the seat refusing its own family's work.

R217 C fixes the roles at two model families -- Claude authors, GPT grades and
reviews -- and OPERATIONS' "Doctrine seat protocol" says why: a seat that
writes a row and then grades it has graded its own work, and the outcome is
not evidence. Klee slice 1 is the case that made it mechanical.

The RED FIXTURES are the point of this module. Each one proves a door SHUTS:

  * a turn carrying a `gpt`-authored row refuses `seat grade` -- before codex
    is contacted, so it runs in CI with no sign-in and no network;
  * a review brief that asks the seat for a REMEDY refuses `seat review`;
  * a surface row with no `authored_by` (or an unknown family) refuses the
    generator;
  * the lint's debt list is EXACT in both directions -- an unlisted violation
    is red, and a listed entry that has stopped tripping is red too.

And one green fixture that is load-bearing: the field must not move one byte
of generated C#, or `--check` would start failing for a reason that has
nothing to do with a card.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from understudy import authorship, seat

REPO = Path(__file__).resolve().parents[2]

# Two REAL turns from Klee slice 1. t02's row has always been Claude's alone;
# t04's row is Rummage, whose text the seat re-wrote in round 1.
#
# SINCE KLEE ROUND 3 (2026-08-29) THE SURFACE HOLDS NO `gpt`-AUTHORED ROW AT
# ALL: Rummage and Slow Burn were re-derived Claude-side from the seat's named
# clause and both read `authored_by: [claude]` again. So the refusal fixtures
# below can no longer be driven off the shipped sheet, and they monkeypatch
# `authorship.SURFACE` to a one-row sheet that puts `gpt` back on the row this
# real turn carries. The TURN is still real and the CLI path is still the whole
# path -- only the provenance the sheet records is supplied by the fixture.
CLEAN_TURN = "klee-slice1-t02"
AUTHORED_TURN = "klee-slice1-t04"
AUTHORED_TURN_ROW = "proto_spark_priced_draw"


def _sheet_with_a_gpt_authored_row(tmp_path, monkeypatch):
    """Put `gpt` back on `AUTHORED_TURN`'s row, for the refusal fixtures."""
    sheet = tmp_path / "surface-with-a-gpt-row.yaml"
    sheet.write_text(yaml.safe_dump(
        [{"id": AUTHORED_TURN_ROW, "authored_by": ["claude", "gpt"]}]),
        encoding="utf-8")
    monkeypatch.setattr(authorship, "SURFACE", sheet)
    return sheet


# ------------------------------------------------------------ the schema ---

def test_every_shipped_row_records_a_valid_authored_by():
    rows = yaml.safe_load(
        authorship.SURFACE.read_text(encoding="utf-8")) or []
    assert rows, "the surface is empty; this test would prove nothing"
    for row in rows:
        assert not authorship.field_findings(row), row.get("id")


def test_the_klee_rows_are_claude_authored_again_after_round_three():
    """Rummage's text and Slow Burn's number WERE the seat's, and rounds 1 and
    2 recorded that honestly. Klee round 3 re-derived both from the clause the
    seat named, discarded its text and its number, and set the provenance back
    -- so all three Klee slice-1 rows are Claude's alone."""
    known = authorship.rows_authorship()
    assert known["proto_spark_priced_draw"] == ["claude"]
    assert known["proto_spark_burst_conversion"] == ["claude"]
    assert known["proto_spark_priced_strike"] == ["claude"]


def test_no_shipped_row_records_a_contributing_family():
    """The state round 3 restored, asserted over the WHOLE surface rather than
    three ids: `claude` authors, and nothing else is recorded as having
    written a row. A future slice that accepts a seat's text will fail here,
    which is the point -- it must be a deliberate edit, not a drift."""
    for rid, families in authorship.rows_authorship().items():
        assert families == [authorship.AUTHOR_FAMILY], rid


@pytest.mark.parametrize("row", [
    {"id": "proto_x", "character": "kokomi"},                  # absent
    {"id": "proto_x", "authored_by": []},                      # empty
    {"id": "proto_x", "authored_by": "claude"},                # not a list
    {"id": "proto_x", "authored_by": ["mistral"]},             # unknown
    {"id": "proto_x", "authored_by": ["claude", "claude"]},    # repeated
])
def test_a_bad_authored_by_is_a_finding(row):
    assert authorship.field_findings(row)


def test_the_generator_refuses_a_row_without_the_field(tmp_path, monkeypatch):
    """RED FIXTURE. A row the seat's refusal cannot read is a row that puts
    the separation back to being a procedure somebody remembers."""
    import tools.gen_prototype_cards as genproto

    sheet = tmp_path / "prototype-surface.yaml"
    sheet.write_text(yaml.safe_dump([{
        "id": "proto_no_author", "name": "Nameless", "character": "kokomi",
        "cost": 1, "type": "skill", "rarity": "common",
        "effects": [{"op": "block", "amount": 5}]}]), encoding="utf-8")
    monkeypatch.setattr(genproto, "SHEET", sheet)
    with pytest.raises(SystemExit) as excinfo:
        genproto.plan()
    assert "authored_by" in str(excinfo.value)

    sheet.write_text(yaml.safe_dump([{
        "id": "proto_no_author", "name": "Nameless", "character": "kokomi",
        "authored_by": ["deepmind"],
        "cost": 1, "type": "skill", "rarity": "common",
        "effects": [{"op": "block", "amount": 5}]}]), encoding="utf-8")
    with pytest.raises(SystemExit) as excinfo:
        genproto.plan()
    assert "unknown famil" in str(excinfo.value)


def test_the_field_cannot_move_generated_output(tmp_path, monkeypatch):
    """The green fixture that keeps `--check` honest: provenance is stripped
    before the emitter, so the same row with and without it emits the same C#.
    """
    import tools.gen_prototype_cards as genproto

    row = {"id": "proto_same", "name": "Same Card", "character": "kokomi",
           "cost": 1, "type": "skill", "rarity": "common",
           "effects": [{"op": "block", "amount": 5}]}

    sheet = tmp_path / "prototype-surface.yaml"
    monkeypatch.setattr(genproto, "SHEET", sheet)
    sheet.write_text(yaml.safe_dump([dict(row, authored_by=["claude"])]),
                     encoding="utf-8")
    with_field = genproto.plan().generated["proto_same"]
    sheet.write_text(yaml.safe_dump([dict(row, authored_by=["claude", "gpt"])]),
                     encoding="utf-8")
    other_field = genproto.plan().generated["proto_same"]
    assert with_field == other_field


def test_the_card_schema_never_sees_the_field(tmp_path):
    """`Card.from_dict` is total on unknown fields, so the loader must strip
    provenance rather than the surface omitting it."""
    from tier0.content import loader

    sheet = tmp_path / "prototype-surface.yaml"
    sheet.write_text(yaml.safe_dump([{
        "id": "proto_loads", "name": "Loads", "character": "kokomi",
        "authored_by": ["claude", "gpt"],
        "cost": 1, "type": "skill", "rarity": "common",
        "effects": [{"op": "block", "amount": 5}]}]), encoding="utf-8")
    cards = loader.prototype_cards(sheet)
    assert [c.id for c in cards] == ["proto_loads"]
    assert not hasattr(cards[0], "authored_by")


# ------------------------------------------------------ turn -> its rows ---

def test_a_turn_resolves_to_the_prototype_rows_it_carries():
    assert authorship.rows_in_turn(AUTHORED_TURN) == \
        ["proto_spark_priced_draw"]
    assert authorship.rows_in_turn(CLEAN_TURN) == \
        ["proto_spark_priced_strike"]
    # A shipped-card turn resolves to nothing, and that is a PASS, not a gap.
    assert authorship.rows_in_turn("klee-slice1-t03") == []
    assert authorship.rows_in_turn("no-such-turn-id") == []


def test_both_declarations_are_read(tmp_path):
    """A turn names its cards twice -- the `give:` step and the tier0 mirror.
    Reading only one would pass a turn that grants a row it does not mirror."""
    (tmp_path / "a.yaml").write_text(yaml.safe_dump({
        "id": "only-staged",
        "staging": [{"give": {"card": "KLEEMOD-PROTO_ONLY_STAGED"}}]}),
        encoding="utf-8")
    (tmp_path / "b.yaml").write_text(yaml.safe_dump({
        "id": "only-mirrored",
        "board": {"hand": ["proto_only_mirrored", "duck_and_cover"]}}),
        encoding="utf-8")
    assert authorship.rows_in_turn("only-staged", tmp_path) == \
        ["proto_only_staged"]
    assert authorship.rows_in_turn("only-mirrored", tmp_path) == \
        ["proto_only_mirrored"]


# ------------------------------------------------------- `seat grade` -----

def test_a_gpt_authored_row_refuses_the_gpt_seat(tmp_path, capsys,
                                                 monkeypatch):
    """THE RED FIXTURE. No network and no codex: the refusal lands before the
    binary is even located, which is also why `--dry-run` cannot get past it.

    The provenance comes from a fixture sheet since round 3 emptied the real
    surface of `gpt`-authored rows; the turn, the CLI and the refusal path are
    the shipped ones.
    """
    _sheet_with_a_gpt_authored_row(tmp_path, monkeypatch)
    rc = seat.main(["grade", AUTHORED_TURN, "--dry-run",
                    "--log-root", str(tmp_path)])
    assert rc == 1
    err = capsys.readouterr().err
    assert "seat_authored_row" in err
    assert "proto_spark_priced_draw" in err
    assert "'gpt'" in err

    session = next(tmp_path.glob(f"{AUTHORED_TURN}-*"))
    blob = json.loads((session / "seat.json").read_text(encoding="utf-8"))
    assert blob["refused"] == "seat_authored_row"
    assert blob["prototype_rows"] == ["proto_spark_priced_draw"]
    # Nothing was executed, and nothing was PREPARED to be executed.
    assert "dry_run" not in blob


def test_a_claude_only_row_lets_the_gpt_seat_through(tmp_path, capsys):
    rc = seat.main(["grade", CLEAN_TURN, "--dry-run",
                    "--log-root", str(tmp_path)])
    assert rc == 0
    assert "DRY RUN" in capsys.readouterr().out


def test_seat_authored_row_is_a_named_refusal():
    assert "seat_authored_row" in seat.REFUSAL_REASONS


# ------------------------------------------------------ `seat review` -----

@pytest.mark.parametrize("brief", [
    "Read the arms. Then rewrite the row that fails.",
    "For any arm that fails, propose a fix.",
    "If the cost is wrong, what number should it be?",
    "Suggest new text for the failing arm.",
    "Tell me how would you fix arm 2.",
])
def test_a_remedy_asking_brief_is_found(brief):
    assert seat.remedy_findings(brief), brief


@pytest.mark.parametrize("brief", [
    "Answer FOLLOWS or REQUIRES_MODIFICATION. Do not rewrite the row.",
    "You may not propose a fix; name the clause instead.",
    "Never suggest a number. The number is derived from a shipped card.",
    "Name the clause. No rewrite, no remedy, no text.",
])
def test_a_brief_that_forbids_a_remedy_passes(brief):
    assert not seat.remedy_findings(brief), brief


@pytest.mark.parametrize("brief", [
    "Further copies need a second job, which is a re-authoring question, not a number.",
    "| `all_streams_flow` | +1 per 2 Charge | **Re-author.** It was authored as the reader |",
    "   # W2b took the family five -> three; this rewrite is what completes R208.",
    "```" + chr(10) + "rewrite the row" + chr(10) + "```" + chr(10) + "Name the clause.",
])
def test_descriptive_uses_in_inlined_material_pass(brief):
    """A brief that INLINES a proposal or a sheet carries the words as
    description (a table verdict, a comment, prose about a question), not as
    an ask. The kokomi-kurage-memory brief was refused for these."""
    assert not seat.remedy_findings(brief), brief


def test_the_shipped_review_prompts_pass():
    """The four briefs already committed under review/qa/ must not be refused
    by a guard added after them -- a gate that red-lights the existing corpus
    is a gate nobody will run."""
    for path in sorted((REPO / "review" / "qa").glob("*review-prompt*.txt")):
        assert not seat.remedy_findings(
            path.read_text(encoding="utf-8")), path.name


def test_seat_review_refuses_a_remedy_asking_brief(tmp_path, capsys):
    """RED FIXTURE, through the CLI, with `--dry-run` so nothing can run."""
    brief = tmp_path / "prompt.txt"
    brief.write_text("Read arm 1 against the charter and rewrite it.",
                     encoding="utf-8")
    rc = seat.main(["review", str(brief), "--dry-run"])
    assert rc == 1
    err = capsys.readouterr().err
    assert "review_asks_for_a_remedy" in err
    assert "rewrite" in err


def test_seat_review_refuses_a_brief_naming_the_seats_own_row(tmp_path,
                                                              capsys,
                                                              monkeypatch):
    """The pair-review half of the same door: the brief names its TURNS, the
    turns resolve to rows, and one of those rows is the seat's own work. Same
    fixture sheet as the grade half, for the same round-3 reason."""
    _sheet_with_a_gpt_authored_row(tmp_path, monkeypatch)
    brief = tmp_path / "prompt.txt"
    brief.write_text(
        f"Review the three arms. The turns are {CLEAN_TURN} and "
        f"{AUTHORED_TURN}. Answer FOLLOWS or REQUIRES_MODIFICATION.",
        encoding="utf-8")
    rc = seat.main(["review", str(brief), "--dry-run"])
    assert rc == 1
    err = capsys.readouterr().err
    assert "seat_authored_row" in err
    assert "proto_spark_priced_draw" in err


def test_seat_review_passes_a_clean_brief_and_prepends_the_protocol(tmp_path,
                                                                    capsys):
    brief = tmp_path / "prompt.txt"
    brief.write_text(f"Review {CLEAN_TURN}. Answer FOLLOWS or "
                     f"REQUIRES_MODIFICATION and name the clause.",
                     encoding="utf-8")
    assert seat.main(["review", str(brief), "--dry-run"]) == 0
    assert "protocol:" in capsys.readouterr().out


def test_the_protocol_carries_the_whole_rule():
    """The four clauses OPERATIONS' doctrine-seat block names, in the text the
    seat is actually handed -- not in whichever prompt file the round used."""
    text = seat.REVIEW_PROTOCOL
    assert "FOLLOWS" in text and "REQUIRES_MODIFICATION" in text
    assert "CLAUSE" in text
    assert "DISCARDED" in text
    for banned in ("card text", "a number", "a mode"):
        assert banned in text
    assert seat.build_review_prompt("BODY").startswith(text)
    assert seat.build_review_prompt("BODY").endswith("BODY")


def test_the_pair_read_has_its_own_output_shape_and_the_same_ban():
    """The seat has TWO review jobs. Klee round 3 found that one protocol was
    prepended to both: the doctrine gate's "That is the whole output" and "It
    overrides anything below that conflicts with it" turned a pair read into
    two lines of FOLLOWS, because the seat obeyed the protocol over the brief.

    The REMEDY BAN is identical in both roles -- that half is the rule. Only
    the output shape differs.
    """
    pair = seat.REVIEW_ROLES["pair"]
    doctrine = seat.REVIEW_ROLES["doctrine"]
    assert pair != doctrine

    # The pair read's own output shape, which the doctrine text forbids.
    for token in ("NOT PLAYABLE", "PLAYABLE", "ESCALATE", "numbered questions"):
        assert token in pair, token
    assert "FOLLOWS" not in pair
    # ...and it says plainly what PLAYABLE is not.
    flat = " ".join(pair.split())
    assert "PLAYABLE means the arm is worth asking again with whole-fight play" \
        in flat
    assert "It is NOT ship approval, not a balance reading and not validation" \
        in flat

    # The ban, in both, and in the same words.
    for text in (pair, doctrine):
        assert "DISCARDED" in text
        for banned in ("card text", "a number", "a mode"):
            assert banned in text
        assert "MODEL FAMILY" in text

    assert seat.build_review_prompt("BODY", "pair").startswith(pair)
    assert seat.build_review_prompt("BODY", "pair").endswith("BODY")
    # The DEFAULT is unchanged, so every existing caller still gets the gate.
    assert seat.build_review_prompt("BODY") == \
        seat.build_review_prompt("BODY", "doctrine")


def test_an_unknown_review_role_raises_rather_than_falling_back():
    """A silent fallback is how a pair read gets the gate's output shape
    without anyone noticing -- which is the defect this door was added for."""
    with pytest.raises(seat.SeatError) as excinfo:
        seat.build_review_prompt("BODY", "whatever")
    assert "whatever" in str(excinfo.value)


def test_the_committed_pair_reads_are_run_in_the_pair_role(tmp_path, capsys):
    """The CLI half, with `--dry-run` so nothing runs: `--role pair` reaches
    the prompt, and the line the operator reads names the role."""
    brief = tmp_path / "prompt.txt"
    brief.write_text(f"Review {CLEAN_TURN}. Answer the five questions and "
                     f"give NOT PLAYABLE, PLAYABLE or ESCALATE.", encoding="utf-8")
    assert seat.main(["review", str(brief), "--role", "pair",
                      "--dry-run"]) == 0
    out = capsys.readouterr().out
    assert "protocol:   pair" in out


# ------------------------------------------------------------- the lint ---

def test_the_lint_is_green_on_the_shipped_tree():
    import tools.lint_prototype_authorship as lint

    assert lint.findings() == []


def test_the_debt_list_is_exactly_the_records_that_trip(tmp_path):
    """EXACT in both directions. An unlisted violation is red; a listed entry
    that has stopped tripping is red, so the set can only shrink."""
    import tools.lint_prototype_authorship as lint

    offenders = set(lint.grade_offenders())
    assert offenders == set(lint.DEBT), (
        f"the debt list and the tree disagree: only in tree "
        f"{sorted(offenders - set(lint.DEBT))}, only in DEBT "
        f"{sorted(set(lint.DEBT) - offenders)}")
    # EMPTY since Klee round 3 re-derived Rummage and Slow Burn: with no
    # contributing family on either row, the four records that opened this
    # list stop tripping check (2), and the staleness rule then required their
    # deletion. The rounds themselves stand as published (R101b).
    assert offenders == set()
    for why in lint.DEBT.values():
        assert why.strip(), "every carried entry states its reason"


def test_an_unlisted_violation_is_red(tmp_path):
    """RED FIXTURE for the lint itself, on fixtures rather than on the tree."""
    import tools.lint_prototype_authorship as lint

    sheet = tmp_path / "surface.yaml"
    sheet.write_text(yaml.safe_dump(
        [{"id": "proto_fix", "authored_by": ["claude", "gpt"]}]),
        encoding="utf-8")
    turns = tmp_path / "turns"
    turns.mkdir()
    (turns / "t.yaml").write_text(yaml.safe_dump(
        {"id": "fix-t01", "board": {"hand": ["proto_fix"]}}),
        encoding="utf-8")
    qa = tmp_path / "qa" / "fix-t01"
    qa.mkdir(parents=True)
    (qa / "form-codex.json").write_text(
        json.dumps({"grader": {"model": "gpt-5.6-sol"}}), encoding="utf-8")

    assert lint.findings(qa.parent, turns, sheet, debt={})
    assert not lint.findings(qa.parent, turns, sheet,
                             debt={"fix-t01": "carried, with a reason"})
    stale = lint.findings(qa.parent, turns, sheet,
                          debt={"fix-t01": "ok", "gone-t01": "ok"})
    assert any("gone-t01" in line and "stale" in line for line in stale)
