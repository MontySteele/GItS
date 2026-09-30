"""VARKA, THE FOUR WINDS -- a PAPER-STAGE sim arm (exploration only).

Source of truth for the rules: `review/active/varka-paper-kit-2026-09-28.md`
(sec.2-sec.6). Card numbers are the paper's placeholders and are NOT tuned
here. The measuring tool is `tools/varka_paper_report.py`; nothing here is a
balance claim and no calibration band reads it.

THE SWITCH. `VARKA_PAPER` is a MODULE constant, off, for the reason
`furina_stage.FURINA_STAGE` is one: a run of the report moves neither the
constant census nor the world stamp. With it off, every hook this arm adds to
the shared engine (`reactions.resolve_hit`, `reactions._react`,
`effects.flat_attack_bonus`, `effects.bind_card_aim`) is a dead branch, and no
card, op or character id of Varka's is reachable: the cards are built here, by
`build_player`, and never enter the loader's card index. The one op the cards
speak, `varka`, is registered into `effects.OPS` by `enable()` only.

WHAT IS MODELLED (the paper's sec.3 and sec.6, the spec's placeholders):
  * ABSORB -- a card effect. An Absorb Swirl is a Swirl (spent copies spread
    to enemies lacking the element, flat 2 to ALL) that then TAKES the aura
    off the enemy it hit instead of leaving it spent.
  * WINDS -- the first Absorb of Pyro / Hydro / Electro / Cryo each fight
    grants that Wind for the fight: Pyro +2 on Attacks; Hydro 2 Block per
    Swirl; Electro draws 1 on the first Swirl each turn; Cryo 1 Weak to the
    enemy each Swirl hit.
  * BOREAS'S FANG (relic) -- each turn, the first hit of an Attack card on a
    FRESH aura is an Anemo Swirl-with-Absorb of that aura, whatever the card's
    own element (read here as: element-less or Anemo; see `_fang_can_take`).
    An Attack that hits no fresh aura does not use it up.
  * KNIGHTS -- Varka-only companion Skills that paint their element.
  * CONVERGING WINDS (Rare Power) -- the spread hit is the flat 2 carrying the
    swirled element; a reaction it sets off lands on that enemy only (an
    Overload's splash does not leave it); a spread reaction never Swirls.

READINGS TAKEN WHERE THE PAPER IS SILENT (each is flagged in the report):
  * Knights are SKILLS (companion). If they were Attacks, the Fang would
    absorb a Knight's own hit on a painted enemy instead of letting it react.
  * The Fang absorbs on ONE hit per turn -- the first fresh-aura hit of the
    first qualifying Attack -- even when that Attack hits several enemies.
  * Grand Master's Order's "next Knight" counts Knights' Muster as a Knight.
  * Gale Sweep picks its targets when played (every enemy with a fresh aura
    at that moment) and hits them in board order; a spread from an earlier
    target can overwrite a later target's different aura before it is hit.
  * An Absorb grants its Wind AFTER its own Swirl resolves, so the Wind it
    grants does not pay on the Swirl that granted it.

REVISION TWO (paper sec.9, 2026-09-29), a second arm beside revision one,
chosen per fight by `build_player(rev=2)` (revision one stays the default and
is unchanged):
  * ABSORB IS NOT A SWIRL. An Absorb (a card that prints it, or Boreas's Fang
    when the pilot opts in) on a FRESH aura whose Wind is not held takes the
    aura off, grants the Wind, spreads nothing and deals no flat 2; the card's
    own damage lands. On no fresh aura the hit is the shared rule.
  * READING (sec.9.1: an Absorb on "an element whose Wind you hold, does only
    the card's damage"): `ABSORB_HELD_SWIRLS` True (default) lets an Anemo
    Absorb card on a held Wind's fresh aura fall through to the shared rule,
    i.e. SWIRL it; False is the literal reading (the aura is untouched).
  * SWIRL is the shared rule, untouched (a spread copy replaces a different
    aura the other enemy wore).
  * WINDS all pay on a Swirl: Pyro 3 to the enemy hit (element-less, the flat
    2's path); Hydro 3 Block; Electro draws 1 on the first Swirl each turn;
    Cryo 1 Weak to the enemy hit.
  * BOREAS'S FANG is optional: once each turn the pilot may set `fang_want`
    on an Attack; its first hit on a fresh aura then Absorbs. Declining does
    not use the Fang up. Any Attack qualifies (sec.9.3 names no element).
  * Gale Sweep SNAPSHOTS: each target Swirls the aura it wore when the card
    was played, even if an earlier Swirl of the sweep spread over it.
  * Grand Master's Order's repeat may choose a different Knight (Muster) and
    a different target (`muster_choice2`, `aim2`).
  * ASCENSION version A (6 + 6/Wind, Exhaust) or B (6 + 8/Wind, lose those
    Winds, no Exhaust; a lost Wind can be Absorbed again), `asc_version`.
  * SINGLE-WIND runs (`fixed_winds`): those Winds are held from turn 1 and an
    Absorb grants nothing (`no_gain`).

REVISION 2.1 (`build_player(rev=2, fork=True)`), switches on top of two:
  * BOREAS'S FANG IS THE FORK: "Once each turn, when an Attack hits an enemy
    with a fresh aura, you may Absorb it or Swirl it." The pilot sets
    `fang_want` to "absorb" or "swirl". A Fang Swirl is a full shared-rule
    Swirl (spread, flat 2, the Winds) even from a Strike. An Anemo Attack
    Swirls by the shared rule anyway, so a Fang Swirl there is not spent.
  * AN ABSORB ON A HELD WIND SWIRLS INSTEAD (card or Fang).
  * Ascension A is the headline; B stays runnable.

REVISION 2.2 (tuning, switches on top of 2.1):
  * `winds_set="W2"`: Pyro Wind deals 3 to ALL enemies on a Swirl; Hydro 4
    Block per Swirl; Electro's first Swirl each turn draws 2; Cryo as 2.1.
  * `muster_cost=0` (starter variant S1): Knights' Muster costs 0.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

VARKA_PAPER = False          # THE SWITCH. Off: every hook is a dead branch.

CHARACTER = "varka"
HP = 80                      # PLACEHOLDER: the paper names no HP (Ironclad's)
ELEMENT = "anemo"
WIND_ELEMENTS = ("pyro", "hydro", "electro", "cryo")

PYRO_WIND_ATTACK_BONUS = 2
HYDRO_WIND_BLOCK = 2
ELECTRO_WIND_DRAW = 1
CRYO_WIND_WEAK = 1
STORMWARD_BONUS = 3
STORMWARD_WINDS = 2
ASCENSION_BASE = 6
ASCENSION_PER_WIND = 6

# --- revision two (sec.9) placeholders ---
R2_PYRO_SWIRL_DAMAGE = 3
R2_HYDRO_BLOCK = 3
R2_ELECTRO_DRAW = 1
R2_CRYO_WEAK = 1
ASCENSION_B_PER_WIND = 8
ABSORB_HELD_SWIRLS = True    # sec.9.1 reading; see the module docstring
# --- revision 2.2, Winds set W2 ---
W2_PYRO_SWIRL_DAMAGE_ALL = 3
W2_HYDRO_BLOCK = 4
W2_ELECTRO_DRAW = 2

KNIGHT_ELEMENT = {"amber": "pyro", "barbara": "hydro", "lisa": "electro",
                  "kaeya": "cryo"}


@dataclass
class VarkaState:
    """Per-fight state, hung on the Player (a fresh Player per fight)."""
    winds: dict = field(default_factory=dict)     # element -> turn gained
    fang_turn: int = -1          # the turn the Fang was last used
    electro_turn: int = -1       # the turn the Electro Wind last drew
    absorb_card: bool = False    # the resolving card prints Absorb
    playing: object = None       # the card the pilot just handed the engine
    aim: object = None           # the pilot's aim for that card
    muster_choice: Optional[str] = None
    gmo_pending: int = 0
    swirls_this_card: int = 0
    stormward: int = 0
    converging: bool = False
    landing: bool = False        # inside a Converging spread
    disabled_winds: frozenset = frozenset()       # ablation (report only)
    # --- the ledger the report reads ---
    absorbs: list = field(default_factory=list)   # (turn, element, source)
    swirls: int = 0
    knight_hits: list = field(default_factory=list)
    ascension: list = field(default_factory=list)  # (turn, winds, damage)
    wind_value: dict = field(default_factory=lambda: {
        "pyro_hits": 0, "hydro_block": 0, "electro_draws": 0,
        "cryo_weak": 0, "pyro_dmg": 0})
    absorbed_this_turn: int = -1  # the turn the last Absorb happened
    turn_rows: list = field(default_factory=list)
    # --- revision two (sec.9) ---
    rev: int = 1
    asc_version: str = "A"
    no_gain: bool = False        # single-Wind runs: Absorbs grant nothing
    fang_want: object = False    # rev 2: True = Absorb; 2.1: "absorb"/"swirl"
    fork: bool = False           # revision 2.1
    winds_set: str = "r2"        # revision 2.2: "W2"
    aim2: object = None          # Grand Master's Order: the repeat's target
    muster_choice2: Optional[str] = None
    asc_reason: Optional[str] = None
    lost: set = field(default_factory=set)        # B: Winds spent by a fire
    recollect: int = 0           # B: a lost Wind Absorbed again
    swirl_log: list = field(default_factory=list)  # (turn, element, card)
    # --- revision 3, the Oath rework (sec.11; `varka_oath`) ---
    oath: dict = field(default_factory=lambda: {
        "pyro": 0, "hydro": 0, "electro": 0, "cryo": 0})
    current: Optional[str] = None     # the element of the last Knight played
    payout: bool = True               # pick 1: the Swirl payout
    apply_oath: bool = True           # pick 2: applying gains Oath
    fang_done: bool = False
    asc_created_turn: int = -1
    oath_log: list = field(default_factory=list)   # (turn, el, n, source)
    turn_oath: list = field(default_factory=list)  # (turn, cur, oath, all)
    asc: list = field(default_factory=list)        # dict per cast
    pay: dict = field(default_factory=lambda: {
        "pyro_dmg": 0, "hydro_block": 0, "cryo_vuln": 0,
        "electro_dmg": 0})
    switches: int = 0
    knights_played: list = field(default_factory=list)
    unbound: int = 0
    unbound_energy: int = 0
    okn: int = 0
    okn_block: int = 0
    okn_rows: list = field(default_factory=list)
    eye_rows: list = field(default_factory=list)
    sworn: int = 0
    # --- revision 3b (third spec update): Oath per card play ---
    per_card: bool = False
    credited: set = field(default_factory=set)
    asc_elemental: bool = False
    pay_electro: int = 2              # Electro payout to ALL per Swirl
    # --- R4, the paper at sec.3-6 HEAD (batch two) ---
    electro_draw: bool = False        # E-Draw: the Electro payout draws 1
    dawn: int = 0                     # Dawn Wind's March stacks
    dawn_block: int = 0
    standard: int = 0                 # Favonian Standard stacks
    standard_block: int = 0
    swirled_ids: set = field(default_factory=set)
    cog_choice: Optional[str] = None  # Change of Guard's element (pilot)
    roll_pool: tuple = ("amber", "barbara", "lisa", "kaeya")
    cog_rows: list = field(default_factory=list)
    tg_rows: list = field(default_factory=list)


def live(state) -> bool:
    return VARKA_PAPER and getattr(state.player, "varka", None) is not None


def vs_of(state) -> Optional[VarkaState]:
    return getattr(state.player, "varka", None) if VARKA_PAPER else None


def held(vs: VarkaState, element: str) -> bool:
    return element in vs.winds


def _wind_on(vs: VarkaState, element: str) -> bool:
    return element in vs.winds and element not in vs.disabled_winds


# --------------------------------------------------------------------------
#  Hooks the shared engine calls (each behind `VARKA_PAPER`)
# --------------------------------------------------------------------------

def bound_aim(state):
    """`effects.bind_card_aim`: the pilot's aim for the card it just chose."""
    vs = vs_of(state)
    if vs is None or vs.aim is None:
        return None
    aim, vs.aim = vs.aim, None
    return aim if aim.alive else None


