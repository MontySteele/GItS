"""Furina, THE STAGE -- the quarantined prototype engine (`EB-720`).

`review/active/furina-stage-brief-2026-09-08.md` is the design, ruled R269
(2026-09-08, sec.11): "build it". Sections 3, 10, 12 and 13 are the rules, the
disclosed defaults, the faces and the reports; every number below cites the
rule it came from and NOTHING IN THIS MODULE IS ON.

WHAT THE ARM IS, in one paragraph. Furina's party is three seats -- front,
middle, back -- and a performer standing in one is a creature on her side with
its own bar, called Fanfare on the faces. Enemies hit her Block, then the LEAD
performer's bar, then her (rule 6, per attack, never running on to the middle
seat). Her cards SPEND that bar for bigger numbers (rule 8), and a bar emptied
by a Spend earns a bow (rule 9) while one emptied by a hit earns nothing
(rule 7). Every performer performs a flat act at the end of her turn (rule 10),
and her own HP is touched by nothing in the kit (rule 11).

WHY THE FLAGS LIVE HERE AND NOT IN `constants.py`, and it is `furina_reframe`'s
argument inherited rather than re-made: a flag in `constants.py` is read by the
parity gate and the constant census, and a flag the shipped engine only
branches on is quarantined machinery. With `FURINA_STAGE` False this module's
every reader returns the empty answer and the engine is the shipped engine byte
for byte (`tier0/tests/test_furina_stage.py` pins that arm first).

THE ONE STATE THIS ARM ADDS is `Player.stage`: an ordered list of
`[member, fanfare]` pairs, front seat first. It is the source of truth and
there is no counter beside it -- the brief's sec.2 lore table is explicit that
"Fanfare is the performer's bar itself ... no counter beside it", which is what
retired the reframe's `Player.fanfare` meter for this character.

WHAT THIS MODULE DOES NOT DO. It does not touch the shipped Salon
(`Player.salon`), the shipped Fanfare meter, Encore, or the Spotlight: the
Stage is a REPLACEMENT kit and the arm swaps her starter and her offerable pool
at the loader's two doors, so a run under the flag never draws a card that
reads any of them. It also does not render: the strip the brief's sec.8 asks
for ("the lead's bar beside her Block, in the damage order") is the C# half's,
on branch `stage-cs`.
"""

from __future__ import annotations

CHARACTER = "furina"

# ----------------------------------------------------------------------
# THE FLAG. OFF. It may not default True without a ruling.
# ----------------------------------------------------------------------
FURINA_STAGE = False

# ----------------------------------------------------------------------
# THE NUMBERS. Brief sec.3 and sec.10 default 3: "Opening Fanfare 3, regen 1
# from turn two, Refill 5, the nominal rate 2, the acts and the bows at the
# numbers in sec.3 (D, the sim's)." A D default under the delegation ladder --
# disclosed here, applied, never queued.
# ----------------------------------------------------------------------
SEATS = 3                    # rule 1: front, middle, back.
OPENING_MEMBER = "usher"     # sec.10 default 1 (E): FIXED, for legibility.
OPENING_FANFARE = 3          # rule 2, from the relic.
SUMMON_FANFARE = 1           # rule 3: a newcomer arrives at 1.
LEAD_REGEN = 1               # rule 4: the LEAD only, from her second turn.
REFILL_AMOUNT = 5            # rule 5: "Raise 5 Fanfare on the back performer."
SPEND_RATE_NOMINAL = 2       # sec.4: "a nominal rate, not a measure". NOTHING
                             # READS THIS. It is here because the brief names
                             # it and a reader will look for it; every Spend
                             # rider prints its own two numbers on its own face.

#: The three, in the order the brief prints them (sec.12's Commons).
PERFORMERS = ("usher", "chevalmarin", "crabaletta")

#: The starting relic (sec.12): "At the start of combat, Usher takes the front
#: seat with 3 Fanfare." A NAME rather than a number, so
#: `lint_constant_parity` does not read it.
RELIC = "salon_solitaire"

# Rule 10, the ACTS -- flat, from any seat, at the end of Furina's turn, and
# they do not read the bar.
ACT_USHER_BLOCK = 3
ACT_CHEVALMARIN_DAMAGE = 2   # to EVERY enemy, and applies Hydro.
ACT_CRABALETTA_DAMAGE = 5    # to a random enemy.

