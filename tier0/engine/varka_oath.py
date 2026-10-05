"""VARKA, THE OATH REWORK -- the sim's rules, read off the sheet rows.

Design: `review/active/varka-paper-kit-2026-09-28.md` (every pick ruled
2026-09-29). Rows: the `proto_vk_` block of `docs/prototype-surface.yaml`.
C# twin: `klee-mod/KleeCode/Powers/Prototype/VarkaOath.cs` (`VarkaLaw`,
`VarkaOath`, `VarkaCards`).

NO SWITCH (collapsed 2026-10-01, legacy cleanup stage 2): he ships nowhere
else, so there is no shipped world to switch back to. Every hook this module
adds to the shared engine is a dead branch for any player who is not Varka
(`live`). His numbers live here rather than in `constants.py` so they move
neither the constant census nor the world stamp.

THE RULES AS MODELLED:
  * OATH: four counts (pyro, hydro, electro, cryo) on a per-fight ledger on
    the Player (`VarkaLedger`), reset at combat start.
  * CURRENT ELEMENT: None until the first KNIGHT (a companion row with
    `personal_pool: varka`). Playing a Knight sets it to the row's element
    BEFORE the card's effects resolve, so its own application credits the new
    current element. Boreas Unbound pays on every change (None -> X counts).
    Since the Varka defence paper (sec.4) Boreas's Fang makes the starter
    Knight's element current on his first turn (`turn_start`).
  * THE OPEN OATH ([USER], 2026-09-30: "Any card that applies an element
    other than Anemo counts for Oath effects"): inside a play of his own card
    that is NOT a Knight, an application of an Oath element makes it his
    current element before it credits (so Dawn Wind's March pays on it); the
    last one applied wins. A Knight keeps its play-time switch; Baron Bunny's
    burst, a relic, a potion, a power outside a play, a Swirl's spread and a
    Converging Winds landing switch nothing. Knight-named payoffs (Grand
    Master's Order, Knightly Guard, Knights' Roll Call) stay Knight-only.
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
    earlier Swirl spread over gets its own aura back before its hit.

ELEMENT IDENTITIES (review/active/varka-element-identities-2026-10-01.md,
ruled 2026-10-01): Electro's discard-and-spend cards and Retaliating Tide.
What it adds here:
  * KINDS `electro_strike` (Charged Lunge), `electro_all` (Chain Lightning),
    `violet_storm` (discard the hand, one random Electro hit per card), and
    Thundering Verdict at X (`state.current_x` hits of the whole row).
  * RETALIATING TIDE (`turn_end`, after Oathbound Aegis): min(Block, Hydro
    Oath) to a random enemy per stack, element-less and unpowered.
  * Accord, Unfurled Banner, `apply_current_element_all` (Pressure Front)
    and Unbroken Tide's kept Block left with their cards.

THE EXPANSION (review/active/varka-expansion-2026-10-01.md sec.3, ruled
2026-10-01): 37 cards and the Knight pass. What it adds here:
  * NOELLE IS A GEO KNIGHT: a Knight for every Knight-played read (Muster,
    Grand Master's Order, Knightly Guard), but Geo is no Oath element, so
    she sets no current element and gains no Oath.
  * KNIGHTS THIS COMBAT (Charge of the Knights), the turn the current element
    last changed (Shifting Gale), Swirls this turn (Eye of Stormterror).
  * THE SWIRL PAYOUT, per element (`_pay`): Absolute Zero (Cryo) widens its
    to ALL enemies (Wildfire Oath's Pyro widening left with element
    identities); Twin Gales pays the element
    Swirled as well (once, when it is the current one); Crosscurrent's Swirl
    pays twice. Eye Wall and Eye of Stormterror read each Swirl.
  * UNWAVERING BANNER stops the open Oath's switch (a Knight's switch and a
    card that names the switch -- Change of Guard, Weathervane -- still
    move it). (Downburst's "copies arrive fresh" went with spent auras,
    2026-10-03: every copy is fresh.)
  * The pilot's Weathervane choice is `VarkaLedger.weathervane_choice`,
    default: keep the current element unless another holds more Oath, then
    the most, ties in P/H/E/C order.

VARKA DEFENCE (review/active/varka-defence-2026-10-01.md, ruled 2026-10-01):
  * GALE MANTLE reads `half_total_oath` (total Oath // 2). WINDBORNE RESOLVE
    pays Block on every change, after Cycle of Seasons. OATHBOUND AEGIS pays
    total // 2 per copy, uncapped. Favonian Standard left with its card.
  * BOREAS'S FANG (sec.4): on his first turn, post-draw, before Weathervane,
    the starter Knight's element becomes current (`set_current`, not a
    Knight, so a change, as the C# Fang's is). The element is
    `Player.varka_starter_element` (`build_player`), else the first starter
    Knight among his cards. No Oath, so the Ascension still waits.

THE REBALANCE (review/active/varka-rebalance-2026-10-03.md secs.2-5, and the
Varka part of review/active/aoe-trim-2026-10-03.md sec.4; simmed in PR #863,
variant A's starter numbers):
  * WILDFIRE OATH was half the Pyro Oath on the turn's first Attack; see
    "Varka Wildfire Oath and Short Circuit" below.
  * ABSOLUTE ZERO: no Swirl widening; "Whenever you apply Weak or Vulnerable
    to an enemy, deal damage equal to your Cryo Oath to it" -- element-less,
    unpowered, per stack (`on_debuff_applied`, from
    `refpowers.on_power_applied`, Sea's Reproach's seat).
  * CYCLE OF SEASONS: its damage hits one random enemy, not ALL.

THE COMBO PASS (review/active/varka-combo-pass-2026-10-04.md, ruled
2026-10-04, all four picks):
  * FIVE GENERIC BLOCK CARDS LEFT: Oath of the Knights' turn-start Block went
    with its card; the `half_total_oath`, `enemies_with_aura` and
    `oath_elements` counts stay as grammar no row reads.
  * BARON BUNNY's burst is one hit of the whole stack at ONE random living
    enemy (was every enemy).
  * PYRE OATH (`on_card_exhausted`, from `refpowers.after_card_exhausted`,
    the one exhaust funnel): every card of his exhausted gains the stack's
    Pyro Oath, one gain per card. A mid-play exhaust is swept there after
    the play, so Stoke the Flames' own +2 lands first.
  * UNWAVERING BANNER, reworded ("Only Knights can change your current
    element. Whenever another card would, gain 1 Oath of your current element
    instead."): the open Oath's switch and Change of Guard are held, and the
    play gains 1 Oath of the current element, once per play
    (`banner_holds`), when it would have been a change. Weathervane is held
    too and, not being a card, gains nothing.
  * KINDS `gain_pyro_oath` (Stoke the Flames; since the 2026-10-05 seat
    round it also makes Pyro current, `card_makes_current`), `pyro_strike`
    (Ember Cleave),
    `shatter` (stacks of Weak plus Vulnerable on the aim, read before the
    hit) and `deep_freeze` (double the aim's Weak and Vulnerable).

VARKA WILDFIRE OATH AND SHORT CIRCUIT (2026-10-03):
  * WILDFIRE OATH is Pyro's Absolute Zero: "Whenever you apply Pyro to an
    enemy, deal damage equal to your Pyro Oath to it." Paid in `note_hit`,
    AFTER that application's own Oath credit, so the Pyro Oath read is the
    one the triggering application just raised (when it credits).
    Element-less and unpowered, per stack, so it never re-enters `note_hit`.
    C# twin: `VarkaOath.NoteApplication` -> `WildfireOathPower.OnPyroApplied`.
  * RAZOR: AWAKENING (`awakening`) hits the one enemy it is played on.
  * KINDS `kindled_edge`, `storm_battery`, `frost_ward`, `gleeful_songs`,
    `rippling_guard` and `echo_block` (Whisper of Water's next two turns).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from tier0 import constants as C

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
SWORN_BROTHERHOOD = "vk_sworn_brotherhood"
#: Power cost sweep, 2026-09-30: the base card's power, current element only
#: (the upgrade installs SWORN_BROTHERHOOD, every element).
SWORN_BROTHERHOOD_CURRENT = "vk_sworn_brotherhood_current"
BARON_BUNNY = "vk_baron_bunny"
DAWN_WINDS_MARCH = "vk_dawn_winds_march"
BOREAS_UNBOUND = "vk_boreas_unbound"
CONVERGING_WINDS = "vk_converging_winds"
GRAND_MASTERS_ORDER = "vk_grand_masters_order"
# --- the expansion's powers (2026-10-01) ---
STATIC_FIELD = "vk_static_field"
UNWAVERING_BANNER = "vk_unwavering_banner"
CYCLE_OF_SEASONS = "vk_cycle_of_seasons"
EYE_WALL = "vk_eye_wall"                    # this turn only
ASSEMBLY = "vk_assembly_at_the_cathedral"
WILDFIRE_OATH = "vk_wildfire_oath"
RETALIATING_TIDE = "vk_retaliating_tide"
ABSOLUTE_ZERO = "vk_absolute_zero"
OATH_UNTO_DEATH = "vk_oath_unto_death"
WOLFPACK = "vk_wolfpack"
OATHBOUND_AEGIS = "vk_oathbound_aegis"
#: Varka defence (2026-10-01): Cycle of Seasons' Block twin.
WINDBORNE_RESOLVE = "vk_windborne_resolve"
WEATHERVANE = "vk_weathervane"
TWIN_GALES = "vk_twin_gales"
EYE_OF_STORMTERROR = "vk_eye_of_stormterror"
THE_ORDER_ANSWERS = "vk_the_order_answers"
#: The combo pass (2026-10-04): Pyro's Exhaust engine.
PYRE_OATH = "vk_pyre_oath"
#: Unwavering Banner's "gain 1 Oath of your current element instead".
BANNER_OATH = 1
#: Eye of Stormterror: "The first 3 times you Swirl each turn".
EYE_OF_STORMTERROR_SWIRLS = 3
#: Tempest of the Four Winds' four hits, in the printed order.
TEMPEST_ELEMENTS = ("pyro", "hydro", "cryo", "electro")

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
    "oath_per_cryo_enemy", "change_of_guard", "rally",
    # THE EXPANSION (2026-10-01).
    "pathfinders_mark", "current_element_strike", "blazing_charge",
    "glacial_edict", "thundering_verdict", "awakening", "draw_per_enemy",
    "cleanse", "crosscurrent", "double_current_oath", "tempest",
    # ELEMENT IDENTITIES (2026-10-01).
    "electro_strike", "electro_all", "violet_storm",
    # THE REBALANCE (2026-10-03).
    "kindled_edge", "storm_battery", "frost_ward", "gleeful_songs",
    "rippling_guard", "echo_block",
    # Downburst's rider (2026-10-04, after #882).
    "swirled_oath",
    # THE COMBO PASS (2026-10-04).
    "gain_pyro_oath", "pyro_strike", "shatter", "deep_freeze",
})
KIND_FIELDS = {
    "ascension_hit": ("per",),
    "avatar_hit": ("base", "per"),
    "swirled_take_more": ("amount",),
    "current_element_strike": ("base",),
    "blazing_charge": ("base", "per"),
    "glacial_edict": ("amount",),
    "thundering_verdict": ("base", "per"),
    "awakening": ("base", "amount"),
    "tempest": ("base",),
    "electro_strike": ("base",),
    "electro_all": ("base",),
    "violet_storm": ("base",),
    "kindled_edge": ("base",),
    "storm_battery": ("per",),
    "frost_ward": ("amount",),
    "gleeful_songs": ("base", "per"),
    "rippling_guard": ("base", "per"),
    "echo_block": ("amount",),
    "swirled_oath": ("amount",),
    # The combo pass (2026-10-04).
    "gain_pyro_oath": ("amount",),
    "pyro_strike": ("base",),
    "shatter": ("base", "per"),
}
#: The target each kind's row names (the codegen's `VARKA_AIMED_KINDS` less
#: the two follow-up hits, and `VARKA_ALL_KINDS`); every other kind, none.
KIND_TARGETS = {
    "apply_current_element": "enemy", "pathfinders_mark": "enemy",
    "current_element_strike": "enemy", "blazing_charge": "enemy",
    "glacial_edict": "enemy", "crosscurrent": "enemy", "tempest": "enemy",
    "thundering_verdict": "all_enemies", "awakening": "enemy",
    "electro_strike": "enemy", "electro_all": "all_enemies",
    "violet_storm": "random_enemy",
    "kindled_edge": "enemy", "storm_battery": "all_enemies",
    "frost_ward": "all_enemies", "gleeful_songs": "all_enemies",
    # The combo pass (2026-10-04).
    "pyro_strike": "enemy", "shatter": "enemy", "deep_freeze": "enemy",
}
#: `upgraded` is the `varka_upgraded` delta's mark (Pathfinder's Mark+).
OP_FIELDS = frozenset({"op", "kind", "target", "per", "base", "amount",
                       "upgraded"})

COUNTS = frozenset({"current_oath", "oath_elements",
                    # THE EXPANSION (2026-10-01).
                    "enemies_with_aura", "hydro_oath",
                    "knights_played_this_combat",
                    # VARKA DEFENCE (2026-10-01): Gale Mantle.
                    "half_total_oath"})
PREDICATES = frozenset({"has_current_element", "knight_played_this_turn",
                        "swirled_by_this",
                        # THE EXPANSION (2026-10-01).
                        "target_has_pyro", "element_changed_this_turn"})


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
    #: Per play, parallel to `scopes`: the elements this play Swirled, in
    #: order (Downburst's "gain 2 Oath of the element Swirled").
    play_swirl_elements: list = field(default_factory=list)
    #: Per play, parallel to `scopes`: is it an open-Oath play (his own
    #: non-Knight card), whose applications set the current element.
    play_open: list = field(default_factory=list)
    swirls_made: int = 0              # this combat
    knights_this_turn: int = 0        # Knight plays this turn, replays too
    # --- the expansion (2026-10-01) ---
    knights_this_combat: int = 0      # Charge of the Knights, replays too
    swirls_this_turn: int = 0         # Eye of Stormterror
    element_changed_turn: int = -1    # Shifting Gale: state.turn of the change
    static_field_turn: int = -1       # Static Field: the turn it drew
    pays_twice: int = 0               # > 0 inside Crosscurrent's Swirl
    #: Per play, parallel to `scopes`: did the play's aim wear Pyro at the
    #: top of the play (Amber: Sharpshooter's "already has Pyro").
    play_target_pyro: list = field(default_factory=list)
    no_apply_credit: int = 0          # > 0 inside a hit that credits nothing
    landing: bool = False             # inside a Converging Winds spread
    stormward_in_bonus: int = 0       # Stormward's part of this play's bonus
    #: Unwavering Banner (the combo pass): has the outermost open play paid
    #: its "gain 1 Oath instead" yet.
    banner_paid: bool = False
    # --- the rebalance paper (sim only) ---
    #: Whisper of Water: [Block, turns left] paid at each turn start.
    echo_block: list = field(default_factory=list)
    # --- the pilot's choices (None: the default reading) ---
    guard_choice: Optional[str] = None
    knight_choice: Optional[str] = None
    #: Weathervane: an element, or "keep" to leave the current one.
    weathervane_choice: Optional[str] = None


# --------------------------------------------------------------------------
#  Who is Varka
# --------------------------------------------------------------------------

def live(player) -> bool:
    """This Player is Varka."""
    return getattr(player, "character_id", "") == CHARACTER


def ledger(player) -> Optional[VarkaLedger]:
    """His ledger, made on first use; None for anyone else."""
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


#: The expansion's Noelle: a Geo Knight, which is no Oath element.
KNIGHT_ELEMENTS = ELEMENTS + ("geo",)


def is_knight(card) -> bool:
    return (getattr(card, "personal_pool", None) == CHARACTER
            and card.is_companion
            and getattr(card, "element", "none") in KNIGHT_ELEMENTS)


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
    # OATH UNTO DEATH: "Whenever you gain Oath of your current element, gain
    # 1 more." Inside the one gain event, so March pays once.
    if element == led.current:
        n += _power(state.player, OATH_UNTO_DEATH)
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


def open_scope(state, open_oath: bool = False,
               target_pyro: bool = False) -> None:
    led = ledger(state.player)
    if led is not None:
        if not led.scopes:
            led.banner_paid = False
        led.scopes.append(set())
        led.play_swirls.append([])
        led.play_swirl_elements.append([])
        led.play_open.append(open_oath)
        led.play_target_pyro.append(target_pyro)


def close_scope(state) -> None:
    led = ledger(state.player)
    if led is not None and led.scopes:
        led.scopes.pop()
        led.play_swirls.pop()
        if led.play_swirl_elements:
            led.play_swirl_elements.pop()
        if led.play_open:
            led.play_open.pop()
        if led.play_target_pyro:
            led.play_target_pyro.pop()


#: The open Oath's switch (module, so a paired sim can run the old rule).
OPEN_OATH = True

#: Whisper of Water (rebalance sec.3): "at the start of your next 2 turns".
ECHO_BLOCK_TURNS = 2


def open_oath_switches(led: VarkaLedger, element: str,
                       player=None) -> bool:
    """Does this application make `element` current? Only inside an
    open-Oath play, for an Oath element, outside a no-credit hit, and never
    under Unwavering Banner ("Only Knights can change your current element";
    `note_hit` asks with no `player` and pays the Banner itself)."""
    if player is not None and _power(player, UNWAVERING_BANNER):
        return False
    return bool(OPEN_OATH and led.play_open and led.play_open[-1]
                and element in ELEMENTS and not led.no_apply_credit
                and not led.landing)


def banner_holds(state, element: str) -> None:
    """UNWAVERING BANNER (the combo pass, 2026-10-04): "Whenever another card
    would [change your current element], gain 1 Oath of your current element
    instead." Only when it would have been a change (another element is
    current), once per play. C# twin: `VarkaOath.BannerHolds`."""
    led = ledger(state.player)
    if (led is None or led.current is None or element == led.current
            or led.banner_paid):
        return
    led.banner_paid = True
    state.emit("varka_banner", element=led.current, would=element)
    gain(state, led.current, BANNER_OATH, "unwavering_banner")


