"""VARKA, THE OATH REWORK -- the sim's rules, read off the sheet rows.

Design: `review/active/varka-paper-kit-2026-09-28.md` (every pick ruled
2026-09-29). Rows: the `proto_vk_` block of `docs/prototype-surface.yaml`.
C# twin: `klee-mod/KleeCode/Powers/Prototype/VarkaOath.cs` (`VarkaLaw`,
`VarkaOath`, `VarkaCards`).

THE SWITCH. `VARKA_OATH` is a MODULE constant, off, for the reason
`furina_stage.FURINA_STAGE` is one: a sim twin ships off because the
calibration bands are measured on the shipped world, and a prototype's numbers
live here rather than in `constants.py` so they move neither the constant
census nor the world stamp. With it off every hook this module adds to the
shared engine is a dead branch, and with it on every hook is still a dead
branch for any player who is not Varka (`live`). A test fixture flips it.

THE RULES AS MODELLED:
  * OATH: four counts (pyro, hydro, electro, cryo) on a per-fight ledger on
    the Player (`VarkaLedger`), reset at combat start.
  * CURRENT ELEMENT: None until the first KNIGHT (a companion row with
    `personal_pool: varka`). Playing a Knight sets it to the row's element
    BEFORE the card's effects resolve, so its own application credits the new
    current element. Favonian Standard pays on a Knight whose element was
    already current; Boreas Unbound pays on every change (None -> X counts).
  * THE OPEN OATH ([USER], 2026-09-30: "Any card that applies an element
    other than Anemo counts for Oath effects"): inside a play of his own card
    that is NOT a Knight, an application of an Oath element makes it his
    current element before it credits (so Dawn Wind's March pays on it); the
    last one applied wins. A Knight keeps its play-time switch; Baron Bunny's
    burst, a relic, a potion, a power outside a play, a Swirl's spread and a
    Converging Winds landing switch nothing. Knight-named payoffs (Favonian
    Standard, Grand Master's Order, Knightly Guard, Knights' Roll Call) stay
    Knight-only.
  * CREDIT, PER CARD PLAY: within one play, the first application of E to a
    live enemy is +1 Oath of E, and the first Swirl of an E aura is +1 Oath of
    E -- two keys, at most once each per play. A Swirl's spread copies, a
    Converging Winds landing and Four Winds' Ascension's elemental hit credit
    nothing. Outside a card play a scope is opened around the event (Baron
    Bunny's burst); an event with no scope open is its own scope.
  * GAIN EVENTS (any +n): Dawn Wind's March pays Block on a gain of the
    current element; the first gain of the combat has Boreas's Fang add Four
    Winds' Ascension to the hand (the discard pile if the hand is full).
  * SWIRL PAYOUT: every Swirl he makes, after the shared Swirl (spread and the
    flat 2), credits first and then pays his current element.

READINGS TAKEN WHERE THE SPEC LEAVES ROOM (each also in the builder's report):
  * Tier 0 seats one player, so "dealt by Varka" is "the player is Varka":
    every application and Swirl while the seat is his is his.
  * Grand Master's Order: every stack is spent by the next Knight, one replay
    per stack (Study Buddy's accumulator, `combat._finish_play`).
  * Four Winds' Ascension's and Northwind Avatar's elemental hits take the
    card's flat Attack riders (`state.current_attack_bonus`) less Stormward
    Stance's part, because that hit is not Anemo; Strength counts.
  * Change of Guard's choice is the pilot's (`VarkaLedger.guard_choice`),
    default the element with the most Oath, ties in P/H/E/C order. The
    upgraded Knights' Roll Call's choice is `VarkaLedger.knight_choice`,
    default the first pool Knight of the current element, else the first.
  * Gale Sweep and Wall of Gales shield their snapshot: an enemy a sweep's
    earlier Swirl spread over gets its own fresh aura back before its hit.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from tier0 import constants as C

VARKA_OATH = False          # THE SWITCH. Off: every hook is a dead branch.

CHARACTER = "varka"
HP = 80
ELEMENT = "anemo"
ELEMENTS = ("pyro", "hydro", "electro", "cryo")

# --- the Swirl payout of each current element (C# `VarkaLaw`) ---
SWIRL_PYRO_DAMAGE = 3             # to the enemy Swirled, element-less
SWIRL_HYDRO_BLOCK = 3             # Block, unpowered
SWIRL_CRYO_VULNERABLE = 1         # on the enemy Swirled
SWIRL_ELECTRO_DAMAGE_ALL = 3      # to ALL living enemies, element-less
# Stormward Stance: the current element's Oath it asks for.
STORMWARD_OATH_NEEDED = 4

#: The damage source a payout and Baron Bunny's burst carry: his card's, on
#: the unpowered door (`ElementalHit.DealUnelemented(powered: false)`).
PAYOUT_SOURCE = "card"

# --- the powers his rows apply (`apply_power`, target self) ---
STORMWARD = "vk_stormward_stance"
OATH_OF_THE_KNIGHTS = "vk_oath_of_the_knights"
SWORN_BROTHERHOOD = "vk_sworn_brotherhood"
#: Power cost sweep, 2026-09-30: the base card's power, current element only
#: (the upgrade installs SWORN_BROTHERHOOD, every element).
SWORN_BROTHERHOOD_CURRENT = "vk_sworn_brotherhood_current"
BARON_BUNNY = "vk_baron_bunny"
FAVONIAN_STANDARD = "vk_favonian_standard"
DAWN_WINDS_MARCH = "vk_dawn_winds_march"
BOREAS_UNBOUND = "vk_boreas_unbound"
CONVERGING_WINDS = "vk_converging_winds"
GRAND_MASTERS_ORDER = "vk_grand_masters_order"

# --- the relic, as the sim spells a starting relic (`Player.relic_hooks`) ---
FANG = "boreas_fang"
FANG_UPGRADED = "boreas_fang+"

ASCENSION_ID = "proto_vk_four_winds_ascension"
ID_PREFIX = "proto_vk_"

#: One of the four joins the starter at random each run.
STARTER_KNIGHT_IDS = {
    "pyro": "proto_vk_amber_fiery_rain",
    "hydro": "proto_vk_barbara_melody_loop",
    "electro": "proto_vk_lisa_lightning_rose",
    "cryo": "proto_vk_kaeya_glacial_waltz",
}
STARTER_BASE_IDS: tuple[str, ...] = (
    "strike", "strike", "strike", "strike",
    "defend", "defend", "defend", "defend",
    "proto_vk_windbound_execution",
)

#: The `varka` op's kinds (C# `VarkaCards.<Method>`, the codegen's
#: `VARKA_KINDS`), and the numeric fields each one prints.
KINDS = frozenset({
    "apply_current_element", "gain_current_oath", "ascension_hit",
    "avatar_hit", "swirled_take_more", "swirl_fresh_auras",
    "oath_per_cryo_enemy", "change_of_guard", "rally", "accord",
    "unfurled_banner",
})
KIND_FIELDS = {
    "ascension_hit": ("per",),
    "avatar_hit": ("base", "per"),
    "swirled_take_more": ("amount",),
}
OP_FIELDS = frozenset({"op", "kind", "target", "per", "base", "amount"})

COUNTS = frozenset({"current_oath", "oath_elements"})
PREDICATES = frozenset({"has_current_element", "knight_played_this_turn",
                        "swirled_by_this"})


@dataclass
class VarkaLedger:
    """Per-fight state, hung on the Player (`Player.varka_ledger`)."""
    oath: dict = field(default_factory=lambda: {el: 0 for el in ELEMENTS})
    current: Optional[str] = None
    fang_fired: bool = False
    #: The open credit scopes, innermost last: one set of ("apply"|"swirl",
    #: element) keys per card play (or per scoped event).
    scopes: list = field(default_factory=list)
    #: Per play, parallel to `scopes`: the Swirls this play made and the
    #: enemies they struck (`swirled_by_this`, Storm Surge).
    play_swirls: list = field(default_factory=list)
    #: Per play, parallel to `scopes`: is it an open-Oath play (his own
    #: non-Knight card), whose applications set the current element.
    play_open: list = field(default_factory=list)
    swirls_made: int = 0              # this combat
    knights_this_turn: int = 0        # Knight plays this turn, replays too
    no_apply_credit: int = 0          # > 0 inside a hit that credits nothing
    landing: bool = False             # inside a Converging Winds spread
    stormward_in_bonus: int = 0       # Stormward's part of this play's bonus
    # --- the pilot's choices (None: the default reading) ---
    guard_choice: Optional[str] = None
    knight_choice: Optional[str] = None


# --------------------------------------------------------------------------
#  Who is Varka
# --------------------------------------------------------------------------

def live(player) -> bool:
    """The switch is on and this Player is Varka."""
    return (VARKA_OATH
            and getattr(player, "character_id", "") == CHARACTER)


def ledger(player) -> Optional[VarkaLedger]:
    """His ledger, made on first use; None for anyone else or switch off."""
    if not live(player):
        return None
    led = getattr(player, "varka_ledger", None)
    if led is None:
        led = VarkaLedger()
        player.varka_ledger = led
    return led


def open_combat(player) -> None:
    """`combat.run_fight`: a fresh ledger per fight."""
    if live(player):
        player.varka_ledger = VarkaLedger()


def is_knight(card) -> bool:
    return (getattr(card, "personal_pool", None) == CHARACTER
            and card.is_companion
            and getattr(card, "element", "none") in ELEMENTS)


def current_oath(player) -> int:
    led = ledger(player)
    if led is None or led.current is None:
        return 0
    return led.oath[led.current]


def oath_elements(player) -> int:
    led = ledger(player)
    return 0 if led is None else sum(1 for v in led.oath.values() if v > 0)


def _power(player, name: str) -> int:
    return int(player.powers.get(name, 0))


def _block(state, amount: int, reason: str) -> None:
    """Unpowered Block (no Dexterity, no Frail), the payouts' door."""
    if amount <= 0:
        return
    state.player.block += amount
    state.emit("block", amount=amount)
    state.emit("varka_block", amount=amount, reason=reason)


