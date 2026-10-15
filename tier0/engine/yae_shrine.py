"""YAE MIKO, THE SHRINE AND THE PUBLISHING HOUSE -- the sim's rules twin.

Design: `review/active/yae-proposal-2026-10-12.md` (ruled 2026-10-12) and the
card paper `review/active/yae-card-paper-2026-10-13.md`, whose sec.2 is the
list of readings this module takes, ruled 2026-10-13. Rows: the `proto_ym_`
rows of `docs/prototype-surface.yaml`. C# twin:
`klee-mod/KleeCode/Powers/Prototype/YaeShrine.cs` (`YaeLaw` mirrors the
numbers below, `tools/lint_constant_parity.py`).

NO SWITCH, as Varka: she ships nowhere else, so every hook this module adds to
the shared engine is a dead branch for any player who is not Yae (`live`).
Her numbers live here rather than in `constants.py` so they move neither the
constant census nor the world stamp.

THE RULES AS MODELLED:
  * SAKURA: up to `sakura_cap` (`SAKURA_CAP`, plus 2 per Sakura
    Channeling) on a per-fight ledger (`YaeLedger.sakura`),
    each with a LEVEL and a TIMER (strikes left). SHRINE R2 (ruled
    2026-10-14): a plant creates a Sakura at the Level the card prints
    (`PLANT_LEVEL`, Grafted Branch its own), +1 per Fox's Mooncall, with 3
    strikes left, and does NOT level the others. With the shrine full a
    plant instead makes the OLDEST strike as its Last Bloom would, then
    refresh (3 strikes again) and gain 1 Level (2026-10-14)
    (`SCALING == "level"`, the paper's pick 1 (a)). Levels have no cap
    (Yae review r1, pick 2). Under `SCALING == "count"` (pick 1 (b),
    the proposal's placeholder) Levels are off: a Sakura strikes for the
    count-table value, a fourth plant replaces the oldest, and each Tenko
    raises a per-fight shrine bonus that every strike adds. The table
    is the proposal's placeholder lifted by 1 so both answers share a
    ceiling (15 a turn at three).
  * STRIKE: at the end of her turn each Sakura, oldest first, ALWAYS as
    Thunder (shrine r2: there is no Rite any more), deals
    `SAKURA_BASE + Level` Electro to one random living enemy (the Lure's
    enemy this turn, while it lives), unpowered (a pet's hit: no Strength, no
    Weak; Vulnerable and Block apply), source "card" (a Power's hit in the
    EB-495 matrix). Then its timer ticks; at 0 it withers. LAST BLOOM (Yae
    review r1, pick 1 (a)): a Sakura that withers first strikes once more
    as Thunder (a normal strike), then leaves; Fallen Petals
    banks it after the bloom. A strike that kills ends nothing else early.
  * TENKO (shrine r2): every Sakura strikes now, oldest first, as the
    card's KIND says: plain Tenko as Thunder; Tenko (Warding) as Block;
    Tenko (Wildfire) its Level to ALL; Tenko (Offering) 1 more card next
    turn. Then every timer is set back to 3 ([USER], 2026-10-14: "make
    Tenko keep resetting the duration"). Tenko with no Sakura does nothing.
  * EDIT: a card in hand (never the editing card itself, never a Status,
    Curse or kit card) gains one ANNOTATION for the combat, overwriting any
    it had: Red Ink (+3 damage and +3 Block, as the card's own riders),
    Footnote (draw 1 after its own effects), Deadline Extension (Retain), Fox
    Fire (after its own effects, 4 Electro to a random enemy, unpowered),
    Sakura Seal (after its own effects, plant a Sakura), Royalties (after
    its own effects, gain 1 Energy), Reprint (the first play each combat is
    played twice, Glam's rule: `reprint_replays`, read by
    `combat._finish_play`'s replay loop). The target is the
    pilot's (`YaeLedger.edit_choice`); the default reading is `_edit_target`.
    "Annotated" is any card carrying one (`is_annotated`), a Published one
    included.
  * PUBLISH: the card's Annotation is marked permanent (`ym_published`). The
    sim's fights are single combats; the run harness (`tools/yae_expansion_sim`)
    carries a Published Annotation into the next fight by deck slot, and
    Meditations of a Yako Publishes after an elite or boss fight (ruled
    2026-10-14; it was a rest-site option): it reads the DRAFTS that fight
    left (`YaeLedger.drafts`, slot -> last Annotation) and offers each slot
    not yet Published (`publish_choices`, `publish_after_fight`).
  * POWERS (self, by name): Sakura Grove (at her turn start, after Yakan
    Offering, each Sakura gains n Levels), Edict of Cleansing
    (+n on a damage strike at an enemy that is Weak or wears Pyro, Hydro or
    Cryo), Serialization (Block per Annotated card played, unpowered), Fox's Mooncall (plant
    n Levels higher), Yakan Offering (plant at the start of her turn, after
    the draw), Sakura Channeling ("You can have 2 more Sakura": its amount,
    2 per copy, adds to `SAKURA_CAP` for the fight, `sakura_cap`),
    Editor-in-Chief (after an Annotated card's play, the highest-Level Sakura
    strikes), Fallen Petals
    (Energy per wither; its upgrade's power also draws).

  * TENKO KINDS (shrine r2, `review/active/yae-design-axes-2026-10-14.md`,
    ruled 2026-10-14; the persistent Rite is gone): a strike is one of
    Thunder 2 + Level Electro to a random enemy; Warding 2 + Level Block
    (unpowered); Wildfire Level Electro to ALL; Offering, 1 more card
    drawn at the start of her next turn. Only a typed Tenko strikes in the
    last three. Edict pays on damage strikes at an enemy that is Weak or
    will react. The Lure aims single-target damage strikes.
  * SAKURA ANNOTATIONS: a Sakura may carry one of Red Ink (its strike is 3
    bigger, not in Offering, as Sakura Grove), Fox Fire (4 Electro
    to a random enemy whenever it strikes) or Deadline Extension (its timer
    never ticks, so it never withers), written by "Edit your newest /
    oldest / every Sakura" (`edit_sakura`). A new one replaces the old; it
    lasts the Sakura's life and is never Published.
  * RED INK ON A PLANTING CARD (ruled 2026-10-14, the design-axes doc):
    Red Ink on a card that plants a Sakura and itself deals no damage and
    gives no Block passes to every Sakura that play plants (`inherits`); a
    full-shrine plant that only levels plants nothing, so nothing inherits.
    THE DEAD-EDIT FILTER: an Edit, Reborn as Guuji Yae and the after-elite
    Publish offer skip a card the Annotation would do nothing on
    (`affects`): Red Ink is dead on a card that deals no damage, gives no
    Block and plants nothing; Reprint on a card that cannot be played. C#
    twin: `YaeAnnotationReach`.
  * WITHERS: Fallen Petals' Energy (and its upgrade's draw) are paid at
    the start of her next turn, beside Offering's draw: a Sakura withers at
    the end of her turn, when Energy would be lost.

READINGS TAKEN WHERE THE PAPER LEAVES ROOM (each in the builder's report):
  * Tier 0 seats one player, so every Sakura is hers.
  * `damage_per_sakura` and `damage_per_annotated` are ONE powered hit of
    the card (Strength counts, flat Attack riders ride it) carrying Electro.
  * Reborn as Guuji Yae's one Annotation is the pilot's (`reborn_choice`),
    else the row's printed default (Sakura Seal).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

CHARACTER = "yae"
HP = 72
ELEMENT = "electro"
CADENCE = "catalyst"

# --- the shrine (C# twin: `YaeLaw`, Powers/Prototype/YaeShrine.cs) ---
SAKURA_CAP = 3
SAKURA_TURNS = 3            # strikes a Sakura has when planted or refreshed
SAKURA_BASE = 2             # a strike deals this plus the Sakura's Level
PLANT_LEVEL = 1             # +1 per Fox's Mooncall; Levels have no cap
#: Pick 1 (b): the proposal's placeholder, a strike by the COUNT standing.
COUNT_TABLE = {1: 3, 2: 4, 3: 5}   # the same ceiling as (a), paired
COUNT_TENKO_BONUS = 1       # (b): each Tenko adds 1 to every later strike
#: "level" (pick 1 (a), the default) or "count" (pick 1 (b)).
SCALING = "level"

# --- the Annotations ---
RED_INK, FOOTNOTE, DEADLINE, FOX_FIRE, SAKURA_SEAL, ROYALTIES, REPRINT = (
    "red_ink", "footnote", "deadline", "fox_fire", "sakura_seal",
    "royalties", "reprint")
ANNOTATIONS = (RED_INK, FOOTNOTE, DEADLINE, FOX_FIRE, SAKURA_SEAL, ROYALTIES,
               REPRINT)
ROYALTIES_ENERGY = 1
RED_INK_AMOUNT = 3
FOX_FIRE_DAMAGE = 4
#: What a Publish is worth to the default pilot, best first.
PUBLISH_ORDER = (REPRINT, SAKURA_SEAL, ROYALTIES, FOOTNOTE, RED_INK, FOX_FIRE,
                 DEADLINE)

# --- the powers her rows apply (`apply_power`, target self) ---
SAKURA_GROVE = "ym_sakura_grove"
EDICT = "ym_edict_of_cleansing"
SERIALIZATION = "ym_serialization"
MOONCALL = "ym_foxs_mooncall"
YAKAN_OFFERING = "ym_yakan_offering"
CHANNELING = "ym_sakura_channeling"
EDITOR_IN_CHIEF = "ym_editor_in_chief"
#: Auras an Electro strike reacts with (Edict of Cleansing's read).
REACTING_AURAS = ("pyro", "hydro", "cryo")

# --- the relic, as the sim spells a starting relic (`Player.relic_hooks`) ---
MEDITATIONS = "meditations_of_a_yako"
MEDITATIONS_UPGRADED = "meditations_of_a_yako+"
#: Annotations one after-elite Publish may keep (C# `PublishCount`):
#: Enlightened Blessing, the Orobas upgrade, keeps up to two.
PUBLISH_COUNT = {MEDITATIONS: 1, MEDITATIONS_UPGRADED: 2}
#: The rooms whose win offers it (C# `YaeEditing.OffersPublish`).
PUBLISH_ROOMS = ("elite", "boss")

# --- the Tenko kinds (shrine r2, ruled 2026-10-14; C# `YaeTenkoKind`) ---
THUNDER, WARDING, WILDFIRE, OFFERING = (
    "thunder", "warding", "wildfire", "offering")
TENKO_KINDS = (THUNDER, WARDING, WILDFIRE, OFFERING)
#: Offering's strike: this many more cards at the start of her next turn.
OFFERING_DRAW = 1
#: The Annotations a Sakura can carry (`edit_sakura`).
SAKURA_ANNOTATIONS = (RED_INK, FOX_FIRE, DEADLINE)
SAKURA_EDIT_ENDS = ("newest", "oldest", "every")
FALLEN_PETALS = "ym_fallen_petals"
FALLEN_PETALS_PLUS = "ym_fallen_petals_plus"

ID_PREFIX = "proto_ym_"
STARTER_IDS: tuple[str, ...] = (
    "strike", "strike", "strike", "strike",
    "defend", "defend", "defend", "defend",
    "proto_ym_yakan_evocation", "proto_ym_proofread",
)

#: The `yae` op's kinds and the numeric fields each one prints.
KIND_FIELDS = {
    "plant": ("amount",),
    "tenko": (),
    "extend": ("amount",),
    "level_up": ("amount",),
    "edit": ("amount",),
    "edit_all": (),
    "publish": (),
    "lure": (),
    "damage_per_sakura": ("base", "per"),
    "block_per_sakura": ("base", "per"),
    "damage_per_annotated": ("base", "per"),
    "block_per_annotated": ("base", "per"),
    "annotated_strike": ("base", "amount"),
    "fox_fire": (),
    # The design axes (ruled 2026-10-14).
    "edit_sakura": ("amount",),
    "plant_level": ("amount",),
    "strike_if_weak": (),
}
KINDS = frozenset(KIND_FIELDS)
KIND_TARGETS = {
    "lure": "enemy", "damage_per_sakura": "enemy",
    "damage_per_annotated": "enemy", "annotated_strike": "enemy",
    "strike_if_weak": "enemy",
}
#: Kinds that take an `annotation:` name.
ANNOTATION_KINDS = frozenset({"edit", "edit_all", "edit_sakura"})
#: `as:` names a typed Tenko's kind (shrine r2); absent, it is Thunder.
OP_FIELDS = frozenset({"op", "kind", "amount", "base", "per", "target",
                       "annotation", "as", "which"})


@dataclass
class Sakura:
    level: int
    turns_left: int
    seq: int                      # planting order, the ledger's clock
    annotation: Optional[str] = None   # Red Ink, Fox Fire or Deadline


@dataclass
class YaeLedger:
    """Per-fight state, hung on the Player (`Player.yae_ledger`)."""
    sakura: list = field(default_factory=list)
    seq: int = 0
    shrine_bonus: int = 0         # SCALING == "count": +1 per Tenko
    lure: object = None           # this turn's aimed enemy, or None
    pending_draw: int = 0         # Offering: cards at her next turn start
    pending_withers: int = 0      # Fallen Petals: withers to pay next turn
    strikes: int = 0              # this combat
    strike_damage: int = 0        # printed amounts, this combat
    edits: int = 0
    #: Reprint (2026-10-14): the cards (by `id`) whose Reprint has spent
    #: its replay this fight. Per fight, so a Published Reprint plays twice
    #: once every combat; a fresh Edit takes the card off it again.
    reprinted: set = field(default_factory=set)
    #: slot -> last Annotation the fight left on that deck card (the
    #: evidence the after-elite Publish reads).
    drafts: dict = field(default_factory=dict)
    # --- the pilot's choices (None: the default reading) ---
    edit_choice: object = None    # (state, card, annotation) -> card | None
    reborn_choice: Optional[str] = None


# --------------------------------------------------------------------------
#  Who is Yae
# --------------------------------------------------------------------------

def live(player) -> bool:
    return getattr(player, "character_id", "") == CHARACTER


def ledger(player) -> Optional[YaeLedger]:
    if not live(player):
        return None
    led = getattr(player, "yae_ledger", None)
    if led is None:
        led = YaeLedger()
        player.yae_ledger = led
    return led


def open_combat(player) -> None:
    """`combat.run_fight`: a fresh shrine per fight."""
    if live(player):
        player.yae_ledger = YaeLedger()


def _power(player, name: str) -> int:
    return int(player.powers.get(name, 0))


def _block(state, amount: int, reason: str) -> None:
    """Unpowered Block (no Dexterity, no Frail), the Powers' door."""
    if amount <= 0:
        return
    state.player.block += amount
    state.emit("block", amount=amount)
    state.emit("yae_block", amount=amount, reason=reason)


