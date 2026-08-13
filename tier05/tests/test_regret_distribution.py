"""EB-72: the margin-free regret gap sample, and the printer over it.

`test_route_regret.py` already pins the route sampler's CONSTRUCTION. What is
new here is the split R164 forced: the gap sample has to be reachable WITHOUT
the margin, because the margin is not ratified and the distribution is the
only quotable read until it is.

So these tests pin three things and nothing about any threshold's value:

  - the summary is a REDUCTION of the sample, not a second computation of it
    (route and draft, both directions);
  - collection is MARGIN-FREE -- moving the margin moves the counted regrets
    and leaves every distribution number byte-identical;
  - the printer re-prices exactly the sample the live run priced, which is
    the claim its `cross-check` lines make on the page.
"""

from __future__ import annotations

import random

from tier0 import constants as C
from tier0.content import loader
from tier05 import cells, draft, maps, model, route, run_metrics
from tier05.maps import ELITE, NORMAL, SHOP, TREASURE, ActMap, Room
from tools import regret_distribution as rd


def _state(hp: int) -> route.RouteState:
    return route.RouteState(hp=hp, max_hp=80, gold=0, deck_size=15, floor=0,
                            act=0, elites_taken=0, rests_taken=0)


HEALTHY, HURT = _state(80), _state(20)


def _two_lane_map() -> ActMap:
    """`test_route_regret._two_lane_map`, same board: lane 0 rich, lane 1
    plain, one real fork on floor 1."""
    return ActMap(act=0, floors=[
        [Room(0, 0, NORMAL, out=[0]), Room(0, 1, NORMAL, out=[1])],
        [Room(1, 0, ELITE, out=[0]), Room(1, 1, NORMAL, out=[1])],
        [Room(2, 0, SHOP, out=[0]), Room(2, 1, NORMAL, out=[1])],
        [Room(3, 0, TREASURE, out=[]), Room(3, 1, NORMAL, out=[])],
    ])


def _decisions(m, policy, st):
    return route.walk_decisions(random.Random(0), m, policy, lambda: st)


# --- the summary is a reduction of the sample -------------------------------

def test_route_summary_is_a_reduction_of_the_gap_sample():
    """Every distribution key `route_regret` reports has to be computable
    from `route_regret_gaps` alone. If it is not, the printer is describing a
    different sample from the one the run recorded."""
    m = maps.generate(random.Random(5), 0)
    decisions = _decisions(m, route.hunter, HEALTHY)

    gaps, forced = run_metrics.route_regret_gaps(
        random.Random(0), m, decisions, HURT, "hunter")
    summary = run_metrics.route_regret(random.Random(0), m, decisions,
                                       HURT, "hunter")

    assert summary["forced"] == forced
    assert summary["sampled"] == len(gaps)
    assert summary["mean_regret"] == sum(gaps) / len(gaps)
    assert summary["max_regret"] == max(gaps)
    assert summary["p50_regret"] == run_metrics._percentile(gaps, 0.50)
    assert summary["p90_regret"] == run_metrics._percentile(gaps, 0.90)


def test_draft_regret_is_the_count_of_gaps_over_the_margin():
    """The drafter's integer, re-derived from its own magnitudes. The split
    consumes the rng identically, so the same seed samples the same screens."""
    results = model.run_many("klee", "demolition", "demolition",
                             draft.assigned_policy, 3, 7)
    for r in results:
        deck = [loader.peek_card(cid) for cid in r.deck_ids]
        gaps = draft.draft_regret_gaps(random.Random(r.seed), r.decisions,
                                       deck, "demolition")
        count = draft.draft_regret(random.Random(r.seed), r.decisions,
                                   deck, "demolition")
        assert count == sum(1 for g in gaps
                            if g > draft.DRAFT_REGRET_MARGIN)


def test_the_zero_gaps_are_kept_in_the_sample():
    """A decision the policy got right is a 0.0, not an absence. Dropping it
    would silently turn every percentile into a percentile of the regrets --
    the exact confusion the printer's two denominators exist to keep apart."""
    m = _two_lane_map()
    gaps, _ = run_metrics.route_regret_gaps(
        random.Random(0), m, _decisions(m, route.hunter, HEALTHY),
        HEALTHY, "hunter")
    assert gaps == [0.0]            # one forked floor, no hindsight shift


# --- collection is margin-free ----------------------------------------------

def test_moving_the_margin_moves_nothing_but_the_count():
    """THE property R164 needs. `mean/p50/p90/max` are quotable while the
    margin is unratified precisely because they cannot see it."""
    m = maps.generate(random.Random(5), 0)
    decisions = _decisions(m, route.hunter, HEALTHY)

    def priced(margin):
        return run_metrics.route_regret(random.Random(0), m, decisions,
                                        HURT, "hunter", margin=margin)

    tight, loose = priced(0.0), priced(10 ** 6)
    free = ("policy", "decisions", "forced", "sampled", "mean_regret",
            "p50_regret", "p90_regret", "max_regret")
    assert {k: tight[k] for k in free} == {k: loose[k] for k in free}
    assert tight["regretted"] > loose["regretted"] == 0


def test_the_gap_collector_takes_no_margin_at_all():
    """Structural, not behavioural: a margin-free read is only trustworthy if
    the collection loop has no way to consult one."""
    import inspect
    assert "margin" not in inspect.signature(
        run_metrics.route_regret_gaps).parameters
    assert "margin" not in inspect.signature(
        draft.draft_regret_gaps).parameters


