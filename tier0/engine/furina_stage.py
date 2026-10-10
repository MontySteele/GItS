"""Furina, THE SALON'S TAB -- her arm, on the research slice's rules.

`review/active/furina-research-proposal-2026-10-05.md` is the design: sec.2's
rules with sec.16's Repay and curtain call, sec.16's slice of 24 and sec.17's
two edits. Its rows are `docs/prototype-surface.yaml`'s `proto_fs_*`. The
RULES are `tier0.engine.furina_tide`'s, the slice the proposal was proven on:
this module attaches that slice's per-combat record (`furina_tide.Ftd`) to
Furina at every combat's start, so every hook the engine already calls for the
slice (`turn_open`, `energy_kept`, `end_of_turn`, `on_hp_loss`) runs for her,
and the sheet's ops below call the slice's verbs. Its C# twin mirrors the
constants below by NAME (`tools/lint_constant_parity.py`).

THE RULES (the slice's docstring has them whole):

1. DRAIN N: lose N HP for the bigger effect -- a mode on a two-mode card, or
   a fixed price a card cannot be played without. Never to 0 HP; it may go
   past the line, the HP she started this combat with minus 1/4 of her Max
   HP (2026-10-09). HP lost to a Drain is drained.
2. REPAY N: regain up to N drained HP, never more.
3. FANFARE: +1 per HP lost from any cause (after Block) and +1 per HP
   repaid. Spend N and the spend-all cards pay it. Universal Revelry adds
   that much again to a Drain or a Repay, never a hit
   (`review/active/furina-pool-40-2026-10-05.md` sec.2).
4. SALON SOLITAIRE: at the end of her turn, Repay 2, after the guests act.
5. GUEST STARS (the pool to 75's rule, `review/active/furina-pool-growth-
   2026-10-09.md` sec.3): three seats (four with Ensemble Cast), guests
   only. A Guest Star exhausts and has no effect on summon; a guest acts at
   the end of her turn, oldest first; a fourth makes the oldest leave (no
   act) and its card goes to the discard pile, as Final Bow's guest's does;
   a second copy of one on stage moves it to the newest seat, no act.
6. THE CURTAIN CALL: when the combat ends, all drained HP returns
   (`close_combat`), and the HP carries into the run.

The choices a player makes inside a card (whether to take a Drain or a Spend
mode) are the decider's (`FurinaTideDecider`, or a pilot's own on
`Player.stage_decider`).
"""

from __future__ import annotations

from tier0.engine import furina_tide as T

CHARACTER = "furina"

