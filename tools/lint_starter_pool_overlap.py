#!/usr/bin/env python3
"""EB-255: the "rarity separates starter from drafted" invariant, made checkable.

WHAT IS BEING LINTED. `tier05.draft.archetype_shares` -- the `_committed_share`
the adaptive drafter classifies a deck by, and the rest plan `tier05.model`
picks off `dominant_archetype` -- excludes the starting deck from "what has
been drafted" by asking `c.rarity != "basic"`. Its docstring states the
invariant that makes that exclusion exact, in these words:

    Rarity separates the two exactly: every starter card is basic and basic
    never appears in the draftable pool.

Nothing checked it, and it is FALSE. [USER]'s manual solo Kokomi playtest
(2026-08-31, finding `B1`) found it from the other end: a starter card that is
not basic is read back as a card the drafter chose, so a run is credited with
a commitment it was dealt at floor zero -- which is the exact contamination
the basics exclusion exists to prevent, arriving through the door the
exclusion left open.

THREE CLAIMS, LINTED SEPARATELY, because they fail differently:

  (1) every starter card is `basic`
  (2) no `basic` card is offerable in the draftable pool
  (3) no starter card id is ALSO offerable

(2) is a clean gate today and carries no debt. (1) and (3) carry the curated
DEBT set below, the structurally-invisible-defects pattern this repo already
runs six other gates on: the lint is GREEN from this commit forward while the
known rows are a work list, a NEW violation is red, and a DEBT row that has
become clean is ALSO red -- so the set can only shrink, and it cannot rot.

WHAT THIS LINT DOES NOT DO, and it is the reason the row is not closed by it.
The fix the row names -- "exclude by starter membership, not rarity" -- moves
`archetype_shares` for Furina and Kokomi, therefore `dominant_archetype`,
therefore the rest plan and the adaptive drafter, therefore every tier-0.5
number those produce. That is a `POLICY_VERSION` window with a re-baseline,
and it needs a slate. This lint is the half that can land without one: it
makes the invariant a thing the repo can see, and it is what will prove the
fix complete when the window opens.

THE FLAGGED ARMS ARE LINTED TOO. `to_the_front` is a common that enters
Kokomi's starter only under `C.KURAGE_MEMORY`, so a lint that read the live
tree alone would call the row clean and then go red the day the flag flips --
which is the day nobody is looking at this file. Every arm that moves a
starter is walked, through `loader.starting_deck` and `loader.starter_
replaced_whole` (the named seam for a whole-starter replacement, PR #276);
this file derives no starter of its own.

Usage: python tools/lint_starter_pool_overlap.py
Exit 1 with findings on stdout if the debt set and the tree disagree.
"""

from __future__ import annotations

import sys
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tier0 import constants as C                            # noqa: E402
from tier0.content import loader                            # noqa: E402
from tier0.engine import furina_reframe                     # noqa: E402
from tier05 import rewards                                  # noqa: E402


