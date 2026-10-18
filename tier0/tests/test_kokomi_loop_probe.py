"""Kokomi's loop probe (`tier0/harness/kokomi_loop_probe.py`), built
2026-10-18 from the BACKLOG line "Kokomi has no loop probe".

Its known set, from that line: Shoal Call x2 + Watchful Shoal+ + The Shape of
Water (review r3: a one-turn burst, kept and listed) and Kurage Canopy plus a
planned Ward, "a steady 0-cost Weak and 3 Block a turn" (review r4), with its
Endless Shoal twin. The Kokomi card paper v2 (2026-10-18, sec.2 change 5) took
a Sting's or Ward's carry-out off Canopy and Endless Shoal, which closes the
second; `pre_fix` puts it back so the probe is seen to find it. And the v2
check: Shoal Call's Stings written as Plans with Feint and Turning Tide paying
per Plan carried out stay bounded.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions about an engine.
"""

from __future__ import annotations

import pytest

from tier0.harness import kokomi_loop_probe as P


def _verdict(row: dict) -> tuple[bool, bool, bool]:
    w = row["worst"]
    return (w["runaway"], w["growing"], w["perpetual"])


@pytest.mark.parametrize("name", sorted(P.NAMED))
def test_no_named_combination_runs_away_grows_or_feeds_itself(name):
    assert _verdict(P.named_report(name)) == (False, False, False), name


def test_the_shape_of_water_burst_is_one_turn_and_spends_its_calls():
    """Review r3's known entry: the Calls exhaust, so the turn after the
    burst has no Stings left to make."""
    w = P.named_report("shoal_shape_of_water")["worst"]
    assert w["tokens"][0] >= 6
    assert sum(w["tokens"][1:]) == 0
    assert w["dealt"][0] > 4 * max(w["dealt"][1:])


@pytest.mark.parametrize("name", ["canopy_ward", "endless_shoal_sting"])
def test_v2_closed_the_jellyfish_that_returned_itself(name):
    """Review r4's known entry. Before v2 a planned Ward came back every
    morning under Kurage Canopy (a Sting under Endless Shoal); the probe
    finds that cycle with the old rule put back, and not with the new one."""
    old = P.named_report(name, fixed=False)["worst"]
    assert old["perpetual"]
    assert all(n == 1 for n in old["plays"])
    new = P.named_report(name)["worst"]
    assert not new["perpetual"]
    assert sum(new["plays"][1:]) == 0


def test_stings_feint_and_turning_tide_settle_to_a_flat_morning():
    """The v2 check: per-Plan payoffs over written Stings do not compound.
    After the Calls are spent, each morning carries out the same count and
    deals the same damage."""
    for name in ("shoal_feint_turning_tide",
                 "shoal_feint_turning_tide_engines"):
        w = P.named_report(name)["worst"]
        assert not w["runaway"] and not w["growing"], name
        tail = w["dealt"][-(P.TURNS // 2):]
        assert len(set(tail)) == 1, (name, w["dealt"])


def test_the_engines_pay_for_feint_and_not_for_its_stings():
    """With Endless Shoal and Canopy out, the old rule paid for every
    written Sting too, so each morning made a hand of them; the new rule pays
    for Feint's and Turning Tide's carry-outs only."""
    old = P.named_report("shoal_feint_turning_tide_engines",
                         fixed=False)["worst"]
    new = P.named_report("shoal_feint_turning_tide_engines")["worst"]
    assert max(new["tokens"][1:]) < max(old["tokens"][1:])
    assert max(new["tokens"][1:]) > 0


@pytest.mark.battery
def test_the_in_turn_sweep_finds_no_cycle():
    """Furina's criterion: no combination of up to three of her cards, under
    no Power or one, refills the hand and the Energy for a whole long turn."""
    found = P.search()
    assert [f.label() for f in found] == []
