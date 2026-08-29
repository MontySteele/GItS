#!/usr/bin/env python3
"""Generate every character profile in the shared roster mod.

The historical ``gen_klee_cards.py`` entry point remains available and still
defaults to Klee for compatibility with existing scripts. This is the roster
entry point used by CI and future character additions.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Both invocations have to work. `python tools/gen_roster_cards.py` puts
# `tools/` on sys.path itself, so the bare import below resolves; `python -m
# tools.gen_roster_cards` puts the REPO ROOT there instead and the same import
# raised ModuleNotFoundError -- so the two ways of asking "is codegen stale?"
# did not answer the same question. Prepending this file's own directory makes
# the bare import correct under both.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from gen_klee_cards import main   # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main(default_character="all"))
