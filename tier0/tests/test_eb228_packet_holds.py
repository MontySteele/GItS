"""EB-228: the packet-holds lint, and the sentence it was built to catch.

Kokomi slice 2's section 9 said *"Staging the round-2 boards and whole-fight
play of the two advanced arms are HELD on this pick"* and named `PICK 2`, a
heading inside its own packet. No `QUEUE.md` row was minted, `STATE.md`
reported no prototype-slice row open, and a round-2 run was scheduled on
2026-08-30 against that clean-looking register and stopped at the door.

The lint is only worth having if it BITES and only survivable if it does not
bite on ordinary prose, so the fixtures here go both ways:

  * the historical sentence, with no id, is a finding;
  * the same sentence citing an OPEN `QUEUE.md` id is clean, and citing a
    CLOSED one is not -- the discharge is liveness, not mention;
  * every exclusion the tool documents is exercised on the shape that
    justified it, all five drawn from real packet text;
  * the two register readers are tested on the header row that would
    otherwise let the literal word `ID` discharge a hold;
  * and the real `review/active/` tree is green under the real gate, so a
    packet that grows an unminted hold fails here as well as in the lint lane.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]

_spec = importlib.util.spec_from_file_location(
    "lint_packet_holds", REPO / "tools" / "lint_packet_holds.py")
assert _spec and _spec.loader
lint = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = lint
_spec.loader.exec_module(lint)


# The sentence verbatim from the packet that left HEAD with the slice --
# `git show a1df7d6:review/active/kokomi-slice-2-2026-08-29.md` -- wrapped
# exactly as it wrapped it: the hold phrase spans the line break, which is
# the reason the tool normalises whitespace at all.
HELD = (
    "**Staging the round-2 boards and whole-fight play of the two advanced\n"
    "arms are HELD on this pick.** Options 1-4 retire arms 1-4 as authored --\n"
    "every one of them prices or banks Charge under the current accrual rule.\n"
)

QUEUE = (
    "# QUEUE\n\n"
    "| ID | Decision needed | Status | Provenance |\n"
    "|---|---|---|---|\n"
    "| `M69` | **Ask:** rule on X9 | OPEN -- the graded read is in | R188 |\n"
    "| `S4-G12` / `CC-G1` | **Ask:** approve the faces | OPEN -- ready | x |\n"
    "| `M14` | **Ask:** amend the trigger | CLOSED (R231) | x |\n"
)

BACKLOG = (
    "# BACKLOG\n\n"
    "| ID | Item | Provenance |\n"
    "|---|---|---|\n"
    "| `EB-188` | **Scope:** prototype rows are quarantined | 2026-08-29 |\n"
)


def _tree(tmp_path: Path, *packets: str) -> Path:
    """A miniature repo: two registers and however many active packets."""
    (tmp_path / "docs" / "current").mkdir(parents=True)
    (tmp_path / "docs" / "current" / "QUEUE.md").write_text(
        QUEUE, encoding="utf-8")
    (tmp_path / "docs" / "current" / "BACKLOG.md").write_text(
        BACKLOG, encoding="utf-8")
    active = tmp_path / "review" / "active"
    active.mkdir(parents=True)
    for index, body in enumerate(packets, start=1):
        (active / f"packet-{index}.md").write_text(
            f"Status: OPEN (pick {index})\n\n" + body, encoding="utf-8")
    return tmp_path


def _run(tmp_path: Path, *packets: str) -> list[str]:
    """Findings the lint reports over that miniature repo."""
    root = _tree(tmp_path, *packets)
    known = (lint.queue_open_ids(
        (root / "docs" / "current" / "QUEUE.md").read_text(encoding="utf-8"))
        | lint.backlog_ids(
            (root / "docs" / "current" / "BACKLOG.md").read_text(
                encoding="utf-8")))
    files = [(p.name, p.read_text(encoding="utf-8"))
             for p in sorted((root / "review" / "active").glob("*.md"))]
    return lint.findings(files, known)


def test_the_historical_sentence_is_a_finding(tmp_path: Path) -> None:
    """A hold on a pick named only by a packet heading fails.

    This is the whole row: the packet was right, the register could not see
    it, and a run was scheduled against the register.
    """
    hits = _run(tmp_path, HELD)
    assert len(hits) == 1, hits
    assert "HELD on this pick" in hits[0]
    assert "packet-1.md:3" in hits[0]


def test_naming_an_open_queue_id_discharges(tmp_path: Path) -> None:
    """The fix the finding asks for actually clears it."""
    assert _run(tmp_path, HELD.replace("this pick", "the `M69` pick")) == []


def test_a_compound_queue_cell_defines_every_id(tmp_path: Path) -> None:
    """`S4-G12` / `CC-G1` in one cell is two open ids, not one."""
    assert _run(tmp_path, HELD.replace("this pick", "the `CC-G1` pick")) == []


def test_naming_a_closed_queue_id_does_not_discharge(tmp_path: Path) -> None:
    """The discharge is LIVENESS, not mention.

    `M14` is a real row in the fixture register and it is CLOSED. A hold that
    cites it is held on nothing, which is the same defect wearing an id.
    """
    hits = _run(tmp_path, HELD.replace("this pick", "the `M14` pick"))
    assert len(hits) == 1, hits


def test_naming_a_backlog_row_discharges(tmp_path: Path) -> None:
    """A hold on engineering work is minted and visible.

    `EB-228`'s complaint is a hold that reaches NO register, not one that
    reaches the other. The historical packet's own *blocked on `EB-188`* is
    the shape: real, registered, and not a defect.
    """
    assert _run(tmp_path, HELD.replace("this pick", "the `EB-188` work")) == []


def test_exclusion_1_fenced_code(tmp_path: Path) -> None:
    """A pasted transcript or sample row is not this packet's own claim."""
    assert _run(tmp_path, "```\n" + HELD + "```\n") == []