# ----------------------------------------------------------------------
# THE NUMBERS. Names are fixed: the C# `FurinaStageLaw` mirrors them by name.
# ----------------------------------------------------------------------
SEATS = T.SEATS                              # rule 5
SINGER_REPAY = T.SINGER_REPAY                # rule 4: Salon Solitaire
SINGER_REPAY_UPGRADED = 2                    # The Curtain Never Falls (2026-10-09 trim, was 3)
CHARLOTTE_ACT_REPAY = T.CHARLOTTE_ACT_REPAY
CHARLOTTE_LINE_DRAW = 1
WRIOTHESLEY_ACT_DAMAGE = T.WRIOTHESLEY_ACT
LYNETTE_ACT_DAMAGE = T.LYNETTE_ACT
CLORINDE_ACT_DAMAGE = T.CLORINDE_ACT
CLORINDE_PER_REPAY = T.CLORINDE_PER_REPAY
# The pool to 39 (review/active/furina-pool-40-2026-10-05.md sec.3).
LYNEY_LINE_DROP = T.LYNEY_LINE_DROP
LYNEY_ACT_DRAIN = T.LYNEY_ACT_DRAIN
LYNEY_ACT_DAMAGE = T.LYNEY_ACT
SIGEWINNE_ACT_REPAY = T.SIGEWINNE_ACT_REPAY
CHEVREUSE_ACT_DAMAGE = T.CHEVREUSE_ACT
CHEVREUSE_LINE_VULNERABLE = T.CHEVREUSE_LINE_VULNERABLE
DRAIN_FLOOR = T.DRAIN_FLOOR
SHIPPED_LINE = T.SHIPPED_LINE
LINE_MAX_HP_DIVISOR = T.LINE_MAX_HP_DIVISOR
FREMINET_ACT_BLOCK = T.FREMINET_ACT_BLOCK
FREMINET_ACT_BLOCK_UPGRADED = T.FREMINET_ACT_BLOCK_UPGRADED
# The Spend paper (2026-10-10): Navia's half, Freminet's quarter, and "for
# every 4".
NAVIA_SPEND_DIVISOR = T.NAVIA_SPEND_DIVISOR
FREMINET_SPEND_DIVISOR = T.FREMINET_SPEND_DIVISOR
SPEND_UP_TO_EVERY = T.SPEND_UP_TO_EVERY
FOUNTAIN_TURNS = T.FOUNTAIN_TURNS
# The pool to 75 (review/active/furina-pool-growth-2026-10-09.md, ruled
# 2026-10-09): the guests' upgraded lines and acts (sec.3) and the new
# numbers (sec.5).
CHARLOTTE_ACT_REPAY_UPGRADED = T.CHARLOTTE_ACT_REPAY_UPGRADED
SIGEWINNE_ACT_REPAY_UPGRADED = T.SIGEWINNE_ACT_REPAY_UPGRADED
WRIOTHESLEY_ACT_DAMAGE_UPGRADED = T.WRIOTHESLEY_ACT_UPGRADED
LYNEY_ACT_DAMAGE_UPGRADED = T.LYNEY_ACT_UPGRADED
LYNETTE_ACT_DAMAGE_UPGRADED = T.LYNETTE_ACT_UPGRADED
CHEVREUSE_LINE_WEAK_UPGRADED = T.CHEVREUSE_LINE_WEAK_UPGRADED
CLORINDE_ACT_DAMAGE_UPGRADED = T.CLORINDE_ACT_UPGRADED
NAVIA_LINE_DISCOUNT = T.NAVIA_LINE_DISCOUNT
NAVIA_LINE_DISCOUNT_UPGRADED = T.NAVIA_LINE_DISCOUNT_UPGRADED
NEUVILLETTE_HYDRO_BONUS = T.NEUVILLETTE_HYDRO_BONUS
NEUVILLETTE_HYDRO_BONUS_UPGRADED = T.NEUVILLETTE_HYDRO_BONUS_UPGRADED
ESCOFFIER_ACT_DAMAGE = T.ESCOFFIER_ACT
ESCOFFIER_ACT_DAMAGE_UPGRADED = T.ESCOFFIER_ACT_UPGRADED
ESCOFFIER_LINE_REPAY = T.ESCOFFIER_LINE_REPAY
ENSEMBLE_SEATS = T.ENSEMBLE_SEATS
SHOWSTOPPER_SPEND = T.SHOWSTOPPER_SPEND
NEAR_LINE = T.NEAR_LINE
HYMN_THRESHOLD = T.HYMN_THRESHOLD
PRIMA_DONNA_FANFARE = T.PRIMA_DONNA_FANFARE
REGINA_DRAIN = T.REGINA_DRAIN
STAR_TURN_FANFARE_PER = T.STAR_TURN_FANFARE_PER

#: The eleven guests, as the sheet's `stage_guest` names them: the slice's
#: four, the pool to 39's three and the pool to 75's four.
GUESTS = ("charlotte", "wriothesley", "lynette", "clorinde",
          "lyney", "sigewinne", "chevreuse",
          "freminet", "navia", "neuvillette", "escoffier")

