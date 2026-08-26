#!/usr/bin/env python3
"""Correction D: a sheet edit that did not bump a stamp fails, instead of being noticed.

WHY THIS EXISTS. The stamp law is the repo's oldest rule and its most
frequently broken one: *"every published number is world-stamped, and worlds
are not comparable"*. `CONSTANTS_VERSION` guards the constants file, and the
suite pins plenty of individual card values -- but the CONTENT SHEETS
(`docs/*-cards.yaml`, `docs/*-companions.yaml`) are the largest surface that
moves a measured world, and until now nothing connected an edit there to a
stamp bump. Two of the five re-stamps `M14` needed were exactly this shape:
*"version-integer-free content ... the shelf itself renumbers"* -- a pool
grows by three Uncommons, `rng.choice` maps the same draw to a different card,
every arm's numbers move, and no integer anywhere changed.

WHAT IS CHECKED. One digest over all six sheets must equal `SHEET_DIGEST`,
pinned beside `CONSTANTS_VERSION` in `tier0/constants.py`. Touch a sheet
without re-pinning and this fails; re-pin it and the stamp bump is in the same
diff as the content that earned it, where a reviewer can see both.

  * **The digest covers path AND bytes**, so renaming a sheet, adding one, or
    deleting one moves it -- a content change that a per-file hash list would
    have to be taught about separately.
  * **Newlines are normalised to `\\n` first.** The sheets are CRLF in this
    checkout; a digest that did not normalise would read differently under a
    different `core.autocrlf` and the gate would fire on the checkout rather
    than on the content.
  * **It is a fingerprint, not a diff.** It says *something moved and the stamp
    did not*, never what moved. `git diff` answers that, and a lint that tried
    to would be re-implementing it.

`--update` re-pins. It is the whole workflow: edit the sheet, run
`--update`, and commit both halves together. It rewrites exactly the one
assignment line and nothing else in a 2,500-line file that is otherwise not
this tool's to touch.

**DEBT: none, by construction.** The other Correction-D lints ship green by
carrying a curated set of rows that fail today; this one ships green because
`--update` pins it green at birth. There is nothing to grandfather -- the
digest is either current or it is not.

    python tools/lint_sheet_stamp.py
    python tools/lint_sheet_stamp.py --update      # re-pin after a sheet edit
    python tools/lint_sheet_stamp.py --self-test

Exit 1 with findings on stdout.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

CONSTANTS = REPO / "tier0" / "constants.py"
PATTERNS = ("docs/*-cards.yaml", "docs/*-companions.yaml")

# The one line this tool may rewrite. Anchored at the start of a line so a
# mention inside a docstring or a comment cannot be mistaken for the constant.
PIN = re.compile(r'^SHEET_DIGEST = "([0-9a-f]{0,64})"', re.MULTILINE)


def sheets() -> list[Path]:
    found: list[Path] = []
    for pattern in PATTERNS:
        found.extend(REPO.glob(pattern))
    return sorted(found, key=lambda p: p.relative_to(REPO).as_posix())


def digest(paths: list[Path] | None = None) -> str:
    """One sha256 over `<relative path>\\n<normalised bytes>` for each sheet."""
    hasher = hashlib.sha256()
    for path in (sheets() if paths is None else paths):
        try:
            rel = path.relative_to(REPO).as_posix()
        except ValueError:
            # Outside the repo: the self-test's temp files. The NAME still
            # participates, which is what makes the rename case meaningful.
            rel = path.name
        body = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        hasher.update(rel.encode("utf-8") + b"\n")
        hasher.update(body)
        hasher.update(b"\n--\n")
    return hasher.hexdigest()


def pinned(text: str | None = None) -> str | None:
    """The pinned digest, or `None` when the constant is absent."""
    if text is None:
        # newline="" so the file's own line endings survive a --update
        # round-trip: this file is 2,500 lines that are not this tool's, and a
        # lint that silently rewrote all of them would be a worse defect than
        # the one it gates.
        text = CONSTANTS.read_text(encoding="utf-8", newline="")
    match = PIN.search(text)
    return match.group(1) if match else None


def repin(new: str) -> bool:
    text = CONSTANTS.read_text(encoding="utf-8", newline="")
    if not PIN.search(text):
        return False
    text = PIN.sub(f'SHEET_DIGEST = "{new}"', text, count=1)
    CONSTANTS.write_text(text, encoding="utf-8", newline="")
    return True


def findings() -> tuple[list[str], str, str | None, int]:
    found = sheets()
    live = digest()
    stamp = pinned()
    out: list[str] = []

    if not found:
        out.append("VACUOUS: no sheets matched " + " or ".join(PATTERNS) +
                   " -- this lint compared nothing and must not read clean.")
    elif stamp is None:
        out.append(f"NO PIN: tier0/constants.py has no `SHEET_DIGEST = \"...\"` "
                   f"line. Add it beside CONSTANTS_VERSION and run "
                   f"`python tools/lint_sheet_stamp.py --update`.")
    elif stamp != live:
        out.append(f"SHEET STAMP STALE: the {len(found)} content sheets digest "
                   f"to {live[:16]}... and tier0/constants.py pins "
                   f"{stamp[:16]}.... A sheet moved and no stamp moved with "
                   f"it. Content with no version integer still renumbers the "
                   f"shelf and moves every arm -- decide the version bump the "
                   f"edit earns, then re-pin with "
                   f"`python tools/lint_sheet_stamp.py --update` in the SAME "
                   f"commit as the sheet edit.")
    return out, live, stamp, len(found)


def self_test() -> list[str]:
    """The digest's own properties, on temporary files -- never on the sheets."""
    import tempfile

    bad: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        a, b = root / "a-cards.yaml", root / "b-companions.yaml"
        a.write_bytes(b"one: 1\n")
        b.write_bytes(b"two: 2\n")

        first = digest([a, b])
        if first != digest([a, b]):
            bad.append("self-test: the digest is not deterministic")

        a.write_bytes(b"one: 2\n")
        if digest([a, b]) == first:
            bad.append("self-test: a CONTENT change did not move the digest — "
                       "this is the whole failure the lint exists to catch")

        a.write_bytes(b"one: 1\n")
        if digest([a, b]) != first:
            bad.append("self-test: reverting the content did not restore the "
                       "digest")

        a.write_bytes(b"one: 1\r\n")
        if digest([a, b]) != first:
            bad.append("self-test: CRLF vs LF moved the digest — the gate "
                       "would fire on the checkout instead of on the content")

        c = root / "c-cards.yaml"
        c.write_bytes(b"")
        if digest([a, b, c]) == first:
            bad.append("self-test: ADDING an empty sheet did not move the "
                       "digest")

        renamed = root / "z-cards.yaml"
        a.rename(renamed)
        if digest([renamed, b]) == first:
            bad.append("self-test: RENAMING a sheet did not move the digest")

    if not sheets():
        bad.append("self-test: the live sheet glob matches nothing")
    return bad


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        bad = self_test()
        for line in bad:
            print(line)
        print(f"self-test: 7 case(s), {len(bad)} failure(s)")
        return 1 if bad else 0

    if "--update" in argv:
        live = digest()
        if not repin(live):
            print("NO PIN: tier0/constants.py has no `SHEET_DIGEST = \"...\"` "
                  "line to rewrite. Add one beside CONSTANTS_VERSION first.")
            return 1
        print(f"re-pinned SHEET_DIGEST = \"{live}\" over "
              f"{len(sheets())} sheet(s). Commit it WITH the sheet edit.")
        return 0

    bad, live, stamp, count = findings()
    for line in bad:
        print(line)
    print(f"scope: {count} sheet(s), digest {live[:16]}..., pinned "
          f"{(stamp or '<none>')[:16]}...")
    if bad:
        return 1
    print("sheet-stamp OK: every content sheet is accounted for by the digest "
          "pinned beside CONSTANTS_VERSION.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
