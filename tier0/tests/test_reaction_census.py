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
import threading

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


def _stale_copy(tmp_path, name="reaction-census-stale.md"):
    """A record that is exactly the committed one plus a marker, IN TEMP.

    `EB-772`. This used to be the committed record itself, tampered with in
    place and put back in a `finally`. That made a tracked file into shared
    mutable state for the length of a subprocess, and two fast lanes running
    at once raced over it: whichever lane's `--check` read the other lane's
    tampered bytes, and the tree was left modified whenever the loser restored
    last. The stale record is a COPY now, and nothing in this module writes
    inside the checkout at all.
    """
    copy = tmp_path / name
    copy.write_text(census.OUT.read_text(encoding="utf-8") + "\nSTALE MARKER\n",
                    encoding="utf-8")
    return copy


def _check(record=None):
    """`--check`, optionally against a copy. Returns the finished process."""
    argv = [sys.executable, "tools/reaction_census.py", "--check"]
    if record is not None:
        argv += ["--record", str(record)]
    return subprocess.run(argv, cwd=census.REPO, capture_output=True,
                          text=True)


def test_check_fails_when_the_record_is_stale(tmp_path):
    """A tampered record must be reported as stale, not silently accepted --
    `--check`'s entire job. Read off a temp copy (`EB-772`); the committed
    record is never written by this suite."""
    before = census.OUT.read_bytes()
    result = _check(_stale_copy(tmp_path))
    assert result.returncode != 0
    assert "STALE" in result.stdout
    assert census.OUT.read_bytes() == before, (
        "the tracked record must be untouched by the stale-record check")


def test_the_stale_check_survives_two_lanes_running_it_at_once(tmp_path):
    """`EB-772`, and it is `EB-730`'s pin one test over.

    THE FAILURE, FOUR TIMES ON 2026-09-16 AND ONLY EVER WITH A SECOND LANE UP:
    the old test wrote its stale marker into the TRACKED record, ran a
    subprocess, and restored it. Two full fast lanes each did that, so one
    lane's `--check` read bytes the other lane had staged (or had already put
    back, which reads as OK where STALE was asserted), and the loser's restore
    left `review/records/reaction-census-2026-09-05.md` modified in the tree.

    THE OVERLAP IS COMMANDED, NOT TIMED, which is `_CommandedReads`' rule in
    `test_local_tester`: a BARRIER holds both checks until both are genuinely
    in flight, so this asserts about a real concurrency rather than hoping two
    sleeps interleave. What it then asserts is the property the repair buys --
    each lane reads ITS OWN copy, both see STALE, and the tracked record is
    byte-identical afterwards.
    """
    before = census.OUT.read_bytes()
    copies = [_stale_copy(tmp_path, f"stale-{lane}.md") for lane in "ab"]
    gate = threading.Barrier(len(copies), timeout=120.0)
    results: dict[int, subprocess.CompletedProcess] = {}

    def lane(index):
        gate.wait()
        results[index] = _check(copies[index])

    threads = [threading.Thread(target=lane, args=(i,))
               for i in range(len(copies))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=300.0)
        assert not thread.is_alive(), "a lane never finished"

    assert len(results) == len(copies)
    for index, result in results.items():
        assert result.returncode != 0, (
            f"lane {index}: stdout={result.stdout!r} "
            f"stderr={result.stderr!r}")
        assert "STALE" in result.stdout
    assert census.OUT.read_bytes() == before


def test_committed_record_names_its_inputs():
    """The census is pinned to the record files it was written over, so a
    seat record landing after it does not turn the committed table stale."""
    listed = census.listed_inputs(census.OUT.read_text(encoding="utf-8"))
    assert listed, "the committed census carries no inputs footer"
    assert all((census.REPO / p).is_file() for p in listed)


def test_discovery_restricted_to_listed_inputs():
    """`--check` reads exactly the files the record names: restricting
    discovery to a two-file subset returns those two and nothing else."""
    listed = census.listed_inputs(census.OUT.read_text(encoding="utf-8"))
    subset = set(listed[:2])
    found = census.discover_records(subset)
    assert {r[3].relative_to(census.REPO).as_posix() for r in found} == subset