# --------------------------------------------------------------------------
#  Oath: gain events and per-play credit
# --------------------------------------------------------------------------

def gain(state, element: str, n: int = 1, source: str = "gain") -> None:
    """One GAIN EVENT of `n` Oath of `element`."""
    led = ledger(state.player)
    if led is None or element not in ELEMENTS or n <= 0:
        return
    led.oath[element] += n
    state.emit("varka_oath", element=element, amount=n, source=source,
               total=led.oath[element])
    p = state.player
    if element == led.current:
        _block(state, _power(p, DAWN_WINDS_MARCH), "dawn_winds_march")
    if not led.fang_fired and (FANG in p.relic_hooks
                               or FANG_UPGRADED in p.relic_hooks):
        led.fang_fired = True
        _add_ascension(state, upgraded=FANG_UPGRADED in p.relic_hooks)


def _add_ascension(state, upgraded: bool) -> None:
    from tier0.content import loader                # late: cycle
    card = loader.get_card(ASCENSION_ID + ("+" if upgraded else ""))
    # Wolf's Gravestone (the Fang upgraded, 2026-09-30): "It costs 0 this
    # turn." `BoreasFang.AddAscension`'s `SetThisTurn(0)` is the twin.
    card.free_this_turn = upgraded
    p = state.player
    if len(p.hand) < C.MAX_HAND_SIZE:
        p.hand.append(card)
        zone = "hand"
    else:
        p.discard_pile.append(card)
        zone = "discard"
    state.cards_created_this_turn += 1
    state.emit("add_card", card=card.id, to=zone)
    state.emit("varka_fang", card=card.id, to=zone)


