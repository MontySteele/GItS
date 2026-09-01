"""Furina reframe, SLICE 1 -- the quarantined prototype engine.

`review/ruled/furina-reframe-2026-08-29.md` is the countersigned design (R220
A, F-picks answered by R224); `review/ruled/furina-spotlight-options-2026-08-30.md`
§5 is R228's ruled Spotlight direction. This module is the sim half of that
packet's §6 testable slice, and NOTHING IN IT IS ON.

WHY THE FLAGS LIVE HERE AND NOT IN `constants.py`. The packet's §6.1 table says
so in as many words: the master flag is "sim-side a module constant in the
reframe module, **not** in `constants.py`". The reason is the stamp. A flag in
`constants.py` is read by the parity gate and the constant census; a flag in a
module the shipped engine only branches on is a piece of quarantined machinery,
and with every flag False the engine is the shipped engine byte for byte
(`tier0/tests/test_furina_reframe_slice1.py` pins that arm first).

THE HONESTY NOTE THE PACKET ASKS FOR, restated where a reader will hit it:
turning `FURINA_REFRAME_MANUAL` or `FURINA_REFRAME_METER` ON is a
`CONSTANTS_VERSION` event, because both are engine behaviour and not a card
row. No number measured with a flag on is comparable to the standing baseline,
and any LANDED step re-baselines the whole twelve-arm table. The slice is
built; it is not run, deployed, or migrated. R213's sequencing gate
("nothing implements before Klee closes", R224) is untouched by a default-off
module: this is the build, and the run still waits its turn.

WHAT SLICE 1 IMPLEMENTS (the five ruled sentences, and nothing else):

  MANUAL   Members stop auto-playing -- the turn-start upkeep is suppressed
           for Furina. A Companion play makes the FRONT member perform and
           then rotate (`F3` (1), `F4` (1): once per Companion CARD PLAY,
           unbounded per turn). A deploy performs the member it deploys, and
           a deploy onto a full stage EVOKES the front member to make room
           (§4.2, all three RULED). An empty stage does nothing extra, and
           says so in the log.
  EVOKE    The Evoke verb: the member the card NAMES, front when it names
           none (`F5`, as the slot-6 ruling revised it), the Focus term applied
           `EVOKE_FOCUS_MULT` times instead of once (`F6` (1), the printed
           multiplier), priced in Encore through the card's shipped
           `encore_cost` field (`F7` (1)).
  METER    Fanfare is minted by a member PERFORMING and by nothing else
           (§4.1): a trigger mints the small amount, an Evoke the larger. The
           four shipped legs -- HP lost, Encore spent, Encore absorbed, a
           Spotlighted card played -- mint nothing.
  SPOTLIGHT  R228 option (1), ONE MODE, PRICED: Center Stage retires, Guest
           Cast and `SPOTLIGHT_BASE_MULT` stay, and the selector costs Encore
           instead of running a heuristic between two modes.

WHAT SLICE 1 DOES NOT IMPLEMENT, so nobody reads an absence as a decision:
the `F1` (2) fourth (scaling) member, the `F9` (1) cap carriers, the `F11`/`F12`
drain cards, the `F16` (1) starter delta (`FURINA_REFRAME_STARTER` is not
declared here because nothing would read it), the `F13`/`F14`/`F15` display
work, the Burst-meter retirement (R220 B's own branch owns it), the named
Companion TARGET half of R228's selector, and the C# leg. §11 of the packet
lists each one with its reason.

LAW:145 IS LIVE HERE, and it is why `FANFARE_PER_COMPANION_TRIGGER_MAX` exists.
The clause (countersigned R224) permits "a character-owned engine [to] respond
to a Companion play and generate its resource where that character's kit
explicitly declares the trigger and BOUNDS THE AMOUNT GENERATED PER COMPANION
PLAY". Klee's kit declares hers with `KLEE_COMPANION_SPARK_MAX_PER_PLAY`; this
is the same declaration for Furina's, and it is a bound rather than a
recommendation -- one performance per play, one trigger mint, capped.
"""

from __future__ import annotations

CHARACTER = "furina"

# ----------------------------------------------------------------------
# THE FLAGS. All OFF. Nothing here may default True without a ruling.
# ----------------------------------------------------------------------
FURINA_REFRAME = False            # master. Every leg below is AND-ed with it,
                                  # so one flip returns the shipped engine.
