"""THE COMPANION STAND-IN SEAM (QUARANTINED, `C.COMPANION_OVERHAUL`).

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

THE FIVE CARETAKERS' RULES also live here, for the reason the seam does: they
are the only rules that read a stand-in, and a new file is what keeps a
quarantined arm's whole behaviour greppable in one place.

  * Shaken, Not Purred (Diona) -- ONE-SHOT. "If a Bomb goes off this turn,
    gain 5 Block." A printed conditional with no ordering word is true whether
    the Bomb went off before the card or after it, so the card pays at once
    when one already has and otherwise arms a watcher for the rest of the turn.
  * I Got Your Back (Noelle) -- REPEATING. "Whenever a Mine goes off this
    turn, gain 4 Block." `Whenever` is forward-looking and it pays per Mine.
  * Cold-Blooded Strike (Kaeya) -- a MARKER. "This turn, Grounded counts
    nothing as having gone off." Grounded reads LAST turn's count at the start
    of the next one, so the marker survives to that roll and is spent there.
  * Lion's Fang, Fair Protector (Jean) -- a POWER, Grounded's shape with a
    card on it: at the start of your turn, if none of your Bombs went off last
    turn, gain its stacks in Block and draw one.
  * Front Row Seat (Barbara, R252) -- REPEATING, and every Bomb. "Whenever a
    Bomb goes off this turn, gain 3 Block": Noelle's card with the Mines-only
    clause taken off, so a Mine pays both.

"THIS TURN" IS THE ROUND, including the enemy's half, and that is not a
liberty: Klee's Mines go off when an ENEMY attacks, so a window that closed at
the end of the player's own turn would leave "whenever a Mine goes off this
turn" unable to fire at all. Every watcher is therefore cleared where the
explosion counters roll -- the start of the player's NEXT turn.
"""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

from tier0 import constants as C

if TYPE_CHECKING:                                   # pragma: no cover
    from tier0.engine.state import Card, CombatState

#: Diona's one-shot watcher. Stacks are the BLOCK it pays, so the row's own
#: printed number is on the row and the Prototype-stage upgrade rule moves it.
SHAKEN_NOT_PURRED = "mc_shaken_not_purred"
#: Noelle's repeating watcher. Stacks are the Block paid per Mine.
I_GOT_YOUR_BACK = "mc_i_got_your_back"
#: Kaeya's marker. Stacks are a FLAG -- the row says so and states its own
#: upgrade rather than letting the rule move a number nothing reads.
COLD_BLOODED = "mc_cold_blooded"
#: Jean's power. Stacks are the Block, Grounded's own grammar.
LIONS_FANG = "mc_lions_fang"
#: Barbara's repeating watcher (R252). Stacks are the Block paid per BOMB --
#: Noelle's grammar with her Mines-only clause taken off, which is the one line
#: that separates the two.
FRONT_ROW_SEAT = "mc_front_row_seat"