def attack_bonus(state, card) -> int:
    """`effects.flat_attack_bonus`: Pyro Wind and Stormward Stance."""
    vs = vs_of(state)
    if vs is None or card.type != "attack":
        return 0
    if vs.rev == 3:
        from tier0.engine import varka_oath            # late: cycle
        return varka_oath.attack_bonus(state, vs, card)
    bonus = 0
    if vs.rev == 1 and _wind_on(vs, "pyro"):
        bonus += PYRO_WIND_ATTACK_BONUS
    if (vs.stormward and card.element == ELEMENT
            and len(vs.winds) >= STORMWARD_WINDS):
        bonus += vs.stormward
    return bonus


def _playing_attack(state, vs) -> bool:
    card = vs.playing
    return bool(state.card_aim_bound and card is not None
                and card.type == "attack")


def _fang_can_take(element) -> bool:
    """The relic's Absorb stands in for an Anemo Swirl. An element-less hit
    (a base Strike) or an Anemo hit qualifies; a hit that carries an aura
    element of its own (a Sturm und Drang override) reacts as itself."""
    return element in (None, "none", ELEMENT)


def intercept_hit(state, enemy, element, damage):
    """`reactions.resolve_hit`, first line. Returns the hit's damage when this
    hit is an ABSORB (card or relic), else None and the shared rule runs."""
    vs = vs_of(state)
    if vs is None or vs.landing:
        return None
    if vs.rev == 3:
        # The Oath rework has no Absorb: only count an application.
        from tier0.engine import varka_oath            # late: cycle
        varka_oath.on_hit_pre(state, vs, enemy, element)
        return None
    if vs.rev == 2:
        return _intercept_rev2(state, vs, enemy, element, damage)
    if _playing_attack(state, vs) and _wind_on(vs, "pyro"):
        vs.wind_value["pyro_hits"] += 1      # one +2 per Attack hit
    if not enemy.aura or enemy.aura_spent:
        return None
    if element == enemy.aura:
        return None
    source = None
    if vs.absorb_card and element == ELEMENT and state.card_aim_bound:
        source = "card"
    elif (_playing_attack(state, vs) and vs.fang_turn != state.turn
          and _fang_can_take(element)):
        source = "fang"
        vs.fang_turn = state.turn
    if source is None:
        return None
    from tier0.engine import reactions            # late: cycle
    aura = enemy.aura
    enemy.aura_spent = True
    out = reactions._react(state, enemy, trigger=ELEMENT, aura=aura,
                           damage=damage)
    # THE ABSORB: the aura leaves the enemy it hit. The spread copies the
    # Swirl sent out stay where they landed, spent.
    enemy.aura = None
    enemy.aura_turns_left = 0
    enemy.aura_spent = False
    vs.absorbs.append((state.turn, aura, source))
    vs.absorbed_this_turn = state.turn
    state.emit("varka_absorb", element=aura, target=enemy.name, source=source)
    if aura in WIND_ELEMENTS and aura not in vs.winds:
        vs.winds[aura] = state.turn
        state.emit("varka_wind", element=aura, winds=len(vs.winds))
    return out


