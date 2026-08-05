"""Track O slice 6 — pins on `understudy.replay`'s SPOTLIGHT_FORCE handling.

Only behaviour that is UNAMBIGUOUSLY correct from the module's own contract
is pinned here (`replay.py` §"the selector channel"; the `--use-selectors`
help text: "OFF by default ... the S7 artefact must stay reproducible").

The save/restore around the replayed turn must be a save/RESTORE, not a
save/clear: it has to hand back whatever value it found, including a value
an OUTER caller (an experiment cell, `tools/archive/exp_furina_pass3.py`)
had deliberately set, and it has to do that on the raising path too. The
existing `test_understudy_replay_selectors.py` pins the None baseline; these
pin the nested case, which is the one where a save/clear would look green.
"""
from __future__ import annotations

import collections

from tier0.engine import effects

from understudy import replay


SPOTLIGHT_PAIR = ["Center Stage", "Guest Cast"]


def _spec(selectors, plays):
    fight = {
        "enemies": [{"name": "probe", "max_hp": 50}],
        "max_hp": 60,
        "hp_trajectory": [[1, 60, 0], [2, 60, 0]],
        "meters_by_turn": [[1, 0, 0, 3, 0], [2, 4, 0, 3, 0]],
        "enemy_pool_by_turn": [[1, 50], [2, 50]],
        "block_at_turn_end": [[1, 0]],
        "selectors": selectors,
        "cards_played": [],
    }
    return {
        "fight_id": "s06#f1",
        "log": "s06",
        "fight": fight,
        "turns": [{"round": 1, "hand_at_open": [], "hp_at_open": 60,
                   "plays": [{"card": c, "card_id": None, "upgraded": False,
                              "target_id": None, "target_name": None,
                              "target_hp": None, "status": "ok", "i": i}
                             for i, c in enumerate(plays)]}],
    }


def _run(spec, use_selectors):
    replay.l2_rows(spec, replay.Names(), "furina",
                   collections.Counter(), use_selectors=use_selectors)


def test_an_outer_force_survives_a_replayed_turn(monkeypatch):
    """The restore hands back what it found, not None."""
    monkeypatch.setattr(effects, "SPOTLIGHT_FORCE", "self", raising=False)
    _run(_spec([[1, "choose", 1, "Guest Cast", SPOTLIGHT_PAIR]],
               ["Stage Presence"]), True)
    assert effects.SPOTLIGHT_FORCE == "self"


def test_an_outer_force_survives_a_raising_turn(monkeypatch):
    """Same, on the path that leaks if the restore is not in `finally`."""
    def boom(*a, **kw):
        raise RuntimeError("probe")

    monkeypatch.setattr(effects, "SPOTLIGHT_FORCE", "companion", raising=False)
    monkeypatch.setattr(replay.combat, "play_card", boom)
    _run(_spec([[1, "choose", 0, "Center Stage", SPOTLIGHT_PAIR]],
               ["Stage Presence"]), True)
    assert effects.SPOTLIGHT_FORCE == "companion"


def test_without_the_flag_a_selector_log_does_not_touch_the_switch(monkeypatch):
    """`--use-selectors` OFF means the recorded answer is not consulted AND
    the diagnostic switch is not driven, on a corpus that has selectors."""
    seen = []
    real = replay.combat.play_card

    def watch(state, card):
        seen.append(effects.SPOTLIGHT_FORCE)
        return real(state, card)

    monkeypatch.setattr(effects, "SPOTLIGHT_FORCE", None, raising=False)
    monkeypatch.setattr(replay.combat, "play_card", watch)
    _run(_spec([[1, "choose", 1, "Guest Cast", SPOTLIGHT_PAIR]],
               ["Stage Presence"]), False)
    assert seen and all(v is None for v in seen)
    assert effects.SPOTLIGHT_FORCE is None
