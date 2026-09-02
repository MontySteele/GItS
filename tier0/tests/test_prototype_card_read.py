"""`tools/prototype_card_read.py` -- the per-card prototype-arm instrument.

THE ONE THING THAT MATTERS IS THE FLAG RESTORE. The instrument sets a
quarantined arm's constant in process; a leak would move every test that runs
after it, so the restore and the cache clear are pinned rather than trusted.
The rest is shape: the rows carry the four rates the read is made of, and the
Klee arm reports its refusal instead of a table.
"""

from __future__ import annotations

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier05 import rewards
from tools import prototype_card_read as pcr


def test_the_flag_is_restored_and_the_caches_cleared():
    assert C.KOKOMI_OVERHAUL is False
    with pcr.arm_live("kokomi"):
        assert C.KOKOMI_OVERHAUL is True
        assert loader._card_prototype("proto_kk_ambush").id == "proto_kk_ambush"
    assert C.KOKOMI_OVERHAUL is False
    # The cache must not still be answering from inside the block: with the
    # flag off a `proto_kk_` id is not a card at all.
    with pytest.raises(KeyError):
        loader._card_prototype("proto_kk_ambush")
    assert rewards.character_pool.cache_info().currsize == 0


def test_the_klee_arm_reports_its_refusal_rather_than_running():
    reason = pcr.probe_arm_runnable("klee")
    assert reason and "KLEE_OVERHAUL" in reason and "set_off" in reason
    assert pcr.probe_arm_runnable("kokomi") is None


def test_a_small_kokomi_cohort_produces_the_four_rates():
    out = pcr.tally("kokomi", runs=4, seed=42, n_acts=1)
    assert out["runs"] == 4 and out["fights"] > 0
    assert out["avg_fight_turns"] > 0
    assert [a["act"] for a in out["act_funnel"]] == [1]
    rows = {r["id"]: r for r in out["rows"]}
    # Her two starter prototype rows open every deck, so they are drawn and
    # they carry a play rate; a rate with no denominator is None, never 0.0.
    # `carried_runs` reads the FINAL deck, which a shop removal can shorten,
    # so it is bounded rather than pinned at the cohort size.
    oath = rows["proto_kk_kurages_oath"]
    assert 0 < oath["carried_runs"] <= 4
    assert oath["draws"] > 0
    assert 0.0 <= oath["play_rate_in_hand"] <= 1.0
    for row in out["rows"]:
        for key in ("pick_rate_when_offered", "play_rate_in_hand"):
            assert row[key] is None or 0.0 <= row[key] <= 1.0
    assert C.KOKOMI_OVERHAUL is False
