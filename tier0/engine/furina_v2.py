"""Furina, THE RE-FOUNDING -- the sim slice, a separate arm (sim only, no C#).

The design is `review/active/furina-refounding-2026-10-03.md`: sec.1's rules
as sec.8 amends them, sec.2's cast as sec.8 amends it, and sec.9's exact slice
rows. Every card text and number below is the paper's; where the paper is
silent the reading taken is the simplest one consistent with it and is listed
in `READINGS` at the foot of this module (and in the slice report).

HOW IT IS SWITCHED ON. Per player: a `Player` built by `build_player` carries
`player.fv2` (an `Fv2` record) and `character_id = "furina_v2"`. Every hook
the engine calls is a no-op for any other player, so today's Furina
(`furina_stage`, `character_id = "furina"`) and every other kit is untouched:
no sheet row, no pool, no loader door, no codegen sees this arm. Its cards are
built here (`make_card`) and carry the tag `fv2`; `effects.resolve_card` hands
a card with that tag to `resolve_card` below once the shared aim is bound.

THE RULES, in the paper's order (sec.1 as amended by sec.8):

1. Three seats; performers have no bars, take no hits, and act front to back
   at the end of Furina's turn. Combat opens with Usher on stage (Salon
   Solitaire).
2. The Salon trio (Usher, Chevalmarin, Crabaletta) carries the numbers; a
   Guest Star bends a rule while on stage and/or has a utility act. One of
   each guest; a second copy Bows it and returns it.
3. A performer that leaves acts once more, FREE (a star does not pay), then
   gives 1 Fanfare, after its act.
4. Overflow: a summon onto a full stage Bows the front-most Salon member; a
   Salon summon onto three guests is a WALK-ON (its free Bow act + 1 Fanfare,
   no seat); a guest summon onto three guests Bows the front guest.
5. Fanfare is one number on Furina, no cap, no fade. Spend N on cards; stars
   PAY for their acts (skip and stay if short, nothing spent). A payment is not
   a Spend. Readers count flow (gained / spent this turn), reset at the start
   of Furina's turn, so they hold through the end-of-turn sequence.
6. Rehearsal: +1 per stack to every performer's damage and Block act, guests
   included; never Energy, draw or Fanfare.
7. Cue: the chosen performer acts now; a star pays as usual (a short star
   skips, the card's other effects still happen).

PROVENANCE. Every card text and number is the paper's: the starter, the trio
and the twenty slice rows from sec.9 (upgraded numbers where sec.9 prints
them; a row it gives no upgrade has none here), the guests' lines and acts
from sec.2's table as sec.8 amends it (Escoffier's once-a-turn free summon,
Thunderous Applause's draw per Bow), the starting relic from sec.9. The one
row that is not the paper's is `PROBE_CONTROLS`' plain 8 Block, which sec.9's
probe 4 names as the twin to compare against; it is never offered. The probe
packages (`tier0/harness/furina_v2_probe.py`) and the pilot's value model
(`tier0/pilot/furina_v2_pilot.py`) are instrument choices, not designs.
`READINGS` lists every place the paper was silent.
"""

from __future__ import annotations

import collections
from dataclasses import dataclass, field

CHARACTER = "furina_v2"
TAG = "fv2"
HP = 78                      # furina.yaml's hp; the slice does not move it
ELEMENT = "hydro"            # furina.yaml
CADENCE = "skill"            # furina.yaml: her Skills' damage carries Hydro

SEATS = 3                    # rule 1
OPENING_MEMBER = "usher"     # Salon Solitaire (sec.9 starter relic)

SALON = ("usher", "chevalmarin", "crabaletta")
#: The slice's guests (sec.9). Lyney, Lynette, Chevreuse and Wriothesley are
#: in sec.2 but not in the slice: `summon` refuses them by name.
STARS = ("neuvillette", "clorinde", "escoffier", "navia")
SUPPORTS = ("charlotte", "sigewinne")
GUESTS = STARS + SUPPORTS
NOT_IN_SLICE = ("lyney", "lynette", "chevreuse", "wriothesley")