# Rule 9, the BOWS -- earned by a Spend that empties the bar, and by nothing
# else. Death by a hit, and leaving by rotation, earn none (sec.10 default 5).
BOW_USHER_BLOCK = 4
BOW_CRABALETTA_DAMAGE = 8    # to a random enemy. Chevalmarin's bow is Hydro
                             # on every enemy and carries no number.

#: Where a Raise lands. Rule 5: the BACK-MOST performer, which is the lead when
#: it is alone. Written out as words so a row and a face say the same thing.
SEAT_BACK = "back"
SEAT_LEAD = "lead"


# ----------------------------------------------------------------------
# THE STARTER SEAM (`EB-719`). `{shipped id: prototype id}`, read by
# `loader._starter_ids` under `FURINA_STAGE` and nowhere else -- the reframe's
# slot shape inherited, one card for one card, so the printed ten stays ten and
# this is a substitution rather than a starter rework.
#
# THE SEVEN BASICS ARE UNTOUCHED AND THAT IS A STANDING RULE, not a choice made
# here: three Soloist's Solicitation, three Stage Presence and Regal Bearing
# are the base game's basics and stay exactly as printed (brief sec.7 says so
# in as many words -- "all the base game's basics and untouched"). The three
# swapped ids are her three KIT starters, which is the whole of what an arm may
# move.
# ----------------------------------------------------------------------
STARTER_SUBS: dict[str, str] = {
    "aria_of_recompense": "proto_fs_curtain_rise",     # Deal 7 / Spend 3: 13
    "salon_debut": "proto_fs_salon_debut",             # the random summon
    "an_invitation": "proto_fs_standing_ovation",      # Raise 5 at the back
}


# ----------------------------------------------------------------------
# THE POOL SEAM (`EB-719`). `{shipped id: prototype id}`, read by
# `loader._pool_substitutions` under `FURINA_STAGE` and nowhere else. Fourteen
# rows -- the brief's sec.12 batch one minus the three starters above -- each
# swapped ONE FOR ONE AT THE SAME RARITY, so the offer odds do not move
# (`rewards.character_pool` refuses a substitution that would change a card's
# tier).
#
# WHY A SWAP AND NOT A SHEET EDIT, for `furina_reframe.POOL_SUBS`'s reason
# verbatim: the shipped sheet is Balance-stage content and does not move for a
# prototype arm (R213 B), so the batch is prototype rows and the arm swaps them
# in at the one offer door. WITH THE FLAG OFF this map is unread and no surface
# can see a `proto_fs_` id.
#
# WHICH SHIPPED ROW EACH REPLACED, and it is a D default disclosed rather than
# a design act: the same rarity always, the same TYPE and COST where her sheet
# had one to spare, and otherwise the nearest plain row of that rarity. The
# three named summons land on the three shipped rows of the same NAME
# (`gentilhomme_usher`, `surintendante_chevalmarin`,
# `mademoiselle_crabaletta`), which is the cleanest swap on the sheet: same
# rarity, same type, same cost, same card in the fiction.
#
# THIS IS A PARTIAL SWAP AND SAYS SO. Fourteen of her twenty-three Commons,
# thirty-seven Uncommons and nineteen Rares move; the rest of her pool still
# prints Encore, the shipped Fanfare meter and the shipped Salon. Batch one is
# "enough to play Preserve and Expend against each other" (sec.12) and not a
# whole pool, so a run under the arm drafts a mixed sheet by construction.
# That is a KNOWN limitation of round one, not an oversight, and it belongs in
# the round packet's own "what this round cannot see".
# ----------------------------------------------------------------------
POOL_SUBS: dict[str, str] = {
    # --- Commons (eight) ---
    "gentilhomme_usher": "proto_fs_gentilhomme_usher",
    "surintendante_chevalmarin": "proto_fs_surintendante_chevalmarin",
    "mademoiselle_crabaletta": "proto_fs_mademoiselle_crabaletta",
    "suffering_for_art": "proto_fs_understudy",        # 0 Skill for 0 Skill
    "blocking_notes": "proto_fs_warm_reception",       # 1 Skill for 1 Skill
    "usher_the_waves": "proto_fs_tidal_flourish",      # 1 Attack for 1 Attack
    "stage_lights": "proto_fs_interposition",          # 1 Skill for 1 Skill
    "held_breath": "proto_fs_scene_change",            # 1 Skill -> a 0 Skill
    # --- Uncommons (five) ---
    "torrential_turn": "proto_fs_grand_entrance",      # 2 Attack for 2 Attack
    "crescendo": "proto_fs_ousia_surge",               # 1 Attack for 1 Attack
    "many_waters_melody": "proto_fs_pneuma_refrain",   # 1 Skill for 1 Skill
    "change_the_bill": "proto_fs_bis",                 # 1 Skill for 1 Skill
    "take_your_bow": "proto_fs_final_bow",             # 0 Skill -> a 1 Skill
    # --- Rare (one) ---
    "universal_revelry": "proto_fs_let_the_people_rejoice",   # 2 Attack, 2 Attack
}