# --------------------------------------------------------------------------
#  The current element
# --------------------------------------------------------------------------

def set_current(state, element: str, knight: bool) -> None:
    led = ledger(state.player)
    if led is None or element not in ELEMENTS:
        return
    p = state.player
    if element != led.current:
        led.current = element
        led.element_changed_turn = state.turn
        state.emit("varka_current", element=element, knight=knight)
        n = _power(p, BOREAS_UNBOUND)
        if n:
            p.energy += n
            state.emit("varka_unbound", energy=n)
        # CYCLE OF SEASONS: "Whenever your current element changes, deal 7
        # damage to ALL enemies." Element-less and unpowered, a Power's.
        cycle = _power(p, CYCLE_OF_SEASONS)
        if cycle:
            from tier0.engine import effects        # late: cycle
            state.emit("varka_cycle_of_seasons", amount=cycle)
            # The AoE trim (sec.4): "deal damage to a random enemy".
            targets = list(state.living_enemies)
            if targets:
                targets = [state.rng.choice(targets)]
            for e in targets:
                effects.deal_damage_to_enemy(state, e, cycle, element=None,
                                             source="card", powered=False)
        # WINDBORNE RESOLVE (Varka defence): "Whenever your current element
        # changes, gain 5 Block." Unpowered, a Power's.
        _block(state, _power(p, WINDBORNE_RESOLVE), "windborne_resolve")


