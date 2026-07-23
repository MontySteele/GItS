"""L1/L7 source_group semantics in tools/art_lint.py.

The Furina pass needs one dedupe rule to mean two opposite things
(requirements 9.3): Chevreuse's three cards SHOULD share a source family and
differ by crop, while two unrelated cards sharing a source is the original L1
defect. `source_group` is what separates those cases, so both directions are
pinned here -- a rule that only ever gets exercised in its passing direction
is not a gate.
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

import art_lint  # noqa: E402


def row(asset_id, title, *, mode="cover_autocrop", focus="cover@0.06",
        group=None, register="splash", out=None):
    return {
        "asset_id": asset_id,
        "out": out or f"ImageGen/images/cards/companions/{asset_id}.png",
        "w": 500, "h": 380,
        "mode": mode, "focus": focus,
        "pick": "auto", "rank": 1,
        "source": "png", "title": title, "frame": None,
        "register": register, "source_group": group,
    }


@pytest.fixture(autouse=True)
def _no_clip_probing(monkeypatch):
    """L6 reads real source files off disk; irrelevant here and absent in CI."""
    monkeypatch.setattr(art_lint, "clip_warnings", lambda effective: [])


def test_sibling_reuse_with_different_crops_is_legal():
    """The intended Companion pattern: one family, three crops."""
    problems = art_lint.lint([
        row("chevreuse_interdiction_fire", "Chevreuse Wish.png",
            focus="cover@0.02", group="chevreuse"),
        row("chevreuse_vanguards_valor", "Chevreuse Wish.png",
            focus="cover@0.10", group="chevreuse"),
        row("chevreuse_bursting_grenades", "Chevreuse Wish.png",
            mode="cover", focus="top", group="chevreuse"),
    ])
    assert problems == [], problems


def test_sibling_reuse_with_identical_crop_is_L7():
    """Same family, same crop = the same picture printed on two cards."""
    problems = art_lint.lint([
        row("lynette_box_trick", "Lynette Wish.png", group="lynette"),
        row("lynette_enigmatic_feint", "Lynette Wish.png", group="lynette"),
    ])
    assert len(problems) == 1, problems
    assert problems[0].startswith("L7 lynette_enigmatic_feint")
    assert "IDENTICAL crop" in problems[0]


def test_cross_family_reuse_is_still_L1():
    """A group must not become a licence to share across characters."""
    problems = art_lint.lint([
        row("chevreuse_interdiction_fire", "Fontaine Group Wish.png",
            focus="cover@0.02", group="chevreuse"),
        row("lynette_box_trick", "Fontaine Group Wish.png",
            focus="cover@0.10", group="lynette"),
    ])
    assert len(problems) == 1, problems
    assert problems[0].startswith("L1 lynette_box_trick")
    assert "cross-family reuse is illegal" in problems[0]


def test_ungrouped_rows_keep_strict_L1():
    """Furina's own cards are ungrouped ON PURPOSE.

    They are all one character, so grouping by character would have legalised
    exactly the reuse requirements sec.2 forbids ("one effective source should
    not serve two unrelated Furina cards"). Blank source_group must therefore
    stay strict even when the crops differ.
    """
    problems = art_lint.lint([
        row("high_tide", "Furina Wish.png", focus="cover@0.02",
            out="ImageGen/images/cards/furina/high_tide.png"),
        row("crashing_waves", "Furina Wish.png", focus="cover@0.10",
            out="ImageGen/images/cards/furina/crashing_waves.png"),
    ])
    assert len(problems) == 1, problems
    assert problems[0].startswith("L1 crashing_waves")


def test_one_sided_group_does_not_pair():
    """A grouped row colliding with an ungrouped one is still L1."""
    problems = art_lint.lint([
        row("dahlia_favonian_favor", "Dahlia Wish.png", group="dahlia"),
        row("deep_breath", "Dahlia Wish.png", focus="top",
            out="ImageGen/images/cards/furina/deep_breath.png"),
    ])
    assert len(problems) == 1, problems
    assert problems[0].startswith("L1 deep_breath")