#: The Powers this arm reads, by `apply_power` id. Each sheet row applies its
#: printed number: Salon's Encore and Thunderous Applause their damage (3, 4
#: upgraded), Universal Revelry 1 a copy.
SALONS_ENCORE = "fs_salons_encore"
THUNDEROUS_APPLAUSE = "fs_thunderous_applause"
UNIVERSAL_REVELRY = "fs_universal_revelry"
# The pool to 39: Ousia Surge, A Five-Century Act, Critics' Darling and Bis!
# 1 a copy; Fountain of Lucine its Repay (3, 4 upgraded) a play, scheduled
# for three turns at her next turn start (`furina_tide.turn_start`).
OUSIA_SURGE = "fs_ousia_surge"
A_FIVE_CENTURY_ACT = "fs_a_five_century_act"
CRITICS_DARLING = "fs_critics_darling"
BIS = "fs_bis"
FOUNTAIN_OF_LUCINE = "fs_fountain_of_lucine"
# The pool to 75: each applies its printed number (Grand Entrance 4 [6], High
# Stakes 4 [6], Pneuma Tides 2 [3]) or 1 a copy.
GRAND_ENTRANCE = "fs_grand_entrance"
SHOWSTOPPER = "fs_showstopper"
ENSEMBLE_CAST = "fs_ensemble_cast"
CRESCENDO = "fs_crescendo"
PRIMA_DONNA = "fs_prima_donna"
STANDING_ROOM_ONLY = "fs_standing_room_only"
HIGH_STAKES = "fs_high_stakes"
REGINA_OF_ALL_WATERS = "fs_regina_of_all_waters"
PNEUMA_TIDES = "fs_pneuma_tides"
HYMN_OF_RENEWAL = "fs_hymn_of_renewal"
# The block gap (2026-10-09): 1 a copy.
THE_MASQUERADE = "fs_the_masquerade"

#: The slice's Power keys (`furina_tide.Ftd.powers`) to the arm's ids.
ARM_POWER_IDS = {
    "salon_encore": SALONS_ENCORE,
    "thunderous": THUNDEROUS_APPLAUSE,
    "revelry": UNIVERSAL_REVELRY,
    "ousia_surge": OUSIA_SURGE,
    "five_century": A_FIVE_CENTURY_ACT,
    "critics_darling": CRITICS_DARLING,
    "bis": BIS,
    # The pool to 75.
    "grand_entrance": GRAND_ENTRANCE,
    "showstopper": SHOWSTOPPER,
    "ensemble_cast": ENSEMBLE_CAST,
    "crescendo": CRESCENDO,
    "prima_donna": PRIMA_DONNA,
    "standing_room_only": STANDING_ROOM_ONLY,
    "high_stakes": HIGH_STAKES,
    "regina": REGINA_OF_ALL_WATERS,
    "pneuma_tides": PNEUMA_TIDES,
    "hymn_of_renewal": HYMN_OF_RENEWAL,
    # The block gap.
    "masquerade": THE_MASQUERADE,
}

# ----------------------------------------------------------------------
# THE STARTER AND THE POOL (read by `tier0/content/loader.py`).
# ----------------------------------------------------------------------
#: Base Strike x4, Defend x4, and the two kit cards (sec.16).
STARTER_IDS: tuple[str, ...] = (
    "strike", "strike", "strike", "strike",
    "defend", "defend", "defend", "defend",
    "proto_fs_curtain_rise",        # Deal 7. Drain 3: deal 12 instead.
    "proto_fs_standing_ovation",    # Rising Applause
)