# ----------------------------------------------------------------------
# The readers. Functions rather than module constants at the call sites, so a
# test can flip the flag with `monkeypatch.setattr` and every branch sees it.
# ----------------------------------------------------------------------
def is_furina(player) -> bool:
    return getattr(player, "character_id", None) == CHARACTER


def active(player) -> bool:
    """Is the Stage live for this player? Every leg is AND-ed with this."""
    return FURINA_STAGE and is_furina(player)


def stage(player) -> list:
    """The seats, front first. `[]` when the arm is off, always -- so a caller
    that walks the stage on a shipped run walks nothing rather than branching
    on the flag itself."""
    return getattr(player, "stage", []) if active(player) else []


def lead(player):
    """The FRONT seat's `[member, fanfare]` pair, or None on an empty stage."""
    seats = stage(player)
    return seats[0] if seats else None


def back(player):
    """The BACK-MOST occupied seat's pair -- the lead when it is alone
    (rule 5). None on an empty stage."""
    seats = stage(player)
    return seats[-1] if seats else None


def lead_fanfare(player) -> int:
    pair = lead(player)
    return pair[1] if pair else 0


def back_fanfare(player) -> int:
    pair = back(player)
    return pair[1] if pair else 0


def total_fanfare(player) -> int:
    return sum(f for _m, f in stage(player))


def count(player) -> int:
    return len(stage(player))


def _seats(player) -> list:
    """The mutable list, created on first use. Only writers call this."""
    if not hasattr(player, "stage") or player.stage is None:
        player.stage = []
    return player.stage


# ----------------------------------------------------------------------
# Arrivals and departures.
# ----------------------------------------------------------------------
def open_combat(state) -> None:
    """The relic (rule 2): Usher takes the front seat at 3, once, on turn one.

    THE SITE IS `AfterPlayerTurnStart`, which is `furina_reframe`'s argument
    inherited whole: this engine fires its combat-start effects on TURN 1 after
    the block clear, the energy reset and the draw, so a grant written at true
    combat start would land before the setup that follows it. `== 1` rather
    than `<= 1`, so an extra first turn cannot field twice.

    IT REPLACES WHATEVER RELIC THE SIM GIVES HER. The loader's
    `_starting_relic_effects` returns `[]` for Furina under the arm -- see
    `loader._starting_relic_effects` -- so this is her one relic and not a
    second one on top.
    """
    if not active(state.player) or state.turn != 1:
        return
    seats = _seats(state.player)
    if seats:
        return
    seats.append([OPENING_MEMBER, OPENING_FANFARE])
    state.emit("stage_open", member=OPENING_MEMBER, fanfare=OPENING_FANFARE)


def summon(state, member: str) -> None:
    """Rule 3. A summon fills the BACK-MOST EMPTY seat with that performer at
    1. On a FULL stage it rotates the cast: the front performer leaves without
    a bow, the other two step forward, and the newcomer takes the back seat
    WITH THE LEAVER'S FANFARE -- "pools are never lost to rotation".

    AND THE NEWCOMER PERFORMS ITS ACT THE SAME TURN (rule 3, as GPT's read of
    draft 1 corrected it, sec.14). That is `perform` below, called here, so a
    summon is one call at every site rather than a pair somebody has to
    remember.
    """
    p = state.player
    if not active(p):
        return
    if member not in PERFORMERS:
        # A typo in a row must not degrade quietly into "somebody": the deploy
        # verb one arm over refuses an unknown member and so does this one.
        raise ValueError(f"unknown performer {member!r}")
    seats = _seats(p)
    if len(seats) < SEATS:
        seats.append([member, SUMMON_FANFARE])
        state.emit("stage_summon", member=member, fanfare=SUMMON_FANFARE,
                   seats=len(seats), rotated=False)
    else:
        leaver, carried = seats.pop(0)
        seats.append([member, carried])
        state.emit("stage_rotate_out", member=leaver, fanfare=carried,
                   arriving=member)
        state.emit("stage_summon", member=member, fanfare=carried,
                   seats=len(seats), rotated=True)
    perform(state, member)