def test_exclusion_2_table_row(tmp_path: Path) -> None:
    """`kokomi-overhaul-round-2`'s run table has a `Stopped by` column.

    Every row of it says why a seat's session ended. None of them is a hold
    on a pick, and a lint that read them as holds would fire on every graded
    run this repo files.
    """
    table = ("| Seat | Seed | Stopped by |\n"
             "|---|---|---|\n"
             "| Opus | 4471 | held on the pick |\n")
    assert _run(tmp_path, table) == []


def test_exclusion_3_block_quote(tmp_path: Path) -> None:
    """A published record is struck, never rewritten (R101b).

    Demanding an id inside a quoted verdict would be demanding an edit to
    someone else's words.
    """
    quoted = "".join(f"> {line}\n" for line in HELD.splitlines())
    assert _run(tmp_path, quoted) == []


def test_exclusion_4_heading(tmp_path: Path) -> None:
    """A title names a section; the claim lives in the paragraph under it."""
    assert _run(tmp_path, "## Work HELD on this pick\n") == []


def test_exclusion_5_the_status_line(tmp_path: Path) -> None:
    """`lint_review_status.py` owns the first line's shape.

    `_tree` writes one on every fixture packet, so this asserts the tool
    reads past it rather than treating the packet's own pointer as a hold.
    """
    root = _tree(tmp_path, HELD)
    packet = root / "review" / "active" / "packet-1.md"
    packet.write_text("Status: OPEN (staging waits on the pick)\n\n"
                      "Ordinary prose with nothing held in it.\n",
                      encoding="utf-8")
    files = [(packet.name, packet.read_text(encoding="utf-8"))]
    assert lint.findings(files, {"M69"}) == []


@pytest.mark.parametrize("sentence", lint.CLEAN)
def test_real_packet_prose_does_not_fire(tmp_path: Path, sentence: str) -> None:
    """Every near-miss is a real sentence from the tree on 2026-09-02.

    The word-list version of this lint matched 53 lines across the nine live
    packets and none of them was a hold on a pick: `every deck holds from turn
    one`, `SAME_NATION_REWARD_SHARE HOLDS AT 0.5`, `both rows read pending`,
    `Superconduct, Overloaded and Frozen`, `blocked on EB-188`.
    """
    assert _run(tmp_path, sentence) == []


@pytest.mark.parametrize("sentence", lint.CAUGHT)
def test_every_caught_shape_bites(tmp_path: Path, sentence: str) -> None:
    """The three spellings of the hazard the tool claims to catch."""
    assert _run(tmp_path, sentence), sentence


def test_a_table_header_cell_is_not_an_id() -> None:
    """`BACKLOG.md`'s header cell is the literal word `ID`.

    It satisfies the id pattern, so without dropping header rows any
    paragraph containing the word `ID` would discharge its own hold.
    """
    assert lint.backlog_ids(BACKLOG) == {"EB-188"}
    assert lint.queue_open_ids(QUEUE) == {"M69", "S4-G12", "CC-G1"}


def test_queue_status_is_read_off_the_first_word() -> None:
    """`OPEN -- mechanism ANSWERED (R231)` is an OPEN row.

    The live `S4-G6` row reads exactly that. A substring search for a
    closed-marker word anywhere in the status cell would close it.
    """
    table = ("| ID | Decision needed | Status | Provenance |\n"
             "|---|---|---|---|\n"
             "| `S4-G6` | **Ask:** declare the band "
             "| OPEN -- mechanism ANSWERED (R231), the band still owed "
             "| R231 |\n")
    assert lint.queue_open_ids(table) == {"S4-G6"}


def test_the_lint_self_test_passes() -> None:
    """The tool's own `--self-test`, which the CI lane never runs."""
    rc = subprocess.run(
        [sys.executable, "tools/lint_packet_holds.py", "--self-test"],
        cwd=REPO).returncode
    assert rc == 0


def test_the_real_tree_is_green() -> None:
    """`review/active/` holds nothing on an unminted pick today.

    This is the gate as CI runs it. A packet that grows an unregistered hold
    fails here, not only in the lint lane.
    """
    proc = subprocess.run(
        [sys.executable, "tools/lint_packet_holds.py"],
        cwd=REPO, capture_output=True, text=True,
        encoding="utf-8", errors="backslashreplace")
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_the_lint_is_registered_in_the_ci_lane() -> None:
    """A lint nobody runs is not a lint (`run_lints.py` registry-coverage)."""
    spec = importlib.util.spec_from_file_location(
        "run_lints", REPO / "tools" / "run_lints.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    rows = [r for r in module.REGISTRY
            if r.script == "tools/lint_packet_holds.py"]
    assert len(rows) == 1, rows
    assert rows[0].lane == "ci"
    assert module.registry_gaps() == []