#: THE SLICE'S 24 (sec.16), THE POOL TO 39's ten
#: (`review/active/furina-pool-40-2026-10-05.md` sec.3) and THE POOL TO 75's
#: 41 (`review/active/furina-pool-growth-2026-10-09.md` sec.5), in the C#
#: roster's order (`FurinaStageRoster.Pool`), less Endless Waltz (cut
#: 2026-10-09, with Standing Ovation moved to Uncommon), and the block gap's
#: four (ruled 2026-10-09): 20 Common, 37 Uncommon, 21 Rare, 78.
POOL_IDS: tuple[str, ...] = (
    # Drain (five).
    "proto_fs_mademoiselle_crabaletta",
    "proto_fs_soloists_solicitation",
    "proto_fs_surintendante_chevalmarin",
    "proto_fs_leading_lady",              # Gentilhomme Usher
    "proto_fs_salons_tab",
    # Repay (four).
    "proto_fs_surging_waters",
    "proto_fs_hymn_of_many_waters",
    "proto_fs_pneuma_refrain",
    "proto_fs_singer_of_many_waters",
    # Fanfare outlets (six).
    "proto_fs_tidal_flourish",
    "proto_fs_spirited_aria",
    "proto_fs_quick_cue",                 # Quick Flourish
    "proto_fs_standing_ovation_all",      # Standing Ovation
    "proto_fs_interval_bell",
    "proto_fs_bravura",
    # The two Powers (Endless Waltz was cut 2026-10-09).
    "proto_fs_salons_encore",
    "proto_fs_thunderous_applause",
    # The four guests.
    "proto_fs_guest_star_charlotte",
    "proto_fs_guest_star_wriothesley",
    "proto_fs_guest_star_lynette",
    "proto_fs_guest_star_clorinde",
    # The two Rares.
    "proto_fs_universal_revelry",
    "proto_fs_let_the_people_rejoice",
    # The pool to 39. Ousia.
    "proto_fs_grand_deluge",
    "proto_fs_ousia_surge",
    "proto_fs_guest_star_lyney",
    "proto_fs_a_five_century_act",
    # Pneuma.
    "proto_fs_guest_star_sigewinne",
    "proto_fs_fountain_of_lucine",
    "proto_fs_critics_darling",
    # The Crowd.
    "proto_fs_hold_the_stage",
    "proto_fs_guest_star_chevreuse",
    "proto_fs_bis",
    # The pool to 75 (2026-10-09). Guests and stage (11).
    "proto_fs_casting_call",
    "proto_fs_encore",
    "proto_fs_tutti",
    "proto_fs_final_bow",
    "proto_fs_grand_entrance",
    "proto_fs_guest_star_freminet",
    "proto_fs_showstopper",
    "proto_fs_ensemble_cast",
    "proto_fs_guest_star_navia",
    "proto_fs_guest_star_neuvillette",
    "proto_fs_guest_star_escoffier",
    # The Crowd (9).
    "proto_fs_crashing_waves",
    "proto_fs_bubble_aria",
    "proto_fs_commanding_gaze",
    "proto_fs_star_turn",
    "proto_fs_sold_out",
    "proto_fs_crescendo",
    "proto_fs_prima_donna",
    "proto_fs_standing_room_only",
    "proto_fs_bring_the_house_down",
    # Ousia, Drain (10).
    "proto_fs_undercurrent",
    "proto_fs_overdraft",
    "proto_fs_ousia_pledge",
    "proto_fs_against_the_tide",
    "proto_fs_pay_the_tab",
    "proto_fs_riptide_lunge",
    "proto_fs_high_stakes",
    "proto_fs_regina_of_all_waters",
    "proto_fs_the_deluge",
    "proto_fs_all_in",
    # Pneuma, Repay (10).
    "proto_fs_soothing_waters",
    "proto_fs_gentle_current",
    "proto_fs_clean_slate",
    "proto_fs_hydro_lance",
    "proto_fs_cleansing_torrent",
    "proto_fs_balance_the_books",
    "proto_fs_rising_tide",
    "proto_fs_pneuma_tides",
    "proto_fs_hymn_of_renewal",
    "proto_fs_grand_absolution",
    # The bridge (1).
    "proto_fs_ebb_and_flow",
    # The block gap (review/records/furina-drain-line-round-2026-10-09.md
    # pick 2, ruled 2026-10-09): 1 Common, 2 Uncommon, 1 Rare.
    "proto_fs_velvet_curtain",
    "proto_fs_private_box",
    "proto_fs_the_masquerade",
    "proto_fs_the_show_must_go_on",
)

#: The loader's older seams, empty since the slice: nothing is substituted
#: for a retired row, and the whole offer is `POOL_IDS` (`POOL_ADDS`).
STARTER_SUBS: dict[str, str] = {}
PROMOTED_STARTERS: dict[str, str] = {}
POOL_SUBS: dict[str, str] = {}
POOL_ADDS: tuple[str, ...] = POOL_IDS


# ----------------------------------------------------------------------
# The readers.
# ----------------------------------------------------------------------
def is_furina(player) -> bool:
    return getattr(player, "character_id", None) == CHARACTER


def active(player) -> bool:
    """Is her kit live for this player (Furina with a combat record)?"""
    return is_furina(player) and T.live(player)


