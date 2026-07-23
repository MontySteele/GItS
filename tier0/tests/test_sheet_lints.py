"""Cross-sheet lint gates (tools/lint_strict_domination.py).

The per-sheet comment/number lint gate lives with its sheet's tests
(test_furina_sheet.test_sheet_comments_match_numbers); this module holds
the lints that sweep every docs card sheet at once.
"""

import subprocess
import sys
from pathlib import Path

from tier0.content import loader

REPO = Path(loader.__file__).resolve().parents[2]


def test_no_strict_domination_on_docs_sheets():
    sheets = [str(loader.DOCS_DIR / s) for s in loader.DOCS_CARD_SHEETS]
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_strict_domination.py"),
         *sheets],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr


def test_card_names_are_unique():
    """Display names: unique internally, and clear of docs/reserved-card-names.txt.

    The reserved list exists because this class of bug is STRUCTURALLY
    INVISIBLE to the repo -- we ship alongside base-game and third-party
    cards whose name lists we cannot read, and the engine resolves a clash
    unpredictably. It was a human who noticed our "Grand Finale" was also
    the Silent's. No instrument here could have. The list is the record of
    those catches; append to it, and don't prune without a reason on file.
    """
    sheets = [str(loader.DOCS_DIR / s) for s in loader.DOCS_CARD_SHEETS]
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_unique_names.py"),
         *sheets],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