def credit(state, kind: str, element: str) -> None:
    """Per-play Oath credit: ("apply"|"swirl", element), once per play."""
    led = ledger(state.player)
    if led is None or element not in ELEMENTS:
        return
    if led.scopes:
        key = (kind, element)
        if key in led.scopes[-1]:
            return
        led.scopes[-1].add(key)
    gain(state, element, 1, kind)


def open_scope(state, open_oath: bool = False) -> None:
    led = ledger(state.player)
    if led is not None:
        led.scopes.append(set())
        led.play_swirls.append([])
        led.play_open.append(open_oath)


def close_scope(state) -> None:
    led = ledger(state.player)
    if led is not None and led.scopes:
        led.scopes.pop()
        led.play_swirls.pop()
        if led.play_open:
            led.play_open.pop()


#: The open Oath's switch (module, so a paired sim can run the old rule).
OPEN_OATH = True


def open_oath_switches(led: VarkaLedger, element: str) -> bool:
    """Does this application make `element` current? Only inside an
    open-Oath play, for an Oath element, outside a no-credit hit."""
    return bool(OPEN_OATH and led.play_open and led.play_open[-1]
                and element in ELEMENTS and not led.no_apply_credit
                and not led.landing)


# --------------------------------------------------------------------------
#  The current element
# --------------------------------------------------------------------------