def stage(player) -> list:
    """The guest seats, front (oldest) first. `[]` for anyone else."""
    return list(player.ftd.stage) if active(player) else []


def fanfare(player) -> int:
    return int(player.ftd.fanfare) if active(player) else 0


def drained(player) -> int:
    return int(player.ftd.drained) if active(player) else 0


def count(player) -> int:
    return len(stage(player))


def can_pay(player, amount: int) -> bool:
    """Can she pay a Spend of `amount`? A Spend is offered only then.
    Navia's line makes the first Spend each turn cost 2 less
    (`furina_tide.price_of`)."""
    return (active(player)
            and int(player.ftd.fanfare) >= T.price_of(player.ftd, amount))


def can_drain(player, amount: int) -> bool:
    """Rule 1 (the Drain line rule, 2026-10-09): a Drain is never refused
    for the line; only one that would take her to 0 HP or below is
    (`furina_tide.can_drain`)."""
    return (active(player) and int(amount) > 0
            and player.hp - int(amount) >= T.DRAIN_FLOOR)


# ----------------------------------------------------------------------
# The combat's start and end.
# ----------------------------------------------------------------------
def reset_for_combat(player) -> None:
    """Every fight opens with an empty stage, no Fanfare, nothing drained,
    and the line read from the HP she enters with. Furina only: the research
    slice's own players (`furina_tide.build_player`) keep their record."""
    if not is_furina(player):
        return
    player.ftd = T.Ftd(singer=SINGER_REPAY, hit_fanfare=True,
                       line=T.SHIPPED_LINE,
                       entry_hp=int(player.hp),
                       entry_max_hp=int(player.max_hp), line_from_entry=True,
                       curtain_call=True,
                       decider=getattr(player, "stage_decider", None)
                       or FURINA_TIDE_DECIDER)
    player.ftd.ledger["started_at_or_below_half"] = (
        player.hp <= player.max_hp / 2)


def close_combat(state) -> None:
    """THE CURTAIN CALL (sec.16): every drained HP returns when the combat
    ends, if she lived; the HP carries into the run."""
    if active(state.player):
        T.close_ledger(state)


# ----------------------------------------------------------------------
# Modes and fixed prices.
# ----------------------------------------------------------------------
#: The head ops of a priced mode: "Spend 3: ..." and "Drain 3: ...".
SPEND_MODE_OP = "stage_spend"
DRAIN_MODE_OP = "stage_drain"


def _head(mode: dict):
    body = mode.get("effects") or []
    return body[0] if body else {}


def spend_mode_amount(mode: dict):
    """`N` when this mode is a Spend mode, else None."""
    head = _head(mode)
    if head.get("op") != SPEND_MODE_OP:
        return None
    amount = head.get("amount", 1)
    return int(amount) if isinstance(amount, int) else None


def drain_mode_amount(mode: dict):
    """`N` when this mode is a Drain mode, else None."""
    head = _head(mode)
    if head.get("op") != DRAIN_MODE_OP:
        return None
    amount = head.get("amount", 1)
    return int(amount) if isinstance(amount, int) else None


def mode_offered(player, mode: dict) -> bool:
    """A Spend mode is offered only when she holds its price, a Drain mode
    only when it would not take her to 0 HP. Off Furina neither is
    offered."""
    spend = spend_mode_amount(mode)
    if spend is not None:
        return can_pay(player, spend)
    drain = drain_mode_amount(mode)
    if drain is not None:
        return can_drain(player, drain)
    return True


def mode_refusal(player, mode: dict):
    if mode_offered(player, mode):
        return None
    label = mode.get("label") or "(unlabelled mode)"
    if drain_mode_amount(mode) is not None:
        return f"{label!r} would take her to 0 HP"
    return f"{label!r} needs that much Fanfare"


def spend_mode_index(state, modes: list):
    """Which mode the decider takes on a card with a Spend or a Drain mode,
    or None where the rule does not reach (another character, or no priced
    mode)."""
    if not active(state.player):
        return None
    if not any(spend_mode_amount(m) is not None
               or drain_mode_amount(m) is not None for m in modes):
        return None
    return _decider(state).spend_mode(state, modes)


