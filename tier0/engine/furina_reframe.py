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
FURINA_REFRAME_BURST = False      # R251 / `EB-365`: the SHIPPED Burst meter
                                  # retires under this arm -- it neither draws
                                  # nor fills, and `let_the_people_rejoice` is
                                  # never granted. ARM-ONLY: the shared
                                  # retirement (`EB-199`, `EB-200`) still owns
                                  # the shipped engines, and nothing outside
                                  # this flag moves.

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
OPENING_ENCORE = 2                # R258 (`EB-479`): she starts each combat
                                  # with this much Encore, so turn ONE can pay
                                  # one thing -- a Spotlight designation or a
                                  # wet performance -- instead of nothing.
                                  # Rounds 5 to 8 each read the first turn as
                                  # no decision at 0 Encore and round 9 called
                                  # the opening "by construction its own
                                  # weakest version". SIZED TO THE TWO PRICES
                                  # IT UNLOCKS, which are both 2: the number
                                  # buys exactly one opening move, never two.
OPENING_MEMBER = "crabaletta"     # R260 (`EB-553`): who is already on the
                                  # stage when the fight opens. NAMED and not
                                  # rolled, which is `EB-416`'s finding one
                                  # rule over -- under the manual stage the
                                  # FRONT member is the one a Companion play
                                  # makes perform, so a rolled opening would
                                  # decide for the player which member their
                                  # first trigger fires. It is the starter
                                  # deploy's own member. A STRING and not a
                                  # number, so `lint_constant_parity` does not
                                  # read it; the mod's twin is
                                  # `FurinaReframeOpening.OpeningMember`.


# ----------------------------------------------------------------------
# THE POOL SEAM (round 2 pick 1 at its default, 2026-09-04; widened by the
# pool pass, `EB-493`, 2026-09-05). `{shipped id: prototype id}`, read by
# `loader._pool_substitutions` under `FURINA_REFRAME` and nowhere else -- the
# Kurage's Oath shape, one for one and at the SAME rarity, so the offer odds do
# not move (`rewards.character_pool` refuses a substitution that would change a
# card's tier).
#
# WHY THE FIRST FOUR AND WHY A SWAP RATHER THAN A SHEET EDIT. The arm mints
# Fanfare by performance only, 2 per trigger and 5 per Evoke, and across three
# rounds the meter ranged 0 to 15 -- while the four shipped riders that GATE on
# it ask 12, 12, 15 and 20. Two of them can essentially never pay under the arm.
# The shipped sheet is Balance-stage content and does not move for a prototype
# arm (R213 B), so the copies are prototype rows and the arm swaps them in at
# the one offer door. WITH THE FLAG OFF this map is unread, `_pool_substitutions`
# returns `{}` for Furina exactly as before, and no surface can see a
# `proto_fr_` id -- which is the acceptance condition, pinned by test.
#
# THE MAP MIRRORS THE SHEET'S OWN `replaces:` KEY, and
# `tier0/tests/test_furina_reframe_pool.py` compares the two in both
# directions -- against this map UNIONED WITH `STARTER_SUBS` below, since a
# `replaces:` row is one seam's or the other's -- so a copy on the surface that
# nobody named in either is a red test rather than a row nothing ever deals.
# ----------------------------------------------------------------------
POOL_SUBS: dict[str, str] = {
    "florid_cadenza": "proto_fr_florid_cadenza",        # 12 -> 6,  uncommon
    "dramatic_entrance": "proto_fr_dramatic_entrance",  # 12 -> 6,  uncommon
    "universal_revelry": "proto_fr_universal_revelry",  # 15 -> 8,  rare
    "flood_of_emotion": "proto_fr_flood_of_emotion",    # 20 -> 10, rare
    # ---- POOL PASS ONE (`EB-493`, `review/active/furina-pool-pass-2026-09-05
    # .md` sec.2; four FOLLOWS off the doctrine read, record 5.5, one of them
    # since withdrawn). A DIFFERENT ARGUMENT AT THE SAME SEAM, and it is worth
    # naming because this map now carries two. The four rows above are COPIES
    # -- the same card at a bar this arm's meter can reach. The three below are
    # NEW ROWS wearing a shipped Common's slot and its art, because rounds 9
    # and 10 read the Salon as
    # FURNITURE: one Deploy in the whole deck, most Companion plays printing
    # "No member on stage: performs nobody", and no card of her own that asks a
    # member to act. Each row answers one of those readings.
    #
    # ALL OF THEM ARE COMMON FOR COMMON, so the offer odds do not move here,
    # and each replaced row was chosen because it is a plain number card of the
    # same type and cost as its replacement (the packet's sec.5 D default; it
    # moves on the seats' word).
    "house_call": "proto_fr_curtain_rises",        # a Deploy on an Attack
    "dinner_service": "proto_fr_second_course",    # a priced 2nd performance
    "blocking_notes": "proto_fr_guest_list",       # a generator in the pool
}
# ROLLING TIDE WAS WITHDRAWN (`EB-552`, round 13, a D default). The kit's own
# perform verb on a draftable row was read once at 2 energy and once at 1, by
# four seats over three rounds, and the answer never moved: "4 damage into one
# body; zero against Plating 8; actively harmful against four Skittish bodies".
# The price was not the reason, so the row left rather than moving again -- the
# loop's first cut. `undercurrent` is absent from this map, which is the whole
# of the change on this side: the shipped Undercurrent is offered again at that
# seam, and the row and its pins left the surface under R213 B's deletion rule.