def card_makes_current(state, element: str) -> None:
    """A card of his that is not a Knight says "`element` becomes your
    current element" (Stoke the Flames, 2026-10-05): the open Oath's fork in
    `note_hit`, Unwavering Banner holding it. C# twin:
    `VarkaOath.CardMakesCurrent`."""
    if ledger(state.player) is None or element not in ELEMENTS:
        return
    if _power(state.player, UNWAVERING_BANNER):
        banner_holds(state, element)
    else:
        set_current(state, element, knight=False)


# --------------------------------------------------------------------------
#  Hooks the shared engine calls (each a no-op for anyone but Varka)
# --------------------------------------------------------------------------

def begin_play(state, card) -> None:
    """`effects.resolve_card`, after the bind: open this play's scope, and a
    Knight sets the current element before its effects resolve."""
    led = ledger(state.player)
    if led is None:
        return
    aim = state.card_aim
    open_scope(state, open_oath=not is_knight(card),
               target_pyro=bool(aim is not None and aim.aura == "pyro"))
    if is_knight(card):
        led.knights_this_turn += 1
        led.knights_this_combat += 1
        # Noelle's Geo is no Oath element: `set_current` refuses it.
        set_current(state, card.element, knight=True)


def end_play(state, card=None) -> None:
    """The play's scope closes; then the expansion's after-play Power,
    Wolfpack on Four Winds' Ascension. (Assembly at the Cathedral pays at
    `note_hit` since co-op notes pick 2.)"""
    close_scope(state)
    led = ledger(state.player)
    if led is None or card is None:
        return
    p = state.player
    wolves = _power(p, WOLFPACK)
    if wolves and card.id.rstrip("+") == ASCENSION_ID:
        from tier0.content import loader            # late: cycle
        for _ in range(wolves):
            copy = loader.get_card(card.id)
            p.discard_pile.append(copy)
            state.cards_created_this_turn += 1
            state.emit("add_card", card=copy.id, to="discard")


