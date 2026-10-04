"""Furina, THE STAGE -- the re-founded rules (v2).

`review/active/furina-refounding-2026-10-03.md` is the design: sec.1's rules
as sec.8 amends them, sec.2's cast as sec.8 amends it, and sec.10's full
sheet, whose rows are `docs/prototype-surface.yaml`'s `proto_fs_*`.
`tier0/engine/furina_v2.py` is the sim slice the paper was proven on and stays
a separate arm; this module is Furina's arm (`character_id = "furina"`), every
row of her pool on the same rules. Its C# twin mirrors the constants below by
NAME (`tools/lint_constant_parity.py`).

THE RULES, in the paper's order:

1. Three seats (four under Sold Out). Performers have no bars, take no hits
   and cannot be emptied. At the end of Furina's turn they act FRONT TO BACK,
   over a snapshot of the stage. Combat opens with Usher on stage (Salon
   Solitaire, her starting relic).
2. The Salon trio (Usher 4 Block, Chevalmarin 2 to ALL, Crabaletta 5 to a
   random enemy; no element) carries the numbers; a Guest Star bends a rule
   while on stage and/or has a utility act. One of each guest: a second copy
   Bows it (free act + 1 Fanfare) and it keeps its seat.
3. The Bow: a leaving performer acts once more, FREE (a star does not pay),
   then gives 1 Fanfare, after its act. Grand Finale's and Let the People
   Rejoice's Bows give 1 each too and remove nobody.
4. Overflow: a summon onto a full stage Bows the front-most SALON member; a
   Salon summon onto an all-guest stage is a WALK-ON (its free Bow act + 1
   Fanfare, no seat); a guest summon onto an all-guest stage Bows the front
   guest. A summon takes the back-most free seat.
5. Fanfare is ONE number on Furina (`Player.stage_fanfare`): no cap, no fade,
   hits never touch it. Filled by gains, Charlotte, reactions and Bows;
   drained by a card's Spend and by the stars' payments. A star that cannot
   pay skips the act and stays; nothing is spent. A payment is NOT a Spend.
   The flow counts (gained / spent this turn) reset at the START of her turn.
6. Rehearsal (the `fs_rehearsal` Power's stacks): +1 per stack to every
   performer's damage and Block act, guests included; never Energy, draw or
   Fanfare.
7. Cue: the chosen performer acts now, as at the end of the turn; a star pays
   as usual. On an empty stage a Cue does nothing.

THE READINGS taken where the paper is silent are `READINGS` at the foot of
this module; the choices a player makes inside a card (which performer a Cue
names, and so on) are the pilot's (`tier0.pilot.policy.FurinaStageDecider`).
"""

from __future__ import annotations

import collections

CHARACTER = "furina"

# ----------------------------------------------------------------------
# THE NUMBERS (sec.2 as sec.8 and sec.10 amend it). Names are fixed: the C#
# `FurinaStageLaw` mirrors them by name.
# ----------------------------------------------------------------------
SEATS = 3                    # rule 1
SOLD_OUT_SEATS = 4           # Sold Out: "Your stage has a fourth seat."
CASTING_AGENT_OFFER = 3      # Casting Agent: "Choose 1 of 3"
BOW_FANFARE = 1              # rule 3

ACT_USHER_BLOCK = 4
ACT_CHEVALMARIN_DAMAGE = 2   # to ALL enemies
ACT_CRABALETTA_DAMAGE = 5    # to a random enemy

ACT_NEUVILLETTE_PRICE = 2
ACT_NEUVILLETTE_DAMAGE = 7   # Hydro to ALL
#: Neuvillette's line: "Your Hydro damage deals 2 more" -- a Hydro card's
#: hits and Hydro act hits, per hit, while she is on stage.
NEUVILLETTE_HYDRO_BONUS = 2
ACT_CLORINDE_PRICE = 1
ACT_CLORINDE_DAMAGE = 6      # Electro to a random enemy
#: Clorinde's line: "Whenever you Spend, deal 4 Electro damage to a random
#: enemy." Flat: a line, not an act, so Rehearsal does not scale it.
CLORINDE_SPEND_DAMAGE = 4
ACT_LYNEY_PRICE = 1          # act: add a Trick to your hand
TRICK_DAMAGE = 4             # Trick: 0 cost, "Deal 4 Pyro damage. Retain. Exhaust."
ACT_ESCOFFIER_PRICE = 2      # act: your Salon members act
NAVIA_PER_SPENT = 2          # free act: Geo, twice the Fanfare spent this turn
ACT_CHARLOTTE_GAIN = 1       # act: gain 1 Fanfare
CHARLOTTE_DRAW = 1           # line: at the start of your turn, draw 1 more
ACT_LYNETTE_DAMAGE = 3       # Anemo to an enemy with an aura if any
ACT_CHEVREUSE_PRICE = 2      # act, the first time each turn: pay 2 ...
ACT_CHEVREUSE_ENERGY = 1     # ... and next turn gain 1 Energy
ACT_SIGEWINNE_BLOCK = 3      # act: 3 Block ...
SIGEWINNE_PER_HP_LOSS = 2    # ... plus 2 per time you lost HP since her last act
ACT_WRIOTHESLEY_DAMAGE = 4   # act: 4 Cryo to a random enemy ...
WRIOTHESLEY_PER_BLOCKED = 1  # ... plus 1 per damage your Block stopped since
PNEUMA_FANFARE = 2           # Arkhe Alignment / Dual Nature: Pneuma's gain

SALON = ("usher", "chevalmarin", "crabaletta")
#: Kept as `PERFORMERS` too: the trio is who "a random Salon member" rolls.
PERFORMERS = SALON
OPENING_MEMBER = "usher"     # Salon Solitaire