# ----------------------------------------------------------------------
# THE STARTER SEAM (R254, round 4 pick 1, 2026-09-04). `{shipped id: prototype
# id}`, read by `loader._starter_ids` under `FURINA_REFRAME` and nowhere else
# -- the Kurage's slot-eleven shape, ONE CARD FOR ONE CARD, so the printed ten
# stays ten and this is a substitution rather than a starter rework.
#
# WHY, and it is [USER]'s ruling rather than a number picked here (R254,
# `review/ruled/furina-reframe-round-4-2026-09-04.md` sec.6): "maybe a reader
# in the starter deck? I still want to leave it at just 2 'good' cards, but
# they can be stronger." So the starter keeps its two kit cards -- Salon Début
# and Aria of Recompense -- and ONE of them reads Fanfare. The reader goes on
# Aria, the card the seats had already weighed on three axes. Both numbers are
# LIFTED and neither is new: the 5 is Aria's own printed Encore, the 3 is the
# Fanfare the seat records show on an Aria turn. The loop it closes is the
# arm's own (a stage that performs mints Fanfare, Fanfare pays Encore, Encore
# pays performances) and the shipped Encore decay is its brake.
#
# THE BAR MOVED 6 -> 3 (round 6 sec.4, 2026-09-04, a D default). It was built
# at the rider copies' bar in `POOL_SUBS` above and three seat runs never once
# paid the second line: Aria is played BEFORE the stage performs, so the meter
# it reads is the one an Aria turn actually has. The OFFERED rider copies keep
# their own bars, which are read later in the turn.
#
# THE SHIPPED SHEET STANDS, for `POOL_SUBS`'s reason verbatim: Balance-stage
# content does not move for a prototype arm (R213 B), so the arm carries a copy
# and swaps it in at the one seam. WITH THE FLAG OFF this map is unread and the
# printed Aria is dealt -- the acceptance condition, pinned by
# `tier0/tests/test_furina_reframe_starter.py` rather than intended.
#
# A STARTER MAP AND NOT A POOL ONE, kept apart because they are read at
# different doors and one of them cannot express this pair: a `basic` row is
# unofferable by construction, so naming Aria in `POOL_SUBS` would declare a
# swap `rewards.character_pool` can never make. `loader.declared_starter_
# substitutions` is the flag-blind union the sheet's `replaces:` key is checked
# against here, exactly as `declared_pool_substitutions` is for the other.
#
# THE ALTERNATIVE READER IS HELD, not withdrawn: Salon Début performing its
# member again at 6 Fanfare is the packet's own re-ask if Aria's does not read.
#
# THE SECOND PAIR IS `EB-416`, and it is a wiring defect rather than a new
# decision. The reframe packet's sec.5 ruled the starter deploy NAMES its
# member -- the shipped Salon Début deploys a RANDOM one, which under the
# manual arm decides for the player which member their first Companion play
# will make perform -- and slice 2 built the row for it
# (`proto_fr_salon_debut_named`, "Deploy Mademoiselle Crabaletta"). It had a
# generated class and pins and was wired into NO starter in either engine, so
# the arm went on dealing the random Début; the R254 Aria build found it while
# opening this very seam. The row is unchanged: what is new is that something
# now hands it out.
# ----------------------------------------------------------------------
STARTER_SUBS: dict[str, str] = {
    "aria_of_recompense": "proto_fr_aria_of_recompense",   # 5 Encore, 10 at 3
    "salon_debut": "proto_fr_salon_debut_named",           # names Crabaletta
}


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