# The rows failing (1) or (3) today, as `(arm, character, card id, claims)`.
# `arm` is the flag tree the row is reachable in; `claims` is which of the
# three numbered claims above it breaks.
#
# TWELVE OF THE THIRTEEN NON-BASIC STARTER ROWS ARE COMPANIONS, and they are
# debt of a milder kind: `archetype_shares(companions=False)` -- the
# classification call, the one `_committed_share` is -- already drops them for
# their own documented reason, and no companion is offerable, so none of them
# can reach the defect `B1` found. They are listed because claim (1) is what
# the docstring says and they do break it; a fix that switches to starter
# membership makes all thirteen correct at once.
DEBT: tuple[tuple[str, str, str, tuple[int, ...]], ...] = (
    # The one row that actually contaminates `_committed_share`: a common,
    # NOT a companion, carrying the `spotlight` archetype tag, shipped in
    # Furina's starter AND in her reward pool. Every Furina run is credited
    # with one drafted spotlight card before a reward screen is shown.
    ("shipped", "furina", "an_invitation", (1, 3)),
    ("shipped", "furina", "charlotte_enduring_frosthelm", (1,)),
    ("shipped", "furina", "chevreuse_interdiction_fire", (1,)),
    ("shipped", "furina", "freminet_pers_deploy", (1,)),
    ("shipped", "furina", "lynette_enigmatic_feint", (1,)),
    ("shipped", "klee", "barbara_melody", (1,)),
    ("shipped", "klee", "dahlia_sacramental_shower", (1,)),
    ("shipped", "klee", "kaeya_frostgnaw", (1,)),
    ("shipped", "klee", "prune_witch_hunt", (1,)),
    ("shipped", "kokomi", "gorou_inuzaka_charge", (1,)),
    ("shipped", "kokomi", "sayu_daruma_gift", (1,)),
    ("shipped", "kokomi", "shinobu_grass_ring_bond", (1,)),
    # The row the playtest named beside `an_invitation`, and the reason this
    # lint walks the flagged arms: the second contaminator, one flag away.
    # Listed under the arm that ADDS it -- a flagged arm reports only its
    # delta from the shipped tree, so the three shipped Kokomi companion rows
    # above are not repeated here.
    ("kurage_memory", "kokomi", "to_the_front", (1, 3)),
)


def _drop_caches() -> None:
    """Every memoized view of the content tree, on BOTH sides of the seam.

    `loader.reset_caches` is the one door for tier 0's, and the tier-0.5
    reward pools are memoized separately -- they hold `Card` OBJECTS built
    from whichever tree was live when they were filled, so leaving them warm
    across a flag flip serves a prototype card out of a flag-off tree and
    raises on the next id resolution. Both halves, one helper, because
    clearing one of them is how this goes subtly wrong.
    """
    loader.reset_caches()
    rewards.character_pool.cache_clear()
    rewards.companion_pool.cache_clear()


@contextmanager
def _arm(module=C, **flags):
    """Read the content tree under a flag set, then put it back.

    `module` is WHERE the flags live, and it DEFAULTS to `constants.py`
    because that is where four of the five arms declare theirs -- so every
    caller that names only flags keeps working unchanged. The fifth, the
    Furina reframe, declares its master in `tier0/engine/furina_reframe.py` on
    purpose: a flag in `constants.py` is read by the parity gate and the
    constant census, and that module's header gives the argument in full. A
    helper that could only reach `C` would have to skip the one arm whose flag
    is quarantined hardest, which is exactly the arm nobody is watching.
    """
    old = {k: getattr(module, k) for k in flags}
    try:
        for k, v in flags.items():
            setattr(module, k, v)
        _drop_caches()
        yield
    finally:
        for k, v in old.items():
            setattr(module, k, v)
        _drop_caches()


# Every arm that moves a starter, and nothing else: an arm that changes only
# the offerable pool cannot move claim (1), and claim (2) is swept on the
# shipped tree where every published number was taken. Each row names the
# module its flags live in -- see `_arm`.
ARMS: tuple[tuple[str, object, dict], ...] = (
    ("shipped", C, {}),
    ("kurage_memory", C, {"KURAGE_MEMORY": True}),
    ("kokomi_overhaul", C, {"KOKOMI_OVERHAUL": True}),
    ("klee_overhaul", C, {"KLEE_OVERHAUL": True}),
    ("spark_alt_cost", C, {"SPARK_ALT_COST_ENABLED": True}),
    # R254: her starter reader. One `basic` row swapped for one `basic` row,
    # so the arm's delta ought to be empty -- which is the assertion, not an
    # exemption.
    ("furina_reframe", furina_reframe, {"FURINA_REFRAME": True}),
)


def _starter_universe(character_id: str) -> list[str]:
    """Every card id that can open a run as this character's starter.

    The printed ten (or twelve) PLUS every `randomized_starter` choice, which
    is a starter slot too -- a card the run is dealt and never drafted. A
    whole-starter replacement has no slot to roll, and `loader.starter_
    replaced_whole` is the named predicate for that; asking it here rather
    than re-deriving the answer is the point of the seam.
    """
    ids = list(loader.starting_deck(character_id))
    if not loader.starter_replaced_whole(character_id):
        spec = loader._character_index()[character_id]
        for slot in spec.get("randomized_starter", {}).values():
            ids += list(slot["choices"])
    return ids


