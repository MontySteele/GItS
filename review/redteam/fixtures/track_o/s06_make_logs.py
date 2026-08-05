"""Track O / slice 6 fixture builder — synthetic soak logs for `understudy.replay`.

Writes two one-fight soak run logs into this directory:

  s06-selectors.jsonl   a P1.5 log: `fight.selectors` carries the Center
                        Stage / Guest Cast answers, and the `card_select`
                        decision rows that recorded them sit INTERLEAVED
                        with the plays (that is where the answer happened).
  s06-no-selectors.jsonl  the same fight, pre-P1.5: no selectors, no
                        card_select rows. Everything else identical.

  s06-interleave-a.jsonl / s06-interleave-b.jsonl  the same fight recorded
                        twice with the selector answered at a DIFFERENT
                        point in the turn (before vs after the first play).

Nothing here is an instrument. Run it, then drive `understudy.replay`.
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PAIR = ["Center Stage", "Guest Cast"]

FURINA_CARD = "Stage Presence"
COMPANION_CARD = "Lynette — Enigmatic Feint"


def _play(i, rnd, card, hand, target_hp=None):
    return {
        "record": "decision", "i": i, "state_type": "monster",
        "act": 1, "floor": 1, "round": rnd, "hp": 60,
        "action": {"action": "play_card", "card_index": 0},
        "names": {"verb": "play_card", "card_name": card, "card_id": None,
                  "card_upgraded": False,
                  "target_id": "e0" if target_hp is not None else None,
                  "target_name": "probe" if target_hp is not None else None,
                  "target_hp": target_hp},
        "hand": hand, "mechanical": False, "status": "ok", "message": None,
    }


def _selector_decision(i, chosen):
    """The answer, as `soak.RunDriver.post` writes it: its own decision row,
    state_type `card_select`, and `round` is None because the overlay the
    bridge builds carries no `battle` block at all."""
    return {
        "record": "decision", "i": i, "state_type": "card_select",
        "act": 1, "floor": 1, "round": None, "hp": 60,
        "action": {"action": "choose", "index": PAIR.index(chosen)},
        "names": {"verb": "choose", "card_name": chosen,
                  "screen_type": "card_select"},
        "hand": [], "mechanical": False, "status": "ok", "message": None,
    }


def _fight(selectors):
    return {
        "record": "fight", "ts": 0.0, "act": 1, "floor": 1, "kind": "monster",
        "enemies": [{"name": "probe", "max_hp": 200}],
        "max_hp": 60, "hp_start": 60, "hp_end": 40, "turns": 2,
        "outcome": "won",
        "hp_trajectory": [[1, 60, 0], [2, 55, 0], [3, 50, 0]],
        "meters_by_turn": [[1, 0, 0, 3, -1], [2, 4, 0, 3, -1], [3, 8, 0, 3, -1]],
        "enemy_pool_by_turn": [[1, 200], [2, 180], [3, 160]],
        "block_at_turn_end": [[1, 0], [2, 0]],
        "incoming_by_turn": [[1, 5, 1], [2, 5, 1]],
        "selectors": selectors,
        "cards_played": [[1, FURINA_CARD], [1, COMPANION_CARD],
                         [2, COMPANION_CARD]],
        "potions_used": [],
    }


def _write(name, rows):
    path = os.path.join(HERE, name)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    return path


def build() -> dict:
    hand1 = [FURINA_CARD, COMPANION_CARD]
    hand2 = [COMPANION_CARD]

    # --- the P1.5 log: turn 1 answers Guest Cast, turn 2 answers Center Stage.
    sel_rows = [
        _play(1, 1, FURINA_CARD, hand1, 200),
        _selector_decision(2, "Guest Cast"),
        _play(3, 1, COMPANION_CARD, hand1, 190),
        _play(4, 2, COMPANION_CARD, hand2, 180),
        _selector_decision(5, "Center Stage"),
    ]
    selectors = [[1, "card_select", 1, "Guest Cast", PAIR],
                 [2, "card_select", 0, "Center Stage", PAIR]]
    a = _write("s06-selectors.jsonl", sel_rows + [_fight(selectors)])

    # --- the pre-P1.5 log: same combat decisions, no selector channel.
    plain = [r for r in sel_rows if r["state_type"] != "card_select"]
    b = _write("s06-no-selectors.jsonl", plain + [_fight([])])

    # --- the interleave pair: identical `fight.selectors`, the answer given
    #     at a different point in the turn.
    inter_a = [
        _selector_decision(1, "Guest Cast"),          # answered FIRST
        _play(2, 1, FURINA_CARD, hand1, 200),
        _play(3, 1, COMPANION_CARD, hand1, 190),
    ]
    inter_b = [
        _play(1, 1, FURINA_CARD, hand1, 200),
        _play(2, 1, COMPANION_CARD, hand1, 190),
        _selector_decision(3, "Guest Cast"),          # answered LAST
    ]
    one = [[1, "card_select", 1, "Guest Cast", PAIR]]
    c = _write("s06-interleave-a.jsonl", inter_a + [_fight(one)])
    d = _write("s06-interleave-b.jsonl", inter_b + [_fight(one)])
    return {"selectors": a, "no_selectors": b,
            "interleave_a": c, "interleave_b": d}


if __name__ == "__main__":
    for k, v in build().items():
        print(k, v)