def fixed_price(card):
    """`(op, N)` of a card's one TOP-LEVEL `stage_drain` or `stage_spend` (a
    fixed price, "Drain 5. Deal 24 damage."), or None. Codegen twin:
    `gen_klee_cards.stage_fixed_price`."""
    for fx in getattr(card, "effects", None) or []:
        if fx.get("op") in (DRAIN_MODE_OP, SPEND_MODE_OP):
            amount = fx.get("amount", 1)
            return str(fx["op"]), int(amount) if isinstance(amount, int) else 0
    return None


def fixed_price_refusal(state, card):
    """Why a fixed-price card cannot be played now (Hemokinesis's shape), or
    None. A fixed Drain or Spend is unplayable for anyone but Furina."""
    price = fixed_price(card)
    if price is None:
        return None
    op, amount = price
    if op == DRAIN_MODE_OP and not can_drain(state.player, amount):
        return "it would take you to 0 HP"
    if op == SPEND_MODE_OP and not can_pay(state.player, amount):
        return "you do not have that much Fanfare"
    return None


# ----------------------------------------------------------------------
# The sheet's verbs (called by `effects`'s `stage_*` ops). Each is inert for
# anyone who is not Furina.
# ----------------------------------------------------------------------
def drain(state, amount: int) -> bool:
    if not active(state.player):
        return False
    return T.drain(state, int(amount))


def repay(state, amount: int, floor: str = "none") -> int:
    """A card's Repay N, with its Repay floor (`floor`: none, block or
    vigor; ruled 2026-10-09). The leftover is recorded for the play
    (`repay_left`)."""
    if not active(state.player):
        return 0
    return T.card_repay(state, int(amount), str(floor))


def repay_all(state) -> int:
    if not active(state.player):
        return 0
    return T.repay(state, int(state.player.ftd.drained))


def spend(state, amount: int) -> int:
    """A Spend N at the full price only. Returns what was spent."""
    amount = int(amount)
    if not active(state.player) or amount <= 0:
        return 0
    return amount if T.spend(state, amount) else 0


def spend_all(state) -> int:
    """"Spend all your Fanfare." Nothing held is no Spend; Bis! keeps half
    (`furina_tide.spend_all`)."""
    if not active(state.player):
        return 0
    return T.spend_all(state)


def spend_up_to(state, cap: int) -> int:
    """"Spend up to X" (the Spend paper, 2026-10-10): X or all she holds,
    never fails (`furina_tide.spend_up_to`). Returns what counts as spent."""
    if not active(state.player):
        return 0
    return T.spend_up_to(state, int(cap))


def spent_fours(spent: int) -> int:
    """`stage_spent_fours`: a play's spend in fours, rounded down ("Draw 1
    for every 4 spent"; the C# `FurinaStage.SpentFours`)."""
    return max(0, int(spent)) // SPEND_UP_TO_EVERY


def gain(state, amount: int, source: str = "card") -> None:
    if active(state.player):
        T.gain(state, int(amount), source)


def guest_star(state, member: str, upgraded: bool = False,
               card=None) -> str:
    """A Guest Star card (rule 5, the pool to 75's sec.3): summon the guest,
    no effect on summon; `card` is held by its seat until the guest leaves,
    and an upgraded one raises the guest's line or act. Grand Entrance
    Repays after."""
    if not active(state.player):
        return "off"
    if member not in GUESTS:
        raise ValueError(f"unknown guest {member!r}")
    result = T.summon(state, member, upgraded=upgraded, card=card)
    entrance = T._player_power(state.player, "grand_entrance")
    if entrance and not state.over:
        # "Repay 4. Gain 1 Block for any HP it could not Repay." (The Repay
        # floor, ruled 2026-10-09.)
        T.repay_floor(state, entrance, "block")
    return result


# ----------------------------------------------------------------------
# THE POOL TO 75's card verbs (`{op: furina, kind: ...}`), the C#
# `FurinaCards`. Each kind with a number prints it as `amount` (the card's
# `FsAmount`, upgrade key `furina_amount`).
# ----------------------------------------------------------------------
KINDS = ("act_oldest", "act_all", "final_bow", "tutor_guest", "repay_next",
         # The block gap (2026-10-09): Velvet Curtain's "Gain 2 Fanfare".
         "gain_fanfare")
