"""EB-225: the prototype patch-scope lint, and the four doors it shuts.

R225 item 6 (M66 pick 2) kept the SINGLE `PROTOTYPE_CARDS` switch and bought
the guard it does not give with a lint instead. The lint is only worth having
if it BITES, so the fixtures here are red first and green second, in both
directions:

  * a patch that reaches a character predicate and the guarded seat accessor
    is clean;
  * the same patch with the character test removed is a `(a)` finding -- this
    is `EB-194`/`EB-221`'s shape, a Kokomi patch acting on a Klee seat under
    one flag;
  * the same patch calling `LocalContext.GetMe` outside a `try` is a `(b)`
    finding -- this is `d217b4f`'s shape, the throw on a seatless combat that
    ended two whole blind sessions at their second Monster room;
  * a `// lint: no-seat` marker exempts, and a marker with NO REASON does not.

And two properties that are load-bearing rather than decorative: the lint
reads CODE and not prose (a docstring naming `LocalContext.GetMe` is not a
call), and the shipped prototype tree is green under the real gate -- so a
regression on that tree shows up here as well as in the lint lane.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]

_spec = importlib.util.spec_from_file_location(
    "lint_prototype_patch_scope", REPO / "tools" / "lint_prototype_patch_scope.py")
assert _spec and _spec.loader
lint = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = lint
_spec.loader.exec_module(lint)


@pytest.mark.parametrize("name", sorted(lint.FIXTURES))
def test_fixture(name: str) -> None:
    """Each fixture says exactly what it is meant to say, and nothing else."""
    source, wanted = lint.FIXTURES[name]
    hits = lint.fixture_findings(source)
    if not wanted:
        assert hits == [], f"{name} must be clean"
        return
    assert len(hits) == len(wanted), hits
    for want in wanted:
        assert any(want in h for h in hits), hits


def test_the_patch_is_found_at_all() -> None:
    """A lint that parses nothing is green for the wrong reason.

    The green fixture must produce a PATCH, not merely no findings: every
    other assertion in this module is worthless if the scanner silently sees
    zero patches, which is exactly what a broken declaration regex looks like.
    """
    units = lint.scan_source(lint.FIXTURES["green"][0], "fixture.cs")
    assert [u.name for u in units] == ["A_Patch.Postfix"]
    assert {m.name for m in units[0].reached} >= {"Postfix", "DiscardAll",
                                                  "TryGetMe"}, \
        "the effective body must follow the patch's own calls -- every patch " \
        "on this surface is a one-line delegation, so a body-only lint reads " \
        "nothing"


def test_prose_is_not_code() -> None:
    """`KurageMemoryCard`'s own docstring names the accessor it forbids."""
    src = lint.FIXTURES["comment-only"][0]
    assert "LocalContext.GetMe" in src
    assert lint.fixture_findings(src) == []


def test_marker_stops_at_the_end_of_its_line() -> None:
    """A reasonless marker may not adopt the next line as its reason.

    `\\s` crosses a newline, so the first draft's marker regex read the
    `[HarmonyPatch]` attribute below a bare `// lint: no-seat` as the reason
    and the exemption went through silently -- the one failure mode a marker
    exists to prevent.
    """
    units = lint.scan_source(lint.FIXTURES["marked-no-reason"][0], "f.cs")
    assert len(units) == 1
    assert "HarmonyPatch" not in (units[0].marker or "")


def test_the_shipped_prototype_tree_is_green() -> None:
    """The gate's own invocation, over the three quarantined directories."""
    hits, markers, count = lint.scan()
    assert hits == [], hits
    assert count >= 3, "the prototype directories must still hold patches"
    # Every exemption is visible, and there are THREE: the pile-screen
    # teardown, the Kokomi Plan strip's teardown (whose character scope is one
    # call in, on the guarded seat resolver), and the Kokomi arm's target-type
    # registration, which runs at `ModelDb.Init` before any run exists. A
    # FOURTH appearing here is a review question.
    assert len(markers) == 3, markers


def test_registered_in_the_ci_lane() -> None:
    """A lint nobody runs is not a lint (run_lints' own coverage rule)."""
    spec = importlib.util.spec_from_file_location(
        "run_lints", REPO / "tools" / "run_lints.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    row = [l for l in mod.REGISTRY
           if l.script == "tools/lint_prototype_patch_scope.py"]
    assert len(row) == 1 and row[0].lane == "ci", row
    assert mod.registry_gaps() == []
