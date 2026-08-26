"""`--help` for the tier 0.5 experiment scripts, and nothing else (EB-115).

THE TRAP THIS CLOSES. Every `tier05/exp_*.py` reads its arguments -- when it
reads them at all -- inside `main()`, after the sweep has already been built
and often after it has already run. So

    python -m tier05.exp_roster_anchors --help

executed a full 600-run, seed-11 twelve-arm sweep and only THEN printed
something. Nothing was recorded from that accidental run, but the cost is
real, and it is the same curated footgun `art_fetch --help` had: the one
command a reader types to find out what a script does is the command that
runs it.

WHY A HELPER RATHER THAN AN `argparse` PASS PER SCRIPT. Two of these scripts
-- `exp_shop_companion_channel` (`M14`) and `exp_eb17p_forced_copy` -- are
STAGED REGISTERED INSTRUMENTS whose run behaviour, seeding and output must
stay byte-identical until their registered runs are taken and graded. Handing
either one a real argument parser would move argument handling, and argument
handling is upstream of seeding. This helper cannot: it is called as the FIRST
statement of the `__main__` block, it looks at `sys.argv` for exactly two
literal strings, and on every other invocation it returns having done nothing
at all. A run with no `-h` in it takes the identical path it took before.

WHAT IT PRINTS is the module's own docstring, verbatim. These docstrings are
the documentation -- predictions, RNG discipline, usage lines, the lot -- and
extracting a "usage section" from them would be a second thing to keep in
step with the first. Printing the whole thing cannot go stale.

Usage, at the top of a script's `__main__` block and before anything else:

    if __name__ == "__main__":
        expcli.help_if_asked(__doc__)
        raise SystemExit(main())
"""

from __future__ import annotations

import sys

#: The two spellings. Deliberately not a prefix match: `--helpful-arm` is not
#: a help request, and a script that grows one must not start printing its
#: docstring instead of running.
HELP_FLAGS = ("-h", "--help")


def help_requested(argv: list[str] | None = None) -> bool:
    """Is `-h` or `--help` among these arguments?"""
    return any(a in HELP_FLAGS for a in (sys.argv[1:] if argv is None
                                         else argv))


def help_if_asked(doc: str | None, argv: list[str] | None = None) -> None:
    """Print `doc` and exit 0 if help was asked for; otherwise do nothing.

    `SystemExit` rather than a return value on purpose: the caller is a
    `__main__` block, and a helper that only ADVISES the script to stop is a
    helper the next script forgets to obey.
    """
    if not help_requested(argv):
        return
    print((doc or "").strip() or
          "(this script has no docstring, so there is no help to print)")
    raise SystemExit(0)