FURINA_REFRAME_MANUAL = False     # members stop auto-playing; the Companion
                                  # trigger fires; deploy performs; a deploy
                                  # onto a full stage Evokes.
FURINA_REFRAME_EVOKE = False      # the Evoke verb, its Focus multiplier and
                                  # its Encore price.
FURINA_REFRAME_METER = False      # Fanfare minted by performance, and only by
                                  # performance.
FURINA_REFRAME_SPOTLIGHT = False  # R228 (1): one mode, priced.

# ----------------------------------------------------------------------
# THE PROTOTYPE SEEDS. Not ruled numbers -- §4.1 says the small/large pair are
# "prototype seeds ... their ORDERING is ruled: trigger < Evoke, because Evoke
# costs a member". Under R215 B no number measured on a prototype is quotable.
# ----------------------------------------------------------------------
FANFARE_PER_TRIGGER = 2           # a member performing and staying.
FANFARE_PER_EVOKE = 5             # a member performing and leaving. > trigger,
                                  # which is the ruled half of the pair.
FANFARE_PER_COMPANION_TRIGGER_MAX = FANFARE_PER_TRIGGER
                                  # LAW:145's per-Companion-play bound. One
                                  # performance per play means one mint, and
                                  # this is what makes that a bound instead of
                                  # an accident of the call site.
EVOKE_FOCUS_MULT = 3              # `F6` (1): the Focus term applied N times on
                                  # an Evoke, once on a trigger, N printed on
                                  # the face. One divisor, one number on screen.
SPOTLIGHT_DESIGNATE_ENCORE_COST = 2
                                  # R228 (1): the selector's price. The packet
                                  # names the risk itself -- a THIRD claim on
                                  # one unbounded buffer, beside the deferred
                                  # Block and the Evoke price -- and rules that
                                  # it is measured rather than assumed away.


# ----------------------------------------------------------------------
# The readers. Functions rather than module constants at the call sites, so a
# test can flip a flag with `monkeypatch.setattr` and every branch sees it.
# ----------------------------------------------------------------------
def is_furina(player) -> bool:
    """Whose engine this is. Every leg is character-scoped: the reframe is one
    character's redesign and a roster-wide branch would be a different (and
    much larger) change than the one the packet countersigned."""
    return getattr(player, "character_id", None) == CHARACTER


def manual_active(player) -> bool:
    return FURINA_REFRAME and FURINA_REFRAME_MANUAL and is_furina(player)


def evoke_active(player) -> bool:
    return FURINA_REFRAME and FURINA_REFRAME_EVOKE and is_furina(player)


def meter_active(player) -> bool:
    return FURINA_REFRAME and FURINA_REFRAME_METER and is_furina(player)


def spotlight_active(player) -> bool:
    return FURINA_REFRAME and FURINA_REFRAME_SPOTLIGHT and is_furina(player)


def evoke_focus_mult(player) -> int:
    """How many times an Evoke applies the Focus term. ONE when the Evoke leg
    is off, which is what makes the `salon_evoke` op resolve exactly like the
    shipped `salon_bow` in a release world."""
    return EVOKE_FOCUS_MULT if evoke_active(player) else 1


# ----------------------------------------------------------------------
# The aimed Evoke -- the slot-6 ruling, 2026-08-30.
# ----------------------------------------------------------------------
EVOKE_TARGET_FRONT = "front"      # the sentinel a card prints when it does not
                                  # aim: written out rather than left implicit,
                                  # so "unstated" and "front" are the SAME
                                  # word on a face and in a row.
EVOKE_TARGET_ABSENT = -1          # the named member is not on the stage. The
                                  # caller says so out loud (D4) and takes the
                                  # front, which is what an unaimed Evoke does.


