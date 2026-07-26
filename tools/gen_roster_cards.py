#!/usr/bin/env python3
"""Generate every character profile in the shared roster mod.

The historical ``gen_klee_cards.py`` entry point remains available and still
defaults to Klee for compatibility with existing scripts. This is the roster
entry point used by CI and future character additions.
"""

from __future__ import annotations

from gen_klee_cards import main


if __name__ == "__main__":
    raise SystemExit(main(default_character="all"))
