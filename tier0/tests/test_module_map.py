"""tools/module_map.py -- a def-level map is small, complete, and import-free."""

from __future__ import annotations

import io
import re
from pathlib import Path

import pytest

from tools import module_map

ROOT = Path(__file__).resolve().parents[2]

SAMPLE = '''
class Session:
    """One live game.

    More words.
    """

    def _settle(self, state):
        """Ride out a transient frame."""
        return state

    async def run(self):
        pass


def helper():
    pass
'''


def test_map_lists_every_definition_with_range_and_doc():
    lines = module_map.map_source(SAMPLE)
    assert [l.split()[2] for l in lines] == ["Session", "Session._settle", "Session.run", "helper"]
    assert lines[0].startswith("    2-13    class Session  One live game.")
    assert "Ride out a transient frame." in lines[1]


def test_grep_narrows_to_matching_dotted_names():
    lines = module_map.map_source(SAMPLE, grep=re.compile("settle"))
    assert len(lines) == 1 and "Session._settle" in lines[0]


@pytest.mark.parametrize("module", ["understudy/soak.py", "understudy/blindplay.py",
                                    "understudy/staged_turn.py", "understudy/seat.py"])
def test_map_is_under_a_tenth_of_the_module(module):
    src = io.open(ROOT / module, encoding="utf-8").read()
    mapped = "\n".join(module_map.map_source(src))
    assert 0 < len(mapped) < len(src) / 10, (len(mapped), len(src))


def test_mapping_does_not_import_the_module(monkeypatch):
    # A module whose import would be a side effect must still map: ast only.
    poison = "import sys\nsys.exit(99)\n\ndef f():\n    pass\n"
    assert module_map.map_source(poison) == ["    4-5     def   f"]