def _intercept_rev2(state, vs, enemy, element, damage):
    """Revision two's Absorb: NOT a Swirl (sec.9.1)."""
    if not enemy.aura or enemy.aura_spent or enemy.aura not in WIND_ELEMENTS:
        return None
    if not _playing_attack(state, vs):
        return None                               # Knights are Skills
    aura = enemy.aura
    is_held = held(vs, aura) and not vs.no_gain
    source = None
    if vs.absorb_card and state.card_aim_bound:
        if is_held:
            # sec.9.1: "does only the card's damage". Default reading: the
            # Anemo hit then meets the shared rule (it Swirls).
            return None if (ABSORB_HELD_SWIRLS or vs.fork) else damage
        source = "card"
    elif vs.fork and vs.fang_want and vs.fang_turn != state.turn:
        # 2.1: the Fang is the fork; a held Wind's Absorb Swirls instead.
        swirl = vs.fang_want == "swirl" or is_held
        if swirl:
            if element == ELEMENT:
                return None               # the shared rule Swirls it anyway
            from tier0.engine import reactions    # late: cycle
            vs.fang_turn = state.turn
            enemy.aura_spent = True
            return reactions._react(state, enemy, trigger=ELEMENT, aura=aura,
                                    damage=damage)
        source = "fang"
        vs.fang_turn = state.turn
    elif vs.fang_want and vs.fang_turn != state.turn and not is_held:
        source = "fang"
        vs.fang_turn = state.turn
    if source is None:
        return None
    enemy.aura = None
    enemy.aura_turns_left = 0
    enemy.aura_spent = False
    vs.absorbs.append((state.turn, aura, source))
    vs.absorbed_this_turn = state.turn
    state.emit("varka_absorb", element=aura, target=enemy.name, source=source)
    if not vs.no_gain and aura not in vs.winds:
        if aura in vs.lost:
            vs.recollect += 1
        vs.winds[aura] = state.turn
        state.emit("varka_wind", element=aura, winds=len(vs.winds))
    return damage                                 # the card's own damage