def set_current(state, element: str, knight: bool) -> None:
    led = ledger(state.player)
    if led is None or element not in ELEMENTS:
        return
    p = state.player
    if knight and element == led.current:
        _block(state, _power(p, FAVONIAN_STANDARD), "favonian_standard")
    if element != led.current:
        led.current = element
        state.emit("varka_current", element=element, knight=knight)
        n = _power(p, BOREAS_UNBOUND)
        if n:
            p.energy += n
            state.emit("varka_unbound", energy=n)


# --------------------------------------------------------------------------
#  Hooks the shared engine calls (each behind `VARKA_OATH`)
# --------------------------------------------------------------------------

def begin_play(state, card) -> None:
    """`effects.resolve_card`, after the bind: open this play's scope, and a
    Knight sets the current element before its effects resolve."""
    led = ledger(state.player)
    if led is None:
        return
    open_scope(state, open_oath=not is_knight(card))
    if is_knight(card):
        led.knights_this_turn += 1
        set_current(state, card.element, knight=True)


def end_play(state) -> None:
    close_scope(state)


def note_hit(state, enemy, element) -> None:
    """`reactions.resolve_hit`, first line: an application of an element to
    a live enemy credits apply-Oath (whether it sticks, refreshes or reacts).
    """
    led = ledger(state.player)
    if (led is None or element not in ELEMENTS or not enemy.alive
            or led.landing or led.no_apply_credit):
        return
    if open_oath_switches(led, element):
        set_current(state, element, knight=False)
    credit(state, "apply", element)


def converging(state) -> bool:
    led = ledger(state.player)
    return bool(led is not None and _power(state.player, CONVERGING_WINDS))


def landing_only(state) -> bool:
    """`reactions._react`'s Overload branch: inside a Converging spread the
    splash lands on the struck enemy only."""
    led = ledger(state.player)
    return bool(led is not None and led.landing)


def converging_spread(state, struck, aura: str, flat: int) -> None:
    """CONVERGING WINDS: replaces the Swirl's spread and flat 2. The struck
    enemy takes the flat 2 element-less; every other enemy takes it CARRYING
    the swirled element: a bare one gets a spent copy, one already wearing it
    only the 2, and one wearing another aura reacts with it, on that enemy
    alone, and never Swirls. Nothing here credits Oath."""
    from tier0.engine import reactions              # late: cycle
    led = ledger(state.player)
    reactions._splash(state, struck, flat)
    for other in list(state.living_enemies):
        if other is struck:
            continue
        if other.aura == aura:
            reactions._splash(state, other, flat)
            continue
        bare = other.aura is None
        led.landing = True
        try:
            dmg = reactions.resolve_hit(state, other, aura, flat,
                                        "converging_spread")
        finally:
            led.landing = False
        if bare:
            other.aura_spent = True
        reactions._splash(state, other, int(dmg))


