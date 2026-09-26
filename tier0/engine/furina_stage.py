"""Furina, THE STAGE -- the quarantined prototype engine (`EB-724`).

`review/active/furina-stage-brief-2026-09-08.md` is the design, ruled R269
(2026-09-08, sec.11): "build it". Sections 3, 10, 12 and 13 are the rules, the
disclosed defaults, the faces and the reports; every number below cites the
rule it came from and NOTHING IN THIS MODULE IS ON.

WHAT THE ARM IS, in one paragraph. Furina's party is three seats -- front,
middle, back -- and a performer standing in one is a creature on her side with
its own bar, called Fanfare on the faces. Enemies hit her Block, then the LEAD
performer's bar, then her (rule 6, per attack, never running on to the middle
seat). Her cards SPEND the BACK performer's bar for bigger numbers, and only at
the full price (rule 8 as R276 ruled it: the lead is the shield, the back is
the bank), and a bar emptied by a Spend earns a bow (rule 9) while one emptied
by a hit earns nothing (rule 7). Every performer performs a flat act at the
end of her turn (rule 10), and her own HP is touched by nothing in the kit
(rule 11).

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
SOLD_OUT_SEATS = 4           # Sold Out (2026-09-26): front, two middles, back.
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
# they do not read the bar. NO ACT APPLIES HYDRO (draft 3, 2026-09-25; [USER]:
# "removing the Hydro application from the end-of-turn effects on Chevalmarin
# and Crabaletta"): the two damage acts are plain damage, and Hydro comes from
# cards (Tidal Flourish and Quick Cue's Spend modes, Chevalmarin's card).
ACT_USHER_BLOCK = 3
ACT_CHEVALMARIN_DAMAGE = 2   # to EVERY enemy.
ACT_CRABALETTA_DAMAGE = 5    # to a random enemy.

# Rule 9, the BOW, is the performer's own act ONE MORE TIME as it leaves
# (draft 3, 2026-09-25, the Stage review's pick 1). It has no numbers of its
# own: `_bow` calls `perform`.

# THE GUEST CAST (2026-09-25, review/active/furina-guest-batch-2026-09-25.md,
# ruled that evening; then no guest cap, and one of each guest). Eight Fontaine
# characters reach the Stage through Furina's own Guest Star cards; each is a
# performer in every other way. What a guest ARRIVES with is its card's; the
# acts' numbers are these, mirrored by `FurinaStageLaw`. C# twin:
# `Powers/Prototype/FurinaStageGuests.cs`.
GUESTS = ("neuvillette", "clorinde", "navia", "chevreuse", "wriothesley",
          "sigewinne", "charlotte", "lynette",
          # THE SUPPORTING POOL (2026-09-26): two more guests, each with a job
          # the eight lack. Lyney rotates the stage; Escoffier feeds the cast.
          "lyney", "escoffier")
ACT_NEUVILLETTE_PRICE = 3     # of his own Fanfare ...
ACT_NEUVILLETTE_DAMAGE = 8    # ... for Hydro damage to ALL enemies.
ACT_CLORINDE_TAX = 1          # from each other performer ...
ACT_CLORINDE_DAMAGE = 8       # ... for Electro damage to a random enemy.
ACT_CHEVREUSE_PRICE = 2       # Spent from the back performer ...
ACT_CHEVREUSE_ENERGY = 1      # ... for Energy next turn.
ACT_WRIOTHESLEY_RATE = 2      # Cryo damage per Fanfare lost since his act.
ACT_SIGEWINNE_GIFT = 3        # to the performer behind her.
ACT_CHARLOTTE_GIFT = 1        # to each other performer.
ACT_LYNETTE_DAMAGE = 3        # Anemo damage to a random enemy, one with an
#                               aura if any (2026-09-25 night: the act always
#                               lands, and Swirls where it finds an aura).
# THE SUPPORTING POOL (2026-09-26, review/active/furina-supporting-pool-
# 2026-09-26.md). Lyney pays 2 of his own for 6 Pyro damage to a random enemy,
# then swaps the front and back performers; Escoffier pays 3 of her own to give
# each other performer 2 and deal 3 Cryo damage to ALL enemies.
ACT_LYNEY_PRICE = 2
ACT_LYNEY_DAMAGE = 6
ACT_ESCOFFIER_PRICE = 3
ACT_ESCOFFIER_GIFT = 2
ACT_ESCOFFIER_DAMAGE = 3

#: The elements the guests' damage acts carry (the Guest Cast's LAW
#: amendment: a guest on Furina's stage may carry its element).
GUEST_ELEMENTS = {"neuvillette": "hydro", "clorinde": "electro",
                  "navia": "geo", "wriothesley": "cryo", "lynette": "anemo",
                  "lyney": "pyro", "escoffier": "cryo"}

# Rule 12, THE APPLAUSE FADES (draft 3, 2026-09-25). At the end of Furina's
# turn, after the acts, each performer BEHIND THE FRONT loses half of its
# Fanfare above this, rounded down (`fade_loss`). The front never fades. The
# threshold is the knob seat rounds tune.
FADE_THRESHOLD = 5
#: THE SUPPORTING POOL (2026-09-26), *Eternal Applause*: "Your performers fade
#: only above 10 Fanfare, not 5." A Rare that bends rule 12 rather than
#: removing it; copies do not stack further.
ETERNAL_FADE_THRESHOLD = 10

#: Where a Raise lands. Rule 5: the BACK-MOST performer, which is the lead when
#: it is alone. Written out as words so a row and a face say the same thing.
#: `all` is R276 batch two's Gala Dinner.
SEAT_BACK = "back"
SEAT_LEAD = "lead"
SEAT_ALL = "all"

# R276 batch two's five powers (their C# twins are in
# `Powers/Prototype/FurinaStagePowers.cs`).
FULL_HOUSE = "fs_full_house"
THUNDEROUS_APPLAUSE = "fs_thunderous_applause"
RAPT_AUDIENCE = "fs_rapt_audience"
FIVE_CENTURY_ACT = "fs_five_century_act"
ARKHE_ALIGNMENT = "fs_arkhe_alignment"
#: The supporting pool's Sold Out (2026-09-26, family 7): "Your stage has a
#: fourth seat." Its C# twin is `SoldOutPower`; `capacity` reads it.
SOLD_OUT = "fs_sold_out"
#: Arkhe Alignment's Pneuma half: what the lead regains. C# twin:
#: `ArkheAlignmentPower.PneumaLeadRegain`.
PNEUMA_LEAD_REGAIN = 2

# THE SUPPORTING POOL's powers (2026-09-26). Their C# twins are in
# `Powers/Prototype/FurinaStagePowers.cs`; each is a switch the rule it bends
# asks about.
REVOLVING_STAGE = "fs_revolving_stage"      # turn start: back to the front
SEASON_TICKETS = "fs_season_tickets"        # turn start: the back gains N
STAR_BILLING = "fs_star_billing"            # a Guest Star joins: draw N
ECHOING_HALL = "fs_echoing_hall"            # the fade's loss goes to the front
ETERNAL_APPLAUSE = "fs_eternal_applause"    # the fade starts above 10
TIDE_OF_APPLAUSE = "fs_tide_of_applause"    # a reaction: the back gains N
REGINA = "fs_regina_of_all_waters"          # turn start: Hydro on ALL
SOLILOQUY = "fs_soliloquy"                  # empty stage: Attacks +N a hit
ONE_WOMAN_SHOW = "fs_one_woman_show"        # empty stage at turn start: +E, +1


# ----------------------------------------------------------------------
# THE STARTER SEAM (`EB-723`). `{shipped id: prototype id}`, read by
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
# THE POOL SEAM (`EB-723`). `{shipped id: prototype id}`, read by
# `loader._pool_substitutions` under `FURINA_STAGE` and nowhere else. Fourteen
# rows -- the brief's sec.12 batch one minus the three starters above -- and
# R276's batch two, fifteen more, each
# swapped at the same rarity (`rewards.character_pool` refuses a substitution
# that would change a card's tier). The GAME's offer is not this one-for-one
# swap any more: `EB-736`'s text filter
# (`FurinaStageRoster.DropRetiredRows`) drops every shipped row printing a
# retired word first, which this sim does not model, so the live pool is far
# smaller than the sim's.
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
    # --- R276 BATCH TWO. Each replaced row is one the game's EB-736 filter
    # already drops, at the same rarity, so the mod's appended rows and this
    # swap name the same fifteen. Commons (six). ---
    "breathless": "proto_fs_improvised_number",         # 1 Attack for 1 Attack
    "graceful_retreat": "proto_fs_between_acts",        # 1 Skill for 1 Skill
    "house_call": "proto_fs_ensemble_piece",            # 1 Attack for 1 Attack
    "lasting_impression": "proto_fs_hold_your_places",  # 1 Skill for 1 Skill
    "applause_line": "proto_fs_quick_cue",              # 0 Attack for 0 Attack
    "swelling_overture": "proto_fs_step_forward",       # 1 Skill -> a 0 Skill
    # --- Uncommons (seven) ---
    "dress_rehearsal": "proto_fs_gala_dinner",          # 1 Skill for 1 Skill
    "matinee_performance": "proto_fs_double_casting",   # 1 Skill for 1 Skill
    "full_ensemble": "proto_fs_tutti",                  # 2 Skill -> a 1 Skill
    "dramatic_entrance": "proto_fs_bravura",            # 1 Attack for 1 Attack
    "fortissimo_guard": "proto_fs_full_house",          # 2 Power for 2 Power
    "standing_ovation": "proto_fs_thunderous_applause", # 1 Power for 1 Power
    "crowd_work": "proto_fs_rapt_audience",             # 1 Power for 1 Power
    # --- Rares (two) ---
    "endless_waltz": "proto_fs_arkhe_alignment",        # 2 Power for 2 Power
    "prima_donna": "proto_fs_five_century_act",         # 2 Power for 2 Power
    # --- THE GUEST CAST (2026-09-25): eight Guest Star Skills, each for a
    # same-rarity shipped Skill the game's EB-736 filter already drops.
    # Rares (three). ---
    "reginas_mercy": "proto_fs_guest_star_neuvillette",       # Skill, Skill
    "thunderous_ovation": "proto_fs_guest_star_clorinde",     # Skill, Skill
    "encore_performance": "proto_fs_guest_star_navia",        # Skill, Skill
    # --- Uncommons (five) ---
    "audience_participation": "proto_fs_guest_star_chevreuse",
    "deep_breath": "proto_fs_guest_star_wriothesley",
    "standing_room_only": "proto_fs_guest_star_sigewinne",
    "limelight": "proto_fs_guest_star_charlotte",
    "take_it_from_the_top": "proto_fs_guest_star_lynette",
    # --- THE SUPPORTING POOL (2026-09-26, review/active/furina-supporting-
    # pool-2026-09-26.md): 28 of its 29 (Sold Out is built beside it). Each
    # replaces a same-rarity shipped row the game's EB-736 filter already
    # drops. Commons (five; the sixth, Solo Verse, is `POOL_ADDS`'s). ---
    "shared_billing": "proto_fs_plot_twist",
    "ebb_and_flow": "proto_fs_stage_whisper",
    "dinner_service": "proto_fs_cheered_on",
    "macaron_break": "proto_fs_spirited_aria",
    "casting_call": "proto_fs_bubble_aria",
    # --- Uncommons (thirteen) ---
    "grand_salon": "proto_fs_revolving_stage",
    "curtain_cue": "proto_fs_oratrices_verdict",
    "top_billing": "proto_fs_season_tickets",
    "supporting_cast": "proto_fs_star_billing",
    "directors_cut": "proto_fs_held_applause",
    "pit_orchestra": "proto_fs_echoing_hall",
    "tempo_change": "proto_fs_intermission",
    "poised_riposte": "proto_fs_counterclaim",
    "florid_cadenza": "proto_fs_da_capo",
    "waters_embrace": "proto_fs_groundswell",
    "leading_role": "proto_fs_tide_of_applause",
    "hearts_swelling": "proto_fs_soliloquy",
    "curtain_up": "proto_fs_dual_nature",
    # --- Rares (nine) ---
    "rain_of_roses": "proto_fs_guest_star_lyney",
    "the_final_verdict": "proto_fs_guest_star_escoffier",
    "rapturous_applause": "proto_fs_eternal_applause",
    "showstopper": "proto_fs_bring_the_house_down",
    "flood_of_emotion": "proto_fs_grand_finale",
    "grand_gala": "proto_fs_gala_premiere",
    "high_tide": "proto_fs_grand_deluge",
    "the_sea_is_my_stage": "proto_fs_regina_of_all_waters",
    "star_of_the_show": "proto_fs_one_woman_show",
    # --- THE SUPPORTING POOL (2026-09-26): Sold Out, a Rare Power, for a
    # same-rarity shipped Power the EB-736 filter drops. ---
    "unheard_confession": "proto_fs_sold_out",          # 2 Power for 2 Power
}


# ----------------------------------------------------------------------
# THE POOL'S ADDITIONS (2026-09-26). Rows the arm OFFERS WITHOUT REPLACING a
# shipped row, read by `loader.pool_additions` under `FURINA_STAGE` and
# nowhere else. The supporting pool has six Commons and her sheet has only
# five Commons the EB-736 filter drops that no earlier batch replaced, so the
# sixth is appended at its own rarity rather than displacing a shipped Common
# the arm still offers. The mod's offer is an append anyway
# (`FurinaStageRoster.SwapOfferedRows`), so this is the sim catching up with
# it, not a new rule.
# ----------------------------------------------------------------------
POOL_ADDS: tuple[str, ...] = (
    "proto_fs_solo_verse",
)


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


def capacity(player) -> int:
    """How many seats her stage has: `SEATS`, or `SOLD_OUT_SEATS` with *Sold
    Out* on her (the supporting pool, 2026-09-26), for the rest of the combat
    however many copies. Every rule that meets a full stage asks this -- the
    summon's recast, Wriothesley's front-join, the returns and Full House --
    so a full stage is four under the power. C# twin:
    `FurinaStage.CapacityOf` / `FurinaStageLedger.Capacity`."""
    if active(player) and (getattr(player, "powers", None) or {}).get(SOLD_OUT, 0):
        return SOLD_OUT_SEATS
    return SEATS


def _seats(player) -> list:
    """The mutable list, created on first use. Only writers call this."""
    if not hasattr(player, "stage") or player.stage is None:
        player.stage = []
    return player.stage


# ----------------------------------------------------------------------
# THE FANFARE LEDGER. INSTRUMENT ONLY, the fence `state.spark_ledger` carries
# one arm over: nothing reads it back to decide anything, and it is not on the
# event stream, so no log digest moves. Every writer below that moves a bar
# books the move HERE, at the source, so the report never has to reconstruct
# the economy by diffing bars:
#
#     start + gained - spent - paid_other - left - faded - hit == end
#
# where `end` is `total_fanfare` whenever it is read. `gained` is split by the
# door it came through (`GAIN_*`). `left` is Fanfare that walks off the stage
# with its performer -- Final Bow's bar, which becomes Block and is not a
# Spend. Rotation carries a bar from one performer to another and books
# nothing. `back_at_turn_end` is the back performer's bar at the end of each
# of Furina's turns, after the fade (0 on an empty stage).
# ----------------------------------------------------------------------
GAIN_OPENING = "opening"        # the relic's Usher at 3
GAIN_REGEN = "regen"            # rule 4, the lead's 1
GAIN_CARD = "card"              # a card's Raise (and a named summon's bump)
GAIN_BOW = "bow"                # what a Bow sets off (Thunderous Applause)
GAIN_POWER = "power"            # Rapt Audience, Arkhe Alignment's Pneuma
GAIN_SUMMON = "summon"          # rule 3, a newcomer at 1
GAIN_EMPTY_SUMMON = "empty_summon"   # a Raise onto an empty stage, at the amount
GAIN_RETURN = "return"          # A Five-Century Act, the Rare's return at 1
GAIN_GUEST = "guest"            # a Guest Star's arrival (or its repeat's add)
GAIN_GIFT = "gift"              # Sigewinne's and Charlotte's gifts
GAIN_SOURCES = (GAIN_OPENING, GAIN_REGEN, GAIN_CARD, GAIN_BOW, GAIN_POWER,
                GAIN_SUMMON, GAIN_EMPTY_SUMMON, GAIN_RETURN, GAIN_GUEST,
                GAIN_GIFT)

#: The losses that are not a payment.
LOSS_FADED = "faded"
LOSS_HIT = "hit"
LOSS_LEFT = "left"

#: WHO PAID. `PAYER_SPEND` is a Spend card (a Spend mode, Bravura, the Rare);
#: any other payer -- the guests, when they land -- books under its own name
#: in `paid_other` through `book_paid`, which is the one hook they need.
PAYER_SPEND = "spend"


def ledger(state) -> dict:
    """This fight's ledger, created on first use with `start` = the Fanfare on
    stage at that moment. `open_combat` touches it before the relic fields
    anybody, so on a real fight `start` is what the stage held at combat start
    (0 on a fresh fight)."""
    led = getattr(state, "stage_ledger", None)
    if led is None:
        led = {}
        state.stage_ledger = led
    if not led:
        led.update(start=total_fanfare(state.player),
                   gained={s: 0 for s in GAIN_SOURCES},
                   spent=0, paid_other={}, left=0, faded=0, hit=0,
                   back_at_turn_end=[],
                   # THE GUEST CAST's measures (2026-09-25): per guest, acts
                   # that could not pay and turns on stage (at turn close).
                   unpaid={}, guest_turns={})
    return led


def book_gain(state, source: str, amount: int) -> None:
    """Fanfare that came onto a bar. Call BEFORE the bar moves, so a ledger
    first opened here reads the stage it found."""
    if amount <= 0 or not active(state.player):
        return
    if source not in GAIN_SOURCES:
        raise ValueError(f"unknown Fanfare source {source!r}")
    ledger(state)["gained"][source] += int(amount)


def book_loss(state, kind: str, amount: int) -> None:
    """Fanfare that left a bar other than by a payment. Call BEFORE the bar
    moves."""
    if amount <= 0 or not active(state.player):
        return
    if kind not in (LOSS_FADED, LOSS_HIT, LOSS_LEFT):
        raise ValueError(f"unknown Fanfare loss {kind!r}")
    ledger(state)[kind] += int(amount)


def book_paid(state, amount: int, payer: str = PAYER_SPEND) -> None:
    """Fanfare a PAYMENT took. A Spend card books under `spent`; any other
    payer (the guests, later) under `paid_other[payer]`. Call BEFORE the bar
    moves."""
    if amount <= 0 or not active(state.player):
        return
    led = ledger(state)
    if payer == PAYER_SPEND:
        led["spent"] += int(amount)
    else:
        led["paid_other"][payer] = led["paid_other"].get(payer, 0) + int(amount)


def ledger_expected_end(led: dict) -> int:
    """What the ledger says the stage should hold now."""
    return (led["start"] + sum(led["gained"].values()) - led["spent"]
            - sum(led["paid_other"].values()) - led["left"] - led["faded"]
            - led["hit"])


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
    ledger(state)               # `start` is the stage as combat found it
    seats = _seats(state.player)
    if seats:
        return
    book_gain(state, GAIN_OPENING, OPENING_FANFARE)
    seats.append([OPENING_MEMBER, OPENING_FANFARE])
    state.emit("stage_open", member=OPENING_MEMBER, fanfare=OPENING_FANFARE)


def summon(state, member: str, fanfare: int = SUMMON_FANFARE) -> None:
    """Rule 3. A summon fills the BACK-MOST EMPTY seat with that performer at
    1. On a FULL stage it rotates the cast: the front performer leaves without
    a bow, the other two step forward, and the newcomer takes the back seat
    WITH THE LEAVER'S FANFARE -- "pools are never lost to rotation".

    AND THE NEWCOMER DOES NOT ACT ON ARRIVAL (`EB-738`, round one's one E
    default, packet sec.5). Rule 3 reads "a newcomer performs with the others
    at the end of that turn, never on arrival", and this engine had read the
    draft's older wording as an act on play: three seats watched every summon
    deal damage and apply Hydro with nothing on its face, and a summon turn
    performed twice.

    THERE IS NO CODE FOR THE RULE AND THAT ABSENCE IS THE RULE.
    `end_of_turn_acts` walks whoever is on stage when it fires (rule 10), so a
    performer summoned during the turn is standing there when the sweep runs
    and performs exactly once. Stated here because "the rule needs no code" and
    "the rule was dropped" look identical in a diff.
    """
    p = state.player
    if not active(p):
        return
    if member not in PERFORMERS:
        # A typo in a row must not degrade quietly into "somebody": the deploy
        # verb one arm over refuses an unknown member and so does this one.
        raise ValueError(f"unknown performer {member!r}")
    seats = _seats(p)
    if len(seats) < capacity(p):
        # `fanfare` is the arrival: rule 3's 1, or a face's own number (THE
        # SUPPORTING POOL's Gala Premiere summons the trio at 3 each).
        book_gain(state, GAIN_SUMMON, int(fanfare))
        seats.append([member, int(fanfare)])
        state.emit("stage_summon", member=member, fanfare=int(fanfare),
                   seats=len(seats), rotated=False)
    else:
        leaver, carried = seats.pop(0)
        seats.append([member, carried])
        state.emit("stage_rotate_out", member=leaver, fanfare=carried,
                   arriving=member)
        state.emit("stage_summon", member=member, fanfare=carried,
                   seats=len(seats), rotated=True)


def recast_front(state, newcomer: str | None = None,
                 arrival: int = SUMMON_FANFARE) -> None:
    """A SUMMON ON A FULL STAGE (2026-09-25) -- `FurinaStage.
    RecastFromFront`'s twin. [USER]: "treat this like a Defect orb summon? the
    stage members rotate, ... bows, and their remaining fanfare transfers to
    the newest member", and the seat that leaves is the LEAD.

    The lead takes a Bow and leaves and the other two step forward; the Bow is
    a real one (its departure effect, then every Bow reader -- Thunderous
    Applause draws and Raises), but A Five-Century Act does NOT return it,
    because the summon is filling the seat it would return to. Then the
    newcomer enters the back seat holding the lead's remaining Fanfare. The
    newcomer is `newcomer` for a named summon, and for a random one a uniform
    roll over the trio (2026-09-25: the trio can be cloned), which may be the
    performer who just bowed.

    THE ORDER IS BOW, READERS, ARRIVAL: the applause's Raise lands on the
    stage of two the bow left. The arrival does not act on arrival
    (`EB-738`); it acts once at the end of the turn with everyone else.
    """
    p = state.player
    if not active(p):
        return
    seats = _seats(p)
    if len(seats) < capacity(p):
        return
    member = newcomer or state.rng.choice(PERFORMERS)
    pair = seats.pop(0)
    leaver, kept = pair
    _unrest(p, pair)
    exit_ = _exit(p, leaver, 0, held=kept)
    state.emit("stage_leave", member=leaver, bowed=True, reason="recast",
               fanfare=kept)
    _bow(state, leaver, exit_)
    _after_bow(state, leaver, may_return=False)
    if len(seats) >= capacity(p):
        # No seat to come back to: the bar walks off with the performer.
        # The ledger booked nothing when it left the front, so it books the
        # loss here, where the bar is finally gone.
        book_loss(state, LOSS_LEFT, kept)
        return
    # THE RECAST ADDS (2026-09-25): the newcomer's own arrival Fanfare (1
    # for the trio, a Guest Star's N) on top of what the leaver left with.
    book_gain(state, GAIN_GUEST if member in GUESTS else GAIN_SUMMON,
              int(arrival))
    seats.append([member, kept + int(arrival)])
    state.emit("stage_summon", member=member, fanfare=kept + int(arrival),
               seats=len(seats), rotated=True, via="recast")


def recast_back(state, newcomer: str, arrival: int) -> None:
    """A FRONT-SEAT GUEST ON A FULL STAGE (the guest seat round, 2026-09-25)
    -- `FurinaStage.RecastFromBack`'s twin. `recast_front` with the leaver at
    the other end: the BACK performer Bows (a real Bow, its readers too, but
    no Five-Century return) and leaves, and the newcomer arrives at the FRONT
    holding `arrival` plus the leaver's remaining Fanfare. Bow, readers,
    arrival. It does not act on arrival (`EB-738`)."""
    p = state.player
    if not active(p):
        return
    seats = _seats(p)
    if len(seats) < capacity(p):
        return
    index = len(seats) - 1
    pair = seats.pop(index)
    leaver, kept = pair
    _unrest(p, pair)
    exit_ = _exit(p, leaver, index, held=kept)
    state.emit("stage_leave", member=leaver, bowed=True, reason="recast",
               fanfare=kept)
    _bow(state, leaver, exit_)
    _after_bow(state, leaver, may_return=False)
    if len(seats) >= capacity(p):
        book_loss(state, LOSS_LEFT, kept)
        return
    book_gain(state, GAIN_GUEST if newcomer in GUESTS else GAIN_SUMMON,
              int(arrival))
    seats.insert(0, [newcomer, kept + int(arrival)])
    state.emit("stage_summon", member=newcomer, fanfare=kept + int(arrival),
               seats=len(seats), rotated=True, via="recast", seat="front")


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


def _leave(state, index: int, *, bowed: bool, reason: str,
           pay_now: bool = True, owed: list | None = None) -> dict:
    """A performer leaves the stage. ONE implementation, every caller (a hit
    that empties the bar, a Spend that does, Final Bow, a guest's payment),
    so "a performer at 0 Fanfare bows" (rule 7, 2026-09-25) cannot drift
    between them.

    `pay_now=False` is the hit's: the bow is owed, and `settle_hit` pays it
    once the hit has been dealt -- `FurinaStage.Flush`'s twin. `owed` is a
    guest act's: the Bow is appended there and paid after the act's effect
    (rule 4). Returns the exit, which is what the Bow reads (`_exit`)."""
    p = state.player
    seats = _seats(p)
    book_loss(state, LOSS_LEFT, seats[index][1])   # Final Bow's bar; else 0
    pair = seats.pop(index)
    member, remaining = pair
    _unrest(p, pair)
    exit_ = _exit(p, member, index, held=0)
    state.emit("stage_leave", member=member, bowed=bowed, reason=reason,
               fanfare=remaining)
    if bowed and owed is not None:
        owed.append(exit_)
    elif bowed and not pay_now:
        pending = list(getattr(state, _HIT_BOWS, []) or [])
        pending.append(exit_)
        setattr(state, _HIT_BOWS, pending)
    elif bowed:
        _bow(state, member, exit_)
        _after_bow(state, member, may_return=True)
    return exit_


def _exit(player, member: str, index: int, held: int,
          stayer=None) -> dict:
    """What a Bow reads, taken as the performer leaves (the Guest Cast,
    2026-09-25): the Fanfare it still HELD (Navia; 0 at 0 Fanfare and for a
    cash-out), the seat it stood in (Sigewinne gives to the one behind), and
    what it LOST since its last act (Wriothesley, the hit that took him down
    included). A guest's loss count leaves the stage with it. C# twin:
    `StageExit`."""
    if stayer is not None:
        # THE SUPPORTING POOL's Grand Finale (2026-09-26): a Bow WITHOUT
        # LEAVING. The performer keeps its seat, so its loss count stays with
        # it (the Bow resets it, as every act does) and the Bow reads the seat
        # it still stands in (`stayer`, the live pair).
        lost = int(player.stage_lost.get(member, 0)) if member in GUESTS else 0
    else:
        lost = (int(player.stage_lost.pop(member, 0)) if member in GUESTS
                else 0)
    return {"member": member, "held": int(held), "former": int(index),
            "lost": lost, "stayer": stayer}


def _lose(player, member: str, amount: int) -> None:
    """An enemy's HIT took Fanfare: count it for Wriothesley's reading
    (rule 6). HITS ONLY (2026-09-25: "he is the tank, not a Spend engine"):
    Spends, payments, taxes, gifts, cash-outs and the fade do not count.
    Guests only -- one of each, so the name is the seat. C# twin:
    `FurinaStageLedger.Absorb`."""
    if amount > 0 and member in GUESTS:
        player.stage_lost[member] = int(player.stage_lost.get(member, 0)) + int(amount)


#: The bows hits have emptied performers into, waiting for `settle_hit`. On
#: the STATE, as `_PENDING` is: one hit's two halves, and nothing else reads it.
_HIT_BOWS = "_stage_hit_bows"


def settle_hit(state) -> None:
    """RULE 7 (2026-09-25; [USER]: "Stage members bow out when they are
    destroyed or replaced, not just when you deliberately spend them down to
    0"): a performer a hit emptied takes its Bow AFTER that hit is dealt --
    `FurinaStage.Flush`'s twin, which the mod runs at `AfterDamageReceived`,
    once per hit and before the next hit of the same attack. So Usher's
    Fanfare never softens the hit that emptied him, and the performer it lands
    on does meet the next one.

    NO BOW when that hit killed Furina or ended the combat; what is owed is
    dropped, never kept for a later hit."""
    owed = list(getattr(state, _HIT_BOWS, []) or [])
    if not owed:
        return
    setattr(state, _HIT_BOWS, [])
    p = state.player
    for exit_ in owed:
        if not active(p) or not p.alive or not state.living_enemies:
            return
        _bow(state, exit_["member"], exit_)
        _after_bow(state, exit_["member"], may_return=True)


def is_resting(player, pair) -> bool:
    """Is THIS seat resting? BY IDENTITY and not by name, since the trio can
    be cloned (2026-09-25): two Ushers are two seats, and A Five-Century
    Act's returnee is only one of them. C# twin: `StageSeat.Resting`."""
    return any(r is pair for r in player.stage_resting)


def _unrest(player, pair) -> None:
    """A seat leaving the stage stops resting."""
    player.stage_resting[:] = [r for r in player.stage_resting
                               if r is not pair]


def _after_bow(state, member: str, *, may_return: bool) -> None:
    """R276 batch two: what a Bow sets off once the performer has left and
    its departure effect has resolved -- `FurinaStage.AfterBow`'s twin.
    Thunderous Applause (each copy draws 1 and Raises its share on the back
    performer -- round four: on an empty stage that Raise summons a random
    performer holding it), then A Five-Century Act (the performer returns to the back
    seat at 1 and rests through this turn's acts; once, and never from Let
    the People Rejoice, whose own return is the return)."""
    p = state.player
    copies = int(p.stage_power_copies.get(THUNDEROUS_APPLAUSE, 0))
    raise_total = int(p.powers.get(THUNDEROUS_APPLAUSE, 0))
    if copies > 0:
        state.draw(copies)
        raise_fanfare(state, raise_total, source=GAIN_BOW)
    if (may_return and p.powers.get(FIVE_CENTURY_ACT, 0)
            and len(_seats(p)) < capacity(p)):
        book_gain(state, GAIN_RETURN, SUMMON_FANFARE)
        pair = [member, SUMMON_FANFARE]
        _seats(p).append(pair)
        p.stage_resting.append(pair)
        state.emit("stage_return", member=member, fanfare=SUMMON_FANFARE)


def _bow(state, member: str, exit_: dict | None = None) -> None:
    """Rule 9, the curtain call: THE PERFORMER'S OWN ACT, ONE MORE TIME, as it
    leaves (draft 3, 2026-09-25; [USER] ruled the Stage review's pick 1, one
    effect per performer, since Chevalmarin's old Bow was "strictly worse than
    the end-of-turn effect"). Usher 3 Block, Chevalmarin 2 to every enemy,
    Crabaletta 5 to a random enemy -- `perform` itself, so the two cannot
    drift.

    ONE ACT: Arkhe Alignment's Ousia and Pneuma double it like any act (the
    multipliers `perform` reads), and Full House does NOT repeat it (only the
    end-of-turn sweep loops). A hit's Bow lands on the enemy's turn, after the
    sweep has reset the multipliers, so there it is the printed act. A
    Five-Century Act's return comes after it (`_after_bow`). C# twin:
    `FurinaStage.Bow`.
    """
    state.emit("stage_bow", member=member)
    # THE SUPPORTING POOL's Da Capo (2026-09-26): every Bow this combat, all
    # causes, the Grand Finale's included.
    state.player.stage_bows = int(state.player.stage_bows) + 1
    perform(state, member, bow=True, exit_=exit_)


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
    book_gain(state, GAIN_REGEN, LEAD_REGEN)
    pair[1] += LEAD_REGEN
    state.emit("stage_regen", member=pair[0], amount=LEAD_REGEN,
               fanfare=pair[1])


def raise_fanfare(state, amount: int, seat: str = SEAT_BACK, *,
                  summon_on_empty: bool = True,
                  source: str = GAIN_CARD) -> int:
    """Rule 5. "Raise N Fanfare on the back performer" lands on the BACK-MOST
    performer, which is the lead when it is alone. `seat=SEAT_LEAD` is the
    other spelling, for a face that names the lead instead.

    ROUND FOUR: RAISE ON AN EMPTY STAGE SUMMONS. With nobody on stage a random
    performer arrives HOLDING THE RAISE AMOUNT (not rule 3's 1) and nothing
    else is raised -- for every seat a face names, and for the Raise powers.
    Gala Dinner on an empty stage fields ONE performer at 3. The arrival
    performs at the end of the turn with the others (rule 3, `EB-738`). C#
    twin: `FurinaStage.SummonForRaise`.

    `summon_on_empty=False` is Arkhe Alignment's Pneuma, which prints "the
    lead REGAINS" -- a regain like rule 4's, with no lead to regain on an
    empty stage (C# twin: `FurinaStage.RegainLead`).

    Returns what landed -- 0 on an empty stage that does not summon, which the
    caller emits rather than swallowing, for the reason `rotate` gives above.

    `source` is the ledger's door (`GAIN_*`): a card's Raise by default, a
    Bow's or a power's where those call. An empty-stage summon books as
    `GAIN_EMPTY_SUMMON` whoever raised.
    """
    p = state.player
    if not active(p) or amount <= 0:
        return 0
    if summon_on_empty and not stage(p):
        member = state.rng.choice(PERFORMERS)
        book_gain(state, GAIN_EMPTY_SUMMON, int(amount))
        _seats(p).append([member, int(amount)])
        state.emit("stage_summon", member=member, fanfare=int(amount),
                   seats=1, rotated=False, via="raise")
        return int(amount)
    if seat == SEAT_ALL:
        seats = stage(p)
        if not seats:
            state.emit("stage_raise_whiffed", amount=amount, seat=seat)
            return 0
        for pair in seats:
            book_gain(state, source, int(amount))
            pair[1] += int(amount)
            state.emit("stage_raise", member=pair[0], amount=int(amount),
                       seat=seat, fanfare=pair[1])
        return int(amount) * len(seats)
    pair = lead(p) if seat == SEAT_LEAD else back(p)
    if pair is None:
        state.emit("stage_raise_whiffed", amount=amount, seat=seat)
        return 0
    book_gain(state, source, int(amount))
    pair[1] += int(amount)
    state.emit("stage_raise", member=pair[0], amount=int(amount), seat=seat,
               fanfare=pair[1])
    return int(amount)


def can_spend(player) -> bool:
    """Is anybody on stage? The `stage_occupied` predicate. A Spend MODE asks
    the stricter `can_pay` below (R276)."""
    return active(player) and bool(stage(player))


def can_pay(player, amount: int) -> bool:
    """R276 pick 1: can the BACK performer pay `amount` IN FULL? False on an
    empty stage and on a bar short of the price. C# twin:
    `FurinaStage.CanSpend`."""
    return can_spend(player) and back_fanfare(player) >= int(amount)


#: `EB-746`. THE HEAD OP OF A SPEND MODE, which is what makes a `choose_one`
#: mode the Spend one. Read the way `effects.MODE_PRICE_OPS` reads a priced
#: mode: the mode's body OPENS with the payment, the colon in "Spend 3: deal 13
#: instead" is that boundary, and everything after it is what the payment buys.
SPEND_MODE_OP = "stage_spend"


def spend_mode_amount(mode: dict):
    """`N` when this mode is a Spend mode, else None."""
    body = mode.get("effects") or []
    if not body:
        return None
    head = body[0]
    if head.get("op") != SPEND_MODE_OP:
        return None
    amount = head.get("amount", 1)
    return int(amount) if isinstance(amount, int) else None


def mode_offered(player, mode: dict) -> bool:
    """Rule 8's refusal, per MODE (`EB-746`, R276 pick 1).

    A Spend mode is offered only when the BACK performer can pay its whole
    price; on an empty stage or a short bar the card plays its base mode. C#
    twin: `FurinaStage.CanSpend` through the generated `ModeRequirements`.
    """
    amount = spend_mode_amount(mode)
    return amount is None or can_pay(player, amount)


def mode_refusal(player, mode: dict):
    """Why this mode is not offered, in the words `effects.mode_refusal` uses
    for a priced one: the rule, then the board."""
    if mode_offered(player, mode):
        return None
    label = mode.get("label") or "(unlabelled mode)"
    return f"{label!r} needs its full price from the back performer"


# ----------------------------------------------------------------------
# THE PILOT'S SPEND POLICY (`EB-746`).
# ----------------------------------------------------------------------
#
# WHY THE PILOT NEEDS ONE AT ALL. Spend was a rider the engine fired whenever a
# lead stood, so the sim never chose; four of six round-two seats said the card
# spent for them ("no verb to decline"), and the fix makes it a mode. A mode
# nobody chooses defaults to index 0 -- `effects._chosen_mode`'s tie-break --
# so without a policy the sim would model a Furina who never spends at all,
# which is a different character from the one the seats play.
#
# THE POLICY, IN ONE SENTENCE, and it is deliberately the simplest rule that
# reproduces the brief's own turn-one wager: SPEND WHEN THE PAYER SURVIVES THE
# PAYMENT, OR WHEN THE PAYMENT KILLS. The payer is the BACK performer since
# R276, and a mode it cannot pay in full is never offered. Written out:
#
#   * the back performer's bar stays above 0 after paying -- the performer keeps
#     standing, so the extra damage costs a number and not a body (brief
#     sec.7's line A against line B, where the whole wager is whether the
#     Usher survives the turn);
#   * or the mode's biggest hit is at least the smallest living enemy's HP --
#     the fight ends, and rule 4's "every point unspent when the last enemy
#     falls is gone" makes a bar kept past the last body worth nothing;
#   * otherwise KEEP, which is the Preserve read: a bar that would be emptied
#     for a number is a body traded for a number, and this policy does not
#     make that trade.
#
# WHAT IT IS NOT. It is not the Expend deck (brief sec.4), which spends a
# 1-bar body ON PURPOSE for the full rider and the bow, and it is not a
# measurement of which deck is better -- that is sec.13's question and the
# seats'. A pilot that always kept and a pilot that always spent are both
# worse models of a played run than this one, and the ROW that decides the
# over-sized Spend (`furina-stage-round-2` 5.1) is [USER]'s and still open, so
# the policy deliberately does not lean on the answer.
#
# INSIDE THE ARM, NOT IN `pilot/policy.py`, and it is `EB-118` 2C's boundary
# kept: `policy.choose_mode` is a shipped valuation behind its own
# POLICY_VERSION window, and a Stage rule that moved it would renumber every
# tier0.5 read taken with a modal card in the pool. This is quarantined
# machinery and returns None the moment the arm is off.
def spend_mode_index(state, modes: list):
    """Which mode this arm's pilot takes, or None where the rule does not
    reach -- the arm is off, no mode is a Spend, or the stage is empty."""
    if not active(state.player):
        return None
    spends = [(i, spend_mode_amount(mode)) for i, mode in enumerate(modes)]
    spends = [(i, n) for i, n in spends if n is not None]
    if len(spends) != 1:
        # Two Spend modes on one face is a shape no row on the surface has,
        # and picking between them is a rule nobody has written. Fall through
        # to the engine's own chooser rather than inventing one here.
        return None
    index, amount = spends[0]
    keep = next((i for i in range(len(modes)) if i != index), 0)
    if not can_pay(state.player, amount):
        return keep                       # rule 8's refusal, as a choice
    if back_fanfare(state.player) - amount > 0:
        return index
    return index if _mode_kills(state, modes[index]) else keep


def _mode_kills(state, mode: dict) -> bool:
    """Would this mode's biggest printed hit finish the smallest body standing?

    A FORECAST OFF PRINTED NUMBERS and not a simulation: the pilot is choosing
    before anything resolves, and what it can read is the face. Block, powers
    and reactions all move the real number, so this is a floor on "the fight
    can end here" rather than a promise that it does -- which is the honest
    shape for a tie-breaker whose other arm is "keep the body".
    """
    living = [e for e in state.living_enemies if getattr(e, "hp", 0) > 0]
    if not living:
        return False
    weakest = min(e.hp for e in living)
    biggest = 0
    for fx in mode.get("effects") or []:
        if fx.get("op") == "damage" and isinstance(fx.get("amount"), int):
            biggest = max(biggest, int(fx["amount"]))
    return biggest >= weakest


def spend(state, amount: int) -> int:
    """Rule 8 as R276 ruled it (picks 1 and 2). Pay N from the BACK
    performer's bar -- the bank -- and only IN FULL. A performer the payment
    empties EXACTLY leaves with a bow. A bar short of N pays nothing: the
    chooser never offers such a mode (`mode_offered`), so this is the engine's
    own refusal rather than a path a play takes.

    Returns what was paid: N, or 0 where it refused.
    """
    p = state.player
    if not active(p):
        return 0
    pair = back(p)
    if pair is None or pair[1] < int(amount):
        state.emit("stage_spend_whiffed", amount=amount)
        return 0
    member, bar = pair
    paid = int(amount)
    book_paid(state, paid)
    pair[1] = bar - paid
    state.emit("stage_spend", member=member, asked=int(amount), paid=paid,
               bar_at_spend=bar, fanfare=pair[1], turn=state.turn,
               enemies_alive=len(state.living_enemies))
    if pair[1] <= 0:
        _leave(state, len(_seats(p)) - 1, bowed=True, reason="spend")
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
    book_paid(state, total)
    exits = [_exit(p, member, i, held=0) for i, (member, _f) in
             enumerate(seats)]
    seats.clear()
    setattr(state, _PENDING, exits)
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
    exits = [e if isinstance(e, dict) else _exit(p, e, -1, held=0)
             for e in (getattr(state, _PENDING, []) or [])]
    setattr(state, _PENDING, [])
    if not exits:
        return
    company = [e["member"] for e in exits]
    for exit_ in exits:
        state.emit("stage_leave", member=exit_["member"], bowed=True,
                   reason="spend_all", fanfare=0)
        _bow(state, exit_["member"], exit_)
        _after_bow(state, exit_["member"], may_return=False)
    seats = _seats(p)
    for member in company:
        # To an EMPTY seat only. Since the trio can be cloned (2026-09-25) a
        # trio member returns even where a Thunderous Applause Raise summoned
        # another of its name onto the stage the card emptied; one of each
        # GUEST, so a guest already back does not return twice.
        # `FurinaStageLedger.ReturnCompany`'s twin.
        if len(seats) >= capacity(p):
            break
        if member in GUESTS and any(m == member for m, _f in seats):
            continue
        book_gain(state, GAIN_RETURN, SUMMON_FANFARE)
        seats.append([member, SUMMON_FANFARE])
    state.emit("stage_encore_return", company=[m for m, _f in seats],
               fanfare=SUMMON_FANFARE)


def final_bow(state) -> int:
    """*Final Bow* (sec.12, R276): "The back performer takes a Bow and leaves.
    Gain Block equal to its Fanfare."

    A BOW WITHOUT A SPEND, and the one card that grants one. Rule 9 says a bow
    is earned by Spend; this face pays for it with a card and an Exhaust
    instead, which is a printed exception rather than a hole in the rule.
    Returns the bar it left with, which is the Block the card gains.
    """
    p = state.player
    if not active(p):
        return 0
    pair = back(p)
    if pair is None:
        state.emit("stage_final_bow_whiffed")
        return 0
    bar = pair[1]
    # A CASH-OUT: the card is paid for the whole bar, so the Bow holds
    # nothing (`_leave` passes held=0).
    _leave(state, len(_seats(p)) - 1, bowed=True, reason="final_bow")
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

    A performer emptied HERE leaves now and BOWS AFTER THE HIT (rule 7,
    2026-09-25): the caller runs `settle_hit` once the hit is dealt.
    """
    p = state.player
    if not active(p) or incoming <= 0:
        return 0
    pair = lead(p)
    if pair is None:
        return 0
    member, bar = pair
    two_or_more = count(p) >= 2
    eaten = min(int(incoming), bar)
    if eaten > 0:
        # THE SUPPORTING POOL's Counterclaim (2026-09-26): an enemy's hit
        # reached the front performer's bar since the end of her last turn --
        # A Rapt Audience's notion of a hit. Cleared when her turn ends.
        p.stage_front_hit = True
    book_loss(state, LOSS_HIT, eaten)
    _lose(p, member, eaten)
    pair[1] = bar - eaten
    state.emit("stage_absorb", member=member, amount=eaten,
               incoming=int(incoming), fanfare=pair[1])
    caught = 0
    if pair[1] <= 0:
        exit_ = _leave(state, 0, bowed=True, reason="hit", pay_now=False)
        # 2026-09-25 night (the granted-guest seat round): "a performer
        # emptied by a hit Bows before the rest of that hit reaches you".
        # The Bow is still paid by `settle_hit`, but its Block (Usher's act)
        # meets the rest of THIS hit first, and the Bow then gives only what
        # is left of it. `FurinaStageLedger.Absorb`'s twin.
        caught = min(int(incoming) - eaten, bow_block(p, member))
        exit_["caught"] = caught
        if caught > 0:
            state.emit("stage_bow_caught", member=member, amount=caught)
    # R276 batch two, A RAPT AUDIENCE: a fixed Raise on the back performer
    # per hit that took Fanfare off the lead, copies adding (2026-09-26
    # balance review: 2, 3 upgraded; it was a share of what the lead lost) --
    # and nothing when the lead was also the back performer. Every caller
    # here is an enemy's hit.
    rapt = int(p.powers.get(RAPT_AUDIENCE, 0))
    if rapt and two_or_more and eaten > 0:
        raise_fanfare(state, rapt, source=GAIN_POWER)
    # What the lead ate. What its Bow Block caught of the rest waits for the
    # caller (`take_caught`), which takes it off the hit before her HP.
    setattr(state, _HIT_CAUGHT, caught)
    return eaten


#: What the last `absorb`'s emptied lead's Bow Block caught of the rest of
#: that hit, for the hit loop to take off before her HP. On the STATE, as
#: `_HIT_BOWS` is.
_HIT_CAUGHT = "_stage_hit_caught"


def take_caught(state) -> int:
    """What the Bow Block of a lead the last hit emptied caught of the rest
    of that hit (2026-09-25 night), taken once. `combat._enemy_action`
    subtracts it from the hit after `absorb` and before her HP."""
    caught = int(getattr(state, _HIT_CAUGHT, 0) or 0)
    setattr(state, _HIT_CAUGHT, 0)
    return caught


def bow_block(player, member: str) -> int:
    """The Block a performer's Bow gives her: Usher's act at this turn's
    Pneuma multiple, 0 for everyone else (no guest's act gives Block). C#
    twin: `FurinaStageLedger.BowBlock`."""
    if member != "usher":
        return 0
    return ACT_USHER_BLOCK * int(player.stage_act_block_mult)


# ----------------------------------------------------------------------
# The acts.
# ----------------------------------------------------------------------
def perform(state, member: str, *, bow: bool = False, pair=None,
            exit_: dict | None = None) -> None:
    """Rule 10: one performer's flat act, from any seat, reading no bar.

    ONE implementation for every caller -- the end-of-turn sweep, *Bis!*,
    *Tutti!* and, since draft 3 (2026-09-25), the Bow -- so an act cannot
    mean two things. A newcomer's arrival was once another,
    until `EB-738` removed it: a summon performs at the END of the turn,
    with the others, and reaches this function through the sweep.

    `EB-495` D3, REPAIRED HERE. This function called `deal_damage_to_enemy`
    with no `powered=` at all, so the signature's default `True` applied and
    Furina's Strength and Weak scaled a performance.

    `FurinaStage.Perform` passes `powered: false` (`FurinaStage.cs:463`,
    `:477`) and `.Bow` a third time (`:544`) -- the same refusal the Salon's
    `PerformMember` makes at `SalonPowers.cs:981`, and the one the sim's own
    Salon twin already made at `effects.salon_member_act`. THE BRIEF IS WITH
    THE GAME, so the sim was the one-sided defect and this is the model
    catching up rather than a rule moving: sec.3 rule 10 calls an act "a flat
    act that does not read its bar" and ends "scaling on Fanfare lives in
    payoff cards (sec.5.2), never in the performer", and the sentence the
    Stage inherited from the Salon is "a performance is not an Attack and not
    a hit" (`EB-588`).

    NO ACT CARRIES AN ELEMENT (draft 3, 2026-09-25). `EB-495` D4 had given
    Crabaletta's hit the game's Hydro; [USER] then ruled the Hydro off both
    damage acts ("removing the Hydro application from the end-of-turn effects
    on Chevalmarin and Crabaletta"), so both are plain damage in both engines
    (`element=None` here, `ElementalHit.DealUnelemented` in the mod): no aura
    set, none consumed, no reaction.
    """
    from tier0.engine import effects                  # late: avoids the cycle
    p = state.player
    if not active(p):
        return
    if member in GUESTS:
        # THE GUEST CAST (2026-09-25): every act pays, and a Bow is free. A
        # caller that names a guest and no seat means the one on stage (one
        # of each); one that is not on stage has nothing to act with.
        if not bow and pair is None:
            pair = next((s for s in stage(p) if s[0] == member), None)
            if pair is None:
                return
        _guest_act(state, member, pair=None if bow else pair, exit_=exit_)
        return
    if not bow:                       # a Bow files its own `stage_bow`
        state.emit("stage_act", member=member)
    # R276 batch two, ARKHE ALIGNMENT: this turn's doubling of the acts'
    # printed numbers.
    dmg = int(p.stage_act_damage_mult)
    blk = int(p.stage_act_block_mult)
    if member == "usher":
        # A hit's Bow whose Block the rest of that hit already spent
        # (`absorb`, 2026-09-25 night) gives only what is left of it.
        caught = int((exit_ or {}).get("caught", 0)) if bow else 0
        p.block += max(0, ACT_USHER_BLOCK * blk - caught)
    elif member == "chevalmarin":
        for enemy in list(state.living_enemies):
            effects.deal_damage_to_enemy(state, enemy,
                                         ACT_CHEVALMARIN_DAMAGE * dmg,
                                         element=None,
                                         powered=False,
                                         source=("furina_stage/bow" if bow
                                                 else "furina_stage/act"))
    elif member == "crabaletta":
        if state.living_enemies:
            enemy = _act_target(state, state.living_enemies)
            effects.deal_damage_to_enemy(state, enemy,
                                         ACT_CRABALETTA_DAMAGE * dmg,
                                         element=None,
                                         powered=False,
                                         source=("furina_stage/bow" if bow
                                                 else "furina_stage/act"))


def perform_lead(state, times: int = 1) -> None:
    """*Bis!* (sec.12): the lead performer acts `times` times now (twice since
    the 2026-09-26 balance review). Each act resolves in full before the next
    and a guest's act pays each time; a lead that left after an act (it paid
    its last Fanfare) does not act again, and the next performer does not
    inherit the repeat. C# twin: `FurinaStage.PerformLead`."""
    p = state.player
    if not active(p):
        return
    pair = lead(p)
    if pair is None or is_resting(p, pair):
        state.emit("stage_act_whiffed")
        return
    for _ in range(times):
        if state.over or not p.alive:
            break
        if not _holds(p, pair):
            break
        perform(state, pair[0], pair=pair)


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
    # THE SUPPORTING POOL's Counterclaim reads hits "since your last turn":
    # the window opens here, at the end of her turn.
    p.stage_front_hit = False
    pairs = list(stage(p))
    company = [m for m, _f in pairs]
    if company:
        # R276 batch two, FULL HOUSE: with every seat filled (three, or four
        # under Sold Out) each performer acts once more per copy.
        times = 1 + (int(p.powers.get(FULL_HOUSE, 0))
                     if len(company) >= capacity(p) else 0)
        state.emit("stage_acts", company=list(company), times=times)
        for pair in pairs:
            if is_resting(p, pair):
                continue        # A Five-Century Act: re-enters without acting
            for _ in range(times):
                if state.over or not p.alive or not state.living_enemies:
                    break
                # A guest that paid its last Fanfare, or was taxed out, has
                # left and Bowed; it does not act again (the Guest Cast).
                if not _holds(p, pair):
                    break
                perform(state, pair[0], pair=pair)
    p.stage_resting.clear()
    p.stage_act_damage_mult = 1
    p.stage_act_block_mult = 1
    # Oratrice's Verdict lasts "this turn": the sweep was its last use.
    p.stage_verdict = None
    fade(state)


def fade_loss(fanfare: int, threshold: int = FADE_THRESHOLD) -> int:
    """Rule 12's arithmetic: half of the Fanfare above `FADE_THRESHOLD`,
    rounded down. 5 -> 0, 6 -> 0, 7 -> 1, 9 -> 2, 15 -> 5, 25 -> 10. ONE
    function, so the threshold (and the halving) is tuned in one place. C#
    twin: `FurinaStageLaw.FadeLoss`. `threshold` is *Eternal Applause*'s
    (2026-09-26): with it in play the fade starts above 10."""
    return max(0, int(fanfare) - int(threshold)) // 2


def fade_threshold(player) -> int:
    """Rule 12's line this turn: 5, or 10 with *Eternal Applause* in play
    (any number of copies). C# twin: `FurinaStage.FadeThresholdFor`."""
    if player.powers.get(ETERNAL_APPLAUSE, 0):
        return ETERNAL_FADE_THRESHOLD
    return FADE_THRESHOLD


def fade(state) -> None:
    """RULE 12, THE APPLAUSE FADES (draft 3, 2026-09-25). At the end of
    Furina's turn, AFTER the acts, each performer behind the front (the middle
    and back seats) loses `fade_loss` of its bar. The front never fades, so a
    lone performer never does. The loss is half of what stands ABOVE the
    threshold, so it never takes a bar below the threshold, never empties a
    performer and never causes a Bow. [USER] ruled out a flat halving
    ("taking away half from the back means it's hard to build up fanfare").
    C# twin: `FurinaStageLedger.Fade`."""
    p = state.player
    if not active(p):
        return
    # THE SUPPORTING POOL (2026-09-26). *Held Applause*: no fade at the end
    # of this turn, taken once. *Eternal Applause*: the line is 10. *Echoing
    # Hall*: what the fade takes goes to the front performer (a move, so a
    # second copy moves nothing more).
    held = bool(p.stage_hold_fade)
    p.stage_hold_fade = False
    threshold = fade_threshold(p)
    echoed = 0
    for pair in ([] if held else stage(p)[1:]):
        loss = fade_loss(pair[1], threshold)
        if loss <= 0:
            continue
        before = pair[1]
        book_loss(state, LOSS_FADED, loss)
        pair[1] = before - loss
        echoed += loss
        state.emit("stage_fade", member=pair[0], amount=loss,
                   before=before, fanfare=pair[1])
    if echoed and p.powers.get(ECHOING_HALL, 0) and stage(p):
        front = stage(p)[0]
        book_gain(state, GAIN_POWER, echoed)
        front[1] += echoed
        state.emit("stage_raise", member=front[0], amount=echoed,
                   seat=SEAT_LEAD, fanfare=front[1], by="echoing_hall")
    # THE LEDGER'S SAMPLE (a): the back performer's bar at the end of her
    # turn, after the fade, and 0 on an empty stage -- a distribution that
    # omits its zeros is not a distribution.
    ledger(state)["back_at_turn_end"].append(back_fanfare(p))


# ----------------------------------------------------------------------
# R276 BATCH TWO's verbs.
# ----------------------------------------------------------------------
def step_forward(state) -> None:
    """*Step Forward*: the BACK performer moves to the front seat and the
    others shift back one -- Scene Change run the other way. With one
    performer nothing moves."""
    p = state.player
    if not active(p):
        return
    seats = _seats(p)
    if len(seats) < 2:
        state.emit("stage_step_forward_whiffed")
        return
    seats.insert(0, seats.pop())
    state.emit("stage_step_forward", company=[m for m, _f in seats])


def perform_all(state) -> None:
    """*Tutti!*: every performer performs its act now, front first."""
    p = state.player
    if not active(p):
        return
    for pair in list(stage(p)):
        if state.over or not p.alive or not state.living_enemies:
            break
        if is_resting(p, pair) or not _holds(p, pair):
            continue            # A Five-Century Act's returnee rests
        perform(state, pair[0], pair=pair)


def spend_all_of_back(state) -> int:
    """*Bravura*: spend ALL of the back performer's Fanfare. The bar is
    emptied exactly, so the performer bows. 0 on an empty stage."""
    p = state.player
    if not active(p):
        return 0
    pair = back(p)
    if pair is None:
        state.emit("stage_spend_whiffed", amount="all_of_back")
        return 0
    member, bar = pair
    book_paid(state, bar)
    pair[1] = 0
    state.emit("stage_spend", member=member, asked=bar, paid=bar,
               bar_at_spend=bar, fanfare=0, turn=state.turn,
               enemies_alive=len(state.living_enemies))
    _leave(state, len(_seats(p)) - 1, bowed=True, reason="spend")
    return bar


def note_power_applied(state, power: str) -> None:
    """How many copies of an instanced Stage power are in play. Thunderous
    Applause draws once PER COPY, and the `powers` map sums amounts, so the
    copy count lives beside it. (Arkhe Alignment applies 1 a copy, so its
    `powers` amount IS the copy count.)"""
    if power == THUNDEROUS_APPLAUSE:
        copies = state.player.stage_power_copies
        copies[power] = int(copies.get(power, 0)) + 1


def arkhe_choice(state) -> str:
    """The PILOT's Arkhe Alignment pick: Pneuma (act Block multiplied, the
    lead regains 2 a copy) when an enemy intends to attack, else Ousia (double act
    damage). The player's own choice in the game; a simple, stated policy
    here, in the arm and not in `pilot/policy.py`."""
    for enemy in state.living_enemies:
        intents = getattr(enemy, "intents", None) or []
        idx = getattr(enemy, "intent_index", 0) or 0
        if intents:
            nxt = intents[idx % len(intents)]
            if isinstance(nxt, dict) and nxt.get("kind") == "attack":
                return "pneuma"
    return "ousia"


def turn_start_powers(state) -> None:
    """R276 batch two's turn-start power: Arkhe Alignment. ONE choice a turn
    however many copies are in play; copies ADD, so the chosen half is
    x(1 + copies) and Pneuma's lead regains 2 a copy. C# twin:
    `ArkheAlignmentPower.Choose`."""
    p = state.player
    if not active(p):
        return
    # THE GUEST CAST (2026-09-25): Chevreuse's Energy, next turn (the mod's
    # `EnergyNextTurnPower`).
    if p.stage_energy_next:
        p.energy += int(p.stage_energy_next)
        state.emit("stage_energy", amount=int(p.stage_energy_next))
        p.stage_energy_next = 0
    supporting_pool_turn_start(state)
    copies = int(p.powers.get(ARKHE_ALIGNMENT, 0))
    if copies <= 0:
        return
    choice = arkhe_choice(state)
    if choice == "pneuma":
        p.stage_act_block_mult = 1 + copies
        # A REGAIN, not a Raise: no summon on an empty stage (round four).
        raise_fanfare(state, PNEUMA_LEAD_REGAIN * copies, SEAT_LEAD,
                      summon_on_empty=False, source=GAIN_POWER)
    else:
        p.stage_act_damage_mult = 1 + copies
    state.emit("stage_arkhe", choice=choice, copies=copies)


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
    # THE GUEST CAST's measure: turns each guest spent on stage.
    turns = ledger(state)["guest_turns"]
    for member, _f in stage(p):
        if member in GUESTS:
            turns[member] = int(turns.get(member, 0)) + 1


# ----------------------------------------------------------------------
# THE GUEST CAST (2026-09-25). C# twin: `FurinaStageGuests.cs` and
# `FurinaStageLedger.ActFanfare`.
# ----------------------------------------------------------------------
def _holds(player, pair) -> bool:
    """Is THIS seat still on the stage? By identity (two Ushers are two
    seats)."""
    return any(s is pair for s in stage(player))


def guest_star(state, member: str, amount: int, front: bool = False) -> None:
    """A GUEST STAR CARD: "<Name> joins the stage with N Fanfare."

      * already on stage (one of each; [USER]: "only one Neuvillette allowed -
        repeats trigger a Bow and then resummon them, carrying over unused
        Fanfare"): it steps out holding its bar, Bows (its act, free), with
        every Bow reader but no Five-Century return, and comes back to the
        same seat holding its unused Fanfare plus N;
      * a full stage (no guest cap: "why not just let the Stage be filled
        with guest stars if the player wants?"): the front Bows and leaves,
        and the guest arrives at the back holding the front's Fanfare, like
        any summon (`recast_front`);
      * otherwise the back-most empty seat, holding N.

    `front` (the guest seat round, 2026-09-25; Wriothesley's card): he joins
    in the FRONT seat and the others shift back one, and on a full stage the
    recast's leaver is the BACK performer (`recast_back`). A repeat copy is
    unchanged.

    It does not act on arrival (`EB-738`). C# twin: `FurinaStage.GuestStar`.

    THE SUPPORTING POOL's *Star Billing* (2026-09-26): "Whenever a Guest Star
    joins the stage, draw 2 cards" -- after the arrival, whichever way it
    arrived (a second copy's recast included).
    """
    p = state.player
    if not active(p):
        return
    if member not in GUESTS:
        raise ValueError(f"unknown guest {member!r}")
    _guest_joins(state, member, amount, front)
    billing = int(p.powers.get(STAR_BILLING, 0))
    if billing > 0 and not state.over:
        state.draw(billing)
        state.emit("stage_star_billing", member=member, drew=billing)


def _guest_joins(state, member: str, amount: int, front: bool) -> None:
    """`guest_star`'s arrival, whichever of its three ways."""
    p = state.player
    seats = _seats(p)
    for index, pair in enumerate(seats):
        if pair[0] != member:
            continue
        seats.pop(index)
        _unrest(p, pair)
        exit_ = _exit(p, member, index, held=pair[1])
        state.emit("stage_leave", member=member, bowed=True, reason="repeat",
                   fanfare=pair[1])
        _bow(state, member, exit_)
        _after_bow(state, member, may_return=False)
        if len(seats) < capacity(p):
            book_gain(state, GAIN_GUEST, int(amount))
            pair[1] += int(amount)
            seats.insert(min(index, len(seats)), pair)
            state.emit("stage_summon", member=member, fanfare=pair[1],
                       seats=len(seats), rotated=False, via="repeat")
        else:
            book_loss(state, LOSS_LEFT, pair[1])
        return
    if len(seats) >= capacity(p):
        if front:
            recast_back(state, member, int(amount))
        else:
            recast_front(state, member, int(amount))
        return
    book_gain(state, GAIN_GUEST, int(amount))
    if front:
        seats.insert(0, [member, int(amount)])
    else:
        seats.append([member, int(amount)])
    state.emit("stage_summon", member=member, fanfare=int(amount),
               seats=len(seats), rotated=False, via="guest",
               seat="front" if front else "back")


def _pay(state, pair, amount: int, actor: str, owed: list) -> None:
    """One payment off one bar, by `actor`'s act (rule 4). Booked under the
    actor in `paid_other` (the ledger's guest hook); a payer emptied leaves
    and its Bow joins `owed`, paid after the act's effect."""
    p = state.player
    if amount <= 0:
        return
    book_paid(state, amount, payer=actor)
    before = pair[1]
    pair[1] = before - amount
    state.emit("stage_pay", member=pair[0], by=actor, amount=int(amount),
               before=before, fanfare=pair[1])
    if pair[1] <= 0:
        index = next(i for i, s in enumerate(_seats(p)) if s is pair)
        _leave(state, index, bowed=True, reason="paid", owed=owed)


def _gain(state, pair, amount: int, actor: str) -> None:
    """A gift onto a bar (Sigewinne, Charlotte)."""
    if amount <= 0:
        return
    book_gain(state, GAIN_GIFT, amount)
    pair[1] += int(amount)
    state.emit("stage_raise", member=pair[0], amount=int(amount),
               seat="gift", fanfare=pair[1], by=actor)


def _unpaid(state, member: str) -> None:
    """An act that could not pay does nothing (rule 4), and is counted."""
    counts = ledger(state)["unpaid"]
    counts[member] = int(counts.get(member, 0)) + 1
    state.emit("stage_unpaid", member=member)


def guest_fanfare(state, member: str, pair, exit_, owed: list) -> bool:
    """A GUEST'S ACT, ITS FANFARE HALF: pay what the act costs and move the
    Fanfare it moves. False where it could not pay. A Bow (`pair` None) is
    free: no payment, and the gifts land in full. C# twin:
    `FurinaStageLedger.ActFanfare`."""
    p = state.player
    seats = _seats(p)
    bow = pair is None
    # THE SUPPORTING POOL's Grand Finale (2026-09-26): a Bow WITHOUT LEAVING
    # is free like any Bow, but the performer is still in its seat, so a gift
    # that goes to "each other performer" or "the one behind her" must not
    # find her. `self_` is that seat, or the acting one.
    self_ = pair if pair is not None else (exit_ or {}).get("stayer")
    if member in ("lyney", "escoffier"):
        # Lyney pays 2 and Escoffier 3, each of their own (Neuvillette's
        # shape); a Bow is free. Escoffier's gift is the Fanfare half of her
        # act, and lands in full on a Bow.
        price = (ACT_LYNEY_PRICE if member == "lyney"
                 else ACT_ESCOFFIER_PRICE)
        if not bow:
            if pair[1] < price:
                _unpaid(state, member)
                return False
            _pay(state, pair, price, member, owed)
        if member == "escoffier":
            for other in [s for s in _seats(p) if s is not self_]:
                _gain(state, other, ACT_ESCOFFIER_GIFT, member)
        return True
    if member == "neuvillette":
        if bow:
            return True
        if pair[1] < ACT_NEUVILLETTE_PRICE:
            _unpaid(state, member)
            return False
        _pay(state, pair, ACT_NEUVILLETTE_PRICE, member, owed)
        return True
    if member == "clorinde":
        if bow:
            return True
        others = [s for s in seats if s is not pair]
        if not others:
            _unpaid(state, member)
            return False
        for other in others:
            _pay(state, other, ACT_CLORINDE_TAX, member, owed)
        return True
    if member == "chevreuse":
        if bow:
            return True
        bank = seats[-1] if seats else None
        if bank is None or bank[1] < ACT_CHEVREUSE_PRICE:
            _unpaid(state, member)
            return False
        _pay(state, bank, ACT_CHEVREUSE_PRICE, member, owed)
        return True
    if member == "sigewinne":
        if bow and self_ is not None:
            # The Grand Finale's Bow in place: the gift goes where her act
            # would send it, free.
            at = next((i for i, s in enumerate(seats) if s is self_), -1)
            if at >= 0 and len(seats) > 1:
                to = seats[at + 1] if at + 1 < len(seats) else seats[0]
                _gain(state, to, ACT_SIGEWINNE_GIFT, member)
            return True
        if bow:
            index = (exit_ or {}).get("former", -1)
            if seats and index >= 0:
                heir = seats[index] if index < len(seats) else seats[0]
                _gain(state, heir, ACT_SIGEWINNE_GIFT, member)
            return True
        others = [s for s in seats if s is not pair]
        if not others:
            return True
        at = next(i for i, s in enumerate(seats) if s is pair)
        to = seats[at + 1] if at + 1 < len(seats) else seats[0]
        gift = min(ACT_SIGEWINNE_GIFT, pair[1])
        _pay(state, pair, gift, member, owed)
        _gain(state, to, gift, member)
        return True
    if member == "charlotte":
        for other in [s for s in seats if s is not self_]:
            _gain(state, other, ACT_CHARLOTTE_GIFT, member)
        return True
    return True


def _guest_act(state, member: str, *, pair, exit_) -> None:
    """A guest's act or Bow: its Fanfare half, then its effect on the board,
    then the Bows its payment earned. Ousia doubles the damage number and
    never the payment. C# twin: `FurinaStage.GuestAct`."""
    from tier0.engine import effects, reactions        # late: the cycle
    p = state.player
    owed: list = []
    if pair is not None:
        state.emit("stage_act", member=member)
    if not guest_fanfare(state, member, pair, exit_, owed):
        return
    dmg = int(p.stage_act_damage_mult)
    source = "furina_stage/bow" if pair is None else "furina_stage/act"
    element = GUEST_ELEMENTS.get(member)
    if member == "neuvillette":
        for enemy in list(state.living_enemies):
            effects.deal_damage_to_enemy(state, enemy,
                                         ACT_NEUVILLETTE_DAMAGE * dmg,
                                         element=element, powered=False,
                                         source=source)
    elif member == "escoffier":
        # THE SUPPORTING POOL (2026-09-26): her gift was the Fanfare half;
        # the board half is 3 Cryo damage to ALL enemies.
        for enemy in list(state.living_enemies):
            effects.deal_damage_to_enemy(state, enemy,
                                         ACT_ESCOFFIER_DAMAGE * dmg,
                                         element=element, powered=False,
                                         source=source)
    elif member in ("clorinde", "navia", "wriothesley", "lyney"):
        if member == "clorinde":
            amount = ACT_CLORINDE_DAMAGE
        elif member == "lyney":
            amount = ACT_LYNEY_DAMAGE
        elif member == "navia":
            amount = pair[1] if pair is not None else (exit_ or {}).get("held", 0)
        else:
            lost = (int(p.stage_lost.get(member, 0)) if pair is not None
                    else int((exit_ or {}).get("lost", 0)))
            amount = ACT_WRIOTHESLEY_RATE * lost
        if amount > 0 and state.living_enemies:
            enemy = _act_target(state, state.living_enemies)
            effects.deal_damage_to_enemy(state, enemy, amount * dmg,
                                         element=element, powered=False,
                                         source=source)
    elif member == "chevreuse":
        p.stage_energy_next = int(p.stage_energy_next) + ACT_CHEVREUSE_ENERGY
    elif member == "lynette":
        # 2026-09-25 night (the granted-guest seat round; both seats never
        # played her): "deal 3 Anemo damage to a random enemy, one with an
        # aura if any". Always lands; on an aura the Anemo damage Swirls
        # through the ordinary pipeline, on none it is plain damage.
        wearing = [e for e in state.living_enemies if e.aura]
        pool = wearing or list(state.living_enemies)
        if pool:
            effects.deal_damage_to_enemy(state, _act_target(state, pool),
                                         ACT_LYNETTE_DAMAGE * dmg,
                                         element=element, powered=False,
                                         source=source)
    if member == "lyney":
        # "... then swap your front and back performers" -- after the hit,
        # whichever seat he stands in (a Bow: on the stage he left).
        swap_ends(state)
    # Rule 6: every act resets the reading, so a repeat reads 0.
    if pair is not None:
        p.stage_lost[member] = 0
    for gone in owed:
        if state.over or not p.alive:
            break
        _bow(state, gone["member"], gone)
        _after_bow(state, gone["member"], may_return=True)


def forecast(state) -> dict:
    """RULE 7, THE FORECAST, sim side: the end of this turn on a COPY of the
    fight -- the acts, their payments and the fade -- and the enemies' posted
    attacks on it, given her Block after the acts. PURE: the real state is
    never touched (the copy carries its own rng). Returns each seat's bar now
    and after, the Block after the acts, what the front performers take and
    what reaches her. The mod prints the same (`FurinaStage.Forecast`).
    """
    import copy
    from tier0.engine import combat
    p = state.player
    if not active(p):
        return {}
    now = [[m, f] for m, f in stage(p)]
    ghost = copy.deepcopy(state)
    ghost.log = []
    enemy_hp = sum(max(0, e.hp) for e in ghost.enemies)
    end_of_turn_acts(ghost)
    # 2026-09-25 night: what the acts actually took off the enemies' HP --
    # the number the mod's forecast act lines add up to on a board with no
    # Block, Vulnerable or reaction on it.
    acts_dealt = enemy_hp - sum(max(0, e.hp) for e in ghost.enemies)
    after = [[m, f] for m, f in stage(ghost.player)]
    block = int(ghost.player.block)
    hp = int(ghost.player.hp)
    for enemy in list(ghost.living_enemies):
        if ghost.over or not ghost.player.alive:
            break
        combat._enemy_turn(ghost, enemy)
    front = sum(e.get("amount", 0) for e in ghost.log
                if e.get("event") == "stage_absorb")
    # Hit by hit, performer by performer, in the order they took them.
    takers: list = []
    for e in ghost.log:
        if e.get("event") != "stage_absorb" or not e.get("amount"):
            continue
        leaves = int(e.get("fanfare", 0)) <= 0
        if takers and takers[-1][0] == e["member"] and not takers[-1][2]:
            takers[-1] = [e["member"], takers[-1][1] + int(e["amount"]),
                          leaves]
        else:
            takers.append([e["member"], int(e["amount"]), leaves])
    return {"now": now, "after": after, "block_after_acts": block,
            "front_takes": int(front),
            "reaches_furina": max(0, hp - int(ghost.player.hp)),
            "acts_dealt": int(acts_dealt), "takers": takers}


# ----------------------------------------------------------------------
# THE SUPPORTING POOL (2026-09-26, review/active/furina-supporting-pool-
# 2026-09-26.md). C# twin: `FurinaStageSupporting.cs` and the ledger's
# moves. Every verb is inert with the flag off.
# ----------------------------------------------------------------------
def _act_target(state, pool):
    """Who an act that "hits a random enemy" hits: *Oratrice's Verdict*'s
    enemy while it stands (this turn), else a random one of `pool`. C#
    twin: `FurinaStage.ActTarget`."""
    verdict = getattr(state.player, "stage_verdict", None)
    if (verdict is not None and getattr(verdict, "alive", False)
            and verdict in state.living_enemies):
        return verdict
    return state.rng.choice(pool)


def swap_ends(state) -> None:
    """Lyney's act: the front and back performers change places. With one
    performer nothing moves. C# twin: `FurinaStageLedger.SwapEnds`."""
    p = state.player
    seats = _seats(p)
    if len(seats) < 2:
        return
    seats[0], seats[-1] = seats[-1], seats[0]
    state.emit("stage_reorder", company=[m for m, _f in seats], by="swap")


def reverse(state) -> None:
    """*Plot Twist*: "Reverse the order of your performers." Three
    performers: the front and back change places; two: they swap. A pure
    reorder -- nothing Bows, nothing is lost. C# twin:
    `FurinaStageLedger.Reverse`."""
    p = state.player
    if not active(p):
        return
    seats = _seats(p)
    if len(seats) < 2:
        state.emit("stage_reorder_whiffed")
        return
    seats.reverse()
    state.emit("stage_reorder", company=[m for m, _f in seats], by="reverse")


def whisper(state, amount: int) -> int:
    """*Stage Whisper*: "Move up to 3 of your back performer's Fanfare to your
    front performer. It keeps at least 1." min(amount, back - 1), so it never
    empties the back and never Bows it (a 0-cost Bow would loop with
    Thunderous Applause and A Five-Century Act). With one performer it does
    nothing. A move between bars books nothing. Returns what moved. C# twin:
    `FurinaStageLedger.Whisper`."""
    p = state.player
    if not active(p):
        return 0
    seats = _seats(p)
    if len(seats) < 2:
        state.emit("stage_whisper_whiffed")
        return 0
    back_pair, front = seats[-1], seats[0]
    moved = max(0, min(int(amount), int(back_pair[1]) - 1))
    if moved <= 0:
        state.emit("stage_whisper_whiffed")
        return 0
    back_pair[1] -= moved
    front[1] += moved
    state.emit("stage_whisper", member=back_pair[0], to=front[0],
               amount=moved, fanfare=back_pair[1], front=front[1])
    return moved


def hold_fade(state) -> None:
    """*Held Applause*: "At the end of this turn, your performers do not
    fade." A flag `fade` takes once."""
    p = state.player
    if not active(p):
        return
    p.stage_hold_fade = True
    state.emit("stage_hold_fade")


def intermission(state, every: int) -> int:
    """*Intermission*: "Your back performer Bows and leaves. Draw 1 card for
    every 3 Fanfare it had." A real Bow (its act, the Bow readers, A
    Five-Century Act's return) and a CASH-OUT like Final Bow's, so the Bow
    holds nothing; then draw floor(F / every), F its Fanfare before the Bow.
    Returns F. C# twin: `FurinaStage.Intermission`."""
    p = state.player
    if not active(p):
        return 0
    pair = back(p)
    if pair is None:
        state.emit("stage_intermission_whiffed")
        return 0
    bar = int(pair[1])
    _leave(state, len(_seats(p)) - 1, bowed=True, reason="intermission")
    cards = bar // max(1, int(every))
    if cards > 0 and not state.over:
        state.draw(cards)
    state.emit("stage_intermission", fanfare=bar, drew=cards)
    return bar


def spend_all_of_front(state) -> int:
    """*Bring the House Down*: spend ALL of the FRONT performer's Fanfare --
    the first card that cashes the shield. The emptied front Bows (rule 7).
    0 on an empty stage. C# twin: `FurinaStage.SpendAllOfFront`."""
    p = state.player
    if not active(p):
        return 0
    pair = lead(p)
    if pair is None:
        state.emit("stage_spend_whiffed", amount="all_of_front")
        return 0
    member, bar = pair
    book_paid(state, bar)
    pair[1] = 0
    state.emit("stage_spend", member=member, asked=bar, paid=bar,
               bar_at_spend=bar, fanfare=0, turn=state.turn,
               enemies_alive=len(state.living_enemies), seat=SEAT_LEAD)
    _leave(state, 0, bowed=True, reason="spend")
    return bar


def grand_finale(state) -> None:
    """*Grand Finale*: "All your performers Bow without leaving." Front
    first, each Bow a real one -- its act (free), then every Bow reader
    (Thunderous Applause) -- but the performer keeps its seat and its
    Fanfare, so A Five-Century Act has nobody to return. Every Bow counts
    for Da Capo, and resets the performer's loss count like any act. C#
    twin: `FurinaStage.GrandFinale`."""
    p = state.player
    if not active(p):
        return
    for pair in list(stage(p)):
        if state.over or not p.alive:
            break
        if not _holds(p, pair):
            continue
        index = next(i for i, s in enumerate(_seats(p)) if s is pair)
        exit_ = _exit(p, pair[0], index, held=pair[1], stayer=pair)
        _bow(state, pair[0], exit_)
        _after_bow(state, pair[0], may_return=False)
        if pair[0] in GUESTS:
            p.stage_lost[pair[0]] = 0


def set_verdict(state) -> None:
    """*Oratrice's Verdict*: "This turn, your performers' acts that hit a
    random enemy hit this enemy instead." The card's own target, until the
    end-of-turn sweep has passed (`end_of_turn_acts` clears it). C# twin:
    `FurinaStageLedger.VerdictTarget`."""
    p = state.player
    if not active(p):
        return
    p.stage_verdict = state.card_aim
    state.emit("stage_verdict",
               target=getattr(state.card_aim, "name", None))


def dual_nature(state) -> None:
    """*Dual Nature*: "Choose Ousia or Pneuma for this turn." Arkhe
    Alignment's choice, once, for this turn only: the chosen half's multiple
    becomes at least x2 (it does not stack on an Arkhe Alignment that chose
    the same half), and Pneuma's front performer regains 2. The pilot's pick
    is Arkhe Alignment's (`arkhe_choice`). C# twin:
    `ArkheAlignmentPower.ChooseForTurn`."""
    p = state.player
    if not active(p):
        return
    choice = arkhe_choice(state)
    if choice == "pneuma":
        p.stage_act_block_mult = max(int(p.stage_act_block_mult), 2)
        raise_fanfare(state, PNEUMA_LEAD_REGAIN, SEAT_LEAD,
                      summon_on_empty=False, source=GAIN_POWER)
    else:
        p.stage_act_damage_mult = max(int(p.stage_act_damage_mult), 2)
    state.emit("stage_dual_nature", choice=choice)


def note_reaction(state) -> None:
    """*Tide of Applause*: "Whenever you trigger an Elemental Reaction, your
    back performer gains 2 Fanfare." Called from `reactions._react`, the one
    site this engine counts a reaction (C# twin: `FurinaStage.OnReaction`,
    from `ReactionEffects.Resolve`). A Raise, so on an empty stage it
    summons (rule 5)."""
    p = state.player
    if not active(p):
        return
    n = int(p.powers.get(TIDE_OF_APPLAUSE, 0))
    if n > 0:
        raise_fanfare(state, n, source=GAIN_POWER)


def regina_hydro(state) -> None:
    """*Regina of All Waters*: "At the start of your turn, apply Hydro to ALL
    enemies." Through the ordinary aura pipeline, so reactions trigger as any
    application does. Copies apply once: a second Hydro changes nothing."""
    from tier0.engine import reactions                 # late: the cycle
    for enemy in list(state.living_enemies):
        reactions.resolve_hit(state, enemy, "hydro", 0,
                              "furina_stage/regina")


def supporting_pool_turn_start(state) -> None:
    """The supporting pool's turn-start powers, AFTER rule 4's regen (so the
    lead's 1 went to the performer that led last turn) and before Arkhe
    Alignment's choice. C# twin: `FurinaStage.TurnStartPowers`.

      1. *One-Woman Show* first, while the stage is as the turn found it: if
         no one is on stage, gain 1 Energy and draw 1 card, per copy. (Asked
         before Season Tickets, whose Raise on an empty stage summons.)
      2. *Revolving Stage*: the back performer moves to the front, once per
         copy.
      3. *Season Tickets*: the back performer gains N (summons on empty).
      4. *Regina of All Waters*: Hydro on ALL enemies.
    """
    p = state.player
    if not active(p):
        return
    show = int(p.powers.get(ONE_WOMAN_SHOW, 0))
    if show > 0 and not stage(p):
        p.energy += show
        state.draw(show)
        state.emit("stage_one_woman_show", energy=show, drew=show)
    for _ in range(int(p.powers.get(REVOLVING_STAGE, 0))):
        step_forward(state)
    tickets = int(p.powers.get(SEASON_TICKETS, 0))
    if tickets > 0:
        raise_fanfare(state, tickets, source=GAIN_POWER)
    if p.powers.get(REGINA, 0):
        regina_hydro(state)