def converging(state) -> bool:
    vs = vs_of(state)
    return bool(vs and vs.converging)


def landing_only(state) -> bool:
    """`reactions._react`'s Overload branch: inside a Converging spread the
    splash lands on the struck enemy only."""
    vs = vs_of(state)
    return bool(vs and vs.landing)


def converging_spread(state, struck, aura, flat: int) -> None:
    """CONVERGING WINDS (paper sec.5.2). Replaces the spread and the flat 2 of
    a Swirl: the struck enemy takes the flat 2 element-less; every other enemy
    takes the flat 2 CARRYING the swirled element. A bare enemy gets a spent
    copy; an enemy already wearing it gets only the 2; an enemy wearing a
    different aura reacts with it, on that enemy alone, and never Swirls."""
    from tier0.engine import reactions            # late: cycle
    vs = vs_of(state)
    reactions._splash(state, struck, flat)
    for other in list(state.living_enemies):
        if other is struck:
            continue
        if other.aura == aura:
            reactions._splash(state, other, flat)
            continue
        bare = other.aura is None
        vs.landing = True
        try:
            dmg = reactions.resolve_hit(state, other, aura, flat,
                                        "converging_spread")
        finally:
            vs.landing = False
        if bare:
            other.aura_spent = True
        reactions._splash(state, other, int(dmg))