#: The stars pay for their acts; the supports are free (Chevreuse's own
#: "pay 2" is her act's payment, not a star's price).
STAR_PRICE = {"neuvillette": ACT_NEUVILLETTE_PRICE,
              "clorinde": ACT_CLORINDE_PRICE,
              "lyney": ACT_LYNEY_PRICE,
              "escoffier": ACT_ESCOFFIER_PRICE,
              "navia": 0}
STARS = tuple(STAR_PRICE)
SUPPORTS = ("charlotte", "lynette", "chevreuse", "sigewinne", "wriothesley")
GUESTS = ("neuvillette", "clorinde", "navia", "chevreuse", "wriothesley",
          "sigewinne", "charlotte", "lynette", "lyney", "escoffier")

#: The elements the guests' damage acts carry (the trio's carry none).
GUEST_ELEMENTS = {"neuvillette": "hydro", "clorinde": "electro",
                  "navia": "geo", "wriothesley": "cryo", "lynette": "anemo"}

#: The Powers this arm reads, by `apply_power` id.
REHEARSAL = "fs_rehearsal"
PREMIERE_SEASON = "fs_premiere_season"
THUNDEROUS_APPLAUSE = "fs_thunderous_applause"
REVOLVING_STAGE = "fs_revolving_stage"
SEASON_TICKETS = "fs_season_tickets"
TIDE_OF_APPLAUSE = "fs_tide_of_applause"
CRITICS_DARLING = "fs_critics_darling"
FIVE_CENTURY_ACT = "fs_five_century_act"
ARKHE_ALIGNMENT = "fs_arkhe_alignment"
FULL_HOUSE = "fs_full_house"
STAR_BILLING = "fs_star_billing"
STAR_TURN = "fs_star_turn"
SOLD_OUT = "fs_sold_out"
REGINA = "fs_regina_of_all_waters"
SOLILOQUY = "fs_soliloquy"
ONE_WOMAN_SHOW = "fs_one_woman_show"
PEOPLE_OF_FONTAINE = "fs_people_of_fontaine"
THE_CROWD_ROARS = "fs_the_crowd_roars"

#: The Last Act: "Costs 1 less for each empty seat." Keyed by id.
LAST_ACT_ID = "proto_fs_the_last_act"

#: Casting Agent's offer: the Guest Cast's ten cards, one per guest.
GUEST_STAR_CARD_IDS: tuple[str, ...] = tuple(
    "proto_fs_guest_star_" + g for g in GUESTS)

#: Lyney's Trick, a token card (no sheet row): built by `make_trick`.
TRICK_ID = "proto_fs_trick"


# ----------------------------------------------------------------------
# THE STARTER AND THE POOL (read by `tier0/content/loader.py`).
# ----------------------------------------------------------------------
#: Base Strike x4, Defend x4, and the two kit cards (sec.4 / sec.10).
STARTER_IDS: tuple[str, ...] = (
    "strike", "strike", "strike", "strike",
    "defend", "defend", "defend", "defend",
    "proto_fs_curtain_rise",        # Deal 7. Spend 3: deal 17 instead.
    "proto_fs_standing_ovation",    # Rising Applause: Gain 3 Fanfare.
)

#: Which shipped kit card each starter row re-authors (the rows' own
#: `replaces:`; `loader.declared_starter_substitutions`).
STARTER_SUBS: dict[str, str] = {
    "aria_of_recompense": "proto_fs_curtain_rise",
    "an_invitation": "proto_fs_standing_ovation",
}

#: Two shipped starter rows whose Stage twins are offered as Commons.
PROMOTED_STARTERS: dict[str, str] = {
    "salon_debut": "proto_fs_salon_debut",
    "regal_bearing": "proto_fs_regal_bearing",
}

#: `{shipped id: prototype id}`, each at the same rarity
#: (`rewards.character_pool` refuses a cross-rarity substitution).
POOL_SUBS: dict[str, str] = {
    # --- Commons ---
    "surintendante_chevalmarin": "proto_fs_surintendante_chevalmarin",
    "mademoiselle_crabaletta": "proto_fs_mademoiselle_crabaletta",
    "blocking_notes": "proto_fs_warm_reception",
    "usher_the_waves": "proto_fs_tidal_flourish",
    "stage_lights": "proto_fs_interposition",          # Places, Everyone!
    "breathless": "proto_fs_improvised_number",
    "graceful_retreat": "proto_fs_between_acts",
    "house_call": "proto_fs_ensemble_piece",
    "lasting_impression": "proto_fs_hold_your_places",
    "applause_line": "proto_fs_quick_cue",             # Quick Flourish
    "swelling_overture": "proto_fs_step_forward",
    "shared_billing": "proto_fs_plot_twist",           # Encore!
    "ebb_and_flow": "proto_fs_stage_whisper",
    "dinner_service": "proto_fs_cheered_on",
    "macaron_break": "proto_fs_spirited_aria",
    "casting_call": "proto_fs_bubble_aria",
    "commanding_gaze": "proto_fs_commanding_gaze",
    "undercurrent": "proto_fs_undercurrent",
    "warmup_act": "proto_fs_warmup_act",
    # --- Uncommons ---
    "torrential_turn": "proto_fs_grand_entrance",
    "crescendo": "proto_fs_ousia_surge",
    "many_waters_melody": "proto_fs_pneuma_refrain",
    "change_the_bill": "proto_fs_bis",
    "take_your_bow": "proto_fs_final_bow",
    "full_ensemble": "proto_fs_tutti",
    "dramatic_entrance": "proto_fs_bravura",
    "fortissimo_guard": "proto_fs_full_house",
    "standing_ovation": "proto_fs_thunderous_applause",
    "audience_participation": "proto_fs_guest_star_chevreuse",
    "deep_breath": "proto_fs_guest_star_wriothesley",
    "standing_room_only": "proto_fs_guest_star_sigewinne",
    "limelight": "proto_fs_guest_star_charlotte",
    "take_it_from_the_top": "proto_fs_guest_star_lynette",
    "grand_salon": "proto_fs_revolving_stage",
    "curtain_cue": "proto_fs_oratrices_verdict",
    "top_billing": "proto_fs_season_tickets",
    "supporting_cast": "proto_fs_star_billing",
    "tempo_change": "proto_fs_intermission",
    "poised_riposte": "proto_fs_counterclaim",         # Dress Rehearsal
    "florid_cadenza": "proto_fs_da_capo",
    "waters_embrace": "proto_fs_groundswell",
    "leading_role": "proto_fs_tide_of_applause",
    "hearts_swelling": "proto_fs_soliloquy",
    "curtain_up": "proto_fs_dual_nature",
    "courtroom_drama": "proto_fs_courtroom_drama",
    "crashing_waves": "proto_fs_crashing_waves",
    "duet": "proto_fs_duet",
    "quick_change": "proto_fs_quick_change",
    "witness_stand": "proto_fs_witness_stand",
    # --- Rares ---
    "universal_revelry": "proto_fs_let_the_people_rejoice",
    "endless_waltz": "proto_fs_arkhe_alignment",
    "prima_donna": "proto_fs_five_century_act",
    "reginas_mercy": "proto_fs_guest_star_neuvillette",
    "thunderous_ovation": "proto_fs_guest_star_clorinde",
    "encore_performance": "proto_fs_guest_star_navia",
    "rain_of_roses": "proto_fs_guest_star_lyney",
    "the_final_verdict": "proto_fs_guest_star_escoffier",
    "showstopper": "proto_fs_bring_the_house_down",
    "flood_of_emotion": "proto_fs_grand_finale",
    "grand_gala": "proto_fs_gala_premiere",
    "high_tide": "proto_fs_grand_deluge",
    "the_sea_is_my_stage": "proto_fs_regina_of_all_waters",
    "star_of_the_show": "proto_fs_one_woman_show",
    "unheard_confession": "proto_fs_sold_out",
    "singer_of_many_waters": "proto_fs_singer_of_many_waters",
    "command_performance": "proto_fs_endless_waltz",
}