def note_hit(state, enemy, element) -> None:
    """`reactions.resolve_hit`, first line: an application of an element to
    a live enemy credits apply-Oath (whether it sticks, refreshes or reacts).
    """
    led = ledger(state.player)
    if (led is None or element not in ELEMENTS or not enemy.alive
            or led.landing):
        return
    # STATIC FIELD: "The first time each turn you apply Electro, draw 2."
    # Any application of his, a no-credit hit's too.
    if element == "electro":
        sf = _power(state.player, STATIC_FIELD)
        if sf and led.static_field_turn != state.turn:
            led.static_field_turn = state.turn
            state.emit("varka_static_field", draw=sf)
            state.draw(sf)
    if not led.no_apply_credit:
        if open_oath_switches(led, element):
            if _power(state.player, UNWAVERING_BANNER):
                banner_holds(state, element)
            else:
                set_current(state, element, knight=False)
        credit(state, "apply", element)
    # WILDFIRE OATH (Varka Wildfire Oath and Short Circuit, 2026-10-03):
    # "Whenever you apply Pyro to an enemy, deal damage equal to your Pyro
    # Oath to it" -- after the credit above, so the Oath this application
    # just raised counts. Element-less, so it never comes back here.
    if element == "pyro":
        _wildfire(state, enemy)
    # ASSEMBLY AT THE CATHEDRAL (co-op notes pick 2, 2026-10-02): "Whenever
    # you apply an element, deal 2 [3] damage to a random enemy" -- any
    # application of his, a no-credit hit's too. Element-less, so its own
    # hit never comes back here. C# twin: `VarkaOath.NoteApplication`.
    assembly = _power(state.player, ASSEMBLY)
    if assembly and state.living_enemies:
        from tier0.engine import effects            # late: cycle
        e = state.rng.choice(list(state.living_enemies))
        state.emit("varka_assembly", target=e.name, amount=assembly)
        effects.deal_damage_to_enemy(state, e, assembly, element=None,
                                     source="card", powered=False)