# --- sec.2 / sec.9: the trio's acts ------------------------------------
ACT_USHER_BLOCK = 4
ACT_CHEVALMARIN_DAMAGE = 2       # to ALL enemies
ACT_CRABALETTA_DAMAGE = 5        # to a random enemy

# --- sec.2: the guests -------------------------------------------------
STAR_PRICE = {"neuvillette": 2, "clorinde": 1, "escoffier": 2, "navia": 0}
ACT_NEUVILLETTE_DAMAGE = 7       # Hydro to ALL
#: Pass two (main session, 2026-10-04): Neuvillette's on-stage line is now
#: "Your Hydro damage deals 2 more" -- card damage AND performer acts that
#: carry Hydro. The old line, "Your Hydro cards deal 3 more damage", is kept
#: as a variant (`Variant.neuvillette_line == "cards"`).
NEUVILLETTE_HYDRO_DAMAGE_BONUS = 2   # new line: any Hydro damage
NEUVILLETTE_HYDRO_BONUS = 3          # old line: Hydro cards only
#: Pass two: Clorinde's act is "pay 1: 6 Electro to a random enemy" (was 8;
#: the 8 is kept as a variant).
ACT_CLORINDE_DAMAGE = 6          # Electro to a random enemy
ACT_CLORINDE_DAMAGE_OLD = 8
CLORINDE_SPEND_DAMAGE = 4        # "Whenever you Spend, deal 4 Electro ..."
NAVIA_PER_SPENT = 2              # "twice the Fanfare you spent this turn"
CHARLOTTE_GAIN = 1               # her act: gain 1 Fanfare
CHARLOTTE_DRAW = 1               # "At the start of your turn, draw 1 more"
ACT_SIGEWINNE_BLOCK = 3          # "3 Block, plus 2 for each time you lost HP
SIGEWINNE_PER_HP_LOSS = 2        #  since her last act"

GUEST_ELEMENTS = {"neuvillette": "hydro", "clorinde": "electro",
                  "navia": "geo"}

BOW_FANFARE = 1                  # rule 3


# ----------------------------------------------------------------------
# Design variants (pass two), switchable per player so both the old and the
# new values can be probed side by side. The default is the new design.
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Variant:
    clorinde_act: int = ACT_CLORINDE_DAMAGE
    #: "hydro": "Your Hydro damage deals 2 more" (cards and acts).
    #: "cards": "Your Hydro cards deal 3 more damage" (the first slice).
    neuvillette_line: str = "hydro"


VARIANTS: dict[str, Variant] = {
    "new": Variant(ACT_CLORINDE_DAMAGE, "hydro"),
    "old": Variant(ACT_CLORINDE_DAMAGE_OLD, "cards"),
    "c8_hydro": Variant(ACT_CLORINDE_DAMAGE_OLD, "hydro"),
    "c6_cards": Variant(ACT_CLORINDE_DAMAGE, "cards"),
}
DEFAULT_VARIANT = "new"


# ----------------------------------------------------------------------
# The arm's one state record.
# ----------------------------------------------------------------------
def _new_ledger() -> dict:
    return {
        "gained": 0, "gained_by": collections.Counter(),
        "spent": 0, "spends": 0, "paid": 0,
        "star_acts": collections.Counter(),
        "star_skips": collections.Counter(),
        "acts": collections.Counter(),
        "cues": 0, "cues_on": collections.Counter(), "cue_whiffs": 0,
        "walk_ons": 0, "bows": collections.Counter(),
        "guest_repeats": 0, "summons": collections.Counter(),
        "clorinde_procs": 0, "neuvillette_bonus_hits": 0,
        "thunderous_draws": 0, "charlotte_draws": 0,
        "escoffier_free_summons": 0,
    }


