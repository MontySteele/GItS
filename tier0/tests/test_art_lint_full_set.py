"""`art_lint` runs against the WHOLE plan, in the suite. (C3, audit sec.3.7.)

The largest lint in the repo was wired into no validate rule and no test: it
ran only when somebody typed its name. The sprint log's L11 claim "verified by
negative test" referred to a test that did not exist in the repo.

This file is the first half of the fix (`validate.ps1` S10 is the other half),
and it is deliberately structured the way `test_sheet_lints.py` argues for:
the rule is exercised in BOTH directions, because a lint only ever seen
passing is not a gate.

**Bare-clone contract.** Every plan-driven check here needs `art/plan.tsv`,
and the L12 pixel check needs `ImageGen/images/cards/**` -- both Tier F and
gitignored. Where an input is genuinely absent the test skips with the reason
on record, as `test_char_stills` and `test_real_ironclad` do, rather than
asserting on an artifact nothing can regenerate (Track A's lesson). The
SYNTHETIC halves below run everywhere, which is what keeps the skip from
becoming a hole.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

import art_lint  # noqa: E402

PLAN = REPO / "art" / "plan.tsv"
SHIPPED = REPO / "ImageGen" / "images" / "cards"

needs_plan = pytest.mark.skipif(
    not PLAN.exists(),
    reason="art/plan.tsv is a Tier F ledger artifact; gitignored inputs absent")
# `is_dir()` is NOT the right predicate: an EMPTY ImageGen/images/cards is a
# real state on a bare clone, because tests that probe art coverage create the
# directory and remove only the files they wrote. That made this skipif read
# "art is present" and the tests below fail on a clone with no art at all.
# Presence of an actual PNG is what these need.
needs_art = pytest.mark.skipif(
    not (SHIPPED.is_dir() and any(SHIPPED.rglob("*.png"))),
    reason="ImageGen/images is gitignored Tier F; nothing shipped to hash")


def _rows():
    from art_fetch import read_plan
    return read_plan()


# --- the full-set run ----------------------------------------------------

@needs_plan
def test_the_whole_plan_lints_clean():
    """What the tool reports when run by hand, asserted in the suite."""
    problems = art_lint.lint(_rows())
    assert not problems, "\n".join(problems)


@needs_plan
def test_the_full_set_run_is_not_vacuous():
    """A lint that scans zero rows reports the same clean line as one that
    scans them all -- the sec.3.1/sec.3.7 dead-gate class, stated by R69's
    sibling test and applied here."""
    rows = _rows()
    effective = [r for r in rows
                 if "/cards/" in r["out"] and (r["pick"] == "auto"
                                               or r["rank"] == 1)]
    assert len(effective) > 100, (
        f"only {len(effective)} effective card rows; this gate is supposed to "
        "cover the whole roster")


# --- L12, the check that was dark ----------------------------------------

@needs_art
def test_l12_hashes_the_shipped_files_not_the_shortlist():
    """The three reasons L12 was off, asserted as one positive fact.

    It hashed `art/candidates/**` (gitignored, absent on a clean checkout, so
    it returned [] in silence), which is also the SHORTLIST -- auto-picks get
    no candidates directory, so a duplicate between two auto-picked cards was
    structurally invisible. Both are the same repair: hash what ships.
    """
    stems = {p.stem for p in SHIPPED.rglob("*.png")}
    assert len(stems) > 100, "shipped card art is suspiciously sparse"
    # The pair C3 found the moment this was pointed at the package. Both are
    # auto-picks, which is exactly why the old candidates hash could not see
    # them; it is allowlisted with its reason, not silently tolerated.
    assert frozenset({"kaboom", "spark_knight_style"}) in art_lint.KNOWN_IDENTICAL


@needs_art
def test_every_allowlisted_identical_pair_is_still_identical():
    """The rot direction. An entry that outlives its own defect is a hole.

    Each KNOWN_IDENTICAL pair is an admitted defect awaiting a re-pick or a
    ruling. When one is finally re-cropped, this fails and the entry has to
    be deleted -- which is how the allowlist stops growing monotonically.
    """
    digests: dict[str, str] = {}
    for p in SHIPPED.rglob("*.png"):
        digests[p.stem] = hashlib.sha256(p.read_bytes()).hexdigest()
    for pair in art_lint.KNOWN_IDENTICAL:
        present = [i for i in pair if i in digests]
        if len(present) < 2:
            continue          # not shipped yet; art_coverage owns that bill
        assert len({digests[i] for i in present}) == 1, (
            f"{sorted(pair)} are no longer pixel-identical -- the defect is "
            "fixed, so remove the KNOWN_IDENTICAL entry")


def test_l12_is_reachable_from_lint_not_only_from_main():
    """The third reason it was dark, and the one no data can demonstrate.

    `art_process` imports `lint()` and never called `identical_crops()`, so
    the tool that WRITES the crops did not pixel-check its own output. Pinned
    on the call graph because a green run proves nothing about which function
    did the checking.
    """
    import inspect
    src = inspect.getsource(art_lint.lint)
    assert "identical_crops()" in src, (
        "lint() must call identical_crops(); reachable only from main() is "
        "how this check spent its life switched off for every importer")


def test_l12_finds_a_duplicate_it_is_shown(tmp_path, monkeypatch):
    """The negative half, synthetic so it runs on a bare clone too.

    This is the direction the sprint log claimed was "verified by negative
    test" while no such test existed.
    """
    cards = tmp_path / "ImageGen" / "images" / "cards" / "klee"
    cards.mkdir(parents=True)
    blob = b"\x89PNG\r\n\x1a\n" + b"identical bytes"
    (cards / "probe_one.png").write_bytes(blob)
    (cards / "probe_two.png").write_bytes(blob)
    (cards / "probe_three.png").write_bytes(blob + b"different")

    monkeypatch.setattr(art_lint, "__file__", str(tmp_path / "tools" / "x.py"))
    problems = art_lint.identical_crops()
    assert len(problems) == 1, problems
    assert "probe_one" in problems[0] and "probe_two" in problems[0]
    assert "probe_three" not in problems[0]


def test_l12_is_silent_when_nothing_has_shipped(tmp_path, monkeypatch):
    """Absence is a no-op, and that is correct rather than lax.

    A bare clone has no `ImageGen/images` at all. "Did the art ship" is S9's
    question and art_coverage.py's; this rule only answers "do two shipped
    cards render the same pixels", and it must not manufacture an opinion
    about a package it cannot see.
    """
    monkeypatch.setattr(art_lint, "__file__", str(tmp_path / "tools" / "x.py"))
    assert art_lint.identical_crops() == []


def test_an_allowlisted_pair_is_reported_but_not_failed(tmp_path, monkeypatch,
                                                        capsys):
    """KNOWN_IDENTICAL suppresses the failure, never the visibility."""
    cards = tmp_path / "ImageGen" / "images" / "cards" / "klee"
    cards.mkdir(parents=True)
    blob = b"\x89PNG\r\n\x1a\n" + b"same"
    (cards / "kaboom.png").write_bytes(blob)
    (cards / "spark_knight_style.png").write_bytes(blob)

    monkeypatch.setattr(art_lint, "__file__", str(tmp_path / "tools" / "x.py"))
    assert art_lint.identical_crops() == []
    out = capsys.readouterr().out
    assert "KNOWN IDENTICAL (allowlisted)" in out
    assert "kaboom" in out