def _offerable(character_id: str) -> set[str]:
    """The draftable pool: exactly what `rewards.character_pool` will offer,
    which is the single source of truth for every offer surface."""
    return {c.id for cards in rewards.character_pool(character_id).values()
            for c in cards}


def _arm_rows(basics_offered: list[str], sweep_basics: bool
              ) -> dict[tuple[str, str], tuple[int, ...]]:
    """`{(character, card id): broken claims}` for the tree as it stands."""
    out: dict[tuple[str, str], tuple[int, ...]] = {}
    for character_id in sorted(loader._character_index()):
        try:
            starter = _starter_universe(character_id)
            pool = _offerable(character_id)
        except Exception as exc:                    # a defect of its own
            basics_offered.append(
                f"{character_id}: could not read the starter or the pool "
                f"-- {exc}")
            continue
        if sweep_basics:
            for cid in sorted(pool):
                if loader.get_card(cid).rarity == "basic":
                    basics_offered.append(
                        f"{character_id}: basic {cid!r} is offerable -- "
                        f"claim (2) is the one gate here with no debt, so "
                        f"this is a new defect")
        for cid in sorted(set(starter)):
            claims = []
            if loader.get_card(cid).rarity != "basic":
                claims.append(1)
            if cid in pool:
                claims.append(3)
            if claims:
                out[(character_id, cid)] = tuple(claims)
    return out


def findings() -> tuple[dict[tuple[str, str, str], tuple[int, ...]], list[str]]:
    """`({(arm, character, card id): broken claims}, claim-2 failures)`.

    A flagged arm reports only what it ADDS to the shipped tree. Every arm
    moves one character's starter and leaves the other two alone, so echoing
    the shipped rows back under four more names would bury the one row an arm
    is actually responsible for -- which is the row a reader came here for.
    """
    basics_offered: list[str] = []
    shipped = _arm_rows(basics_offered, sweep_basics=True)
    rows = {("shipped", c, i): claims for (c, i), claims in shipped.items()}
    for arm_name, module, flags in ARMS:
        if not flags:
            continue
        with _arm(module, **flags):
            for key, claims in _arm_rows(basics_offered,
                                         sweep_basics=False).items():
                if shipped.get(key) != claims:
                    rows[(arm_name, *key)] = claims
    return rows, basics_offered


def main() -> int:
    seen, basics_offered = findings()
    known = {(a, c, i): claims for a, c, i, claims in DEBT}

    new = sorted(k for k in seen if k not in known)
    fixed = sorted(k for k in known if k not in seen)
    changed = sorted(k for k in seen.keys() & known.keys()
                     if seen[k] != known[k])

    print(f"starter/pool overlap: {len(seen)} row(s) over {len(ARMS)} arm(s); "
          f"DEBT holds {len(known)}")
    for arm, character_id, cid in sorted(seen):
        mark = "DEBT" if (arm, character_id, cid) in known else "NEW "
        claims = ", ".join(str(n) for n in seen[(arm, character_id, cid)])
        print(f"  {mark} {arm}/{character_id}: {cid} breaks claim(s) {claims}")

    ok = True
    for line in basics_offered:
        print(f"  FAIL {line}")
        ok = False
    for arm, character_id, cid in new:
        print(f"  FAIL new violation {arm}/{character_id}: {cid} -- either "
              f"fix it or add it to DEBT with the row that justifies it")
        ok = False
    for arm, character_id, cid in fixed:
        print(f"  FAIL {arm}/{character_id}: {cid} is in DEBT and is now "
              f"clean -- delete the DEBT entry (the set may only shrink)")
        ok = False
    for arm, character_id, cid in changed:
        print(f"  FAIL {arm}/{character_id}: {cid} breaks claims "
              f"{seen[(arm, character_id, cid)]}, DEBT records "
              f"{known[(arm, character_id, cid)]}")
        ok = False

    print("OK" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