# --------------------------------------------------------------------------
#  The shrine
# --------------------------------------------------------------------------

def sakura_count(player) -> int:
    led = ledger(player)
    return 0 if led is None else len(led.sakura)


def sakura_cap(player) -> int:
    """How many Sakura may stand: 3, plus Sakura Channeling's amount (2 per
    copy, designed 2026-10-14). The full-shrine rule fires at this. C#
    twin: `YaeShrine.MaxSakura`."""
    return SAKURA_CAP + _power(player, CHANNELING)


def _plant_level(player) -> int:
    """1, plus 1 for each Fox's Mooncall ("planted 1 Level higher")."""
    return PLANT_LEVEL + _power(player, MOONCALL)


def plant(state, n: int = 1, reason: str = "plant",
          level: Optional[int] = None,
          annotation: Optional[str] = None) -> None:
    """Plant `n` Sakura, one at a time. SHRINE R2 (ruled 2026-10-14): a
    plant creates a Sakura at the card's Level (`level`, Grafted Branch;
    else `PLANT_LEVEL`) plus Fox's Mooncall's bonus, and does not level the
    others. With the shrine full (3 standing, plus 2 per Sakura Channeling:
    `sakura_cap`) the OLDEST first strikes once exactly as its Last Bloom
    would (Thunder, its Lure, Red Ink and Fox Fire as usual; 2026-10-14),
    then refreshes (3 strikes again) and gains 1 Level instead (Mooncall
    does not add to that Level). No Level cap. A two-plant into a full
    shrine does it per plant.
    `annotation`: what each NEW Sakura inherits from the planting card (Red
    Ink on a card that only plants, `inherited`); a refreshed oldest keeps
    its own."""
    led = ledger(state.player)
    if led is None:
        return
    cap = sakura_cap(state.player)
    for _ in range(n):
        if len(led.sakura) >= cap:
            if SCALING == "level":
                oldest = led.sakura[0]
                strike(state, oldest, "full_shrine")   # as its Last Bloom
                oldest.turns_left = SAKURA_TURNS
                oldest.level += 1
                state.emit("yae_level", reason=reason,
                           levels=[s.level for s in led.sakura])
                continue
            led.sakura.pop(0)                       # (b): the oldest goes
        led.seq += 1
        start = _plant_level(state.player)
        if level is not None:
            start = max(start, level + start - PLANT_LEVEL)   # Mooncall too
        led.sakura.append(Sakura(
            level=start, turns_left=SAKURA_TURNS, seq=led.seq,
            annotation=(annotation if annotation in SAKURA_ANNOTATIONS
                        else None)))
        state.emit("yae_plant", reason=reason, count=len(led.sakura),
                   levels=[s.level for s in led.sakura])