def on_swirl(state, enemy, aura: str) -> None:
    """`reactions._react`, after the shared Swirl: count it, credit it, then
    pay his current element."""
    from tier0.engine import effects, powers        # late: cycle
    led = ledger(state.player)
    if led is None:
        return
    led.swirls_made += 1
    if led.play_swirls:
        led.play_swirls[-1].append(enemy)
    state.emit("varka_swirl", element=aura, target=enemy.name,
               current=led.current)
    credit(state, "swirl", aura)
    cur = led.current
    if cur == "pyro":
        if enemy.alive:
            effects.deal_damage_to_enemy(state, enemy, SWIRL_PYRO_DAMAGE,
                                         element=None, source="card",
                                         powered=False)
    elif cur == "hydro":
        _block(state, SWIRL_HYDRO_BLOCK, "swirl_hydro")
    elif cur == "cryo":
        if enemy.alive:
            powers.apply_power(state, enemy, "vulnerable",
                               SWIRL_CRYO_VULNERABLE)
    elif cur == "electro":
        for e in list(state.living_enemies):
            effects.deal_damage_to_enemy(state, e, SWIRL_ELECTRO_DAMAGE_ALL,
                                         element=None, source="card",
                                         powered=False)


def card_hits_anemo(state, card) -> bool:
    """Is this card's (first) hit Anemo? Stormward Stance's 'Anemo Attacks'."""
    from tier0.engine import effects                # late: cycle
    for fx in card.effects:
        if fx.get("op") == "damage" and fx.get("target") != "self":
            return effects._element_for(state, fx, card) == ELEMENT
    return False


def attack_bonus(state, card) -> int:
    """`effects.flat_attack_bonus`: Stormward Stance, on a powered Attack
    whose hit is Anemo while his current element's Oath is at the bar."""
    p = state.player
    if (ledger(p) is None or card.type != "attack"
            or not _power(p, STORMWARD)
            or current_oath(p) < STORMWARD_OATH_NEEDED
            or not card_hits_anemo(state, card)):
        return 0
    return _power(p, STORMWARD)


def note_attack_bonus(state, card) -> None:
    """`effects._resolve_card_bound`, beside the bonus snapshot: remember
    Stormward's part, which the elemental follow-up hits do not take."""
    led = ledger(state.player)
    if led is not None:
        led.stormward_in_bonus = attack_bonus(state, card)


def gmo_replays(state, card) -> int:
    """`combat._finish_play`: Grand Master's Order -- the next Knight played
    this turn is played again, once per stack, spending every stack."""
    p = state.player
    if ledger(p) is None or not is_knight(card):
        return 0
    n = int(p.powers.pop(GRAND_MASTERS_ORDER, 0))
    if n:
        state.emit("varka_grand_masters_order", card=card.id, replays=n)
    return n


