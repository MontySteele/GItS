"""Track O slice 4 -- the two replayers' input contracts, pinned.

`understudy/replay.py` (S7) and `understudy/trace_replay.py` (P1.5) are two
different instruments wearing one word, and they read overlapping subsets of
the SAME soak fight record. This file pins only the reading rules that the
modules' own docstrings and `understudy/soak.py`'s declared row shapes state
unambiguously -- it is a contract pin, not a defect list. The defects the
slice found are surfaced in prose and deliberately NOT encoded here.

Fixtures: `review/redteam/fixtures/track_o/s04-logdir-A/`.
"""

from __future__ import annotations

import json
from pathlib import Path

from understudy import replay as s7
from understudy import trace_replay as tr

FIX = (Path(__file__).resolve().parents[2] / "review" / "redteam"
       / "fixtures" / "track_o")
RUN_LOG = FIX / "s04-logdir-A" / "soak-S04A-run001.jsonl"


def _fight_record() -> dict:
    for line in RUN_LOG.read_text(encoding="utf-8").splitlines():
        rec = json.loads(line)
        if rec.get("record") == "fight":
            return rec
    raise AssertionError("fixture carries no fight record")


# ------------------------------------------------------- trace_replay ----

def test_trace_reads_missing_keys_as_empty():
    """`trace`'s docstring: a record written by a pre-P1.5 soak carries no
    `selectors`, and the honest report on that is "recorded no selector
    answers", not a crash. Absent and empty are therefore ONE reading.
    """
    absent = {"act": 1, "floor": 2, "kind": "monster"}
    empty = dict(absent, cards_played=[], selectors=[], meters_by_turn=[])
    assert tr.trace(absent) == tr.trace(empty)
    assert tr.trace(absent) == {k: [] for k in tr.TRACE_KEYS}


def test_trace_identity_excludes_hp_and_damage():
    """Module docstring: `hp_trajectory` and the damage totals are
    deliberately NOT part of the trace identity -- they are the OUTPUT a
    comparison measures, and folding them in would make every interesting
    result an inequality of the thing being compared with itself.
    """
    fight = _fight_record()
    assert fight["hp_trajectory"] and fight["damage_by_source"]
    for key in ("hp_trajectory", "damage_by_source", "damage_dealt",
                "damage_taken", "hp_lost"):
        assert key not in tr.TRACE_KEYS
    moved = dict(fight, hp_trajectory=[[1, 1, 0]], damage_by_source={"x": 99},
                 damage_dealt=99, damage_taken=99, hp_lost=99)
    assert tr.trace(moved) == tr.trace(fight)


def test_fight_keys_are_the_identity_not_the_description():
    """`FIGHT_KEYS` are the fields that IDENTIFY a fight within a run."""
    assert tr.FIGHT_KEYS == ("act", "floor", "kind")
    assert tr.TRACE_KEYS == ("cards_played", "selectors", "meters_by_turn")


def test_selector_lines_print_the_offer_list():
    """`selector_lines`: the OFFERED list is printed, not just the answer --
    a reconstruction that cannot say what was available has not reconstructed
    the choice. The chosen entry is the starred one.
    """
    lines = tr.selector_lines(_fight_record())
    assert len(lines) == 1
    assert "*Center Stage*" in lines[0] and "Guest Cast" in lines[0]


# ------------------------------------------------------------ replay -----

def test_meters_column_order_matches_the_soak_row_shape():
    """`understudy/soak.py`: `meters_by_turn` is
    `[(rnd, fanfare, salon, salon_cap, encore)]`. `replay._meters_at` is the
    only place that names those columns, so the mapping is the schema.
    """
    fight = _fight_record()
    assert fight["meters_by_turn"][1] == [2, 3, 1, 4, -1]
    assert s7._meters_at(fight, 2) == {
        "fanfare": 3, "salon_members": 1, "salon_cap": 4, "encore": -1}
    assert s7._meters_at(fight, 99) == {}


def test_encore_sentinel_is_not_loaded_onto_the_sim():
    """`_apply_meters`: `encore == -1` means the bot feed could not see the
    meter; it is left at the sim's own value rather than compared against a
    sentinel.
    """
    player = s7._fresh_player("furina", 70, 75, 0,
                              {"fanfare": 3, "salon_members": 0,
                               "salon_cap": 0, "encore": -1})
    baseline = s7.loader.build_player("furina")
    assert player.encore == baseline.encore
    assert player.fanfare == 3


def test_selector_choice_needs_the_whole_offer_pair():
    """`SPOTLIGHT_OFFERS`: matching is on the OFFER LIST as well as the chosen
    name. "Center Stage" chosen from a list that did not also contain "Guest
    Cast" is a different screen wearing a familiar word.
    """
    good = {"selectors": [[1, "card_select", 0, "Center Stage",
                           ["Center Stage", "Guest Cast"]]]}
    lone = {"selectors": [[1, "card_select", 0, "Center Stage",
                           ["Center Stage", "Skip"]]]}
    assert s7._selector_choice(good, 1) == "self"
    assert s7._selector_choice(lone, 1) is None
    assert s7._selector_choice(good, 2) is None
    assert s7._selector_choice(_fight_record(), 1) == "self"


def test_fight_specs_needs_decision_rows_to_replay_anything():
    """`fight_specs` splits a run log into fights plus the COMBAT decisions
    that preceded each. A fight record alone yields a spec with no turns, and
    `main` skips those -- `fights_found` and `fights_replayed` are separate
    counters for exactly that reason.
    """
    specs = s7.fight_specs(str(RUN_LOG))
    assert len(specs) == 1
    assert specs[0]["fight_id"] == "soak-S04A-run001#f1"
    assert [t["round"] for t in specs[0]["turns"]] == [1, 2]
    assert [p["card"] for p in specs[0]["turns"][0]["plays"]] == [
        "Stage Presence", "Soloist's Solicitation"]

    mod_only = str(FIX / "s04-modfeed.jsonl")
    mod_specs = s7.fight_specs(mod_only)
    assert len(mod_specs) == 1
    assert mod_specs[0]["turns"] == []
