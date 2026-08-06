"""Every `docs/` path a tool cites must resolve (docs diet, Track Z / Z-4).

WHY THIS EXISTS
---------------
Z-4's finding was that four `tools/` modules cite `docs/track-a-kickoff-brief.md`
in their module docstrings, and that this is exactly why the 2026-08-06 archive
review declined to archive it: moving a document makes live citations stale to
fix one index row.

The diet's answer was to freeze rather than move -- REFERENCE documents stay at
their path -- and this test is that answer made mechanical. It is not a style
check. It fails the moment a paper pass moves or renames a document that a tool
reads or names, which is the only way that class of breakage has ever happened
here.

Deliberately narrow: it checks *existence*, never content. A tool may cite a
frozen document; it may not cite a missing one.

WHAT R121 `Q20` ADDED (2026-08-06)
----------------------------------
Freeze-over-move was only ever the answer for *live* citers. A citation inside
an append-only DECISIONS volume can never be repointed at all (rail 1), so the
45 files a ledger cites by path were unmovable -- until `Q20` ruled
MOVE-WITH-RESOLVER: move the file, leave the ledger byte alone, and record the
redirect in `docs/registry/identifiers.md` section 17.

The tests below pin that mechanism in both directions, because a resolver
asserted only in the green direction rots into a no-op: the real lint
(`tools/lint_doc_citations.py`) must go GREEN on a stale path that resolves,
and RED on one that does not.
"""

from __future__ import annotations

import importlib.util
import pathlib
import re
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
TOOLS = REPO_ROOT / "tools"
CITATION_LINT = TOOLS / "lint_doc_citations.py"

DOC_PATH = re.compile(r"docs/[A-Za-z0-9_./-]+\.(?:md|yaml|tsv|json|txt)")


def _cited() -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for path in sorted(TOOLS.rglob("*.py")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for m in DOC_PATH.finditer(text):
            out.setdefault(m.group(0), set()).add(path.relative_to(REPO_ROOT).as_posix())
    return out


def _lint_module():
    spec = importlib.util.spec_from_file_location("lint_doc_citations", CITATION_LINT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_every_docs_path_cited_from_tools_exists():
    resolver = _lint_module().load_resolver()
    missing = {
        target: sorted(who)
        for target, who in _cited().items()
        if not (REPO_ROOT / target).exists() and target not in resolver
    }
    assert not missing, (
        "tools/ cite docs/ paths that do not exist and that no resolver row "
        "(identifiers.md section 17) redirects -- a paper pass moved or "
        f"renamed a citation target: {missing}"
    )


def test_the_flagged_case_is_still_pinned():
    """`track-a-kickoff-brief.md` is the case the archive review called out by
    name. If a future sweep archives it, four tools go stale; this asserts the
    citation set is real so the failure is loud rather than silent."""
    cited = _cited()
    brief = "docs/track-a-kickoff-brief.md"
    assert brief in cited, "the flagged citation disappeared -- re-read Z-4 before deleting this test"
    assert len(cited[brief]) >= 4, cited[brief]
    assert (REPO_ROOT / brief).exists()


# --- R121 `Q20`: the resolver, pinned in both directions ---------------------


def _run_lint(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CITATION_LINT), *args],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )


def test_resolver_lint_runs_green_and_actually_resolved_something():
    """Green, and green for the right reason.

    A resolver with zero rows, or a sweep that found zero stale paths, would
    also print OK -- and would be a no-op. Both are asserted away.
    """
    res = _run_lint("--all")
    assert res.returncode == 0, res.stdout + res.stderr
    resolver = _lint_module().load_resolver()
    assert len(resolver) >= 45, f"resolver table shrank to {len(resolver)} rows"
    m = re.search(r"(\d+) stale path\(s\) resolved", res.stdout)
    assert m and int(m.group(1)) > 0, res.stdout


def test_every_resolver_row_points_at_a_real_file():
    resolver = _lint_module().load_resolver()
    dead = {old: new for old, new in resolver.items() if not (REPO_ROOT / new).exists()}
    assert not dead, f"resolver rows that resolve to nothing: {dead}"


def test_the_ledgers_cite_stale_paths_on_purpose_and_the_table_covers_them():
    """The premise of `Q20`: ledger bytes are never rewritten, so the ledgers DO
    carry stale paths. If that stops being true the resolver is dead weight and
    someone has edited a frozen record -- which is the rail-1 violation."""
    mod = _lint_module()
    cited = mod.cited_paths(list(mod.LEDGERS))
    stale = [t for t in cited if not (REPO_ROOT / t).exists()]
    assert stale, "no ledger citation is stale -- did a pass rewrite a ledger?"
    resolver = mod.load_resolver()
    assert all(t in resolver for t in stale), sorted(t for t in stale if t not in resolver)


def test_a_stale_path_with_no_resolver_row_is_red():
    """The red direction, run against a fabricated frozen record."""
    mod = _lint_module()
    probe = REPO_ROOT / "tier0" / "_q20_lint_probe.md"
    probe.write_text("cites docs/no-such-file-q20-probe.md\n", encoding="utf-8")
    try:
        mod.LEDGERS = tuple(mod.LEDGERS) + ("tier0/_q20_lint_probe.md",)
        assert mod.check(False) == 1
    finally:
        probe.unlink()


def test_a_resolver_row_pointing_at_nothing_is_red(monkeypatch):
    mod = _lint_module()
    monkeypatch.setattr(
        mod, "load_resolver", lambda: {"docs/gone.md": "docs/archive/also-gone.md"}
    )
    assert mod.check(False) == 1