def turn_start(state) -> None:
    """`combat._player_turn`, post-draw: the per-turn clears, then Baron
    Bunny's burst, Sworn Brotherhood, Oath of the Knights, in that order."""
    from tier0.engine import effects                # late: cycle
    led = ledger(state.player)
    if led is None:
        return
    p = state.player
    led.knights_this_turn = 0
    p.powers.pop(GRAND_MASTERS_ORDER, None)         # "this turn" ran out
    bunny = int(p.powers.pop(BARON_BUNNY, 0))
    if bunny:
        state.emit("varka_baron_bunny", amount=bunny)
        open_scope(state)
        try:
            for e in list(state.living_enemies):
                effects.deal_damage_to_enemy(state, e, bunny, element="pyro",
                                             source="card", powered=False)
        finally:
            close_scope(state)
    sworn = _power(p, SWORN_BROTHERHOOD)
    if sworn:
        for el in ELEMENTS:
            gain(state, el, sworn, "sworn_brotherhood")
    sworn_current = _power(p, SWORN_BROTHERHOOD_CURRENT)
    led_now = ledger(p)
    if sworn_current and led_now is not None and led_now.current is not None:
        gain(state, led_now.current, sworn_current, "sworn_brotherhood")
    okn = _power(p, OATH_OF_THE_KNIGHTS)
    if okn:
        _block(state, current_oath(p) * okn, "oath_of_the_knights")


# --------------------------------------------------------------------------
#  Readers: counts and predicates
# --------------------------------------------------------------------------

def count(state, token: str) -> int:
    if token == "current_oath":
        return current_oath(state.player)
    if token == "oath_elements":
        return oath_elements(state.player)
    raise ValueError(f"not a Varka count: {token!r}")


def predicate(state, name: str) -> bool:
    led = ledger(state.player)
    if led is None:
        return False
    if name == "has_current_element":
        return led.current is not None
    if name == "knight_played_this_turn":
        return led.knights_this_turn > 0
    if name == "swirled_by_this":
        return bool(led.play_swirls and led.play_swirls[-1])
    raise ValueError(f"not a Varka predicate: {name!r}")


# --------------------------------------------------------------------------
#  Gale Sweep: `damage` with `only_if: fresh_aura`
# --------------------------------------------------------------------------

def _fresh_snapshot(state) -> list:
    return [(e, e.aura, e.aura_turns_left) for e in state.living_enemies
            if e.aura and not e.aura_spent]


def _restore(e, aura: str, turns: int) -> None:
    if e.aura != aura or e.aura_spent:
        e.aura = aura
        e.aura_spent = False
        e.aura_turns_left = max(e.aura_turns_left, turns)


def fresh_aura_sweep(state, fx: dict, card) -> None:
    """`effects._op_damage`, for a `damage` op carrying `only_if:
    fresh_aura`: the enemies wearing a fresh aura when the op resolves, each
    hit once through the ordinary damage op aimed at its body (so the card's
    Anemo, Strength and Stormward land as on any hit of his)."""
    from tier0.engine import effects, klee_overhaul  # late: cycle
    hit = {k: v for k, v in fx.items() if k != "only_if"}
    hit["target"] = "enemy"
    for e, aura, turns in _fresh_snapshot(state):
        if not e.alive:
            continue
        _restore(e, aura, turns)
        with klee_overhaul.aimed_at(state, e):
            effects._op_damage(state, hit, card)


# --------------------------------------------------------------------------
#  The ops: `varka` (one kind per rule) and `add_knight`
# --------------------------------------------------------------------------

def _refuse(what: str) -> None:
    raise NotImplementedError(
        f"{what} is VARKA's (tier0/engine/varka_oath.py) and resolves only "
        "for a Varka seat with `varka_oath.VARKA_OATH` on; no shipped row "
        "prints it, so reaching this is a defect rather than a degradation.")


def validate_op(card_id: str, fx: dict) -> None:
    """The loader's shape check for one `varka` op, AT LOAD."""
    kind = fx.get("kind")
    if kind not in KINDS:
        raise ValueError(f"card {card_id!r}: unknown varka kind {kind!r}")
    unknown = set(fx) - OP_FIELDS
    if unknown:
        raise ValueError(
            f"card {card_id!r}: varka {kind!r} has unknown fields "
            f"{sorted(unknown)}")
    want = set(KIND_FIELDS.get(kind, ()))
    have = set(fx) & {"per", "base", "amount"}
    if want != have:
        raise ValueError(
            f"card {card_id!r}: varka {kind!r} takes the fields "
            f"{sorted(want)}, got {sorted(have)}")
    for key in want:
        if not isinstance(fx[key], int) or fx[key] < 0:
            raise ValueError(
                f"card {card_id!r}: varka {kind!r} `{key}` must be a "
                f"non-negative int, got {fx[key]!r}")
    if "target" in fx and (kind != "apply_current_element"
                           or fx["target"] != "enemy"):
        raise ValueError(
            f"card {card_id!r}: varka {kind!r} takes no target "
            f"{fx['target']!r}")