#: Rows offered without replacing a shipped row. Gentilhomme Usher (a Common,
#: was the Uncommon Leading Lady) and Premiere Season (a Rare Power, was the
#: Uncommon Double Casting) changed rarity in sec.10, so they left `POOL_SUBS`
#: for here and their old shipped rows are `POOL_DROPS`.
POOL_ADDS: tuple[str, ...] = (
    "proto_fs_solo_verse",
    "proto_fs_aria_for_one",
    "proto_fs_interval_bell",
    "proto_fs_casting_agent",
    "proto_fs_the_last_act",
    "proto_fs_critics_darling",
    "proto_fs_star_turn",
    "proto_fs_opening_number",
    "proto_fs_leading_lady",        # Gentilhomme Usher (Common)
    "proto_fs_double_casting",      # Premiere Season (Rare Power)
)

#: Shipped rows taken out of the offer with no Stage row in their slot.
POOL_DROPS: tuple[str, ...] = (
    "gentilhomme_usher",
    "suffering_for_art",
    "held_breath",
    "dress_rehearsal",
    "crowd_work",
    "directors_cut",
    "pit_orchestra",
    "rapturous_applause",
    "an_invitation",
    "guest_list",
    "matinee_performance",
)


# ----------------------------------------------------------------------
# The readers.
# ----------------------------------------------------------------------
def is_furina(player) -> bool:
    return getattr(player, "character_id", None) == CHARACTER


def active(player) -> bool:
    """Is the Stage live for this player? Every hook is AND-ed with this."""
    return is_furina(player)


def stage(player) -> list:
    """The seats, front first (performer names). `[]` for anyone else."""
    return getattr(player, "stage", []) if active(player) else []


def fanfare(player) -> int:
    return int(getattr(player, "stage_fanfare", 0)) if active(player) else 0


def count(player) -> int:
    return len(stage(player))


def rehearsal(player) -> int:
    return int((getattr(player, "powers", None) or {}).get(REHEARSAL, 0))


def capacity(player) -> int:
    """`SEATS`, or `SOLD_OUT_SEATS` with Sold Out on her."""
    if active(player) and (getattr(player, "powers", None) or {}).get(
            SOLD_OUT, 0):
        return SOLD_OUT_SEATS
    return SEATS


def _seats(player) -> list:
    if getattr(player, "stage", None) is None:
        player.stage = []
    return player.stage


def _decider(state):
    d = getattr(state.player, "stage_decider", None)
    if d is None:
        from tier0.pilot import policy               # late: avoids the cycle
        return policy.FURINA_STAGE_DECIDER
    return d


def is_salon_summon_card(card) -> bool:
    """Escoffier's "Salon summon card": a row whose OWN effect summons a
    Salon member, a TOP-LEVEL `stage_summon` (Improvised Number's
    conditional summon is not one). Codegen twin: `IStageSalonSummonCard`."""
    return any(fx.get("op") == "stage_summon"
               for fx in (getattr(card, "effects", None) or []))


def _walk(effects_):
    for fx in effects_ or []:
        yield fx
        for branch in ("then", "else"):
            yield from _walk(fx.get(branch))
        for mode in fx.get("modes") or []:
            yield from _walk(mode.get("effects"))


def is_cue_card(card) -> bool:
    """Lyney's "Cue card": a card with a `stage_cue` op anywhere on it.
    Codegen twin: `IStageCueCard`."""
    return any(fx.get("op") == "stage_cue"
               for fx in _walk(getattr(card, "effects", None)))


# ----------------------------------------------------------------------
# THE LEDGER. INSTRUMENT ONLY: nothing reads it back to decide anything.
#
#     start + gained - spent - paid == fanfare now
# ----------------------------------------------------------------------
GAIN_CARD = "card"          # a card's "Gain N Fanfare" (and a guest card's)
GAIN_BOW = "bow"            # rule 3's 1
GAIN_CHARLOTTE = "charlotte"
GAIN_POWER = "power"        # Season Tickets, Tide of Applause, Pneuma, ...
GAIN_SOURCES = (GAIN_CARD, GAIN_BOW, GAIN_CHARLOTTE, GAIN_POWER)


