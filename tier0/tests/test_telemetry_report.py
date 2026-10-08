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


# ------------------------------------------------------------- reactions ---

def _rx_row(character, seat_index, *, turns=4, fight_index=0, run_id="CO1",
            by_type=None, amp=None, debuffs=None, seats=2, **extra):
    row = fight(character, turns=turns, seats=seats, run_id=run_id,
                feed="human", fight_index=fight_index, seat_index=seat_index,
                encounter="ENC", floor=2, **extra)
    if by_type is not None:
        row["reactions_by_type"] = by_type
        row["amp_bonus_damage"] = amp or {}
        row["debuffs_from_reactions"] = debuffs or {}
    return row


def _coop_fixture():
    klee = dict(by_type={"Vaporize": 2, "Overload": 1},
                amp={"Vaporize": 6}, debuffs={"Weak": 1})
    koko = dict(by_type={"Vaporize": 1}, amp={"Vaporize": 3})
    return [
        # fight 0, written by BOTH lanes (the duplicate must not count twice)
        _rx_row("Klee", 0, **klee), _rx_row("Kokomi", 1, **koko),
        _rx_row("Klee", 0, **klee), _rx_row("Kokomi", 1, **koko),
        # fight 1, an older record with no reaction keys: counted in n only
        _rx_row("Klee", 0, fight_index=1), _rx_row("Kokomi", 1, fight_index=1),
        # a base pair
        _rx_row("The Ironclad", 0, run_id="CO2", by_type={}),
        _rx_row("The Silent", 1, run_id="CO2", by_type={}),
        # a solo fight, which --coop must leave out
        _rx_row("Klee", 0, run_id="SOLO", seats=1,
                by_type={"Melt": 4}, amp={"Melt": 12}),
    ]


def test_reactions_section_is_opt_in(tmp_path, capsys):
    out = run(tmp_path, _coop_fixture(), capsys=capsys)
    assert "reactions" not in out


def test_solo_reactions_are_pooled_per_turn(tmp_path, capsys):
    out = run(tmp_path, _coop_fixture(), "--reactions", "--character", "Klee",
              capsys=capsys)
    (klee,) = out["reactions"]
    assert klee["group"] == "Klee" and klee["fights"] == 1
    assert klee["reactions_by_type_turn"] == {"Melt": 1.0}
    assert klee["amp_bonus_turn"] == 3.0
    assert klee["debuffs_turn"] == 0


def test_coop_groups_by_team_and_dedupes_lanes(tmp_path, capsys):
    out = run(tmp_path, _coop_fixture(), "--coop", "--reactions",
              capsys=capsys)
    assert out["filters"]["coop"] is True
    by = {(s["group"], s.get("team")): s for s in out["reactions"]}
    team = by[("Klee + Kokomi", None)]
    assert team["fights"] == 2 and team["fights_with_keys"] == 1
    assert team["turns"] == 4            # one fight's turns, counted once
    assert team["totals"]["reactions_by_type"] == {"Overload": 1, "Vaporize": 3}
    assert team["reactions_turn"] == 1.0
    assert team["amp_bonus_by_type_turn"] == {"Vaporize": 9 / 4}
    assert team["debuffs_by_type_turn"] == {"Weak": 0.25}
    klee = by[("Klee", "Klee + Kokomi")]
    assert klee["member"] and klee["reactions_turn"] == 0.75
    base = by[("The Ironclad + The Silent", None)]
    assert base["fights_with_keys"] == 1 and base["reactions_turn"] == 0
    assert ("Klee", None) not in by     # the solo fight stays out


def test_coop_character_filter_keeps_teams_holding_it(tmp_path, capsys):
    out = run(tmp_path, _coop_fixture(), "--coop", "--reactions",
              "--character", "base5", capsys=capsys)
    teams = {s["group"] for s in out["reactions"] if not s.get("member")}
    assert teams == {"The Ironclad + The Silent"}