def _elemental_follow_up(state, card, amount: int, credits: bool) -> None:
    """Ascension's and Northwind Avatar's second hit: `amount` carrying the
    current element into the play's target, a powered card hit."""
    from tier0.engine import effects                # late: cycle
    led = ledger(state.player)
    target = state.card_aim
    if (led.current is None or target is None or not target.alive
            or amount <= 0):
        return
    amount += max(0, state.current_attack_bonus - led.stormward_in_bonus)
    source = "attack" if card.type == "attack" else "card"
    if not credits:
        led.no_apply_credit += 1
    try:
        effects.deal_damage_to_enemy(state, target, amount,
                                     element=led.current, source=source)
    finally:
        if not credits:
            led.no_apply_credit -= 1


def op_varka(state, fx: dict, card) -> None:
    """`effects.OPS['varka']`."""
    from tier0.engine import effects, reactions     # late: cycle
    led = ledger(state.player)
    if led is None:
        _refuse(f"op 'varka' ({fx.get('kind')!r}) on {card.id!r}")
    kind = fx["kind"]
    p = state.player
    if kind == "apply_current_element":
        if led.current is None:
            return
        for e in effects._pick_targets(state, fx.get("target", "enemy"),
                                       allow_dead=True):
            reactions.resolve_hit(state, e, led.current, 0, "apply_aura_op")
    elif kind == "gain_current_oath":
        if led.current is not None:
            gain(state, led.current, 1, "gain_current_oath")
    elif kind == "ascension_hit":
        if led.current is not None:
            _elemental_follow_up(state, card,
                                 fx["per"] * current_oath(p), credits=False)
    elif kind == "avatar_hit":
        if led.current is not None:
            _elemental_follow_up(
                state, card, fx["base"] + fx["per"] * current_oath(p),
                credits=True)
    elif kind == "swirled_take_more":
        struck = led.play_swirls[-1] if led.play_swirls else []
        seen: set = set()
        for e in state.enemies:
            if id(e) in seen or not any(e is s for s in struck):
                continue
            seen.add(id(e))
            if e.alive:
                effects.deal_damage_to_enemy(
                    state, e, fx["amount"], element=None,
                    source="attack" if card.type == "attack" else "card")
    elif kind == "swirl_fresh_auras":
        for e, aura, turns in _fresh_snapshot(state):
            if not e.alive:
                continue
            _restore(e, aura, turns)
            reactions.resolve_hit(state, e, ELEMENT, 0, "swirl_op")
    elif kind == "oath_per_cryo_enemy":
        n = sum(1 for e in state.living_enemies if e.aura == "cryo")
        if n:
            gain(state, "cryo", n, "oath_per_cryo_enemy")
    elif kind == "change_of_guard":
        held = [el for el in ELEMENTS if led.oath[el] > 0]
        if not held:
            return
        choice = led.guard_choice if led.guard_choice in held else None
        led.guard_choice = None
        if choice is None:
            choice = max(held, key=lambda el: (led.oath[el],
                                               -ELEMENTS.index(el)))
        set_current(state, choice, knight=False)    # the draw is the row's op
    elif kind == "rally":
        if led.current is not None:
            total = sum(led.oath.values())
            led.oath = {el: 0 for el in ELEMENTS}
            led.oath[led.current] = total
            state.emit("varka_rally", element=led.current, total=total)
    elif kind == "accord":
        each = sum(led.oath.values()) // 4
        led.oath = {el: each for el in ELEMENTS}
        state.emit("varka_accord", each=each)
        for el in ELEMENTS:
            gain(state, el, 1, "accord")
    elif kind == "unfurled_banner":
        if len(p.hand) >= C.MAX_HAND_SIZE:
            return
        for i, c in enumerate(p.discard_pile):
            if c.id.rstrip("+") == ASCENSION_ID:
                p.discard_pile.pop(i)
                c.free_this_turn = True
                p.hand.append(c)
                state.emit("varka_unfurled_banner", card=c.id)
                return
    else:
        raise ValueError(f"card {card.id!r}: unknown varka kind {kind!r}")


