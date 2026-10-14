"""YAE MIKO, THE SHRINE AND THE PUBLISHING HOUSE -- the sim's rules twin.

Design: `review/active/yae-proposal-2026-10-12.md` (ruled 2026-10-12) and the
card paper `review/active/yae-card-paper-2026-10-13.md`, whose sec.2 is the
list of readings this module takes. Rows: `docs/yae-staging.yaml`, a SIM-ONLY
staging sheet (the prototype surface compiles to the mod, and her C# waits on
the paper's picks), read through the loader's prototype validators
(`loader.STAGING_SHEETS`). No C# twin yet.

NO SWITCH, as Varka: she ships nowhere else, so every hook this module adds to
the shared engine is a dead branch for any player who is not Yae (`live`).
Her numbers live here rather than in `constants.py` so they move neither the
constant census nor the world stamp.

THE RULES AS MODELLED:
  * SAKURA: up to `SAKURA_CAP` on a per-fight ledger (`YaeLedger.sakura`),
    each with a LEVEL and a TIMER (strikes left). Planted at `PLANT_LEVEL`
    (2 under Fox's Mooncall) with 3 strikes left. Planting while others stand
    raises every standing Sakura's Level by 1, to `LEVEL_CAP` (4 under
    Mooncall); planting a fourth levels the three and adds none (`SCALING ==
    "level"`, the paper's pick 1 (a)). Under `SCALING == "count"` (pick 1 (b),
    the proposal's placeholder) Levels are off: a Sakura strikes for the
    count-table value, a fourth plant replaces the oldest, and each Tenko
    raises a per-fight shrine bonus that every strike adds. The table
    is the proposal's placeholder lifted by 1 so both answers share a
    ceiling (15 a turn at three).
  * STRIKE: at the end of her turn each Sakura, oldest first, deals
    `SAKURA_BASE + Level` Electro to one random living enemy (the Lure's
    enemy this turn, while it lives), unpowered (a pet's hit: no Strength, no
    Weak; Vulnerable and Block apply), source "card" (a Power's hit in the
    EB-495 matrix). Then its timer ticks; at 0 it withers. A strike that
    kills ends nothing else early.
  * TENKO: every Sakura strikes now, oldest first, then every timer is set
    back to 3. The strikes are the same strikes (Grove, Edict, Channeling
    all pay). Tenko with no Sakura does nothing.
  * EDIT: a card in hand (never the editing card itself, never a Status,
    Curse or kit card) gains one ANNOTATION for the combat, overwriting any
    it had: Red Ink (+3 damage and +3 Block, as the card's own riders),
    Footnote (draw 1 after its own effects), Deadline Extension (Retain), Fox
    Fire (after its own effects, 4 Electro to a random enemy, unpowered),
    Sakura Seal (after its own effects, plant a Sakura). The target is the
    pilot's (`YaeLedger.edit_choice`); the default reading is `_edit_target`.
    "Annotated" is any card carrying one (`is_annotated`), a Published one
    included.
  * PUBLISH: the card's Annotation is marked permanent (`ym_published`). The
    sim's fights are single combats; the run harness (`tools/yae_expansion_sim`)
    carries a Published Annotation into the next fight by deck slot, and
    Meditations of a Yako's rest-site Publish reads the DRAFTS the fight
    left (`YaeLedger.drafts`, slot -> last Annotation).
  * POWERS (self, by name): Sakura Grove (+n per strike), Edict of Cleansing
    (+n on a strike at an enemy wearing Pyro, Hydro or Cryo: the strike will
    react), Serialization (Block per Edit, unpowered), Fox's Mooncall (plant at
    Level 2, cap 4), Yakan Offering (plant at the start of her turn, after the
    draw), Sakura Channeling (Block per strike, unpowered), Editor-in-Chief
    (after an Annotated card's play, the highest-Level Sakura strikes).

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

# --- the shrine (C# twin to come: `YaeShrine`) ---
SAKURA_CAP = 3
SAKURA_TURNS = 3            # strikes a Sakura has when planted or refreshed
SAKURA_BASE = 2             # a strike deals this plus the Sakura's Level
PLANT_LEVEL = 1
LEVEL_CAP = 3
MOONCALL_PLANT_LEVEL = 2    # Fox's Mooncall: planted at 2, cap 4
MOONCALL_LEVEL_CAP = 4
#: Pick 1 (b): the proposal's placeholder, a strike by the COUNT standing.
COUNT_TABLE = {1: 3, 2: 4, 3: 5}   # the same ceiling as (a), paired
COUNT_TENKO_BONUS = 1       # (b): each Tenko adds 1 to every later strike
#: "level" (pick 1 (a), the default) or "count" (pick 1 (b)).
SCALING = "level"

# --- the Annotations ---
RED_INK, FOOTNOTE, DEADLINE, FOX_FIRE, SAKURA_SEAL = (
    "red_ink", "footnote", "deadline", "fox_fire", "sakura_seal")
ANNOTATIONS = (RED_INK, FOOTNOTE, DEADLINE, FOX_FIRE, SAKURA_SEAL)
RED_INK_AMOUNT = 3
FOX_FIRE_DAMAGE = 4
#: What a Publish is worth to the default pilot, best first.
PUBLISH_ORDER = (SAKURA_SEAL, FOOTNOTE, RED_INK, FOX_FIRE, DEADLINE)

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
}
KINDS = frozenset(KIND_FIELDS)
KIND_TARGETS = {
    "lure": "enemy", "damage_per_sakura": "enemy",
    "damage_per_annotated": "enemy", "annotated_strike": "enemy",
}
#: Kinds that take an `annotation:` name.
ANNOTATION_KINDS = frozenset({"edit", "edit_all"})
OP_FIELDS = frozenset({"op", "kind", "amount", "base", "per", "target",
                       "annotation"})


@dataclass
class Sakura:
    level: int
    turns_left: int
    seq: int                      # planting order, the ledger's clock


@dataclass
class YaeLedger:
    """Per-fight state, hung on the Player (`Player.yae_ledger`)."""
    sakura: list = field(default_factory=list)
    seq: int = 0
    shrine_bonus: int = 0         # SCALING == "count": +1 per Tenko
    lure: object = None           # this turn's aimed enemy, or None
    strikes: int = 0              # this combat
    strike_damage: int = 0        # printed amounts, this combat
    edits: int = 0
    #: slot -> last Annotation the fight left on that deck card (the
    #: manuscript the rest-site Publish reads).
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


def _level_cap(player) -> int:
    return MOONCALL_LEVEL_CAP if _power(player, MOONCALL) else LEVEL_CAP


def _plant_level(player) -> int:
    return MOONCALL_PLANT_LEVEL if _power(player, MOONCALL) else PLANT_LEVEL


def plant(state, n: int = 1, reason: str = "plant") -> None:
    """Plant `n` Sakura, one at a time (each levels the ones standing)."""
    led = ledger(state.player)
    if led is None:
        return
    for _ in range(n):
        cap = _level_cap(state.player)
        if SCALING == "level":
            for s in led.sakura:
                s.level = min(cap, s.level + 1)
            if len(led.sakura) >= SAKURA_CAP:
                state.emit("yae_level", reason=reason,
                           levels=[s.level for s in led.sakura])
                continue
        elif len(led.sakura) >= SAKURA_CAP:
            led.sakura.pop(0)                       # (b): the oldest goes
        led.seq += 1
        led.sakura.append(Sakura(level=_plant_level(state.player),
                                 turns_left=SAKURA_TURNS, seq=led.seq))
        state.emit("yae_plant", reason=reason, count=len(led.sakura),
                   levels=[s.level for s in led.sakura])


def strike_damage(state, s: Sakura, target) -> int:
    p = state.player
    if SCALING == "level":
        dmg = SAKURA_BASE + s.level
    else:
        led = ledger(p)
        dmg = COUNT_TABLE[min(SAKURA_CAP, len(led.sakura))] + led.shrine_bonus
    dmg += _power(p, SAKURA_GROVE)
    if target is not None and target.aura in REACTING_AURAS:
        dmg += _power(p, EDICT)
    return dmg


def _aim(state):
    led = ledger(state.player)
    if led.lure is not None and led.lure.alive:
        return led.lure
    living = list(state.living_enemies)
    return state.rng.choice(living) if living else None


def strike(state, s: Sakura, reason: str) -> None:
    """One Sakura's strike: one random living enemy, Electro, unpowered."""
    from tier0.engine import effects                # late: cycle
    led = ledger(state.player)
    target = _aim(state)
    if target is None:
        return
    dmg = strike_damage(state, s, target)
    led.strikes += 1
    led.strike_damage += dmg
    state.emit("yae_sakura_strike", reason=reason, level=s.level,
               amount=dmg, target=target.name)
    effects.deal_damage_to_enemy(state, target, dmg, element=ELEMENT,
                                 source="card", powered=False)
    _block(state, _power(state.player, CHANNELING), "sakura_channeling")


