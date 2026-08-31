"""EB-153: the power-icon lint bites on BOTH shapes, and its curation is live.

A gate is not trusted until it has been watched fail. The two shapes below are
the two halves of the row -- a power covered by nothing, and the aura path
built by concatenation -- and each is driven against SYNTHETIC input so the
failure is exercised rather than argued for. The HEAD arm then asserts the
shipped tree is green, and that the curated sets still describe it.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools import lint_power_icons as lint   # noqa: E402


def _world(**over):
    """A minimal class table plus the four injected sets, all overridable."""
    known = {
        "PowerModel": {"bases": [], "abstract": True, "static": False,
                       "file": REPO, "element": None},
        "AuraPower": {"bases": ["PowerModel"], "abstract": True,
                      "static": False, "file": REPO, "element": None},
        "PyroAuraPower": {"bases": ["AuraPower"], "abstract": False,
                          "static": False, "file": REPO, "element": "Pyro"},
    }
    world = dict(
        known=known,
        arms={"AuraPower"},
        exemptions=set(),
        plan={"ImageGen/images/powers/aura_pyro.png"},
        debt={},
        aura_icons={"Pyro": "ImageGen/images/powers/aura_pyro.png"},
    )
    world.update(over)
    return world


def test_the_clean_world_is_silent():
    """The control arm: without it, a lint that always fires would pass both
    shape tests below and mean nothing."""
    assert lint.findings(**_world()) == []


# --------------------------------------------------------------- shape one --

def test_shape_one_a_power_with_no_case_and_no_exemption_bites():
    world = _world()
    world["known"]["OrphanPower"] = {
        "bases": ["PowerModel"], "abstract": False, "static": False,
        "file": REPO, "element": None}

    out = lint.findings(**world)

    assert len(out) == 1
    assert "OrphanPower" in out[0]
    assert "no IconExempt entry" in out[0]


def test_shape_one_an_exemption_on_the_BASE_does_not_cover_a_subclass():
    """SpotlightPower is exempt as an abstract base precisely so that a new
    concrete subclass has to answer for itself -- inheriting a sibling's sigil
    is the failure the 2026-07-24 sweep was cleaning up."""
    world = _world()
    world["known"]["BasePower"] = {
        "bases": ["PowerModel"], "abstract": True, "static": False,
        "file": REPO, "element": None}
    world["known"]["NewChildPower"] = {
        "bases": ["BasePower"], "abstract": False, "static": False,
        "file": REPO, "element": None}
    world["exemptions"] = {"BasePower"}

    assert any("NewChildPower" in f for f in lint.findings(**world))


def test_shape_one_an_ARM_on_the_base_does_cover_a_subclass():
    """The other direction, because C# pattern matching really does match base
    types: the four `*AuraPower`s are covered by the `AuraPower` arm."""
    world = _world()
    world["known"]["BasePower"] = {
        "bases": ["PowerModel"], "abstract": True, "static": False,
        "file": REPO, "element": None}
    world["known"]["ChildPower"] = {
        "bases": ["BasePower"], "abstract": False, "static": False,
        "file": REPO, "element": None}
    world["arms"] = {"AuraPower", "BasePower"}

    assert lint.findings(**world) == []


def test_a_debt_row_that_has_been_paid_bites():
    """The rot rule: ICON_DEBT can only ever shrink."""
    world = _world(debt={"PyroAuraPower": "covered by the aura arm"})

    out = lint.findings(**world)

    assert any("delete the row" in f for f in out)


def test_a_debt_row_for_a_class_that_no_longer_exists_bites():
    world = _world(debt={"GonePower": "renamed away"})

    assert any("no such power class" in f for f in lint.findings(**world))


# --------------------------------------------------------------- shape two --

def test_shape_two_an_aura_element_with_no_icon_bites():
    """The concatenated path. A new aura element needs NO new switch case --
    it matches the AuraPower arm, builds `klee/powers/aura_dendro.png`, and
    resolves to nothing. There is no omission for any other gate to see."""
    world = _world()
    world["known"]["DendroAuraPower"] = {
        "bases": ["AuraPower"], "abstract": False, "static": False,
        "file": REPO, "element": "Dendro"}

    out = lint.findings(**world)

    assert len(out) == 1
    assert "aura_dendro.png" in out[0]
    assert "concatenation" in out[0]


def test_shape_two_an_icon_the_art_plan_does_not_produce_bites():
    world = _world(plan=set())

    out = lint.findings(**world)

    assert any("art/plan.tsv declares no producer" in f for f in out)


def test_shape_two_a_coverage_row_that_outlived_its_power_bites():
    world = _world(aura_icons={
        "Pyro": "ImageGen/images/powers/aura_pyro.png",
        "Geo": "ImageGen/images/powers/aura_geo.png"})

    assert any("outlived its power" in f for f in lint.findings(**world))


# --------------------------------------------------------------------- HEAD --

def test_head_is_green():
    assert lint.findings() == []


def test_the_curated_sets_still_describe_head():
    """Both sets are read off HEAD rather than trusted: a debt row naming a
    class that has moved, or an aura row for a retired element, is caught by
    the shape tests above -- this asserts the shipped values are the live ones.
    """
    known = lint.classes()
    assert set(lint.ICON_DEBT) <= set(known)
    live_elements = {row["element"] for name, row in known.items()
                     if row["element"] and not row["abstract"]}
    assert set(lint.AURA_ICONS) <= live_elements


def test_it_is_registered_in_the_ci_lane():
    """A lint nobody runs is not a lint."""
    from tools import run_lints
    assert run_lints.registry_gaps() == []
    row = next(l for l in run_lints.REGISTRY if l.name == "power-icons")
    assert row.lane == "ci"