def ledger(state) -> dict:
    led = getattr(state, "stage_ledger", None)
    if led is None:
        led = {}
        state.stage_ledger = led
    if not led:
        led.update(
            start=fanfare(state.player),
            gained={s: 0 for s in GAIN_SOURCES}, spent=0, spends=0,
            paid={}, acts=collections.Counter(),
            star_acts=collections.Counter(), star_skips=collections.Counter(),
            cues=0, cues_on=collections.Counter(), cue_whiffs=0,
            bows=collections.Counter(), walk_ons=0, guest_repeats=0,
            summons=collections.Counter(), clorinde_procs=0,
            thunderous_draws=0, returns=0, guest_turns=collections.Counter(),
            fanfare_at_turn_end=[])
    return led


def ledger_expected_end(led: dict) -> int:
    return (led["start"] + sum(led["gained"].values()) - led["spent"]
            - sum(led["paid"].values()))


# ----------------------------------------------------------------------
# Fanfare: gain, Spend, payment.
# ----------------------------------------------------------------------
def _changed(state, delta: int) -> None:
    """Critics' Darling: "Whenever your Fanfare changes, deal that much damage
    to a random enemy." Every gain, every Spend, every payment; unpowered,
    no element, once per stack."""
    from tier0.engine import effects                 # late: avoids the cycle
    copies = int(state.player.powers.get(CRITICS_DARLING, 0))
    size = abs(int(delta))
    if copies <= 0 or size <= 0:
        return
    state.emit("stage_critics_darling", amount=size, copies=copies)
    for _ in range(copies):
        if not state.living_enemies:
            return
        enemy = state.rng.choice(state.living_enemies)
        effects.deal_damage_to_enemy(state, enemy, size, element=None,
                                     powered=False, source="card")


def gain(state, amount: int, source: str = GAIN_CARD) -> int:
    """Gain N Fanfare (rule 5)."""
    p = state.player
    amount = int(amount)
    if not active(p) or amount <= 0:
        return 0
    if source not in GAIN_SOURCES:
        raise ValueError(f"unknown Fanfare source {source!r}")
    ledger(state)["gained"][source] += amount
    p.stage_fanfare += amount
    p.stage_gained_this_turn += amount
    state.emit("stage_gain", amount=amount, source=source,
               fanfare=p.stage_fanfare)
    _changed(state, amount)
    return amount


def can_pay(player, amount: int) -> bool:
    """Does she hold `amount` Fanfare? A Spend mode is offered only then."""
    return active(player) and fanfare(player) >= int(amount)


def spend(state, amount: int) -> int:
    """A card's Spend N, at the full price only. Feeds the spent-this-turn
    count and Clorinde's line. Returns what was spent (0: refused)."""
    p = state.player
    amount = int(amount)
    if not active(p) or amount <= 0:
        return 0
    if p.stage_fanfare < amount:
        state.emit("stage_spend_whiffed", amount=amount)
        return 0
    led = ledger(state)
    led["spent"] += amount
    led["spends"] += 1
    p.stage_fanfare -= amount
    p.stage_spent_this_turn += amount
    state.emit("stage_spend", amount=amount, fanfare=p.stage_fanfare,
               turn=state.turn)
    _changed(state, -amount)
    _clorinde_line(state)
    return amount


def spend_all(state) -> int:
    """"Spend all your Fanfare." Nothing held is no Spend."""
    p = state.player
    if not active(p):
        return 0
    held = int(p.stage_fanfare)
    if held <= 0:
        state.emit("stage_spend_whiffed", amount="all")
        return 0
    return spend(state, held)


def pay(state, member: str, amount: int) -> bool:
    """A performer's payment for its act (a star's price, Chevreuse's 2).
    NOT a Spend. False (nothing paid) when she holds less."""
    p = state.player
    amount = int(amount)
    if amount <= 0:
        return True
    if p.stage_fanfare < amount:
        return False
    paid = ledger(state)["paid"]
    paid[member] = paid.get(member, 0) + amount
    p.stage_fanfare -= amount
    state.emit("stage_paid", member=member, amount=amount,
               fanfare=p.stage_fanfare)
    _changed(state, -amount)
    return True


def _act_target(state, pool):
    """A performer's "random enemy": Oratrice's Verdict's enemy while it
    lives (this turn), else a random one of `pool`."""
    verdict = getattr(state.player, "stage_verdict", None)
    if (verdict is not None and getattr(verdict, "alive", False)
            and verdict in state.living_enemies):
        return verdict
    return state.rng.choice(pool)


def _clorinde_line(state) -> None:
    if "clorinde" not in stage(state.player) or not state.living_enemies:
        return
    ledger(state)["clorinde_procs"] += 1
    _hit(state, _act_target(state, state.living_enemies),
         CLORINDE_SPEND_DAMAGE, "electro", LINE_SOURCE)


# ----------------------------------------------------------------------
# Acts and Bows.
# ----------------------------------------------------------------------
def hydro_bonus(state) -> int:
    """Neuvillette's line for ONE Hydro hit: 2 while she is on stage."""
    return NEUVILLETTE_HYDRO_BONUS if "neuvillette" in stage(
        state.player) else 0


#: The `source` a performer's damage carries: an act, a Bow (a free act), or
#: Clorinde's line. Kit verbs, not card hits.
ACT_SOURCE = "furina_stage/act"
BOW_SOURCE = "furina_stage/bow"
LINE_SOURCE = "furina_stage/line"