def strike_size(state, s: Sakura, rite: Optional[str] = None) -> int:
    """One strike's size as `rite` (a Tenko kind; Thunder by default),
    before Edict: Thunder and Warding 2 + Level, Wildfire Level, Offering
    1; a Red Ink Sakura's 3 adds to all but Offering (Claude, 2026-10-14).
    No global bonus: Grove and Mikage Thunder raise Levels."""
    p = state.player
    led = ledger(p)
    rite = rite or THUNDER
    if rite == OFFERING:
        size = OFFERING_DRAW
    else:
        if SCALING == "level":
            size = SAKURA_BASE + s.level
        else:
            size = (COUNT_TABLE[min(SAKURA_CAP, len(led.sakura))]
                    + led.shrine_bonus)
        if rite == WILDFIRE:
            size -= SAKURA_BASE
        if s.annotation == RED_INK:
            size += RED_INK_AMOUNT
    return size


#: THE LIVE TENKO CLAUSE (shrine r2, 2026-10-14; C# twin `YaeShrineFace`).
#: In combat a Tenko card says what its Tenko would do now, summed over the
#: Sakura standing: "Tenko (12 damage)", "Tenko (Warding: 12 damage, 12
#: Block)" (the strike, then the kind's bonus, 2026-10-14); with
#: none standing "Tenko (no Sakura)", "Tenko (Warding, no Sakura)". Before
#: Edict and Fox Fire: the Tenko's own job only.
TENKO_FACE = {THUNDER: "{n} damage", WARDING: "{n} Block",
              WILDFIRE: "{n} to each enemy", OFFERING: "draw {n}"}