KIND_AMOUNT = ("final_bow", "repay_next", "gain_fanfare")


def validate_op(card_id: str, fx: dict) -> None:
    """The loader's check, the codegen's `FURINA_KINDS` taken here too."""
    unknown = set(fx) - {"op", "kind", "amount"}
    if unknown:
        raise ValueError(f"card {card_id!r}: furina field(s) "
                         f"{sorted(unknown)} not understood")
    kind = fx.get("kind")
    if kind not in KINDS:
        raise ValueError(f"card {card_id!r}: furina kind {kind!r}")
    if ("amount" in fx) != (kind in KIND_AMOUNT):
        raise ValueError(f"card {card_id!r}: furina {kind} amount mismatch")
    amount = fx.get("amount", 1)
    if (not isinstance(amount, int) or isinstance(amount, bool)
            or amount <= 0):
        raise ValueError(f"card {card_id!r}: furina amount must be a "
                         "positive literal int")


def kind(state, fx: dict, card) -> None:
    """One `furina` kind. Inert for anyone who is not Furina."""
    if not active(state.player):
        return
    k = fx["kind"]
    if k == "act_oldest":
        T.act_oldest(state)
    elif k == "act_all":
        T.act_all(state)
    elif k == "final_bow":
        if state.player.ftd.stage:
            T.final_bow(state, T._decider_bow(state), int(fx["amount"]))
    elif k == "tutor_guest":
        T.tutor_guest(state)
    elif k == "repay_next":
        state.player.ftd.repay_next += int(fx["amount"])
    elif k == "gain_fanfare":
        # The ledger's gain, the path Universal Revelry's gain takes.
        T.gain(state, int(fx["amount"]), "card")
    else:                                            # pragma: no cover
        raise ValueError(f"unknown furina kind {k!r}")


# ---- the pool to 75's reads (count tokens and predicates) -------------
def drains_this_combat(player) -> int:
    """Undercurrent: "for each time you have Drained this combat"."""
    return int(player.ftd.drains_this_combat) if active(player) else 0


def half_drained(player) -> int:
    """Balance the Books: "half your drained HP", rounded down."""
    return drained(player) // 2


def repays_this_turn(player) -> int:
    """Rising Tide: "for each time you Repaid this turn"."""
    return int(player.ftd.repays_this_turn) if active(player) else 0


def repaid_this_play(player) -> int:
    """Grand Absolution's "that much": HP this play's Repays returned."""
    return int(player.ftd.repaid_this_play) if active(player) else 0


def repay_left(player) -> int:
    """The Repay floor's damage (Surging Waters, Hydro Lance, Cleansing
    Torrent): what this play's Repay could not return."""
    return int(player.ftd.repay_left_this_play) if active(player) else 0


def near_line(player) -> bool:
    """Against the Tide and High Stakes: within 5 HP of the Drain line, or
    at or below it."""
    return active(player) and T.near_line(player)


def none_drained(player) -> bool:
    """Clean Slate: "If you have no drained HP left"."""
    return active(player) and drained(player) <= 0


def hydro_bonus(state) -> int:
    """Neuvillette's line (`furina_tide.hydro_bonus`); 0 for anyone with no
    stage record (the slice's own players have one too)."""
    return T.hydro_bonus(state) if T.live(state.player) else 0


def high_stakes_bonus(state) -> int:
    """High Stakes: "While you are within 5 HP of your Drain line, your
    Attacks deal 4 more damage." 0 off the line or off Furina."""
    if not T.live(state.player):
        return 0
    n = T._player_power(state.player, "high_stakes")
    return n if n and T.near_line(state.player) else 0


def begin_play(state) -> None:
    """A card play opens: a fresh per-play Repay record."""
    if active(state.player):
        state.player.ftd.repaid_this_play = 0
        state.player.ftd.repay_left_this_play = 0