def _hit(state, enemy, amount: int, element, source: str) -> None:
    """Every performer's damage, through one door: unpowered (Furina's
    Strength and Weak do not touch a performer), the performer's element,
    and Neuvillette's +2 on a Hydro hit while she is on stage."""
    from tier0.engine import effects                 # late: avoids the cycle
    if element == "hydro":
        amount += hydro_bonus(state)
    effects.deal_damage_to_enemy(state, enemy, amount, element=element,
                                 powered=False, source=source)


def make_trick():
    """Lyney's Trick: "Deal 4 Pyro damage. Retain. Exhaust." (0 cost)."""
    from tier0.engine.state import Card
    return Card(id=TRICK_ID, name="Trick", cost=0, type="attack",
                rarity="token", element="pyro", exhaust=True, retain=True,
                character=CHARACTER,
                effects=[{"op": "damage", "amount": TRICK_DAMAGE,
                          "target": "enemy", "applies_element": True}])


def act(state, member: str, *, free: bool = False) -> bool:
    """One performer's act. A star pays unless `free` (a Bow); a star that
    cannot pay skips (nothing spent). Returns whether it acted."""
    from tier0.engine import effects                 # late: avoids the cycle
    p = state.player
    if not active(p) or state.over or not p.alive:
        return False
    led = ledger(state)
    if member in STARS and not free:
        price = STAR_PRICE[member]
        if not pay(state, member, price):
            led["star_skips"][member] += 1
            state.emit("stage_star_skip", member=member, price=price,
                       fanfare=p.stage_fanfare)
            return False
        led["star_acts"][member] += 1
    if member == "chevreuse":
        # Once a turn, every act counted (a Bow included). A Bow is free; an
        # act she cannot pay skips and does not use the turn's act.
        if p.stage_chevreuse_acted:
            state.emit("stage_act_spent", member=member)
            return False
        if not free and not pay(state, member, ACT_CHEVREUSE_PRICE):
            led["star_skips"][member] += 1
            state.emit("stage_star_skip", member=member,
                       price=ACT_CHEVREUSE_PRICE, fanfare=p.stage_fanfare)
            return False
        p.stage_chevreuse_acted = True
    led["acts"][member] += 1
    state.emit("stage_act", member=member, free=free)
    source = BOW_SOURCE if free else ACT_SOURCE
    r = rehearsal(p)
    mult = max(1, int(p.stage_act_damage_mult))
    living = list(state.living_enemies)
    if member == "usher":
        p.block += ACT_USHER_BLOCK + r
    elif member == "chevalmarin":
        for enemy in living:
            _hit(state, enemy, (ACT_CHEVALMARIN_DAMAGE + r) * mult, None,
                 source)
    elif member == "crabaletta":
        if living:
            _hit(state, _act_target(state, living),
                 (ACT_CRABALETTA_DAMAGE + r) * mult, None, source)
    elif member == "neuvillette":
        for enemy in living:
            _hit(state, enemy, (ACT_NEUVILLETTE_DAMAGE + r) * mult, "hydro",
                 source)
    elif member == "clorinde":
        if living:
            _hit(state, _act_target(state, living),
                 (ACT_CLORINDE_DAMAGE + r) * mult, "electro", source)
    elif member == "lyney":
        # A full hand sends it to the discard pile (`_add_token`).
        effects._add_token(state, make_trick(), "hand")
    elif member == "escoffier":
        # "Your Salon members act": front to back, each its own act.
        for m in list(stage(p)):
            if m in SALON:
                act(state, m)
    elif member == "navia":
        spent = int(p.stage_spent_this_turn)
        if spent > 0 and living:
            _hit(state, _act_target(state, living),
                 (NAVIA_PER_SPENT * spent + r) * mult, "geo", source)
    elif member == "charlotte":
        gain(state, ACT_CHARLOTTE_GAIN, GAIN_CHARLOTTE)
    elif member == "lynette":
        wearing = [e for e in living if e.aura]
        pool = wearing or living
        if pool:
            _hit(state, _act_target(state, pool),
                 (ACT_LYNETTE_DAMAGE + r) * mult, "anemo", source)
    elif member == "chevreuse":
        energy_next_turn(state, ACT_CHEVREUSE_ENERGY)
    elif member == "sigewinne":
        losses = max(0, int(state.player_damage_events)
                     - int(p.stage_sigewinne_mark))
        p.block += ACT_SIGEWINNE_BLOCK + SIGEWINNE_PER_HP_LOSS * losses + r
        p.stage_sigewinne_mark = int(state.player_damage_events)
    elif member == "wriothesley":
        blocked = max(0, int(p.stage_wriothesley_blocked))
        p.stage_wriothesley_blocked = 0
        if living:
            _hit(state, _act_target(state, living),
                 (ACT_WRIOTHESLEY_DAMAGE + WRIOTHESLEY_PER_BLOCKED * blocked
                  + r) * mult, "cryo", source)
    return True


def energy_next_turn(state, amount: int) -> None:
    """"Gain N Energy next turn": Chevreuse's act and Interval Bell's Spend
    mode. Owed on `Player.stage_energy_next`, paid at `turn_start`."""
    p = state.player
    if not active(p) or int(amount) <= 0:
        return
    p.stage_energy_next = int(p.stage_energy_next) + int(amount)


def bow(state, member: str) -> None:
    """Rule 3: the performer's act once more, FREE, then 1 Fanfare after it;
    then Thunderous Applause's draw (1 per stack)."""
    p = state.player
    led = ledger(state)
    led["bows"][member] += 1
    p.stage_bows = int(p.stage_bows) + 1
    state.emit("stage_bow", member=member)
    act(state, member, free=True)
    gain(state, BOW_FANFARE, GAIN_BOW)
    draws = int(p.powers.get(THUNDEROUS_APPLAUSE, 0))
    if draws > 0 and not state.over:
        state.draw(draws)
        led["thunderous_draws"] += draws


