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
   a fixed price a card cannot be played without. Never below the line, half
   the HP she started this combat with. HP lost to a Drain is drained.
2. REPAY N: regain up to N drained HP, never more.
3. FANFARE: +1 per HP lost from any cause (after Block) and +1 per HP
   repaid. Spend N and the spend-all cards pay it. Universal Revelry doubles
   every gain (sec.17; a second copy triples it).
4. SALON SOLITAIRE: at the end of her turn, Repay 2, after the guests act.
5. GUEST STARS: three seats, guests only; a guest acts at the end of her
   turn; a fourth makes the oldest leave, acting once more; a second copy of
   one on stage makes it act and stay.
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
SINGER_REPAY_UPGRADED = 3                    # The Curtain Never Falls
CHARLOTTE_ACT_REPAY = T.CHARLOTTE_ACT_REPAY
CHARLOTTE_LINE_DRAW = 1
WRIOTHESLEY_ACT_DAMAGE = T.WRIOTHESLEY_ACT
LYNETTE_ACT_DAMAGE = T.LYNETTE_ACT
CLORINDE_ACT_DAMAGE = T.CLORINDE_ACT
CLORINDE_PER_REPAY = T.CLORINDE_PER_REPAY

#: The four guests of the slice, as the sheet's `stage_guest` names them.
GUESTS = ("charlotte", "wriothesley", "lynette", "clorinde")

#: The Powers this arm reads, by `apply_power` id. Each sheet row applies its
#: printed number: Salon's Encore and Thunderous Applause their damage (3, 4
#: upgraded), Endless Waltz and Universal Revelry 1 a copy.
SALONS_ENCORE = "fs_salons_encore"
ENDLESS_WALTZ = "fs_endless_waltz"
THUNDEROUS_APPLAUSE = "fs_thunderous_applause"
UNIVERSAL_REVELRY = "fs_universal_revelry"

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

#: THE SLICE'S 24 (sec.16), in the C# roster's order
#: (`FurinaStageRoster.Pool`): 12 Common, 8 Uncommon, 4 Rare.
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
    # The three Powers.
    "proto_fs_salons_encore",
    "proto_fs_endless_waltz",
    "proto_fs_thunderous_applause",
    # The four guests.
    "proto_fs_guest_star_charlotte",
    "proto_fs_guest_star_wriothesley",
    "proto_fs_guest_star_lynette",
    "proto_fs_guest_star_clorinde",
    # The two Rares.
    "proto_fs_universal_revelry",
    "proto_fs_let_the_people_rejoice",
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
    """Does she hold `amount` Fanfare? A Spend is offered only then."""
    return active(player) and int(player.ftd.fanfare) >= int(amount)


def can_drain(player, amount: int) -> bool:
    """Rule 1: would a Drain of `amount` stay at or above the line?"""
    return (active(player) and int(amount) > 0
            and player.hp - int(amount) >= T.half_line(player))


# ----------------------------------------------------------------------
# The combat's start and end.
# ----------------------------------------------------------------------
def reset_for_combat(player) -> None:
    """Every fight opens with an empty stage, no Fanfare, nothing drained,
    and the line read from the HP she enters with. Furina only: the research
    slice's own players (`furina_tide.build_player`) keep their record."""
    if not is_furina(player):
        return
    player.ftd = T.Ftd(singer=SINGER_REPAY, hit_fanfare=True, line=0.5,
                       entry_hp=int(player.hp), line_from_entry=True,
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
    only when it would not cross the line. Off Furina neither is offered."""
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
        return f"{label!r} would take her below the Drain line"
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
        return "it would take you below your Drain line"
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


def repay(state, amount: int) -> int:
    if not active(state.player):
        return 0
    return T.repay(state, int(amount))


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
    """"Spend all your Fanfare." Nothing held is no Spend."""
    if not active(state.player):
        return 0
    held = int(state.player.ftd.fanfare)
    return held if held > 0 and T.spend(state, held) else 0


def gain(state, amount: int, source: str = "card") -> None:
    if active(state.player):
        T.gain(state, int(amount), source)


def guest_star(state, member: str) -> str:
    """A Guest Star card: summon the guest (rule 5)."""
    if not active(state.player):
        return "off"
    if member not in GUESTS:
        raise ValueError(f"unknown guest {member!r}")
    return T.summon(state, member)


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
    "The line is half the HP she entered the combat with, compared in "
    "floats: from 78 or 77 a Drain may reach 39 and no lower.",
    "A guest already on stage acts and keeps its seat when summoned again "
    "(the slice's reading; no Fanfare for it).",
    "Salon Solitaire's Repay comes after the guests act, at the end of her "
    "turn.",
    "Charlotte's line counts the Singer's end-of-turn Repay: with no Repay "
    "earlier in the turn, it draws then.",
    "Lynette's act hits nothing when no enemy wears an aura.",
    "The curtain call is not a Repay: no Fanfare and no Repay reader.",
)