def rotate(state) -> None:
    """Scene Change (sec.12): the FRONT performer moves to the back seat, bar
    and all. A pure reorder -- no bow, no act, nothing lost (sec.5.2:
    "Rotation grants no bow, and the card's name says nothing about one").

    NOT SILENT ON AN EMPTY STAGE, for `salon_rotate`'s reason one arm over: a
    rotate that found nothing to rotate is invisible in the state afterwards.
    """
    p = state.player
    if not active(p):
        return
    seats = _seats(p)
    if not seats:
        state.emit("stage_rotate_whiffed")
        return
    seats.append(seats.pop(0))
    state.emit("stage_scene_change", company=[m for m, _f in seats])


def _leave(state, index: int, *, bowed: bool, reason: str) -> None:
    """A performer leaves the stage. ONE implementation, three callers (a hit
    that empties the bar, a Spend that does, and Final Bow), so "a bow is
    earned by Spend only" cannot drift between them."""
    p = state.player
    seats = _seats(p)
    member, remaining = seats.pop(index)
    state.emit("stage_leave", member=member, bowed=bowed, reason=reason,
               fanfare=remaining)
    if bowed:
        _bow(state, member)


def _bow(state, member: str) -> None:
    """Rule 9, the curtain call, performed ONCE by a performer emptied by a
    Spend. Usher: Furina gains 4 Block. Chevalmarin: Hydro on every enemy.
    Crabaletta: deal 8 to a random enemy."""
    from tier0.engine import effects, reactions       # late: avoids the cycle
    p = state.player
    state.emit("stage_bow", member=member)
    if member == "usher":
        p.block += BOW_USHER_BLOCK
    elif member == "chevalmarin":
        for enemy in list(state.living_enemies):
            reactions.resolve_hit(state, enemy, "hydro", 0,
                                  "furina_stage/bow")
    elif member == "crabaletta":
        if state.living_enemies:
            enemy = state.rng.choice(state.living_enemies)
            effects.deal_damage_to_enemy(state, enemy, BOW_CRABALETTA_DAMAGE,
                                         source="furina_stage/bow")


# ----------------------------------------------------------------------
# The bar: regen, Raise, Spend, and the damage order.
# ----------------------------------------------------------------------
def turn_start_regen(state) -> None:
    """Rule 4. The LEAD regains 1 at the start of Furina's turn, from her
    SECOND turn on (sec.3 rule 2: "the first hand sees 3"). Only the lead.
    Bars have no cap, so nothing clamps here."""
    p = state.player
    if not active(p) or state.turn < 2:
        return
    pair = lead(p)
    if pair is None:
        return
    pair[1] += LEAD_REGEN
    state.emit("stage_regen", member=pair[0], amount=LEAD_REGEN,
               fanfare=pair[1])


def raise_fanfare(state, amount: int, seat: str = SEAT_BACK) -> int:
    """Rule 5. "Raise N Fanfare on the back performer" lands on the BACK-MOST
    performer, which is the lead when it is alone. `seat=SEAT_LEAD` is the
    other spelling, for a face that names the lead instead.

    Returns what landed -- 0 on an empty stage, which the caller emits rather
    than swallowing, for the reason `rotate` gives above.
    """
    p = state.player
    if not active(p) or amount <= 0:
        return 0
    pair = lead(p) if seat == SEAT_LEAD else back(p)
    if pair is None:
        state.emit("stage_raise_whiffed", amount=amount, seat=seat)
        return 0
    pair[1] += int(amount)
    state.emit("stage_raise", member=pair[0], amount=int(amount), seat=seat,
               fanfare=pair[1])
    return int(amount)


