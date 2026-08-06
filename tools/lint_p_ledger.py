"""The P-ledger's two mechanical checks, exactly as the Class-P charter wrote them.

WHY THIS IS A LINT
------------------
The Class-P charter (`docs/class-p-charter-2026-08-06.md` §3, SIGNED per R119)
states two suite-failure conditions in so many words:

    "Lint: a P-ledger row without a five-line attestation fails the suite; a
    Class-P change touching a file owned by a [USER]-gated register fails the
    suite."

The whole consent structure of Class-P is that [USER]'s veto stays cheap: he
reads a digest, flags a row, the row reverts by handle. That only works if
(a) every row actually carries the attestation he is ratifying by silence, and
(b) no commit a row points at ever touched the surfaces his gates own. Both
are facts about text and about a commit's file list -- checkable mechanically,
so they are checked mechanically.

RULE 1 -- five-line attestations. Every item section of
`docs/registry/p-ledger.md` (mechanically: any `## ` section containing a
`**Handle:**` field) must carry an `**Attestation:**` block of exactly five
numbered lines, `1.` through `5.`, one per charter §2 test. Fewer, more,
out of order, or absent -- finding.

RULE 2 -- the gated-register guard. Every commit a `**Handle:**` field names
is shown (`git show --name-only`) and its touched paths are matched against
OWNED_BY_USER_GATED_REGISTERS below. Any hit -- finding.

WHAT "OWNED BY A [USER]-GATED REGISTER" MEANS HERE, MECHANICALLY
----------------------------------------------------------------
Defined conservatively as a fixed glob list, not inferred from content. A path
is owned when it is one of:

  - the DECISIONS ledgers, archive volumes included (the ruling bodies
    themselves; a Class-P item may cite them, never write them);
  - pre-registration documents and their probe reports (`docs/probe-*.md`,
    `docs/*registration*.md`) -- pre-registrations stay [USER] by standing law
    and a probe report is the registration's escrowed output;
  - `docs/kokomi-playtest-protocol.md` -- its Answers block is gated by the
    declare-before-playtest law (DEC-D5);
  - the quotable roster-anchor tables (`docs/roster-anchor-*.md`) -- carrying
    a [USER]-designated quotable surface and an in-effect quarantine;
  - verbatim [USER] dispatch and sitting records (`docs/dispatch-*.md`,
    `docs/sitting-record-*.md`) and the pre-drafted landing-text slots
    (`docs/awaiting-user-slots-*.md`).

Deliberately NOT owned: `docs/registry/user-queue.md` and `docs/dockets/` --
the charter's §3 explicitly directs the swarm to sweep and strike queue rows,
so listing them here would make every legitimate Class-P landing a finding.
Widening this list is cheap and safe (more conservative); narrowing it is a
decision, not a repair -- record it.

SHALLOW CLONES. Rule 2 needs the named commits in local history. On a shallow
clone (CI's default fetch-depth: 1) an ancestor commit may be absent; that is
reported per-handle as SKIPPED, not failed, because "this clone cannot see
history" is not a fact about the ledger. The enforcing venue for rule 2 is any
full clone -- the `lints` CI job checks out with fetch-depth: 0 for exactly
this reason, and every dev checkout is full.

Usage: python tools/lint_p_ledger.py
Exit 1 with findings on stdout.
"""

from __future__ import annotations

import fnmatch
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEDGER = REPO / "docs" / "registry" / "p-ledger.md"

OWNED_BY_USER_GATED_REGISTERS = (
    # Widened to the volume globs 2026-08-06 (Track R-D ledger split, a
    # recorded widening per the note above: archive volumes are the same
    # frozen spine -- see docs/registry/ledger-layout-note-2026-08-06.md).
    "tier0/DECISIONS*.md",
    "klee-mod/DECISIONS*.md",
    "docs/probe-*.md",
    "docs/*registration*.md",
    "docs/kokomi-playtest-protocol.md",
    "docs/roster-anchor-*.md",
    "docs/dispatch-*.md",
    "docs/sitting-record-*.md",
    "docs/awaiting-user-slots-*.md",
)

