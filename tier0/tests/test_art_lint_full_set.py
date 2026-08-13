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

RAW = REPO / "art" / "raw"


def _has_pillow() -> bool:
    try:
        import PIL  # noqa: F401
        return True
    except ImportError:
        return False


# L8's staleness check has to actually MEASURE the sources, so it needs both a
# decoder and the gitignored raw files. Same contract as needs_plan: skip with
# the reason on record rather than assert on something absent.
needs_raw_images = pytest.mark.skipif(
    not (_has_pillow() and RAW.is_dir() and any(RAW.iterdir())),
    reason="L8 staleness needs Pillow and the gitignored art/raw sources")


def _rows():
    from art_fetch import read_plan
    return read_plan()


def _effective(rows):
    return [r for r in rows
            if "/cards/" in r["out"] and (r["pick"] == "auto"
                                          or r["rank"] == 1)]


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


# --- the three PENDING waiver sets, and their rot direction ---------------
#
# `KNOWN_IDENTICAL` already had `test_every_allowlisted_identical_pair_is_
# still_identical` above: an entry whose underlying defect is gone FAILS, so
# the allowlist can only shrink. `PENDING_UNDERSIZE` (L8), `PENDING_BANNED_
# FAMILY` (L9) and `PENDING_RED_PEN` (L1) had no such guard -- three
# hand-maintained sets that only printed and could only grow, each carrying a
# comment asking a future human to "DELETE the entry once resolved". The
# request in a comment is the failure mode; a test that breaks is the fix.
#
# All three are checked the same way, and it is the only honest way: EMPTY the
# waiver set and re-run the rule. An entry that no longer produces its finding
# with the suppression lifted is guarding nothing.
#
# Verified 2026-07-29 when these were written: all thirteen entries across the
# three sets still fire. Nothing was removed as stale.


@needs_plan
@needs_raw_images
def test_pending_undersize_entries_are_still_undersize(monkeypatch):
    """L8's waiver set, rot direction.

    Lift the suppression and each entry must still produce its own L8 line.
    It stops firing when the pick is re-hunted onto a big enough source, when
    the row leaves the plan, or when it is promoted to KNOWN_UNDERSIZED -- and
    every one of those is a reason the entry must come OUT, not linger.
    """
    entries = set(art_lint.PENDING_UNDERSIZE)      # snapshot before lifting
    monkeypatch.setattr(art_lint, "PENDING_UNDERSIZE", set())
    effective = _effective(_rows())
    problems = art_lint.undersized(effective)
    hit = {p.split()[1].rstrip(":") for p in problems}

    # A raw source that is absent cannot be measured, so it cannot prove
    # staleness either. Those entries are reported as UNVERIFIED rather than
    # silently counted as fine -- and if that is all of them the test has
    # measured nothing, which is the dead-gate class this file exists to name.
    from art_fetch import rawname
    by_id = {r["asset_id"]: r for r in effective}
    # An entry that is not an effective plan row at all is NOT unverifiable --
    # it is definitively stale (the row was retired or re-ranked), so it stays
    # in the checked set and fails below.
    unverified = {a for a in entries
                  if a in by_id
                  and not (RAW / rawname(by_id[a]["title"])).exists()}
    checkable = entries - unverified
    assert checkable, (
        f"no PENDING_UNDERSIZE entry could be measured (unverified: "
        f"{sorted(unverified)}); this gate would pass by scanning nothing")

    stale = sorted(checkable - hit)
    assert not stale, (
        "these PENDING_UNDERSIZE entries no longer produce an L8 finding -- "
        "the undersize is resolved (re-picked, row retired, or approved into "
        f"KNOWN_UNDERSIZED), so DELETE them from the set: {stale}"
        + (f" (unverified, raw source absent: {sorted(unverified)})"
           if unverified else ""))


@needs_plan
def test_pending_banned_family_entries_still_hit_a_ban(monkeypatch):
    """L9's waiver set, rot direction. Pure string work, so no decoder or raw
    file is needed -- this one runs wherever the plan does."""
    entries = set(art_lint.PENDING_BANNED_FAMILY)   # snapshot before lifting
    monkeypatch.setattr(art_lint, "PENDING_BANNED_FAMILY", set())
    problems = art_lint.banned_families(_effective(_rows()))
    hit = {p.split()[1].rstrip(":") for p in problems}
    stale = sorted(entries - hit)
    assert not stale, (
        "these PENDING_BANNED_FAMILY entries no longer draw from a banned "
        "family -- the pick was changed or the family was unbanned, so DELETE "
        f"them from the set: {stale}")