def on_swirl(state, enemy, aura) -> None:
    """Every Swirl (plain or Absorb): the Winds' per-Swirl effects."""
    vs = vs_of(state)
    if vs is None:
        return
    if vs.rev == 3:
        from tier0.engine import varka_oath            # late: cycle
        varka_oath.on_swirl(state, vs, enemy, aura)
        return
    vs.swirls += 1
    vs.swirls_this_card += 1
    vs.swirl_log.append((state.turn, aura, vs.playing.id
                         if vs.playing is not None else None))
    p = state.player
    if vs.rev == 2:
        _on_swirl_rev2(state, vs, enemy)
        return
    if _wind_on(vs, "hydro"):
        p.block += HYDRO_WIND_BLOCK
        vs.wind_value["hydro_block"] += HYDRO_WIND_BLOCK
        state.emit("block", amount=HYDRO_WIND_BLOCK)
    if _wind_on(vs, "electro") and vs.electro_turn != state.turn:
        vs.electro_turn = state.turn
        state.draw(ELECTRO_WIND_DRAW)
        vs.wind_value["electro_draws"] += ELECTRO_WIND_DRAW
    if _wind_on(vs, "cryo") and enemy.alive:
        from tier0.engine import powers           # late: cycle
        powers.apply_power(state, enemy, "weak", CRYO_WIND_WEAK)
        vs.wind_value["cryo_weak"] += CRYO_WIND_WEAK


