"""EB-127: the row-id lint runs green AND can see the collision.

The sibling of `test_r_numbers_lint.py`, for the sibling namespace. The
R/D-series had a gate; the `M`-series in QUEUE and the `EB`-series in BACKLOG
had none, and two collisions reached review inside two weeks
(`EB-119`/`EB-120`, and `M38` minted twice off one base) — both caught by a
human, neither by the suite.

The lint carries its own `--self-test` (a uniqueness check that has never seen
a duplicate is indistinguishable from one that cannot see duplicates), and
this file both RUNS that self-test and asserts the real tree is clean with a
non-vacuous denominator. The two are not redundant: the self-test proves the
rules bite, this proves the tool is wired to the actual registers.

Since the manifest half landed, this file also guards the MANIFEST as a
committed artifact: that it is non-empty, that it is not silently derived from
the thing it checks, that its ceilings do not fork the series
`lint_r_numbers.py` already owns, and that it holds nothing but ids the
registers actually define. The rot rule is enforced by the lint itself, so
what is left for a test is the shape of the constants.

**And since 2026-09-02 the ceiling is DERIVED**, so the last section here is a
MERGE test in a hermetic repository: two branches that each mint a row must
merge with no conflict in this file at all, because neither of them touched it.
That is the property the redesign bought, and a property nothing else in the
suite could see — the old failure was a conflict, and a conflict is not a test
failure, it is a person's afternoon.
"""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "tools" / "lint_register_ids.py"

GIT_ID = ["-c", "user.name=Test", "-c", "user.email=test@example.invalid"]