# --- L9's APPROVED exceptions (R151) --------------------------------------
#
# Not a PENDING set: these are resolved rulings, so they suppress permanently.
# They get the same rot guard anyway, plus the guard the PENDING sets do not
# need -- that the entry is ONE ENTRY and not a category.


def test_approved_family_exception_suppresses_only_its_exact_title(capsys):
    """L9 stands down for the approved title and for nothing else in its family.

    Synthetic rows, so this runs on a bare clone: the family ban must still
    fire on a sibling `Character Details` file, which is what "one entry, not
    a category" means mechanically.
    """
    base = {"out": "ImageGen/images/cards/kokomi/x.png", "pick": "auto",
            "rank": None, "register": "splash", "mode": "cover", "focus": "c",
            "source": "png", "frame": None, "w": 500, "h": 380,
            "source_group": None}
    approved = dict(base, asset_id="approved_rare",
                    title="Sangonomiya Kokomi Character Details 1.png")
    sibling = dict(base, asset_id="sibling_card",
                   title="Sangonomiya Kokomi Character Details 5.png")

    hit = {p.split()[1].rstrip(":")
           for p in art_lint.banned_families([approved, sibling])}
    assert hit == {"sibling_card"}, (
        "the exception must license exactly its own title; the rest of the "
        f"family stays banned (fired: {sorted(hit)})")
    assert "APPROVED EXCEPTION (L9, allowlisted)" in capsys.readouterr().out


def test_approved_family_exceptions_are_exact_titles_not_prefixes():
    """A prefix-shaped entry would re-open the family the L9 ban closed.

    Keys are compared with `_title_key`, which only folds case and the image
    extension -- so an entry must be a whole filename. The cheap structural
    proof: every key is normalised, is not itself a ban prefix, and records
    the ruling that granted it.
    """
    prefixes = {p.strip().lower() for p, _ in art_lint.BANNED_SOURCE_FAMILIES}
    for key, why in art_lint.APPROVED_FAMILY_EXCEPTIONS.items():
        assert key == art_lint._title_key(key), (
            f"exception key '{key}' is not normalised; write it lowercase "
            "and without the file extension")
        assert key not in prefixes, (
            f"exception key '{key}' IS a banned-family prefix -- that "
            "un-bans the whole category instead of naming one entry")
        assert why and why.strip(), (
            f"exception '{key}' records no approval; every entry must name "
            "the ruling that granted it")


def test_approved_family_exceptions_still_need_their_waiver():
    """Rot direction, same idiom as the PENDING sets but purely structural.

    An approved exception exists to cancel a banned-family finding. If its
    title no longer matches any ban prefix -- family unbanned, source renamed
    -- the entry suppresses nothing and must be DELETED so the lint keeps
    guarding the resolution rather than carrying a dead waiver.
    """
    prefixes = [p.lower() for p, _ in art_lint.BANNED_SOURCE_FAMILIES]
    stale = sorted(k for k in art_lint.APPROVED_FAMILY_EXCEPTIONS
                   if not any(k.startswith(p) for p in prefixes))
    assert not stale, (
        "these APPROVED_FAMILY_EXCEPTIONS no longer fall under any banned "
        "family, so they waive nothing -- DELETE them: " + repr(stale))


@needs_plan
def test_pending_red_pen_entries_are_still_colliding(monkeypatch):
    """L1's waiver set, rot direction.

    The precedent is in the set's own comment: {kaboom, spark_knight_style}
    was removed in Sweep II D1 BY HAND after the ruling retired one plan row,
    with the note that "leaving the entry would suppress a duplicate-source
    finding that can no longer occur". That removal was remembered. This makes
    the next one mandatory.
    """
    entries = set(art_lint.PENDING_RED_PEN)         # snapshot before lifting
    monkeypatch.setattr(art_lint, "PENDING_RED_PEN", set())
    problems = art_lint.lint(_rows())
    collisions = [p for p in problems if p.startswith("L1 ")]
    stale = []
    for pair in entries:
        if not any(all(a in msg for a in pair) for msg in collisions):
            stale.append(sorted(pair))
    assert not stale, (
        "these PENDING_RED_PEN pairs no longer share an effective source -- "
        "the collision they suppress can no longer occur, so DELETE them from "
        f"the set: {stale}")


# --- L10: an unreadable source is a finding, not a skip -------------------

