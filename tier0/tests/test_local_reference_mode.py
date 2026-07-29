"""Portable-test mode excludes local reference artifacts atomically."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_committed_only_mode_ignores_game_ref_even_when_it_exists():
    env = dict(os.environ)
    env["GITS_REFERENCE_MODE"] = "committed-only"
    probe = """
from tier0.content import loader, upgrades
assert not (loader.GAME_REF_DIR / "ironclad_pool.yaml").exists()
assert not upgrades.EXTERNAL_UPGRADE_SHEETS[0].exists()
assert "real_ironclad" not in loader._character_index()
assert not any(
    card.character == "real_ironclad"
    for card in loader._card_index().values()
)
"""
    # cwd PINNED TO THE REPO ROOT. The subprocess resolves `tier0` off its own
    # working directory, so this inherited pytest's -- fine from the repo root,
    # and a ModuleNotFoundError from anywhere else. validate.ps1 runs the
    # portable suite from the STAGED PACKAGE directory, where this failed for
    # a reason that had nothing to do with reference modes.
    #
    # PRE-EXISTING, not introduced by the Fanfare rework: confirmed by running
    # this test at HEAD from klee-mod/, where it fails identically. Fixed here
    # because it is the same cwd-dependence class as the one this sprint's own
    # validate run surfaced in test_roster_codegen, and a gate that only
    # passes from one directory is not a gate.
    subprocess.run(
        [sys.executable, "-c", probe],
        env=env,
        cwd=Path(__file__).resolve().parent.parent.parent,
        check=True,
        text=True,
        capture_output=True,
    )
