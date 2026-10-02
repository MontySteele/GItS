"""Pass-3 ruling verification (docs/archive/pass2-rulings-round3.md)."""

from tier0 import constants as C
from tier0.content import loader


def test_the_retired_band_system_cannot_quietly_regrow():
    """R204 deleted `deck_bands` / `stale_bands` -- both accessors and all
    three characters' data, roster-wide, with no replacement bands ratified.
    Re-adding a per-axis band gate means deleting this test, and deleting it
    means reading why it is here. (`winrate_bands` is a DIFFERENT system and
    the ruling leaves it standing, so it is asserted present.)
    """
    assert not hasattr(loader, "deck_bands")
    assert not hasattr(loader, "stale_bands")
    assert hasattr(loader, "winrate_bands")
    for character in ("klee", "furina", "kokomi"):
        raw = loader._character_index()[character]
        assert "deck_bands" not in raw, character
        assert "stale_bands" not in raw, character


def test_splash_proc_cap_armed_and_functional():
    # ARMED (was dormant round 3) by the errata/M5 triage ruling 1: the
    # sanctioned demolition ceiling knob, codified in sheet v0.4.
    from tier0.engine import effects
    from tier0.engine.state import Bomb
    from tier0.tests.conftest import make_enemy, make_state
    assert C.DETONATION_SPLASH_PROC_CAP == 3

    st = make_state(enemies=[make_enemy(hp=200, name="a"),
                             make_enemy(hp=200, name="b")])
    st.player.powers["detonation_splash"] = 3
    st.splash_procs_this_turn = 0
    st.enemies[0].bombs = [Bomb(damage=5) for _ in range(5)]
    effects.detonate_bombs(st, st.enemies[0])
    splashes = [e for e in st.log
                if e["event"] == "damage"
                and e.get("source") == "detonation_splash"]
    # 5 detonations, cap 3 -> 3 procs x 2 enemies = 6 splash events
    assert len(splashes) == 6
