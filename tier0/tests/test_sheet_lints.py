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