def can_spend(player) -> bool:
    """Rule 8's one refusal: "With no performer on stage the rider cannot fire
    and the card plays at its base number." A bar of ANY size can pay -- one
    point buys the whole rider -- so the question is occupancy and never
    size."""
    return active(player) and bool(stage(player))


def spend(state, amount: int) -> int:
    """Rule 8. Pay N from the LEAD's bar for a rider that has already been
    decided to fire. "If the lead has less than N, the rider STILL fires in
    full, the lead pays what it has and leaves with a bow" (sec.10 default 4,
    [USER]'s own words).

    Returns what was actually paid, which is the number sec.13's first report
    is bucketed on -- NOT the printed N. The caller has already checked
    `can_spend`; this refuses an empty stage rather than inventing a payment.
    """
    p = state.player
    if not active(p):
        return 0
    pair = lead(p)
    if pair is None:
        state.emit("stage_spend_whiffed", amount=amount)
        return 0
    member, bar = pair
    paid = min(int(amount), bar)
    pair[1] = bar - paid
    state.emit("stage_spend", member=member, asked=int(amount), paid=paid,
               bar_at_spend=bar, fanfare=pair[1], turn=state.turn,
               enemies_alive=len(state.living_enemies))
    if pair[1] <= 0:
        _leave(state, 0, bowed=True, reason="spend")
    return paid


#: What `collect_all` emptied, read back by `bow_and_return`. On the STATE and
#: not on the player, because the pair is one card play's two halves and dies
#: with it; a company left here by a play that never reached its third clause
#: is overwritten by the next `collect_all` and read by nothing else.
_PENDING = "_stage_curtain_company"


def collect_all(state) -> int:
    """*Let the People Rejoice* (sec.5.3 / sec.12), first clause: "Spend all
    Fanfare on stage." Empties every bar, remembers who was standing, and
    returns the total -- which is the card's damage number. "Worth nothing on
    an empty stage."

    THE BOWS ARE NOT HERE. `bow_and_return` below is the card's third clause
    and the printed order puts the card's own area damage between them; see
    `effects._op_stage_spend_all`.
    """
    p = state.player
    if not active(p):
        return 0
    seats = _seats(p)
    if not seats:
        state.emit("stage_spend_all_whiffed")
        setattr(state, _PENDING, [])
        return 0
    company = [m for m, _f in seats]
    total = sum(f for _m, f in seats)
    seats.clear()
    setattr(state, _PENDING, list(company))
    state.emit("stage_spend_all", total=total, company=list(company))
    return total


def bow_and_return(state) -> None:
    """The same card's third clause: "Every performer takes a bow, then returns
    at 1."

    The bows fire in seat order and the cast returns in the SAME order, so the
    front seat is still the front seat afterwards. The two are separate loops
    because the sentence is: every bow lands on the board the card left, and
    only then does anybody come back.
    """
    p = state.player
    if not active(p):
        return
    company = list(getattr(state, _PENDING, []) or [])
    setattr(state, _PENDING, [])
    if not company:
        return
    for member in company:
        state.emit("stage_leave", member=member, bowed=True,
                   reason="spend_all", fanfare=0)
        _bow(state, member)
    seats = _seats(p)
    for member in company:
        if len(seats) < SEATS:
            seats.append([member, SUMMON_FANFARE])
    state.emit("stage_encore_return", company=[m for m, _f in seats],
               fanfare=SUMMON_FANFARE)


def final_bow(state) -> int:
    """*Final Bow* (sec.12): "The lead performer takes a bow and leaves. Gain
    Block equal to its Fanfare."

    A BOW WITHOUT A SPEND, and the one card that grants one. Rule 9 says a bow
    is earned by Spend; this face pays for it with a card and an Exhaust
    instead, which is a printed exception rather than a hole in the rule.
    Returns the bar it left with, which is the Block the card gains.
    """
    p = state.player
    if not active(p):
        return 0
    pair = lead(p)
    if pair is None:
        state.emit("stage_final_bow_whiffed")
        return 0
    bar = pair[1]
    _leave(state, 0, bowed=True, reason="final_bow")
    return bar