def _wildfire(state, enemy) -> None:
    """WILDFIRE OATH's payout: the Pyro Oath per stack, to the enemy the
    Pyro landed on, element-less and unpowered (Absolute Zero's shape,
    `on_debuff_applied`). C# twin: `WildfireOathPower.OnPyroApplied`."""
    led = ledger(state.player)
    if led is None or not enemy.alive:
        return
    n = _power(state.player, WILDFIRE_OATH) * led.oath["pyro"]
    if n <= 0:
        return
    from tier0.engine import effects                # late: cycle
    state.emit("varka_wildfire", target=enemy.name, amount=n)
    effects.deal_damage_to_enemy(state, enemy, n, element=None,
                                 source="card", powered=False)


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
    the swirled element: a bare one gets a copy, one already wearing it
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
        led.landing = True
        try:
            dmg = reactions.resolve_hit(state, other, aura, flat,
                                        "converging_spread")
        finally:
            led.landing = False
        reactions._splash(state, other, int(dmg))


def on_swirl(state, enemy, aura: str) -> None:
    """`reactions._react`, after the shared Swirl: count it, credit it, then
    pay his current element."""
    from tier0.engine import effects, powers        # late: cycle
    led = ledger(state.player)
    if led is None:
        return
    led.swirls_made += 1
    led.swirls_this_turn += 1
    if led.play_swirls:
        led.play_swirls[-1].append(enemy)
    if led.play_swirl_elements:
        led.play_swirl_elements[-1].append(aura)
    state.emit("varka_swirl", element=aura, target=enemy.name,
               current=led.current)
    credit(state, "swirl", aura)
    cur = led.current
    p = state.player
    # Crosscurrent: "This Swirl pays twice." Twin Gales: the element Swirled
    # pays too, once, when it is not already the current one.
    for _ in range(2 if led.pays_twice else 1):
        if cur is not None:
            _pay(state, enemy, cur)
        if (_power(p, TWIN_GALES) and aura in ELEMENTS and aura != cur):
            _pay(state, enemy, aura)
    # EYE WALL: "Whenever you Swirl this turn, gain 3 Block."
    _block(state, _power(p, EYE_WALL), "eye_wall")
    # EYE OF STORMTERROR: "The first 3 times you Swirl each turn, draw 1."
    eye = _power(p, EYE_OF_STORMTERROR)
    if eye and led.swirls_this_turn <= EYE_OF_STORMTERROR_SWIRLS:
        state.draw(eye)


def _pay(state, enemy, element: str) -> None:
    """One Swirl payout of `element` (sec.3). (Wildfire Oath widened Pyro's
    until element identities; Absolute Zero widened Cryo's until the
    rebalance, which made it a debuff payoff, `on_debuff_applied`.)"""
    from tier0.engine import effects, powers        # late: cycle
    led = ledger(state.player)
    p = state.player
    if element == "pyro":
        if enemy.alive:
            effects.deal_damage_to_enemy(state, enemy, SWIRL_PYRO_DAMAGE,
                                         element=None, source="card",
                                         powered=False)
    elif element == "hydro":
        _block(state, SWIRL_HYDRO_BLOCK, "swirl_hydro")
    elif element == "cryo":
        if enemy.alive:
            powers.apply_power(state, enemy, "vulnerable",
                               SWIRL_CRYO_VULNERABLE, applier=p)
    elif element == "electro":
        for e in list(state.living_enemies):
            effects.deal_damage_to_enemy(state, e, SWIRL_ELECTRO_DAMAGE_ALL,
                                         element=None, source="card",
                                         powered=False)