def burst_retired(player) -> bool:
    """`EB-365` (R251). IS THE SHIPPED BURST METER RETIRED FOR THIS PLAYER?

    The round-one seat's meter read `78/70`, over its own cap, and *Let the
    People Rejoice* arrived off that overflow to take the boss from 28 to 14 --
    the run's clutch turn, and the shipped kit's rather than the reframe's.
    R220 B had sequenced the Burst fold last; the pick's new fact is that the
    shipped meter will sit inside every Furina read until it goes.

    ONE QUESTION, asked by the income funnel (`resources.gain_burst`) and by
    the kit grant (`combat.grant_charged_kit`), so "she has no Burst meter
    under the arm" is one decision rather than two that can be retired by
    halves. Klee's `EB-266` and Kokomi's `EB-327` are the same sentence one
    character over, and their guards sit at the same funnel.

    ARM-ONLY. The shared retirement (`EB-199`, `EB-200`) still owns the shipped
    engines: `burst_max`, the ops, the `requires` gate and every other
    character's meter are untouched here. The mod's twin is
    `FurinaReframe.BurstRetiredFor`.
    """
    return FURINA_REFRAME and FURINA_REFRAME_BURST and is_furina(player)


def opening_encore(player) -> int:
    """R258 (`EB-479`): how much Encore she opens a combat with -- 2 under the
    arm, 0 everywhere else.

    THE MASTER FLAG AND NO LEG OF ITS OWN. The pick is a fact about the whole
    reframe rather than about the manual stage, the Evoke or the meter: what
    it fixes is that turn one had no decision to make, and every leg of the arm
    was in the room for that. A sixth flag would let a build run the arm with
    the opening it was ruled out of.
    """
    return OPENING_ENCORE if (FURINA_REFRAME and is_furina(player)) else 0


def grant_opening_encore(state) -> None:
    """Pay it, once, on turn one.

    THE SITE IS `AfterPlayerTurnStart` ON BOTH SIDES, `KleeOverhaulOpening`'s
    argument taken whole one character over: this engine fires its combat-start
    effects on TURN 1 after the block clear, the energy reset and the draw, so
    a grant written at true combat start would land before the setup that
    follows it -- and turn 1 of that hook is the moment the blind-play page
    renders its first Encore line, which is where the number has to show.

    `== 1` rather than `<= 1`, so an extra first turn cannot pay twice. The
    mod's twin is `FurinaReframeOpening.GrantEncore`.
    """
    from tier0.engine import resources           # late: avoids the cycle
    if state.turn != 1:
        return
    n = opening_encore(state.player)
    if n <= 0:
        return
    state.emit("fr_opening_encore", amount=n)
    resources.gain_encore(state, n, "furina_reframe/opening_encore")


def opening_member(player):
    """R260 (`EB-553`): who is on the Salon stage when a combat opens, or None
    where nobody is.

    THE MASTER FLAG AND NO LEG OF ITS OWN, `opening_encore`'s gate one rule
    over and for its reason: the pick is a fact about the whole reframe -- turn
    one was empty BY CONSTRUCTION, so every Companion card printed "performs
    nobody" on it -- and a sixth flag would let a build run the arm with the
    opening it was ruled out of.

    The mod's twin is `FurinaReframeOpening.OpeningMemberFor`.
    """
    return (OPENING_MEMBER
            if (FURINA_REFRAME and is_furina(player)) else None)