def _module():
    spec = importlib.util.spec_from_file_location("lint_register_ids", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_committed_registers_are_clean():
    res = subprocess.run([sys.executable, str(TOOL)],
                         capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr


def test_the_sweep_is_not_vacuous():
    """A scan of zero rows is also 'no findings'. Assert it saw both
    registers and a real number of rows in each."""
    mod = _module()
    _, where = mod.findings()
    per = {rel: 0 for rel in mod.REGISTERS}
    for sites in where.values():
        for rel, _line in sites:
            per[rel] += 1
    for rel, count in per.items():
        assert count >= 5, f"{rel} contributed only {count} row id(s): {per}"
    # The two series the row was filed about are both present.
    assert any(cid.startswith("EB-") for cid in where), sorted(where)[:5]
    assert any(cid.startswith("M") and cid[1:].isdigit() for cid in where), \
        sorted(where)


def test_the_lints_own_self_test_passes():
    res = subprocess.run([sys.executable, str(TOOL), "--self-test"],
                         capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    assert "0 failure(s)" in res.stdout, res.stdout


def test_the_self_test_case_count_is_honest():
    """The printed denominator is a hand-kept number; a self-test that says
    eleven cases and runs three is the vacuum this file exists to prevent."""
    mod = _module()
    assert mod.SELF_TEST_CASES == 21
    assert mod.self_test() == []


def test_it_is_registered_in_the_ci_lane():
    """`run_lints.registry_gaps()` would fail the whole run on an unregistered
    lint; this asserts the lane it landed in, which that check cannot."""
    from tools import run_lints
    assert run_lints.registry_gaps() == []
    row = next(l for l in run_lints.REGISTRY if l.name == "register-ids")
    assert row.lane == "ci"
    assert row.script == "tools/lint_register_ids.py"


# --- the three rules, asserted here as well as in the tool -----------------

def test_a_duplicate_in_one_register_is_a_finding():
    mod = _module()
    q, b = mod.REGISTERS
    bad, _ = mod.findings({q: "| `M38` | one |\n| `M38` | two |", b: ""})
    assert any(f.startswith("DUPLICATE:") for f in bad), bad


def test_the_same_id_in_both_registers_is_a_finding():
    mod = _module()
    q, b = mod.REGISTERS
    bad, _ = mod.findings({q: "| `EB-9` | queue |", b: "| `EB-9` | backlog |"})
    assert any(f.startswith("CROSS-REGISTER:") for f in bad), bad


def test_a_citation_is_not_a_definition():
    """The scope line: citations elsewhere are fine and out of scope. A row
    whose PROSE names another row's id must not read as a second definition
    of it — that shape is on nearly every row in BACKLOG."""
    mod = _module()
    q, b = mod.REGISTERS
    bad, where = mod.findings(
        {q: "| `M14` | blocked on `EB-74`, see `EB-74` |",
         b: "| `EB-74` | staged; QUEUE `M14` owns the pull |"},
        ceilings={"EB": 74, "M": 14},
        open_ids={"EB": {74}, "M": {14}}, open_irregular=set())
    assert bad == [], bad
    assert sorted(where) == ["EB-74", "M14"], sorted(where)


# --- the manifest half: a retired id is not re-mintable --------------------

def test_a_retired_id_cannot_be_re_minted():
    """The failure EB-127 was filed about, and the one nothing else in the
    tree can see: EB-53's row closed and LEFT HEAD, so a branch re-taking 53
    collides with git history rather than with anything a lint can read."""
    mod = _module()
    q, b = mod.REGISTERS
    bad, _ = mod.findings({q: "", b: "| `EB-53` | re-taken |"},
                          ceilings={"EB": 137}, open_ids={"EB": set()},
                          open_irregular=set())
    assert any(f.startswith("RE-MINT:") and "EB-53" in f for f in bad), bad


def test_a_fresh_mint_needs_its_ceiling_bump_and_passes_with_it():
    mod = _module()
    q, b = mod.REGISTERS
    fresh = {q: "", b: "| `EB-138` | fresh |"}
    unbumped, _ = mod.findings(fresh, ceilings={"EB": 137},
                               open_ids={"EB": {138}}, open_irregular=set())
    assert any(f.startswith("UNRECORDED MINT:") for f in unbumped), unbumped
    bumped, _ = mod.findings(fresh, ceilings={"EB": 138},
                             open_ids={"EB": {138}}, open_irregular=set())
    assert bumped == [], bumped


def test_a_manifest_entry_that_outlived_its_row_is_a_finding():
    """The KNOWN_FAILING / CROSS_KNOWN rule, applied to ids: an entry that
    outlives its row rots into cover for the next branch that re-takes it."""
    mod = _module()
    q, b = mod.REGISTERS
    bad, _ = mod.findings({q: "", b: "| `EB-138` | fresh |"},
                          ceilings={"EB": 138}, open_ids={"EB": {99, 138}},
                          open_irregular=set())
    assert any(f.startswith("STALE MANIFEST ENTRY:") and "99" in f
               for f in bad), bad


def test_an_irregular_id_is_covered_by_the_explicit_set():
    """`S4-G*` carries no arithmetic, so the set IS the manifest — in both
    directions."""
    mod = _module()
    q, b = mod.REGISTERS
    bad, _ = mod.findings(
        {q: "| `S4-G6` | live |\n| `S4-G7` | re-taken |", b: ""},
        ceilings={}, open_ids={}, open_irregular={"S4-G6"})
    assert any(f.startswith("UNRECORDED ID:") and "S4-G7" in f
               for f in bad), bad
    stale, _ = mod.findings({q: "| `S4-G6` | live |", b: ""},
                            ceilings={}, open_ids={},
                            open_irregular={"S4-G6", "S4-G7"})
    assert any(f.startswith("STALE MANIFEST ENTRY:") and "S4-G7" in f
               for f in stale), stale


# --- the manifest as a committed artifact ----------------------------------

def test_the_manifest_is_not_derived_from_what_it_checks():
    """A ceiling recomputed from the live rows ALONE guards nothing: it would
    follow a closed row out of HEAD and re-offer its number. Since 2026-09-02
    the ceiling IS computed at runtime — from the rows PLUS `RETIRED`, which is
    the half no scan of the registers can produce. So no ceiling may sit BELOW
    the highest id still defining a row, and the manifest must record numbers
    the live scan cannot see.

    THE EVIDENCE OF THAT IS THE HOLES IN `OPEN_IDS`, NOT A CEILING GAP. This
    test used to demand that at least one ceiling sit STRICTLY above its
    series' top live row. That is a coincidence, not an invariant: it holds
    only while some series' highest number happens to have retired, and a
    perfectly legal mint at `ceiling + 1` in every series drives every gap to
    zero at once (M45, 2026-08-26, with EB already flush at 145). The durable
    statement is the one below — every series carries retired numbers at or
    below its ceiling whose rows have left HEAD, which `max(live)` wearing a
    different name could never produce."""
    mod = _module()
    _, where = mod.findings()
    top = {}
    for cid in where:
        series, num = mod.parse(cid)
        if series in mod.CEILINGS:
            top[series] = max(top.get(series, 0), num)
    assert set(top) == set(mod.CEILINGS), (top, sorted(mod.CEILINGS))
    for series, highest_live in top.items():
        assert mod.CEILINGS[series] >= highest_live, (series, top)
    for series, ceiling in mod.CEILINGS.items():
        retired = set(range(1, ceiling + 1)) - set(mod.OPEN_IDS.get(series, ()))
        assert retired, (series, ceiling, sorted(mod.OPEN_IDS.get(series, ())))


def test_the_manifest_does_not_fork_a_series_another_lint_owns():
    """Cheap consistency with `lint_r_numbers.py`: one namespace, one ceiling.
    R and D are its, and a register row must not define one of those numbers —
    it reads `## R<n>` headings and would never see a table cell."""
    mod = _module()
    from tools import lint_r_numbers
    assert set(mod.CEILINGS) & set(mod.FOREIGN_SERIES) == set()
    assert set(mod.FOREIGN_SERIES) == {"R", "D"}
    assert lint_r_numbers.R_CEILING and lint_r_numbers.D_CEILING
    q, b = mod.REGISTERS
    bad, _ = mod.findings({q: "", b: "| `R209` | a ruling as a row |"},
                          ceilings={}, open_ids={}, open_irregular=set())
    assert any(f.startswith("FOREIGN SERIES:") for f in bad), bad


def test_the_manifest_is_neither_empty_nor_a_blanket():
    """test_the_cross_sheet_allowlist_is_not_a_blanket, for ids. Every entry
    names a real id in a real series; an empty manifest would make every rule
    above vacuously true."""
    mod = _module()
    assert mod.CEILINGS, "no series has a ceiling -- rules 4 and 5 are dead"
    assert sum(len(v) for v in mod.OPEN_IDS.values()) >= 20, mod.OPEN_IDS
    assert len(mod.OPEN_IRREGULAR) >= 5, mod.OPEN_IRREGULAR
    assert set(mod.OPEN_IDS) <= set(mod.CEILINGS), sorted(mod.OPEN_IDS)
    for series, nums in mod.OPEN_IDS.items():
        assert all(isinstance(n, int) and n > 0 for n in nums), (series, nums)
        assert max(nums) <= mod.CEILINGS[series], (series, max(nums))
    for cid in mod.OPEN_IRREGULAR:
        assert mod.ID.match(cid), cid
        assert mod.parse(cid) == (None, None), (
            f"{cid} is an integer id and belongs under a CEILINGS series")


# --- the derived ceiling: two branches minting in parallel MERGE -----------

def _hermetic(tmp_path: Path) -> Path:
    """A git repo carrying the real lint, the real registers and the real
    minting tools, and nothing else.

    The REAL files, copied: a merge test against a synthetic lint would be a
    test of the synthetic lint. Each tool resolves its repo root from
    `__file__`, so a copy under `<tmp>/tools/` reads `<tmp>/docs/current/`.
    """
    root = tmp_path / "repo"
    (root / "tools").mkdir(parents=True)
    (root / "docs" / "current").mkdir(parents=True)
    for name in ("lint_register_ids.py", "lint_register_shape.py",
                 "register_io.py", "mint_row.py"):
        shutil.copyfile(REPO / "tools" / name, root / "tools" / name)
    for name in ("BACKLOG.md", "QUEUE.md"):
        shutil.copyfile(REPO / "docs" / "current" / name,
                        root / "docs" / "current" / name)
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
    subprocess.run(["git", *GIT_ID, "add", "tools", "docs"], cwd=root,
                   check=True)
    subprocess.run(["git", *GIT_ID, "commit", "-qm", "base"], cwd=root,
                   check=True)
    return root


def _mint(root: Path, section: str, register: str = "BACKLOG",
          **fields: str) -> subprocess.CompletedProcess:
    argv = [sys.executable, "tools/mint_row.py", register, section,
            "--provenance", "test", "--write"]
    if register == "BACKLOG":
        fields = {"scope": "a synthetic row.", "next-action": "none.",
                  "gate": "none.", "acceptance": "the test passes.", **fields}
    for key, value in fields.items():
        argv += [f"--{key}", value]
    return subprocess.run(argv, cwd=root, capture_output=True, text=True)


def _branch(root: Path, name: str, section: str, register: str = "BACKLOG",
            **fields: str) -> None:
    subprocess.run(["git", *GIT_ID, "checkout", "-q", "-b", name, "main"],
                   cwd=root, check=True)
    res = _mint(root, section, register, **fields)
    assert res.returncode == 0, res.stdout + res.stderr
    page = f"docs/current/{register}.md"
    subprocess.run(["git", *GIT_ID, "add", page], cwd=root, check=True)
    subprocess.run(["git", *GIT_ID, "commit", "-qm", f"mint on {name}"],
                   cwd=root, check=True)


def _merge(root: Path, into: str, other: str) -> subprocess.CompletedProcess:
    subprocess.run(["git", *GIT_ID, "checkout", "-q", into], cwd=root,
                   check=True)
    return subprocess.run(["git", *GIT_ID, "merge", "--no-edit", other],
                          cwd=root, capture_output=True, text=True)


def test_two_branches_each_minting_a_row_merge_with_no_conflict_in_the_lint(
        tmp_path):
    """THE PROPERTY THE DERIVED CEILING BOUGHT, and it lands green.

    Under the frozen literal, a branch minting an `EB` row bumped
    `CEILINGS["EB"]` and extended `OPEN_IDS["EB"]`, and a branch minting an `M`
    row did the same two things in the same dict — so two mints in one sitting
    met in the same file, and four such conflicts were resolved by hand on
    2026-09-02. Now NEITHER branch touches the file at all: the row is the
    record.
    """
    root = _hermetic(tmp_path)
    lint_before = (root / "tools" / "lint_register_ids.py").read_bytes()

    _branch(root, "a", "tools")                      # the next free EB
    _branch(root, "b", "5", register="QUEUE",        # the next free M
            decision="**CHOOSE** between (1) a and (2) b",
            status="OPEN -- gated on the test")

    # Neither commit touched the lint; each touched only its own register.
    for branch, page in (("a", "docs/current/BACKLOG.md"),
                         ("b", "docs/current/QUEUE.md")):
        changed = subprocess.run(
            ["git", "diff", "--name-only", "main", branch],
            cwd=root, capture_output=True, text=True).stdout.split()
        assert changed == [page], (branch, changed)

    merged = _merge(root, "a", "b")
    assert merged.returncode == 0, merged.stdout + merged.stderr
    assert "CONFLICT" not in (merged.stdout + merged.stderr)

    lint_after = (root / "tools" / "lint_register_ids.py").read_bytes()
    assert lint_after == lint_before, "the merge touched the lint file"
    assert b"<<<<<<<" not in lint_after

    checked = subprocess.run(
        [sys.executable, "tools/lint_register_ids.py"], cwd=root,
        capture_output=True, text=True)
    assert checked.returncode == 0, checked.stdout + checked.stderr


def test_when_both_branches_take_the_same_number_the_LINT_catches_it(tmp_path):
    """The hazard did not vanish, it MOVED — and this is where it lands.

    Two branches deriving "the next free number" in the SAME series off the
    same base both take it. Under the literal that was a merge conflict in
    this file; now the merge is clean, the file is untouched, and rule 1 fires
    on the merged tree naming both rows and both line numbers. That is the
    trade this design makes, and it is only a good trade if the finding is
    real, so: assert it.
    """
    root = _hermetic(tmp_path)
    lint_before = (root / "tools" / "lint_register_ids.py").read_bytes()
    _branch(root, "a", "tools")          # no --id: both derive the same one
    _branch(root, "b", "tests")

    merged = _merge(root, "a", "b")
    assert merged.returncode == 0, merged.stdout + merged.stderr
    assert (root / "tools" / "lint_register_ids.py").read_bytes() \
        == lint_before

    checked = subprocess.run(
        [sys.executable, "tools/lint_register_ids.py"], cwd=root,
        capture_output=True, text=True)
    assert checked.returncode == 1, checked.stdout
    assert "DUPLICATE:" in checked.stdout, checked.stdout


def test_a_close_that_records_no_retirement_leaves_a_hole_the_lint_finds(
        tmp_path):
    """Rule 5, on the real registers: delete a row, record nothing, fail.

    This is the successor to "an OPEN_IDS entry that outlived its row", and it
    is what keeps `RETIRED` from rotting: the retirement is recorded by the
    act of retiring, or the lint says so.
    """
    root = _hermetic(tmp_path)
    page = root / "docs" / "current" / "BACKLOG.md"
    module = _module()
    text = page.read_text(encoding="utf-8")
    lines = text.split("\n")
    # Drop one EB row that is NOT the highest (the ceiling must not move).
    #
    # THE VICTIM IS A ROW, NOT A STRING. Rows CITE each other -- `EB-327`'s
    # scope names `EB-266` in its own text -- so dropping every line
    # CONTAINING the id can delete two rows, which asserts nothing about the
    # rule under test and starts failing the day the register grows past a new
    # median. The DEFINING line is the one the row starts with, which is
    # exactly what `row_ids` reads.
    numbers = sorted(n for cid, _ in module.row_ids(text)
                     for s, n in [module.parse(cid)] if s == "EB")
    victim = numbers[len(numbers) // 2]
    defining = f"| `EB-{victim}` |"
    kept = [l for l in lines if not l.lstrip().startswith(defining)]
    assert len(kept) == len(lines) - 1, victim
    page.write_text("\n".join(kept), encoding="utf-8")

    checked = subprocess.run(
        [sys.executable, "tools/lint_register_ids.py"], cwd=root,
        capture_output=True, text=True)
    assert checked.returncode == 1, checked.stdout
    assert f"UNRECORDED RETIREMENT: EB-{victim}" in checked.stdout, \
        checked.stdout