_HANDLE = re.compile(r"\*\*Handle:\*\*\s*`([0-9a-f]{7,40})`")
_ATT_LINE = re.compile(r"^\s*(\d)\.\s+\S")


def parse_items(text: str) -> list[tuple[str, str]]:
    """(heading, body) for every `## ` section that carries a Handle field.

    Sections without a Handle are prose (the header, the not-landed record)
    and are not rows; a row IS defined by pointing at a commit, because the
    revert-by-handle veto is what a row exists to enable.
    """
    items: list[tuple[str, str]] = []
    heads = [m for m in re.finditer(r"^##\s+(.+)$", text, re.M)]
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        body = text[m.end():end]
        if _HANDLE.search(body):
            items.append((m.group(1).strip(), body))
    return items


def attestation_problem(body: str) -> str | None:
    """None when the body carries exactly lines 1..5 after **Attestation:**."""
    marker = body.find("**Attestation:**")
    if marker == -1:
        return "no **Attestation:** block"
    numbers: list[str] = []
    for line in body[marker:].splitlines()[1:]:
        got = _ATT_LINE.match(line)
        if got:
            numbers.append(got.group(1))
        elif numbers and line.strip() and not line.startswith(" "):
            break  # the block ended; later prose is not attestation
    if numbers[:5] == list("12345") and len(numbers) == 5:
        return None
    return (f"attestation lines read {numbers or 'as empty'}, "
            "need exactly 1. through 5. (charter §2, one line per test)")


def handles(body: str) -> list[str]:
    return _HANDLE.findall(body)


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(REPO), *args],
                          capture_output=True, text=True)


def is_shallow() -> bool:
    got = _git("rev-parse", "--is-shallow-repository")
    return got.returncode == 0 and got.stdout.strip() == "true"


def changed_files(sha: str) -> list[str] | None:
    """Paths the commit touched, or None when the commit is not in history."""
    if _git("cat-file", "-e", f"{sha}^{{commit}}").returncode != 0:
        return None
    got = _git("show", "--name-only", "--format=", sha)
    if got.returncode != 0:
        return None
    return [line.strip() for line in got.stdout.splitlines() if line.strip()]


def owned_paths(paths: list[str]) -> list[str]:
    return [p for p in paths
            if any(fnmatch.fnmatch(p, glob)
                   for glob in OWNED_BY_USER_GATED_REGISTERS)]


def main() -> int:
    if not LEDGER.exists():
        print("p-ledger: docs/registry/p-ledger.md does not exist -- the "
              "charter (R119 §3) mandates one row per landed Class-P item")
        return 1

    items = parse_items(LEDGER.read_text(encoding="utf-8"))
    findings: list[str] = []
    skipped: list[str] = []
    if not items:
        findings.append("ledger parses to zero rows (a row = a `## ` section "
                        "with a **Handle:** field) -- a dead gate checks "
                        "nothing")

    shallow = is_shallow()
    checked_commits = 0
    for heading, body in items:
        problem = attestation_problem(body)
        if problem:
            findings.append(f"row '{heading}': {problem}")
        for sha in handles(body):
            paths = changed_files(sha)
            if paths is None:
                if shallow:
                    skipped.append(f"row '{heading}': commit {sha} not in "
                                   "this shallow clone's history -- rule 2 "
                                   "unverifiable here, enforced on full "
                                   "clones")
                    continue
                findings.append(f"row '{heading}': handle {sha} is not a "
                                "commit in this repository -- a veto cannot "
                                "revert what it cannot find")
                continue
            checked_commits += 1
            for path in owned_paths(paths):
                findings.append(f"row '{heading}': commit {sha} touches "
                                f"{path}, a file owned by a [USER]-gated "
                                "register -- never Class-P (charter §2 "
                                "test 5 / §3 lint)")

    for note in skipped:
        print(f"  note: {note}")
    if findings:
        print(f"p-ledger: {len(findings)} finding(s)")
        for finding in findings:
            print(f"  {finding}")
        return 1

    print(f"p-ledger OK: {len(items)} row(s), all with five-line "
          f"attestations; {checked_commits} handle commit(s) touch no "
          "[USER]-gated register")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