def field_opening_member(state) -> None:
    """Field her, once, on turn one.

    R260 (2026-09-05): under the reframe every combat opens with a member
    ALREADY on the stage, the way the Necrobinder's Osty and the Defect's first
    orb are already out. Round 11 read both lanes' turn one as empty by
    construction and the natural lane counted it -- zero empty turns in the
    fights where Salon Debut was in the opening hand, six of twenty-two
    otherwise. [USER] took the relic over an Innate starter, so Salon Debut
    stays as printed and deploys a SECOND body; duplicates on the stage are
    legal and always have been (Grand Gala deploys Crabaletta twice on the
    shipped sheet).

    SHE PERFORMS ON ARRIVAL, because this goes through
    `effects._deploy_salon_members` -- the one deploy -- and the arm's
    deploy-performs clause lives inside it. That is the ruling read straight:
    the relic deploys, and a deploy performs.

    AND THE ARRIVAL IS FREE (`EB-558`, 2026-09-05). It was not at first, and
    the arithmetic was the defect: the performance paid
    `C.SALON_TICK_ENCORE_COST` out of the opening bank, so turn one opened on 1
    Encore and could buy NEITHER of the two doors R258 sized its 2 for -- a
    Spotlight designation and a wet performance both cost 2, and the pick was
    sized to buy exactly one of them. [USER]'s own analogy for R260 is the
    rule: "one free Osty". The Necrobinder's pet is summoned and out and
    nothing on turn one is billed for it being there, so the relic's member
    arrives, performs PAID -- full value, not the dry three-quarters -- and
    spends nothing. R258's 2 stands untouched and turn one opens on all of it
    with the stage occupied.

    THE FREE PASS IS THE ONE PERFORMANCE AND NOT THE TURN. Everything after it
    pays: next turn's upkeep bills her 1 like any member, and every DEPLOY a
    card makes pays as it always has. `free=` is a parameter on
    `salon_member_act` -- the one implementation of a member acting -- rather
    than a branch written here, so this arrival cannot drift from the upkeep
    that performs the same member.

    THE SITE IS `grant_opening_encore`'s, one line later and AFTER it. The
    ordering no longer decides the arithmetic now that the arrival is free, and
    it stays where it is: the mint and the pilot both read a bank, and a
    performance recorded before the bank exists would be a different turn one
    on paper. `== 1` rather than `<= 1`, so an extra first turn cannot field
    twice. The mod's twin is `FurinaReframeOpening.FieldOpeningMember`.
    """
    from tier0.engine import effects              # late: avoids the cycle
    if state.turn != 1:
        return
    member = opening_member(state.player)
    if member is None:
        return
    state.emit("fr_opening_stage", member=member)
    effects._deploy_salon_members(state, 1, member, free_performance=True)


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


def companion_replay(state, card) -> None:
    """A Companion REPLAY -- the extra play, said out loud (`EB-420`).

    IT PERFORMS, SINCE `EB-464`. It did not until the r8 ruling:
    `combat._finish_play` gated the trigger above on `replay_index == 0`, on
    LAW:145 read through "a replay is one card being resolved twice, and a
    per-play bound a replay can double is not a bound" (`KleeCompanionSpark`,
    the same clause one kit over). That clause is about a resource MINT, and a
    performance is not one -- so the gate came off this trigger and stayed on
    Klee's mint, which is what it was written for.

    THE FACT STILL LEAVES NO TRACE, which is why it keeps its event, the same
    argument the whiff above is emitted under: two performs off two plays and
    two performs off one Duet-doubled play are the same board a moment later,
    and the performance list cannot tell them apart. The round-5 seat played
    Duet into Freminet, counted three Companion plays' worth of triggers, got
    two, and found no line naming the second play at all. C# twin:
    `SalonMemberPower.NoteCompanionReplay`, at the same site.

    NOTHING HAPPENS HERE. It emits and returns; no rule reads the event back.
    """
    if not manual_active(state.player) or not card.is_companion:
        return
    state.emit("salon_replay", card=card.id)
