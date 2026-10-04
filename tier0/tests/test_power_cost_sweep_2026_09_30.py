"""POWER COST SWEEP (2026-09-30) -- the sim engine's pins for the rows whose
EFFECT moved, not just their cost.

[USER]: "can we do a sweep over the current card pools and break them up a
bit so it's less of a standard? Alter the effects to rebalance at a different
energy level, basically (either the higher or the lower)".

Provenance: docs/notes/prototype-surface-provenance.md, "Power cost sweep,
2026-09-30". NOTHING MEASURED ON A PROTOTYPE IS QUOTABLE (R215 B).
"""

from __future__ import annotations

import random

from tier0.content import loader, upgrades, yaml_memo
from tier0.engine import furina_stage as FS
from tier0.engine import kokomi_plan
from tier0.engine import varka_oath as V
from tier0.engine.state import CombatState, Enemy, Player
from tier0.tests.test_kokomi_plan import kokomi_state, overhaul  # noqa: F401
from tier0.tests.test_varka_oath import _led, _state as _varka_state  # noqa: F401
from tier0.tests.test_varka_oath import varka  # noqa: F401


def _row(cid):
    return loader.get_card(cid)


def _sheet():
    rows = yaml_memo.safe_load(
        (loader.DOCS_DIR / "prototype-surface.yaml").read_text(
            encoding="utf-8"))
    return {r["id"]: r for r in rows}


def _up(cid):
    return upgrades.apply_upgrade(loader.get_card(cid))


def _power_of(card):
    return next(fx for fx in card.effects if fx.get("op") == "apply_power")


def test_the_long_game_upgrade_installs_the_drawing_twin(overhaul):
    assert _power_of(_row("proto_kk_the_long_game"))["power"] == \
        kokomi_plan.LONG_GAME
    up = _up("proto_kk_the_long_game")
    assert _power_of(up)["power"] == kokomi_plan.LONG_GAME_PLUS
    assert up.cost == 1
    st = kokomi_state()
    st.player.draw_pile = [loader.get_card("proto_kk_nip") for _ in range(3)]
    st.player.hand = []
    st.player.powers[kokomi_plan.LONG_GAME_PLUS] = 1
    st.player.energy = 3
    kokomi_plan.long_game(st, 1)
    assert st.player.energy == 4
    assert len(st.player.hand) == 1
    kokomi_plan.long_game(st, 2)                    # two waiting: nothing
    assert (st.player.energy, len(st.player.hand)) == (4, 1)


def test_sworn_brotherhood_base_gains_the_current_element_only(varka):
    row = _row("proto_vk_sworn_brotherhood")
    assert row.cost == 1
    assert _power_of(row)["power"] == V.SWORN_BROTHERHOOD_CURRENT
    assert _power_of(_up("proto_vk_sworn_brotherhood"))["power"] == \
        V.SWORN_BROTHERHOOD
    st = _varka_state(n=1, fang=False)
    led = _led(st)
    before = dict(led.oath)
    led.current = None
    st.player.powers[V.SWORN_BROTHERHOOD_CURRENT] = 1
    V.turn_start(st)
    assert led.oath == before                       # no current: nothing
    led.current = "hydro"
    V.turn_start(st)
    assert led.oath == {**before, "hydro": before["hydro"] + 1}
