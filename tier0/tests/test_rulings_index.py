"""The rulings index resolves what it claims to, and its gate can see defects.

Two things are pinned here, and they fail for different reasons.

THE REAL TREE. `docs/current/RULINGS.md` is current, covers every cited
R-number, and is byte-identical to what the generator produces. If this goes
red the fix is one command (`python -m tools.gen_rulings_index`), and the red
is the point: a ruling landed and the index did not catch up.

A FIXTURE REPO. Everything else runs against a throwaway git repo built in
`tmp_path` with a known ledger, known ruling commits, and known citations --
so the source-precedence rules, the unresolved fallback, the omission rule and
the no-history degradation are asserted on inputs whose right answer is known,
rather than on 210 rows of real history that will keep changing.

The degradation case is not decoration. CI checks out depth-1 with no tags, so
the generator's git reads ALL fail there; the contract is that it produces a
valid file of unresolved rows instead of raising, and that the lint declines
to run its staleness half rather than diffing against that file.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
GEN = REPO / "tools" / "gen_rulings_index.py"
LINT = REPO / "tools" / "lint_rulings_index.py"
INDEX = REPO / "docs" / "current" / "RULINGS.md"


def _module(name: str, path: Path):
    """A private copy of the tool, so a test's monkeypatching cannot leak."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# --- the fixture repo --------------------------------------------------------

LEDGER = """\
# Fixture ledger

## Current-law digest (GENERATED -- do not hand-edit)

- **R2** (2026-01-02) — the digest line wins over everything else — `OPERATIVE`

## A dated section (2026-01-01, some plan.md)

7. **R4 — a bold definition** whose sentence wraps onto
   a second line and keeps going.
8. **R5 + R6 + a shared disposition**: two ids, one entry.
- **R7/R9–R10:** a grouped entry covering a range.

## R3 -- a headed entry (2026-01-03)

Body prose that is not part of the title.
"""


def _git(cwd: Path, *args: str, **kw) -> subprocess.CompletedProcess:
    # gpgsign off and a fixed identity: the fixture must not reach for the
    # developer's signing key, and must commit the same way on a CI runner
    # that has no user configured at all.
    base = ["git", "-c", "commit.gpgsign=false",
            "-c", "user.name=Fixture", "-c", "user.email=fixture@example.com"]
    return subprocess.run(base + list(args), cwd=cwd, capture_output=True,
                          text=True, encoding="utf-8", errors="replace", **kw)


def _commit(root: Path, subject: str, body: str = "") -> None:
    _git(root, "add", "-A")
    message = subject if not body else f"{subject}\n\n{body}"
    res = _git(root, "commit", "-q", "--allow-empty", "-m", message)
    assert res.returncode == 0, res.stdout + res.stderr


@pytest.fixture
def fixture_repo(tmp_path: Path) -> Path:
    """A repo whose whole ruling history is known by construction."""
    root = tmp_path / "repo"
    (root / "docs" / "current").mkdir(parents=True)
    assert _git(tmp_path, "init", "-q", str(root)).returncode == 0

    (root / "LEDGER.md").write_text(LEDGER, encoding="utf-8")
    _commit(root, "The ledger lands")
    _git(root, "tag", "fixture-ledger")
    (root / "LEDGER.md").unlink()
    _commit(root, "Retire the ledger")

    # R11: subject LEADS with the id -- the house convention for a ruling.
    _commit(root, "R11: the leading subject is the summary")
    # R12 is only NAMED by a subject that leads with another id.
    _commit(root, "R13: a ruling that also discharges R12")
    # R14/R15 recorded as body paragraphs under one sitting subject.
    _commit(root, "The sitting lands: R14-R15 across the registers",
            "Recording pass only; every ruling below is [USER]'s.\n\n"
            "R14 the fourteenth ruling, recorded as its own paragraph.\n\n"
            "R15 the fifteenth ruling, likewise.\n")
    return root


def _configured(root: Path):
    """The generator, pointed at the fixture repo instead of the real one."""
    mod = _module("gen_fixture", GEN)
    mod.REPO = root
    mod.DOCS = root / "docs" / "current"
    mod.OUT = mod.DOCS / "RULINGS.md"
    mod.LEDGER_REVS = ("fixture-ledger",)
    mod.LEDGER_PATHS = ("LEDGER.md",)
    mod.R_CEILING = 16
    return mod