@dataclass
class Fv2:
    stage: list = field(default_factory=list)       # member names, front first
    fanfare: int = 0
    gained_this_turn: int = 0
    spent_this_turn: int = 0
    rehearsal: int = 0
    thunderous: int = 0
    salon_summon_cards_this_turn: int = 0
    sigewinne_mark: int = 0          # `state.player_damage_events` at her last act
    opened: bool = False
    variant: Variant = field(default_factory=Variant)
    #: Who decides the player's choices inside a card (Cue target, Curtain
    #: Rise's mode, Step Forward's performer). None = the slice pilot's.
    decider: object = None
    ledger: dict = field(default_factory=_new_ledger)


def live(player) -> bool:
    return isinstance(getattr(player, "fv2", None), Fv2)


def _fv(state) -> Fv2:
    return state.player.fv2


def _decider(state):
    d = _fv(state).decider
    if d is None:
        from tier0.pilot import furina_v2_pilot      # late: avoids the cycle
        return furina_v2_pilot.DEFAULT_DECIDER
    return d


# ----------------------------------------------------------------------
# The cards (sec.9, exact rows). One spec per base id; `make_card` builds a
# tier0 `Card` whose effects list is EMPTY and whose behaviour is
# `resolve_card`'s, keyed by id.
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Spec:
    name: str
    cost: int
    type: str                  # attack | skill | power
    rarity: str
    kind: str
    n: tuple = ()              # the printed numbers, base
    n_up: tuple | None = None  # the printed numbers, upgraded (None: no row)
    cost_up: int | None = None
    salon_summon: bool = False
    member: str = ""


CARDS: dict[str, Spec] = {
    # --- Starter (sec.9) ---
    "fv2_curtain_rise": Spec("Curtain Rise", 1, "attack", "basic",
                             "curtain_rise", (7, 3, 17), (10, 3, 21)),
    "fv2_rising_applause": Spec("Rising Applause", 1, "skill", "basic",
                                "gain", (3,), (4,)),
    # --- Common ---
    "fv2_take_the_stage": Spec("Take the Stage", 1, "skill", "common",
                               "take_the_stage", (1,), (1,), cost_up=0,
                               salon_summon=True),
    "fv2_gentilhomme_usher": Spec("Gentilhomme Usher", 1, "skill", "common",
                                  "summon_block", (4,), (6,),
                                  salon_summon=True, member="usher"),
    "fv2_surintendante_chevalmarin": Spec(
        "Surintendante Chevalmarin", 1, "skill", "common", "hydro_summon",
        (), None, salon_summon=True, member="chevalmarin"),
    "fv2_mademoiselle_crabaletta": Spec(
        "Mademoiselle Crabaletta", 1, "skill", "common", "summon_damage",
        (4,), (6,), salon_summon=True, member="crabaletta"),
    "fv2_encore": Spec("Encore!", 1, "attack", "common", "damage_cue",
                       (7,), (10,)),
    "fv2_places_everyone": Spec("Places, Everyone!", 1, "skill", "common",
                                "block_cue", (5,), (8,)),
    "fv2_stage_whisper": Spec("Stage Whisper", 1, "skill", "common",
                              "cue_draw", (1,), (2,)),
    "fv2_step_forward": Spec("Step Forward", 0, "skill", "common",
                             "step_forward", (3,), (5,)),
    # --- Uncommon ---
    "fv2_ousia_surge": Spec("Ousia Surge", 1, "attack", "uncommon",
                            "ousia", (4, 2), (4, 3)),
    "fv2_pneuma_refrain": Spec("Pneuma Refrain", 1, "skill", "uncommon",
                               "pneuma", (4, 2), (4, 3)),
    "fv2_bravura": Spec("Bravura", 1, "attack", "uncommon", "bravura",
                        (4, 2), (4, 3)),
    "fv2_thunderous_applause": Spec("Thunderous Applause", 1, "power",
                                    "uncommon", "thunderous", (1,), (1,)),
    "fv2_dress_rehearsal": Spec("Dress Rehearsal", 1, "power", "uncommon",
                                "rehearsal", (1,), (2,)),
    "fv2_guest_star_charlotte": Spec("Guest Star: Charlotte", 1, "skill",
                                     "uncommon", "guest", (0,),
                                     member="charlotte"),
    "fv2_guest_star_sigewinne": Spec("Guest Star: Sigewinne", 1, "skill",
                                     "uncommon", "guest", (0,),
                                     member="sigewinne"),
    # --- Rare ---
    "fv2_guest_star_neuvillette": Spec("Guest Star: Neuvillette", 2, "skill",
                                       "rare", "guest", (4,),
                                       member="neuvillette"),
    "fv2_guest_star_clorinde": Spec("Guest Star: Clorinde", 1, "skill",
                                    "rare", "guest", (2,), member="clorinde"),
    "fv2_guest_star_escoffier": Spec("Guest Star: Escoffier", 2, "skill",
                                     "rare", "guest", (3,),
                                     member="escoffier"),
    "fv2_guest_star_navia": Spec("Guest Star: Navia", 1, "skill", "rare",
                                 "guest", (2,), member="navia"),
}