def pool_knight_ids() -> list[str]:
    """Knights' Roll Call's pool: every Knight row that is not a starter
    (rarity basic), in sheet order."""
    from tier0.content import loader                # late: cycle
    return [c.id for c in loader.prototype_cards()
            if c.id.startswith(ID_PREFIX) and is_knight(c)
            and c.rarity != "basic"]


def op_add_knight(state, fx: dict, card) -> None:
    """`effects.OPS['add_knight']`: Knights' Roll Call. A random pool Knight
    (upgraded, `choose: true`, the pilot's pick) into the hand, 0 this turn.
    """
    from tier0.content import loader                # late: cycle
    from tier0.engine import effects                # late: cycle
    led = ledger(state.player)
    if led is None:
        _refuse(f"op 'add_knight' on {card.id!r}")
    pool = pool_knight_ids()
    if not pool:
        return
    if fx.get("choose"):
        pick = led.knight_choice if led.knight_choice in pool else None
        led.knight_choice = None
        if pick is None:
            pick = next((cid for cid in pool
                         if loader.peek_card(cid).element == led.current),
                        pool[0])
    else:
        pick = state.rng.choice(pool)
    knight = loader.get_card(pick)
    knight.free_this_turn = True
    effects._add_token(state, knight, "hand")


# --------------------------------------------------------------------------
#  A fresh Varka for one fight
# --------------------------------------------------------------------------

def starter_ids(element: str) -> list[str]:
    """The starter: base Strike x4, Defend x4, Windbound Execution, and the
    starter Knight of `element`."""
    return list(STARTER_BASE_IDS) + [STARTER_KNIGHT_IDS[element]]


def build_player(element: Optional[str] = None, rng=None,
                 extra: tuple = (), hp: Optional[int] = None,
                 fang: bool = True, fang_upgraded: bool = False):
    """A fresh Varka combat Player (80 HP) holding the starter, `extra` card
    ids, and Boreas's Fang. `element` picks the starter Knight; None rolls it
    with `rng` (a `random.Random`, e.g. the run's), as the C# Fang re-rolls
    the dealt Knight on `AfterObtained`. Needs the switch on (the `proto_vk_`
    rows resolve through the loader's flagged door)."""
    from tier0.content import loader                # late: cycle
    from tier0.engine.state import Player
    if not VARKA_OATH:
        raise RuntimeError("varka_oath.build_player needs VARKA_OATH on")
    if element is None:
        if rng is None:
            raise ValueError("pass `element` or an `rng` to roll one")
        element = rng.choice(ELEMENTS)
    if element not in STARTER_KNIGHT_IDS:
        raise ValueError(f"no starter Knight of {element!r}")
    ids = starter_ids(element) + list(extra)
    cards = [loader.get_card(cid) for cid in ids]
    hp = HP if hp is None else hp
    player = Player(hp=hp, max_hp=max(hp, HP), draw_pile=cards,
                    element=ELEMENT, cadence="catalyst",
                    character_id=CHARACTER)
    if fang or fang_upgraded:
        player.relic_hooks.append(FANG_UPGRADED if fang_upgraded else FANG)
    player.varka_ledger = VarkaLedger()
    return player
