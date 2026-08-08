"""Pin tests for the hardened rework-sim helper (`EB-49`).

Each test locks one of the three ways the naive in-process patch measured the
shipped card instead of the reworked one. No Monte Carlo here on purpose: the
failures are all cache/boundary bookkeeping, visible from the prototypes and
the argument check alone.
"""

from __future__ import annotations

import pytest

from tier0.content import loader, upgrades
from tier05 import draft, model, rework_sim

# A base card with a real upgrade delta (`kaboom: {damage: +3}`), so the
# upgraded prototype is DERIVED from the patched effects rather than sharing
# the object -- which is what makes the stale cache observable.
CARD = "kaboom"
UPGRADED = CARD + upgrades.SUFFIX
PATCH = {CARD: [{"op": "damage", "amount": 1, "target": "enemy"}]}


def _damage(card_id: str) -> int:
    return loader.peek_card(card_id).effects[0]["amount"]


def test_patch_reaches_the_upgraded_prototype():
    """Failure mode (a): a run before the patch memoizes `<id>+` with the
    SHIPPED effects, so the sim A/Bs the shipped card against itself."""
    shipped_base = _damage(CARD)
    shipped_up = _damage(UPGRADED)         # warms the lru_cache -- the trap
    assert shipped_up > shipped_base

    with rework_sim.patched_cards(PATCH):
        assert _damage(CARD) == 1
        assert _damage(UPGRADED) == 1 + (shipped_up - shipped_base)


def test_exit_restores_both_forms():
    shipped = (_damage(CARD), _damage(UPGRADED))
    with rework_sim.patched_cards(PATCH):
        pass
    assert (_damage(CARD), _damage(UPGRADED)) == shipped


def test_exit_restores_on_exception():
    shipped = (_damage(CARD), _damage(UPGRADED))
    with pytest.raises(RuntimeError):
        with rework_sim.patched_cards(PATCH):
            raise RuntimeError("the sim died mid-batch")
    assert (_damage(CARD), _damage(UPGRADED)) == shipped


def test_unknown_card_id_is_loud():
    with pytest.raises(KeyError, match="no_such_card"):
        with rework_sim.patched_cards({"no_such_card": []}):
            pass


@pytest.mark.parametrize("jobs", [2, 0])
def test_run_many_refuses_parallel(monkeypatch, jobs):
    """Failure mode (b): the patch does not cross the ProcessPool boundary.
    The refusal must land BEFORE any run happens, hence the tripwire."""
    def never(*args, **kwargs):
        raise AssertionError("run_many should have refused before running")

    monkeypatch.setattr(model, "run_many", never)
    with pytest.raises(ValueError, match="jobs=1"):
        rework_sim.run_many("klee", "generic", "generic",
                            draft.POLICIES["assigned"], 1, 0, jobs=jobs)


def test_base_id_strips_the_upgrade_suffix():
    """Failure mode (c) is the caller's to avoid; this is the tool."""
    assert rework_sim.base_id(UPGRADED) == CARD
    assert rework_sim.base_id(CARD) == CARD
