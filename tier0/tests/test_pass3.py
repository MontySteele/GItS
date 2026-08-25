"""Pass-3 ruling verification (docs/archive/pass2-rulings-round3.md)."""

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.harness import metrics
from tier0.harness.runner import run_battery, score_character

# Canonical scorecard parameters. These used to be load-bearing: the per-deck
# A2 band gate was noise-marginal at low fight counts (3.59 vs 3.36 canonical)
# and passed only at this cell. R204 retired that gate, so nothing here reads
# an axis value against a threshold any more and the cell is now just a stable
# place to exercise the reporting.
FIGHTS = 300
SEED = 42


@pytest.fixture(scope="module")
def klee_report():
    return score_character("klee", FIGHTS, SEED)


def test_boom_rework_is_amp_nuke():
    boom = loader.get_card("boom_goes_the_dynamite")    # sheet v0.3
    assert boom.effects[0]["amount"] == 18               # survival sprint B
    assert boom.effects[1]["then"][0]["op"] == "repeat_this"


def test_reaction_solo_floors():
    # Ruling: co-op-primary archetype, accepted solo floors.
    tb = metrics.summarize(run_battery("klee", "reaction_weighted",
                                       "tank_boss", "reaction", 300, 42))
    ga = metrics.summarize(run_battery("klee", "reaction_weighted",
                                       "gauntlet", "reaction", 300, 42))
    assert tb["winrate"] >= 0.35, tb
    assert ga["winrate"] >= 0.75, ga


def test_median_identity_evaluation(klee_report):
    """R204 (2026-08-24) took the ASSERTIONS out of this test and left the
    REPORTING in.

    What stood here: `median_flags == []`, and a hard
    `m["A1_frontload"] > m["A2_scaling"]` on the archetype median. Both are
    gone. The ruling retired the live per-axis deck-band system as acceptance
    law and demoted the declared identity comparison with it -- seven-axis
    values and declared identity comparisons are reportable diagnostics that
    may identify something to investigate, and may not gate a merge, require
    re-banding, or justify moving a value.

    What is left is the half the ruling explicitly preserved: the comparison
    still RUNS on the median and still prints, so a declared identity cannot
    quietly stop being visible. This asserts that the reporting works. It
    never asserts what the reporting says -- a median that breaches Klee's
    frontload-over-scaling identity has to leave this suite GREEN, because
    that identity is binding DESIGN INTENT (LAW, unchanged by R204) and no
    longer a mechanical gate.
    """
    flags = klee_report["median_identity_flags"]
    assert isinstance(flags, list), flags   # she declares one, so not None
    for f in flags:
        assert "DECLARED_IDENTITY" in f and "A1_frontload>A2_scaling" in f, f


def test_the_declared_identity_is_reported_on_every_deck(klee_report):
    """R204's "demote, don't delete", executable.

    The comparison used to be emitted on every deck -- `CONSTRAINT VIOLATED`
    on starter, `warn (package deck)` elsewhere. It still is emitted on every
    deck; what left is the severity and the gate. This also pins that the
    retired vocabulary is gone from the report entirely.
    """
    assert loader.character_constraints("klee") == ["A1_frontload>A2_scaling"]
    for deck, result in klee_report["per_deck"].items():
        assert isinstance(result["identity_flags"], list), deck
        for f in result["heuristic_flags"] + result["identity_flags"]:
            assert "CONSTRAINT VIOLATED" not in f, (deck, f)
            assert "BAND EXCEEDED" not in f, (deck, f)


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
