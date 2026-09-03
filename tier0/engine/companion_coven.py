"""KLEE'S FOUR COVEN PERSONALS (QUARANTINED, `C.COMPANION_OVERHAUL`).

The approved Mondstadt workshop's sec.4 and its sec.3 Prune entry, ruled R236.
Four rows, offered to Klee alone through the Personal channel
`prune_witch_hunt` already rides, and three engine behaviours between them:

    proto_mc_prune_hexhunter_chime   the next Bomb set off this turn deals the
                                     swirled element instead of Pyro
    proto_mc_sayu_silencers_secret   no power: `swirl` + `block` + the shipped
                                     `bomb_went_off_this_turn` predicate
    proto_mc_qiqi_herald_of_frost    a start-of-turn payout, 3 turns
    proto_mc_yaoyao_yuegui_throwing_mode  an end-of-turn Bomb, 3 turns

A SEPARATE MODULE, not three more branches in `effects.companion_overhaul_*`,
and the reason is the same one that gave the Klee overhaul its own file: these
rows are the only place in either engine where the COMPANION arm reaches into
the KLEE arm's rules, so "what does a Personal do to a Bomb" has one greppable
home. The four registration lines that call in are named in `HOOKS` below.

TWO ARMS, TWO GATES, AND BOTH ARE LOAD-BEARING. Every function here returns
before touching anything while `C.COMPANION_OVERHAUL` is off -- that is the
arm's acceptance condition, pinned rather than intended. The two rows that
speak about Bombs also need the KLEE overhaul live, because a Bomb is that
arm's rule and not this one's: `klee_overhaul.live` is the same gate the ops
take, so a Yuegui thrown by a co-op Furina plants nothing and a Chime armed on
a board with no Bomb rules is inert rather than an exception.

NOTHING MEASURED ON A PROTOTYPE ROW IS QUOTABLE ANYWHERE (R215 B).
"""

from __future__ import annotations

from tier0 import constants as C
from tier0.engine.state import CombatState

#: The four registration lines in shared files that reach this module, so the
#: seam is greppable from one end as well as the other:
#:
#:   effects.player_turn_start_triggers  -> turn_start   (Qiqi's payout)
#:   effects.player_turn_end_triggers    -> turn_end     (Yuegui, then expiry)
#:   effects.companion_overhaul_reaction -> note_swirl   (Prune's latch)
#:   klee_overhaul._explode              -> bomb_element (Prune's override)
HOOKS = ("turn_start", "turn_end", "note_swirl", "bomb_element")


def note_swirl(state: CombatState, aura: str) -> None:
    """A Swirl has just resolved, consuming `aura`. LAST WINS.

    Called from `effects.companion_overhaul_reaction`, at the one site this
    engine resolves a reaction -- beside Varka's latch and Heizou's counter,
    off the same event, so the three cannot disagree about what a Swirl was.
    C# twin: `CompanionOverhaulLedger.NoteSwirl`, whose call site is that
    engine's own single `ReactionEffects.Resolve`.

    LATCHED UNCONDITIONALLY, unlike Varka's, and the difference is the card.
    Sturm und Drang is a POWER that is already standing when the Swirl happens,
    so its latch can ask whether it is up; the Chime is an ATTACK whose own
    printed order is "Deal 8 damage. Swirl. The next Bomb ...", so the Swirl it
    names resolves BEFORE the rider it arms. A latch that asked "is a Chime
    up?" would answer no on the one card that needs it. The field is turn
    scoped (`combat._player_turn` clears it beside `mi_swirls_this_turn`), so
    what it remembers is "the last element swirled this turn" and nothing
    longer.
    """
    if not C.COMPANION_OVERHAUL:
        return
    state.cvn_swirl_element = aura


def bomb_element(state: CombatState) -> str:
    """RULE 5's element for the explosion about to resolve: `"pyro"`, unless
    Prune's Chime is armed and a Swirl has happened this turn.

    Called from `klee_overhaul._explode`, which is the ONE place a charge deals
    its damage, so the override cannot reach a hit that is not a Bomb's and
    cannot miss one that is. C# twin: `CompanionCovenBombs.ElementFor`, called
    from `ProtoBombPower.Explode`, that engine's same one place.

    "THE NEXT BOMB", SINGULAR, so the rider is CONSUMED here rather than read.
    A three-charge Set off is three explosions (rule 2's "one at a time"), and
    the card promises the element to the first of them; the other two are Pyro.
    Consumed even when no Swirl landed, because the card spent its rider on
    that Bomb either way and a rider that survived a fizzled Swirl would make
    the Chime say something its face does not.

    Returns `"pyro"` with either arm off, which is what leaves every shipped
    explosion byte-identical.
    """
    if not C.COMPANION_OVERHAUL:
        return "pyro"
    if not state.player.powers.pop("cvn_hexhunter_chime", 0):
        return "pyro"
    return state.cvn_swirl_element or "pyro"