def energy_next_turn(state, amount: int) -> None:
    """"Gain N Energy next turn" (Interval Bell, Salon's Tab): owed on the
    slice's record, paid by `furina_tide.energy_kept` at her next turn."""
    if active(state.player) and int(amount) > 0:
        state.player.ftd.energy_next += int(amount)


# ----------------------------------------------------------------------
# The decider.
# ----------------------------------------------------------------------
def _decider(state):
    d = getattr(state.player, "stage_decider", None)
    return d if d is not None else FURINA_TIDE_DECIDER


class FurinaTideDecider:
    """The choices inside her cards, for the sim. Simple on purpose: a Drain
    mode is taken whenever it is offered (the slice's judged pilot takes 97
    to 100% of legal Drains, sec.10 K3), and a Spend mode whenever she holds
    its price. The slice's own pilots (`furina_tide_pilot`) are the
    instruments that price either."""

    def spend_mode(self, state, modes: list):
        priced = [i for i, m in enumerate(modes)
                  if spend_mode_amount(m) is not None
                  or drain_mode_amount(m) is not None]
        if len(priced) != 1:
            return None
        index = priced[0]
        keep = next((i for i in range(len(modes)) if i != index), 0)
        return index if mode_offered(state.player, modes[index]) else keep

    # The slice's decider hooks (`furina_tide.resolve_card` asks them for its
    # own rows only; the arm's rows resolve through the sheet's ops).
    def drain(self, state, card, spec) -> bool:
        return True

    def spend(self, state, card, spec) -> bool:
        return True

    def spend_all(self, state, card, spec) -> bool:
        return True


FURINA_TIDE_DECIDER = FurinaTideDecider()


# ----------------------------------------------------------------------
# READINGS: where the sheet and the paper are silent. Pinned by
# `tier0/tests/test_furina_tide_arm.py`.
# ----------------------------------------------------------------------
READINGS: tuple[str, ...] = (
    "The line is the HP she entered the combat with, minus 1/4 of the Max "
    "HP she entered it with, rounded down (ruled 2026-10-09): from 50/80 "
    "it is 30, from 78/78 it is 59. "
    "A Drain may go past it, never to 0 HP; the part drained past it is "
    "lost at the curtain call unless Repaid.",
    "A second copy of a guest already on stage moves it to the newest seat "
    "with no act (the pool to 75, sec.3); its card joins the seat's and "
    "returns with it, and an upgraded copy upgrades the guest.",
    "A guest evicted by a fourth summon leaves without acting (sec.3: no "
    "effect on summon); its cards return from the exhaust pile to the "
    "discard pile.",
    "Final Bow's guest is the decider's pick; the sim's default is the guest "
    "with the biggest act, the oldest on a tie.",
    "Casting Call takes the first Guest Star in the draw pile whose guest is "
    "not on stage, else the first (the C# asks the player).",
    "Showstopper Spends only when a guest is on stage and the bank holds the "
    "price; each copy is its own Spend and its own round of acts.",
    "Navia's discount is the first Spend each turn (a Spend made before she "
    "arrived uses it up); a Spend discounted to 0 is still a Spend.",
    "Spend up to X counts X or her Fanfare plus Navia's free points, "
    "whichever is less; the free points count and are not taken, so at 0 "
    "Fanfare with Navia on stage it counts 2 [3] (the Spend paper, "
    "2026-10-10).",
    "Navia's half-Spend and Freminet's quarter-Spend are each a Spend when "
    "at least 1 is spent, and Navia's discount applies when it is the turn's "
    "first Spend; each guest takes its share of what is left, oldest first, "
    "and again after Showstopper.",
    "Escoffier's line answers every act, his own included.",
    "Regina drains first at turn start, then Fountain of Lucine, Gentle "
    "Current and Pneuma Tides Repay, then Prima Donna reads the Fanfare.",
    "Salon Solitaire's Repay comes after the guests act, at the end of her "
    "turn.",
    "Charlotte's line counts the Singer's end-of-turn Repay: with no Repay "
    "earlier in the turn, it draws then.",
    "Lynette's act hits nothing when no enemy wears an aura.",
    "The curtain call is not a Repay: no Fanfare and no Repay reader.",
)