def _on_swirl_rev2(state, vs, enemy) -> None:
    """sec.9.2: every Wind pays on a Swirl."""
    from tier0.engine import powers, reactions    # late: cycle
    p = state.player
    w2 = vs.winds_set == "W2"
    if _wind_on(vs, "pyro"):
        hit = (list(state.living_enemies) if w2
               else [enemy] if enemy.alive else [])
        amount = W2_PYRO_SWIRL_DAMAGE_ALL if w2 else R2_PYRO_SWIRL_DAMAGE
        for e in hit:
            reactions._splash(state, e, amount)
            vs.wind_value["pyro_dmg"] += amount
        if hit:
            vs.wind_value["pyro_hits"] += 1
    if _wind_on(vs, "hydro"):
        blk = W2_HYDRO_BLOCK if w2 else R2_HYDRO_BLOCK
        p.block += blk
        vs.wind_value["hydro_block"] += blk
        state.emit("block", amount=blk)
    if _wind_on(vs, "electro") and vs.electro_turn != state.turn:
        vs.electro_turn = state.turn
        n = W2_ELECTRO_DRAW if w2 else R2_ELECTRO_DRAW
        state.draw(n)
        vs.wind_value["electro_draws"] += n
    if _wind_on(vs, "cryo") and enemy.alive:
        powers.apply_power(state, enemy, "weak", R2_CRYO_WEAK)
        vs.wind_value["cryo_weak"] += R2_CRYO_WEAK


# --------------------------------------------------------------------------
#  The one op: {op: varka, kind: ...}
# --------------------------------------------------------------------------

def _dmg_fx(amount, target="enemy", times=1):
    return {"op": "damage", "amount": amount, "target": target,
            "applies_element": True, "times": times}


def _classify(target, element) -> str:
    if target.aura is None:
        return "painted"
    if target.aura == element:
        return "refreshed"
    return "reacted_spent" if target.aura_spent else "reacted_fresh"


def muster_default(state, vs) -> str:
    for el in WIND_ELEMENTS:
        if el not in vs.winds:
            return el
    return "pyro"


def op_varka(state, fx, card) -> None:
    from tier0.engine import effects              # late: cycle
    vs = vs_of(state)
    kind = fx["kind"]
    if kind == "absorb_begin":
        vs.absorb_card = True
    elif kind == "absorb_end":
        vs.absorb_card = False
    elif kind == "count_begin":
        vs.swirls_this_card = 0
    elif kind == "draw_if_swirled":
        if vs.swirls_this_card:
            state.draw(fx.get("amount", 1))
    elif kind == "ascension":
        per = (ASCENSION_B_PER_WIND if vs.asc_version == "B"
               else ASCENSION_PER_WIND)
        n = len(vs.winds)
        amount = ASCENSION_BASE + per * n
        mark = len(state.log)
        effects._op_damage(state, _dmg_fx(amount), card)
        dealt = sum(r.get("amount", 0) for r in state.log[mark:]
                    if r.get("event") == "damage")
        vs.ascension.append((state.turn, n, dealt) if vs.rev == 1
                            else (state.turn, n, dealt, vs.asc_reason))
        if vs.asc_version == "B" and not vs.no_gain:
            vs.lost |= set(vs.winds)              # "You lose those Winds."
            vs.winds.clear()
    elif kind == "gale_sweep":
        targets = [(e, e.aura) for e in state.living_enemies
                   if e.aura and not e.aura_spent]
        for e, snap in targets:
            if e.alive and vs.rev >= 2 and (e.aura != snap or e.aura_spent):
                # sec.9.6: the snapshot stands; an earlier Swirl's spread
                # in this sweep does not cancel this one.
                from tier0.engine import reactions    # late: cycle
                e.aura = snap
                e.aura_spent = False
                e.aura_turns_left = max(e.aura_turns_left,
                                        reactions.aura_duration(state))
            if e.alive:
                effects.deal_damage_to_enemy(
                    state, e, fx["amount"] + state.current_attack_bonus,
                    element=ELEMENT, source="attack")
    elif kind == "wind_wall":
        amount = fx["amount"] + (fx["bonus"] if vs.winds else 0)
        effects._op_block(state, {"op": "block", "amount": amount}, card)
    elif kind == "gmo":
        vs.gmo_pending += 1
    elif kind == "stormward":
        vs.stormward += STORMWARD_BONUS
    elif kind == "converging":
        vs.converging = True
    elif kind == "knight":
        times = 1
        if vs.gmo_pending:
            vs.gmo_pending -= 1
            times = 2
        saved_aim = state.card_aim
        if vs.rev == 3:
            # sec.11.1: the current element is the last Knight played.
            from tier0.engine import varka_oath        # late: cycle
            varka_oath.set_current(state, vs, fx["element"])
        for i in range(times):
            element = fx["element"]
            if element == "choose":
                choice = vs.muster_choice
                if i == 1 and vs.rev == 2 and vs.muster_choice2:
                    choice = vs.muster_choice2   # sec.9.6: may differ
                element = choice or muster_default(state, vs)
            if (i == 1 and vs.rev == 2 and vs.aim2 is not None
                    and vs.aim2.alive):
                state.card_aim = vs.aim2
            targets = (list(state.living_enemies) if fx.get("all")
                       else [state.card_aim] if state.card_aim is not None
                       and state.card_aim.alive else [])
            after = vs.absorbed_this_turn == state.turn
            for t in targets:
                vs.knight_hits.append((state.turn, after, element,
                                       _classify(t, element), held(vs, element)))
            saved = card.element
            card.element = element
            try:
                effects._resolve_effects(state, fx["inner"], card)
            finally:
                card.element = saved
        state.card_aim = saved_aim
        vs.muster_choice = None
        vs.muster_choice2 = None
        vs.aim2 = None
    else:
        raise ValueError(f"unknown varka kind {kind!r}")