def absorb(state, incoming: int) -> int:
    """Rule 6, the DAMAGE ORDER, per attack: Furina's Block, then the LEAD
    performer's Fanfare, then Furina.

    Called from `combat._enemy_action`'s hit loop with what one hit put through
    her Block, and returns what the lead ate. "The lead absorbs what one attack
    puts through her Block, UP TO ITS BAR; the rest reaches Furina. IT NEVER
    RUNS ON TO THE MIDDLE SEAT." A big single hit therefore rips through the
    lead and lands on her; a flurry can kill the lead and leave her untouched,
    because the call site is per HIT and rule 7 empties the seat between them.

    A performer emptied HERE takes no bow (rule 7): it just leaves.
    """
    p = state.player
    if not active(p) or incoming <= 0:
        return 0
    pair = lead(p)
    if pair is None:
        return 0
    member, bar = pair
    eaten = min(int(incoming), bar)
    pair[1] = bar - eaten
    state.emit("stage_absorb", member=member, amount=eaten,
               incoming=int(incoming), fanfare=pair[1])
    if pair[1] <= 0:
        _leave(state, 0, bowed=False, reason="hit")
    return eaten


# ----------------------------------------------------------------------
# The acts.
# ----------------------------------------------------------------------
def perform(state, member: str) -> None:
    """Rule 10: one performer's flat act, from any seat, reading no bar.

    ONE implementation, three callers -- the end-of-turn sweep, a newcomer's
    arrival (rule 3) and *Bis!* (sec.12) -- so an act cannot mean three things.
    """
    from tier0.engine import effects, reactions       # late: avoids the cycle
    p = state.player
    if not active(p):
        return
    state.emit("stage_act", member=member)
    if member == "usher":
        p.block += ACT_USHER_BLOCK
    elif member == "chevalmarin":
        for enemy in list(state.living_enemies):
            effects.deal_damage_to_enemy(state, enemy,
                                         ACT_CHEVALMARIN_DAMAGE,
                                         element="hydro",
                                         source="furina_stage/act")
        # The Hydro is the ACT's, not the hit's: sec.3 rule 10 reads "deals 2
        # to every enemy AND APPLIES HYDRO", so a dead body or a zero that
        # Block ate still leaves the aura the Guest Cast plan (sec.5.3) reacts
        # off. `deal_damage_to_enemy` with an element already applies on a
        # landing hit; this second pass is what makes the clause hold when it
        # does not land.
        for enemy in list(state.living_enemies):
            reactions.resolve_hit(state, enemy, "hydro", 0,
                                  "furina_stage/act")
    elif member == "crabaletta":
        if state.living_enemies:
            enemy = state.rng.choice(state.living_enemies)
            effects.deal_damage_to_enemy(state, enemy, ACT_CRABALETTA_DAMAGE,
                                         source="furina_stage/act")


def perform_lead(state) -> None:
    """*Bis!* (sec.12): the lead performer performs its act now."""
    p = state.player
    if not active(p):
        return
    pair = lead(p)
    if pair is None:
        state.emit("stage_act_whiffed")
        return
    perform(state, pair[0])


def end_of_turn_acts(state) -> None:
    """Rule 10, the sweep: EACH performer performs at the end of Furina's
    turn, in seat order, front first.

    THE LIST IS SNAPSHOTTED, so a cast that changes mid-sweep (Crabaletta's 5
    killing the last enemy) cannot skip or double an act, and the walk stops
    when the fight is over.
    """
    p = state.player
    if not active(p):
        return
    company = [m for m, _f in stage(p)]
    if not company:
        return
    state.emit("stage_acts", company=list(company))
    for member in company:
        if state.over or not p.alive or not state.living_enemies:
            break
        perform(state, member)


# ----------------------------------------------------------------------
# THE TURN CENSUS (sec.13, "Turns with one, two and three performers on
# stage"). INSTRUMENT ONLY: nothing reads it back to decide anything, which is
# the same fence `state.spark_ledger` carries one arm over.
# ----------------------------------------------------------------------
def note_turn_census(state) -> None:
    """One sample per player turn, taken at turn CLOSE beside `turn_close`, and
    emitted at zero as well -- a distribution that silently omits its zeros is
    not a distribution."""
    p = state.player
    if not active(p):
        return
    state.emit("stage_census", performers=count(p), lead_fanfare=lead_fanfare(p),
               total_fanfare=total_fanfare(p),
               company=[m for m, _f in stage(p)])