#: A typed Tenko's printed name, "Tenko (Warding)".
TENKO_NAME = {WARDING: "Warding", WILDFIRE: "Wildfire", OFFERING: "Offering"}
NO_SAKURA = " (no Sakura)"
NO_SAKURA_TYPED = ", no Sakura"


def tenko_total(state, kind: str = THUNDER) -> int:
    """What every Sakura standing would strike for as `kind`, summed."""
    led = ledger(state.player)
    if led is None:
        return 0
    return sum(strike_size(state, s, kind) for s in led.sakura)


def tenko_words(kind: str, damage: int, bonus: int = 0) -> str:
    """The clause for the strikes' damage and a typed kind's bonus; at 0
    damage (no Sakura standing) the "no Sakura" words. Thunder's stands in
    its own brackets, a typed kind's inside the kind's ("Tenko (Warding: 5
    damage, 5 Block)"). PURE."""
    typed = kind != THUNDER
    if damage <= 0:
        return NO_SAKURA_TYPED if typed else NO_SAKURA
    strike = TENKO_FACE[THUNDER].format(n=damage)
    if not typed:
        return f" ({strike})"
    return f": {strike}, {TENKO_FACE[kind].format(n=bonus)}"


def tenko_line(state, kind: str = THUNDER) -> str:
    """A Tenko card's live clause; "" off a Yae."""
    if ledger(state.player) is None:
        return ""
    return tenko_words(kind, tenko_total(state, THUNDER),
                       tenko_total(state, kind))


def edict_applies(target) -> bool:
    """Edict of Cleansing's read: the enemy is Weak, or wears an aura an
    Electro strike reacts with."""
    return target is not None and (
        target.aura in REACTING_AURAS
        or int(target.powers.get("weak", 0)) > 0)


def strike_damage(state, s: Sakura, target) -> int:
    """A Thunder strike's damage at `target` (Edict included)."""
    dmg = strike_size(state, s, THUNDER)
    if edict_applies(target):
        dmg += _power(state.player, EDICT)
    return dmg


def _aim(state, aim=None):
    if aim is not None and aim.alive:
        return aim
    led = ledger(state.player)
    if led.lure is not None and led.lure.alive:
        return led.lure
    living = list(state.living_enemies)
    return state.rng.choice(living) if living else None


def _hit(state, target, size: int, reason: str, rite: str) -> None:
    """One damage strike's hit: Electro, unpowered, Edict on top."""
    from tier0.engine import effects                # late: cycle
    led = ledger(state.player)
    dmg = size + (_power(state.player, EDICT) if edict_applies(target) else 0)
    if dmg <= 0:
        return
    led.strike_damage += dmg
    state.emit("yae_sakura_hit", reason=reason, rite=rite, amount=dmg,
               target=target.name)
    effects.deal_damage_to_enemy(state, target, dmg, element=ELEMENT,
                                 source="card", powered=False)


def fox_fire(state, source: str) -> None:
    """Fox Fire: 4 Electro to a random enemy, unpowered, not aimed."""
    from tier0.engine import effects                # late: cycle
    living = list(state.living_enemies)
    if not living:
        return
    target = state.rng.choice(living)
    state.emit("yae_fox_fire", card=source, target=target.name)
    effects.deal_damage_to_enemy(state, target, FOX_FIRE_DAMAGE,
                                 element=ELEMENT, source="card",
                                 powered=False)


def strike(state, s: Sakura, reason: str, aim=None,
           rite: str = THUNDER) -> None:
    """One Sakura's strike: a Thunder hit, plus a typed Tenko's bonus as
    `rite` (Warding Block, Wildfire Level to ALL, Offering a card next turn),
    then the Sakura's own Fox Fire, once. `aim` (Kitsune
    Pounce) names the enemy a single-target damage strike lands on, ahead
    of the Lure."""
    led = ledger(state.player)
    if not state.living_enemies:
        return
    damage = strike_size(state, s, THUNDER)
    size = strike_size(state, s, rite)
    led.strikes += 1
    target = _aim(state, aim)
    state.emit("yae_sakura_strike", reason=reason, level=s.level,
               amount=damage, rite=rite,
               target=None if target is None else target.name)
    # Every strike is a Thunder hit; a typed Tenko's ALSO does its kind
    # ([USER], 2026-10-14: "Hmm, the double strike makes Tenko effects quite
    # strong, but let's try it and see what happens").
    if target is not None:
        _hit(state, target, damage, reason, THUNDER)
    if rite == WARDING:
        _block(state, size, "warding")
    elif rite == WILDFIRE:
        for e in list(state.living_enemies):
            _hit(state, e, size, reason, rite)
    elif rite == OFFERING:
        led.pending_draw += size
    if s.annotation == FOX_FIRE:
        fox_fire(state, "sakura")


def strike_all(state, reason: str, rite: str = THUNDER) -> None:
    led = ledger(state.player)
    for s in list(led.sakura):
        if not state.living_enemies:
            break
        strike(state, s, reason, rite=rite)


