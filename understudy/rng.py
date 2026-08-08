"""Dedicated RNG streams for the bot apparatus.

Standing rule, restated by the Understudy brief and inherited from tier05:
**a new stochastic surface gets its own stream, and policy seeds never share a
stream with game seeds.** tier05 implements that by offsetting a run seed by
multiples of 1e9 (`model.py`: +2e9 Featured Banner, +3e9 randomized starter);
those offsets are effectively the contract, so this module takes the next free
one and writes down which.

There is a second, sharper separation here that tier05 never needed. The GAME
seed is not ours at all -- it is an alphanumeric string the game generates and
owns, it indexes generated run content, and it is the thing our measurements
are conditioned on. Feeding it into a policy RNG would make the policy's
choices a function of the map it is choosing on, which is the one correlation
that would quietly invalidate every counterfactual this sprint produces.

So: the game seed is recorded, never consumed. `policy_rng` refuses it.
"""

from __future__ import annotations

import random

# THE OFFSET REGISTRY. Every dedicated stream in the repo takes a distinct
# multiple of 1e9 off the same seed, and is recorded here so the next one can
# see what is taken:
#   1e9  draft regret          tier05/draft.py
#   2e9  featured banner       tier05/model.py
#   3e9  randomized starter    tier05/model.py
#   4e9  hand-full selector    tier0/engine/combat.py (CombatState.selector_rng;
#                              sitting 2026-08-06, family X14 leg (b))
#   5e9  route regret          tier05/model.py (EB-16w, 2026-08-07)
#   7e9  understudy policy     this module
# Understudy takes 7e9 and leaves room between.
UNDERSTUDY_STREAM_OFFSET = 7 * 10**9

# The policy's own base seed. Deliberately a constant and not derived from
# anything about the run: policy_v0 is meant to be reproducible ACROSS runs,
# so that two runs disagreeing is a fact about the runs.
POLICY_BASE_SEED = 20260804


class GameSeedLeak(RuntimeError):
    """A game seed reached a policy RNG. See this module's docstring."""


def policy_rng(label: str = "") -> random.Random:
    """A policy-side stream, keyed only by a caller-chosen label.

    `label` distinguishes sub-policies (draft / route / combat) so that adding
    a roll to one of them cannot renumber another's sequence -- the same
    reasoning as tier05's per-surface offsets, one level down.
    """
    if _looks_like_a_game_seed(label):
        raise GameSeedLeak(
            f"refusing to key a policy stream on {label!r}: that is the shape of "
            f"a game seed, and the policy must not be a function of the content "
            f"it is choosing over")
    mixed = POLICY_BASE_SEED + UNDERSTUDY_STREAM_OFFSET + _label_offset(label)
    return random.Random(mixed)


def _label_offset(label: str) -> int:
    # Stable across processes, unlike hash(). Small, so streams stay adjacent
    # and legible in a log rather than looking like unrelated magic numbers.
    total = 0
    for i, ch in enumerate(label):
        total += (i + 1) * ord(ch)
    return total


def _looks_like_a_game_seed(label: str) -> bool:
    s = label.strip()
    if len(s) < 6:
        return False
    # STS2 seeds are uppercase alphanumeric words with no separators
    # (SSRWEGLNRG, 1A2B3C4D). Policy labels are lowercase words by convention,
    # so "no lowercase character anywhere" separates the two without needing
    # the seed alphabet to be known. Deliberately over-eager: a refused label
    # costs a rename, an accepted seed costs every counterfactual in the run.
    return s.isalnum() and not any(c.islower() for c in s)