def test_reactions_text_block(tmp_path, capsys):
    d = write(tmp_path, _coop_fixture())
    assert tr.main(["--dir", str(d), "--coop", "--reactions"]) == 0
    text = capsys.readouterr().out
    assert "REACTIONS (pooled a turn" in text
    assert "Klee + Kokomi" in text and "  | Kokomi" in text
    assert "reactions/t: Vaporize 0.75  Overload 0.25" in text
    assert "amp bonus/t: Vaporize 2.25" in text
    assert "debuffs/t:   Weak 0.25" in text


# ------------------------------------------------- run instances, lane copies ---

def test_fight_key_separates_run_instances_on_one_seed(tmp_path, capsys):
    """An abandoned attempt and its rerun on the same seed restart
    fight_index; run_instance keeps them two fights, two teams' worth."""
    rows = [
        _rx_row("Klee", 0, run_instance="20261007-010000#0", by_type={}),
        _rx_row("Varka", 1, run_instance="20261007-010000#0", by_type={}),
        _rx_row("Klee", 0, run_instance="20261007-020000#0", by_type={}),
        _rx_row("Varka", 1, run_instance="20261007-020000#0", by_type={}),
    ]
    out = run(tmp_path, rows, "--coop", "--reactions", capsys=capsys)
    teams = [s for s in out["reactions"] if not s.get("member")]
    assert [(t["group"], t["fights"]) for t in teams] == [("Klee + Varka", 2)]
    assert out["records_kept"] == 4


def test_lane_copies_of_coop_rows_are_dropped_on_read(tmp_path):
    """Both co-op lanes write both seats: each (fight, seat) arrives twice,
    once per lane dir. load_fights keeps one; solo rows are never merged."""
    inst = {"run_instance": "20260927-014342#0"}
    coop = [_rx_row("Klee", 0, **inst), _rx_row("Furina", 1, **inst)]
    solo = [fight("Klee", run_instance="20261003-000551#0", fight_index=0,
                  floor=2, seat_index=0)]
    lane_a = write(tmp_path / "lane1", coop + solo)
    lane_b = write(tmp_path / "lane2", coop + solo)
    rows = tr.load_fights([lane_a, lane_b])
    assert sorted((r["character"], r["seats"]) for r in rows) == [
        ("Furina", 2), ("Klee", 1), ("Klee", 1), ("Klee", 2)]
    assert len(tr.load_fights([lane_a, lane_b], dedupe=False)) == 6


def test_run_instance_filter_is_repeatable_and_prefix_matched(tmp_path,
                                                              capsys):
    rows = [fight("Klee", run_instance="20261007-235701#0", dealt=40),
            fight("Klee", run_instance="20261007-235702#0", dealt=40),
            fight("Klee", run_instance="20261007-204801#0", dealt=80),
            fight("The Ironclad", run_instance="20261005-105504#0"),
            fight("The Regent", run_instance="20261005-113940#0"),
            fight("The Silent", run_instance="20261005-125503#0", dealt=999),
            fight("Klee")]                          # no run_instance at all
    out = run(tmp_path, rows, "--character", "Klee",
              "--run-instance", "20261007-2357", capsys=capsys)
    assert cell(out, "Klee", 1)["fights"] == 2
    assert out["filters"]["run_instance"] == ["20261007-2357"]
    out = run(tmp_path / "b", rows, "--character", "Klee",
              "--character", "base5",
              "--run-instance", "20261007-2357",
              "--baseline-run-instance", "20261005-1055",
              "--baseline-run-instance", "20261005-113940#0", capsys=capsys)
    (act1,) = [c for c in out["comparison"] if c["act"] == 1]
    assert act1["fights"] == 2 and act1["base_fights"] == 2
    assert act1["base_dmg_turn"] == 10.0          # the 999 run is left out


def test_help_prints_the_field_notes(capsys):
    with pytest.raises(SystemExit):
        tr.main(["--help"])
    text = capsys.readouterr().out
    assert "RUNNING TOTAL" in text and "never a sum" in text
    assert "EB-156" in text and "run_instance" in text
