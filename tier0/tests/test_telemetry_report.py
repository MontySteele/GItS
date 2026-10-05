"""tools/telemetry_report.py on small synthetic fight records.

The report is the Balance instrument (review/active/klee-balance-measurement,
ruled 2026-10-05): medians by group x act x kind, the ratio to the base five,
and per-card damage by act. These pin the arithmetic, the filters and the
tolerance of older records that lack keys.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


def _module():
    path = REPO / "tools" / "telemetry_report.py"
    spec = importlib.util.spec_from_file_location("_telemetry_report", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


tr = _module()


def fight(character="Klee", act=1, kind="monster", turns=4, dealt=40,
          hp_lost=8, max_hp=80, block=None, outcome="won", seats=1,
          feed="bot", ts=1_790_000_000.0, run_id="SEED1", cards=(),
          by_source=None, **extra):
    row = {"record": "fight", "schema": "1", "feed": feed, "source": "mod",
           "run_id": run_id, "seats": seats, "seat_index": 0,
           "character": character, "act": act, "kind": kind,
           "turns": turns, "damage_dealt": dealt, "hp_lost": hp_lost,
           "max_hp": max_hp, "outcome": outcome, "ts": ts,
           "cards_played": [[1, c] for c in cards],
           "damage_by_source": by_source or {}}
    if block is not None:
        row["block_gained"] = block
    row.update(extra)
    return row


def write(tmp_path: Path, rows, name="play-1.jsonl") -> Path:
    d = tmp_path / "gits_telemetry"
    d.mkdir(parents=True, exist_ok=True)
    with (d / name).open("a", encoding="utf-8") as fh:
        for r in rows:
            fh.write((r if isinstance(r, str) else json.dumps(r)) + "\n")
    return d


def run(tmp_path, rows, *argv, capsys=None):
    d = write(tmp_path, rows)
    args = ["--dir", str(d), "--json", *argv]
    assert tr.main(args) == 0
    return json.loads(capsys.readouterr().out)


def cell(out, group, act, kind="monster"):
    for c in out["table"]:
        if (c["group"], c["act"], c["kind"]) == (group, act, kind):
            return c
    raise AssertionError((group, act, kind, out["table"]))


def test_medians_by_group_act_and_kind(tmp_path, capsys):
    rows = [fight(turns=4, dealt=40, hp_lost=8, block=20),
            fight(turns=2, dealt=40, hp_lost=16, block=None),
            fight(turns=5, dealt=50, hp_lost=0, block=10, outcome="died"),
            fight(kind="elite", turns=5, dealt=100, hp_lost=40),
            "not json", json.dumps({"record": "step"})]
    out = run(tmp_path, rows, "--character", "Klee", capsys=capsys)
    c = cell(out, "Klee", 1)
    assert c["fights"] == 3
    assert c["dmg_turn"] == 10.0            # median of 10, 20, 10
    assert c["hp_lost_pct"] == 10.0         # median of 10, 20, 0
    assert c["turns"] == 4
    assert c["block_turn"] == pytest.approx(3.5)   # median of 5, 2; one lacks it
    assert c["n_block"] == 2
    assert c["losses"] == 1
    assert cell(out, "Klee", 1, "elite")["dmg_turn"] == 20.0
    assert out["records_read"] == 4


def test_base5_pools_the_five_and_names_resolve(tmp_path, capsys):
    rows = [fight("The Ironclad", dealt=40), fight("The Silent", dealt=80),
            fight("The Regent", dealt=120), fight("Varka", dealt=999)]
    out = run(tmp_path, rows, "--character", "base5", "--character",
              "ironclad", capsys=capsys)
    assert out["groups"] == {"base5": 3, "The Ironclad": 1}
    assert cell(out, "base5", 1)["dmg_turn"] == 20.0


def test_comparison_is_a_ratio_to_the_base_five_on_normal_fights(tmp_path,
                                                                   capsys):
    rows = [fight("The Ironclad", act=1, dealt=40, hp_lost=8),
            fight("The Defect", act=1, dealt=40, hp_lost=8),
            fight("The Ironclad", act=2, dealt=80, hp_lost=8),
            fight("Klee", act=1, dealt=44, hp_lost=8),
            fight("Klee", act=2, dealt=40, hp_lost=16),
            # an elite never enters the comparison
            fight("Klee", act=1, kind="elite", dealt=400, hp_lost=0)]
    out = run(tmp_path, rows, "--character", "Klee", capsys=capsys)
    comp = {c["act"]: c for c in out["comparison"]}
    assert comp[1]["dmg_ratio"] == pytest.approx(1.1)
    assert comp[1]["hp_ratio"] == pytest.approx(1.0)
    assert comp[1]["within_bar"] is True
    assert comp[2]["dmg_ratio"] == pytest.approx(0.5)
    assert comp[2]["hp_ratio"] == pytest.approx(2.0)
    assert comp[2]["within_bar"] is False
    assert comp[3]["dmg_ratio"] is None and comp[3]["fights"] == 0


def test_filters_solo_feed_seed_and_time(tmp_path, capsys):
    t0 = 1_790_000_000.0
    rows = [fight(ts=t0, run_id="A"),
            fight(ts=t0 + 86400 * 3, run_id="B"),
            fight(ts=t0, seats=2),
            fight(ts=t0, feed="human")]
    d = write(tmp_path, rows)

    def n(*argv):
        assert tr.main(["--dir", str(d), "--json", "--character", "Klee",
                        *argv]) == 0
        return json.loads(capsys.readouterr().out)["groups"]["Klee"]
    assert n() == 3                                   # co-op dropped
    assert n("--no-solo") == 4
    assert n("--feed", "human") == 1
    assert n("--feed", "bot") == 2
    assert n("--seed", "B") == 1
    assert n("--run-id", "A", "--run-id", "B") == 2
    import datetime as dt
    mid = dt.datetime.fromtimestamp(t0 + 86400).isoformat()
    assert n("--since", mid) == 1
    assert n("--until", mid) == 2


def test_baseline_window_is_its_own(tmp_path, capsys):
    t0 = 1_790_000_000.0
    rows = [fight("The Ironclad", ts=t0, dealt=40),
            fight("The Ironclad", ts=t0 + 86400 * 5, dealt=80),
            fight("Klee", ts=t0 + 86400 * 5, dealt=80)]
    import datetime as dt
    since = dt.datetime.fromtimestamp(t0 + 86400).isoformat()
    out = run(tmp_path, rows, "--character", "Klee", "--since", since,
              "--baseline-since", "2000-01-01", capsys=capsys)
    comp = out["comparison"][0]
    assert comp["base_fights"] == 2 and comp["base_dmg_turn"] == 15.0


def test_older_records_missing_keys_are_left_out_not_zeroed(tmp_path, capsys):
    old = fight(dealt=40)
    for k in ("damage_dealt", "hp_lost", "max_hp", "damage_by_source",
              "cards_played", "seats"):
        old.pop(k)
    rows = [old, fight(dealt=80, hp_lost=8)]
    out = run(tmp_path, rows, "--character", "Klee", capsys=capsys)
    c = cell(out, "Klee", 1)
    assert c["fights"] == 2                 # a missing `seats` reads as solo
    assert c["dmg_turn"] == 20.0            # the old row does not count as 0
    assert c["hp_lost_pct"] == 10.0
    assert c["block_turn"] is None and c["n_block"] == 0



def test_strength_is_the_median_of_each_fights_peak(tmp_path, capsys):
    rows = [fight(strength_by_turn=[[1, 0], [2, 3], [3, 2]]),     # peak 3
            fight(strength_by_turn=[[1, 0], [2, 0]]),             # peak 0
            fight(strength_by_turn=[[1, 2], [2, 5], [3, 7]]),     # peak 7
            fight()]                                              # older: no key
    out = run(tmp_path, rows, "--character", "Klee", capsys=capsys)
    assert cell(out, "Klee", 1)["strength"] == 3.0
    d = write(tmp_path / "t", rows)
    assert tr.main(["--dir", str(d), "--character", "Klee"]) == 0
    text = capsys.readouterr().out
    assert " str " in text and "3.0" in text


def test_strength_is_none_without_the_key(tmp_path, capsys):
    out = run(tmp_path, [fight()], "--character", "Klee", capsys=capsys)
    assert cell(out, "Klee", 1)["strength"] is None

def test_hp_lost_falls_back_to_start_minus_end(tmp_path, capsys):
    row = fight(hp_start=80, hp_end=60)
    row.pop("hp_lost")
    out = run(tmp_path, [row], "--character", "Klee", capsys=capsys)
    assert cell(out, "Klee", 1)["hp_lost_pct"] == 25.0


def test_per_card_plays_damage_and_upgrades_by_act(tmp_path, capsys):
    rows = [fight(act=1, cards=("Strike", "Strike", "Big Badda Boom"),
                  by_source={"Strike": 12, "Big Badda Boom": 20,
                             "(Bomb)": 9}),
            fight(act=2, cards=("Strike+", "Big Badda Boom"),
                  by_source={"Strike+": 9, "Big Badda Boom": 40}),
            fight(act=2, cards=("Strike",), by_source={"Strike": 6})]
    out = run(tmp_path, rows, "--character", "Klee", "--character", "base5",
              capsys=capsys)
    assert out["cards_for"] == "Klee"
    got = {(c["card"], c["upgraded"], c["act"]): c for c in out["cards"]}
    s1 = got[("Strike", False, 1)]
    assert (s1["fights"], s1["plays"], s1["damage"]) == (1, 2, 12)
    assert s1["dmg_per_play"] == 6.0
    assert got[("Strike", True, 2)]["dmg_per_play"] == 9.0
    assert got[("Big Badda Boom", False, 2)]["dmg_per_play"] == 40.0
    bomb = got[("(Bomb)", False, 1)]
    assert bomb["plays"] == 0 and bomb["dmg_per_play"] is None
    # sorted by total damage: Big Badda Boom (60) before Strike (18)
    assert out["cards"][0]["card"] == "Big Badda Boom"

    merged = run(tmp_path / "m", rows, "--character", "Klee",
                 "--cards-merge-upgrades", capsys=capsys)
    got = {(c["card"], c["act"]): c for c in merged["cards"]}
    s2 = got[("Strike", 2)]
    assert (s2["fights"], s2["plays"], s2["damage"]) == (2, 2, 15)
    assert all(not c["upgraded"] for c in merged["cards"])


def test_split_name():
    assert tr.split_name("Strike++") == ("Strike", True)
    assert tr.split_name("Strike+") == ("Strike", True)
    assert tr.split_name("Kaboom!") == ("Kaboom!", False)


def test_text_output_carries_the_three_blocks(tmp_path, capsys):
    rows = [fight("The Ironclad", dealt=40), fight("Klee", dealt=44,
                                                  cards=("Strike",),
                                                  by_source={"Strike": 6})]
    d = write(tmp_path, rows)
    assert tr.main(["--dir", str(d), "--character", "Klee",
                    "--character", "base5"]) == 0
    text = capsys.readouterr().out
    assert "BY GROUP x ACT x KIND" in text
    assert "COMPARISON" in text and "within" in text
    assert "PER CARD: Klee" in text and "Strike" in text