# --------------------------------------------------------------------------
#  Cards (sim-side defs; never in the loader's index)
# --------------------------------------------------------------------------

def _v(kind, **kw):
    return {"op": "varka", "kind": kind, **kw}


def _card(cid, name, cost, ctype, rarity, effects_, element=ELEMENT,
          exhaust=False, knight=False):
    from tier0.engine.state import Card
    return Card(id=f"varka_{cid}", name=name, cost=cost, type=ctype,
                rarity=rarity, element=element, effects=effects_,
                exhaust=exhaust, character=CHARACTER,
                role_c="applier" if knight else None,
                tags=["knight"] if knight else [])


def _knight(cid, name, element, inner, all_=False, rarity="common"):
    return _card(cid, name, 1, "skill", rarity,
                 [_v("knight", element=element, inner=inner, all=all_)],
                 element=element if element != "choose" else "none",
                 knight=True)


CARD_BUILDERS = {
    "knights_muster": lambda: _knight(
        "knights_muster", "Knights' Muster", "choose", [_dmg_fx(4)],
        rarity="basic"),
    "four_winds_ascension": lambda: _card(
        "four_winds_ascension", "Four Winds' Ascension", 2, "attack", "basic",
        [_v("ascension")], exhaust=True),
    "windbound_execution": lambda: _card(
        "windbound_execution", "Windbound Execution", 1, "attack", "common",
        [_v("absorb_begin"), _dmg_fx(6), _v("absorb_end")]),
    "squall": lambda: _card("squall", "Squall", 1, "attack", "common",
                            [_dmg_fx(4, times=2)]),
    "gale_sweep": lambda: _card("gale_sweep", "Gale Sweep", 1, "attack",
                                "common", [_v("gale_sweep", amount=3)]),
    "wind_wall": lambda: _card("wind_wall", "Wind Wall", 1, "skill", "common",
                               [_v("wind_wall", amount=7, bonus=3)]),
    "amber": lambda: _knight("amber", "Amber - Baron Bunny", "pyro",
                             [_dmg_fx(6)]),
    "barbara": lambda: _knight(
        "barbara", "Barbara - Let the Show Begin", "hydro",
        [{"op": "apply_aura", "element": "hydro", "target": "all_enemies"},
         {"op": "block", "amount": 3}], all_=True),
    "lisa": lambda: _knight("lisa", "Lisa - Violet Arc", "electro",
                            [_dmg_fx(5), {"op": "draw", "amount": 1}]),
    "kaeya": lambda: _knight("kaeya", "Kaeya - Frostgnaw", "cryo",
                             [_dmg_fx(6)]),
    "tempest_charge": lambda: _card(
        "tempest_charge", "Tempest Charge", 1, "attack", "uncommon",
        [_v("count_begin"), _dmg_fx(8), _v("draw_if_swirled", amount=1)]),
    "grand_masters_order": lambda: _card(
        "grand_masters_order", "Grand Master's Order", 0, "skill", "uncommon",
        [_v("gmo")], exhaust=True),
    "stormward_stance": lambda: _card(
        "stormward_stance", "Stormward Stance", 1, "power", "uncommon",
        [_v("stormward")]),
    "favonius_cut": lambda: _card(
        "favonius_cut", "Favonius Cut", 2, "attack", "uncommon",
        [_v("absorb_begin"), _dmg_fx(14), _v("absorb_end")]),
    "converging_winds": lambda: _card(
        "converging_winds", "Converging Winds", 2, "power", "rare",
        [_v("converging")]),
}

