"""`art_source_census` — the SLOT arithmetic, pinned in both directions (`EB-121`).

The census exists because a hand-counted art pool cannot be re-derived, only
re-guessed: `kokomi-art-pass-requirements.md` §2 priced her at "33 sources / 70
slots" on 2026-07-25, `EB-69` moved her faces 62 -> 76, and the difference was
read as a 6-slot DEFICIT with no way to check it. A tool that replaces a guess
is only worth having if the tool itself is pinned, so this file pins the two
claims the recount actually rests on:

1. **The anchor grid reproduces the SHIPPED plan.** That is what licenses using
   the grid to price the sources nobody has shortlisted yet. Six of the eight
   multi-anchor Kokomi sources come out anchor-for-anchor identical, and this
   file asserts each one -- if the geometry ever drifts, these fail rather than
   quietly re-pricing the pool.
2. **The 70-slot figure reconciles at `--reuse-cap 4`.** This is the whole
   finding: the deficit was an artifact of an unstated CROP-REUSE BUDGET, not
   of the inventory. If that reconciliation ever stops holding, the doc's
   history section is wrong and should be re-derived, not patched.

**Bare-clone contract**, same as `test_art_lint_full_set`: everything here
needs `art/plan.tsv` (tracked) but NOT `art/raw/` (gitignored Tier F) -- the
census falls back to its `NATIVE_DIMS` table and says which it used, so these
run in CI. The tests that would need pixels are not written.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

pytest.importorskip("yaml")
import art_source_census as census  # noqa: E402

CARD_W, CARD_H = 500, 380

pytestmark = pytest.mark.skipif(
    not (REPO / "art" / "plan.tsv").exists(),
    reason="art/plan.tsv absent -- nothing to price",
)


def test_centre_range_matches_the_two_ranges_the_doc_states():
    """§2, "Anchors are computed, not chosen", names both of these by hand."""
    axis, _, lo, hi = census.centre_range(4900, 5700, CARD_W, CARD_H)
    assert axis == "y"
    assert (round(lo, 2), round(hi, 2)) == (0.33, 0.67)          # Portrait

    axis, _, lo, hi = census.centre_range(2250, 2250, CARD_W, CARD_H)
    assert axis == "y"
    assert (round(lo, 2), round(hi, 2)) == (0.38, 0.62)          # Intro Card


def test_a_source_wider_than_the_card_ratio_crops_on_x():
    """The freedom is on whichever axis the fill scale does NOT saturate.

    Getting this backwards would price a landscape namecard strip against its
    height, which has no freedom at all, and report one slot where there are
    five.
    """
    axis, _, lo, hi = census.centre_range(2048, 1024, CARD_W, CARD_H)   # Wish
    assert axis == "x"
    assert lo < 0.5 < hi


# Source -> the anchors the SHIPPED plan actually uses at rank 1. Typed out
# rather than read back from plan.tsv on purpose: reading them back would make
# the test tautological, and the claim under test is that the GRID and the
# SHIPPED PLAN agree.
SHIPPED_ANCHORS = {
    (4900, 5700, None): [0.33, 0.41, 0.5, 0.59, 0.67],       # Portrait
    (2250, 2250, None): [0.38, 0.5, 0.62],                   # Introduction Card
    (1080, 1920, (0.24, 0.74)): [0.24, 0.34, 0.44, 0.54, 0.64, 0.74],  # Card
    (964, 1736, None): [0.21, 0.33, 0.44, 0.56, 0.67, 0.79],  # Game
    (700, 2646, None): [0.1, 0.26, 0.42, 0.58, 0.74, 0.9],   # Showcase
    (420, 720, None): [0.22, 0.33, 0.44, 0.56, 0.67, 0.78],  # tcg Character Card
}


@pytest.mark.parametrize("geom,expected", sorted(SHIPPED_ANCHORS.items()))
def test_grid_reproduces_the_shipped_anchors(geom, expected):
    w, h, restrict = geom
    _, _, lo, hi = census.centre_range(w, h, CARD_W, CARD_H)
    if restrict:
        lo, hi = max(lo, restrict[0]), min(hi, restrict[1])
    assert census.anchor_grid(lo, hi, census.REUSE_CAP) == expected


def test_card_png_needs_its_restricted_range_to_match_what_shipped():
    """The red half of the row above: WITHOUT the wordmark restriction the
    grid for `Sangonomiya Kokomi Card.png` is a different set of anchors, and
    `RESTRICTED_RANGE` is doing real work rather than decorating the module."""
    _, _, lo, hi = census.centre_range(1080, 1920, CARD_W, CARD_H)
    assert census.anchor_grid(lo, hi, census.REUSE_CAP) != \
        SHIPPED_ANCHORS[(1080, 1920, (0.24, 0.74))]
    assert "Sangonomiya Kokomi Card.png" in census.RESTRICTED_RANGE


@pytest.mark.parametrize("focus,expected", [
    ("y0.33", 0.33),
    ("x0.62", 0.62),
    ("y0.5@1.5", 0.5),          # zoom suffix is not part of the anchor
    ("cover@0.06", None),       # cover_autocrop consumes the whole source
    ("contain@0.10", None),
    ("center", None),
    ("top", None),
])
def test_parse_anchor_reads_every_spelling_the_plan_uses(focus, expected):
    assert census.parse_anchor(focus) == expected


def _totals(reuse_cap):
    recs, _, _ = census.census("kokomi", None, reuse_cap)
    by_reg = {}
    for r in recs:
        if r["slots"]:
            by_reg[r["register"]] = by_reg.get(r["register"], 0) + r["slots"]
    return by_reg, sum(by_reg.values())


def test_the_doc_s_70_slot_figure_reconciles_at_a_reuse_cap_of_four():
    """THE finding. 38 splash + 12 tcg + 5 item + 15 sticker = 70 is the census
    run at `--reuse-cap 4` -- so the 2026-08-23 "6-slot deficit" was a stale
    CROP-REUSE BUDGET and never a fact about the source pool. The extra 4 are
    Bake-Kurage Summon, the 34th source the 2026-07-25 table omitted while the
    plan was already claiming it."""
    by_reg, total = _totals(4)
    assert by_reg["splash"] == 38
    assert by_reg["tcg"] == 12
    assert by_reg["item"] == 5
    assert by_reg["sticker"] == 15
    assert by_reg["splash"] + by_reg["tcg"] + by_reg["item"] + by_reg["sticker"] == 70
    assert by_reg["vfx"] == 4                     # Bake-Kurage, capped at 4
    assert total == 74


def test_the_shipped_budget_of_six_clears_the_bill():
    """And the budget the plan ALREADY SHIPS is 6, which is +17 against 76
    faces. A cap of 4 cannot be restored without re-cropping shipped art."""
    _, total = _totals(census.REUSE_CAP)
    assert census.REUSE_CAP == 6
    assert total == 93
    assert total - len(census.faces("kokomi")) == 17


def test_vfx_is_a_dead_register_except_for_bake_kurage():
    """§2's "single most important finding", asserted rather than remembered:
    every other piece of her kit art fails L8's both-dimensions test."""
    recs, _, _ = census.census("kokomi", None, census.REUSE_CAP)
    vfx = {r["title"]: r["slots"] for r in recs if r["register"] == "vfx"}
    assert vfx, "the plan must still carry vfx rows for this to mean anything"
    assert vfx.pop("Bake-Kurage Summon.png") > 1
    assert set(vfx.values()) == {0}


def test_single_anchor_registers_are_worth_exactly_one_slot():
    """item and sticker are rendered `contain` / `cover_autocrop` -- the whole
    source, one picture. Pricing them by geometry would invent headroom that
    cannot be cropped."""
    recs, _, _ = census.census("kokomi", None, census.REUSE_CAP)
    for r in recs:
        if r["register"] in ("item", "sticker") and r["slots"]:
            assert r["slots"] == 1, r["title"]