def strike_all(state, reason: str) -> None:
    led = ledger(state.player)
    for s in list(led.sakura):
        if not state.living_enemies:
            break
        strike(state, s, reason)


def tenko(state) -> None:
    """Every Sakura strikes now, then every timer is set back to 3."""
    led = ledger(state.player)
    if led is None or not led.sakura:
        return
    state.emit("yae_tenko", count=len(led.sakura))
    strike_all(state, "tenko")
    for s in led.sakura:
        s.turns_left = SAKURA_TURNS
    if SCALING == "count":
        led.shrine_bonus += COUNT_TENKO_BONUS


def extend(state, n: int) -> None:
    led = ledger(state.player)
    for s in led.sakura:
        s.turns_left += n


def level_up(state, n: int) -> None:
    led = ledger(state.player)
    cap = _level_cap(state.player)
    for s in led.sakura:
        s.level = min(cap, s.level + n)


def turn_start(state) -> None:
    """`combat._player_turn`, post-draw: the Lure expires; Yakan Offering
    plants."""
    led = ledger(state.player)
    if led is None:
        return
    led.lure = None
    for _ in range(_power(state.player, YAKAN_OFFERING)):
        plant(state, 1, "yakan_offering")


def turn_end(state) -> None:
    """`combat`'s player turn end: the strikes, then the timers tick and
    the withered leave."""
    led = ledger(state.player)
    if led is None:
        return
    strike_all(state, "turn_end")
    for s in led.sakura:
        s.turns_left -= 1
    withered = [s for s in led.sakura if s.turns_left <= 0]
    if withered:
        led.sakura = [s for s in led.sakura if s.turns_left > 0]
        state.emit("yae_wither", count=len(withered),
                   standing=len(led.sakura))
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
    card.enchant_damage = RED_INK_AMOUNT if name == RED_INK else 0
    card.enchant_block = RED_INK_AMOUNT if name == RED_INK else 0
    card.retain = card.ym_base_retain or name == DEADLINE
    if name == FOOTNOTE:
        card.enchant_effects = [{"op": "draw", "amount": 1}]
    elif name == FOX_FIRE:
        card.enchant_effects = [{"op": "yae", "kind": "fox_fire"}]
    elif name == SAKURA_SEAL:
        card.enchant_effects = [{"op": "yae", "kind": "plant", "amount": 1}]
    else:
        card.enchant_effects = []
    if state is not None:
        state.emit("yae_annotate", card=card.id, annotation=name,
                   reason=reason)


