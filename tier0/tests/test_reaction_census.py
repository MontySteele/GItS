"""Regression tests for the reaction census (`tools/reaction_census.py`).

Two things are worth pinning: the classifier's three-way split (a sentence
that reads as a decision, one that reads as a number found afterwards, and
one that is neither -- a rule quote, most often) on hand-written sentences
chosen to each hit exactly one bucket; and that `--check` actually verifies
the committed record against the seat files on disk, rather than always
passing. Nothing here re-derives the corpus counts -- those live only in
`review/records/reaction-census-2026-09-05.md` and are read from disk by the
same script that wrote them.
"""

import subprocess
import sys

from tools import reaction_census as census


def test_decision_sentence_reads_as_decision():
    """"Preview" is a decision-word: the seat is reporting that the card told
    them the reaction before they committed to the play."""
    sentence = ("Ka-pow! printed a Reaction preview: Melt, so I chose to "
                "play Rosaria first instead of last.")
    assert census.reading_of(sentence) == "decision"


def test_found_afterwards_sentence_reads_as_found():
    """No decision-word appears; the seat is doing arithmetic to explain a
    number that showed up on the HP total, after the fact."""
    sentence = ("The Superconduct damage was unexplained until I did the "
                "arithmetic: 12 where 7 was printed.")
    assert census.reading_of(sentence) == "found-afterwards"


def test_rule_quote_sentence_is_unmarked_not_forced_into_a_bucket():
    """A keyword-box definition names the reaction without any signal that
    the seat weighed a choice or worked out a discrepancy -- the census must
    not force it into either read."""
    sentence = ('The glossary printed "Vaporize -- the triggering hit deals '
                '1.5x damage and consumes the aura."')
    assert census.reading_of(sentence) == "unmarked"


def test_check_passes_on_the_committed_record():
    """The record on disk must be exactly what the script would write today.
    If a seat record changes and nobody re-runs the script, this is the test
    that catches it."""
    result = subprocess.run(
        [sys.executable, "tools/reaction_census.py", "--check"],
        cwd=census.REPO, capture_output=True, text=True)
    assert result.returncode == 0, (
        f"stdout={result.stdout!r} stderr={result.stderr!r}")


def test_check_fails_when_the_record_is_stale(tmp_path, monkeypatch):
    """A tampered committed file must be reported as stale, not silently
    accepted -- `--check`'s entire job."""
    stale = census.OUT.read_text(encoding="utf-8") + "\nSTALE MARKER\n"
    backup = census.OUT.read_text(encoding="utf-8")
    census.OUT.write_text(stale, encoding="utf-8")
    try:
        result = subprocess.run(
            [sys.executable, "tools/reaction_census.py", "--check"],
            cwd=census.REPO, capture_output=True, text=True)
        assert result.returncode != 0
        assert "STALE" in result.stdout
    finally:
        census.OUT.write_text(backup, encoding="utf-8")
