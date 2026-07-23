"""The ref_ironclad anchor lock, and the graceful-degradation contract for
the gitignored game_ref/ reference pool.

WHY THIS FILE EXISTS. Adding `real_ironclad` put a second character
through the same loader, the same reward pools and the same battery as the
3.0 anchor. Every archived number in the project -- the V01_MEDIAN lock,
the Furina pass reports, the Klee M-reports -- is a RATIO against
ref_ironclad's starter battery. So the anchor's behaviour has to be pinned
by something sharper than "the suite is green": test_axes asserts the
baseline scores 3.0, but it scores 3.0 against ITSELF by construction and
would keep doing so if his deck changed underneath us. These tests pin the
divisor itself.

Nothing here is skip-guarded. It must all pass on a fresh clone with no
game_ref/ directory at all -- that IS the second half of the contract.
"""

import pytest

from tier0.content import loader
from tier0.harness import metrics, runner
from tier0.harness.runner import run_battery

SEED = 7


# --- the anchor is frozen -------------------------------------------------

def test_baseline_is_still_ref_ironclad_starter():
    # runner.BASELINE is the divisor in axes.normalize(). Scoring the real
    # 87-card pool AGAINST the six-card construct is precisely the
    # experiment, so this must not drift to the new character.
    assert runner.BASELINE == ("ref_ironclad", "starter")


def test_ref_ironclad_spec_is_byte_identical():
    spec = loader._character_index()["ref_ironclad"]
    assert spec["hp"] == 80
    assert spec["starting_deck"] == ["strike"] * 5 + ["defend"] * 4 + ["bash"]
    assert spec["relic_hooks"] == ["heal_after_won_fight"]
    assert spec["packages"]["archetype_package"] == [
        "inflame_like", "inflame_like", "heavy_blade_like", "heavy_blade_like",
        "pommel_strike_like", "pommel_strike_like", "shrug_it_off_like",
        "shrug_it_off_like", "cleave_like", "metallicize_like"]
    # No archetype_decks/constraints/bands: the anchor is calibration, not
    # a designed identity. If one appears here, score_character starts
    # doing something new to the divisor.
    assert not spec.get("archetype_decks")
    assert not spec.get("constraints")


def test_ref_ironclad_battery_numbers_locked():
    """Exact, not banded: the battery is deterministic at a fixed seed, so
    the anchor moving AT ALL is a fact worth failing on. Measured
    2026-07-21 at 200 fights / seed 7, immediately before real_ironclad
    was wired in."""
    s = metrics.summarize(run_battery("ref_ironclad", "starter", "punisher",
                                      "generic", 200, SEED))
    assert s["winrate"] == pytest.approx(0.525, abs=1e-9)
    assert s["avg_turns"] == pytest.approx(9.585, abs=1e-9)


# --- absence of game_ref/ is total ---------------------------------------

@pytest.fixture
def no_game_ref(tmp_path, monkeypatch):
    """Simulate a fresh clone: game_ref/ does not exist at all.

    The indexes are lru_cached over the whole content tree, so they are
    cleared on the way in AND on the way out -- a stale index leaking into
    a later test would be a far more confusing failure than any this file
    is trying to catch.
    """
    for cache in (loader._card_index, loader._character_index):
        cache.cache_clear()
    monkeypatch.setattr(loader, "GAME_REF_DIR", tmp_path / "does_not_exist")
    yield
    for cache in (loader._card_index, loader._character_index):
        cache.cache_clear()


def test_missing_game_ref_loads_without_raising(no_game_ref):
    # The whole point: no exception, not a caught-and-swallowed one.
    assert loader._card_index()
    assert loader._character_index()


def test_missing_game_ref_means_no_such_character(no_game_ref):
    assert "real_ironclad" not in loader._character_index()
    with pytest.raises(KeyError):
        loader.build_player("real_ironclad")


def test_missing_game_ref_means_no_reference_cards(no_game_ref):
    assert not [c for c in loader._card_index() if c.startswith("ic_")]


def test_missing_game_ref_leaves_the_anchor_intact(no_game_ref):
    player = loader.build_player("ref_ironclad", "starter")
    assert player.max_hp == 80
    assert len(player.draw_pile) == 10