#: PROBE-ONLY CONTROL (sec.9 probe 4: "a plain 1-cost 8 Block"). Not a slice
#: row and never offered; it exists so probe 4 has its plain twin.
PROBE_CONTROLS: dict[str, Spec] = {
    "fv2_probe_plain_block": Spec("Plain Block (probe control)", 1, "skill",
                                  "common", "block", (8,)),
}

ALL_SPECS = {**CARDS, **PROBE_CONTROLS}

UPGRADE_SUFFIX = "+"

STARTER_IDS: tuple[str, ...] = (
    "strike", "strike", "strike", "strike",
    "defend", "defend", "defend", "defend",
    "fv2_curtain_rise", "fv2_rising_applause",
)


def _base_id(card_id: str) -> str:
    return card_id[:-1] if card_id.endswith(UPGRADE_SUFFIX) else card_id


def spec_of(card) -> Spec | None:
    return ALL_SPECS.get(_base_id(getattr(card, "id", "")))


def numbers(card) -> tuple:
    spec = spec_of(card)
    if card.id.endswith(UPGRADE_SUFFIX):
        return spec.n_up
    return spec.n


def make_card(card_id: str):
    """A tier0 `Card` for one slice id (an upgraded id ends in `+`). A base
    Strike or Defend comes from the loader, which owns them."""
    from tier0.content import loader
    from tier0.engine.state import Card
    base = _base_id(card_id)
    if base not in ALL_SPECS:
        if base in ("strike", "defend"):
            return loader.get_card(card_id)
        raise KeyError(f"{card_id!r} is not a Furina re-founding slice row")
    spec = ALL_SPECS[base]
    up = card_id.endswith(UPGRADE_SUFFIX)
    if up and spec.n_up is None:
        raise KeyError(f"{base!r}: the paper gives this row no upgrade")
    cost = spec.cost_up if (up and spec.cost_up is not None) else spec.cost
    tags = [TAG]
    if spec.salon_summon:
        tags.append("fv2_salon_summon")
    return Card(id=card_id, name=spec.name + ("+" if up else ""), cost=cost,
                type=spec.type, rarity=spec.rarity, effects=[], tags=tags,
                character=CHARACTER,
                # sec.9: Thunderous Applause is Innate upgraded.
                innate=bool(up and spec.kind == "thunderous"))


def build_player(card_ids, hp: int | None = None, max_hp: int = HP,
                 variant: str | Variant = DEFAULT_VARIANT):
    """The slice's Furina: a fresh Player with `fv2` attached, playing the
    named design `variant` (see `VARIANTS`)."""
    from tier0.engine.state import Player
    p = Player(hp=max_hp if hp is None else hp, max_hp=max_hp,
               draw_pile=[make_card(cid) for cid in card_ids],
               element=ELEMENT, cadence=CADENCE, character_id=CHARACTER)
    p.fv2 = Fv2(variant=VARIANTS[variant] if isinstance(variant, str)
                else variant)
    return p