def test_describe_moves_only_its_three_margin_keys():
    """The printer's reduction obeys the same rule as the sampler."""
    gaps = [0.0, 0.0, 0.5, 1.5, 4.0, -0.25]
    a, b = rd.describe(gaps, 1.0), rd.describe(gaps, 3.0)
    moved = {k for k in a if a[k] != b[k]}
    assert moved == {"above_margin", "above_margin_share", "margin"}
    assert a["n"] == 6 and a["zero"] == 2 and a["negative"] == 1
    assert a["nonzero"]["n"] == 3       # the negative is not a regret


# --- the printer re-prices the sample the run recorded ----------------------

def _cell(**deltas) -> cells.Cell:
    """A cheap, non-canonical cell. `realistic=False` and 3 runs make this a
    unit test rather than a measurement; nothing printed off it is citable."""
    return cells.CANONICAL.but(name="eb72-test", character="klee",
                               archetype="demolition", runs=3, seed=42,
                               realistic=False, jobs=1, **deltas)


def test_the_printer_reproduces_the_live_per_act_route_summaries():
    """The `cross-check` line on the page. The tool re-prices on the same
    dedicated stream `model._run_range` used, one fresh Random per act -- so
    a non-zero mismatch count means the tool has drifted off the pipeline it
    claims to describe."""
    data = rd.collect(_cell())
    assert data["route"]["acts"] > 0
    assert data["route"]["gaps"]            # not an empty instrument
    assert data["route"]["mismatches"] == 0


def test_the_printer_reproduces_the_live_draft_regret_counts():
    """Same claim for the drafter: the recomputed count over the in-tree
    margin has to equal the `regret_samples` the run already carries."""
    data = rd.collect(_cell())
    d = data["draft"]
    assert d["recomputed_regrets"] == d["live_regrets"]
    assert d["mismatches"] == 0
    assert d["sample_rate"] == C.DRAFT_REGRET_SAMPLE


def test_raising_the_draft_sample_rate_widens_the_sample_and_voids_the_check():
    """The census mode. It re-scores screens the run never priced, so the
    sample grows and the `regret_samples` equality stops being the right
    check -- reported as n/a, never as a pass."""
    cell = _cell()
    results = cell.run()
    default = rd.draft_gaps(results, cell.archetype)
    census = rd.draft_gaps(results, cell.archetype, sample=1.0)
    assert len(census["gaps"]) > len(default["gaps"])
    assert default["mismatches"] == 0
    assert census["mismatches"] is None
    assert census["sample_rate"] == 1.0


def test_the_report_states_its_own_limits(capsys):
    """The page must not read as a proposal. Two things it always says: the
    margin is not ratified, and the two denominators are different."""
    cell = _cell()
    data = rd.collect(cell)
    rd.report(cell, data["route"], data["draft"])
    out = capsys.readouterr().out
    assert "NOT RATIFIED" in out
    assert "R164" in out
    assert "margin-free" in out
    assert "NON-ZERO ONLY" in out
    assert cell.stamp() in out
    assert "No threshold, band or acceptance target is stated here." in out
    # No recommendation vocabulary anywhere on the page.
    lowered = out.lower()
    for word in ("recommend", "we suggest", "the right margin"):
        assert word not in lowered


def test_the_json_payload_carries_its_stamp():
    """An unstamped number is not citable (R68), and a JSON file outlives the
    terminal it was printed in."""
    cell = _cell()
    payload = rd._payload(cell, rd.collect(cell))
    assert payload["stamp"] == cell.stamp()
    assert payload["versions"] == cell.versions
    assert "gaps" not in payload["route"]        # the sample is not shipped
    assert payload["route"]["distribution"]["margin"] == \
        run_metrics.ROUTE_REGRET_MARGIN
    assert payload["draft"]["distribution"]["margin"] == \
        draft.DRAFT_REGRET_MARGIN


class _AlwaysSample:
    """An rng whose `random()` always falls under any sample rate."""

    def random(self) -> float:
        return 0.0


class _Offer:
    def __init__(self, cid: str) -> None:
        self.id = cid


def test_a_gap_of_exactly_one_point_is_not_a_regret(monkeypatch):
    """The boundary the EB-72 split re-associated, pinned so it stops being
    untested.

    MEDIUM-11's invariant is MORE THAN a full point, and the split expresses it
    as `(max - picked) > DRAFT_REGRET_MARGIN`. The pre-split loop asked
    `any(v > picked + 1.0)`, which is a DIFFERENT predicate in floating point:
    these two scores are a real pair off klee/demolition seed 18, and
    `picked + 1.0` rounds BELOW the rival, so the old form counted this screen
    and the new one does not. Nothing gates on the count; this test exists so
    the convention is chosen on purpose rather than by rounding.
    """
    picked, rival = 0.6666666666666666, 1.6666666666666667
    # The two forms genuinely disagree here -- that is the whole point.
    assert rival > picked + 1.0
    assert not (rival - picked) > 1.0

    scores = {"picked": picked, "rival": rival}
    monkeypatch.setattr(draft, "score_offer",
                        lambda card, deck, archetype: scores[card.id])
    decisions = [{"offers": [_Offer("picked"), _Offer("rival")],
                  "picked": "picked"}]

    gaps = draft.draft_regret_gaps(_AlwaysSample(), decisions, [], "demolition",
                                   sample=1.0)
    assert gaps == [1.0]
    assert draft.draft_regret(_AlwaysSample(), decisions, [], "demolition") == 0
