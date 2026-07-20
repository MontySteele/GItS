"""Errata verification (furina-predesign-notes.md Part 1 + pass-3
ratification closeout): Frozen v2, companion healing Exhaust, the
control_uptime/SUPPORT_CARRY detector, and the ratified winrate bands.

The 1000-fight band tests are the v0.1 regression lock — they ARE slow;
that's the ratification's process fix (bands only mean anything >=1000).
"""

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.harness import metrics
from tier0.harness.runner import run_battery, score_character
from tier0.tests.conftest import make_enemy, make_state

BAND_FIGHTS = 1000
SEED = 42


# --- companion healing errata (sheet v0.3.1) ---

def test_companion_heals_exhaust():
    # Healing-grade policy (principles v1.5): repeatable true healing is
    # not a thing companions provide. Barbara/Bennett heals now Exhaust.
    from tier0.engine.combat import play_card
    for cid in ("barbara_melody", "bennett_fantastic_voyage"):
        card = loader.get_card(cid)
        assert card.exhaust, cid
        st = make_state()
        st.player.hp = 40
        st.player.energy = 3
        st.player.hand.append(card)
        play_card(st, card)
        assert card in st.player.exhaust_pile


# --- control_uptime / SUPPORT_CARRY (§2.2a) ---

def _freeze_via_companion(st):
    """Seed hydro, then freeze with a companion cryo attack."""
    from tier0.engine import effects
    e = st.enemies[0]
    effects.resolve_card(st, loader.get_card("dahlia_sacramental_shower"))
    st.player.hand.append(loader.get_card("kaeya_frostgnaw"))
    effects.resolve_card(st, loader.get_card("kaeya_frostgnaw"))
    return e


def test_control_uptime_counts_companion_frozen_attacks():
    from tier0.engine.combat import _enemy_turn
    st = make_state(enemies=[make_enemy(hp=200)])
    e = _freeze_via_companion(st)
    assert e.frozen and e.frozen_by_companion
    e.intents = [{"kind": "attack", "amount": 8}]
    _enemy_turn(st, e)                      # halved action: 0.5 negated
    _enemy_turn(st, e)                      # normal action
    st.emit("fight_end", won=True, turns=st.turn)
    stats = metrics.extract(st, hp_start=st.player.max_hp)
    assert stats.control_negated == pytest.approx(1 - C.FROZEN_DAMAGE_MULT)
    assert stats.enemy_actions == 2
    # 0.25 uptime < 0.40 threshold: no flag on this fight.
    assert "SUPPORT_CARRY" not in stats.flags


def test_support_carry_flags_control_carried_wins():
    from tier0.engine.combat import _enemy_turn
    st = make_state(enemies=[make_enemy(hp=200)])
    e = st.enemies[0]
    e.intents = [{"kind": "attack", "amount": 8}]
    for _ in range(5):                      # every action frozen-halved
        e.frozen = True
        e.frozen_by_companion = True
        _enemy_turn(st, e)
    st.emit("fight_end", won=True, turns=st.turn)
    stats = metrics.extract(st, hp_start=st.player.max_hp)
    assert stats.control_negated / stats.enemy_actions > C.CONTROL_UPTIME_CARRY
    assert "SUPPORT_CARRY" in stats.flags


def test_klee_cannot_source_frozen_alone():
    # Klee is pyro; every Frozen in her fights is companion-sourced.
    # (Provenance sanity for the detector, not a balance claim.)
    st = make_state(enemies=[make_enemy(hp=200)])
    e = _freeze_via_companion(st)
    assert e.frozen_by_companion


# --- the frozen v0.1 median identity (regression lock) ---

# Measured post-errata at 300 fights / seed 42. Deterministic at fixed
# seed; the tolerance is headroom for benign engine changes, not noise.
V01_MEDIAN = {"A1_frontload": 4.19, "A2_scaling": 3.95, "A3_block": 2.26,
              "A4_sustain": 0.50, "A5_velocity": 3.04, "A6_utility": 3.59,
              "A7_setup_tax": 2.35}


def test_v01_median_scorecard_locked():
    rep = score_character("klee", 300, SEED)
    for ax, frozen in V01_MEDIAN.items():
        assert rep["median_scores"][ax] == pytest.approx(frozen, abs=0.3), ax


# --- ratified winrate bands (the v0.1 regression lock) ---

def test_winrate_bands_skipped_below_min_fights():
    rep = score_character("klee", 50, SEED)
    assert any("not checked" in f for f in rep["band_flags"])


def test_sheet_splash_cap_matches_engine_constant():
    # Triage ruling 1: sheet v0.4 carries the knob so the design artifact
    # is authoritative; this guard catches sheet/engine drift.
    blazing = loader.get_card("blazing_delight")
    fx = next(f for f in blazing.effects
              if f.get("power") == "detonation_splash")
    assert fx["splash_procs_per_turn"] == C.DETONATION_SPLASH_PROC_CAP


@pytest.mark.parametrize("deck,pilot,enc", [
    ("demolition_weighted", "demolition", "tank_boss"),
    ("spark_weighted", "spark", "tank_boss"),
    ("reaction_weighted", "reaction", "tank_boss"),
    ("reaction_weighted", "reaction", "gauntlet"),
])
def test_ratified_winrate_bands(deck, pilot, enc):
    bands = loader.winrate_bands("klee")
    lo, hi = bands[enc][deck]
    wr = metrics.summarize(
        run_battery("klee", deck, enc, pilot, BAND_FIGHTS, SEED))["winrate"]
    assert wr >= lo, (deck, enc, wr)
    if hi is not None:
        assert wr <= hi, (deck, enc, wr)