def test_l10_reports_a_source_it_cannot_decode(tmp_path, monkeypatch):
    """The red demonstration for item 1.

    L8 and the L6 warn both `continue`d on any `Image.open` failure, so a
    truncated download or a saved HTML error page passed BOTH image checks in
    silence -- the single source neither rule could measure was the one they
    reported nothing about.
    """
    pytest.importorskip("PIL")
    raw = tmp_path / "art" / "raw"
    raw.mkdir(parents=True)
    (raw / "Bogus_Source.png").write_bytes(b"<html>404 Not Found</html>")
    monkeypatch.setattr(art_lint, "__file__", str(tmp_path / "tools" / "x.py"))

    row = {"asset_id": "probe_card", "title": "Bogus Source.png",
           "out": "ImageGen/images/cards/klee/probe_card.png", "pick": "auto",
           "rank": None, "register": "splash", "mode": "cover", "focus": "c",
           "source": "png", "frame": None, "w": 500, "h": 380,
           "source_group": None}
    problems = art_lint.undecodable([row])
    assert len(problems) == 1, problems
    assert problems[0].startswith("L10 probe_card:")
    assert "cannot be decoded" in problems[0]

    # ...and the finding reaches the gate, not just the helper.
    assert any(p.startswith("L10 probe_card:") for p in art_lint.lint([row]))


def test_l10_catches_a_truncated_file_whose_header_is_intact(tmp_path,
                                                             monkeypatch):
    """The fix-sweep-1 EB-7 residual, pinned.

    An HTML error page (above) fails at `Image.open` -- even a header-only
    probe caught that. A TRUNCATED download is the harder input: its header
    is fine, so `Image.open().size` succeeds and only a full pixel `load()`
    hits the missing tail. This is the input the header-only L10 provably
    passed; if the probe ever regresses to `.size`, this test goes red.
    """
    Image = pytest.importorskip("PIL.Image")
    raw = tmp_path / "art" / "raw"
    raw.mkdir(parents=True)
    intact = tmp_path / "intact.png"
    Image.new("RGBA", (800, 600), (200, 30, 30, 255)).save(intact, "PNG")
    data = intact.read_bytes()
    (raw / "Torn_Source.png").write_bytes(data[:int(len(data) * 0.6)])
    monkeypatch.setattr(art_lint, "__file__", str(tmp_path / "tools" / "x.py"))

    row = {"asset_id": "probe_card", "title": "Torn Source.png",
           "out": "ImageGen/images/cards/klee/probe_card.png", "pick": "auto",
           "rank": None, "register": "splash", "mode": "cover", "focus": "c",
           "source": "png", "frame": None, "w": 500, "h": 380,
           "source_group": None}
    # the premise: the header really is intact, so open() alone sees nothing
    with Image.open(raw / "Torn_Source.png") as img:
        assert img.size == (800, 600)
    problems = art_lint.undecodable([row])
    assert len(problems) == 1, problems
    assert problems[0].startswith("L10 probe_card:")


def test_l10_stays_silent_on_the_two_documented_skips(tmp_path, monkeypatch):
    """Absence of a decoder and absence of the raw file are facts about the
    MACHINE, not about the pick, and the plan must stay lintable under both.
    Only present-and-unopenable is a defect."""
    (tmp_path / "art" / "raw").mkdir(parents=True)
    monkeypatch.setattr(art_lint, "__file__", str(tmp_path / "tools" / "x.py"))
    row = {"asset_id": "probe_card", "title": "Never Fetched.png",
           "out": "ImageGen/images/cards/klee/probe_card.png", "pick": "auto",
           "rank": None, "register": "splash", "mode": "cover", "focus": "c",
           "source": "png", "frame": None, "w": 500, "h": 380,
           "source_group": None}
    assert art_lint.undecodable([row]) == []


def test_the_staleness_idiom_detects_an_entry_that_stopped_firing():
    """The synthetic red half of the three tests above, so the IDIOM is pinned
    on a bare clone where the plan-driven versions skip.

    Lifting a waiver and diffing "entries" against "ids that fired" is the
    whole mechanism; this shows it going red on a waiver whose defect is gone,
    using rows built here rather than the gitignored plan.
    """
    row = {"asset_id": "clean_card", "title": "Furina Portrait.png",
           "out": "ImageGen/images/cards/furina/clean_card.png",
           "pick": "auto", "rank": None, "register": "splash", "mode": "cover",
           "focus": "c", "source": "png", "frame": None, "w": 500, "h": 380,
           "source_group": None}
    banned = dict(row, asset_id="banned_card",
                  title="Test Run Fischl Banner.png")

    # L9 fires for the banned row and not for the clean one, so a waiver
    # naming the clean one is guarding nothing -- which is what the diff says.
    hit = {p.split()[1].rstrip(":")
           for p in art_lint.banned_families([row, banned])}
    assert hit == {"banned_card"}
    assert {"clean_card"} - hit == {"clean_card"}, (
        "the staleness diff must report a waived id that no longer fires")
    assert not {"banned_card"} - hit