def _seat(state, member: str, *, front: bool = False) -> None:
    p = state.player
    seats = _seats(p)
    if front:
        seats.insert(0, member)
    else:
        seats.append(member)
    if member == "sigewinne":
        p.stage_sigewinne_mark = int(state.player_damage_events)
    elif member == "wriothesley":
        p.stage_wriothesley_blocked = 0


def summon(state, member: str) -> str:
    """Rule 4. Returns what happened: seated | repeat | evict | walk_on."""
    p = state.player
    if not active(p):
        return "off"
    if member not in SALON and member not in GUESTS:
        raise ValueError(f"unknown performer {member!r}")
    seats = _seats(p)
    led = ledger(state)
    led["summons"][member] += 1
    if member in GUESTS and member in seats:
        # One of each: a second copy Bows it and it keeps its seat.
        led["guest_repeats"] += 1
        state.emit("stage_summon", member=member, via="repeat")
        bow(state, member)
        return "repeat"
    if len(seats) < capacity(p):
        _seat(state, member)
        state.emit("stage_summon", member=member, via="seat",
                   seats=len(seats))
        return "seated"
    salon_at = [i for i, m in enumerate(seats) if m in SALON]
    if salon_at:
        leaver = seats.pop(salon_at[0])
    elif member in SALON:
        # The walk-on: its free Bow act + 1 Fanfare, no seat.
        led["walk_ons"] += 1
        state.emit("stage_walk_on", member=member)
        bow(state, member)
        return "walk_on"
    else:
        leaver = seats.pop(0)                 # a guest onto an all-guest stage
    state.emit("stage_leave", member=leaver, reason="evicted",
               arriving=member)
    bow(state, leaver)
    _seat(state, member)
    state.emit("stage_summon", member=member, via="evict", seats=len(seats))
    return "evict"


def open_combat(state) -> None:
    """Salon Solitaire: combat opens with Usher on stage. Turn one only, at
    the post-draw site (`combat._player_turn`), onto an empty stage."""
    p = state.player
    if not active(p) or state.turn != 1:
        return
    ledger(state)
    seats = _seats(p)
    if seats:
        return
    _seat(state, OPENING_MEMBER)
    state.emit("stage_open", member=OPENING_MEMBER)


def guest_star(state, member: str, amount: int = 0) -> str:
    """A Guest Star card: "Summon X. Gain N Fanfare." Then Star Billing's draw
    and Star Turn's act (after the arrival, a repeat included)."""
    p = state.player
    if not active(p):
        return "off"
    if member not in GUESTS:
        raise ValueError(f"unknown guest {member!r}")
    how = summon(state, member)
    gain(state, int(amount), GAIN_CARD)
    billing = int(p.powers.get(STAR_BILLING, 0))
    if billing > 0 and not state.over:
        state.draw(billing)
        state.emit("stage_star_billing", member=member, drew=billing)
    for _ in range(int(p.powers.get(STAR_TURN, 0))):
        if state.over or not p.alive or member not in stage(p):
            break
        state.emit("stage_star_turn", member=member)
        act(state, member)
    return how


def cue(state, times: int = 1, index=None) -> bool:
    """Rule 7: the chosen performer acts now (`times` times: Bis!), a star
    paying each time. Lynette's line: the first Cue each turn moves the cued
    performer to the front first. An empty stage: nothing."""
    p = state.player
    if not active(p):
        return False
    seats = _seats(p)
    led = ledger(state)
    if not seats:
        led["cue_whiffs"] += 1
        state.emit("stage_cue_whiffed")
        return False
    if index is None:
        index = _decider(state).cue_target(state)
    if index is None or not (0 <= index < len(seats)):
        index = 0
    first = int(p.stage_cues_this_turn) == 0
    p.stage_cues_this_turn = int(p.stage_cues_this_turn) + 1
    if first and "lynette" in seats and index != 0:
        seats.insert(0, seats.pop(index))
        index = 0
        state.emit("stage_reorder", company=list(seats), by="lynette")
    member = seats[index]
    led["cues"] += 1
    led["cues_on"][member] += 1
    state.emit("stage_cue", member=member, times=int(times))
    for _ in range(max(1, int(times))):
        if state.over or not p.alive:
            break
        act(state, member)
    return True


def step_forward(state, index=None) -> None:
    """Step Forward: "Move a performer to the front." Empty stage: nothing."""
    p = state.player
    if not active(p):
        return
    seats = _seats(p)
    if len(seats) < 2:
        state.emit("stage_step_forward_whiffed")
        return
    if index is None:
        index = _decider(state).front_target(state)
    if index is None or not (0 < index < len(seats)):
        return
    seats.insert(0, seats.pop(index))
    state.emit("stage_reorder", company=list(seats), by="step_forward")


def final_bow(state, index=None):
    """Final Bow / Intermission: "A performer Bows and leaves." It leaves,
    then Bows (free act + 1 Fanfare); A Five-Century Act may return it.
    Empty stage: nothing. Returns the member, or None."""
    p = state.player
    if not active(p):
        return None
    seats = _seats(p)
    if not seats:
        state.emit("stage_final_bow_whiffed")
        return None
    if index is None:
        index = _decider(state).final_bow_target(state)
    if index is None or not (0 <= index < len(seats)):
        index = 0
    member = seats.pop(index)
    state.emit("stage_leave", member=member, reason="final_bow")
    bow(state, member)
    # A Five-Century Act: the first time each turn a performer Bows AND
    # LEAVES, it returns at the back if a seat is free.
    if (p.powers.get(FIVE_CENTURY_ACT, 0) and not p.stage_returned
            and len(seats) < capacity(p) and not state.over):
        p.stage_returned = True
        if member not in GUESTS or member not in seats:
            _seat(state, member)
            ledger(state)["returns"] += 1
            state.emit("stage_return", member=member)
    return member


