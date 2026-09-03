"""THE HEXEREI MARK AND ITS READERS (QUARANTINED, two arms).

Four stand-ins on the seam `companion_standins` opened, and the file exists for
that module's reason: a quarantined arm's whole behaviour should be greppable
in one place. `companion_standins` holds the SEAM (the sheet contract, the
hand-off, the map derived from `replaces:`) and the FOUR CARETAKERS' rules;
this file holds the four FAMILY stand-ins' rules, THE FAMILY MARK ITSELF, and
nothing else. Nothing here is reachable with both flags off -- every function
returns at the top, checked rather than assumed by its callers, which is what
keeps the byte-identity pin a property of the module.

THE MARK IS SHARED AND THE READERS ARE NOT (R244). `hexerei:` is one word on a
row with no effect of its own, and until R244 it had exactly one reader:
Nicole's Ladder of Divine Ascent, a `C.COMPANION_OVERHAUL` stand-in. The three
Klee readers the ruling adds (`review/ruled/klee-hexerei-readers-2026-09-02.md`)
sit on `C.KLEE_OVERHAUL` instead, so "is this play a Hexerei card?" is now a
question two arms ask -- and it is answered HERE, once, by `is_hexerei`, with
each reader gated on its own flag afterwards. A second definition of the family
is exactly what the field exists to prevent.

ALICE'S INTRODUCTION MAGIC WIDENS THE MARK FOR ONE TURN, which is why the
answer takes the STATE and not just the card: "All cards in your hand count as
Hexerei cards this turn" is a window over the card INSTANCES that were in hand
when it resolved (the ruling's own derived reading -- a card drawn later this
turn is not counted, which is why the upgrade is Retain), and
`state.ko_hexerei_marked` is that list. It is dropped whole at the arm's turn
end, so nothing outlives the turn that wrote it.

WHAT A FAMILY STAND-IN IS. The caretakers read the Klee overhaul's explosion
ledger, which is what a caretaker is for. These four read the REACTION, because
Hexerei is the reaction family (the approved Mondstadt workshop sec.1; R236
sec.3). Each is handed to Klee in place of one Hexerei Universal and wears its
art; each is Hexerei-tagged itself, which is why Nicole's power can pay for
three of the other four.

  * Tectonic Tide (Albedo, for Solar Isotoma) -- a POWER, permanent. "Whenever
    a reaction happens, deal 4 damage to that enemy." ANY reaction, exactly as
    Dahlia's Favonian Favor counts any; the card names none. The damage carries
    NO ELEMENT, because the printed text names none -- the same call Solar
    Isotoma and the Lightfall Sword already made -- so it can neither consume an
    aura nor start a second reaction.
  * Undone Be Thy Sinful Hex (Fischl, for Nightrider) -- an ATTACK arming a
    this-turn watcher. "Whenever an Electro reaction happens this turn, deal 5
    Electro damage to a random enemy."
  * Mollis Favonius (Sucrose, for Wind Spirit Creation) -- a SKILL arming a
    this-turn ADDITIVE. "This turn, reactions deal 4 additional damage." Only
    the reactions that deal damage of their own can deal more of it; see
    below.
  * Ladder of Divine Ascent (Nicole, for Revelation) -- a POWER, permanent, and
    the first reader the family mark has ever had. "Whenever you play a Hexerei
    card, deal 6 damage of that card's element to a random enemy."

AN ELECTRO REACTION IS DERIVED, NEVER PASSED. `companion_overhaul_reaction`
hands this file the reaction's NAME and the CONSUMED AURA, and that pair names
both elements: Overload, Superconduct and Electro-Charged are the three
reactions Electro can be the TRIGGER of, and every other way Electro takes part
is as the aura that was standing. Anemo and Geo never stick as an aura, so the
aura is always one of the four that can be Electro -- which is what makes the
derivation total and why no hook signature had to widen for this slice.

WHY FISCHL'S VOLLEY MAY FIRE FROM INSIDE THE REACTION SITE. It deals ELECTRO
damage, so it can react again, and the two things that could go wrong both do
not:

  * THE LOG. `reactions._react` emits its own `reaction` event AFTER this call,
    and `reactions.settle_amp_delta` rewrites the first event since the mark
    that carries a nonzero `amp_delta`. A nested event would be found first --
    but Electro is in no amplifier pair (Vaporize is Pyro/Hydro, Melt is
    Pyro/Cryo), so every reaction this volley can cause carries `amp_delta` 0
    and is skipped. The outer amplifier still settles against its own event.
  * THE DEPTH. A chained firing consumes a standing aura and creates none
    (Overload, Superconduct and Electro-Charged all leave the target bare); a
    volley that instead APPLIES Electro to a bare enemy causes no reaction and
    so cannot chain. Each link therefore strictly spends one of the at most
    one-per-enemy auras on the board, and the chain is bounded by the enemy
    count.

MOLLIS FAVONIUS IS DELIVERED AT THE REACTION SITE, NOT INSIDE THE AMPLIFIER,
and that is the one implementation call in this file worth arguing.

  * WHAT IT REACHES is Durin's White boundary, cited rather than re-derived:
    the reactions that deal damage OF THEIR OWN are the two amplifiers and
    Overload. Superconduct, Frozen, Crystallize and Swirl deal none, so "deal
    4 additional damage" has nothing to add to; Electro-Charged applies a dot
    POWER rather than damage. Albedo's Tectonic Tide pays on ALL of them, and
    that difference is the two cards' printed words, not an accident.
  * WHY NOT FOLDED INTO THE AMPLIFIER ARITHMETIC. That is where White lives,
    and in the sim a flat term could sit beside it -- but the mod's amplifier
    is a MULTIPLIER (`AuraPower.ModifyDamageMultiplicative` returns a factor,
    with no damage to add a constant to) and its additive phase runs BEFORE
    the amplifier, so the same 4 would be scaled there and not here. A rule
    that lands on a different number in each engine is worse than one that
    lands beside the reaction in both.
  * THE ORDER, since the two stack: MULTIPLY FIRST, ADD AFTER. White scales
    the reaction's own contribution inside the damage pipeline
    (`reactions._react`, `out = damage + (out - damage) * m`, and the Overload
    splash); Mollis Favonius adds its flat 4 afterwards, at the site the
    reaction is announced, so White never scales the 4 and the 4 never enters
    an amplifier. Both engines, same sentence.

C# TWIN: `KleeMod.Powers.CompanionHexerei` and the four powers beside it,
called from the same two mouths -- the one reaction site and `AfterCardPlayed`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tier0 import constants as C

if TYPE_CHECKING:                                   # pragma: no cover
    from tier0.engine.state import Card, CombatState, Enemy

#: Albedo. Stacks are the damage each reaction deals, so a second copy pays
#: twice -- Favonian Favor's grammar, and the row's own printed number.
TECTONIC_TIDE = "mc_tectonic_tide"
#: Fischl. Stacks are the Electro damage per Electro reaction. THIS TURN.
SINFUL_HEX = "mc_sinful_hex"
#: Sucrose. Stacks are the flat damage a damaging reaction adds. THIS TURN.
MOLLIS_FAVONIUS = "mc_mollis_favonius"
#: Nicole. Stacks are the damage each Hexerei play deals.
LADDER_OF_ASCENT = "mc_ladder_of_ascent"

#: The two this-turn windows, popped together where the arm's other "this
#: turn" promises are (`effects.companion_overhaul_turn_end`).
_THIS_TURN = (SINFUL_HEX, MOLLIS_FAVONIUS)

#: The three reactions Electro can be the TRIGGER of. Every other appearance of
#: Electro in a reaction is as the aura that was standing, which the caller
#: hands over -- see the module header for why that pair is total.
_ELECTRO_REACTIONS = frozenset(("overload", "superconduct", "electrocharged"))

#: The reactions that deal damage OF THEIR OWN, which is Durin's White form's
#: boundary read off `effects.companion_overhaul_reaction_mult`'s own docstring
#: rather than re-derived: the two amplifiers' contribution and the Overload
#: splash. Sucrose's card adds to the same quantity White multiplies, so it
#: must reach the same reactions or the two sentences stop being about one
#: thing.
_DAMAGING_REACTIONS = frozenset(("vaporize", "melt", "overload"))


def is_hexerei(state: "CombatState", card: "Card") -> bool:
    """Is this card in the Hexerei family RIGHT NOW? The mark's ONE reader.

    Two ways in, and they are deliberately different kinds of thing:

      * `card.hexerei` -- the PRINTED mark, one word on the row, read off the
        sheet key rather than off a list of ids kept in a reader (which is what
        the field exists to avoid);
      * the this-turn window Alice's Introduction Magic opens (R244), which is
        a list of card INSTANCES rather than ids, so a second copy drawn after
        the spell is not counted.

    UNGATED, and the two callers are what makes that right: this is a question
    about a card, not a rule that pays out, and every reader below it is gated
    on its own arm's flag. With both arms off `card.hexerei` is False on every
    shipped row and the list is empty on every tree, so the answer is False by
    construction rather than by a flag test written twice.
    """
    if card.hexerei:
        return True
    return any(marked is card for marked in state.ko_hexerei_marked)


def mark_hand(state: "CombatState") -> int:
    """Alice's Introduction Magic: every card in hand joins the family for this
    turn. Returns how many were marked. `IntroductionMagicPower`'s twin.

    THE CARDS IN HAND WHEN IT RESOLVES, and no others -- the ruling's first
    derived reading. The card marks the hand it was played from, so the way to
    hold it for a big hand is the upgrade's Retain and not a later draw.

    THE SPELL COUNTS ITSELF, which is the ruling's second derived reading, and
    it needs no line here: the row carries `hexerei: true`, so it is in the
    family printed rather than by this list -- and a card that is being played
    has already left the hand, so marking the hand could not have reached it.
    """
    marked = [card for card in state.player.hand
              if not any(seen is card for seen in state.ko_hexerei_marked)]
    state.ko_hexerei_marked.extend(marked)
    state.emit("ko_hexerei_marked", count=len(marked))
    return len(marked)


def roll_hand_marks(state: "CombatState") -> None:
    """The this-turn window closes. Called from `klee_overhaul.turn_end`.

    DROPPED WHOLE rather than un-stamped card by card, which is the reason the
    marks are a list on the state instead of a flag on the `Card`: a marked
    card that was discarded, exhausted or shuffled away during the turn is
    reached by this line without the engine having to walk every pile to find
    it, and a stamp that survived into the next turn would be a rule nobody
    printed.
    """
    state.ko_hexerei_marked.clear()


def is_electro_reaction(name: str, aura: str) -> bool:
    """"An Electro reaction is any reaction with Electro as either element"
    (R236 sec.3), answered from the reaction's name and the consumed aura."""
    return name in _ELECTRO_REACTIONS or aura == "electro"