def _rows(text: str) -> dict[str, tuple[str, str, str]]:
    out: dict[str, tuple[str, str, str]] = {}
    for line in text.splitlines():
        if not line.startswith("| R"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        out[cells[0]] = (cells[1], cells[2], cells[3])
    return out


def _cite(root: Path, text: str) -> None:
    (root / "docs" / "current" / "PAGE.md").write_text(text, encoding="utf-8")


# --- the real tree -----------------------------------------------------------

def test_the_committed_index_passes_its_own_gate():
    res = subprocess.run([sys.executable, str(LINT)],
                         capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    assert res.returncode == 0, res.stdout + res.stderr
    assert "rulings-index OK" in res.stdout


def test_the_committed_index_is_what_the_generator_produces():
    gen = _module("gen_real", GEN)
    lint = _module("lint_real", LINT)
    fresh, stats = gen.render()
    if not stats["history"]:
        pytest.skip("no retired ledgers in this clone -- nothing to compare")
    assert lint.normalise(fresh) == lint.normalise(
        INDEX.read_text(encoding="utf-8")), (
        "docs/current/RULINGS.md is stale; "
        "run `python -m tools.gen_rulings_index`")


def test_the_generator_writes_lf(tmp_path):
    """The blob is LF, so a Linux checkout and this file agree byte for byte.

    The WORKING COPY is a different question: `core.autocrlf=true` hands
    Windows a CRLF checkout of the same blob, which is why the gate compares
    normalised text rather than bytes.
    """
    gen = _module("gen_lf", GEN)
    out = tmp_path / "RULINGS.md"
    assert gen.main(["--out", str(out)]) == 0
    assert b"\r" not in out.read_bytes()


def test_a_crlf_working_copy_is_not_stale(fixture_repo):
    gen = _configured(fixture_repo)
    _cite(fixture_repo, "See R2.\n")
    gen.main([])
    gen.OUT.write_bytes(
        gen.OUT.read_text(encoding="utf-8").replace("\n", "\r\n")
        .encode("utf-8"))
    assert _lint_for(fixture_repo, gen).main([]) == 0


def test_generation_is_idempotent():
    mod = _module("gen_idem", GEN)
    first, _ = mod.render()
    second, _ = mod.render()
    assert first == second


def test_every_real_row_is_within_the_frozen_ceiling():
    """The index must not mint a number `lint_r_numbers` would refuse."""
    mod = _module("gen_ceiling", GEN)
    ids = [int(r[1:]) for r in _rows(INDEX.read_text(encoding="utf-8"))]
    assert ids == sorted(ids), "rows are not in id order"
    assert max(ids) <= mod.R_CEILING


# --- source precedence, over known history -----------------------------------

def test_the_digest_line_beats_the_commit(fixture_repo):
    mod = _configured(fixture_repo)
    _cite(fixture_repo, "See R2.\n")
    rows = _rows(mod.render()[0])
    assert rows["R2"][0] == "2026-01-02"
    assert rows["R2"][1] == "the digest line wins over everything else"


def test_a_ledger_heading_carries_its_title_and_date(fixture_repo):
    mod = _configured(fixture_repo)
    _cite(fixture_repo, "See R3.\n")
    rows = _rows(mod.render()[0])
    date, text, rev = rows["R3"]
    assert (date, text) == ("2026-01-03", "a headed entry")
    assert rev.startswith("`") and len(rev.strip("`")) == mod.ABBREV


def test_a_bold_definition_wraps_and_inherits_its_section_date(fixture_repo):
    """Pre-R39 entries were never headed; the section heading is their date."""
    mod = _configured(fixture_repo)
    _cite(fixture_repo, "See R4.\n")
    rows = _rows(mod.render()[0])
    date, text, _rev = rows["R4"]
    assert date == "2026-01-01"
    assert text.startswith("a bold definition whose sentence wraps")
    assert "\n" not in text and "  " not in text


def test_one_bold_entry_can_define_several_ids(fixture_repo):
    mod = _configured(fixture_repo)
    _cite(fixture_repo, "See R5, R6, R7, R9, R10.\n")
    rows = _rows(mod.render()[0])
    assert rows["R5"][1] == rows["R6"][1] == "a shared disposition: two ids, one entry."
    # `R7/R9-R10` is a range: R8 is NOT in it and must not be invented.
    grouped = "a grouped entry covering a range."
    assert rows["R7"][1] == rows["R9"][1] == rows["R10"][1] == grouped
    assert "R8" not in rows


def test_a_leading_subject_resolves_a_post_ledger_ruling(fixture_repo):
    mod = _configured(fixture_repo)
    _cite(fixture_repo, "See R11.\n")
    rows = _rows(mod.render()[0])
    assert rows["R11"][1] == "the leading subject is the summary"
    assert rows["R11"][0] == mod.commits()[0].date


def test_a_body_paragraph_headed_by_the_id_beats_the_range_subject(fixture_repo):
    """The sitting-commit shape: one subject over many rulings, one paragraph
    each. The paragraph is what says something about R14."""
    mod = _configured(fixture_repo)
    _cite(fixture_repo, "See R14 and R15.\n")
    rows = _rows(mod.render()[0])
    assert rows["R14"][1] == "the fourteenth ruling, recorded as its own paragraph."
    assert rows["R15"][1] == "the fifteenth ruling, likewise."


def test_a_draft_slate_commit_yields_to_the_landing(fixture_repo):
    """R212 has Claude commit a slate BEFORE [USER] rules it, subjected
    "R<n> DRAFT slate: ...". That subject leads with the id and is earlier
    than the landing by construction, so without a rule the index would send
    a reader to the proposal. A DRAFT subject is demoted to NEARBY: it loses
    to the landing, and still resolves an id nothing else records."""
    mod = _configured(fixture_repo)
    _commit(fixture_repo, "R16 DRAFT slate: the proposal, four picks")
    _commit(fixture_repo, "R16 landed: the sixteenth ruling, as ruled")
    _cite(fixture_repo, "See R16.\n")
    rows = _rows(mod.render()[0])
    assert "DRAFT" not in rows["R16"][1]
    assert "the sixteenth ruling, as ruled" in rows["R16"][1]
    assert rows["R16"][2].strip("`") == mod.commits()[0].short


def test_a_draft_alone_still_resolves_its_id(fixture_repo):
    mod = _configured(fixture_repo)
    _commit(fixture_repo, "R16 DRAFT slate: the proposal, four picks")
    _cite(fixture_repo, "See R16.\n")
    rows = _rows(mod.render()[0])
    assert rows["R16"][1] != mod.UNRESOLVED
    assert "DRAFT" in rows["R16"][1]


def test_an_id_with_no_definition_gets_the_unresolved_row(fixture_repo):
    mod = _configured(fixture_repo)
    _cite(fixture_repo, "See R16, which nothing ever defined.\n")
    text, stats = mod.render()
    rows = _rows(text)
    assert rows["R16"] == (mod.NONE, mod.UNRESOLVED, mod.NONE)
    assert "pre-simplification-2026-08-06" in mod.UNRESOLVED
    assert stats["unresolved"] == 1


def test_an_id_neither_cited_nor_defined_is_omitted_and_counted(fixture_repo):
    mod = _configured(fixture_repo)
    _cite(fixture_repo, "See R2.\n")
    text, stats = mod.render()
    rows = _rows(text)
    assert "R1" not in rows and "R8" not in rows and "R16" not in rows
    assert stats["omitted"] >= 3
    assert f"{stats['omitted']} id(s) omitted" in text


def test_a_cited_id_always_gets_a_row(fixture_repo):
    mod = _configured(fixture_repo)
    _cite(fixture_repo, "R1 R2 R3 R4 R5 R6 R7 R9 R10 R11 R12 R13 R14 R15 R16\n")
    rows = _rows(mod.render()[0])
    assert set(rows) == {f"R{n}" for n in range(1, 17)} - {"R8"}


def test_the_generated_file_does_not_index_itself(fixture_repo):
    """RULINGS.md cites every number it lists; scanning it would make the
    coverage check circular and the omission count meaningless."""
    mod = _configured(fixture_repo)
    _cite(fixture_repo, "See R2.\n")
    mod.OUT.write_text("| R16 | x | y | z |\n", encoding="utf-8")
    rows = _rows(mod.render()[0])
    assert "R16" not in rows


# --- degradation --------------------------------------------------------------

def test_no_history_degrades_instead_of_raising(tmp_path):
    """The depth-1 CI checkout: no ledgers, no ruling commits, no crash."""
    root = tmp_path / "bare"
    (root / "docs" / "current").mkdir(parents=True)
    (root / "docs" / "current" / "LAW.md").write_text(
        "Held under R2 and R99.\n", encoding="utf-8")
    mod = _module("gen_bare", GEN)
    mod.REPO = root                      # not a git repo at all
    mod.DOCS = root / "docs" / "current"
    mod.OUT = mod.DOCS / "RULINGS.md"
    mod.R_CEILING = 100

    text, stats = mod.render()
    assert stats["history"] is False
    assert stats["unresolved"] == 2
    rows = _rows(text)
    assert rows["R2"] == (mod.NONE, mod.UNRESOLVED, mod.NONE)
    assert rows["R99"] == (mod.NONE, mod.UNRESOLVED, mod.NONE)
    assert "UNAVAILABLE" in text
    assert mod.main(["--out", str(mod.OUT)]) == 0
    assert mod.OUT.read_text(encoding="utf-8") == text


def test_git_absent_is_not_a_crash(monkeypatch):
    mod = _module("gen_nogit", GEN)
    monkeypatch.setattr(mod.subprocess, "run",
                        lambda *a, **k: (_ for _ in ()).throw(OSError("nope")))
    assert mod.run("log") == (127, "")
    assert mod.commits() == []
    assert mod.ledger_entries() == ({}, None)


# --- text hygiene -------------------------------------------------------------

def test_a_summary_never_exceeds_the_cell_budget():
    mod = _module("gen_clip", GEN)
    long = "word " * 200
    assert len(mod.clip(long)) <= mod.MAXLEN
    assert mod.clip(long).endswith("…")
    # A sentence end inside the budget is preferred to a mid-word cut.
    sentence = "A first sentence long enough to stand on its own. " + "tail " * 100
    assert mod.clip(sentence) == "A first sentence long enough to stand on its own."
    # ... but not a two-word one: an id-and-colon opener says nothing, so the
    # budget is spent on prose instead.
    assert mod.clip("M9. " + "tail " * 100).startswith("M9. tail")


def test_a_pipe_in_the_source_cannot_break_the_table():
    mod = _module("gen_pipe", GEN)
    assert mod.summarise("**R5 - a | b | c**") == r"a \| b \| c"


def test_the_leading_id_run_is_stripped_from_the_summary():
    mod = _module("gen_lead", GEN)
    assert mod.summarise("74. **R21 + R22 + the disposition**: body") == \
        "the disposition: body"
    assert mod.summarise("- **R9/R12–R15:** grouped") == "grouped"


def test_leading_ids_expands_a_range_but_not_a_wild_one():
    mod = _module("gen_ids", GEN)
    assert mod.leading_ids(9, "/R12–R15:**") == [9, 12, 13, 14, 15]
    assert mod.leading_ids(21, " + R22 + more") == [21, 22]
    assert mod.leading_ids(1, "–R900: everything") == [1]
    assert mod.leading_ids(34, " executed (X-cost):") == [34]


# --- the lint ------------------------------------------------------------------

def _lint_for(root: Path, gen):
    mod = _module("lint_fixture", LINT)
    mod.REPO = root
    mod.OUT = gen.OUT
    mod.R_CEILING = gen.R_CEILING
    mod.pages = gen.pages
    mod.render = gen.render
    return mod


def test_the_lint_passes_on_a_freshly_generated_index(fixture_repo, capsys):
    gen = _configured(fixture_repo)
    _cite(fixture_repo, "See R2 and R11.\n")
    gen.main([])
    assert _lint_for(fixture_repo, gen).main([]) == 0


def test_a_citation_with_no_row_is_a_finding(fixture_repo, capsys):
    """The realistic failure: a number is cited before the index catches up.

    R16 is the right probe because nothing defines it -- an id that some
    commit defines already has a row whether or not anyone cites it, so only
    an undefined citation can open a coverage hole.
    """
    gen = _configured(fixture_repo)
    _cite(fixture_repo, "See R2.\n")
    gen.main([])
    _cite(fixture_repo, "See R2 and now R16 as well.\n")
    lint = _lint_for(fixture_repo, gen)
    assert lint.main([]) == 1
    out = capsys.readouterr().out
    assert "R16" in out and "no row" in out
    assert "docs/current/PAGE.md" in out


def test_a_hand_edited_index_is_a_finding(fixture_repo, capsys):
    gen = _configured(fixture_repo)
    _cite(fixture_repo, "See R2.\n")
    gen.main([])
    gen.OUT.write_text(
        gen.OUT.read_text(encoding="utf-8").replace("digest line", "DIGEST"),
        encoding="utf-8")
    lint = _lint_for(fixture_repo, gen)
    assert lint.main([]) == 1
    assert "stale" in capsys.readouterr().out


def test_a_missing_index_is_a_finding(fixture_repo, capsys):
    gen = _configured(fixture_repo)
    _cite(fixture_repo, "See R2.\n")
    lint = _lint_for(fixture_repo, gen)
    assert lint.main([]) == 1
    assert "missing" in capsys.readouterr().out


def test_staleness_is_skipped_when_the_clone_has_no_history(fixture_repo,
                                                            capsys):
    """The CI contract: coverage still bites, staleness declines to answer."""
    gen = _configured(fixture_repo)
    _cite(fixture_repo, "See R2.\n")
    gen.main([])
    gen.LEDGER_REVS = ("no-such-rev",)          # simulate the depth-1 checkout
    gen.commits = lambda: []
    lint = _lint_for(fixture_repo, gen)
    assert lint.main([]) == 0
    out = capsys.readouterr().out
    assert "staleness SKIPPED" in out


def test_the_lint_is_registered_in_the_ci_lane():
    """A lint no runner names is a lint nobody runs -- run_lints fails the
    whole battery on an unregistered tools/lint_*.py, and this pins the LANE
    as well, which that check cannot see."""
    reg = _module("run_lints_reg", REPO / "tools" / "run_lints.py")
    rows = [l for l in reg.REGISTRY
            if l.script == "tools/lint_rulings_index.py"]
    assert len(rows) == 1, "rulings-index is not in the registry exactly once"
    assert rows[0].lane == "ci"
    assert not reg.registry_gaps()
