"""`run_many(jobs=N)` is a wall-clock lever, never a fidelity one.

Run i is a pure function of `seed + i` (spec §2: one Random per run, no
global state), so spreading the batch over worker processes must return the
SAME list, element for element. If that ever stops holding, every archived
Tier 0.5 number becomes uncomparable to anything measured with --jobs -- so
it is pinned rather than assumed.
"""

from __future__ import annotations

import warnings

import pytest

from tier05 import draft, model


def _fingerprint(results):
    return [(r.seed, r.won, r.death_node, tuple(r.hp_by_node),
             tuple(r.deck_ids), r.gold, r.regret_samples, r.time_to_online,
             tuple(r.relics), tuple(r.potions_used), r.acts_completed,
             tuple((d["node"], d["picked"]) for d in r.decisions))
            for r in results]


RUNS = 7          # deliberately not a multiple of the job counts below


@pytest.mark.parametrize("jobs", [2, 3, RUNS + 2])
def test_parallel_batches_match_the_serial_batch(jobs):
    kw = dict(grant_relics=True, grant_potions=True, n_acts=1)
    serial = model.run_many("ref_ironclad", "generic", "generic",
                            draft.POLICIES["assigned"], RUNS, 11,
                            jobs=1, **kw)
    parallel = model.run_many("ref_ironclad", "generic", "generic",
                              draft.POLICIES["assigned"], RUNS, 11,
                              jobs=jobs, **kw)
    assert len(parallel) == RUNS
    assert _fingerprint(parallel) == _fingerprint(serial)


def test_more_jobs_than_runs_does_not_lose_or_duplicate_runs():
    # Empty chunks are dropped rather than dispatched; the seeds must still
    # come back exactly once each, in order.
    res = model.run_many("ref_ironclad", "generic", "generic",
                         draft.POLICIES["assigned"], 3, 11, jobs=8, n_acts=1)
    assert [r.seed for r in res] == [11, 12, 13]


def test_unpicklable_policy_falls_back_to_serial_with_a_warning():
    """An experiment script may pass its own closure. Running it in-process
    beats refusing to run it -- but silently ignoring `jobs` would be a lie,
    so it warns."""
    calls = []

    def custom_policy(rng, deck, offers, archetype):
        calls.append(1)
        return draft.POLICIES["assigned"](rng, deck, offers, archetype)

    with pytest.warns(UserWarning, match="running serially"):
        res = model.run_many("ref_ironclad", "generic", "generic",
                             custom_policy, 2, 11, jobs=4, n_acts=1)
    assert len(res) == 2
    assert calls                     # the caller's own policy really ran

    with warnings.catch_warnings():
        warnings.simplefilter("error")      # jobs=1 must not warn
        model.run_many("ref_ironclad", "generic", "generic", custom_policy,
                       1, 11, jobs=1, n_acts=1)