def note_reaction(state: "CombatState", enemy: "Enemy", name: str,
                  aura: str) -> None:
    """A reaction has just resolved: pay Albedo, then Sucrose, then Fischl.

    Called from the tail of `effects.companion_overhaul_reaction`, which is the
    site `reactions._react` already counts a reaction at -- so "a reaction
    happened" keeps ONE definition in this engine and these three readers cannot
    disagree with `reaction_triggered_this_turn` about it. Beside
    `companion_coven.note_swirl`, for the same reason it is there.

    THE UNELEMENTED TWO FIRST, and the order is stated rather than incidental:
    Albedo's and Sucrose's hits carry no element and cannot chain, so paying
    them first means the board Fischl's volley draws from is the one they left.
    The reverse order could let a chained Electro reaction kill the body their
    damage was owed to.
    """
    if not C.COMPANION_OVERHAUL:
        return
    from tier0.engine import effects                # late import (cycle)

    p = state.player
    # NC-1 for all three: power-sourced DAMAGE runs the pipeline.
    n = p.powers.get(TECTONIC_TIDE, 0)
    if n and enemy.alive:
        # NO ELEMENT -- the card names none, the same call Solar Isotoma (the
        # Universal this stands in for) already made.
        effects.deal_damage_to_enemy(state, enemy, n, element=None,
                                     source="companion")
        state.emit("mc_tectonic_tide", amount=n, target=enemy.name)
    n = p.powers.get(MOLLIS_FAVONIUS, 0)
    if n and name in _DAMAGING_REACTIONS and enemy.alive:
        # ON THE REACTED ENEMY, ONCE -- including Overload, whose splash is
        # spread over the board: "the reaction deals 4 additional damage" is
        # one promise about one reaction, not one per body it splashed.
        effects.deal_damage_to_enemy(state, enemy, n, element=None,
                                     source="companion")
        state.emit("mc_mollis_favonius", amount=n, target=enemy.name)
    n = p.powers.get(SINFUL_HEX, 0)
    if n and is_electro_reaction(name, aura) and state.living_enemies:
        target = state.rng.choice(state.living_enemies)
        effects.deal_damage_to_enemy(state, target, n, element="electro",
                                     source="companion")
        state.emit("mc_sinful_hex", amount=n, target=target.name)