def edit_sakura(state, which: str, n: int, annotation: str) -> None:
    """"Edit your newest / oldest Sakura" (`n` from that end), "Edit every
    Sakura" (`which` every): the Annotation replaces any the Sakura
    carried."""
    if annotation not in SAKURA_ANNOTATIONS:
        raise ValueError(f"no Sakura reading for {annotation!r}")
    led = ledger(state.player)
    ordered = led.sakura if which == "oldest" else list(reversed(led.sakura))
    if which == "every":
        n = len(ordered)
    for s in ordered[:n]:
        s.annotation = annotation
        state.emit("yae_sakura_annotate", seq=s.seq, annotation=annotation)


def highest(led):
    """Editor-in-Chief's Sakura: the highest Level, the oldest on a tie."""
    if not led.sakura:
        return None
    return max(led.sakura, key=lambda s: (s.level, -s.seq))


def tenko(state, kind: str = THUNDER) -> None:
    """Every Sakura strikes now as Thunder, plus `kind`'s bonus on a typed
    Tenko (2026-10-14), then every timer is set back to 3 ([USER], 2026-10-14: "make
    Tenko keep resetting the duration")."""
    if kind not in TENKO_KINDS:
        raise ValueError(f"unknown Tenko kind {kind!r}")
    led = ledger(state.player)
    if led is None or not led.sakura:
        return
    state.emit("yae_tenko", count=len(led.sakura), kind=kind)
    strike_all(state, "tenko", kind)
    for s in led.sakura:
        s.turns_left = SAKURA_TURNS
    if SCALING == "count":
        led.shrine_bonus += COUNT_TENKO_BONUS


def extend(state, n: int) -> None:
    led = ledger(state.player)
    for s in led.sakura:
        s.turns_left += n


def level_up(state, n: int) -> None:
    """"Each Sakura gains a Level" (n Levels), no cap."""
    led = ledger(state.player)
    for s in led.sakura:
        s.level += n


def grove(state, n: int) -> None:
    """Sakura Grove (shrine r2): "each Sakura gains a Level" (n Levels)."""
    led = ledger(state.player)
    if led.sakura:
        for s in led.sakura:
            s.level += n
        state.emit("yae_level", reason="sakura_grove",
                   levels=[s.level for s in led.sakura])


def turn_start(state) -> None:
    """`combat._player_turn`, post-draw: the Lure expires; Yakan Offering
    plants; then Sakura Grove levels every Sakura."""
    led = ledger(state.player)
    if led is None:
        return
    led.lure = None
    # Offering's cards and Fallen Petals' Energy (and draw), owed since the
    # end of her last turn.
    withers, led.pending_withers = led.pending_withers, 0
    p = state.player
    energy = withers * (_power(p, FALLEN_PETALS) + _power(p, FALLEN_PETALS_PLUS))
    draw = led.pending_draw + withers * _power(p, FALLEN_PETALS_PLUS)
    led.pending_draw = 0
    if energy:
        p.energy += energy
        state.emit("energy", amount=energy)
    if draw:
        state.draw(draw)
    for _ in range(_power(state.player, YAKAN_OFFERING)):
        plant(state, 1, "yakan_offering")
    levels = _power(state.player, SAKURA_GROVE)
    if levels:
        grove(state, levels)


def turn_end(state) -> None:
    """`combat`'s player turn end: the strikes, then the timers tick. LAST
    BLOOM (Yae review r1, pick 1 (a), ruled 2026-10-14): each Sakura whose
    timer ran out, oldest first, strikes once more as Thunder, then withers
    (and Fallen Petals banks it)."""
    led = ledger(state.player)
    if led is None:
        return
    strike_all(state, "turn_end")
    for s in led.sakura:
        if s.annotation != DEADLINE:          # Deadline Extension: no wither
            s.turns_left -= 1
    withered = [s for s in led.sakura if s.turns_left <= 0]
    for s in withered:
        strike(state, s, "bloom")             # still standing as it blooms
        led.sakura.remove(s)
        led.pending_withers += 1
        state.emit("yae_wither", count=1, standing=len(led.sakura))
    _record_drafts(state)


def _record_drafts(state) -> None:
    """The manuscript: every Annotated deck card's slot -> its Annotation,
    read at the end of each turn so a fight that ends mid-turn still left
    it. A Published card is its own permanence."""
    led = ledger(state.player)
    p = state.player
    for pile in (p.hand, p.draw_pile, p.discard_pile, p.exhaust_pile):
        for c in pile:
            slot = getattr(c, "ym_slot", None)
            ann = getattr(c, "ym_annotation", None)
            if slot is not None and ann:
                led.drafts[slot] = ann


# --------------------------------------------------------------------------
#  The publishing house
# --------------------------------------------------------------------------

def is_annotated(card) -> bool:
    return bool(getattr(card, "ym_annotation", None))


def annotated_in_hand(state) -> int:
    return sum(1 for c in state.player.hand if is_annotated(c))


def annotate(state, card, name: str, reason: str = "edit") -> None:
    """Give `card` one Annotation for the combat, overwriting any it had."""
    if name not in ANNOTATIONS:
        raise ValueError(f"unknown Annotation {name!r}")
    if getattr(card, "ym_base_retain", None) is None:
        card.ym_base_retain = bool(card.retain)
    card.ym_annotation = name
    if state is not None and name == REPRINT:
        led = ledger(state.player)
        if led is not None:
            led.reprinted.discard(id(card))   # a fresh Reprint, unspent
    # The draft (pick 2 (a)): the C# writes it at every Edit
    # (`YaeEditing.Annotate`); the end-of-turn sweep below stays as the
    # backstop for a card annotated outside an Edit.
    slot = getattr(card, "ym_slot", None)
    if state is not None and slot is not None and reason != "published":
        led = ledger(state.player)
        if led is not None:
            led.drafts[slot] = name
    card.enchant_damage = RED_INK_AMOUNT if name == RED_INK else 0
    card.enchant_block = RED_INK_AMOUNT if name == RED_INK else 0
    card.retain = card.ym_base_retain or name == DEADLINE
    if name == FOOTNOTE:
        card.enchant_effects = [{"op": "draw", "amount": 1}]
    elif name == FOX_FIRE:
        card.enchant_effects = [{"op": "yae", "kind": "fox_fire"}]
    elif name == SAKURA_SEAL:
        card.enchant_effects = [{"op": "yae", "kind": "plant", "amount": 1}]
    elif name == ROYALTIES:
        card.enchant_effects = [{"op": "energy", "amount": ROYALTIES_ENERGY}]
    else:
        card.enchant_effects = []
    if state is not None:
        state.emit("yae_annotate", card=card.id, annotation=name,
                   reason=reason)