#: The three watchers, cleared together at the turn roll.
_WATCHERS = (SHAKEN_NOT_PURRED, I_GOT_YOUR_BACK, FRONT_ROW_SEAT)


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

    IT CANNOT BE ANONYMOUS. `replaces:` without `personal_pool:` names no
    character to hand the card to, so it would be a row that replaces a
    Universal for everybody -- which is a pool REPLACEMENT, not a stand-in, and
    the arm already has one of those (`MONDSTADT_OVERHAUL_POOL_IDS`).
    """
    from tier0.content.loader import PROTOTYPE_ID_PREFIX

    if card.replaces is None:
        return
    if not card.id.startswith(PROTOTYPE_ID_PREFIX):
        raise ValueError(
            f"card {card.id!r}: `replaces:` is prototype surface only -- a "
            f"shipped row may not stand in for another card (ids on that "
            f"surface carry {PROTOTYPE_ID_PREFIX!r})")
    if not card.personal_pool:
        raise ValueError(
            f"card {card.id!r}: `replaces:` needs a `personal_pool:` -- a "
            "stand-in is handed to ONE character in place of a Universal, and "
            "a row that replaces a Universal for everybody is a pool "
            "replacement rather than a stand-in")


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
    if not C.COMPANION_OVERHAUL or character_id is None:
        return card_id
    return _replacements().get((card_id, character_id), card_id)


def standin_ids() -> tuple[str, ...]:
    """Every stand-in the surface declares, sorted. The test seam, and the
    derivation `C.COMPANION_STANDIN_IDS` is pinned against."""
    return tuple(sorted(_replacements().values()))


# --- the four caretakers' rules ---------------------------------------------

def roll_turn(state: "CombatState") -> None:
    """The turn boundary: spend Kaeya's marker, close both watchers.

    Called from `combat._player_turn` on the line under
    `klee_overhaul.roll_to`, which is where this arm's explosion counters roll,
    so "this turn" means the same span to the watchers and to the counters.

    THE MARKER IS SPENT HERE and not inside Grounded's own check, because
    Grounded may not be in the deck: a marker that only a Grounded in play
    could clear would sit on the player forever and blind a Grounded drafted
    three fights later.
    """
    if not C.COMPANION_OVERHAUL:
        return
    p = state.player
    state.mc_grounded_blind = bool(p.powers.pop(COLD_BLOODED, 0))
    for name in _WATCHERS:
        p.powers.pop(name, None)


def grounded_blind(state: "CombatState") -> bool:
    """Does Grounded see nothing this turn? Read once, by
    `klee_overhaul.turn_start_late`, and false on every flag-off tree."""
    return C.COMPANION_OVERHAUL and state.mc_grounded_blind


def note_explosion(state: "CombatState", is_mine: bool) -> None:
    """One explosion landed: pay whichever watcher is armed.

    Called from `klee_overhaul._explode`, beside `note_explosion`, rather than
    through `_notify_explosion`: that bus carries no Mine flag, and widening it
    for one card would put a stand-in's rule inside the Klee arm's own hook.

    BLOCK IS RAW, the argument `companion_overhaul_turn_start` makes for every
    power-sourced Block on this arm: neither block funnel may touch a gain the
    card that banked it is no longer the source of.
    """
    if not C.COMPANION_OVERHAUL:
        return
    p = state.player
    # Diona -- ONE-SHOT, popped as it pays.
    n = p.powers.pop(SHAKEN_NOT_PURRED, 0)
    if n:
        p.block += n
        state.emit("block", amount=n)
        state.emit("mc_shaken_not_purred", amount=n)
    # Noelle -- REPEATING, and MINES ONLY.
    if is_mine:
        n = p.powers.get(I_GOT_YOUR_BACK, 0)
        if n:
            p.block += n
            state.emit("block", amount=n)
            state.emit("mc_i_got_your_back", amount=n)
    # Barbara -- REPEATING, and EVERY Bomb (R252). Noelle's shape without her
    # Mines clause, which is the whole difference between the two cards: a
    # Mine is a Bomb, so Noelle's window is a subset of this one.
    n = p.powers.get(FRONT_ROW_SEAT, 0)
    if n:
        p.block += n
        state.emit("block", amount=n)
        state.emit("mc_front_row_seat", amount=n)


def on_played(state: "CombatState", card: "Card") -> None:
    """Diona's card, played on a turn a Bomb has ALREADY gone off, pays now.

    "If a Bomb goes off this turn, gain 5 Block" carries no ordering word, so
    the condition is about the TURN and not about what happens next; a watcher
    alone would print a card that reads true and does nothing. Called from
    `effects.resolve_card` after the body, so the watcher the body just applied
    is the stack this spends.
    """
    if not C.COMPANION_OVERHAUL:
        return
    if state.ko_set_off_this_turn <= 0:
        return
    p = state.player
    n = p.powers.pop(SHAKEN_NOT_PURRED, 0)
    if n:
        p.block += n
        state.emit("block", amount=n)
        state.emit("mc_shaken_not_purred", amount=n)


def turn_start(state: "CombatState") -> None:
    """Jean, Lion's Fang, Fair Protector -- Grounded's shape with a card on it.

    Called from the tail of `effects.companion_overhaul_turn_start`, which is
    where this arm's start-of-turn payouts live, and it is COMMUTATIVE with the
    three already there: it grants the player Block and a card, and none of
    them reads a value it writes.

    IT READS `ko_set_off_last_turn` DIRECTLY, so it agrees with Grounded by
    construction. It does NOT read Kaeya's blind: that card names Grounded, and
    a marker that quietly paid a second power would be a rule the player was
    never shown.
    """
    if not C.COMPANION_OVERHAUL:
        return
    p = state.player
    n = p.powers.get(LIONS_FANG, 0)
    if not n or state.ko_set_off_last_turn != 0:
        return
    p.block += n
    state.emit("block", amount=n)
    state.draw(C.MC_LIONS_FANG_DRAW)
    state.emit("extra_draw", amount=C.MC_LIONS_FANG_DRAW)
    state.emit("mc_lions_fang", amount=n)