def curtain_call(state) -> None:
    """Grand Finale / Let the People Rejoice: every performer Bows (free act
    + 1 Fanfare each) and keeps its seat. Front to back over a snapshot."""
    p = state.player
    if not active(p):
        return
    for member in list(stage(p)):
        if state.over or not p.alive:
            break
        bow(state, member)


def perform_all(state, guests_only: bool = False) -> None:
    """Tutti!: every performer acts now, front to back; Endless Waltz
    (`guests_only`): each guest acts. Stars pay."""
    p = state.player
    if not active(p):
        return
    for member in list(stage(p)):
        if state.over or not p.alive or not state.living_enemies:
            break
        if guests_only and member not in GUESTS:
            continue
        act(state, member)


def set_verdict(state) -> None:
    """Oratrice's Verdict: this turn, the performers' random picks find the
    card's own target."""
    p = state.player
    if not active(p):
        return
    p.stage_verdict = state.card_aim
    state.emit("stage_verdict", target=getattr(state.card_aim, "name", None))


def _ousia_or_pneuma(state, copies: int, *, floor: bool) -> str:
    p = state.player
    choice = _decider(state).arkhe_choice(state)
    if choice == "pneuma":
        gain(state, PNEUMA_FANFARE * copies, GAIN_POWER)
    else:
        choice = "ousia"
        mult = 1 + copies
        p.stage_act_damage_mult = (max(int(p.stage_act_damage_mult), mult)
                                   if floor else mult)
    return choice


def dual_nature(state) -> None:
    """Dual Nature: "Choose Ousia or Pneuma for this turn." Ousia: the
    performers' damage acts x2 this turn (not on top of an Arkhe Ousia);
    Pneuma: gain 2 Fanfare."""
    if not active(state.player):
        return
    choice = _ousia_or_pneuma(state, 1, floor=True)
    state.emit("stage_dual_nature", choice=choice)


def casting_agent(state, upgraded: bool = False):
    """Casting Agent: one of 3 random Guest Star cards (three different) into
    the hand, free this turn, upgraded when the card is. The pilot takes the
    first offered. A full hand takes nothing."""
    import copy                                      # stdlib, local by habit
    from tier0 import constants as C
    from tier0.content import loader, upgrades       # late: avoids the cycle
    from tier0.engine import effects                 # late: avoids the cycle
    p = state.player
    if not active(p):
        return None
    if len(p.hand) >= C.MAX_HAND_SIZE:
        state.emit("stage_casting_agent", offered=[], took=None)
        return None
    offer = state.rng.sample(list(GUEST_STAR_CARD_IDS),
                             min(CASTING_AGENT_OFFER, len(GUEST_STAR_CARD_IDS)))
    cid = offer[0] + (upgrades.SUFFIX if upgraded else "")
    card = copy.deepcopy(loader.get_card(cid))
    card.free_this_turn = True
    effects._add_token(state, card, "hand")
    state.emit("stage_casting_agent", offered=list(offer), took=card.id)
    return card


def empty_seats(player) -> int:
    if not active(player):
        return 0
    return max(0, capacity(player) - count(player))


def last_act_discount(state, card) -> int:
    """The Last Act: "Costs 1 less for each empty seat." PURE."""
    base = str(getattr(card, "id", "")).split("+")[0]
    if base != LAST_ACT_ID:
        return 0
    return empty_seats(state.player)


def cost_free(state, card) -> bool:
    """PURE. Escoffier's line ("The first Salon summon card you play each
    turn costs 0") and Lyney's ("The first Cue card you play each turn costs
    0"), each while that guest is on stage."""
    p = state.player
    if not active(p):
        return False
    seats = stage(p)
    if ("escoffier" in seats and int(p.stage_salon_cards_this_turn) == 0
            and is_salon_summon_card(card)):
        return True
    if ("lyney" in seats and int(p.stage_cue_cards_this_turn) == 0
            and is_cue_card(card)):
        return True
    return False


def note_card_played(state, card) -> None:
    """Counted at play, before the card resolves: the Salon summon cards and
    Cue cards played this turn (a card played before the guest arrived still
    counts as the first)."""
    p = state.player
    if not active(p):
        return
    if is_salon_summon_card(card):
        p.stage_salon_cards_this_turn = int(p.stage_salon_cards_this_turn) + 1
    if is_cue_card(card):
        p.stage_cue_cards_this_turn = int(p.stage_cue_cards_this_turn) + 1


# ----------------------------------------------------------------------
# Spend modes (`choose_one`).
# ----------------------------------------------------------------------
#: The head op of a Spend mode: "Spend 3: deal 17 instead".
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
    """A Spend mode is offered only when she holds its whole price."""
    amount = spend_mode_amount(mode)
    return amount is None or can_pay(player, amount)


def mode_refusal(player, mode: dict):
    if mode_offered(player, mode):
        return None
    label = mode.get("label") or "(unlabelled mode)"
    return f"{label!r} needs that much Fanfare"


def spend_mode_index(state, modes: list):
    """Which mode the pilot takes when a mode is a Spend mode, or None where
    the rule does not reach (another character, or no Spend mode)."""
    if not active(state.player):
        return None
    if not any(spend_mode_amount(m) is not None for m in modes):
        return None
    return _decider(state).spend_mode(state, modes)


# ----------------------------------------------------------------------
# The engine's hooks (`combat`, `reactions`).
# ----------------------------------------------------------------------
def turn_open(state) -> None:
    """The top of her turn: the flow counts and the once-a-turn latches reset
    (they held through the whole end-of-turn sequence before)."""
    p = state.player
    if not active(p):
        return
    p.stage_gained_this_turn = 0
    p.stage_spent_this_turn = 0
    p.stage_salon_cards_this_turn = 0
    p.stage_cue_cards_this_turn = 0
    p.stage_cues_this_turn = 0
    p.stage_chevreuse_acted = False
    p.stage_returned = False
    p.stage_act_damage_mult = 1
    p.stage_verdict = None