# ----------------------------------------------------------------------
# The ledger of Fanfare: gained, spent (a card's Spend), paid (a star's act).
# ----------------------------------------------------------------------
def gain(state, amount: int, source: str) -> None:
    if amount <= 0:
        return
    f = _fv(state)
    f.fanfare += amount
    f.gained_this_turn += amount
    f.ledger["gained"] += amount
    f.ledger["gained_by"][source] += amount
    state.emit("fv2_gain", amount=amount, source=source, fanfare=f.fanfare)


def spend(state, amount: int) -> bool:
    """A card's Spend N: only at the full price, and only a Spend feeds the
    spent-this-turn count and Clorinde's line (sec.8)."""
    f = _fv(state)
    if amount <= 0 or f.fanfare < amount:
        return False
    f.fanfare -= amount
    f.spent_this_turn += amount
    f.ledger["spent"] += amount
    f.ledger["spends"] += 1
    state.emit("fv2_spend", amount=amount, fanfare=f.fanfare)
    _clorinde_line(state)
    return True


def spend_all(state) -> int:
    """Bravura's "Spend all your Fanfare". Nothing held is no Spend."""
    f = _fv(state)
    held = f.fanfare
    if held <= 0:
        return 0
    spend(state, held)
    return held


def pay(state, member: str, amount: int) -> bool:
    """A star's payment for its act. NOT a Spend (sec.8)."""
    f = _fv(state)
    if amount <= 0:
        return True
    if f.fanfare < amount:
        return False
    f.fanfare -= amount
    f.ledger["paid"] += amount
    state.emit("fv2_paid", member=member, amount=amount, fanfare=f.fanfare)
    return True


def _clorinde_line(state) -> None:
    from tier0.engine import effects
    f = _fv(state)
    if "clorinde" not in f.stage or not state.living_enemies:
        return
    f.ledger["clorinde_procs"] += 1
    enemy = state.rng.choice(state.living_enemies)
    effects.deal_damage_to_enemy(state, enemy, CLORINDE_SPEND_DAMAGE,
                                 element="electro", powered=False,
                                 source="furina_v2/clorinde_line")


# ----------------------------------------------------------------------
# Acts, Bows, summons, Cues.
# ----------------------------------------------------------------------
def hydro_bonus(state, *, card: bool) -> int:
    """Neuvillette's on-stage line for one Hydro hit: the new line adds 2 to
    any Hydro damage (a card's or an act's); the old line adds 3 to a Hydro
    card's damage only. 0 when she is not on stage."""
    f = _fv(state)
    if "neuvillette" not in f.stage:
        return 0
    if f.variant.neuvillette_line == "hydro":
        return NEUVILLETTE_HYDRO_DAMAGE_BONUS
    return NEUVILLETTE_HYDRO_BONUS if card else 0


def _hit(state, enemy, amount: int, element) -> None:
    from tier0.engine import effects
    if element == "hydro":
        bonus = hydro_bonus(state, card=False)
        if bonus:
            amount += bonus
            _fv(state).ledger["neuvillette_bonus_hits"] += 1
    effects.deal_damage_to_enemy(state, enemy, amount, element=element,
                                 powered=False, source="furina_v2/act")


