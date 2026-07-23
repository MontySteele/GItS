"""Portable-test mode excludes local reference artifacts atomically."""

from __future__ import annotations

import os
import subprocess
import sys


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
    subprocess.run(
        [sys.executable, "-c", probe],
        env=env,
        check=True,
        text=True,
        capture_output=True,
    )
