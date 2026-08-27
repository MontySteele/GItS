"""Visual QA gates (surplus-dispatch-3 lane C, charter label EB-151).

Five INDEPENDENT checks over the artefacts a pck build leaves behind, none of
which needs the game, the editor, or a live capture to run:

    export-log     the MegaDot headless import/export log, read for errors
    scene-deps     .tscn/.tres under klee-mod/pck-src, read for broken
                   resource and animation references
    fallback       the build's own "X fallback: <rel> <- Y" lines, read
                   against a declared policy
    contract       klee.pck.contract.txt and the staged package, read against
                   each other and against the git-tracked scene sources
    contact-sheet  a deterministic sheet built from a directory of PNGs

Why a separate family rather than more rules inside
`klee-mod/build/validate.ps1`: every S-gate in that file is PowerShell, runs
only on the deploy path, and several of them need the game install. These
gates are Python, take their inputs as FILES, and therefore run in CI, in a
test, and on a machine that has never had Slay the Spire 2 on it. They do not
replace the S-gates and do not edit them; where they overlap (S1's stray-JSON
rule, S2's contract sha256) the overlap is deliberate and noted at the rule.

Nothing here reads or writes the game installation, the deployed mod, or
ImageGen. Every entry point takes explicit paths.

Run with:

    python -m tools.visual_qa --help
"""

from __future__ import annotations

from .findings import Finding, Report, ERROR, WARNING, NOTE

__all__ = ["Finding", "Report", "ERROR", "WARNING", "NOTE"]