def act(state, member: str, *, free: bool = False) -> bool:
    """One performer's act. A star pays unless `free` (its Bow); a star that
    cannot pay skips and nothing is spent. Returns whether it acted."""
    p = state.player
    f = _fv(state)
    if state.over or not p.alive:
        return False
    if member in STARS and not free:
        price = STAR_PRICE[member]
        if not pay(state, member, price):
            f.ledger["star_skips"][member] += 1
            state.emit("fv2_star_skip", member=member, price=price,
                       fanfare=f.fanfare)
            return False
        f.ledger["star_acts"][member] += 1
    f.ledger["acts"][member] += 1
    r = f.rehearsal
    living = list(state.living_enemies)
    if member == "usher":
        p.block += ACT_USHER_BLOCK + r
    elif member == "chevalmarin":
        for enemy in living:
            _hit(state, enemy, ACT_CHEVALMARIN_DAMAGE + r, None)
    elif member == "crabaletta":
        if living:
            _hit(state, state.rng.choice(living),
                 ACT_CRABALETTA_DAMAGE + r, None)
    elif member == "neuvillette":
        for enemy in living:
            _hit(state, enemy, ACT_NEUVILLETTE_DAMAGE + r, "hydro")
    elif member == "clorinde":
        if living:
            _hit(state, state.rng.choice(living), f.variant.clorinde_act + r,
                 "electro")
    elif member == "escoffier":
        # "your Salon members act", front to back, each its ordinary act.
        for m in list(f.stage):
            if m in SALON:
                act(state, m)
    elif member == "navia":
        base = NAVIA_PER_SPENT * f.spent_this_turn
        if base > 0 and living:
            _hit(state, state.rng.choice(living), base + r, "geo")
    elif member == "charlotte":
        gain(state, CHARLOTTE_GAIN, "charlotte")
    elif member == "sigewinne":
        losses = int(state.player_damage_events) - f.sigewinne_mark
        p.block += (ACT_SIGEWINNE_BLOCK + SIGEWINNE_PER_HP_LOSS * max(0, losses)
                    + r)
        f.sigewinne_mark = int(state.player_damage_events)
    state.emit("fv2_act", member=member, free=free)
    return True


def bow(state, member: str) -> None:
    """Rule 3: the leaver's last act, free, then 1 Fanfare after it; then
    Thunderous Applause's draw."""
    f = _fv(state)
    f.ledger["bows"][member] += 1
    act(state, member, free=True)
    gain(state, BOW_FANFARE, "bow")
    if f.thunderous and not state.over:
        state.draw(f.thunderous)
        f.ledger["thunderous_draws"] += f.thunderous


def _seat(state, member: str) -> None:
    f = _fv(state)
    f.stage.append(member)
    if member == "sigewinne":
        f.sigewinne_mark = int(state.player_damage_events)


def summon(state, member: str) -> str:
    """Rule 4. Returns what happened: seated | repeat | evict | walk_on."""
    f = _fv(state)
    if member in NOT_IN_SLICE:
        raise ValueError(f"{member!r} is not in the re-founding sim slice")
    if member not in SALON and member not in GUESTS:
        raise ValueError(f"unknown performer {member!r}")
    f.ledger["summons"][member] += 1
    if member in GUESTS and member in f.stage:
        # "One of each; a second copy Bows it and returns it."
        f.ledger["guest_repeats"] += 1
        bow(state, member)
        return "repeat"
    if len(f.stage) < SEATS:
        _seat(state, member)
        return "seated"
    salon_seats = [i for i, m in enumerate(f.stage) if m in SALON]
    if salon_seats:
        leaver = f.stage.pop(salon_seats[0])
        bow(state, leaver)
        _seat(state, member)
        return "evict"
    if member in SALON:
        # The walk-on: one act (its free Bow act) + 1 Fanfare, no seat.
        f.ledger["walk_ons"] += 1
        state.emit("fv2_walk_on", member=member)
        bow(state, member)
        return "walk_on"
    leaver = f.stage.pop(0)              # a guest onto three guests
    bow(state, leaver)
    _seat(state, member)
    return "evict"


def cue(state, index) -> None:
    """Rule 7: the chosen performer acts now; a star pays as usual."""
    f = _fv(state)
    if index is None or not f.stage:
        f.ledger["cue_whiffs"] += 1
        return
    member = f.stage[index]
    f.ledger["cues"] += 1
    f.ledger["cues_on"][member] += 1
    act(state, member)


def move_to_front(state, index) -> None:
    f = _fv(state)
    if index is None or not (0 <= index < len(f.stage)):
        return
    f.stage.insert(0, f.stage.pop(index))