#: The `yae` kinds whose play plants a Sakura (C# `ISakuraPlanterCard`,
#: `gen_klee_cards.YAE_PLANT_KINDS`).
PLANT_KINDS = frozenset({"plant", "plant_level"})


def _walk(effects):
    """Every effect, `conditional` branches and `choose_one` modes
    included."""
    for fx in effects or ():
        yield fx
        if fx.get("op") == "conditional":
            yield from _walk(fx.get("then"))
            yield from _walk(fx.get("else"))
        if fx.get("op") == "choose_one":
            for mode in fx.get("modes") or ():
                yield from _walk(mode.get("effects"))


def plants_sakura(card) -> bool:
    """Does the card's own play plant a Sakura?"""
    return any(fx.get("op") == "yae" and fx.get("kind") in PLANT_KINDS
               for fx in _walk(card.effects))


def deals_damage(card) -> bool:
    """An Attack, or any card with a damage op (the C# reads a damage var):
    widened past Sharp's Attack door so a Skill that hits stays editable."""
    return card.type == "attack" or any(
        fx.get("op") == "damage" for fx in _walk(card.effects))


#: The `yae` kinds that give the card's own Block (C# `IYaeBlockCard`).
BLOCK_KINDS = frozenset({"block_per_sakura", "block_per_annotated"})


def gives_block(card) -> bool:
    """Nimble's door (the game's `GainsBlock`), or a `yae` kind that gives
    the card's own Block (Print Run), which Red Ink rides too."""
    from tier0.content import enchantments          # late: cycle
    return enchantments._gains_block(card) or any(
        fx.get("op") == "yae" and fx.get("kind") in BLOCK_KINDS
        for fx in _walk(card.effects))


def playable(card) -> bool:
    """Can the card be played at all? A Status or Curse, or an Unplayable
    card, never is (C# `YaeAnnotationReach.Playable`)."""
    return not card.is_junk and "unplayable" not in (card.tags or ())


def affects(card, annotation: str) -> bool:
    """Would `annotation` do anything on `card`? Red Ink needs damage, Block
    or a plant; Reprint needs a playable card. C#
    `YaeAnnotationReach.Affects`."""
    if annotation == REPRINT:
        return playable(card)
    return (annotation != RED_INK or deals_damage(card) or gives_block(card)
            or plants_sakura(card))


def reprint_replays(state, card) -> int:
    """Reprint, the base game's Glam ([USER], 2026-10-14: "Let's bump it to
    'Play it twice.'"): "The first time this card is played each combat,
    play it twice." The extra play count, 1 or 0, spent on the first play
    this fight. C# `ReprintAnnotation.EnchantPlayCount`."""
    if getattr(card, "ym_annotation", None) != REPRINT:
        return 0
    led = ledger(state.player)
    if led is None or id(card) in led.reprinted:
        return 0
    led.reprinted.add(id(card))
    state.emit("yae_reprint", card=card.id)
    return 1


def inherits(card) -> bool:
    """Does the card's Annotation pass to the Sakura it plants? Red Ink, on
    a card that plants and deals no damage and gives no Block."""
    return (getattr(card, "ym_annotation", None) == RED_INK
            and plants_sakura(card) and not deals_damage(card)
            and not gives_block(card))


def inherited(card) -> Optional[str]:
    return RED_INK if inherits(card) else None


def _editable(state, editor, annotation: Optional[str] = None) -> list:
    """The cards an Edit can reach; with `annotation`, only those it would
    do something on (the dead-edit filter)."""
    return [c for c in state.player.hand
            if c is not editor and not c.kit_card and not c.is_junk
            and (annotation is None or affects(c, annotation))]


def _edit_reaches(state, editor, annotation: str) -> list:
    """The cards an Edit (the chooser and Reborn as Guuji Yae) can reach:
    `_editable` with the dead-edit filter, never a card with a Published
    Annotation (shrine-r2 seat, 2026-10-14: an Edit used to override it for
    the combat). C# twin: `YaeEditing.EditReaches`."""
    return [c for c in _editable(state, editor, annotation)
            if not getattr(c, "ym_published", False)]


def _has_op(card, op: str) -> bool:
    return any(fx.get("op") == op for fx in card.effects)


def _edit_target(state, editor, annotation: str):
    """The default reading of "a card in your hand": Red Ink goes on the
    hardest-hitting Attack (most hits), else a Block card; Deadline on the
    dearest card; Reprint on the dearest card, an Attack first; the play
    riders on the cheapest card. A card not yet
    Annotated is preferred, so an Edit overwrites only when it must."""
    cands = _edit_reaches(state, editor, annotation)
    if not cands:
        return None
    fresh = [c for c in cands if not is_annotated(c)] or cands

    def cost(c):
        return c.cost if isinstance(c.cost, int) else 1

    if annotation == RED_INK:
        hits = [c for c in fresh if _has_op(c, "damage")]
        if hits:
            return max(hits, key=lambda c: (
                max((int(fx.get("times", 1)) if isinstance(
                    fx.get("times", 1), int) else 1)
                    for fx in c.effects if fx.get("op") == "damage"),
                -cost(c)))
        blocks = [c for c in fresh if _has_op(c, "block")]
        return blocks[0] if blocks else fresh[0]
    if annotation == DEADLINE:
        return max(fresh, key=cost)
    if annotation == REPRINT:
        # The card most worth a second play: the dearest, an Attack first.
        return max(fresh, key=lambda c: (cost(c), c.type == "attack"))
    plain = [c for c in fresh if not c.exhaust] or fresh
    return min(plain, key=cost)


