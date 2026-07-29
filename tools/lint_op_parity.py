#!/usr/bin/env python3
"""Parity lint: the engine's OPS registry vs the drafter's priced-op set.

WHY THIS EXISTS. `tier05.draft._static_power` is the offer-time power
estimate -- what a card is worth on a reward screen, before any combat state
exists. It works by enumerating ops. For most of this project's life it
enumerated TEN of them, and the engine registry had grown to fifty-six, so
forty-six ops were priced at exactly zero: not "approximately zero", not
"conservatively low", but INVISIBLE. A card whose whole printed text was one
of those ops read to every drafting arm as blank cardboard.

That defect has now been found four separate times, always the same way --
somebody noticed one character drafting badly and traced it back:

    DRAFTER_VERSION 6   all_enemies damage counted one body   (Furina 0%)
    DRAFTER_VERSION 7   conscript / gain_charge / Sly riders  (Kokomi v0.2)
    DRAFTER_VERSION 8   summon_kurage                         (Kokomi v0.4)
    DRAFTER_VERSION 9   fanfare floor grants                  (Furina F-A7)

Four discoveries, four one-character fixes, and no reason to think the fifth
would have been found any faster. DRAFTER_VERSION 13 priced the whole
registry at once; this lint is what stops the population from regrowing. It
is the same instrument `tools/lint_constant_parity.py` is for the C# mirrors,
pointed at a different correspondence.

THE DISCIPLINE (tier0's UNAPPLIABLE, applied again). Every key of
`tier0.engine.effects.OPS` must appear in `tier05.draft.STATIC_OP_PRICING`
with a one-line rationale for the price it receives -- including the ops
priced at ZERO, which must say so and say why. An op in the registry with no
entry is a FINDING, not a skip. That is what makes this survive contact with
future work: registering an op forces a pricing decision at the moment the
author still knows the answer, rather than leaving a silent zero for a
sprint six months later to rediscover by measuring a character.

The lint also runs the pricer over EVERY committed card, because a table
entry is a promise and `_op_price` is the thing that keeps it: an op listed
in the table but missing from the function raises KeyError there, and this
is where that surfaces.

Run: python tools/lint_op_parity.py
Exit 1 with findings on stdout.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from tier0 import constants as C            # noqa: E402
from tier0.content import loader            # noqa: E402
from tier0.engine.effects import OPS        # noqa: E402
from tier05 import draft                    # noqa: E402


def findings() -> list[str]:
    out: list[str] = []
    registry = set(OPS)
    priced = set(draft.STATIC_OP_PRICING)

    for op in sorted(registry - priced):
        out.append(
            f"UNPRICED OP: {op!r} is registered in tier0.engine.effects.OPS "
            f"but has no entry in tier05.draft.STATIC_OP_PRICING. Every op "
            f"needs a price and a one-line rationale -- including a "
            f"deliberate zero, which must say ZERO and say why. A card built "
            f"on an unpriced op is worth nothing to the drafter, silently.")
    for op in sorted(priced - registry):
        out.append(
            f"STALE PRICE: {op!r} has an entry in "
            f"tier05.draft.STATIC_OP_PRICING but is not in the engine's OPS "
            f"registry. Either the op was renamed or removed; the price is "
            f"now documenting a verb the engine cannot resolve.")
    for op, why in sorted(draft.STATIC_OP_PRICING.items()):
        if not str(why).strip():
            out.append(
                f"EMPTY RATIONALE: {op!r} is listed but says nothing about "
                f"why it is priced the way it is. The sentence IS the lint.")

    # The table is a promise; `_op_price` is what keeps it. Sweep every
    # committed card so a listed-but-unimplemented op fails HERE rather than
    # in the middle of somebody's 7,200-run measurement.
    for cid, card in sorted(loader._card_index().items()):
        try:
            draft._static_power(card)
        except Exception as exc:            # noqa: BLE001 -- reported, not raised
            out.append(
                f"PRICER FAILED on card {cid!r}: {type(exc).__name__}: {exc}")
    return out


def main() -> int:
    bad = findings()
    for line in bad:
        print(line)
    if bad:
        print(f"\n{len(bad)} finding(s). "
              f"DRAFTER_VERSION is {C.DRAFTER_VERSION}; a change to the "
              f"priced-op set is a DRAFTER_VERSION bump, and every number "
              f"measured in the old world is archived by house rule.")
        return 1
    print(f"op parity OK: {len(OPS)} registered ops, "
          f"{len(draft.STATIC_OP_PRICING)} priced, "
          f"{len(loader._card_index())} cards priced without error "
          f"(DRAFTER_VERSION {C.DRAFTER_VERSION})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
