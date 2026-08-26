"""EB-141 half (a) — the §4.7 shop instrument names the world it ran in.

`exp_shop_companion_channel` printed n and seed and nothing else, so its own
output failed the citability half of R68 ("a report without a stamp is not
citable"). It is also the registered `M14` measurement, staged to fire on a
registered seed, which is what splits the fix in two:

  (a) PRINTING the live stamp is safe at any time -- four attribute reads and
      one `print`, no rng, no run construction, so the registered seed plays
      out byte-identically. That is what landed.
  (b) ROUTING the instrument through a `Cell` -- R68's usual answer, because a
      Cell prints the stamp itself -- is NOT safe in the window: a Cell
      carries its own seed, runs, plan resolution and run entry. It waits
      until `M14`'s run is taken and graded.

So this file pins (a) WITHOUT pinning it the way (b) would, and the pin is
deliberately structural rather than behavioural: asserting the header by
running the instrument would mean running the registered-seed sweep on every
suite invocation, which is the opposite of leaving the registration alone.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from tier0 import constants as C
from tier05 import cells, draft, exp_shop_companion_channel as shop

STAMP = re.compile(r"^RT\d+/D\d+/P\d+/C\d+$")


# ---------------------------------------------------------------------------
#  The source of truth, and the fact that there is only one
# ---------------------------------------------------------------------------

def test_the_live_stamp_reads_the_four_live_version_attributes():
    assert cells.live_versions() == {
        "RT": C.RUNTEMPLATE_VERSION,
        "D": C.DRAFTER_VERSION,
        "P": draft.POLICY_VERSION,
        "C": C.CONSTANTS_VERSION,
    }
    assert STAMP.match(cells.world_stamp()), cells.world_stamp()


def test_a_cells_stamp_and_the_bare_world_stamp_cannot_disagree():
    """One producer of the spelling. Two would be two ways to write the same
    world down, which is worse than no stamp because it looks fine."""
    assert cells.CANONICAL.stamp().endswith(" " + cells.world_stamp())
    assert cells.CANONICAL.versions == cells.live_versions()


def test_nothing_is_captured_at_import_time():
    """A stored stamp is a stamp that can claim a world it is not in."""
    v = cells.live_versions()
    assert v is not cells.live_versions()          # freshly built each call
    assert cells.live_versions() == v


# ---------------------------------------------------------------------------
#  The instrument -- read structurally, never run
# ---------------------------------------------------------------------------

def _main_prints() -> list[str]:
    """Every `print(...)` argument in the instrument's `main`, unparsed, in
    source order."""
    tree = ast.parse(Path(shop.__file__).read_text(encoding="utf-8"))
    fn = next(n for n in tree.body
              if isinstance(n, ast.FunctionDef) and n.name == "main")
    return [ast.unparse(node.args[0])
            for node in ast.walk(fn)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name) and node.func.id == "print"
            and node.args]


def test_the_first_thing_the_instrument_prints_is_the_live_world_stamp():
    prints = _main_prints()
    assert prints, "the instrument prints nothing at all any more"
    assert prints[0] == "cells.world_stamp()", prints[:2]


def test_the_pre_existing_header_is_untouched_below_it():
    """Half (a) is ADDITIVE. Every line this instrument printed before is
    printed unchanged, so the numbers already published against it stay
    reproducible -- the same bargain the 2026-08-10 repairs took with their
    `NEW` lines."""
    # `ast.unparse` normalises the quoting, so the expected text goes through
    # the parser too rather than being spelled twice.
    expected = ast.unparse(ast.parse(
        'f"§4.7 companion channel -- {runs} runs/arm, seed {SEED}\\n"',
        mode="eval").body)
    assert _main_prints()[1] == expected


def test_the_instrument_still_does_not_route_through_a_cell():
    """Half (b)'s gate, held open. `Cell` construction or `Cell.run` appearing
    in this file before `M14` is run and graded is the change the registration
    window forbids."""
    src = Path(shop.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    calls = {ast.unparse(n.func) for n in ast.walk(tree)
             if isinstance(n, ast.Call)}
    assert calls & {"cells.world_stamp"}
    assert not calls & {"cells.Cell", "cells.CANONICAL.but", "cell.run"}, calls
    assert "cells.CANONICAL" not in src
