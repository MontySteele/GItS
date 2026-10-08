"""Jean, Lion's Fang, Fair Protector -- a Klee-own companion's one rule.

A POWER, Grounded's shape with a card on it: at the start of your turn, if
none of your Bombs went off last turn, gain its stacks in Block and draw one.

C# TWIN: `KleeMod.Powers.LionsFangPower` (`Powers/Prototype/LionsFangPower.cs`).

Jean was a companion stand-in until the Klee-only companions (2026-10-03,
review/active/mondstadt-companions-2026-10-03.md sec.4) put her in Klee's own
draftable pool. The empty stand-in seam that used to hold this rule was
deleted on 2026-10-08 (project review 2026-10-08, pick 3).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tier0 import constants as C

if TYPE_CHECKING:                                   # pragma: no cover
    from tier0.engine.state import CombatState

#: Jean's power. Stacks are the Block, Grounded's own grammar.
LIONS_FANG = "mc_lions_fang"


def turn_start(state: "CombatState") -> None:
    """Pay Lion's Fang on a quiet turn.

    Called from the tail of `effects.companion_overhaul_turn_start`, which is
    where this arm's start-of-turn payouts live, and it is COMMUTATIVE with the
    ones already there: it grants the player Block and a card, and none of
    them reads a value it writes.

    IT READS `ko_set_off_last_turn` DIRECTLY, so it agrees with Grounded by
    construction.
    """
    p = state.player
    n = p.powers.get(LIONS_FANG, 0)
    if not n or state.ko_set_off_last_turn != 0:
        return
    p.block += n
    state.emit("block", amount=n)
    state.draw(C.MC_LIONS_FANG_DRAW)
    state.emit("extra_draw", amount=C.MC_LIONS_FANG_DRAW)
    state.emit("mc_lions_fang", amount=n)
