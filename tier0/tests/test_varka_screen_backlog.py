"""BACKLOG, the Varka screen (wave 2026-10-12), three parts:

(a) Sayu's random Swirl on an enemy with no aura: the played line says the
    Swirl did nothing (`ResolutionLedger.NoteAnemoApplication` now hears an
    Anemo HIT too, at `KleeElementalHooks.BeforeDamageReceived`).
(b) Amber: Sharpshooter's "if the enemy already has Pyro" is read once, when
    the card is played, before its first hit; a reaction that eats the Pyro
    mid-card does not cancel the second hit. Both engines already snapshot at
    play start; this pins it.
(c) Cycle of Seasons' damage gets a line of its own on the played page
    (`ResolutionLedger.HitsBy`, the hit's `by`).

C# twin: `VarkaBacklogDisplayTests`. NOTHING MEASURED HERE IS QUOTABLE
(R215 B): shape assertions.
"""
from __future__ import annotations

from understudy import blindplay_render
from understudy.blindplay_notes import (RESOLUTION_NO_AURA_HIT,
                                        RESOLUTION_NO_AURA)

from tier0.tests import test_varka_expansion as T


def _row(hits, **extra):
    row = {"card": "Sayu — Yoohoo Art: Fuuin Dash", "hits": hits,
           "applied": [], "killed": [], "oath": []}
    row.update(extra)
    return row


def _hit(target, amount, by="", seq=None):
    return {"target": target, "amount": amount, "blocked": 0,
            "combat_id": "1", "killed": False, "on_player": False,
            "source": "", "self": False, "seq": seq, "by": by}


# ---- (a) ---------------------------------------------------------------------

def test_an_anemo_hit_on_a_bare_enemy_says_the_swirl_did_nothing():
    lines = blindplay_render._resolution_lines(
        [_row([_hit("Slime", 8)], swirl_no_aura=1, swirl_on_aura=0)])
    assert RESOLUTION_NO_AURA_HIT in lines
    assert any("**Slime** -- 8" in line for line in lines)
    # One that found an aura says nothing of the kind.
    lines = blindplay_render._resolution_lines(
        [_row([_hit("Slime", 8)], swirl_no_aura=1, swirl_on_aura=1)])
    assert RESOLUTION_NO_AURA_HIT not in lines
    # The hitless line keeps its own sentence (Sucrose on a bare board).
    lines = blindplay_render._resolution_lines(
        [_row([], swirl_no_aura=1, swirl_on_aura=0)])
    assert RESOLUTION_NO_AURA in lines


# ---- (b) ---------------------------------------------------------------------

def test_sharpshooter_reads_pyro_once_before_its_first_hit():
    """The enemy wears Pyro; Kyouka turns the first hit Hydro, whose
    Vaporize eats the Pyro mid-card. The second hit still lands: 18 (12 x
    1.5) and then 12 on the Hydro the Vaporize left."""
    T._reset()
    try:
        st = T._state(enemies=[T._enemy(aura="pyro")])
        st.player.powers["mi_kyouka"] = 2
        T._play(st, T._vk("amber_sharpshooter"))
        assert st.enemies[0].aura != "pyro"
        assert st.enemies[0].hp == 100 - 18 - 12
        # And no Pyro at the start: one hit, whatever the first hit leaves.
        st = T._state()
        T._play(st, T._vk("amber_sharpshooter"))
        assert st.enemies[0].hp == 100 - 8
    finally:
        T._reset()


# ---- (c) ---------------------------------------------------------------------

def test_a_powers_hit_inside_the_play_is_labelled_not_numbered():
    lines = blindplay_render._resolution_lines([_row(
        [_hit("Slime", 9, seq=1), _hit("Mite", 7, by="Cycle of Seasons",
                                       seq=2), _hit("Slime", 9, seq=3)])])
    assert "  Cycle of Seasons: **Mite** -- 7" in lines
    assert "  1. **Slime** -- 9" in lines
    assert "  2. **Slime** -- 9" in lines