# ----------------------------------------------------------------------
# The engine's hooks. Each is a no-op for any player without `fv2`.
# ----------------------------------------------------------------------
def turn_open(state) -> None:
    """Top of Furina's turn: the flow counts and the once-a-turn latches
    reset (sec.8: they hold through the whole end-of-turn sequence before)."""
    if not live(state.player):
        return
    f = _fv(state)
    f.gained_this_turn = 0
    f.spent_this_turn = 0
    f.salon_summon_cards_this_turn = 0


def turn_start(state) -> None:
    """After the hand draw: Salon Solitaire on turn one, then Charlotte's
    extra card."""
    if not live(state.player):
        return
    f = _fv(state)
    if not f.opened:
        f.opened = True
        f.stage = [OPENING_MEMBER]
    if "charlotte" in f.stage:
        state.draw(CHARLOTTE_DRAW)
        f.ledger["charlotte_draws"] += CHARLOTTE_DRAW


def end_of_turn_acts(state) -> None:
    """Rule 1: front to back, over a snapshot of the stage."""
    if not live(state.player):
        return
    for member in list(_fv(state).stage):
        if state.over or not state.player.alive or not state.living_enemies:
            break
        act(state, member)


def free_salon_summon(state, card) -> bool:
    """Escoffier: "The first Salon summon card you play each turn costs 0"."""
    if not live(state.player):
        return False
    f = _fv(state)
    return ("fv2_salon_summon" in getattr(card, "tags", ())
            and "escoffier" in f.stage
            and f.salon_summon_cards_this_turn == 0)


def _card_damage(state, card, amount: int) -> None:
    """A card's own hit at the play's aim, through the shared damage op (so
    Strength, Weak, Vulnerable, Block and the cadence's element all apply).
    Neuvillette on stage adds her line's bonus when the hit carries Hydro."""
    from tier0.engine import effects
    fx = {"op": "damage", "amount": amount, "target": "enemy"}
    bonus = hydro_bonus(state, card=True)
    if bonus and effects._element_for(state, fx, card) == "hydro":
        fx["amount"] = amount + bonus
        _fv(state).ledger["neuvillette_bonus_hits"] += 1
    effects.OPS["damage"](state, fx, card)


def _card_block(state, card, amount: int) -> None:
    from tier0.engine import effects
    effects.OPS["block"](state, {"op": "block", "amount": amount}, card)


def resolve_card(state, card) -> None:
    """One slice card's printed text, in printed order."""
    if not live(state.player):
        return
    spec = spec_of(card)
    if spec is None:
        return
    f = _fv(state)
    n = numbers(card)
    if spec.salon_summon:
        if free_salon_summon(state, card):
            f.ledger["escoffier_free_summons"] += 1
        f.salon_summon_cards_this_turn += 1
    k = spec.kind
    d = _decider(state)
    if k == "curtain_rise":
        plain, price, big = n
        if f.fanfare >= price and d.curtain_spend(state, card, plain, big,
                                                  price):
            spend(state, price)
            _card_damage(state, card, big)
        else:
            _card_damage(state, card, plain)
    elif k == "gain":
        gain(state, n[0], "card")
    elif k == "take_the_stage":
        summon(state, state.rng.choice(SALON))
        state.draw(n[0])
    elif k == "summon_block":
        summon(state, spec.member)
        _card_block(state, card, n[0])
    elif k == "hydro_summon":
        from tier0.engine import effects
        effects.OPS["apply_aura"](state, {"op": "apply_aura",
                                          "element": "hydro",
                                          "target": "all_enemies"}, card)
        summon(state, spec.member)
    elif k == "summon_damage":
        summon(state, spec.member)
        _card_damage(state, card, n[0])
    elif k == "damage_cue":
        _card_damage(state, card, n[0])
        cue(state, d.cue_target(state))
    elif k == "block_cue":
        _card_block(state, card, n[0])
        cue(state, d.cue_target(state))
    elif k == "cue_draw":
        cue(state, d.cue_target(state))
        state.draw(n[0])
    elif k == "step_forward":
        move_to_front(state, d.front_target(state))
        _card_block(state, card, n[0])
    elif k == "ousia":
        base, per = n
        _card_damage(state, card, base + per * f.gained_this_turn)
    elif k == "pneuma":
        base, per = n
        _card_block(state, card, base + per * f.spent_this_turn)
    elif k == "bravura":
        base, per = n
        points = spend_all(state)
        _card_damage(state, card, base + per * points)
    elif k == "thunderous":
        f.thunderous += n[0]
    elif k == "rehearsal":
        f.rehearsal += n[0]
    elif k == "guest":
        summon(state, spec.member)
        gain(state, n[0], "guest_card")
    elif k == "block":
        _card_block(state, card, n[0])
    else:                                    # pragma: no cover
        raise ValueError(f"unknown slice kind {k!r}")