def on_debuff_applied(state, target, name: str, stacks: int) -> None:
    """`refpowers.on_power_applied`, for a Weak or Vulnerable HE applied
    (Sea's Reproach's test). ABSOLUTE ZERO (the rebalance, sec.2): "Whenever
    you apply Weak or Vulnerable to an enemy, deal damage equal to your Cryo
    Oath to it." Element-less and unpowered (a Power's), per stack. C# twin:
    `AbsoluteZeroPower.AfterPowerAmountChanged`."""
    if name not in ("weak", "vulnerable") or stacks <= 0:
        return
    led = ledger(state.player)
    if (led is None or target is state.player
            or not getattr(target, "alive", False)
            or not any(target is e for e in state.enemies)):
        return
    n = _power(state.player, ABSOLUTE_ZERO) * led.oath["cryo"]
    if n <= 0:
        return
    from tier0.engine import effects                # late: cycle
    state.emit("varka_absolute_zero", target=target.name, amount=n)
    effects.deal_damage_to_enemy(state, target, n, element=None,
                                 source="card", powered=False)


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
    Bunny's burst, Sworn Brotherhood, The Order Answers, in that order (Oath
    of the Knights left with its card in the combo pass)."""
    from tier0.engine import effects                # late: cycle
    led = ledger(state.player)
    if led is None:
        return
    p = state.player
    led.knights_this_turn = 0
    led.swirls_this_turn = 0
    p.powers.pop(GRAND_MASTERS_ORDER, None)         # "this turn" ran out
    p.powers.pop(EYE_WALL, None)                    # Eye Wall's too
    # WHISPER OF WATER (rebalance sec.3): "Gain 4 Block ... at the start of
    # your next 2 turns." Raw, as `block_next_turn`'s payout is.
    if led.echo_block:
        for echo in led.echo_block:
            _block(state, echo[0], "echo_block")
            echo[1] -= 1
        led.echo_block = [e for e in led.echo_block if e[1] > 0]
    # BOREAS'S FANG (Varka defence sec.4): "At the start of each combat, your
    # starting Knight's element becomes your current element."
    if state.turn == 1 and (FANG in p.relic_hooks
                            or FANG_UPGRADED in p.relic_hooks):
        el = starting_element(p)
        if el is not None:
            state.emit("varka_fang_element", element=el)
            set_current(state, el, knight=False)
    # WEATHERVANE (the expansion), first: "you may choose an element you have
    # Oath in; it becomes your current element." Sworn Brotherhood below
    # gains the new one. Since the combo pass "Only Knights can change your
    # current element": the Banner holds it, and it is no card, so no Oath.
    if _power(p, WEATHERVANE) and not _power(p, UNWAVERING_BANNER):
        _weathervane(state, led)
    bunny = int(p.powers.pop(BARON_BUNNY, 0))
    if bunny:
        state.emit("varka_baron_bunny", amount=bunny)
        # The combo pass (2026-10-04): one random living enemy, was ALL.
        targets = list(state.living_enemies)
        if targets:
            e = state.rng.choice(targets)
            open_scope(state)
            try:
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
    # THE ORDER ANSWERS (the expansion), last: "add a random Knight to your
    # hand" -- a pool Knight, at its own cost.
    for _ in range(_power(p, THE_ORDER_ANSWERS)):
        _add_random_knight(state, free=False)


def _weathervane(state, led: VarkaLedger) -> None:
    held = [el for el in ELEMENTS if led.oath[el] > 0]
    choice = led.weathervane_choice
    led.weathervane_choice = None
    if choice == "keep" or not held:
        return
    if choice not in held:
        best = max(held, key=lambda el: (led.oath[el], -ELEMENTS.index(el)))
        if led.current in held and led.oath[led.current] >= led.oath[best]:
            return
        choice = best
    state.emit("varka_weathervane", element=choice)
    set_current(state, choice, knight=False)


def turn_end(state) -> None:
    """`combat`'s player turn end, beside Dusk: OATHBOUND AEGIS, "gain Block
    equal to half your total Oath" (rounded down, per copy), unpowered."""
    led = ledger(state.player)
    if led is None:
        return
    copies = _power(state.player, OATHBOUND_AEGIS)
    if copies:
        _block(state, (sum(led.oath.values()) // 2) * copies,
               "oathbound_aegis")
    # RETALIATING TIDE (element identities), after the Aegis so its Block
    # counts: "deal damage equal to your Block, up to your Hydro Oath, to a
    # random enemy". Element-less and unpowered (a Power's), once per stack.
    from tier0.engine import effects                # late: cycle
    for _ in range(_power(state.player, RETALIATING_TIDE)):
        amount = min(state.player.block, led.oath["hydro"])
        if amount <= 0 or not state.living_enemies:
            break
        e = state.rng.choice(list(state.living_enemies))
        state.emit("varka_retaliating_tide", target=e.name, amount=amount)
        effects.deal_damage_to_enemy(state, e, amount, element=None,
                                     source="card", powered=False)


# --------------------------------------------------------------------------
#  Readers: counts and predicates
# --------------------------------------------------------------------------

def count(state, token: str) -> int:
    if token == "current_oath":
        return current_oath(state.player)
    if token == "oath_elements":
        return oath_elements(state.player)
    led = ledger(state.player)
    if token == "enemies_with_aura":
        return (0 if led is None else
                sum(1 for e in state.living_enemies if e.aura))
    if token == "hydro_oath":
        return 0 if led is None else led.oath["hydro"]
    if token == "knights_played_this_combat":
        return 0 if led is None else led.knights_this_combat
    if token == "half_total_oath":
        return 0 if led is None else sum(led.oath.values()) // 2
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
    if name == "target_has_pyro":
        return bool(led.play_target_pyro and led.play_target_pyro[-1])
    if name == "element_changed_this_turn":
        return led.element_changed_turn == state.turn
    raise ValueError(f"not a Varka predicate: {name!r}")


# --------------------------------------------------------------------------
#  Gale Sweep: `damage` with `only_if: fresh_aura`
# --------------------------------------------------------------------------
# `fresh_aura` predates 2026-10-03, when spent auras went: every aura is
# fresh, so the sweep takes every enemy wearing one.

def _fresh_snapshot(state) -> list:
    return [(e, e.aura, e.aura_turns_left) for e in state.living_enemies
            if e.aura]


def _restore(e, aura: str, turns: int) -> None:
    if e.aura != aura:
        e.aura = aura
        e.aura_turns_left = max(e.aura_turns_left, turns)


def fresh_aura_sweep(state, fx: dict, card) -> None:
    """`effects._op_damage`, for a `damage` op carrying `only_if:
    fresh_aura`: the enemies wearing an aura when the op resolves, each
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
        "for a Varka seat; no shipped row "
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
    if fx.get("target") != KIND_TARGETS.get(kind):
        raise ValueError(
            f"card {card_id!r}: varka {kind!r} takes target "
            f"{KIND_TARGETS.get(kind)!r}, got {fx.get('target')!r}")


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


def _card_hit(state, card, target, amount: int, element: str,
              credits: bool = True) -> None:
    """One powered hit of `card` on `target` carrying `element` (the
    expansion's element hits: Cavalry Charge, Blazing Charge, Thundering
    Verdict, Razor, Tempest). The card's flat Attack riders ride it, less
    Stormward Stance's part unless the hit is Anemo; Strength counts."""
    from tier0.engine import effects                # late: cycle
    led = ledger(state.player)
    if target is None or not target.alive or amount <= 0:
        return
    bonus = state.current_attack_bonus
    if element != ELEMENT:
        bonus -= led.stormward_in_bonus
    amount += max(0, bonus)
    source = "attack" if card.type == "attack" else "card"
    if not credits:
        led.no_apply_credit += 1
    try:
        effects.deal_damage_to_enemy(state, target, amount, element=element,
                                     source=source)
    finally:
        if not credits:
            led.no_apply_credit -= 1


def _add_random_knight(state, free: bool) -> None:
    """The Order Answers: a random pool Knight into the hand."""
    from tier0.content import loader                # late: cycle
    from tier0.engine import effects                # late: cycle
    pool = pool_knight_ids()
    if not pool:
        return
    knight = loader.get_card(state.rng.choice(pool))
    knight.free_this_turn = free
    state.emit("varka_order_answers", card=knight.id)
    effects._add_token(state, knight, "hand")


def _expansion_kind(state, fx: dict, card, led: VarkaLedger) -> bool:
    """The expansion's kinds. True when `fx` was one of them."""
    from tier0.engine import effects, powers, reactions  # late: cycle
    kind = fx["kind"]
    p = state.player
    aim = state.card_aim
    if kind == "pathfinders_mark":
        # "Apply your current element to an enemy (a random one of the four
        # if you have none). [ALL enemies]" One element for every target.
        el = led.current or state.rng.choice(ELEMENTS)
        targets = (list(state.living_enemies) if fx.get("upgraded")
                   else effects._pick_targets(state, "enemy",
                                              allow_dead=True))
        for e in targets:
            reactions.resolve_hit(state, e, el, 0, "apply_aura_op")
    elif kind == "current_element_strike":
        # Cavalry Charge: "Deal 7 damage as your current element." Without
        # one it is his plain Anemo hit.
        _card_hit(state, card, aim, fx["base"], led.current or ELEMENT)
    elif kind == "blazing_charge":
        _card_hit(state, card, aim, fx["base"] + fx["per"] * led.oath["pyro"],
                  "pyro")
    elif kind == "glacial_edict":
        # "1 Weak and 1 Vulnerable, plus 1 of each for every 4 Cryo Oath",
        # read after the row's own Cryo landed.
        if aim is not None and aim.alive:
            n = 1 + led.oath["cryo"] // max(1, fx["amount"])
            powers.apply_power(state, aim, "weak", n, applier=p)
            powers.apply_power(state, aim, "vulnerable", n, applier=p)
    elif kind == "thundering_verdict":
        # Element identities: X times (the Energy spent, `state.current_x`),
        # each time to ALL. The Electro Oath is read once, before the hits.
        amount = fx["base"] + fx["per"] * led.oath["electro"]
        for _ in range(int(state.current_x or 0)):
            for e in list(state.living_enemies):
                _card_hit(state, card, e, amount, "electro")
    elif kind == "electro_strike":
        # Charged Lunge: "Deal 6 Electro damage."
        _card_hit(state, card, aim, fx["base"], "electro")
    elif kind == "electro_all":
        # Chain Lightning: "Deal 8 Electro damage to ALL enemies."
        for e in list(state.living_enemies):
            _card_hit(state, card, e, fx["base"], "electro")
    elif kind == "violet_storm":
        # "Discard your hand. Deal 8 Electro damage to a random enemy for
        # each card discarded." Storm of Steel's discard (the sheet's own
        # `discard` op, `amount: hand_size`, so Sly and the turn's count see
        # it), then one hit per card actually discarded.
        before = state.discards_this_turn
        effects._op_discard(state, {"op": "discard", "amount": "hand_size"},
                            card)
        for _ in range(state.discards_this_turn - before):
            if not state.living_enemies:
                break
            _card_hit(state, card,
                      state.rng.choice(list(state.living_enemies)),
                      fx["base"], "electro")
    elif kind == "awakening":
        # Razor (the AoE trim, sec.4): "Deal 4 Electro damage to an enemy, 3
        # more if it already has Electro" -- fresh or spent, read before the
        # hit.
        if aim is not None and aim.alive:
            more = fx["amount"] if aim.aura == "electro" else 0
            _card_hit(state, card, aim, fx["base"] + more, "electro")
    elif kind == "draw_per_enemy":
        n = len(state.living_enemies)
        if n:
            state.draw(n)
    elif kind == "cleanse":
        for name in ("weak", "frail", "vulnerable"):
            if p.powers.pop(name, None):
                state.emit("varka_cleanse", power=name)
    elif kind == "crosscurrent":
        if aim is not None:
            led.pays_twice += 1
            try:
                reactions.resolve_hit(state, aim, ELEMENT, 0, "swirl_op")
            finally:
                led.pays_twice -= 1
    elif kind == "double_current_oath":
        if led.current is not None and led.oath[led.current] > 0:
            gain(state, led.current, led.oath[led.current],
                 "double_current_oath")
    elif kind == "tempest":
        for el in TEMPEST_ELEMENTS:
            _card_hit(state, card, aim, fx["base"], el)
    elif _rebalance_kind(state, fx, card, led):
        pass
    elif _combo_kind(state, fx, card, led):
        pass
    else:
        return False
    return True


def _powered_block(state, card, amount: int) -> None:
    """Printed Block through the shared `block` op (Dexterity, Frail)."""
    from tier0.engine import effects                # late: cycle
    if amount > 0:
        effects._op_block(state, {"op": "block", "amount": amount}, card)


def _rebalance_kind(state, fx: dict, card, led: VarkaLedger) -> bool:
    """THE REBALANCE's kinds. True when `fx` was one of them. C# twins:
    `VarkaCards.<Kind>`."""
    from tier0.engine import effects, powers, reactions  # late: cycle
    kind = fx["kind"]
    p = state.player
    aim = state.card_aim
    if kind == "kindled_edge":
        # "Deal 7 Pyro damage. If it sets off an Elemental Reaction, deal 7
        # more." The more is element-less (a second application is not
        # printed), a powered hit of the card on the same enemy.
        before = state.reactions_this_card
        _card_hit(state, card, aim, fx["base"], "pyro")
        if (state.reactions_this_card > before and aim is not None
                and aim.alive):
            _card_hit(state, card, aim, fx["base"], None)
    elif kind == "storm_battery":
        # "Deal 2 Electro damage to ALL enemies for each other card in your
        # hand." The card has left the hand, so the hand is the others.
        n = len(p.hand)
        for e in list(state.living_enemies):
            _card_hit(state, card, e, fx["per"] * n, "electro")
    elif kind == "frost_ward":
        # "Apply 1 Weak to each enemy with an aura. Gain 3 Block for each."
        hit = [e for e in state.living_enemies if e.aura]
        for e in hit:
            powers.apply_power(state, e, "weak", 1, applier=p)
        _powered_block(state, card, fx["amount"] * len(hit))
    elif kind == "gleeful_songs":
        # "Apply Hydro to ALL enemies. Gain 4 Block, plus 3 for each enemy it
        # reacts on."
        reacted = 0
        for e in effects._pick_targets(state, "all_enemies",
                                       allow_dead=True):
            before = state.reactions_this_card
            reactions.resolve_hit(state, e, "hydro", 0, "apply_aura_op")
            reacted += state.reactions_this_card > before
        _powered_block(state, card, fx["base"] + fx["per"] * reacted)
    elif kind == "rippling_guard":
        # "Gain 3 Block, plus 2 for each other card you played this turn."
        # `cards_played_this_turn` already counts this play.
        others = max(0, state.cards_played_this_turn - 1)
        _powered_block(state, card, fx["base"] + fx["per"] * others)
    elif kind == "echo_block":
        # Whisper of Water's "and at the start of your next 2 turns".
        led.echo_block.append([fx["amount"], ECHO_BLOCK_TURNS])
    else:
        return False
    return True


def weak_and_vulnerable(enemy) -> int:
    """Shatter's count: the stacks of Weak plus Vulnerable on `enemy`."""
    if enemy is None:
        return 0
    return (int(enemy.powers.get("weak", 0))
            + int(enemy.powers.get("vulnerable", 0)))


def _combo_kind(state, fx: dict, card, led: VarkaLedger) -> bool:
    """THE COMBO PASS's kinds (2026-10-04). True when `fx` was one of them.
    C# twins: `VarkaCards.<Kind>`."""
    from tier0.engine import powers                 # late: cycle
    kind = fx["kind"]
    p = state.player
    aim = state.card_aim
    if kind == "gain_pyro_oath":
        # Stoke the Flames: "Gain 2 Pyro Oath. Pyro becomes your current
        # element." A gain, not an application; then the switch, a non-Knight
        # card's, so Unwavering Banner holds it (2026-10-05 seat round).
        gain(state, "pyro", fx["amount"], "gain_pyro_oath")
        card_makes_current(state, "pyro")
    elif kind == "pyro_strike":
        # Ember Cleave: "Deal 9 Pyro damage." The Exhaust is the row's op.
        _card_hit(state, card, aim, fx["base"], "pyro")
    elif kind == "shatter":
        # "Deal 5 Cryo damage, plus 2 for each Weak and Vulnerable on the
        # enemy." Stacks, read before the hit.
        if aim is not None and aim.alive:
            _card_hit(state, card, aim,
                      fx["base"] + fx["per"] * weak_and_vulnerable(aim),
                      "cryo")
    elif kind == "deep_freeze":
        # "Double its Weak and Vulnerable." After the row's own Cryo; each
        # doubling is an application of what it holds.
        if aim is not None and aim.alive:
            for name in ("weak", "vulnerable"):
                n = int(aim.powers.get(name, 0))
                if n > 0 and aim.alive:
                    powers.apply_power(state, aim, name, n, applier=p)
    else:
        return False
    return True


def on_card_exhausted(state, card) -> None:
    """`refpowers.after_card_exhausted`: PYRE OATH (the combo pass,
    2026-10-04), "Whenever you Exhaust a card, gain 1 Pyro Oath." One gain
    of the stack per card, any card of his. C# twin:
    `PyreOathPower.AfterCardExhausted`."""
    if ledger(state.player) is None:
        return
    n = _power(state.player, PYRE_OATH)
    if n:
        gain(state, "pyro", n, "pyre_oath")


def op_varka(state, fx: dict, card) -> None:
    """`effects.OPS['varka']`."""
    from tier0.engine import effects, reactions     # late: cycle
    led = ledger(state.player)
    if led is None:
        _refuse(f"op 'varka' ({fx.get('kind')!r}) on {card.id!r}")
    kind = fx["kind"]
    p = state.player
    if _expansion_kind(state, fx, card, led):
        return
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
    elif kind == "swirled_oath":
        # Downburst (2026-10-04): "If it Swirls, gain 2 Oath of the element
        # Swirled." One gain event per element Swirled, on top of the Swirl's
        # own credit; through `gain`, so Oath Unto Death, Dawn Wind's March
        # and Boreas's Fang all see it.
        swirled = led.play_swirl_elements[-1] if led.play_swirl_elements else []
        for el in dict.fromkeys(swirled):
            gain(state, el, fx["amount"], "swirled_oath")
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
        if _power(p, UNWAVERING_BANNER):
            # The combo pass: only Knights change it. The Banner holds, and
            # pays when another element could have been chosen.
            other = next((el for el in held if el != led.current), None)
            if other is not None:
                banner_holds(state, other)
            led.guard_choice = None
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
    the dealt Knight on `AfterObtained`. The `proto_vk_` rows resolve through
    the loader's prototype door, always open for his ids."""
    from tier0.content import loader                # late: cycle
    from tier0.engine.state import Player
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
    # The run's starter Knight element, as the C# Fang records it
    # (`VarkaStarterKnight`): Boreas's Fang makes it current at combat start.
    player.varka_starter_element = element
    player.varka_ledger = VarkaLedger()
    return player


def starting_element(player) -> Optional[str]:
    """The element Boreas's Fang makes current: the recorded starter Knight
    element, else the first starter Knight among his cards (Knight's
    Commission's fallback), else None."""
    el = getattr(player, "varka_starter_element", None)
    if el in ELEMENTS:
        return el
    by_id = {cid: e for e, cid in STARTER_KNIGHT_IDS.items()}
    for pile in (player.hand, player.draw_pile, player.discard_pile,
                 player.exhaust_pile):
        for card in pile:
            hit = by_id.get(card.id.rstrip("+"))
            if hit:
                return hit
    return None
