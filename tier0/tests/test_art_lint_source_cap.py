"""L14 in tools/art_lint.py: at most two cards per source in one character's
card partition, and the quote rule in `art_fetch.rawname`.

Kokomi art pass 2 (2026-09-29) replaced 32 prototype portraits that were nine
wiki renders cut three or four ways each -- mostly legs and torso, because a
tall render has one head. L14 keeps that from coming back. Both directions are
pinned, synthetic rows run everywhere (`pixel_check=False`, as in
test_art_lint_source_group.py), and the real-plan half reads the tracked
`art/plan.tsv`.
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

import art_lint  # noqa: E402
from art_fetch import rawname, read_plan  # noqa: E402

KOKOMI = "ImageGen/images/cards/kokomi"


def row(asset_id, title, *, focus, part=KOKOMI, register="splash",
        mode="cover"):
    return {
        "asset_id": asset_id, "out": f"{part}/{asset_id}.png",
        "w": 500, "h": 380, "mode": mode, "focus": focus,
        "pick": "shortlist", "rank": 1, "source": "png", "title": title,
        "frame": None, "register": register, "source_group": "kokomi_pool",
    }


@pytest.fixture(autouse=True)
def _no_clip_probing(monkeypatch):
    """L6 reads real source files off disk; irrelevant here."""
    monkeypatch.setattr(art_lint, "clip_warnings", lambda effective: [])


def _l14(rows):
    return [p for p in art_lint.lint(rows, pixel_check=False)
            if p.startswith("L14")]


def test_two_cards_on_one_source_is_legal():
    assert _l14([
        row("proto_kk_a", "Some Render.png", focus="y0.20"),
        row("proto_kk_b", "Some Render.png", focus="y0.60"),
    ]) == []


def test_three_cards_on_one_source_is_L14_even_at_three_crops():
    problems = _l14([
        row("proto_kk_a", "Some Render.png", focus="y0.20"),
        row("proto_kk_b", "Some Render.png", focus="y0.50"),
        row("proto_kk_c", "Some Render.png", focus="y0.80"),
    ])
    assert len(problems) == 1, problems
    assert "3 cards" in problems[0] and "proto_kk_c" in problems[0]


def test_stickers_count():
    problems = _l14([
        row("proto_kk_a", "Sticker.png", focus="contain@0.08",
            mode="cover_autocrop", register="sticker"),
        row("proto_kk_b", "Sticker.png", focus="contain@0.10",
            mode="cover_autocrop", register="sticker"),
        row("proto_kk_c", "Sticker.png", focus="contain@0.12",
            mode="cover_autocrop", register="sticker"),
    ])
    assert len(problems) == 1, problems


def test_partitions_are_per_character_and_per_prototype_flag():
    """Two in one character's folder plus one in another's is fine, and so is
    a prototype pair beside a shipped card on the same source."""
    assert _l14([
        row("proto_kk_a", "Shared.png", focus="y0.20"),
        row("proto_kk_b", "Shared.png", focus="y0.60"),
        row("proto_fs_c", "Shared.png", focus="y0.40",
            part="ImageGen/images/cards/furina"),
        row("shipped_d", "Shared.png", focus="y0.30"),
    ]) == []


def test_the_companion_folder_is_not_one_characters_partition():
    """Guest characters keep one source family at three crops (L7's job)."""
    part = "ImageGen/images/cards/companions"
    assert _l14([
        row("chevreuse_a", "Chevreuse Wish.png", focus="y0.2", part=part),
        row("chevreuse_b", "Chevreuse Wish.png", focus="y0.5", part=part),
        row("chevreuse_c", "Chevreuse Wish.png", focus="y0.8", part=part),
    ]) == []


def test_allow_list_suppresses_only_its_own_entry():
    title = "Sangonomiya Kokomi Card.png"
    assert (KOKOMI, False, title) in art_lint.KNOWN_SOURCE_CONCENTRATION
    shipped = [row(f"shipped_{i}", title, focus=f"y0.{i}") for i in range(1, 4)]
    assert _l14(shipped) == []
    proto = [row(f"proto_kk_{i}", title, focus=f"y0.{i}") for i in range(1, 4)]
    assert len(_l14(proto)) == 1


def test_no_prototype_partition_is_allow_listed():
    """Kokomi's live kit, and every prototype kit, passes with no exception."""
    assert not [e for e in art_lint.KNOWN_SOURCE_CONCENTRATION if e[1]]


def test_real_plan_passes_and_the_allow_list_is_not_stale():
    rows = read_plan()
    effective = [r for r in rows if "/cards/" in r["out"]
                 and (r["pick"] == "auto" or r["rank"] == 1)]
    assert art_lint.source_concentration(effective) == []
    assert art_lint.stale_source_concentration(rows) == []


def test_stale_entry_is_reported():
    """An entry whose source has fallen to two cards must be deleted."""
    rows = [row("shipped_a", "Sangonomiya Kokomi Card.png", focus="y0.2")]
    stale = art_lint.stale_source_concentration(rows)
    assert any("Sangonomiya Kokomi Card.png" in s for s in stale), stale


def test_rawname_drops_double_quotes():
    """Windows cannot hold a '"' in a filename; the saved file has none."""
    title = ('Character Teaser - "Sangonomiya Kokomi- The Ocean\'s Will" '
             'Wallpaper 1.png')
    assert rawname(title) == ("Character_Teaser_-_Sangonomiya_Kokomi-_The_"
                              "Ocean's_Will_Wallpaper_1.png")
