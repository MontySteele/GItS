"""THE COMPANION STAND-IN SEAM (`C.COMPANION_OVERHAUL`).

A STAND-IN IS NOT A POOL MEMBER. It is a whole Klee-only card, with its own
unique name, handed to Klee IN PLACE of one named Universal (Klee brief pick 6;
the approved Mondstadt workshop sec.1; R236 sec.3). Every rule the seam has
follows from that one sentence:

  * it never enters ANY pool on its own -- not the character-blind Universal
    pool (`tier05.rewards.companion_pool`), not the Personal reward share, not
    a shop slot, not the Featured Banner, not an event. The ids are absent from
    `C.MONDSTADT_OVERHAUL_POOL_IDS`, so `companion_roster_replacement` cannot
    return one and no surface can tier one;
  * it is reached at the HAND-OFF and nowhere else -- after a surface has
    rolled its rarity and picked its card, `hand_off` swaps the Universal for
    the stand-in if this character owns one. The candidate lists, the rng
    stream and the weights are untouched, so THE OFFER ODDS DO NOT MOVE: a
    stand-in is offered exactly as often as the Universal it replaces was;
  * every other character is handed the Universal and never sees the stand-in,
    because the swap is keyed on `(replaces, personal_pool)`.

THE MAP IS DERIVED FROM THE SHEET, never listed here. A row states which
Universal it replaces (`replaces:`) and who may be handed it (`personal_pool:`);
a second, hand-copied table would be a list somebody must remember to update
and would fail silently the day a row is renamed.

C# TWIN: `KleeMod.Powers.CompanionStandIns`, which holds the same pair table
(by TYPE, so the compiler owns the correspondence) and is called from the same
two mouths -- the reward slot and the shop channel.

FLAG OFF EVERY FUNCTION HERE IS A NO-OP, checked at the top of each rather than
assumed by its callers, which is what makes the byte-identity pin
(`tier0/tests/test_companion_standins.py`) a property of this module.

THE STAND-INS ARE GONE SINCE THE KLEE-ONLY COMPANIONS (2026-10-03,
review/active/mondstadt-companions-2026-10-03.md sec.4): four were cut, three
joined the shared pool and two joined Klee's own draftable pool. The seam
stays with nothing to hand off (`C.COMPANION_STANDIN_IDS` is empty), and the
one rule left here is Jean's Lion's Fang, Fair Protector -- a POWER,
Grounded's shape with a card on it: at the start of your turn, if none of your
Bombs went off last turn, gain its stacks in Block and draw one.
"""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

from tier0 import constants as C

if TYPE_CHECKING:                                   # pragma: no cover
    from tier0.engine.state import Card, CombatState

#: Jean's power. Stacks are the Block, Grounded's own grammar.
LIONS_FANG = "mc_lions_fang"


# --- the sheet contract ------------------------------------------------------

def validate_row(card: "Card") -> None:
    """`replaces:` is prototype surface only, and it needs a `personal_pool:`.

    Run from `loader._validate_card_shape`, which every sheet row passes
    through -- shipped and staged alike -- so the two halves are checked in one
    place:

    IT IS PROTOTYPE SURFACE ONLY, the same rule `description:` and `plan:`
    carry and for the same reason. A stand-in is a quarantined arm's card; a
    shipped row claiming to replace another would be a second, permanent pool
    rule wearing a schema key, and R213 B's deletion rule could never reach it.

    IT CANNOT BE ANONYMOUS -- UNLESS IT IS THE OTHER SHAPE. `replaces:`
    without `personal_pool:` names no character to hand the card to, so it is
    not a stand-in: it is a row that replaces another FOR EVERYBODY playing the
    arm, which is a SUBSTITUTION -- at the offer door
    (`loader._pool_substitutions`, the Kurage's Oath seam) or at the printed
    starter (`loader._starter_ids`, the Kurage's slot eleven). That shape is
    legal, and this is the only place the two meanings are told apart, so it is
    CHECKED rather than assumed: the row must be named in
    `loader.declared_pool_substitutions()` or
    `loader.declared_starter_substitutions()`, the flag-blind unions of the
    arms' own maps. A `replaces:` that names neither a character to hand the
    card to nor a declared swap is a row no surface can ever reach, and still
    raises.

    Furina's arm rows are the users of the second shape at the offer door,
    and her arm STARTERS are the reason the check reads two maps rather than
    one: a starter row is `basic`, so the POOL map could never legally name
    it. The Mondstadt stand-ins are the
    first shape and nothing about them moves -- `_replacements` has always
    filtered on `personal_pool`.
    """
    from tier0.content.loader import (PROTOTYPE_ID_PREFIX,
                                      declared_pool_substitutions,
                                      declared_starter_substitutions)

    if card.replaces is None:
        return
    if not card.id.startswith(PROTOTYPE_ID_PREFIX):
        raise ValueError(
            f"card {card.id!r}: `replaces:` is prototype surface only -- a "
            f"shipped row may not stand in for another card (ids on that "
            f"surface carry {PROTOTYPE_ID_PREFIX!r})")
    if not card.personal_pool:
        if (declared_pool_substitutions().get(card.replaces) == card.id
                or declared_starter_substitutions().get(card.replaces)
                == card.id):
            return
        raise ValueError(
            f"card {card.id!r}: `replaces:` needs a `personal_pool:` -- a "
            "stand-in is handed to ONE character in place of a Universal -- "
            "or an arm's pool- or starter-substitution map has to name it. A "
            "row that replaces another for everybody and is in no arm's map "
            "can never be dealt or offered at all")


@lru_cache(maxsize=1)
def _replacements() -> dict[tuple[str, str], str]:
    """`(universal id, character id) -> stand-in id`, derived from the sheet.

    Memoized off `loader._prototype_index`, which is itself the memoized read
    of the surface; `loader.reset_caches` drops both together.
    """
    from tier0.content import loader

    return {(c.replaces, c.personal_pool): c.id
            for c in loader._prototype_index().values()
            if c.replaces is not None and c.personal_pool}


def hand_off(card_id: str, character_id: str | None) -> str:
    """THE HAND-OFF, and the whole seam in the sim.

    Every companion offer surface calls this on the id it is about to hand
    over, AFTER the pick: `tier05.rewards.roll_rewards` (the reward slot) and
    `tier05.shop.companion_offers` (both shop slots). Called on the picked card
    rather than on the candidate list on purpose -- the lists, the weights and
    the rng draws are then provably the Universal's own, so no offer's odds can
    move.

    Returns `card_id` unchanged for every character but the stand-in's, and for
    every build with the arm off.
    """
    if character_id is None:
        return card_id
    return _replacements().get((card_id, character_id), card_id)


def standin_ids() -> tuple[str, ...]:
    """Every stand-in the surface declares, sorted. The test seam, and the
    derivation `C.COMPANION_STANDIN_IDS` is pinned against."""
    return tuple(sorted(_replacements().values()))


# --- Jean's rule ---------------------------------------------------------

def turn_start(state: "CombatState") -> None:
    """Jean, Lion's Fang, Fair Protector -- Grounded's shape with a card on it.

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