def evoke_target_index(player, named=None) -> int:
    """Which member the dedicated Evoke takes: the index into `player.salon`.

    THE RULE, from the slot-6 ruling (2026-08-30, [USER]): the dedicated Evoke
    lets the card CHOOSE which member it removes, and the FRONT is what it
    takes when nothing is named. The full-stage deploy path is untouched and
    stays automatic-front -- it never calls this function -- because the same
    ruling keeps the overflow Evoke as the reward for filling the stage, and
    what Encore now buys is the deliberate aim the free route structurally
    lacks.

    WHY THIS IS NOT A NEW OP, checked rather than assumed. `tools/lint_op_
    parity.py` compares the KEY SET of `tier0.engine.effects.OPS` against
    `tier05.draft.STATIC_OP_PRICING`; the drafter's `_op_price` branches on the
    op name and reads no argument of it. An extra `member:` ARGUMENT on the
    shipped `salon_bow` verb therefore leaves the priced-op set identical, so
    it is not a `DRAFTER_VERSION` event -- which is the same reasoning slice 1
    used to refuse a `salon_evoke` synonym op, applied to its own next step.
    A new op would have bought a stamp for a verb the engine already has.

    FLAG-GATED, so the shipped engine cannot be aimed. With
    `FURINA_REFRAME_EVOKE` off this returns 0 whatever a row names, which is
    the front member the shipped bow has always popped.
    """
    if not named or named == EVOKE_TARGET_FRONT or not evoke_active(player):
        return 0
    if named not in player.salon:
        return EVOKE_TARGET_ABSENT
    return player.salon.index(named)


# ----------------------------------------------------------------------
# The mints. Both live here rather than at the four retired legs, because
# §4.1's rule is positive ("a member performing mints Fanfare, and nothing
# else does") and a rule stated positively should have one home.
# ----------------------------------------------------------------------
def mint_for_performance(state, member: str) -> None:
    """A member performed and STAYED: the small amount (a trigger, a
    deploy-performs, or a `salon_perform` card -- all the same act, so all the
    same mint)."""
    from tier0.engine import resources           # late: avoids the cycle
    if not meter_active(state.player):
        return
    n = min(FANFARE_PER_TRIGGER, FANFARE_PER_COMPANION_TRIGGER_MAX)
    resources.gain_fanfare(state, n, "salon_performance")


def mint_for_evoke(state, member: str) -> None:
    """A member performed and LEFT: the larger amount. Ordering is ruled."""
    from tier0.engine import resources           # late: avoids the cycle
    if not meter_active(state.player):
        return
    resources.gain_fanfare(state, FANFARE_PER_EVOKE, "salon_evoke")


# ----------------------------------------------------------------------
# The Companion trigger -- §4.3, `F3` (1) and `F4` (1).
# ----------------------------------------------------------------------
def companion_play_trigger(state, card) -> None:
    """A Companion play makes the FRONT member perform, then rotates it back.

    CALLED FROM `combat._finish_play`, gated to the first resolution of the
    play, which is the same seam and the same guard Klee's kit uses
    (`effects.klee_personal_companion_spark`). The reasons carry over exactly:
    `_finish_play` is the shared half of every card play, so "once per
    Companion play" is true by construction rather than by discipline, and a
    replay is one card resolved twice rather than two plays.

    The pair is `salon_perform` then `salon_rotate` -- literally what
    `change_the_bill` prints today (§4.3) -- so this hook adds no new
    resolution path: it calls `salon_member_act`, the one implementation, and
    rotates the shipped queue.

    AN EMPTY SALON DOES NOTHING EXTRA (§1.1a item 2, RULED), and under D4 that
    has to be visible, so the whiff is emitted rather than silent. The event is
    a NEW name (`salon_trigger_whiffed`) and not the card verbs' own
    `salon_perform_whiffed`, because a display that wants to say "your
    Companion found an empty stage" must be able to tell that apart from a card
    the player chose to play into an empty stage.
    """
    from tier0.engine import effects              # late: avoids the cycle
    p = state.player
    if not manual_active(p) or not card.is_companion:
        return
    if not p.salon:
        state.emit("salon_trigger_whiffed", card=card.id)
        return
    member = p.salon[0]
    acted = effects.salon_member_act(state, member)
    if not acted:
        # A cleared board or a dead player: the shared act refused, so nothing
        # performed, so nothing mints and the queue does not turn either.
        return
    # NO MINT HERE, deliberately. `salon_member_act` is the one implementation
    # of a member performing and it carries the one mint (§4.1); a second call
    # at this seam would pay the trigger twice, which is exactly the drift the
    # shared act exists to prevent -- and it would also break LAW:145's
    # per-Companion-play bound while appearing to honour it.
    p.salon.append(p.salon.pop(0))
    state.emit("salon_trigger", card=card.id, member=member,
               company=list(p.salon))