def note_card_played(state: "CombatState", card: "Card") -> None:
    """A card was played: if it is Hexerei, pay every arm that reads the mark.

    Called from `combat._finish_play` beside
    `effects.companion_overhaul_card_played`, the one site both play paths
    reach and the site the mod's `AfterCardPlayed` answers.

    ONE MOUTH, TWO ARMS (R244). The question is asked once, by `is_hexerei`,
    and each reader is gated on its own flag underneath: Nicole's Ladder is a
    `C.COMPANION_OVERHAUL` stand-in and the Klee readers this ruling adds are
    `C.KLEE_OVERHAUL`. The packet's sec.4 says why it lands here rather than as
    a second hook -- "a Hexerei-play trigger, which the Nicole stand-in already
    needs, so it lands once".

    THE OWN-CARD CASE IS NOT A SPECIAL CASE, for either reader. This site runs
    after the card's effects, so a power the body just applied is standing --
    the same contract Diona's stand-in leans on
    (`companion_standins.on_played`) and the same one `AfterCardPlayed` gives
    the mod. Nicole's Hexerei-tagged card therefore pays once for itself, and
    Witches' Circle does not (it is not Hexerei and it is a Power, so the play
    that sets it up plants nothing).
    """
    if not is_hexerei(state, card):
        return
    _pay_ladder(state, card)
    from tier0.engine import klee_overhaul           # late import (cycle)

    klee_overhaul.note_hexerei_played(state, card)


