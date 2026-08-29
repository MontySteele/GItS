#!/usr/bin/env python3
"""Classify a CI diff: is this change docs-only, or does it need the full suite?

WHY THIS EXISTS. `.github/workflows/repo.yml` has no path filters at the
trigger level, and it must not gain any: `paths-ignore` makes a skipped job
report NOTHING, and a required check that never reports blocks the pull
request forever. So the filtering has to happen INSIDE a job that always runs
and always reports. This tool is the decision that job makes.

THE RULE. `docs_only=true` only when EVERY changed path is a `.md` file living
under `docs/current/`, `review/`, or the repo root (`README.md`, `CLAUDE.md`,
`AGENTS.md`, a memory-style note). Anything else is `false`:

  * `docs/*.yaml` and `docs/*.md` outside `current/` -- the card sheets and
    their siblings are CONTENT; the suite reads them.
  * `review/qa/*.json` / `*.txt` -- graded QA artifacts that tests parse.
  * `.py`, `.cs`, `.yml`, `tools/`, `tier0/`, `tier05/`, `klee-mod/`,
    `understudy/`, `vendor/` -- code, by any route.

FAIL SAFE. An EMPTY list is `false`, not `true`. The empty case is what a
failed `git diff` looks like (a shallow checkout, a force-push, a first push
whose `before` is all zeros), and the one answer that must never come out of
a broken measurement is "run less".

    python tools/ci_changed_paths.py docs/current/STATE.md   # docs_only=true
    git diff --name-only origin/main...HEAD | python tools/ci_changed_paths.py
    python tools/ci_changed_paths.py --self-test
"""
from __future__ import annotations

import sys

# A path is docs-only when it ends in `.md` AND sits in one of these places.
# `docs/current/` is the always-loadable register set; `review/` is the packet
# tree (prose only -- its .json/.txt siblings are excluded by the .md rule).
DOC_PREFIXES = ("docs/current/", "review/")


def normalise(path: str) -> str:
    """Git's `--name-only` spelling, made comparable."""
    return path.strip().strip('"').replace("\\", "/").lstrip("./")


def is_doc_path(path: str) -> bool:
    """True when this one path is a markdown doc the suite does not read."""
    path = normalise(path)
    if not path or not path.lower().endswith(".md"):
        return False
    if "/" not in path:                 # repo root: README/CLAUDE/AGENTS/...
        return True
    return path.startswith(DOC_PREFIXES)


def docs_only(paths: list[str]) -> bool:
    """True when EVERY changed path is a doc. Empty => False (fail safe)."""
    cleaned = [normalise(p) for p in paths]
    cleaned = [p for p in cleaned if p]
    if not cleaned:
        return False
    return all(is_doc_path(p) for p in cleaned)


CASES: list[tuple[list[str], bool, str]] = [
    # --- true: markdown, in the three allowed places -----------------------
    (["docs/current/STATE.md"], True, "one register page"),
    (["docs/current/STATE.md", "docs/current/QUEUE.md",
      "docs/current/atlas/klee-mod-runtime.md"], True,
     "several pages under docs/current, nested included"),
    (["review/active/ci-fast-lane-2026-08-29.md"], True, "a review packet"),
    (["README.md"], True, "a repo-root readme"),
    (["CLAUDE.md", "AGENTS.md"], True, "the two routing files"),
    (["docs/current/STATE.md", "review/active/x.md", "CLAUDE.md"], True,
     "all three allowed places at once"),
    (["docs/current/STATE.MD"], True, "the extension is case-insensitive"),
    (["docs\\current\\STATE.md"], True, "a Windows-spelled path"),
    # --- false: anything else ----------------------------------------------
    ([], False, "EMPTY LIST FAILS SAFE to the full run"),
    (["   ", ""], False, "whitespace-only list fails safe too"),
    (["docs/current/STATE.md", "docs/kokomi-cards.yaml"], False,
     "md plus a card sheet"),
    (["docs/kokomi-cards.yaml"], False, "a card sheet alone"),
    (["docs/furina-upgrades.yaml"], False, "an upgrades sheet"),
    (["review/qa/kokomi-t01-review-prompt.txt"], False, "a review/qa txt"),
    (["review/qa/grades.json"], False, "a review/qa json"),
    (["docs/current/STATE.md", "review/qa/grades.json"], False,
     "one non-doc poisons the whole set"),
    ([".github/workflows/repo.yml"], False, "the workflow itself"),
    ([".github/requirements-ci.txt"], False, "the CI requirements file"),
    (["tools/run_lints.py"], False, "a tool"),
    (["tools/ci_changed_paths.py"], False, "this very tool"),
    (["tier0/tests/test_furina.py"], False, "a test"),
    (["tier0/constants.py"], False, "engine constants"),
    (["tier05/model.py"], False, "the tier 0.5 model"),
    (["klee-mod/KleeCode/PrototypeCards.cs"], False, "C# mod source"),
    (["understudy/README.md"], False,
     "md OUTSIDE the three places -- understudy/ is read by the suite"),
    (["docs/kokomi-kickoff-v1.md"], False,
     "md under docs/ but NOT under docs/current/"),
    (["vendor/STS2_MCP/docs/raw-simplified.md"], False,
     "vendor md is a pinned upstream file, not a doc of ours"),
    (["klee-mod/pck-src/README.md"], False, "a README the suite reads"),
    (["pytest.ini"], False, "test configuration"),
    (["docs/current"], False, "a bare directory name is not a .md"),
    (["README.md.py"], False, "the extension must be LAST"),
]


def self_test() -> int:
    failures = []
    for paths, expected, label in CASES:
        got = docs_only(paths)
        if got != expected:
            failures.append(f"self-test FAIL [{label}]: {paths!r} -> "
                            f"docs_only={got}, expected {expected}")
    for line in failures:
        print(line)
    print(f"self-test: {len(CASES)} case(s), {len(failures)} failure(s)")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    paths = [a for a in argv if not a.startswith("--")]
    if not paths and not sys.stdin.isatty():
        paths = sys.stdin.read().splitlines()
    print(f"docs_only={'true' if docs_only(paths) else 'false'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
