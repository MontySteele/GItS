"""Selection policy for gitignored, machine-local reference artifacts.

The default remains strict: use game_ref when it is present, allowing the
loader to reject an incomplete artifact loudly. Deployment validation may set
GITS_REFERENCE_MODE=committed-only to test the portable, repository-owned
content surface without treating a stale local reference as real data.
"""

from __future__ import annotations

import os
from pathlib import Path

REFERENCE_MODE_ENV = "GITS_REFERENCE_MODE"
AUTO = "auto"
COMMITTED_ONLY = "committed-only"

DEFAULT_GAME_REF_DIR = Path(__file__).parents[2] / "game_ref"


def mode() -> str:
    value = os.environ.get(REFERENCE_MODE_ENV, AUTO).strip().lower()
    if value not in {AUTO, COMMITTED_ONLY}:
        raise ValueError(
            f"{REFERENCE_MODE_ENV} must be {AUTO!r} or "
            f"{COMMITTED_ONLY!r}, got {value!r}")
    return value


def game_ref_dir() -> Path:
    if mode() == COMMITTED_ONLY:
        # Deliberately nonexistent beneath the ignored directory. Returning a
        # path instead of sprinkling mode branches through the loader preserves
        # its existing "total absence" behavior and skip guards.
        return DEFAULT_GAME_REF_DIR / ".disabled-for-committed-only"
    return DEFAULT_GAME_REF_DIR