KNIGHT_IDS = ("varka_knights_muster", "varka_amber", "varka_barbara",
              "varka_lisa", "varka_kaeya")
ABSORB_IDS = ("varka_windbound_execution", "varka_favonius_cut")

STARTER = (["strike"] * 4 + ["defend"] * 4
           + ["knights_muster", "four_winds_ascension"])
STURM = "proto_mc_varka_sturm_und_drang"


def make_card(name: str):
    if name in CARD_BUILDERS:
        return CARD_BUILDERS[name]()
    from tier0.content import loader
    return loader.get_card(name)


def build_player(extra: list[str] = (), disabled_winds=frozenset(),
                 rev: int = 1, asc_version: str = "A", fixed_winds=None,
                 fork: bool = False, winds_set: str = "r2",
                 muster_cost=None):
    """A fresh Varka for one fight: the starter plus `extra`, the relic's
    state on the Player. Boreas's Fang has no hook id: it is the arm's rule,
    read by `intercept_hit` for every Varka. `rev=2` is sec.9; `asc_version`
    "B" makes Ascension sec.9.5's B (revision two only); `fixed_winds` holds
    those Winds from turn 1 and turns Absorb gains off (single-Wind runs)."""
    from tier0.engine.state import Player
    if (asc_version != "A" or fork or winds_set != "r2"
            or muster_cost is not None) and rev != 2:
        raise ValueError("Ascension B and the 2.1 fork are revision two")
    cards = [make_card(n) for n in list(STARTER) + list(extra)]
    if muster_cost is not None:
        for c in cards:
            if c.id == "varka_knights_muster":
                c.cost = muster_cost
    if asc_version == "B":
        for c in cards:
            if c.id == "varka_four_winds_ascension":
                c.exhaust = False
    player = Player(hp=HP, max_hp=HP, draw_pile=cards, element=ELEMENT,
                    cadence="catalyst", character_id=CHARACTER)
    vs = VarkaState(disabled_winds=frozenset(disabled_winds), rev=rev,
                    asc_version=asc_version, fork=fork,
                    winds_set=winds_set)
    if fixed_winds is not None:
        vs.winds = {el: 0 for el in fixed_winds}
        vs.no_gain = True
    player.varka = vs
    return player


def turn_start(state) -> None:
    """`combat` post-draw turn start: the Oath rework's start-of-turn Powers
    (Oath of the Knights, Sworn Brotherhood). Nothing for revisions 1-2."""
    vs = vs_of(state)
    if vs is not None and vs.rev == 3:
        from tier0.engine import varka_oath            # late: cycle
        varka_oath.turn_start(state)


def enable() -> None:
    """Turn the arm on for this process: the switch, the op, and the element
    port's Swirl rule the paper assumes (`C.SWIRL_PAYS`, and
    `C.CRYSTALLIZE_KEEPS_AURA` beside it, both ruled)."""
    global VARKA_PAPER
    from tier0 import constants as C
    from tier0.engine import effects
    VARKA_PAPER = True
    C.SWIRL_PAYS = True
    C.CRYSTALLIZE_KEEPS_AURA = True
    effects.OPS["varka"] = op_varka


def disable() -> None:
    global VARKA_PAPER
    from tier0.engine import effects
    VARKA_PAPER = False
    effects.OPS.pop("varka", None)
