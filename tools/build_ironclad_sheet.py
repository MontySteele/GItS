"""Thin Ironclad entry point for tools/build_official_sheet.py.

The assembler was generalised for the Silent anchor (2026-07-27); ALL of the
logic, and every fail-closed / disjointness / --verify guarantee, now lives in
`tools.build_official_sheet`. This module exists because the name is a call
site, not because it holds anything:

  * klee-mod/build/validate.ps1 invokes `python -m tools.build_ironclad_sheet
    --verify` inside the local-reference gate;
  * every generated header in the existing game_ref/ artifacts names it as the
    rebuild command, and those artifacts are gitignored -- nothing in the repo
    can rewrite them for a user who already has them on disk.

Flags pass straight through. `--character` is fixed to ironclad here; use
`python -m tools.build_official_sheet --character silent` for the other anchor.
"""
from __future__ import annotations

import sys

from tools.build_official_sheet import main

if __name__ == "__main__":
    # argparse keeps the LAST occurrence, so a --character in the passthrough
    # would silently win over the pin. Refuse it instead of lying.
    if any(a == "--character" or a.startswith("--character=")
           for a in sys.argv[1:]):
        sys.exit("this entry point is pinned to ironclad; use "
                 "tools.build_official_sheet to pick a character")
    sys.exit(main(["--character", "ironclad", *sys.argv[1:]]))