# ----------------------------------------------------------------------
# READINGS: where the paper is silent, the simplest reading consistent with
# it. Printed by the probe report and pinned by the slice tests.
# ----------------------------------------------------------------------
READINGS: tuple[str, ...] = (
    "A summoned performer takes the back-most free seat; on a full stage the "
    "leaver Bows first and the newcomer then takes the back seat (the rest "
    "close ranks).",
    "A second copy of a guest already on stage: that guest Bows (free act + "
    "1 Fanfare) and returns to the same seat; the card's own Fanfare still "
    "comes.",
    "Guest Star: Charlotte and Guest Star: Sigewinne give no Fanfare on "
    "arrival (sec.9 prints a Fanfare number only on the four Rare guests).",
    "\"Your Hydro cards\" (Neuvillette) means a card whose own damage carries "
    "Hydro under her cadence (furina.yaml: skill cadence, so her damaging "
    "Skills). In the slice that is Mademoiselle Crabaletta's 4 only; base "
    "Strike, Curtain Rise and the slice Attacks carry no element.",
    "Clorinde's line fires once per Spend event (Curtain Rise's Spend 3, "
    "Bravura's spend-all of at least 1), for a flat 4 Electro to a random "
    "enemy, not scaled by Rehearsal (it is a line, not an act). Bravura with "
    "0 Fanfare is not a Spend.",
    "Rehearsal adds to every damage and Block act's number, Bows included; "
    "Navia's act with 0 spent this turn deals nothing and Rehearsal does not "
    "make it a hit. Escoffier's act makes each Salon member on stage perform "
    "its own act (each takes Rehearsal once).",
    "Escoffier's free summon: the first Salon summon CARD played this turn "
    "(Take the Stage, Gentilhomme Usher, Surintendante Chevalmarin, "
    "Mademoiselle Crabaletta) costs 0 while she is on stage; a Salon summon "
    "card played before she arrived still counts as the first.",
    "Charlotte's \"draw 1 more card\" is paid as one extra draw right after "
    "the hand draw, when she is on stage at the start of the turn.",
    "Sigewinne counts HP-loss events (`state.player_damage_events`) since "
    "her last act, or since she took her seat if she has not acted.",
    "Card damage aims at the engine's bound aim (the lowest-HP enemy); "
    "\"random enemy\" acts draw from the combat rng.",
    "Step Forward with an empty stage only gains Block; a Cue with an empty "
    "stage does nothing but the card's plain effect.",
    "The performers' acts and Clorinde's line are unpowered (Furina's "
    "Strength and Weak do not touch them), as today's Stage acts are.",
    # --- pass two ---
    "Neuvillette's new line (\"Your Hydro damage deals 2 more\") adds 2 per "
    "Hydro HIT: per enemy on an ALL act, once on a single-target card. In "
    "the slice the Hydro hits are Mademoiselle Crabaletta's card damage "
    "(Skill cadence) and Neuvillette's own act; none of the Salon trio's "
    "acts carries an element (Chevalmarin's CARD applies Hydro, its act "
    "deals plain damage). It applies only while she is on stage: her own "
    "act at end of turn or on a Cue takes it, and a repeat-copy Bow (she "
    "stays seated) takes it, but her Bow on being evicted does not (she "
    "has left the stage before the Bow act).",
    "Clorinde's 6 or 8 is the act only; her Spend line stays a flat 4.",
)
