"""The standing rule, made executable: policy seeds are not game seeds.

`understudy/` is a new stochastic surface, so it gets its own stream (the
brief's P1 line, and tier05's own convention of offsetting a run seed by
multiples of 1e9). The sharper half is specific to this apparatus: the GAME
seed indexes the run content the policy is choosing OVER. A policy keyed on it
would be a function of its own question, and every counterfactual the sprint
produces would inherit that correlation silently.

So the refusal is coded, not merely documented -- prose does not stop a seed
from being passed at 3am.
"""

import pytest

from understudy import rng


def test_policy_streams_are_separated_from_tier05s_offsets():
    # tier05/model.py uses +1e9, +2e9, +3e9. Understudy must not land on one.
    assert rng.UNDERSTUDY_STREAM_OFFSET % 10**9 == 0
    assert rng.UNDERSTUDY_STREAM_OFFSET // 10**9 not in (0, 1, 2, 3)


def test_sub_streams_do_not_share_a_sequence():
    a = [rng.policy_rng("draft").random() for _ in range(3)]
    b = [rng.policy_rng("route").random() for _ in range(3)]
    assert a != b, "two sub-policies drawing the same numbers is one stream"


def test_a_stream_is_reproducible():
    assert (rng.policy_rng("draft").random()
            == rng.policy_rng("draft").random())


def test_a_game_seed_is_refused():
    """The shape of the failure: someone passes the run's seed as a label
    because it is the identifier nearest to hand."""
    with pytest.raises(rng.GameSeedLeak):
        rng.policy_rng("SSRWEGLNRG")
    with pytest.raises(rng.GameSeedLeak):
        rng.policy_rng("1A2B3C4D")


def test_ordinary_labels_still_work():
    assert rng.policy_rng("draft") is not None
    assert rng.policy_rng("") is not None
