"""EB-141 half (b) -- the §4.7 shop instrument RUNS THROUGH A `Cell`.

This file replaces `test_eb141a_shop_stamp.py`, which pinned half (a) (the
instrument PRINTING the live stamp beside a `model.run_many` it called itself)
and held (b)'s gate open by FAILING if a `Cell` appeared in the file. That gate
opened on 2026-08-26, when `M14`'s registered run was taken and graded and the
world-freeze the packet declared was spent, so the leg retires here with the
reroute it was guarding.

What (a) established stays pinned below -- `cells.live_versions()` /
`cells.world_stamp()` are still the single producer of the world half, and
nothing is captured at import time. What changes is the claim on the
instrument: it must now route, and the routing must be argument-for-argument
the direct call it replaces.

THE EQUIVALENCE PIN IS THE POINT OF THIS FILE. The whole reason (b) was parked
rather than fixed inline is that a `Cell` carries its own seed, runs, plan
resolution, route, jobs and run entry, any one of which could move the
registered seed's behaviour. So the test CAPTURES what `Cell.run` hands
`model.run_many` and asserts it equals what the pre-reroute call passed --
byte for byte, argument for argument. It never runs the sweep: asserting the
header by running the instrument would mean firing a registered-seed
measurement on every suite invocation, which is the opposite of leaving a
registration alone.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from tier0 import constants as C
from tier05 import cells, draft, model
from tier05 import exp_shop_companion_channel as shop

STAMP = re.compile(r"RT\d+/D\d+/P\d+/C\d+$")


# ---------------------------------------------------------------------------
#  The source of truth, and the fact that there is still only one
# ---------------------------------------------------------------------------

def test_the_live_stamp_reads_the_four_live_version_attributes():
    assert cells.live_versions() == {
        "RT": C.RUNTEMPLATE_VERSION,
        "D": C.DRAFTER_VERSION,
        "P": draft.POLICY_VERSION,
        "C": C.CONSTANTS_VERSION,
    }
    assert STAMP.search(cells.world_stamp()), cells.world_stamp()


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


def test_the_instruments_base_cell_reads_the_live_world_too():
    """`BASE_CELL` is built at IMPORT time, but `Cell.versions` is a property
    over `live_versions()`, so the module-level object cannot carry a stale
    world into a run started an hour later."""
    assert shop.BASE_CELL.versions == cells.live_versions()
    assert shop.BASE_CELL.stamp().endswith(" " + cells.world_stamp())


# ---------------------------------------------------------------------------
#  The reroute -- half (b)'s own claim
# ---------------------------------------------------------------------------

def test_the_instrument_routes_through_a_cell():
    """(b)'s gate, now CLOSED THE OTHER WAY. The (a)-era test asserted that no
    `Cell` appeared in this file; the reroute is what it was waiting for."""
    src = Path(shop.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    calls = {ast.unparse(n.func) for n in ast.walk(tree)
             if isinstance(n, ast.Call)}
    assert "cells.Cell" in calls
    assert "cell.run" in calls
    # And the direct call it replaced is gone -- a second, unrouted run path
    # would put the stamp back beside the run instead of on it.
    assert "model.run_many" not in calls, calls


def test_the_first_thing_the_instrument_prints_is_a_cell_stamp():
    """The header is the RUN OBJECT's stamp now, not a bare world string
    printed next to it."""
    tree = ast.parse(Path(shop.__file__).read_text(encoding="utf-8"))
    fn = next(n for n in tree.body
              if isinstance(n, ast.FunctionDef) and n.name == "main")
    prints = [ast.unparse(node.args[0])
              for node in ast.walk(fn)
              if isinstance(node, ast.Call)
              and isinstance(node.func, ast.Name) and node.func.id == "print"
              and node.args]
    assert prints, "the instrument prints nothing at all any more"
    assert prints[0] == "header.stamp()", prints[:2]
    # The pre-existing header line is still printed unchanged below it, so the
    # numbers already published against this instrument -- the graded M14 read
    # of 2026-08-26 among them -- stay line-comparable.
    expected = ast.unparse(ast.parse(
        'f"§4.7 companion channel -- {runs} runs/arm, seed {SEED}\\n"',
        mode="eval").body)
    assert prints[1] == expected


# ---------------------------------------------------------------------------
#  The equivalence pin: the Cell hands `run_many` what the direct call did
# ---------------------------------------------------------------------------

#: The pre-reroute call, transcribed from the code this change replaced:
#:
#:     model.run_many(character, archetype, archetype,
#:                    draft.assigned_policy, runs, SEED,
#:                    grant_relics=True, grant_potions=True, n_acts=3)
#:
#: with `run_many`'s own defaults filled in for the three arguments it did not
#: pass (`jobs=1`, `route_name="hunter"`, `force_cards=None`). Those three are
#: exactly where a `Cell` could have diverged -- `Cell.jobs` defaults to 0,
#: one worker per CPU, which would have run the arms without the monkeypatch.
def _expected(character, archetype, runs):
    return (
        (character, archetype, archetype, draft.assigned_policy, runs,
         shop.SEED),
        dict(grant_relics=True, grant_potions=True, n_acts=3, jobs=1,
             route_name="hunter", force_cards=None),
    )


@pytest.mark.parametrize("character,archetype", shop.CHARACTERS)
@pytest.mark.parametrize("companions", (False, True))
def test_the_cell_passes_exactly_what_the_direct_call_passed(
        monkeypatch, character, archetype, companions):
    """Argument for argument, on every arm of the sweep. This is the claim the
    registration window would not let (b) make on its own: if any of these
    moved, the registered seed would not play out the way the graded M14 read
    played it out."""
    seen = {}

    def spy(*args, **kwargs):
        seen["args"] = args
        seen["kwargs"] = kwargs
        return []

    monkeypatch.setattr(model, "run_many", spy)
    assert shop.arm(character, archetype, 7, companions=companions) == []
    assert (seen["args"], seen["kwargs"]) == _expected(character, archetype, 7)


def test_the_arm_restores_visit_shop_even_though_it_now_runs_a_cell(
        monkeypatch):
    """The monkeypatch is the ONE variable between the arms, and it is still
    installed around the run and taken off afterwards -- a `Cell` in the middle
    does not change that."""
    import tier05.shop as shop_mod
    original = shop_mod.visit_shop
    inside = {}

    monkeypatch.setattr(model, "run_many",
                        lambda *a, **k: inside.setdefault(
                            "patched", shop_mod.visit_shop is not original)
                        or [])
    shop.arm("klee", "demolition", 3, companions=True)

    assert inside["patched"] is True
    assert shop_mod.visit_shop is original


def test_each_arm_cell_names_its_own_arm():
    """`companions` cannot be a `Cell` field, so it lives in the NAME. Two arms
    that stamped the same line would be an on-arm row claiming to be the
    control -- the mislabelling `Cell.but` renames to prevent."""
    names = {(c, a, on): shop.arm_cell(c, a, 500, companions=on).name
             for c, a in shop.CHARACTERS for on in (False, True)}
    assert len(set(names.values())) == len(names)
    for (c, a, on), name in names.items():
        assert c in name and a in name
        assert ("companions=on" if on else "companions=off") in name


def test_every_arm_cell_keeps_the_base_cells_run_settings():
    """The only declared deltas are character, archetype, runs and the name.
    A cell that quietly moved seed, route, policy, loadout, acts or jobs would
    be a different world wearing this instrument's header."""
    base = shop.BASE_CELL
    for c, a in shop.CHARACTERS:
        for on in (False, True):
            cell = shop.arm_cell(c, a, 500, companions=on)
            assert (cell.seed, cell.route, cell.policy, cell.realistic,
                    cell.n_acts, cell.jobs, cell.pilot_override,
                    cell.force_cards) == (
                base.seed, base.route, base.policy, base.realistic,
                base.n_acts, base.jobs, base.pilot_override, base.force_cards)
            # The pilot the plan resolves to is what the direct call hardcoded
            # by passing `archetype` twice; `resolve_plan` agreeing is what
            # makes the reroute a no-op rather than a re-aim.
            assert cell.pilot == a
