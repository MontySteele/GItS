"""The sim's shipped Fanfare meter is gone (2026-10-19).

The Stage retired it for Furina, the only character that carried it
(`stage_retires_the_shipped_meters` refused every gain), so the meter sat at
0 and only its decay and snapshot events ran. Furina's live Fanfare is the
Stage's (`furina_tide.Ftd.fanfare`, read through `furina_stage.fanfare`), and
nothing here touches it.
"""

from __future__ import annotations

import dataclasses

import pytest

from tier0.content import loader
from tier0.engine import combat, effects, resources
from tier0.engine.state import Player
from tier0.tests.conftest import make_enemy


def test_the_player_carries_no_shipped_meter_fields():
    names = {f.name for f in dataclasses.fields(Player)}
    assert not names & {"fanfare", "fanfare_cap", "fanfare_cap_base",
                        "fanfare_cap_hp", "fanfare_floor"}


def test_the_meter_ops_predicate_and_rider_are_gone():
    for op in ("gain_fanfare_floor", "raise_fanfare_cap", "crash_fanfare",
               "drain_fanfare"):
        assert op not in effects.OPS, op
    assert not effects.is_known_predicate("fanfare_at_least_6")
    with pytest.raises(ValueError):
        effects._bonus_formula(None, "1_per_4_fanfare")


def test_resources_keeps_only_the_hp_loss_hook():
    public = {n for n in vars(resources) if not n.startswith("_")
              and callable(getattr(resources, n))
              and getattr(getattr(resources, n), "__module__", "")
              == resources.__name__}
    assert public == {"note_player_hp_loss"}


def test_a_furina_fight_runs_on_the_stage_fanfare_alone():
    """HP lost still prints the Stage's Fanfare (`furina_tide.on_hp_loss`,
    behind the same funnel), and no shipped-meter event is emitted."""
    p = loader.build_player("furina")
    enemy = make_enemy(hp=400, intents=[{"kind": "attack", "amount": 9}])

    def pilot(s):
        return None                               # end every turn

    st = combat.run_fight(p, [enemy], pilot, seed=3)
    kinds = {e["event"] for e in st.log}
    assert "ftd_gain" in kinds
    assert not kinds & {"fanfare_turn", "fanfare_decay", "gain_fanfare",
                        "fanfare_read", "fanfare_floor_granted"}