def _pay_ladder(state: "CombatState", card: "Card") -> None:
    """Nicole: a Hexerei card was played, so one random enemy takes its element.

    THE MARK'S FIRST READER, and it is read off the CARD rather than off a list
    of ids kept here: `hexerei:` is on the row precisely so a reader can see
    which rows the family owns without re-deriving it from a character list,
    and a second copy of that list would be the thing the field exists to
    avoid. `tier0/tests/test_companion_overhaul.py` pinned the mark as inert
    and names this module as the one reader that moved it.

    A HEXEREI CARD WITH NO ELEMENT DEALS PLAIN DAMAGE (R236 pick 6), which is
    `element=None` here and the shipped `deal_damage_to_enemy` default. A Klee
    pool row that joins the family through R244 carries no `element:` at all,
    so the sheet's `"none"` is the same answer spelled the sheet's way.
    """
    if not C.COMPANION_OVERHAUL:
        return
    n = state.player.powers.get(LADDER_OF_ASCENT, 0)
    if not n or not state.living_enemies:
        return
    from tier0.engine import effects                # late import (cycle)

    element = card.element if card.element and card.element != "none" else None
    target = state.rng.choice(state.living_enemies)
    effects.deal_damage_to_enemy(state, target, n, element=element,
                                 source="companion")
    state.emit("mc_ladder_of_ascent", amount=n, target=target.name,
               element=element or "none")


def roll_turn_end(state: "CombatState") -> None:
    """Both this-turn windows close, whether or not they ever paid.

    Called from `effects.companion_overhaul_turn_end` beside the pops for
    Dahlia's Favonian Favor and Bennett's Passion Overload -- the arm's own
    reading of "this turn", and the one these two cards must share: they are
    reaction cards, not Bomb cards, so nothing they promise can be kept during
    the enemy's half the way a Mine's can (which is why the CARETAKERS' two
    watchers close at the turn START instead, `companion_standins.roll_turn`).
    """
    if not C.COMPANION_OVERHAUL:
        return
    for name in _THIS_TURN:
        state.player.powers.pop(name, None)
