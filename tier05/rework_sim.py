"""The hardened idiom for measuring a card rework in-process (`EB-49`).

Patching `loader._card_index()[cid].effects` and running the sim again is the
cheapest A/B there is, and three ways of doing it silently measure the SHIPPED
card twice — the delta comes out ~0 and reads as "the rework does nothing":

  (a) STALE PROTOTYPES. `loader._card_prototype` is `lru_cache(maxsize=None)`
      and builds each `<id>+` form by deep-copying the base card, so any run
      before the patch leaves every upgraded copy holding the shipped effects.
      `patched_cards` clears that cache on entry AND on exit.
  (b) LOST PATCH. `model.run_many(jobs != 1)` crosses a `ProcessPoolExecutor`
      boundary; workers re-import and re-load the sheets, so they run the
      shipped card. `run_many` here refuses anything but `jobs=1`.
  (c) BASE-ID-ONLY KEYING. Offer/pick/fire-rate events carry the PLAYED card's
      id, so a dict keyed by base id drops every `<id>+` copy — the upgraded
      form of the reworked card, which is exactly the population under test.
      That one is the caller's to avoid: fold event ids through `base_id`
      before keying.
"""

from __future__ import annotations

import contextlib
import copy
import inspect
from typing import Iterator

from tier0.content import loader, upgrades
from tier05 import model

# Bound at import: `jobs` is a positional-or-keyword parameter, so the guard
# has to read it the way the callee would rather than off `kwargs`.
_RUN_MANY_SIG = inspect.signature(model.run_many)


@contextlib.contextmanager
def patched_cards(reworks: dict[str, list[dict]]) -> Iterator[None]:
    """Run the body with `reworks` (base id -> effect list) as the live cards.

    The index holds one shared Card per id, so the patch is a mutation and the
    restore has to be exact: pristine effects are deep-copied out first and
    put back on the way out, exception or not.
    """
    index = loader._card_index()
    unknown = sorted(cid for cid in reworks if cid not in index)
    if unknown:
        raise KeyError(
            f"unknown card id(s) {unknown} in rework patch; patch base ids "
            f"only (`<id>+` forms are derived, not indexed)")

    pristine = {cid: copy.deepcopy(index[cid].effects) for cid in reworks}
    try:
        for cid, effects in reworks.items():
            index[cid].effects = copy.deepcopy(effects)
        loader._card_prototype.cache_clear()
        yield
    finally:
        for cid, effects in pristine.items():
            index[cid].effects = effects
        loader._card_prototype.cache_clear()


def run_many(*args, **kwargs):
    """`model.run_many`, refusing the job counts that would drop the patch.

    Signature is `model.run_many`'s; `jobs=0` (one worker per CPU) is a
    rejection too, not a default.
    """
    bound = _RUN_MANY_SIG.bind(*args, **kwargs)
    jobs = bound.arguments.get("jobs", 1)
    if jobs != 1:
        raise ValueError(
            f"rework sims must run jobs=1, got jobs={jobs!r}: run_many "
            "spreads the batch over a ProcessPoolExecutor, and the in-process "
            "card patch does not survive that boundary — the workers would "
            "A/B the shipped card against itself")
    return model.run_many(*args, **kwargs)


def base_id(card_id: str) -> str:
    """`'kaboom+'` -> `'kaboom'`; anything else unchanged.

    For keying offer/pick/fire-rate tallies, so an upgraded copy counts with
    the card it was upgraded from (`EB-49` clause c).
    """
    if card_id.endswith(upgrades.SUFFIX):
        return card_id[:-len(upgrades.SUFFIX)]
    return card_id