def turn_start(state) -> None:
    """After the hand draw (StS2 `AfterPlayerTurnStart`): Salon Solitaire on
    turn one; Chevreuse's Energy; Charlotte's extra card; then the turn-start
    Powers, in this order: One-Woman Show (on the stage the turn found),
    Premiere Season, Season Tickets, Regina of All Waters, Arkhe Alignment,
    and Revolving Stage last (so its Cue meets this turn's Rehearsal, Fanfare
    and Ousia)."""
    p = state.player
    if not active(p):
        return
    open_combat(state)
    if p.stage_energy_next:
        p.energy += int(p.stage_energy_next)
        state.emit("stage_energy", amount=int(p.stage_energy_next))
        p.stage_energy_next = 0
    if "charlotte" in stage(p):
        state.draw(CHARLOTTE_DRAW)
    show = int(p.powers.get(ONE_WOMAN_SHOW, 0))
    if show > 0 and not stage(p):
        p.energy += show
        state.draw(2 * show)
        state.emit("stage_one_woman_show", energy=show, drew=2 * show)
    season = int(p.powers.get(PREMIERE_SEASON, 0))
    if season > 0:
        p.powers[REHEARSAL] = rehearsal(p) + season
        state.emit("stage_premiere_season", rehearsal=p.powers[REHEARSAL])
    tickets = int(p.powers.get(SEASON_TICKETS, 0))
    if tickets > 0:
        gain(state, tickets, GAIN_POWER)
    if p.powers.get(REGINA, 0):
        from tier0.engine import reactions           # late: the cycle
        for enemy in list(state.living_enemies):
            reactions.resolve_hit(state, enemy, "hydro", 0,
                                  "furina_stage/regina")
    copies = int(p.powers.get(ARKHE_ALIGNMENT, 0))
    if copies > 0:
        choice = _ousia_or_pneuma(state, copies, floor=False)
        state.emit("stage_arkhe", choice=choice, copies=copies)
    for _ in range(int(p.powers.get(REVOLVING_STAGE, 0))):
        if state.over or not p.alive:
            break
        cue(state, 1, index=0)


def end_of_turn_acts(state) -> None:
    """Rule 1: every performer acts, front to back, over a snapshot of the
    stage. Full House: with every seat filled, each acts once more per
    stack."""
    p = state.player
    if not active(p):
        return
    company = list(stage(p))
    if company:
        times = 1 + (int(p.powers.get(FULL_HOUSE, 0))
                     if len(company) >= capacity(p) else 0)
        state.emit("stage_acts", company=list(company), times=times)
        for member in company:
            for _ in range(times):
                if (state.over or not p.alive
                        or not state.living_enemies):
                    break
                act(state, member)
    ledger(state)["fanfare_at_turn_end"].append(fanfare(p))


def note_blocked(state, blocked: int) -> None:
    """Wriothesley: what her Block stopped (any dealer) since his last act
    or his seating, counted while he is on stage."""
    p = state.player
    if active(p) and blocked > 0 and "wriothesley" in stage(p):
        p.stage_wriothesley_blocked = (int(p.stage_wriothesley_blocked)
                                       + int(blocked))


def note_reaction(state) -> None:
    """Tide of Applause: "Whenever you trigger an Elemental Reaction, gain N
    Fanfare." From `reactions._react`."""
    p = state.player
    if not active(p):
        return
    n = int(p.powers.get(TIDE_OF_APPLAUSE, 0))
    if n > 0:
        gain(state, n, GAIN_POWER)


def note_turn_census(state) -> None:
    """INSTRUMENT ONLY: one sample per player turn, at turn close."""
    p = state.player
    if not active(p):
        return
    state.emit("stage_census", performers=count(p), fanfare=fanfare(p),
               company=list(stage(p)))
    turns = ledger(state)["guest_turns"]
    for member in stage(p):
        if member in GUESTS:
            turns[member] += 1


def reset_for_combat(player) -> None:
    """Every fight opens on an empty stage with no Fanfare (performers are
    pets and live one combat)."""
    player.stage = []
    player.stage_fanfare = 0
    player.stage_gained_this_turn = 0
    player.stage_spent_this_turn = 0
    player.stage_salon_cards_this_turn = 0
    player.stage_cue_cards_this_turn = 0
    player.stage_cues_this_turn = 0
    player.stage_chevreuse_acted = False
    player.stage_returned = False
    player.stage_act_damage_mult = 1
    player.stage_energy_next = 0
    player.stage_verdict = None
    player.stage_bows = 0
    player.stage_sigewinne_mark = 0
    player.stage_wriothesley_blocked = 0


# ----------------------------------------------------------------------
# READINGS: where the sheet and the brief are silent. Pinned by
# `tier0/tests/test_furina_stage.py`.
# ----------------------------------------------------------------------
READINGS: tuple[str, ...] = (
    "A Guest Star card resolves in this order: the summon (rule 4), the "
    "card's own Fanfare, Star Billing's draw, then Star Turn's act (so a "
    "star that arrives with Fanfare can pay for its Star Turn act).",
    "Lynette's line counts every Cue this turn, made while she was on stage "
    "or not: a Cue before she arrived is still the turn's first. A Cue on "
    "an empty stage is no Cue and does not count.",
    "The turn-start order: Salon Solitaire (turn one), Chevreuse's Energy, "
    "Charlotte's draw, One-Woman Show, Premiere Season, Season Tickets, "
    "Regina of All Waters, Arkhe Alignment, Revolving Stage.",
    "Ousia's multiple and Oratrice's Verdict last until the start of her "
    "next turn (the end-of-turn acts are part of this turn).",
    "A Five-Century Act's returner re-takes a seat at the back; a guest "
    "already back on stage (a repeat cannot happen from a Final Bow) is not "
    "seated twice.",
    "Critics' Darling picks a plain random enemy (it is a Power, not a "
    "performer, so Oratrice's Verdict does not redirect it).",
)