def edit(state, editor, annotation: str, n: int = 1) -> None:
    led = ledger(state.player)
    for _ in range(n):
        chooser = led.edit_choice or _edit_target
        target = chooser(state, editor, annotation)
        if target is None or target not in _edit_reaches(state, editor,
                                                     annotation):
            return
        annotate(state, target, annotation)
        led.edits += 1


def edit_all(state, editor, default: str) -> None:
    """Reborn as Guuji Yae: one Annotation (the pilot's `reborn_choice`,
    else the row's) on every other card in hand."""
    led = ledger(state.player)
    name = led.reborn_choice or default
    cards = _edit_reaches(state, editor, name)
    for c in cards:
        annotate(state, c, name, "reborn")
    if cards:
        led.edits += len(cards)


def publish(state, editor) -> None:
    """The Seven Glamours: the best Annotated card in hand is Published."""
    cands = [c for c in _editable(state, editor) if is_annotated(c)]
    if not cands:
        return
    best = min(cands, key=lambda c: PUBLISH_ORDER.index(c.ym_annotation))
    best.ym_published = True
    state.emit("yae_publish", card=best.id, annotation=best.ym_annotation)


def offers_publish(room: str, gives_rewards: bool = True,
                   final_boss: bool = False) -> bool:
    """Meditations of a Yako: "After an elite or boss fight, you may Publish
    an Annotation." Never a normal fight, and never the final boss (no
    reward screen follows it). C# `YaeEditing.OffersPublish`."""
    return gives_rewards and not final_boss and room in PUBLISH_ROOMS


def publish_choices(drafts: dict, published: dict,
                    cards: Optional[dict] = None) -> list:
    """The offer: every deck slot the fight left Annotated that is not yet
    Published (a card holds one Enchantment), in slot order. `cards` (slot
    -> card): a slot whose draft would do nothing on its card is not
    offered (the dead-edit filter). C# `YaeEditing.PublishChoices`."""
    return [slot for slot in sorted(drafts)
            if drafts[slot] and slot not in published
            and (cards is None or slot not in cards
                 or affects(cards[slot], drafts[slot]))]


def publish_after_fight(room: str, drafts: dict, published: dict,
                        relic: str = MEDITATIONS, pick=None,
                        final_boss: bool = False,
                        cards: Optional[dict] = None) -> list:
    """The after-elite Publish, run-level: `drafts` is the fight's
    (`YaeLedger.drafts`), `published` the run's {slot: Annotation}, written
    in place. `pick(choices, drafts)` returns the slots to keep (empty is the
    skip); the default reading keeps the best by `PUBLISH_ORDER`. Returns
    [(slot, Annotation)] Published, empty when nothing is offered."""
    if relic not in PUBLISH_COUNT or not offers_publish(
            room, final_boss=final_boss):
        return []
    choices = publish_choices(drafts, published, cards)
    if not choices:
        return []
    if pick is None:
        picked = sorted(choices, key=lambda s: (
            PUBLISH_ORDER.index(drafts[s]), s))
    else:
        picked = [s for s in (pick(choices, drafts) or []) if s in choices]
    out = []
    for slot in picked[:PUBLISH_COUNT[relic]]:
        published[slot] = drafts[slot]
        out.append((slot, drafts[slot]))
    return out


def after_play(state, card) -> None:
    """`effects.resolve_card`, after the card's own effects, for an
    Annotated card: Serialization (shrine r2, "whenever you play an
    Annotated card, gain 3 Block"), then Editor-in-Chief, "a Sakura
    strikes" (the highest Level, the oldest on a tie)."""
    led = ledger(state.player)
    if led is None or not is_annotated(card):
        return
    _block(state, _power(state.player, SERIALIZATION), "serialization")
    if not led.sakura:
        return
    for _ in range(_power(state.player, EDITOR_IN_CHIEF)):
        if not state.living_enemies:
            return
        strike(state, highest(led), "editor_in_chief")


#: Universals never offered to one character: "Yae Miko -- Sesshou Sakura"
#: stays in the Inazuma roster for the others and is hidden from Yae's own
#: offers (pick 5 (a), ruled 2026-10-13). C# twin:
#: `CompanionPool.IsHiddenFrom`.
HIDDEN_COMPANIONS = {"proto_mi_yae_sesshou_sakura": CHARACTER}


def hidden_from(card_id: str, character_id) -> bool:
    """Is this companion never offered to `character_id`?"""
    return HIDDEN_COMPANIONS.get(card_id) == character_id


# --------------------------------------------------------------------------
#  The op
# --------------------------------------------------------------------------

def _refuse(what: str) -> None:
    raise NotImplementedError(
        f"{what} is YAE's (tier0/engine/yae_shrine.py) and resolves only "
        "for a Yae seat; no shipped row prints it.")