def _editable(state, editor) -> list:
    return [c for c in state.player.hand
            if c is not editor and not c.kit_card and not c.is_junk]


def _has_op(card, op: str) -> bool:
    return any(fx.get("op") == op for fx in card.effects)


def _edit_target(state, editor, annotation: str):
    """The default reading of "a card in your hand": Red Ink goes on the
    hardest-hitting Attack (most hits), else a Block card; Deadline on the
    dearest card; the three play riders on the cheapest card. A card not yet
    Annotated is preferred, so an Edit overwrites only when it must."""
    cands = _editable(state, editor)
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
    plain = [c for c in fresh if not c.exhaust] or fresh
    return min(plain, key=cost)


def edit(state, editor, annotation: str, n: int = 1) -> None:
    led = ledger(state.player)
    for _ in range(n):
        chooser = led.edit_choice or _edit_target
        target = chooser(state, editor, annotation)
        if target is None:
            return
        annotate(state, target, annotation)
        led.edits += 1
        _block(state, _power(state.player, SERIALIZATION), "serialization")


def edit_all(state, editor, default: str) -> None:
    """Reborn as Guuji Yae: one Annotation (the pilot's `reborn_choice`,
    else the row's) on every other card in hand."""
    led = ledger(state.player)
    name = led.reborn_choice or default
    cards = _editable(state, editor)
    for c in cards:
        annotate(state, c, name, "reborn")
    if cards:
        led.edits += len(cards)
        _block(state, _power(state.player, SERIALIZATION) * len(cards),
               "serialization")


def publish(state, editor) -> None:
    """The Seven Glamours: the best Annotated card in hand is Published."""
    cands = [c for c in _editable(state, editor) if is_annotated(c)]
    if not cands:
        return
    best = min(cands, key=lambda c: PUBLISH_ORDER.index(c.ym_annotation))
    best.ym_published = True
    state.emit("yae_publish", card=best.id, annotation=best.ym_annotation)


def after_play(state, card) -> None:
    """`effects.resolve_card`, after the card's own effects: Editor-in-Chief,
    "whenever you play an Annotated card, a Sakura strikes" (the highest
    Level, the oldest on a tie)."""
    led = ledger(state.player)
    if led is None or not is_annotated(card) or not led.sakura:
        return
    for _ in range(_power(state.player, EDITOR_IN_CHIEF)):
        if not state.living_enemies:
            return
        s = max(led.sakura, key=lambda s: (s.level, -s.seq))
        strike(state, s, "editor_in_chief")


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
        plant(state, fx["amount"], "card")
    elif kind == "tenko":
        tenko(state)
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
        living = list(state.living_enemies)
        if living:
            target = state.rng.choice(living)
            state.emit("yae_fox_fire", card=card.id, target=target.name)
            effects.deal_damage_to_enemy(state, target, FOX_FIRE_DAMAGE,
                                         element=ELEMENT, source="card",
                                         powered=False)
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
