"""`tools/prototype_card_read.py` -- the per-card prototype-arm instrument.

The kits are always on (legacy cleanup stage 6); what is pinned is the cache
clear on the way in and out, and the shape: the rows carry the four rates the
read is made of.
"""

from __future__ import annotations

from tier0.content import loader
from tier05 import rewards
from tools import prototype_card_read as pcr



def test_the_caches_are_cleared_going_in_and_out():
    with pcr.arm_live("kokomi"):
        assert loader._card_prototype("proto_kk_ambush").id == "proto_kk_ambush"
    assert rewards.character_pool.cache_info().currsize == 0


def test_both_arms_run_and_the_probe_still_asks_the_ops_table():
    """`EB-312`: the Klee arm used to report a refusal here, on the slice
    packet's C#-first sentence, and `tier0/engine/klee_overhaul.py` is the twin
    that closed it. The probe is KEPT rather than deleted -- it answers "does
    this engine run the arm", which a future arm will ask again -- and it still
    reads `effects.OPS` rather than a list of its own, which is what makes a
    re-quarantined arm report itself."""
    assert pcr.probe_arm_runnable("klee") is None
    assert pcr.probe_arm_runnable("kokomi") is None
    assert set(pcr._UNBUILT_MARKERS) == set(pcr.ARMS)


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