def validate_op(card_id: str, fx: dict) -> None:
    """The loader's shape check for one `yae` op, AT LOAD."""
    kind = fx.get("kind")
    if kind not in KINDS:
        raise ValueError(f"card {card_id!r}: unknown yae kind {kind!r}")
    unknown = set(fx) - OP_FIELDS
    if unknown:
        raise ValueError(f"card {card_id!r}: yae {kind!r} has unknown "
                         f"fields {sorted(unknown)}")
    have = set(fx) & {"per", "base", "amount"}
    want = set(KIND_FIELDS[kind])
    if want != have:
        raise ValueError(f"card {card_id!r}: yae {kind!r} takes the fields "
                         f"{sorted(want)}, got {sorted(have)}")
    for key in want:
        if not isinstance(fx[key], int) or fx[key] < 0:
            raise ValueError(f"card {card_id!r}: yae {kind!r} `{key}` must "
                             f"be a non-negative int, got {fx[key]!r}")
    if fx.get("target") != KIND_TARGETS.get(kind):
        raise ValueError(f"card {card_id!r}: yae {kind!r} takes target "
                         f"{KIND_TARGETS.get(kind)!r}, got "
                         f"{fx.get('target')!r}")
    if (kind in ANNOTATION_KINDS) != ("annotation" in fx):
        raise ValueError(f"card {card_id!r}: yae {kind!r} "
                         f"{'needs' if kind in ANNOTATION_KINDS else 'takes no'}"
                         " `annotation:`")
    if "annotation" in fx and fx["annotation"] not in ANNOTATIONS:
        raise ValueError(f"card {card_id!r}: unknown Annotation "
                         f"{fx['annotation']!r}")
    if "as" in fx and kind != "tenko":
        raise ValueError(f"card {card_id!r}: yae {kind!r} takes no `as:`")
    if "as" in fx and fx["as"] not in TENKO_NAME:
        raise ValueError(f"card {card_id!r}: unknown Tenko kind "
                         f"{fx['as']!r}")
    if (kind == "edit_sakura") != ("which" in fx):
        raise ValueError(f"card {card_id!r}: yae {kind!r} "
                         f"{'needs' if kind == 'edit_sakura' else 'takes no'}"
                         " `which:`")
    if "which" in fx and fx["which"] not in SAKURA_EDIT_ENDS:
        raise ValueError(f"card {card_id!r}: `which:` is newest, oldest or "
                         "every, "
                         f"got {fx['which']!r}")
    if kind == "edit_sakura" and fx["annotation"] not in SAKURA_ANNOTATIONS:
        raise ValueError(f"card {card_id!r}: {fx['annotation']!r} has no "
                         "Sakura reading")


def _card_hit(state, card, amount: int) -> None:
    """One powered Electro hit of the card on the play's aim."""
    from tier0.engine import effects                # late: cycle
    targets = effects._pick_targets(state, "enemy")
    if not targets or amount <= 0:
        return
    if card.type == "attack":
        amount += state.current_attack_bonus + card.enchant_damage
    source = "attack" if card.type == "attack" else "card"
    effects.deal_damage_to_enemy(state, targets[0], amount, element=ELEMENT,
                                 source=source)


def _card_block(state, card, amount: int) -> None:
    from tier0.engine import effects                # late: cycle
    if amount > 0:
        effects._op_block(state, {"op": "block", "amount": amount}, card)


def op_yae(state, fx: dict, card) -> None:
    """`effects.OPS['yae']`."""
    from tier0.engine import effects                # late: cycle
    led = ledger(state.player)
    if led is None:
        _refuse(f"op 'yae' ({fx.get('kind')!r}) on {card.id!r}")
    kind = fx["kind"]
    if kind == "plant":
        plant(state, fx["amount"], "card", annotation=inherited(card))
    elif kind == "tenko":
        tenko(state, fx.get("as", THUNDER))
    elif kind == "extend":
        extend(state, fx["amount"])
    elif kind == "level_up":
        level_up(state, fx["amount"])
    elif kind == "edit":
        edit(state, card, fx["annotation"], fx["amount"])
    elif kind == "edit_all":
        edit_all(state, card, fx["annotation"])
    elif kind == "publish":
        publish(state, card)
    elif kind == "lure":
        targets = effects._pick_targets(state, "enemy")
        led.lure = targets[0] if targets else None
    elif kind == "damage_per_sakura":
        _card_hit(state, card, fx["base"] + fx["per"] * len(led.sakura))
    elif kind == "block_per_sakura":
        _card_block(state, card, fx["base"] + fx["per"] * len(led.sakura))
    elif kind == "damage_per_annotated":
        _card_hit(state, card,
                  fx["base"] + fx["per"] * annotated_in_hand(state))
    elif kind == "block_per_annotated":
        _card_block(state, card,
                    fx["base"] + fx["per"] * annotated_in_hand(state))
    elif kind == "annotated_strike":
        _card_hit(state, card,
                  fx["base"] + (fx["amount"] if is_annotated(card) else 0))
    elif kind == "fox_fire":
        fox_fire(state, card.id)
    elif kind == "edit_sakura":
        edit_sakura(state, fx["which"], fx["amount"], fx["annotation"])
    elif kind == "plant_level":
        plant(state, 1, "card", level=fx["amount"],
              annotation=inherited(card))
    elif kind == "strike_if_weak":
        targets = effects._pick_targets(state, "enemy")
        target = targets[0] if targets else None
        if (target is not None and target.alive and led.sakura
                and int(target.powers.get("weak", 0)) > 0):
            strike(state, highest(led), "pounce", aim=target)
    else:
        _refuse(f"yae kind {kind!r}")


# --------------------------------------------------------------------------
#  Building her
# --------------------------------------------------------------------------

def starter_ids() -> list[str]:
    return list(STARTER_IDS)


def build_player(extra: tuple = (), hp: Optional[int] = None,
                 relic: bool = True, relic_upgraded: bool = False,
                 published: Optional[dict] = None):
    """A fresh Yae combat Player (72 HP) holding the starter, `extra` card
    ids and Meditations of a Yako. `published` is {deck slot: Annotation}
    (slots index `starter_ids() + extra`): those cards enter the fight
    Annotated, the run harness's permanence. Every card carries its slot
    (`ym_slot`) so the fight can report the drafts it leaves."""
    from tier0.content import loader                # late: cycle
    from tier0.engine.state import Player
    ids = starter_ids() + list(extra)
    cards = []
    for i, cid in enumerate(ids):
        c = loader.get_card(cid)
        c.ym_slot = i
        cards.append(c)
    hp = HP if hp is None else hp
    player = Player(hp=hp, max_hp=max(hp, HP), draw_pile=cards,
                    element=ELEMENT, cadence=CADENCE,
                    character_id=CHARACTER)
    if relic or relic_upgraded:
        player.relic_hooks.append(
            MEDITATIONS_UPGRADED if relic_upgraded else MEDITATIONS)
    player.yae_ledger = YaeLedger()
    for slot, name in (published or {}).items():
        annotate(None, cards[slot], name, "published")
        cards[slot].ym_published = True
    return player