def turn_start(state: CombatState) -> None:
    """The coven's start-of-turn block: Qiqi, and nothing else.

    Called from the tail of `effects.player_turn_start_triggers`, AFTER
    `companion_overhaul_turn_start`. The order is law and the C# side keeps it
    by the same argument the Mondstadt block makes for its own three: Mona's
    omen applies Vulnerable to ALL enemies at the start of the turn, and the
    Cryo the Herald applies can resolve a REACTION whose damage that Vulnerable
    amplifies. So the two are not commutative, one sequence is written down,
    and this is the end of it.

    Herald of Frost -- "For 3 turns, at the start of your turn apply Cryo twice
    to a random enemy and gain 3 Block." Stacks are TURNS REMAINING (the
    `oz_summon` grammar every timed row on this surface uses). PAY, THEN TICK,
    THEN EXPIRE.

    TWICE MEANS TWO APPLICATIONS AT ONE BODY, not two rolls: the printed words
    aim once ("to a random enemy") and then say how many times. The second
    application is what makes the card its own reaction -- the first Cryo meets
    whatever is standing, the second lands on the Cryo the first left.
    """
    if not C.COMPANION_OVERHAUL:
        return
    from tier0.engine import reactions            # late import: cycle

    p = state.player
    n = p.powers.get("cvn_herald_of_frost", 0)
    if not n:
        return
    for _ in range(C.CVN_HERALD_APPLICATIONS):
        living = state.living_enemies
        if not living:
            break
        # Re-rolled per application, because the first one can kill: an aura
        # that Vaporizes is damage, and a corpse is not "a random enemy".
        enemy = state.rng.choice(living)
        reactions.resolve_hit(state, enemy, "cryo", 0, "apply_aura_op")
    # RAW, sharing `block_next_turn`'s argument verbatim with the arm's other
    # power-sourced Block (NC-11): neither block funnel may touch a gain the
    # card that banked it is no longer the source of.
    p.block += C.CVN_HERALD_BLOCK
    state.emit("block", amount=C.CVN_HERALD_BLOCK)
    if n > 1:
        p.powers["cvn_herald_of_frost"] = n - 1
    else:
        del p.powers["cvn_herald_of_frost"]


def turn_end(state: CombatState) -> None:
    """The coven's end-of-turn block: Yuegui, then the Chime's expiry.

    Called from the tail of `effects.player_turn_end_triggers`, AFTER
    `companion_overhaul_turn_end` and its Inazuma half. Same argument as the
    start-of-turn block: Yuegui's Bomb draws from `state.rng`, so its position
    decides every later roll in the fight, and one sequence is written down per
    engine. C# twin: the tail of `CompanionOverhaulTurnEnd`, before Nicole's
    latch -- a Bomb grants no Block, so it cannot change the latch's answer.

    Yuegui: Throwing Mode -- "For 3 turns, at the end of your turn place a Bomb
    3 on a random enemy." Stacks are TURNS REMAINING; FIRE, THEN TICK, the
    idiom the arm's other volleys use, so a stack count still means "this many
    more turns, including this one".

    THE CLOCK TICKS EVEN WHERE THE BOMB CANNOT LAND. `klee_overhaul.live` is
    false for a seat that is not running the Bomb rules, and an empty board has
    nobody to throw at; in both cases the card's three turns still pass, which
    is the reading that keeps the power from becoming permanent on a board it
    could not reach.
    """
    if not C.COMPANION_OVERHAUL:
        return
    from tier0.engine import klee_overhaul        # late import: cycle

    p = state.player
    n = p.powers.get("cvn_yuegui", 0)
    if n:
        living = state.living_enemies
        if living and klee_overhaul.live(state):
            klee_overhaul.place(state, state.rng.choice(living),
                                C.CVN_YUEGUI_BOMB_SIZE)
        if n > 1:
            p.powers["cvn_yuegui"] = n - 1
        else:
            del p.powers["cvn_yuegui"]
    # "THIS TURN" IS THE REMOVAL, the shipped `attack_up_this_turn` shape and
    # the one the C# `PassionOverloadPower` takes for the same clause. A Chime
    # that survived the turn boundary would colour a Bomb the card never
    # promised.
    p.powers.pop("cvn_hexhunter_chime", None)
