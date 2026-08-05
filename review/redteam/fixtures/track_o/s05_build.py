"""SLICE 5 fixture builder — malformed / truncated soak logs.

Writes a BASELINE soak run log (index + run001.jsonl) in the exact shape
`understudy/soak.py` emits, plus one mutated copy per mutation under test.
Nothing here is an instrument; it only manufactures inputs. Deterministic:
re-running rewrites byte-identical files.

    python review/redteam/fixtures/track_o/s05_build.py
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

SEED = "S05BASELINE"
CHAR = "furina"

# Cards that exist in tier0's Furina pool (checked against loader._card_index).
A1 = "Soloist's Solicitation"
A2 = "Stage Presence"
A3 = "Regal Bearing"


def dec(i, rnd, act, floor, card, tid, thp, hand, state_type="monster", hp=60):
    return {
        "record": "decision", "i": i, "state_type": state_type,
        "act": act, "floor": floor, "round": rnd, "hp": hp,
        "action": {"action": "play_card", "index": 0, "target": tid},
        "names": {"verb": "play_card", "card_name": card,
                  "card_id": card.lower().replace(" ", "_"),
                  "card_upgraded": False,
                  "target_id": tid, "target_name": "Cultist",
                  "target_hp": thp},
        "hand": list(hand), "mechanical": False,
        "status": "ok", "message": "ok",
    }


def fight(act, floor, kind, plays, turns, outcome="win"):
    """`plays` is [(round, card_name)]; meters/curves are synthesised per turn."""
    rounds = sorted({r for r, _ in plays})
    return {
        "record": "fight", "schema": 4, "feed": "bot", "source": "soak",
        "intent": "salon", "seats": 1, "seat_index": 0,
        "act": act, "floor": floor, "kind": kind,
        "enemies": [{"name": "Cultist", "max_hp": 50}],
        "hp_start": 60, "hp_end": 48, "max_hp": 75, "hp_lost": 12,
        "turns": turns, "outcome": outcome,
        "hp_trajectory": [[r, 60 - 4 * i, 0] for i, r in enumerate(rounds)],
        "incoming_by_turn": [[r, 6, 1] for r in rounds],
        "enemy_pool_by_turn": [[r, 50 - 12 * i] for i, r in enumerate(rounds)],
        "meters_by_turn": [[r, 2 * i, i, 4, -1] for i, r in enumerate(rounds)],
        "block_at_turn_end": [[r, 0] for r in rounds],
        "cards_played": [[r, c] for r, c in plays],
        "n_cards_played": len(plays),
        "selectors": [],
        "potions_used": [],
        "damage_by_source": {A1: 18.0, A2: 12.0},
        "damage_dealt": 30.0, "damage_taken": 12,
    }


def baseline_rows():
    rows = [{"record": "seed_read_back", "seed": SEED,
             "chosen": None, "honoured": None}]
    i = 0
    # ---- fight 1: two turns, two bracketed plays per turn ----
    for rnd, hps in ((1, (50, 38, 26)), (2, (26, 18, 10))):
        for k, card in enumerate((A1, A2)):
            rows.append(dec(i, rnd, 1, 1, card, "e0", hps[k], [A1, A2, A3]))
            i += 1
    rows.append(fight(1, 1, "monster",
                      [(1, A1), (1, A2), (2, A1), (2, A2)], 2))
    # ---- fight 2: one turn ----
    for k, card in enumerate((A1, A3)):
        rows.append(dec(i, 1, 1, 2, card, "e0", (44, 30)[k], [A1, A3],
                        state_type="elite"))
        i += 1
    rows.append(fight(1, 2, "elite", [(1, A1), (1, A3)], 1))
    rows.append({"record": "run_end", "outcome": "dead", "detail": "",
                 "seed": SEED, "run": 1, "actions": i, "wall_s": 12.0,
                 "fights": 2, "final_act": 1, "final_floor": 2,
                 "defects": 0, "forced_defaults": 0, "log": "run001"})
    return rows


def index_doc(stamp, runs=1):
    return {
        "stamp": stamp, "character": CHAR, "policy": "policy_v1/R93",
        "commit": "salon", "seeds": None, "requested_runs": runs,
        "runs": [{"record": "run_end", "outcome": "dead", "seed": SEED,
                  "run": n, "actions": 6, "wall_s": 12.0, "fights": 2,
                  "final_act": 1, "final_floor": 2, "defects": 0,
                  "forced_defaults": 0} for n in range(1, runs + 1)],
        "stopped_on": None, "reversibility": [],
    }


def dumps(rows, trailing_newline=True):
    s = "\n".join(json.dumps(r, sort_keys=True) for r in rows)
    return s + ("\n" if trailing_newline else "")


def write(name, text):
    p = os.path.join(HERE, name)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return p


def main():
    base = baseline_rows()
    fight_idx = [n for n, r in enumerate(base) if r.get("record") == "fight"]
    f1, f2 = fight_idx

    write("s05-baseline-index.json", json.dumps(index_doc("S05BASE"), indent=1))
    write("s05-baseline-run001.jsonl", dumps(base))

    # M01 mid-JSON truncation: the file stops inside the LAST fight record.
    txt = dumps(base)
    cut = txt.index('"record": "fight"', txt.index('"record": "fight"') + 10)
    write("s05-m01-truncated-midjson-run001.jsonl", txt[:cut + 40])

    # M02 mid-fight truncation: fight 2's decisions are present, its fight
    # record never arrives (a soak killed mid-combat).
    write("s05-m02-fight-never-closed-run001.jsonl", dumps(base[:f2]))

    # M03 one unparseable line in the middle: fight 1's RECORD line is
    # corrupted; every decision before it is still in the file.
    rows = [json.dumps(r, sort_keys=True) for r in base]
    rows[f1] = rows[f1][: len(rows[f1]) // 2] + "  <<TRUNCATED>>"
    write("s05-m03-badline-midfile-run001.jsonl", "\n".join(rows) + "\n")

    # M04 duplicated whole fight: fight 2's record written twice.
    write("s05-m04-duplicate-fight-run001.jsonl",
          dumps(base[:f2 + 1] + [base[f2]] + base[f2 + 1:]))

    # M05 duplicated round: fight 1's meters/pool/block rows for round 2 are
    # written twice with DIFFERENT values, and round 2's two decisions repeat.
    rows = [json.loads(json.dumps(r)) for r in base]
    fr = rows[f1]
    for key, extra in (("meters_by_turn", [2, 99, 3, 4, -1]),
                       ("enemy_pool_by_turn", [2, 999]),
                       ("block_at_turn_end", [2, 77]),
                       ("hp_trajectory", [2, 9, 9])):
        fr[key] = fr[key] + [extra]
    dup = [json.loads(json.dumps(r)) for r in rows[2:4]]  # round-2 decisions
    write("s05-m05-duplicate-round-run001.jsonl",
          dumps(rows[:4] + dup + rows[4:]))

    # M06 out-of-order rounds: fight 1's decisions arrive 2,2,1,1.
    write("s05-m06-out-of-order-rounds-run001.jsonl",
          dumps(base[:1] + base[3:5] + base[1:3] + base[5:]))

    # M07 required field missing: fight 1's record has no `floor`.
    rows = [json.loads(json.dumps(r)) for r in base]
    rows[f1].pop("floor")
    write("s05-m07-missing-floor-run001.jsonl", dumps(rows))

    # M08 null instead of missing: floor/turns/n_cards_played are null.
    rows = [json.loads(json.dumps(r)) for r in base]
    rows[f1]["floor"] = None
    rows[f1]["turns"] = None
    rows[f1]["n_cards_played"] = None
    write("s05-m08-null-fields-run001.jsonl", dumps(rows))

    # M09 interleaved fights: fight 2's decisions are emitted BEFORE fight 1's
    # record closes (two runs' rows concatenated into one file).
    write("s05-m09-interleaved-run001.jsonl",
          dumps(base[:f1] + base[f1 + 1:f2] + [base[f1]] + base[f2:]))

    # M10 whitespace: blank lines interleaved, no trailing newline.
    txt = "\n".join(
        ("\n" if n in (2, 5) else "") + json.dumps(r, sort_keys=True)
        for n, r in enumerate(base))
    write("s05-m10-blanklines-no-trailing-nl-run001.jsonl", txt)

    # M11 unknown row type + unknown fields on a known row.
    rows = [json.loads(json.dumps(r)) for r in base]
    rows[f1]["unknown_key"] = {"deep": [1, 2, 3]}
    rows.insert(f1, {"record": "quantum_flux", "act": 1, "floor": 1,
                     "hp_lost": 999, "turns": 99})
    write("s05-m11-unknown-rows-run001.jsonl", dumps(rows))

    # M13 within-round reorder: fight 1 round 1's two plays swap places, and
    # the hand shrank between them. `_turns` takes hand/hp from the FIRST row
    # it sees for the round, so the reorder rewrites the turn's opening hand.
    rows = [json.loads(json.dumps(r)) for r in base]
    rows[1]["hand"] = [A1, A2, A3]
    rows[2]["hand"] = [A2, A3]          # hand after the first play
    rows[2]["hp"] = 51                  # and HP after it
    write("s05-m13-within-round-reorder-run001.jsonl",
          dumps(rows[:1] + [rows[2], rows[1]] + rows[3:]))

    # M14 malformed `cards_played` row (3 elements instead of 2).
    rows = [json.loads(json.dumps(r)) for r in base]
    rows[f1]["cards_played"] = [[r, c, "extra"] for r, c in
                                [(1, A1), (1, A2), (2, A1), (2, A2)]]
    write("s05-m14-cards-played-arity-run001.jsonl", dumps(rows))

    # M12 for trace_replay: an index claiming 3 runs when only run001 exists.
    write("s05-ghostruns-index.json", json.dumps(index_doc("S05GHOST", 3),
                                                 indent=1))
    print("wrote fixtures to", HERE)


if __name__ == "__main__":
    main()
