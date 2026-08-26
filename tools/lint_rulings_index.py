#!/usr/bin/env python3
"""`docs/current/RULINGS.md` covers every cited R-number, and is not stale.

TWO ASSERTIONS, AND THEY ANSWER DIFFERENT QUESTIONS.

1. **COVERAGE.** Every `R<n>` token in `docs/current/**/*.md` has a row in the
   index. This is the reader's guarantee: a citation you meet in QUEUE, LAW or
   an atlas page can be resolved by opening ONE file. It reads two files and
   no history, so it runs anywhere -- including the depth-1 CI checkout.

   Coverage does not require that the ruling was RESOLVED. An unresolved row
   still tells the reader the true thing ("this number does not resolve from
   HEAD; the tag is where to look"), and an id that never resolves is a fact
   about the archive, not a defect in the index.

2. **STALENESS.** The committed file equals what `tools/gen_rulings_index.py`
   generates right now. Regenerating in-process and comparing is the same code
   path the generator's own `--out` takes; no temp file is needed to know
   whether the bytes differ, and `--diff` prints the difference when they do.

   This half NEEDS HISTORY, and CI has none: `actions/checkout@v4` takes a
   depth-1 clone with no tags, so the retired ledgers and every ruling commit
   are simply absent there and a regeneration would produce an all-unresolved
   file. So the check SKIPS ITSELF, loudly, when the generator reports no
   history -- it declares a question it cannot ask rather than answering it
   wrong. The half that always runs is coverage, which is also the half that
   catches the realistic failure: a new ruling cited before the index caught
   up.

Registered in the CI lane on the strength of assertion 1 and its cost --
around a third of a second, one `git log` and three `git show`s at worst.

Usage:
    python tools/lint_rulings_index.py
    python tools/lint_rulings_index.py --diff   # show the staleness diff

Exit 1 with findings on stdout.
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from tools.gen_rulings_index import (OUT, R_TOKEN, pages,  # noqa: E402
                                     render)
from tools.lint_r_numbers import R_CEILING                 # noqa: E402
from understudy.report import console_safe                 # noqa: E402

ROW = re.compile(r"(?m)^\|\s*R(\d+)\s*\|")


def indexed_ids(text: str) -> set[int]:
    return {int(m) for m in ROW.findall(text)}


def citations() -> dict[int, list[str]]:
    """id -> the pages that cite it, over the same tree lint_r_numbers scans."""
    out: dict[int, list[str]] = {}
    for page in pages():
        rel = page.relative_to(REPO).as_posix()
        for m in set(R_TOKEN.findall(page.read_text(encoding="utf-8"))):
            n = int(m)
            if 1 <= n <= R_CEILING:
                out.setdefault(n, []).append(rel)
    return out


def main(argv: list[str]) -> int:
    console_safe()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--diff", action="store_true",
                    help="print the staleness diff, not just the verdict")
    args = ap.parse_args(argv)

    rel = OUT.relative_to(REPO).as_posix()
    if not OUT.is_file():
        print(f"rulings-index: {rel} is missing "
              "-- run `python -m tools.gen_rulings_index`")
        return 1

    committed = OUT.read_text(encoding="utf-8")
    have = indexed_ids(committed)
    cited = citations()
    findings: list[str] = []

    for n in sorted(set(cited) - have):
        where = ", ".join(sorted(cited[n])[:3])
        extra = "" if len(cited[n]) <= 3 else f" (+{len(cited[n]) - 3} more)"
        findings.append(f"R{n} is cited in {where}{extra} but has no row in "
                        f"{rel} -- regenerate the index")

    fresh, stats = render()
    if not stats["history"]:
        print(f"rulings-index: staleness SKIPPED -- no history in this clone "
              f"(no retired ledgers, {stats['commits']} commits readable). "
              "Coverage still checked.")
    elif fresh != committed:
        findings.append(
            f"{rel} is stale -- `python -m tools.gen_rulings_index` produces "
            "different bytes. Regenerate it in the commit that changed the "
            "citations or the history.")
        if args.diff:
            print("\n".join(difflib.unified_diff(
                committed.splitlines(), fresh.splitlines(),
                fromfile=f"{rel} (committed)", tofile="(generated)",
                lineterm="")))

    if findings:
        print(f"rulings-index: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1

    print(f"rulings-index OK: {len(have)} rows cover "
          f"{len(cited)} cited R-number(s) across {len(pages())} pages"
          + ("" if not stats["history"] else ", and the file is current"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
