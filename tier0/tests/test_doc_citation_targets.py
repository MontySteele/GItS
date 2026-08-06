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
"""

from __future__ import annotations

import pathlib
import re

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
TOOLS = REPO_ROOT / "tools"

DOC_PATH = re.compile(r"docs/[A-Za-z0-9_./-]+\.(?:md|yaml|tsv|json|txt)")


def _cited() -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for path in sorted(TOOLS.rglob("*.py")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for m in DOC_PATH.finditer(text):
            out.setdefault(m.group(0), set()).add(path.relative_to(REPO_ROOT).as_posix())
    return out


def test_every_docs_path_cited_from_tools_exists():
    missing = {
        target: sorted(who)
        for target, who in _cited().items()
        if not (REPO_ROOT / target).exists()
    }
    assert not missing, (
        "tools/ cite docs/ paths that do not exist -- a paper pass moved or "
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
